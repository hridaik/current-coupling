"""Estimator guardrails and scaffold functions for Phase 0.

The hard constraint is enforced here: precision-like operations on real
behavioral data are blocked until ``phase0_config.PHASE0_COMPLETE`` is True.

Synthetic-only functions (generate_true_precision_pair, stability_selection_glasso,
anatomy_guided_glasso_admm) do not handle real data and require data_kind="synthetic"
to be passed through to any underlying precision computation.
"""

from __future__ import annotations

import importlib
from typing import Literal, Sequence

import numpy as np

DataKind = Literal["synthetic", "real"]


def _phase0_complete() -> bool:
    config = importlib.import_module("phase0_config")
    return bool(getattr(config, "PHASE0_COMPLETE", False))


def _require_precision_allowed(data_kind: DataKind, operation: str) -> None:
    if data_kind not in {"synthetic", "real"}:
        raise ValueError('data_kind must be "synthetic" or "real"')
    if data_kind == "real" and not _phase0_complete():
        raise RuntimeError(
            f"{operation} on real data is blocked while PHASE0_COMPLETE is False. "
            "Phase 0 forbids real-data precision matrices, inverse covariance, "
            "graphical-lasso estimates, and Delta-Q-like objects."
        )


def _validate_neuron_list(neuron_list: Sequence[str] | None, n_neurons: int) -> None:
    if neuron_list is None:
        return
    if len(neuron_list) != n_neurons:
        raise ValueError(
            f"neuron_list has length {len(neuron_list)}, expected {n_neurons}"
        )


def _as_square_matrix(matrix: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(matrix, dtype=float)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError(f"{name} must be a square 2D matrix")
    return array


def inverse_covariance(
    covariance: np.ndarray,
    *,
    data_kind: DataKind,
    neuron_list: Sequence[str] | None = None,
) -> np.ndarray:
    """Return a precision matrix from a covariance matrix.

    This function is allowed for synthetic data during Phase 0 and blocked for
    real data until Phase 0 is complete.
    """

    _require_precision_allowed(data_kind, "inverse covariance")
    covariance = _as_square_matrix(covariance, "covariance")
    _validate_neuron_list(neuron_list, covariance.shape[0])
    print(f"inverse_covariance condition_number={np.linalg.cond(covariance):.6g}")
    return np.linalg.inv(covariance)


def estimate_precision(
    covariance: np.ndarray,
    *,
    data_kind: DataKind,
    neuron_list: Sequence[str] | None = None,
) -> np.ndarray:
    """Estimate a precision matrix from covariance.

    The scaffold implementation delegates to direct inversion for synthetic
    dry-run use only.
    """

    _require_precision_allowed(data_kind, "precision estimation")
    return inverse_covariance(
        covariance,
        data_kind=data_kind,
        neuron_list=neuron_list,
    )


def graphical_lasso_estimate(
    samples: np.ndarray,
    *,
    data_kind: DataKind,
    neuron_list: Sequence[str] | None = None,
    alpha: float = 0.01,
) -> np.ndarray:
    """Stub graphical-lasso-style precision estimate.

    The real estimator is implemented in later stages. The scaffold keeps the
    guardrail active and returns a synthetic-only inverse sample covariance.
    """

    _require_precision_allowed(data_kind, "graphical-lasso estimation")
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 2:
        raise ValueError("samples must be a 2D array with shape T x N")
    _validate_neuron_list(neuron_list, samples.shape[1])
    covariance = np.cov(samples, rowvar=False)
    regularized = covariance + alpha * np.eye(covariance.shape[0])
    return inverse_covariance(
        regularized,
        data_kind=data_kind,
        neuron_list=neuron_list,
    )


def compute_delta_q(
    q_left: np.ndarray,
    q_right: np.ndarray,
    *,
    data_kind: DataKind,
    neuron_list: Sequence[str] | None = None,
) -> np.ndarray:
    """Compute a Delta-Q-like difference with the Phase 0 guardrail applied."""

    _require_precision_allowed(data_kind, "Delta-Q-like computation")
    q_left = _as_square_matrix(q_left, "q_left")
    q_right = _as_square_matrix(q_right, "q_right")
    if q_left.shape != q_right.shape:
        raise ValueError("q_left and q_right must have the same shape")
    _validate_neuron_list(neuron_list, q_left.shape[0])
    return q_left - q_right


# ---------------------------------------------------------------------------
# Synthetic data generation — Phase 0 estimator dry-run support
# ---------------------------------------------------------------------------

def generate_true_precision_pair(
    N: int,
    A_raw: np.ndarray,
    effect_size: float,
    n_signal_pairs: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a (Q_roam, Q_dwell, delta_mask) triple for synthetic dry-runs.

    Both precision matrices are positive-definite. ΔQ = Q_roam - Q_dwell is
    non-zero ONLY at off-connectome positions (delta_mask).

    Parameters
    ----------
    N : int — number of neurons
    A_raw : (N, N) binary adjacency — connectome support (undirected)
    effect_size : float — magnitude of ΔQ entries relative to σ of on-connectome Q entries
    n_signal_pairs : int — number of off-connectome pairs to set non-zero
    rng : numpy random generator

    Returns
    -------
    Q_roam : (N, N) positive-definite precision matrix
    Q_dwell : (N, N) positive-definite precision matrix
    delta_mask : (N, N) bool — True at signal off-connectome entries
    """
    A = np.asarray(A_raw, dtype=float)
    A = np.maximum(A, A.T)   # ensure symmetric
    np.fill_diagonal(A, 0)

    # --- Build Q_base using diagonal dominance ---
    # Off-diagonal entries at connectome edges: random in [-w, w]
    w = 0.35
    triu_i, triu_j = np.triu_indices(N, k=1)
    edge_mask = A[triu_i, triu_j].astype(bool)
    edge_weights = rng.uniform(-w, w, size=edge_mask.sum())

    W = np.zeros((N, N))
    W[triu_i[edge_mask], triu_j[edge_mask]] = edge_weights
    W = W + W.T

    # Diagonal: row-sum of absolute off-diagonal + slack → diagonal dominance
    row_abs_sums = np.abs(W).sum(axis=1)
    diag_entries = row_abs_sums + 0.5
    Q_base = W + np.diag(diag_entries)

    # Verify PD (diagonal dominance guarantees it, but check numerically)
    eigs = np.linalg.eigvalsh(Q_base)
    if eigs.min() < 1e-6:
        Q_base += (1e-6 - eigs.min() + 0.01) * np.eye(N)

    # --- Select signal off-connectome pairs ---
    off_i, off_j = np.triu_indices(N, k=1)
    off_mask_edges = ~A[off_i, off_j].astype(bool)
    cand_i = off_i[off_mask_edges]
    cand_j = off_j[off_mask_edges]

    n_actual = min(n_signal_pairs, len(cand_i))
    idx = rng.choice(len(cand_i), size=n_actual, replace=False)
    sig_i = cand_i[idx]
    sig_j = cand_j[idx]

    # Scale effect to achieve the desired partial-correlation change.
    # Partial correlation ρ_{ij.rest} = -Q_{ij} / sqrt(Q_{ii} * Q_{jj}).
    # To get Δρ ≈ effect_size, set delta_val ≈ effect_size * mean(Q_diag).
    mean_diag = float(Q_base.diagonal().mean())
    delta_val = effect_size * mean_diag   # gives |Δρ| ≈ effect_size

    # Q_roam = Q_base + ΔQ at signal pairs
    Q_roam = Q_base.copy()
    for r, c in zip(sig_i, sig_j):
        Q_roam[r, c] += delta_val
        Q_roam[c, r] += delta_val

    # Ensure Q_roam stays PD
    eigs_r = np.linalg.eigvalsh(Q_roam)
    if eigs_r.min() < 1e-6:
        Q_roam += (1e-6 - eigs_r.min() + 0.01) * np.eye(N)

    Q_dwell = Q_base.copy()

    delta_mask = np.zeros((N, N), dtype=bool)
    for r, c in zip(sig_i, sig_j):
        delta_mask[r, c] = True
        delta_mask[c, r] = True

    # Condition number diagnostics (required by AGENTS.md)
    print(f"  generate_true_precision_pair: "
          f"cond(Q_roam)={np.linalg.cond(Q_roam):.3g}  "
          f"cond(Q_dwell)={np.linalg.cond(Q_dwell):.3g}  "
          f"min_eig_roam={eigs_r.min():.4g}  "
          f"n_signal={n_actual}")

    return Q_roam, Q_dwell, delta_mask


def _bic_alpha(X: np.ndarray, alpha_grid: np.ndarray) -> float:
    """Choose graphical-lasso alpha via BIC on the empirical covariance of X.

    BIC = -T*(log det Q - tr(S Q)) + k * log(T)
    where k = number of selected off-diagonal edges (undirected).
    """
    from sklearn.covariance import GraphicalLasso

    T, N = X.shape
    S = np.cov(X, rowvar=False)
    best_bic = np.inf
    best_alpha = alpha_grid[0]

    for alpha in alpha_grid:
        try:
            gl = GraphicalLasso(alpha=float(alpha), max_iter=300, tol=1e-3)
            gl.fit(X)
            Q = gl.precision_
            sign, logdet = np.linalg.slogdet(Q)
            if sign <= 0:
                continue
            log_lik = 0.5 * T * (logdet - np.trace(S @ Q))
            k = int(np.sum(np.abs(Q) > 1e-6)) - N  # off-diag non-zeros (counted twice → /2)
            k = max(k // 2, 0)
            bic = -2 * log_lik + k * np.log(T)
            if bic < best_bic:
                best_bic = bic
                best_alpha = float(alpha)
        except Exception:
            continue

    return best_alpha


def stability_selection_glasso(
    X: np.ndarray,
    *,
    data_kind: DataKind,
    n_bootstrap: int = 50,
    alpha_grid: np.ndarray | None = None,
    stability_threshold: float = 0.75,
    neuron_list: Sequence[str] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Stability-selection graphical lasso (discovery estimator).

    Phase 0 guard: blocked for real data.

    Algorithm (per task.md Stage 7):
    1. Select alpha via BIC on full data.
    2. B=n_bootstrap half-data bootstrap subsamples (without replacement).
    3. For each subsample: fit GraphicalLasso(alpha) on half the frames.
    4. Stability score = fraction of subsamples where each edge was selected.
    5. Return: stability_scores matrix and binary selection at threshold.

    Parameters
    ----------
    X : (T, N) array — neural activity (synthetic only during Phase 0)
    data_kind : "synthetic" or "real"
    n_bootstrap : int — number of bootstrap subsamples
    alpha_grid : 1D array of candidate regularization values (or None for default)
    stability_threshold : float — edge selection threshold (default 0.75)
    neuron_list : optional sequence of neuron names

    Returns
    -------
    stability_scores : (N, N) array in [0, 1]
    selected : (N, N) bool — True where stability_scores >= threshold
    """
    from sklearn.covariance import GraphicalLasso

    _require_precision_allowed(data_kind, "stability_selection_glasso")
    X = np.asarray(X, dtype=float)
    T, N = X.shape
    _validate_neuron_list(neuron_list, N)

    if alpha_grid is None:
        alpha_grid = np.logspace(-2.0, 0.0, 15)

    # Global BIC alpha on full data
    alpha_bic = _bic_alpha(X, alpha_grid)
    print(f"  stability_selection: T={T}  N={N}  alpha_bic={alpha_bic:.4g}")

    T_boot = T // 2
    rng = np.random.default_rng(42)
    stability_counts = np.zeros((N, N))

    for _ in range(n_bootstrap):
        idx = rng.choice(T, size=T_boot, replace=False)
        X_boot = X[idx]
        try:
            gl = GraphicalLasso(alpha=alpha_bic, max_iter=300, tol=1e-3)
            gl.fit(X_boot)
            Q_boot = gl.precision_
            # Selected edges: off-diagonal entries above threshold
            sel = np.abs(Q_boot) > 1e-6
            np.fill_diagonal(sel, False)
            stability_counts += sel.astype(float)
        except Exception:
            pass  # subsample may be ill-conditioned; skip

    stability_scores = stability_counts / n_bootstrap
    selected = stability_scores >= stability_threshold

    n_sel = int(np.sum(selected)) // 2
    print(f"  stability_selection: n_selected_edges={n_sel}  "
          f"(threshold={stability_threshold}  B={n_bootstrap})")
    print(f"  stability_selection condition_number=n/a (applied to subsamples)")

    return stability_scores, selected


def _glasso_admm(
    S: np.ndarray,
    Lambda: np.ndarray,
    rho: float = 1.0,
    max_iter: int = 300,
    tol: float = 1e-4,
) -> np.ndarray:
    """ADMM for graphical lasso with per-entry L1 penalty.

    Minimizes: -log det(Theta) + tr(S Theta) + sum_{i!=j} Lambda[i,j] |Theta[i,j]|

    Parameters
    ----------
    S : (N, N) empirical covariance
    Lambda : (N, N) non-negative penalty matrix (0 on diagonal)
    rho : ADMM step size
    max_iter : maximum iterations
    tol : convergence tolerance on ||Theta - Z||_inf

    Returns
    -------
    Theta : (N, N) estimated precision matrix (positive definite)
    """
    N = S.shape[0]
    Theta = np.eye(N)
    Z     = np.eye(N)
    U     = np.zeros((N, N))

    for it in range(max_iter):
        # Theta update: solve -Theta^{-1} + rho*(Theta - (Z-U)) + S = 0
        # Equivalently: eigendecompose B = (Z - U - S/rho)
        # Theta_ij = Q_i * f(d_i) * Q_i^T where f(d) = (d + sqrt(d^2 + 4/rho)) / 2
        B = Z - U - S / rho
        B_sym = (B + B.T) / 2.0   # ensure symmetry
        eigvals, eigvecs = np.linalg.eigh(B_sym)
        new_eigs = (eigvals + np.sqrt(eigvals ** 2 + 4.0 / rho)) / 2.0
        Theta = eigvecs @ np.diag(new_eigs) @ eigvecs.T

        # Z update: per-entry soft threshold
        W = Theta + U
        Z_new = np.sign(W) * np.maximum(np.abs(W) - Lambda / rho, 0.0)
        diag_idx = np.arange(N)
        Z_new[diag_idx, diag_idx] = W[diag_idx, diag_idx]   # no penalty on diagonal

        # U update
        res = Theta - Z_new
        U = U + res

        if np.max(np.abs(res)) < tol:
            break

        Z = Z_new

    return Theta


def anatomy_guided_glasso_admm(
    X: np.ndarray,
    *,
    data_kind: DataKind,
    A_raw: np.ndarray,
    lambda_on: float,
    lambda_off: float,
    neuron_list: Sequence[str] | None = None,
    tol: float = 1e-4,
    max_iter: int = 300,
) -> tuple[np.ndarray, np.ndarray]:
    """Anatomy-guided graphical lasso via ADMM (confirmation estimator).

    Phase 0 guard: blocked for real data.

    Connectome-weighted penalty:
      lambda[i,j] = lambda_on  if A_raw[i,j] = 1  (on-connectome)
      lambda[i,j] = lambda_off if A_raw[i,j] = 0  (off-connectome, heavier penalty)

    Parameters
    ----------
    X : (T, N) array
    data_kind : "synthetic" or "real"
    A_raw : (N, N) binary connectome adjacency
    lambda_on : penalty for on-connectome entries
    lambda_off : penalty for off-connectome entries (typically > lambda_on)
    neuron_list : optional
    tol, max_iter : ADMM convergence settings

    Returns
    -------
    Theta : (N, N) precision matrix
    selected : (N, N) bool — True for non-zero off-diagonal entries
    """
    _require_precision_allowed(data_kind, "anatomy_guided_glasso_admm")
    X = np.asarray(X, dtype=float)
    T, N = X.shape
    _validate_neuron_list(neuron_list, N)

    A = np.asarray(A_raw, dtype=float)
    A = np.maximum(A, A.T)
    np.fill_diagonal(A, 0)

    # Build per-entry penalty matrix
    Lambda = np.where(A > 0, lambda_on, lambda_off).astype(float)
    np.fill_diagonal(Lambda, 0.0)

    S = np.cov(X, rowvar=False)
    # Ridge regularization for ill-conditioned S (T < N case)
    eigs_s = np.linalg.eigvalsh(S)
    if eigs_s.min() < 1e-6 or np.linalg.cond(S) > 1e10:
        ridge = max(1e-4, -eigs_s.min() + 1e-4)
        S = S + ridge * np.eye(N)
    print(f"  anatomy_guided_glasso: T={T}  N={N}  "
          f"lambda_on={lambda_on:.4g}  lambda_off={lambda_off:.4g}  "
          f"cond(S)={np.linalg.cond(S):.3g}")

    Theta = _glasso_admm(S, Lambda, tol=tol, max_iter=max_iter)
    print(f"  anatomy_guided_glasso: cond(Theta)={np.linalg.cond(Theta):.3g}")

    selected = np.abs(Theta) > 1e-6
    np.fill_diagonal(selected, False)
    n_sel = int(np.sum(selected)) // 2
    print(f"  anatomy_guided_glasso: n_selected_edges={n_sel}")

    return Theta, selected


def evaluate_recovery(
    true_delta_mask: np.ndarray,
    A_raw: np.ndarray,
    discovered: np.ndarray,
) -> dict:
    """Compute TPR and FPR for synthetic ΔQ recovery.

    Parameters
    ----------
    true_delta_mask : (N, N) bool — True where true ΔQ is non-zero (off-connectome signal)
    A_raw : (N, N) binary connectome — off-connectome entries are the target set
    discovered : (N, N) bool — estimated non-zero entries (from estimator)

    Returns
    -------
    dict with keys: TPR, FPR, n_true_signal, n_discovered, n_true_positives
    """
    # Off-diagonal positions only (undirected: upper triangle)
    triu_i, triu_j = np.triu_indices(true_delta_mask.shape[0], k=1)

    signal_mask  = true_delta_mask[triu_i, triu_j]   # true positives (off-connectome signal)
    off_mask     = ~A_raw[triu_i, triu_j].astype(bool)  # all off-connectome pairs
    on_mask      = A_raw[triu_i, triu_j].astype(bool)   # all on-connectome pairs
    disc_triu    = discovered[triu_i, triu_j]

    n_true_signal = int(signal_mask.sum())
    n_off_total   = int(off_mask.sum())
    n_on_total    = int(on_mask.sum())

    # TPR: fraction of true signal pairs discovered
    tp = int((signal_mask & disc_triu).sum())
    tpr = tp / max(n_true_signal, 1)

    # FPR: among on-connectome pairs, fraction incorrectly discovered
    fp_on  = int((on_mask & disc_triu).sum())
    fpr_on = fp_on / max(n_on_total, 1)

    # Discovery rate on off-connectome non-signal (false alarm rate)
    fp_off  = int((off_mask & ~signal_mask & disc_triu).sum())
    fpr_off = fp_off / max(n_off_total - n_true_signal, 1)

    return {
        "TPR"              : tpr,
        "FPR_on_connectome": fpr_on,
        "FPR_off_noise"    : fpr_off,
        "n_true_signal"    : n_true_signal,
        "n_true_positives" : tp,
        "n_discovered_off" : int((off_mask & disc_triu).sum()),
        "n_discovered_on"  : fp_on,
    }


# ---------------------------------------------------------------------------
# Stage 8 robustness: nonstationary + blockwise/pooled synthetic generation
# ---------------------------------------------------------------------------

def generate_drifting_data(
    Q_roam: np.ndarray,
    Q_dwell_start: np.ndarray,
    Q_dwell_end: np.ndarray,
    T: int,
    drift_fraction: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate (X_roam, X_dwell) where dwell covariance drifts over the recording.

    X_roam is stationary (from Q_roam throughout).
    X_dwell is non-stationary: first (1-drift_fraction)*T frames from Q_dwell_start,
    last drift_fraction*T frames from Q_dwell_end.

    drift_fraction=0 → fully stationary dwell.
    drift_fraction=0.5 → half-recording drift (mimics observed covariance drift).
    drift_fraction=1.0 → complete transition from start to end covariance.

    This mimics the photobleaching / neuromodulatory drift pattern identified in
    Stage 6 (NONSTATIONARITY_FRACTION=1.0; first/second half covariance drift ≈ 0.85-1.05).
    """
    N = Q_roam.shape[0]
    Sigma_roam        = np.linalg.inv(Q_roam)
    Sigma_dwell_start = np.linalg.inv(Q_dwell_start)
    Sigma_dwell_end   = np.linalg.inv(Q_dwell_end)

    X_roam = rng.multivariate_normal(np.zeros(N), Sigma_roam, size=T)

    T_stable = int(T * (1.0 - drift_fraction))
    T_drift  = T - T_stable

    parts = []
    if T_stable > 0:
        parts.append(rng.multivariate_normal(np.zeros(N), Sigma_dwell_start, size=T_stable))
    if T_drift > 0:
        parts.append(rng.multivariate_normal(np.zeros(N), Sigma_dwell_end, size=T_drift))
    X_dwell = np.vstack(parts) if len(parts) > 1 else parts[0]

    return X_roam, X_dwell


def generate_dwell_drift_precision(
    Q_base: np.ndarray,
    A_raw: np.ndarray,
    drift_amplitude: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Produce Q_dwell_start and Q_dwell_end by drifting on-connectome entries.

    The topology (which entries are non-zero) is preserved; only amplitudes change.
    The signal ΔQ (Q_roam vs Q_dwell) is not affected by this drift — drift is in
    background structure, not in signal entries.

    drift_amplitude controls how much Q_dwell on-connectome entries change in the
    second half of the recording, as a fraction of their initial magnitude.
    """
    N = Q_base.shape[0]
    A = np.asarray(A_raw, dtype=float)
    A = np.maximum(A, A.T)
    np.fill_diagonal(A, 0)

    triu_i, triu_j = np.triu_indices(N, k=1)
    edge_mask = A[triu_i, triu_j].astype(bool)
    edge_rows  = triu_i[edge_mask]
    edge_cols  = triu_j[edge_mask]

    # Current on-connectome off-diagonal entries
    W_start = Q_base.copy()

    # Generate a perturbation to existing on-connectome entries
    existing_vals = W_start[edge_rows, edge_cols]
    perturbation  = rng.uniform(-drift_amplitude, drift_amplitude, size=len(edge_rows))
    delta_W = existing_vals * perturbation   # fractional change

    W_end = W_start.copy()
    W_end[edge_rows, edge_cols] += delta_W
    W_end[edge_cols, edge_rows] += delta_W

    # Restore diagonal dominance if broken
    def make_pd(Q):
        eigs = np.linalg.eigvalsh(Q)
        if eigs.min() < 1e-6:
            Q = Q + (1e-6 - eigs.min() + 0.05) * np.eye(N)
        return Q

    Q_start = make_pd(W_start)
    Q_end   = make_pd(W_end)
    return Q_start, Q_end


def stability_scores_only(
    X: np.ndarray,
    *,
    data_kind: DataKind,
    n_bootstrap: int = 30,
    alpha_grid: np.ndarray | None = None,
) -> np.ndarray:
    """Return raw stability scores (continuous, in [0,1]) without thresholding.

    Useful for topology analysis: a lower stability threshold (e.g. 0.50) captures
    edges that are consistently detected but at lower signal-to-noise, which
    corresponds to topology recovery (edge present/absent) rather than amplitude
    recovery (precise coefficient value).
    """
    from sklearn.covariance import GraphicalLasso

    _require_precision_allowed(data_kind, "stability_scores_only")
    X = np.asarray(X, dtype=float)
    T, N = X.shape

    if alpha_grid is None:
        alpha_grid = np.logspace(-2.0, 0.0, 15)

    alpha_bic = _bic_alpha(X, alpha_grid)
    T_boot = T // 2
    rng = np.random.default_rng(99)
    counts = np.zeros((N, N))

    for _ in range(n_bootstrap):
        idx = rng.choice(T, size=T_boot, replace=False)
        try:
            gl = GraphicalLasso(alpha=alpha_bic, max_iter=300, tol=1e-3)
            gl.fit(X[idx])
            sel = np.abs(gl.precision_) > 1e-6
            np.fill_diagonal(sel, False)
            counts += sel.astype(float)
        except Exception:
            pass

    return counts / n_bootstrap


def blockwise_stability_selection(
    X: np.ndarray,
    *,
    data_kind: DataKind,
    block_assignments: np.ndarray,
    n_bootstrap: int = 30,
    stability_threshold: float = 0.75,
    alpha_grid: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Blockwise stability selection: fit each neuron block independently.

    For each block, extracts the sub-matrix of X and runs stability selection.
    Only within-block edges are estimated; cross-block edges are set to zero.

    This exploits the observation that if the true precision matrix is block-diagonal
    or has strong block structure, fitting N_block × N_block sub-problems with
    T / N_block^2 effective support is more tractable than fitting the full N × N system.

    Parameters
    ----------
    X : (T, N) array
    data_kind : "synthetic" or "real"
    block_assignments : (N,) int array — block index per neuron (0-indexed)
    n_bootstrap, stability_threshold, alpha_grid : as in stability_selection_glasso

    Returns
    -------
    stability_scores : (N, N) float in [0,1]  (zeros for cross-block pairs)
    selected : (N, N) bool
    """
    _require_precision_allowed(data_kind, "blockwise_stability_selection")
    X = np.asarray(X, dtype=float)
    T, N = X.shape
    blocks = np.asarray(block_assignments)
    unique_blocks = np.unique(blocks)

    stability_full = np.zeros((N, N))
    selected_full  = np.zeros((N, N), dtype=bool)

    for blk in unique_blocks:
        idx_b = np.where(blocks == blk)[0]
        N_b   = len(idx_b)
        if N_b < 2:
            continue
        X_b = X[:, idx_b]
        stab_b, sel_b = stability_selection_glasso(
            X_b,
            data_kind=data_kind,
            n_bootstrap=n_bootstrap,
            stability_threshold=stability_threshold,
            alpha_grid=alpha_grid,
        )
        # Insert block results into full matrices
        for i_local, i_full in enumerate(idx_b):
            for j_local, j_full in enumerate(idx_b):
                if i_local != j_local:
                    stability_full[i_full, j_full] = stab_b[i_local, j_local]
                    selected_full[i_full, j_full]  = sel_b[i_local, j_local]

    return stability_full, selected_full


def generate_pooled_animal_data(
    Q_roam: np.ndarray,
    Q_dwell: np.ndarray,
    n_animals: int,
    T_per_animal: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate pooled multi-animal synthetic data (X_roam_pooled, X_dwell_pooled).

    Each animal contributes T_per_animal independent frames from the same
    Q_roam / Q_dwell. Pooling adds frames independently (no cross-animal
    autocorrelation), consistent with the n_eff_pooled additive aggregation
    used in Stage 6.
    """
    N = Q_roam.shape[0]
    Sigma_roam  = np.linalg.inv(Q_roam)
    Sigma_dwell = np.linalg.inv(Q_dwell)

    X_roam_list, X_dwell_list = [], []
    for _ in range(n_animals):
        X_roam_list.append(
            rng.multivariate_normal(np.zeros(N), Sigma_roam, size=T_per_animal)
        )
        X_dwell_list.append(
            rng.multivariate_normal(np.zeros(N), Sigma_dwell, size=T_per_animal)
        )

    return np.vstack(X_roam_list), np.vstack(X_dwell_list)
