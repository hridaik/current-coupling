# Phase 6A — Ground-Truth Recurrent Network Design

## Objective

Construct a realistic recurrent neural-network validation benchmark that tests whether the current-velocity framework correctly distinguishes:

1. Structural links
2. State-dependent links
3. Mixed links (structural + state-dependent)
4. Null links

while maintaining exact ground truth.

The benchmark must be substantially more realistic than:

* OU cascade
* Leech phase model

but remain interpretable.

No implementation, simulation, estimation, or analysis is performed in this phase.

---

# Design Principles

The benchmark should satisfy five constraints:

### P1. Realistic network structure

Network topology should resemble biological circuits rather than random OU chains.

### P2. Genuine state dependence

State transitions must arise from latent circuit modulation rather than explicit edge toggling.

### P3. Emergent current-supported links

Current-supported links must emerge through network dynamics and state-dependent flow.

They must not be directly specified.

### P4. Hidden-variable challenge

Observed neurons should not comprise the entire dynamical system.

### P5. No answer leakage

The simulator must never generate:

* Q
* Ω
* current labels
* framework classifications

Only dynamics are generated.

All classifications are recovered post hoc.

---

# Recommended Protocol

## Network Scale

### Observed neurons

100 neurons

### Hidden neurons

40 neurons

### Total dynamical system

140 neurons

Rationale:

* large enough for realistic graph structure
* small enough for exact ground truth bookkeeping
* permits hidden-variable effects

---

# Ground-Truth Coupling Matrix

## Recommendation

Modular sparse low-rank hybrid

Avoid purely random connectivity.

---

## Construction

Four modules:

M1–M4

Each module:

25 observed neurons

plus hidden neurons distributed across modules.

---

### Local connectivity

Within-module:

* sparse directed recurrent graph
* connection probability ≈ 0.15

---

### Long-range connectivity

Between modules:

* sparse directed projections
* probability ≈ 0.03

---

### Global low-rank component

Add 2–3 latent population modes.

Interpretation:

* neuromodulatory pathways
* global attractor structure
* shared recurrent motifs

These modes generate realistic long-range covariance without creating explicit pairwise links.

---

## Why not alternatives?

### Pure sparse random

Rejected.

Produces unrealistic graph statistics and weak mesoscopic organization.

### Pure modular

Rejected.

Too easy for graphical methods.

### Connectome-inspired

Rejected for Phase 6A.

Requires arbitrary biological assumptions and complicates interpretation.

Can be reserved for Phase 6B.

---

# State Mechanism

## Recommendation

Continuous latent neuromodulatory variable

Not discrete switching.

---

## Latent state

Introduce a low-dimensional hidden process:

z(t)

representing:

* arousal
* neuromodulatory tone
* behavioral context

---

## Action of z

z modulates:

### Recurrent gain

Selected subnetworks receive gain modulation.

### Input routing

Certain modules become more excitable.

### Noise injection

Innovation structure changes with state.

---

## Important restriction

A remains fixed.

No edge is turned on or off.

Structural connectivity never changes.

Only dynamical regime changes.

---

# Ground-Truth Current-Supported Links

## Recommendation

Generate indirectly.

Never specify them.

---

## Mechanism

Current-supported links arise through:

### 1. State-dependent gain

Changes effective propagation lengths.

### 2. Low-rank latent modes

Create coordinated activity among distant neurons.

### 3. Hidden neurons

Transmit state information through unobserved pathways.

### 4. Directed recurrent loops

Generate nonequilibrium circulation.

---

## Ground-truth definition

A pair is current-supported if:

* no direct structural edge exists
* state manipulation induces reproducible conditional dependence
* dependence disappears when state drive is removed
* effect is mediated by recurrent flow

The simulator does not label such pairs.

Labels are derived only from known construction rules after simulation design is complete.

---

# Observation Model

## Recommendation

Partial calcium observation

Not full-state observation.

---

## Hidden observation pipeline

Neural state

→ firing-rate nonlinearity

→ calcium dynamics

→ measurement noise

→ subsampling

---

## Observed fraction

Observe:

70–80%

of neurons.

Unobserved neurons remain latent.

---

## Why?

Real experiments rarely observe:

* full state
* true membrane potential
* all neurons

This creates a realistic inference challenge.

---

# Hidden Variable Structure

## Recommendation

Yes.

Hidden neurons are required.

---

## Hidden populations

Two classes.

### Class H1

Local hidden interneurons

Inside modules.

---

### Class H2

Global hidden modulators

Drive multiple modules simultaneously.

---

## Purpose

Creates:

* indirect dependencies
* latent confounding
* realistic state organization

without explicitly creating current-supported labels.

---

# Noise Model

## Recommendation

State-dependent diagonal plus low-rank component

---

## Base diffusion

Diagonal innovation noise.

Neuron-specific amplitudes.

---

## State dependence

Latent variable z modifies:

* variance scale
* module-specific innovation rates

---

## Shared component

Add weak low-rank correlated innovations.

Interpretation:

* common drive
* neuromodulation
* physiological fluctuations

---

## Why not alternatives?

### Identity D

Rejected.

Too idealized.

### Dense arbitrary D

Rejected.

Difficult to interpret.

### Fully state-dependent dense D

Rejected.

May blur attribution between current and coupling.

---

# Structural Perturbation Ground Truth

The protocol should include virtual lesion definitions.

No implementation is performed.

---

## Lesion classes

### Structural lesion

Remove selected anatomical projections.

Expected effect:

structural links disappear.

---

### State lesion

Suppress latent modulation z.

Expected effect:

current-supported links disappear.

---

### Combined lesion

Both manipulations.

Used to identify mixed links.

---

# Ground-Truth Link Categories

Ground truth is defined exclusively from simulator construction.

Not from estimated quantities.

---

## Class S

Structural only

Conditions:

* direct coupling exists
* state manipulation has negligible effect

---

## Class C

Current-supported only

Conditions:

* no direct coupling
* state modulation required

---

## Class M

Mixed

Conditions:

* direct coupling exists
* state modulation alters magnitude

---

## Class N

Neither

Conditions:

* no coupling
* no state dependence

---

# Validation Metrics

The framework must recover classes at the edge level.

---

## Primary metric

Four-way edge classification accuracy.

Classes:

S
C
M
N

---

## Secondary metrics

### Precision

Per class.

---

### Recall

Per class.

---

### AUROC

One-vs-rest.

---

### Confusion matrix

Particularly:

Structural ↔ Current confusion.

---

### Calibration

Probability of class assignment versus true frequency.

---

# Mechanistic Validation Metrics

Evaluate whether recovered current-supported links satisfy:

### Off-structure enrichment

Fraction of detected current-supported links lacking direct coupling.

---

### State sensitivity

Change under state lesion.

---

### Structural sensitivity

Change under structural lesion.

---

### Mixed-link identification

Ability to separate:

* state contribution
* structural contribution

for the same edge.

---

# Expected Failure Modes

## F1

Hidden-neuron confounding

Current-supported links misclassified as structural.

---

## F2

Low-rank mode inflation

Large-scale modes create dense apparent connectivity.

---

## F3

Weak state separation

Current-supported links become undetectable.

---

## F4

Strong diffusion heterogeneity

D dominates Ω reconstruction.

---

## F5

Partial observation bias

Observed network differs substantially from full network.

---

## F6

Module imbalance

One module dominates network statistics.

---

# Quantities Constituting Ground Truth

The following are known exactly by construction.

---

## Structural Ground Truth

Fixed coupling matrix:

A

Observed-observed block

Observed-hidden block

Hidden-hidden block

---

## State Ground Truth

Latent state trajectory definition:

z

State modulation operators

Gain-modulation maps

Noise-modulation maps

---

## Lesion Ground Truth

Structural lesion set

State lesion set

Combined lesion set

---

## Edge Ground Truth

For every observed pair:

Structural category:

* S
* C
* M
* N

derived from simulator construction rules.

---

# Explicit Non-Ground-Truth Quantities

The simulator must never generate or expose:

* Q
* Ω
* ΔQ
* ΔΩ
* precision graphs
* current graphs
* framework classifications

These quantities must emerge only from analysis.

This prevents answer leakage.

---

# Final Recommendation

Use a 140-neuron recurrent system composed of:

* modular sparse anatomy
* low-rank global structure
* hidden neurons
* latent neuromodulatory state
* state-dependent diffusion
* partial calcium observation

with fixed structural connectivity and state-dependent dynamics.

This configuration is sufficiently realistic to stress-test the current-velocity framework while preserving exact, non-leaking ground truth and maintaining interpretability of all validation outcomes.
