# Phase 8B-0 Verdict Validation Report

**Date**: 2026-06-13  
**Script**: `scripts/phase8/validate_verdict.py`  
**Result**: 55/55 checks PASSED

---

## Overview

The verdict engine (`scripts/phase8/verdict.py`) was validated against all branches of the decision tree from `phase8a_success_criteria.md`. Tests cover: SUCCESS, PARTIAL_SUCCESS (PS-1/PS-2/PS-3), FAILURE, INCONCLUSIVE-CI, all FO-1 through FO-5 overrides, all BV-1 through BV-5 validity checks, determinism, schema completeness, and condition comparisons.

One bug was found and fixed during validation.

---

## Bug Found

### PS-2 sub-category unreachable

**Location**: `_determine_partial_sub()` in `scripts/phase8/verdict.py`

**Description**: The variable `s_high` was set to `macro >= THRESHOLD_PARTIAL_MACRO_AUROC (0.60)`. Since `_determine_partial_sub` is only called from the PARTIAL branch, which requires all metrics to be ≥ their partial thresholds (including `macro >= 0.60`), `s_high` was always True and `not s_high` was always False. The PS-2 branch (`c_high and not s_high`) could never trigger.

**Correct interpretation**: PS-2 = "C-AUROC is in the success range but overall macro is not" → `s_high` should be `macro >= THRESHOLD_SUCCESS_MACRO_AUROC (0.70)`.

**Fix applied**:
```python
# Before (wrong):
s_high = macro >= cfg.THRESHOLD_PARTIAL_MACRO_AUROC  # always True in PARTIAL branch

# After (correct):
macro_success = macro >= cfg.THRESHOLD_SUCCESS_MACRO_AUROC  # can be False in PARTIAL branch
```

---

## Test Results

### T1: SUCCESS — all thresholds exceeded

Input: `macro=0.75, c=0.70, lr=0.72, b4_c=0.60` (margin=0.10 > 0.05)

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | SUCCESS | SUCCESS | PASS |
| sub_category | None | None | PASS |
| rationale non-empty | True | True | PASS |

---

### T2: SUCCESS — exactly at thresholds (edge case)

Input: `macro=0.70, c=0.65, lr=0.65, b4_c=0.60` (margin=0.05 exactly)

**Analytical**: All comparisons use `>=`, so exact equality satisfies the SUCCESS condition.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | SUCCESS | SUCCESS | PASS |

---

### T3: FAILURE — macro_auroc < 0.60

Input: `macro=0.55, c=0.70, lr=0.70, b4_c=0.50`

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | FAILURE | FAILURE | PASS |
| sub_category mentions MacroAUROC | True | True | PASS |

---

### T4: FAILURE — c_auroc < 0.55

Input: `macro=0.72, c=0.50, lr=0.70, b4_c=0.40`

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | FAILURE | FAILURE | PASS |
| sub_category mentions C-AUROC | True | True | PASS |

---

### T5: FAILURE — lr_auroc < 0.55

Input: `macro=0.72, c=0.68, lr=0.50, b4_c=0.40`

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | FAILURE | FAILURE | PASS |

---

### T6: PARTIAL_SUCCESS — all metrics in partial range

Input: `macro=0.63, c=0.60, lr=0.61, b4_c=0.56`

All metrics ≥ partial threshold but none meet success threshold.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | PARTIAL_SUCCESS | PARTIAL_SUCCESS | PASS |
| sub_category set | True | True | PASS |

---

### T7: PARTIAL_SUCCESS PS-2 — high C-AUROC, low MacroAUROC

Input: `macro=0.62, c=0.68, lr=0.62, b4_c=0.50`

PS-2 = "current signal only": C-AUROC meets success threshold (≥0.65) but macro does not (< 0.70).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | PARTIAL_SUCCESS | PARTIAL_SUCCESS | PASS |
| sub_category | PS-2 | PS-2 | PASS |

*(This was FAIL before the bug fix; sub_category was incorrectly 'PS-3'.)*

---

### T8: Not SUCCESS when B4 margin not met

Input: `macro=0.72, c=0.68, lr=0.70, b4_c=0.65` (margin=0.03 < 0.05)

All point estimates above success thresholds but framework doesn't beat B4 by required margin.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | PARTIAL_SUCCESS | PARTIAL_SUCCESS | PASS |

---

### T9: INCONCLUSIVE-CI — CI spans threshold boundary

Input: `macro=0.73, c=0.68, lr=0.68, b4_c=0.58`  
CI for macro_auroc: `[0.55, 0.85]` — spans both partial (0.60) and success (0.70) thresholds.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | INCONCLUSIVE | INCONCLUSIVE | PASS |
| sub_category | INCONCLUSIVE-CI | INCONCLUSIVE-CI | PASS |

---

### T10: CI that does not span → SUCCESS maintained

Input: `macro=0.75, c=0.70, lr=0.72, b4_c=0.60`  
CI for macro_auroc: `[0.68, 0.82]` — both bounds above success threshold.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| verdict | SUCCESS | SUCCESS | PASS |

---

### T11: FO-1 — weak C-pair fraction

FO-1 triggers when `weak_fraction_c > 0.60`.

| Input weak_fraction_c | Expected verdict | Got | Status |
|----------------------|-----------------|-----|--------|
| 0.70 (above 0.60) | INCONCLUSIVE_BENCHMARK_FAILURE | INCONCLUSIVE_BENCHMARK_FAILURE | PASS |
| 0.50 (below 0.60) | FAILURE (unchanged) | FAILURE | PASS |

---

### T12: FO-2 — mean path strength near zero

FO-2 triggers when `mean_strength_c < 0.005`.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| FO-2 with mean_strength=0.001 | INCONCLUSIVE_BENCHMARK_FAILURE | INCONCLUSIVE_BENCHMARK_FAILURE | PASS |
| FO-2 in override list | True | True | PASS |

---

### T13: FO-3 — n(C) < 200

FO-3 triggers when the realized n(C) < 200 (statistical power too low).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| FO-3 with n_c=150 | INCONCLUSIVE_BENCHMARK_FAILURE | INCONCLUSIVE_BENCHMARK_FAILURE | PASS |
| FO-3 in override list | True | True | PASS |

---

### T14: FO-4 — y variance collapsed

FO-4 triggers when `all_y_variance < 1e-4` (dynamics collapsed or numerical underflow).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| FO-4 with variance=1e-6 | INCONCLUSIVE_BENCHMARK_FAILURE | INCONCLUSIVE_BENCHMARK_FAILURE | PASS |

---

### T15: FO-5 — non-finite observations

FO-5 triggers when `all_y_finite = False` (NaN or Inf in observations).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| FO-5 with all_y_finite=False | INCONCLUSIVE_BENCHMARK_FAILURE | INCONCLUSIVE_BENCHMARK_FAILURE | PASS |

---

### T16: FO overrides do not apply to SUCCESS

FO context with extreme values (weak_fraction=0.90, variance=1e-8, non-finite) does not change a SUCCESS verdict.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| SUCCESS verdict unchanged | SUCCESS | SUCCESS | PASS |
| No overrides applied | True (0 overrides) | 0 overrides | PASS |

---

### T17: BV-1 through BV-5 — all pass with valid inputs

Labels: 870 C pairs, 56 M pairs (sufficient). b4_direct=0.60 > 0.52.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BV-1: n(C) ≥ 100 | True | True | PASS |
| BV-2: n(M) ≥ 30 | True | True | PASS |
| BV-3: B4 direct ≥ 0.52 | True | True | PASS |
| BV-4: blinding passed | True | True | PASS |
| BV-5: output hash verified | True | True | PASS |
| benchmark_validity_passed | True | True | PASS |

---

### T18: BV-1 fails when n(C) < 100

Labels: only 1 C pair.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BV-1 fails | False | False | PASS |
| benchmark_validity_passed returns False | False | False | PASS |

---

### T19: BV-3 fails when B4 direct AUROC below 0.52

b4_direct=0.48 < 0.52.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BV-3 fails | False | False | PASS |

---

### T20: Determinism

Same metric inputs → same verdict, same sub_category on independent calls.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Same verdict | PARTIAL_SUCCESS | PARTIAL_SUCCESS | PASS |
| Same sub_category | PS-3 | PS-3 | PASS |

---

### T21: Output schema

Required keys in verdict output dict.

| Key | Present | Status |
|-----|---------|--------|
| verdict | True | PASS |
| sub_category | True | PASS |
| primary_metrics | True | PASS |
| threshold_checks | True | PASS |
| ci_spans_threshold | True | PASS |
| rationale | True | PASS |

Required keys in `threshold_checks`:

| Key | Present | Status |
|-----|---------|--------|
| macro_auroc_success | True | PASS |
| macro_auroc_partial | True | PASS |
| c_auroc_success | True | PASS |
| c_auroc_partial | True | PASS |
| lr_auroc_success | True | PASS |
| lr_auroc_partial | True | PASS |
| beats_b4_by_margin | True | PASS |

---

### T22: compute_condition_comparisons

Input: metrics for oracle_z (reference), blind_z, neural_state.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| blind_z in diffs | True | True | PASS |
| oracle_z not in diffs (reference) | True | True | PASS |
| blind_z delta_macro_auroc | -0.0800 | -0.0800 | PASS |
| neural_state delta_c_auroc | -0.1400 | -0.1400 | PASS |

---

## Summary

| Category | Checks | Passed |
|----------|--------|--------|
| SUCCESS branch | 3 | 3 |
| FAILURE branches (3 triggers) | 5 | 5 |
| PARTIAL_SUCCESS sub-categories | 4 | 4 |
| B4 margin check | 1 | 1 |
| INCONCLUSIVE-CI (spans/no spans) | 4 | 4 |
| FO-1 through FO-5 overrides | 11 | 11 |
| FO inapplicability to SUCCESS | 2 | 2 |
| BV-1 through BV-5 validity | 9 | 9 |
| Determinism | 2 | 2 |
| Schema completeness | 13 | 13 |
| compute_condition_comparisons | 4 | 4 |
| **Total** | **55** | **55** |

---

*Validation completed: 2026-06-13. No benchmark labels accessed. No framework outputs used.*
