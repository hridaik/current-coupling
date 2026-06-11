"""Phase 3C — Current Organization Analysis.

Authorization: Phase 3C, 2026-06-03.

Central identity: Q = D^{-1}(Ω - A)
  → Ω = D Q + A
  → ΔΩ = Ω_roam - Ω_dwell = D (Q_roam - Q_dwell) = D ΔQ

3C-A: Ω robustness under D1/D2/D3 and A_raw/A_Creamer
3C-B: ΔΩ vs ΔQ comparison — does Ω add information?
3C-C: Blockwise current attribution (Leech-style)
3C-D: Sensitivity to D and A choices

PROHIBITIONS: No held-out evaluation. No new α fitting. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys, warnings
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
from scipy import linalg, stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

OUT3C = ROOT / "results/phase3c"
OUT3C.mkdir(parents=True, exist_ok=True)

# ── Load neuron metadata ──────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)

# ── Load Phase 2 precision matrices (confirmation only) ───────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r + Q_r.T) / 2
Q_d = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d + Q_d.T) / 2
DQ  = Q_r - Q_d    # Phase 2 ΔQ (state-dependent conditional dependence change)

# GCaMP for robustness
Q_r_g = np.load(PREC_DIR / "Q_gcamp_roam_conf.npy");  Q_r_g = (Q_r_g + Q_r_g.T) / 2
Q_d_g = np.load(PREC_DIR / "Q_gcamp_dwell_conf.npy"); Q_d_g = (Q_d_g + Q_d_g.T) / 2
DQ_g  = Q_r_g - Q_d_g

# ── Load A matrices ───────────────────────────────────────────────────────────
# Reconstruct A_raw from Phase 2 authoritative Class 4 set
ranked_c4  = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ranked_off = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
ii_off = ii_all[ranked_off]; jj_off = jj_all[ranked_off]
N_C4 = len(ranked_c4)

all_pairs   = set(zip(map(int, ii_all), map(int, jj_all)))
off_set     = set(zip(map(int, ii_off), map(int, jj_off)))
on_set      = all_pairs - off_set
A_raw       = np.zeros((N, N), dtype=float)
for (a, b) in on_set:
    A_raw[a, b] = 1.0; A_raw[b, a] = 1.0

# ── Load Creamer A_C ──────────────────────────────────────────────────────────
CREAMER_DIR = ROOT / "data/creamer/Creamer_LDS_2026"
A_creamer   = None
try:
    for mod_name in ["mpi4py", "mpi4py.MPI", "mpi4py.util", "mpi4py.util.pkl5"]:
        sys.modules[mod_name] = MagicMock()
    sys.path.insert(0, str(CREAMER_DIR))
    import ssm_classes  # type: ignore
    import pickle
    with open(CREAMER_DIR / "models/fully_connected.pkl", "rb") as f:
        cr = pickle.load(f)
    cr_ids    = [str(c) for c in cr.cell_ids]
    cr_in_61  = [c for c in cr_ids if c in n2i]
    cr_idx_cr = [cr_ids.index(c) for c in cr_in_61]
    cr_idx_61 = [n2i[c] for c in cr_in_61]
    A_C_sub   = cr.dynamics_weights[np.ix_(cr_idx_cr, cr_idx_cr)]
    A_creamer = np.zeros((N, N), dtype=float)
    for ki, i61 in enumerate(cr_idx_61):
        for kj, j61 in enumerate(cr_idx_61):
            A_creamer[i61, j61] = A_C_sub[ki, kj]
    print("Creamer A_C loaded.")
except Exception as e:
    print(f"Creamer A_C unavailable: {e}")

# ── Compute D matrices ────────────────────────────────────────────────────────
# D1: identity
D1 = np.ones(N)

# D2: per-neuron residual variance from CePNEM sufficient statistics
# var_i = E[x_i^2] - E[x_i]^2 pooled across all recordings and states
SUFF = ROOT / "results/phase2/stage1/suff_stats"
n_frames  = np.load(SUFF / "n_frames_cepnem.npy")   # (40, 61, 2)
suf_xi    = np.load(SUFF / "suf_xi_cepnem.npy")     # (40, 61, 2)
suf_xii   = np.load(SUFF / "suf_xii_cepnem.npy")    # (40, 61, 2)

D2 = np.zeros(N)
for i in range(N):
    # Pool across all recordings and both states
    T_total = int(n_frames[:, i, :].sum())
    if T_total < 2:
        D2[i] = 1.0
        continue
    sum_x   = float(suf_xi[:, i, :].sum())
    sum_xx  = float(suf_xii[:, i, :].sum())
    mean_i  = sum_x / T_total
    var_i   = sum_xx / T_total - mean_i**2
    D2[i]   = max(var_i, 1e-6)  # clip to avoid zero

print(f"D2 variance range: [{D2.min():.4f}, {D2.max():.4f}]  "
      f"mean={D2.mean():.4f}  std={D2.std():.4f}")

# D3: high-frequency innovation variance (first-difference variance of CePNEM residuals)
# Load actual residuals and compute Var(Δx_i) per neuron
RESID_DIR = ROOT / "results/phase1/data/cepnem_residuals"
sumsq_diff = np.zeros(N)
count_diff = np.zeros(N, dtype=int)

for rec_npz in sorted(RESID_DIR.glob("*.npz")):
    npz = np.load(rec_npz)
    resid   = npz["residual"]    # (T, n_rec)
    sub_lbl = list(npz["neuron_labels"])
    for j, lbl in enumerate(sub_lbl):
        if lbl in n2i:
            idx  = n2i[lbl]
            xi   = resid[:, j].astype(float)
            xi   = xi[np.isfinite(xi)]   # remove NaN/Inf
            if len(xi) < 2: continue
            diff = np.diff(xi)
            sumsq_diff[idx] += float(np.nansum(diff**2))
            count_diff[idx] += len(diff)

D3 = np.where(count_diff > 0, sumsq_diff / count_diff, 1.0)
D3 = np.maximum(D3, 1e-6)
print(f"D3 (first-diff) range: [{D3.min():.4f}, {D3.max():.4f}]  mean={D3.mean():.4f}")

# ── Compute Ω for each (D, A) combination ────────────────────────────────────
# Ω = D Q + A  (row-scaling by diagonal D, then add A)
# For diagonal D: (DQ)_ij = D_ii * Q_ij  (left-multiply)
# ΔΩ = D ΔQ  (A cancels)

def compute_omega(Q: np.ndarray, D_vec: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Ω = diag(D) @ Q + A"""
    return D_vec[:, None] * Q + A

def compute_deltaOmega(DQ: np.ndarray, D_vec: np.ndarray) -> np.ndarray:
    """ΔΩ = diag(D) @ ΔQ"""
    return D_vec[:, None] * DQ

# All combinations
omega_configs = {
    "D1_Araw":     (D1, A_raw),
    "D2_Araw":     (D2, A_raw),
    "D3_Araw":     (D3, A_raw),
}
if A_creamer is not None:
    omega_configs["D1_Acreamer"] = (D1, A_creamer)
    omega_configs["D2_Acreamer"] = (D2, A_creamer)

Omega_roam  = {}  # config → Ω_roam
Omega_dwell = {}  # config → Ω_dwell
DeltaOmega  = {}  # config → ΔΩ

for cfg, (D_vec, A_mat) in omega_configs.items():
    Omega_roam[cfg]  = compute_omega(Q_r, D_vec, A_mat)
    Omega_dwell[cfg] = compute_omega(Q_d, D_vec, A_mat)
    DeltaOmega[cfg]  = compute_deltaOmega(DQ, D_vec)

print(f"Computed Ω for {len(omega_configs)} (D, A) configurations.")

# ── Load PDF annotation ───────────────────────────────────────────────────────
DATA_DIR  = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
c4_set    = set(zip(map(int, ii_c4), map(int, jj_c4)))

pdf_c4: set = set()
pdf_edges: list[tuple[int,int]] = []
with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
    reader = csv.reader(f); next(reader)
    seen: set = set()
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        if (a, b) not in seen:
            seen.add((a, b))
            pdf_edges.append((a, b))
        pdf_c4.add((min(a, b), max(a, b)))

pdf_c4 = pdf_c4 & c4_set

# ADEL-related indices
ADEL = n2i["ADEL"]
adel_pairs_c4 = [(k, ii_c4[k], jj_c4[k]) for k in range(N_C4)
                 if ii_c4[k] == ADEL or jj_c4[k] == ADEL]

print(f"PDF Class 4 pairs: {len(pdf_c4)}")
print(f"ADEL Class 4 pairs: {len(adel_pairs_c4)}")

# =============================================================================
# 3C-A: Ω ROBUSTNESS TO D
# =============================================================================
print("\n" + "="*70)
print("3C-A — Ω Robustness to D")
print("="*70)

# For each config, rank Class 4 pairs by |ΔΩ|
# Compare rankings across D models

DQ_abs_c4 = np.abs(DQ[ii_c4, jj_c4])
rank_DQ    = np.argsort(-DQ_abs_c4)

rankings = {}  # cfg → rank array for ΔΩ on Class 4 pairs
for cfg, dO in DeltaOmega.items():
    dO_abs_c4 = np.abs(dO[ii_c4, jj_c4])
    rankings[cfg] = np.argsort(-dO_abs_c4)

# Spearman between D1_Araw (reference) and others
ref_key = "D1_Araw"
ref_abs  = np.abs(DeltaOmega[ref_key][ii_c4, jj_c4])
print(f"\nSpearman ρ between {ref_key} and others:")
for cfg, dO in DeltaOmega.items():
    if cfg == ref_key: continue
    rho, _ = stats.spearmanr(ref_abs, np.abs(dO[ii_c4, jj_c4]))
    print(f"  {cfg}: ρ={rho:.4f}")

# Top-20 overlap between D choices
print("\nTop-20 overlap with D1_Araw:")
ref_top20 = set(rank_DQ[:20])   # NB: rank_DQ is the ΔQ ranking not ΔΩ D1
ref_dO_top20 = set(rankings[ref_key][:20])
for cfg in rankings:
    if cfg == ref_key: continue
    ov = len(ref_dO_top20 & set(rankings[cfg][:20]))
    print(f"  {cfg}: {ov}/20 overlap with D1_Araw top-20")

# Robust Ω entries: in top-100 for ALL D_Araw variants
robust_candidates = set(range(N_C4))
for cfg in ["D1_Araw", "D2_Araw", "D3_Araw"]:
    if cfg in rankings:
        robust_candidates &= set(rankings[cfg][:100])
print(f"\nRobust entries (top-100 in ALL D_Araw variants): {len(robust_candidates)}")

# Robust top-20: in top-20 for all D variants (more stringent)
robust_top20 = set(range(N_C4))
for cfg in ["D1_Araw", "D2_Araw", "D3_Araw"]:
    if cfg in rankings:
        robust_top20 &= set(rankings[cfg][:20])
print(f"Robust top-20 (top-20 in ALL D_Araw variants): {len(robust_top20)}")
if robust_top20:
    for k in sorted(robust_top20):
        ni, nj = NEURONS[ii_c4[k]], NEURONS[jj_c4[k]]
        dO_vals = {cfg: float(DeltaOmega[cfg][ii_c4[k], jj_c4[k]])
                   for cfg in ["D1_Araw", "D2_Araw", "D3_Araw"] if cfg in DeltaOmega}
        in_pdf = (min(ii_c4[k],jj_c4[k]), max(ii_c4[k],jj_c4[k])) in pdf_c4
        print(f"  {ni}–{nj}: D1={dO_vals.get('D1_Araw',0):.4f}  "
              f"D2={dO_vals.get('D2_Araw',0):.4f}  D3={dO_vals.get('D3_Araw',0):.4f}  "
              f"PDF={in_pdf}")

# Save Ω matrices
np.save(OUT3C / "omega_roam_D1_Araw.npy",  Omega_roam["D1_Araw"])
np.save(OUT3C / "omega_dwell_D1_Araw.npy", Omega_dwell["D1_Araw"])
np.save(OUT3C / "omega_roam_D2_Araw.npy",  Omega_roam["D2_Araw"])
np.save(OUT3C / "omega_dwell_D2_Araw.npy", Omega_dwell["D2_Araw"])
np.save(OUT3C / "deltaomega_D1_Araw.npy",  DeltaOmega["D1_Araw"])
np.save(OUT3C / "deltaomega_D2_Araw.npy",  DeltaOmega["D2_Araw"])
np.save(OUT3C / "deltaomega_D3_Araw.npy",  DeltaOmega["D3_Araw"])

# =============================================================================
# 3C-B: ΔΩ vs ΔQ COMPARISON
# =============================================================================
print("\n" + "="*70)
print("3C-B — ΔΩ vs ΔQ Comparison")
print("="*70)

# Primary: D1_Araw ΔΩ (= ΔQ since D=I and A cancels in difference)
# D2 gives the most distinct comparison
dO_D2_c4 = np.abs(DeltaOmega["D2_Araw"][ii_c4, jj_c4])
dO_D3_c4 = np.abs(DeltaOmega["D3_Araw"][ii_c4, jj_c4])
dq_c4    = np.abs(DQ[ii_c4, jj_c4])

rho_D2_DQ, _ = stats.spearmanr(dO_D2_c4, dq_c4)
rho_D3_DQ, _ = stats.spearmanr(dO_D3_c4, dq_c4)
print(f"\nSpearman ΔΩ_D2 vs ΔQ: ρ={rho_D2_DQ:.4f}")
print(f"Spearman ΔΩ_D3 vs ΔQ: ρ={rho_D3_DQ:.4f}")

# Question 1: Do PDF pairs remain exceptional in ΔΩ?
pdf_mask_c4 = np.array([(min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in pdf_c4
                         for k in range(N_C4)])

def auroc_pdf(scores: np.ndarray) -> float:
    ps = scores[pdf_mask_c4]; ns = scores[~pdf_mask_c4]
    if len(ps) == 0 or len(ns) == 0: return 0.5
    U, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(U / (len(ps) * len(ns)))

print(f"\nPDF AUROC in ΔQ:       {auroc_pdf(dq_c4):.4f}")
for cfg in ["D1_Araw", "D2_Araw", "D3_Araw"]:
    if cfg in DeltaOmega:
        dO_abs = np.abs(DeltaOmega[cfg][ii_c4, jj_c4])
        print(f"PDF AUROC in ΔΩ_{cfg}: {auroc_pdf(dO_abs):.4f}")

# Question 2: ADEL pairs — rank in ΔΩ vs ΔQ
rank_DQ_arr = np.argsort(-dq_c4)  # position → index in C4
rank_DQ_pos = np.empty(N_C4, dtype=int)
rank_DQ_pos[rank_DQ_arr] = np.arange(1, N_C4+1)  # index → rank

rank_DO_D2_arr = np.argsort(-dO_D2_c4)
rank_DO_D2_pos = np.empty(N_C4, dtype=int)
rank_DO_D2_pos[rank_DO_D2_arr] = np.arange(1, N_C4+1)

print("\nADEL Class 4 pairs — ΔQ rank vs ΔΩ_D2 rank:")
for k, i, j in sorted(adel_pairs_c4, key=lambda x: rank_DQ_pos[x[0]]):
    ni, nj = NEURONS[i], NEURONS[j]
    r_DQ = rank_DQ_pos[k]
    r_DO = rank_DO_D2_pos[k]
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    print(f"  {ni}–{nj}: ΔQ rank={r_DQ:4d}  ΔΩ_D2 rank={r_DO:4d}  "
          f"Δrank={r_DO-r_DQ:+d}  {'PDF' if is_pdf else ''}")

# Question 3: Strong ΔΩ entries absent from ΔQ top-200
top200_DQ = set(rank_DQ_arr[:200])
top200_DO = set(rank_DO_D2_arr[:200])
absent_from_DQ = top200_DO - top200_DQ
print(f"\nStrong ΔΩ_D2 pairs (top-200) absent from ΔQ top-200: {len(absent_from_DQ)}")
print("Top-10 by ΔΩ_D2 among those absent from ΔQ top-200:")
absent_sorted = sorted(absent_from_DQ, key=lambda k: -dO_D2_c4[k])
for k in absent_sorted[:10]:
    i, j = ii_c4[k], jj_c4[k]
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    print(f"  {NEURONS[i]}–{NEURONS[j]}: ΔΩ_D2={DeltaOmega['D2_Araw'][i,j]:.4f}  "
          f"ΔQ={DQ[i,j]:.4f}  PDF={is_pdf}")

# Top-20 ΔΩ_D2 Class 4 pairs
print("\nTop-20 ΔΩ_D2 Class 4 pairs:")
for pos, k in enumerate(rank_DO_D2_arr[:20]):
    i, j = ii_c4[k], jj_c4[k]
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    adel_flag = "ADEL" if (i == ADEL or j == ADEL) else ""
    print(f"  {pos+1:3d}. {NEURONS[i]}–{NEURONS[j]}: ΔΩ_D2={DeltaOmega['D2_Araw'][i,j]:.4f}  "
          f"ΔQ={DQ[i,j]:.4f}  {'PDF' if is_pdf else ''}  {adel_flag}")

# =============================================================================
# 3C-C: BLOCKWISE CURRENT ATTRIBUTION
# =============================================================================
print("\n" + "="*70)
print("3C-C — Blockwise Current Attribution")
print("="*70)

# Define neuron blocks
BLOCKS = {
    "DA_mech":    [n2i[n] for n in ["ADEL", "CEPDL", "CEPDR", "CEPVL"]],
    "RID":        [n2i["RID"]],
    "RME":        [n2i["RMEL"], n2i["RMER"]],
    "URY_URX":    [n2i[n] for n in ["URYDL", "URYVL", "URYVR", "URXL"]],
    "command_IN": [n2i[n] for n in ["AVAL", "AVAR", "AVEL", "AVER",
                                     "AVDL", "AVJL", "AVJR"]],
    "OLL_OLQ":    [n2i[n] for n in ["OLLL", "OLLR", "OLQDL", "OLQDR",
                                     "OLQVL", "OLQVR"]],
    "IL1_IL2":    [n2i[n] for n in ["IL1DR", "IL1L", "IL1R",
                                     "IL2DL", "IL2DR", "IL2VL", "IL2VR"]],
    "pharyngeal": [n2i[n] for n in ["I1L", "I1R", "I2L", "I2R", "I3",
                                     "M1", "M3L", "M3R", "M4", "MI",
                                     "NSML", "NSMR"]],
    "RMD_SMD":    [n2i[n] for n in ["RMDDR", "RMDL", "RMDVL", "RMDVR", "SMDVL"]],
    "other":      [n2i[n] for n in ["AIBL", "AIBR", "AIZL", "ASEL", "ASGL",
                                     "AUAL", "AWAL", "AWBL", "AWCL", "FLPL",
                                     "RICL", "RIVL", "URBL"]],
}

# Verify coverage
assigned = set()
for block, idxs in BLOCKS.items():
    assigned |= set(idxs)
print(f"Block coverage: {len(assigned)}/61 neurons assigned")
if len(assigned) < 61:
    unassigned = [NEURONS[i] for i in range(N) if i not in assigned]
    print(f"  Unassigned: {unassigned}")

block_names = list(BLOCKS.keys())
n_blocks = len(block_names)
B = n_blocks

# Inter-block ΔΩ flow (using D2_Araw as primary)
dO_D2 = DeltaOmega["D2_Araw"]  # (61, 61)

# Flow matrix: flow[b1, b2] = mean |ΔΩ| for all pairs (i∈B1, j∈B2), i<j
flow_mean = np.zeros((B, B))
flow_sum  = np.zeros((B, B))
flow_npairs = np.zeros((B, B), dtype=int)

for b1 in range(B):
    for b2 in range(b1, B):
        idxs1 = BLOCKS[block_names[b1]]
        idxs2 = BLOCKS[block_names[b2]]
        vals  = []
        for i in idxs1:
            for j in idxs2:
                if i == j: continue
                if b1 == b2 and j <= i: continue  # upper triangle within block
                # Check if this is a Class 4 pair (both in Creamer)
                key = (min(i,j), max(i,j))
                if key in c4_set:
                    vals.append(dO_D2[i, j])
        if vals:
            flow_mean[b1, b2] = float(np.mean(np.abs(vals)))
            flow_sum[b1, b2]  = float(np.sum(np.abs(vals)))
            flow_npairs[b1, b2] = len(vals)
            flow_mean[b2, b1] = flow_mean[b1, b2]
            flow_sum[b2, b1]  = flow_sum[b1, b2]
            flow_npairs[b2, b1] = flow_npairs[b1, b2]

# Also compute for ΔQ
dq_mat = DQ
flow_DQ_mean = np.zeros((B, B))
for b1 in range(B):
    for b2 in range(b1, B):
        idxs1 = BLOCKS[block_names[b1]]
        idxs2 = BLOCKS[block_names[b2]]
        vals = []
        for i in idxs1:
            for j in idxs2:
                if i == j: continue
                if b1 == b2 and j <= i: continue
                key = (min(i,j), max(i,j))
                if key in c4_set:
                    vals.append(dq_mat[i, j])
        if vals:
            flow_DQ_mean[b1, b2] = float(np.mean(np.abs(vals)))
            flow_DQ_mean[b2, b1] = flow_DQ_mean[b1, b2]

# Top block pairs by total |ΔΩ| flow
block_pair_flows = []
for b1 in range(B):
    for b2 in range(b1, B):
        if flow_npairs[b1, b2] > 0:
            block_pair_flows.append({
                "b1": block_names[b1],
                "b2": block_names[b2],
                "mean_abs_dO": float(flow_mean[b1, b2]),
                "sum_abs_dO": float(flow_sum[b1, b2]),
                "n_c4_pairs": int(flow_npairs[b1, b2]),
                "mean_abs_dq": float(flow_DQ_mean[b1, b2]),
            })
block_pair_flows.sort(key=lambda x: -x["mean_abs_dO"])

print("\nTop 15 block pairs by mean |ΔΩ_D2| flow (Class 4 pairs only):")
for row in block_pair_flows[:15]:
    print(f"  {row['b1']:12s}↔{row['b2']:12s}: "
          f"mean_dO={row['mean_abs_dO']:.4f}  mean_dq={row['mean_abs_dq']:.4f}  "
          f"n={row['n_c4_pairs']}")

# ADEL participation
print("\nADEL (DA_mech) block flows:")
for row in block_pair_flows:
    if "DA_mech" in (row["b1"], row["b2"]):
        print(f"  DA_mech↔{row['b2'] if row['b1']=='DA_mech' else row['b1']}: "
              f"mean_dO={row['mean_abs_dO']:.4f}  mean_dq={row['mean_abs_dq']:.4f}  "
              f"n={row['n_c4_pairs']}")

# PDF-attributed flow per block pair
pdf_flow = {}
for b1 in range(B):
    for b2 in range(b1, B):
        idxs1 = BLOCKS[block_names[b1]]
        idxs2 = BLOCKS[block_names[b2]]
        pdf_vals = []
        for i in idxs1:
            for j in idxs2:
                if i == j: continue
                if b1 == b2 and j <= i: continue
                key = (min(i,j), max(i,j))
                if key in pdf_c4:
                    pdf_vals.append(dO_D2[i, j])
        if pdf_vals:
            pdf_flow[(block_names[b1], block_names[b2])] = {
                "mean_abs": float(np.mean(np.abs(pdf_vals))),
                "n_pairs": len(pdf_vals)
            }

print("\nPDF-attributed block flows:")
for (b1, b2), stats_val in sorted(pdf_flow.items(), key=lambda x: -x[1]["mean_abs"]):
    print(f"  {b1:12s}↔{b2:12s}: mean_dO={stats_val['mean_abs']:.4f}  n_PDF={stats_val['n_pairs']}")

np.save(OUT3C / "block_flow_deltaomega.npy", flow_mean)
np.save(OUT3C / "block_flow_deltaq.npy", flow_DQ_mean)

# =============================================================================
# 3C-D: SENSITIVITY TO D AND A CHOICES
# =============================================================================
print("\n" + "="*70)
print("3C-D — Sensitivity to D and A Choices")
print("="*70)

# Stability: Spearman rank correlation of |ΔΩ| Class 4 rankings across configs
configs = list(DeltaOmega.keys())
print("\nSpearman rank correlation of |ΔΩ| Class 4 rankings:")
for i, ci in enumerate(configs):
    for j, cj in enumerate(configs):
        if j <= i: continue
        dOi = np.abs(DeltaOmega[ci][ii_c4, jj_c4])
        dOj = np.abs(DeltaOmega[cj][ii_c4, jj_c4])
        rho, _ = stats.spearmanr(dOi, dOj)
        print(f"  {ci} vs {cj}: ρ={rho:.4f}")

# Key conclusion: are top-pairs stable across D choices?
print("\nTop-20 pair stability across D choices:")
all_top20s = {}
for cfg in ["D1_Araw", "D2_Araw", "D3_Araw"]:
    if cfg in DeltaOmega:
        dO_abs = np.abs(DeltaOmega[cfg][ii_c4, jj_c4])
        all_top20s[cfg] = set(np.argsort(-dO_abs)[:20])

if len(all_top20s) == 3:
    intersection_3 = set.intersection(*all_top20s.values())
    print(f"  Pairs in top-20 for ALL D_Araw variants: {len(intersection_3)}")
    for k in sorted(intersection_3, key=lambda k: -np.abs(DeltaOmega['D2_Araw'][ii_c4[k],jj_c4[k]])):
        i, j = ii_c4[k], jj_c4[k]
        print(f"    {NEURONS[i]}–{NEURONS[j]}: "
              f"D1={DeltaOmega['D1_Araw'][i,j]:.4f}  "
              f"D2={DeltaOmega['D2_Araw'][i,j]:.4f}  "
              f"D3={DeltaOmega['D3_Araw'][i,j]:.4f}")

# =============================================================================
# SAVE JSON SUMMARY
# =============================================================================
# Per-neuron D values
d_vals = {}
for i, name in enumerate(NEURONS):
    d_vals[name] = {
        "D1": float(D1[i]),
        "D2_residual_var": float(D2[i]),
        "D3_firstdiff_var": float(D3[i]),
    }

# Top-20 ΔΩ_D2 Class 4 pairs
top20_dO = []
for pos, k in enumerate(rank_DO_D2_arr[:20]):
    i, j = ii_c4[k], jj_c4[k]
    top20_dO.append({
        "rank": pos + 1,
        "pair": f"{NEURONS[i]}–{NEURONS[j]}",
        "deltaOmega_D2": float(DeltaOmega["D2_Araw"][i, j]),
        "deltaQ": float(DQ[i, j]),
        "pdf_annotated": (min(i,j),max(i,j)) in pdf_c4,
        "adel_involved": (i == ADEL or j == ADEL),
    })

# Robust entries (top-100 all D variants)
robust_entries = []
for k in sorted(robust_candidates,
                key=lambda k: -np.abs(DeltaOmega["D2_Araw"][ii_c4[k], jj_c4[k]])):
    i, j = ii_c4[k], jj_c4[k]
    robust_entries.append({
        "pair": f"{NEURONS[i]}–{NEURONS[j]}",
        "deltaOmega_D1": float(DeltaOmega["D1_Araw"][i, j]),
        "deltaOmega_D2": float(DeltaOmega["D2_Araw"][i, j]),
        "deltaOmega_D3": float(DeltaOmega["D3_Araw"][i, j]) if "D3_Araw" in DeltaOmega else None,
        "deltaQ": float(DQ[i, j]),
        "pdf_annotated": (min(i,j),max(i,j)) in pdf_c4,
    })

output = {
    "date": "2026-06-03",
    "authorization": "Phase 3C",
    "identity": "Q = D^{-1}(Omega - A) --> Omega = D Q + A,  DeltaOmega = D DeltaQ",
    "D_statistics": {
        "D1": "identity (D_ii = 1.0)",
        "D2_range": [float(D2.min()), float(D2.max())],
        "D2_mean": float(D2.mean()),
        "D3_range": [float(D3.min()), float(D3.max())],
        "D3_mean": float(D3.mean()),
    },
    "per_neuron_D": d_vals,
    "cA_robustness": {
        "n_robust_top100": len(robust_candidates),
        "n_robust_top20_all_D": len(robust_top20),
        "robust_top20_pairs": robust_entries[:20],
    },
    "cB_pdf_auroc": {
        "DQ_auroc":          float(auroc_pdf(dq_c4)),
        "DO_D1_Araw_auroc":  float(auroc_pdf(np.abs(DeltaOmega["D1_Araw"][ii_c4, jj_c4]))),
        "DO_D2_Araw_auroc":  float(auroc_pdf(np.abs(DeltaOmega["D2_Araw"][ii_c4, jj_c4]))),
        "DO_D3_Araw_auroc":  float(auroc_pdf(np.abs(DeltaOmega["D3_Araw"][ii_c4, jj_c4]))),
    },
    "cB_top20_deltaOmega_D2": top20_dO,
    "cC_block_names": block_names,
    "cC_top_block_flows": block_pair_flows[:15],
    "cD_spearman_stability": {
        "D1_vs_D2": float(stats.spearmanr(
            np.abs(DeltaOmega["D1_Araw"][ii_c4, jj_c4]),
            np.abs(DeltaOmega["D2_Araw"][ii_c4, jj_c4]))[0]),
        "D1_vs_D3": float(stats.spearmanr(
            np.abs(DeltaOmega["D1_Araw"][ii_c4, jj_c4]),
            np.abs(DeltaOmega["D3_Araw"][ii_c4, jj_c4]))[0]),
        "D2_vs_D3": float(stats.spearmanr(
            np.abs(DeltaOmega["D2_Araw"][ii_c4, jj_c4]),
            np.abs(DeltaOmega["D3_Araw"][ii_c4, jj_c4]))[0]),
    },
}

def sanitize_for_json(obj):
    """Recursively convert numpy types and NaN/Inf for JSON serialization."""
    if isinstance(obj, (np.floating, np.complexfloating)):
        v = float(obj)
        return None if (v != v or v == float('inf') or v == float('-inf')) else v
    if isinstance(obj, float):
        return None if (obj != obj or obj == float('inf') or obj == float('-inf')) else obj
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return [sanitize_for_json(v) for v in obj.tolist()]
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    return obj

with open(OUT3C / "omega_models.json", "w") as f:
    json.dump(sanitize_for_json(output), f, indent=2)
print("\nSaved: omega_models.json")
print("\n>>> STOP CONDITION — awaiting reports then summary <<<")
