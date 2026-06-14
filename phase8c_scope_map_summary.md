# Phase 8C Scope Map Summary

**Date**: 2026-06-13  
**Status**: FINAL — all four diagnostic axes complete  
**Frozen verdict**: Phase 8B FAILURE (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197)

---

## Scope Map Classification

Per the pre-registered schema in `phase8c_scope_map_plan.md`:

| Criterion | Result | Classification |
|-----------|--------|---------------|
| C-AUROC ≥ 0.55 at any Axis 1 probe | NOT MET (max=0.4657) | — |
| C-AUROC ≥ 0.55 at any Axis 3 probe | NOT MET (max=0.4609) | — |
| C-AUROC ≥ 0.55 only at Axis 4 | NOT MET (0.4837) | — |
| C-AUROC < 0.55 at ALL probes including Axis 4 | **MET** | **Architecture-limited failure** |
| Positive control success (C-AUROC ≥ 0.65) | NOT MET (0.4837) | Framework is not valid in any tested regime |

**Classification: ARCHITECTURE-LIMITED FAILURE.**

The benchmark is not too hard. The framework has a fundamental design limitation.

---

## Results Table

### Axis 1: GAMMA_H2 (current strength)

| GAMMA_H2 | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|----------|-----------|---------|----------|---------|
| 0.5 | 0.5444 | 0.4500 | 0.4224 | 0.8804 |
| 1.5 | 0.5396 | 0.4459 | 0.4164 | 0.8662 |
| **3.0 (frozen)** | **0.5385** | **0.4484** | **0.4197** | **0.8531** |
| 6.0 | 0.5333 | 0.4572 | 0.4271 | 0.8259 |
| 12.0 | 0.5294 | 0.4657 | 0.4386 | 0.7827 |

### Axis 2: N_H2_ACTIVE (hidden fraction)

| N_H2_ACTIVE | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|-------------|-----------|---------|----------|---------|
| 0 | 0.5414 | 0.4425 | 0.4083 | 0.8896 |
| 2 | 0.5408 | 0.4442 | 0.4110 | 0.8798 |
| 4 | 0.5493 | 0.4480 | 0.4225 | 0.8684 |
| 6 | 0.5392 | 0.4402 | 0.4112 | 0.8672 |
| **8 (frozen)** | **0.5385** | **0.4484** | **0.4197** | **0.8531** |

### Axis 3: THETA_Z (state separability)

| THETA_Z | var(z) | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|---------|--------|-----------|---------|----------|---------|
| 0.01 | 50.0 | 0.5367 | 0.4609 | 0.4368 | 0.8088 |
| 0.05 | 10.0 | 0.5386 | 0.4494 | 0.4218 | 0.8471 |
| **0.10 (frozen)** | **5.0** | **0.5385** | **0.4484** | **0.4197** | **0.8531** |
| 0.50 | 1.0 | 0.5398 | 0.4460 | 0.4152 | 0.8670 |
| 2.00 | 0.25 | 0.5409 | 0.4503 | 0.4159 | 0.8832 |

### Axis 4: Positive Control (GAMMA_H2=12.0, THETA_Z=0.01)

| Condition | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|-----------|-----------|---------|----------|---------|
| Benchmark | 0.5385 | 0.4484 | 0.4197 | 0.8531 |
| Positive control | 0.5214 | 0.4837 | 0.4621 | 0.7085 |

---

## Per-Axis Findings

### Axis 1 (GAMMA_H2): Not signal-limited

C-AUROC varies by only 0.0198 across a 24× range of H2 drive strength. All values remain below chance. The framework does not benefit meaningfully from stronger z-mediated drive. **Benchmark GAMMA_H2=3.0 is not a disadvantaged regime.**

### Axis 2 (N_H2_ACTIVE): Insensitive to H2 mediation

C-AUROC at k=0 (no active H2 neurons) is 0.4425 — nearly identical to the k=8 baseline (0.4484). The framework's C-score (Delta_PCor) is functionally insensitive to whether H2 neurons receive z-drive. **This is direct evidence that the Delta_PCor mechanism does not exploit the H2-mediated signal structure.** The total variation (0.0082) is smaller than any other axis.

### Axis 3 (THETA_Z): Not separability-limited

C-AUROC varies by 0.0149 over a 200× range of z coherence times. The best result (theta_z=0.01) is 0.4609, still 0.0391 below the partial threshold. **State separability is marginally helpful but not the limiting factor.**

### Axis 4 (Positive control): Framework fails even under favorable conditions

C-AUROC = 0.4837 under combined extreme conditions (GAMMA_H2=12.0, THETA_Z=0.01). This is the highest C-AUROC across all probes but still below chance. **The pre-registered success criterion (C-AUROC ≥ 0.55) is not met.** The benchmark is not too hard; the framework is architecturally limited.

---

## C-AUROC Landscape

C-AUROC range across ALL probes (N=15 conditions + 1 frozen benchmark):

| Summary | Value |
|---------|-------|
| Minimum C-AUROC (any probe) | 0.4402 (N_H2_ACTIVE=6) |
| Maximum C-AUROC (any probe) | 0.4837 (positive control) |
| Frozen benchmark | 0.4484 |
| Chance | 0.5000 |
| Partial threshold | 0.5500 |
| Success threshold | 0.6500 |

The entire C-AUROC landscape lies below chance. The gap to the partial threshold is 0.0663 (from the best probe) and 0.1016 (from the frozen benchmark).

---

## Diagnostic Interpretation

The Phase 8B FAILURE is an **architecture-limited failure**, not a signal-limited or dataset-limited failure. The key evidence:

1. **H2 active fraction insensitivity** (Axis 2, range 0.0082): The framework's C-score does not detect H2-mediated signal. Even removing all z-drive from H2 neurons does not change C-AUROC meaningfully. This directly implicates the Delta_PCor scoring design.

2. **Below-chance C-AUROC at k=0**: At N_H2_ACTIVE=0, there is definitionally no z-mediated signal for C pairs. Yet C-AUROC=0.4425 (below chance). This means the C-scoring is anti-informative due to structural effects — SAREACHABLE pairs (C topology) have lower Delta_PCor than non-SAREACHABLE pairs (N topology), likely because their H2 connectivity creates structural partial correlations that persist after z-regression.

3. **Positive control failure** (C-AUROC=0.4837 < 0.50): Under 4× stronger signal and 10× more persistent z, C-AUROC remains below chance.

4. **Signal strength saturation**: Axis 1 shows C-AUROC is nearly constant across a 24× range, with the relationship between GAMMA_H2 and C-AUROC being very weak and possibly confounded by S-AUROC degradation at high drive.

---

## Root Cause Hypothesis

The Delta_PCor scoring mechanism (C-score = |PCor_raw - PCor_cond|) is negatively correlated with SAREACHABLE topology. Possible mechanisms:

a) **Structural confound**: C pairs (i→H2→j connectivity) have H2-mediated structural pathways that affect PCor_cond via direct structural paths — not z-mediated — causing the conditional partial correlation to differ from the unconditional in a way that is similar for N pairs, or even more pronounced for N pairs through other structural pathways.

b) **Regression residual confound**: After z-regression, the residuals y_resid still contain H2-mediated correlation through structural paths (A[j,h2]≠0 means h2 affects j even after z is conditioned out). So PCor_cond for C pairs reflects both structural H2-mediated and z-independent H2-mediated paths, not purely the z-free structure.

c) **Statistical power**: With T_EFF=48,000 and N_OBS=100, the precision matrix estimation is in the low-sample-to-dimension regime (n/p = 480), making Delta_PCor estimates noisy and potentially dominated by estimation variance rather than true z-mediated signal.

---

## Implications for Future Frameworks

A framework targeting latent-regulated (C/M) detection in this architecture should:

1. Exploit the signed structure of z-mediated influence — not just the change in partial correlation, but the *direction* of change and the *sign* of the H2-output projection.
2. Use z as an instrument for interventional inference rather than a confounder to regress out — the current z-regression may remove the very signal it aims to detect.
3. Consider the H2 structural paths separately from z-mediated paths, since H2 neurons influence outputs both through z-modulation and through structural connections.
4. Address the finite-sample precision matrix estimation problem (n/p=480 is marginal for 100-dimensional PCor inference).

---

## Deliverable Checklist

| Deliverable | Status |
|-------------|--------|
| phase8c_scope_map_plan.md | COMPLETE |
| phase8c_strength_sensitivity.md | COMPLETE |
| phase8c_hidden_fraction_sensitivity.md | COMPLETE |
| phase8c_state_separability_sensitivity.md | COMPLETE |
| phase8c_positive_control.md | COMPLETE |
| phase8c_scope_map_summary.md | COMPLETE |
| results/phase8c/scope_map_results.json | COMPLETE |
