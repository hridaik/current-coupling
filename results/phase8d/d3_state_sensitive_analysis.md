# D3: State-Sensitive Analysis

**Metric**: |ΔCorr| = |corr(y_i, y_j | z > median) - corr(y_i, y_j | z ≤ median)|  
**Data**: 5 oracle_z runs (z available for state splitting)  
**Date**: 2026-06-13

---

## Setup

State sensitivity is measured by the absolute change in pairwise correlation across z-states:

```
state_sensitivity(i, j) = | corr(y_i, y_j | z > median) − corr(y_i, y_j | z ≤ median) |
```

Averaged across 5 oracle_z runs. This is the empirical B5 signal — the same quantity used by the B5 (state-ΔCorr) baseline.

| Percentile | State sensitivity value |
|-----------|------------------------|
| 25th (p25) | 0.0298 |
| 75th (p75) | 0.0585 |

Pairs with state_sensitivity ≥ p75 are classified **sensitive** (top quartile); ≤ p25 are **invariant** (bottom quartile).

---

## Distribution of Class Labels Across State-Sensitivity Bins

| Class | n | In sensitive quartile | Expected (25%) | Enrichment |
|-------|---|----------------------|----------------|------------|
| C | 857 | 252 (29.4%) | 214 (25%) | 1.18× |
| M | 89 | 29 (32.6%) | 22 (25%) | 1.30× |
| S | 497 | 95 (19.1%) | 124 (25%) | **0.76×** |
| N | 8457 | 2099 (24.8%) | 2114 (25%) | ~1.0× |

**Key finding**: C and M pairs are over-represented in the state-sensitive quartile (1.18× and 1.30× enrichment respectively). S pairs are under-represented (0.76×). This confirms that the ground-truth labels are *ecologically valid* — SAREACHABLE links genuinely produce more state-dependent correlation than structural links. The benchmark's z-driven structure produces detectable state sensitivity.

---

## Framework C-Score Performance by State-Sensitivity Subset

| Subset | n | C-AUROC | Interpretation |
|--------|---|---------|---------------|
| C (state-sensitive, top quartile) | 252 | **0.3935** | Worse than overall C |
| C (state-invariant, bottom quartile) | 166 | **0.5276** | Slightly above chance |
| C (all) | 857 | 0.4484 | Overall framework result |

**Critical finding**: The framework performs *better* on state-INVARIANT C pairs (AUROC=0.5276) than state-SENSITIVE C pairs (AUROC=0.3935). This is the opposite of what a state-sensitive detector should show.

A framework that correctly exploits z-mediated structure would score higher for C pairs in the state-sensitive quartile (where the H2-mediated z-correlation is strongest). Instead, the framework is most anti-informative precisely for those C pairs that exhibit the strongest state-dependent behavior.

---

## Top-K Enrichment by C-Score

| Subset | k=50 OR | k=50 p | k=100 OR | k=200 OR |
|--------|---------|-------|---------|---------|
| C ∩ sensitive | 0.000 | 1.000 | 0.384 | 0.981 |
| C ∩ invariant | 0.000 | 1.000 | 0.000 | 0.587 |
| State-sensitive (all classes) | 0.749 | 0.826 | 1.111 | 1.000 |
| S | 0.000 | 1.000 | 0.189 | 0.188 |

No enrichment for any C subset in top-50. The "sensitive_all" category (all pairs in state-sensitive quartile, regardless of class) shows near-chance enrichment in top-100 (OR=1.111) — the framework does not specifically rank state-sensitive pairs at the top.

---

## Using State Sensitivity as a Score (B5 Oracle)

If state_sensitivity = |ΔCorr| is used directly as a C-score:

| Metric | Value | vs Framework |
|--------|-------|-------------|
| C-AUROC from |ΔCorr| | 0.5517 | +0.103 |
| B5 top-50 precision for C | 0.080 | vs 0.000 (framework) |
| B5 top-50 OR for C | 0.917 | vs 0.000 (framework) |

The |ΔCorr| signal itself has C-AUROC=0.5517 — above chance, and the best C-AUROC of any method. However, even this oracle-adjacent signal doesn't produce significant top-50 enrichment for C (OR=0.917, p=0.635). The AUROC advantage of B5 over chance is spread across the full ranking distribution, not concentrated at the top.

---

## Mechanism Interpretation

The pattern is consistent with the following mechanism:

1. **State-sensitive C pairs** have strong z-mediated correlation in the raw y signal. When the framework regresses z out of y to get y_resid, it removes this correlation. PCor_cond for these pairs (estimated from y_resid) is then similar to N pairs — the z-regression removes the distinguishing signal.

2. **State-invariant C pairs** have weaker z-mediated correlation but stronger structural H2-path correlation that persists after z-regression (because H2 affects y through structural paths independently of z). PCor_cond for these pairs retains some H2-path-mediated structure, making them slightly distinguishable from N pairs.

3. The framework's z-regression step transforms the most detectable C pairs (state-sensitive) into the hardest-to-detect pairs. The architecture actively degrades the signal it is trying to exploit.

---

## Conclusion

The framework does **not** preferentially identify state-dependent organization:

- State-sensitive C pairs (the biologically most relevant subset) have the *lowest* C-AUROC (0.3935).
- State-invariant C pairs (structurally connected via H2 but weakly z-modulated) have slightly above-chance C-AUROC (0.5276).
- Top-k enrichment for state-sensitive C is zero at k=50 and below chance at k=100 and k=200.
- The z-regression step in the framework removes state-dependent signal from the residuals, inverting the intended effect.

**The framework recovers structurally-embedded H2-path links (weakly), not state-dependent links. The architecture is sensitive to the wrong signal.**
