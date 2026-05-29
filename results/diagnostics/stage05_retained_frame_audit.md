# Stage 5 Retained-Frame Feasibility Audit

Date: 2026-05-28
Pipeline:
  EWMA tau = 20.0 s (provisional, approved 2026-05-28)
  BEHAV_THRESHOLD = 0.284 (LOCKED)
  W_TRANS_SECONDS = 30.0 s (= 150 frames at 5 Hz)
Recordings: 40 NeuroPAL

## Scope

Applied the full provisional segmentation pipeline and counted retained frames
after transition-exclusion windows. No covariance/precision/DeltaQ computed.
MIN_BOUT_SECONDS NOT set.

Retained frame definition:
  - Belongs to a sustained state (velocity_s_ewma20 > 0.284 or ≤ 0.284)
  - NOT within 150 frames of any state transition (W_TRANS exclusion)

---

## 1. Frame Allocation Summary (NeuroPAL recordings, n=40)

| Metric | Roaming | Non-roaming | Transition-lost | Total retained |
|---|---|---|---|---|
| Mean fraction of recording | 0.031 | 0.341 | 0.628 | 0.372 |
| Median fraction | 0.000 | 0.189 | 0.776 | 0.224 |
| IQR | [0.000, 0.015] | [0.055, 0.650] | [0.350, 0.921] | [0.079, 0.650] |

Pooled across all 40 NeuroPAL recordings:
  - Total frames:           64,308
  - Retained roaming:       2,019 (3.1%)
  - Retained non-roaming:   21,938   (34.1%)
  - Total retained:         23,957 (37.3%)

---

## 2. Per-Animal Retained Frame Counts

| Metric | Roaming retained (s) | Non-roaming retained (s) |
|---|---|---|
| Median | 0 s | 61 s |
| Mean | 10 s | 110 s |
| Min | 0 s | 0 s |
| Max | 166 s | 323 s |
| IQR | [0, 5] s | [18, 208] s |

At 5 Hz, each retained second = 5 frames.
Per-animal retained frames (median):
  Roaming:     0 s × 5 = 0 frames
  Non-roaming: 61 s × 5 = 305 frames

---

## 3. Sustained-Epoch Distributions

Epochs = consecutive retained-frame runs in the same state (after W_TRANS exclusion).

### Roaming epochs (18 total across 40 recordings)

| Metric | Value |
|---|---|
| Median duration | 9.8 s |
| Mean duration | 22.4 s |
| p75 | 27.5 s |
| p90 | 40.2 s |
| p95 | 56.0 s |
| Max | 139.8 s |
| Fraction >= 10 s | 0.500 |
| Fraction >= 20 s | 0.389 |
| Fraction >= 30 s | 0.222 |
| Fraction >= 60 s | 0.056 |
| Median n_epochs per recording | 0 |
| Min n_epochs per recording | 0 |
| Max n_epochs per recording | 3 |

### Non-roaming epochs (46 total across 40 recordings)

| Metric | Value |
|---|---|
| Median duration | 54.5 s |
| Mean duration | 95.4 s |
| p75 | 138.9 s |
| p90 | 258.1 s |
| p95 | 322.2 s |
| Max | 323.0 s |
| Fraction >= 10 s | 0.935 |
| Fraction >= 20 s | 0.804 |
| Fraction >= 30 s | 0.652 |
| Fraction >= 60 s | 0.457 |
| Median n_epochs per recording | 1 |
| Min n_epochs per recording | 0 |
| Max n_epochs per recording | 3 |

---

## 4. W_TRANS Feasibility Assessment

W_TRANS_SECONDS = 30.0 s = 150 frames.
A bout must exceed 2 × 30 = 60 s to contribute ANY retained frames.

Number of recordings with ZERO roaming epochs:    25 / 40
Number of recordings with ZERO non-roaming epochs:9 / 40

Min n_roam_epochs per animal:     0
Min n_nr_epochs per animal:       0

**Assessment**: WARNING: some recordings have 0 epochs in one state after W_TRANS exclusion.

---

## 5. Adequacy for Covariance Estimation (Stage 6 context)

For Stage 6 n_eff computation from cross-products, each epoch contributes
independent samples. The key question is whether retained-frame counts are
adequate for stable covariance estimates.

Rule of thumb (task.md Stage 6): n_eff / N_COMMON_NEURONS ≥ 1 per epoch
is the minimum, with ≥ 5 being adequate for animal-level estimation.

At 5 Hz and with N_COMMON_NEURONS = 61:
  - 1 effective sample per neuron pair requires n_eff ≥ N*(N-1)/2 = 1830 samples
    (but n_eff << n_t due to autocorrelation, so this is not a simple frame count)
  - For a rough bound: 61 neurons × 5 independent samples ≥ 305 effective samples
  - At GCaMP6s timescales (τ_int ≈ 5–20 s), each effective sample ≈ 50-100 frames

Median retained roaming seconds per animal: 0 s
Median retained non-roaming seconds per animal: 61 s

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
| No filter | 18 | 100.0% | 9.8 |
| 10 s | 9 | 50.0% | 28.0 |
| 20 s | 7 | 38.9% | 37.8 |
| 30 s | 4 | 22.2% | 40.5 |
| 60 s | 1 | 5.6% | 139.8 |

For non-roaming epochs:

| MIN_BOUT_SECONDS | Epochs surviving | % | Median remaining (s) |
|---|---|---|---|
| No filter | 46 | 100.0% | 54.5 |
| 10 s | 43 | 93.5% | 59.6 |
| 20 s | 37 | 80.4% | 80.0 |
| 30 s | 30 | 65.2% | 109.5 |
| 60 s | 21 | 45.7% | 144.6 |

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

- `results/figures/stage05_retained_frames.pdf` — per-recording frame allocation, retained fraction, epoch counts
- `results/figures/stage05_epoch_durations.pdf` — epoch duration distributions (roaming and non-roaming)
- `results/figures/stage05_retained_summary.pdf` — per-animal epoch median scatter and epoch count scatter

---

## 9. Deviations

No deviations. Threshold and EWMA parameters applied as approved.
MIN_BOUT_SECONDS not set. phase0_config.py updated with EWMA_TIMESCALE_SECONDS = 20.0.
