# Phase 8C: Axis 3 — State Separability Sensitivity

**Axis**: THETA_Z (OU mean-reversion rate)  
**Pre-specified values**: {0.01, 0.05, 0.10, 0.50, 2.00}  
**Date**: 2026-06-13

---

## Pre-Registered Interpretation Criteria

From `phase8c_scope_map_plan.md`:
- If C-AUROC increases with lower theta_z: state separability is a limiting factor.
- If C-AUROC flat despite 200× variation: framework's z-regression does not benefit from state persistence.
- If monotone: supports state-separability as mechanism.
- If C-AUROC decreases at very low theta_z: persistent z creates global correlation confound.

---

## Setup

| theta_z | var(z) = σ²/(2θ) | Coherence time ≈ 1/θ steps | Source |
|---------|-----------------|---------------------------|--------|
| 0.01 | 50.0 | 100 steps | probe simulation |
| 0.05 | 10.0 | 20 steps | probe simulation |
| 0.10 | 5.0 | 10 steps | **frozen benchmark** |
| 0.50 | 1.0 | 2 steps | probe simulation |
| 2.00 | 0.25 | 0.5 steps | probe simulation |

sigma_z fixed at 1.00 (var(z) changes with theta_z). GAMMA_H2=3.00 fixed.

---

## Results

| THETA_Z | var(z) | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|---------|--------|-----------|---------|----------|---------|
| 0.01 | 50.00 | 0.5367 | 0.4609 | 0.4368 | 0.8088 |
| 0.05 | 10.00 | 0.5386 | 0.4494 | 0.4218 | 0.8471 |
| 0.10 | 5.00 | **0.5385** | **0.4484** | **0.4197** | **0.8531** |
| 0.50 | 1.00 | 0.5398 | 0.4460 | 0.4152 | 0.8670 |
| 2.00 | 0.25 | 0.5409 | 0.4503 | 0.4159 | 0.8832 |

---

## Findings

### C-AUROC trend

- **Range**: 0.4460 to 0.4609 (total variation: 0.0149)
- **Weak U-shape or near-monotone**: C-AUROC is highest at theta_z=0.01 (0.4609) and lowest at theta_z=0.50 (0.4460).
- **theta_z=2.00 slightly higher than 0.50**: 0.4503 vs 0.4460, breaking strict monotonicity at the high end.
- **All values below chance**: C-AUROC < 0.50 at all five probe points.
- **Best probe (theta_z=0.01)**: C-AUROC=0.4609, which is 0.0941 below partial threshold (0.55).

### MacroAUROC and S-AUROC

MacroAUROC is essentially flat (0.5367–0.5409). S-AUROC shows a clear monotone decrease from 0.8832 at theta_z=2.00 to 0.8088 at theta_z=0.01: more persistent z creates global co-variance that moderately disrupts structural detection. This is a consistent pattern with Axis 1 — both higher GAMMA_H2 and lower THETA_Z appear to increase the "z-confound" on structural pairs.

### LR-AUROC

LR-AUROC follows C-AUROC: best at theta_z=0.01 (0.4368), worst at theta_z=0.50 (0.4152). Still below chance throughout.

---

## Interpretation Against Pre-Registered Criteria

| Criterion | Pre-specified | Result |
|-----------|---------------|--------|
| C-AUROC increases with lower theta_z | State separability limiting | **WEAKLY MET** (+0.0125 gain from 0.10 → 0.01) |
| C-AUROC flat despite 200× range | Framework insensitive to persistence | **LARGELY MET** (range = 0.0149) |
| Monotone increasing | State separability as mechanism | **PARTIALLY MET** (not strict) |
| C-AUROC decreases at theta_z=0.01 | Persistent z creates confound | **NOT MET** (theta_z=0.01 is best, but confound present in S-AUROC) |

---

## Conclusion

**State separability is not the limiting factor, but provides the most signal of any axis.** Reducing theta_z from 0.10 to 0.01 (making z 10× more persistent) improves C-AUROC by 0.0125. This is the largest per-step improvement seen across all three single-parameter axes, but still far too small to approach the partial threshold (0.55). The framework's z-regression receives marginally more signal when z is highly persistent (because persistent z creates stronger conditional/unconditional covariance divergence in H2-output pairs), but this effect is too weak to produce meaningful C-detection.

The simultaneous S-AUROC degradation at low theta_z (0.8531 → 0.8088) confirms that persistent z disrupts the estimation of structural correlation, creating a trade-off. There is no value of theta_z at which the framework successfully detects both structural and latent-regulated links.
