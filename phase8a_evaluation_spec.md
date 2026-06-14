# Phase 8A Evaluation Specification
**Status:** PRE-REGISTERED — frozen before framework execution  
**Date:** 2026-06-13  
**Supersedes:** phase6a_validation_plan.md (which contained underspecified degrees of freedom)

This document completely specifies the evaluation protocol. Every decision made here is final. No decision may be revisited after framework outputs are observed.

---

## 1. Evaluation Unit

**The evaluation unit is the directed ordered pair (i, j), i ≠ j, i, j ∈ {0, …, 99}.**

There are 9,900 such pairs. Each pair has exactly one ground-truth label ∈ {S, C, M, N} committed in `ground_truth/labels.json` (hash: `dc99697e…`).

**Rationale:** The current-velocity framework makes claims about directed functional links between observed neurons. The SAREACHABLE criterion defines link labels in terms of directed paths (i→h→j). The natural evaluation unit must therefore be the directed pair. Undirected evaluation would collapse S and M with their reversal, which are distinct by the label definition.

Evaluation does NOT aggregate to neuron level, module level, or condition level as primary analysis. Condition-level comparison is a secondary analysis (see §6).

---

## 2. Inputs Available to the Framework

The framework is treated as a black box. It receives a fixed set of files and nothing else. The evaluation code enforces this by providing a sandboxed input bundle.

### 2.1 Allowed Inputs

| Input | Format | Condition | Rationale |
|-------|--------|-----------|-----------|
| Observed calcium traces `y(t)` | float64 ndarray (T_eff × N_obs) = (48000 × 100) | All conditions | Primary observable; what the framework is designed to analyze |
| Oracle latent state `z_oracle(t)` | float64 ndarray (T_eff,) | oracle_z, neural_state, weak_z, strong_z only | Per experimental condition; blind_z condition withholds this |
| Neuron index set | list of int, range(100) | All conditions | Identifies which indices are observed neurons |
| Run indices | list of int, range(5) | All conditions | Identifies which runs are independent; allows across-run aggregation |
| Condition name | string | All conditions | Identifies which evaluation condition the data comes from |
| Temporal metadata | dt=0.10, T_eff=48000 | All conditions | Time base; necessary for any temporal analysis |
| Number of conditions | integer = 5 | All conditions | Structural information about the experiment design |

**The framework may access multiple runs and must aggregate or use them as it sees fit. It must produce one output per directed pair, not one per run.**

### 2.2 Forbidden Inputs — Complete List

The following are forbidden. Any framework access to these constitutes a protocol violation and invalidates the evaluation.

| Forbidden Item | Why Forbidden |
|---------------|---------------|
| `ground_truth/labels.json` | Ground-truth labels; direct leakage |
| `ground_truth/A_sparse.npy` | Full coupling matrix; INV-I1 |
| Any submatrix of A (DIRECT matrix, A[j,i] entries) | Derivable from A_sparse; still forbidden |
| DIRECT indicator matrix | Encodes A_sparse sparsity pattern |
| SAREACHABLE indicator matrix | Encodes label derivation directly |
| H2 neuron membership (SA set, indices 132–139) | INV-I2; topology leakage |
| H2 target module assignments (H2_TARGETS) | INV-I2 |
| H1 neuron membership or structure | INV-I2 by analogy |
| `ground_truth/A_sparse.sha256` | Reveals A_sparse hash |
| `ground_truth/construction_params.json` | Reveals network parameters |
| D diffusion matrix or any submatrix | INV-I3 |
| `results/phase7c/canonical/metadata.json` | Contains seed policy, parameter values |
| `results/phase7c/canonical/hashes.json` | Reveals dataset provenance metadata |
| Any Phase 7B or 7C intermediate files | Contain A_sparse, labels, parameters |
| `scripts/phase7b/config.py` | Contains all 34 parameters including SA |
| Spectral abscissa of A | Derived from A_sparse |
| Module membership indices | The framework does NOT know which neurons belong to which module |
| Expected class counts | Would reveal label distribution before evaluation |
| `audit_log.jsonl` | May contain label-related events |

**Note on module membership:** Neuron indices 0–99 are provided, but the module structure (M1={0..24}, M2={25..49}, etc.) is NOT disclosed. The framework must infer any structure from the observed dynamics. This is critical: module membership is derivable from the index structure (contiguous blocks of 25), so module-aware analyses by the framework would constitute partial topology leakage. This is recorded as Vulnerability V-E1 in the leakage audit.

### 2.3 Input Bundle Specification

The evaluation infrastructure provides the framework with a structured input bundle:

```python
{
    'condition': str,               # 'oracle_z', 'blind_z', etc.
    'n_obs': 100,
    'n_runs': 5,
    'dt': 0.10,
    't_eff': 48000,
    'runs': [
        {
            'run_index': int,
            'y': np.ndarray,        # (48000, 100) float64
            'z_oracle': np.ndarray  # (48000,) float64, or None if blind_z
        },
        ...
    ]
}
```

No other information is present in the bundle.

---

## 3. Framework Output Schema

The framework must produce exactly the following for each condition it is evaluated on.

### 3.1 Required Output — Per Directed Pair

For every ordered pair (i, j), i ≠ j, i, j ∈ {0, …, 99}, the framework must produce:

```python
{
    'i': int,            # source neuron index, 0-indexed
    'j': int,            # target neuron index, 0-indexed
    'class_prob': {
        'S': float,      # P(label=S | pair (i,j)), ≥ 0
        'C': float,      # P(label=C | pair (i,j)), ≥ 0
        'M': float,      # P(label=M | pair (i,j)), ≥ 0
        'N': float,      # P(label=N | pair (i,j)), ≥ 0
        # sum must equal 1.0 (±1e-6)
    },
    'class_pred': str,   # argmax of class_prob; ∈ {'S','C','M','N'}
}
```

**All 9,900 pairs must be present. No pairs may be omitted.**

**class_prob values must be non-negative and sum to 1.0 (±1e-6 tolerance). If the framework cannot produce calibrated probabilities, it must produce a score vector and normalize (softmax or simplex projection). The normalization method must be declared in the framework's output metadata.**

### 3.2 Optional Supplementary Outputs — Raw Feature Scores

The framework may additionally produce raw continuous scores that map to the classification:

```python
{
    'i': int,
    'j': int,
    'raw_scores': {
        'q_directed': float,      # directed current or flow estimate Q[i,j]
        'omega_partial': float,   # precision matrix entry or partial correlation
        'delta_omega': float,     # change in precision with z vs without z
        # any additional framework-specific scores
    }
}
```

These supplementary scores are used for secondary metric evaluation only. They are never used to alter primary metric outcomes.

### 3.3 Output Metadata

```python
{
    'framework_name': str,
    'framework_version': str,
    'condition': str,
    'output_timestamp': str,      # ISO 8601
    'normalization_method': str,  # how class_prob was obtained
    'n_pairs': 9900,
    'framework_commit': str,      # code version if applicable
}
```

### 3.4 Output Freeze

The framework must write its output to a designated file before any evaluation code is run. The output file path is specified by the evaluation harness. The framework may not modify its output after writing.

The evaluation harness computes a SHA-256 hash of the output file immediately after writing and logs it to the evaluation audit log. This hash is the output fingerprint.

---

## 4. Evaluation Conditions

The framework is evaluated on all 5 pre-specified conditions. The oracle_z condition is the **primary condition** for success/failure determination.

| Condition | gamma_H2 | z provided | Obs model | Role |
|-----------|----------|------------|-----------|------|
| `oracle_z` | 3.00 | Yes | Calcium | PRIMARY — determines framework verdict |
| `blind_z` | 3.00 | No | Calcium | SECONDARY — tests whether z access is required |
| `neural_state` | 3.00 | Yes | Raw softplus | SECONDARY — tests calcium model sensitivity |
| `weak_z` | 1.50 | Yes | Calcium | SECONDARY — tests SNR dependence |
| `strong_z` | 6.00 | Yes | Calcium | SECONDARY — tests SNR dependence |

**Primary success/failure is determined from `oracle_z` condition only.**  
Secondary conditions are used for interpretive analysis after the primary verdict is recorded.

---

## 5. Evaluation Order

1. Framework receives input bundle for `oracle_z` condition
2. Framework writes output for `oracle_z`; output hash recorded
3. Primary metrics computed (§phase8a_metric_registry.md); success/failure verdict recorded
4. Verdict is frozen
5. Framework receives input bundles for remaining 4 conditions
6. Framework writes outputs; output hashes recorded
7. Secondary metrics computed for all 5 conditions
8. Full report written

Steps 3–4 must occur before step 5. The oracle_z verdict cannot be revised based on secondary condition results.

---

## 6. Secondary Analyses (Pre-specified)

These analyses are permitted but do not alter the primary verdict:

| Analysis | Description | Purpose |
|----------|-------------|---------|
| Condition comparison | Primary metric vs condition (oracle_z baseline) | Tests z-access dependency |
| Per-class performance profile | AUROC per class per condition | Identifies which link types drive performance |
| Run-level variance | Metric variance across 5 runs | Assesses stability |
| LR binary reduction | C+M vs S+N AUROC | Tests latent-regulation detection |
| Direct binary reduction | S+M vs C+N AUROC | Tests structural link detection |
| Between-condition ΔMetric | oracle_z minus blind_z per metric | Tests information value of z |
