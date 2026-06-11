# Phase 3C-C — Blockwise Current Attribution
Date: 2026-06-03
Authorization: Phase 3C

## Block Partition

The 61 neurons are partitioned into 10 biologically interpretable blocks:

| Block | Neurons (n) | Functional identity |
|---|---|---|
| DA_mech | ADEL, CEPDL, CEPDR, CEPVL (4) | Dopaminergic mechanosensors (dopamine; substrate contact / locomotion slowing) |
| RID | RID (1) | Orphan locomotion modulator (pdf-1/pdf-2, dense-core vesicles) |
| RME | RMEL, RMER (2) | GABAergic head ring motor neurons (pdf-1 source; head oscillation) |
| URY_URX | URYDL, URYVL, URYVR, URXL (4) | O₂/aerotaxis sensory neurons (pdfr-1-expressing; locomotion state integration) |
| command_IN | AVAL, AVAR, AVEL, AVER, AVDL, AVJL, AVJR (7) | Forward/reversal command interneurons |
| OLL_OLQ | OLLL, OLLR, OLQDL, OLQDR, OLQVL, OLQVR (6) | Head mechanosensory neurons |
| IL1_IL2 | IL1DR, IL1L, IL1R, IL2DL, IL2DR, IL2VL, IL2VR (7) | Inner labial sensory neurons |
| pharyngeal | I1L, I1R, I2L, I2R, I3, M1, M3L, M3R, M4, MI, NSML, NSMR (12) | Pharyngeal neurons |
| RMD_SMD | RMDDR, RMDL, RMDVL, RMDVR, SMDVL (5) | Head motor neurons |
| other | AIBL, AIBR, AIZL, ASEL, ASGL, AUAL, AWAL, AWBL, AWCL, FLPL, RICL, RIVL, URBL (13) | Remaining head interneurons and sensory neurons |

All 61 neurons assigned.

## Top Block Flows: Mean |ΔΩ_D2| (Class 4 pairs only)

| Rank | Block pair | Mean |ΔΩ| | Mean |ΔQ| | n Class 4 pairs | Interpretation |
|---|---|---|---|---|---|
| 1 | RME ↔ RME | 0.0615 | 0.0579 | 1 | RMEL–RMER bilateral coupling (within-block) |
| **2** | **DA_mech ↔ URY_URX** | **0.0274** | **0.0267** | **12** | **ADEL/CEP → URY/URX reorganization** |
| 3 | RID ↔ IL1_IL2 | 0.0211 | 0.0193 | 5 | RID → inner labial neurons |
| 4 | RME ↔ URY_URX | 0.0200 | 0.0188 | 8 | RMEL/RMER → URY/URX |
| 5 | DA_mech ↔ RME | 0.0169 | 0.0165 | 7 | ADEL/CEP → RMEL/RMER |
| 6 | URY_URX ↔ URY_URX | 0.0167 | 0.0158 | 5 | Within URY/URX (mutual) |
| 7 | URY_URX ↔ IL1_IL2 | 0.0161 | 0.0159 | 20 | URY/URX → inner labial |
| 8 | command_IN ↔ command_IN | 0.0159 | 0.0159 | 2 | Within-command (AVA-AVE, etc.) |
| 9 | RID ↔ URY_URX | 0.0145 | 0.0132 | 3 | RID → URY/URX |
| 10 | URY_URX ↔ RMD_SMD | 0.0131 | 0.0124 | 13 | URY/URX → head motor |

## Key Finding: DA_mech (ADEL/CEP) → URY_URX Is the Dominant Multi-Pair Flow

With n=12 Class 4 pairs, **DA_mech ↔ URY_URX is the second-largest block flow
by mean |ΔΩ| (0.0274) and the LARGEST multi-pair block flow by total signal**
(12 pairs × 0.0274 = 0.33, vs RME↔RME = 1 pair × 0.0615 = 0.062).

This block pair encompasses all four ADEL→URY/URX Class 4 pairs (ADEL–URYVR,
ADEL–URYDL, ADEL–URXL, plus CEP–URY pairs) and confirms that:

**The dopaminergic mechanosensory (DA_mech) → aerotaxis/O₂ sensor (URY_URX)
functional coupling is the most extensively reorganized block-to-block connection
during roaming vs. dwelling transition.**

## PDF-Attributed Block Flows

| Block pair | Mean |ΔΩ| | n PDF pairs |
|---|---|---|
| DA_mech ↔ RME | **0.0982** | 1 (ADEL–RMEL) |
| **DA_mech ↔ URY_URX** | **0.0680** | **4** |
| RME ↔ RME | 0.0615 | 1 (RMEL–RMER) |
| RME ↔ URY_URX | 0.0200 | 8 |
| URY_URX ↔ command_IN | 0.0147 | 4 |
| RID ↔ URY_URX | 0.0145 | 3 |

The two highest-signal PDF block flows are:
1. **DA_mech ↔ RME** (mean 0.098): single pair ADEL–RMEL with the strongest
   ADEL-to-RME coupling reorganization
2. **DA_mech ↔ URY_URX** (mean 0.068, n=4): the ADEL→URY cluster — the largest
   multi-pair PDF signal

## ADEL Block Participation

DA_mech (ADEL + CEP) block flows by target block:

| Target block | Mean |ΔΩ| | Mean |ΔQ| | n |
|---|---|---|---|
| URY_URX | **0.0274** | 0.0267 | 12 |
| RME | 0.0169 | 0.0165 | 7 |
| RID | 0.0121 | 0.0118 | 4 |
| IL1_IL2 | 0.0116 | 0.0113 | 17 |
| DA_mech (self) | 0.0074 | 0.0073 | 4 |
| OLL_OLQ | 0.0072 | 0.0071 | 17 |
| pharyngeal | 0.0041 | 0.0040 | 48 |
| other | 0.0035 | 0.0034 | 33 |
| command_IN | 0.0024 | 0.0023 | 21 |
| RMD_SMD | 0.000 | 0.000 | 15 |

**ADEL participates disproportionately in URY_URX block flow**: the DA_mech ↔ URY_URX
flow (0.027) is the highest DA_mech cross-block flow, substantially above the mean
DA_mech flow to other blocks (average ~0.006 excluding URY_URX and RME).

The near-zero DA_mech ↔ RMD_SMD flow indicates ADEL/CEP have no state-dependent
coupling reorganization with head motor neurons (RMDL, RMDVR, SMDVL) — all changes
are concentrated in the neuromodulatory pathway (RME, URY_URX).

## Summary

The blockwise attribution confirms:

1. **The dominant multi-pair current reorganization is DA_mech → URY_URX** (12 pairs,
   mean ΔΩ = 0.027) — the dopaminergic mechanosensory → aerotaxis/locomotion-state
   pathway shows the largest aggregate state-dependent decoupling.

2. **PDF signal is concentrated in two block flows**: DA_mech↔RME (ADEL→RMEL, the
   single strongest PDF pair by ΔΩ) and DA_mech↔URY_URX (the 4 ADEL→URY pairs).

3. **ADEL participates disproportionately** in state-dependent current reorganization
   relative to other DA_mech neurons (CEP). The CEP→URY and CEP→RME flows contribute
   to the block flow, but ADEL-specific pairs (ranks 5, 9, 10 in ΔΩ) dominate.

---

## Block Flow Matrices Saved

- `block_flow_deltaomega.npy`: (10×10) mean |ΔΩ_D2| per block pair (Class 4)
- `block_flow_deltaq.npy`: (10×10) mean |ΔQ| per block pair (Class 4)

Block ordering: DA_mech, RID, RME, URY_URX, command_IN, OLL_OLQ, IL1_IL2,
pharyngeal, RMD_SMD, other.

---
*3C-C scope: blockwise attribution only. No hypothesis testing. No new fitting.*
