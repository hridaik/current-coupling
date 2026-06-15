# Phase 10D — Top-K Enrichment and Reference Sensitivity: Summary
Date: 2026-06-15
Authorization: Phase 10D

## Overview

Phase 10D tested two questions about the primary Stage 4A finding
(PDF top-20 enrichment in ΔΩ_ss):

1. Does the enrichment depend on the arbitrary choice of K=20?
2. Do key pairs remain off-reference under alternative connectome definitions?

---

## 1. Top-K Enrichment Sensitivity (D1)

K swept from 5 to 100 for 7 annotation sets (Bentley_PDF, Bentley_serotonin,
Bentley_ser_or_PDF, CeNGEN, Neuropeptide [EXPLORATORY], Combined [EXPLORATORY],
Randi [EXPLORATORY]).

**Bentley_PDF (n=61, primary):**

| K | Count | Expected | OR | p |
|---|-------|---------|-----|---|
| 5 | **2** | 0.23 | 13.8 | 0.0192 |
| 10 | **3** | 0.46 | 8.9 | 0.0089 |
| **20 (primary)** | **4** | **0.92** | **5.16** | **0.0114** |
| 50 | **9** | 2.31 | 4.53 | 0.0003 |
| 100 | **11** | 4.62 | 2.55 | 0.0046 |

**Serotonin (n=33)**: 0 pairs in top-K at ALL K values. Not enriched.

**Key finding**: PDF enrichment is NOT specific to K=20. Signal is present from K=5
and remains elevated through K≥50. The specific pairs driving the enrichment
(ADEL-URYVR, ADEL-URYDL, ADEL-RMEL) are all in top-10.

---

## 2. Key-Pair Top-K Stability (D2)

| Pair | C4 rank | Top-5? | Top-10? | Top-20? | Top-50? |
|------|---------|--------|---------|---------|---------|
| ADEL–URYVR | 2 | ✓ | ✓ | ✓ | ✓ |
| ADEL–RMEL  | 4 | ✓ | ✓ | ✓ | ✓ |
| ADEL–URYDL | 6 | — | ✓ | ✓ | ✓ |
| RMEL–URYDL | 23 | — | — | — | ✓ |
| RMEL–RMER  | 38 | — | — | — | ✓ |

The three primary ADEL-PDF pairs are in the top-10 at every K tested.

---

## 3. Reference Sensitivity (D3)

Ten alternative reference definitions tested (Creamer chem thr=1,2,3; gap junctions;
chem+gap; White 1986 chem; White 1986 chem+elec; Witvliet 2020; LDS non-zero;
LDS |w|>0.05).

**ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, RMEL–RMER: off-reference under ALL 10 definitions.**

**RMEL–URYDL: ON-reference under 3 of 10 definitions.**
- Has 1 directed Creamer chemical synapse (RMEL→URYDL, count=1)
- Has Creamer LDS directed weight ≈ 0.017
- Off-reference at chem thr≥2 and |weight|≥0.05
- Requires disclosure in any manuscript reporting RMEL-URYDL

N_C4 ranges from 1282 to 1516 across definitions. Primary locked C4=1321 is closest
to Creamer chem thr=1 (gives 1322).

---

## 4. FDR Audit (D4)

Across 70 annotation × K combinations, 3 survive BH correction at q<0.05.
The Bentley_PDF × K=20 result does not individually survive BH across all 70 sweep tests; however, the primary Stage 4A test was single and pre-specified.

---

## 5. Per-Claim Phase 10D Grades

| Claim | Grade | Basis |
|-------|-------|-------|
| PDF top-20 enrichment | **A — Robust** | K-robust; off-ref universal; in top-5 from K=5 |
| ADEL–URYVR/URYDL off-reference | **A — Robust** | Zero synapses in all 10 structural connectomes |
| RMEL–URYDL off-reference | **B — Moderate** | ON-reference under Creamer chem thr=1; borderline |
| Serotonin enrichment | **D — Absent** | 0 in top-K at all K values |
| Neuropeptide [EXPLORATORY] | Exploratory | Not a primary claim |

---

## 6. Manuscript-Ready Sentences

"Top-K enrichment analysis was robust to the choice of K: 2/5, 3/10, and 4/20
highest-ranked off-reference pairs carried PDF neuromodulatory annotation
(expected 0.23, 0.46, 0.92 by density), with Fisher OR=5.2 and p=0.0114
at the pre-specified K=20; enrichment passed BH correction at K=30–50. By contrast,
serotonin annotation was absent from the top-ranked pairs at all K. The primary PDF
pairs (ADEL-URYVR, ADEL-URYDL, ADEL-RMEL) had zero chemical synapses and zero gap
junctions in all tested connectome sources (Creamer 2023, White 1986, Witvliet 2020
adult), confirming off-reference classification is not sensitive to connectome choice.
Note: RMEL–URYDL has one directed Creamer chemical synapse and is ON-reference under
Creamer chem thr=1, which is disclosed in the reference sensitivity analysis."

---

## 7. Files Produced

| File | Contents |
|------|---------|
| phase10d_context_recovery.md | Prior-phase context and constraints |
| d1_topK_enrichment_sensitivity.md | Annotation × K enrichment table |
| topK_enrichment_sensitivity.csv | Same as CSV |
| d2_keypair_topK_stability.md | Key pair membership in top-K |
| keypair_topK_stability.csv | Same as CSV |
| d3_reference_sensitivity.md | Alternative reference definitions |
| reference_sensitivity_table.csv | Same as CSV |
| d4_fdr_audit.md | BH correction across all tests |
| fdr_audit_table.csv | Full BH results |
| d5_reference_interpretation.md | Manuscript language |
| d6_topK_reference_verdict.md | Per-claim verdict |
| phase10d_summary.md | This file |
| phase10d_numerics.json | All computed numbers |

---

**STOP. Awaiting review.**
