"""
Current-velocity framework — Phase 8B first blinded evaluation.

Inputs (oracle_z condition):
    y(t): (T_eff, N_OBS) calcium-filtered observations
    z_oracle(t): (T_eff,) latent H2 drive variable

Method:
    1. For each run, regress z_oracle out of y to get y_resid.
    2. Compute unconditional precision matrix Omega_raw = inv(Cov(y)).
    3. Compute z-conditioned precision matrix Omega_cond = inv(Cov(y_resid)).
    4. Delta_Omega = |Omega_raw - Omega_cond|  (z-mediated partial correlation change).
    5. Compute lag-1 cross-correlation matrices for directed current estimation.
       Current_cond[j,i] = E[y_j_resid(t+1)*y_i_resid(t)] - E[y_i_resid(t+1)*y_j_resid(t)]
       Positive Current_cond[j,i] means i causally leads j (z-conditioned).
    6. For directed pair (i->j):
         S-score = |Omega_cond[i,j]| + kappa * max(0, Current_cond[j,i])
         C-score = Delta_Omega[i,j]
         M-score = S-score * C-score (both present)
         N-score = 0 (baseline)
       Apply softmax with temperature T to get class_prob.

Scoring design notes:
    - Omega_cond captures paths that persist after z removal: structural (S/M) and
      structural-indirect (i->H2->j, which also persists after z regression on observed y).
    - Delta_Omega captures the z-mediated component: present for C/M pairs where
      H2-mediation adds z-correlated correlation on top of structural paths.
    - Current_cond[j,i] captures directed causal asymmetry under z-conditioning,
      strengthening the S signal for direct edges.
    - The directed current is SIGNED: positive = i leads j. Both S and C pairs
      have i->j directed influence (direct vs through H2), but direct edges
      produce stronger lag-1 asymmetry in the z-conditioned residuals.

No parameter tuning. No validation against labels. No iteration.
This script runs once. Its output is frozen and scored blind.
"""

import json
import hashlib
import os
import sys

import numpy as np
from scipy.special import softmax

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Framework hyperparameters — frozen before output generation
# ---------------------------------------------------------------------------

TEMPERATURE      = 5.0    # softmax temperature
KAPPA            = 0.3    # weight of directed current in S-score
RIDGE            = 1e-3   # Tikhonov regularization for precision matrix inversion
N_OBS            = 100    # number of observed neurons
CONDITION        = 'oracle_z'
OUTPUT_PATH      = 'framework_output.json'


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_runs(dataset_dir: str) -> list[dict]:
    """Load all 5 oracle_z runs from the frozen dataset."""
    runs = []
    for r in range(5):
        path = os.path.join(dataset_dir, f'{CONDITION}_run{r}.npz')
        data = np.load(path)
        runs.append({
            'run_index': r,
            'y':        data['y'].astype(np.float64),          # (48000, 100)
            'z_oracle': data['z_oracle'].astype(np.float64),   # (48000,)
        })
        print(f'  Loaded run {r}: y={data["y"].shape}, z={data["z_oracle"].shape}')
    return runs


# ---------------------------------------------------------------------------
# Per-run statistics
# ---------------------------------------------------------------------------

def _compute_run_stats(run: dict) -> dict:
    """
    Compute lag-0 and lag-1 covariance statistics for one run.
    Returns both raw (y) and z-conditioned (y_resid) versions.
    """
    y = run['y']        # (T, 100)
    z = run['z_oracle'] # (T,)
    T = y.shape[0]

    # Regress z from y: y_resid = y - z * beta^T
    z_c   = z - z.mean()
    z_var = z_c @ z_c  # scalar
    beta  = (z_c @ y) / z_var   # (100,) regression coefficient per neuron
    y_resid = y - np.outer(z, beta)

    # Center
    y_c      = y - y.mean(axis=0)
    yr_c     = y_resid - y_resid.mean(axis=0)

    # Lag-0 (covariance, divided by T)
    Cov_raw  = (y_c.T  @ y_c)  / T          # (100, 100)
    Cov_cond = (yr_c.T @ yr_c) / T          # (100, 100)

    # Lag-1: C1[j,i] = (1/T-1) * sum_{t} y_j(t+1) * y_i(t)
    Lag1_raw  = (y_c[1:].T  @ y_c[:-1])  / (T - 1)   # (100, 100)
    Lag1_cond = (yr_c[1:].T @ yr_c[:-1]) / (T - 1)   # (100, 100)

    return {
        'Cov_raw':   Cov_raw,
        'Cov_cond':  Cov_cond,
        'Lag1_raw':  Lag1_raw,
        'Lag1_cond': Lag1_cond,
    }


# ---------------------------------------------------------------------------
# Framework estimation
# ---------------------------------------------------------------------------

def estimate_framework_quantities(runs: list[dict]) -> dict:
    """
    Pool statistics across runs and compute Omega, Delta_Omega, Current.
    """
    # Accumulate
    Cov_raw   = np.zeros((N_OBS, N_OBS))
    Cov_cond  = np.zeros((N_OBS, N_OBS))
    Lag1_raw  = np.zeros((N_OBS, N_OBS))
    Lag1_cond = np.zeros((N_OBS, N_OBS))

    for r, run in enumerate(runs):
        print(f'  Computing statistics for run {r}...')
        stats = _compute_run_stats(run)
        Cov_raw   += stats['Cov_raw']
        Cov_cond  += stats['Cov_cond']
        Lag1_raw  += stats['Lag1_raw']
        Lag1_cond += stats['Lag1_cond']

    n = len(runs)
    Cov_raw   /= n
    Cov_cond  /= n
    Lag1_raw  /= n
    Lag1_cond /= n

    # Precision matrices (Tikhonov-regularized)
    I = np.eye(N_OBS)
    Omega_raw  = np.linalg.inv(Cov_raw  + RIDGE * I)  # (100, 100)
    Omega_cond = np.linalg.inv(Cov_cond + RIDGE * I)  # (100, 100)

    # Normalize precision by diagonal (partial correlation form)
    # pcor[i,j] = -Omega[i,j] / sqrt(Omega[i,i] * Omega[j,j])
    d_raw  = np.sqrt(np.diag(Omega_raw))
    d_cond = np.sqrt(np.diag(Omega_cond))
    PCor_raw  = -Omega_raw  / np.outer(d_raw,  d_raw)   # symmetric, off-diag = pcor
    PCor_cond = -Omega_cond / np.outer(d_cond, d_cond)

    # Delta partial correlation (z-mediated component)
    Delta_PCor = np.abs(PCor_raw - PCor_cond)  # symmetric

    # Directed current: antisymmetric lag-1 asymmetry (z-conditioned)
    # Current_cond[j,i] > 0 means i causally leads j
    Current_cond = Lag1_cond - Lag1_cond.T   # antisymmetric (100, 100)
    # Normalize current by joint standard deviation
    std_cond = np.sqrt(np.diag(Cov_cond))
    Current_norm = Current_cond / (np.outer(std_cond, std_cond) + 1e-12)

    print(f'  Omega_raw: diag min={np.diag(Omega_raw).min():.4f}, max={np.diag(Omega_raw).max():.4f}')
    print(f'  PCor_cond: abs off-diag mean={np.abs(PCor_cond[~np.eye(N_OBS,dtype=bool)]).mean():.6f}')
    print(f'  Delta_PCor: mean={Delta_PCor[~np.eye(N_OBS,dtype=bool)].mean():.6f}')
    print(f'  Current_norm: abs mean={np.abs(Current_norm[~np.eye(N_OBS,dtype=bool)]).mean():.6f}')

    return {
        'PCor_cond':    PCor_cond,
        'Delta_PCor':   Delta_PCor,
        'Current_norm': Current_norm,
    }


# ---------------------------------------------------------------------------
# Score → class probability mapping
# ---------------------------------------------------------------------------

def score_pair(i: int, j: int, fq: dict) -> dict[str, float]:
    """
    For directed pair (i->j), compute class_prob using framework quantities.

    S-score: magnitude of z-conditioned partial correlation + directed current
    C-score: magnitude of z-mediated partial correlation change
    M-score: geometric mean of S and C scores (both must be nonzero)
    N-score: 0 (baseline)
    """
    omega   = float(np.abs(fq['PCor_cond'][i, j]))     # symmetric
    delta   = float(fq['Delta_PCor'][i, j])              # symmetric
    current = float(fq['Current_norm'][j, i])            # directed: positive = i leads j

    s_score = omega + KAPPA * max(0.0, current)
    c_score = delta
    m_score = 2.0 * (s_score * c_score) / (s_score + c_score + 1e-12)  # harmonic mean
    n_score = 0.0

    logits = np.array([s_score, c_score, m_score, n_score]) * TEMPERATURE
    probs  = softmax(logits)

    return {
        'S': float(probs[0]),
        'C': float(probs[1]),
        'M': float(probs[2]),
        'N': float(probs[3]),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    print('=' * 60)
    print('Phase 8B: Current-velocity framework — oracle_z condition')
    print('=' * 60)
    print(f'Temperature={TEMPERATURE}, Kappa={KAPPA}, Ridge={RIDGE}')
    print()

    # Locate dataset
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir  = os.path.join(project_root, 'results', 'phase7c', 'canonical', 'data')

    # Load data
    print('Loading oracle_z runs...')
    runs = load_runs(dataset_dir)
    print()

    # Estimate framework quantities
    print('Estimating precision, delta, and current matrices...')
    fq = estimate_framework_quantities(runs)
    print()

    # Score all 9900 directed pairs
    print('Scoring 9900 directed pairs...')
    predictions = []
    for i in range(N_OBS):
        for j in range(N_OBS):
            if i == j:
                continue
            cp   = score_pair(i, j, fq)
            pred = max(cp, key=cp.get)
            predictions.append({'i': i, 'j': j, 'class_prob': cp, 'class_pred': pred})

    # Count predictions
    from collections import Counter
    pred_counts = Counter(p['class_pred'] for p in predictions)
    print(f'Predicted class distribution: {dict(pred_counts)}')
    print()

    # Write output
    output = {
        'metadata': {
            'framework':   'current_velocity_v1',
            'condition':   CONDITION,
            'temperature': TEMPERATURE,
            'kappa':       KAPPA,
            'ridge':       RIDGE,
            'n_runs':      len(runs),
            'n_pairs':     len(predictions),
            'method':      (
                'Omega_cond: partial correlation after z regression; '
                'Delta_PCor: z-mediated partial correlation change; '
                'Current_norm: normalized lag-1 asymmetry (z-conditioned)'
            ),
        },
        'predictions': predictions,
    }

    out_path = os.path.join(project_root, OUTPUT_PATH)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=True)

    # Hash the output
    with open(out_path, 'rb') as f:
        content = f.read()
    h = hashlib.sha256(content).hexdigest()

    print(f'Output written to: {out_path}')
    print(f'SHA-256: {h}')
    print(f'Size: {len(content):,} bytes')

    return out_path, h


if __name__ == '__main__':
    main()
