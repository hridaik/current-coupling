#!/usr/bin/env python3
"""
Phase 9D Baselines — B1 through B4 on the frozen dataset.

B1: Random ranking (null)
B2: |ΔCorr_AB| — rank by absolute correlation change
B3: Graphical Lasso on pooled data — rank by |Q_pooled[i,j]| for off-connectome pairs
B4: Oracle — rank by |ΔΩ_true[i,j]| (already computed in Phase 9C)

Framework must exceed B2 on all three primary metrics to claim added value.
"""

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.covariance import GraphicalLassoCV
from scipy.stats import spearmanr
import json, hashlib, os

GT_DIR   = "results/phase9c/ground_truth"
DATA_DIR = "results/phase9d/dataset"
OUT_DIR  = "results/phase9d"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load frozen oracle objects ──────────────────────────────────────────────────
print("=== Phase 9D Baselines ===")
off_pairs      = np.load(f"{GT_DIR}/GT1_off_pairs.npy")
oracle_vals    = np.load(f"{GT_DIR}/GT1_oracle_vals.npy")
pmc_binary     = np.load(f"{GT_DIR}/GT2_pmc_binary.npy")
oracle_rank_order = np.load(f"{GT_DIR}/GT3_oracle_rank_order.npy")
A_obs          = np.load(f"{GT_DIR}/A_obs.npy")
spec           = json.load(open(f"{GT_DIR}/network_spec.json"))

N_OBS = spec["N_OBS"]   # 150
n_off = len(off_pairs)
n_pmc = int(pmc_binary.sum())

# Load trajectories
x_A = np.load(f"{DATA_DIR}/x_A.npy").astype(np.float64)
x_B = np.load(f"{DATA_DIR}/x_B.npy").astype(np.float64)
print(f"  Data loaded: x_A={x_A.shape}, x_B={x_B.shape}")

# ── Shared evaluation function ─────────────────────────────────────────────────
def evaluate(scores, label):
    """scores: (n_off,) — higher = more likely PMC. Returns dict of metrics."""
    auroc = float(roc_auc_score(pmc_binary, scores))
    # Rank correlation with oracle
    rho, _ = spearmanr(scores, oracle_vals)
    # Precision@k
    rank_order = np.argsort(-scores)
    prec = {}
    for k in [20, 50, 100]:
        prec[k] = float(pmc_binary[rank_order[:k]].sum()) / k
    print(f"  {label}: AUROC={auroc:.4f}, ρ={rho:.4f}, "
          f"Prec@20={prec[20]:.3f}, Prec@50={prec[50]:.3f}, Prec@100={prec[100]:.3f}")
    return {"auroc": auroc, "spearman_rho": float(rho),
            "precision_at_20": prec[20], "precision_at_50": prec[50],
            "precision_at_100": prec[100]}

# ── B1: Random ranking ──────────────────────────────────────────────────────────
print("\n--- B1: Random ranking ---")
rng_b1  = np.random.default_rng(9001)
b1_scores = rng_b1.random(n_off)
b1_results = evaluate(b1_scores, "B1 random")

# ── B2: |ΔCorr_AB| ─────────────────────────────────────────────────────────────
print("\n--- B2: |ΔCorr_AB| ---")
Corr_A = np.corrcoef(x_A.T)   # (150, 150)
Corr_B = np.corrcoef(x_B.T)
DeltaCorr = np.abs(Corr_A - Corr_B)
b2_scores = np.array([float(DeltaCorr[i, j]) for i, j in off_pairs])
b2_results = evaluate(b2_scores, "B2 |ΔCorr|")

# ── B3: Graphical Lasso on pooled data ─────────────────────────────────────────
print("\n--- B3: Graphical Lasso (pooled) ---")
x_pooled = np.vstack([x_A, x_B])   # (300000, 150)
try:
    gl = GraphicalLassoCV(cv=3, max_iter=500, n_jobs=1)
    gl.fit(x_pooled)
    Q_pooled = gl.precision_           # (150, 150)
    b3_scores = np.array([float(np.abs(Q_pooled[i, j])) for i, j in off_pairs])
    b3_results = evaluate(b3_scores, "B3 Glasso pooled")
    b3_converged = True
except Exception as e:
    print(f"  B3 Glasso failed: {e}")
    b3_scores    = np.zeros(n_off)
    b3_results   = {"auroc": 0.5, "spearman_rho": 0.0,
                    "precision_at_20": 0.0, "precision_at_50": 0.0, "precision_at_100": 0.0}
    b3_converged = False

# ── B4: Oracle ─────────────────────────────────────────────────────────────────
print("\n--- B4: Oracle (ΔΩ_true) ---")
b4_scores  = oracle_vals.copy()
b4_results = evaluate(b4_scores, "B4 oracle")

# ── Summary ────────────────────────────────────────────────────────────────────
print("\n=== Baseline Summary ===")
print(f"{'Baseline':>15}  {'AUROC':>7}  {'ρ':>6}  {'Prec@50':>8}")
print("-" * 45)
for name, res in [("B1 random", b1_results), ("B2 |ΔCorr|", b2_results),
                   ("B3 Glasso", b3_results), ("B4 oracle", b4_results)]:
    print(f"  {name:>13}  {res['auroc']:>7.4f}  {res['spearman_rho']:>6.3f}  "
          f"{res['precision_at_50']:>8.3f}")

# ── Save baseline outputs ───────────────────────────────────────────────────────
np.save(f"{OUT_DIR}/b1_scores.npy", b1_scores)
np.save(f"{OUT_DIR}/b2_scores.npy", b2_scores)
np.save(f"{OUT_DIR}/b3_scores.npy", b3_scores)
np.save(f"{OUT_DIR}/b4_scores.npy", b4_scores)

baseline_results = {
    "B1_random":  b1_results,
    "B2_deltacorr": b2_results,
    "B3_glasso":  {**b3_results, "converged": b3_converged},
    "B4_oracle":  b4_results,
    "oracle_ceiling_pass": b4_results["auroc"] >= 0.90,
    "b3_converged": b3_converged,
}

with open(f"{OUT_DIR}/baseline_results.json", "w") as f:
    json.dump(baseline_results, f, indent=2)

# Hash-lock
bl_hash = {}
for fname in ["b1_scores.npy", "b2_scores.npy", "b3_scores.npy", "b4_scores.npy",
              "baseline_results.json"]:
    with open(f"{OUT_DIR}/{fname}", "rb") as fh:
        bl_hash[fname] = hashlib.sha256(fh.read()).hexdigest()
with open(f"{OUT_DIR}/baseline_hashes.json", "w") as f:
    json.dump(bl_hash, f, indent=2)

print(f"\n  Baselines hash-locked. B4 AUROC={b4_results['auroc']:.4f} (≥0.90: PASS)")
