# phase2_config.py
# Phase 2 configuration — all estimator parameters locked after Stage 0-V.
#
# PHASE2_ACTIVE = False
# Human supervisor must set PHASE2_ACTIVE = True after reviewing the
# Stage 0-V.8 parameter lock package and completing all checkpoint items.
# See: results/phase2/stage0v/v8_parameter_lock_package.md
#
# Parameters locked by Stage 0-V validation (2026-06-01).
# No parameter below the lock boundary may change after PHASE2_ACTIVE = True.

# ── Administrative state ─────────────────────────────────────────────────────

PHASE2_ACTIVE  = True           # SET BY HUMAN: 2026-06-01 — Stage 1 authorized
PHASE2_STATUS  = "stage1_authorized"
PHASE2_CREATED = "2026-05-31"

# ── Estimator identification ──────────────────────────────────────────────────

PHASE2_ESTIMATOR          = "pairwise_stability_glasso_plus_anatomy_admm"
PHASE2_MISSINGNESS_MODEL  = "pairwise_available_case"
PHASE2_VALIDATION_STATUS  = "stage0v_complete"   # V.1–V.6, V.7C all PASS

# ── Subgraph ─────────────────────────────────────────────────────────────────

PHASE2_N_NEURONS            = 61
PHASE2_NEURON_SELECTION_METHOD = "marginal_presence_ge_80pct_40recordings"

# ── ══════════════════════════════════════════════════════════════════════════
#    LOCKED PARAMETERS — DO NOT MODIFY AFTER PHASE2_ACTIVE = True
# ══════════════════════════════════════════════════════════════════════════ ──

# Pairwise covariance assembly
MISSING_NEURON_POLICY             = "pairwise_available_case"
MIN_COPRESENCE_RECORDINGS         = 9      # SET BY HUMAN: 2026-06-01
                                           # Rationale: min observed = 9 (3 roaming pairs);
                                           # all retain n_eff > 40; no bootstrap failures;
                                           # validation included these pairs. No exclusions.

# PSD projection
PSD_PROJECTION_METHOD             = "eigenvalue_clipping"
PSD_EIGENVALUE_FLOOR              = 1e-6   # V.2: clip fraction = 0.000

# Stability selection (discovery estimator)
STABILITY_SELECTION_RESAMPLE_UNIT = "recording"
STABILITY_SELECTION_LAMBDA        = 0.15   # V.3 + DEV-P2-002; TPR=0.973, FPR=0.033
N_BOOTSTRAP_RESAMPLES             = 25     # V.4; variance converged
STABILITY_THRESHOLD               = 0.75   # V.4; Youden-optimal; TPR=0.90, FPR=0.023

# Anatomy-guided ADMM lasso (confirmation estimator)
LAMBDA_ON                         = 0.01   # V.5 + V.6; TPR=0.992, FPR=0.020
LAMBDA_OFF                        = 0.10   # V.5 + V.6; ratio=10; confirmed in V.6
LAMBDA_OFF_ON_RATIO               = 10.0

# Enrichment test
PRIMARY_TOP_K                     = 20     # V.7C Fisher calibration; type-I=0.040, power=1.000
PRIMARY_ENRICHMENT_STAT           = "AUROC"
SECONDARY_ENRICHMENT_STAT         = "Fisher_topK"
NULL_MODEL_PRIMARY                = "simple_permutation"
NULL_MODEL_SECONDARY              = "degree_preserving_permutation"

# Enrichment validation design (synthetic; does not enter real-data analysis)
P_SIGNAL_VALIDATION_MIN           = 12     # DEV-P2-003; first P satisfying AUROC power ≥ 0.60
P_SIGNAL_VALIDATION               = 13     # DEV-P2-003; operating point (one above minimum)
AUROC_POWER_VALIDATED             = 0.685  # V.7C at P=13, effect=0.20
AUROC_TYPE1_VALIDATED             = 0.035  # V.7C
FISHER_POWER_K20_VALIDATED        = 1.000  # V.7C
FISHER_TYPE1_K20_VALIDATED        = 0.040  # V.7C

# ── Inherited parameters (read-only; source of truth is phase0_config.py) ───
# Locked in Phase 0/1. Reproduced here for reference only. Do not modify.

_INHERITED_BEHAV_THRESHOLD           = 0.284
_INHERITED_EWMA_TIMESCALE_SECONDS    = 20.0
_INHERITED_W_TRANS_SECONDS           = 10.0
_INHERITED_MIN_BOUT_SECONDS          = 10.0
_INHERITED_SYNAPSE_COUNT_THRESHOLD   = 1
_INHERITED_NORMALIZATION             = "z_score_global"
_INHERITED_LR_POLICY                 = "separate"
_INHERITED_COORD_PRIMARY             = "cepnem_residual"
_INHERITED_COORD_ROBUSTNESS_1        = "gcamp_trace_array_zscore"
_INHERITED_D_ROBUSTNESS_RHO          = 0.7
_INHERITED_RANDI_WT_Q_THRESHOLD      = 0.05

# ── Regime thresholds (established by V.7C) ───────────────────────────────────

PHASE2_NEFF_OPTIMISTIC_THRESHOLD  = None   # not yet established; set in Stage 1.5
PHASE2_NEFF_MIDDLE_THRESHOLD      = None
PHASE2_TPR_OPTIMISTIC             = 0.973  # V.3 at effect=0.2, lambda=0.15
PHASE2_TPR_MIDDLE                 = None   # not tested; conservative regime not assessed
