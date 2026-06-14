# Phase 8A Baseline Specification
**Status:** FROZEN — pre-registered before framework execution  
**Date:** 2026-06-13

All baselines are defined here. No baseline may be added after framework evaluation begins. No baseline may be selected or removed based on how it compares to the framework.

---

## 0. Purpose and Principles

Baselines serve two roles:

1. **Null reference**: establishes the performance floor (random) and the performance that can be achieved without the framework's key mechanisms
2. **Diagnostic decomposition**: identifies which component of framework performance (if any) is explained by simpler structure

All baselines use only information available to the framework (see phase8a_evaluation_spec.md §2.1-2.2). No baseline may access A_sparse, labels, H2 topology, or D.

**Exception:** Module-membership oracle (B4) explicitly uses meta-structural knowledge of the network design. It is labeled an oracle baseline and interpreted differently (see §4).

---

## 1. Baseline B1 — Null / Chance

### Description
Uniformly random class probabilities for every directed pair.

### Inputs
None (uses no data).

### Algorithm
```python
for (i, j):
    class_prob = {'S': 0.25, 'C': 0.25, 'M': 0.25, 'N': 0.25}
    class_pred = random.choice(['S','C','M','N'])
```

### Expected Metrics
- AUROC = 0.50 for every class
- MacroAUROC = 0.50
- LR-AUROC = 0.50
- Brier score = 0.1875 (uniform prediction)

### Strengths
None.

### Weaknesses
Ignores all observable information.

### Role
Defines the performance floor. Any result at or below B1 constitutes active mis-ranking.

---

## 2. Baseline B2 — Marginal Frequency Prior

### Description
Assigns each pair the empirical marginal class frequency as its class probability. Every pair receives the same probability vector derived from the training-free class distribution.

### Inputs
None (prior is derived from class counts only, which are not available to the framework — but the marginal frequencies are computed from the locked label counts and hardcoded in the evaluation script, not revealed to the framework).

### Algorithm
The marginal frequencies are:
```python
class_prob = {
    'S': 497 / 9900,   # ≈ 0.0502
    'C': 857 / 9900,   # ≈ 0.0866
    'M':  89 / 9900,   # ≈ 0.0090
    'N': 8457 / 9900,  # ≈ 0.8543
}
# same for all pairs
class_pred = 'N'  # always predict majority class
```

### Expected Metrics
- AUROC = 0.50 for all classes (constant score → no discrimination)
- MacroAUROC = 0.50
- Brier score: lower than B1 because probabilities are better calibrated at the mean level
- Balanced accuracy = 25% (predicting N for everything gives 100% recall on N, 0% on others)

### Strengths
Best-calibrated baseline in expectation (minimizes Brier score among constant predictors).

### Weaknesses
Zero discriminative ability.

### Role
Calibration reference. Also demonstrates the magnitude of class imbalance.

---

## 3. Baseline B3 — Pairwise Correlation

### Description
Uses Pearson correlation between observed traces y_i(t) and y_j(t) as a proxy for functional connectivity. Symmetric. Cannot distinguish S from C or directed from undirected links.

### Inputs
- y(t): observed calcium traces (48,000 × 100), oracle_z condition
- Run aggregation: average absolute correlation across 5 runs

### Algorithm
```python
for run in runs:
    y = run['y']  # (48000, 100)
    C = corrcoef(y.T)  # (100, 100) Pearson correlation matrix
    
for (i, j):
    score = mean over runs of |C[i, j]|  # unsigned
    # Convert to class_prob via softmax of (score, score, 0, -score) for S,C,M,N
    # This is pre-specified mapping; cannot be changed post-hoc
```

**Pre-specified score-to-class mapping for B3:**
- S score: |corr(i,j)|  (symmetric; direct links should be correlated)
- C score: |corr(i,j)|  (same signal; correlation cannot distinguish C from S)
- M score: |corr(i,j)|  (same signal)
- N score: -|corr(i,j)|

class_prob obtained by softmax([|C[i,j]|, |C[i,j]|, |C[i,j]|, -|C[i,j]|] × 5) with temperature 5.

This is deliberately naive: B3 cannot distinguish S from C from M, only from N.

### Expected Metrics
- LR-AUROC: moderate (connected pairs of any type tend to be correlated, but C pairs may be more weakly correlated than S due to indirect coupling)
- S-AUROC: moderate to good (direct links correlate strongly)
- C-AUROC: unclear (may be good or poor depending on indirect correlation strength)
- M-AUROC: moderate

### Assumptions
Functional connectivity is reflected in pairwise correlation.

### Strengths
Simple, parameter-free, uses only observed data.

### Weaknesses
Symmetric; cannot distinguish direction. Cannot distinguish C from S. Cannot isolate state-dependent links.

### Role
Establishes the performance achievable by the simplest correlation-based approach. The framework's LR-AUROC should exceed B3's LR-AUROC for the C detection claim to be meaningful.

---

## 4. Baseline B4 — Graphical Lasso (Partial Correlation)

### Description
Estimates the partial correlation structure of y(t) using the graphical lasso (GL) estimator with a pre-specified regularization path.

### Inputs
- y(t): oracle_z condition, all 5 runs pooled (stacking along time axis → 240,000 × 100 after pooling)

### Algorithm
```python
Y_pooled = vstack([run['y'] for run in runs])  # (240000, 100)
# Center each neuron
Y_c = Y_pooled - Y_pooled.mean(axis=0)

# Graphical lasso with pre-specified regularization sequence
# alpha ∈ {0.005, 0.01, 0.02, 0.05, 0.10}
# Select alpha by BIC on held-out run (run 4, held out from fitting)
Y_fit = vstack([runs[r]['y'] for r in [0,1,2,3]])  # 192000 × 100
Y_val = runs[4]['y']  # 48000 × 100

best_alpha = argmin(BIC(alpha, Y_fit, Y_val)) over alpha_grid
Omega_hat = graphical_lasso(Y_fit, alpha=best_alpha).precision_

for (i,j):
    score_direct = abs(Omega_hat[i, j])  # partial correlation (symmetric)
```

**Pre-specified score-to-class mapping for B4:**
- S score: |Ω[i,j]|
- C score: |Ω[i,j]| (partial correlation cannot distinguish C from S)
- M score: |Ω[i,j]|
- N score: -|Ω[i,j]|

class_prob as softmax with same logic as B3.

### Regularization governance
The regularization grid `{0.005, 0.01, 0.02, 0.05, 0.10}` is frozen here. Alpha is selected by BIC on the validation run. This is permitted because: (a) the validation run is not the same data as the held-out test labels, (b) the regularization affects only the baseline's performance, not the framework's, and (c) the selection procedure is fully pre-specified.

### Expected Metrics
- Direct-AUROC: likely good (precision matrix entries recover direct coupling structure when regularization is appropriate)
- LR-AUROC: poor to moderate (partial correlation is designed to remove indirect paths; C pairs — which have no direct edge — may be penalized by regularization)
- C-AUROC: expected poor (partial correlation specifically removes the kind of indirect dependence that C pairs exhibit)

### Assumptions
The partial correlation structure of y(t) reflects the conditional independence structure of the neural state.

### Strengths
Principled statistical estimator with theoretical guarantees (in the Gaussian case). Represents the state-of-the-art simple connectivity estimator.

### Weaknesses
Assumes stationarity. Ignores z-modulation. Symmetric. Cannot leverage oracle z signal. Expected to be specifically bad at detecting C-class pairs, which is the framework's claimed advantage.

### Role
The most important diagnostic baseline. If the framework's C-AUROC < B4's C-AUROC, the framework has failed its primary claim. If the framework's C-AUROC > B4's C-AUROC, this is the first positive evidence for the framework.

---

## 5. Baseline B5 — State-Dependent Correlation Difference

### Description
Approximates the framework's core idea using a simple statistic: the difference in correlation structure between high-z and low-z time periods. This does not use any structural information.

### Inputs
- y(t): oracle_z condition
- z_oracle(t): oracle latent state time series

### Algorithm
```python
for run in runs:
    z = run['z_oracle']  # (48000,)
    y = run['y']         # (48000, 100)
    
    # Split into high-z and low-z epochs (above/below median z)
    z_median = median(z)
    high_idx = where(z > z_median)[0]
    low_idx  = where(z <= z_median)[0]
    
    C_high = corrcoef(y[high_idx].T)  # correlation in high-z state
    C_low  = corrcoef(y[low_idx].T)   # correlation in low-z state
    delta_C = C_high - C_low          # state-dependent correlation change

# Average delta_C across runs
delta_C_mean = mean over runs of delta_C

for (i,j):
    raw_score = |delta_C_mean[i,j]|
```

**Pre-specified score-to-class mapping for B5:**
- C score: |ΔC[i,j]|  (C pairs should show state-dependent correlation change)
- M score: |ΔC[i,j]|  (M pairs also state-dependent)
- S score: -|ΔC[i,j]|  (direct links should be less state-dependent)
- N score: -|ΔC[i,j]|  (null links: low everything)

class_prob: softmax([−|ΔC|, |ΔC|, |ΔC|, −|ΔC|] × 5) for [S, C, M, N].

### Expected Metrics
- LR-AUROC: moderate (approximates what the framework computes, but crudely)
- C-AUROC: moderate (main signal)
- S-AUROC: moderate (predicted to rank low in the C score, correctly)

### Assumptions
State-dependent correlation changes are informative about H2-mediation.

### Strengths
Captures the core conceptual signal (state-dependent connectivity). Uses oracle z. Simple.

### Weaknesses
Ignores directionality. Does not estimate partial correlations or currents. Symmetric. Sensitive to z distribution (median split may not be optimal).

### Role
Establishes the performance of the simplest state-dependent approach. The framework should outperform B5 by virtue of more principled estimation of ΔΩ and probability currents. If framework ≤ B5 on LR-AUROC, the framework adds no value over simple median-split correlation difference.

---

## 6. Baseline B6 — Module-Membership Oracle

### Description
Uses prior knowledge of the network's modular structure to generate predictions. Exploits that: (a) within-module pairs are more likely to be connected (p_within=0.15 >> p_between=0.03), and (b) C pairs require a path through H2, which targets 2-module combinations.

### Inputs
None (uses hardcoded module boundaries derived from network design, not observed data).

### Algorithm
```python
# Module membership: derived from neuron indices (hardcoded, not from A_sparse or labels)
# M1: 0-24, M2: 25-49, M3: 50-74, M4: 75-99

for (i,j):
    same_module = (i // 25 == j // 25)
    
    if same_module:
        # Within-module: high S probability, low C (C requires H2 path across modules)
        class_prob = {'S': 0.40, 'C': 0.10, 'M': 0.10, 'N': 0.40}
    else:
        # Between-module: low S (sparse across modules), higher C (H2 connects modules)
        class_prob = {'S': 0.05, 'C': 0.30, 'M': 0.02, 'N': 0.63}
```

**Note:** The values above are computed from the known network parameters (P_WITHIN=0.15, P_BETWEEN=0.03, P_H2_OUT=0.20), not from observations. This is an **oracle baseline**: it uses information the framework is not given.

Specifically: the framework does not know module boundaries. The contiguous index structure (0-24=M1, etc.) is observable from neuron indices, but the framework must not use this knowledge per the information barrier. This baseline is provided as an upper bound from structural meta-knowledge.

**Forbidden for framework use:** The framework must not implement logic equivalent to B6. This would constitute topology leakage.

### Expected Metrics
- LR-AUROC: moderate (captures between-module C enrichment but imprecisely)
- S-AUROC: moderate (within-module S enrichment)
- No ability to detect specific pairs; only module-level separation

### Role
Oracle upper bound for module-aware predictions. If the framework is better than B6, it has learned pair-level information beyond module membership. If it is worse than B6, it may have failed to capture even coarse structure.

---

## 7. Summary Table

| Baseline | Uses y? | Uses z? | Symmetric? | Oracle info? | Primary comparison target |
|----------|---------|---------|------------|-------------|--------------------------|
| B1 Null | No | No | Yes | No | Floor reference |
| B2 Marginal prior | No | No | Yes | Class counts (eval code) | Calibration reference |
| B3 Correlation | Yes | No | Yes | No | Undirected connectivity baseline |
| B4 Graphical lasso | Yes | No | Yes | No | Key diagnostic for C-class claim |
| B5 State-ΔCorr | Yes | Yes | Yes | No | State-dependence baseline |
| B6 Module oracle | No | No | Yes | Module boundaries | Oracle upper bound |

**All baselines are symmetric.** The framework's claim includes detecting directed probability currents. If the framework outperforms all baselines on directed-pair-specific metrics, this provides evidence for directed estimation beyond what correlation-based methods achieve.

---

## 8. Governance Rules

- No baseline may be added after framework evaluation begins.
- No baseline may be removed or re-specified based on how it compares to the framework.
- If a baseline fails to run (technical error), it is reported as failed and excluded from comparison; this does not affect the framework's verdict.
- B4's alpha selection procedure is pre-specified and may not be modified to make B4 perform better or worse.
