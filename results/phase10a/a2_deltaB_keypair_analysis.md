# Phase 10A.2 — Does ΔB Explain the ADEL/PDF Current Ranking?
Date: 2026-06-15

## ΔB Computation

ΔB = B_roam − B_dwell  (state-specific effective drift change)
For off-diagonal pairs (i,j): |ΔB_{ij}| = |ΔB[i,j] + ΔB[j,i]| / 2  (symmetrized)
Ranked over all 1321 Class-4 pairs by symmetrized |ΔB|.

## Key Pair Rankings

| Pair | ΔB_sym | |ΔB| Rank | ΔΩ_ss | |ΔΩ_ss| Rank | ΔQ | |ΔQ| Rank |
|------|--------|----------|-------|-------------|-----|---------|
| ADEL–URYVR | 0.0079 | 370 | -0.0688 | 2 | -0.1222 | 5 |
| ADEL–URYDL | 0.0053 | 601 | -0.0498 | 6 | -0.0980 | 9 |
| ADEL–RMEL | 0.0240 | 1 | -0.0549 | 4 | -0.0957 | 10 |
| ADEL–URXL | 0.0083 | 337 | -0.0288 | 29 | -0.0450 | 59 |
| RMEL–URYDL | 0.0120 | 125 | -0.0310 | 23 | -0.0754 | 16 |
| RMEL–URYVR | 0.0093 | 273 | -0.0267 | 34 | -0.0701 | 21 |
| RMEL–RMER | 0.0131 | 95 | -0.0254 | 38 | -0.0579 | 32 |

## Top-20 by |ΔB|

| Rank | Pair | |ΔB| | PDF? |
|------|------|-----|-----|
| 1 | ADEL–RMEL | 0.0240 | Yes |
| 2 | AWBL–RMDDR | 0.0238 | No |
| 3 | I1L–IL2DR | 0.0237 | No |
| 4 | ADEL–M4 | 0.0227 | No |
| 5 | AWBL–RID | 0.0222 | No |
| 6 | FLPL–OLQVR | 0.0209 | No |
| 7 | NSML–RID | 0.0207 | No |
| 8 | NSMR–OLQDR | 0.0204 | No |
| 9 | M4–RMDL | 0.0203 | No |
| 10 | IL1DR–URXL | 0.0203 | No |
| 11 | AVEL–OLQVL | 0.0196 | No |
| 12 | AVAL–IL2VL | 0.0195 | No |
| 13 | AWAL–RMDDR | 0.0195 | No |
| 14 | ASGL–M3R | 0.0192 | No |
| 15 | AIZL–OLLR | 0.0191 | No |
| 16 | ASEL–CEPDR | 0.0190 | No |
| 17 | RID–URXL | 0.0190 | Yes |
| 18 | IL2VR–RICL | 0.0186 | No |
| 19 | AVJR–OLLR | 0.0186 | No |
| 20 | IL1DR–OLQVR | 0.0186 | No |

ADEL pairs in |ΔB| top-20: 2
PDF pairs in |ΔB| top-20: 2

## Question: Are ADEL/PDF Pairs Top-Ranked by ΔB?

YES — at least one ADEL-PDF pair appears in the ΔB top-20.

If ADEL-PDF pairs are NOT top-ranked by |ΔB|, then state-specific effective coupling change does NOT explain their high ranking under ΔΩ_ss.

## Rank Correlations

- Spearman ρ(|ΔB|, |ΔΩ_ss|) on Class-4 = 0.0991
- Spearman ρ(|ΔB|, |ΔQ|) on Class-4 = 0.2126

Interpretation: if ρ is small, ΔB and ΔΩ_ss track different pair-level structure.
If ρ is large, state-specific coupling change is correlated with the current ranking.
