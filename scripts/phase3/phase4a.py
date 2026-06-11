"""Phase 4A — ADEL–URY Activity Organization.

Authorization: Phase 4A, 2026-06-04.

Analyses A–E using CePNEM residuals and behavioral state labels.
Target neurons: ADEL, URYVR, URYDL, URXL, RMEL, RMER.
Recordings: all 22 with complete target coverage.

PROHIBITIONS: No held-out evaluation. No model fitting. No perturbation predictions.
No revisiting Ω or enrichment.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import signal, stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.stage06_neff_stationarity import segment, SAMPLING_HZ
import phase0_config as p0cfg

OUT4A = ROOT / "results/phase4a"
OUT4A.mkdir(parents=True, exist_ok=True)

RESID_DIR = ROOT / "results/phase1/data/cepnem_residuals"
H5_DIR    = ROOT / "data/atanas/AtanasKim-Cell2023"
TAU = p0cfg.EWMA_TIMESCALE_SECONDS; THR = p0cfg.BEHAV_THRESHOLD
W_FR = int(p0cfg.W_TRANS_SECONDS * SAMPLING_HZ)
MB_FR = int(p0cfg.MIN_BOUT_SECONDS * SAMPLING_HZ)

with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
REC_IDS = cop["recording_ids"]
n2i = {n: i for i, n in enumerate(NEURONS)}

TARGET  = ["ADEL", "URYVR", "URYDL", "URXL", "RMEL", "RMER"]
COLORS  = {"ADEL": "#e31a1c", "URYVR": "#1f78b4", "URYDL": "#33a02c",
           "URXL": "#ff7f00", "RMEL": "#6a3d9a", "RMER": "#b15928"}
STATE_COLORS = {0: "#4393c3", 1: "#d6604d"}  # dwell=blue, roam=red

# ── Load all recordings with full target coverage ─────────────────────────────
print("Loading recordings ...")
recordings: list[dict] = []
for rec_id in REC_IDS:
    npz_path = RESID_DIR / f"{rec_id}.npz"
    if not npz_path.exists(): continue
    npz = np.load(npz_path)
    labels_in_rec = set(npz["neuron_labels"])
    if not all(n in labels_in_rec for n in TARGET): continue

    h5_path = H5_DIR / f"{rec_id}-data.h5"
    with h5py.File(h5_path, "r") as hf:
        v_raw = hf["behavior/velocity"][:]
    lbl_arr, ret = segment(v_raw, TAU, THR, W_FR, MB_FR)

    resid   = npz["residual"].astype(float)
    sub_lbl = list(npz["neuron_labels"])
    T = len(v_raw)
    X = {}
    for j, n in enumerate(sub_lbl):
        if n in set(TARGET):
            X[n] = resid[:, j]

    recordings.append({
        "rec_id": rec_id, "T": T, "lbl": lbl_arr, "X": X,
        "n_roam": int((lbl_arr==1).sum()), "n_dwell": int((lbl_arr==0).sum()),
    })

N_REC = len(recordings)
print(f"Loaded {N_REC} recordings with all 6 target neurons.")

# =============================================================================
# ANALYSIS A — State-Conditioned Activity Profiles
# =============================================================================
print("\n" + "="*70); print("Analysis A — Activity Profiles")

# Per-neuron, per-state statistics accumulated across recordings
stats_A: dict[str, dict[int, list]] = {n: {0: [], 1: []} for n in TARGET}

for rec in recordings:
    lbl = rec["lbl"]
    for s in [0, 1]:
        mask = lbl == s
        if mask.sum() < 10: continue
        for n in TARGET:
            if n not in rec["X"]: continue
            x = rec["X"][n][mask]
            x = x[np.isfinite(x)]
            if len(x) < 5: continue
            stats_A[n][s].append({
                "mean": float(np.mean(x)),
                "var":  float(np.var(x)),
                "cv":   float(np.abs(np.std(x)/np.mean(x))) if np.abs(np.mean(x)) > 1e-6 else np.nan,
                "q25":  float(np.percentile(x, 25)),
                "q75":  float(np.percentile(x, 75)),
                "n":    len(x),
            })

# Aggregate
def agg(vals, key):
    v = [d[key] for d in vals if np.isfinite(d[key])]
    return float(np.nanmean(v)), float(np.nanstd(v)) if len(v) > 1 else 0.0

print("\nMean activity (±sd across recordings):")
A_summary = {}
for n in TARGET:
    r_mean, r_sd = agg(stats_A[n][1], "mean")
    d_mean, d_sd = agg(stats_A[n][0], "mean")
    r_var, _ = agg(stats_A[n][1], "var")
    d_var, _ = agg(stats_A[n][0], "var")
    r_cv, _ = agg(stats_A[n][1], "cv")
    d_cv, _ = agg(stats_A[n][0], "cv")
    print(f"  {n:8s}: roam_mean={r_mean:+.3f}(±{r_sd:.3f})  "
          f"dwell_mean={d_mean:+.3f}(±{d_sd:.3f})  "
          f"Δmean={r_mean-d_mean:+.3f}")
    A_summary[n] = {"roam_mean": r_mean, "roam_sd": r_sd,
                    "dwell_mean": d_mean, "dwell_sd": d_sd,
                    "roam_var": r_var, "dwell_var": d_var,
                    "roam_cv": r_cv, "dwell_cv": d_cv}

# Test: is there significant state difference?
print("\nPaired t-test (roam vs dwell mean across recordings):")
A_tests = {}
for n in TARGET:
    roam_means = [d["mean"] for d in stats_A[n][1] if np.isfinite(d["mean"])]
    dwell_means = [d["mean"] for d in stats_A[n][0] if np.isfinite(d["mean"])]
    if len(roam_means) < 3 or len(dwell_means) < 3:
        print(f"  {n}: insufficient data"); continue
    # Paired: match by index
    pairs = list(zip(roam_means[:len(dwell_means)], dwell_means[:len(roam_means)]))
    rm = [p[0] for p in pairs]; dm = [p[1] for p in pairs]
    t, p = stats.ttest_rel(rm, dm)
    print(f"  {n:8s}: t={t:+.2f}  p={p:.4f}  d={np.mean(rm)-np.mean(dm):+.3f}  "
          f"{'*' if p<0.05 else 'ns'}")
    A_tests[n] = {"t": float(t), "p": float(p)}

# FIGURE A1
fig, axes = plt.subplots(2, 3, figsize=(12, 7))
for ax, n in zip(axes.flat, TARGET):
    roam_means = [d["mean"] for d in stats_A[n][1]]
    dwell_means = [d["mean"] for d in stats_A[n][0]]
    rm = np.array([x for x in roam_means if np.isfinite(x)])
    dm = np.array([x for x in dwell_means if np.isfinite(x)])
    x_r = np.random.default_rng(42).uniform(-0.1, 0.1, len(rm))
    x_d = np.random.default_rng(43).uniform(-0.1, 0.1, len(dm))
    ax.scatter(np.zeros(len(dm)) + x_d, dm, color=STATE_COLORS[0], alpha=0.4, s=20, label="Dwell")
    ax.scatter(np.ones(len(rm))  + x_r, rm, color=STATE_COLORS[1], alpha=0.4, s=20, label="Roam")
    ax.errorbar([0,1], [dm.mean(), rm.mean()], [dm.std()/len(dm)**0.5, rm.std()/len(rm)**0.5],
                fmt='o-', color='k', zorder=5, linewidth=2, markersize=8)
    ax.set_title(n, fontsize=12, color=COLORS[n], fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Dwell", "Roam"])
    ax.set_ylabel("CePNEM residual" if ax in axes[:,0] else "")
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    p = A_tests.get(n, {}).get("p", 1.0)
    if p < 0.001: sig = "***"
    elif p < 0.01: sig = "**"
    elif p < 0.05: sig = "*"
    else: sig = "ns"
    ax.text(0.5, 0.95, sig, transform=ax.transAxes, ha='center', va='top', fontsize=14)
axes[0,2].legend(loc='upper right', fontsize=8)
fig.suptitle("FigA1: Per-Neuron Activity — Roaming vs Dwelling\n"
             "(each point = one recording mean; error bars = SEM of recording means)", fontsize=11)
plt.tight_layout()
fig.savefig(OUT4A / "FigA1_state_profiles.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved FigA1")

# =============================================================================
# ANALYSIS B — State-Conditioned Cross-Correlation
# =============================================================================
print("\n" + "="*70); print("Analysis B — Cross-Correlations")

PAIRS_B = [("ADEL","URYVR"), ("ADEL","URYDL"), ("ADEL","URXL"), ("ADEL","RMEL")]
LAG_FRAMES = 50   # ±10 s at 5 Hz
lags = np.arange(-LAG_FRAMES, LAG_FRAMES+1) / SAMPLING_HZ  # in seconds

def xcorr_normalized(a, b, maxlag):
    """Normalized cross-correlation at lags -maxlag..+maxlag."""
    a = (a - np.mean(a)) / (np.std(a) + 1e-12)
    b = (b - np.mean(b)) / (np.std(b) + 1e-12)
    full = np.correlate(a, b, mode="full")
    n_full = len(full)
    center = n_full // 2
    c = full[center-maxlag:center+maxlag+1] / len(a)
    return c

xcorr_all: dict[tuple, dict[int, list]] = {p: {0:[], 1:[]} for p in PAIRS_B}

for rec in recordings:
    lbl = rec["lbl"]
    for s in [0, 1]:
        mask = lbl == s
        idx = np.where(mask)[0]
        if len(idx) < 2*LAG_FRAMES + 10: continue
        # Use consecutive epochs within state
        for n1, n2 in PAIRS_B:
            if n1 not in rec["X"] or n2 not in rec["X"]: continue
            x1 = rec["X"][n1]; x2 = rec["X"][n2]
            x1_s = x1[mask]; x2_s = x2[mask]
            valid = np.isfinite(x1_s) & np.isfinite(x2_s)
            if valid.sum() < 2*LAG_FRAMES + 10: continue
            x1_v = x1_s[valid]; x2_v = x2_s[valid]
            if len(x1_v) < 2*LAG_FRAMES + 10: continue
            c = xcorr_normalized(x1_v, x2_v, LAG_FRAMES)
            xcorr_all[(n1,n2)][s].append(c)

# Aggregate
B_summary = {}
for pair in PAIRS_B:
    for s, sname in [(0,"dwell"), (1,"roam")]:
        cs = xcorr_all[pair][s]
        if not cs: continue
        C = np.array(cs)
        mean_c = C.mean(axis=0)
        sem_c  = C.std(axis=0) / C.shape[0]**0.5
        peak_val = float(mean_c.max())
        peak_lag = float(lags[np.argmax(mean_c)])
        key = f"{pair[0]}-{pair[1]}_{sname}"
        B_summary[key] = {
            "mean_xcorr": mean_c.tolist(),
            "sem_xcorr":  sem_c.tolist(),
            "peak_corr": peak_val, "peak_lag_s": peak_lag,
            "n_epochs": len(cs),
        }
        print(f"  {pair[0]}–{pair[1]} [{sname}]: peak={peak_val:.3f} at lag={peak_lag:.1f}s "
              f"(n_recs={len(cs)})")

# FIGURE A2
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, (n1, n2) in zip(axes.flat, PAIRS_B):
    for s, sname, color in [(0,"Dwell",STATE_COLORS[0]),(1,"Roam",STATE_COLORS[1])]:
        key = f"{n1}-{n2}_{sname}"
        if key not in B_summary: continue
        bs = B_summary[key]
        m = np.array(bs["mean_xcorr"]); se = np.array(bs["sem_xcorr"])
        ax.plot(lags, m, color=color, label=f"{sname} (peak={bs['peak_corr']:.2f})", linewidth=2)
        ax.fill_between(lags, m-se, m+se, color=color, alpha=0.15)
    ax.axhline(0, color='gray', linewidth=0.5); ax.axvline(0, color='k', linewidth=0.5, linestyle='--')
    ax.set_title(f"ADEL × {n2}", fontsize=11)
    ax.set_xlabel("Lag (s)"); ax.set_ylabel("Normalized Xcorr")
    ax.legend(fontsize=8)
fig.suptitle("FigA2: State-Conditioned Cross-Correlations\n"
             "(shaded: ±1 SEM across recordings)", fontsize=11)
plt.tight_layout()
fig.savefig(OUT4A / "FigA2_crosscorrelations.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved FigA2")

# =============================================================================
# ANALYSIS C — State-Transition Trajectories
# =============================================================================
print("\n" + "="*70); print("Analysis C — Transition Trajectories")

WIN = 300  # ±60 s at 5 Hz
# Transitions: 0→1 (dwell→roam) and 1→0 (roam→dwell)
TRANS_NEURONS = ["ADEL", "URYVR", "URYDL", "URXL", "RMEL"]
t_axis = np.arange(-WIN, WIN+1) / SAMPLING_HZ   # in seconds

traj: dict[str, dict[str, list]] = {
    "D2R": {n: [] for n in TRANS_NEURONS},  # dwell→roam
    "R2D": {n: [] for n in TRANS_NEURONS},  # roam→dwell
}
n_trans_D2R = 0; n_trans_R2D = 0

for rec in recordings:
    lbl = rec["lbl"]; T = rec["T"]
    # Find transition frames: frame t where lbl switches (excluding transitions = -1)
    for t in range(1, T):
        if lbl[t-1] < 0 or lbl[t] < 0: continue
        if lbl[t-1] == lbl[t]: continue
        trans_type = "D2R" if (lbl[t-1]==0 and lbl[t]==1) else "R2D"
        if t < WIN or t + WIN >= T: continue
        for n in TRANS_NEURONS:
            if n not in rec["X"]: continue
            seg = rec["X"][n][t-WIN:t+WIN+1].copy()
            if np.isnan(seg).mean() > 0.3: continue   # skip if >30% NaN
            # Interpolate short NaN gaps
            nans = np.isnan(seg)
            x_idx = np.arange(len(seg))
            if nans.sum() > 0:
                seg[nans] = np.interp(x_idx[nans], x_idx[~nans], seg[~nans])
            # Z-score relative to pre-window baseline (first 60 frames)
            baseline_mean = np.nanmean(seg[:60])
            baseline_std  = np.nanstd(seg[:60])
            if baseline_std > 1e-8:
                seg = (seg - baseline_mean) / baseline_std
            else:
                seg = seg - baseline_mean
            traj[trans_type][n].append(seg)
        if trans_type == "D2R": n_trans_D2R += 1
        else: n_trans_R2D += 1

print(f"Found {n_trans_D2R} dwell→roam transitions, {n_trans_R2D} roam→dwell transitions")

# Average trajectories
C_summary = {}
for ttype in ["D2R", "R2D"]:
    C_summary[ttype] = {}
    for n in TRANS_NEURONS:
        segs = traj[ttype][n]
        if not segs: continue
        arr = np.array(segs)
        C_summary[ttype][n] = {
            "mean": arr.mean(axis=0).tolist(),
            "sem":  (arr.std(axis=0) / arr.shape[0]**0.5).tolist(),
            "n": len(segs),
        }
    print(f"  {ttype}: n_ADEL={len(traj[ttype].get('ADEL',[]))}")

# Identify which neuron changes first: find time of max |deflection| in each transition type
def time_of_change(mean_traj, t_axis, pre_win=50, post_win=100):
    """Find frame (relative to 0) where trajectory first exceeds 0.5 std from baseline."""
    baseline = np.abs(mean_traj[WIN-pre_win:WIN]).mean()
    post = mean_traj[WIN:WIN+post_win]
    thresh = max(0.3, 2*baseline)
    for i, v in enumerate(post):
        if abs(v) > thresh:
            return float(t_axis[WIN+i])
    return None

print("\nEstimated onset times (seconds from transition):")
for ttype in ["D2R", "R2D"]:
    print(f"  {ttype}:")
    onsets = {}
    for n in TRANS_NEURONS:
        if n not in C_summary[ttype]: continue
        mt = np.array(C_summary[ttype][n]["mean"])
        t_on = time_of_change(mt, t_axis)
        onsets[n] = t_on
        print(f"    {n:8s}: onset≈{t_on:.1f}s" if t_on is not None else f"    {n:8s}: no clear onset")

# FIGURE A3
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, ttype, title in zip(axes, ["D2R", "R2D"],
                              ["Dwell → Roam", "Roam → Dwell"]):
    for n in TRANS_NEURONS:
        if n not in C_summary[ttype]: continue
        d = C_summary[ttype][n]
        m = np.array(d["mean"]); se = np.array(d["sem"])
        ax.plot(t_axis, m, color=COLORS.get(n,"gray"), label=n, linewidth=2)
        ax.fill_between(t_axis, m-se, m+se, color=COLORS.get(n,"gray"), alpha=0.12)
    ax.axvline(0, color='k', linewidth=1.5, linestyle='--', label="transition")
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvspan(-60, 0, alpha=0.04, color=STATE_COLORS[0 if ttype=="D2R" else 1])
    ax.axvspan(0, 60, alpha=0.04, color=STATE_COLORS[1 if ttype=="D2R" else 0])
    ax.set_xlabel("Time from transition (s)"); ax.set_ylabel("Activity (z-scored to pre-window)")
    ax.set_title(f"{title} (n_transitions≈{n_trans_D2R if ttype=='D2R' else n_trans_R2D})",
                 fontsize=11)
    ax.legend(fontsize=8, loc='upper right' if ttype=="R2D" else 'upper left')
    ax.set_xlim(-60, 60)
fig.suptitle("FigA3: State-Transition Trajectories\n"
             "(activity z-scored to 10s pre-window baseline; shaded: ±1 SEM)", fontsize=11)
plt.tight_layout()
fig.savefig(OUT4A / "FigA3_transition_trajectories.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved FigA3")

# =============================================================================
# ANALYSIS D — Module-Level Activity
# =============================================================================
print("\n" + "="*70); print("Analysis D — Module-Level Activity")

DA_MECH = ["ADEL"]   # only ADEL from DA_mech is in TARGET; CEP neurons add noise
URY_URX = ["URYVR", "URYDL", "URXL"]

# Compute module traces for each recording
D_corrs = []  # within-recording module correlation
paired_corrs = []  # (roam_r, dwell_r) per recording for paired analysis
D_corrs_roam = []; D_corrs_dwell = []

for rec in recordings:
    lbl = rec["lbl"]; T = rec["T"]
    da_trace = rec["X"].get("ADEL", np.full(T, np.nan))
    ury_traces = [rec["X"].get(n, np.full(T, np.nan)) for n in URY_URX]
    with np.errstate(all='ignore'):
        ury_mean = np.nanmean(ury_traces, axis=0)

    valid = np.isfinite(da_trace) & np.isfinite(ury_mean)
    if valid.sum() < 50: continue
    r_all,  _ = stats.pearsonr(da_trace[valid], ury_mean[valid])
    D_corrs.append(float(r_all))

    r_s = {}
    for s in [0, 1]:
        mask = (lbl == s) & valid
        if mask.sum() < 20: continue
        r, _ = stats.pearsonr(da_trace[mask], ury_mean[mask])
        r_s[s] = float(r)
    if 0 in r_s: D_corrs_dwell.append(r_s[0])
    if 1 in r_s: D_corrs_roam.append(r_s[1])
    if 0 in r_s and 1 in r_s:
        paired_corrs.append((r_s[0], r_s[1]))

print(f"  Mean ADEL vs URY_URX correlation:")
print(f"    Overall:  {np.mean(D_corrs):+.3f} (±{np.std(D_corrs):.3f})")
print(f"    Roaming:  {np.mean(D_corrs_roam):+.3f} (±{np.std(D_corrs_roam):.3f})  n={len(D_corrs_roam)}")
print(f"    Dwelling: {np.mean(D_corrs_dwell):+.3f} (±{np.std(D_corrs_dwell):.3f})  n={len(D_corrs_dwell)}")

t_corr, p_corr = stats.ttest_ind(D_corrs_roam, D_corrs_dwell)
print(f"  t-test roam vs dwell correlation: t={t_corr:.2f}  p={p_corr:.4f}")

D_summary = {
    "corr_overall_mean": float(np.mean(D_corrs)),
    "corr_roam_mean":    float(np.mean(D_corrs_roam)),
    "corr_dwell_mean":   float(np.mean(D_corrs_dwell)),
    "p_state_diff":      float(p_corr),
}

# FIGURE A4
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
ax = axes[0]
x = np.random.default_rng(44).uniform(-0.1,0.1, len(D_corrs_roam))
ax.scatter(np.zeros(len(D_corrs_dwell)), D_corrs_dwell, color=STATE_COLORS[0],
           alpha=0.5, s=30, label=f"Dwell (n={len(D_corrs_dwell)})")
ax.scatter(np.ones(len(D_corrs_roam)) + x, D_corrs_roam, color=STATE_COLORS[1],
           alpha=0.5, s=30, label=f"Roam (n={len(D_corrs_roam)})")
ax.errorbar([0,1], [np.mean(D_corrs_dwell), np.mean(D_corrs_roam)],
            [np.std(D_corrs_dwell)/len(D_corrs_dwell)**0.5,
             np.std(D_corrs_roam)/len(D_corrs_roam)**0.5],
            fmt='o-', color='k', zorder=5, linewidth=2, markersize=9)
ax.axhline(0, color='gray', linewidth=0.5)
ax.set_xticks([0,1]); ax.set_xticklabels(["Dwell","Roam"])
ax.set_ylabel("Pearson r (ADEL vs mean URY_URX)")
ax.set_title("Module Correlation by State")
ax.legend(fontsize=8)
sig = "***" if p_corr < 0.001 else "**" if p_corr < 0.01 else "*" if p_corr < 0.05 else "ns"
ax.text(0.5, 0.95, sig, transform=ax.transAxes, ha='center', va='top', fontsize=14)

ax = axes[1]
if paired_corrs:
    pd_arr = np.array(paired_corrs)
    ax.scatter(pd_arr[:,0], pd_arr[:,1], color='k', alpha=0.5, s=30)
    ax.axhline(0, color='gray', linewidth=0.5); ax.axvline(0, color='gray', linewidth=0.5)
    lim = max(abs(pd_arr).max() + 0.05, 0.3)
    ax.plot([-lim,lim],[-lim,lim], color='gray', linewidth=0.5, linestyle='--')
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    n_above = (pd_arr[:,1] > pd_arr[:,0]).sum()
    ax.text(0.05, 0.95, f"Roam>Dwell: {n_above}/{len(paired_corrs)}",
            transform=ax.transAxes, va='top', fontsize=9)
ax.set_xlabel("Dwell correlation"); ax.set_ylabel("Roam correlation")
ax.set_title("Paired: Dwell vs Roam r (ADEL × URY_URX)")
ax.set_aspect('equal')

fig.suptitle("FigA4: Module Coordination — ADEL vs URY_URX\n"
             "(each point = one recording)", fontsize=11)
plt.tight_layout()
fig.savefig(OUT4A / "FigA4_module_coordination.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved FigA4")

# =============================================================================
# ANALYSIS E — Exemplary Trace Figures
# =============================================================================
print("\n" + "="*70); print("Analysis E — Exemplary Traces")

# Selection rule: all 6 neurons present (already ensured);
# select 4 recordings with most transitions AND reasonable roam/dwell balance
# (|n_roam/n_dwell - 1| closest to 0), plus at least 1 transition
scored = [(abs(r["n_roam"]/(r["n_dwell"]+1)-1),
           r["rec_id"]) for r in recordings
          if r["n_roam"]>=100 and r["n_dwell"]>=100]
scored.sort()
exemplary_recs = [rec_id for _, rec_id in scored[:4]]
print(f"Selected recordings: {exemplary_recs}")

PLOT_NEURONS = ["ADEL", "URYVR", "URYDL"]

fig = plt.figure(figsize=(16, 11))
outer = gridspec.GridSpec(4, 1, hspace=0.45)
for row_idx, rec_id in enumerate(exemplary_recs):
    rec = next(r for r in recordings if r["rec_id"] == rec_id)
    inner = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=outer[row_idx], hspace=0.05)
    lbl = rec["lbl"]; T = rec["T"]
    t = np.arange(T) / SAMPLING_HZ

    for col_idx, n in enumerate(PLOT_NEURONS):
        ax = plt.subplot(inner[col_idx])
        x = rec["X"].get(n, np.full(T, np.nan))

        # Shade state background
        in_roam = False; start = 0
        for i in range(T):
            s = lbl[i]
            if s == 1 and not in_roam:
                in_roam = True; start = i
            elif s != 1 and in_roam:
                ax.axvspan(t[start], t[i], alpha=0.2, color=STATE_COLORS[1], linewidth=0)
                in_roam = False
        if in_roam:
            ax.axvspan(t[start], t[-1], alpha=0.2, color=STATE_COLORS[1], linewidth=0)

        ax.plot(t, x, color=COLORS[n], linewidth=0.8, alpha=0.9)
        ax.set_ylabel(n, fontsize=8, color=COLORS[n], fontweight="bold")
        ax.set_yticks([]); ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if col_idx < 2:
            ax.set_xticks([])
        else:
            ax.set_xlabel("Time (s)", fontsize=8)
            ax.tick_params(labelsize=7)
        if col_idx == 0:
            ax.set_title(rec_id, fontsize=9, fontweight="bold", loc='left')

# Add legend patch
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor=STATE_COLORS[1], alpha=0.4, label="Roaming")],
           loc='upper right', fontsize=9)
fig.suptitle("FigA5: Example ADEL–URY Activity Traces\n"
             "(shaded = roaming; selection: most balanced roam/dwell ratio with all neurons present)",
             fontsize=11)
fig.savefig(OUT4A / "FigA5_example_traces.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved FigA5")
print(f"Exemplary recordings (selection rule: balanced roam/dwell, all 6 neurons): {exemplary_recs}")

# =============================================================================
# Save JSON summary
# =============================================================================
summary = {
    "date": "2026-06-04",
    "authorization": "Phase 4A",
    "n_recordings": N_REC,
    "target_neurons": TARGET,
    "exemplary_recordings": exemplary_recs,
    "A_activity_profiles": A_summary,
    "A_tests": A_tests,
    "B_xcorr_peaks": {k: {"peak_corr": v["peak_corr"], "peak_lag_s": v["peak_lag_s"],
                           "n_epochs": v["n_epochs"]}
                      for k, v in B_summary.items()},
    "C_n_transitions": {"D2R": n_trans_D2R, "R2D": n_trans_R2D},
    "D_module_coordination": D_summary,
}

def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v=float(obj); return None if (v!=v or abs(v)==float("inf")) else v
    if isinstance(obj, float): return None if (obj!=obj or abs(obj)==float("inf")) else obj
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.bool_,)):   return bool(obj)
    if isinstance(obj, np.ndarray):    return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict):          return {k: sanitize(v) for k,v in obj.items()}
    if isinstance(obj, (list,tuple)):  return [sanitize(v) for v in obj]
    return obj

import json as json_mod
with open(OUT4A / "phase4a_results.json","w") as f:
    json_mod.dump(sanitize(summary), f, indent=2)
print("\nSaved: phase4a_results.json")
print("All Phase 4A computations complete.")
