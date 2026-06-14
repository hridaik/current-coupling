# D1: Top-K Enrichment for the Current-Supported Class (C)

**Metric used**: Framework class_prob_C (the direct C-score output)  
**Reference**: Phase 8B frozen output (framework_output.json)  
**Date**: 2026-06-13

---

## Setup

| Parameter | Value |
|-----------|-------|
| Total pairs | 9900 |
| n(C) | 857 |
| C base rate | 0.0866 |
| C-AUROC (framework) | 0.4484 |
| Permutation samples | 10,000 |
| Ranking criterion | class_prob_C descending |

---

## Top-K Results (C class, ranked by C-score)

| K | Observed C | Expected C | Enrichment OR | Perm p-value | Precision@K | Recall@K | F1@K |
|---|-----------|-----------|--------------|-------------|------------|---------|-----|
| 10 | 0 | 0.9 | 0.000 | 1.0000 | 0.0000 | 0.0000 | 0.000 |
| 20 | 0 | 1.7 | 0.000 | 1.0000 | 0.0000 | 0.0000 | 0.000 |
| 50 | 0 | 4.3 | 0.000 | 1.0000 | 0.0000 | 0.0000 | 0.000 |
| 100 | 3 | 8.7 | 0.324 | 0.9949 | 0.0300 | 0.0035 | 0.006 |
| 200 | 13 | 17.3 | 0.729 | 0.8953 | 0.0650 | 0.0152 | 0.025 |
| 500 | 35 | 43.3 | 0.785 | 0.9260 | 0.0700 | 0.0408 | 0.053 |

**Interpretation**: OR < 1 at all tested K. The framework's C-score is uniformly anti-enriching for C at every rank threshold. Zero C pairs appear in the top 50 highest-ranked (by C-score) positions out of 9900. The permutation p-values confirm the depletion is systematic (p > 0.89 at all K), not just sampling noise.

---

## Inverted Score (Bottom-K by C-score = pairs most likely to be C by the framework's own logic)

| K | Observed C | Expected C | Enrichment OR | Perm p-value |
|---|-----------|-----------|--------------|-------------|
| 10 | 1 | 0.9 | 1.173 | 0.5898 |
| 20 | 1 | 1.7 | 0.555 | 0.8278 |
| 50 | 2 | 4.3 | 0.438 | 0.9303 |
| 100 | 7 | 8.7 | 0.793 | 0.7726 |

**Interpretation**: Even the bottom-K by C-score (pairs the framework most disfavors as C) does not show enrichment for C. The signal is not merely inverted — it is absent. C pairs are distributed approximately uniformly across the ranking, with a slight tendency toward mid-ranks.

---

## S-class Enrichment by S-score (Contrast)

For contrast, using S-score to rank S pairs:

| K | Observed S | Expected S | Enrichment OR | Perm p-value | Precision@K |
|---|-----------|-----------|--------------|-------------|------------|
| 10 | 8 | 0.5 | 76.9 | 0.0000 | 0.800 |
| 20 | 11 | 1.0 | 23.6 | 0.0000 | 0.550 |
| 50 | 26 | 2.5 | 21.6 | 0.0000 | 0.520 |
| 100 | 43 | 5.0 | 15.5 | 0.0000 | 0.430 |

The framework achieves strong top-K enrichment for S (structural) links — showing the ranking mechanism itself is functional; it simply does not recover C.

---

## Conclusion

The framework does NOT preferentially rank the current-supported (C) class at any tested K. Its C-score is systematically anti-informative: the highest-ranked pairs (by C-score) have fewer C pairs than a random draw, at all K from 10 through 500. This is confirmed by both the observed OR < 1 and the permutation test (all p > 0.89).

By contrast, the S-score achieves 80% precision at K=10 (OR=76.9, p<0.0001), confirming the framework's ranking mechanism works well for the structural class.

**The framework does not preferentially rank C-class links, at any granularity.**
