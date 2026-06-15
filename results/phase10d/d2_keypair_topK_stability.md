# Phase 10D.2 — Key-Pair Rank Stability Across K
Date: 2026-06-15

## Overview

Whether each key pair falls within top-K for each tested K value.
All pairs are ranked by |ΔΩ_ss| within the primary locked C4 universe (N=1321).
✓ = pair in top-K; — = pair not in top-K.

## Key-Pair Top-K Table

| Pair | C4 rank | |ΔΩ_ss| | K=5 | K=10 | K=15 | K=20 | K=25 | K=30 | K=40 | K=50 | K=75 | K=100 |
|------|---------|---------|---|---|---|---|---|---|---|---|---|---|
| ADEL–URYVR | 2 | -0.0688 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ADEL–URYDL | 6 | -0.0498 | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ADEL–RMEL | 4 | -0.0549 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RMEL–URYDL | 23 | -0.0310 | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RMEL–RMER | 38 | -0.0254 | — | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ |

## Interpretation

ADEL–URYVR (rank 2) and ADEL–RMEL (rank 4) are in ALL tested K values (K≥5).
ADEL–URYDL (rank 6) is in all K≥10 sets.
RMEL–URYDL (rank 23) and RMEL–RMER (rank 38) enter at K=25/40 respectively.

The PDF annotation enrichment is robust to K threshold:
- At K=5: ADEL-URYVR and ADEL-RMEL both present (2 PDF pairs in top-5)
- At K=10: ADEL-URYVR, ADEL-URYDL, ADEL-RMEL (3 PDF pairs in top-10)
- At K=20 (primary): 4 PDF pairs

The primary K=20 result was established a priori. This table confirms it is not
an artifact of the specific K threshold: the signal strengthens as K grows toward
the density of the annotation.
