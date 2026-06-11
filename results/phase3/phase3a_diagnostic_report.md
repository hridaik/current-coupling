# Phase 3A Diagnostic Report
Date: 2026-06-03
Authorization: Phase 3A.5-D
Status: COMPLETE — awaiting review before held-out evaluation

---

## D1 — Held-Out Preview

Predicted rankings for 4 ADEL held-out pairs under M1 (α_r=-26.25, α_d=-23.97):

| Pair | Predicted rank | Percentile | |ΔQ_pred| |
|---|---|---|---|
| ADEL–URYVR | 245 / 1321 | 18.6th | 0.00671 |
| ADEL–URYDL | 107 / 1321 | 8.1th | 0.04073 |
| ADEL–RMEL | 108 / 1321 | 8.2th | 0.03617 |
| ADEL–URXL | 171 / 1321 | 12.9th | 0.01081 |

Observed ΔQ for these pairs: **NOT consulted.** No success/failure judgment made.

---

## D2 — Randomized-P Null (Corrected, N=100)

Proper 2D fit (52×52) applied independently to each P_rand.

| Metric | M1 (Bentley PDF) | M2 null median | M2 null p95 |
|---|---|---|---|
| ρ_train (Spearman) | **0.0618** | 0.0618 | 0.0618 |

**Empirical p-value P(M2 ≥ M1) = 1.000**

Interpretation:
- p-value near 0: M1 significantly exceeds null (PDF structure adds signal)
- p-value near 1: M1 does not exceed random structure (PDF identity does not matter)

M2 α distribution (roam/dwell): median α_r = -26.25, α_d = -23.97
Compare M1: α_r = -26.25, α_d = -23.97

---

## D3 — PDF Contribution Map

| Rank | Pair | |ΔQ_pdf| | PDF? | Source? |
|---|---|---|---|---|
| 1 | RMEL–RMER | 0.15115 | YES | SRC |
| 2 | AVDL–RMEL | 0.11490 | YES | SRC |
| 3 | OLLL–OLQDL | 0.11381 |  |  |
| 4 | OLLL–URYVR | 0.11225 |  |  |
| 5 | OLLR–OLQDL | 0.11212 |  |  |
| 6 | OLLR–URYVR | 0.11137 |  |  |
| 7 | OLLL–URXL | 0.11101 |  |  |
| 8 | OLLL–OLQDR | 0.11089 |  |  |
| 9 | OLLR–URXL | 0.11012 |  |  |
| 10 | OLQDL–URYVR | 0.11011 |  |  |
| 11 | OLQDL–OLQDR | 0.10941 |  |  |
| 12 | I1R–OLLL | 0.10923 |  |  |
| 13 | OLQDL–URYVL | 0.10922 |  |  |
| 14 | I1R–OLQDL | 0.10906 |  |  |
| 15 | I1R–OLLR | 0.10905 |  |  |
| 16 | I1R–URYVR | 0.10892 |  |  |
| 17 | OLQDR–URYVR | 0.10829 |  |  |
| 18 | URYVL–URYVR | 0.10819 |  |  |
| 19 | OLQDL–URXL | 0.10809 |  |  |
| 20 | I1R–URYVL | 0.10776 |  |  |

Top-K PDF enrichment in predicted list:
- Top-20: 2 PDF pairs (expected 0.9; 2.2×)
- Top-50: 4 PDF pairs (expected 2.3; 1.7×)
- Top-100: 30 PDF pairs (expected 4.6; 6.5×)

Source-neuron concentrations:
- RID: mean |ΔQ_pdf| = 0.0139
- ADEL: mean |ΔQ_pdf| = 0.0127
- RMEL: mean |ΔQ_pdf| = 0.0275
- RMER: mean |ΔQ_pdf| = 0.0272
- AVDL: mean |ΔQ_pdf| = 0.0302

---

## D4 — α Landscape

Sweep 1 (α_r=0, α_d varied): max ρ=0.0390 at α_d=-4.078
Sweep 3 shape: **BROAD PLATEAU — objective weakly sensitive to exact α_d** (97/102 points above half-max)

Optimum boundary-seeking? NO (M1 |α_r|=26.3 vs |α_min|=43.9)

---

## D5 — Sparsity Mismatch

| | Density |
|---|---|
| ΔQ_obs | 18.4% nonzero |
| ΔQ_pred (M1) | 100.0% nonzero |

Top-K overlap enrichment:
- Top-10: 0/10 overlap (0.0× expected)
- Top-20: 0/20 overlap (0.0× expected)
- Top-50: 2/50 overlap (1.06× expected)
- Top-100: 7/100 overlap (0.92× expected)

Conditional Spearman (nonzero-observed pairs only): ρ = 0.0897 (n=243)
Full-pairs Spearman (M1 objective): ρ = 0.0618

---

## Summary for Human Review

| Diagnostic | Question | Finding |
|---|---|---|
| D1 | Are held-out pairs in interesting regime? | See ranks above |
| D2 | Does real PDF beat random PDF? | p-value = 1.000 |
| D3 | Is prediction concentrated at PDF sources? | See top-20 table |
| D4 | Is α optimum sharp or boundary-seeking? | BROAD PLATEAU |
| D5 | Does dense/sparse mismatch explain weak ρ? | Conditional ρ = 0.0897 vs full ρ = 0.0618 |

**STOP. Awaiting human review before held-out evaluation.**
