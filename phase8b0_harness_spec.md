# Phase 8B-0 Harness Specification

**Date**: 2026-06-13  
**Status**: Implementation complete; validation passed

This document maps every item from Phase 8A specifications (inputs, metrics, baselines, blinding rules, success criteria) to its implementation module and function, with test coverage.

---

## 1. Module Architecture

```
scripts/phase8/
├── config8.py          # All frozen constants (thresholds, hashes, taxonomy)
├── input_validator.py  # Framework output loading and schema validation
├── metrics.py          # M1–M14 metric implementations
├── baselines.py        # B1–B6 baseline implementations
├── verdict.py          # Decision tree, BV checks, FO overrides
├── blinding.py         # Audit log, event sequencing, hash freeze
├── harness.py          # Master orchestrator (CLI entry point)
├── validate_metrics.py # Metric validation (61/61 PASS)
├── validate_blinding.py # Blinding validation (23/23 PASS)
└── validate_verdict.py  # Verdict validation (55/55 PASS)
```

---

## 2. Phase 8A Item → Implementation Mapping

### 2.1 Inputs and Information Barrier

| Phase 8A Item | Location | Function |
|--------------|----------|----------|
| Framework receives only y(t) and optionally z_oracle(t) | `blinding.py:build_input_bundle()` | Returns `{'runs': [{'y':..., 'z_oracle':...}]}` from DATASET_DIR only; never touches ground_truth/ |
| Framework never receives A_sparse, labels, D, H2_TARGETS | `blinding.py:build_input_bundle()` | Source-inspected in T8 of validate_blinding.py; confirmed no LABELS_PATH/A_SPARSE_PATH/GROUND_TRUTH_DIR access |
| Framework output schema: list of {i,j,class_prob,class_pred} | `input_validator.py:load_framework_output()` | Validates JSON structure, normalizes to simplex |
| Missing pairs filled with uniform 0.25 | `input_validator.py:validate_completeness()` | Fills any of the 9900 missing pairs |
| Output arrays (9900×4) | `input_validator.py:build_output_arrays()` | Returns `{'class_prob':(9900,4), 'class_pred':(9900,), 'pair_keys', 'pairs'}` |
| BC-3: Framework code must not reference forbidden paths | `blinding.py:audit_framework_code_paths()` | Scans for 'ground_truth', 'labels.json', 'A_sparse', 'H2_TARGETS', 'SA =', etc. |

### 2.2 Metrics (M1–M14)

| Metric | Phase 8A Name | Implementation | Tested |
|--------|--------------|----------------|--------|
| M1 | AUROC (per class) | `metrics.py:compute_class_auroc()` | T1,T2,T3 |
| M2 | AUPRC (per class) | `metrics.py:compute_class_auprc()` | T5,T17 |
| M3 | F1 at optimal threshold | `metrics.py:compute_class_f1()` (calls `compute_f1_at_optimal_threshold()`) | T6 |
| M4 | Precision at optimal threshold | `metrics.py:compute_class_f1()` (returns tuple) | T6 |
| M5 | Recall at optimal threshold | `metrics.py:compute_class_f1()` (returns tuple) | T6 |
| M6 | MacroAUROC | `metrics.py:compute_macro_auroc()` | T1,T2,T14,T16 |
| M7 | WeightedAUROC | `metrics.py:compute_weighted_auroc()` | T15 |
| M8 | Balanced accuracy | `metrics.py:compute_balanced_accuracy()` | T7 |
| M9 | Confusion matrix | `metrics.py:compute_confusion_matrix()` | T8 |
| M10 | LR-AUROC (score=P(C)+P(M)) | `metrics.py:compute_lr_auroc()` | T4 |
| M11 | Brier score + skill | `metrics.py:compute_brier_score()` | T9 |
| M12 | ECE | `metrics.py:compute_ece()` | T10 |
| M13 | Top-K precision | `metrics.py:compute_topk_precision()` | T11 |
| M14 | Enrichment | `metrics.py:compute_enrichment()` | T12 |
| — | AUPRC lift | `metrics.py:compute_class_auprc_lift()` | T17 |
| — | Bootstrap CI (95%) | `metrics.py:compute_bootstrap_ci()` | T13,T16 |
| — | Direct-AUROC (P(S)+P(M)) | `metrics.py:compute_direct_auroc()` | used in BV-3 |
| — | All-metrics driver | `metrics.py:compute_all_primary_metrics()` | via harness |

**Bootstrap note**: `compute_bootstrap_ci()` uses seed=8888, n_boot=2000 (N_BOOTSTRAP). The internal `_bootstrap_one()` was fixed during Phase 8B-0 validation to properly align labels with scores (see metric validation report, Bug 1).

**LR Top-K special handling**: When computing Top-K for the LR group, `compute_all_primary_metrics()` builds a virtual single-column array via `_build_lr_arrays()` to handle the binary LR case.

### 2.3 Baselines (B1–B6)

| Baseline | Phase 8A Name | Implementation | Inputs Used |
|----------|--------------|----------------|-------------|
| B1 | Null/Chance | `baselines.py:run_b1_uniform()` | None (constant 0.25) |
| B2 | Marginal frequency prior | `baselines.py:run_b2_marginal()` | COMMITTED_CLASS_COUNTS from config8 |
| B3 | Pairwise correlation | `baselines.py:run_b3_correlation(runs)` | y(t) only |
| B4 | Graphical Lasso (BIC) | `baselines.py:run_b4_glasso(runs)` | y(t) only, train=runs 0-3, val=run 4 |
| B5 | State-dependent ΔCorr | `baselines.py:run_b5_state_delta_corr(runs)` | y(t) + z_oracle(t); falls back to B3 if z missing |
| B6 | Module-membership oracle | `baselines.py:run_b6_module_oracle()` | Hardcoded i//25==j//25 rule |

**Lock enforcement**: `VALID_BASELINES = frozenset({'B1','B2','B3','B4','B5','B6'})`. The `run_all_baselines()` runner asserts `name in VALID_BASELINES` before executing any baseline.

**B4 details**: Alpha grid `[0.005, 0.01, 0.02, 0.05, 0.10]` (B4_ALPHA_GRID). Selection via BIC = `-2*loglik + k*log(n_val)` where k = non-zero off-diagonal entries. Falls back to B2 if all alpha values fail convergence.

**B3/B4/B5 softmax temperature**: 5.0 for all three (B3_SOFTMAX_TEMP, B4_SOFTMAX_TEMP, B5_SOFTMAX_TEMP). This is a frozen design parameter, not tuned.

### 2.4 Blinding Protocol (BC-1 through BC-4)

| Control | Phase 8A Item | Implementation | Tested |
|---------|--------------|----------------|--------|
| BC-1 | Output hash integrity | `blinding.py:run_blinding_checks()` → `sha256_file(output_path) == recorded_hash` | T2 |
| BC-2 | Label hash integrity | `blinding.py:run_blinding_checks()` → `sha256_file(LABELS_PATH) == COMMITTED_LABEL_HASH` | T3 |
| BC-3 | Information barrier path audit | `blinding.py:run_blinding_checks()` → metadata scan for forbidden indicators; `audit_framework_code_paths()` for code scan | T4,T5 |
| BC-4 | Output schema validity | `blinding.py:run_blinding_checks()` → `n_pairs == 9900` and all class_prob sums ≈ 1.0 | validated in input_validator |
| — | Event sequence | `blinding.py:REQUIRED_EVENT_ORDER`, `assert_event_not_yet()`, `assert_event_completed()` | T6,T7 |
| — | Output file freeze | `blinding.py:freeze_output_file()` | T1 |
| — | Label loading gate | `blinding.py:load_labels_for_scoring()` requires `blinding_check_passed` event | T9 |
| — | Verdict freeze | `blinding.py:record_verdict()` → writes to VERDICT_PATH, chmod 444, logs `verdict_recorded` | T11 |
| — | Label reveal logging | `blinding.py:record_label_reveal()` → logs `labels_revealed_to_evaluator` | part of harness step 8 |

### 2.5 Success Criteria (phase8a_success_criteria)

| Criterion | Frozen Value | Implementation |
|-----------|-------------|----------------|
| SUCCESS: MacroAUROC ≥ 0.70 | config8.THRESHOLD_SUCCESS_MACRO_AUROC | `verdict.py:determine_verdict()` |
| SUCCESS: C-AUROC ≥ 0.65 | config8.THRESHOLD_SUCCESS_C_AUROC | `verdict.py:determine_verdict()` |
| SUCCESS: LR-AUROC ≥ 0.65 | config8.THRESHOLD_SUCCESS_LR_AUROC | `verdict.py:determine_verdict()` |
| SUCCESS: framework_C_AUROC > B4_C_AUROC + 0.05 | config8.THRESHOLD_FRAMEWORK_VS_B4_C_MARGIN | `verdict.py:determine_verdict()` |
| PARTIAL: MacroAUROC ≥ 0.60 | config8.THRESHOLD_PARTIAL_MACRO_AUROC | `verdict.py:determine_verdict()` |
| PARTIAL: C-AUROC ≥ 0.55 | config8.THRESHOLD_PARTIAL_C_AUROC | `verdict.py:determine_verdict()` |
| PARTIAL: LR-AUROC ≥ 0.55 | config8.THRESHOLD_PARTIAL_LR_AUROC | `verdict.py:determine_verdict()` |
| INCONCLUSIVE-CI: CI spans threshold | — | `verdict.py:determine_verdict()` → `ci_spans` logic |
| BV-1: n(C) ≥ 100 | config8.BV1_MIN_C_COUNT | `verdict.py:check_benchmark_validity()` |
| BV-2: n(M) ≥ 30 | config8.BV2_MIN_M_COUNT | `verdict.py:check_benchmark_validity()` |
| BV-3: B4 direct AUROC ≥ 0.52 | config8.BV3_MIN_B4_DIRECT_AUROC | `verdict.py:check_benchmark_validity()` |
| BV-4: blinding audit passed | — | `verdict.py:check_benchmark_validity()` |
| BV-5: output hash verified | — | `verdict.py:check_benchmark_validity()` |
| FO-1: weak_fraction > 0.60 | config8.FO1_WEAK_FRACTION_TRIGGER | `verdict.py:apply_failure_mode_overrides()` |
| FO-2: mean_strength < 0.005 | config8.FO2_MEAN_STRENGTH_TRIGGER | `verdict.py:apply_failure_mode_overrides()` |
| FO-3: n_c < 200 | — | `verdict.py:apply_failure_mode_overrides()` |
| FO-4: y variance < 1e-4 | — | `verdict.py:apply_failure_mode_overrides()` |
| FO-5: y non-finite | — | `verdict.py:apply_failure_mode_overrides()` |

### 2.6 Frozen Constants (config8.py)

All values are derived from Phase 8A specification documents and committed to `config8.py`. Any change to `config8.py` after Phase 8B begins is a protocol violation.

| Constant | Value | Source |
|----------|-------|--------|
| COMMITTED_LABEL_HASH | dc99697e…8081 | phase7b audit |
| COMMITTED_DATASET_META_HASH | 7f398677…aed | phase7c freeze |
| COMMITTED_CLASS_COUNTS | S=497, C=857, M=89, N=8457 | sealed labels |
| N_PAIRS | 9900 | N_OBS=100, directed pairs |
| N_BOOTSTRAP | 2000 | phase8a_metric_registry §7 |
| BOOTSTRAP_CI_LEVEL | 0.95 | phase8a_metric_registry §7 |
| TOPK_VALUES | [50, 100, 200, 500] | phase8a_metric_registry §4 |
| B4_ALPHA_GRID | [0.005, 0.01, 0.02, 0.05, 0.10] | phase8a_baseline_spec |
| ECE_N_BINS | 10 | phase8a_metric_registry §3 |
| MODULE_SIZE | 25 | network design |

---

## 3. Harness Execution Sequence

`harness.py:run_evaluation(condition, output_path)` implements the 8-step sequence from `phase8a_blinding_protocol.md §BC`:

```
Step 1: freeze_output_file(output_path) → record_framework_output()
           Logs: framework_output_received
Step 2: run_blinding_checks(output_path, recorded_hash, metadata)
           Checks: BC-1, BC-2, BC-3, BC-4
           Logs: blinding_check_passed (or blinding_check_failed → RuntimeError)
Step 3: load_framework_output(output_path) → validate_completeness() → build_output_arrays()
           Validates schema, fills missing pairs, normalizes probabilities
Step 4: load_labels_for_scoring()
           Gate: requires blinding_check_passed in audit log
           Logs: labels_loaded_for_scoring
Step 5: build_input_bundle(condition) → run_all_baselines(runs)
           Reads DATASET_DIR only; runs B1–B6
Step 6: compute_all_primary_metrics(labels_dict, output_arrays)
           Logs: metrics_computed
Step 7: Save metrics JSON to METRICS_DIR/metrics_{condition}.json
Step 8: (Primary condition only) determine_verdict() → record_verdict()
           Logs: verdict_recorded, then labels_revealed_to_evaluator
```

**Protocol constraints enforced**:
- No framework outputs can be computed before blinding checks pass
- Labels cannot be loaded before blinding checks pass
- Verdict can only be recorded after metrics are computed
- Reveal can only happen after verdict is recorded
- Any blinding check failure raises RuntimeError (halts execution)

---

## 4. No Orphan Logic Audit

Every public function in every module is either:
(a) Called by `harness.py:run_evaluation()` directly or indirectly, or
(b) Called by a validation script, or
(c) A utility used by (a) or (b)

| Function | Called by |
|----------|-----------|
| `config8.*` | all modules |
| `input_validator.load_framework_output` | harness step 3 |
| `input_validator.validate_completeness` | harness step 3 |
| `input_validator.build_output_arrays` | harness step 3; baselines.py; validate_metrics.py |
| `metrics.compute_class_auroc` | harness step 6; validate_metrics.py T1-T3 |
| `metrics.compute_lr_auroc` | harness step 6; validate_metrics.py T4 |
| `metrics.compute_macro_auroc` | harness step 6; validate_metrics.py T1,T2,T14,T15,T16 |
| `metrics.compute_weighted_auroc` | harness step 6; validate_metrics.py T15 |
| `metrics.compute_class_auprc` | harness step 6; validate_metrics.py T5,T17 |
| `metrics.compute_class_f1` | harness step 6; validate_metrics.py T6 |
| `metrics.compute_balanced_accuracy` | harness step 6; validate_metrics.py T7 |
| `metrics.compute_confusion_matrix` | harness step 6; validate_metrics.py T8 |
| `metrics.compute_brier_score` | harness step 6; validate_metrics.py T9 |
| `metrics.compute_ece` | harness step 6; validate_metrics.py T10 |
| `metrics.compute_topk_precision` | harness step 6; validate_metrics.py T11 |
| `metrics.compute_enrichment` | harness step 6; validate_metrics.py T12 |
| `metrics.compute_bootstrap_ci` | harness step 6; validate_metrics.py T13,T16 |
| `metrics.compute_all_primary_metrics` | harness step 6 |
| `baselines.run_b1_uniform` | harness step 5 |
| `baselines.run_b2_marginal` | harness step 5 |
| `baselines.run_b3_correlation` | harness step 5 |
| `baselines.run_b4_glasso` | harness step 5 |
| `baselines.run_b5_state_delta_corr` | harness step 5 |
| `baselines.run_b6_module_oracle` | harness step 5 |
| `baselines.run_all_baselines` | harness step 5 |
| `verdict.check_benchmark_validity` | harness step 8 |
| `verdict.determine_verdict` | harness step 8; validate_verdict.py T1-T10 |
| `verdict.apply_failure_mode_overrides` | harness step 8; validate_verdict.py T11-T16 |
| `verdict.compute_condition_comparisons` | post-hoc analysis; validate_verdict.py T22 |
| `blinding.log_eval_event` | harness all steps |
| `blinding.freeze_output_file` | harness step 1 |
| `blinding.record_framework_output` | harness step 1 |
| `blinding.run_blinding_checks` | harness step 2; validate_blinding.py T2-T4 |
| `blinding.assert_event_not_yet` | called internally; validate_blinding.py T6 |
| `blinding.assert_event_completed` | called internally; validate_blinding.py T7 |
| `blinding.load_labels_for_scoring` | harness step 4; validate_blinding.py T9 |
| `blinding.record_verdict` | harness step 8; validate_blinding.py T11 |
| `blinding.record_label_reveal` | harness step 8 |
| `blinding.audit_framework_code_paths` | harness step 2 (optional); validate_blinding.py T5 |
| `blinding.build_input_bundle` | harness step 5; validate_blinding.py T8 |

**Functions not called by harness** (auxiliary/analysis):
- `metrics.load_labels()` — direct load without blinding gate; use only in diagnostics
- `baselines.run_b1_null()` — seeded random variant; B1 in harness uses uniform
- `baselines.register_baseline_lock()` — utility for external verification
- `verdict.benchmark_validity_passed()` — called by harness for verbose output

---

## 5. Protocol Prohibitions (enforced)

The following actions are blocked by implementation:

| Prohibition | Enforcement |
|-------------|-------------|
| Labels revealed before blinding checks | `load_labels_for_scoring()` requires `blinding_check_passed` event |
| Labels revealed before output frozen | `framework_output_received` must precede `blinding_check_passed` in sequence |
| Verdict before metrics | `record_verdict()` requires `metrics_computed` event |
| Out-of-order events | `assert_event_not_yet()` checks for later events already logged |
| Modified output file | BC-1 hash comparison detects any change |
| Modified labels | BC-2 hash comparison against COMMITTED_LABEL_HASH |
| Unauthorized baselines | `VALID_BASELINES` frozenset asserted in `run_all_baselines()` |
| Framework execution in this phase | harness.py is the only scoring entry point; no simulation code is imported |

---

## 6. Acceptance Status

All Phase 8B-0 acceptance criteria are satisfied:

| Criterion | Status |
|-----------|--------|
| All metrics validated (M1–M14) | PASS — 61/61 checks (validate_metrics.py) |
| All baselines validated (B1–B6) | PASS — structure and lock verified (baselines.py) |
| Blinding validated (BC-1–BC-4) | PASS — 23/23 checks (validate_blinding.py) |
| Verdict engine validated | PASS — 55/55 checks (validate_verdict.py) |
| Deterministic execution confirmed | PASS — T16 metrics, T20 verdict |
| No protocol violations | PASS — no framework run, no labels revealed |
| Bootstrap CI bug fixed | PASS — label-alignment error corrected |
| PS-2 sub-category bug fixed | PASS — success threshold used for routing |

**Phase 8B may begin.** The framework may now be run and its output submitted to `harness.py`.
