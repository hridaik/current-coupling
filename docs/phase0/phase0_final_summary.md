# Phase 0 Final Summary

Date: 2026-05-29 (methodology lock)
Re-locked: 2026-05-29
PHASE0_COMPLETE = False          ← real-data inference still prohibited
PHASE0_METHOD_LOCK_COMPLETE = True  ← methodology and synthetic validation frozen
Consistency: 41/41 checks passed (methodology lock)

## Re-Lock Notice

PHASE0_COMPLETE was set prematurely and has been restored to False.
Real-data precision / ΔQ / enrichment remain blocked (src/estimators.py guardrail
re-active). PHASE0_METHOD_LOCK_COMPLETE=True records that scientific methodology
is frozen without authorizing real-data inference.

Remaining deviations blocking real-data inference:
- DEV-003: NONSTATIONARITY_FRACTION=1.0; covariance drift confirmed real; cause unresolved
- DEV-004: COORD_PRIMARY=gcamp_trace_array_zscore (CePNEM residuals unavailable)
- DEV-005: Stage 7 not completed; OUTLIER_ANIMALS=[]; CV fold assignments pending

---

## Stage Completion

| Stage | Status | Key Output |
|---|---|---|
| 1 Creamer feasibility | ✓ | A_C stable; D_C available; Ω_C=8.6089 |
| 2 Subgraph | ✓ | N_COMMON_NEURONS=61; 61/60/56 spaces |
| 3 Randi pairs | ✓ | N_RANDI_SUBGRAPH_PAIRS=189 (Rule A) |
| 4 RC check | ✓ | eigenworm-only; Jacobian not viable |
| 5 Threshold + feasibility | ✓ | BEHAV_THRESHOLD=0.284; MIN_BOUT=10s |
| 6 n_eff + stationarity | ✓ | pooled_hierarchical; NONSTATIONARITY=1.0 (confirmed real) |
| 7 Inter-animal variability | ✗ NOT DONE | OUTLIER_ANIMALS=[] (default) |
| 8 Estimator dry-run | ✓ | SS TPR≥0.8; drift-robust; pooled-25 TPR=0.90 |
| 9 Enrichment power | ✓ | AUROC power=1.0 at OR=2; null calibrated |
| 10 Hypothesis lock | ✓ | hypothesis_lock.md; manifest |

---

## Locked Parameters (summary)

- N_COMMON_NEURONS = 61
- BEHAV_THRESHOLD = 0.284
- ESTIMATOR_TIER = 'pooled_hierarchical'
- COORD_PRIMARY = 'gcamp_trace_array_zscore'
- LAMBDA_ON = 0.04 / LAMBDA_OFF = 0.45
- NULL_MODEL_PRIMARY = 'simple_permutation'
- PRIMARY_TOP_K = 50
- D_ROBUSTNESS_RHO = 0.7
- ENRICHMENT_POWER_AT_OR2 = 1.0
- NONSTATIONARITY_FRACTION = 1.0 (DEV-003 accepted)

---

## Deviations

| ID | Description |
|---|---|
| DEV-001 | COVERAGE_FRACTION hardcoded (resolved) |
| DEV-002 | N_COMMON_NEURONS without checkpoint (approved) |
| DEV-003 | NONSTATIONARITY_FRACTION=1.0 accepted; covariance = time-averaged effective structure |
| DEV-004 | COORD_PRIMARY=gcamp_trace_array_zscore (CePNEM unavailable); behavioral confounds unresolved |
| DEV-005 | Stage 7 not completed; OUTLIER_ANIMALS=[]; NFOLDS=5 design only |

---

## Consistency Check Failures

None.

---

## Post-Phase-0 Priority

1. Obtain CePNEM files → rerun in cepnem_residuals coordinate
2. Run Stage 7 inter-animal consistency → OUTLIER_ANIMALS
3. Generate actual CV fold assignments
4. Run real-data ΔQ → enrichment test
5. Check D-robustness criterion (Spearman ≥ 0.7 in top-50)
