"""
Baseline engine — Phase 8B.

Implements B1–B6 exactly as specified in phase8a_baseline_spec.md.
No baseline may be added or modified after Phase 8B begins.
"""

import numpy as np
import scipy.special
from . import config8 as cfg
from .input_validator import build_output_arrays

VALID_BASELINES = frozenset({'B1', 'B2', 'B3', 'B4', 'B5', 'B6'})


# ---------------------------------------------------------------------------
# Output format constructor
# ---------------------------------------------------------------------------

def _make_pred_map(score_fn) -> tuple[dict, dict]:
    """
    Build a pred_map from a score_fn(i, j) → class_prob dict.
    Returns (pred_map, output_arrays).
    """
    n_obs = 100
    pred_map = {}
    for i in range(n_obs):
        for j in range(n_obs):
            if i == j:
                continue
            cp = score_fn(i, j)
            pred_map[(i, j)] = {
                'i': i, 'j': j,
                'class_prob': {k: float(cp[k]) for k in cfg.CLASSES},
                'class_pred': max(cp, key=cp.get),
            }
    arrays = build_output_arrays(pred_map)
    return pred_map, arrays


def _softmax_to_classprob(
    s_score: float, c_score: float, m_score: float, n_score: float,
    temp: float = 5.0,
) -> dict[str, float]:
    """Convert 4-element scores to class_prob via softmax with temperature."""
    logits = np.array([s_score, c_score, m_score, n_score]) * temp
    probs  = scipy.special.softmax(logits)
    return {k: float(probs[i]) for i, k in enumerate(cfg.CLASSES)}


# ---------------------------------------------------------------------------
# B1: Null / Chance
# ---------------------------------------------------------------------------

def run_b1_null(rng_seed: int = 1) -> tuple[dict, dict]:
    """
    B1: Uniform random class probabilities for every pair.
    Deterministic given seed (for reproducibility checks).
    """
    rng = np.random.default_rng(rng_seed)

    def score_fn(i, j):
        r = rng.dirichlet(np.ones(4))
        return dict(zip(cfg.CLASSES, r))

    return _make_pred_map(score_fn)


def run_b1_uniform() -> tuple[dict, dict]:
    """B1 uniform variant: exactly 0.25 per class (used for metric validation)."""
    def score_fn(i, j):
        return {k: 0.25 for k in cfg.CLASSES}
    return _make_pred_map(score_fn)


# ---------------------------------------------------------------------------
# B2: Marginal frequency prior
# ---------------------------------------------------------------------------

def run_b2_marginal() -> tuple[dict, dict]:
    """B2: Assign committed class frequencies as constant probability for all pairs."""
    total = sum(cfg.COMMITTED_CLASS_COUNTS.values())
    const_prob = {k: cfg.COMMITTED_CLASS_COUNTS[k] / total for k in cfg.CLASSES}

    def score_fn(i, j):
        return const_prob

    return _make_pred_map(score_fn)


# ---------------------------------------------------------------------------
# B3: Pairwise correlation
# ---------------------------------------------------------------------------

def run_b3_correlation(runs: list[dict]) -> tuple[dict, dict]:
    """
    B3: |Pearson corr(y_i, y_j)| averaged across runs.
    Score mapped to class_prob via pre-specified softmax.
    """
    n_obs = 100
    corr_accum = np.zeros((n_obs, n_obs), dtype=np.float64)

    for run in runs:
        y = run['y'].astype(np.float64)  # (T_eff, n_obs)
        y_c = y - y.mean(axis=0)
        std = y_c.std(axis=0)
        std[std < 1e-12] = 1.0  # avoid division by zero
        y_n = y_c / std
        C = (y_n.T @ y_n) / y.shape[0]  # correlation matrix (n_obs, n_obs)
        corr_accum += np.abs(C)

    corr_mean = corr_accum / len(runs)

    def score_fn(i, j):
        cor = float(corr_mean[i, j])
        # S,C,M score = |corr|; N score = -|corr|
        return _softmax_to_classprob(cor, cor, cor, -cor, temp=cfg.B3_SOFTMAX_TEMP)

    return _make_pred_map(score_fn)


# ---------------------------------------------------------------------------
# B4: Graphical Lasso
# ---------------------------------------------------------------------------

def _glasso_log_likelihood(prec: np.ndarray, S_val: np.ndarray, n_val: int) -> float:
    """Gaussian log-likelihood on validation data given precision matrix."""
    sign, logdet = np.linalg.slogdet(prec)
    if sign <= 0:
        return -np.inf
    # log L = (n/2) * [log|Ω| - tr(S_val Ω)] + const
    return (n_val / 2) * (float(logdet) - float(np.trace(S_val @ prec)))


def _compute_bic(prec: np.ndarray, S_val: np.ndarray, n_val: int) -> float:
    """BIC = -2*log_likelihood + k*log(n) where k = non-zero off-diagonal entries."""
    ll = _glasso_log_likelihood(prec, S_val, n_val)
    # k = number of non-zero off-diagonal entries
    p = prec.shape[0]
    mask = np.abs(prec) > 1e-10
    np.fill_diagonal(mask, False)
    k = int(mask.sum())
    return -2 * ll + k * np.log(n_val)


def run_b4_glasso(runs: list[dict]) -> tuple[dict, dict]:
    """
    B4: Graphical lasso precision matrix with BIC-selected alpha.
    Training: runs 0-3. Validation: run 4.
    Alpha grid: cfg.B4_ALPHA_GRID.
    """
    from sklearn.covariance import GraphicalLasso

    n_obs = 100

    # Pool training data
    Y_train = np.vstack([runs[r]['y'] for r in cfg.B4_TRAIN_RUNS])  # (192000, 100)
    Y_val   = runs[cfg.B4_VAL_RUN]['y']                              # (48000, 100)

    # Center
    mu_train = Y_train.mean(axis=0)
    Y_train_c = Y_train - mu_train
    Y_val_c   = Y_val   - mu_train  # use training mean for val

    # Sample covariance for validation data
    n_val = Y_val_c.shape[0]
    S_val = (Y_val_c.T @ Y_val_c) / n_val

    best_bic   = np.inf
    best_prec  = None
    best_alpha = None

    for alpha in cfg.B4_ALPHA_GRID:
        try:
            gl = GraphicalLasso(alpha=alpha, max_iter=500, tol=1e-4)
            gl.fit(Y_train_c)
            prec = gl.precision_
            bic  = _compute_bic(prec, S_val, n_val)
            if bic < best_bic:
                best_bic   = bic
                best_prec  = prec
                best_alpha = alpha
        except Exception:
            continue  # convergence failure; skip

    if best_prec is None:
        # All alphas failed; fall back to B2
        print('B4 WARNING: all alpha values failed; falling back to B2')
        return run_b2_marginal()

    def score_fn(i, j):
        omega_ij = float(np.abs(best_prec[i, j]))
        # S,C,M score = |Ω|; N score = -|Ω|
        return _softmax_to_classprob(omega_ij, omega_ij, omega_ij, -omega_ij,
                                     temp=cfg.B4_SOFTMAX_TEMP)

    pred_map, arrays = _make_pred_map(score_fn)

    # Attach metadata
    arrays['_b4_metadata'] = {
        'best_alpha': best_alpha,
        'best_bic':   float(best_bic),
        'alpha_grid': cfg.B4_ALPHA_GRID,
    }
    return pred_map, arrays


# ---------------------------------------------------------------------------
# B5: State-dependent correlation difference
# ---------------------------------------------------------------------------

def run_b5_state_delta_corr(runs: list[dict]) -> tuple[dict, dict]:
    """
    B5: |ΔC| = |C_high_z - C_low_z|, averaged across runs.
    Split on median(z_oracle) per run.
    """
    n_obs = 100
    delta_c_accum = np.zeros((n_obs, n_obs), dtype=np.float64)
    n_runs_used = 0

    for run in runs:
        if run.get('z_oracle') is None:
            continue  # skip runs without z (blind_z condition)
        y = run['y'].astype(np.float64)
        z = run['z_oracle'].astype(np.float64)
        z_median = np.median(z)
        high_idx = z > z_median
        low_idx  = ~high_idx

        def _corr(Y):
            Y_c = Y - Y.mean(axis=0)
            std = Y_c.std(axis=0)
            std[std < 1e-12] = 1.0
            Y_n = Y_c / std
            return (Y_n.T @ Y_n) / Y.shape[0]

        C_high = _corr(y[high_idx])
        C_low  = _corr(y[low_idx])
        delta_c_accum += np.abs(C_high - C_low)
        n_runs_used += 1

    if n_runs_used == 0:
        # blind_z condition has no z_oracle; fall back to B3
        return run_b3_correlation(runs)

    delta_c_mean = delta_c_accum / n_runs_used

    def score_fn(i, j):
        dc = float(delta_c_mean[i, j])
        # C,M high score; S,N low score
        return _softmax_to_classprob(-dc, dc, dc, -dc, temp=cfg.B5_SOFTMAX_TEMP)

    return _make_pred_map(score_fn)


# ---------------------------------------------------------------------------
# B6: Module-membership oracle
# ---------------------------------------------------------------------------

def run_b6_module_oracle() -> tuple[dict, dict]:
    """
    B6: Predict from module membership (i // 25 == j // 25).
    This is an oracle baseline: uses knowledge of network design.
    Forbidden for the framework to replicate.
    """
    def score_fn(i, j):
        same_module = (i // cfg.MODULE_SIZE == j // cfg.MODULE_SIZE)
        if same_module:
            return dict(cfg.B6_WITHIN_MODULE_PROBS)
        else:
            return dict(cfg.B6_BETWEEN_MODULE_PROBS)

    return _make_pred_map(score_fn)


# ---------------------------------------------------------------------------
# All-baselines runner
# ---------------------------------------------------------------------------

def run_all_baselines(
    runs: list[dict],
    verbose: bool = True,
) -> dict[str, tuple[dict, dict]]:
    """
    Run all 6 baselines. Returns {baseline_name: (pred_map, output_arrays)}.

    Permitted baselines: B1-B6 only (enforced by VALID_BASELINES).
    """
    results = {}

    baseline_fns = {
        'B1': lambda: run_b1_uniform(),
        'B2': lambda: run_b2_marginal(),
        'B3': lambda: run_b3_correlation(runs),
        'B4': lambda: run_b4_glasso(runs),
        'B5': lambda: run_b5_state_delta_corr(runs),
        'B6': lambda: run_b6_module_oracle(),
    }

    for name, fn in baseline_fns.items():
        assert name in VALID_BASELINES, f'Non-registered baseline {name}!'
        if verbose:
            print(f'  Running {name}...', flush=True)
        try:
            results[name] = fn()
        except Exception as e:
            print(f'  WARNING: {name} failed: {e}')
            results[name] = None

    return results


def register_baseline_lock() -> frozenset:
    """Return the frozen set of valid baselines. Calling code must verify membership."""
    return VALID_BASELINES
