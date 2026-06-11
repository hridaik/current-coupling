# Phase 3C-H2 — ADEL-Centered Analysis
Date: 2026-06-03
Authorization: Phase 3C-H

## Question

Does ΔΩ_full specifically strengthen the ADEL hypothesis?

---

## Summary Statistics

| Group | n pairs | Mean Δrank | Median Δrank | Top-20 ΔQ | Top-20 ΔΩ | Top-50 ΔQ | Top-50 ΔΩ |
|---|---|---|---|---|---|---|---|
| ADEL PDF pairs | 12 | **+2.9** | **0.0** | **3** | **3** | **3** | **3** |
| ADEL non-PDF pairs | 32 | **+28.6** | **+4.5** | 0 | 1 | 1 | 1 |
| All PDF pairs | 61 | **+156.5** | **+67.0** | 4 | 5 | 7 | 6 |

---

## ADEL PDF Pairs: Complete Movement Table

| Pair | ΔQ rank | ΔΩ rank | Δrank | ΔQ | ΔΩ |
|---|---|---|---|---|---|
| ADEL–URYVR | **5** | **5** | **0** | 0.1222 | 0.0595 |
| ADEL–URYDL | 9 | **7** | **+2** | 0.0980 | 0.0485 |
| ADEL–RMEL | 10 | **8** | **+2** | 0.0957 | 0.0463 |
| ADEL–URXL | 59 | 59 | 0 | 0.0450 | 0.0194 |
| ADEL–OLQDL | 541 | 373 | +168 | 0.0000 | 0.0025 |
| ADEL–OLQVL | 1139 | 516 | +623 | 0.0000 | 0.0018 |
| ADEL–I1L | 922 | 459 | +463 | 0.0000 | 0.0021 |
| ADEL–OLQDR | 542 | 642 | −100 | 0.0000 | 0.0014 |
| ADEL–OLLR | 549 | 673 | −124 | 0.0000 | 0.0014 |
| ADEL–OLQVR | 121 | 140 | −19 | 0.0215 | 0.0080 |
| ADEL–I1R | 932 | 1263 | **−331** | 0.0000 | 0.0001 |
| ADEL–URYVL | 523 | 1172 | **−649** | 0.0000 | 0.0003 |

The 4 pairs with nonzero ΔQ (URYVR, URYDL, RMEL, URXL) show changes of 0, +2, +2, 0.
The 8 zero-ΔQ ADEL pairs split: 3 up, 1 slightly down, 4 significantly down.
**Mean net change = +2.9 ≈ 0.**

### Key observation: ADEL predictions split under D_emp

**Top group (ranks 5, 7, 8, 59)**: ADEL–URYVR, URYDL, RMEL, URXL are essentially
unchanged. These are the Phase 2 primary predictions. ΔΩ does not alter them.

**Upward-imputed ADEL pairs**: ADEL–OLQVL (+623), ADEL–I1L (+463), ADEL–OLQDL (+168)
had ΔQ=0 and gain nonzero ΔΩ through D_emp mixing from ADEL's high-variance
D_emp neighborhood. These are NOT in the Bentley PDF annotation (I1L and OLQ do
not appear as pdfr-1 targets for ADEL). Their upward movement is a D_emp imputation
artifact, not a validated signal.

**Downward-crashed ADEL pairs**: ADEL–URYVL (−649), ADEL–I1R (−331) had ΔQ=0 and
receive NEGATIVE D_emp contributions from specific off-diagonal terms, sending them
to ranks 1172 and 1263. These negative movements are equally artifacts of D_emp
structure.

---

## ADEL Non-PDF Pairs: Selected Movements

| Pair | ΔQ rank | ΔΩ rank | Δrank | Notes |
|---|---|---|---|---|
| ADEL–AVJR | 917 | 194 | +723 | ΔQ=0, imputed upward |
| ADEL–ASGL | 915 | 325 | +590 | ΔQ=0, imputed upward |
| ADEL–IL1DR | 929 | 406 | +523 | ΔQ=0, imputed upward |
| ADEL–I2L | 26 | **18** | +8 | Enters ΔΩ top-20 |
| ADEL–RID | 99 | 86 | +13 | Modest improvement |
| ADEL–M4 | 538 | 1273 | **−735** | ΔQ=0, imputed downward |
| ADEL–RMDDR | 519 | 1275 | **−756** | ΔQ=0, imputed downward |
| ADEL–IL2VL | 534 | 1228 | **−694** | ΔQ=0, imputed downward |

ADEL non-PDF pairs show large symmetric up-and-down movements for zero-ΔQ entries.
ADEL–I2L entering the top-20 under ΔΩ (rank 26→18) is the only meaningful non-PDF
ADEL movement at the top of the distribution.

---

## Does Ω Strengthen the ADEL Hypothesis?

**No. The ADEL hypothesis is unchanged by ΔΩ_full.**

### Evidence:

1. **Top-20 count: 3 → 3** (unchanged). The three ADEL PDF pairs in the ΔQ top-20
   (ADEL–URYVR rank 5, ADEL–URYDL rank 9→7, ADEL–RMEL rank 10→8) remain in the ΔΩ
   top-20 at essentially the same positions.

2. **Mean Δrank of ADEL PDF pairs = +2.9 ≈ 0**. The average rank change across
   all 12 ADEL PDF pairs is essentially zero. For every ADEL pair that moves up,
   another moves down.

3. **The top-4 ADEL predictions are locked**: ADEL–URYVR (rank 5 in both),
   ADEL–URYDL (+2 positions), ADEL–RMEL (+2 positions), ADEL–URXL (unchanged).
   The changes are within the range of tie-breaking noise.

4. **ADEL-specific AUROC gain (H5): +12.9% of total concordance increase.**
   ADEL source pairs are the SMALLEST contributor to the AUROC improvement,
   contributing only 13% of the total +31,082 concordant pairs added.

The ADEL hypothesis is exactly as strong under ΔΩ_full as under ΔQ. The D_emp
operation neither strengthens nor weakens the Phase 2 ADEL predictions.

---

*3C-H2 scope: ADEL analysis only.*
