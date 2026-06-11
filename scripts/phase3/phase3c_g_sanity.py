"""Phase 3C-G — Ω Sanity Check: Why Does AUROC Increase?

Authorization: Phase 3C-G, 2026-06-03.

Computes pair-level movement tables for all 61 Bentley PDF Class 4 pairs,
source/target attribution, and quantitative AUROC explanation.

PROHIBITIONS: No new fitting. No held-out evaluation. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT3C = ROOT / "results/phase3c"

# ── Load metadata ──────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Class 4 pairs ──────────────────────────────────────────────────────────────
ranked_c4 = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

# ── Load ΔQ and D_emp ─────────────────────────────────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r + Q_r.T)/2
Q_d = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d + Q_d.T)/2
DQ  = Q_r - Q_d

D_emp = np.load(OUT3C / "D_emp_cepnem.npy")
DO    = D_emp @ DQ           # ΔΩ_full

dq_c4 = np.abs(DQ[ii_c4, jj_c4])
do_c4 = np.abs(DO[ii_c4, jj_c4])

# Build ranks (1 = highest)
rank_dq = np.empty(N_C4, dtype=int)
rank_dq[np.argsort(-dq_c4)] = np.arange(1, N_C4+1)
rank_do = np.empty(N_C4, dtype=int)
rank_do[np.argsort(-do_c4)] = np.arange(1, N_C4+1)

# ── Bentley PDF annotation ─────────────────────────────────────────────────────
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
PEP_CSV  = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"

pdf_pairs_directed: list[tuple[int,int]] = []   # (src, tgt) directed
pdf_c4: set = set()

with open(PEP_CSV) as f:
    reader = csv.reader(f); next(reader)
    seen: set = set()
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        key = (min(a,b), max(a,b))
        if key in c4_set:
            pdf_c4.add(key)
            if (a, b) not in seen:
                seen.add((a, b))
                pdf_pairs_directed.append((a, b))

pdf_mask = np.array([(min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in pdf_c4
                     for k in range(N_C4)])
N_PDF = pdf_mask.sum()
pdf_idx = np.where(pdf_mask)[0]   # indices into Class 4 of PDF pairs
print(f"PDF Class 4 pairs: {N_PDF}")

# PDF source neurons (from Bentley directed graph)
pdf_sources = set()
pdf_targets = set()
for (a, b) in pdf_pairs_directed:
    pdf_sources.add(a)
    pdf_targets.add(b)
print(f"PDF sources (directed): {[NEURONS[i] for i in sorted(pdf_sources)]}")
print(f"PDF targets (directed): {[NEURONS[i] for i in sorted(pdf_targets)][:10]}...")

# ── G1: Pair Movement Table ───────────────────────────────────────────────────
print("\n" + "="*70)
print("G1 — Pair Movement Table (all PDF Class 4 pairs)")
print("="*70)

rows = []
for k in pdf_idx:
    i, j = ii_c4[k], jj_c4[k]
    rdq = int(rank_dq[k]); rdo = int(rank_do[k])
    delta = rdq - rdo      # positive = moved UP in Ω
    rows.append({
        "k": int(k),
        "pair": f"{NEURONS[i]}–{NEURONS[j]}",
        "i": i, "j": j,
        "dq": float(dq_c4[k]),
        "do": float(do_c4[k]),
        "rank_dq": rdq,
        "rank_do": rdo,
        "delta_rank": int(delta),   # positive = upward
        "src_i": (i in pdf_sources) or (j in pdf_sources),
        "src_j": (j in pdf_sources) or (i in pdf_sources),
        "is_adel": (i == n2i["ADEL"]) or (j == n2i["ADEL"]),
        "is_ury": any(NEURONS[x] in {"URYDL","URYVL","URYVR","URXL"} for x in [i,j]),
        "is_rme": any(NEURONS[x] in {"RMEL","RMER"} for x in [i,j]),
        "is_rid": any(NEURONS[x] == "RID" for x in [i,j]),
        "source_names": [NEURONS[x] for x in [i, j] if x in pdf_sources],
    })

rows.sort(key=lambda r: -r["delta_rank"])  # most upward first

print(f"\nAll {N_PDF} PDF Class 4 pairs sorted by Δrank (rank_Q - rank_Ω):")
print(f"  {'Pair':20s}  {'ΔQ':>7s}  {'ΔΩ':>7s}  {'rank_Q':>7s}  {'rank_Ω':>7s}  {'Δrank':>6s}  Source")
for r in rows:
    src = ",".join(r["source_names"]) if r["source_names"] else "?"
    print(f"  {r['pair']:20s}  {r['dq']:7.4f}  {r['do']:7.4f}  "
          f"{r['rank_dq']:7d}  {r['rank_do']:7d}  {r['delta_rank']:+6d}  {src}")

upward   = [r for r in rows if r["delta_rank"] > 0]
downward = [r for r in rows if r["delta_rank"] < 0]
unchanged = [r for r in rows if r["delta_rank"] == 0]
print(f"\nMovement summary: {len(upward)} upward, {len(downward)} downward, "
      f"{len(unchanged)} unchanged")
print(f"Mean Δrank across all PDF pairs: {np.mean([r['delta_rank'] for r in rows]):.1f}")
print(f"Median Δrank: {np.median([r['delta_rank'] for r in rows]):.1f}")

# ── G2: Source/Target Attribution ─────────────────────────────────────────────
print("\n" + "="*70)
print("G2 — Source/Target Attribution")
print("="*70)

# Group by source neuron in Bentley annotation
source_stats: dict = {}
for src_idx in sorted(pdf_sources):
    src_name = NEURONS[src_idx]
    src_rows = [r for r in rows if src_idx in [r["i"], r["j"]]
                                 and src_idx in pdf_sources]
    if not src_rows: continue
    deltas = [r["delta_rank"] for r in src_rows]
    source_stats[src_name] = {
        "n_pairs": len(src_rows),
        "mean_delta": float(np.mean(deltas)),
        "median_delta": float(np.median(deltas)),
        "n_upward": sum(1 for d in deltas if d > 0),
        "n_downward": sum(1 for d in deltas if d < 0),
        "pairs": [r["pair"] for r in src_rows],
        "deltas": deltas,
    }

print("\nBy source neuron (Bentley directed sources):")
for src, st in sorted(source_stats.items(), key=lambda x: -x[1]["mean_delta"]):
    print(f"  {src:6s}: n={st['n_pairs']:2d}  mean_Δ={st['mean_delta']:+6.1f}  "
          f"median_Δ={st['median_delta']:+6.1f}  "
          f"up={st['n_upward']} dn={st['n_downward']}")

# Target neurons
target_stats: dict = {}
for tgt_idx in sorted(pdf_targets):
    tgt_name = NEURONS[tgt_idx]
    tgt_rows = [r for r in rows if tgt_idx in [r["i"], r["j"]]
                                 and tgt_idx in pdf_targets]
    if not tgt_rows: continue
    deltas = [r["delta_rank"] for r in tgt_rows]
    target_stats[tgt_name] = {
        "n_pairs": len(tgt_rows),
        "mean_delta": float(np.mean(deltas)),
        "pairs": [r["pair"] for r in tgt_rows],
        "deltas": deltas,
    }

print("\nBy target neuron (Bentley pdfr-1 targets):")
for tgt, st in sorted(target_stats.items(), key=lambda x: -x[1]["mean_delta"]):
    print(f"  {tgt:6s}: n={st['n_pairs']:2d}  mean_Δ={st['mean_delta']:+6.1f}")

# ADEL vs non-ADEL split
adel_rows   = [r for r in rows if r["is_adel"]]
nonadel_pdf = [r for r in rows if not r["is_adel"]]
print(f"\nADEL-involved PDF pairs: n={len(adel_rows)}, "
      f"mean_Δ={np.mean([r['delta_rank'] for r in adel_rows]):.1f}")
print(f"Non-ADEL PDF pairs:      n={len(nonadel_pdf)}, "
      f"mean_Δ={np.mean([r['delta_rank'] for r in nonadel_pdf]):.1f}")

# ── G3: Top-20 Comparison ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("G3 — Top-20 Comparison")
print("="*70)

top20_dq_idx = set(np.argsort(-dq_c4)[:20])
top20_do_idx = set(np.argsort(-do_c4)[:20])

entering  = top20_do_idx - top20_dq_idx
departing = top20_dq_idx - top20_do_idx

print(f"\nPairs entering ΔΩ top-20 (not in ΔQ top-20): {len(entering)}")
for k in sorted(entering, key=lambda k: rank_do[k]):
    i, j = ii_c4[k], jj_c4[k]
    is_pdf  = (min(i,j),max(i,j)) in pdf_c4
    is_adel = (i == n2i["ADEL"] or j == n2i["ADEL"])
    is_ury  = any(NEURONS[x] in {"URYDL","URYVL","URYVR","URXL"} for x in [i,j])
    print(f"  {NEURONS[i]:6s}–{NEURONS[j]:6s}: "
          f"ΔΩ_rank={rank_do[k]:3d}  ΔQ_rank={rank_dq[k]:3d}  "
          f"Δrank={rank_dq[k]-rank_do[k]:+d}  "
          f"PDF={is_pdf}  ADEL={is_adel}  URY={is_ury}")

print(f"\nPairs departing ΔQ top-20 (not in ΔΩ top-20): {len(departing)}")
for k in sorted(departing, key=lambda k: rank_dq[k]):
    i, j = ii_c4[k], jj_c4[k]
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    print(f"  {NEURONS[i]:6s}–{NEURONS[j]:6s}: "
          f"ΔQ_rank={rank_dq[k]:3d}  ΔΩ_rank={rank_do[k]:3d}  "
          f"Δrank={rank_dq[k]-rank_do[k]:+d}  PDF={is_pdf}")

# ── G4: Why Does AUROC Increase? ──────────────────────────────────────────────
print("\n" + "="*70)
print("G4 — AUROC Decomposition")
print("="*70)

# AUROC = E[score_pdf > score_nonpdf]
# = P(a randomly chosen PDF pair ranks higher than a randomly chosen non-PDF pair)

# Under ΔQ: which non-PDF pairs are 'beaten' by PDF?
# Under ΔΩ: how does this change?

def auroc_exact(ann, scores):
    ps = scores[ann]; ns = scores[~ann]
    u, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(u / (len(ps)*len(ns)))

auroc_dq = auroc_exact(pdf_mask, dq_c4)
auroc_do = auroc_exact(pdf_mask, do_c4)
print(f"\nAUROC: ΔQ={auroc_dq:.4f}  ΔΩ={auroc_do:.4f}  Δ={auroc_do-auroc_dq:+.4f}")

# Measure A: mean rank of PDF pairs in each framework
mean_rank_dq = np.mean(rank_dq[pdf_mask])
mean_rank_do = np.mean(rank_do[pdf_mask])
print(f"\nMean rank of PDF pairs: ΔQ={mean_rank_dq:.1f}  ΔΩ={mean_rank_do:.1f}  "
      f"Δ={mean_rank_do-mean_rank_dq:+.1f}")

# Measure B: distribution of rank changes
deltas = rank_dq[pdf_mask] - rank_do[pdf_mask]  # positive = upward
print(f"\nRank change distribution (rank_Q - rank_Ω, positive=upward):")
print(f"  Mean:   {deltas.mean():+.1f}")
print(f"  Median: {np.median(deltas):+.1f}")
print(f"  Std:    {deltas.std():.1f}")
print(f"  Min:    {deltas.min():+d}")
print(f"  Max:    {deltas.max():+d}")
print(f"  n upward:    {(deltas > 0).sum()} / {N_PDF}")
print(f"  n unchanged: {(deltas == 0).sum()} / {N_PDF}")
print(f"  n downward:  {(deltas < 0).sum()} / {N_PDF}")

# Quantile breakdown
for q in [25, 50, 75, 90, 95]:
    print(f"  p{q}: {np.percentile(deltas, q):+.0f}")

# Non-PDF rank changes for comparison
nonpdf_deltas = rank_dq[~pdf_mask] - rank_do[~pdf_mask]
print(f"\nNon-PDF rank changes:")
print(f"  Mean: {nonpdf_deltas.mean():+.2f}  Std: {nonpdf_deltas.std():.1f}")
print(f"  n upward:   {(nonpdf_deltas > 0).sum()} / {(~pdf_mask).sum()}")
print(f"  n downward: {(nonpdf_deltas < 0).sum()} / {(~pdf_mask).sum()}")

# Mechanism: few large movers vs many small movers
# Split by Δrank magnitude
large_movers = [r for r in rows if abs(r["delta_rank"]) >= 50]
small_movers = [r for r in rows if 0 < abs(r["delta_rank"]) < 50]
print(f"\nLarge movers (|Δrank| ≥ 50): {len(large_movers)}")
for r in large_movers:
    print(f"  {r['pair']:20s}: Δrank={r['delta_rank']:+d}  "
          f"(Q:{r['rank_dq']} → Ω:{r['rank_do']})")

# Counterfactual: AUROC if only the large movers changed (fix small movers at ΔQ rank)
large_upward = [r for r in rows if r["delta_rank"] >= 50]
print(f"\nLarge upward movers (Δrank ≥ 50): {len(large_upward)}")
for r in large_upward:
    print(f"  {r['pair']:20s}: Δrank={r['delta_rank']:+d}  ADEL={r['is_adel']}  URY={r['is_ury']}")

# AUROC impact per pair: contribution to AUROC change
# AUROC = (1/N_pdf/N_nonpdf) * sum_{pdf_i} sum_{nonpdf_j} I(score_i > score_j)
# Change in AUROC = change in pairwise concordance
print(f"\nRaw concordance change:")
# Count concordant pairs under ΔQ vs ΔΩ
N_nonpdf = int((~pdf_mask).sum())
conc_dq = 0; conc_do = 0
pdf_scores_dq  = dq_c4[pdf_mask]; pdf_scores_do  = do_c4[pdf_mask]
npdf_scores_dq = dq_c4[~pdf_mask]; npdf_scores_do = do_c4[~pdf_mask]
# Vectorized
for ps in pdf_scores_dq:
    conc_dq += (npdf_scores_dq < ps).sum()
for ps in pdf_scores_do:
    conc_do += (npdf_scores_do < ps).sum()
delta_conc = conc_do - conc_dq
total = N_PDF * N_nonpdf
print(f"  ΔQ concordant pairs: {conc_dq}/{total} ({100*conc_dq/total:.1f}%)")
print(f"  ΔΩ concordant pairs: {conc_do}/{total} ({100*conc_do/total:.1f}%)")
print(f"  Added concordant pairs: {delta_conc} ({100*delta_conc/total:.2f}%)")

# ── Save results ───────────────────────────────────────────────────────────────
result = {
    "date": "2026-06-03",
    "authorization": "Phase 3C-G",
    "n_pdf_c4": int(N_PDF),
    "auroc_dq": float(auroc_dq),
    "auroc_do": float(auroc_do),
    "delta_auroc": float(auroc_do - auroc_dq),
    "mean_rank_dq": float(mean_rank_dq),
    "mean_rank_do": float(mean_rank_do),
    "pair_movements": rows,
    "source_stats": source_stats,
    "target_stats": target_stats,
    "upward_count": int(len(upward)),
    "downward_count": int(len(downward)),
    "unchanged_count": int(len(unchanged)),
    "delta_rank_mean": float(deltas.mean()),
    "delta_rank_median": float(np.median(deltas)),
    "delta_rank_std": float(deltas.std()),
    "n_large_upward_ge50": len(large_upward),
    "delta_concordant_pairs": int(delta_conc),
    "total_pairs": int(total),
}

def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v = float(obj); return None if (v != v or abs(v) == float("inf")) else v
    if isinstance(obj, float):
        return None if (obj != obj or abs(obj) == float("inf")) else obj
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.bool_,)):   return bool(obj)
    if isinstance(obj, np.ndarray):    return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict):          return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [sanitize(v) for v in obj]
    return obj

import json as json_mod
with open(OUT3C / "phase3c_g_results.json", "w") as f:
    json_mod.dump(sanitize(result), f, indent=2)
print("\nSaved: phase3c_g_results.json")
