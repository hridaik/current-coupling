"""
Stage 6: Acceptance tests P1-A through P1-D.
All must pass before simulation is unlocked.
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase7b.audit import load_labels, build_label_dict, verify_label_hash, log_event
from scripts.phase7b.acceptance import run_all_acceptance_tests, check_all_acceptance_tests_passed


def run():
    print('=' * 60)
    print('STAGE 6: Acceptance tests P1-A through P1-D')
    print('=' * 60)

    # Verify hash at V2 checkpoint before running tests
    print('\nCheckpoint V2: verifying hash before metrics...')
    try:
        verify_label_hash(checkpoint='V2')
        print('  V2: PASS')
    except Exception as e:
        print(f'  V2: FAIL — {e}')
        sys.exit(1)

    # Load committed labels and A
    records = load_labels()
    a_path  = os.path.join(cfg.GROUND_TRUTH_DIR, '_stage2_A.npy')
    if not os.path.exists(a_path):
        print('ERROR: Stage 2 A_sparse not found. Run run_stage2.py first.')
        sys.exit(1)
    A = np.load(a_path)

    # Rebuild labels_dict for P1-D hash tests
    labels_dict = build_label_dict(records, A)

    print(f'\nLoaded {len(records)} committed label records.')
    print('Running all acceptance tests...\n')

    results = run_all_acceptance_tests(labels_dict, records, A)

    print()
    print('Summary:')
    for test in ['P1-A', 'P1-B', 'P1-C', 'P1-D']:
        info = results[test]
        status = 'PASS' if info['passed'] else 'FAIL'
        print(f'  {status:4s}  {test}')
        details = info['details']
        if test == 'P1-A':
            print(f'         weak_fraction={details["weak_fraction"]:.4f} '
                  f'(threshold={details["max_weak_allowed"]}), '
                  f'n_C={details["n_c_pairs"]}')
        elif test == 'P1-B':
            print(f'         counts={details["counts"]}')
            if details['violations']:
                print(f'         violations: {details["violations"]}')
        elif test == 'P1-C':
            print(f'         mismatches={details["n_mismatches"]}')
        elif test == 'P1-D':
            for k, v in details['sub_tests'].items():
                sub_status = 'PASS' if v else 'FAIL'
                print(f'         {sub_status:4s}  {k}')

    print()
    if results['all_passed']:
        print('All acceptance tests PASSED.')
        print('Verifying gate function...')
        try:
            check_all_acceptance_tests_passed()
            print('Gate function: OK (simulation unlocked)')
        except RuntimeError as e:
            print(f'Gate function ERROR: {e}')
            sys.exit(1)
        print()
        print('STAGE 6 PASSED')
    else:
        failed = [t for t in ['P1-A','P1-B','P1-C','P1-D'] if not results[t]['passed']]
        print(f'Acceptance tests FAILED: {failed}')
        print('STAGE 6 FAILED — simulation remains blocked')
        sys.exit(1)


if __name__ == '__main__':
    run()
