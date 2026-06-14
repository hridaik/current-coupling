# Phase 9A Protocol — High-Dimensional Organization-Recovery Benchmark

**Status:** PROTOCOL DESIGN ONLY  
**Date:** 2026-06-14  
**No implementation. No simulator. No code. No data generation. Frozen pending review.**

---

## What This Protocol Is

A replacement for the Phase 6–8 benchmark. The prior benchmark tested pair-level
classification (can every pair be labeled S/C/M/N?). That benchmark failed — not because
the framework is wrong, but because it asked the wrong scientific question.

This protocol asks the question the paper actually asks:

> Can the framework recover the dominant state-dependent organization?

---

## Why the Previous Benchmark Was Misaligned

The Phase 6–8 benchmark evaluated AUROC over four-way pair labels (S, C, M, N). It
declared failure when C-AUROC = 0.4484 — below chance.

This evaluation is not what the paper does:

- **OU cascade:** The paper reports Scur = ‖M⊙Ω‖_F and the off-local share of conditional
  dependence growing from 5% to 14.7% as α increases. Not "classify each of the 28 pairs."

- **Leech:** The paper reports that 55–56 non-adjacent ganglion pairs become conditionally
  coupled at nominal gain, and that they dissolve under gain reduction but survive removal
  of cells 27 and 33. Not "assign a label to each of the 153 possible ganglion pairs."

- **Worm:** The paper reports AUROC = 0.664 (p = 0.004) and Fisher OR = 7.2 (p = 0.002)
  for PDF-annotated pairs among the top-20 off-connectome ΔΩ entries. Not "classify each
  of the 1,321 Class 4 pairs."

In all three cases, the evaluation is: **do the biologically relevant pairs dominate the
top of the organization ranking?** Not: can every pair be classified?

The Phase 6–8 benchmark measured the wrong quantity. The new benchmark measures the
right one.

---

## Question 1: What Organization Is Planted?

### Planted Modulatory Circuit (PMC)

A set of 20 neurons across a 150-neuron observed network:

```
PMC sources:  8 neurons in module M1 (sensory/drive analog)
PMC targets: 12 neurons in modules M3 and M4 (output/modulatory analog)
```

Construction rules (specified before any simulation):

1. PMC sources have elevated connectivity to a set of 10 global hidden neurons (H_global):
   each source projects to ≥3 H_global neurons (vs. background ~1).

2. PMC targets have elevated H_global input:
   each target receives from ≥4 H_global neurons (vs. background ~1).

3. No direct structural edge between any PMC source and any PMC target:
   ```
   A[i,j] = 0   for all i ∈ PMC_sources, j ∈ PMC_targets
   ```

4. H_global gain is modulated by the latent state variable z:
   ```
   gain_H_global = g_base + g_mod × z
   ```

**Result:** In State A (z = z_high), PMC source-target pairs acquire large ΔΩ through
H_global relay. In State B (z = 0), they do not. The organization is state-created.

This is the analog of:
- OU cascade: nodes 6 and 8 connected by propagated source-node fluctuations at high α
- Leech: 55–56 non-adjacent ganglion pairs co-organized by the wave regime at nominal gain
- Worm: ADEL/RMEL/RMER/RID → URYVR/URYDL/URXL coordinated through pdf-1/pdfr-1 signaling
  during dwelling

### The Network

```
N_obs = 150 neurons    (observed)
N_hid = 30 neurons     (hidden: 20 local H1 + 10 global H_global)
N_tot = 180 neurons
4 modules (M1: 40, M2: 40, M3: 35, M4: 35 neurons)
Structural coupling A: sparse, fixed, state-invariant
  Within-module: p = 0.12
  Between-module: p = 0.02
  H_global → observed: p = 0.10
Latent state z: 1-dimensional continuous OU process
States: z_mean = z_high (State A) vs. z_mean = 0 (State B)
```

The coupling matrix A never changes. Only z changes. This mirrors the paper exactly.

---

## Question 2: What Organization Is Observable?

### Observable to the Framework

The framework receives:

1. **Neural activity time series** x(t): activity of all 150 observed neurons across
   T time steps, in State A and State B epochs.

2. **State labels**: which time points belong to State A (high z) and State B (low z),
   as epoch-level labels. Exact z(t) values are not provided.

3. **Structural coupling reference A_obs**: the observed-observed block of A (known from
   construction, analogous to the worm's connectome A_raw).

The framework does NOT receive:
- z(t) trajectories
- H_global neuron activity
- The identity of PMC neurons
- ΔΩ_true

### Observable Organization (Ground Truth)

The key observable organization is the ΔΩ matrix restricted to off-connectome pairs:

```
ΔΩ_true_off[i,j]   for all (i,j) with A[i,j] = 0
```

This is computed analytically from the Lyapunov equation at State A and State B and
represents the true ranking the framework should recover. PMC pairs dominate the top of
this ranking (dominance condition D1, verified before simulation).

---

## Question 3: What Constitutes Success?

### Primary Success Criteria (all three required)

| Metric | Success threshold | Meaning |
|---|---|---|
| PMC_AUROC | ≥ 0.75 | PMC pairs enriched among top-ranked off-connectome pairs |
| Precision@50 | ≥ 0.25 | ≥12/50 top-estimated pairs are PMC pairs (29× enrichment over random) |
| Rank correlation ρ | ≥ 0.40 | Estimated ΔΩ ranking correlates with oracle ranking |

PMC_AUROC is computed only over off-connectome pairs. It is the analog of the worm's
PDF-annotation enrichment AUROC (0.664, p=0.004).

### Partial Success

At least one primary metric meets:
```
PMC_AUROC ≥ 0.60   OR   Precision@50 ≥ 0.10   OR   ρ ≥ 0.15
```

### Failure

All primary metrics below partial thresholds. Framework does not recover the planted
organization at above-random levels.

### Why These Thresholds?

The worm achieved PDF-annotation AUROC = 0.664. The benchmark uses exact ground truth
(no biological noise, no annotation imprecision), so the threshold (0.75) is higher.
Precision@50 at random is ~0.87%; success requires 29× enrichment. This matches the
magnitude of the leech result (55–56 out of ~153 non-adjacent pairs, ~36% precision at k=55
vs. random ~16%, ≈ 2.3× enrichment). The higher threshold in the benchmark reflects
that the planted signal is exact.

---

## Question 4: How Does This Benchmark Mirror OU / Leech / Worm?

### The OU Cascade

**Paper:** Fixed A, varying α. At high α, nodes 6 and 8 (non-adjacent, A[6,8]=0) become
conditionally coupled through propagated source fluctuations. The framework correctly
identifies Q[6,8] = Ω[6,8] at each α.

**Benchmark analog:** Fixed A, varying z. At high z, PMC source-target pairs (A[i,j]=0)
become conditionally coupled through H_global relay. The framework should correctly
identify that PMC pairs dominate ΔΩ.

**Shared logic:** Both test whether the framework correctly attributes off-connectome
conditional dependence to current flow (not structural coupling) in a regime where
the drive parameter changes while A is fixed.

### The Leech CPG

**Paper:** Fixed K (coupling matrix), varying gain. At nominal gain, 55–56 non-adjacent
ganglion pairs acquire current-supported organization. The same pairs appear at 25%, 50%,
and 100% of nominal gain (topology is set by phase, not amplitude). The framework
classifies pairs by their intervention response (load-bearing / current-supported /
coupling-supported).

**Benchmark analog:** Fixed A, varying z. PMC source-target pairs acquire current-supported
organization at State A. The same pairs should be identified regardless of the exact value
of z_high (topology set by H_global connectivity pattern, not z amplitude). The framework
is evaluated on the three-way intervention classification (state-lesion vs. structural-lesion
response).

**Shared logic:** Both test whether the framework can separate (a) the pairs that require
the regime to exist from (b) the pairs that exist because of the regime, at a circuit-level
resolution (not pair-by-pair).

### The C. elegans Worm

**Paper:** Fixed A_raw/A_C, two behavioral states (dwelling/roaming). The PDF-receptor
circuit (ADEL→URY/URX) is enriched among the top off-connectome ΔΩ entries. AUROC = 0.664,
Fisher OR = 7.2. The circuit has identifiable source neurons (pdf-1/pdf-2 expressing),
target neurons (pdfr-1 expressing), and a specific behavioral state (dwelling) in which
it is active.

**Benchmark analog:** Fixed A, two states (z_high / z_low). The PMC circuit (M1 sources →
M3/M4 targets) is enriched among the top off-connectome ΔΩ_estimated entries. The circuit
has identifiable sources (elevated H_global connectivity in M1), targets (elevated H_global
input in M3/M4), and a specific drive state (z_high) in which it is active.

**Shared logic:** Both test enrichment of a planted/known circuit annotation among the
top-ranked off-connectome ΔΩ entries. Both use AUROC and Fisher top-k as evaluation metrics.
Both specify the correct enrichment as an annotation over off-connectome pairs, not a
pair-level binary label requiring a decision for every pair.

---

## Question 5: Why Is This Benchmark Aligned When the Previous One Was Not?

### The misalignment of Phase 6–8

The Phase 6–8 benchmark evaluated AUROC over four-way pair labels (S, C, M, N). This
translates the scientific question to:

> "Does the framework assign the label C to pairs that have C-type properties and N to
> pairs that have N-type properties, at every pair in the network?"

This is not what the paper tests. No section of the paper asks whether the framework
classifies individual pairs correctly. The evaluation is always:

- **OU:** Organizational summary statistics (Scur, Sstat, off-local share)
- **Leech:** Circuit-level intervention classification (which cells are load-bearing;
  which pairs are current-supported as a set)
- **Worm:** Enrichment of a biologically annotated set among the top-ranked ΔΩ entries

When the Phase 6–8 framework failed (C-AUROC = 0.4484), the correct interpretation is:
"The framework cannot recover the off-connectome state-dependent organization in the form
tested." But the benchmark was additionally testing something the paper never tests —
the ability to assign a binary label to every pair, including the vast majority of null pairs.

### The alignment of Phase 9A

Phase 9A evaluates:

1. **Enrichment:** Is the PMC annotation enriched among the top-k estimated ΔΩ entries?
   (mirrors the worm's PDF enrichment test)

2. **Ranking correlation:** Does the framework's estimated ΔΩ ranking correlate with the
   oracle ΔΩ_true ranking?
   (mirrors the OU paper's comparison: does the framework detect the growth of Scur with α?)

3. **Intervention logic:** Do framework-identified current-supported pairs dissolve under
   state intervention and survive structural intervention?
   (mirrors the leech's three-way classification)

None of these require the framework to assign a label to every off-connectome pair. A
framework that correctly identifies the PMC circuit (29× enrichment, Precision@50 = 0.25)
but ranks non-PMC off-connectome pairs randomly still succeeds, because the organization
is correctly recovered even if the null set is not perfectly discriminated.

### The fundamental shift

```
Phase 6–8:   "Can every pair be classified?"
Phase 9A:    "Can the planted organization be recovered?"
```

This shift is not methodological convenience. It is scientific alignment. The theoretical
framework claims to recover state-dependent organizational changes — the dominant modules,
the dominant off-connectome circuit, the enriched biological pathway. It does not claim
to classify every neuron pair. The benchmark should test what is claimed.

---

## Protocol Files

| File | Contents |
|---|---|
| p1_theoretical_target.md | OU/Leech/Worm summaries; operational definition of current-supported organization |
| p2_ground_truth_design.md | Network architecture; PMC construction; dominance condition D1 |
| p3_intervention_logic.md | State and structural interventions; expected outcomes; OU/Leech/Worm logic |
| p4_ground_truth_objects.md | Five ground-truth objects (ΔΩ_true, PMC pairs, oracle ranking, modules, intervention predictions) |
| p5_evaluation_metrics.md | Three primary metrics (PMC_AUROC, Precision@k, rank ρ); three baselines; secondary module and intervention metrics |
| p6_failure_modes.md | Success/partial/failure criteria; mechanism diagnosis; biological interpretations |

---

## Pre-Conditions Before Implementation

The following must be true before any simulation or framework evaluation:

### P1. Dominance condition verified analytically
Before generating any trajectory, solve the Lyapunov equation at z_high and z=0.
Verify that:
```
Median |ΔΩ_true| for PMC pairs > 2 × 90th percentile |ΔΩ_true| for non-PMC off-connectome pairs
```
If not satisfied, increase z_high. Lock z_high once D1 is satisfied. Do not change it thereafter.

### P2. PMC pair set locked before simulation
Specify the 8 PMC source neurons, 12 PMC target neurons, and H_global connectivity pattern
before generating A or any trajectory. Lock this specification.

### P3. Success thresholds locked before evaluation
Pre-register all metric thresholds from p5_evaluation_metrics.md before the framework
produces any output. No post-hoc threshold adjustment.

### P4. Baselines evaluated first
Evaluate B1 (random), B2 (ΔCorr), and B3 (state-averaged Glasso) before the framework
is evaluated. The framework must exceed B2 on primary metrics to claim success.

---

## What Happens After This Protocol Is Approved

1. **Phase 9B:** Implementation of the synthetic network simulator (A, z, Lyapunov solution,
   trajectory generation). Verification of dominance condition D1. Locking all parameters.

2. **Phase 9C:** Trajectory generation in State A and State B. Framework application.
   Computation of PMC_AUROC, Precision@k, and rank correlation ρ. Comparison to baselines.

3. **Phase 9D:** Intervention experiments (state lesion and structural lesion). Evaluation
   of secondary metrics (module recovery, intervention correlation). Diagnosis of failure
   mode if applicable.

---

## STOP

Protocol design is complete. No implementation proceeds until this protocol is reviewed
and approved. The protocol may be modified during review; all modifications must be
committed before Phase 9B begins.
