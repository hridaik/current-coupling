# Phase 8B Metric Report

**Condition**: oracle_z  
**Date**: 2026-06-13  
**Generated from**: `results/phase8b/metrics/metrics_oracle_z.json`

---

## Primary Metrics (governance: PRIMARY)

| Metric | Value |
|--------|-------|
| MacroAUROC (M6) | 0.5385 |
| C-AUROC (M1-C) | 0.4484 |
| LR-AUROC (M10) | 0.4197 |

### 95% Bootstrap Confidence Intervals (N_boot=2000, seed=8888)

| Metric | Lower | Upper | Width |
|--------|-------|-------|-------|
| MacroAUROC | 0.5255 | 0.5522 | 0.0267 |
| C-AUROC | 0.4284 | 0.4676 | 0.0392 |
| LR-AUROC | 0.3994 | 0.4387 | 0.0393 |

---

## Per-Class AUROC (governance: SECONDARY)

| Class | AUROC | n(class) |
|-------|-------|----------|
| S | 0.8531 | 497 |
| C | 0.4484 | 857 |
| M | 0.1561 | 89 |
| N | 0.6963 | 8457 |
| LR (C+M) | 0.4197 | 946 |
| Direct (S+M) | 0.8585 | 586 |

**MacroAUROC = mean(S,C,M,N) = (0.8531+0.4484+0.1561+0.6963)/4 = 0.5385**  
**WeightedAUROC = Σ n(k)/N × AUROC(k) = 0.6779**

---

## AUPRC and Lift (governance: SECONDARY)

| Class | AUPRC | Baseline (class freq) | Lift |
|-------|-------|----------------------|------|
| S | 0.3205 | 0.0502 | 6.383 |
| C | 0.0756 | 0.0866 | 0.873 |
| M | 0.0058 | 0.0090 | 0.645 |
| N | 0.9158 | 0.8543 | 1.072 |

---

## F1 / Precision / Recall at Optimal Threshold (governance: SECONDARY)

| Class | F1 | Precision | Recall | Threshold |
|-------|----|-----------|--------|-----------|
| S | 0.4212 | 0.3712 | 0.4869 | 0.3187 |
| C | 0.1607 | 0.0877 | 0.9615 | 0.2214 |
| M | 0.0196 | 0.0769 | 0.0112 | 0.2523 |
| N | 0.9226 | 0.8649 | 0.9886 | 0.2015 |

---

## Balanced Accuracy (governance: SECONDARY)

0.2531

---

## Confusion Matrix (governance: SECONDARY)

Rows = true class, columns = predicted class. Order: S, C, M, N.

|       | Pred S | Pred C | Pred M | Pred N |
|-------|--------|--------|--------|--------|
| True S | 495 | 2 | 0 | 0 |
| True C | 843 | 14 | 0 | 0 |
| True M | 89 | 0 | 0 | 0 |
| True N | 8185 | 272 | 0 | 0 |

**Note**: The framework predicts only S (9612) and C (288). M and N are never predicted. The confusion pattern reveals the framework correctly ranks S-type pairs highly but maps almost all pairs to the S/C space, missing M and N discrimination entirely.

---

## Brier Score (governance: EXPLORATORY)

| Class | Brier Score | Baseline (freq×(1-freq)) | Skill |
|-------|-------------|--------------------------|-------|
| S | 0.0916 | 0.0476 | -0.921 |
| C | 0.1037 | 0.0793 | -0.312 |
| M | 0.0645 | 0.0090 | -6.242 |
| N | 0.4973 | 0.1241 | -2.994 |

All Brier skill scores are negative — the framework is worse than the no-skill baseline on all classes.

---

## Expected Calibration Error (governance: EXPLORATORY)

ECE = 0.2207

---

## Top-K Precision (governance: EXPLORATORY)

### Class C

| K | Top-K Precision | Enrichment vs random |
|---|----------------|---------------------|
| 50 | 0.000 | 0.000 |
| 100 | 0.030 | 0.347 |
| 200 | 0.065 | 0.751 |
| 500 | 0.070 | 0.809 |

### LR (C+M combined)

| K | Top-K Precision | Enrichment vs random |
|---|----------------|---------------------|
| 50 | 0.060 | 0.628 |
| 100 | 0.070 | 0.733 |
| 200 | 0.070 | 0.733 |
| 500 | 0.074 | 0.774 |

Top-50 enrichment for LR is 0.63 (below 1.0) — the framework's top-50 highest-scored pairs contain fewer LR pairs than a random draw.
