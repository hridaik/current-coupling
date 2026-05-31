# Phase 0 Executive Summary

Date archived: 2026-05-29
PHASE0_COMPLETE = False          (real-data inference still prohibited)
PHASE0_METHOD_LOCK_COMPLETE = True  (methodology frozen)

---

## What Phase 0 Accomplished

Phase 0 was a pre-analysis lock program for a C. elegans whole-brain calcium imaging study.
Its purpose was to freeze every methodological decision — subgraph definition, preprocessing
policy, estimator design, enrichment test design, and the primary hypothesis — before any
state-conditioned precision matrix or ΔQ is computed from real behavioral data.

All ten planned stages were addressed (Stage 7 was not fully executed; documented as DEV-005).
41/41 internal consistency checks passed. 27/27 pytest tests pass.

---

## Locked Methodological Choices

### Dataset and subgraph
| Parameter | Value |
|---|---|
| N_COMMON_NEURONS | 61 (NeuroPAL-identified, confidence ≥ 2.5, ≥80% animal coverage) |
| N_RANDI_SUBGRAPH_NEURONS | 60 (AWCL absent from funatlas namespace) |
| N_CREAMER_SUBGRAPH_NEURONS | 56 (AIBL, AIBR, AWCL, IL1L, IL1R absent from Creamer) |
| LR_POLICY | "separate" (bilateral pairs treated as distinct nodes) |
| SYNAPSE_COUNT_THRESHOLD | 1 (primary); 3 (sensitivity) |

### Behavioral threshold
| Parameter | Value |
|---|---|
| BEHAVIOR_SCORE_SOURCE | velocity_s |
| BEHAV_THRESHOLD | 0.284 (pooled KDE trough between dwelling and roaming modes) |
| EWMA_TIMESCALE_SECONDS | 20.0 |
| W_TRANS_SECONDS | 10.0 |
| MIN_BOUT_SECONDS | 10.0 |
| NORMALIZATION | z_score_global |

### Randi pair definition (Rule A)
| Parameter | Value |
|---|---|
| RANDI_WT_Q_THRESHOLD | 0.05 |
| RANDI_AMPLITUDE_GATE_DFF | None (excluded from primary rule) |
| N_RANDI_SUBGRAPH_PAIRS | 189 |

### Estimators
| Parameter | Value |
|---|---|
| ESTIMATOR_TIER | pooled_hierarchical |
| POOLING_STRATEGY | pooled |
| DISCOVERY_ESTIMATOR | unstructured_stability_selection |
| CONFIRMATION_ESTIMATOR | anatomy_guided_lasso |
| LAMBDA_ON | 0.04 |
| LAMBDA_OFF | 0.45 |
| NFOLDS | 5 (design; fold assignments not generated — DEV-005) |

### Enrichment
| Parameter | Value |
|---|---|
| PRIMARY_ENRICHMENT_STAT | AUROC |
| NULL_MODEL_PRIMARY | simple_permutation |
| PRIMARY_TOP_K | 50 |
| ENRICHMENT_POWER_AT_OR2 | 1.0 |
| D_ROBUSTNESS_RHO | 0.7 |

---

## Validated Estimator Regime

Synthetic dry-run (Stage 8) validated the following regimes:

| Regime | T (pooled frames) | TPR (effect=0.2) | Status |
|---|---|---|---|
| Non-roaming optimistic | 2000 | 1.00 | PASS |
| Roaming optimistic | 420 | 0.80 | PASS |
| Pooled 25 animals | 1000 | 0.90 | PASS — matches real roaming scenario |

Real data analysis regime:
- **Non-roaming**: primary (39/40 animals, well-supported)
- **Roaming**: exploratory only (25/40 animals, pooled, fragile)
- **Full-matrix pooled** estimation (blockwise estimation rejected in Stage 8)
- **AUROC** primary enrichment, Fisher_topK secondary

---

## Known Limitations

| ID | Description |
|---|---|
| DEV-003 | NONSTATIONARITY_FRACTION=1.0 — confirmed real temporal covariance drift (likely photobleaching). Results represent time-averaged effective structure, not stationary per-animal precision geometry. |
| DEV-004 | COORD_PRIMARY=gcamp_trace_array_zscore — CePNEM residuals (ideal coordinate) were unavailable at methodology lock time. Behavioral confounds not removed. Results tentative pending CePNEM replication. |
| DEV-005 | Stage 7 (inter-animal variability) not completed. OUTLIER_ANIMALS=[]. CV fold assignments not generated. All-animal pooling strategy used by default. |

These three deviations are the reason PHASE0_COMPLETE remains False. All three must be
explicitly addressed and authorized by human before real-data precision analysis begins.

---

## CePNEM Status

| Item | Status |
|---|---|
| fit_results_lite.jld2.bz2 | Available (1.3 GB compressed) |
| fit_results.jld2 | Available and decompressed (19.55 GB) |
| sampled_trace_params | Directly confirmed present (11, 10001, N, n_epochs) |
| Behavioral encoding params (c_v, c_θh, c_P, c_vT) | Directly accessible in sampled_trace_params[0–3] |
| Precomputed residuals | NOT present — must be computed |
| Timescale parameter (s0) translation | Requires verification (non-trivial reparameterization) |
| Authorized to compute residuals | NO — future checkpoint required |

CePNEM residuals can be computed via the model_nl8 forward equations once authorized.
When available, they will upgrade COORD_PRIMARY from gcamp_trace_array_zscore to
cepnem_residuals, resolving DEV-004.

---

## Guardrail Status

```
PHASE0_COMPLETE = False             ← real-data precision blocked
PHASE0_METHOD_LOCK_COMPLETE = True  ← methodology frozen
```

The guardrail in `src/estimators.py` raises `RuntimeError` for any call with
`data_kind="real"` while `PHASE0_COMPLETE` is False. This covers:
- `estimate_precision`, `inverse_covariance`
- `stability_selection_glasso`, `anatomy_guided_glasso_admm`
- `compute_delta_q`

Synthetic-data calls (`data_kind="synthetic"`) are unaffected.
4/4 guard tests pass as of archival date.

---

## Locked Hypothesis Text

> The top 50 stable off-synaptic ΔQ entries in gcamp_trace_array_zscore (globally
> z-scored GCaMP calcium fluorescence; fallback coordinate — CePNEM residuals
> unavailable) — classified as off-connectome against both raw Cook/Witvliet
> connectome support and Creamer A_C support — are enriched for non-synaptic
> signaling annotations (neuropeptide connectome from Ripoll-Sánchez et al. 2023 or
> Randi unc-31-sensitive relationships from Randi et al. 2023), using simple
> permutation null restricted to the 61-neuron identified subgraph. Estimation uses
> pooled-hierarchical stability selection across all contributing NeuroPAL animals.
> Non-roaming is the primary regime (adequate power); roaming is exploratory (pooled,
> fragile). Covariance estimates represent time-averaged effective structure under
> confirmed within-recording drift (NONSTATIONARITY_FRACTION=1.0).
