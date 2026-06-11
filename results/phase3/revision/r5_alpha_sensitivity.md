# R5 — α Sensitivity Analysis
Date: 2026-06-03
Authorization: Phase 3A.6

## Question

Does α have meaningful leverage on the ΔQ structure?
Is the sensitivity ∂ΔQ/∂α_s concentrated on PDF pairs?
Is the sensitivity large relative to the existing signal?

## Method

Lyapunov sensitivity equation: differentiating J_eff Σ + Σ J_eff^T = −I w.r.t. α_s
gives:

    J_s (∂Σ_s/∂α_s) + (∂Σ_s/∂α_s) J_s^T = −(P Σ_s + Σ_s P^T)

This is another Lyapunov equation solved for ∂Σ_s/∂α_s.

Then: ∂Q_s/∂α_s = −Q_s (∂Σ_s/∂α_s) Q_s

∂ΔQ/∂α_r = ∂Q_r/∂α_r  
∂ΔQ/∂α_d = −∂Q_d/∂α_d

Evaluated at fitted M1 parameters (α_r = −26.25, α_d = −23.97).

## Results

| Metric | ∂ΔQ/∂α_r | ∂ΔQ/∂α_d |
|---|---|---|
| Mean |∂ΔQ/∂α| on PDF Class 4 pairs | 0.02539 | **0.02617** |
| Mean |∂ΔQ/∂α| on non-PDF Class 4 pairs | 0.00354 | **0.00365** |
| **Concentration ratio (PDF/non-PDF)** | **7.18×** | **7.17×** |
| ||∂ΔQ/∂α_d|| / ||ΔQ_M1|| (leverage ratio) | — | **0.443** |
| Nonzero entries of ∂ΔQ/∂α_d | 100% | — |

## Interpretation

**Concentration ratio = 7.17×**: A marginal change in α_d (dwelling PDF gain)
affects PDF Class 4 pairs 7× more than non-PDF Class 4 pairs. The model architecture
IS preferentially sensitive to PDF annotation edges — the 7× concentration is a
structural property of the Lyapunov dynamics at the PDF-annotated entries.

**Leverage ratio = 0.443**: ||∂ΔQ/∂α_d|| ≈ 44% of ||ΔQ_M1||. A unit change in
α_d would produce a ΔQ perturbation 44% as large as the entire fitted ΔQ_M1. This
is a MEANINGFUL perturbation magnitude — α has real leverage on the network structure.

**Nonzero entries = 100%**: The sensitivity matrix is fully dense (same issue as
the prediction — Lyapunov sensitivity is also dense).

## Critical Observation

R5 reveals a structural asymmetry that explains R2 and R4:

The 7× concentration does NOT mean ADEL pairs are sensitive — it means the PDF
annotation as a whole is 7× more sensitive. Within the PDF annotation, RMEL/RMER
pairs (which have mutual feedback loops in P) dominate the sensitivity. The
sensitivity matrix ∂ΔQ/∂α_d is highest for RMEL-RMER and AVDL-RMEL pairs, NOT
for ADEL-URYVR or ADEL-URYDL.

This means: even though α has meaningful leverage on PDF pairs in aggregate, it
has HIGHER leverage on the WRONG PDF pairs (RMEL/RMER-dominated) and LOWER
leverage on the ADEL-centric pairs that carry the observed signal.

## Implication

R5 is the ONLY finding in Phase 3A.6 that provides a pathway to improvement:
if the ADEL-specific sensitivity could be enhanced (e.g., ADEL-specific α in a
neuron-class framework), the model architecture would have real leverage on the
relevant pairs. However, neuron-specific α is prohibited under the scalar-α constraint.

## Files

r5_dDQ_dAlphaR.npy: ∂ΔQ/∂α_r (61×61, Class 4 evaluation)
r5_dDQ_dAlphaD.npy: ∂ΔQ/∂α_d (61×61, Class 4 evaluation)

---
*R5 scope: sensitivity characterization only. No model refitting.*
