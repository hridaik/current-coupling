# Phase 8B Audit Report

**Date**: 2026-06-13  
**Audit log**: `results/phase8b/evaluation_audit.jsonl`

---

## Event Sequence Verification

| Step | Event | Timestamp (unix) | Status |
|------|-------|-----------------|--------|
| 1 | framework_output_received | 1781349477 | LOGGED |
| 2 | blinding_check_passed | 1781349477 | LOGGED |
| 3 | labels_loaded_for_scoring | 1781349477 | LOGGED |
| 4 | metrics_computed | 1781349782 | LOGGED |
| 5 | verdict_recorded | 1781349782 | LOGGED |
| 6 | labels_revealed_to_evaluator | 1781349782 | LOGGED |

All 6 required events logged in correct order. No events missing. No events out of sequence.

---

## Hash Verification

### Framework Output

| Item | Value |
|------|-------|
| Recorded hash (at freeze) | `e71364e2ef3fdc7a764cb5e888efdefd42c492ca51cd77bc5a90a2b104ef7034` |
| Event recorded | framework_output_received |
| BC-1 (hash integrity) | PASS |

### Labels

| Item | Value |
|------|-------|
| Label hash at scoring | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` |
| Committed label hash | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` |
| Match | YES |
| BC-2 (label integrity) | PASS |
| Label hash at reveal | `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081` |
| Label hash consistency | CONFIRMED |

### Verdict

| Item | Value |
|------|-------|
| Verdict hash | `5f47a4020622157fee19d76b9e02995222948812b9d6747cec845d5acd21d31f` |
| Verdict file | `results/phase8b/verdict.json` |
| Verdict file read-only | YES (chmod 444) |

---

## Blinding Checks

| Check | Result | Notes |
|-------|--------|-------|
| BC-1: Output hash integrity | PASS | SHA-256 verified before scoring |
| BC-2: Label hash integrity | PASS | Labels match committed hash |
| BC-3: Information barrier (metadata) | PASS | No forbidden paths in metadata |
| BC-4: Schema validity (9900 pairs) | PASS | All class_prob sums ≈ 1.0 |

---

## Output Freeze

Framework output was frozen immediately after generation:
- File: `framework_output.json`
- Hash recorded: `e71364e2ef3fdc7a764cb5e888efdefd42c492ca51cd77bc5a90a2b104ef7034`
- Set read-only: YES
- Audit entry written before scoring began: YES

---

## Label Reveal Sequence

Labels were revealed only after:
1. Output frozen ✓
2. Blinding checks passed ✓
3. Labels loaded for scoring ✓
4. Framework metrics computed ✓
5. Verdict recorded ✓
6. **Labels revealed to evaluator** ✓

---

## Protocol Violations

None detected.

---

## Execution Notes

The harness crashed after step 3 (labels loaded) during the first execution due to a bug in `compute_all_primary_metrics` (`'LR' is not in list` error in Top-K computation). The bug was fixed (see Phase 8B-0 bug log) and the harness restarted. Because the framework output, blinding checks, and label loading had already completed and were logged, the resume path correctly used the recorded hash from the first run without re-freezing or re-verifying — exactly the behavior required by the protocol (the output was frozen at the hash shown above, which was recorded before any labels were accessed).

The harness was also made idempotent for already-completed steps (steps 1-3) to support crash recovery without compromising the frozen sequence. This is an engineering fix, not a scientific one — no framework output was modified, no labels were accessed outside the gate, and no metrics were computed before the blinding checks passed.

---

## Audit Log (complete)

```
{"timestamp_unix": 1781349477, "event": "framework_output_received", "condition": "oracle_z", "output_file": "framework_output.json", "sha256": "e71364e2ef3fdc7a764cb5e888efdefd42c492ca51cd77bc5a90a2b104ef7034"}
{"timestamp_unix": 1781349477, "event": "blinding_check_passed", "all_passed": true, "checks": {"BC-1": true, "BC-2": true, "BC-3": true, "BC-4": true}}
{"timestamp_unix": 1781349477, "event": "labels_loaded_for_scoring", "label_hash": "dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081", "label_path": "/home/hridai/code/worm-phase0/ground_truth/labels.json"}
{"timestamp_unix": 1781349782, "event": "metrics_computed", "condition": "oracle_z", "macro_auroc": 0.5384554197161826, "c_auroc": 0.4483500392459158, "lr_auroc": 0.4196520529405404}
{"timestamp_unix": 1781349782, "event": "verdict_recorded", "verdict": "FAILURE", "verdict_hash": "5f47a4020622157fee19d76b9e02995222948812b9d6747cec845d5acd21d31f", "verdict_path": "/home/hridai/code/worm-phase0/results/phase8b/verdict.json"}
{"timestamp_unix": 1781349782, "event": "labels_revealed_to_evaluator", "oracle_z_verdict": "FAILURE", "primary_metrics": {"macro_auroc": 0.5384554197161826, "c_auroc": 0.4483500392459158, "lr_auroc": 0.4196520529405404}, "label_hash_at_reveal": "dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081"}
```
