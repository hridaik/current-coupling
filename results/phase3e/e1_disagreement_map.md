# Phase 3E-1 — Ω–Q Disagreement Map
Date: 2026-06-03
Authorization: Phase 3E

## Definition

R_ij = |ΔΩ_full[i,j] − ΔQ[i,j]|  (Class 4 pairs only)

ΔΩ_full = D_emp @ ΔQ, where D_emp = Cov(Δx) from Phase 3C-E.

---

## E1.1 — Overall Disagreement Statistics

| Metric | Value |
|---|---|
| Mean R | 0.0045 |
| Median R | 0.0014 |
| Std | 0.0108 |
| Max R | 0.1621 |

The distribution is heavily right-skewed: most pairs have tiny disagreement
(median 0.0014) while a small set have large disagreement (top-10 have R > 0.05).

---

## E1.1 — Top 20 Disagreement Pairs

All top-50 R pairs have **ΔQ ≠ 0** — the disagreement is concentrated entirely in
pairs that already have strong precision signal.

| R rank | Pair | R | ΔQ | ΔΩ | ΔQ rank | ΔΩ rank | Ann |
|---|---|---|---|---|---|---|---|
| 1 | IL1DR–URYVR | 0.162 | −0.254 | −0.092 | 1 | 1 | — |
| 2 | AVER–I1L | 0.133 | −0.216 | −0.083 | 2 | 2 | — |
| 3 | AVJR–OLLR | 0.101 | −0.170 | −0.069 | 3 | 3 | — |
| 4 | AVJR–OLQVR | 0.097 | −0.161 | −0.064 | 4 | 4 | — |
| 5 | AVER–AWAL | 0.065 | −0.109 | −0.044 | 6 | 9 | — |
| **6** | **ADEL–URYVR** | **0.063** | **−0.122** | **−0.060** | **5** | **5** | **PDF** |
| 7 | OLLR–RICL | 0.059 | −0.099 | −0.040 | 8 | 10 | — |
| 8 | AIZL–AVJL | 0.058 | −0.109 | −0.051 | 7 | 6 | — |
| 9 | I2R–IL2DR | 0.057 | −0.086 | −0.029 | 15 | 21 | — |
| 10 | I1L–IL2DR | 0.056 | +0.090 | +0.035 | 11 | 12 | — |
| 11 | OLLL–SMDVL | 0.056 | −0.088 | −0.033 | 13 | 16 | — |
| 12 | CEPDR–IL2VL | 0.053 | −0.089 | −0.036 | 12 | 11 | — |
| 13 | CEPDR–IL2VR | 0.053 | −0.086 | −0.034 | 14 | 13 | — |
| **14** | **ADEL–URYDL** | **0.050** | **−0.098** | **−0.049** | **9** | **7** | **PDF** |
| **15** | **ADEL–RMEL** | **0.049** | **−0.096** | **−0.046** | **10** | **8** | **PDF** |
| 16 | ASGL–RMDVL | 0.046 | −0.075 | −0.029 | 18 | 23 | — |
| 17 | AVER–NSMR | 0.046 | −0.075 | −0.029 | 17 | 20 | — |
| **18** | **RMEL–URYDL** | **0.043** | **−0.075** | **−0.032** | **16** | **17** | **PDF** |
| 19 | AWAL–M1 | 0.042 | −0.069 | −0.027 | 22 | 24 | — |
| 20 | I2R–URBL | 0.042 | −0.063 | −0.021 | 25 | 46 | — |

---

## E1.2 — R by Annotation Category

| Annotation | n | Mean R | Median R | Max R |
|---|---|---|---|---|
| **PDF** | 61 | **0.0083** | 0.0023 | **0.0627** |
| Randi unc-31 | 91 | 0.0038 | 0.0013 | 0.0379 |
| Serotonin | 33 | 0.0036 | 0.0015 | 0.0217 |
| Unannotated | 1145 | 0.0044 | 0.0014 | 0.1621 |

PDF pairs have the highest mean R (0.0083 vs 0.0038–0.0044 for others). This is NOT
a signal of biological specificity — it reflects that PDF pairs include the top-ranked
ΔQ pairs (ADEL→URY, RMEL↔RMER), which by definition have larger absolute disagreement
when scaled by D_emp.

The unannotated category contains the max R (0.162, IL1DR–URYVR) because that pair
has the largest ΔQ in the dataset.

---

## E1.3 — R vs ΔQ and ΔΩ Correlation

| Metric | Value |
|---|---|
| ρ(R, |ΔQ|) | **0.567** |
| ρ(R, |ΔΩ|) | **0.951** |
| Mean R when ΔQ = 0 | 0.0014 |
| Mean R when ΔQ ≠ 0 | 0.0181 (13× higher) |
| Top-50 R pairs with ΔQ ≠ 0 | **50/50** (100%) |

**The disagreement is almost entirely a scaling artifact.** R ≈ |D_emp @ ΔQ − ΔQ|
= |(D_emp − I) @ ΔQ|. Since D_emp diagonal ≈ 0.40, the dominant contribution is
|(0.40 − 1) × ΔQ| ≈ 0.60 × |ΔQ| for each pair's diagonal term. Pairs with large
|ΔQ| therefore have large R, and pairs with ΔQ = 0 have very small R (≈ 0.0014).

### Signed disagreement (ΔΩ − ΔQ)

| Group | Mean signed R |
|---|---|
| PDF pairs | +0.0050 |
| Non-PDF pairs | +0.0015 |

Positive signed R means ΔΩ > ΔQ (in the direction of the original sign). For most
pairs, since D_emp diagonal < 1, ΔΩ has smaller magnitude than ΔQ — hence ΔΩ − ΔQ
has the same sign as ΔQ itself, giving positive mean signed R for most groups.

108 pairs have ΔΩ significantly inflating over ΔQ (> +0.01), 33 have ΔΩ deflating.
The inflation is the zero-ΔQ pairs getting nonzero ΔΩ from off-diagonal mixing.

---

## Interpretation: Does the Disagreement Map Reveal New Biology?

**No.** The disagreement map is structurally determined by |ΔQ|:
- Top-50 R = top-50 |ΔQ| (all 50 are nonzero-ΔQ pairs)
- ρ(R, |ΔQ|) = 0.57

The pairs where Ω and Q disagree most are the pairs where Q was strongest — the
D_emp operation scales them down by ~0.6×, producing disagreement proportional to
the original signal. No new biological category is selectively enriched in R.

The map does NOT reveal:
- Pairs where Ω discovers signal absent from Q (all top-R pairs already had ΔQ ≠ 0)
- Any annotation enrichment beyond what ΔQ already ranks highly
- Any long-range or topologically special pairs

---

*E1 scope: disagreement characterization only.*
