"""
Dynamics simulator — Phase 7B Stage 5.

Implements Euler-Maruyama integration of the SDE system from
phase6b_architecture_spec.md §2.5-2.8. No scientific decisions here.

FORBIDDEN: This module never reads A, D, H2 topology, or labels.
It receives A, D_sqrt, and compute_B as opaque callables/arrays.
"""

import numpy as np
from . import config as cfg


# ---------------------------------------------------------------------------
# Observation model (phase6b_architecture_spec.md §2.7)
# ---------------------------------------------------------------------------

def softplus(x: np.ndarray) -> np.ndarray:
    """Softplus nonlinearity: log(1 + exp(x)), numerically stable."""
    return np.where(x > 30.0, x, np.log1p(np.exp(np.clip(x, -500, 30))))


def apply_calcium_filter(
    r: np.ndarray,
    ca: np.ndarray,
    kappa: float = cfg.KAPPA_CA,
    dt: float = cfg.DT,
) -> np.ndarray:
    """
    One-step AR(1) calcium filter.
    ca_new = (1 - kappa*dt) * ca + kappa*dt * r
    """
    alpha = kappa * dt
    return (1.0 - alpha) * ca + alpha * r


def observe(
    x_obs: np.ndarray,
    ca: np.ndarray,
    rng: np.random.Generator,
    sigma_noise: float = cfg.SIGMA_OBS_NOISE,
    kappa: float = cfg.KAPPA_CA,
    dt: float = cfg.DT,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Observation model: softplus → calcium filter → additive Gaussian noise.

    Parameters
    ----------
    x_obs : (N_OBS,) float64
        Current neural state for observed neurons.
    ca : (N_OBS,) float64
        Previous calcium trace.
    rng : Generator
        Seeded PRNG (observation seed).

    Returns
    -------
    y : (N_OBS,) float64 — noisy calcium observation
    ca_new : (N_OBS,) float64 — updated latent calcium
    """
    r = softplus(x_obs)
    ca_new = apply_calcium_filter(r, ca, kappa=kappa, dt=dt)
    noise = rng.standard_normal(x_obs.shape) * sigma_noise
    y = ca_new + noise
    return y, ca_new


# ---------------------------------------------------------------------------
# OU process for latent state z (phase6b_architecture_spec.md §2.6)
# ---------------------------------------------------------------------------

def step_z(
    z: float,
    rng: np.random.Generator,
    theta: float = cfg.THETA_Z,
    sigma: float = cfg.SIGMA_Z,
    dt: float = cfg.DT,
) -> float:
    """
    Euler-Maruyama step for OU process:
    dz = -theta*z*dt + sigma*dW_z
    """
    dW = rng.standard_normal() * np.sqrt(dt)
    return z - theta * z * dt + sigma * dW


# ---------------------------------------------------------------------------
# Neural state SDE step (phase6b_architecture_spec.md §2.5)
# ---------------------------------------------------------------------------

def step_x(
    x: np.ndarray,
    z: float,
    A: np.ndarray,
    D_sqrt: np.ndarray,
    B_fn,
    rng: np.random.Generator,
    dt: float = cfg.DT,
) -> np.ndarray:
    """
    Euler-Maruyama step for neural SDE:
    dx = (A @ x + B(z)) * dt + D^{1/2} @ dW

    Parameters
    ----------
    x : (N_TOTAL,) float64
    z : float — current latent state
    A : (N_TOTAL, N_TOTAL) float64 — coupling matrix (never modified)
    D_sqrt : (N_TOTAL, N_TOTAL) float64 — Cholesky factor of D
    B_fn : callable(z) -> (N_TOTAL,) float64
    rng : Generator — seeded per run

    Returns
    -------
    x_new : (N_TOTAL,) float64
    """
    B = B_fn(z)
    drift = (A @ x + B) * dt
    dW = rng.standard_normal(x.shape) * np.sqrt(dt)
    diffusion = D_sqrt @ dW
    return x + drift + diffusion


# ---------------------------------------------------------------------------
# Single-run simulator
# ---------------------------------------------------------------------------

def simulate_run(
    run_index: int,
    A: np.ndarray,
    D_sqrt: np.ndarray,
    B_fn,
    gamma_H2: float = cfg.GAMMA_H2,
    provide_z: bool = True,
    use_obs_model: bool = True,
    dt: float = cfg.DT,
    T: int = cfg.T,
    T_warmup: int = cfg.T_WARMUP,
) -> dict:
    """
    Run one simulation and return the effective (post-warmup) trajectory.

    Parameters
    ----------
    run_index : int — 0-indexed run number (determines seeds)
    A : (N_TOTAL, N_TOTAL) — coupling matrix (read-only)
    D_sqrt : (N_TOTAL, N_TOTAL) — Cholesky factor of D
    B_fn : callable(z: float) -> (N_TOTAL,) ndarray
    gamma_H2 : float — override for evaluation conditions (default: GAMMA_H2)
    provide_z : bool — if True, oracle z(t) is included in output
    use_obs_model : bool — if False, return raw softplus(x_obs) instead of calcium traces
    dt, T, T_warmup : from config

    Returns
    -------
    dict with keys:
        'y'       : (T_eff, N_OBS) float64 — observations
        'z_oracle': (T_eff,) float64 if provide_z else None
        'run_index': int
    """
    T_eff = T - T_warmup

    rng_z = np.random.default_rng(cfg.z_seed(run_index))
    rng_x = np.random.default_rng(cfg.x_seed(run_index))

    # Initial conditions: x=0, z=0, ca=0
    x  = np.zeros(cfg.N_TOTAL, dtype=np.float64)
    z  = 0.0
    ca = np.zeros(cfg.N_OBS, dtype=np.float64)

    # Storage (only allocate after warm-up)
    y_store = np.empty((T_eff, cfg.N_OBS), dtype=np.float64)
    z_store = np.empty(T_eff, dtype=np.float64) if provide_z else None

    for t in range(T):
        # Advance z
        z = step_z(z, rng_z)

        # Advance x
        x = step_x(x, z, A, D_sqrt, B_fn, rng_x, dt=dt)

        # Record post-warmup
        if t >= T_warmup:
            t_eff = t - T_warmup
            x_obs = x[:cfg.N_OBS]

            if use_obs_model:
                y, ca = observe(x_obs, ca, rng_x)
            else:
                # neural_state condition: raw softplus (no calcium filter or noise)
                y = softplus(x_obs)

            y_store[t_eff] = y

            if provide_z:
                z_store[t_eff] = z

    return {
        'y':        y_store,
        'z_oracle': z_store,
        'run_index': run_index,
    }


# ---------------------------------------------------------------------------
# Multi-run driver
# ---------------------------------------------------------------------------

def simulate_all_runs(
    A: np.ndarray,
    D_sqrt: np.ndarray,
    B_fn,
    condition: str = 'oracle_z',
    verbose: bool = True,
) -> list[dict]:
    """
    Run all R simulations under the specified evaluation condition.
    Returns list of R dicts (one per run) from simulate_run().

    This function must NOT be called before check_all_acceptance_tests_passed().
    The gate is enforced in run_stage6.py.
    """
    cond = cfg.CONDITIONS[condition]
    gamma_H2  = cond['gamma_H2']
    provide_z = cond['provide_z']
    use_obs   = cond['use_obs_model']

    from .graph import compute_B as _base_B

    def B_fn_cond(z: float) -> np.ndarray:
        return _base_B(z, gamma_H2=gamma_H2)

    runs = []
    for r in range(cfg.R):
        if verbose:
            print(f'  run {r+1}/{cfg.R} (condition={condition})...', flush=True)
        result = simulate_run(
            run_index=r,
            A=A,
            D_sqrt=D_sqrt,
            B_fn=B_fn_cond,
            gamma_H2=gamma_H2,
            provide_z=provide_z,
            use_obs_model=use_obs,
        )
        runs.append(result)

    return runs
