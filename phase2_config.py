# phase2_config.py
# Phase 2 administrative configuration.
# Status: INITIALIZING — no scientific parameters are locked here.
# Created: 2026-05-31
#
# This file contains only administrative placeholders.
# No estimator has been selected.
# No missing-data model has been authorized.
# No scientific parameters have been locked.
#
# Phase 2 methodology will be established through the Stage 0 checkpoint process.
# See phase2_task.md and PHASE2_AGENTS.md for governance rules.
#
# Do not commit scientific parameter choices to this file without a preceding
# human checkpoint recorded in PHASE2_CHECKPOINT_LOG.md.

# ── Administrative state ─────────────────────────────────────────────────────

PHASE2_ACTIVE = False
PHASE2_STATUS = "initializing"
PHASE2_CREATED = "2026-05-31"

# ── Estimator placeholders ────────────────────────────────────────────────────
# To be determined in Stage 0 checkpoint.

PHASE2_ESTIMATOR = None
PHASE2_MISSINGNESS_MODEL = None
PHASE2_VALIDATION_STATUS = "not_started"

# ── Subgraph placeholder ──────────────────────────────────────────────────────
# N_COMMON_NEURONS is not carried forward as a locked requirement.
# The achievable neuron set will be determined after Stage 0-V validation.

PHASE2_N_NEURONS = None
PHASE2_NEURON_SELECTION_METHOD = None

# ── Regularization placeholders ───────────────────────────────────────────────
# LAMBDA_ON and LAMBDA_OFF from Phase 0/1 are not automatically transferred.
# They will be re-validated in Stage 0-V under the Phase 2 estimator.

PHASE2_LAMBDA_ON = None
PHASE2_LAMBDA_OFF = None

# ── Regime thresholds (to be established in Stage 0-V) ───────────────────────

PHASE2_NEFF_OPTIMISTIC_THRESHOLD = None
PHASE2_NEFF_MIDDLE_THRESHOLD = None
PHASE2_TPR_OPTIMISTIC = None
PHASE2_TPR_MIDDLE = None

# ── Inherited parameters (read-only reference; source of truth is phase0_config.py) ──
# These are reproduced here for reference only. Do not modify.
# Behavioral segmentation carries forward unchanged from Phase 0/1.

_INHERITED_BEHAV_THRESHOLD = 0.284
_INHERITED_EWMA_TIMESCALE_SECONDS = 20.0
_INHERITED_W_TRANS_SECONDS = 10.0
_INHERITED_MIN_BOUT_SECONDS = 10.0
_INHERITED_SYNAPSE_COUNT_THRESHOLD = 1
_INHERITED_COORD_PRIMARY = "cepnem_residual"
_INHERITED_COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"
