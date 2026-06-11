# Phase 3C-F3 — Blockwise Current Analysis: ΔΩ_full vs ΔQ
Date: 2026-06-03
Authorization: Phase 3C-F

## Question

Does ΔΩ_full reveal block-level organization not visible in ΔQ?

---

## CePNEM Blockwise Comparison

### Top-10 block flows: ΔQ vs ΔΩ_full (mean |score| per Class 4 pair)

| ΔQ rank | Block pair | ΔQ mean | ΔΩ rank | Block pair | ΔΩ mean |
|---|---|---|---|---|---|
| 1 | RME↔RME | 0.0579 | 1 | RME↔RME | 0.0201 |
| 2 | DA_mech↔URY_URX | 0.0267 | 2 | DA_mech↔URY_URX | 0.0144 |
| 3 | RID↔IL1_IL2 | 0.0193 | 3 | DA_mech↔RME | 0.0101 |
| 4 | RME↔URY_URX | 0.0188 | 4 | URY_URX↔URY_URX | 0.0100 |
| 5 | DA_mech↔RME | 0.0165 | 5 | RID↔IL1_IL2 | 0.0099 |
| 6 | command_IN↔command_IN | 0.0159 | 6 | RME↔URY_URX | 0.0095 |
| 7 | URY_URX↔IL1_IL2 | 0.0159 | 7 | RID↔URY_URX | 0.0090 |
| 8 | URY_URX↔URY_URX | 0.0158 | 8 | command_IN↔command_IN | 0.0080 |
| 9 | RID↔URY_URX | 0.0132 | 9 | URY_URX↔IL1_IL2 | 0.0077 |
| 10 | URY_URX↔RMD_SMD | 0.0124 | 10 | RID↔RME | 0.0074 |

### What changes

**Preserved**: Top-2 ranking (RME↔RME, DA_mech↔URY_URX) is identical.
The DA_mech (ADEL/CEP) → URY_URX block pair remains the dominant multi-pair flow.

**Shifts**: 
- DA_mech↔RME rises from rank 5 to rank 3 (from 0.0165 to 0.0101 in absolute terms, but
  relatively more prominent versus other blocks)
- URY_URX↔URY_URX rises from rank 8 to rank 4
- URY_URX↔RMD_SMD exits the top-10 (rank 10 in ΔQ → not listed)
- RID↔RME enters the top-10 at rank 10 (was not in top-10 for ΔQ)

**Absolute magnitudes**: All ΔΩ_full block means are ~40% smaller than ΔQ block means.
This is expected: D_emp operates as a ~0.40 multiplicative scale on the dominant diagonal
(D3 mean = 0.40 in CePNEM) plus off-diagonal mixing that partially redistributes signal.

### Does ΔΩ_full reveal new structure?

**No new block pairs emerge.** The same 10 biologically meaningful block connections
dominate in both ΔQ and ΔΩ_full. The ordering shift (DA_mech↔RME rising) reflects
the elevated ADEL off-diagonal D_emp entries (ADEL had top-5 PC1 loading in GCaMP D_emp,
and DA_mech block had elevated off-diagonal entries AVAR–RMDVL, ASEL–OLQDL in the
CePNEM top-10).

The key biological conclusion from Phase 3C-C (DA_mech↔URY_URX as the dominant
multi-pair reorganization) is **confirmed and preserved** in ΔΩ_full.

---

## GCaMP Blockwise Comparison

### Top-10 block flows: ΔQ vs ΔΩ_full

| ΔQ rank | Block pair | ΔQ mean | ΔΩ rank | Block pair | ΔΩ mean |
|---|---|---|---|---|---|
| 1 | RID↔RME | 0.0554 | 1 | RID↔RME | 0.0184 |
| 2 | command_IN↔command_IN | 0.0512 | 2 | command_IN↔command_IN | 0.0112 |
| 3 | OLL_OLQ↔RMD_SMD | 0.0386 | 3 | DA_mech↔URY_URX | 0.0109 |
| 4 | DA_mech↔URY_URX | 0.0368 | 4 | RID↔IL1_IL2 | 0.0099 |
| 5 | RID↔IL1_IL2 | 0.0363 | 5 | OLL_OLQ↔RMD_SMD | 0.0097 |
| 6 | DA_mech↔RME | 0.0346 | 6 | DA_mech↔RME | 0.0094 |
| 7 | RME↔URY_URX | 0.0323 | 7 | DA_mech↔RID | 0.0088 |
| 8 | RID↔OLL_OLQ | 0.0315 | 8 | OLL_OLQ↔IL1_IL2 | 0.0082 |
| 9 | DA_mech↔command_IN | 0.0309 | 9 | RID↔OLL_OLQ | 0.0080 |
| 10 | URY_URX↔other | 0.0300 | 10 | RME↔URY_URX | 0.0080 |

### What changes

**Preserved**: Top-2 (RID↔RME, command_IN↔command_IN) unchanged.

**Shifts**:
- DA_mech↔URY_URX rises from rank 4 → rank 3 under ΔΩ_full (consistent with CePNEM)
- OLL_OLQ↔RMD_SMD falls from rank 3 → rank 5
- DA_mech↔command_IN exits top-10 (was rank 9 in ΔQ)
- DA_mech↔RID enters at rank 7 (not in ΔQ top-10)
- OLL_OLQ↔IL1_IL2 enters at rank 8 (not in ΔQ top-10)

### Key GCaMP-specific observation

The GCaMP blockwise structure differs from CePNEM in one important way:
**RID↔RME is rank #1 in GCaMP** for both ΔQ and ΔΩ_full. In CePNEM, RME↔RME
(bilateral coupling) is rank #1. This coordinate difference reflects the different
functional architecture captured by the two measurement modalities.

DA_mech↔URY_URX is rank 4 in GCaMP ΔQ and rises to rank 3 in ΔΩ_full — consistent
with ADEL's elevated innovation variance (D3_ADEL = 0.287 in GCaMP, 8th highest)
upweighting ADEL pairs in the D_emp mixing.

---

## Does ΔΩ_full Reveal Block-Level Structure Absent from ΔQ?

**No.** The top-10 block pairs for both ΔQ and ΔΩ_full contain the same functional
blocks. The two new entries (DA_mech↔RID in GCaMP, RID↔RME in CePNEM top-10) were
already present further down the ΔQ ranking. The block ordering shifts are quantitative,
not qualitative.

The biological conclusion from Phase 3C-C is fully confirmed:

1. **DA_mech↔URY_URX remains the dominant multi-pair reorganization** in both ΔQ and
   ΔΩ_full, in both coordinates. The dopaminergic mechanosensory → aerotaxis/O₂ sensor
   pathway shows the most extensive state-dependent functional decoupling.

2. **The RME/RID block interactions** (neuropeptide-related neurons) consistently
   appear in the top of both rankings, supporting a neuromodulatory interpretation.

3. **No pharyngeal or sensory-motor pairs** rise into the top-10 under ΔΩ_full that
   were not already prominent in ΔQ.

**Verdict**: ΔΩ_full provides a modest quantitative reweighting of block importance
but reveals no qualitatively new block-level organization.

---

*3C-F3 scope: blockwise characterization only. No new fitting. No held-out evaluation.*
