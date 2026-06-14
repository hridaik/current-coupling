# F2: Class Composition of Top-K Framework Predictions

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**Ranking**: C-score (class_prob['C']) descending

---

## Base Rates (Global)

| Class | n | Base rate |
|-------|---|-----------|
| S | 497 | 5.02% |
| C | 857 | 8.66% |
| M | 89 | 0.90% |
| N | 8457 | 85.43% |
| LR (C+M) | 946 | 9.56% |

Total: 9900 directed pairs

---

## Class Composition at Top-K

| k | S (obs/exp/%) | C (obs/exp/%) | M (obs/exp) | N (obs/exp/%) | LR (obs/exp) |
|---|--------------|--------------|------------|--------------|-------------|
| 10 | 0/0.50 (0%) | 0/0.87 (0%) | 0/0.09 | **10/8.54 (100%)** | 0/0.96 |
| 20 | 0/1.00 (0%) | 0/1.73 (0%) | 0/0.18 | **20/17.09 (100%)** | 0/1.91 |
| 50 | 0/2.51 (0%) | 0/4.33 (0%) | 0/0.45 | **50/42.71 (100%)** | 0/4.78 |
| 100 | 1/5.02 (1%) | 3/8.66 (3%) | 0/0.90 | **96/85.43 (96%)** | 3/9.56 |

---

## Enrichment Odds Ratios and Permutation P-values

### N-class enrichment in top-K

| k | N observed | N expected | Enrichment OR | p-value |
|---|-----------|-----------|--------------|---------|
| 10 | 10 | 8.54 | 1.71 | 0.2033 |
| 20 | 20 | 17.09 | **3.41** | **0.0421** |
| 50 | 50 | 42.71 | **8.53** | **0.0001** |
| 100 | 96 | 85.43 | **4.10** | **0.0006** |

N-class is significantly enriched in top-50 (OR=8.53, p=0.0001) and top-100 (OR=4.10, p=0.0006). At top-50: the probability of observing 50/50 N-labeled pairs by chance is p=0.0001.

### C-class depletion in top-K

| k | C observed | C expected | Depletion OR | p-value |
|---|-----------|-----------|-------------|---------|
| 10 | 0 | 0.87 | 0.000 | 1.000 |
| 20 | 0 | 1.73 | 0.000 | 1.000 |
| 50 | 0 | 4.33 | 0.000 | 1.000 |
| 100 | 3 | 8.66 | **0.326** | **0.992** |

C-class is completely depleted from top-10, top-20, top-50 (OR=0.000, p=1.000). At top-100, C appears 3 times vs expected 8.66 (OR=0.326, p=0.992). The framework ranks C pairs below chance at every k tested.

### S-class depletion in top-K

| k | S observed | S expected | Depletion OR | p-value |
|---|-----------|-----------|-------------|---------|
| 10 | 0 | 0.50 | 0.000 | 1.000 |
| 20 | 0 | 1.00 | 0.000 | 1.000 |
| 50 | 0 | 2.51 | 0.000 | 1.000 |
| 100 | 1 | 5.02 | 0.191 | 0.994 |

S-class is also completely depleted from top-50, even though S detection (by S-score ranking) is the framework's strongest signal. The explanation: S pairs have high S-scores and low C-scores — they are near the bottom of the C-score ranking.

---

## What These Numbers Mean

### At k=50: The framework's top 50 by C-score are 100% N-labeled.

- Expected N under null: ~43 out of 50
- Observed: 50 out of 50
- OR=8.53, p=0.0001
- Expected C under null: ~4.3 out of 50
- Observed: **0** out of 50

### At k=100: 96% N, 3% C, 1% S.

The first C-labeled pair appears at rank **71** (out of 9900). The first S-labeled pair appears at rank **62** — as a result of the C-score anti-correlation with S-pairs, a structural pair appears earlier than any C pair.

### Score Margin:

The highest C-score in the entire dataset is **0.2570** (pair (51,71), N-labeled). The maximum theoretically possible C-score approaches 1.0 if the framework had detected a clear C pair. Instead:
- Highest C-score = 0.2570 (N pair, maximum entropy)
- N-class mean C-score = 0.2444
- C-class mean C-score = 0.2425
- S-class mean C-score = 0.2207

The N-class sits at the top of the C-score distribution. The C-class scores **below** the N-class. The S-class is lowest.

---

## C-score vs. S-score Anti-Correlation

The most important structural finding for understanding class composition:

| | C-score mean | S-score mean |
|--|-------------|-------------|
| S-class | 0.2207 | 0.3381 |
| C-class | 0.2425 | 0.2728 |
| N-class | 0.2444 | 0.2672 |
| M-class | 0.2209 | 0.3376 |

Spearman ρ(C-score, S-score) = **−0.997** (p ≈ 0)

The C-score and S-score are anti-correlated at ρ=−0.997. This is a consequence of softmax architecture with Temperature=5: the four logits sum-normalize to 1.0. When S-score (driven by PCor_cond) is high, C-score (driven by Delta_PCor) is necessarily depressed. The framework's scoring is near-zero-sum between S and C.

Result: The pairs with the highest C-scores are NOT the pairs with the largest Delta_PCor — they are the pairs with the LOWEST PCor_cond. N pairs, which have neither direct structural coupling nor H2-mediated coupling, have naturally low PCor_cond and thus naturally high C-scores by default.

---

## Summary

| Target class | Top-50 result | Interpretation |
|-------------|--------------|---------------|
| N | 50/50 (100%), OR=8.53, p=0.0001 | Strongly enriched |
| C | 0/50 (0%), OR=0.000, p=1.000 | Completely absent |
| S | 0/50 (0%), OR=0.000, p=1.000 | Completely absent |
| M | 0/50, OR=0.000 | Completely absent |
| LR | 0/50, OR=0.000 | Completely absent |

**The framework's C-score ranking is not a detector for C pairs — it is a detector for N pairs with weak structural coupling, where maximum softmax uncertainty is reached.**
