# Stage 5 Preprocessing and Behavioral Metadata Audit

Date: 2026-05-28

## CRITICAL DATA-ACCESS STATUS

Processed H5 files status: **NOT FOUND (BLOCKER)**

  (none)

Processed files required: `{recording_id}-data.h5` for each of the 40 Atanas
recording IDs (e.g. `2022-06-14-01-data.h5`).

Source:
  - Zenodo: https://doi.org/10.5281/zenodo.8150514
  - WormWideWeb: https://wormwideweb.org

Per task.md external-data-access rule:
  "Stop and report the exact missing resource. Record the issue in PROGRESS.md
  and CONTEXT.md. Do not substitute unrelated data."

Stage 5 preprocessing implementation and all behavioral-score KDE plots require
at least one processed H5 file. The human must provide local data access before
Stage 5 can proceed beyond schema documentation.

---

## Scope

Source-code-based schema audit only. No data arrays loaded.

NOT computed:
  - Behavioral thresholds or state labels
  - Covariance, precision, DeltaQ, D_C DeltaQ, Omega_s
  - Stationarity or variability statistics
  - Behavioral segmentation

Source files inspected:
| `data_h5.jl (ANTSUNData)` | present |
| `data_h5.jl (ANTSUNDataJLD2)` | present |
| `FlavellConstants/antsun_data.jl` | present |
| `CePNEM.jl/src/model.jl` | present |
| `behaviors.jl` | present |

---

## 1. Processed HDF5 Schema (from ANTSUNData.jl / ANTSUNDataJLD2.jl)

Each recording produces one `{recording_id}-data.h5` file with three top-level
groups:

### 1.1 Group: `gcamp/` — Neural Activity

| Dataset | Content | Notes |
|---|---|---|
| `traces_array_F_F20` | ΔF/F normalized by F₂₀ (20th-percentile baseline) | Raw fluorescence ratio; not z-scored |
| `trace_array` | Globally z-scored traces | Standardized per-neuron across full recording |
| `trace_array_original` | Pre-z-scoring traces | Raw (before z-score normalization) |
| `idx_splits` | Recording segment indices | [start, end] pairs; for multi-segment recordings |
| `match_org_to_skip` | Neuron index map (original → kept) | For neurons removed during alignment |
| `match_skip_to_org` | Inverse map (kept → original) | — |

Shape convention: `(n_neuron, n_t)` — neurons as rows, time as columns.

`n_neuron` varies per recording (typically 80–140 in freely-moving recordings).
`n_t` varies (at 5 Hz sampling: ~1500–3000 frames per recording based on the
Stage 2 decode report showing median 111 labels per record).

### 1.2 Group: `behavior/` — Behavioral Variables

All behavioral variables are sampled at the confocal volumetric rate (5 Hz).

| Dataset | Content | Units / Notes | Pre-standardized? |
|---|---|---|---|
| `velocity` | Forward locomotion speed | m/s; pre-filtered for stimulation artifacts | YES — filtered by `velocity_filter_threshold=0.2` |
| `reversal_vec` | Binary reversal indicator | 1=reversing, 0=forward/stationary | No |
| `reversal_events` | Reversal start/end index pairs | (n_reversals × 2) int array | No |
| `head_angle` | Head angle (θh) | radians | No (raw) |
| `angular_velocity` | Head angular velocity | rad/s; Savitzky-Golay filtered | YES — smoothed |
| `pumping` | Pharyngeal pump rate | pumps/s (approx) | No |
| `worm_curvature` | Whole-body curvature | Summary curvature metric | No |
| `body_angle` | Body segment angles (relative, first `max_pt-1` segments) | rad | No |
| `body_angle_all` | All body segment angles (relative) | rad; NaN if spline failed | No |
| `body_angle_absolute` | Absolute body segment angles | rad; locally-recentered | No |

**Pre-standardized variables available via `import_data()` with `std_method=:global`:**

The `import_data()` function from ANTSUNData.jl applies global normalization:

| Variable | Standardized name | Global constant | Value |
|---|---|---|---|
| `velocity` | `velocity_s` | `v_STD` | 0.06031 m/s |
| `head_angle` | `θh_s` | `θh_STD` | 0.4943 rad |
| `pumping` | `pumping_s` | `P_STD` | 1.277 pumps/s |

These constants are hard-coded in `FlavellConstants.jl/src/antsun_data.jl` and
are global (shared across all animals). The `velocity_s`, `θh_s`, `pumping_s`
fields are the inputs to the CePNEM encoder model.

### 1.3 Group: `timing/` — Timestamps

| Dataset | Content |
|---|---|
| `timestamp_nir` | NIR behavior camera timestamps (higher-frequency) |
| `timestamp_confocal` | Confocal volumetric-scan timestamps (5 Hz) |
| `stim_begin_confocal` | (optional) stimulation start times, in confocal frames |

### 1.4 Group: `neuropal_registration/` — (optional)

Present only for recordings with NeuroPAL neuron identification.

| Dataset | Content |
|---|---|
| `roi_match_confidence` | Per-ROI NeuroPAL confidence score (scalar per ROI) |
| `roi_match` | ROI-to-neuron-name mapping |

These are the source of the per-recording identity-confidence data used in
Stage 2 (and already accessed via the JLD2 artifact).

---

## 2. CePNEM Model Structure

The CePNEM model (`model_nl7b` / `model_nl8`) decomposes each neuron's calcium
trace into a behavioral encoding component and a residual.

### 2.1 Model inputs (behavioral variables)

| Input | Variable | Standardized by |
|---|---|---|
| Forward velocity | `velocity_s` = `velocity / v_STD` | v_STD = 0.06031 |
| Velocity sign asymmetry | `c_vT` parameter (per neuron) | Fitted |
| Head angle | `θh_s` = `θh / θh_STD` | θh_STD = 0.4943 |
| Pumping | `pumping_s` = `pumping / P_STD` | P_STD = 1.277 |

The velocity term uses a nonlinear rectification: `lesser(v, v_0)` separates
forward (v > v_0) from reverse (v < v_0) encoding. `v_0 = 0` (fixed in
current models).

### 2.2 Model structure (per neuron)

```
y(t) = f(c_v · v_s(t), c_vT, c_θh · θh_s(t), c_P · pumping_s(t), c) / (s+1)
       + (y(t-1) - b) · s / (s+1) + b + noise
```

where:
- `c_vT`: velocity-sign asymmetry coefficient (roaming vs. reversal encoding)
- `c_v`: velocity tuning coefficient
- `c_θh`: head-angle tuning coefficient
- `c_P`: pumping tuning coefficient
- `c`: constant tuning (baseline encoding)
- `s` (= EWMA parameter = `s0`): exponential memory timescale
- `b`: baseline offset

**CePNEM residual** = observed trace - CePNEM predicted activity.

### 2.3 CePNEM EWMA (smoothing) parameter `s`

The parameter `s` in the CePNEM model is an exponentially-weighted moving
average (EWMA) timescale fitted per neuron. It controls how much a neuron's
current activity depends on past behavioral values (memory/integration).

IMPORTANT: `s` is a PER-NEURON fitted parameter, not a global smoothing
applied to the behavioral variable. The EWMA alternative comparison notebook
demonstrates that EWMA-smoothed velocity (a global operation) is a reasonable
proxy for the CePNEM behavioral score, but it is NOT identical to the CePNEM
residual coordinate system.

---

## 3. Candidate Preprocessing Coordinate Systems

### 3.1 COORD_PRIMARY: CePNEM residuals

Definition: `trace_array(t) - CePNEM_prediction(t)` per neuron per timepoint.

**Not directly stored in the processed H5 files.** Requires:
1. Loading `trace_array` from H5
2. Loading CePNEM fit results (posterior mean of `c_v`, `c_vT`, `c_θh`, `c_P`,
   `s`, `b`, `c` per neuron per recording) from Zenodo
   (exact filename pattern requires verification)
3. Computing `CePNEM_prediction(t)` = `model_nl8(...)` with posterior mean params

Status: **feasible but requires two data downloads**: processed H5 AND CePNEM
fit results. The CePNEM fit results may be a separate Zenodo artifact.
Exact filename pattern (e.g. `RECORDING_ID-fit.jld2`) requires verification.

### 3.2 COORD_ROBUSTNESS_1: Processed raw GCaMP

Two candidates in the H5 file:
- `trace_array` — globally z-scored across the full recording; READY to use
- `traces_array_F_F20` — ΔF/F₂₀ (fluorescence ratio); not z-scored

`trace_array` is the more interpretable choice (zero-mean, unit-variance per
neuron). It is the input to the CePNEM model, so it already has consistent
normalization across recordings.

Status: **directly available** from the processed H5 files. No additional
computation required beyond loading the dataset.

### 3.3 COORD_ROBUSTNESS_2: Deconvolved activity

Not stored in the processed H5 files as a pre-computed array. CePNEM provides
"deconvolved activity matrices" (described in the EWMA alternative comparison
notebook as the modeled activity at fixed behavioral values), but these are
not saved in the H5 file and must be recomputed from CePNEM fit results.

The task.md says: "If deconvolution is not available or produces unstable
estimates, omit and record `DECONV_AVAILABLE = False`."

Status: **not pre-stored**; requires CePNEM fit results and non-trivial
recomputation. DECONV_AVAILABLE should remain None until the CePNEM fit
results are available and the computation is assessed.

---

## 4. Candidate Behavioral-State Scoring Variables

**Primary candidate: `velocity`** (forward locomotion speed, m/s)

Rationale:
- Standard in the Atanas/Flavell lab for roaming/dwelling classification
- Roaming = sustained forward locomotion (positive velocity)
- Dwelling = slow/stationary or reversing
- The EWMA notebook validates EWMA-smoothed velocity as the primary score
- `velocity` is already velocity-filtered (stimulation artifact removal)
- Global standardization constant `v_STD = 0.06031` is hard-coded

**CRITICAL constraint (task.md Stage 5):**
The behavioral threshold MUST NOT be derived from any neural covariance,
precision, ΔQ, or enrichment output. It must be set from the behavioral
score distribution alone (KDE, bimodality, trough between modes).

Candidate secondary variables:
- `reversal_vec` — provides discrete reversal events (useful for bout detection)
- `angular_velocity` — head turns; correlated with dwelling
- `worm_curvature` — body curvature; correlated with roaming posture
- `pumping` — pharyngeal; not directly locomotion-related

---

## 5. Missing-Data and Interpolation Structure

From source code (`data_h5.jl` and `behaviors.jl`):

**Neural traces:**
- `match_org_to_skip` and `match_skip_to_org` track neurons removed during
  alignment (those with no identified trace for the full recording). These
  become NaN columns when aligning recordings to a common neuron list.
- Per task.md: `MISSING_NEURON_POLICY = "nan_complete_case"`.

**Behavioral variables:**
- `velocity`: pre-filtered using `filter_velocity(velocity, 0.2)` — stimulation
  artifact windows replaced by interpolation.
- `body_angle_all` / `body_angle_absolute`: NaN-filled at timepoints where the
  worm spline computation crashed (no body curvature computed). These timepoints
  are then interpolated by `interpolate_splines!()` before being saved.
- `angular_velocity`: Savitzky-Golay filtered from head angle.
- No explicit NaN-filling is applied to `velocity`, `pumping`, or `θh` in the
  H5 export path; they should be complete.

---

## 6. Pre-Standardization Summary

| Variable | In H5 | Pre-standardized? | How |
|---|---|---|---|
| Neural traces (`trace_array`) | Yes | YES (z-score) | Global z-score per neuron (mean=0, std=1) |
| `traces_array_F_F20` | Yes | Normalized | ΔF/F₂₀ (not z-scored) |
| `velocity` | Yes | Partially | Stimulation-artifact filtered; raw units m/s |
| `velocity_s` | NO (computed by import_data) | YES | velocity / v_STD (global) |
| `θh` | Yes | No | Raw radians |
| `θh_s` | NO (computed by import_data) | YES | θh / θh_STD (global) |
| `pumping` | Yes | No | Raw |
| `pumping_s` | NO (computed by import_data) | YES | pumping / P_STD (global) |
| `angular_velocity` | Yes | Smoothed | Savitzky-Golay derivative |
| Body angles | Yes | Locally recentered | `local_recenter_angle()` |
| Timestamps | Yes | No | Raw microseconds/seconds |

The `_s` (globally-standardized) versions are computed by `import_data()` at
load time, not stored in the H5 file directly.

---

## 7. Data-Access Requirements for Stage 5 Implementation

| Task | Files needed | Location |
|---|---|---|
| Implement `preprocess_raw_gcamp()` | `{id}-data.h5` (any one recording) | Zenodo 10.5281/zenodo.8150514 |
| Implement `preprocess_cepnem_residuals()` | `{id}-data.h5` + CePNEM fit results | Zenodo (may be separate artifact) |
| Behavioral KDE plots (task.md Stage 5 Task 4-6) | All 40 `{id}-data.h5` files | Zenodo |
| CePNEM DECONV availability check | CePNEM fit results | Zenodo / WormWideWeb |

The exact Zenodo artifact structure (how many files, their names, whether
CePNEM fit results are included) must be verified before downloading.

---

## 8. Config Fields Affected by Stage 5 (not set here)

| Field | Status | Requires |
|---|---|---|
| `COORD_PRIMARY` | None | Human decision after KDE plots |
| `COORD_ROBUSTNESS_1` | None | Human confirmation; `trace_array` is the candidate |
| `COORD_ROBUSTNESS_2` | None | CePNEM fit data availability check |
| `DECONV_AVAILABLE` | None | Requires CePNEM fit results |
| `BEHAVIOR_SCORE_SOURCE` | None | Human decision; `velocity` is candidate |
| `BEHAV_THRESHOLD` | None | Human decision ONLY after KDE plots |
| `BEHAV_THRESHOLD_RULE` | None | With BEHAV_THRESHOLD |
| `MIN_BOUT_SECONDS` | None | After epoch distribution |
| `COORD_INTERP_RULE` | None | Human decision, pre-specified before ΔQ |

---

## 9. Deviations

No deviations. All findings are from source code inspection; no data loaded.
This section will be updated when processed H5 files become available.
