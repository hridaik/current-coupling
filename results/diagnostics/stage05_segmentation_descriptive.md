# Stage 5 Segmentation Descriptive Audit

Date: 2026-05-28
Threshold applied: BEHAV_THRESHOLD = 0.284 (velocity_s)
Rule: BEHAV_THRESHOLD_RULE = "pooled_velocity_s_kde_trough_between_dwelling_and_roaming"
Recordings: 68 total (40 NeuroPAL)

## Scope

Provisional binary roam/non-roam labels applied for descriptive purposes.
roaming  = velocity_s > 0.284
non-roaming = velocity_s ≤ 0.284

W_TRANS_SECONDS = 30.0 s (150 frames) — NOT yet applied.
MIN_BOUT_SECONDS = None — NOT yet set; bout statistics are unfiltered.

NOT computed:
  - Covariance, precision, DeltaQ, enrichment
  - Stationarity / variability analysis
  - Neural-informed threshold adjustment

---

## 1. Roaming Occupancy

| Metric | All recordings (n=68) | NeuroPAL only (n=40) |
|---|---|---|
| Mean roaming occupancy | 0.528 | 0.491 |
| Median roaming occupancy | 0.539 | 0.495 |
| Std | 0.097 | 0.094 |
| IQR | [0.455, 0.597] | [0.400, 0.566] |
| Range | [0.332, 0.701] | [0.332, 0.686] |

Non-roaming occupancy = 1 − roaming occupancy.
Median non-roaming (NeuroPAL): 0.505

The between-animal std of 0.094 is low relative to the
mean occupancy of 0.491. Animals vary in their roaming/dwelling balance.

---

## 2. Bout-Length Distributions (NeuroPAL, no MIN_BOUT_SECONDS filter)

All bouts counted, including very short ones that would typically be excluded.

### Roaming bouts (n=2,597 total across 40 recordings)

| Metric | Value |
|---|---|
| Median | 1.8 s |
| Mean | 2.4 s |
| Std | 2.4 s |
| p25 | 0.8 s |
| p75 | 3.2 s |
| p90 | 5.2 s |
| p95 | 6.8 s |
| Min | 0.2 s |
| Max | 30.0 s |
| Fraction ≥ 10 s | 0.016 |
| Fraction ≥ 20 s | 0.001 |
| Fraction ≥ 30 s (W_TRANS) | 0.000 |
| Fraction ≥ 60 s | 0.000 |

### Non-roaming bouts (n=2,594 total across 40 recordings)

| Metric | Value |
|---|---|
| Median | 1.8 s |
| Mean | 2.5 s |
| Std | 2.5 s |
| p25 | 0.6 s |
| p75 | 3.6 s |
| p90 | 5.8 s |
| p95 | 7.2 s |
| Min | 0.2 s |
| Max | 29.2 s |
| Fraction ≥ 10 s | 0.016 |
| Fraction ≥ 20 s | 0.000 |
| Fraction ≥ 30 s (W_TRANS) | 0.000 |
| Fraction ≥ 60 s | 0.000 |

---

## 3. Transition Rates (NeuroPAL recordings)

| Metric | Value |
|---|---|
| Mean transitions/min | 8.00 |
| Median transitions/min | 7.86 |
| Std transitions/min | 1.83 |
| IQR | [6.54, 8.96] |
| Mean n_roam_bouts per recording | 64.9 |
| Median n_roam_bouts | 64 |
| Mean n_non_roam_bouts | 64.8 |
| Median n_non_roam_bouts | 64 |

At median 7.86 transitions/min, an average recording of
16.1 min contains approximately
127 state transitions.
Each W_TRANS = 30 s exclusion window removes 150 frames per transition;
at 127 transitions this removes
~393.0%
of total frames.

---

## 4. Segmentation Stability Across Animals

| Metric | NeuroPAL recordings |
|---|---|
| n recordings with roaming occupancy 0.2–0.8 (balanced) | 40 / 40 |
| n recordings with occupancy < 0.1 (mostly non-roaming) | 0 / 40 |
| n recordings with occupancy > 0.9 (mostly roaming) | 0 / 40 |
| IQR of occupancy | [0.400, 0.566] |

The segmentation appears stable: most recordings have mixed roaming/non-roaming occupancy.

---

## 5. Candidate MIN_BOUT_SECONDS Ranges (Descriptive)

These are presented for human review only. MIN_BOUT_SECONDS is NOT set here.

### For roaming bouts:

| Candidate filter | Fraction surviving | n bouts surviving |
|---|---|---|
| ≥ 10 s | 0.016 | 41 |
| ≥ 20 s | 0.001 | 2 |
| ≥ 30 s | 0.000 | 1 |
| ≥ 60 s | 0.000 | 0 |

### For non-roaming bouts:

| Candidate filter | Fraction surviving | n bouts surviving |
|---|---|---|
| ≥ 10 s | 0.016 | 42 |
| ≥ 20 s | 0.000 | 1 |
| ≥ 30 s | 0.000 | 0 |
| ≥ 60 s | 0.000 | 0 |

**Key consideration**: W_TRANS_SECONDS = 30 s means each bout must have a
sustained portion of at least 30.0 s AFTER transition exclusion.
A bout of 30 s with a W_TRANS window on each end has 0 net usable frames;
bouts must be significantly longer than W_TRANS to contribute data.

The median roaming bout is 1.8 s. Only 0.0% of roaming bouts
exceed 30 s. Only 0.0% exceed 60 s (2 × W_TRANS).

A MIN_BOUT_SECONDS of 30–60 s would retain 0.0%–0.0% of roaming
bouts for the roaming state, and 0.0%–0.0% of non-roaming bouts.
The choice of MIN_BOUT_SECONDS should balance usable frame count against
bout-duration bias.

---

## 6. Figures

- `results/figures/stage05_occupancy_per_animal.pdf` — per-animal occupancy and transition rate
- `results/figures/stage05_bout_lengths.pdf` — bout length distributions
- `results/figures/stage05_transitions.pdf` — bout count per recording

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
