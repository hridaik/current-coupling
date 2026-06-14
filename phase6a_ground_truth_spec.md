# Phase 6A — Ground-Truth Specification

## Preamble

This document defines the ground-truth labels for all four link categories (S, C, M, N).

All definitions must satisfy two hard constraints:

**Constraint 1 — Construction-exclusivity**: Labels are derived solely from the
simulator's construction parameters (coupling matrix, modulation operators, network
topology). No quantity estimated or computed from simulated data is used for labeling.

**Constraint 2 — Framework-independence**: No quantity that is in the estimating family
of the current-velocity framework may appear in a label definition. Specifically, the
following are **forbidden** from appearing in any label criterion:

- Ω (precision matrix, empirical or analytical)
- Q (probability current, empirical or analytical)
- ΔΩ, ΔQ, or any state-difference of these
- Covariance matrices Σ(z) or their inverses
- Partial correlations computed from data
- Any estimated connectivity measure

**Rationale for forbidding analytical Ω and Q:** Even though Ω and Q can in principle be
computed analytically from known parameters (via the Lyapunov equation), using them for
label assignment creates near-circular validation. If the framework estimates Ω̂ → Ω_true
at large sample sizes, any Ω-derived label is trivially recovered. Ground truth must be
defined at the level of circuit topology, not statistical consequences of that topology.

---

## Construction Parameters (Known Exactly)

The following quantities are assumed known exactly from the simulator's construction
procedure. These are the only inputs to the label-assignment procedure.

### Coupling matrix A

The full 140×140 coupling matrix, decomposed as:

```
A = A_sparse + A_lr
```

where:
- `A_sparse` is the sparse random directed coupling matrix (contains module-level structure)
- `A_lr = U · Vᵀ` is the 2–3 rank global component (population modes)

Both components are fixed throughout all simulations. A does not change with z.

### Sub-blocks of A

```
A_oo   : observed × observed block   (100 × 100)
A_oh   : observed × hidden block     (100 × 40)
A_ho   : hidden × observed block     (40 × 100)
A_hh   : hidden × hidden block       (40 × 40)
```

### Hidden neuron membership

For each hidden neuron h ∈ {1, ..., 40}:

- `type(h)` ∈ {H1, H2}
  - H1: local interneuron (assigned to one module)
  - H2: global modulator (projects across multiple modules)
- `module(h)`: module assignment for H1 neurons
- `target_modules(h)`: set of modules targeted for H2 neurons

### Gain modulation operators

For each neuron k (observed or hidden), the state-dependent gain:

```
g_k(z) : ℝ^d → ℝ₊
```

This function is known from construction. The effective local coupling from neuron j to
neuron k at state z is:

```
A_eff[k,j](z) = g_k(z) · A[k,j]
```

The **gain-modulated indicator** is:

```
gmod(k) = 1   if g_k(z) is not constant in z
         = 0   if g_k(z) = constant for all z
```

All `gmod(k)` values are known from construction.

### State drive B(z)

The state-dependent external input to each neuron, known from construction:

```
B[k](z) : ℝ^d → ℝ
```

The **state-driven indicator**:

```
sdrv(k) = 1   if B[k](z) is not constant in z
         = 0   otherwise
```

---

## Required Pre-Computation (Before Any Simulation)

Before running any simulation, the following must be computed and recorded from the
construction parameters alone.

### Step 1 — Identify state-active neurons

A neuron k is **state-active** if it satisfies at least one of:

```
gmod(k) = 1    (gain-modulated)
sdrv(k) = 1    (state-driven input)
type(k) = H2   (global modulator, by definition state-driven)
```

Let `SA` = set of all state-active neurons.

### Step 2 — Compute the state-active reachability graph

For each ordered pair (i, j) of **observed** neurons, determine whether j is reachable
from i through a state-active path in A_sparse:

```
SAREACHABLE(i → j) = True
    if ∃ directed path i = v₀ → v₁ → ... → vₙ = j in A_sparse such that:
       (i)   A_sparse[v_{k+1}, v_k] ≠ 0  for all steps k
       (ii)  ∃ at least one node v_m ∈ SA on the path
       (iii) The path does not pass through any observed neuron other than i and j
             [i.e., all intermediate nodes v₁, ..., v_{n-1} are hidden neurons
              OR are observed neurons in SA]
```

**Important:** Condition (iii) prevents the use of observed-neuron shortcuts that would
make the indirect path redundant (conditional on the intermediate observed neuron, the
i-j dependence would vanish). Paths entirely through observed neurons do not generate
current-supported links unless they pass through SA nodes.

**Note:** This reachability computation uses only the sparse component A_sparse. The
low-rank component A_lr is handled separately (see below).

### Step 3 — Compute direct sparse structural indicator

For each ordered pair (i, j):

```
DIRECT(i, j) = 1   if A_sparse_oo[i, j] ≠ 0
             = 0   otherwise
```

### Step 4 — Compute low-rank structural indicator

For each ordered pair (i, j):

```
LR(i, j) = 1   if (U_o · Vᵀ_o)[i, j] > δ_lr   [threshold δ_lr specified below]
          = 0   otherwise
```

where U_o and V_o are the observed-neuron rows of U and V respectively.

**Threshold δ_lr**: Set to the 95th percentile of |(U_o · Vᵀ_o)[i,j]| across all i≠j.
This identifies the most strongly low-rank-coupled pairs as "low-rank structural." All
other low-rank entries are treated as negligible background.

This threshold is computed from U and V directly (construction parameters), not from data.

---

## Label Assignment Rules

Labels are assigned **after** Steps 1–4 are complete and **before** any simulation is run.

### Step 5 — Assign labels

For each ordered pair (i, j) with i ≠ j and both i, j in the observed set:

```
Label(i, j) = S   if DIRECT(i, j) = 1
                      AND NOT SAREACHABLE(i → j)
                      AND NOT LR(i, j)
```

```
Label(i, j) = M   if DIRECT(i, j) = 1
                      AND SAREACHABLE(i → j)
```

```
Label(i, j) = C   if DIRECT(i, j) = 0
                      AND LR(i, j) = 0
                      AND SAREACHABLE(i → j)
```

```
Label(i, j) = LR  if DIRECT(i, j) = 0
                      AND LR(i, j) = 1
              [separate class, excluded from primary S/C/M/N evaluation]
```

```
Label(i, j) = N   if DIRECT(i, j) = 0
                      AND LR(i, j) = 0
                      AND NOT SAREACHABLE(i → j)
```

**The LR class is excluded from the primary four-way evaluation to prevent the
low-rank ambiguity (L3) from contaminating S/C/M/N metrics. It is reported separately.**

---

## Definition Commentary

### What exactly constitutes a structural link (S)?

A structural link (i→j) exists if and only if:
- A_sparse_oo[i,j] ≠ 0 (neuron j directly receives input from neuron i through the
  sparse coupling matrix)
- The path is **not** modulated by the latent state z (no gain-modulated neuron lies on
  a meaningful indirect route)
- The link does not involve the low-rank background

This is the anatomical ground truth: there is a physical synapse from i to j that is
present and active regardless of behavioral state.

**What this excludes deliberately:**
- Long indirect paths through observed neurons (i→k→j with A[k,i]≠0 and A[j,k]≠0
  where k is observed): these become detectable as S only if i-k and k-j are both S.
  The i-j pair itself is not S unless A_sparse_oo[i,j]≠0.
- Low-rank entries of A even when large: treated as background population coupling,
  not pairwise structural.

### What exactly constitutes a current-supported link (C)?

A current-supported link (i→j) exists if and only if:
- No direct sparse structural coupling (A_sparse_oo[i,j] = 0)
- No low-rank component above threshold (LR(i,j) = 0)
- There exists at least one directed path from i to j through the full network that:
  (a) passes through at least one state-active neuron (gain-modulated or state-driven),
  (b) travels through hidden neurons at some point (preventing the path from being
      "explained" by conditioning on intermediate observed neurons),
  (c) has nonzero entries in A_sparse along every edge

The pair (i,j) is current-supported because the indirect path that connects them is
active primarily under state modulation (z ≠ baseline). Without z, the state-active
nodes on the path are quiescent or at their baseline gain, reducing the effective
propagation along this route.

**Critical distinction from the protocol's formulation:** We do NOT use the phrase
"dependence disappears when state drive is removed" as part of the definition. That
phrase describes an expected observable consequence of being C-labeled under this
constructive definition, not the definition itself. It is used only for post-hoc
sanity checking of the ground truth, not for label assignment.

**What this excludes deliberately:**
- Pairs connected only through state-inactive hidden neurons (H1 interneurons with no
  gain modulation and no z-driven input): these are labeled N, even though they have
  an indirect path. The indirect path does not depend on state, so it is not
  "current-supported" in the framework's sense.
- Pairs connected through low-rank A only: labeled LR, excluded from primary analysis.

### What exactly constitutes a mixed link (M)?

A mixed link (i→j) exists if and only if:
- A_sparse_oo[i,j] ≠ 0 (structural direct edge)
- AND SAREACHABLE(i → j) (also connected through a state-active pathway)

This means the pair has both a direct structural component and a state-dependent
indirect component. The framework should detect both the structural and the
state-sensitive aspect of this pair. In the evaluation, M pairs should reduce both
S-precision (they are not pure S) and C-recall (they are not purely C).

**Threshold note:** All pairs with A_sparse_oo[i,j] ≠ 0 and SAREACHABLE = True are M,
regardless of the relative magnitudes of the direct and indirect contributions. The
magnitude question is post-hoc mechanistic analysis, not part of label assignment.

### What exactly constitutes a null link (N)?

A null link (i→j) exists if and only if:
- A_sparse_oo[i,j] = 0
- LR(i,j) = 0
- NOT SAREACHABLE(i → j)

The pair has no direct coupling and no state-active indirect path. Any residual
correlation between i and j arises from: (a) state-inactive indirect paths through
other observed neurons (should be zero after conditioning), (b) the very small A_lr
background below threshold δ_lr, or (c) finite sample noise.

True null pairs are not "completely zero" — they share some covariance through the
network. But the covariance is not state-dependent and does not involve direct coupling
or state-active routing.

---

## Quantities Explicitly Forbidden from Label Assignment

The following quantities must **not** appear in any label-assignment step:

| Forbidden quantity | Reason |
|---|---|
| Ω(z) or Ω(z₁) − Ω(z₂) | In the framework's estimating family |
| Q(z) or ΔQ | In the framework's estimating family |
| Σ(z) (from Lyapunov equation) | Derived from Ω, same circularity |
| Partial correlations from data | Estimated, finite-sample noise |
| Conditional independence test results | Data-derived |
| Mutual information / transfer entropy | Data-derived |
| Any quantity estimated from simulated trajectories | By construction |
| "Effect of state lesion on observed correlation" | Circular with L2 |

---

## Pre-Commitment Requirement

All labels must be computed and **sealed** (cryptographic hash of label file recorded)
before the first simulation trajectory is generated.

The label file must contain, for every ordered pair (i, j) with i, j ∈ observed set and
i ≠ j:
- DIRECT(i, j)
- LR(i, j)
- SAREACHABLE(i → j)
- Final label ∈ {S, C, M, N, LR}

Any post-hoc modification of labels invalidates the benchmark.

---

## Sanity Checks (Post-Simulation, Not Used for Labeling)

After simulation, the following checks confirm that the constructive labels are
consistent with observed dynamics. These are diagnostic, not definitional.

**Check 1 — State-lesion consistency:** C-labeled pairs should show greater reduction in
conditional dependence under state lesion than N-labeled pairs. This is a one-sided
test: if C pairs do NOT show this, the construction has a problem; if N pairs ALSO show
this, either δ_lr is misset or the state drive is leaking.

**Check 2 — Structural-lesion consistency:** S-labeled pairs should disappear in the
precision graph after structural lesion. If S pairs survive structural lesion with
unchanged magnitude, either A_sparse was not correctly specified or indirect paths are
dominating.

**Check 3 — Class frequency plausibility:** The fraction of C pairs in the total should
be substantially less than 50%. With p=0.15 within-module and p=0.03 between-module
sparse coupling, and modulation restricted to a subset of nodes, C pairs should be rare
compared to N pairs. If C ≥ 20% of all pairs, the construction is likely creating
excessive indirect state-active paths.

**These checks are recorded but do not modify labels.**

---

## Disambiguation of Edge Cases

### Case 1: H1 local interneuron with no gain modulation

An H1 interneuron h with gmod(h)=0 and sdrv(h)=0 is not state-active. Paths through h
do not qualify as state-active paths. Pairs connected only through such H1 neurons are N.

### Case 2: H1 interneuron with gain modulation

An H1 interneuron h with gmod(h)=1 is state-active. Pairs connected through h and
satisfying the other C criteria are labeled C.

### Case 3: H2 global modulator

All H2 neurons are by construction state-active (they receive z-dependent drive). Any
path through an H2 neuron counts as a state-active path. Pairs (i,j) connected only
through H2 neurons (with no direct sparse edge) are labeled C.

### Case 4: Long paths through multiple observed neurons

A path i → o₁ → o₂ → j where o₁ and o₂ are observed neurons: this path does NOT
satisfy condition (iii) of SAREACHABLE unless o₁ or o₂ is state-active (gmod=1 or
sdrv=1). Pure chains of observed-to-observed structural edges create indirect
structural correlations that are captured by the S labels of the intermediate edges,
not by a new C label on (i,j).

### Case 5: Directed asymmetry

Labels are assigned per directed pair: (i→j) and (j→i) may have different labels.
A_sparse_oo[i,j] and A_sparse_oo[j,i] are independently nonzero/zero. The framework
must handle directed evaluation.

### Case 6: Self-loops

Self-loops (i→i) are excluded from the evaluation set.

### Case 7: Low-rank background below threshold

Pairs with LR(i,j) = 0 (below threshold δ_lr) but with (U_o·Vᵀ_o)[i,j] ≠ 0 are treated
as N or C depending on other criteria. The below-threshold low-rank contribution is
treated as negligible background that neither qualifies nor disqualifies a pair for any
label.
