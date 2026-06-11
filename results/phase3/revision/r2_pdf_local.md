# R2 — PDF-Pair Local Objective
Date: 2026-06-03
Authorization: Phase 3A.6

## Question

Can PDF architecture explain the ordering of PDF pairs when the objective is
restricted to PDF training pairs only (57 non-ADEL pairs)?

Is the weak global Spearman (ρ=0.062) caused by 1260 non-PDF pairs diluting the
PDF signal?

## Method

Fitting objective: Spearman rank correlation on 57 non-ADEL PDF Class 4 training
pairs only (instead of all 1317 training Class 4 pairs).

Same grid + Nelder-Mead optimization, same J_base, same P_norm.

## Results

| Metric | M1 (global obj, R1) | R2 (PDF-local obj) |
|---|---|---|
| α_roam | −26.25 | −39.52 (boundary) |
| α_dwell | −23.97 | −39.52 (boundary) |
| ρ_pdf_train (57 pairs) | **−0.072** | 0.000 |
| ρ_global (1317 pairs) | 0.062 | 0.000 |
| AUROC_pdf | 0.919 | 0.500 |
| Top-10 overlap | 0 | artifact† |
| Top-20 overlap | 0 | artifact† |

†When ΔQ_pred = 0 everywhere, top-K overlap = K (spurious; see Note below).

## Key Finding

**R2 collapses to α_r = α_d = α_min (stability boundary)**, producing ΔQ_pred = 0.

The reason: **R1 at the PDF-local objective gives ρ_pdf = −0.072** (negative correlation).
Any parameter value producing nonzero ΔQ has NEGATIVE PDF-pair Spearman. The optimizer
retreats to the boundary (ΔQ = 0 → correlation undefined → treated as 0 > −0.072).

This means:

1. **The model anti-predicts PDF pairs**: the parameters fitted to maximize global
   Spearman predict high |ΔQ_pred| for PDF pairs with LOW observed |ΔQ_obs|, and low
   |ΔQ_pred| for PDF pairs with HIGH observed |ΔQ_obs|. The prediction is inverted
   at the PDF-pair level.

2. **No α value recovers positive PDF Spearman**: restricting the objective to PDF
   pairs does not help — the model structure (Lyapunov + RMEL/AVDL-dominated output)
   is orthogonal to the observed ADEL-centric PDF signal.

3. **The global ρ = 0.062 is driven entirely by non-PDF pairs**: the weak positive
   global Spearman comes from incidental correlations between dense Lyapunov predictions
   and the ~18% nonzero non-PDF pairs. The PDF annotation contributes negatively to
   the objective.

## Note on Top-K Artifact

When DQ_pred = 0 everywhere, the predicted top-K is determined by numpy array ordering,
which happens to match the observed top-K (since both arrays were constructed from the
same ranked Class 4 list). Top-K overlap = K for any zero-ΔQ prediction is a
data-structure artifact, not a meaningful signal.

## Conclusion

R2 **does not** resolve the architecture failure. The PDF-pair-only objective confirms
the model has no useful PDF prediction power — the failure is in the forward model
architecture, not in the dilution by non-PDF pairs.

---
*R2 scope: alternative fitting objective only. No held-out evaluation. No Phase 3B.*
