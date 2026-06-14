# F3: State Dependence of Top-Ranked Pairs

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**State-dependence measure**: |ΔCorr|(i,j) = |corr(y|z>median) − corr(y|z≤median)|, averaged over 5 oracle_z runs  
**Interpretation**: Higher |ΔCorr| = more state-dependent co-activity

---

## Distributions of |ΔCorr|

### Global Reference

| Population | n | Mean |ΔCorr| | Median | Std | p10 | p90 |
|-----------|---|-------------|--------|-----|-----|-----|
| All pairs | 9900 | 0.0476 | — | — | — | — |
| C class | 857 | 0.0517 | — | — | — | — |
| Top-10% C class | 86 | **0.1137** | — | — | — | — |
| Top-K by C-score (K=10) | 10 | **0.0289** | — | — | — | — |
| Top-K by C-score (K=50) | 50 | **0.0455** | — | — | — | — |
| Top-K by C-score (K=100) | 100 | **0.0508** | — | — | — | — |

*Top-10% C class = top 86 C pairs by |ΔCorr| (the most worm-like subset)*

---

## Top-K by C-score vs. Reference Distributions

| k | Mean |ΔCorr| | vs. All pairs | vs. C-class mean | MW p-value (top-k > all) | Top-10% C in top-k |
|---|------------|--------------|-----------------|----------------------|-------------------|
| 10 | **0.0289** | 0.61× | 0.56× | 0.9976 | 0 |
| 20 | **0.0339** | 0.71× | 0.66× | 0.9975 | 0 |
| 50 | **0.0455** | 0.96× | 0.88× | 0.6971 | 0 |
| 100 | **0.0508** | 1.07× | 0.98× | 0.1722 | 1 |

- At k=10: top-ranked pairs have **39% LOWER** |ΔCorr| than the average pair
- At k=50: top-ranked pairs have **4% lower** |ΔCorr| than the average pair
- MW test p-values all >> 0.05: top-k pairs are NOT significantly more state-dependent than random pairs
- At k=100: only 1 of the top-10% state-sensitive C pairs appears

---

## State Dependence Profile: Top-10 Pairs

```
Pair       Label |ΔCorr|  vs C-mean  |  Interpretation
--------- ----- -------- ----------  |-----------------
(51,71)   N     0.0493   0.95×       |  near-average N pair
(32,64)   N     0.0223   0.43×       |  below-average N pair
(64,32)   N     0.0223   0.43×       |  below-average N pair
(64,22)   N     0.0167   0.32×       |  weak state signal
(22,64)   N     0.0167   0.32×       |  weak state signal
(45,51)   N     0.0269   0.52×       |  weak state signal
(70,22)   N     0.0135   0.26×       |  very weak state signal
(51,45)   N     0.0269   0.52×       |  weak state signal
(51,88)   N     0.0337   0.65×       |  below-average
(22,28)   N     0.0605   1.17×       |  slightly above average
```

7 of the top-10 C-scored pairs have |ΔCorr| below the C-class mean. None are among the most state-sensitive pairs. They are N-labeled pairs with moderate-to-weak state signal.

---

## State Dependence of the C Class vs. Framework Ranking

| Subset | n | Mean |ΔCorr| | Mean C-score | C-score rank (median) |
|--------|---|------------|-------------|----------------------|
| C ∩ state-sensitive (top |ΔCorr| quartile) | 252 | 0.085+ | 0.2421 | ~5800 |
| C ∩ state-invariant (bottom |ΔCorr| quartile) | 166 | 0.027− | 0.2431 | ~5400 |
| N ∩ state-invariant | ~2114 | 0.020− | **0.2457** | ~4100 |

The framework preferentially ranks state-INVARIANT N pairs higher than state-SENSITIVE C pairs. Among N pairs, those with lower |ΔCorr| (less state-dependent) receive higher C-scores on average.

---

## Top-K by |ΔCorr| vs. Top-K by C-score (State-Sensitivity Oracle vs. Framework)

| Criterion | Top-10 mean |ΔCorr| | % C-labeled | % N-labeled |
|-----------|------------|------------|------------|
| Top-10 by C-score | 0.0289 | **0%** | **100%** |
| Top-10 by |ΔCorr| (all classes) | 0.255+ | (mixed S,C,N) | — |
| Top-10 C pairs by |ΔCorr| | 0.114+ | **100%** | 0% |

The framework's top-10 and the oracle top-10 C pairs are completely disjoint.

---

## Direction of Effect

The critical finding from Phase 8D (confirmed here):

**State-sensitivity is NEGATIVELY associated with C-score.**

| Quantity | Spearman ρ with C-score | p-value |
|---------|------------------------|---------|
| |ΔCorr| (all pairs) | **−0.140** | 1.04×10⁻⁴⁴ |
| |ΔCorr| (within C-class only) | **−0.162** | 1.79×10⁻⁶ |

The framework is not neutral to state-sensitivity — it is inversely sensitive. The pairs it places at the top (N-labeled, low |ΔCorr|) are systematically more state-INVARIANT than average. The pairs it places at the bottom of C-score ranking include the most state-SENSITIVE C pairs.

---

## Conclusion

**The framework's top-K by C-score does NOT select state-dependent pairs.**

1. Top-10 mean |ΔCorr| = 0.0289, which is 39% BELOW the global mean and 44% below the C-class mean.
2. None of the top-10% state-sensitive C pairs appear in the top-50 by C-score (only 1 appears in top-100).
3. The Mann-Whitney test for "top-K is more state-dependent than a random sample" fails at every k ≤ 50 (p > 0.69).
4. State-sensitivity (|ΔCorr|) is significantly NEGATIVELY correlated with C-score (ρ=−0.140, p=10⁻⁴⁴).

The framework is recovering pairs with BELOW-AVERAGE state-dependent signal. It is anti-selecting for the biological target property.
