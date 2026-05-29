# CePNEM Lite Schema Audit

Date: 2026-05-29
PHASE0_COMPLETE = False  (real-data inference still prohibited)
Stage: metadata/structure inspection only

---

## 1. Artifact Location and Size

```
data/atanas/AtanasKim-Cell2023/cepnem/fit_results_lite.jld2   1.85 GB
data/atanas/AtanasKim-Cell2023/cepnem/fit_results_lite.jld2.bz2   1.3 GB (compressed source)
```

---

## 2. JLD2 / HDF5 Structure

Top-level keys: `_types` (named HDF5 datatypes), `fit_results_lite` (scalar object → Reference)

```
fit_results_lite
  → HDF5 Reference → Dataset (68,) object
      [i] → HDF5 Reference → Pair(first, second)
               first  → string  recording_id  (e.g. '2022-04-12-04')
               second → HDF5 Reference → Dict encoded as object array of 11 Pair(key, value)
```

The JLD2 encoding uses Julia's Pair{String, Dict} structure. Each of the 68 entries corresponds to one recording and decodes to a dictionary of 11 fields.

---

## 3. Per-Recording Field Names

All 68 recordings have **identical field sets** (11 fields):

| Field | Shape | Dtype | Interpretation |
|---|---|---|---|
| `trace_array` | (T, N) | float64 | Z-scored GCaMP traces — **bit-identical to H5 gcamp/trace_array** |
| `trace_original` | (T, N) | float64 | Raw fluorescence traces (mean≈0.6, std≈0.2) |
| `v` | (T,) | float64 | Velocity behavioral covariate |
| `ang_vel` | (T,) | float64 | Angular velocity covariate |
| `θh` | (T,) | float64 | Head angle covariate |
| `P` | (T,) | float64 | Pumping rate covariate |
| `curve` | (T,) | float64 | Body curvature covariate |
| `sampled_tau_vals` | (10001, N, n_epochs) | float64 | MCMC posterior of EWMA timescale τ per neuron/epoch |
| `ranges` | (n_epochs,) | structured (start, stop) | Epoch boundary frame indices |
| `num_neurons` | scalar | int64 | N for this recording |
| `avg_timestep` | scalar | float64 | Mean frame duration (seconds) |

T varies across recordings (1544–1615); N varies (105–163); n_epochs = 2–3.

---

## 4. Recording ID Alignment with Processed H5 Data

| Metric | Value |
|---|---|
| H5 processed files | 68 |
| CePNEM lite entries | 68 |
| Overlap | **68 (PERFECT — 100% alignment)** |
| CePNEM only | 0 |
| H5 only | 0 |

Recording IDs use identical `YYYY-MM-DD-NN` convention in both sources.

---

## 5. trace_array Cross-Check

For recording `'2022-04-12-04'`:
- H5 `gcamp/trace_array` shape: (1600, 151)
- CePNEM `trace_array` shape: (1600, 151)
- Max absolute difference: **0.00 (bit-identical)**

The `trace_array` field in the CePNEM lite artifact is a redundant copy of the H5 z-scored neural data. It is NOT a residualized trace.

---

## 6. Sampling Rate

| Metric | Value |
|---|---|
| CePNEM avg_timestep | ~0.60–0.74 s/frame |
| Derived sampling rate | 1.36–1.66 Hz (median 1.66 Hz) |
| ATANAS_SAMPLING_HZ in config | 5.0 Hz |

**Note:** The config value `ATANAS_SAMPLING_HZ = 5.0` is the raw volumetric acquisition rate from the Atanas 2023 paper methods. The processed H5 files and CePNEM fits use data at ~1.66 Hz. This is an informational finding — no config change is required or performed (this audit is schema-only).

---

## 7. Neuron Indexing Convention

The CePNEM lite artifact contains **no neuron label field**. Neurons are indexed positionally (integer column index in `trace_array`). The column order matches the H5 `gcamp/trace_array` column order for the same recording. Mapping to NeuroPAL names requires the harmonization table from Stage 2 and the JLD2 label file (`dict_neuropal_label.jld2`).

---

## 8. sampled_tau_vals Interpretation

Shape: `(10001, N_neurons, n_epochs)` — 10001 MCMC posterior samples of the EWMA timescale parameter τ_i for each neuron i in each epoch. This is the key CePNEM output in the lite artifact.

Sample τ values for recording 0 (neurons 0–4, epoch 0): `[3.80, 3.86, 41.46, 1.91, 3.64]` seconds.

The wide range (1.9s–41.5s for just 5 neurons) reflects genuine neuron-to-neuron variability in behavioral encoding timescales, consistent with the CePNEM model design.

---

## 9. Residual Availability

### Directly stored: NO

| Field | Present |
|---|---|
| `residuals` / `trace_residual` | **NO** |
| `predicted` (behavior-predicted traces) | **NO** |
| `beta` / `mu` (encoding coefficients) | **NO** |
| `tau_map` / `tau_median` (point estimates of τ) | **NO** |
| `sampled_tau_vals` (MCMC posterior of τ) | YES |
| `trace_array` (z-scored neural input) | YES |
| All 5 behavioral covariates (v, ang_vel, θh, P, curve) | YES |
| Epoch boundaries (ranges) | YES |

### Computable from lite: YES — but requires future checkpoint

CePNEM residuals can be derived from the lite artifact by:

1. **τ̂_i = median(sampled_tau_vals[:, i, epoch])** — posterior median EWMA timescale per neuron per epoch
2. **EWMA_i(t) = behavioral_covariates smoothed at τ̂_i** — per-neuron behavioral feature
3. **β̂_i = OLS(trace_array[:, i], EWMA_i)** — encode behavioral component
4. **ε_i(t) = trace_array[:, i] - β̂_i · EWMA_i(t)** — residual

All required inputs (`sampled_tau_vals`, `trace_array`, `v`, `ang_vel`, `θh`, `P`, `curve`, `ranges`) are present. This computation is **not performed in this audit** and requires a dedicated checkpoint before implementation.

---

## 10. Missing Relative to Full fit_results Archive

The "lite" designation implies a subset of the full CePNEM fit results. Missing fields (inferred from CePNEM model design):

- `beta` / `sampled_beta_vals` — behavioral encoding coefficient posterior
- Precomputed residuals (`trace_residual`)
- Log-likelihood values per neuron per epoch
- Convergence diagnostics (R-hat, ESS)
- Possibly: covariate-specific contribution arrays

The lite artifact provides τ posterior samples and behavioral inputs; the full archive would additionally provide β posterior samples enabling direct residual extraction without recomputation.

---

## 11. Sufficiency Assessment for Future Robustness Analyses

| Question | Answer |
|---|---|
| Residuals directly stored? | **NO** |
| Behavior-predicted component stored? | **NO** |
| Computable from lite? | **YES** (EWMA regression, one checkpoint required) |
| Recording IDs align with H5? | **YES — perfect 68/68** |
| Neuron order matches H5? | **YES — trace_array bit-identical to H5** |
| Behavioral covariates present? | **YES — all 5 (v, ang_vel, θh, P, curve)** |
| τ posterior present? | **YES — 10001 MCMC samples** |
| Epoch structure present? | **YES — ranges array** |

**Assessment:** The lite artifact is **conditionally sufficient** for future CePNEM residual robustness analyses. It contains all computational ingredients, but residuals must be computed via EWMA regression (Step 9 above) rather than read directly. A future session requiring CePNEM residuals must:

1. Obtain human checkpoint authorization for the EWMA regression computation
2. Implement `compute_cepnem_residuals(recording_id, d)` in `src/preprocessing.py`
3. Verify residual quality on a subset before running full 68-recording pipeline
4. NOT use these residuals to inform any locked methodological decision

---

## 12. Deviations

None. This was a metadata-only schema inspection. No scientific computation was performed. No methodological config values were modified.

---

## 13. Output Files

| File | Description |
|---|---|
| `results/diagnostics/cepnem_lite_schema_audit.md` | This document |
| `results/diagnostics/cepnem_lite_schema_audit.json` | Machine-readable field metadata for all 68 recordings |
| `scripts/stage05_cepnem_lite_schema_audit.py` | Audit script (metadata-only) |
