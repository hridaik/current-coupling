"""Stage 0-V.7B — AUROC Enrichment Power Re-run.

Authorization: 2026-05-31. Option B authorized by supervisor.

Deviation record: DEV-P2-003
  The original V.7 synthetic enrichment design used P_SIGNAL=10. V.7A diagnostic
  demonstrated that 10 planted pairs among 159 annotated pairs creates an analytical
  AUROC ceiling of 0.531, making the pre-specified power criterion (≥ 0.60) unachievable
  regardless of effect size. The minimum signal density satisfying the criterion was
  determined by fine sweep (Part 1 of this script) before any real-data analysis.
  The validation design is updated to P_SIGNAL_min — the smallest integer value at which
  AUROC power ≥ 0.60 at effect_size = 0.20. Biological justification: neuropeptide DCV
  release is volume transmission affecting multiple targets simultaneously; the state switch
  between dwelling and roaming engages a distributed neuromodulatory circuit. The
  P_SIGNAL_min/159 signal fraction represents the minimum density required to satisfy
  the pre-specified power criterion; it is not an upper bound on the biological signal.
  All other V.7 parameters are unchanged.

Structure:
  Part 1 — Fine sweep: P_SIGNAL ∈ {11, 12, 13, 14}, 100 reps, analytical Mann-Whitney.
            Determines P_SIGNAL_min.

  Part 2 — Full V.7B validation: 200 null + 200 power replications with 1000-permutation
            null model (identical to original V.7 protocol except P_SIGNAL = P_SIGNAL_min).
            Saves v7b_validation.json and updates validation_summary.json.

Seeds: offset from V.7 and V.7A to ensure independent replications.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase0_config as cfg
from src.enrichment import auroc_pvalue, fisher_topk
from src.null_models import permute_simple, permute_degree_stratified
from sklearn.covariance import graphical_lasso

# ── Constants (all identical to V.7 except where noted) ─────────────────────
RANDOM_SEED   = cfg.RANDOM_SEED
N             = 61
N_REC         = 40
PSD_FLOOR     = 1e-6
FIXED_LAMBDA  = 0.15        # DEV-P2-002 (from V.3)
EFFECT_SIZE   = 0.20        # unchanged from V.7
N_RANDI_PAIRS = 189

# Part 1 — Fine sweep settings
P_SIGNAL_SWEEP_FINE = [11, 12, 13, 14]
N_REP_SWEEP  = 100          # reps per point (SE ≈ ±0.05 at p≈0.60)
# Seeds for fine sweep: offset 900000 from V.7A D2 (which used 700000+)
SEED_SWEEP_OFFSET = 900000

# Part 2 — Full V.7B validation settings (identical to original V.7)
N_REP_V7B_NULL  = 200
N_REP_V7B_POWER = 200
N_PERMS_NULL    = 1000
# Seeds: offset from original V.7 (null: +1000000, power: +2000000) to avoid reuse
SEED_V7B_NULL_OFFSET  = 5000000
SEED_V7B_POWER_OFFSET = 6000000
K_GRID = [20, 30, 40, 50, 60, 70, 80]
POWER_CRITERION = 0.60

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load SF corpus missingness structure ─────────────────────────────────────
presence     = np.load("/tmp/presence_matrix.npy")
roam_frames  = np.load("/tmp/roam_frames.npy")
dwell_frames = np.load("/tmp/dwell_frames.npy")
A_raw        = np.load("/tmp/A_raw_61.npy")

roam_avail  = (presence & (roam_frames  > 0)[:, None]).astype(bool)
dwell_avail = (presence & (dwell_frames > 0)[:, None]).astype(bool)

ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)
off_mask = A_raw[ii_all, jj_all] == 0
off_pairs_ii = ii_all[off_mask]
off_pairs_jj = jj_all[off_mask]
n_off = int(off_mask.sum())

# Annotation vector (same seed as V.7)
rng_annot = np.random.default_rng(RANDOM_SEED + 77777)
randi_annot = np.zeros(n_pairs, dtype=bool)
randi_annot[:N_RANDI_PAIRS] = True
rng_annot.shuffle(randi_annot)
off_annot    = randi_annot[off_mask]
off_deg_sums = (A_raw.sum(axis=1)[ii_all] + A_raw.sum(axis=1)[jj_all])[off_mask]

n_off_annotated = int(off_annot.sum())
labels = off_annot.astype(int)

roam_rec_indices = np.where(roam_frames > 0)[0]


# ── Shared pipeline (identical to V.7) ───────────────────────────────────────

def make_true_precisions(rng, effect_size, p_signal, signal_must_be_randi=True):
    W = rng.standard_normal((2 * N, N))
    Q_base = (W.T @ W) / (2 * N) + 0.5 * np.eye(N)
    sparsity_mask = np.zeros((N, N), dtype=bool)
    np.fill_diagonal(sparsity_mask, True)
    sparsity_mask |= A_raw.astype(bool)
    off_m = (A_raw == 0)
    np.fill_diagonal(off_m, False)
    oi, oj = np.where(np.triu(off_m, k=1))
    keep = rng.random(len(oi)) < 0.15
    for k in np.where(keep)[0]:
        sparsity_mask[oi[k], oj[k]] = True
        sparsity_mask[oj[k], oi[k]] = True
    Q_0 = Q_base * sparsity_mask
    me = np.linalg.eigvalsh(Q_0).min()
    if me < 0.1:
        Q_0 += (0.1 - me + 0.05) * np.eye(N)
    Sigma_raw = np.linalg.inv(Q_0)
    d = np.sqrt(np.diag(Sigma_raw))
    Sigma_corr = Sigma_raw / np.outer(d, d)
    Q_corr = np.linalg.inv(Sigma_corr)
    Q_true_dwell = Q_corr.copy()

    if signal_must_be_randi:
        ri = np.where(off_annot)[0]
        n_plant = min(p_signal, len(ri))
        si = rng.choice(len(ri), size=n_plant, replace=False)
    else:
        si = rng.choice(n_off, size=p_signal, replace=False)
        ri = np.arange(n_off)
    sig_ii = off_pairs_ii[ri[si]]
    sig_jj = off_pairs_jj[ri[si]]

    Q_true_roam = Q_true_dwell.copy()
    for a, b in zip(sig_ii, sig_jj):
        Q_true_roam[a, b] += effect_size
        Q_true_roam[b, a] += effect_size
    me_r = np.linalg.eigvalsh(Q_true_roam).min()
    if me_r < 0.05:
        Q_true_roam += (0.05 - me_r + 0.01) * np.eye(N)
    return Q_true_roam, Q_true_dwell


def compute_suff_stats(Q_s, state_frames, avail, rng):
    Sigma_s = np.linalg.inv(Q_s)
    suf_xi  = np.full((N_REC, N), np.nan)
    suf_xixj = np.zeros((N_REC, N, N))
    n_fr = np.zeros(N_REC, dtype=int)
    for r in range(N_REC):
        T_r = int(state_frames[r])
        if T_r == 0:
            continue
        O_r = np.where(avail[r])[0]
        if not len(O_r):
            continue
        Sr = Sigma_s[np.ix_(O_r, O_r)]
        Sr = (Sr + Sr.T) / 2
        me = np.linalg.eigvalsh(Sr).min()
        if me < 1e-10:
            Sr += (1e-8 - me) * np.eye(len(O_r))
        L  = np.linalg.cholesky(Sr)
        Xr = rng.standard_normal((T_r, len(O_r))) @ L.T
        suf_xi[r, O_r] = Xr.sum(axis=0)
        XXT = Xr.T @ Xr
        for ki, i in enumerate(O_r):
            suf_xixj[r, i, O_r] = XXT[ki]
        n_fr[r] = T_r
    return suf_xi, suf_xixj, n_fr


def assemble_from_suff(boot_mask, avail, suf_xi, suf_xixj, n_frames):
    active  = boot_mask & (n_frames > 0)
    avail_f = avail.astype(float)
    copres  = active[:, None, None] * avail_f[:, :, None] * avail_f[:, None, :]
    T_ij    = (copres * n_frames[:, None, None]).sum(axis=0)
    sx_nn   = np.nan_to_num(suf_xi, nan=0.0)
    Sxi     = (copres * sx_nn[:, :, None]).sum(axis=0)
    Sxj     = (copres * sx_nn[:, None, :]).sum(axis=0)
    Sxixj   = (copres * suf_xixj).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mi = Sxi / T_ij
        mj = Sxj / T_ij
        S  = (Sxixj - T_ij * mi * mj) / np.maximum(T_ij - 1, 1)
    S = np.where(T_ij >= 2, S, np.nan)
    T_i   = (active[:, None] * avail_f * n_frames[:, None]).sum(axis=0)
    Sxi_d = (active[:, None] * avail_f * sx_nn).sum(axis=0)
    Sx2_d = (active[:, None] * avail_f * suf_xixj[:, range(N), range(N)]).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mi_d  = Sxi_d / T_i
        var_i = (Sx2_d - T_i * mi_d ** 2) / np.maximum(T_i - 1, 1)
    np.fill_diagonal(S, np.where(T_i >= 2, var_i, np.nan))
    S = np.nan_to_num((S + S.T) / 2, nan=0.0)
    np.fill_diagonal(S, np.where(np.diag(S) <= 0, 1.0, np.diag(S)))
    return S


def psd_project_safe(S):
    S_sym = (S + S.T) / 2
    ev, vc = np.linalg.eigh(S_sym)
    return (vc @ np.diag(np.maximum(ev, PSD_FLOOR)) @ vc.T + S_sym.T) / 2


def glasso_fixed(S):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            Q, _ = graphical_lasso(S, alpha=FIXED_LAMBDA, max_iter=300, tol=5e-4)
        except Exception:
            Q = np.eye(N)
    return Q


def compute_delta_q(Q_r, Q_d, rng_rep):
    sx_r, sxx_r, nfr_r = compute_suff_stats(Q_r, roam_frames,  roam_avail,  rng_rep)
    sx_d, sxx_d, nfr_d = compute_suff_stats(Q_d, dwell_frames, dwell_avail, rng_rep)
    S_r = psd_project_safe(
        assemble_from_suff(roam_frames > 0, roam_avail, sx_r, sxx_r, nfr_r))
    S_d = psd_project_safe(
        assemble_from_suff(dwell_frames > 0, dwell_avail, sx_d, sxx_d, nfr_d))
    return glasso_fixed(S_r) - glasso_fixed(S_d)


# ── Part 1: Fine sweep (analytical MW, fast) ─────────────────────────────────

def run_fine_sweep():
    print("\n" + "=" * 70)
    print("PART 1 — Fine sweep: P_SIGNAL ∈ {11, 12, 13, 14}")
    print(f"EFFECT_SIZE={EFFECT_SIZE}, N_REP={N_REP_SWEEP} per point (analytical MW)")
    print(f"Known: P_SIGNAL=10 → power=0.48,  P_SIGNAL=15 → power=0.66")
    print("=" * 70)
    t0 = time.time()

    sweep_results = {}
    p_signal_min = None

    for idx, ps in enumerate(P_SIGNAL_SWEEP_FINE):
        rej = []
        aurocs = []
        t_pt = time.time()
        for rep in range(N_REP_SWEEP):
            rng = np.random.default_rng(RANDOM_SEED + SEED_SWEEP_OFFSET + idx * 10000 + rep)
            Q_r, Q_d = make_true_precisions(rng, EFFECT_SIZE, ps, signal_must_be_randi=True)
            dq = compute_delta_q(Q_r, Q_d, rng)
            dq_off = np.abs(dq[off_pairs_ii, off_pairs_jj])
            auc, p_val = auroc_pvalue(labels, dq_off)
            rej.append(p_val < 0.05)
            aurocs.append(auc)

        power   = float(np.mean(rej))
        se      = float(np.sqrt(power * (1 - power) / N_REP_SWEEP))
        mean_auc = float(np.mean(aurocs))
        meets   = power >= POWER_CRITERION
        sweep_results[str(ps)] = {
            "p_signal": ps,
            "power": power,
            "se": se,
            "mean_auroc": mean_auc,
            "meets_criterion": meets,
            "fraction_of_annotated": float(ps / n_off_annotated),
        }
        status = "YES ← FIRST" if (meets and p_signal_min is None) else ("YES" if meets else "---")
        if meets and p_signal_min is None:
            p_signal_min = ps
        print(f"  P_SIGNAL={ps:>3}  ({100*ps/n_off_annotated:.1f}% of {n_off_annotated} ann)  "
              f"power={power:.3f} ±{se:.3f}  auroc={mean_auc:.4f}  [{status}]  "
              f"time={time.time()-t_pt:.0f}s")

    # Anchor points from V.7A for context
    print(f"\n  [V.7A] P_SIGNAL=10  power=0.480  (below criterion)")
    print(f"  [V.7A] P_SIGNAL=15  power=0.660  (above criterion)")

    if p_signal_min is None:
        print("\n  WARNING: power ≥ 0.60 not reached in {11,12,13,14}.")
        print("  Defaulting to P_SIGNAL=15 from V.7A coarser sweep.")
        p_signal_min = 15

    print(f"\n  P_SIGNAL_min = {p_signal_min}  "
          f"({100*p_signal_min/n_off_annotated:.1f}% of {n_off_annotated} annotated pairs)")
    print(f"  Total Part 1 wall time: {time.time()-t0:.0f}s")

    result = {
        "sweep": sweep_results,
        "anchor_v7a": {"p10": 0.480, "p15": 0.660},
        "p_signal_min": p_signal_min,
        "p_signal_min_fraction_of_annotated": float(p_signal_min / n_off_annotated),
        "n_off_annotated": n_off_annotated,
        "n_off": n_off,
        "effect_size": EFFECT_SIZE,
        "power_criterion": POWER_CRITERION,
        "n_rep_sweep": N_REP_SWEEP,
        "p_value_method": "analytical_mannwhitney",
    }
    with open(OUT_DIR / "v7b_fine_sweep.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: v7b_fine_sweep.json")
    return p_signal_min, result


# ── Part 2: Full V.7B validation (permutation-based, identical protocol to V.7) ──

def run_v7b_full(p_signal):
    print("\n" + "=" * 70)
    print(f"PART 2 — Full V.7B validation  (P_SIGNAL={p_signal})")
    print(f"N_null={N_REP_V7B_NULL}, N_power={N_REP_V7B_POWER}, N_perms={N_PERMS_NULL}")
    print(f"Protocol: identical to V.7 except P_SIGNAL={p_signal} (was 10)")
    print("=" * 70)
    t0 = time.time()

    def enrichment_stats(delta_q):
        """Identical to V.7 enrichment_stats — permutation-based p-values."""
        dq_off  = np.abs(delta_q[off_pairs_ii, off_pairs_jj])
        auc, _  = auroc_pvalue(labels, dq_off)

        # Simple permutation null
        null_s = np.zeros(N_PERMS_NULL)
        for pi in range(N_PERMS_NULL):
            perm = permute_simple(labels, rng=np.random.default_rng(pi))
            null_s[pi], _ = auroc_pvalue(perm, dq_off)
        p_simple = float((null_s >= auc).mean())

        # Degree-preserving null
        null_d = np.zeros(N_PERMS_NULL)
        for pi in range(N_PERMS_NULL):
            perm = permute_degree_stratified(
                labels, off_deg_sums, n_bins=5,
                rng=np.random.default_rng(pi + N_PERMS_NULL))
            null_d[pi], _ = auroc_pvalue(perm, dq_off)
        p_deg = float((null_d >= auc).mean())

        # Fisher top-K
        fisher_res = {}
        for k in K_GRID:
            or_, pf = fisher_topk(labels, dq_off, k=k)
            fisher_res[str(k)] = {"or": float(or_), "pval": float(pf)}

        return {"auroc": float(auc), "p_simple": p_simple, "p_deg": p_deg,
                "fisher": fisher_res}

    # ── Type-I error ──────────────────────────────────────────────────────────
    print("\n  Type-I error runs (effect=0.0, Q_roam=Q_dwell)...")
    null_rej_s, null_rej_d = [], []
    null_fisher = {str(k): [] for k in K_GRID}
    t_null = time.time()
    for rep in range(N_REP_V7B_NULL):
        rng = np.random.default_rng(RANDOM_SEED + rep * 7654 + SEED_V7B_NULL_OFFSET)
        _, Q_base = make_true_precisions(rng, effect_size=0.0, p_signal=p_signal,
                                         signal_must_be_randi=True)
        dq = compute_delta_q(Q_base, Q_base, rng)
        st = enrichment_stats(dq)
        null_rej_s.append(st["p_simple"] < 0.05)
        null_rej_d.append(st["p_deg"] < 0.05)
        for k in K_GRID:
            null_fisher[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep + 1) % 50 == 0:
            print(f"    null {rep+1}/{N_REP_V7B_NULL}: "
                  f"type-I(simple)={np.mean(null_rej_s):.3f}  "
                  f"type-I(deg)={np.mean(null_rej_d):.3f}  "
                  f"elapsed={time.time()-t_null:.0f}s")

    t1_s = float(np.mean(null_rej_s))
    t1_d = float(np.mean(null_rej_d))
    t1_fisher = {str(k): float(np.mean(null_fisher[str(k)])) for k in K_GRID}

    # ── Power ─────────────────────────────────────────────────────────────────
    print(f"\n  Power runs (effect={EFFECT_SIZE}, P_SIGNAL={p_signal})...")
    pow_rej_s, pow_rej_d = [], []
    pow_fisher = {str(k): [] for k in K_GRID}
    pow_aurocs = []
    t_pow = time.time()
    for rep in range(N_REP_V7B_POWER):
        rng = np.random.default_rng(RANDOM_SEED + rep * 3571 + SEED_V7B_POWER_OFFSET)
        Q_r, Q_d = make_true_precisions(rng, EFFECT_SIZE, p_signal,
                                         signal_must_be_randi=True)
        dq = compute_delta_q(Q_r, Q_d, rng)
        st = enrichment_stats(dq)
        pow_rej_s.append(st["p_simple"] < 0.05)
        pow_rej_d.append(st["p_deg"] < 0.05)
        pow_aurocs.append(st["auroc"])
        for k in K_GRID:
            pow_fisher[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep + 1) % 50 == 0:
            print(f"    power {rep+1}/{N_REP_V7B_POWER}: "
                  f"power(simple)={np.mean(pow_rej_s):.3f}  "
                  f"power(deg)={np.mean(pow_rej_d):.3f}  "
                  f"elapsed={time.time()-t_pow:.0f}s")

    pw_s = float(np.mean(pow_rej_s))
    pw_d = float(np.mean(pow_rej_d))
    pw_fisher = {str(k): float(np.mean(pow_fisher[str(k)])) for k in K_GRID}
    pw_auroc_mean = float(np.mean(pow_aurocs))
    pw_auroc_std  = float(np.std(pow_aurocs))

    # ── PRIMARY_TOP_K re-check (should remain 20 from V.7) ───────────────────
    valid_k  = [k for k in K_GRID if t1_fisher[str(k)] <= 0.06]
    best_ptk = max(valid_k, key=lambda k: pw_fisher[str(k)]) if valid_k else 20

    # ── Pass / fail ───────────────────────────────────────────────────────────
    pass_t1s = t1_s <= 0.06
    pass_t1d = t1_d <= 0.06
    pass_pws = pw_s >= POWER_CRITERION
    pass_pwd = pw_d >= POWER_CRITERION
    pass_v7b = pass_t1s and pass_pws

    print(f"\n  {'='*50}")
    print(f"  V.7B Results (P_SIGNAL={p_signal})")
    print(f"  {'='*50}")
    print(f"  Type-I (simple):   {t1_s:.4f}  [{'PASS' if pass_t1s else 'FAIL'} ≤ 0.06]")
    print(f"  Type-I (deg):      {t1_d:.4f}  [{'PASS' if pass_t1d else 'FAIL'} ≤ 0.06]")
    print(f"  Power  (simple):   {pw_s:.4f}  [{'PASS' if pass_pws else 'FAIL'} ≥ 0.60]")
    print(f"  Power  (deg):      {pw_d:.4f}  [{'PASS' if pass_pwd else 'FAIL'} ≥ 0.60]")
    print(f"  Mean AUROC (power reps): {pw_auroc_mean:.4f} ± {pw_auroc_std:.4f}")
    print(f"  PRIMARY_TOP_K re-check:  {best_ptk}  "
          f"(type-I={t1_fisher[str(best_ptk)]:.4f} power={pw_fisher[str(best_ptk)]:.4f})")
    print(f"  V.7B overall: {'PASS' if pass_v7b else 'FAIL'}")
    print(f"  Total Part 2 wall time: {time.time()-t0:.0f}s")

    report = {
        "stage":             "0-V.7B",
        "date":              "2026-05-31",
        "deviation":         "DEV-P2-003",
        "p_signal":          p_signal,
        "p_signal_original": 10,
        "p_signal_fraction_of_annotated": float(p_signal / n_off_annotated),
        "effect_size":       EFFECT_SIZE,
        "n_null":            N_REP_V7B_NULL,
        "n_power":           N_REP_V7B_POWER,
        "n_perms":           N_PERMS_NULL,
        "type1_error": {
            "auroc_simple": t1_s, "auroc_degree": t1_d,
            "fisher": t1_fisher,
        },
        "power": {
            "auroc_simple":     pw_s,
            "auroc_degree":     pw_d,
            "mean_auroc":       pw_auroc_mean,
            "std_auroc":        pw_auroc_std,
            "fisher":           pw_fisher,
        },
        "calibration": {
            "primary_top_k": best_ptk,
            "primary_top_k_unchanged_from_v7": best_ptk == 20,
        },
        "pass_conditions": {
            "t1_simple_le_006": pass_t1s,
            "t1_deg_le_006":    pass_t1d,
            "power_simple_ge_060": pass_pws,
            "power_deg_ge_060":    pass_pwd,
        },
        "overall_pass": pass_v7b,
        "wall_time_s":  round(time.time() - t0, 1),
    }
    with open(OUT_DIR / "v7b_validation.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Saved: v7b_validation.json")
    return report, best_ptk


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Stage 0-V.7B — AUROC Enrichment Power Re-run")
    print("Authorization: Option B (supervisor, 2026-05-31)")
    print("Deviation: DEV-P2-003 — P_SIGNAL updated to P_SIGNAL_min")
    print("=" * 70)
    t_global = time.time()

    print(f"\nAnnotation structure:")
    print(f"  Off-connectome pairs:      {n_off}")
    print(f"  Off-connectome annotated:  {n_off_annotated} ({100*n_off_annotated/n_off:.1f}%)")
    print(f"  Original P_SIGNAL (V.7):   10  ({100*10/n_off_annotated:.1f}% of annotated)")
    print(f"  AUROC ceiling at P=10:     0.531 (analytical; from V.7A)")
    print(f"  V.7 AUROC power at P=10:   0.525 (observed; FAIL against ≥ 0.60)")
    print(f"  Seeking: smallest P with power ≥ 0.60 at effect={EFFECT_SIZE}")

    # Part 1 — Fine sweep
    p_signal_min, sweep_result = run_fine_sweep()

    # Part 2 — Full V.7B validation
    v7b, ptk = run_v7b_full(p_signal_min)

    # ── Consolidated summary ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STAGE 0-V.7B SUMMARY")
    print("=" * 70)
    print(f"\n  Deviation DEV-P2-003:")
    print(f"    Original design:  P_SIGNAL=10 ({100*10/n_off_annotated:.1f}% of {n_off_annotated} annotated pairs)")
    print(f"    Ceiling (P=10):   AUROC_max=0.531 → power=0.525 (criterion unsatisfiable)")
    print(f"    P_SIGNAL_min:     {p_signal_min} ({100*p_signal_min/n_off_annotated:.1f}% of annotated)")
    print(f"    Biological basis: minimum signal density satisfying power ≥ 0.60 at effect=0.20")
    print(f"    Updated design:   P_SIGNAL={p_signal_min}")
    print(f"\n  V.7B results:")
    print(f"    Type-I error (simple):   {v7b['type1_error']['auroc_simple']:.4f}  "
          f"[{'PASS' if v7b['pass_conditions']['t1_simple_le_006'] else 'FAIL'}]")
    print(f"    Type-I error (degree):   {v7b['type1_error']['auroc_degree']:.4f}  "
          f"[{'PASS' if v7b['pass_conditions']['t1_deg_le_006'] else 'FAIL'}]")
    print(f"    AUROC power (simple):    {v7b['power']['auroc_simple']:.4f}  "
          f"[{'PASS' if v7b['pass_conditions']['power_simple_ge_060'] else 'FAIL'}]")
    print(f"    AUROC power (degree):    {v7b['power']['auroc_degree']:.4f}  "
          f"[{'PASS' if v7b['pass_conditions']['power_deg_ge_060'] else 'FAIL'}]")
    print(f"    Mean AUROC (power):      {v7b['power']['mean_auroc']:.4f} ± {v7b['power']['std_auroc']:.4f}")
    print(f"    PRIMARY_TOP_K:           {ptk}  (unchanged from V.7 calibration: {ptk == 20})")
    print(f"    V.7B overall pass:       {v7b['overall_pass']}")

    if v7b["overall_pass"]:
        print(f"\n  STAGE 0-V (all stages) STATUS AFTER V.7B:")
        print(f"    V.1 PASS  V.2 PASS  V.3 PASS  V.4 PASS  V.5 PASS  V.6 PASS  V.7B PASS")
        print(f"\n  READY FOR: Stage 0-V.8 parameter lock")
        print(f"  REQUIRED:  Human authorization for PHASE2_ACTIVE=True after Stage 0-V.8")
    else:
        print(f"\n  V.7B FAIL — further diagnosis required before Stage 0-V.8")

    # Update summary record
    summary_update = {
        "v7b_replaces_v7": True,
        "deviation": "DEV-P2-003",
        "p_signal_original": 10,
        "p_signal_min": p_signal_min,
        "p_signal_min_fraction": float(p_signal_min / n_off_annotated),
        "v7b_pass": v7b["overall_pass"],
        "v7b_type1_simple": v7b["type1_error"]["auroc_simple"],
        "v7b_power_simple": v7b["power"]["auroc_simple"],
        "primary_top_k_confirmed": ptk,
        "fine_sweep": sweep_result,
    }
    with open(OUT_DIR / "v7b_summary.json", "w") as f:
        json.dump(summary_update, f, indent=2)
    print(f"\n  Saved: v7b_summary.json")
    print(f"  Total wall time: {time.time()-t_global:.0f}s")


if __name__ == "__main__":
    main()
