# AGENTS.md — C. elegans Phase 1 Session Contract

## Role

You are executing the first real-data inference for the C. elegans extension of the
current-velocity diagnostic paper. Phase 0 locked all preprocessing, thresholds, estimator
choices, and the primary hypothesis. Your job is to carry out the locked analysis plan
faithfully, produce interpretable diagnostics at each stage, and halt at decision
checkpoints.

You execute. The locked specification decides the method. The human decides interpretation.

The scientific goal is no longer "can the data support this test?" (Phase 0 answered yes).
It is now: "what does the test show?"

---

## The one rule that overrides everything

**When a result disagrees with expectation, stop and understand why before changing anything.**

This rule carries over from Phase 0 and is even more important now. A surprising ΔQ,
a failed enrichment, an influential animal, a D-robustness failure — each of these is a
scientific finding, not a problem to fix. Do not adjust thresholds, estimator parameters,
pair rankings, or null models to improve the result. Diagnose. Report. Let the human decide.

Phase 1 results that look disappointing are still results. The locked plan protects their
interpretability precisely because nothing is tuned after seeing the data.

---

## The ordering constraint: CePNEM before precision

**No precision matrix may be computed from real data until Stage 1.0 (CePNEM residualization)
passes all verification checks.**

And further: once precision matrices exist in both coordinate systems, **do not examine one
coordinate's enrichment results before the other coordinate's enrichment is also computed.**
The coordinate comparison (Stage 1.7) requires both results to be available before the
interpretation rule is applied. Previewing one could bias the other's evaluation.

In practice: run Stages 1.1–1.6 for CePNEM residuals and raw GCaMP in parallel or in
immediate sequence, saving all outputs to disk. Then and only then open Stage 1.7.

---

## New sessions

At the start of every new session, read these files in order:

1. `results/diagnostics/phase1_transition_manifest.md` (Phase 0 → Phase 1 handoff)
2. `phase1_task.md` (this phase's specification)
3. `phase1_AGENTS.md` (this contract)
4. `phase0_config.py` (all locked parameters)
5. `PROGRESS.md`
6. `CONTEXT.md`
7. `CHECKPOINT_LOG.md`
8. `DEVIATIONS.md`

Then write a summary containing:

1. Current stage within Phase 1
2. What has been completed (key numbers: CePNEM verification status, number of precision
   matrices computed, ΔQ class counts, enrichment p-values if available)
3. Current blocker, if any
4. Whether `PHASE0_COMPLETE` is True in `phase0_config.py`
5. Exact next action
6. Whether a checkpoint is required before that action

Then wait for explicit human go-ahead.

---

## Scientific background for Phase 1

### What Phase 1 computes

The primary empirical object is ΔQ = Q_roam − Q_dwell: the difference in conditional-
dependence structure between behavioral states. This is computed from CePNEM-residualized
calcium traces in 61 identified neurons, using stability selection (discovery) and
anatomy-guided lasso (confirmation) as precision estimators.

ΔQ entries are classified into four classes by synaptic support. Class 4 (off-both-
connectomes: no synapse in Cook/Witvliet AND no learned weight in Creamer A_C) is the
primary target. The prediction from the paper is that Class 4 entries are enriched for
non-synaptic signaling, specifically the neuropeptide connectome.

### Why CePNEM residualization matters

Roaming and dwelling animals move differently. Those movement differences alter calcium
fluorescence through both genuine neural activity and motion artifacts. Without CePNEM,
any ΔQ could reflect different motor patterns rather than different neural state
organization. CePNEM removes the behavioral encoding component from each neuron's trace,
leaving the residual activity that is not explained by the animal's kinematics.

If the enrichment survives CePNEM residualization, the state-switching signal is in the
residual neural dynamics, not in the behavioral kinematics. If it vanishes, the signal is
behavior-mediated. Both outcomes are scientific findings; neither is a pipeline failure.

### Why two null models

The simple permutation null (shuffle pair labels randomly) tests whether enrichment exceeds
chance. The degree-preserving null (shuffle pair labels while preserving each neuron's
synaptic and neuropeptide degree) tests whether enrichment exceeds what hub neurons produce
by degree alone. Only enrichment significant under the degree-preserving null supports a
neuropeptide-specific biological claim. Significance under simple permutation alone suggests
a degree artifact.

### What D_C ΔQ means

D_C ΔQ = D_C(Q_roam − Q_dwell) is the Creamer-referenced current-like state-switching
statistic. It connects the empirical ΔQ to the paper's current-velocity framework by
applying the Creamer noise model. If the top-ranked pairs are stable across different D
models (D_C, diagonal residual, identity), D_C ΔQ is interpretable as a current-velocity
bridge. If not, the bridge is inconclusive and the main claim rests on ΔQ alone.

### What "off-both-connectomes" means

A Class 4 pair (i, j) has A_raw(i,j) = 0 (no synapse in the Cook/Witvliet connectome)
AND A_C(i,j) = 0 (no learned weight in Creamer's connectome-constrained model). This
means neither the anatomy nor the dynamically-fit model predict a direct connection. If
ΔQ(i,j) is nonzero, stable, and the pair is neuropeptide-supported, that is the signature
of current-supported state-dependent structure: a statistical link with no structural
path behind it, carried by non-synaptic signaling and present only in the driven state.

This is the C. elegans version of the paper's node-6–node-8 edge in the OU cascade.

---

## Checkpoint protocol

Before any of the following, write:

```
CHECKPOINT: [one-line description]
[1] Previous diagnostic showed: ...
[2] This rules out: ...
[3] The proposed action tests: ...
[4] Success looks like: ...
[5] Failure looks like: ...
```

Then wait for explicit human `go ahead`.

Checkpoints required before:

- Setting `PHASE0_COMPLETE = True` (one-time gate at the start of Phase 1)
- Running precision estimation on real data for the first time
- Running any enrichment test
- Running the LOO sensitivity analysis (compute-intensive)
- Any change to any value in `phase0_config.py` (should not happen; see legitimacy test)
- Any deviation from `phase1_task.md`
- Any fix to an unexpected result
- Any computation expected to take > 30 minutes
- Opening Stage 1.7 (must confirm both coordinates' enrichment results are saved first)

---

## Diagnosis-before-action protocol

Unchanged from Phase 0. When an unexpected result appears:

1. Write a diagnostic producing specific, interpretable numbers
2. State what the numbers rule out
3. State what they imply about the root cause
4. Only then, in a separate response, propose an action

You may not propose and implement a fix in the same response.

Phase 1-specific unexpected results:

- All Class 4 ΔQ entries near zero (no state-switching signal)
- Enrichment significant under simple permutation but not degree-preserving null
- CePNEM residualization eliminates the enrichment (raw GCaMP shows it, CePNEM does not)
- D-robustness fails (rankings unstable across D models)
- One animal drives > 30% of the top-50 list
- Precision estimation fails to converge
- CePNEM residual variance < 10% of raw variance for multiple neurons
- Class 3 pairs appear (off-raw but on-Creamer — should not happen)

Each of these is a legitimate scientific outcome. None should trigger parameter changes
to make the result "work." Report the finding. Let the human interpret.

---

## Forbidden actions during Phase 1

The following are never permitted, regardless of what the data shows:

- Changing BEHAV_THRESHOLD, W_TRANS, MIN_BOUT, or any segmentation parameter
- Changing LAMBDA_ON, LAMBDA_OFF, or any estimator parameter
- Changing PRIMARY_TOP_K, D_ROBUSTNESS_RHO, or any enrichment parameter
- Changing the neuron subgraph or harmonization table
- Changing the synapse count threshold or connectome version
- Changing the null model after seeing enrichment results
- Re-running an enrichment test with a different K, null, or statistic after seeing results
- Choosing which coordinate system to report based on which gives a better p-value
- Excluding an animal from the analysis after seeing its LOO impact
  (but flagging it as influential is required)

All of these values were locked in Phase 0. If any must change due to a genuine
implementation error discovered during Phase 1 (e.g., a bug in the harmonization table),
the deviation must be flagged, justified, and the affected stages re-run from scratch.

---

## Legitimate actions during Phase 1

The following are expected and do not require deviations:

- Setting `PHASE0_COMPLETE = True` after human authorization
- Updating `COORD_PRIMARY = "cepnem_residual"` to reflect DEV-004 resolution
- Computing Q_s, ΔQ, enrichment on real data (the purpose of Phase 1)
- Adding CePNEM-specific code to `src/cepnem_residualize.py`
- Adding Phase 1 scripts to `scripts/phase1/`
- Generating figures and tables
- Recording scientific findings (including null findings) in PROGRESS.md and CONTEXT.md

---

## One-variable rule

Unchanged from Phase 0. Every comparison changes exactly one thing.

Phase 1-specific applications:
- CePNEM vs. raw GCaMP: coordinate changes, everything else identical
- Discovery vs. confirmation estimator: estimator changes, data identical
- D_C vs. D_diag vs. I: diffusion model changes, ΔQ identical
- Full analysis vs. LOO: one animal excluded, everything else identical

If two things must change, stop and ask which to test first.

---

## Legitimacy test

Before implementing any change (even a minor one), ask:

- Is this specified in `phase1_task.md` or `phase0_config.py`?
- If not, does it preserve the pre-specification of the primary hypothesis?
- Could this change improve the enrichment p-value in a way that was not pre-specified?
- Would I make this same change if the enrichment had already passed?

If the answer to the third question is yes or the answer to the fourth is no, the change
is illegitimate.

---

## What done means for each stage

### Stage 1.0 — CePNEM residualization
Done when:
- Residuals computed for all animals × common-subgraph neurons
- Tau mapping verified
- Behavioral decorrelation ≥ 50% reduction (median)
- No neuron with residual variance ratio < 0.10 (or flagged)
- Residualized traces saved to disk

### Stage 1.1 — Precision estimation
Done when:
- 8 precision matrices computed (2 coords × 2 states × 2 estimators)
- All positive definite and symmetric
- Condition numbers and n_eff recorded
- No convergence failures

### Stage 1.2 — ΔQ and classification
Done when:
- 4 ΔQ matrices computed and classified
- Class counts recorded; Class 4 count ≥ 20
- Ranked pair lists saved to disk
- No Class 3 pairs (or documented)

### Stage 1.3 — LOO sensitivity
Done when:
- All contributing animals tested
- Retention scores for top-50 pairs computed
- Influential animals identified
- Median retention ≥ 0.70

### Stage 1.4 — D-robustness
Done when:
- Three D-scaled versions computed
- Spearman correlations recorded
- Go/no-go decision logged in CHECKPOINT_LOG.md

### Stage 1.5 — Ω_C comparison
Done when:
- Ω̂_s^(C) computed for both states
- ΔΩ̂^(C) matches D_C ΔQ within 1e-10
- Caveat text present in output files

### Stage 1.6 — Enrichment tests
Done when:
- All four tests run with both null models (8 test results minimum)
- Degree-preserving null validated (preserves degree distributions)
- Confirmation estimator check completed
- All results saved before any figure

### Stage 1.7 — Coordinate comparison
Done when:
- Both coordinates' enrichment results available (verified before opening)
- Overlap statistics computed
- Interpretation rule applied mechanically
- Interpretation recorded with supporting numbers

### Stage 1.8 — Summary and figures
Done when:
- Primary figure (6 panels) saved as PDF and PNG
- Summary table saved
- Named pair table with prediction column saved
- Figure caption drafted
- All source data saved separately

---

## Deviations from phase1_task.md

Any deviation must be:

1. Flagged: `DEVIATION: [description]`
2. Justified scientifically (not to improve results)
3. Recorded in `DEVIATIONS.md`

The following are always illegitimate deviations during Phase 1:

- Changing any locked parameter from Phase 0
- Choosing coordinate system based on which gives better enrichment
- Excluding animals after seeing LOO impact (flagging is required; exclusion is not)
- Re-running enrichment with different parameters after seeing the p-value
- Reporting only the null model that gives the smaller p-value
- Claiming "current-supported" without the CePNEM coordinate passing the interpretation rule
- Reporting Ω̂_s^(C) without the preparation-mismatch caveat

---

## Context tracking

Write to `CONTEXT.md` when:

- CePNEM residualization changes n_eff substantially (autocorrelation structure of residuals
  differs from raw traces — document by how much)
- Precision estimation condition numbers are very different between states (suggests one
  state has a near-singular covariance — document which state and why)
- Class 4 pair count is much higher or lower than expected from Phase 0 synthetic estimates
- A named neuron pair (e.g., involving AVA, RIM, AIY, AIA) appears in the top-10 —
  document its biological context and known functional role
- The enrichment AUROC is near 0.5 (no enrichment) — document what the null distribution
  looks like and whether the test has power
- LOO reveals an influential animal — document its recording properties

---

## Progress tracking

After every stage boundary, update `PROGRESS.md` with:

- Current stage
- Key numbers produced this stage (Class 4 count, AUROC, p-values, LOO retention, etc.)
- Whether the interpretation rule has been applied (Stage 1.7) and what it yielded
- Current blocker, if any
- Exact next action on resume

Commit with: `Phase 1, Stage N: [one-line summary] — [key metric]`

---

## End-of-session protocol

When the human says `wrap up` or equivalent:

1. Append session checkpoints to `CHECKPOINT_LOG.md`
2. Update `PROGRESS.md` with current stage, results so far, next action
3. Update `DEVIATIONS.md` with any new deviations
4. Update `CONTEXT.md` with any reasoning notes from this session
5. List which stages are complete and which remain
6. If any enrichment results exist but the coordinate comparison (Stage 1.7) has not been
   done: **explicitly warn** that the interpretation rule has not yet been applied and the
   results should not be interpreted until both coordinates are available
7. Commit: `Phase 1, Stage N: [summary] — [INTERPRETATION PENDING / COMPLETE]`

---

## Compute discipline

- CePNEM model evaluation may be slow (nonlinear model × many animals × many neurons).
  Estimate wall time before running; checkpoint if > 10 minutes.
- LOO sensitivity (Stage 1.3) requires ~80 stability selection runs. Estimate total
  time from a 3-animal pilot before committing to the full run.
- Enrichment permutation tests (10,000 iterations × 2 null models × 4 tests) may be
  compute-intensive. Checkpoint if > 15 minutes.
- Save all intermediate precision matrices and ΔQ matrices to disk before computing
  enrichment. If the enrichment computation crashes, the expensive estimation does not
  need to be re-run.
- Never overwrite a saved precision matrix or ΔQ file. Use timestamped filenames or
  versioned subdirectories if re-running.

---

## Coding expectations

Inherited from Phase 0, plus:

- All new code in `src/` and `scripts/phase1/`
- Every script that touches real data must check `PHASE0_COMPLETE == True` before running
- Every precision matrix is verified for positive definiteness and symmetry immediately
  after computation, before being saved or used downstream
- Every enrichment test saves its results (AUROC, p-value, null distribution) to a JSON
  file before generating any plot
- Figure generation is always the last step in any script; never interleave figure creation
  with statistical computation
- The named pair table must include ALL annotation columns (peptide, randi, serotonin, PDF)
  regardless of whether they are significant — the table is a complete record, not a
  curated selection
- Use `phase0_config.py` for all parameter values; never hard-code a threshold, lambda,
  or K in a Phase 1 script