# Stage 2 Report — ΔQ Computation and Connectome Classification
Date: 2026-06-01

## Pass Conditions

| Condition | Status |
|---|---|
| 4 ΔQ matrices computed | PASS |
| Class 4 count ≥ 30 | PASS (1321 pairs) |
| Ranked pair lists saved | PASS |

## Four-Class Classification

Classification uses A_raw (synaptic connectome) and the 56-neuron Creamer subspace.
Neurons outside Creamer scope: AIBL, AIBR, AWCL, IL1L, IL1R.

| Class | Definition | Count |
|---|---|---|
| 1 | On A_raw AND both neurons in Creamer 56-subspace | 219 |
| 2 | On A_raw AND at least one neuron outside Creamer | 41 |
| 3 | Off A_raw AND at least one neuron outside Creamer | 249 |
| 4 | **Off A_raw AND both in Creamer 56 (primary enrichment target)** | **1321** |

## Off-Connectome Annotation Counts

| Annotation | Off-connectome pairs | All pairs |
|---|---|---|
| Randi (unc-31-sensitive, Rule A, q_wt<0.05) | 109 | 160 |
| Neuropeptide (Ripoll-Sánchez, from Creamer peptide.pkl) | 1144 | 1345 |
| Both Randi and neuropeptide | 74 | — |

**Note on Randi count:** Phase 0 config stated N_RANDI_SUBGRAPH_PAIRS=189.
This was the count of DIRECTED pairs (q_wt<0.05 applied to i→j only).
Undirected pairs = 160 total (109 off-connectome, 51 on-connectome).
The enrichment test uses the 109 off-connectome undirected Randi pairs.
The Stage 0-V synthetic validation used 159 synthetic off-connectome annotated pairs
(randomly placed from 189 directed → ~159 off-connectome). The real annotation
has 109. This is noted for the enrichment power assessment in Stage 4.

## CEPNEM Coordinate — ΔQ Summary

ΔQ = Q_cepnem_roam_conf − Q_cepnem_dwell_conf

Class 4 (primary enrichment target): 1321 pairs, 243 non-zero.
|ΔQ| Class 4: mean=0.0057, median=0.0000, p95=0.0412, max=0.2541

Top-20 Class 4 pairs ranked by |ΔQ|:

| Rank | Pair | |ΔQ| | Sign | Randi | Peptide |
|---|---|---|---|---|---|
| 1 | IL1DR-URYVR | 0.2541 | − |  |  |
| 2 | AVER-I1L | 0.2160 | − |  | YES |
| 3 | AVJR-OLLR | 0.1697 | − |  | YES |
| 4 | AVJR-OLQVR | 0.1614 | − |  | YES |
| 5 | ADEL-URYVR | 0.1222 | − |  |  |
| 6 | AVER-AWAL | 0.1094 | − |  | YES |
| 7 | AIZL-AVJL | 0.1089 | − |  | YES |
| 8 | OLLR-RICL | 0.0985 | − |  | YES |
| 9 | ADEL-URYDL | 0.0980 | − |  |  |
| 10 | ADEL-RMEL | 0.0957 | − |  |  |
| 11 | I1L-IL2DR | 0.0903 | + |  | YES |
| 12 | CEPDR-IL2VL | 0.0891 | − |  |  |
| 13 | OLLL-SMDVL | 0.0881 | − |  | YES |
| 14 | CEPDR-IL2VR | 0.0863 | − |  |  |
| 15 | I2R-IL2DR | 0.0857 | − |  | YES |
| 16 | RMEL-URYDL | 0.0754 | − |  |  |
| 17 | AVER-NSMR | 0.0750 | − |  | YES |
| 18 | ASGL-RMDVL | 0.0745 | − |  | YES |
| 19 | AVJR-URYDL | 0.0736 | − |  |  |
| 20 | AVEL-RIVL | 0.0732 | − |  | YES |

## GCAMP Coordinate — ΔQ Summary

ΔQ = Q_gcamp_roam_conf − Q_gcamp_dwell_conf

Class 4 (primary enrichment target): 1321 pairs, 585 non-zero.
|ΔQ| Class 4: mean=0.0204, median=0.0000, p95=0.0998, max=0.2897

Top-20 Class 4 pairs ranked by |ΔQ|:

| Rank | Pair | |ΔQ| | Sign | Randi | Peptide |
|---|---|---|---|---|---|
| 1 | OLLL-SMDVL | 0.2897 | − |  | YES |
| 2 | NSMR-RMDVL | 0.2336 | − |  | YES |
| 3 | RIVL-URYVR | 0.2200 | − |  | YES |
| 4 | I1L-M4 | 0.2142 | + |  | YES |
| 5 | M3L-OLQDL | 0.2111 | − |  |  |
| 6 | AVJR-OLQVR | 0.2102 | − |  | YES |
| 7 | AVAR-SMDVL | 0.1980 | − |  | YES |
| 8 | IL2VL-M4 | 0.1919 | + |  |  |
| 9 | AVJR-OLQVL | 0.1822 | + |  | YES |
| 10 | IL2DR-OLQVL | 0.1774 | − |  |  |
| 11 | CEPDL-FLPL | 0.1760 | + |  |  |
| 12 | AWAL-M1 | 0.1745 | − |  | YES |
| 13 | IL1DR-URYVR | 0.1720 | − |  |  |
| 14 | M1-RMEL | 0.1626 | − |  |  |
| 15 | AVAR-URYVR | 0.1597 | + |  | YES |
| 16 | AIZL-FLPL | 0.1580 | − |  | YES |
| 17 | AVEL-CEPVL | 0.1578 | − |  | YES |
| 18 | AVJR-M3R | 0.1570 | + |  | YES |
| 19 | ADEL-URXL | 0.1516 | − |  | YES |
| 20 | AVJR-AWAL | 0.1478 | − | YES | YES |

## Stage 1A Finding (Recorded)

CePNEM dwelling stability is near-zero (1/1830 pairs stable at threshold 0.75). This does NOT affect Stage 2 or the enrichment test. The enrichment test operates on the full |ΔQ| distribution for all off-connectome pairs, independent of stability scores. Stability affects only the Stage 6 named-pair ranking table.

## Next Step

**Stage 3 (sensitivity analysis) and Stage 4 (enrichment tests) require
explicit human authorization.** Review this report. Do NOT proceed automatically.

---
*Stage 2 scope: ΔQ computation, classification, annotation, ranking. No enrichment statistics.*