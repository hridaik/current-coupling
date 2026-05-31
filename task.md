# task.md — C. elegans Phase 1
## Real-Data Inference: State-Conditioned Precision, ΔQ, and Enrichment

---

## Scientific purpose

Phase 1 answers the question Phase 0 was built to protect: does the conditional-dependence
structure of identified C. elegans neurons differ between roaming and dwelling behavioral
states in a way that cannot be attributed to the fixed synaptic connectome, and is that
difference enriched for non-synaptic signaling?

Phase 0 locked all preprocessing decisions, validated the estimation pipeline on synthetic
data, and confirmed statistical power. Phase 1 computes state-conditioned precision matrices
from real behavioral data, classifies ΔQ entries against the synaptic connectome, tests for
neuropeptide enrichment, and determines whether the result survives CePNEM residualization.

---

## CONSTRAINT: CePNEM RESIDUALIZATION BEFORE ANY PRECISION MATRIX

The single ordering constraint that governs Phase 1:

**No precision matrix may be computed from real data until Stage 1.0 (CePNEM residualization)
passes all verification checks.**

The reason: CePNEM residuals are the primary coordinate system. If precision matrices are
computed in raw GCaMP first and the results are seen, there is a risk of interpretation
contamination — knowing the raw-coordinate result biases evaluation of the CePNEM result.
The correct order is: implement CePNEM, verify it works, then compute precision in both
coordinate systems without previewing either before both are complete.

---

## GUARDRAIL CHANGE FROM PHASE 0

Phase 0 prohibited all real-data precision computation via a RuntimeError guard in
`src/estimators.py`. Phase 1 lifts this guard.

Before beginning Stage 1.1, set `PHASE0_COMPLETE = True` in `phase0_config.py` and verify
the guardrail permits `data_kind="real"`. This requires explicit human authorization and
must be recorded in `CHECKPOINT_LOG.md` with date and rationale.

The human must first acknowledge the three standing deviations from Phase 0:

1. **DEV-003 (nonstationarity):** All recordings show temporal covariance drift
   (photobleaching). Results are time-averaged effective structure, not stationary.
   Interpretation rule: accepted as design constraint.

2. **DEV-004 (coordinate system):** Now RESOLVED. CePNEM residuals are available and
   become the primary coordinate system. Raw GCaMP becomes robustness coordinate.
   Update `COORD_PRIMARY = "cepnem_residual"` in `phase0_config.py`.

3. **DEV-005 (inter-animal variability):** Stage 7 was not completed. Leave-one-animal-out
   sensitivity in Stage 1.3 compensates. Human confirms all-animal pooling without
   prior outlier screening.

---

## Inherited locked parameters

All values below are inherited from Phase 0 and must not be changed during Phase 1.
They live in `phase0_config.py` and are imported by every script.

```
# Subgraph
N_COMMON_NEURONS                = 61
N_RANDI_SUBGRAPH_NEURONS        = 60   (AWCL absent from funatlas)
N_CREAMER_SUBGRAPH_NEURONS      = 56   (AIBL, AIBR, AWCL, IL1L, IL1R absent)

# Behavioral segmentation
BEHAV_THRESHOLD                 = 0.284
BEHAVIOR_SCORE_SOURCE           = "velocity_s"
EWMA_TIMESCALE_SECONDS          = 20.0
W_TRANS_SECONDS                 = 10.0
MIN_BOUT_SECONDS                = 10.0

# Normalization
NORMALIZATION                   = "z_score_global"
MISSING_NEURON_POLICY           = "nan_complete_case"
LR_POLICY                       = "separate"
SYNAPSE_COUNT_THRESHOLD         = 1

# Estimation
ESTIMATOR_TIER                  = "pooled_hierarchical"
POOLING_STRATEGY                = "pooled"
DISCOVERY_ESTIMATOR             = "unstructured_stability_selection"
CONFIRMATION_ESTIMATOR          = "anatomy_guided_lasso"
LAMBDA_ON                       = 0.04
LAMBDA_OFF                      = 0.45

# Enrichment
PRIMARY_ENRICHMENT_STAT         = "AUROC"
SECONDARY_ENRICHMENT_STAT       = "Fisher_topK"
PRIMARY_TOP_K                   = 50
D_ROBUSTNESS_RHO                = 0.7

# Creamer
CREAMER_TIME_CONVENTION         = "discrete"
CREAMER_DT                      = 0.5
CREAMER_MAX_EIGENVALUE           = 0.9966
CREAMER_DC_AVAILABLE            = True
CREAMER_OMEGA_NORM              = 8.6089  # 56-neuron subspace

# Validated regimes (from Phase 0 synthetic)
# non_roaming: 39/40 animals, TPR=1.00 at optimistic T
# roaming: 25/40 animals, TPR=0.90 at pooled T=1000; exploratory
```

---

## Phase 1 repository additions

Phase 0 code remains in `src/` and `scripts/`. Phase 1 adds:

```
src/
  cepnem_residualize.py    # CePNEM model evaluation and residual computation
  delta_q.py               # ΔQ computation, classification, ranking
  d_robustness.py          # D-scaling and Spearman rank comparison
  omega_comparison.py      # Ω̂_s^(C) and ΔΩ_model computation
  coord_comparison.py      # cross-coordinate overlap and interpretation rule
scripts/
  phase1/
    stage0_cepnem.py             # CePNEM residualization and verification
    stage1_precision.py          # state-conditioned precision estimation
    stage2_delta_q.py            # ΔQ computation and classification
    stage3_loo_sensitivity.py    # leave-one-animal-out
    stage4_d_robustness.py       # D-robustness check and current-velocity bridge
    stage5_omega_comparison.py   # Ω_C comparison (secondary)
    stage6_enrichment.py         # all enrichment tests
    stage7_coord_comparison.py   # cross-coordinate interpretation
    stage8_summary.py            # figures, tables, named pairs
results/
  phase1/
    data/          # all numerical outputs
    figures/       # all figures
    tables/        # summary tables, named pair lists
```

---

## Stage 1.0 — CePNEM residualization

### Purpose

Implement and verify CePNEM residualization so that the primary coordinate system (residual
neural activity after removing behavioral encoding) is available for all subsequent stages.

### Implementation

The CePNEM model decomposes each neuron's calcium trace into a predicted behavioral
component and a residual:

```
predicted_i(t) = model_nl8(posterior_median_params_i, behavioral_covariates(t))
residual_i(t)  = trace_array_i(t) - predicted_i(t)
```

Source: `fit_results.jld2` contains `sampled_trace_params`, behavioral encoding posterior
samples, behavioral covariates, epoch boundaries, and aligned recording identifiers.
Precomputed residuals are NOT present; they must be computed here.

### Tasks

1. Load `fit_results.jld2`. Extract posterior median parameters for each neuron.
   Resolve the `sampled_trace_params[..., 6]` ↔ `sampled_tau_vals` mapping by checking
   the CePNEM source code parameter ordering. Document the verified mapping.

2. For each animal and each identified neuron in the 61-neuron common subgraph:
   - Evaluate the CePNEM nonlinear model at the posterior median parameters
   - Compute residual = raw trace − predicted
   - Apply the same z-score normalization used for raw GCaMP (`z_score_global`)

3. Verification checks (all must pass):

   a. **Behavioral decorrelation:** For each neuron, compute the Pearson correlation between
      the residual and each primary behavioral covariate (velocity, angular velocity,
      curvature). Compare to the same correlations for the raw trace. The median absolute
      correlation with behavioral covariates must decrease by ≥ 50% after residualization.

   b. **Residual variance:** For each neuron, compute var(residual) / var(raw). If this
      ratio < 0.10 for any neuron, the CePNEM model is overfitting that neuron; flag it
      for potential exclusion from the CePNEM coordinate analysis (retain in raw GCaMP).

   c. **Epoch boundary artifacts:** Plot residuals around epoch boundaries for a
      representative subset of animals. Verify no systematic transients at boundaries.

   d. **Residual stationarity:** Compute the same rolling-covariance and first/second-half
      drift metrics used in Phase 0 Stage 7. Compare NONSTATIONARITY_FRACTION for
      CePNEM residuals vs. raw GCaMP. If residualization reduces drift (because
      photobleaching is partially captured by the behavioral model), record the improvement.

4. Save residualized traces to `results/phase1/data/cepnem_residuals/` in the same
   format as raw trace arrays.

### Pass conditions

```
CePNEM model evaluated for all animals × common-subgraph neurons
Tau parameter mapping verified and documented
Behavioral decorrelation: median |r| reduction ≥ 50%
No neuron with residual variance ratio < 0.10 (or flagged and documented)
No epoch boundary artifacts
Residualized traces saved to disk
```

**GATE: Do not proceed to Stage 1.1 until all Stage 1.0 checks pass.**

---

## Stage 1.1 — State-conditioned precision estimation

### Purpose

Compute state-conditioned precision matrices in both coordinate systems using both
estimators. This is the first computation that was forbidden during Phase 0.

### Procedure

**For each coordinate system** (CePNEM residual, raw GCaMP), **independently:**

1. Segment recordings using locked parameters (BEHAV_THRESHOLD = 0.284 on EWMA velocity_s,
   W_TRANS = 10s, MIN_BOUT = 10s). Record per-animal epoch counts and frame totals for
   each state.

2. Pool frames across animals within each state. Record:
   - N_animals contributing to roaming (expected: ~25)
   - N_animals contributing to dwelling (expected: ~39)
   - Total frames per state
   - Effective sample size per state (from Phase 0 n_eff computation, recomputed on
     CePNEM residuals if the autocorrelation structure differs)

3. **Discovery estimator (stability selection with graphical lasso):**
   - 50 bootstrap resamples of animals (draw half without replacement each time)
   - For each resample: fit graphical lasso with BIC alpha selection
   - Record stability score for each edge: fraction of resamples selecting it
   - Threshold at 0.75 for edge inclusion
   - Output: Q_s^disc (precision matrix), stability_s (edge stability matrix)

4. **Confirmation estimator (anatomy-guided lasso):**
   - ADMM solver with per-entry penalty (LAMBDA_ON = 0.04 on-connectome, LAMBDA_OFF = 0.45
     off-connectome)
   - Output: Q_s^conf (precision matrix)

5. For each precision matrix, verify:
   - Positive definite
   - Symmetric within tolerance (max |Q − Q^T| < 1e-10)
   - Condition number < 10^6
   - Print and record all diagnostics

This stage produces 8 precision matrices total:
{CePNEM, raw_GCaMP} × {roaming, dwelling} × {discovery, confirmation}

### Pass conditions

```
All 8 precision matrices computed and saved
All positive definite and symmetric
Condition numbers recorded
N_animals and n_eff per state per coordinate recorded
No convergence failures in either estimator
```

---

## Stage 1.2 — ΔQ computation and connectome classification

### Purpose

Compute the state-switching signal and classify every entry by its synaptic support status.

### Procedure

1. For each estimator × each coordinate system, compute:
   ```
   ΔQ = Q_roam − Q_dwell
   ```
   (4 ΔQ matrices total)

2. For each off-diagonal entry (i, j), assign a support class based on the
   61-neuron anatomical subgraph:

   **Class 1 — On-both:** A_raw(i,j) ≥ 1 AND A_C(i,j) ≠ 0
   **Class 2 — On-raw-only:** A_raw(i,j) ≥ 1 AND A_C(i,j) = 0
   **Class 3 — Off-raw, on-Creamer:** A_raw(i,j) = 0 AND A_C(i,j) ≠ 0
     (should not occur if Creamer is connectome-constrained; flag if present)
   **Class 4 — Off-both:** A_raw(i,j) = 0 AND A_C(i,j) = 0
     (primary candidates for current-supported state-dependent structure)

3. Within Class 4, annotate each pair:
   - `peptide_supported`: A_peptide(i,j) = 1 (either direction)
   - `randi_dcv`: pair is among the 189 Randi DCV-sensitive pairs
   - `serotonin_receptor`: either neuron expresses a serotonin receptor
   - `pdf_receptor`: either neuron expresses PDFR-1

4. Rank Class 4 pairs by a combined score:
   ```
   rank_score(i,j) = |ΔQ(i,j)| × min(stability_roam(i,j), stability_dwell(i,j))
   ```
   where stability comes from the discovery estimator. A pair that is not stably estimated
   in both states gets a low score regardless of its ΔQ magnitude.

5. Save the full classified and ranked pair list to
   `results/phase1/data/delta_q_classified_[coord]_[estimator].csv`
   with columns: neuron_i, neuron_j, class, ΔQ, stability_roam, stability_dwell,
   rank_score, peptide_supported, randi_dcv, serotonin_receptor, pdf_receptor.

6. Print summary statistics:
   - Number of pairs in each class
   - Number of Class 4 pairs with rank_score > 0 (nonzero ΔQ and stable in both states)
   - Top-10 Class 4 pairs by rank_score (names and annotations)

### Pass conditions

```
All 4 ΔQ matrices computed and classified
Class 3 count = 0 (or flagged with explanation)
Class 4 pair count ≥ 20 (otherwise enrichment test is underpowered)
Ranked pair lists saved for all 4 analysis variants
Summary statistics recorded
```

---

## Stage 1.3 — Leave-one-animal-out sensitivity

### Purpose

Compensate for the missing inter-animal variability assessment (Phase 0 DEV-005) by
testing whether the top-ranked pairs are driven by individual animals.

### Procedure

Run in the primary analysis variant only: CePNEM residuals × discovery estimator.

1. For each contributing animal a ∈ {1, ..., N_animals}:
   - Recompute pooled ΔQ with animal a excluded (re-run stability selection on the
     remaining animals for both states)
   - Re-rank Class 4 pairs

2. For each of the top-50 Class 4 pairs from the full analysis:
   - Compute retention: fraction of leave-one-out iterations where the pair remains
     in the top-50
   - A pair with retention ≥ 0.80 is animal-robust
   - A pair with retention < 0.50 is flagged as potentially single-animal-driven

3. Identify influential animals: any animal whose exclusion changes > 30% of the top-50
   list. Record their IDs.

4. Save a leave-one-out stability matrix to
   `results/phase1/data/loo_retention_matrix.csv`

### Computational note

This stage requires N_animals × 2 (states) runs of stability selection. With 50
bootstrap resamples per run and ~39 animals, this is ~3900 graphical lasso fits.
Estimate wall time before running and request a checkpoint if > 30 minutes.

For feasibility: run a quick 3-animal LOO pilot first (exclude animals 1, 15, 30)
to verify the pipeline works and estimate per-iteration time.

### Pass conditions

```
LOO completed for all contributing animals
Retention scores computed for top-50 pairs
Median retention across top-50 ≥ 0.70
Influential animals (if any) identified and recorded
LOO retention matrix saved
```

---

## Stage 1.4 — D-robustness check and current-velocity bridge

### Purpose

Determine whether D_C ΔQ (the Creamer-referenced current-like statistic) is interpretable,
and if so, compute it.

### Procedure

Restrict to the 56-neuron Creamer-compatible subspace. Use the CePNEM residual ΔQ from
the discovery estimator.

1. Compute three D-scaled versions of ΔQ (Class 4 entries only):
   - `D_C ΔQ`: Creamer's diagonal D_C (available from Phase 0)
   - `D_diag ΔQ`: diagonal D estimated from per-neuron CePNEM residual variance
   - `I · ΔQ`: identity diffusion (unscaled ΔQ)

2. Rank Class 4 pairs by magnitude in each version.

3. Compute pairwise Spearman correlations among all three rankings for the top-50 pairs.

4. Apply the locked decision rule:
   - All three Spearman correlations ≥ D_ROBUSTNESS_RHO (0.7):
     **D-robustness PASSES**. D_C ΔQ is the reported current-velocity bridge.
   - Any correlation < 0.7:
     **D-robustness FAILS**. ΔQ is the primary statistic. D_C ΔQ reported as inconclusive,
     with the specific disagreeing pair listed.

5. If D-robustness passes, save `results/phase1/data/dc_delta_q.csv` with the D_C-scaled
   ranked pair list.

### Pass conditions

```
Three D-scaled ΔQ versions computed
Spearman correlations recorded
Go/no-go decision recorded in CHECKPOINT_LOG.md
If PASS: D_C ΔQ saved; if FAIL: documented with specific disagreements
```

---

## Stage 1.5 — Ω_C comparison (secondary)

### Purpose

Compare freely moving state-conditioned current-like structure to the Creamer model's
own predicted current structure. This is secondary and carries a preparation mismatch
caveat that must be stated in every result from this stage.

### Procedure

In the 56-neuron Creamer subspace, using CePNEM residual precision matrices:

1. Compute the Creamer-referenced current-like structure per state:
   ```
   Ω̂_s^(C) = A_C + D_C Q_s
   ```

2. Compute the departure from the Creamer model's own prediction:
   ```
   ΔΩ_model_s = Ω̂_s^(C) − Ω_C
   ```
   where Ω_C = 8.6089 (Frobenius norm, computed in Phase 0).

3. Compute the state difference:
   ```
   ΔΩ̂^(C) = Ω̂_roam^(C) − Ω̂_dwell^(C) = D_C · ΔQ
   ```
   Verify this equals D_C ΔQ from Stage 1.4 to numerical precision (< 1e-10).

4. Save all matrices and their Frobenius norms.

### Caveat (must appear in every result)

Ω̂_s^(C) mixes Creamer's (A_C, D_C) from immobilized optogenetic perturbation recordings
with Atanas Q_s from freely moving spontaneous behavior. The absolute values of Ω̂_s^(C)
and ΔΩ_model contain preparation mismatch, coordinate mismatch, and noise mismatch in
addition to biological current. They are model-based residuals, not direct measurements
of biological probability current.

ΔΩ̂^(C) = D_C ΔQ is more robust because A_C cancels in the state difference.

### Pass conditions

```
Ω̂_s^(C) computed for both states
ΔΩ̂^(C) matches D_C ΔQ from Stage 1.4 within 1e-10
All matrices and norms saved
Caveat text included in every output file header
```

---

## Stage 1.6 — Enrichment tests

### Purpose

Test whether the off-connectome state-switched ΔQ entries are enriched for non-synaptic
signaling annotations. This is the primary scientific result of Phase 1.

### Procedure

Run in the primary analysis variant: CePNEM residuals × discovery estimator × Class 4 pairs.

**Test 1 — Neuropeptide enrichment (AUROC) [PRIMARY]:**

- Pair list: all Class 4 pairs with rank_score > 0
- Binary label: peptide_supported (from Stage 1.2)
- Statistic: AUROC — how well does neuropeptide annotation predict high |ΔQ| rank?
- Null model A (simple permutation): shuffle peptide labels across pairs, 10,000 iterations
- Null model B (degree-preserving): shuffle peptide labels preserving each neuron's
  degree in A_raw and in A_peptide within the 61-neuron subgraph, 10,000 iterations
- Report: AUROC, p_simple, p_degree, 95% CI on AUROC

**Test 2 — Neuropeptide enrichment (Fisher top-K) [SECONDARY]:**

- Take top-50 Class 4 pairs by rank_score
- 2×2 table: (top-50 vs. rest) × (peptide_supported vs. not)
- Fisher exact test under both null models
- Report: odds ratio, p_simple, p_degree

**Test 3 — Randi unc-31-sensitive enrichment [SECONDARY]:**

- Restrict to the 60-neuron Randi subgraph
- Binary label: randi_dcv
- Same AUROC + Fisher framework as Tests 1–2
- Report: AUROC, odds ratio, p-values under both nulls

**Test 4 — Serotonin/PDF receptor enrichment [EXPLORATORY]:**

- Binary label: serotonin_receptor OR pdf_receptor for either neuron in the pair
- AUROC + Fisher
- Reported as exploratory; not part of the primary hypothesis

**Confirmation estimator check:**

- Repeat Test 1 (neuropeptide AUROC) using the confirmation estimator's ΔQ
- This tests whether the enrichment survives the heavier off-connectome penalty
- If AUROC is comparable (within 0.1 of discovery estimate): circularity concern addressed
- If AUROC drops substantially: the result may be estimator-dependent; flag

### Null model implementation for degree-preserving permutation

```python
def degree_preserving_permutation(pair_list, labels, A_raw, A_peptide, n_perms=10000):
    """
    Permute pair labels while approximately preserving:
    - each neuron's degree in A_raw within the subgraph
    - each neuron's degree in A_peptide within the subgraph
    Uses a Markov-chain edge-swap approach restricted to the pair list.
    """
```

Validate the null model preserves both degree distributions (Kolmogorov-Smirnov test
between original and permuted degree sequences, p > 0.05 for ≥ 95% of permutations).

### Pass conditions

```
All 4 tests run with both null models
p-values, AUROCs, odds ratios, and CIs saved to results/phase1/data/enrichment_results.json
Confirmation estimator check completed
Null model degree-preservation validated
All results saved BEFORE any figure is generated
```

---

## Stage 1.7 — Coordinate comparison

### Purpose

Determine whether the enrichment result survives CePNEM residualization. This is the key
interpretive step that was impossible during Phase 0 (DEV-004) and is now the highest-value
comparison in the analysis.

### Procedure

By this point, Stages 1.1–1.6 have been run independently in both coordinate systems.

1. Compare top-50 Class 4 pair lists:
   - How many of the CePNEM top-50 also appear in the raw GCaMP top-50?
   - Jaccard similarity of the two sets
   - Spearman correlation of the rank_scores across all Class 4 pairs

2. Compare enrichment results:
   - CePNEM AUROC vs. raw GCaMP AUROC (Test 1 from Stage 1.6)
   - Both p-values (simple and degree-preserving)

3. Apply the locked interpretation rule:

   | CePNEM enrichment significant | Raw GCaMP enrichment significant | Interpretation |
   |------|------|------|
   | Yes (p < 0.05, degree-preserving) | Yes | **Residual neural state organization** — strong claim; the state-switching structure is not explained by behavioral kinematics or the synaptic connectome, and it targets non-synaptic signaling channels |
   | Yes | No | **Neural organization masked by behavioral noise** — CePNEM reveals structure hidden in raw coordinates |
   | No | Yes | **Behavior-mediated state structure** — the state-switching signal is present only in raw coordinates where behavioral confounds are uncontrolled; the CePNEM residual shows no enrichment; interpret cautiously |
   | No | No | **Null result** — no evidence for current-supported state-dependent neuropeptide-enriched structure in this dataset under these methods |

4. Record the interpretation in `results/phase1/data/coord_comparison_interpretation.json`
   with the specific p-values, AUROCs, and overlap statistics that determined it.

### Pass conditions

```
Both coordinate analyses complete before comparison is evaluated
Overlap statistics computed
Interpretation rule applied mechanically (not post-hoc)
Interpretation recorded with supporting numbers
```

---

## Stage 1.8 — Summary, figures, and named pairs

### Purpose

Produce all deliverables for Phase 1: the primary figure, the summary table, and the
named pair list that feeds Phase 4 (experimental predictions).

### Primary figure (6 panels)

**A.** ΔQ heatmap in CePNEM residual coordinates (61 × 61), with Class 4 entries
highlighted (distinct border or overlay). Color scale: diverging, centered at zero.
Neurons ordered by anatomical class (sensory, inter, motor) then alphabetically.

**B.** Same heatmap in raw GCaMP coordinates, identical ordering and color scale.

**C.** Ranked |ΔQ| × stability for Class 4 pairs (x-axis: rank; y-axis: score).
Points colored by neuropeptide annotation (peptide_supported or not).
Both coordinate systems overlaid or side-by-side.

**D.** AUROC curve for neuropeptide enrichment in CePNEM coordinates.
Null distribution (degree-preserving) shown as shaded area.
p-value annotated.

**E.** Leave-one-animal-out retention heatmap: top-50 pairs (rows) × animals (columns),
colored by whether the pair remains in top-50 when that animal is excluded.

**F.** D-robustness scatter: for each Class 4 pair, plot |D_C ΔQ| vs. |I · ΔQ| in
56-neuron Creamer subspace. Color by neuropeptide annotation. Spearman ρ annotated.
(Only if D-robustness passed in Stage 1.4.)

### Summary table

One row per analysis variant (coordinate × estimator), with columns:
- N Class 4 pairs with rank_score > 0
- Neuropeptide AUROC (degree-preserving p-value)
- Neuropeptide Fisher OR (degree-preserving p-value)
- Randi AUROC (degree-preserving p-value)
- D-robustness outcome
- LOO median retention

### Named pair table (the Phase 4 input)

The top-20 Class 4 pairs in CePNEM residual coordinates (discovery estimator), ranked by
rank_score × LOO_retention, with columns:

| neuron_i | neuron_j | ΔQ_cepnem | ΔQ_raw | rank_score | LOO_retention | peptide | randi_dcv | 5HT_receptor | PDF_receptor | prediction |

The `prediction` column states, for each pair, the expected outcome of specific
perturbations (to be developed in Phase 4):
- `unc31_shrink`: ΔQ should shrink in unc-31 mutants (if peptide_supported)
- `tph1_shrink_dwell`: ΔQ should shrink in tph-1 if the pair is dwelling-enriched and
  serotonin-receptor-expressing
- `pdfr1_shrink_roam`: ΔQ should shrink in pdfr-1 if roaming-enriched and PDF-expressing
- `structural_robust`: ΔQ should survive ablation of any single neuron on the shortest
  synaptic path between i and j (because no such path exists for Class 4 pairs)

### Pass conditions

```
Figure saved as PDF and PNG to results/phase1/figures/
Summary table saved to results/phase1/tables/summary.csv
Named pair table saved to results/phase1/tables/named_pairs.csv
All figure source data saved separately under results/phase1/data/
Caption text drafted in results/phase1/figures/figure_caption.md
```

---

## Passing criteria — graded

### Minimum viable (sufficient to report a result)

```
1. CePNEM residualization verified (Stage 1.0 passed)
2. Precision matrices computed in both coordinates (Stage 1.1 passed)
3. ΔQ computed and classified; Class 4 count ≥ 20 (Stage 1.2 passed)
4. Neuropeptide AUROC computed with both null models (Stage 1.6 Test 1)
5. Coordinate comparison completed; interpretation rule applied (Stage 1.7)
6. Summary table produced
```

### Adequate

All minimum plus:
```
7. LOO sensitivity completed; median retention ≥ 0.70 (Stage 1.3)
8. D-robustness check completed with go/no-go recorded (Stage 1.4)
9. All four enrichment tests run with both nulls (Stage 1.6)
10. Confirmation estimator enrichment check completed
11. Named pair table produced with prediction column
```

### Good

All adequate plus:
```
12. Neuropeptide enrichment significant (p < 0.05) under degree-preserving null
    in CePNEM residual coordinates
13. Enrichment survives CePNEM residualization (interpretation = row 1 or row 2 of table)
14. D-robustness passes (Spearman ≥ 0.7 across all D models)
15. Primary figure complete with all 6 panels
16. LOO identifies no animal driving > 30% of top-50
```

### Best case

All good plus:
```
17. Enrichment significant under degree-preserving null in BOTH coordinates (row 1)
18. Randi unc-31-sensitive enrichment also significant (independent validation)
19. Confirmation estimator AUROC within 0.10 of discovery estimator (circularity addressed)
20. Named pairs include ≥ 5 pairs with both peptide and randi_dcv annotations
    (convergent evidence from independent sources)
21. Clear separation in the AUROC curve between annotated and unannotated pairs
```

---

## Failure modes to diagnose before changing anything

**All Class 4 pairs have ΔQ ≈ 0:**
- Check that Q_roam and Q_dwell actually differ (print ||Q_roam - Q_dwell||_F)
- Check that stability selection is not over-regularizing (all edges pruned)
- Check that the behavioral segmentation is producing distinct epochs (not mixing states)
- Check that CePNEM residualization did not remove all state-dependent structure
  (compare to raw GCaMP ΔQ)

**Enrichment fails under degree-preserving null but passes simple permutation:**
- This suggests the signal is driven by hub neurons appearing in both the ΔQ ranking
  and the neuropeptide connectome by virtue of degree, not by neuropeptide-specific biology
- Report as a degree artifact; do not claim neuropeptide enrichment
- Check which specific neurons drive the discrepancy

**CePNEM residualization eliminates the signal (row 3 or 4 of interpretation table):**
- This is not a failure — it is an interpretive finding
- If raw GCaMP shows enrichment but CePNEM does not: the state-switching structure
  is behavior-mediated (different motor patterns → different covariance → different precision)
- Report honestly; this constrains what the framework can claim in C. elegans

**D-robustness fails:**
- This means the top-ranked pairs depend on which D model is used
- The current-velocity bridge (D_C ΔQ) is not interpretable
- The main claim rests on ΔQ alone (which does not require D)
- Report the discrepancy and which D model disagrees

**LOO sensitivity shows one influential animal:**
- Identify the animal; check its recording quality, epoch durations, and neuron coverage
- Recompute enrichment with that animal excluded
- If enrichment disappears when one animal is removed: the result is fragile; report as such

**Precision estimation does not converge:**
- Increase ADMM max iterations for anatomy-guided lasso
- Check condition number of Σ_s — very high condition number indicates near-singular
  covariance (too few effective samples or near-collinear neurons)
- If persistent: fall back to blockwise analysis and report the descoping

---

## Minimum viable success for Phase 1

Phase 1 succeeds if it produces:

1. State-conditioned precision matrices in CePNEM residual coordinates for both
   roaming and dwelling
2. A classified ΔQ with Class 4 pairs ranked by |ΔQ| × stability
3. A neuropeptide enrichment AUROC with p-value from degree-preserving null
4. A coordinate comparison applying the locked interpretation rule
5. A named pair table ready for Phase 4 experimental predictions

This is sufficient to state: "We applied the current-velocity diagnostic framework to
whole-brain calcium imaging of freely behaving C. elegans. After CePNEM residualization
to remove behavioral encoding, the state-switched conditional-dependence structure between
roaming and dwelling, classified against the synaptic connectome, shows [significant /
non-significant] enrichment for neuropeptide signaling in off-connectome neuron pairs."

That sentence — with the specific numbers filled in — is the scientific output of Phase 1.