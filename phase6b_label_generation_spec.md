# Phase 6B — Label Generation Specification

## Purpose

This document specifies the exact procedure for generating ground-truth labels for all
9,900 directed observed-neuron pairs. Labels must be computed before any simulation is
run. They depend only on the construction parameters defined in
`phase6b_architecture_spec.md`. They do not depend on any simulated trajectory, any
estimated statistical quantity, or any output of the framework.

This is the most important document in Phase 6B. Errors here invalidate the entire
benchmark.

---

## Hard Constraints

**Constraint 1 — Construction-exclusivity**:
Every label must be derivable from the following inputs alone:

- A_sparse (the fixed coupling matrix, known from construction)
- SA = {133, 134, 135, 136, 137, 138, 139, 140} (H2 index set, known from construction)
- Module assignments (known from construction)
- H2 target module assignments (known from construction)

No other input is permitted.

**Constraint 2 — Framework-independence**:
The following quantities are explicitly **forbidden** from the label generation procedure:

| Forbidden | Why |
|---|---|
| Σ(z), Ω(z) = Σ(z)⁻¹, or any Lyapunov-equation output | In framework's estimating family |
| Q(z) (probability current) | In framework's estimating family |
| ΔΩ, ΔQ, or any state difference of these | Circular |
| Partial correlations | Estimated from data |
| Any quantity derived from simulated x(t) | By definition |
| Conditional independence test outcomes | Data-derived |
| Any effect of virtual lesions on simulated data | Circular (see leakage audit below) |

**Why even analytical Ω is forbidden**: the framework estimates Ω̂ → Ω_true as T → ∞.
If ground truth C is defined via Ω_true (e.g., "ΔΩ_true[i,j] is large"), then the
framework trivially approaches perfect performance as T increases. This tests estimation
variance, not conceptual validity. Ground truth must be defined at the level of
circuit topology.

---

## Definitions

### State-active set

```
SA = {h : h is an H2 neuron} = {133, 134, 135, 136, 137, 138, 139, 140}
```

A neuron h is state-active if and only if it receives z-dependent external drive
(B_h(z) = γ_H2 × z ≠ 0 for z ≠ 0). By the architecture specification, exactly the H2
neurons satisfy this condition.

### Direct structural indicator

For each ordered pair (i, j) with i ≠ j and both i, j ∈ {1, ..., 100} (observed set):

```
DIRECT(i → j) = 1   if A_sparse[j, i] ≠ 0
              = 0   otherwise
```

Note: A_sparse[j, i] ≠ 0 means neuron i drives neuron j (i → j coupling exists).
The self-inhibition entries A[k,k] = -1.5 are excluded (self-loops are not evaluated).

### State-active reachability

For each ordered pair (i, j) with i ≠ j and both i, j ∈ {1, ..., 100}:

```
SAREACHABLE(i → j) = True
```

if and only if there exists an H2 neuron h ∈ SA such that:

```
(a) A_sparse[h, i] ≠ 0    (neuron i projects to H2 neuron h)
(b) A_sparse[j, h] ≠ 0    (H2 neuron h projects to neuron j)
```

Both conditions must hold simultaneously for the same h.

**Why this two-hop definition is complete**: the architecture specification forbids H2–H2
connections and H1–H2 connections. Therefore no hidden-to-hidden edges exist. All paths
from observed neuron i to H2 neuron h that do not pass through other observed neurons
are exactly the direct edges A[h, i]. All paths from H2 to observed neuron j are exactly
A[j, h]. The only valid state-active paths of the form obs → (hidden)* → obs are
therefore exactly the two-hop paths obs → H2 → obs. There are no longer valid paths
because: (1) H2–H2 connections are forbidden (no chain obs→H2→H2→obs), (2) H1–H2
connections are forbidden (no path obs→H1→H2→obs or obs→H2→H1→obs), and (3) any
path that passes through an intermediate observed neuron is d-separated by conditioning
on that neuron (it cannot contribute to the marginal precision matrix).

**Why conditioning on intermediate observed neurons matters**: in a linear Gaussian
system, the precision matrix Ω_obs (the inverse of the marginal covariance of observed
neurons) has Ω_obs[i,j] = 0 if and only if the path from i to j passes only through
observed neurons (which can be conditioned out). Hidden neurons that lie on the path
cannot be conditioned out, so they create nonzero entries in Ω_obs even when A[j,i] = 0.
The SAREACHABLE criterion captures exactly the paths that cannot be d-separated by
conditioning on observed neurons.

---

## Label Assignment Rules

For each ordered pair (i, j) with i ≠ j and i, j ∈ {1, ..., 100}:

### Step 1 — Compute DIRECT(i → j)

```
DIRECT = 1   if A_sparse[j, i] ≠ 0   else 0
```

### Step 2 — Compute SAREACHABLE(i → j)

```
SAREACHABLE = 1   if any h in SA satisfies both A_sparse[h,i]≠0 and A_sparse[j,h]≠0
              0   otherwise
```

### Step 3 — Assign label

```
if   DIRECT = 1  and  SAREACHABLE = 0:   Label = S   (structural only)
if   DIRECT = 1  and  SAREACHABLE = 1:   Label = M   (mixed)
if   DIRECT = 0  and  SAREACHABLE = 1:   Label = C   (current-supported only)
if   DIRECT = 0  and  SAREACHABLE = 0:   Label = N   (null)
```

These four cases are mutually exclusive and exhaustive. Every directed pair receives
exactly one label.

---

## Formal Definitions

### Class S (Structural only)

**Formal**: Label(i→j) = S if and only if A_sparse[j,i] ≠ 0 AND there is no H2 neuron
h ∈ {133,...,140} such that both A_sparse[h,i] ≠ 0 and A_sparse[j,h] ≠ 0.

**Graph-theoretic**: i has a direct edge to j in A_sparse. i is not the source of any
two-hop path i→h→j through a state-active hidden neuron.

**Inclusion criteria**:
- Observed-to-observed direct coupling exists in the observed-observed block
- No state-active indirect path connects this same pair

**Exclusion criteria**:
- A_sparse[j,i] = 0 (would be C or N)
- SAREACHABLE (would be M)

**Interpretation**: i directly drives j through an anatomical connection. This coupling
exists at all values of z. The state z does not create or substantially amplify any
additional indirect route between this pair.

---

### Class C (Current-supported only)

**Formal**: Label(i→j) = C if and only if A_sparse[j,i] = 0 AND there exists at least
one H2 neuron h ∈ {133,...,140} such that A_sparse[h,i] ≠ 0 and A_sparse[j,h] ≠ 0.

**Graph-theoretic**: i has no direct edge to j in A_sparse. There exists a two-hop path
i→h→j through at least one state-active hidden neuron h.

**Inclusion criteria**:
- No direct observed-to-observed coupling
- At least one complete state-active two-hop path i→H2→j exists

**Exclusion criteria**:
- A_sparse[j,i] ≠ 0 (would be S or M)
- No complete two-hop state-active path exists (would be N)

**Interpretation**: i and j have no direct anatomical connection in the observed-neuron
subgraph. However, i drives at least one H2 neuron, which in turn drives j. H2 neurons
are driven by z. When z is large (high modulation state), H2 neurons are strongly
activated, propagating i's activity to j through the H2 relay. The i-j correlation is
therefore state-dependent: it is amplified at high |z| and reduced at z ≈ 0.

**What makes this genuinely current-supported and not merely a long structural path**:
H2 neurons are in SA — they receive z-dependent external drive γ_H2 × z. The effective
propagation along the path i→H2→j scales with the activity of H2, which is elevated in
high-z states. The pair (i,j) is not connected by a passive structural relay; it is
connected by a dynamically activated relay whose activity level depends on network state.
This is the sense in which the link is "current-supported."

---

### Class M (Mixed)

**Formal**: Label(i→j) = M if and only if A_sparse[j,i] ≠ 0 AND there exists at least
one H2 neuron h ∈ {133,...,140} such that A_sparse[h,i] ≠ 0 and A_sparse[j,h] ≠ 0.

**Graph-theoretic**: i has a direct edge to j AND a two-hop state-active path i→H2→j.

**Inclusion criteria**:
- Direct coupling in observed-observed block
- At least one complete state-active two-hop path

**Interpretation**: two independent mechanisms connect i to j. The direct structural edge
is always active regardless of z. The H2-mediated indirect path is additionally active
in high-|z| states. The total effective coupling from i to j is stronger in high-z states
than in low-z states.

The framework must correctly identify M pairs as having both a structural and a
state-dependent component. M pairs are important test cases because a framework that
only looks for off-structural C links will miss the state-sensitive component of M, and
a framework that only looks for structural links will miss the C component.

---

### Class N (Null)

**Formal**: Label(i→j) = N if and only if A_sparse[j,i] = 0 AND there is no H2 neuron
h ∈ {133,...,140} such that both A_sparse[h,i] ≠ 0 and A_sparse[j,h] ≠ 0.

**Graph-theoretic**: no direct edge from i to j, and no complete two-hop state-active
path from i to j.

**Exclusion criteria**:
- A_sparse[j,i] ≠ 0 (would be S or M)
- SAREACHABLE (would be C)

**Note on residual correlations**: N-labeled pairs may still show nonzero empirical
correlations arising from: (a) shared H1 interneuron inputs (H1 creates correlation
but H1 is NOT state-active, so this correlation is not state-dependent), (b) long
multi-hop paths through observed neurons (these paths can be conditioned out in the
precision graph), (c) shared noise via D_lr (very small). None of these create entries
in Ω_obs[i,j] at leading order, so N-labeled pairs appear as near-zero precision entries.

This is correct: the framework should find small Ω values for N pairs, which it can
then threshold to N classification. The residual correlations are not test failures.

---

## Leakage Audit

For each label class, this section proves that the label **cannot be reconstructed from
framework outputs** by construction.

### S labels

S-labeled pairs satisfy A_sparse[j,i] ≠ 0 and NOT SAREACHABLE. The framework recovers
Ω̂ and Q̂ from x_obs(t). It does not observe A_sparse. Knowledge of Ω̂ tells you that
(i,j) is in the non-null set (Ω̂[i,j] large), but does not distinguish whether the
nonzero precision entry arises from a direct structural edge (S) or from a hidden-H2-
mediated two-hop path (C). Both S and C create nonzero Ω̂[i,j]. The S/C distinction
requires access to A_sparse, which is inaccessible to the framework. **No leakage.**

### C labels

C-labeled pairs satisfy A_sparse[j,i] = 0 and SAREACHABLE. The framework may estimate
a large ΔΩ̂[i,j] for C pairs (because z-modulation affects the H2-mediated path). But
the framework cannot verify that A_sparse[j,i] = 0 from observation alone — it must
infer this. The ground truth label is assigned from the known A_sparse, not from ΔΩ̂.
If the framework's ΔΩ̂ is large for a C pair, that is a correct detection. If it is
small (type II error), the pair is still C. The label does not use ΔΩ̂. **No leakage.**

### M labels

M-labeled pairs satisfy both A_sparse[j,i] ≠ 0 and SAREACHABLE. A framework that
estimates ΔΩ̂ will find these pairs have both large Ω̂ (direct coupling) and large ΔΩ̂
(state sensitivity). The framework cannot reconstruct the M label from its outputs
without independently recovering A_sparse. **No leakage.**

### N labels

N-labeled pairs satisfy A_sparse[j,i] = 0 and NOT SAREACHABLE. The framework should
find small Ω̂ and small ΔΩ̂ for N pairs. If the framework assigns label N to these
pairs, it is because of small estimated values, not because it knows A_sparse[j,i] = 0.
Finite-sample noise may cause some N pairs to appear non-null. These are false positives
from the framework, not label leakage. **No leakage.**

### The SAREACHABLE criterion and its independence from framework quantities

The critical concern (vulnerability L1 in Phase 6A review) was that SAREACHABLE might
be operationally equivalent to "ΔΩ_true[i,j] is large." This would make the label
equivalent to the framework's output at infinite data.

**This equivalence does not hold** in the present architecture, for the following reason:

SAREACHABLE(i→j) = True requires the simultaneous existence of edges A_sparse[h,i] ≠ 0
AND A_sparse[j,h] ≠ 0 for some h ∈ SA. This is a statement about the sparsity pattern
of A_sparse (two specific binary random variables), not about any derived statistical
quantity. Two pairs (i₁→j₁) and (i₂→j₂) could have identical ΔΩ values but different
SAREACHABLE labels if one has the required H2 path and one does not. Conversely, two
pairs could both be SAREACHABLE but with different ΔΩ values depending on the weight
magnitudes A[h,i] and A[j,h].

The SAREACHABLE criterion is coarser than ΔΩ: it is a binary (path exists / does not
exist) indicator that ignores path weights. ΔΩ is a continuous quantity that depends
on path weights. They are correlated (stronger path → larger ΔΩ) but not equivalent.
In particular:
- A pair can be SAREACHABLE with A[h,i] ≈ 0 (very small weight): ΔΩ ≈ 0, label = C.
- A pair can be non-SAREACHABLE but have large ΔΩ from a longer multi-hop route through
  observed neurons: label = N (conditioned out), ΔΩ nonzero in marginal statistics.

The framework cannot reconstruct SAREACHABLE from ΔΩ̂ alone. **Leakage is eliminated.**

---

## Expected Class Counts (Pre-computed, Not Derived from Simulation)

These counts are computed from the parameter values in `phase6b_architecture_spec.md`
as expected values over the random construction. The actual counts will vary by ±5–10%
depending on the random seed.

### Within-module pairs (4 modules × 25 × 24 = 2,400 directed pairs)

Let f_R = P(SAREACHABLE within module). For a within-module pair, SAREACHABLE requires
a path through one of the 4 H2 neurons that target that module:

```
P(path via single H2) = p_H2_in × p_H2_out = 0.20 × 0.20 = 0.04
P(SAREACHABLE) = 1 - (1 - 0.04)^4 = 1 - 0.96^4 ≈ 0.152
```

| Label | P(label) | Expected count |
|---|---|---|
| S | 0.15 × (1-0.152) = 0.127 | 305 |
| M | 0.15 × 0.152 = 0.023 | 55 |
| C | 0.85 × 0.152 = 0.129 | 310 |
| N | 0.85 × (1-0.152) = 0.720 | 1,730 |

### Between-module pairs — heavy (M1-M2 and M3-M4; 2 pairs × 2 directions × 625 = 2,500 directed pairs)

2 H2 neurons target each of these module pairs:

```
P(SAREACHABLE) = 1 - (1 - 0.04)^2 = 1 - 0.96^2 ≈ 0.077
```

| Label | P(label) | Expected count |
|---|---|---|
| S | 0.03 × (1-0.077) = 0.028 | 69 |
| M | 0.03 × 0.077 = 0.002 | 6 |
| C | 0.97 × 0.077 = 0.075 | 187 |
| N | 0.97 × (1-0.077) = 0.895 | 2,238 |

### Between-module pairs — light (other 4 pairs; 4 × 2 × 625 = 5,000 directed pairs)

1 H2 neuron targets each of these module pairs:

```
P(SAREACHABLE) = 0.04
```

| Label | P(label) | Expected count |
|---|---|---|
| S | 0.03 × 0.96 = 0.029 | 144 |
| M | 0.03 × 0.04 = 0.001 | 6 |
| C | 0.97 × 0.04 = 0.039 | 194 |
| N | 0.97 × 0.96 = 0.931 | 4,656 |

### Totals

| Label | Expected count | Fraction |
|---|---|---|
| S | 518 | 5.2% |
| M | 67 | 0.7% |
| C | 691 | 7.0% |
| N | 8,624 | 87.1% |
| **Total** | **9,900** | 100% |

**Imbalance check**: |C|/|S| ≈ 1.33. C and S have similar counts. This prevents the
S-class from trivially dominating and ensures the S↔C confusion matrix is informative.

**Non-null fraction**: (|S|+|M|+|C|) / total ≈ 12.9%. All metrics are primarily
reported over the 1,276 non-null pairs.

---

## Algorithmic Implementation

The implementer must execute the following procedure exactly once, before any simulation:

```python
# Pseudocode — to be translated into the implementation language

import numpy as np

def generate_labels(A_sparse, SA, N_obs=100):
    """
    A_sparse: (140,140) array, A_sparse[k,j] = coupling from j to k
    SA: list of H2 indices [133,134,135,136,137,138,139,140] (0-indexed: [132,...,139])
    N_obs: number of observed neurons (indices 0..99 in 0-indexed)
    Returns: labels dict { (i,j): label } for all i!=j in 0..N_obs-1
    """
    labels = {}
    SA_set = set(SA)

    for i in range(N_obs):
        for j in range(N_obs):
            if i == j:
                continue

            # Step 1: direct coupling j->i in A_sparse (A[j,i] means i drives j)
            direct = (A_sparse[j, i] != 0)

            # Step 2: state-active reachability via any H2 neuron
            sareachable = False
            for h in SA_set:
                if A_sparse[h, i] != 0 and A_sparse[j, h] != 0:
                    sareachable = True
                    break

            # Step 3: assign label
            if direct and not sareachable:
                labels[(i, j)] = 'S'
            elif direct and sareachable:
                labels[(i, j)] = 'M'
            elif not direct and sareachable:
                labels[(i, j)] = 'C'
            else:
                labels[(i, j)] = 'N'

    return labels
```

Time complexity: O(N_obs² × |SA|) = O(100² × 8) = 80,000 operations. Completes in
milliseconds.

---

## Pre-Commitment Protocol

1. Run `generate_labels(A_sparse, SA)` on the constructed A_sparse.
2. Serialize the label dictionary to a canonical format (JSON, sorted by key).
3. Compute SHA-256 hash of the serialized file.
4. Record hash in `phase6b_pre_registration.md` under "Frozen quantities."
5. Lock the label file. No modification permitted after this step.
6. Verify: run all five conditions (oracle_z, blind_z, etc.) and collect framework outputs.
7. After all framework outputs are saved, load the locked label file and compute metrics.
8. Verify SHA-256 hash of the label file before metric computation.

---

## Sanity Checks (Post-Label-Generation, Pre-Simulation)

These do not modify labels. They confirm the construction is well-formed.

**Check LG1 — Class count plausibility**:
Verify |C| ≥ 20, |S| ≥ 20, |M| ≥ 5. If any class has fewer than 5 members,
the random construction is degenerate; resample with seed + 1000.

**Check LG2 — C-label H2 pathway audit**:
For every pair labeled C, verify that the H2 path witnessing SAREACHABLE is recorded
in the label file (store the witnessing H2 index h). This allows post-hoc attribution
of false-C detections to specific H2 neurons.

**Check LG3 — S-label isolation**:
For every pair labeled S, verify that no H2 neuron h has both A[h,i] ≠ 0 and
A[j,h] ≠ 0. This is a redundant check of the label assignment logic.

**Check LG4 — Symmetry audit**:
Verify that the directed nature of labels is respected: for any pair (i,j) labeled C,
(j,i) may be labeled S, M, C, or N — there is no required symmetry.
Report the fraction of C pairs where the reverse (j,i) is also C, S, M, or N.
