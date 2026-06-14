# Phase 9A.2 — Ground-Truth Organization Design

## Purpose

Design the synthetic high-dimensional recurrent network whose planted organization the
framework must recover. Ground truth is defined at the organization level, not the pair level.

---

## Design Targets

```
N_obs         = 150 neurons (observed)
N_hidden      = 30 neurons (hidden)
N_total       = 180 neurons
States        = 2 (State A: high drive; State B: low drive)
Latent state  = 1-dimensional continuous z(t)
```

These numbers are in the 100–200 observed neuron range specified. The ratio N_hidden/N_total
= 30/180 ≈ 17%, consistent with realistic partial observation.

---

## Network Architecture

### Module Structure

Four modules of observed neurons:

```
M1: 40 neurons  (sensory analog — primary drive entry)
M2: 40 neurons  (integration analog)
M3: 35 neurons  (motor-output analog)
M4: 35 neurons  (modulatory analog)
```

Total observed: 150 neurons.

Hidden neurons: 30, distributed as:
```
H_local : 20 neurons  (local hidden interneurons, 5 per module)
H_global: 10 neurons  (global hidden modulators — key for planted organization)
```

### Sparse Anatomical Coupling

The coupling matrix A is fixed throughout all states. No edge turns on or off.

Construction:

```
Within-module coupling:   connection probability p_within = 0.12
Between-module coupling:  connection probability p_between = 0.02
H_local → observed:       connection probability p_local = 0.15 (within module only)
H_global → observed:      connection probability p_global = 0.10 (across all modules)
```

Edge weights are drawn from a truncated normal distribution with mean 0 and std 0.3,
constrained so that A has all eigenvalues in (-1, 0) to ensure stability.

**The coupling matrix A is never revealed to the framework. Only observed activity is
provided. A is ground truth for structural classification only.**

---

## Latent State Variable

A single latent process z(t) represents neuromodulatory drive:

```
dz = -θ_z z dt + σ_z dW_z
```

Two states are defined by z's long-term mean regime:

```
State A (high drive):  z_mean = z_high   (parameterized to create visible reorganization)
State B (low drive):   z_mean = 0        (baseline, near-equilibrium regime)
```

In the benchmark, State A and State B are defined as long trajectory segments at fixed z_mean,
computed separately for the Lyapunov analysis. The exact values of z_high and θ_z are
committed before any simulation (no tuning after observing framework performance).

**z(t) is never provided to the framework.** The framework receives only the observed
neural activity x(t). State labels (A vs. B) are provided at the segment level, exactly
as in the worm analysis (roaming/dwelling epoch labels were provided; z was not).

---

## Planted Organization

This is the core of the ground-truth design. The planted organization is the analog of
the PDF-receptor circuit in the worm and the non-adjacent ganglion pairs in the leech.

### Planted Modulatory Circuit (PMC)

A set of 20 observed neurons designated as the PMC, spanning modules:

```
PMC sources:  8 neurons drawn from M1 (the "sensory/drive" module)
PMC targets: 12 neurons drawn from M3 and M4 (the "output/modulatory" modules)
```

**Construction rule (critical — specifies organization without specifying pair labels):**

1. PMC sources have elevated connectivity to H_global neurons:
   each PMC source neuron projects to at least 3 of the 10 H_global neurons
   (vs. background rate of ~1).

2. PMC targets have elevated H_global input:
   each PMC target neuron receives projections from at least 4 of the 10 H_global neurons
   (vs. background rate of ~1).

3. No direct structural edges between PMC sources and PMC targets:
   ```
   A[i,j] = 0   for all i ∈ PMC_sources, j ∈ PMC_targets
   ```
   This is enforced by construction. PMC source-target pairs are off-connectome.

4. H_global neurons have their drive modulated by z:
   ```
   effective gain of H_global neurons = g_base + g_mod × z(t)
   ```
   where g_mod > 0, so H_global neurons transmit more strongly in State A.

**Result:** In State A, H_global neurons transmit strong coordinated fluctuations from PMC
sources to PMC targets. The PMC source-target pairs acquire large ΔΩ entries. In State B,
H_global gain is near zero; PMC source-target coordination disappears.

This mirrors the OU cascade (source node drive α amplifies long-range current-supported
links) and the leech (coupling gain switches on specific non-adjacent ganglion pairs)
and the worm (neuromodulatory state creates PDF-receptor circuit coordination).

### PMC Pair Count

Off-connectome PMC pairs: 8 × 12 = 96 pairs (undirected: 96 ordered source-target pairs).
These 96 pairs are the ground-truth planted organization.

Total off-connectome observed pairs: approximately
```
C(150,2) - structural_edges ≈ 11,175 - 180 ≈ 10,995 off-connectome pairs
```

PMC pairs constitute approximately 0.87% of all off-connectome pairs — a density
comparable to the PDF-annotated fraction (4.6% of Class 4 pairs in the worm, here
somewhat sparser to make recovery harder).

---

## State A Organization

In State A (high z):

- H_global neurons are strongly activated, transmitting correlated fluctuations
- PMC sources co-vary with PMC targets through H_global relay paths
- ΔΩ_true[i,j] for (i,j) ∈ PMC pairs is large and positive (dwelling-like state in the
  worm, high-α state in OU cascade)
- ΔΩ_true[i,j] for non-PMC off-connectome pairs is near zero (random noise level)

The planted organization is captured by:

```
ΔΩ_true = Ω_A − Ω_B
         = D_A Q_A − D_B Q_B
```

computed analytically from the Lyapunov equation at each state. This is the true ranking
the framework should recover.

**Dominant modules in State A:**
- PMC sources form a functional cluster (they co-organize through shared H_global input)
- PMC targets form a functional cluster (they co-organize through shared H_global output)
- PMC source cluster and PMC target cluster are cross-module connected in ΔΩ

**Dominant off-connectome organization:**
- Top 96 off-connectome ΔΩ entries are predominantly PMC pairs
- Background off-connectome pairs have |ΔΩ_true| near zero
- The planted signal is strong enough for top-k overlap evaluation at k = 20, 50

---

## State B Organization

In State B (z = 0, baseline):

- H_global neurons are at baseline, transmitting only background noise
- PMC source-target coordination is absent
- ΔΩ[i,j] ≈ 0 for PMC pairs
- Ω_B is determined primarily by the structural coupling A and the baseline diffusion D_B

The State B precision graph reflects network structure without the modulatory drive.

---

## Dominance Requirement (Pre-Registration)

Before any simulation, the following dominance condition is verified analytically:

```
Condition D1: Median |ΔΩ_true| for PMC pairs > 2 × 90th percentile |ΔΩ_true|
              for non-PMC off-connectome pairs
```

If D1 is not satisfied at the chosen parameters, z_high is increased until it is. The
value at which D1 is first satisfied defines the operating point. This prevents post-hoc
tuning; the dominance condition is a go/no-go criterion for the parameter choice.

---

## Diffusion Matrix Design

The diffusion matrix D captures where new fluctuations enter the circuit.

```
D_base: diagonal, neuron-specific amplitude drawn from log-normal distribution
D_A = D_base + g_D × z_high × D_PMC_sources   (State A: elevated variance at PMC sources)
D_B = D_base                                   (State B: baseline)
```

where D_PMC_sources is a diagonal matrix that elevates variance at the PMC source neurons
in State A, mimicking the increased variability at URXL and URYVL during roaming in the
worm.

This models the paper's key finding: "diffusion and precision change along different axes."
In the benchmark, the PMC sources have increased innovation amplitude in State A AND form
current-supported organization in ΔΩ. The non-PMC neurons have stable diffusion across
states.

---

## What Constitutes Ground Truth (Organization Level)

The following objects are known exactly by construction:

### G1. PMC Membership
The 20 PMC neurons (8 sources, 12 targets) and their module assignments.
These are the "planted circuit" — the analog of ADEL/RMEL/RMER/RID → URYVR/URYDL/URXL.

### G2. PMC Pair Set
The 96 directed PMC source-target pairs. These are off-connectome by construction (A[i,j]=0).
This is the "ground-truth annotation" — the analog of the PDF-receptor annotation in the worm.

### G3. ΔΩ_true Ranking
The true ranking of all off-connectome pairs by |ΔΩ_true|, computed analytically from
the Lyapunov solutions at State A and State B. This is the oracle ranking the framework
should approximate.

### G4. Module-Level Organization
The community structure of ΔΩ_true restricted to off-connectome pairs. PMC sources form
community C_src; PMC targets form community C_tgt. The dominant cross-module organization
in ΔΩ_true is the C_src ↔ C_tgt coupling.

### G5. Intervention Outcomes
Which pairs dissolve under state intervention and which survive under structural
intervention (specified in p3_intervention_logic.md).

---

## What is NOT Ground Truth

The following are NOT computed or exposed as ground truth:

```
Q_A, Q_B                    (estimated by framework)
Ω_A, Ω_B                    (estimated by framework)
ΔΩ_estimated                (estimated by framework)
Per-pair labels (S/C/M/N)   (NOT the primary benchmark target)
```

Per-pair labels are not pre-registered as the evaluation target. The evaluation target
is recovery of the organization described in G1–G5.

---

## Design Rationale: Why This Mirrors the Paper

The OU cascade: α drives off-local current-supported organization.
→ z drives PMC source-target organization through H_global relay.

The leech: coupling gain creates a specific set of non-adjacent ganglion pairs as the
current-supported "wave connectivity."
→ z_high creates a specific set of off-connectome pairs (PMC) as the state-dependent
functional connectivity.

The worm: neuromodulatory dwelling state creates PDF-receptor circuit enrichment among
Class 4 ΔΩ entries.
→ z_high creates PMC circuit enrichment among off-connectome ΔΩ entries.

In all three cases: the planted organization has a clear subnetwork structure (not random),
requires a state regime (not structural wiring) to exist, and is testable via enrichment
(not pair-level classification).
