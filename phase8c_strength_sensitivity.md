# Phase 8C: Axis 1 — Current-Supported Link Strength Sensitivity

**Axis**: GAMMA_H2 (H2 z-drive gain)  
**Pre-specified values**: {0.5, 1.5, 3.0, 6.0, 12.0}  
**Date**: 2026-06-13

---

## Pre-Registered Interpretation Criteria

From `phase8c_scope_map_plan.md`:
- If C-AUROC ≥ 0.55 at GAMMA_H2=12.0: "signal too weak" partially explains FAILURE.
- If C-AUROC < 0.55 at all probe values: framework is fundamentally blind to z-mediated signals.
- If monotone increasing: signal strength is the primary limiting factor.
- If non-monotone or peaks below 0.55: confounds exist.

---

## Results

| GAMMA_H2 | Source | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|----------|--------|-----------|---------|----------|---------|
| 0.5 | probe simulation | 0.5444 | 0.4500 | 0.4224 | 0.8804 |
| 1.5 | canonical weak_z | 0.5396 | 0.4459 | 0.4164 | 0.8662 |
| 3.0 | **frozen benchmark** | **0.5385** | **0.4484** | **0.4197** | **0.8531** |
| 6.0 | canonical strong_z | 0.5333 | 0.4572 | 0.4271 | 0.8259 |
| 12.0 | probe simulation | 0.5294 | 0.4657 | 0.4386 | 0.7827 |

---

## Findings

### C-AUROC trend

C-AUROC across the 24× range of GAMMA_H2 (0.5 → 12.0):

- **Range**: 0.4459 to 0.4657 (total variation: 0.0198)
- **Direction**: Very weakly positive — higher GAMMA_H2 is associated with slightly higher C-AUROC.
- **All values remain below chance**: C-AUROC < 0.50 across all five probe points. The framework is anti-informative on C-classification at all tested signal strengths.
- **Success threshold never approached**: C-AUROC of 0.4657 at GAMMA_H2=12.0 is 0.0843 below the partial threshold (0.55) and 0.1843 below the success threshold (0.65).

### MacroAUROC trend

MacroAUROC decreases with increasing GAMMA_H2 (0.5444 → 0.5294 across the range). The decrease is driven by S-AUROC: structural detection degrades at high H2 drive (0.8804 → 0.7827), likely because strong H2 activity introduces confounding correlation patterns that disrupt the PCor_cond estimation.

### LR-AUROC trend

Follows C-AUROC: slight positive trend with GAMMA_H2 but all values below 0.44.

---

## Interpretation Against Pre-Registered Criteria

| Criterion | Pre-specified | Result |
|-----------|---------------|--------|
| C-AUROC ≥ 0.55 at GAMMA_H2=12.0 | Would support "signal too weak" | **NOT MET** (0.4657) |
| C-AUROC < 0.55 at all probes | Supports fundamental blindness | **MET** |
| Monotone increasing in GAMMA_H2 | Signal strength primary factor | **PARTIALLY MET** (weak positive trend) |
| Non-monotone / peak below 0.55 | Confounds exist | **MET** (MacroAUROC falls) |

---

## Conclusion

**Signal strength is not the limiting factor.** Varying GAMMA_H2 over a 24× range (0.5 to 12.0) moves C-AUROC by only 0.0198, and C-AUROC remains below chance at all values. The framework cannot exploit z-mediated signal regardless of its amplitude. The benchmark's GAMMA_H2=3.0 does not place it in an especially disadvantaged regime on this axis — even 4× stronger drive (GAMMA_H2=12.0) produces no meaningful C-detection improvement.

The declining S-AUROC at high GAMMA_H2 indicates a confound: strong H2 drive disrupts the precision matrix estimation, degrading structural detection while providing negligible gain on latent-regulated detection. This is a trade-off that the framework handles poorly.
