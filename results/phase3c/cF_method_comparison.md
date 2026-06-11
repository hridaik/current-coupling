# Phase 3C-F4 — Method Comparison: ΔQ vs ΔΩ_full
Date: 2026-06-03
Authorization: Phase 3C-F

## Question

Which object is better for this dataset?

```
A. ΔQ
B. ΔΩ_full = D_emp @ ΔQ
```

Criteria: enrichment strength, biological coherence, robustness, interpretability.

---

## Criterion 1: Enrichment Strength

### CePNEM

| Annotation | ΔQ AUROC | ΔΩ AUROC | Winner |
|---|---|---|---|
| Bentley PDF | 0.556 (PASS) | **0.664** (PASS) | **ΔΩ_full** |
| Bentley combined | 0.536 (PASS) | **0.623** (PASS) | **ΔΩ_full** |
| CeNGEN ser/PDF | 0.522 (PASS) | 0.517 (FAIL) | **ΔQ** |
| Randi unc-31 | null | null | tie |

**CePNEM verdict**: ΔΩ_full wins on the biologically motivated (Bentley PDF, +0.108)
and combined (+0.088) annotations. ΔQ wins on the broad CeNGEN annotation.
Net: ΔΩ_full is better for targeted annotations; mixed for broad annotations.

### GCaMP

| Annotation | ΔQ AUROC | ΔΩ AUROC | Winner |
|---|---|---|---|
| Bentley PDF | 0.526 (FAIL) | 0.488 (FAIL) | **ΔQ** |
| Bentley combined | 0.491 (FAIL) | 0.498 (FAIL) | tie |
| CeNGEN ser/PDF | 0.535 (PASS) | 0.557 (PASS) | **ΔΩ_full** |
| Randi unc-31 | null | null | tie |

**GCaMP verdict**: ΔQ wins for PDF; ΔΩ_full wins slightly for CeNGEN. No clear winner.

### Summary

ΔΩ_full is unambiguously better for **CePNEM × Bentley PDF** (the primary pre-specified
annotation, AUROC 0.664 vs 0.556). For all other annotation/coordinate combinations
the advantage is mixed or absent.

**Enrichment winner: ΔΩ_full for the primary annotation in the primary coordinate.**

---

## Criterion 2: Biological Coherence

### ADEL predictions under ΔΩ_full

The key Phase 2 predictions (ADEL→URYVR rank 5, ADEL→URYDL rank 9, ADEL→RMEL rank 10)
are **preserved or improved** under CePNEM ΔΩ_full:

- ADEL–URYVR: rank 5 → rank 5 (unchanged)
- ADEL–URYDL: rank 9 → rank 7 (improved)
- ADEL–RMEL: rank 10 → rank 8 (improved)

The ADEL predictions represent the strongest biological motivation for this analysis
(novel dopaminergic → aerotaxis neuropeptide connections). Their preservation and
strengthening under ΔΩ_full is a positive indicator.

### Block structure coherence

Top-2 block flows (RME↔RME, DA_mech↔URY_URX for CePNEM; RID↔RME, command_IN↔command_IN
for GCaMP) are identical under ΔQ and ΔΩ_full. The biological interpretation of the
dominant reorganization pathways does not change.

### New pair ADEL–I2L (rank 26→18 in CePNEM ΔΩ)

ADEL–I2L enters the top-20 under ΔΩ_full. I2L is a pharyngeal interneuron.
ADEL–I2 functional coupling is not in the Bentley PDF annotation (I2 does not express
pdfr-1), so this is not a primary prediction. It may reflect a secondary diffusion
coupling pathway through shared off-diagonal D_emp terms, not a new biological signal.

**Biological coherence verdict: ΔΩ_full is at least as coherent as ΔQ, with the
core ADEL predictions preserved or improved.**

---

## Criterion 3: Robustness

### Coordinate consistency

ΔQ shows consistent PDF enrichment in CePNEM (PASS, AUROC 0.556) and weak but
directionally consistent enrichment in GCaMP (FAIL, AUROC 0.526).

ΔΩ_full shows STRONGER enrichment in CePNEM (AUROC 0.664) but WEAKER in GCaMP
(AUROC 0.488). This **coordinate inconsistency** is a robustness concern:

- If ΔΩ_full were a fundamentally better summary statistic, it should improve or
  at minimum maintain enrichment in both coordinates.
- The degradation in GCaMP (−0.038 on the primary annotation) suggests the
  improvement in CePNEM is coordinate-specific, not universally valid.

### Why the asymmetry?

CePNEM D_emp off-diagonal structure concentrates signal onto the PDF-relevant block
flows (DA_mech↔URY_URX benefits from ADEL's high-innovation entries). GCaMP D_emp
has different off-diagonal structure (more pharyngeal/motor cross-coupling), which
dilutes rather than amplifies the PDF signal.

This suggests ΔΩ_full improvement is data-specific to CePNEM processing, not a
model-level improvement.

### Annotation breadth effect

The CeNGEN annotation (382 pairs, 29% of Class 4) DEGRADES in CePNEM under ΔΩ_full
while IMPROVING slightly in GCaMP. This opposite behavior across annotations within
the same coordinate further limits the robustness of ΔΩ_full as a universal improvement.

**Robustness verdict: ΔQ is more robust. ΔΩ_full's CePNEM PDF improvement is
coordinate-specific and annotation-density dependent.**

---

## Criterion 4: Interpretability

### ΔQ

ΔQ = Q_roam − Q_dwell is a direct measure of state-dependent change in the
precision (conditional independence) structure. It is the primary output of the
graphical lasso estimation. Each entry has a clear interpretation:

  ΔQ_ij > 0: pair (i,j) becomes MORE conditionally dependent during roaming
  ΔQ_ij < 0: pair (i,j) becomes LESS conditionally dependent during roaming

### ΔΩ_full = D_emp @ ΔQ

ΔΩ_full_ij = Σ_k D_emp[i,k] × ΔQ[k,j]

Each entry is a weighted average of all ΔQ row-i entries, where weights are the
empirical covariance of first-differences between neuron i and neuron k. This is
NOT directly interpretable as "current organization" in the model Q = D^{-1}(Ω-A)
sense — that model requires D to be diagonal.

The operation D_emp @ ΔQ is:
1. NOT the model Ω = D Q + A with D = D_emp (that would give D_emp @ Q, not just ΔQ)
2. NOT directly interpretable as a physical quantity in the CePNEM framework
3. A weighted combination of ΔQ rows using the first-difference covariance structure

While exploratory value exists (it amplifies the PDF signal in CePNEM), the
interpretation requires additional theoretical scaffolding that has not been developed.

**Interpretability verdict: ΔQ is clearly superior. ΔΩ_full requires theoretical
justification that does not currently exist.**

---

## Overall Verdict

| Criterion | Winner | Magnitude |
|---|---|---|
| Enrichment (CePNEM PDF) | **ΔΩ_full** | Strong (+0.108 AUROC) |
| Enrichment (GCaMP PDF) | **ΔQ** | Moderate (+0.038) |
| Enrichment (other annotations) | Mixed | Weak or null |
| Biological coherence | Tie | ADEL preserved in both |
| Robustness (cross-coord) | **ΔQ** | ΔΩ inconsistent |
| Robustness (cross-annot) | **ΔQ** | ΔΩ annotation-dependent |
| Interpretability | **ΔQ** | Clear advantage |

**ΔQ is the more robust and interpretable choice for the primary analysis.**
ΔΩ_full (= D_emp @ ΔQ) shows a specific benefit for the Bentley PDF annotation in
CePNEM that merits reporting as an exploratory finding, but cannot replace ΔQ as
the primary object due to coordinate inconsistency and lack of theoretical grounding.

---

*3C-F4 scope: comparative assessment. No new fitting. No held-out evaluation.*
