"""Phase 3D — State-Dependent Diffusion and Module-Level Current Analysis.

Authorization: Phase 3D, 2026-06-03.

D1: State-dependent diffusion (D_roam, D_dwell for CePNEM and GCaMP)
D2: Module-level Q and Ω organization

Uses same behavioral segmentation as Phase 2 (EWMA velocity, locked parameters).
State-specific Δx computed from consecutive same-state frames only.

PROHIBITIONS: No model fitting. No held-out evaluation. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
from unittest.mock import MagicMock

import h5py
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.stage06_neff_stationarity import segment, SAMPLING_HZ
from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.phase1.stage0_cepnem import build_label_maps

import phase0_config as p0cfg

OUT3D = ROOT / "results/phase3d"
OUT3D.mkdir(parents=True, exist_ok=True)

# ── Locked segmentation parameters (Phase 2 values) ─────────────────────────
TAU   = p0cfg.EWMA_TIMESCALE_SECONDS   # 20.0 s
THR   = p0cfg.BEHAV_THRESHOLD           # 0.284
W_FR  = int(p0cfg.W_TRANS_SECONDS  * SAMPLING_HZ)  # 50
MB_FR = int(p0cfg.MIN_BOUT_SECONDS * SAMPLING_HZ)  # 50
H5_DIR = ROOT / "data/atanas/AtanasKim-Cell2023"

# ── Metadata ──────────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
REC_IDS = cop["recording_ids"]
N = len(NEURONS)
N_REC = len(REC_IDS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Load Phase 2 precision matrices ───────────────────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r  = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r  = (Q_r  + Q_r.T )/2
Q_d  = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d  = (Q_d  + Q_d.T )/2
DQ   = Q_r - Q_d
Q_rg = np.load(PREC_DIR / "Q_gcamp_roam_conf.npy");   Q_rg = (Q_rg + Q_rg.T)/2
Q_dg = np.load(PREC_DIR / "Q_gcamp_dwell_conf.npy");  Q_dg = (Q_dg + Q_dg.T)/2
DQg  = Q_rg - Q_dg

# ── Class 4 pairs ──────────────────────────────────────────────────────────────
ranked_c4 = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))
ranked_off = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
off_set = set(zip(map(int, ii_all[ranked_off]), map(int, jj_all[ranked_off])))
A_raw = np.zeros((N, N), dtype=bool)
for k in range(len(ii_all)):
    i, j = int(ii_all[k]), int(jj_all[k])
    if (i, j) not in off_set:
        A_raw[i, j] = A_raw[j, i] = True
A_mat = A_raw.astype(float)

# ── Bentley PDF annotation ────────────────────────────────────────────────────
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
PEP_CSV  = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"
pdf_c4: set = set()
with open(PEP_CSV) as f:
    reader = csv.reader(f); next(reader)
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
deg_raw = A_raw.astype(int).sum(axis=1)
pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]

# =============================================================================
# D1: STATE-DEPENDENT DIFFUSION
# =============================================================================
print("="*70); print("D1 — State-Dependent Diffusion Estimation")

def compute_state_diffusion(coord: str) -> dict[str, np.ndarray]:
    """Compute D_roam, D_dwell using vectorized pairwise complete-case Cov(Δx | state).

    Key: NaN-replaced-with-0 outer products give correct pairwise-complete sums:
      dX_clean[t,i] = dX[t,i] if finite else 0
      sum_xy[i,j]  = dX_clean.T @ dX_clean  (only finite pairs contribute)
      sum_x[i,j]   = (dX_clean * valid).T @ valid  (sum of Δx_i where both finite)
      cnt[i,j]     = valid.T @ valid  (count of frames where both finite)
    """
    sum_xy   = [np.zeros((N, N)), np.zeros((N, N))]
    sum_x    = [np.zeros((N, N)), np.zeros((N, N))]  # sum_x[s][i,j] = sum Δx_i where both (i,j) finite
    sum_y    = [np.zeros((N, N)), np.zeros((N, N))]  # sum_y[s][i,j] = sum Δx_j where both finite
    cnt      = [np.zeros((N, N), dtype=np.float64), np.zeros((N, N), dtype=np.float64)]

    if coord == "gcamp":
        recs  = decode_atanas_jld2(H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2")
        lmaps = build_label_maps(recs, H5_DIR)

    RESID_DIR = ROOT / "results/phase1/data/cepnem_residuals"

    for rec_id in REC_IDS:
        h5_path = H5_DIR / f"{rec_id}-data.h5"
        if not h5_path.exists(): continue
        with h5py.File(h5_path, "r") as hf:
            v_raw = hf["behavior/velocity"][:]
            if coord == "gcamp":
                trace_h5 = hf["gcamp/trace_array"][:]

        lbl_arr, _ = segment(v_raw, TAU, THR, W_FR, MB_FR)

        if coord == "cepnem":
            npz_path = RESID_DIR / f"{rec_id}.npz"
            if not npz_path.exists(): continue
            npz = np.load(npz_path)
            resid   = npz["residual"].astype(float)
            sub_lbl = list(npz["neuron_labels"])
            X = np.full((len(v_raw), N), np.nan)
            for j, lbl in enumerate(sub_lbl):
                if lbl in n2i:
                    X[:, n2i[lbl]] = resid[:, j]
        else:
            col_map = lmaps.get(rec_id, {})
            if not col_map: continue
            X = np.full((len(v_raw), N), np.nan)
            for lbl, col_idx in col_map.items():
                if lbl in n2i:
                    X[:, n2i[lbl]] = trace_h5[:, col_idx].astype(float)

        # First differences: (T-1, N); NaN propagates through gaps/absent neurons
        dX = np.diff(X, axis=0)   # (T-1, N)
        lbl_curr = lbl_arr[1:]    # state at frame t (diff is x[t]-x[t-1])
        lbl_prev = lbl_arr[:-1]   # state at frame t-1

        for s in [0, 1]:  # dwell, roam
            # Same-state consecutive frames only
            same_state = (lbl_curr == s) & (lbl_prev == s)
            dX_s = dX[same_state, :]   # (T_s, N)
            if dX_s.shape[0] < 2: continue

            valid = np.isfinite(dX_s).astype(np.float64)   # (T_s, N)
            dX_clean = np.where(np.isfinite(dX_s), dX_s, 0.0)

            # Vectorized accumulation — all O(T_s * N^2) but as BLAS calls
            sum_xy[s]  += dX_clean.T @ dX_clean    # (N,N): Σ_t Δx_i Δx_j (both finite)
            sum_x[s]   += (dX_clean).T @ valid      # (N,N): Σ_t Δx_i * 1[j finite]
            sum_y[s]   += valid.T @ dX_clean         # (N,N): Σ_t 1[i finite] * Δx_j
            cnt[s]     += valid.T @ valid             # (N,N): Σ_t 1[i finite] * 1[j finite]

    result = {}
    for s, sname in [(0, "dwell"), (1, "roam")]:
        D = np.zeros((N, N))
        c = cnt[s]
        ok = c >= 2
        # Cov = E[xy] - E[x]*E[y]  (pairwise complete case)
        with np.errstate(invalid="ignore", divide="ignore"):
            e_xy = np.where(ok, sum_xy[s] / c, 0.0)
            e_x  = np.where(ok, sum_x[s]  / c, 0.0)
            e_y  = np.where(ok, sum_y[s]  / c, 0.0)
        D = np.where(ok, e_xy - e_x * e_y, 0.0)
        D = (D + D.T) / 2   # symmetrize numerical noise
        result[sname] = D
        n_covered = int((np.diag(c) > 0).sum())
        diag = np.diag(D)
        m = diag.mean(); cv = diag.std()/m if m > 0 else 0
        print(f"  {coord} {sname}: diag=[{diag.min():.4f},{diag.max():.4f}] "
              f"mean={m:.4f} std={diag.std():.4f} CV={cv:.4f} "
              f"n_neurons={n_covered}")
    return result

print("\nCePNEM state-specific diffusion:")
cep_state_D = compute_state_diffusion("cepnem")
print("\nGCaMP state-specific diffusion:")
g_state_D = compute_state_diffusion("gcamp")

# Load pooled D_emp from Phase 3C-E
D_pool_cep = np.load(ROOT / "results/phase3c/D_emp_cepnem.npy")
D_pool_g   = np.load(ROOT / "results/phase3c/D_emp_gcamp.npy")

# ── D1.2: ΔD = D_roam - D_dwell ──────────────────────────────────────────────
print("\n" + "="*70); print("D1.2 — ΔD = D_roam - D_dwell")

def delta_D_metrics(D_r, D_d, name):
    dD = D_r - D_d
    diag_dD = np.diag(dD)
    offdiag_vals = dD[ii_all, jj_all]

    frob_dD = float(np.linalg.norm(dD, "fro"))
    frob_D  = float(np.linalg.norm(D_r, "fro"))
    rel_change = frob_dD / frob_D

    # Diagonal CV per state
    cv_r = float(np.diag(D_r).std() / np.diag(D_r).mean())
    cv_d = float(np.diag(D_d).std() / np.diag(D_d).mean())

    # Eigenvalue change
    ev_r = np.linalg.eigvalsh((D_r + D_r.T)/2)
    ev_d = np.linalg.eigvalsh((D_d + D_d.T)/2)

    # Spearman rank correlation of absolute diagonals
    rho_diag, _ = stats.spearmanr(np.abs(np.diag(D_r)), np.abs(np.diag(D_d)))

    # Spearman of full |ΔD| vs non-state Class 4 |ΔQ|
    dD_c4 = np.abs(dD[ii_c4, jj_c4])
    dq_c4_abs = np.abs(DQ[ii_c4, jj_c4])
    rho_dD_dQ, _ = stats.spearmanr(dD_c4, dq_c4_abs)

    print(f"\n  {name}:")
    print(f"    ||ΔD||_F = {frob_dD:.4f}  (relative to ||D_roam||: {rel_change:.4f})")
    print(f"    Diagonal: mean_roam={np.diag(D_r).mean():.4f}  mean_dwell={np.diag(D_d).mean():.4f}")
    print(f"    Diagonal CV: roam={cv_r:.4f}  dwell={cv_d:.4f}")
    print(f"    Diag Δ range: [{diag_dD.min():.4f}, {diag_dD.max():.4f}]")
    print(f"    Off-diag Δ range: [{offdiag_vals.min():.4f}, {offdiag_vals.max():.4f}]")
    print(f"    Spearman ρ(diag_roam, diag_dwell): {rho_diag:.4f}")
    print(f"    Eigenvalue sum roam: {ev_r.sum():.4f}  dwell: {ev_d.sum():.4f}")
    print(f"    Condition number roam: {ev_r.max()/ev_r[ev_r>0].min():.2f}  dwell: {ev_d.max()/ev_d[ev_d>0].min():.2f}")
    print(f"    Spearman ρ(|ΔD|, |ΔQ|) on C4: {rho_dD_dQ:.4f}")

    return {
        "frob_deltaD": frob_dD, "frob_D_roam": frob_D,
        "relative_change": rel_change,
        "diag_roam_mean": float(np.diag(D_r).mean()),
        "diag_dwell_mean": float(np.diag(D_d).mean()),
        "diag_roam_cv": cv_r, "diag_dwell_cv": cv_d,
        "diag_delta_range": [float(diag_dD.min()), float(diag_dD.max())],
        "offdiag_delta_range": [float(offdiag_vals.min()), float(offdiag_vals.max())],
        "spearman_diag_roam_dwell": float(rho_diag),
        "cond_roam": float(ev_r.max()/ev_r[ev_r>0].min()),
        "cond_dwell": float(ev_d.max()/ev_d[ev_d>0].min()),
        "spearman_deltaD_deltaQ": float(rho_dD_dQ),
    }

d1_metrics = {
    "cepnem": delta_D_metrics(cep_state_D["roam"], cep_state_D["dwell"], "CePNEM"),
    "gcamp":  delta_D_metrics(g_state_D["roam"],   g_state_D["dwell"],   "GCaMP"),
}

# ── D1.3: State-specific ΔΩ ──────────────────────────────────────────────────
print("\n" + "="*70); print("D1.3 — State-Specific ΔΩ")

# ΔΩ_state = D_roam @ Q_roam - D_dwell @ Q_dwell  (A cancels)
# For diagonal D (row-scaling): ΔΩ_diag_state[i,j] = D_roam[i,i]*Q_roam[i,j] - D_dwell[i,i]*Q_dwell[i,j]
# For full D matrix: ΔΩ_full_state = D_roam @ Q_roam - D_dwell @ Q_dwell

def state_specific_deltaOmega(D_r, D_d, Q_r, Q_d):
    """Full matrix state-specific ΔΩ."""
    return D_r @ Q_r - D_d @ Q_d

def state_specific_deltaOmega_diag(D_r, D_d, Q_r, Q_d):
    """Diagonal D (row-scaling) state-specific ΔΩ."""
    dr_diag = np.diag(D_r); dd_diag = np.diag(D_d)
    return dr_diag[:, None] * Q_r - dd_diag[:, None] * Q_d

# CePNEM
DO_state_cep_full = state_specific_deltaOmega(
    cep_state_D["roam"], cep_state_D["dwell"], Q_r, Q_d)
DO_state_cep_diag = state_specific_deltaOmega_diag(
    cep_state_D["roam"], cep_state_D["dwell"], Q_r, Q_d)
DO_pooled_cep = D_pool_cep @ DQ   # from Phase 3C-E

# GCaMP
DO_state_g_full = state_specific_deltaOmega(
    g_state_D["roam"], g_state_D["dwell"], Q_rg, Q_dg)
DO_state_g_diag = state_specific_deltaOmega_diag(
    g_state_D["roam"], g_state_D["dwell"], Q_rg, Q_dg)
DO_pooled_g = np.load(ROOT / "results/phase3c/D_emp_gcamp.npy") @ DQg

# Rank correlations on C4
dq_c4_abs  = np.abs(DQ[ii_c4, jj_c4])
do_pool_c4 = np.abs(DO_pooled_cep[ii_c4, jj_c4])
do_ss_full_c4 = np.abs(DO_state_cep_full[ii_c4, jj_c4])
do_ss_diag_c4 = np.abs(DO_state_cep_diag[ii_c4, jj_c4])

rho_pool_dq,_ = stats.spearmanr(do_pool_c4, dq_c4_abs)
rho_ssf_dq,_  = stats.spearmanr(do_ss_full_c4, dq_c4_abs)
rho_ssd_dq,_  = stats.spearmanr(do_ss_diag_c4, dq_c4_abs)
rho_ssf_pool,_= stats.spearmanr(do_ss_full_c4, do_pool_c4)
rho_ssd_pool,_= stats.spearmanr(do_ss_diag_c4, do_pool_c4)

print(f"\n  CePNEM rank correlations (Class 4 |score|):")
print(f"    ρ(ΔΩ_pooled, ΔQ)       = {rho_pool_dq:.6f}")
print(f"    ρ(ΔΩ_ss_diag, ΔQ)      = {rho_ssd_dq:.6f}")
print(f"    ρ(ΔΩ_ss_full, ΔQ)      = {rho_ssf_dq:.6f}")
print(f"    ρ(ΔΩ_ss_full, ΔΩ_pool) = {rho_ssf_pool:.6f}")
print(f"    ρ(ΔΩ_ss_diag, ΔΩ_pool) = {rho_ssd_pool:.6f}")

# ── D1.4: PDF enrichment under state-specific Ω ──────────────────────────────
print("\n" + "="*70); print("D1.4 — PDF Enrichment Under State-Specific Ω")

def auroc_pdf(scores, mask=None):
    if mask is None: mask = pdf_mask
    ps = scores[mask]; ns = scores[~mask]
    if ps.size==0 or ns.size==0: return float("nan")
    u,_ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(u/(ps.size*ns.size))

def fisher_or_topk(scores, mask=None, k=20):
    if mask is None: mask = pdf_mask
    top = set(np.argsort(scores)[::-1][:k])
    a = sum(1 for i in range(N_C4) if i in top and mask[i])
    b = sum(1 for i in range(N_C4) if i in top and not mask[i])
    c = sum(1 for i in range(N_C4) if i not in top and mask[i])
    d = sum(1 for i in range(N_C4) if i not in top and not mask[i])
    or_,_ = stats.fisher_exact([[a,b],[c,d]], alternative="greater")
    return float(or_), int(a)

scores = {
    "ΔQ":             dq_c4_abs,
    "ΔΩ_pooled":      do_pool_c4,
    "ΔΩ_ss_diag":     do_ss_diag_c4,
    "ΔΩ_ss_full":     do_ss_full_c4,
}
print(f"\n  CePNEM PDF enrichment (n_pdf={pdf_mask.sum()}, k=20):")
d14_results = {}
for label, sc in scores.items():
    auc = auroc_pdf(sc)
    or_, k_ann = fisher_or_topk(sc)
    print(f"    {label:20s}: AUROC={auc:.4f}  Fisher OR={or_:.2f} [k_ann={k_ann}]")
    d14_results[label] = {"auroc": float(auc), "fisher_or": float(or_), "k_ann": int(k_ann)}

# GCaMP version
dqg_c4  = np.abs(DQg[ii_c4, jj_c4])
dpo_g_c4 = np.abs(DO_pooled_g[ii_c4, jj_c4])
dss_gf_c4 = np.abs(DO_state_g_full[ii_c4, jj_c4])
dss_gd_c4 = np.abs(DO_state_g_diag[ii_c4, jj_c4])
gcamp_scores = {
    "ΔQ": dqg_c4, "ΔΩ_pooled": dpo_g_c4,
    "ΔΩ_ss_diag": dss_gd_c4, "ΔΩ_ss_full": dss_gf_c4,
}
print(f"\n  GCaMP PDF enrichment:")
d14_gcamp = {}
for label, sc in gcamp_scores.items():
    auc = auroc_pdf(sc)
    or_, k_ann = fisher_or_topk(sc)
    print(f"    {label:20s}: AUROC={auc:.4f}  Fisher OR={or_:.2f} [k_ann={k_ann}]")
    d14_gcamp[label] = {"auroc": float(auc), "fisher_or": float(or_), "k_ann": int(k_ann)}

# =============================================================================
# D2: MODULE-LEVEL ANALYSIS
# =============================================================================
print("\n"+"="*70); print("D2 — Module-Level Current Organization")

BLOCKS = {
    "DA_mech":    [n2i[n] for n in ["ADEL","CEPDL","CEPDR","CEPVL"]],
    "RID":        [n2i["RID"]],
    "RME":        [n2i["RMEL"],n2i["RMER"]],
    "URY_URX":    [n2i[n] for n in ["URYDL","URYVL","URYVR","URXL"]],
    "command_IN": [n2i[n] for n in ["AVAL","AVAR","AVEL","AVER","AVDL","AVJL","AVJR"]],
    "OLL_OLQ":    [n2i[n] for n in ["OLLL","OLLR","OLQDL","OLQDR","OLQVL","OLQVR"]],
    "IL1_IL2":    [n2i[n] for n in ["IL1DR","IL1L","IL1R","IL2DL","IL2DR","IL2VL","IL2VR"]],
    "pharyngeal": [n2i[n] for n in ["I1L","I1R","I2L","I2R","I3","M1","M3L","M3R","M4","MI","NSML","NSMR"]],
    "RMD_SMD":    [n2i[n] for n in ["RMDDR","RMDL","RMDVL","RMDVR","SMDVL"]],
    "other":      [n2i[n] for n in ["AIBL","AIBR","AIZL","ASEL","ASGL","AUAL","AWAL","AWBL","AWCL","FLPL","RICL","RIVL","URBL"]],
}
block_names = list(BLOCKS.keys()); B = len(block_names)

def module_matrix(mat, use_abs=True):
    """Compute B×B matrix of mean absolute values per block pair (Class 4 pairs only)."""
    M = np.zeros((B, B))
    N_pairs = np.zeros((B, B), dtype=int)
    for b1 in range(B):
        for b2 in range(b1, B):
            vals = []
            for i in BLOCKS[block_names[b1]]:
                for j in BLOCKS[block_names[b2]]:
                    if i == j: continue
                    if b1 == b2 and j <= i: continue
                    key = (min(i,j),max(i,j))
                    if key in c4_set:
                        v = float(mat[i,j])
                        vals.append(abs(v) if use_abs else v)
            if vals:
                M[b1,b2] = M[b2,b1] = float(np.mean(vals))
                N_pairs[b1,b2] = N_pairs[b2,b1] = len(vals)
    return M, N_pairs

# Module matrices for all 4 combinations × 3 frameworks
print("\nD2.2 — Module-level matrices")
# CePNEM
M_dq,    N_m = module_matrix(DQ)
M_do_pool,_  = module_matrix(DO_pooled_cep)
M_do_ssd,_   = module_matrix(DO_state_cep_diag)
M_do_ssf,_   = module_matrix(DO_state_cep_full)
M_Qr,_       = module_matrix(Q_r)
M_Qd,_       = module_matrix(Q_d)

# Rank correlations between module-level ΔQ and ΔΩ
mask_m = N_m > 0
rho_mod_pool,_= stats.spearmanr(M_dq[mask_m], M_do_pool[mask_m])
rho_mod_ssd,_ = stats.spearmanr(M_dq[mask_m], M_do_ssd[mask_m])
rho_mod_ssf,_ = stats.spearmanr(M_dq[mask_m], M_do_ssf[mask_m])
print(f"  Module-level ρ(ΔΩ_pooled, ΔQ):    {rho_mod_pool:.6f}")
print(f"  Module-level ρ(ΔΩ_ss_diag, ΔQ):   {rho_mod_ssd:.6f}")
print(f"  Module-level ρ(ΔΩ_ss_full, ΔQ):   {rho_mod_ssf:.6f}")

def ranked_block_flows(M, N_pairs_mat, label):
    flows = []
    for b1 in range(B):
        for b2 in range(b1, B):
            if N_pairs_mat[b1,b2] > 0:
                flows.append({"b1": block_names[b1], "b2": block_names[b2],
                               "mean": float(M[b1,b2]), "n": int(N_pairs_mat[b1,b2])})
    flows.sort(key=lambda x: -x["mean"])
    print(f"\n  Top-10 module flows ({label}):")
    for i,row in enumerate(flows[:10]):
        da_ury = (row["b1"]=="DA_mech" and row["b2"]=="URY_URX") or \
                 (row["b1"]=="URY_URX" and row["b2"]=="DA_mech")
        marker = " ← DA_mech↔URY_URX" if da_ury else ""
        print(f"    {i+1:2d}. {row['b1']:12s}↔{row['b2']:12s}: "
              f"mean={row['mean']:.4f} n={row['n']}{marker}")
    return flows

print("\nD2.3 — Module-level ΔQ vs ΔΩ rankings")
flows_dq   = ranked_block_flows(M_dq,    N_m, "ΔQ (CePNEM)")
flows_pool  = ranked_block_flows(M_do_pool, N_m, "ΔΩ_pooled (CePNEM)")
flows_ssd   = ranked_block_flows(M_do_ssd,  N_m, "ΔΩ_ss_diag (CePNEM)")
flows_ssf   = ranked_block_flows(M_do_ssf,  N_m, "ΔΩ_ss_full (CePNEM)")

# D2.4: DA_mech ↔ URY_URX rank in each framework
da_ury_ranks = {}
for label, flows in [("ΔQ", flows_dq), ("ΔΩ_pooled", flows_pool),
                     ("ΔΩ_ss_diag", flows_ssd), ("ΔΩ_ss_full", flows_ssf)]:
    for i, row in enumerate(flows):
        if (row["b1"]=="DA_mech" and row["b2"]=="URY_URX") or \
           (row["b1"]=="URY_URX" and row["b2"]=="DA_mech"):
            da_ury_ranks[label] = i+1
            break
print(f"\n  DA_mech↔URY_URX rank:")
for label, rank in da_ury_ranks.items():
    print(f"    {label}: rank={rank}")

# D2.5: Module-level Ω visible but absent in Q
# Check if any block pair has much larger mean in ΔΩ than ΔQ (relative change > 50%)
print("\nD2.5 — Module pairs with >50% relative ΔΩ/ΔQ divergence:")
for b1 in range(B):
    for b2 in range(b1, B):
        if N_m[b1,b2] == 0: continue
        mq = M_dq[b1,b2]; ms = M_do_ssf[b1,b2]
        if mq < 1e-8: continue
        rel = (ms - mq) / mq
        if abs(rel) > 0.5:
            print(f"  {block_names[b1]:12s}↔{block_names[b2]:12s}: "
                  f"ΔQ={mq:.4f} ΔΩ_ssf={ms:.4f} rel_change={rel:+.2f}")

# ── D per module ─────────────────────────────────────────────────────────────
print("\nState-specific D diagonal by module (mean D_ii):")
for bname, bidxs in BLOCKS.items():
    dr = [cep_state_D["roam"][i,i]  for i in bidxs]
    dd = [cep_state_D["dwell"][i,i] for i in bidxs]
    delta = np.array(dr) - np.array(dd)
    print(f"  {bname:12s}: D_roam={np.mean(dr):.4f} D_dwell={np.mean(dd):.4f} "
          f"ΔD={delta.mean():+.4f} (|range| [{delta.min():+.4f},{delta.max():+.4f}])")

# ── Save results ───────────────────────────────────────────────────────────────
def sanitize(obj):
    if isinstance(obj,(np.floating,)):
        v=float(obj); return None if (v!=v or abs(v)==float("inf")) else v
    if isinstance(obj,float): return None if (obj!=obj or abs(obj)==float("inf")) else obj
    if isinstance(obj,(np.integer,)): return int(obj)
    if isinstance(obj,(np.bool_,)):   return bool(obj)
    if isinstance(obj,np.ndarray):    return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj,dict):          return {k: sanitize(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):  return [sanitize(v) for v in obj]
    return obj

# D per-neuron
pn_D = {}
for i, n in enumerate(NEURONS):
    pn_D[n] = {
        "D_roam_diag_cepnem":  float(cep_state_D["roam"][i,i]),
        "D_dwell_diag_cepnem": float(cep_state_D["dwell"][i,i]),
        "delta_D_diag_cepnem": float(cep_state_D["roam"][i,i] - cep_state_D["dwell"][i,i]),
        "D_roam_diag_gcamp":   float(g_state_D["roam"][i,i]),
        "D_dwell_diag_gcamp":  float(g_state_D["dwell"][i,i]),
        "delta_D_diag_gcamp":  float(g_state_D["roam"][i,i]  - g_state_D["dwell"][i,i]),
    }

output = {
    "date": "2026-06-03",
    "authorization": "Phase 3D",
    "D1_metrics": d1_metrics,
    "D1_rank_correlations": {
        "rho_DO_pooled_DQ": float(rho_pool_dq),
        "rho_DO_ss_diag_DQ": float(rho_ssd_dq),
        "rho_DO_ss_full_DQ": float(rho_ssf_dq),
        "rho_DO_ss_full_pooled": float(rho_ssf_pool),
        "rho_DO_ss_diag_pooled": float(rho_ssd_pool),
    },
    "D1_pdf_enrichment": {
        "cepnem": d14_results,
        "gcamp": d14_gcamp,
    },
    "D2_module_rank_correlations": {
        "rho_DO_pooled_DQ": float(rho_mod_pool),
        "rho_DO_ss_diag_DQ": float(rho_mod_ssd),
        "rho_DO_ss_full_DQ": float(rho_mod_ssf),
    },
    "D2_DA_URY_ranks": da_ury_ranks,
    "D2_top10_dq": flows_dq[:10],
    "D2_top10_do_ssf": flows_ssf[:10],
    "per_neuron_D": pn_D,
}

with open(OUT3D / "d1_diffusion_metrics.json","w") as f:
    json.dump(sanitize(output), f, indent=2)

np.save(OUT3D / "D_roam_cepnem.npy",   cep_state_D["roam"])
np.save(OUT3D / "D_dwell_cepnem.npy",  cep_state_D["dwell"])
np.save(OUT3D / "D_roam_gcamp.npy",    g_state_D["roam"])
np.save(OUT3D / "D_dwell_gcamp.npy",   g_state_D["dwell"])
np.save(OUT3D / "DO_state_cep_full.npy", DO_state_cep_full)
np.save(OUT3D / "DO_state_cep_diag.npy", DO_state_cep_diag)
print("\nSaved: d1_diffusion_metrics.json + state D matrices")
print("\n>>> STOP — awaiting reports <<<")
