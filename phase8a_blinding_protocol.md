# Phase 8A Blinding Protocol
**Status:** FROZEN — pre-registered before framework execution  
**Date:** 2026-06-13

This document specifies the complete information flow, barrier enforcement, and label-reveal procedure for Phase 8B evaluation.

---

## 0. Three-Party Architecture

The evaluation is structured as three logically separate parties:

| Party | Role | Information access |
|-------|------|--------------------|
| **Simulator** | Generated the benchmark corpus | Has been frozen. Takes no further action. |
| **Framework** | Black-box participant | Receives input bundle only (§2 of evaluation spec) |
| **Evaluation Engine** | Computes metrics, enforces barriers | Has framework outputs + ground-truth labels; framework never accesses this party's data |

In practice, all three parties run on the same machine. The logical separation is enforced by file permissions and the audit log.

---

## 1. Evaluation Phase

### 1.1 What the Framework Receives

The evaluation harness constructs the input bundle as specified in phase8a_evaluation_spec.md §2.3. It reads from:

- `results/phase7c/canonical/data/{condition}_run{r}.npz` — trajectory data
- The hardcoded parameter `dt=0.10`, `t_eff=48000`, `n_obs=100`

The harness does NOT pass:
- Any path or reference to `ground_truth/`
- Any parameter from `config.py` (except dt, t_eff, n_obs which are observational metadata)
- Any hash or provenance information

### 1.2 Framework Execution

The framework is executed in a subprocess or contained environment. It writes its output to a pre-specified path:

```
results/phase8b/framework_outputs/{condition}_output.json
```

The output schema is as specified in phase8a_evaluation_spec.md §3.

### 1.3 Output Immediately Frozen

Immediately after the framework writes each output file, the evaluation harness:
1. Computes SHA-256 of the output file
2. Records the hash in the evaluation audit log:
   ```json
   {"event": "framework_output_received", "condition": "...", 
    "output_file": "...", "sha256": "...", "timestamp_unix": ...}
   ```
3. Sets the output file to read-only (chmod 444)

**No modification to the framework output is permitted after this point.**

The framework is NOT told the hash. The hash is held by the evaluation harness only.

---

## 2. Scoring Phase

### 2.1 Trigger

Scoring begins only after:
- oracle_z output is written and frozen (for primary verdict)
- Blinding checks (§2.2) pass

### 2.2 Blinding Checks Before Scoring

The following checks run before any label is revealed to the scoring process:

| Check | Procedure | Failure action |
|-------|-----------|---------------|
| BC-1: Output file hash integrity | Recompute SHA-256 of output file; compare to logged hash | Abort evaluation; report tampering |
| BC-2: Label file hash integrity | Recompute SHA-256 of `labels.json`; compare to committed hash `dc99697e…` | Abort evaluation; report tampering |
| BC-3: Information barrier audit | Confirm framework process had no access to `ground_truth/labels.json` or `ground_truth/A_sparse.npy` | Report violation; flag results as potentially contaminated |
| BC-4: Output schema validity | Confirm output contains all 9,900 pairs with valid class_prob (sums to 1 ± 1e-6) | Apply degenerate-output handling from metric registry §8 |

### 2.3 BC-3: Information Barrier Audit Procedure

The audit checks:
1. **File access log**: if the OS or execution environment provides file access logging, verify `ground_truth/labels.json` and `ground_truth/A_sparse.npy` were not opened by the framework process
2. **Content inspection**: verify framework output does not contain any string that matches a label (`"S"`, `"C"`, `"M"`, `"N"` are too common to be informative; verify that class_prob values are not suspiciously concentrated on the correct classes at a rate >99% for any class before seeing results — this would require a formal run of the evaluation)
3. **Path audit**: verify the framework's code does not contain hardcoded paths to `ground_truth/` or `results/phase7c/canonical/metadata.json`

If BC-3 is inconclusive (e.g., file access logging unavailable), this is noted in the evaluation report as a limitation. The evaluation proceeds but the report includes the audit limitation statement.

### 2.4 Metric Computation

After blinding checks pass, the evaluation engine:
1. Loads `ground_truth/labels.json` (hash verified again)
2. Loads framework output `results/phase8b/framework_outputs/{condition}_output.json`
3. Computes all metrics defined in phase8a_metric_registry.md
4. Records all metric values with 95% bootstrap CIs
5. Records all values in `results/phase8b/metrics_{condition}.json`

The evaluation engine has no feedback path to the framework.

---

## 3. Reveal Phase

Ground-truth labels become human-visible only after:
1. Oracle_z output is frozen (hash recorded)
2. Blinding checks BC-1 through BC-4 pass
3. Primary metric values are computed and logged (oracle_z)
4. Primary verdict is determined (SUCCESS/PARTIAL/FAILURE/INCONCLUSIVE)
5. The verdict is written to `results/phase8b/verdict.json` with hash

**Only then** may the evaluator inspect individual pairs' true labels against framework predictions, or generate the confusion matrix.

### 3.1 Label Reveal Log Event

```json
{"event": "labels_revealed_to_evaluator",
 "oracle_z_verdict": "...",
 "primary_metrics": {...},
 "label_hash_at_reveal": "dc99697e...",
 "reveal_timestamp_unix": ...}
```

This event is appended to the audit log. It is immutable.

### 3.2 Post-Reveal Restrictions

After labels are revealed, the following are forbidden:
- Adjusting success/failure thresholds
- Adding or removing metrics from the primary set
- Adding or removing baselines
- Recomputing metrics with alternative aggregation
- Re-running the framework with any parameter adjustments
- Reinterpreting what "C" or "LR" means

Post-reveal analysis is permitted but must be labeled as **EXPLORATORY** and cannot modify the pre-registered verdict.

---

## 4. Audit Trail Requirements

The evaluation audit log (`results/phase8b/evaluation_audit.jsonl`) must contain the following events in order:

| Event | When logged |
|-------|------------|
| `evaluation_started` | Before framework receives any input |
| `input_bundle_created` | After constructing each condition's input bundle |
| `framework_output_received` | After each output file is written and hashed |
| `blinding_check_passed` | After BC-1 through BC-4 pass for oracle_z |
| `labels_loaded_for_scoring` | When evaluation engine first reads labels.json |
| `metrics_computed` | After each condition's metrics are computed |
| `verdict_recorded` | After primary verdict is determined |
| `labels_revealed_to_evaluator` | When human evaluator may see pair-level labels |

Any deviation from this order must be recorded and explained.

---

## 5. Framework Sandboxing

### 5.1 Minimum Barrier

At minimum, the framework must be executed with its working directory set to a location that does not contain or link to `ground_truth/` or `results/phase7c/canonical/`. 

The evaluation harness must not pass any environment variable that would allow the framework to locate these directories by traversing the filesystem.

### 5.2 Forbidden Framework Behaviors

The framework code must not:
- Import from `scripts.phase7b` or `scripts.phase7c`
- Read any file from `ground_truth/`
- Read any file from `results/phase7c/`
- Call `generate_labels()`, `build_A_sparse()`, or any Phase 7B function
- Use the neuron indices to infer module membership through hardcoded modular arithmetic (e.g., `module = neuron_idx // 25`)

### 5.3 Acceptable Framework Behaviors

The framework may:
- Use the provided `y(t)` and `z_oracle(t)` arrays in any way
- Use any statistical or machine learning method that operates only on the observed data
- Use the neuron indices as arbitrary identifiers
- Use multiple runs for cross-validation, aggregation, or denoising
- Use the condition name to adjust its algorithm (e.g., different algorithm for blind_z)

---

## 6. Re-evaluation Rules

A second framework evaluation (e.g., with bug fixes) is permitted only under the following conditions:
- The original evaluation is clearly labeled as INVALIDATED in the audit log
- The reason for re-evaluation is documented (bug, not performance)
- The re-evaluation uses identical input bundles (same frozen data files)
- The original output files and metric reports are preserved
- The re-evaluation uses the same pre-registered protocol with no modifications to metrics, thresholds, or baselines

Re-evaluation to improve performance is explicitly forbidden.
