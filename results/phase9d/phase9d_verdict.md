# Phase 9D — Stage 6: Blinded Verdict

**Date:** 2026-06-14  
**Evaluation hash:** `77d7a3a6820b95d5...`  
**Thresholds:** Frozen in Phase 9B, verified in Phase 9D preflight

---

## Frozen Thresholds (verbatim)

```
SUCCESS: Precision@50 ≥ 0.25  AND  ρ_Spearman ≥ 0.40  AND  PMC_AUROC ≥ 0.75
PARTIAL: at least one primary metric ≥ partial threshold
FAILURE: all primary metrics below partial thresholds

Partial thresholds: Precision@50 ≥ 0.10, ρ ≥ 0.15, PMC_AUROC ≥ 0.60
```

---

## Threshold Evaluation

### Primary Metric Outcomes

| Metric | Observed | Success Threshold | Success? | Partial Threshold | Partial? |
|--------|----------|------------------|----------|------------------|----------|
| PMC_AUROC | 0.7943 | ≥ 0.75 | **YES** | ≥ 0.60 | YES |
| ρ_Spearman | 0.1899 | ≥ 0.40 | **NO** | ≥ 0.15 | YES |
| Precision@50 | 0.920 | ≥ 0.25 | **YES** | ≥ 0.10 | YES |

### Verdict Logic

```
SUCCESS requires: ALL THREE at success threshold → NOT MET (ρ = 0.19 < 0.40)
PARTIAL requires: at least one at partial threshold → MET (all three ≥ partial)
FAILURE requires: ALL THREE below partial threshold → NOT MET
```

---

## VERDICT: PARTIAL

**Two of three primary metrics achieve the SUCCESS threshold.**  
**All three primary metrics achieve the PARTIAL threshold.**  
**One metric (ρ_Spearman) falls below the SUCCESS threshold.**

---

## Per-Metric Assessment

**PMC_AUROC = 0.7943 — SUCCESS**  
The framework successfully discriminates PMC pairs from non-PMC pairs at the AUROC level. Performance is significantly above the best non-oracle baseline (B3: 0.497) and above the success threshold (0.75).

**ρ_Spearman = 0.190 — PARTIAL (not SUCCESS)**  
The framework's ranking is positively correlated with the oracle (p = 2.6×10⁻⁸⁵), substantially better than all baselines (best: B1 at +0.013). However, the ranking is not tight enough across the full range of 10,433 pairs to reach ρ = 0.40. This is mechanistically consistent with the design: the framework estimates D from the Lyapunov residual using a first-order approximation (diagonal extraction), introducing noise in the continuous ranking even while correctly identifying the top PMC pairs.

**Precision@50 = 0.920 — SUCCESS**  
46 of the top-50 ranked pairs are PMC, far exceeding the success threshold (0.25) and the best non-oracle baseline (B3: 0.380). Precision@20 = 1.000 (perfect top-20 recovery). The framework concentrates PMC pairs at the top of the ranking with high fidelity.

---

## No Post-Hoc Adjustments

This verdict is applied directly from the pre-registered frozen thresholds. No threshold changes, no relabeling, no new metrics were introduced. The verdict is PARTIAL.

---

## Status

STAGE 6 COMPLETE. VERDICT: **PARTIAL**. Proceed to final summary.
