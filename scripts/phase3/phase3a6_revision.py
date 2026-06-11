"""Phase 3A.6 — Architecture Revision Study (R2–R5).

Authorization: Phase 3A.6, 2026-06-03.

R1: Reference (Lyapunov, global Spearman objective) — reproduced numbers only
R2: PDF-pair local objective (fit on 57 non-ADEL PDF pairs only)
R3: Sparse forward model (apply ADMM sparsification to Lyapunov Q_pred)
R4: Degree-sequence control (source-out-degree-preserving target shuffle null, N=100)
R5: α sensitivity (∂ΔQ/∂α at fitted M1 solution)

PROHIBITIONS: No held-out ADEL evaluation. No Phase 3B. No neuron-specific α.
"""
from __future__ import annotations
import csv, json, sys, time, warnings
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
from scipy import linalg, stats, optimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

OUT_P3  = ROOT / "results/phase3"
OUT_REV = OUT_P3 / "revision"
OUT_REV.mkdir(parents=True, exist_ok=True)

# ── Load fixed artifacts ──────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"

with open(OUT_P3 / "phase3a_fit_parameters.json") as f:
    fp = json.load(f)
with open(OUT_P3 / "phase3a_stability_report.json") as f:
    sr = json.load(f)

alpha_r_M1 = float(fp["M1"]["alpha_roam"])
alpha_d_M1 = float(fp["M1"]["alpha_dwell"])
gamma_J    = float(sr["M1_J_directed"]["gamma"])
alpha_max  = float(sr["M1_J_directed"]["alpha_max_P_norm"])
alpha_min  = float(sr["M1_J_directed"]["alpha_min_P_norm"])
rho_M1     = float(fp["M1"]["rho_train"])
auroc_M1   = float(fp["M1"]["auroc_pdf_train"])

J_directed = np.load(OUT_P3 / "phase3a_J_directed.npy")
J_base     = J_directed - gamma_J * np.eye(N)
P_directed = np.load(OUT_P3 / "phase3a_P_directed.npy")
P_norm     = np.load(OUT_P3 / "phase3a_P_norm.npy")
P_rand_all = np.load(OUT_P3 / "phase3a_P_rand.npy")           # (1000,61,61) edge-swap
P_rand_norm_all = np.load(OUT_P3 / "phase3a_P_rand_norm.npy") # (1000,61,61)

DQ_obs     = np.load(ROOT / "results/phase2/stage2/DQ_cepnem.npy")

ranked_c4  = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)

HELD_OUT = frozenset([(n2i["ADEL"], n2i["URYVR"]), (n2i["ADEL"], n2i["URYDL"]),
                      (n2i["ADEL"], n2i["RMEL"]),  (n2i["ADEL"], n2i["URXL"])])
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

# PDF annotation
pdf_c4: set = set()
P_sources = {n2i["RID"], n2i["ADEL"], n2i["RMEL"], n2i["RMER"], n2i["AVDL"]}
P_targets: set = set()
with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
    reader = csv.reader(f); next(reader)
    seen_pdf: set = set()
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        if (a, b) not in seen_pdf:
            seen_pdf.add((a, b))
            P_targets.add(b)
        pdf_c4.add((min(a, b), max(a, b)))
pdf_c4 = pdf_c4 & c4_set
pdf_train = pdf_c4 - HELD_OUT   # 57 non-ADEL PDF training pairs
P_targets_list = sorted(P_targets)

# Training indices
train_mask = np.array([(ii_c4[k], jj_c4[k]) not in HELD_OUT for k in range(N_C4)], dtype=bool)
train_ii   = ii_c4[train_mask]; train_jj = jj_c4[train_mask]
DQ_obs_train = DQ_obs[train_ii, train_jj]

# PDF training mask (within train set)
train_pdf_mask = np.array([
    (min(ii_c4[k], jj_c4[k]), max(ii_c4[k], jj_c4[k])) in pdf_c4
    for k in range(N_C4) if train_mask[k]
])

# PDF training pair indices (in full Class 4 list)
pdf_train_k = [k for k in range(N_C4) if train_mask[k] and
               (min(ii_c4[k], jj_c4[k]), max(ii_c4[k], jj_c4[k])) in pdf_train]
pdf_train_ii = ii_c4[pdf_train_k]
pdf_train_jj = jj_c4[pdf_train_k]
DQ_obs_pdf   = DQ_obs[pdf_train_ii, pdf_train_jj]

# Phase 2 parameters for ADMM
import phase2_config as p2cfg
LAM_ON  = p2cfg.LAMBDA_ON   # 0.01
LAM_OFF = p2cfg.LAMBDA_OFF  # 0.10
A_raw   = (J_directed + J_directed.T) > 0   # symmetric for penalty mask

print(f"Setup: N_C4={N_C4}  N_train={train_mask.sum()}  N_pdf_train={len(pdf_train_k)}  N_held_out=4")
print(f"P_sources={len(P_sources)}  P_targets={len(P_targets)}")
print(f"M1 reference: α_r={alpha_r_M1:.4f}, α_d={alpha_d_M1:.4f}, ρ={rho_M1:.4f}")

# ── Forward model utilities ───────────────────────────────────────────────────
def lyapunov(J_eff: np.ndarray) -> np.ndarray | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Sig = linalg.solve_continuous_lyapunov(J_eff, -np.eye(N))
        Sig = (Sig + Sig.T) / 2
        ev = np.linalg.eigvalsh(Sig)
        if ev.min() < -1e-8: return None
        Sig += max(0.0, -ev.min() + 1e-10) * np.eye(N)
        return Sig
    except Exception: return None

def predict_Q(alpha: float, J_b: np.ndarray, P_m: np.ndarray) -> np.ndarray | None:
    Sig = lyapunov(J_b + alpha * P_m)
    if Sig is None: return None
    Q = np.linalg.inv(Sig)
    return (Q + Q.T) / 2

def predict_deltaQ(alpha_r: float, alpha_d: float,
                   J_b: np.ndarray, P_m: np.ndarray) -> np.ndarray | None:
    Q_r = predict_Q(alpha_r, J_b, P_m)
    Q_d = predict_Q(alpha_d, J_b, P_m)
    if Q_r is None or Q_d is None: return None
    return Q_r - Q_d

def spearman_obj_global(ar: float, ad: float, J_b: np.ndarray, P_m: np.ndarray) -> float:
    DQ = predict_deltaQ(ar, ad, J_b, P_m)
    if DQ is None: return float("nan")
    rho, _ = stats.spearmanr(np.abs(DQ[train_ii, train_jj]), np.abs(DQ_obs_train))
    return float(rho) if not np.isnan(rho) else 0.0

def spearman_obj_pdf(ar: float, ad: float, J_b: np.ndarray, P_m: np.ndarray) -> float:
    """Spearman on PDF training pairs only."""
    DQ = predict_deltaQ(ar, ad, J_b, P_m)
    if DQ is None: return float("nan")
    pred = np.abs(DQ[pdf_train_ii, pdf_train_jj])
    obs  = np.abs(DQ_obs_pdf)
    if np.std(pred) < 1e-12 or np.std(obs) < 1e-12: return 0.0
    rho, _ = stats.spearmanr(pred, obs)
    return float(rho) if not np.isnan(rho) else 0.0

def auroc(dq_pred_c4: np.ndarray) -> float:
    """AUROC: do PDF training pairs rank higher than non-PDF training pairs?"""
    dq_train = np.abs(dq_pred_c4[train_mask])
    ps = np.abs(dq_train[train_pdf_mask])
    ns = np.abs(dq_train[~train_pdf_mask])
    if len(ps) == 0 or len(ns) == 0: return 0.5
    U, _ = stats.mannwhitneyu(ps, ns, alternative="greater")
    return float(U / (len(ps) * len(ns)))

# Alpha grid (same as M1)
alpha_lo_coarse = float(alpha_min * 0.9)
alpha_lo_fine   = float(alpha_min * 0.05)
alpha_hi_fine   = float(alpha_max * 0.9)
alpha_coarse    = np.linspace(alpha_lo_coarse, alpha_lo_fine, 11, endpoint=False)
alpha_fine      = np.linspace(alpha_lo_fine, alpha_hi_fine, 41)
alpha_grid      = np.concatenate([alpha_coarse, alpha_fine])
GRID_N          = len(alpha_grid)

def grid_fit_2d(spearman_fn, J_b: np.ndarray, P_m: np.ndarray,
                lo: float = alpha_lo_coarse, hi: float = alpha_hi_fine):
    """Grid search + Nelder-Mead for 2D (α_r, α_d)."""
    surf = np.full((GRID_N, GRID_N), np.nan)
    for i, ar in enumerate(alpha_grid):
        for j, ad in enumerate(alpha_grid):
            surf[i, j] = spearman_fn(ar, ad, J_b, P_m)
    best = int(np.nanargmax(surf))
    bi, bj = np.unravel_index(best, surf.shape)
    ar0, ad0 = alpha_grid[bi], alpha_grid[bj]
    def neg(params):
        v = spearman_fn(params[0], params[1], J_b, P_m)
        if np.isnan(v): return 1.0
        return -v
    res = optimize.minimize(neg, [ar0, ad0], method="Nelder-Mead",
                            options={"maxiter": 1000, "xatol": 1e-4, "fatol": 1e-4})
    return float(res.x[0]), float(res.x[1]), float(-res.fun), surf

def grid_fit_1d(spearman_fn, J_b: np.ndarray, P_m: np.ndarray, ar_fixed: float):
    """1D grid search over α_d with fixed α_r."""
    best_rho, best_ad = -np.inf, 0.0
    for ad in alpha_grid:
        rho = spearman_fn(ar_fixed, ad, J_b, P_m)
        if not np.isnan(rho) and rho > best_rho:
            best_rho, best_ad = rho, ad
    return float(best_ad), float(best_rho)

# ADMM confirmation estimator (from Phase 2)
def admm_confirmation(S: np.ndarray, A: np.ndarray = A_raw) -> np.ndarray:
    L = np.where(A > 0, LAM_ON, LAM_OFF).astype(float)
    np.fill_diagonal(L, 0.0)
    Theta = np.eye(N); Z = np.eye(N); U = np.zeros((N, N))
    for _ in range(1000):
        B = Z - U - S; B = (B + B.T) / 2
        ev, vc = np.linalg.eigh(B)
        Theta = vc @ np.diag((ev + np.sqrt(ev**2 + 4)) / 2) @ vc.T
        W = Theta + U
        Z_new = np.sign(W) * np.maximum(np.abs(W) - L, 0.0)
        Z_new[np.arange(N), np.arange(N)] = W[np.arange(N), np.arange(N)]
        res = Theta - Z_new; U += res; Z = Z_new
        if np.max(np.abs(res)) < 1e-5: break
    return Z

def topk_overlap(arr1: np.ndarray, arr2: np.ndarray, K: int) -> int:
    return len(set(np.argsort(-np.abs(arr1))[:K]) & set(np.argsort(-np.abs(arr2))[:K]))

# Pre-compute M1 ΔQ (reference)
DQ_M1 = predict_deltaQ(alpha_r_M1, alpha_d_M1, J_base, P_norm)
assert DQ_M1 is not None
DQ_M1_train = DQ_M1[train_ii, train_jj]
DQ_obs_c4   = DQ_obs[ii_c4, jj_c4]
DQ_M1_c4    = DQ_M1[ii_c4, jj_c4]

rng = np.random.default_rng(2026_06_03 + 1)

# =============================================================================
print("\n" + "="*70)
print("R1 — Reference (reproduce key numbers)")
print("="*70)
rho_R1  = float(stats.spearmanr(np.abs(DQ_M1_train), np.abs(DQ_obs_train))[0])
auroc_R1= auroc(DQ_M1_c4)
ov10_R1 = topk_overlap(DQ_obs_c4, DQ_M1_c4, 10)
ov20_R1 = topk_overlap(DQ_obs_c4, DQ_M1_c4, 20)
print(f"  ρ={rho_R1:.4f}  AUROC={auroc_R1:.4f}  top-10 overlap={ov10_R1}  top-20={ov20_R1}")

# =============================================================================
print("\n" + "="*70)
print("R2 — PDF-pair local objective")
print("="*70)
t0 = time.time()
ar_R2, ad_R2, rho_R2_pdf, _ = grid_fit_2d(spearman_obj_pdf, J_base, P_norm)
DQ_R2 = predict_deltaQ(ar_R2, ad_R2, J_base, P_norm)
rho_R2_global = spearman_obj_global(ar_R2, ad_R2, J_base, P_norm)
auroc_R2 = auroc(DQ_R2[ii_c4, jj_c4]) if DQ_R2 is not None else 0.5
ov10_R2 = topk_overlap(DQ_obs_c4, DQ_R2[ii_c4, jj_c4], 10) if DQ_R2 is not None else 0
ov20_R2 = topk_overlap(DQ_obs_c4, DQ_R2[ii_c4, jj_c4], 20) if DQ_R2 is not None else 0

# Also compare PDF-specific ρ for M1 at R1 fit
rho_M1_pdfonly = spearman_obj_pdf(alpha_r_M1, alpha_d_M1, J_base, P_norm)
print(f"  R2 fit: α_r={ar_R2:.4f}, α_d={ad_R2:.4f}  ({time.time()-t0:.1f}s)")
print(f"  R2: ρ_pdf={rho_R2_pdf:.4f}  ρ_global={rho_R2_global:.4f}  AUROC={auroc_R2:.4f}  top-10={ov10_R2}  top-20={ov20_R2}")
print(f"  R1 at PDF-only obj: ρ_pdf={rho_M1_pdfonly:.4f}")
print(f"  Δρ_pdf (R2 vs R1): {rho_R2_pdf - rho_M1_pdfonly:+.4f}")

# =============================================================================
print("\n" + "="*70)
print("R3 — Sparse forward model (3 variants)")
print("="*70)

# ── R3A: Apply ADMM graphical lasso to Lyapunov Σ ────────────────────────────
print("  [R3A] ADMM sparsification of Lyapunov covariance...")
t0 = time.time()

# Get Lyapunov Σ at fitted M1 parameters
J_r = J_base + alpha_r_M1 * P_norm
J_d = J_base + alpha_d_M1 * P_norm
Sig_r = lyapunov(J_r)
Sig_d = lyapunov(J_d)
assert Sig_r is not None and Sig_d is not None

# Normalize to correlation matrix (unit diagonal)
d_r = np.sqrt(np.diag(Sig_r))
d_d = np.sqrt(np.diag(Sig_d))
Sig_r_norm = Sig_r / np.outer(d_r, d_r)
Sig_d_norm = Sig_d / np.outer(d_d, d_d)

# Apply ADMM with Phase 2 parameters
Q_r_sparse = admm_confirmation(Sig_r_norm)
Q_d_sparse = admm_confirmation(Sig_d_norm)
DQ_R3A     = Q_r_sparse - Q_d_sparse
DQ_R3A_c4  = DQ_R3A[ii_c4, jj_c4]

rho_R3A  = float(stats.spearmanr(np.abs(DQ_R3A[train_ii, train_jj]), np.abs(DQ_obs_train))[0])
auroc_R3A = auroc(DQ_R3A_c4)
ov10_R3A  = topk_overlap(DQ_obs_c4, DQ_R3A_c4, 10)
ov20_R3A  = topk_overlap(DQ_obs_c4, DQ_R3A_c4, 20)
ov50_R3A  = topk_overlap(DQ_obs_c4, DQ_R3A_c4, 50)
ov100_R3A = topk_overlap(DQ_obs_c4, DQ_R3A_c4, 100)
nonzero_R3A = (np.abs(DQ_R3A_c4) > 1e-9).sum()
print(f"  R3A: ρ={rho_R3A:.4f}  AUROC={auroc_R3A:.4f}  nonzero={nonzero_R3A}/{N_C4}"
      f"  overlap top-10={ov10_R3A}  top-20={ov20_R3A}  top-50={ov50_R3A}  top-100={ov100_R3A}  ({time.time()-t0:.1f}s)")

# ── R3B: Top-k threshold (match observed density) ────────────────────────────
obs_nonzero = (np.abs(DQ_obs_c4) > 0).sum()
k_thresh    = obs_nonzero  # keep same number nonzero as observed
rank_pred   = np.argsort(-np.abs(DQ_M1_c4))
DQ_R3B_c4  = np.zeros(N_C4)
DQ_R3B_c4[rank_pred[:k_thresh]] = DQ_M1_c4[rank_pred[:k_thresh]]

rho_R3B   = float(stats.spearmanr(np.abs(DQ_R3B_c4[train_mask]), np.abs(DQ_obs_train))[0])
auroc_R3B = auroc(DQ_R3B_c4)
ov10_R3B  = topk_overlap(DQ_obs_c4, DQ_R3B_c4, 10)
ov20_R3B  = topk_overlap(DQ_obs_c4, DQ_R3B_c4, 20)
ov50_R3B  = topk_overlap(DQ_obs_c4, DQ_R3B_c4, 50)
ov100_R3B = topk_overlap(DQ_obs_c4, DQ_R3B_c4, 100)
print(f"  R3B: ρ={rho_R3B:.4f}  AUROC={auroc_R3B:.4f}  (density-matched threshold)"
      f"  top-10={ov10_R3B}  top-20={ov20_R3B}  top-50={ov50_R3B}")

# ── R3C: ADMM then evaluate at R2-fitted α (PDF-optimized) ───────────────────
print("  [R3C] ADMM sparsification at R2-optimized α...")
t0 = time.time()
J_r2 = J_base + ar_R2 * P_norm
J_d2 = J_base + ad_R2 * P_norm
Sig_r2 = lyapunov(J_r2); Sig_d2 = lyapunov(J_d2)
rho_R3C = ov10_R3C = ov20_R3C = None
if Sig_r2 is not None and Sig_d2 is not None:
    d_r2 = np.sqrt(np.diag(Sig_r2)); d_d2 = np.sqrt(np.diag(Sig_d2))
    S_r2_n = Sig_r2 / np.outer(d_r2, d_r2)
    S_d2_n = Sig_d2 / np.outer(d_d2, d_d2)
    Q_r2_sp = admm_confirmation(S_r2_n)
    Q_d2_sp = admm_confirmation(S_d2_n)
    DQ_R3C_c4 = (Q_r2_sp - Q_d2_sp)[ii_c4, jj_c4]
    rho_R3C  = float(stats.spearmanr(np.abs(DQ_R3C_c4[train_mask]), np.abs(DQ_obs_train))[0])
    auroc_R3C = auroc(DQ_R3C_c4)
    ov10_R3C = topk_overlap(DQ_obs_c4, DQ_R3C_c4, 10)
    ov20_R3C = topk_overlap(DQ_obs_c4, DQ_R3C_c4, 20)
    ov50_R3C = topk_overlap(DQ_obs_c4, DQ_R3C_c4, 50)
    print(f"  R3C: ρ={rho_R3C:.4f}  AUROC={auroc_R3C:.4f}  top-10={ov10_R3C}  top-20={ov20_R3C}  top-50={ov50_R3C}  ({time.time()-t0:.1f}s)")
else:
    print("  R3C: Lyapunov failed at R2 α")

# =============================================================================
print("\n" + "="*70)
print("R4 — Degree-sequence control (source-out-degree-preserving target shuffle, N=100)")
print("="*70)
# Build null: for each source neuron, keep same out-degree
# but randomly sample targets from P_targets_list (the pdfr-1 pool)
# This preserves source identity and out-degree, randomizes target assignment

def build_target_shuffle_null(P_ref: np.ndarray,
                              sources: set, targets: list,
                              rng: np.random.Generator) -> np.ndarray:
    """Shuffle targets for each source while preserving out-degree.
    Source identity is fixed; targets are sampled from the pdfr-1 target pool.
    """
    P_null = np.zeros_like(P_ref)
    for src_idx in sorted(sources):
        orig_targets = np.where(P_ref[src_idx] > 0)[0].tolist()
        k = len(orig_targets)
        if k == 0: continue
        pool = [t for t in targets if t != src_idx]   # exclude self-loops
        new_tgts = rng.choice(pool, size=k, replace=False)
        for t in new_tgts:
            P_null[src_idx, t] = 1.0
    return P_null

# Build R4 null ensemble
N_R4 = 100
P_r4_list = []
for _ in range(N_R4):
    P_r4_list.append(build_target_shuffle_null(P_directed, P_sources, P_targets_list, rng))

# Normalize
P_r4_norm_list = [p / (np.linalg.norm(p, "fro") + 1e-12) for p in P_r4_list]

# Verify degree preservation
for P_r4 in P_r4_list[:5]:
    for src_idx in P_sources:
        assert P_r4[src_idx].sum() == P_directed[src_idx].sum(), "Out-degree mismatch"
print("  R4 out-degree preservation verified.")

t0 = time.time()
R4_rho_best  = np.full(N_R4, np.nan)
R4_alpha_r   = np.full(N_R4, np.nan)
R4_alpha_d   = np.full(N_R4, np.nan)

for k, P_r4n in enumerate(P_r4_norm_list):
    surf = np.full((GRID_N, GRID_N), np.nan)
    for i, ar in enumerate(alpha_grid):
        for j, ad in enumerate(alpha_grid):
            surf[i, j] = spearman_obj_global(ar, ad, J_base, P_r4n)
    best = int(np.nanargmax(surf))
    bi, bj = np.unravel_index(best, surf.shape)
    ar0, ad0 = alpha_grid[bi], alpha_grid[bj]

    def neg_r4(params, _Prn=P_r4n):
        v = spearman_obj_global(params[0], params[1], J_base, _Prn)
        return -v if not np.isnan(v) else 1.0

    res = optimize.minimize(neg_r4, [ar0, ad0], method="Nelder-Mead",
                            options={"maxiter": 500, "xatol": 1e-4, "fatol": 1e-4})
    R4_rho_best[k] = float(-res.fun)
    R4_alpha_r[k]  = float(res.x[0])
    R4_alpha_d[k]  = float(res.x[1])
    if (k + 1) % 10 == 0:
        print(f"  {k+1}/{N_R4}  ({time.time()-t0:.0f}s)  "
              f"median ρ={np.nanmedian(R4_rho_best[:k+1]):.4f}  M1={rho_M1:.4f}")

R4_valid  = ~np.isnan(R4_rho_best)
R4_median = float(np.nanmedian(R4_rho_best))
R4_p95    = float(np.nanpercentile(R4_rho_best[R4_valid], 95))
R4_pval   = float((R4_rho_best[R4_valid] >= rho_M1).mean())
print(f"\n  R4 null: median={R4_median:.4f}, p95={R4_p95:.4f}")
print(f"  M1 ρ={rho_M1:.4f}  vs R4 p95={R4_p95:.4f}")
print(f"  Empirical p-value P(R4 ≥ M1): {R4_pval:.3f}")

np.save(OUT_REV / "r4_rho_distribution.npy", R4_rho_best)
np.save(OUT_REV / "r4_alpha.npy", np.vstack([R4_alpha_r, R4_alpha_d]))

# =============================================================================
print("\n" + "="*70)
print("R5 — α sensitivity (∂ΔQ/∂α at fitted M1)")
print("="*70)

# Lyapunov sensitivity: differentiate J_s Σ_s + Σ_s J_s^T = -I w.r.t. α_s
# → J_s (∂Σ_s/∂α_s) + (∂Σ_s/∂α_s) J_s^T = -(P Σ_s + Σ_s P^T)
# → ∂Q_s/∂α_s = -Q_s (∂Σ_s/∂α_s) Q_s

def alpha_sensitivity(J_eff: np.ndarray, P_m: np.ndarray,
                      Sig: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Compute ∂Q/∂α at given J_eff, P, Σ, Q."""
    rhs = -(P_m @ Sig + Sig @ P_m.T)
    rhs = (rhs + rhs.T) / 2
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dSig = linalg.solve_continuous_lyapunov(J_eff, rhs)
        dSig = (dSig + dSig.T) / 2
        dQ   = -(Q @ dSig @ Q)
        return (dQ + dQ.T) / 2
    except Exception:
        return np.zeros_like(Q)

J_r_fit = J_base + alpha_r_M1 * P_norm
J_d_fit = J_base + alpha_d_M1 * P_norm
Sig_r_fit = lyapunov(J_r_fit)
Sig_d_fit = lyapunov(J_d_fit)
assert Sig_r_fit is not None and Sig_d_fit is not None
Q_r_fit = np.linalg.inv(Sig_r_fit); Q_r_fit = (Q_r_fit + Q_r_fit.T) / 2
Q_d_fit = np.linalg.inv(Sig_d_fit); Q_d_fit = (Q_d_fit + Q_d_fit.T) / 2

# ∂ΔQ/∂α_r = ∂Q_r/∂α_r,   ∂ΔQ/∂α_d = -∂Q_d/∂α_d
dQ_r = alpha_sensitivity(J_r_fit, P_norm, Sig_r_fit, Q_r_fit)
dQ_d = alpha_sensitivity(J_d_fit, P_norm, Sig_d_fit, Q_d_fit)
dDQ_dAlphaR = dQ_r             # ∂ΔQ/∂α_r
dDQ_dAlphaD = -dQ_d            # ∂ΔQ/∂α_d

# Characterize sensitivity on PDF vs non-PDF Class 4 pairs
sens_r_c4  = np.abs(dDQ_dAlphaR[ii_c4, jj_c4])
sens_d_c4  = np.abs(dDQ_dAlphaD[ii_c4, jj_c4])
pdf_mask_c4 = np.array([(min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k])) in pdf_c4
                         for k in range(N_C4)])

mean_sens_r_pdf    = float(sens_r_c4[pdf_mask_c4].mean())
mean_sens_r_nonpdf = float(sens_r_c4[~pdf_mask_c4].mean())
mean_sens_d_pdf    = float(sens_d_c4[pdf_mask_c4].mean())
mean_sens_d_nonpdf = float(sens_d_c4[~pdf_mask_c4].mean())

print(f"  ∂ΔQ/∂α_r: mean PDF={mean_sens_r_pdf:.5f}  non-PDF={mean_sens_r_nonpdf:.5f}"
      f"  ratio={mean_sens_r_pdf/mean_sens_r_nonpdf:.2f}×")
print(f"  ∂ΔQ/∂α_d: mean PDF={mean_sens_d_pdf:.5f}  non-PDF={mean_sens_d_nonpdf:.5f}"
      f"  ratio={mean_sens_d_pdf/mean_sens_d_nonpdf:.2f}×")

# Frobenius norm ratio: sensitivity vs signal
dDQ_total = dDQ_dAlphaD  # Use dwell sensitivity (α_d more physically meaningful)
frob_sens = float(np.linalg.norm(dDQ_total[ii_c4, jj_c4]))
frob_DQ   = float(np.linalg.norm(DQ_M1[ii_c4, jj_c4]))
print(f"  ||∂ΔQ/∂α_d|| = {frob_sens:.4f}  ||ΔQ_M1|| = {frob_DQ:.4f}  ratio = {frob_sens/frob_DQ:.3f}")

# Sparsity of sensitivity matrix
nonzero_sens  = (np.abs(dDQ_total[ii_c4, jj_c4]) > 1e-8).sum()
print(f"  Nonzero sensitivity entries: {nonzero_sens}/{N_C4} ({100*nonzero_sens/N_C4:.1f}%)")

np.save(OUT_REV / "r5_dDQ_dAlphaR.npy", dDQ_dAlphaR)
np.save(OUT_REV / "r5_dDQ_dAlphaD.npy", dDQ_dAlphaD)

# =============================================================================
print("\n" + "="*70)
print("SUCCESS CRITERIA EVALUATION")
print("="*70)

# Pre-specified criteria:
# 1. M1 significantly exceeds degree-matched nulls (R4 p-value < 0.05)
# 2. PDF identity matters beyond degree structure (M1 > R4)
# 3. Top-pair overlap improves materially over zero (any R3 variant top-20 > 0)
# 4. Evidence ADEL evaluation would be informative

crit1_R4 = R4_pval < 0.05
crit2    = rho_M1 > R4_p95 + 0.01
crit3    = max(ov20_R3A, ov20_R3B, ov20_R3C or 0) > 0
top20_best = max(ov20_R3A, ov20_R3B, ov20_R3C or 0)

print(f"  Criterion 1 (M1 > degree-matched null): p-val={R4_pval:.3f}  →  {'PASS' if crit1_R4 else 'FAIL'}")
print(f"  Criterion 2 (PDF identity > degree):    margin={rho_M1-R4_p95:+.4f}  →  {'PASS' if crit2 else 'FAIL'}")
print(f"  Criterion 3 (top-20 overlap > 0):       best={top20_best}  →  {'PASS' if crit3 else 'FAIL'}")

# =============================================================================
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

results = {
    "date": "2026-06-03",
    "authorization": "Phase 3A.6",
    "R1_reference": {
        "rho_global": rho_R1, "auroc_pdf": auroc_R1,
        "top10_overlap": ov10_R1, "top20_overlap": ov20_R1,
        "alpha_r": alpha_r_M1, "alpha_d": alpha_d_M1,
    },
    "R2_pdf_local": {
        "alpha_r": ar_R2, "alpha_d": ad_R2,
        "rho_pdf_train": rho_R2_pdf,
        "rho_global_at_R2alpha": rho_R2_global,
        "auroc_pdf": auroc_R2,
        "top10_overlap": ov10_R2, "top20_overlap": ov20_R2,
        "rho_M1_at_pdf_obj": rho_M1_pdfonly,
        "delta_rho_pdf_R2_vs_R1": rho_R2_pdf - rho_M1_pdfonly,
    },
    "R3_sparse_forward": {
        "R3A_admm": {"rho": rho_R3A, "auroc": auroc_R3A, "nonzero": int(nonzero_R3A),
                     "top10": ov10_R3A, "top20": ov20_R3A, "top50": ov50_R3A, "top100": ov100_R3A},
        "R3B_density_threshold": {"rho": rho_R3B, "auroc": auroc_R3B,
                                   "top10": ov10_R3B, "top20": ov20_R3B, "top50": ov50_R3B},
        "R3C_admm_R2alpha": {"rho": rho_R3C, "auroc": auroc_R3C if rho_R3C else None,
                              "top10": ov10_R3C, "top20": ov20_R3C} if rho_R3C else None,
    },
    "R4_degree_control": {
        "n_rand": N_R4,
        "null_type": "source-out-degree-preserving target shuffle",
        "M1_rho": rho_M1,
        "R4_median_rho": R4_median,
        "R4_p95_rho": R4_p95,
        "empirical_pvalue": R4_pval,
    },
    "R5_sensitivity": {
        "mean_sens_alphaD_pdf_pairs": mean_sens_d_pdf,
        "mean_sens_alphaD_nonpdf":    mean_sens_d_nonpdf,
        "concentration_ratio_dwell":  mean_sens_d_pdf / mean_sens_d_nonpdf,
        "frob_sensitivity": frob_sens,
        "frob_DQ_M1":       frob_DQ,
        "leverage_ratio":   frob_sens / frob_DQ,
        "nonzero_sens_pct": float(nonzero_sens / N_C4),
    },
    "success_criteria": {
        "crit1_M1_exceeds_degree_null_R4": {"result": crit1_R4, "pval_R4": R4_pval},
        "crit2_pdf_identity_beyond_degree": {"result": crit2, "margin": rho_M1 - R4_p95},
        "crit3_top20_overlap_improved": {"result": crit3, "best_top20": top20_best},
        "any_criterion_passed": crit1_R4 or crit2 or crit3,
    },
}

with open(OUT_REV / "revision_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("  Saved: revision_results.json")
print()
print(">>> STOP CONDITION <<<")
print("Architecture revision complete. No held-out evaluation. No Phase 3B.")
