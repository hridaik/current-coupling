"""
Metric validation — Phase 8B-0.

Validates every metric implementation using synthetic toy examples.
Does NOT use benchmark outputs. Does NOT reveal labels.
All expected values are analytically derived before running.
"""

import sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase8 import config8 as cfg
from scripts.phase8 import metrics as met
from scripts.phase8.input_validator import build_output_arrays

PASS = 'PASS'
FAIL = 'FAIL'
results = []

ALL_PAIRS = [(i, j) for i in range(100) for j in range(100) if i != j]
N_ALL = len(ALL_PAIRS)  # 9900


# ---------------------------------------------------------------------------
# Synthetic dataset builders (all 9900 pairs required by build_output_arrays)
# ---------------------------------------------------------------------------

def make_synthetic() -> tuple[dict, dict]:
    """
    Perfect classifier: 9900 pairs, evenly split across S/C/M/N (2475 each).
    class_prob[true_class]=0.97, others 0.01/3.
    """
    classes = cfg.CLASSES
    n_per   = N_ALL // 4
    labels  = {}
    pred_map = {}
    for idx, (i, j) in enumerate(ALL_PAIRS):
        lbl = classes[idx // n_per] if idx // n_per < 4 else classes[-1]
        labels[(i, j)] = lbl
        cp = {k: 0.01 for k in classes}
        cp[lbl] = 0.97
        total = sum(cp.values())
        cp = {k: v / total for k, v in cp.items()}
        pred_map[(i, j)] = {'i': i, 'j': j, 'class_prob': cp, 'class_pred': lbl}
    return labels, build_output_arrays(pred_map)


def make_random_output() -> tuple[dict, dict]:
    """Random classifier: all class_prob = 0.25, balanced labels."""
    labels   = {}
    pred_map = {}
    for idx, (i, j) in enumerate(ALL_PAIRS):
        lbl = cfg.CLASSES[idx % 4]
        labels[(i, j)] = lbl
        pred_map[(i, j)] = {
            'i': i, 'j': j,
            'class_prob': {k: 0.25 for k in cfg.CLASSES},
            'class_pred': 'N',
        }
    return labels, build_output_arrays(pred_map)


def make_inverted_output() -> tuple[dict, dict]:
    """Worst-case: always predicts wrong class."""
    wrong_map = {'S': 'N', 'C': 'S', 'M': 'C', 'N': 'M'}
    labels   = {}
    pred_map = {}
    for idx, (i, j) in enumerate(ALL_PAIRS):
        lbl   = cfg.CLASSES[idx % 4]
        wrong = wrong_map[lbl]
        labels[(i, j)] = lbl
        cp = {k: 0.01 for k in cfg.CLASSES}
        cp[wrong] = 0.97
        total = sum(cp.values())
        cp = {k: v / total for k, v in cp.items()}
        pred_map[(i, j)] = {'i': i, 'j': j, 'class_prob': cp, 'class_pred': wrong}
    return labels, build_output_arrays(pred_map)


def make_lr_signal_output() -> tuple[dict, dict]:
    """High LR-AUROC: C and M pairs get high P(C)+P(M) but C vs M confused."""
    n4     = N_ALL // 4
    labels  = {}
    pred_map = {}
    for idx, (i, j) in enumerate(ALL_PAIRS):
        lbl = cfg.CLASSES[idx // n4] if idx // n4 < 4 else cfg.CLASSES[-1]
        labels[(i, j)] = lbl
        if lbl in ('C', 'M'):
            cp = {'S': 0.03, 'C': 0.47, 'M': 0.47, 'N': 0.03}
        else:
            cp = {'S': 0.47, 'C': 0.03, 'M': 0.03, 'N': 0.47}
        pred_map[(i, j)] = {
            'i': i, 'j': j, 'class_prob': cp,
            'class_pred': max(cp, key=cp.get),
        }
    return labels, build_output_arrays(pred_map)


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------

def check(name: str, expected, actual, tol: float = 1e-4) -> None:
    ok = abs(float(actual) - float(expected)) <= tol
    status = PASS if ok else FAIL
    results.append({'name': name, 'status': status,
                    'expected': float(expected), 'actual': float(actual), 'tol': tol})
    print(f'  {status:4s}  {name}: expected={float(expected):.6f}, got={float(actual):.6f}')


def check_bool(name: str, expected: bool, actual: bool) -> None:
    ok = (expected == actual)
    status = PASS if ok else FAIL
    results.append({'name': name, 'status': status, 'expected': expected, 'actual': actual})
    print(f'  {status:4s}  {name}: expected={expected}, got={actual}')


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------

def run_all():
    print('=' * 60)
    print('Metric validation — synthetic examples only')
    print('=' * 60)

    # Pre-build datasets (expensive, do once)
    print('Building synthetic datasets...')
    labels_p, arrays_p = make_synthetic()
    labels_r, arrays_r = make_random_output()
    labels_inv, arrays_inv = make_inverted_output()
    labels_lr, arrays_lr = make_lr_signal_output()
    print('Done.\n')

    # -----------------------------------------------------------------------
    # T1: Perfect classifier — AUROC = 1.0 per class and macro
    # -----------------------------------------------------------------------
    print('T1: Perfect classifier → AUROC = 1.0 per class')
    for k in cfg.CLASSES:
        auroc = met.compute_class_auroc(labels_p, arrays_p, k)
        check(f'AUROC({k}) perfect', 1.0, auroc, tol=1e-3)
    check('MacroAUROC perfect', 1.0, met.compute_macro_auroc(labels_p, arrays_p), tol=1e-3)

    # -----------------------------------------------------------------------
    # T2: Random classifier — AUROC ≈ 0.5 per class
    # -----------------------------------------------------------------------
    print('\nT2: Random classifier → AUROC ≈ 0.50 per class')
    for k in cfg.CLASSES:
        auroc = met.compute_class_auroc(labels_r, arrays_r, k)
        check(f'AUROC({k}) random', 0.50, auroc, tol=0.05)
    check('MacroAUROC random', 0.50, met.compute_macro_auroc(labels_r, arrays_r), tol=0.05)

    # -----------------------------------------------------------------------
    # T3: Inverted classifier — AUROC < 0.5
    # -----------------------------------------------------------------------
    print('\nT3: Inverted classifier → AUROC < 0.5')
    for k in cfg.CLASSES:
        auroc = met.compute_class_auroc(labels_inv, arrays_inv, k)
        check_bool(f'AUROC({k}) inverted < 0.5', True, auroc < 0.50)

    # -----------------------------------------------------------------------
    # T4: LR-AUROC — combined C+M signal
    # -----------------------------------------------------------------------
    print('\nT4: LR signal → LR-AUROC high, individual C/M AUROC moderate')
    lr_auroc = met.compute_lr_auroc(labels_lr, arrays_lr)
    c_auroc  = met.compute_class_auroc(labels_lr, arrays_lr, 'C')
    check_bool('LR-AUROC > 0.85', True, lr_auroc > 0.85)
    check_bool('C-AUROC < LR-AUROC', True, c_auroc < lr_auroc)

    # -----------------------------------------------------------------------
    # T5: AUPRC random ≈ class frequency
    # -----------------------------------------------------------------------
    print('\nT5: AUPRC random ≈ class frequency')
    n_n = sum(1 for v in labels_r.values() if v == 'N')
    expected_baseline = n_n / N_ALL
    auprc_n = met.compute_class_auprc(labels_r, arrays_r, 'N')
    check('AUPRC(N) random ≈ class frequency', expected_baseline, auprc_n, tol=0.05)

    # -----------------------------------------------------------------------
    # T6: F1/Precision/Recall at optimal threshold — perfect classifier
    # -----------------------------------------------------------------------
    print('\nT6: F1 at optimal threshold — perfect classifier')
    for k in cfg.CLASSES:
        f1, prec, rec, thresh = met.compute_class_f1(labels_p, arrays_p, k)
        check(f'F1({k}) perfect ≈ 1.0', 1.0, f1, tol=0.02)
        check(f'Precision({k}) perfect ≈ 1.0', 1.0, prec, tol=0.02)
        check(f'Recall({k}) perfect ≈ 1.0', 1.0, rec, tol=0.02)

    # -----------------------------------------------------------------------
    # T7: Balanced accuracy
    # -----------------------------------------------------------------------
    print('\nT7: Balanced accuracy')
    check('BalancedAcc perfect ≈ 1.0', 1.0,
          met.compute_balanced_accuracy(labels_p, arrays_p), tol=0.02)
    check('BalancedAcc random ≈ 0.25', 0.25,
          met.compute_balanced_accuracy(labels_r, arrays_r), tol=0.10)

    # -----------------------------------------------------------------------
    # T8: Confusion matrix — perfect classifier has zero off-diagonal
    # -----------------------------------------------------------------------
    print('\nT8: Confusion matrix diagonal')
    cm = met.compute_confusion_matrix(labels_p, arrays_p)
    off_diag = cm - np.diag(np.diag(cm))
    check_bool('Confusion matrix off-diagonal = 0 (perfect)', True, off_diag.sum() == 0)
    check_bool('Confusion matrix shape (4,4)', True, cm.shape == (4, 4))

    # -----------------------------------------------------------------------
    # T9: Brier score
    # -----------------------------------------------------------------------
    print('\nT9: Brier score')
    brier = met.compute_brier_score(labels_p, arrays_p)
    for k in cfg.CLASSES:
        check_bool(f'Brier({k}) perfect < 0.01', True, brier[k]['brier_score'] < 0.01)
        check_bool(f'Brier skill({k}) perfect > 0.95', True, brier[k]['skill'] > 0.95)

    brier_r = met.compute_brier_score(labels_r, arrays_r)
    for k in cfg.CLASSES:
        # P(k)=0.25, freq=0.25 → BS = 0.25^2*0.75 + 0.75^2*0.25 = 0.1875
        check(f'Brier({k}) random ≈ 0.1875', 0.1875, brier_r[k]['brier_score'], tol=0.005)

    # -----------------------------------------------------------------------
    # T10: ECE
    # -----------------------------------------------------------------------
    print('\nT10: ECE')
    ece_p = met.compute_ece(labels_p, arrays_p)
    check_bool('ECE perfect classifier < 0.10', True, ece_p < 0.10)
    ece_r = met.compute_ece(labels_r, arrays_r)
    # Uniform random: confidence = 0.25, accuracy = 0.25 → ECE ≈ 0
    check('ECE random ≈ 0.0', 0.0, ece_r, tol=0.05)

    # -----------------------------------------------------------------------
    # T11: Top-K precision
    # -----------------------------------------------------------------------
    print('\nT11: Top-K precision')
    # Perfect: top-50 for class C should all be true C
    topk_prec = met.compute_topk_precision(labels_p, arrays_p, 'C', K=50)
    check('TopK-Prec(C, K=50) perfect = 1.0', 1.0, topk_prec, tol=1e-6)
    # Random: ~0.25 expected
    topk_r = met.compute_topk_precision(labels_r, arrays_r, 'C', K=50)
    check_bool('TopK-Prec(C, K=50) random ≈ 0.25', True, abs(topk_r - 0.25) < 0.15)

    # -----------------------------------------------------------------------
    # T12: Enrichment
    # -----------------------------------------------------------------------
    print('\nT12: Enrichment')
    enr_p = met.compute_enrichment(labels_p, arrays_p, 'C', K=50)
    check_bool('Enrichment(C, K=50) perfect >> 1', True, enr_p > 3.0)

    # -----------------------------------------------------------------------
    # T13: Bootstrap CI — perfect classifier gives [1.0, 1.0]
    # -----------------------------------------------------------------------
    print('\nT13: Bootstrap CI — perfect classifier')
    lo, hi = met.compute_bootstrap_ci(labels_p, arrays_p, 'macro_auroc', n_boot=200)
    # Perfect classifier: every bootstrap resample also scores 1.0 → CI = [1.0, 1.0]
    check_bool('Bootstrap CI upper = 1.0 (perfect)', True, hi > 0.98)
    check_bool('Bootstrap CI lower = 1.0 (perfect)', True, lo > 0.98)
    check_bool('Bootstrap CI upper ≥ lower', True, hi >= lo)

    # -----------------------------------------------------------------------
    # T14: MacroAUROC = unweighted mean of per-class AUROCs
    # -----------------------------------------------------------------------
    print('\nT14: MacroAUROC = mean of per-class AUROCs')
    per_class = [met.compute_class_auroc(labels_p, arrays_p, k) for k in cfg.CLASSES]
    macro = met.compute_macro_auroc(labels_p, arrays_p)
    check('MacroAUROC = mean of per-class', float(np.mean(per_class)), macro, tol=1e-6)

    # -----------------------------------------------------------------------
    # T15: WeightedAUROC formula
    # -----------------------------------------------------------------------
    print('\nT15: WeightedAUROC formula')
    total = sum(cfg.COMMITTED_CLASS_COUNTS.values())
    expected_weighted = sum(
        (cfg.COMMITTED_CLASS_COUNTS[k] / total) * per_class[i]
        for i, k in enumerate(cfg.CLASSES)
    )
    weighted = met.compute_weighted_auroc(labels_p, arrays_p)
    check('WeightedAUROC correct formula', expected_weighted, weighted, tol=1e-4)

    # -----------------------------------------------------------------------
    # T16: Determinism
    # -----------------------------------------------------------------------
    print('\nT16: Determinism')
    auroc1 = met.compute_macro_auroc(labels_p, arrays_p)
    auroc2 = met.compute_macro_auroc(labels_p, arrays_p)
    check('MacroAUROC deterministic', auroc1, auroc2, tol=1e-12)

    ci1 = met.compute_bootstrap_ci(labels_p, arrays_p, 'macro_auroc', n_boot=50)
    ci2 = met.compute_bootstrap_ci(labels_p, arrays_p, 'macro_auroc', n_boot=50)
    check_bool('Bootstrap CI deterministic', True, ci1 == ci2)

    # -----------------------------------------------------------------------
    # T17: AUPRC lift > 1 for perfect classifier
    # -----------------------------------------------------------------------
    print('\nT17: AUPRC lift > 1 for perfect classifier')
    for k in cfg.CLASSES:
        lift = met.compute_class_auprc_lift(labels_p, arrays_p, k)
        check_bool(f'AUPRC lift({k}) perfect > 1', True, lift > 1.0)

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
                exp = r.get('expected', '?')
                act = r.get('actual', '?')
                print(f'  FAIL  {r["name"]}: expected={exp!r}, got={act!r}')
        return False
    print('All metric validation checks PASSED.')
    return True


if __name__ == '__main__':
    ok = run_all()
    sys.exit(0 if ok else 1)
