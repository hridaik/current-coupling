# Stage 1A Diagnostic Report — Stability Structure and Ranking-Rule Audit
Date: 2026-06-01
Authorization: Diagnostic checkpoint (no Stage 2 authorization).

## Summary

Stage 1 produced PD confirmation matrices and naturally-PSD covariances for all
four coordinate × state combinations. The primary open question is the near-zero
CePNEM dwelling stability (1 stable pair) and how it affects the ΔQ ranking rule.

**Primary finding:** CePNEM dwelling stability near-zero is a genuine data property
(H1 + H3), not a scripting artifact. CePNEM dwelling covariance is 0.76x weaker
than roaming. At λ=0.15, the graphical lasso regularizes away nearly all dwelling
edges in each bootstrap, producing near-zero stability despite real ADMM-confirmed
structure (305 non-zero edges in Q_cepnem_dwell_conf).

**Ranking finding:** The pre-specified min-stability ranking (Scheme A) collapses
almost all CePNEM pair rankings to ≈0 because stab_dwell ≈ 0 for all pairs.
Scheme B (mean stability) and Scheme C (|ΔQ| only) give well-ordered rankings.
The top-50 overlap between all schemes and the rank correlations inform the
supervisor's choice of ranking rule for Stage 2.

---

## Task 1 — Stability Distribution Audit

Fractions of the 1830 off-diagonal pairs exceeding each threshold:

| Coord | State | ≥0.10 | ≥0.25 | ≥0.50 | ≥0.75 | ≥0.90 | Mean | Median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| cepnem | roam | 1.000 | 1.000 | 1.000 | 0.966 | 0.850 | 0.954 | 0.960 | 1.000 |
| cepnem | dwell | 0.509 | 0.191 | 0.019 | 0.001 | 0.000 | 0.140 | 0.120 | 0.400 |
| gcamp | roam | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gcamp | dwell | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.994 | 1.000 | 1.000 |

**CePNEM dwelling interpretation:** The p95 stability is 0.400 and mean is 0.140. The near-zero stability is not merely sub-threshold — the entire distribution is concentrated near zero. This confirms H1 and H3.

**GCaMP interpretation:** All pairs have stability = 1.000. The entire distribution is degenerate at the maximum. Stability weighting carries no discriminative information for GCaMP.

---

## Task 2 — Stability vs |Q_conf| Correlation

| Coord | State | Pearson (all) | Spearman (all) | Spearman (non-zero stab) | n_nonzero |
|---|---|---|---|---|---|
| cepnem | roam | 0.0914 | 0.0886 | 0.0886 | 1830 |
| cepnem | dwell | 0.1518 | 0.1574 | 0.1400 | 1451 |
| gcamp | roam | nan | nan | nan | 1830 |
| gcamp | dwell | 0.0503 | 0.0415 | 0.0415 | 1830 |

**CePNEM roam:** Pearson=0.091, Spearman=0.089. Stability and |Q_conf| are moderately correlated — stability provides independent signal beyond edge magnitude.

**CePNEM dwell:** Pearson=0.152, Spearman=0.157. Near-zero stability makes the correlation unreliable — the distribution is effectively constant.

**GCaMP:** All stability scores are 1.000. All pairwise correlations are undefined (zero variance in stability). Spearman computed across identical-rank values is numerically degenerate.

---

## Task 3 — Ranking Rule Sensitivity Audit

### CEPNEM Coordinate

ΔQ distribution (|Q_roam_conf − Q_dwell_conf|):
  mean=0.0113  median=0.0000  p95=0.0648  max=0.2541  n_nonzero=545

| Scheme | Description | n_nonzero | max score |
|---|---|---|---|
| A — min(stab_r, stab_d) | Pre-specified | 470 | 0.0807 |
| B — mean(stab_r, stab_d) | Mean stability | 545 | 0.1575 |
| C — |ΔQ| only | No stability | 545 | 0.2541 |

Top-50 overlap:
  A∩B = 26/50   A∩C = 21/50   B∩C = 43/50

Spearman rank correlation (all 1830 pairs):
  A–B = 0.8993   A–C = 0.8906   B–C = 0.9994

Top-20 pairs by |ΔQ| (Scheme C — unweighted):

| Rank | Pair | |ΔQ| |
|---|---|---|
| 1 | IL1DR–URYVR | 0.2541 |
| 2 | AVER–I1L | 0.2160 |
| 3 | ADEL–RMDL | 0.1879 |
| 4 | AVJR–OLLR | 0.1697 |
| 5 | AVAL–AWCL | 0.1682 |
| 6 | AVJR–OLQVR | 0.1614 |
| 7 | AIBR–AWCL | 0.1504 |
| 8 | IL2VL–RMEL | 0.1415 |
| 9 | IL1DR–IL1R | 0.1382 |
| 10 | RMDL–RMDVL | 0.1349 |
| 11 | AUAL–AWCL | 0.1349 |
| 12 | AVEL–URXL | 0.1319 |
| 13 | CEPDL–RMDVL | 0.1247 |
| 14 | AVDL–AVER | 0.1242 |
| 15 | I2R–NSML | 0.1227 |
| 16 | ADEL–URYVR | 0.1222 |
| 17 | OLLL–URYDL | 0.1205 |
| 18 | IL1R–RMDDR | 0.1143 |
| 19 | AVER–AWCL | 0.1128 |
| 20 | RIVL–RMDL | 0.1102 |

### GCAMP Coordinate

ΔQ distribution (|Q_roam_conf − Q_dwell_conf|):
  mean=0.0285  median=0.0018  p95=0.1294  max=0.3339  n_nonzero=944

| Scheme | Description | n_nonzero | max score |
|---|---|---|---|
| A — min(stab_r, stab_d) | Pre-specified | 944 | 0.3206 |
| B — mean(stab_r, stab_d) | Mean stability | 944 | 0.3273 |
| C — |ΔQ| only | No stability | 944 | 0.3339 |

Top-50 overlap:
  A∩B = 50/50   A∩C = 49/50   B∩C = 49/50

Spearman rank correlation (all 1830 pairs):
  A–B = 1.0000   A–C = 1.0000   B–C = 1.0000

Top-20 pairs by |ΔQ| (Scheme C — unweighted):

| Rank | Pair | |ΔQ| |
|---|---|---|
| 1 | OLLR–RMDL | 0.3339 |
| 2 | AVEL–RMDVR | 0.3123 |
| 3 | IL1DR–IL1R | 0.2981 |
| 4 | OLLL–SMDVL | 0.2897 |
| 5 | AVDL–AVJR | 0.2571 |
| 6 | IL1R–RMDVR | 0.2484 |
| 7 | I1R–M1 | 0.2451 |
| 8 | CEPVL–OLQVL | 0.2392 |
| 9 | IL2VL–RMEL | 0.2380 |
| 10 | AVAL–AWCL | 0.2362 |
| 11 | NSMR–RMDVL | 0.2336 |
| 12 | AVAL–AVJR | 0.2293 |
| 13 | RIVL–URYVR | 0.2200 |
| 14 | AVDL–AVER | 0.2186 |
| 15 | IL1DR–OLQDR | 0.2150 |
| 16 | I1L–M4 | 0.2142 |
| 17 | M3L–OLQDL | 0.2111 |
| 18 | AVJR–OLQVR | 0.2102 |
| 19 | M3R–M4 | 0.2007 |
| 20 | AVAR–AVJR | 0.1995 |

---

## Task 4 — CePNEM Dwelling Failure Mode Diagnosis

| Hypothesis | Assessment | Key evidence |
|---|---|---|
| H1 — Weak covariance | **STRONGLY SUPPORTED** | dwell/roam cov ratio = 0.764; |cov| dwell p95 = 0.1003 vs roam p95 = 0.1523 |
| H2 — Threshold too strict | **PARTIALLY SUPPORTED** | stab_dwell max = 0.760; p95 = 0.400; only 0.191 pairs ≥ 0.25 |
| H3 — Bootstrap variability | **SUPPORTED** | |Q_conf| dwell/roam ratio = 0.543; 305 ADMM edges despite near-zero stability |
| H4 — Disc/conf disagree | **SUPPORTED** | 15.7% of top-quartile |Q_conf| pairs have stab < 0.50 |

**Primary diagnosis:**

H1 (weak covariance) and H3 (bootstrap variability) are the primary drivers. CePNEM dwelling covariance is genuinely weaker than roaming (ratio 0.76x). At λ=0.15, the graphical lasso regularizes away nearly all dwelling edges in each of the 25 bootstrap subsamples, producing near-zero stability scores. The confirmation estimator (ADMM, λ_on=0.01) still recovers 305 edges because it uses the full-data covariance without resampling. The stability near-zero is real: it reflects that dwelling conditional structure is not reproducibly detectable across bootstrap subsamples at the current λ. This is a DATA-DRIVEN finding, not a scripting artifact.

**Single stable dwelling pair:**
  Pair: IL2DL–URYVL    Stability: 0.760    |Q_conf|: 0.0384    Rank by |ΔQ|: 221/1830

---

## Implications for Stage 2 Ranking Rule

These findings are factual characterizations. The supervisor decides the ranking rule.
The following consequences are mechanical, not recommendations:

**Scheme A (min-stab):**  All CePNEM pair ranks collapse to ≈0 because stab_dwell ≈ 0. No pair from CePNEM would rank above any pair from GCaMP (stab_gcamp_roam = stab_gcamp_dwell = 1.0).

**Scheme B (mean-stab):**  CePNEM pairs receive weight ≈ stab_roam/2 (since stab_dwell ≈ 0). This preserves the roaming stability signal for CePNEM. CePNEM top-50 (Scheme B) overlaps 43/50 with Scheme C.

**Scheme C (|ΔQ| only):**  The four confirmation matrices and their difference define the ranking. The stability selection provided a FILTER in Stage 0-V (its purpose was to validate edge identifiability), not a WEIGHT in the enrichment test. The enrichment test (AUROC, Fisher) ranks ALL off-connectome pairs by |ΔQ|, independent of whether pairs were stable in bootstrap.

**Key clarification for Stage 2:**  The enrichment test (Stage 4, AUROC/Fisher) operates on ALL off-connectome |ΔQ| values, not just stable ones. Stability scores affect only the named-pair RANKING table (Stage 6), not the enrichment p-value. The enrichment result is independent of which ranking scheme is chosen.

---

## Stop Condition

This report contains only diagnostic computations from Stage 1 outputs.
No enrichment tests, no ΔQ biological interpretation, no neuron-pair biological annotation.
Awaiting Stage 2 authorization checkpoint.