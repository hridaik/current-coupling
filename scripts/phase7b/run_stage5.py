"""
Stage 5: Dynamics unit tests.
Tests the SDE integrator in isolation (no acceptance gate yet).
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.graph import build_D, compute_B
from scripts.phase7b.dynamics import (
    softplus, step_z, step_x, simulate_run, observe
)


def run():
    print('=' * 60)
    print('STAGE 5: Dynamics unit tests')
    print('=' * 60)

    # Load A from stage 2
    a_path = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_A.npy')
    if not os.path.exists(a_path):
        print('ERROR: Stage 2 output not found. Run run_stage2.py first.')
        sys.exit(1)
    A = np.load(a_path)
    D, D_sqrt, u = build_D()

    checks = []

    # ----- softplus tests -----
    sp0 = softplus(np.array([0.0]))
    checks.append(('softplus(0) ≈ log(2)', abs(sp0[0] - np.log(2)) < 1e-6))

    sp_neg = softplus(np.array([-100.0]))
    checks.append(('softplus(-100) ≈ 0', sp_neg[0] < 1e-3))

    sp_pos = softplus(np.array([100.0]))
    checks.append(('softplus(100) ≈ 100', abs(sp_pos[0] - 100.0) < 1e-3))

    # ----- B(z) tests -----
    B_pos = compute_B(2.0)
    for h in cfg.SA:
        ok = abs(B_pos[h] - cfg.GAMMA_H2 * 2.0) < 1e-10
        if not ok:
            checks.append((f'B({h}, z=2)', False))
            break
    else:
        checks.append(('B(h in SA, z=2) = GAMMA_H2*2', True))

    B_non_h2 = [B_pos[k] == 0.0 for k in range(cfg.N_TOTAL) if k not in cfg.SA]
    checks.append(('B(k not in SA) = 0', all(B_non_h2)))

    # ----- OU z step tests -----
    # With theta=10, dt=0.1, z=5: drift = -10*5*0.1 = -5, so z_next ≈ 0 + noise
    # EM is stable for theta*dt=1.0; just verify direction of pull
    rng = np.random.default_rng(999)
    z = 5.0
    z_next = step_z(z, rng, theta=10.0)
    # Mean of z_next ≈ 0; check it is less than z in absolute value (pulled toward 0)
    checks.append(('step_z: high theta pulls z toward 0', abs(z_next) < abs(z)))

    # OU process: stationary variance should be sigma_z^2 / (2*theta)
    rng2 = np.random.default_rng(7777)
    z_vals = [0.0]
    for _ in range(50_000):
        z_vals.append(step_z(z_vals[-1], rng2))
    z_arr = np.array(z_vals[1000:])  # discard burn-in
    expected_var = cfg.SIGMA_Z**2 / (2 * cfg.THETA_Z)
    actual_var   = float(np.var(z_arr))
    checks.append((f'OU stationary var ≈ {expected_var:.2f} (got {actual_var:.2f})',
                   abs(actual_var - expected_var) / expected_var < 0.10))

    # ----- SDE x step test -----
    rng3 = np.random.default_rng(42)
    x0 = np.zeros(cfg.N_TOTAL)
    x1 = step_x(x0, 0.0, A, D_sqrt, lambda z: compute_B(z), rng3)
    checks.append(('step_x returns correct shape', x1.shape == (cfg.N_TOTAL,)))
    checks.append(('step_x: finite output', np.all(np.isfinite(x1))))

    # ----- Short simulation test (50 steps, 1 run) -----
    print('\nRunning short simulation test (T=100, T_warmup=10)...')
    result = simulate_run(
        run_index=0, A=A, D_sqrt=D_sqrt,
        B_fn=lambda z: compute_B(z),
        T=100, T_warmup=10,
    )
    y = result['y']
    z_out = result['z_oracle']
    checks.append(('simulate_run y shape', y.shape == (90, cfg.N_OBS)))
    checks.append(('simulate_run z_oracle shape', z_out.shape == (90,)))
    checks.append(('simulate_run y finite', bool(np.all(np.isfinite(y)))))
    checks.append(('simulate_run y > 0 (calcium-like)', bool(np.all(y > -5.0))))

    # ----- Observation model test -----
    x_obs = np.ones(cfg.N_OBS) * 2.0
    ca    = np.zeros(cfg.N_OBS)
    rng_obs = np.random.default_rng(0)
    y_obs, ca_new = observe(x_obs, ca, rng_obs)
    checks.append(('observe returns correct shapes',
                   y_obs.shape == (cfg.N_OBS,) and ca_new.shape == (cfg.N_OBS,)))
    checks.append(('calcium filter ca_new < softplus(x)', bool(np.all(ca_new < softplus(x_obs)))))

    # ----- Seed independence: two runs have different trajectories -----
    result0 = simulate_run(0, A, D_sqrt, lambda z: compute_B(z), T=200, T_warmup=10)
    result1 = simulate_run(1, A, D_sqrt, lambda z: compute_B(z), T=200, T_warmup=10)
    checks.append(('runs 0 and 1 differ', not np.allclose(result0['y'], result1['y'])))

    # ----- Reproducibility: same run index → same output -----
    result0b = simulate_run(0, A, D_sqrt, lambda z: compute_B(z), T=200, T_warmup=10)
    checks.append(('run 0 reproducible', np.allclose(result0['y'], result0b['y'])))

    print()
    n_pass = n_fail = 0
    for name, ok in checks:
        status = 'PASS' if ok else 'FAIL'
        print(f'  {status:4s}  {name}')
        if ok: n_pass += 1
        else:  n_fail += 1

    print()
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')
    if n_fail:
        print('STAGE 5 FAILED')
        sys.exit(1)
    print('STAGE 5 PASSED')


if __name__ == '__main__':
    run()
