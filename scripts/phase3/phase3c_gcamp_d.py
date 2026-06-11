"""Phase 3C supplement — GCaMP D-characterization.

Compute D2 (residual variance) and D3 (first-difference innovation variance)
for the raw GCaMP coordinate, using the exact procedures from Phase 3C.

Then compute ΔΩ = D · ΔQ_gcamp and compare rankings vs ΔQ_gcamp.

Authorization: Phase 3C supplement, 2026-06-03.
PROHIBITIONS: No held-out evaluation. No new fitting. No new hypotheses.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import h5py
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.phase1.stage0_cepnem import build_label_maps

OUT3C = ROOT / "results/phase3c"

# ── Load neuron metadata ──────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
REC_IDS = cop["recording_ids"]
N = len(NEURONS)
N_REC = len(REC_IDS)
n2i = {n: i for i, n in enumerate(NEURONS)}

# ── Load GCaMP ΔQ and Class 4 pairs ──────────────────────────────────────────
PREC_DIR  = ROOT / "results/phase2/stage1/precision"
Q_r_g = np.load(PREC_DIR / "Q_gcamp_roam_conf.npy");  Q_r_g = (Q_r_g + Q_r_g.T) / 2
Q_d_g = np.load(PREC_DIR / "Q_gcamp_dwell_conf.npy"); Q_d_g = (Q_d_g + Q_d_g.T) / 2
DQ_g  = Q_r_g - Q_d_g

ranked_c4  = np.load(ROOT / "results/phase2/stage2/ranked_class4_gcamp.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))
print(f"GCaMP Class 4 pairs: {N_C4}")

# Load CePNEM ΔQ and its Class 4 for cross-comparison
DQ_cepnem = np.load(ROOT / "results/phase2/stage2/DQ_cepnem.npy")
ranked_c4_cepnem = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4_cep = ii_all[ranked_c4_cepnem]; jj_c4_cep = jj_all[ranked_c4_cepnem]

# ── D1: Identity ──────────────────────────────────────────────────────────────
D1 = np.ones(N)

# ── D2: GCaMP residual variance from sufficient statistics ───────────────────
# Exact procedure from Phase 3C phase3c.py lines 96-111
SUFF = ROOT / "results/phase2/stage1/suff_stats"
n_frames  = np.load(SUFF / "n_frames_gcamp.npy")   # (40, 61, 2)
suf_xi    = np.load(SUFF / "suf_xi_gcamp.npy")     # (40, 61, 2)
suf_xii   = np.load(SUFF / "suf_xii_gcamp.npy")    # (40, 61, 2)

D2_gcamp = np.zeros(N)
for i in range(N):
    T_total = int(n_frames[:, i, :].sum())
    if T_total < 2:
        D2_gcamp[i] = 1.0
        continue
    sum_x  = float(suf_xi[:, i, :].sum())
    sum_xx = float(suf_xii[:, i, :].sum())
    mean_i = sum_x / T_total
    var_i  = sum_xx / T_total - mean_i**2
    D2_gcamp[i] = max(var_i, 1e-6)

print(f"D2_gcamp variance range: [{D2_gcamp.min():.4f}, {D2_gcamp.max():.4f}]  "
      f"mean={D2_gcamp.mean():.4f}  std={D2_gcamp.std():.4f}  "
      f"CV={D2_gcamp.std()/D2_gcamp.mean():.4f}")

# ── D3: First-difference innovation variance from raw GCaMP traces ────────────
# Exact procedure from Phase 3C phase3c.py lines 117-138, adapted for GCaMP
H5_DIR     = ROOT / "data/atanas/AtanasKim-Cell2023"
LABEL_PATH = H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2"

print("Building GCaMP label maps ...")
label_records = decode_atanas_jld2(LABEL_PATH)
label_maps    = build_label_maps(label_records, H5_DIR)
print(f"  {len(label_maps)} recordings mapped.")

sumsq_diff = np.zeros(N)
count_diff = np.zeros(N, dtype=int)

for rec_id in REC_IDS:
    h5_path = H5_DIR / f"{rec_id}-data.h5"
    if not h5_path.exists():
        print(f"  WARNING: {rec_id} not found, skipping.")
        continue
    col_map = label_maps.get(rec_id, {})
    if not col_map:
        continue
    with h5py.File(h5_path, "r") as hf:
        trace_h5 = hf["gcamp/trace_array"][:]   # (T, n_total)
    for lbl, col_idx in col_map.items():
        if lbl not in n2i:
            continue
        idx = n2i[lbl]
        xi  = trace_h5[:, col_idx].astype(float)
        xi  = xi[np.isfinite(xi)]
        if len(xi) < 2:
            continue
        diff = np.diff(xi)
        sumsq_diff[idx] += float(np.nansum(diff**2))
        count_diff[idx] += len(diff)

D3_gcamp = np.where(count_diff > 0, sumsq_diff / count_diff, 1.0)
D3_gcamp = np.maximum(D3_gcamp, 1e-6)
print(f"D3_gcamp (first-diff) range: [{D3_gcamp.min():.4f}, {D3_gcamp.max():.4f}]  "
      f"mean={D3_gcamp.mean():.4f}  std={D3_gcamp.std():.4f}  "
      f"CV={D3_gcamp.std()/D3_gcamp.mean():.4f}")

# Coverage check
n_covered = int((count_diff > 0).sum())
print(f"  Neurons with GCaMP trace data: {n_covered}/61")

# ── Retrieve CePNEM D statistics for comparison ───────────────────────────────
# These are already in omega_models.json
with open(OUT3C / "omega_models.json") as f:
    om = json.load(f)
D2_cepnem = np.array([om["per_neuron_D"][n]["D2_residual_var"] for n in NEURONS])
D3_cepnem = np.array([om["per_neuron_D"][n]["D3_firstdiff_var"] for n in NEURONS])

# ── Top 10 largest / smallest per D ──────────────────────────────────────────
def top10_report(D, name):
    idx_sort = np.argsort(-D)
    print(f"\n{name} — top 10 largest:")
    for rank, i in enumerate(idx_sort[:10]):
        print(f"  {rank+1:2d}. {NEURONS[i]:8s}: {D[i]:.4f}")
    print(f"{name} — top 10 smallest:")
    for rank, i in enumerate(idx_sort[-10:][::-1]):
        print(f"  {rank+1:2d}. {NEURONS[i]:8s}: {D[i]:.4f}")

top10_report(D2_gcamp, "D2_gcamp")
top10_report(D3_gcamp, "D3_gcamp")

# ── Compute ΔΩ = D · ΔQ_gcamp ────────────────────────────────────────────────
def dO(D_vec, DQ):
    return D_vec[:, None] * DQ

dO_D1 = dO(D1,       DQ_g)
dO_D2 = dO(D2_gcamp, DQ_g)
dO_D3 = dO(D3_gcamp, DQ_g)

# Extract Class 4 values
dq_abs_c4  = np.abs(DQ_g[ii_c4, jj_c4])
dO1_abs_c4 = np.abs(dO_D1[ii_c4, jj_c4])
dO2_abs_c4 = np.abs(dO_D2[ii_c4, jj_c4])
dO3_abs_c4 = np.abs(dO_D3[ii_c4, jj_c4])

# Spearman rank correlations
rho_D1, _ = stats.spearmanr(dO1_abs_c4, dq_abs_c4)
rho_D2, _ = stats.spearmanr(dO2_abs_c4, dq_abs_c4)
rho_D3, _ = stats.spearmanr(dO3_abs_c4, dq_abs_c4)
rho_D1_D2, _ = stats.spearmanr(dO1_abs_c4, dO2_abs_c4)
rho_D1_D3, _ = stats.spearmanr(dO1_abs_c4, dO3_abs_c4)
rho_D2_D3, _ = stats.spearmanr(dO2_abs_c4, dO3_abs_c4)

print(f"\nSpearman ρ(|ΔΩ|, |ΔQ|) for GCaMP Class 4 pairs:")
print(f"  D1 vs ΔQ : {rho_D1:.6f}")
print(f"  D2 vs ΔQ : {rho_D2:.6f}")
print(f"  D3 vs ΔQ : {rho_D3:.6f}")
print(f"\nSpearman ρ between ΔΩ variants:")
print(f"  D1 vs D2: {rho_D1_D2:.6f}")
print(f"  D1 vs D3: {rho_D1_D3:.6f}")
print(f"  D2 vs D3: {rho_D2_D3:.6f}")

# ── PDF AUROC ─────────────────────────────────────────────────────────────────
# Load PDF annotation
import csv
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
neurons_set = set(NEURONS)
pdf_c4: set = set()
with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
    reader = csv.reader(f); next(reader)
    seen: set = set()
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        pdf_c4.add((min(a,b), max(a,b)))
pdf_c4 = pdf_c4 & c4_set

pdf_mask = np.array([(min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in pdf_c4
                     for k in range(N_C4)])

def auroc_pdf(scores):
    ps = scores[pdf_mask]; ns = scores[~pdf_mask]
    if len(ps) == 0 or len(ns) == 0: return 0.5
    U, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(U / (len(ps) * len(ns)))

auroc_dq   = auroc_pdf(dq_abs_c4)
auroc_dO1  = auroc_pdf(dO1_abs_c4)
auroc_dO2  = auroc_pdf(dO2_abs_c4)
auroc_dO3  = auroc_pdf(dO3_abs_c4)
print(f"\nPDF AUROC (GCaMP Class 4):")
print(f"  ΔQ:       {auroc_dq:.4f}")
print(f"  ΔΩ_D1:    {auroc_dO1:.4f}")
print(f"  ΔΩ_D2:    {auroc_dO2:.4f}")
print(f"  ΔΩ_D3:    {auroc_dO3:.4f}")
print(f"  n_pdf_c4: {pdf_mask.sum()}")

# ── Top-20 ΔΩ_D2 rankings ────────────────────────────────────────────────────
rank_dO2 = np.argsort(-dO2_abs_c4)
rank_dq  = np.argsort(-dq_abs_c4)

ADEL = n2i["ADEL"]
print("\nTop-20 GCaMP ΔΩ_D2 Class 4 pairs:")
for pos, k in enumerate(rank_dO2[:20]):
    i, j = ii_c4[k], jj_c4[k]
    is_pdf  = (min(i,j),max(i,j)) in pdf_c4
    is_adel = (i == ADEL or j == ADEL)
    print(f"  {pos+1:2d}. {NEURONS[i]:6s}–{NEURONS[j]:6s}: "
          f"ΔΩ_D2={dO_D2[i,j]:+.4f}  ΔQ={DQ_g[i,j]:+.4f}  "
          f"{'PDF' if is_pdf else '   '}  {'ADEL' if is_adel else ''}")

# Top-20 ΔΩ_D2 overlap vs top-20 ΔQ
top20_dO2 = set(rank_dO2[:20])
top20_dq  = set(rank_dq[:20])
overlap = len(top20_dO2 & top20_dq)
print(f"\nTop-20 ΔΩ_D2 vs top-20 ΔQ overlap: {overlap}/20")

# Pairs in top-200 ΔΩ_D2 but not top-200 ΔQ
absent = set(np.argsort(-dO2_abs_c4)[:200]) - set(np.argsort(-dq_abs_c4)[:200])
print(f"Pairs in top-200 ΔΩ_D2 but not top-200 ΔQ: {len(absent)}")

# ── ADEL ranks ────────────────────────────────────────────────────────────────
rank_dq_pos = np.empty(N_C4, dtype=int)
rank_dq_pos[rank_dq] = np.arange(1, N_C4+1)
rank_dO2_pos = np.empty(N_C4, dtype=int)
rank_dO2_pos[rank_dO2] = np.arange(1, N_C4+1)

adel_pairs = [(k, ii_c4[k], jj_c4[k]) for k in range(N_C4)
              if ii_c4[k] == ADEL or jj_c4[k] == ADEL]
print("\nADEL GCaMP Class 4 pairs — ΔQ rank vs ΔΩ_D2 rank:")
for k, i, j in sorted(adel_pairs, key=lambda x: rank_dq_pos[x[0]]):
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    print(f"  {NEURONS[i]:6s}–{NEURONS[j]:6s}: ΔQ rank={rank_dq_pos[k]:4d}  "
          f"ΔΩ_D2 rank={rank_dO2_pos[k]:4d}  "
          f"Δrank={rank_dO2_pos[k]-rank_dq_pos[k]:+d}  "
          f"{'PDF' if is_pdf else ''}")

# ── Per-neuron D comparison: CePNEM vs GCaMP ──────────────────────────────────
print("\n\nPer-neuron D comparison: CePNEM vs GCaMP")
print(f"{'Neuron':8s}  {'D2_CEP':>9s}  {'D2_GCAMP':>9s}  {'ratio_D2':>9s}  "
      f"{'D3_CEP':>9s}  {'D3_GCAMP':>9s}  {'ratio_D3':>9s}")
for i, n in enumerate(NEURONS):
    r2 = D2_gcamp[i] / D2_cepnem[i] if D2_cepnem[i] > 0 else float('nan')
    r3 = D3_gcamp[i] / D3_cepnem[i] if D3_cepnem[i] > 0 else float('nan')
    print(f"{n:8s}  {D2_cepnem[i]:9.4f}  {D2_gcamp[i]:9.4f}  {r2:9.3f}  "
          f"{D3_cepnem[i]:9.4f}  {D3_gcamp[i]:9.4f}  {r3:9.3f}")

# ── Summary statistics ─────────────────────────────────────────────────────────
print("\n\n=== SUMMARY ===")
def stats_summary(D, name):
    cv = D.std() / D.mean()
    idx = np.argsort(-D)
    top10 = [(NEURONS[i], float(D[i])) for i in idx[:10]]
    bot10 = [(NEURONS[i], float(D[i])) for i in idx[-10:]]
    return {
        "name": name,
        "min": float(D.min()),
        "max": float(D.max()),
        "mean": float(D.mean()),
        "std": float(D.std()),
        "cv": float(cv),
        "top10_largest": top10,
        "top10_smallest": bot10,
    }

cepnem_d2_stats = stats_summary(D2_cepnem, "CePNEM_D2")
cepnem_d3_stats = stats_summary(D3_cepnem, "CePNEM_D3")
gcamp_d2_stats  = stats_summary(D2_gcamp,  "GCaMP_D2")
gcamp_d3_stats  = stats_summary(D3_gcamp,  "GCaMP_D3")

for s in [cepnem_d2_stats, gcamp_d2_stats, cepnem_d3_stats, gcamp_d3_stats]:
    print(f"\n{s['name']}:")
    print(f"  range=[{s['min']:.4f}, {s['max']:.4f}]  mean={s['mean']:.4f}  "
          f"std={s['std']:.4f}  CV={s['cv']:.4f}")

# Save JSON summary
result = {
    "date": "2026-06-03",
    "authorization": "Phase 3C supplement",
    "gcamp_D2": {
        "range": [float(D2_gcamp.min()), float(D2_gcamp.max())],
        "mean": float(D2_gcamp.mean()),
        "std": float(D2_gcamp.std()),
        "cv": float(D2_gcamp.std() / D2_gcamp.mean()),
        "per_neuron": {NEURONS[i]: float(D2_gcamp[i]) for i in range(N)},
        "top10_largest":  [(NEURONS[i], float(D2_gcamp[i]))
                           for i in np.argsort(-D2_gcamp)[:10]],
        "top10_smallest": [(NEURONS[i], float(D2_gcamp[i]))
                           for i in np.argsort(D2_gcamp)[:10]],
    },
    "gcamp_D3": {
        "range": [float(D3_gcamp.min()), float(D3_gcamp.max())],
        "mean": float(D3_gcamp.mean()),
        "std": float(D3_gcamp.std()),
        "cv": float(D3_gcamp.std() / D3_gcamp.mean()),
        "per_neuron": {NEURONS[i]: float(D3_gcamp[i]) for i in range(N)},
        "top10_largest":  [(NEURONS[i], float(D3_gcamp[i]))
                           for i in np.argsort(-D3_gcamp)[:10]],
        "top10_smallest": [(NEURONS[i], float(D3_gcamp[i]))
                           for i in np.argsort(D3_gcamp)[:10]],
    },
    "ranking_comparison": {
        "rho_D1_vs_DQ": float(rho_D1),
        "rho_D2_vs_DQ": float(rho_D2),
        "rho_D3_vs_DQ": float(rho_D3),
        "rho_D1_vs_D2": float(rho_D1_D2),
        "rho_D1_vs_D3": float(rho_D1_D3),
        "rho_D2_vs_D3": float(rho_D2_D3),
    },
    "pdf_auroc": {
        "DQ": float(auroc_dq),
        "DO_D1": float(auroc_dO1),
        "DO_D2": float(auroc_dO2),
        "DO_D3": float(auroc_dO3),
        "n_pdf_c4": int(pdf_mask.sum()),
    },
    "top20_overlap_dO2_vs_dQ": overlap,
    "absent_top200_dO2_not_dQ": len(absent),
}

import json as json_mod
with open(OUT3C / "gcamp_d_characterization.json", "w") as f:
    json_mod.dump(result, f, indent=2)
print("\nSaved: gcamp_d_characterization.json")
