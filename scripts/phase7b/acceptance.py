"""
Acceptance tests P1-A through P1-D — Phase 7B Stage 6.

Implements all gate tests from phase7a_acceptance_tests.md.
All four must pass before simulation is permitted.
"""

import hashlib
import json
import os
import numpy as np
from . import config as cfg
from .audit import (
    canonicalize, compute_label_hash, compute_file_hash,
    verify_label_hash, load_labels, log_event, read_audit_log,
)


# ---------------------------------------------------------------------------
# P1-A: Near-zero H2 path strength check
# ---------------------------------------------------------------------------

def test_p1a_path_strength(
    records: list[dict],
    A: np.ndarray,
) -> tuple[bool, dict]:
    """
    P1-A: For all C-labeled pairs, compute max_{h in SA} |A[h,i]| * |A[j,h]|.
    Fail if > 30% of C pairs have max path strength < 0.01.

    Returns (passed, details).
    """
    c_pairs = [(r['i'], r['j']) for r in records if r['label'] == 'C']
    n_c = len(c_pairs)

    if n_c == 0:
        return False, {'error': 'No C-labeled pairs found'}

    sa_list = sorted(cfg.SA)
    weak_count = 0
    strengths = []

    for i, j in c_pairs:
        max_strength = max(
            abs(A[h, i]) * abs(A[j, h])
            for h in sa_list
        )
        strengths.append(max_strength)
        if max_strength < cfg.P1A_WEAK_STRENGTH_THRESHOLD:
            weak_count += 1

    weak_fraction = weak_count / n_c
    passed = weak_fraction <= cfg.P1A_MAX_WEAK_FRACTION

    details = {
        'n_c_pairs':       n_c,
        'weak_count':      weak_count,
        'weak_fraction':   round(weak_fraction, 4),
        'threshold':       cfg.P1A_WEAK_STRENGTH_THRESHOLD,
        'max_weak_allowed': cfg.P1A_MAX_WEAK_FRACTION,
        'min_strength':    round(float(np.min(strengths)), 6),
        'median_strength': round(float(np.median(strengths)), 6),
        'max_strength':    round(float(np.max(strengths)), 6),
        'passed':          passed,
    }

    log_event({'event': 'acceptance_test', 'test': 'P1-A', 'result': 'PASS' if passed else 'FAIL', **details})
    return passed, details


# ---------------------------------------------------------------------------
# P1-B: Class count bounds check
# ---------------------------------------------------------------------------

def test_p1b_class_counts(records: list[dict]) -> tuple[bool, dict]:
    """
    P1-B: Check that each class count falls within its specified bounds.

    Returns (passed, details).
    """
    from .labels import class_counts
    counts = class_counts(records)
    violations = []

    for lbl, (lo, hi) in cfg.P1B_BOUNDS.items():
        cnt = counts.get(lbl, 0)
        if not (lo <= cnt <= hi):
            violations.append(f'{lbl}={cnt} outside [{lo},{hi}]')

    passed = len(violations) == 0
    details = {
        'counts':     counts,
        'bounds':     cfg.P1B_BOUNDS,
        'violations': violations,
        'passed':     passed,
    }

    log_event({'event': 'acceptance_test', 'test': 'P1-B', 'result': 'PASS' if passed else 'FAIL', **details})
    return passed, details


# ---------------------------------------------------------------------------
# P1-C: Label reproducibility check
# ---------------------------------------------------------------------------

def test_p1c_label_reproducibility(
    committed_records: list[dict],
    A: np.ndarray,
) -> tuple[bool, dict]:
    """
    P1-C: Regenerate labels from A_sparse from scratch; must exactly match committed labels.
    Zero mismatches required.

    Returns (passed, details).
    """
    from .labels import generate_labels

    fresh_records = generate_labels(A, cfg.SA)

    # Index committed by (i, j) for fast lookup
    committed_map = {(r['i'], r['j']): r['label'] for r in committed_records}
    fresh_map     = {(r['i'], r['j']): r['label'] for r in fresh_records}

    all_keys = set(committed_map.keys()) | set(fresh_map.keys())
    mismatches = []
    for key in sorted(all_keys):
        c_lbl = committed_map.get(key, 'MISSING')
        f_lbl = fresh_map.get(key, 'MISSING')
        if c_lbl != f_lbl:
            mismatches.append({'pair': key, 'committed': c_lbl, 'fresh': f_lbl})

    passed = len(mismatches) == 0
    details = {
        'n_committed': len(committed_records),
        'n_fresh':     len(fresh_records),
        'n_mismatches': len(mismatches),
        'example_mismatches': mismatches[:5],
        'passed':      passed,
    }

    log_event({'event': 'acceptance_test', 'test': 'P1-C', 'result': 'PASS' if passed else 'FAIL',
               'n_mismatches': len(mismatches)})
    return passed, details


# ---------------------------------------------------------------------------
# P1-D: Hash system integrity (4 sub-tests)
# ---------------------------------------------------------------------------

def test_p1d_hash_integrity(labels_dict: dict) -> tuple[bool, dict]:
    """
    P1-D: Four sub-tests for hash system correctness.

    P1-D-1: Deterministic hashing (same input → same hash)
    P1-D-2: Disk round-trip (hash of labels.json matches stored hash)
    P1-D-3: Tamper detection (mutating a label changes the hash)
    P1-D-4: Format compliance (canonical JSON is compact, no whitespace)

    Returns (passed, details).
    """
    sub_results = {}

    # --- P1-D-1: Deterministic ---
    hash_a = compute_label_hash(labels_dict)
    hash_b = compute_label_hash(labels_dict)
    sub_results['P1-D-1-deterministic'] = hash_a == hash_b

    # --- P1-D-2: Disk match ---
    try:
        disk_ok = verify_label_hash(checkpoint='V1')
        sub_results['P1-D-2-disk-match'] = disk_ok
    except (ValueError, FileNotFoundError) as e:
        sub_results['P1-D-2-disk-match'] = False
        sub_results['P1-D-2-error'] = str(e)

    # --- P1-D-3: Tamper detection ---
    import copy
    tampered = copy.deepcopy(labels_dict)
    # Mutate the first label
    first = tampered['labels'][0]
    orig_lbl = first['label']
    first['label'] = 'X'  # invalid, definitely different
    hash_tampered = compute_label_hash(tampered)
    sub_results['P1-D-3-tamper-detection'] = hash_tampered != hash_a
    # Restore (defensive)
    first['label'] = orig_lbl

    # --- P1-D-4: Format compliance ---
    canonical_bytes = canonicalize(labels_dict)
    canonical_str = canonical_bytes.decode('utf-8')
    # Compact: no leading/trailing whitespace per token, no indentation
    has_newlines = '\n' in canonical_str
    has_indent   = '  ' in canonical_str[:200]  # check start
    # Re-parse and re-serialize to verify round-trip
    reparsed     = json.loads(canonical_str)
    rehashed     = compute_label_hash(reparsed)
    sub_results['P1-D-4-format-compact']    = not has_newlines and not has_indent
    sub_results['P1-D-4-roundtrip-stable']  = rehashed == hash_a

    all_passed = all(
        v for k, v in sub_results.items() if isinstance(v, bool)
    )

    details = {'sub_tests': sub_results, 'passed': all_passed}
    log_event({'event': 'acceptance_test', 'test': 'P1-D',
               'result': 'PASS' if all_passed else 'FAIL', 'sub_tests': sub_results})
    return all_passed, details


# ---------------------------------------------------------------------------
# Gate function — must be called as first line of simulate()
# ---------------------------------------------------------------------------

def check_all_acceptance_tests_passed(audit_log_path: str = cfg.AUDIT_LOG_PATH) -> None:
    """
    Gate function: verify all 4 acceptance tests have PASS entries in the audit log.
    Raises RuntimeError if any test is missing or failed.
    This is the MANDATORY first line of any simulation function.
    """
    required = {'P1-A', 'P1-B', 'P1-C', 'P1-D'}
    passed_tests = set()

    if not os.path.exists(audit_log_path):
        raise RuntimeError(
            f'Audit log not found at {audit_log_path}. '
            'Run all acceptance tests before simulation.'
        )

    events = read_audit_log()
    for event in events:
        if event.get('event') == 'acceptance_test' and event.get('result') == 'PASS':
            passed_tests.add(event.get('test'))

    missing = required - passed_tests
    if missing:
        raise RuntimeError(
            f'Simulation blocked: acceptance tests not passed: {sorted(missing)}. '
            'All of P1-A, P1-B, P1-C, P1-D must pass before simulation.'
        )

    log_event({'event': 'simulation_gate_passed', 'passed_tests': sorted(passed_tests)})


# ---------------------------------------------------------------------------
# Run all acceptance tests in sequence
# ---------------------------------------------------------------------------

def run_all_acceptance_tests(
    labels_dict: dict,
    records: list[dict],
    A: np.ndarray,
) -> dict:
    """
    Run P1-A, P1-B, P1-C, P1-D in order. Return summary dict.
    """
    results = {}

    print('Running P1-A (path strength)...', flush=True)
    ok_a, det_a = test_p1a_path_strength(records, A)
    results['P1-A'] = {'passed': ok_a, 'details': det_a}

    print('Running P1-B (class counts)...', flush=True)
    ok_b, det_b = test_p1b_class_counts(records)
    results['P1-B'] = {'passed': ok_b, 'details': det_b}

    print('Running P1-C (reproducibility)...', flush=True)
    ok_c, det_c = test_p1c_label_reproducibility(records, A)
    results['P1-C'] = {'passed': ok_c, 'details': det_c}

    print('Running P1-D (hash integrity)...', flush=True)
    ok_d, det_d = test_p1d_hash_integrity(labels_dict)
    results['P1-D'] = {'passed': ok_d, 'details': det_d}

    all_passed = ok_a and ok_b and ok_c and ok_d
    results['all_passed'] = all_passed

    log_event({
        'event':      'all_acceptance_tests_complete',
        'all_passed': all_passed,
        'P1-A':       ok_a,
        'P1-B':       ok_b,
        'P1-C':       ok_c,
        'P1-D':       ok_d,
    })

    return results
