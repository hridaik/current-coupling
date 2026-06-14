# Phase 8C Scope Map Plan

**Date**: 2026-06-13  
**Status**: PRE-REGISTERED — written before any sensitivity analysis is run  
**Purpose**: Define the four diagnostic axes, probe values, and interpretation criteria for post-hoc failure analysis of the Phase 8B FAILURE verdict.

---

## Context

Phase 8B verdict: **FAILURE** (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197).  
The framework detects structural edges (S-AUROC=0.8531) but fails to detect latent-regulated edges (C-AUROC=0.4484, below chance; LR-AUROC=0.4197, well below chance).  
B5 (state-ΔCorr, a naive baseline) outperforms the framework on LR detection (LR-AUROC=0.5503 vs 0.4197).

Phase 8C goal: map the recoverability space — under what parameter regime could the current-velocity framework succeed, and does the benchmark lie outside that regime?

---

## Analysis Rules (from Phase 8C specification)

- Use the frozen primary metrics (MacroAUROC, C-AUROC, LR-AUROC).
- Use pre-specified sensitivity points (this document).
- No adaptive search; no optimization.
- Only the targeted axis may change per analysis.
- Do not modify the benchmark, framework, or frozen verdict.
- Look for evidence that the benchmark is too hard AND the opposite possibility.

---

## Axis 1: Current-Supported Link Strength (GAMMA_H2)

**Parameter**: H2 z-drive gain (GAMMA_H2).  
**Rationale**: GAMMA_H2 controls the strength of z-mediated modulation of H2 neurons. Higher GAMMA_H2 → larger Delta_PCor (z-mediated partial correlation change) for C pairs → more detectable C signal.

**Pre-specified probe values**: {0.5, 1.5, 3.0, 6.0, 12.0}

| Point | GAMMA_H2 | Source |
|-------|----------|--------|
| 1 | 0.5 | New probe simulation |
| 2 | 1.5 | Existing canonical `weak_z` data |
| 3 | 3.0 | Frozen benchmark (`oracle_z`) — result frozen |
| 4 | 6.0 | Existing canonical `strong_z` data |
| 5 | 12.0 | New probe simulation |

**Fixed across all points**: topology (A_sparse), theta_z=0.10, sigma_z=1.00, z_seeds=49+r, x_seeds=60+r, n_runs=5.

**Interpretation criteria**:
- If C-AUROC ≥ 0.55 at GAMMA_H2=12.0: "signal too weak" partially explains the FAILURE — stronger drive would partially recover detection.
- If C-AUROC < 0.55 at all probe values: framework is fundamentally blind to z-mediated signals regardless of strength.
- If C-AUROC monotone increasing in GAMMA_H2: signal strength is the primary limiting factor for this axis.
- If C-AUROC non-monotone or peaks below 0.55: confounds exist (e.g., high GAMMA_H2 saturates the network and disrupts PCor estimation).

---

## Axis 2: Hidden-Neuron Fraction (N_H2_ACTIVE)

**Parameter**: Number of H2 neurons receiving nonzero z-drive (GAMMA_H2=3.0 for active, GAMMA_H2=0 for inactive).  
**Rationale**: Varying the number of active H2 mediators changes how many C pairs have detectable z-mediated signal. With fewer active H2 neurons, more C pairs are "ghost C" — correctly labeled as C by topology but carrying zero z-mediated signal.

**Pre-specified probe values**: {0, 2, 4, 6, 8} active H2 neurons (out of 8 total SA neurons).

Active neurons are always the first k from sorted(SA) = {132, 133, 134, 135, 136, 137, 138, 139}:
- k=0: none active (GAMMA_H2=0 for all H2)
- k=2: {132, 133} active
- k=4: {132, 133, 134, 135} active
- k=6: {132, 133, 134, 135, 136, 137} active
- k=8: all active — baseline (use oracle_z canonical data)

**Fixed across all points**: topology (A_sparse), theta_z=0.10, sigma_z=1.00, z_seeds=49+r, x_seeds=60+r, n_runs=5.

**Interpretation criteria**:
- If C-AUROC degrades monotonically as N_H2_ACTIVE decreases: framework is sensitive to H2 active fraction, consistent with the Delta_PCor mechanism working partially.
- If C-AUROC is flat across all N_H2_ACTIVE: framework's C-score mechanism is insensitive to z-mediation regardless of how many H2 neurons are active.
- If C-AUROC degrades sharply at k<4 but is stable for k≥4: minimum active-H2 threshold exists for detectability.
- At k=0: C-AUROC should be ≈ 0.50 (no z-mediated signal, only topology noise). Significant deviation indicates confounds.

---

## Axis 3: State Separability (THETA_Z)

**Parameter**: OU mean-reversion rate (theta_z). Lower theta_z → more persistent z states → more distinct "high z" vs "low z" epochs.  
**Rationale**: The z-regression step in the framework removes z-correlated variance from y. The effectiveness of this removal depends partly on how persistent z is — more persistent z creates longer coherent epochs where H2 drive is consistently high or low, making the conditional and unconditional covariances more distinct.

**Pre-specified probe values**: {0.01, 0.05, 0.10, 0.50, 2.00}

| theta_z | Stationary var(z) = σ²/(2θ) | Coherence time ≈ 1/θ steps | Source |
|---------|---------------------------|---------------------------|--------|
| 0.01 | 50.0 | 100 steps | New probe |
| 0.05 | 10.0 | 20 steps | New probe |
| 0.10 | 5.0 | 10 steps | Frozen benchmark (oracle_z) |
| 0.50 | 1.0 | 2 steps | New probe |
| 2.00 | 0.25 | 0.5 steps | New probe |

sigma_z is held fixed at 1.00 (so stationary variance changes with theta_z). This deliberately conflates persistence and amplitude to represent realistic parameter variation.

**Fixed across all points**: GAMMA_H2=3.0, sigma_z=1.00, topology (A_sparse), z_seeds=49+r, x_seeds=60+r, n_runs=5.

**Interpretation criteria**:
- If C-AUROC increases with lower theta_z (more persistent z): state separability is a limiting factor; the benchmark (theta_z=0.10) lies in a moderate regime.
- If C-AUROC is flat despite theta_z ranging over 200×: the framework's z-regression does not benefit from state persistence.
- If C-AUROC increases at theta_z=0.01 but decreases at theta_z=2.00: monotone relationship supporting state-separability as mechanism.
- If C-AUROC decreases at very low theta_z (theta_z=0.01): z is so persistent it creates strong global correlation that overwhelms the PCor estimation.

---

## Axis 4: Positive Control

**Parameters**: Combined favorable conditions — GAMMA_H2=12.0 AND theta_z=0.01.  
**Rationale**: If the framework can detect LR edges under the most favorable plausible conditions (strong H2 drive + persistent z states), this confirms the architecture is valid but the benchmark is hard. If C-AUROC remains ≤ 0.55 even under favorable conditions, the framework has a fundamental design limitation.

**Probe**: Single condition — GAMMA_H2=12.0, theta_z=0.01, sigma_z=1.00, n_runs=5, z_seeds=49+r, x_seeds=60+r.

**Interpretation criteria**:
- If C-AUROC ≥ 0.55: framework can succeed under favorable conditions → benchmark difficulty explains Phase 8B failure.
- If C-AUROC ≥ 0.65 (matching primary success threshold): framework fully succeeds in favorable regime → benchmark lies at detection boundary.
- If C-AUROC < 0.55: framework has fundamental architectural limitation — neither stronger signal nor better state separation rescues detection.

---

## Metrics

For all probe conditions, compute (using same code as Phase 8B harness, same frozen labels):
- **MacroAUROC** (primary)
- **C-AUROC** (primary)
- **LR-AUROC** (primary)
- **S-AUROC** (secondary, for sanity check — should remain high)

Bootstrap CI not required for probe conditions (not primary endpoints). Point estimates only.

---

## Scope Map Summary Interpretation Schema

After all axes are measured, the scope map will be classified by:

| Result | Classification |
|--------|---------------|
| C-AUROC ≥ 0.55 at any Axis 1 or Axis 3 probe | "Signal-limited" failure — stronger signal rescues detection |
| C-AUROC ≥ 0.55 only at Axis 4 (combined favorable) | "Compound-limited" failure — requires both axes simultaneously |
| C-AUROC < 0.55 at all probes including Axis 4 | "Architecture-limited" failure — fundamental design issue |
| Positive control success (C-AUROC ≥ 0.65 at Axis 4) | "Benchmark is hard but framework is valid" |
| Positive control failure (C-AUROC < 0.55 at Axis 4) | "Framework architecture does not exploit current structure" |

---

## Pre-Specified Comparison Points

The Phase 8B result (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197) is the reference. All probe results are interpreted relative to this baseline. Sensitivity is evaluated by the *gradient* of performance improvement across probe values, not by whether any single probe achieves a success threshold.

---

## Implementation Notes

- Framework code: `scripts/phase8b_framework.py` (frozen, unmodified)
- Labels: `ground_truth/labels.json` (frozen, unmodified)
- Graph: `ground_truth/A_sparse.npy` (frozen, unmodified)
- New probe data: generated using same seed schedule as canonical (z_seed=49+r, x_seed=60+r)
- Existing data: `results/phase7c/canonical/data/` (weak_z, strong_z, oracle_z)
- Output directory: `results/phase8c/`
