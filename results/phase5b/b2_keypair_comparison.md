# Phase 5B.2 — Key Pair Comparison Under ΔΩ_ss
Date: 2026-06-12

---

## Five Tracked Pairs: ΔΩ_ss vs ΔQ

| Pair | ΔΩ_ss | ΔΩ_ss Rank | ΔQ | ΔQ Rank | Rank Change | Direction |
|------|-------|-----------|-----|---------|-------------|-----------|
| ADEL–URYVR | −0.0688 | **2** | −0.063 | 5 | +3 (promoted) | Dwell, dwell |
| ADEL–URYDL | −0.0498 | **6** | −0.060 | 9 | +3 (promoted) | Dwell, dwell |
| ADEL–RMEL | −0.0549 | **4** | −0.054 | 10 | +6 (promoted) | Dwell, dwell |
| RMEL–URYDL | −0.0310 | 23 | −0.063 | 16 | −7 (demoted) | Dwell, dwell |
| RMEL–RMER | −0.0254 | 38 | −0.058 | 32 | −6 (demoted) | Dwell, dwell |

All five pairs remain negative (dwelling-dominant) under both formulations.
Sign stability: 5/5 pairs agree. Direction of state preference is robust.

---

## ADEL–URYVR

**ΔQ:** −0.063, rank 5 of 1321. Top 0.38% by precision difference.
**ΔΩ_ss:** −0.0688, rank 2 of 1321. Top 0.15% by state-specific current.

The state-specific current formulation promotes ADEL–URYVR from rank 5 to rank 2.
This is the **most-promoted pair** among the ADEL-PDF circuit triplet.
ADEL expresses pdf-1 (PDF neuropeptide); URYVR is a URY sensory neuron.
The pair has 0 funatlas observations and remains an untested prediction.

Under ΔΩ_ss: the dwelling-dominant current value is **stronger** relative to ΔQ.
Interpretation: not only does the conditional precision show dwelling-dominance, but
the full diffusion-weighted current also amplifies the dwell-vs-roam contrast for this pair.
The increased |ΔΩ_ss| relative to |ΔQ| indicates the diffusion enhancement (D_roam vs D_dwell)
cooperates with the precision difference to amplify the state signal for ADEL–URYVR.

---

## ADEL–URYDL

**ΔQ:** −0.060, rank 9 of 1321.
**ΔΩ_ss:** −0.0498, rank 6 of 1321.

Promoted +3 places. The dwelling-dominant signal persists under ΔΩ_ss.
|ΔΩ_ss| < |ΔQ| for this pair, meaning the diffusion factor partially attenuates the
precision difference, but not enough to drop it out of the top-10.

---

## ADEL–RMEL

**ΔQ:** −0.054, rank 10 of 1321.
**ΔΩ_ss:** −0.0549, rank 4 of 1321.

Promoted +6 places. The largest rank improvement among the ADEL-PDF triplet.
|ΔΩ_ss| ≈ |ΔQ| (essentially equal magnitude), but rank is higher because neighboring pairs
are more strongly affected by the diffusion factor.
ADEL expresses pdf-1; RMEL expresses pdfr-1/pdf-1 (bilateral motor neuron).
Under ΔΩ_ss this becomes the 4th-most-differentiated pair in the entire Class-4 set.

---

## RMEL–URYDL

**ΔQ:** −0.063, rank 16 of 1321.
**ΔΩ_ss:** −0.0310, rank 23 of 1321.

Demoted −7 places. The dwelling-dominant signal persists (both negative), but is weaker
relative to its neighbors under ΔΩ_ss.
|ΔΩ_ss| is substantially smaller than |ΔQ| for this pair: the diffusion factor partially
cancels the precision difference when the full product D_s @ Q_s is taken.
RMEL expresses pdf-1/pdfr-1; URYDL is a URY sensory neuron.
This pair is intermediate in both formulations — not in the top-20 for ΔΩ_ss, but still
in the top 25.

---

## RMEL–RMER (Confirmed Pair)

**ΔQ:** −0.058, rank 32 of 1321.
**ΔΩ_ss:** −0.0254, rank 38 of 1321.

Demoted −6 places. The confirmed case weakens under ΔΩ_ss.
|ΔΩ_ss| = 0.0254 vs |ΔQ| = 0.058: a substantial reduction in magnitude.
The diffusion factor (D_roam vs D_dwell product) partially cancels the precision difference
for RMEL–RMER.

**Biological interpretation:** For RMEL–RMER, the dwelling-dominant conditional precision
(ΔQ < 0) is attenuated when weighted by the state-specific diffusion matrix. This could mean
that the RMEL–RMER conditional coupling is precision-specific (Q-driven) rather than
diffusion-amplified (D-Q product-driven). The funatlas confirmation (wt q = 0.0002) remains
valid; only the rank within the framework changes.

---

## Summary Assessment

| Group | Rank change under ΔΩ_ss | Interpretation |
|-------|------------------------|----------------|
| ADEL-PDF triplet (URYVR, URYDL, RMEL) | **Promoted +3, +3, +6** | ΔΩ_ss amplifies ADEL-PDF circuit signal |
| RMEL-connected (URYDL, RMER) | Demoted −7, −6 | ΔΩ_ss attenuates RMEL-centered coupling |
| Sign stability | 5/5 negative (dwelling) | Dwelling-dominant prediction is robust |

**Conclusion:** The ADEL-PDF circuit predictions are strengthened under ΔΩ_ss.
The RMEL hub pairs (RMEL–URYDL, RMEL–RMER) are weakened.
This creates a subtle split: ΔΩ_ss promotes ADEL as the central node (ranks 2, 4, 6)
while demoting RMEL-centric pairs (ranks 23, 38 vs 16, 32 under ΔQ).
