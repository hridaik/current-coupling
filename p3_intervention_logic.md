# Phase 9A.3 — Intervention Logic

## Purpose

For each planted organization in the benchmark, specify the structural and state
interventions, and their expected outcomes. This mirrors the paper's intervention
logic: current-supported links dissolve under state intervention and survive structural
intervention; coupling-supported links dissolve under structural intervention.

---

## The Two Intervention Types

### State Intervention
Change the behavioral/dynamical regime without touching anatomy.

In the benchmark: suppress the latent drive from z_high to z_low = 0.

This is the analog of:
- OU cascade: reduce α from 20 to 1
- Leech: reduce coupling gain to zero
- Worm: transition from dwelling to roaming (or vice versa)

### Structural Intervention
Remove specific anatomical connections without changing the dynamical regime.

In the benchmark: remove a set of edges from A (the observed coupling matrix) while
keeping z at z_high.

This is the analog of:
- Leech: remove cells 27 and 33 (reduces phase lag; some current-supported pairs persist)
- Worm: synaptic block or cell ablation prediction

---

## Organization 1: PMC Source-Target Pairs

### What is planted
96 directed pairs (i,j) where i ∈ PMC_sources, j ∈ PMC_targets, A[i,j] = 0.
These pairs acquire large ΔΩ_true in State A through H_global relay.

### Structural Intervention

**Operation:** Remove all within-module edges from M1 to M2
(a set of structural edges that do not include PMC source-target pairs directly).

**Expected outcome for PMC pairs:**
```
ΔΩ[i,j] for (i,j) ∈ PMC pairs ≈ ΔΩ_original[i,j]
```
The PMC source-target organization is largely unchanged. The relay path goes
i (M1) → H_global → j (M3, M4), not through M2. Removing M1→M2 structural edges
does not disrupt the H_global relay.

**Expected outcome for M1→M2 coupled pairs:**
```
ΔΩ[i,j] for (i ∈ M1, j ∈ M2, A[i,j] ≠ 0) changes
```
Structural links disappear from the precision graph; their ΔΩ contribution changes.

**Interpretation:**
The PMC organization survives this structural intervention. It is not carried by the
removed edges. This matches the leech finding: removing cells 27 and 33 reduces
phase lag but does not eliminate the non-adjacent ganglion pair current-supported
links.

### State Intervention

**Operation:** Set z_mean = 0. Compute Ω_A0 = D_B × Q_A0 + A, where Q_A0 is
the precision matrix at z=0 (same anatomy, baseline drive).

**Expected outcome for PMC pairs:**
```
ΔΩ[i,j] = Ω_A0[i,j] − Ω_B[i,j] ≈ 0   for (i,j) ∈ PMC pairs
```
The PMC source-target coordination dissolves. H_global neurons revert to baseline;
the relay path that created ΔΩ for PMC pairs is no longer driven. The conditional
dependence between PMC sources and PMC targets becomes indistinguishable from that
of non-PMC off-connectome pairs.

**Interpretation:**
The PMC organization is entirely state-created. Suppressing z eliminates it. This
matches OU cascade (reduce α → off-local R68 returns to −0.026) and the leech
(gain = 0 → current-velocity term is exactly zero).

### Summary Table for PMC Pairs

| Intervention | ΔΩ for PMC pairs | ΔΩ for structural pairs | Interpretation |
|---|---|---|---|
| None (baseline) | Large, positive | Present | PMC organization active |
| Structural (remove M1→M2 edges) | Unchanged | Changed | PMC survives; structural links affected |
| State (z=0) | ≈ 0 | Unchanged | PMC dissolves; structure unchanged |
| Both | ≈ 0 | Changed | Independent effects |

---

## Organization 2: Structural (On-Connectome) Pairs

### What is planted
All pairs with A[i,j] ≠ 0. These are on-connectome pairs. In the worm these correspond
to Class 1 (on both A_raw and A_C) and Class 2 pairs.

### Structural Intervention

**Operation:** Remove a targeted subset of edges (e.g., all edges from M1 neurons
to their M1 within-module targets).

**Expected outcome:**
```
Q[i,j] changes for removed pairs
ΔΩ[i,j] changes for removed pairs
```
Structural links in the removed set disappear from the precision graph. Their
ΔΩ contribution changes proportionally to their anatomical weight.

**Interpretation:**
Coupling-supported links respond to structural intervention. This is the control
that confirms the structural lesion has the expected effect.

### State Intervention

**Expected outcome for pure structural pairs (A[i,j] ≠ 0, no PMC pathway involvement):**
```
ΔΩ[i,j] ≈ 0   (small change; structural pairs are state-stable)
```
Structural links are present in both State A and State B. Their ΔΩ is small compared
to PMC pairs' ΔΩ. The state switch does not eliminate them.

**Interpretation:**
Coupling-supported links survive state intervention. Changing the neuromodulatory
regime does not remove synaptic connections.

---

## Organization 3: Non-PMC Off-Connectome Pairs

### What is planted
All off-connectome pairs that are NOT PMC source-target pairs. These have A[i,j] = 0
and are NOT part of the planted organization. They are the "null" set of off-connectome
pairs.

### Expected behavior under both interventions
```
ΔΩ[i,j] ≈ 0   under all conditions
```
These pairs show small, noise-level ΔΩ. They do not respond systematically to either
structural or state intervention. They are the background against which the PMC
organization must be detected.

**Critical check:** The dominance condition (G1, p2) guarantees that non-PMC off-connectome
pairs have ΔΩ distributions centered near zero, while PMC pairs have ΔΩ distributions
shifted well above the background. This must be verifiable analytically before simulation.

---

## The OU/Leech/Worm Logic Reproduced

The three-way classification from the leech paper maps onto the benchmark as follows:

### Load-bearing (regime-creating) connections
In the benchmark: the H_global → PMC_target projections. These are the structural
connections (A[H_global, j] ≠ 0) that, when intact, allow the z drive to propagate
and create the PMC organization. Removing H_global neurons from the dynamics
collapses the PMC organization. But H_global neurons are hidden — the framework
cannot identify or remove them.

### Current-supported connections
In the benchmark: the PMC source-target pairs. These have A[i,j] = 0. They acquire
ΔΩ through H_global relay. They survive structural intervention on observed edges
and dissolve under state intervention (z = 0).

### Coupling-supported connections
In the benchmark: all pairs with A[i,j] ≠ 0. These change when edges are removed
and are relatively stable across states.

---

## Operationalizing the Intervention Test

The benchmark's intervention test is analytical, not empirical. Because the ground
truth A is known, we compute:

```
ΔΩ_state_lesion  = Ω(z=0, A_full) − Ω(z=0, A_full) = 0  [trivially; both states at z=0]
```

More precisely, define:

```
ΔΩ_planted = Ω(z=z_high, A_full) − Ω(z=0, A_full)
```

This is the current organization change attributable to the state, with anatomy fixed.
PMC pairs should dominate the top of this ranking.

And:

```
ΔΩ_structural = Ω(z=z_high, A_full) − Ω(z=z_high, A_lesioned)
```

This is the organization change attributable to a structural lesion, with state fixed.
Structural pairs should dominate the top of this ranking. PMC pairs should be absent
from the top of this ranking.

The framework succeeds in intervention recovery if:
- PMC pairs dominate the top-k of ΔΩ_planted
- PMC pairs are absent from the top-k of ΔΩ_structural
- Structural pairs dominate the top-k of ΔΩ_structural

This is an exact analog of the leech's three-way classification by intervention response.

---

## Why This Avoids Circularity (vs. Phase 6–8 Design)

**Phase 6–8 problem:** The C label was defined by state sensitivity (SAREACHABLE = 1, meaning
there exists a z-mediated path). This was then tested by asking whether the framework
recovers state-sensitive pairs. Circular.

**Phase 9A resolution:** PMC membership is defined by construction topology (which neurons
project to H_global, which H_global neurons project to which targets). This is specified
before any Lyapunov computation. The intervention outcomes are then *predictions* from
the construction, not definitions. The framework's performance is tested against the
analytical ΔΩ ranking (which is a consequence of the construction, not its definition).

The PMC circuit is defined by:
```
Membership criterion: shared H_global connectivity pattern
NOT by: state-sensitivity of ΔΩ
```

The state-sensitivity of ΔΩ is a prediction that is verified analytically (dominance
condition D1) and then tested by the framework.
