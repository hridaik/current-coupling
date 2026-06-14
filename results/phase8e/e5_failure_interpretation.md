# E5: Failure Interpretation Given Accepted Labels

**Phase**: 8E — Label-Definition Audit  
**Date**: 2026-06-14  
**Question**: Given the benchmark labels as they are, what exactly does Phase 8D prove?  
**Frozen verdict**: FAILURE (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197)

---

## 1. The Three Interpretations

| Code | Interpretation | Meaning |
|------|---------------|---------|
| A | Framework fails theoretical object | Labels are valid; framework cannot recover what they test |
| B | Framework fails labels; labels are broader than object | Labels are an over-inclusive proxy; some labeled positives are not truly the paper's target |
| C | Framework fails labels; labels are wrong target | Labels test something categorically different from the paper's theoretical object |

---

## 2. Evidence Evaluation

### 2.1 Evidence for A (Framework fails theoretical object)

**Key empirical fact**: B5 (state-ΔCorr = |corr(y|z>median) − corr(y|z≤median)|) achieves C-AUROC=0.5517, significantly above chance (p ≪ 0.01 given n=857 C pairs, n=8457 N pairs).

This is decisive: a different detector — one that directly measures state-conditioned co-activity change — can retrieve above-chance C-class information from the same simulated data. The signal IS present. The framework IS the problem.

Additional confirmatory evidence:

| Evidence item | Implication |
|--------------|-------------|
| B5 C-AUROC=0.5517 > 0.50 | Observable state-dependent signal exists in the C class |
| D3: C pairs 1.18× enriched in top |ΔCorr| quartile | Labels correctly tag pairs with more state-dependent signal |
| D4: B3 (correlation) achieves C precision@50=0.20 (OR=2.657, p=0.010) | Simple methods outperform the framework; signal is not subtle |
| Phase 8C Axis 1: C-AUROC near flat across 24× GAMMA_H2 range | Framework's failure is structural, not due to insufficient signal strength |
| Phase 8C Axis 2: C-AUROC at k=0 H2 (0.4425) ≈ k=8 H2 (0.4484) | Delta_PCor cannot exploit H2-mediated paths even when explicitly present |
| D3: State-sensitive C has WORST C-AUROC (0.3935) | Framework inverts the signal — the most detectable C pairs are ranked last |

**Mechanism of failure (confirmed)**:
The framework regresses z out of y to compute y_resid, then uses the change in partial correlation (Delta_PCor = |PCor_raw − PCor_cond|) as C-score. For C pairs:
1. C pairs have z-correlated variance in y (from H2 drive at high z)
2. Z-regression removes this z-correlated variance from y_resid
3. After removal, C pairs in y_resid look similar to N pairs in y_resid
4. PCor_cond from y_resid does not distinguish C from N
5. Delta_PCor is determined by structural properties of the H2-path that happen to be shared between C and N pairs with different characteristics → C pairs get LOWER Delta_PCor than N pairs → AUROC < 0.50

The inversion (AUROC < 0.50, not just near 0.50) is the signature: the z-regression actively degrades the C signal.

---

### 2.2 Evidence for or against B (Labels broader than object)

**Evidence FOR B (partial)**:

The E3 analysis identified two genuine gaps between the C label and the paper's ideal "current-supported" object:

1. **Topological vs. observed**: ~28% of C pairs have path_strength < 0.01. These pairs may not exhibit detectable ΔQ in practice. They are labeled C by topology but may be empirically null.

2. **Common cause vs. current**: Per W7, H2-mediated correlation is a confounding structure (common hidden cause), not directed probability current. The C label may be measuring a different but related phenomenon.

**Evidence AGAINST B being the primary explanation**:

Interpretation B would predict: if we restrict to the "true" subset of C (the pairs that genuinely satisfy the paper's object), the framework would succeed on them. This prediction fails:

| Test | B predicts | Observed |
|------|-----------|---------|
| Framework on strong C (path_str>med) | Should succeed (strong path, strong signal) | **C-AUROC=0.4069 — WORSE than full C** |
| Framework on state-sensitive C (top |ΔCorr| quartile) | Should succeed (highest observable signal) | **C-AUROC=0.3935 — WORST** |
| Framework on top-10% |ΔCorr| C pairs | Should succeed (most worm-like) | **Median C-rank=7230, only 1/86 in top-100** |

The framework is MOST ANTI-INFORMATIVE for the pairs most closely matching the paper's theoretical object. This falsifies B as the primary explanation.

B is partially true (the labels do have excess coverage), but B does not explain the framework failure.

---

### 2.3 Evidence for or against C (Labels are wrong target)

**Evidence FOR C (partial)**:

The W7 theoretical critique: H2-mediated pairs are not "current-supported" in the thermodynamic sense. If the paper's framework is designed specifically to detect probability current (Q = ΩD) changes, and the benchmark tests changes in covariance/precision (ΔΩ) from a common-cause structure, these are different mathematical objects.

**Evidence AGAINST C being the primary explanation**:

1. Even if the C labels test ΔΩ from common cause rather than ΔQ from current, the framework still fails at detecting ΔΩ. B5 (which directly measures ΔCorr, a function of ΔΩ) succeeds. The framework's failure is not in choosing the wrong target — it is in being unable to detect ANY state-conditioned covariance change for C pairs.

2. The paper's application to the worm uses ΔΩ and ΔQ in the same derivation; both quantities are expected to identify the same pairs in practice for a well-functioning framework. The gap between "measuring ΔΩ" and "measuring ΔQ" is not the bottleneck.

3. The benchmark labels DO produce an observable, detectable signal (B5 above chance). If the labels were testing a completely wrong object, B5 would be near chance too. It is not.

C is a theoretical criticism worth noting but does not explain the empirical failure.

---

## 3. Verdict

**Primary conclusion: A — Framework fails to recover the theoretical object.**

The benchmark labels are valid proxies for the paper's theoretical object:
- C pairs are genuinely off-connectome (P3: exact match)
- C pairs genuinely show state-dependent signal (P1: confirmed by B5 above chance, 1.18× enrichment)
- C pairs are observable with appropriate state access (P2: confirmed with oracle z)

The framework cannot recover these pairs despite the signal being present and detectable. The specific architectural failure (z-regression removes z-correlated signal from y_resid before computing PCor_cond) explains why the most detectable C pairs receive the worst scores.

---

## 4. What Exactly Does Phase 8D Prove?

Phase 8D proves **three things**:

### 4.1 The framework fails to detect off-connectome state-dependent organization.

**Precision**: The current-velocity framework, given access to z (oracle condition) or without z (blind condition), produces C-scores that are negatively correlated with C-class membership. This is not random failure — it is structural inversion. The C-score is better described as an "anti-C score" in the range of C detection.

**Quantification**: C-AUROC=0.4484, zero C pairs in top-50, zero in top-20, zero in top-10. Spearman ρ(|ΔCorr|, C-score) = -0.163 (p=1.8e-6) — the framework ranks the most state-detectable C pairs LAST.

**This is the primary scientific claim Phase 8D establishes.**

---

### 4.2 The signal the benchmark tests IS detectable — just not by this framework.

**Precision**: B5 (|ΔCorr|) achieves C-AUROC=0.5517 using the same data the framework uses. B3 (pairwise correlation) achieves C-precision@50=0.20 (OR=2.657, p=0.010). Both exceed framework performance with simpler methods.

**Implication**: The benchmark is not too hard. The signal is not too weak. The framework's architecture is specifically wrong for the H2-mediated mechanism.

**This rules out the hypothesis that the benchmark is flawed or the signal is undetectable.**

---

### 4.3 The failure is architectural and irreversible under the current design.

**Precision**: Phase 8C demonstrated that varying GAMMA_H2 across 24×, N_H2_ACTIVE from 0 to 8, and THETA_Z across 200× moves C-AUROC by at most 0.039. The framework's performance is insensitive to the strength of the signal it is supposed to detect.

The D3 result (state-sensitive C → worst C-AUROC) identifies the mechanism: z-regression is the failure point. Any framework that begins with z-regression of y will exhibit this inversion.

**This rules out "insufficient signal" and "wrong parameter regime" as explanations.**

---

## 5. The Partial Mismatch (B) and Its Significance

Even though B is not the PRIMARY explanation, it is a genuine concern for theoretical precision:

| Mismatch | Severity | What it means |
|----------|---------|--------------|
| 28% C pairs below path_strength 0.01 | Moderate | ~240 C pairs may be empirically null; labels are over-inclusive |
| Common cause ≠ probability current (W7) | Theoretical | Benchmark tests ΔΩ from confounding, not ΔQ from current |
| State-amplified ≠ state-exclusive | Moderate | Benchmark C lacks the near-zero baseline that makes worm pairs distinctive |

**What this means for interpretation**: The Phase 8D conclusion that "the framework fails to recover the theoretical object" is correct and not undermined by these mismatches. However, for future benchmark design:

- Requiring path_strength > 0.01 (or > 0.027) as a minimum for C labeling would make the C class more conservative and more directly analogous to worm Class 4 pairs.
- The W7 gap (common cause vs. current) is the theoretically cleanest mismatch: the benchmark tests whether the framework can identify pairs jointly driven by a state-modulated hidden common cause. This is a real and meaningful detection task, but it is not identical to detecting probability current changes.
- The P5 gap (state-amplified vs. state-exclusive) could be addressed by requiring that path_strength × GAMMA_H2 exceeds some minimum observable threshold, or by selecting C pairs using oracle-state information during label generation.

None of these changes would alter the FAILURE verdict. They would, however, make the benchmark's claim more precise: "the framework cannot detect off-connectome, state-amplified hidden-common-cause links" rather than "the framework cannot detect current-supported links" (which requires a stronger theoretical claim about the mechanism).

---

## 6. Single-Sentence Summary

**Phase 8D proves that the current-velocity framework architecturally fails to detect state-dependent off-connectome organization — an organization that IS present in the benchmark data, IS detected by simpler baselines, and CORRESPONDS to the benchmark's C-class labels — because z-regression removes exactly the signal that distinguishes C pairs from N pairs, causing the framework to rank the most detectable C pairs last.**
