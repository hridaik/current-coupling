"""
Verdict engine — Phase 8B.

Implements the exact decision procedure from phase8a_success_criteria.md.
Thresholds and logic are frozen. No modification after Phase 8B begins.
"""

from . import config8 as cfg


# ---------------------------------------------------------------------------
# Benchmark validity checks (phase8a_success_criteria §1)
# ---------------------------------------------------------------------------

def check_benchmark_validity(
    labels_dict: dict,
    b4_direct_auroc: float,
    blinding_audit_passed: bool,
    output_hash_verified: bool,
) -> dict[str, bool]:
    """
    BV-1 through BV-5.
    Returns {check_id: passed} dict.
    All must be True before primary verdict is computed.
    """
    n_c = sum(1 for v in labels_dict.values() if v == 'C')
    n_m = sum(1 for v in labels_dict.values() if v == 'M')

    return {
        'BV-1': n_c >= cfg.BV1_MIN_C_COUNT,
        'BV-2': n_m >= cfg.BV2_MIN_M_COUNT,
        'BV-3': b4_direct_auroc >= cfg.BV3_MIN_B4_DIRECT_AUROC,
        'BV-4': blinding_audit_passed,
        'BV-5': output_hash_verified,
    }


def benchmark_validity_passed(bv_results: dict) -> bool:
    """True iff all BV checks pass."""
    return all(bv_results.values())


# ---------------------------------------------------------------------------
# Primary verdict (phase8a_success_criteria §3)
# ---------------------------------------------------------------------------

def determine_verdict(
    macro_auroc: float,
    c_auroc: float,
    lr_auroc: float,
    b4_c_auroc: float,
    ci_95: dict | None = None,
) -> dict:
    """
    Apply the frozen decision procedure.

    Parameters
    ----------
    macro_auroc  : M6 on oracle_z condition
    c_auroc      : M1-C on oracle_z condition
    lr_auroc     : M10 (LR-AUROC) on oracle_z condition
    b4_c_auroc   : B4 baseline C-AUROC on oracle_z condition
    ci_95        : optional dict {'macro_auroc': {'lower':, 'upper':}, ...}

    Returns
    -------
    dict with keys: 'verdict', 'sub_category', 'primary_metrics',
                    'threshold_checks', 'ci_spans_threshold', 'rationale'
    """
    result = {
        'primary_metrics': {
            'macro_auroc':  macro_auroc,
            'c_auroc':      c_auroc,
            'lr_auroc':     lr_auroc,
            'b4_c_auroc':   b4_c_auroc,
        },
        'thresholds': {
            'macro_auroc_success': cfg.THRESHOLD_SUCCESS_MACRO_AUROC,
            'macro_auroc_partial': cfg.THRESHOLD_PARTIAL_MACRO_AUROC,
            'c_auroc_success':     cfg.THRESHOLD_SUCCESS_C_AUROC,
            'c_auroc_partial':     cfg.THRESHOLD_PARTIAL_C_AUROC,
            'lr_auroc_success':    cfg.THRESHOLD_SUCCESS_LR_AUROC,
            'lr_auroc_partial':    cfg.THRESHOLD_PARTIAL_LR_AUROC,
            'b4_margin':           cfg.THRESHOLD_FRAMEWORK_VS_B4_C_MARGIN,
        },
    }

    # Per-metric checks
    framework_vs_b4_margin = c_auroc - b4_c_auroc
    checks = {
        'macro_auroc_success':  macro_auroc >= cfg.THRESHOLD_SUCCESS_MACRO_AUROC,
        'macro_auroc_partial':  macro_auroc >= cfg.THRESHOLD_PARTIAL_MACRO_AUROC,
        'c_auroc_success':      c_auroc     >= cfg.THRESHOLD_SUCCESS_C_AUROC,
        'c_auroc_partial':      c_auroc     >= cfg.THRESHOLD_PARTIAL_C_AUROC,
        'lr_auroc_success':     lr_auroc    >= cfg.THRESHOLD_SUCCESS_LR_AUROC,
        'lr_auroc_partial':     lr_auroc    >= cfg.THRESHOLD_PARTIAL_LR_AUROC,
        'beats_b4_by_margin':   framework_vs_b4_margin >= cfg.THRESHOLD_FRAMEWORK_VS_B4_C_MARGIN,
    }
    result['threshold_checks']  = checks
    result['framework_vs_b4_c'] = framework_vs_b4_margin

    # INCONCLUSIVE-CI: does the CI span both a success and a failure threshold?
    ci_spans = {}
    if ci_95:
        for metric, thresh_s, thresh_f in [
            ('macro_auroc', cfg.THRESHOLD_SUCCESS_MACRO_AUROC, cfg.THRESHOLD_PARTIAL_MACRO_AUROC),
            ('c_auroc',     cfg.THRESHOLD_SUCCESS_C_AUROC,     cfg.THRESHOLD_PARTIAL_C_AUROC),
            ('lr_auroc',    cfg.THRESHOLD_SUCCESS_LR_AUROC,    cfg.THRESHOLD_PARTIAL_LR_AUROC),
        ]:
            ci = ci_95.get(metric, {})
            lo, hi = ci.get('lower', None), ci.get('upper', None)
            if lo is not None and hi is not None:
                # CI spans: lower < failure threshold AND upper > success threshold
                ci_spans[metric] = (lo < thresh_f) and (hi > thresh_s)
    result['ci_spans_threshold'] = ci_spans

    # -----------------------------------------------------------------------
    # Decision tree (exact order from spec §3)
    # -----------------------------------------------------------------------

    # FAILURE: any one sufficient
    failure_triggered = (
        macro_auroc < cfg.THRESHOLD_PARTIAL_MACRO_AUROC or
        c_auroc     < cfg.THRESHOLD_PARTIAL_C_AUROC     or
        lr_auroc    < cfg.THRESHOLD_PARTIAL_LR_AUROC
    )

    # SUCCESS: all must hold
    success_triggered = (
        checks['macro_auroc_success'] and
        checks['c_auroc_success']     and
        checks['lr_auroc_success']    and
        checks['beats_b4_by_margin']
    )

    # Check for INCONCLUSIVE-CI
    inconclusive_ci = any(ci_spans.values()) if ci_spans else False

    if failure_triggered:
        verdict = 'FAILURE'
        sub_cat = _determine_failure_sub(macro_auroc, c_auroc, lr_auroc, b4_c_auroc)
        rationale = (
            f'At least one primary metric below failure threshold: '
            f'MacroAUROC={macro_auroc:.4f} (threshold {cfg.THRESHOLD_PARTIAL_MACRO_AUROC}), '
            f'C-AUROC={c_auroc:.4f} (threshold {cfg.THRESHOLD_PARTIAL_C_AUROC}), '
            f'LR-AUROC={lr_auroc:.4f} (threshold {cfg.THRESHOLD_PARTIAL_LR_AUROC})'
        )

    elif success_triggered:
        if inconclusive_ci:
            verdict = 'INCONCLUSIVE'
            sub_cat = 'INCONCLUSIVE-CI'
            rationale = 'Point estimates meet SUCCESS criteria but CI spans threshold boundary'
        else:
            verdict = 'SUCCESS'
            sub_cat = None
            rationale = (
                f'All primary metrics meet success thresholds: '
                f'MacroAUROC={macro_auroc:.4f}≥{cfg.THRESHOLD_SUCCESS_MACRO_AUROC}, '
                f'C-AUROC={c_auroc:.4f}≥{cfg.THRESHOLD_SUCCESS_C_AUROC}, '
                f'LR-AUROC={lr_auroc:.4f}≥{cfg.THRESHOLD_SUCCESS_LR_AUROC}, '
                f'framework vs B4 margin={framework_vs_b4_margin:.4f}≥{cfg.THRESHOLD_FRAMEWORK_VS_B4_C_MARGIN}'
            )

    else:
        # Partial
        if inconclusive_ci:
            verdict = 'INCONCLUSIVE'
            sub_cat = 'INCONCLUSIVE-CI'
            rationale = 'Metrics fall in partial range but CI prevents definitive conclusion'
        else:
            verdict = 'PARTIAL_SUCCESS'
            sub_cat  = _determine_partial_sub(macro_auroc, c_auroc, lr_auroc)
            rationale = (
                f'Primary metrics in partial range: '
                f'MacroAUROC={macro_auroc:.4f}, '
                f'C-AUROC={c_auroc:.4f}, '
                f'LR-AUROC={lr_auroc:.4f}'
            )

    result['verdict']     = verdict
    result['sub_category'] = sub_cat
    result['rationale']   = rationale
    return result


def _determine_failure_sub(macro, c_auroc, lr_auroc, b4_c):
    parts = []
    if macro < cfg.THRESHOLD_PARTIAL_MACRO_AUROC:
        parts.append(f'MacroAUROC={macro:.4f}<{cfg.THRESHOLD_PARTIAL_MACRO_AUROC}')
    if c_auroc < cfg.THRESHOLD_PARTIAL_C_AUROC:
        parts.append(f'C-AUROC={c_auroc:.4f}<{cfg.THRESHOLD_PARTIAL_C_AUROC}')
    if lr_auroc < cfg.THRESHOLD_PARTIAL_LR_AUROC:
        parts.append(f'LR-AUROC={lr_auroc:.4f}<{cfg.THRESHOLD_PARTIAL_LR_AUROC}')
    if c_auroc <= b4_c:
        parts.append(f'C-AUROC≤B4({c_auroc:.4f}≤{b4_c:.4f})')
    return 'FAILURE[' + '; '.join(parts) + ']'


def _determine_partial_sub(macro, c_auroc, lr_auroc):
    """Classify into PS-1 through PS-3 (PS-4 requires cross-condition comparison)."""
    # Use success thresholds for sub-classification: "high" = in success range
    macro_success = macro   >= cfg.THRESHOLD_SUCCESS_MACRO_AUROC
    c_high        = c_auroc >= cfg.THRESHOLD_SUCCESS_C_AUROC
    c_low         = c_auroc <  cfg.THRESHOLD_PARTIAL_C_AUROC

    if c_high and not macro_success:
        return 'PS-2'  # C-AUROC in success range but overall macro not
    if macro_success and c_low:
        return 'PS-1'  # structural only
    return 'PS-3'  # weak signal across board


# ---------------------------------------------------------------------------
# Failure-mode overrides (phase8a_success_criteria §5)
# ---------------------------------------------------------------------------

def apply_failure_mode_overrides(
    verdict: str,
    fo_context: dict,
) -> tuple[str, list[str]]:
    """
    Check failure-mode overrides FO-1 through FO-5.
    Returns (final_verdict, list_of_applied_overrides).

    fo_context keys:
        'weak_fraction_c'  : fraction of C pairs with near-zero path strength
        'mean_strength_c'  : mean max-path strength for C pairs
        'n_c'              : actual n(C) at evaluation
        'all_y_variance'   : minimum per-neuron y variance across runs
        'all_y_finite'     : bool, all y values finite
    """
    if verdict != 'FAILURE':
        return verdict, []

    overrides_applied = []

    # FO-1: Weak path fraction exceeds trigger
    wf = fo_context.get('weak_fraction_c', 0.0)
    if wf > cfg.FO1_WEAK_FRACTION_TRIGGER:
        overrides_applied.append(
            f'FO-1: {wf:.3f} of C pairs have near-zero path strength '
            f'(>{cfg.FO1_WEAK_FRACTION_TRIGGER}); benchmark limitation suspected'
        )

    # FO-2: Mean path strength below trigger
    ms = fo_context.get('mean_strength_c', 1.0)
    if ms < cfg.FO2_MEAN_STRENGTH_TRIGGER:
        overrides_applied.append(
            f'FO-2: Mean C-pair path strength {ms:.6f} < {cfg.FO2_MEAN_STRENGTH_TRIGGER}; '
            'H2 weights near-zero; benchmark unable to produce detectable signal'
        )

    # FO-3: n(C) below minimum
    n_c = fo_context.get('n_c', cfg.COMMITTED_CLASS_COUNTS['C'])
    if n_c < 200:
        overrides_applied.append(
            f'FO-3: n(C)={n_c} < 200; statistical power insufficient for reliable C-AUROC'
        )

    # FO-4: All y variance collapsed
    min_var = fo_context.get('all_y_variance', 1.0)
    if min_var < 1e-4:
        overrides_applied.append(
            f'FO-4: Min y variance = {min_var:.2e} < 1e-4; dynamics collapsed'
        )

    # FO-5: y contains non-finite values
    if not fo_context.get('all_y_finite', True):
        overrides_applied.append('FO-5: Observation array contains NaN or Inf')

    if overrides_applied:
        return 'INCONCLUSIVE_BENCHMARK_FAILURE', overrides_applied
    return verdict, []


# ---------------------------------------------------------------------------
# Condition-level secondary comparisons (phase8a_success_criteria §6)
# ---------------------------------------------------------------------------

def compute_condition_comparisons(metrics_by_condition: dict) -> dict:
    """
    Compare primary metrics between conditions.
    Returns diff table for interpretation.
    """
    primary = 'oracle_z'
    if primary not in metrics_by_condition:
        return {}

    base_macro  = metrics_by_condition[primary]['macro_auroc']
    base_c      = metrics_by_condition[primary]['auroc']['C']
    base_lr     = metrics_by_condition[primary]['auroc']['LR']

    diffs = {}
    for cond, mets in metrics_by_condition.items():
        if cond == primary:
            continue
        diffs[cond] = {
            'delta_macro_auroc': mets['macro_auroc'] - base_macro,
            'delta_c_auroc':     mets['auroc']['C']  - base_c,
            'delta_lr_auroc':    mets['auroc']['LR']  - base_lr,
        }
    return diffs
