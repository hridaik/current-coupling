"""
Blinding validation — Phase 8B-0.

Demonstrates that:
  1. Forbidden file paths cannot be accessed through the input bundle
  2. Labels remain hidden until blinding checks pass
  3. Output freeze (hash + chmod) works correctly
  4. Event sequence is enforced (out-of-order access raises)
  5. BC-1 through BC-4 checks validate correctly

All tests use temporary files and directories. No benchmark data is accessed.
No labels are revealed outside the gated path.
"""

import hashlib
import json
import os
import stat
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PASS = 'PASS'
FAIL = 'FAIL'
results = []


def check_bool(name: str, expected: bool, actual: bool) -> None:
    ok = (expected == actual)
    status = PASS if ok else FAIL
    results.append({'name': name, 'status': status, 'expected': expected, 'actual': actual})
    print(f'  {status:4s}  {name}')


def check_raises(name: str, fn, exc_type=Exception) -> None:
    try:
        fn()
        status = FAIL
        results.append({'name': name, 'status': status, 'reason': 'Did not raise'})
        print(f'  {FAIL:4s}  {name}: expected {exc_type.__name__}, did not raise')
    except exc_type:
        status = PASS
        results.append({'name': name, 'status': status})
        print(f'  {PASS:4s}  {name}: raised {exc_type.__name__} as expected')
    except Exception as e:
        status = FAIL
        results.append({'name': name, 'status': status, 'reason': str(e)})
        print(f'  {FAIL:4s}  {name}: raised wrong exception type: {type(e).__name__}: {e}')


def make_minimal_output(pairs_probs: dict | None = None) -> str:
    """Write a minimal valid framework output JSON; return path."""
    tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w')
    preds = []
    if pairs_probs is None:
        for i in range(99):
            j = (i + 1) % 100
            if i != j:
                preds.append({
                    'i': i, 'j': j,
                    'class_prob': {'S': 0.25, 'C': 0.25, 'M': 0.25, 'N': 0.25},
                })
    else:
        for (i, j), cp in pairs_probs.items():
            preds.append({'i': i, 'j': j, 'class_prob': cp})
    json.dump({'metadata': {'method': 'test'}, 'predictions': preds}, tmp)
    tmp.close()
    return tmp.name


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run_all():
    print('=' * 60)
    print('Blinding validation')
    print('=' * 60)

    # Patch cfg paths to use temp dirs for all tests
    import scripts.phase8.config8 as cfg_orig
    import scripts.phase8.blinding as bld

    tmpdir = tempfile.mkdtemp(prefix='phase8_blind_validate_')
    orig_audit_path   = cfg_orig.EVAL_AUDIT_PATH
    orig_verdict_path = cfg_orig.VERDICT_PATH
    orig_phase8b_dir  = cfg_orig.PHASE8B_DIR
    orig_labels_path  = cfg_orig.LABELS_PATH

    try:
        # Redirect audit log to tmpdir
        tmp_audit  = os.path.join(tmpdir, 'eval_audit.jsonl')
        tmp_verdict = os.path.join(tmpdir, 'verdict.json')
        tmp_gt_dir  = os.path.join(tmpdir, 'ground_truth')
        tmp_labels  = os.path.join(tmp_gt_dir, 'labels.json')
        os.makedirs(tmp_gt_dir, exist_ok=True)

        cfg_orig.EVAL_AUDIT_PATH = tmp_audit
        cfg_orig.VERDICT_PATH    = tmp_verdict
        cfg_orig.PHASE8B_DIR     = tmpdir
        cfg_orig.LABELS_PATH     = tmp_labels

        # ----------------------------------------------------------------
        # T1: freeze_output_file hashes correctly and sets chmod 444
        # ----------------------------------------------------------------
        print('\nT1: Output file freeze — hash and chmod')
        tmp_out = make_minimal_output()
        expected_hash = sha256_file(tmp_out)
        recorded_hash = bld.freeze_output_file(tmp_out)
        check_bool('freeze_output_file returns correct SHA-256', True,
                   recorded_hash == expected_hash)
        mode = stat.S_IMODE(os.stat(tmp_out).st_mode)
        check_bool('freeze_output_file sets read-only (0o444)', True,
                   mode == 0o444)
        # Write back permissions for cleanup
        os.chmod(tmp_out, 0o644)
        os.unlink(tmp_out)

        # Write a fake labels file so BC-2 hash check doesn't FileNotFoundError
        with open(tmp_labels, 'w') as f:
            json.dump({'labels': [{'i': 0, 'j': 1, 'label': 'N'}]}, f)

        # ----------------------------------------------------------------
        # T2: Hash mismatch detection after tampering
        # ----------------------------------------------------------------
        print('\nT2: Hash mismatch → BC-1 fails')
        tmp_out2 = make_minimal_output()
        good_hash = sha256_file(tmp_out2)
        checks = bld.run_blinding_checks(
            output_path=tmp_out2,
            recorded_output_hash='0' * 64,  # wrong hash
            output_metadata={},
        )
        check_bool('BC-1 fails on hash mismatch', False, checks['BC-1'])
        # With correct hash it should pass
        os.chmod(tmp_out2, 0o644)
        checks_ok = bld.run_blinding_checks(
            output_path=tmp_out2,
            recorded_output_hash=good_hash,
            output_metadata={},
        )
        check_bool('BC-1 passes on correct hash', True, checks_ok['BC-1'])
        os.chmod(tmp_out2, 0o644)
        os.unlink(tmp_out2)

        # ----------------------------------------------------------------
        # T3: BC-2 label hash check
        # ----------------------------------------------------------------
        print('\nT3: Label hash integrity — BC-2')
        # Write a fake labels file with the wrong hash
        tmp_fake_labels = tmp_labels
        with open(tmp_fake_labels, 'w') as f:
            json.dump({'labels': [{'i': 0, 'j': 1, 'label': 'N'}]}, f)

        tmp_out3 = make_minimal_output()
        h3 = sha256_file(tmp_out3)
        checks3 = bld.run_blinding_checks(
            output_path=tmp_out3,
            recorded_output_hash=h3,
            output_metadata={},
        )
        check_bool('BC-2 fails when label file has wrong hash', False, checks3['BC-2'])
        os.chmod(tmp_out3, 0o644)
        os.unlink(tmp_out3)

        # ----------------------------------------------------------------
        # T4: BC-3 forbidden path detection in metadata
        # ----------------------------------------------------------------
        print('\nT4: Information barrier — BC-3 detects forbidden references')
        tmp_out4 = make_minimal_output()
        h4 = sha256_file(tmp_out4)

        # Metadata that references a forbidden path
        bad_metadata = {'input_files': ['/path/to/ground_truth/labels.json']}
        checks4 = bld.run_blinding_checks(
            output_path=tmp_out4,
            recorded_output_hash=h4,
            output_metadata=bad_metadata,
        )
        check_bool('BC-3 fails when metadata references ground_truth', False, checks4['BC-3'])

        # Clean metadata should pass BC-3
        good_metadata = {'method': 'current_velocity', 'run': 1}
        checks4b = bld.run_blinding_checks(
            output_path=tmp_out4,
            recorded_output_hash=h4,
            output_metadata=good_metadata,
        )
        check_bool('BC-3 passes on clean metadata', True, checks4b['BC-3'])
        os.chmod(tmp_out4, 0o644)
        os.unlink(tmp_out4)

        # ----------------------------------------------------------------
        # T5: audit_framework_code_paths detects forbidden symbols
        # ----------------------------------------------------------------
        print('\nT5: Framework code audit — forbidden path detection')
        tmp_clean   = tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w')
        tmp_dirty   = tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w')

        tmp_clean.write('def estimate(y):\n    return {}\n')
        tmp_clean.close()

        tmp_dirty.write(
            'import numpy\n'
            '# ground_truth labels loaded\n'
            'labels = load(ground_truth_path)\n'
        )
        tmp_dirty.close()

        clean_violations = bld.audit_framework_code_paths([tmp_clean.name])
        dirty_violations = bld.audit_framework_code_paths([tmp_dirty.name])

        check_bool('Clean code: no violations', True, len(clean_violations) == 0)
        check_bool('Code with "ground_truth": violations found', True,
                   len(dirty_violations) > 0)

        os.unlink(tmp_clean.name)
        os.unlink(tmp_dirty.name)

        # ----------------------------------------------------------------
        # T6: Event sequence enforcement
        # ----------------------------------------------------------------
        print('\nT6: Event sequence — assert_event_not_yet raises on order violation')

        # Clear audit log for clean sequence test
        if os.path.exists(tmp_audit):
            os.unlink(tmp_audit)

        # Simulate metrics_computed event directly in the log
        bld.log_eval_event({'event': 'metrics_computed', 'macro_auroc': 0.5})

        # Now trying to record framework_output (earlier in sequence) should fail
        check_raises(
            'assert_event_not_yet raises if later event already occurred',
            lambda: bld.assert_event_not_yet('framework_output_received'),
            RuntimeError,
        )

        # ----------------------------------------------------------------
        # T7: assert_event_completed raises if prerequisite missing
        # ----------------------------------------------------------------
        print('\nT7: assert_event_completed raises when prerequisite missing')

        # Fresh audit log
        if os.path.exists(tmp_audit):
            os.unlink(tmp_audit)

        # blinding_check_passed has not occurred
        check_raises(
            'assert_event_completed raises when blinding_check_passed missing',
            lambda: bld.assert_event_completed('blinding_check_passed'),
            RuntimeError,
        )

        # After logging it, should not raise
        bld.log_eval_event({'event': 'blinding_check_passed', 'all_passed': True})
        raised = False
        try:
            bld.assert_event_completed('blinding_check_passed')
        except RuntimeError:
            raised = True
        check_bool('assert_event_completed does not raise after event logged', False, raised)

        # ----------------------------------------------------------------
        # T8: build_input_bundle never reads ground_truth/ directory
        # ----------------------------------------------------------------
        print('\nT8: build_input_bundle path audit — no ground_truth open() calls')

        # Check for actual file-open calls to forbidden paths (comments OK)
        import inspect, ast
        src = inspect.getsource(bld.build_input_bundle)
        # Forbidden: any open() whose argument string contains ground_truth/ paths.
        # We verify by checking that LABELS_PATH/A_SPARSE_PATH/GROUND_TRUTH_DIR
        # config symbols are not passed to open()
        check_bool('build_input_bundle does not open LABELS_PATH',
                   True, 'LABELS_PATH' not in src)
        check_bool('build_input_bundle does not open A_SPARSE_PATH',
                   True, 'A_SPARSE_PATH' not in src)
        check_bool('build_input_bundle does not open GROUND_TRUTH_DIR',
                   True, 'GROUND_TRUTH_DIR' not in src)

        # ----------------------------------------------------------------
        # T9: load_labels_for_scoring is gated by blinding_check_passed
        # ----------------------------------------------------------------
        print('\nT9: load_labels_for_scoring requires blinding_check_passed')

        # Fresh audit log (no blinding_check_passed)
        if os.path.exists(tmp_audit):
            os.unlink(tmp_audit)

        check_raises(
            'load_labels_for_scoring raises without blinding_check_passed',
            lambda: bld.load_labels_for_scoring(),
            RuntimeError,
        )

        # ----------------------------------------------------------------
        # T10: get_completed_events returns correct set
        # ----------------------------------------------------------------
        print('\nT10: Event log reading')
        if os.path.exists(tmp_audit):
            os.unlink(tmp_audit)

        bld.log_eval_event({'event': 'evaluation_started'})
        bld.log_eval_event({'event': 'input_bundle_created'})
        completed = bld.get_completed_events()
        check_bool('evaluation_started in completed events', True,
                   'evaluation_started' in completed)
        check_bool('input_bundle_created in completed events', True,
                   'input_bundle_created' in completed)
        check_bool('framework_output_received NOT yet in events', True,
                   'framework_output_received' not in completed)

        # ----------------------------------------------------------------
        # T11: Verdict written + read-only after record_verdict
        # ----------------------------------------------------------------
        print('\nT11: Verdict recording — file frozen after write')
        if os.path.exists(tmp_audit):
            os.unlink(tmp_audit)

        # Need metrics_computed event before record_verdict
        bld.log_eval_event({'event': 'metrics_computed', 'macro_auroc': 0.75})
        test_verdict = {
            'verdict': 'SUCCESS',
            'primary_metrics': {'macro_auroc': 0.75, 'c_auroc': 0.70, 'lr_auroc': 0.72},
        }
        verdict_hash = bld.record_verdict(test_verdict)
        check_bool('record_verdict returns non-empty hash', True, len(verdict_hash) == 64)
        check_bool('verdict file exists', True, os.path.exists(tmp_verdict))
        vmode = stat.S_IMODE(os.stat(tmp_verdict).st_mode)
        check_bool('verdict file is read-only (0o444)', True, vmode == 0o444)

        # Allow cleanup
        os.chmod(tmp_verdict, 0o644)

        # ----------------------------------------------------------------
        # T12: REQUIRED_EVENT_ORDER has all mandatory events
        # ----------------------------------------------------------------
        print('\nT12: REQUIRED_EVENT_ORDER completeness')
        expected_events = {
            'evaluation_started',
            'input_bundle_created',
            'framework_output_received',
            'blinding_check_passed',
            'labels_loaded_for_scoring',
            'metrics_computed',
            'verdict_recorded',
            'labels_revealed_to_evaluator',
        }
        actual_events = set(bld.REQUIRED_EVENT_ORDER)
        check_bool('REQUIRED_EVENT_ORDER contains all 8 mandatory events',
                   True, expected_events == actual_events)

    finally:
        # Restore cfg paths
        cfg_orig.EVAL_AUDIT_PATH = orig_audit_path
        cfg_orig.VERDICT_PATH    = orig_verdict_path
        cfg_orig.PHASE8B_DIR     = orig_phase8b_dir
        cfg_orig.LABELS_PATH     = orig_labels_path
        # Cleanup temp files
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    print()
    n_pass = sum(1 for r in results if r['status'] == PASS)
    n_fail = sum(1 for r in results if r['status'] == FAIL)
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')

    if n_fail:
        print('\nFailed checks:')
        for r in results:
            if r['status'] == FAIL:
                print(f'  FAIL  {r["name"]}')
        return False
    print('All blinding validation checks PASSED.')
    return True


if __name__ == '__main__':
    ok = run_all()
    sys.exit(0 if ok else 1)
