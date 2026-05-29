# Stage 5 Transition-Window Feasibility Sweep

Date: 2026-05-28
Fixed pipeline:
  EWMA tau = 20.0 s  (EWMA_TIMESCALE_SECONDS, provisional)
  BEHAV_THRESHOLD = 0.284 (LOCKED)
Recordings: 40 NeuroPAL
Candidate W_TRANS windows tested: [0, 5, 10, 15, 20, 30] s

NOT computed:
  - Covariance, precision, DeltaQ, enrichment
  - Stationarity / variability analysis
  - Neural analysis

W_TRANS_SECONDS NOT set. MIN_BOUT_SECONDS NOT set.

---

## 1. Frame Allocation vs W_TRANS

Median fractions across 40 NeuroPAL recordings.

| W_TRANS | frac_roam (med) | frac_nr (med) | frac_lost (med) | frac_total (med) | n_zero_roam |
|---------|----------------|---------------|-----------------|------------------|-------------|
|   0 s | 0.224 | 0.776 | 0.000 | 1.000 |  4/40 |
|   5 s | 0.071 | 0.553 | 0.291 | 0.709 | 10/40 |
|  10 s | 0.026 | 0.450 | 0.455 | 0.545 | 15/40 |
|  15 s | 0.000 | 0.347 | 0.573 | 0.427 | 21/40 |
|  20 s | 0.000 | 0.283 | 0.674 | 0.326 | 22/40 |
|  30 s | 0.000 | 0.189 | 0.776 | 0.224 | 25/40 |

Notes:
- frac_roam + frac_nr + frac_lost ≈ 1.0 per recording
- n_zero_roam = recordings with 0 retained roaming frames

---

## 2. Retained Time per Animal (seconds)

| W_TRANS | roam_med (s) | roam_IQR (s) | nr_med (s) | nr_IQR (s) |
|---------|-------------|--------------|-----------|------------|
|   0 s | 72 | [22, 142] | 251 | [179, 300] |
|   5 s | 23 | [1, 73] | 178 | [89, 283] |
|  10 s | 8 | [0, 49] | 145 | [43, 256] |
|  15 s | 0 | [0, 32] | 112 | [34, 239] |
|  20 s | 0 | [0, 19] | 91 | [28, 228] |
|  30 s | 0 | [0, 5] | 61 | [18, 208] |

At 5 Hz: 1 s = 5 frames. N_COMMON_NEURONS = 61.

---

## 3. Epoch Duration vs W_TRANS

Epochs = consecutive retained frames in one state (after exclusion windows applied).
Red dashed line in figures = 2 × W_TRANS (minimum viable bout).

| W_TRANS | roam_med (s) | roam_p90 (s) | n_roam_ep | nr_med (s) | nr_p90 (s) | n_nr_ep |
|---------|-------------|-------------|-----------|-----------|-----------|---------|
|   0 s | 3.8 | 23.7 |  372 | 6.4 | 62.8 |  381 |
|   5 s | 12.2 | 42.1 |   89 | 20.1 | 134.1 |  150 |
|  10 s | 16.0 | 50.8 |   51 | 28.9 | 164.1 |  102 |
|  15 s | 19.3 | 57.7 |   32 | 36.3 | 186.7 |   78 |
|  20 s | 15.2 | 53.0 |   27 | 47.2 | 219.4 |   63 |
|  30 s | 9.8 | 40.2 |   18 | 54.5 | 258.1 |   46 |

---

## 4. Feasibility Analysis

### 4.1 Roaming retained-frame coverage

First W_TRANS where ALL 40 animals retain ≥1 roaming epoch: **None s** 
First W_TRANS where median retained roaming ≥ 30 s: **0.0**
First W_TRANS where all animals retain ≥1 non-roaming epoch: **0.0 s**

### 4.2 Biological plausibility assessment

The transition exclusion window serves two purposes:
1. Remove frames contaminated by ongoing state transitions (signal not in steady state)
2. Ensure epochs are from persistent behavioral states, not transient fluctuations

At tau = 20.0 s EWMA, the behavioral state signal already has smoothing on a
20.0-s timescale. This means:
  - State transitions in the smoothed signal take ≈ 20.0 s to resolve
  - W_TRANS values < 20.0 s may not fully exclude transition artifacts
  - W_TRANS values >> 20.0 s exclude more data than necessary
  - A value near tau itself (20.0 s) is a natural lower bound

| W_TRANS | Roaming animals (≥1 epoch) | Roaming retained (med) | Assessment |
|---------|--------------------------|------------------------|------------|
|   0 s | 36/40 | 72 s | No exclusion — transition artifacts retained |
|   5 s | 30/40 | 23 s | W_TRANS < tau — partial exclusion only |
|  10 s | 25/40 | 8 s | W_TRANS < tau — partial exclusion only |
|  15 s | 19/40 | 0 s | W_TRANS < tau — partial exclusion only |
|  20 s | 18/40 | 0 s | W_TRANS = tau — natural lower bound |
|  30 s | 15/40 | 0 s | Infeasible — >50% animals have 0 roam epochs |

### 4.3 Effect on effective covariance sample sizes (qualitative)

For Stage 6 n_eff analysis (cross-product autocorrelation), effective samples
accrue at the rate of 1 independent sample per τ_int frames, where τ_int is
the GCaMP6s autocorrelation time (estimated ≈ 5–20 s at 5 Hz in prior studies).

Rough rule: n_eff ≈ T_retained / (2 × τ_int)

At τ_int ≈ 10 s (middle estimate), for roaming:
  W_TRANS=  0s: median roaming retained=72s → n_eff_rough ≈ 3.6 per animal (needs ≥ 61 for pairwise analysis)
  W_TRANS=  5s: median roaming retained=23s → n_eff_rough ≈ 1.1 per animal (needs ≥ 61 for pairwise analysis)
  W_TRANS= 10s: median roaming retained=8s → n_eff_rough ≈ 0.4 per animal (needs ≥ 61 for pairwise analysis)
  W_TRANS= 15s: no retained roaming
  W_TRANS= 20s: no retained roaming
  W_TRANS= 30s: no retained roaming

These are rough estimates only. Actual n_eff will be computed in Stage 6
from cross-product autocorrelation times.

---

## 5. Candidate W_TRANS Ranges (Descriptive — NOT final)

| Candidate | Biological rationale | Coverage | Data volume |
|-----------|---------------------|----------|-------------|
| W_TRANS = tau = 20.0 s | Matches EWMA timescale; minimal exclusion | All/most animals | Highest |
| W_TRANS = 2×tau = 40.0 s | Double-margin for transition resolution | Partial | Moderate |
| W_TRANS = 30 s (original) | Flavell lab convention | Only subset | Lowest |

The key tradeoff:
- Smaller W_TRANS → more retained data, but some transition-contamination risk
- Larger W_TRANS → cleaner epochs, but fewer animals/epochs contribute

At tau = 20.0 s, a W_TRANS in the range 20.0–30 s appears most biologically
justified: it excludes one EWMA time constant around each transition
(where the signal is resolving) while preserving substantially more data
than W_TRANS = 30 s.

Human decision required. W_TRANS_SECONDS NOT set here.

---

## 6. Figures

- `results/figures/stage05_wtrans_sweep.pdf` — 6-panel summary sweep
- `results/figures/stage05_wtrans_epochs.pdf` — epoch-duration histograms per W_TRANS
- `results/figures/stage05_wtrans_per_animal.pdf` — per-animal retained-time distributions

---

## 7. Config Fields NOT Changed

| Field | Value | Status |
|---|---|---|
| BEHAV_THRESHOLD | 0.284 | LOCKED |
| EWMA_TIMESCALE_SECONDS | 20.0 | Provisional |
| W_TRANS_SECONDS | 30.0 | NOT revised here |
| MIN_BOUT_SECONDS | None | NOT SET |

---

## 8. Deviations

No deviations. No config fields changed. Threshold and EWMA tau fixed.
W_TRANS_SECONDS sweep is descriptive only.
