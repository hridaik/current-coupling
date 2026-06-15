# Phase 10F.4 — Coupling-Corrected PDF Enrichment
Date: 2026-06-15

## Design

Three analyses:
1. PDF enrichment under |ΔΩ^B| = |ΔΩ_ss + ΔB| (Phase 10A correction, +1×ΔB)
2. PDF enrichment under |ΔΩ^B_cont| = |ΔΩ_ss + 2ΔB| (continuous-time correction)
3. Drift-filtered enrichment: exclude top-{20, 50, 100} |ΔB| pairs from universe,
   then recompute PDF enrichment in remaining C4 pairs by |ΔΩ_ss|.

## Results

### Table: PDF enrichment across scoring objects

| K | Primary ΔΩ_ss | | ΔΩ^B (+1×ΔB) | | ΔΩ^B_cont (+2×ΔB) | |
|---|count|p_fisher|count|p_fisher|count|p_fisher|
| 10 | 3/10 | 0.0089 | 2/10 | 0.0744 | 2/10 | 0.0744 |
| 20 | 4/20 | 0.0114 | 3/20 | 0.0610 | 2/20 | 0.2350 |
| 30 | 6/30 | 0.0019 | 3/30 | 0.1575 | 3/30 | 0.1575 |
| 40 | 8/40 | 0.0003 | 4/40 | 0.1087 | 3/40 | 0.2801 |
| 50 | 9/50 | 0.0003 | 4/50 | 0.1961 | 4/50 | 0.1961 |

### Drift-filtered enrichment (|ΔΩ_ss| ranking, top |ΔB| pairs excluded):
  Exclude top-20 |ΔB|: N_remaining=1301, PDF pairs in excluded=2, PDF/20=4, OR=5.26, p=0.0107
  Exclude top-50 |ΔB|: N_remaining=1271, PDF pairs in excluded=3, PDF/20=4, OR=5.23, p=0.0109
  Exclude top-100 |ΔB|: N_remaining=1221, PDF pairs in excluded=5, PDF/20=5, OR=6.93, p=0.0016

Note: ADEL–RMEL is the C4 pair with highest |ΔB| (rank 1).
ADEL–RMEL is PDF-annotated: True.
Highest |ΔB| pair is PDF-annotated: True.

## Conclusions

### Does PDF enrichment survive coupling correction?
ATTENUATED — Fisher p=0.0610 under |ΔΩ^B| at K=20.

### Should the manuscript qualify PDF enrichment as partly drift-supported?
PARTIAL QUALIFICATION NEEDED: ADEL–RMEL (|ΔB| rank 1) is PDF-annotated.
Part of the top-20 PDF count comes from a pair with large coupling change.
Drift-filtered analysis shows whether PDF enrichment survives excluding ADEL-RMEL.
