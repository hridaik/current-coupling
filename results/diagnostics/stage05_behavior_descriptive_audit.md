# Stage 5 Behavioral Descriptive Audit

Date: 2026-05-28
Recordings loaded: 68 (40 with NeuroPAL registration, 28 without)

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
| Total recordings | 68 |
| NeuroPAL-registered recordings | 40 |
| Non-NeuroPAL recordings | 28 |
| Median duration | 16.2 min |
| Duration range | [15.5, 32.6] min |
| Duration IQR | [16.0, 16.3] min |
| Total recording time | 1158 min (19.3 h) |
| Median n_t (frames) | 1600 |
| Frame-count range | [1544, 1615] |
| Median n_neuron | 138 |
| n_neuron range | [105, 163] |
| Median n_neuron (NeuroPAL only) | 138 |
| Median NaN fraction (trace_array) | 0.0000 |
| NaN fraction range | [0.0000, 0.0000] |

Note on recording count:
  - The Stage 2 NeuroPAL label decode identified 40 NeuroPAL-labeled records.
  - The H5 data directory contains 68 processed files, of which 40 have
    the `neuropal_registration` group. The additional 28 recordings lack
    NeuroPAL identification and are NOT part of the primary N_COMMON_NEURONS = 61
    subgraph analysis. They may be used for n_eff and stationarity assessment if needed.

---

## 2. Coordinate Availability

| Coordinate / Array | Present in N recordings | % |
|---|---|---|
| gcamp/trace_array (z-scored) | 68 | 100% |
| gcamp/traces_array_F_F20 (ΔF/F₂₀) | 68 | 100% |
| gcamp/traces_array_F_Fmean (ΔF/Fmean) | 68 | 100% |
| neuropal_registration (NeuroPAL IDs) | 40 | 59% |

**COORD_ROBUSTNESS_1 candidate (`trace_array`)**: present in all 68 recordings.
**COORD_PRIMARY (CePNEM residuals)**: NOT pre-stored; requires CePNEM fit files.
**COORD_ROBUSTNESS_2 (deconvolved)**: NOT pre-stored; requires CePNEM fit files.

---

## 3. Velocity Distribution

Velocity is in m/s; velocity_s = velocity / v_STD (v_STD = 0.06031).
No threshold applied.

### Raw velocity (m/s)
mean=0.0107  median=0.0232  std=0.0660  p5=-0.1007  p95=0.1032  min=-0.2582  max=0.2465  n=109,052

### Standardized velocity_s (dimensionless)
mean=0.1772  median=0.3846  std=1.0938  p5=-1.6693  p95=1.7119  min=-4.2818  max=4.0872  n=109,052

**Interpretation note**: velocity_s > 0 = forward motion; velocity_s < 0 = backward
(reversals). The distribution below characterizes where a threshold would split
the data, but no threshold is chosen here.

Fraction of frames with velocity_s > 0:   0.612
Fraction of frames in reversal (rev_vec=1): 0.3519 (mean per recording)

**Velocity KDE plots**: see `results/figures/stage05_velocity_kde.pdf`

---

## 4. Reversal Statistics

| Metric | Value |
|---|---|
| Mean reversal fraction per recording | 0.3519 |
| Median reversal fraction | 0.3474 |
| Reversal fraction IQR | [0.2967, 0.4005] |
| Reversal fraction range | [0.1469, 0.5511] |
| Mean n_reversals per recording | 44.9 |
| Median n_reversals | 43.0 |

Reversal bout lengths (frames): mean=2.5204  median=2.0000  std=2.2148  p5=0.4000  p95=6.6000  min=0.4000  max=40.6000  n=3,035

---

## 5. Angular Velocity Distribution

Savitzky-Golay filtered head angular velocity (rad/s).

mean=0.0134  median=0.0106  std=0.1684  p5=-0.2606  p95=0.2966  min=-0.9333  max=1.0098  n=109,052

---

## 6. Worm Curvature Distribution

Whole-body curvature summary metric.

mean=0.7146  median=0.6289  std=0.3326  p5=0.3359  p95=1.4347  min=0.0628  max=2.6072  n=109,052

---

## 7. Neuron Coverage

| Metric | All recordings | NeuroPAL recordings only |
|---|---|---|
| Median n_neuron | 138 | 138 |
| Mean n_neuron | 136.8 | 136.4 |
| n_neuron range | [105, 163] | [109, 153] |
| Median trace NaN fraction | 0.0000 | 0.0000 |

Coverage figures: see `results/figures/stage05_neuron_coverage.pdf`

The N_COMMON_NEURONS = 61 subgraph analysis requires only 61 identified neurons
per recording. At median n_neuron = 138, most recordings have substantially
more neurons recorded than the subgraph size. The NaN fraction reflects neurons
that are absent from individual recordings.

---

## 8. Assessment: Roam/Dwell Segmentation Feasibility

Based on descriptive statistics only (no thresholding):

1. **Velocity bimodality (qualitative)**: The velocity_s distribution spans
   roughly [-1.67, 1.71] (5th–95th percentile).
   The median of 0.385 and the forward/backward split seen in
   per-animal KDEs suggest a mixture of locomotion modes. Whether this is
   bimodal requires visual inspection of per-animal KDEs (see figure).

2. **Reversal structure**: Mean reversal fraction = 35.2%,
   suggesting worms spend roughly 35% of recording time in reversals.
   This is behaviorally consistent with interleaved dwelling bouts.

3. **Recording duration**: Median duration = 16.2 min; range
   [15.5, 32.6] min. With W_TRANS_SECONDS = 30 s (6 Hz × 30 = 150 frames)
   transition-exclusion windows, the bulk of each recording (~85% at median
   duration) is available for state analysis.

4. **Candidate threshold location**: The velocity_s distribution is centered
   near 0.385, with a forward-fraction of 61.2%.
   A threshold near velocity_s = 0 (i.e., v = 0 m/s) separates forward from
   backward, but may not capture dwelling/roaming in the classical sense.
   A positive threshold (e.g. velocity_s ≈ 0.1–0.3) may better capture sustained
   roaming. Human decision required — see BEHAV_THRESHOLD human checkpoint.

5. **Data sufficiency**: 40 NeuroPAL-registered recordings with median
   138 neurons is sufficient for the pairwise analysis
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
