"""
Phase 8A frozen constants — evaluation thresholds, metric IDs, output paths.

All values derive from phase8a_*.md documents. Nothing may be changed
after Phase 8B begins. Changes here are protocol violations.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GROUND_TRUTH_DIR   = os.path.join(PROJECT_ROOT, 'ground_truth')
LABELS_PATH        = os.path.join(GROUND_TRUTH_DIR, 'labels.json')
LABELS_HASH_PATH   = os.path.join(GROUND_TRUTH_DIR, 'labels.sha256')
A_SPARSE_PATH      = os.path.join(GROUND_TRUTH_DIR, 'A_sparse.npy')
DATASET_DIR        = os.path.join(PROJECT_ROOT, 'results', 'phase7c', 'canonical', 'data')
PHASE8B_DIR        = os.path.join(PROJECT_ROOT, 'results', 'phase8b')
OUTPUTS_DIR        = os.path.join(PHASE8B_DIR, 'framework_outputs')
METRICS_DIR        = os.path.join(PHASE8B_DIR, 'metrics')
EVAL_AUDIT_PATH    = os.path.join(PHASE8B_DIR, 'evaluation_audit.jsonl')
VERDICT_PATH       = os.path.join(PHASE8B_DIR, 'verdict.json')

# ---------------------------------------------------------------------------
# Committed hashes (from phase7b and phase7c freeze)
# ---------------------------------------------------------------------------
COMMITTED_LABEL_HASH = 'dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081'
COMMITTED_DATASET_META_HASH = '7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed'

# ---------------------------------------------------------------------------
# Class taxonomy
# ---------------------------------------------------------------------------
CLASSES     = ['S', 'C', 'M', 'N']
LR_CLASSES  = frozenset({'C', 'M'})    # SAREACHABLE=True
DIR_CLASSES = frozenset({'S', 'M'})    # DIRECT=True

# ---------------------------------------------------------------------------
# Committed class counts (from locked labels, confirmed in phase7c)
# ---------------------------------------------------------------------------
COMMITTED_CLASS_COUNTS = {'S': 497, 'C': 857, 'M': 89, 'N': 8457}
N_PAIRS = 9900

# ---------------------------------------------------------------------------
# Evaluation conditions (from phase8a_evaluation_spec §4)
# ---------------------------------------------------------------------------
CONDITIONS = ['oracle_z', 'blind_z', 'neural_state', 'weak_z', 'strong_z']
PRIMARY_CONDITION = 'oracle_z'

# ---------------------------------------------------------------------------
# Primary metric thresholds (phase8a_success_criteria §2.1)
# ---------------------------------------------------------------------------
THRESHOLD_SUCCESS_MACRO_AUROC = 0.70
THRESHOLD_PARTIAL_MACRO_AUROC = 0.60

THRESHOLD_SUCCESS_C_AUROC = 0.65
THRESHOLD_PARTIAL_C_AUROC = 0.55

THRESHOLD_SUCCESS_LR_AUROC = 0.65
THRESHOLD_PARTIAL_LR_AUROC = 0.55

# Framework must exceed B4 C-AUROC by this margin for SUCCESS
THRESHOLD_FRAMEWORK_VS_B4_C_MARGIN = 0.05

# ---------------------------------------------------------------------------
# Statistical uncertainty (phase8a_metric_registry §7)
# ---------------------------------------------------------------------------
N_BOOTSTRAP = 2000
BOOTSTRAP_CI_LEVEL = 0.95          # 95% CI
BONFERRONI_N_PRIMARY = 3           # 3 primary metrics
ALPHA_BONFERRONI = 0.05 / BONFERRONI_N_PRIMARY   # ≈ 0.0167

# ---------------------------------------------------------------------------
# Benchmark validity thresholds (phase8a_success_criteria §1)
# ---------------------------------------------------------------------------
BV1_MIN_C_COUNT = 100
BV2_MIN_M_COUNT = 30
BV3_MIN_B4_DIRECT_AUROC = 0.52

# ---------------------------------------------------------------------------
# Failure-mode override triggers (phase8a_success_criteria §5)
# ---------------------------------------------------------------------------
FO1_WEAK_FRACTION_TRIGGER = 0.60   # > 60% of C pairs near-zero strength
FO2_MEAN_STRENGTH_TRIGGER  = 0.005  # mean C pair strength < 0.005

# ---------------------------------------------------------------------------
# Baselines (phase8a_baseline_spec)
# ---------------------------------------------------------------------------
# B4 Glasso
B4_ALPHA_GRID = [0.005, 0.01, 0.02, 0.05, 0.10]
B4_TRAIN_RUNS = [0, 1, 2, 3]
B4_VAL_RUN    = 4
B4_SOFTMAX_TEMP = 5.0

B3_SOFTMAX_TEMP = 5.0
B5_SOFTMAX_TEMP = 5.0

# B6 module oracle probabilities
MODULE_SIZE = 25   # neurons per module (M1=0-24, M2=25-49, etc.)
B6_WITHIN_MODULE_PROBS  = {'S': 0.40, 'C': 0.10, 'M': 0.10, 'N': 0.40}
B6_BETWEEN_MODULE_PROBS = {'S': 0.05, 'C': 0.30, 'M': 0.02, 'N': 0.63}

# ---------------------------------------------------------------------------
# Top-K enrichment K values (phase8a_metric_registry §4)
# ---------------------------------------------------------------------------
TOPK_VALUES = [50, 100, 200, 500]

# ---------------------------------------------------------------------------
# ECE bin count (phase8a_metric_registry §3)
# ---------------------------------------------------------------------------
ECE_N_BINS = 10

# ---------------------------------------------------------------------------
# M-class AUROC CI width flag threshold
# ---------------------------------------------------------------------------
M_AUROC_CI_WIDTH_FLAG = 0.20
