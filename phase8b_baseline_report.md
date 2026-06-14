# Phase 8B Baseline Report

**Condition**: oracle_z  
**Date**: 2026-06-13

---

## Baseline Performance

| Baseline | MacroAUROC | C-AUROC | LR-AUROC | Direct-AUROC |
|----------|-----------|---------|----------|-------------|
| B1 (Null/Uniform) | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| B2 (Marginal prior) | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| B3 (Pairwise correlation) | 0.5277 | 0.5314 | 0.5327 | 0.5173 |
| B4 (Graphical Lasso) | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| B5 (State-ΔCorr) | 0.5348 | 0.5517 | 0.5503 | 0.4898 |
| B6 (Module oracle) | 0.6340 | 0.3830 | 0.3617 | 0.7058 |
| **Framework** | **0.5385** | **0.4484** | **0.4197** | **0.8585** |

---

## Notes on Individual Baselines

### B1 (Null)
Uniform 0.25 per class. MacroAUROC = 0.50 as expected.

### B2 (Marginal frequency prior)
Assigns committed class frequencies as constant. All AUROCs = 0.50 (constant score provides no ranking information).

### B3 (Pairwise correlation)
`|Pearson corr(y_i, y_j)|` averaged across 5 runs, softmax temperature 5.0. Slight improvement over chance (0.5277 MacroAUROC). Captures some shared signal.

### B4 (Graphical Lasso)
**GraphicalLasso failed to converge for all alpha values in the pre-specified grid** `[0.005, 0.01, 0.02, 0.05, 0.10]` (NaN duality gap for all). Fell back to B2 as specified. This triggered BV-3 failure (B4 direct-AUROC = 0.50 < 0.52 threshold). The pre-specified alpha grid was insufficient for the data scale.

### B5 (State-dependent ΔCorr)
Uses `|C_high_z - C_low_z|` with z_oracle median split. Achieves C-AUROC = 0.5517 and LR-AUROC = 0.5503 — the strongest C/LR signal among baselines. This is the pre-specified diagnostic: framework should exceed B5 LR-AUROC to demonstrate added value over pure state-detection.

**Framework LR-AUROC (0.4197) < B5 LR-AUROC (0.5503).** The framework underperforms state-ΔCorr on LR detection.

### B6 (Module oracle)
Uses known module membership (i//25 == j//25). Achieves MacroAUROC = 0.6340 — the highest of any baseline. This is an oracle baseline that uses knowledge forbidden to the framework. Direct-AUROC = 0.7058 is high because structural edges tend to be within-module.

Framework MacroAUROC (0.5385) < B6 (0.6340). The framework does not exceed the module-membership oracle.

---

## Pre-Registered Comparisons

| Comparison | Pre-specified | Result |
|------------|---------------|--------|
| Framework C-AUROC > B4 C-AUROC + 0.05 | Required for SUCCESS | FAIL (0.4484 < 0.5000 + 0.05) |
| Framework LR-AUROC > B5 LR-AUROC | Interpretive diagnostic | FAIL (0.4197 < 0.5503) |
| Framework MacroAUROC > B6 MacroAUROC | Interpretive diagnostic | FAIL (0.5385 < 0.6340) |

---

## B4 Failure Note

BV-3 (B4 direct-AUROC ≥ 0.52) failed due to B4 falling back to B2. This indicates the GraphicalLasso alpha grid was too coarse or the data scale was problematic. The BV-3 failure is a benchmark validity concern — it means the structural connectivity detector (B4) was not operational, which reduces confidence in the baseline comparison. This is pre-specified failure mode material, deferred to post-hoc interpretation.
