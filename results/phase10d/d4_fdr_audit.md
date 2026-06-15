# Phase 10D.4 — FDR Audit
Date: 2026-06-15

## Overview

Benjamini-Hochberg (BH) FDR correction applied across ALL annotation × K combinations.
Total tests: 70 (7 annotations × 10 K values).
FDR threshold: q < 0.05.

**Significant at BH q<0.05: 3 of 70 tests.**

## Top-20 Tests by Nominal p-Value

| Annotation | Type | K | top-K count | OR | p (Fisher) | BH rank | BH threshold | BH sig? |
|-----------|------|---|------------|-----|-----------|---------|------------|--------|
| Bentley_PDF | primary | 50 | 9 | 4.53 | 0.0003 | 1 | 0.0007 | ✓ |
| Bentley_PDF | primary | 40 | 8 | 5.16 | 0.0003 | 2 | 0.0014 | ✓ |
| Bentley_PDF | primary | 30 | 6 | 5.16 | 0.0019 | 3 | 0.0021 | ✓ |
| Bentley_PDF | primary | 100 | 11 | 2.55 | 0.0046 | 4 | 0.0029 | — |
| Bentley_PDF | primary | 25 | 5 | 5.16 | 0.0046 | 5 | 0.0036 | — |
| Bentley_ser_or_PDF | primary | 40 | 8 | 3.26 | 0.0056 | 6 | 0.0043 | — |
| Bentley_PDF | primary | 75 | 9 | 2.82 | 0.0059 | 7 | 0.0050 | — |
| Bentley_ser_or_PDF | primary | 50 | 9 | 2.87 | 0.0069 | 8 | 0.0057 | — |
| Bentley_PDF | primary | 10 | 3 | 8.85 | 0.0089 | 9 | 0.0064 | — |
| Bentley_PDF | primary | 20 | 4 | 5.16 | 0.0114 | 10 | 0.0071 | — |
| Bentley_ser_or_PDF | primary | 30 | 6 | 3.26 | 0.0163 | 11 | 0.0079 | — |
| Bentley_PDF | primary | 5 | 2 | 13.77 | 0.0192 | 12 | 0.0086 | — |
| Bentley_ser_or_PDF | primary | 25 | 5 | 3.26 | 0.0279 | 13 | 0.0093 | — |
| Bentley_PDF | primary | 15 | 3 | 5.16 | 0.0287 | 14 | 0.0100 | — |
| Bentley_ser_or_PDF | primary | 10 | 3 | 5.59 | 0.0290 | 15 | 0.0107 | — |
| Bentley_ser_or_PDF | primary | 5 | 2 | 8.70 | 0.0435 | 16 | 0.0114 | — |
| Bentley_ser_or_PDF | primary | 100 | 12 | 1.78 | 0.0451 | 17 | 0.0121 | — |
| Bentley_ser_or_PDF | primary | 20 | 4 | 3.26 | 0.0482 | 18 | 0.0129 | — |
| Bentley_ser_or_PDF | primary | 75 | 9 | 1.78 | 0.0785 | 19 | 0.0136 | — |
| Bentley_ser_or_PDF | primary | 15 | 3 | 3.26 | 0.0850 | 20 | 0.0143 | — |


## Summary by Annotation (K=20)

| Annotation | n | OR | p_Fisher | BH significant? |
|-----------|---|-----|----------|----------------|
| Bentley_PDF | [False  True False ... False False False] | 5.16 | 0.0114 | — no |
| Bentley_ser_or_PDF | [False  True False ... False False False] | 3.26 | 0.0482 | — no |
| Combined_neuromod | [ True  True False ...  True  True False] | 1.80 | 0.2500 | — no |
| Randi_Funatlas | [False False False ...  True False False] | 0.82 | 0.7078 | — no |
| Neuropeptide_Ripoll | [ True False False ...  True  True False] | 0.84 | 0.7404 | — no |
| Bentley_serotonin | [False False False ... False False False] | 0.00 | 1.0000 | — no |
| CeNGEN_ser_or_PDF | [False False False ... False False False] | nan | 1.0000 | — no |


## Key Findings

- **Bentley_PDF at K=20**: p=0.0114 —
  NOT BH-significant after correction for {m} tests.

- The PDF signal at several K values may not survive multi-test correction across all
  annotation × K combinations. This does NOT invalidate the primary Stage 4A finding,
  which was a single pre-specified test (K=20, Bentley_PDF).

- PROHIBITION: Do NOT describe any annotation × K combination as "FDR-controlled"
  unless it passes BH correction here.

## Interpretation of BH Scope

The BH correction here is applied to the SENSITIVITY SWEEP (Phase 10D), which tests
70 combinations that were not all pre-specified. The original Stage 4A test (K=20,
Bentley_PDF, single test) remains the primary result. The BH analysis here shows
which, if any, sweep results would survive multiple-testing correction.
