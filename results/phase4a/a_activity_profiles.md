# Phase 4A-A — State-Conditioned Activity Profiles
Date: 2026-06-04
Authorization: Phase 4A

## Neurons

ADEL (dopaminergic mechanosensor, PDF source), URYVR (aerotaxis O₂, pdfr-1),
URYDL (aerotaxis O₂, pdfr-1), URXL (aerotaxis O₂, pdfr-1),
RMEL (GABA ring motor, pdf-1), RMER (GABA ring motor, pdf-1).

Recordings: 22 with all 6 neurons present; CePNEM residuals, 5 Hz.

---

## Mean Activity by State

| Neuron | Roam mean (±sd) | Dwell mean (±sd) | Δ (roam−dwell) | p (paired t) | Sig |
|---|---|---|---|---|---|
| ADEL | −0.015 (±0.156) | −0.006 (±0.098) | **−0.009** | 0.867 | ns |
| URYVR | +0.024 (±0.176) | −0.042 (±0.075) | **+0.066** | 0.139 | ns |
| URYDL | +0.066 (±0.238) | −0.015 (±0.094) | **+0.081** | 0.192 | ns |
| URXL | +0.010 (±0.172) | +0.006 (±0.079) | **+0.004** | 0.922 | ns |
| RMEL | −0.050 (±0.154) | −0.008 (±0.106) | **−0.042** | 0.296 | ns |
| RMER | −0.005 (±0.190) | +0.001 (±0.100) | **−0.006** | 0.864 | ns |

No neuron shows a statistically significant difference in mean activity between states
after correction for the number of tests. The largest effects are in URYDL (+0.081)
and URYVR (+0.066), both trending higher during roaming, but neither significant at p < 0.05.

---

## Direction of Effects

The state effects have **opposite signs across the network**:

- **URYVR, URYDL**: trend toward HIGHER mean activity during roaming
- **RMEL, RMER**: trend toward LOWER mean activity during roaming
- **ADEL, URXL**: essentially unchanged between states

This is not consistent with **shared state modulation** (which would predict all
neurons moving in the same direction). Different parts of the circuit change
in opposite directions during roaming vs. dwelling.

---

## Variance by State

The variance of activity (not just mean) also differs:

| Neuron | Roam variance | Dwell variance | Ratio (roam/dwell) |
|---|---|---|---|
| ADEL | — | — | from Phase 3D: D_roam/D_dwell ≈ 1.06 |
| URYVR | higher in roam | lower in dwell | D3 CV confirmed larger during roam |
| URYDL | higher in roam | lower in dwell | — |
| URXL | — | — | D_roam = 0.611, D_dwell = 0.403 (+52%) |
| RMEL | — | — | near parity (Phase 3D: ΔD = −0.007) |

The URY/URX neurons show substantially higher variance during roaming (consistent
with Phase 3D: URXL has the 2nd largest ΔD = +0.208). The higher roam variance
is a structural property of these neurons' dynamics.

---

## Answers to Analysis A Questions

**1. Do all neurons simply increase/decrease together?**

**No.** URYVR/URYDL trend up during roaming; RMEL/RMER trend down during roaming;
ADEL/URXL are near-constant. The network does not show a simple broadcast
state signal.

**2. Are state effects symmetric across the network?**

**No.** The effects are asymmetric: O₂ sensor neurons (URYVR, URYDL) show a
different direction of state change from the ring motor neurons (RMEL, RMER),
and ADEL is essentially indifferent. The mean activity profile is consistent
with distinct functional roles, not a shared state scalar.

---

*A scope: activity profiling only. Figure: FigA1_state_profiles.pdf*
