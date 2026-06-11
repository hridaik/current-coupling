# D3 — PDF Contribution Map
Date: 2026-06-03

ΔQ_pdf = ΔQ_pred(M1) − ΔQ_pred(M0) = ΔQ_pred(M1) (since M0 predicts ΔQ=0 everywhere).

## Top 50 Class 4 Pairs by |ΔQ_pdf|

| Rank | Pair | |ΔQ_pdf| | Sign | PDF? | Source? | Target? | Held-out? |
|---|---|---|---|---|---|---|---|
| 1 | RMEL–RMER | 0.15115 | + | YES | SRC |  |  |
| 2 | AVDL–RMEL | 0.11490 | + | YES | SRC |  |  |
| 3 | OLLL–OLQDL | 0.11381 | + |  |  | TGT |  |
| 4 | OLLL–URYVR | 0.11225 | + |  |  | TGT |  |
| 5 | OLLR–OLQDL | 0.11212 | + |  |  | TGT |  |
| 6 | OLLR–URYVR | 0.11137 | + |  |  | TGT |  |
| 7 | OLLL–URXL | 0.11101 | + |  |  | TGT |  |
| 8 | OLLL–OLQDR | 0.11089 | + |  |  | TGT |  |
| 9 | OLLR–URXL | 0.11012 | + |  |  | TGT |  |
| 10 | OLQDL–URYVR | 0.11011 | + |  |  | TGT |  |
| 11 | OLQDL–OLQDR | 0.10941 | + |  |  | TGT |  |
| 12 | I1R–OLLL | 0.10923 | + |  |  | TGT |  |
| 13 | OLQDL–URYVL | 0.10922 | + |  |  | TGT |  |
| 14 | I1R–OLQDL | 0.10906 | + |  |  | TGT |  |
| 15 | I1R–OLLR | 0.10905 | + |  |  | TGT |  |
| 16 | I1R–URYVR | 0.10892 | + |  |  | TGT |  |
| 17 | OLQDR–URYVR | 0.10829 | + |  |  | TGT |  |
| 18 | URYVL–URYVR | 0.10819 | + |  |  | TGT |  |
| 19 | OLQDL–URXL | 0.10809 | + |  |  | TGT |  |
| 20 | I1R–URYVL | 0.10776 | + |  |  | TGT |  |
| 21 | OLQDL–OLQVL | 0.10734 | + |  |  | TGT |  |
| 22 | OLQVL–URYVR | 0.10709 | + |  |  | TGT |  |
| 23 | URXL–URYVR | 0.10649 | + |  |  | TGT |  |
| 24 | I1L–URYVR | 0.10637 | + |  |  | TGT |  |
| 25 | OLQDR–URYVL | 0.10621 | + |  |  | TGT |  |
| 26 | I1L–OLQDL | 0.10618 | + |  |  | TGT |  |
| 27 | I1R–URXL | 0.10613 | + |  |  | TGT |  |
| 28 | I1R–OLQDR | 0.10605 | + |  |  | TGT |  |
| 29 | I1L–I1R | 0.10570 | + |  |  | TGT |  |
| 30 | I1L–OLLR | 0.10565 | + |  |  | TGT |  |
| 31 | AVDL–RMER | 0.10555 | + | YES | SRC |  |  |
| 32 | OLQDR–OLQVL | 0.10546 | + |  |  | TGT |  |
| 33 | I1L–OLLL | 0.10529 | + |  |  | TGT |  |
| 34 | URYDL–URYVR | 0.10520 | + |  |  | TGT |  |
| 35 | I1L–URYVL | 0.10507 | + |  |  | TGT |  |
| 36 | I1R–OLQVL | 0.10501 | + |  |  | TGT |  |
| 37 | OLQDR–URXL | 0.10444 | + |  |  | TGT |  |
| 38 | OLQDR–URYDL | 0.10417 | + |  |  | TGT |  |
| 39 | OLQVR–RMEL | 0.10384 | + | YES | SRC | TGT |  |
| 40 | OLQVR–URYVR | 0.10378 | + |  |  | TGT |  |
| 41 | OLLR–URYDL | 0.10375 | + |  |  | TGT |  |
| 42 | URYDL–URYVL | 0.10355 | + |  |  | TGT |  |
| 43 | OLLR–OLQVL | 0.10350 | + |  |  | TGT |  |
| 44 | I1L–URXL | 0.10349 | + |  |  | TGT |  |
| 45 | I1R–URYDL | 0.10337 | + |  |  | TGT |  |
| 46 | I1L–OLQDR | 0.10296 | + |  |  | TGT |  |
| 47 | OLQDL–OLQVR | 0.10265 | + |  |  | TGT |  |
| 48 | OLLL–OLQVR | 0.10215 | + |  |  | TGT |  |
| 49 | I1L–OLQVL | 0.10193 | + |  |  | TGT |  |
| 50 | FLPL–OLLR | 0.10173 | + |  |  | TGT |  |

## PDF-Annotated Enrichment in Top-K

Total PDF Class 4 pairs: 61 / 1321 = 4.6%

| K | N PDF in top-K | Expected by chance | Enrichment ratio |
|---|---|---|---|
| 20 | 2 | 0.9 | 2.17× |
| 50 | 4 | 2.3 | 1.73× |
| 100 | 30 | 4.6 | 6.50× |
| 200 | 55 | 9.2 | 5.96× |
| 500 | 60 | 23.1 | 2.60× |

## Source-Neuron Breakdown

| Source | N C4 pairs | Mean |ΔQ_pdf| | Max |ΔQ_pdf| |
|---|---|---|---|
| RID | 52 | 0.0139 | 0.0883 |
| ADEL | 44 | 0.0127 | 0.0883 |
| RMEL | 48 | 0.0275 | 0.1512 |
| RMER | 46 | 0.0272 | 0.1512 |
| AVDL | 47 | 0.0302 | 0.1149 |

*Note: Held-out ADEL pairs appear with HELD flag. Their ranks are reported but observed ΔQ not consulted.*
