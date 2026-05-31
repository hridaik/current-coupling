# phase2_task.md — C. elegans Phase 2
## Missing-Data-Aware Precision Estimation on the Full 61-Neuron Subgraph

---

## Scientific purpose

Phase 2 answers the same biological question as Phase 1: does the conditional-dependence
structure of identified C. elegans neurons differ between behavioral states in a way that
cannot be attributed to the fixed synaptic connectome, and is that difference enriched for
non-synaptic signaling?

Phase 1 was closed because its estimation pipeline required a dense T × 61 pooled array
that does not exist in the SF freely-behaving corpus. Per-animal neuron identification
produces ~70 neurons from ~302, with each animal resolving a different ~70-neuron subset.
The complete-case intersection across ≥19 recordings collapses to 4–13 neurons — too few
to test the locked hypothesis on the intended circuit.

Phase 2 replaces the estimation object. Instead of requiring all 61 neurons simultaneously
observed in every contributing recording, the pairwise available-case approach estimates
each entry of the covariance matrix from the recordings where both neurons in that pair are
co-observed, then assembles the full 61 × 61 matrix. Per-pair co-observation is high
(~30–38 of 40 recordings for most pairs) even though the all-neuron intersection is 4.

The biological question, the enrichment test, the connectome classification, the behavioral
segmentation, and the coordinate system are all inherited from Phase 1. The estimation
pathway is new and requires its own specification, validation, and parameter lock before
real-data inference.

---

## Why this is a new project, not a Phase 1 patch

The validated statistical object changes. Phase 0/1 validated:
```
X_pooled (T_total × 61 dense array) → np.cov(X_pooled) → GraphicalLasso.fit()
```

Phase 2 validates:
```
{X_pair(i,j) for all pairs} → assemble S_pairwise (61 × 61) → PSD_project(S) → ADMM(S_projected)
```

The input to the estimator is no longer a data matrix but a pre-computed, assembled,
projected covariance estimate. The statistical properties of this pipeline — bias from
PSD projection, variance from heterogeneous per-pair sample sizes, calibration of
stability selection under recording-level resampling — are different from the complete-case
pipeline and must be established from scratch. That is why Phase 2 begins with a fresh
Stage 0.

---

## THE HARD CONSTRAINT: NO REAL-DATA PRECISION BEFORE STAGE 0-V PASSES

Inherited from Phase 0/1 and restated for Phase 2:

**No precision matrix, ΔQ, or enrichment statistic may be computed from real behavioral data
until Stage 0-V (estimator validation on synthetic data) passes all checks and the human
authorizes Stage 1.**

The pairwise covariance assembly itself (Stage 1.1) requires human authorization after
Stage 0-V. The covariance is the input to the precision estimator, and assembling it
from real data commits the analysis to the pairwise pathway.

**Permitted before Stage 0-V:**
- Characterizing the missingness structure (co-observation counts, graph properties)
- Literature review
- Implementing and testing the pairwise estimator on synthetic data
- Power analysis on synthetic data

---

## Inherited assets from Phase 0/1

The following are complete, validated, and carry forward without modification:

```
# From Phase 0 — carry forward unchanged
neuron_harmonization.csv              61-neuron master harmonization table
A_raw, A_gj, A_chem, A_peptide       connectome matrices (61 × 61)
randi_dcv_pairs.csv                   189 Randi unc-31-sensitive pairs
Creamer A_C, D_C, Ω_C                connectome-constrained LDS (56-neuron subspace)
BEHAV_THRESHOLD = 0.284               behavioral state segmentation
EWMA_TIMESCALE_SECONDS = 20.0
W_TRANS_SECONDS = 10.0
MIN_BOUT_SECONDS = 10.0
SYNAPSE_COUNT_THRESHOLD = 1
COORD_PRIMARY = "cepnem_residual"
COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"
LR_POLICY = "separate"
NORMALIZATION = "z_score_global"

# From Phase 1 Stage 1.0 — carry forward
CePNEM residualization pipeline       implemented and verified
CePNEM residualized traces            computed for all animals × common-subgraph neurons

# From Phase 0 Stage 8/9 — carry forward as reference (not as validation)
Enrichment test framework             AUROC + Fisher, simple + degree-preserving null
Null model implementation             degree-, class-preserving permutation
Power analysis framework              synthetic power curves

# Standing deviations — carry forward
DEV-003                               nonstationarity (photobleaching); accepted
DEV-004                               RESOLVED; CePNEM available
DEV-005                               all-animal pooling without outlier screening
```

## Parameters that must be re-established in Phase 2

```
MISSING_NEURON_POLICY                 → "pairwise_available_case" (to be validated)
DISCOVERY_ESTIMATOR                   → to be specified in Stage 0.3
CONFIRMATION_ESTIMATOR                → to be specified in Stage 0.3
N_COMMON_NEURONS                      → 61 (restored; pairwise approach recovers full space)
LAMBDA_ON / LAMBDA_OFF                → to be re-calibrated in Stage 0-V
PRIMARY_TOP_K                         → to be set after Stage 0-V power analysis
D_ROBUSTNESS_RHO                      → 0.7 (carry forward provisionally; confirm in Stage 0-V)
ESTIMATOR_TIER                        → to be determined in Stage 0-V
PSD_PROJECTION_METHOD                 → to be specified in Stage 0.3
PSD_EIGENVALUE_FLOOR                  → to be calibrated in Stage 0-V
STABILITY_SELECTION_RESAMPLE_UNIT     → "recording" (to be validated)
N_BOOTSTRAP_RESAMPLES                 → to be set in Stage 0-V
STABILITY_THRESHOLD                   → to be calibrated in Stage 0-V
MIN_COPRESENCE_RECORDINGS             → to be set in Stage 0.1
```

---

## Phase 2 repository structure

```
docs/
  phase0/                            Phase 0 archive (read-only reference)
  phase1_archive/                    Phase 1 archive (read-only reference)
  phase2/
    PHASE2_DESIGN_DECISIONS.md       All design decisions with justifications
src/
  # Inherited modules (no modification without deviation)
  data_access.py
  harmonization.py
  preprocessing.py
  cepnem_residualize.py
  enrichment.py
  null_models.py
  power_analysis.py
  plotting.py
  # New Phase 2 modules
  pairwise_covariance.py             pairwise assembly, co-observation tracking
  psd_projection.py                  eigenvalue projection onto PSD cone
  pairwise_estimators.py             stability selection + ADMM on pre-computed S
  missingness.py                     co-observation characterization, synthetic generator
scripts/
  phase2/
    stage0_1_copresence.py           co-observation structure characterization
    stage0_2_literature.py           (manual; notes file, not executable)
    stage0_3_estimator_spec.py       estimator specification and API design
    stage0_v1_synthetic_generator.py synthetic data with real missingness
    stage0_v2_pairwise_validation.py pairwise covariance + PSD projection validation
    stage0_v3_glasso_validation.py   graphical lasso on projected pairwise S
    stage0_v4_stability_sel.py       stability selection with recording resampling
    stage0_v5_anatomy_guided.py      anatomy-guided lasso on pairwise S
    stage0_v6_circularity.py         circularity control verification
    stage0_v7_power.py               power analysis and regime characterization
    stage0_v8_lock.py                parameter lock and summary
    stage1_estimation.py             real-data pairwise estimation
    stage2_delta_q.py                ΔQ computation and classification
    stage3_sensitivity.py            LOO and D-robustness
    stage4_enrichment.py             all enrichment tests
    stage5_coord_comparison.py       CePNEM vs raw GCaMP
    stage6_summary.py                figures, tables, named pairs
results/
  phase2/
    stage0/                          Stage 0 diagnostics
    stage0v/                         Stage 0-V validation outputs
    data/                            Stage 1+ numerical outputs
    figures/
    tables/
tests/
  test_pairwise_covariance.py
  test_psd_projection.py
  test_pairwise_estimators.py
  test_missingness_generator.py
phase2_config.py                     Phase 2 parameters (initially mostly None)
PHASE2_CHECKPOINT_LOG.md
```

---

## Stage 0 — Estimator Specification

### Stage 0.1 — Co-observation structure characterization

**Purpose:** Establish the exact missingness structure that the pairwise estimator must
handle, before designing the estimator.

**Tasks:**

1. For each neuron pair (i, j) in the 61-neuron subgraph, for each behavioral state
   s ∈ {dwelling, roaming}, count:
   - N_recordings_copresent(i, j, s): number of recordings where both i and j are
     identified AND the recording contributes ≥1 epoch in state s
   - N_frames_copresent(i, j, s): total frames in state s across those recordings

2. Compute the co-observation graph: nodes = 61 neurons, edge weight = N_recordings_copresent.
   Characterize:
   - Minimum, median, maximum co-observation count across all pairs
   - Number of pairs with co-observation count < 5 (potential instability threshold)
   - Whether the co-observation graph is connected (all pairs have ≥1 shared recording)
   - Degree distribution of the co-observation graph

3. Identify fragile pairs: any (i, j) where N_recordings_copresent < MIN_COPRESENCE_RECORDINGS.
   These pairs will have poorly estimated covariance entries and may need special treatment
   (exclusion, stronger regularization, or blockwise grouping).

4. Compute the per-pair effective sample size n_eff(i, j, s) using the cross-product
   integrated autocorrelation method from Phase 0, but now per-pair (using only the
   frames from recordings where both i and j are co-present).

5. Report summary statistics:
   - Median n_eff per pair per state
   - 25th percentile n_eff per pair per state
   - Fraction of pairs with n_eff < 20 per state (the Phase 0 underpowered threshold)

**Pass conditions:**
```
Co-observation graph is connected (no isolated pair)
Median co-observation recordings ≥ 25 per pair per state
Fewer than 10% of pairs with co-observation < 10 recordings
Summary statistics saved to results/phase2/stage0/copresence_report.json
```

**HUMAN CHECKPOINT after Stage 0.1:** Review the co-observation structure. Set
MIN_COPRESENCE_RECORDINGS in phase2_config.py (suggested: 10). Confirm that the
pairwise approach is justified given the observed co-observation density.

---

### Stage 0.2 — Literature review (manual, not coded)

Survey the missing-data graphical model literature for the specific estimator class.
Key references to evaluate:

- Städler & Bühlmann (2012) — graphical lasso with missing data; EM-based approach
- Loh & Wainwright (2012) — high-dimensional regression with missing observations
- Kolar & Xing (2012) — estimating sparse precision matrices with incomplete data
- The "huge" R package documentation on pairwise estimation
- Any C. elegans-specific applications of graphical models with missing neurons

Record findings in `docs/phase2/PHASE2_DESIGN_DECISIONS.md` with a recommendation
for the estimator class. This is a human research task, not a coding task.

---

### Stage 0.3 — Estimator specification

**Purpose:** Define the exact pairwise estimation pipeline that will be validated.

**Proposed pipeline (subject to human authorization):**

```
Step 1: Pairwise covariance assembly
  For each state s and each pair (i, j):
    Identify recordings where both i and j are co-present in state s
    Pool CePNEM-residualized frames from those recordings
    Compute sample covariance: S_pairwise(i, j, s) = cov(x_i, x_j)
    Record n_eff(i, j, s) and N_recordings(i, j, s)

Step 2: Assemble the full 61 × 61 covariance matrix S_s
  S_s[i, j] = S_pairwise(i, j, s) for all pairs
  S_s is symmetric by construction (cov(i,j) = cov(j,i) computed from same frames)
  Diagonal: S_s[i, i] = var(x_i) computed from all recordings containing neuron i in state s

Step 3: PSD projection
  Eigendecompose S_s = V Λ V^T
  If any λ_k < PSD_EIGENVALUE_FLOOR:
    Set λ_k = PSD_EIGENVALUE_FLOOR
    Record number of clipped eigenvalues and total clipped magnitude
  Reconstruct: S_s_proj = V Λ_clipped V^T

Step 4: Precision estimation
  Discovery: stability selection with recording-level resampling
    For each of N_BOOTSTRAP_RESAMPLES iterations:
      Draw half the recordings without replacement
      Recompute pairwise covariance on the subsample → S_boot
      PSD-project S_boot
      Run graphical lasso (BIC alpha) on S_boot_proj → Q_boot
      Record selected edges
    Stability score = fraction of bootstrap iterations selecting each edge
    Threshold at STABILITY_THRESHOLD for inclusion

  Confirmation: anatomy-guided ADMM lasso
    Input: S_s_proj (PSD-projected pairwise covariance from full data)
    Penalty: LAMBDA_ON for on-connectome, LAMBDA_OFF for off-connectome
    Output: Q_s_conf
```

**Key design decisions to record:**

- PSD_EIGENVALUE_FLOOR: how aggressively to clip negative eigenvalues.
  Too high = distorts the covariance; too low = numerical instability in lasso.
  Calibrate in Stage 0-V.

- STABILITY_SELECTION_RESAMPLE_UNIT = "recording": resample whole recordings, not frames.
  This preserves the within-recording temporal structure and the recording-level
  missingness pattern. Each bootstrap subsample has a different co-observation structure.

- Whether to weight pairwise covariance entries by their n_eff (inverse-variance weighting)
  or treat all entries equally. Evaluate in Stage 0-V.

**HUMAN CHECKPOINT after Stage 0.3:** Authorize the specific estimator pipeline or
request modifications. Only after authorization does Stage 0-V begin.

---

## Stage 0-V — Estimator Validation

### Purpose

Validate the pairwise estimation pipeline on synthetic data with the exact SF missingness
pattern. Establish power, calibration, and parameter values. This is the Phase 2 equivalent
of Phase 0 Stage 8.

### Synthetic data generator

```python
def generate_synthetic_pairwise_data(
    Q_true_roam,           # 61 × 61 true precision (roaming)
    Q_true_dwell,          # 61 × 61 true precision (dwelling)
    neuron_presence_matrix, # 40 × 61 boolean (actual SF recording × neuron presence)
    recording_state_frames, # dict: recording_id → {dwelling: n_frames, roaming: n_frames}
    rng                     # random seed
):
    """
    Generate synthetic multivariate Gaussian data with the EXACT SF missingness structure.

    For each recording r:
      - Identify which neurons are present: S_r = neuron_presence_matrix[r]
      - For each state s with frames in this recording:
        - Generate n_frames multivariate Gaussian samples from
          N(0, Q_true_s^{-1})[S_r, S_r] (marginal distribution over observed neurons)
        - Store as the "observed data" for this recording in this state
    """
```

The true ΔQ = Q_true_roam − Q_true_dwell should have planted off-connectome entries
(using the same A_raw classification as the real analysis) at a specified effect size.

### Validation stages

**Stage 0-V.1 — Pairwise covariance assembly under missingness:**

Generate synthetic data. Assemble pairwise covariance. Compare to the true covariance
(computed from Q_true^{-1}). Report:
- Per-entry bias: E[S_pairwise(i,j)] − Σ_true(i,j) (should be near zero under MCAR)
- Per-entry variance: Var[S_pairwise(i,j)] across 100 synthetic replications
- Correlation between assembled S_pairwise and Σ_true (vectorized)

Pass: per-entry bias < 0.01 × |Σ_true(i,j)| for ≥ 95% of entries.

**Stage 0-V.2 — PSD projection impact:**

For each synthetic replication, compute:
- Fraction of eigenvalues clipped
- Total spectral mass removed (sum of clipped eigenvalue magnitudes / trace)
- Frobenius distance ||S_projected − Σ_true||_F / ||Σ_true||_F
- Rank correlation of off-diagonal entries between S_projected and Σ_true

Pass: median fraction of clipped eigenvalues ≤ 0.15 (≤ 9 of 61).
Pass: rank correlation of off-diagonal entries ≥ 0.95.
Calibrate PSD_EIGENVALUE_FLOOR to minimize clipped fraction while keeping
the projected matrix well-conditioned.

**Stage 0-V.3 — Graphical lasso on projected pairwise covariance:**

Run graphical lasso (BIC alpha) on S_projected. Compare recovered Q to Q_true.
Report TPR and FPR for off-connectome ΔQ entries at specified effect sizes
(0.1, 0.2, 0.3, 0.5).

Compare to Phase 0 Stage 8 complete-case performance at equivalent n_eff.
The pairwise approach should not be dramatically worse (TPR within 0.2 of
complete-case at matched effective sample size).

Pass: TPR ≥ 0.6 at effect size 0.2 for the dwelling regime.

**Stage 0-V.4 — Stability selection with recording-level resampling:**

Run the full stability selection pipeline (N_BOOTSTRAP_RESAMPLES = 50,
recording-level resampling, pairwise covariance per subsample, PSD projection per
subsample, graphical lasso per subsample). Report:
- Stability score distribution for true-positive and true-negative edges
- Calibrate STABILITY_THRESHOLD: choose the threshold that maximizes
  (TPR − FPR) on synthetic data, or use 0.75 if the curve is flat

Pass: at STABILITY_THRESHOLD = 0.75, TPR ≥ 0.5 and FPR ≤ 0.10.

**Stage 0-V.5 — Anatomy-guided lasso on pairwise covariance:**

Run anatomy-guided ADMM lasso on S_projected with LAMBDA_ON and LAMBDA_OFF.
Sweep LAMBDA_ON ∈ {0.01, 0.02, 0.04, 0.08} and LAMBDA_OFF/LAMBDA_ON ∈ {5, 10, 15, 20}.
Select the combination that maximizes TPR while keeping FPR ≤ 0.05.

Lock LAMBDA_ON and LAMBDA_OFF in phase2_config.py.

**Stage 0-V.6 — Circularity control:**

Verify that the anatomy-guided lasso (with heavier off-connectome penalty) correctly acts
as a conservative confirmation estimator:
- Off-connectome entries selected by discovery (stability selection) should survive
  the anatomy-guided lasso at a rate ≥ 0.7 when they are true positives
- Off-connectome entries that are true negatives should be selected by the anatomy-guided
  lasso at a rate ≤ 0.05
- The circularity control logic is: if an off-connectome entry survives BOTH estimators,
  it is robust; if it survives only discovery, it has lower confidence

Pass: confirmation rate for true positives ≥ 0.7.
Pass: false confirmation rate ≤ 0.05.

**Stage 0-V.7 — Enrichment test calibration under pairwise assembly:**

Run the full enrichment pipeline (AUROC + Fisher, simple + degree-preserving null) on
synthetic ΔQ assembled via the pairwise pathway. Check:
- Type-I error: under null ΔQ (Q_true_roam = Q_true_dwell), is p < 0.05 in ≤ 5% of
  replications?
- Power: under planted enrichment (OR = 2), what fraction of replications achieve p < 0.05?

Pass: type-I error ≤ 0.06 (calibrated).
Pass: power at OR = 2 ≥ 0.60.

Calibrate PRIMARY_TOP_K: the K that maximizes Fisher test power at OR = 2 on synthetic data.
Lock in phase2_config.py.

**Stage 0-V.8 — Parameter lock:**

Lock all Phase 2 estimator parameters in phase2_config.py:
```
PSD_EIGENVALUE_FLOOR
STABILITY_SELECTION_RESAMPLE_UNIT = "recording"
N_BOOTSTRAP_RESAMPLES
STABILITY_THRESHOLD
LAMBDA_ON
LAMBDA_OFF
PRIMARY_TOP_K
MIN_COPRESENCE_RECORDINGS
```

Write `results/phase2/stage0v/validation_summary.md` with all pass/fail outcomes,
TPR/FPR curves, and calibrated parameters.

**HUMAN CHECKPOINT after Stage 0-V.8:** Review validation summary. Authorize Stage 1
(real-data estimation) or request additional validation. Set PHASE2_ACTIVE = True.

---

## Stage 1 — State-conditioned pairwise precision estimation

### Prerequisites

- PHASE2_ACTIVE = True (set by human after Stage 0-V)
- CePNEM residualized traces available (from Phase 1 Stage 1.0)
- All Phase 2 parameters locked in phase2_config.py

### Procedure

**For each coordinate system** (CePNEM residual primary, raw GCaMP robustness):

1.1 — **Pairwise covariance assembly.** For each state s and each pair (i, j):
identify co-present recordings, pool state-s frames, compute cov(i, j).
Record n_eff(i, j, s) and N_recordings(i, j, s). Assemble the full 61 × 61 S_s.
Save S_s to disk before any projection.

1.2 — **PSD projection.** Eigendecompose S_s. Apply PSD_EIGENVALUE_FLOOR clipping.
Record number of clipped eigenvalues and spectral mass removed. Compare to the
Stage 0-V synthetic baseline: if clipping is dramatically worse on real data
(>2× the synthetic median), halt and diagnose.

1.3 — **Discovery estimator.** Stability selection with recording-level resampling
(N_BOOTSTRAP_RESAMPLES, STABILITY_THRESHOLD). Output: Q_s_disc, stability_s.

1.4 — **Confirmation estimator.** Anatomy-guided ADMM lasso (LAMBDA_ON, LAMBDA_OFF)
on full-data S_s_projected. Output: Q_s_conf.

1.5 — **Diagnostics.** For each precision matrix: verify positive definite, symmetric,
condition number < 10^6. Print per-state summary.

This stage produces 8 precision matrices:
{CePNEM, raw_GCaMP} × {dwelling, roaming} × {discovery, confirmation}

### Pass conditions
```
All 8 precision matrices computed and saved
All positive definite and symmetric
PSD projection clipping within 2× the Stage 0-V synthetic baseline
Condition numbers recorded
No convergence failures
```

---

## Stage 2 — ΔQ computation and connectome classification

Identical to Phase 1 Stage 1.2 specification. The pairwise pathway is invisible
downstream: ΔQ = Q_roam − Q_dwell operates on the same 61 × 61 precision matrices
regardless of how they were estimated.

Classify into Class 1–4 using A_raw and A_C. Annotate Class 4 pairs with neuropeptide,
Randi, serotonin/PDF labels. Rank by |ΔQ| × min(stability_roam, stability_dwell).

### Pass conditions
```
4 ΔQ matrices computed (2 coords × 2 estimators)
Class 4 count ≥ 30 (the pairwise approach should recover the full 61-neuron pair space)
Ranked pair lists saved
```

---

## Stage 3 — Sensitivity analysis

### Stage 3.1 — Leave-one-animal-out

For each animal, recompute pairwise covariance with that animal excluded, PSD-project,
run discovery estimator, compute ΔQ, rank Class 4 pairs. Report retention of top-50
pairs across LOO iterations. Flag influential animals.

Primary analysis variant only: CePNEM residuals × discovery estimator.

### Stage 3.2 — D-robustness check

Identical to Phase 1 Stage 1.4: compute D_C ΔQ, D_diag ΔQ, I·ΔQ in the 56-neuron
Creamer subspace. Spearman correlation of top-50 rankings across all three D models.
Go/no-go at D_ROBUSTNESS_RHO = 0.7.

### Stage 3.3 — Ω_C comparison (secondary)

Identical to Phase 1 Stage 1.5: compute Ω̂_s^(C) = A_C + D_C Q_s in 56-neuron subspace.
Verify ΔΩ̂^(C) = D_C ΔQ numerically. Report with preparation-mismatch caveat.

### Pass conditions
```
LOO completed; median retention ≥ 0.70
D-robustness go/no-go recorded
Ω_C comparison saved with caveat
```

---

## Stage 4 — Enrichment tests

Identical to Phase 1 Stage 1.6 specification:

- Test 1: Neuropeptide AUROC (primary) — simple + degree-preserving null
- Test 2: Neuropeptide Fisher top-K (secondary) — both nulls
- Test 3: Randi unc-31 AUROC + Fisher (secondary) — both nulls
- Test 4: Serotonin/PDF receptor AUROC + Fisher (exploratory)
- Confirmation estimator check: repeat Test 1 with confirmation estimator's ΔQ

All tests use the Phase 2-locked PRIMARY_TOP_K (calibrated in Stage 0-V.7).
Degree-preserving null preserves degree in A_raw and A_peptide.

### Pass conditions
```
All tests run with both null models
p-values, AUROCs, odds ratios, CIs saved
Confirmation estimator check completed
Null model degree-preservation validated
Results saved BEFORE any figure
```

---

## Stage 5 — Coordinate comparison

Identical to Phase 1 Stage 1.7 specification. Apply the locked interpretation table:

| CePNEM enrichment | Raw GCaMP enrichment | Interpretation |
|---|---|---|
| Significant (p < 0.05, degree-preserving) | Significant | Residual neural state organization |
| Significant | Not significant | Neural organization masked by behavioral noise |
| Not significant | Significant | Behavior-mediated state structure |
| Not significant | Not significant | Null result |

### Pass conditions
```
Both coordinate analyses complete before interpretation
Interpretation rule applied mechanically
Interpretation recorded with supporting numbers
```

---

## Stage 6 — Summary, figures, named pairs

Identical to Phase 1 Stage 1.8 specification:

Primary figure (6 panels): ΔQ heatmaps (both coords), ranked Class 4 pairs with
neuropeptide overlay, AUROC curve, LOO retention heatmap, D-robustness scatter.

Summary table: per-variant statistics.

Named pair table: top-20 Class 4 pairs with all annotations and prediction column.

**Additional Phase 2-specific panel (Panel G):**
PSD projection diagnostic: eigenvalue spectrum of S_pairwise before and after projection,
for each state. This documents how much the pairwise assembly deviated from PSD and how
the projection corrected it. Essential for reviewers evaluating the methodology.

### Pass conditions
```
Figure saved as PDF and PNG
Summary table saved
Named pair table with predictions saved
PSD diagnostic panel included
All source data saved separately
```

---

## Passing criteria — graded

### Minimum viable
```
1. Co-observation structure characterized (Stage 0.1)
2. Pairwise estimator specified and authorized (Stage 0.3)
3. Synthetic validation passes (Stage 0-V, all checks)
4. Pairwise precision matrices computed in CePNEM residual coordinates (Stage 1)
5. ΔQ computed and classified; Class 4 count ≥ 30 (Stage 2)
6. Neuropeptide AUROC computed with both nulls (Stage 4)
7. Coordinate comparison completed (Stage 5)
```

### Adequate
All minimum plus:
```
8. LOO sensitivity completed; median retention ≥ 0.70 (Stage 3.1)
9. D-robustness check completed (Stage 3.2)
10. All four enrichment tests with both nulls (Stage 4)
11. Confirmation estimator check completed (Stage 4)
12. Named pair table produced (Stage 6)
```

### Good
All adequate plus:
```
13. Neuropeptide enrichment significant (p < 0.05) under degree-preserving null
    in CePNEM coordinates
14. Enrichment survives CePNEM residualization (interpretation row 1 or 2)
15. D-robustness passes (Spearman ≥ 0.7)
16. PSD projection clipped ≤ 10% of eigenvalues
17. Full figure with all panels including PSD diagnostic
```

### Best case
All good plus:
```
18. Enrichment significant under degree-preserving null in BOTH coordinates
19. Randi unc-31 enrichment also significant
20. Confirmation estimator AUROC within 0.10 of discovery
21. Named pairs include ≥ 5 with convergent peptide + Randi annotation
22. LOO identifies no influential animal (>30% top-50 change)
```

---

## Failure modes specific to the pairwise approach

**PSD projection clips > 30% of eigenvalues:**
- The pairwise covariance matrix is far from PSD
- Possible cause: heterogeneous per-pair sample sizes creating inconsistent estimates
- Diagnosis: check whether fragile pairs (low co-observation) are responsible
- Remediation: exclude pairs below MIN_COPRESENCE_RECORDINGS and re-assemble
- If still > 30% after exclusion: the pairwise approach is not viable for this dataset

**TPR on synthetic data drops substantially below complete-case baseline:**
- The PSD projection or per-pair variance is degrading the signal
- Diagnosis: compare TPR at matched n_eff between pairwise and complete-case on the
  same synthetic Q_true (using the small complete-case subgraph as baseline)
- If TPR < 0.4 at effect size 0.2: the pairwise approach does not have adequate power

**Type-I error inflated under pairwise assembly:**
- The PSD projection or heterogeneous sample sizes create spurious precision entries
- Diagnosis: run null ΔQ (Q_roam = Q_dwell) through the full pipeline 200 times;
  check rejection rate
- If type-I > 0.10: the enrichment test is not calibrated; cannot proceed

**Stability selection gives very low stability scores for all edges:**
- Recording-level resampling produces highly variable pairwise covariances
- Each bootstrap subsample has a different co-observation structure, changing which
  pairs are estimable
- Diagnosis: check whether stability improves with frame-level resampling (less variable
  but does not respect recording structure)
- Consider a hybrid: resample recordings, then compute pairwise S only for pairs with
  ≥ MIN_COPRESENCE in the subsample

**Real-data PSD clipping is dramatically worse than synthetic:**
- The real covariance structure violates the synthetic assumptions (Gaussian, MCAR)
- Diagnosis: compare eigenvalue spectra of real vs. synthetic S_pairwise
- Possible cause: non-Gaussianity (heavy tails, multimodality), non-stationarity within
  state, or subtle violations of MCAR (some neurons' absence is correlated with neural state)

---

## Minimum viable success for Phase 2

Phase 2 succeeds if it produces:

1. A validated pairwise estimation pipeline with documented power and calibration
2. State-conditioned precision matrices on the full 61-neuron subgraph
3. A classified ΔQ with Class 4 pairs ranked by stability-weighted magnitude
4. A neuropeptide enrichment AUROC with p-value from the degree-preserving null
5. A coordinate comparison applying the locked interpretation rule
6. A PSD projection diagnostic documenting how far from PSD the assembled covariance was

This is sufficient to state: "Using pairwise available-case covariance estimation with
PSD projection to accommodate the per-animal neuron observability structure of freely
behaving C. elegans whole-brain calcium imaging, we estimated state-conditioned precision
matrices on 61 identified neurons and tested whether off-connectome state-switched
conditional-dependence structure is enriched for neuropeptide signaling."