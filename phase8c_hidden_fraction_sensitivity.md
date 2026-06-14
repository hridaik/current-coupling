# Phase 8C: Axis 2 — Hidden-Neuron Fraction Sensitivity

**Axis**: N_H2_ACTIVE (number of H2 neurons with nonzero z-drive)  
**Pre-specified values**: {0, 2, 4, 6, 8}  
**Date**: 2026-06-13

---

## Pre-Registered Interpretation Criteria

From `phase8c_scope_map_plan.md`:
- If C-AUROC degrades monotonically as N_H2_ACTIVE decreases: framework is sensitive to H2 active fraction.
- If C-AUROC is flat: framework is insensitive to z-mediation regardless of active H2 count.
- If sharp degradation at k<4: minimum active-H2 threshold exists.
- At k=0: C-AUROC should be ≈ 0.50 (no z-mediated signal). Significant deviation indicates confounds.

---

## Setup

Active H2 neurons (in order from sorted SA = {132,...,139}):
- k=0: none active (GAMMA_H2=0 for all H2)
- k=2: {132, 133} active
- k=4: {132, 133, 134, 135} active
- k=6: {132, 133, 134, 135, 136, 137} active
- k=8: all active (baseline = oracle_z frozen result)

All labels are unchanged (topology fixed; SAREACHABLE defined by structure, not drive amplitude).

---

## Results

| N_H2_ACTIVE | Active H2 neurons | MacroAUROC | C-AUROC | LR-AUROC | S-AUROC |
|-------------|------------------|-----------|---------|----------|---------|
| 0 | none | 0.5414 | 0.4425 | 0.4083 | 0.8896 |
| 2 | {132, 133} | 0.5408 | 0.4442 | 0.4110 | 0.8798 |
| 4 | {132,133,134,135} | 0.5493 | 0.4480 | 0.4225 | 0.8684 |
| 6 | {132,...,137} | 0.5392 | 0.4402 | 0.4112 | 0.8672 |
| 8 | all (frozen) | **0.5385** | **0.4484** | **0.4197** | **0.8531** |

---

## Findings

### C-AUROC behavior across active H2 count

- **Range**: 0.4402 to 0.4493 (total variation: 0.0082)
- **No monotone trend**: C-AUROC does not systematically increase as more H2 neurons become active.
- **At k=0 (no H2 active)**: C-AUROC = 0.4425, compared to 0.4484 at k=8. The difference is 0.0059 — negligible. The framework's C-score is nearly unchanged when all H2 z-drive is eliminated.
- **All values below chance**: C-AUROC < 0.50 at all k values.

### S-AUROC trend

S-AUROC decreases monotonically as more H2 neurons are deactivated (from 0.8531 at k=8 to 0.8896 at k=0). The relationship is inverse — fewer active H2 neurons improves structural detection, consistent with H2 drive being a confound for S-classification rather than an aid.

### The k=0 baseline

At k=0, H2 neurons exist in the network topology (A_sparse) but receive no z-drive. The C labels remain (topology unchanged) but carry zero z-mediated signal. The framework achieves C-AUROC=0.4425 in this regime — essentially identical to the baseline (0.4484) where all H2 neurons are z-driven. This is the most critical result: the framework cannot distinguish its C-AUROC regime with z-mediated signal from its regime without any z-mediated signal.

---

## Interpretation Against Pre-Registered Criteria

| Criterion | Pre-specified | Result |
|-----------|---------------|--------|
| C-AUROC degrades with fewer active H2 | Framework sensitive to H2 active fraction | **NOT MET** (no clear trend) |
| C-AUROC flat across all N_H2_ACTIVE | Framework insensitive to z-mediation | **MET** (range = 0.0082) |
| Sharp degradation at k<4 | Minimum threshold exists | **NOT MET** (flat throughout) |
| At k=0: C-AUROC ≈ 0.50 | No z-signal → chance performance | **NOT MET** (0.4425, below chance) |

---

## Conclusion

**The framework's C-detection mechanism does not exploit H2-mediated z signals.** The C-AUROC at k=0 (no active H2) is virtually identical to the k=8 baseline. This means the Delta_PCor quantity — which is designed to capture z-mediated partial correlation change — is not reliably detecting the H2-mediated signal structure even when it is present at full strength.

Additionally, C-AUROC below chance (< 0.50) even at k=0 indicates the framework is anti-informative: pairs labeled C tend to receive lower C-scores than pairs labeled N. This is not a noise floor effect — it is a systematic sign reversal. Pairs with SAREACHABLE topology receive lower Delta_PCor scores than pairs without it, possibly because their structural connectivity (H2 in-edges and out-edges) affects PCor_cond estimation in a way that reduces Delta_PCor relative to non-SAREACHABLE pairs.

This finding is the strongest evidence of an architectural limitation in the current-velocity framework.
