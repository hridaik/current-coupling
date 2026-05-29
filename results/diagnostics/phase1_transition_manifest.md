# Phase 1 Transition Manifest

Date: 2026-05-29
PHASE0_COMPLETE = False         (real-data inference still prohibited)
PHASE0_METHOD_LOCK_COMPLETE = True  (methodology frozen; this document is its record)

This document is the operational handoff package for Phase 1 (real-data inference).
It is designed for a fresh-session start. Do not begin Phase 1 without reading this
document and obtaining explicit human authorization.

---

## 1. Lock Status

| Item | Status |
|---|---|
| Methodology lock | COMPLETE |
| Synthetic feasibility validation | COMPLETE (25/25 tests; TPR≥0.8) |
| Hypothesis text | LOCKED |
| Preprocessing parameters | LOCKED |
| Estimator design | LOCKED |
| Enrichment test design | LOCKED |
| Real-data precision / ΔQ / enrichment | **PROHIBITED** |

---

## 2. Locked Methodological Choices

### Harmonization
| Field | Value |
|---|---|
| LR_POLICY | "separate" |
| IDENTITY_CONFIDENCE_THRESHOLD | 2.5 |
| N_COMMON_NEURONS | 61 |
| N_RANDI_SUBGRAPH_NEURONS | 60 (AWCL excluded from funatlas) |
| N_CREAMER_SUBGRAPH_NEURONS | 56 (AIBL, AIBR, AWCL, IL1L, IL1R absent) |

Three distinct neuron spaces:
- Anatomical: 61 neurons (primary analysis space)
- Randi pair analysis: 60 neurons (AWCL absent from funatlas)
- Creamer/current-velocity bridge: 56 neurons

AWC convention: AWCL/AWCR (anatomical) ≠ AWCON/AWCOFF (functional-state).
No cross-mapping. Two distinct namespaces.

### Randi Pair Definition (Rule A — locked)
| Field | Value |
|---|---|
| RANDI_WT_Q_THRESHOLD | 0.05 |
| RANDI_AMPLITUDE_GATE_DFF | None (excluded from primary) |
| N_RANDI_SUBGRAPH_PAIRS | 189 |

Rule A: q_wt < 0.05 AND occ1_wt > 0 AND occ1_u31 > 0.
Rule B (amplitude gate |dFF|≥0.10) retained for robustness only.

### Behavioral Threshold (locked)
| Field | Value |
|---|---|
| BEHAVIOR_SCORE_SOURCE | "velocity_s" |
| BEHAV_THRESHOLD | 0.284 |
| BEHAV_THRESHOLD_RULE | "pooled_velocity_s_kde_trough_between_dwelling_and_roaming" |
| EWMA_TIMESCALE_SECONDS | 20.0 |
| W_TRANS_SECONDS | 10.0 |
| MIN_BOUT_SECONDS | 10.0 |

Threshold derived from pooled KDE trough only. NOT derived from any neural output.

### Normalization and Missing Data
| Field | Value |
|---|---|
| NORMALIZATION | "z_score_global" |
| MISSING_NEURON_POLICY | "nan_complete_case" |
| SYNAPSE_COUNT_THRESHOLD | 1 |

### Coordinate System
| Field | Value |
|---|---|
| COORD_PRIMARY | "gcamp_trace_array_zscore" (fallback; DEV-004) |
| COORD_ROBUSTNESS_1 | None (CePNEM unavailable) |
| COORD_ROBUSTNESS_2 | None (CePNEM unavailable) |

COORD_INTERP_RULE: "gcamp_trace_array_zscore_only: ΔQ_significant → report as
tentative state-conditional fluorescence structure; behavioral confound unresolved
until CePNEM residual replication."

---

## 3. Frozen Config Values for Future Inference

| Field | Value |
|---|---|
| ESTIMATOR_TIER | "pooled_hierarchical" |
| POOLING_STRATEGY | "pooled" |
| DISCOVERY_ESTIMATOR | "unstructured_stability_selection" |
| CONFIRMATION_ESTIMATOR | "anatomy_guided_lasso" |
| LAMBDA_ON | 0.04 |
| LAMBDA_OFF | 0.45 |
| LAMBDA_OFF_ON_RATIO | 11.25 |
| NFOLDS | 5 (design; actual fold assignments not generated — DEV-005) |
| PRIMARY_ENRICHMENT_STAT | "AUROC" |
| SECONDARY_ENRICHMENT_STAT | "Fisher_topK" |
| NULL_MODEL_PRIMARY | "simple_permutation" |
| ENRICHMENT_POWER_AT_OR2 | 1.0 |
| PRIMARY_TOP_K | 50 |
| D_ROBUSTNESS_RHO | 0.7 |
| NEFF_METHOD | "cross_product_integrated_autocorrelation" |
| NEFF_K_MAX_FRAMES | 200 |
| NONSTATIONARITY_FRACTION | 1.0 (DEV-003; accepted limitation) |
| OUTLIER_ANIMALS | [] (DEV-005; Stage 7 not completed) |
| EXCLUDED_ANIMALS_PRIMARY | [] |

---

## 4. Expected Analysis Regime

### Primary regime (non-roaming)
- ESTIMATOR_TIER: pooled_hierarchical
- Full-matrix pooled estimation (blockwise rejected in Stage 8)
- Stability selection discovery → anatomy-guided lasso confirmation
- Enrichment: AUROC primary, Fisher_topK secondary
- 39/40 NeuroPAL animals with non-roaming data

### Roaming regime (exploratory only)
- Pooled-only (25/40 animals with roaming epochs post-filter)
- T_eff ≈ 25 animals × 40 frames = 1000 frames; TPR=0.90 at effect=0.2
- Fragile: sensitive to further data loss
- Results reported as exploratory

### Current-velocity bridge (D_C ΔQ)
- Conditional on D-robustness go/no-go: Spearman ≥ 0.7 in top-50 pairs
- Restricted to 56-neuron Creamer-compatible subspace
- Creamer: discrete-time, dt=0.5s, max|eig|=0.9966, D_C diagonal posdef
- Omega_C (Frobenius) = 8.6089 (56-neuron subspace)

### Enrichment target
- Off-connectome ΔQ entries (classified against Cook/Witvliet A_raw and Creamer A_C)
- Primary: neuropeptide connectome (Ripoll-Sánchez)
- Secondary: Randi unc-31-sensitive pairs (N=189 in subgraph)
- Null: simple permutation (type-I error calibrated at 0.04)

---

## 5. Validated Estimator Regimes (Stage 8 Synthetic)

| Regime | T | TPR (effect=0.2) | Status |
|---|---|---|---|
| non_roaming_optimistic | 2000 | 1.00 | PASS |
| roaming_optimistic | 420 | 0.80 | PASS |
| non_roaming_middle | 300 | 0.40 | FAIL (underpowered) |
| roaming_middle | 60 | 0.00 | FAIL |
| roaming_conservative | 30 | 0.00 | FAIL |
| pooled_25_animals (T=1000) | — | 0.90 | PASS |

Nonstationarity robustness: TPR 0.80-1.00 across drift fractions 0–100%.
Blockwise estimation: rejected (full-matrix strictly better for cross-block signal).

---

## 6. Prohibited Operations (Still Blocked)

The following must NOT be computed until PHASE0_COMPLETE is set to True by
explicit human authorization:

- State-conditioned precision matrices Q_roam, Q_dwell from real Atanas data
- ΔQ = Q_roam − Q_dwell from real data
- D_C ΔQ (current-velocity bridge) from real data
- Ω_s from real data
- Any enrichment test using real ΔQ as input
- Any current-velocity statistic from real behavioral data
- graphical_lasso_estimate(data_kind="real")
- stability_selection_glasso(data_kind="real")
- anatomy_guided_glasso_admm(data_kind="real")
- estimate_precision(data_kind="real")
- inverse_covariance(data_kind="real")
- compute_delta_q(data_kind="real")

The src/estimators.py guardrail enforces these via RuntimeError.

---

## 7. Remaining Unresolved Limitations

### DEV-003 — NONSTATIONARITY_FRACTION = 1.0
- All 26 assessed animal-state pairs show temporal covariance drift
- Temporal excess over random-split null: median 0.666 (all 26 pairs positive)
- Leading cause: photobleaching (GCaMP6s over 30–60 min recordings)
- Consequence: pooled covariance = time-averaged effective structure (not stationary)
- Required before real-data inference: human explicitly accepts this as a design
  constraint and confirms the interpretation rule for results

### DEV-004 — COORD_PRIMARY = gcamp_trace_array_zscore
- CePNEM residuals (ideal) not locally available (separate Zenodo artifact)
- Behavioral confounds (velocity, curvature, pumping) not removed
- All results tentative; "residual neural organization" interpretation not supported
- Required before real-data inference: human confirms willingness to proceed with
  this coordinate and to interpret results as behavioral-state-conditional fluorescence
  structure (not residual neural structure)

### DEV-005 — Stage 7 not completed
- No inter-animal covariance consistency characterization
- OUTLIER_ANIMALS = [] (no systematic identification)
- CV fold assignments not generated (NFOLDS=5 design only)
- Required before real-data inference: human confirms proceed with all-animal
  pooled strategy without outlier screening, or runs Stage 7 first

---

## 8. Required Future Checkpoints Before Real-Data Inference

Before setting PHASE0_COMPLETE = True, the human must explicitly:

1. Acknowledge DEV-003 (nonstationarity=1.0; photobleaching) and confirm
   interpretation rule: "results represent time-averaged effective coupling
   under confirmed within-recording drift"

2. Acknowledge DEV-004 (gcamp coordinate; behavioral confounds present) and
   confirm interpretation rule: "results are tentative state-conditional
   fluorescence structure pending CePNEM replication"

3. Decide on DEV-005: either run Stage 7 (inter-animal variability) to screen
   outliers and generate CV folds, OR explicitly sign off on all-animal pooling
   without systematic outlier identification

4. After all three decisions: set PHASE0_COMPLETE = True in phase0_config.py
   and record the authorization date and rationale in CHECKPOINT_LOG.md

Only after Step 4 may the guardrail in src/estimators.py be passed with
data_kind="real".

---

## 9. Synthetic Validation Outcomes

All validated with data_kind="synthetic"; test suite: 25/25 pass.

- generate_true_precision_pair: PD, off-connectome ΔQ only ✓
- stability_selection_glasso: BIC alpha, 50-bootstrap, threshold 0.75 ✓
- anatomy_guided_glasso_admm: ADMM with per-entry penalty; convergent PD ✓
- circularity control: high off-connectome penalty → fewer off-connectome selections ✓
- nonstationarity robustness: TPR 0.80–1.00 at drift 0–100% ✓
- pooled multi-animal: TPR=0.90 at 25 animals × 40 frames ✓
- enrichment AUROC power: 1.0 at OR=2 (all regimes) ✓
- null calibration: type-I error 0.04 (simple permutation) ✓

---

## 10. Key File Locations

| Artifact | Path |
|---|---|
| Config | phase0_config.py |
| Hypothesis lock | results/hypothesis_lock.md |
| Final summary | results/diagnostics/phase0_final_summary.md |
| This manifest | results/diagnostics/phase1_transition_manifest.md |
| Locked config snapshot | results/diagnostics/phase0_locked_config_snapshot.json |
| Guardrail source | src/estimators.py |
| Guard tests | tests/test_phase0_guard.py |
| Estimator tests | tests/test_estimators.py |
| n_eff report | results/diagnostics/neff_report.json |
| Deviations | DEVIATIONS.md |
| Checkpoint log | CHECKPOINT_LOG.md |
