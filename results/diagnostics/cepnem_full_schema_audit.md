# CePNEM Full Archive Schema Audit

Date: 2026-05-29
PHASE0_COMPLETE = False  (real-data inference still prohibited)
Stage: metadata/structure inspection only

---

## 1. Artifact Location and Status

```
data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2       4.23 GB (on disk; TRUNCATED)
data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2.bz2  12.38 GB (complete compressed source)
```

**BLOCKER: The JLD2 file is a truncated decompression.**

| Metric | Value |
|---|---|
| Bytes on disk | 4,234,498,048 (~4.23 GB) |
| Expected size (per HDF5 superblock) | 19,546,890,115 (~19.55 GB) |
| Missing | ~15.3 GB |
| Root group address | 19,546,888,935 (last 668 bytes of full file) |
| h5py openable | **NO — truncated file detection at superblock** |

The HDF5 root group (which holds all key/dataset names) is stored at byte 19,546,888,935 of the full file — at the very end. Only 4.23 GB of the 19.55 GB file is present on disk. h5py detects the truncation at the superblock level and refuses to open the file. **The metadata tree cannot be read from the truncated file.**

To use the full archive: complete the decompression of `fit_results.jld2.bz2` (12.38 GB compressed → ~19.55 GB decompressed).

---

## 2. Audit Methodology

Because h5py cannot open the truncated file, this audit uses three converging evidence sources:

1. **HDF5 superblock inspection** — raw binary read of the superblock at offset 512 confirms file identity, version, and stored EOF.
2. **CePNEM Julia source code** — `CePNEMAnalysis.jl/src/data.jl` explicitly shows what fields are populated in `fit_results` for each dataset.
3. **Notebook analysis** — `CePNEM-UMAP.ipynb` states it "requires the full version of `fit_results`"; notebooks access `sampled_trace_params` as the key additional field.
4. **Size arithmetic** — expected `sampled_trace_params` size matches observed full-file size within 5%.

All inferred fields are labelled **SOURCE_CODE_INFERRED** to distinguish from direct file inspection.

---

## 3. HDF5 Superblock (Directly Verified)

| Field | Value |
|---|---|
| JLD2 preamble text | `HDF5-based Julia Data Format, version 0.1.1` |
| HDF5 signature at offset 512 | YES (`\x89HDF\r\n\x1a\n`) |
| Superblock version | 2 |
| offset_size | 8 bytes |
| base_address | 512 |
| stored_eof_addr | 19,546,889,603 |
| root_group_addr | 19,546,888,935 |
| root_group near end of file | YES (last 668 bytes) |

---

## 4. Field Inventory (Source-Code Inferred)

### Fields shared with lite archive (11 fields — identical)

| Field | Python shape | Dtype | Description |
|---|---|---|---|
| `trace_array` | (T, N) | float64 | Z-scored GCaMP (= H5 gcamp/trace_array) |
| `trace_original` | (T, N) | float64 | Raw fluorescence |
| `v` | (T,) | float64 | Velocity covariate |
| `ang_vel` | (T,) | float64 | Angular velocity covariate |
| `θh` | (T,) | float64 | Head angle covariate |
| `P` | (T,) | float64 | Pumping rate covariate |
| `curve` | (T,) | float64 | Body curvature covariate |
| `ranges` | (n_epochs,) struct | structured | Epoch frame boundaries (start, stop) |
| `num_neurons` | scalar | int64 | Number of neurons |
| `avg_timestep` | scalar | float64 | Mean frame duration (s) |
| `sampled_tau_vals` | (10001, N, n_epochs) | float64 | MCMC posterior of τ (EWMA timescale) |

### Fields present ONLY in full archive

#### `sampled_trace_params` ← KEY ADDITION (SOURCE_CODE_INFERRED)

**Python shape: `(11, 10001, N, n_epochs)` — float64**

Source: `CePNEMAnalysis.jl/src/data.jl` lines 47, 73 and `CePNEM.jl/src/model.jl` `get_free_params`.

The 11-parameter MCMC posterior for model NL10d, per neuron, per epoch:

| Index | Parameter | Type |
|---|---|---|
| 1 | `c_vT` | velocity rectification |
| **2** | **`c_v`** | **velocity encoding weight ← behavioral coefficient** |
| **3** | **`c_θh`** | **head curvature encoding weight ← behavioral coefficient** |
| **4** | **`c_P`** | **pumping encoding weight ← behavioral coefficient** |
| 5 | `0` | constant (disabled/zeroed in NL10d) |
| 6 | `y0` | initial neural activity |
| **7** | **`s0`** | **EWMA timescale source (same as sampled_tau_vals)** |
| **8** | **`b`** | **baseline activity** |
| 9 | `ℓ0` | GP residual length scale |
| 10 | `σ0_SE` | GP squared-exponential amplitude |
| 11 | `σ0_noise` | noise amplitude |

This is the critical missing field from the lite archive. With `sampled_trace_params`, CePNEM residuals are computable via a **closed-form model evaluation** (no OLS regression required).

#### Conditional fields (only if `save_raw_params=True`)

| Field | Python shape | Description |
|---|---|---|
| `trace_params` | (11, n_particles, N, n_epochs) | Raw particle filter particles |
| `log_weights` | (n_particles, N, n_epochs) | Log importance weights |
| `trace_scores` | (n_particles, N, n_epochs) | Particle log-likelihoods |
| `log_ml_est` | (N, n_epochs) | Log marginal likelihood per neuron |

Whether these conditional fields are present is unknown until the complete file is readable.

---

## 5. Size Arithmetic

| Quantity | Value |
|---|---|
| `sampled_trace_params` per recording | 11 × 10001 × 138 × 2 × 8 = 0.243 GB (typical N=138, n_epochs=2) |
| `sampled_trace_params` × 68 recordings | ~16.5 GB |
| `sampled_tau_vals` × 68 recordings | ~1.5 GB |
| Other lite fields × 68 recordings | ~0.5 GB |
| **Estimated total full archive** | **~18.5 GB** |
| **Stored EOF (actual header)** | **19.55 GB** |
| Discrepancy | +1 GB — consistent with conditional fields or actual N/n_epochs variation |

**Arithmetic is consistent**: `sampled_trace_params` alone accounts for ~89% of the full archive size increase over lite.

---

## 6. Residual Availability in Full Archive

| Question | Answer |
|---|---|
| Precomputed residuals stored? | **NO** |
| Predicted neural activity stored? | **NO** |
| β coefficients / encoding weights present? | **YES — in `sampled_trace_params` indices 1–4, 8** |
| `sampled_trace_params` present? | **YES (source-code inferred; file truncated)** |
| OLS regression required? | **NO — closed-form model_nl8 formula suffices** |
| Residual computation method | median(sampled_trace_params) → model_nl8 → residual |
| Custom reconstruction still needed? | Yes — but simpler than lite-only approach |
| File currently accessible? | **NO — truncated; bz2 decompression required** |

**Closed-form residual formula (NL10d model):**

```python
# From CePNEM.jl/src/model.jl, model_nl8 (converted to Python)
params = np.median(sampled_trace_params[:, :, neuron, epoch], axis=1)
# params[0]=c_vT, [1]=c_v, [2]=c_θh, [3]=c_P, [4]=0 (disabled), [5]=y0, [6]=s0, [7]=b
c_vT, c_v, c_θh, c_P = params[0], params[1], params[2], params[3]
s0, b = params[6], params[7]
s = compute_s(s0)  # EWMA decay rate
# Per timepoint (vectorizable):
rect = (c_vT + 1) / np.sqrt(c_vT**2 + 1) - 2*c_vT/np.sqrt(c_vT**2 + 1) * (std_v < 0)
predicted = rect * (c_v*std_v + c_θh*std_θh + c_P*std_P) / (s+1) + (activity_prev - b)*s/(s+1) + b
residual = trace_array[:, neuron] - predicted
```

This computation is **not performed in this audit** and requires a future checkpoint authorization.

---

## 7. Lite vs Full Comparison

| Property | Lite archive | Full archive |
|---|---|---|
| Size | 1.85 GB | 19.55 GB (expected; 4.23 GB on disk) |
| Fields | 11 | 11 + sampled_trace_params (+ conditional) |
| β coefficients present | NO | YES (sampled_trace_params) |
| τ posterior present | YES (sampled_tau_vals) | YES (+ derivable from sampled_trace_params) |
| Residual computation | OLS proxy (from τ median) | Closed-form model_nl8 (more accurate) |
| File accessible | Yes (already decompressed) | **NO — truncated** |

**The lite archive (fit_results_lite.jld2) is NOT accessible either** — only the `.bz2` compressed version remains.

---

## 8. Required Action

To make the full CePNEM archive usable:

```bash
# Complete decompression (takes ~10–30 min; produces ~19.5 GB file)
bzip2 -dk data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2.bz2
```

After decompression, a future session should:
1. Verify the complete file with h5py (top-level key check)
2. Confirm `sampled_trace_params` is present and has expected shape
3. Request a checkpoint to implement `compute_cepnem_residuals()` in `src/preprocessing.py`

---

## 9. Deviations

None. No scientific computation performed. No methodological config values modified. File access was limited to superblock binary inspection (512 bytes). All field inventory is source-code inferred and clearly labeled as such.

---

## 10. Output Files

| File | Description |
|---|---|
| `results/diagnostics/cepnem_full_schema_audit.md` | This document |
| `results/diagnostics/cepnem_full_schema_audit.json` | Machine-readable audit report |
| `scripts/stage05_cepnem_full_schema_audit.py` | Audit script |
