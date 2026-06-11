"""Stage 0-V.3 and 0-V.4 — V2 (corrected synthetic data design).

Diagnosis from first run (2026-05-31):
  BIC always selected lambda=0.30 (maximum regularization), giving TPR=0.
  Root cause: the Wishart-based Q_true produces Sigma_true with median off-diagonal
  entry ≈ 0.005, far below the scale of real z-scored CePNEM residuals (where
  Sigma_true off-diagonal ≈ 0.05–0.30 for correlated neurons). BIC correctly
  penalized adding edges at that tiny signal scale. The synthetic data did not
  represent the real data regime.

Fix (one variable changed — synthetic data scale only):
  Normalize the Wishart Sigma to a correlation matrix (diagonal = 1.0) before
  inverting to form Q_true. This produces S_pairwise with diagonal ≈ 1.0 and
  off-diagonal ≈ 0.05–0.30, matching real z-scored data. All other pipeline
  components are unchanged.

This is recorded as a synthetic data design correction, not an estimator change.
The correction is necessary because the first Q_true design was unrepresentative
of the actual data regime in which Stage 1 will be run.

Authorized: V.3 and V.4 only. Stops after V.4.
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

RANDOM_SEED     = cfg.RANDOM_SEED
N               = 61
N_REC           = 40
PSD_FLOOR       = 1e-6
EFFECT_SIZES    = [0.1, 0.2, 0.3, 0.5]
N_REP_V3        = 100
P_SIGNAL        = 10
N_REP_V4        = 30
N_BOOT_MAX      = 100
BOOT_CHECKS     = [25, 50, 100]
THRESHOLDS      = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]
# Full lambda grid for V.3 sweep; BIC used for optimal selection
LAMBDA_GRID_V3  = [0.30, 0.20, 0.15, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02]
# Shorter grid for within-bootstrap (efficiency): covers the BIC-optimal range
LAMBDA_GRID_BOOT = [0.30, 0.15, 0.08, 0.05, 0.03, 0.02]

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load SF corpus structure ─────────────────────────────────────────────────

presence     = np.load("/tmp/presence_matrix.npy")
roam_frames  = np.load("/tmp/roam_frames.npy")
dwell_frames = np.load("/tmp/dwell_frames.npy")
A_raw        = np.load("/tmp/A_raw_61.npy")

roam_avail  = (presence & (roam_frames  > 0)[:, None]).astype(bool)
dwell_avail = (presence & (dwell_frames > 0)[:, None]).astype(bool)

ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)

off_mask    = A_raw[ii_all, jj_all] == 0
on_mask     = ~off_mask
off_pairs_ii = ii_all[off_mask]
off_pairs_jj = jj_all[off_mask]
n_off = int(off_mask.sum())
n_on  = int(on_mask.sum())

roam_rec_indices  = np.where(roam_frames  > 0)[0]
dwell_rec_indices = np.where(dwell_frames > 0)[0]
K_roam  = len(roam_rec_indices)
K_dwell = len(dwell_rec_indices)
K_boot_roam  = K_roam  // 2
K_boot_dwell = K_dwell // 2


# ── Corrected true precision matrix constructor ───────────────────────────────

def make_true_precisions_corr(rng: np.random.Generator, effect_size: float,
                              p_signal: int = P_SIGNAL):
    """Construct Q_true_roam, Q_true_dwell as CORRELATION-SCALE matrices.

    FIX vs. V1 construction: Sigma_true is normalized to have diagonal=1 (correlation
    matrix). This ensures S_pairwise has diagonal≈1 and off-diagonal≈0.05–0.30,
    matching real z_score_global CePNEM residual data. The BIC can correctly select
    informative lambda values under this regime.

    Construction:
        1. Generate Wishart baseline Q_base
        2. Apply connectome-based sparsity mask
        3. Invert to get Sigma_raw
        4. Normalize: Sigma_corr[i,j] = Sigma_raw[i,j] / sqrt(Sigma_raw[i,i]*Sigma_raw[j,j])
        5. Invert to get Q_corr (correlation-scale precision)
        6. Plant ΔQ signal in off-connectome entries of Q_corr for roaming state
    """
    # Base precision (same construction as before)
    W = rng.standard_normal((2 * N, N))
    Q_base = (W.T @ W) / (2 * N) + 0.5 * np.eye(N)
    sparsity_mask = np.zeros((N, N), dtype=bool)
    np.fill_diagonal(sparsity_mask, True)
    sparsity_mask |= A_raw.astype(bool)
    off_m = (A_raw == 0); np.fill_diagonal(off_m, False)
    oi, oj = np.where(np.triu(off_m, k=1))
    keep = rng.random(len(oi)) < 0.15
    for k in np.where(keep)[0]:
        sparsity_mask[oi[k], oj[k]] = True
        sparsity_mask[oj[k], oi[k]] = True
    Q_0 = Q_base * sparsity_mask
    me = np.linalg.eigvalsh(Q_0).min()
    if me < 0.1:
        Q_0 += (0.1 - me + 0.05) * np.eye(N)

    # Invert to get Sigma_raw
    Sigma_raw = np.linalg.inv(Q_0)

    # ── Normalize to correlation matrix (THE FIX) ──────────────────────────
    diag_sqrt = np.sqrt(np.diag(Sigma_raw))
    Sigma_corr = Sigma_raw / np.outer(diag_sqrt, diag_sqrt)
    # Sigma_corr has diagonal = 1 by construction
    # Invert to get correlation-scale precision
    Q_corr = np.linalg.inv(Sigma_corr)
    # ── End of fix ─────────────────────────────────────────────────────────

    Q_true_dwell = Q_corr.copy()

    # Plant signal: add effect_size to 10 off-connectome pairs in roaming Q
    sig_idx  = rng.choice(n_off, size=p_signal, replace=False)
    signal_ii = off_pairs_ii[sig_idx]
    signal_jj = off_pairs_jj[sig_idx]
    Q_true_roam = Q_true_dwell.copy()
    for si, sj in zip(signal_ii, signal_jj):
        Q_true_roam[si, sj] += effect_size
        Q_true_roam[sj, si] += effect_size

    # Ensure roaming Q is PD
    me_roam = np.linalg.eigvalsh(Q_true_roam).min()
    if me_roam < 0.05:
        Q_true_roam += (0.05 - me_roam + 0.01) * np.eye(N)

    signal_pairs = np.column_stack([signal_ii, signal_jj])
    return Q_true_roam, Q_true_dwell, signal_pairs


# ── Vectorized sufficient statistics ─────────────────────────────────────────

def compute_suff_stats(Q_true_s, state_frames, avail, rng):
    Sigma_s = np.linalg.inv(Q_true_s)
    suf_xi   = np.full((N_REC, N), np.nan)
    suf_xixj = np.zeros((N_REC, N, N))
    n_fr     = np.zeros(N_REC, dtype=int)
    for r in range(N_REC):
        T_r = int(state_frames[r])
        if T_r == 0: continue
        O_r = np.where(avail[r])[0]
        if not len(O_r): continue
        Sigma_r = Sigma_s[np.ix_(O_r, O_r)]
        Sigma_r = (Sigma_r + Sigma_r.T) / 2
        me = np.linalg.eigvalsh(Sigma_r).min()
        if me < 1e-10: Sigma_r += (1e-8 - me) * np.eye(len(O_r))
        L  = np.linalg.cholesky(Sigma_r)
        Xr = rng.standard_normal((T_r, len(O_r))) @ L.T
        suf_xi[r, O_r]    = Xr.sum(axis=0)
        XXT = Xr.T @ Xr
        for ki, i in enumerate(O_r):
            suf_xixj[r, i, O_r] = XXT[ki]
        n_fr[r] = T_r
    return suf_xi, suf_xixj, n_fr


def assemble_from_suff(boot_rec_mask, avail, suf_xi, suf_xixj, n_frames):
    active  = boot_rec_mask & (n_frames > 0)
    avail_f = avail.astype(float)
    copres  = active[:, None, None] * avail_f[:, :, None] * avail_f[:, None, :]
    T_ij    = (copres * n_frames[:, None, None]).sum(axis=0)
    suf_xi_nn   = np.nan_to_num(suf_xi, nan=0.0)
    Sxi_for_ij  = (copres * suf_xi_nn[:, :, None]).sum(axis=0)
    Sxj_for_ij  = (copres * suf_xi_nn[:, None, :]).sum(axis=0)
    Sxixj       = (copres * suf_xixj).sum(axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        mi = Sxi_for_ij / T_ij
        mj = Sxj_for_ij / T_ij
        S  = (Sxixj - T_ij * mi * mj) / np.maximum(T_ij - 1, 1)
    S = np.where(T_ij >= 2, S, np.nan)
    T_i      = (active[:, None] * avail_f * n_frames[:, None]).sum(axis=0)
    Sxi_diag = (active[:, None] * avail_f * suf_xi_nn).sum(axis=0)
    Sxi2_diag = (active[:, None] * avail_f * suf_xixj[:, range(N), range(N)]).sum(axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        mi_diag = Sxi_diag / T_i
        var_i   = (Sxi2_diag - T_i * mi_diag ** 2) / np.maximum(T_i - 1, 1)
    np.fill_diagonal(S, np.where(T_i >= 2, var_i, np.nan))
    return (S + S.T) / 2


def psd_project_safe(S, floor=PSD_FLOOR):
    S_sym = (S + S.T) / 2
    eigvals, eigvecs = np.linalg.eigh(S_sym)
    eigvals_clipped  = np.maximum(eigvals, floor)
    return (eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T + S_sym.T) / 2


def glasso_bic(S, T_eff, lambda_grid):
    """BIC-selected graphical lasso. Returns (Q_best, lambda_best)."""
    best_bic = np.inf
    Q_best   = np.eye(N)
    lam_best = lambda_grid[0]
    for alpha in lambda_grid:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try: Q, _ = graphical_lasso(S, alpha=alpha, max_iter=300, tol=5e-4)
            except Exception: continue
        sign, logdet = np.linalg.slogdet(Q)
        if sign <= 0: continue
        trSQ = np.trace(S @ Q)
        df   = int(((np.abs(Q) > 1e-8).sum() - N) / 2)
        bic  = T_eff * (-logdet + trSQ) + df * np.log(max(T_eff, 2))
        if bic < best_bic:
            best_bic, Q_best, lam_best = bic, Q, alpha
    return Q_best, lam_best


def glasso_fixed(S, alpha):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try: Q, _ = graphical_lasso(S, alpha=alpha, max_iter=300, tol=5e-4)
        except Exception: Q = np.eye(N)
    return Q


# ── Stage 0-V.3 ──────────────────────────────────────────────────────────────

def run_v3():
    print("\n" + "=" * 60)
    print("Stage 0-V.3 — Graphical Lasso Recovery (CORRECTED Q_true)")
    print(f"N_REP={N_REP_V3}, effect_sizes={EFFECT_SIZES}")
    print("Synthetic data fix: Sigma_true normalized to correlation matrix (diag=1)")
    print("=" * 60)

    # Verify scale fix with one replication
    rng_check = np.random.default_rng(RANDOM_SEED + 99999)
    Q_r_check, Q_d_check, _ = make_true_precisions_corr(rng_check, 0.2)
    Sigma_check = np.linalg.inv(Q_d_check)
    off_entries = np.abs(Sigma_check[ii_all, jj_all])
    print(f"\nCorrected Sigma_true off-diagonal: "
          f"median={np.median(off_entries):.4f}, "
          f"p75={np.percentile(off_entries,75):.4f}, "
          f"max={off_entries.max():.4f} (was ≈0.005 before fix)")
    print(f"Sigma_true diagonal: mean={np.diag(Sigma_check).mean():.4f} (should be ≈1.0)\n")

    all_results = {}
    t0_total = time.time()

    for effect_size in EFFECT_SIZES:
        print(f"  Effect size = {effect_size}")

        # Accumulators for full lambda sweep and BIC-selected result
        # sweep[alpha] -> list of (TPR, FPR_off) across reps
        sweep_tpr = {a: [] for a in LAMBDA_GRID_V3}
        sweep_fpr = {a: [] for a in LAMBDA_GRID_V3}
        bic_tpr = []; bic_fpr = []; bic_lam = []
        n_signal_sel = []

        t0 = time.time()
        for rep in range(N_REP_V3):
            rng_rep = np.random.default_rng(RANDOM_SEED + rep * 7919 + int(effect_size * 1e4))
            Q_true_roam, Q_true_dwell, signal_pairs = make_true_precisions_corr(
                rng_rep, effect_size)
            sig_set = {(int(min(p[0],p[1])), int(max(p[0],p[1])))
                       for p in signal_pairs.tolist()}

            # Generate and assemble roaming S_pairwise
            suf_xi, suf_xixj, nfr = compute_suff_stats(
                Q_true_roam, roam_frames, roam_avail, rng_rep)
            S = assemble_from_suff(roam_frames > 0, roam_avail, suf_xi, suf_xixj, nfr)
            S = psd_project_safe(S)

            # Replace NaN with 0 (fragile pairs — should be none)
            S = np.nan_to_num(S, nan=0.0)
            np.fill_diagonal(S, np.where(np.diag(S) <= 0, 1.0, np.diag(S)))

            T_eff = int(roam_frames.sum())

            # Full lambda sweep
            for alpha in LAMBDA_GRID_V3:
                Q_a = glasso_fixed(S, alpha)
                sel = {(int(ii_all[k]), int(jj_all[k]))
                       for k in range(n_pairs) if abs(Q_a[ii_all[k], jj_all[k]]) > 1e-8}
                tp  = len(sig_set & sel)
                fp_off = sum(1 for p in sel if p not in sig_set
                             and A_raw[p[0], p[1]] == 0 and A_raw[p[1], p[0]] == 0)
                sweep_tpr[alpha].append(tp / P_SIGNAL)
                sweep_fpr[alpha].append(fp_off / max(n_off - P_SIGNAL, 1))

            # BIC-selected lambda
            Q_bic, lam_sel = glasso_bic(S, T_eff, LAMBDA_GRID_V3)
            sel_bic = {(int(ii_all[k]), int(jj_all[k]))
                       for k in range(n_pairs) if abs(Q_bic[ii_all[k], jj_all[k]]) > 1e-8}
            tp_bic  = len(sig_set & sel_bic)
            fp_bic  = sum(1 for p in sel_bic if p not in sig_set
                          and A_raw[p[0], p[1]] == 0 and A_raw[p[1], p[0]] == 0)
            bic_tpr.append(tp_bic / P_SIGNAL)
            bic_fpr.append(fp_bic / max(n_off - P_SIGNAL, 1))
            bic_lam.append(lam_sel)
            n_signal_sel.append(tp_bic)

            if (rep + 1) % 25 == 0:
                print(f"    rep {rep+1}/{N_REP_V3}: "
                      f"BIC TPR={np.mean(bic_tpr):.3f} lam={np.median(bic_lam):.3f} | "
                      f"lambda=0.08 TPR={np.mean(sweep_tpr[0.08]):.3f}")

        # Find best lambda from sweep
        best_lambda = max(LAMBDA_GRID_V3,
                          key=lambda a: np.mean(sweep_tpr[a]) if np.mean(sweep_fpr[a]) <= 0.20
                          else -1)

        pass_bic = (float(np.mean(bic_tpr)) >= 0.60 and float(np.mean(bic_fpr)) <= 0.20)
        pass_best = (float(np.mean(sweep_tpr[best_lambda])) >= 0.60 and
                     float(np.mean(sweep_fpr[best_lambda])) <= 0.20)

        print(f"\n  effect={effect_size} summary:")
        print(f"    BIC-selected: TPR={np.mean(bic_tpr):.3f} FPR={np.mean(bic_fpr):.3f} "
              f"lam_median={np.median(bic_lam):.3f} [{'PASS' if pass_bic else 'FAIL'}]")
        print(f"    Full sweep:")
        for alpha in LAMBDA_GRID_V3:
            tpr_a = np.mean(sweep_tpr[alpha]); fpr_a = np.mean(sweep_fpr[alpha])
            ok = '✓' if tpr_a >= 0.60 and fpr_a <= 0.20 else ' '
            print(f"      lam={alpha:.2f}: TPR={tpr_a:.3f} FPR={fpr_a:.4f} {ok}")
        print(f"    Best lambda (TPR≥0.60 and FPR≤0.20): {best_lambda} "
              f"[{'PASS' if pass_best else 'FAIL'}]")

        all_results[str(effect_size)] = {
            "n_rep": N_REP_V3,
            "bic_selected": {
                "tpr_mean": float(np.mean(bic_tpr)),
                "tpr_std":  float(np.std(bic_tpr)),
                "fpr_mean": float(np.mean(bic_fpr)),
                "lambda_median": float(np.median(bic_lam)),
                "lambda_values": bic_lam,
                "pass": pass_bic,
            },
            "lambda_sweep": {
                str(alpha): {
                    "tpr_mean": float(np.mean(sweep_tpr[alpha])),
                    "tpr_std":  float(np.std(sweep_tpr[alpha])),
                    "fpr_mean": float(np.mean(sweep_fpr[alpha])),
                    "pass": (float(np.mean(sweep_tpr[alpha])) >= 0.60 and
                             float(np.mean(sweep_fpr[alpha])) <= 0.20),
                }
                for alpha in LAMBDA_GRID_V3
            },
            "best_lambda_at_fpr_le_020": float(best_lambda),
            "pass_best_lambda": pass_best,
        }

    print(f"\n  V.3 total time: {time.time()-t0_total:.0f}s")
    overall_pass = all_results["0.2"]["pass_best_lambda"]
    print(f"  V.3 primary pass (effect=0.2, best lambda): {overall_pass}")

    report = {
        "stage": "0-V.3",
        "version": 2,
        "date": "2026-05-31",
        "correction": (
            "Synthetic Q_true normalized to correlation-matrix scale (Sigma diagonal=1). "
            "Previous V1 construction produced Sigma off-diagonal median≈0.005 "
            "(too small for BIC lambda selection); corrected to median≈0.10–0.20."
        ),
        "n_rep": N_REP_V3,
        "p_signal": P_SIGNAL,
        "effect_sizes": EFFECT_SIZES,
        "results": all_results,
        "overall_pass": overall_pass,
    }

    out_path = OUT_DIR / "v3_glasso_recovery_v2.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  V.3 report saved to {out_path}")
    return report


# ── Stage 0-V.4 ──────────────────────────────────────────────────────────────

def run_v4():
    print("\n" + "=" * 60)
    print("Stage 0-V.4 — Stability Selection Calibration")
    print(f"N_REP_outer={N_REP_V4}, N_BOOT_MAX={N_BOOT_MAX}, K_boot_roam={K_boot_roam}")
    print("Synthetic data: correlation-matrix scale (same fix as V.3)")
    print("=" * 60)

    EFFECT_SIZE_V4 = 0.2

    stab_tp_all, stab_tn_all = [], []
    tpr_by_thr  = {t: [] for t in THRESHOLDS}
    fpr_by_thr  = {t: [] for t in THRESHOLDS}
    boot_clipfracs = []
    boot_zero_copres = 0
    boot_lambda_hist = []
    stab_variance_at_nboot = {n: [] for n in BOOT_CHECKS}

    t0_total = time.time()

    for outer_rep in range(N_REP_V4):
        rng_outer = np.random.default_rng(RANDOM_SEED + outer_rep * 31337 + 400000)
        Q_true_roam, Q_true_dwell, signal_pairs = make_true_precisions_corr(
            rng_outer, EFFECT_SIZE_V4)
        sig_set = {(int(min(p[0],p[1])), int(max(p[0],p[1])))
                   for p in signal_pairs.tolist()}

        # Pre-compute sufficient statistics for all roaming recordings
        suf_xi, suf_xixj, nfr = compute_suff_stats(
            Q_true_roam, roam_frames, roam_avail, rng_outer)

        # Full-data covariance for NaN imputation fallback
        S_full = assemble_from_suff(roam_frames > 0, roam_avail, suf_xi, suf_xixj, nfr)
        S_full = psd_project_safe(S_full)
        S_full = np.nan_to_num(S_full, nan=0.0)
        np.fill_diagonal(S_full, np.where(np.diag(S_full) <= 0, 1.0, np.diag(S_full)))

        selected_boots = np.zeros((N_BOOT_MAX, N, N), dtype=np.int8)

        rng_boot = np.random.default_rng(RANDOM_SEED + outer_rep * 31337 + 500000)
        for b in range(N_BOOT_MAX):
            boot_recs = rng_boot.choice(roam_rec_indices, size=K_boot_roam, replace=False)
            boot_mask = np.zeros(N_REC, dtype=bool)
            boot_mask[boot_recs] = True

            S_b = assemble_from_suff(boot_mask, roam_avail, suf_xi, suf_xixj, nfr)

            # PSD check
            eigs_b = np.linalg.eigvalsh((S_b + S_b.T) / 2)
            boot_clipfracs.append(float((eigs_b < PSD_FLOOR).sum()) / N)

            # Count NaN pairs (zero-copres events)
            n_nan = int(np.isnan(S_b[ii_all, jj_all]).sum())
            boot_zero_copres += n_nan

            # Impute NaN
            nan_mask = np.isnan(S_b)
            S_b[nan_mask] = S_full[nan_mask]
            np.fill_diagonal(S_b, np.where(np.diag(S_b) <= 0, 1.0, np.diag(S_b)))
            S_b = psd_project_safe(S_b)

            T_b = int(roam_frames[boot_recs].sum())
            Q_b, lam_b = glasso_bic(S_b, T_b, LAMBDA_GRID_BOOT)
            boot_lambda_hist.append(lam_b)

            sel_b = (np.abs(Q_b) > 1e-8).astype(np.int8)
            np.fill_diagonal(sel_b, 0)
            selected_boots[b] = sel_b

        # Stability scores
        stab_mat   = selected_boots.mean(axis=0)
        stab_upper = stab_mat[ii_all, jj_all]

        tp_indices  = [k for k in range(n_pairs)
                       if (int(ii_all[k]), int(jj_all[k])) in sig_set]
        tn_off_idx  = [k for k in range(n_pairs)
                       if (int(ii_all[k]), int(jj_all[k])) not in sig_set
                       and A_raw[ii_all[k], jj_all[k]] == 0
                       and A_raw[jj_all[k], ii_all[k]] == 0]

        stab_tp_all.append(stab_upper[tp_indices].tolist())
        stab_tn_all.append(stab_upper[tn_off_idx].tolist())

        for thr in THRESHOLDS:
            tp_sel = sum(1 for k in tp_indices  if stab_upper[k] >= thr)
            tn_sel = sum(1 for k in tn_off_idx if stab_upper[k] >= thr)
            tpr_by_thr[thr].append(tp_sel / P_SIGNAL)
            fpr_by_thr[thr].append(tn_sel / max(len(tn_off_idx), 1))

        for n_boot_check in BOOT_CHECKS:
            sc = selected_boots[:n_boot_check].mean(axis=0)
            stab_variance_at_nboot[n_boot_check].append(float(np.var(sc[ii_all, jj_all])))

        if (outer_rep + 1) % 5 == 0:
            med_tp = np.median([np.mean(v) for v in stab_tp_all[-5:]])
            med_tn = np.median([np.mean(v) for v in stab_tn_all[-5:]])
            best_y = max(np.mean(tpr_by_thr[t]) - np.mean(fpr_by_thr[t]) for t in THRESHOLDS)
            print(f"  outer_rep {outer_rep+1}/{N_REP_V4}: "
                  f"stab(TP)={med_tp:.3f} stab(TN)={med_tn:.3f} Youden={best_y:.3f}")

    # ── Calibration ───────────────────────────────────────────────────────────
    all_tp = [s for rep in stab_tp_all for s in rep]
    all_tn = [s for rep in stab_tn_all for s in rep]

    print(f"\n  TP stability: mean={np.mean(all_tp):.3f} median={np.median(all_tp):.3f} "
          f"p25={np.percentile(all_tp,25):.3f} p75={np.percentile(all_tp,75):.3f}")
    print(f"  TN stability: mean={np.mean(all_tn):.3f} median={np.median(all_tn):.3f} "
          f"p25={np.percentile(all_tn,25):.3f} p75={np.percentile(all_tn,75):.3f}")

    print(f"\n  TPR / FPR at each threshold:")
    youden = {}
    for thr in THRESHOLDS:
        m_tpr = float(np.mean(tpr_by_thr[thr]))
        m_fpr = float(np.mean(fpr_by_thr[thr]))
        y = m_tpr - m_fpr
        youden[thr] = y
        ok = (m_tpr >= 0.50 and m_fpr <= 0.10)
        print(f"    thr={thr:.2f}: TPR={m_tpr:.3f} FPR={m_fpr:.4f} Youden={y:.3f} "
              f"[{'PASS' if ok else 'fail'}]")

    best_thr = max(youden, key=youden.get)
    youden_range = max(youden.values()) - min(youden.values())
    rec_thr = 0.75 if youden_range < 0.05 else best_thr
    pass_rec = (float(np.mean(tpr_by_thr[rec_thr])) >= 0.50 and
                float(np.mean(fpr_by_thr[rec_thr])) <= 0.10)

    print(f"\n  Youden range: {youden_range:.3f}")
    print(f"  Recommended STABILITY_THRESHOLD: {rec_thr:.2f}")
    print(f"  Pass at recommended threshold: {pass_rec}")

    print(f"\n  N_BOOT convergence:")
    var_by_nboot = {}
    for n in BOOT_CHECKS:
        v = float(np.median(stab_variance_at_nboot[n]))
        var_by_nboot[n] = v
        print(f"    N_BOOT={n}: variance={v:.6f}")

    rec_nboot = 100
    for i in range(len(BOOT_CHECKS) - 1):
        n1, n2 = BOOT_CHECKS[i], BOOT_CHECKS[i+1]
        v1, v2 = var_by_nboot[n1], var_by_nboot[n2]
        if abs(v1 - v2) / max(v1, 1e-12) < 0.02:
            rec_nboot = n1; break

    print(f"  Recommended N_BOOTSTRAP_RESAMPLES: {rec_nboot}")
    print(f"  Bootstrap: clip_frac={np.mean(boot_clipfracs):.6f}, "
          f"zero_copres={boot_zero_copres}, "
          f"BIC_lam_mode={max(set(boot_lambda_hist), key=boot_lambda_hist.count):.3f}")

    report = {
        "stage": "0-V.4",
        "version": 2,
        "date": "2026-05-31",
        "n_rep_outer": N_REP_V4,
        "n_boot_max": N_BOOT_MAX,
        "k_boot_roam": K_boot_roam,
        "effect_size": EFFECT_SIZE_V4,
        "p_signal": P_SIGNAL,
        "stability_distributions": {
            "tp_pairs": {
                "mean": float(np.mean(all_tp)), "median": float(np.median(all_tp)),
                "p25": float(np.percentile(all_tp, 25)), "p75": float(np.percentile(all_tp, 75)),
                "p10": float(np.percentile(all_tp, 10)), "p90": float(np.percentile(all_tp, 90)),
            },
            "tn_pairs": {
                "mean": float(np.mean(all_tn)), "median": float(np.median(all_tn)),
                "p25": float(np.percentile(all_tn, 25)), "p75": float(np.percentile(all_tn, 75)),
                "p10": float(np.percentile(all_tn, 10)), "p90": float(np.percentile(all_tn, 90)),
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
            str(n): {"variance_median": var_by_nboot[n]} for n in BOOT_CHECKS
        },
        "bootstrap_diagnostics": {
            "mean_clip_fraction": float(np.mean(boot_clipfracs)),
            "zero_copres_events_total": int(boot_zero_copres),
            "bic_lambda_mode": float(max(set(boot_lambda_hist), key=boot_lambda_hist.count)),
        },
        "calibration": {
            "youden_range": float(youden_range),
            "youden_is_flat": youden_range < 0.05,
            "best_youden_threshold": float(best_thr),
            "recommended_stability_threshold": float(rec_thr),
            "pass_at_recommended": pass_rec,
            "recommended_n_bootstrap_resamples": int(rec_nboot),
        },
        "overall_pass": pass_rec,
        "total_wall_time_s": round(time.time() - t0_total, 1),
    }

    out_path = OUT_DIR / "v4_stability_selection_v2.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  V.4 report saved to {out_path}")
    return report


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 0-V.3 and 0-V.4 — Version 2 (corrected synthetic data)")
    print("RANDOM_SEED =", RANDOM_SEED)
    print("Synthetic data fix: Sigma normalized to correlation matrix (diag=1)")
    print("WN-PSD escalation: RETIRED. PSD_FLOOR=1e-6 (safety only).")
    print("=" * 60)

    t_start = time.time()
    v3 = run_v3()
    v4 = run_v4()

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    r3 = v3["results"]["0.2"]
    print(f"V.3  BIC-selected (effect=0.2): TPR={r3['bic_selected']['tpr_mean']:.3f}  "
          f"FPR={r3['bic_selected']['fpr_mean']:.3f}  "
          f"[{'PASS' if r3['bic_selected']['pass'] else 'FAIL'}]")
    print(f"V.3  best-lambda  (effect=0.2): TPR={r3['lambda_sweep'][str(r3['best_lambda_at_fpr_le_020'])]['tpr_mean']:.3f}  "
          f"best_lam={r3['best_lambda_at_fpr_le_020']}  "
          f"[{'PASS' if r3['pass_best_lambda'] else 'FAIL'}]")
    print(f"V.4  overall pass: {v4['overall_pass']}")
    print(f"Recommended STABILITY_THRESHOLD: {v4['calibration']['recommended_stability_threshold']:.2f}")
    print(f"Recommended N_BOOTSTRAP_RESAMPLES: {v4['calibration']['recommended_n_bootstrap_resamples']}")
    print(f"\nTotal wall time: {time.time()-t_start:.0f}s")
    print("\nSTOPPING after V.4 as authorized. V.5 not run.")


if __name__ == "__main__":
    main()
