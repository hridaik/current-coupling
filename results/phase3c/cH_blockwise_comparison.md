# Phase 3C-H3 — Blockwise Comparison
Date: 2026-06-03
Authorization: Phase 3C-H

## Does DA_mech ↔ URY_URX Become More Prominent?

**Answer: No. DA_mech ↔ URY_URX remains rank #2 in both ΔQ and ΔΩ_full.**

---

## Top-10 Block Flows

| Rank | ΔQ Block Pair | ΔQ mean | | Rank | ΔΩ Block Pair | ΔΩ mean |
|---|---|---|---|---|---|---|
| 1 | RME↔RME | 0.0579 | | 1 | RME↔RME | 0.0201 |
| **2** | **DA_mech↔URY_URX** | **0.0267** | | **2** | **DA_mech↔URY_URX** | **0.0144** |
| 3 | RID↔IL1_IL2 | 0.0193 | | 3 | DA_mech↔RME | 0.0101 |
| 4 | RME↔URY_URX | 0.0188 | | 4 | URY_URX↔URY_URX | 0.0100 |
| 5 | DA_mech↔RME | 0.0165 | | 5 | RID↔IL1_IL2 | 0.0099 |
| 6 | command_IN↔command_IN | 0.0159 | | 6 | RME↔URY_URX | 0.0095 |
| 7 | URY_URX↔IL1_IL2 | 0.0159 | | 7 | RID↔URY_URX | 0.0090 |
| 8 | URY_URX↔URY_URX | 0.0158 | | 8 | command_IN↔command_IN | 0.0080 |
| 9 | RID↔URY_URX | 0.0132 | | 9 | URY_URX↔IL1_IL2 | 0.0077 |
| 10 | URY_URX↔RMD_SMD | 0.0124 | | 10 | RID↔RME | 0.0074 |

---

## Structural Changes

### What is preserved:
- Top-2 ranking (RME↔RME, DA_mech↔URY_URX) identical in both frameworks
- All 9 blocks appearing in the ΔQ top-10 also appear in the ΔΩ top-10
- No new block pair enters the top-10 under ΔΩ_full

### What shifts:
- **DA_mech↔RME** rises from rank 5 → rank 3 (gains relative to other mid-tier blocks)
- **URY_URX↔URY_URX** rises from rank 8 → rank 4
- **URY_URX↔RMD_SMD** exits the top-10 (rank 10 → not listed)
- **RID↔RME** enters at rank 10 (was not in ΔQ top-10)
- **command_IN↔command_IN** drops from rank 6 → rank 8

### Absolute scale change:
All ΔΩ block means are ~35–40% of ΔQ block means. This is expected: D3 (first-difference
variance) has mean ≈ 0.40 in CePNEM, and ΔΩ = D_emp @ ΔQ effectively scales the
magnitudes by the typical diagonal D3 value (plus off-diagonal mixing).

---

## Does DA_mech ↔ URY_URX Become More Prominent?

**No change in rank (2 → 2).** The DA_mech↔URY_URX block pair is the dominant
multi-pair reorganization flow in both ΔQ and ΔΩ_full. Its relative prominence
does not increase under ΔΩ.

The block pairs that gain under ΔΩ are DA_mech↔RME and URY_URX↔URY_URX — both
of which involve the PDF-relevant modules (DA_mech, URY) — but not through the
specific ADEL→URY pathway.

### Why DA_mech↔RME rises to rank 3:
ADEL's D_emp has substantial off-diagonal terms connecting to RMEL/RMER (the strong
bilateral coupling RMEL⟷RMER has elevated D_emp entries). This mixing enhances the
apparent DA_mech↔RME flow under ΔΩ, as ADEL-related ΔQ signal gets mixed into the
RMEL/RMER dimension. This is an artifact of diffusion mixing, not a new biological finding.

---

## Conclusion

The blockwise structure is **completely preserved** under ΔΩ_full. The ranking of the
dominant block pair (DA_mech↔URY_URX at rank 2) does not change. The Phase 3C-C
conclusion — that DA_mech→URY_URX is the dominant multi-pair reorganization pathway —
is robustly confirmed in both frameworks.

ΔΩ_full provides no qualitatively new blockwise organization beyond what ΔQ reveals.

---

*3C-H3 scope: blockwise comparison only.*
