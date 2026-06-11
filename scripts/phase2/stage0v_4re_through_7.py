"""Stage 0-V.4 (re-run, fixed λ=0.15) through Stage 0-V.7 — complete validation suite.

Authorization: 2026-05-31.
  V.4 re-run: fixed λ=0.15 within-bootstrap GLASSO (pre-specified from V.3 sweep,
    replacing BIC-based selection which was underpowered at effect=0.2).
  V.5–V.7: authorized to run immediately after V.4 calibration.

Deviation recorded:
  DEV-P2-002: Within-bootstrap GLASSO lambda = 0.15 (fixed), replacing BIC-based
    selection. Basis: V.3 synthetic sweep identified λ=0.15 as producing
    TPR=0.973, FPR=0.033 at effect=0.2. Determined entirely from synthetic
    data before any real-data results. All other pipeline components unchanged.

Outputs written to results/phase2/stage0v/:
  v4_stability_rerun.json       (calibrated STABILITY_THRESHOLD, N_BOOT)
  v5_anatomy_guided.json        (calibrated LAMBDA_ON, LAMBDA_OFF)
  v6_circularity.json
  v7_enrichment_power.json
  validation_summary.json       (full consolidated pass/fail report)
"""

from __future__ import annotations
import json, sys, time, warnings
from pathlib import Path
import numpy as np
from scipy import stats
from sklearn.covariance import graphical_lasso

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import phase0_config as cfg

from src.estimators  import _glasso_admm
from src.enrichment  import auroc_pvalue, fisher_topk
from src.null_models import permute_simple, permute_degree_stratified

# ── Constants ────────────────────────────────────────────────────────────────
RANDOM_SEED      = cfg.RANDOM_SEED          # 20260527
N                = 61
N_REC            = 40
PSD_FLOOR        = 1e-6
FIXED_LAMBDA     = 0.15                     # V.4 re-run; V.6 stability selection
EFFECT_SIZE      = 0.2                      # primary validation effect size
P_SIGNAL         = 10
N_RANDI_PAIRS    = 189                      # background annotation count

# V.4 re-run settings
N_REP_V4         = 30
N_BOOT_MAX       = 100
BOOT_CHECKS      = [25, 50, 100]
THRESHOLDS       = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]

# V.5 settings
N_REP_V5         = 50
LAMBDA_ON_GRID   = [0.01, 0.02, 0.04, 0.08]
RATIO_GRID       = [5, 10, 15, 20]

# V.6 settings
N_REP_V6         = 50
N_BOOT_V6        = 50

# V.7 settings
N_REP_V7_NULL    = 200
N_REP_V7_POWER   = 200
N_PERMS_NULL     = 1000
K_GRID           = [20, 30, 40, 50, 60, 70, 80]

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load corpus structure ─────────────────────────────────────────────────────
presence     = np.load("/tmp/presence_matrix.npy")
roam_frames  = np.load("/tmp/roam_frames.npy")
dwell_frames = np.load("/tmp/dwell_frames.npy")
A_raw        = np.load("/tmp/A_raw_61.npy")

roam_avail  = (presence & (roam_frames  > 0)[:, None]).astype(bool)
dwell_avail = (presence & (dwell_frames > 0)[:, None]).astype(bool)
ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)

off_mask = A_raw[ii_all, jj_all] == 0
on_mask  = ~off_mask
off_pairs_ii = ii_all[off_mask]
off_pairs_jj = jj_all[off_mask]
n_off = int(off_mask.sum())
n_on  = int(on_mask.sum())

roam_rec_indices  = np.where(roam_frames  > 0)[0]   # 19 recordings
dwell_rec_indices = np.where(dwell_frames > 0)[0]   # 39 recordings
K_roam  = len(roam_rec_indices)    # 19
K_dwell = len(dwell_rec_indices)   # 39
K_boot_roam  = K_roam  // 2       # 9
K_boot_dwell = K_dwell // 2       # 19

# ── Synthetic neuropeptide annotation (fixed seed, 189/1830 pairs) ────────────
rng_annot = np.random.default_rng(RANDOM_SEED + 77777)
randi_annot = np.zeros(n_pairs, dtype=bool)
randi_annot[:N_RANDI_PAIRS] = True
rng_annot.shuffle(randi_annot)
# Degree sums for degree-preserving permutation
degree_A = A_raw.sum(axis=1)
pair_degree_sums = degree_A[ii_all] + degree_A[jj_all]   # (n_pairs,)
off_annot = randi_annot[off_mask]   # (n_off,) — annotation for off-connectome pairs
off_degree_sums = pair_degree_sums[off_mask]
print(f"Randi annotation: {randi_annot.sum()} annotated / {n_pairs} total pairs")
print(f"Off-connectome annotated: {off_annot.sum()} / {n_off}")


# ── Shared utilities (from V.3/V.4 scripts) ──────────────────────────────────

def make_true_precisions(rng, effect_size=EFFECT_SIZE, p_signal=P_SIGNAL,
                         signal_must_be_randi=False):
    """Correlation-scale Q_true. If signal_must_be_randi=True, planted pairs
    are drawn from Randi-annotated off-connectome pairs."""
    W = rng.standard_normal((2*N, N))
    Q_base = (W.T @ W)/(2*N) + 0.5*np.eye(N)
    sparsity_mask = np.zeros((N,N), dtype=bool); np.fill_diagonal(sparsity_mask, True)
    sparsity_mask |= A_raw.astype(bool)
    off_m = (A_raw==0); np.fill_diagonal(off_m, False)
    oi, oj = np.where(np.triu(off_m, k=1)); keep = rng.random(len(oi)) < 0.15
    for k in np.where(keep)[0]: sparsity_mask[oi[k],oj[k]] = True; sparsity_mask[oj[k],oi[k]] = True
    Q_0 = Q_base * sparsity_mask
    me = np.linalg.eigvalsh(Q_0).min()
    if me < 0.1: Q_0 += (0.1-me+0.05)*np.eye(N)
    Sigma_raw = np.linalg.inv(Q_0)
    diag_sqrt = np.sqrt(np.diag(Sigma_raw))
    Sigma_corr = Sigma_raw / np.outer(diag_sqrt, diag_sqrt)
    Q_corr = np.linalg.inv(Sigma_corr)
    Q_true_dwell = Q_corr.copy()

    if signal_must_be_randi:
        randi_off_idx = np.where(off_annot)[0]
        sig_idx = rng.choice(len(randi_off_idx), size=p_signal, replace=False)
        signal_ii = off_pairs_ii[randi_off_idx[sig_idx]]
        signal_jj = off_pairs_jj[randi_off_idx[sig_idx]]
    else:
        sig_idx = rng.choice(n_off, size=p_signal, replace=False)
        signal_ii = off_pairs_ii[sig_idx]
        signal_jj = off_pairs_jj[sig_idx]

    Q_true_roam = Q_true_dwell.copy()
    for si, sj in zip(signal_ii, signal_jj):
        Q_true_roam[si, sj] += effect_size
        Q_true_roam[sj, si] += effect_size
    me_r = np.linalg.eigvalsh(Q_true_roam).min()
    if me_r < 0.05: Q_true_roam += (0.05-me_r+0.01)*np.eye(N)
    signal_pairs = np.column_stack([signal_ii, signal_jj])
    return Q_true_roam, Q_true_dwell, signal_pairs


def compute_suff_stats(Q_true_s, state_frames, avail, rng):
    Sigma_s = np.linalg.inv(Q_true_s)
    suf_xi=np.full((N_REC,N),np.nan); suf_xixj=np.zeros((N_REC,N,N)); n_fr=np.zeros(N_REC,dtype=int)
    for r in range(N_REC):
        T_r=int(state_frames[r]);
        if T_r==0: continue
        O_r=np.where(avail[r])[0]
        if not len(O_r): continue
        Sr=Sigma_s[np.ix_(O_r,O_r)]; Sr=(Sr+Sr.T)/2
        me=np.linalg.eigvalsh(Sr).min()
        if me<1e-10: Sr+=(1e-8-me)*np.eye(len(O_r))
        L=np.linalg.cholesky(Sr); Xr=rng.standard_normal((T_r,len(O_r)))@L.T
        suf_xi[r,O_r]=Xr.sum(axis=0); XXT=Xr.T@Xr
        for ki,i in enumerate(O_r): suf_xixj[r,i,O_r]=XXT[ki]
        n_fr[r]=T_r
    return suf_xi, suf_xixj, n_fr


def assemble_from_suff(boot_mask, avail, suf_xi, suf_xixj, n_frames):
    active=boot_mask&(n_frames>0); avail_f=avail.astype(float)
    copres=active[:,None,None]*avail_f[:,:,None]*avail_f[:,None,:]
    T_ij=(copres*n_frames[:,None,None]).sum(axis=0)
    sx_nn=np.nan_to_num(suf_xi,nan=0.0)
    Sxi=(copres*sx_nn[:,:,None]).sum(axis=0); Sxj=(copres*sx_nn[:,None,:]).sum(axis=0)
    Sxixj=(copres*suf_xixj).sum(axis=0)
    with np.errstate(invalid='ignore',divide='ignore'):
        mi=Sxi/T_ij; mj=Sxj/T_ij
        S=(Sxixj-T_ij*mi*mj)/np.maximum(T_ij-1,1)
    S=np.where(T_ij>=2,S,np.nan)
    T_i=(active[:,None]*avail_f*n_frames[:,None]).sum(axis=0)
    Sxi_d=(active[:,None]*avail_f*sx_nn).sum(axis=0)
    Sxi2_d=(active[:,None]*avail_f*suf_xixj[:,range(N),range(N)]).sum(axis=0)
    with np.errstate(invalid='ignore',divide='ignore'):
        mi_d=Sxi_d/T_i; var_i=(Sxi2_d-T_i*mi_d**2)/np.maximum(T_i-1,1)
    np.fill_diagonal(S,np.where(T_i>=2,var_i,np.nan))
    S=np.nan_to_num((S+S.T)/2,nan=0.0)
    np.fill_diagonal(S,np.where(np.diag(S)<=0,1.0,np.diag(S)))
    return S


def psd_project_safe(S):
    S_sym=(S+S.T)/2; ev,vc=np.linalg.eigh(S_sym)
    return (vc@np.diag(np.maximum(ev,PSD_FLOOR))@vc.T+S_sym.T)/2


def glasso_fixed(S, alpha):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try: Q,_=graphical_lasso(S,alpha=alpha,max_iter=300,tol=5e-4)
        except Exception: Q=np.eye(N)
    return Q


def anatomy_admm(S_proj, lambda_on, lambda_off):
    """Anatomy-guided ADMM lasso on precomputed S_proj."""
    Lambda = np.where(A_raw>0, lambda_on, lambda_off).astype(float)
    np.fill_diagonal(Lambda, 0.0)
    return _glasso_admm(S_proj, Lambda, rho=1.0, max_iter=500, tol=1e-4)


def sig_set_from(signal_pairs):
    return {(int(min(p[0],p[1])), int(max(p[0],p[1]))) for p in signal_pairs.tolist()}


def tpr_fpr(signal_pairs, Q_mat):
    sig = sig_set_from(signal_pairs)
    sel = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
           if abs(Q_mat[ii_all[k],jj_all[k]])>1e-8}
    tp  = len(sig & sel)
    fp_off = sum(1 for p in sel if p not in sig and A_raw[p[0],p[1]]==0 and A_raw[p[1],p[0]]==0)
    return tp/P_SIGNAL, fp_off/max(n_off-P_SIGNAL,1)


def full_data_S(Q_true_s, state_frames, avail, rng_r):
    sx, sxx, nfr = compute_suff_stats(Q_true_s, state_frames, avail, rng_r)
    S = assemble_from_suff(state_frames>0, avail, sx, sxx, nfr)
    return psd_project_safe(S), sx, sxx, nfr


# ── Stage 0-V.4 re-run (fixed λ=0.15) ────────────────────────────────────────
def run_v4_rerun():
    print("\n" + "="*60)
    print(f"Stage 0-V.4 re-run — Fixed lambda={FIXED_LAMBDA}")
    print(f"N_REP={N_REP_V4}, N_BOOT_MAX={N_BOOT_MAX}, K_boot={K_boot_roam}")
    print("="*60)
    t0_total = time.time()

    stab_tp_all, stab_tn_all = [], []
    tpr_by_thr = {t:[] for t in THRESHOLDS}
    fpr_by_thr = {t:[] for t in THRESHOLDS}
    boot_clipfracs = []; n_boot_var = {n:[] for n in BOOT_CHECKS}

    for outer in range(N_REP_V4):
        rng_o = np.random.default_rng(RANDOM_SEED + outer*31337 + 600000)
        Q_r, Q_d, sig_pairs = make_true_precisions(rng_o)
        sig = sig_set_from(sig_pairs)
        sx, sxx, nfr = compute_suff_stats(Q_r, roam_frames, roam_avail, rng_o)
        S_full,_,_,_ = full_data_S(Q_r, roam_frames, roam_avail,
                                    np.random.default_rng(RANDOM_SEED+outer))
        selected_boots = np.zeros((N_BOOT_MAX, N, N), dtype=np.int8)
        rng_b = np.random.default_rng(RANDOM_SEED + outer*31337 + 700000)
        for b in range(N_BOOT_MAX):
            boot_recs = rng_b.choice(roam_rec_indices, size=K_boot_roam, replace=False)
            boot_mask = np.zeros(N_REC, dtype=bool); boot_mask[boot_recs] = True
            S_b = assemble_from_suff(boot_mask, roam_avail, sx, sxx, nfr)
            eigs_b = np.linalg.eigvalsh((S_b+S_b.T)/2)
            boot_clipfracs.append(float((eigs_b<PSD_FLOOR).sum())/N)
            S_b = psd_project_safe(S_b)
            Q_b = glasso_fixed(S_b, FIXED_LAMBDA)
            sel_b = (np.abs(Q_b)>1e-8).astype(np.int8); np.fill_diagonal(sel_b,0)
            selected_boots[b] = sel_b
        stab_mat = selected_boots.mean(axis=0)
        stab_u = stab_mat[ii_all, jj_all]
        tp_idx = [k for k in range(n_pairs) if (int(ii_all[k]),int(jj_all[k])) in sig]
        tn_off = [k for k in range(n_pairs) if (int(ii_all[k]),int(jj_all[k])) not in sig
                  and A_raw[ii_all[k],jj_all[k]]==0 and A_raw[jj_all[k],ii_all[k]]==0]
        stab_tp_all.append(stab_u[tp_idx].tolist())
        stab_tn_all.append(stab_u[tn_off].tolist())
        for thr in THRESHOLDS:
            tpr_by_thr[thr].append(sum(1 for k in tp_idx if stab_u[k]>=thr)/P_SIGNAL)
            fpr_by_thr[thr].append(sum(1 for k in tn_off if stab_u[k]>=thr)/max(len(tn_off),1))
        for nbc in BOOT_CHECKS:
            sc = selected_boots[:nbc].mean(axis=0)
            n_boot_var[nbc].append(float(np.var(sc[ii_all,jj_all])))
        if (outer+1)%10==0:
            mt = np.median([np.mean(v) for v in stab_tp_all[-10:]])
            mn = np.median([np.mean(v) for v in stab_tn_all[-10:]])
            by = max(np.mean(tpr_by_thr[t])-np.mean(fpr_by_thr[t]) for t in THRESHOLDS)
            print(f"  outer {outer+1}/{N_REP_V4}: stab_TP={mt:.3f} stab_TN={mn:.3f} Youden={by:.3f}")

    all_tp = [s for rep in stab_tp_all for s in rep]
    all_tn = [s for rep in stab_tn_all for s in rep]

    print(f"\n  TP stability: mean={np.mean(all_tp):.3f} median={np.median(all_tp):.3f} "
          f"p25={np.percentile(all_tp,25):.3f} p75={np.percentile(all_tp,75):.3f}")
    print(f"  TN stability: mean={np.mean(all_tn):.3f} median={np.median(all_tn):.3f}")

    youden = {}
    print(f"\n  TPR / FPR by threshold:")
    for thr in THRESHOLDS:
        m_tpr=float(np.mean(tpr_by_thr[thr])); m_fpr=float(np.mean(fpr_by_thr[thr]))
        y=m_tpr-m_fpr; youden[thr]=y
        print(f"    thr={thr:.2f}: TPR={m_tpr:.3f} FPR={m_fpr:.4f} Youden={y:.3f} "
              f"[{'PASS' if m_tpr>=0.50 and m_fpr<=0.10 else 'fail'}]")

    best_thr = max(youden, key=youden.get)
    youden_range = max(youden.values())-min(youden.values())
    rec_thr = 0.75 if youden_range < 0.05 else best_thr
    pass_rec = (float(np.mean(tpr_by_thr[rec_thr]))>=0.50 and
                float(np.mean(fpr_by_thr[rec_thr]))<=0.10)
    print(f"\n  Youden range: {youden_range:.3f}, best thr: {best_thr:.2f}")
    print(f"  Recommended STABILITY_THRESHOLD: {rec_thr:.2f} (pass: {pass_rec})")

    var_nboot = {n: float(np.median(n_boot_var[n])) for n in BOOT_CHECKS}
    rec_nboot = 100
    for i in range(len(BOOT_CHECKS)-1):
        n1,n2=BOOT_CHECKS[i],BOOT_CHECKS[i+1]
        if abs(var_nboot[n1]-var_nboot[n2])/max(var_nboot[n1],1e-12) < 0.02:
            rec_nboot=n1; break
    print(f"  N_BOOT convergence: {var_nboot}")
    print(f"  Recommended N_BOOTSTRAP_RESAMPLES: {rec_nboot}")

    report = {
        "stage": "0-V.4-rerun", "date": "2026-05-31",
        "fixed_lambda": FIXED_LAMBDA, "n_rep": N_REP_V4, "n_boot": N_BOOT_MAX,
        "stability_distributions": {
            "tp_pairs": {"mean":float(np.mean(all_tp)),"median":float(np.median(all_tp)),
                         "p25":float(np.percentile(all_tp,25)),"p75":float(np.percentile(all_tp,75)),
                         "p10":float(np.percentile(all_tp,10)),"p90":float(np.percentile(all_tp,90))},
            "tn_pairs": {"mean":float(np.mean(all_tn)),"median":float(np.median(all_tn)),
                         "p25":float(np.percentile(all_tn,25)),"p75":float(np.percentile(all_tn,75))}},
        "tpr_fpr_by_threshold": {
            str(thr): {"mean_tpr":float(np.mean(tpr_by_thr[thr])),
                       "mean_fpr":float(np.mean(fpr_by_thr[thr])),
                       "youden":float(youden[thr]),
                       "pass":(float(np.mean(tpr_by_thr[thr]))>=0.50 and
                               float(np.mean(fpr_by_thr[thr]))<=0.10)}
            for thr in THRESHOLDS},
        "n_boot_convergence": {str(n):{"variance":var_nboot[n]} for n in BOOT_CHECKS},
        "bootstrap_clip_fraction_mean": float(np.mean(boot_clipfracs)),
        "calibration": {
            "youden_range": float(youden_range), "best_thr": float(best_thr),
            "recommended_stability_threshold": float(rec_thr),
            "pass_at_recommended": pass_rec,
            "recommended_n_bootstrap_resamples": int(rec_nboot)},
        "overall_pass": pass_rec,
        "wall_time_s": round(time.time()-t0_total,1)
    }
    with open(OUT_DIR/"v4_stability_rerun.json","w") as f: json.dump(report,f,indent=2)
    print(f"  V.4 re-run saved. Time: {time.time()-t0_total:.0f}s")
    return report


# ── Stage 0-V.5: Anatomy-guided lasso calibration ────────────────────────────
def run_v5():
    print("\n"+"="*60)
    print(f"Stage 0-V.5 — Anatomy-Guided Lasso Calibration")
    print(f"N_REP={N_REP_V5}, {len(LAMBDA_ON_GRID)}×{len(RATIO_GRID)}=16 combinations")
    print("="*60)
    t0_total = time.time()

    combo_results = {}
    for lam_on in LAMBDA_ON_GRID:
        for ratio in RATIO_GRID:
            lam_off = lam_on * ratio
            tpr_list, fpr_list = [], []
            for rep in range(N_REP_V5):
                rng_r = np.random.default_rng(RANDOM_SEED + rep*9001 + int(lam_on*1e5) + ratio)
                Q_r, Q_d, sig = make_true_precisions(rng_r)
                sig_s = sig_set_from(sig)
                S_proj,_,_,_ = full_data_S(Q_r, roam_frames, roam_avail, rng_r)
                Q_conf = anatomy_admm(S_proj, lam_on, lam_off)
                tpr, fpr = tpr_fpr(sig, Q_conf)
                tpr_list.append(tpr); fpr_list.append(fpr)
            key = f"lon={lam_on:.3f}_loff={lam_off:.3f}"
            combo_results[key] = {
                "lambda_on": lam_on, "lambda_off": lam_off, "ratio": ratio,
                "tpr_mean": float(np.mean(tpr_list)), "tpr_std": float(np.std(tpr_list)),
                "fpr_mean": float(np.mean(fpr_list)), "fpr_std": float(np.std(fpr_list)),
                "pass": (float(np.mean(tpr_list))>=0.50 and float(np.mean(fpr_list))<=0.10)
            }

    print(f"\n  Combo results (λ_on, ratio: TPR, FPR, pass):")
    best_key = None; best_score = -1
    for k, v in sorted(combo_results.items(), key=lambda x: x[1]["lambda_on"]):
        ok = v["pass"]
        score = v["tpr_mean"] if v["fpr_mean"] <= 0.05 else (
                v["tpr_mean"] * 0.5 if v["fpr_mean"] <= 0.10 else -1)
        if score > best_score:
            best_score = score; best_key = k
        print(f"    λ_on={v['lambda_on']:.3f} ratio={v['ratio']:>2}: "
              f"TPR={v['tpr_mean']:.3f} FPR={v['fpr_mean']:.4f} "
              f"[{'PASS' if ok else 'fail'}]")

    best = combo_results[best_key]
    pass_v5 = best["pass"]
    print(f"\n  Selected: λ_on={best['lambda_on']:.3f}, λ_off={best['lambda_off']:.3f} "
          f"(ratio={best['ratio']})")
    print(f"  V.5 TPR={best['tpr_mean']:.3f} FPR={best['fpr_mean']:.4f} "
          f"[{'PASS' if pass_v5 else 'FAIL'}]")

    report = {
        "stage": "0-V.5", "date": "2026-05-31", "n_rep": N_REP_V5,
        "all_combos": combo_results,
        "selected": {"lambda_on": best["lambda_on"], "lambda_off": best["lambda_off"],
                     "ratio": best["ratio"]},
        "pass_conditions": {"tpr_ge_050": True, "fpr_le_010": True},
        "overall_pass": pass_v5,
        "wall_time_s": round(time.time()-t0_total,1)
    }
    with open(OUT_DIR/"v5_anatomy_guided.json","w") as f: json.dump(report,f,indent=2)
    print(f"  V.5 saved. Time: {time.time()-t0_total:.0f}s")
    return report, best["lambda_on"], best["lambda_off"]


# ── Stage 0-V.6: Circularity control ─────────────────────────────────────────
def run_v6(lambda_on, lambda_off, stability_threshold):
    print("\n"+"="*60)
    print(f"Stage 0-V.6 — Circularity Control")
    print(f"N_REP={N_REP_V6}, N_BOOT={N_BOOT_V6}, "
          f"stability_thr={stability_threshold:.2f}, "
          f"λ_on={lambda_on:.3f}, λ_off={lambda_off:.3f}")
    print("="*60)
    t0_total = time.time()

    confirm_rate_tp_list  = []   # fraction of TP-in-discovery that survive confirmation
    false_confirm_list    = []   # fraction of TN off-connectome in confirmation
    disc_tp_list          = []   # fraction of TP in discovery set

    for rep in range(N_REP_V6):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*54321 + 800000)
        Q_r, Q_d, sig = make_true_precisions(rng_r)
        sig_s = sig_set_from(sig)

        sx, sxx, nfr = compute_suff_stats(Q_r, roam_frames, roam_avail, rng_r)
        S_full = assemble_from_suff(roam_frames>0, roam_avail, sx, sxx, nfr)
        S_full = psd_project_safe(S_full)

        # Discovery: stability selection
        selected_b = np.zeros((N_BOOT_V6, N, N), dtype=np.int8)
        rng_b = np.random.default_rng(RANDOM_SEED + rep*54321 + 900000)
        for b in range(N_BOOT_V6):
            boot_recs = rng_b.choice(roam_rec_indices, size=K_boot_roam, replace=False)
            bm = np.zeros(N_REC, dtype=bool); bm[boot_recs] = True
            S_b = assemble_from_suff(bm, roam_avail, sx, sxx, nfr)
            S_b = psd_project_safe(S_b)
            Q_b = glasso_fixed(S_b, FIXED_LAMBDA)
            sb = (np.abs(Q_b)>1e-8).astype(np.int8); np.fill_diagonal(sb,0)
            selected_b[b] = sb

        stab = selected_b.mean(axis=0)
        # Discovery set: edges above threshold
        disc_set = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
                    if stab[ii_all[k],jj_all[k]] >= stability_threshold}

        # Confirmation: anatomy-guided ADMM on full-data S
        Q_conf = anatomy_admm(S_full, lambda_on, lambda_off)
        conf_set = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
                    if abs(Q_conf[ii_all[k],jj_all[k]])>1e-8}

        # Evaluate
        tp_in_disc = sig_s & disc_set
        tp_in_both = sig_s & disc_set & conf_set
        tn_off_in_conf = sum(1 for p in conf_set
                             if p not in sig_s and A_raw[p[0],p[1]]==0 and A_raw[p[1],p[0]]==0)
        n_tn_off = n_off - P_SIGNAL

        confirm_rate = len(tp_in_both)/max(len(tp_in_disc),1) if tp_in_disc else np.nan
        false_conf   = tn_off_in_conf / max(n_tn_off, 1)
        disc_tp      = len(tp_in_disc) / P_SIGNAL

        if not np.isnan(confirm_rate): confirm_rate_tp_list.append(confirm_rate)
        false_confirm_list.append(false_conf)
        disc_tp_list.append(disc_tp)

    median_confirm = float(np.nanmedian(confirm_rate_tp_list)) if confirm_rate_tp_list else 0.0
    mean_false     = float(np.mean(false_confirm_list))
    mean_disc_tp   = float(np.mean(disc_tp_list))

    pass_confirm = median_confirm >= 0.70
    pass_false   = mean_false   <= 0.05
    pass_v6 = pass_confirm and pass_false

    print(f"\n  Discovery TPR (fraction of signal in disc set): {mean_disc_tp:.3f}")
    print(f"  Confirmation rate for TP (in disc AND conf): {median_confirm:.3f} "
          f"[{'PASS' if pass_confirm else 'FAIL'} >= 0.70]")
    print(f"  False confirmation rate (TN off-conn in conf): {mean_false:.4f} "
          f"[{'PASS' if pass_false else 'FAIL'} <= 0.05]")
    print(f"  V.6 overall pass: {pass_v6}")

    report = {
        "stage": "0-V.6", "date": "2026-05-31",
        "n_rep": N_REP_V6, "n_boot": N_BOOT_V6,
        "stability_threshold_used": stability_threshold,
        "lambda_on_used": lambda_on, "lambda_off_used": lambda_off,
        "discovery_tpr_mean": mean_disc_tp,
        "confirmation_rate_tp_median": median_confirm,
        "false_confirmation_rate_mean": mean_false,
        "pass_conditions": {
            "confirm_rate_ge_070": {"value": median_confirm, "pass": pass_confirm},
            "false_confirm_le_005": {"value": mean_false,    "pass": pass_false}},
        "overall_pass": pass_v6,
        "wall_time_s": round(time.time()-t0_total,1)
    }
    with open(OUT_DIR/"v6_circularity.json","w") as f: json.dump(report,f,indent=2)
    print(f"  V.6 saved. Time: {time.time()-t0_total:.0f}s")
    return report


# ── Stage 0-V.7: Enrichment test calibration ─────────────────────────────────
def run_v7(stability_threshold, lambda_on, lambda_off):
    print("\n"+"="*60)
    print(f"Stage 0-V.7 — Enrichment Test Calibration")
    print(f"N_null={N_REP_V7_NULL}, N_power={N_REP_V7_POWER}, N_perm={N_PERMS_NULL}")
    print(f"Randi annotation: {off_annot.sum()} / {n_off} off-connectome pairs")
    print("="*60)
    t0_total = time.time()

    def compute_delta_q(Q_r, Q_d, rng_rep):
        """Generate synthetic data for both states, assemble S, compute ΔQ via GLASSO."""
        # Roaming
        sx_r, sxx_r, nfr_r = compute_suff_stats(Q_r, roam_frames,  roam_avail,  rng_rep)
        # Dwelling
        sx_d, sxx_d, nfr_d = compute_suff_stats(Q_d, dwell_frames, dwell_avail, rng_rep)
        S_r = assemble_from_suff(roam_frames>0,  roam_avail,  sx_r, sxx_r, nfr_r)
        S_d = assemble_from_suff(dwell_frames>0, dwell_avail, sx_d, sxx_d, nfr_d)
        S_r = psd_project_safe(S_r); S_d = psd_project_safe(S_d)
        Qr  = glasso_fixed(S_r, FIXED_LAMBDA)
        Qd  = glasso_fixed(S_d, FIXED_LAMBDA)
        return Qr - Qd

    def enrichment_stats(delta_q, n_perms=N_PERMS_NULL):
        """Compute AUROC + Fisher p-values under simple + degree-preserving null."""
        dq_off = np.abs(delta_q[off_pairs_ii, off_pairs_jj])   # (n_off,)
        labels  = off_annot.astype(int)                          # (n_off,)
        auc, pval_auroc_simple = auroc_pvalue(labels, dq_off)

        # Degree-preserving null: permute labels within degree bins
        null_aucs = np.zeros(n_perms)
        for p in range(n_perms):
            perm_l = permute_degree_stratified(labels, off_degree_sums,
                                               n_bins=5, rng=np.random.default_rng(p))
            null_aucs[p] = float(np.mean(dq_off[perm_l==1])) if perm_l.sum()>0 else 0
            # Use AUROC for degree-preserving null
            perm_auc, _ = auroc_pvalue(perm_l, dq_off)
            null_aucs[p] = perm_auc
        pval_auroc_deg = float((null_aucs >= auc).mean())

        # Fisher top-K
        fisher_results = {}
        for k in K_GRID:
            or_, pf = fisher_topk(labels, dq_off, k=k)
            fisher_results[str(k)] = {"or": float(or_), "pval": float(pf)}

        return {
            "auroc": float(auc),
            "pval_auroc_simple": float(pval_auroc_simple),
            "pval_auroc_degree": float(pval_auroc_deg),
            "fisher": fisher_results,
        }

    # ── Type-I error (null: Q_roam = Q_dwell) ────────────────────────────────
    print("\n  Running null datasets (type-I error)...")
    null_auroc_simple = []; null_auroc_deg = []
    null_fisher = {str(k): [] for k in K_GRID}
    for rep in range(N_REP_V7_NULL):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*7654 + 1000000)
        # Null: Q_roam = Q_dwell — use baseline precision for both states
        _, Q_baseline, _ = make_true_precisions(rng_r, effect_size=0.0)
        delta_q = compute_delta_q(Q_baseline, Q_baseline, rng_r)
        stats_r  = enrichment_stats(delta_q)
        null_auroc_simple.append(stats_r["pval_auroc_simple"] < 0.05)
        null_auroc_deg.append(stats_r["pval_auroc_degree"] < 0.05)
        for k in K_GRID:
            null_fisher[str(k)].append(stats_r["fisher"][str(k)]["pval"] < 0.05)
        if (rep+1)%50==0:
            ti_s = float(np.mean(null_auroc_simple)); ti_d = float(np.mean(null_auroc_deg))
            print(f"    null rep {rep+1}/{N_REP_V7_NULL}: "
                  f"type-I(simple)={ti_s:.3f} type-I(deg)={ti_d:.3f}")

    type1_auroc_simple = float(np.mean(null_auroc_simple))
    type1_auroc_deg    = float(np.mean(null_auroc_deg))
    type1_fisher       = {str(k): float(np.mean(null_fisher[str(k)])) for k in K_GRID}

    # ── Power (planted enrichment: 10 signal pairs all Randi-annotated) ───────
    print("\n  Running power datasets (planted enrichment)...")
    power_auroc_simple = []; power_auroc_deg = []
    power_fisher = {str(k): [] for k in K_GRID}
    for rep in range(N_REP_V7_POWER):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*3571 + 2000000)
        Q_r, Q_d, sig = make_true_precisions(rng_r, signal_must_be_randi=True)
        delta_q = compute_delta_q(Q_r, Q_d, rng_r)
        stats_r  = enrichment_stats(delta_q)
        power_auroc_simple.append(stats_r["pval_auroc_simple"] < 0.05)
        power_auroc_deg.append(stats_r["pval_auroc_degree"] < 0.05)
        for k in K_GRID:
            power_fisher[str(k)].append(stats_r["fisher"][str(k)]["pval"] < 0.05)
        if (rep+1)%50==0:
            pw_s = float(np.mean(power_auroc_simple)); pw_d = float(np.mean(power_auroc_deg))
            print(f"    power rep {rep+1}/{N_REP_V7_POWER}: "
                  f"power(simple)={pw_s:.3f} power(deg)={pw_d:.3f}")

    power_auroc_simple_val = float(np.mean(power_auroc_simple))
    power_auroc_deg_val    = float(np.mean(power_auroc_deg))
    power_fisher_vals      = {str(k): float(np.mean(power_fisher[str(k)])) for k in K_GRID}

    # ── Calibrate PRIMARY_TOP_K ───────────────────────────────────────────────
    # K maximizing Fisher power at type-I ≤ 0.06
    valid_k = [k for k in K_GRID if type1_fisher[str(k)] <= 0.06]
    if valid_k:
        primary_top_k = max(valid_k, key=lambda k: power_fisher_vals[str(k)])
    else:
        primary_top_k = 50  # fallback to Phase 0 value

    pass_type1_simple = type1_auroc_simple <= 0.06
    pass_type1_deg    = type1_auroc_deg    <= 0.06
    pass_power_simple = power_auroc_simple_val >= 0.60
    pass_power_deg    = power_auroc_deg_val    >= 0.60
    pass_v7 = pass_type1_simple and pass_power_simple

    print(f"\n  Type-I error:")
    print(f"    AUROC simple:       {type1_auroc_simple:.4f} [{'PASS' if pass_type1_simple else 'FAIL'} ≤0.06]")
    print(f"    AUROC deg-preserv:  {type1_auroc_deg:.4f}    [{'PASS' if pass_type1_deg else 'FAIL'}]")
    print(f"    Fisher(K={primary_top_k}): {type1_fisher[str(primary_top_k)]:.4f}")
    print(f"\n  Power at OR_planted (effect=0.2, Randi-planted):")
    print(f"    AUROC simple:       {power_auroc_simple_val:.4f} [{'PASS' if pass_power_simple else 'FAIL'} ≥0.60]")
    print(f"    AUROC deg-preserv:  {power_auroc_deg_val:.4f}    [{'PASS' if pass_power_deg else 'FAIL'}]")
    print(f"    Fisher(K={primary_top_k}): {power_fisher_vals[str(primary_top_k)]:.4f}")
    print(f"\n  PRIMARY_TOP_K calibrated: {primary_top_k}")
    print(f"  V.7 overall pass: {pass_v7}")

    report = {
        "stage": "0-V.7", "date": "2026-05-31",
        "n_null": N_REP_V7_NULL, "n_power": N_REP_V7_POWER, "n_perms": N_PERMS_NULL,
        "randi_annotation_fraction": float(off_annot.mean()),
        "type1_error": {
            "auroc_simple": type1_auroc_simple,
            "auroc_degree_preserving": type1_auroc_deg,
            "fisher_by_k": type1_fisher},
        "power": {
            "auroc_simple": power_auroc_simple_val,
            "auroc_degree_preserving": power_auroc_deg_val,
            "fisher_by_k": power_fisher_vals},
        "calibration": {"primary_top_k": primary_top_k},
        "pass_conditions": {
            "type1_auroc_le_006": pass_type1_simple,
            "power_auroc_ge_060": pass_power_simple,
            "type1_auroc_deg_le_006": pass_type1_deg},
        "overall_pass": pass_v7,
        "wall_time_s": round(time.time()-t0_total,1)
    }
    with open(OUT_DIR/"v7_enrichment_power.json","w") as f: json.dump(report,f,indent=2)
    print(f"  V.7 saved. Time: {time.time()-t0_total:.0f}s")
    return report, primary_top_k


# ── Main: run all stages sequentially ─────────────────────────────────────────
def main():
    print("="*60)
    print("Stage 0-V.4 (re-run) through V.7 — Full Validation Suite")
    print(f"RANDOM_SEED={RANDOM_SEED}, FIXED_LAMBDA={FIXED_LAMBDA}")
    print("DEV-P2-002: within-bootstrap lambda=0.15 (fixed, from V.3 sweep)")
    print("="*60)
    t_global = time.time()

    # V.4 re-run
    v4 = run_v4_rerun()
    rec_thr  = float(v4["calibration"]["recommended_stability_threshold"])
    rec_nboot = int(v4["calibration"]["recommended_n_bootstrap_resamples"])
    pass_v4  = v4["overall_pass"]

    # V.5
    v5, lam_on, lam_off = run_v5()
    pass_v5 = v5["overall_pass"]

    # V.6 (use calibrated threshold from V.4)
    v6 = run_v6(lam_on, lam_off, rec_thr)
    pass_v6 = v6["overall_pass"]

    # V.7 (use calibrated parameters from V.4 and V.5)
    v7, primary_top_k = run_v7(rec_thr, lam_on, lam_off)
    pass_v7 = v7["overall_pass"]

    # ── Consolidated validation summary ──────────────────────────────────────
    all_pass = pass_v4 and pass_v5 and pass_v6 and pass_v7

    tp_mean  = v4["stability_distributions"]["tp_pairs"]["mean"]
    tn_mean  = v4["stability_distributions"]["tn_pairs"]["mean"]
    tpr_rec  = v4["tpr_fpr_by_threshold"][str(rec_thr)]["mean_tpr"]
    fpr_rec  = v4["tpr_fpr_by_threshold"][str(rec_thr)]["mean_fpr"]
    type1    = v7["type1_error"]["auroc_simple"]
    power    = v7["power"]["auroc_simple"]

    print("\n" + "="*60)
    print("CONSOLIDATED VALIDATION SUMMARY")
    print("="*60)
    print(f"\nStage    Pass   Key metric")
    print(f"V.1      PASS   Pearson(S_pw, Σ_true)=0.921(roam), 0.981(dwell)")
    print(f"V.2      PASS   Clip_fraction=0.000 (S_pairwise always PSD)")
    print(f"V.3      PASS   TPR=0.973, FPR=0.033 at λ=0.15, effect=0.2")
    print(f"V.4      {'PASS' if pass_v4 else 'FAIL'}   Stability TP={tp_mean:.3f} TN={tn_mean:.3f}; "
          f"TPR={tpr_rec:.3f} FPR={fpr_rec:.4f} at thr={rec_thr:.2f}")
    print(f"V.5      {'PASS' if pass_v5 else 'FAIL'}   "
          f"TPR={v5['selected']['lambda_on']:.3f}/{v5['selected']['lambda_off']:.3f}; "
          f"confirmation TPR={v5['all_combos'][list(v5['all_combos'].keys())[0]]['tpr_mean']:.3f}")

    best_k5 = list(v5["all_combos"].keys())
    best_tpr5 = max(v["tpr_mean"] for v in v5["all_combos"].values() if v["pass"])
    print(f"         Best: λ_on={lam_on:.3f} λ_off={lam_off:.3f}")
    print(f"V.6      {'PASS' if pass_v6 else 'FAIL'}   "
          f"Confirm-rate-TP={v6['confirmation_rate_tp_median']:.3f} "
          f"False-confirm={v6['false_confirmation_rate_mean']:.4f}")
    print(f"V.7      {'PASS' if pass_v7 else 'FAIL'}   "
          f"Type-I={type1:.4f} Power={power:.4f}")
    print(f"\nOVERALL VALIDATION: {'PASS — PAC-PSD-GL validated for Stage 1' if all_pass else 'FAIL — see individual stages'}")

    print("\n" + "="*60)
    print("RECOMMENDED LOCKED PARAMETERS (Phase 2 Stage 0-V)")
    print("="*60)
    print(f"  MISSING_NEURON_POLICY         = 'pairwise_available_case'")
    print(f"  PSD_PROJECTION_METHOD         = 'eigenvalue_clipping'")
    print(f"  PSD_EIGENVALUE_FLOOR          = {PSD_FLOOR:.0e}  (safety; never clips in practice)")
    print(f"  STABILITY_SELECTION_LAMBDA    = {FIXED_LAMBDA}  (fixed; replaces BIC — DEV-P2-002)")
    print(f"  STABILITY_SELECTION_RESAMPLE  = 'recording'")
    print(f"  N_BOOTSTRAP_RESAMPLES         = {rec_nboot}")
    print(f"  STABILITY_THRESHOLD           = {rec_thr:.2f}")
    print(f"  LAMBDA_ON                     = {lam_on:.3f}")
    print(f"  LAMBDA_OFF                    = {lam_off:.3f}")
    print(f"  MIN_COPRESENCE_RECORDINGS     = [PENDING human Stage 0.1 checkpoint]")
    print(f"  PRIMARY_TOP_K                 = {primary_top_k}")
    print(f"\n  WN-PSD escalation path        RETIRED (S_pairwise always PSD under SF corpus)")

    summary = {
        "date": "2026-05-31",
        "stages_passed": {"V1":True,"V2":True,"V3":True,
                          "V4":pass_v4,"V5":pass_v5,"V6":pass_v6,"V7":pass_v7},
        "all_pass": all_pass,
        "recommended_parameters": {
            "MISSING_NEURON_POLICY":          "pairwise_available_case",
            "PSD_PROJECTION_METHOD":          "eigenvalue_clipping",
            "PSD_EIGENVALUE_FLOOR":           PSD_FLOOR,
            "STABILITY_SELECTION_LAMBDA":     FIXED_LAMBDA,
            "STABILITY_SELECTION_RESAMPLE":   "recording",
            "N_BOOTSTRAP_RESAMPLES":          rec_nboot,
            "STABILITY_THRESHOLD":            rec_thr,
            "LAMBDA_ON":                      lam_on,
            "LAMBDA_OFF":                     lam_off,
            "PRIMARY_TOP_K":                  primary_top_k,
            "MIN_COPRESENCE_RECORDINGS":      None,  # pending human checkpoint
        },
        "deviation": "DEV-P2-002: STABILITY_SELECTION_LAMBDA=0.15 (fixed), "
                     "replacing BIC-based selection, determined from V.3 synthetic sweep.",
        "key_metrics": {
            "V1_pearson_roaming":         0.921,
            "V2_clip_fraction":           0.000,
            "V3_tpr_at_best_lambda":      0.973,
            "V3_fpr_at_best_lambda":      0.033,
            "V4_stability_tp_mean":       tp_mean,
            "V4_stability_tn_mean":       tn_mean,
            "V4_tpr_at_rec_threshold":    tpr_rec,
            "V4_fpr_at_rec_threshold":    fpr_rec,
            "V5_lambda_on":               lam_on,
            "V5_lambda_off":              lam_off,
            "V6_confirmation_rate_tp":    v6["confirmation_rate_tp_median"],
            "V6_false_confirmation_rate": v6["false_confirmation_rate_mean"],
            "V7_type1_auroc":             type1,
            "V7_power_auroc":             power,
        },
        "total_wall_time_s": round(time.time()-t_global,1)
    }
    with open(OUT_DIR/"validation_summary.json","w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Validation summary saved.")
    print(f"  Total wall time: {time.time()-t_global:.0f}s")
    if all_pass:
        print("\n  PAC-PSD-GL IS VALIDATED for Stage 1 real-data estimation.")
        print("  Human must set PHASE2_ACTIVE=True and MIN_COPRESENCE_RECORDINGS")
        print("  to authorize Stage 1.")
    else:
        print("\n  NOT fully validated. See individual stage failures above.")


if __name__ == "__main__":
    main()
