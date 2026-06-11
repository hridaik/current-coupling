# Phase 4A-C — State-Transition Trajectories
Date: 2026-06-04
Authorization: Phase 4A

## Method

172 dwell→roam (D2R) transitions and 174 roam→dwell (R2D) transitions identified
across 22 recordings. Activity aligned to transition onset (t=0), window ±60 s
(±300 frames at 5 Hz). Activity z-scored to pre-window 10 s baseline per epoch.

---

## C1 — Dwell → Roam Transitions

| Neuron | Estimated onset | Notes |
|---|---|---|
| RMEL | **≈ 0.2 s** | Earliest; changes essentially at transition onset |
| URXL | ≈ 2.6 s | Second; rapid O₂ sensor response |
| URYVR | ≈ 3.4 s | Third |
| URYDL | ≈ 17.0 s | Very late / weak; may not be a reliable D2R response |
| ADEL | **No clear onset** | No threshold-crossing detected |

**At dwell→roam transitions:**
- **RMEL leads** — the GABA ring motor / PDF-source neuron changes first (within
  1 frame of the transition label). This is consistent with RMEL being involved
  in driving the state switch rather than responding to it.
- **URY/URX follow** within 3–4 seconds — the aerotaxis/O₂ sensors respond shortly
  after roaming begins, likely reflecting the animal's changed position relative
  to O₂ gradients.
- **ADEL does not show a reliable trajectory deflection** at D2R transitions.
  ADEL's activity does not systematically change when the animal begins roaming.

## C2 — Roam → Dwell Transitions

| Neuron | Estimated onset | Notes |
|---|---|---|
| URYVR | **≈ 1.4 s** | Earliest; O₂ sensor responds first |
| ADEL | ≈ 2.0 s | Second; ADEL changes shortly after URY |
| URXL | ≈ 2.2 s | Third |
| RMEL | ≈ 3.8 s | Fourth; ring motor changes last |
| URYDL | **No clear onset** | No threshold-crossing detected |

**At roam→dwell transitions:**
- **URYVR leads** — the pdfr-1-expressing O₂ sensor responds first. This is
  consistent with the animal detecting a favorable O₂/food environment and
  initiating dwelling. The O₂ sensor triggers the state switch.
- **ADEL changes second** (≈2 s), closely following URYVR. This temporal
  proximity is the clearest Activity evidence for ADEL–URY coordination.
- **RMEL changes last** — the PDF-producing ring motor follows rather than leads.

---

## C3 — Temporal Ordering Asymmetry

The transition-direction asymmetry is the most biologically informative finding:

| | First to change | Last to change |
|---|---|---|
| D→R (dwell to roam) | RMEL (ring motor) | URY sensors (late) |
| R→D (roam to dwell) | URYVR (O₂ sensor) | RMEL (ring motor) |

This suggests a circuit where:
- **Initiating roaming**: a ring motor signal (RMEL) precedes sensory adjustments
- **Initiating dwelling**: sensory detection (URYVR) precedes motor adjustment

ADEL is conspicuously absent from D→R transitions (no clear response) but
responds at R→D transitions (second, after URYVR). This suggests ADEL's
state-dependent activity is more relevant to the dwelling state entry than
to roaming initiation.

---

## Answers to Analysis C Questions

**1. Which neurons change first?**
- D→R: RMEL first, then URXL, URYVR
- R→D: URYVR first, then ADEL, URXL

**2. Do ADEL and URY move together?**
Partially. At R→D transitions, ADEL changes just after URYVR (offset ≈0.6s),
suggesting sequential rather than simultaneous activation. At D→R transitions,
ADEL does not show a reliable response.

**3. Are there reproducible motifs?**
Yes: a reproducible two-motif pattern exists:
- **D→R**: RMEL → URX/URY (motor-first, sensor-second)
- **R→D**: URY → ADEL (sensor-first, dopaminergic response second)

---

*C scope: transition analysis only. Figure: FigA3_transition_trajectories.pdf*
