# D2: Off-Connectome / Structure-of-Interest Subset Enrichment

**Date**: 2026-06-13

---

## Biologically Relevant Subset Definition

The benchmark does not directly encode "behaviorally meaningful" labels, but the ground truth provides enough structure to define a close proxy.

**Off-connectome + state-dependent analog = Class C:**
- `direct=0`: not in the structural connectome (off-connectome)
- `sareachable=1`: regulated through a state-active H2 neuron (state-dependent)
- Each C pair has a `witness_h2` — the specific H2 neuron whose topology creates the SAREACHABLE path

**Within C, a strength gradient exists.** The H2 path strength is:

`path_strength(i→j via h) = |A[h, i]| × |A[j, h]|`

This captures the product of the H2 input weight from i and the H2 output weight to j — the mechanistic coupling strength of the z-mediated path.

| Subset | Definition | n |
|--------|-----------|---|
| C_all | all C pairs (direct=0, sareachable=1) | 857 |
| strong_C | C pairs with path_strength > median (0.0272) | 428 |
| weak_C | C pairs with path_strength ≤ median | 429 |
| M | direct=1, sareachable=1 (structural + state-modulated) | 89 |
| LR | C ∪ M (all SAREACHABLE links) | 946 |
| S | direct=1, sareachable=0 (pure structural) | 497 |

**Path strength distribution for C:** min=0.000, p10=0.002, median=0.027, mean=0.051, max=0.392. Roughly 28% of C pairs have path_strength < 0.01 (per acceptance test P1A).

---

## AUROC and AUPRC by Subset (C-score ranking)

| Subset | n | C-AUROC | C-AUPRC | AUPRC/base_rate |
|--------|---|---------|---------|----------------|
| C_all | 857 | 0.4484 | 0.0756 | 0.873 |
| strong_C | 428 | **0.4069** | 0.0348 | 0.803 |
| weak_C | 429 | **0.4944** | 0.0415 | 0.958 |
| M | 89 | 0.1518 | 0.0049 | 0.547 |
| LR (C+M) | 946 | 0.4168 | 0.0788 | 0.824 |
| S | 497 | 0.1472 | 0.0276 | 0.550 |

**Key finding**: The framework is MORE anti-informative for strong_C (AUROC=0.4069) than for weak_C (AUROC=0.4944). The biologically strongest off-connectome links are ranked worse by the framework's C-score. This is the inverse of the desired behavior.

AUPRC is below base_rate for all subsets using C-score, confirming the framework cannot identify any subset at precision above chance.

---

## Top-K Enrichment by C-Score

| Subset | k=50 OR | k=50 p | k=100 OR | k=200 OR |
|--------|---------|-------|---------|---------|
| C_all | 0.000 | 1.000 | 0.324 | 0.729 |
| strong_C | 0.000 | 1.000 | 0.449 | 0.680 |
| weak_C | 0.000 | 1.000 | 0.221 | 0.797 |
| M | 0.000 | 1.000 | 0.000 | 0.000 |
| LR | 0.000 | 1.000 | 0.290 | 0.653 |
| S | 0.000 | 1.000 | 0.189 | 0.188 |

Zero enrichment (OR=0) at k=50 for every subset. No biologically relevant subset appears in the top 50 by C-score. At k=100, weak_C has slightly higher depletion (OR=0.221) than strong_C (OR=0.449), consistent with the AUROC finding that strong_C is more anti-informative.

---

## Top-K Enrichment by LR-Score (C+M combined)

| Subset | k=50 OR | k=50 p | k=100 OR | k=200 OR |
|--------|---------|-------|---------|---------|
| C_all | 0.672 | 0.823 | 0.671 | 0.729 |
| strong_C | 0.450 | 0.900 | 0.449 | 0.799 |
| weak_C | 0.919 | 0.661 | 0.919 | 0.678 |
| LR | 0.603 | 0.867 | 0.710 | 0.708 |

LR-score is marginally better than C-score for weak_C (OR=0.919 vs 0.000 at k=50) but still not significant. Strong_C enrichment remains near zero.

---

## H2-Witness-Specific Analysis

C pairs are distributed across 8 H2 witnesses (132–139) with varying counts:

| H2 witness | Count | Pct |
|-----------|-------|-----|
| 135 | 164 | 19.1% |
| 137 | 143 | 16.7% |
| 134 | 133 | 15.5% |
| 139 | 44 | 5.1% |
| (others) | 373 | 43.5% |

The analysis does not reveal differential recovery by H2 witness — all subsets show the same anti-informative ranking pattern.

---

## Conclusion

The framework does not selectively recover the biologically relevant subset of off-connectome, state-dependent links (C class) at any granularity:

1. **No improvement for strong C**: The highest-strength C links (strong_C, path_strength > 0.027) are ranked *worse* by the framework than weak_C. The mechanistically strongest off-connectome links are not preferentially recovered.

2. **All subsets depleted in top-K**: At k=50, no C subset (strong, weak, or mixed) has any representation in the top-ranked pairs.

3. **Framework is not selectively recovering any off-connectome organization**: The C-score is anti-informative across all tested subsets and biologically motivated stratifications.

4. **The biologically relevant subset (strong C, sareachable, off-connectome) is the hardest case** — not the easiest — for this framework. The architecture does not produce preferential recovery of the most mechanistically meaningful links.
