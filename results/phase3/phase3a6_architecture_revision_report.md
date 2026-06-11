# Phase 3A.6 Architecture Revision Report
Date: 2026-06-03
Authorization: Phase 3A.6
Status: COMPLETE — awaiting review. Held-out ADEL pairs NOT evaluated.

---

## 1. Summary Table

| Model | Description | ρ_train | AUROC_pdf | top-20 | M2/R4 p-val | Criterion |
|---|---|---|---|---|---|---|
| **R1** | Reference (Lyapunov + global obj) | 0.062 | 0.920 | 0 | — | baseline |
| **R2** | PDF-local objective | 0.000 | 0.500 | artifact | — | FAIL |
| **R3A** | ADMM sparsified Lyapunov | 0.033 | 0.779 | **1** | — | partial |
| **R3B** | Density-matched threshold | 0.040 | 0.915 | 0 | — | FAIL |
| **R4** | Stronger degree-null (source-only) | — | — | — | 1.000 | FAIL |
| **R5** | α sensitivity | — | — | — | — | diagnostic |

---

## 2. Pre-specified Success Criteria Evaluation

| Criterion | Threshold | Measured | Result |
|---|---|---|---|
| 1: M1 exceeds degree-matched nulls | R4 p-val < 0.05 | p = 1.000 | **FAIL** |
| 2: PDF identity matters beyond degree | M1 > R4_p95 + 0.01 | margin = 0.000 | **FAIL** |
| 3: Top-pair overlap improves materially | Non-degenerate top-20 > 0 | R3A top-20 = 1 | **marginal** |

**Criterion 3 Note**: The script reported "best=20" from degenerate R3C (ΔQ=0 everywhere
produces spurious K/K overlap). The actual non-degenerate best is R3A top-20=**1**. One
pair in the top-20 barely clears zero; this is not a material improvement (expected 0.3 by
chance; 1 is ~3× but not statistically meaningful).

**Pre-specified outcome: all three criteria FAIL under a fair interpretation.**

---

## 3. Results by Variant

### R2 — PDF-Pair Local Objective

The M1-fitted parameters give **ρ_pdf = −0.072** (negative) when evaluated on PDF pairs only.

The R2 optimizer collapses to α_r = α_d = −39.52 (stability boundary), producing ΔQ = 0.
This is the highest achievable PDF-pair objective: no α value produces positive PDF-specific
Spearman. The model anti-predicts PDF pairs.

**Finding**: The 1260 non-PDF pairs are not diluting a real PDF signal — there is no
positive PDF-pair Spearman to be found within the scalar-α Lyapunov architecture.

### R3 — Sparse Forward Model

R3A (ADMM sparsification) improves top-20 overlap from 0 to 1 (marginally above zero).
The sparsification changes which pairs appear in the model's top-20: one PDF pair now
enters (vs. zero in dense R1). However:
- Top-100 overlap is 11 vs 7.6 expected by chance (1.4× — barely above chance)
- The ADMM selects based on Lyapunov covariance structure (RMEL/AVDL-dominated), not on
  the ADEL-centric signal in the observed data
- ρ DECREASES from 0.062 to 0.033 after sparsification

The sparsification does not repair the architecture. The ranking failure persists.

**Finding**: Sparsity mismatch is a contributing factor but not the root cause.

### R4 — Stronger Degree Control (Source-Out-Degree-Preserving Target Shuffle)

All 100 random target assignments (preserving only source identity and out-degree) achieve
EXACTLY ρ = 0.0618, identical to M1. Empirical p-value = 1.000.

This is more stringent than D2: the edge-swap null preserved BOTH source and target degree,
while R4 randomizes target identity entirely. The result is the same: complete degeneracy.

**Finding**: The predictive power of M1 comes entirely from knowing which 5 neurons
are PDF sources with what out-degree. The specific source→target pairings (ADEL→URYVR
vs. ADEL→any other pdfr-1 neuron) contribute ZERO additional information.

### R5 — α Sensitivity

The sensitivity ∂ΔQ/∂α_d is 7.17× more concentrated on PDF Class 4 pairs than non-PDF.
The leverage ratio ||∂ΔQ/∂α_d|| / ||ΔQ_M1|| = 0.443.

**Finding**: The architecture IS structurally sensitive to PDF pairs in aggregate.
However, the sensitivity is dominated by RMEL–RMER (mutual feedback loop in P) and
AVDL–RMEL, not by ADEL-centric pairs. The 7× concentration on PDF pairs does not
translate to useful prediction because the model is "looking at the wrong PDF pairs."

---

## 4. Root-Cause Diagnosis

The five diagnostics (D1–D5) and four revision models (R2–R5) together produce a
coherent explanation of the architecture failure:

### Primary cause: RMEL↔RMER mutual feedback dominates Lyapunov dynamics

The Bentley P matrix contains RMEL→RMER and RMER→RMEL (both sources are also targets
of each other). This mutual feedback loop creates a strong resonance in the Lyapunov
dynamics at large inhibitory α. The model predicts RMEL–RMER as the #1 most-changed
pair (|ΔQ_pred| = 0.151), followed by AVDL–RMEL (0.115).

In the OBSERVED data, RMEL–RMER is at rank 32 (|ΔQ_obs| = 0.058). The model's top
prediction has a 7× overestimate of its observed signal.

### Secondary cause: ADEL has no mutual loop in P

ADEL's 16 targets in P are all one-directional (ADEL→target, but none of ADEL's targets
→ADEL in P). This means ADEL has no Lyapunov resonance amplification. At the fitted
inhibitory α, ADEL–URYVR and ADEL–URYDL appear at ranks 245 and 107 (predicted), while
they appear at ranks 5 and 9 (observed).

### Consequence: Anti-correlation at PDF-pair level

The model's PDF predictions are ANTI-correlated with the observed PDF ΔQ (ρ_pdf = −0.072).
Pairs the model predicts highest (RMEL–RMER, AVDL–RMEL) are not among the highest observed.
Pairs observed highest (ADEL–URYVR, ADEL–URYDL) are not among the highest predicted.

### Why all degree-preserving nulls give identical ρ

At large |α| (the plateau found in D4), the Lyapunov dynamics are dominated by the
spectral structure of P, which depends primarily on the degree sequence. Since P,
D2-swapped P, and R4-shuffled P all have the same degree sequence, they all produce
the same ΔQ ranking at the plateau. The specific wiring adds no information.

---

## 5. What R5 Tells Us About Model Families

R5 is the one finding that distinguishes architecture failure from hypothesis failure:

**Architecture failure (confirmed)**: The scalar Lyapunov model cannot distinguish
ADEL-centric from RMEL-centric PDF signal because it does not have neuron-specific
sensitivity. A scalar α gives all 5 sources the same gain.

**Hypothesis status (unresolved)**: If a SOURCE-SPECIFIC α were permitted (one α per
PDF source neuron: α_RID, α_ADEL, α_RMEL, α_RMER, α_AVDL), the model WOULD have
differential leverage. Specifically, an architecture that suppresses RMEL/RMER gain
while enhancing ADEL gain could in principle predict the observed pattern. R5's 7×
PDF concentration confirms the architecture is responsive; it's the equal-gain
constraint that breaks it.

This distinction is important: the hypothesis (PDF architecture predicts ΔQ) is NOT
falsified by Phase 3A. It is untested, because the scalar-α architecture is not
sensitive enough to test it.

---

## 6. Decision Criteria and Recommendation

The authorization specifies:

> If no architecture satisfies these criteria: STOP. Do not consume held-out ADEL
> pairs. Recommend termination of this model family.

**Criteria assessment**:
- Criterion 1 (M1 > degree-matched null): FAIL (p = 1.000; confirmed by both D2 and R4)
- Criterion 2 (PDF identity matters): FAIL (margin = 0; confirmed by D2 and R4)
- Criterion 3 (top-20 > 0): marginal (R3A = 1; artifact-free count is 1, not 20)

**Formal recommendation**: The scalar-α Lyapunov model family FAILS all success
criteria under the locked Phase 3A constraints. Per the authorization, this triggers
the termination path for THIS MODEL FAMILY.

**This is a model family termination, not a hypothesis termination.** The R5 finding
(7× sensitivity concentration; identifiability requires neuron-class-specific α)
provides a specific architectural direction for a revised model family if authorized.

---

## 7. What the Held-Out ADEL Evaluation Would Contribute

The D1 preview showed 3/4 ADEL held-out pairs in the top 12.9% of predictions:
- ADEL–URYDL: rank 107 (top 8.1%)
- ADEL–RMEL: rank 108 (top 8.2%)
- ADEL–URXL: rank 171 (top 12.9%)
- ADEL–URYVR: rank 245 (top 18.6%, narrowly outside top 15%)

Given:
1. The model anti-predicts PDF pairs (ρ_pdf = −0.072)
2. R4 confirms predictions driven by source degree, not ADEL-specific wiring
3. ADEL's predicted high rank is likely because ADEL's 16 out-edges (= high source degree) happen to place its targets in the model's moderately-predicted region

Consuming the held-out evaluation on the current scalar-α model would NOT be informative.
Even if 3/4 ADEL pairs meet the top-15% rank criterion (likely by degree-structure artifact,
not by genuine prediction), this would not validate the PDF hypothesis under the current
architecture's known failures.

**The held-out evaluation should be reserved for a model that passes at least Criterion 2
(PDF identity matters beyond degree structure).**

---

## 8. Stop Condition

**Phase 3A.6 is complete.**

**DO NOT**: evaluate held-out ADEL pairs, begin Phase 3B, introduce new model complexity
within the scalar-α framework.

**Awaiting human review** for one of:
A. Authorization to terminate the scalar-α Lyapunov model family (recommended)
B. Authorization to develop a revised model family (e.g., source-class-specific α)
   addressing the RMEL↔RMER feedback dominance, with new success criteria

---

## 9. Output Files

| File | Location |
|---|---|
| phase3a6_architecture_revision_report.md | results/phase3/ |
| revision_results.json | results/phase3/revision/ |
| r2_pdf_local.md | results/phase3/revision/ |
| r3_sparse_forward.md | results/phase3/revision/ |
| r4_degree_control.md | results/phase3/revision/ |
| r5_alpha_sensitivity.md | results/phase3/revision/ |
| r4_rho_distribution.npy | results/phase3/revision/ |
| r4_alpha.npy | results/phase3/revision/ |
| r5_dDQ_dAlphaR.npy | results/phase3/revision/ |
| r5_dDQ_dAlphaD.npy | results/phase3/revision/ |
