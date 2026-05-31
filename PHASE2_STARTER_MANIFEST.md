# PHASE2_STARTER_MANIFEST.md
## What Carries Forward, What Does Not, What Must Be Re-established

Date: 2026-05-31
Status: Phase 2 initialized — Stage 0 not yet authorized

---

## 1. Why Phase 2 Exists

Phase 1 discovered that the complete-case estimation pipeline (validated in Phase 0 Stage 8)
requires a dense T × 61 pooled data matrix that does not exist in the SF freely-behaving
corpus. Per-animal neuron identification produces ~55–61 of the 61-neuron subgraph per
recording, but each recording is missing a different random subset. The complete-case
intersection across ≥19 roaming recordings collapses to 4–13 neurons. The corpus-wide audit
confirmed this is a field-wide limitation of NeuroPAL confocal imaging under free behavior,
not a property of the specific 40-animal dataset.

Phase 2 replaces the estimation object: from complete-case data matrix to pairwise
available-case covariance assembly with PSD projection. The biological question, the
enrichment framework, and all behavioral segmentation parameters are unchanged.

---

## 2. Assets That Carry Forward Unchanged

### Data products (read from disk, do not recompute)

| Asset | Location | Status |
|---|---|---|
| Neuron harmonization table | results/diagnostics/neuron_harmonization.csv | Complete |
| Connectome matrices A_raw, A_gj, A_chem, A_peptide | results/diagnostics/ | Complete, 61×61 |
| Randi DCV-sensitive pair list | results/diagnostics/randi_dcv_pairs.csv | 189 pairs |
| Creamer A_C, D_C, Ω_C | results/diagnostics/ | 56-neuron subspace |
| CePNEM residualized traces | results/phase1/data/cepnem_residuals/ | All animals × subgraph |
| Behavioral epoch segmentation | (recompute from locked parameters) | Locked parameters |
| Co-observation structure | (to be computed in Stage 0.1) | Not yet available |

### Locked parameters (in phase0_config.py — do not modify)

| Parameter | Value | Source |
|---|---|---|
| BEHAV_THRESHOLD | 0.284 | Phase 0 Stage 5 |
| BEHAVIOR_SCORE_SOURCE | velocity_s | Phase 0 Stage 5 |
| EWMA_TIMESCALE_SECONDS | 20.0 | Phase 0 Stage 5 |
| W_TRANS_SECONDS | 10.0 | Phase 0 Stage 5 |
| MIN_BOUT_SECONDS | 10.0 | Phase 0 Stage 5 |
| SYNAPSE_COUNT_THRESHOLD | 1 | Phase 0 Stage 2 |
| NORMALIZATION | z_score_global | Phase 0 Stage 5 |
| LR_POLICY | separate | Phase 0 Stage 2 |
| COORD_PRIMARY | cepnem_residual | Phase 1 Stage 1.0 |
| COORD_ROBUSTNESS_1 | gcamp_trace_array_zscore | Phase 0 |

### Code modules (usable without modification)

| Module | Purpose |
|---|---|
| src/data_access.py | Load Atanas, Creamer, connectome, Randi data |
| src/harmonization.py | Neuron name mapping |
| src/preprocessing.py | CePNEM residuals, normalization, epoch segmentation |
| src/cepnem_residualize.py | CePNEM model evaluation |
| src/enrichment.py | AUROC, Fisher, enrichment statistics |
| src/null_models.py | Degree-preserving permutation |
| src/power_analysis.py | Enrichment power simulation |
| src/neff.py | Autocorrelation and effective sample size |

### Standing deviations

| Deviation | Status | Implication for Phase 2 |
|---|---|---|
| DEV-003 (nonstationarity) | Accepted | Time-averaged effective structure; unchanged |
| DEV-004 (CePNEM coordinate) | Resolved | CePNEM is primary coordinate |
| DEV-005 (all-animal pooling) | Carries forward | LOO sensitivity compensates |

---

## 3. What Does NOT Carry Forward

### Estimation pipeline (replaced entirely)

| Phase 0/1 Component | Phase 2 Replacement | Reason |
|---|---|---|
| Complete-case pooled array | Pairwise available-case covariance | Intersection collapse |
| np.cov(X_pooled) | Pairwise assembly + PSD projection | Different statistical object |
| stability_selection_glasso() | Recording-resampled pairwise stability selection | Different resampling unit |
| anatomy_guided_glasso_admm() | ADMM on PSD-projected pairwise S | Different input object |
| Phase 0 Stage 8 validation | Phase 2 Stage 0-V validation | Must re-validate for new estimator |

### Parameters (must be re-established)

| Parameter | Phase 0/1 Value | Phase 2 Status |
|---|---|---|
| MISSING_NEURON_POLICY | nan_complete_case | → pairwise_available_case |
| DISCOVERY_ESTIMATOR | unstructured_stability_selection | → pairwise_stability_selection |
| CONFIRMATION_ESTIMATOR | anatomy_guided_lasso | → pairwise_anatomy_guided_lasso |
| LAMBDA_ON | 0.04 | Re-calibrate in Stage 0-V |
| LAMBDA_OFF | 0.45 | Re-calibrate in Stage 0-V |
| PRIMARY_TOP_K | 50 | Re-calibrate in Stage 0-V |
| ESTIMATOR_TIER | pooled_hierarchical | Re-determine in Stage 0-V |
| N_BOOTSTRAP_RESAMPLES | (was 50) | Re-calibrate in Stage 0-V |
| STABILITY_THRESHOLD | (was 0.75) | Re-calibrate in Stage 0-V |

### New parameters (Phase 2 only)

| Parameter | Initial Value | Set In |
|---|---|---|
| PSD_EIGENVALUE_FLOOR | None | Stage 0-V.2 |
| PSD_PROJECTION_METHOD | None | Stage 0.3 |
| STABILITY_SELECTION_RESAMPLE_UNIT | "recording" (proposed) | Stage 0.3 |
| MIN_COPRESENCE_RECORDINGS | None | Stage 0.1 |

---

## 4. The Validation Break

Phase 0 validated:
```
generate_synthetic_complete_data() → np.cov() → GraphicalLasso → ΔQ → enrichment
```

Phase 2 must validate:
```
generate_synthetic_pairwise_data() → assemble_pairwise_S() → PSD_project() → ADMM → ΔQ → enrichment
```

The complete-case validation results (TPR ≥ 0.8, type-I ≤ 0.06, power at OR=2 = 1.0)
are reference benchmarks, not validity guarantees for the pairwise pipeline. Phase 2
Stage 0-V must establish its own benchmarks under the real missingness structure.

---

## 5. What Success Looks Like

Phase 2 succeeds at the project level if:
- The pairwise estimator is validated with documented power and calibration
- State-conditioned precision matrices are computed on the full 61-neuron subgraph
- The enrichment test is run with degree-preserving null
- The coordinate comparison is completed
- The result (positive, negative, or null) is reported honestly with the PSD diagnostic

The 61-neuron scope is recovered. The estimation methodology is new but validated.
The biological question is unchanged from Phase 1.