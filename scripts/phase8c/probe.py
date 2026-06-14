"""
Phase 8C probe machinery.

Generates probe datasets with varied parameters and scores them using the
frozen framework (scripts/phase8b_framework.py estimation logic).

Labels are already revealed (Phase 8B complete). This is post-hoc analysis.
No harness overhead — direct metric computation against frozen labels.
"""

import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.dynamics import softplus, apply_calcium_filter, observe, step_x
from scripts.phase7b.graph import compute_B

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_OBS        = cfg.N_OBS          # 100
N_TOTAL      = cfg.N_TOTAL        # 140
T            = cfg.T              # 50_000
T_WARMUP     = cfg.T_WARMUP       # 2_000
T_EFF        = cfg.T_EFF          # 48_000
DT           = cfg.DT             # 0.10
TEMPERATURE  = 5.0
KAPPA_FW     = 0.3                # framework kappa (weight of directed current)
RIDGE        = 1e-3

# Framework classes (same order as phase8 harness)
CLASSES = ['S', 'C', 'M', 'N']
LR_CLASSES = {'C', 'M'}


# ---------------------------------------------------------------------------
# Load frozen artifacts
# ---------------------------------------------------------------------------

def load_frozen_graph():
    """Return (A, D_sqrt) from ground_truth/."""
    root = cfg.PROJECT_ROOT
    A      = np.load(os.path.join(root, 'ground_truth', 'A_sparse.npy'))
    D_sqrt = np.load(os.path.join(root, 'ground_truth', '_stage2_D_sqrt.npy'))
    return A, D_sqrt


def load_frozen_labels():
    """Return {(i,j): class_str} from ground_truth/labels.json."""
    root = cfg.PROJECT_ROOT
    with open(os.path.join(root, 'ground_truth', 'labels.json')) as f:
        data = json.load(f)
    raw = data['labels'] if isinstance(data, dict) else data
    return {(d['i'], d['j']): d['label'] for d in raw}


def load_canonical_run(condition: str, run_index: int) -> dict:
    """
    Load a pre-generated canonical run from results/phase7c/canonical/data/.
    Returns {'y': (T_EFF, N_OBS), 'z_oracle': (T_EFF,)}.
    """
    root  = cfg.PROJECT_ROOT
    path  = os.path.join(root, 'results', 'phase7c', 'canonical', 'data',
                         f'{condition}_run{run_index}.npz')
    data  = np.load(path)
    return {
        'y':        data['y'].astype(np.float64),
        'z_oracle': data['z_oracle'].astype(np.float64),
        'run_index': run_index,
    }


# ---------------------------------------------------------------------------
# Probe simulation (varied parameters)
# ---------------------------------------------------------------------------

def _step_z_custom(z: float, rng, theta: float, sigma: float, dt: float) -> float:
    """Euler-Maruyama OU step with custom theta/sigma."""
    dW = rng.standard_normal() * np.sqrt(dt)
    return z - theta * z * dt + sigma * dW


def simulate_probe_run(
    run_index: int,
    A: np.ndarray,
    D_sqrt: np.ndarray,
    gamma_h2: float = cfg.GAMMA_H2,
    theta_z: float = cfg.THETA_Z,
    sigma_z: float = cfg.SIGMA_Z,
    h2_active_set: frozenset | None = None,
) -> dict:
    """
    Simulate one probe run with varied parameters.

    Parameters
    ----------
    run_index : int
        Run index (0–4). Uses z_seed=49+run_index, x_seed=60+run_index.
    A : (N_TOTAL, N_TOTAL) float64
        Frozen coupling matrix.
    D_sqrt : (N_TOTAL,) float64
        Frozen noise amplitude per neuron.
    gamma_h2 : float
        H2 z-drive gain (default: cfg.GAMMA_H2=3.0).
    theta_z : float
        OU mean-reversion rate (default: cfg.THETA_Z=0.10).
    sigma_z : float
        OU noise amplitude (default: cfg.SIGMA_Z=1.00).
    h2_active_set : frozenset or None
        Which H2 neurons receive nonzero z-drive. If None, uses cfg.SA (all 8).

    Returns
    -------
    dict with 'y' (T_EFF, N_OBS), 'z_oracle' (T_EFF,), 'run_index'.
    """
    if h2_active_set is None:
        h2_active_set = cfg.SA

    rng_z = np.random.default_rng(49 + run_index)
    rng_x = np.random.default_rng(60 + run_index)

    def B_fn(z: float) -> np.ndarray:
        B = np.zeros(N_TOTAL, dtype=np.float64)
        for h in h2_active_set:
            B[h] = gamma_h2 * z
        return B

    x  = np.zeros(N_TOTAL, dtype=np.float64)
    z  = 0.0
    ca = np.zeros(N_OBS, dtype=np.float64)

    y_store = np.empty((T_EFF, N_OBS), dtype=np.float64)
    z_store = np.empty(T_EFF, dtype=np.float64)

    for t in range(T):
        z = _step_z_custom(z, rng_z, theta=theta_z, sigma=sigma_z, dt=DT)
        x = step_x(x, z, A, D_sqrt, B_fn, rng_x, dt=DT)
        if t >= T_WARMUP:
            t_eff = t - T_WARMUP
            y, ca = observe(x[:N_OBS], ca, rng_x)
            y_store[t_eff] = y
            z_store[t_eff] = z

    return {'y': y_store, 'z_oracle': z_store, 'run_index': run_index}


# ---------------------------------------------------------------------------
# Framework estimation (identical logic to scripts/phase8b_framework.py)
# ---------------------------------------------------------------------------

def _run_stats(run: dict) -> dict:
    """Compute covariance and lag-1 statistics for one run."""
    y = run['y']
    z = run['z_oracle']
    T_local = y.shape[0]

    z_c  = z - z.mean()
    beta = (z_c @ y) / (z_c @ z_c)
    y_resid = y - np.outer(z, beta)

    y_c  = y - y.mean(axis=0)
    yr_c = y_resid - y_resid.mean(axis=0)

    return {
        'Cov_raw':   (y_c.T  @ y_c)  / T_local,
        'Cov_cond':  (yr_c.T @ yr_c) / T_local,
        'Lag1_cond': (yr_c[1:].T @ yr_c[:-1]) / (T_local - 1),
    }


def estimate_framework_quantities(runs: list[dict]) -> dict:
    """Pool statistics across runs; compute PCor_cond, Delta_PCor, Current_norm."""
    acc = {'Cov_raw': 0.0, 'Cov_cond': 0.0, 'Lag1_cond': 0.0}
    for run in runs:
        s = _run_stats(run)
        for k in acc:
            acc[k] = acc[k] + s[k]
    n = len(runs)
    Cov_raw   = acc['Cov_raw']   / n
    Cov_cond  = acc['Cov_cond']  / n
    Lag1_cond = acc['Lag1_cond'] / n

    I = np.eye(N_OBS)
    Omega_raw  = np.linalg.inv(Cov_raw  + RIDGE * I)
    Omega_cond = np.linalg.inv(Cov_cond + RIDGE * I)

    d_raw  = np.sqrt(np.diag(Omega_raw))
    d_cond = np.sqrt(np.diag(Omega_cond))
    PCor_raw  = -Omega_raw  / np.outer(d_raw,  d_raw)
    PCor_cond = -Omega_cond / np.outer(d_cond, d_cond)

    Delta_PCor   = np.abs(PCor_raw - PCor_cond)
    Current_cond = Lag1_cond - Lag1_cond.T
    std_cond     = np.sqrt(np.diag(Cov_cond))
    Current_norm = Current_cond / (np.outer(std_cond, std_cond) + 1e-12)

    return {
        'PCor_cond':    PCor_cond,
        'Delta_PCor':   Delta_PCor,
        'Current_norm': Current_norm,
    }


def _score_pair(i: int, j: int, fq: dict) -> np.ndarray:
    """Return softmax class_prob [S, C, M, N] for directed pair (i->j)."""
    omega   = float(np.abs(fq['PCor_cond'][i, j]))
    delta   = float(fq['Delta_PCor'][i, j])
    current = float(fq['Current_norm'][j, i])

    s_score = omega + KAPPA_FW * max(0.0, current)
    c_score = delta
    m_score = 2.0 * s_score * c_score / (s_score + c_score + 1e-12)
    n_score = 0.0

    logits = np.array([s_score, c_score, m_score, n_score]) * TEMPERATURE
    logits -= logits.max()
    e = np.exp(logits)
    return e / e.sum()


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def _build_score_arrays(fq: dict, labels: dict):
    """
    Build parallel arrays for AUROC computation.

    Returns
    -------
    class_prob : (9900, 4) float64  — ordered S, C, M, N
    true_labels : list[str]          — same order as pairs
    pairs : list[(i,j)]
    """
    pairs      = [(i, j) for i in range(N_OBS) for j in range(N_OBS) if i != j]
    n          = len(pairs)
    class_prob = np.empty((n, 4), dtype=np.float64)
    true_lbl   = []

    for k, (i, j) in enumerate(pairs):
        class_prob[k] = _score_pair(i, j, fq)
        true_lbl.append(labels.get((i, j), 'N'))

    return class_prob, true_lbl, pairs


def compute_metrics(fq: dict, labels: dict) -> dict:
    """
    Compute MacroAUROC, per-class AUROCs, LR-AUROC against frozen labels.
    """
    class_prob, true_lbl, _ = _build_score_arrays(fq, labels)
    true_arr = np.array(true_lbl)

    per_class = {}
    for c_i, cls in enumerate(CLASSES):
        y_true  = (true_arr == cls).astype(int)
        y_score = class_prob[:, c_i]
        if y_true.sum() == 0 or y_true.sum() == len(y_true):
            per_class[cls] = float('nan')
        else:
            per_class[cls] = float(roc_auc_score(y_true, y_score))

    macro_auroc = float(np.nanmean([per_class[c] for c in CLASSES]))

    # C-AUROC
    c_auroc = per_class['C']

    # LR-AUROC (C+M combined)
    y_lr_true  = np.array([1 if l in LR_CLASSES else 0 for l in true_lbl], dtype=int)
    lr_score   = class_prob[:, CLASSES.index('C')] + class_prob[:, CLASSES.index('M')]
    lr_auroc   = float(roc_auc_score(y_lr_true, lr_score)) if y_lr_true.sum() > 0 else float('nan')

    return {
        'macro_auroc': macro_auroc,
        'c_auroc':     c_auroc,
        'lr_auroc':    lr_auroc,
        's_auroc':     per_class['S'],
        'm_auroc':     per_class['M'],
        'n_auroc':     per_class['N'],
    }


# ---------------------------------------------------------------------------
# High-level probe runner
# ---------------------------------------------------------------------------

def run_probe(
    runs: list[dict],
    labels: dict,
    label: str,
) -> dict:
    """
    Given pre-loaded runs and labels, estimate framework quantities and compute metrics.

    Parameters
    ----------
    runs : list of run dicts (each has 'y', 'z_oracle', 'run_index')
    labels : {(i,j): class_str}
    label : short descriptive label for this probe condition

    Returns
    -------
    dict with label, metrics.
    """
    fq      = estimate_framework_quantities(runs)
    metrics = compute_metrics(fq, labels)
    return {'label': label, **metrics}
