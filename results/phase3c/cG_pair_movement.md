# Phase 3C-G1 — PDF Pair Movement Table: ΔQ → ΔΩ_full
Date: 2026-06-03
Authorization: Phase 3C-G

## Setup

All 61 Bentley PDF Class 4 pairs ranked by |ΔQ| and |ΔΩ_full| separately.

Δrank = rank_Q − rank_Ω. **Positive = pair moved UPWARD in Ω-space (better rank).**

---

## Movement Summary

| Category | Count | Fraction |
|---|---|---|
| Upward movers (Δrank > 0) | **39** | 64% |
| Unchanged (Δrank = 0) | 2 | 3% |
| Downward movers (Δrank < 0) | **20** | 33% |

Mean Δrank = **+156.5** (strongly upward on average).  
Median Δrank = **+67.0**.  
Std = **408.9** (bimodal — large upward AND large downward movers).

---

## Top 20 Upward Movers

| Rank | Pair | ΔQ rank | ΔΩ rank | Δrank | ΔQ | ΔΩ | Source |
|---|---|---|---|---|---|---|---|
| 1 | I1R–RMEL | 1274 | 232 | **+1042** | 0.0000 | 0.0039 | RMEL |
| 2 | FLPL–RMEL | 1085 | 207 | **+878** | 0.0000 | 0.0044 | RMEL |
| 3 | OLQDR–RMEL | 995 | 192 | **+803** | 0.0000 | 0.0049 | RMEL |
| 4 | I1L–RMEL | 1077 | 334 | **+743** | 0.0000 | 0.0028 | RMEL |
| 5 | OLQVR–RMEL | 905 | 221 | **+684** | 0.0000 | 0.0042 | RMEL |
| 6 | RID–URYDL | 888 | 218 | **+670** | 0.0000 | 0.0042 | RID |
| 7 | RID–URYVR | 889 | 224 | **+665** | 0.0000 | 0.0041 | RID |
| 8 | OLQVL–RID | 1002 | 337 | **+665** | 0.0000 | 0.0028 | RID |
| 9 | ADEL–OLQVL | 1139 | 516 | **+623** | 0.0000 | 0.0018 | ADEL |
| 10 | OLQVL–RMEL | 896 | 292 | **+604** | 0.0000 | 0.0032 | RMEL |
| 11 | I1L–RMER | 1078 | 479 | **+599** | 0.0000 | 0.0020 | RMER |
| 12 | FLPL–RMER | 1086 | 501 | **+585** | 0.0000 | 0.0019 | RMER |
| 13 | OLQDR–RID | 992 | 419 | **+573** | 0.0000 | 0.0023 | RID |
| 14 | I1R–RID | 1279 | 713 | **+566** | 0.0000 | 0.0012 | RID |
| 15 | OLLL–RID | 964 | 422 | **+542** | 0.0000 | 0.0023 | RID |
| 16 | OLLL–RMER | 968 | 464 | **+504** | 0.0000 | 0.0021 | RMER |
| 17 | ADEL–I1L | 922 | 459 | **+463** | 0.0000 | 0.0021 | ADEL |
| 18 | AVDL–URYVR | 638 | 199 | **+439** | 0.0000 | 0.0047 | AVDL |
| 19 | OLQDL–RMER | 1022 | 649 | **+373** | 0.0000 | 0.0014 | RMER |
| 20 | RID–RMER | 895 | 539 | **+356** | 0.0000 | 0.0018 | RID/RMER |

**Critical observation**: Every top-20 upward mover had **ΔQ = 0.0000** — these pairs had
zero conditional-dependence signal in the graphical lasso. They gain nonzero ΔΩ entirely
through the D_emp mixing operation spreading signal from neighboring neurons.

---

## Top 20 Downward Movers

| Pair | ΔQ rank | ΔΩ rank | Δrank | ΔQ | ΔΩ | Source |
|---|---|---|---|---|---|---|
| AVDL–URYVL | 637 | 1295 | **−658** | 0.0000 | 0.0000 | AVDL |
| ADEL–URYVL | 523 | 1172 | **−649** | 0.0000 | 0.0003 | ADEL |
| RMER–URXL | 540 | 1168 | **−628** | 0.0000 | 0.0003 | RMER |
| RMEL–URXL | 546 | 1169 | **−623** | 0.0000 | 0.0003 | RMEL |
| AVDL–I1R | 644 | 1239 | **−595** | 0.0000 | 0.0002 | AVDL |
| RMEL–URYVL | 201 | 738 | **−537** | 0.0049 | 0.0012 | RMEL |
| ADEL–I1R | 932 | 1263 | **−331** | 0.0000 | 0.0001 | ADEL |
| AVDL–OLQVR | 627 | 906 | **−279** | 0.0000 | 0.0008 | AVDL |
| AVDL–OLQDR | 625 | 875 | **−250** | 0.0000 | 0.0009 | AVDL |
| AVDL–OLQDL | 229 | 404 | **−175** | 0.0019 | 0.0024 | AVDL |
| AVDL–OLLR | 624 | 789 | **−165** | 0.0000 | 0.0011 | AVDL |
| ADEL–OLLR | 549 | 673 | **−124** | 0.0000 | 0.0014 | ADEL |
| ADEL–OLQDR | 542 | 642 | **−100** | 0.0000 | 0.0014 | ADEL |
| AVDL–RID | 141 | 193 | **−52** | 0.0172 | 0.0048 | AVDL/RID |
| AVDL–OLLL | 623 | 992 | **−369** | 0.0000 | 0.0007 | AVDL |
| RMEL–RMER | 32 | 54 | **−22** | 0.0579 | 0.0201 | RMEL/RMER |
| ADEL–OLQVR | 121 | 140 | **−19** | 0.0215 | 0.0080 | ADEL |
| OLQDL–RID | 203 | 214 | **−11** | 0.0048 | 0.0042 | RID |
| RMEL–URYDL | 16 | 17 | **−1** | 0.0754 | 0.0322 | RMEL |

The largest downward movers are mostly zero-ΔQ AVDL and ADEL pairs. Notably:
- **ADEL–URYVL** falls from rank 523 → 1172 (−649)
- **RMEL–RMER** (the strongest signal pair in Phase 3C-C) falls from rank 32 → 54 (−22)
- **RMEL–URXL, RMER–URXL** fall dramatically (−623, −628) — both had ΔQ = 0

---

## Key Pattern

**The movement table reveals a two-class structure:**

Class A — Zero-ΔQ pairs that rise (39 pairs, all had ΔQ = 0):
These gain nonzero ΔΩ via D_emp mixing. They span the entire spectrum from
mild gains (RMER–URYVL, +67) to massive gains (I1R–RMEL, +1042). The AUROC
improvement is almost entirely driven by this class.

Class B — Pairs with existing ΔQ signal (22 pairs):
These show modest movement ±22 ranks, with the exception of RMEL–URYVL (−537)
and AVDL–OLQDL (−175) which had small nonzero ΔQ but are pulled DOWN by the
D_emp mixing.

---

*3C-G1 scope: pair movement characterization only.*
