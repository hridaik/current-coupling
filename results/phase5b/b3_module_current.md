# Phase 5B.3 — Module Organization Under ΔΩ_ss
Date: 2026-06-12

---

## Module Definitions

Neurons grouped by known functional role (from Phase 3D module analysis):
- **DA_mech:** ADAL, ADAR, PDAL, PDAR — mechanosensory and dopamine neurons
- **URY_URX:** URYVR, URYDL, URYVL, URYDL, URXL, URXR — oxygen/URY/URX sensory
- **RME:** RMEL, RMER, RMEV, RMED — ring motor neurons
- **IL:** IL1DL, IL1DR, IL1L, IL1R, IL1VL, IL1VR, IL2DL, IL2DR, IL2L, IL2R, IL2VL, IL2VR — inner labial neurons
- **AV:** AVJL, AVJR, AVEL, AVER — command interneurons

Module-block mean |ΔΩ_ss| computed over all Class-4 pairs within each cross-block category.

---

## Top Module Blocks by Mean |ΔΩ_ss|

| Block | Mean |ΔΩ_ss| | Mean |ΔQ| | Rank (ΔΩ) | Rank (ΔQ) | Change |
|-------|--------------|-----------|------------|-----------|--------|
| DA_mech ↔ URY_URX | **0.0428** | 0.0421 | **1** | **1** | Same |
| DA_mech ↔ RME | 0.0251 | 0.0180 | **2** | 5 | Promoted +3 |
| AV ↔ IL | 0.0243 | 0.0263 | 3 | 2 | Demoted −1 |
| IL ↔ IL | 0.0238 | 0.0118 | **4** | 9 | **Promoted +5** |
| DA_mech ↔ AV | 0.0231 | 0.0241 | 5 | 3 | Demoted −2 |
| AV ↔ URY_URX | 0.0218 | 0.0258 | 6 | 4 | Demoted −2 |
| RME ↔ URY_URX | 0.0195 | 0.0207 | 7 | 6 | Demoted −1 |
| IL ↔ URY_URX | 0.0174 | 0.0231 | 8 | 7 | Demoted −1 |
| DA_mech ↔ IL | 0.0163 | 0.0189 | 9 | 8 | Demoted −1 |

---

## Key Finding: DA_mech ↔ URY_URX Remains #1

The DA_mech ↔ URY_URX block has the highest mean |ΔΩ_ss| of any module block (0.0428)
AND the highest mean |ΔQ| (0.0421). The two formulations agree completely on the
top module: mechanosensory/dopaminergic neurons interact most strongly (in state-specific
current) with URY/URX sensory neurons.

This block contains the ADEL–URYVR, ADEL–URYDL, ADEL–RMEL pairs.
Under ΔΩ_ss the ADEL sub-block (DA_mech ↔ URY_URX) is further amplified by the
cooperation between precision difference and diffusion weights.

---

## Novel Under ΔΩ_ss: IL ↔ IL Block

Under ΔQ the IL ↔ IL block ranks 9th (mean |ΔQ| = 0.0118).
Under ΔΩ_ss it rises to rank 4 (mean |ΔΩ_ss| = 0.0238 — **doubling in magnitude**).

This is the most significant structural change between ΔQ and ΔΩ_ss at the module level.
The IL (inner labial) neurons form a within-module block that is specifically amplified
when diffusion weighting is applied. IL neurons mediate mechanosensation around the
mouth and are involved in feeding-state modulation.

The rise of IL ↔ IL under ΔΩ_ss is consistent with: the D matrix encoding more IL–IL
correlated diffusion in one behavioral state (likely dwelling/feeding), amplifying what
was already a non-zero ΔQ signal.

---

## Novel Under ΔΩ_ss: DA_mech ↔ RME Block

Under ΔQ the DA_mech ↔ RME block ranks 5th (mean |ΔQ| = 0.0180).
Under ΔΩ_ss it rises to rank 2 (mean |ΔΩ_ss| = 0.0251).

This block includes ADEL–RMEL (ΔΩ_ss rank 4, promoted from ΔQ rank 10).
The rise of the DA_mech ↔ RME block under ΔΩ_ss is driven primarily by the ADEL–RMEL pair,
which benefits from a diffusion amplification of its already-high precision difference.

---

## Demoted Under ΔΩ_ss: AV ↔ IL and AV ↔ URY_URX

The AV-interneuron blocks (AV ↔ IL at rank 2 under ΔQ, AV ↔ URY_URX at rank 4)
both fall in rank under ΔΩ_ss (ranks 3 and 6 respectively).

This reflects the demotion of the AVJR–OLLR, AVJR–OLQVR pairs (from ΔQ ranks 3, 4 to
ΔΩ_ss ranks 9, 8). The AV-interneuron ↔ sensory-circuit signature is more prominent
under precision difference than under diffusion-weighted current.

---

## Module Stability Summary

**Stable (same rank or ±1):**
- DA_mech ↔ URY_URX (#1 in both)
- AV ↔ IL (#2 → #3)
- RME ↔ URY_URX (#6 → #7)

**Promoted under ΔΩ_ss:**
- IL ↔ IL (#9 → #4, +5 places): most novel structural difference
- DA_mech ↔ RME (#5 → #2, +3 places): ADEL–RMEL driven

**Demoted under ΔΩ_ss:**
- DA_mech ↔ AV (#3 → #5): AVJR-pair driven
- AV ↔ URY_URX (#4 → #6): same

**Conclusion:** The ΔΩ_ss formulation reveals a more feeding-circuit-centric organization:
DA_mech ↔ URY_URX remains the core, with IL↔IL and DA_mech↔RME rising in prominence.
The interneuron (AV) blocks that were prominent under ΔQ are slightly demoted.
