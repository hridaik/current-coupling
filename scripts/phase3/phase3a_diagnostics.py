"""Phase 3A Diagnostic Package (D1–D5).

Authorization: Phase 3A.5-D, 2026-06-03.

Purpose: Distinguish architecture limitation vs. weak signal vs. null BEFORE
consuming the one-shot held-out evaluation.

D1 — Held-out preview (no success/failure decision; report predicted ranks only)
D2 — Randomized-P null repair (proper 2D fit for each P_rand; N=100)
D3 — PDF contribution map (which pairs does M1 predict; source-neuron breakdown)
D4 — α landscape (objective vs α; is optimum sharp, plateau, or boundary-seeking?)
D5 — Sparsity mismatch audit (dense prediction vs. sparse observation)

STOP after diagnostics. No held-out evaluation. No Phase 3B.
"""
from __future__ import annotations
import csv, json, sys, time, warnings
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
from scipy import linalg, stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

OUT_P3     = ROOT / "results/phase3"
OUT_DIAG   = OUT_P3 / "diagnostics"
OUT_DIAG.mkdir(parents=True, exist_ok=True)

# ── Load Phase 3A artifacts ───────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N       = len(NEURONS)
n2i     = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)

with open(OUT_P3 / "phase3a_fit_parameters.json") as f:
    fit_params = json.load(f)
with open(OUT_P3 / "phase3a_stability_report.json") as f:
    stab_report = json.load(f)

alpha_r_M1   = float(fit_params["M1"]["alpha_roam"])
alpha_d_M1   = float(fit_params["M1"]["alpha_dwell"])
ALPHA_LO_FIT = float(fit_params["alpha_grid_range"][0])
ALPHA_HI_FIT = float(fit_params["alpha_grid_range"][1])
alpha_max_M1 = float(stab_report["M1_J_directed"]["alpha_max_P_norm"])
alpha_min_M1 = float(stab_report["M1_J_directed"]["alpha_min_P_norm"])

J_base_raw = np.load(OUT_P3 / "phase3a_J_directed.npy")
P_norm     = np.load(OUT_P3 / "phase3a_P_norm.npy")
P_directed = np.load(OUT_P3 / "phase3a_P_directed.npy")
P_rand     = np.load(OUT_P3 / "phase3a_P_rand.npy")       # (1000, 61, 61)
P_rand_norm= np.load(OUT_P3 / "phase3a_P_rand_norm.npy")  # (1000, 61, 61)

gamma_J  = float(stab_report["M1_J_directed"]["gamma"])
J_base   = J_base_raw - gamma_J * np.eye(N)

DQ_obs_cep = np.load(ROOT / "results/phase2/stage2/DQ_cepnem.npy")
ranked_c4  = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4      = ii_all[ranked_c4]
jj_c4      = jj_all[ranked_c4]
N_C4       = len(ranked_c4)

# Held-out pairs — authoritative (4 only)
HELD_OUT_PAIRS = frozenset([
    (n2i["ADEL"], n2i["URYVR"]),
    (n2i["ADEL"], n2i["URYDL"]),
    (n2i["ADEL"], n2i["RMEL"]),
    (n2i["ADEL"], n2i["URXL"]),
])
held_out_list = [
    ("ADEL–URYVR", n2i["ADEL"], n2i["URYVR"]),
    ("ADEL–URYDL", n2i["ADEL"], n2i["URYDL"]),
    ("ADEL–RMEL",  n2i["ADEL"], n2i["RMEL"]),
    ("ADEL–URXL",  n2i["ADEL"], n2i["URXL"]),
]

# Training mask (exclude held-out)
train_mask  = np.array(
    [(ii_c4[k], jj_c4[k]) not in HELD_OUT_PAIRS for k in range(N_C4)],
    dtype=bool,
)
train_ii    = ii_c4[train_mask]
train_jj    = jj_c4[train_mask]
DQ_obs_train = DQ_obs_cep[train_ii, train_jj]

# PDF Class 4 pairs
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
c4_set   = set(zip(map(int, ii_c4), map(int, jj_c4)))

def load_bentley_pdf_c4() -> set:
    pairs: set = set()
    with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 3: continue
            src, tgt = row[0].strip(), row[1].strip()
            if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
            if "pdf" not in row[2].strip().lower(): continue
            a, b = n2i[src], n2i[tgt]
            pairs.add((min(a, b), max(a, b)))
    return pairs & c4_set

bentley_pdf_c4 = load_bentley_pdf_c4()

# PDF source neurons (for D3)
PDF_SOURCES = {n2i["RID"], n2i["ADEL"], n2i["RMEL"], n2i["RMER"], n2i["AVDL"]}
PDF_TARGETS = set()
for (a, b) in bentley_pdf_c4:
    PDF_TARGETS.add(a); PDF_TARGETS.add(b)
PDF_TARGETS -= PDF_SOURCES

# ── Forward model ─────────────────────────────────────────────────────────────
def lyapunov_Q(J_eff: np.ndarray) -> np.ndarray | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Sigma = linalg.solve_continuous_lyapunov(J_eff, -np.eye(N))
        Sigma = (Sigma + Sigma.T) / 2
        ev    = np.linalg.eigvalsh(Sigma)
        if ev.min() < -1e-8:
            return None
        Sigma += max(0.0, -ev.min() + 1e-10) * np.eye(N)
        Q = np.linalg.inv(Sigma)
        return (Q + Q.T) / 2
    except Exception:
        return None

def predict_deltaQ(alpha_r: float, alpha_d: float,
                   J_b: np.ndarray, P_m: np.ndarray) -> np.ndarray | None:
    Q_r = lyapunov_Q(J_b + alpha_r * P_m)
    Q_d = lyapunov_Q(J_b + alpha_d * P_m)
    if Q_r is None or Q_d is None:
        return None
    return Q_r - Q_d

def spearman_obj(alpha_r: float, alpha_d: float,
                 J_b: np.ndarray, P_m: np.ndarray) -> float:
    DQ = predict_deltaQ(alpha_r, alpha_d, J_b, P_m)
    if DQ is None:
        return float("nan")
    rho, _ = stats.spearmanr(
        np.abs(DQ[train_ii, train_jj]),
        np.abs(DQ_obs_train),
    )
    return float(rho) if not np.isnan(rho) else 0.0

# Pre-compute M1 predicted ΔQ (used in D1, D3, D5)
DQ_M1 = predict_deltaQ(alpha_r_M1, alpha_d_M1, J_base, P_norm)
assert DQ_M1 is not None, "M1 Lyapunov failed"

# ═══════════════════════════════════════════════════════════════════════════════
# D1 — HELD-OUT PREVIEW
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("D1 — Held-out Preview")
print("=" * 70)

dq_pred_c4_abs = np.abs(DQ_M1[ii_c4, jj_c4])  # (1321,) |ΔQ_pred| for all Class 4 pairs

# Rank 1 = highest |ΔQ_pred|
rank_order = np.argsort(-dq_pred_c4_abs)
pair_rank  = np.empty(N_C4, dtype=int)
pair_rank[rank_order] = np.arange(1, N_C4 + 1)

d1_rows = []
for pair_name, pi, pj in held_out_list:
    key = (min(pi, pj), max(pi, pj))
    # Find this pair in the Class 4 list
    match = np.where((ii_c4 == min(pi,pj)) & (jj_c4 == max(pi,pj)))[0]
    if len(match) == 0:
        print(f"  WARNING: {pair_name} not found in Class 4 list")
        continue
    k         = int(match[0])
    pred_rank = int(pair_rank[k])
    pred_pct  = float(pred_rank / N_C4 * 100)
    pred_abs  = float(dq_pred_c4_abs[k])
    d1_rows.append({
        "pair":             pair_name,
        "predicted_rank":   pred_rank,
        "predicted_pctile": round(pred_pct, 2),
        "predicted_abs_dq": round(pred_abs, 6),
    })
    print(f"  {pair_name}: rank={pred_rank}/{N_C4}  ({pred_pct:.1f}th pctile)  |ΔQ_pred|={pred_abs:.5f}")

print()
print("NOTE: Observed ΔQ values NOT consulted. No success/failure judgment made.")

d1_text = f"""# D1 — Held-Out Preview
Date: 2026-06-03
Authorization: Phase 3A.5-D

## M1 Predicted Rankings for Held-Out ADEL Pairs

Using fitted M1 parameters: α_roam = {alpha_r_M1:.4f}, α_dwell = {alpha_d_M1:.4f} (P_norm units).
Rankings are among all {N_C4} Class 4 pairs by |ΔQ_pred|. Rank 1 = highest |ΔQ_pred|.

| Pair | Predicted rank | Predicted percentile | Predicted |ΔQ_pred| |
|---|---|---|---|
"""
for r in d1_rows:
    d1_text += f"| {r['pair']} | {r['predicted_rank']} / {N_C4} | {r['predicted_pctile']:.1f}th | {r['predicted_abs_dq']:.5f} |\n"

d1_text += f"""
## Context

Top-10 percentile cutoff: rank ≤ {int(N_C4*0.10)} ({10.0:.1f}th pctile)
Top-15 percentile cutoff: rank ≤ {int(N_C4*0.15)} ({15.0:.1f}th pctile)
Top-25 percentile cutoff: rank ≤ {int(N_C4*0.25)} ({25.0:.1f}th pctile)

Pairs ranked ABOVE median ({N_C4//2}) are above-average predictions.

## Observed values NOT included in this report.
No success/failure classification made.
Awaiting human review before held-out evaluation is opened.

*D1 scope: forward model prediction only. No reference to observed ΔQ for held-out pairs.*
"""
with open(OUT_DIAG / "d1_heldout_preview.md", "w") as f:
    f.write(d1_text)
print("  Written: d1_heldout_preview.md")

# ═══════════════════════════════════════════════════════════════════════════════
# D2 — RANDOMIZED-P NULL REPAIR
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("D2 — Randomized-P Null Repair (N=100, 2D grid)")
print("=" * 70)

# Use the fine part of the alpha grid only (same as M1 fine range)
ALPHA_LO_FINE = float(alpha_min_M1 * 0.05)  # -2.20
ALPHA_HI_FINE = float(alpha_max_M1 * 0.9)   # +0.060
GRID_N_D2     = 41   # 41-point 1D → 41×41 2D
alpha_1d_d2   = np.linspace(ALPHA_LO_FINE, ALPHA_HI_FINE, GRID_N_D2)
# Also add coarse range for negative sweep
alpha_coarse_d2 = np.linspace(float(alpha_min_M1 * 0.9), ALPHA_LO_FINE, 11, endpoint=False)
alpha_grid_d2   = np.concatenate([alpha_coarse_d2, alpha_1d_d2])
GRID_TOTAL_D2   = len(alpha_grid_d2)
print(f"  Grid: {GRID_TOTAL_D2}×{GRID_TOTAL_D2} = {GRID_TOTAL_D2**2} points per P_rand")

N_RAND_D2 = 100
rng_d2    = np.random.default_rng(2026_06_03 + 99)

M2_rho_best    = np.full(N_RAND_D2, np.nan)
M2_alpha_r_best= np.full(N_RAND_D2, np.nan)
M2_alpha_d_best= np.full(N_RAND_D2, np.nan)
M2_auroc_best  = np.full(N_RAND_D2, np.nan)

def auroc_pdf(dq_pred_flat: np.ndarray) -> float:
    pdf_idx    = np.array([train_mask[k] and
                           (min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in bentley_pdf_c4
                           for k in range(N_C4)])
    nonpdf_idx = train_mask & ~pdf_idx
    ps = np.abs(dq_pred_flat[pdf_idx[train_mask]])
    ns = np.abs(dq_pred_flat[nonpdf_idx])  # wait, need to index properly
    # Simpler: use train set arrays
    dq_train = dq_pred_flat[train_mask]
    pdf_mask_train = np.array([
        (min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in bentley_pdf_c4
        for k in range(N_C4) if train_mask[k]
    ])
    if pdf_mask_train.sum() == 0 or (~pdf_mask_train).sum() == 0:
        return 0.5
    U, _ = stats.mannwhitneyu(
        np.abs(dq_train[pdf_mask_train]),
        np.abs(dq_train[~pdf_mask_train]),
        alternative="greater"
    )
    return float(U / (pdf_mask_train.sum() * (~pdf_mask_train).sum()))

# pre-compute train pdf mask once
train_pdf_mask = np.array([
    (min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in bentley_pdf_c4
    for k in range(N_C4) if train_mask[k]
])

def auroc_train(dq_pred_train: np.ndarray) -> float:
    ps = np.abs(dq_pred_train[train_pdf_mask])
    ns = np.abs(dq_pred_train[~train_pdf_mask])
    if len(ps) == 0 or len(ns) == 0: return 0.5
    U, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(U / (len(ps) * len(ns)))

t0 = time.time()
for k in range(N_RAND_D2):
    Pr_k = P_rand_norm[k]   # (61, 61) normalized random P
    surf  = np.full((GRID_TOTAL_D2, GRID_TOTAL_D2), np.nan)
    for i, ar in enumerate(alpha_grid_d2):
        for j, ad in enumerate(alpha_grid_d2):
            surf[i, j] = spearman_obj(ar, ad, J_base, Pr_k)
    best_flat = int(np.nanargmax(surf))
    bi, bj    = np.unravel_index(best_flat, surf.shape)
    ar0, ad0  = alpha_grid_d2[bi], alpha_grid_d2[bj]
    # Quick Nelder-Mead refinement
    from scipy.optimize import minimize
    def neg_obj_rand(params):
        ar, ad = params
        v = spearman_obj(ar, ad, J_base, Pr_k)
        return -v if not np.isnan(v) else 1.0
    res = minimize(neg_obj_rand, [ar0, ad0], method="Nelder-Mead",
                   options={"maxiter": 500, "xatol": 1e-4, "fatol": 1e-4})
    M2_alpha_r_best[k] = float(res.x[0])
    M2_alpha_d_best[k] = float(res.x[1])
    M2_rho_best[k]     = float(-res.fun)
    # AUROC at best α
    DQ_rand = predict_deltaQ(M2_alpha_r_best[k], M2_alpha_d_best[k], J_base, Pr_k)
    if DQ_rand is not None:
        M2_auroc_best[k] = auroc_train(DQ_rand[train_ii, train_jj])
    if (k + 1) % 10 == 0:
        valid_so_far = ~np.isnan(M2_rho_best[:k+1])
        print(f"  {k+1}/{N_RAND_D2}  ({time.time()-t0:.0f}s)"
              f"  median ρ={np.nanmedian(M2_rho_best[:k+1]):.4f}"
              f"  M1={fit_params['M1']['rho_train']:.4f}")

# Results
valid    = ~np.isnan(M2_rho_best)
m2_median = float(np.nanmedian(M2_rho_best))
m2_p95    = float(np.nanpercentile(M2_rho_best[valid], 95))
m2_p99    = float(np.nanpercentile(M2_rho_best[valid], 99))
m2_max    = float(np.nanmax(M2_rho_best))

rho_M1   = float(fit_params["M1"]["rho_train"])
emp_pval = float((M2_rho_best[valid] >= rho_M1).mean())

print(f"\n  M2 (proper): median={m2_median:.4f}, p95={m2_p95:.4f}, max={m2_max:.4f}")
print(f"  M1: {rho_M1:.4f}")
print(f"  Empirical p-value P(M2 ≥ M1): {emp_pval:.3f}")

auroc_M1 = float(fit_params["M1"]["auroc_pdf_train"])
m2_auroc_median = float(np.nanmedian(M2_auroc_best))
m2_auroc_p95    = float(np.nanpercentile(M2_auroc_best[~np.isnan(M2_auroc_best)], 95))

np.save(OUT_DIAG / "d2_M2_rho_proper.npy", M2_rho_best)
np.save(OUT_DIAG / "d2_M2_alpha.npy", np.vstack([M2_alpha_r_best, M2_alpha_d_best]))

d2_text = f"""# D2 — Randomized-P Null Repair
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Method

For each of {N_RAND_D2} degree-preserving randomized P graphs:
- Fit (α_r, α_d) independently using {GRID_TOTAL_D2}×{GRID_TOTAL_D2} grid + Nelder-Mead
- Same objective as M1: Spearman rank correlation on training Class 4 pairs
- Same J_base (directed A_raw with γ={gamma_J:.3f})

## Objective (ρ_train) Distribution

| Statistic | M2 null (proper) | M1 (real PDF) |
|---|---|---|
| Median | {m2_median:.4f} | — |
| p75 | {np.nanpercentile(M2_rho_best[valid],75):.4f} | — |
| p95 | {m2_p95:.4f} | — |
| p99 | {m2_p99:.4f} | — |
| Max | {m2_max:.4f} | — |
| **M1 value** | — | **{rho_M1:.4f}** |

**Empirical p-value P(M2 ≥ M1) = {emp_pval:.3f}** ({int(emp_pval*N_RAND_D2)}/{N_RAND_D2} random graphs exceed M1)

## AUROC (PDF training pairs) Distribution

| Statistic | M2 null | M1 |
|---|---|---|
| Median | {m2_auroc_median:.4f} | {auroc_M1:.4f} |
| p95 | {m2_auroc_p95:.4f} | — |

## Fitted α Distribution (M2 null)

| Parameter | Median | p5 | p95 |
|---|---|---|---|
| α_roam | {np.nanmedian(M2_alpha_r_best):.3f} | {np.nanpercentile(M2_alpha_r_best[valid],5):.3f} | {np.nanpercentile(M2_alpha_r_best[valid],95):.3f} |
| α_dwell | {np.nanmedian(M2_alpha_d_best):.3f} | {np.nanpercentile(M2_alpha_d_best[valid],5):.3f} | {np.nanpercentile(M2_alpha_d_best[valid],95):.3f} |
| Δα = α_d − α_r | {np.nanmedian(M2_alpha_d_best-M2_alpha_r_best):.3f} | {np.nanpercentile((M2_alpha_d_best-M2_alpha_r_best)[valid],5):.3f} | {np.nanpercentile((M2_alpha_d_best-M2_alpha_r_best)[valid],95):.3f} |

## Interpretation

An empirical p-value near 0 indicates M1 significantly exceeds the null.
An empirical p-value near 1 indicates M1 does not exceed random PDF structure.

Note: The M2 α distribution tells us what α values the objective selects for
random graphs — if these match M1's α, it means the optimum is driven by
degree structure, not PDF identity.
"""
with open(OUT_DIAG / "d2_randomized_pdf_null.md", "w") as f:
    f.write(d2_text)
print("  Written: d2_randomized_pdf_null.md")

# ═══════════════════════════════════════════════════════════════════════════════
# D3 — PDF CONTRIBUTION MAP
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("D3 — PDF Contribution Map")
print("=" * 70)

# ΔQ_pdf = ΔQ_pred(M1) - ΔQ_pred(M0) = ΔQ_pred(M1) - 0 = ΔQ_pred(M1)
DQ_pdf = DQ_M1.copy()   # M0 gives exactly 0 everywhere

dq_pdf_c4     = DQ_pdf[ii_c4, jj_c4]
dq_pdf_abs_c4 = np.abs(dq_pdf_c4)

# Rank by |ΔQ_pdf| among all 1321 Class 4 pairs
rank_ord_pdf  = np.argsort(-dq_pdf_abs_c4)
pdf_pair_rank = np.empty(N_C4, dtype=int)
pdf_pair_rank[rank_ord_pdf] = np.arange(1, N_C4 + 1)

# Top 50 pairs by |ΔQ_pdf|
top50_idx    = rank_ord_pdf[:50]
top50_rows   = []
for pos, k in enumerate(top50_idx):
    i, j     = int(ii_c4[k]), int(jj_c4[k])
    ni, nj   = NEURONS[i], NEURONS[j]
    is_pdf   = (min(i,j), max(i,j)) in bentley_pdf_c4
    src_flag = "SRC" if (i in PDF_SOURCES or j in PDF_SOURCES) else ""
    tgt_flag = "TGT" if (i in PDF_TARGETS or j in PDF_TARGETS) else ""
    held_flag= "HELD" if (i, j) in HELD_OUT_PAIRS else ""
    top50_rows.append({
        "rank": pos + 1, "pair": f"{ni}–{nj}",
        "abs_dq_pdf": round(float(dq_pdf_abs_c4[k]), 5),
        "sign": int(np.sign(dq_pdf_c4[k])),
        "pdf_annotated": is_pdf,
        "source_flag": src_flag,
        "target_flag": tgt_flag,
        "held_out": held_flag,
    })

# Source-neuron breakdown
source_names = {n2i["RID"]: "RID", n2i["ADEL"]: "ADEL",
                n2i["RMEL"]: "RMEL", n2i["RMER"]: "RMER", n2i["AVDL"]: "AVDL"}
source_stats = {}
for sname, sidx in [(v, k) for k, v in source_names.items()]:
    src_pairs   = [(ii_c4[k], jj_c4[k]) for k in range(N_C4)
                   if ii_c4[k] == sidx or jj_c4[k] == sidx]
    if not src_pairs:
        continue
    src_abs     = [float(dq_pdf_abs_c4[np.where((ii_c4 == p[0]) & (jj_c4 == p[1]))[0][0]])
                   for p in src_pairs
                   if len(np.where((ii_c4 == p[0]) & (jj_c4 == p[1]))[0]) > 0]
    source_stats[sname] = {
        "n_pairs":        len(src_pairs),
        "mean_abs_dq_pdf": round(float(np.mean(src_abs)) if src_abs else 0, 5),
        "max_abs_dq_pdf":  round(float(np.max(src_abs)) if src_abs else 0, 5),
        "n_in_top100":    sum(1 for r in top50_rows[:100] if sname in r["pair"]),
    }
    print(f"  {sname}: n={len(src_pairs)}, mean|ΔQ_pdf|={source_stats[sname]['mean_abs_dq_pdf']:.4f}, "
          f"max={source_stats[sname]['max_abs_dq_pdf']:.4f}")

# PDF-annotated vs non-PDF enrichment in top-K
for K in [50, 100, 200]:
    topk_idx      = rank_ord_pdf[:K]
    n_pdf_in_topk = sum(1 for k in topk_idx
                        if (min(int(ii_c4[k]),int(jj_c4[k])),
                            max(int(ii_c4[k]),int(jj_c4[k]))) in bentley_pdf_c4)
    expected      = len(bentley_pdf_c4) * K / N_C4
    print(f"  Top-{K}: {n_pdf_in_topk} PDF pairs (expected {expected:.1f} by chance)")

d3_text = "# D3 — PDF Contribution Map\nDate: 2026-06-03\n\n"
d3_text += "ΔQ_pdf = ΔQ_pred(M1) − ΔQ_pred(M0) = ΔQ_pred(M1) (since M0 predicts ΔQ=0 everywhere).\n\n"
d3_text += "## Top 50 Class 4 Pairs by |ΔQ_pdf|\n\n"
d3_text += "| Rank | Pair | |ΔQ_pdf| | Sign | PDF? | Source? | Target? | Held-out? |\n"
d3_text += "|---|---|---|---|---|---|---|---|\n"
for r in top50_rows:
    d3_text += (f"| {r['rank']} | {r['pair']} | {r['abs_dq_pdf']:.5f} | "
                f"{'−' if r['sign']<0 else '+' if r['sign']>0 else '0'} | "
                f"{'YES' if r['pdf_annotated'] else ''} | {r['source_flag']} | "
                f"{r['target_flag']} | {r['held_out']} |\n")
d3_text += "\n## PDF-Annotated Enrichment in Top-K\n\n"
d3_text += f"Total PDF Class 4 pairs: {len(bentley_pdf_c4)} / {N_C4} = {100*len(bentley_pdf_c4)/N_C4:.1f}%\n\n"
d3_text += "| K | N PDF in top-K | Expected by chance | Enrichment ratio |\n|---|---|---|---|\n"
for K in [20, 50, 100, 200, 500]:
    topk_idx2     = rank_ord_pdf[:K]
    n_pdf_topk    = sum(1 for k in topk_idx2
                        if (min(int(ii_c4[k]),int(jj_c4[k])),
                            max(int(ii_c4[k]),int(jj_c4[k]))) in bentley_pdf_c4)
    expected_topk = len(bentley_pdf_c4) * K / N_C4
    ratio         = n_pdf_topk / expected_topk if expected_topk > 0 else float("inf")
    d3_text += f"| {K} | {n_pdf_topk} | {expected_topk:.1f} | {ratio:.2f}× |\n"
d3_text += "\n## Source-Neuron Breakdown\n\n"
d3_text += "| Source | N C4 pairs | Mean |ΔQ_pdf| | Max |ΔQ_pdf| |\n|---|---|---|---|\n"
for sname, stat in source_stats.items():
    d3_text += f"| {sname} | {stat['n_pairs']} | {stat['mean_abs_dq_pdf']:.4f} | {stat['max_abs_dq_pdf']:.4f} |\n"
d3_text += "\n*Note: Held-out ADEL pairs appear with HELD flag. Their ranks are reported but observed ΔQ not consulted.*\n"
with open(OUT_DIAG / "d3_pdf_contribution_map.md", "w") as f:
    f.write(d3_text)
print("  Written: d3_pdf_contribution_map.md")

# ═══════════════════════════════════════════════════════════════════════════════
# D4 — ALPHA LANDSCAPE
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("D4 — α Landscape")
print("=" * 70)

# 1D sweeps
alpha_sweep_fine   = np.linspace(ALPHA_LO_FINE, ALPHA_HI_FINE, 81)
alpha_sweep_full   = np.concatenate([
    np.linspace(float(alpha_min_M1 * 0.95), ALPHA_LO_FINE, 21, endpoint=False),
    alpha_sweep_fine,
])

# Sweep 1: Fix α_r = 0, vary α_d (full range)
rho_sweep_d_only = np.array([
    spearman_obj(0.0, ad, J_base, P_norm)
    for ad in alpha_sweep_full
])
# Sweep 2: Δα = α_d - α_r, fixing mean at M1 mean = (alpha_r_M1 + alpha_d_M1)/2
alpha_mean_M1 = (alpha_r_M1 + alpha_d_M1) / 2.0
delta_sweep   = np.linspace(-10.0, 10.0, 81)
rho_sweep_delta = []
for da in delta_sweep:
    ar = alpha_mean_M1 - da / 2
    ad = alpha_mean_M1 + da / 2
    rho_sweep_delta.append(spearman_obj(ar, ad, J_base, P_norm))
rho_sweep_delta = np.array(rho_sweep_delta)

# Sweep 3: Fix α_r = α_r_M1, vary α_d (sensitivity of dwell axis)
rho_sweep_dwell_only = np.array([
    spearman_obj(alpha_r_M1, ad, J_base, P_norm)
    for ad in alpha_sweep_full
])

print(f"  Sweep 1 (α_r=0, α_d varied): max ρ={rho_sweep_d_only.max():.4f} at α_d={alpha_sweep_full[rho_sweep_d_only.argmax()]:.3f}")
print(f"  Sweep 2 (Δα varied, mean={alpha_mean_M1:.2f}): max ρ={rho_sweep_delta.max():.4f} at Δα={delta_sweep[rho_sweep_delta.argmax()]:.3f}")
print(f"  Sweep 3 (α_r={alpha_r_M1:.2f}, α_d varied): max ρ={rho_sweep_dwell_only.max():.4f}")

# Characterize shape: plateau or sharp?
sweep3_max_idx = rho_sweep_dwell_only.argmax()
sweep3_halfmax = rho_sweep_dwell_only.max() / 2 if rho_sweep_dwell_only.max() > 0 else 0
n_above_half3  = (rho_sweep_dwell_only > sweep3_halfmax).sum()
print(f"  Sweep 3 shape: {n_above_half3}/{len(rho_sweep_dwell_only)} points above half-max → {'BROAD PLATEAU' if n_above_half3 > 20 else 'SHARP'}")

np.save(OUT_DIAG / "d4_rho_sweep_dfull.npy", rho_sweep_d_only)
np.save(OUT_DIAG / "d4_rho_sweep_delta.npy", rho_sweep_delta)
np.save(OUT_DIAG / "d4_rho_sweep_dwell.npy", rho_sweep_dwell_only)
np.save(OUT_DIAG / "d4_alpha_sweep_full.npy", alpha_sweep_full)
np.save(OUT_DIAG / "d4_delta_sweep.npy",      delta_sweep)

d4_text = f"""# D4 — α Landscape
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Sweep 1: α_r = 0, α_d varied across full stability range [{alpha_sweep_full[0]:.2f}, {alpha_sweep_full[-1]:.3f}]

| Range | Max ρ | Best α_d | Shape |
|---|---|---|---|
| Full | {rho_sweep_d_only.max():.4f} | {alpha_sweep_full[rho_sweep_d_only.argmax()]:.3f} | {'{0} points above half-max'.format(n_above_half3)} |

α_max boundary at {alpha_max_M1:.4f}. α_min boundary at {alpha_min_M1:.2f}.

## Sweep 2: Δα varied (mean α fixed at M1 mean = {alpha_mean_M1:.2f})

| Δα range | Max ρ | Best Δα | Optimum boundary-seeking? |
|---|---|---|---|
| [−10, +10] | {rho_sweep_delta.max():.4f} | {delta_sweep[rho_sweep_delta.argmax()]:.3f} | {'YES (at boundary)' if abs(delta_sweep[rho_sweep_delta.argmax()]) > 8 else 'NO (interior)'} |

M1 fitted Δα = {alpha_d_M1 - alpha_r_M1:+.3f}.

## Sweep 3: α_r = {alpha_r_M1:.2f} (M1 fitted), α_d varied

Max ρ = {rho_sweep_dwell_only.max():.4f} at α_d = {alpha_sweep_full[rho_sweep_dwell_only.argmax()]:.3f}.
Shape: {n_above_half3}/{len(rho_sweep_dwell_only)} points above half-max objective.
Shape classification: {'BROAD PLATEAU — objective weakly sensitive to exact α_d' if n_above_half3 > 25 else 'MODERATELY PEAKED' if n_above_half3 > 10 else 'SHARP PEAK'}.

## Summary

The α landscape characterizes whether:
- The optimum is sharply localized (strong signal), or
- A broad plateau (objective weakly informative), or
- Boundary-seeking (pushed against the stability limit)

Implications:
- Boundary-seeking: model at edge of stability → potentially pathological fit
- Broad plateau: weak signal; many α values give similar ρ
- Sharp peak: strong constraint on α from data
"""
with open(OUT_DIAG / "d4_alpha_landscape.md", "w") as f:
    f.write(d4_text)
print("  Written: d4_alpha_landscape.md")

# ═══════════════════════════════════════════════════════════════════════════════
# D5 — SPARSITY MISMATCH AUDIT
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("D5 — Sparsity Mismatch Audit")
print("=" * 70)

dq_obs_c4  = DQ_obs_cep[ii_c4, jj_c4]
dq_pred_c4 = DQ_M1[ii_c4, jj_c4]

obs_nonzero  = (dq_obs_c4 != 0).sum()
pred_nonzero = (np.abs(dq_pred_c4) > 1e-10).sum()
obs_density  = obs_nonzero / N_C4
pred_density = pred_nonzero / N_C4

print(f"  Observed ΔQ:   {obs_nonzero}/{N_C4} nonzero ({obs_density*100:.1f}%)")
print(f"  Predicted ΔQ:  {pred_nonzero}/{N_C4} nonzero ({pred_density*100:.1f}%)")

# Rank-based overlap for top-K
obs_rank  = np.argsort(-np.abs(dq_obs_c4))   # rank by |ΔQ_obs|
pred_rank = np.argsort(-np.abs(dq_pred_c4))  # rank by |ΔQ_pred|

overlap_stats = {}
for K in [10, 20, 50, 100, 200, 500]:
    obs_topk  = set(obs_rank[:K])
    pred_topk = set(pred_rank[:K])
    overlap   = len(obs_topk & pred_topk)
    expected  = K * K / N_C4
    overlap_stats[K] = {
        "overlap": overlap,
        "expected_random": round(expected, 1),
        "enrichment": round(overlap / expected, 2) if expected > 0 else float("inf"),
    }
    print(f"  Top-{K:4d}: {overlap} pairs in common (expected {expected:.1f}, ratio={overlap/expected:.2f}×)")

# Where the predicted top-K actually come from (source analysis)
pred_top20 = [int(v) for v in pred_rank[:20]]
pred_top20_neurons = [(NEURONS[ii_c4[k]], NEURONS[jj_c4[k]]) for k in pred_top20]
print("\n  Predicted top-20 pairs:")
for rank_i, (na, nb) in enumerate(pred_top20_neurons):
    is_held = (n2i[na], n2i[nb]) in HELD_OUT_PAIRS or (n2i[nb], n2i[na]) in HELD_OUT_PAIRS
    print(f"    {rank_i+1:3d}. {na}–{nb}{'  [HELD-OUT]' if is_held else ''}")

# Conditional Spearman: only nonzero-observed pairs
nonzero_mask = dq_obs_c4 != 0
dq_obs_nz   = np.abs(dq_obs_c4[nonzero_mask])
dq_pred_nz  = np.abs(dq_pred_c4[nonzero_mask])
rho_nz, pv_nz = stats.spearmanr(dq_pred_nz, dq_obs_nz)
print(f"\n  Spearman on nonzero-observed pairs only: ρ={rho_nz:.4f} (p={pv_nz:.4f}, n={nonzero_mask.sum()})")
print(f"  Spearman on ALL training pairs (M1 objective): ρ={float(fit_params['M1']['rho_train']):.4f}")

d5_text = f"""# D5 — Sparsity Mismatch Audit
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Density Comparison

| | Nonzero entries | Density |
|---|---|---|
| Observed ΔQ (Class 4) | {obs_nonzero} / {N_C4} | {obs_density*100:.1f}% |
| Predicted ΔQ_M1 (Class 4) | {pred_nonzero} / {N_C4} | {pred_density*100:.1f}% |

The Lyapunov-derived precision matrix is **dense** (all entries nonzero), while the
graphical lasso ΔQ_obs is **sparse** (82% zeros enforced by regularization).

## Top-K Rank Overlap

| K | Overlap | Expected (random) | Enrichment |
|---|---|---|---|
"""
for K, stat in overlap_stats.items():
    d5_text += f"| {K} | {stat['overlap']} | {stat['expected_random']} | {stat['enrichment']}× |\n"

d5_text += f"""
## Conditional Spearman (nonzero-observed pairs only)

Spearman on pairs where |ΔQ_obs| > 0:
ρ = {rho_nz:.4f} (p = {pv_nz:.4f}, n = {nonzero_mask.sum()})

Compare to full training objective (all pairs, 82% zeros included): ρ = {float(fit_params['M1']['rho_train']):.4f}

## Key Question

Is the weak Spearman caused by dense prediction vs. sparse observation?

The conditional Spearman on nonzero pairs ({rho_nz:.4f}) is {'SIMILAR TO' if abs(rho_nz - float(fit_params['M1']['rho_train'])) < 0.01 else 'DIFFERENT FROM'} the full-pair Spearman ({float(fit_params['M1']['rho_train']):.4f}).
"""
with open(OUT_DIAG / "d5_sparsity_audit.md", "w") as f:
    f.write(d5_text)
print("  Written: d5_sparsity_audit.md")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DIAGNOSTIC REPORT
# ═══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("Writing phase3a_diagnostic_report.md")
print("=" * 70)

sweep3_shape = ('BROAD PLATEAU — objective weakly sensitive to exact α_d'
                if n_above_half3 > 25 else
                'MODERATELY PEAKED' if n_above_half3 > 10 else 'SHARP PEAK')

d4_best_alpha_d_sweep1 = float(alpha_sweep_full[rho_sweep_d_only.argmax()])
d4_max_rho_sweep1      = float(rho_sweep_d_only.max())

diag_report = f"""# Phase 3A Diagnostic Report
Date: 2026-06-03
Authorization: Phase 3A.5-D
Status: COMPLETE — awaiting review before held-out evaluation

---

## D1 — Held-Out Preview

Predicted rankings for 4 ADEL held-out pairs under M1 (α_r={alpha_r_M1:.2f}, α_d={alpha_d_M1:.2f}):

| Pair | Predicted rank | Percentile | |ΔQ_pred| |
|---|---|---|---|
"""
for r in d1_rows:
    diag_report += f"| {r['pair']} | {r['predicted_rank']} / {N_C4} | {r['predicted_pctile']:.1f}th | {r['predicted_abs_dq']:.5f} |\n"

diag_report += f"""
Observed ΔQ for these pairs: **NOT consulted.** No success/failure judgment made.

---

## D2 — Randomized-P Null (Corrected, N={N_RAND_D2})

Proper 2D fit ({GRID_TOTAL_D2}×{GRID_TOTAL_D2}) applied independently to each P_rand.

| Metric | M1 (Bentley PDF) | M2 null median | M2 null p95 |
|---|---|---|---|
| ρ_train (Spearman) | **{rho_M1:.4f}** | {m2_median:.4f} | {m2_p95:.4f} |

**Empirical p-value P(M2 ≥ M1) = {emp_pval:.3f}**

Interpretation:
- p-value near 0: M1 significantly exceeds null (PDF structure adds signal)
- p-value near 1: M1 does not exceed random structure (PDF identity does not matter)

M2 α distribution (roam/dwell): median α_r = {np.nanmedian(M2_alpha_r_best):.2f}, α_d = {np.nanmedian(M2_alpha_d_best):.2f}
Compare M1: α_r = {alpha_r_M1:.2f}, α_d = {alpha_d_M1:.2f}

---

## D3 — PDF Contribution Map

| Rank | Pair | |ΔQ_pdf| | PDF? | Source? |
|---|---|---|---|---|
"""
for r in top50_rows[:20]:
    diag_report += (f"| {r['rank']} | {r['pair']} | {r['abs_dq_pdf']:.5f} | "
                    f"{'YES' if r['pdf_annotated'] else ''} | {r['source_flag']} |\n")

diag_report += f"""
Top-K PDF enrichment in predicted list:
"""
for K in [20, 50, 100]:
    topk_i2   = rank_ord_pdf[:K]
    n_pdf_tk  = sum(1 for k in topk_i2
                    if (min(int(ii_c4[k]),int(jj_c4[k])),
                        max(int(ii_c4[k]),int(jj_c4[k]))) in bentley_pdf_c4)
    expected2 = len(bentley_pdf_c4) * K / N_C4
    diag_report += f"- Top-{K}: {n_pdf_tk} PDF pairs (expected {expected2:.1f}; {n_pdf_tk/expected2:.1f}×)\n"

diag_report += f"""
Source-neuron concentrations:
"""
for sname, stat in source_stats.items():
    diag_report += f"- {sname}: mean |ΔQ_pdf| = {stat['mean_abs_dq_pdf']:.4f}\n"

diag_report += f"""
---

## D4 — α Landscape

Sweep 1 (α_r=0, α_d varied): max ρ={d4_max_rho_sweep1:.4f} at α_d={d4_best_alpha_d_sweep1:.3f}
Sweep 3 shape: **{sweep3_shape}** ({n_above_half3}/{len(rho_sweep_dwell_only)} points above half-max)

Optimum boundary-seeking? {'YES' if abs(alpha_r_M1) > abs(alpha_min_M1)*0.7 else 'NO'} (M1 |α_r|={abs(alpha_r_M1):.1f} vs |α_min|={abs(alpha_min_M1):.1f})

---

## D5 — Sparsity Mismatch

| | Density |
|---|---|
| ΔQ_obs | {obs_density*100:.1f}% nonzero |
| ΔQ_pred (M1) | {pred_density*100:.1f}% nonzero |

Top-K overlap enrichment:
"""
for K, stat in list(overlap_stats.items())[:4]:
    diag_report += f"- Top-{K}: {stat['overlap']}/{K} overlap ({stat['enrichment']}× expected)\n"

diag_report += f"""
Conditional Spearman (nonzero-observed pairs only): ρ = {rho_nz:.4f} (n={nonzero_mask.sum()})
Full-pairs Spearman (M1 objective): ρ = {float(fit_params['M1']['rho_train']):.4f}

---

## Summary for Human Review

| Diagnostic | Question | Finding |
|---|---|---|
| D1 | Are held-out pairs in interesting regime? | See ranks above |
| D2 | Does real PDF beat random PDF? | p-value = {emp_pval:.3f} |
| D3 | Is prediction concentrated at PDF sources? | See top-20 table |
| D4 | Is α optimum sharp or boundary-seeking? | {sweep3_shape.split(' — ')[0]} |
| D5 | Does dense/sparse mismatch explain weak ρ? | Conditional ρ = {rho_nz:.4f} vs full ρ = {float(fit_params['M1']['rho_train']):.4f} |

**STOP. Awaiting human review before held-out evaluation.**
"""

with open(OUT_P3 / "phase3a_diagnostic_report.md", "w") as f:
    f.write(diag_report)

print("  Written: phase3a_diagnostic_report.md")
print()
print("All diagnostics complete.")
print(">>> STOP CONDITION <<<")
print("Do NOT evaluate held-out pairs. Do NOT begin Phase 3B.")
