"""
Verdict engine validation — Phase 8B-0.

Tests all verdict branches (SUCCESS, PARTIAL_SUCCESS, FAILURE, INCONCLUSIVE),
all failure-mode overrides (FO-1 through FO-5), benchmark validity checks
(BV-1 through BV-5), and invariant properties (determinism, schema, hash-lock).

Does NOT use benchmark outputs. Does NOT reveal labels.
All inputs are synthetic metric values.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase8 import config8 as cfg
from scripts.phase8 import verdict as vrd

PASS = 'PASS'
FAIL = 'FAIL'
results = []


def check(name: str, expected, actual, tol: float | None = None) -> None:
    if tol is not None:
        ok = abs(float(actual) - float(expected)) <= tol
    else:
        ok = (expected == actual)
    status = PASS if ok else FAIL
    results.append({'name': name, 'status': status, 'expected': expected, 'actual': actual})
    print(f'  {status:4s}  {name}: expected={expected!r}, got={actual!r}')


def check_bool(name: str, expected: bool, actual: bool) -> None:
    ok = (expected == actual)
    status = PASS if ok else FAIL
    results.append({'name': name, 'status': status})
    print(f'  {status:4s}  {name}: expected={expected}, got={actual}')


def run_all():
    print('=' * 60)
    print('Verdict engine validation')
    print('=' * 60)

    # -----------------------------------------------------------------------
    # T1: SUCCESS branch — all thresholds met
    # -----------------------------------------------------------------------
    print('\nT1: SUCCESS — all thresholds exceeded')
    v = vrd.determine_verdict(
        macro_auroc=0.75, c_auroc=0.70, lr_auroc=0.72,
        b4_c_auroc=0.60,  # margin = 0.10 > 0.05
        ci_95=None,
    )
    check('T1 verdict', 'SUCCESS', v['verdict'])
    check('T1 sub_category', None, v['sub_category'])
    check_bool('T1 rationale non-empty', True, len(v['rationale']) > 0)

    # -----------------------------------------------------------------------
    # T2: SUCCESS — exactly at thresholds
    # -----------------------------------------------------------------------
    print('\nT2: SUCCESS — exactly at thresholds (edge case)')
    v2 = vrd.determine_verdict(
        macro_auroc=0.70, c_auroc=0.65, lr_auroc=0.65,
        b4_c_auroc=0.60,  # margin = 0.05 exactly
    )
    check('T2 verdict', 'SUCCESS', v2['verdict'])

    # -----------------------------------------------------------------------
    # T3: FAILURE — macro_auroc below partial threshold
    # -----------------------------------------------------------------------
    print('\nT3: FAILURE — macro_auroc < 0.60')
    v3 = vrd.determine_verdict(
        macro_auroc=0.55, c_auroc=0.70, lr_auroc=0.70, b4_c_auroc=0.50
    )
    check('T3 verdict', 'FAILURE', v3['verdict'])
    check_bool('T3 sub_category mentions MacroAUROC', True,
               'MacroAUROC' in v3.get('sub_category', ''))

    # -----------------------------------------------------------------------
    # T4: FAILURE — c_auroc below partial threshold
    # -----------------------------------------------------------------------
    print('\nT4: FAILURE — c_auroc < 0.55')
    v4 = vrd.determine_verdict(
        macro_auroc=0.72, c_auroc=0.50, lr_auroc=0.70, b4_c_auroc=0.40
    )
    check('T4 verdict', 'FAILURE', v4['verdict'])
    check_bool('T4 sub_category mentions C-AUROC', True,
               'C-AUROC' in v4.get('sub_category', ''))

    # -----------------------------------------------------------------------
    # T5: FAILURE — lr_auroc below partial threshold
    # -----------------------------------------------------------------------
    print('\nT5: FAILURE — lr_auroc < 0.55')
    v5 = vrd.determine_verdict(
        macro_auroc=0.72, c_auroc=0.68, lr_auroc=0.50, b4_c_auroc=0.40
    )
    check('T5 verdict', 'FAILURE', v5['verdict'])

    # -----------------------------------------------------------------------
    # T6: PARTIAL_SUCCESS — in partial range
    # -----------------------------------------------------------------------
    print('\nT6: PARTIAL_SUCCESS — all in partial range')
    v6 = vrd.determine_verdict(
        macro_auroc=0.63, c_auroc=0.60, lr_auroc=0.61, b4_c_auroc=0.56
    )
    check('T6 verdict', 'PARTIAL_SUCCESS', v6['verdict'])
    check_bool('T6 sub_category set', True, v6.get('sub_category') is not None)

    # -----------------------------------------------------------------------
    # T7: PARTIAL_SUCCESS PS-2 — c_auroc ≥ 0.65 but macro < 0.60
    # -----------------------------------------------------------------------
    print('\nT7: PARTIAL_SUCCESS PS-2 — high C-AUROC, low MacroAUROC')
    v7 = vrd.determine_verdict(
        macro_auroc=0.62, c_auroc=0.68, lr_auroc=0.62, b4_c_auroc=0.50
    )
    check('T7 verdict', 'PARTIAL_SUCCESS', v7['verdict'])
    check('T7 sub_category PS-2', 'PS-2', v7.get('sub_category'))

    # -----------------------------------------------------------------------
    # T8: PARTIAL_SUCCESS — doesn't beat B4 margin (still partial, not failure)
    # -----------------------------------------------------------------------
    print('\nT8: PARTIAL_SUCCESS — in success range but fails B4 margin → not SUCCESS')
    v8 = vrd.determine_verdict(
        macro_auroc=0.72, c_auroc=0.68, lr_auroc=0.70,
        b4_c_auroc=0.65,  # margin = 0.03 < 0.05
    )
    check('T8 verdict is not SUCCESS (B4 margin not met)', 'PARTIAL_SUCCESS', v8['verdict'])

    # -----------------------------------------------------------------------
    # T9: INCONCLUSIVE-CI — CI spans threshold boundary
    # -----------------------------------------------------------------------
    print('\nT9: INCONCLUSIVE-CI — CI spans success threshold')
    v9 = vrd.determine_verdict(
        macro_auroc=0.73, c_auroc=0.68, lr_auroc=0.68,
        b4_c_auroc=0.58,
        ci_95={
            'macro_auroc': {'lower': 0.55, 'upper': 0.85},  # spans both thresholds
            'c_auroc':     {'lower': 0.62, 'upper': 0.72},
            'lr_auroc':    {'lower': 0.63, 'upper': 0.73},
        },
    )
    check('T9 verdict INCONCLUSIVE when CI spans', 'INCONCLUSIVE', v9['verdict'])
    check('T9 sub_category INCONCLUSIVE-CI', 'INCONCLUSIVE-CI', v9['sub_category'])

    # -----------------------------------------------------------------------
    # T10: ci_spans logic — CI that does NOT span
    # -----------------------------------------------------------------------
    print('\nT10: CI that does not span → SUCCESS maintained')
    v10 = vrd.determine_verdict(
        macro_auroc=0.75, c_auroc=0.70, lr_auroc=0.72,
        b4_c_auroc=0.60,
        ci_95={
            'macro_auroc': {'lower': 0.68, 'upper': 0.82},  # both > success
            'c_auroc':     {'lower': 0.65, 'upper': 0.75},
            'lr_auroc':    {'lower': 0.65, 'upper': 0.79},
        },
    )
    check('T10 SUCCESS when CI does not span thresholds', 'SUCCESS', v10['verdict'])

    # -----------------------------------------------------------------------
    # T11: FO-1 — high weak fraction triggers benchmark failure
    # -----------------------------------------------------------------------
    print('\nT11: FO-1 — weak C-pair fraction above trigger')
    base_verdict, _ = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.70, 'mean_strength_c': 0.10,
         'all_y_variance': 1.0, 'all_y_finite': True},
    )
    check('T11 FO-1: FAILURE → INCONCLUSIVE_BENCHMARK_FAILURE',
          'INCONCLUSIVE_BENCHMARK_FAILURE', base_verdict)

    # FO-1 not triggered below threshold
    v_no_fo1, _ = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.50, 'mean_strength_c': 0.10,
         'all_y_variance': 1.0, 'all_y_finite': True},
    )
    check('T11 FO-1: no override when weak_fraction ≤ 0.60', 'FAILURE', v_no_fo1)

    # -----------------------------------------------------------------------
    # T12: FO-2 — mean path strength below trigger
    # -----------------------------------------------------------------------
    print('\nT12: FO-2 — mean C path strength near zero')
    v_fo2, fo2_overrides = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.30, 'mean_strength_c': 0.001,
         'all_y_variance': 1.0, 'all_y_finite': True},
    )
    check('T12 FO-2: FAILURE → INCONCLUSIVE_BENCHMARK_FAILURE',
          'INCONCLUSIVE_BENCHMARK_FAILURE', v_fo2)
    check_bool('T12 FO-2 listed in overrides', True,
               any('FO-2' in s for s in fo2_overrides))

    # -----------------------------------------------------------------------
    # T13: FO-3 — n(C) below minimum
    # -----------------------------------------------------------------------
    print('\nT13: FO-3 — n(C) < 200')
    v_fo3, fo3_ov = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.30, 'mean_strength_c': 0.10,
         'n_c': 150, 'all_y_variance': 1.0, 'all_y_finite': True},
    )
    check('T13 FO-3: FAILURE → INCONCLUSIVE_BENCHMARK_FAILURE',
          'INCONCLUSIVE_BENCHMARK_FAILURE', v_fo3)
    check_bool('T13 FO-3 in overrides', True, any('FO-3' in s for s in fo3_ov))

    # -----------------------------------------------------------------------
    # T14: FO-4 — y variance collapsed
    # -----------------------------------------------------------------------
    print('\nT14: FO-4 — y variance collapsed')
    v_fo4, fo4_ov = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.30, 'mean_strength_c': 0.10,
         'all_y_variance': 1e-6, 'all_y_finite': True},
    )
    check('T14 FO-4: FAILURE → INCONCLUSIVE_BENCHMARK_FAILURE',
          'INCONCLUSIVE_BENCHMARK_FAILURE', v_fo4)

    # -----------------------------------------------------------------------
    # T15: FO-5 — NaN in observations
    # -----------------------------------------------------------------------
    print('\nT15: FO-5 — non-finite observations')
    v_fo5, fo5_ov = vrd.apply_failure_mode_overrides(
        'FAILURE',
        {'weak_fraction_c': 0.30, 'mean_strength_c': 0.10,
         'all_y_variance': 1.0, 'all_y_finite': False},
    )
    check('T15 FO-5: FAILURE → INCONCLUSIVE_BENCHMARK_FAILURE',
          'INCONCLUSIVE_BENCHMARK_FAILURE', v_fo5)

    # -----------------------------------------------------------------------
    # T16: FO overrides only apply to FAILURE
    # -----------------------------------------------------------------------
    print('\nT16: FO overrides do NOT apply to SUCCESS')
    v_suc, ov_suc = vrd.apply_failure_mode_overrides(
        'SUCCESS',
        {'weak_fraction_c': 0.90, 'mean_strength_c': 0.0001,
         'all_y_variance': 1e-8, 'all_y_finite': False},
    )
    check('T16 SUCCESS not changed by FO context', 'SUCCESS', v_suc)
    check_bool('T16 no overrides applied to SUCCESS', True, len(ov_suc) == 0)

    # -----------------------------------------------------------------------
    # T17: BV checks — all pass with correct counts
    # -----------------------------------------------------------------------
    print('\nT17: Benchmark validity checks BV-1 through BV-5')
    labels_valid = {(i, j): 'C' for i in range(30) for j in range(30) if i != j}
    labels_valid.update({(i+50, j+50): 'M' for i in range(8) for j in range(8) if i != j})
    labels_valid.update({(i, j+70): 'N' for i in range(5) for j in range(10)})

    bv = vrd.check_benchmark_validity(
        labels_dict           = labels_valid,
        b4_direct_auroc       = 0.60,
        blinding_audit_passed = True,
        output_hash_verified  = True,
    )
    check_bool('BV-1: n(C) ≥ 100', True, bv['BV-1'])
    check_bool('BV-2: n(M) ≥ 30', True, bv['BV-2'])
    check_bool('BV-3: B4 direct ≥ 0.52', True, bv['BV-3'])
    check_bool('BV-4: blinding passed', True, bv['BV-4'])
    check_bool('BV-5: output hash verified', True, bv['BV-5'])
    check_bool('benchmark_validity_passed returns True', True,
               vrd.benchmark_validity_passed(bv))

    # -----------------------------------------------------------------------
    # T18: BV-1 fails when n(C) < 100
    # -----------------------------------------------------------------------
    print('\nT18: BV-1 fails when n(C) insufficient')
    labels_small_c = {(0, 1): 'C', (2, 3): 'M'}
    bv2 = vrd.check_benchmark_validity(
        labels_dict           = labels_small_c,
        b4_direct_auroc       = 0.60,
        blinding_audit_passed = True,
        output_hash_verified  = True,
    )
    check_bool('BV-1 fails with n(C)=1', False, bv2['BV-1'])
    check_bool('benchmark_validity_passed returns False', False,
               vrd.benchmark_validity_passed(bv2))

    # -----------------------------------------------------------------------
    # T19: BV-3 fails when B4 direct AUROC too low
    # -----------------------------------------------------------------------
    print('\nT19: BV-3 fails when B4 direct AUROC below 0.52')
    bv3 = vrd.check_benchmark_validity(
        labels_dict           = labels_valid,
        b4_direct_auroc       = 0.48,
        blinding_audit_passed = True,
        output_hash_verified  = True,
    )
    check_bool('BV-3 fails with B4_direct=0.48', False, bv3['BV-3'])

    # -----------------------------------------------------------------------
    # T20: Determinism — same inputs always produce same verdict
    # -----------------------------------------------------------------------
    print('\nT20: Determinism')
    def make_verdict():
        return vrd.determine_verdict(
            macro_auroc=0.68, c_auroc=0.62, lr_auroc=0.64, b4_c_auroc=0.55,
            ci_95={'macro_auroc': {'lower': 0.60, 'upper': 0.75},
                   'c_auroc': {'lower': 0.55, 'upper': 0.69},
                   'lr_auroc': {'lower': 0.57, 'upper': 0.71}},
        )
    v_det1 = make_verdict()
    v_det2 = make_verdict()
    check('Determinism: same verdict', v_det1['verdict'], v_det2['verdict'])
    check('Determinism: same sub_category', v_det1['sub_category'], v_det2['sub_category'])

    # -----------------------------------------------------------------------
    # T21: Output schema validation
    # -----------------------------------------------------------------------
    print('\nT21: Output schema — required keys present')
    required_keys = {'verdict', 'sub_category', 'primary_metrics', 'threshold_checks',
                     'ci_spans_threshold', 'rationale'}
    v_schema = vrd.determine_verdict(
        macro_auroc=0.72, c_auroc=0.67, lr_auroc=0.68, b4_c_auroc=0.60
    )
    for key in required_keys:
        check_bool(f'Schema: key {key!r} present', True, key in v_schema)

    # threshold_checks has all required sub-keys
    expected_tc_keys = {'macro_auroc_success', 'macro_auroc_partial',
                        'c_auroc_success', 'c_auroc_partial',
                        'lr_auroc_success', 'lr_auroc_partial',
                        'beats_b4_by_margin'}
    for key in expected_tc_keys:
        check_bool(f'Schema: threshold_checks[{key!r}] present', True,
                   key in v_schema['threshold_checks'])

    # -----------------------------------------------------------------------
    # T22: condition_comparisons helper
    # -----------------------------------------------------------------------
    print('\nT22: compute_condition_comparisons')
    metrics_by_cond = {
        'oracle_z':    {'macro_auroc': 0.72, 'auroc': {'C': 0.68, 'LR': 0.70}},
        'blind_z':     {'macro_auroc': 0.64, 'auroc': {'C': 0.60, 'LR': 0.62}},
        'neural_state':{'macro_auroc': 0.58, 'auroc': {'C': 0.54, 'LR': 0.56}},
    }
    diffs = vrd.compute_condition_comparisons(metrics_by_cond)
    check_bool('blind_z in diffs', True, 'blind_z' in diffs)
    check_bool('oracle_z not in diffs (reference)', False, 'oracle_z' in diffs)
    check('blind_z delta_macro_auroc', -0.08, diffs['blind_z']['delta_macro_auroc'], tol=1e-6)
    check('neural_state delta_c_auroc', -0.14, diffs['neural_state']['delta_c_auroc'], tol=1e-6)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print()
    n_pass = sum(1 for r in results if r['status'] == PASS)
    n_fail = sum(1 for r in results if r['status'] == FAIL)
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')

    if n_fail:
        print('\nFailed checks:')
        for r in results:
            if r['status'] == FAIL:
                print(f'  FAIL  {r["name"]}: expected={r["expected"]!r}, got={r["actual"]!r}')
        return False
    print('All verdict validation checks PASSED.')
    return True


if __name__ == '__main__':
    ok = run_all()
    sys.exit(0 if ok else 1)
