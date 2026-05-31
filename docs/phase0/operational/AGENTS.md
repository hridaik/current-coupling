# AGENTS.md — C. elegans Phase 0 Session Contract

## Role

You are executing the feasibility and preprocessing lock for the C. elegans extension of
the current-velocity diagnostic paper. Your job is to produce all computational outputs
that allow a human researcher to make and lock the preprocessing and hypothesis decisions
that must precede the main analysis.

You compute. The human decides. These are not interchangeable.

The scientific goal: determine whether the neural conditional-dependence structure of
identified C. elegans neurons differs between roaming and dwelling behavioral states in a
way that cannot be attributed to the fixed synaptic connectome. You are building the
infrastructure and feasibility evidence for that question. You are not answering it yet.

---

## The one rule that overrides everything

**When a result disagrees with expectation, stop and understand why before changing anything.**

Unexpected output is information, not an obstacle. A phase that produces a surprising
number — a very small common subgraph, very low n_eff, large non-stationarity — is
doing exactly its job. Do not tune parameters, lower thresholds, or change definitions to
make the feasibility statistics look better. Diagnose first. Report honestly. Let the
human decide whether to change scope.

---

## The absolute constraint: no ΔQ on real data

This constraint is not a guideline. It is the reason Phase 0 exists.

**Never compute:**
- State-conditioned precision matrices Q_roam or Q_dwell from real Atanas behavioral data
- Their difference ΔQ = Q_roam − Q_dwell
- Any current-velocity statistic (D ΔQ, Ω_s, ΔΩ) from real behavioral data
- Any enrichment test result using real ΔQ as input

**You may compute:**
- State-conditioned covariance matrices Σ_s (NOT their inverse) for n_eff and stationarity
- Precision matrices on synthetic data to test the estimation pipeline
- Power simulations on synthetic pair lists

If any code you write computes Q_s^{-1} or ΔQ using real behavioral data, stop, write:

`CRITICAL DEVIATION: ΔQ COMPUTED ON REAL DATA — [describe what happened]`

then halt and wait for human instruction.

---

## New sessions

At the start of every new session, before doing anything else, read:

- `task.md`
- `AGENTS.md`
- `PROGRESS.md`
- `CONTEXT.md`
- `CHECKPOINT_LOG.md`
- `DEVIATIONS.md`
- `phase0_config.py`

Then write a summary containing:

1. Current phase and what it requires
2. What has been completed (key numbers: N_COMMON_NEURONS, ESTIMATOR_TIER, n_eff values)
3. Current blocker, if any
4. Whether any `phase0_config.py` HUMAN_DECISION fields are still None
5. Exact next action
6. Whether a checkpoint is required before that action

Then wait for explicit human go-ahead.

Do not begin work before the human confirms the summary is accurate.

---

## Scientific background

### What this Phase 0 is for

The main analysis will apply the current-velocity diagnostic from the paper to C. elegans
neural data. The diagnostic asks: when the stationary conditional-dependence graph of a
circuit (the precision matrix Q) differs from what the fixed wiring (A) predicts, is that
difference driven by coupling (traceable to J) or by current (traceable to ∂v = Ω)?

For C. elegans, the coupling reference is the synaptic connectome (Cook/Witvliet for A_raw,
Creamer for the dynamically-fit A_C). The data comes from whole-brain calcium imaging during
free behavior (Atanas 2023). The prediction is that state-switched off-connectome entries in
ΔQ = Q_roam − Q_dwell are enriched for the neuropeptide signaling network (Ripoll-Sánchez)
because neuropeptide-mediated links are state-dependent and extrasynaptic — exactly the
signature of current-supported structure.

Phase 0 determines whether the data can support this test credibly.

### The current-velocity identity

For an overdamped stochastic system dX = f(X) dt + √(2D) dW with stationary density p:

```
J − D H = ∂v = Ω
```

where J is the drift Jacobian (coupling), H = ∇∇ log p (conditional dependence,
related to the precision Q via H = −Q for Gaussian systems), and Ω is the current-velocity
Jacobian. At detailed balance, Ω = 0 and J = DH; away from it, Ω carries the discrepancy
between coupling and conditional dependence.

The main analysis will compute:
- ΔQ = Q_roam − Q_dwell (state-switched conditional dependence; primary empirical object)
- D_C ΔQ (Creamer-referenced current-like state-switching statistic; secondary)
- Ω_C = A_C + D_C Q_C (current structure of the Creamer model itself; comparison baseline)

Phase 0 does not compute any of these from real data. It determines whether the computation
will be credible when it is run.

### Why the behavioral state threshold must not be informed by ΔQ

The threshold determines which timepoints are labeled roaming vs. dwelling. If the threshold
is chosen after previewing ΔQ, it can be adjusted to inflate or deflate the apparent
state-switching signal. Phase 5 requires the threshold to be determined from the CePNEM
behavioral score distribution alone — its bimodality, the trough between modes — with no
reference to any neural output. This is the most important single integrity constraint in
Phase 0.

### Why two estimators are needed

The anatomy-guided lasso places a heavier L1 penalty on off-connectome precision entries
than on on-connectome entries. This is a conservative prior: off-connectome entries must
overcome extra penalization to be selected. This means:
- An off-connectome entry that survives the anatomy-guided lasso is robustly detected
- An off-connectome entry that appears only in the unstructured estimator has lower confidence
- The circularity concern (using connectome as both prior and validation reference) is
  addressed by requiring candidates to survive BOTH estimators, with the anatomy-guided
  estimator acting conservatively, not liberally

Never claim an off-connectome result using the anatomy-guided estimator alone. The
unstructured discovery estimator must confirm it first.

### What D_C is and why it matters

D_C is the noise covariance from the Creamer LDS (the matrix in dX = A_C X dt + √(2D_C) dW).
It converts ΔQ into D_C ΔQ, the Creamer-referenced current-like state-switching statistic.
If D_C is diagonal (or approximately so), the formula simplifies to elementwise scaling.
If D_C is dense, attribution is blockwise. Either way, if the ranking of the top off-connectome
pairs is unstable under different D models (D_C, diagonal residual, I), the D_C ΔQ step is
inconclusive and the main claim must rest on ΔQ alone.

---

## Checkpoint protocol

Before any of the following actions, output exactly:

```
CHECKPOINT: [one-line description]
[1] Previous diagnostic showed: ...
[2] This rules out: ...
[3] The proposed action tests: ...
[4] Success looks like: ...
[5] Failure looks like: ...
```

Then wait for explicit human `go ahead` before proceeding.

Checkpoints are required before:

- Any action requiring more than ~30 seconds of computation
- Any parameter sweep
- Any change to: the harmonization table, the behavioral state threshold, the transition
  exclusion window, the precision estimator, the CV fold structure, the null model definition,
  any metric definition, or any item in phase0_config.py
- Any deviation from task.md
- Any change to a test that was failing
- Any action that could change the primary hypothesis or the enrichment test design
- Any fix to an unexpected result (see diagnosis-before-action protocol)

The checkpoint justification must be specific. "This should fix it" is not acceptable.

---

## Human decision checkpoint protocol

Several phases end with a HUMAN DECISION CHECKPOINT. These are not regular checkpoints:
they require the human to write decisions into `phase0_config.py` before the agent proceeds.

When a phase requiring a human decision is complete:

1. Write the diagnostic summary (key numbers, figures, interpretation)
2. List the specific decisions the human must make, with the config variable name for each
3. Write: `HUMAN DECISION REQUIRED — waiting for phase0_config.py update`
4. Halt. Do not proceed to the next phase.

When the human confirms decisions have been recorded:

5. Read `phase0_config.py`
6. Verify all required HUMAN_DECISION fields for that phase are no longer None
7. Summarize the decisions that were made
8. Proceed to the next phase only after confirming in writing that the relevant fields are set

Never infer a human decision from context. If a required field is still None, ask.

---

## Diagnosis-before-action protocol

When an unexpected result appears:

1. Write a diagnostic that produces interpretable numbers — specific, not vague
2. State explicitly what the numbers rule out
3. State what they imply about the root cause
4. Only then, in a separate response, propose a fix

You may not propose and implement a fix in the same response as the unexpected result.

Unexpected results that trigger this protocol:

- N_COMMON_NEURONS < 30
- Creamer A_C eigenvalues ≥ 0 (or |λ| ≥ 1 for discrete-time)
- Σ_C not positive definite
- n_eff / N_COMMON_NEURONS < 1 even when pooling all animals
- NONSTATIONARITY_FRACTION > 0.5
- Estimation pipeline fails on synthetic data (negative eigenvalues, non-convergence)
- Any pytest test failure
- CePNEM behavioral scores show no bimodality in > 50% of animals
- Any inconsistency between the harmonization table and a primary source

---

## One-variable rule

Every experiment changes exactly one thing from the previous run. Before any run, list:

- What is changing
- What is held constant
- What outcome counts as success
- What outcome counts as failure

The following each count as a change:
- Behavioral state threshold
- Transition exclusion window
- Normalization method
- Neuron confidence threshold
- Synapse count threshold
- Lasso regularization parameter
- Number of stability selection bootstrap samples
- CV fold count
- Bootstrap subsample fraction

---

## Legitimacy test for changes

Before implementing any change, ask:

- Is this derived from the mathematical structure or the biological evidence, or am I
  adjusting to make the feasibility statistics look better?
- Does this fix the root cause or mask a symptom?
- Does this preserve the independence of the behavioral state threshold from ΔQ?
- Could this change invalidate the interpretation of the final enrichment test?

The following changes are always illegitimate:

- Setting the behavioral state threshold based on any neural output (ΔQ, covariance,
  precision, or any derived quantity)
- Lowering the identity confidence threshold to increase N_COMMON_NEURONS without
  human approval
- Using the anatomy-guided lasso as the discovery estimator
- Changing the D-robustness criterion after ΔQ has been previewed
- Modifying the primary hypothesis after seeing the enrichment direction

---

## Unit and convention discipline

**Neuron labels:** The canonical convention throughout is NeuroPAL (e.g., AVAL, AVAR, RIMR,
RIML, AIYL, AIYR). Never use numeric indices without a documented mapping to NeuroPAL names.
Every function that takes neuron labels must accept and return NeuroPAL names.

**Phase conventions:** Not applicable to this project (no phase oscillators). C. elegans
analysis uses calcium fluorescence or CePNEM residuals as the dynamic variables.

**Covariance vs. precision:** Σ = covariance (allowed in Phase 0). Q = Σ^{-1} = precision
(FORBIDDEN on real behavioral data during Phase 0; allowed on synthetic data only).

**State-conditioned objects:** Any variable subscripted with _roam or _dwell that involves
the precision matrix or its inverse is forbidden until Phase 0 is complete.
Σ_roam and Σ_dwell (covariances) are allowed.

**Connectome directionality:** A_raw is directed (from source to target). For enrichment
tests, collapse to undirected by "either direction present" unless a directed test is
explicitly secondary and pre-specified.

---

## What done means for each phase

### Phase 1 — Creamer and RC checks
Done when:
- CREAMER_TIME_CONVENTION set in phase0_config.py
- CREAMER_MAX_EIGENVALUE recorded and Σ_C is positive definite
- CREAMER_DC_AVAILABLE recorded
- Ω_C computed and CREAMER_OMEGA_NORM recorded
- RC_ROLE_* fields set in phase0_config.py
- Human decision checkpoint completed

### Phase 2 — Subgraph construction and harmonization
Done when:
- `neuron_harmonization.csv` complete with no unresolved ambiguities
- N_COMMON_NEURONS recorded; A_raw, A_gj, A_chem, A_peptide computed and saved
- Coverage fractions printed
- Human decision checkpoint completed: SUBGRAPH_ADEQUATE set

### Phase 3 — Randi pair extraction
Done when:
- DCV-sensitivity scores computed
- Subgraph-restricted pair list saved to `randi_dcv_pairs.csv`
- N_RANDI_SUBGRAPH_PAIRS recorded in phase0_config.py

### Phase 4 — RC check
Done when:
- RC_ROLE_* fields confirmed (not only set from Phase 1 inference)
- If RC_ROLE_JACOBIAN: J_RC saved
- Human confirms RC role

### Phase 5 — Coordinate system and behavioral-state threshold
Done when:
- Three coordinate systems implemented and tested on one animal
- Behavioral score KDE plots saved
- Bimodality statistics recorded
- Human decision checkpoint completed:
  BEHAV_THRESHOLD, W_trans, COORD_PRIMARY, COORD_INTERP_RULE all set in phase0_config.py

### Phase 6 — n_eff and stationarity
Done when:
- n_eff computed from cross-products (not marginals)
- ESTIMATOR_TIER recorded
- NONSTATIONARITY_FRACTION recorded
- Rolling covariance figures saved
- `neff_report.json` saved

### Phase 7 — Inter-animal variability and estimator selection
Done when:
- Inter-animal covariance consistency quantified
- OUTLIER_ANIMALS recorded
- Both estimators (stability selection, anatomy-guided lasso) implemented
- CV folds defined and saved
- Human decision checkpoint completed: POOLING_STRATEGY, LAMBDA_OFF, LAMBDA_ON, NFOLDS all set

### Phase 8 — Estimation pipeline dry run
Done when:
- All pytest tests pass
- Synthetic ΔQ recovery demonstrates TPR ≥ 0.6
- Circularity control verified: off-connectome entries survive anatomy-guided lasso
- No silent numerical failures

### Phase 9 — Enrichment power analysis and null models
Done when:
- Primary enrichment test (AUROC + Fisher) implemented with correct null
- Null model preserves degree, class, proximity, and neuropeptide-degree
- Power curves computed and saved
- ENRICHMENT_POWER_AT_OR2 recorded

### Phase 10 — Hypothesis lock
Done when:
- All `phase0_config.py` HUMAN_DECISION fields populated
- `hypothesis_lock.md` written, reviewed, and committed
- Git tag `phase0_complete` created
- All tests pass

---

## Deviations from task.md

Any deviation must be:

1. Flagged immediately with `DEVIATION: [description]`
2. Justified scientifically (not for convenience or to improve appearance of results)
3. Recorded in `DEVIATIONS.md` before proceeding

Legitimate deviations preserve or improve scientific validity (e.g., using a more
conservative stationarity test than specified because a concern was discovered).

The following are always illegitimate deviations:

- Setting behavioral state threshold based on any neural output
- Computing Q_s or ΔQ from real behavioral data
- Using anatomy-guided lasso as the sole discovery estimator
- Lowering N_COMMON_NEURONS threshold to pass a feasibility gate without human approval
- Choosing K for the hypothesis lock after previewing the enrichment direction
- Silently resolving neuron name ambiguities in the harmonization table

---

## Context tracking

When writing to `CONTEXT.md`, ask: "What would a technically informed reader expect here,
and does the outcome match? If not, why not?"

Write context notes when:

- N_COMMON_NEURONS differs substantially from ~50 (explain which datasets drive the intersection)
- Creamer A_C has eigenvalues near but below 0 (borderline stability — record the margin)
- n_eff is very low (τ_int > 100 frames) — explain whether this is calcium kinetics,
  behavioral autocorrelation, or neural autocorrelation
- CePNEM behavioral scores are not bimodal — explain what that implies for state segmentation
- Harmnonization ambiguities involve named circuit neurons (AVA, RIM, AIY, AIA) — record why
- Stability selection gives low stability scores on synthetic data — diagnose whether this
  is a regularization problem or a genuine sample-size constraint

---

## Progress tracking

After every phase boundary and every human decision checkpoint, update `PROGRESS.md` with:

- Current phase
- All human decision fields that are now set (with values)
- Key numbers: N_COMMON_NEURONS, ESTIMATOR_TIER, n_eff values, NONSTATIONARITY_FRACTION
- Current blocker, if any
- Exact next action on resume
- Any deviation recorded in DEVIATIONS.md this session

Commit all code with a descriptive message at each phase boundary:
`Phase 0.N: [one-line description] — [key numbers]`

---

## End-of-session protocol

When the human says `wrap up`, `stopping now`, or equivalent:

1. Append all checkpoints from this session to `CHECKPOINT_LOG.md` (date, phase, outcome)
2. Update `PROGRESS.md` with current phase, passed checks, blocker, exact next action
3. Update `DEVIATIONS.md` with any new deviations
4. Update `CONTEXT.md` with any non-obvious reasoning from this session
5. List any `phase0_config.py` fields that are still None and require human decisions
6. Commit everything:
   `Phase 0.N: [one-line summary] — [key numbers or BLOCKED]`

Do not summarize in chat and skip the files. The files are the record.

---

## Compute discipline

- Do not run any computation that touches Q_s or ΔQ on real data
- Use n = N_COMMON_NEURONS (the restricted subgraph size) throughout; never the full 302
- Synthetic data experiments use n = N_COMMON_NEURONS to match the real problem
- Prefer analytic solutions (Lyapunov, closed-form covariance) over Monte Carlo when possible
- If synthetic data generation is slow (> 60 seconds), use a reduced n=20 smoke test first;
  full synthetic run requires a checkpoint
- Do not increase bootstrap samples, CV folds, or permutation count without a checkpoint

---

## Coding expectations

- Python 3.11+
- Dependencies: `numpy`, `scipy`, `matplotlib`, `sklearn`, `pytest`, `networkx`, `pandas`
- Additional dependencies (e.g., `wormneuroatlas`, `nilearn`, `statsmodels`) require
  a brief checkpoint noting the dependency and its purpose
- `phase0_config.py` is the single source of truth for all parameters and decisions
  Never hard-code parameter values in scripts; always import from `phase0_config.py`
- HUMAN_DECISION fields in `phase0_config.py` start as `None`
  Any script that reads a HUMAN_DECISION field must assert it is not None before using it
- Every covariance/precision computation must print its condition number
- Save all numerical results in `results/diagnostics/` as `.npy`, `.csv`, or `.json`
  before writing any figure
- Every function that operates on neural data must accept a `neuron_list` argument
  specifying which neurons to include; never use positional indexing without a named list
- All random operations use a seed from `phase0_config.py` as `RANDOM_SEED`
- Do not silently ignore scipy or numpy warnings; treat them as unexpected results