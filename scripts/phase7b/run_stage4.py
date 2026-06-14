"""
Stage 4: Hash-lock commit and Checkpoint V1 verification.
Depends on Stages 2 and 3.
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.graph import build_A_sparse
from scripts.phase7b.labels import generate_labels, class_counts
from scripts.phase7b.audit import (
    build_label_dict, commit_labels, verify_label_hash, log_event
)


def run():
    print('=' * 60)
    print('STAGE 4: Hash-lock commit (Checkpoint V1)')
    print('=' * 60)

    # Load A from stage 2 (deterministic — same seeds produce same A)
    a_path = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_A.npy')
    if not os.path.exists(a_path):
        print('ERROR: Stage 2 output not found. Run run_stage2.py first.')
        sys.exit(1)
    A = np.load(a_path)
    print(f'Loaded A_sparse: {A.shape}')

    # Load records from stage 3
    records_path = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage3_records.json')
    if not os.path.exists(records_path):
        print('ERROR: Stage 3 output not found. Run run_stage3.py first.')
        sys.exit(1)
    with open(records_path) as f:
        records = json.load(f)
    counts = class_counts(records)
    print(f'Loaded {len(records)} label records: {counts}')

    # Compute spectral abscissa for logging
    abscissa = float(__import__('numpy').max(__import__('numpy').linalg.eigvals(A).real))

    # Build canonical label dict
    labels_dict = build_label_dict(records, A)

    print('\nCommitting labels (writing files + setting read-only)...')
    label_hash = commit_labels(labels_dict, A, n_resample=0, spectral_abscissa=abscissa)
    print(f'  Label hash: {label_hash}')
    print(f'  labels.json: {cfg.LABELS_PATH}')
    print(f'  labels.sha256: {cfg.LABELS_HASH_PATH}')

    print('\nCheckpoint V1: verifying hash...')
    ok = verify_label_hash(checkpoint='V1')
    print(f'  V1: {"PASS" if ok else "FAIL"}')

    log_event({'event': 'stage4_complete', 'label_hash': label_hash, 'v1_ok': ok})

    print()
    if not ok:
        print('STAGE 4 FAILED')
        sys.exit(1)
    print('STAGE 4 PASSED')


if __name__ == '__main__':
    run()
