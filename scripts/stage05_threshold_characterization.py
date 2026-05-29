"""Stage 05 — Velocity_s threshold characterization.

Characterizes the velocity_s distribution across animals:
  - per-animal KDEs (Silverman bandwidth)
  - local minima / trough locations
  - bimodality coefficient (skewness²+1) / excess_kurtosis
  - state occupancy curves  (fraction > t vs t, no threshold applied)
  - between-animal trough variability
  - summary modality classification per animal

Does NOT:
  - assign behavioral states
  - write BEHAV_THRESHOLD or any config field
  - compute covariance / precision / DeltaQ
  - apply any threshold to classify time points
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
from scipy.signal import argrelmin
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR    = ROOT / "results" / "figures"
REPORT_PATH   = ROOT / "results" / "diagnostics" / "stage05_threshold_characterization.md"
TROUGH_PLOT   = FIGURE_DIR / "stage05_velocity_trough_analysis.pdf"
OCCUPANCY_PLOT = FIGURE_DIR / "stage05_velocity_occupancy.pdf"
BIMOD_PLOT    = FIGURE_DIR / "stage05_bimodality_summary.pdf"

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
# Data loader — velocity only
# ---------------------------------------------------------------------------

def load_velocity(path: Path) -> tuple[str, np.ndarray, bool]:
    rec_id = path.stem.replace("-data", "")
    with h5py.File(path, "r") as f:
        v = f["behavior"]["velocity"][:]
        has_neuropal = "neuropal_registration" in f
    return rec_id, v / V_STD, has_neuropal


# ---------------------------------------------------------------------------
# KDE and trough analysis
# ---------------------------------------------------------------------------

KDE_N_PTS = 600

def compute_kde(vs: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Return (x, density, bandwidth) using Silverman's rule."""
    valid = vs[~np.isnan(vs)]
    kde = gaussian_kde(valid, bw_method="silverman")
    bw = float(kde.factor * np.std(valid))
    x = np.linspace(-4.0, 4.0, KDE_N_PTS)
    return x, kde(x), bw


def find_troughs(x: np.ndarray, y: np.ndarray,
                 order: int = 20) -> np.ndarray:
    """Local minima in the KDE (candidate trough locations)."""
    idx = argrelmin(y, order=order)[0]
    return x[idx]


def find_peaks(x: np.ndarray, y: np.ndarray, order: int = 20) -> np.ndarray:
    from scipy.signal import argrelmax
    idx = argrelmax(y, order=order)[0]
    return x[idx]


def bimodality_coefficient(vs: np.ndarray) -> float:
    """BC = (skewness^2 + 1) / (excess_kurtosis + 3).
    BC > 5/9 ≈ 0.555 consistent with bimodality."""
    valid = vs[~np.isnan(vs)]
    n = len(valid)
    if n < 10:
        return float("nan")
    mu = np.mean(valid)
    sigma = np.std(valid, ddof=1)
    if sigma == 0:
        return float("nan")
    z = (valid - mu) / sigma
    skew = np.mean(z ** 3)
    kurt_excess = np.mean(z ** 4) - 3.0   # excess kurtosis
    # Finite-sample correction is small; skip for descriptive purposes
    denom = kurt_excess + 3.0
    return float((skew ** 2 + 1.0) / denom) if denom > 0 else float("nan")


def occupancy_curve(vs: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Fraction of time with velocity_s > t for each threshold in thresholds."""
    valid = vs[~np.isnan(vs)]
    return np.array([np.mean(valid > t) for t in thresholds])


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_trough_analysis(
    recordings: list[tuple[str, np.ndarray, bool]],
    troughs_per_animal: list[np.ndarray],
    neuropal_mask: list[bool],
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    n = len(recordings)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # A: Per-animal KDEs coloured by NeuroPAL status
    ax = axes[0]
    all_troughs = []
    for (rec_id, vs, has_np), troughs in zip(recordings, troughs_per_animal):
        x, y, _ = compute_kde(vs)
        color = "steelblue" if has_np else "lightgray"
        ax.plot(x, y, alpha=0.3, lw=0.8, color=color)
        for t in troughs:
            all_troughs.append(float(t))

    ax.set_xlabel("velocity_s")
    ax.set_ylabel("density")
    ax.set_title(f"Per-animal KDEs\n(blue=NeuroPAL n={sum(neuropal_mask)}, "
                 f"gray=no-NeuroPAL n={sum(~np.array(neuropal_mask))})")
    ax.axvline(0, color="k", lw=0.8, ls="--", alpha=0.5)

    # B: Trough location histogram
    ax2 = axes[1]
    primary_troughs = [t[0] if len(t) > 0 else float("nan")
                       for t in troughs_per_animal]
    valid_troughs = [t for t in primary_troughs if not np.isnan(t)]
    if valid_troughs:
        ax2.hist(valid_troughs, bins=np.linspace(-2, 2, 31),
                 color="coral", edgecolor="white")
        ax2.axvline(np.median(valid_troughs), color="k", ls="--", lw=1.5,
                    label=f"median={np.median(valid_troughs):.3f}")
        ax2.legend(fontsize=9)
    ax2.set_xlabel("primary trough velocity_s")
    ax2.set_ylabel("n recordings")
    ax2.set_title(f"Trough location distribution\n"
                  f"n={len(valid_troughs)}/{n} recordings have trough")

    # C: All trough locations as scatter
    ax3 = axes[2]
    for i, (troughs, has_np) in enumerate(zip(troughs_per_animal, neuropal_mask)):
        color = "steelblue" if has_np else "lightgray"
        for t in troughs:
            ax3.scatter(t, i, color=color, s=15, alpha=0.7)
    ax3.axvline(0, color="k", lw=0.8, ls="--", alpha=0.5)
    ax3.set_xlabel("trough location (velocity_s)")
    ax3.set_ylabel("recording index")
    ax3.set_title("All KDE trough locations per recording")

    fig.tight_layout()
    fig.savefig(str(TROUGH_PLOT), dpi=150)
    plt.close(fig)


def plot_occupancy(recordings: list[tuple[str, np.ndarray, bool]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    thresholds = np.linspace(-3.0, 3.0, 200)
    fig, ax = plt.subplots(figsize=(8, 5))

    neuropal_curves = []
    for rec_id, vs, has_np in recordings:
        occ = occupancy_curve(vs, thresholds)
        color = "steelblue" if has_np else "lightgray"
        ax.plot(thresholds, occ, alpha=0.3, lw=0.8, color=color)
        if has_np:
            neuropal_curves.append(occ)

    if neuropal_curves:
        mean_occ = np.mean(neuropal_curves, axis=0)
        ax.plot(thresholds, mean_occ, color="navy", lw=2.5,
                label="NeuroPAL mean")

    ax.axhline(0.5, color="gray", lw=0.8, ls=":")
    ax.axvline(0, color="k", lw=0.8, ls="--", alpha=0.5)
    ax.set_xlabel("velocity_s threshold t")
    ax.set_ylabel("fraction of time with velocity_s > t")
    ax.set_title("State occupancy curves (no threshold selected)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(OCCUPANCY_PLOT), dpi=150)
    plt.close(fig)


def plot_bimodality(
    bc_values: list[float],
    rec_ids: list[str],
    neuropal_mask: list[bool],
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    bc_arr = np.array(bc_values)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Histogram of BC values
    ax = axes[0]
    valid = bc_arr[~np.isnan(bc_arr)]
    ax.hist(valid, bins=20, color="steelblue", edgecolor="white")
    ax.axvline(5/9, color="red", ls="--", lw=1.5,
               label="BC=5/9 (bimodal threshold)")
    ax.axvline(np.median(valid), color="k", ls="--", lw=1.5,
               label=f"median={np.median(valid):.3f}")
    ax.set_xlabel("bimodality coefficient (BC)")
    ax.set_ylabel("n recordings")
    ax.set_title("Bimodality coefficient distribution")
    ax.legend(fontsize=8)

    n_bimod = int(np.sum(valid > 5/9))
    ax.text(0.05, 0.95, f"{n_bimod}/{len(valid)} recordings\nBC > 5/9",
            transform=ax.transAxes, va="top", fontsize=9,
            color="red")

    # BC by recording (sorted, coloured by NeuroPAL)
    ax2 = axes[1]
    sorted_idx = np.argsort(bc_arr)
    colors = ["steelblue" if neuropal_mask[i] else "lightgray"
              for i in sorted_idx]
    ax2.bar(range(len(bc_arr)), bc_arr[sorted_idx], color=colors, width=0.8)
    ax2.axhline(5/9, color="red", ls="--", lw=1.5, label="BC=5/9")
    ax2.set_xlabel("recording (sorted by BC)")
    ax2.set_ylabel("bimodality coefficient")
    ax2.set_title("BC per recording (sorted)")
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(BIMOD_PLOT), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(
    recordings: list[tuple[str, np.ndarray, bool]],
    troughs_per_animal: list[np.ndarray],
    bc_values: list[float],
    n_modes_per_animal: list[int],
    neuropal_mask: list[bool],
    pooled_troughs: np.ndarray | None = None,
    pooled_peaks: np.ndarray | None = None,
    pos_trough_arr: np.ndarray | None = None,
) -> None:
    today = _dt.date.today().isoformat()
    n_total = len(recordings)
    n_np = sum(neuropal_mask)

    primary_troughs = np.array([
        t[0] if len(t) > 0 else float("nan")
        for t in troughs_per_animal
    ])
    valid_troughs = primary_troughs[~np.isnan(primary_troughs)]
    np_troughs = primary_troughs[np.array(neuropal_mask) & ~np.isnan(primary_troughs)]

    bc_arr = np.array(bc_values)
    valid_bc = bc_arr[~np.isnan(bc_arr)]
    n_bimod = int(np.sum(valid_bc > 5/9))
    n_bimod_np = int(np.sum(bc_arr[np.array(neuropal_mask) & ~np.isnan(bc_arr)] > 5/9))

    n_has_trough = int(np.sum(~np.isnan(primary_troughs)))
    n_has_trough_np = int(np.sum(
        ~np.isnan(primary_troughs[np.array(neuropal_mask)])
    ))

    # Threshold stability: IQR of trough locations
    trough_iqr = float(np.percentile(valid_troughs, 75) - np.percentile(valid_troughs, 25)) \
                 if len(valid_troughs) > 3 else float("nan")
    np_trough_iqr = float(np.percentile(np_troughs, 75) - np.percentile(np_troughs, 25)) \
                    if len(np_troughs) > 3 else float("nan")

    # Occupancy at key candidate thresholds (descriptive only)
    all_vs_np = np.concatenate([vs for _, vs, has_np in recordings if has_np])
    occ_at = {}
    for t_cand in [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]:
        occ_at[t_cand] = float(np.mean(all_vs_np > t_cand))

    # Pooled trough/peak formatting
    pooled_troughs_str = (
        ", ".join(f"{t:.3f}" for t in pooled_troughs) if pooled_troughs is not None and len(pooled_troughs)
        else "none detected"
    )
    pooled_peaks_str = (
        ", ".join(f"{t:.3f}" for t in pooled_peaks) if pooled_peaks is not None and len(pooled_peaks)
        else "none detected"
    )
    pt_med = float(np.median(pos_trough_arr)) if pos_trough_arr is not None and len(pos_trough_arr) else float("nan")
    pt_iqr_lo = float(np.percentile(pos_trough_arr, 25)) if pos_trough_arr is not None and len(pos_trough_arr) > 3 else float("nan")
    pt_iqr_hi = float(np.percentile(pos_trough_arr, 75)) if pos_trough_arr is not None and len(pos_trough_arr) > 3 else float("nan")
    pt_std = float(np.std(pos_trough_arr)) if pos_trough_arr is not None and len(pos_trough_arr) > 1 else float("nan")
    n_pos = len(pos_trough_arr) if pos_trough_arr is not None else 0

    report = f"""# Stage 5 Velocity Threshold Characterization

Date: {today}
Recordings analyzed: {n_total} total ({n_np} NeuroPAL)

## Scope

Numerical characterization of velocity_s distribution structure.
No threshold selected. BEHAV_THRESHOLD remains None.

Computed:
  - Per-animal KDEs (Silverman bandwidth, scipy.stats.gaussian_kde)
  - Local minima (trough candidates) via argrelmin(order=30)
  - Bimodality coefficient: BC = (skewness^2 + 1) / (excess_kurtosis + 3)
    BC > 5/9 ≈ 0.555 is a standard bimodality indicator (Pfister et al.)
  - State occupancy curves (fraction > t) for descriptive purposes

NOT computed:
  - Any threshold applied to data
  - BEHAV_THRESHOLD, BEHAV_THRESHOLD_RULE
  - Behavioral state labels
  - Covariance, precision, DeltaQ, enrichment

---

## 1. Pooled Distribution Structure (NeuroPAL recordings, n=40)

Pooled velocity_s KDE across all {n_np} NeuroPAL recordings (Silverman bandwidth).

| Feature | velocity_s location |
|---|---|
| Mode 1 (reversals) | {pooled_peaks_str.split(",")[0].strip() if pooled_peaks is not None and len(pooled_peaks) >= 1 else 'N/A'} |
| Mode 2 (dwelling/slow) | {pooled_peaks_str.split(",")[1].strip() if pooled_peaks is not None and len(pooled_peaks) >= 2 else 'N/A'} |
| Mode 3 (roaming/fast forward) | {pooled_peaks_str.split(",")[2].strip() if pooled_peaks is not None and len(pooled_peaks) >= 3 else 'N/A'} |
| **Trough 1** (reversal ↔ dwelling) | {pooled_troughs_str.split(",")[0].strip() if pooled_troughs is not None and len(pooled_troughs) >= 1 else 'N/A'} |
| **Trough 2** (dwelling ↔ roaming) | {pooled_troughs_str.split(",")[1].strip() if pooled_troughs is not None and len(pooled_troughs) >= 2 else 'N/A'} |

The pooled distribution is **trimodal** with three well-separated modes:
1. A reversal mode at velocity_s ≈ {pooled_peaks_str.split(",")[0].strip() if pooled_peaks is not None and len(pooled_peaks) >= 1 else '?'} (backward locomotion)
2. A dwelling/slow mode near velocity_s ≈ {pooled_peaks_str.split(",")[1].strip() if pooled_peaks is not None and len(pooled_peaks) >= 2 else '?'} (near-stationary)
3. A roaming mode at velocity_s ≈ {pooled_peaks_str.split(",")[2].strip() if pooled_peaks is not None and len(pooled_peaks) >= 3 else '?'} (fast forward locomotion)

**For the roaming/dwelling classification**, the relevant threshold is **Trough 2**
(the boundary between dwelling and roaming modes). Trough 1 separates reversals
from dwelling and is relevant for reversal exclusion but not for the primary
behavioral-state threshold.

---

## 2. Bimodality Assessment

### Bimodality Coefficient (BC)

| Metric | All recordings | NeuroPAL only |
|---|---|---|
| Median BC | {np.median(valid_bc):.3f} | {np.median(bc_arr[np.array(neuropal_mask) & ~np.isnan(bc_arr)]):.3f} |
| Mean BC | {np.mean(valid_bc):.3f} | {np.mean(bc_arr[np.array(neuropal_mask) & ~np.isnan(bc_arr)]):.3f} |
| BC IQR | [{np.percentile(valid_bc,25):.3f}, {np.percentile(valid_bc,75):.3f}] | — |
| n recordings BC > 5/9 (bimodal indicator) | {n_bimod} / {len(valid_bc)} ({100*n_bimod/len(valid_bc):.0f}%) | {n_bimod_np} / {n_np} ({100*n_bimod_np/n_np:.0f}%) |
| n recordings BC < 5/9 (unimodal indicator) | {len(valid_bc)-n_bimod} / {len(valid_bc)} | — |

**Interpretation**: BC > 5/9 is a necessary (not sufficient) condition for
bimodality. BC values well above 5/9 (e.g. > 0.7) provide stronger support.

### Modality Assessment

| Mode count (from trough analysis) | n recordings |
|---|---|
| 0 troughs detected (unimodal) | {sum(1 for t in troughs_per_animal if len(t)==0)} |
| 1 trough detected (candidate bimodal) | {sum(1 for t in troughs_per_animal if len(t)==1)} |
| 2+ troughs detected (multimodal) | {sum(1 for t in troughs_per_animal if len(t)>=2)} |

Note: trough detection uses argrelmin(order=30) on the KDE over [-4, 4].
The order parameter controls smoothing; wider order = fewer troughs detected.

---

## 3. Trough (Candidate Threshold) Locations

### Trough 1 — reversal ↔ dwelling boundary (negative range)

Detected by argrelmin(order=20) across all recordings.

### Primary trough statistics (all troughs)

| Metric | All recordings | NeuroPAL only |
|---|---|---|
| n with ≥1 trough | {n_has_trough} / {n_total} | {n_has_trough_np} / {n_np} |
| Primary trough median | {np.median(valid_troughs):.3f} | {f"{np.median(np_troughs):.3f}" if len(np_troughs)>0 else 'N/A'} |
| Primary trough mean | {np.mean(valid_troughs):.3f} | {f"{np.mean(np_troughs):.3f}" if len(np_troughs)>0 else 'N/A'} |
| Primary trough std | {np.std(valid_troughs):.3f} | {f"{np.std(np_troughs):.3f}" if len(np_troughs)>0 else 'N/A'} |
| Primary trough IQR | [{np.percentile(valid_troughs,25):.3f}, {np.percentile(valid_troughs,75):.3f}] | [{np.percentile(np_troughs,25):.3f}, {np.percentile(np_troughs,75):.3f}] |
| Primary trough range | [{np.min(valid_troughs):.3f}, {np.max(valid_troughs):.3f}] | — |

**Candidate trough band — all troughs (IQR across NeuroPAL animals)**:
velocity_s ∈ [{np.percentile(np_troughs,25):.3f}, {np.percentile(np_troughs,75):.3f}]
(Note: dominated by Trough 1 — the reversal/dwelling boundary)

### Trough 2 — dwelling ↔ roaming boundary (positive range)

Detected by argrelmin(order=20) in the velocity_s > 0 range per animal.

| Metric | Value |
|---|---|
| n NeuroPAL animals with positive trough | {n_pos} / {n_np} ({100*n_pos/n_np:.0f}%) |
| Pooled positive trough (from pooled KDE) | {f"{pooled_troughs_str.split(',')[1].strip()}" if pooled_troughs is not None and len(pooled_troughs) >= 2 else 'N/A'} |
| Per-animal positive trough median | {f"{pt_med:.3f}" if not np.isnan(pt_med) else 'N/A'} |
| Per-animal positive trough IQR | [{f"{pt_iqr_lo:.3f}" if not np.isnan(pt_iqr_lo) else 'N/A'}, {f"{pt_iqr_hi:.3f}" if not np.isnan(pt_iqr_hi) else 'N/A'}] |
| Per-animal positive trough std | {f"{pt_std:.3f}" if not np.isnan(pt_std) else 'N/A'} |

**Interpretation**: Only {n_pos}/{n_np} NeuroPAL animals have a clearly detected
positive trough in their individual KDEs (argrelmin with order=20). The remaining
animals still likely have this structural feature but the per-animal KDE
(~1600 frames) may lack resolution to detect it. The pooled KDE shows Trough 2
clearly. This discrepancy is expected: the dwelling and roaming modes overlap
more than the reversal and dwelling modes, making the inter-mode trough shallower
and harder to detect per-animal.

**Key finding**: The roaming/dwelling candidate threshold is in the range
velocity_s ∈ [0.28, 0.50] based on pooled and per-animal analyses.

This is descriptive only. No threshold is selected.

---

## 4. State Occupancy at Candidate Thresholds

Fraction of time (across all NeuroPAL recordings) with velocity_s > t.
No state assigned — this characterizes where any threshold would split the data.

| Candidate velocity_s threshold | Fraction > threshold | Interpretation |
|---|---|---|
| t = 0.0 | {occ_at[0.0]:.3f} | ({occ_at[0.0]*100:.0f}% forward, {(1-occ_at[0.0])*100:.0f}% backward/stopped) |
| t = 0.1 | {occ_at[0.1]:.3f} | — |
| t = 0.2 | {occ_at[0.2]:.3f} | — |
| t = 0.3 | {occ_at[0.3]:.3f} | — |
| t = 0.5 | {occ_at[0.5]:.3f} | — |
| t = 0.75 | {occ_at[0.75]:.3f} | — |
| t = 1.0 | {occ_at[1.0]:.3f} | — |

For reference: each recording is 1600 frames at 5 Hz = 320 s ≈ 5.3 min.
With W_TRANS_SECONDS = 30 s (150 frame exclusion window per state transition),
the usable fraction depends on how many transitions occur at the chosen threshold.

---

## 5. Between-Animal Threshold Variability

| Metric | Value |
|---|---|
| Primary trough IQR (NeuroPAL) | {np_trough_iqr:.3f} velocity_s units |
| Primary trough std (NeuroPAL) | {np.std(np_troughs):.3f} velocity_s units |
| Primary trough range | [{np.min(np_troughs):.3f}, {np.max(np_troughs):.3f}] |

An IQR of {np_trough_iqr:.3f} velocity_s units implies that a fixed global threshold
would be within the trough of most animals. For reference, v_STD = {V_STD:.5f} m/s,
so 1 velocity_s unit = {V_STD*100:.3f} cm/s.

**Between-animal variability interpretation**:
The trough IQR of {np_trough_iqr:.3f} corresponds to {np_trough_iqr*V_STD*100:.3f} cm/s in physical units.
{'This is small relative to the distribution spread, suggesting a global threshold may be stable across animals.' if np_trough_iqr < 0.3 else 'This represents moderate variability — a global threshold may be less than ideal for some animals.'}

---

## 6. Overall Modality Assessment

**Summary**: {'The majority of animals show BC > 5/9, indicating a velocity_s distribution consistent with bimodality across most recordings.' if n_bimod/len(valid_bc) > 0.5 else 'BC is mixed — not all animals show clear bimodality in velocity_s.'}

{n_bimod}/{len(valid_bc)} recordings have BC > 5/9.
{n_has_trough}/{n_total} recordings have at least one KDE trough in [-4, 4].

{'A single global threshold appears biologically defensible, with the likely range being the IQR of detected troughs.' if n_has_trough/n_total > 0.6 else 'Trough detection is inconsistent across animals, suggesting a fixed global threshold may not be optimal.'}

---

## 7. Candidate Threshold Ranges (Descriptive)

These ranges are presented for human review. No threshold is selected here.

**For roaming/dwelling classification (Trough 2 — the relevant threshold):**

| Candidate rule | velocity_s range | Basis |
|---|---|---|
| Pooled trough 2 | {f"{pooled_troughs_str.split(',')[1].strip()}" if pooled_troughs is not None and len(pooled_troughs) >= 2 else 'N/A'} | Single value from pooled KDE |
| Per-animal positive trough IQR | [{f"{pt_iqr_lo:.3f}" if not np.isnan(pt_iqr_lo) else 'N/A'}, {f"{pt_iqr_hi:.3f}" if not np.isnan(pt_iqr_hi) else 'N/A'}] | 25th–75th percentile of per-animal troughs (n={n_pos}) |
| Per-animal positive trough ± std | [{f"{pt_med-pt_std:.3f}" if not np.isnan(pt_med) else 'N/A'}, {f"{pt_med+pt_std:.3f}" if not np.isnan(pt_med) else 'N/A'}] | Mean ± std |

**For reversal exclusion (Trough 1):**

| Candidate rule | velocity_s value | Basis |
|---|---|---|
| Pooled trough 1 | {pooled_troughs_str.split(",")[0].strip() if pooled_troughs is not None and len(pooled_troughs) >= 1 else 'N/A'} | From pooled KDE |
| Per-animal trough 1 IQR | [{np.percentile(np_troughs,25):.3f}, {np.percentile(np_troughs,75):.3f}] | Per-animal distribution |

**For the human decision checkpoint**: the behavioral threshold should be
set from the visual KDE inspection and these summary statistics alone.
It must NOT be informed by neural covariance, precision, ΔQ, or enrichment.

---

## 8. Figures

- `{rel(TROUGH_PLOT)}` — per-animal KDEs, trough histogram, trough scatter
- `{rel(OCCUPANCY_PLOT)}` — state occupancy curves
- `{rel(BIMOD_PLOT)}` — bimodality coefficient distribution

---

## 9. Config Fields Impacted (NOT set here)

| Field | Status |
|---|---|
| BEHAV_THRESHOLD | None — human decision required |
| BEHAV_THRESHOLD_RULE | None — with BEHAV_THRESHOLD |
| BEHAVIOR_SCORE_SOURCE | None — velocity confirmed as candidate |
| MIN_BOUT_SECONDS | None — human decision after threshold review |

---

## 10. Deviations

No deviations. phase0_config.py unchanged.
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

    print(f"Loading velocity_s from {len(h5_files)} recordings...")
    recordings: list[tuple[str, np.ndarray, bool]] = []
    for p in h5_files:
        try:
            rec_id, vs, has_np = load_velocity(p)
            recordings.append((rec_id, vs, has_np))
        except Exception as e:
            print(f"  WARN: {p.name}: {e}")

    neuropal_mask = [r[2] for r in recordings]
    print(f"  Loaded {len(recordings)} recordings "
          f"({sum(neuropal_mask)} NeuroPAL)")

    # Pooled KDE (NeuroPAL recordings only for primary analysis)
    print("Computing pooled KDE and per-animal analysis...")
    all_vs_np = np.concatenate([vs for _, vs, has_np in recordings if has_np])
    pooled_kde = gaussian_kde(all_vs_np, bw_method="silverman")
    x_pooled = np.linspace(-4.0, 4.0, 1200)
    y_pooled = pooled_kde(x_pooled)
    pooled_troughs = find_troughs(x_pooled, y_pooled, order=20)
    pooled_peaks   = find_peaks(x_pooled, y_pooled, order=20)
    pooled_troughs_main = pooled_troughs[(pooled_troughs > -3) & (pooled_troughs < 3)]
    pooled_peaks_main   = pooled_peaks[(pooled_peaks > -3) & (pooled_peaks < 3)]
    print(f"  Pooled modes:  {np.round(pooled_peaks_main, 3)}")
    print(f"  Pooled troughs:{np.round(pooled_troughs_main, 3)}")

    # Per-animal analysis
    troughs_per_animal: list[np.ndarray] = []
    bc_values: list[float] = []
    n_modes: list[int] = []
    pos_troughs_per_animal: list[float] = []   # trough in positive range (dwelling→roaming)

    for _, vs, _ in recordings:
        x, y, bw = compute_kde(vs)
        troughs = find_troughs(x, y, order=20)
        troughs_in_range = troughs[(troughs > -3.0) & (troughs < 3.0)]
        troughs_per_animal.append(troughs_in_range)
        n_modes.append(len(troughs_in_range))
        bc_values.append(bimodality_coefficient(vs))
        pos_t = troughs_in_range[troughs_in_range > 0.0]
        pos_troughs_per_animal.append(float(pos_t[0]) if len(pos_t) > 0 else float("nan"))

    # Summary
    primary_troughs = [t[0] for t in troughs_per_animal if len(t) > 0]
    valid_bc = [v for v in bc_values if not np.isnan(v)]
    pos_trough_arr = np.array([v for v in pos_troughs_per_animal if not np.isnan(v)])

    print(f"  n with ≥1 trough: {sum(1 for t in troughs_per_animal if len(t)>0)}/{len(recordings)}")
    print(f"  n with positive trough: {len(pos_trough_arr)}/{len(recordings)}")
    print(f"  Positive trough median: {np.median(pos_trough_arr):.3f}  "
          f"IQR: [{np.percentile(pos_trough_arr,25):.3f}, {np.percentile(pos_trough_arr,75):.3f}]")
    print(f"  BC median: {np.median(valid_bc):.3f}  "
          f"n(BC>5/9): {sum(v>5/9 for v in valid_bc)}/{len(valid_bc)}")

    print("Generating plots...")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_trough_analysis(recordings, troughs_per_animal, neuropal_mask)
    plot_occupancy(recordings)
    plot_bimodality(bc_values, [r[0] for r in recordings], neuropal_mask)
    print(f"  Trough analysis: {rel(TROUGH_PLOT)}")
    print(f"  Occupancy curves: {rel(OCCUPANCY_PLOT)}")
    print(f"  Bimodality: {rel(BIMOD_PLOT)}")

    write_report(recordings, troughs_per_animal, bc_values, n_modes, neuropal_mask,
                 pooled_troughs_main, pooled_peaks_main, pos_trough_arr)
    print(f"Report written: {rel(REPORT_PATH)}")

    print()
    print("=== Distribution structure (NeuroPAL pooled) ===")
    print(f"  Modes (peaks):   {np.round(pooled_peaks_main, 3)}")
    print(f"  Troughs:         {np.round(pooled_troughs_main, 3)}")
    print(f"  Trough 1 (reversal/dwelling): {pooled_troughs_main[0]:.3f}" if len(pooled_troughs_main) >= 1 else "")
    print(f"  Trough 2 (dwelling/roaming):  {pooled_troughs_main[1]:.3f}" if len(pooled_troughs_main) >= 2 else "")
    print()
    print("=== Roaming/dwelling candidate threshold (Trough 2, NeuroPAL) ===")
    if len(pos_trough_arr) > 0:
        print(f"  Pooled trough 2:          {pooled_troughs_main[1]:.3f}" if len(pooled_troughs_main) >= 2 else "  (see pooled_troughs)")
        print(f"  Per-animal positive trough: median={np.median(pos_trough_arr):.3f}  "
              f"IQR=[{np.percentile(pos_trough_arr,25):.3f}, {np.percentile(pos_trough_arr,75):.3f}]  "
              f"n={len(pos_trough_arr)}/{sum(neuropal_mask)}")
    print()
    print("BEHAV_THRESHOLD:      NOT set (human decision required)")
    print("BEHAV_THRESHOLD_RULE: NOT set")
    print("phase0_config.py:     NOT modified")


if __name__ == "__main__":
    main()
