# Phase 8A Metric Registry
**Status:** FROZEN — pre-registered before framework execution  
**Date:** 2026-06-13

All metrics are defined here in full before any framework output is observed. No metric may be added, removed, or redefined after framework evaluation begins.

---

## 0. Notation and Definitions

For a binary classification task (class k vs rest):
- **TP(k)**: true positives for class k
- **FP(k)**: false positives for class k
- **FN(k)**: false negatives for class k
- **TN(k)**: true negatives for class k
- **n(k)**: number of ground-truth positive pairs for class k
- **N_pairs = 9,900** total directed pairs
- **score(i,j,k)**: framework's probability output P(label=k | (i,j)) = class_prob[k]

Class counts (committed, from locked labels):

| Class | n | Fraction |
|-------|---|----------|
| S | 497 | 0.0502 |
| C | 857 | 0.0866 |
| M | 89 | 0.0090 |
| N | 8457 | 0.8543 |
| LR = C+M | 946 | 0.0955 |
| Direct = S+M | 586 | 0.0592 |

**LR (Latent-Regulated)** is defined as the event that SAREACHABLE=True, i.e., label ∈ {C, M}. This is the primary detection target of the current-velocity framework. The framework claims to detect pairs where H2-mediated state modulation creates functional influence.

**Direct** is defined as the event that DIRECT=True, i.e., label ∈ {S, M}.

---

## 1. Class-Level Metrics

Computed for each class k ∈ {S, C, M, N, LR, Direct} as one-vs-rest binary classification.

### M1: AUROC (Area Under the ROC Curve)

**Definition:**  
Let score(i,j,k) = class_prob[k] from the framework output. AUROC for class k is the probability that a randomly drawn positive pair (label=k) receives a higher score than a randomly drawn negative pair (label≠k).

**Formula:**  
```
AUROC(k) = (1 / (n(k) * n_neg(k))) * Σ_{pos} Σ_{neg} [score(pos,k) > score(neg,k)]
           + 0.5 * [score(pos,k) == score(neg,k)]
```

Computed via the trapezoidal rule on the ROC curve (sensitivity vs 1-specificity) at all score thresholds. Ties broken by averaging.

For **LR** class: score(i,j,LR) = class_prob['C'] + class_prob['M'].  
For **Direct** class: score(i,j,Direct) = class_prob['S'] + class_prob['M'].

**Interpretation:**  
- 1.0 = perfect separation  
- 0.5 = random  
- < 0.5 = worse than random (systematic mis-ranking)

**Failure mode:** Degenerate scores (all pairs receive same score) → AUROC = 0.5 exactly. This is reported as "random performance" not "failure."

**Rationale:** Threshold-free metric. Unaffected by threshold choice or class imbalance in the standard formulation. Selected as primary metric for this reason.

---

### M2: AUPRC (Area Under the Precision-Recall Curve)

**Formula:**  
At each score threshold τ, compute Precision(k,τ) = TP/(TP+FP), Recall(k,τ) = TP/(TP+FN). Integrate using linear interpolation (trapezoidal) over all thresholds.

Baseline AUPRC for random classifier = n(k)/N_pairs (class frequency).

AUPRC values are reported as **lift** = AUPRC(k) / baseline_AUPRC(k) for comparability across classes.

**Interpretation:**  
- Lift = 1.0 → random performance  
- Lift > 1.0 → above random  
- Class M has baseline AUPRC = 0.009; a lift of 3× means AUPRC = 0.027 — still a small absolute value

**Failure mode:** AUPRC is sensitive to class imbalance. For class M (n=89), confident wrong predictions near the decision boundary will produce sharp drops. Report alongside AUROC.

**Rationale:** Captures performance in the high-precision regime relevant to hypothesis testing about individual pairs. Complements AUROC for imbalanced classes.

---

### M3: F1 Score (at optimal threshold)

**Formula:**  
```
F1(k) = 2 * Precision(k) * Recall(k) / (Precision(k) + Recall(k))
```

Threshold is selected to **maximize F1 on the full evaluation set**. This threshold is chosen post-hoc (on evaluation data), which is a permitted operation since F1 is a secondary metric and the threshold is not used for any primary analysis.

**Failure mode:** Threshold selection on the same data used for evaluation inflates F1 relative to held-out performance. Acknowledged limitation; F1 is secondary only.

---

### M4: Precision at Optimal F1 Threshold

Reported jointly with M3.

### M5: Recall at Optimal F1 Threshold

Reported jointly with M3.

---

### Metric Computation for Each Class

| Metric | S | C | M | N | LR | Direct |
|--------|---|---|---|---|----|--------|
| M1 AUROC | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| M2 AUPRC (lift) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| M3 F1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| M4 Precision | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| M5 Recall | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 2. Global Metrics

### M6: Macro-AUROC

```
MacroAUROC = mean(AUROC(S), AUROC(C), AUROC(M), AUROC(N))
```

Unweighted mean over the four primary classes.

**Primary metric for the oracle_z success/failure determination (see phase8a_success_criteria.md).**

**Rationale:** Equal weight to each class regardless of size. Prevents N (majority class, n=8457) from dominating. This is appropriate since S, C, M, N represent qualitatively distinct link types, not a single spectrum.

---

### M7: Weighted-AUROC

```
WeightedAUROC = Σ_k [n(k)/N_pairs * AUROC(k)]
```

Class-frequency-weighted mean AUROC.

**Secondary metric.** Expected to be dominated by N and C due to their frequency.

---

### M8: Balanced Accuracy (at threshold)

```
BalancedAcc = (1/4) * Σ_k [TP(k) / n(k)]  (mean recall per class)
```

Threshold for multi-class prediction: use argmax of class_prob.

**Secondary metric.**

---

### M9: Confusion Matrix

4×4 matrix, rows = true label, columns = predicted label. Predicted label = argmax(class_prob).

Reported as counts and as fractions of row total (per-class recall profile).

**Exploratory metric.** Used for qualitative diagnosis of failure modes.

---

### M10: LR-AUROC

```
LR-AUROC = AUROC(LR)
```

Binary AUROC for detecting whether a pair is latent-regulated (SAREACHABLE=True).

This is the most direct test of the framework's core claim: that probability currents detect H2-mediated functional links. LR-AUROC > baseline is the pre-specified primary hypothesis test.

**LR-AUROC is a co-primary metric along with MacroAUROC.**

---

## 3. Calibration Metrics

These apply only if class_prob values are intended to represent calibrated probabilities (i.e., the framework declares its normalization_method is 'calibrated' in output metadata).

If normalization_method is 'softmax' or 'simplex_projection', calibration metrics are reported but cannot be used to assess the framework's classification ability (only its calibration quality).

### M11: Brier Score (per class, multiclass)

```
BS(k) = (1/N_pairs) * Σ_{(i,j)} (class_prob[k][i,j] - 1[label(i,j)==k])^2
```

Range [0,1]; lower is better. Baseline for class k = n(k)/N_pairs * (1 - n(k)/N_pairs).

Skill score: BS_skill(k) = 1 - BS(k) / BS_baseline(k). Positive = better than climatology.

---

### M12: Expected Calibration Error (ECE)

Computed on the argmax probability (the predicted class confidence):

1. Bin predictions into 10 equal-width bins by max(class_prob)
2. For each bin b: ECE_b = |mean(confidence_b) - mean(accuracy_b)|
3. ECE = Σ_b [|bin_b| / N_pairs * ECE_b]

**Exploratory metric only.** ECE is sensitive to bin choice and class imbalance. Not used for success/failure determination.

---

## 4. Ranking Metrics

Applies to the directed ranking of pairs by framework score.

### M13: Top-K Precision for Class k

For K ∈ {50, 100, 200, 500}:
```
TopK-Prec(k, K) = |{(i,j) : rank_by_score_k(i,j) ≤ K AND label(i,j)=k}| / K
```

where score_k(i,j) = class_prob[k].

**Secondary metric.** Relevant for the use case where the framework is used to prioritize pairs for follow-up experimental validation.

---

### M14: Enrichment Score for Class k

```
Enrichment(k, K) = TopK-Prec(k, K) / (n(k) / N_pairs)
```

Expected value under random ranking = 1.0. Reported at K = 50, 100, 200 for classes C and LR (primary detection targets of the framework).

---

## 5. Supplementary Raw-Score Metrics (if raw_scores provided)

If the framework provides supplementary raw_scores (q_directed, omega_partial, delta_omega), compute:

| Metric | Score used | Target class |
|--------|-----------|-------------|
| Q-AUROC(LR) | q_directed | LR (C+M) |
| Q-AUROC(Direct) | q_directed | Direct (S+M) |
| Ω-AUROC(Direct) | omega_partial | Direct (S+M) |
| ΔΩ-AUROC(LR) | delta_omega | LR (C+M) |
| ΔΩ-AUROC(C) | delta_omega | C |

**Pre-specified hypothesis:** The framework claims that:
- High |ΔΩ[i,j]| identifies C and M pairs (SAREACHABLE=True)
- High |Ω[i,j]| identifies S and M pairs (DIRECT=True)

These supplementary metrics directly test these claims on the raw feature scores, independent of the classification layer. They are secondary metrics.

---

## 6. Metric Governance

### 6.1 Primary Metrics

**Determine success/failure verdict. Frozen before evaluation.**

| ID | Name | Condition |
|----|------|-----------|
| M1-C | AUROC for class C | oracle_z |
| M1-LR | AUROC for LR class (C+M) | oracle_z |
| M6 | Macro-AUROC (S,C,M,N) | oracle_z |

### 6.2 Secondary Metrics

**Reported. Used for interpretation. Do not alter the primary verdict.**

M1 (S, M, N), M2 (all classes), M3-M5, M7, M8, M9, M10, M13, M14, plus all primary metrics on non-oracle_z conditions.

### 6.3 Exploratory Metrics

**Reported. Hypothesis-generating only. Not pre-specified as tests.**

M11, M12, supplementary raw-score metrics (§5), condition-comparison analyses.

---

## 7. Statistical Uncertainty

### 7.1 Bootstrap Confidence Intervals

For all primary metrics: compute 95% bootstrap CIs using 2,000 bootstrap samples of the 9,900 pairs. Report as [lower, upper].

Sampling unit: directed pair (i,j). Pairs are sampled with replacement. Each bootstrap sample has 9,900 pairs.

### 7.2 Run-level Variance

For each condition, the framework receives 5 independent runs. If the framework uses only one run, report which. If it aggregates, the CI above applies to the aggregated output.

Additionally, compute the metric on each run separately and report the across-run standard deviation.

### 7.3 Multiple Comparison Correction

There are 3 primary metrics. If any formal null-hypothesis test is applied:
- Use Bonferroni correction (α_adj = 0.05/3 = 0.0167)
- Report uncorrected and corrected p-values

The pre-specified primary test is one-sided: H1: primary_metric > threshold, H0: primary_metric ≤ threshold (see phase8a_success_criteria.md for thresholds).

Bootstrap test: compute the fraction of bootstrap samples where metric ≤ threshold → p-value.

---

## 8. Handling of Degenerate Outputs

| Degenerate case | Handling |
|----------------|---------|
| All pairs assigned same class_prob | AUROC = 0.5; report as "random performance" |
| class_prob does not sum to 1 | Normalize to simplex; flag in report |
| Missing pairs | Fatal error; evaluation cannot proceed |
| class_prob contains NaN or Inf | Replace with uniform 0.25 per class; flag as framework error |
| Framework produces class_prob for fewer than 9,900 pairs | Fill missing pairs with uniform 0.25; flag |

---

## 9. Metric Computation Code

Metric computation is implemented in `scripts/phase8/compute_metrics.py` (to be written in Phase 8B). The metric definitions above are authoritative. If implementation and definition disagree, the definition here governs.
