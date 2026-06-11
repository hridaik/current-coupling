"""Stage 0-V.5 through V.7 — with corrected anatomy ADMM (return Z, not Theta).

V.4 re-run results (from stage0v_4re_through_7.py):
  STABILITY_THRESHOLD = 0.75 (Youden-optimal, pass confirmed)
  N_BOOTSTRAP_RESAMPLES = 25 (variance converged)
  TP stability mean = 0.945, TN stability mean = 0.039
  V.4 PASS.

Bug fix applied here:
  anatomy_admm_z() returns Z (exact zeros) not Theta (ADMM residuals ≈1e-4).
  This was causing FPR≈1.0 in V.5 (all Theta entries > 1e-8 even when Z=0).
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
from src.enrichment  import auroc_pvalue, fisher_topk
from src.null_models import permute_simple, permute_degree_stratified

RANDOM_SEED   = cfg.RANDOM_SEED
N             = 61
N_REC         = 40
PSD_FLOOR     = 1e-6
FIXED_LAMBDA  = 0.15
EFFECT_SIZE   = 0.2
P_SIGNAL      = 10
N_RANDI_PAIRS = 189

N_REP_V5 = 50
LAMBDA_ON_GRID = [0.01, 0.02, 0.04, 0.08]
RATIO_GRID     = [5, 10, 15, 20]
N_REP_V6 = 50
N_BOOT_V6 = 50
STABILITY_THRESHOLD = 0.75  # from V.4 re-run
N_REP_V7_NULL  = 200
N_REP_V7_POWER = 200
N_PERMS_NULL   = 1000
K_GRID = [20, 30, 40, 50, 60, 70, 80]

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

presence     = np.load("/tmp/presence_matrix.npy")
roam_frames  = np.load("/tmp/roam_frames.npy")
dwell_frames = np.load("/tmp/dwell_frames.npy")
A_raw        = np.load("/tmp/A_raw_61.npy")
roam_avail   = (presence & (roam_frames  > 0)[:, None]).astype(bool)
dwell_avail  = (presence & (dwell_frames > 0)[:, None]).astype(bool)
ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)
off_mask = A_raw[ii_all, jj_all] == 0
on_mask  = ~off_mask
off_pairs_ii = ii_all[off_mask]; off_pairs_jj = jj_all[off_mask]
n_off = int(off_mask.sum()); n_on = int(on_mask.sum())
roam_rec_indices  = np.where(roam_frames  > 0)[0]
dwell_rec_indices = np.where(dwell_frames > 0)[0]
K_roam  = len(roam_rec_indices); K_dwell = len(dwell_rec_indices)
K_boot_roam = K_roam // 2; K_boot_dwell = K_dwell // 2

rng_annot = np.random.default_rng(RANDOM_SEED + 77777)
randi_annot = np.zeros(n_pairs, dtype=bool)
randi_annot[:N_RANDI_PAIRS] = True; rng_annot.shuffle(randi_annot)
degree_A = A_raw.sum(axis=1)
pair_degree_sums = degree_A[ii_all] + degree_A[jj_all]
off_annot    = randi_annot[off_mask]
off_deg_sums = pair_degree_sums[off_mask]
print(f"Randi: {randi_annot.sum()} / {n_pairs} pairs annotated; "
      f"off-connectome: {off_annot.sum()} / {n_off}")


# ── Shared utilities (identical to previous scripts) ─────────────────────────

def make_true_precisions(rng, effect_size=EFFECT_SIZE, p_signal=P_SIGNAL,
                         signal_must_be_randi=False):
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
    d = np.sqrt(np.diag(Sigma_raw))
    Sigma_corr = Sigma_raw / np.outer(d, d)
    Q_corr = np.linalg.inv(Sigma_corr)
    Q_true_dwell = Q_corr.copy()
    if signal_must_be_randi:
        ri = np.where(off_annot)[0]
        si = rng.choice(len(ri), size=p_signal, replace=False)
        sig_ii = off_pairs_ii[ri[si]]; sig_jj = off_pairs_jj[ri[si]]
    else:
        si = rng.choice(n_off, size=p_signal, replace=False)
        sig_ii = off_pairs_ii[si]; sig_jj = off_pairs_jj[si]
    Q_true_roam = Q_true_dwell.copy()
    for a,b in zip(sig_ii, sig_jj): Q_true_roam[a,b]+=effect_size; Q_true_roam[b,a]+=effect_size
    me_r = np.linalg.eigvalsh(Q_true_roam).min()
    if me_r < 0.05: Q_true_roam += (0.05-me_r+0.01)*np.eye(N)
    return Q_true_roam, Q_true_dwell, np.column_stack([sig_ii, sig_jj])


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
        mi=Sxi/T_ij; mj=Sxj/T_ij; S=(Sxixj-T_ij*mi*mj)/np.maximum(T_ij-1,1)
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


def anatomy_admm_z(S_proj, lambda_on, lambda_off, rho=1.0, max_iter=500, tol=1e-4):
    """Anatomy-guided ADMM returning Z (the exactly-sparse variable).

    Bug fix: the Phase 0 _glasso_admm returns Theta (positive definite intermediate
    variable) which has ADMM residuals ~1e-4 even for entries that should be zero.
    This function returns Z (soft-thresholded variable) which has exact zeros,
    correctly reflecting the regularized solution.
    """
    Lambda = np.where(A_raw > 0, lambda_on, lambda_off).astype(float)
    np.fill_diagonal(Lambda, 0.0)
    Theta = np.eye(N); Z = np.eye(N); U = np.zeros((N, N))
    for _ in range(max_iter):
        B = Z - U - S_proj / rho; B = (B + B.T) / 2
        ev, vc = np.linalg.eigh(B)
        new_ev = (ev + np.sqrt(ev**2 + 4.0/rho)) / 2.0
        Theta = vc @ np.diag(new_ev) @ vc.T
        W = Theta + U
        Z_new = np.sign(W) * np.maximum(np.abs(W) - Lambda/rho, 0.0)
        Z_new[np.arange(N), np.arange(N)] = W[np.arange(N), np.arange(N)]
        res = Theta - Z_new; U = U + res; Z = Z_new
        if np.max(np.abs(res)) < tol: break
    return Z   # ← exactly sparse (zeros where regularized)


def sig_set_from(signal_pairs):
    return {(int(min(p[0],p[1])), int(max(p[0],p[1]))) for p in signal_pairs.tolist()}


def tpr_fpr_from_Z(signal_pairs, Z_mat):
    """TPR and FPR using Z (exact zeros) for edge selection."""
    sig = sig_set_from(signal_pairs)
    sel = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
           if abs(Z_mat[ii_all[k],jj_all[k]]) > 1e-9}
    tp     = len(sig & sel)
    fp_off = sum(1 for p in sel if p not in sig
                 and A_raw[p[0],p[1]]==0 and A_raw[p[1],p[0]]==0)
    return tp/P_SIGNAL, fp_off/max(n_off-P_SIGNAL, 1)


def full_data_S(Q_true_s, state_frames, avail, rng_r):
    sx, sxx, nfr = compute_suff_stats(Q_true_s, state_frames, avail, rng_r)
    S = assemble_from_suff(state_frames>0, avail, sx, sxx, nfr)
    return psd_project_safe(S), sx, sxx, nfr


# ── Stage 0-V.5: Anatomy-guided lasso calibration ────────────────────────────
def run_v5():
    print("\n" + "="*60)
    print(f"Stage 0-V.5 — Anatomy-Guided Lasso Calibration (Z-based selection)")
    print(f"N_REP={N_REP_V5}, {len(LAMBDA_ON_GRID)}×{len(RATIO_GRID)}=16 combos")
    print("="*60)
    t0 = time.time()

    combo_results = {}
    for lam_on in LAMBDA_ON_GRID:
        for ratio in RATIO_GRID:
            lam_off = lam_on * ratio
            tpr_list, fpr_list = [], []
            for rep in range(N_REP_V5):
                rng_r = np.random.default_rng(RANDOM_SEED + rep*9001 + int(lam_on*1e5) + ratio)
                Q_r, Q_d, sig = make_true_precisions(rng_r)
                S_proj,_,_,_ = full_data_S(Q_r, roam_frames, roam_avail, rng_r)
                Z_conf = anatomy_admm_z(S_proj, lam_on, lam_off)
                tpr, fpr = tpr_fpr_from_Z(sig, Z_conf)
                tpr_list.append(tpr); fpr_list.append(fpr)
            key = f"lon={lam_on:.3f}_loff={lam_off:.4f}"
            combo_results[key] = {
                "lambda_on": lam_on, "lambda_off": lam_off, "ratio": ratio,
                "tpr_mean": float(np.mean(tpr_list)), "tpr_std": float(np.std(tpr_list)),
                "fpr_mean": float(np.mean(fpr_list)), "fpr_std": float(np.std(fpr_list)),
                "pass": float(np.mean(tpr_list)) >= 0.50 and float(np.mean(fpr_list)) <= 0.10
            }

    print(f"\n  λ_on   ratio   TPR    FPR    pass")
    passing = []; all_combos = list(combo_results.items())
    for k, v in sorted(all_combos, key=lambda x: x[1]["lambda_on"]):
        ok = v["pass"]
        if ok: passing.append((v["tpr_mean"], k))
        print(f"  {v['lambda_on']:.3f}  ×{v['ratio']:>2}   "
              f"{v['tpr_mean']:.3f}  {v['fpr_mean']:.4f}  "
              f"[{'PASS' if ok else 'fail'}]")

    # Selection rule per Stage 0.3 spec: maximize TPR subject to FPR ≤ 0.05
    fpr_strict = [(v["tpr_mean"], k) for k, v in combo_results.items()
                  if v["tpr_mean"] >= 0.50 and v["fpr_mean"] <= 0.05]
    if fpr_strict:
        # Prefer FPR ≤ 0.05 constraint (more conservative, lower false confirmation)
        fpr_strict.sort(key=lambda x: -x[0])
        best_key = fpr_strict[0][1]
    elif passing:
        # Relax to FPR ≤ 0.10 if nothing passes FPR ≤ 0.05
        passing.sort(key=lambda x: -x[0])
        best_key = passing[0][1]
    else:
        # No combination passes — pick the one with smallest FPR
        best_key = min(combo_results, key=lambda k: combo_results[k]["fpr_mean"])
        print(f"  WARNING: no combination passed. Selecting minimum FPR: {best_key}")

    best = combo_results[best_key]
    pass_v5 = best["pass"]
    print(f"\n  Selected: λ_on={best['lambda_on']:.3f}  λ_off={best['lambda_off']:.4f}  "
          f"ratio={best['ratio']}")
    print(f"  TPR={best['tpr_mean']:.3f}  FPR={best['fpr_mean']:.4f}  "
          f"[{'PASS' if pass_v5 else 'FAIL'}]")

    report = {
        "stage": "0-V.5", "date": "2026-05-31", "n_rep": N_REP_V5,
        "selection_method": "Z-variable from ADMM (exact zeros)",
        "all_combos": combo_results,
        "selected": {"lambda_on": best["lambda_on"], "lambda_off": best["lambda_off"],
                     "ratio": best["ratio"], "tpr": best["tpr_mean"], "fpr": best["fpr_mean"]},
        "overall_pass": pass_v5,
        "wall_time_s": round(time.time()-t0, 1)
    }
    with open(OUT_DIR/"v5_anatomy_guided.json","w") as f: json.dump(report, f, indent=2)
    print(f"  V.5 saved. Time: {time.time()-t0:.0f}s")
    return report, best["lambda_on"], best["lambda_off"]


# ── Stage 0-V.6: Circularity control ─────────────────────────────────────────
def run_v6(lambda_on, lambda_off):
    print("\n" + "="*60)
    print(f"Stage 0-V.6 — Circularity Control")
    print(f"N_REP={N_REP_V6}, N_BOOT={N_BOOT_V6}, "
          f"stab_thr={STABILITY_THRESHOLD}, λ_on={lambda_on:.3f}, λ_off={lambda_off:.4f}")
    print("="*60)
    t0 = time.time()

    confirm_tp, false_conf, disc_tp = [], [], []
    for rep in range(N_REP_V6):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*54321 + 800000)
        Q_r, Q_d, sig = make_true_precisions(rng_r)
        sig_s = sig_set_from(sig)
        sx, sxx, nfr = compute_suff_stats(Q_r, roam_frames, roam_avail, rng_r)
        S_full = assemble_from_suff(roam_frames>0, roam_avail, sx, sxx, nfr)
        S_full = psd_project_safe(S_full)
        # Discovery: stability selection with FIXED_LAMBDA
        sel_b = np.zeros((N_BOOT_V6, N, N), dtype=np.int8)
        rng_b = np.random.default_rng(RANDOM_SEED + rep*54321 + 900000)
        for b in range(N_BOOT_V6):
            boot_recs = rng_b.choice(roam_rec_indices, size=K_boot_roam, replace=False)
            bm = np.zeros(N_REC, dtype=bool); bm[boot_recs] = True
            S_b = assemble_from_suff(bm, roam_avail, sx, sxx, nfr)
            S_b = psd_project_safe(S_b)
            Q_b = glasso_fixed(S_b, FIXED_LAMBDA)
            sb = (np.abs(Q_b)>1e-8).astype(np.int8); np.fill_diagonal(sb,0); sel_b[b]=sb
        stab = sel_b.mean(axis=0)
        disc_set = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
                    if stab[ii_all[k],jj_all[k]] >= STABILITY_THRESHOLD}
        # Confirmation: anatomy-guided ADMM (Z-based)
        Z_conf = anatomy_admm_z(S_full, lambda_on, lambda_off)
        conf_set = {(int(ii_all[k]),int(jj_all[k])) for k in range(n_pairs)
                    if abs(Z_conf[ii_all[k],jj_all[k]]) > 1e-9}
        tp_disc = sig_s & disc_set
        tp_both = sig_s & disc_set & conf_set
        tn_off_conf = sum(1 for p in conf_set if p not in sig_s
                          and A_raw[p[0],p[1]]==0 and A_raw[p[1],p[0]]==0)
        cr = len(tp_both)/max(len(tp_disc),1) if tp_disc else np.nan
        fc = tn_off_conf / max(n_off-P_SIGNAL, 1)
        dtp = len(tp_disc)/P_SIGNAL
        if not np.isnan(cr): confirm_tp.append(cr)
        false_conf.append(fc); disc_tp.append(dtp)

    med_cr  = float(np.nanmedian(confirm_tp)) if confirm_tp else 0.0
    mean_fc = float(np.mean(false_conf))
    mean_dtp = float(np.mean(disc_tp))
    pass_cr = med_cr  >= 0.70
    pass_fc = mean_fc <= 0.05
    pass_v6 = pass_cr and pass_fc

    print(f"\n  Discovery TPR: {mean_dtp:.3f}")
    print(f"  Confirmation rate TP: {med_cr:.3f} [{'PASS' if pass_cr else 'FAIL'} ≥0.70]")
    print(f"  False confirmation:   {mean_fc:.4f} [{'PASS' if pass_fc else 'FAIL'} ≤0.05]")
    print(f"  V.6 pass: {pass_v6}")
    report = {
        "stage": "0-V.6", "date": "2026-05-31",
        "n_rep": N_REP_V6, "n_boot": N_BOOT_V6,
        "stability_threshold": STABILITY_THRESHOLD,
        "lambda_on": lambda_on, "lambda_off": lambda_off,
        "discovery_tpr_mean": mean_dtp,
        "confirmation_rate_tp_median": med_cr,
        "false_confirmation_rate_mean": mean_fc,
        "pass_conditions": {"confirm_ge_070": pass_cr, "false_le_005": pass_fc},
        "overall_pass": pass_v6, "wall_time_s": round(time.time()-t0,1)
    }
    with open(OUT_DIR/"v6_circularity.json","w") as f: json.dump(report, f, indent=2)
    print(f"  V.6 saved. Time: {time.time()-t0:.0f}s")
    return report


# ── Stage 0-V.7: Enrichment test calibration ─────────────────────────────────
def run_v7(lambda_on, lambda_off):
    print("\n" + "="*60)
    print(f"Stage 0-V.7 — Enrichment Test Calibration")
    print(f"N_null={N_REP_V7_NULL}, N_power={N_REP_V7_POWER}, N_perms={N_PERMS_NULL}")
    print("="*60)
    t0 = time.time()

    rng_perm = np.random.default_rng(RANDOM_SEED + 999999)

    def compute_delta_q(Q_r, Q_d, rng_rep):
        sx_r, sxx_r, nfr_r = compute_suff_stats(Q_r, roam_frames,  roam_avail,  rng_rep)
        sx_d, sxx_d, nfr_d = compute_suff_stats(Q_d, dwell_frames, dwell_avail, rng_rep)
        S_r = psd_project_safe(assemble_from_suff(roam_frames>0,  roam_avail,  sx_r, sxx_r, nfr_r))
        S_d = psd_project_safe(assemble_from_suff(dwell_frames>0, dwell_avail, sx_d, sxx_d, nfr_d))
        Qr = glasso_fixed(S_r, FIXED_LAMBDA); Qd = glasso_fixed(S_d, FIXED_LAMBDA)
        return Qr - Qd

    def enrichment_stats(delta_q):
        dq_off  = np.abs(delta_q[off_pairs_ii, off_pairs_jj])
        labels  = off_annot.astype(int)
        auc, p_simple = auroc_pvalue(labels, dq_off)

        # Simple permutation null for AUROC
        null_aucs = np.zeros(N_PERMS_NULL)
        for p_i in range(N_PERMS_NULL):
            perm = permute_simple(labels, rng=np.random.default_rng(p_i))
            null_aucs[p_i], _ = auroc_pvalue(perm, dq_off)
        p_simple_perm = float((null_aucs >= auc).mean())

        # Degree-preserving null for AUROC
        null_aucs_deg = np.zeros(N_PERMS_NULL)
        for p_i in range(N_PERMS_NULL):
            perm = permute_degree_stratified(labels, off_deg_sums, n_bins=5,
                                             rng=np.random.default_rng(p_i + N_PERMS_NULL))
            null_aucs_deg[p_i], _ = auroc_pvalue(perm, dq_off)
        p_deg_perm = float((null_aucs_deg >= auc).mean())

        # Fisher top-K
        fisher_results = {}
        for k in K_GRID:
            or_, pf = fisher_topk(labels, dq_off, k=k)
            fisher_results[str(k)] = {"or": float(or_), "pval": float(pf)}

        return {"auroc": float(auc), "p_simple": p_simple_perm, "p_degree": p_deg_perm,
                "fisher": fisher_results}

    # Type-I error
    print("\n  Type-I error runs...")
    null_rej_s, null_rej_d = [], []
    null_fisher_rej = {str(k): [] for k in K_GRID}
    for rep in range(N_REP_V7_NULL):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*7654 + 1000000)
        _, Q_base, _ = make_true_precisions(rng_r, effect_size=0.0)
        dq = compute_delta_q(Q_base, Q_base, rng_r)
        st = enrichment_stats(dq)
        null_rej_s.append(st["p_simple"] < 0.05)
        null_rej_d.append(st["p_degree"] < 0.05)
        for k in K_GRID: null_fisher_rej[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep+1)%50==0:
            print(f"    null {rep+1}/{N_REP_V7_NULL}: "
                  f"type-I(simple)={np.mean(null_rej_s):.3f} "
                  f"type-I(deg)={np.mean(null_rej_d):.3f}")

    t1_s = float(np.mean(null_rej_s)); t1_d = float(np.mean(null_rej_d))
    t1_fisher = {str(k): float(np.mean(null_fisher_rej[str(k)])) for k in K_GRID}

    # Power
    print("\n  Power runs...")
    pow_rej_s, pow_rej_d = [], []
    pow_fisher_rej = {str(k): [] for k in K_GRID}
    for rep in range(N_REP_V7_POWER):
        rng_r = np.random.default_rng(RANDOM_SEED + rep*3571 + 2000000)
        Q_r, Q_d, _ = make_true_precisions(rng_r, signal_must_be_randi=True)
        dq = compute_delta_q(Q_r, Q_d, rng_r)
        st = enrichment_stats(dq)
        pow_rej_s.append(st["p_simple"] < 0.05)
        pow_rej_d.append(st["p_degree"] < 0.05)
        for k in K_GRID: pow_fisher_rej[str(k)].append(st["fisher"][str(k)]["pval"] < 0.05)
        if (rep+1)%50==0:
            print(f"    power {rep+1}/{N_REP_V7_POWER}: "
                  f"power(simple)={np.mean(pow_rej_s):.3f} "
                  f"power(deg)={np.mean(pow_rej_d):.3f}")

    pw_s = float(np.mean(pow_rej_s)); pw_d = float(np.mean(pow_rej_d))
    pw_fisher = {str(k): float(np.mean(pow_fisher_rej[str(k)])) for k in K_GRID}

    # Calibrate PRIMARY_TOP_K
    valid_k = [k for k in K_GRID if t1_fisher[str(k)] <= 0.06]
    if valid_k:
        primary_top_k = max(valid_k, key=lambda k: pw_fisher[str(k)])
    else:
        primary_top_k = 50

    pass_t1s = t1_s <= 0.06; pass_t1d = t1_d <= 0.06
    pass_pws = pw_s >= 0.60; pass_pwd = pw_d >= 0.60
    pass_v7  = pass_t1s and pass_pws

    print(f"\n  Type-I error:  simple={t1_s:.4f}[{'P' if pass_t1s else 'F'}]  "
          f"deg={t1_d:.4f}[{'P' if pass_t1d else 'F'}]")
    print(f"  Power:         simple={pw_s:.4f}[{'P' if pass_pws else 'F'}]  "
          f"deg={pw_d:.4f}[{'P' if pass_pwd else 'F'}]")
    print(f"  PRIMARY_TOP_K calibrated: {primary_top_k}  "
          f"(type-I={t1_fisher[str(primary_top_k)]:.4f} power={pw_fisher[str(primary_top_k)]:.4f})")
    print(f"  V.7 pass: {pass_v7}")

    report = {
        "stage": "0-V.7", "date": "2026-05-31",
        "n_null": N_REP_V7_NULL, "n_power": N_REP_V7_POWER, "n_perms": N_PERMS_NULL,
        "type1_error": {"auroc_simple": t1_s, "auroc_degree": t1_d, "fisher": t1_fisher},
        "power":       {"auroc_simple": pw_s, "auroc_degree": pw_d, "fisher": pw_fisher},
        "calibration": {"primary_top_k": primary_top_k},
        "pass_conditions": {"t1_simple_le_006": pass_t1s, "power_simple_ge_060": pass_pws,
                            "t1_deg_le_006": pass_t1d, "power_deg_ge_060": pass_pwd},
        "overall_pass": pass_v7, "wall_time_s": round(time.time()-t0, 1)
    }
    with open(OUT_DIR/"v7_enrichment_power.json","w") as f: json.dump(report, f, indent=2)
    print(f"  V.7 saved. Time: {time.time()-t0:.0f}s")
    return report, primary_top_k


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*60)
    print("Stage 0-V.5 through V.7")
    print("V.4 re-run results loaded from v4_stability_rerun.json")
    print(f"STABILITY_THRESHOLD={STABILITY_THRESHOLD} (from V.4)")
    print("Bug fix: anatomy_admm_z() returns Z (exact zeros), not Theta")
    print("="*60)
    t_global = time.time()

    # Load V.4 re-run results
    with open(OUT_DIR/"v4_stability_rerun.json") as f:
        v4 = json.load(f)
    print(f"\nV.4 (loaded): TP={v4['stability_distributions']['tp_pairs']['mean']:.3f} "
          f"TN={v4['stability_distributions']['tn_pairs']['mean']:.3f} "
          f"pass={v4['overall_pass']}")

    v5, lam_on, lam_off = run_v5()
    v6 = run_v6(lam_on, lam_off)
    v7, ptk = run_v7(lam_on, lam_off)

    # Consolidated summary
    all_pass = v4["overall_pass"] and v5["overall_pass"] and v6["overall_pass"] and v7["overall_pass"]

    tp_m = v4["stability_distributions"]["tp_pairs"]["mean"]
    tn_m = v4["stability_distributions"]["tn_pairs"]["mean"]
    tpr_rec = v4["tpr_fpr_by_threshold"][str(STABILITY_THRESHOLD)]["mean_tpr"]
    fpr_rec = v4["tpr_fpr_by_threshold"][str(STABILITY_THRESHOLD)]["mean_fpr"]

    print("\n" + "="*60)
    print("FULL VALIDATION SUMMARY — Stage 0-V.1 through V.7")
    print("="*60)
    print(f"\nStage  Pass   Key metric")
    print(f"V.1    PASS   Pearson(S_pw,Σ_true): 0.921(roam) 0.981(dwell)")
    print(f"V.2    PASS   Clip_fraction=0.000 (S_pairwise always PSD; floor=1e-6 safety)")
    print(f"V.3    PASS   TPR=0.973 FPR=0.033 at λ=0.15, effect=0.2 (100 reps)")
    print(f"V.4    {'PASS' if v4['overall_pass'] else 'FAIL'}   "
          f"Stab TP={tp_m:.3f} TN={tn_m:.3f}; "
          f"TPR={tpr_rec:.3f} FPR={fpr_rec:.4f} at thr={STABILITY_THRESHOLD}")
    print(f"V.5    {'PASS' if v5['overall_pass'] else 'FAIL'}   "
          f"λ_on={lam_on:.3f} λ_off={lam_off:.4f}; "
          f"TPR={v5['selected']['tpr']:.3f} FPR={v5['selected']['fpr']:.4f}")
    print(f"V.6    {'PASS' if v6['overall_pass'] else 'FAIL'}   "
          f"Confirm-TP={v6['confirmation_rate_tp_median']:.3f} "
          f"False-confirm={v6['false_confirmation_rate_mean']:.4f}")
    print(f"V.7    {'PASS' if v7['overall_pass'] else 'FAIL'}   "
          f"Type-I={v7['type1_error']['auroc_simple']:.4f} "
          f"Power={v7['power']['auroc_simple']:.4f}")

    print(f"\nOVERALL: {'PASS' if all_pass else 'FAIL'}")

    print("\n" + "="*60)
    print("RECOMMENDED LOCKED PARAMETERS")
    print("="*60)
    params = {
        "MISSING_NEURON_POLICY":        "pairwise_available_case",
        "PSD_PROJECTION_METHOD":        "eigenvalue_clipping",
        "PSD_EIGENVALUE_FLOOR":         PSD_FLOOR,
        "STABILITY_SELECTION_LAMBDA":   FIXED_LAMBDA,
        "STABILITY_SELECTION_RESAMPLE": "recording",
        "N_BOOTSTRAP_RESAMPLES":        v4["calibration"]["recommended_n_bootstrap_resamples"],
        "STABILITY_THRESHOLD":          STABILITY_THRESHOLD,
        "LAMBDA_ON":                    lam_on,
        "LAMBDA_OFF":                   lam_off,
        "MIN_COPRESENCE_RECORDINGS":    None,   # pending human Stage 0.1 checkpoint
        "PRIMARY_TOP_K":                ptk,
    }
    for k, v in params.items():
        print(f"  {k:<38} = {v}")

    summary = {
        "date": "2026-05-31",
        "stages": {
            "V1": {"pass": True, "pearson_roaming": 0.921, "pearson_dwelling": 0.981},
            "V2": {"pass": True, "clip_fraction": 0.000, "note": "S_pairwise always PSD"},
            "V3": {"pass": True, "tpr_at_lambda_015": 0.973, "fpr_at_lambda_015": 0.033},
            "V4": {"pass": v4["overall_pass"],
                   "stability_tp_mean": tp_m, "stability_tn_mean": tn_m,
                   "tpr_at_thr": tpr_rec, "fpr_at_thr": fpr_rec},
            "V5": {"pass": v5["overall_pass"],
                   "lambda_on": lam_on, "lambda_off": lam_off,
                   "tpr": v5["selected"]["tpr"], "fpr": v5["selected"]["fpr"]},
            "V6": {"pass": v6["overall_pass"],
                   "confirmation_rate_tp": v6["confirmation_rate_tp_median"],
                   "false_confirmation_rate": v6["false_confirmation_rate_mean"]},
            "V7": {"pass": v7["overall_pass"],
                   "type1_auroc_simple": v7["type1_error"]["auroc_simple"],
                   "power_auroc_simple": v7["power"]["auroc_simple"]},
        },
        "all_pass": all_pass,
        "recommended_parameters": params,
        "deviations": ["DEV-P2-002: STABILITY_SELECTION_LAMBDA=0.15 (fixed, from V.3 sweep)"],
        "wn_psd_status": "RETIRED — S_pairwise always PSD under SF corpus",
        "total_wall_time_s": round(time.time()-t_global, 1)
    }
    with open(OUT_DIR/"validation_summary.json","w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  validation_summary.json saved. Total: {time.time()-t_global:.0f}s")
    if all_pass:
        print("\n  PAC-PSD-GL IS VALIDATED for Stage 1.")
        print("  Human must: (1) set MIN_COPRESENCE_RECORDINGS, (2) set PHASE2_ACTIVE=True.")
    else:
        print("\n  One or more stages failed. See above.")


if __name__ == "__main__":
    main()
