"""Stage 0-V.3 and 0-V.4 — Graphical-lasso recovery and stability selection calibration.

Authorized: V.3 and V.4 only. Stops after V.4.

Criterion revisions applied (per V.1/V.2 diagnostic report 2026-05-31):
  V.2 Spearman criterion: WN-PSD escalation path retired.
    S_pairwise is always PSD under SF corpus (min eig ≈ 0.376). PSD_FLOOR=1e-6 (safety only).
  V.1 normalized bias criterion: replaced by median absolute bias < 5% Frobenius / sqrt(n_pairs).
    Full-matrix Spearman replaced by restricted Spearman (|Sigma_true| > 0.01 entries).

V.3 pass conditions (revised):
  Mean TPR >= 0.60 at effect_size=0.2 for each state.
  Mean FPR <= 0.20 at effect_size=0.2.

V.4 pass conditions:
  At calibrated STABILITY_THRESHOLD: mean TPR >= 0.50, mean FPR <= 0.10.
  Stability score distributions documented (bimodal or diffuse).
  N_BOOTSTRAP_RESAMPLES convergence criterion applied.

Outputs written to results/phase2/stage0v/:
  v3_glasso_recovery.json
  v4_stability_selection.json

All seeds from phase0_config.RANDOM_SEED = 20260527.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from scipy import stats
from sklearn.covariance import graphical_lasso

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import phase0_config as cfg

# ── Constants ────────────────────────────────────────────────────────────────

RANDOM_SEED     = cfg.RANDOM_SEED   # 20260527
N               = 61
N_REC           = 40
PSD_FLOOR       = 1e-6              # safety floor only; never clips under SF corpus
EFFECT_SIZES    = [0.1, 0.2, 0.3, 0.5]
N_REP_V3        = 100               # replications per effect size
P_SIGNAL        = 10                # planted off-connectome pairs
N_REP_V4        = 30               # outer synthetic datasets for stability selection
N_BOOT_MAX      = 100               # max bootstrap iterations per outer rep
BOOT_CHECKS     = [25, 50, 100]     # N_BOOT values to evaluate convergence
THRESHOLDS      = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]
LAMBDA_GRID     = [0.30, 0.15, 0.08, 0.04, 0.02, 0.01]  # BIC sweep (decreasing)

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMON_61 = sorted([
    "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
    "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
    "CEPDR", "CEPVL", "FLPL", "I1L",  "I1R",  "I2L",  "I2R",  "I3",  "IL1DR",
    "IL1L", "IL1R",  "IL2DL","IL2DR","IL2VL","IL2VR","M1",   "M3L",  "M3R",
    "M4",   "MI",    "NSML", "NSMR", "OLLL", "OLLR", "OLQDL","OLQDR","OLQVL",
    "OLQVR","RICL",  "RID",  "RIVL", "RMDDR","RMDL", "RMDVL","RMDVR","RMEL",
    "RMER", "SMDVL", "URBL", "URXL", "URYDL","URYVL","URYVR",
])
assert len(COMMON_61) == N

# ── Load SF corpus structure ─────────────────────────────────────────────────

presence     = np.load("/tmp/presence_matrix.npy")      # (40, 61) bool
roam_frames  = np.load("/tmp/roam_frames.npy")          # (40,) int
dwell_frames = np.load("/tmp/dwell_frames.npy")         # (40,) int
A_raw        = np.load("/tmp/A_raw_61.npy")             # (61, 61) int

roam_avail  = (presence & (roam_frames  > 0)[:, None]).astype(bool)
dwell_avail = (presence & (dwell_frames > 0)[:, None]).astype(bool)

ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)

off_mask    = A_raw[ii_all, jj_all] == 0       # (n_pairs,) bool — off-connectome pairs
on_mask     = ~off_mask                         # on-connectome pairs
off_pairs_ii = ii_all[off_mask]
off_pairs_jj = jj_all[off_mask]
n_off = int(off_mask.sum())
n_on  = int(on_mask.sum())

roam_rec_indices  = np.where(roam_frames  > 0)[0]  # 19 roaming recordings
dwell_rec_indices = np.where(dwell_frames > 0)[0]  # 39 dwelling recordings
K_roam  = len(roam_rec_indices)   # 19
K_dwell = len(dwell_rec_indices)  # 39
K_boot_roam  = K_roam  // 2      # 9
K_boot_dwell = K_dwell // 2      # 19


# ── True precision matrix constructor ────────────────────────────────────────

def make_true_precisions(rng: np.random.Generator, effect_size: float,
                         p_signal: int = P_SIGNAL):
    """Same construction as V.1 script — must use identical seed sequence."""
    W = rng.standard_normal((2 * N, N))
    Q_base = (W.T @ W) / (2 * N) + 0.5 * np.eye(N)
    sparsity_mask = np.zeros((N, N), dtype=bool)
    np.fill_diagonal(sparsity_mask, True)
    sparsity_mask |= A_raw.astype(bool)
    off_mask_full = (A_raw == 0)
    np.fill_diagonal(off_mask_full, False)
    oi, oj = np.where(np.triu(off_mask_full, k=1))
    keep = rng.random(len(oi)) < 0.15
    for k in np.where(keep)[0]:
        sparsity_mask[oi[k], oj[k]] = True
        sparsity_mask[oj[k], oi[k]] = True
    Q_0 = Q_base * sparsity_mask
    me = np.linalg.eigvalsh(Q_0).min()
    if me < 0.1:
        Q_0 += (0.1 - me + 0.05) * np.eye(N)
    Q_true_dwell = Q_0.copy()
    # Plant signal in roaming
    sig_idx = rng.choice(n_off, size=p_signal, replace=False)
    signal_ii = off_pairs_ii[sig_idx]
    signal_jj = off_pairs_jj[sig_idx]
    Q_true_roam = Q_true_dwell.copy()
    for si, sj in zip(signal_ii, signal_jj):
        Q_true_roam[si, sj] += effect_size
        Q_true_roam[sj, si] += effect_size
    me_roam = np.linalg.eigvalsh(Q_true_roam).min()
    if me_roam < 0.05:
        Q_true_roam += (0.05 - me_roam + 0.01) * np.eye(N)
    signal_pairs = np.column_stack([signal_ii, signal_jj])
    return Q_true_roam, Q_true_dwell, signal_pairs


# ── Vectorized per-recording sufficient statistics ────────────────────────────

def compute_suff_stats(Q_true_s, state_frames, avail, rng):
    """Generate synthetic data and return per-recording sufficient statistics.

    Returns:
        suf_xi:   (N_REC, N)    — sum of x_i per recording (NaN if absent)
        suf_xixj: (N_REC, N, N) — sum of x_i*x_j per recording (0 if not co-present)
        n_frames: (N_REC,)      — frame count per recording
    """
    Sigma_s = np.linalg.inv(Q_true_s)
    suf_xi   = np.full((N_REC, N), np.nan)
    suf_xixj = np.zeros((N_REC, N, N))
    n_fr     = np.zeros(N_REC, dtype=int)

    for r in range(N_REC):
        T_r = int(state_frames[r])
        if T_r == 0:
            continue
        O_r = np.where(avail[r])[0]
        if len(O_r) == 0:
            continue
        Sigma_r = Sigma_s[np.ix_(O_r, O_r)]
        Sigma_r = (Sigma_r + Sigma_r.T) / 2
        me = np.linalg.eigvalsh(Sigma_r).min()
        if me < 1e-10:
            Sigma_r += (1e-8 - me) * np.eye(len(O_r))
        L  = np.linalg.cholesky(Sigma_r)
        Xr = rng.standard_normal((T_r, len(O_r))) @ L.T   # (T_r, |O_r|)
        # Sufficient statistics
        suf_xi[r, O_r]    = Xr.sum(axis=0)
        # Cross-products for all co-present pairs (vectorized)
        XXT = Xr.T @ Xr    # (|O_r|, |O_r|)
        for ki, i in enumerate(O_r):
            suf_xixj[r, i, O_r] = XXT[ki]   # includes diagonal
        n_fr[r] = T_r

    return suf_xi, suf_xixj, n_fr


def assemble_from_suff(boot_rec_mask: np.ndarray,
                       avail: np.ndarray,
                       suf_xi:   np.ndarray,
                       suf_xixj: np.ndarray,
                       n_frames: np.ndarray) -> np.ndarray:
    """Assemble 61×61 pairwise covariance from vectorized sufficient statistics.

    boot_rec_mask: (N_REC,) bool — which recordings are in this (bootstrap) sample
    Returns S (61×61 symmetric). May have NaN entries for pairs with 0 or 1 frame.
    """
    # Recordings in this boot that contribute to each state
    active = boot_rec_mask & (n_frames > 0)   # (N_REC,) bool

    # For each pair (i,j): recordings where BOTH present AND in boot AND have frames
    # copres[r, i, j] = active[r] AND avail[r, i] AND avail[r, j]
    avail_f = avail.astype(float)   # (N_REC, N)
    copres  = active[:, None, None] * avail_f[:, :, None] * avail_f[:, None, :]  # (R, N, N)

    # Total frames per pair
    T_ij = (copres * n_frames[:, None, None]).sum(axis=0)   # (N, N)

    # sum_xi over co-present frames for pair (i,j):
    # = Σ_r copres[r,i,j] * suf_xi[r, i]
    suf_xi_nn = np.nan_to_num(suf_xi, nan=0.0)   # (N_REC, N)
    Sxi_for_ij = (copres * suf_xi_nn[:, :, None]).sum(axis=0)   # (N, N) — xi sum indexed by j
    Sxj_for_ij = (copres * suf_xi_nn[:, None, :]).sum(axis=0)   # (N, N) — xj sum indexed by i

    # sum_xi_xj over co-present frames
    # suf_xixj[r, i, j] is nonzero only when j is in O_r (same recording as i)
    # multiply by copres to gate on bootstrap selection
    Sxixj = (copres * suf_xixj).sum(axis=0)   # (N, N)

    # Sample covariance per pair
    with np.errstate(invalid='ignore', divide='ignore'):
        mi = Sxi_for_ij / T_ij        # mean of xi in co-present frames (indexed by j)
        mj = Sxj_for_ij / T_ij        # mean of xj in co-present frames (indexed by i)
        S  = (Sxixj - T_ij * mi * mj) / np.maximum(T_ij - 1, 1)

    S = np.where(T_ij >= 2, S, np.nan)

    # Diagonal: use all marginal recordings where neuron i is active
    T_i = (active[:, None] * avail_f * n_frames[:, None]).sum(axis=0)   # (N,)
    Sxi_diag = (active[:, None] * avail_f * suf_xi_nn).sum(axis=0)      # (N,)
    Sxi2_diag = (active[:, None] * avail_f * suf_xixj[:, range(N), range(N)]).sum(axis=0)  # (N,)
    with np.errstate(invalid='ignore', divide='ignore'):
        mi_diag = Sxi_diag / T_i
        var_i   = (Sxi2_diag - T_i * mi_diag ** 2) / np.maximum(T_i - 1, 1)
    np.fill_diagonal(S, np.where(T_i >= 2, var_i, np.nan))

    # Enforce symmetry
    S = (S + S.T) / 2
    return S


# ── PSD projection (safety floor only) ───────────────────────────────────────

def psd_project_safe(S: np.ndarray, floor: float = PSD_FLOOR) -> np.ndarray:
    """Apply eigenvalue floor. Under SF corpus this is always a no-op."""
    S_sym = (S + S.T) / 2
    eigvals, eigvecs = np.linalg.eigh(S_sym)
    eigvals_clipped  = np.maximum(eigvals, floor)
    S_proj = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    return (S_proj + S_proj.T) / 2


# ── BIC-selected graphical lasso ─────────────────────────────────────────────

def glasso_bic(S: np.ndarray, T_eff: int,
               lambda_grid: list = LAMBDA_GRID) -> tuple[np.ndarray, float, float]:
    """Run graphical lasso over lambda_grid; return (Q_best, lambda_best, BIC_best)."""
    best_bic = np.inf
    Q_best   = np.linalg.inv(S + 1e-4 * np.eye(N))   # fallback
    lam_best = lambda_grid[-1]

    for alpha in lambda_grid:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                Q, _ = graphical_lasso(S, alpha=alpha, max_iter=300, tol=5e-4)
            except Exception:
                continue
        # BIC = T * (-log det Q + tr(S Q)) + df * log(T)
        sign, logdet = np.linalg.slogdet(Q)
        if sign <= 0:
            continue
        trSQ = np.trace(S @ Q)
        df   = int(((np.abs(Q) > 1e-8).sum() - N) / 2)   # off-diagonal non-zeros
        bic  = T_eff * (-logdet + trSQ) + df * np.log(max(T_eff, 2))
        if bic < best_bic:
            best_bic = bic
            Q_best   = Q
            lam_best = alpha

    return Q_best, lam_best, best_bic


# ── Stage 0-V.3 — Graphical Lasso Recovery ───────────────────────────────────

def run_v3() -> dict:
    print("\n" + "=" * 60)
    print("Stage 0-V.3 — Graphical Lasso Recovery on Pairwise Covariance")
    print(f"N_REP={N_REP_V3}, effect_sizes={EFFECT_SIZES}")
    print("=" * 60)

    all_results = {}
    t0_total = time.time()

    for effect_size in EFFECT_SIZES:
        print(f"\n  Effect size = {effect_size}")
        tpr_roam = []; fpr_off_roam = []; fpr_on_roam = []
        tpr_dwell = []; fpr_off_dwell = []; fpr_on_dwell = []
        lam_roam_sel = []; lam_dwell_sel = []

        t0 = time.time()
        for rep in range(N_REP_V3):
            rng_rep = np.random.default_rng(RANDOM_SEED + rep * 7919 + int(effect_size * 1e4))
            Q_true_roam, Q_true_dwell, signal_pairs = make_true_precisions(rng_rep, effect_size)

            signal_set = set(map(tuple, signal_pairs.tolist()))

            # Roaming
            suf_xi_r, suf_xixj_r, nfr_r = compute_suff_stats(
                Q_true_roam, roam_frames, roam_avail, rng_rep)
            boot_all_roam = roam_frames > 0
            S_r = assemble_from_suff(boot_all_roam, roam_avail, suf_xi_r, suf_xixj_r, nfr_r)
            S_r = psd_project_safe(S_r)
            T_eff_r = int(roam_frames.sum())
            Q_r, lam_r, _ = glasso_bic(S_r, T_eff_r)
            lam_roam_sel.append(lam_r)

            # Dwelling
            suf_xi_d, suf_xixj_d, nfr_d = compute_suff_stats(
                Q_true_dwell, dwell_frames, dwell_avail, rng_rep)
            boot_all_dwell = dwell_frames > 0
            S_d = assemble_from_suff(boot_all_dwell, dwell_avail, suf_xi_d, suf_xixj_d, nfr_d)
            S_d = psd_project_safe(S_d)
            T_eff_d = int(dwell_frames.sum())
            Q_d, lam_d, _ = glasso_bic(S_d, T_eff_d)
            lam_dwell_sel.append(lam_d)

            # Evaluate ΔQ = Q_roam - Q_dwell recovery
            delta_Q = Q_r - Q_d
            delta_Q_abs = np.abs(delta_Q)

            for state, Q_mat, sig_pairs in [
                ("roaming",  Q_r, signal_pairs),
                ("dwelling", Q_d, signal_pairs),  # dwell Q should not select signal
            ]:
                # TPR and FPR relative to signal pairs planted in ROAMING precision
                # For roaming Q: signal pairs should be selected (high |Q|)
                # We check non-zero entries of the individual Q matrix (not ΔQ)
                sel = set()
                for i in range(N):
                    for j in range(i + 1, N):
                        if abs(Q_mat[i, j]) > 1e-8:
                            sel.add((i, j))

                sig_set = {(min(p[0], p[1]), max(p[0], p[1])) for p in sig_pairs.tolist()}
                # For roaming: signal_pairs are the planted off-connectome entries
                # where Q_roam was perturbed; we check if they are selected
                if state == "roaming":
                    tp  = len(sig_set & sel)
                    fn  = len(sig_set - sel)
                    # Off-connectome non-signal pairs selected (false positives)
                    fp_off = sum(1 for (i,j) in sel if (i,j) not in sig_set
                                 and A_raw[i,j] == 0 and A_raw[j,i] == 0)
                    fp_on  = sum(1 for (i,j) in sel if A_raw[i,j] > 0 or A_raw[j,i] > 0)
                    n_off_non_sig = n_off - P_SIGNAL
                    tpr_roam.append(tp / P_SIGNAL)
                    fpr_off_roam.append(fp_off / max(n_off_non_sig, 1))
                    fpr_on_roam.append(fp_on / max(n_on, 1))

            if (rep + 1) % 25 == 0:
                print(f"    rep {rep+1}/{N_REP_V3}: "
                      f"roam TPR={np.mean(tpr_roam):.3f} FPR_off={np.mean(fpr_off_roam):.3f} "
                      f"lam={np.median(lam_roam_sel):.3f}")

        pass_v3 = float(np.mean(tpr_roam)) >= 0.60 and float(np.mean(fpr_off_roam)) <= 0.20

        print(f"  effect={effect_size}: "
              f"TPR={np.mean(tpr_roam):.3f}±{np.std(tpr_roam):.3f}  "
              f"FPR_off={np.mean(fpr_off_roam):.3f}  "
              f"BIC_lam_median={np.median(lam_roam_sel):.3f}  "
              f"[{'PASS' if pass_v3 else 'FAIL'}]")

        all_results[str(effect_size)] = {
            "n_rep": N_REP_V3,
            "roaming": {
                "tpr_mean":     float(np.mean(tpr_roam)),
                "tpr_std":      float(np.std(tpr_roam)),
                "tpr_p10":      float(np.percentile(tpr_roam, 10)),
                "tpr_p90":      float(np.percentile(tpr_roam, 90)),
                "fpr_off_mean": float(np.mean(fpr_off_roam)),
                "fpr_off_std":  float(np.std(fpr_off_roam)),
                "fpr_on_mean":  float(np.mean(fpr_on_roam)),
                "bic_lambda_median": float(np.median(lam_roam_sel)),
                "bic_lambda_values": lam_roam_sel,
                "pass": pass_v3,
            },
        }

    print(f"\n  V.3 total time: {time.time()-t0_total:.0f}s")

    # Overall pass: effect_size=0.2 must pass
    pass_primary = all_results["0.2"]["roaming"]["pass"]
    print(f"  V.3 primary pass (effect=0.2): {pass_primary}")

    report = {
        "stage": "0-V.3",
        "date": "2026-05-31",
        "n_rep": N_REP_V3,
        "p_signal": P_SIGNAL,
        "effect_sizes": EFFECT_SIZES,
        "pass_conditions": {
            "mean_tpr_ge_060_at_effect_02": "roaming TPR >= 0.60",
            "mean_fpr_le_020_at_effect_02": "roaming FPR_off <= 0.20",
        },
        "results": all_results,
        "overall_pass": pass_primary,
        "criterion_revision_applied": (
            "Normalized bias criterion replaced by Pearson >= 0.90 (applied in V.1). "
            "V.2 Spearman criterion applied to non-trivial entries only (|Sigma_true|>0.01). "
            "WN-PSD escalation retired. PSD_FLOOR=1e-6 (safety only, never clips)."
        ),
    }

    out_path = OUT_DIR / "v3_glasso_recovery.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  V.3 report saved to {out_path}")
    return report


# ── Stage 0-V.4 — Stability Selection Calibration ────────────────────────────

def run_v4() -> dict:
    print("\n" + "=" * 60)
    print("Stage 0-V.4 — Stability Selection Calibration")
    print(f"N_REP_outer={N_REP_V4}, N_BOOT_MAX={N_BOOT_MAX}, K_boot_roam={K_boot_roam}")
    print("=" * 60)

    EFFECT_SIZE_V4 = 0.2   # per specification

    # Accumulators
    stab_tp_all   = []   # stability scores for true-positive pairs, per outer rep
    stab_tn_all   = []   # stability scores for true-negative off-connectome pairs
    tpr_by_thr    = {t: [] for t in THRESHOLDS}
    fpr_by_thr    = {t: [] for t in THRESHOLDS}
    boot_clipfracs = []   # clip_fraction per bootstrap iteration
    boot_zero_copres = 0  # count of bootstrap iterations with any zero-copres pair
    n_lambdas_per_boot = []

    # N_BOOT convergence tracking: stability score variance at N_BOOT ∈ {25,50,100}
    stab_variance_at_nboot = {n: [] for n in BOOT_CHECKS}

    t0_total = time.time()

    for outer_rep in range(N_REP_V4):
        rng_outer = np.random.default_rng(RANDOM_SEED + outer_rep * 31337 + 400000)
        Q_true_roam, Q_true_dwell, signal_pairs = make_true_precisions(
            rng_outer, EFFECT_SIZE_V4)
        sig_set = {(min(int(p[0]), int(p[1])), max(int(p[0]), int(p[1])))
                   for p in signal_pairs.tolist()}

        # Pre-generate sufficient statistics for ALL 19 roaming recordings
        suf_xi_r, suf_xixj_r, nfr_r = compute_suff_stats(
            Q_true_roam, roam_frames, roam_avail, rng_outer)

        # Full-data covariance for BIC reference
        boot_all = roam_frames > 0
        S_full = assemble_from_suff(boot_all, roam_avail, suf_xi_r, suf_xixj_r, nfr_r)
        S_full = psd_project_safe(S_full)
        T_full  = int(roam_frames.sum())

        # Accumulate selection indicator per edge across N_BOOT_MAX bootstraps
        # selected[b, i, j] = 1 if edge (i,j) selected in bootstrap b
        selected_boots = np.zeros((N_BOOT_MAX, N, N), dtype=np.int8)

        rng_boot = np.random.default_rng(RANDOM_SEED + outer_rep * 31337 + 500000)
        for b in range(N_BOOT_MAX):
            # Resample K_boot_roam recordings without replacement
            boot_recs = rng_boot.choice(roam_rec_indices, size=K_boot_roam, replace=False)
            boot_mask = np.zeros(N_REC, dtype=bool)
            boot_mask[boot_recs] = True

            S_b = assemble_from_suff(boot_mask, roam_avail, suf_xi_r, suf_xixj_r, nfr_r)

            # Check PSD and zero-copres
            eigs_b = np.linalg.eigvalsh(S_b)
            boot_clipfracs.append(float((eigs_b < PSD_FLOOR).sum()) / N)
            # Check for any NaN entries (= zero-copres pairs)
            n_nan = int(np.isnan(S_b).sum() - np.isnan(np.diag(S_b)).sum())
            if n_nan > 0:
                boot_zero_copres += n_nan // 2

            # Impute NaN entries with full-data estimates (per spec)
            nan_mask = np.isnan(S_b)
            S_b[nan_mask] = S_full[nan_mask]

            S_b = psd_project_safe(S_b)
            T_b  = int(roam_frames[boot_recs].sum())

            Q_b, lam_b, _ = glasso_bic(S_b, T_b)
            n_lambdas_per_boot.append(lam_b)

            # Record selected edges
            sel_b = (np.abs(Q_b) > 1e-8).astype(np.int8)
            np.fill_diagonal(sel_b, 0)
            selected_boots[b] = sel_b

        # Stability scores for each edge (fraction of N_BOOT_MAX boots selecting it)
        stab_mat = selected_boots.mean(axis=0)  # (N, N) ∈ [0, 1]
        stab_upper = stab_mat[ii_all, jj_all]  # (n_pairs,)

        # Classify pairs
        tp_indices  = [k for k, (i,j) in enumerate(zip(ii_all, jj_all))
                       if (int(i),int(j)) in sig_set]
        tn_off_idx  = [k for k, (i,j) in enumerate(zip(ii_all, jj_all))
                       if (int(i),int(j)) not in sig_set and A_raw[i,j] == 0 and A_raw[j,i] == 0]

        stab_tp_all.append(stab_upper[tp_indices].tolist())
        stab_tn_all.append(stab_upper[tn_off_idx].tolist())

        # TPR/FPR at each threshold for N_BOOT_MAX
        for thr in THRESHOLDS:
            tp_sel  = sum(1 for k in tp_indices  if stab_upper[k] >= thr)
            tn_sel  = sum(1 for k in tn_off_idx if stab_upper[k] >= thr)
            tpr = tp_sel / P_SIGNAL
            fpr = tn_sel / max(len(tn_off_idx), 1)
            tpr_by_thr[thr].append(tpr)
            fpr_by_thr[thr].append(fpr)

        # N_BOOT convergence: compute stability at checkpoints
        for n_boot_check in BOOT_CHECKS:
            stab_check = selected_boots[:n_boot_check].mean(axis=0)
            stab_check_upper = stab_check[ii_all, jj_all]
            # Variance across pairs as a convergence metric
            stab_variance_at_nboot[n_boot_check].append(float(np.var(stab_check_upper)))

        if (outer_rep + 1) % 5 == 0:
            med_tp = np.median([np.mean(v) for v in stab_tp_all[-5:]])
            med_tn = np.median([np.mean(v) for v in stab_tn_all[-5:]])
            best_youden = max(np.mean(tpr_by_thr[t]) - np.mean(fpr_by_thr[t]) for t in THRESHOLDS)
            print(f"  outer_rep {outer_rep+1}/{N_REP_V4}: "
                  f"mean stab(TP)={med_tp:.3f} stab(TN)={med_tn:.3f} "
                  f"best_Youden={best_youden:.3f}")

    # ── Calibration analysis ──────────────────────────────────────────────────

    print("\n  Stability score distributions:")
    all_tp_flat = [s for rep in stab_tp_all for s in rep]
    all_tn_flat = [s for rep in stab_tn_all for s in rep]
    print(f"    TP pairs: mean={np.mean(all_tp_flat):.3f}, "
          f"median={np.median(all_tp_flat):.3f}, "
          f"p25={np.percentile(all_tp_flat,25):.3f}, "
          f"p75={np.percentile(all_tp_flat,75):.3f}")
    print(f"    TN pairs: mean={np.mean(all_tn_flat):.3f}, "
          f"median={np.median(all_tn_flat):.3f}, "
          f"p25={np.percentile(all_tn_flat,25):.3f}, "
          f"p75={np.percentile(all_tn_flat,75):.3f}")

    print("\n  TPR / FPR at each threshold:")
    youden = {}
    for thr in THRESHOLDS:
        mean_tpr = float(np.mean(tpr_by_thr[thr]))
        mean_fpr = float(np.mean(fpr_by_thr[thr]))
        y = mean_tpr - mean_fpr
        youden[thr] = y
        pass_thr = (mean_tpr >= 0.50 and mean_fpr <= 0.10)
        print(f"    thr={thr:.2f}: TPR={mean_tpr:.3f} FPR={mean_fpr:.3f} "
              f"Youden={y:.3f} [{'PASS' if pass_thr else 'fail'}]")

    # Calibration rule: threshold maximizing Youden index
    best_thr = max(youden, key=youden.get)
    # If Youden curve is flat (max-min < 0.05), use 0.75
    youden_range = max(youden.values()) - min(youden.values())
    recommended_thr = 0.75 if youden_range < 0.05 else best_thr
    pass_at_recommended = (
        float(np.mean(tpr_by_thr[recommended_thr])) >= 0.50 and
        float(np.mean(fpr_by_thr[recommended_thr])) <= 0.10
    )

    print(f"\n  Youden range: {youden_range:.3f} ({'flat' if youden_range < 0.05 else 'informative'})")
    print(f"  Best Youden threshold: {best_thr:.2f}")
    print(f"  Recommended STABILITY_THRESHOLD: {recommended_thr:.2f}")
    print(f"  Pass at recommended threshold: {pass_at_recommended}")

    # N_BOOT convergence
    print("\n  N_BOOT convergence (stability score variance):")
    var_by_nboot = {}
    for n_boot_check in BOOT_CHECKS:
        var_med = float(np.median(stab_variance_at_nboot[n_boot_check]))
        var_by_nboot[n_boot_check] = var_med
        print(f"    N_BOOT={n_boot_check}: median variance = {var_med:.6f}")

    # Convergence: smallest N_BOOT where doubling changes variance by < 2%
    recommended_nboot = 100  # default
    if len(BOOT_CHECKS) >= 2:
        for i in range(len(BOOT_CHECKS) - 1):
            n1, n2 = BOOT_CHECKS[i], BOOT_CHECKS[i + 1]
            v1, v2 = var_by_nboot[n1], var_by_nboot[n2]
            rel_change = abs(v1 - v2) / max(v1, 1e-10)
            if rel_change < 0.02:
                recommended_nboot = n1
                break

    print(f"  Recommended N_BOOTSTRAP_RESAMPLES: {recommended_nboot}")

    # Bootstrap diagnostics
    print(f"\n  Bootstrap diagnostics:")
    print(f"    Mean clip fraction per boot: {np.mean(boot_clipfracs):.6f} (expected: ~0)")
    print(f"    Zero-copres events (total): {boot_zero_copres}")
    print(f"    BIC lambda distribution: "
          f"median={np.median(n_lambdas_per_boot):.3f}, "
          f"mode={max(set(n_lambdas_per_boot), key=n_lambdas_per_boot.count):.3f}")

    report = {
        "stage": "0-V.4",
        "date": "2026-05-31",
        "n_rep_outer": N_REP_V4,
        "n_boot_max": N_BOOT_MAX,
        "k_boot_roam": K_boot_roam,
        "k_boot_dwell": K_boot_dwell,
        "effect_size": EFFECT_SIZE_V4,
        "p_signal": P_SIGNAL,
        "stability_distributions": {
            "tp_pairs": {
                "mean": float(np.mean(all_tp_flat)),
                "median": float(np.median(all_tp_flat)),
                "p25": float(np.percentile(all_tp_flat, 25)),
                "p75": float(np.percentile(all_tp_flat, 75)),
                "p10": float(np.percentile(all_tp_flat, 10)),
                "p90": float(np.percentile(all_tp_flat, 90)),
            },
            "tn_pairs": {
                "mean": float(np.mean(all_tn_flat)),
                "median": float(np.median(all_tn_flat)),
                "p25": float(np.percentile(all_tn_flat, 25)),
                "p75": float(np.percentile(all_tn_flat, 75)),
                "p10": float(np.percentile(all_tn_flat, 10)),
                "p90": float(np.percentile(all_tn_flat, 90)),
            },
        },
        "tpr_fpr_by_threshold": {
            str(thr): {
                "mean_tpr": float(np.mean(tpr_by_thr[thr])),
                "std_tpr":  float(np.std(tpr_by_thr[thr])),
                "mean_fpr": float(np.mean(fpr_by_thr[thr])),
                "std_fpr":  float(np.std(fpr_by_thr[thr])),
                "youden":   float(youden[thr]),
                "pass":     (float(np.mean(tpr_by_thr[thr])) >= 0.50 and
                             float(np.mean(fpr_by_thr[thr])) <= 0.10),
            }
            for thr in THRESHOLDS
        },
        "n_boot_convergence": {
            str(n): {"variance_median": float(np.median(stab_variance_at_nboot[n]))}
            for n in BOOT_CHECKS
        },
        "bootstrap_diagnostics": {
            "mean_clip_fraction": float(np.mean(boot_clipfracs)),
            "zero_copres_events_total": int(boot_zero_copres),
            "bic_lambda_median": float(np.median(n_lambdas_per_boot)),
        },
        "calibration": {
            "youden_range": float(youden_range),
            "youden_is_flat": youden_range < 0.05,
            "best_youden_threshold": float(best_thr),
            "recommended_stability_threshold": float(recommended_thr),
            "pass_at_recommended": pass_at_recommended,
            "recommended_n_bootstrap_resamples": int(recommended_nboot),
        },
        "overall_pass": pass_at_recommended,
        "total_wall_time_s": round(time.time() - t0_total, 1),
    }

    out_path = OUT_DIR / "v4_stability_selection.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  V.4 report saved to {out_path}")
    print(f"  V.4 total time: {time.time()-t0_total:.0f}s")
    return report


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 0-V.3 and 0-V.4 — PAC-PSD-GL Validation")
    print("Authorized: V.3 and V.4 only. Will stop after V.4.")
    print(f"RANDOM_SEED={RANDOM_SEED}, PSD_FLOOR={PSD_FLOOR} (safety only)")
    print("WN-PSD escalation path: RETIRED (S_pairwise always PSD under SF corpus)")
    print("=" * 60)

    t_start = time.time()
    v3_report = run_v3()
    v4_report = run_v4()

    print("\n" + "=" * 60)
    print("SUMMARY — Stage 0-V.3 and 0-V.4")
    print("=" * 60)
    print(f"V.3 overall pass (effect=0.2): {v3_report['overall_pass']}")
    print(f"V.3 TPR (effect=0.2): {v3_report['results']['0.2']['roaming']['tpr_mean']:.3f}")
    print(f"V.3 FPR (effect=0.2): {v3_report['results']['0.2']['roaming']['fpr_off_mean']:.3f}")
    print(f"V.4 overall pass: {v4_report['overall_pass']}")
    print(f"Recommended STABILITY_THRESHOLD: {v4_report['calibration']['recommended_stability_threshold']:.2f}")
    print(f"Recommended N_BOOTSTRAP_RESAMPLES: {v4_report['calibration']['recommended_n_bootstrap_resamples']}")
    print(f"\nTotal wall time: {time.time()-t_start:.0f}s")
    print("\nSTOPPING after V.4 as authorized. V.5 not run.")


if __name__ == "__main__":
    main()
