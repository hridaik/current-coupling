# Phase 9B — Protocol Recovery Document

**Source:** Phase 9A protocol files (p1–p6, phase9a_protocol.md)  
**Purpose:** Exact transcription of frozen benchmark objective, design choices, success
criteria, failure criteria, and all identified ambiguities requiring clarification before
implementation begins.  
**Status:** READ-ONLY. No design decisions may be modified here. All changes require
amending the Phase 9A source files and re-freezing.

---

## 1. Benchmark Objective

The benchmark tests one question:

> **Can the framework recover the dominant state-dependent organization in a realistic
> high-dimensional recurrent network?**

This is an enrichment and ranking test, not a classification test. The framework is
evaluated on whether the planted circuit (PMC) is concentrated near the top of its
estimated ΔΩ ranking, not on whether it assigns correct labels to every pair.

The prior benchmark (Phases 6–8) asked: "Can every pair be classified?" That was
scientifically misaligned. The paper evaluates:

- **OU cascade:** growth of Scur and Sstat as α increases — organizational summaries
- **Leech:** which of the 55–56 non-adjacent ganglion pairs are current-supported — set recovery
- **Worm:** enrichment of PDF-annotated Class 4 pairs in top-ranked ΔΩ — circuit enrichment

None of these are pair-level classification accuracy. The new benchmark evaluates
organization recovery directly.

---

## 2. Frozen Network Design

All quantities below are from p2_ground_truth_design.md and are frozen.

### 2.1 Network Scale

```
N_obs   = 150   (observed neurons, framework receives activity only for these)
N_hid   = 30    (hidden neurons, never observed)
  H_local  = 20 (5 per module, local interneurons)
  H_global = 10 (global modulators — key mechanism for planted organization)
N_total = 180
```

### 2.2 Module Structure

```
M1: 40 neurons  (sensory/drive analog — PMC sources drawn from here)
M2: 40 neurons  (integration analog)
M3: 35 neurons  (motor-output analog — PMC targets drawn from here)
M4: 35 neurons  (modulatory analog   — PMC targets drawn from here)
```

### 2.3 Coupling Matrix A

Fixed throughout all states. No edge turns on or off. This is the key constraint
shared with the OU cascade (A fixed, α varies) and the leech (K fixed, gain varies).

```
p_within   = 0.12  (within-module connection probability)
p_between  = 0.02  (between-module connection probability)
p_local    = 0.15  (H_local → observed, within module only)
p_global   = 0.10  (H_global → observed, all modules)
Edge weights: truncated normal, mean 0, std 0.3
Stability:  all eigenvalues of A in (-1, 0)
```

### 2.4 Latent State Variable

```
dz = -θ_z × z × dt + σ_z × dW_z
State A: z_mean = z_high  (to be determined by dominance condition D1)
State B: z_mean = 0
```

z(t) is NEVER provided to the framework. Framework receives only epoch-level state labels
(A vs. B), exactly as the worm framework received roaming/dwelling epoch labels but not
the underlying neuromodulatory signal.

### 2.5 Diffusion Matrix

```
D_B = D_base          (diagonal, log-normal neuron-specific amplitudes)
D_A = D_base + g_D × z_high × D_PMC_sources
```

D_PMC_sources is diagonal with elevated entries only at the 8 PMC source neurons in State A.
Mirrors paper: URXL and URYVL had the largest ΔD during roaming.

---

## 3. Frozen Planted Organization

All quantities below are from p2_ground_truth_design.md and are frozen.

### 3.1 PMC Definition

```
PMC_sources:  8 neurons from M1, designated before any simulation
PMC_targets: 12 neurons from M3 and M4, designated before any simulation
PMC pairs:   96 directed source-target pairs
```

### 3.2 Construction Rules (the non-circular ground truth)

```
Rule 1: Each PMC source projects to ≥3 of the 10 H_global neurons
        (background rate ≈1)
Rule 2: Each PMC target receives from ≥4 of the 10 H_global neurons
        (background rate ≈1)
Rule 3: A[i,j] = 0 for all i ∈ PMC_sources, j ∈ PMC_targets
        (enforced by construction — no direct structural edge)
Rule 4: effective gain of H_global = g_base + g_mod × z(t)
        (H_global transmit more strongly in State A)
```

PMC membership is defined by H_global connectivity topology — NOT by state-sensitivity
of ΔΩ. This eliminates the Phase 6A circular labeling vulnerability (L2).

### 3.3 Dominance Condition D1

Before any simulation or framework evaluation, verify analytically from the Lyapunov
solution:

```
D1: median |ΔΩ_true[i,j]| for (i,j) ∈ PMC pairs
    > 2 × 90th_percentile |ΔΩ_true[i,j]| for (i,j) ∉ PMC pairs, A[i,j]=0
```

If D1 fails: increase z_high and recheck. Lock z_high once D1 is satisfied. Never
change z_high after D1 is verified.

Additionally, pre-verify:
```
D2: At least 60% of Top_50_oracle are PMC pairs
```

---

## 4. Frozen Ground-Truth Objects

All five ground-truth objects are derived from construction parameters before any
simulation. They are never exposed to the framework.

| Object | Definition | Derivation |
|---|---|---|
| GT1: ΔΩ_true | D_A×Q_A − D_B×Q_B, full 150×150 matrix | Lyapunov at z_high and z=0 |
| GT2: PMC pair set P | 96 directed (i,j) with i∈PMC_src, j∈PMC_tgt, A[i,j]=0 | Construction topology |
| GT3: Oracle ranking | All ~10,995 off-connectome pairs ranked by |ΔΩ_true_off| | From GT1 |
| GT4: Community structure | {C_src=PMC_sources, C_tgt=PMC_targets, background} | PMC membership |
| GT5a: State-lesion ranking | |Ω_A − Ω_B0| where B0 = z=0 condition | Lyapunov at z_high and z=0 |
| GT5b: Structural-lesion ranking | |Ω_A − Ω_A_lesioned| where lesion = M1→M2 edges removed | Lyapunov at z_high, A_lesioned |

**NOT ground truth:** Q_A_estimated, Q_B_estimated, Ω_A_estimated, Ω_B_estimated,
ΔΩ_estimated, any framework output, per-pair S/C/M/N labels.

---

## 5. Frozen Evaluation Metrics

### 5.1 Primary Metrics

All three primary metrics must be evaluated. Success requires all three to meet the
success threshold simultaneously.

#### M1: Precision@k

```
Precision@k = |{top-k estimated ΔΩ_off pairs} ∩ PMC pair set| / k
```

Computed at k = 20, 50, 100. Primary decision uses k=50.

"top-k estimated" means: the k off-connectome pairs (A[i,j]=0) with the largest
absolute value of the framework's estimated ΔΩ (or ΔQ if that is the framework's output).

#### M2: Rank Correlation with Oracle

```
ρ = Spearman correlation between:
    rank_estimated(i,j) [by |ΔΩ_estimated_off|, descending]
    rank_oracle(i,j)    [by |ΔΩ_true_off|, descending, = GT3]
```

Computed over all ~10,995 off-connectome pairs.

#### M3: PMC_AUROC

```
PMC_AUROC = AUROC(binary_PMC_label, |ΔΩ_estimated_off|)
```

Binary label: 1 if (i,j) ∈ PMC pair set, 0 otherwise. Computed only over off-connectome
pairs. Null = 0.50 under random ranking.

### 5.2 Success / Partial / Failure Thresholds (frozen)

| Metric | Success | Partial | Failure |
|---|---|---|---|
| M1: Precision@50 | ≥ 0.25 | ≥ 0.10 | < 0.05 |
| M2: ρ rank correlation | ≥ 0.40 | ≥ 0.15 | < 0.10 |
| M3: PMC_AUROC | ≥ 0.75 | ≥ 0.60 | < 0.55 |

**Verdict rules:**
- SUCCESS: all three primary metrics meet Success threshold
- PARTIAL: at least one meets Partial, none meets Success on all three
- FAILURE: all three primary metrics below Partial threshold

### 5.3 Secondary Metrics

| Metric | Success | Partial |
|---|---|---|
| NMI_module | ≥ 0.40 | ≥ 0.20 |
| ρ_state intervention | ≥ 0.30 | ≥ 0.15 |
| ρ_structural intervention | ≥ 0.40 | ≥ 0.20 |

Secondary metrics do not change the primary verdict. They provide mechanistic
interpretation.

### 5.4 Diagnostic Metrics (not part of verdict)

```
S_AUROC       (structural pair recovery — expected to be high)
Macro_AUROC   (mean of PMC_AUROC, S_AUROC, N_AUROC — Phase 8B analog for reference only)
```

### 5.5 Pre-Specified Baselines

All baselines are evaluated BEFORE the framework is evaluated. The framework must exceed
B2 on all three primary metrics to claim that it adds value beyond simple correlation change.

```
B1: Random ranking          — PMC_AUROC ≈ 0.50, Precision@50 ≈ 0.87%, ρ ≈ 0
B2: |ΔCorr_AB|              — rank off-connectome pairs by |corr_A[i,j] − corr_B[i,j]|
B3: Glasso pooled           — rank off-connectome pairs by |Q_pooled[i,j]|, no state info
B4: Oracle (GT1)            — rank by |ΔΩ_true_off|, ceiling for all metrics
```

---

## 6. Frozen Intervention Logic

From p3_intervention_logic.md:

### 6.1 State Intervention
Set z_mean = 0, recompute Lyapunov. Expected: PMC pairs lose their ΔΩ. Structural
pairs are unchanged. ΔΩ_state_lesion is dominated by PMC pairs.

### 6.2 Structural Intervention
Remove M1→M2 directed edges from A, recompute Lyapunov at z_high. Expected: M1→M2
structural pairs change in precision. PMC pairs are unchanged (they route through H_global,
not M1→M2). ΔΩ_structural_lesion is dominated by structural pairs, NOT PMC pairs.

### 6.3 Three-Way Classification (Leech Analog)

| Pair type | Structural intervention | State intervention |
|---|---|---|
| PMC (current-supported) | Survives | Dissolves |
| Structural (coupling-supported) | Dissolves | Survives |
| Non-PMC off-connectome (null) | Near-zero ΔΩ in both conditions | Near-zero ΔΩ in both conditions |

---

## 7. Frozen Failure Modes

From p6_failure_modes.md:

| Outcome | Criteria | PMC_AUROC | Mechanism |
|---|---|---|---|
| A: Success | All primary ≥ Success threshold | ≥ 0.75 | Framework recovers planted organization |
| B: Partial | At least one primary ≥ Partial | 0.55–0.74 | Signal attenuation, diffuse detection, or module-only recovery |
| C: Failure | All primary < Partial | < 0.55 | Z-regression destroys signal (C1), noise floor (C2), or structure-only (C3) |
| D: Invalid | Dominance D1 fails | N/A | Signal too weak; redesign benchmark |

---

## 8. What the Framework Receives (Framework Interface — Frozen)

```
INPUT TO FRAMEWORK:
  x_A(t): (T_A, 150) neural activity in State A epochs
  x_B(t): (T_B, 150) neural activity in State B epochs
  A_obs:  (150, 150) observed-observed block of the coupling matrix
           (known from construction, analogous to C. elegans connectome)

NOT PROVIDED:
  z(t)              — latent state trajectory
  H_global activity — hidden neurons
  PMC membership    — which neurons are sources/targets
  ΔΩ_true           — oracle matrix
  GT1–GT5           — any ground-truth object

OUTPUT FROM FRAMEWORK:
  ΔΩ_estimated:  (150, 150) estimated current difference matrix
                 OR equivalently ΔQ_estimated if D approximation is used
  Any per-pair score that can be converted to a ranking of off-connectome pairs
```

---

## 9. Ambiguities Requiring Clarification Before Implementation

The following items are identified as under-specified in Phase 9A. They must be resolved
and locked before Phase 9B implementation begins.

### A1. z_high exact value [BLOCKER]

p2 specifies that z_high is set to satisfy D1, but does not give a starting value or
search range. Implementation requires a concrete z_high search procedure:
- Starting point for z_high search?
- Maximum allowed z_high (avoid numerical instability)?
- Precision required for D1 verification (e.g., does 2.01× satisfy 2×)?

**Resolution needed:** Specify z_high search range [z_min, z_max] and the exact
numerical criterion for D1.

### A2. g_mod and g_base values [BLOCKER]

The H_global gain rule is `gain = g_base + g_mod × z`. The values of g_base and g_mod
are not specified in the protocol. They must be committed before simulation.

**Resolution needed:** Specify g_base and g_mod, or specify the constraint on g_mod
(e.g., g_mod × z_high / g_base ≥ 5, meaning at least 5× amplification in State A).

### A3. Directed vs. undirected PMC pairs [BLOCKER]

p2 specifies "96 directed source-target pairs" (8 sources × 12 targets). But ΔΩ_true
is a symmetric matrix (Σ is symmetric, Q is symmetric). Should PMC pairs be evaluated
as directed (96 ordered pairs) or undirected (96 unordered pairs)? The worm evaluation
used directed pairs for the PDF annotation (pdf-1-expressing → pdfr-1-expressing).

**Resolution needed:** Clarify directed vs. undirected convention for GT2 and the
Precision@k metric.

### A4. Structural lesion target for GT5b [SECONDARY]

p3 specifies removing "all within-module edges from M1 to M2" for the structural
intervention. The exact set must be specified (all M1→M2 directed edges? or all M1↔M2
edges, including M2→M1?). The lesion must be large enough to cause measurable ΔΩ in
structural pairs but must not overlap with any H_global relay path.

**Resolution needed:** Confirm the structural lesion set (M1→M2 directed edges only, or
bidirectional M1↔M2). Verify that no PMC relay path passes through this set.

### A5. Trajectory length T [SECONDARY]

The protocol does not specify the trajectory length T for State A and State B epochs.
T determines the finite-sample noise in the framework's precision estimates. The signal-
to-noise ratio for PMC pair recovery scales as O(T^{-1/2}). The C2 failure mode
(noise floor) can occur at small T even with a large planted signal.

**Resolution needed:** Specify T_A and T_B (or a single T with equal split). Based on
Phase 8B experience (T_eff ≈ 48,000 with N=100; n/p = 480), for N=150, a rough target
is T ≥ 100,000 per state to achieve n/p ≥ 667.

### A6. Structural pair definition for S_AUROC diagnostic [MINOR]

The diagnostic metric S_AUROC requires a binary structural label. p4 specifies
"Structural (S): A[i,j] ≠ 0" but does not distinguish the observed-observed block
from hidden-observed edges. Only observed-observed structural edges should be used
(framework cannot observe H_global).

**Resolution needed:** Confirm S label = A_obs[i,j] ≠ 0 (observed-observed block only).

### A7. Spectral clustering parameters for NMI_module [MINOR]

p5 specifies spectral clustering on M_off = |ΔΩ_estimated_off| with k=3 clusters.
The exact algorithm (normalized vs. unnormalized Laplacian, random state, convergence
criterion) must be specified before evaluation so the module recovery metric is
reproducible.

**Resolution needed:** Lock spectral clustering hyperparameters: algorithm variant,
random seed, k=3, evaluation repeated N times with different seeds and results averaged.

---

## 10. Items That Are NOT Ambiguous (Closed)

The following items were identified as risks in Phase 6A but are resolved in Phase 9A:

| Risk | Resolution in Phase 9A |
|---|---|
| L1: Definitional equivalence of C with ΔΩ | PMC membership defined by H_global topology, not by ΔΩ value |
| L2: State lesion used for both labeling and validation | PMC membership is topological; state-sensitivity is a *prediction* |
| L3: Low-rank A ambiguously structural | No low-rank component in Phase 9A A matrix; only sparse construction |
| W21: S/M threshold undefined | M class eliminated from benchmark; three-class only (S, PMC, null) |
| W25: AUROC inflated by N-class dominance | PMC_AUROC computed only within off-connectome pairs; S-class excluded |
| W7: H2-mediated ≠ probability current | Explicitly acknowledged; benchmark tests H_global relay detection, not thermodynamic current per se |
