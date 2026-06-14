"""
Audit / hash-lock system — Phase 7B Stage 4.

Implements the exact procedures from phase7a_hashlock_system.md.
"""

import hashlib
import json
import os
import time
import numpy as np
from . import config as cfg


# ---------------------------------------------------------------------------
# Canonical serialization (phase7a_hashlock_system §1)
# ---------------------------------------------------------------------------

def build_label_dict(records: list[dict], A_sparse: np.ndarray) -> dict:
    """
    Build the full top-level dict ready for serialization/hashing.
    Sorted by (i, j) as required by the canonical format.
    """
    from .labels import class_counts
    counts = class_counts(records)
    sorted_records = sorted(records, key=lambda r: (r['i'], r['j']))

    return {
        'metadata': {
            'version':         'phase6b_v1',
            'n_pairs':         len(sorted_records),
            'n_obs':           cfg.N_OBS,
            'master_seed':     cfg.MASTER_SEED,
            'class_counts':    counts,
            'sa_set':          sorted(cfg.SA),
            'generated_at_unix': int(time.time()),
        },
        'labels': sorted_records,
    }


def canonicalize(labels_dict: dict) -> bytes:
    """Return canonical UTF-8 bytes for hashing (compact JSON, no whitespace)."""
    return json.dumps(
        labels_dict,
        separators=(',', ':'),
        sort_keys=False,
        ensure_ascii=True,
    ).encode('utf-8')


def compute_label_hash(labels_dict: dict) -> str:
    """SHA-256 hex digest of canonical form."""
    return hashlib.sha256(canonicalize(labels_dict)).hexdigest()


def compute_matrix_hash(A: np.ndarray) -> str:
    """SHA-256 of A_sparse bytes (float64, C order)."""
    return hashlib.sha256(A.astype(np.float64).tobytes(order='C')).hexdigest()


def compute_file_hash(path: str) -> str:
    """SHA-256 of raw file bytes."""
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Hash commit (phase7a_hashlock_system §2–4)
# ---------------------------------------------------------------------------

def commit_labels(
    labels_dict: dict,
    A_sparse: np.ndarray,
    n_resample: int,
    spectral_abscissa: float,
) -> str:
    """
    Write labels.json, labels.sha256, A_sparse.npy, A_sparse.sha256,
    construction_params.json/.sha256 to GROUND_TRUTH_DIR.
    Set labels.json to read-only.
    Returns the label hash.
    """
    os.makedirs(cfg.GROUND_TRUTH_DIR, exist_ok=True)

    # 1. Write labels.json
    canonical_bytes = canonicalize(labels_dict)
    with open(cfg.LABELS_PATH, 'wb') as f:
        f.write(canonical_bytes)

    # 2. Compute and write hash
    label_hash = hashlib.sha256(canonical_bytes).hexdigest()
    with open(cfg.LABELS_HASH_PATH, 'w') as f:
        f.write(f'{label_hash}  labels.json\n')

    # 3. Write A_sparse
    np.save(cfg.A_SPARSE_PATH, A_sparse)
    A_hash = compute_matrix_hash(A_sparse)
    with open(cfg.A_HASH_PATH, 'w') as f:
        f.write(f'{A_hash}  A_sparse.npy\n')

    # 4. Write construction params
    params = _build_params_record()
    params_bytes = json.dumps(params, separators=(',', ':'),
                               sort_keys=True, ensure_ascii=True).encode('utf-8')
    with open(cfg.PARAMS_PATH, 'wb') as f:
        f.write(params_bytes)
    params_hash = hashlib.sha256(params_bytes).hexdigest()
    with open(cfg.PARAMS_HASH_PATH, 'w') as f:
        f.write(f'{params_hash}  construction_params.json\n')

    # 5. Set labels.json read-only
    os.chmod(cfg.LABELS_PATH, 0o444)

    # 6. Log to audit trail
    log_event({
        'event':              'hash_committed',
        'label_file_hash':    label_hash,
        'A_sparse_hash':      A_hash,
        'params_hash':        params_hash,
        'hash_file_path':     cfg.LABELS_HASH_PATH,
        'labels_readonly':    True,
        'spectral_abscissa':  spectral_abscissa,
        'n_resample_attempts': n_resample,
    })

    return label_hash


def _build_params_record() -> dict:
    """Serialize the frozen parameter values for archival."""
    return {
        'N_OBS': cfg.N_OBS, 'N_H1': cfg.N_H1, 'N_H2': cfg.N_H2,
        'N_MODULES': cfg.N_MODULES, 'N_PER_MODULE': cfg.N_PER_MODULE,
        'N_H1_PER_MODULE': cfg.N_H1_PER_MODULE,
        'P_WITHIN': cfg.P_WITHIN, 'P_BETWEEN': cfg.P_BETWEEN,
        'P_H1_IN': cfg.P_H1_IN, 'P_H1_OUT': cfg.P_H1_OUT,
        'P_H2_IN': cfg.P_H2_IN, 'P_H2_OUT': cfg.P_H2_OUT,
        'SIGMA_OBS_OBS': cfg.SIGMA_OBS_OBS, 'SIGMA_H1': cfg.SIGMA_H1,
        'SIGMA_H2_IN': cfg.SIGMA_H2_IN, 'SIGMA_H2_OUT': cfg.SIGMA_H2_OUT,
        'A_SELF': cfg.A_SELF, 'MASTER_SEED': cfg.MASTER_SEED,
        'SA': sorted(cfg.SA),
        'H2_TARGETS': {str(k): sorted(v) for k, v in cfg.H2_TARGETS.items()},
    }


# ---------------------------------------------------------------------------
# Verification (phase7a_hashlock_system §3)
# ---------------------------------------------------------------------------

def verify_label_hash(checkpoint: str = 'V1') -> bool:
    """
    Verify labels.json matches the committed hash in labels.sha256.
    Logs the result. Raises ValueError on mismatch.
    """
    if not os.path.exists(cfg.LABELS_HASH_PATH):
        log_event({'event': 'hash_file_missing', 'checkpoint': checkpoint})
        raise FileNotFoundError(
            f'Hash file {cfg.LABELS_HASH_PATH} missing — labels not committed.'
        )

    with open(cfg.LABELS_PATH, 'rb') as f:
        content = f.read()
    computed = hashlib.sha256(content).hexdigest()

    with open(cfg.LABELS_HASH_PATH) as f:
        stored = f.read().strip().split()[0]

    result = 'PASS' if computed == stored else 'FAIL'
    log_event({
        'event':          'hash_verification',
        'checkpoint':     checkpoint,
        'result':         result,
        'stored_hash':    stored,
        'computed_hash':  computed,
    })

    if result == 'FAIL':
        raise ValueError(
            f'HASH MISMATCH at {checkpoint}: stored={stored}, computed={computed}. '
            'Label file has been modified. Evaluation is invalid.'
        )
    return True


def load_labels() -> list[dict]:
    """Load and return the committed label records from disk."""
    with open(cfg.LABELS_PATH, 'r', encoding='utf-8') as f:
        d = json.load(f)
    return d['labels']


# ---------------------------------------------------------------------------
# Audit log (phase7a_hashlock_system §5)
# ---------------------------------------------------------------------------

def log_event(event: dict) -> None:
    """Append a timestamped JSON event to the audit log."""
    os.makedirs(cfg.GROUND_TRUTH_DIR, exist_ok=True)
    if 'timestamp_unix' not in event:
        event = {'timestamp_unix': int(time.time()), **event}
    with open(cfg.AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=True) + '\n')


def read_audit_log() -> list[dict]:
    """Return all audit log events as a list of dicts."""
    if not os.path.exists(cfg.AUDIT_LOG_PATH):
        return []
    events = []
    with open(cfg.AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events
