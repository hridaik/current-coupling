"""
Phase 7C — Canonical dataset generation.

Generates one canonical benchmark corpus from the locked Phase 7B simulator.
No scientific evaluation. No parameter tuning. No post-hoc adjustment.

Order of operations (enforced):
  1. Acceptance gate check (must pass before any simulation)
  2. Load locked artifacts (A_sparse, labels)
  3. Simulate all conditions × all runs
  4. Save artifacts
  5. Return metadata dict for hashing by freeze_dataset.py
"""

import hashlib
import json
import os
import time
import numpy as np

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.insert(0, PROJECT_ROOT)

from scripts.phase7b import config as cfg
from scripts.phase7b.acceptance import check_all_acceptance_tests_passed
from scripts.phase7b.audit import verify_label_hash, log_event, read_audit_log
from scripts.phase7b.graph import build_D, compute_B
from scripts.phase7b.dynamics import simulate_run

CANONICAL_DIR = os.path.join(PROJECT_ROOT, 'results', 'phase7c', 'canonical')
DATA_DIR      = os.path.join(CANONICAL_DIR, 'data')


def _make_B_fn(gamma_H2: float):
    """Return a B function with the given gamma override."""
    def B_fn(z: float) -> np.ndarray:
        return compute_B(z, gamma_H2=gamma_H2)
    return B_fn


def generate_canonical_dataset(verbose: bool = True) -> dict:
    """
    Generate the full canonical dataset.

    Returns a metadata dict describing all produced artifacts.
    """
    t_start = time.time()
    t_start_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t_start))

    # -----------------------------------------------------------------------
    # Gate: all acceptance tests must pass before simulation
    # -----------------------------------------------------------------------
    check_all_acceptance_tests_passed(cfg.AUDIT_LOG_PATH)
    if verbose:
        print('Acceptance gate: PASSED')

    # -----------------------------------------------------------------------
    # Checkpoint V2: verify label hash before using labels
    # -----------------------------------------------------------------------
    verify_label_hash(checkpoint='V2')
    if verbose:
        print('Checkpoint V2: PASSED')

    # -----------------------------------------------------------------------
    # Load locked artifacts
    # -----------------------------------------------------------------------
    A = np.load(cfg.A_SPARSE_PATH)
    D, D_sqrt, u = build_D()

    with open(cfg.LABELS_HASH_PATH) as f:
        committed_label_hash = f.read().strip().split()[0]

    with open(cfg.A_HASH_PATH) as f:
        committed_A_hash = f.read().strip().split()[0]

    if verbose:
        print(f'Loaded A_sparse: {A.shape}, spectral abscissa: '
              f'{float(np.max(np.linalg.eigvals(A).real)):.6f}')
        print(f'Label hash: {committed_label_hash}')

    # -----------------------------------------------------------------------
    # Simulate all conditions × all runs
    # -----------------------------------------------------------------------
    os.makedirs(DATA_DIR, exist_ok=True)

    artifact_index = []   # list of {condition, run, file, shape, dtype}

    for condition, cond_params in cfg.CONDITIONS.items():
        gamma_H2  = cond_params['gamma_H2']
        provide_z = cond_params['provide_z']
        use_obs   = cond_params['use_obs_model']
        B_fn      = _make_B_fn(gamma_H2)

        if verbose:
            print(f'\nCondition: {condition}  (gamma_H2={gamma_H2}, '
                  f'provide_z={provide_z}, use_obs={use_obs})')

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
            fpath = os.path.join(DATA_DIR, fname)

            arrays = {'y': result['y']}
            if result['z_oracle'] is not None:
                arrays['z_oracle'] = result['z_oracle']

            np.savez_compressed(fpath, **arrays)

            if verbose:
                y_shape = result['y'].shape
                z_shape = result['z_oracle'].shape if result['z_oracle'] is not None else None
                print(f'  run {r}: y={y_shape}, z={z_shape} → {fname}')

            artifact_index.append({
                'condition': condition,
                'run_index': r,
                'file':      fname,
                'y_shape':   list(result['y'].shape),
                'z_shape':   list(result['z_oracle'].shape) if result['z_oracle'] is not None else None,
                'gamma_H2':  gamma_H2,
                'provide_z': provide_z,
                'use_obs_model': use_obs,
            })

    t_end     = time.time()
    t_end_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t_end))
    duration_s = round(t_end - t_start, 1)

    # -----------------------------------------------------------------------
    # Write metadata.json (before hashing)
    # -----------------------------------------------------------------------
    metadata = {
        'phase': '7C',
        'dataset_type': 'canonical',
        'generated_at': t_start_iso,
        'completed_at': t_end_iso,
        'duration_seconds': duration_s,
        'code_commit': _git_commit(),
        'simulator': {
            'module': 'scripts.phase7b.dynamics',
            'function': 'simulate_run',
            'spec': 'phase6b_architecture_spec.md',
        },
        'parameters': {
            'N_OBS': cfg.N_OBS,
            'N_TOTAL': cfg.N_TOTAL,
            'T': cfg.T,
            'T_WARMUP': cfg.T_WARMUP,
            'T_EFF': cfg.T_EFF,
            'DT': cfg.DT,
            'R': cfg.R,
            'GAMMA_H2': cfg.GAMMA_H2,
            'THETA_Z': cfg.THETA_Z,
            'SIGMA_Z': cfg.SIGMA_Z,
            'D_0': cfg.D_0,
            'EPS_LR': cfg.EPS_LR,
            'KAPPA_CA': cfg.KAPPA_CA,
            'SIGMA_OBS_NOISE': cfg.SIGMA_OBS_NOISE,
            'NONLINEARITY': cfg.NONLINEARITY,
        },
        'seed_policy': {
            'z_seed': 'z_seed(run) = 49 + run_index',
            'x_seed': 'x_seed(run) = 60 + run_index',
            'sparsity_seeds': dict(cfg.SEEDS),
            'run_indices': list(range(cfg.R)),
        },
        'conditions': {
            name: {
                'gamma_H2': v['gamma_H2'],
                'provide_z': v['provide_z'],
                'use_obs_model': v['use_obs_model'],
            }
            for name, v in cfg.CONDITIONS.items()
        },
        'locked_artifacts': {
            'labels_hash': committed_label_hash,
            'A_sparse_hash': committed_A_hash,
            'labels_path': cfg.LABELS_PATH,
            'A_sparse_path': cfg.A_SPARSE_PATH,
        },
        'artifacts': artifact_index,
        'n_artifacts': len(artifact_index),
    }

    metadata_path = os.path.join(CANONICAL_DIR, 'metadata.json')
    metadata_bytes = json.dumps(metadata, indent=2, ensure_ascii=True).encode('utf-8')
    with open(metadata_path, 'wb') as f:
        f.write(metadata_bytes)

    if verbose:
        print(f'\nMetadata written: {metadata_path}')
        print(f'Generation complete in {duration_s:.1f}s')

    log_event({
        'event': 'phase7c_canonical_generation_complete',
        'n_artifacts': len(artifact_index),
        'duration_seconds': duration_s,
        'generated_at': t_start_iso,
    })

    return metadata


def _git_commit() -> str:
    """Return current HEAD commit hash, or 'unknown'."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except Exception:
        return 'unknown'


if __name__ == '__main__':
    print('=' * 60)
    print('PHASE 7C: Canonical dataset generation')
    print('=' * 60)
    metadata = generate_canonical_dataset(verbose=True)
    print(f'\nArtifacts: {metadata["n_artifacts"]} files in results/phase7c/canonical/data/')
