# Phase 10C.5 — Timescale Diffusion Summary
Date: 2026-06-15

## Source

Phase 4C D(τ) matrices: D_cepnem_tau{τ}_{state}.npy for τ ∈ {1, 2, 5, 10, 20}.
Reused here with same Q_roam and Q_dwell matrices (Phase 2) to compute ΔΩ(τ).
No new computation of Q — only D varies across τ.

Note: τ=1 matrix was already used as primary D in Phase 3D.
Confirmed: ρ(|ΔΩ(τ=1)|, |ΔΩ_primary|) = 1.0 (identical).

## Results Table

| τ (frames) | τ (seconds) | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–URYDL | RMEL–RMER | PDF/20 | ρ_prim |
|------------|------------|-----------|-----------|---------|----------|---------|-------|-------|
| 1 (primary) | 0.25 s | **2** (−0.0688) | **6** (−0.0498) | **4** (−0.0549) | 23 (−0.0310) | 38 (−0.0254) | 4/20 | 1.000 |
| 2 | 0.5 s | **4** (−0.0853) | **7** (−0.0701) | **3** (−0.0859) | 22 (−0.0466) | 48 (−0.0371) | 3/20 | 0.650 |
| 5 | 1.25 s | **3** (−0.1467) | 12 (−0.0909) | **4** (−0.1454) | 17 (−0.0844) | 126 (−0.0495) | 6/20 | 0.331 |
| 10 | 2.5 s | **2** (−0.2166) | 20 (−0.1153) | **7** (−0.1348) | 37 (−0.1028) | 120 (−0.0772) | 4/20 | 0.238 |
| 20 | 5.0 s | **3** (−0.2455) | 220 (−0.0920) | 70 (−0.1333) | 537 (−0.0541) | 171 (−0.1007) | 2/20 | 0.133 |

All signs remain negative (dwelling-dominant) at all timescales for all five pairs.

## Sign Stability

| Pair | τ=1 | τ=2 | τ=5 | τ=10 | τ=20 | Always negative? |
|------|-----|-----|-----|------|------|-----------------|
| ADEL–URYVR | − | − | − | − | − | **YES** |
| ADEL–URYDL | − | − | − | − | − | **YES** |
| ADEL–RMEL  | − | − | − | − | − | **YES** |
| RMEL–URYDL | − | − | − | − | − | **YES** |
| RMEL–RMER  | − | − | − | − | − | **YES** |

Sign stability: 5/5 pairs, all 5 timescales — 100% consistent.

## Rank Stability

**ADEL–URYVR:** Ranks 2–4 across τ=1,2,5,10,20. Always in the top-5.
This is the most timescale-stable primary result. At τ=10 and τ=20, it is
actually RANK 2–3 — even more prominent at longer timescales.

**ADEL–URYDL:** Stable (ranks 6–12) at τ=1,2,5; drops to rank 20 at τ=10;
falls sharply to rank 220 at τ=20. Rank degradation begins at τ≈10 frames (2.5 s).
This is consistent with Phase 4C's observation that ADEL-URYDL ΔD sign was
consistently positive at all timescales (roaming-dominant diffusion), which partially
opposes the dwelling-dominant Q signal at longer lags.

**ADEL–RMEL:** Ranks 3–7 at τ=1,2,5,10; drops to rank 70 at τ=20.
Moderately stable at short-medium timescales.

**RMEL–URYDL:** Ranks 17–37 at τ=1,2,5,10; drops to rank 537 at τ=20.
Timescale-sensitive; meaningful primarily at short lags.

**RMEL–RMER:** Ranks 38–48 at τ=1,2; drops sharply to 120–171 at longer τ.
Most timescale-unstable of the key pairs, consistent with its instability in
Phases 10A (coupling correction) and 10B (residualization).

## PDF Enrichment Stability

- PDF top-20 count: 4, 3, 6, 4, 2 across τ=1,2,5,10,20.
- At τ=5, the top-20 contains 6 PDF pairs — maximum enrichment.
- At τ=20, the count drops to 2 (approaching chance level = 61/1321 × 20 ≈ 0.9).

The top-20 PDF enrichment degrades at long timescales (τ=20) where the global
ranking structure reorganizes substantially (ρ_prim = 0.133).

## Notes from Phase 4C Context

Phase 4C showed:
- |ΔΩ| self-correlation between timescales decays rapidly: ρ(τ=1, τ=20) ≈ 0.13
- The ΔΩ–ΔQ alignment also decays: ρ = 0.331 (τ=1) → 0.136 (τ=20)
- But sign stability for ADEL-PDF pairs was already noted as a key positive finding

The present analysis confirms and extends this: ADEL-URYVR is top-5 at ALL timescales.
The timescale sensitivity primarily affects the weaker ADEL-URYDL and RMEL-linked pairs.

## Conclusion

> Is the primary ADEL/PDF ΔΩ_ss signal timescale-invariant?

- **ADEL–URYVR: YES** — top-5 at τ=1,2,5,10,20; always dwelling-dominant.
- **ADEL–URYDL: MOSTLY** — stable at τ≤5 (top-12), degrades at τ≥10.
- **Sign stability: COMPLETE** — 5/5 pairs × 5 timescales all negative.
- **Module (DA_URY): NOT CHECKED separately here** — but ADEL-URYVR stability
  implies DA_mech ↔ URY_URX remains highly ranked at all timescales.
