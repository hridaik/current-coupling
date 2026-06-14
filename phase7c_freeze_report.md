# Phase 7C Freeze Report
**Frozen:** 2026-06-13T10:19:04Z  
**Status:** SEALED

---

## Summary

The canonical dataset was generated exactly once, sealed immediately after generation, and verified for hash integrity. No post-generation edits occurred. No evaluation outputs influenced the dataset.

---

## Canonical Generation: Exactly Once

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Generation script executed once | CONFIRMED | Single run of `scripts/phase7c/generate_dataset.py` at 2026-06-13T10:17:08Z–10:18:24Z |
| No re-run to improve class balance | CONFIRMED | Class counts are determined entirely by locked A_sparse and locked label algorithm; generation has no class-balance feedback loop |
| No re-run to improve output appearance | CONFIRMED | No inspection of trajectory statistics prior to or during generation |
| Acceptance gate passed before generation | CONFIRMED | `check_all_acceptance_tests_passed()` is the first line of `generate_dataset.py`; gate was PASSED |
| Label hash verified (V2) before generation | CONFIRMED | `verify_label_hash(checkpoint='V2')` called; hash `dc99697e…` matched |

---

## Canonical Hash Recorded

| Artifact | Hash |
|----------|------|
| `hashes.json` meta-hash | `7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed` |
| `labels.json` | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` |
| `A_sparse.npy` | `4e02d897f6d0f6aef2a1edff077abb1d3f878618a39c5b09e1f3d108e10f291b` |
| `metadata.json` | `2cfe4015ba1893f16dbbe063e13768ce0953a4a623c1c62ee1fe70a452044326` |

All 32 artifact hashes are recorded in `results/phase7c/canonical/hashes.json`.

---

## Dataset Sealed

| Criterion | Status | Evidence |
|-----------|--------|---------|
| All trajectory files read-only | CONFIRMED | chmod 444 applied to 25 `.npz` files at freeze time |
| `metadata.json` read-only | CONFIRMED | chmod 444 |
| `hashes.json` read-only | CONFIRMED | chmod 444 |
| `labels.json` read-only | CONFIRMED | chmod 444 (set in Phase 7B Stage 4) |
| Freeze logged in audit trail | CONFIRMED | `phase7c_dataset_frozen` event in `audit_log.jsonl` |

---

## No Post-Generation Edits

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Trajectory files modified after freeze | NOT OCCURRED | Files are chmod 444; any write attempt would raise PermissionError |
| Labels modified after freeze | NOT OCCURRED | `labels.json` has been chmod 444 since Phase 7B Stage 4 (pre-generation) |
| A_sparse modified | NOT OCCURRED | Loaded from `A_sparse.npy`; same hash at freeze and regeneration check |
| Parameters modified post-generation | NOT OCCURRED | config.py is not frozen at filesystem level, but all parameters are logged in committed `construction_params.json` (hash: `41337b50…`) |

---

## No Evaluation Influenced the Dataset

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Framework evaluation run | NOT OCCURRED | No framework module imported or invoked in any Phase 7C script |
| Classification metrics computed | NOT OCCURRED | No call to any metric function on benchmark output |
| Scientific parameters tuned based on output | NOT OCCURRED | No parameter was modified after observing any trajectory |
| H2 topology altered | NOT OCCURRED | SA = frozenset({132..139}) fixed in config.py; H2_TARGETS unchanged |
| Diffusion altered | NOT OCCURRED | D_0=1.00, EPS_LR=0.10, D_STATE_DEPENDENT=False; unchanged |
| Observation settings altered | NOT OCCURRED | KAPPA_CA=0.50, SIGMA_OBS_NOISE=0.10, NONLINEARITY='softplus'; unchanged |
| Labels altered after generation | NOT OCCURRED | labels.json was read-only before generation began |

---

## Deviations

None.

All pre-registered deviations from Phase 6A protocol were documented in `phase6b_pre_registration.md` before implementation and are carried forward without additional modification:

1. No A_lr component (INV-A4 confirmed)
2. Scalar z (DIM_Z=1)
3. No gain modulation (B is linear in z)
4. D is state-independent (INV-C1 confirmed)
5. z enters only through B(z) (INV-B1 by design)

No new deviations arose during Phase 7C.

---

## Protocol Compliance Checklist

- [x] Canonical dataset generated exactly once
- [x] Acceptance gate passed before generation
- [x] Label hash verified (V2 checkpoint) before generation
- [x] Canonical hash recorded for every artifact
- [x] Dataset sealed (read-only) immediately after generation
- [x] No post-generation edits
- [x] No evaluation outputs influenced the dataset
- [x] Exact regeneration check passed (25/25)
- [x] Audit trail complete
- [x] Phase 7C STOPPED here — no framework evaluation follows from this phase
