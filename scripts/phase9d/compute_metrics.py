#!/usr/bin/env python3
"""
Phase 9D Stage 5 — Metric Computation

Computes all pre-registered metrics on the frozen framework output.
No new metrics, no threshold changes, no relabeling.

Primary metrics:
  - Precision@50, Precision@20, Precision@100
  - ρ_Spearman (vs oracle_vals)
  - PMC_AUROC

Secondary metrics:
  - NMI_module (SpectralClustering k=3 on |ΔΩ_hat| affinity)
  - ρ_state_intervention (framework on x_A vs x_A_lesion)
  - ρ_structural_intervention (framework on x_A vs x_B vs x_A_lesion)
  - S_AUROC diagnostic (structural pair detection)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import json, hashlib
from sklearn.metrics import roc_auc_score, normalized_mutual_info_score
from sklearn.cluster import SpectralClustering
from scipy.stats import spearmanr

GT_DIR   = "results/phase9c/ground_truth"
DATA_DIR = "results/phase9d/dataset"
OUT_DIR  = "results/phase9d"

print("=== Phase 9D Stage 5: Metric Computation ===")

# ── Load ground truth objects ──────────────────────────────────────────────────
off_pairs      = np.load(f"{GT_DIR}/GT1_off_pairs.npy")          # (10433, 2)
oracle_vals    = np.load(f"{GT_DIR}/GT1_oracle_vals.npy")         # (10433,)
pmc_binary     = np.load(f"{GT_DIR}/GT2_pmc_binary.npy")          # (10433,)
gt5a_vals      = np.load(f"{GT_DIR}/GT5a_state_lesion_vals.npy")  # (10433,)
gt5b_vals      = np.load(f"{GT_DIR}/GT5b_struct_lesion_vals.npy") # (10433,)
communities    = json.load(open(f"{GT_DIR}/GT4_communities.json"))
spec           = json.load(open(f"{GT_DIR}/network_spec.json"))
A_obs          = np.load(f"{DATA_DIR}/A_obs.npy")

N_OBS   = spec["N_OBS"]
n_off   = len(off_pairs)
n_pmc   = int(pmc_binary.sum())
PMC_SRC = set(spec["PMC_SRC"])
PMC_TGT = set(spec["PMC_TGT"])
print(f"  Ground truth: {n_off} off-connectome pairs, {n_pmc} PMC")

# Verify framework output hash
fw_path = f"{OUT_DIR}/framework_DeltaOmega.npy"
with open(fw_path, "rb") as fh:
    fw_hash = hashlib.sha256(fh.read()).hexdigest()
fw_log = json.load(open(f"{OUT_DIR}/framework_log.json"))
assert fw_hash == fw_log["framework_output_hash"], "Framework output hash mismatch"
print(f"  Framework hash verified: {fw_hash[:16]}...")

DeltaOmega_est = np.load(fw_path)   # (150, 150)

# ── Extract per-pair scores for off-connectome pairs ──────────────────────────
# Score = |ΔΩ_estimated[i,j]|, symmetrized
DO_sym = (DeltaOmega_est + DeltaOmega_est.T) / 2
fw_scores = np.array([float(np.abs(DO_sym[i, j])) for i, j in off_pairs])
print(f"  Score range: [{fw_scores.min():.5f}, {fw_scores.max():.5f}]")

# ── Primary metrics ────────────────────────────────────────────────────────────
print("\n--- Primary Metrics ---")

# PMC_AUROC
pmc_auroc = float(roc_auc_score(pmc_binary, fw_scores))
print(f"  PMC_AUROC:     {pmc_auroc:.4f}")

# Spearman ρ vs oracle
rho_oracle, p_rho = spearmanr(fw_scores, oracle_vals)
rho_oracle = float(rho_oracle)
print(f"  ρ_Spearman:    {rho_oracle:.4f}  (p={p_rho:.3e})")

# Precision@k
rank_order = np.argsort(-fw_scores)
prec = {}
for k in [20, 50, 100]:
    hits = int(pmc_binary[rank_order[:k]].sum())
    prec[k] = float(hits) / k
    print(f"  Precision@{k:3d}:  {prec[k]:.3f}  ({hits}/{k} PMC)")

# ── Secondary metric: NMI_module ──────────────────────────────────────────────
print("\n--- Secondary: NMI_module ---")

# Build dense affinity matrix from |ΔΩ_est| for off-connectome pairs
W = np.zeros((N_OBS, N_OBS))
for idx, (i, j) in enumerate(off_pairs):
    W[i, j] = fw_scores[idx]
    W[j, i] = fw_scores[idx]

# SpectralClustering with pre-registered params (A7)
sc = SpectralClustering(
    n_clusters=3,
    affinity='precomputed',
    random_state=42,
    n_init=20,
    assign_labels='kmeans'
)
labels_pred = sc.fit_predict(W)

# GT4 community labels: C_src, C_tgt, background
labels_true = np.zeros(N_OBS, dtype=int)  # background = 0
for node in communities["C_src"]:
    labels_true[node] = 1
for node in communities["C_tgt"]:
    labels_true[node] = 2

nmi = float(normalized_mutual_info_score(labels_true, labels_pred))
print(f"  NMI_module:    {nmi:.4f}")

# ── Secondary metric: Intervention ρ (state lesion) ──────────────────────────
print("\n--- Secondary: Intervention Recovery ---")

# State intervention: compare framework scores vs GT5a (state-lesion oracle)
rho_state, p_state = spearmanr(fw_scores, gt5a_vals)
rho_state = float(rho_state)
print(f"  ρ_state_intervention vs GT5a:  {rho_state:.4f}")

# Structural intervention: compute framework on x_A vs x_A_lesion
from evaluate_framework import evaluate_framework

x_A       = np.load(f"{DATA_DIR}/x_A.npy").astype(np.float64)
x_A_les   = np.load(f"{DATA_DIR}/x_A_lesion.npy").astype(np.float64)

DO_les_est = evaluate_framework(x_A, x_A_les, A_obs)  # framework on lesion pair
DO_les_sym = (DO_les_est + DO_les_est.T) / 2
fw_lesion_scores = np.array([float(np.abs(DO_les_sym[i, j])) for i, j in off_pairs])

rho_struct, p_struct = spearmanr(fw_lesion_scores, gt5b_vals)
rho_struct = float(rho_struct)
print(f"  ρ_structural_intervention vs GT5b:  {rho_struct:.4f}")

# ── Secondary metric: S_AUROC ─────────────────────────────────────────────────
print("\n--- Secondary: S_AUROC diagnostic ---")

# S label: A_obs[i,j] ≠ 0 OR A_obs[j,i] ≠ 0 (for observed-observed pairs)
s_labels = np.array([
    1 if (A_obs[i, j] != 0 or A_obs[j, i] != 0) else 0
    for i, j in off_pairs
])
n_struct = int(s_labels.sum())
print(f"  Structural pairs (S=1): {n_struct}")

if n_struct > 0 and n_struct < n_off:
    s_auroc = float(roc_auc_score(s_labels, fw_scores))
    print(f"  S_AUROC:               {s_auroc:.4f}")
else:
    s_auroc = float('nan')
    print(f"  S_AUROC:               N/A (n_struct={n_struct})")

# ── Collect and save results ──────────────────────────────────────────────────
print("\n--- Summary ---")

results = {
    "framework_output_hash": fw_hash,
    "primary_metrics": {
        "pmc_auroc": pmc_auroc,
        "spearman_rho": rho_oracle,
        "spearman_pval": float(p_rho),
        "precision_at_20": prec[20],
        "precision_at_50": prec[50],
        "precision_at_100": prec[100],
    },
    "secondary_metrics": {
        "nmi_module": nmi,
        "rho_state_intervention": rho_state,
        "rho_structural_intervention": rho_struct,
        "s_auroc_diagnostic": s_auroc if not np.isnan(s_auroc) else None,
        "n_structural_pairs": n_struct,
    },
    "top20_pairs": [
        {
            "rank": r + 1,
            "i": int(off_pairs[rank_order[r], 0]),
            "j": int(off_pairs[rank_order[r], 1]),
            "score": float(fw_scores[rank_order[r]]),
            "is_pmc": bool(pmc_binary[rank_order[r]]),
        }
        for r in range(20)
    ],
    "baselines_for_comparison": json.load(open(f"{OUT_DIR}/baseline_results.json")),
}

print(f"  PMC_AUROC:   {pmc_auroc:.4f}  (B4 oracle: 0.9983, B1 random: 0.5105)")
print(f"  ρ_Spearman:  {rho_oracle:.4f}  (B4 oracle: 1.000)")
print(f"  Prec@50:     {prec[50]:.3f}   (B4 oracle: 1.000)")
print(f"  NMI_module:  {nmi:.4f}")

with open(f"{OUT_DIR}/evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Hash-lock evaluation results
with open(f"{OUT_DIR}/evaluation_results.json", "rb") as fh:
    eval_hash = hashlib.sha256(fh.read()).hexdigest()
with open(f"{OUT_DIR}/evaluation_hash.txt", "w") as f:
    f.write(eval_hash + "\n")

np.save(f"{OUT_DIR}/fw_scores.npy", fw_scores)
np.save(f"{OUT_DIR}/fw_lesion_scores.npy", fw_lesion_scores)

print(f"\n  Evaluation results saved and hash-locked.")
print(f"  evaluation_hash: {eval_hash[:16]}...")
print("\n=== STAGE 5 COMPLETE ===")
