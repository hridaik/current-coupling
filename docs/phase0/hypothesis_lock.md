# Phase 0 Hypothesis Lock Document

Date: 2026-05-29 (methodology lock)
Re-locked: 2026-05-29
PHASE0_COMPLETE = False          ← real-data inference still prohibited
PHASE0_METHOD_LOCK_COMPLETE = True  ← methodology and synthetic validation frozen

## Re-Lock Notice

PHASE0_COMPLETE was set prematurely. Real-data precision / ΔQ / enrichment
analysis must remain blocked until explicit future human authorization.

Three deviations remain unresolved and block real-data inference:
- DEV-003: NONSTATIONARITY_FRACTION=1.0 accepted as limitation; cause unresolved
- DEV-004: COORD_PRIMARY=gcamp_trace_array_zscore (CePNEM unavailable)
- DEV-005: Stage 7 not completed; OUTLIER_ANIMALS=[]; CV folds not generated

What IS complete and frozen:
- All methodological choices (see Sections 4–6)
- Hypothesis text (Section 1)
- Synthetic feasibility validation (TPR≥0.8; 25/25 tests pass)
- Estimator design and enrichment power analysis

---

## 1. Primary Hypothesis

The top 50 stable off-synaptic ΔQ entries in gcamp_trace_array_zscore (globally z-scored GCaMP calcium fluorescence; fallback coordinate — CePNEM residuals unavailable) — classified as off-connectome against both raw Cook/Witvliet connectome support and Creamer A_C support — are enriched for non-synaptic signaling annotations (neuropeptide connectome from Ripoll-Sánchez et al. 2023 or Randi unc-31-sensitive relationships from Randi et al. 2023), using simple permutation null restricted to the 61-neuron identified subgraph. Estimation uses pooled-hierarchical stability selection across all contributing NeuroPAL animals. Non-roaming is the primary regime (adequate power); roaming is exploratory (pooled, fragile). Covariance estimates represent time-averaged effective structure under confirmed within-recording drift (NONSTATIONARITY_FRACTION=1.0).

**Target object**: stable pooled regime-supported structure (connectivity topology
and enrichment signatures), NOT exact stationary per-animal precision geometry.

**Coordinate system**: gcamp_trace_array_zscore
  - Fallback coordinate (CePNEM residuals unavailable; see Section 9 Limitation 1)
  - Behavioral confound contribution present; results are tentative

**Subgraph**: 61-neuron NeuroPAL-identified subgraph
  - Three spaces: anatomical (61), Randi (60), Creamer (56)
  - PRIMARY_TOP_K=50 ≤ 1830 = N×(N-1)/2 ✓

---

## 2. D-Robustness Go/No-Go Criterion

Candidate rankings under D_C (Creamer process-noise covariance), residual
diagonal D, and identity I must share a Spearman correlation ≥ 0.7
in the top-50 pairs.

If ρ_Spearman < 0.7: D_C ΔQ reported as inconclusive;
the main claim rests on ΔQ alone.

D_ROBUSTNESS_RHO = 0.7

---

## 3. Coordinate Interpretation Rule

gcamp_trace_array_zscore_only: ΔQ_significant → report as tentative state-conditional fluorescence structure; behavioral confound unresolved until CePNEM residual replication.

---

## 4. Locked Preprocessing Parameters

| Parameter | Value |
|---|---|
| BEHAVIOR_SCORE_SOURCE | velocity_s |
| BEHAV_THRESHOLD | 0.284 |
| BEHAV_THRESHOLD_RULE | pooled_velocity_s_kde_trough_between_dwelling_and_roaming |
| EWMA_TIMESCALE_SECONDS | 20.0 |
| W_TRANS_SECONDS | 10.0 |
| MIN_BOUT_SECONDS | 10.0 |
| LR_POLICY | separate |
| IDENTITY_CONFIDENCE_THRESHOLD | 2.5 |
| NORMALIZATION | z_score_global |
| MISSING_NEURON_POLICY | nan_complete_case |
| SYNAPSE_COUNT_THRESHOLD | 1 |
| RANDI_WT_Q_THRESHOLD | 0.05 |

---

## 5. Locked Estimation Parameters

| Parameter | Value |
|---|---|
| DISCOVERY_ESTIMATOR | unstructured_stability_selection |
| CONFIRMATION_ESTIMATOR | anatomy_guided_lasso |
| LAMBDA_ON | 0.04 |
| LAMBDA_OFF | 0.45 |
| LAMBDA_OFF_ON_RATIO | 11.25 |
| ESTIMATOR_TIER | pooled_hierarchical |
| POOLING_STRATEGY | pooled |
| STABILITY_THRESHOLD | 0.75 |
| NFOLDS | 5 (design; actual assignments not generated) |

---

## 6. Locked Enrichment Parameters

| Parameter | Value |
|---|---|
| PRIMARY_ENRICHMENT_STAT | AUROC |
| SECONDARY_ENRICHMENT_STAT | Fisher_topK |
| NULL_MODEL_PRIMARY | simple_permutation |
| PRIMARY_TOP_K | 50 |
| ENRICHMENT_POWER_AT_OR2 | 1.0 |
| D_ROBUSTNESS_RHO | 0.7 |

---

## 7. Pre-Specified Secondary Analyses

1. **D_C ΔQ (current-velocity bridge)** — conditional on D-robustness go/no-go.
2. **Ω_C comparison** — departure from Creamer synapse-only model. Exploratory.
3. **Sign-specific tests** — positive vs. negative ΔQ entries separately.
4. **Homolog symmetrization sensitivity** — LR_POLICY="separate" vs collapsed.
5. **Randi unc-31-sensitive validation** — secondary enrichment (N_RANDI_SUBGRAPH_PAIRS=189).
6. **CePNEM replication** — if fit files become available post-Phase-0, repeat in COORD_PRIMARY=cepnem_residuals.

No other secondary analyses may be added post-hoc.

---

## 8. Analysis Classification

| Analysis | Classification |
|---|---|
| Off-connectome ΔQ enrichment (non-roaming) | **Validated** — adequate power; well-supported |
| Off-connectome ΔQ enrichment (roaming pooled) | **Exploratory** — pooled-only; fragile |
| D_C ΔQ current-velocity bridge | **Exploratory** — conditional on D-robustness |
| Ω_C comparison | **Exploratory** — preparation mismatch |
| CePNEM residual analysis | **Unsupported** — deferred (files unavailable) |
| Per-animal precision estimation | **Unsupported** — n_eff insufficient |
| Blockwise estimation | **Unsupported** — Stage 8 shows no benefit |

---

## 9. Known Limitations

1. **Coordinate system**: COORD_PRIMARY = gcamp_trace_array_zscore (z-scored raw GCaMP).
   CePNEM residuals (ideal) unavailable. Behavioral confounds not removed.
   All results tentative pending CePNEM replication.

2. **Nonstationarity**: NONSTATIONARITY_FRACTION = 1.0. First/second-half covariance
   drift confirmed real (excess 0.666 vs null). Covariance = time-averaged effective
   structure under drift. Likely cause: photobleaching. Accepted as DEV-003.

3. **Roaming support**: 25/40 animals; median 8s/animal. Pooled TPR=0.90 at T=1000.
   Marginal — sensitive to further data loss. Exploratory regime only.

4. **Stage 7 not completed**: No inter-animal consistency characterization.
   OUTLIER_ANIMALS=[]; CV fold assignments not generated.

5. **Single coordinate**: No COORD_ROBUSTNESS_1/2 available. All robustness
   evidence is synthetic; no real-data coordinate robustness established.
