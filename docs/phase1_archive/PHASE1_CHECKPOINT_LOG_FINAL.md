# Phase 1 Checkpoint Log — FINAL ARCHIVE COPY

> **ARCHIVE RECORD**
> Archived: 2026-05-31
> Rationale: Phase 1 formally closed — structural observability obstruction.
>   N_COMMON_NEURONS = 61 and MISSING_NEURON_POLICY = "nan_complete_case" are
>   jointly unachievable on the Atanas SF freely-behaving corpus.
> Closure status: No further Phase 1 computation authorized.
> Phase 2 not yet authorized.
> Source file: PHASE1_CHECKPOINT_LOG.md (repo root) — preserved unchanged.
> The 2026-05-31 ARCHIVE CHECKPOINT entry is the final entry.

---

# Phase 1 Checkpoint Log

Status: **FORMALLY CLOSED — structural observability obstruction (2026-05-31)**
Initialized: 2026-05-29
Closed: 2026-05-31

Phase 0 operational checkpoints are archived at: `docs/phase0/operational/CHECKPOINT_LOG.md`

Checkpoint format:
```
## YYYY-MM-DD — [description]
Date:
Phase:
Action:
Prior state:
Outcome:
Files changed:
Tests:
```

---

## 2026-05-31 — PHASE 1 ARCHIVE CHECKPOINT — FORMAL CLOSURE

Date: 2026-05-31
Phase: Phase 1 — FORMALLY CLOSED
Action: Phase 1 archived as structurally obstructed. No further Phase 1 computation
        is authorized. Phase 2 has not been authorized. This entry is the final
        checkpoint for Phase 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ORIGINAL PHASE 1 OBJECTIVE

Test whether off-connectome precision matrix differences between roaming and
dwelling behavioral states in freely-behaving C. elegans are enriched in
neuropeptide-signaling neuron pairs. Primary coordinate: CePNEM residuals.
Robustness coordinate: raw GCaMP z-score. Analysis subgraph: 61 neurons
(N_COMMON_NEURONS = 61). Estimation policy: nan_complete_case.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REASON FOR CLOSURE

The locked parameters N_COMMON_NEURONS = 61 and
MISSING_NEURON_POLICY = "nan_complete_case" are jointly unachievable on the
Atanas SF freely-behaving corpus.

The 61-neuron subgraph was defined by marginal presence (each neuron identified
in ≥80% of recordings). Complete-case estimation requires all 61 neurons to be
present simultaneously in each contributing recording. Because different
recordings are missing different neurons, the complete-case intersection across
all recordings is 4 neurons. No recording simultaneously contains all 61
subgraph neurons.

This is a set-intersection property of the recording-level neuron presence
matrix. It is not resolvable by adjusting the marginal-presence threshold,
by re-running scripts, by re-identifying neurons in existing recordings, or
by corpus expansion: the SF dataset is the only freely-behaving C. elegans
calcium imaging dataset with neuron identification in the world as of 2026-05-31,
and its per-animal coverage ceiling (~70 neurons, 23% of 302) is set by the
optical and motion constraints of imaging freely-behaving animals, not by
labeling effort.

FAILURE POINT: Stage 1.1, Gate A, data-object assembly — before any statistical
estimation is attempted.

FAILURE TYPE: Dataset / observability limitation.
  NOT an implementation failure.
  NOT a statistical failure.
  NOT a coding failure.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPLETED WORK

Stage 1.0 — CePNEM residualization: COMPLETE (human-authorized 2026-05-31)
  40 NeuroPAL recordings residualized. All pass conditions met.
  Tau reparameterization: PASS (max error = 0.00e+00).
  Behavioral decorrelation: PASS (aggregate median reduction = 0.545 ≥ 0.50).
  14 variance-ratio pairs flagged < 0.10 (documented); 6 pairs > 1.0 (documented).
  Stationarity ratio = 1.083 (DEV-003 applies).
  COORD_PRIMARY updated to "cepnem_residual". DEV-004 resolved.
  40 .npz files saved: results/phase1/data/cepnem_residuals/

Stage 1.1 Gate A — complete-case characterization: COMPLETE
  Strict complete-case (all 40 recordings):
    Dwelling: 4 neurons, 30,583 frames, n_eff=33.09 (39 contributing recordings)
    Roaming:  13 neurons, 5,587 frames,  n_eff=24.17 (19 contributing recordings)
  Interpretation C (per-state 80% marginal threshold):
    Dwelling: 53 neurons, 166 frames, n_eff=36.07 — not viable
    Roaming:  48 neurons, 0 frames,   n_eff=0.0   — not viable

Construction-B tradeoff: COMPLETE
  Full sweep over all K × N operating points for all four state × coordinate
  combinations. No operating point achieves both N ≥ 61 neurons and K ≥ 19
  roaming recordings simultaneously.
  Results: results/phase1/data/construction_b_tradeoff.json

Joint subgraph analysis: COMPLETE
  Largest joint subgraph with all 19 roaming and 34 dwelling contributing
  recordings: 13 neurons (pharyngeal and head sensory; no locomotion
  interneurons: AVA, RIM, AIY, AIA absent).
  Results: results/phase1/data/joint_subgraph_tradeoff.json

Dwelling-vs-baseline feasibility (K=34): COMPLETE
  11 neurons; 55 total pairs; 7 on-connectome; 48 off-connectome.
  Dwelling: 26,961 frames, n_eff=26.9.
  Baseline-A: 31,085 frames, n_eff=79.9.
  PRIMARY_TOP_K=50 not executable (50 > 48 off-connectome pairs).
  Signal diluted ~7.7× (dwelling = 87% of baseline pool).

Corpus-feasibility audit: COMPLETE
  7 public NeuroPAL Ca²⁺ datasets surveyed (118 animals, 5 labs).
  SF (Atanas/Flavell) is the only freely-behaving + Ca²⁺ + neuron ID dataset.
  Per-animal coverage in freely-behaving recordings: avg 70 neurons (23% of 302).
  Coverage ceiling is optical/motion-limited, not labeling-limited.
  Automated re-ID pipelines cannot recover neurons below optical resolution floor.
  Adding more SF-type recordings does not increase the complete-case intersection.
  Source: Sprague, Rusch et al. 2025, Cell Reports Methods, PMC11840940.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REUSABLE ASSETS

All of the following are correct, complete, and directly applicable to any
successor project using the SF corpus:

  results/phase1/data/cepnem_residuals/           (40 .npz files)
    CePNEM residualized + raw GCaMP z-score traces, per recording.

  results/phase1/data/construction_b_tradeoff.json
    Full Construction-B operating point table for all four state × coordinate
    combinations. Defines every feasible complete-case subgraph for this corpus.

  results/phase1/data/joint_subgraph_tradeoff.json
    Feasible joint (roaming + dwelling) observability subgraphs, all operating
    points. Defines the roaming-driven ceiling (13 neurons).

  results/phase1/data/supplementary_coverage.json
    Marginal and complete-case frame counts for all four state × coordinate
    combinations under Interpretation C.

  results/phase1/data/supplementary_coverage_neuron_table.json
    Per-neuron presence counts and inclusion flags.

  src/cepnem_residualize.py
    CePNEM residualization implementation; verified correct.

  scripts/phase1/stage0_cepnem.py
    Stage 1.0 execution script including build_label_maps().

  scripts/phase1/stage1_supplementary_coverage.py
    Neuron presence matrix, Construction-B greedy sweep, n_eff computation.
    All functions are estimator-agnostic and reusable.

  src/estimators.py
    stability_selection_glasso() and anatomy_guided_glasso_admm() — Phase 0
    validated for complete-case pooled data. Reusable on any complete-case
    matrix; reusable as reference implementation for pairwise extension.

  phase0_config.py
    All locked behavioral segmentation parameters (BEHAV_THRESHOLD=0.284,
    EWMA_TIMESCALE_SECONDS=20.0, W_TRANS_SECONDS=10.0, MIN_BOUT_SECONDS=10.0),
    connectome thresholds (SYNAPSE_COUNT_THRESHOLD=1), and enrichment design
    parameters carry forward. Estimator parameters require review for any
    successor using a different estimation method.

  scripts/stage06_neff_stationarity.py
    segment(), get_epoch_slices(), tau_int_batch(), ewma() — behavioral
    segmentation and n_eff pipelines, reusable unchanged.

  Cook/Witvliet synaptic adjacency (herm_full_edgelist_MODIFIED.csv)
    Connectome annotation for the SF neuron set. Fully reusable.

  Phase 0 synthetic validation results (scripts/stage08_estimator_dryrun.py)
    Validated regime thresholds for complete-case GLASSO. Reference baseline
    for any successor estimator validation; do not transfer directly to
    pairwise or EM estimators without re-validation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UNRESOLVED SUCCESSOR DIRECTIONS (not authorized; recorded for reference only)

  SUCCESSOR-A — Phase 2: Pairwise-Estimator Extension
    Scientific question: same as Phase 1 (off-connectome ΔQ enrichment in
    neuropeptide pairs, roaming vs. dwelling). Replace nan_complete_case pooled
    GLASSO with a pairwise or EM-based estimator that handles per-observation
    missing patterns. Requires: new estimator implementation, Phase 0-equivalent
    synthetic validation under SF missingness structure, deviation records for
    MISSING_NEURON_POLICY and DISCOVERY_ESTIMATOR. Classification: new project
    (Phase 0-equivalent validation required; existing regime thresholds do not
    transfer). All behavioral segmentation, connectome annotation, and enrichment
    test design parameters carry forward.

  SUCCESSOR-B — RC/Model-Based Branch
    Scientific question: population-level whole-brain functional connectivity
    and its behavioral-state modulation, using a hierarchical or latent-variable
    graphical model that marginalizes over per-animal neuron subsets. Requires:
    new statistical framework (hierarchical GLASSO or equivalent), new validation
    study, reframing of the neuropeptide enrichment test as a subquestion.
    Classification: new project with a reframed scientific question.

  SUCCESSOR-C — Future Experimental Branch
    Resolution path: improve per-animal neuron coverage in freely-behaving
    recordings to ≥50% (≥150 neurons) through faster volumetric acquisition,
    motion-corrected NeuroPAL, or a second freely-behaving dataset from a
    collaborating lab. At ≥50% per-animal coverage, a 30–40 neuron complete-case
    subgraph becomes constructible; at ≥90%, the original Phase 1 object becomes
    constructible. No computational action required now. Phase 1 methodology
    and infrastructure are directly reusable if a suitable corpus becomes
    available.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AUTHORIZATION STATE

No further Phase 1 computation is authorized.
Phase 2 has not been authorized.
No successor-direction work may begin without a separate project kickoff
and explicit human authorization.

Files changed by this checkpoint: PHASE1_CHECKPOINT_LOG.md, PHASE1_PROGRESS.md
Tests: no new test runs authorized or required at closure.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 2026-05-29 — Phase 1 operational state initialized

Date: 2026-05-29
Phase: Phase 1 initialization (pre-authorization)
Action: Read all required documents in specified order; populated PHASE1_CONTEXT.md,
        PHASE1_PROGRESS.md, and PHASE1_CHECKPOINT_LOG.md with Phase 0 inherited state.
        No scientific computation performed. No config values modified.
Prior state: All three files contained placeholder headers only.
Outcome: Phase 1 operational state established. Guardrail confirmed active (4/4 tests pass).
         PHASE0_COMPLETE = False confirmed in phase0_config.py.
Files changed: PHASE1_CONTEXT.md, PHASE1_PROGRESS.md, PHASE1_CHECKPOINT_LOG.md
Tests: test_phase0_guard.py — 4/4 passed (run 2026-05-29)

---

## 2026-05-29 — PHASE0_COMPLETE = True authorization

Date: 2026-05-29
Phase: Phase 1 gate — methodology guardrail lift
Action: Set PHASE0_COMPLETE = True in phase0_config.py
Prior state: PHASE0_COMPLETE = False; real-data precision estimation blocked by RuntimeError
             in src/estimators.py across all 7 guarded entry points

Rationale for lifting the Phase 0 guardrail:
  All Phase 0 methodological prerequisites are satisfied:
  PHASE0_METHOD_LOCK_COMPLETE = True; hypothesis locked; synthetic validation complete
  (25/25 tests; TPR ≥ 0.80 in all supported regimes); all parameters frozen in
  phase0_config.py and phase0_locked_config_snapshot.json; fit_results.jld2 confirmed
  present and accessible (19.55 GB, 68 recordings, bit-identical to H5 files);
  sampled_trace_params (11,10001,N,n_epochs) confirmed; NL10d ordering confirmed.
  The three blocking deviations have been explicitly acknowledged and authorized below.

DEV-003 ACKNOWLEDGMENT (human, 2026-05-29):
  Phase 1 results represent time-averaged effective coupling under confirmed
  within-recording temporal covariance drift (photobleaching). This is an accepted
  design constraint. Results will not be interpreted as stationary per-animal precision
  geometry. The interpretation rule "time-averaged effective structure under confirmed
  drift" accompanies every result produced in Phase 1.

DEV-004 ACKNOWLEDGMENT (human, 2026-05-29):
  CePNEM residualization is authorized as the Phase 1 primary coordinate resolution path
  (Stage 1.0). No precision matrix may be computed until Stage 1.0 passes all
  verification checks. COORD_PRIMARY remains "gcamp_trace_array_zscore" until Stage 1.0
  passes; it is not changed by this checkpoint. The update to
  COORD_PRIMARY = "cepnem_residual" is deferred to the Stage 1.0 completion checkpoint.
  Raw GCaMP will serve as the robustness coordinate once the primary coordinate is
  established.

DEV-005 ACKNOWLEDGMENT (human, 2026-05-29):
  All-animal pooling without prior inter-animal outlier screening is authorized.
  The missing Stage 7 characterization is compensated by Stage 1.3 leave-one-animal-out
  sensitivity analysis. No animal will be excluded from the primary analysis based on
  LOO impact; influential animals will be flagged and reported but not removed.

Scope of this checkpoint (exhaustive):
  Authorized: PHASE0_COMPLETE = True in phase0_config.py; this log entry
  Not authorized: COORD_PRIMARY change; any Stage 1.0 planning or implementation;
                  any precision estimation, ΔQ, enrichment, or biological interpretation

Files changed: phase0_config.py (PHASE0_COMPLETE = True), PHASE1_CHECKPOINT_LOG.md (this entry)
Tests (run 2026-05-29, post-flag-flip): see guardrail verification below

Guardrail verification (post-flip):
  test_phase0_complete_is_false            → FAILED  (expected: flag is now True)
  test_phase0_method_lock_complete_is_true → PASSED
  test_real_data_precision_blocked         → FAILED  (expected: guard is now lifted)
  test_synthetic_precision_allowed         → PASSED
  Interpretation: the two newly failing tests confirm the guardrail was correctly lifted.
  Real-data precision estimation is now permitted. Synthetic-data calls unaffected.

Next required action:
  A separate Stage 1.0 CHECKPOINT for CePNEM residualization must be issued and
  approved before any implementation activity begins.

---

## ARCHIVE: Pending Authorization Template (superseded by entry above)

~~Pending: PHASE0_COMPLETE Authorization (human action required)~~

Before any Phase 1 scientific computation may begin, the following must be entered here
by explicit human authorization:

```
## YYYY-MM-DD — PHASE0_COMPLETE authorization
Date:
Phase: Phase 1 gate
Action: Set PHASE0_COMPLETE = True in phase0_config.py
Rationale:
  DEV-003 acknowledgment: [human statement accepting nonstationarity interpretation]
  DEV-004 acknowledgment: [human statement on CePNEM as primary coordinate]
  DEV-005 acknowledgment: [human statement on all-animal pooling without prior outlier screening]
COORD_PRIMARY update: cepnem_residual (after Stage 1.0 passes)
Tests: test_phase0_guard.py — [expected: 3 passed, 1 changed semantics after flag flip]
```

---

## 2026-05-29 — Gate A and Gate B authorization: Stage 1.0 CePNEM residualization

Date: 2026-05-29
Phase: Phase 1, Stage 1.0 (CePNEM residualization)
Action authorized:
  Gate A: Implement src/cepnem_residualize.py, scripts/phase1/__init__.py,
           scripts/phase1/stage0_cepnem.py; resolve four pre-coding ambiguities
           through limited read-only archive inspection before any residual
           computation, residual saving, verification metric computation, or
           scientific analysis.
  Gate B: Execute single-recording pilot on recording "2022-04-12-04" (index 0,
           N=151, 2 epochs, T=1600 frames); stop and report all Gate B items before
           any further execution.
Checkpoint clarification (human-issued): Pre-coding ambiguity resolution is
  permitted via limited read-only archive inspection before any residual computation,
  residual saving, verification metric computation, or scientific analysis.
Not authorized: Gate C (full 68-recording execution). Requires a separate checkpoint
  after the Gate B report is reviewed.
Files to be created: src/cepnem_residualize.py, scripts/phase1/__init__.py,
  scripts/phase1/stage0_cepnem.py, results/phase1/data/cepnem_residuals/ (runtime)
COORD_PRIMARY: remains "gcamp_trace_array_zscore" — not changed by this checkpoint.

Gate B results: see entry below.

## 2026-05-29 — Gate B results and Gate C authorization: Stage 1.0 full run

Date: 2026-05-29
Phase: Phase 1, Stage 1.0 (CePNEM residualization)

Gate B outcome:
  Pilot recording: 2022-06-14-07 (fit_results index 2; first NeuroPAL recording)
  NOTE: Original pilot target (index 0, "2022-04-12-04") was non-NeuroPAL;
        pilot correctly redirected to first NeuroPAL recording.
  Identity check: PASS (max |error| = 0.00e+00)
  Variance ratios: min=0.097, median=0.538, max=0.834; 1 flagged (FLPL, 0.097)
  Decorrelation: v=0.61, θh=0.50, P=0.90, curve=0.69 reduction (model inputs all ≥ 50%)
  Stationarity: drift_ratio_resid_over_raw = 1.115 (unexpected; to be assessed in aggregate)
  Wall time: 1.33 s/recording; estimated full-40 run: ~53 s

Gate C authorized (human, 2026-05-29):
  Scope: full Stage 1.0 run on 40 NeuroPAL-labeled recordings only (not 68)
  Restrictions:
    - Do not modify methodology or thresholds
    - Do not exclude FLPL
    - Do not investigate or attempt to correct the stationarity finding during execution
    - Complete all Stage 1.0 outputs exactly as specified
    - Stop after completion; do not begin Stage 1.1
    - A separate Stage 1.0 completion checkpoint determines progression to Stage 1.1
  COORD_PRIMARY: remains "gcamp_trace_array_zscore" — not changed by this checkpoint

Files to be created during Gate C:
  results/phase1/data/cepnem_residuals/{rec_id}.npz  (40 files)
  results/phase1/data/cepnem_residuals/verification/variance_ratios.csv
  results/phase1/data/cepnem_residuals/verification/decorrelation_stats.json
  results/phase1/data/cepnem_residuals/verification/stationarity_comparison.json
  results/phase1/figures/stage0/epoch_boundaries_*.pdf  (3 representative recordings)

Gate C results: see report entry below.

## 2026-05-29 — Gate C results: Stage 1.0 full run complete

Date: 2026-05-29
Phase: Phase 1, Stage 1.0 — complete
Wall time: 52.9 s (40 recordings)
Implementation bug fixed during execution: stationarity NaN for 21 recordings caused
  by NaN check over full T (including trailing frames after last epoch) instead of
  in-epoch frames only. Fixed in src/cepnem_residualize.py; stationarity recomputed
  from saved .npz files and H5 raw traces. Residualized traces not affected.
COORD_PRIMARY: remains "gcamp_trace_array_zscore" — not changed.
Next action: Stage 1.0 completion checkpoint required before Stage 1.1.

---

## 2026-05-29 — Stage 1.0 completion checkpoint

Date: 2026-05-29
Phase: Phase 1, Stage 1.0 — COMPLETE (human authorized)
Authorization: Human declares Stage 1.0 complete and authorizes transition planning.

HUMAN DECISION — Decorrelation covariate interpretation:
  Selected: CePNEM model inputs — (v, θh, P). These are the covariates the model was fit
  to remove. Aggregate median reduction = 0.545, which is above the 0.50 threshold.
  Stage 1.0 behavioral decorrelation criterion: PASS.
  Rationale: ang_vel and curve are in the archive but are NOT CePNEM model inputs (model.jl
  takes v, θh, P only). The check verifies removal of what the model was designed to remove.
  The ambiguity with the task.md phrase "velocity, angular velocity, curvature" is retained
  as a documented artifact inconsistency in PHASE1_CONTEXT.md. The human resolved it in
  favor of the model-input interpretation.

STAGE 1.0 FINDINGS — FULL RECORD:

  Identity check (implementation verification):
    Result: PASS — 40/40 recordings; max |first-frame error| = 0.00e+00 for all neurons
    and epochs. Forward equations confirmed correct.

  Recordings processed:
    40 of 40 NeuroPAL-labeled recordings. 28 non-NeuroPAL recordings in fit_results.jld2
    excluded (no neuron identity → no subgraph mapping possible).
    Subgraph neurons per recording: min=33, median=55, max=61.

  Behavioral decorrelation (Check A) — covariates (v, θh, P) [human-selected]:
    v:  median |r_raw|=0.148, |r_resid|=0.064, reduction=0.545
    θh: median |r_raw|=0.095, |r_resid|=0.053, reduction=0.380
    P:  median |r_raw|=0.148, |r_resid|=0.039, reduction=0.677
    Aggregate median reduction = 0.545 (≥ 0.50 threshold) → PASS
    P (pumping) shows strongest removal (67.7%), consistent with pumping being
    a dominant behavioral signal in the model. θh shows weakest removal (38.0%);
    this is noted in PHASE1_CONTEXT.md as a caveat for Stage 1.7 interpretation.
    For reference, non-model covariates:
      ang_vel: reduction=0.181 (not a model input — expected low)
      curve:   reduction=0.461 (not a model input)
    Artifact inconsistency: task.md check (a) lists "velocity, angular velocity,
    curvature" which does not match model inputs (v, θh, P). Human resolved this
    ambiguity in favor of model inputs. Full record in PHASE1_CONTEXT.md.

  Variance ratios (Check B) — on residual_raw before normalization:
    2,160 (recording × neuron) pairs total.
    Min=0.060, Median=0.562, Max=1.073.
    Flagged < 0.10: 14 pairs (see PHASE1_CONTEXT.md for full list). Not excluded.
    Flagged > 1.0: 6 pairs (max 1.073). Diagnosed as expected Bayesian behavior for
      weakly-tuned neurons (positive Cov(trace, predicted) in all 6 cases; Var(pred) > 2·Cov
      because Corr < 0.25 for all 6). Not an implementation error; not excluded.

  Epoch boundary artifacts (Check C):
    Boundary plot saved: results/phase1/figures/stage0/2022-06-14-07_epoch_boundaries.pdf
    All 40 NeuroPAL recordings are 2-epoch with no gap frames; no 3-epoch NeuroPAL
    recordings present in the archive.
    Qualitative verdict: no systematic directional transient observed.

  Residual stationarity (Check D):
    Median drift_raw: 0.785; Median drift_resid: 0.867.
    Median ratio (resid / raw): 1.083.
    33/40 recordings: ratio > 1.0 (residuals more nonstationary than raw trace).
    7/40 recordings: ratio < 1.0.
    Finding: CePNEM residualization does not reduce temporal covariance drift.
    Interpretation: The behavioral model (v, θh, P) does not capture the long-timescale
    drift (photobleaching). DEV-003 interpretation applies equally to CePNEM residuals.
    This is a scientific finding, not a failure.

  Implementation notes:
    Stationarity NaN bug (trailing-frame NaN check) found during execution and corrected.
    Residualized traces are unaffected. Bug was in the verification metric only.

  Files saved:
    40 .npz files: results/phase1/data/cepnem_residuals/{rec_id}.npz
    results/phase1/data/cepnem_residuals/verification/variance_ratios.csv
    results/phase1/data/cepnem_residuals/verification/decorrelation_stats.json
    results/phase1/data/cepnem_residuals/verification/stationarity_comparison.json
    results/phase1/figures/stage0/2022-06-14-07_epoch_boundaries.pdf
    src/cepnem_residualize.py, scripts/phase1/stage0_cepnem.py

COORD_PRIMARY update: PROPOSED but NOT YET IMPLEMENTED.
  Proposed: COORD_PRIMARY = "cepnem_residual"
  Proposed: COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"
  Requires a separate Stage 1.1 CHECKPOINT that explicitly authorizes the config
  change before any precision matrix is computed. phase0_config.py is not modified here.

Next required action: Stage 1.1 CHECKPOINT (see pending entry below).

---

## 2026-05-31 — Stage 1.0 completion: coordinate transition executed

Date: 2026-05-31
Phase: Phase 1, Stage 1.0 — FORMALLY CLOSED
Action: Updated two fields in phase0_config.py per the approved Stage 1.0 completion
        checkpoint. No other fields changed. No scientific computation performed.

Fields changed:
  COORD_PRIMARY:      "gcamp_trace_array_zscore" → "cepnem_residual"
  COORD_ROBUSTNESS_1: None                       → "gcamp_trace_array_zscore"

DEV-004 status: RESOLVED.
  CePNEM residuals computed, verified, and saved (40 recordings).
  COORD_PRIMARY now reflects the primary analysis coordinate.
  Raw GCaMP is now formally designated the robustness coordinate.

Config integrity verification:
  git diff phase0_config.py: exactly 2 value-bearing lines changed for this checkpoint
    (PHASE0_COMPLETE = True is a pre-existing change from the 2026-05-29 authorization).
  All other fields in phase0_config.py: unchanged; consistent with
    phase0_locked_config_snapshot.json.

Test suite results after coordinate update (37 tests):
  31 passed — unaffected by coordinate update.
  6 failed — ALL pre-existing; NONE attributable to this checkpoint:
    test_harmonization.py::test_behavioral_threshold_config
      Pre-existing: stale Phase 0 test asserting MIN_BOUT_SECONDS is None
      (correctly set to 10.0 at Stage 5).
    test_harmonization.py::test_phase0_midproject_config_integrity
      Pre-existing: stale Phase 0 test asserting SUBGRAPH_ADEQUATE is None
      (correctly set to True at Stage 10).
    test_phase0_guard.py::test_phase0_complete_is_false
      Pre-existing since 2026-05-29: expected failure; PHASE0_COMPLETE = True.
    test_phase0_guard.py::test_real_data_precision_estimation_is_blocked
      Pre-existing since 2026-05-29: expected failure; guard is lifted.
    test_estimators.py::test_stability_selection_blocked_for_real_data
      Pre-existing since 2026-05-29: expected failure; guard is lifted.
    test_estimators.py::test_anatomy_guided_blocked_for_real_data
      Pre-existing since 2026-05-29: expected failure; guard is lifted.
  Neither COORD_PRIMARY nor COORD_ROBUSTNESS_1 is referenced by any test.
  No new failures introduced.

Stage 1.0: FORMALLY CLOSED.
DEV-004: RESOLVED.
Next action: Stage 1.1 Gate A + pilot — authorized and recorded below.

---

## 2026-05-31 — Stage 1.1 Gate A and limited precision-estimation pilot: authorized

Date: 2026-05-31
Phase: Phase 1, Stage 1.1 (partial — Gate A + 5-fit pilot only)
Action authorized:
  Gate A: Behavioral segmentation (exact Stage 6 implementation), state counts,
    frame counts, n_eff recomputation on CePNEM residuals, effective neuron counts
    after nan_complete_case filtering for each state × coordinate combination.
  Pilot: 5 real-data graphical-lasso fits (cepnem_residual × dwelling only).
    For each fit: convergence outcome, BIC alpha, condition number, warnings.
    Wall time measured; Gate B total extrapolated.
Restrictions:
  Pilot matrices are not outputs and must not be used for ΔQ, enrichment, ranking,
    or any interpretation.
  No precision matrices saved. No Gate B without separate checkpoint.
  Segmentation must exactly reproduce Stage 6 implementation.
  No alternative frame-rate convention evaluated.

Gate A + pilot results: see report below.

## 2026-05-31 — Stage 1.1 Gate A + pilot results

Date: 2026-05-31
Phase: Phase 1, Stage 1.1 (Gate A + limited pilot only)
Unexpected finding: nan_complete_case applied cross-recording yields 4 effective
  neurons (dwelling) and 13 (roaming). This makes the pilot timing (< 0.01s/fit)
  not representative of the intended full-scale problem. Human direction required
  before Gate B proceeds. Full report in session output.

---

## 2026-05-31 — Supplementary neuron-coverage computation (Interpretation C)

Date: 2026-05-31
Phase: Phase 1, Stage 1.1 pre-estimation (supplementary computation only)
Action: Ran supplementary neuron-coverage computation under Interpretation C,
        as authorized by human checkpoint. No precision matrices computed.
        No pilot rerun. No Stage 1.1 Gate B.

Method: For each state × coordinate combination, neurons present (no NaN in
  all state-epoch frames) in >= ceil(COVERAGE_FRACTION × N_contributing) of the
  contributing recordings are included. MISSING_NEURON_POLICY = nan_complete_case
  retained: any frame with NaN in an included neuron column is dropped.

Results:

  CePNEM dwelling (N_contributing=39, threshold=32):
    n_neurons_strict:        4   (Gate A; 100% presence required)
    n_neurons_Interp_C:     53   (>= 32/39 recordings)
    excluded_neurons:        AVJR, IL1R, IL2VL, IL2VR, M1, OLQVR, RMDDR, URYVR
    n_frames_complete_case: 166  (from 1 recording only: 2023-01-10-07)
    n_eff_p25:               36.07
    viable:                 False  (166 frames for 1378 pairs; below-middle)

  CePNEM roaming (N_contributing=19, threshold=16):
    n_neurons_strict:       13   (Gate A)
    n_neurons_Interp_C:     48   (>= 16/19 recordings)
    excluded_neurons:        AIBR, AIZL, AVEL, AVER, AVJR, IL1R, IL2VL, IL2VR,
                             M1, OLQVL, RMDDR, RMDL, URBL
    n_frames_complete_case:  0   (no recording has all 48 included neurons)
    n_eff_p25:               0.0
    viable:                 False  (0 frames)

  GCaMP dwelling (N_contributing=39, threshold=32):
    n_neurons_Interp_C:     53   (same as CePNEM — same NeuroPAL identity)
    n_frames_complete_case: 166  (same 1 recording)
    n_eff_p25:               20.44
    viable:                 False

  GCaMP roaming (N_contributing=19, threshold=16):
    n_neurons_Interp_C:     48   (same as CePNEM)
    n_frames_complete_case:  0
    viable:                 False

Root cause of collapse:
  The 80% marginal-presence threshold includes neurons absent from ~20% of
  contributing recordings. Under complete-case, any recording missing any
  included neuron contributes 0 frames. Because different recordings are missing
  different neurons, the intersection (recordings with ALL included neurons) is
  near-empty: 1 recording for dwelling, 0 for roaming. This is not a bug;
  it is a structural property of the dataset — each recording typically has
  50-58 of the 61 subgraph neurons, with the missing neurons varying by animal.

Comparison (strict vs. Interpretation C — CePNEM):
  Strict complete-case (Gate A):  dwelling 4 neurons, 30,583 frames, n_eff=33
  Interpretation C:               dwelling 53 neurons, 166 frames, n_eff=36
  Strict:                         roaming 13 neurons, 5,587 frames, n_eff=24
  Interpretation C:               roaming 48 neurons, 0 frames, n_eff=0
  Result: Interpretation C yields more neurons but far fewer (or zero) usable frames.

Files saved:
  results/phase1/data/supplementary_coverage.json
  results/phase1/data/supplementary_coverage_neuron_table.json
  scripts/phase1/stage1_supplementary_coverage.py

Next required action: human decision. Both interpretations are non-viable under
  the locked full-matrix precision estimation plan (61-neuron subgraph). The
  complete-case policy is incompatible with the 80% marginal-presence threshold
  because no single animal has all marginally-present neurons simultaneously.

---

## ARCHIVE: Stage 1.0 CHECKPOINT template (superseded by entry above)

~~Pending: Stage 1.0 CePNEM Checkpoint (agent issues; human approves)~~

When the human issues "go ahead" for Stage 1.0, the agent will write:

```
CHECKPOINT: Implement CePNEM residualization (Stage 1.0)
[1] fit_results.jld2 available (19.55 GB); 68 recordings; sampled_trace_params confirmed (11, 10001, N, n_epochs)
[2] NL10d param ordering confirmed (param[4]=0.0); behavioral weights at params[0-3]
[3] Proposed action: implement compute_cepnem_residuals() in src/cepnem_residualize.py
    using model_nl8 forward equations with posterior median parameters and z_score_global normalization
[4] Success: decorrelation ≥ 50%; no neuron variance ratio < 0.10; no epoch artifacts; traces saved
[5] Failure: decorrelation < 50% (behavioral confound not captured); variance ratio < 0.10 for many neurons
```

Then await explicit "go ahead".

---

## Pending: Stage 1.1 Precision Estimation Checkpoint

```
CHECKPOINT: Compute state-conditioned precision matrices (Stage 1.1)
[1] Stage 1.0 CePNEM pass conditions all met (to be filled in)
[2] Rules out: behavioral confound driving all ΔQ structure
[3] Proposed: run stability selection + anatomy-guided lasso for both states × both coordinates
[4] Success: 8 PD symmetric precision matrices; condition numbers < 1e6; no convergence failures
[5] Failure: convergence failure, non-PD matrix, or near-singular covariance in one state
```

---

## Pending: Stage 1.6 Enrichment Checkpoint

```
CHECKPOINT: Run enrichment tests (Stage 1.6)
[1] ΔQ computed and classified; Class 4 count ≥ 20 (to be filled)
[2] LOO retention: median ≥ 0.70 (to be filled)
[3] Proposed: run all 4 tests × 2 null models; validate degree-preserving null
[4] Success: all 8 test results saved to JSON before any figure
[5] Failure: Class 4 count < 20 (underpowered); degree-preserving null fails KS validation
```

---

## Pending: Stage 1.7 Coordinate Comparison Checkpoint

```
CHECKPOINT: Open coordinate comparison (Stage 1.7)
[1] Both coordinates' enrichment results confirmed saved on disk (to be filled)
[2] Rules out: peeking at one coordinate before the other
[3] Apply locked interpretation table mechanically
[4] Success: interpretation recorded in coord_comparison_interpretation.json with supporting numbers
[5] Failure: results not yet available for one coordinate
```
