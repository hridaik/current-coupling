# Phase 3C-G5 — Primary Object Assessment
Date: 2026-06-03
Authorization: Phase 3C-G

---

## The Evidence

Phase 3C-G produced four findings that directly answer the primary-object question:

**G1 (Movement table)**: All 20 largest upward-moving PDF pairs had ΔQ = 0.000.
They gain nonzero ΔΩ entirely through D_emp imputation.

**G2 (Source attribution)**: ADEL is neutral (mean Δrank = +2.9 ≈ 0). The AUROC gain
is driven by RID/RMEL/RMER pairs (mean Δrank +215 to +353), none of which are the
Phase 2 primary predictions.

**G3 (Top-20)**: 18/20 top pairs unchanged. The top-20 is not restructured.

**G4 (AUROC mechanism)**: Mechanism B confirmed. +31,082 concordant pairs added by
imputing nonzero ΔΩ for zero-ΔQ PDF pairs. The imputation is driven by hub position
of RID/RMEL/RMER in the CePNEM diffusion structure.

---

## Primary Object Assessment

```
[x] ΔQ primary, Ω secondary (or not used)
[ ] Ω primary, Q special case
```

**ΔQ is the primary object. ΔΩ_full should not be presented as primary, and
the Phase 3C-F AUROC increase should not be reported as a scientific finding
without the explanation from Phase 3C-G.**

---

## Justification

### 1. The AUROC increase is an imputation artifact, not a signal

The +0.108 AUROC increase does not reflect new evidence about state-dependent
functional connectivity. It reflects the D_emp operation assigning nonzero
predicted values to pairs that the graphical lasso explicitly regularized to zero.

The graphical lasso sets ΔQ = 0 for a pair when the data provide insufficient
evidence for state-dependent conditional dependence, after accounting for all
other pairwise relationships. This is the correct statistical decision. D_emp
overrides this decision by spreading signal from neighboring neurons, without
any additional data supporting those pairs.

Reporting ΔΩ_full AUROC = 0.664 as the primary enrichment result would imply
that 31 additional PDF pairs have state-dependent signal that the data actually
do not support.

### 2. ADEL predictions are unchanged — the primary motivation is unaffected

The Phase 3C-F framing suggested ΔΩ_full might strengthen the ADEL→URY predictions.
The sanity check shows this is false:

| ADEL pair | ΔQ rank | ΔΩ rank | Δrank |
|---|---|---|---|
| ADEL–URYVR | 5 | 5 | 0 |
| ADEL–URYDL | 9 | 7 | +2 |
| ADEL–RMEL | 10 | 8 | +2 |
| ADEL–URXL | 59 | 59 | 0 |

The primary ADEL predictions are at ranks 5, 9/7, 10/8, 59. The changes (+2 positions
for ADEL–URYDL and ADEL–RMEL) are within noise. The D_emp operation does not
strengthen the ADEL case.

### 3. ΔΩ_full violates the model identity

The original motivation for Ω was Q = D^{-1}(Ω − A), with D the diagonal noise
matrix. Phase 3C established that under this model, ΔΩ ≡ D·ΔQ ≈ ΔQ.

Phase 3C-E used D_emp = Cov(Δx) — the full off-diagonal first-difference covariance —
as the D matrix. This produces D_emp @ ΔQ, which is NOT the model Ω. In the model,
Ω[i,j] = D[i,i] × Q[i,j] + A[i,j] (row-scaling by diagonal only). The full matrix
product D_emp @ ΔQ has no direct correspondence to model Ω.

Presenting D_emp @ ΔQ as "current organization" would misrepresent the theoretical
object.

### 4. The coordinate inconsistency is explained and is not recoverable

GCaMP PDF AUROC DECREASES under ΔΩ_full (0.526 → 0.488). The G2 analysis explains
why: AVDL (mean Δrank = −80) is the largest source in GCaMP, and AVDL's diffusion
structure in GCaMP D_emp does not connect to high-ΔQ neighbors. The CePNEM improvement
is specific to the RID/RMEL/RMER hub structure in CePNEM residuals.

This coordinate inconsistency is not a model property — it is an artifact of the
specific D_emp estimated from each modality.

---

## What ΔΩ_full Does Offer (Limited)

The analysis is not without value:

1. **Robustness confirmation**: The Phase 2 top-tier predictions (ranks 1–20)
   are stable under the D_emp mixing. ADEL→URYVR remains rank 5 regardless of
   whether D is diagonal or full.

2. **Diffusion structure characterization**: The D_emp analysis (Phase 3C-E)
   revealed that RID and RMEL/RMER are diffusion hubs in CePNEM residuals.
   This is a finding about the measurement modality (CePNEM), not about the
   biology being measured.

3. **Documentation of a null pathway**: Phase 3C-G completes the investigation
   of the Ω pathway. The conclusion — that ΔΩ_full does not improve the primary
   predictions and its AUROC gain is an imputation artifact — is a clear result
   that justifies terminating the Ω pathway.

---

## Recommended Manuscript Treatment

**ΔQ is the primary summary statistic.** The manuscript can note:

> "The current organization Ω = D Q + A, under the diagonal noise model appropriate
> for CePNEM, produces ΔΩ = D · ΔQ — numerically equivalent to ΔQ (Spearman ρ > 0.9999)
> under z-scored residuals (Phase 3C). Using the full empirical diffusion matrix
> D_emp = Cov(Δx) changes the ranking of zero-ΔQ PDF pairs but does not affect
> the top-tier predictions (ADEL→URYVR, URYDL, RMEL at ranks 5, 9, 10 in ΔQ;
> 5, 7, 8 in D_emp @ ΔQ). The primary analysis uses ΔQ."

**Do NOT report:**
- ΔΩ_full AUROC = 0.664 as a primary result
- The D_emp @ ΔQ operation as "current organization" in the model sense
- The AUROC increase as strengthening the ADEL predictions

---

## Final Judgment on Phase 3C

Phase 3C (including sub-phases E, F, G) is a complete theoretical validation exercise
that reached the following conclusion:

**ΔQ is the correct primary object. The Ω pathway, under both the diagonal model
(Phase 3C) and the full empirical diffusion model (Phase 3C-E/F/G), does not
improve the primary scientific predictions or provide interpretable new biology.**

The Phase 3C-D termination recommendation stands:

> [x] Terminate Ω pathway
> [ ] Continue Ω pathway

**Phase 3C: STOP. Awaiting human review before held-out evaluation.**

---

*3C-G5 scope: assessment only. No new analysis.*
