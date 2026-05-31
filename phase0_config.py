"""Phase 0 configuration.

This file is the single source of truth for Phase 0 paths, parameters,
diagnostic outputs, and human decisions. Human-decision fields start as None.
"""

# ----------------
# VERIFIED
# ----------------
ATANAS_SAMPLING_HZ = 5.0
ATANAS_INDICATOR = "GCaMP6s"
ATANAS_N_ANIMALS_APPROX = 30
ATANAS_GITHUB = "https://github.com/flavell-lab/AtanasKim-Cell2023"

N_NEURONS_TOTAL = 302
N_HEAD_NEURONS_APPROX = 180

COOK_N_NEURONS = 302
COOK_N_SYNAPSES_APPROX = 7000
CONNECTOME_GITHUB = "https://github.com/openworm/ConnectomeToolbox"

RANDI_N_PAIRS = 23433
RANDI_PREPARATION = "immobilized"
RANDI_GITHUB = "https://github.com/francescorandi/wormneuroatlas"

CREAMER_GITHUB = "https://github.com/Nondairy-Creamer/Creamer_LDS_2024"
CREAMER_MODEL_TYPE = "noisy_linear_dynamical_system"
CREAMER_CONNECTOME_CONSTRAINED = True

# ----------------
# PATHS
# ----------------
DATA_ROOT = "data"
ATANAS_PATH = "data/atanas/AtanasKim-Cell2023"
CREAMER_PATH = "data/creamer/Creamer_LDS_2026"
CONNECTOME_PATH = "data/connectome/ConnectomeToolbox"
RANDI_PATH = "data/randi/wormneuroatlas"
NEUROPEPTIDE_PATH = "data/randi/wormneuroatlas"
RESULTS_DIR = "results"
RANDOM_SEED = 20260527

# ----------------
# CREAMER
# ----------------
# CREAMER_TIME_CONVENTION: confirmed discrete-time from sample_rate=2 Hz.
# Continuous-time equivalent requires (1/dt)*logm(A_disc); not needed
# if the analysis stays in discrete time.
CREAMER_TIME_CONVENTION = "discrete_time"
CREAMER_DT = 0.5                  # seconds per sample (1 / 2 Hz)
# CREAMER_MAX_EIGENVALUE: max |eig| of A_C for the full 154-neuron model.
# 56-neuron Creamer-compatible subspace: max |eig| = 0.984367.
CREAMER_MAX_EIGENVALUE = 0.996609  # connectome_constrained full model
CREAMER_STABLE = True              # all |eig| < 1.0 (discrete-time stable)
CREAMER_DC_AVAILABLE = True        # dynamics_cov present, diagonal, posdef
CREAMER_D_TYPE = "discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D"
CREAMER_LABEL_CONVENTION = "neuropal_str"  # NeuroPAL-style string IDs (e.g. ADAL)
# CREAMER_SIGMA_POSDEF: verified by scipy.linalg.solve_discrete_lyapunov.
# 56-neuron subspace: min eig = 9.97e-3, max eig = 3.50e-1, kappa = 35.1.
# Full 154-neuron model: min eig = 9.70e-3, max eig = 1.85, kappa = 190.
CREAMER_SIGMA_POSDEF = True
# CREAMER_OMEGA_NORM: ||Omega_C||_F = ||A_C + D_C Q_C||_F.
# Recorded for the 56-neuron Creamer-compatible subspace (approved scope).
# Full 154-neuron reference: 14.12.
CREAMER_OMEGA_NORM = 8.6089        # 56-neuron subspace Frobenius norm

# ----------------
# RC
# ----------------
RC_CODE_PATH = "ReservoirComputing"
# RC operates in 5D eigenworm space (crawl PCs), NOT identified-neuron space.
# Wout maps reservoir (N=10000) -> eigenworm (dim=5); no NeuroPAL Jacobian.
RC_OUTPUT_NEURON_COORDS = False
RC_OUTPUT_JACOBIAN_AVAILABLE = False
RC_STATE_CONDITIONED = False       # saved ESN has no behavioral-state context
RC_NEURON_COVERAGE = 0             # zero identified neurons in RC output
# RC_ROLE_JACOBIAN: not viable — no Jacobian in NeuroPAL neuron coordinates.
# RC_ROLE_DRIVE_SWEEP: not viable — eigenworm space is orthogonal to neuron space.
# RC_ROLE_SAMPLING: restricted to behavioral eigenworm sampling only.
RC_ROLE_SAMPLING = "behavioral_eigenworm_only"
RC_ROLE_JACOBIAN = "not_viable"
RC_ROLE_DRIVE_SWEEP = "not_viable"

# ----------------
# SUBGRAPH / HARMONIZATION
# ----------------
LR_POLICY = "separate"
IDENTITY_CONFIDENCE_THRESHOLD = 2.5
COVERAGE_FRACTION = 0.80
N_COMMON_NEURONS = 61
# N_RANDI_SUBGRAPH_NEURONS: neurons from the common subgraph with a direct
# name match in funatlas.h5. AWCL is present in N_COMMON_NEURONS (anatomical
# namespace) but absent from funatlas (which uses AWCOF/AWCON functional-state
# labels). This asymmetry is approved; the two namespaces remain distinct.
N_RANDI_SUBGRAPH_NEURONS = 60
# N_CREAMER_SUBGRAPH_NEURONS: neurons from the common-61 subgraph that have a
# direct name match in all three Creamer LDS models (154-neuron models).
# AIBL, AIBR, AWCL, IL1L, IL1R are absent from all Creamer models. These 5
# neurons must NOT be imputed or padded; D_C / Omega_C / current-velocity
# bridge analyses are restricted to this 56-neuron subspace.
N_CREAMER_SUBGRAPH_NEURONS = 56
# SUBGRAPH_ADEQUATE: N_COMMON_NEURONS=61 >> 30 minimum viable threshold.
# Key circuit neurons (AVA, RIM, AIY, AIA) confirmed present in Stage 2
# harmonization audit. Subgraph is biologically adequate for the roaming/dwelling
# state-switch hypothesis. Approved Stage 10.
SUBGRAPH_ADEQUATE = True
SYNAPSE_COUNT_THRESHOLD = 1
SYNAPSE_COUNT_THRESHOLD_SENSITIVITY = 3

# ---- Randi pair-filtering policy (Rule A, approved 2026-05-28) ----
# Primary pair definition: q_wt < RANDI_WT_Q_THRESHOLD AND occ1_wt > 0
#   AND occ1_u31 > 0.
# q threshold documented as "Default: 0.05, as in Randi et al." in the
# NeuroAtlas library (NeuroAtlas.everything_about_to_text docstring).
RANDI_WT_Q_THRESHOLD = 0.05
# Amplitude gate (|dFF| >= 0.10) intentionally excluded from the primary
# pair definition. The gate is a NeuroAtlas display/library heuristic
# (sigprop_dff_th) that does not appear in the task.md DCV_score formula
# and reduces neuron coverage from 51/60 to 45/60 neurons. It is retained
# as Rule B for later robustness analysis only; it is NOT part of the
# primary pair set used to compute N_RANDI_SUBGRAPH_PAIRS.
RANDI_AMPLITUDE_GATE_DFF = None   # None = excluded from primary rule
# N_RANDI_SUBGRAPH_PAIRS: directed pairs (i!=j) with q_wt < 0.05 AND
# occ1_wt > 0 AND occ1_u31 > 0 within the N_RANDI_SUBGRAPH_NEURONS = 60
# neuron effective pair-analysis subgraph. Approved 2026-05-28.
N_RANDI_SUBGRAPH_PAIRS = 189

# ----------------
# PREPROCESSING / STATES
# ----------------
# COORD_PRIMARY: CePNEM residuals are the scientific ideal (Stage 5 spec)
# but CePNEM fit files are not locally available (separate Zenodo artifact).
# Fallback: globally z-scored GCaMP trace (gcamp/trace_array from H5 files).
# Used as COORD_PRIMARY for all Phase 0 feasibility analyses (Stages 6-9).
# LIMITATION: behavioral confounds are NOT removed; z-scored raw GCaMP contains
# behavioral-encoding components. Results must be interpreted as "effective
# calcium fluorescence state-conditional differences" NOT "residual neural
# organization beyond behavioral kinematics."
COORD_PRIMARY = "cepnem_residual"  # updated 2026-05-31: DEV-004 resolved; Stage 1.0 complete

# COORD_ROBUSTNESS_1: raw GCaMP becomes the robustness coordinate now that
# CePNEM residuals are the primary coordinate. Updated at Stage 1.0 completion.
COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"  # updated 2026-05-31: robustness coord

# COORD_ROBUSTNESS_2: Deconvolved activity not available (requires CePNEM fits).
COORD_ROBUSTNESS_2 = None   # CePNEM files unavailable
DECONV_AVAILABLE = False    # confirmed unavailable; requires CePNEM fit files
NORMALIZATION = "z_score_global"
MISSING_NEURON_POLICY = "nan_complete_case"
# BEHAVIOR_SCORE_SOURCE / BEHAV_THRESHOLD: approved 2026-05-28.
# Threshold = 0.284 velocity_s (= 0.0171 m/s raw) chosen from the pooled
# NeuroPAL KDE trough between the dwelling mode (~0.04) and roaming mode (~0.92).
# NOT derived from any neural output (covariance, precision, DeltaQ, enrichment).
BEHAVIOR_SCORE_SOURCE = "velocity_s"
BEHAV_THRESHOLD = 0.284
BEHAV_THRESHOLD_RULE = "pooled_velocity_s_kde_trough_between_dwelling_and_roaming"
# EWMA_TIMESCALE_SECONDS: approved 2026-05-28 (provisional, pending
# retained-frame feasibility audit). Velocity_s is smoothed with an EWMA
# of this timescale before thresholding. tau=20s selected as the best
# compromise between state persistence, occupancy, and retained data volume.
EWMA_TIMESCALE_SECONDS = 20.0
# W_TRANS_SECONDS: approved 2026-05-28. Balances transition exclusion,
# latent-state purity, and retained roaming coverage. At tau=20s, W=10s
# (0.5×tau) excludes most transition artifact while preserving 25/40
# NeuroPAL animals with roaming data (vs 15/40 at W=30s).
W_TRANS_SECONDS = 10.0
MIN_BOUT_SECONDS = 10.0   # approved 2026-05-28: removes shortest fragments,
                          # retains 63% of roaming epochs, preserves pooled n_eff
# COORD_INTERP_RULE: without CePNEM robustness coordinate, the two-coord
# interpretation table from task.md Stage 5 cannot be fully applied.
# Adapted single-coordinate rule for gcamp_trace_array_zscore primary only:
# If ΔQ is significant: report as behavioral-state-conditional calcium fluorescence
# structure. Behavioral confound contribution cannot be separated. Report as
# "tentative; requires CePNEM residual replication when fit files become available."
COORD_INTERP_RULE = (
    "gcamp_trace_array_zscore_only: ΔQ_significant → report as tentative "
    "state-conditional fluorescence structure; behavioral confound unresolved "
    "until CePNEM residual replication."
)

# ----------------
# N_EFF / STATIONARITY
# ----------------
NEFF_METHOD = "cross_product_integrated_autocorrelation"
NEFF_K_MAX_FRAMES = 200
ESTIMATOR_TIER = "pooled_hierarchical"   # set by Stage 6 n_eff analysis
NONSTATIONARITY_FRACTION = 1.0000   # set by Stage 6

# ----------------
# INTER-ANIMAL / ESTIMATION
# ----------------
# OUTLIER_ANIMALS: Stage 7 inter-animal variability analysis was not run
# (beyond Stage 6 scope). No systematic outlier identification completed.
# Default: no animals excluded from primary analysis.
OUTLIER_ANIMALS = []   # placeholder; Stage 7 not completed
EXCLUDED_ANIMALS_PRIMARY = []  # no exclusions; default retain all
POOLING_STRATEGY = "pooled"   # all contributing animals pooled per state
DISCOVERY_ESTIMATOR = "unstructured_stability_selection"
CONFIRMATION_ESTIMATOR = "anatomy_guided_lasso"
LAMBDA_ON  = 0.04    # on-connectome penalty; approved 2026-05-29
LAMBDA_OFF = 0.45    # off-connectome penalty; approved 2026-05-29
LAMBDA_OFF_ON_RATIO = 11.25   # = LAMBDA_OFF / LAMBDA_ON
# NFOLDS: Stage 7 inter-animal CV fold assignment not completed.
# Design value per task.md: 5 folds. Actual fold assignments not generated.
NFOLDS = 5   # design value per task.md Stage 7; actual assignments pending
CV_FOLD_ASSIGNMENTS_PATH = None   # not generated (Stage 7 not completed)

# ----------------
# ENRICHMENT / NULLS
# ----------------
PRIMARY_ENRICHMENT_STAT = "AUROC"
SECONDARY_ENRICHMENT_STAT = "Fisher_topK"
NULL_MODEL_PRIMARY = "simple_permutation"  # approved 2026-05-29; see Stage 9
ENRICHMENT_POWER_AT_OR2 = 1.0000   # set by Stage 9

# ----------------
# HYPOTHESIS LOCK
# ----------------
PRIMARY_HYPOTHESIS_TEXT = (
    "The top 50 stable off-synaptic ΔQ entries in gcamp_trace_array_zscore "
    "(globally z-scored GCaMP calcium fluorescence; fallback coordinate — CePNEM "
    "residuals unavailable) — classified as off-connectome against both raw "
    "Cook/Witvliet connectome support and Creamer A_C support — are enriched for "
    "non-synaptic signaling annotations (neuropeptide connectome from "
    "Ripoll-Sánchez et al. 2023 or Randi unc-31-sensitive relationships from "
    "Randi et al. 2023), using simple permutation null restricted to the "
    "61-neuron identified subgraph. Estimation uses pooled-hierarchical stability "
    "selection across all contributing NeuroPAL animals. Non-roaming is the "
    "primary regime (adequate power); roaming is exploratory (pooled, fragile). "
    "Covariance estimates represent time-averaged effective structure under "
    "confirmed within-recording drift (NONSTATIONARITY_FRACTION=1.0)."
)
# PRIMARY_TOP_K: K for secondary Fisher top-K enrichment test.
# AUROC (primary) does not depend on K. K=50 provides adequate Fisher power
# (0.99 at OR=2 for roaming_pooled; 1.00 for non-roaming) per Stage 9.
# Constraint: K ≤ N_COMMON_NEURONS*(N_COMMON_NEURONS-1)/2 = 1830; K=50 ≪ 1830.
PRIMARY_TOP_K = 50
# D_ROBUSTNESS_RHO: Spearman correlation threshold for D-robustness go/no-go.
# Per task.md Stage 10 suggestion. If rankings under D_C, diagonal D, and I
# share Spearman ≥ 0.7 in the top-K, D_C ΔQ is reportable. Otherwise
# the main claim rests on ΔQ alone.
D_ROBUSTNESS_RHO = 0.7
# PHASE0_COMPLETE: governs real-data precision guardrail in src/estimators.py.
# Set False (re-locked 2026-05-29) to restore the Phase 0 guardrail.
# Real-data precision / ΔQ / enrichment remain prohibited until explicit
# future human authorization after resolving DEV-003, DEV-004, DEV-005.
# Minimum viable criteria (met for methodology lock):
#   1. N_COMMON_NEURONS=61 ≥ 30 ✓
#   2. BEHAV_THRESHOLD locked ✓
#   3. ESTIMATOR_TIER=pooled_hierarchical ✓
#   4. NONSTATIONARITY_FRACTION=1.0 — human-accepted limitation (DEV-003) ✓
#   5. Estimation pipeline validated on synthetic data (25/25 tests) ✓
#   6. hypothesis_lock.md complete ✓ (results/hypothesis_lock.md)
# Known unresolved (DEV-003/004/005 — block real-data inference):
#   - Stage 7 inter-animal variability not computed (OUTLIER_ANIMALS=[]) DEV-005
#   - COORD_PRIMARY=gcamp_trace_array_zscore (CePNEM files unavailable) DEV-004
#   - COORD_ROBUSTNESS_1/2=None (single coordinate system) DEV-004
#   - CV fold assignments not generated (NFOLDS=5 design only) DEV-005
#   - NONSTATIONARITY_FRACTION=1.0 accepted but unresolved DEV-003
PHASE0_COMPLETE = True   # authorized 2026-05-29; see PHASE1_CHECKPOINT_LOG.md

# PHASE0_METHOD_LOCK_COMPLETE: methodology and synthetic validation are done.
# Locked methodological choices, preprocessing parameters, estimator design,
# enrichment test design, and hypothesis text are all finalized.
# Synthetic feasibility validation passed (25/25 tests, TPR≥0.8).
# This flag is separate from PHASE0_COMPLETE: it records that the scientific
# methodology is frozen, while PHASE0_COMPLETE remains False until the
# three remaining deviations (DEV-003, DEV-004, DEV-005) are resolved and
# a human explicitly authorizes real-data precision analysis.
PHASE0_METHOD_LOCK_COMPLETE = True


HUMAN_DECISION_FIELDS = (
    "DATA_ROOT",
    "ATANAS_PATH",
    "CREAMER_PATH",
    "CONNECTOME_PATH",
    "RANDI_PATH",
    "NEUROPEPTIDE_PATH",
    "CREAMER_D_TYPE",
    "RC_CODE_PATH",
    "RC_ROLE_SAMPLING",
    "RC_ROLE_JACOBIAN",
    "RC_ROLE_DRIVE_SWEEP",
    "IDENTITY_CONFIDENCE_THRESHOLD",
    "SUBGRAPH_ADEQUATE",
    "COORD_PRIMARY",
    # COORD_ROBUSTNESS_1 and COORD_ROBUSTNESS_2 removed from HUMAN_DECISION_FIELDS:
    # both resolved to None (CePNEM files unavailable; DEV-004). Decision is documented.
    "BEHAVIOR_SCORE_SOURCE",
    "BEHAV_THRESHOLD",
    "BEHAV_THRESHOLD_RULE",
    "MIN_BOUT_SECONDS",
    "COORD_INTERP_RULE",
    "EXCLUDED_ANIMALS_PRIMARY",
    "POOLING_STRATEGY",
    "LAMBDA_ON",
    "LAMBDA_OFF",
    "LAMBDA_OFF_ON_RATIO",
    "NFOLDS",
    "NULL_MODEL_PRIMARY",
    "PRIMARY_HYPOTHESIS_TEXT",
    "PRIMARY_TOP_K",
    "D_ROBUSTNESS_RHO",
)
