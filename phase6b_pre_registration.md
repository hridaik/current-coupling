# Phase 6B — Pre-Registration Document

## Purpose

This document constitutes the formal pre-registration of the Phase 6A benchmark.
All quantities listed here are immutable after the hash lock step.

Pre-registration prevents: post-hoc threshold adjustment, outcome-driven label changes,
selective reporting, and any form of "looking at results and fixing the labels."

---

## 1. Frozen Quantities

The following become immutable at the moment of hash commitment (Step 3 of the hash
lock protocol).

### 1.1 Network construction

| Quantity | Frozen value |
|---|---|
| Coupling matrix A_sparse | Full 140×140 matrix; exact entries frozen |
| Sparsity pattern of A_sparse | Exact binary pattern; determined by master_seed=42 |
| A[k,k] self-inhibition | -1.5 for all k |
| Module assignments | {1-25}=M1, {26-50}=M2, {51-75}=M3, {76-100}=M4 |
| H1 assignments | {101-108}=M1 H1, ..., {125-132}=M4 H1 |
| H2 assignments | Indices 133-140 with target modules per architecture spec |
| SA set | {133, 134, 135, 136, 137, 138, 139, 140} |
| D matrix | D_diag + D_lr with d_0=1.0, ε_lr=0.1, u from sub-seed 48 |

### 1.2 Ground-truth labels

| Quantity | Frozen value |
|---|---|
| Label(i→j) for all 9,900 pairs | {S, C, M, N} per label generation spec |
| Witnessing H2 index for each C/M label | Recorded at generation time |
| DIRECT(i→j) for all pairs | Binary, frozen from A_sparse |
| SAREACHABLE(i→j) for all pairs | Binary, frozen from A_sparse and SA |
| SHA-256 hash of label file | **[TO BE FILLED AT COMMIT TIME]** |

### 1.3 Primary metrics and thresholds

| Quantity | Frozen value |
|---|---|
| Primary metric | C-recall, C-precision, S↔C confusion rate (non-null pairs) |
| Non-null evaluation set | Pairs labeled S, C, or M only |
| Success criterion — C-recall | ≥ 0.50 (oracle_z condition) |
| Success criterion — C-precision | ≥ 0.50 (oracle_z condition) |
| Success criterion — S↔C confusion | ≤ 0.20 (oracle_z condition) |
| Partial success criterion | Any 1 of 3 primary criteria met |
| Failure criterion | C-recall < 0.30 AND C-precision < 0.30 |
| Inconclusive criterion | CRITICAL failure mode triggered (CF1, CF2, DF2, SF1 not plateaued) |
| AUROC evaluation set | Non-null pairs only (S ∪ C ∪ M) |
| S↔C confusion rate definition | (C pairs classified S + S pairs classified C) / (|C|+|S|) |

### 1.4 Baselines (computed before any framework output is evaluated)

| Baseline | Definition |
|---|---|
| Random classifier | Assigns each label with probability equal to its class frequency |
| Module classifier | Labels (i,j) as S if i and j in same module and p_within>0 else N; no activity data |
| Glasso baseline | Per-state Glasso precision estimate; assigns S from average Ω̂, C from ΔΩ̂ threshold |

All three baselines are computed on the same data as the framework, before framework
outputs are evaluated.

### 1.5 Evaluation conditions

The following conditions are pre-registered and must all be reported:

| Condition | γ_H2 | D state-dep. | y(t) | z(t) provided |
|---|---|---|---|---|
| `oracle_z` (primary) | 3.0 | No | calcium | Yes |
| `blind_z` | 3.0 | No | calcium | No |
| `neural_state` | 3.0 | No | x_obs(t) directly | Yes |
| `weak_z` | 1.5 | No | calcium | Yes |
| `strong_z` | 6.0 | No | calcium | Yes |

---

## 2. Forbidden Actions

The following actions are **prohibited** after the hash lock step and constitute
protocol violations that invalidate the benchmark:

### 2.1 Label modifications

- Changing the definition of DIRECT(i→j) or SAREACHABLE(i→j)
- Changing the label assignment rules (S/C/M/N)
- Re-running label generation with a different A_sparse or different parameters
- Adding, removing, or merging label categories
- Changing the S/M threshold, S/C threshold, or any threshold that determines labels
- Changing the LR handling (currently: no LR class; this decision is frozen)

### 2.2 Metric modifications

- Changing the success/failure/inconclusive criteria after seeing any results
- Changing the definition of the evaluation set (non-null pairs)
- Adding new primary metrics after seeing results
- Removing pre-registered baselines from the reported comparison
- Reporting only the best-performing evaluation condition without reporting all conditions
- Reporting per-class metrics only for classes where the framework performs well

### 2.3 Graph modifications

- Changing A_sparse or its sparsity pattern
- Changing H2 topology (target module assignments)
- Changing the SA set
- Changing which neurons are observed vs. hidden

### 2.4 State and dynamics modifications

- Changing γ_H2 (the primary γ_H2 = 3.0 value)
- Changing the functional form of B(z) (currently B_h(z) = γ_H2 × z for h ∈ SA)
- Adding gain modulation (A is fixed; this is frozen)
- Making D state-dependent in the primary condition

### 2.5 Post-hoc tuning

- Tuning any framework hyperparameter (regularization, bandwidth, threshold) using
  knowledge of which pairs are labeled C, S, M, or N
- Re-running the framework with modified hyperparameters after seeing class-specific
  performance breakdowns
- Adding framework components that specifically target the known failure modes of this
  benchmark (e.g., a module-boundary correction added because of the module-classifier
  baseline comparison)

---

## 3. Allowed Actions

The following actions are permitted after the hash lock, provided they are documented
and do not alter scientific content:

### 3.1 Implementation corrections

- Fixing numerical bugs in the simulation code (e.g., incorrect array indexing,
  wrong dt applied to noise term) **provided the fix does not change the scientific
  design intent**
- Fixing numerical bugs in the label generation code **provided the fix does not change
  label values for any pair** (i.e., the bug was in bookkeeping, not in DIRECT or
  SAREACHABLE computation)

If a bug fix changes label values for any pair, it constitutes a label modification.
The corrected labels must be regenerated, re-hashed, and a new pre-registration issued.
The original pre-registration and its hash must be retained in the record.

### 3.2 Numerical stabilization

- Adjusting the Euler-Maruyama step dt downward (e.g., 0.10 → 0.05) if numerical
  instability is detected, **provided all conditions use the same dt**
- Increasing the warm-up period T_warmup if non-stationarity is detected

### 3.3 Additional conditions (supplementary, not primary)

- Running additional evaluation conditions beyond the five pre-registered conditions
  **provided these are clearly labeled "supplementary" and not used to determine
  the primary pass/fail outcome**

### 3.4 Diagnostic analyses

- Running any diagnostic analysis described in the failure mode registry
- Computing baselines not listed in Section 1.4 **provided these are reported as
  supplementary and the pre-registered baselines are also reported**

---

## 4. Evaluation Firewall

The evaluation is divided into three sides. Each side has defined access permissions.

### 4.1 Simulator side

The simulator side has access to:
- All construction parameters (A_sparse, D, γ_H2, θ_z, σ_z, etc.)
- The true latent state z(t) for all runs
- The full neural state x(t) including hidden neurons
- The calcium observation y(t)

The simulator side **must not** provide to the framework side:
- A_sparse or any block of A
- D or any component of D
- The identity of hidden neurons (H1, H2, or which indices are unobserved)
- The labels or any label-derived statistics

The simulator side **provides to the framework side** (per condition):
- y^(r)(t): calcium traces for observed neurons
- z^(r)(t): latent state (oracle_z condition only)
- The metadata: T_eff, N_obs, dt

### 4.2 Framework side

The framework side has access to:
- Everything provided by the simulator side for the active condition
- No other information

The framework side produces:
- ĉ(i→j) ∈ {S, C, M, N}: discrete classification per pair, at a pre-specified threshold
- s_S(i→j), s_C(i→j), s_M(i→j), s_N(i→j): continuous scores per class

The framework side **must not**:
- Access labels or the SHA-256 hash of the label file before outputting classifications
- Access A_sparse, H2 topology, or module structure
- Tune hyperparameters based on knowledge of the label distribution or any class-specific
  performance feedback

### 4.3 Audit side

The audit side has access to:
- The locked label file (post-hash-verification)
- The framework output files (saved before label revelation)
- The pre-registration document (this document)

The audit side computes all pre-registered metrics and produces the final report.

The audit side **verifies**:
- SHA-256 hash of label file matches pre-registration record
- Framework output file timestamps predate label file revelation
- All pre-registered conditions and baselines are reported

---

## 5. Hash Lock Protocol

Execute the following steps in order. Steps must be timestamped and logged.

**Step 1 — Construct the network**

Generate A_sparse using master_seed=42 and all parameters from `phase6b_parameter_registry.md`.
Run the post-generation stability check (spectral abscissa < -0.1). Record the spectral
abscissa and any resampling events.

**Step 2 — Generate labels**

Run the label generation algorithm from `phase6b_label_generation_spec.md` on the
constructed A_sparse. Record: DIRECT(i→j), SAREACHABLE(i→j), and Label(i→j) for all
9,900 pairs. Record witnessing H2 index for each C/M pair.

Run sanity checks LG1–LG4. Record outcomes.

**Step 3 — Serialize and hash**

Serialize the label file to a canonical deterministic format:

```
JSON array, sorted by (i, j) lexicographically:
[{"i": 0, "j": 1, "direct": 0, "sareachable": 1, "label": "C", "witness_h2": 132}, ...]
```

(Using 0-indexed neuron numbers in the serialized file.)

Compute SHA-256:

```bash
sha256sum labels.json > labels.sha256
```

Record the hash value here: **[HASH TO BE FILLED AT COMMIT TIME]**

**Step 4 — Commit and freeze**

Commit `labels.json` and `labels.sha256` to version control. Record the commit hash.
The git commit hash serves as the timestamp proof.

**Step 5 — Run simulations**

Run all five evaluation conditions (Section 1.5) with R=5 runs each.
Save all framework outputs with creation timestamps.
Do not open the label file during this step.

**Step 6 — Framework analysis**

Apply the framework to all conditions. Save classification outputs to files with creation
timestamps. All output files must be saved before Step 7.

**Step 7 — Reveal labels and verify**

Open `labels.sha256` and recompute `sha256sum labels.json`.
Verify the hashes match. If they do not match, the label file has been tampered with
and the evaluation is invalid.

Record the verification result and timestamp.

**Step 8 — Compute metrics and report**

The audit side computes all pre-registered metrics using the verified labels and the
framework outputs. Report all conditions (primary + supplementary). Report all
pre-registered baselines.

---

## 6. Deviations from Phase 6A Protocol

The following deviations from the Phase 6A protocol recommendations are pre-registered.
Each deviation must be justified and its consequence documented.

| Deviation | Phase 6A recommended | Phase 6B decision | Justification | Risk |
|---|---|---|---|---|
| No A_lr | Include 2–3 rank global modes | A = A_sparse only | Eliminates L3, IF2; no loss of S/C conceptual test | Lower realism; extend to Phase 6B+ |
| D constant | State-dependent D(z) | D fixed | Eliminates DF5; z enters only via B(z) | Some loss of realism; noise state-dependence deferred |
| No gain modulation | Modulate recurrent gain | No gain modulation | Eliminates W13, makes label computation exact | Less "recurrent flow" character; H2-relay mechanism only |
| Scalar z | Unspecified dimensionality | dim_z = 1 | Eliminates W12 (z-component interaction) | Single arousal mode; cannot test multi-dimensional modulation |
| H2 no self-connections | Unspecified | H2-H2 = 0, H1-H2 = 0 | Makes SAREACHABLE exact 2-hop computation | Simpler H2 structure; chain-H2 effects excluded |

---

## 7. Post-Hoc Analysis Permissions

The following analyses are explicitly permitted after seeing results, provided they are
clearly labeled as post-hoc and do not affect the primary pass/fail determination:

1. Investigating which H2 neurons are responsible for the most framework errors
2. Computing performance stratified by connection weight magnitude
3. Computing performance as a function of path length through H2
4. Investigating whether within-module C vs. between-module C have different detection rates
5. Investigating the D_lr alignment with A_sparse (IF3 check)

These post-hoc analyses may inform Phase 6C design but do not modify Phase 6A conclusions.
