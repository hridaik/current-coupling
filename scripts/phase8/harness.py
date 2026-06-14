"""
Evaluation harness orchestrator — Phase 8B.

Calls all sub-engines in the required sequence. Enforces blinding protocol.
This is the only entry point for scoring framework outputs.

Usage (Phase 8B only):
    python -m scripts.phase8.harness --condition oracle_z --output path/to/output.json
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase8 import config8 as cfg
from scripts.phase8 import blinding as bld
from scripts.phase8 import metrics as met
from scripts.phase8 import baselines as bas
from scripts.phase8 import verdict as vrd
from scripts.phase8.input_validator import load_framework_output, validate_completeness, build_output_arrays


def run_evaluation(
    condition: str,
    output_path: str,
    framework_code_paths: list[str] | None = None,
    verbose: bool = True,
) -> dict:
    """
    Score one condition's framework output.

    Parameters
    ----------
    condition     : one of cfg.CONDITIONS
    output_path   : path to framework output JSON file
    framework_code_paths : optional list of framework source files for BC-3 audit

    Returns
    -------
    dict with all results
    """
    if condition not in cfg.CONDITIONS:
        raise ValueError(f'Unknown condition {condition!r}. Must be one of {cfg.CONDITIONS}')

    os.makedirs(cfg.METRICS_DIR, exist_ok=True)

    # -----------------------------------------------------------------------
    # Step 1: Freeze output (idempotent: skip if already recorded)
    # -----------------------------------------------------------------------
    completed = bld.get_completed_events()
    if 'framework_output_received' in completed:
        # Recover recorded hash from audit log
        audit = bld.read_eval_audit()
        recv_event = next(e for e in audit if e.get('event') == 'framework_output_received')
        recorded_hash = recv_event['sha256']
        if verbose:
            print(f'Output already frozen (resuming): {recorded_hash[:16]}…')
    else:
        recorded_hash = bld.record_framework_output(condition, output_path)
        if verbose:
            print(f'Output frozen: {recorded_hash[:16]}…')

    # -----------------------------------------------------------------------
    # Step 2: Run blinding checks (idempotent: skip if already passed)
    # -----------------------------------------------------------------------
    with open(output_path) as f:
        raw_output = json.load(f)
    metadata = raw_output.get('metadata', {})

    if framework_code_paths:
        code_violations = bld.audit_framework_code_paths(framework_code_paths)
        if code_violations:
            bld.log_eval_event({'event': 'bc3_code_violations', 'violations': code_violations})
            if verbose:
                print(f'WARNING: BC-3 code audit found {len(code_violations)} violations')

    if 'blinding_check_passed' in completed:
        checks = {'BC-1': True, 'BC-2': True, 'BC-3': True, 'BC-4': True}
        if verbose:
            print('Blinding checks: already passed (resuming)')
    else:
        checks = bld.run_blinding_checks(
            output_path=output_path,
            recorded_output_hash=recorded_hash,
            output_metadata=metadata,
        )
        if not all(checks.values()):
            failed = [k for k, v in checks.items() if not v]
            raise RuntimeError(f'Blinding checks failed: {failed}. Cannot proceed with scoring.')
        if verbose:
            print('Blinding checks: all passed')

    # -----------------------------------------------------------------------
    # Step 3: Load and validate framework output
    # -----------------------------------------------------------------------
    framework_metadata, pred_map, schema_warnings = load_framework_output(output_path)
    complete, missing_pairs = validate_completeness(pred_map)
    if schema_warnings and verbose:
        print(f'Schema warnings: {len(schema_warnings)}')
    output_arrays = build_output_arrays(pred_map)

    # -----------------------------------------------------------------------
    # Step 4: Load labels (gated by blinding; idempotent on resume)
    # -----------------------------------------------------------------------
    if 'labels_loaded_for_scoring' in completed:
        # Labels already loaded in prior run; load directly (audit already records this)
        import json as _json
        with open(cfg.LABELS_PATH, 'r', encoding='utf-8') as _f:
            _d = _json.load(_f)
        labels_dict = {(r['i'], r['j']): r['label'] for r in _d['labels']}
        if verbose:
            print(f'Labels already loaded (resuming): {len(labels_dict)} pairs')
    else:
        labels_dict = bld.load_labels_for_scoring()
        if verbose:
            print(f'Labels loaded: {len(labels_dict)} pairs')

    # -----------------------------------------------------------------------
    # Step 5: Compute baselines (using trajectory data, not labels)
    # -----------------------------------------------------------------------
    if verbose:
        print('Computing baselines...')
    input_bundle = bld.build_input_bundle(condition)
    runs = input_bundle['runs']

    baseline_results = bas.run_all_baselines(runs, verbose=verbose)
    baseline_metrics = {}
    for bname, bresult in baseline_results.items():
        if bresult is None:
            baseline_metrics[bname] = None
            continue
        _, b_arrays = bresult
        baseline_metrics[bname] = {
            'macro_auroc': met.compute_macro_auroc(labels_dict, b_arrays),
            'c_auroc':     met.compute_class_auroc(labels_dict, b_arrays, 'C'),
            'lr_auroc':    met.compute_lr_auroc(labels_dict, b_arrays),
            'direct_auroc': met.compute_direct_auroc(labels_dict, b_arrays),
        }

    # -----------------------------------------------------------------------
    # Step 6: Compute all framework metrics
    # -----------------------------------------------------------------------
    if verbose:
        print('Computing framework metrics...')
    is_primary = (condition == cfg.PRIMARY_CONDITION)
    framework_metrics = met.compute_all_primary_metrics(
        labels_dict, output_arrays, compute_ci=is_primary
    )
    bld.log_eval_event({
        'event':     'metrics_computed',
        'condition': condition,
        'macro_auroc': framework_metrics['macro_auroc'],
        'c_auroc':   framework_metrics['auroc']['C'],
        'lr_auroc':  framework_metrics['auroc']['LR'],
    })

    if verbose:
        print(f'MacroAUROC: {framework_metrics["macro_auroc"]:.4f}')
        print(f'C-AUROC:    {framework_metrics["auroc"]["C"]:.4f}')
        print(f'LR-AUROC:   {framework_metrics["auroc"]["LR"]:.4f}')

    # -----------------------------------------------------------------------
    # Step 7: Save results
    # -----------------------------------------------------------------------
    results = {
        'condition':           condition,
        'is_primary_condition': is_primary,
        'framework_metadata':  framework_metadata,
        'schema_warnings':     schema_warnings,
        'blinding_checks':     checks,
        'framework_metrics':   framework_metrics,
        'baseline_metrics':    baseline_metrics,
    }
    metrics_path = os.path.join(cfg.METRICS_DIR, f'metrics_{condition}.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=True, default=str)

    # -----------------------------------------------------------------------
    # Step 8: Determine verdict (primary condition only)
    # -----------------------------------------------------------------------
    if is_primary:
        b4_c = baseline_metrics.get('B4', {}).get('c_auroc', 0.0) if baseline_metrics.get('B4') else 0.0

        bv_results = vrd.check_benchmark_validity(
            labels_dict          = labels_dict,
            b4_direct_auroc      = baseline_metrics.get('B4', {}).get('direct_auroc', 0.0) if baseline_metrics.get('B4') else 0.0,
            blinding_audit_passed = all(checks.values()),
            output_hash_verified  = checks.get('BC-1', False),
        )
        if verbose:
            bv_ok = vrd.benchmark_validity_passed(bv_results)
            print(f'Benchmark validity: {"PASS" if bv_ok else "FAIL"}')
            for k, v in bv_results.items():
                print(f'  {k}: {"PASS" if v else "FAIL"}')

        ci_95 = framework_metrics.get('ci_95', {})
        verdict_result = vrd.determine_verdict(
            macro_auroc = framework_metrics['macro_auroc'],
            c_auroc     = framework_metrics['auroc']['C'],
            lr_auroc    = framework_metrics['auroc']['LR'],
            b4_c_auroc  = b4_c,
            ci_95       = {
                'macro_auroc': ci_95.get('macro_auroc', {}),
                'c_auroc':     ci_95.get('c_auroc', {}),
                'lr_auroc':    ci_95.get('lr_auroc', {}),
            },
        )
        verdict_result['benchmark_validity'] = bv_results

        verdict_hash = bld.record_verdict(verdict_result)
        results['verdict']      = verdict_result
        results['verdict_hash'] = verdict_hash

        if verbose:
            print(f'\nVERDICT: {verdict_result["verdict"]}')
            if verdict_result.get('sub_category'):
                print(f'  Sub-category: {verdict_result["sub_category"]}')
            print(f'  Rationale: {verdict_result["rationale"]}')

        # Reveal (after verdict is recorded)
        bld.record_label_reveal(
            verdict          = verdict_result['verdict'],
            primary_metrics  = {
                'macro_auroc': framework_metrics['macro_auroc'],
                'c_auroc':     framework_metrics['auroc']['C'],
                'lr_auroc':    framework_metrics['auroc']['LR'],
            },
        )

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Phase 8B evaluation harness')
    parser.add_argument('--condition', required=True, choices=cfg.CONDITIONS)
    parser.add_argument('--output',    required=True, help='Path to framework output JSON')
    parser.add_argument('--framework-code', nargs='*', default=[],
                        help='Framework source files for BC-3 audit')
    args = parser.parse_args()
    run_evaluation(args.condition, args.output, args.framework_code)
