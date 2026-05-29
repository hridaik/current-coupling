"""Stage 05 — Retained-frame feasibility audit.

Applies the full provisional segmentation pipeline:
  1. EWMA smoothing: tau = EWMA_TIMESCALE_SECONDS (20 s)
  2. Threshold: velocity_s > BEHAV_THRESHOLD (0.284)
  3. Transition exclusion: W_TRANS_SECONDS (30 s) on each side of every transition

Computes DESCRIPTIVE STATISTICS ONLY:
  - retained-frame fractions per state per animal
  - retained-epoch counts and duration distributions
  - transition-window loss
  - usable-frame counts for the 61-neuron subgraph

Does NOT:
  - compute covariance, precision, DeltaQ, enrichment
  - run stationarity / variability analysis
  - fit estimators
  - set MIN_BOUT_SECONDS (still None)
  - finalize behavioral states
  - access neural activity arrays
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR   = ROOT / "results" / "figures"
REPORT_PATH  = ROOT / "results" / "diagnostics" / "stage05_retained_frame_audit.md"
RETAINED_PLOT = FIGURE_DIR / "stage05_retained_frames.pdf"
EPOCH_PLOT    = FIGURE_DIR / "stage05_epoch_durations.pdf"
SUMMARY_PLOT  = FIGURE_DIR / "stage05_retained_summary.pdf"

SAMPLING_HZ = 5.0
V_STD = 0.06030961137253011

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_config():
    config_path = ROOT / "phase0_config.py"
    spec = importlib.util.spec_from_file_location("phase0_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def ewma(vs: np.ndarray, tau_sec: float) -> np.ndarray:
    if tau_sec <= 0:
        return vs.copy()
    alpha = 1.0 / (tau_sec * SAMPLING_HZ)
    alpha = min(alpha, 1.0)
    out = np.empty_like(vs)
    out[0] = vs[0]
    for t in range(1, len(vs)):
        out[t] = alpha * vs[t] + (1.0 - alpha) * out[t - 1]
    return out


def apply_transition_exclusion(
    labels: np.ndarray, w_frames: int
) -> np.ndarray:
    """Return a mask of retained frames (True = retained).

    Excludes w_frames on each side of every state transition.
    This means each bout contributes: max(0, bout_len - 2*w_frames) retained frames.
    """
    n = len(labels)
    retained = np.ones(n, dtype=bool)
    # find transitions
    diffs = np.where(np.diff(labels.astype(int)) != 0)[0]  # index of last frame before transition
    for t in diffs:
        lo = max(0, t - w_frames + 1)
        hi = min(n, t + w_frames + 1)
        retained[lo:hi] = False
    return retained


def get_epochs(labels: np.ndarray, retained: np.ndarray,
               state: int) -> np.ndarray:
    """Epoch lengths (in seconds) for consecutive retained frames in `state`."""
    active = (labels == state) & retained
    # find consecutive runs
    diffs = np.diff(active.astype(int), prepend=0, append=0)
    starts = np.where(diffs == 1)[0]
    ends   = np.where(diffs == -1)[0]
    lengths_sec = (ends - starts) / SAMPLING_HZ
    return lengths_sec[lengths_sec > 0]


def process_recording(
    path: Path, tau_sec: float, threshold: float, w_frames: int
) -> dict:
    rec_id = path.stem.replace("-data", "")
    with h5py.File(path, "r") as f:
        v = f["behavior"]["velocity"][:]
        ts = f["timing"]["timestamp_confocal"][:]
        has_np = "neuropal_registration" in f

    n_t = len(v)
    vs = v / V_STD
    smoothed = ewma(vs, tau_sec)
    labels = (smoothed > threshold).astype(np.int8)
    retained = apply_transition_exclusion(labels, w_frames)

    n_roam_retained  = int(np.sum((labels == 1) & retained))
    n_nr_retained    = int(np.sum((labels == 0) & retained))
    n_total_retained = n_roam_retained + n_nr_retained
    n_trans_lost     = int(np.sum(~retained))

    roam_epochs  = get_epochs(labels, retained, 1)
    nr_epochs    = get_epochs(labels, retained, 0)

    duration_min = float(ts[-1] - ts[0]) / 60.0 if len(ts) > 1 else float("nan")

    return {
        "rec_id":          rec_id,
        "has_neuropal":    has_np,
        "n_t":             n_t,
        "duration_min":    duration_min,
        "n_roam_retained": n_roam_retained,
        "n_nr_retained":   n_nr_retained,
        "n_total_retained":n_total_retained,
        "n_trans_lost":    n_trans_lost,
        "frac_roam_retained":  n_roam_retained  / n_t,
        "frac_nr_retained":    n_nr_retained    / n_t,
        "frac_total_retained": n_total_retained / n_t,
        "frac_lost":           n_trans_lost     / n_t,
        "roam_epochs_s":   roam_epochs,
        "nr_epochs_s":     nr_epochs,
        "n_roam_epochs":   len(roam_epochs),
        "n_nr_epochs":     len(nr_epochs),
        "roam_epoch_median_s": float(np.median(roam_epochs)) if len(roam_epochs) else float("nan"),
        "nr_epoch_median_s":   float(np.median(nr_epochs))   if len(nr_epochs)   else float("nan"),
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_retained_summary(recordings: list[dict], config) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    np_recs = [r for r in recordings if r["has_neuropal"]]

    frac_roam  = [r["frac_roam_retained"]  for r in np_recs]
    frac_nr    = [r["frac_nr_retained"]    for r in np_recs]
    frac_total = [r["frac_total_retained"] for r in np_recs]
    frac_lost  = [r["frac_lost"]           for r in np_recs]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    ax = axes[0]
    x = np.arange(len(np_recs))
    ax.bar(x, frac_roam,  label="roaming retained",     color="steelblue", alpha=0.8)
    ax.bar(x, frac_nr,    label="non-roaming retained",
           bottom=frac_roam, color="coral", alpha=0.8)
    ax.bar(x, frac_lost,  label="transition windows",
           bottom=[r + n for r, n in zip(frac_roam, frac_nr)],
           color="lightgray", alpha=0.8)
    ax.set_xlabel("recording (NeuroPAL)")
    ax.set_ylabel("fraction of total frames")
    ax.set_title(f"Frame allocation (tau={config.EWMA_TIMESCALE_SECONDS}s, "
                 f"W_TRANS={config.W_TRANS_SECONDS}s)")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_ylim(0, 1.05)

    ax2 = axes[1]
    ax2.hist(frac_total, bins=15, color="steelblue", edgecolor="white")
    ax2.axvline(np.median(frac_total), color="k", ls="--", lw=1.5,
                label=f"median={np.median(frac_total):.3f}")
    ax2.set_xlabel("total retained fraction")
    ax2.set_ylabel("n recordings")
    ax2.set_title("Total retained-frame fraction")
    ax2.legend(fontsize=8)

    ax3 = axes[2]
    n_roam_ep = [r["n_roam_epochs"] for r in np_recs]
    n_nr_ep   = [r["n_nr_epochs"]   for r in np_recs]
    ax3.bar(x, n_roam_ep, label="roaming epochs",     color="steelblue", alpha=0.8)
    ax3.bar(x, n_nr_ep,   label="non-roaming epochs",
            bottom=n_roam_ep, color="coral", alpha=0.8)
    ax3.set_xlabel("recording (NeuroPAL)")
    ax3.set_ylabel("n sustained epochs")
    ax3.set_title("Retained epochs per recording")
    ax3.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(RETAINED_PLOT), dpi=150)
    plt.close(fig)


def plot_epoch_durations(recordings: list[dict], config) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    np_recs = [r for r in recordings if r["has_neuropal"]]
    all_roam = np.concatenate([r["roam_epochs_s"] for r in np_recs if len(r["roam_epochs_s"])])
    all_nr   = np.concatenate([r["nr_epochs_s"]   for r in np_recs if len(r["nr_epochs_s"])])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, data, label, color in [
        (axes[0], all_roam, "roaming", "steelblue"),
        (axes[1], all_nr,   "non-roaming", "coral"),
    ]:
        if len(data) == 0:
            continue
        cap = min(float(np.percentile(data, 97)), 300)
        bins = np.linspace(0, cap, 50)
        ax.hist(data, bins=bins, color=color, edgecolor="none", alpha=0.8)
        ax.axvline(np.median(data), color="k", ls="--", lw=1.5,
                   label=f"median={np.median(data):.1f}s")
        for ref_s, ref_label in [(30, "30s"), (60, "60s"), (120, "2min")]:
            ax.axvline(ref_s, color="gray", lw=0.8, ls=":", alpha=0.7,
                       label=ref_label if ref_s == 30 else "_")
        ax.set_xlabel(f"{label} epoch duration (s)")
        ax.set_ylabel("n epochs")
        ax.set_title(f"{label.capitalize()} sustained epoch durations\n"
                     f"(tau={config.EWMA_TIMESCALE_SECONDS}s, W_TRANS={config.W_TRANS_SECONDS}s)")
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(EPOCH_PLOT), dpi=150)
    plt.close(fig)


def plot_per_animal_summary(recordings: list[dict], config) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    np_recs = [r for r in recordings if r["has_neuropal"]]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    roam_med = [r["roam_epoch_median_s"] for r in np_recs]
    nr_med   = [r["nr_epoch_median_s"]   for r in np_recs]

    ax = axes[0]
    ax.scatter(roam_med, nr_med, color="steelblue", alpha=0.7, s=30)
    ax.axvline(30, color="red", ls=":", lw=1, alpha=0.7, label="30s")
    ax.axhline(30, color="red", ls=":", lw=1, alpha=0.7)
    ax.set_xlabel("roaming epoch median (s)")
    ax.set_ylabel("non-roaming epoch median (s)")
    ax.set_title("Per-animal epoch medians\n(blue dot = one recording)")
    ax.legend(fontsize=8)

    ax2 = axes[1]
    n_roam = [r["n_roam_epochs"] for r in np_recs]
    n_nr   = [r["n_nr_epochs"]   for r in np_recs]
    ax2.scatter(n_roam, n_nr, color="steelblue", alpha=0.7, s=30)
    ax2.set_xlabel("n roaming epochs per recording")
    ax2.set_ylabel("n non-roaming epochs per recording")
    ax2.set_title("Per-animal sustained epoch counts")

    fig.tight_layout()
    fig.savefig(str(SUMMARY_PLOT), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(recordings: list[dict], config) -> None:
    today = _dt.date.today().isoformat()
    tau = config.EWMA_TIMESCALE_SECONDS
    threshold = config.BEHAV_THRESHOLD
    w_trans = config.W_TRANS_SECONDS
    w_frames = int(w_trans * SAMPLING_HZ)

    np_recs = [r for r in recordings if r["has_neuropal"]]
    n_np = len(np_recs)

    # Pooled arrays
    all_roam = np.concatenate([r["roam_epochs_s"] for r in np_recs if len(r["roam_epochs_s"])])
    all_nr   = np.concatenate([r["nr_epochs_s"]   for r in np_recs if len(r["nr_epochs_s"])])

    frac_total = np.array([r["frac_total_retained"] for r in np_recs])
    frac_roam  = np.array([r["frac_roam_retained"]  for r in np_recs])
    frac_nr    = np.array([r["frac_nr_retained"]    for r in np_recs])
    frac_lost  = np.array([r["frac_lost"]           for r in np_recs])

    n_roam_ep = np.array([r["n_roam_epochs"] for r in np_recs])
    n_nr_ep   = np.array([r["n_nr_epochs"]   for r in np_recs])

    def surv(arr, s):
        return float(np.mean(arr >= s)) if len(arr) else float("nan")

    # Total retained frames across all NeuroPAL recordings
    total_retained_roam = sum(r["n_roam_retained"] for r in np_recs)
    total_retained_nr   = sum(r["n_nr_retained"]   for r in np_recs)
    total_frames        = sum(r["n_t"] for r in np_recs)

    # Usable seconds per animal (median)
    retained_sec_roam = np.array([r["n_roam_retained"] / SAMPLING_HZ for r in np_recs])
    retained_sec_nr   = np.array([r["n_nr_retained"]   / SAMPLING_HZ for r in np_recs])

    report = f"""# Stage 5 Retained-Frame Feasibility Audit

Date: {today}
Pipeline:
  EWMA tau = {tau} s (provisional, approved 2026-05-28)
  BEHAV_THRESHOLD = {threshold} (LOCKED)
  W_TRANS_SECONDS = {w_trans} s (= {w_frames} frames at {SAMPLING_HZ:.0f} Hz)
Recordings: {n_np} NeuroPAL

## Scope

Applied the full provisional segmentation pipeline and counted retained frames
after transition-exclusion windows. No covariance/precision/DeltaQ computed.
MIN_BOUT_SECONDS NOT set.

Retained frame definition:
  - Belongs to a sustained state (velocity_s_ewma20 > {threshold} or ≤ {threshold})
  - NOT within {w_frames} frames of any state transition (W_TRANS exclusion)

---

## 1. Frame Allocation Summary (NeuroPAL recordings, n={n_np})

| Metric | Roaming | Non-roaming | Transition-lost | Total retained |
|---|---|---|---|---|
| Mean fraction of recording | {np.mean(frac_roam):.3f} | {np.mean(frac_nr):.3f} | {np.mean(frac_lost):.3f} | {np.mean(frac_total):.3f} |
| Median fraction | {np.median(frac_roam):.3f} | {np.median(frac_nr):.3f} | {np.median(frac_lost):.3f} | {np.median(frac_total):.3f} |
| IQR | [{np.percentile(frac_roam,25):.3f}, {np.percentile(frac_roam,75):.3f}] | [{np.percentile(frac_nr,25):.3f}, {np.percentile(frac_nr,75):.3f}] | [{np.percentile(frac_lost,25):.3f}, {np.percentile(frac_lost,75):.3f}] | [{np.percentile(frac_total,25):.3f}, {np.percentile(frac_total,75):.3f}] |

Pooled across all {n_np} NeuroPAL recordings:
  - Total frames:           {total_frames:,}
  - Retained roaming:       {total_retained_roam:,} ({100*total_retained_roam/total_frames:.1f}%)
  - Retained non-roaming:   {total_retained_nr:,}   ({100*total_retained_nr/total_frames:.1f}%)
  - Total retained:         {total_retained_roam+total_retained_nr:,} ({100*(total_retained_roam+total_retained_nr)/total_frames:.1f}%)

---

## 2. Per-Animal Retained Frame Counts

| Metric | Roaming retained (s) | Non-roaming retained (s) |
|---|---|---|
| Median | {np.median(retained_sec_roam):.0f} s | {np.median(retained_sec_nr):.0f} s |
| Mean | {np.mean(retained_sec_roam):.0f} s | {np.mean(retained_sec_nr):.0f} s |
| Min | {np.min(retained_sec_roam):.0f} s | {np.min(retained_sec_nr):.0f} s |
| Max | {np.max(retained_sec_roam):.0f} s | {np.max(retained_sec_nr):.0f} s |
| IQR | [{np.percentile(retained_sec_roam,25):.0f}, {np.percentile(retained_sec_roam,75):.0f}] s | [{np.percentile(retained_sec_nr,25):.0f}, {np.percentile(retained_sec_nr,75):.0f}] s |

At {SAMPLING_HZ:.0f} Hz, each retained second = {int(SAMPLING_HZ)} frames.
Per-animal retained frames (median):
  Roaming:     {np.median(retained_sec_roam):.0f} s × {SAMPLING_HZ:.0f} = {np.median(retained_sec_roam)*SAMPLING_HZ:.0f} frames
  Non-roaming: {np.median(retained_sec_nr):.0f} s × {SAMPLING_HZ:.0f} = {np.median(retained_sec_nr)*SAMPLING_HZ:.0f} frames

---

## 3. Sustained-Epoch Distributions

Epochs = consecutive retained-frame runs in the same state (after W_TRANS exclusion).

### Roaming epochs ({len(all_roam):,} total across {n_np} recordings)

| Metric | Value |
|---|---|
| Median duration | {np.median(all_roam):.1f} s |
| Mean duration | {np.mean(all_roam):.1f} s |
| p75 | {np.percentile(all_roam,75):.1f} s |
| p90 | {np.percentile(all_roam,90):.1f} s |
| p95 | {np.percentile(all_roam,95):.1f} s |
| Max | {np.max(all_roam):.1f} s |
| Fraction >= 10 s | {surv(all_roam,10):.3f} |
| Fraction >= 20 s | {surv(all_roam,20):.3f} |
| Fraction >= 30 s | {surv(all_roam,30):.3f} |
| Fraction >= 60 s | {surv(all_roam,60):.3f} |
| Median n_epochs per recording | {np.median(n_roam_ep):.0f} |
| Min n_epochs per recording | {np.min(n_roam_ep)} |
| Max n_epochs per recording | {np.max(n_roam_ep)} |

### Non-roaming epochs ({len(all_nr):,} total across {n_np} recordings)

| Metric | Value |
|---|---|
| Median duration | {np.median(all_nr):.1f} s |
| Mean duration | {np.mean(all_nr):.1f} s |
| p75 | {np.percentile(all_nr,75):.1f} s |
| p90 | {np.percentile(all_nr,90):.1f} s |
| p95 | {np.percentile(all_nr,95):.1f} s |
| Max | {np.max(all_nr):.1f} s |
| Fraction >= 10 s | {surv(all_nr,10):.3f} |
| Fraction >= 20 s | {surv(all_nr,20):.3f} |
| Fraction >= 30 s | {surv(all_nr,30):.3f} |
| Fraction >= 60 s | {surv(all_nr,60):.3f} |
| Median n_epochs per recording | {np.median(n_nr_ep):.0f} |
| Min n_epochs per recording | {np.min(n_nr_ep)} |
| Max n_epochs per recording | {np.max(n_nr_ep)} |

---

## 4. W_TRANS Feasibility Assessment

W_TRANS_SECONDS = {w_trans} s = {w_frames} frames.
A bout must exceed 2 × {w_trans:.0f} = {2*w_trans:.0f} s to contribute ANY retained frames.

Number of recordings with ZERO roaming epochs:    {sum(1 for r in np_recs if r['n_roam_epochs'] == 0)} / {n_np}
Number of recordings with ZERO non-roaming epochs:{sum(1 for r in np_recs if r['n_nr_epochs'] == 0)} / {n_np}

Min n_roam_epochs per animal:     {np.min(n_roam_ep)}
Min n_nr_epochs per animal:       {np.min(n_nr_ep)}

**Assessment**: {'W_TRANS = 30 s is feasible — all recordings retain usable epochs in both states.' if np.min(n_roam_ep) > 0 and np.min(n_nr_ep) > 0 else f'WARNING: some recordings have 0 epochs in one state after W_TRANS exclusion.'}

---

## 5. Adequacy for Covariance Estimation (Stage 6 context)

For Stage 6 n_eff computation from cross-products, each epoch contributes
independent samples. The key question is whether retained-frame counts are
adequate for stable covariance estimates.

Rule of thumb (task.md Stage 6): n_eff / N_COMMON_NEURONS ≥ 1 per epoch
is the minimum, with ≥ 5 being adequate for animal-level estimation.

At {SAMPLING_HZ:.0f} Hz and with N_COMMON_NEURONS = 61:
  - 1 effective sample per neuron pair requires n_eff ≥ N*(N-1)/2 = {61*60//2} samples
    (but n_eff << n_t due to autocorrelation, so this is not a simple frame count)
  - For a rough bound: 61 neurons × 5 independent samples ≥ 305 effective samples
  - At GCaMP6s timescales (τ_int ≈ 5–20 s), each effective sample ≈ {int(10*SAMPLING_HZ)}-{int(20*SAMPLING_HZ)} frames

Median retained roaming seconds per animal: {np.median(retained_sec_roam):.0f} s
Median retained non-roaming seconds per animal: {np.median(retained_sec_nr):.0f} s

These will be evaluated in Stage 6 against the actual τ_int values.
The retained-frame counts cannot be pre-assessed for n_eff adequacy
without computing the autocorrelation time (Stage 6 task).

---

## 6. Candidate MIN_BOUT_SECONDS Ranges (Descriptive Only)

Applying a MIN_BOUT_SECONDS filter would keep only epochs ≥ the minimum duration.
The effect on epoch counts is described below (for reference only — no value selected).

For roaming epochs:

| MIN_BOUT_SECONDS | Epochs surviving | % | Median remaining (s) |
|---|---|---|---|
| No filter | {len(all_roam)} | 100.0% | {np.median(all_roam):.1f} |
| 10 s | {int(np.sum(all_roam >= 10))} | {100*surv(all_roam,10):.1f}% | {f"{np.median(all_roam[all_roam >= 10]):.1f}" if np.sum(all_roam >= 10) > 0 else 'N/A'} |
| 20 s | {int(np.sum(all_roam >= 20))} | {100*surv(all_roam,20):.1f}% | {f"{np.median(all_roam[all_roam >= 20]):.1f}" if np.sum(all_roam >= 20) > 0 else 'N/A'} |
| 30 s | {int(np.sum(all_roam >= 30))} | {100*surv(all_roam,30):.1f}% | {f"{np.median(all_roam[all_roam >= 30]):.1f}" if np.sum(all_roam >= 30) > 0 else 'N/A'} |
| 60 s | {int(np.sum(all_roam >= 60))} | {100*surv(all_roam,60):.1f}% | {f"{np.median(all_roam[all_roam >= 60]):.1f}" if np.sum(all_roam >= 60) > 0 else 'N/A'} |

For non-roaming epochs:

| MIN_BOUT_SECONDS | Epochs surviving | % | Median remaining (s) |
|---|---|---|---|
| No filter | {len(all_nr)} | 100.0% | {np.median(all_nr):.1f} |
| 10 s | {int(np.sum(all_nr >= 10))} | {100*surv(all_nr,10):.1f}% | {f"{np.median(all_nr[all_nr >= 10]):.1f}" if np.sum(all_nr >= 10) > 0 else 'N/A'} |
| 20 s | {int(np.sum(all_nr >= 20))} | {100*surv(all_nr,20):.1f}% | {f"{np.median(all_nr[all_nr >= 20]):.1f}" if np.sum(all_nr >= 20) > 0 else 'N/A'} |
| 30 s | {int(np.sum(all_nr >= 30))} | {100*surv(all_nr,30):.1f}% | {f"{np.median(all_nr[all_nr >= 30]):.1f}" if np.sum(all_nr >= 30) > 0 else 'N/A'} |
| 60 s | {int(np.sum(all_nr >= 60))} | {100*surv(all_nr,60):.1f}% | {f"{np.median(all_nr[all_nr >= 60]):.1f}" if np.sum(all_nr >= 60) > 0 else 'N/A'} |

MIN_BOUT_SECONDS is NOT set here. Human decision required after reviewing
Stage 6 n_eff outputs and the retained-epoch counts above.

---

## 7. Config Fields Updated This Step

| Field | Value | Status |
|---|---|---|
| EWMA_TIMESCALE_SECONDS | 20.0 | **Added** (provisional, approved 2026-05-28) |
| BEHAV_THRESHOLD | 0.284 | Locked — unchanged |
| MIN_BOUT_SECONDS | None | NOT SET |

---

## 8. Figures

- `{rel(RETAINED_PLOT)}` — per-recording frame allocation, retained fraction, epoch counts
- `{rel(EPOCH_PLOT)}` — epoch duration distributions (roaming and non-roaming)
- `{rel(SUMMARY_PLOT)}` — per-animal epoch median scatter and epoch count scatter

---

## 9. Deviations

No deviations. Threshold and EWMA parameters applied as approved.
MIN_BOUT_SECONDS not set. phase0_config.py updated with EWMA_TIMESCALE_SECONDS = 20.0.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

NEUROPAL_IDS = {
    "2022-06-14-01","2022-06-14-07","2022-06-14-13","2022-06-28-01",
    "2022-06-28-07","2022-07-15-06","2022-07-15-12","2022-07-20-01",
    "2022-07-26-01","2022-08-02-01","2022-12-21-06","2023-01-05-01",
    "2023-01-05-18","2023-01-06-01","2023-01-06-08","2023-01-06-15",
    "2023-01-09-08","2023-01-09-15","2023-01-09-22","2023-01-09-28",
    "2023-01-10-07","2023-01-10-14","2023-01-13-07","2023-01-16-01",
    "2023-01-16-08","2023-01-16-15","2023-01-16-22","2023-01-17-01",
    "2023-01-17-07","2023-01-17-14","2023-01-18-01","2023-01-19-01",
    "2023-01-19-08","2023-01-19-15","2023-01-19-22","2023-01-23-01",
    "2023-01-23-08","2023-01-23-15","2023-01-23-21","2023-03-07-01",
}


def main() -> None:
    config = load_config()
    tau = config.EWMA_TIMESCALE_SECONDS
    threshold = config.BEHAV_THRESHOLD
    w_trans = config.W_TRANS_SECONDS
    w_frames = int(w_trans * SAMPLING_HZ)

    print(f"Pipeline: EWMA tau={tau}s  threshold={threshold}  W_TRANS={w_trans}s ({w_frames} frames)")

    atanas_root = ROOT / config.ATANAS_PATH
    h5_files = sorted(atanas_root.glob("*-data.h5"))

    print(f"Processing {len(h5_files)} recordings (NeuroPAL only)...")
    recordings: list[dict] = []
    for p in h5_files:
        if p.stem.replace("-data", "") not in NEUROPAL_IDS:
            continue
        try:
            rec = process_recording(p, tau, threshold, w_frames)
            recordings.append(rec)
        except Exception as e:
            print(f"  WARN: {p.name}: {e}")

    np_recs = [r for r in recordings if r["has_neuropal"]]
    print(f"  Processed {len(np_recs)} NeuroPAL recordings")

    print("Generating plots...")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_retained_summary(recordings, config)
    plot_epoch_durations(recordings, config)
    plot_per_animal_summary(recordings, config)

    write_report(recordings, config)
    print(f"Report written: {rel(REPORT_PATH)}")

    # Key numbers
    frac_total = np.array([r["frac_total_retained"] for r in np_recs])
    n_roam_ep  = np.array([r["n_roam_epochs"]       for r in np_recs])
    n_nr_ep    = np.array([r["n_nr_epochs"]          for r in np_recs])
    all_roam   = np.concatenate([r["roam_epochs_s"] for r in np_recs if len(r["roam_epochs_s"])])
    all_nr     = np.concatenate([r["nr_epochs_s"]   for r in np_recs if len(r["nr_epochs_s"])])
    ret_roam_s = np.array([r["n_roam_retained"] / SAMPLING_HZ for r in np_recs])
    ret_nr_s   = np.array([r["n_nr_retained"]   / SAMPLING_HZ for r in np_recs])

    print()
    print(f"=== Retained-frame summary (tau={tau}s, W_TRANS={w_trans}s) ===")
    print(f"  Total retained fraction:     median={np.median(frac_total):.3f}  "
          f"IQR=[{np.percentile(frac_total,25):.3f}, {np.percentile(frac_total,75):.3f}]")
    print(f"  Retained roaming (median):   {np.median(ret_roam_s):.0f} s/recording")
    print(f"  Retained non-roaming (med):  {np.median(ret_nr_s):.0f} s/recording")
    print(f"  n_roam_epochs (median):      {np.median(n_roam_ep):.0f}")
    print(f"  n_nr_epochs (median):        {np.median(n_nr_ep):.0f}")
    print(f"  Roaming epoch median:        {np.median(all_roam):.1f} s  p90={np.percentile(all_roam,90):.1f} s")
    print(f"  Non-roaming epoch median:    {np.median(all_nr):.1f} s  p90={np.percentile(all_nr,90):.1f} s")
    print(f"  Zero-epoch recordings (roam): {sum(1 for r in np_recs if r['n_roam_epochs']==0)}")
    print(f"  Zero-epoch recordings (nr):   {sum(1 for r in np_recs if r['n_nr_epochs']==0)}")
    print()
    print("MIN_BOUT_SECONDS: NOT set")
    print("BEHAV_THRESHOLD:  0.284 (LOCKED)")
    print(f"EWMA tau:         {tau} s (provisional, written to config)")


if __name__ == "__main__":
    main()
