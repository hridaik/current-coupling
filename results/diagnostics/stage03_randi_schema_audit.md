# Stage 3 Randi Schema Audit

Date: 2026-05-28

## Scope

Metadata-only HDF5 structure inspection of:

`data/randi/wormneuroatlas/wormneuroatlas/data/funatlas.h5`

No numeric arrays (dFF, q, q_eq, occ1, dFF_all, kernels) were loaded.
No pair statistics, DCV scores, covariance, precision, or enrichment were computed.
No phase0_config.py changes were made.
N_RANDI_SUBGRAPH_PAIRS was not set.

## funatlas.h5 Top-Level Structure

Top-level keys: ['neuron_ids', 'unc31', 'wt']

Top-level attributes:
  'kernels_keys': 'g,factor,power_t,branch'
  'time_compiled': '2023-06-28_19-52-14'

### Scalar fields (safe scalars)

  unc31/q_eq_th                                  1.2
  wt/q_eq_th                                     1.2

### Datasets (shapes and dtypes only — not loaded)

  neuron_ids                                     shape=[300]  dtype=|S5  size≈1,500 bytes
  unc31/dFF                                      shape=[300, 300]  dtype=float64  size≈720,000 bytes
  unc31/dFF_all                                  shape=[300, 300]  dtype=object  size≈variable (object array)
  unc31/kernels                                  shape=[300, 300]  dtype=object  size≈variable (object array)
  unc31/occ1                                     shape=[300, 300]  dtype=int64  size≈720,000 bytes
  unc31/q                                        shape=[300, 300]  dtype=float64  size≈720,000 bytes
  unc31/q_eq                                     shape=[300, 300]  dtype=float64  size≈720,000 bytes
  wt/dFF                                         shape=[300, 300]  dtype=float64  size≈720,000 bytes
  wt/dFF_all                                     shape=[300, 300]  dtype=object  size≈variable (object array)
  wt/kernels                                     shape=[300, 300]  dtype=object  size≈variable (object array)
  wt/occ1                                        shape=[300, 300]  dtype=int64  size≈720,000 bytes
  wt/q                                           shape=[300, 300]  dtype=float64  size≈720,000 bytes
  wt/q_eq                                        shape=[300, 300]  dtype=float64  size≈720,000 bytes

## Neuron Label Inventory

- neuron_ids count: 300
- neuron_ids dtype: |S5  (5-byte fixed-length strings)
- First 10: ['ADAL', 'ADAR', 'ADEL', 'ADER', 'ADFL', 'ADFR', 'ADLL', 'ADLR', 'AFDL', 'AFDR']
- Last 5:   ['VD5', 'VD6', 'VD7', 'VD8', 'VD9']

## AWC Naming Convention

funatlas.h5 stores AWC labels as: ['AWCOF', 'AWCON']
  dtype is |S5 (5-byte fixed string), so 'AWCOFF' is truncated to 'AWCOF'.
  After normalize_neuron_label: ['AWCOF', 'AWCON']
  The common-61 subgraph contains 'AWCL' which does NOT match 'AWCOF' or
  'AWCON'. 'AWCL' is absent from funatlas under its anatomical label.
  Per the approved methodological decision (2026-05-28): AWCL/AWCR
  (anatomical) and AWCON/AWCOFF (functional-state) remain distinct namespaces.
  No mapping is applied.

## Common-61 Subgraph Coverage in funatlas

- Common-61 neurons found in funatlas (exact name, after normalization): 60
- Common-61 neurons NOT found in funatlas: AWCL

The single missing neuron is AWCL. N_COMMON_NEURONS = 61 is retained for
anatomical harmonization. N_RANDI_SUBGRAPH_NEURONS = 60 is the effective
pair-analysis subgraph size. This asymmetry is approved and documented.

## Candidate Pair Datasets

| Dataset          | Shape      | Dtype    | Role                                       | Safe to load later? |
|------------------|------------|----------|--------------------------------------------|---------------------|
| wt/dFF           | (300, 300) | float64  | Mean ΔF/F response (WT)                    | Yes (~720 KB)       |
| unc31/dFF        | (300, 300) | float64  | Mean ΔF/F response (unc-31)                | Yes (~720 KB)       |
| wt/occ1          | (300, 300) | int64    | Observation count (pairs measured in WT)   | Yes (~720 KB)       |
| unc31/occ1       | (300, 300) | int64    | Observation count (pairs measured in unc31)| Yes (~720 KB)       |
| wt/q             | (300, 300) | float64  | Significance q-values (WT)                 | Yes (~720 KB)       |
| unc31/q          | (300, 300) | float64  | Significance q-values (unc-31)             | Yes (~720 KB)       |
| wt/q_eq          | (300, 300) | float64  | Equivalence-test statistic (WT)            | Yes (load; do not use for filtering) |
| unc31/q_eq       | (300, 300) | float64  | Equivalence-test statistic (unc-31)        | Yes (load; do not use for filtering) |
| wt/dFF_all       | (300, 300) | object   | Per-trial ΔF/F (ragged, variable-length)   | **DO NOT LOAD**     |
| unc31/dFF_all    | (300, 300) | object   | Per-trial ΔF/F (ragged, variable-length)   | **DO NOT LOAD**     |
| wt/kernels       | (300, 300) | object   | Response kernel parameters (ragged)        | **DO NOT LOAD**     |
| unc31/kernels    | (300, 300) | object   | Response kernel parameters (ragged)        | **DO NOT LOAD**     |

## q_eq_th Semantics — Approved Treatment

The stored scalars `wt/q_eq_th = 1.2` and `unc31/q_eq_th = 1.2`.
Per human decision (2026-05-28): q_eq_th is NOT approved for filtering use.
It is treated as undocumented/stale metadata unless later justified by
documentation. The q_eq matrix may be loaded for archival purposes but
must not be used as a significance threshold in Stage 3.

## DCV Score Feasibility

`task.md` Stage 3 Task 2 specifies:
  DCV_score(i,j) = WT_response(i,j) - unc31_response(i,j)

WT_response = wt/dFF, unc31_response = unc31/dFF. Both available as dense
float64 matrices. Computation is feasible in the authorized Stage 3 extraction.

## Additional Dependencies

None required beyond h5py (already installed) and numpy.

## Deviations

No deviations.
