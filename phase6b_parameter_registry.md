# Phase 6B — Parameter Registry

## Purpose

Every parameter used in the simulator is listed here with its exact frozen value,
scientific role, justification, acceptable range for sensitivity studies, and whether
it affects ground-truth labels.

**Justification constraint**: no parameter may be justified by "improves framework
performance," "makes C links detectable," or "increases classification accuracy."
All justifications must cite biological plausibility, mathematical stability,
identifiability, or benchmark interpretability.

Parameters marked **[AFFECTS LABELS]** directly change which pairs are labeled S, C, M,
or N. They may not be varied in sensitivity studies without re-generating labels.

Parameters marked **[DOES NOT AFFECT LABELS]** can in principle be varied without
changing labels, but such variations must be pre-registered before running any additional
simulations.

---

## Category 1 — Network Structure Parameters

### P01
**Name**: N_obs  
**Value**: 100  
**Role**: Number of observed neurons  
**Rationale**: 100 neurons gives ~9,900 directed pairs for evaluation — enough statistical
power to detect class differences while remaining computationally tractable. Standard
scale for in vivo calcium imaging experiments (large field-of-view two-photon).  
**Acceptable range (sensitivity)**: 50–200  
**Affects labels**: YES [AFFECTS LABELS] — changes the total pair count and module sizes

---

### P02
**Name**: N_H1  
**Value**: 32  
**Role**: Total H1 hidden interneurons (local, non-state-active)  
**Rationale**: 8 per module provides realistic local interneuron density. In neocortex,
~20–25% of neurons are inhibitory interneurons (local). With 25 observed per module,
8 H1 per module gives a local hidden fraction of 8/33 ≈ 24%, consistent with biology.  
**Acceptable range (sensitivity)**: 16–48  
**Affects labels**: NO [DOES NOT AFFECT LABELS] — H1 neurons are not state-active; their
paths do not contribute to SAREACHABLE

---

### P03
**Name**: N_H2  
**Value**: 8  
**Role**: Total H2 global modulator neurons (state-active)  
**Rationale**: 8 H2 neurons provide coverage of all 6 module pairs (one per pair, with
two pairs receiving double coverage) while keeping the total modulator count small
(analogous to neuromodulatory projection neurons being a minority of the circuit).
With 8 H2 neurons, every module has exactly 4 H2 sources, creating symmetric coverage.  
**Acceptable range (sensitivity)**: 4–16  
**Affects labels**: YES [AFFECTS LABELS] — H2 topology directly determines SAREACHABLE

---

### P04
**Name**: N_modules  
**Value**: 4  
**Role**: Number of functional modules  
**Rationale**: Four modules is the minimum to create a non-trivial H2 topology (6 module
pairs, allowing both "heavy" pairs with 2 H2 neurons and "light" pairs with 1) while
remaining small enough to interpret all inter-module relationships. Analogous to 4
cortical areas or 4 ganglia in a small invertebrate circuit.  
**Acceptable range (sensitivity)**: 3–6  
**Affects labels**: YES [AFFECTS LABELS]

---

### P05
**Name**: N_per_module  
**Value**: 25  
**Role**: Observed neurons per module  
**Rationale**: Equal module sizes simplify analysis and expected class count calculations.
25 per module gives dense within-module connectivity (25×24 = 600 directed pairs) while
ensuring that the ~585 expected S-links distribute interpretably across modules.  
**Acceptable range (sensitivity)**: Fixed (derived from P01 / P04 = 25; do not vary independently)  
**Affects labels**: YES [AFFECTS LABELS]

---

### P06
**Name**: N_H1_per_module  
**Value**: 8  
**Role**: H1 neurons per module  
**Rationale**: See P02. Fixed at 8 = N_H1 / N_modules.  
**Acceptable range (sensitivity)**: Fixed (derived from P02 / P04)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

## Category 2 — Graph Connectivity Parameters

### P07
**Name**: p_within  
**Value**: 0.15  
**Role**: Directed edge probability between observed neurons within the same module  
**Rationale**: Local cortical connectivity in dense regions has ~10–20% pairwise connection
probability (Markram et al. 1997; Song et al. 2005). 0.15 is a biologically plausible
mid-range value. At p=0.15 and 24 partners, each observed neuron receives ~3.6 within-
module inputs on average, giving a sparse but connected local circuit.  
**Acceptable range (sensitivity)**: 0.10–0.25  
**Affects labels**: YES [AFFECTS LABELS] — changes DIRECT values for within-module pairs

---

### P08
**Name**: p_between  
**Value**: 0.03  
**Role**: Directed edge probability between observed neurons in different modules  
**Rationale**: Long-range cortical connections are substantially sparser than local
connections. A factor of 5 reduction (0.15 → 0.03) is conservative but biologically
justified. At p=0.03, each observed neuron receives ~2.25 inputs from each other module
(75 neurons × 0.03 = 2.25), providing weak but real inter-module structural coupling.  
**Acceptable range (sensitivity)**: 0.01–0.06  
**Affects labels**: YES [AFFECTS LABELS] — changes DIRECT values for between-module pairs

---

### P09
**Name**: p_H1_in  
**Value**: 0.30  
**Role**: Probability that each observed neuron in a module projects to each H1 neuron in that module  
**Rationale**: Local interneurons in cortex receive dense input from nearby pyramidal
neurons. 30% of within-module observed neurons projecting to each H1 neuron is
biologically plausible (Holmgren et al. 2003). Gives each H1 ~7.5 inputs.  
**Acceptable range (sensitivity)**: 0.20–0.50  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P10
**Name**: p_H1_out  
**Value**: 0.25  
**Role**: Probability that each H1 neuron projects to each observed neuron in its module  
**Rationale**: Local interneurons project broadly within their module. 25% gives each H1
~6.25 outputs. Slightly less than p_H1_in to model integrator-type interneurons that
sample widely but project more selectively.  
**Acceptable range (sensitivity)**: 0.15–0.40  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P11
**Name**: p_H2_in  
**Value**: 0.20  
**Role**: Probability that each observed neuron in an H2's target module projects to that H2 neuron  
**Rationale**: Neuromodulatory neurons sample their projection areas but are not connected
to every neuron. 20% gives each H2 ~10 inputs from its 50-neuron target area (25 per
target module × 2 modules × 0.20 = 10 expected inputs). Sparser than H1 to reflect
the integrative character of modulatory projection neurons.  
**Acceptable range (sensitivity)**: 0.10–0.35  
**Affects labels**: YES [AFFECTS LABELS] — affects SAREACHABLE (whether path i→H2 exists)

---

### P12
**Name**: p_H2_out  
**Value**: 0.20  
**Role**: Probability that each H2 neuron projects to each observed neuron in its target modules  
**Rationale**: Matching p_H2_in for symmetry of the H2 relay structure. Gives ~10
outputs per H2 neuron. This creates an expected C-link probability of 0.04 per (i,j)
pair connected through a given H2, leading to ~700 total C-labeled pairs — a
statistically meaningful class while remaining a challenge for the framework.  
**Acceptable range (sensitivity)**: 0.10–0.35  
**Affects labels**: YES [AFFECTS LABELS] — affects SAREACHABLE (whether path H2→j exists)

---

## Category 3 — Weight Distribution Parameters

### P13
**Name**: σ_obs_obs  
**Value**: 0.30  
**Role**: Standard deviation of coupling weights between observed neurons  
**Rationale**: With self-inhibition -1.5 and ~9 expected inputs to each observed neuron,
the spectral contribution from off-diagonal weights is ~σ × sqrt(n_in) ≈ 0.30×3 = 0.90,
well below the self-inhibition magnitude of 1.5. This gives expected spectral abscissa
≈ -1.5 + 0.90 = -0.60, ensuring stable dynamics with good margin.  
**Acceptable range (sensitivity)**: 0.10–0.45 (stability check required above 0.35)  
**Affects labels**: NO [DOES NOT AFFECT LABELS] — weights don't change sparsity pattern;
only magnitudes change (magnitudes do not enter DIRECT or SAREACHABLE)

---

### P14
**Name**: σ_H1  
**Value**: 0.25  
**Role**: Standard deviation of H1 coupling weights (both in and out connections)  
**Rationale**: H1 neurons are local interneurons with smaller individual synaptic weights
than pyramidal-to-pyramidal connections, consistent with inhibitory post-synaptic
potential magnitudes in cortex. Smaller than σ_obs_obs to model weaker individual
interneuron synapses.  
**Acceptable range (sensitivity)**: 0.10–0.40  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P15
**Name**: σ_H2_in  
**Value**: 0.25  
**Role**: Standard deviation of weights on connections from observed neurons to H2  
**Rationale**: H2 receives from its target area but individual connections are modest.
Same as H1 weights for simplicity.  
**Acceptable range (sensitivity)**: 0.10–0.40  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P16
**Name**: σ_H2_out  
**Value**: 0.35  
**Role**: Standard deviation of weights on connections from H2 to observed neurons  
**Rationale**: H2 out-weights are larger than other weights (0.35 vs. 0.25) because H2
projection to observed neurons must produce a detectable state-dependent signal. With
self-inhibition -1.5 and γ_H2 = 3.0 (z drive), a typical H2→j weight of 0.35 creates
an H2-driven fluctuation in j of ~(0.35/1.5) × (H2 activity) ≈ 0.23 × (H2 activity),
giving SNR ≈ 1.8 as documented in the architecture spec.  
**Acceptable range (sensitivity)**: 0.20–0.50 (SNR check required)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P17
**Name**: A_self  
**Value**: -1.5  
**Role**: Diagonal self-inhibition applied to all 140 neurons  
**Rationale**: Self-inhibition provides the primary restoring force that ensures stability
regardless of the sparse random off-diagonal weights. -1.5 gives a fast decay time
τ = 1/1.5 ≈ 0.67 time units (6.7 integration steps), keeping the system well within
the stable regime. Biologically plausible as representing adaptation currents, spike-
frequency adaptation, and recurrent inhibition not explicitly modeled.  
**Acceptable range (sensitivity)**: -2.5 to -1.0 (stability check required)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

## Category 4 — State Parameters

### P18
**Name**: dim_z  
**Value**: 1  
**Role**: Dimensionality of the latent state z  
**Rationale**: Scalar z is the minimum design to create state-dependent dynamics. It
eliminates the interaction-effects failure mode (W12 in Phase 6A review) and makes
partial-vs-full lesion ambiguity (W10) irrelevant. Scalar z maps onto a single
"arousal" or "neuromodulatory tone" variable, a well-established concept in systems
neuroscience. Expansion to 2D is a Phase 6B extension.  
**Acceptable range (sensitivity)**: Fixed at 1 for primary benchmark  
**Affects labels**: YES [AFFECTS LABELS] — the SA definition assumes all H2 neurons
respond to the same z; multi-dimensional z would require different H2 subsets per dimension

---

### P19
**Name**: θ_z  
**Value**: 0.10  
**Role**: Mean-reversion rate of the OU latent state process  
**Rationale**: Gives autocorrelation time τ_z = 1/0.10 = 10 time units = 100 integration
steps. This is slow enough that the network has time to reach quasi-stationary behavior
within each z-regime (neural autocorrelation time ≈ 0.67 time units, 14× faster), but
fast enough that within the 4,800 effective simulation time units, z undergoes
~480 independent "states" — sufficient for state-conditioned covariance estimation.  
**Acceptable range (sensitivity)**: 0.05–0.20  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P20
**Name**: σ_z  
**Value**: 1.00  
**Role**: Noise amplitude of the z OU process  
**Rationale**: Combined with θ_z, gives stationary variance σ_z²/(2θ_z) = 5.0, standard
deviation ≈ 2.24. The range z ∈ [-3σ, +3σ] ≈ [-6.7, +6.7] gives a factor of ~13
variation in the H2 drive B_H2(z) = 3.0×z from -20 to +20, creating clearly
distinguishable high-z and low-z regimes. The zero-mean OU ensures symmetric coverage
of both states.  
**Acceptable range (sensitivity)**: 0.50–2.00  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P21
**Name**: γ_H2  
**Value**: 3.00  
**Role**: Gain of z-drive to H2 neurons (B_h(z) = γ_H2 × z for all h ∈ SA)  
**Rationale**: Set to achieve signal-to-noise ratio ≈ 1.8 for H2-driven fluctuations in
target observed neurons. Derivation: steady-state H2 response to constant z ≈ γ_H2 × z /
|A_self| = 3.0 × z / 1.5 = 2z. Downstream observed neuron j receives H2 drive
≈ E[|A[j,H2]|] × (H2 response) / |A_self| ≈ σ_H2_out × (2 × SD(z)) / 1.5
≈ 0.35 × 4.47 / 1.5 ≈ 1.04. Noise-driven fluctuation in j ≈ sqrt(d_0/(2×|A_self|))
= sqrt(1/3) ≈ 0.577. SNR = 1.04/0.577 ≈ 1.8.  
**Acceptable range (sensitivity)**: 1.0–6.0 (weak_z and strong_z conditions vary this implicitly)  
**Affects labels**: NO [DOES NOT AFFECT LABELS] — only the magnitude of z-drive, not the sparsity
pattern. SAREACHABLE depends only on A_sparse ≠ 0 indicators, not on weights.

---

### P22
**Name**: γ_H2_weak  
**Value**: 1.50  
**Role**: γ_H2 for the `weak_z` evaluation condition  
**Rationale**: Half the primary value, reducing SNR to ~0.9 (below unity). Tests whether
the framework can detect C links near the detection boundary.  
**Acceptable range (sensitivity)**: Fixed for the `weak_z` condition  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P23
**Name**: γ_H2_strong  
**Value**: 6.00  
**Role**: γ_H2 for the `strong_z` evaluation condition  
**Rationale**: Double the primary value, increasing SNR to ~3.6 (well above unity). Tests
whether high SNR enables near-perfect C detection. Confirms the benchmark can be solved
in principle. Stability check required: verify spectral abscissa remains < -0.1 at
max |z| × γ_H2_strong.  
**Acceptable range (sensitivity)**: Fixed for the `strong_z` condition  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

## Category 5 — Diffusion Parameters

### P24
**Name**: d_0  
**Value**: 1.00  
**Role**: Baseline diagonal innovation noise amplitude (D_diag = d_0 × I)  
**Rationale**: Unit noise normalizes the effective signal-to-noise calculation and
simplifies analytical Lyapunov computations. Noise-driven variance of observed neuron
k ≈ d_0 / (2 × |A_self|) = 1.0 / 3.0 ≈ 0.33, giving SD(x_k) ≈ 0.577. This is the
reference unit against which the H2 signal (SNR ~1.8) is compared.  
**Acceptable range (sensitivity)**: 0.50–2.00  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P25
**Name**: ε_lr  
**Value**: 0.10  
**Role**: Amplitude of the low-rank correlated noise component (D_lr = ε_lr × u × uᵀ)  
**Rationale**: ε_lr = 0.10 with ||u|| = 1 gives ||D_lr||_F = 0.10. The ratio
||D_lr||_F / ||D_diag||_F = 0.10 / sqrt(140) ≈ 0.0085, below the 5% threshold from
Phase 6A review (vulnerability W14). The low-rank noise adds realistic common-input
correlation while remaining a small perturbation to the diagonal structure.  
**Acceptable range (sensitivity)**: 0.00–0.50 (IF3 risk increases above 0.30)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P26
**Name**: D_state_dependent  
**Value**: False  
**Role**: Flag indicating whether D varies with z  
**Rationale**: Set to False (state-independent) to eliminate failure mode DF5 (D(z)
dominance). State-dependent noise is deferred to Phase 6B extensions.  
**Acceptable range (sensitivity)**: True/False (sensitivity study requires separate label generation)  
**Affects labels**: NO [DOES NOT AFFECT LABELS] (but may affect detectability of C labels)

---

## Category 6 — Observation Parameters

### P27
**Name**: κ_ca  
**Value**: 0.50  
**Role**: Calcium indicator decay rate constant  
**Rationale**: GCaMP6s (a standard calcium indicator) has ~500ms decay time constant.
At dt=0.1 time units, one time unit corresponds to ~100ms (typical neural timescale).
κ_ca = 0.50 gives decay time 1/κ_ca = 2 time units ≈ 200ms, consistent with fast
GCaMP variants (GCaMP6f). The discrete-time coefficient 1 - κ_ca × dt = 0.95 per step.  
**Acceptable range (sensitivity)**: 0.20–1.00 (longer decay → more temporal blurring)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P28
**Name**: σ_obs  
**Value**: 0.10  
**Role**: Standard deviation of additive measurement noise on calcium signals  
**Rationale**: σ_obs = 0.10 gives a measurement SNR of sqrt(signal variance) / σ_obs.
The typical calcium signal variance ≈ 0.33 / κ_ca² ≈ 0.33 / 0.25 = 1.32 (rough
estimate of calcium variance from neural variance with time constant 1/κ_ca).
Measurement SNR ≈ sqrt(1.32) / 0.10 ≈ 11.5, consistent with high-quality two-photon
imaging SNR.  
**Acceptable range (sensitivity)**: 0.05–0.50  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P29
**Name**: nonlinearity  
**Value**: softplus  (i.e., f(x) = log(1 + exp(x)))  
**Role**: Firing-rate nonlinearity applied to neural state before calcium dynamics  
**Rationale**: Softplus is a smooth, differentiable approximation to ReLU that maps
(-∞, +∞) → (0, +∞), consistent with non-negative firing rates. It avoids the kink
at zero (ReLU is not differentiable at 0), which can cause numerical issues in
gradient-based analyses. Softplus → linear for large positive x, which preserves
large-x dynamics.  
**Acceptable range (sensitivity)**: sigmoid, ReLU (different nonlinearities are a robustness test)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

## Category 7 — Simulation Parameters

### P30
**Name**: dt  
**Value**: 0.10  
**Role**: Euler-Maruyama integration step size  
**Rationale**: dt = 0.10 time units gives 10 steps per neural autocorrelation time
(τ_neural ≈ 0.67), ensuring the numerical integration is accurate. The stability
criterion |1 + A_self × dt| = |1 - 1.5 × 0.10| = 0.85 < 1 ensures the discrete-time
self-inhibition also remains stable.  
**Acceptable range (sensitivity)**: 0.01–0.10 (smaller dt improves accuracy but increases cost)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P31
**Name**: T  
**Value**: 50,000  
**Role**: Total integration steps per simulation run (before warm-up discard)  
**Rationale**: 5,000 time units = 500 z-autocorrelation times (τ_z = 10 time units).
Effective samples for covariance estimation (after calcium autocorrelation of ~2 time
units = 20 steps): T_eff / 20 ≈ 2,400 per run, or ~12,000 across R=5 runs. For
100-dimensional covariance estimation, 12,000/100 = 120× the dimension. This is
adequate for precision matrix estimation by standard thresholds.  
**Acceptable range (sensitivity)**: 20,000–200,000 (used in the `long_T` condition)  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P32
**Name**: T_warmup  
**Value**: 2,000  
**Role**: Integration steps discarded at start of each run (stationarity warm-up)  
**Rationale**: 200 time units = 20 z-autocorrelation times, ensuring z and x have both
reached stationarity. Neural stationarity requires ~5 neural autocorrelation times
(~3.3 time units = 33 steps); z stationarity requires ~5 z-autocorrelation times
(50 time units = 500 steps). 200 time units provides 4× margin for both.  
**Acceptable range (sensitivity)**: 500–5,000  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P33
**Name**: R  
**Value**: 5  
**Role**: Number of independent simulation runs  
**Rationale**: 5 runs provides both: (a) enough total data for stable covariance estimates
(5 × 48,000 = 240,000 effective steps), and (b) run-to-run variance estimates for
uncertainty quantification. 5 is the minimum for bootstrap confidence intervals.  
**Acceptable range (sensitivity)**: 3–20  
**Affects labels**: NO [DOES NOT AFFECT LABELS]

---

### P34
**Name**: master_seed  
**Value**: 42  
**Role**: Master random seed from which all sub-seeds are derived  
**Rationale**: Fixed seed ensures full reproducibility. Seed 42 is a convention; the
value is arbitrary but immutable.  
**Acceptable range (sensitivity)**: Any integer (different seeds test robustness to realization)  
**Affects labels**: YES [AFFECTS LABELS] — the sparsity pattern (DIRECT, SAREACHABLE)
depends on the random draw; different seeds give different A_sparse and different labels

---

## Label-Affecting Parameter Summary

The following parameters directly affect ground-truth labels. They may not be changed
after pre-commitment without re-generating and re-hashing labels:

| Parameter | Value | Effect on labels |
|---|---|---|
| P01 N_obs | 100 | Changes pair count and module sizes |
| P03 N_H2 | 8 | Changes SA set |
| P04 N_modules | 4 | Changes module structure |
| P05 N_per_module | 25 | Changes module sizes |
| P07 p_within | 0.15 | Changes DIRECT for within-module pairs |
| P08 p_between | 0.03 | Changes DIRECT for between-module pairs |
| P11 p_H2_in | 0.20 | Changes SAREACHABLE |
| P12 p_H2_out | 0.20 | Changes SAREACHABLE |
| P18 dim_z | 1 | Changes SA definition |
| P34 master_seed | 42 | Changes specific realization of A_sparse |

All other parameters affect dynamics, observation, or simulation but not labels.
