# Phase 8E Summary: Label-Definition Audit

**Date**: 2026-06-14  
**Frozen verdict**: Phase 8B FAILURE (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197)  
**Phase 8C classification**: Architecture-limited failure  
**Phase 8D classification**: A — No useful recovery of the organization of interest

---

## The Three Questions

---

### Q1: Is the benchmark testing the same theoretical object as the paper?

**Answer: PARTIALLY — the benchmark is a reasonable but imperfect proxy for the paper's theoretical object.**

The paper's theoretical object is **observable, state-conditioned, off-connectome conditional dependence change** — formally pairs (i,j) where:
- A_raw(i,j) = 0 (off the synaptic connectome)
- |ΔQ(i,j)| = |Q_roam(i,j) − Q_dwell(i,j)| is large (state-conditioned precision change)
- The signal is detectable in neural recordings (observable)

The benchmark's C label approximates this object:
- DIRECT=0 maps exactly to "off-connectome" ✓
- SAREACHABLE=1 proxies "state-conditioned" via H2-relay topology ✓ (with qualification below)
- The signal IS observable: B5 achieves C-AUROC=0.5517 and C pairs are 1.18× enriched in state-sensitive quartile ✓

**Two specific gaps** prevent the alignment from being exact:

**Gap 1 — Topological proxy vs. observed signal**:  
The C label uses topology (path exists) rather than empirical state-sensitivity (signal is above noise). ~28% of C pairs have path_strength < 0.01 and may not exhibit detectable state-dependent signal in finite data. The paper's object requires a large OBSERVED ΔQ; the label requires only topological reachability.

**Gap 2 — Common-cause mechanism vs. probability current** (Phase 6A review, W7):  
The paper's framework targets *probability current* Q = ΩD, which reflects directed conditional dependence changes between neurons. The benchmark's H2-mediated mechanism creates a *hidden common cause* structure: both i and j receive input from h, and h is driven by z. This creates SYMMETRIC ΔΩ from the common source — not directed probability current circulation. Per W7: *"The probability current between two neurons jointly driven by a common unobserved source need not involve nonequilibrium circulation."*

Additionally, the benchmark's H2-mediated correlation is **state-amplified** (present at z=0, stronger at high z), not **state-exclusive** (absent at baseline). The paper's ideal Class 4 pairs (RMEL-RMER type) appear to exhibit near-zero correlation in one state and significant correlation in the other — a harder, cleaner version of the detection problem.

**Overall assessment**: The benchmark is testing "pairs that are off the structural coupling matrix and have a topological mechanism for state-dependent co-activity amplification through a hidden relay." This is a reasonable but weaker version of the paper's "pairs that exhibit state-exclusive probability-current-supported functional connectivity."

---

### Q2: Where specifically is the mismatch?

| Property | Paper's ideal object | Benchmark C label | Gap severity |
|----------|---------------------|------------------|-------------|
| Off-connectome | A_raw = 0 (exact) | DIRECT=0 (exact analog) | NONE |
| State-dependent | ΔQ large (observed) | SAREACHABLE=1 (topological) | MODERATE |
| Observable | Detectable in recordings | Confirmed: B5 C-AUROC=0.5517 | SMALL (signal is weaker than ideal) |
| State-exclusive | Near-zero at baseline state | State-amplified (present at z=0) | MODERATE |
| Mechanism | Directed probability current | Hidden common cause (common H2 drive) | THEORETICAL |
| Behavioral meaning | Roaming/dwelling distinction, neuropeptide enrichment | z(t) as behavioral analog | PARTIAL |

**The most operationally significant gap** is the state-amplified vs. state-exclusive distinction (P5 in E4):
- When H2 z-drive is set to zero (Phase 8C Axis 2, k=0 active H2), C-AUROC barely changes (0.4425 vs. 0.4484)
- This means the H2-mediated structural paths create baseline correlation between C pairs that makes them indistinguishable from N pairs even without the z-drive
- A state-EXCLUSIVE link would produce C-AUROC near 0.50 at z=0 (no H2 drive → no state signal → random ranking) but above 0.50 at high z drive — the benchmark does not show this pattern because the structural paths persist

**The most theoretically significant gap** is the common-cause vs. current mismatch (W7):
- The paper claims to detect directed probability current changes between states
- The benchmark tests detection of hidden-common-cause correlation amplification
- These are different objects; the paper's current framework (z-regression + Delta_PCor) is architecturally suited for neither, as demonstrated by Phase 8B-8D results

---

### Q3: Should the labels be redefined? What is the correct interpretation of the failure?

**On label redefinition**: NO — the labels should NOT be redefined for the following reasons:
1. Redefining to require observable state-dependence (|ΔCorr| > threshold) would be circular — it requires running simulations to define labels
2. Redefining to exclude low path_strength pairs would change the benchmark but not the verdict (strong C AUROC=0.4069, worse than full C)
3. The frozen verdict must not be modified, and label redefinition would constitute a post-hoc benchmark modification

**Optional improvement for future versions**: A stronger benchmark would additionally require path_strength ≥ 0.01 (filtering ~28% of weak C pairs) and would report results separately for strong_C and full_C. This would make the label more conservative and more analogous to the worm's Class 4 pairs.

**Failure interpretation**: **A — Framework fails to recover the theoretical object.**

The benchmark labels, despite their partial misalignment with the ideal paper object, DO correspond to pairs with observable state-dependent signal. The failure is attributable to the framework's architecture, not to the labels:

1. **The signal is present**: B5 C-AUROC=0.5517 (above chance) using the same data
2. **The labels are right**: C pairs are enriched for state-dependent signal (1.18× enrichment in top |ΔCorr| quartile)
3. **Simple baselines work**: B3 (pairwise correlation) achieves C precision@50=0.20 (OR=2.657, p=0.010)
4. **The framework inverts the signal**: State-sensitive C pairs receive the LOWEST C-scores (C-AUROC=0.3935); state-invariant C pairs receive slightly higher scores (0.5276) — the opposite of the correct ranking
5. **The mechanism is confirmed**: Z-regression in the framework removes the z-correlated variance from y_resid, which is precisely the variance that distinguishes C pairs from N pairs. After z-regression, Delta_PCor is determined by residual structural properties that are anti-correlated with C-class membership.

---

## Classification

**Benchmark verdict**: **B — Partially aligned with the paper's theoretical object.**

The labels correctly capture off-connectome and state-regulated properties. The partial misalignment (common-cause mechanism ≠ probability current; state-amplified ≠ state-exclusive) means the benchmark is testing a slightly easier and mechanistically different version of the paper's target. Both properties (state-amplified off-connectome pairs vs. state-exclusive current-supported links) are legitimate scientific targets; the benchmark tests one, the paper claims to detect the other.

**Failure verdict**: **A — Framework fails to recover the theoretical object, where "theoretical object" here is the benchmark's operationalization of off-connectome state-dependent pairs.**

The partial misalignment (B) does not rescue the framework. Even on the benchmark's own terms, with its own C labels, with oracle z access, in parameter regimes with strong signal (GAMMA_H2=12.0, THETA_Z=0.01), the framework's C-AUROC never exceeds 0.4837. The signal is present; the framework cannot detect it.

---

## Implications

The Phase 8B FAILURE verdict is not explained by label mismatch. The failure is architectural.

For a framework to succeed on this benchmark, it would need to:
1. NOT regress z out of y before covariance estimation (this removes the C-signal)
2. USE z as an instrument to compare conditional correlation structure at different state values
3. DETECT the change in pairwise correlation between z-stratified conditions (the B5 approach)
4. HANDLE the precision estimation challenge at n/p=480 (regularized estimation of two 100×100 precision matrices)

No modification to the benchmark labels is warranted or would change the scientific conclusion.

---

## Deliverables

| File | Status |
|------|--------|
| results/phase8e/e1_theoretical_object.md | COMPLETE |
| results/phase8e/e2_label_definitions.md | COMPLETE |
| results/phase8e/e3_alignment_table.md | COMPLETE |
| results/phase8e/e4_worm_object_overlap.md | COMPLETE |
| results/phase8e/e5_failure_interpretation.md | COMPLETE |
| phase8e_summary.md | COMPLETE |
