"""
Stage 3: Label generation and CK-L* / CK-H* checks.
Depends on Stage 2 having saved A_sparse.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.labels import generate_labels, class_counts
from scripts.phase7b.checks import run_label_checks


def run():
    print('=' * 60)
    print('STAGE 3: Label generation + CK-L* / CK-H* checks')
    print('=' * 60)

    # Load A from stage 2
    a_path = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_A.npy')
    if not os.path.exists(a_path):
        print('ERROR: Stage 2 output not found. Run run_stage2.py first.')
        sys.exit(1)
    A = np.load(a_path)
    print(f'Loaded A_sparse: {A.shape}')

    print('\nGenerating labels...')
    records = generate_labels(A, cfg.SA)
    counts  = class_counts(records)
    print(f'  Total pairs: {len(records)}')
    print(f'  Class counts: {counts}')

    print('\nRunning CK-L* and CK-H* checks...')
    results = run_label_checks(records, A)

    n_pass = n_fail = 0
    for name, passed, msg in results:
        status = 'PASS' if passed else 'FAIL'
        print(f'  {status:4s}  {name}: {msg}')
        if passed:
            n_pass += 1
        else:
            n_fail += 1

    print()
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')

    # Save records for stage 4
    import json
    records_path = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage3_records.json')
    with open(records_path, 'w') as f:
        json.dump(records, f, separators=(',', ':'))
    print(f'Saved {len(records)} label records to {records_path}')

    if n_fail:
        print('STAGE 3 FAILED')
        sys.exit(1)
    print('STAGE 3 PASSED')


if __name__ == '__main__':
    run()
