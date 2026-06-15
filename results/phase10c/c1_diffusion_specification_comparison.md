# Phase 10C.1 — Diffusion Specification Comparison
Date: 2026-06-15

Five diffusion specifications applied to the same Q_roam and Q_dwell matrices.
For each: ΔΩ^(spec) = D_roam^(spec) @ Q_roam − D_dwell^(spec) @ Q_dwell.
1321 Class-4 pairs ranked by |ΔΩ^(spec)|.

## Results Table

| Variant | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–URYDL | RMEL–RMER | DA_URY | PDF/20 | ρ_prim | Ovlp/20 |
|---------|-----------|-----------|---------|----------|---------|-------|-------|-------|---------|
| Identity (D=I) | 5 | 9 | 10 | 16 | 32 | 1 | 4/20 | 0.331 | 15/20 |
| Pooled diagonal | 5 | 7 | 8 | 20 | 38 | 1 | 4/20 | 0.331 | 15/20 |
| State-specific diagonal | 3 | 6 | 7 | 23 | 49 | 1 | 3/20 | 0.331 | 16/20 |
| Pooled full | 4 | 6 | 7 | 16 | 54 | 1 | 5/20 | 0.244 | 14/20 |
| **State-specific full (primary)** | **2** | **6** | **4** | **23** | **38** | **1** | **4/20** | 1.000 | **20/20** |

ρ_prim = Spearman ρ between |ΔΩ^(spec)| and primary |ΔΩ_ss| over 1321 pairs.

## Notes on Identity Variant

Identity diffusion (D=I) gives ΔΩ^{identity} = Q_roam − Q_dwell = ΔQ.
This is numerically confirmed (ρ = 0.331 = Spearman ρ between |ΔQ| and |ΔΩ_ss|,
and ADEL-URYVR/URYDL ranks 5/9 match the ΔQ ranks from Phase 5B).
This variant serves as the pure-precision baseline.

## Interpretation

**The ADEL/PDF signal is NOT a dense-diffusion artifact.**

The signal is ALREADY PRESENT under identity diffusion (D=I), which is equivalent
to pure ΔQ. ADEL–URYVR ranks 5th, ADEL–URYDL ranks 9th — both in the top-1% of
1321 Class-4 pairs — without any diffusion weighting at all.

**The diffusion specifications progressively refine the ranking:**

| Effect | ADEL–URYVR | ADEL–URYDL |
|--------|-----------|-----------|
| D=I (no D) | 5 | 9 |
| Pooled diagonal | 5 | 7 |
| State-specific diagonal | 3 | 6 |
| Pooled full | 4 | 6 |
| State-specific full | **2** | **6** |

The full state-specific D promotes ADEL-URYVR from rank 5 to rank 2 (a 3-place
improvement), and ADEL-URYDL from rank 9 to rank 6.

**The dense off-diagonal structure adds modestly to the ranking:**
- Pooled full vs pooled diagonal: ADEL-URYVR 4 vs 5 (minor)
- State-specific full vs state-specific diagonal: ADEL-URYVR 2 vs 3 (single step)

**The state-dependence of D matters more than the off-diagonal structure:**
- State-specific diagonal: ADEL-URYVR rank 3 (better than pooled full at rank 4)

**DA_mech ↔ URY_URX module is rank 1 across ALL five specifications.** The module-level
signal is completely invariant to diffusion specification choice.

**RMEL-RMER** moves from rank 32 (D=I) to rank 38 (primary) but is demoted to rank 49
under state-specific diagonal and rank 54 under pooled full. Its ranking is somewhat
specification-dependent even among the simpler forms.

## Answer to the Key Question

> Does the ADEL/PDF result require full dense diffusion,
> or is it already present under identity / diagonal diffusion?

**The signal is already present under identity (ΔQ) and diagonal diffusion.**
Dense state-specific diffusion provides incremental refinement: ADEL-URYVR moves
from rank 5→3→2 as diffusion complexity increases, but does not first appear at
high rank only with full diffusion. The result is not a dense-diffusion artifact.
