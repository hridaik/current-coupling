"""
Phase 8C: Run all four sensitivity axes and save results.

Pre-specified sensitivity points (from phase8c_scope_map_plan.md):

  Axis 1 (GAMMA_H2):     {0.5, 1.5, 3.0, 6.0, 12.0}
  Axis 2 (N_H2_ACTIVE):  {0, 2, 4, 6, 8}
  Axis 3 (THETA_Z):      {0.01, 0.05, 0.10, 0.50, 2.00}
  Axis 4 (positive ctrl): GAMMA_H2=12.0, THETA_Z=0.01

Frozen benchmark reference: MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197

Usage:
    python -m scripts.phase8c.run_axes
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg
from scripts.phase8c.probe import (
    load_frozen_graph,
    load_frozen_labels,
    load_canonical_run,
    simulate_probe_run,
    run_probe,
)

N_RUNS   = 5
OUT_DIR  = os.path.join(cfg.PROJECT_ROOT, 'results', 'phase8c')


# ---------------------------------------------------------------------------
# Frozen benchmark reference
# ---------------------------------------------------------------------------

BENCHMARK = {
    'label':       'oracle_z (frozen)',
    'macro_auroc': 0.5385,
    'c_auroc':     0.4484,
    'lr_auroc':    0.4197,
    's_auroc':     0.8531,
    'm_auroc':     0.1561,
    'n_auroc':     0.6963,
}


# ---------------------------------------------------------------------------
# Axis helpers
# ---------------------------------------------------------------------------

def _load_canonical_runs(condition: str) -> list[dict]:
    return [load_canonical_run(condition, r) for r in range(N_RUNS)]


def _simulate_runs(A, D_sqrt, **kwargs) -> list[dict]:
    return [simulate_probe_run(r, A, D_sqrt, **kwargs) for r in range(N_RUNS)]


# ---------------------------------------------------------------------------
# Axis 1: GAMMA_H2 sensitivity
# ---------------------------------------------------------------------------

def run_axis1(A, D_sqrt, labels, verbose=True):
    """Current-supported link strength: vary GAMMA_H2."""
    print('\n' + '='*60)
    print('AXIS 1: GAMMA_H2 sensitivity')
    print('='*60)

    results = []

    # GAMMA_H2=3.0: use frozen benchmark result directly
    results.append({**BENCHMARK, 'label': 'GAMMA_H2=3.0 (frozen)'})
    print('  GAMMA_H2=3.0: using frozen benchmark result')

    for gamma in [0.5, 1.5, 6.0, 12.0]:
        t0 = time.time()
        if gamma == 1.5:
            # Use existing canonical weak_z data
            runs = _load_canonical_runs('weak_z')
            source = 'canonical weak_z'
        elif gamma == 6.0:
            # Use existing canonical strong_z data
            runs = _load_canonical_runs('strong_z')
            source = 'canonical strong_z'
        else:
            # New probe simulation
            runs = _simulate_runs(A, D_sqrt, gamma_h2=gamma)
            source = 'probe simulation'

        result = run_probe(runs, labels, label=f'GAMMA_H2={gamma}')
        elapsed = time.time() - t0

        if verbose:
            print(f'  GAMMA_H2={gamma:.1f} ({source}): '
                  f'MacroAUROC={result["macro_auroc"]:.4f}, '
                  f'C-AUROC={result["c_auroc"]:.4f}, '
                  f'LR-AUROC={result["lr_auroc"]:.4f}  [{elapsed:.1f}s]')
        results.append(result)

    # Sort by gamma value for output
    order = [0.5, 1.5, 3.0, 6.0, 12.0]
    results.sort(key=lambda r: float(r['label'].split('=')[1].split(' ')[0]))
    return results


# ---------------------------------------------------------------------------
# Axis 2: N_H2_ACTIVE sensitivity
# ---------------------------------------------------------------------------

def run_axis2(A, D_sqrt, labels, verbose=True):
    """Hidden-neuron fraction: vary number of active H2 neurons."""
    print('\n' + '='*60)
    print('AXIS 2: N_H2_ACTIVE sensitivity')
    print('='*60)

    sa_sorted = sorted(cfg.SA)  # [132, 133, ..., 139]
    results   = []

    for k in [0, 2, 4, 6, 8]:
        t0 = time.time()
        if k == 8:
            # Use frozen benchmark (all H2 active with GAMMA_H2=3.0)
            results.append({**BENCHMARK, 'label': 'N_H2_ACTIVE=8 (frozen)'})
            print(f'  N_H2_ACTIVE=8: using frozen benchmark result')
            continue

        active_set = frozenset(sa_sorted[:k])
        runs = _simulate_runs(A, D_sqrt, gamma_h2=cfg.GAMMA_H2, h2_active_set=active_set)
        result = run_probe(runs, labels, label=f'N_H2_ACTIVE={k}')
        elapsed = time.time() - t0

        if verbose:
            print(f'  N_H2_ACTIVE={k} (active={sorted(active_set) if k>0 else []}): '
                  f'MacroAUROC={result["macro_auroc"]:.4f}, '
                  f'C-AUROC={result["c_auroc"]:.4f}, '
                  f'LR-AUROC={result["lr_auroc"]:.4f}  [{elapsed:.1f}s]')
        results.append(result)

    results.sort(key=lambda r: int(r['label'].split('=')[1].split(' ')[0]))
    return results


# ---------------------------------------------------------------------------
# Axis 3: THETA_Z sensitivity
# ---------------------------------------------------------------------------

def run_axis3(A, D_sqrt, labels, verbose=True):
    """State separability: vary OU mean-reversion rate theta_z."""
    print('\n' + '='*60)
    print('AXIS 3: THETA_Z sensitivity')
    print('='*60)

    results = []

    for theta in [0.01, 0.05, 0.10, 0.50, 2.00]:
        t0 = time.time()
        if theta == 0.10:
            # Baseline — use frozen benchmark
            results.append({**BENCHMARK, 'label': 'THETA_Z=0.10 (frozen)'})
            print(f'  THETA_Z=0.10: using frozen benchmark result')
            continue

        runs = _simulate_runs(A, D_sqrt, gamma_h2=cfg.GAMMA_H2, theta_z=theta)
        result = run_probe(runs, labels, label=f'THETA_Z={theta}')
        elapsed = time.time() - t0

        var_z = cfg.SIGMA_Z**2 / (2 * theta)
        if verbose:
            print(f'  THETA_Z={theta:.2f} (var(z)={var_z:.2f}): '
                  f'MacroAUROC={result["macro_auroc"]:.4f}, '
                  f'C-AUROC={result["c_auroc"]:.4f}, '
                  f'LR-AUROC={result["lr_auroc"]:.4f}  [{elapsed:.1f}s]')
        results.append(result)

    results.sort(key=lambda r: float(r['label'].split('=')[1].split(' ')[0]))
    return results


# ---------------------------------------------------------------------------
# Axis 4: Positive control
# ---------------------------------------------------------------------------

def run_axis4(A, D_sqrt, labels, verbose=True):
    """Positive control: GAMMA_H2=12.0, THETA_Z=0.01 (combined favorable conditions)."""
    print('\n' + '='*60)
    print('AXIS 4: Positive control (GAMMA_H2=12.0, THETA_Z=0.01)')
    print('='*60)

    t0   = time.time()
    runs = _simulate_runs(A, D_sqrt, gamma_h2=12.0, theta_z=0.01)
    result = run_probe(runs, labels, label='positive_control (GAMMA_H2=12.0, THETA_Z=0.01)')
    elapsed = time.time() - t0

    if verbose:
        print(f'  MacroAUROC={result["macro_auroc"]:.4f}, '
              f'C-AUROC={result["c_auroc"]:.4f}, '
              f'LR-AUROC={result["lr_auroc"]:.4f}  [{elapsed:.1f}s]')

    return [result]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('Phase 8C: Scope map diagnostic analysis')
    print(f'Output directory: {OUT_DIR}')
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load frozen artifacts
    print('\nLoading frozen graph and labels...')
    A, D_sqrt = load_frozen_graph()
    labels    = load_frozen_labels()
    n_C = sum(1 for v in labels.values() if v == 'C')
    n_M = sum(1 for v in labels.values() if v == 'M')
    print(f'  A: {A.shape}, D_sqrt: {D_sqrt.shape}')
    print(f'  Labels: {len(labels)} pairs, n(C)={n_C}, n(M)={n_M}')

    t_total = time.time()

    # Run axes
    axis1 = run_axis1(A, D_sqrt, labels)
    axis2 = run_axis2(A, D_sqrt, labels)
    axis3 = run_axis3(A, D_sqrt, labels)
    axis4 = run_axis4(A, D_sqrt, labels)

    elapsed_total = time.time() - t_total
    print(f'\nAll axes complete in {elapsed_total:.1f}s')

    # Save results
    output = {
        'benchmark': BENCHMARK,
        'axis1_gamma_h2':     axis1,
        'axis2_n_h2_active':  axis2,
        'axis3_theta_z':      axis3,
        'axis4_positive_ctrl': axis4,
    }

    out_path = os.path.join(OUT_DIR, 'scope_map_results.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'\nResults saved to: {out_path}')

    # Print summary tables
    print('\n' + '='*60)
    print('SUMMARY')
    print('='*60)

    def print_axis(name, rows):
        print(f'\n{name}:')
        print(f'  {"Label":<40} {"MacroAUROC":>12} {"C-AUROC":>9} {"LR-AUROC":>10} {"S-AUROC":>9}')
        print(f'  {"-"*40} {"-"*12} {"-"*9} {"-"*10} {"-"*9}')
        for r in rows:
            print(f'  {r["label"]:<40} {r["macro_auroc"]:>12.4f} {r["c_auroc"]:>9.4f} '
                  f'{r["lr_auroc"]:>10.4f} {r["s_auroc"]:>9.4f}')

    print_axis('Axis 1 (GAMMA_H2)', axis1)
    print_axis('Axis 2 (N_H2_ACTIVE)', axis2)
    print_axis('Axis 3 (THETA_Z)', axis3)
    print_axis('Axis 4 (positive control)', axis4)

    return output


if __name__ == '__main__':
    main()
