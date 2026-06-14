# Phase 4B — Context Note: Available Behavioral Variables
Date: 2026-06-12

---

## Required Context Recovery Summary

### 1. figure_specification_package.md (Phase 2C-A / 2C-A.1)

- **Primary result:** Null result for broad neuropeptide enrichment hypothesis.
- **Exploratory result:** CePNEM-specific Bentley PDF signal, centered on ADEL→URY/URX/RMEL connections during dwelling.
- **Key pairs:** ADEL–URYVR (ΔQ=−0.122, rank 5), ADEL–URYDL (ΔQ=−0.098, rank 9), ADEL–RMEL (ΔQ=−0.096, rank 10).
- **Sign convention:** ΔQ = Q_roam − Q_dwell. Negative ΔQ = dwelling-dominant conditional dependence.
- **PDF pairs (17 nonzero ΔQ):** 14 dwelling-dominant, 3 roaming-dominant.
- **Annotation densities:** PDF 4.6% of Class-4, serotonin 2.5%, neuropeptide 73.6%.

### 2. stage2_results.json (Phase 2, Stage 2)

- 61-neuron subgraph, 1321 Class-4 (off-connectome, both neurons in Creamer subspace) pairs.
- 243 nonzero |ΔQ_cepnem| out of 1321 (18.4%).
- |ΔQ| p95 = 0.041, max = 0.254.
- Ranked pairs stored as upper-triangle indices (np.triu_indices(61, k=1)) sorted by |ΔQ_cepnem| descending.

### 3. phase4a_activity_summary.md (Phase 4A)

- ADEL: no significant state-dependent mean activity change (p=0.87).
- URYVR/URYDL: trend toward higher activity during roaming (p≈0.14–0.19, not significant).
- ADEL–RMEL cross-correlation 2× higher during roaming than dwelling.
- Temporal order at R→D transitions: URYVR leads (1.4s), then ADEL (2.0s), then RMEL (3.8s).
- Phase 2 ΔQ signal is a **conditional precision structure effect**, not visible in simple correlations.

---

## Available Behavioral Encoding Vectors

### Source

CePNEM NL10d model fitted to each recording. Parameters stored in `params_med` field of
per-recording residual `.npz` files (`results/phase1/data/cepnem_residuals/`).

**Parameter layout (0-based, from `src/cepnem_residualize.py`):**

| Index | Name | Description |
|---|---|---|
| 0 | c_vT | Velocity rectification (direction selectivity) |
| 1 | c_v | **Velocity encoding coefficient** |
| 2 | c_θh | Head angle encoding coefficient |
| 3 | c_P | Pumping rate encoding coefficient |

Parameters are posterior medians from MCMC, averaged across epochs within each recording,
then averaged across recordings for each neuron.

### Variables Available

| Variable | Symbol | n_neurons | Biological meaning |
|---|---|---|---|
| Velocity | c_v | 61/61 | Forward/backward locomotion speed; positive = more active during roaming (forward motion) |
| Head angle | c_θh | 61/61 | Head curvature / turning encoding |
| Pumping | c_P | 61/61 | Pharyngeal pumping (feeding behavior); positive = active during feeding (dwelling) |
| Velocity rectification | c_vT | 61/61 | Direction sensitivity (asymmetric velocity response) |

### Dimensionality

- **Scalar analysis:** c_v only (1D). Directly linked to dwelling/roaming state.
- **Vector analysis:** [c_v, c_θh, c_P] (3D). Full behavioral tuning vector.

### Note on Dwelling/Roaming State Encoding

The behavioral state (dwelling vs. roaming) is primarily defined by velocity:
- dwelling = low velocity, often high pumping
- roaming = high velocity, low pumping

Neurons with **c_v > 0** are more active during roaming (velocity-positive, forward-tuned).
Neurons with **c_v < 0** are more active during dwelling (velocity-negative).
Pumping (c_P) provides a complementary axis: c_P > 0 encodes feeding/dwelling activity.

**For Phase 4B:** c_v is the primary alignment variable for testing dwelling/roaming encoding.
The 3D cosine alignment serves as a more comprehensive but less interpretable metric.

### Data Completeness

All 61 neurons observed in at least 1 of the 40 recordings.
Median number of recordings per neuron: see individual neuron data in b1_behavioral_encoding.md.

---

*Note: CePNEM sampled_trace_params (full MCMC posterior of behavioral encoding weights) are NOT
stored in the lite .npz files. The params_med field (posterior median per epoch) is used here.*
