"""Phase 3C-E — Empirical Diffusion Structure Analysis.

Authorization: Phase 3C-E, 2026-06-03.

Tasks:
  E1: Compute D_emp = Cov(Δx) for CePNEM and GCaMP (pooled across recordings)
  E2: Isotropy metrics (diagonal CV, eigenvalue spectrum, condition number,
      isotropy score ||D - cI||_F / ||D||_F)
  E3: Density metrics (off-diagonal energy fraction, median |D_ij|/D_ii)
  E4: Principal modes (variance explained by PC1, PC2, PC5)
  E5: ΔΩ_emp = D_emp @ ΔQ comparison vs ΔQ (Spearman ρ, top-20/100 overlap)

D_emp_ij = pairwise-complete Cov(Δx_i, Δx_j) pooled across all 40 recordings.
Gap frames handled implicitly: NaN in residuals/traces → NaN diff → excluded.

PROHIBITIONS: No model fitting. No held-out evaluation. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

import h5py
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.phase1.stage0_cepnem import build_label_maps

OUT3C = ROOT / "results/phase3c"

# ── Neuron/recording metadata ─────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS  = cop["neurons"]
REC_IDS  = cop["recording_ids"]
N        = len(NEURONS)           # 61
N_REC    = len(REC_IDS)          # 40
n2i      = {n: i for i, n in enumerate(NEURONS)}

# ── Load Phase 2 ΔQ matrices and Class 4 pairs ───────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r_cep  = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r_cep = (Q_r_cep + Q_r_cep.T)/2
Q_d_cep  = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d_cep = (Q_d_cep + Q_d_cep.T)/2
DQ_cep   = Q_r_cep - Q_d_cep

Q_r_g    = np.load(PREC_DIR / "Q_gcamp_roam_conf.npy");   Q_r_g  = (Q_r_g + Q_r_g.T)/2
Q_d_g    = np.load(PREC_DIR / "Q_gcamp_dwell_conf.npy");  Q_d_g  = (Q_d_g + Q_d_g.T)/2
DQ_g     = Q_r_g - Q_d_g

# Load CePNEM Class 4 set (used for ΔΩ_emp comparison)
ranked_c4_cep = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ranked_c4_g   = np.load(ROOT / "results/phase2/stage2/ranked_class4_gcamp.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4_cep = ii_all[ranked_c4_cep]; jj_c4_cep = jj_all[ranked_c4_cep]
ii_c4_g   = ii_all[ranked_c4_g];   jj_c4_g   = jj_all[ranked_c4_g]
c4_set_cep = set(zip(map(int, ii_c4_cep), map(int, jj_c4_cep)))
c4_set_g   = set(zip(map(int, ii_c4_g),   map(int, jj_c4_g)))
N_C4_cep = len(ranked_c4_cep)
N_C4_g   = len(ranked_c4_g)

# Load PDF annotation
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
neurons_set = set(NEURONS)
pdf_pairs: set = set()
with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        pdf_pairs.add((min(a,b), max(a,b)))
pdf_c4_cep = pdf_pairs & c4_set_cep
pdf_c4_g   = pdf_pairs & c4_set_g
ADEL = n2i["ADEL"]

# =============================================================================
# TASK E1 — Empirical Diffusion Matrices
# =============================================================================
print("=" * 70)
print("E1 — Empirical Diffusion Matrices: D_emp = Cov(Δx)")
print("=" * 70)

def compute_diffusion_matrix(coord: str) -> tuple[np.ndarray, dict]:
    """Compute pairwise-complete Cov(Δx_i, Δx_j) pooled across all recordings.

    For each pair (i, j), uses all time steps where BOTH Δx_i and Δx_j are finite.
    Gap frames are implicitly excluded because they are NaN in the source data,
    making the finite-difference NaN and thus excluded from the sum.

    Returns:
        D_emp: (N, N) empirical diffusion covariance matrix
        diagnostics: dict with coverage info
    """
    # Accumulators: sum of Δx_i * Δx_j, sum of Δx_i, sum of Δx_j, count
    sum_xy  = np.zeros((N, N), dtype=np.float64)
    sum_x   = np.zeros((N, N), dtype=np.float64)   # sum_x[i,j] = sum Δx_i where both finite
    sum_y   = np.zeros((N, N), dtype=np.float64)   # sum_y[i,j] = sum Δx_j where both finite
    cnt     = np.zeros((N, N), dtype=np.int64)

    if coord == "cepnem":
        RESID_DIR = ROOT / "results/phase1/data/cepnem_residuals"
        for rec_id in REC_IDS:
            npz_path = RESID_DIR / f"{rec_id}.npz"
            if not npz_path.exists():
                continue
            npz = np.load(npz_path)
            resid     = npz["residual"].astype(float)   # (T, n_rec)
            sub_lbl   = list(npz["neuron_labels"])

            # Build (T, 61) matrix; absent neurons remain NaN
            X = np.full((resid.shape[0], N), np.nan)
            for j, lbl in enumerate(sub_lbl):
                if lbl in n2i:
                    X[:, n2i[lbl]] = resid[:, j]

            # First differences: (T-1, 61), NaN propagates through gaps
            dX = np.diff(X, axis=0)   # (T-1, 61)

            # Accumulate pairwise complete-case
            # For efficiency, vectorize over column pairs
            for i in range(N):
                di = dX[:, i]
                fi = np.isfinite(di)
                if fi.sum() == 0:
                    continue
                for j in range(i, N):
                    dj = dX[:, j]
                    fj = np.isfinite(dj)
                    both = fi & fj
                    n_both = both.sum()
                    if n_both == 0:
                        continue
                    sv = float(np.sum(di[both] * dj[both]))
                    sx = float(di[both].sum())
                    sy = float(dj[both].sum())
                    sum_xy[i, j] += sv; sum_xy[j, i] += sv
                    sum_x[i, j]  += sx; sum_x[j, i]  += sx
                    sum_y[i, j]  += sy; sum_y[j, i]  += sy
                    cnt[i, j]    += n_both; cnt[j, i] += n_both

    else:  # gcamp
        H5_DIR     = ROOT / "data/atanas/AtanasKim-Cell2023"
        LABEL_PATH = H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2"
        label_recs = decode_atanas_jld2(LABEL_PATH)
        lmaps      = build_label_maps(label_recs, H5_DIR)

        for rec_id in REC_IDS:
            h5_path = H5_DIR / f"{rec_id}-data.h5"
            if not h5_path.exists():
                continue
            col_map = lmaps.get(rec_id, {})
            if not col_map:
                continue
            with h5py.File(h5_path, "r") as hf:
                trace_h5 = hf["gcamp/trace_array"][:]   # (T, n_total)

            X = np.full((trace_h5.shape[0], N), np.nan)
            for lbl, col_idx in col_map.items():
                if lbl in n2i:
                    X[:, n2i[lbl]] = trace_h5[:, col_idx].astype(float)

            dX = np.diff(X, axis=0)   # (T-1, 61)

            for i in range(N):
                di = dX[:, i]
                fi = np.isfinite(di)
                if fi.sum() == 0:
                    continue
                for j in range(i, N):
                    dj = dX[:, j]
                    fj = np.isfinite(dj)
                    both = fi & fj
                    n_both = both.sum()
                    if n_both == 0:
                        continue
                    sv = float(np.sum(di[both] * dj[both]))
                    sx = float(di[both].sum())
                    sy = float(dj[both].sum())
                    sum_xy[i, j] += sv; sum_xy[j, i] += sv
                    sum_x[i, j]  += sx; sum_x[j, i]  += sx
                    sum_y[i, j]  += sy; sum_y[j, i]  += sy
                    cnt[i, j]    += n_both; cnt[j, i] += n_both

    # Compute Cov(Δx_i, Δx_j) = E[ΔxΔx^T] - E[Δx_i]*E[Δx_j]
    D_emp = np.zeros((N, N), dtype=np.float64)
    for i in range(N):
        for j in range(i, N):
            c = cnt[i, j]
            if c < 2:
                D_emp[i, j] = D_emp[j, i] = 0.0
                continue
            e_xy = sum_xy[i, j] / c
            e_x  = sum_x[i, j]  / c
            e_y  = sum_y[i, j]  / c
            cov  = e_xy - e_x * e_y
            D_emp[i, j] = cov
            D_emp[j, i] = cov

    diag_D = np.diag(D_emp)
    n_zero_diag = int((diag_D <= 0).sum())
    n_pairs_covered = int((cnt[ii_all, jj_all] > 0).sum())
    diagnostics = {
        "min_count_diagonal": int(cnt.diagonal().min()),
        "min_count_offdiag":  int(cnt[ii_all, jj_all].min()),
        "n_zero_diag":        n_zero_diag,
        "n_off_diag_covered": n_pairs_covered,
        "total_off_diag":     len(ii_all),
    }
    print(f"  {coord}: diag range [{diag_D.min():.4f}, {diag_D.max():.4f}], "
          f"zero_diag={n_zero_diag}, "
          f"pairs_covered={n_pairs_covered}/{len(ii_all)}")
    return D_emp, diagnostics


print("\nComputing D_emp_CePNEM ...")
D_cep, diag_cep = compute_diffusion_matrix("cepnem")
print("Computing D_emp_GCaMP ...")
D_g,   diag_g   = compute_diffusion_matrix("gcamp")

np.save(OUT3C / "D_emp_cepnem.npy", D_cep)
np.save(OUT3C / "D_emp_gcamp.npy",  D_g)
print("Saved D_emp_cepnem.npy and D_emp_gcamp.npy")


# =============================================================================
# TASK E2 — Isotropy Metrics
# =============================================================================
print("\n" + "=" * 70)
print("E2 — Isotropy Metrics")
print("=" * 70)

def isotropy_metrics(D: np.ndarray, name: str) -> dict:
    diag_D = np.diag(D)
    c      = float(diag_D.mean())        # scalar for cI

    # Diagonal CV
    diag_cv = float(diag_D.std() / c) if c > 0 else float("inf")

    # Eigenvalue spectrum (symmetrize for safety)
    D_sym = (D + D.T) / 2
    evals  = np.linalg.eigvalsh(D_sym)
    evals_sorted = np.sort(evals)[::-1]  # largest first

    # Condition number (ratio of largest to smallest positive eigenvalue)
    pos_evals = evals[evals > 0]
    cond = float(pos_evals.max() / pos_evals.min()) if len(pos_evals) > 1 else float("inf")

    # Isotropy score: ||D - cI||_F / ||D||_F
    iso_score = float(np.linalg.norm(D - c * np.eye(N), "fro") / np.linalg.norm(D, "fro"))

    # Fraction of variance explained by diagonal
    fro_D    = float(np.linalg.norm(D, "fro") ** 2)
    fro_diag = float(np.linalg.norm(np.diag(diag_D), "fro") ** 2)
    diag_frac = fro_diag / fro_D if fro_D > 0 else 0.0

    print(f"\n{name}:")
    print(f"  Diagonal: mean={c:.4f}  std={diag_D.std():.4f}  CV={diag_cv:.4f}")
    print(f"  Eigenvalues (top 5): {evals_sorted[:5].tolist()}")
    print(f"  Eigenvalues (bot 5): {evals_sorted[-5:].tolist()}")
    print(f"  Condition number: {cond:.2e}")
    print(f"  Isotropy score ||D-cI||/||D||: {iso_score:.4f}")
    print(f"  Diagonal fraction of ||D||^2: {diag_frac:.4f}")

    return {
        "diagonal_mean":   c,
        "diagonal_std":    float(diag_D.std()),
        "diagonal_cv":     diag_cv,
        "diagonal_range":  [float(diag_D.min()), float(diag_D.max())],
        "eigenvalues_top5":  [float(v) for v in evals_sorted[:5]],
        "eigenvalues_bot5":  [float(v) for v in evals_sorted[-5:]],
        "eigenvalue_full":   [float(v) for v in evals_sorted],
        "condition_number":  cond,
        "isotropy_score":    iso_score,
        "diagonal_energy_frac": diag_frac,
        "n_negative_eigenvalues": int((evals < 0).sum()),
    }

e2_cep = isotropy_metrics(D_cep, "D_emp_CePNEM")
e2_g   = isotropy_metrics(D_g,   "D_emp_GCaMP")


# =============================================================================
# TASK E3 — Density Metrics
# =============================================================================
print("\n" + "=" * 70)
print("E3 — Density Metrics")
print("=" * 70)

def density_metrics(D: np.ndarray, name: str) -> dict:
    diag_D  = np.diag(D).copy()
    D_offdiag = D.copy()
    np.fill_diagonal(D_offdiag, 0.0)

    # Off-diagonal energy fraction: ||D - diag(D)||_F / ||D||_F
    fro_offdiag = float(np.linalg.norm(D_offdiag, "fro"))
    fro_D       = float(np.linalg.norm(D, "fro"))
    offdiag_frac = fro_offdiag / fro_D if fro_D > 0 else 0.0

    # Median |D_ij| / median D_ii for i ≠ j
    offdiag_vals = D[ii_all, jj_all]  # upper triangle off-diagonal
    med_abs_off  = float(np.median(np.abs(offdiag_vals)))
    med_diag     = float(np.median(np.abs(diag_D)))
    ratio_med    = med_abs_off / med_diag if med_diag > 0 else float("inf")

    # Top 10 largest |off-diagonal| entries
    abs_off = np.abs(D_offdiag)
    flat_idx = np.argsort(-abs_off.ravel())
    seen = set()
    top10_off = []
    for idx in flat_idx:
        i, j = divmod(idx, N)
        if i >= j: continue
        if (i, j) in seen: continue
        seen.add((i, j))
        top10_off.append((NEURONS[i], NEURONS[j], float(D[i, j])))
        if len(top10_off) == 10:
            break

    print(f"\n{name}:")
    print(f"  Off-diagonal energy frac ||D-diag||/||D||: {offdiag_frac:.4f}")
    print(f"  Median |D_ij|/median D_ii (off-diag): {ratio_med:.4f}")
    print(f"  Top-10 |off-diagonal| entries:")
    for ni, nj, v in top10_off:
        print(f"    {ni:8s}–{nj:8s}: {v:+.6f}")

    return {
        "offdiag_energy_frac": offdiag_frac,
        "median_abs_offdiag":  med_abs_off,
        "median_diag":         med_diag,
        "ratio_median_offdiag_to_diag": ratio_med,
        "top10_offdiag": top10_off,
    }

e3_cep = density_metrics(D_cep, "D_emp_CePNEM")
e3_g   = density_metrics(D_g,   "D_emp_GCaMP")


# =============================================================================
# TASK E4 — Principal Modes
# =============================================================================
print("\n" + "=" * 70)
print("E4 — Principal Modes (PCA of D_emp)")
print("=" * 70)

def principal_modes(D: np.ndarray, name: str) -> dict:
    D_sym  = (D + D.T) / 2
    # Eigendecomposition (eigvalsh returns ascending order)
    evals, evecs = np.linalg.eigh(D_sym)
    evals = evals[::-1]; evecs = evecs[:, ::-1]  # descending

    # Variance explained = eigenvalue_k / sum(abs(eigenvalues))
    # Use sum of positive eigenvalues as total variance
    pos_sum = float(evals[evals > 0].sum())
    var_exp = np.maximum(evals, 0) / pos_sum if pos_sum > 0 else np.zeros_like(evals)

    ve1 = float(var_exp[0])
    ve2 = float(var_exp[:2].sum())
    ve5 = float(var_exp[:5].sum())

    # PC1 loadings — top 5 contributing neurons
    pc1 = evecs[:, 0]
    top5_pc1 = sorted(zip(NEURONS, pc1.tolist()), key=lambda x: -abs(x[1]))[:5]

    print(f"\n{name}:")
    print(f"  Variance explained — PC1: {ve1:.4f}  PC1+2: {ve2:.4f}  PC1-5: {ve5:.4f}")
    print(f"  PC1 top-5 loadings: {[(n, f'{v:.3f}') for n, v in top5_pc1]}")

    return {
        "var_explained_pc1":   ve1,
        "var_explained_pc1_2": ve2,
        "var_explained_pc1_5": ve5,
        "pc1_top5_neurons":    [(n, float(v)) for n, v in top5_pc1],
        "eigenvalues_pos_sum": pos_sum,
    }

e4_cep = principal_modes(D_cep, "D_emp_CePNEM")
e4_g   = principal_modes(D_g,   "D_emp_GCaMP")


# =============================================================================
# TASK E5 — ΔΩ_emp vs ΔQ
# =============================================================================
print("\n" + "=" * 70)
print("E5 — ΔΩ_emp = D_emp @ ΔQ vs ΔQ")
print("=" * 70)

def deltaOmega_emp_comparison(D_emp: np.ndarray, DQ: np.ndarray,
                               ii_c4, jj_c4, pdf_c4, name: str) -> dict:
    # ΔΩ_emp[i,j] = Σ_k D_emp[i,k] * ΔQ[k,j]
    # This is a full matrix multiplication, not elementwise
    dO_emp = D_emp @ DQ   # (61, 61)

    N_C4 = len(ii_c4)
    dq_c4   = np.abs(DQ[ii_c4, jj_c4])
    dO_c4   = np.abs(dO_emp[ii_c4, jj_c4])

    # Spearman ρ
    rho, _ = stats.spearmanr(dO_c4, dq_c4)

    # Top-20 and top-100 overlap
    rank_dO = np.argsort(-dO_c4)
    rank_dQ = np.argsort(-dq_c4)
    top20_dO  = set(rank_dO[:20]);  top20_dQ  = set(rank_dQ[:20])
    top100_dO = set(rank_dO[:100]); top100_dQ = set(rank_dQ[:100])
    ov20  = len(top20_dO  & top20_dQ)
    ov100 = len(top100_dO & top100_dQ)

    # PDF AUROC
    pdf_mask = np.array([(min(ii_c4[k], jj_c4[k]), max(ii_c4[k], jj_c4[k])) in pdf_c4
                          for k in range(N_C4)])
    def auroc(scores):
        ps = scores[pdf_mask]; ns = scores[~pdf_mask]
        if len(ps) == 0 or len(ns) == 0: return 0.5
        U, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
        return float(U / (len(ps) * len(ns)))

    auroc_dO = auroc(dO_c4)
    auroc_dQ = auroc(dq_c4)

    # Pairs absent from ΔQ top-200 that appear in ΔΩ_emp top-200
    absent = len(set(rank_dO[:200]) - set(rank_dQ[:200]))

    print(f"\n{name}:")
    print(f"  Spearman ρ(|ΔΩ_emp|, |ΔQ|): {rho:.6f}")
    print(f"  Top-20 overlap:  {ov20}/20")
    print(f"  Top-100 overlap: {ov100}/100")
    print(f"  PDF AUROC — ΔΩ_emp: {auroc_dO:.4f}  ΔQ: {auroc_dQ:.4f}")
    print(f"  New pairs in top-200 ΔΩ_emp not in top-200 ΔQ: {absent}")

    # ADEL pairs
    adel_pairs = [(k, ii_c4[k], jj_c4[k]) for k in range(N_C4)
                  if ii_c4[k] == ADEL or jj_c4[k] == ADEL]
    rank_dq_pos  = np.empty(N_C4, dtype=int); rank_dq_pos[rank_dQ] = np.arange(1, N_C4+1)
    rank_dO_pos  = np.empty(N_C4, dtype=int); rank_dO_pos[rank_dO] = np.arange(1, N_C4+1)
    print(f"  ADEL top-6 (by ΔQ):")
    for k, i, j in sorted(adel_pairs, key=lambda x: rank_dq_pos[x[0]])[:6]:
        is_pdf = (min(i,j), max(i,j)) in pdf_c4
        print(f"    {NEURONS[i]:6s}–{NEURONS[j]:6s}: ΔQ rank={rank_dq_pos[k]:4d}  "
              f"ΔΩ_emp rank={rank_dO_pos[k]:4d}  Δ={rank_dO_pos[k]-rank_dq_pos[k]:+d}"
              f"  {'PDF' if is_pdf else ''}")

    return {
        "spearman_rho": float(rho),
        "top20_overlap": ov20,
        "top100_overlap": ov100,
        "pdf_auroc_dO_emp": auroc_dO,
        "pdf_auroc_dQ":     auroc_dQ,
        "new_pairs_top200": absent,
    }

e5_cep = deltaOmega_emp_comparison(D_cep, DQ_cep, ii_c4_cep, jj_c4_cep,
                                    pdf_c4_cep, "CePNEM")
e5_g   = deltaOmega_emp_comparison(D_g,   DQ_g,   ii_c4_g,   jj_c4_g,
                                    pdf_c4_g,   "GCaMP")


# =============================================================================
# SAVE RESULTS
# =============================================================================
output = {
    "date":          "2026-06-03",
    "authorization": "Phase 3C-E",
    "E1_diagnostics": {
        "cepnem": diag_cep,
        "gcamp":  diag_g,
    },
    "E2_isotropy": {
        "cepnem": e2_cep,
        "gcamp":  e2_g,
    },
    "E3_density": {
        "cepnem": e3_cep,
        "gcamp":  e3_g,
    },
    "E4_pca": {
        "cepnem": e4_cep,
        "gcamp":  e4_g,
    },
    "E5_deltaOmega_emp": {
        "cepnem": e5_cep,
        "gcamp":  e5_g,
    },
}

def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if (v != v or abs(v) == float("inf")) else v
    if isinstance(obj, float):
        return None if (obj != obj or abs(obj) == float("inf")) else obj
    if isinstance(obj, (np.integer,)):      return int(obj)
    if isinstance(obj, (np.bool_,)):        return bool(obj)
    if isinstance(obj, np.ndarray):         return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict):               return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):      return [sanitize(v) for v in obj]
    return obj

with open(OUT3C / "diffusion_metrics.json", "w") as f:
    json.dump(sanitize(output), f, indent=2)

# Save diagonal entries for per-neuron table
diag_table = {
    "neurons": NEURONS,
    "D_emp_cepnem_diagonal": [float(D_cep[i, i]) for i in range(N)],
    "D_emp_gcamp_diagonal":  [float(D_g[i, i])   for i in range(N)],
}
with open(OUT3C / "diffusion_matrices.json", "w") as f:
    json.dump(sanitize(diag_table), f, indent=2)

print("\nSaved: diffusion_metrics.json, diffusion_matrices.json")
print("\n>>> STOP CONDITION — awaiting cE report <<<")
