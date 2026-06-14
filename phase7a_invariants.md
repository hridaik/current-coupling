# Phase 7A — System Invariants

## Purpose

This document lists every invariant the simulator must maintain. Each invariant is:
- stated as a formal condition
- explained (what it protects)
- given a machine-checkable test
- classified by when it can be checked (construction-time, runtime, or post-hoc)

Invariants are grouped by the system component they govern.

Violation of any invariant is a **protocol error** that invalidates any results produced
while the invariant was violated.

---

## Category A — Coupling Matrix Invariants

### INV-A1: A is fixed throughout all simulations

**Statement**: For all time steps t and all simulation runs r, the matrix A passed to
the integrator is identical to A_sparse as constructed and hashed.

```python
# At each integration step (or verified pre-simulation):
assert compute_matrix_hash(A_used_in_step) == A_SPARSE_HASH
```

**What it protects**: The ground truth labels are derived from A_sparse. If A changes
during simulation, the labels no longer correspond to the dynamics being simulated.

**When to check**: Once before simulation starts (hash comparison). Runtime check would
be too expensive; rely on code review to confirm A is never reassigned.

**Checkable at**: construction-time (hash comparison) + code review

---

### INV-A2: No gain modulation (A does not depend on z)

**Statement**: The matrix A passed to the integrator is the same object regardless of
the current value of z(t).

```python
# B(z) encapsulates all z-dependence; A is never multiplied by any function of z
# Code review check: search for patterns like A * g(z), diag(z) @ A, etc.
assert 'A_eff' not in simulator_code  # no "effective A" variable exists
assert 'gain' not in variable_names_used_in_integrator
```

**What it protects**: If gain modulation is accidentally introduced (e.g., by scaling A
by z for any neuron), the label derivation — which assumes B(z) is the only z-dependent
term — becomes incorrect.

**When to check**: Code review before implementation begins; static analysis on integrator code.

**Checkable at**: code review / static analysis

---

### INV-A3: Spectral abscissa of A is negative

**Statement**: max(Re(λ_k)) < -0.1 where λ_k are the eigenvalues of A_sparse.

```python
eigenvalues = np.linalg.eigvals(A_sparse)
assert np.max(eigenvalues.real) < -0.1
```

**What it protects**: If A is unstable, the SDE diverges, producing infinite or NaN
trajectories. The benchmark becomes unusable.

**When to check**: Construction-time (CK-G4). Re-check if any weight modification occurs.

**Checkable at**: construction-time

---

### INV-A4: A_lr = 0

**Statement**: A contains no low-rank additive component. A = A_sparse only.

```python
# Verified by CK-G3: hash of A used in dynamics == hash of A_sparse
assert A_used_in_sim is A_sparse  # identity (not just equal)
```

**What it protects**: Adding A_lr post-hoc would change the dynamics without changing
the labels (which are derived from A_sparse alone), creating a discrepancy between what
the system computes and what the labels describe.

**Checkable at**: construction-time

---

### INV-A5: A[k,k] = -1.5 for all k

**Statement**: The diagonal entries are all exactly -1.5.

```python
assert np.allclose(np.diag(A_sparse), -1.5, atol=1e-10)
```

**What it protects**: self-inhibition magnitude governs the stability margin and the
SNR calculation. If it differs, the SNR calculation documented in the parameter registry
is incorrect.

**Checkable at**: construction-time (CK-G2)

---

## Category B — State and Drive Invariants

### INV-B1: z enters the system only through B(z)

**Statement**: The function z → B(z) with B_h(z) = 3.0 × z for h ∈ SA and B_k(z) = 0
otherwise is the unique path by which z affects the system state. No other equation in
the integrator contains z.

```python
# Pseudocode structural check:
def integrator_step(x, z, A, B, D, dt):
    drift = A @ x + B(z)    # B is the ONLY place z appears
    noise = D_sqrt @ rng.normal(size=140) * np.sqrt(dt)
    return x + drift * dt + noise
# Any other occurrence of z in the integrator code is a violation
```

**What it protects**: If z enters through gain (A_eff = A × g(z)) or through D (D(z)),
the label derivation is wrong. Labels assume z acts only through additive H2 drive.

**Checkable at**: code review / unit test

---

### INV-B2: B(z) is linear in z

**Statement**: B_h(z) = γ_H2 × z with γ_H2 = 3.0 for all h ∈ SA. B is exactly linear
with no saturations, thresholds, or nonlinearities.

```python
# Test at construction time:
for z_test in [-5.0, -1.0, 0.0, 1.0, 5.0]:
    B_vec = compute_B(z_test)
    for h in SA:
        assert abs(B_vec[h] - 3.0 * z_test) < 1e-10, \
            f"B[{h}]({z_test}) = {B_vec[h]}, expected {3.0 * z_test}"
    for k in set(range(140)) - SA:
        assert B_vec[k] == 0.0, \
            f"B[{k}]({z_test}) = {B_vec[k]}, expected 0.0 (non-SA neuron)"
```

**What it protects**: a saturating B (e.g., tanh) would make the z→H2 relationship
nonlinear, creating a different state-dependence profile than assumed by the label
derivation.

**Checkable at**: unit test on B function

---

### INV-B3: Only H2 neurons receive z-drive

**Statement**: B_k(z) = 0 for all k ∉ SA. Observed neurons and H1 neurons receive no
direct z input.

```python
B_vec = compute_B(z=1.0)
for k in range(140):
    if k not in SA:
        assert B_vec[k] == 0.0, f"Non-SA neuron {k} has nonzero B: {B_vec[k]}"
```

**What it protects**: if observed neurons receive z-drive directly, the "C link" concept
changes — pairs could appear correlated simply because both receive direct z modulation,
without the H2 relay. This would inflate the C class in a way not captured by
SAREACHABLE.

**Checkable at**: unit test

---

### INV-B4: SA is fixed throughout simulation

**Statement**: The set SA = {132, ..., 139} (0-indexed) does not change during any
simulation run.

```python
SA_FIXED = frozenset(range(132, 140))  # immutable
# SA is never reassigned, never augmented, never filtered
```

**What it protects**: if SA changes (e.g., by accidentally adding an observed neuron),
the SAREACHABLE computation used for labels would not match the actual drive structure.

**Checkable at**: code review; SA defined as frozenset (immutable by construction)

---

## Category C — Diffusion Invariants

### INV-C1: D is state-independent

**Statement**: The diffusion matrix D passed to the integrator is constant — it has
the same value for every time step, regardless of z(t).

```python
# At integration time (pseudocode):
D_CONSTANT = build_D(d0=1.0, eps_lr=0.1, u=u_fixed)  # built once at construction
def integrator_step(x, z, t):
    ...
    noise = D_CONSTANT_SQRT @ rng.normal(...)  # D_CONSTANT_SQRT never changes
    ...
    # z does NOT appear in noise term
```

**What it protects**: state-dependent D would activate failure mode DF5 (D dominates ΔΩ).
The labels are derived assuming D is constant; state-dependent D would change Ω(z) via
the D channel, creating apparent C links in the framework output that are not labeled C.

**Checkable at**: code review + unit test (confirm same D at z=0 and z=5)

---

### INV-C2: D is positive definite

**Statement**: All eigenvalues of D are strictly positive.

```python
eigenvalues_D = np.linalg.eigvalsh(D)
assert np.min(eigenvalues_D) > 0.0, \
    f"D has non-positive eigenvalue: {np.min(eigenvalues_D)}"
```

**What it protects**: a non-positive-definite D would make the SDE ill-defined (negative
variance in some direction).

**Checkable at**: construction-time. D = d_0 × I + ε_lr × uuᵀ has eigenvalues d_0 and
d_0 + ε_lr, both positive. This is analytically guaranteed by construction but should
be verified numerically.

---

### INV-C3: D_lr has rank 1

**Statement**: D_lr = ε_lr × u × uᵀ is a rank-1 matrix with ε_lr = 0.1 and ||u|| = 1.

```python
rank_D_lr = np.linalg.matrix_rank(D_lr, tol=1e-8)
assert rank_D_lr == 1, f"D_lr has rank {rank_D_lr}, expected 1"
u_norm = np.linalg.norm(u)
assert abs(u_norm - 1.0) < 1e-10, f"||u|| = {u_norm}, expected 1.0"
```

**Checkable at**: construction-time

---

## Category L — Label Invariants

### INV-L1: Labels are generated before any trajectory

**Statement**: The label file `ground_truth/labels.json` and its hash must exist and
be verified (V1 checkpoint) before the first call to the integrator for any simulation run.

```python
# Enforced by requiring verify_label_hash() to return True before simulation loop begins
assert os.path.exists('ground_truth/labels.sha256'), \
    "Hash file missing — labels not committed before simulation"
verify_label_hash('ground_truth/labels.json', 'ground_truth/labels.sha256')
# If verify_label_hash raises, execution stops here
```

**What it protects**: generating labels after simulation could allow (intentional or
accidental) label generation that uses trajectory statistics.

**Checkable at**: runtime (V1 verification checkpoint)

---

### INV-L2: Labels depend only on A_sparse and SA

**Statement**: The label generation function `generate_labels(A_sparse, SA)` uses no
other inputs. It does not read from disk (other than receiving A_sparse as argument),
does not call any trajectory-generating function, and does not compute any statistical
quantity from data.

**Formal check** (static analysis):
```
Inspect generate_labels() source code for:
  - Any call to simulate(), integrate(), or any SDE function → VIOLATION
  - Any reference to x(t), y(t), z(t) as data arrays → VIOLATION
  - Any call to np.cov, np.corrcoef, scipy.stats, sklearn → VIOLATION
  - Any reference to Omega, precision, or any matrix inversion on data → VIOLATION
  - Any file I/O other than receiving A_sparse as argument → VIOLATION
```

**Checkable at**: code review / static analysis (grep for forbidden function calls)

---

### INV-L3: Labels are immutable after hash commit

**Statement**: After `labels.sha256` is written, `labels.json` is read-only. Any
process that modifies `labels.json` is a protocol violation.

```python
# Verified at V1 and V2 checkpoints by hash comparison
# File system enforcement: labels.json has mode 0444 after commit
import stat
mode = os.stat('ground_truth/labels.json').st_mode
assert not (mode & stat.S_IWUSR), \
    "labels.json is writable — hash commit did not set read-only"
```

**Checkable at**: runtime (V1, V2 checkpoints) + file permissions check

---

### INV-L4: Labels do not use Ω, Q, ΔΩ, ΔQ, or any matrix derived from data

**Statement**: The label values in the committed label file cannot be reproduced by any
procedure that uses precision matrices, probability currents, or covariance estimates
computed from simulated or real data. Labels are reproducible only from A_sparse and SA.

**Formal verification**: run `generate_labels(A_sparse, SA)` fresh and compare to
committed labels:

```python
fresh_labels = generate_labels(A_sparse, SA)
fresh_dict = build_label_dict(fresh_labels, A_sparse, SA)  # same structure as committed

# Compare every field
committed = json.load(open('ground_truth/labels.json'))
for committed_record, fresh_record in zip(
        sorted(committed['labels'], key=lambda r: (r['i'], r['j'])),
        sorted(fresh_dict['labels'],   key=lambda r: (r['i'], r['j']))):
    for field in ('i', 'j', 'direct', 'sareachable', 'label', 'witness_h2'):
        assert committed_record[field] == fresh_record[field], \
            f"Mismatch at ({committed_record['i']},{committed_record['j']}) field {field}"
```

**Checkable at**: construction-time and at any point during audit

---

## Category I — Information Barrier Invariants

### INV-I1: Framework receives no A_sparse information

**Statement**: The analysis pipeline does not receive A_sparse, any block of A_sparse,
or any information derived directly from A_sparse (connectivity graph, edge list, etc.)
as an input.

**What it protects**: if the framework receives A_sparse, it can trivially compute DIRECT
and SAREACHABLE and reproduce the ground truth labels without doing any current estimation.

**Checkable at**: code review of the data-passing interface between simulator and framework

---

### INV-I2: Framework receives no H2 topology information

**Statement**: The analysis pipeline does not receive: the SA set, the H2 target module
assignments, the H1 module assignments, or any labeling of neurons as observed vs. hidden.

**What it protects**: knowing which neurons are H2 and which modules they project to
would allow the framework to directly infer SAREACHABLE, making C detection trivial.

**Checkable at**: code review of the data-passing interface

---

### INV-I3: Labels are not revealed to the framework before all outputs are saved

**Statement**: The ground_truth directory (including labels.json) is not readable by the
framework process until after all classification output files for all conditions have been
saved with their final contents.

**Implementation**: run the framework as a separate process with no read access to the
`ground_truth/` directory. Grant access only to the audit process after all outputs
are finalized.

```bash
# During framework execution:
chmod 000 ground_truth/   # revoke all access to the framework process
# Run framework analysis
chmod 755 ground_truth/   # restore access for audit process
```

**Checkable at**: process isolation at runtime; verify no framework output file has a
modification timestamp after the `ground_truth/` directory was made readable.

---

### INV-I4: D is not provided to the framework

**Statement**: The analysis pipeline does not receive D (the diffusion matrix) as an input.

**What it protects**: D is needed to solve the Lyapunov equation and compute Ω analytically.
Providing D would give the framework oracle precision matrices, trivializing estimation.

**Checkable at**: code review of the data-passing interface

---

## Category S — Simulation Integrity Invariants

### INV-S1: Warm-up steps are discarded and never evaluated

**Statement**: The first T_warmup = 2,000 integration steps of each run are excluded
from the data arrays passed to the framework and from covariance estimation.

```python
assert y_provided.shape[1] == T_EFF == 48000, \
    f"y has {y_provided.shape[1]} columns; expected {T_EFF} (T - T_warmup)"
```

**Checkable at**: runtime check on array shapes

---

### INV-S2: Runs are independent

**Statement**: Each of the R=5 runs uses a different random seed for the Brownian
motion trajectories (sub-seeds 49, 50, 51, 52, 53 for z; sub-seeds 60, 61, 62, 63, 64
for x). They share the same A_sparse, D, and B(z) function.

```python
seeds_used = set()
for run_idx in range(5):
    z_seed = 49 + run_idx
    x_seed = 60 + run_idx
    assert z_seed not in seeds_used, f"Duplicate seed {z_seed}"
    seeds_used.add(z_seed)
    assert x_seed not in seeds_used, f"Duplicate seed {x_seed}"
    seeds_used.add(x_seed)
```

**Checkable at**: construction-time check on seed assignments

---

### INV-S3: The oracle z trajectory is the true z from the simulation

**Statement**: In the `oracle_z` condition, the z(t) array provided to the framework
must be the exact z trajectory generated by the SDE, not an approximation or re-drawn
sample.

```python
# Enforce by saving z alongside y in each simulation run:
np.save(f'run_{run_idx}_z.npy', z_trajectory[T_warmup:])
np.save(f'run_{run_idx}_y.npy', y_trajectory[T_warmup:])
# The oracle_z condition loads z from the same file
```

**Checkable at**: code review / file reference verification

---

## Invariant Summary Table

| ID | Category | Description | Checkable at |
|---|---|---|---|
| INV-A1 | Coupling | A fixed throughout simulation | Construction + code review |
| INV-A2 | Coupling | No gain modulation | Code review / static analysis |
| INV-A3 | Coupling | Spectral abscissa < -0.1 | Construction-time |
| INV-A4 | Coupling | A_lr = 0 | Construction-time |
| INV-A5 | Coupling | Diagonal = -1.5 | Construction-time |
| INV-B1 | State drive | z enters only through B(z) | Code review + unit test |
| INV-B2 | State drive | B(z) = 3.0z for H2, 0 elsewhere | Unit test |
| INV-B3 | State drive | Only H2 neurons receive z-drive | Unit test |
| INV-B4 | State drive | SA is fixed (frozenset) | Code review |
| INV-C1 | Diffusion | D is constant (not z-dependent) | Code review + unit test |
| INV-C2 | Diffusion | D is positive definite | Construction-time |
| INV-C3 | Diffusion | D_lr has rank 1 | Construction-time |
| INV-L1 | Labels | Labels generated before trajectories | Runtime V1 checkpoint |
| INV-L2 | Labels | Label function uses only A_sparse and SA | Code review |
| INV-L3 | Labels | Labels immutable after hash commit | Runtime V1/V2 + file perms |
| INV-L4 | Labels | Labels reproducible from construction only | Verification re-run |
| INV-I1 | Info barrier | Framework receives no A_sparse | Code review |
| INV-I2 | Info barrier | Framework receives no H2 topology | Code review |
| INV-I3 | Info barrier | Labels hidden from framework until after output | Process isolation |
| INV-I4 | Info barrier | Framework receives no D | Code review |
| INV-S1 | Simulation | Warm-up steps discarded | Runtime array shape check |
| INV-S2 | Simulation | Runs use independent seeds | Construction-time |
| INV-S3 | Simulation | Oracle z is true simulated z | Code review / file reference |
