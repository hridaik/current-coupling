# Phase 7C Run Manifest
**Status:** CANONICAL — sealed 2026-06-13T10:19:04Z

This manifest is sufficient for an independent third party to reproduce the exact canonical dataset.

---

## Code Version

| Field | Value |
|-------|-------|
| Repository | `/home/hridai/code/worm-phase0` |
| Commit hash | `b6117b238f510109f3b964d07c60bd9b2c6d3ddc` |
| Branch | `main` |
| Generation timestamp | 2026-06-13T10:17:08Z – 10:18:24Z (76.0 s) |
| Freeze timestamp | 2026-06-13T10:19:04Z |
| Host OS | Linux 6.18.33.1-microsoft-standard-WSL2 |
| Python | `.venv/bin/python` (project virtual environment) |
| numpy | installed in `.venv` |

---

## Simulator Version

| Field | Value |
|-------|-------|
| Module | `scripts/phase7b/dynamics.py` |
| Entry point | `simulate_run(run_index, A, D_sqrt, B_fn, ...)` |
| Spec authority | `phase6b_architecture_spec.md` |
| Implementation spec | `phase7b_implementation_map.md` |
| Acceptance gate | `scripts/phase7b/acceptance.py::check_all_acceptance_tests_passed()` |
| Gate status at generation | PASSED (all P1-A through P1-D) |

---

## Parameter Registry Version

| Field | Value |
|-------|-------|
| Registry file | `scripts/phase7b/config.py` |
| Spec authority | `phase6b_parameter_registry.md` (P01–P34, 34 parameters) |
| Registry hash | SHA-256 of `construction_params.json`: `41337b50724594ca0f70eb262c992feefb7e5d8398d0f309bfd02dab04afe455` |

### Key Scientific Parameters

| ID | Name | Value |
|----|------|-------|
| P01 | N_OBS | 100 |
| P02 | N_H1 | 32 |
| P03 | N_H2 | 8 |
| P17 | A_SELF | −1.5 |
| P19 | THETA_Z | 0.10 |
| P20 | SIGMA_Z | 1.00 |
| P21 | GAMMA_H2 | 3.00 (nominal; overridden per condition) |
| P24 | D_0 | 1.00 |
| P25 | EPS_LR | 0.10 |
| P27 | KAPPA_CA | 0.50 |
| P28 | SIGMA_OBS_NOISE | 0.10 |
| P29 | NONLINEARITY | softplus |
| P30 | DT | 0.10 |
| P31 | T | 50,000 steps |
| P32 | T_WARMUP | 2,000 steps |
| P34 | MASTER_SEED | 42 |

---

## Label Specification Version

| Field | Value |
|-------|-------|
| Spec file | `phase6b_label_generation_spec.md` |
| Implementation | `scripts/phase7b/labels.py::generate_labels()` |
| Definition | SAREACHABLE(i→j) = ∃ h ∈ SA: A[h,i]≠0 ∧ A[j,h]≠0 |
| Committed label hash (SHA-256) | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` |
| Label file | `ground_truth/labels.json` (read-only, chmod 444) |
| Class counts | S=497, C=857, M=89, N=8457 |

---

## Random Seed Policy

Seeds are fixed by the sub-seed table in `phase6b_architecture_spec.md §2.9`.

| Component | Seed formula | Purpose |
|-----------|-------------|---------|
| oo_sparsity | 42 | Obs-obs edge pattern |
| h1_sparsity | 43 | H1 edge pattern |
| h2_sparsity | 44 | H2 edge pattern |
| oo_weights | 45 | Obs-obs coupling weights |
| h1_weights | 46 | H1 coupling weights |
| h2_weights | 47 | H2 coupling weights |
| D_lr_u | 48 | Low-rank noise direction |
| z process | 49 + run_index | OU latent state per run |
| x/obs process | 60 + run_index | Neural SDE + observation noise per run |

Run indices: 0, 1, 2, 3, 4 (R=5 independent runs per condition).

All RNGs use `numpy.random.default_rng(seed)` (PCG64 algorithm).

Observation noise shares the x-process RNG (`rng_x = default_rng(60 + run_index)`).

---

## Number of Trajectories

| Condition | R | Runs |
|-----------|---|------|
| oracle_z | 5 | run0–run4 |
| blind_z | 5 | run0–run4 |
| neural_state | 5 | run0–run4 |
| weak_z | 5 | run0–run4 |
| strong_z | 5 | run0–run4 |
| **Total** | **25** | |

---

## Trajectory Lengths

| Quantity | Value |
|----------|-------|
| Total integration steps (T) | 50,000 |
| Warm-up steps discarded (T_WARMUP) | 2,000 |
| Effective steps per run (T_EFF) | 48,000 |
| Time step (DT) | 0.10 |
| Effective time span | 4,800 time units |

---

## Evaluation Conditions

| Condition | gamma_H2 | provide_z | use_obs_model | Description |
|-----------|----------|-----------|---------------|-------------|
| oracle_z | 3.00 | True | True | Canonical: framework receives y(t) and true z(t) |
| blind_z | 3.00 | False | True | Framework receives y(t) only |
| neural_state | 3.00 | True | False | Raw softplus(x_obs), not calcium-filtered |
| weak_z | 1.50 | True | True | Attenuated H2 drive |
| strong_z | 6.00 | True | True | Amplified H2 drive |

---

## Observation Model

Applied to all conditions with `use_obs_model=True`:

1. **Nonlinearity**: r(t) = softplus(x_obs(t)) = log(1 + exp(x_obs(t)))
2. **Calcium filter**: ca(t) = (1 − κ·dt)·ca(t−1) + κ·dt·r(t), κ=0.50, dt=0.10
3. **Observation noise**: y(t) = ca(t) + ε(t), ε ~ N(0, 0.10²)

For `neural_state` condition: y(t) = softplus(x_obs(t)) only (no calcium filter or noise).

---

## Saved Artifact Paths

```
results/phase7c/canonical/
  data/
    oracle_z_run{0..4}.npz      — arrays: y (48000×100), z_oracle (48000,)
    blind_z_run{0..4}.npz       — arrays: y (48000×100) only
    neural_state_run{0..4}.npz  — arrays: y (48000×100), z_oracle (48000,)
    weak_z_run{0..4}.npz        — arrays: y (48000×100), z_oracle (48000,)
    strong_z_run{0..4}.npz      — arrays: y (48000×100), z_oracle (48000,)
  metadata.json                 — full run metadata (read-only)
  hashes.json                   — SHA-256 for all 32 artifacts (read-only)

ground_truth/
  labels.json                   — committed ground-truth labels (read-only)
  labels.sha256                 — label hash file
  A_sparse.npy                  — coupling matrix (read-only)
  A_sparse.sha256               — A_sparse hash file
  construction_params.json      — frozen parameter snapshot
  audit_log.jsonl               — complete audit trail
```

All data files are chmod 444 (read-only). The framework receives only `y` arrays (and `z_oracle` in oracle-z conditions). It never receives `A_sparse`, `labels.json`, or H2 topology.

---

## Timestamp Window

| Event | Timestamp (UTC) |
|-------|----------------|
| Acceptance gate cleared | 2026-06-13 (Phase 7B) |
| Label commit (V1 checkpoint) | 2026-06-13 |
| Generation started | 2026-06-13T10:17:08Z |
| Generation completed | 2026-06-13T10:18:24Z |
| Dataset frozen | 2026-06-13T10:19:04Z |
| Regeneration check completed | 2026-06-13 |

---

## Reproduction Instructions

To reproduce the exact canonical dataset from scratch:

```bash
# 1. Restore the same commit
git checkout b6117b238f510109f3b964d07c60bd9b2c6d3ddc

# 2. Activate the project virtual environment
source .venv/bin/activate

# 3. Run Phase 7B to rebuild locked artifacts
python scripts/phase7b/run_all_stages.py

# 4. Regenerate the dataset
python scripts/phase7c/generate_dataset.py

# 5. Hash and compare (do not freeze a second time)
python scripts/phase7c/regeneration_check.py
```

The regeneration check compares array-level SHA-256 hashes (not file-level, since npz
compression metadata may vary by numpy version). All 25 trajectory files and 2 locked
artifacts must produce matching array hashes.
