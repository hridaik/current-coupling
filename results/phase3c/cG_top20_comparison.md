# Phase 3C-G3 — Top-20 Comparison: ΔQ vs ΔΩ_full
Date: 2026-06-03
Authorization: Phase 3C-G

## Top-20 Overlap

| | Count |
|---|---|
| Pairs in both ΔQ top-20 and ΔΩ top-20 | 18/20 |
| Pairs entering ΔΩ top-20 (not in ΔQ) | 2 |
| Pairs departing ΔQ top-20 (not in ΔΩ) | 2 |

---

## Pairs Entering ΔΩ Top-20

| Pair | ΔΩ rank | ΔQ rank | Δrank | PDF? | ADEL? | URY? |
|---|---|---|---|---|---|---|
| RMEL–URYVR | 19 | 21 | +2 | **YES** | No | Yes |
| ADEL–I2L | 18 | 26 | +8 | No | **Yes** | No |

**RMEL–URYVR**: A PDF-annotated pair (RMEL→URYVR is in the Bentley ESconnectome).
This pair already had strong ΔQ = 0.0701 (rank 21); it moves to rank 19 under ΔΩ.
This is a genuine signal-bearing pair rising 2 positions.

**ADEL–I2L**: Not PDF-annotated. ADEL is a source neuron, I2L is a pharyngeal
interneuron. ADEL–I2L had ΔQ = 0.0624 (rank 26); it moves to rank 18 under ΔΩ.
This is an ADEL-related pair but not a PDF pair; I2L does not express pdfr-1.

---

## Pairs Departing ΔQ Top-20

| Pair | ΔQ rank | ΔΩ rank | Δrank | PDF? |
|---|---|---|---|---|
| I2R–IL2DR | 15 | 21 | −6 | No |
| ASGL–RMDVL | 18 | 23 | −5 | No |

Both departing pairs are non-PDF. Neither has biological annotation relevant to
the neuropeptide enrichment analysis. Their departures are not interpretable as
losses of important signal.

---

## Full Top-20 ΔΩ_full Table (with ΔQ context)

| ΔΩ rank | Pair | ΔΩ | ΔQ | ΔQ rank | PDF | ADEL | Change |
|---|---|---|---|---|---|---|---|
| 1 | IL1DR–URYVR | 0.092 | 0.254 | 1 | — | — | stable |
| 2 | AVER–I1L | 0.083 | 0.216 | 2 | — | — | stable |
| 3 | AVJR–OLLR | 0.069 | 0.170 | 3 | — | — | stable |
| 4 | AVJR–OLQVR | 0.064 | 0.161 | 4 | — | — | stable |
| **5** | **ADEL–URYVR** | **0.060** | **0.122** | **5** | **YES** | **YES** | **stable** |
| 6 | AIZL–AVJL | 0.051 | 0.109 | 7 | — | — | +1 |
| **7** | **ADEL–URYDL** | **0.049** | **0.098** | **9** | **YES** | **YES** | **+2** |
| **8** | **ADEL–RMEL** | **0.046** | **0.096** | **10** | **YES** | **YES** | **+2** |
| 9 | AVER–AWAL | 0.044 | 0.109 | 6 | — | — | −3 |
| 10 | OLLR–RICL | 0.040 | 0.099 | 8 | — | — | −2 |
| 11 | CEPDR–IL2VL | 0.036 | 0.089 | 12 | — | — | +1 |
| 12 | I1L–IL2DR | 0.035 | 0.090 | 11 | — | — | −1 |
| 13 | CEPDR–IL2VR | 0.034 | 0.086 | 14 | — | — | +1 |
| 14 | AVEL–RIVL | 0.034 | 0.073 | 20 | — | — | +6 |
| 15 | AVJR–URYDL | 0.033 | 0.074 | 19 | — | — | +4 |
| 16 | OLLL–SMDVL | 0.033 | 0.088 | 13 | — | — | −3 |
| **17** | **RMEL–URYDL** | **0.032** | **0.075** | **16** | **YES** | — | **−1** |
| 18 | **ADEL–I2L** | 0.031 | 0.062 | 26 | — | **YES** | **NEW** |
| **19** | **RMEL–URYVR** | **0.031** | **0.070** | **21** | **YES** | — | **NEW** |
| 20 | AVER–NSMR | 0.029 | 0.075 | 17 | — | — | −3 |

**5 PDF pairs in the ΔΩ top-20** (ranks 5, 7, 8, 17, 19) vs 4 in ΔQ top-20.
The additional PDF pair is RMEL–URYVR, entering at rank 19.

---

## Interpretation

The top-20 comparison shows minimal structural change: 18/20 pairs are identical,
the two new entries (RMEL–URYVR, ADEL–I2L) are marginal additions from just
outside the ΔQ top-20, and the two departures (I2R–IL2DR, ASGL–RMDVL) are
uninformative non-PDF pairs.

The ADEL predictions are stable and slightly improved (ranks 5,7,8 vs ΔQ ranks 5,9,10),
but this improvement is +2 positions, not a major restructuring.

**The AUROC improvement (+0.108) is not reflected in the top-20**: the top-20 changes
are marginal. The AUROC gain comes entirely from mid-to-bottom-of-ranking pairs
(ranks 200–1300) shifting through D_emp zero-pair imputation — not from any
restructuring of the top signal tier.

---

*3C-G3 scope: top-20 comparison only.*
