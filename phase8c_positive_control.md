# Phase 8C: Axis 4 — Positive Control

**Condition**: GAMMA_H2=12.0, THETA_Z=0.01 (combined favorable conditions)  
**Date**: 2026-06-13

---

## Pre-Registered Interpretation Criteria

From `phase8c_scope_map_plan.md`:
- If C-AUROC ≥ 0.55: framework can succeed under favorable conditions → benchmark difficulty explains Phase 8B failure.
- If C-AUROC ≥ 0.65: framework fully succeeds in favorable regime → benchmark at detection boundary.
- If C-AUROC < 0.55: fundamental architectural limitation — neither stronger signal nor better state separation rescues detection.

---

## Setup

| Parameter | Value |
|-----------|-------|
| GAMMA_H2 | 12.0 (4× benchmark) |
| THETA_Z | 0.01 (10× slower than benchmark) |
| SIGMA_Z | 1.00 (unchanged) |
| Topology (A_sparse) | frozen (unchanged) |
| Seeds | z_seed=49+r, x_seed=60+r |
| N_RUNS | 5 |

Stationary var(z) = σ²/(2θ) = 1.0/(2×0.01) = 50.0 (10× benchmark).

---

## Results

| Metric | Benchmark (frozen) | Positive control | Change |
|--------|-------------------|-----------------|--------|
| MacroAUROC | 0.5385 | 0.5214 | −0.0171 |
| C-AUROC | 0.4484 | 0.4837 | **+0.0353** |
| LR-AUROC | 0.4197 | 0.4621 | **+0.0424** |
| S-AUROC | 0.8531 | 0.7085 | −0.1446 |

---

## Findings

### C-AUROC

C-AUROC = **0.4837** — the highest C-AUROC observed across all probes in Phase 8C. The combined effect of 4× stronger H2 drive and 10× more persistent z improves C-AUROC by 0.0353 over the frozen benchmark. This gain exceeds either axis alone (Axis 1 gain at GAMMA_H2=12.0: +0.0173; Axis 3 gain at THETA_Z=0.01: +0.0125), suggesting partial superadditivity of the two favorable conditions.

**However**, C-AUROC = 0.4837 remains below chance (< 0.50). The framework is still anti-informative on C-classification even in the most favorable tested regime.

### LR-AUROC

LR-AUROC = 0.4621, also the highest across all probes. Still below chance.

### MacroAUROC

MacroAUROC = 0.5214 — *lower* than the benchmark (0.5385), because the large S-AUROC degradation (−0.1446) more than offsets the C/LR gains. The positive-control regime damages structural detection while providing limited improvement in latent-regulated detection.

### S-AUROC

S-AUROC = 0.7085 — a substantial drop from the benchmark's 0.8531. Very high GAMMA_H2 and very slow z create strong global correlated activity that confounds PCor_cond estimation for structural pairs.

---

## Interpretation Against Pre-Registered Criteria

| Criterion | Threshold | Result | Assessment |
|-----------|-----------|--------|------------|
| C-AUROC ≥ 0.55 | Benchmark too hard, not framework broken | **NOT MET** (0.4837) | — |
| C-AUROC ≥ 0.65 | Framework fully succeeds in favorable regime | **NOT MET** (0.4837) | — |
| C-AUROC < 0.55 | Architectural limitation | **MET** | Confirmed |

---

## Combined Axis Comparison

| Condition | GAMMA_H2 | THETA_Z | C-AUROC | C-AUROC above 0.50? |
|-----------|----------|---------|---------|---------------------|
| Axis 1 extreme (strength only) | 12.0 | 0.10 | 0.4657 | No |
| Axis 3 extreme (separability only) | 3.0 | 0.01 | 0.4609 | No |
| Positive control (combined) | 12.0 | 0.01 | 0.4837 | No |
| Frozen benchmark | 3.0 | 0.10 | 0.4484 | No |

The positive control produces the best C-AUROC of any tested condition — but it never crosses 0.50. The gain from combining both favorable parameters is +0.0353, consistent with partial additivity of individual axis gains.

---

## Conclusion

**The framework has a fundamental architectural limitation.** Even in the most favorable tested regime (GAMMA_H2=12.0, THETA_Z=0.01), C-AUROC remains below chance (0.4837 < 0.50). The positive control pre-registered criterion for "benchmark too hard, framework valid" (C-AUROC ≥ 0.55) is not met.

This constitutes the scope map's definitive finding: the current-velocity framework fails to detect latent-regulated pairs not because the benchmark is too hard, but because the Delta_PCor scoring mechanism is systematically anti-correlated with C-ness across the entire tested parameter space. The framework's architecture — using z-mediated partial correlation change as the C-signal — does not effectively distinguish SAREACHABLE pairs (C/M) from non-SAREACHABLE pairs (N), even under the most favorable signal conditions.

The S-AUROC degradation at extreme parameters (0.7085) also indicates that the precision matrix estimation is fragile when global z-correlations are strong, creating a conflicting objective between structural detection (requires well-estimated PCor_cond) and latent-regulated detection (requires large Delta_PCor).
