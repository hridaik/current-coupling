# Phase 7A — Hash-Lock System Specification

## Purpose

This document specifies the exact procedure for serializing ground-truth labels,
computing a tamper-evident hash, verifying that hash at evaluation time, and maintaining
an append-only audit trail. The hash-lock system is the enforcement mechanism for the
pre-registration commitments in `phase6b_pre_registration.md`.

The system must make it impossible to evaluate the framework using different labels than
those that were committed — not just unlikely, but cryptographically detectable.

---

## 1. Canonical Serialization Format

### 1.1 Label record structure

Each directed pair (i, j) with i ≠ j and i, j ∈ {0, ..., 99} (0-indexed) produces
exactly one record. There are 9,900 records.

Each record is a JSON object with the following fields, in exactly this key order:

```json
{
  "i": <int>,
  "j": <int>,
  "direct": <0|1>,
  "sareachable": <0|1>,
  "label": <"S"|"C"|"M"|"N">,
  "witness_h2": <int|null>
}
```

Field definitions:

| Field | Type | Meaning |
|---|---|---|
| `i` | int, 0-indexed | Source neuron |
| `j` | int, 0-indexed | Target neuron |
| `direct` | 0 or 1 | 1 if A_sparse[j,i] ≠ 0; 0 otherwise |
| `sareachable` | 0 or 1 | 1 if ∃ h ∈ SA: A[h,i]≠0 and A[j,h]≠0 |
| `label` | string | One of "S", "C", "M", "N" |
| `witness_h2` | int (0-indexed) or null | The lowest-index h ∈ SA witnessing SAREACHABLE=1; null for N and S |

**Witness selection rule**: when multiple H2 neurons witness SAREACHABLE, record the
one with the smallest index. This makes the witness deterministic.

### 1.2 Top-level structure

The serialized file is a JSON object with two fields:

```json
{
  "metadata": {
    "version": "phase6b_v1",
    "n_pairs": 9900,
    "n_obs": 100,
    "master_seed": 42,
    "class_counts": {
      "S": <int>,
      "C": <int>,
      "M": <int>,
      "N": <int>
    },
    "sa_set": [132, 133, 134, 135, 136, 137, 138, 139],
    "generated_at_unix": <int>
  },
  "labels": [<record>, <record>, ...]
}
```

Note: `sa_set` uses 0-indexed H2 neuron indices (133–140 in 1-indexed = 132–139 in 0-indexed).

### 1.3 Sort order

Records in the `labels` array must be sorted in ascending lexicographic order by (i, j):
first by i ascending, then by j ascending for equal i.

Pairs with i = j are excluded (9,900 = 100 × 99 directed pairs).

### 1.4 Encoding rules

- No trailing whitespace
- No trailing comma after the last record in the array
- Compact format: no indentation, no newlines within records
- The entire file is a single line EXCEPT that the outer JSON object may be pretty-
  printed, provided the content is identical to the compact form after whitespace removal
- **Canonical form for hashing**: the file must be re-serialized to compact, no-whitespace
  form immediately before hashing. The hash is computed on the compact form.

**Canonical serialization procedure:**

```python
import json

def canonicalize(labels_dict):
    """Convert labels dict to canonical bytes for hashing."""
    return json.dumps(
        labels_dict,
        separators=(',', ':'),   # no spaces after , or :
        sort_keys=False,          # key order is fixed by schema above, not alphabetical
        ensure_ascii=True
    ).encode('utf-8')
```

### 1.5 Example records (illustrative only — not real labels)

```json
{"i":0,"j":25,"direct":0,"sareachable":1,"label":"C","witness_h2":132}
{"i":0,"j":26,"direct":0,"sareachable":0,"label":"N","witness_h2":null}
{"i":0,"j":1,"direct":1,"sareachable":0,"label":"S","witness_h2":null}
{"i":0,"j":2,"direct":1,"sareachable":1,"label":"M","witness_h2":133}
```

These are illustrative. Real labels depend on the A_sparse realization from seed 42.

---

## 2. Hashing Procedure

### 2.1 Algorithm

Hash function: **SHA-256** (FIPS 180-4).

```python
import hashlib
import json

def compute_label_hash(labels_dict):
    """
    labels_dict: the full dict with 'metadata' and 'labels' keys.
    Returns: hex-encoded SHA-256 hash string (64 chars).
    """
    canonical_bytes = json.dumps(
        labels_dict,
        separators=(',', ':'),
        sort_keys=False,
        ensure_ascii=True
    ).encode('utf-8')

    return hashlib.sha256(canonical_bytes).hexdigest()
```

### 2.2 Hash file format

The hash is stored in a plain text file with exactly one line:

```
<64-char hex hash>  labels.json
```

This follows the standard checksum file format (as output by `sha256sum`). Example:

```
a3f1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2  labels.json
```

(This is a placeholder — not a real hash.)

### 2.3 Matrix hash (secondary, for construction verification)

In addition to the label hash, compute the hash of A_sparse itself:

```python
def compute_matrix_hash(A_sparse):
    """
    A_sparse: (140, 140) float64 numpy array.
    Returns: hex SHA-256 hash of the matrix bytes.
    """
    # Ensure reproducible byte representation
    A_bytes = A_sparse.astype(np.float64).tobytes(order='C')
    return hashlib.sha256(A_bytes).hexdigest()
```

Store in `A_sparse.sha256` alongside `labels.json`.

---

## 3. Verification Procedure

Verification must be run at two mandatory checkpoints:

**Checkpoint V1**: immediately before any simulation trajectory is generated.
**Checkpoint V2**: immediately before metric computation (after all framework outputs are saved).

### 3.1 Verification algorithm

```python
def verify_label_hash(labels_path, hash_path):
    """
    Returns True if file hash matches stored hash; raises ValueError otherwise.
    """
    with open(labels_path, 'r', encoding='utf-8') as f:
        labels_dict = json.load(f)

    with open(hash_path, 'r') as f:
        stored_line = f.read().strip()
        stored_hash = stored_line.split()[0]  # first token is the hash

    computed_hash = compute_label_hash(labels_dict)

    if computed_hash != stored_hash:
        raise ValueError(
            f"HASH MISMATCH: stored={stored_hash}, computed={computed_hash}. "
            "Label file has been modified. Evaluation is invalid."
        )

    return True
```

### 3.2 Verification output

Each verification call must write one line to the audit log (see Section 5):

```json
{"event": "hash_verification", "checkpoint": "V1|V2", "result": "PASS|FAIL",
 "stored_hash": "...", "computed_hash": "...", "timestamp_unix": <int>}
```

If the result is FAIL, execution must halt immediately. No simulation or metric
computation may proceed after a hash verification failure.

### 3.3 Tamper detection test

This test is run once at audit setup time to verify the hash system works:

1. Generate a test label file (any content)
2. Hash it → store hash H1
3. Modify one character of one label (e.g., change "C" to "N" for one pair)
4. Re-hash → compute H2
5. Verify H1 ≠ H2
6. If H1 = H2, the hash system is broken; halt

---

## 4. Storage Locations

All files related to the hash-lock system are stored in a dedicated directory:

```
ground_truth/
├── labels.json          # The canonical label file (9,900 records)
├── labels.sha256        # SHA-256 hash of labels.json
├── A_sparse.npy         # The coupling matrix (NumPy binary format)
├── A_sparse.sha256      # SHA-256 hash of A_sparse bytes
├── construction_params.json  # All parameters from parameter registry
├── construction_params.sha256
└── audit_log.jsonl      # Append-only audit trail (one JSON record per line)
```

### 4.1 File permissions

After the hash commit step:
- `labels.json` and `labels.sha256` must be set to read-only: `chmod 444`
- `A_sparse.npy`, `A_sparse.sha256`, `construction_params.json`, and
  `construction_params.sha256` must be set to read-only: `chmod 444`
- `audit_log.jsonl` must be append-only: `chattr +a audit_log.jsonl` (Linux)
  or equivalent write-protection that permits appending but not overwriting

### 4.2 Git integration

The commit that creates these files is the pre-registration commit.

Required files to be tracked by git:
- `ground_truth/labels.sha256` (the hash only, not the full label file which may be large)
- `ground_truth/A_sparse.sha256`
- `ground_truth/construction_params.json`
- `ground_truth/construction_params.sha256`
- `ground_truth/audit_log.jsonl`

Optional but recommended:
- `ground_truth/labels.json` (if file size permits; ~1MB)
- `ground_truth/A_sparse.npy` (140KB; recommended to include)

The git commit hash at the time of this commit serves as the timestamped pre-registration
proof. Record it in `audit_log.jsonl` immediately.

---

## 5. Audit Trail

### 5.1 Format

`audit_log.jsonl` is a newline-delimited JSON file (JSONL). Each line is a complete
JSON object. Lines are appended in chronological order. Existing lines are never modified.

### 5.2 Required event types

The following events must be logged:

#### Event: `construction_complete`
Logged when A_sparse is constructed and stability-checked.

```json
{
  "event": "construction_complete",
  "timestamp_unix": 1750000000,
  "master_seed": 42,
  "A_sparse_hash": "a3f1b2...",
  "spectral_abscissa": -0.612,
  "n_resample_attempts": 0,
  "stability_check_passed": true
}
```

#### Event: `labels_generated`
Logged when all 9,900 labels are computed.

```json
{
  "event": "labels_generated",
  "timestamp_unix": 1750000001,
  "n_pairs": 9900,
  "class_counts": {"S": 521, "C": 688, "M": 64, "N": 8627},
  "sanity_checks_passed": ["LG1", "LG2", "LG3", "LG4"],
  "label_file_hash": "c8d9e0...",
  "labels_path": "ground_truth/labels.json"
}
```

#### Event: `hash_committed`
Logged when the hash file is written and the label file is set to read-only.

```json
{
  "event": "hash_committed",
  "timestamp_unix": 1750000002,
  "label_file_hash": "c8d9e0...",
  "hash_file_path": "ground_truth/labels.sha256",
  "git_commit": "e4f5a6b7c8d9",
  "labels_file_set_readonly": true
}
```

#### Event: `hash_verification`
Logged at checkpoints V1 and V2.

```json
{
  "event": "hash_verification",
  "timestamp_unix": 1750000003,
  "checkpoint": "V1",
  "result": "PASS",
  "stored_hash": "c8d9e0...",
  "computed_hash": "c8d9e0..."
}
```

#### Event: `acceptance_test_result`
Logged for each of P1-A through P1-D.

```json
{
  "event": "acceptance_test_result",
  "timestamp_unix": 1750000004,
  "test_id": "P1-A",
  "result": "PASS",
  "details": {
    "n_C_pairs": 688,
    "n_weak_C_below_0.01": 12,
    "fraction_weak": 0.017,
    "threshold": 0.01,
    "pass_condition": "fraction_weak < 0.30"
  }
}
```

#### Event: `simulation_started`
Logged when the first trajectory step is taken (after V1 verification passes).

```json
{
  "event": "simulation_started",
  "timestamp_unix": 1750000010,
  "condition": "oracle_z",
  "run_index": 0,
  "T": 50000,
  "dt": 0.1,
  "gamma_H2": 3.0,
  "hash_verification_v1_passed": true
}
```

#### Event: `framework_output_saved`
Logged when the framework saves its classification outputs for a condition.

```json
{
  "event": "framework_output_saved",
  "timestamp_unix": 1750000100,
  "condition": "oracle_z",
  "output_file": "results/oracle_z_classifications.json",
  "output_file_hash": "b2c3d4...",
  "labels_revealed": false
}
```

#### Event: `evaluation_complete`
Logged when metrics are computed after label revelation.

```json
{
  "event": "evaluation_complete",
  "timestamp_unix": 1750000200,
  "condition": "oracle_z",
  "hash_verification_v2_passed": true,
  "primary_metrics": {
    "C_recall": 0.61,
    "C_precision": 0.54,
    "SC_confusion": 0.17
  },
  "outcome": "success"
}
```

### 5.3 Audit log integrity

The audit log itself should be hashed at the end of each phase and the hash recorded
in the pre-registration document. However, the audit log is not subject to the same
immutability requirements as `labels.json` — new entries may be appended. The
constraint is that no existing line may be modified or deleted.

---

## 6. Recovery Procedures

### 6.1 Hash mismatch at V1

If V1 verification fails (hash mismatch before simulation starts):

1. Log the failure event
2. Halt — do not run simulations
3. Investigate: compare the label file to the git-committed hash
4. If the file was accidentally modified, restore from git and re-verify
5. If the file was intentionally modified, a new pre-registration is required:
   - Re-generate labels with the new parameters
   - Re-hash
   - Re-commit
   - Document the change as a protocol deviation

### 6.2 Hash mismatch at V2

If V2 verification fails (hash mismatch before metric computation):

1. Log the failure event
2. Halt — do not compute metrics
3. The evaluation is **invalidated** — results computed with modified labels cannot be reported
4. Restore the original label file from git, re-verify, and re-compute metrics

### 6.3 Missing hash file

If `labels.sha256` does not exist when V1 or V2 is attempted:

1. Log: `{"event": "hash_file_missing", ...}`
2. Halt — evaluation is not permitted without a committed hash
3. This means the hash-lock protocol was not executed before simulation; the benchmark
   is not pre-registered and results are not reportable as a valid benchmark evaluation
