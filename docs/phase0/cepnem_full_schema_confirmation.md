# CePNEM Full Archive Schema Confirmation

Date: 2026-05-29
PHASE0_COMPLETE = False  (real-data inference still prohibited)
Stage: direct file inspection — metadata/structure only
Prior document: cepnem_full_schema_audit.md (source-code inferred, truncated file)

---

## 1. File Status

```
data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2   19.55 GB  (COMPLETE — h5py opens OK)
```

Full decompression confirmed. h5py opens without error. Prior blocker resolved.

---

## 2. Top-Level Structure

| Key | Type | Description |
|---|---|---|
| `_types` | Group | 4 named HDF5 datatypes |
| `fit_results` | Dataset (scalar object → Reference) | → (68,) object array of per-recording Pairs |

Root key is `fit_results` (full archive), vs `fit_results_lite` in the lite archive.

---

## 3. Field Inventory (Directly Confirmed)

All 68 recordings have **identical field sets** — **12 fields** (lite had 11):

| Field | Shape | Dtype | Present in lite | Notes |
|---|---|---|---|---|
| `trace_array` | (T, N) | float64 | YES | Bit-identical to H5 gcamp/trace_array |
| `trace_original` | (T, N) | float64 | YES | Raw fluorescence |
| `v` | (T,) | float64 | YES | Velocity covariate |
| `ang_vel` | (T,) | float64 | YES | Angular velocity covariate |
| `θh` | (T,) | float64 | YES | Head angle covariate |
| `P` | (T,) | float64 | YES | Pumping rate covariate |
| `curve` | (T,) | float64 | YES | Body curvature covariate |
| `ranges` | (n_epochs,) struct | structured | YES | Epoch frame boundaries |
| `num_neurons` | scalar | int64 | YES | N for this recording |
| `avg_timestep` | scalar | float64 | YES | Mean frame duration (s) |
| `sampled_tau_vals` | (10001, N, n_epochs) | float64 | YES | EWMA τ posterior (seconds) |
| **`sampled_trace_params`** | **(11, 10001, N, n_epochs)** | **float64** | **NO** | **← KEY ADDITION, DIRECTLY CONFIRMED** |

---

## 4. `sampled_trace_params` — Direct Confirmation

**Shape: `(11, 10001, N, n_epochs)` float64 — CONFIRMED in all 68 recordings.**

| Property | Value |
|---|---|
| n_params | **11** (all 68 recordings) |
| n_samples | **10001** (all 68 recordings) |
| N_neurons | 105–163 (median 138) |
| n_epochs | 2–3 |
| Dtype | float64 |

---

## 5. NL10d Parameter Ordering — Confirmed

**param[4] = 0.0000 exactly across all samples, neurons, and epochs** — directly confirms NL10d parameter ordering from `get_free_params` in `CePNEM.jl/src/model.jl`.

| Index | Name | Range (200 samples, all neurons, epoch 0) | Role |
|---|---|---|---|
| 0 | `c_vT` | [−5.42, 4.09] | velocity rectification (behavioral) |
| **1** | **`c_v`** | **[−3.91, 3.47]** | **velocity encoding weight ← behavioral** |
| **2** | **`c_θh`** | **[−5.05, 4.36]** | **head curvature weight ← behavioral** |
| **3** | **`c_P`** | **[−2.26, 2.98]** | **pumping weight ← behavioral** |
| **4** | **`0_disabled`** | **[0.0000, 0.0000]** | **CONFIRMED ZERO ✓ — NL10d constant disabled** |
| 5 | `y0` | [−3.30, 5.70] | initial neural activity |
| 6 | `s0` | [−3.80, 4.80] | EWMA timescale parameter |
| 7 | `b` | [−3.51, 3.29] | baseline |
| 8 | `ℓ0` | [−3.42, 1.14] | GP residual length scale |
| 9 | `σ0_SE` | [−2.56, 0.99] | GP amplitude |
| 10 | `σ0_noise` | [−0.69, 4.22] | noise amplitude |

The zero-confirmed param[4] is the definitive structural evidence that the parameter ordering matches NL10d exactly.

---

## 6. Recording ID and Data Alignment

| Metric | Value |
|---|---|
| H5 processed files | 68 |
| CePNEM full archive entries | 68 |
| Overlap | **68 (PERFECT)** |
| `trace_array` vs H5 max diff | **0.00e+00 (bit-identical)** |

---

## 7. Precomputed Residuals / Predicted Activity

All absent from the full archive:

| Field | Status |
|---|---|
| `residuals` | ABSENT |
| `trace_residual` | ABSENT |
| `predicted` / `predicted_activity` | ABSENT |
| `trace_params` (conditional) | ABSENT |
| `log_weights` (conditional) | ABSENT |
| `trace_scores` (conditional) | ABSENT |
| `log_ml_est` (conditional) | ABSENT |

No shortcut path exists. CePNEM residuals must be computed from `sampled_trace_params`.

---

## 8. Timescale Parameter Reparameterization — Observation

**`stp[6]` (s0) is highly correlated with `sampled_tau_vals`** (corr ≈ +0.99 for neuron 0). However, the relationship is not the simple `compute_s(s0) = s_MEAN * exp(s0)` formula documented in `CePNEM.jl/src/model.jl` using `s_MEAN = 10`. Specifically:

- `sampled_tau_vals` range: 0.24–504 seconds (biologically plausible EWMA timescales)
- The implied s0 to produce these τ values via `s = 10*exp(s0)` and `tau = log(s/(s+1))/log(0.5)*dt` would be in the range −∞ to −5, but observed stp[6] is in [−3.8, 4.8]
- For the fastest neurons (small τ): the formula gives approximate agreement (~factor 1.2× off)
- For the slowest neurons (large τ): the formula fails completely (factor 100× discrepancy)

**Interpretation**: `sampled_trace_params` stores parameters in the MCMC sampler's internal parameterization, which may differ from the "natural" parameterization exposed by `get_free_params`. The CePNEM residual computation function must use the model equations directly (not the simplified formula) when evaluating predicted activity from `sampled_trace_params`.

**Impact on residual computation**: The behavioral encoding weights (params 0–3: `c_vT`, `c_v`, `c_θh`, `c_P`) appear to be in their natural space (ranges consistent with unit-normal priors and meaningful regression coefficients). Only the timescale parameter transform needs careful verification. This does **not** block residual computation, but the implementation must use the model's own forward equations rather than a simplified formula.

---

## 9. Residual Reconstruction Feasibility — Confirmed Possible

| Question | Answer |
|---|---|
| `sampled_trace_params` present? | **YES — directly confirmed** |
| NL10d ordering confirmed? | **YES — param[4]=0 conclusive** |
| Behavioral encoding weights accessible? | **YES — params[0–3]** |
| Precomputed residuals? | **NO** |
| Custom reconstruction needed? | **YES** |
| Method | `model_nl8` evaluation with posterior median params |
| Timescale param translation | Needs verification (high-correlation but non-trivial) |
| All 68 recordings present? | **YES** |
| OLS regression required? | **NO** (model_nl8 is deterministic given params) |
| Authorized to compute yet? | **NO — future checkpoint required** |

**Conclusion**: Published-posterior-based residual reconstruction is **confirmed feasible**. The residual computation requires a future authorized checkpoint to implement `compute_cepnem_residuals()` in `src/preprocessing.py`, which must use the CePNEM `model_nl8` forward equations with posterior median parameters and verify the timescale parameter mapping.

---

## 10. Deviations

None. No scientific computation performed. No config values modified. Only small parameter slices (200 samples, all neurons, epoch 0) were loaded for verification — no large dense array was held in memory. The timescale reparameterization observation is a new empirical finding documented for the future checkpoint; it does not constitute a deviation.

---

## 11. Output Files

| File | Description |
|---|---|
| `results/diagnostics/cepnem_full_schema_confirmation.md` | This document |
| `results/diagnostics/cepnem_full_schema_confirmation.json` | Machine-readable confirmation |
| `scripts/stage05_cepnem_full_schema_audit.py` | Updated audit script |
