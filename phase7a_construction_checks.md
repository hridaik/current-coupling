# Phase 7A — Construction Verification Checks

## Purpose

This document defines the automated checks that verify the A_sparse matrix, label
array, and H2 coverage conform exactly to the Phase 6B specifications. Every check
is machine-runnable. Every check has a binary PASS/FAIL outcome. All checks must pass
before the acceptance tests (Phase 7A Deliverable 4) are run.

Each check is referenced by a code of the form `CK-XN` where X is a category letter
and N is a number within that category.

---

## Category G — Graph Realization Checks

These checks verify that A_sparse is correctly constructed.

---

### CK-G1 — Neuron count

**What**: Verify the dimensions of A_sparse.

**Check**:
```python
assert A_sparse.shape == (140, 140), \
    f"Expected (140,140), got {A_sparse.shape}"
```

**Pass condition**: A_sparse.shape == (140, 140)

**On failure**: construction error; do not proceed.

---

### CK-G2 — Self-inhibition uniformity

**What**: Verify every diagonal entry equals -1.5.

**Check**:
```python
diagonal = np.diag(A_sparse)
assert np.allclose(diagonal, -1.5, atol=1e-10), \
    f"Diagonal deviates: min={diagonal.min():.6f}, max={diagonal.max():.6f}"
```

**Pass condition**: all |A[k,k] - (-1.5)| < 1e-10

**On failure**: self-inhibition was not applied uniformly.

---

### CK-G3 — No A_lr component

**What**: Verify A = A_sparse only (no low-rank additive component). Since A_lr was
specified as zero in Phase 6B, the full A passed to the simulator must equal A_sparse.

**Check**: this is an identity check — the matrix used in the SDE must be the same
object as A_sparse. Implemented as a pointer/reference check or hash comparison:

```python
assert compute_matrix_hash(A_dynamics) == compute_matrix_hash(A_sparse), \
    "A_dynamics differs from A_sparse — low-rank component may have been added"
```

**Pass condition**: A_dynamics is identical to A_sparse.

---

### CK-G4 — Stability (spectral abscissa)

**What**: Verify all eigenvalues of A have negative real parts with margin.

**Check**:
```python
eigenvalues = np.linalg.eigvals(A_sparse)
spectral_abscissa = np.max(eigenvalues.real)
assert spectral_abscissa < -0.1, \
    f"Spectral abscissa = {spectral_abscissa:.4f} >= -0.1 (unstable)"
```

**Pass condition**: max(Re(λ)) < -0.1

**On failure**: resample off-diagonal weights per the stability protocol
(phase6b_architecture_spec.md Section 2.8). Log each attempt.

---

### CK-G5 — Module assignment consistency

**What**: Verify that all module index ranges are correct and non-overlapping.

Definitions (0-indexed):
- M1 observed: {0, ..., 24}
- M2 observed: {25, ..., 49}
- M3 observed: {50, ..., 74}
- M4 observed: {75, ..., 99}
- M1 H1: {100, ..., 107}
- M2 H1: {108, ..., 115}
- M3 H1: {116, ..., 123}
- M4 H1: {124, ..., 131}
- SA (H2): {132, ..., 139}

**Check**:
```python
MODULE_OBS = {
    'M1': set(range(0, 25)),
    'M2': set(range(25, 50)),
    'M3': set(range(50, 75)),
    'M4': set(range(75, 100)),
}
MODULE_H1 = {
    'M1': set(range(100, 108)),
    'M2': set(range(108, 116)),
    'M3': set(range(116, 124)),
    'M4': set(range(124, 132)),
}
SA = set(range(132, 140))
ALL_NEURONS = set(range(0, 140))

# Verify partition
all_assigned = set().union(*MODULE_OBS.values(), *MODULE_H1.values(), SA)
assert all_assigned == ALL_NEURONS, "Neuron index sets do not cover {0..139}"

# Verify no overlaps
for name_a, set_a in {**MODULE_OBS, **MODULE_H1, 'SA': SA}.items():
    for name_b, set_b in {**MODULE_OBS, **MODULE_H1, 'SA': SA}.items():
        if name_a != name_b:
            overlap = set_a & set_b
            assert len(overlap) == 0, f"Overlap between {name_a} and {name_b}: {overlap}"
```

**Pass condition**: all sets are disjoint and their union is {0,...,139}.

---

### CK-G6 — H2 target module assignments

**What**: Verify that the H2→target-module mapping matches the spec exactly.

```python
H2_TARGETS = {
    132: {'M1', 'M2'},
    133: {'M1', 'M2'},
    134: {'M3', 'M4'},
    135: {'M3', 'M4'},
    136: {'M1', 'M3'},
    137: {'M2', 'M4'},
    138: {'M1', 'M4'},
    139: {'M2', 'M3'},
}
# Verify this dict is hardcoded and matches spec
assert set(H2_TARGETS.keys()) == SA
for h2, targets in H2_TARGETS.items():
    assert len(targets) == 2, f"H2 {h2} has {len(targets)} targets, expected 2"
```

**Pass condition**: H2_TARGETS matches the architecture spec exactly.
This check is a code review / constant verification check.

---

### CK-G7 — Forbidden edges: H2-H2

**What**: Verify no H2 neuron receives input from another H2 neuron.

**Check**:
```python
for h2_src in SA:
    for h2_dst in SA:
        assert A_sparse[h2_dst, h2_src] == 0.0, \
            f"Forbidden H2→H2 edge: {h2_src} → {h2_dst}, weight={A_sparse[h2_dst, h2_src]}"
```

**Pass condition**: A_sparse[h, h'] = 0 for all h, h' ∈ SA.

---

### CK-G8 — Forbidden edges: H1-H2 and H2-H1

**What**: Verify no H1 neuron connects to any H2 neuron and vice versa.

**Check**:
```python
ALL_H1 = set().union(*MODULE_H1.values())  # {100,...,131}

for h1 in ALL_H1:
    for h2 in SA:
        assert A_sparse[h2, h1] == 0.0, \
            f"Forbidden H1→H2 edge: {h1} → {h2}"
        assert A_sparse[h1, h2] == 0.0, \
            f"Forbidden H2→H1 edge: {h2} → {h1}"
```

**Pass condition**: A_sparse[h2, h1] = 0 and A_sparse[h1, h2] = 0 for all h1 ∈ H1, h2 ∈ SA.

---

### CK-G9 — Forbidden edges: H1-H1

**What**: Verify no H1 neuron connects to any other H1 neuron.

**Check**:
```python
for h1_a in ALL_H1:
    for h1_b in ALL_H1:
        if h1_a != h1_b:
            assert A_sparse[h1_b, h1_a] == 0.0, \
                f"Forbidden H1→H1 edge: {h1_a} → {h1_b}"
```

**Pass condition**: A_sparse[h1_b, h1_a] = 0 for all distinct h1_a, h1_b ∈ H1.

---

### CK-G10 — H1 cross-module connections forbidden

**What**: Verify that H1 neurons only connect to observed neurons in their assigned module.

**Check**:
```python
for module, h1_set in MODULE_H1.items():
    out_of_module_obs = set(range(0, 100)) - MODULE_OBS[module]
    for h1 in h1_set:
        for obs in out_of_module_obs:
            assert A_sparse[obs, h1] == 0.0, \
                f"Forbidden out-of-module H1→obs: {h1}(mod {module}) → {obs}"
            assert A_sparse[h1, obs] == 0.0, \
                f"Forbidden out-of-module obs→H1: {obs} → {h1}(mod {module})"
```

**Pass condition**: H1 neurons have zero entries for all observed neurons outside their module.

---

### CK-G11 — H2 out-of-target connections forbidden

**What**: Verify H2 neurons only connect to observed neurons in their target modules.

**Check**:
```python
for h2, targets in H2_TARGETS.items():
    target_obs = set().union(*[MODULE_OBS[m] for m in targets])
    non_target_obs = set(range(0, 100)) - target_obs
    for obs in non_target_obs:
        assert A_sparse[obs, h2] == 0.0, \
            f"Forbidden out-of-target H2→obs: {h2} → {obs}"
        assert A_sparse[h2, obs] == 0.0, \
            f"Forbidden out-of-target obs→H2: {obs} → {h2}"
```

**Pass condition**: H2 neurons have zero entries for all observed neurons outside their target modules.

---

### CK-G12 — Observed-to-observed block upper-triangular and lower-triangular are both allowed

**What**: Verify the observed-to-observed block has the expected sparsity character.
(This is a soft check, not a hard constraint — the sparsity is random.)

**Check** (monitoring, not a hard assertion):
```python
oo_block = A_sparse[:100, :100]
np.fill_diagonal(oo_block_copy := oo_block.copy(), 0)  # exclude diagonal

# Count edges within and between modules
within_edges = 0
within_possible = 0
between_edges = 0
between_possible = 0

for mod_a, obs_a in MODULE_OBS.items():
    for mod_b, obs_b in MODULE_OBS.items():
        for i in obs_a:
            for j in obs_b:
                if i == j:
                    continue
                w = oo_block[j, i]  # edge i → j
                if mod_a == mod_b:
                    within_possible += 1
                    if w != 0: within_edges += 1
                else:
                    between_possible += 1
                    if w != 0: between_edges += 1

p_within_realized = within_edges / within_possible
p_between_realized = between_edges / between_possible

# Soft assertion: within ±4 sigma of expected binomial
import scipy.stats
p_within_lo = scipy.stats.binom.ppf(0.0001, within_possible, 0.15) / within_possible
p_within_hi = scipy.stats.binom.ppf(0.9999, within_possible, 0.15) / within_possible
p_between_lo = scipy.stats.binom.ppf(0.0001, between_possible, 0.03) / between_possible
p_between_hi = scipy.stats.binom.ppf(0.9999, between_possible, 0.03) / between_possible

assert p_within_lo <= p_within_realized <= p_within_hi, \
    f"p_within_realized={p_within_realized:.4f} outside [{p_within_lo:.4f}, {p_within_hi:.4f}]"
assert p_between_lo <= p_between_realized <= p_between_hi, \
    f"p_between_realized={p_between_realized:.4f} outside [{p_between_lo:.4f}, {p_between_hi:.4f}]"
```

**Pass condition**: realized sparsity fractions fall within the 4-sigma range of the
expected binomial distribution. (Extremely unlikely to fail if seed 42 is used correctly.)

---

## Category L — Label Realization Checks

These checks verify that the label array is correctly generated from A_sparse.

---

### CK-L1 — Total pair count

**What**: Verify exactly 9,900 labels are generated.

**Check**:
```python
assert len(labels) == 9900, \
    f"Expected 9900 labels, got {len(labels)}"
```

**Pass condition**: |labels| = 9,900

---

### CK-L2 — Coverage: every valid pair has a label

**What**: Verify every ordered pair (i,j) with i≠j and i,j ∈ {0,...,99} has exactly one label.

**Check**:
```python
expected_pairs = {(i, j) for i in range(100) for j in range(100) if i != j}
actual_pairs = {(r['i'], r['j']) for r in labels}
assert expected_pairs == actual_pairs, \
    f"Missing pairs: {expected_pairs - actual_pairs}; extra pairs: {actual_pairs - expected_pairs}"
```

**Pass condition**: label set covers exactly the 9,900 valid pairs.

---

### CK-L3 — Label vocabulary

**What**: Verify all labels are one of the four valid strings.

**Check**:
```python
valid_labels = {'S', 'C', 'M', 'N'}
for record in labels:
    assert record['label'] in valid_labels, \
        f"Invalid label '{record['label']}' for pair ({record['i']}, {record['j']})"
```

**Pass condition**: all labels in {'S', 'C', 'M', 'N'}.

---

### CK-L4 — Mutual exclusivity and completeness

**What**: Verify label counts sum to 9,900 and all are positive.

**Check**:
```python
from collections import Counter
counts = Counter(r['label'] for r in labels)
assert set(counts.keys()) == {'S', 'C', 'M', 'N'}, \
    f"Missing label classes: {{'S','C','M','N'} - set(counts.keys())}"
assert sum(counts.values()) == 9900, \
    f"Counts sum to {sum(counts.values())}, expected 9900"
for lbl, cnt in counts.items():
    assert cnt > 0, f"Label class {lbl} has zero members"
```

**Pass condition**: each class is non-empty and counts sum to 9,900.

---

### CK-L5 — Label consistency with DIRECT

**What**: For every S- or M-labeled pair, verify A_sparse[j, i] ≠ 0 (DIRECT=1).
For every C- or N-labeled pair, verify A_sparse[j, i] = 0 (DIRECT=0).

**Check**:
```python
for record in labels:
    i, j, lbl = record['i'], record['j'], record['label']
    direct = (A_sparse[j, i] != 0.0)

    if lbl in ('S', 'M'):
        assert direct, \
            f"Pair ({i},{j}) labeled {lbl} but A_sparse[{j},{i}]=0 (DIRECT should be 1)"
    elif lbl in ('C', 'N'):
        assert not direct, \
            f"Pair ({i},{j}) labeled {lbl} but A_sparse[{j},{i}]≠0 (DIRECT should be 0)"
```

**Pass condition**: all 9,900 pairs pass the DIRECT consistency check.

---

### CK-L6 — Label consistency with SAREACHABLE

**What**: For every C- or M-labeled pair, verify ∃ h ∈ SA with A[h,i]≠0 and A[j,h]≠0.
For every S- or N-labeled pair, verify no such h exists.

**Check**:
```python
def compute_sareachable(i, j, A_sparse, SA):
    for h in SA:
        if A_sparse[h, i] != 0.0 and A_sparse[j, h] != 0.0:
            return True, h
    return False, None

for record in labels:
    i, j, lbl = record['i'], record['j'], record['label']
    sareachable, witness = compute_sareachable(i, j, A_sparse, SA)

    if lbl in ('C', 'M'):
        assert sareachable, \
            f"Pair ({i},{j}) labeled {lbl} but SAREACHABLE=False"
    elif lbl in ('S', 'N'):
        assert not sareachable, \
            f"Pair ({i},{j}) labeled {lbl} but SAREACHABLE=True (witness: {witness})"
```

**Pass condition**: all 9,900 pairs pass the SAREACHABLE consistency check.

**Note**: this is an O(9900 × 8) = 79,200-operation check. It completes in milliseconds.

---

### CK-L7 — Witness field correctness

**What**: For C- and M-labeled pairs, verify the `witness_h2` field stores the
lowest-index H2 that witnesses SAREACHABLE. For S- and N-labeled pairs, verify
`witness_h2` is null.

**Check**:
```python
for record in labels:
    i, j, lbl = record['i'], record['j'], record['label']
    wh = record['witness_h2']

    if lbl in ('S', 'N'):
        assert wh is None, \
            f"Pair ({i},{j}) labeled {lbl} should have witness_h2=null, got {wh}"
    else:  # C or M
        assert wh is not None, \
            f"Pair ({i},{j}) labeled {lbl} has witness_h2=null"
        assert wh in SA, \
            f"Pair ({i},{j}) witness_h2={wh} is not in SA"
        # Verify it is the lowest-index witness
        assert A_sparse[wh, i] != 0.0 and A_sparse[j, wh] != 0.0, \
            f"Recorded witness {wh} does not actually witness pair ({i},{j})"
        # Verify no lower-index witness exists
        for h_lower in SA:
            if h_lower < wh:
                if A_sparse[h_lower, i] != 0.0 and A_sparse[j, h_lower] != 0.0:
                    assert False, \
                        f"Pair ({i},{j}): lower-index witness {h_lower} exists but {wh} recorded"
```

**Pass condition**: all witness fields are correct.

---

## Category H — H2 Coverage Checks

These checks verify that the H2 topology produces the expected module-pair coverage.

---

### CK-H1 — Every module pair has at least one H2 neuron

**What**: Verify all 6 module pairs have at least one H2 neuron with both modules as targets.

**Check**:
```python
import itertools

MODULE_NAMES = ['M1', 'M2', 'M3', 'M4']
covered_pairs = set()
for h2, targets in H2_TARGETS.items():
    # Add both orderings of the module pair
    target_list = sorted(targets)
    covered_pairs.add(tuple(target_list))

all_pairs = set(tuple(sorted(p)) for p in itertools.combinations(MODULE_NAMES, 2))
assert all_pairs == covered_pairs, \
    f"Uncovered module pairs: {all_pairs - covered_pairs}"
```

**Pass condition**: all 6 module pairs appear in at least one H2 neuron's target set.

---

### CK-H2 — Exact H2 count per module pair

**What**: Verify that {M1,M2} and {M3,M4} each have exactly 2 H2 neurons, and all
other pairs have exactly 1.

**Check**:
```python
pair_counts = Counter()
for h2, targets in H2_TARGETS.items():
    key = tuple(sorted(targets))
    pair_counts[key] += 1

EXPECTED_COUNTS = {
    ('M1', 'M2'): 2,
    ('M3', 'M4'): 2,
    ('M1', 'M3'): 1,
    ('M2', 'M4'): 1,
    ('M1', 'M4'): 1,
    ('M2', 'M3'): 1,
}

for pair, expected in EXPECTED_COUNTS.items():
    actual = pair_counts[pair]
    assert actual == expected, \
        f"Module pair {pair}: expected {expected} H2 neurons, got {actual}"
```

**Pass condition**: each module pair has exactly the specified number of H2 neurons.

---

### CK-H3 — Each module targeted by exactly 4 H2 neurons

**What**: Verify each module appears in exactly 4 H2 target sets.

**Check**:
```python
module_h2_count = Counter()
for h2, targets in H2_TARGETS.items():
    for m in targets:
        module_h2_count[m] += 1

for module in MODULE_NAMES:
    assert module_h2_count[module] == 4, \
        f"Module {module} targeted by {module_h2_count[module]} H2 neurons, expected 4"
```

**Pass condition**: each module appears in exactly 4 H2 target sets.

---

### CK-H4 — No H2 neuron targets more than 2 modules

**What**: Verify the no H2 neuron has more than 2 target modules (per spec, each has exactly 2).

**Check**:
```python
for h2, targets in H2_TARGETS.items():
    assert len(targets) == 2, \
        f"H2 neuron {h2} has {len(targets)} target modules, expected exactly 2"
```

**Pass condition**: all H2 neurons have exactly 2 target modules.

---

## Check Execution Order

All checks must be run in this order. Each check must PASS before the next group begins.

**Stage 1 — Run CK-G1 through CK-G4** (basic matrix properties and stability)

**Stage 2 — Run CK-G5 through CK-G11** (topology and forbidden edges) and
**CK-H1 through CK-H4** (H2 coverage) in parallel

**Stage 3 — Run CK-G12** (soft sparsity plausibility)

**Stage 4 — Run CK-L1 through CK-L4** (label count and vocabulary)

**Stage 5 — Run CK-L5 through CK-L7** (label-matrix consistency)

If any check in a stage fails, subsequent stages do not run.

---

## Check Summary Table

| Code | Category | What it checks | Hard/Soft |
|---|---|---|---|
| CK-G1 | Graph | Matrix dimensions (140×140) | Hard |
| CK-G2 | Graph | Diagonal = -1.5 for all neurons | Hard |
| CK-G3 | Graph | A_dynamics = A_sparse (no A_lr) | Hard |
| CK-G4 | Graph | Spectral abscissa < -0.1 | Hard |
| CK-G5 | Graph | Module index partition | Hard |
| CK-G6 | Graph | H2 target module spec | Hard |
| CK-G7 | Graph | No H2→H2 edges | Hard |
| CK-G8 | Graph | No H1↔H2 edges | Hard |
| CK-G9 | Graph | No H1→H1 edges | Hard |
| CK-G10 | Graph | H1 stays in assigned module | Hard |
| CK-G11 | Graph | H2 stays in target modules | Hard |
| CK-G12 | Graph | Sparsity within expected range | Soft |
| CK-L1 | Label | Exactly 9,900 labels | Hard |
| CK-L2 | Label | All valid pairs covered | Hard |
| CK-L3 | Label | Labels in {S,C,M,N} | Hard |
| CK-L4 | Label | Counts sum to 9,900; all classes non-empty | Hard |
| CK-L5 | Label | DIRECT consistent with A_sparse | Hard |
| CK-L6 | Label | SAREACHABLE consistent with A_sparse and SA | Hard |
| CK-L7 | Label | Witness field correct for all pairs | Hard |
| CK-H1 | H2 coverage | All 6 module pairs covered | Hard |
| CK-H2 | H2 coverage | Exact H2 counts per module pair | Hard |
| CK-H3 | H2 coverage | Each module targeted by 4 H2 neurons | Hard |
| CK-H4 | H2 coverage | Each H2 targets exactly 2 modules | Hard |

All hard checks must pass. Soft checks are logged but do not block progress.
