# Phase 6A — Failure Mode Analysis

## Preamble

This document catalogs the ways the current-velocity framework can fail on the Phase 6A
benchmark, including modes identified in the protocol (F1–F6) and additional modes
identified through adversarial analysis. For each mode:

- **Mechanism**: how it arises
- **Expected signature**: what you would observe in the results
- **Severity**: impact on the validity of the benchmark conclusion
- **Detectability**: how easily diagnosed post-hoc
- **Mitigation**: what design changes reduce the risk

Severity levels: **CRITICAL** (invalidates benchmark), **HIGH** (substantially confounds
interpretation), **MED** (distorts specific metrics), **LOW** (limited impact).

---

## Statistical Failures

### SF1 — Finite-sample covariance estimation failure

**Mechanism**: The precision matrix Ω̂ and current Q̂ are estimated from T time points of
100-dimensional activity. For a 100-neuron system, the sample covariance matrix is
unreliable unless T ≫ 100. With calcium imaging dynamics (temporal autocorrelation from
the kernel), the effective sample size is T/τ_eff, where τ_eff is the effective correlation
time of the calcium trace. For a 500ms calcium decay and 30Hz imaging, τ_eff ≈ 15 frames,
so 10,000 frames give ~667 effective samples — marginal for 100-neuron covariance estimation.

**Expected signature**: High variance in per-pair classification. Recall on C is low
(C links near the detection boundary fluctuate to N). Calibration curves are poorly fit.
The S↔C confusion matrix is noisy but not systematically biased.

**Severity**: HIGH. Finite sample failure looks exactly like framework failure to detect C
links, making it difficult to attribute poor C-recall to the estimation procedure vs. the
framework's conceptual model.

**Detectability**: Medium. Diagnostic test: repeat analysis on subsets of T to produce
a learning curve. If performance improves monotonically and has not plateaued at the full
T, finite-sample effects dominate.

**Mitigation**: Pre-specify T from a power analysis (what T is needed for Ω̂ to converge
within ε of Ω_true in spectral norm?). Analytical computation of T given the known A and D.
Report effective sample size after accounting for calcium autocorrelation.

---

### SF2 — Regularization-induced bias in precision estimation

**Mechanism**: Glasso or other regularized precision estimators introduce a sparsity bias
that preferentially zeros out weak edges. Structural edges with small A[i,j] and C links
with small indirect contributions are underestimated. The regularization hyperparameter λ
is typically chosen by cross-validation, which optimizes held-out likelihood — not
classification accuracy for the S/C/M/N task.

**Expected signature**: High precision on S (regularization retains strong direct edges)
but low recall on C (weak C links regularized to zero). The framework appears to work for
S but not for C. This is a correct assessment of the estimator, not a fundamental failure
of the framework's conceptual model.

**Severity**: HIGH. Attributing regularization-induced C-miss to the framework's theory is
incorrect. Regularization must be separated from theory.

**Detectability**: Medium. Diagnostic: vary λ and observe the precision-recall tradeoff for
C. If C-recall increases sharply as λ decreases (at the cost of increased false S), the
failure is regularization-driven.

**Mitigation**: Use non-regularized precision estimation for benchmark evaluation (at the
cost of requiring large T). Alternatively, report the oracle precision (computed from true
Σ analytically) as the framework's upper bound.

---

### SF3 — State estimation failure

**Mechanism**: The framework may require knowledge of the latent state z(t) to compute
state-specific statistics. If z(t) is inferred from the data rather than provided
directly, estimation errors in z propagate to errors in Ω(z) and Q(z). z-inference from
100-dimensional activity is itself a hard problem, especially when z is continuous and
multi-dimensional.

**Expected signature**: State-average statistics (ignoring z) perform similarly to
state-conditioned statistics. The benefit of state conditioning is invisible. This would
appear as low C-detection (C links emerge only when state is correctly conditioned).

**Severity**: HIGH if the framework requires z to be known. Medium if the framework
estimates z internally (tests both z-inference and current estimation simultaneously).

**Detectability**: Easy. Run the framework with oracle z (known state trajectory) vs.
inferred z. The gap measures z-inference contribution to total error.

**Mitigation**: Provide z(t) as a known observable in the primary benchmark condition.
The "hidden z" condition is a separate, harder challenge that should be clearly labeled
as such.

---

### SF4 — Non-stationarity and epoch contamination

**Mechanism**: If z(t) drifts slowly, the stationarity assumption underlying covariance
estimation is violated within any epoch. Long calcium recordings with slow z drift
produce covariance matrices that blend multiple states. Epoch-based analysis (split by
z value) may create too-short segments for reliable estimation.

**Expected signature**: Performance degrades monotonically as z drift rate increases.
Per-state precision matrices have inflated off-diagonal terms (cross-state bleeding).

**Severity**: MED. Primarily affects C-detection rather than S-detection.

**Detectability**: Easy. Diagnostic: compare performance under fast-switching z (epochs
are short but stationary) vs. slow-drifting z (epochs are long but non-stationary).

**Mitigation**: Pre-specify z(t) statistics to include a fast-switching condition
(z decorrelates within ~50 frames) and a slow-drift condition (z decorrelates over
~1000 frames). Report separately.

---

## Dynamical Failures

### DF1 — Weak state separation (F3 in protocol)

**Mechanism**: The gain modulation amplitude from z is too small to produce detectable
changes in Ω across states. The difference ΔΩ = Ω(high-z) − Ω(low-z) is below the
estimation noise floor. All C links appear as N because their state sensitivity is
below threshold.

**Expected signature**: Near-zero recall on C, near-100% recall on N. No qualitative
difference between per-state precision matrices. State lesion shows negligible effect
on activity statistics.

**Severity**: HIGH. The framework is correct in its mechanism but the benchmark
parameters are below the detection threshold. This is a benchmark parameter failure,
not a framework failure — but it is indistinguishable from framework failure in the
output metrics.

**Detectability**: Easy. Compute ΔΩ_true analytically from the Lyapunov equation for
the true parameters and compare its magnitude to the expected estimation error. If
||ΔΩ_true||_F ≪ ||ΔΩ̂ − ΔΩ_true||_F, the task is impossible regardless of framework quality.

**Mitigation**: Pre-compute the SNR for C-link detection using true parameters. If
SNR < 1, increase z modulation amplitude or reduce estimation noise (increase T).
This must be computed before running any simulations.

---

### DF2 — Attractor collapse under gain modulation

**Mechanism**: If z increases recurrent gain sufficiently, the dynamical system dx=Axdt
may approach the stability boundary (spectral radius of A approaches 1). Near this
boundary, the covariance Σ diverges and precision matrices become ill-conditioned.
C-link detection becomes unreliable not because of the framework but because the
dynamics are ill-posed.

**Expected signature**: Covariance matrices with very large eigenvalues at high-z
states. Precision matrices nearly singular. Numerical instability in Ω̂ estimation.
Activity time series shows near-explosive dynamics or long-range autocorrelations.

**Severity**: CRITICAL if the network becomes unstable. HIGH if it becomes ill-conditioned.

**Detectability**: Easy. Compute spectral radius of A at each z value analytically and
ensure it remains below 1 with margin (recommended: spectral radius ≤ 0.85 at maximum z).

**Mitigation**: Constrain z modulation amplitude such that ρ(A_eff(z)) ≤ 0.85 for all z
in the support of the z process. This is a hard constraint that must be verified before
implementation.

---

### DF3 — Hidden-neuron confounding (F1 in protocol)

**Mechanism**: H1 local interneurons drive pairs of observed neurons simultaneously.
The pairs appear strongly coupled (high precision entry) but have no direct structural
edge. The framework may classify these as strong C links (good) or as strong S links
(bad — the H1 path is not state-dependent). If H1 neurons have no gain modulation,
these pairs are labeled N in the ground truth (no state-active path), but they appear
functionally coupled. The framework will likely classify them as S, producing false-S.

**Expected signature**: High false-S rate for within-module pairs separated by one
hidden interneuron. The S-precision is low even though the framework correctly identified
functionally strong pairs.

**Severity**: HIGH. This failure is not about C detection — it is about whether the
framework can distinguish direct S from H1-mediated apparent-S. This distinction may
be beyond the framework's scope.

**Detectability**: Easy to diagnose post-hoc: false-S pairs are systematically within-
module pairs with a shared H1 neighbor. Check whether false-S pairs have a common
H1 ancestor in the known construction.

**Mitigation**: Add a separate evaluation category for "H1-confounded N" pairs to
separate this failure mode from S/C confusion. The primary metric should exclude
these pairs from the S-precision computation.

---

### DF4 — Low-rank mode inflation (F2 in protocol)

**Mechanism**: The 2–3 global low-rank modes in A create population-level covariance that
appears as dense functional connectivity. The framework may detect the low-rank modes
as large blocks of apparent structural or current-supported links. This inflates apparent
S-density and reduces precision on the true sparse S set.

**Expected signature**: The recovered connectivity graph has a dense block structure
corresponding to pairs sharing low-rank population modes. S-precision is low (many
non-S pairs recovered as S). C pairs are buried under the low-rank noise floor.

**Severity**: MED-HIGH. Depends on the strength of A_lr relative to A_sparse.

**Detectability**: Moderate. Low-rank inflation produces characteristic singular-value
structure in the activity covariance. Comparing the rank of Ω̂ to the expected sparsity
reveals inflation.

**Mitigation**: Ensure A_lr entries are substantially smaller than A_sparse entries (in
spectral norm, ||A_lr|| ≪ ||A_sparse||). Report the ratio before implementation.

---

### DF5 — State-dependent diffusion dominates over coupling (F4 in protocol)

**Mechanism**: When D(z) varies substantially with state, the difference ΔΩ is driven
primarily by the change in D rather than the change in dynamics. The framework attributes
ΔΩ to current (recurrent flow changes) when it is actually driven by noise changes.
This produces spurious C detections (N pairs whose precision changes because D changed)
and potentially misses true C links (whose current signal is overwhelmed by D noise).

**Expected signature**: Many N pairs show up as C detections. State sensitivity of the
detected C set correlates with D(z) variance rather than with the SAREACHABLE indicator.

**Severity**: HIGH. If D(z) variation dominates, the benchmark is testing D-estimation,
not current estimation.

**Detectability**: Moderate. Run the framework on a system with D=constant to isolate the
coupling-driven component. Compare C-detection performance with and without D variation.

**Mitigation**: Keep D(z) variation small relative to D_baseline. Quantify this ratio
and report it: ||D(z₁) − D(z₂)||_F / ||D_baseline||_F should be ≤ 0.2.

---

### DF6 — Partial observation creates systematic bias (F5 in protocol)

**Mechanism**: When 20–30% of neurons are unobserved, the marginal process of observed
neurons is not a linear dynamical system with the same A_oo structure. The effective
coupling among observed neurons includes contributions from hidden neurons:
A_eff_oo = A_oo + A_oh (I − A_hh)⁻¹ A_ho. The framework applied to the observed process
recovers A_eff_oo, not A_oo. S links in A_oo may be absent from A_eff_oo (if they cancel
hidden contributions), and N pairs in A_oo may appear as S in A_eff_oo.

**Expected signature**: S-recall is below the level explainable by estimation noise.
Some N pairs are systematically classified as S. The errors cluster around pairs with
nearby hidden neurons.

**Severity**: HIGH. This is a fundamental identification failure for S links, not a
C-detection failure. It means the benchmark partially tests something different from
what is intended.

**Detectability**: Moderate. Compute A_eff_oo analytically from the known A blocks and
compare to A_oo. Pairs where A_eff_oo[i,j] ≠ A_oo[i,j] are "contaminated" and should
be flagged separately.

**Mitigation**: Define the ground truth for S links as A_eff_oo (the effective observed-
neuron coupling including hidden-neuron marginalization) rather than A_oo. Report both
the "anatomical S" (A_oo-based) and "effective S" (A_eff_oo-based) metrics separately.
This is a significant protocol change that requires rethinking the structural ground truth.

---

## Identifiability Failures

### IF1 — Diffusion/coupling ambiguity

**Mechanism**: The stationary covariance Σ satisfies AΣ + ΣA^T + D = 0. Given Σ alone,
A and D cannot be jointly identified without additional constraints. The framework must
make assumptions about D (e.g., diagonal D) to recover A. If these assumptions are
wrong (e.g., D has a low-rank shared component), the estimated A will absorb part of D's
contribution, producing spurious structural edges.

**Expected signature**: Spurious S detections (false-S) at pairs where D has correlated
noise. These pairs show up as structural even though A_sparse_oo[i,j] = 0. They may
cluster around the shared noise modes of D_lr.

**Severity**: HIGH. This is a fundamental identifiability issue, not an estimation issue.
Even with infinite data, A cannot be recovered from Σ without knowing D.

**Detectability**: Easy. Run the framework with known D provided as oracle. Compare
performance to the blind-D condition. The gap measures D-misspecification contribution.

**Mitigation**: Include an oracle-D condition in the evaluation where D is provided.
This separates the D-estimation problem from the S/C detection problem.

---

### IF2 — Latent low-rank structure absorbs apparent current

**Mechanism**: The low-rank component of A creates a low-dimensional attractor subspace.
The probability current in this subspace is large (the low-rank modes drive correlated
circulation). The framework may correctly detect large current along the low-rank modes
but misclassify these as C links between individual pairs rather than population-level
modes.

**Expected signature**: The detected C links form dense blocks corresponding to the
eigenvectors of U and V. High apparent C-precision at the population level but low
precision at the individual-pair level.

**Severity**: MED. Primarily a question of interpretation (population mode vs. pairwise
link) rather than a direct S/C confusion.

**Detectability**: Easy. Compute the SVD of the detected C connectivity matrix and
compare to the known UV^T structure.

**Mitigation**: Separate the LR class from C in the evaluation. Pairs with high LR(i,j)
are excluded from the C-precision computation.

---

### IF3 — Nonequilibrium ambiguity between drift and diffusion

**Mechanism**: In a linear SDE, nonequilibrium (probability current) can arise either
from antisymmetric components of A (driving cyclic dynamics) or from correlation between
noise components of D (if D is non-diagonal). A non-diagonal D with off-diagonal elements
creates apparent current even in a symmetric (gradient) system. If the benchmark's D has
a low-rank correlated noise component D_lr, the framework may attribute D_lr-induced
apparent current to A's structure.

**Expected signature**: C links detected at pairs that are connected through D_lr noise
modes but have no state-active path in A. These pairs are labeled N in ground truth
but detected as C by the framework.

**Severity**: HIGH if D_lr is substantial. The framework is detecting D-induced apparent
current and mislabeling it as A-induced current.

**Detectability**: Moderate. Compute the "expected current" from D_lr alone (analytically)
and check whether false-C pairs cluster around D_lr-driven pairs.

**Mitigation**: Ensure D_lr is genuinely weak. Quantify: ||D_lr||_F / ||D_diag||_F < 0.05.

---

## Conceptual Failures

### CF1 — Ground truth circularity (primary leakage, see L1 in review)

**Mechanism**: If the ground truth for C is derived using any quantity in the framework's
estimating family (Ω, Q, ΔΩ, or any precision-based measure), the benchmark becomes a
consistency check, not a validation. At large sample size, the framework reproduces the
exact computation used to define C, trivially achieving high performance.

**Expected signature**: Performance improves continuously and without bound as T increases.
No saturation in C-recall. The benchmark appears "too easy" at large T.

**Severity**: CRITICAL. Invalidates the benchmark entirely.

**Detectability**: Easy in principle: check whether the ground-truth labeling procedure
ever invokes a precision matrix, covariance matrix, or conditional independence test.

**Mitigation**: Enforce the construction-exclusivity constraint in `phase6a_ground_truth_spec.md`.
Hash the label file before any simulation begins (pre-commitment). Any label change after
simulation starts invalidates the benchmark.

---

### CF2 — Circular mechanistic validation (secondary leakage, see L2 in review)

**Mechanism**: The mechanistic validation metric "state sensitivity" (change under state
lesion) is identical in logic to the ground truth criterion "dependence disappears when
state drive removed" if state lesion is also used for ground truth labeling. The
mechanistic check becomes a consistency test, not an independent validation.

**Expected signature**: State sensitivity scores and ground truth C labels are nearly
perfectly correlated by construction (not by measurement). The metric appears highly
discriminating but has zero information content beyond the label itself.

**Severity**: HIGH. Makes the mechanistic validation uninformative.

**Detectability**: Conceptual — must be caught in protocol design, not in results.

**Mitigation**: Ground truth must be assigned from construction topology (as specified in
`phase6a_ground_truth_spec.md`). Only then does state lesion serve as an independent
sanity check rather than a circular validation.

---

### CF3 — Module-identity shortcut

**Mechanism**: The modular network structure creates a strong prior: within-module pairs
are more likely to be S, between-module pairs are more likely to be N or C. A classifier
using only module membership as a feature achieves substantially above-chance four-way
accuracy without using any current estimation. If the framework's features correlate with
module membership (which they will, since precision matrices reflect module structure),
the framework may appear to perform well simply because it has learned the module prior.

**Expected signature**: Performance on within-module pairs (where the true test is S vs.
H1-confounded-N) is much lower than on between-module pairs (where the true test is C
vs. N). Overall accuracy is high, but within-module accuracy is near chance.

**Severity**: HIGH for overall metrics. The headline performance number is misleading.

**Detectability**: Easy. Compute performance separately for within-module and between-
module pairs and compare to module-membership baseline.

**Mitigation**: Report all metrics stratified by within-module vs. between-module. Define
the primary metric as within-module S-detection accuracy, not overall four-way accuracy.
Between-module C detection is a secondary test.

---

### CF4 — Tautological definition of Class M

**Mechanism**: Class M (mixed) is defined as having both direct coupling and state-
sensitive response. But in a connected network with gain modulation, virtually every
direct edge (A_sparse[i,j] ≠ 0) will have some state sensitivity, because z modulation
changes the network-wide dynamics, which feeds back onto every edge's effective
contribution. The S/M distinction requires a threshold for "substantial state sensitivity"
that is not defined in the current protocol.

If the threshold is set to zero (any state sensitivity → M), then S is empty.
If the threshold is set infinitely high (M requires very large state sensitivity), then M
is empty. The size of the S and M classes is determined entirely by the threshold choice.

**Expected signature**: Large sensitivity of S/M class balance to threshold choice.
The framework's S/M confusion rate is threshold-dependent in a way that is not informative
about the framework's capability.

**Severity**: MED. Primarily affects the M and S class sizes; C detection is unaffected.

**Detectability**: Easy. Sweep the threshold and observe the class size ratio.

**Mitigation**: Define the S/M threshold from biological considerations: a pair is M if
z modulation changes the effective coupling A_eff[i,j](z) by more than 20% relative to
baseline. This is a pre-specified biological threshold, not a threshold tuned to the
framework's operating point.

---

### CF5 — Evaluation granularity mismatch

**Mechanism**: The framework may produce continuous scores (e.g., a "current score" for
each pair) while the ground truth is a discrete label. The conversion from continuous
score to discrete label requires a threshold. If this threshold is set by optimizing
accuracy on the benchmark data, the framework is being evaluated on its optimal tuning,
not its pre-specified operating point. This is a form of label leakage.

**Expected signature**: Performance appears higher when thresholds are tuned to the
benchmark than when they are set from priors. The gap between tuned and prior-set
performance measures the degree of leakage.

**Severity**: MED-HIGH. Depending on the threshold sensitivity of the framework.

**Detectability**: Easy. Set thresholds from the prior-phase analyses (or biological
priors) and report performance without any threshold tuning on the benchmark data.

**Mitigation**: Pre-specify all thresholds before seeing the benchmark data. If the
framework produces continuous scores, evaluate with AUROC rather than accuracy to avoid
threshold dependence. Accuracy should only be reported at the pre-specified threshold.

---

## Summary Table

| ID | Failure Type | Mode | Severity | Detectability | Priority |
|----|---|---|---|---|---|
| CF1 | Conceptual | Ground truth circularity (leakage L1) | CRITICAL | Easy | P0 |
| CF2 | Conceptual | State lesion circularity (leakage L2) | HIGH | Conceptual | P0 |
| DF2 | Dynamical | Attractor collapse | CRITICAL | Easy | P1 |
| SF1 | Statistical | Finite-sample estimation | HIGH | Medium | P1 |
| DF5 | Dynamical | D(z) dominates ΔΩ | HIGH | Moderate | P1 |
| DF3 | Dynamical | H1 confounding (protocol F1) | HIGH | Easy | P1 |
| IF1 | Identifiability | D/A ambiguity | HIGH | Easy | P1 |
| CF3 | Conceptual | Module-identity shortcut | HIGH | Easy | P1 |
| DF6 | Dynamical | Partial observation bias (protocol F5) | HIGH | Moderate | P2 |
| SF2 | Statistical | Regularization bias | HIGH | Medium | P2 |
| SF3 | Statistical | State estimation failure | HIGH | Easy | P2 |
| DF1 | Dynamical | Weak state separation (protocol F3) | HIGH | Easy | P2 |
| IF3 | Identifiability | D_lr-induced apparent current | HIGH | Moderate | P2 |
| DF4 | Dynamical | Low-rank inflation (protocol F2) | MED | Moderate | P3 |
| CF4 | Conceptual | S/M threshold tautology | MED | Easy | P3 |
| CF5 | Conceptual | Threshold tuning leakage | MED | Easy | P3 |
| SF4 | Statistical | Non-stationarity | MED | Easy | P3 |
| IF2 | Identifiability | Low-rank mode absorption | MED | Easy | P3 |
| DF6 | Dynamical | Module imbalance (protocol F6) | LOW | Easy | P4 |

Priority P0: must be resolved before any other work.
Priority P1: must be resolved before implementation.
Priority P2: must be measured and reported.
Priority P3: should be measured if time permits.
Priority P4: note and flag but may defer.
