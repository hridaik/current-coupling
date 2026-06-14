"""
Stage 1: Validate parameters and configuration.
Verifies all 34 parameters load correctly from config.py.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.phase7b import config as cfg


def run():
    print('=' * 60)
    print('STAGE 1: Parameter validation')
    print('=' * 60)

    checks = [
        ('N_OBS',            cfg.N_OBS == 100),
        ('N_H1',             cfg.N_H1 == 32),
        ('N_H2',             cfg.N_H2 == 8),
        ('N_MODULES',        cfg.N_MODULES == 4),
        ('N_PER_MODULE',     cfg.N_PER_MODULE == 25),
        ('N_H1_PER_MODULE',  cfg.N_H1_PER_MODULE == 8),
        ('N_TOTAL',          cfg.N_TOTAL == 140),
        ('P_WITHIN',         abs(cfg.P_WITHIN  - 0.15) < 1e-9),
        ('P_BETWEEN',        abs(cfg.P_BETWEEN - 0.03) < 1e-9),
        ('P_H2_IN',          abs(cfg.P_H2_IN   - 0.20) < 1e-9),
        ('P_H2_OUT',         abs(cfg.P_H2_OUT  - 0.20) < 1e-9),
        ('A_SELF',           abs(cfg.A_SELF + 1.5) < 1e-9),
        ('GAMMA_H2',         abs(cfg.GAMMA_H2 - 3.00) < 1e-9),
        ('DT',               abs(cfg.DT - 0.10) < 1e-9),
        ('T',                cfg.T == 50_000),
        ('T_WARMUP',         cfg.T_WARMUP == 2_000),
        ('T_EFF',            cfg.T_EFF == 48_000),
        ('R',                cfg.R == 5),
        ('MASTER_SEED',      cfg.MASTER_SEED == 42),
        ('SA_size',          len(cfg.SA) == 8),
        ('SA_type_frozenset', isinstance(cfg.SA, frozenset)),
        ('SA_contents',      cfg.SA == frozenset({132,133,134,135,136,137,138,139})),
        ('ALL_H1_size',      len(cfg.ALL_H1) == 32),
        ('H1_H2_disjoint',   len(cfg.ALL_H1 & cfg.SA) == 0),
        ('seeds_present',    all(k in cfg.SEEDS for k in
                                 ['oo_sparsity','h1_sparsity','h2_sparsity',
                                  'oo_weights','h1_weights','h2_weights','D_lr_u'])),
        ('z_seed_run0',      cfg.z_seed(0) == 49),
        ('x_seed_run0',      cfg.x_seed(0) == 60),
        ('z_seed_run4',      cfg.z_seed(4) == 53),
        ('x_seed_run4',      cfg.x_seed(4) == 64),
        ('P1B_bounds_present', all(k in cfg.P1B_BOUNDS for k in ['S','C','M','N'])),
        ('conditions_present', all(c in cfg.CONDITIONS for c in
                                   ['oracle_z','blind_z','neural_state','weak_z','strong_z'])),
        ('MODULE_OBS_M1',    cfg.MODULE_OBS['M1'] == list(range(0, 25))),
        ('MODULE_H1_M1',     cfg.MODULE_H1['M1'] == list(range(100, 108))),
    ]

    n_pass = n_fail = 0
    for name, ok in checks:
        status = 'PASS' if ok else 'FAIL'
        print(f'  {status:4s}  {name}')
        if ok:
            n_pass += 1
        else:
            n_fail += 1

    print()
    print(f'Result: {n_pass}/{n_pass+n_fail} checks passed')
    if n_fail:
        print('STAGE 1 FAILED')
        sys.exit(1)
    print('STAGE 1 PASSED')


if __name__ == '__main__':
    run()
