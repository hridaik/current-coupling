# Phase 3C-H5 — Localization Analysis
Date: 2026-06-03
Authorization: Phase 3C-H

## Question

What fraction of the AUROC improvement comes from ADEL vs RMEL/RMER vs RID?

---

## Method

Partial AUROC for each source class = fraction of (source-PDF pairs × all 1260 non-PDF pairs)
where the source-PDF pair ranks higher.

Δconcordant = change in concordant pairings from ΔQ to ΔΩ for that source class.

Total Δconcordant = +31,082 (confirmed from Phase 3C-G4: concordance increases from
19,987 to 51,069 across all 61 × 1260 = 76,860 comparisons).

---

## Results by Source

| Source | n PDF pairs | AUROC_ΔQ | AUROC_ΔΩ | ΔAUROC | Δconcordant | % of total |
|---|---|---|---|---|---|---|
| **RID** | 14 | 0.258 | **0.712** | **+0.455** | **+8,020** | **25.8%** |
| **RMER** | 13 | 0.213 | **0.699** | **+0.487** | **+7,973** | **25.7%** |
| **AVDL** | 15 | 0.180 | 0.544 | +0.364 | +6,871 | 22.1% |
| **RMEL** | 14 | 0.408 | **0.797** | **+0.389** | **+6,863** | **22.1%** |
| **ADEL** | 12 | 0.405 | 0.671 | +0.266 | **+4,023** | **12.9%** |

Attributed total: +33,750 (108.6% of actual +31,082; overlap from pairs involving
two sources counted twice).

---

## Key Finding: ADEL Is the Smallest Contributor

**ADEL source pairs account for only 12.9% of the AUROC concordance gain.**

The remaining 87% comes from RID (25.8%), RMER (25.7%), AVDL (22.1%), and RMEL (22.1%).

**RID and RMER together contribute 51.5% of the total AUROC gain** — the largest
combined contribution. Neither RID nor RMER is the primary focus of the Phase 2
biological hypothesis (ADEL→URY is).

---

## Partial AUROC Interpretation

### ADEL (AUROC_ΔQ = 0.405)

ADEL starts below 0.5 in ΔQ because 8 of 12 ADEL PDF pairs have ΔQ=0. In pairwise
comparisons, a zero-ΔQ pair ties (does not win) against any non-PDF pair. The 4
nonzero ADEL pairs (URYVR rank 5, URYDL rank 9, RMEL rank 10, URXL rank 59) beat
many non-PDF pairs, but the 8 zero-pairs contribute 0 wins, dragging the average
below 0.5.

Under ΔΩ, ADEL rises to 0.671. This is because even the 8 zero-ΔQ ADEL pairs now
receive nonzero ΔΩ, some of which are higher than many non-PDF ΔΩ values. However,
this is D_emp imputation, not validated signal.

### RID (AUROC_ΔQ = 0.258)

RID starts very low (0.258) because ALL 14 RID-source pairs have ΔQ = 0. 
Under ΔΩ, RID rises to 0.712 — an exceptional jump of +0.455. This is because RID
has the highest D3 in CePNEM (0.483) and is a diffusion hub, so all 14 zero-ΔQ RID
pairs receive large imputed ΔΩ values. The AUROC improvement for RID is the largest
of any source, but it comes entirely from zero-pair imputation.

### RMEL and RMER

Both start low (0.408 and 0.213 respectively) because most of their PDF pairs had
ΔQ = 0. They have stronger bilateral coupling (RMEL–RMER rank 32 in ΔQ) and their
mutual D_emp off-diagonal terms are the strongest in the network — creating large
imputed ΔΩ for their zero-ΔQ targets.

### AVDL (AUROC_ΔQ = 0.180)

AVDL starts the lowest. All 15 AVDL PDF pairs had ΔQ = 0. AVDL gains +0.364 in
AUROC — but this gain is uneven. AVDL rises to 0.544 (barely above chance). Some
AVDL pairs are imputed upward (AVDL–URYVR +439) while others crash (AVDL–URYVL
−658, AVDL–I1R −595). The AVDL contribution to AUROC gain is the lowest per pair
of all sources (despite 22.1% of total concordance gain due to its 15 pairs).

---

## Localization Summary

| Source | Δ per pair | Biological role | AUROC-gain mechanism |
|---|---|---|---|
| RID | +573 Δconc/pair | PDF neuropeptide modulator (orphan locomotion) | Zero → imputed via high D3 hub |
| RMER | +613 Δconc/pair | GABAergic ring motor (pdf-1 source) | Zero → imputed via RMEL mutual coupling |
| RMEL | +490 Δconc/pair | GABAergic ring motor (pdf-1 source) | Zero → imputed via RMER mutual coupling |
| AVDL | +458 Δconc/pair | Command interneuron (pdf-1 source) | Mixed up/down, weak net gain |
| ADEL | +335 Δconc/pair | Dopaminergic mechano (pdf-1 source) | Mostly zero → marginally imputed |

**ADEL has the lowest gain per pair and the smallest total contribution.**

---

## Answer: Fraction of AUROC Improvement from Each Source

| Source | % of total concordance gain |
|---|---|
| RID | **25.8%** |
| RMER | **25.7%** |
| AVDL | **22.1%** |
| RMEL | **22.1%** |
| **ADEL** | **12.9%** |

**87% of the AUROC improvement comes from sources other than ADEL.**

The AUROC improvement is driven by RID/RMEL/RMER hub structure in D_emp, not by
strengthening the ADEL-centered hypothesis that motivated Phase 2.

---

*3C-H5 scope: localization analysis only.*
