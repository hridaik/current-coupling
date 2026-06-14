"""
Parameter registry — Phase 7B reference implementation.

All scientific constants originate from phase6b_parameter_registry.md.
No hard-coded values appear in any other module.
Parameters are referenced by their registry IDs (P01–P34).
"""

import os

# ---------------------------------------------------------------------------
# Category 1 — Network structure (P01–P06)
# ---------------------------------------------------------------------------
N_OBS = 100          # P01: observed neurons
N_H1 = 32            # P02: total H1 hidden interneurons
N_H2 = 8             # P03: total H2 global modulator neurons
N_MODULES = 4        # P04: number of functional modules
N_PER_MODULE = 25    # P05: observed neurons per module (derived: N_OBS / N_MODULES)
N_H1_PER_MODULE = 8  # P06: H1 neurons per module (derived: N_H1 / N_MODULES)
N_TOTAL = N_OBS + N_H1 + N_H2  # 140

# ---------------------------------------------------------------------------
# Neuron index ranges (0-indexed throughout)
# ---------------------------------------------------------------------------
# Observed neurons: 0 – 99
# H1 neurons:       100 – 131  (8 per module)
# H2 neurons:       132 – 139
MODULE_OBS = {
    'M1': list(range(0, 25)),
    'M2': list(range(25, 50)),
    'M3': list(range(50, 75)),
    'M4': list(range(75, 100)),
}
MODULE_H1 = {
    'M1': list(range(100, 108)),
    'M2': list(range(108, 116)),
    'M3': list(range(116, 124)),
    'M4': list(range(124, 132)),
}
# Map each observed index to its module name
OBS_TO_MODULE = {}
for _mod, _idxs in MODULE_OBS.items():
    for _i in _idxs:
        OBS_TO_MODULE[_i] = _mod

# Map each H1 index to its assigned module
H1_TO_MODULE = {}
for _mod, _idxs in MODULE_H1.items():
    for _h in _idxs:
        H1_TO_MODULE[_h] = _mod

# H2 neuron assignments (0-indexed: 132–139)
# Each H2 is assigned exactly two target modules (phase6b_architecture_spec §1.4)
H2_TARGETS = {
    132: frozenset({'M1', 'M2'}),
    133: frozenset({'M1', 'M2'}),
    134: frozenset({'M3', 'M4'}),
    135: frozenset({'M3', 'M4'}),
    136: frozenset({'M1', 'M3'}),
    137: frozenset({'M2', 'M4'}),
    138: frozenset({'M1', 'M4'}),
    139: frozenset({'M2', 'M3'}),
}

SA = frozenset(H2_TARGETS.keys())  # {132, 133, 134, 135, 136, 137, 138, 139}
ALL_H1 = frozenset(range(100, 132))
ALL_H2 = SA

# All hidden neurons
ALL_HIDDEN = ALL_H1 | ALL_H2

# ---------------------------------------------------------------------------
# Category 2 — Graph connectivity (P07–P12)
# ---------------------------------------------------------------------------
P_WITHIN = 0.15   # P07: within-module obs-obs edge probability
P_BETWEEN = 0.03  # P08: between-module obs-obs edge probability
P_H1_IN  = 0.30   # P09: obs → H1 probability
P_H1_OUT = 0.25   # P10: H1 → obs probability
P_H2_IN  = 0.20   # P11: obs → H2 probability (H2 receives from target-module obs)
P_H2_OUT = 0.20   # P12: H2 → obs probability (H2 projects to target-module obs)

# ---------------------------------------------------------------------------
# Category 3 — Weight distributions (P13–P17)
# ---------------------------------------------------------------------------
SIGMA_OBS_OBS = 0.30   # P13: obs-obs coupling weight std
SIGMA_H1     = 0.25    # P14: H1 in/out weight std
SIGMA_H2_IN  = 0.25    # P15: obs→H2 weight std
SIGMA_H2_OUT = 0.35    # P16: H2→obs weight std
A_SELF       = -1.5    # P17: self-inhibition on all neurons (diagonal of A)

# ---------------------------------------------------------------------------
# Category 4 — State (P18–P23)
# ---------------------------------------------------------------------------
DIM_Z          = 1     # P18: latent state dimensionality (scalar)
THETA_Z        = 0.10  # P19: OU mean-reversion rate
SIGMA_Z        = 1.00  # P20: OU noise amplitude
GAMMA_H2       = 3.00  # P21: z-drive gain to H2 neurons (primary)
GAMMA_H2_WEAK  = 1.50  # P22: z-drive gain for weak_z condition
GAMMA_H2_STRONG = 6.00 # P23: z-drive gain for strong_z condition

# ---------------------------------------------------------------------------
# Category 5 — Diffusion (P24–P26)
# ---------------------------------------------------------------------------
D_0               = 1.00   # P24: baseline diagonal noise amplitude
EPS_LR            = 0.10   # P25: low-rank noise component amplitude
D_STATE_DEPENDENT = False  # P26: D does not vary with z

# ---------------------------------------------------------------------------
# Category 6 — Observation (P27–P29)
# ---------------------------------------------------------------------------
KAPPA_CA        = 0.50    # P27: calcium decay rate
SIGMA_OBS_NOISE = 0.10    # P28: measurement noise std
NONLINEARITY    = 'softplus'  # P29

# ---------------------------------------------------------------------------
# Category 7 — Simulation (P30–P34)
# ---------------------------------------------------------------------------
DT        = 0.10    # P30: Euler-Maruyama step size
T         = 50_000  # P31: total integration steps per run
T_WARMUP  = 2_000   # P32: warm-up steps discarded
T_EFF     = T - T_WARMUP  # effective steps: 48,000
R         = 5       # P33: number of independent runs
MASTER_SEED = 42    # P34: master random seed

# ---------------------------------------------------------------------------
# Sub-seed table (phase6b_architecture_spec §2.9)
# ---------------------------------------------------------------------------
SEEDS = {
    'oo_sparsity':  42,
    'h1_sparsity':  43,
    'h2_sparsity':  44,
    'oo_weights':   45,
    'h1_weights':   46,
    'h2_weights':   47,
    'D_lr_u':       48,
    # z and x seeds are 49+run_index and 60+run_index respectively
}

def z_seed(run_index: int) -> int:
    return 49 + run_index

def x_seed(run_index: int) -> int:
    return 60 + run_index

# Stability check: maximum resample attempts
MAX_RESAMPLE_ATTEMPTS = 10
SPECTRAL_ABSCISSA_THRESHOLD = -0.1  # must be strictly less than this

# ---------------------------------------------------------------------------
# Evaluation conditions
# ---------------------------------------------------------------------------
CONDITIONS = {
    'oracle_z':    {'gamma_H2': GAMMA_H2,        'provide_z': True,  'use_obs_model': True},
    'blind_z':     {'gamma_H2': GAMMA_H2,        'provide_z': False, 'use_obs_model': True},
    'neural_state':{'gamma_H2': GAMMA_H2,        'provide_z': True,  'use_obs_model': False},
    'weak_z':      {'gamma_H2': GAMMA_H2_WEAK,   'provide_z': True,  'use_obs_model': True},
    'strong_z':    {'gamma_H2': GAMMA_H2_STRONG, 'provide_z': True,  'use_obs_model': True},
}

# ---------------------------------------------------------------------------
# Acceptance test thresholds (phase7a_acceptance_tests.md)
# ---------------------------------------------------------------------------
P1A_WEAK_STRENGTH_THRESHOLD = 0.01   # path strength below this is "weak"
P1A_MAX_WEAK_FRACTION       = 0.30   # at most 30% of C pairs may be weak
P1B_BOUNDS = {
    'S': (400, 700),
    'C': (450, 950),
    'M': (5,   200),
    'N': (7000, 9000),
}

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
GROUND_TRUTH_DIR = os.path.join(PROJECT_ROOT, 'ground_truth')
LABELS_PATH      = os.path.join(GROUND_TRUTH_DIR, 'labels.json')
LABELS_HASH_PATH = os.path.join(GROUND_TRUTH_DIR, 'labels.sha256')
A_SPARSE_PATH    = os.path.join(GROUND_TRUTH_DIR, 'A_sparse.npy')
A_HASH_PATH      = os.path.join(GROUND_TRUTH_DIR, 'A_sparse.sha256')
PARAMS_PATH      = os.path.join(GROUND_TRUTH_DIR, 'construction_params.json')
PARAMS_HASH_PATH = os.path.join(GROUND_TRUTH_DIR, 'construction_params.sha256')
AUDIT_LOG_PATH   = os.path.join(GROUND_TRUTH_DIR, 'audit_log.jsonl')

# ---------------------------------------------------------------------------
# Derived consistency assertions (checked at import time)
# ---------------------------------------------------------------------------
assert N_PER_MODULE * N_MODULES == N_OBS, "N_PER_MODULE * N_MODULES must equal N_OBS"
assert N_H1_PER_MODULE * N_MODULES == N_H1, "H1 count mismatch"
assert len(SA) == N_H2, f"SA size {len(SA)} != N_H2 {N_H2}"
assert N_TOTAL == 140, f"N_TOTAL = {N_TOTAL}, expected 140"
assert len(ALL_H1) == N_H1
assert not (ALL_H1 & SA), "H1 and SA must be disjoint"
