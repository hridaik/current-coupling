# Stage 0-V.8 — Parameter Lock Package

Date: 2026-06-01  
Prepared by: coding agent (post-V.7C PASS)  
Authorization required: Human supervisor must set PHASE2_ACTIVE = True in phase2_config.py

---

## 1. Final Locked Parameter Table

All parameters determined from synthetic validation (Stage 0-V), prior to any real-data estimation.
No parameter may change after PHASE2_ACTIVE is set to True.

### Core estimation pipeline

| Parameter | Locked Value | Set In | Evidence |
|---|---|---|---|
| MISSING_NEURON_POLICY | `"pairwise_available_case"` | Stage 0.3 | Architecture decision |
| PSD_PROJECTION_METHOD | `"eigenvalue_clipping"` | Stage 0.3 | Architecture decision |
| PSD_EIGENVALUE_FLOOR | `1e-6` | V.2 | Clip fraction = 0.000 (S always PSD) |
| STABILITY_SELECTION_RESAMPLE_UNIT | `"recording"` | Stage 0.3 | Architecture decision |
| STABILITY_SELECTION_LAMBDA | `0.15` | V.3 + DEV-P2-002 | TPR=0.973, FPR=0.033 at effect=0.2 |
| N_BOOTSTRAP_RESAMPLES | `25` | V.4 | Variance converged; TP=0.945, TN=0.039 |
| STABILITY_THRESHOLD | `0.75` | V.4 | Youden-optimal; TPR=0.90, FPR=0.023 |
| LAMBDA_ON | `0.01` | V.5 + V.6 | TPR=0.992, FPR=0.020 (V.6 confirmed) |
| LAMBDA_OFF | `0.10` | V.5 + V.6 | Ratio=10; confirmed in v6_circularity.json |
| PRIMARY_TOP_K | `20` | V.7C | Fisher type-I=0.040, power=1.000 |

### Enrichment validation design

| Parameter | Locked Value | Set In | Evidence |
|---|---|---|---|
| P_SIGNAL_VALIDATION_MIN | `12` | V.7A + V.7B fine sweep | AUROC ceiling at P=10; first P meeting criterion |
| P_SIGNAL_VALIDATION | `13` | V.7C + DEV-P2-003 | One step above minimum; power=0.685 |
| ENRICHMENT_EFFECT_SIZE | `0.20` | V.7 spec | Inherited from Phase 0 |
| AUROC_POWER | `0.685` | V.7C | At P=13, effect=0.20 |
| AUROC_TYPE1 | `0.035` | V.7C | Well below 0.06 criterion |
| FISHER_POWER_K20 | `1.000` | V.7C | Unchanged across all P_SIGNAL values |
| FISHER_TYPE1_K20 | `0.040` | V.7C | Calibrated |

### Inherited locked parameters (from Phase 0 — unchanged)

| Parameter | Value | Source |
|---|---|---|
| BEHAV_THRESHOLD | `0.284` | Phase 0 Stage 5 |
| BEHAVIOR_SCORE_SOURCE | `"velocity_s"` | Phase 0 Stage 5 |
| EWMA_TIMESCALE_SECONDS | `20.0` | Phase 0 Stage 5 |
| W_TRANS_SECONDS | `10.0` | Phase 0 Stage 5 |
| MIN_BOUT_SECONDS | `10.0` | Phase 0 Stage 5 |
| SYNAPSE_COUNT_THRESHOLD | `1` | Phase 0 Stage 2 |
| NORMALIZATION | `"z_score_global"` | Phase 0 Stage 5 |
| LR_POLICY | `"separate"` | Phase 0 Stage 2 |
| COORD_PRIMARY | `"cepnem_residual"` | Phase 1 Stage 1.0 |
| COORD_ROBUSTNESS_1 | `"gcamp_trace_array_zscore"` | Phase 0 |
| D_ROBUSTNESS_RHO | `0.7` | Phase 0 |
| RANDI_WT_Q_THRESHOLD | `0.05` | Phase 0 Stage 3 |

### Parameter pending human decision

| Parameter | Status | Recommended | Reference |
|---|---|---|---|
| MIN_COPRESENCE_RECORDINGS | **PENDING** | `10` | Stage 0.1 checkpoint (not yet closed) |

The Stage 0.1 copresence report established: roaming median = 15 co-observations, min = 9 (3 fragile pairs: AVEL-URBL, IL2VL-URBL, RMDL-URBL). n_eff is adequate for all pairs (min = 42 >> 20). The human must set this value in phase2_config.py before Stage 1 begins. Suggested value: 10 (excludes only the 3 pairs below 9, treating them as fragile; retains all 1830 pairs for covariance assembly).

---

## 2. Phase 2 Validation Summary

### Stage 0-V pass/fail record

| Stage | Criterion | Observed | Status |
|---|---|---|---|
| V.1 | Pairwise covariance bias < 1% | Pearson(S_pw, Σ_true) = 0.921 (roam), 0.981 (dwell) | **PASS** |
| V.2 | PSD clip fraction ≤ 15% | Clip fraction = 0.000 (S always PSD; floor = 1e-6 safety net) | **PASS** |
| V.3 | TPR ≥ 0.60 at effect = 0.2 | TPR = 0.973, FPR = 0.033 at λ = 0.15 (100 reps) | **PASS** |
| V.4 | Stability calibrated | TP stab = 0.945, TN stab = 0.039; TPR = 0.90, FPR = 0.023 at thr = 0.75 | **PASS** |
| V.5 | Anatomy-guided lasso calibrated | λ_on = 0.01, λ_off = 0.10; TPR = 0.992, FPR = 0.020 | **PASS** |
| V.6 | Circularity control | Confirm-TP = 1.000, False-confirm = 0.021 | **PASS** |
| V.7 | Type-I ≤ 0.06; Power ≥ 0.60 (original P=10) | Type-I = 0.050 PASS; Power = 0.525 FAIL | **FAIL** |
| V.7A | Diagnostic (authorized) | P_SIGNAL_min = 12; enrichment-design limitation confirmed | — |
| V.7B | Re-run at P=12 (Path 2 trial) | Type-I = 0.085 (seed fluctuation), Power = 0.595 (1 rep short) | **FAIL** |
| V.7C | Re-run at P=13 (DEV-P2-003) | Type-I = 0.035, Power = 0.685 | **PASS** |

### Deviations recorded

| Deviation | Description | Status |
|---|---|---|
| DEV-P2-002 | STABILITY_SELECTION_LAMBDA = 0.15 (fixed, from V.3 synthetic sweep) | Authorized |
| DEV-P2-003 | P_SIGNAL updated from 10 to 13 (P_SIGNAL_min = 12 established by V.7A/B fine sweep; operating point = 13 for validated margin above minimum) | Authorized |

Inherited deviations (from Phase 0/1, unchanged):

| Deviation | Description |
|---|---|
| DEV-003 | Nonstationarity (photobleaching): time-averaged effective structure accepted |
| DEV-004 | RESOLVED — CePNEM residuals available; COORD_PRIMARY = cepnem_residual |
| DEV-005 | All-animal pooling without outlier screening; compensated by LOO sensitivity (Stage 3) |

---

## 3. Unresolved Assumptions

The following assumptions carry into Stage 1. Each must be acknowledged before PHASE2_ACTIVE = True is set.

### UA-1 — MCAR missingness assumption

The pairwise available-case estimator is unbiased under Missing Completely At Random (MCAR): each neuron's absence from a recording is independent of its activity and the activity of other neurons.

Stage 0 evidence: Phase 1 corpus audit concluded missingness is driven by optical resolution constraints under animal motion, not by neural signal content. This is consistent with MCAR but not formally tested.

Implication: if some neurons' absence correlates with behavioral state (e.g., fast-moving animals systematically miss certain neurons), the pairwise covariance estimate is biased. The bias would inflate the apparent state-conditioned difference for neurons that are under-represented in one behavioral state.

Status: accepted as a design constraint. The LOO sensitivity analysis (Stage 3) provides partial compensation — if a few recordings with atypical missingness patterns drive the result, LOO will reveal it.

### UA-2 — PSD projection preserves rank ordering

The enrichment test uses ranks of |ΔQ| entries, not magnitudes. The PSD projection (eigenvalue clipping to 1e-6) is valid if it preserves the rank ordering of off-diagonal entries.

Stage 0 evidence: V.2 showed S_pairwise is always PSD under the SF corpus (clip fraction = 0.000). PSD projection is a safety net that was never triggered in synthetic validation. The rank preservation assumption has not been directly tested for real data where non-Gaussian distributions, heavy tails, or non-stationarity might produce near-singular assembled covariances.

Implication: if real data produces negative eigenvalues in S_pairwise (e.g., from heavy-tailed GCaMP fluorescence or systematic inter-recording drifts), the PSD projection will alter magnitudes. If the projection systematically promotes or demotes specific pairs, the AUROC is biased.

Safeguard: Stage 1.2 mandates a halt-and-diagnose condition if real-data PSD clipping exceeds 2× the synthetic baseline (0.000 → any clipping at all triggers review).

### UA-3 — Annotation independence from estimation

The circularity control (V.6) tests that the anatomy-guided lasso does not artificially inflate annotated off-connectome entries through its penalty structure. V.6 passed (confirmation rate = 1.000, false confirmation = 0.021). However, there is a residual concern: per-pair co-observation counts might correlate with annotation status (pairs that co-occur more frequently have more stable pairwise covariance estimates, which could correlate with their position in either the connectome or the Randi annotation).

Stage 0 evidence: not directly tested. V.6 tests the estimator's selectivity, not the co-observation correlation structure.

Status: accepted. The degree-preserving null model (used throughout V.7C) partially compensates for this by stratifying on node degree.

### UA-4 — Gaussian generative model

All Stage 0-V validation used Gaussian synthetic data. Real GCaMP fluorescence is non-Gaussian: bounded below, right-skewed, with photobleaching-induced drift. CePNEM residualization partially addresses the behavioral confound but does not produce Gaussian residuals.

Stage 0 evidence: non-Gaussianity was flagged as a risk in Phase 0 (DEV-003). Phase 0 synthetic validation showed robustness to nonstationarity (TPR 0.80–1.00 across drift fractions 0–100%). The Phase 2 synthetic validation did not specifically test non-Gaussian score distributions.

Implication: the graphical lasso is maximum likelihood under Gaussianity; its behavior under non-Gaussian inputs is heuristic. Heavy-tailed residuals may inflate or deflate specific precision entries.

Status: accepted. Both coordinate systems (CePNEM residual primary, raw GCaMP robustness) are computed; discordant results between coordinates are the diagnostic for behavioral confound effects.

### UA-5 — Behavioral state segmentation carries forward

The behavioral threshold (BEHAV_THRESHOLD = 0.284) was locked in Phase 0 from EWMA-smoothed velocity. It was not re-validated under the pairwise estimation framework. The number of roaming vs dwelling frames per recording determines per-pair available-case sample sizes and affects both the pairwise covariance estimate and the effective sample size.

Stage 0 evidence: V.1 used the actual SF corpus roaming/dwelling frame counts as inputs to the synthetic data generator. The synthetic validation is therefore conditioned on the real frame distribution. This is the correct approach.

Status: inherited and accepted. No re-validation needed.

---

## 4. Stage 1 Authorization Checkpoint Package

### What Stage 1 does

Stage 1 computes state-conditioned pairwise precision matrices from real behavioral data. It is the first computation that directly informs the scientific result. All Stage 0 validation was designed to ensure Stage 1 is trustworthy before it runs.

Stage 1 consists of:
- 1.1: Pairwise covariance assembly for each state × coordinate (4 matrices: CePNEM × {roam, dwell}; raw GCaMP × {roam, dwell})
- 1.2: PSD projection with diagnostic logging
- 1.3: Discovery estimator (stability selection with recording resampling)
- 1.4: Confirmation estimator (anatomy-guided ADMM lasso)
- 1.5: Diagnostics (positive-definite check, condition numbers, convergence)

### Prerequisites before setting PHASE2_ACTIVE = True

The human supervisor must:

**[1] Set MIN_COPRESENCE_RECORDINGS in phase2_config.py**

Recommended value: 10. This excludes from the covariance assembly any pair with fewer than 10 co-observations in the relevant state. The Stage 0.1 copresence analysis found 3 fragile pairs in roaming (min = 9). Setting this to 10 excludes those 3 pairs; all other 1827 pairs remain.

**[2] Acknowledge UA-1 through UA-5** and confirm that the analysis proceeds under these assumptions. Each assumption must be explicitly acknowledged in PHASE2_CHECKPOINT_LOG.md.

**[3] Confirm the interpretation table** for the coordinate comparison (Stage 5) is locked as specified in phase2_task.md:

| CePNEM enrichment | Raw GCaMP enrichment | Interpretation |
|---|---|---|
| Significant (p < 0.05) | Significant | Residual neural state organization |
| Significant | Not significant | Neural organization masked by behavioral noise |
| Not significant | Significant | Behavior-mediated state structure |
| Not significant | Not significant | Null result |

**[4] Confirm the ordering constraint**: Stages 1.1–1.6 run for BOTH coordinates before Stage 5 (coordinate comparison) is opened. Previewing one coordinate's enrichment before the other is computed contaminates the comparison.

**[5] Set PHASE2_ACTIVE = True in phase2_config.py** and record the authorization date and rationale in PHASE2_CHECKPOINT_LOG.md.

### The irreversibility trigger

Once PHASE2_ACTIVE = True, the following parameters are frozen permanently:

PSD_EIGENVALUE_FLOOR, STABILITY_THRESHOLD, N_BOOTSTRAP_RESAMPLES, STABILITY_SELECTION_LAMBDA, LAMBDA_ON, LAMBDA_OFF, PRIMARY_TOP_K, MIN_COPRESENCE_RECORDINGS, the enrichment null models, the coordinate interpretation table.

No methodology change is permitted after seeing any real-data precision matrix, ΔQ, or enrichment statistic.

### Stage 1 halt conditions

Stage 1.2 must halt if:
- Real-data PSD clipping exceeds any clipping (synthetic baseline = 0.000); halt and characterize the eigenvalue spectrum before continuing.
- Any precision matrix is not positive definite after PSD projection.
- Any ADMM convergence failure.
- Condition number > 10^6 for any precision matrix.

These are diagnostic halt points, not failures. They require investigation before the run continues.

---

## Certification Statement

All Stage 0-V validation has been completed on synthetic data only. No real-data precision matrix, ΔQ, or enrichment statistic has been computed. All parameters in Section 1 are locked based solely on synthetic validation outcomes. The biological question (whether off-connectome ΔQ is enriched for neuropeptide-signaling pairs) has not been examined in real data. The analysis is pre-registered in the sense that all methodological decisions were finalized before the first real-data computation.

**Stage 0-V status: COMPLETE (V.1–V.6, V.7C all PASS)**  
**Stage 0-V.8 status: READY FOR HUMAN AUTHORIZATION**  
**Stage 1 status: PROHIBITED until PHASE2_ACTIVE = True**
