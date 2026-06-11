# Phase 3D-2 — Module-Level Current Organization
Date: 2026-06-03
Authorization: Phase 3D

---

## D2.1 — Module Definitions

10 biologically motivated modules (same as Phase 3C-C):

| Module | Neurons (n) | Functional role |
|---|---|---|
| DA_mech | ADEL, CEPDL, CEPDR, CEPVL (4) | Dopaminergic mechanosensors; substrate-contact locomotion signaling |
| RID | RID (1) | Orphan neuropeptide modulator; pdf-1/pdf-2 source |
| RME | RMEL, RMER (2) | GABAergic head ring motors; pdf-1 source; head oscillation |
| URY_URX | URYDL, URYVL, URYVR, URXL (4) | O₂/aerotaxis sensors; pdfr-1-expressing; locomotion state |
| command_IN | AVAL, AVAR, AVEL, AVER, AVDL, AVJL, AVJR (7) | Forward/reversal command interneurons |
| OLL_OLQ | OLLL, OLLR, OLQDL, OLQDR, OLQVL, OLQVR (6) | Head mechanosensory neurons |
| IL1_IL2 | IL1DR, IL1L, IL1R, IL2DL, IL2DR, IL2VL, IL2VR (7) | Inner labial sensory neurons |
| pharyngeal | I1L, I1R, I2L, I2R, I3, M1, M3L, M3R, M4, MI, NSML, NSMR (12) | Pharyngeal circuit |
| RMD_SMD | RMDDR, RMDL, RMDVL, RMDVR, SMDVL (5) | Head motor neurons |
| other | AIBL, AIBR, AIZL, ASEL, ASGL, AUAL, AWAL, AWBL, AWCL, FLPL, RICL, RIVL, URBL (13) | Remaining interneurons/sensory |

All 61 neurons assigned; all module-level flows use Class 4 pairs only.

---

## D2.2–D2.3 — Module-Level Rankings: ΔQ vs All Ω

### Rank correlations at module level

| Comparison | ρ (module-level flows) |
|---|---|
| ΔΩ_pooled vs ΔQ | **0.980** |
| ΔΩ_ss_diag vs ΔQ | **0.987** |
| ΔΩ_ss_full vs ΔQ | **0.680** |

At the module level, ΔΩ_pooled and ΔΩ_ss_diag are essentially identical to ΔQ
(ρ > 0.98). Even the most divergent framework (ΔΩ_ss_full) preserves 68% of
the module-level ranking structure.

### Top-10 module flows across all frameworks

| Rank | ΔQ | ΔΩ_pooled | ΔΩ_ss_diag | ΔΩ_ss_full |
|---|---|---|---|---|
| **1** | **RME↔RME** | **RME↔RME** | **RME↔RME** | **RME↔RME** |
| **2** | **DA_mech↔URY_URX** | **DA_mech↔URY_URX** | **DA_mech↔URY_URX** | **DA_mech↔URY_URX** |
| 3 | RID↔IL1_IL2 | DA_mech↔RME | RID↔IL1_IL2 | DA_mech↔RME |
| 4 | RME↔URY_URX | URY_URX↔URY_URX | DA_mech↔RME | URY_URX↔URY_URX |
| 5 | DA_mech↔RME | RME↔URY_URX | RME↔URY_URX | RID↔RME |
| 6 | command_IN↔command_IN | RID↔IL1_IL2 | RID↔URY_URX | RME↔URY_URX |
| 7 | URY_URX↔IL1_IL2 | RID↔URY_URX | command_IN↔command_IN | URY_URX↔command_IN |
| 8 | URY_URX↔URY_URX | command_IN↔command_IN | URY_URX↔RMD_SMD | RID↔pharyngeal |
| 9 | RID↔URY_URX | RID↔RME | URY_URX↔URY_URX | command_IN↔command_IN |
| 10 | URY_URX↔RMD_SMD | URY_URX↔IL1_IL2 | URY_URX↔IL1_IL2 | URY_URX↔RMD_SMD |

---

## D2.4 — Targeted Test: DA_mech ↔ URY_URX Prominence

**DA_mech ↔ URY_URX (the dopaminergic mechanosensory → aerotaxis module pathway)
is rank #2 in every single Ω formulation.**

| Framework | DA_mech↔URY_URX rank |
|---|---|
| ΔQ | **2** |
| ΔΩ_pooled | **2** |
| ΔΩ_ss_diag | **2** |
| ΔΩ_ss_full | **2** |

This result is unambiguous: **Ω does NOT make DA_mech↔URY_URX more prominent.**
It is the dominant multi-pair module reorganization in both ΔQ and all Ω variants.

The absolute values change: ΔΩ_ss_full gives mean 0.0196 vs ΔQ's 0.0267 (scaled
differently), and the RELATIVE rank is preserved at #2 behind RME↔RME.

---

## D2.5 — Module-Level Organization Visible in Ω but Absent in Q

Pairs with >50% relative divergence between ΔΩ_ss_full and ΔQ:

| Block pair | ΔQ mean | ΔΩ_ss_full mean | Relative change | Biological interpretation |
|---|---|---|---|---|
| RID↔other | ~0.000 | 0.0083 | +564% | ΔQ≈0; imputed from RID's D_r hub |
| RID↔OLL_OLQ | 0.0008 | 0.0050 | +524% | Small ΔQ; inflated by RID D state-change |
| RID↔RMD_SMD | 0.0024 | 0.0083 | +245% | RID↔motor neurons: imputed signal |
| DA_mech↔command_IN | 0.0023 | 0.0052 | +122% | Low-signal block; inflated |
| OLL_OLQ↔IL1_IL2 | 0.0030 | 0.0070 | +134% | Sensory↔sensory; inflated |
| IL1_IL2↔other | 0.0025 | 0.0059 | +141% | Low-signal; inflated |
| RME↔RME | 0.0579 | 0.0254 | −56% | STRONG signal REDUCED by D state-change |

**Key observations:**

1. **All apparent "new" block-level structure in ΔΩ_ss_full originates from
   low-signal (ΔQ ≈ 0) block pairs.** The large relative changes (+100% to +564%)
   are entirely in pairs where ΔQ was near-zero. These are imputed values, not
   discovered signal.

2. **RME↔RME is REDUCED (−56%) under ΔΩ_ss_full.** This is the single strongest
   within-block signal, and state-specific Ω WEAKENS it. The state-specific D
   partially cancels the existing signal rather than amplifying it.

3. **The "RID↔other" divergence (+564%) looks dramatic in percentage terms but
   the absolute values are tiny** (ΔQ ≈ 0.000 → ΔΩ = 0.008). This is imputation
   from near-zero, not discovery of genuine signal.

4. **No high-signal block pair gains new prominence under Ω.** The pairs with
   largest ΔQ (RME↔RME, DA_mech↔URY_URX, RID↔IL1_IL2) are either unchanged
   in rank or weakened in absolute value.

### Is any module-level organization VISIBLE in Ω but ABSENT from Q?

**No.** All Ω variants preserve the same top-2 (RME↔RME, DA_mech↔URY_URX).
The divergences in lower-ranked pairs involve imputed signal from near-zero ΔQ.
No module pair that was silent in ΔQ becomes meaningfully active in Ω at a
rank above ~7.

---

## Summary of Module-Level Findings

| Question | Answer |
|---|---|
| Does DA_mech↔URY_URX become more prominent in Ω? | **No** — rank 2 in all frameworks |
| Does Ω reveal new block structure absent in Q? | **No** — all divergences are from zero-ΔQ imputation |
| Is module-level ΔΩ ≈ ΔQ? | **Yes** — ρ > 0.98 for diagonal variants |
| Does state-specific D change module-level conclusions? | **No** — DA_mech↔URY_URX rank = 2 in all |

**The module-level organization is fully captured by ΔQ. Ω provides no module-level
insight beyond what ΔQ reveals.**

---

*D2 scope: module-level characterization only.*
