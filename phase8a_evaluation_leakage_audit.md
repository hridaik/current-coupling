# Phase 8A Evaluation Leakage Audit
**Status:** ADVERSARIAL REVIEW — pre-registered  
**Date:** 2026-06-13  
**Stance:** Assume the framework is wrong. Find every way a false positive or false negative result could be manufactured.

This document is a first-class adversarial deliverable, not a formality. Every vulnerability is recorded regardless of whether a mitigation exists.

---

## 0. Adversarial Framing

**Question 1:** How could a non-working framework produce a SUCCESS verdict?  
**Question 2:** How could a working framework produce a FAILURE verdict?  
**Question 3:** What structural features of the evaluation design could be exploited by a motivated evaluator?

Each vulnerability is rated:
- **Severity:** P0 (blocks evaluation), P1 (significant risk, must be mitigated), P2 (minor risk, monitor)
- **Exploit path:** exactly how the vulnerability could be used
- **Mitigation:** what the pre-registration does to prevent it
- **Residual risk:** what remains despite mitigation

---

## Vulnerability V-E1 — Module Structure Leakage via Neuron Indices

**Category:** Label leakage (indirect)  
**Severity:** P1

**Exploit path:**  
Neuron indices 0–99 are provided to the framework. Module boundaries are contiguous (M1=0-24, M2=25-49, M3=50-74, M4=75-99). A framework that computes `module = neuron_idx // 25` exploits prior knowledge of the network design. Since C-class pairs are enriched between modules (H2 neurons target 2-module combinations), this would produce spurious C-AUROC lift without estimating probability currents.

**Magnitude:** Expected ~5-10% lift in LR-AUROC from module awareness alone. Baseline B6 demonstrates this upper bound.

**Mitigation:**  
- Framework is forbidden from using modular arithmetic on indices (blinding protocol §5.2)
- Baseline B6 explicitly captures this signal; framework must beat B6 on LR-AUROC for the result to be meaningful
- If framework LR-AUROC ≤ B6 LR-AUROC, the result is explained by module-awareness alone

**Residual risk:**  
If the framework uses an inductive bias (e.g., clustering algorithm on y) that implicitly discovers the module structure from the data, this is a legitimate statistical result, not leakage. The framework is allowed to discover structure that is observable in y(t). The restriction is on hardcoded use of index-based module membership, not data-driven discovery.

**Action:** B6 comparison is mandatory. Evaluator must report whether framework LR-AUROC exceeds B6 LR-AUROC.

---

## Vulnerability V-E2 — Metric Shopping

**Category:** Evaluation-side manipulation  
**Severity:** P1

**Exploit path:**  
After seeing framework outputs and computing metrics, the evaluator could select whichever metric shows the best performance as the "primary" metric, or add new metrics that favor the framework.

**Mitigation:**  
- Primary metrics (M6 MacroAUROC, M1-C, M1-LR) are frozen here before evaluation
- Metric registry defines secondary and exploratory metrics in advance
- No metric may be added or reclassified post-hoc

**Residual risk:**  
The evaluator could selectively emphasize secondary metrics in the narrative while technically adhering to the pre-registered primary verdict. This is a soft manipulation that the pre-registration cannot fully prevent. The mitigation is explicit: the primary verdict must be stated first, verbatim, before any narrative.

---

## Vulnerability V-E3 — Threshold Hacking

**Category:** Evaluation-side manipulation  
**Severity:** P1

**Exploit path:**  
If the framework achieves Macro-AUROC = 0.68 (in the Partial range), the evaluator could argue the threshold of 0.70 was too strict, or that 0.68 "rounds to 0.70" within CI, and reclassify the result as SUCCESS.

**Mitigation:**  
- Success thresholds are frozen at 0.70, 0.65, 0.65 (§3 of success criteria)
- The verdict is based on point estimates, not CI boundaries (except for INCONCLUSIVE-CI determination)
- No threshold adjustment is permitted for any reason after evaluation begins

**Residual risk:**  
The initial threshold setting is the most critical juncture. Thresholds set here (before evaluation) determine the verdict. They were set based on theoretical reasoning, not on knowledge of the framework's performance. The residual risk is that the thresholds were inadvertently calibrated too leniently (true negative results classified as partial success) or too strictly (true positive results classified as partial success). This risk is inherent to any threshold-based evaluation and is acknowledged.

---

## Vulnerability V-E4 — Baseline Shopping

**Category:** Evaluation-side manipulation  
**Severity:** P1

**Exploit path:**  
After seeing the framework's C-AUROC, the evaluator could design a baseline that underperforms on C specifically (e.g., by choosing a very high regularization for Glasso that drives C-AUROC to 0.50), making the framework look better by comparison. Conversely, a baseline that beats the framework could be excluded.

**Mitigation:**  
- All 6 baselines are pre-specified in full algorithmic detail (phase8a_baseline_spec.md)
- B4 regularization alpha selection procedure is pre-specified (BIC on held-out run 4)
- No baseline may be added or removed after evaluation begins
- Failed baselines are excluded (not used to make the framework look better)

**Residual risk:**  
The B4 regularization grid `{0.005, 0.01, 0.02, 0.05, 0.10}` was set here. A different grid could produce different B4 performance. This grid was chosen to span a reasonable range for 100 neurons with 192,000 time points. The specific alpha selected by BIC may favor or disfavor the framework. This is unavoidable without knowing the framework's result in advance.

---

## Vulnerability V-E5 — Post-Hoc Class Redefinition

**Category:** Label leakage (indirect)  
**Severity:** P1

**Exploit path:**  
After seeing that the framework achieves high AUROC on, say, S and N but low AUROC on C and M, the evaluator could argue that "C and M should really be merged" or "M is too small to matter" and recompute metrics on a 2-class version that shows better results.

**Mitigation:**  
- The 4-class taxonomy (S,C,M,N) and the LR/Direct reductions are frozen in this spec
- No new class grouping may be introduced after evaluation
- LR and Direct reductions are pre-specified and their metrics are labeled secondary

**Residual risk:**  
The pre-registration does not prevent exploratory analysis of other groupings *after* recording the verdict. These must be labeled EXPLORATORY and cannot alter the verdict. A sufficiently motivated evaluator could emphasize exploratory favorable groupings in their narrative. This is a social risk that the pre-registration mitigates but cannot eliminate.

---

## Vulnerability V-E6 — Ranking-to-Class Conversion Flexibility

**Category:** Evaluation-side manipulation  
**Severity:** P2

**Exploit path:**  
The framework produces class_prob vectors. If the framework produces scores rather than probabilities (e.g., [5.2, 3.1, 0.8, 0.1] without normalization), different normalization methods (softmax with different temperature, simplex projection) produce different AUROC values. The evaluator could choose the normalization post-hoc to maximize performance.

**Mitigation:**  
- The framework must declare its normalization_method in output metadata before evaluation
- The declared method is used for evaluation and cannot be changed
- Degenerate outputs (NaN, non-summing) are handled by pre-specified rules in metric registry §8

**Residual risk:**  
The framework developer might try different temperature values for softmax and report the best one as the declared method. This is a legitimate technical decision (temperature is a hyperparameter of the normalization) but could be gamed. The mitigation: if the framework iterates over temperatures, it must declare this and use a principled selection (e.g., minimize calibration error on a held-out run, which does not use labels).

---

## Vulnerability V-E7 — Calibration Leakage

**Category:** Label leakage (indirect)  
**Severity:** P2

**Exploit path:**  
Calibration metrics (Brier score, ECE) require knowledge of true labels to compute. If the framework were to receive calibration feedback (even indirectly, e.g., through cross-validation against some external labeled set), it could adjust its output probabilities to match the label distribution, producing better calibration scores that superficially look like better performance.

**Mitigation:**  
- Calibration metrics (M11, M12) are designated **exploratory** only
- They cannot affect the primary verdict
- The framework has no access to any labels or calibration feedback before output freeze

**Residual risk:**  
Low. Calibration metrics are not part of the primary verdict. Even if calibration were inflated, it would not change AUROC (AUROC is rank-based, not affected by probability scaling).

---

## Vulnerability V-E8 — Hyperparameter Tuning Leakage

**Category:** Test-set contamination  
**Severity:** P1

**Exploit path:**  
If the current-velocity framework has hyperparameters (e.g., regularization for Ω estimation, window sizes for Q estimation), and these are tuned using the benchmark test data (either through iterative evaluation or through observing metric values), the effective sample size is reduced and the evaluation is optimistic.

**Mitigation:**  
- The framework receives the benchmark data once per condition (no iterative feedback)
- Framework outputs are frozen immediately upon writing
- The framework may not be re-run to improve performance (except for documented bug fixes per blinding protocol §6)
- The framework may use held-out runs (e.g., run 4) for internal cross-validation, as long as it declares this in output metadata

**Residual risk:**  
The framework developer has access to the full evaluation data during development. If the framework was developed using synthetic data that approximates the benchmark, some implicit hyperparameter tuning toward the benchmark structure may have occurred. This risk is inherent to any fixed benchmark and cannot be fully mitigated by pre-registration.

**Disclosure requirement:** The framework developer must disclose whether the framework was developed or tuned using any data derived from this benchmark (including approximate synthetic versions with similar parameters).

---

## Vulnerability V-E9 — Direction Averaging

**Category:** Structural exploit  
**Severity:** P2

**Exploit path:**  
The evaluation unit is the directed pair (i,j). The framework might produce symmetric scores (score[i,j] == score[j,i] for all pairs) and still receive credit for correct directed pair classification, because the labels themselves have some directional asymmetry (A is not symmetric in general). A symmetric framework that correctly identifies which pairs are connected (undirected) would receive partial AUROC credit.

**Mitigation:**  
- The supplementary metric ΔDirected (reported): compare performance on (i,j) vs (j,i) for each pair; a genuinely directed estimator should show asymmetry
- The evaluation does NOT penalize symmetric estimators — if a symmetric estimator is best, that is a legitimate finding
- The question of whether the framework is genuinely directed is tracked as an exploratory metric

**Residual risk:**  
Low for AUROC. A symmetric estimator cannot reach high MacroAUROC because it cannot distinguish S(i→j) from S(j→i) when only one of these is true. For a random network, A is not symmetric, so S pairs are unlikely to be mutual. The AUROC penalty for directionality is implicitly captured.

---

## Vulnerability V-E10 — Condition-Level Leakage via Condition Name

**Category:** Label leakage (indirect)  
**Severity:** P2

**Exploit path:**  
The input bundle includes the condition name (e.g., 'oracle_z'). A framework that has been designed with knowledge of the evaluation conditions (and their expected effects on class separability) could implement condition-specific logic that exploits this knowledge. For example, if the framework knows that oracle_z data has stronger C-class signal (higher H2 weights due to larger effective SNR), it could apply more aggressive thresholds for C classification.

**Mitigation:**  
- Condition names are well-defined scientific experimental conditions, not labels
- A framework that adapts its algorithm per condition is scientifically legitimate
- The evaluation compares all conditions against the same pre-specified baselines

**Residual risk:**  
Negligible. Condition-adaptive algorithms are a feature, not a bug. The evaluation is designed to assess whether the framework correctly uses the additional information in each condition.

---

## Vulnerability V-E11 — Circularity via SAREACHABLE Definition

**Category:** Ground-truth leakage (conceptual)  
**Severity:** P0 (assessed; determined to be already mitigated)

**Exploit path:**  
The ground-truth label C is defined by SAREACHABLE, which is a topological property of A_sparse. If the framework estimates ΔΩ[i,j], and if ΔΩ[i,j] is mathematically equivalent to (or tightly coupled to) the SAREACHABLE indicator, then high C-AUROC would be tautological: the framework detects exactly what the labels were designed to encode.

**Phase 6A finding:** This was identified as Leakage L1 in phase6a_review.md. The resolution: SAREACHABLE is a *binary topology check* (path exists), while ΔΩ is a *continuous weight-sensitive quantity*. They are not equivalent:
- A C pair with near-zero H2 weights has SAREACHABLE=True but ΔΩ[i,j] ≈ 0
- A pair with large indirect coupling but SAREACHABLE=False (e.g., path through non-H2 hidden neurons) would have ΔΩ[i,j] > 0 but label=N or S

**Current risk assessment:** This vulnerability is NOT fully mitigated by SAREACHABLE's binary nature. The benchmark is designed so that most C pairs have paths through H2 neurons. The test is whether the framework's ΔΩ signal is informative about *which* pairs have H2-mediated paths. This is a scientifically valid test — not circular — because:
1. The framework does not know H2 membership (forbidden input)
2. The framework estimates ΔΩ from observational data, not from topology
3. A failing framework (no working estimator) would not produce high C-AUROC regardless of the label definition

**Residual risk:**  
P1 residual. If the framework happens to pick up on the specific statistical signature of H2-mediated modulation without estimating probability currents per se (e.g., a generic state-dependent correlation estimator would detect the same thing), high C-AUROC does not specifically validate the *probability current* mechanism. This is why B5 (state-dependent correlation difference) is included as a baseline: it approximates H2-mediated dependence without the current-velocity framework's specific mechanism. If the framework does not outperform B5, the positive result may be explained by generic state-detection.

---

## Vulnerability V-E12 — Small M-Class Instability

**Category:** Statistical limitation  
**Severity:** P1

**Exploit path:**  
Class M has only 89 pairs. AUROC for M is estimated from 89 positive pairs vs 9,811 negatives. The bootstrap CI for M-AUROC is expected to be very wide (±0.10 or more). The framework could achieve high M-AUROC by chance (e.g., if its score happens to rank the 89 M pairs well), and this would count toward MacroAUROC.

**Mitigation:**  
- M-AUROC is included in MacroAUROC but the wide CI is reported
- The success threshold for MacroAUROC (0.70) must be met jointly across all four classes; a framework that inflates M-AUROC at the expense of other classes will fail on other metrics
- M is not a primary metric in isolation (only through MacroAUROC aggregation)

**Residual risk:**  
MacroAUROC gives equal weight to M despite its small size. A framework that gets M-AUROC = 1.0 by chance (all 89 M pairs ranked first) gets a +0.25/4 = +0.0625 boost to MacroAUROC. If this tips the verdict from Partial to Success, it is a statistical artifact. The 95% CI assessment will reveal this.

**Additional monitoring:** Report bootstrap variance of M-AUROC specifically. If M-AUROC CI width > 0.20, flag the MacroAUROC as M-class-sensitive.

---

## Vulnerability V-E13 — Near-Zero C Paths (P1-A Residual)

**Category:** Ground-truth quality limitation  
**Severity:** P1

**Exploit path:**  
26.1% of C pairs have near-zero H2 path strength (max_{h∈SA} |A[h,i]|·|A[j,h]| < 0.01). These pairs are correctly labeled C (path exists) but the path is too weak to produce detectable ΔΩ signal. A working framework should receive credit for *not* classifying these as C. But the ground truth says they are C.

This creates a structural ceiling on C-AUROC: even a perfect framework that correctly identifies all detectable C pairs will rank near-zero-path C pairs low, which counts as false negatives. This caps C-AUROC below 1.0 even for a perfect estimator.

**Assessment of ceiling:**  
26.1% of C pairs are near-zero path strength. If a perfect framework assigns all high-strength C pairs top ranks and all near-zero C pairs low ranks, AUROC for C would be approximately:
- Positives ranked correctly: 857 × 0.739 = 633 high-strength C pairs ranked near top
- Positives ranked incorrectly: 857 × 0.261 = 224 near-zero C pairs ranked near bottom
- Approximate C-AUROC ceiling ≈ 0.739 + 0.261 × 0.50 = 0.87 (rough estimate)

The C-AUROC ceiling is approximately 0.87 due to near-zero paths. The success threshold of 0.65 is well below this ceiling.

**Mitigation:**  
- Failure-mode override FO-2 applies if the framework fails and post-hoc analysis attributes failures primarily to near-zero-path C pairs
- The success threshold (0.65) is set below the ceiling (0.87)
- P1-A passed (26.1% < 30%), so this is within pre-registered acceptance

**Residual risk:**  
The ceiling analysis above is approximate. If the framework achieves C-AUROC between 0.65 and 0.87, the result is scientifically meaningful. If C-AUROC < 0.65, it could be because the framework has no signal (true failure) or because the ceiling is lower than estimated (benchmark limitation). Post-hoc path strength stratification (high-strength C vs low-strength C) is a pre-specified exploratory analysis that can diagnose this.

---

## Vulnerability V-E14 — Cross-Run Nonstationarity

**Category:** Statistical limitation  
**Severity:** P2

**Exploit path:**  
The framework pools 5 independent runs. If the framework fits a model on some runs and predicts on others, it could exploit run-to-run differences to inflate performance (within-run overfitting that generalized across runs because all runs use the same A).

**Mitigation:**  
- All runs use the same A_sparse and labels; cross-run generalization does not provide label information
- The framework's cross-run use is left to its discretion; any cross-run procedure that uses only y and z_oracle is legitimate

**Residual risk:**  
Negligible. The ground truth (A_sparse structure, labels) is constant across runs. Cross-run procedures cannot leak label information because labels are not encoded in any individual trajectory.

---

## Summary Table

| ID | Vulnerability | Severity | Mitigation Status | Residual |
|----|--------------|----------|------------------|---------|
| V-E1 | Module index leakage | P1 | Mitigated (B6 comparison) | Low |
| V-E2 | Metric shopping | P1 | Mitigated (frozen registry) | Low |
| V-E3 | Threshold hacking | P1 | Mitigated (frozen thresholds) | Low |
| V-E4 | Baseline shopping | P1 | Mitigated (frozen baselines) | Medium |
| V-E5 | Post-hoc class redefinition | P1 | Mitigated (frozen taxonomy) | Low |
| V-E6 | Ranking-to-class flexibility | P2 | Mitigated (declared normalization) | Low |
| V-E7 | Calibration leakage | P2 | Mitigated (exploratory only) | Negligible |
| V-E8 | Hyperparameter tuning | P1 | Partially mitigated | Medium |
| V-E9 | Direction averaging | P2 | Monitored (supplementary metric) | Low |
| V-E10 | Condition-name leakage | P2 | Accepted | Negligible |
| V-E11 | SAREACHABLE circularity | P1 residual | Mitigated in Phase 6A; B5 diagnostic | Medium |
| V-E12 | Small M-class instability | P1 | Monitored (CI width) | Medium |
| V-E13 | Near-zero C paths | P1 | Acknowledged (FO-2 override, ceiling analysis) | Medium |
| V-E14 | Cross-run nonstationarity | P2 | Accepted | Negligible |

**Unresolved P0 vulnerabilities: 0**

V-E11 was classified P0 during Phase 6A and is now resolved at P1 residual following the SAREACHABLE redesign and B5 diagnostic. All remaining vulnerabilities are P1 or P2.

---

## Adversarial Scenarios

### Scenario A: Manufacturing a False Positive

**Attack:** Developer runs framework, sees C-AUROC = 0.58 (Partial range). Modifies framework to use module index arithmetic (`cluster = idx // 25`) to boost C predictions for between-module pairs. C-AUROC rises to 0.67 (SUCCESS range).

**Defense:** V-E1 mitigation requires B6 comparison. If framework LR-AUROC ≤ B6 LR-AUROC, the success is explained by module-awareness. B6 LR-AUROC is expected at ~0.60-0.65 from structural meta-knowledge alone. A framework that barely exceeds B6 is not demonstrating probability current estimation.

**Residual concern:** If genuine current estimation + module awareness together push framework above B6 by a small margin, the result is ambiguous. Report B6 comparison in all cases.

### Scenario B: Manufacturing a False Negative

**Attack:** Developer who wants to report a null result uses a suboptimal implementation of the framework (e.g., too short estimation window, excessive regularization) that suppresses the signal. Framework fails.

**Defense:** Pre-registration cannot prevent this. The mitigation is: (a) the framework implementation details must be disclosed, (b) re-evaluation due to bug fixes is permitted (§6 of blinding protocol), (c) the framework developer must declare whether they believe the implementation is faithful to the theoretical framework.

### Scenario C: Inconclusive Fishing

**Attack:** Developer sees INCONCLUSIVE-CI result (CI spans SUCCESS and FAILURE). Argues for more data (more runs, longer trajectories) until result tips to SUCCESS.

**Defense:** The pre-registered benchmark is 5 runs × 48,000 steps. No additional data collection is permitted for this pre-registered evaluation. Additional data is a separate experiment with its own pre-registration.
