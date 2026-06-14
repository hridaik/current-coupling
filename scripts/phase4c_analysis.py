"""Phase 4C — Multi-Timescale Structure Analysis.

Authorization: Phase 4C.

Central question: On what timescale do the observed structures (D, Q, Ω) exist?

C1: Multi-timescale diffusion D(Δτ) at Δτ = 1, 2, 5, 10, 20 frames
C2: Multi-timescale Ω(Δτ)
C3: Multi-timescale ΔQ comparison
C4: Track ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, RMEL–URYDL across timescales
C5: Latent-neuron diagnostic: Cov(Δx(t), Δx(t+k)) for k = 0, 1, 2, 5

PROHIBITIONS: No new model fitting. No held-out evaluation. No perturbation predictions.
Do NOT revisit Ω vs Q debates. Do NOT revisit information-limiting analysis.
Do NOT revisit coupling models.
"""
from __future__ import annotations
import csv, json, sys, warnings
from pathlib import Path
from unittest.mock import MagicMock

import h5py
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.stage06_neff_stationarity import segment, SAMPLING_HZ
from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.phase1.stage0_cepnem import build_label_maps
import phase0_config as p0cfg

OUT4C = ROOT / "results/phase4c"
OUT4C.mkdir(parents=True, exist_ok=True)

# ── Locked segmentation parameters ───────────────────────────────────────────
TAU   = p0cfg.EWMA_TIMESCALE_SECONDS
THR   = p0cfg.BEHAV_THRESHOLD
W_FR  = int(p0cfg.W_TRANS_SECONDS  * SAMPLING_HZ)
MB_FR = int(p0cfg.MIN_BOUT_SECONDS * SAMPLING_HZ)
H5_DIR  = ROOT / "data/atanas/AtanasKim-Cell2023"
RESID_DIR = ROOT / "results/phase1/data/cepnem_residuals"

# ── Metadata ──────────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS  = cop["neurons"]
REC_IDS  = cop["recording_ids"]
N        = len(NEURONS)
n2i      = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Load Phase 2 precision matrices ───────────────────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r + Q_r.T) / 2
Q_d = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d + Q_d.T) / 2
DQ  = Q_r - Q_d

# ── Class 4 pairs ──────────────────────────────────────────────────────────────
ranked_c4 = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))
DQ_c4  = DQ[ii_c4, jj_c4]

# ── Key pair indices ──────────────────────────────────────────────────────────
KEY_PAIRS = {
    "ADEL-URYVR": ("ADEL", "URYVR"),
    "ADEL-URYDL": ("ADEL", "URYDL"),
    "ADEL-RMEL":  ("ADEL", "RMEL"),
    "RMEL-URYDL": ("RMEL", "URYDL"),
}
key_idx = {}
for label, (a, b) in KEY_PAIRS.items():
    if a in n2i and b in n2i:
        i, j = n2i[a], n2i[b]
        key_idx[label] = (min(i,j), max(i,j))

TAUS = [1, 2, 5, 10, 20]

# =============================================================================
# CORE FUNCTION: Multi-lag state-conditioned diffusion
# =============================================================================

def compute_diffusion_lag(tau: int) -> dict[str, np.ndarray]:
    """Compute D(τ) = Cov(x(t+τ) - x(t) | state) pooled across recordings.

    State-conditioning: all frames t, t+1, ..., t+τ must be in the same state.
    Uses pairwise complete-case covariance (NaN-zeroing method from phase3d).
    """
    sum_xy = [np.zeros((N, N)), np.zeros((N, N))]
    sum_x  = [np.zeros((N, N)), np.zeros((N, N))]
    sum_y  = [np.zeros((N, N)), np.zeros((N, N))]
    cnt    = [np.zeros((N, N), dtype=np.float64), np.zeros((N, N), dtype=np.float64)]

    for rec_id in REC_IDS:
        h5_path = H5_DIR / f"{rec_id}-data.h5"
        npz_path = RESID_DIR / f"{rec_id}.npz"
        if not h5_path.exists() or not npz_path.exists():
            continue

        with h5py.File(h5_path, "r") as hf:
            v_raw = hf["behavior/velocity"][:]

        lbl_arr, _ = segment(v_raw, TAU, THR, W_FR, MB_FR)

        npz = np.load(npz_path)
        resid   = npz["residual"].astype(float)
        sub_lbl = list(npz["neuron_labels"])
        T_rec   = len(v_raw)
        X = np.full((T_rec, N), np.nan)
        for j, lbl in enumerate(sub_lbl):
            if lbl in n2i:
                X[:, n2i[lbl]] = resid[:, j]

        if T_rec <= tau:
            continue

        # Δx(t, τ) = x(t+τ) - x(t)
        dX = X[tau:, :] - X[:-tau, :]  # (T_rec - tau, N)

        # State label: all frames t..t+τ-1 must be in the same state
        # Efficient approach: for state s, need all τ consecutive frames same state
        # Build a "same-state run" indicator using sliding min over τ-window
        lbl_float = lbl_arr.astype(float)  # dwell=0, roam=1
        T_diff = T_rec - tau

        for s in [0, 1]:
            state_at_t = (lbl_arr[:T_rec] == s).astype(float)
            # All frames t, t+1, ..., t+tau must be state s
            # Use convolution: sum of indicator over [t, t+tau] == tau+1
            from numpy.lib.stride_tricks import sliding_window_view
            wins = sliding_window_view(state_at_t, window_shape=tau + 1)  # (T_diff, tau+1)
            all_same = (wins.sum(axis=1) == tau + 1)  # (T_diff,)

            dX_s = dX[all_same, :]
            if dX_s.shape[0] < 2:
                continue

            valid    = np.isfinite(dX_s).astype(np.float64)
            dX_clean = np.where(np.isfinite(dX_s), dX_s, 0.0)

            sum_xy[s] += dX_clean.T @ dX_clean
            sum_x[s]  += dX_clean.T @ valid
            sum_y[s]  += valid.T   @ dX_clean
            cnt[s]    += valid.T   @ valid

    result = {}
    for s, sname in [(0, "dwell"), (1, "roam")]:
        D = np.zeros((N, N))
        c = cnt[s]
        ok = c >= 2
        with np.errstate(invalid="ignore", divide="ignore"):
            e_xy = np.where(ok, sum_xy[s] / c, 0.0)
            e_x  = np.where(ok, sum_x[s]  / c, 0.0)
            e_y  = np.where(ok, sum_y[s]  / c, 0.0)
        D = np.where(ok, e_xy - e_x * e_y, 0.0)
        D = (D + D.T) / 2
        result[sname] = D
        result[f"{sname}_cnt"] = c
        diag = np.diag(D)
        print(f"  τ={tau:2d} {sname}: diag=[{diag.min():.4f},{diag.max():.4f}] "
              f"mean={diag.mean():.4f} n_frames_min={int(c.diagonal().min())}")
    return result


def compute_cross_innovation_lag(k: int) -> np.ndarray:
    """Compute Cov(Δx(t), Δx(t+k)) pooled across all states and recordings.

    For a Markov process, this should be ~0 for k >= 1.
    Nonzero cross-innovation covariance implies latent dynamics.
    """
    # Δx(t) = x(t+1) - x(t)
    # We compute E[Δx(t) Δx(t+k)^T] - E[Δx(t)] E[Δx(t+k)]^T
    # Simplified: pooled, all-state

    sum_xy = np.zeros((N, N))
    sum_x  = np.zeros((N,))
    sum_y  = np.zeros((N,))
    sum_xx = np.zeros((N,))
    sum_yy = np.zeros((N,))
    cnt_xy = np.zeros((N, N), dtype=np.float64)
    n_total = 0

    for rec_id in REC_IDS:
        h5_path  = H5_DIR / f"{rec_id}-data.h5"
        npz_path = RESID_DIR / f"{rec_id}.npz"
        if not h5_path.exists() or not npz_path.exists():
            continue

        with h5py.File(h5_path, "r") as hf:
            v_raw = hf["behavior/velocity"][:]

        npz    = np.load(npz_path)
        resid  = npz["residual"].astype(float)
        sub_lbl = list(npz["neuron_labels"])
        T_rec   = len(v_raw)
        X = np.full((T_rec, N), np.nan)
        for j, lbl in enumerate(sub_lbl):
            if lbl in n2i:
                X[:, n2i[lbl]] = resid[:, j]

        if T_rec <= k + 1:
            continue

        dX = np.diff(X, axis=0)  # (T-1, N)
        if dX.shape[0] <= k:
            continue

        # Δx(t) pairs: t vs t+k
        dX_t  = dX[:dX.shape[0] - k, :]     # (T-1-k, N)
        dX_tk = dX[k:,                 :]    # (T-1-k, N)

        valid_t  = np.isfinite(dX_t).astype(np.float64)
        valid_tk = np.isfinite(dX_tk).astype(np.float64)
        dX_t_c   = np.where(np.isfinite(dX_t),  dX_t,  0.0)
        dX_tk_c  = np.where(np.isfinite(dX_tk), dX_tk, 0.0)

        cnt_pair = valid_t.T @ valid_tk  # (N, N)
        sum_xy  += dX_t_c.T @ dX_tk_c
        cnt_xy  += cnt_pair

    ok = cnt_xy >= 2
    with np.errstate(invalid="ignore", divide="ignore"):
        C_cross = np.where(ok, sum_xy / cnt_xy, 0.0)
    return C_cross


# =============================================================================
# C1: Multi-timescale D(τ)
# =============================================================================
print("\n" + "="*70)
print("C1 — Multi-Timescale Diffusion D(τ)")

D_results = {}
for tau in TAUS:
    print(f"\n  Computing D(τ={tau})...")
    D_results[tau] = compute_diffusion_lag(tau)

# Save all D matrices
np.save(OUT4C / "D_cepnem_tau1_roam.npy",  D_results[1]["roam"])
np.save(OUT4C / "D_cepnem_tau1_dwell.npy", D_results[1]["dwell"])
for tau in TAUS:
    np.save(OUT4C / f"D_cepnem_tau{tau}_roam.npy",  D_results[tau]["roam"])
    np.save(OUT4C / f"D_cepnem_tau{tau}_dwell.npy", D_results[tau]["dwell"])

# ── C1 metrics ────────────────────────────────────────────────────────────────
c1_metrics = {}
DQ_c4_abs = np.abs(DQ_c4)

for tau in TAUS:
    Dr = D_results[tau]["roam"]
    Dd = D_results[tau]["dwell"]
    dD = Dr - Dd

    diag_r    = np.diag(Dr)
    diag_d    = np.diag(Dd)
    diag_dD   = np.diag(dD)
    dD_c4     = dD[ii_c4, jj_c4]
    dD_c4_abs = np.abs(dD_c4)

    # Diagonal scaling: mean variance vs τ
    # For a Markov process: diag_D(τ) ~ 2σ²(1 - exp(-τ/τ_corr)) ≈ 2σ²τ/τ_corr for small τ
    # Normalized: diag_D(τ)/τ should be ~constant for Markov
    diag_r_norm = diag_r / tau
    diag_d_norm = diag_d / tau

    # ΔD rank correlation with ΔQ on Class-4 pairs
    rho_dD_DQ, p_dD_DQ = stats.spearmanr(dD_c4_abs, DQ_c4_abs)

    # Diagonal rank reordering: ρ(diag_D_roam(τ), diag_D_roam(1))
    rho_diag_r, _ = stats.spearmanr(diag_r, np.diag(D_results[1]["roam"]))
    rho_diag_d, _ = stats.spearmanr(diag_d, np.diag(D_results[1]["dwell"]))
    rho_diag_rd, _ = stats.spearmanr(diag_r, diag_d)

    frob_dD = float(np.linalg.norm(dD, "fro"))
    frob_Dr = float(np.linalg.norm(Dr, "fro"))

    c1_metrics[tau] = {
        "diag_roam_mean": float(diag_r.mean()),
        "diag_dwell_mean": float(diag_d.mean()),
        "diag_roam_norm_mean": float(diag_r_norm.mean()),
        "diag_dwell_norm_mean": float(diag_d_norm.mean()),
        "diag_roam_cv": float(diag_r.std() / diag_r.mean()),
        "diag_dwell_cv": float(diag_d.std() / diag_d.mean()),
        "diag_delta_mean": float(diag_dD.mean()),
        "diag_delta_range": [float(diag_dD.min()), float(diag_dD.max())],
        "rho_diag_r_vs_tau1": float(rho_diag_r),
        "rho_diag_d_vs_tau1": float(rho_diag_d),
        "rho_diag_roam_dwell": float(rho_diag_rd),
        "frob_dD": frob_dD,
        "frob_Dr": frob_Dr,
        "rel_change": float(frob_dD / frob_Dr) if frob_Dr > 0 else 0.0,
        "rho_dD_DQ_c4": float(rho_dD_DQ),
        "p_dD_DQ_c4": float(p_dD_DQ),
    }

    print(f"\n  τ={tau:2d}:")
    print(f"    Diag D_roam mean={diag_r.mean():.4f}  norm/τ={diag_r_norm.mean():.4f}")
    print(f"    Diag D_dwell mean={diag_d.mean():.4f}  norm/τ={diag_d_norm.mean():.4f}")
    print(f"    ρ(diag_roam, diag_roam(τ=1))={rho_diag_r:.4f}")
    print(f"    ρ(diag_roam, diag_dwell)={rho_diag_rd:.4f}")
    print(f"    ||ΔD||_F/||D_roam||={frob_dD/frob_Dr:.4f}")
    print(f"    ρ(|ΔD|, |ΔQ|) on C4={rho_dD_DQ:.4f}  p={p_dD_DQ:.4f}")

# =============================================================================
# C2: Multi-timescale Ω(τ) = D(τ) @ Q
# =============================================================================
print("\n" + "="*70)
print("C2 — Multi-Timescale Ω(τ) = D(τ) @ Q")

c2_metrics = {}
for tau in TAUS:
    Dr = D_results[tau]["roam"]
    Dd = D_results[tau]["dwell"]

    # Ω(τ) components using τ=1 precision matrices (stationary organization)
    DO_r = Dr @ Q_r    # Ω_roam(τ)
    DO_d = Dd @ Q_d    # Ω_dwell(τ)
    dDO  = DO_r - DO_d  # ΔΩ(τ)

    # Antisymmetric part of each
    dDO_anti = (dDO - dDO.T) / 2  # antisymmetric component = "current" contribution

    # Rank correlation of |ΔΩ(τ)| vs |ΔQ| on Class-4
    dDO_c4  = dDO[ii_c4, jj_c4]
    rho_dO_DQ, p_dO_DQ = stats.spearmanr(np.abs(dDO_c4), DQ_c4_abs)

    # Rank correlation of ΔΩ(τ) vs ΔΩ(1)
    if tau == 1:
        dDO_tau1 = dDO.copy()
        dDO_tau1_c4 = dDO_c4.copy()

    if tau > 1:
        rho_dO_vs_1, _ = stats.spearmanr(np.abs(dDO_c4), np.abs(dDO_tau1_c4))
    else:
        rho_dO_vs_1 = 1.0

    c2_metrics[tau] = {
        "rho_dOmega_DQ_c4": float(rho_dO_DQ),
        "p_dOmega_DQ_c4": float(p_dO_DQ),
        "rho_dOmega_vs_tau1": float(rho_dO_vs_1),
        "frob_dOmega": float(np.linalg.norm(dDO, "fro")),
        "anti_frac": float(np.linalg.norm(dDO_anti, "fro") / max(np.linalg.norm(dDO, "fro"), 1e-12)),
    }

    print(f"\n  τ={tau:2d}: ρ(|ΔΩ|, |ΔQ|) on C4={rho_dO_DQ:.4f}  p={p_dO_DQ:.4f}")
    print(f"          ρ(|ΔΩ(τ)|, |ΔΩ(1)|) on C4={rho_dO_vs_1:.4f}")
    print(f"          ||ΔΩ||_F={np.linalg.norm(dDO,'fro'):.4f}  anti_frac={c2_metrics[tau]['anti_frac']:.4f}")

# =============================================================================
# C3: Multi-timescale ΔQ via normalized diffusion D(τ)/τ
# =============================================================================
print("\n" + "="*70)
print("C3 — Multi-Timescale ΔQ Comparison: D(τ)/τ Structure")

c3_metrics = {}

# Approach: compute Spearman rank correlation of ΔD(τ)/τ with ΔQ on Class-4 pairs
# For a Markov process, D(τ)/τ → 2Σ as τ→∞. ΔQ and ΔΣ are related by ΔΣ ≈ -Σ_r ΔQ Σ_d
# Track whether pair rankings change as τ increases

# Normalized ΔD at each τ
for tau in TAUS:
    Dr = D_results[tau]["roam"]
    Dd = D_results[tau]["dwell"]
    dD_norm = (Dr - Dd) / tau  # normalize by lag

    dD_norm_c4 = dD_norm[ii_c4, jj_c4]
    rho, p = stats.spearmanr(np.abs(dD_norm_c4), DQ_c4_abs)

    # Rank stability relative to τ=1
    dD_norm_tau1_c4 = (D_results[1]["roam"] - D_results[1]["dwell"])[ii_c4, jj_c4]
    rho_vs_1, _ = stats.spearmanr(np.abs(dD_norm_c4), np.abs(dD_norm_tau1_c4))

    # Top-20 pair overlap between τ=1 and this τ
    rank_c4_tau1 = np.argsort(-np.abs(dD_norm_tau1_c4))[:20]
    rank_c4_tau  = np.argsort(-np.abs(dD_norm_c4))[:20]
    overlap_20 = len(set(rank_c4_tau1) & set(rank_c4_tau))

    c3_metrics[tau] = {
        "rho_dDnorm_DQ": float(rho),
        "p_dDnorm_DQ": float(p),
        "rho_dDnorm_vs_tau1": float(rho_vs_1),
        "top20_overlap_vs_tau1": int(overlap_20),
        "diag_Dr_norm_mean": float(np.diag(Dr).mean() / tau),
        "diag_Dd_norm_mean": float(np.diag(Dd).mean() / tau),
    }

    print(f"\n  τ={tau:2d}: ρ(|ΔD/τ|, |ΔQ|) on C4={rho:.4f}  p={p:.4f}")
    print(f"          ρ(|ΔD(τ)/τ|, |ΔD(1)|) on C4={rho_vs_1:.4f}")
    print(f"          Top-20 pair overlap with τ=1: {overlap_20}/20")
    print(f"          Diag D_roam/τ={np.diag(Dr).mean()/tau:.4f}  diag D_dwell/τ={np.diag(Dd).mean()/tau:.4f}")

# =============================================================================
# C4: Track key pairs across timescales
# =============================================================================
print("\n" + "="*70)
print("C4 — Key Pair Timescale Profiles")

c4_pair_data = {label: {} for label in KEY_PAIRS}

for tau in TAUS:
    Dr = D_results[tau]["roam"]
    Dd = D_results[tau]["dwell"]
    dD = Dr - Dd

    # Also compute ΔΩ(τ) for pair-level
    dDO = Dr @ Q_r - Dd @ Q_d

    for label, (a_name, b_name) in KEY_PAIRS.items():
        if label not in key_idx:
            continue
        i, j = key_idx[label]

        d_roam  = float(Dr[i, j])
        d_dwell = float(Dd[i, j])
        dd      = float(dD[i, j])
        do      = float(dDO[i, j])
        dq_val  = float(DQ[i, j])

        # Rank of |ΔD(τ)| among all C4 pairs
        dd_c4     = np.abs(dD[ii_c4, jj_c4])
        if (i, j) in c4_set:
            pair_c4_idx = list(zip(map(int,ii_c4),map(int,jj_c4))).index((i,j))
            rank_dd = int(np.sum(dd_c4 > np.abs(dd))) + 1
        else:
            pair_c4_idx = None
            rank_dd = None

        c4_pair_data[label][tau] = {
            "D_roam_ij": d_roam,
            "D_dwell_ij": d_dwell,
            "deltaD_ij": dd,
            "deltaOmega_ij": do,
            "deltaQ_ij": dq_val,
            "rank_deltaD_among_c4": rank_dd,
        }

        print(f"  τ={tau:2d} {label}: D_r={d_roam:.4f} D_d={d_dwell:.4f} "
              f"ΔD={dd:.4f} ΔΩ={do:.4f} (ΔQ={dq_val:.4f})")

# =============================================================================
# C5: Latent-neuron diagnostic Cov(Δx(t), Δx(t+k))
# =============================================================================
print("\n" + "="*70)
print("C5 — Latent-State Diagnostic: Cross-Innovation Covariance")

LAG_LIST = [0, 1, 2, 5]
cross_cov = {}
for k in LAG_LIST:
    print(f"  Computing cross-innovation covariance at lag k={k}...")
    cross_cov[k] = compute_cross_innovation_lag(k)
    np.save(OUT4C / f"cross_innov_lag{k}.npy", cross_cov[k])

c5_metrics = {}
C0 = cross_cov[0]  # auto-covariance (= D at τ=1, pooled over states)
diag_C0 = np.diag(C0)
C0_diag_safe = np.where(diag_C0 > 0, diag_C0, 1.0)

for k in LAG_LIST:
    Ck = cross_cov[k]

    # Off-diagonal elements give the cross-innovation structure
    off_diag_Ck = Ck[ii_all, jj_all]
    off_diag_C0 = C0[ii_all, jj_all]

    # Normalized cross-lag: C(k)[i,j] / sqrt(C(0)[i,i] * C(0)[j,j])
    denom = np.outer(np.sqrt(np.abs(diag_C0)), np.sqrt(np.abs(diag_C0)))
    denom[denom == 0] = 1.0
    Ck_norm = Ck / denom

    # Frobenius norm of off-diagonal cross-innovation relative to C(0)
    frob_Ck_off = float(np.linalg.norm(Ck[ii_all, jj_all]))
    frob_C0_off = float(np.linalg.norm(C0[ii_all, jj_all]))
    rel_off = frob_Ck_off / frob_C0_off if frob_C0_off > 0 else 0.0

    # Diagonal autocorrelation: C(k)[i,i] / C(0)[i,i]
    diag_Ck = np.diag(Ck)
    diag_autocorr = diag_Ck / C0_diag_safe  # per-neuron autocorrelation at lag k
    mean_diag_autocorr = float(diag_autocorr.mean())
    frac_nonzero_diag  = float((np.abs(diag_autocorr) > 0.05).mean())

    # Rank correlation of |C(k)| with |C(0)| on all pairs
    rho_Ck_C0, _ = stats.spearmanr(np.abs(off_diag_Ck), np.abs(off_diag_C0))

    # Rank correlation of |C(k)| with |ΔQ| on Class-4
    Ck_c4 = np.abs(Ck[ii_c4, jj_c4])
    rho_Ck_DQ, p_Ck_DQ = stats.spearmanr(Ck_c4, DQ_c4_abs)

    c5_metrics[k] = {
        "frob_off_diag_abs": frob_Ck_off,
        "rel_to_C0": rel_off,
        "mean_diag_autocorr": mean_diag_autocorr,
        "frac_diag_autocorr_gt05": frac_nonzero_diag,
        "rho_Ck_vs_C0": float(rho_Ck_C0),
        "rho_Ck_DQ_c4": float(rho_Ck_DQ),
        "p_Ck_DQ_c4": float(p_Ck_DQ),
    }

    print(f"  k={k}: ||C(k)_off||_F / ||C(0)_off||_F = {rel_off:.4f}")
    print(f"         Mean diag autocorr = {mean_diag_autocorr:.4f}  "
          f"frac(|r|>0.05) = {frac_nonzero_diag:.4f}")
    print(f"         ρ(|C(k)|, |C(0)|) = {rho_Ck_C0:.4f}")
    print(f"         ρ(|C(k)|, |ΔQ|) on C4 = {rho_Ck_DQ:.4f}  p={p_Ck_DQ:.4f}")

# =============================================================================
# Save results JSON
# =============================================================================
results = {
    "c1_diffusion_timescale": c1_metrics,
    "c2_omega_timescale": c2_metrics,
    "c3_precision_timescale": c3_metrics,
    "c4_pair_profiles": c4_pair_data,
    "c5_latent_diagnostic": c5_metrics,
    "metadata": {
        "taus": TAUS,
        "lag_list": LAG_LIST,
        "N_neurons": N,
        "N_recordings": len(REC_IDS),
        "N_class4": N_C4,
    }
}

# Convert dict keys to strings for JSON serialization
def jsonify(obj):
    if isinstance(obj, dict):
        return {str(k): jsonify(v) for k, v in obj.items()}
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

with open(OUT4C / "phase4c_results.json", "w") as f:
    json.dump(jsonify(results), f, indent=2)

print("\n" + "="*70)
print("Phase 4C numeric results saved to results/phase4c/phase4c_results.json")
print("="*70)
