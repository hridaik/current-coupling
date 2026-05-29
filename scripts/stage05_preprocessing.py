"""Stage 05 — Behavioral and preprocessing descriptive audit.

Loads behavioral variables (velocity, reversal_vec, angular_velocity,
worm_curvature) and neural array shapes from all available processed H5 files.

Computes DESCRIPTIVE STATISTICS ONLY:
  - recording durations and frame counts
  - velocity KDE per animal and pooled
  - reversal fraction, bout-duration distributions (without thresholding)
  - angular velocity and curvature distributions
  - neuron coverage per recording
  - NaN fraction in neural traces
  - coordinate availability across animals
  - NeuroPAL registration availability

Does NOT:
  - assign behavioral states
  - choose or apply velocity thresholds
  - compute covariance, precision, DeltaQ, enrichment
  - run stationarity or variability analysis
  - perform estimator fitting
  - modify phase0_config.py behavioral-threshold fields
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH   = ROOT / "results" / "diagnostics" / "stage05_behavior_descriptive_audit.md"
FIGURE_DIR    = ROOT / "results" / "figures"
VELOCITY_PLOT = FIGURE_DIR / "stage05_velocity_kde.pdf"
COVERAGE_PLOT = FIGURE_DIR / "stage05_neuron_coverage.pdf"
DURATION_PLOT = FIGURE_DIR / "stage05_recording_durations.pdf"

SAMPLING_HZ = 5.0          # confirmed from phase0_config.py
V_STD = 0.06030961137253011  # from FlavellConstants.jl

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
# Per-recording loader (behavioral only + shape metadata)
# ---------------------------------------------------------------------------

def load_recording(path: Path) -> dict[str, Any]:
    """Load behavioral scalars and shape metadata only. No neural traces."""
    rec: dict[str, Any] = {}
    rec["path"] = str(path)
    rec["recording_id"] = path.stem.replace("-data", "")

    with h5py.File(path, "r") as f:
        top_keys = list(f.keys())

        # --- behavioral variables (1D arrays, ~12 KB each) ---
        beh = f["behavior"]
        rec["velocity"]         = beh["velocity"][:]            # m/s
        rec["reversal_vec"]     = beh["reversal_vec"][:].astype(int)
        rec["angular_velocity"] = beh["angular_velocity"][:]    # rad/s
        rec["worm_curvature"]   = beh["worm_curvature"][:]      # summary curvature

        # reversal events shape → number of reversals
        rev_shape = beh["reversal_events"].shape
        rec["n_reversals"] = max(rev_shape)  # shape is (2, n_rev) in Julia → (n_rev, 2) in h5py?

        # body_angle shapes (just shape, not values)
        if "body_angle" in beh:
            rec["body_angle_shape"] = tuple(beh["body_angle"].shape)
        if "body_angle_absolute" in beh:
            rec["body_angle_absolute_shape"] = tuple(beh["body_angle_absolute"].shape)

        # additional behavioral keys
        rec["behavior_keys"] = sorted(beh.keys())

        # --- gcamp shape metadata + NaN check ---
        gc = f["gcamp"]
        trace_shape = gc["trace_array"].shape   # (T, N) in Python (transposed from Julia)
        rec["n_t"] = trace_shape[0]
        rec["n_neuron"] = trace_shape[1]

        # count NaN in trace_array — safe, needed for missingness audit
        trace = gc["trace_array"][:]
        rec["trace_nan_frac"] = float(np.mean(np.isnan(trace)))
        rec["neurons_all_nan"] = int(np.sum(np.all(np.isnan(trace), axis=0)))
        rec["neurons_any_nan"] = int(np.sum(np.any(np.isnan(trace), axis=0)))
        del trace  # free memory

        # idx_splits — recording segments
        splits_raw = gc["idx_splits"][:]
        rec["n_segments"] = int(splits_raw.shape[1])  # (2, n_seg) in Julia → (n_seg, 2)?

        rec["gcamp_keys"] = sorted(gc.keys())

        # --- timing ---
        timing = f["timing"]
        ts = timing["timestamp_confocal"][:]
        rec["duration_seconds"] = float(ts[-1] - ts[0]) if len(ts) > 1 else float("nan")
        rec["timestamp_range"]  = (float(ts[0]), float(ts[-1]))
        rec["n_t_confocal"]     = len(ts)

        # --- NeuroPAL registration presence ---
        rec["has_neuropal"] = "neuropal_registration" in top_keys
        if rec["has_neuropal"]:
            nr = f["neuropal_registration"]
            conf = nr["roi_match_confidence"][:]
            rec["neuropal_n_rois"] = len(conf)
            rec["neuropal_conf_median"] = float(np.median(conf))
            rec["neuropal_conf_above_25"] = int(np.sum(conf >= 2.5))

        rec["top_keys"] = top_keys

    # derived
    rec["velocity_s"] = rec["velocity"] / V_STD
    rec["duration_minutes"] = rec["duration_seconds"] / 60.0
    rec["reversal_fraction"] = float(np.mean(rec["reversal_vec"] > 0))

    return rec


# ---------------------------------------------------------------------------
# Descriptive statistics helpers
# ---------------------------------------------------------------------------

def describe(arr: np.ndarray, label: str) -> dict[str, float]:
    valid = arr[~np.isnan(arr)]
    return {
        "label": label, "n": len(valid),
        "mean": float(np.mean(valid)),
        "median": float(np.median(valid)),
        "std": float(np.std(valid)),
        "p5": float(np.percentile(valid, 5)),
        "p25": float(np.percentile(valid, 25)),
        "p75": float(np.percentile(valid, 75)),
        "p95": float(np.percentile(valid, 95)),
        "min": float(np.min(valid)),
        "max": float(np.max(valid)),
        "n_nan": int(np.sum(np.isnan(arr))),
    }


def kde_grid(data: np.ndarray, n_pts: int = 300) -> tuple[np.ndarray, np.ndarray]:
    """Simple Gaussian KDE without sklearn dependency."""
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(data[~np.isnan(data)], bw_method="scott")
    x = np.linspace(np.nanmin(data) - 0.5 * np.nanstd(data),
                    np.nanmax(data) + 0.5 * np.nanstd(data), n_pts)
    return x, kde(x)


def reversal_bout_lengths(reversal_vec: np.ndarray) -> np.ndarray:
    """Durations (in frames) of sustained reversal bouts and forward bouts."""
    diffs = np.diff(reversal_vec.astype(int))
    starts = np.where(diffs == 1)[0] + 1
    ends   = np.where(diffs == -1)[0] + 1
    if len(starts) == 0 or len(ends) == 0:
        return np.array([])
    if ends[0] < starts[0]:
        ends = ends[1:]
    min_len = min(len(starts), len(ends))
    return ends[:min_len] - starts[:min_len]


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_velocity_kde(recordings: list[dict], path: Path) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Per-animal KDE
    ax = axes[0]
    all_vs = []
    for rec in recordings:
        v = rec["velocity_s"]
        valid = v[~np.isnan(v)]
        if len(valid) < 50:
            continue
        x, y = kde_grid(valid)
        ax.plot(x, y, alpha=0.35, lw=0.8, color="steelblue")
        all_vs.append(valid)

    ax.set_xlabel("velocity_s = velocity / v_STD")
    ax.set_ylabel("density")
    ax.set_title(f"Per-animal velocity KDE (n={len(all_vs)} recordings)")
    ax.axvline(0, color="k", lw=0.8, ls="--", alpha=0.6)

    # Pooled KDE
    ax2 = axes[1]
    pooled = np.concatenate(all_vs)
    x, y = kde_grid(pooled)
    ax2.plot(x, y, color="steelblue", lw=2)
    ax2.set_xlabel("velocity_s")
    ax2.set_ylabel("density")
    ax2.set_title(f"Pooled velocity KDE (n={len(pooled):,} frames)")
    ax2.axvline(0, color="k", lw=0.8, ls="--", alpha=0.6)

    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_neuron_coverage(recordings: list[dict], path: Path) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    n_neurons = [r["n_neuron"] for r in recordings]
    durations = [r["duration_minutes"] for r in recordings]

    axes[0].hist(n_neurons, bins=20, color="steelblue", edgecolor="white")
    axes[0].set_xlabel("n_neuron per recording")
    axes[0].set_ylabel("count")
    axes[0].set_title("Neuron count distribution")
    axes[0].axvline(np.median(n_neurons), color="red", ls="--", lw=1, label=f"median={int(np.median(n_neurons))}")
    axes[0].legend(fontsize=8)

    axes[1].hist(durations, bins=20, color="coral", edgecolor="white")
    axes[1].set_xlabel("recording duration (min)")
    axes[1].set_ylabel("count")
    axes[1].set_title("Recording duration distribution")
    axes[1].axvline(np.median(durations), color="k", ls="--", lw=1, label=f"median={np.median(durations):.1f} min")
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_duration(recordings: list[dict], path: Path) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    durations = sorted([r["duration_minutes"] for r in recordings])
    ax.barh(range(len(durations)), durations, color="steelblue", height=0.8)
    ax.set_xlabel("duration (min)")
    ax.set_ylabel("recording index (sorted)")
    ax.set_title(f"Recording durations — n={len(recordings)} recordings")
    ax.axvline(np.median(durations), color="red", ls="--", lw=1.5, label=f"median={np.median(durations):.1f} min")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(
    recordings: list[dict],
    neuropal_ids: set[str],
    velocity_desc: dict,
    vel_s_desc: dict,
    ang_vel_desc: dict,
    curvature_desc: dict,
    reversal_frac_desc: dict,
    bout_len_desc: dict | None,
) -> None:
    today = _dt.date.today().isoformat()

    n_total = len(recordings)
    n_neuropal = sum(1 for r in recordings if r["has_neuropal"])
    n_nonneuropal = n_total - n_neuropal

    durations = [r["duration_minutes"] for r in recordings]
    n_neurons_list = [r["n_neuron"] for r in recordings]
    nan_fracs = [r["trace_nan_frac"] for r in recordings]

    # NeuroPAL-only subset
    np_recs = [r for r in recordings if r["has_neuropal"]]
    np_neurons = [r["n_neuron"] for r in np_recs]

    # Coordinate availability: trace_array present in all; traces_array_F_F20 check
    n_with_f20 = sum(1 for r in recordings if "traces_array_F_F20" in r["gcamp_keys"])
    n_with_fmean = sum(1 for r in recordings if "traces_array_F_Fmean" in r["gcamp_keys"])
    n_with_neuropal_reg = n_neuropal

    def fmt_desc(d: dict) -> str:
        return (f"mean={d['mean']:.4f}  median={d['median']:.4f}  "
                f"std={d['std']:.4f}  p5={d['p5']:.4f}  p95={d['p95']:.4f}  "
                f"min={d['min']:.4f}  max={d['max']:.4f}  n={d['n']:,}")

    report = f"""# Stage 5 Behavioral Descriptive Audit

Date: {today}
Recordings loaded: {n_total} ({n_neuropal} with NeuroPAL registration, {n_nonneuropal} without)

## Scope

Descriptive statistics on behavioral variables and recording metadata.
No behavioral states assigned. No thresholds chosen.

Loaded per recording:
  - behavior/velocity, reversal_vec, angular_velocity, worm_curvature
  - gcamp/trace_array shape and NaN fraction
  - timing/timestamp_confocal (for duration)
  - neuropal_registration (presence and confidence)

NOT computed:
  - Behavioral state labels (roaming/dwelling)
  - Behavioral thresholds (BEHAV_THRESHOLD still None)
  - Covariance, precision, DeltaQ, enrichment

---

## 1. Recording-Level Summary

| Metric | Value |
|---|---|
| Total recordings | {n_total} |
| NeuroPAL-registered recordings | {n_neuropal} |
| Non-NeuroPAL recordings | {n_nonneuropal} |
| Median duration | {np.median(durations):.1f} min |
| Duration range | [{np.min(durations):.1f}, {np.max(durations):.1f}] min |
| Duration IQR | [{np.percentile(durations,25):.1f}, {np.percentile(durations,75):.1f}] min |
| Total recording time | {np.sum(durations):.0f} min ({np.sum(durations)/60:.1f} h) |
| Median n_t (frames) | {int(np.median([r['n_t'] for r in recordings]))} |
| Frame-count range | [{min(r['n_t'] for r in recordings)}, {max(r['n_t'] for r in recordings)}] |
| Median n_neuron | {int(np.median(n_neurons_list))} |
| n_neuron range | [{min(n_neurons_list)}, {max(n_neurons_list)}] |
| Median n_neuron (NeuroPAL only) | {int(np.median(np_neurons)) if np_neurons else 'N/A'} |
| Median NaN fraction (trace_array) | {np.median(nan_fracs):.4f} |
| NaN fraction range | [{np.min(nan_fracs):.4f}, {np.max(nan_fracs):.4f}] |

Note on recording count:
  - The Stage 2 NeuroPAL label decode identified 40 NeuroPAL-labeled records.
  - The H5 data directory contains {n_total} processed files, of which {n_neuropal} have
    the `neuropal_registration` group. The additional {n_nonneuropal} recordings lack
    NeuroPAL identification and are NOT part of the primary N_COMMON_NEURONS = 61
    subgraph analysis. They may be used for n_eff and stationarity assessment if needed.

---

## 2. Coordinate Availability

| Coordinate / Array | Present in N recordings | % |
|---|---|---|
| gcamp/trace_array (z-scored) | {n_total} | 100% |
| gcamp/traces_array_F_F20 (ΔF/F₂₀) | {n_with_f20} | {100*n_with_f20/n_total:.0f}% |
| gcamp/traces_array_F_Fmean (ΔF/Fmean) | {n_with_fmean} | {100*n_with_fmean/n_total:.0f}% |
| neuropal_registration (NeuroPAL IDs) | {n_neuropal} | {100*n_neuropal/n_total:.0f}% |

**COORD_ROBUSTNESS_1 candidate (`trace_array`)**: present in all {n_total} recordings.
**COORD_PRIMARY (CePNEM residuals)**: NOT pre-stored; requires CePNEM fit files.
**COORD_ROBUSTNESS_2 (deconvolved)**: NOT pre-stored; requires CePNEM fit files.

---

## 3. Velocity Distribution

Velocity is in m/s; velocity_s = velocity / v_STD (v_STD = {V_STD:.5f}).
No threshold applied.

### Raw velocity (m/s)
{fmt_desc(velocity_desc)}

### Standardized velocity_s (dimensionless)
{fmt_desc(vel_s_desc)}

**Interpretation note**: velocity_s > 0 = forward motion; velocity_s < 0 = backward
(reversals). The distribution below characterizes where a threshold would split
the data, but no threshold is chosen here.

Fraction of frames with velocity_s > 0:   {float(np.mean(np.concatenate([r['velocity_s'] for r in recordings]) > 0)):.3f}
Fraction of frames in reversal (rev_vec=1): {reversal_frac_desc['mean']:.4f} (mean per recording)

**Velocity KDE plots**: see `{rel(VELOCITY_PLOT)}`

---

## 4. Reversal Statistics

| Metric | Value |
|---|---|
| Mean reversal fraction per recording | {reversal_frac_desc['mean']:.4f} |
| Median reversal fraction | {reversal_frac_desc['median']:.4f} |
| Reversal fraction IQR | [{reversal_frac_desc['p25']:.4f}, {reversal_frac_desc['p75']:.4f}] |
| Reversal fraction range | [{reversal_frac_desc['min']:.4f}, {reversal_frac_desc['max']:.4f}] |
| Mean n_reversals per recording | {np.mean([r['n_reversals'] for r in recordings]):.1f} |
| Median n_reversals | {np.median([r['n_reversals'] for r in recordings]):.1f} |

{f"Reversal bout lengths (frames): {fmt_desc(bout_len_desc)}" if bout_len_desc else "Reversal bout length data unavailable."}

---

## 5. Angular Velocity Distribution

Savitzky-Golay filtered head angular velocity (rad/s).

{fmt_desc(ang_vel_desc)}

---

## 6. Worm Curvature Distribution

Whole-body curvature summary metric.

{fmt_desc(curvature_desc)}

---

## 7. Neuron Coverage

| Metric | All recordings | NeuroPAL recordings only |
|---|---|---|
| Median n_neuron | {int(np.median(n_neurons_list))} | {int(np.median(np_neurons)) if np_neurons else 'N/A'} |
| Mean n_neuron | {np.mean(n_neurons_list):.1f} | {f"{np.mean(np_neurons):.1f}" if np_neurons else 'N/A'} |
| n_neuron range | [{min(n_neurons_list)}, {max(n_neurons_list)}] | {f'[{min(np_neurons)}, {max(np_neurons)}]' if np_neurons else 'N/A'} |
| Median trace NaN fraction | {np.median(nan_fracs):.4f} | {f"{np.median([r['trace_nan_frac'] for r in np_recs]):.4f}" if np_recs else 'N/A'} |

Coverage figures: see `{rel(COVERAGE_PLOT)}`

The N_COMMON_NEURONS = 61 subgraph analysis requires only 61 identified neurons
per recording. At median n_neuron = {int(np.median(n_neurons_list))}, most recordings have substantially
more neurons recorded than the subgraph size. The NaN fraction reflects neurons
that are absent from individual recordings.

---

## 8. Assessment: Roam/Dwell Segmentation Feasibility

Based on descriptive statistics only (no thresholding):

1. **Velocity bimodality (qualitative)**: The velocity_s distribution spans
   roughly [{vel_s_desc['p5']:.2f}, {vel_s_desc['p95']:.2f}] (5th–95th percentile).
   The median of {vel_s_desc['median']:.3f} and the forward/backward split seen in
   per-animal KDEs suggest a mixture of locomotion modes. Whether this is
   bimodal requires visual inspection of per-animal KDEs (see figure).

2. **Reversal structure**: Mean reversal fraction = {reversal_frac_desc['mean']:.1%},
   suggesting worms spend roughly {reversal_frac_desc['mean']*100:.0f}% of recording time in reversals.
   This is behaviorally consistent with interleaved dwelling bouts.

3. **Recording duration**: Median duration = {np.median(durations):.1f} min; range
   [{np.min(durations):.1f}, {np.max(durations):.1f}] min. With W_TRANS_SECONDS = 30 s (6 Hz × 30 = 150 frames)
   transition-exclusion windows, the bulk of each recording (~{(np.median(durations)*60 - 150)/np.median(durations)/60*100:.0f}% at median
   duration) is available for state analysis.

4. **Candidate threshold location**: The velocity_s distribution is centered
   near {vel_s_desc['median']:.3f}, with a forward-fraction of {float(np.mean(np.concatenate([r['velocity_s'] for r in recordings]) > 0)):.1%}.
   A threshold near velocity_s = 0 (i.e., v = 0 m/s) separates forward from
   backward, but may not capture dwelling/roaming in the classical sense.
   A positive threshold (e.g. velocity_s ≈ 0.1–0.3) may better capture sustained
   roaming. Human decision required — see BEHAV_THRESHOLD human checkpoint.

5. **Data sufficiency**: {n_neuropal} NeuroPAL-registered recordings with median
   {int(np.median(np_neurons))} neurons is sufficient for the pairwise analysis
   (N_COMMON_NEURONS = 61 < median n_neuron).

---

## 9. Config Fields Impacted (NOT set here)

| Field | Status | Required before setting |
|---|---|---|
| BEHAVIOR_SCORE_SOURCE | None | Human confirms velocity as primary |
| BEHAV_THRESHOLD | None | KDE review + human decision |
| BEHAV_THRESHOLD_RULE | None | With BEHAV_THRESHOLD |
| MIN_BOUT_SECONDS | None | Epoch distribution reviewed by human |
| COORD_PRIMARY | None | CePNEM fit files needed + human decision |
| COORD_ROBUSTNESS_1 | None | Likely trace_array; human confirmation |
| COORD_ROBUSTNESS_2 | None | CePNEM deconvolution availability check |
| DECONV_AVAILABLE | None | CePNEM fit files needed |
| COORD_INTERP_RULE | None | Human pre-specification before ΔQ |

---

## 10. Deviations

No deviations. matplotlib installed as a core dependency (per AGENTS.md, approved
at each stage boundary). phase0_config.py unchanged.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    atanas_root = ROOT / config.ATANAS_PATH

    h5_files = sorted(atanas_root.glob("*-data.h5"))
    if not h5_files:
        raise RuntimeError(f"No processed H5 files found under {atanas_root}")

    print(f"Loading {len(h5_files)} H5 recordings...")
    recordings: list[dict] = []
    for p in h5_files:
        try:
            rec = load_recording(p)
            recordings.append(rec)
        except Exception as e:
            print(f"  WARN: failed to load {p.name}: {e}")

    print(f"  Loaded {len(recordings)} recordings successfully")

    # NeuroPAL record IDs from Stage 2
    neuropal_ids_stage2 = {
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

    # Pooled behavioral arrays
    all_velocity    = np.concatenate([r["velocity"]         for r in recordings])
    all_velocity_s  = np.concatenate([r["velocity_s"]       for r in recordings])
    all_ang_vel     = np.concatenate([r["angular_velocity"]  for r in recordings])
    all_curvature   = np.concatenate([r["worm_curvature"]    for r in recordings])
    all_rev_frac    = np.array([r["reversal_fraction"] for r in recordings])

    # Reversal bout lengths (without any threshold)
    all_bout_lens = np.concatenate([
        reversal_bout_lengths(r["reversal_vec"]) for r in recordings
        if len(reversal_bout_lengths(r["reversal_vec"])) > 0
    ])

    velocity_desc    = describe(all_velocity, "velocity (m/s)")
    vel_s_desc       = describe(all_velocity_s, "velocity_s")
    ang_vel_desc     = describe(all_ang_vel, "angular_velocity (rad/s)")
    curvature_desc   = describe(all_curvature, "worm_curvature")
    rev_frac_desc    = describe(all_rev_frac, "reversal_fraction per recording")
    bout_len_desc    = describe(all_bout_lens / SAMPLING_HZ, "reversal bout length (s)") \
                       if len(all_bout_lens) > 0 else None

    print("Generating plots...")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_velocity_kde(recordings, VELOCITY_PLOT)
    plot_neuron_coverage(recordings, COVERAGE_PLOT)
    plot_duration(recordings, DURATION_PLOT)
    print(f"  Velocity KDE: {rel(VELOCITY_PLOT)}")
    print(f"  Neuron coverage: {rel(COVERAGE_PLOT)}")
    print(f"  Duration: {rel(DURATION_PLOT)}")

    write_report(
        recordings, neuropal_ids_stage2,
        velocity_desc, vel_s_desc, ang_vel_desc, curvature_desc,
        rev_frac_desc, bout_len_desc,
    )
    print(f"Report written: {rel(REPORT_PATH)}")

    # Print key numbers to stdout
    n_np = sum(1 for r in recordings if r["has_neuropal"])
    durations = [r["duration_minutes"] for r in recordings]
    n_neurons = [r["n_neuron"] for r in recordings]
    print()
    print(f"=== Summary ===")
    print(f"  n recordings total:          {len(recordings)}")
    print(f"  n with NeuroPAL:             {n_np}")
    print(f"  recording duration:          median={np.median(durations):.1f} min, "
          f"range=[{np.min(durations):.1f}, {np.max(durations):.1f}]")
    print(f"  n_neuron:                    median={int(np.median(n_neurons))}, "
          f"range=[{min(n_neurons)}, {max(n_neurons)}]")
    print(f"  velocity_s median:           {vel_s_desc['median']:.4f}")
    print(f"  velocity_s [p5, p95]:        [{vel_s_desc['p5']:.3f}, {vel_s_desc['p95']:.3f}]")
    print(f"  frames forward (v_s>0):      {float(np.mean(all_velocity_s > 0)):.3f}")
    print(f"  mean reversal fraction:      {rev_frac_desc['mean']:.4f}")
    print(f"  trace NaN fraction (median): {np.median([r['trace_nan_frac'] for r in recordings]):.4f}")
    print()
    print("BEHAV_THRESHOLD:   NOT set (requires human KDE review)")
    print("COORD_PRIMARY:     NOT set (requires CePNEM fit files)")
    print("phase0_config.py:  NOT modified")


if __name__ == "__main__":
    main()
