"""
Blinding engine — Phase 8B.

Enforces the access-control and reveal sequence from phase8a_blinding_protocol.md.
Tracks evaluation state via the evaluation audit log.
"""

import hashlib
import json
import os
import stat
import time
import numpy as np
from . import config8 as cfg


# ---------------------------------------------------------------------------
# Hash utilities
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_dict(d: dict) -> str:
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, ensure_ascii=True).encode('utf-8')
    ).hexdigest()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

def log_eval_event(event: dict) -> None:
    """Append event to evaluation audit log."""
    os.makedirs(os.path.dirname(cfg.EVAL_AUDIT_PATH), exist_ok=True)
    event = {'timestamp_unix': int(time.time()), **event}
    with open(cfg.EVAL_AUDIT_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=True) + '\n')


def read_eval_audit() -> list[dict]:
    if not os.path.exists(cfg.EVAL_AUDIT_PATH):
        return []
    events = []
    with open(cfg.EVAL_AUDIT_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


# ---------------------------------------------------------------------------
# Reveal-sequence state machine
# ---------------------------------------------------------------------------

REQUIRED_EVENT_ORDER = [
    'evaluation_started',
    'input_bundle_created',
    'framework_output_received',
    'blinding_check_passed',
    'labels_loaded_for_scoring',
    'metrics_computed',
    'verdict_recorded',
    'labels_revealed_to_evaluator',
]


def get_completed_events() -> set[str]:
    """Return set of event types that have occurred in the audit log."""
    return {e.get('event') for e in read_eval_audit()}


def assert_event_not_yet(event_type: str) -> None:
    """Raise if a later event has already occurred (sequence violation)."""
    completed = get_completed_events()
    later_events = REQUIRED_EVENT_ORDER[REQUIRED_EVENT_ORDER.index(event_type) + 1:]
    for later in later_events:
        if later in completed:
            raise RuntimeError(
                f'Sequence violation: cannot record {event_type!r} — '
                f'{later!r} has already occurred.'
            )


def assert_event_completed(event_type: str) -> None:
    """Raise if a prerequisite event has not yet occurred."""
    if event_type not in get_completed_events():
        raise RuntimeError(
            f'Sequence violation: {event_type!r} must occur before this step.'
        )


# ---------------------------------------------------------------------------
# Output freeze
# ---------------------------------------------------------------------------

def freeze_output_file(path: str) -> str:
    """Hash output file and set it read-only. Returns SHA-256."""
    h = sha256_file(path)
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # 0o444
    return h


def record_framework_output(condition: str, output_path: str) -> str:
    """
    Freeze the framework output, record the hash, return the hash.
    Must be called immediately after the framework writes its output.
    """
    assert_event_not_yet('framework_output_received')
    h = freeze_output_file(output_path)
    log_eval_event({
        'event':      'framework_output_received',
        'condition':  condition,
        'output_file': output_path,
        'sha256':     h,
    })
    return h


# ---------------------------------------------------------------------------
# Blinding checks BC-1 through BC-4
# ---------------------------------------------------------------------------

def run_blinding_checks(
    output_path: str,
    recorded_output_hash: str,
    output_metadata: dict | None = None,
) -> dict[str, bool]:
    """
    Run blinding checks before scoring.

    BC-1: Output file hash integrity
    BC-2: Label file hash integrity
    BC-3: Information barrier audit (path-based)
    BC-4: Output schema validity (9900 pairs, sums to 1)

    Returns {check_id: passed} dict.
    """
    results = {}

    # BC-1: Recompute output hash
    current_hash = sha256_file(output_path)
    bc1_ok = (current_hash == recorded_output_hash)
    results['BC-1'] = bc1_ok
    if not bc1_ok:
        log_eval_event({
            'event': 'blinding_check_failed',
            'check': 'BC-1',
            'reason': 'Output file hash mismatch — possible tampering',
            'expected': recorded_output_hash,
            'actual':   current_hash,
        })

    # BC-2: Label file hash
    label_hash = sha256_file(cfg.LABELS_PATH)
    bc2_ok = (label_hash == cfg.COMMITTED_LABEL_HASH)
    results['BC-2'] = bc2_ok
    if not bc2_ok:
        log_eval_event({
            'event':    'blinding_check_failed',
            'check':    'BC-2',
            'reason':   'Label file hash mismatch — labels may have been modified',
            'expected': cfg.COMMITTED_LABEL_HASH,
            'actual':   label_hash,
        })

    # BC-3: Path audit (check output metadata for forbidden paths)
    bc3_ok = True
    bc3_warnings = []
    if output_metadata:
        metadata_str = json.dumps(output_metadata, ensure_ascii=True).lower()
        forbidden_indicators = [
            'ground_truth', 'labels.json', 'a_sparse',
            'phase7b', 'phase7c', 'config8', 'sa_set',
        ]
        for indicator in forbidden_indicators:
            if indicator in metadata_str:
                bc3_warnings.append(f'Metadata contains reference to {indicator!r}')
                bc3_ok = False
    results['BC-3'] = bc3_ok
    if bc3_warnings:
        log_eval_event({
            'event':    'blinding_check_warning',
            'check':    'BC-3',
            'warnings': bc3_warnings,
        })

    # BC-4: Schema validity
    try:
        with open(output_path, 'r') as f:
            raw = json.load(f)
        preds = raw.get('predictions', [])
        n_pairs = len(preds)
        all_sums_ok = all(
            abs(sum(p.get('class_prob', {}).get(k, 0) for k in cfg.CLASSES) - 1.0) < 1e-5
            for p in preds
        )
        bc4_ok = (n_pairs == cfg.N_PAIRS) and all_sums_ok
        if not bc4_ok:
            log_eval_event({
                'event':     'blinding_check_warning',
                'check':     'BC-4',
                'n_pairs':   n_pairs,
                'expected':  cfg.N_PAIRS,
                'sums_ok':   all_sums_ok,
            })
    except Exception as e:
        bc4_ok = False
        log_eval_event({'event': 'blinding_check_failed', 'check': 'BC-4', 'error': str(e)})
    results['BC-4'] = bc4_ok

    all_passed = all(results.values())
    log_eval_event({
        'event':      'blinding_check_passed' if all_passed else 'blinding_check_failed',
        'all_passed': all_passed,
        'checks':     results,
    })
    return results


# ---------------------------------------------------------------------------
# Label loading (gated by blinding sequence)
# ---------------------------------------------------------------------------

def load_labels_for_scoring() -> dict:
    """
    Load ground-truth labels. May only be called after blinding checks pass.
    Logs the label-load event.
    """
    assert_event_completed('blinding_check_passed')
    log_eval_event({
        'event':       'labels_loaded_for_scoring',
        'label_hash':  cfg.COMMITTED_LABEL_HASH,
        'label_path':  cfg.LABELS_PATH,
    })
    import json
    with open(cfg.LABELS_PATH, 'r', encoding='utf-8') as f:
        d = json.load(f)
    return {(r['i'], r['j']): r['label'] for r in d['labels']}


# ---------------------------------------------------------------------------
# Verdict recording
# ---------------------------------------------------------------------------

def record_verdict(verdict_dict: dict) -> str:
    """
    Write verdict to file, set read-only, log event.
    Returns the verdict SHA-256 hash.
    """
    assert_event_completed('metrics_computed')
    os.makedirs(cfg.PHASE8B_DIR, exist_ok=True)
    verdict_bytes = json.dumps(verdict_dict, indent=2, ensure_ascii=True).encode('utf-8')
    with open(cfg.VERDICT_PATH, 'wb') as f:
        f.write(verdict_bytes)
    os.chmod(cfg.VERDICT_PATH, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    h = hashlib.sha256(verdict_bytes).hexdigest()
    log_eval_event({
        'event':        'verdict_recorded',
        'verdict':      verdict_dict.get('verdict'),
        'verdict_hash': h,
        'verdict_path': cfg.VERDICT_PATH,
    })
    return h


# ---------------------------------------------------------------------------
# Label reveal (final step)
# ---------------------------------------------------------------------------

def record_label_reveal(verdict: str, primary_metrics: dict) -> None:
    """
    Log the label-reveal event. After this, labels may be shown to the evaluator.
    """
    assert_event_completed('verdict_recorded')
    log_eval_event({
        'event':              'labels_revealed_to_evaluator',
        'oracle_z_verdict':   verdict,
        'primary_metrics':    primary_metrics,
        'label_hash_at_reveal': cfg.COMMITTED_LABEL_HASH,
    })


# ---------------------------------------------------------------------------
# Information barrier — check framework code for forbidden paths
# ---------------------------------------------------------------------------

def audit_framework_code_paths(framework_code_paths: list[str]) -> list[str]:
    """
    Scan framework source files for references to forbidden paths/symbols.
    Returns list of violation strings (empty = clean).
    """
    forbidden_patterns = [
        'ground_truth',
        'labels.json',
        'a_sparse',
        'A_sparse',
        'H2_TARGETS',
        'SA =',
        'frozenset({132',
        'config8.COMMITTED',
        'phase7b',
        'phase7c',
        '// 25',          # module arithmetic
    ]
    violations = []
    for fpath in framework_code_paths:
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for pattern in forbidden_patterns:
            if pattern in content:
                violations.append(f'{fpath}: contains {pattern!r}')
    return violations


# ---------------------------------------------------------------------------
# Input bundle constructor (evaluation-side; framework never sees this)
# ---------------------------------------------------------------------------

def build_input_bundle(condition: str) -> dict:
    """
    Construct the framework input bundle for one condition.
    Reads ONLY trajectory data files. Does not touch ground_truth/.
    """
    import numpy as np

    runs = []
    for r in range(5):  # R=5 runs
        fpath = os.path.join(cfg.DATASET_DIR, f'{condition}_run{r}.npz')
        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Dataset file not found: {fpath}')
        data = np.load(fpath)
        run_dict = {
            'run_index': r,
            'y': data['y'],
            'z_oracle': data['z_oracle'] if 'z_oracle' in data.files else None,
        }
        runs.append(run_dict)

    return {
        'condition': condition,
        'n_obs':     100,
        'n_runs':    5,
        'dt':        0.10,
        't_eff':     48000,
        'runs':      runs,
    }
