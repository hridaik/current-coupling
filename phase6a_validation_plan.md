# Phase 6A — Validation Plan

## Design Principle

The validation workflow is structured as a **strict information barrier**. Ground truth
is computed from construction parameters and sealed before simulation. Analysis receives
only activity traces. The two pipelines never communicate until the final evaluation
step, which is governed by locked, pre-specified metrics.

Any workflow that allows information from the analysis pipeline to influence ground truth
assignment, or allows ground truth knowledge to influence analysis choices, is invalid.

---

## Pipeline Overview

```
Construction Parameters
        │
        ├─── [PIPELINE A: GROUND TRUTH] ─────────────────────────────────┐
        │    Compute labels from A, G(z), B(z), H2 topology              │
        │    Seal label file (record SHA-256 hash)                        │
        │    Lock all thresholds (δ_lr, S/M threshold)                    │
        │                                                                  │
        └─── [PIPELINE B: DATA GENERATION] ──────────────────────────────┤
             Simulate trajectories x(t) using A, D(z), z(t)              │
             Apply observation pipeline                                    │
             HIDE: A, D(z), z(t), all construction parameters             │
                                                                          │
[PIPELINE C: FRAMEWORK ANALYSIS]                                          │
    Receives ONLY: activity traces x_obs(t), T, N_obs                     │
    Optionally receives: oracle z(t) in primary condition                 │
    Produces: scored classification per directed pair (i,j)               │
                                                                          │
[PIPELINE D: BLIND EVALUATION] ◄──────────────────────────────────────────┘
    Receives: framework scores + sealed ground truth labels
    Computes: all pre-specified metrics
    Produces: final report
```

---

## Stage 1 — Pre-Simulation Specification

Everything in this stage is completed and committed before any simulation trajectory
is generated.

### 1.1 — Network construction specification

Commit the following parameters to a locked specification file:

- N_obs = 100, N_hidden = 40, N_total = 140
- Module assignments: which of the 140 neurons belong to M1, M2, M3, M4
- H1 neuron count, H2 neuron count, and module assignments for each
- H2 target-module mapping (which modules each H2 neuron projects to)
- A_sparse generation seed and parameters (p_within = 0.15, p_between = 0.03,
  weight distribution)
- A_lr rank (2 or 3), U and V matrices
- Gain modulation functions g_k(z) for all k ∈ SA (state-active neurons)
- State drive functions B[k](z) for all k with sdrv(k)=1
- D_diag baseline values, D_diag(z) modulation amplitude
- D_lr component
- z(t) process: dimensionality, autocorrelation time, amplitude distribution,
  number of states or continuous parameterization
- Observation pipeline parameters: f(·) nonlinearity, calcium kernel κ, measurement
  noise σ, subsampling fraction and scheme (random uniform vs. structured)
- T (total simulation length in time steps)
- Number of independent simulation runs R (recommended R ≥ 5)

**Stability check (must pass before proceeding):**
- Spectral radius of A_eff(z) ≤ 0.85 for all z in the support of z(t)
- Compute this analytically from the locked parameters

**SNR check (must pass before proceeding):**
- Compute ΔΩ_true = Ω_true(z_high) − Ω_true(z_low) analytically from Lyapunov equation
- Compute expected estimation error ||ΔΩ̂ − ΔΩ_true||_F for the planned T
- Confirm SNR = ||ΔΩ_true||_F / expected_error ≥ 3 for the primary condition
- If SNR < 3, increase T or increase z modulation amplitude (requires re-running 1.1)

Note: these SNR checks use Ω_true to verify the benchmark is feasible, not to assign
ground truth labels. This use is permitted because Ω_true is used only as a feasibility
filter on construction parameters, applied before any simulation.

### 1.2 — Ground truth label computation

Execute the label-assignment procedure from `phase6a_ground_truth_spec.md` using the
locked construction parameters. This produces:

- DIRECT(i,j) for all 9900 ordered pairs
- LR(i,j) for all pairs
- SAREACHABLE(i → j) for all pairs
- Label(i,j) ∈ {S, C, M, N, LR} for all pairs

**Record and lock:**
- SHA-256 hash of the label file
- Class counts: |S|, |C|, |M|, |N|, |LR|
- Class imbalance ratios

**Imbalance check (must pass before proceeding):**
- Verify |C| ≥ 20 and |S| ≥ 20 (minimum class sizes for meaningful evaluation)
- Verify |C| / (|S| + |C| + |M|) ≥ 0.10 (C must be at least 10% of non-null pairs)
- If not satisfied, revise H2 topology or z drive strength and re-run 1.1–1.2

### 1.3 — Pre-specified metrics and thresholds

Lock the following before simulation:

**Thresholds:**
- Framework classification threshold for each class (from prior-phase analysis or
  biological priors, not from this benchmark)
- S/M threshold: a pair is M if |ΔA_eff[i,j]| / |A_eff_baseline[i,j]| > 0.20
- LR threshold δ_lr: 95th percentile of |(U_o·Vᵀ_o)[i,j]|

**Primary metric:**
- C-detection precision and recall (over non-null pairs: S ∪ C ∪ M)
- S-detection precision and recall (over non-null pairs)
- S↔C confusion rate (fraction of C pairs classified as S, and vice versa)

**Secondary metrics:**
- Four-way classification accuracy (reported but not primary)
- AUROC for C-detection (one-vs-rest, restricted to non-null pairs)
- Calibration (expected calibration error over the full pair set)

**Baseline metrics (computed from ground truth, no framework required):**
- Random classifier performance (analytical, from class frequencies)
- Module-membership classifier (uses only module identity of i and j, ignores activity)
- Per-state Glasso (recovers S only, used as structural baseline)

**Criteria for outcomes (see Stage 4 for interpretation):**
- Success: C-recall ≥ 0.50 AND C-precision ≥ 0.50 AND S↔C confusion rate ≤ 0.20,
  all in the primary analysis condition (oracle z provided)
- Partial success: C-recall ≥ 0.30 OR C-precision ≥ 0.50, with identified failure modes
- Failure: C-recall < 0.30 AND C-precision < 0.30
- Inconclusive: SF1 or DF1 detected (finite-sample or weak-state failure prevents
  meaningful evaluation)

---

## Stage 2 — Data Generation

### 2.1 — What is generated

For each of R independent simulation runs:

- Simulate the full 140-neuron system: dx = A_eff(z)x dt + D(z)^{1/2} dW, starting from
  the stationary distribution
- Generate T time steps at the specified integration step size
- Apply the full observation pipeline: f(x_obs) → calcium convolution → measurement noise
  → subsampling
- Record y(t): the observed calcium traces for the N_obs observed neurons

### 2.2 — What is hidden from the analysis pipeline

The following are generated but immediately sealed and inaccessible to the analysis
pipeline:

- A (all blocks: A_oo, A_oh, A_ho, A_hh)
- D(z) at any z value
- The true latent state trajectory z(t) [EXCEPT in the oracle-z condition]
- The identity of hidden neurons (which indices are unobserved)
- All construction parameters from Stage 1.1

### 2.3 — What is revealed to the analysis pipeline

**Primary condition (oracle z):**
- y(t): observed calcium traces
- z(t): the true latent state trajectory (provided as an observable input)
- T, N_obs, sampling rate

**Secondary condition (blind z):**
- y(t): observed calcium traces only
- T, N_obs, sampling rate

**Both conditions must be evaluated.** The gap between oracle-z and blind-z performance
isolates the z-inference contribution to total error.

### 2.4 — Simulation conditions

Run all R trials under the following conditions:

| Condition | z amplitude | D(z) variation | T | Purpose |
|---|---|---|---|---|
| Primary | Standard | Standard | Full | Main benchmark |
| Weak-z | 0.25× standard | Standard | Full | Near-null test |
| Strong-z | 2.0× standard (if stable) | Standard | Full | High-SNR sanity check |
| No-obs-model | Standard | Standard | Full | Bypass calcium pipeline |
| Long-T | Standard | Standard | 4× full | Sample-size learning curve |

The No-obs-model condition provides the framework with the true latent neural state
(not calcium-filtered). Performance in this condition establishes the upper bound from
removing the observation model confound.

---

## Stage 3 — Framework Analysis

### 3.1 — Allowed inputs

The framework receives only what is specified in Stage 2.3. No other information.
Specifically forbidden from entering the analysis pipeline:

- Any knowledge of A, D, or z beyond what is provided in the condition specification
- The ground truth labels
- The class counts |S|, |C|, |M|, |N|
- Any output from prior phases that was computed from knowledge of this benchmark's
  construction

### 3.2 — Required outputs

The framework must produce, for each ordered pair (i,j):

- A classification ĉ(i,j) ∈ {S, C, M, N} using the pre-specified threshold from Stage 1.3
- A continuous score s(i,j) for each class (used for AUROC computation)

The framework must not produce or inspect ground truth labels at any point during analysis.

### 3.3 — Analysis procedure (framework-internal, not specified here)

The framework applies its own procedure (current-velocity estimation, state conditioning,
etc.) to the activity traces. The analysis procedure is fixed and not modified in response
to benchmark performance. Any modification to the analysis procedure during the benchmark
constitutes overfitting and invalidates the result.

If the framework has tunable parameters (regularization, bandwidth, etc.), these must be
set from cross-validation on held-out time windows, not from knowledge of the ground
truth class balance.

### 3.4 — Controls that must be run alongside the framework

The following controls run on the same data and are computed before the framework outputs
are evaluated:

**Control C1 — Module membership classifier:**
ĉ(i,j) = S if i and j are in the same module and i,j within 2 hops in A_sparse_oo,
else N. No activity data used. This establishes the module-structure performance floor.

**Control C2 — Per-state Glasso:**
Estimate Ω̂(z_high) and Ω̂(z_low) using Glasso (separate precision matrices per state).
Classify (i,j) as S if Ω̂_average[i,j] is large, C if Ω̂_diff[i,j] is large, N otherwise.
This is the strongest conventional baseline and the most important comparison.

**Control C3 — Oracle upper bound:**
Apply the framework with true A, D, z(t) provided (no estimation required). This gives the
upper bound on performance given the framework's classification logic applied to true
parameters, eliminating all estimation noise. If the oracle upper bound is below the
success threshold, the benchmark design or the framework's conceptual model has a
fundamental problem.

---

## Stage 4 — Blind Evaluation

### 4.1 — Label revelation

After all framework analyses are complete and outputs are saved:

1. Verify SHA-256 hash of the label file matches the hash recorded in Stage 1.2
2. Reveal labels to the evaluator
3. Confirm that the framework outputs were not modified after label revelation (check
   output file timestamps vs. label revelation timestamp)

### 4.2 — Metric computation

Compute all metrics pre-specified in Stage 1.3.

All metric computations use the **non-null pair restriction** for primary reporting:
the evaluation set for S-detection and C-detection metrics is {(i,j) : Label(i,j) ∈ {S,C,M}},
excluding N and LR pairs. This prevents N-class inflation from dominating metrics.

The full-pair metrics (including N) are computed as secondary metrics.

**For each simulation run r, compute:**
- Per-class precision and recall (primary metrics)
- AUROC for C-detection (non-null pairs)
- S↔C confusion rate
- Module-blind confusion matrix (within-module vs. between-module pairs)
- Performance gap: framework minus Control C2 (Glasso baseline)

**Aggregate across R runs:**
- Report mean ± standard deviation for all metrics
- Report 95% bootstrap confidence intervals

### 4.3 — Failure mode diagnosis

Before interpreting classification performance, run all diagnostic checks from
`phase6a_failure_modes.md`:

| Check | How | Decision |
|---|---|---|
| Finite-sample sufficiency (SF1) | T learning curve | Flag if not plateaued |
| Stability (DF2) | Spectral radius vs. z | Must pass; else invalid |
| State separation (DF1) | ||ΔΩ_true||_F / noise | Flag if SNR < 3 |
| D dominance (DF5) | ||ΔD(z)||_F / ||D_baseline||_F | Flag if > 0.2 |
| D/A alignment (IF3) | Eigenvector overlap | Report |
| H1 confounding (DF3) | False-S near H1 nodes | Report |
| Low-rank inflation (DF4) | Rank of Ω̂ vs. expected | Report |
| Module shortcut (CF3) | Framework vs. Control C1 gap | Report |

If any CRITICAL or HIGH-severity failure mode is triggered, that failure mode is
reported as the primary finding, and the classification performance is interpreted
conditional on the failure.

---

## Stage 5 — Final Reporting

### 5.1 — Outcome interpretation

**Success** (C-recall ≥ 0.50, C-precision ≥ 0.50, S↔C confusion ≤ 0.20, all in oracle-z
primary condition, with no CRITICAL failure modes triggered):

The framework correctly distinguishes structural from current-supported links at above-
chance rates. The result is consistent with the framework's theoretical claims.

Important caveats: success in the oracle-z condition does not imply success in the
blind-z condition; success on this benchmark does not imply success on different network
topologies or observation modalities.

**Partial success** (one or two of the three primary criteria met, or all met only in
the high-SNR condition):

The framework shows evidence of the hypothesized capability but with limited reliability.
Report which criteria are met and which are not, and which failure modes appear to limit
performance. Partial success is still scientifically meaningful if the failure modes are
identified: it indicates the framework's principle is sound but requires better estimation.

**Failure** (C-recall < 0.30 AND C-precision < 0.30 in oracle-z condition, with no
CRITICAL failure mode triggered that would confound the result):

The framework does not reliably identify current-supported links in this benchmark.
This is a strong negative result about the framework's discriminative ability.

**Inconclusive** (CRITICAL failure mode triggered: SF1 with T-learning-curve not
plateaued, DF2 stability violated, or CF1/CF2 circularity detected):

The benchmark result cannot be interpreted as a test of the framework because a
confounding failure mode prevents clean evaluation. The benchmark must be redesigned
before a conclusion can be drawn.

### 5.2 — Required elements of the final report

Every final report must include, in this order:

1. **Failure mode audit result** — which failure modes were detected and at what severity
2. **Baseline comparisons** — framework vs. Control C1 (module classifier), Control C2
   (Glasso), and random baseline
3. **Primary metrics** — C-recall, C-precision, S↔C confusion on non-null pairs,
   oracle-z condition
4. **Condition comparison** — oracle-z vs. blind-z gap; primary vs. weak-z vs. strong-z;
   with vs. without calcium observation model
5. **Outcome classification** — one of: success / partial success / failure / inconclusive
6. **Interpretation of failure modes** — if failure or partial success, which failure mode
   is the most plausible explanation
7. **Recommendations for Phase 6B** — what changes would be required to achieve a
   conclusive result if the current result is inconclusive or partial

### 5.3 — What the benchmark cannot conclude

Regardless of outcome, the following conclusions are not supported by this benchmark:

- **A positive result does not validate the framework on real biological data.** The
  benchmark uses a synthetic system with known, clean construction. Real systems
  have noise sources, nonstationarities, and unknown structure not present here.

- **A positive result does not validate the framework's physical interpretation.** The
  framework may correctly classify pairs as C for the wrong mechanistic reasons (e.g.,
  detecting H2-common-cause structure rather than recurrent flow).

- **A negative result does not disprove the framework's theoretical claims.** The
  benchmark may have subthreshold SNR (DF1), misspecified observation model (W17), or
  be too hard in a specific way (H1 confounding) that does not reflect the framework's
  intended domain.

- **Performance on the N class is not informative.** The overwhelming majority of pairs
  are N, and correct N-classification is trivial. No conclusion about the framework's
  value should be based on overall accuracy including N.

### 5.4 — Pre-registration

The entire content of Stage 1 (construction specification, ground truth labels, metrics,
thresholds, outcome criteria) must be committed to version control with a timestamp
before any simulation is run. The commit hash serves as the pre-registration record.

Any deviation from the pre-registered protocol must be clearly labeled in the report as
a post-hoc modification, with the original pre-registered result also reported.
