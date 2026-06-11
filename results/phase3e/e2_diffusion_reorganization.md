# Phase 3E-2 — State-Dependent Diffusion Reorganization
Date: 2026-06-03
Authorization: Phase 3E

## What Biological Organization Is Carried by ΔD?

ΔD_ii = D_roam[i,i] − D_dwell[i,i] = change in per-neuron innovation variance
between roaming and dwelling states.

---

## E2.1 — Top Neurons by ΔD (Ranked)

### Roaming-dominant neurons (D_roam >> D_dwell)

| Rank | Neuron | ΔD | D_roam | D_dwell | Biological role |
|---|---|---|---|---|---|
| 1 | RMDVL | **+0.225** | 0.613 | 0.389 | Head ring motor (dorsal-ventral) |
| 2 | **URXL** | **+0.208** | 0.611 | 0.403 | **Aerotaxis/O₂ sensor (pdfr-1)** |
| 3 | IL1L | **+0.197** | 0.457 | 0.260 | Inner labial sensory |
| 4 | ASGL | **+0.176** | 0.519 | 0.343 | Interneuron |
| 5 | FLPL | **+0.150** | 0.520 | 0.370 | Touch mechanosensory (FLP) |
| 6 | **URYVL** | **+0.149** | 0.564 | 0.415 | **Aerotaxis/O₂ sensor (pdfr-1)** |
| 7 | URBL | +0.105 | 0.497 | 0.393 | Head sensory neuron |
| 8 | OLQVL | +0.100 | 0.516 | 0.416 | Head mechanosensory (OLQ) |
| 9 | M1 | +0.099 | 0.461 | 0.362 | Pharyngeal motor |
| 10 | MI | +0.096 | 0.408 | 0.312 | Pharyngeal interneuron |

### Dwelling-dominant neurons (D_dwell >> D_roam)

| Rank | Neuron | ΔD | D_roam | D_dwell | Biological role |
|---|---|---|---|---|---|
| 1 | AIZL | **−0.167** | 0.343 | 0.510 | Olfactory interneuron (AIZ) |
| 2 | AVJR | **−0.150** | 0.305 | 0.455 | Reversal/command interneuron |
| 3 | OLLL | **−0.133** | 0.278 | 0.411 | Head mechanosensory (OLL) |
| 4 | M3R | −0.104 | 0.332 | 0.436 | Pharyngeal motor (M3) |
| 5 | SMDVL | −0.100 | 0.377 | 0.477 | Head motor (SMD) |
| 6 | IL1DR | −0.095 | 0.278 | 0.372 | Inner labial (IL1) |
| 7 | AIBL | −0.089 | 0.269 | 0.358 | Bistable interneuron (AIB) |
| 8 | RMDL | −0.071 | 0.347 | 0.418 | Head motor |
| 9 | I2R | −0.063 | 0.306 | 0.369 | Pharyngeal sensory |
| 10 | AWAL | −0.062 | 0.337 | 0.399 | Olfactory sensory (AWA) |

---

## E2.2 — Module-Level ΔD

(From Phase 3D-1 data; repeated here for reference)

| Module | Mean ΔD_ii | Biological notes |
|---|---|---|
| **URY_URX** | **+0.078** | URXL (+0.208), URYVL (+0.149) drive this; pdfr-1 sensors most active during roaming |
| RMD_SMD | +0.027 | Head motors; mixed signal (RMDVL +0.225, RMDL −0.071) |
| DA_mech | +0.025 | ADEL/CEP more dynamically active during roaming |
| IL1_IL2 | +0.019 | Inner labial; IL1L +0.197 but IL1DR −0.095 |
| RID | +0.019 | Single neuron; roaming-slightly-dominant |
| other | +0.020 | Mixed interneurons |
| pharyngeal | +0.008 | Weakly roaming-dominant overall |
| command_IN | +0.012 | Mixed; AVJR −0.150 partially offsets others |
| OLL_OLQ | +0.002 | Near neutral; OLLL −0.133 vs OLQVL +0.100 cancel |
| **RME** | **−0.007** | GABA ring motors slightly less active during roaming |

---

## E2.3 — ΔD vs ΔQ Independence

| Metric | Value |
|---|---|
| ρ(ΔD_ii, mean|ΔQ|_i) across 61 neurons | **−0.152** |
| p-value | **0.241** (not significant) |

The neurons that change most in innovation variance between states (RMDVL, URXL, AIZL)
are NOT the neurons that show the largest state-dependent Q changes. The correlation
is essentially zero (ρ = −0.15, not significant).

**Diffusion (D) and functional connectivity (Q) are independent structures in
state-dependent neural reorganization.** They capture different biological aspects:
- D captures how DYNAMICALLY VARIABLE each neuron is within each state
- Q captures how COORDINATELY REGULATED pairs of neurons are between states

---

## Biological Interpretation

### The URY/URX axis as roaming-dominant diffusion hub

URXL (+0.208) and URYVL (+0.149) are the 2nd and 6th most roaming-dominant neurons
by ΔD. These are pdfr-1-expressing aerotaxis/O₂-sensing neurons. Their high
roaming-state D means their activity is more dynamically variable when the animal
is actively moving.

This is consistent with the proposed role of URY/URX neurons: during roaming, the
animal is moving through O₂ gradients, and these sensor neurons must dynamically
track the changing O₂ level. Their high innovation variance during roaming reflects
this active sensing role.

ADEL (dopaminergic, DA_mech module): ΔD = +0.031 (smaller than URY/URX). ADEL
is also somewhat more active during roaming, consistent with its role in substrate
contact signaling during locomotion — but the effect is smaller than for URY/URX.

### The AIZL/AVJR axis as dwelling-dominant diffusion hub

AIZL (−0.167) and AVJR (−0.150) are the two most dwelling-dominant neurons. AIZL
is an interneuron involved in olfactory integration that often shows graded activity
during local search behavior. AVJR is a command interneuron. During dwelling, the
animal may be in a "local search" mode characterized by frequent reversals and
turning — both AIZL (evaluating olfactory cues) and AVJR (controlling reversals)
would be highly variable during this state.

### Conclusion

ΔD reveals a biologically coherent reorganization: roaming is characterized by high
O₂-sensor dynamics (URY/URX), while dwelling is characterized by high interneuron/
command dynamics (AIZL, AVJR). This is an independent characterization of state-
dependent neural variability that complements ΔQ.

**However, this ΔD biology does not translate into Ω-specific information** (as
shown in Phase 3D), because ΔD and ΔQ are largely independent structures.

---

*E2 scope: diffusion reorganization characterization only.*
