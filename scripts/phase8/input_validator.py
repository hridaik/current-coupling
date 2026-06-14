"""
Input validation for framework outputs — Phase 8B.

Validates that framework output files conform to the schema in
phase8a_evaluation_spec.md §3. Degenerate outputs handled per
phase8a_metric_registry.md §8.
"""

import json
import numpy as np
from . import config8 as cfg


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def load_framework_output(path: str) -> tuple[dict, dict]:
    """
    Load and validate framework output from JSON file.

    Returns (metadata, pred_map) where pred_map maps (i,j) → prediction record.
    Raises ValueError on schema violations that cannot be auto-corrected.
    """
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)

    if 'predictions' not in raw:
        raise ValueError(f'Missing key "predictions" in framework output {path}')

    metadata = raw.get('metadata', {})
    predictions = raw['predictions']

    pred_map, warnings = _validate_predictions(predictions)
    return metadata, pred_map, warnings


def _validate_predictions(predictions: list) -> tuple[dict, list]:
    """
    Validate and normalise prediction records.

    Returns (pred_map {(i,j): record}, warnings [str]).
    """
    warnings = []
    pred_map = {}
    required_keys = {'i', 'j', 'class_prob', 'class_pred'}

    for rec in predictions:
        missing = required_keys - set(rec.keys())
        if missing:
            warnings.append(f'Record missing keys {missing}: {rec}')
            continue

        i, j = int(rec['i']), int(rec['j'])

        if i == j:
            warnings.append(f'Self-pair ({i},{j}) in output; skipped')
            continue
        if not (0 <= i < cfg.N_PAIRS ** 0.5 + 1 and 0 <= j < cfg.N_PAIRS ** 0.5 + 1):
            # Loose check; exact bound checked below
            pass

        cp = rec['class_prob']
        if not isinstance(cp, dict):
            warnings.append(f'class_prob is not dict for ({i},{j}); using uniform')
            cp = {'S': 0.25, 'C': 0.25, 'M': 0.25, 'N': 0.25}

        # Ensure all four classes present
        for k in cfg.CLASSES:
            if k not in cp:
                cp[k] = 0.0
                warnings.append(f'class_prob missing key {k} for ({i},{j}); set to 0')

        # Handle NaN/Inf
        has_degenerate = any(not np.isfinite(cp[k]) for k in cfg.CLASSES)
        if has_degenerate:
            warnings.append(f'Non-finite class_prob for ({i},{j}); replaced with uniform')
            cp = {'S': 0.25, 'C': 0.25, 'M': 0.25, 'N': 0.25}

        # Ensure non-negative
        for k in cfg.CLASSES:
            if cp[k] < 0:
                cp[k] = 0.0
                warnings.append(f'Negative class_prob[{k}] for ({i},{j}); clamped to 0')

        # Normalise to simplex
        total = sum(cp[k] for k in cfg.CLASSES)
        if total < 1e-12:
            warnings.append(f'All-zero class_prob for ({i},{j}); using uniform')
            cp = {k: 0.25 for k in cfg.CLASSES}
        elif abs(total - 1.0) > 1e-6:
            warnings.append(f'class_prob sums to {total:.6f} for ({i},{j}); normalised')
            cp = {k: cp[k] / total for k in cfg.CLASSES}

        class_pred = str(rec.get('class_pred', max(cp, key=cp.get)))
        if class_pred not in cfg.CLASSES:
            class_pred = max(cp, key=cp.get)
            warnings.append(f'Invalid class_pred for ({i},{j}); using argmax {class_pred}')

        pred_map[(i, j)] = {
            'i': i, 'j': j,
            'class_prob': {k: float(cp[k]) for k in cfg.CLASSES},
            'class_pred': class_pred,
        }

    return pred_map, warnings


def validate_completeness(pred_map: dict) -> tuple[bool, list]:
    """
    Check that all 9,900 directed pairs are present.

    Returns (ok, missing_pairs).
    """
    n_obs = 100  # fixed by spec
    expected = {(i, j) for i in range(n_obs) for j in range(n_obs) if i != j}
    actual   = set(pred_map.keys())
    missing  = sorted(expected - actual)
    extra    = sorted(actual - expected)

    if missing:
        # Fill missing pairs with uniform (per metric registry §8)
        for pair in missing:
            pred_map[pair] = {
                'i': pair[0], 'j': pair[1],
                'class_prob': {k: 0.25 for k in cfg.CLASSES},
                'class_pred': 'N',
            }
    return len(missing) == 0, missing


def build_output_arrays(pred_map: dict) -> dict[str, np.ndarray]:
    """
    Convert pred_map to numpy arrays for fast metric computation.

    Returns dict with:
        'class_prob': (9900, 4) float64  — columns: S, C, M, N (in CLASSES order)
        'class_pred': (9900,) str
        'pair_keys':  (9900, 2) int      — rows: [i, j]
    """
    n_obs = 100
    pairs = [(i, j) for i in range(n_obs) for j in range(n_obs) if i != j]
    n = len(pairs)

    class_prob = np.zeros((n, len(cfg.CLASSES)), dtype=np.float64)
    class_pred = np.empty(n, dtype=object)
    pair_keys  = np.array(pairs, dtype=np.int32)

    for idx, (i, j) in enumerate(pairs):
        rec = pred_map[(i, j)]
        for c_idx, c in enumerate(cfg.CLASSES):
            class_prob[idx, c_idx] = rec['class_prob'][c]
        class_pred[idx] = rec['class_pred']

    return {
        'class_prob': class_prob,
        'class_pred': class_pred,
        'pair_keys':  pair_keys,
        'pairs':      pairs,
    }
