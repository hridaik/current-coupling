# PROGRESS

## Current Stage

**PHASE 0 ARCHIVED — METHODOLOGY LOCK COMPLETE — REAL-DATA INFERENCE STILL PROHIBITED** (2026-05-29).

Archive location: docs/phase0/
Phase 1 planning: not yet begun.
Next action: human reviews docs/phase0/phase1_transition_manifest.md, authorizes
  DEV-003/DEV-004/DEV-005, sets PHASE0_COMPLETE=True, then authorizes Phase 1 planning.

---

**PHASE 0 METHODOLOGY LOCK COMPLETE — REAL-DATA INFERENCE STILL PROHIBITED** (2026-05-29).

Stage 10 hypothesis lock finalized. 41/41 consistency checks pass.
Methodology and synthetic validation are frozen (PHASE0_METHOD_LOCK_COMPLETE=True).

Re-lock executed 2026-05-29: PHASE0_COMPLETE restored to False.
Real-data precision / ΔQ / enrichment remain blocked in src/estimators.py.
PHASE0_METHOD_LOCK_COMPLETE=True separately records methodology completion.

Remaining deviations that block real-data inference:
- DEV-003: NONSTATIONARITY_FRACTION=1.0 (covariance drift real; cause unresolved)
- DEV-004: COORD_PRIMARY=gcamp_trace_array_zscore (CePNEM files unavailable)
- DEV-005: Stage 7 not completed; OUTLIER_ANIMALS=[]; CV fold assignments not generated

Phase 1 transition package: results/diagnostics/phase1_transition_manifest.md
Locked config snapshot: results/diagnostics/phase0_locked_config_snapshot.json

## CePNEM Full Archive — Schema Confirmation (2026-05-29)

fit_results.jld2 now FULLY DECOMPRESSED (19.55 GB). h5py opens cleanly.

Direct confirmation (no longer source-code inferred):
  - sampled_trace_params: shape (11, 10001, N, n_epochs) float64 — CONFIRMED in all 68 recordings
  - 12 fields total (lite had 11); addition is exactly sampled_trace_params
  - param[4] = 0.0000 exactly → NL10d parameter ordering CONFIRMED
  - Behavioral encoding params (c_vT, c_v, c_θh, c_P) = params[0–3] — directly readable
  - No precomputed residuals, predicted traces, or conditional fields (trace_params etc.)
  - trace_array bit-identical to H5 gcamp/trace_array
  - 68/68 recording IDs align perfectly with H5 files
  - sampled_tau_vals range: 0.24–504 s (biologically plausible)

New finding — timescale reparameterization:
  - stp[6] (s0) is highly correlated (r~0.99) with sampled_tau_vals
  - But the simple compute_s(s0)=10*exp(s0) formula does NOT reproduce tau values
  - Residual computation must use CePNEM model_nl8 forward equations directly
  - Does NOT block residual feasibility; behavioral encoding params unaffected

Residual reconstruction: CONFIRMED FEASIBLE via model_nl8 posterior evaluation.
Authorized to compute: NO — future checkpoint required.
Report: results/diagnostics/cepnem_full_schema_confirmation.md

## CePNEM Full Archive Audit (2026-05-29)

fit_results.jld2 (19.55 GB full; 4.23 GB on disk — TRUNCATED):
  data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2
  data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2.bz2  (12.38 GB — complete)

Full archive schema audit (source-code inferred; file truncated):
  - Key additional field: sampled_trace_params (11, 10001, N, n_epochs) float64
  - Contains all NL10d parameters: c_v, c_θh, c_P, c_vT (behavioral encoding weights)
    + y0, s0, b, ℓ0, σ0_SE, σ0_noise
  - CePNEM residuals computable via closed-form model_nl8 (NO OLS needed)
  - Conditional fields (if save_raw_params): trace_params, log_weights, trace_scores, log_ml_est
  - File INACCESSIBLE: truncated JLD2 (root group at byte 19.5 GB, only 4.23 GB present)
  - BLOCKER: complete bzip2 decompression required before use
  - Lite JLD2 also unavailable (only .bz2 remains)

Size arithmetic: sampled_trace_params alone ≈ 16.5 GB × 68 recordings → consistent
with observed full-archive stored EOF of 19.55 GB.

Report: results/diagnostics/cepnem_full_schema_audit.md
Action needed: `bzip2 -dk fit_results.jld2.bz2` (also `fit_results_lite.jld2.bz2`)

## CePNEM Lite Availability (2026-05-29)

fit_results_lite.jld2 (1.85 GB) now present at:
  data/atanas/AtanasKim-Cell2023/cepnem/fit_results_lite.jld2

Schema audit complete (metadata only; no residuals computed):
  - 68 recordings, perfect ID alignment with H5 files
  - 11 fields per recording: behavioral covariates + trace_array + sampled_tau_vals
  - trace_array is bit-identical to H5 gcamp/trace_array (NOT residualized)
  - CePNEM residuals NOT directly stored; computable via EWMA regression (future checkpoint)
  - sampled_tau_vals: MCMC posterior of EWMA timescale τ per neuron/epoch (10001 samples)
  - beta coefficients (required to directly extract residuals) NOT in lite artifact

COORD_PRIMARY = "gcamp_trace_array_zscore" remains unchanged (DEV-004).
Future upgrade path: checkpoint → implement compute_cepnem_residuals() in preprocessing.py.
Report: results/diagnostics/cepnem_lite_schema_audit.md

## Previous Stage

Stage 8 synthetic robustness characterization complete (2026-05-29).
Key findings:
  1. Nonstationarity robustness: TPR 0.80-1.00 across all drift levels (0-100%).
     Drift in dwell state does NOT hurt roaming signal detection.
  2. Topology threshold (0.50) not materially better than amplitude (0.75) — signal
     pairs have consistently high stability scores (median 0.97-1.00).
  3. Blockwise estimation DOES NOT HELP for arbitrary cross-block signal.
     Full-matrix pooled estimation is strictly better.
  4. Pooled multi-animal: 25 animals × 40 frames = T_total=1000 → TPR=0.90.
     This exactly matches real roaming situation (25/40 animals with data).
All 10 pytest tests pass.

## Completed

- Repository scaffold initialized.
- Required path/source checkpoint recorded.
- Creamer LDS source audit script/report prepared without loading model/data arrays.
- Creamer D-type human decision recorded.
- Stage 2 read-only planning audit prepared for Atanas, ConnectomeToolbox, and
  wormneuroatlas label/source discovery. No label tables, connectome matrices,
  or biological arrays were loaded.
- Identity-confidence threshold human decision recorded before loading label
  tables or computing subgraph feasibility.
- Stage 2 feasibility script loaded only small label/metadata files under the
  locked threshold and `LR_POLICY = "separate"`. It found metadata-only overlap
  counts, but did not compute `N_COMMON_NEURONS` because the required Atanas
  confidence-filtered per-animal label table was not present in the allowed
  local files.
- Read-only Atanas input-discovery audit completed under `data/atanas/`.
  The audit found repository instructions and code/notebook references for
  `processed_h5`, `list_neuropal_label.jld2`, `Neuron ID.xlsx`,
  `neuropal_registration`, and `roi_match_confidence`, but did not find the
  required confidence-bearing Atanas label files locally.
- The human placed `dict_neuropal_label.jld2` under
  `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/`. A read-only
  metadata audit confirmed the file exists and is 11,343,265 bytes, but current
  `.venv` dependencies cannot inspect JLD2 keys or Julia object structure.
- Human approved installing exactly one additional `.venv` dependency, `h5py`,
  for metadata-only inspection of the Atanas JLD2 file. `h5py==3.16.0` was
  installed. The h5py audit found a JLD2 dictionary keyed by 40 Atanas-style
  record IDs. Sampled leaves contain label-like strings and a confidence-like
  float scalar, but h5py does not expose Julia field names or full semantic
  decoding.
- Stage 2 label-only h5py decoding completed under the locked
  `IDENTITY_CONFIDENCE_THRESHOLD = 2.5` and `LR_POLICY = "separate"`.
  The JLD2 structure exposed literal `label` and `confidence` fields, so
  confidence-filtered Atanas coverage was computable. `N_COMMON_NEURONS` was
  computed and recorded as 61. `N_RANDI_SUBGRAPH_PAIRS` was not computed and
  `SUBGRAPH_ADEQUATE` remains unset.
- Stage 2 diagnosis report produced
  (`results/diagnostics/stage02_diagnosis_report.md`). Two deviations
  identified (DEV-001, DEV-002). Human approved AWC methodological
  interpretation and procedural cleanup. `COVERAGE_FRACTION = 0.80` moved
  into `phase0_config.py`; hardcoded constant removed from script; deviations
  recorded in `DEVIATIONS.md`; two new tests added to
  `tests/test_harmonization.py`. No recomputation performed.
- Stage 3 schema audit completed (`results/diagnostics/stage03_randi_schema_audit.md`).
  Inspected funatlas.h5 structure (neuron_ids, shapes/dtypes, scalar thresholds).
  Key findings: pair metadata is separable from per-trial traces; AWCL absent
  from funatlas (same AWC mismatch as Stage 2); q_eq_th semantics unresolved.
- Stage 3 pair-index planning completed
  (`results/diagnostics/stage03_randi_pair_index_plan.md`).
  Human approved: AWCL/AWCR and AWCON/AWCOFF remain distinct namespaces;
  N_COMMON_NEURONS = 61 retained; effective funatlas subgraph = 60 neurons;
  q_eq_th not used. Loaded only wt/occ1 and unc31/occ1. Results:
  WT 3118, unc31 2057, both 1964 observed directed pairs / 3540 possible.
  N_RANDI_SUBGRAPH_NEURONS = 60 added to phase0_config.py.
- Stage 3 filter-policy audit completed
  (`results/diagnostics/stage03_filter_policy_audit.md`).
  Loaded occ1, q, dFF for descriptive characterization. Five candidate rules
  documented (A: 189, B: 101, C: 112, D: 168, E: 83 pairs). Library documents
  q < 0.05 ("as in Randi et al.") + |dFF| >= 0.10 as default. q-values
  well-behaved (range 5e-39 to 0.65). No threshold selected.
  N_RANDI_SUBGRAPH_PAIRS not set. phase0_config.py unchanged.
- Stage 3 pair-filtering rule locked: Rule A approved (q_wt < 0.05,
  occ1_wt > 0, occ1_u31 > 0, no amplitude gate). Config fields added:
  RANDI_WT_Q_THRESHOLD = 0.05, RANDI_AMPLITUDE_GATE_DFF = None,
  N_RANDI_SUBGRAPH_PAIRS = 189. Rule B retained for robustness analysis only.
- Mid-project checkpoint produced
  (`results/diagnostics/phase0_midproject_checkpoint.md`). All approved
  decisions, unset fields, deviations, dependencies, and blockers documented.
  Test added: test_phase0_midproject_config_integrity. 10/10 tests pass.
- Stage 4 Creamer/RC bridge structural feasibility audit completed
  (`results/diagnostics/stage04_creamer_rc_bridge_audit.md`).
  Creamer: 154 neurons, dt=0.5s, A_C stable (max|eig|=0.9966), D_C diagonal
  posdef. Common-61 ∩ Creamer = 56/61 (AIBL, AIBR, AWCL, IL1L, IL1R absent).
  RC: 5D eigenworm space, no neuron-space Jacobian, no state-conditioning.
- Stage 4 numerical feasibility audit completed
  (`results/diagnostics/stage04_creamer_numerical_feasibility.md`).
  scipy 1.17.1 installed. Sigma_C: posdef, kappa=35.1. Omega_C: Frob=8.6089.
  All CREAMER_* and RC_* config fields set. N_CREAMER_SUBGRAPH_NEURONS=56.
  Three-space model established: 61 (anatomical) / 60 (Randi) / 56 (Creamer).
  Test: test_creamer_rc_numerical_feasibility_config. 11/11 pass.
- Stage 5 preprocessing metadata audit completed (source-code only; DATA BLOCKED).
  H5 schema documented from ANTSUNData.jl / ANTSUNDataJLD2.jl / FlavellConstants.jl.
  CePNEM model structure documented. BEHAV_THRESHOLD NOT set. phase0_config.py unchanged.
- Stage 5 behavioral descriptive audit completed
  (`results/diagnostics/stage05_behavior_descriptive_audit.md`).
  68 H5 recordings loaded (40 NeuroPAL). matplotlib 3.10.9 installed.
  Key results: median duration=16.2 min; median n_neuron=138; velocity_s
  median=0.385, p5=-1.67, p95=1.71; 61.2% frames forward; mean reversal
  fraction=35.2%; trace NaN fraction median=0.000. Figures saved.
  BEHAV_THRESHOLD NOT set. phase0_config.py unchanged.
- Stage 5 threshold characterization completed
  (`results/diagnostics/stage05_threshold_characterization.md`).
  Pooled velocity_s is trimodal: modes at -0.971, 0.037, 0.924.
  Trough 1 (reversal/dwelling): -0.337. Trough 2 (dwelling/roaming): 0.284.
- BEHAV_THRESHOLD=0.284 approved by human (2026-05-28). Config updated:
  BEHAVIOR_SCORE_SOURCE="velocity_s", BEHAV_THRESHOLD=0.284,
  BEHAV_THRESHOLD_RULE="pooled_velocity_s_kde_trough_between_dwelling_and_roaming".
- Stage 5 segmentation descriptive completed
  (`results/diagnostics/stage05_segmentation_descriptive.md`).
  Roaming occupancy: median=0.495, IQR=[0.400, 0.566]. CRITICAL FINDING:
  raw velocity_s bouts have median=1.8 s; 0% exceed 30 s. Raw threshold alone
  insufficient for sustained-state analysis. MIN_BOUT_SECONDS NOT set.
- Stage 5 EWMA characterization completed
  (`results/diagnostics/stage05_ewma_characterization.md`).
  tau=0→30s: roam_frac>=30s 0%→14.6%; trans/min 23.6→1.49; occ 0.495→0.186.
  Candidate range: tau=10–30s for W_TRANS-compatible epochs. No selection made.
- Stage 5 retained-frame feasibility audit completed
  (`results/diagnostics/stage05_retained_frame_audit.md`).
  EWMA_TIMESCALE_SECONDS=20.0 added to config. CRITICAL: tau=20s + W_TRANS=30s:
  25/40 recordings have ZERO retained roaming epochs; 9/40 zero non-roaming.
  Retained roaming median=0s; non-roaming median=61s. W_TRANS=30s infeasible.
- Stage 5 transition-window sweep completed
  (`results/diagnostics/stage05_transition_window_audit.md`).
  W=0s: 4/40 zero_roam, roam_med=72s; W=5s: 10/40, 23s; W=10s: 15/40, 8s;
  W=15s+: median roaming=0s. No W_TRANS gives all 40 animals roaming data.
  W=5s: 30/40 with roaming, roam_med=23s (best coverage+exclusion tradeoff).
  W_TRANS_SECONDS NOT set. No config changes.
- Stage 6 stationarity robustness audit completed
  (`results/diagnostics/stage06_stationarity_robustness.md`).
  Temporal drift median=0.891 >> null drift median=0.214. ALL 26/26 assessed
  pairs show excess > 0.05 (median excess=0.666). Excess does not decrease with
  sample support (r=-0.162). True within-recording temporal covariance structure
  confirmed. Leading candidate: photobleaching or within-recording behavioral
  drift. No parameters changed. HUMAN REVIEW REQUIRED.
  τ_int unit labels corrected in script, JSON, report.
- Stage 6 n_eff and stationarity diagnostics completed
  (`results/diagnostics/stage06_neff_audit.md`,
   `results/diagnostics/neff_report.json`).
  tau_int: roaming 1.2s, non-roaming 1.7s (cross-product; underestimated due to
  short-epoch k_cap truncation). Per-animal n_eff: roaming median 0 (half animals
  have zero roaming), non-roaming median 84.8. Pooled p25/N: roaming 6.99,
  non-roaming 32.86. ESTIMATOR_TIER = pooled_hierarchical. NONSTATIONARITY_FRACTION
  = 1.0 (all 26 assessed pairs drift > 0.3; likely sampling-noise artifact due to
  ill-conditioned covariance, not confirmed non-stationarity). Human review
  required before Stage 7. Figures saved.
- Stage 5 covariance-support feasibility audit completed
  (`results/diagnostics/stage05_covariance_support_audit.md`).
  At locked params (tau=20s, BEHAV_THRESHOLD=0.284, W_TRANS=10s):
  Roaming: 25/40 animals, 51 epochs total, med_ep=16.0s, p90=50.8s,
  med_retained=8s/animal, mean_retained=30s/animal.
  Non-roaming: 39/40 animals, 102 epochs total, med_ep=28.9s, p90=164.1s,
  med_retained=145s/animal, mean_retained=157s/animal.
  Pooled roaming n_eff_rough: 60 (τ_int=10s), 30 (τ_int=20s).
  Pooled n_eff/N: 1.0 (τ_int=10s), 0.5 (τ_int=20s) — borderline/infeasible.
  Pooled non-roaming n_eff/N: 5.1 (τ_int=10s), 2.6 (τ_int=20s) — feasible.
  MIN_BOUT_SECONDS NOT set. Figures saved.

## Key Numbers

- N_COMMON_NEURONS: 61
- N_RANDI_SUBGRAPH_PAIRS: 189 (Rule A)
- ESTIMATOR_TIER: pooled_hierarchical (set Stage 6)
- n_eff pooled p25/N: roaming 6.99, non-roaming 32.86 (likely overestimated; see Stage 6 notes)
- NONSTATIONARITY_FRACTION: 1.0 (unresolved; likely sampling-noise artifact)

## Current Blockers

1. **W_TRANS_SECONDS decision** — sweep shows no W_TRANS value gives all 40
   animals roaming data with tau=20s. Candidate options:
   - W=5s: 30/40 animals, roam_med=23s, roam_ep_med=12s (best coverage)
   - W=10s: 25/40 animals, roam_med=8s
   - W=tau=20s: ~18/40 animals, roam_med=0s (biologically clean, minimal data)
   Human must choose W_TRANS and decide whether to use all-animal pooling or
   accept reduced animal count for roaming analysis.
2. **MIN_BOUT_SECONDS** — cannot set until W_TRANS is chosen.
3. **COORD_PRIMARY** — still `None`; CePNEM fit files not locally available.
4. **SUBGRAPH_ADEQUATE** — still `None`; human must set this.
5. Human authorization for Stage 3 DCV extraction.

## Exact Next Action

Human decisions required (in order):
1. Review velocity KDE plots; decide BEHAV_THRESHOLD and BEHAVIOR_SCORE_SOURCE.
2. Set COORD_PRIMARY (pending CePNEM fit access) and COORD_ROBUSTNESS_1.
3. Set SUBGRAPH_ADEQUATE.
4. Authorize Stage 3 DCV extraction.
After (1)+(2): implement Stage 5 preprocessing functions on actual H5 data.
After (3)+(4): run Stage 3 DCV extraction.

## Human-Decision Fields Set

- DATA_ROOT: `data`
- ATANAS_PATH: `data/atanas/AtanasKim-Cell2023`
- CREAMER_PATH: `data/creamer/Creamer_LDS_2026`
- CONNECTOME_PATH: `data/connectome/ConnectomeToolbox`
- RANDI_PATH: `data/randi/wormneuroatlas`
- NEUROPEPTIDE_PATH: `data/randi/wormneuroatlas`
- CREAMER_D_TYPE: `discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D`
- RC_CODE_PATH: `ReservoirComputing`
- RC_ROLE_SAMPLING: `audit_only`
- RC_ROLE_JACOBIAN: `audit_only`
- RC_ROLE_DRIVE_SWEEP: `not_used_phase0`
- IDENTITY_CONFIDENCE_THRESHOLD: `2.5`
- N_RANDI_SUBGRAPH_NEURONS: `60` (60 of 61 common neurons have a funatlas entry; AWCL excluded)
- RANDI_WT_Q_THRESHOLD: `0.05`
- RANDI_AMPLITUDE_GATE_DFF: `None` (amplitude gate excluded from primary rule)
- N_RANDI_SUBGRAPH_PAIRS: `189` (Rule A: q_wt<0.05, both strains observed)
- CREAMER_TIME_CONVENTION: `"discrete_time"`
- CREAMER_DT: `0.5`
- CREAMER_MAX_EIGENVALUE: `0.996609`
- CREAMER_STABLE: `True`
- CREAMER_DC_AVAILABLE: `True`
- CREAMER_LABEL_CONVENTION: `"neuropal_str"`
- CREAMER_SIGMA_POSDEF: `True`
- CREAMER_OMEGA_NORM: `8.6089` (56-neuron subspace Frobenius norm)
- N_CREAMER_SUBGRAPH_NEURONS: `56`
- RC_ROLE_SAMPLING: `"behavioral_eigenworm_only"`
- RC_ROLE_JACOBIAN: `"not_viable"`
- RC_ROLE_DRIVE_SWEEP: `"not_viable"`
- RC_OUTPUT_NEURON_COORDS: `False`
- RC_OUTPUT_JACOBIAN_AVAILABLE: `False`
- RC_STATE_CONDITIONED: `False`
- RC_NEURON_COVERAGE: `0`

## Human-Decision Fields Still Unset

- SUBGRAPH_ADEQUATE
- COORD_PRIMARY
- COORD_ROBUSTNESS_1
- COORD_ROBUSTNESS_2
- BEHAVIOR_SCORE_SOURCE
- BEHAV_THRESHOLD
- BEHAV_THRESHOLD_RULE
- MIN_BOUT_SECONDS
- COORD_INTERP_RULE
- EXCLUDED_ANIMALS_PRIMARY
- POOLING_STRATEGY
- LAMBDA_ON
- LAMBDA_OFF
- LAMBDA_OFF_ON_RATIO
- NFOLDS
- NULL_MODEL_PRIMARY
- PRIMARY_HYPOTHESIS_TEXT
- PRIMARY_TOP_K
- D_ROBUSTNESS_RHO

## Deviations This Session

- DEV-001: `COVERAGE_FRACTION` was hardcoded in `scripts/stage02_subgraph.py`
  instead of imported from `phase0_config.py`. Resolved: value moved to config.
- DEV-002: `N_COMMON_NEURONS` was written to `phase0_config.py` by the script
  without a checkpoint, using an uncheckpointed head-vs-all Randi label-file
  choice. Resolved: human approved `randi_head` as canonical and accepted
  `N_COMMON_NEURONS = 61` provisionally.
- Stage 7 synthetic estimator dry-runs completed
  (`results/diagnostics/stage07_synthetic_estimator_dryrun.md`,
   `results/diagnostics/stage07_dryrun_results.json`).
  SS PASS at T=2000 (non-roaming optimistic) and T=420 (roaming optimistic) for effect=0.2.
  AG FAIL due to lambda_off=0.25 too permissive; needs lambda tuning to ~0.40-0.50.
  SS FAIL at T≤300 (middle/conservative regimes).
  10/10 pytest tests pass. sklearn GL convergence warnings noted (dual gap ~1e-3).
- Stage 8 robustness characterization completed (stage08_nonstationary_synthetic_robustness.md,
  stage08_synthetic_blockwise.md). Key: drift-robust (TPR 0.80-1.00), blockwise fails,
  pooled-25-animals achieves TPR=0.90 matching real roaming scenario.
