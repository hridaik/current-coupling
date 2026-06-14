# F4: Off-Connectome Organization in Top-K Framework Predictions

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**Off-connectome definition**: DIRECT(i,j) = 0 in A_sparse (obs-submatrix)  
**State-modulated off-connectome**: DIRECT=0 AND SAREACHABLE=1 (= C class)

---

## Core Question

The paper targets pairs that are:
1. Off-connectome (DIRECT=0) ← necessary but not sufficient
2. State-modulated (SAREACHABLE=1, observable |ΔCorr| significant)

The framework's top-K has already shown 100% N at k=10,20,50. N pairs are also off-connectome (DIRECT=0) but NOT state-modulated (SAREACHABLE=0).

This section disentangles: is the framework recovering "off-connectome" in a broad sense, or specifically the state-modulated subset?

---

## Off-Connectome Fraction in Top-K

| k | Off-connectome (DIRECT=0) | On-connectome (DIRECT=1) | % Off-connectome |
|---|--------------------------|--------------------------|-----------------|
| 10 | 10 | 0 | **100%** |
| 20 | 20 | 0 | **100%** |
| 50 | 50 | 0 | **100%** |
| 100 | 98 | 2 | **98%** |

All top-50 pairs are off-connectome. This appears to suggest "off-connectome detection" — but:

---

## SAREACHABLE (State-Modulated) Fraction in Top-K

| k | SAREACHABLE=1 (C or M) | SAREACHABLE=0 | % SAREACHABLE |
|---|------------------------|---------------|--------------|
| 10 | 0 | 10 | **0%** |
| 20 | 0 | 20 | **0%** |
| 50 | 0 | 50 | **0%** |
| 100 | 3 | 97 | **3%** (vs base rate 9.56%) |

**The top-50 pairs are 100% off-connectome AND 0% SAREACHABLE.** They are all N-class pairs: off the structural connectome but with no state-active H2 relay. The framework is selecting within the off-connectome region, but the wrong sub-region.

---

## Why Does the Framework Select Off-Connectome Pairs?

The framework's S-score is driven by PCor_cond = z-conditioned partial correlation. Direct structural connections (DIRECT=1) create strong partial correlations that drive PCor_cond and S-score high. High S-score → low C-score (due to softmax anti-correlation ρ=−0.997).

Therefore:
- On-connectome (DIRECT=1) pairs → high S-score → low C-score → ranked LAST
- Off-connectome (DIRECT=0) pairs → low S-score → high C-score → ranked FIRST

This means the "off-connectome" property in the top-K is a **byproduct of the S/C softmax competition**, not genuine detection of off-connectome organization. The framework cannot distinguish C (off-connectome + state-modulated) from N (off-connectome, not state-modulated) within the off-connectome pool.

---

## Where Do C Pairs Rank?

| Metric | Value |
|--------|-------|
| C-pair rank (mean) | 5,617 / 9,900 |
| C-pair rank (median) | **5,674** / 9,900 |
| C-pair rank (p10) | 1,302 |
| C-pair rank (p90) | 8,879 |

C pairs are ranked **at the bottom half** of the distribution. Their median rank is 5,674 — near the midpoint — but the p90 is 8,879, meaning the top-10% state-dependent C pairs are ranked near the bottom 10% overall.

The first C-labeled pair appears at rank **71** out of 9,900. The first S-labeled pair appears at rank **62**. Out of 9,900 pairs, only 3 C pairs appear in the top-100.

---

## Top-K Framework Pairs vs. Top-K C Pairs (by |ΔCorr|)

| Property | Top-50 by C-score | Top-50 C-class pairs (by |ΔCorr|) |
|----------|-----------------|----------------------------------|
| Labels | 100% N | 100% C |
| Off-connectome | 100% (DIRECT=0) | 100% (DIRECT=0) |
| SAREACHABLE | 0% | 100% |
| Direct connection | 0% | 0% |
| Mean |ΔCorr| | 0.0455 | ~0.090+ |
| Mean C-score | 0.2534 | ~0.243 (ranked ~5000–9000) |

Both sets are off-connectome by structural definition. The key distinction:
- Top-50 by C-score: N-labeled, no H2 relay, low state signal
- Top-50 C pairs by |ΔCorr|: C-labeled, H2 relay exists, stronger state signal

The framework cannot distinguish them. Worse: it ranks the C subset **below** the N subset.

---

## N vs. C Within the Off-Connectome Pool

The benchmark has 9,314 off-connectome pairs (DIRECT=0): 857 C, 8,457 N.

| Subset | n | Mean C-score | Mean |ΔCorr| |
|--------|---|-------------|------------|
| Off-connectome C (SAREACHABLE) | 857 | 0.2425 | 0.0517 |
| Off-connectome N (not SAREACHABLE) | 8,457 | 0.2444 | 0.0468 |

Within the off-connectome pool, N pairs score HIGHER on C-score than C pairs (0.2444 vs 0.2425). The framework cannot distinguish C from N within their shared off-connectome region — and if anything, it ranks N above C.

---

## Path Length Analysis

All N pairs in the top-K have path_strength = 0.000 (no H2-mediated path exists). The C pairs that do appear (at ranks 71, ~80, ~90) have path_strength values corresponding to weak-to-moderate H2 relay — but path_strength is negatively correlated with C-score within the C class (ρ=−0.187, p=3.7×10⁻⁸), meaning the framework ranks lower path_strength C pairs slightly higher.

---

## Conclusion

The framework's top-K by C-score is **off-connectome but not state-modulated**:

1. Top-50 is 100% DIRECT=0 — off the structural connectome (this appears correct superficially)
2. Top-50 is 0% SAREACHABLE — no state-active H2 path in any top-50 pair
3. The "off-connectome" property is an artifact of the S/C softmax competition: DIRECT=1 pairs have high S-score and thus low C-score
4. Within the off-connectome pool (N and C together), the framework ranks N above C (0.2444 vs 0.2425 mean C-score)

**The framework is NOT recovering off-connectome state-dependent organization. It is recovering off-connectome structurally-weak organization — a byproduct of the scoring architecture's anti-correlation between S and C.**
