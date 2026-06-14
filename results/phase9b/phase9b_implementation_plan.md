# Phase 9B — Implementation Plan

**Status:** PLANNING ONLY. No code written. No data generated.  
**Pre-condition:** All ambiguities in phase9b_protocol_recovery.md Section 9 (A1–A7) must
be resolved and locked before any code in this plan is executed.

---

## Overview

The implementation consists of four stages executed in strict sequential order:

```
Stage 1: Ground-truth generation     (simulator + Lyapunov oracle)
Stage 2: Trajectory generation       (not needed for primary evaluation — see note)
Stage 3: Baseline evaluation
Stage 4: Framework evaluation
Stage 5: Secondary metrics
Stage 6: Verdict generation
```

**Note on Stage 2:** The primary metrics (rank correlation ρ with oracle, PMC_AUROC,
Precision@k) require only the framework's estimated ΔΩ and the oracle GT objects.
The framework estimates ΔΩ from neural trajectories. Trajectories must be generated
(Stage 2) before the framework can produce estimates.

**No stage may begin before the preceding stage is complete and hash-locked.**

---

## Stage 1: Ground-Truth Generation

### 1.1 Parameter Lock

Before generating anything, write and lock:

```
scripts/phase9b/config9b.py
```

Contents:

```python
# Network parameters — FROZEN
N_OBS       = 150
N_H_LOCAL   = 20
N_H_GLOBAL  = 10
N_HIDDEN    = 30
N_TOTAL     = 180

MODULES = {
    'M1': list(range(0, 40)),        # PMC sources drawn from here
    'M2': list(range(40, 80)),
    'M3': list(range(80, 115)),       # PMC targets drawn from here
    'M4': list(range(115, 150)),      # PMC targets drawn from here
}

# PMC membership — MUST be committed before generating A
PMC_SOURCE_INDICES = [...]   # 8 indices from M1, committed here
PMC_TARGET_INDICES = [...]   # 12 indices from M3+M4, committed here
H_GLOBAL_INDICES   = [...]   # 10 indices in hidden space

# Connectivity probabilities — FROZEN
P_WITHIN   = 0.12
P_BETWEEN  = 0.02
P_LOCAL    = 0.15
P_GLOBAL   = 0.10
WEIGHT_STD = 0.30

# PMC connectivity rules — FROZEN
PMC_SRC_MIN_H_GLOBAL_PROJECTIONS = 3   # each source projects to ≥3 H_global
PMC_TGT_MIN_H_GLOBAL_INPUTS      = 4   # each target receives from ≥4 H_global

# State parameters — FROZEN after D1 verification
THETA_Z    = ...   # OU mean-reversion rate
SIGMA_Z    = ...   # OU noise amplitude
G_BASE     = ...   # H_global baseline gain
G_MOD      = ...   # H_global state modulation coefficient
Z_HIGH     = ...   # locked after D1 verification

# Diffusion parameters — FROZEN
G_D = ...   # diffusion elevation at PMC sources in State A

# Trajectory parameters — FROZEN
T_STATE_A  = ...   # timesteps in State A for framework evaluation
T_STATE_B  = ...   # timesteps in State B for framework evaluation
RNG_SEED   = 42    # global random seed

# Structural lesion definition — FROZEN
LESION_EDGES = 'M1_to_M2_directed'  # edges removed for GT5b
```

This file is hash-locked immediately after completion. Any change to config9b.py
invalidates all subsequent outputs.

### 1.2 Coupling Matrix Construction

**Script:** `scripts/phase9b/build_network.py`

```
INPUTS:  config9b.py
OUTPUTS: results/phase9b/ground_truth/A_full.npy     (N_TOTAL × N_TOTAL coupling matrix)
         results/phase9b/ground_truth/A_obs.npy      (N_OBS × N_OBS observed block)
         results/phase9b/ground_truth/network_spec.json  (indices, module assignments)
         results/phase9b/ground_truth/network_spec.json.sha256
```

**Construction procedure:**

1. Set RNG to RNG_SEED.
2. Build A_full block by block:
   - Observed-observed block (150×150): sparse random edges per p_within / p_between rules
   - H_local → observed: sparse per p_local, within-module only
   - H_global → observed: sparse per p_global, but PMC connectivity rules enforced:
     * For each PMC source: ensure ≥ PMC_SRC_MIN_H_GLOBAL_PROJECTIONS connections to H_global
     * For each PMC target: ensure ≥ PMC_TGT_MIN_H_GLOBAL_INPUTS connections from H_global
   - Zero out any A_full[i,j] for i ∈ PMC_source_indices, j ∈ PMC_target_indices
     (enforce construction rule: no direct PMC source-target edges)
3. Scale edge weights to achieve all eigenvalues in (-1, 0) via spectral scaling.
4. Extract A_obs = A_full[:N_OBS, :N_OBS].

**Acceptance test AT-1:**
```
All eigenvalues of A_full in (-1, 0)
A_full[PMC_source_indices, PMC_target_indices] == 0 exactly
For each PMC source i: sum(A_full[H_global_indices, i] != 0) >= 3
For each PMC target j: sum(A_full[j, H_global_indices] != 0) >= 4
```

### 1.3 Lyapunov Oracle — State A

**Script:** `scripts/phase9b/lyapunov_oracle.py`

**Mathematical procedure:**

For state s ∈ {A, B}:
```
1. Build effective coupling A_eff_s:
     For State A: A_eff_A = A_full, with H_global gain scaled by (g_base + g_mod × z_high)
     For State B: A_eff_B = A_full, with H_global gain scaled by g_base (z=0)
     Implementation: scale the columns of A_eff corresponding to H_global neurons by
     the effective gain factor relative to nominal.

2. Build diffusion D_s:
     D_B = diag(d_base_i)       for i = 0..N_OBS-1
     D_A = D_B + g_D × z_high × D_PMC_src
     where D_PMC_src is diagonal with 1 at PMC source indices, 0 elsewhere.
     (D is defined only for the observed block; full-system D has corresponding structure)

3. Solve Lyapunov equation for the full N_TOTAL × N_TOTAL system:
     A_eff_s × Sigma_s + Sigma_s × A_eff_s^T + 2 × D_full_s = 0
     using scipy.linalg.solve_continuous_lyapunov or equivalent.
     This gives the stationary covariance Sigma_s (N_TOTAL × N_TOTAL).

4. Extract observed-observed block:
     Sigma_obs_s = Sigma_s[:N_OBS, :N_OBS]

5. Compute precision:
     Q_s = inv(Sigma_obs_s)  [N_OBS × N_OBS, observed block only]

6. Compute current organization:
     Omega_s = D_s_obs × Q_s + A_obs
     where D_s_obs is the observed-observed diffusion matrix.

7. Compute current difference:
     DeltaOmega_true = Omega_A - Omega_B
     Note: A_obs cancels because it is state-invariant.
```

**OUTPUTS:**
```
results/phase9b/ground_truth/Sigma_A_obs.npy       (150×150)
results/phase9b/ground_truth/Sigma_B_obs.npy       (150×150)
results/phase9b/ground_truth/Q_A_obs.npy           (150×150)
results/phase9b/ground_truth/Q_B_obs.npy           (150×150)
results/phase9b/ground_truth/Omega_A_obs.npy       (150×150)
results/phase9b/ground_truth/Omega_B_obs.npy       (150×150)
results/phase9b/ground_truth/DeltaOmega_true.npy   (150×150)  ← GT1
results/phase9b/ground_truth/oracle_manifest.json
results/phase9b/ground_truth/oracle_manifest.json.sha256
```

**Acceptance test AT-2:**
```
Sigma_A_obs and Sigma_B_obs are symmetric positive-definite
max(|Sigma_obs - Sigma_obs^T|) < 1e-10
condition_number(Sigma_obs) < 1e8
A_obs cancellation verified: Omega_A - D_A @ Q_A - A_obs == 0 (within 1e-10)
DeltaOmega_true symmetric (expected since D and Q symmetric)
```

### 1.4 Dominance Condition Verification

**Script:** `scripts/phase9b/verify_dominance.py`

```
1. Load DeltaOmega_true.npy
2. Build off-connectome mask: M_off[i,j] = 1 iff A_obs[i,j] == 0 and i != j
3. Compute |DeltaOmega_true_off[i,j]| for all off-connectome (i,j)
4. Compute PMC_mask: 1 iff (i,j) is a PMC source-target pair
5. Check D1:
     pmc_median     = median of |DeltaOmega_true_off| over PMC pairs
     nonpmc_p90     = 90th percentile of |DeltaOmega_true_off| over non-PMC off-connectome
     D1_satisfied   = (pmc_median > 2 × nonpmc_p90)
6. Check D2:
     top50_oracle   = top 50 off-connectome pairs by |DeltaOmega_true_off|
     pmc_in_top50   = count of PMC pairs in top50_oracle
     D2_satisfied   = (pmc_in_top50 / 50 >= 0.60)
7. If D1 or D2 fails: HALT. Return to config9b.py and increase Z_HIGH. Re-run from 1.3.
8. If both pass: write dominance_report.json and hash-lock.
```

**OUTPUTS:**
```
results/phase9b/ground_truth/dominance_report.json
  {D1_satisfied: bool, D2_satisfied: bool, pmc_median: float, nonpmc_p90: float,
   pmc_in_top50: int, z_high_used: float}
results/phase9b/ground_truth/dominance_report.json.sha256
```

**GATE:** No Stage 1.5 or Stage 2 proceeds until D1 and D2 are both True.

### 1.5 Oracle Object Generation

**Script:** `scripts/phase9b/build_oracle.py`

```
INPUTS:  DeltaOmega_true.npy, A_obs.npy, network_spec.json
OUTPUTS: results/phase9b/ground_truth/GT1_DeltaOmega_off.npy   (10995 × 3: [i, j, value])
         results/phase9b/ground_truth/GT2_PMC_pairs.npy        (96 × 2: [i, j])
         results/phase9b/ground_truth/GT3_oracle_ranking.npy   (10995 × 2: [pair_idx, rank])
         results/phase9b/ground_truth/GT4_communities.json     ({C_src: [...], C_tgt: [...], background: [...]})
         results/phase9b/ground_truth/GT5a_state_lesion_ranking.npy
         results/phase9b/ground_truth/GT5b_structural_lesion_ranking.npy
         results/phase9b/ground_truth/oracle_objects.json.sha256
```

**GT1 construction:**
```
Extract upper-triangle off-connectome pairs (i,j) with A_obs[i,j]==0 and i<j.
Record (i, j, DeltaOmega_true[i,j]) for each. (If directed, record all pairs with i!=j.)
```

**GT3 construction:**
```
Sort GT1 pairs by |DeltaOmega_true[i,j]| descending. Assign rank 1 to largest.
```

**GT4 construction:**
```
C_src = PMC_SOURCE_INDICES
C_tgt = PMC_TARGET_INDICES
background = all other observed neurons
```

**GT5a construction:**
```
Compute Omega_B0 = D_B @ Q_B0 + A_obs, where Q_B0 = inv(Sigma_obs at z=z_high, D=D_B)
(Same A, z=z_high dynamics, but using baseline diffusion D_B instead of D_A)
Wait — this is the state lesion: z set to 0. So:
Omega_B0 = D_B @ Q_B + A_obs (already computed in oracle)
ΔΩ_state_lesion = Omega_A - Omega_B0
The top of |ΔΩ_state_lesion| should be dominated by PMC pairs.
```

**GT5b construction:**
```
Build A_lesioned = A_full with M1→M2 directed edges zeroed out.
Solve Lyapunov for A_lesioned at State A (z=z_high, D=D_A).
Compute Omega_A_lesioned = D_A @ Q_A_lesioned + A_obs_lesioned.
ΔΩ_structural_lesion = Omega_A - Omega_A_lesioned.
The top of |ΔΩ_structural_lesion| should be dominated by M1→M2 structural pairs.
```

### 1.6 Hash-Lock Ground Truth

After completing all of Stage 1:

```python
# Compute master hash of all ground-truth outputs
import hashlib, json, pathlib

GT_FILES = [
    'A_full.npy', 'A_obs.npy', 'DeltaOmega_true.npy',
    'GT1_DeltaOmega_off.npy', 'GT2_PMC_pairs.npy', 'GT3_oracle_ranking.npy',
    'GT4_communities.json', 'GT5a_state_lesion_ranking.npy', 'GT5b_structural_lesion_ranking.npy'
]

# SHA-256 each file, write to ground_truth_manifest.json
# Master hash = SHA-256 of concatenated individual hashes
```

**OUTPUT:**
```
results/phase9b/ground_truth/ground_truth_manifest.json
  {file: sha256, ...}
results/phase9b/ground_truth/ground_truth_master_hash.txt
```

**GATE:** Ground truth manifest must be written and verified before any framework output
is generated. The manifest is the single authoritative record of what the oracle is.

---

## Stage 2: Trajectory Generation

**Script:** `scripts/phase9b/generate_trajectories.py`

The framework needs neural activity time series to estimate ΔΩ.

```
INPUTS:  A_full.npy, config9b.py
OUTPUTS: results/phase9b/trajectories/x_A.npy     (T_STATE_A × N_OBS)
         results/phase9b/trajectories/x_B.npy     (T_STATE_B × N_OBS)
         results/phase9b/trajectories/trajectory_manifest.json
         results/phase9b/trajectories/trajectory_manifest.json.sha256
```

**Generation procedure:**

```
1. For State B (z=0):
   Euler-Maruyama integration of dx = A_eff_B × x × dt + sqrt(2 D_B) × dW
   for T_STATE_B steps, dt=1.
   Keep only observed neurons (indices 0..N_OBS-1). Discard hidden.

2. For State A (z=z_high):
   Set H_global effective gain = g_base + g_mod × z_high.
   Euler-Maruyama integration of dx = A_eff_A × x × dt + sqrt(2 D_A) × dW
   for T_STATE_A steps, dt=1.
   Keep only observed neurons. Discard hidden.

3. Both trajectories use separate RNG streams derived from RNG_SEED.

4. Do NOT provide z(t) to the trajectory output files. Framework receives x only.
```

**Acceptance test AT-3:**
```
Sample covariance Cov(x_A) ≈ Sigma_A_obs within tolerance (|rho_Spearman - 1| < 0.05)
Sample covariance Cov(x_B) ≈ Sigma_B_obs within tolerance
If tolerance not met: increase T and re-generate
```

**IMPORTANT:** The trajectory files are generated AFTER the ground-truth manifest is
locked. The framework evaluator receives only x_A.npy, x_B.npy, and A_obs.npy.
They do not receive any ground-truth file.

---

## Stage 3: Baseline Evaluation

**Script:** `scripts/phase9b/evaluate_baselines.py`

All baselines are evaluated and their metrics computed before the framework is evaluated.

```
INPUTS:  x_A.npy, x_B.npy, A_obs.npy, GT2_PMC_pairs.npy, GT3_oracle_ranking.npy
OUTPUTS: results/phase9b/baselines/baseline_metrics.json
         results/phase9b/baselines/baseline_metrics.json.sha256
```

### B1: Random Ranking

```python
import numpy as np
rng = np.random.default_rng(seed=RNG_SEED + 1)
random_scores = rng.permutation(n_off_connectome_pairs)
```

### B2: ΔCorr Baseline

```python
corr_A = np.corrcoef(x_A.T)  # (150, 150)
corr_B = np.corrcoef(x_B.T)  # (150, 150)
delta_corr = np.abs(corr_A - corr_B)
# Restrict to off-connectome pairs
b2_scores = delta_corr[off_connectome_mask]
```

### B3: Glasso Pooled

```python
from sklearn.covariance import GraphicalLassoCV
x_pooled = np.vstack([x_A, x_B])
model = GraphicalLassoCV()
model.fit(x_pooled)
Q_pooled = model.precision_
b3_scores = np.abs(Q_pooled[off_connectome_mask])
```

### B4: Oracle Bound

```python
# Load GT1 directly as the ranking signal
oracle_scores = np.abs(DeltaOmega_true_off)  # loaded from GT1
```

For each baseline, compute M1 (Precision@k at k=20,50,100), M2 (rank correlation ρ),
M3 (PMC_AUROC) using the shared evaluation functions defined in Stage 4.

---

## Stage 4: Framework Evaluation

**Script:** `scripts/phase9b/evaluate_framework.py`

```
INPUTS:  x_A.npy, x_B.npy, A_obs.npy
         (No ground-truth files are loaded by this script)
OUTPUTS: results/phase9b/framework/DeltaOmega_estimated.npy   (150×150)
         results/phase9b/framework/framework_scores_off.npy   (n_pairs × 3: [i, j, score])
         results/phase9b/framework/framework_manifest.json
         results/phase9b/framework/framework_manifest.json.sha256
```

The framework's task:

```
1. Estimate Q_A from x_A (N_OBS × N_OBS precision matrix, State A)
2. Estimate Q_B from x_B (N_OBS × N_OBS precision matrix, State B)
3. Estimate D_A from x_A (diffusion matrix)
4. Estimate D_B from x_B (diffusion matrix)
5. Compute Omega_A_hat = D_A_hat @ Q_A_hat + A_obs
6. Compute Omega_B_hat = D_B_hat @ Q_B_hat + A_obs
7. Compute DeltaOmega_estimated = Omega_A_hat - Omega_B_hat
8. For each off-connectome pair (i,j): record |DeltaOmega_estimated[i,j]| as the score
```

The framework script is evaluated in isolation. It does not import or read any ground-truth file.

**After framework produces output:**

Merge framework scores with GT2/GT3 to compute metrics (in a separate evaluation script).

### 4.1 Evaluation Function Library

**Module:** `scripts/phase9b/evaluation_lib.py`

Shared functions used by both baseline and framework evaluation:

```python
def compute_precision_at_k(scores_off, pmc_binary, k):
    """
    scores_off: array of length n_off_pairs
    pmc_binary: binary array, 1 if PMC pair
    k: int
    Returns: Precision@k = fraction of top-k pairs that are PMC
    """
    top_k_idx = np.argsort(scores_off)[::-1][:k]
    return pmc_binary[top_k_idx].sum() / k


def compute_rank_correlation(scores_off, oracle_values_off):
    """
    Spearman correlation between estimated ranking and oracle ranking.
    scores_off:        framework scores for off-connectome pairs
    oracle_values_off: |DeltaOmega_true| for off-connectome pairs
    Both must be indexed identically.
    Returns: Spearman rho
    """
    from scipy.stats import spearmanr
    rho, pval = spearmanr(scores_off, oracle_values_off)
    return rho, pval


def compute_pmc_auroc(scores_off, pmc_binary):
    """
    AUROC for binary PMC label among off-connectome pairs.
    Computed using sklearn.metrics.roc_auc_score.
    """
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(pmc_binary, scores_off)


def compute_permutation_null(scores_off, pmc_binary, n_perms=10000, seed=42):
    """
    Simple permutation null: shuffle pmc_binary, recompute PMC_AUROC.
    Returns array of null AUROC values.
    """
    rng = np.random.default_rng(seed)
    null_aurocs = []
    for _ in range(n_perms):
        null_labels = rng.permutation(pmc_binary)
        null_aurocs.append(compute_pmc_auroc(scores_off, null_labels))
    return np.array(null_aurocs)
```

### 4.2 Metric Computation

**Script:** `scripts/phase9b/compute_metrics.py`

```
INPUTS:  framework_scores_off.npy
         GT2_PMC_pairs.npy
         GT3_oracle_ranking.npy
         baseline_metrics.json
OUTPUTS: results/phase9b/metrics/primary_metrics.json
         results/phase9b/metrics/primary_metrics.json.sha256
```

Computes for the framework:
- Precision@20, Precision@50, Precision@100
- ρ (Spearman rank correlation with oracle)
- PMC_AUROC with permutation p-value (10,000 permutations)
- Permutation null 95th percentile and p-value

Also reports all baseline values for comparison.

---

## Stage 5: Secondary Metrics

**Script:** `scripts/phase9b/compute_secondary_metrics.py`

### 5.1 Module Recovery (NMI)

```python
from sklearn.metrics import normalized_mutual_info_score, adjusted_mutual_info_score
from sklearn.cluster import SpectralClustering

# Build off-connectome adjacency matrix from framework scores
M_off = np.zeros((N_OBS, N_OBS))
for i, j, score in framework_scores_off:
    M_off[i,j] = M_off[j,i] = score  # symmetrize

# Spectral clustering with k=3, fixed random state for reproducibility
sc = SpectralClustering(n_clusters=3, affinity='precomputed',
                        random_state=RNG_SEED, n_init=20)
cluster_labels = sc.fit_predict(M_off)

# Ground-truth communities
gt_labels = np.zeros(N_OBS, dtype=int)
gt_labels[PMC_SOURCE_INDICES] = 1  # C_src
gt_labels[PMC_TARGET_INDICES] = 2  # C_tgt
# All others = 0 (background)

NMI = normalized_mutual_info_score(gt_labels, cluster_labels)
AMI = adjusted_mutual_info_score(gt_labels, cluster_labels)
```

### 5.2 Intervention Recovery

```python
# The framework re-estimates DeltaOmega under each intervention condition
# Framework evaluates on:
#   x_A_lesioned: trajectories generated under A_lesioned, z=z_high
#   x_B (already generated): trajectories at z=0

# Compute DeltaOmega_framework_state_lesion:
#   State lesion: compare framework output for x_B vs x_B (trivially 0)
#   Correct definition: compare framework DeltaOmega at z=z_high vs z=0
#   framework_state_lesion_scores = |DeltaOmega_at_z_high - DeltaOmega_at_z0|
#   But DeltaOmega_at_z0 = Omega(z=0,A) - Omega(z=0,A) = 0, trivially
#   
#   Correct operationalization: rerun framework on (x_A, x_B) to get DeltaOmega_AB
#   This is already the state lesion comparison (A=high drive vs B=low drive).
#   State lesion scores = framework's primary DeltaOmega_estimated scores.
#
# Compute DeltaOmega_framework_structural_lesion:
#   Generate x_A_lesioned from A_lesioned at z=z_high
#   Run framework on (x_A, x_A_lesioned) to get structural lesion DeltaOmega
#   structural_lesion_scores = |DeltaOmega_framework on (x_A, x_A_lesioned)|

rho_state = spearmanr(
    framework_state_lesion_scores[off_connectome_mask],
    GT5a_state_lesion_ranking[off_connectome_mask]
).correlation

rho_structural = spearmanr(
    framework_structural_lesion_scores[off_connectome_mask],
    GT5b_structural_lesion_ranking[off_connectome_mask]
).correlation
```

---

## Stage 6: Verdict Generation

**Script:** `scripts/phase9b/verdict.py`

```python
def generate_verdict(primary_metrics):
    p50 = primary_metrics['precision_at_50']
    rho  = primary_metrics['rank_correlation']
    auroc = primary_metrics['pmc_auroc']

    success = p50 >= 0.25 and rho >= 0.40 and auroc >= 0.75
    partial = (p50 >= 0.10 or rho >= 0.15 or auroc >= 0.60) and not success
    failure = p50 < 0.05 and rho < 0.10 and auroc < 0.55

    if success:
        return 'SUCCESS'
    elif partial:
        return 'PARTIAL'
    elif failure:
        return 'FAILURE'
    else:
        return 'INDETERMINATE'  # between failure and partial

verdict_text = generate_verdict(primary_metrics)
```

**OUTPUTS:**
```
results/phase9b/verdict/primary_verdict.json
  {verdict: str, precision_at_50: float, rank_correlation: float, pmc_auroc: float,
   p_value_auroc: float, baseline_b2_auroc: float, exceeds_b2: bool, ...}
results/phase9b/verdict/primary_verdict.json.sha256
```

The verdict script reads only the metric file. It has no access to ground-truth files.

---

## File Structure

```
results/phase9b/
├── ground_truth/
│   ├── A_full.npy
│   ├── A_obs.npy
│   ├── network_spec.json
│   ├── Sigma_A_obs.npy
│   ├── Sigma_B_obs.npy
│   ├── Q_A_obs.npy
│   ├── Q_B_obs.npy
│   ├── Omega_A_obs.npy
│   ├── Omega_B_obs.npy
│   ├── DeltaOmega_true.npy
│   ├── GT1_DeltaOmega_off.npy
│   ├── GT2_PMC_pairs.npy
│   ├── GT3_oracle_ranking.npy
│   ├── GT4_communities.json
│   ├── GT5a_state_lesion_ranking.npy
│   ├── GT5b_structural_lesion_ranking.npy
│   ├── dominance_report.json
│   ├── ground_truth_manifest.json       ← master hash of all GT files
│   └── ground_truth_master_hash.txt
├── trajectories/
│   ├── x_A.npy
│   ├── x_B.npy
│   ├── x_A_lesioned.npy               ← for structural intervention
│   └── trajectory_manifest.json
├── baselines/
│   └── baseline_metrics.json
├── framework/
│   ├── DeltaOmega_estimated.npy
│   ├── framework_scores_off.npy
│   └── framework_manifest.json
├── metrics/
│   └── primary_metrics.json
├── secondary/
│   └── secondary_metrics.json
└── verdict/
    └── primary_verdict.json
```

---

## Metric Computation: Exact Formulae (Frozen)

### M1: Precision@k

```
Input:  ranked_pairs = top-k off-connectome pairs by |ΔΩ_estimated_off| (descending)
        PMC_set      = set of 96 directed PMC source-target pairs
Output: Precision@k = |ranked_pairs ∩ PMC_set| / k

k=20:  Report as Precision@20
k=50:  Primary decision metric. Threshold: ≥0.25 for success, ≥0.10 partial, <0.05 failure
k=100: Report as Precision@100
```

### M2: Rank Correlation ρ

```
Input:  scores_off[i] = |ΔΩ_estimated[pair_i]| for all off-connectome pairs
        oracle_off[i] = |ΔΩ_true[pair_i]| for all off-connectome pairs
        Both arrays indexed over the same set of off-connectome pairs.
Output: Spearman rho = 1 - 6×Σ(d_i²) / (n×(n²-1))
        where d_i = rank(scores_off[i]) - rank(oracle_off[i])
        
Threshold: ≥0.40 success, ≥0.15 partial, <0.10 failure
p-value from scipy.stats.spearmanr
```

### M3: PMC_AUROC

```
Input:  scores_off[i] = |ΔΩ_estimated[pair_i]| for all off-connectome pairs
        pmc_binary[i] = 1 if pair_i ∈ PMC_set, 0 otherwise
        Both over the same off-connectome pair set.
Output: AUROC = sklearn.metrics.roc_auc_score(pmc_binary, scores_off)

Permutation p-value: 10,000 permutations of pmc_binary labels, seed = RNG_SEED+2
p-value = fraction of null AUROCs ≥ observed AUROC

Threshold: ≥0.75 success, ≥0.60 partial, <0.55 failure
```

### M4: NMI_module (Secondary)

```
Input:  cluster_labels[i] from SpectralClustering(k=3) on M_off matrix
        gt_labels[i]: 0=background, 1=C_src, 2=C_tgt
Output: NMI = sklearn.metrics.normalized_mutual_info_score(gt_labels, cluster_labels)

Threshold: ≥0.40 success, ≥0.20 partial, <0.10 failure
```

---

## Acceptance Tests (AT) — Complete List

| ID | Stage | Test | Failure action |
|---|---|---|---|
| AT-1 | 1.2 | All eigenvalues of A_full in (-1,0) | Re-scale weights |
| AT-1b | 1.2 | A_full[PMC_src, PMC_tgt] == 0 exactly | Fix construction |
| AT-1c | 1.2 | PMC H_global connectivity ≥ minimum | Fix construction |
| AT-2 | 1.3 | Sigma_A_obs, Sigma_B_obs symmetric positive-definite | Re-check A stability |
| AT-2b | 1.3 | A_obs cancels in DeltaOmega_true | Verify Lyapunov solution |
| AT-3 | 2 | Sample covariance ≈ Lyapunov covariance (rho > 0.95) | Increase T |
| AT-4 | 1.4 | D1 and D2 both satisfied | Increase z_high, re-run 1.3 |
| AT-5 | 3 | B4 oracle achieves PMC_AUROC ≥ 0.90 | Dominance check failed; halt |
| AT-6 | 4 | Framework script reads no GT file | Code review |
| AT-7 | 6 | Verdict script reads only metrics, not raw data | Code review |

---

## Implementation Order (Sequential, No Skipping)

```
1. Resolve ambiguities A1–A7 from protocol_recovery.md
2. Write and lock config9b.py
3. AT-1: build_network.py → A_full.npy, A_obs.npy
4. AT-2: lyapunov_oracle.py → Sigma, Q, Omega, DeltaOmega_true
5. AT-4: verify_dominance.py → dominance_report.json [GATE]
6. build_oracle.py → GT1–GT5 objects
7. Hash-lock ground_truth_manifest.json [GATE]
8. AT-3: generate_trajectories.py → x_A.npy, x_B.npy
9. evaluate_baselines.py → baseline_metrics.json
   [AT-5: verify B4 oracle achieves PMC_AUROC ≥ 0.90]
10. evaluate_framework.py → DeltaOmega_estimated.npy, framework_scores_off.npy
11. compute_metrics.py → primary_metrics.json
12. compute_secondary_metrics.py → secondary_metrics.json
13. verdict.py → primary_verdict.json
```
