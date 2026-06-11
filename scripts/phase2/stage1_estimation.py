"""Stage 1 — Real-data pairwise precision estimation.

Authorization: 2026-06-01, human supervisor.
PHASE2_ACTIVE must be True.

Scope (strictly):
  Step 1.1 — Sufficient statistics accumulation (CePNEM + raw GCaMP)
  Step 1.2 — Pairwise covariance assembly + PSD safeguard
  Step 1.3 — Discovery estimator (stability selection, 25 bootstraps, λ=0.15)
  Step 1.4 — Confirmation estimator (anatomy-guided ADMM, λ_on=0.01, λ_off=0.10)
  Step 1.5 — Diagnostics (PD, condition numbers, convergence)
  Step 1.6 — Stage 1 report (STOP SIGNAL — no Stage 2 without human review)

Produces 8 precision matrices:
  {cepnem, gcamp} × {roam, dwell} × {discovery, confirmation}

STOP AFTER REPORT. No ΔQ. No enrichment. No interpretation.
"""
from __future__ import annotations
import json, sys, time, warnings
from pathlib import Path
import h5py
import numpy as np
from sklearn.covariance import graphical_lasso

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase2_config as p2cfg
import phase0_config as p0cfg
assert p2cfg.PHASE2_ACTIVE, "PHASE2_ACTIVE must be True."

from scripts.stage06_neff_stationarity import ewma, segment, get_epoch_slices, SAMPLING_HZ
from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.phase1.stage0_cepnem import build_label_maps

# ── Locked parameters ────────────────────────────────────────────────────────
SAMPLING_HZ_ = SAMPLING_HZ            # 5.0
TAU    = p0cfg.EWMA_TIMESCALE_SECONDS  # 20.0 s
THR    = p0cfg.BEHAV_THRESHOLD         # 0.284
W_FR   = int(p0cfg.W_TRANS_SECONDS  * SAMPLING_HZ_)   # 50 frames
MB_FR  = int(p0cfg.MIN_BOUT_SECONDS  * SAMPLING_HZ_)   # 50 frames
N      = p2cfg.PHASE2_N_NEURONS        # 61
PSD_FLOOR   = p2cfg.PSD_EIGENVALUE_FLOOR       # 1e-6
LAM_DISC    = p2cfg.STABILITY_SELECTION_LAMBDA  # 0.15
N_BOOT      = p2cfg.N_BOOTSTRAP_RESAMPLES       # 25
STAB_THR    = p2cfg.STABILITY_THRESHOLD         # 0.75
LAM_ON      = p2cfg.LAMBDA_ON                   # 0.01
LAM_OFF     = p2cfg.LAMBDA_OFF                  # 0.10
MIN_COPRES  = p2cfg.MIN_COPRESENCE_RECORDINGS   # 9
SEED        = p0cfg.RANDOM_SEED

# ── Paths ────────────────────────────────────────────────────────────────────
H5_DIR     = ROOT / "data/atanas/AtanasKim-Cell2023"
LABEL_PATH = H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2"
RESID_DIR  = ROOT / "results/phase1/data/cepnem_residuals"
OUT_COV    = ROOT / "results/phase2/stage1/covariance"
OUT_PREC   = ROOT / "results/phase2/stage1/precision"
OUT_SUFF   = ROOT / "results/phase2/stage1/suff_stats"
OUT_DIR    = ROOT / "results/phase2/stage1"
for d in [OUT_COV, OUT_PREC, OUT_SUFF, OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Canonical neuron ordering ────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    _cop = json.load(f)
NEURONS_61 = _cop["neurons"]          # 61-element alphabetical list
REC_IDS    = _cop["recording_ids"]    # 40 recording IDs
N_REC      = len(REC_IDS)
L2I        = {lbl: i for i, lbl in enumerate(NEURONS_61)}  # label → 0-based index

A_raw = np.load("/tmp/A_raw_61.npy")  # (61, 61)

print(f"Stage 1 | N={N} neurons, N_REC={N_REC}")
print(f"  λ_disc={LAM_DISC}, N_boot={N_BOOT}, stab_thr={STAB_THR}")
print(f"  λ_on={LAM_ON}, λ_off={LAM_OFF}, min_copres={MIN_COPRES}")
print(f"  PSD_FLOOR={PSD_FLOOR}")

# ── Core utilities ───────────────────────────────────────────────────────────

def psd_project(S):
    S_sym = (S + S.T) / 2
    ev, vc = np.linalg.eigh(S_sym)
    n_clip = int((ev < PSD_FLOOR).sum())
    neg_mass = float(np.abs(np.minimum(ev, 0)).sum())
    S_proj = (vc @ np.diag(np.maximum(ev, PSD_FLOOR)) @ vc.T + S_sym.T) / 2
    return S_proj, {"n_clipped": n_clip, "neg_mass": neg_mass,
                    "min_ev_before": float(ev.min()), "max_ev": float(ev.max())}


def glasso_fit(S):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            Q, _ = graphical_lasso(S, alpha=LAM_DISC, max_iter=500, tol=1e-4)
            return Q, True
        except Exception:
            return np.eye(N), False


def admm_z(S_proj, lam_on, lam_off, rho=1.0, max_iter=1000, tol=1e-5):
    L = np.where(A_raw > 0, lam_on, lam_off).astype(float)
    np.fill_diagonal(L, 0.0)
    Theta = np.eye(N); Z = np.eye(N); U = np.zeros((N, N))
    for _ in range(max_iter):
        B = Z - U - S_proj / rho; B = (B + B.T) / 2
        ev, vc = np.linalg.eigh(B)
        Theta = vc @ np.diag((ev + np.sqrt(ev**2 + 4/rho)) / 2) @ vc.T
        W = Theta + U
        Z_new = np.sign(W) * np.maximum(np.abs(W) - L/rho, 0.0)
        Z_new[np.arange(N), np.arange(N)] = W[np.arange(N), np.arange(N)]
        res = Theta - Z_new; U += res; Z = Z_new
        if np.max(np.abs(res)) < tol:
            return Z, True
    return Z, False


def matrix_diag(Q, name):
    ev = np.linalg.eigvalsh(Q)
    is_pd  = bool(ev.min() > 0)
    is_sym = bool(np.max(np.abs(Q - Q.T)) < 1e-10)
    cond   = float(ev.max() / max(ev.min(), 1e-15)) if is_pd else float("inf")
    n_nonzero = int((np.abs(Q - np.diag(np.diag(Q))) > 1e-9).sum()) // 2
    print(f"  {name}: PD={is_pd}, cond={cond:.2e}, n_edges={n_nonzero}, "
          f"min_ev={ev.min():.3e}")
    return {"name": name, "is_pd": is_pd, "is_symmetric": is_sym,
            "condition_number": cond, "min_eigenvalue": float(ev.min()),
            "max_eigenvalue": float(ev.max()), "n_nonzero_off_diag": n_nonzero}


# ── Step 0: Build label maps (for raw GCaMP column mapping) ──────────────────
print("\n[Step 0] Building label maps from JLD2 ...")
t0 = time.time()
label_records = decode_atanas_jld2(LABEL_PATH)
label_maps    = build_label_maps(label_records, H5_DIR)
print(f"  Done. {len(label_maps)} recordings mapped. {time.time()-t0:.1f}s")


# ── Steps 1.1 + 1.2: Sufficient stats + covariance assembly ─────────────────
#   Outer loop over coordinates; PSD diagnostics accumulated across both.

psd_diag_all = {}   # accumulate all (coord, state) PSD info here

for coord in ["cepnem", "gcamp"]:
    print(f"\n{'='*60}")
    print(f"[Step 1.1] Sufficient statistics — {coord}")
    t_coord = time.time()

    # Per-recording, per-neuron, per-state sufficient statistics
    # Shapes: (N_REC, 61, 2)  — axis 2: 0=dwell, 1=roam
    suf_xi   = np.zeros((N_REC, N, 2), dtype=np.float64)  # sum x_i
    suf_xii  = np.zeros((N_REC, N, 2), dtype=np.float64)  # sum x_i^2
    suf_xixj = np.zeros((N_REC, N, N, 2), dtype=np.float64)  # sum x_i*x_j
    n_frames = np.zeros((N_REC, N, 2), dtype=np.int64)    # frame count

    for r_idx, rec_id in enumerate(REC_IDS):
        h5_path  = H5_DIR / f"{rec_id}-data.h5"
        npz_path = RESID_DIR / f"{rec_id}.npz"

        with h5py.File(h5_path, "r") as hf:
            v_raw = hf["behavior/velocity"][:]
            if coord == "gcamp":
                trace_h5 = hf["gcamp/trace_array"][:]

        lbl_arr, ret = segment(v_raw, TAU, THR, W_FR, MB_FR)

        npz     = np.load(npz_path)
        ep_mask = npz["epoch_mask"]    # (T,) bool
        sub_lbl = list(npz["neuron_labels"])
        T_rec   = len(v_raw)

        # Build (T, 61) neural data array — NaN for absent neurons
        X_full = np.full((T_rec, N), np.nan, dtype=np.float64)
        if coord == "cepnem":
            resid = npz["residual"]    # (T, n_rec)
            for j, lbl in enumerate(sub_lbl):
                if lbl in L2I:
                    X_full[:, L2I[lbl]] = resid[:, j]
            valid_base = ret & ep_mask
        else:
            col_map = label_maps.get(rec_id, {})
            for lbl, h5_col in col_map.items():
                if lbl in L2I:
                    X_full[:, L2I[lbl]] = trace_h5[:, h5_col]
            valid_base = ret

        # Per-state accumulation
        for s_int in [0, 1]:  # 0=dwell, 1=roam
            valid_s = valid_base & (lbl_arr == s_int)
            if valid_s.sum() == 0:
                continue
            X_s = X_full[valid_s, :]           # (n_valid, 61)
            present = ~np.isnan(X_s[0, :])    # (61,) — same for all frames (per-recording)
            pidx    = np.where(present)[0]     # indices of present neurons
            if len(pidx) == 0:
                continue

            # Diagonal sufficient stats
            for i in pidx:
                xi = X_s[:, i]
                n_frames[r_idx, i, s_int] = len(xi)
                suf_xi[r_idx, i, s_int]   = xi.sum()
                suf_xii[r_idx, i, s_int]  = (xi ** 2).sum()

            # Off-diagonal cross-products
            X_pres = X_s[:, pidx]             # (n_valid, n_present)
            XXT    = X_pres.T @ X_pres         # (n_present, n_present)
            for ki, i in enumerate(pidx):
                suf_xixj[r_idx, i, pidx, s_int] += XXT[ki, :]

        if (r_idx + 1) % 10 == 0:
            print(f"    {r_idx+1}/{N_REC} done ({time.time()-t_coord:.1f}s)")

    np.save(OUT_SUFF / f"n_frames_{coord}.npy",  n_frames)
    np.save(OUT_SUFF / f"suf_xi_{coord}.npy",    suf_xi)
    np.save(OUT_SUFF / f"suf_xii_{coord}.npy",   suf_xii)
    np.save(OUT_SUFF / f"suf_xixj_{coord}.npy",  suf_xixj)
    print(f"  Sufficient stats saved. {time.time()-t_coord:.1f}s")

    # ── Step 1.2: Pairwise covariance assembly + PSD projection ──────────────
    print(f"\n[Step 1.2] Pairwise covariance assembly — {coord}")

    for s_int, state in [(0, "dwell"), (1, "roam")]:
        S = np.zeros((N, N), dtype=np.float64)

        # Off-diagonal
        for i in range(N):
            for j in range(i + 1, N):
                copres = (n_frames[:, i, s_int] > 0) & (n_frames[:, j, s_int] > 0)
                if copres.sum() < MIN_COPRES:
                    continue
                T_tot = int(n_frames[copres, i, s_int].sum())
                if T_tot < 2:
                    continue
                Sxi  = float(suf_xi[copres, i, s_int].sum())
                Sxj  = float(suf_xi[copres, j, s_int].sum())
                Sxij = float(suf_xixj[copres, i, j, s_int].sum())
                mi   = Sxi / T_tot; mj = Sxj / T_tot
                cov  = (Sxij - T_tot * mi * mj) / (T_tot - 1)
                S[i, j] = S[j, i] = cov

        # Diagonal
        for i in range(N):
            pres_r = n_frames[:, i, s_int] > 0
            T_i    = int(n_frames[pres_r, i, s_int].sum())
            if T_i < 2:
                S[i, i] = 1.0; continue
            Sxi  = float(suf_xi[pres_r, i, s_int].sum())
            Sxii = float(suf_xii[pres_r, i, s_int].sum())
            mi   = Sxi / T_i
            var  = (Sxii - T_i * mi**2) / (T_i - 1)
            S[i, i] = var if var > 0 else 1.0

        np.save(OUT_COV / f"S_{coord}_{state}.npy", S)

        off_mask = ~np.eye(N, dtype=bool)
        off_vals = S[off_mask]
        print(f"  S_{coord}_{state}: diag=[{np.diag(S).min():.3f}, {np.diag(S).max():.3f}]"
              f"  off=[{off_vals.min():.4f}, {off_vals.max():.4f}]")

        S_proj, psd_info = psd_project(S)
        psd_info["coord"] = coord; psd_info["state"] = state
        psd_diag_all[f"{coord}_{state}"] = psd_info
        np.save(OUT_COV / f"S_{coord}_{state}_proj.npy", S_proj)

        if psd_info["n_clipped"] > 0:
            print(f"  *** PSD HALT: {psd_info['n_clipped']} eigenvalues clipped "
                  f"(min={psd_info['min_ev_before']:.4e}) for {coord}_{state} ***")
            print(f"  *** Synthetic baseline was 0 clipped. Flag for report review. ***")
        else:
            print(f"  S_{coord}_{state}_proj: 0 eigenvalues clipped (PSD safe)")

    # ── Step 1.3: Stability selection (discovery estimator) ──────────────────
    print(f"\n[Step 1.3] Stability selection — {coord}")
    rng = np.random.default_rng(SEED + (0 if coord == "cepnem" else 99991))

    # Identify contributing recordings per state (for THIS coordinate)
    roam_recs  = [r for r in range(N_REC) if n_frames[r, :, 1].sum() > 0]
    dwell_recs = [r for r in range(N_REC) if n_frames[r, :, 0].sum() > 0]
    K_roam  = len(roam_recs);  Kb_roam  = K_roam  // 2
    K_dwell = len(dwell_recs); Kb_dwell = K_dwell // 2
    print(f"  Roam: {K_roam} recs → {Kb_roam}/boot | Dwell: {K_dwell} recs → {Kb_dwell}/boot")

    def assemble_S(boot_recs, s_int):
        """Build pairwise covariance from a subset of recordings."""
        bm = np.zeros(N_REC, dtype=bool); bm[boot_recs] = True
        S_b = np.zeros((N, N), dtype=np.float64)
        for i in range(N):
            for j in range(i + 1, N):
                cp = bm & (n_frames[:, i, s_int] > 0) & (n_frames[:, j, s_int] > 0)
                if cp.sum() < 1: continue
                T = int(n_frames[cp, i, s_int].sum())
                if T < 2: continue
                Sxi  = float(suf_xi[cp, i, s_int].sum())
                Sxj  = float(suf_xi[cp, j, s_int].sum())
                Sxij = float(suf_xixj[cp, i, j, s_int].sum())
                mi   = Sxi/T; mj = Sxj/T
                S_b[i,j] = S_b[j,i] = (Sxij - T*mi*mj)/(T-1)
            pres = bm & (n_frames[:, i, s_int] > 0)
            Ti = int(n_frames[pres, i, s_int].sum())
            if Ti < 2: S_b[i,i] = 1.0; continue
            Sxi  = float(suf_xi[pres, i, s_int].sum())
            Sxii = float(suf_xii[pres, i, s_int].sum())
            mi   = Sxi/Ti
            v    = (Sxii - Ti*mi**2)/(Ti-1)
            S_b[i,i] = v if v > 0 else 1.0
        return S_b

    sel_counts = {0: np.zeros((N, N), dtype=np.int32),
                  1: np.zeros((N, N), dtype=np.int32)}
    conv_counts = {0: 0, 1: 0}
    t_disc = time.time()

    for b in range(N_BOOT):
        for s_int, all_recs, K_b in [(1, roam_recs, Kb_roam),
                                      (0, dwell_recs, Kb_dwell)]:
            boot = rng.choice(all_recs, size=K_b, replace=False).tolist()
            S_b  = assemble_S(boot, s_int)
            S_bp, _ = psd_project(S_b)
            Q_b, conv = glasso_fit(S_bp)
            if conv:
                conv_counts[s_int] += 1
                sel = (np.abs(Q_b) > 1e-8).astype(np.int32)
                np.fill_diagonal(sel, 0)
                sel_counts[s_int] += sel

        if (b + 1) % 5 == 0:
            print(f"    boot {b+1}/{N_BOOT}  "
                  f"roam_conv={conv_counts[1]}/{b+1}  "
                  f"dwell_conv={conv_counts[0]}/{b+1}  "
                  f"{time.time()-t_disc:.0f}s")

    for s_int, state in [(1, "roam"), (0, "dwell")]:
        nc = conv_counts[s_int]
        stab = sel_counts[s_int].astype(float) / max(nc, 1)
        np.fill_diagonal(stab, 0.0)
        np.save(OUT_PREC / f"stab_{coord}_{state}.npy", stab)

        Q_disc = np.zeros((N, N), dtype=np.float64)
        Q_disc[stab >= STAB_THR] = stab[stab >= STAB_THR]
        np.fill_diagonal(Q_disc, 0.0)
        np.save(OUT_PREC / f"Q_{coord}_{state}_disc.npy", Q_disc)

        n_edges = int((stab >= STAB_THR).sum()) // 2
        print(f"  stab_{coord}_{state}: {n_edges} stable edges, "
              f"max_stab={stab.max():.3f}, conv={nc}/{N_BOOT}")

    print(f"  Stability selection done. {time.time()-t_disc:.0f}s")

    # ── Step 1.4: ADMM confirmation estimator ────────────────────────────────
    print(f"\n[Step 1.4] ADMM confirmation — {coord}")
    t_conf = time.time()
    for state in ["roam", "dwell"]:
        S_proj = np.load(OUT_COV / f"S_{coord}_{state}_proj.npy")
        Q_conf, converged = admm_z(S_proj, LAM_ON, LAM_OFF)
        np.save(OUT_PREC / f"Q_{coord}_{state}_conf.npy", Q_conf)
        n_edges = int((np.abs(Q_conf - np.diag(np.diag(Q_conf))) > 1e-9).sum()) // 2
        print(f"  Q_{coord}_{state}_conf: converged={converged}, {n_edges} edges")
        if not converged:
            print(f"  WARNING: ADMM did not converge for {coord}_{state}!")
    print(f"  ADMM done. {time.time()-t_conf:.0f}s")

# Write accumulated PSD diagnostics
with open(OUT_COV / "psd_diagnostics.json", "w") as f:
    json.dump(psd_diag_all, f, indent=2)
print(f"\nPSD diagnostics saved.")


# ── Step 1.5: Diagnostics ────────────────────────────────────────────────────
print("\n[Step 1.5] Precision matrix diagnostics ...")
diag_records = []
HALT_FLAGS   = []

for coord in ["cepnem", "gcamp"]:
    for state in ["roam", "dwell"]:
        for etype in ["disc", "conf"]:
            fpath = OUT_PREC / f"Q_{coord}_{state}_{etype}.npy"
            if not fpath.exists():
                HALT_FLAGS.append(f"MISSING: Q_{coord}_{state}_{etype}.npy")
                continue
            Q = np.load(fpath)
            d = matrix_diag(Q, f"Q_{coord}_{state}_{etype}")
            diag_records.append(d)
            if not d["is_pd"]:
                HALT_FLAGS.append(
                    f"NOT_PD: Q_{coord}_{state}_{etype} (min_ev={d['min_eigenvalue']:.3e})")
            if d["condition_number"] > 1e6:
                HALT_FLAGS.append(
                    f"HIGH_COND: Q_{coord}_{state}_{etype} (cond={d['condition_number']:.2e})")

for key, info in psd_diag_all.items():
    if info["n_clipped"] > 0:
        HALT_FLAGS.append(
            f"PSD_CLIP: {key} — {info['n_clipped']} eigenvalues clipped "
            f"(min_ev={info['min_ev_before']:.3e})")

stage1_diag = {
    "date": "2026-06-01",
    "precision_diagnostics": diag_records,
    "psd_diagnostics": psd_diag_all,
    "halt_flags": HALT_FLAGS,
    "halt_triggered": len(HALT_FLAGS) > 0,
    "parameters": {
        "LAMBDA_DISC": LAM_DISC, "N_BOOT": N_BOOT, "STAB_THR": STAB_THR,
        "LAMBDA_ON": LAM_ON, "LAMBDA_OFF": LAM_OFF,
        "PSD_FLOOR": PSD_FLOOR, "MIN_COPRES": MIN_COPRES,
    },
}
with open(OUT_DIR / "stage1_diagnostics.json", "w") as f:
    json.dump(stage1_diag, f, indent=2)

if HALT_FLAGS:
    print(f"\n*** HALT CONDITIONS: ***")
    for flag in HALT_FLAGS: print(f"  {flag}")


# ── Step 1.6: Stage 1 report ─────────────────────────────────────────────────
print("\n[Step 1.6] Writing Stage 1 report ...")

def _bool_str(b): return "YES" if b else "**NO**"

lines = [
    "# Stage 1 Report — Pairwise Precision Estimation",
    f"Date: 2026-06-01",
    "",
]
if HALT_FLAGS:
    lines.append("**STATUS: HALT CONDITIONS PRESENT — Stage 2 blocked pending human review**")
else:
    lines.append("**STATUS: Stage 1 complete — awaiting human authorization for Stage 2**")
lines += ["", "## Precision Matrix Diagnostics", "",
          "| Matrix | PD | Cond. | min_ev | n_edges |",
          "|---|---|---|---|---|"]
for d in diag_records:
    lines.append(f"| {d['name']} | {_bool_str(d['is_pd'])} | "
                 f"{d['condition_number']:.2e} | {d['min_eigenvalue']:.3e} | "
                 f"{d['n_nonzero_off_diag']} |")

lines += ["", "## PSD Projection (covariance assembly)", "",
          "Synthetic baseline: 0 eigenvalues clipped.",
          "",
          "| Key | Clipped | min_ev before |",
          "|---|---|---|"]
for key, info in psd_diag_all.items():
    lines.append(f"| {key} | {info['n_clipped']} | {info['min_ev_before']:.4e} |")

lines += ["", "## Stability Selection Summary", "",
          "| Coord | State | Stable edges | max_stab |",
          "|---|---|---|---|"]
for coord in ["cepnem", "gcamp"]:
    for state in ["roam", "dwell"]:
        sp = OUT_PREC / f"stab_{coord}_{state}.npy"
        if sp.exists():
            stab = np.load(sp)
            ne = int((stab >= STAB_THR).sum()) // 2
            lines.append(f"| {coord} | {state} | {ne} | {stab.max():.3f} |")

lines += ["", "## Halt Conditions", ""]
if HALT_FLAGS:
    for f in HALT_FLAGS: lines.append(f"- **{f}**")
else:
    lines.append("None. All precision matrices PD and well-conditioned.")

lines += ["", "## Output Files", ""]
for coord in ["cepnem", "gcamp"]:
    for state in ["roam", "dwell"]:
        for et in ["disc", "conf"]:
            fp = OUT_PREC / f"Q_{coord}_{state}_{et}.npy"
            lines.append(f"- {'✓' if fp.exists() else '✗'} Q_{coord}_{state}_{et}.npy")

lines += ["", "## Next Step", ""]
if HALT_FLAGS:
    lines.append("Stage 2 **BLOCKED**. Human must review halt conditions and authorize explicitly.")
else:
    lines.append(
        "Stage 2 (ΔQ computation) requires **explicit human authorization**. "
        "Review this report. Record authorization in PHASE2_CHECKPOINT_LOG.md. "
        "Do NOT begin Stage 2 automatically."
    )
lines += ["", "---",
          "*Stage 1 scope: covariance assembly, PSD projection, stability selection, "
          "ADMM confirmation. No ΔQ, enrichment, or interpretation.*"]

with open(OUT_DIR / "stage1_report.md", "w") as f:
    f.write("\n".join(lines))

print(f"\n{'='*70}")
print("STAGE 1 COMPLETE.")
print(f"Halt flags: {HALT_FLAGS if HALT_FLAGS else 'None'}")
print("Report: results/phase2/stage1/stage1_report.md")
print("Human review required before Stage 2. Do NOT proceed automatically.")
print("="*70)
