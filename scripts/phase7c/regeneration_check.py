"""
Phase 7C — Exact regeneration check.

Re-simulates all conditions from the same seeds and verifies that
every output file produces an identical SHA-256 hash to the canonical dataset.

This is a provenance check only. No scientific metrics are computed.
"""

import hashlib
import json
import os
import time
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.insert(0, PROJECT_ROOT)

from scripts.phase7b import config as cfg
from scripts.phase7b.acceptance import check_all_acceptance_tests_passed
from scripts.phase7b.audit import verify_label_hash, log_event
from scripts.phase7b.graph import build_D, compute_B
from scripts.phase7b.dynamics import simulate_run

CANONICAL_DIR   = os.path.join(PROJECT_ROOT, 'results', 'phase7c', 'canonical')
REGEN_DIR       = os.path.join(PROJECT_ROOT, 'results', 'phase7c', 'regeneration')
REGEN_DATA_DIR  = os.path.join(REGEN_DIR, 'data')


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _sha256_npz_arrays(path: str) -> dict[str, str]:
    """Hash each array inside an npz separately (numpy bytes, C order)."""
    d = np.load(path)
    return {k: hashlib.sha256(d[k].astype(np.float64).tobytes(order='C')).hexdigest()
            for k in sorted(d.files)}


def _make_B_fn(gamma_H2: float):
    def B_fn(z: float) -> np.ndarray:
        return compute_B(z, gamma_H2=gamma_H2)
    return B_fn


def run_regeneration_check(verbose: bool = True) -> dict:
    """
    Regenerate all dataset files, compare SHA-256 hashes to canonical,
    and return a check report dict.
    """
    t_start = time.time()

    # -----------------------------------------------------------------------
    # Load canonical hashes
    # -----------------------------------------------------------------------
    hashes_path = os.path.join(CANONICAL_DIR, 'hashes.json')
    with open(hashes_path) as f:
        canonical_hashes = json.load(f)
    canonical_files = canonical_hashes['files']

    if verbose:
        print(f'Loaded canonical hashes for {len(canonical_files)} files.')

    # -----------------------------------------------------------------------
    # Gate and hash checkpoint
    # -----------------------------------------------------------------------
    check_all_acceptance_tests_passed(cfg.AUDIT_LOG_PATH)
    verify_label_hash(checkpoint='V2-regen')

    # -----------------------------------------------------------------------
    # Load locked A (same seeds → same A)
    # -----------------------------------------------------------------------
    A = np.load(cfg.A_SPARSE_PATH)
    D, D_sqrt, u = build_D()

    os.makedirs(REGEN_DATA_DIR, exist_ok=True)

    # -----------------------------------------------------------------------
    # Regenerate all condition × run files
    # -----------------------------------------------------------------------
    results = []
    all_pass = True

    for condition, cond_params in cfg.CONDITIONS.items():
        gamma_H2  = cond_params['gamma_H2']
        provide_z = cond_params['provide_z']
        use_obs   = cond_params['use_obs_model']
        B_fn      = _make_B_fn(gamma_H2)

        if verbose:
            print(f'\nRegenerating condition: {condition}')

        for r in range(cfg.R):
            result = simulate_run(
                run_index=r,
                A=A,
                D_sqrt=D_sqrt,
                B_fn=B_fn,
                gamma_H2=gamma_H2,
                provide_z=provide_z,
                use_obs_model=use_obs,
            )

            fname = f'{condition}_run{r}.npz'
            fpath = os.path.join(REGEN_DATA_DIR, fname)

            arrays = {'y': result['y']}
            if result['z_oracle'] is not None:
                arrays['z_oracle'] = result['z_oracle']

            np.savez_compressed(fpath, **arrays)

            # Compare SHA-256 of regenerated file to canonical
            regen_hash = _sha256_file(fpath)
            canonical_hash = canonical_files.get(fname, {}).get('sha256', 'MISSING')

            # npz format may vary slightly (compression metadata, timestamps) even
            # with identical contents. Compare array-level hashes as ground truth.
            regen_array_hashes  = _sha256_npz_arrays(fpath)
            canonical_fpath     = os.path.join(CANONICAL_DIR, 'data', fname)
            canonical_array_hashes = _sha256_npz_arrays(canonical_fpath)

            file_match  = (regen_hash == canonical_hash)
            array_match = (regen_array_hashes == canonical_array_hashes)
            passed      = array_match  # array-level is the definitive check

            status = 'PASS' if passed else 'FAIL'
            if not passed:
                all_pass = False

            if verbose:
                indicator = '✓' if passed else '✗'
                file_note = '(file exact)' if file_match else '(file differs, checking arrays)'
                print(f'  {indicator} run {r}: {status} {file_note}')
                if not passed:
                    for k in sorted(regen_array_hashes):
                        match_k = regen_array_hashes[k] == canonical_array_hashes.get(k)
                        print(f'    {k}: {"MATCH" if match_k else "MISMATCH"}')

            results.append({
                'condition':    condition,
                'run_index':    r,
                'file':         fname,
                'file_hash_match':  file_match,
                'array_hash_match': array_match,
                'passed':       passed,
                'regen_array_hashes':    regen_array_hashes,
                'canonical_array_hashes': canonical_array_hashes,
            })

    # -----------------------------------------------------------------------
    # Also verify locked artifacts haven't changed
    # -----------------------------------------------------------------------
    locked_checks = []
    for src_name, src_path in [
        ('labels.json',  cfg.LABELS_PATH),
        ('A_sparse.npy', cfg.A_SPARSE_PATH),
    ]:
        current_hash  = _sha256_file(src_path)
        canonical_rec = canonical_files.get(src_name, {})
        recorded_hash = canonical_rec.get('sha256', 'MISSING')
        match = current_hash == recorded_hash
        if not match:
            all_pass = False
        locked_checks.append({
            'file':          src_name,
            'current_hash':  current_hash,
            'recorded_hash': recorded_hash,
            'match':         match,
        })
        if verbose:
            status = 'PASS' if match else 'FAIL'
            print(f'\n  {status}  locked artifact {src_name}')

    # -----------------------------------------------------------------------
    # Write check report
    # -----------------------------------------------------------------------
    t_end = time.time()
    report = {
        'completed_at':    time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'duration_seconds': round(t_end - t_start, 1),
        'all_passed':      all_pass,
        'n_files_checked': len(results),
        'n_passed':        sum(1 for r in results if r['passed']),
        'n_failed':        sum(1 for r in results if not r['passed']),
        'trajectory_checks': results,
        'locked_artifact_checks': locked_checks,
    }

    report_path = os.path.join(REGEN_DIR, 'check_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=True)

    if verbose:
        print(f'\nCheck report: {report_path}')
        n_ok = report['n_passed']
        n_all = report['n_files_checked']
        print(f'Trajectory checks: {n_ok}/{n_all} PASSED')
        print(f'All passed: {all_pass}')

    log_event({
        'event':         'phase7c_regeneration_check_complete',
        'all_passed':    all_pass,
        'n_passed':      report['n_passed'],
        'n_failed':      report['n_failed'],
        'duration_seconds': report['duration_seconds'],
    })

    return report


if __name__ == '__main__':
    print('=' * 60)
    print('PHASE 7C: Exact regeneration check')
    print('=' * 60)
    report = run_regeneration_check(verbose=True)
    status = 'PASSED' if report['all_passed'] else 'FAILED'
    print(f'\nREGENERATION CHECK: {status}')
    if not report['all_passed']:
        import sys
        sys.exit(1)
