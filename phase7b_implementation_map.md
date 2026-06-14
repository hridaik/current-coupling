# Phase 7B — Implementation Map

## Purpose

Every item in the Phase 6B specifications and Phase 7A audit specs maps to exactly one
code location. Every code module maps to exactly one spec item. No orphan logic exists.

---

## Module Layout

```
scripts/phase7b/
├── config.py        Stage 1 — parameter registry (all scientific constants)
├── graph.py         Stage 2 — graph construction (A_sparse, D, B)
├── labels.py        Stage 3 — label generation (DIRECT, SAREACHABLE, S/C/M/N)
├── audit.py         Stage 4 — hash-lock, audit log, serialization
├── checks.py        Stage 2/3 — construction checks CK-G*, CK-L*, CK-H*
├── dynamics.py      Stage 5 — SDE integrator, observation model
├── acceptance.py    Stage 6 — acceptance tests P1-A through P1-D
├── run_stage1.py    Verify config completeness
├── run_stage2.py    Build graph; run CK-G*
├── run_stage3.py    Generate labels; run CK-L*; run CK-H*
├── run_stage4.py    Hash lock; V1 verification
├── run_stage5.py    Unit-test dynamics components (no trajectories)
├── run_stage6.py    Run acceptance tests P1-D, P1-C, P1-B, P1-A in order
└── run_all_stages.py  Drive all 6 stages; emit test report
ground_truth/
├── labels.json
├── labels.sha256
├── A_sparse.npy
├── A_sparse.sha256
├── construction_params.json
├── construction_params.sha256
└── audit_log.jsonl
```

---

## Spec → Code Mapping

### phase6b_parameter_registry.md

| Parameter | Code location | Verification |
|---|---|---|
| P01 N_obs=100 | `config.N_OBS` | `run_stage1` checks all P* constants exist |
| P02 N_H1=32 | `config.N_H1` | same |
| P03 N_H2=8 | `config.N_H2` | same |
| P04 N_modules=4 | `config.N_MODULES` | same |
| P05 N_per_module=25 | `config.N_PER_MODULE` | same |
| P06 N_H1_per_module=8 | `config.N_H1_PER_MODULE` | same |
| P07 p_within=0.15 | `config.P_WITHIN` | CK-G12 |
| P08 p_between=0.03 | `config.P_BETWEEN` | CK-G12 |
| P09 p_H1_in=0.30 | `config.P_H1_IN` | CK-G10 enforcement |
| P10 p_H1_out=0.25 | `config.P_H1_OUT` | CK-G10 enforcement |
| P11 p_H2_in=0.20 | `config.P_H2_IN` | P1-A strength calculation |
| P12 p_H2_out=0.20 | `config.P_H2_OUT` | P1-A strength calculation |
| P13 σ_obs_obs=0.30 | `config.SIGMA_OBS_OBS` | CK-G13 (weight range) |
| P14 σ_H1=0.25 | `config.SIGMA_H1` | same |
| P15 σ_H2_in=0.25 | `config.SIGMA_H2_IN` | same |
| P16 σ_H2_out=0.35 | `config.SIGMA_H2_OUT` | same |
| P17 A_self=-1.5 | `config.A_SELF` | CK-G2 |
| P18 dim_z=1 | `config.DIM_Z` | INV-B4 |
| P19 θ_z=0.10 | `config.THETA_Z` | dynamics unit test |
| P20 σ_z=1.00 | `config.SIGMA_Z` | dynamics unit test |
| P21 γ_H2=3.00 | `config.GAMMA_H2` | INV-B2 test |
| P22 γ_H2_weak=1.50 | `config.GAMMA_H2_WEAK` | condition config |
| P23 γ_H2_strong=6.00 | `config.GAMMA_H2_STRONG` | condition config |
| P24 d_0=1.00 | `config.D_0` | CK-G (D construction) |
| P25 ε_lr=0.10 | `config.EPS_LR` | INV-C3 |
| P26 D_state_dep=False | `config.D_STATE_DEPENDENT` | INV-C1 |
| P27 κ_ca=0.50 | `config.KAPPA_CA` | dynamics unit test |
| P28 σ_obs=0.10 | `config.SIGMA_OBS_NOISE` | dynamics unit test |
| P29 nonlinearity=softplus | `config.NONLINEARITY` | dynamics unit test |
| P30 dt=0.10 | `config.DT` | dynamics unit test |
| P31 T=50000 | `config.T` | run_stage5 |
| P32 T_warmup=2000 | `config.T_WARMUP` | INV-S1 |
| P33 R=5 | `config.R` | run_stage5 |
| P34 master_seed=42 | `config.MASTER_SEED` | CK-G (seed used) |

---

### phase6b_architecture_spec.md

| Spec section | Code location |
|---|---|
| §1.1 Neuron counts | `config.N_OBS`, `config.N_H1`, `config.N_H2`, `config.N_TOTAL` |
| §1.2 Module assignments (observed) | `config.MODULE_OBS` |
| §1.3 Module assignments (H1) | `config.MODULE_H1` |
| §1.4 H2 target modules | `config.H2_TARGETS`, `config.SA` |
| §2.1 Coupling convention A[k,j]=j→k | enforced in `graph.build_A_sparse` |
| §2.2 No A_lr (A=A_sparse) | CK-G3; `graph.build_A_sparse` returns no lr term |
| §2.3 Observed-observed sparsity | `graph._draw_oo_sparsity` |
| §2.4 H1 connectivity | `graph._draw_h1_connectivity` |
| §2.5 H2 connectivity | `graph._draw_h2_connectivity` |
| §2.6 Self-connections A[k,k]=-1.5 | `graph._set_diagonal` |
| §2.7 Weight distributions | `graph._draw_weights` |
| §2.8 Stability check + resampling | `graph._stability_check_and_resample` |
| §2.9 Sub-seed table | `config.SEEDS` dict |
| §3.1 dim_z=1 | `config.DIM_Z`; `dynamics.step_z` |
| §3.2 z OU dynamics | `dynamics.step_z` |
| §3.3 z effect via B(z) | `dynamics.compute_B` |
| §3.4 SA set | `config.SA` (frozenset) |
| §3.5 No gain modulation | enforced: A never modified in `dynamics.step_x` |
| §4.1 D=D_diag+D_lr | `graph.build_D` |
| §4.2 D_lr = ε_lr × u×uᵀ | `graph.build_D`, seed 48 |
| §4.3 D state-independent | INV-C1; `dynamics.step_x` receives fixed D |
| §5.1 Euler-Maruyama | `dynamics.step_x`, `dynamics.step_z` |
| §5.2 Warm-up 2000 steps | `dynamics.simulate_run` discards first T_WARMUP |
| §6.1 Observed fraction | 100/140; all obs indices 0-99 are imaged |
| §6.2 Observation pipeline | `dynamics.observe` (softplus → calcium → noise) |
| §6.3 What framework receives | documented in `dynamics.simulate_run` output |
| §6.4 Evaluation conditions | `config.CONDITIONS` |

---

### phase6b_label_generation_spec.md

| Spec section | Code location |
|---|---|
| Hard Constraint 1 (construction-exclusivity) | `labels.generate_labels` takes only A_sparse, SA |
| Hard Constraint 2 (framework-independence) | no imports from dynamics/audit in labels.py |
| DIRECT(i,j) definition | `labels._compute_direct` |
| SAREACHABLE(i,j) definition | `labels._compute_sareachable` |
| Label assignment rules (S/C/M/N) | `labels._assign_label` |
| Witness selection (lowest-index H2) | `labels._find_lowest_witness` |
| Pre-commitment protocol | `audit.commit_labels` |
| Sanity checks LG1-LG4 | `checks.run_label_checks` (CK-L*) |

---

### phase7a_construction_checks.md

| Check | Code location |
|---|---|
| CK-G1 dimensions | `checks.ck_g1_dimensions` |
| CK-G2 self-inhibition | `checks.ck_g2_self_inhibition` |
| CK-G3 no A_lr | `checks.ck_g3_no_alr` |
| CK-G4 stability | `checks.ck_g4_stability` |
| CK-G5 module partition | `checks.ck_g5_module_partition` |
| CK-G6 H2 target spec | `checks.ck_g6_h2_target_spec` |
| CK-G7 no H2-H2 | `checks.ck_g7_no_h2h2` |
| CK-G8 no H1-H2 | `checks.ck_g8_no_h1h2` |
| CK-G9 no H1-H1 | `checks.ck_g9_no_h1h1` |
| CK-G10 H1 cross-module | `checks.ck_g10_h1_cross_module` |
| CK-G11 H2 out-of-target | `checks.ck_g11_h2_out_of_target` |
| CK-G12 sparsity plausibility | `checks.ck_g12_sparsity_plausibility` |
| CK-L1 pair count | `checks.ck_l1_pair_count` |
| CK-L2 coverage | `checks.ck_l2_coverage` |
| CK-L3 vocabulary | `checks.ck_l3_vocabulary` |
| CK-L4 mutual exclusivity | `checks.ck_l4_mutual_exclusivity` |
| CK-L5 DIRECT consistency | `checks.ck_l5_direct_consistency` |
| CK-L6 SAREACHABLE consistency | `checks.ck_l6_sareachable_consistency` |
| CK-L7 witness correctness | `checks.ck_l7_witness_correctness` |
| CK-H1 module pair coverage | `checks.ck_h1_module_pair_coverage` |
| CK-H2 exact H2 counts | `checks.ck_h2_exact_h2_counts` |
| CK-H3 module H2 count | `checks.ck_h3_module_h2_count` |
| CK-H4 H2 target count | `checks.ck_h4_h2_target_count` |

---

### phase7a_invariants.md

| Invariant | Verification location |
|---|---|
| INV-A1 A fixed | `checks.inv_a1_a_fixed` (hash comparison) |
| INV-A2 no gain modulation | static: `dynamics.step_x` never reads A through z |
| INV-A3 spectral abscissa | CK-G4 |
| INV-A4 A_lr=0 | CK-G3 |
| INV-A5 diagonal=-1.5 | CK-G2 |
| INV-B1 z only through B | `checks.inv_b1_z_only_through_B` (unit test) |
| INV-B2 B(z)=γz for H2 | `checks.inv_b2_B_linearity` |
| INV-B3 only H2 get z-drive | `checks.inv_b3_only_h2_z_drive` |
| INV-B4 SA is frozenset | `config.SA` type assertion |
| INV-C1 D constant | `checks.inv_c1_D_constant` (D not z-dependent) |
| INV-C2 D positive definite | `checks.inv_c2_D_posdef` |
| INV-C3 D_lr rank 1 | `checks.inv_c3_Dlr_rank1` |
| INV-L1 labels before trajectories | `run_stage4` completes before `run_stage5` |
| INV-L2 labels from construction only | `labels.py` imports only numpy; no dynamics imports |
| INV-L3 labels immutable after commit | file mode 0444 after `audit.commit_labels` |
| INV-L4 labels reproducible | P1-C test |
| INV-I1 framework gets no A | not implemented in 7B (framework not yet run) |
| INV-I2 framework gets no H2 topology | same |
| INV-I3 labels hidden from framework | same |
| INV-I4 framework gets no D | same |
| INV-S1 warm-up discarded | array shape assertion in `dynamics.simulate_run` |
| INV-S2 runs independent | seed table: 49+r for z, 60+r for x |
| INV-S3 oracle z is true z | same output array saved alongside y |

---

### phase7a_acceptance_tests.md

| Test | Code location |
|---|---|
| P1-A H2 weight effectiveness | `acceptance.p1a_h2_weight_effectiveness` |
| P1-B class count plausibility | `acceptance.p1b_class_count_plausibility` |
| P1-C SAREACHABLE consistency | `acceptance.p1c_sareachable_consistency` |
| P1-D hash round-trip | `acceptance.p1d_hash_roundtrip` |
| Gate function | `acceptance.check_all_passed` |
