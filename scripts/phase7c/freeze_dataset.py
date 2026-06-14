"""
Phase 7C — Hash all artifacts and freeze (set read-only).

Must be run after generate_dataset.py and before any downstream use.
"""

import hashlib
import json
import os
import stat
import time
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.insert(0, PROJECT_ROOT)

from scripts.phase7b import config as cfg
from scripts.phase7b.audit import log_event

CANONICAL_DIR = os.path.join(PROJECT_ROOT, 'results', 'phase7c', 'canonical')
DATA_DIR      = os.path.join(CANONICAL_DIR, 'data')


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _file_size(path: str) -> int:
    return os.path.getsize(path)


def _set_readonly(path: str) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # 0o444


def freeze_canonical_dataset(verbose: bool = True) -> dict:
    """
    Hash every artifact in results/phase7c/canonical/, write hashes.json,
    and set all data files to read-only.

    Returns the hashes dict.
    """
    if verbose:
        print('Hashing all artifacts...')

    hashes = {}

    # -----------------------------------------------------------------------
    # Hash data files
    # -----------------------------------------------------------------------
    data_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith('.npz'))
    for fname in data_files:
        fpath = os.path.join(DATA_DIR, fname)
        h = _sha256_file(fpath)
        sz = _file_size(fpath)
        hashes[fname] = {'sha256': h, 'bytes': sz, 'type': 'trajectory_npz'}
        if verbose:
            print(f'  {fname}: {sz:,} bytes  {h[:16]}…')

    # -----------------------------------------------------------------------
    # Hash metadata.json
    # -----------------------------------------------------------------------
    meta_path = os.path.join(CANONICAL_DIR, 'metadata.json')
    h = _sha256_file(meta_path)
    sz = _file_size(meta_path)
    hashes['metadata.json'] = {'sha256': h, 'bytes': sz, 'type': 'metadata_json'}
    if verbose:
        print(f'  metadata.json: {sz:,} bytes  {h[:16]}…')

    # -----------------------------------------------------------------------
    # Hash locked ground-truth artifacts (provenance chain)
    # -----------------------------------------------------------------------
    for src_name, src_path in [
        ('labels.json',              cfg.LABELS_PATH),
        ('labels.sha256',            cfg.LABELS_HASH_PATH),
        ('A_sparse.npy',             cfg.A_SPARSE_PATH),
        ('A_sparse.sha256',          cfg.A_HASH_PATH),
        ('construction_params.json', cfg.PARAMS_PATH),
        ('audit_log.jsonl',          cfg.AUDIT_LOG_PATH),
    ]:
        h = _sha256_file(src_path)
        sz = _file_size(src_path)
        hashes[src_name] = {
            'sha256': h, 'bytes': sz,
            'type': 'locked_ground_truth',
            'source_path': src_path,
        }
        if verbose:
            print(f'  {src_name}: {sz:,} bytes  {h[:16]}…')

    # -----------------------------------------------------------------------
    # Write hashes.json to canonical dir
    # -----------------------------------------------------------------------
    hashes_snapshot = {
        'frozen_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'n_files': len(hashes),
        'files': hashes,
    }
    hashes_path = os.path.join(CANONICAL_DIR, 'hashes.json')
    hashes_bytes = json.dumps(hashes_snapshot, indent=2, ensure_ascii=True).encode('utf-8')
    with open(hashes_path, 'wb') as f:
        f.write(hashes_bytes)

    # Hash hashes.json itself (meta-hash)
    meta_hash = hashlib.sha256(hashes_bytes).hexdigest()
    hashes_snapshot['hashes_json_sha256'] = meta_hash

    # Rewrite with the meta-hash included
    hashes_bytes2 = json.dumps(hashes_snapshot, indent=2, ensure_ascii=True).encode('utf-8')
    with open(hashes_path, 'wb') as f:
        f.write(hashes_bytes2)

    if verbose:
        print(f'\nhashes.json written: {hashes_path}')
        print(f'  meta-hash: {meta_hash}')

    # -----------------------------------------------------------------------
    # Freeze: set all data files and metadata to read-only
    # -----------------------------------------------------------------------
    if verbose:
        print('\nSetting files read-only...')
    for fname in data_files:
        _set_readonly(os.path.join(DATA_DIR, fname))
        if verbose:
            print(f'  → {fname} (read-only)')
    _set_readonly(meta_path)
    _set_readonly(hashes_path)
    if verbose:
        print(f'  → metadata.json (read-only)')
        print(f'  → hashes.json (read-only)')

    log_event({
        'event': 'phase7c_dataset_frozen',
        'n_data_files': len(data_files),
        'hashes_meta_hash': meta_hash,
        'frozen_at': hashes_snapshot['frozen_at'],
    })

    return hashes_snapshot


if __name__ == '__main__':
    print('=' * 60)
    print('PHASE 7C: Freeze canonical dataset')
    print('=' * 60)
    result = freeze_canonical_dataset(verbose=True)
    print(f'\nFrozen {result["n_files"]} artifacts.')
    print(f'Meta-hash: {result["hashes_json_sha256"]}')
