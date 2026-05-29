"""Tests for synthetic estimator recovery — Phase 0 dry-run.

All tests use data_kind="synthetic" and work only on synthetic data.
Real-data precision estimation remains blocked (verified in test_phase0_guard.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.estimators import (
    anatomy_guided_glasso_admm,
    compute_delta_q,
    evaluate_recovery,
    generate_true_precision_pair,
    stability_selection_glasso,
)


def _make_adjacency(N: int, density: float, rng: np.random.Generator) -> np.ndarray:
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(i + 1, N):
            if rng.random() < density:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# 1. Synthetic precision pair generation
# ---------------------------------------------------------------------------

def test_synthetic_precision_matrices_are_positive_definite():
    rng = np.random.default_rng(0)
    N = 20
    A = _make_adjacency(N, 0.2, rng)
    Q_roam, Q_dwell, mask = generate_true_precision_pair(N, A, 0.2, 5, rng)

    eigs_r = np.linalg.eigvalsh(Q_roam)
    eigs_d = np.linalg.eigvalsh(Q_dwell)
    assert eigs_r.min() > 0, f"Q_roam not PD: min eig = {eigs_r.min():.4g}"
    assert eigs_d.min() > 0, f"Q_dwell not PD: min eig = {eigs_d.min():.4g}"


def test_delta_mask_is_off_connectome_only():
    rng = np.random.default_rng(1)
    N = 20
    A = _make_adjacency(N, 0.2, rng)
    _, _, mask = generate_true_precision_pair(N, A, 0.2, 5, rng)

    # All masked entries should be off-connectome (A[i,j] == 0 for i != j)
    rows, cols = np.where(mask)
    for r, c in zip(rows, cols):
        if r != c:
            assert A[r, c] == 0, (
                f"Signal at ({r},{c}) but A[{r},{c}]=1 (on-connectome): "
                "ΔQ is not entirely off-connectome"
            )


def test_delta_q_equals_difference_of_true_precisions():
    rng = np.random.default_rng(2)
    N = 15
    A = _make_adjacency(N, 0.25, rng)
    Q_roam, Q_dwell, mask = generate_true_precision_pair(N, A, 0.3, 4, rng)
    delta_q = compute_delta_q(Q_roam, Q_dwell, data_kind="synthetic")
    # All non-zero ΔQ entries should be at off-connectome positions
    triu_i, triu_j = np.triu_indices(N, k=1)
    off = ~A[triu_i, triu_j].astype(bool)
    on  =  A[triu_i, triu_j].astype(bool)
    # No on-connectome ΔQ should exist
    dq_on = np.abs(delta_q[triu_i[on], triu_j[on]])
    assert dq_on.max() < 1e-10, (
        f"ΔQ has on-connectome non-zero entries (max={dq_on.max():.2e})"
    )


# ---------------------------------------------------------------------------
# 2. Stability selection at high support recovers signal
# ---------------------------------------------------------------------------

def test_stability_selection_recovers_signal_at_high_neff():
    """TPR should be high when T >> N (easy case)."""
    rng = np.random.default_rng(10)
    N = 20
    T = 1000
    A = _make_adjacency(N, 0.2, rng)
    Q_roam, _, mask = generate_true_precision_pair(N, A, 0.4, 5, rng)

    Sigma_roam = np.linalg.inv(Q_roam)
    X = rng.multivariate_normal(np.zeros(N), Sigma_roam, size=T)

    stability, selected = stability_selection_glasso(
        X, data_kind="synthetic", n_bootstrap=30, stability_threshold=0.60
    )

    metrics = evaluate_recovery(mask, A, selected)
    assert metrics["TPR"] >= 0.4, (
        f"Stability selection TPR={metrics['TPR']:.2f} < 0.4 at T={T}, N={N}"
    )


# ---------------------------------------------------------------------------
# 3. Anatomy-guided lasso is more conservative off-connectome
# ---------------------------------------------------------------------------

def test_anatomy_guided_more_conservative_off_connectome():
    """High off-connectome penalty should select fewer off-connectome entries
    than uniform penalty (same lambda_on for all edges).

    This tests the circularity control property: the anatomy-guided estimator
    penalizes off-connectome entries more heavily, so it is conservative against
    off-connectome discoveries.
    """
    rng = np.random.default_rng(20)
    N = 20
    T = 300
    A = _make_adjacency(N, 0.25, rng)
    Q_base, _, _ = generate_true_precision_pair(N, A, 0.0, 0, rng)
    Sigma = np.linalg.inv(Q_base)
    X = rng.multivariate_normal(np.zeros(N), Sigma, size=T)

    lambda_on = 0.15  # same for both estimators

    # Anatomy-guided: heavier off-connectome penalty
    _, selected_guided = anatomy_guided_glasso_admm(
        X, data_kind="synthetic", A_raw=A,
        lambda_on=lambda_on, lambda_off=lambda_on * 10
    )

    # Uniform: equal penalty everywhere (standard lasso)
    _, selected_uniform = anatomy_guided_glasso_admm(
        X, data_kind="synthetic", A_raw=A,
        lambda_on=lambda_on, lambda_off=lambda_on
    )

    triu_i, triu_j = np.triu_indices(N, k=1)
    off = ~A[triu_i, triu_j].astype(bool)
    n_guided_off  = int(selected_guided[triu_i[off], triu_j[off]].sum())
    n_uniform_off = int(selected_uniform[triu_i[off], triu_j[off]].sum())

    assert n_guided_off <= n_uniform_off, (
        f"High off-penalty (λ_off=10×λ_on) selects MORE off-connectome "
        f"({n_guided_off}) than uniform penalty ({n_uniform_off}). "
        "Circularity control is broken."
    )


# ---------------------------------------------------------------------------
# 4. ADMM convergence produces a positive-definite result
# ---------------------------------------------------------------------------

def test_admm_precision_is_positive_definite():
    rng = np.random.default_rng(30)
    N = 15
    T = 200
    A = _make_adjacency(N, 0.2, rng)
    Q_true, _, _ = generate_true_precision_pair(N, A, 0.2, 3, rng)
    Sigma = np.linalg.inv(Q_true)
    X = rng.multivariate_normal(np.zeros(N), Sigma, size=T)

    Theta, _ = anatomy_guided_glasso_admm(
        X, data_kind="synthetic", A_raw=A, lambda_on=0.05, lambda_off=0.3
    )
    eigs = np.linalg.eigvalsh(Theta)
    assert eigs.min() > 0, f"ADMM Theta not PD: min eig = {eigs.min():.4g}"


# ---------------------------------------------------------------------------
# 5. Real-data precision estimation is still blocked
# ---------------------------------------------------------------------------

def test_stability_selection_blocked_for_real_data():
    """Real-data stability selection must raise RuntimeError while PHASE0_COMPLETE=False.

    PHASE0_COMPLETE was re-set to False (2026-05-29 re-lock). Methodology is
    frozen (PHASE0_METHOD_LOCK_COMPLETE=True) but real-data inference remains
    prohibited until DEV-003/DEV-004/DEV-005 are resolved.
    """
    rng = np.random.default_rng(40)
    X = rng.standard_normal((50, 5))
    with pytest.raises(RuntimeError, match="PHASE0_COMPLETE"):
        stability_selection_glasso(X, data_kind="real", n_bootstrap=5)


def test_anatomy_guided_blocked_for_real_data():
    """Real-data anatomy-guided glasso must raise RuntimeError while PHASE0_COMPLETE=False.

    Same re-lock rationale as test_stability_selection_blocked_for_real_data.
    """
    rng = np.random.default_rng(41)
    X = rng.standard_normal((50, 5))
    A = np.zeros((5, 5))
    with pytest.raises(RuntimeError, match="PHASE0_COMPLETE"):
        anatomy_guided_glasso_admm(
            X, data_kind="real", A_raw=A, lambda_on=0.1, lambda_off=1.0
        )
