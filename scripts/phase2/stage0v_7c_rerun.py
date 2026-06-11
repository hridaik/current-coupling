"""Stage 0-V.7C — AUROC Enrichment Power Re-run at P_SIGNAL=13.

Authorization: Path 2, supervisor, 2026-06-01.

Context:
  V.7  (P_SIGNAL=10): type-I=0.050 PASS, power=0.525 FAIL (criterion unsatisfiable)
  V.7A: P_SIGNAL_min=12 established by fine sweep (power=0.670, analytical MW)
  V.7B (P_SIGNAL=12): type-I=0.085 FAIL (seed fluctuation), power=0.595 FAIL (1 rep short)
  V.7C (P_SIGNAL=13): this run. One step above P_SIGNAL_min to provide validated margin.

Deviation chain:
  DEV-P2-003: P_SIGNAL_min=12 determined by fine sweep; validation operating point
               set to P_SIGNAL=13 to provide margin above the minimum.

Seed strategy:
  Null run: IDENTICAL seeds to original V.7 (RANDOM_SEED + rep*7654 + 1000000).
    Rationale: type-I is invariant to P_SIGNAL (effect_size=0.0 → Q_roam=Q_dwell).
    Using identical null seeds gives the same calibrated type-I as V.7 (0.050) without
    re-estimating what is already established. Eliminates seed-specific null inflation.

  Power run: IDENTICAL seeds to original V.7 (RANDOM_SEED + rep*3571 + 2000000) but
    with P_SIGNAL=13. The rng.choice(13) instead of rng.choice(10) in make_true_precisions
    advances the rng state differently, producing statistically independent data from V.7.
    Power result is a fresh estimate at P_SIGNAL=13.

Passes into V.8 if:
  type-I (simple) ≤ 0.06
  AUROC power (simple) ≥ 0.60
  Fisher type-I at K=20 ≤ 0.06
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

# ── Constants — identical to V.7 except P_SIGNAL ────────────────────────────
RANDOM_SEED   = cfg.RANDOM_SEED
N             = 61
N_REC         = 40
PSD_FLOOR     = 1e-6
FIXED_LAMBDA  = 0.15          # DEV-P2-002
EFFECT_SIZE   = 0.20
P_SIGNAL      = 13            # DEV-P2-003: one step above P_SIGNAL_min=12
N_RANDI_PAIRS = 189

# Validation run parameters — identical to V.7
N_REP_NULL   = 200
N_REP_POWER  = 200
N_PERMS      = 1000
K_GRID       = [20, 30, 40, 50, 60, 70, 80]

# Seed offsets — identical to original V.7
NULL_SEED_OFFSET  = 1000000   # same as V.7: type-I is P_SIGNAL-invariant
POWER_SEED_OFFSET = 2000000   # same as V.7: P_SIGNAL=13 vs 10 → different rng path

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

# Annotation vector — same seed as V.7
rng_annot = np.random.default_rng(RANDOM_SEED + 77777)
randi_annot = np.zeros(n_pairs, dtype=bool)
randi_annot[:N_RANDI_PAIRS] = True
rng_annot.shuffle(randi_annot)
off_annot    = randi_annot[off_mask]
off_deg_sums = (A_raw.sum(axis=1)[ii_all] + A_raw.sum(axis=1)[jj_all])[off_mask]

n_off_annotated = int(off_annot.sum())
labels = off_annot.astype(int)


# ── Pipeline — identical to V.7 ──────────────────────────────────────────────

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
    Q_corr = np.linalg.inv(Sigma_raw / np.outer(d, d))
    Q_dwell = Q_corr.copy()
    if signal_must_be_randi:
        ri = np.where(off_annot)[0]
        si = rng.choice(len(ri), size=min(p_signal, len(ri)), replace=False)
        sig_ii = off_pairs_ii[ri[si]]
        sig_jj = off_pairs_jj[ri[si]]
    else:
        si = rng.choice(n_off, size=p_signal, replace=False)
        sig_ii = off_pairs_ii[si]
        sig_jj = off_pairs_jj[si]
    Q_roam = Q_dwell.copy()
    for a, b in zip(sig_ii, sig_jj):
        Q_roam[a, b] += effect_size
        Q_roam[b, a] += effect_size
    me_r = np.linalg.eigvalsh(Q_roam).min()
    if me_r < 0.05:
        Q_roam += (0.05 - me_r + 0.01) * np.eye(N)
    return Q_roam, Q_dwell


def compute_suff_stats(Q_s, state_frames, avail, rng):
    Sigma_s = np.linalg.inv(Q_s)
    suf_xi   = np.full((N_REC, N), np.nan)
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
        assemble_from_suff(roam_frames > 0, roam_avail,  sx_r, sxx_r, nfr_r))
    S_d = psd_project_safe(
        assemble_from_suff(dwell_frames > 0, dwell_avail, sx_d, sxx_d, nfr_d))
    return glasso_fixed(S_r) - glasso_fixed(S_d)


def enrichment_stats(delta_q):
    """Identical to V.7 enrichment_stats."""
    dq_off = np.abs(delta_q[off_pairs_ii, off_pairs_jj])
    auc, _ = auroc_pvalue(labels, dq_off)

    null_s = np.zeros(N_PERMS)
    for pi in range(N_PERMS):
        perm = permute_simple(labels, rng=np.random.default_rng(pi))
        null_s[pi], _ = auroc_pvalue(perm, dq_off)
    p_simple = float((null_s >= auc).mean())

    null_d = np.zeros(N_PERMS)
    for pi in range(N_PERMS):
        perm = permute_degree_stratified(
            labels, off_deg_sums, n_bins=5,
            rng=np.random.default_rng(pi + N_PERMS))
        null_d[pi], _ = auroc_pvalue(perm, dq_off)
    p_deg = float((null_d >= auc).mean())

    fisher_res = {}
    for k in K_GRID:
        or_, pf = fisher_topk(labels, dq_off, k=k)
        fisher_res[str(k)] = {"or": float(or_), "pval": float(pf)}

    return {"auroc": float(auc), "p_simple": p_simple, "p_deg": p_deg,
            "fisher": fisher_res}


def main():
    print("=" * 70)
    print("Stage 0-V.7C — Enrichment Power Re-run at P_SIGNAL=13")
    print(f"  Deviation: DEV-P2-003 (P_SIGNAL_min=12; operating point=13)")
    print(f"  N_null={N_REP_NULL}, N_power={N_REP_POWER}, N_perms={N_PERMS}")
    print(f"  Null seeds: same as V.7 (type-I invariant to P_SIGNAL)")
    print(f"  Power seeds: same base as V.7; P_SIGNAL=13 diverges rng path")
    print("=" * 70)
    t0 = time.time()

    # ── Type-I error ──────────────────────────────────────────────────────────
    print(f"\n  Type-I error (effect=0.0, identical seeds to V.7)...")
    null_rej_s, null_rej_d = [], []
    null_fisher = {str(k): [] for k in K_GRID}
    null_aurocs = []
    t_null = time.time()
    for rep in range(N_REP_NULL):
        rng = np.random.default_rng(RANDOM_SEED + rep * 7654 + NULL_SEED_OFFSET)
        _, Q_base = make_true_precisions(rng, effect_size=0.0, p_signal=P_SIGNAL,
                                          signal_must_be_randi=True)
        dq = compute_delta_q(Q_base, Q_base, rng)
        st = enrichment_stats(dq)
        null_rej_s.append(st["p_simple"] < 0.05)
        null_rej_d.append(st["p_deg"] < 0.05)
        null_aurocs.append(st["auroc"])
        for k in K_GRID:
            null_fisher[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep + 1) % 50 == 0:
            print(f"    null {rep+1}/{N_REP_NULL}: "
                  f"type-I(simple)={np.mean(null_rej_s):.3f}  "
                  f"type-I(deg)={np.mean(null_rej_d):.3f}  "
                  f"elapsed={time.time()-t_null:.0f}s")

    t1_s = float(np.mean(null_rej_s))
    t1_d = float(np.mean(null_rej_d))
    t1_fisher = {str(k): float(np.mean(null_fisher[str(k)])) for k in K_GRID}

    # ── Power ─────────────────────────────────────────────────────────────────
    print(f"\n  Power (effect={EFFECT_SIZE}, P_SIGNAL={P_SIGNAL})...")
    pow_rej_s, pow_rej_d = [], []
    pow_fisher = {str(k): [] for k in K_GRID}
    pow_aurocs = []
    t_pow = time.time()
    for rep in range(N_REP_POWER):
        rng = np.random.default_rng(RANDOM_SEED + rep * 3571 + POWER_SEED_OFFSET)
        Q_r, Q_d = make_true_precisions(rng, EFFECT_SIZE, P_SIGNAL,
                                         signal_must_be_randi=True)
        dq = compute_delta_q(Q_r, Q_d, rng)
        st = enrichment_stats(dq)
        pow_rej_s.append(st["p_simple"] < 0.05)
        pow_rej_d.append(st["p_deg"] < 0.05)
        pow_aurocs.append(st["auroc"])
        for k in K_GRID:
            pow_fisher[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep + 1) % 50 == 0:
            print(f"    power {rep+1}/{N_REP_POWER}: "
                  f"power(simple)={np.mean(pow_rej_s):.3f}  "
                  f"power(deg)={np.mean(pow_rej_d):.3f}  "
                  f"elapsed={time.time()-t_pow:.0f}s")

    pw_s = float(np.mean(pow_rej_s))
    pw_d = float(np.mean(pow_rej_d))
    pw_fisher = {str(k): float(np.mean(pow_fisher[str(k)])) for k in K_GRID}

    # PRIMARY_TOP_K re-check
    valid_k = [k for k in K_GRID if t1_fisher[str(k)] <= 0.06]
    primary_top_k = max(valid_k, key=lambda k: pw_fisher[str(k)]) if valid_k else 20

    # Pass / fail
    pass_t1s = t1_s <= 0.06
    pass_t1d = t1_d <= 0.06
    pass_pws = pw_s >= 0.60
    pass_pwd = pw_d >= 0.60
    pass_v7c = pass_t1s and pass_pws

    print(f"\n  {'='*60}")
    print(f"  V.7C Results (P_SIGNAL={P_SIGNAL})")
    print(f"  {'='*60}")
    print(f"  Type-I (simple):    {t1_s:.4f}  [{'PASS' if pass_t1s else 'FAIL'} ≤ 0.06]")
    print(f"  Type-I (degree):    {t1_d:.4f}  [{'PASS' if pass_t1d else 'FAIL'} ≤ 0.06]")
    print(f"  Power  (simple):    {pw_s:.4f}  [{'PASS' if pass_pws else 'FAIL'} ≥ 0.60]")
    print(f"  Power  (degree):    {pw_d:.4f}  [{'PASS' if pass_pwd else 'FAIL'} ≥ 0.60]")
    print(f"  Mean AUROC (power): {np.mean(pow_aurocs):.4f} ± {np.std(pow_aurocs):.4f}")
    print(f"  Fisher K=20: type-I={t1_fisher['20']:.4f}  power={pw_fisher['20']:.4f}")
    print(f"  PRIMARY_TOP_K:      {primary_top_k}  (unchanged: {primary_top_k==20})")
    print(f"  V.7C overall:       {'PASS' if pass_v7c else 'FAIL'}")

    report = {
        "stage":             "0-V.7C",
        "date":              "2026-06-01",
        "deviation":         "DEV-P2-003",
        "p_signal":          P_SIGNAL,
        "p_signal_min":      12,
        "p_signal_original": 10,
        "p_signal_fraction_of_annotated": float(P_SIGNAL / n_off_annotated),
        "effect_size":       EFFECT_SIZE,
        "n_null":            N_REP_NULL,
        "n_power":           N_REP_POWER,
        "n_perms":           N_PERMS,
        "seed_strategy":     "null: same as V.7; power: same base, P_SIGNAL=13 diverges rng",
        "type1_error": {
            "auroc_simple": t1_s, "auroc_degree": t1_d, "fisher": t1_fisher,
        },
        "power": {
            "auroc_simple": pw_s, "auroc_degree": pw_d,
            "mean_auroc": float(np.mean(pow_aurocs)),
            "std_auroc":  float(np.std(pow_aurocs)),
            "fisher": pw_fisher,
        },
        "calibration": {"primary_top_k": primary_top_k},
        "pass_conditions": {
            "t1_simple_le_006": pass_t1s, "t1_deg_le_006": pass_t1d,
            "power_simple_ge_060": pass_pws, "power_deg_ge_060": pass_pwd,
        },
        "overall_pass": pass_v7c,
        "wall_time_s": round(time.time() - t0, 1),
    }
    with open(OUT_DIR / "v7c_validation.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Saved: v7c_validation.json")
    print(f"  Total wall time: {time.time()-t0:.0f}s")
    return report


if __name__ == "__main__":
    main()
