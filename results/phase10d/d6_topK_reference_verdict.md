# Phase 10D.6 — Top-K and Reference Verdict
Date: 2026-06-15

---

## Q1: Is the K=20 PDF enrichment specific to the choice of K=20?

**NO. The PDF enrichment is robust across K values.**

| K | PDF count | Expected | OR | p_Fisher |
|---|-----------|----------|-----|----------|
| 5 | 2 | 0.23 | 13.77 | 0.0192 |
| 10 | 3 | 0.46 | 8.85 | 0.0089 |
| 15 | 3 | 0.69 | 5.16 | 0.0287 |
| 20 | 4 | 0.92 | 5.16 | 0.0114 |
| 25 | 5 | 1.15 | 5.16 | 0.0046 |
| 30 | 6 | 1.39 | 5.16 | 0.0019 |
| 40 | 8 | 1.85 | 5.16 | 0.0003 |
| 50 | 9 | 2.31 | 4.53 | 0.0003 |
| 75 | 9 | 3.46 | 2.82 | 0.0059 |
| 100 | 11 | 4.62 | 2.55 | 0.0046 |


PDF pairs appear in top-5, top-10, top-20, and remain elevated through top-50.
The enrichment holds at the k values closest to the annotation density (61/1321 = 4.6%
of C4 pairs are PDF-annotated, meaning ≥2 expected at K≥43).

**Verdict: PDF enrichment is K-threshold robust.**

---

## Q2: Do key pairs remain in top-K across alternative K values?

**YES.**

- ADEL–URYVR (rank 2): in top-K for ALL K ∈ [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
- ADEL–RMEL (rank 4): in top-K for ALL K ∈ [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
- ADEL–URYDL (rank 6): in top-K for K ≥ 10 (all K except K=5)
- RMEL–URYDL (rank 23): in top-K for K ≥ 25
- RMEL–RMER (rank 38): in top-K for K ≥ 40

**Verdict: Key pair top-K membership is stable.**

---

## Q3: Are key pairs off-reference under alternative connectome definitions?

**ADEL–URYVR and ADEL–URYDL (primary claims): YES — off-reference under ALL 10 definitions.**

**RMEL–URYDL: MIXED — ON-reference under 3 of 10 definitions.**
- Creamer chemical thr=1: ON-reference (1 directed synapse RMEL→URYDL)
- Creamer chem or gap: ON-reference (same 1 synapse)
- Creamer LDS non-zero: ON-reference (directed weight ≈ 0.017)
- At thr≥2 synapses or |weight|≥0.05: off-reference in all tested definitions

ADEL–RMEL and RMEL–RMER: off-reference under ALL 10 definitions.

**Verdict for primary PDF pairs (ADEL-URYVR, ADEL-URYDL): Off-reference status universally robust.**
**Verdict for RMEL-URYDL: Borderline — marginal Creamer connectivity exists; requires disclosure.**

---

## Q4: Is the PDF enrichment FDR-controlled?

**MIXED — depends on scope.**

The Bentley_PDF × K=20 test (primary, pre-specified) does NOT survive BH correction
when tested alongside all 70 annotation × K sweep combinations. This does not
undermine the primary Stage 4A result (single pre-specified test, not a sweep).

However, Bentley_PDF DOES pass BH correction at K=30, 40, and 50 — three of the
tested K values survive FDR control across the 70-test sweep (see D4).

**Primary claim (K=20, pre-specified in Stage 4A)**: significant as a single test;
not BH-significant within the sweep of 70.
**K=30,40,50**: BH-significant within the sweep; these are confirmation only (K=20 was locked).

PROHIBITION: Do NOT claim the K-sweep results are FDR-controlled unless they pass
BH correction in the D4 audit.

---

## Q5: Is the serotonin annotation enriched?

**NO.**

Serotonin (n=33 C4 pairs) shows 0 pairs in top-20 at K=20 and remains depleted
at all K values tested. This contrasts sharply with PDF.

The AUROC for serotonin under ΔΩ_ss is ~0.495 (essentially chance).

---

## Per-Claim Grades (Phase 10D)

| Claim | D1/D2 grade | D3 grade | D4 grade | Overall |
|-------|------------|---------|---------|---------|
| PDF top-20 enrichment | **A** — robust to K | N/A | BH-sig at K=30,40,50 | **A — Robust** |
| ADEL-URYVR/URYDL off-reference | N/A | **A** — all 10 refs | N/A | **A — Robust** |
| RMEL-URYDL off-reference | N/A | **B** — ON-ref in Creamer chem thr1 | N/A | **B — Disclose** |
| ADEL-RMEL / RMEL-RMER off-reference | N/A | **A** — all 10 refs | N/A | **A — Robust** |
| Serotonin enrichment | **D** — not enriched | N/A | N/A | **D — Absent** |
| Neuropeptide [EXPLORATORY] | See D1 | N/A | See D4 | Exploratory only |

---

## STOP Signal

Phase 10D is complete. All 12 required files have been written to results/phase10d/.
Awaiting human review.
