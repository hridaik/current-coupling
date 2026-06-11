# Phase 3E-4 — Network Motif Analysis
Date: 2026-06-03
Authorization: Phase 3E

## Conditional Trigger Assessment

Phase 3E-4 is triggered "only if E1 or E3 show signal." Assessment:

- **E1**: Disagreement R is a scaling artifact of |ΔQ|; no new biological structure
- **E3**: No topological distinction between ΔΩ and ΔQ pair sets; OU prediction not supported

Neither E1 nor E3 showed clear signal warranting full motif analysis. However,
a preliminary motif assessment was conducted to document the absence of structure.

---

## Preliminary Motif Scan: Top-100 Ω-only Pairs

"Ω-only" pairs: ΔQ = 0, ΔΩ ≠ 0 (n = 1,078 total; top 100 by |ΔΩ| analyzed).

### Common-Source Motif

PDF source neurons (Bentley ESconnectome): ADEL, RID, RMEL, RMER, AVDL.
Expected fraction if random: ~2 × (5/61) × 100 ≈ 16/100.

**Observed: 30/100 top-Ω-only pairs involve a PDF source.**
Enrichment: 30/16 ≈ 1.9×.

This reflects the Phase 3C-G/H finding: RID, RMEL, RMER are diffusion hubs that
impute signal into their zero-ΔQ pair partners.

### Common-Target Motif

PDF target neurons (pdfr-1 expressing, Bentley): ~16 neurons.
Expected fraction: ~2 × (16/61) × 100 ≈ 52/100.

**Observed: 78/100 top-Ω-only pairs involve a PDF target.**
Enrichment: 78/52 ≈ 1.5×.

This is a modest enrichment. The PDF targets (URY, URX, OLQ, I1, FLP, OLL, RMEL, RMER)
are a large fraction of the 61-neuron subgraph and naturally appear in many pairs.

### D_emp Hub Structure

Top-5 D_emp hubs (by off-diagonal Frobenius energy):
URBL, IL2VL, AWCL, AUAL, OLQVR.

Fraction of top-100 Ω-only pairs involving a top-5 hub: **15/100**.
Expected if random: 2 × (5/61) × 100 ≈ 16/100. **No enrichment.**

The D_emp hubs by off-diagonal energy are NOT the same as the neurons driving the
AUROC improvement (RID, RMEL, RMER in Phase 3C-G/H). The AUROC improvement required
specific high-value D_emp entries connecting RID/RMEL/RMER to their ΔQ partners —
not general off-diagonal hub status.

### Shared Connectome Neighbor

Pairs (i,j) sharing at least one common connectome neighbor.

| Group | Shared-neighbor fraction |
|---|---|
| Top-100 Ω-only | 49/100 (49%) |
| Top-100 ΔQ | 46/100 (46%) |

No enrichment in shared-neighbor motifs. Ω-only pairs do not preferentially involve
neurons with common synaptic input or output.

---

## Conclusion: No Coherent Motif Structure

The motif scan finds **no coherent network motif** selectively enriched in
Ω-only pairs beyond what is explained by the D_emp imputation mechanism
(Phase 3C-G/H). The modest PDF-source enrichment (1.9×) and PDF-target enrichment
(1.5×) are consistent with the known D_emp hub structure and do not represent
new biology.

**E4 verdict**: No motif analysis is warranted. The conditional trigger (E1 or E3
showing clear signal) was not met.

---

*E4 scope: preliminary motif scan only. Full analysis not triggered.*
