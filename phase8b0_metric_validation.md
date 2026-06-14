# Phase 8B-0 Metric Validation Report

**Date**: 2026-06-13  
**Script**: `scripts/phase8/validate_metrics.py`  
**Result**: 61/61 checks PASSED

---

## Overview

All metrics M1–M14 were validated using synthetic toy examples only. No benchmark data was accessed. No framework outputs were used. All expected values were derived analytically before running.

Two bugs were found and fixed during validation:

1. **Bootstrap CI label-alignment bug** (`metrics.py:_bootstrap_one`): The original implementation used `build_binary_labels()` which regenerates the full 9900-pair grid in fixed order, while `boot_arrays['class_prob']` was in bootstrap-resampled order — a systematic misalignment. Fixed by computing aligned labels directly from the bootstrap index: `boot_true = [labels_dict.get(pairs[i], 'N') for i in idx]`.

2. **PS-2 sub-category unreachable** (`verdict.py:_determine_partial_sub`): Used `s_high = macro >= THRESHOLD_PARTIAL_MACRO_AUROC (0.60)` for sub-category routing, but the PARTIAL branch is only entered when `macro >= 0.60`, making `not s_high` always False. Fixed to `s_high = macro >= THRESHOLD_SUCCESS_MACRO_AUROC (0.70)` — the correct interpretation: "macro is in the success range." *(Fix applied in validate_verdict.py context; also corrected in production verdict.py.)*

---

## Synthetic Datasets

| Dataset | Description | Labels | Classifier |
|---------|-------------|--------|-----------|
| Perfect | All 9900 pairs, 2475 per class | Balanced S/C/M/N | P(true class)=0.97, others 0.01/3 |
| Random | All 9900 pairs, balanced | Balanced S/C/M/N | P(all classes)=0.25 |
| Inverted | All 9900 pairs, balanced | Balanced S/C/M/N | Always predicts wrong class (wrong_map: S→N, C→S, M→C, N→M) |
| LR signal | All 9900 pairs, 2475 per class | Balanced S/C/M/N | C,M pairs: P(C)=P(M)=0.47, S,N pairs: P(S)=P(N)=0.47 |

---

## Test Results

### T1: Perfect classifier — AUROC = 1.0 per class

**Analytical expectation**: A classifier that assigns P(true class)=0.97 and all others 0.01/3 is monotonically correct; every true positive outranks every negative. AUROC = 1.0 exactly.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| AUROC(S) perfect | 1.000000 | 1.000000 | PASS |
| AUROC(C) perfect | 1.000000 | 1.000000 | PASS |
| AUROC(M) perfect | 1.000000 | 1.000000 | PASS |
| AUROC(N) perfect | 1.000000 | 1.000000 | PASS |
| MacroAUROC perfect | 1.000000 | 1.000000 | PASS |

### T2: Random classifier — AUROC ≈ 0.50

**Analytical expectation**: Uniform P(k)=0.25 provides no discrimination; AUROC = 0.5 exactly for balanced datasets.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| AUROC(S) random | 0.500000 | 0.500000 | PASS |
| AUROC(C) random | 0.500000 | 0.500000 | PASS |
| AUROC(M) random | 0.500000 | 0.500000 | PASS |
| AUROC(N) random | 0.500000 | 0.500000 | PASS |
| MacroAUROC random | 0.500000 | 0.500000 | PASS |

### T3: Inverted classifier — AUROC < 0.5

**Analytical expectation**: A systematic mis-predictor has inverted ranking; AUROC < 0.5.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| AUROC(S) inverted < 0.5 | True | True | PASS |
| AUROC(C) inverted < 0.5 | True | True | PASS |
| AUROC(M) inverted < 0.5 | True | True | PASS |
| AUROC(N) inverted < 0.5 | True | True | PASS |

### T4: LR-AUROC from combined C+M signal

**Analytical expectation**: Assigning P(C)+P(M)=0.94 to true C/M pairs and 0.06 to S/N pairs gives near-perfect LR discrimination. Individual C-AUROC is degraded because C and M pairs are indistinguishable from each other.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| LR-AUROC > 0.85 | True | True | PASS |
| C-AUROC < LR-AUROC | True | True | PASS |

### T5: AUPRC random ≈ class frequency

**Analytical expectation**: For a random classifier with balanced classes (25% each), AUPRC equals the class frequency (0.25). This verifies the no-skill baseline.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| AUPRC(N) random ≈ 0.25 | 0.250000 | 0.250000 | PASS |

### T6: F1/Precision/Recall at optimal threshold — perfect classifier

**Analytical expectation**: Perfect classifier at optimal threshold achieves F1=Precision=Recall=1.0.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| F1(S,C,M,N) perfect ≈ 1.0 | 1.000000 (×4) | 1.000000 (×4) | PASS ×4 |
| Precision(S,C,M,N) perfect | 1.000000 (×4) | 1.000000 (×4) | PASS ×4 |
| Recall(S,C,M,N) perfect | 1.000000 (×4) | 1.000000 (×4) | PASS ×4 |

### T7: Balanced accuracy

**Analytical expectation**: Perfect classifier: BalAcc=1.0. Random balanced classifier: BalAcc=0.25 (predicts N always → recall for S,C,M = 0; recall for N = 1 → mean = 0.25).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BalancedAcc perfect ≈ 1.0 | 1.000000 | 1.000000 | PASS |
| BalancedAcc random ≈ 0.25 | 0.250000 | 0.250000 | PASS |

### T8: Confusion matrix

**Analytical expectation**: Perfect classifier has zero off-diagonal entries.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Off-diagonal = 0 | True | True | PASS |
| Shape (4,4) | True | True | PASS |

### T9: Brier score

**Analytical expectation**:  
- Perfect: BS(k) = (0.97-1)² × freq + (0.01/3-0)² × (1-freq) ≈ 0.0009×0.25 + 0.0000044×0.75 ≈ 0.000228 < 0.01.  
- Skill > 0.95 (very close to 1).  
- Random (P(k)=0.25, freq=0.25): BS = 0.25²×0.75 + 0.75²×0.25 = 0.046875 + 0.140625 = 0.1875.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Brier(S,C,M,N) perfect < 0.01 | True (×4) | True (×4) | PASS ×4 |
| Brier skill(S,C,M,N) perfect > 0.95 | True (×4) | True (×4) | PASS ×4 |
| Brier(S,C,M,N) random ≈ 0.1875 | 0.187500 (×4) | 0.187500 (×4) | PASS ×4 |

### T10: ECE

**Analytical expectation**:  
- Perfect: confidence ≈ 0.97, accuracy ≈ 1.0 → ECE ≈ 0.03 × (1 bin weight) < 0.10.  
- Random: confidence = 0.25 = accuracy → ECE = 0.0 exactly.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| ECE perfect < 0.10 | True | True | PASS |
| ECE random ≈ 0.0 | 0.000000 | 0.000000 | PASS |

### T11: Top-K precision

**Analytical expectation**: Perfect classifier ranks all true-C pairs at top by P(C)=0.97 > all non-C pairs (P(C)≈0.003). Top-50 C-precision = 1.0. Random: ≈0.25.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| TopK-Prec(C, K=50) perfect = 1.0 | 1.000000 | 1.000000 | PASS |
| TopK-Prec(C, K=50) random ≈ 0.25 | True | True | PASS |

### T12: Enrichment

**Analytical expectation**: Enrichment = TopK-Prec / class_frequency = 1.0 / 0.25 = 4.0 for perfect classifier.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Enrichment(C, K=50) perfect > 3.0 | True | True | PASS |

### T13: Bootstrap CI — perfect classifier

**Analytical expectation**: Every bootstrap resample of a perfect classifier also scores AUROC=1.0 (since the perfect score ordering is preserved regardless of which pairs are sampled). CI = [1.0, 1.0].

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| CI upper > 0.98 | True | True | PASS |
| CI lower > 0.98 | True | True | PASS |
| CI upper ≥ lower | True | True | PASS |

### T14: MacroAUROC = unweighted mean

**Analytical expectation**: MacroAUROC is defined as (1/4) × Σ_k AUROC(k). Verified numerically.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| MacroAUROC = mean of per-class | 1.000000 | 1.000000 | PASS |

### T15: WeightedAUROC formula

**Analytical expectation**: WeightedAUROC = Σ_k (n(k)/N) × AUROC(k) using committed class counts from config8.COMMITTED_CLASS_COUNTS.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| WeightedAUROC correct formula | 1.000000 | 1.000000 | PASS |

### T16: Determinism

**Analytical expectation**: All metric functions are deterministic given fixed inputs. Bootstrap uses fixed seed=8888.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| MacroAUROC deterministic | 1.000000 == 1.000000 | True | PASS |
| Bootstrap CI deterministic | (1.0, 1.0) == (1.0, 1.0) | True | PASS |

### T17: AUPRC lift > 1 for perfect classifier

**Analytical expectation**: AUPRC lift = AUPRC / class_frequency. Perfect classifier: AUPRC=1.0, frequency=0.25 → lift=4.0 for all classes.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| AUPRC lift(S,C,M,N) perfect > 1 | True (×4) | True (×4) | PASS ×4 |

---

## Summary

| Category | Checks | Passed | Failed |
|----------|--------|--------|--------|
| AUROC (M1, M6, M7, M10) | 13 | 13 | 0 |
| AUPRC + lift (M2) | 6 | 6 | 0 |
| F1/Precision/Recall (M3-M5) | 12 | 12 | 0 |
| Balanced accuracy (M8) | 2 | 2 | 0 |
| Confusion matrix (M9) | 2 | 2 | 0 |
| Brier score (M11) | 12 | 12 | 0 |
| ECE (M12) | 2 | 2 | 0 |
| Top-K precision + enrichment (M13-M14) | 3 | 3 | 0 |
| Bootstrap CI | 4 | 4 | 0 |
| Determinism | 2 | 2 | 0 |
| LR-AUROC composite | 3 | 3 | 0 |
| **Total** | **61** | **61** | **0** |

---

## Bugs Found

### Bug 1: Bootstrap label-alignment error (`metrics.py`)

**Location**: `_bootstrap_one()` in `scripts/phase8/metrics.py`

**Description**: The function used `build_binary_labels(boot_labels, class_k)` which generates all 9900 pairs in fixed lexicographic order and looks up `boot_labels` for each. However, `boot_labels` is a dict keyed only by the unique pairs in the bootstrap sample (~63.2% of 9900). The remaining ~36.8% of pairs get label 0 (treated as non-class-k) regardless of their true label. Simultaneously, `get_scores(boot_arrays, class_k)` returns 9900 scores in bootstrap-resampled order, not lexicographic order. The two arrays were misaligned: y_true[idx] did not correspond to y_score[idx].

**Effect**: Bootstrap CIs were computed against scrambled (label, score) pairs. On balanced datasets, AUROC might still be approximately correct by symmetry, but for real benchmark data with imbalanced classes this would produce systematically wrong CIs.

**Fix**: Replaced with direct-index computation:
```python
boot_true = [labels_dict.get(pairs[i], 'N') for i in idx]
# then y_true and boot_prob[:, k_idx] are aligned by construction
```

### Bug 2: PS-2 sub-category unreachable (`verdict.py`)

**Location**: `_determine_partial_sub()` in `scripts/phase8/verdict.py`

**Description**: Used `s_high = macro >= THRESHOLD_PARTIAL_MACRO_AUROC (0.60)`. Since `_determine_partial_sub` is only called when the PARTIAL branch fires (i.e., `macro >= 0.60` is guaranteed), `not s_high` is always False, making the PS-2 branch unreachable.

**Fix**: Changed to `s_high = macro >= THRESHOLD_SUCCESS_MACRO_AUROC (0.70)` — "macro is in the success range." PS-2 now correctly identifies cases where C-AUROC is strong (≥0.65) but overall macro has not reached the success threshold.

---

*Validation completed: 2026-06-13. No framework outputs were used. No benchmark labels were accessed.*
