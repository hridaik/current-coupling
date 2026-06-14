# Phase 9B — Audit Layer

**Purpose:** Prevent a repeat of the Phase 6–8 ambiguities. The audit layer specifies
exactly what must be verified at each stage to ensure the benchmark is valid, the oracle
is not leaked, and the verdict is not contaminated.

---

## 1. Leakage Checks

Leakage is the benchmark's primary failure mode. It occurs when ground-truth information
reaches the framework before the framework produces its output. Phase 6A identified seven
leakage vulnerabilities (L1–L7). This section verifies that Phase 9B eliminates each.

### LC-1: Oracle isolation (replaces Phase 6A L1)

**Risk:** The framework script or any intermediate computation reads a ground-truth file
(DeltaOmega_true.npy, GT2, GT3) before or during estimation.

**Control:** The framework evaluation script (`evaluate_framework.py`) is prohibited from
importing any file from `results/phase9b/ground_truth/`.

**Verification procedure:**
```bash
# Before framework evaluation begins, run:
grep -r "ground_truth" scripts/phase9b/evaluate_framework.py
# Must return empty. Any match is a leakage violation.

grep -r "DeltaOmega_true" scripts/phase9b/evaluate_framework.py
# Must return empty.

grep -r "PMC" scripts/phase9b/evaluate_framework.py
# Must return empty (framework does not know PMC membership).
```

**Who checks:** Auditor (different from framework implementer) runs these checks and
signs off in the audit log before framework evaluation proceeds.

### LC-2: PMC membership not in framework inputs (replaces L4)

**Risk:** The framework is given the PMC source/target indices as inputs, allowing it
to focus its estimation on PMC pairs specifically.

**Control:** Framework inputs are exactly and only: `x_A.npy`, `x_B.npy`, `A_obs.npy`.
No additional index lists, annotations, or masks are provided.

**Verification:**
```
Framework interface signature (must match exactly):
evaluate_framework(x_A, x_B, A_obs) → DeltaOmega_estimated

No additional arguments. No keyword arguments referencing PMC, H_global, or oracle.
```

### LC-3: State variable z not in framework inputs

**Risk:** Providing z(t) to the framework gives it information about H_global drive that
a real experimenter would not have.

**Control:** Trajectory files contain only x(t) for observed neurons. z(t) is never
written to any output file accessible to the framework.

**Verification:**
```bash
# Verify trajectory files contain only observed activity
python -c "import numpy as np; x = np.load('results/phase9b/trajectories/x_A.npy'); \
  assert x.shape[1] == 150, f'Expected 150 columns, got {x.shape[1]}'"
# Shape must be (T_A, 150). Any additional columns indicate z leakage.
```

### LC-4: Ground truth locked before trajectories generated

**Risk:** If parameters are adjusted after seeing trajectory statistics, the benchmark
is tuned to the framework's operating range.

**Control:** The ground-truth manifest hash is written BEFORE `generate_trajectories.py`
is called. The trajectory generation uses the locked config, not any post-hoc adjustment.

**Verification:**
```
Check file modification timestamps:
  ground_truth_master_hash.txt   [must be OLDER than]
  trajectories/x_A.npy
  trajectories/x_B.npy

If any trajectory file is older than the master hash: HALT. Trajectories were generated
before oracle was locked. Regenerate everything from Stage 1.
```

### LC-5: Metrics computed after framework output is frozen

**Risk:** Metrics are recomputed after seeing which threshold the framework is close to,
allowing post-hoc threshold adjustment.

**Control:** The framework produces `framework_manifest.json.sha256` when it finishes.
`compute_metrics.py` verifies this hash before computing any metric. Metric thresholds
are read from `config9b.py` (locked in Stage 1), not from any file written after Stage 1.

### LC-6: No parameter tuning after D1 verification (replaces Phase 6A L5)

**Risk:** z_high or g_mod is adjusted after seeing framework performance, making the
benchmark match the framework's operating range.

**Control:** z_high is set once (when D1 is first satisfied) and locked in `config9b.py`.
`config9b.py` is hash-locked immediately after z_high is written. Any modification to
`config9b.py` invalidates all downstream outputs.

**Verification:**
```
config9b_hash = sha256('scripts/phase9b/config9b.py')
# Record at time of Stage 1 completion.
# Re-verify before Stage 4 (framework evaluation):
assert sha256('scripts/phase9b/config9b.py') == config9b_hash
# If mismatch: HALT. Config was modified after ground truth was locked.
```

---

## 2. Provenance Checks

Every output file must be traceable to its inputs. If any input changes, all downstream
outputs are invalidated.

### PC-1: Dependency graph

```
config9b.py
  ↓
A_full.npy, A_obs.npy, network_spec.json
  ↓
Sigma_A_obs.npy, Sigma_B_obs.npy, Q_A.npy, Q_B.npy, Omega_A.npy, Omega_B.npy
  ↓
DeltaOmega_true.npy → GT1, GT3
PMC_pairs.npy → GT2
communities.json → GT4
GT5a_state_lesion_ranking.npy
GT5b_structural_lesion_ranking.npy
  ↓
ground_truth_manifest.json  [GATE: must be written before anything below]
  ↓
x_A.npy, x_B.npy, x_A_lesioned.npy
  ↓
[Baselines]     [Framework output]
  ↓                   ↓
baseline_metrics.json
  +  framework_scores_off.npy
  ↓
primary_metrics.json
  ↓
primary_verdict.json
```

Any modification to a node invalidates all nodes below it in the graph.

### PC-2: Per-file SHA-256 manifest

Every output file in `results/phase9b/` is accompanied by a `.sha256` sidecar:

```
file.npy
file.npy.sha256      ← sha256 of file.npy
```

The sidecar is written immediately after the file is written, before the next script runs.

**Verification function:**
```python
def verify_file_hash(path):
    import hashlib
    with open(path, 'rb') as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    with open(path + '.sha256') as f:
        expected = f.read().strip()
    assert actual == expected, f"Hash mismatch for {path}"
```

Every evaluation script calls `verify_file_hash` on all its inputs before reading them.

### PC-3: Ground truth manifest verification

`compute_metrics.py` must verify that all GT files match the locked manifest before
computing any metric:

```python
import json, hashlib

with open('results/phase9b/ground_truth/ground_truth_manifest.json') as f:
    manifest = json.load(f)

for filename, expected_hash in manifest.items():
    with open(f'results/phase9b/ground_truth/{filename}', 'rb') as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == expected_hash, f"GT file {filename} has been modified after locking"
```

If any GT file has been modified after the manifest was locked: HALT. All downstream
outputs are invalid.

---

## 3. Hash-Lock Strategy

### HL-1: Configuration hash

Immediately after `config9b.py` is finalized:
```bash
sha256sum scripts/phase9b/config9b.py > scripts/phase9b/config9b.py.sha256
```

This hash is the root of trust for the entire benchmark.

### HL-2: Ground truth master hash

After all GT files are generated and individual hashes written:
```python
import hashlib, json

GT_FILES = [sorted list of all GT .npy and .json files]
individual_hashes = {}
for f in GT_FILES:
    with open(f'results/phase9b/ground_truth/{f}', 'rb') as fh:
        individual_hashes[f] = hashlib.sha256(fh.read()).hexdigest()

# Write manifest
with open('results/phase9b/ground_truth/ground_truth_manifest.json', 'w') as f:
    json.dump(individual_hashes, f, indent=2)

# Compute master hash
master_content = json.dumps(individual_hashes, sort_keys=True).encode()
master_hash = hashlib.sha256(master_content).hexdigest()
with open('results/phase9b/ground_truth/ground_truth_master_hash.txt', 'w') as f:
    f.write(master_hash + '\n')
```

### HL-3: Framework output hash

After `evaluate_framework.py` completes:
```python
framework_outputs = {
    'DeltaOmega_estimated.npy': sha256('results/phase9b/framework/DeltaOmega_estimated.npy'),
    'framework_scores_off.npy': sha256('results/phase9b/framework/framework_scores_off.npy'),
}
with open('results/phase9b/framework/framework_manifest.json', 'w') as f:
    json.dump({**framework_outputs, 'timestamp': str(datetime.now())}, f, indent=2)
sha256sum('results/phase9b/framework/framework_manifest.json')
```

### HL-4: Verdict hash

After `verdict.py` completes:
```python
verdict_content = json.dumps(verdict_dict, sort_keys=True).encode()
verdict_hash = hashlib.sha256(verdict_content).hexdigest()
# Append to verdict file
verdict_dict['verdict_hash'] = verdict_hash
```

The verdict is only valid if its hash matches the metric file hash and the GT manifest hash
recorded in the verdict:
```json
{
  "verdict": "SUCCESS/PARTIAL/FAILURE",
  "precision_at_50": ...,
  "rank_correlation": ...,
  "pmc_auroc": ...,
  "gt_master_hash": "...",    ← must match ground_truth_master_hash.txt
  "framework_manifest_hash": "...",
  "verdict_hash": "..."
}
```

---

## 4. Benchmark Validity Checks

These checks verify that the benchmark itself is well-constructed, independent of framework
performance.

### BV-1: Network stability [AT-1]

```
All eigenvalues of A_full in (-1, 0).
Equivalently: spectral radius ρ(A_full) < 1 and A_full has no zero eigenvalues.
If violated: the Lyapunov equation has no unique solution; the system does not have a
stationary distribution.
```

### BV-2: PMC construction integrity [AT-1b, AT-1c]

```
Check 1: A_full[PMC_source_indices, PMC_target_indices] == 0 exactly
  (no direct source-target edges; the rule was correctly enforced)
Check 2: For each PMC source i: number of H_global neurons that i projects to >= 3
Check 3: For each PMC target j: number of H_global neurons projecting to j >= 4
If any check fails: PMC construction rule was violated; ground truth is invalid.
```

### BV-3: Dominance condition satisfied [AT-4]

```
D1: median |ΔΩ_true_off| for PMC > 2 × 90th_pct |ΔΩ_true_off| for non-PMC
D2: ≥ 60% of Top_50_oracle are PMC pairs
If either fails: benchmark signal is too weak; increase z_high.
```

### BV-4: Oracle ceiling verified [AT-5]

```
B4 (oracle baseline) must achieve PMC_AUROC ≥ 0.90.
If not: the oracle itself does not recover the PMC organization, which means either
(a) D1 is marginally satisfied but D2 is not, or
(b) the off-connectome pair count calculation is wrong and the true PMC density is lower.
```

This is an important additional check not in Phase 6–8: the oracle must work before the
framework is evaluated. If the oracle fails, the benchmark design is at fault.

### BV-5: A_obs cancellation verified [AT-2b]

```
DeltaOmega_true = (D_A × Q_A + A_obs) - (D_B × Q_B + A_obs)
                = D_A × Q_A - D_B × Q_B

Verify: max(|DeltaOmega_true - (D_A @ Q_A - D_B @ Q_B)|) < 1e-10
This confirms that A_obs correctly cancels. If not: numerical precision issue in
Lyapunov solver; use higher-precision solver.
```

### BV-6: Trajectory convergence verified [AT-3]

```
Sample_Cov(x_A) ≈ Sigma_A_obs with Spearman ρ ≥ 0.95 over all (i,j) pairs
Sample_Cov(x_B) ≈ Sigma_B_obs with Spearman ρ ≥ 0.95 over all (i,j) pairs
If not: trajectory length T is too short; increase T and regenerate.
```

---

## 5. Oracle Isolation Checks

These checks verify that the oracle is not inadvertently contaminated into the framework's
input or into the metric computation in a circular way.

### OI-1: Framework cannot compute ΔΩ_true from its inputs alone

The framework receives x_A, x_B, A_obs. It does NOT receive D_A, D_B (the true diffusion
matrices), z_high, H_global activity, or the Lyapunov solution. Therefore:

```
The framework CANNOT compute ΔΩ_true = D_A Q_A - D_B Q_B exactly, because:
  - Q_A and Q_B must be estimated from x_A and x_B (finite sample)
  - D_A and D_B must be estimated from x_A and x_B (finite sample)
  - The framework does not know which elements of D differ between states
```

This confirms there is no shortcut: the framework must actually estimate ΔΩ under
finite-sample conditions. **The oracle is not reconstructable from the framework's inputs.**

### OI-2: Metrics use the same pair indexing for oracle and framework

A subtle bug: if the oracle ranking (GT3) and the framework scores are indexed differently
(e.g., different ordering of pairs), the rank correlation computation becomes meaningless.

**Control:** Both GT3 and the framework output use the same canonical pair list:
```python
# Canonical off-connectome pair list (generated once in build_oracle.py)
off_pairs = [(i,j) for i in range(N_OBS) for j in range(i+1, N_OBS)
             if A_obs[i,j] == 0 and A_obs[j,i] == 0]
# Sorted by (i,j) lexicographically. Written to pair_index.npy.
# All subsequent arrays (GT1, framework_scores_off) use this exact ordering.
```

**Verification:** Before computing any metric, verify:
```python
assert GT3_ranking.shape[0] == framework_scores_off.shape[0], \
    "Oracle and framework have different numbers of off-connectome pairs"
assert GT3_ranking.shape[0] == len(off_pairs)
```

### OI-3: Permutation null uses the same off-connectome pair set

The permutation null for PMC_AUROC shuffles `pmc_binary` labels within the off-connectome
pair set. It does NOT add or remove pairs from the set. The pair set is the same for all
permutations and for the observed statistic.

**Control:**
```python
null_aurocs = []
for seed in range(10000):
    rng = np.random.default_rng(RNG_SEED + 2 + seed)
    shuffled_labels = rng.permutation(pmc_binary)  # same length as pmc_binary
    null_aurocs.append(roc_auc_score(shuffled_labels, framework_scores_off))
```

### OI-4: Secondary metrics do not change primary verdict

Module recovery (NMI) and intervention recovery (ρ_state, ρ_structural) are computed
AFTER the primary verdict is written. They cannot change the verdict.

**Control:** `verdict.py` reads only `primary_metrics.json`. It does not read
`secondary_metrics.json`. The secondary metrics file is written separately and labeled
clearly as "supplementary."

---

## 6. Circularity Guards (Phase 6A L2 Resolution)

The Phase 6A review identified that using state-lesion outcomes for both labeling and
validation was circular (L2). Phase 9B eliminates this by construction.

### CG-1: PMC membership is topological, not functional

PMC membership is defined by H_global connectivity rules written in config9b.py BEFORE
the Lyapunov equation is solved. The dominance condition D1 is then verified (confirming
that the topological construction creates detectable state-dependence), but D1 verification
does NOT alter PMC membership.

**Verification:**
```
Audit log entry: "PMC_SOURCE_INDICES and PMC_TARGET_INDICES were committed to
config9b.py on [date], before any call to lyapunov_oracle.py."
```

### CG-2: ΔΩ_true is a consequence, not a definition

The oracle DeltaOmega_true.npy is computed by lyapunov_oracle.py from (A_full, D_A, D_B),
which are derived from config9b.py. It is not used to define PMC membership. The PMC pair
set (GT2) is written from config9b.py directly, independently of the Lyapunov solution.

**Verification:**
```python
# In build_oracle.py:
# GT2 is built from config:
PMC_pairs = [(i,j) for i in PMC_SOURCE_INDICES for j in PMC_TARGET_INDICES]
# NOT from: [(i,j) where DeltaOmega_true[i,j] > threshold]
```

### CG-3: Success thresholds are not adjusted after framework evaluation

The thresholds in `verdict.py` are read from `config9b.py` (written before any evaluation).
They are hard-coded as assertions in the verdict script and cannot be changed without
modifying config9b.py — which would invalidate the config hash.

---

## 7. Audit Log

A human-readable audit log is maintained throughout Phase 9B:

```
results/phase9b/audit_log.md
```

Format for each entry:
```
[DATE] [STAGE] [ACTION] [AUDITOR]
  Description: what was done
  Hash verification: pass/fail
  Files changed: [list]
  Notes: [any deviations or issues]
```

Required audit log entries:

| Entry | When | Required content |
|---|---|---|
| AL-1 | After config9b.py locked | config9b_hash, all parameters listed |
| AL-2 | After build_network.py | AT-1 pass/fail, A_full eigenvalue range |
| AL-3 | After lyapunov_oracle.py | AT-2 pass/fail, Lyapunov solver used |
| AL-4 | After verify_dominance.py | D1/D2 values, z_high used |
| AL-5 | After oracle hash-lock | ground_truth_master_hash value |
| AL-6 | After trajectory generation | AT-3 pass/fail, convergence rho values |
| AL-7 | After baselines | AT-5 oracle ceiling check |
| AL-8 | After framework evaluation | framework_manifest_hash |
| AL-9 | LC-1 through LC-6 checks | All pass/fail |
| AL-10 | Final verdict | Verdict string, all metric values |

The audit log is the definitive record of what happened and when. It must be completed
before Phase 9C (trajectory generation and framework evaluation) begins.

---

## 8. Differences from Phase 6–8 Audit Protocol

Phase 6–8 had a blinding protocol (phase8a_blinding_protocol.md). The key differences here:

| Phase 6–8 | Phase 9B |
|---|---|
| Blinding: evaluator didn't see labels during evaluation | Oracle isolation: framework script has no access to GT files |
| Ground truth: per-pair S/C/M/N labels | Ground truth: PMC pair set + oracle ranking (organization-level) |
| Leakage risk: C-label definitional equivalence with ΔΩ | Resolved: PMC membership topological, not functional |
| Metric: AUROC over all pairs (S inflates aggregate) | Metric: PMC_AUROC over off-connectome pairs only |
| Baseline: GraphicalLasso (B4, failed to converge) | Baselines: Random, ΔCorr, Glasso pooled, Oracle (4 baselines) |
| Verdict engine: verdict.py with frozen hash | Verdict engine: same pattern, additionally verifies GT master hash |
| No oracle ceiling check | Oracle ceiling: B4 must achieve PMC_AUROC ≥ 0.90 (AT-5) |

The most important addition is the oracle ceiling check (AT-5, BV-4). In Phase 8B,
the benchmark validity check BV-3 (B4 direct-AUROC ≥ 0.52) FAILED — meaning the oracle
baseline did not work at all. This is a fundamental validity problem that was only detected
post-hoc. In Phase 9B, the oracle ceiling is verified before the framework is evaluated,
and evaluation is blocked if it fails.
