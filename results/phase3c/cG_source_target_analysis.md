# Phase 3C-G2 — Source/Target Attribution
Date: 2026-06-03
Authorization: Phase 3C-G

## Setup

PDF sources: neurons that contribute directed edges in the Bentley ESconnectome
(pdf-1 / pdf-2 ligand-producing neurons).

PDF targets: neurons expressing pdfr-1 in the Bentley annotation.

---

## By Source Neuron

| Source | n pairs | Mean Δrank | Median Δrank | n upward | n downward | Direction |
|---|---|---|---|---|---|---|
| **RID** | 14 | **+352.6** | **+344.5** | 12 | 2 | Strongly UP |
| **RMEL** | 14 | **+281.8** | **+185.0** | 10 | 4 | Strongly UP |
| **RMER** | 13 | **+214.3** | **+293.0** | 11 | 2 | Strongly UP |
| ADEL | 12 | +2.9 | 0.0 | 5 | 5 | **Neutral** |
| AVDL | 15 | **−80.4** | **−52.0** | 6 | 9 | **DOWN** |

### Critical finding: ADEL is neutral; RID/RMEL/RMER drive the gain

**ADEL** (n=12, mean Δrank = +2.9): Essentially no net change. ADEL pairs split evenly
— 5 up, 5 down. The top ADEL predictions (ADEL–URYVR Δ=0, ADEL–URYDL Δ=+2,
ADEL–RMEL Δ=+2) are essentially preserved, not improved. The AUROC improvement has
nothing to do with ADEL.

**RID** (n=14, mean Δrank = +352.6): All 14 RID pairs had ΔQ = 0. The D_emp matrix
has substantial off-diagonal terms connecting RID to RMEL/RMER (the D_emp top-10
off-diagonal list included RID–RME adjacent entries). RID pairs absorb signal from
RMEL/RMER ΔQ through D_emp mixing, rising from ranks ~500-1300 to ranks ~200-800.

**RMEL/RMER** (n=14/13, mean Δrank +282/+214): RMEL and RMER were already significant
sources in ΔQ (RMEL–RMER bilateral coupling at rank 32). Their off-diagonal D_emp
entries connect to I1, OLQ, OLL, FLP neurons — none of which had ΔQ signal with
RMEL/RMER individually. The D_emp mixing propagates RMEL/RMER's strong bilateral
ΔQ signal outward to all their D_emp-connected neighbors.

**AVDL** (n=15, mean Δrank = −80.4): AVDL pairs are net losers. AVDL has 15 PDF
pairs (the most of any source), predominantly zero-ΔQ. The D_emp mixing drags
AVDL-connected pairs downward, suggesting AVDL's D_emp neighbors have NEGATIVE
ΔQ contributions that mix in through the off-diagonal terms.

---

## By Target Neuron

| Target | n pairs | Mean Δrank | Largest pair gain | Direction |
|---|---|---|---|---|
| FLPL | 2 | **+731.5** | FLPL–RMEL (+878), FLPL–RMER (+585) | Strongly UP |
| I1L | 5 | **+445.4** | I1L–RMEL (+743), I1L–RMER (+599) | Strongly UP |
| OLQVL | 5 | **+373.2** | OLQVL–RID (+665), OLQVL–RMEL (+604) | Strongly UP |
| URYVR | 5 | **+287.6** | RID–URYVR (+665), RMER–URYVR (+332) | Strongly UP |
| RMEL | 14 | **+281.8** | I1R–RMEL (+1042) | Strongly UP |
| OLQDR | 4 | **+256.5** | OLQDR–RMEL (+803), OLQDR–RID (+573) | Strongly UP |
| OLLL | 3 | **+225.7** | OLLL–RID (+542), OLLL–RMER (+504) | Strongly UP |
| RMER | 13 | **+214.3** | I1L–RMER (+599) | Strongly UP |
| URYDL | 5 | **+195.2** | RID–URYDL (+670), RMER–URYDL (+292) | Strongly UP |
| OLQVR | 4 | **+179.8** | OLQVR–RMEL (+684) | Strongly UP |
| URXL | 5 | **−220.4** | RMEL–URXL (−623), RMER–URXL (−628) | **DOWN** |
| URYVL | 4 | **−444.2** | ADEL–URYVL (−649), AVDL–URYVL (−658) | **DOWN** |

### Target pattern

Targets that GAIN: FLPL, I1L, OLQ neurons, URYVR, URYDL — these are neurons connected
to RID or RMEL/RMER in D_emp. The signal flows RMEL → FLPL/I1/OLQ via D_emp
off-diagonal terms (reflecting co-fluctuation in first-differences).

Targets that LOSE: URXL and URYVL — both receive signal from sources (ADEL, AVDL,
RMEL, RMER) that have competing D_emp contributions with negative sign, pulling their
ΔΩ downward.

---

## ADEL vs Non-ADEL Attribution

| Group | n pairs | Mean Δrank | Median Δrank |
|---|---|---|---|
| ADEL-involved | 12 | **+2.9** | **0.0** |
| Non-ADEL PDF | 49 | **+194.2** | **+166.0** |

The AUROC improvement is driven almost entirely by **non-ADEL PDF pairs**. ADEL's
contribution to the AUROC increase is negligible (mean Δrank ≈ 0).

### The ADEL picture in full

| ADEL pair | ΔQ rank | ΔΩ rank | Δrank |
|---|---|---|---|
| ADEL–URYVR | 5 | 5 | **0** |
| ADEL–URYDL | 9 | 7 | **+2** |
| ADEL–RMEL | 10 | 8 | **+2** |
| ADEL–URXL | 59 | 59 | **0** |
| ADEL–OLQDL | 541 | 373 | +168 (ΔQ=0, imputed) |
| ADEL–OLQVL | 1139 | 516 | +623 (ΔQ=0, imputed) |
| ADEL–I1L | 922 | 459 | +463 (ΔQ=0, imputed) |
| ADEL–OLQDR | 542 | 642 | −100 (ΔQ=0, imputed↓) |
| ADEL–OLLR | 549 | 673 | −124 (ΔQ=0, imputed↓) |
| ADEL–I1R | 932 | 1263 | −331 (ΔQ=0, imputed↓) |
| ADEL–URYVL | 523 | 1172 | −649 (ΔQ=0, imputed↓) |
| ADEL–OLQVR | 121 | 140 | −19 (small ΔQ, pulled down) |

The four ADEL predictions from Phase 2 (URYVR, URYDL, RMEL, URXL) are essentially
**unaffected** by the D_emp mixing. Their ranks change by 0–2 positions. The movement
in ADEL's zero-ΔQ pairs (OLQDL, OLQVL, etc.) is a byproduct of D_emp mixing, not
a validated biological signal.

---

## Summary

**The AUROC improvement is driven by RID/RMEL/RMER source neurons lifting
their zero-ΔQ PDF pairs into the middle ranks via D_emp imputation.**

ADEL predictions are unaffected. AVDL pairs are net losers. The signal pattern
is entirely explained by the D_emp off-diagonal structure connecting RID and
RMEL/RMER to inner-labial (I1, I2), head mechanosensory (OLQ, OLL), and
aerotaxis (URY) neurons.

---

*3C-G2 scope: attribution analysis only.*
