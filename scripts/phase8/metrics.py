"""
Metric engine — Phase 8B.

Implements all metrics M1-M14 from phase8a_metric_registry.md.
Every formula is implemented exactly as specified. No deviation permitted.
"""

import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from . import config8 as cfg


# ---------------------------------------------------------------------------
# Label loading helpers
# ---------------------------------------------------------------------------

def load_labels() -> dict[tuple[int, int], str]:
    """Load committed labels; return {(i,j): label_str}."""
    import json, hashlib, os
    # Verify hash before loading
    with open(cfg.LABELS_PATH, 'rb') as f:
        content = f.read()
    computed = hashlib.sha256(content).hexdigest()
    if computed != cfg.COMMITTED_LABEL_HASH:
        raise ValueError(
            f'Label hash mismatch: expected {cfg.COMMITTED_LABEL_HASH}, '
            f'got {computed}. Labels have been tampered with.'
        )
    d = json.loads(content.decode('utf-8'))
    return {(r['i'], r['j']): r['label'] for r in d['labels']}


def build_binary_labels(
    labels_dict: dict,
    class_k: str,
) -> tuple[np.ndarray, list]:
    """
    Build binary 0/1 array for one-vs-rest classification for class k.
    Returns (y_true_binary, pairs) where pairs is ordered list of (i,j).
    """
    pairs = [(i, j) for i in range(100) for j in range(100) if i != j]
    y = np.array([1 if labels_dict.get((i, j)) == class_k else 0
                  for (i, j) in pairs], dtype=np.float64)
    return y, pairs


def build_binary_labels_group(
    labels_dict: dict,
    class_set: frozenset,
) -> tuple[np.ndarray, list]:
    """Binary labels for a group of classes (e.g., LR = {C,M})."""
    pairs = [(i, j) for i in range(100) for j in range(100) if i != j]
    y = np.array([1 if labels_dict.get((i, j)) in class_set else 0
                  for (i, j) in pairs], dtype=np.float64)
    return y, pairs


def get_scores(output_arrays: dict, class_k: str) -> np.ndarray:
    """Extract class_prob[:, k_idx] from output arrays."""
    k_idx = cfg.CLASSES.index(class_k)
    return output_arrays['class_prob'][:, k_idx]


def get_lr_scores(output_arrays: dict) -> np.ndarray:
    """LR score = P(C) + P(M). Specification: phase8a_metric_registry §1 M1."""
    c_idx = cfg.CLASSES.index('C')
    m_idx = cfg.CLASSES.index('M')
    return output_arrays['class_prob'][:, c_idx] + output_arrays['class_prob'][:, m_idx]


def get_direct_scores(output_arrays: dict) -> np.ndarray:
    """Direct score = P(S) + P(M)."""
    s_idx = cfg.CLASSES.index('S')
    m_idx = cfg.CLASSES.index('M')
    return output_arrays['class_prob'][:, s_idx] + output_arrays['class_prob'][:, m_idx]


# ---------------------------------------------------------------------------
# M1: AUROC
# ---------------------------------------------------------------------------

def compute_auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    M1: Area Under the ROC Curve (one-vs-rest, trapezoidal).
    Ties broken by averaging (handled by sklearn's default).
    Returns 0.5 if fewer than 2 classes present.
    """
    if len(np.unique(y_true)) < 2:
        return 0.5
    return float(roc_auc_score(y_true, y_score))


def compute_class_auroc(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
) -> float:
    """AUROC for class k vs rest."""
    y_true, _ = build_binary_labels(labels_dict, class_k)
    y_score   = get_scores(output_arrays, class_k)
    return compute_auroc(y_true, y_score)


def compute_lr_auroc(labels_dict: dict, output_arrays: dict) -> float:
    """M10: LR-AUROC. Score = P(C) + P(M)."""
    y_true, _ = build_binary_labels_group(labels_dict, cfg.LR_CLASSES)
    y_score   = get_lr_scores(output_arrays)
    return compute_auroc(y_true, y_score)


def compute_direct_auroc(labels_dict: dict, output_arrays: dict) -> float:
    """Direct-AUROC. Score = P(S) + P(M)."""
    y_true, _ = build_binary_labels_group(labels_dict, cfg.DIR_CLASSES)
    y_score   = get_direct_scores(output_arrays)
    return compute_auroc(y_true, y_score)


def compute_macro_auroc(labels_dict: dict, output_arrays: dict) -> float:
    """M6: MacroAUROC = mean(AUROC(S), AUROC(C), AUROC(M), AUROC(N))."""
    per_class = [compute_class_auroc(labels_dict, output_arrays, k)
                 for k in cfg.CLASSES]
    return float(np.mean(per_class))


def compute_weighted_auroc(labels_dict: dict, output_arrays: dict) -> float:
    """M7: Weighted-AUROC = sum(n(k)/N * AUROC(k))."""
    total = sum(cfg.COMMITTED_CLASS_COUNTS.values())
    weighted = sum(
        (cfg.COMMITTED_CLASS_COUNTS[k] / total) * compute_class_auroc(labels_dict, output_arrays, k)
        for k in cfg.CLASSES
    )
    return float(weighted)


# ---------------------------------------------------------------------------
# M2: AUPRC
# ---------------------------------------------------------------------------

def compute_auprc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """M2: Average precision (area under precision-recall curve, trapezoidal)."""
    if len(np.unique(y_true)) < 2:
        return float(np.mean(y_true))  # trivial case
    return float(average_precision_score(y_true, y_score))


def compute_class_auprc(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
) -> float:
    y_true, _ = build_binary_labels(labels_dict, class_k)
    y_score   = get_scores(output_arrays, class_k)
    return compute_auprc(y_true, y_score)


def compute_class_auprc_lift(labels_dict: dict, output_arrays: dict, class_k: str) -> float:
    """AUPRC lift = AUPRC(k) / baseline_AUPRC(k)."""
    auprc = compute_class_auprc(labels_dict, output_arrays, class_k)
    n_k   = sum(1 for v in labels_dict.values() if v == class_k)
    baseline = n_k / len(labels_dict)
    if baseline < 1e-12:
        return float('nan')
    return auprc / baseline


# ---------------------------------------------------------------------------
# M3-M5: F1, Precision, Recall at optimal threshold
# ---------------------------------------------------------------------------

def compute_f1_at_optimal_threshold(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> tuple[float, float, float, float]:
    """
    M3/M4/M5: Find threshold maximizing F1 over y_score.

    Returns (f1, precision, recall, threshold).
    Threshold selected post-hoc on evaluation data (secondary metric only).
    """
    from sklearn.metrics import precision_recall_curve, f1_score as sk_f1
    prec, rec, thresholds = precision_recall_curve(y_true, y_score)
    # precision_recall_curve returns arrays where last element corresponds to
    # threshold=max; f1 at each threshold
    f1_scores = np.where(
        (prec + rec) > 0,
        2 * prec * rec / (prec + rec),
        0.0,
    )
    best_idx  = int(np.argmax(f1_scores))
    best_f1   = float(f1_scores[best_idx])
    best_prec = float(prec[best_idx])
    best_rec  = float(rec[best_idx])
    best_thresh = float(thresholds[best_idx]) if best_idx < len(thresholds) else float(thresholds[-1])
    return best_f1, best_prec, best_rec, best_thresh


def compute_class_f1(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
) -> tuple[float, float, float, float]:
    y_true, _ = build_binary_labels(labels_dict, class_k)
    y_score   = get_scores(output_arrays, class_k)
    return compute_f1_at_optimal_threshold(y_true, y_score)


# ---------------------------------------------------------------------------
# M8: Balanced accuracy
# ---------------------------------------------------------------------------

def compute_balanced_accuracy(labels_dict: dict, output_arrays: dict) -> float:
    """
    M8: Balanced accuracy = (1/4) * sum_k(recall_k).
    Prediction = argmax(class_prob).
    """
    pairs = output_arrays['pairs']
    y_true = np.array([labels_dict.get((i, j), 'N') for (i, j) in pairs])
    y_pred = output_arrays['class_pred']

    per_class_recall = []
    for k in cfg.CLASSES:
        mask = (y_true == k)
        if mask.sum() == 0:
            per_class_recall.append(0.0)
        else:
            per_class_recall.append(float((y_pred[mask] == k).mean()))
    return float(np.mean(per_class_recall))


# ---------------------------------------------------------------------------
# M9: Confusion matrix
# ---------------------------------------------------------------------------

def compute_confusion_matrix(labels_dict: dict, output_arrays: dict) -> np.ndarray:
    """
    M9: 4×4 confusion matrix. Rows = true label, cols = predicted label.
    Order: S, C, M, N (cfg.CLASSES order).
    """
    pairs  = output_arrays['pairs']
    y_true = [labels_dict.get((i, j), 'N') for (i, j) in pairs]
    y_pred = list(output_arrays['class_pred'])
    k_map  = {k: idx for idx, k in enumerate(cfg.CLASSES)}
    n      = len(cfg.CLASSES)
    cm     = np.zeros((n, n), dtype=np.int64)
    for yt, yp in zip(y_true, y_pred):
        if yt in k_map and yp in k_map:
            cm[k_map[yt], k_map[yp]] += 1
    return cm


# ---------------------------------------------------------------------------
# M11: Brier score
# ---------------------------------------------------------------------------

def compute_brier_score(labels_dict: dict, output_arrays: dict) -> dict[str, float]:
    """
    M11: Brier score per class and skill score.
    BS(k) = (1/N) * sum (P(k|pair) - 1[label=k])^2
    """
    pairs  = output_arrays['pairs']
    n      = len(pairs)
    result = {}
    for k_idx, k in enumerate(cfg.CLASSES):
        y_true  = np.array([1.0 if labels_dict.get(p) == k else 0.0 for p in pairs])
        y_score = output_arrays['class_prob'][:, k_idx]
        bs      = float(np.mean((y_score - y_true) ** 2))
        freq    = float(np.mean(y_true))
        bs_baseline = freq * (1 - freq)
        skill = 1.0 - (bs / bs_baseline) if bs_baseline > 1e-12 else float('nan')
        result[k] = {'brier_score': bs, 'baseline': bs_baseline, 'skill': skill}
    return result


# ---------------------------------------------------------------------------
# M12: ECE
# ---------------------------------------------------------------------------

def compute_ece(labels_dict: dict, output_arrays: dict) -> float:
    """
    M12: Expected calibration error on argmax confidence.
    Uses cfg.ECE_N_BINS equal-width bins.
    """
    pairs      = output_arrays['pairs']
    class_prob = output_arrays['class_prob']
    class_pred = output_arrays['class_pred']
    n          = len(pairs)

    confidences = class_prob.max(axis=1)
    correct     = np.array([
        1.0 if class_pred[idx] == labels_dict.get(pairs[idx], 'N') else 0.0
        for idx in range(n)
    ])

    bins   = np.linspace(0.0, 1.0, cfg.ECE_N_BINS + 1)
    ece    = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (confidences >= lo) & (confidences < hi)
        if not mask.any():
            continue
        acc  = correct[mask].mean()
        conf = confidences[mask].mean()
        ece += (mask.sum() / n) * abs(acc - conf)
    return float(ece)


# ---------------------------------------------------------------------------
# M13: Top-K precision
# ---------------------------------------------------------------------------

def compute_topk_precision(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
    K: int,
) -> float:
    """
    M13: Top-K precision for class k.
    Rank pairs by class_prob[k] descending; count true k-positives in top K.
    """
    pairs   = output_arrays['pairs']
    k_idx   = cfg.CLASSES.index(class_k)
    scores  = output_arrays['class_prob'][:, k_idx]
    top_idx = np.argsort(scores)[::-1][:K]
    hits    = sum(1 for idx in top_idx if labels_dict.get(pairs[idx]) == class_k)
    return hits / K


def compute_topk_recall(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
    K: int,
) -> float:
    """Top-K recall: fraction of all class-k pairs retrieved in top K."""
    pairs   = output_arrays['pairs']
    k_idx   = cfg.CLASSES.index(class_k)
    scores  = output_arrays['class_prob'][:, k_idx]
    top_idx = set(np.argsort(scores)[::-1][:K])
    n_k     = sum(1 for p in pairs if labels_dict.get(p) == class_k)
    if n_k == 0:
        return float('nan')
    hits = sum(1 for idx in top_idx if labels_dict.get(pairs[idx]) == class_k)
    return hits / n_k


# ---------------------------------------------------------------------------
# M14: Enrichment
# ---------------------------------------------------------------------------

def compute_enrichment(
    labels_dict: dict,
    output_arrays: dict,
    class_k: str,
    K: int,
) -> float:
    """
    M14: Enrichment = TopK-Prec(k,K) / (n(k) / N_pairs).
    """
    topk_prec = compute_topk_precision(labels_dict, output_arrays, class_k, K)
    n_k       = sum(1 for v in labels_dict.values() if v == class_k)
    base      = n_k / len(labels_dict)
    if base < 1e-12:
        return float('nan')
    return topk_prec / base


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

def _bootstrap_one(
    labels_dict: dict,
    output_arrays: dict,
    metric_name: str,
    rng: np.random.Generator,
) -> float:
    """
    Compute metric on one bootstrap resample of pairs.

    Aligns labels directly from the sampled pair indices to avoid the
    full-grid regeneration in build_binary_labels which would misalign
    labels and scores when pairs are in bootstrap order.
    """
    n          = len(output_arrays['pairs'])
    idx        = rng.integers(0, n, size=n)
    pairs      = output_arrays['pairs']
    boot_prob  = output_arrays['class_prob'][idx]     # (n, 4) in bootstrap order
    boot_true  = [labels_dict.get(pairs[i], 'N') for i in idx]  # aligned with boot_prob

    if metric_name == 'macro_auroc':
        per = []
        for c_i, k in enumerate(cfg.CLASSES):
            y_true  = np.array([1 if t == k else 0 for t in boot_true], dtype=np.float64)
            y_score = boot_prob[:, c_i]
            per.append(compute_auroc(y_true, y_score))
        return float(np.mean(per))

    elif metric_name == 'c_auroc':
        c_i    = cfg.CLASSES.index('C')
        y_true = np.array([1 if t == 'C' else 0 for t in boot_true], dtype=np.float64)
        return compute_auroc(y_true, boot_prob[:, c_i])

    elif metric_name == 'lr_auroc':
        c_i    = cfg.CLASSES.index('C')
        m_i    = cfg.CLASSES.index('M')
        y_true = np.array([1 if t in cfg.LR_CLASSES else 0 for t in boot_true], dtype=np.float64)
        return compute_auroc(y_true, boot_prob[:, c_i] + boot_prob[:, m_i])

    else:
        raise ValueError(f'Unknown metric for bootstrap: {metric_name}')


def compute_bootstrap_ci(
    labels_dict: dict,
    output_arrays: dict,
    metric_name: str,
    n_boot: int = cfg.N_BOOTSTRAP,
    ci_level: float = cfg.BOOTSTRAP_CI_LEVEL,
    seed: int = 8888,
) -> tuple[float, float]:
    """
    Compute bootstrap CI for the specified metric.
    Returns (lower, upper) at ci_level (default 95%).
    """
    rng      = np.random.default_rng(seed)
    samples  = np.array([
        _bootstrap_one(labels_dict, output_arrays, metric_name, rng)
        for _ in range(n_boot)
    ])
    alpha    = 1.0 - ci_level
    lower    = float(np.percentile(samples, 100 * alpha / 2))
    upper    = float(np.percentile(samples, 100 * (1 - alpha / 2)))
    return lower, upper


# ---------------------------------------------------------------------------
# All-metrics driver
# ---------------------------------------------------------------------------

def compute_all_primary_metrics(
    labels_dict: dict,
    output_arrays: dict,
    compute_ci: bool = True,
) -> dict:
    """
    Compute all primary and secondary metrics for one condition.
    Returns a nested dict.
    """
    result = {}

    # Per-class AUROC (M1)
    result['auroc'] = {k: compute_class_auroc(labels_dict, output_arrays, k)
                       for k in cfg.CLASSES}
    result['auroc']['LR']     = compute_lr_auroc(labels_dict, output_arrays)
    result['auroc']['Direct'] = compute_direct_auroc(labels_dict, output_arrays)

    # MacroAUROC (M6)
    result['macro_auroc'] = compute_macro_auroc(labels_dict, output_arrays)

    # WeightedAUROC (M7)
    result['weighted_auroc'] = compute_weighted_auroc(labels_dict, output_arrays)

    # Per-class AUPRC + lift (M2)
    result['auprc'] = {k: compute_class_auprc(labels_dict, output_arrays, k)
                       for k in cfg.CLASSES}
    result['auprc_lift'] = {k: compute_class_auprc_lift(labels_dict, output_arrays, k)
                            for k in cfg.CLASSES}

    # F1/Precision/Recall at optimal threshold (M3-M5)
    result['f1'] = {}
    for k in cfg.CLASSES:
        f1, prec, rec, thresh = compute_class_f1(labels_dict, output_arrays, k)
        result['f1'][k] = {'f1': f1, 'precision': prec, 'recall': rec, 'threshold': thresh}

    # Balanced accuracy (M8)
    result['balanced_accuracy'] = compute_balanced_accuracy(labels_dict, output_arrays)

    # Confusion matrix (M9)
    cm = compute_confusion_matrix(labels_dict, output_arrays)
    result['confusion_matrix'] = cm.tolist()

    # Brier scores (M11)
    result['brier'] = compute_brier_score(labels_dict, output_arrays)

    # ECE (M12)
    result['ece'] = compute_ece(labels_dict, output_arrays)

    # Top-K precision and enrichment (M13, M14)
    result['topk_precision'] = {}
    result['enrichment']     = {}
    pairs  = output_arrays['pairs']
    n_pairs = len(pairs)
    n_lr   = sum(1 for v in labels_dict.values() if v in cfg.LR_CLASSES)
    lr_scores = get_lr_scores(output_arrays)

    for k in ['C', 'LR']:
        result['topk_precision'][k] = {}
        result['enrichment'][k]     = {}
        for K in cfg.TOPK_VALUES:
            if k == 'LR':
                # Score = P(C) + P(M); rank descending; count LR-positives in top K
                top_idx = np.argsort(lr_scores)[::-1][:K]
                hits = sum(1 for idx in top_idx if labels_dict.get(pairs[idx]) in cfg.LR_CLASSES)
                prec = hits / K
                base = n_lr / n_pairs if n_pairs > 0 else float('nan')
                enr  = prec / base if base > 1e-12 else float('nan')
            else:
                prec = compute_topk_precision(labels_dict, output_arrays, k, K)
                enr  = compute_enrichment(labels_dict, output_arrays, k, K)
            result['topk_precision'][k][K] = float(prec)
            result['enrichment'][k][K]     = float(enr)

    # Bootstrap CIs for primary metrics
    if compute_ci:
        result['ci_95'] = {}
        for metric_name in ['macro_auroc', 'c_auroc', 'lr_auroc']:
            lo, hi = compute_bootstrap_ci(labels_dict, output_arrays, metric_name)
            result['ci_95'][metric_name] = {'lower': lo, 'upper': hi}

    return result


def _build_lr_arrays(output_arrays: dict) -> dict:
    """Build a virtual output array where the LR score is treated as class 'LR'."""
    lr_scores = get_lr_scores(output_arrays)
    n = len(lr_scores)
    # Single pseudo-class array: LR probability in column 0
    return {
        'class_prob': lr_scores.reshape(n, 1),
        'class_pred': np.where(lr_scores > 0.5, 'LR', 'X'),
        'pair_keys':  output_arrays['pair_keys'],
        'pairs':      output_arrays['pairs'],
    }
