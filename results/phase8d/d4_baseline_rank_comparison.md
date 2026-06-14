# D4: Baseline Comparison Using Rank-Based Metrics

**Date**: 2026-06-13

---

## Baselines

| ID | Name | Score | C-score interpretation |
|----|------|-------|----------------------|
| Framework | Current-velocity | class_prob_C | z-mediated partial correlation change |
| B3 | Pairwise correlation | \|corr(y_i, y_j)\| averaged across 5 runs | Shared co-activity |
| B5 | State-ΔCorr | \|corr(y\|z_high) − corr(y\|z_low)\| | Direct state-dependent co-activity change |
| B6 | Module oracle | 1 if same module, 0 otherwise | Known module membership |

B4 (GraphicalLasso) is excluded — it fell back to B2 (uniform) in Phase 8B and has no meaningful score distribution.

---

## Target: C Class (n=857, base_rate=0.0866)

### AUROC

| Method | C-AUROC |
|--------|---------|
| Framework (c_score) | 0.4484 |
| Framework (lr_score) | 0.4512 |
| B3 (correlation) | 0.5314 |
| B5 (state-ΔCorr) | **0.5517** |
| B6 (module oracle) | 0.6170 |

B5 achieves the highest C-AUROC (0.5517). B3 also exceeds chance (0.5314). The framework is the only method below chance.

### Top-K Enrichment for C

| Method | k=10 OR | k=20 OR | k=50 OR | k=50 p | k=100 OR | k=100 p | prec@50 |
|--------|---------|---------|---------|-------|---------|-------|---------|
| Framework | 0.000 | 0.000 | 0.000 | 1.000 | 0.324 | 0.995 | 0.000 |
| B3 (corr) | — | — | **2.657** | **0.010** | **2.319** | **0.002** | **0.200** |
| B5 (dCorr) | — | — | 0.917 | 0.635 | 0.862 | 0.728 | 0.080 |
| B6 (module) | — | — | **3.365** | **0.001** | **1.808** | **0.051** | **0.240** |

**Key finding**: B3 (simple pairwise correlation) and B6 (module oracle) both achieve statistically significant C-enrichment at k=50, while the framework has zero C pairs in top-50. B5 (the best by AUROC) achieves below-chance enrichment at top-50 (OR=0.917) despite a higher AUROC — this is a metric dissociation discussed further in D5.

---

## Target: LR Class (C+M, n=946, base_rate=0.0956)

### AUROC

| Method | LR-AUROC |
|--------|---------|
| Framework (lr_score) | 0.4197 |
| B3 (correlation) | 0.5327 |
| B5 (state-ΔCorr) | 0.5503 |
| B6 (module oracle) | 0.6383 |

### Top-K Enrichment for LR

| Method | k=50 OR | k=50 p | k=100 OR | prec@50 |
|--------|---------|-------|---------|---------|
| Framework | 0.000 | 1.000 | 0.290 | 0.000 |
| B3 (corr) | **3.015** | **0.003** | **2.523** | **0.240** |
| B5 (dCorr) | 0.822 | 0.710 | 0.891 | 0.080 |
| B6 (module) | **4.106** | **0.000** | **2.316** | **0.300** |

B3 achieves 24% precision at k=50 for LR (vs 9.6% base rate = 2.5× enrichment). B6 achieves 30% precision at k=50 (vs base rate = 3.1× enrichment). Framework achieves 0%.

---

## Target: S Class (n=497, base_rate=0.0502)

### AUROC

| Method | S-AUROC |
|--------|---------|
| Framework (s_score) | **0.8531** |
| B3 (correlation) | 0.5130 |
| B5 (state-ΔCorr) | 0.4615 |
| B6 (module oracle) | 0.6838 |

### Top-K Enrichment for S (using s_score for framework, corr for B3)

| Method | k=50 OR | k=50 p | prec@50 |
|--------|---------|-------|---------|
| Framework (s_score) | **21.572** | **0.000** | **0.520** |
| B3 (corr) | 1.209 | 0.472 | 0.060 |
| B5 (dCorr) | 1.650 | 0.245 | 0.080 |
| B6 (module) | 2.599 | 0.046 | 0.120 |

For S detection, the framework completely dominates: OR=21.6 at k=50 with 52% precision, compared to B3 at 6% precision (near base rate).

---

## Do AUROC and Top-K Tell the Same Story?

### For C/LR detection:

| Method | C-AUROC | top-50 OR | Consistent? |
|--------|---------|---------|-----------|
| Framework | 0.4484 | 0.000 | ✓ (both fail) |
| B3 | 0.5314 | 2.657 | ✓ (both succeed) |
| B5 | 0.5517 | 0.917 | **✗ (AUROC > chance, but OR < 1)** |
| B6 | 0.6170 | 3.365 | ✓ (both succeed) |

**AUROC and top-k are NOT consistent for B5.** B5 achieves the best C-AUROC (0.5517) but below-chance top-50 enrichment (OR=0.917). This dissociation occurs because:
- B5's signal (|ΔCorr|) distinguishes C from N across the full rank distribution (hence positive AUROC)
- But the signal is weak at the very top — many S pairs also have high |ΔCorr| because direct connections create strong state-dependent co-activity
- At k=50, the top positions by |ΔCorr| are filled with strong state-sensitive links that include many S pairs and non-C links, diluting C enrichment

### For S detection:
All metrics agree: framework S-score achieves the best AUROC AND the best top-k enrichment.

---

## Summary Table

| Method | C-AUROC | C top-50 prec | S-AUROC | S top-50 prec |
|--------|---------|-------------|---------|-------------|
| Framework | 0.4484 | **0.000** | **0.8531** | **0.520** |
| B3 (corr) | 0.5314 | **0.200** | 0.513 | 0.060 |
| B5 (ΔCorr) | **0.5517** | 0.080 | 0.462 | 0.080 |
| B6 (module) | 0.6170 | **0.240** | 0.684 | 0.120 |

The framework dominates on S detection at any metric. It underperforms even simple baselines (B3, B6) on C detection at every metric. B3 (correlation) outperforms the framework on C top-k enrichment with a much simpler computational approach.

---

## Conclusion

- The framework beats all baselines on S-class detection (AUROC and top-k).
- The framework is beaten by B3 and B6 on C-class detection (both AUROC and top-k).
- B5 (state-ΔCorr) achieves the best C-AUROC but not the best top-k precision — the B5 signal is diffuse, not concentrated at top ranks.
- B3 (pairwise correlation) achieves better C top-k enrichment than B5, suggesting that correlated co-activity (regardless of state-dependency) is a stronger signal for C recovery than state-differential correlation — at least in the top-ranked pairs.
- AUROC and top-k tell the same qualitative story for the framework (fails on C, succeeds on S), but diverge for B5 (AUROC above chance, top-k not significantly enriched).
