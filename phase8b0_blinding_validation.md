# Phase 8B-0 Blinding Validation Report

**Date**: 2026-06-13  
**Script**: `scripts/phase8/validate_blinding.py`  
**Result**: 23/23 checks PASSED

---

## Overview

All blinding controls from `phase8a_blinding_protocol.md` were validated using temporary files and directories. No benchmark data was accessed. No labels were revealed outside the gated path.

---

## Test Results

### T1: Output file freeze — hash and chmod

**Purpose**: Verify that `freeze_output_file()` (a) computes the correct SHA-256 hash and (b) sets the file to read-only (chmod 0o444).

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| freeze_output_file returns correct SHA-256 | True | True | PASS |
| freeze_output_file sets read-only (0o444) | True | True | PASS |

**Method**: Wrote a temporary JSON file, computed SHA-256 independently, compared to returned hash, then read `stat.S_IMODE(os.stat(path).st_mode)`.

---

### T2: Hash mismatch → BC-1 fails

**Purpose**: BC-1 (output hash integrity) must fail when the recorded hash doesn't match the file, and pass when it matches.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BC-1 fails on hash mismatch | False | False | PASS |
| BC-1 passes on correct hash | True | True | PASS |

**Method**: Passed `recorded_output_hash='0'*64` (wrong hash) and then the correct SHA-256 to `run_blinding_checks()`.

---

### T3: Label hash integrity — BC-2

**Purpose**: BC-2 must fail when the label file does not match `COMMITTED_LABEL_HASH`.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BC-2 fails when label file has wrong hash | False | False | PASS |

**Method**: Wrote a minimal fake labels file to the redirected `LABELS_PATH`. Its SHA-256 does not match the committed hash `dc99697e…`, so BC-2 correctly fails.

---

### T4: Information barrier — BC-3 detects forbidden path references

**Purpose**: BC-3 must flag metadata that contains references to forbidden symbols (e.g., "ground_truth", "labels.json").

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| BC-3 fails when metadata references ground_truth | False | False | PASS |
| BC-3 passes on clean metadata | True | True | PASS |

**Method**: Passed `output_metadata` with `"input_files": ["/path/to/ground_truth/labels.json"]` (fails), then `{"method": "current_velocity"}` (passes). Checked `forbidden_indicators` list in `run_blinding_checks()`.

---

### T5: Framework code audit — forbidden symbol detection

**Purpose**: `audit_framework_code_paths()` must detect references to forbidden symbols in framework source code.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Clean code: no violations | True (0 violations) | 0 violations | PASS |
| Code with "ground_truth": violations found | True (≥1 violation) | ≥1 violation | PASS |

**Method**: Created two temporary `.py` files: one clean (`def estimate(y): return {}`), one containing `# ground_truth labels loaded`. Called `audit_framework_code_paths([path])` on each.

---

### T6: Event sequence — assert_event_not_yet enforces ordering

**Purpose**: If a later event in `REQUIRED_EVENT_ORDER` has already occurred, recording an earlier event must raise `RuntimeError`.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| assert_event_not_yet raises if later event already occurred | RuntimeError | RuntimeError | PASS |

**Method**: Logged `metrics_computed` directly to the audit log, then called `assert_event_not_yet('framework_output_received')` (which is earlier in the sequence). This must raise because `metrics_computed` is later.

---

### T7: assert_event_completed raises when prerequisite missing

**Purpose**: Attempting an action that requires a prior event must raise `RuntimeError` if that event hasn't occurred.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| assert_event_completed raises when blinding_check_passed missing | RuntimeError | RuntimeError | PASS |
| assert_event_completed does not raise after event logged | False (no raise) | False | PASS |

**Method**: Called `assert_event_completed('blinding_check_passed')` on an empty log (raises), then logged the event and called again (does not raise).

---

### T8: build_input_bundle path audit — no ground_truth access

**Purpose**: `build_input_bundle()` must not access any path under `ground_truth/`. Verified by source inspection for forbidden config symbols.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| Source does not reference LABELS_PATH | True | True | PASS |
| Source does not reference A_SPARSE_PATH | True | True | PASS |
| Source does not reference GROUND_TRUTH_DIR | True | True | PASS |

**Method**: Used `inspect.getsource(bld.build_input_bundle)` and searched for the config symbol names (not the word "ground_truth" which legitimately appears in the docstring). The function accesses only `cfg.DATASET_DIR` (trajectory data).

---

### T9: load_labels_for_scoring gated by blinding_check_passed

**Purpose**: Labels may not be loaded until `blinding_check_passed` has been logged.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| load_labels_for_scoring raises without blinding_check_passed | RuntimeError | RuntimeError | PASS |

**Method**: Called `load_labels_for_scoring()` on a fresh audit log containing no `blinding_check_passed` event. The function calls `assert_event_completed('blinding_check_passed')` internally, which raises.

---

### T10: Event log reading

**Purpose**: `get_completed_events()` correctly reflects logged events.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| evaluation_started in completed events | True | True | PASS |
| input_bundle_created in completed events | True | True | PASS |
| framework_output_received NOT yet in events | True | True | PASS |

**Method**: Logged two events, verified presence/absence using `get_completed_events()`.

---

### T11: Verdict file frozen after record_verdict

**Purpose**: After recording the verdict, the verdict file must be written and read-only.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| record_verdict returns non-empty hash | True (64-char hex) | True | PASS |
| verdict file exists | True | True | PASS |
| verdict file is read-only (0o444) | True | True | PASS |

**Method**: Logged `metrics_computed`, called `record_verdict({'verdict': 'SUCCESS', ...})`, inspected return value and file permissions.

---

### T12: REQUIRED_EVENT_ORDER completeness

**Purpose**: The event sequence must contain all 8 mandatory events from the blinding protocol.

| Check | Expected | Got | Status |
|-------|----------|-----|--------|
| REQUIRED_EVENT_ORDER contains all 8 mandatory events | True | True | PASS |

**Events verified present**:
1. `evaluation_started`
2. `input_bundle_created`
3. `framework_output_received`
4. `blinding_check_passed`
5. `labels_loaded_for_scoring`
6. `metrics_computed`
7. `verdict_recorded`
8. `labels_revealed_to_evaluator`

---

## Summary

| Control | Checks | Passed |
|---------|--------|--------|
| Output hash freeze (BC-1) | 3 | 3 |
| Label hash integrity (BC-2) | 1 | 1 |
| Metadata path audit (BC-3) | 2 | 2 |
| Framework code audit | 2 | 2 |
| Event sequence enforcement | 4 | 4 |
| build_input_bundle isolation | 3 | 3 |
| Label loading gate | 1 | 1 |
| Audit log reading | 3 | 3 |
| Verdict recording | 3 | 3 |
| Event order completeness | 1 | 1 |
| **Total** | **23** | **23** |

---

## Bugs Found

None. The blinding implementation matched specification exactly.

**Note on T8 test design**: The check was initially written to look for the string "ground_truth" in `build_input_bundle`'s source. This failed because the docstring legitimately documents what the function does NOT do: "Does not touch ground_truth/". The test was corrected to check for the config symbol names (`LABELS_PATH`, `A_SPARSE_PATH`, `GROUND_TRUTH_DIR`) which would indicate actual access to those paths. This is the correct check.

---

*Validation completed: 2026-06-13. No benchmark labels accessed. No framework outputs used.*
