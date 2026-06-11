# Phase 3C-H4 — Sparsity Audit
Date: 2026-06-03
Authorization: Phase 3C-H

## Question

Is ΔΩ_full selectively rescuing biologically meaningful pairs, or uniformly propagating signal?

---

## Background

The graphical-lasso ADMM estimator (confirmation estimator, λ_off=0.10) sets ΔQ = 0
for 1078 of 1321 Class 4 pairs (81.6%). These pairs had insufficient evidence for
state-dependent conditional dependence after regularization.

Under ΔΩ_full = D_emp @ ΔQ, all 1078 zero-ΔQ pairs receive nonzero ΔΩ (100%
"rescued") because the off-diagonal D_emp terms mix in nonzero ΔQ from neighboring neurons.

---

## Rescue Rate by Annotation

| Annotation | Total C4 | Rescued (ΔQ=0 → ΔΩ≠0) | Rescue rate | Always nonzero |
|---|---|---|---|---|
| **Bentley PDF** | 61 | 44 | **72.1%** | 17 |
| Bentley serotonin | 33 | 27 | 81.8% | 6 |
| Bentley combined | 94 | 71 | 75.5% | 23 |
| CeNGEN ser/PDF | 382 | 300 | 78.5% | 82 |
| Randi unc-31 | 91 | 74 | 81.3% | 17 |
| **Unannotated** | 817 | **678** | **83.0%** | 139 |

Total zero-ΔQ pairs: 1078 (all rescued by D_emp).

---

## Critical Finding: No Selective Rescue

**Unannotated pairs are rescued at a HIGHER rate (83.0%) than any annotated category.**

Bentley PDF pairs have the LOWEST rescue rate (72.1%) — meaning proportionally fewer
PDF zero-ΔQ pairs gain nonzero ΔΩ compared to random unannotated pairs.

This definitively answers the H4 question: **D_emp is NOT selectively rescuing
biologically meaningful pairs.** The rescue operation is driven entirely by the
structural properties of D_emp, which are agnostic to the Bentley annotation.

---

## Why PDF Pairs Have Lower Rescue Rate

17/61 PDF pairs have nonzero ΔQ ("always nonzero") — they were above the graphical
lasso threshold. This 28% nonzero rate is higher than the Class 4 average (18.4%).
The more PDF pairs that already have nonzero ΔQ, the fewer can be "rescued" (they're
already above zero). The lower rescue rate reflects that PDF pairs are enriched
among the existing nonzero ΔQ pairs — which is the Phase 2 PDF enrichment signal.

PDF pairs are split: 17 nonzero (already enriched in ΔQ top tier) + 44 zero
(indistinguishable from background). The D_emp operation assigns values to all 44
zero-ΔQ PDF pairs, but it does so no more selectively than for zero-ΔQ unannotated pairs.

---

## What Makes Some Rescued PDF Pairs Rise High?

The rescued PDF pairs that gain large ΔΩ (e.g., I1R–RMEL +1042 ranks, FLPL–RMEL +878
ranks) do so NOT because D_emp knows they are PDF pairs, but because:

1. They are pairs between neurons (RMEL, RID) that have HIGH innovation variance (D3)
2. These neurons are hubs in D_emp (large off-diagonal values connecting to many others)
3. The ΔQ signal from RMEL's nonzero pairs (RMEL–URYDL rank 16, RMEL–URYVR rank 21)
   gets mixed into RMEL's zero-ΔQ partners (FLPL–RMEL, I1R–RMEL) via D_emp

**It is the hub position of RMEL/RID in D_emp that elevates these pairs — not their
Bentley PDF annotation.** Any zero-ΔQ pair with a hub neuron (RMEL, RID) would be
elevated similarly, regardless of annotation status.

---

## Quantitative Summary

| Metric | Value |
|---|---|
| Total zero-ΔQ C4 pairs | 1078 (81.6% of 1321) |
| Total rescued (ΔQ=0 → ΔΩ≠0) | 1078 (100%) |
| PDF rescue rate | 72.1% (lower than average) |
| Unannotated rescue rate | 83.0% (higher than PDF) |
| Selectivity index (PDF/unannotated) | 0.87 (< 1 = no selective rescue) |

**Selectivity index < 1**: D_emp rescues unannotated pairs MORE readily than
PDF pairs. The rescue is inversely correlated with biological annotation.

---

## Conclusion

ΔΩ_full does not selectively rescue biologically meaningful pairs. It uniformly
propagates signal from nonzero-ΔQ neurons to their D_emp neighbors, with rescue
rates roughly uniform across all annotation categories (72–83%). The AUROC improvement
arises because the rescued PDF pairs happen to receive LARGER imputed ΔΩ values (due
to RID/RMEL/RMER hub position), not because they are selectively identified.

---

*3C-H4 scope: sparsity audit only.*
