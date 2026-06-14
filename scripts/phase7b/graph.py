"""
Graph construction — Phase 7B Stage 2.

Builds A_sparse and D exactly as specified in phase6b_architecture_spec.md.
All parameters come from config.py. No scientific decisions are made here.
"""

import numpy as np
from . import config as cfg


def build_A_sparse() -> tuple[np.ndarray, int]:
    """
    Construct the 140x140 coupling matrix A_sparse.

    Returns (A_sparse, n_resample_attempts).
    Resamples off-diagonal weights up to MAX_RESAMPLE_ATTEMPTS times
    until spectral abscissa < SPECTRAL_ABSCISSA_THRESHOLD.
    Raises RuntimeError if stability cannot be achieved.
    """
    # Draw sparsity pattern once (invariant: never changed on resample)
    sparsity = _draw_sparsity_pattern()

    for attempt in range(cfg.MAX_RESAMPLE_ATTEMPTS + 1):
        # Seed offset: 0 for original, 100*attempt for resamples
        seed_offset = 100 * attempt
        A = _assemble_A(sparsity, seed_offset)
        abscissa = _spectral_abscissa(A)
        if abscissa < cfg.SPECTRAL_ABSCISSA_THRESHOLD:
            return A, attempt

    raise RuntimeError(
        f"Stability not achieved after {cfg.MAX_RESAMPLE_ATTEMPTS} resamples. "
        f"Final spectral abscissa: {abscissa:.4f}"
    )


def _draw_sparsity_pattern() -> dict:
    """
    Draw all binary sparsity indicators from their respective seeded RNGs.
    Returns a dict with keys 'oo', 'h1_in', 'h1_out', 'h2_in', 'h2_out'.
    Each value is a boolean ndarray of appropriate shape.
    """
    rng_oo = np.random.default_rng(cfg.SEEDS['oo_sparsity'])
    rng_h1 = np.random.default_rng(cfg.SEEDS['h1_sparsity'])
    rng_h2 = np.random.default_rng(cfg.SEEDS['h2_sparsity'])

    # Observed-observed: (100, 100) bool matrix, diagonal excluded
    oo = np.zeros((cfg.N_OBS, cfg.N_OBS), dtype=bool)
    for k in range(cfg.N_OBS):
        for j in range(cfg.N_OBS):
            if k == j:
                continue
            p = cfg.P_WITHIN if cfg.OBS_TO_MODULE[k] == cfg.OBS_TO_MODULE[j] else cfg.P_BETWEEN
            oo[k, j] = rng_oo.random() < p

    # H1 in-connections: (32, 100) bool — A[h1, obs]
    # Only draw for obs neurons in h1's assigned module
    h1_in = np.zeros((cfg.N_H1, cfg.N_OBS), dtype=bool)
    for h1_local, h1_global in enumerate(sorted(cfg.ALL_H1)):
        module = cfg.H1_TO_MODULE[h1_global]
        for obs in cfg.MODULE_OBS[module]:
            h1_in[h1_local, obs] = rng_h1.random() < cfg.P_H1_IN

    # H1 out-connections: (100, 32) bool — A[obs, h1]
    h1_out = np.zeros((cfg.N_OBS, cfg.N_H1), dtype=bool)
    for h1_local, h1_global in enumerate(sorted(cfg.ALL_H1)):
        module = cfg.H1_TO_MODULE[h1_global]
        for obs in cfg.MODULE_OBS[module]:
            h1_out[obs, h1_local] = rng_h1.random() < cfg.P_H1_OUT

    # H2 in-connections: (8, 100) bool — A[h2, obs]
    h2_in = np.zeros((cfg.N_H2, cfg.N_OBS), dtype=bool)
    for h2_local, h2_global in enumerate(sorted(cfg.SA)):
        target_obs = []
        for m in cfg.H2_TARGETS[h2_global]:
            target_obs.extend(cfg.MODULE_OBS[m])
        for obs in target_obs:
            h2_in[h2_local, obs] = rng_h2.random() < cfg.P_H2_IN

    # H2 out-connections: (100, 8) bool — A[obs, h2]
    h2_out = np.zeros((cfg.N_OBS, cfg.N_H2), dtype=bool)
    for h2_local, h2_global in enumerate(sorted(cfg.SA)):
        target_obs = []
        for m in cfg.H2_TARGETS[h2_global]:
            target_obs.extend(cfg.MODULE_OBS[m])
        for obs in target_obs:
            h2_out[obs, h2_local] = rng_h2.random() < cfg.P_H2_OUT

    return {'oo': oo, 'h1_in': h1_in, 'h1_out': h1_out, 'h2_in': h2_in, 'h2_out': h2_out}


def _assemble_A(sparsity: dict, seed_offset: int = 0) -> np.ndarray:
    """
    Assemble the full 140x140 A matrix from a sparsity pattern + fresh weights.
    seed_offset: added to weight seeds for resampling (0 = original draw).
    """
    rng_oo  = np.random.default_rng(cfg.SEEDS['oo_weights']  + seed_offset)
    rng_h1  = np.random.default_rng(cfg.SEEDS['h1_weights']  + seed_offset)
    rng_h2  = np.random.default_rng(cfg.SEEDS['h2_weights']  + seed_offset)

    A = np.zeros((cfg.N_TOTAL, cfg.N_TOTAL), dtype=np.float64)

    # Diagonal self-inhibition (P17 = -1.5)
    for k in range(cfg.N_TOTAL):
        A[k, k] = cfg.A_SELF

    h1_sorted = sorted(cfg.ALL_H1)  # [100, 101, ..., 131]
    h2_sorted = sorted(cfg.SA)       # [132, 133, ..., 139]

    # Obs-obs block (rows 0-99, cols 0-99)
    for k in range(cfg.N_OBS):
        for j in range(cfg.N_OBS):
            if k == j:
                continue
            if sparsity['oo'][k, j]:
                A[k, j] = rng_oo.standard_normal() * cfg.SIGMA_OBS_OBS

    # H1 in-connections: A[h1_global, obs]
    for h1_local, h1_global in enumerate(h1_sorted):
        for obs in range(cfg.N_OBS):
            if sparsity['h1_in'][h1_local, obs]:
                A[h1_global, obs] = rng_h1.standard_normal() * cfg.SIGMA_H1

    # H1 out-connections: A[obs, h1_global]
    for h1_local, h1_global in enumerate(h1_sorted):
        for obs in range(cfg.N_OBS):
            if sparsity['h1_out'][obs, h1_local]:
                A[obs, h1_global] = rng_h1.standard_normal() * cfg.SIGMA_H1

    # H2 in-connections: A[h2_global, obs]
    for h2_local, h2_global in enumerate(h2_sorted):
        for obs in range(cfg.N_OBS):
            if sparsity['h2_in'][h2_local, obs]:
                A[h2_global, obs] = rng_h2.standard_normal() * cfg.SIGMA_H2_IN

    # H2 out-connections: A[obs, h2_global]
    for h2_local, h2_global in enumerate(h2_sorted):
        for obs in range(cfg.N_OBS):
            if sparsity['h2_out'][obs, h2_local]:
                A[obs, h2_global] = rng_h2.standard_normal() * cfg.SIGMA_H2_OUT

    return A


def _spectral_abscissa(A: np.ndarray) -> float:
    """Return the spectral abscissa: max real part of eigenvalues of A."""
    eigenvalues = np.linalg.eigvals(A)
    return float(np.max(eigenvalues.real))


def build_D() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Construct the diffusion matrix D = D_diag + D_lr.

    D_diag = d_0 * I_{140}
    D_lr   = eps_lr * u * u^T   (u is a random unit vector, seed 48)

    Returns (D, D_sqrt, u) where D_sqrt = cholesky(D).
    """
    rng_u = np.random.default_rng(cfg.SEEDS['D_lr_u'])
    u_raw = rng_u.standard_normal(cfg.N_TOTAL)
    u = u_raw / np.linalg.norm(u_raw)  # unit vector

    D_diag = cfg.D_0 * np.eye(cfg.N_TOTAL)
    D_lr   = cfg.EPS_LR * np.outer(u, u)
    D      = D_diag + D_lr

    # Cholesky factor for efficient sampling: noise = D_sqrt @ N(0,I)
    D_sqrt = np.linalg.cholesky(D)

    return D, D_sqrt, u


def compute_B(z: float, gamma_H2: float = cfg.GAMMA_H2) -> np.ndarray:
    """
    Compute the state-dependent drive vector B(z).

    B_h(z) = gamma_H2 * z  for h in SA
    B_k(z) = 0             for k not in SA
    """
    B = np.zeros(cfg.N_TOTAL, dtype=np.float64)
    for h in cfg.SA:
        B[h] = gamma_H2 * z
    return B
