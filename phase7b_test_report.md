# Phase 7B Test Report
**Date:** 2026-06-13  
**Branch:** main  
**Spec authority:** phase6b_architecture_spec.md, phase6b_label_generation_spec.md, phase6b_parameter_registry.md, phase7a_construction_checks.md, phase7a_acceptance_tests.md, phase7a_invariants.md  

---

## Outcome

**ALL STAGES PASSED. SIMULATION GATE UNLOCKED.**

All 22 construction checks, 8 invariant checks, and 4 acceptance tests passed on first-seed realization (zero resampling required). Implementation faithfully realizes the Phase 6B specification.

---

## Stage 1 — Parameter Validation

**Result: 33/33 PASS**

All 34 registered parameters (P01–P34) loaded correctly from `config.py`. Key verified values:

| Parameter | Expected | Observed |
|-----------|----------|----------|
| N_TOTAL | 140 | 140 |
| SA | frozenset({132..139}) | frozenset({132..139}) |
| GAMMA_H2 | 3.00 | 3.00 |
| A_SELF | -1.5 | -1.5 |
| DT | 0.10 | 0.10 |
| T / T_WARMUP / T_EFF | 50000/2000/48000 | 50000/2000/48000 |
| R | 5 | 5 |
| MASTER_SEED | 42 | 42 |
| z_seed(0) | 49 | 49 |
| x_seed(0) | 60 | 60 |

SA type confirmed `frozenset`. ALL_H1 and SA confirmed disjoint.

---

## Stage 2 — Graph Construction + CK-G*

**Result: 20/20 PASS (12 graph checks + 8 invariant checks)**

### Graph summary
- Shape: (140, 140) ✓  
- Spectral abscissa: **−0.5390** (threshold < −0.1) ✓  
- Resample attempts: **0** (original weight draw was stable)  
- Realized p_within: 0.1537 (nominal 0.15, within 4-sigma bounds [0.1233, 0.1779]) ✓  
- Realized p_between: 0.0289 (nominal 0.03, within 4-sigma bounds [0.0229, 0.0376]) ✓  

### CK-G* results

| Check | Description | Result |
|-------|-------------|--------|
| CK-G1 | A.shape == (140,140) | PASS |
| CK-G2 | Diagonal = −1.5 everywhere | PASS |
| CK-G3 | A_dynamics == A_sparse (no A_lr) | PASS |
| CK-G4 | Spectral abscissa < −0.1 | PASS (−0.5390) |
| CK-G5 | All 140 indices covered, no overlaps | PASS |
| CK-G6 | H2_TARGETS matches spec | PASS |
| CK-G7 | No H2→H2 off-diagonal edges | PASS |
| CK-G8 | No H1↔H2 edges | PASS |
| CK-G9 | No H1→H1 edges | PASS |
| CK-G10 | H1 neurons only connect within their module | PASS |
| CK-G11 | H2 neurons only connect within target modules | PASS |
| CK-G12 | Sparsity rates within 4-sigma of nominal (soft) | PASS |

### Invariant checks at construction time

| Invariant | Description | Result |
|-----------|-------------|--------|
| INV-A3 | Spectral abscissa < −0.1 | PASS |
| INV-A4 | A_lr = 0 (no deviation from A_sparse) | PASS |
| INV-A5 | Diagonal = −1.5 | PASS |
| INV-B2 | B(z) = γ_H2·z for H2, 0 elsewhere | PASS |
| INV-B4 | SA is frozenset (immutable) | PASS |
| INV-C1 | D is state-independent | PASS |
| INV-C2 | D is positive definite (min eigenvalue = 1.0) | PASS |
| INV-C3 | D_lr is rank-1, ‖u‖ = 1 | PASS |

### Bugs found and fixed during Stage 2
1. **CK-G5 key collision**: `{**MODULE_OBS, **MODULE_H1}` silently overwrites obs entries (both use keys M1–M4). Fixed: namespace keys as `obs_M1`, `h1_M1`, etc.  
2. **CK-G7 self-inhibition false positive**: check flagged diagonal entries (−1.5) as H2→H2 edges. Fixed: skip `src == dst` pairs.

---

## Stage 3 — Label Generation + CK-L* / CK-H*

**Result: 11/11 PASS**

### Realized class counts

| Class | Count | P1-B Bounds | Status |
|-------|-------|-------------|--------|
| S | 498 | [400, 700] | ✓ |
| C | 855 | [450, 950] | ✓ |
| M | 88 | [5, 200] | ✓ |
| N | 8459 | [7000, 9000] | ✓ |

Note: Expected counts from Phase 6B spec were S≈518, C≈691, M≈67, N≈8624. Actual S and N are within expected range; C is higher (855 vs 691) and M is higher (88 vs 67). All within P1-B bounds — these are stochastic realizations.

### CK-L* results

| Check | Description | Result |
|-------|-------------|--------|
| CK-L1 | Exactly 9900 pairs | PASS |
| CK-L2 | All valid (i,j) pairs covered | PASS |
| CK-L3 | All labels in {S,C,M,N} | PASS |
| CK-L4 | Counts sum to 9900, all 4 classes populated | PASS |
| CK-L5 | DIRECT consistent with A_sparse[j,i] != 0 | PASS |
| CK-L6 | SAREACHABLE consistent with path i→h→j via SA | PASS |
| CK-L7 | witness_h2 is lowest-index valid witness | PASS |

### CK-H* results

| Check | Description | Result |
|-------|-------------|--------|
| CK-H1 | All 6 module pairs covered by ≥1 H2 | PASS |
| CK-H2 | Exact H2 counts per module pair | PASS |
| CK-H3 | Each module targeted by exactly 4 H2 neurons | PASS |
| CK-H4 | Each H2 targets exactly 2 modules | PASS |

---

## Stage 4 — Hash-Lock Commit (Checkpoint V1)

**Result: PASS**

- Label hash (SHA-256): `8bef9d4e2122911ee8b63f9db72b812f5f17babfec8a963c4f0427d75230ac68`
- Files written: `ground_truth/labels.json`, `ground_truth/labels.sha256`, `ground_truth/A_sparse.npy`, `ground_truth/A_sparse.sha256`, `ground_truth/construction_params.json`
- `labels.json` set to read-only (chmod 444) ✓
- Checkpoint V1 hash verification: PASS (computed hash matches stored hash)
- Audit log initialized: `ground_truth/audit_log.jsonl`

---

## Stage 5 — Dynamics Unit Tests

**Result: 17/17 PASS**

| Test | Result |
|------|--------|
| softplus(0) ≈ log(2) | PASS |
| softplus(−100) ≈ 0 | PASS |
| softplus(100) ≈ 100 | PASS |
| B(h∈SA, z=2) = γ_H2·2 | PASS |
| B(k∉SA) = 0 | PASS |
| step_z: high θ pulls z toward 0 | PASS |
| OU stationary variance ≈ σ²/(2θ) = 5.00 (got 5.05, <10% error) | PASS |
| step_x returns shape (140,) | PASS |
| step_x: finite output | PASS |
| simulate_run y shape (90, 100) | PASS |
| simulate_run z_oracle shape (90,) | PASS |
| simulate_run y finite | PASS |
| simulate_run y ≥ −5 (calcium-like) | PASS |
| observe returns correct shapes | PASS |
| calcium filter: ca_new < softplus(x_obs) | PASS |
| Runs 0 and 1 differ | PASS |
| Run 0 is reproducible (same seeds → same output) | PASS |

### Bug found and fixed during Stage 5
**step_z stability test**: original test used θ=1e9, dt=0.1, z=5 — Euler-Maruyama is numerically unstable at θ·dt=1e8 (drift = −5×10⁸). Test was conceptually correct (high mean-reversion → collapse) but EM cannot realize it at that step size. Fixed: use θ=10 (θ·dt=1.0, boundary of EM stability), verify |z_next| < |z| (correct directional pull).

---

## Stage 6 — Acceptance Tests P1-A through P1-D

**Result: 4/4 PASS — SIMULATION GATE UNLOCKED**

### Checkpoint V2
Hash re-verified before metrics: **PASS** (no modification since V1).

### P1-A: Near-zero H2 path strength

- C pairs: 855
- Weak pairs (max path strength < 0.01): 223
- Weak fraction: **0.2608**
- Threshold: ≤ 0.30
- Min path strength: see audit log
- **Result: PASS** (26.1% weak, below 30% limit)

### P1-B: Class count bounds

| Class | Count | Bounds [lo, hi] | Status |
|-------|-------|-----------------|--------|
| S | 498 | [400, 700] | PASS |
| C | 855 | [450, 950] | PASS |
| M | 88 | [5, 200] | PASS |
| N | 8459 | [7000, 9000] | PASS |

**Result: PASS**

### P1-C: Label reproducibility

- Re-generated labels from A_sparse from scratch
- Mismatches vs committed: **0**
- **Result: PASS** (construction-only labels are deterministic)

### P1-D: Hash system integrity

| Sub-test | Description | Result |
|----------|-------------|--------|
| P1-D-1 | Deterministic: hash(labels) == hash(labels) | PASS |
| P1-D-2 | Disk match: computed hash matches labels.sha256 | PASS |
| P1-D-3 | Tamper detection: mutating a label changes hash | PASS |
| P1-D-4-format | Canonical JSON: no newlines, no indentation | PASS |
| P1-D-4-roundtrip | Parse and re-serialize → same hash | PASS |

**Result: PASS**

### Gate function
`check_all_acceptance_tests_passed()` confirmed all 4 tests in audit log with PASS status. **Gate cleared.**

---

## Deviations from Specification

None. All deviations were pre-registered in `phase6b_pre_registration.md`:
- No A_lr (confirmed by CK-G3, INV-A4)
- Scalar z (confirmed by DIM_Z=1 in config)
- No gain modulation (confirmed by INV-B2: B(z) = γ_H2·z, linear)
- D constant (confirmed by INV-C1)
- z via B(z) only (confirmed by INV-B1 design)

---

## Forbidden Actions — Confirmed Not Taken

- [ ] Parameters tuned after seeing A_sparse — NO (all parameters frozen in config.py before any code ran)
- [ ] Labels altered after generation — NO (labels.json set read-only immediately after commit)
- [ ] Classification performance inspected — NO (no framework evaluation in any stage)
- [ ] H2 topology altered after graph generation — NO (SA and H2_TARGETS are frozensets)
- [ ] Acceptance thresholds weakened — NO (thresholds match phase7a_acceptance_tests.md exactly)
- [ ] Simulation run before gate cleared — NO (gate function enforced; no simulate_all_runs called)

---

## File Inventory

```
scripts/phase7b/
  __init__.py          — package init
  config.py            — all 34 parameters (P01-P34)
  graph.py             — build_A_sparse(), build_D(), compute_B()
  labels.py            — generate_labels(), SAREACHABLE algorithm
  audit.py             — hash-lock, commit_labels(), verify_label_hash(), log_event()
  checks.py            — 22 construction checks + invariant checks
  dynamics.py          — Euler-Maruyama integrator, simulate_run()
  acceptance.py        — P1-A/B/C/D, check_all_acceptance_tests_passed()
  run_stage1.py        — parameter validation
  run_stage2.py        — graph construction + CK-G*
  run_stage3.py        — label generation + CK-L*/CK-H*
  run_stage4.py        — hash-lock commit + V1
  run_stage5.py        — dynamics unit tests
  run_stage6.py        — acceptance tests P1-A through P1-D
  run_all_stages.py    — master runner

ground_truth/
  labels.json          — committed ground-truth labels (read-only)
  labels.sha256        — SHA-256 hash of labels.json
  A_sparse.npy         — committed coupling matrix
  A_sparse.sha256      — SHA-256 hash of A_sparse.npy
  construction_params.json  — frozen parameter snapshot
  construction_params.sha256
  audit_log.jsonl      — full audit trail
  _stage2_A.npy        — intermediate: A for downstream stages
  _stage2_D_sqrt.npy   — intermediate: Cholesky factor of D
  _stage2_u.npy        — intermediate: low-rank noise direction
  _stage3_records.json — intermediate: label records before commit
```

---

## Status

Phase 7B is complete. The reference implementation is ready. Simulation (Phase 7C or equivalent) may proceed by calling `check_all_acceptance_tests_passed()` as the first line of any simulation function, then calling `simulate_all_runs()` with the desired evaluation condition.

The implementation is a faithful realization of the Phase 6B specification. No scientific decisions were made during implementation. The ground truth is locked and auditable.
