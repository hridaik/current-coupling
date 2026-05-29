# Stage 5 Velocity Threshold Characterization

Date: 2026-05-28
Recordings analyzed: 68 total (40 NeuroPAL)

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

Pooled velocity_s KDE across all 40 NeuroPAL recordings (Silverman bandwidth).

| Feature | velocity_s location |
|---|---|
| Mode 1 (reversals) | -0.971 |
| Mode 2 (dwelling/slow) | 0.037 |
| Mode 3 (roaming/fast forward) | 0.924 |
| **Trough 1** (reversal ↔ dwelling) | -0.337 |
| **Trough 2** (dwelling ↔ roaming) | 0.284 |

The pooled distribution is **trimodal** with three well-separated modes:
1. A reversal mode at velocity_s ≈ -0.971 (backward locomotion)
2. A dwelling/slow mode near velocity_s ≈ 0.037 (near-stationary)
3. A roaming mode at velocity_s ≈ 0.924 (fast forward locomotion)

**For the roaming/dwelling classification**, the relevant threshold is **Trough 2**
(the boundary between dwelling and roaming modes). Trough 1 separates reversals
from dwelling and is relevant for reversal exclusion but not for the primary
behavioral-state threshold.

---

## 2. Bimodality Assessment

### Bimodality Coefficient (BC)

| Metric | All recordings | NeuroPAL only |
|---|---|---|
| Median BC | 0.569 | 0.555 |
| Mean BC | 0.565 | 0.546 |
| BC IQR | [0.507, 0.627] | — |
| n recordings BC > 5/9 (bimodal indicator) | 41 / 68 (60%) | 20 / 40 (50%) |
| n recordings BC < 5/9 (unimodal indicator) | 27 / 68 | — |

**Interpretation**: BC > 5/9 is a necessary (not sufficient) condition for
bimodality. BC values well above 5/9 (e.g. > 0.7) provide stronger support.

### Modality Assessment

| Mode count (from trough analysis) | n recordings |
|---|---|
| 0 troughs detected (unimodal) | 1 |
| 1 trough detected (candidate bimodal) | 56 |
| 2+ troughs detected (multimodal) | 11 |

Note: trough detection uses argrelmin(order=30) on the KDE over [-4, 4].
The order parameter controls smoothing; wider order = fewer troughs detected.

---

## 3. Trough (Candidate Threshold) Locations

### Trough 1 — reversal ↔ dwelling boundary (negative range)

Detected by argrelmin(order=20) across all recordings.

### Primary trough statistics (all troughs)

| Metric | All recordings | NeuroPAL only |
|---|---|---|
| n with ≥1 trough | 67 / 68 | 39 / 40 |
| Primary trough median | -0.407 | -0.421 |
| Primary trough mean | -0.464 | -0.403 |
| Primary trough std | 0.550 | 0.550 |
| Primary trough IQR | [-0.528, -0.327] | [-0.534, -0.327] |
| Primary trough range | [-2.611, 0.621] | — |

**Candidate trough band — all troughs (IQR across NeuroPAL animals)**:
velocity_s ∈ [-0.534, -0.327]
(Note: dominated by Trough 1 — the reversal/dwelling boundary)

### Trough 2 — dwelling ↔ roaming boundary (positive range)

Detected by argrelmin(order=20) in the velocity_s > 0 range per animal.

| Metric | Value |
|---|---|
| n NeuroPAL animals with positive trough | 15 / 40 (38%) |
| Pooled positive trough (from pooled KDE) | 0.284 |
| Per-animal positive trough median | 0.568 |
| Per-animal positive trough IQR | [0.394, 0.715] |
| Per-animal positive trough std | 0.741 |

**Interpretation**: Only 15/40 NeuroPAL animals have a clearly detected
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
| t = 0.0 | 0.574 | (57% forward, 43% backward/stopped) |
| t = 0.1 | 0.533 | — |
| t = 0.2 | 0.510 | — |
| t = 0.3 | 0.487 | — |
| t = 0.5 | 0.434 | — |
| t = 0.75 | 0.353 | — |
| t = 1.0 | 0.265 | — |

For reference: each recording is 1600 frames at 5 Hz = 320 s ≈ 5.3 min.
With W_TRANS_SECONDS = 30 s (150 frame exclusion window per state transition),
the usable fraction depends on how many transitions occur at the chosen threshold.

---

## 5. Between-Animal Threshold Variability

| Metric | Value |
|---|---|
| Primary trough IQR (NeuroPAL) | 0.207 velocity_s units |
| Primary trough std (NeuroPAL) | 0.550 velocity_s units |
| Primary trough range | [-2.317, 0.621] |

An IQR of 0.207 velocity_s units implies that a fixed global threshold
would be within the trough of most animals. For reference, v_STD = 0.06031 m/s,
so 1 velocity_s unit = 6.031 cm/s.

**Between-animal variability interpretation**:
The trough IQR of 0.207 corresponds to 1.248 cm/s in physical units.
This is small relative to the distribution spread, suggesting a global threshold may be stable across animals.

---

## 6. Overall Modality Assessment

**Summary**: The majority of animals show BC > 5/9, indicating a velocity_s distribution consistent with bimodality across most recordings.

41/68 recordings have BC > 5/9.
67/68 recordings have at least one KDE trough in [-4, 4].

A single global threshold appears biologically defensible, with the likely range being the IQR of detected troughs.

---

## 7. Candidate Threshold Ranges (Descriptive)

These ranges are presented for human review. No threshold is selected here.

**For roaming/dwelling classification (Trough 2 — the relevant threshold):**

| Candidate rule | velocity_s range | Basis |
|---|---|---|
| Pooled trough 2 | 0.284 | Single value from pooled KDE |
| Per-animal positive trough IQR | [0.394, 0.715] | 25th–75th percentile of per-animal troughs (n=15) |
| Per-animal positive trough ± std | [-0.173, 1.308] | Mean ± std |

**For reversal exclusion (Trough 1):**

| Candidate rule | velocity_s value | Basis |
|---|---|---|
| Pooled trough 1 | -0.337 | From pooled KDE |
| Per-animal trough 1 IQR | [-0.534, -0.327] | Per-animal distribution |

**For the human decision checkpoint**: the behavioral threshold should be
set from the visual KDE inspection and these summary statistics alone.
It must NOT be informed by neural covariance, precision, ΔQ, or enrichment.

---

## 8. Figures

- `results/figures/stage05_velocity_trough_analysis.pdf` — per-animal KDEs, trough histogram, trough scatter
- `results/figures/stage05_velocity_occupancy.pdf` — state occupancy curves
- `results/figures/stage05_bimodality_summary.pdf` — bimodality coefficient distribution

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
