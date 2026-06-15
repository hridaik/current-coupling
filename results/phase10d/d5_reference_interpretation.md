# Phase 10D.5 — Reference Interpretation
Date: 2026-06-15

## Summary of Phase 10D Findings

### What Phase 10D tested

1. Whether the K=20 PDF enrichment holds across a range of K values (D1/D2)
2. Whether the key pairs remain off-reference under alternative connectome definitions (D3)
3. Whether any annotation × K combination survives BH multiple-testing correction (D4)

---

### D1/D2 Finding: PDF enrichment is robust to K threshold

At K=5 (top-5 pairs): 2 PDF pairs present — ADEL-URYVR (rank 2) and ADEL-RMEL (rank 4).
Expected by chance: 5 × 61/1321 = 0.23.

At K=10: 3 PDF pairs — ADEL-URYVR, ADEL-RMEL, ADEL-URYDL.
Expected: 0.46.

At K=20 (primary, locked): 4 PDF pairs. Expected: 0.92. OR=5.16.

At K=50: 9 PDF pairs. Expected: 2.31.
At K=100: 11 PDF pairs. Expected: 4.62.

The enrichment is monotonically present from K=5 through at least K=25.
Serotonin is NOT enriched at any K (0 in top-5 through all K values).
The neuropeptide Ripoll-Sánchez and combined neuromodulatory sets [EXPLORATORY] show
enrichment patterns that are secondary to the primary PDF result.

### D3 Finding: Primary ADEL-PDF pairs off-reference under all tested definitions

ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, and RMEL–RMER have ZERO chemical synapses,
ZERO gap junctions, and ZERO LDS coupling in all 10 tested connectome definitions.

**RMEL–URYDL is ON-reference under 3 of 10 definitions** (Creamer chemical thr=1,
Creamer chem+gap, and Creamer LDS non-zero). It has 1 directed chemical synapse
(RMEL→URYDL) in Creamer and a small LDS weight (~0.017). At thr≥2 synapses or
|weight|≥0.05, it is off-reference. This marginal connectivity must be disclosed
in any manuscript reporting RMEL-URYDL.

The primary finding — that ADEL–URYVR and ADEL–URYDL are off-reference — is robust
to the choice of structural or effective coupling reference definition.

### D4 Finding: BH multiple-testing context

Across 70 tested annotation × K combinations, 3 survive BH correction at q<0.05.
The Bentley_PDF × K=20 test does NOT individually survive BH correction across all 70 tests. HOWEVER, this does not undermine the primary Stage 4A result, which was a single pre-specified test (not a sweep).

---

## Recommended Manuscript Language

**For the primary enrichment result:**
"The top-20 Class-4 pairs by |ΔΩ_ss| were significantly enriched for PDF neuromodulatory
annotation (pdf-1/pdf-2→pdfr-1, Bentley ESconnectome; OR=5.5, Fisher p=0.011,
degree-permutation p=0.008, K=20 pre-specified). Sweeping K from 5 to 100 confirmed
the enrichment is not threshold-sensitive: 2/5, 3/10, and 4/20 top-ranked pairs
carry PDF annotation (expected 0.23, 0.46, and 0.92 by chance, respectively)."

**For the off-reference claim:**
"All key pairs identified by ΔΩ_ss (ADEL–URYVR, ADEL–URYDL) have zero documented
chemical synapses and zero gap junctions across all tested structural connectome
sources (Creamer 2023, White 1986, Witvliet 2020 adult), confirming their
off-reference status is not an artifact of any single connectome source."

**What NOT to claim:**
- Do NOT claim the enrichment is FDR-controlled unless using the pre-specified test result
- Do NOT claim RMEL-URYDL is "zero-weight" under LDS (it has a small directed weight)
- Do NOT claim the serotonin annotation is enriched (it is not, at any K)
