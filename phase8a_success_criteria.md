# Phase 8A Success Criteria
**Status:** FROZEN — pre-registered before framework execution  
**Date:** 2026-06-13

All success, failure, and inconclusive criteria are defined here. These are expressed exclusively in terms of pre-specified metrics on the `oracle_z` condition unless otherwise noted. The human evaluator may not exercise subjective judgment to override any criterion below.

---

## 0. Primary Verdict Structure

The verdict is determined by a three-step decision procedure applied in order:

1. **Benchmark validity check** — are the results interpretable at all?
2. **Primary metric thresholds** — do primary metrics meet pre-specified levels?
3. **Supplementary diagnostics** — do secondary metrics corroborate the verdict?

Step 3 does not alter the verdict from Step 2. It informs *interpretation* only.

---

## 1. Benchmark Validity Check (Must Pass First)

Before any success/failure evaluation, confirm:

| Check | Criterion | Action if failed |
|-------|-----------|-----------------|
| BV-1: Class C count sufficient | n(C) ≥ 100 at evaluation | → INCONCLUSIVE-B (benchmark failure) |
| BV-2: Class M count sufficient | n(M) ≥ 30 at evaluation | → INCONCLUSIVE-B (M AUROC unreliable) |
| BV-3: Baseline B4 is better than B1 on Direct-AUROC | B4 Direct-AUROC > 0.52 | → INCONCLUSIVE-B (Glasso failed; benchmark broken) |
| BV-4: No label leakage detected | Blinding audit passes | → INVALID (evaluation must be rerun) |
| BV-5: Framework output hash matches pre-run record | Hash check passes | → INVALID |

From locked labels: n(C)=857, n(M)=89. Both exceed thresholds, so BV-1 and BV-2 are satisfied pre-execution. They are included to protect against dataset corruption.

---

## 2. Primary Metrics and Thresholds

Evaluated on `oracle_z` condition. 95% bootstrap CIs required.

### 2.1 Primary Metric Set

| Metric ID | Name | Threshold for Success | Threshold for Partial | Threshold for Failure |
|-----------|------|----------------------|----------------------|-----------------------|
| M6 | Macro-AUROC | ≥ 0.70 | 0.60 – 0.70 | < 0.60 |
| M1-C | Class C AUROC | ≥ 0.65 | 0.55 – 0.65 | < 0.55 |
| M1-LR | LR-AUROC (C+M) | ≥ 0.65 | 0.55 – 0.65 | < 0.55 |

**Thresholds are derived from the following reasoning:**

- MacroAUROC ≥ 0.70: represents a meaningful lift above chance (0.50) that would be consistent with a practically useful classifier. This threshold is conservative relative to "excellent" (0.80+) but requires substantial performance above random.
- C-AUROC ≥ 0.65: the framework's primary claim is detecting H2-mediated links (C class). A threshold of 0.65 requires that the framework's probability current signal outperforms correlation-based baselines (B3, B4 expected at 0.50–0.55 for C) by a meaningful margin.
- LR-AUROC ≥ 0.65: binary detection of any H2-mediated link (C or M). Somewhat easier than C-only because M pairs also satisfy SAREACHABLE.

### 2.2 Threshold Rationale and Anti-Gaming Notes

These thresholds were set **before seeing any framework output**. They are not based on what the framework is capable of producing. They are based on:

1. The effect size expected from a working current-velocity estimator in theory (≥ 0.70 Macro-AUROC)
2. The performance achievable by simple correlation baselines (expected 0.50–0.60 based on network parameters)
3. The class imbalance constraints (C-AUROC at 0.65 represents 30% of the achievable lift above random, conservative)

**These thresholds cannot be adjusted after evaluation begins.**

---

## 3. Verdict Definitions

### 3.1 SUCCESS

Interpretation: The data are consistent with the framework's claims. The framework detects structural and current-supported links better than baselines.

**Criteria (all must hold simultaneously):**
- Macro-AUROC ≥ 0.70 (95% CI lower bound ≥ 0.65)
- C-AUROC ≥ 0.65 (95% CI lower bound ≥ 0.60)
- LR-AUROC ≥ 0.65 (95% CI lower bound ≥ 0.60)
- Framework outperforms B4 (Glasso) on C-AUROC by ≥ 0.05 (point estimate)
- No benchmark validity failure (§1)

**Interpretation guidance:** SUCCESS does not prove the framework is correct. It demonstrates that the framework's outputs predict the ground-truth labels at a level consistent with its theoretical claims on this specific benchmark. The benchmark itself has limitations (see failure modes in phase6a_failure_modes.md).

---

### 3.2 PARTIAL SUCCESS

Interpretation: The framework shows evidence of some claimed ability but fails to demonstrate the full picture.

**Criteria (SUCCESS not achieved; at least one of the following holds):**
- Macro-AUROC 0.60–0.70
- C-AUROC 0.55–0.65 OR LR-AUROC 0.55–0.65
- At least two of the three primary metrics are in the "Partial" range above

**Sub-categories:**

| Sub-category | Pattern | Interpretation |
|-------------|---------|---------------|
| PS-1: Structural only | S-AUROC ≥ 0.65, C-AUROC < 0.55 | Framework detects direct links but not current-supported links |
| PS-2: Current only | C-AUROC ≥ 0.65, S-AUROC < 0.55 | Framework detects H2-mediated links but not direct structural links |
| PS-3: Weak signal | All primary metrics 0.55–0.65 | Framework has a consistent but weak signal across all classes |
| PS-4: Condition-sensitive | oracle_z SUCCESS but blind_z FAILURE | Framework requires oracle z access; z is doing the work |

PS-4 is a significant finding: it would suggest the framework is identifying z-correlated activity rather than network structure per se.

---

### 3.3 FAILURE

Interpretation: The data are inconsistent with the framework's primary claims. The framework does not detect current-supported links above what simple baselines achieve.

**Criteria (any one sufficient):**
- Macro-AUROC < 0.60 (point estimate)
- C-AUROC < 0.55 (point estimate)
- LR-AUROC < 0.55 (point estimate)
- Framework C-AUROC ≤ B4 Glasso C-AUROC (point estimate) — the framework does no better than discarding indirect paths

**Note:** FAILURE on this benchmark does not falsify the current-velocity framework absolutely. It falsifies the claim that the framework's outputs contain signal about the specific link types defined by the SAREACHABLE ground truth on this specific 140-neuron benchmark. This is a meaningful negative result but requires replication before strong conclusions.

---

### 3.4 INCONCLUSIVE

Interpretation: The results cannot be attributed to the framework's success or failure due to a confound.

**Sub-categories:**

| Code | Condition | Meaning |
|------|-----------|---------|
| INCONCLUSIVE-B | Benchmark validity failure (§1) | Technical issue with benchmark prevents interpretation |
| INCONCLUSIVE-N | Sample size insufficient | Too few runs or too short trajectories for reliable estimation |
| INCONCLUSIVE-C | Framework could not produce output | Technical failure; not a scientific result |
| INCONCLUSIVE-CI | CI spans success and failure thresholds | Cannot determine which side of the threshold the true metric falls on |

**INCONCLUSIVE-CI** applies when the 95% CI for a primary metric includes both the success threshold and the failure threshold. Example: if Macro-AUROC point estimate = 0.64 (Partial), 95% CI = [0.58, 0.70] → cannot distinguish Partial from Success or Failure.

---

## 4. Statistical Uncertainty Rules

### 4.1 Confidence Interval Procedure

Bootstrap (B=2,000 samples, sampling directed pairs with replacement). Report [2.5th percentile, 97.5th percentile] of bootstrap distribution.

The verdict is based on **point estimates** of the primary metrics, not on CI boundaries. The CI is used for INCONCLUSIVE-CI determination only.

**Rationale for using point estimates:** Pre-specified thresholds already incorporate a conservative margin. Using CI lower bounds for the verdict would require setting higher thresholds, creating an asymmetric burden on the framework.

### 4.2 Multiple Comparison Handling

Three primary metrics. Each is tested against its threshold.

For formal null-hypothesis testing (optional; metrics are the primary evidence):
- H0 for each metric: metric ≤ threshold (no better than an intermediate baseline)
- H1: metric > threshold
- Bonferroni-corrected α = 0.05/3 ≈ 0.0167
- Bootstrap p-value: fraction of bootstrap samples where metric ≤ threshold

**The verdict is not based on p-values.** P-values are supplementary. The AUROC point estimates are the primary evidence.

### 4.3 Variance Across Runs

If across-run variance of the primary metric is > 0.05, report this as a stability warning. It does not change the verdict but is noted in the report.

---

## 5. Failure-Mode Overrides

The following conditions cause a result to be reclassified as INCONCLUSIVE-B rather than FAILURE, because the failure may be attributable to a benchmark limitation rather than the framework.

| Override Code | Condition | Triggered When |
|--------------|-----------|---------------|
| FO-1: Weak paths | P1-A result extreme | > 60% of C pairs have path strength < 0.01 (resampling remediation was not applied) |
| FO-2: Near-zero H2 weights | Post-hoc inspection of A | Mean path strength for C pairs < 0.005 |
| FO-3: Class C count low | n(C) at evaluation < 200 | Statistical power insufficient |
| FO-4: Dynamical failure | All run variances < 10⁻⁴ | Dynamics collapsed; no signal in y |
| FO-5: Observation model failure | All y values constant or NaN | Technical failure in data |

**FO-1 and FO-2** address the P1-A acceptance test finding: 26.1% of C pairs have near-zero H2 path strength. This is within the 30% threshold (P1-A PASSED) but represents a real concern. If the framework fails and post-hoc analysis reveals that > 90% of the "missed" C pairs are exactly the near-zero-strength ones, this should be reported as PARTIAL-BENCHMARK-LIMITATION rather than outright framework failure.

**The 60% trigger for FO-1 would indicate the remediation should have been applied but was not.** Since P1-A passed at 26.1%, FO-1 is not pre-triggered. It is a contingency.

---

## 6. Condition-Specific Verdicts (Secondary)

After the primary oracle_z verdict is recorded:

| Secondary comparison | Positive finding | Negative finding |
|---------------------|-----------------|-----------------|
| oracle_z − blind_z Macro-AUROC difference | > +0.05: z provides meaningful additional information | < −0.02: framework degrades with z access (unexpected) |
| oracle_z − weak_z difference | > +0.05: performance is SNR-dependent | Negligible: framework is SNR-independent (concerning) |
| strong_z − oracle_z difference | > +0.05: framework benefits from amplified H2 signal | Not applicable if framework already at ceiling |
| neural_state − oracle_z difference | Positive: calcium model hurts performance | Negative: calcium model helps; framework works better with realistic observations |

These comparisons provide interpretive context. They cannot change the primary verdict.

---

## 7. Reporting Requirements

The final report must contain, in this order:

1. Benchmark validity check: PASS/FAIL for each BV-* check
2. Primary verdict: SUCCESS / PARTIAL SUCCESS (with sub-category) / FAILURE / INCONCLUSIVE (with code)
3. Primary metric values with 95% CIs
4. Comparison to all 6 baselines on primary metrics
5. Secondary metric values
6. Condition-comparison table
7. Failure mode override assessment
8. Any deviations from the pre-registered protocol

**The primary verdict in item 2 cannot be altered by anything in items 3–8.**
