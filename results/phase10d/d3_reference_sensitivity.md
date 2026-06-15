# Phase 10D.3 — Reference Sensitivity
Date: 2026-06-15

## Overview

Tests whether key pairs are on- or off-reference under 10 alternative connectome
definitions. If a pair is ON-reference under a given definition, it would be
excluded from that definition's Class-4 universe.

The **primary** Class-4 universe is LOCKED (from Phase 2, N=1321 pairs). This
analysis is a robustness check only — alternative C4 universes are NOT substituted.

## Raw Synapse Counts for Key Pairs

| Pair | Chem (i→j) | Chem (j→i) | Gap | LDS weight (sum) |
|------|-----------|-----------|-----|-----------------|
| ADEL–URYVR | 0 | 0 | 0 | 0.000 |
| ADEL–URYDL | 0 | 0 | 0 | 0.000 |
| ADEL–RMEL | 0 | 0 | 0 | 0.000 |
| RMEL–URYDL | 1 | 0 | 0 | 0.017 |
| RMEL–RMER | 0 | 0 | 0 | 0.000 |


## Reference Sensitivity Table

| Reference definition | N_C4 | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–URYDL | RMEL–RMER |
|---------------------|------|---|---|---|---|---|
| Creamer_chem_thr1 | 1322 | off-reference | off-reference | off-reference | ON-reference | off-reference |
| Creamer_chem_thr2 | 1401 | off-reference | off-reference | off-reference | off-reference | off-reference |
| Creamer_chem_thr3 | 1430 | off-reference | off-reference | off-reference | off-reference | off-reference |
| Creamer_gap_thr1 | 1462 | off-reference | off-reference | off-reference | off-reference | off-reference |
| Creamer_chem_or_gap | 1282 | off-reference | off-reference | off-reference | ON-reference | off-reference |
| White1986_chem | 1403 | off-reference | off-reference | off-reference | off-reference | off-reference |
| White1986_chem_elec | 1375 | off-reference | off-reference | off-reference | off-reference | off-reference |
| Witvliet2020_chem | 1410 | off-reference | off-reference | off-reference | off-reference | off-reference |
| CreamerLDS_nonzero | 1327 | off-reference | off-reference | off-reference | ON-reference | off-reference |
| CreamerLDS_w05 | 1516 | off-reference | off-reference | off-reference | off-reference | off-reference |


## Interpretation

**Primary ADEL-PDF pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL) and RMEL–RMER are
off-reference under ALL 10 tested connectome definitions.** They have zero chemical
synapses, zero gap junctions, and zero LDS effective coupling in all sources tested.

**RMEL–URYDL is ON-reference under 3 of 10 definitions** (Creamer_chem_thr1,
Creamer_chem_or_gap, CreamerLDS_nonzero). Specifically:
- Creamer chemical connectome: 1 directed synapse RMEL→URYDL (0 in reverse direction)
- Creamer LDS: effective coupling weight = 0.017 (RMEL→URYDL directed)
- Both the chemical and LDS connections represent weak, directed RMEL→URYDL links.
- At threshold ≥2 synapses or |weight| ≥ 0.05, RMEL-URYDL is off-reference again.

**Implication**: RMEL–URYDL is a borderline case. It is off-reference in the locked
primary C4 universe (which does NOT use Creamer_chem_thr1 exactly), but a reviewer
could argue it has marginal Creamer connectivity. This should be disclosed in any
manuscript reporting RMEL-URYDL results.

**The primary claims (ADEL–URYVR, ADEL–URYDL) are unaffected**: both are off-reference
under every definition tested, including Creamer chemical thr=1, gap junctions, White
1986, Witvliet 2020, and Creamer LDS at any threshold.

**Implication for N_C4**: Alternative C4 sizes range from 1282 to 1516 pairs across the
tested definitions. The primary universe of 1321 is closest to Creamer_chem_thr1 (1322).
