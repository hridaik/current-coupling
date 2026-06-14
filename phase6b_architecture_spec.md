# Phase 6B — Simulator Architecture Specification

## Status

This document is a complete, frozen specification. An independent implementer must be
able to build the simulator solely from this document and `phase6b_parameter_registry.md`
without making any scientific decision.

Every quantity is exact. No ranges. No "approximately." No "for example."

---

## 1. Network Composition

### 1.1 Total neuron counts

| Population | Count | Index range |
|---|---|---|
| Observed (O) | 100 | 1 – 100 |
| Hidden H1 (local interneuron) | 32 | 101 – 132 |
| Hidden H2 (global modulator) | 8 | 133 – 140 |
| **Total** | **140** | 1 – 140 |

### 1.2 Module assignments — observed neurons

| Module | Neurons | Observed indices |
|---|---|---|
| M1 | 25 | 1 – 25 |
| M2 | 25 | 26 – 50 |
| M3 | 25 | 51 – 75 |
| M4 | 25 | 76 – 100 |

### 1.3 Module assignments — H1 neurons

Each module contains exactly 8 H1 interneurons.

| Module | H1 indices |
|---|---|
| M1 | 101 – 108 |
| M2 | 109 – 116 |
| M3 | 117 – 124 |
| M4 | 125 – 132 |

An H1 neuron assigned to module Mx only connects to observed neurons in Mx.

### 1.4 H2 neuron assignment — target modules

Each H2 neuron is assigned exactly two target modules. Connectivity is drawn only between
the H2 neuron and observed neurons in its target modules.

| H2 index | Target modules | Module index set |
|---|---|---|
| 133 | M1, M2 | {1–25} ∪ {26–50} |
| 134 | M1, M2 | {1–25} ∪ {26–50} |
| 135 | M3, M4 | {51–75} ∪ {76–100} |
| 136 | M3, M4 | {51–75} ∪ {76–100} |
| 137 | M1, M3 | {1–25} ∪ {51–75} |
| 138 | M2, M4 | {26–50} ∪ {76–100} |
| 139 | M1, M4 | {1–25} ∪ {76–100} |
| 140 | M2, M3 | {26–50} ∪ {51–75} |

**Coverage check**: every module pair (6 possible pairs among 4 modules) has at least
one H2 neuron. Module pairs {M1,M2} and {M3,M4} each have two H2 neurons; all other
pairs have exactly one.

**Coverage per module**: each module is a target of exactly 4 H2 neurons.
- M1: H2 indices 133, 134, 137, 139
- M2: H2 indices 133, 134, 138, 140
- M3: H2 indices 135, 136, 137, 140
- M4: H2 indices 135, 136, 138, 139

---

## 2. Graph Generation

### 2.1 Coupling matrix convention

The 140×140 coupling matrix A is defined by the convention:

```
dx_k = sum_j A[k,j] * x_j  dt  +  noise
```

So A[k,j] ≠ 0 means neuron j has a directed influence on neuron k (j → k).

### 2.2 Low-rank component

**Decision**: the low-rank global component A_lr is **not included** in the primary
Phase 6A benchmark. A = A_sparse only.

**Rationale**: the Phase 6A leakage audit identified that a low-rank component creates
ambiguity about what counts as "structural" (vulnerability L3), generates a fifth label
category (LR) that complicates the primary four-way evaluation, and confounds D and A
separation. Omitting A_lr eliminates L3 and IF2 from the failure mode registry with no
loss of scientific validity for the S/C/M/N distinction test.

A_lr can be re-introduced in Phase 6B extension studies once the primary benchmark
is validated.

### 2.3 Sparsity pattern — observed-to-observed block

For each directed pair (j, k) with j ≠ k, both j and k observed:

```
A[k,j] is nonzero with probability:
    p_within = 0.15   if module(k) = module(j)
    p_between = 0.03   if module(k) ≠ module(j)
```

Nonzero entries are drawn independently at construction time using a fixed random seed.

### 2.4 Sparsity pattern — H1 neuron connections

For each H1 neuron h assigned to module Mx:

```
A[h,j] is nonzero with probability p_H1_in = 0.30  for each observed j in Mx
A[k,h] is nonzero with probability p_H1_out = 0.25  for each observed k in Mx
```

H1 neurons have no connections to neurons outside their assigned module.
H1 neurons have no connections to other H1 or H2 neurons.
H1 neurons have no self-connections.

### 2.5 Sparsity pattern — H2 neuron connections

For each H2 neuron h with target module set T(h):

```
A[h,j] is nonzero with probability p_H2_in = 0.20  for each observed j in ∪T(h)
A[k,h] is nonzero with probability p_H2_out = 0.20  for each observed k in ∪T(h)
```

H2 neurons have no connections outside their target modules.
H2 neurons have no connections to H1 or other H2 neurons.
H2 neurons have no self-connections.

**H2 is a relay, not a hub**: H2 neurons can receive inputs from observed neurons in
their target modules (enabling directed paths obs→H2→obs) and project back (enabling
state-dependent flow propagation).

### 2.6 Self-connections (diagonal of A)

All neurons receive a fixed self-inhibition:

```
A[k,k] = -1.5  for all k in {1, ..., 140}
```

This term appears on the diagonal of A and ensures baseline stability. It is part of
A_sparse. It is not random.

### 2.7 Weight distribution — nonzero off-diagonal entries

For each nonzero off-diagonal entry A[k,j] determined in Sections 2.3–2.5, the weight
is drawn from:

```
A[k,j] ~ Normal(0, σ_kj²)
```

where σ_kj depends on the connection type:

| Connection type | σ_kj |
|---|---|
| Observed → observed (within module) | 0.30 |
| Observed → observed (between module) | 0.30 |
| Observed → H1 (in-connection to H1) | 0.25 |
| H1 → observed (out-connection from H1) | 0.25 |
| Observed → H2 (in-connection to H2) | 0.25 |
| H2 → observed (out-connection from H2) | 0.35 |

Justification for uniform σ=0.30 for observed-observed: this gives expected spectral
contribution ~σ√n_in where n_in ~ 9 for typical observed neurons, so ~0.30×3 = 0.9,
well below the self-inhibition magnitude of 1.5. The spectral abscissa is expected to
be negative by a margin of approximately -0.5.

H2→observed weight is 0.35 (larger than average) because H2 is the primary source of
C-link signal and must produce detectable state-dependent correlations.

### 2.8 Post-generation stability check

After constructing A, compute its spectral abscissa:

```
ρ_A = max{ Re(λ) : λ is eigenvalue of A }
```

**Required**: ρ_A < -0.1

If ρ_A ≥ -0.1, resample all nonzero off-diagonal weights (preserving the sparsity
pattern) with the same random seed + 1 until ρ_A < -0.1. Record the number of resamples
required.

**Maximum attempts**: 10. If stability is not achieved in 10 resamples, reduce all σ
values by 10% uniformly and repeat.

### 2.9 Random seed protocol

All random sampling uses a seeded pseudorandom number generator (NumPy default_rng or
equivalent). The master seed is **42**. Sub-seeds for each component are derived as:

| Component | Sub-seed |
|---|---|
| Observed-observed sparsity pattern | 42 |
| H1 sparsity pattern | 43 |
| H2 sparsity pattern | 44 |
| Observed-observed weights | 45 |
| H1 weights | 46 |
| H2 weights | 47 |
| D_lr noise direction u | 48 |
| z(t) process | 49 + run_index (for runs 0–4) |
| State x(0) initialization | 60 + run_index |

---

## 3. State Architecture

### 3.1 Latent state dimensionality

The latent state z(t) is **scalar** (1-dimensional).

Justification: scalar z is the simplest design that creates interpretable state
dependence. Multi-dimensional z creates interaction effects between z components (failure
mode W12 in Phase 6A review) that complicate both label computation and result
interpretation. Phase 6B extensions may add a second z dimension.

### 3.2 Latent state dynamics

z(t) follows a scalar Ornstein-Uhlenbeck (OU) process:

```
dz = -θ_z * z dt + σ_z * dW_z
```

Parameters:
- θ_z = 0.10  (mean-reversion rate; gives correlation time τ_z = 1/θ_z = 10 time units)
- σ_z = 1.00  (noise amplitude)
- Stationary distribution: z ~ N(0, σ_z²/(2θ_z)) = N(0, 5.0)
- Stationary standard deviation: sqrt(5) ≈ 2.236

The z process has mean zero and is symmetric. "High-z" states (z >> 0) and "low-z"
states (z << 0) have equal prior probability.

### 3.3 Effect of z on the network

z enters the network exclusively through additive external drive to H2 neurons.
It does not modify A. A is fixed.

For each H2 neuron h ∈ {133, ..., 140}:

```
B_h(z) = γ_H2 * z    where γ_H2 = 3.0
```

This external drive term adds to the drift of H2 neurons:

```
dx_h = (sum_j A[h,j] * x_j  +  γ_H2 * z) dt  +  D_h^{1/2} dW_h
```

For all other neurons k (observed or H1), B_k(z) = 0. They receive no direct z input.

**Why γ_H2 = 3.0**: with self-inhibition A[h,h] = -1.5, the steady-state H2 response
to constant z is approximately z/1.5 = 2z/3. With z having SD ≈ 2.24, the H2
activity fluctuation is approximately (3.0/1.5) × 2.24 ≈ 4.5 in units of the neural
state. Downstream observed neurons receive H2 drive scaled by A[k,h] (SD ≈ 0.35), so
the expected H2-driven fluctuation in observed neurons ≈ 0.35 × 4.5 / 1.5 ≈ 1.05. The
noise-driven fluctuation in an observed neuron has SD ≈ sqrt(D_k / (2×1.5)) = sqrt(1/3)
≈ 0.577. The H2 signal-to-noise ratio is ≈ 1.05/0.577 ≈ 1.8, which ensures C links
are detectable while remaining a genuine challenge (not trivially large).

### 3.4 State-active neuron set

```
SA = {133, 134, 135, 136, 137, 138, 139, 140}  (all 8 H2 neurons)
```

No observed neuron and no H1 neuron is in SA.
SA is determined entirely by construction and does not change during simulation.

### 3.5 Gain modulation

There is no gain modulation in this design. A is fixed.
gmod(k) = 0 for all neurons k.
All state dependence enters through B_h(z) for h ∈ SA only.

**Why no gain modulation**: gain modulation (multiplicative, A_eff[k,j](z) = g_k(z) ×
A[k,j]) changes the effective coupling matrix with z, which creates a confound between
structural and state-dependent links (vulnerability W13 in Phase 6A review). Pure additive
drive is mechanistically cleaner, enables exact label computation without dynamic
simulation, and avoids the gain-vs-coupling attribution problem.

---

## 4. Diffusion Model

### 4.1 Full diffusion matrix

```
D = D_diag + D_lr
```

where:
- D_diag = d_0 × I_{140}   with d_0 = 1.0
- D_lr = ε_lr × u × uᵀ    with ε_lr = 0.1 and ||u||₂ = 1

### 4.2 Low-rank noise component

u is a 140-dimensional unit vector drawn once at construction time using sub-seed 48.
D_lr = 0.1 × u × uᵀ.

Frobenius norm ratio: ||D_lr||_F / ||D_diag||_F = 0.1 / sqrt(140) ≈ 0.0085.
This is well below the 5% threshold identified in the Phase 6A review (vulnerability W14).

### 4.3 State independence of D

D does **not** depend on z. The diffusion matrix is constant throughout the simulation.

**Rationale**: including D(z) variation introduces failure mode DF5 (D dominates ΔΩ).
As documented in the Phase 6A failure mode registry, ||ΔD(z)||_F / ||D_baseline||_F must
remain below 0.20. Setting D constant eliminates this failure mode entirely.

The state-dependent noise injection described in the Phase 6A protocol is **deferred to
Phase 6B extensions**, where it can be introduced in a controlled sensitivity study
with explicit SNR monitoring.

### 4.4 D construction verification

After constructing D, verify:
1. D is positive definite (all eigenvalues > 0). Since D = d_0 I + ε_lr u uᵀ, the
   eigenvalues are d_0 and d_0 + ε_lr ||u||² = 1.0 + 0.1 = 1.1 (for the u direction).
   Both are positive. D is always positive definite by construction.
2. Record the eigenvalue ratio: λ_max(D) / λ_min(D) = 1.1 / 1.0 = 1.1.

---

## 5. Full System Dynamics

The complete simulator dynamics are:

```
dx(t) = (A x(t) + B(z(t))) dt + D^{1/2} dW(t)
dz(t) = -θ_z z(t) dt + σ_z dW_z(t)
```

where:
- x ∈ ℝ^{140} is the full neural state vector
- A ∈ ℝ^{140×140} is the fixed coupling matrix (A_sparse, no A_lr)
- B(z) ∈ ℝ^{140}: B_k(z) = γ_H2 × z for k ∈ {133,...,140}; B_k(z) = 0 otherwise
- D = D_diag + D_lr ∈ ℝ^{140×140} (positive definite, constant)
- W(t) ∈ ℝ^{140}: standard Brownian motion, independent of W_z
- W_z(t): scalar standard Brownian motion, independent of W(t)
- z ∈ ℝ: scalar latent state

### 5.1 Numerical integration

Method: Euler-Maruyama

```
x(t + dt) = x(t) + A x(t) dt + B(z(t)) dt + D^{1/2} ε_x sqrt(dt)
z(t + dt) = z(t) - θ_z z(t) dt + σ_z ε_z sqrt(dt)
```

where ε_x ~ N(0, I_{140}) and ε_z ~ N(0,1) are drawn fresh at each step.

- Integration step: dt = 0.1 time units
- Total time steps per run: T = 50,000 (5,000 time units per run)
- Number of independent runs: R = 5
- Initialization: x(0) drawn from N(0, Σ_0) where Σ_0 is the stationary covariance
  of the system (computed analytically from the Lyapunov equation before simulation).
  z(0) drawn from N(0, σ_z²/(2θ_z)) = N(0, 5).

### 5.2 Stationarity warm-up

Discard the first 2,000 time steps of each run (200 time units; ~20 correlation times of z).
Analysis uses only time steps 2,001–50,000 (T_eff = 48,000 steps, 4,800 time units).

---

## 6. Observation Architecture

### 6.1 Observed fraction

All 100 observed neurons (indices 1–100) are calcium-imaged.
All 40 hidden neurons (indices 101–140) are completely unobserved throughout the simulation
and evaluation. Their state vectors are generated but never revealed to the analysis pipeline.

Observed fraction: 100/140 = 71.4%, within the 70–80% target range.

### 6.2 Observation pipeline

The observed calcium signal y_k(t) for observed neuron k is generated in four stages:

**Stage 1 — Firing rate transformation**

```
r_k(t) = softplus(x_k(t)) = log(1 + exp(x_k(t)))
```

Softplus is used rather than ReLU (differentiable everywhere) or sigmoid (bounded above).
It approximates a linear relationship for large positive x and saturates to zero for
large negative x.

**Stage 2 — Calcium dynamics (discrete-time filter)**

```
c_k(t + dt) = (1 - κ_ca × dt) × c_k(t) + r_k(t) × dt
```

with κ_ca = 0.5 (calcium decay rate constant; calcium decay time = 1/κ_ca = 2 time units).

At dt = 0.1: c_k(t+1) = 0.95 × c_k(t) + 0.1 × r_k(t)

Initial condition: c_k(0) = r_k(0) / κ_ca (steady-state for the initial neural state).

**Stage 3 — Measurement noise**

```
y_k(t) = c_k(t) + ε_k(t),   ε_k(t) ~ i.i.d. N(0, σ_obs²)
```

with σ_obs = 0.10.

**Stage 4 — No subsampling of observed neurons**

All 100 observed neurons are calcium-imaged. The 40 hidden neurons are absent from y(t)
by design; this is the "subsampling" (from the perspective of the full system).

### 6.3 What the analysis pipeline receives

Per run r ∈ {0,1,2,3,4}:
- y^(r) ∈ ℝ^{100 × T_eff}: calcium traces for 100 observed neurons, T_eff = 48,000 steps
- z^(r) ∈ ℝ^{T_eff}: true latent state trajectory (oracle-z condition only)

The analysis pipeline is **not given**:
- A or any block of A
- D or any component of D
- The indices of H1 or H2 neurons
- The module assignments
- The identity of which neurons are hidden

### 6.4 Evaluation conditions

| Condition label | What the framework receives | Purpose |
|---|---|---|
| `oracle_z` | y(t), z(t) | Primary benchmark |
| `blind_z` | y(t) only | Tests z-inference contribution |
| `neural_state` | x_obs(t) directly, z(t) | Removes observation model confound |
| `weak_z` | y(t), z(t); but z amplitude halved | Near-null H0 sensitivity test |
| `strong_z` | y(t), z(t); z amplitude doubled | High-SNR upper bound |

All five conditions are run. The `oracle_z` condition is the primary result.
Other conditions are diagnostic.

---

## 7. Architectural Decisions Summary

The following deviations from the Phase 6A protocol are made in Phase 6B and must be
explicitly documented:

| Protocol element | Phase 6A recommendation | Phase 6B decision | Reason |
|---|---|---|---|
| Low-rank A component | Include 2–3 rank modes | Omitted (A = A_sparse) | Eliminates L3, IF2 |
| Noise model | State-dependent D(z) | D constant | Eliminates DF5 |
| Gain modulation | Selected subnetworks | No gain modulation; z enters only as B(z) | Eliminates W13 |
| H2 topology | Underspecified | Fully specified (8 H2, fixed target modules) | Resolves L4 |
| z dimensionality | Unspecified | Scalar (1D) | Eliminates W12 |
| H2–H2 connectivity | Unspecified | Forbidden | Simplifies path analysis |
| H1–H2 connectivity | Unspecified | Forbidden | Simplifies path analysis |
