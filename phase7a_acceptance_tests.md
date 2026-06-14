# Phase 7A — Acceptance Tests

## Purpose

These are the four pass/fail gate tests that must all succeed before the first
simulation trajectory is generated. They are run after all construction checks
(CK-G*, CK-L*, CK-H*) pass.

A failed acceptance test blocks Phase 7B entirely. The specified remediation must
be applied and the test re-run before proceeding.

Tests are labeled P1-A through P1-D per the Phase 7A brief.

---

## Pre-Conditions for Running Acceptance Tests

The following must be true before running any acceptance test:

1. All construction checks CK-G1 through CK-H4 have passed.
2. The label file `ground_truth/labels.json` has been generated.
3. The hash commit has been executed (`labels.sha256` exists and was written by the
   hash-lock procedure, not by hand).
4. The audit log `ground_truth/audit_log.jsonl` contains a `labels_generated` event
   and a `hash_committed` event.

---

## P1-A — H2 Weight Effectiveness Test

### Purpose

Verify that the H2 path weights are strong enough that C-labeled pairs have a
detectable state-dependent signal. A C pair where both H2 path edges have near-zero
weights is correctly labeled (the path exists) but may be undetectable by any method.
If too many C pairs fall in this category, the benchmark tests estimation noise rather
than the framework's conceptual capability.

### Inputs

- `A_sparse`: the constructed 140×140 coupling matrix
- `labels`: the committed label array
- `SA`: {132, ..., 139} (0-indexed H2 indices)

### Procedure

For every C-labeled pair (i, j), compute the **effective H2 path strength**:

```
strength(i, j) = max over h in SA of |A_sparse[h, i]| × |A_sparse[j, h]|
```

where the max is taken only over h that witness SAREACHABLE (i.e., both A[h,i]≠0 and
A[j,h]≠0). For pairs where SAREACHABLE is true via exactly one h, strength equals
|A[h,i]| × |A[j,h]|. For pairs with multiple witnessing H2 neurons, strength is the
maximum over all witnesses.

This is a proxy for the contribution of the H2 relay to the covariance Cov(x_i, x_j):
roughly, a larger product means the H2-mediated state-dependent covariance is larger.

```python
def compute_C_pair_strengths(labels, A_sparse, SA):
    strengths = []
    for record in labels:
        if record['label'] != 'C':
            continue
        i, j = record['i'], record['j']
        max_strength = 0.0
        for h in SA:
            if A_sparse[h, i] != 0.0 and A_sparse[j, h] != 0.0:
                s = abs(A_sparse[h, i]) * abs(A_sparse[j, h])
                max_strength = max(max_strength, s)
        strengths.append({'i': i, 'j': j, 'strength': max_strength})
    return strengths
```

### Thresholds

- **Weak threshold**: strength < 0.01 (path exists but effectively undetectable)
- **Pass condition**: fraction of C pairs with strength < 0.01 is **≤ 0.30** (at most 30%)

Derivation of 0.01 threshold: the expected ΔCov(x_i, x_j) from an H2 path of strength s is
proportional to γ_H2² × Var(z) × s² / |A_self|⁴ ≈ 9 × 5 × s² / 5.0625 ≈ 8.9 × s².
For s = 0.01: ΔCov ≈ 0.00089, which is below any practical detection threshold.
For s = 0.05: ΔCov ≈ 0.022, detectable at moderate sample sizes.

### Pass Criterion

```python
strengths = compute_C_pair_strengths(labels, A_sparse, SA)
n_C = len(strengths)
n_weak = sum(1 for r in strengths if r['strength'] < 0.01)
fraction_weak = n_weak / n_C if n_C > 0 else 1.0

PASS = fraction_weak <= 0.30
```

**PASS**: at most 30% of C pairs have strength < 0.01.

**FAIL**: more than 30% of C pairs have strength < 0.01.

### Remediation if FAIL

1. Compute the distribution of strengths: report the 10th, 25th, 50th, 75th, 90th percentiles.

2. If the failure is mild (31–45% weak): resample only the H2 out-weights (columns of
   A_sparse corresponding to H2 neurons) with a minimum weight constraint:
   - Any H2 out-weight drawn with |A[j, h]| < 0.08 is resampled until |A[j, h]| ≥ 0.08.
   - This is a **pre-specified construction filter**, not a post-hoc label change.
   - Re-run CK-G4 (stability check) after resampling.
   - Re-generate labels (same SAREACHABLE topology; some new C pairs may form if new
     nonzero entries appear, but weights-only resampling does not change the sparsity
     pattern — only magnitudes change).
   - **Labels do not change** because SAREACHABLE depends only on sparsity, not magnitudes.
   - Re-hash and re-commit labels (labels are unchanged, so hash is unchanged;
     but A_sparse hash changes — update A_sparse.sha256).
   - Re-run P1-A.

3. If the failure is severe (> 45% weak): increase σ_H2_out from 0.35 to 0.50 globally.
   - Resample all H2 out-weights with the new σ.
   - This may change the sparsity pattern (probability of a weight being drawn exactly zero
     from a continuous distribution is zero; the pattern is fixed by the Bernoulli draws).
   - Re-run all CK-G checks, re-generate labels, re-hash, re-commit, re-run P1-A.
   - **This is a pre-registered remediation** — it is permitted without constituting a
     protocol deviation because it was specified in `phase6b_readiness_assessment.md`
     (Risk P1-A, mitigation: "consider imposing a minimum weight floor").

### Output to Audit Log

```json
{
  "event": "acceptance_test_result",
  "test_id": "P1-A",
  "result": "PASS",
  "n_C_pairs": 688,
  "n_weak_C": 11,
  "fraction_weak": 0.016,
  "threshold_weak": 0.01,
  "pass_threshold": 0.30,
  "strength_percentiles": {"p10": 0.023, "p25": 0.051, "p50": 0.089, "p75": 0.142, "p90": 0.201}
}
```

---

## P1-B — Class Count Plausibility Test

### Purpose

Verify that the random realization of A_sparse (seed 42) produced class counts that
are within the statistically expected range. Extreme realizations (very few C or S pairs)
would make the benchmark unable to support meaningful evaluation.

### Inputs

- `labels`: the committed label array

### Procedure

```python
from collections import Counter
counts = Counter(record['label'] for record in labels)
```

### Pass Criteria

All four conditions must hold:

| Class | Lower bound | Upper bound | Basis |
|---|---|---|---|
| S | 400 | 700 | Expected 518 ± ~4 sigma |
| C | 450 | 950 | Expected 691 ± ~4 sigma |
| M | 5 | 200 | Expected 67; minimum for class to exist |
| N | 7000 | 9000 | Expected 8624 ± ~4 sigma |

```python
bounds = {
    'S': (400, 700),
    'C': (450, 950),
    'M': (5,   200),
    'N': (7000, 9000),
}

all_pass = True
for lbl, (lo, hi) in bounds.items():
    count = counts.get(lbl, 0)
    if not (lo <= count <= hi):
        print(f"FAIL: |{lbl}| = {count}, expected [{lo}, {hi}]")
        all_pass = False
    else:
        print(f"PASS: |{lbl}| = {count} in [{lo}, {hi}]")

PASS = all_pass
```

**PASS**: all four classes have counts within bounds.

**FAIL**: any class has a count outside its bounds.

### Remediation if FAIL

1. Re-run construction with `master_seed = master_seed + 1000` (i.e., seed 1042).
2. Re-generate all CK-* checks from scratch.
3. Re-generate labels.
4. Re-run P1-B.
5. If three consecutive seeds all fail, increase either p_H2_in or p_H2_out by 0.02
   (to increase expected C count) and re-run from construction.
6. Document the seed and any parameter change in the audit log.

**Note on what triggers P1-B failure**: the bounds are deliberately wide (±4 sigma and
more). Failure indicates either: (a) a code error in label generation, (b) a code error
in A_sparse construction, or (c) an extremely unlikely realization (< 0.01% chance given
correct code). In practice, P1-B failure almost always indicates a bug, not bad luck.

### Output to Audit Log

```json
{
  "event": "acceptance_test_result",
  "test_id": "P1-B",
  "result": "PASS",
  "class_counts": {"S": 521, "C": 688, "M": 64, "N": 8627},
  "bounds": {"S": [400, 700], "C": [450, 950], "M": [5, 200], "N": [7000, 9000]}
}
```

---

## P1-C — SAREACHABLE Label Consistency Test

### Purpose

Verify that the committed labels are self-consistent with the A_sparse matrix — that is,
every C- and M-labeled pair genuinely has an H2-mediated path, and every S- and N-labeled
pair genuinely does not. This is a full independent re-computation of all labels from scratch.

This test is not redundant with CK-L5 and CK-L6. Those checks verify that individual
records are self-consistent with A_sparse; P1-C verifies that the entire label file
was generated by the correct algorithm by re-running the algorithm independently.

### Inputs

- `labels`: the committed label array (read from `ground_truth/labels.json`)
- `A_sparse`: the committed coupling matrix (read from `ground_truth/A_sparse.npy`)
- `SA`: frozenset({132, 133, 134, 135, 136, 137, 138, 139})

### Procedure

Run `generate_labels(A_sparse, SA)` independently (as a separate process, using a
clean copy of the label generation code), then compare output to committed labels
record-by-record.

```python
def run_p1c_test(labels_committed, A_sparse, SA):
    """
    Independently regenerate all labels and compare to committed labels.
    Returns (PASS: bool, n_mismatches: int, mismatches: list)
    """
    # Regenerate independently
    fresh_labels = generate_labels(A_sparse, SA)  # returns dict keyed by (i,j)

    mismatches = []
    for record in labels_committed:
        i, j = record['i'], record['j']
        committed_label = record['label']
        fresh_label = fresh_labels[(i, j)]

        if committed_label != fresh_label:
            mismatches.append({
                'i': i, 'j': j,
                'committed': committed_label,
                'fresh': fresh_label
            })

    PASS = len(mismatches) == 0
    return PASS, len(mismatches), mismatches
```

### Pass Criterion

**PASS**: zero mismatches between committed labels and freshly generated labels.

**FAIL**: any mismatch between committed and fresh labels.

### Remediation if FAIL

A mismatch between committed labels and freshly generated labels means one of:

1. **Bug in label generation code**: the code used to generate the committed labels had
   a bug that the fresh run does not. Or vice versa.
   - Identify the mismatch(es); trace the discrepancy to specific records.
   - Fix the bug in `generate_labels`.
   - Re-generate labels with the fixed code.
   - Re-hash and re-commit.
   - Re-run P1-C.

2. **A_sparse was modified after label generation**: the matrix used to generate labels
   differs from the matrix in `A_sparse.npy`.
   - Compare `compute_matrix_hash(A_sparse_loaded)` against the A_sparse hash in the
     audit log `construction_complete` event.
   - If they differ: the matrix was changed. This is a protocol violation. Trace the
     change, revert to the original A_sparse, re-generate labels, re-commit.

3. **SA set was modified**: the SA set used for fresh generation differs from the SA used
   at commit time.
   - SA is hardcoded as frozenset({132,...,139}). Compare to the `sa_set` field in
     the `labels.json` metadata. If they differ, there is a code error.

**Any mismatch in P1-C blocks Phase 7B unconditionally until resolved.**

### Special variant: spot-check for large datasets

If the full 9,900-pair comparison is prohibitively slow (it should not be — it runs in
milliseconds), a spot-check variant is permitted:

1. Randomly sample 500 pairs from the committed label file.
2. Re-compute their labels from scratch.
3. Require zero mismatches in the sample.

However, the full check is strongly preferred and is the primary version of this test.

### Output to Audit Log

```json
{
  "event": "acceptance_test_result",
  "test_id": "P1-C",
  "result": "PASS",
  "n_pairs_checked": 9900,
  "n_mismatches": 0,
  "a_sparse_hash_match": true,
  "sa_set_match": true
}
```

---

## P1-D — Hash Generation and Verification Round-Trip Test

### Purpose

Verify the entire hash-lock pipeline works correctly end-to-end:
1. Serialize labels to canonical form
2. Hash the canonical bytes
3. Write the hash to file
4. Re-read the label file from disk
5. Re-hash it
6. Confirm the hashes match

This test verifies that the I/O pipeline (serialization + deserialization) is lossless
and that the hash function is deterministic. A failure here means the verification system
itself is broken — all subsequent hash verifications (V1, V2) would be unreliable.

### Inputs

- `labels`: the committed label array (in memory)
- `labels_path`: path to `ground_truth/labels.json`
- `hash_path`: path to `ground_truth/labels.sha256`

### Procedure

```python
def run_p1d_test(labels_dict, labels_path, hash_path):
    """
    Runs four sub-tests:
    (a) Serialize-hash-verify round-trip
    (b) Disk read-hash-verify round-trip
    (c) Tamper detection
    (d) Hash file format verification
    """
    results = {}

    # Sub-test (a): in-memory round-trip
    hash_1 = compute_label_hash(labels_dict)
    hash_2 = compute_label_hash(labels_dict)  # deterministic: must equal hash_1
    results['a_deterministic'] = (hash_1 == hash_2)

    # Sub-test (b): disk read round-trip
    with open(labels_path, 'r', encoding='utf-8') as f:
        labels_from_disk = json.load(f)
    hash_from_disk = compute_label_hash(labels_from_disk)
    with open(hash_path, 'r') as f:
        stored_hash = f.read().strip().split()[0]
    results['b_disk_match'] = (hash_from_disk == stored_hash)

    # Sub-test (c): tamper detection
    import copy
    tampered = copy.deepcopy(labels_dict)
    # Modify one label in the copy (guaranteed to be modifiable)
    for record in tampered['labels']:
        if record['label'] == 'C':
            record['label'] = 'N'  # tamper
            break
    hash_tampered = compute_label_hash(tampered)
    results['c_tamper_detected'] = (hash_tampered != hash_1)

    # Sub-test (d): hash file has correct format
    with open(hash_path, 'r') as f:
        content = f.read().strip()
    parts = content.split()
    results['d_format'] = (
        len(parts) == 2 and
        len(parts[0]) == 64 and  # SHA-256 hex is 64 chars
        all(c in '0123456789abcdef' for c in parts[0]) and
        parts[1] == 'labels.json'
    )

    PASS = all(results.values())
    return PASS, results
```

### Pass Criterion

All four sub-tests must pass:

| Sub-test | Condition |
|---|---|
| (a) Deterministic hash | hash_1 == hash_2 (two serializations of same dict give same hash) |
| (b) Disk round-trip | hash re-computed from file matches stored hash in labels.sha256 |
| (c) Tamper detection | modifying one label produces a different hash |
| (d) Hash file format | stored hash is 64 hex chars followed by 'labels.json' |

**PASS**: all four sub-tests pass.

**FAIL**: any sub-test fails.

### Remediation if FAIL

- Sub-test (a) fails: the `compute_label_hash` function is not deterministic.
  Investigate JSON serialization — likely a non-deterministic sort or float representation.
  Fix `canonicalize()` function and re-run.

- Sub-test (b) fails: the hash on disk does not match the in-memory hash. Two possibilities:
  (i) the file was written with different serialization than what `compute_label_hash`
  computes — fix the write procedure; (ii) the file was corrupted in transit — restore
  from git and re-run.

- Sub-test (c) fails: modifying a label does not change the hash. This is a fundamental
  cryptographic failure (collision) or a serialization bug (the tampered field is not
  included in the canonical form). Investigate and fix immediately.

- Sub-test (d) fails: the hash file has wrong format. Re-write it using the correct
  format specified in `phase7a_hashlock_system.md` Section 2.2.

### Output to Audit Log

```json
{
  "event": "acceptance_test_result",
  "test_id": "P1-D",
  "result": "PASS",
  "sub_tests": {
    "a_deterministic": true,
    "b_disk_match": true,
    "c_tamper_detected": true,
    "d_format": true
  },
  "stored_hash": "c8d9e0f1a2b3c4d5...",
  "computed_hash": "c8d9e0f1a2b3c4d5..."
}
```

---

## Acceptance Test Execution Summary

Run all four tests in this order. Each test is independent but they share pre-conditions.

```
[Pre-conditions: all CK-* checks passed, labels generated and committed]
        │
        ▼
[P1-D] Hash round-trip test
        │ PASS                FAIL → Fix hash system, re-run
        ▼
[P1-C] SAREACHABLE label consistency
        │ PASS                FAIL → Identify bug, re-generate labels, re-commit, re-run
        ▼
[P1-B] Class count plausibility
        │ PASS                FAIL → Re-seed construction, re-generate labels, re-commit, re-run
        ▼
[P1-A] H2 weight effectiveness
        │ PASS                FAIL → Apply weight floor, re-run (labels unchanged)
        ▼
[ALL PASS → Phase 7B simulation may begin]
```

**P1-D is run first** because a broken hash system would make P1-C's audit log entry
untrustworthy. **P1-C is run second** because a label inconsistency would make P1-B
(which counts committed labels) potentially misleading. **P1-B is run third** because
an implausible class distribution might explain why P1-A reports an unusually high
weak-C fraction. **P1-A is run last** because it has the gentlest remediation
(weight resampling without label changes).

---

## Gate Enforcement

The simulation code must contain a hard gate that prevents execution if any acceptance
test has not been recorded as PASS in the audit log:

```python
def check_all_acceptance_tests_passed(audit_log_path):
    """
    Read audit log and verify all four acceptance tests have a PASS record.
    Raises RuntimeError if any test has not passed.
    """
    with open(audit_log_path, 'r') as f:
        events = [json.loads(line) for line in f]

    test_results = {}
    for event in events:
        if event.get('event') == 'acceptance_test_result':
            tid = event['test_id']
            result = event['result']
            # Take the most recent result for each test ID
            test_results[tid] = result

    required = {'P1-A', 'P1-B', 'P1-C', 'P1-D'}
    missing = required - set(test_results.keys())
    failed = {tid for tid, result in test_results.items() if result != 'PASS'}

    if missing:
        raise RuntimeError(f"Acceptance tests not run: {missing}")
    if failed:
        raise RuntimeError(f"Acceptance tests failed: {failed}")

    return True  # all passed

# First line of simulate():
check_all_acceptance_tests_passed('ground_truth/audit_log.jsonl')
verify_label_hash('ground_truth/labels.json', 'ground_truth/labels.sha256')  # V1
# ... rest of simulation
```

This gate is the final enforcement mechanism. No simulation trajectory is generated
without it being cleared.
