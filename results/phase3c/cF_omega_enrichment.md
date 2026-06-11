# Phase 3C-F1 — Full Ω Enrichment Analysis
Date: 2026-06-03
Authorization: Phase 3C-F

## Setup

ΔΩ_full = D_emp @ ΔQ, where D_emp = Cov(Δx) is the 61×61 empirical diffusion
matrix from Phase 3C-E. This is a full matrix multiplication (not elementwise).

All enrichment tests use: AUROC + Mann-Whitney analytical p, Fisher top-K (K=20),
simple permutation null (500 perms), degree-preserving null (A_raw degree, 10 bins).

Phase 2 baseline values reproduced exactly for Bentley PDF and serotonin
(annotation counts match: PDF=61, serotonin=33, combined=94 Class 4 pairs).

**Note on Neuropeptide broad annotation**: The Phase 2 pep_61 matrix (972/1321 C4 pairs,
73.6%) could not be reconstructed from source data; the CeNGEN reconstruction covers
100% of C4 pairs and is degenerate. This annotation is excluded from F1.

**Note on Randi unc-31**: Phase 2 had 108 C4 pairs; Phase 3C-F reconstruction gives
91 C4 pairs at q<0.10 threshold (within 16% of Phase 2). Results are directionally
comparable.

---

## F1 Results: CePNEM

### Bentley PDF (n=61 Class 4 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5560 | **0.6644** | **+0.108** |
| p_deg_perm AUROC | 0.024 | **0.000** | **improved** |
| Fisher OR (top-20) | 5.46 | **7.41** | **+1.95** |
| p_deg_perm Fisher | 0.008 | **0.000** | **improved** |
| Top-20 annotated | 4 | **5** | +1 |
| Expected in top-20 | 0.9 | 0.9 | — |
| AUROC pass | **PASS** | **PASS** | maintained |
| Fisher pass | **PASS** | **PASS** | maintained |

**Strongest improvement in the dataset.** AUROC increases by 0.108 (from 0.556 to 0.664),
pushing into the region of strong enrichment. The degree-permutation p-value drops from
0.024 to < 0.002 (500-permutation resolution). Fisher OR increases from 5.46× to 7.41×;
5 of the top-20 ΔΩ_full pairs are PDF-annotated vs 4 for ΔQ.

### Bentley Serotonin (n=33 Class 4 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.4953 | 0.5367 | +0.041 |
| p_deg_perm | 0.566 | 0.348 | — |
| AUROC pass | FAIL | FAIL | — |
| Fisher pass | FAIL | FAIL | — |

No serotonin pairs enter the top-20 under either ΔQ or ΔΩ_full. The small AUROC
increase (+0.041) is not significant. Serotonin enrichment remains a null result.

### Bentley Combined — Serotonin OR PDF (n=94 Class 4 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5356 | **0.6231** | **+0.088** |
| p_deg_perm AUROC | 0.048 | **0.000** | **improved** |
| Fisher OR (top-20) | 3.36 | **4.54** | +1.18 |
| p_deg_perm Fisher | 0.058 | **0.008** | **PASS** |
| AUROC pass | PASS | PASS | maintained |
| Fisher pass | FAIL | **PASS** | **upgraded** |

The combined annotation upgrades from AUROC-only PASS to both AUROC and Fisher PASS.
This is driven by the PDF component (serotonin remains null); the combined annotation
inherits the PDF improvement.

### CeNGEN Serotonin/PDF (n=382 Class 4 pairs; CeNGEN conservative)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5221 | 0.5174 | −0.005 |
| p_deg_perm | 0.004 | 0.164 | **degraded** |
| AUROC pass | PASS | FAIL | **degraded** |

The CeNGEN annotation (382 pairs, 28.9% of Class 4) degrades under ΔΩ_full.
The broad coverage of this annotation means it responds to global reordering effects
from the full D_emp mixing, diluting the signal.

### Randi unc-31 (n=91 C4 pairs; Phase 2: 108)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5007 | 0.4905 | −0.010 |
| p_deg_perm | 0.498 | 0.656 | — |
| AUROC pass | FAIL | FAIL | — |

Randi unc-31 is a null result in both ΔQ and ΔΩ_full. No change in conclusion.

---

## F1 Results: GCaMP

### Bentley PDF (n=61 Class 4 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5260 | 0.4879 | **−0.038** |
| p_deg_perm | 0.256 | 0.664 | degraded |
| AUROC pass | FAIL | FAIL | — |

GCaMP PDF enrichment **degrades** under ΔΩ_full. This contrasts sharply with CePNEM.
The GCaMP D_emp mixing dilutes rather than concentrates the PDF signal.

### Bentley Serotonin (n=33 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.4286 | 0.5151 | +0.087 |
| Fisher OR | 2.09 | 4.55 | +2.46 |
| p_deg_perm Fisher | 0.367 | 0.096 | improved |
| Any pass | FAIL | FAIL | — |

Marginal improvement in GCaMP serotonin but still not significant.

### Bentley Combined (n=94 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.4910 | 0.4975 | +0.007 |
| Any pass | FAIL | FAIL | — |

### CeNGEN serotonin/PDF (n=382 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.5350 | 0.5574 | +0.022 |
| p_deg_perm | 0.008 | **0.000** | improved |
| AUROC pass | PASS | PASS | maintained |
| Fisher pass | FAIL | FAIL | — |

Minor CeNGEN AUROC improvement in GCaMP under ΔΩ_full (+0.022). Both still PASS
on AUROC alone; neither passes Fisher.

### Randi (n=91 pairs)

| Metric | ΔQ | ΔΩ_full | Change |
|---|---|---|---|
| AUROC | 0.4644 | 0.4493 | −0.015 |
| Any pass | FAIL | FAIL | — |

---

## Summary Table: All Annotations, Both Coordinates

| Annotation | CePNEM ΔQ AUROC | CePNEM ΔΩ AUROC | ΔAUROC (cep) | GCaMP ΔQ AUROC | GCaMP ΔΩ AUROC | ΔAUROC (g) |
|---|---|---|---|---|---|---|
| **Bentley PDF** | 0.556 | **0.664** | **+0.108** | 0.526 | 0.488 | −0.038 |
| Bentley serotonin | 0.495 | 0.537 | +0.042 | 0.429 | 0.515 | +0.087 |
| Bentley combined | 0.536 | **0.623** | **+0.088** | 0.491 | 0.498 | +0.007 |
| CeNGEN ser/PDF | 0.522 | 0.517 | −0.005 | 0.535 | 0.557 | +0.022 |
| Randi unc-31 | 0.501 | 0.491 | −0.010 | 0.464 | 0.449 | −0.015 |

### Pass/Fail summary

| Annotation | CePNEM ΔQ | CePNEM ΔΩ | GCaMP ΔQ | GCaMP ΔΩ |
|---|---|---|---|---|
| Bentley PDF | **PASS** | **PASS** | FAIL | FAIL |
| Bentley serotonin | FAIL | FAIL | FAIL | FAIL |
| Bentley combined | AUROC only | **BOTH** | FAIL | FAIL |
| CeNGEN ser/PDF | AUROC only | FAIL | AUROC only | AUROC only |
| Randi unc-31 | FAIL | FAIL | FAIL | FAIL |

---

## Key Conclusion

**ΔΩ_full strengthens the Bentley PDF signal in CePNEM only.**

The improvement is substantial (AUROC +0.108, OR +1.95) and raises the Bentley
combined annotation from AUROC-only to both-tests PASS. This is the only annotation
and coordinate where ΔΩ_full yields a genuine scientific improvement.

The improvement is CePNEM-specific. In GCaMP, the PDF signal degrades (AUROC −0.038)
and the improvement pattern is absent or marginal for all other annotations.

The CeNGEN annotation degrades in CePNEM (PASS→FAIL) under ΔΩ_full, indicating
that the D_emp mixing has unequal effects across annotation types and annotation density.

---

*3C-F1 scope: enrichment characterization only. No new fitting. No held-out evaluation.*
