# Phase 9A.4 — Ground-Truth Objects

## Purpose

Specify exactly which objects will be known from construction and serve as evaluation
targets. These objects are defined at the organization level. Pair-level labels are
not the primary evaluation target.

---

## Principle

The paper evaluates organization recovery, not pair-level classification. This section
specifies exactly what "recovery" means in the benchmark context.

The five ground-truth objects mirror the paper's evaluation objects:

| Paper evaluation | Benchmark ground-truth object |
|---|---|
| Off-local Scur and Sstat (OU) | ΔΩ_true magnitude distribution by pair class |
| Non-adjacent ganglion pair set (Leech) | PMC pair set and its ΔΩ_true ranking |
| PDF-receptor circuit enrichment (Worm) | PMC annotation and enrichment rank |
| Module-level organization (Worm) | PMC source and target communities in ΔΩ_true |
| Intervention prediction (Worm) | ΔΩ response to state vs. structural lesion |

---

## GT1. ΔΩ_true — The True Current Difference Matrix

**Definition:**
```
ΔΩ_true = Ω_A − Ω_B = D_A Q_A − D_B Q_B
```

where Q_A and Q_B are the true precision matrices (inverses of the true covariances
Σ_A and Σ_B) computed analytically from the Lyapunov equation at z_high and z=0.

**Restriction to off-connectome pairs:**
```
ΔΩ_true_off[i,j] = ΔΩ_true[i,j]   for all (i,j) with A[i,j] = 0
```

**This is the oracle.** A perfect framework would recover a ranking proportional to
|ΔΩ_true_off|. The evaluation asks how well the framework approximates this oracle.

**How it is derived:**
1. Solve AΣ_A + Σ_A Aᵀ + 2D_A = 0 for Σ_A (Lyapunov equation at z_high)
2. Solve AΣ_B + Σ_B Aᵀ + 2D_B = 0 for Σ_B (Lyapunov equation at z=0)
3. Compute Q_A = Σ_A⁻¹, Q_B = Σ_B⁻¹
4. Compute Ω_A = D_A Q_A + A, Ω_B = D_B Q_B + A
5. Compute ΔΩ_true = Ω_A − Ω_B

**Note:** A cancels in ΔΩ_true because A is state-invariant. This is explicit in the
paper: "Because A is fixed across states, anatomy cancels."

---

## GT2. PMC Pair Set — The Planted Off-Connectome Organization

**Definition:** The set P of 96 directed off-connectome pairs:
```
P = { (i,j) : i ∈ PMC_sources, j ∈ PMC_targets, A[i,j] = 0 }
```

These are the analog of:
- Nodes 6 and 8 in the OU cascade (the dominant off-local pair at high α)
- The 55–56 non-adjacent ganglion pairs in the leech (at nominal gain)
- The 61 PDF-annotated Class 4 pairs in the worm

**This set is known before simulation.** It is derived from the H_global connectivity
specification (who projects to H_global; who receives from H_global) and the
no-direct-edge construction rule.

**Key property (verified analytically via dominance condition D1):**
The PMC pairs are enriched among the top-k entries of |ΔΩ_true_off|. This must
hold before the framework is evaluated.

---

## GT3. ΔΩ_true Ranking — The Oracle Ranking

**Definition:** The ranked list of all off-connectome pairs, ordered by |ΔΩ_true_off[i,j]|
descending.

```
rank_oracle(i,j) = rank of (i,j) in descending |ΔΩ_true_off|
```

**Top-k oracle sets:**
```
Top_20_oracle  = top 20 off-connectome pairs by |ΔΩ_true_off|
Top_50_oracle  = top 50 off-connectome pairs by |ΔΩ_true_off|
Top_100_oracle = top 100 off-connectome pairs by |ΔΩ_true_off|
```

By the dominance condition D1, PMC pairs dominate these sets. Specifically:
- Median rank of PMC pairs in oracle ranking is in the top 10% of all off-connectome pairs
- At least 60% of Top_50_oracle are PMC pairs (pre-specified; verified before simulation)

This mirrors the leech: at nominal gain, the dominant off-diagonal Ω entries are
specifically the 55–56 non-adjacent ganglion pairs.

---

## GT4. Module-Level Organization — PMC Community Structure

**Definition:** The planted functional communities in the ΔΩ_true organization:
```
C_src = PMC source neurons (8 neurons in M1)
C_tgt = PMC target neurons (12 neurons in M3 and M4)
```

**What module recovery means:**
If we compute the ΔΩ_estimated matrix from framework outputs and apply a community
detection algorithm (e.g., spectral clustering on the off-connectome |ΔΩ_estimated|
matrix), the recovered communities should align with C_src and C_tgt.

This is the organization-level analog of the leech result: the framework recovers
the "source" and "target" ganglion groups that constitute the wave's current-supported
organization.

**Module recovery is evaluated by:**
```
NMI(recovered_communities, {C_src, C_tgt, background})
AMI(recovered_communities, {C_src, C_tgt, background})
```

where NMI and AMI are normalized and adjusted mutual information.

---

## GT5. Intervention Outcomes — The Analytical Predictions

Two analytically computed prediction objects:

### GT5a. State-Lesion Ranking

```
ΔΩ_state_lesion = Ω_A − Ω_B0
```

where Ω_B0 is the current organization at z=0, A unchanged. This measures how
much of the organization is state-created.

Expected: PMC pairs dominate the top of |ΔΩ_state_lesion|.
Structural pairs are stable (small ΔΩ_state_lesion).

### GT5b. Structural-Lesion Ranking

```
ΔΩ_structural_lesion = Ω_A − Ω_A_lesioned
```

where Ω_A_lesioned is the current organization in State A with a designated subset of
structural edges removed.

Expected: Structural pairs (edges that were removed) dominate the top of
|ΔΩ_structural_lesion|. PMC pairs have near-zero change (they do not use the
removed edges).

**These two rankings are the benchmark analog of the leech three-way intervention test.**

---

## What Is NOT Defined as Ground Truth

### Per-pair S/C/M/N labels

These are NOT the primary ground-truth objects. The reason is that the paper does
not evaluate by pair-level label accuracy. The worm does not ask "classify each of the
1,321 Class 4 pairs." It asks "is the PDF annotation enriched among the top-k ΔΩ entries?"

Pair-level labels are available as secondary diagnostic objects (for human interpretation)
but are not used as the primary evaluation metric.

If pair-level labels are computed for secondary analysis, they are derived as:

```
Structural (S): A[i,j] ≠ 0
Off-connectome PMC (C_PMC): A[i,j] = 0 AND (i,j) ∈ P
Off-connectome background (N): A[i,j] = 0 AND (i,j) ∉ P
```

The M (mixed) class is excluded from the primary benchmark to avoid the threshold
ambiguity identified in Phase 6A review (W21).

### Estimated quantities

The following are NEVER part of ground truth:

```
Q_A_estimated, Q_B_estimated     (framework output)
Ω_A_estimated, Ω_B_estimated     (framework output)
ΔΩ_estimated                     (framework output)
Framework confidence scores       (framework output)
```

These emerge from the analysis pipeline and are compared to ground-truth objects GT1–GT5.

---

## Summary: Five Ground-Truth Objects

| Object | Type | Paper analog |
|---|---|---|
| GT1: ΔΩ_true | Matrix, 150×150 | The oracle ΔΩ/ΔQ all three papers compute |
| GT2: PMC pair set | Set of 96 pairs | PDF annotation (worm), non-adjacent ganglion pairs (leech) |
| GT3: Oracle ranking | Ranked list, ~10,995 pairs | Top-k enrichment target |
| GT4: Community structure | {C_src, C_tgt, background} | Source/target circuit structure |
| GT5: Intervention predictions | Two ranked lists | Three-way leech classification; worm ΔΩ vs ΔQ comparison |

All five are derived from construction parameters before any simulation or framework
evaluation. None require running the framework. The framework's output is then compared
to these known objects.
