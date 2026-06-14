# Phase 7C Dataset Provenance
**Frozen:** 2026-06-13T10:19:04Z  
**hashes.json meta-hash:** `7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed`

This document records the complete provenance chain for every artifact in the canonical benchmark corpus.

---

## Dependency Chain

```
phase6b_parameter_registry.md (spec authority)
    └─► config.py (P01-P34)
            └─► graph.py → A_sparse.npy [locked, hash committed]
            └─► labels.py → labels.json [locked, hash committed]
            └─► dynamics.py → simulate_run()
                    └─► oracle_z_run{0..4}.npz
                    └─► blind_z_run{0..4}.npz
                    └─► neural_state_run{0..4}.npz
                    └─► weak_z_run{0..4}.npz
                    └─► strong_z_run{0..4}.npz
                            └─► metadata.json
                                    └─► hashes.json  ← freeze point
```

Labels and A_sparse were committed and hash-locked in Phase 7B before any simulation.
Trajectory files were generated from the locked artifacts without modification.

---

## Locked Ground-Truth Artifacts (Phase 7B)

These artifacts were committed before simulation and must not change.

| File | SHA-256 | Size | Source Stage | Notes |
|------|---------|------|-------------|-------|
| `ground_truth/labels.json` | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` | 719,989 B | Phase 7B Stage 3-4 | Read-only (chmod 444). 9,900 label records. |
| `ground_truth/labels.sha256` | `e38a9687dc17efa5cb541be23f631217a8bacbfc0ae3ec40aa3fb783676a4ec6` | 78 B | Phase 7B Stage 4 | Hash file written at V1 checkpoint. |
| `ground_truth/A_sparse.npy` | `4e02d897f6d0f6aef2a1edff077abb1d3f878618a39c5b09e1f3d108e10f291b` | 156,928 B | Phase 7B Stage 2 | 140×140 float64 coupling matrix. |
| `ground_truth/A_sparse.sha256` | `0930817b6f58d00b7a9035b7e954a2e2b5b8c1eef3cdf7cc2810d977daeb3b1c` | 79 B | Phase 7B Stage 2 | |
| `ground_truth/construction_params.json` | `41337b50724594ca0f70eb262c992feefb7e5d8398d0f309bfd02dab04afe455` | 480 B | Phase 7B Stage 4 | Frozen parameter snapshot. |

**Verification:** `verify_label_hash(checkpoint='V2')` was called immediately before simulation, confirming `labels.json` was unmodified since Phase 7B commit.

---

## Observed Trajectory Artifacts

Format: numpy `.npz` (compressed), float64.  
All files are chmod 444 (read-only) since 2026-06-13T10:19:04Z.  
Arrays: `y` shape (48000, 100); `z_oracle` shape (48000,) if applicable.

### Condition: oracle_z (gamma_H2=3.00, provide_z=True, use_obs_model=True)

| File | SHA-256 | Size | y shape | z shape |
|------|---------|------|---------|---------|
| `oracle_z_run0.npz` | `e4f95b906ebd38a6c389549abfce5625142b6b070a463b776584dbd54184389f` | 36,683,218 B | (48000,100) | (48000,) |
| `oracle_z_run1.npz` | `bedba77c018378b245845540c0fe8a4da8c887a67417574f0b1b28a42fa89033` | 36,692,402 B | (48000,100) | (48000,) |
| `oracle_z_run2.npz` | `8b3055df87210c29a1bcffc2bbb8820819b820a69ddf461eb29b947daaf53984` | 36,705,060 B | (48000,100) | (48000,) |
| `oracle_z_run3.npz` | `d607a0fdc594218026958b40dfe57cc1326aef6145ec1c6a9ae1cf09fe88f7e5` | 36,699,302 B | (48000,100) | (48000,) |
| `oracle_z_run4.npz` | `5f8fa7980c53ddfe4a4d70ab66415542bd9767d8578920cb806bdacd2b4e7012` | 36,718,944 B | (48000,100) | (48000,) |

Seeds: z_seed = 49+r, x_seed = 60+r, r ∈ {0,1,2,3,4}

### Condition: blind_z (gamma_H2=3.00, provide_z=False, use_obs_model=True)

| File | SHA-256 | Size | y shape | z shape |
|------|---------|------|---------|---------|
| `blind_z_run0.npz` | `8137066611ccf81868c86643f943ee84ded8dbba31e8254aafb7c96697fc57fd` | 36,311,252 B | (48000,100) | — |
| `blind_z_run1.npz` | `f88d4d8ecb1487e9fb56b694d76bb8df71ada12bcffbe3202e6b5f180830e5b1` | 36,320,322 B | (48000,100) | — |
| `blind_z_run2.npz` | `2c75b6ee403e5fdc5146098983a0853a5dc0dc8528ea524989bd63a977c9694f` | 36,333,040 B | (48000,100) | — |
| `blind_z_run3.npz` | `25e76e1493457965c8bb96600cf028eb5814368df78090ac86f47f2661779dbc` | 36,327,151 B | (48000,100) | — |
| `blind_z_run4.npz` | `3b84c4fda4c14c72b6b56bd2d9f70005110a1db72bd64d337a0c0b1f8512b268` | 36,346,751 B | (48000,100) | — |

Note: blind_z uses identical seeds and dynamics to oracle_z. z is computed internally but not saved. The y arrays from blind_z therefore equal those from oracle_z, since y depends only on x and ca — not on the provide_z flag. This is correct per spec: the framework's z access is gated by condition, not by the simulation.

### Condition: neural_state (gamma_H2=3.00, provide_z=True, use_obs_model=False)

| File | SHA-256 | Size | y shape | z shape |
|------|---------|------|---------|---------|
| `neural_state_run0.npz` | `bda37ca450db8c63797d2056199cc2466c92c5052154009f82c0061bf79339d5` | 36,760,670 B | (48000,100) | (48000,) |
| `neural_state_run1.npz` | `ee6cb16d27ae5ed06253c1e6ca07785155fe785c154d86dca0e3048a00061c7a` | 36,766,178 B | (48000,100) | (48000,) |
| `neural_state_run2.npz` | `ed3cee06f766d2408a0a30cb977378d2d08b595ab2db1f605115442cee8e4976` | 36,772,948 B | (48000,100) | (48000,) |
| `neural_state_run3.npz` | `8b21bfde4ab1d3aa3438901a5feb42b634a86fdaab127f1c36af12a1f1c68485` | 36,769,826 B | (48000,100) | (48000,) |
| `neural_state_run4.npz` | `a0cae7e462da490420338a184a41b369f6d37b5b2d27fc0a0385e8a577f94721` | 36,781,832 B | (48000,100) | (48000,) |

y values are softplus(x_obs(t)) directly; no calcium filter, no additive noise.

### Condition: weak_z (gamma_H2=1.50, provide_z=True, use_obs_model=True)

| File | SHA-256 | Size | y shape | z shape |
|------|---------|------|---------|---------|
| `weak_z_run0.npz` | `e7bfdb8e0214a3650c1db011f4dc5e01413c970f014bcfa7f25ee2840386854f` | 36,528,436 B | (48000,100) | (48000,) |
| `weak_z_run1.npz` | `6924c836ceba58c742db5f4c076daa7c60e25356d22e31f8b2ea66fef3f75daa` | 36,531,320 B | (48000,100) | (48000,) |
| `weak_z_run2.npz` | `32fb419985795d92daba1c705488b7bdaead8b256eff4377427ee03058cfcc76` | 36,541,589 B | (48000,100) | (48000,) |
| `weak_z_run3.npz` | `495b9141857cd2258c5d31c9e44ce20cf7ad3b808d440488a9abedd834d09532` | 36,533,236 B | (48000,100) | (48000,) |
| `weak_z_run4.npz` | `111e91292bbe9c1f12a9b1ba504407c1229ce247c8ab993d4ed1826aa60527d0` | 36,544,746 B | (48000,100) | (48000,) |

gamma_H2 = 1.50 (P22; halved H2 drive vs nominal).

### Condition: strong_z (gamma_H2=6.00, provide_z=True, use_obs_model=True)

| File | SHA-256 | Size | y shape | z shape |
|------|---------|------|---------|---------|
| `strong_z_run0.npz` | `95be75393f9b9eb6f690ce6fcefae18828f3e61d36ead83f0812c9cd95068f0b` | 36,878,807 B | (48000,100) | (48000,) |
| `strong_z_run1.npz` | `304ffa368010ff157edc4bb37de0bb5cdc4335ee37684fba0d5db11dd6ac91c6` | 36,893,074 B | (48000,100) | (48000,) |
| `strong_z_run2.npz` | `9008a2723562537925a5e502391b6ddb3b3ab73c9d2616429a50004f9c2bef14` | 36,906,726 B | (48000,100) | (48000,) |
| `strong_z_run3.npz` | `91b8a3b6326fe80db2c6005e5f77dc1ef239801a6b13b61b02fd8c4f97d2a71a` | 36,903,837 B | (48000,100) | (48000,) |
| `strong_z_run4.npz` | `e42b8316de831b85428924abdfacf1d26b5f1c13f0ac9a43524f9bf4df284258` | 36,921,452 B | (48000,100) | (48000,) |

gamma_H2 = 6.00 (P23; doubled H2 drive vs nominal).

---

## Metadata Artifact

| File | SHA-256 | Size | Content |
|------|---------|------|---------|
| `results/phase7c/canonical/metadata.json` | `2cfe4015ba1893f16dbbe063e13768ce0953a4a623c1c62ee1fe70a452044326` | 8,776 B | Run configuration, timestamps, parameter values, seed policy, artifact index |

---

## Audit Log Snapshot

| File | SHA-256 (at freeze) | Size | Content |
|------|---------------------|------|---------|
| `ground_truth/audit_log.jsonl` | `57aeb49d6afdf2854cc04220426adc577b1e17573afaccb29fef7c0363072045` | 3,183 B | All 8 required audit event types (hash_committed, hash_verification V1/V2, acceptance_test ×4, simulation_gate_passed, phase7c events) |

---

## Hashes Manifest Artifact

| File | SHA-256 (meta-hash, self-referential) | Size | Content |
|------|---------------------------------------|------|---------|
| `results/phase7c/canonical/hashes.json` | `7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed` | computed | SHA-256 hashes for all 32 artifacts; frozen at 2026-06-13T10:19:04Z |

The meta-hash is the SHA-256 of the `hashes.json` file contents (including itself). It is the canonical fingerprint of the entire dataset.

---

## Information Barrier Confirmation

The following artifacts were NOT provided to the simulator and are NOT included in trajectory files:

| Artifact | Reason withheld |
|----------|-----------------|
| `A_sparse` full matrix | INV-I1: framework never sees coupling matrix |
| H2 topology / SA set | INV-I2: framework never sees H2 membership |
| `D` diffusion matrix | INV-I3: framework never sees noise parameters |
| `labels.json` | INV-I4: framework never sees ground-truth labels |

The framework receives: `y` (calcium traces, shape T_eff×N_OBS) and optionally `z_oracle` (latent state, shape T_eff) depending on condition.

---

## Total Dataset Size

| Component | Size |
|-----------|------|
| Trajectory data (25 npz files) | 874 MB |
| Metadata + hashes | ~9 KB |
| Locked ground truth (labels, A, params) | ~878 KB |
| Audit log | 3 KB |
| **Total** | **~875 MB** |
