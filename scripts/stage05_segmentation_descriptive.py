"""Stage 05 — Provisional segmentation descriptive audit.

Applies BEHAV_THRESHOLD = 0.284 (velocity_s) to generate provisional binary
roam/non-roam labels for each recording, then computes:
  - per-animal roaming occupancy fractions
  - bout-length distributions for both states (no MIN_BOUT_SECONDS filter)
  - transition frequencies and rates
  - state duration statistics
  - per-animal occupancy variability

Does NOT:
  - compute covariance, precision, DeltaQ, enrichment
  - run stationarity or variability analysis
  - fit estimators
  - apply a MIN_BOUT_SECONDS filter (not yet set)
  - change any neural analysis
  - tune the threshold
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
REPORT_PATH  = ROOT / "results" / "diagnostics" / "stage05_segmentation_descriptive.md"
FIGURE_DIR   = ROOT / "results" / "figures"
OCC_PLOT     = FIGURE_DIR / "stage05_occupancy_per_animal.pdf"
BOUT_PLOT    = FIGURE_DIR / "stage05_bout_lengths.pdf"
TRANS_PLOT   = FIGURE_DIR / "stage05_transitions.pdf"

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
# Segmentation helpers (no MIN_BOUT_SECONDS filter)
# ---------------------------------------------------------------------------

def apply_threshold(vs: np.ndarray, threshold: float) -> np.ndarray:
    """Binary roam label: 1 = roaming (vs > threshold), 0 = non-roaming."""
    return (vs > threshold).astype(np.int8)


def get_bouts(labels: np.ndarray) -> dict[str, np.ndarray]:
    """Extract bout lengths (in frames) for each state without any filter."""
    diffs = np.diff(labels.astype(int))
    starts_r = np.where(diffs == 1)[0] + 1   # non-roam → roam
    ends_r   = np.where(diffs == -1)[0] + 1  # roam → non-roam

    if labels[0] == 1:
        starts_r = np.concatenate([[0], starts_r])
    if labels[-1] == 1:
        ends_r = np.concatenate([ends_r, [len(labels)]])

    min_len = min(len(starts_r), len(ends_r))
    roam_bouts = ends_r[:min_len] - starts_r[:min_len]

    starts_nr = np.where(diffs == -1)[0] + 1
    ends_nr   = np.where(diffs == 1)[0] + 1
    if labels[0] == 0:
        starts_nr = np.concatenate([[0], starts_nr])
    if labels[-1] == 0:
        ends_nr = np.concatenate([ends_nr, [len(labels)]])
    min_len_nr = min(len(starts_nr), len(ends_nr))
    non_roam_bouts = ends_nr[:min_len_nr] - starts_nr[:min_len_nr]

    return {"roam": roam_bouts, "non_roam": non_roam_bouts}


def transitions_per_minute(labels: np.ndarray, duration_min: float) -> float:
    """Number of state transitions per minute."""
    n_transitions = int(np.sum(np.abs(np.diff(labels.astype(int)))))
    return n_transitions / duration_min if duration_min > 0 else float("nan")


# ---------------------------------------------------------------------------
# Per-recording loader
# ---------------------------------------------------------------------------

def process_recording(path: Path, threshold: float) -> dict:
    rec_id = path.stem.replace("-data", "")
    with h5py.File(path, "r") as f:
        v = f["behavior"]["velocity"][:]
        ts = f["timing"]["timestamp_confocal"][:]
        has_neuropal = "neuropal_registration" in f

    vs = v / V_STD
    labels = apply_threshold(vs, threshold)
    duration_min = float(ts[-1] - ts[0]) / 60.0 if len(ts) > 1 else float("nan")

    bouts = get_bouts(labels)
    roam_occ = float(np.mean(labels))
    trans_pm = transitions_per_minute(labels, duration_min)

    return {
        "rec_id": rec_id,
        "has_neuropal": has_neuropal,
        "n_t": len(labels),
        "duration_min": duration_min,
        "roam_occupancy": roam_occ,
        "non_roam_occupancy": 1.0 - roam_occ,
        "n_transitions": int(np.sum(np.abs(np.diff(labels.astype(int))))),
        "transitions_per_min": trans_pm,
        "roam_bouts_frames": bouts["roam"],
        "non_roam_bouts_frames": bouts["non_roam"],
        "roam_bouts_sec": bouts["roam"] / SAMPLING_HZ,
        "non_roam_bouts_sec": bouts["non_roam"] / SAMPLING_HZ,
        "n_roam_bouts": len(bouts["roam"]),
        "n_non_roam_bouts": len(bouts["non_roam"]),
    }


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------

def pct_str(arr: np.ndarray) -> str:
    return (f"mean={np.mean(arr):.3f}  median={np.median(arr):.3f}  "
            f"std={np.std(arr):.3f}  p5={np.percentile(arr,5):.3f}  "
            f"p95={np.percentile(arr,95):.3f}")


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_occupancy(recordings: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    occ = np.array([r["roam_occupancy"] for r in recordings])
    has_np = np.array([r["has_neuropal"] for r in recordings])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    ax = axes[0]
    ax.hist(occ[has_np], bins=20, color="steelblue", alpha=0.7,
            edgecolor="white", label="NeuroPAL")
    ax.hist(occ[~has_np], bins=20, color="lightgray", alpha=0.7,
            edgecolor="white", label="No NeuroPAL")
    ax.axvline(np.median(occ[has_np]), color="steelblue", ls="--", lw=1.5,
               label=f"NeuroPAL median={np.median(occ[has_np]):.3f}")
    ax.set_xlabel("roaming occupancy (fraction of recording)")
    ax.set_ylabel("n recordings")
    ax.set_title("Per-animal roaming occupancy")
    ax.legend(fontsize=8)

    ax2 = axes[1]
    trans_pm = np.array([r["transitions_per_min"] for r in recordings])
    ax2.hist(trans_pm[has_np], bins=20, color="coral", alpha=0.7,
             edgecolor="white", label="NeuroPAL")
    ax2.axvline(np.median(trans_pm[has_np]), color="coral", ls="--", lw=1.5,
                label=f"median={np.median(trans_pm[has_np]):.2f}/min")
    ax2.set_xlabel("transitions per minute")
    ax2.set_ylabel("n recordings")
    ax2.set_title("State transition rate per recording")
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(OCC_PLOT), dpi=150)
    plt.close(fig)


def plot_bout_lengths(recordings: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    np_recs = [r for r in recordings if r["has_neuropal"]]
    all_roam_s = np.concatenate([r["roam_bouts_sec"] for r in np_recs]) if np_recs else np.array([])
    all_nr_s   = np.concatenate([r["non_roam_bouts_sec"] for r in np_recs]) if np_recs else np.array([])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    for ax, data, label, color in [
        (axes[0], all_roam_s, "roaming", "steelblue"),
        (axes[1], all_nr_s,   "non-roaming", "coral"),
    ]:
        if len(data) == 0:
            continue
        bins = np.linspace(0, min(np.percentile(data, 98), 200), 50)
        ax.hist(data, bins=bins, color=color, edgecolor="white", alpha=0.8)
        ax.axvline(np.median(data), color="k", ls="--", lw=1.5,
                   label=f"median={np.median(data):.1f} s")
        ax.axvline(30.0, color="red", ls=":", lw=1.2, alpha=0.7,
                   label="W_TRANS=30 s")
        ax.set_xlabel(f"{label} bout length (s)")
        ax.set_ylabel("n bouts")
        ax.set_title(f"{label.capitalize()} bout lengths\n"
                     f"(NeuroPAL, no MIN_BOUT_SECONDS filter)")
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(BOUT_PLOT), dpi=150)
    plt.close(fig)


def plot_transitions(recordings: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    np_recs = [r for r in recordings if r["has_neuropal"]]
    n_roam_bouts = np.array([r["n_roam_bouts"] for r in np_recs])
    n_nr_bouts   = np.array([r["n_non_roam_bouts"] for r in np_recs])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].hist(n_roam_bouts, bins=20, color="steelblue", edgecolor="white")
    axes[0].axvline(np.median(n_roam_bouts), color="k", ls="--", lw=1.5,
                    label=f"median={np.median(n_roam_bouts):.0f}")
    axes[0].set_xlabel("n roaming bouts per recording")
    axes[0].set_title("Roaming bout count (NeuroPAL)")
    axes[0].legend(fontsize=8)

    axes[1].hist(n_nr_bouts, bins=20, color="coral", edgecolor="white")
    axes[1].axvline(np.median(n_nr_bouts), color="k", ls="--", lw=1.5,
                    label=f"median={np.median(n_nr_bouts):.0f}")
    axes[1].set_xlabel("n non-roaming bouts per recording")
    axes[1].set_title("Non-roaming bout count (NeuroPAL)")
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(TRANS_PLOT), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(
    recordings: list[dict],
    config,
) -> None:
    today = _dt.date.today().isoformat()
    threshold = config.BEHAV_THRESHOLD
    w_trans = config.W_TRANS_SECONDS
    n_total = len(recordings)
    np_recs = [r for r in recordings if r["has_neuropal"]]
    n_np = len(np_recs)

    occ_np   = np.array([r["roam_occupancy"] for r in np_recs])
    occ_all  = np.array([r["roam_occupancy"] for r in recordings])
    trans_np = np.array([r["transitions_per_min"] for r in np_recs])

    all_roam_s = np.concatenate([r["roam_bouts_sec"] for r in np_recs])
    all_nr_s   = np.concatenate([r["non_roam_bouts_sec"] for r in np_recs])

    # Fraction of bouts that would survive a MIN_BOUT_SECONDS filter
    def survival(bouts_s: np.ndarray, min_s: float) -> float:
        return float(np.mean(bouts_s >= min_s)) if len(bouts_s) else float("nan")

    report = f"""# Stage 5 Segmentation Descriptive Audit

Date: {today}
Threshold applied: BEHAV_THRESHOLD = {threshold} (velocity_s)
Rule: BEHAV_THRESHOLD_RULE = "{config.BEHAV_THRESHOLD_RULE}"
Recordings: {n_total} total ({n_np} NeuroPAL)

## Scope

Provisional binary roam/non-roam labels applied for descriptive purposes.
roaming  = velocity_s > {threshold}
non-roaming = velocity_s ≤ {threshold}

W_TRANS_SECONDS = {w_trans} s ({int(w_trans * SAMPLING_HZ)} frames) — NOT yet applied.
MIN_BOUT_SECONDS = None — NOT yet set; bout statistics are unfiltered.

NOT computed:
  - Covariance, precision, DeltaQ, enrichment
  - Stationarity / variability analysis
  - Neural-informed threshold adjustment

---

## 1. Roaming Occupancy

| Metric | All recordings (n={n_total}) | NeuroPAL only (n={n_np}) |
|---|---|---|
| Mean roaming occupancy | {np.mean(occ_all):.3f} | {np.mean(occ_np):.3f} |
| Median roaming occupancy | {np.median(occ_all):.3f} | {np.median(occ_np):.3f} |
| Std | {np.std(occ_all):.3f} | {np.std(occ_np):.3f} |
| IQR | [{np.percentile(occ_all,25):.3f}, {np.percentile(occ_all,75):.3f}] | [{np.percentile(occ_np,25):.3f}, {np.percentile(occ_np,75):.3f}] |
| Range | [{np.min(occ_all):.3f}, {np.max(occ_all):.3f}] | [{np.min(occ_np):.3f}, {np.max(occ_np):.3f}] |

Non-roaming occupancy = 1 − roaming occupancy.
Median non-roaming (NeuroPAL): {1 - np.median(occ_np):.3f}

The between-animal std of {np.std(occ_np):.3f} is {'moderate' if np.std(occ_np) > 0.1 else 'low'} relative to the
mean occupancy of {np.mean(occ_np):.3f}. Animals vary in their roaming/dwelling balance.

---

## 2. Bout-Length Distributions (NeuroPAL, no MIN_BOUT_SECONDS filter)

All bouts counted, including very short ones that would typically be excluded.

### Roaming bouts (n={len(all_roam_s):,} total across {n_np} recordings)

| Metric | Value |
|---|---|
| Median | {np.median(all_roam_s):.1f} s |
| Mean | {np.mean(all_roam_s):.1f} s |
| Std | {np.std(all_roam_s):.1f} s |
| p25 | {np.percentile(all_roam_s, 25):.1f} s |
| p75 | {np.percentile(all_roam_s, 75):.1f} s |
| p90 | {np.percentile(all_roam_s, 90):.1f} s |
| p95 | {np.percentile(all_roam_s, 95):.1f} s |
| Min | {np.min(all_roam_s):.1f} s |
| Max | {np.max(all_roam_s):.1f} s |
| Fraction ≥ 10 s | {survival(all_roam_s, 10):.3f} |
| Fraction ≥ 20 s | {survival(all_roam_s, 20):.3f} |
| Fraction ≥ 30 s (W_TRANS) | {survival(all_roam_s, 30):.3f} |
| Fraction ≥ 60 s | {survival(all_roam_s, 60):.3f} |

### Non-roaming bouts (n={len(all_nr_s):,} total across {n_np} recordings)

| Metric | Value |
|---|---|
| Median | {np.median(all_nr_s):.1f} s |
| Mean | {np.mean(all_nr_s):.1f} s |
| Std | {np.std(all_nr_s):.1f} s |
| p25 | {np.percentile(all_nr_s, 25):.1f} s |
| p75 | {np.percentile(all_nr_s, 75):.1f} s |
| p90 | {np.percentile(all_nr_s, 90):.1f} s |
| p95 | {np.percentile(all_nr_s, 95):.1f} s |
| Min | {np.min(all_nr_s):.1f} s |
| Max | {np.max(all_nr_s):.1f} s |
| Fraction ≥ 10 s | {survival(all_nr_s, 10):.3f} |
| Fraction ≥ 20 s | {survival(all_nr_s, 20):.3f} |
| Fraction ≥ 30 s (W_TRANS) | {survival(all_nr_s, 30):.3f} |
| Fraction ≥ 60 s | {survival(all_nr_s, 60):.3f} |

---

## 3. Transition Rates (NeuroPAL recordings)

| Metric | Value |
|---|---|
| Mean transitions/min | {np.mean(trans_np):.2f} |
| Median transitions/min | {np.median(trans_np):.2f} |
| Std transitions/min | {np.std(trans_np):.2f} |
| IQR | [{np.percentile(trans_np,25):.2f}, {np.percentile(trans_np,75):.2f}] |
| Mean n_roam_bouts per recording | {np.mean([r["n_roam_bouts"] for r in np_recs]):.1f} |
| Median n_roam_bouts | {np.median([r["n_roam_bouts"] for r in np_recs]):.0f} |
| Mean n_non_roam_bouts | {np.mean([r["n_non_roam_bouts"] for r in np_recs]):.1f} |
| Median n_non_roam_bouts | {np.median([r["n_non_roam_bouts"] for r in np_recs]):.0f} |

At median {np.median(trans_np):.2f} transitions/min, an average recording of
{np.median([r["duration_min"] for r in np_recs]):.1f} min contains approximately
{np.median(trans_np) * np.median([r["duration_min"] for r in np_recs]):.0f} state transitions.
Each W_TRANS = 30 s exclusion window removes {int(w_trans * SAMPLING_HZ)} frames per transition;
at {np.median(trans_np) * np.median([r["duration_min"] for r in np_recs]):.0f} transitions this removes
~{np.median(trans_np) * np.median([r["duration_min"] for r in np_recs]) * w_trans / (np.median([r["duration_min"] for r in np_recs])*60) * 100:.1f}%
of total frames.

---

## 4. Segmentation Stability Across Animals

| Metric | NeuroPAL recordings |
|---|---|
| n recordings with roaming occupancy 0.2–0.8 (balanced) | {sum(1 for r in np_recs if 0.2 <= r["roam_occupancy"] <= 0.8)} / {n_np} |
| n recordings with occupancy < 0.1 (mostly non-roaming) | {sum(1 for r in np_recs if r["roam_occupancy"] < 0.1)} / {n_np} |
| n recordings with occupancy > 0.9 (mostly roaming) | {sum(1 for r in np_recs if r["roam_occupancy"] > 0.9)} / {n_np} |
| IQR of occupancy | [{np.percentile(occ_np,25):.3f}, {np.percentile(occ_np,75):.3f}] |

{'The segmentation appears stable: most recordings have mixed roaming/non-roaming occupancy.' if sum(1 for r in np_recs if 0.2 <= r["roam_occupancy"] <= 0.8) / n_np > 0.6 else 'Some recordings are dominated by one state; human should check extreme cases.'}

---

## 5. Candidate MIN_BOUT_SECONDS Ranges (Descriptive)

These are presented for human review only. MIN_BOUT_SECONDS is NOT set here.

### For roaming bouts:

| Candidate filter | Fraction surviving | n bouts surviving |
|---|---|---|
| ≥ 10 s | {survival(all_roam_s, 10):.3f} | {int(np.sum(all_roam_s >= 10)):,} |
| ≥ 20 s | {survival(all_roam_s, 20):.3f} | {int(np.sum(all_roam_s >= 20)):,} |
| ≥ 30 s | {survival(all_roam_s, 30):.3f} | {int(np.sum(all_roam_s >= 30)):,} |
| ≥ 60 s | {survival(all_roam_s, 60):.3f} | {int(np.sum(all_roam_s >= 60)):,} |

### For non-roaming bouts:

| Candidate filter | Fraction surviving | n bouts surviving |
|---|---|---|
| ≥ 10 s | {survival(all_nr_s, 10):.3f} | {int(np.sum(all_nr_s >= 10)):,} |
| ≥ 20 s | {survival(all_nr_s, 20):.3f} | {int(np.sum(all_nr_s >= 20)):,} |
| ≥ 30 s | {survival(all_nr_s, 30):.3f} | {int(np.sum(all_nr_s >= 30)):,} |
| ≥ 60 s | {survival(all_nr_s, 60):.3f} | {int(np.sum(all_nr_s >= 60)):,} |

**Key consideration**: W_TRANS_SECONDS = 30 s means each bout must have a
sustained portion of at least {w_trans} s AFTER transition exclusion.
A bout of 30 s with a W_TRANS window on each end has 0 net usable frames;
bouts must be significantly longer than W_TRANS to contribute data.

The median roaming bout is {np.median(all_roam_s):.1f} s. Only {survival(all_roam_s, 30):.1%} of roaming bouts
exceed 30 s. Only {survival(all_roam_s, 60):.1%} exceed 60 s (2 × W_TRANS).

A MIN_BOUT_SECONDS of 30–60 s would retain {survival(all_roam_s, 30):.1%}–{survival(all_roam_s, 60):.1%} of roaming
bouts for the roaming state, and {survival(all_nr_s, 30):.1%}–{survival(all_nr_s, 60):.1%} of non-roaming bouts.
The choice of MIN_BOUT_SECONDS should balance usable frame count against
bout-duration bias.

---

## 6. Figures

- `{rel(OCC_PLOT)}` — per-animal occupancy and transition rate
- `{rel(BOUT_PLOT)}` — bout length distributions
- `{rel(TRANS_PLOT)}` — bout count per recording

---

## 7. Config Fields Updated This Step

| Field | Value |
|---|---|
| BEHAVIOR_SCORE_SOURCE | "velocity_s" |
| BEHAV_THRESHOLD | 0.284 |
| BEHAV_THRESHOLD_RULE | "pooled_velocity_s_kde_trough_between_dwelling_and_roaming" |
| MIN_BOUT_SECONDS | None (NOT YET SET) |

---

## 8. Deviations

No deviations. phase0_config.py BEHAV_THRESHOLD set from behavioral KDE
only (pooled trough at 0.284 velocity_s). No neural output used.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()

    # Verify threshold is set
    assert config.BEHAV_THRESHOLD is not None, "BEHAV_THRESHOLD not set in config"
    threshold = config.BEHAV_THRESHOLD
    print(f"BEHAV_THRESHOLD = {threshold} (velocity_s)")

    atanas_root = ROOT / config.ATANAS_PATH
    h5_files = sorted(atanas_root.glob("*-data.h5"))
    if not h5_files:
        raise RuntimeError(f"No processed H5 files found under {atanas_root}")

    print(f"Processing {len(h5_files)} recordings...")
    recordings: list[dict] = []
    for p in h5_files:
        try:
            rec = process_recording(p, threshold)
            recordings.append(rec)
        except Exception as e:
            print(f"  WARN: {p.name}: {e}")
    print(f"  Processed {len(recordings)} recordings successfully")

    np_recs = [r for r in recordings if r["has_neuropal"]]
    print(f"  NeuroPAL recordings: {len(np_recs)}")

    print("Generating plots...")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_occupancy(recordings)
    plot_bout_lengths(recordings)
    plot_transitions(recordings)

    write_report(recordings, config)
    print(f"Report written: {rel(REPORT_PATH)}")

    # Key numbers printout
    occ_np = np.array([r["roam_occupancy"] for r in np_recs])
    all_roam_s = np.concatenate([r["roam_bouts_sec"] for r in np_recs])
    all_nr_s   = np.concatenate([r["non_roam_bouts_sec"] for r in np_recs])

    print()
    print(f"=== Segmentation summary (NeuroPAL, threshold={threshold}) ===")
    print(f"  Roaming occupancy:    median={np.median(occ_np):.3f}  "
          f"IQR=[{np.percentile(occ_np,25):.3f}, {np.percentile(occ_np,75):.3f}]")
    print(f"  Roaming bout median:  {np.median(all_roam_s):.1f} s  "
          f"p75={np.percentile(all_roam_s,75):.1f} s  p95={np.percentile(all_roam_s,95):.1f} s")
    print(f"  Non-roam bout median: {np.median(all_nr_s):.1f} s  "
          f"p75={np.percentile(all_nr_s,75):.1f} s  p95={np.percentile(all_nr_s,95):.1f} s")
    print(f"  Roaming bouts >= 30s: {np.mean(all_roam_s >= 30):.3f}  "
          f">= 60s: {np.mean(all_roam_s >= 60):.3f}")
    print(f"  Non-roam bouts >= 30s:{np.mean(all_nr_s >= 30):.3f}  "
          f">= 60s: {np.mean(all_nr_s >= 60):.3f}")
    print()
    print("MIN_BOUT_SECONDS: NOT set (pending human review of bout distributions)")


if __name__ == "__main__":
    main()
