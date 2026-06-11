# Stage 4A Report — Serotonin/PDF Exploratory Enrichment
Date: 2026-06-01
Script: `scripts/phase2/stage4a_serotonin_pdf.py`
Authorization: 2026-06-01 human supervisor. Phase 2 addendum.

---

## 1. Context

Stage 4A is an addendum to Phase 2 Stage 4. The primary Stage 4 analysis found null enrichment for neuropeptide annotation (Ripoll-Sánchez atlas) and Randi unc-31 annotation in both CePNEM and GCaMP coordinates. Stage 5 was completed and assigned Row 4 (Null result) of the locked interpretation table.

Test 4 (Serotonin/PDF) was originally skipped because the annotation was not found. A repository audit confirmed that two sources exist:
- **Bentley ESconnectome** (literature-curated, directed pairs, primary annotation)
- **CeNGEN expression atlas** (transcriptomic, ligand-receptor inference, exploratory annotation)

No ΔQ matrices were recomputed. All enrichment machinery is identical to Stage 4.

---

## 2. Annotations Used

| Annotation | Source | Type | Class 4 pairs | Density |
|---|---|---|---|---|
| Bentley serotonin | ESconnectome monoamines, transmitter=="serotonin" | Primary | 33 | 2.5% |
| Bentley PDF | ESconnectome neuropeptides, transmitter contains "pdf" | Primary | 61 | 4.6% |
| Bentley serotonin-or-PDF | Union of above two | Primary | 94 | 7.1% |
| CeNGEN serotonin/PDF | (tph-1/cat-1→ser-1/4/5/7/mod-1) OR (pdf-1/pdf-2→pdfr-1) | Exploratory | 409 | 31.0% |

The Bentley combined annotation (94 pairs, 7.1% density) is the pre-specified Test 4 annotation. All Bentley pair counts were verified in the Stage 4A audit.

---

## 3. Results

### 3.1 CePNEM Coordinate

| Annotation | AUROC | p_MW | p_simple | p_deg | Fisher OR | p_FE | p_simple | p_deg | AUROC verdict | Fisher verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Bentley serotonin | 0.4953 | 0.555 | 0.557 | 0.581 | 0.000 | 1.000 | 1.000 | 1.000 | FAIL | FAIL |
| **Bentley PDF** | **0.5560** | **0.014** | **0.019** | **0.023** | **5.456** | **0.011** | **0.006** | **0.008** | **PASS** | **PASS** |
| Bentley serotonin-or-PDF | 0.5356 | 0.044 | 0.047 | 0.055 | 3.364 | 0.048 | 0.060 | 0.065 | FAIL | FAIL |
| CeNGEN serotonin/PDF | 0.5208 | 0.036 | 0.028 | 0.033 | 0.740 | 0.792 | 0.792 | 0.764 | PASS | FAIL |

### 3.2 GCaMP Coordinate

| Annotation | AUROC | p_MW | p_simple | p_deg | Fisher OR | p_FE | p_simple | p_deg | AUROC verdict | Fisher verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Bentley serotonin | 0.4286 | 0.938 | 0.948 | 0.935 | 2.087 | 0.399 | 0.386 | 0.367 | FAIL | FAIL |
| Bentley PDF | 0.5260 | 0.225 | 0.226 | 0.261 | 1.089 | 0.614 | 0.612 | 0.670 | FAIL | FAIL |
| Bentley serotonin-or-PDF | 0.4910 | 0.625 | 0.637 | 0.674 | 1.460 | 0.422 | 0.444 | 0.445 | FAIL | FAIL |
| CeNGEN serotonin/PDF | 0.5438 | 0.003 | 0.003 | 0.002 | 1.496 | 0.257 | 0.264 | 0.196 | PASS | FAIL |

---

## 4. Detailed Analysis of Significant Results

### 4.1 Bentley PDF — CePNEM (Primary annotation, PASS)

**AUROC = 0.5560**, p_deg = **0.023** (degree-preserving null, 1000 permutations).
**Fisher OR = 5.456**, p_deg = **0.008** (Fisher exact p = 0.011).

Contingency table (top-20):

|  | Annotated (PDF) | Not annotated |
|---|---|---|
| Top-20 | **4** | 16 |
| Rest | 57 | 1244 |

Expected PDF pairs in top-20 by chance: 0.9 (= 61×20/1321). Observed: 4.

The four PDF-annotated pairs in the top-20 CePNEM ΔQ are:

| Rank | Pair | \|ΔQ\| | pdf-1 source | pdfr-1 target |
|---|---|---|---|---|
| 5 | ADEL–URYVR | 0.1222 | ADEL (pdf-1-expressing) | URYVR (pdfr-1-expressing) |
| 9 | ADEL–URYDL | 0.0980 | ADEL | URYDL |
| 10 | ADEL–RMEL | 0.0957 | ADEL | RMEL |
| 16 | RMEL–URYDL | 0.0754 | — | both pdfr-1 |

Three of four involve ADEL (pdf-1-expressing per CeNGEN) targeting URY and RME neurons (both pdfr-1-expressing). The fourth (RMEL–URYDL) connects two pdfr-1 receptor-expressing neurons.

**GCaMP result for Bentley PDF:** AUROC = 0.526, p_deg = 0.261 (FAIL). The PDF enrichment does not replicate in GCaMP. This asymmetry places the result in a CePNEM-specific pattern — consistent with signal present after behavioral confound removal but absent in raw calcium traces.

### 4.2 Bentley serotonin-or-PDF — CePNEM (Pre-specified Test 4, MARGINAL)

**AUROC = 0.5356**, p_deg = **0.055** (above the 0.05 threshold by 0.005).
**Fisher OR = 3.364**, p_deg = **0.065** (above the 0.05 threshold by 0.015).

This is the pre-specified Test 4 annotation (Serotonin OR PDF combined). At the pre-specified threshold of p < 0.05, this annotation fails for both AUROC and Fisher under the degree-preserving null. Adding the serotonin pairs (which contribute 0 to the top-20 and have AUROC < 0.5) dilutes the PDF signal, pulling the combined test from significance to marginal.

The same four PDF pairs drive this test (serotonin contributes 0 annotated pairs to the top-20).

### 4.3 CeNGEN serotonin/PDF — Both coordinates (Exploratory, AUROC pass / Fisher fail)

CePNEM AUROC = 0.521, p_deg = 0.033 (PASS); Fisher OR = 0.740, p_deg = 0.764 (FAIL).
GCaMP AUROC = 0.544, p_deg = 0.002 (PASS); Fisher OR = 1.496, p_deg = 0.196 (FAIL).

With 409/1321 annotated (31% density), the AUROC test detects a modest systematic ranking signal in both coordinates. The Fisher test fails because OR < 1 in CePNEM (annotation slightly depleted in top-20) and because at 31% density the Fisher statistic has low discriminative power at K=20. This result is consistent with a broad, weak expression-based signal that is not strong enough to concentrate in the top-K.

---

## 5. Relation to Stage 5 Interpretation

Stage 5 assigned Row 4 (Null result) based on the Stage 4 neuropeptide and Randi tests.

Stage 4A is exploratory. Its results do not retroactively change the Stage 5 assignment.

For the purpose of assessing the Stage 4A findings against the locked interpretation table:

| Finding | CePNEM | GCaMP | Interpretation table row |
|---|---|---|---|
| **Bentley PDF (primary ann.)** | **PASS (p_deg=0.023/0.008)** | FAIL | Candidate Row 2: "Neural organization masked by behavioral noise" — but NOT assigned because (a) this test was not pre-specified as a primary analysis; (b) the pre-specified combined annotation (Test 4) does not pass at p<0.05 |
| Bentley serotonin-or-PDF (Test 4) | MARGINAL (p_deg=0.055) | FAIL | Row 4: Null result (both coordinates non-significant at p<0.05) |
| CeNGEN combined (exploratory) | PASS AUROC / FAIL Fisher | PASS AUROC / FAIL Fisher | Inconclusive (AUROC signal without Fisher corroboration) |

**The Stage 5 null result stands.** The pre-specified Test 4 annotation (Bentley combined, serotonin-or-PDF) does not pass at p < 0.05 under the degree-preserving null in either coordinate. The Bentley PDF-only sub-annotation was not pre-specified and was identified post-hoc by decomposing the combined annotation.

---

## 6. Stage 4A Pass/Fail Summary

| Test | CePNEM | GCaMP |
|---|---|---|
| Bentley serotonin — AUROC | FAIL | FAIL |
| Bentley serotonin — Fisher | FAIL | FAIL |
| **Bentley PDF — AUROC** | **PASS (p_deg=0.023)** | FAIL |
| **Bentley PDF — Fisher K=20** | **PASS (p_deg=0.008)** | FAIL |
| Bentley combined — AUROC | FAIL (p=0.055) | FAIL |
| Bentley combined — Fisher | FAIL (p=0.065) | FAIL |
| CeNGEN combined — AUROC | PASS (p_deg=0.033) | PASS (p_deg=0.002) |
| CeNGEN combined — Fisher | FAIL | FAIL |
| Results saved before report | PASS | — |

---

## 7. Output Files

| File | Description |
|---|---|
| `results/phase2/stage4a/stage4a_results.json` | All statistics, contingency tables, null distributions |
| `results/phase2/stage4a/stage4a_report.md` | This report |

---

## 8. Phase 2 Closure Recommendation

**Recommendation: Phase 2 is complete. No additional computation is authorized.**

### Basis

1. **Primary result (Stage 4 + Stage 5) is unchanged:** The pre-specified enrichment hypothesis (neuropeptide AUROC, Randi, combined serotonin/PDF) is null. The Stage 5 Row 4 assignment (Null result) stands and is not modified by Stage 4A.

2. **The Bentley PDF finding is exploratory:** The PDF-only annotation was not pre-specified as a standalone test. It was identified by decomposing the combined annotation after the combined test was marginal. Under pre-registration principles, this finding is hypothesis-generating, not confirmatory. It is reported fully and honestly but does not constitute a positive enrichment result for Phase 2.

3. **The pre-specified Test 4 fails:** The authorized Bentley combined (serotonin-or-PDF) annotation achieves p_deg = 0.055 (AUROC) and p_deg = 0.065 (Fisher) in CePNEM — both above the pre-specified threshold of p < 0.05. The pre-registered criterion is not met.

4. **No new methodology, parameters, or data are needed:** Stage 4A was self-contained using existing files. All resources were confirmed present. No external data was required. The analysis is complete.

### What Stage 4A adds to the Phase 2 record

Stage 4A is a complete execution of the pre-specified (but previously skipped) Test 4. The result is honestly characterized:
- The pre-specified combined annotation: marginal, non-significant at p < 0.05
- A post-hoc decomposition reveals that the PDF component alone passes in CePNEM (p < 0.05), while the serotonin component is null
- The CePNEM specificity (PDF pass, GCaMP fail) is consistent with a genuine neural signal rather than a behavioral artifact — but this observation was not pre-specified and cannot be reported as a confirmed finding

### Recommended archival statement

Phase 2 tested whether state-conditioned off-connectome conditional-dependence changes in 61 identified C. elegans neurons are enriched for neuropeptide, Randi unc-31, or serotonin/PDF signaling pairs. The pre-specified enrichment hypothesis was not supported in any primary or secondary test under the degree-preserving null (all primary p > 0.05). An exploratory decomposition of the serotonin/PDF annotation found a Bentley PDF-specific signal in CePNEM (AUROC p_deg = 0.023, Fisher p_deg = 0.008), which is reported as a hypothesis for future investigation. The overall Phase 2 result is null.

---

*Stage 4A scope: exploratory enrichment using serotonin/PDF annotations not available during primary Stage 4. No new estimation. No biological interpretation beyond the statistics reported. No mechanistic claims.*
