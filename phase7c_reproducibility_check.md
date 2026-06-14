# Phase 7C Reproducibility Check
**Check completed:** 2026-06-13  
**Status:** PASSED — exact reproducibility confirmed

This document records an exact regeneration of the canonical dataset from the same seeds and locked artifacts. This is a provenance check only. No scientific metrics were computed.

---

## Methodology

1. Started from the same code commit (`b6117b238f510109f3b964d07c60bd9b2c6d3ddc`)
2. Loaded the identical locked artifacts (`A_sparse.npy`, `labels.json`)
3. Called `check_all_acceptance_tests_passed()` — gate confirmed PASSED
4. Called `verify_label_hash(checkpoint='V2-regen')` — hash confirmed unchanged
5. Re-ran `simulate_run()` for all 5 conditions × 5 runs with identical seeds
6. Saved regenerated files to `results/phase7c/regeneration/data/`
7. Compared SHA-256 hashes at array level (definitive) and file level
8. Compared SHA-256 of `labels.json` and `A_sparse.npy` against canonical records

Script: `scripts/phase7c/regeneration_check.py`  
Duration: 93.5 seconds

---

## Seed Policy Verification

The seed policy `z_seed(r) = 49+r`, `x_seed(r) = 60+r` produces deterministic output from `numpy.random.default_rng` (PCG64). Determinism was verified by comparing file-level SHA-256 hashes between the canonical and regenerated files.

All 25 regenerated files match at the file level (identical compressed bytes, not just array values), confirming:
- No hidden nondeterminism in the RNG stream
- No platform-dependent floating-point behavior affecting these arrays
- numpy compression of float64 arrays is stable across runs on this platform

---

## Trajectory Hash Comparison

**25/25 PASSED — all file-exact and array-exact matches**

| File | Canonical SHA-256 | Regen SHA-256 | Match |
|------|-------------------|---------------|-------|
| oracle_z_run0.npz | `e4f95b906ebd38a6…` | `e4f95b906ebd38a6…` | ✓ |
| oracle_z_run1.npz | `bedba77c018378b2…` | `bedba77c018378b2…` | ✓ |
| oracle_z_run2.npz | `8b3055df87210c29…` | `8b3055df87210c29…` | ✓ |
| oracle_z_run3.npz | `d607a0fdc5942180…` | `d607a0fdc5942180…` | ✓ |
| oracle_z_run4.npz | `5f8fa7980c53ddfe…` | `5f8fa7980c53ddfe…` | ✓ |
| blind_z_run0.npz | `8137066611ccf818…` | `8137066611ccf818…` | ✓ |
| blind_z_run1.npz | `f88d4d8ecb1487e9…` | `f88d4d8ecb1487e9…` | ✓ |
| blind_z_run2.npz | `2c75b6ee403e5fdc…` | `2c75b6ee403e5fdc…` | ✓ |
| blind_z_run3.npz | `25e76e1493457965…` | `25e76e1493457965…` | ✓ |
| blind_z_run4.npz | `3b84c4fda4c14c72…` | `3b84c4fda4c14c72…` | ✓ |
| neural_state_run0.npz | `bda37ca450db8c63…` | `bda37ca450db8c63…` | ✓ |
| neural_state_run1.npz | `ee6cb16d27ae5ed0…` | `ee6cb16d27ae5ed0…` | ✓ |
| neural_state_run2.npz | `ed3cee06f766d240…` | `ed3cee06f766d240…` | ✓ |
| neural_state_run3.npz | `8b21bfde4ab1d3aa…` | `8b21bfde4ab1d3aa…` | ✓ |
| neural_state_run4.npz | `a0cae7e462da4904…` | `a0cae7e462da4904…` | ✓ |
| weak_z_run0.npz | `e7bfdb8e0214a365…` | `e7bfdb8e0214a365…` | ✓ |
| weak_z_run1.npz | `6924c836ceba58c7…` | `6924c836ceba58c7…` | ✓ |
| weak_z_run2.npz | `32fb419985795d92…` | `32fb419985795d92…` | ✓ |
| weak_z_run3.npz | `495b9141857cd225…` | `495b9141857cd225…` | ✓ |
| weak_z_run4.npz | `111e91292bbe9c1f…` | `111e91292bbe9c1f…` | ✓ |
| strong_z_run0.npz | `95be75393f9b9eb6…` | `95be75393f9b9eb6…` | ✓ |
| strong_z_run1.npz | `304ffa368010ff15…` | `304ffa368010ff15…` | ✓ |
| strong_z_run2.npz | `9008a27235625379…` | `9008a27235625379…` | ✓ |
| strong_z_run3.npz | `91b8a3b6326fe80d…` | `91b8a3b6326fe80d…` | ✓ |
| strong_z_run4.npz | `e42b8316de831b85…` | `e42b8316de831b85…` | ✓ |

---

## Label Hash Verification

| Artifact | Canonical hash | Current hash | Match |
|----------|----------------|--------------|-------|
| `labels.json` | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` | ✓ |

`labels.json` has not been modified since Phase 7B Stage 4 commit. The SAREACHABLE-based labels are stable.

---

## Metadata Hash Verification

| Artifact | Canonical hash | Match |
|----------|----------------|-------|
| `A_sparse.npy` | `4e02d897f6d0f6aef2a1edff077abb1d3f878618a39c5b09e1f3d108e10f291b` | ✓ |
| `construction_params.json` | `41337b50724594ca0f70eb262c992feefb7e5d8398d0f309bfd02dab04afe455` | ✓ |
| `metadata.json` | `2cfe4015ba1893f16dbbe063e13768ce0953a4a623c1c62ee1fe70a452044326` | ✓ |

---

## Hidden Nondeterminism Check

**No hidden nondeterminism detected.**

Evidence:
1. All 25 files match at file level (byte-identical compressed output), not just at array level. This rules out nondeterminism in the compression step.
2. The OU process for z and the SDE for x both use `numpy.random.default_rng` with fixed seeds; no time-based or OS-level entropy is consumed during simulation.
3. The observation model (softplus → calcium filter → Gaussian noise) draws from `rng_x`, which is fully seeded.
4. The eigenvalue computation (CK-G4, spectral abscissa) is deterministic for a fixed A matrix.
5. All numpy operations (matrix multiply, elementwise) are deterministic for fixed inputs on this platform.

---

## Conclusion

The benchmark dataset is exactly reproducible from:
- commit `b6117b238f510109f3b964d07c60bd9b2c6d3ddc`
- locked artifacts in `ground_truth/`
- seed policy documented in `phase7c_run_manifest.md`

No scientific parameters, labels, or topology were modified between the canonical run and the regeneration check. The dataset is frozen and the canonical fingerprint is:

```
hashes.json meta-hash: 7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed
```
