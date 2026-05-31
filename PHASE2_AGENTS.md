# PHASE2_AGENTS.md — C. elegans Phase 2 Session Contract
## Missing-Data-Aware Precision Estimation

---

## Role

You are implementing a pairwise available-case precision estimation pipeline for C. elegans
whole-brain calcium imaging data where recording-level neuron missingness prevents
complete-case analysis. Phase 1 established that the intended 61-neuron analysis is not
constructible under the validated complete-case estimator. Phase 2 replaces the estimation
object — from a dense T × N data matrix to a pairwise-assembled, PSD-projected covariance
matrix — while preserving every other component of the analysis.

Your immediate job is Stage 0: characterize the missingness, specify the estimator, and
validate it on synthetic data. Real-data estimation is prohibited until Stage 0-V passes
and the human authorizes Stage 1.

---

## The one rule that overrides everything

**When a result disagrees with expectation, stop and understand why before changing anything.**

This rule now applies specifically to the pairwise estimation methodology. The pairwise
approach introduces new failure modes that do not exist in complete-case estimation:
non-PSD covariance matrices, heterogeneous per-pair sample sizes, instability under
recording-level resampling, and PSD projection artifacts. Each of these is a diagnostic
signal, not a parameter to tune away. When the assembled covariance has 15 negative
eigenvalues instead of the expected 3, that tells you something about the data structure.
Diagnose it before adjusting the eigenvalue floor.

---

## Mandatory reading at session start

Before any work, read ALL of the following in order:

1. `phase2_task.md` — Phase 2 specification
2. `PHASE2_AGENTS.md` — this contract
3. `docs/phase1_archive/PHASE1_CLOSURE_REPORT.md` — why Phase 1 closed
4. `phase2_config.py` — current Phase 2 parameters
5. `phase0_config.py` — inherited locked parameters
6. `docs/phase0/hypothesis_lock.md` — original hypothesis
7. `docs/phase2/PHASE2_DESIGN_DECISIONS.md` — Phase 2 design decisions
8. `PHASE2_CHECKPOINT_LOG.md` — if it exists
9. `PROGRESS.md`
10. `CONTEXT.md`
11. `DEVIATIONS.md`

Then summarize:

1. Current stage within Phase 2
2. Whether PHASE2_ACTIVE is True or False
3. What Stage 0 steps are complete (co-observation characterization, estimator specification,
   which validation stages have passed)
4. Key numbers: median co-observation count, PSD clipping fraction (synthetic), TPR
5. Current blocker
6. Exact next action
7. Whether a checkpoint is required

Wait for human go-ahead before proceeding.

---

## The absolute constraints

### Constraint 1 — No real-data precision before Stage 0-V

**Forbidden until PHASE2_ACTIVE = True:**
- Computing Q_s from real behavioral data (any method)
- Computing ΔQ from real data
- Computing any enrichment statistic from real ΔQ
- Assembling a pairwise covariance matrix from real data for the purpose of precision
  estimation (assembling it for co-observation characterization in Stage 0.1 is permitted,
  but only the covariance itself, not its inverse)

**Permitted before PHASE2_ACTIVE:**
- Co-observation structure characterization (Stage 0.1)
- Synthetic data generation and validation (Stage 0-V)
- Literature review (Stage 0.2)
- Estimator specification and API design (Stage 0.3)

### Constraint 2 — No methodology change after seeing results

Once Stage 1 begins, the following are frozen and cannot change:
- PSD_EIGENVALUE_FLOOR
- STABILITY_THRESHOLD
- N_BOOTSTRAP_RESAMPLES
- LAMBDA_ON, LAMBDA_OFF
- PRIMARY_TOP_K
- MIN_COPRESENCE_RECORDINGS
- The enrichment null models
- The coordinate interpretation table

### Constraint 3 — Inherited behavioral segmentation is locked

The following parameters are inherited from Phase 0 and must not change:
- BEHAV_THRESHOLD = 0.284
- EWMA_TIMESCALE_SECONDS = 20.0
- W_TRANS_SECONDS = 10.0
- MIN_BOUT_SECONDS = 10.0
- SYNAPSE_COUNT_THRESHOLD = 1
- NORMALIZATION = "z_score_global"
- LR_POLICY = "separate"

These were determined from the CePNEM behavioral score distribution without reference
to any neural output. Changing them in Phase 2 would retroactively invalidate the
pre-specification.

---

## Scientific background for Phase 2

### Why pairwise estimation works for this data

The SF corpus has 40 recordings, each identifying ~55–61 of the 61-neuron subgraph (with
a different random subset of ~0–6 neurons missing per recording). Any single neuron is
present in ≥ 80% of recordings. Any pair of neurons is co-present in roughly 60–85% of
recordings. But the intersection of ALL 61 neurons across multiple recordings collapses
rapidly because each recording is missing different neurons.

The pairwise approach exploits the high per-pair coverage while avoiding the intersection
collapse. For each pair (i, j), the sample covariance is computed from all recordings where
both i and j are identified. This per-pair estimate is unbiased under MCAR (confirmed by
the Phase 1 audit — missingness is driven by optical resolution under motion, not by neural
signal content).

### Why the assembled matrix may not be PSD

Each entry of the assembled covariance matrix S_pairwise is computed from a different subset
of recordings (the subset where both neurons in that pair are present). Because different
entries use different data, the matrix is not guaranteed to satisfy the positive
semi-definiteness constraint that any true covariance matrix must satisfy. In finite samples,
this manifests as a small number of negative eigenvalues, typically small in magnitude.

The PSD projection (clipping negative eigenvalues to a positive floor) introduces a small
bias but restores the mathematical property needed for the graphical lasso. The bias is
characterized in Stage 0-V validation: if the projection preserves the rank ordering of
off-diagonal entries (which is what the enrichment test uses), the downstream analysis is
valid even though individual entry magnitudes are slightly altered.

### Why stability selection uses recording-level resampling

In complete-case estimation, stability selection resamples frames (or animals) and
re-estimates the precision matrix on each subsample. In pairwise estimation, resampling
recordings is the natural unit because:

1. Each recording has a different co-observation structure (different neurons present).
   Resampling recordings produces genuinely different pairwise covariance matrices,
   testing stability across the co-observation variability in the data.

2. Resampling frames within a recording does not change which neurons are observed —
   it only changes the within-recording temporal statistics. This misses the
   recording-level uncertainty that dominates the pairwise assembly.

3. Recording-level resampling preserves within-recording temporal autocorrelation,
   avoiding artificial inflation of effective sample sizes.

The consequence: each bootstrap subsample has a different set of per-pair co-observation
counts, a different co-observation graph, and potentially a different PSD projection.
This is expected and is the source of stability assessment.

### What ΔQ means in the pairwise framework

ΔQ = Q_roam − Q_dwell is computed from precision matrices estimated via the pairwise
pathway. Each Q_s is the graphical lasso solution applied to a PSD-projected pairwise
covariance matrix. The interpretation is the same as in Phase 1 — state-switched
conditional-dependence structure — but the estimation pathway is different and introduces
a PSD projection step that was absent in the complete-case pipeline.

The key validity condition: if the PSD projection preserves the rank ordering of
off-connectome ΔQ entries (verified in Stage 0-V.2 and 0-V.3), the enrichment test
is valid because it uses ranks, not magnitudes.

### What the circularity control means in Phase 2

The circularity concern from Phase 1 carries forward: the anatomy-guided lasso uses the
connectome to set differential penalties, then the enrichment test classifies entries
against the same connectome. In Phase 2, the pairwise assembly adds a second layer:
per-pair co-observation counts might correlate with connectome structure (neurons that
are often co-observed might also be synaptically connected). If so, the pairwise
assembly could introduce a subtle bias that inflates or deflates specific entries based
on co-observation rather than neural signal.

Stage 0-V.6 tests this explicitly. The circularity control requires that the
confirmation estimator (anatomy-guided lasso with heavy off-connectome penalty) selects
true-positive off-connectome entries at ≥ 0.7 rate and true-negative entries at ≤ 0.05
rate, under the synthetic missingness pattern.

---

## Checkpoint protocol

Every substantive action requires a preceding checkpoint entry in PHASE2_CHECKPOINT_LOG.md.

```
CHECKPOINT P2-NNN: [one-line description]
Date: YYYY-MM-DD
Stage: [current stage]
[1] Previous diagnostic showed: ...
[2] This rules out: ...
[3] The proposed action tests: ...
[4] Success: ...
[5] Failure: ...
Authorization: [PENDING / AUTHORIZED by human / SELF-AUTHORIZED for minor computation]
```

**Actions requiring human authorization:**
- Setting MIN_COPRESENCE_RECORDINGS (after Stage 0.1)
- Authorizing the estimator specification (after Stage 0.3)
- Setting PHASE2_ACTIVE = True (after Stage 0-V.8)
- Beginning any real-data estimation (Stage 1+)
- Any deviation from phase2_task.md
- Any change to any locked parameter

**Actions self-authorizable** (record checkpoint but may proceed without waiting):
- Running a synthetic validation sub-stage within Stage 0-V
- Computing co-observation statistics (Stage 0.1)
- Writing unit tests
- Generating diagnostic plots from synthetic data

---

## Diagnosis-before-action protocol

Unchanged from Phase 1. When an unexpected result appears:

1. Write a diagnostic with specific numbers
2. State what the numbers rule out
3. State the root cause implication
4. Do NOT propose a fix in the same response
5. Wait for human authorization

Phase 2-specific unexpected results:

- PSD projection clips > 15% of eigenvalues on synthetic data (expected: ≤ 5–10%)
- Stability selection gives stability < 0.3 for all edges (no stable structure detected)
- TPR on synthetic data < 0.4 at effect size 0.2 (estimator underpowered)
- Type-I error > 0.08 on synthetic null data (enrichment test miscalibrated)
- Co-observation graph is disconnected (some pairs never co-observed)
- Recording-level resampling produces wildly different co-observation structures
  across bootstrap iterations (some iterations have pairs with 0 co-observations)
- Real-data PSD clipping is > 2× the synthetic baseline
- Any convergence failure in the ADMM solver on projected covariance

---

## One-variable rule

Unchanged. Every experiment changes exactly one thing.

Phase 2-specific applications:
- PSD floor sweep: vary PSD_EIGENVALUE_FLOOR, hold everything else constant
- Lambda sweep: vary LAMBDA_ON (with fixed ratio to LAMBDA_OFF), hold PSD method constant
- Resampling unit: compare recording-level vs frame-level, hold estimator constant
- Co-observation threshold: vary MIN_COPRESENCE_RECORDINGS, hold estimator constant
- Synthetic vs real: same pipeline, only input data changes (Stage 0-V → Stage 1 transition)

---

## Legitimacy test

Before implementing any change:

- Is this specified in phase2_task.md or phase2_config.py?
- Does it change the statistical object (from pairwise covariance to something else)?
- Could it improve the enrichment p-value in a way not pre-specified?
- Would I make this change if the synthetic validation had already passed?
- Does it introduce a new assumption about the missingness structure?

The following changes are always illegitimate during Phase 2:

- Switching back to complete-case estimation after seeing pairwise results
- Changing the PSD projection method after seeing real-data eigenvalue spectra
- Adjusting STABILITY_THRESHOLD after seeing real-data stability distributions
- Re-calibrating PRIMARY_TOP_K after seeing real-data enrichment direction
- Excluding specific neuron pairs from the analysis after seeing their ΔQ values
- Imputing missing data (the pairwise approach avoids imputation by design;
  introducing imputation changes the statistical object)

---

## What done means for each stage

### Stage 0.1 — Co-observation characterization
Done when:
- Per-pair co-observation counts computed for both states
- Co-observation graph properties documented (connected, degree distribution)
- Fragile pairs identified (below MIN_COPRESENCE threshold)
- n_eff per pair per state computed
- Summary saved to results/phase2/stage0/copresence_report.json
- Human checkpoint completed: MIN_COPRESENCE_RECORDINGS set

### Stage 0.3 — Estimator specification
Done when:
- Literature review documented in PHASE2_DESIGN_DECISIONS.md
- Pairwise estimation pipeline specified (5-step procedure in task.md)
- API for pairwise_covariance.py, psd_projection.py, pairwise_estimators.py designed
- Human checkpoint completed: estimator authorized

### Stage 0-V (all sub-stages)
Done when:
- Synthetic data generator implemented and tested
- All 7 validation stages pass their specified criteria
- All parameters locked in phase2_config.py
- Validation summary written
- All unit tests pass
- Human checkpoint completed: PHASE2_ACTIVE = True

### Stage 1 — Pairwise estimation
Done when:
- 8 precision matrices computed (2 coords × 2 states × 2 estimators)
- All positive definite and symmetric
- PSD clipping within 2× synthetic baseline
- Pairwise covariance matrices saved (pre-projection)
- All diagnostics recorded

### Stage 2 — ΔQ and classification
Done when:
- 4 ΔQ matrices computed and classified
- Class 4 count ≥ 30
- Ranked pair lists saved

### Stage 3 — Sensitivity
Done when:
- LOO completed; median retention ≥ 0.70
- D-robustness go/no-go recorded
- Ω_C comparison saved with caveat

### Stage 4 — Enrichment
Done when:
- All tests run with both nulls
- Confirmation estimator check completed
- All results saved before figures

### Stage 5 — Coordinate comparison
Done when:
- Both coordinates' results available before evaluation
- Interpretation rule applied mechanically
- Interpretation recorded

### Stage 6 — Summary
Done when:
- Full figure (7 panels including PSD diagnostic) saved
- Summary table and named pair table saved
- All source data saved

---

## Deviations

Any deviation from phase2_task.md:

1. Flag: `DEVIATION P2: [description]`
2. Justify scientifically
3. Record in DEVIATIONS.md as DEV-P2-NNN
4. Obtain human authorization before implementation

Always illegitimate:
- Changing any inherited Phase 0 behavioral segmentation parameter
- Switching estimation methodology after seeing real-data results
- Imputing missing values
- Excluding neuron pairs post-hoc based on their ΔQ values
- Reporting only the null model with the smaller p-value
- Omitting the PSD diagnostic panel from the figure

---

## Context tracking

Write to CONTEXT.md when:

- Co-observation counts are unexpectedly low for specific pairs (document which and why)
- PSD projection eigenvalue spectrum reveals structure (e.g., a gap between positive and
  negative eigenvalues suggesting the matrix is "almost PSD" vs "far from PSD")
- Stability selection stability scores are bimodal (some edges always selected,
  others never) — document the separation
- A named neuron pair (AVA, RIM, AIY, AIA) appears in the top-ranked ΔQ — document
  its biological context
- Recording-level resampling produces bootstrap iterations where specific pairs lose
  all co-observations — document frequency and which pairs
- Real-data PSD clipping differs qualitatively from synthetic — document the difference

---

## Progress tracking

After every stage boundary and every human checkpoint, update PROGRESS.md with:

- Current stage
- Key numbers (co-observation median, PSD clipping fraction, synthetic TPR,
  real-data Class 4 count, AUROC, p-values as available)
- Whether PHASE2_ACTIVE is True
- Current blocker
- Exact next action on resume

Commit with: `Phase 2, Stage X.Y: [summary] — [key metric]`

---

## End-of-session protocol

When the human says `wrap up`:

1. Append session checkpoints to PHASE2_CHECKPOINT_LOG.md
2. Update PROGRESS.md
3. Update DEVIATIONS.md
4. Update CONTEXT.md
5. List which Stage 0 validation steps remain
6. If any real-data outputs exist but Stage 5 (coordinate comparison) is incomplete:
   warn that interpretation is pending
7. Commit: `Phase 2, Stage X.Y: [summary] — [VALIDATION / INFERENCE / PENDING]`

---

## Compute discipline

- Synthetic validation is the primary computational load in Stage 0-V. Each validation
  sub-stage involves ~100–200 synthetic replications × graphical lasso fits. Estimate
  wall time before running; checkpoint if > 20 minutes per sub-stage.
- Stage 1 LOO sensitivity requires ~40 × pairwise assembly + PSD projection + stability
  selection. This is the most expensive computation in Phase 2. Run a 3-animal pilot first.
- Save ALL intermediate matrices (pairwise S, eigenvalue spectra, PSD-projected S,
  Q per estimator) to disk before downstream computation. If any step fails, earlier
  expensive computations do not need to be re-run.
- Never overwrite a saved matrix. Use stage-labeled filenames or versioned directories.

---

## Coding expectations

Inherited from Phase 1, plus:

- `pairwise_covariance.py` must track per-pair co-observation metadata alongside
  covariance values. Every entry in the assembled S must have an associated
  n_recordings and n_eff. These are needed for diagnostics and for the PSD
  projection assessment.
- `psd_projection.py` must return both the projected matrix AND a diagnostic object
  containing: original eigenvalues, projected eigenvalues, number clipped, total
  spectral mass removed. Every call to PSD projection must produce this diagnostic.
- The ADMM solver in `pairwise_estimators.py` must accept a pre-computed S matrix
  (not compute np.cov internally). Verify that the solver produces identical output
  to the Phase 0/1 ADMM when given the same S matrix as np.cov would produce on
  complete-case data.
- Unit tests must include a "round-trip" test: generate complete-case Gaussian data,
  compute both np.cov and pairwise covariance (which are identical when data is
  complete), verify identical graphical lasso output. This confirms the pairwise
  pathway reduces to the complete-case pathway when no data is missing.
- All random seeds from phase2_config.py. Record seeds in every output file header.