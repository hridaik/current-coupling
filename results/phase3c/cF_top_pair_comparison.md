# Phase 3C-F2 — Top-Pair Comparison: ΔΩ_full vs ΔQ
Date: 2026-06-03
Authorization: Phase 3C-F

## Questions

1. How many new pairs enter the top-20/50?
2. Do PDF pairs become more concentrated?
3. Do ADEL-centered pairs move upward?

---

## CePNEM: Top-20 Comparison

### Overlap

| Level | ΔΩ_full ∩ ΔQ | New in ΔΩ | Lost from ΔQ |
|---|---|---|---|
| Top-20 | 18/20 | 2 | 2 |
| Top-50 | 44/50 | 6 | 6 |

Most top pairs are preserved: 18/20 top ΔQ pairs remain in top-20 ΔΩ_full.
The two new entries are ADEL–I2L (ΔQ rank 26 → ΔΩ rank 18) and RMEL–URYVR
(ΔQ rank 21 → ΔΩ rank 19). The two pairs that exit: ASGL–RMDVL (ΔQ rank 18 → out)
and RMEL–URYVR was not in ΔQ top-20, but AVJR–URYDL (ΔQ rank 19 → rank 15 in ΔΩ).

### PDF Concentration

| Level | ΔQ PDF count | ΔΩ_full PDF count | Expected |
|---|---|---|---|
| Top-20 | 4 | **5** | 0.9 |
| Top-50 | 7 | 6 | 2.3 |

PDF pairs increase by 1 in the top-20 under ΔΩ_full (4→5; 5.6× over expected 0.9).
At top-50, the count is similar (7→6), but 6/50 = 6.5× over expected 2.3 — still
strong enrichment.

### ADEL Participation

| Level | ΔQ ADEL count | ΔΩ_full ADEL count |
|---|---|---|
| Top-20 | 3 | **4** |

ADEL pairs increase from 3 to 4 in top-20 ΔΩ_full. The four ADEL entries are:
ADEL–URYVR (rank 5), ADEL–URYDL (rank 7), ADEL–RMEL (rank 8), ADEL–I2L (rank 18).

### Full Top-20 ΔΩ_full Table (CePNEM)

| ΔΩ rank | Pair | ΔΩ_full | ΔQ | ΔQ rank | PDF | ADEL |
|---|---|---|---|---|---|---|
| 1 | IL1DR–URYVR | 0.0919 | 0.2541 | 1 | — | — |
| 2 | AVER–I1L | 0.0833 | 0.2160 | 2 | — | — |
| 3 | AVJR–OLLR | 0.0686 | 0.1697 | 3 | — | — |
| 4 | AVJR–OLQVR | 0.0640 | 0.1614 | 4 | — | — |
| **5** | **ADEL–URYVR** | **0.0595** | **0.1222** | **5** | **YES** | **YES** |
| 6 | AIZL–AVJL | 0.0506 | 0.1089 | 7 | — | — |
| **7** | **ADEL–URYDL** | **0.0485** | **0.0980** | **9** | **YES** | **YES** |
| **8** | **ADEL–RMEL** | **0.0463** | **0.0957** | **10** | **YES** | **YES** |
| 9 | AVER–AWAL | 0.0443 | 0.1094 | 6 | — | — |
| 10 | OLLR–RICL | 0.0399 | 0.0985 | 8 | — | — |
| 11 | CEPDR–IL2VL | 0.0359 | 0.0891 | 12 | — | — |
| 12 | I1L–IL2DR | 0.0347 | 0.0903 | 11 | — | — |
| 13 | CEPDR–IL2VR | 0.0337 | 0.0863 | 14 | — | — |
| 14 | AVEL–RIVL | 0.0337 | 0.0732 | 20 | — | — |
| 15 | AVJR–URYDL | 0.0328 | 0.0736 | 19 | — | — |
| 16 | OLLL–SMDVL | 0.0326 | 0.0881 | 13 | — | — |
| **17** | **RMEL–URYDL** | **0.0322** | **0.0754** | **16** | **YES** | — |
| **18** | **ADEL–I2L** | **0.0309** | **0.0624** | **26** | — | **YES** |
| **19** | **RMEL–URYVR** | **0.0305** | **0.0701** | **21** | **YES** | — |
| 20 | AVER–NSMR | 0.0291 | 0.0750 | 17 | — | — |

**5 of the top-20 ΔΩ_full pairs are PDF-annotated (ranks 5, 7, 8, 17, 19).**
The top-3 ΔQ pairs (IL1DR–URYVR, AVER–I1L, AVJR–OLLR) remain at ranks 1–4.
The ADEL→URY predictions are stable at ranks 5, 7, 8 (vs ΔQ ranks 5, 9, 10).

### Notable changes

- **ADEL–URYDL**: rises from ΔQ rank 9 → ΔΩ rank 7
- **ADEL–RMEL**: rises from ΔQ rank 10 → ΔΩ rank 8
- **ADEL–I2L**: enters top-20 (ΔQ rank 26 → ΔΩ rank 18) — new entry
- **AVEL–RIVL**: enters top-20 (ΔQ rank 20 → ΔΩ rank 14)

### Pairs entering top-50 ΔΩ that were not in top-50 ΔQ

The 6 new pairs in top-50 include ADEL–I2L and several non-PDF interneuron pairs
that benefit from the diffusion mixing pattern. These are consistent with the DA_mech
block having elevated off-diagonal D_emp entries.

---

## GCaMP: Top-20 Comparison

### Overlap

| Level | ΔΩ_full ∩ ΔQ | New in ΔΩ | Lost from ΔQ |
|---|---|---|---|
| Top-20 | 16/20 | 4 | 4 |
| Top-50 | 42/50 | 8 | 8 |

More mixing than CePNEM: 4 new entries in top-20. This reflects GCaMP's more
anisotropic D3 (CV=15% vs CePNEM 9%), amplifying the row-mixing effect.

### PDF and ADEL Concentration

| | ΔQ | ΔΩ_full | Expected |
|---|---|---|---|
| PDF in top-20 | 1 | 1 | 0.9 |
| PDF in top-50 | 4 | 4 | 2.3 |
| ADEL in top-20 | 1 | 1 | — |

PDF concentration is unchanged in GCaMP (1/20). The single PDF entry in ΔΩ_full
top-20 is ADEL–URXL (rank 6, same as ΔQ rank 19 → enters top-20).

### Full Top-20 ΔΩ_full Table (GCaMP)

| ΔΩ rank | Pair | ΔΩ_full | ΔQ | ΔQ rank | PDF | ADEL |
|---|---|---|---|---|---|---|
| 1 | OLLL–SMDVL | 0.0597 | 0.2897 | 1 | — | — |
| 2 | M3L–OLQDL | 0.0483 | 0.2111 | 5 | — | — |
| 3 | AIZL–FLPL | 0.0473 | 0.1580 | 16 | — | — |
| 4 | I1L–M4 | 0.0455 | 0.2142 | 4 | — | — |
| 5 | RIVL–URYVR | 0.0448 | 0.2200 | 3 | — | — |
| **6** | **ADEL–URXL** | **0.0427** | **0.1516** | **19** | **YES** | **YES** |
| 7 | IL2VL–M4 | 0.0425 | 0.1919 | 8 | — | — |
| 8 | NSMR–RMDVL | 0.0403 | 0.2336 | 2 | — | — |
| 9 | CEPDL–FLPL | 0.0379 | 0.1760 | 11 | — | — |
| 10 | IL2DR–OLQVL | 0.0376 | 0.1774 | 10 | — | — |
| 11 | AVJR–OLQVR | 0.0373 | 0.2102 | 6 | — | — |
| 12 | M1–RMEL | 0.0373 | 0.1626 | 14 | — | — |
| 13 | AWAL–M1 | 0.0370 | 0.1745 | 12 | — | — |
| 14 | AVJL–NSMR | 0.0369 | 0.1264 | 33 | — | — |
| 15 | IL1DR–URYVR | 0.0367 | 0.1720 | 13 | — | — |
| 16 | AVAR–SMDVL | 0.0365 | 0.1980 | 7 | — | — |
| 17 | IL2VR–OLQVL | 0.0356 | 0.1183 | 39 | — | — |
| 18 | AVEL–CEPVL | 0.0343 | 0.1578 | 17 | — | — |
| 19 | AIZL–AVJL | 0.0333 | 0.1124 | 46 | — | — |
| 20 | AVAL–IL2DL | 0.0322 | 0.1021 | 60 | — | — |

**Only 1 of 20 ΔΩ_full GCaMP top pairs is PDF-annotated** (ADEL–URXL, rank 6).
GCaMP ΔΩ_full substantially reorders the list: pairs from ranks 16, 33, 39, 46, 60
enter the top-20. The reordering is driven by AVJL–NSMR (rank 33→14), IL2VR–OLQVL
(rank 39→17), AIZL–AVJL (rank 46→19), and AVAL–IL2DL (rank 60→20) — all
pharyngeal/command interneuron pairs that benefit from the GCaMP diffusion structure.

---

## Answers to F2 Questions

**1. How many new pairs enter top-20?**
- CePNEM: 2 new pairs (ADEL–I2L, RMEL–URYVR replaces ASGL–RMDVL)
- GCaMP: 4 new pairs (larger reordering)

**2. Do PDF pairs become more concentrated?**
- CePNEM: YES — 4→5 PDF pairs in top-20 (5.6× over expected; slightly stronger)
- GCaMP: NO — 1→1 PDF pairs unchanged

**3. Do ADEL-centered pairs move upward?**
- CePNEM: YES — ADEL gains a 4th top-20 entry (ADEL–I2L); ADEL→URYDL improves 9→7, ADEL→RMEL 10→8
- GCaMP: NEUTRAL — ADEL–URXL enters top-20 at rank 6 (was rank 19), but this is the only ADEL entry in either coordinate

---

*3C-F2 scope: top-pair characterization only. No new fitting. No held-out evaluation.*
