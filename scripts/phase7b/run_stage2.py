"""
Stage 2: Graph construction and CK-G* checks.
Builds A_sparse, verifies all graph-level construction checks.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.graph import build_A_sparse, build_D, compute_B
from scripts.phase7b.checks import run_graph_checks, run_invariant_checks


def run():
    print('=' * 60)
    print('STAGE 2: Graph construction + CK-G* checks')
    print('=' * 60)

    print('\nBuilding A_sparse...')
    A, n_resample = build_A_sparse()
    print(f'  A_sparse shape: {A.shape}')
    print(f'  Resample attempts: {n_resample}')

    abscissa = float(np.max(np.linalg.eigvals(A).real))
    print(f'  Spectral abscissa: {abscissa:.6f}')

    print('\nBuilding D...')
    D, D_sqrt, u = build_D()
    print(f'  D shape: {D.shape}, D_sqrt shape: {D_sqrt.shape}')

    print('\nRunning CK-G* checks...')
    results = run_graph_checks(A)

    n_pass = n_fail = 0
    for name, passed, msg in results:
        status = 'PASS' if passed else 'FAIL'
        print(f'  {status:4s}  {name}: {msg}')
        if passed:
            n_pass += 1
        else:
            n_fail += 1

    print('\nRunning invariant checks...')
    inv_results = run_invariant_checks(A, D, D - cfg.D_0 * np.eye(cfg.N_TOTAL), u, compute_B)
    for name, passed, msg in inv_results:
        status = 'PASS' if passed else 'FAIL'
        print(f'  {status:4s}  {name}: {msg}')
        if passed:
            n_pass += 1
        else:
            n_fail += 1

    print()
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')

    # Save A for downstream stages
    os.makedirs(cfg.GROUND_TRUTH_DIR, exist_ok=True)
    np.save(os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_A.npy'), A)
    np.save(os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_D_sqrt.npy'), D_sqrt)
    np.save(os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_u.npy'), u)
    print(f'Saved A_sparse, D_sqrt, u to {cfg.GROUND_TRUTH_DIR}/')

    if n_fail:
        print('STAGE 2 FAILED')
        sys.exit(1)
    print('STAGE 2 PASSED')


if __name__ == '__main__':
    run()
