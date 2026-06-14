# D5: Calibration / Metric Selection

**Question**: Is AUROC the right primary metric for this benchmark?  
**Date**: 2026-06-13

---

## Metric Comparison for Each Target Class

### C Class (n=857, base_rate=0.0866)

| Metric | Value | vs Null | Interpretation |
|--------|-------|---------|---------------|
| AUROC | 0.4484 | < 0.50 | Anti-informative; ranking inverted |
| AUPRC | 0.0756 | < 0.0866 (base) | Worse than random guess |
| Precision@10 | 0.000 | 0.000 | Zero C in top 10 |
| Precision@50 | 0.000 | 0.087 | Zero C in top 50 |
| Precision@100 | 0.030 | 0.087 | 3 C in top 100 (below base rate) |
| Precision@200 | 0.065 | 0.087 | 13 C in top 200 (below base rate) |
| Enrichment OR@50 | 0.000 | 1.000 | Depletion, not enrichment |
| Enrichment OR@100 | 0.324 | 1.000 | Significant depletion |

All metrics consistently indicate the framework fails to detect C. AUROC (0.4484) and precision@k tell the same story.

### LR Class (C+M, n=946, base_rate=0.0956)

| Metric | Value | vs Null |
|--------|-------|---------|
| AUROC | 0.4197 | < 0.50 |
| AUPRC | 0.0799 | < 0.0956 |
| Precision@50 | 0.060 | 0.096 |
| Precision@100 | 0.070 | 0.096 |
| Enrichment OR@50 | 0.603 | 1.000 |
| Enrichment OR@100 | 0.710 | 1.000 |

All metrics fail. LR is a harder target even than C alone because M pairs (direct=1, sareachable=1) are strongly predicted as S by the framework, pulling the ranking further away from LR.

### S Class (n=497, base_rate=0.0502)

| Metric | Value | vs Null | Interpretation |
|--------|-------|---------|---------------|
| AUROC | 0.8531 | >> 0.50 | Excellent |
| AUPRC | 0.3205 | >> 0.0502 (6.4× lift) | Excellent |
| Precision@10 | 0.800 | 0.050 | 16.0× enrichment |
| Precision@20 | 0.550 | 0.050 | 11.0× enrichment |
| Precision@50 | 0.520 | 0.050 | 10.4× enrichment |
| Precision@100 | 0.430 | 0.050 | 8.6× enrichment |
| Enrichment OR@10 | 76.9 | 1.000 | Highly significant |
| Enrichment OR@50 | 21.6 | 1.000 | Highly significant |

All metrics consistently indicate excellent S-class detection.

---

## AUROC vs Top-K: When They Disagree

The most important disagreement observed was in D4 for B5:
- B5 C-AUROC = 0.5517 (above chance)
- B5 top-50 precision@C = 0.080 (below base rate 0.087, OR=0.917, p=0.635)

This dissociation reveals a fundamental property of these metrics:

**AUROC** measures *global rank ordering quality* — it asks whether a randomly chosen C pair tends to score higher than a randomly chosen N pair. It is sensitive to all 857×8457 ≈ 7.2M pairs in the C/N comparison.

**Precision@k** measures *local rank quality at the top* — it asks whether the k highest-scoring pairs contain more C pairs than expected. It is sensitive only to the top k = 50 out of 9900 pairs.

For B5:
- The |ΔCorr| signal provides a weak C-vs-N discrimination spread across the entire ranking (hence AUROC > 0.5)
- But the top-50 by |ΔCorr| are dominated by pairs with strong state-dependent correlation — which includes many S, N, and cross-module pairs, diluting C enrichment at the top

This means **B5's C-signal is diffuse** (distributed throughout the ranking) rather than **concentrated** (present at the top).

---

## Which Metric Best Matches the Scientific Target?

The biological question is: **Can the framework identify a useful set of off-connectome state-dependent links for follow-up investigation?**

This framing maps naturally to **top-k precision and enrichment odds ratios**, not to AUROC:

| Criterion | Matched metric | Reason |
|-----------|---------------|--------|
| "Can identify a useful set" | Precision@k, enrichment OR | Experiments probe top-ranked candidates |
| "Off-connectome / C class" | C-class precision@k | The biological target is specific |
| "For follow-up investigation" | k ≤ 100 | Lab experiments validate a small set |
| "Global rank ordering quality" | AUROC | Less relevant to experimental follow-up |

For ranking-based experimental validation (the typical use case in biology), precision@k for small k is the most relevant metric. AUROC captures a different question: does the model produce correct relative rankings across the full dataset?

However, for this benchmark, both metrics agree on the main conclusion:
- **For C detection**: all metrics fail (AUROC < 0.50, precision@k below base rate, OR < 1)
- **For S detection**: all metrics succeed (AUROC=0.853, precision@10=0.80, OR=76.9)

---

## PR-AUC Comparison

| Class | PR-AUC | Base rate | Lift |
|-------|--------|-----------|------|
| C (c_score) | 0.0756 | 0.0866 | 0.873× |
| LR (lr_score) | 0.0799 | 0.0956 | 0.836× |
| S (s_score) | **0.3205** | 0.0502 | **6.384×** |

PR-AUC (area under precision-recall curve) confirms: C and LR are worse than random, S is excellent. PR-AUC is arguably the appropriate metric for imbalanced classes (C at 8.7%, S at 5.0%), and it tells the same story as AUROC here.

---

## Recommendation on Primary Metric

**For the current framework on the current benchmark:**
- AUROC is the correct primary metric for the benchmark's formal evaluation (as pre-specified in Phase 8A).
- AUROC and precision@k, AUPRC all tell the same qualitative story: the framework succeeds at S, fails at C.
- For future evaluations that prioritize experimental follow-up, precision@k for small k (e.g., k≤100) would be the more scientifically motivated primary metric.

**For re-evaluating the biological question** (does the framework identify the right kind of organization?):
- Precision@k and enrichment OR at small k are the most operationally relevant metrics.
- These give the same null result as AUROC for the framework: zero C pairs in top-50.

**Conclusion**: AUROC is not the wrong metric — it correctly identifies the failure. Precision@k amplifies the severity: zero C pairs in top-50 makes the failure concrete, not just statistical. Both metrics agree on the scientific verdict.
