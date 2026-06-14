# Phase 9A.5 — Evaluation Metrics

## Purpose

Define the evaluation metrics aligned with the paper's actual evaluation logic. The
primary metrics test organization recovery. AUROC over pair labels is secondary only.

---

## Metric Hierarchy

```
PRIMARY:   Top-k overlap with oracle ranking
           Rank correlation with oracle
           PMC enrichment test

SECONDARY: Module recovery (NMI/AMI)
           Intervention recovery (state vs. structural separation)
           ΔΩ vs. ΔQ comparison

DIAGNOSTIC: AUROC (PMC vs. background, off-connectome only)
            Structural detection accuracy (S-class recovery)
```

AUROC is demoted to diagnostic. It is informative about the shape of the ranking
distribution but is not the primary success criterion.

---

## Primary Metric 1: Top-k Overlap (Precision@k)

**Definition:**
```
Precision@k = |{ top-k estimated } ∩ { PMC pair set }| / k
```

where "top-k estimated" is the k off-connectome pairs with the largest |ΔΩ_estimated|.

**Why this is the primary metric:**

The worm paper uses the Fisher top-K test as its primary evidence of circuit-level
enrichment (Fisher OR = 7.2, p = 0.002 at top 20). The leech paper shows that the
dominant off-diagonal Ω entries are concentrated in the 55–56 non-adjacent ganglion
pairs. The OU cascade shows that the dominant off-local entry (nodes 6 and 8) is
correctly identified by the framework.

In all three cases, the question is: are the planted/known pairs concentrated near
the top of the ranking?

**Pre-specified k values:**
```
k = 20    (strict — top-tier precision)
k = 50    (standard)
k = 100   (liberal)
```

**Expected values under success:**
- PMC pairs have density 96/10,995 ≈ 0.87% of all off-connectome pairs
- Under random ranking, Precision@50 ≈ 0.87%  (expected 0–1 PMC pairs)
- Under oracle ranking (GT3), at least 60% of Top_50_oracle are PMC pairs
- Framework success criterion: Precision@50 ≥ 0.25 (29× enrichment over random)

**Null distribution:** Simple permutation of the estimated ΔΩ ranking, 10,000 iterations.

---

## Primary Metric 2: Rank Correlation with Oracle

**Definition:**
```
ρ_Spearman(rank_estimated, rank_oracle)
```

computed over all off-connectome pairs, where:
- rank_estimated = rank of (i,j) by |ΔΩ_estimated| (framework output)
- rank_oracle = rank of (i,j) by |ΔΩ_true_off| (GT3)

This directly tests whether the framework's organization ranking approximates the
true organization ranking.

**Why this is a primary metric:**

The paper's key comparison is ρ(ΔΩ, ΔQ) = 0.566 (with full D) vs. 0.998 (with
diagonal D approximation). The ρ between different estimates of the same quantity
is the natural measure of how well an estimator tracks the true ranking.

**Expected values:**
- Under random estimation: ρ ≈ 0
- Under framework success: ρ ≥ 0.40 (primary success threshold)
- Under framework partial success: 0.15 ≤ ρ < 0.40
- Under framework failure: ρ ≤ 0.10

**Note:** ρ is computed at the full off-connectome pair set level. At the top-k level,
a top-k rank correlation (Kendall's τ restricted to the top-k oracle pairs) is also
computed as a supplementary check.

---

## Primary Metric 3: PMC Enrichment Test

**Definition:**

AUROC for the binary label "PMC pair vs. background off-connectome pair" as a function
of the estimated |ΔΩ_estimated| ranking.

```
PMC_AUROC = AUROC( binary_PMC_label, |ΔΩ_estimated| )
```

restricted to off-connectome pairs only.

This is the exact analog of the worm's neuropeptide enrichment AUROC (AUROC = 0.664,
p = 0.004 for PDF annotation).

**Why this is primary (but not the only primary metric):**

The worm paper uses AUROC as its main enrichment statistic (alongside Fisher top-K).
The benchmark uses it the same way: AUROC over the planted annotation, not AUROC over
all pair types (which would be inflated by the trivially detectable structural pairs
and the majority null class).

The key distinction from Phase 6–8: this AUROC is computed ONLY over off-connectome
pairs (the inference target), NOT over all pairs (which inflated apparent performance
through the S-class).

**Pre-specified success thresholds:**
```
Primary success:         PMC_AUROC ≥ 0.75
Partial success:         PMC_AUROC ≥ 0.60
Framework failure:       PMC_AUROC < 0.55
```

**Baseline (null hypothesis):** PMC_AUROC = 0.50 under random ranking.

**Comparison baseline:** A simple baseline (correlation-change ΔCorr threshold, the
B5 analog from Phase 8) is computed and must be reported alongside the framework result.

---

## Secondary Metric 4: Module Recovery

**Definition:**

Apply spectral clustering (or equivalent non-parametric community detection) to the
matrix:
```
M_off = |ΔΩ_estimated_off|   (off-connectome pairs only, 150×150 matrix)
```

with k=3 clusters (C_src, C_tgt, background).

Evaluate recovery against GT4:
```
NMI_module = NMI(recovered_communities, ground_truth_communities)
AMI_module = AMI(recovered_communities, ground_truth_communities)
```

**Why this is secondary:**

The paper notes module-level organization in the leech (the ganglia form functional
groups based on the wave's coupling phase). The worm's PDF circuit has a source group
and target group. Module recovery tests whether the framework identifies the correct
functional grouping at the circuit level, not just the pair level.

Module recovery is secondary because it requires a clustering step that introduces
additional hyperparameters (number of clusters, algorithm choice) not part of the
framework itself.

**Success thresholds:**
```
Primary success:   NMI ≥ 0.40
Partial success:   NMI ≥ 0.20
Framework failure: NMI < 0.10
```

---

## Secondary Metric 5: Intervention Recovery

**Definition:**

Compute the correlation between the framework's estimated ΔΩ under the two
intervention conditions (state and structural) and the analytically known intervention
predictions (GT5):

```
ρ_state     = Spearman(|ΔΩ_framework_state_lesion|, |ΔΩ_true_state_lesion|)
ρ_structural = Spearman(|ΔΩ_framework_structural_lesion|, |ΔΩ_true_structural_lesion|)
```

**Why this is secondary:**

The leech paper's key result is the three-way intervention classification:
load-bearing, current-supported, coupling-supported. The benchmark reproduces this logic
analytically. Intervention recovery tests whether the framework's estimated organization
correctly predicts which pairs should dissolve under each intervention type.

This is a genuinely novel and harder test than any metric in Phases 6–8.

**Success criteria:**
```
Current-supported pairs identified (PMC pairs dominant in ΔΩ_state_lesion): ρ_state ≥ 0.30
Structural pairs identified in ΔΩ_structural_lesion:                       ρ_structural ≥ 0.40
```

---

## Diagnostic: AUROC Over All Pairs (Including S-Class)

**Definition:**

For completeness, compute:
```
Macro_AUROC = mean AUROC over three binary labels (PMC vs. rest, S vs. rest, N vs. rest)
S_AUROC     = AUROC for structural pair recovery
```

**Why this is diagnostic only:**

Phase 6–8 used Macro_AUROC and S_AUROC as primary metrics. This inflated apparent
performance because the framework successfully detects structural pairs (S_AUROC = 0.853
in Phase 8B) while failing at the scientifically relevant target (PMC_AUROC equivalent
was 0.4484 in Phase 8B). Including S_AUROC in the primary metric obscured the failure.

In Phase 9A, these are diagnostic checks:
- S_AUROC confirms the framework correctly identifies structural connectivity
- Macro_AUROC provides an aggregate overview

Neither is a primary success criterion.

---

## Baseline Comparators (Pre-Specified)

Three baselines are evaluated on all primary metrics before the framework:

### B1: Random ranking
Randomly order off-connectome pairs. Expected PMC_AUROC = 0.50, Precision@50 ≈ 0.87%.
Establishes the null floor.

### B2: Correlation-change baseline (ΔCorr analog)
Rank off-connectome pairs by |correlation_A[i,j] − correlation_B[i,j]|. This is the
analog of B5 from Phase 8. Expected to partially recover PMC organization (similar to
B5's C-AUROC = 0.5517 in Phase 8). Tests whether correlation change is sufficient.

### B3: State-averaged precision graph (Glasso)
Apply graphical lasso to the pooled data (ignoring state). Ranks pairs by |Q_pooled[i,j]|.
This detects structural connectivity but does not detect state-dependent organization.
Expected PMC_AUROC ≈ 0.50 (no state information used).

### B4: Oracle bound
Use ΔΩ_true directly as the ranking signal. Provides the ceiling on all metrics.
Expected PMC_AUROC ≈ 1.0, Precision@50 ≈ the dominance-condition value.

The framework must exceed B2 on primary metrics to demonstrate that the framework
adds value beyond simple correlation change.

---

## Pre-Specified Success Criteria Summary

| Metric | Success | Partial | Failure |
|---|---|---|---|
| PMC_AUROC (primary) | ≥ 0.75 | ≥ 0.60 | < 0.55 |
| Precision@50 (primary) | ≥ 0.25 | ≥ 0.10 | < 0.05 |
| Rank correlation ρ (primary) | ≥ 0.40 | ≥ 0.15 | < 0.10 |
| NMI_module (secondary) | ≥ 0.40 | ≥ 0.20 | < 0.10 |
| ρ_state intervention (secondary) | ≥ 0.30 | ≥ 0.15 | < 0.10 |

All thresholds are pre-specified and locked before any framework evaluation. They may
not be changed after evaluation begins.

---

## Why AUROC Is Secondary (Not Primary)

Phase 8B used AUROC as the primary metric and declared failure when C-AUROC = 0.4484.
The problem was not the metric — AUROC correctly characterized the failure. The problem
was asking the wrong question: AUROC over all pairs, including the trivially-detectable
structural pairs, obscured the failure to detect the scientifically relevant organization.

In Phase 9A, AUROC (PMC_AUROC) is the third primary metric. It is valid because:
- It is computed only over off-connectome pairs (not inflated by S-class detection)
- It directly mirrors the worm's enrichment AUROC
- It is calibrated against a pre-specified null (0.50)

But it is not the first metric because Precision@k and rank correlation are more
directly interpretable as "did the framework find the planted circuit?"

The worm paper reports AUROC = 0.664 (p = 0.004) as the main result. The same metric
applied to the benchmark is PMC_AUROC. Success threshold (0.75) is higher than the worm
result because the benchmark has exact ground truth — the planted circuit is unambiguous,
and there is no biological noise or annotation imprecision to explain partial enrichment.
