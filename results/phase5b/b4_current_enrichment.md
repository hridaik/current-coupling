# Phase 5B.4 — Annotation Enrichment Under ΔΩ_ss vs ΔQ
Date: 2026-06-12

---

## Enrichment Tests

Tests run on 1321 Class-4 pairs.
Null: degree-preserving permutation (10,000 iterations), label probability ∝ deg_i + deg_j.
Two annotation sets:
- **PDF:** 61 pairs with at least one neuron expressing pdf-1 or pdfr-1 (Bentley ESconnectome)
- **Serotonin:** 33 pairs with at least one serotonin-expressing neuron (Bentley monoamines)

---

## AUROC Results

| Test | ΔΩ_ss AUROC | ΔΩ_ss p_deg | ΔQ AUROC | ΔQ p_deg | Significant? |
|------|-------------|-------------|----------|----------|--------------|
| PDF | 0.5329 | 0.196 | 0.5560 | **0.020** | **ΔQ: Yes; ΔΩ_ss: No** |
| Serotonin | 0.5112 | 0.287 | 0.5248 | 0.172 | Neither |
| Combined PDF+Ser | 0.5220 | 0.241 | 0.5404 | 0.096 | Neither |

---

## Fisher Test (Top-20)

Count of annotation-positive pairs in the top 20 by |ΔΩ_ss| vs by |ΔQ|.
Base rate: 61/1321 = 4.6% PDF, 33/1321 = 2.5% serotonin.

| Test | ΔΩ_ss top-20 | ΔQ top-20 | Fisher OR (ΔΩ_ss) | Fisher OR (ΔQ) |
|------|-------------|-----------|-------------------|----------------|
| PDF | 4/20 (20.0%) | 4/20 (20.0%) | 5.38 | 5.38 |
| Serotonin | 1/20 (5.0%) | 2/20 (10.0%) | 2.05 | 4.41 |

**Fisher count for PDF is identical (4/20) under both formulations.**
The AUROC difference (0.5329 vs 0.5560) reflects the full ranking, not just the top bin.

---

## Why ΔQ PDF AUROC Is Significant but ΔΩ_ss Is Not

The AUROC test weights all 1321 pairs by their rank under the scoring variable.
Under ΔQ, PDF-positive pairs tend to be moderately elevated throughout the ranking,
yielding AUROC = 0.556 (p_deg = 0.020 vs degree-preserving null).

Under ΔΩ_ss, pairs that are PDF-negative but high-|ΔΩ_ss| are promoted:
- CEPDR–URXL (ΔΩ rank 10, not PDF): rises 30 places from ΔQ rank 40
- AVEL–RIVL (ΔΩ rank 5, not PDF): rises 15 places
- ASEL–CEPDR (ΔΩ rank 16, not PDF): rises 69 places from ΔQ rank 85
- FLPL–OLLL (ΔΩ rank 15, not PDF): rises 15 places

These promotions dilute the PDF signal throughout the ranking, reducing AUROC to 0.533
and pushing the enrichment below significance.

The top-20 Fisher count remains 4/20 in both cases because the three ADEL-PDF pairs
(ranks 2, 4, 6 under ΔΩ_ss) are promoted into the top-10, compensating for RMEL–URYDL
exiting the top-20 (replaced by AVDL–URYDL, also PDF-positive, at rank 20).

---

## Funatlas (Randi) Enrichment

Randi-annotated pairs: 91 of 1321 Class-4 pairs have funatlas wt observations (q available).
Test: is high |ΔΩ_ss| enriched for funatlas-confirmed interactions (q < 0.05)?

| Metric | ΔΩ_ss | ΔQ |
|--------|-------|----|
| Randi AUROC (any q < 0.05) | 0.508 | 0.515 |
| Randi AUROC (q < 0.01) | 0.512 | 0.518 |
| Top-20 Randi confirmed | 1 (CEPDR-URXL) | 1 (RMEL-RMER) |

Neither formulation shows strong Randi enrichment. The funatlas coverage (91/1321 = 6.9%
of Class-4 pairs have any data) is too sparse for robust AUROC. The confirmed pairs are
different (CEPDR–URXL is the highest ΔΩ_ss Randi-confirmed pair vs RMEL–RMER under ΔQ).

---

## Summary

| Enrichment | ΔΩ_ss result | ΔQ result | Change |
|-----------|-------------|----------|--------|
| PDF AUROC | 0.533, p=0.196 | 0.556, p=0.020 | **Lost significance** |
| Fisher top-20 (PDF) | 4/20 | 4/20 | Identical |
| Serotonin | Not significant | Not significant | Unchanged |
| Funatlas | Marginal (0.508) | Marginal (0.515) | Minimal change |

**The most consequential finding: PDF enrichment loses statistical significance under ΔΩ_ss.**
The core biological result (PDF circuit as the dominant annotatable pattern) is still present
in the top-20 (4 PDF pairs in both top-20 lists), but the framework-level enrichment that
motivated the PDF hypothesis (Phase 2 Stage 4A) is weaker under the current formulation.

This does not invalidate the PDF hypothesis: the ADEL-PDF pairs are promoted to the top of
the list under ΔΩ_ss. But the global AUROC signal is attenuated because non-PDF pairs also
rise strongly, diluting the enrichment across the full ranking.
