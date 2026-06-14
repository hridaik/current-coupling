# Phase 8D Summary: Structure-of-Interest Evaluation

**Date**: 2026-06-13  
**Frozen verdict**: Phase 8B FAILURE (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197)  
**Phase 8C classification**: Architecture-limited failure

---

## The Four Questions

---

### Q1: Does the framework recover the full C class?

**No.**

| Metric | Value | Threshold / null |
|--------|-------|-----------------|
| C-AUROC | 0.4484 | < 0.50 (below chance) |
| C-AUPRC | 0.0756 | < 0.0866 (below base rate) |
| Precision@50 (C) | 0.000 | base rate = 0.087 |
| Precision@100 (C) | 0.030 | base rate = 0.087 |
| Enrichment OR@50 | 0.000 | null = 1.0 |
| Enrichment OR@100 | 0.324 | null = 1.0 |

Zero C pairs appear in the top-50 highest-scored positions (by C-score). The framework's C-score is anti-informative: pairs labeled C score systematically *lower* on the framework's C-dimension than pairs labeled N. All rank-based and global metrics confirm the framework cannot recover the C class.

---

### Q2: Does the framework recover a biologically relevant subset of current-supported / off-connectome organization?

**No.**

The investigation tested multiple subsets:
- **Strong C** (path_strength > median 0.027): C-AUROC=0.4069 — *more* anti-informative than the full C class
- **Weak C** (path_strength ≤ median): C-AUROC=0.4944 — nearest to chance, but still below
- **State-sensitive C** (|ΔCorr| in top quartile): C-AUROC=0.3935 — worst of all subsets
- **State-invariant C** (|ΔCorr| in bottom quartile): C-AUROC=0.5276 — only subset slightly above chance
- **M class** (C+S simultaneously): C-AUROC=0.1518 — severely anti-informative
- **LR (C+M)**: C-AUROC=0.4168

No biologically motivated subset yields top-k enrichment above chance. At k=50, every C subset has zero representation in the top-ranked positions.

The framework is slightly less wrong for state-INVARIANT C pairs (AUROC=0.5276) — links with structural H2-path correlation that persists after z-regression. But this is not the biologically relevant subset; it is the subset where the z-mediated state signal is weakest.

---

### Q3: Does the framework preferentially recover state-dependent organization?

**No — and the relationship is inverted.**

| Subset | C-AUROC |
|--------|---------|
| C ∩ state-sensitive (|ΔCorr| ≥ p75) | **0.3935** (worst) |
| C ∩ state-invariant (|ΔCorr| ≤ p25) | **0.5276** (best) |
| C overall | 0.4484 |

State-sensitive C pairs — those with the strongest empirical state-dependent co-activity change — receive the *lowest* C-scores from the framework. The framework's z-regression step removes the z-correlated variance from y, which is precisely the signal that makes state-sensitive C pairs detectable. After this removal, the state-sensitive C pairs look more like N pairs (in y_resid) than before the regression.

The framework is preferentially recovering state-*invariant* C links — not because it detects state invariance, but because those links retain some structural H2-path correlation even after z is regressed out.

---

### Q4: Is AUROC the right summary metric here?

**AUROC is an appropriate metric; precision@k is the more operationally relevant metric.**

| Metric | For C class | For S class | Agreement |
|--------|------------|------------|----------|
| AUROC | 0.4484 (fail) | 0.8531 (succeed) | ✓ |
| AUPRC | 0.0756 (fail) | 0.3205 (succeed) | ✓ |
| Precision@50 | 0.000 (fail) | 0.520 (succeed) | ✓ |
| Enrichment OR@50 | 0.000 (fail) | 21.572 (succeed) | ✓ |

All metrics tell the same qualitative story for this framework. AUROC does not mask or distort the failure — it correctly represents the anti-informative C-ranking.

**However**, precision@k at small k (≤50) provides the sharpest operationally relevant characterization: *zero* C pairs in the top 50 highest-confidence predictions makes the failure concrete, not just statistical. For any experimental follow-up use case, precision@k is the most directly interpretable metric.

For a future framework aiming at off-connectome state-dependent organization, **precision@50 ≥ 0.20** (2.3× enrichment, matching B3's performance) should be the minimum success criterion — not just AUROC > 0.65.

---

## Classification

**A: No useful recovery of the organization of interest.**

**Quantitative justification**:

1. Zero C pairs in top-50 (and zero in top-20 and top-10) by any framework score.
2. C-AUROC=0.4484, AUPRC=0.0756 — both below chance level.
3. The biologically most relevant subset (strong C, state-sensitive C) is systematically the hardest case for the framework, not the easiest.
4. Simple baselines (B3: correlation, B6: module oracle) outperform the framework on C top-k enrichment: B3 achieves precision@50=0.200 (OR=2.657, p=0.010) vs framework's 0.000.
5. Even under the most favorable tested conditions (Phase 8C positive control: GAMMA_H2=12×, THETA_Z=10× slower), C-AUROC=0.4837 — still below chance.

The framework successfully recovers structural connectivity (S-AUROC=0.853, precision@50=0.52, OR=21.6) but achieves no useful recovery of the off-connectome, state-dependent organization that is the primary biological target.

---

## Diagnosis

The failure is architectural, not signal-limited:

| Root cause | Evidence |
|-----------|---------|
| z-regression removes C signal | State-sensitive C pairs have lowest C-AUROC (0.3935) |
| Delta_PCor does not detect H2-mediated paths | C-AUROC at k=0 active H2 (0.4425) ≈ C-AUROC at k=8 (0.4484) |
| Framework insensitive to signal strength | 24× variation in GAMMA_H2 moves C-AUROC by only 0.020 |
| C pairs structurally anti-correlated with C-score | C-AUROC < 0.50 means H2 topology suppresses Delta_PCor |

The framework's C-score (Delta_PCor = |PCor_raw − PCor_cond|) is negatively correlated with C-class membership. This is a principled architectural failure: z-regression removes the z-mediated component from y_resid, making PCor_cond for C pairs look structurally similar to PCor_cond for N pairs. The difference Delta_PCor is then determined by structural properties of the H2-topology that are shared by both C and N pairs, with C pairs receiving LOWER Delta_PCor due to structural differences in how H2 connectivity affects precision estimation.

---

## Implications

For future frameworks targeting off-connectome state-dependent organization:

1. **Do not regress z out of y before computing covariance.** Z-regression removes the very signal that distinguishes C from N. Instead, use z as an instrument — compute the conditional distribution of y given z, and look for pairs whose conditional distribution changes.

2. **Use z as an intervention signal.** The correct quantity is: compare the *correlation structure* of y at different z values, not the *correlation of y residuals* after z is removed. B5 (|ΔCorr|) is a better proxy for this, achieving C-AUROC=0.5517.

3. **Address the precision matrix estimation challenge.** With n/p=480 (48,000 timesteps, 100 neurons), the regularized precision matrix estimation is high-variance. The Delta_PCor quantity requires estimating two high-dimensional matrices and computing their difference — a task highly sensitive to finite-sample noise.

4. **Consider directed causal inference more explicitly.** The C class represents a directed influence path (i → H2 → j) that the lag-1 asymmetry should in principle detect. The current lag-1 asymmetry (Current_norm) is used for S-scoring but not for C-scoring. A C-score based on directed current magnitude (not just correlation change) might better identify the directed H2-mediated paths.

---

## Deliverables

| File | Status |
|------|--------|
| results/phase8d/context_recovery_note.md | COMPLETE |
| results/phase8d/d1_topk_current_enrichment.md | COMPLETE |
| results/phase8d/d2_structure_of_interest_enrichment.md | COMPLETE |
| results/phase8d/d3_state_sensitive_analysis.md | COMPLETE |
| results/phase8d/d4_baseline_rank_comparison.md | COMPLETE |
| results/phase8d/d5_metric_calibration.md | COMPLETE |
| results/phase8d/analysis_results.json | COMPLETE |
| phase8d_summary.md | COMPLETE |
