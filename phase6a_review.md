# Phase 6A — Scientific Protocol Review

## Reviewer Stance

This review is adversarial. Every design choice is examined for hidden assumptions,
artificial performance advantages, and logical circularity. Vulnerabilities are recorded
and labeled, not resolved silently. Confidence levels are marked: **[HIGH]**, **[MED]**,
**[LOW]**. Speculative claims are labeled **[SPEC]**.

---

## LEAKAGE AUDIT (First-Class Deliverable)

### The central risk

The biggest threat to this validation is not simulation realism. It is **definitional
equivalence**: accidentally writing a ground-truth definition for Class C that is
mathematically the same expression the framework later estimates, applied to true
parameters instead of estimated ones.

If that happens, the benchmark reduces to a noise-tolerance test: at large N, the
framework trivially succeeds because it estimates what we said the ground truth is.
That tells us the estimator works, not that the framework's physical model is correct.

### Specific leakage scenarios identified

#### L1 — Definitional equivalence of C with ΔΩ [CRITICAL]

The protocol defines Class C as: "no direct coupling, state modulation required;
dependence disappears when state drive is removed." If this is operationalized as
"ΔΩ_true[i,j] is large" (where Ω is the precision matrix), and the framework estimates
ΔΩ̂ from data, then at infinite data ΔΩ̂ → ΔΩ_true and the framework achieves perfect
classification by construction. The test would be measuring estimation variance, not
conceptual validity.

**Status:** The current protocol is ambiguous on this point. The phrase "state modulation
induces reproducible conditional dependence" is not operationally distinguishable from
"ΔΩ[i,j] > threshold." This must be resolved before implementation.

**Required fix:** Ground truth for Class C must be derived exclusively from the
construction parameters (A, gain modulation operators, H2 connectivity topology), not
from any quantity computed from the Lyapunov equation or precision matrix. See
`phase6a_ground_truth_spec.md` for the exact specification.

#### L2 — State lesion used as both label criterion and validation test [CRITICAL]

The protocol uses the outcome of a virtual state lesion (suppressing z) as:
(a) the ground truth criterion for Class C ("dependence disappears when state drive removed"), and
(b) a mechanistic validation metric ("state sensitivity: change under state lesion").

This is logically circular. Using the same experimental manipulation to assign a label
and then to confirm that label teaches us nothing. If C is defined by state-lesion
sensitivity, and the framework detects C by finding state-lesion-sensitive pairs, then
the test is: does the framework agree with itself? That is a consistency check, not a
validation.

**Required fix:** Ground truth labels must be assigned from construction topology alone.
State lesion experiments can then serve as an independent validation of the ground truth
itself (confirming that constructively-labeled C pairs are indeed state-sensitive), but
must not be used in the labeling step.

#### L3 — Low-rank component of A creates ambiguous structural class [HIGH]

The recommended A = A_sparse + U·Vᵀ mixes sparse anatomical coupling with dense low-rank
population modes. If the framework recovers only sparse connectivity, edges with A_sparse[i,j] = 0
but (U·Vᵀ)[i,j] ≠ 0 will be classified as non-structural by the framework and structural
by a naïve ground truth definition. The framework will be penalized for a definitional
ambiguity, not a methodological failure.

**Required fix:** The ground truth spec must explicitly state whether the low-rank
component counts as "structural." Recommendation: it does not; U·Vᵀ entries are
treated as a separate background category excluded from the primary S/C/M/N evaluation,
or the low-rank and sparse components are evaluated separately.

#### L4 — H2 modulator topology not fully specified → C labels cannot be pre-computed [HIGH]

Class C links arise partly through paths passing through H2 global modulators. The exact
assignment of H2 neurons (which modules they project to, their outgoing targets in
observed neurons) determines which pairs of observed neurons qualify as C. If H2
topology is not specified before simulation, C labels cannot be pre-computed from
construction rules, and must be inferred from data — which re-introduces the circularity
the protocol is trying to avoid.

**Required fix:** Full specification of H2 connectivity (source counts, target module
mapping, projection sparsity) must be committed before any simulation occurs.

#### L5 — z parameters tuned to framework sensitivity [HIGH]

If the gain modulation amplitude, noise modulation strength, or state trajectory
statistics are chosen to produce C links that the framework is known to detect well
(e.g., near the framework's operating SNR), the benchmark is optimized for success
rather than falsification. This is subtle because it requires knowing the framework's
sensitivity, which may not be explicitly consulted — but it can happen implicitly through
parameter tweaking driven by intuition about what "looks reasonable."

**Required fix:** z parameters must be fixed from biological priors (neuromodulation
ranges in published literature) before any analysis. The benchmark must include at least
one low-modulation condition (z weak, near-null hypothesis) and one high-modulation
condition, specified in advance.

#### L6 — Module structure enables module-identity shortcuts [MED]

With four modules and between-module connection probability p=0.03, pairs from different
modules are overwhelmingly N or C, while pairs within the same module are primarily S or
H1-confounded. A classifier that uses only module membership as a feature would achieve
high accuracy on the easy cases (inter-module N pairs) without performing any current
estimation. If the benchmark evaluates only overall accuracy, this shortcut is invisible.

**Required fix:** Report classification performance separately for within-module and
between-module pairs. The critical test is the S↔C confusion within the non-null pairs.

#### L7 — No null hypothesis baseline specified [MED]

Without a baseline comparator (e.g., random classifier, Glasso precision graph, sparse
regression, module-membership classifier), any nonzero performance appears meaningful.
The framework could score 70% overall accuracy while a module-membership classifier
scores 68%, demonstrating near-zero incremental value.

**Required fix:** Specify at least three baselines before analysis: (1) random classifier
with class-frequency priors, (2) Glasso applied separately per state (detects S only,
expects zero C), (3) simple group-difference classifier (ΔΩ̂ threshold applied uniformly).

---

## 1. Modular Sparse Architecture

### Design

100 observed + 40 hidden = 140 neurons. Four equal modules M1–M4 of 25 observed neurons,
plus distributed hidden neurons. Intra-module p=0.15, inter-module p=0.03, plus 2–3
global low-rank modes.

### Strengths

- Realistic mesoscopic organization consistent with known circuit motifs in cortex,
  ganglia, and motor circuits
- Modular structure creates interpretable failure modes: within-module S detection vs.
  cross-module C detection are distinguishable
- Scale (140 neurons) permits exact Lyapunov computation of Σ while remaining
  interpretable
- Low-rank global modes simulate neuromodulatory broadcast without all-to-all anatomical
  coupling

### Weaknesses

**W1. Equal module sizes create artificial symmetry.**
Four equal 25-neuron modules ensure balanced class distributions within and between
modules. Unequal modules (e.g., 10, 20, 30, 40) would stress-test robustness to
imbalance, which is characteristic of real biological circuits.

**W2. Module boundary is a known feature the framework could exploit.**
A classifier that knows module membership — even without doing any current estimation —
can perform well. The four-way accuracy metric will not reveal this.

**W3. Between-module density p=0.03 creates many structural between-module edges.**
At p=0.03 across 75×75 between-module pairs, roughly 169 cross-module structural edges
exist per module pair. This is not "sparse" in the sense of being few — it means
structural cross-module links will be abundant. This may make S vs. C distinction harder
for cross-module pairs, which is good for challenge but should be explicitly stated.

**W4. Low-rank modes are ambiguously structural.**
As noted in the leakage audit (L3), the low-rank component is not anatomical coupling
in the usual sense. Its entries will appear non-zero in the precision matrix and could
be recovered as "structural" edges by the framework. The ground truth spec must resolve
whether these count as S.

### Could this artificially favor the framework?

**Yes, moderately.** Module membership is a strong confound that makes overall accuracy
an uninformative metric. A module-aware baseline must be computed and subtracted to
reveal the framework's incremental value. **[HIGH confidence]**

---

## 2. Hidden Neuron Design

### Design

Two classes: H1 (local interneurons, within-module, 40% of hidden neurons **[unspecified in protocol]**) and
H2 (global modulators driving multiple modules simultaneously). Total 40 hidden neurons.

### Strengths

- H1 neurons create realistic local confounding (pairs appear correlated when jointly
  driven by a local interneuron)
- H2 neurons are the primary mechanism generating cross-state, cross-module C links
- The H1/H2 distinction maps onto real biological circuit classes (local vs. projection
  modulatory neurons)

### Weaknesses

**W5. H1/H2 split is unspecified.**
The protocol does not state how many neurons are H1 vs. H2, which modules H2 projects
to, or the sparsity of H2's projections. This directly determines which observed pairs
qualify as C. Without this specification, C labels cannot be derived from construction
rules. **[CRITICAL gap]**

**W6. H2-mediated C links are distinct from recurrent-flow C links.**
A pair (i,j) connected through a common H2 input is a **hidden-common-cause** structure.
A pair (i,j) connected through a state-modulated recurrent loop is a **current-supported**
structure. These are conceptually distinct, may require different estimation methods, and
should be evaluated separately. The protocol conflates them.

**W7. "Current-supported" may not be the right term for H2-mediated correlations.**
The probability current between two neurons jointly driven by a common unobserved source
need not involve nonequilibrium circulation. H2 creates a confounding effect, not a
current-supported effect in the thermodynamic sense. If the framework's theory is
specifically about nonequilibrium probability current, H2-type correlations are a
different phenomenon and should be a separate test category.

**W8. H1 local interneurons may inflate apparent S links.**
An H1 neuron that drives two observed neurons in the same module will make them appear
coupled. The framework may classify this as a direct S edge when it is actually an
indirect H1-mediated path. This is a legitimate failure mode, but it is not about C
detection — it is about S over-detection.

### Could this artificially favor the framework?

**Ambiguous.** H2-mediated C links may be detectable by simple PCA (H2's signature
appears in the first PC of activity), which requires no current estimation. If the
framework uses covariance structure to detect C links, and H2 creates obvious covariance
signals, the framework may score well on H2-type C links without demonstrating current
estimation specifically. Separate evaluation of H2-type vs. flow-type C links is
required. **[MED confidence]**

---

## 3. Latent-State Mechanism

### Design

Continuous latent process z(t) modulating recurrent gain, input routing, and noise
injection. The coupling matrix A remains fixed throughout; only the dynamical regime
changes.

### Strengths

- Continuous z is more realistic than hard-switching discrete states
- Fixed A prevents trivially detectable edge appearance/disappearance
- State-dependent noise creates realistic heteroscedasticity
- z represents a neurobiologically grounded concept (arousal, neuromodulatory tone)

### Weaknesses

**W9. "State lesion" is underspecified.**
What does it mean to "suppress latent modulation z"? Setting z=0? Setting z=E[z]
(mean level)? Removing only variance of z while keeping mean? Each choice creates a
different expected state-lesion outcome and a different ground truth for C links. This
must be unambiguously defined before implementation.

**W10. Continuous z makes C labels threshold-dependent.**
All pairs have some state sensitivity for nonzero z amplitude. The boundary between C
(state-sensitive) and N (state-insensitive) requires a threshold on the magnitude of
state sensitivity. If this threshold is chosen post-hoc to match the framework's
operating point, the benchmark is tuned.

**W11. z modulating noise independently creates a separate C-inflation channel.**
When z changes noise injection (innovation variance), it changes Σ(z) even without
changing A. Changes in Σ change Ω(z) and Q(z). Pairs that appear C because of
noise-driven Σ changes are not "current-supported" in the sense of network flow — they
are "noise-modulated." The two effects must be separated or the noise modulation must
be removed from the design. **[MED confidence, SPEC on severity]**

**W12. Multi-dimensional z creates interaction effects.**
If z = (z₁, z₂) with z₁ modulating gain and z₂ modulating noise, the full state lesion
removes both effects simultaneously. Partial lesions (remove z₁ only) may reveal
different C sets than full lesions. The protocol does not specify the dimensionality of
z or how partial vs. full lesions are handled.

**W13. z parameters are likely tuned toward detectability.**
Without explicit constraints, z parameters will be chosen at magnitudes that create
"interesting" or "visible" state differences. This implicitly selects for the
framework's operating range. **[SPEC]**

### Could this artificially favor the framework?

**Yes, substantially, if z is tuned.** The state effect needs to be parameterized from
biological priors and evaluated across a range. A near-null z condition (where C links
are just barely present) must be included to assess the framework's sensitivity
threshold. **[HIGH confidence]**

---

## 4. Diffusion / Noise Model

### Design

State-dependent diagonal base diffusion D_diag(z) plus weak low-rank correlated
innovation term D_lr. Full: D(z) = D_diag(z) + D_lr.

### Strengths

- Neuron-specific noise amplitudes match known single-cell variability
- Low-rank correlated noise realistically models common-input drive
- State-dependent variance creates realistic non-stationarity

### Weaknesses

**W14. Low-rank noise and low-rank A are structurally confounded.**
The model contains two low-rank components: A's low-rank global modes (UV^T) and D's
shared noise component (D_lr). From observed activity alone, these cannot be separated:
the covariance Σ satisfying AΣ + ΣA^T + D = 0 contains contributions from both. If the
low-rank components are aligned (share eigenvectors), the framework faces a nearly
unidentifiable problem. If they are orthogonal (which random generation approximately
ensures), the problem is easier. The protocol should verify this alignment explicitly
and report it. **[HIGH confidence]**

**W15. D(z) changes contaminate precision-matrix-based C detection.**
When D changes with state, the state difference ΔΩ = Ω(z₁) − Ω(z₂) reflects both
the change in D and the change in effective network dynamics. The framework presumably
cannot disentangle these without knowing D. If D(z) is the dominant source of ΔΩ, the
framework may correctly detect state-sensitive pairs but misattribute them to current
flow rather than noise modulation. This is not a classification error (pairs that are
C-labeled may still be detected) but it is a mechanistic misinterpretation. **[MED]**

**W16. The boundary between "state-dependent diagonal" and "fully state-dependent dense"
D is not quantified.**
The protocol rejects fully state-dependent dense D as "blurring attribution between
current and coupling." The recommended partial D(z) also blurs this attribution, just
less severely. The maximum allowable state sensitivity of D(z) needs to be stated
explicitly.

### Could this artificially favor the framework?

**Yes, if D and A's low-rank components are orthogonal by design.**
If D_lr is constructed to be orthogonal to UV^T (both in eigenvector space), the
separation between noise-induced and coupling-induced covariance is artificially easy.
The protocol should either use random independent generation (which approximately
achieves this) and document the resulting alignment, or actively test robustness to
aligned components. **[MED confidence]**

---

## 5. Observation Model

### Design

Neural state → firing rate nonlinearity f(·) → calcium dynamics (convolution with kernel
κ) → additive measurement noise → 70–80% subsampling of observed neurons.

### Strengths

- Realistic to two-photon calcium imaging, the dominant modality in systems neuroscience
- Nonlinearity and temporal blurring create a genuine inference challenge
- Partial observation (20–30% hidden) introduces realistic hidden variable confounding

### Weaknesses

**W17. Firing rate nonlinearity breaks the linear framework assumption.**
If the current-velocity framework is designed for linear Gaussian dynamics, the firing
rate nonlinearity f(·) violates this assumption. Framework failure due to nonlinearity
is a different failure mode than failure to distinguish S from C. These must be
separated in the analysis: first test the framework on the unobserved neural state (no
observation model), then on calcium observations.

**W18. Calcium convolution introduces temporal autocorrelation.**
Calcium dynamics (rise ~100ms, decay ~500ms–1s) introduce temporal autocorrelation
beyond that generated by network dynamics. If the framework uses covariance estimates
without deconvolution, temporal blurring inflates off-diagonal covariances. This is a
confound for S detection (pairs appear coupled at long lags) and for C detection (state
differences may be smoothed out).

**W19. Subsampling fraction may be too generous.**
At 70–80% observed, 28–32 neurons remain hidden. Real experimental conditions typically
observe 10–30% of neurons in a local volume. The hidden variable challenge at 70–80%
may be unrealistically easy.

**W20. Subsampling scheme is unspecified.**
Random uniform subsampling vs. structured subsampling (e.g., all H2 neurons hidden,
or one full module hidden) creates very different hidden variable challenges. This must
be specified and fixed before simulation.

### Could this artificially favor the framework?

**Yes, if the framework models calcium dynamics explicitly.** If the framework was
designed for calcium-like observations, the benchmark is tailored to its strengths
rather than testing general robustness. Evaluating the framework on the latent neural
state (before the observation pipeline) should be included as a reference condition.
**[MED confidence]**

---

## 6. Link Taxonomy (S, C, M, N)

### Design

Four mutually exclusive classes defined by:
- S: direct coupling in A exists, state manipulation has negligible effect
- C: no direct coupling, state modulation required
- M: direct coupling exists, state modulation alters magnitude
- N: no coupling, no state dependence

### Strengths

- Directly tests the framework's theoretical claims
- Four-way distinction separates anatomical from functional connectivity
- Lesion definitions provide operational handles

### Weaknesses

**W21. "Negligible effect" for Class S is undefined.**
No threshold separates S (state manipulation has negligible effect) from M (state
modulation alters magnitude). Without a pre-specified threshold, the S/M boundary
is arbitrary. Every direct edge (A[i,j] ≠ 0) will show *some* state sensitivity in a
modulated network. The S/M distinction is a matter of degree, not kind.

**W22. True N pairs may be rare or empty.**
With a low-rank component in A, almost every pair of neurons has some indirect
structural path. Near-zero indirect paths (very long, heavily attenuated) may produce
nonzero but undetectable correlations. The N class may be defined by "undetectable
effect" rather than "zero effect," making N labels operationally noisy.

**W23. Class M identification requires quantitative decomposition of a single edge.**
For a pair (i,j) with A[i,j] ≠ 0, separating the "structural contribution" from the
"state-modulated contribution" requires knowing both A[i,j] and the state-sensitive
pathway strength. This decomposition is not trivial and the protocol does not specify
how it is accomplished during ground truth labeling.

**W24. H1/H2-mediated indirect paths are not addressed in the taxonomy.**
The taxonomy does not explicitly handle pairs where: A[i,j] = 0, but H1 or H2 creates
a persistent (state-independent) indirect path. Such pairs would be classified as N
(no state dependence) but may show substantial indirect correlation. These are important
confounders for S detection that fall between C and N.

### Could this artificially favor the framework?

**Yes, if thresholds for "negligible" and "no dependence" are chosen to match framework
sensitivity.** If we set the S/M threshold to the framework's detection boundary, the
framework's M-detection rate will appear high. Thresholds must be set from biological
priors (e.g., a 10% change in effective coupling counts as "negligible"), locked in
advance, and reported alongside results. **[HIGH confidence]**

---

## 7. Validation Metrics

### Design

Primary: four-way edge classification accuracy.
Secondary: precision/recall per class, AUROC one-vs-rest, S↔C confusion matrix,
calibration. Mechanistic: off-structure enrichment, state sensitivity, structural
sensitivity, mixed-link identification.

### Strengths

- Multi-metric approach reduces Goodhart's Law risk
- S↔C confusion matrix directly targets the primary scientific hypothesis
- Calibration tests whether confidence scores are meaningful
- Mechanistic metrics provide diagnostic information

### Weaknesses

**W25. AUROC with heavy N-class dominance is misleading.**
With ~9900 directed observed-pair, roughly 150–300 structural edges, and potentially
100–200 C links, the N class comprises >90% of pairs. AUROC one-vs-rest for N will be
near 1.0 trivially. The informative metric is S-vs-C AUROC or the C-detection precision
in the non-null subset. This must be reported separately.

**W26. State sensitivity as a mechanistic validation metric is circular with L2.**
If ground truth C is defined partly by state sensitivity and the mechanistic validation
confirms C links are state-sensitive, the test is tautological. Mechanistic validation
metrics must be independent of the label-assignment criterion.

**W27. Off-structure enrichment conflates different types of non-structural pairs.**
"Fraction of detected C links lacking direct coupling" includes H2-mediated confounds,
recurrent-flow C links, and near-null pairs alike. This metric needs to be stratified
by the type of non-structural pair.

**W28. No comparison to baselines that do not use current estimation.**
The framework may outperform chance but underperform a simple baseline (e.g., a partial
correlation threshold or a Glasso precision graph). Without this comparison, it is
impossible to assess whether current estimation adds value beyond conventional methods.

### Recommended additional metrics

1. **S-vs-C subclassification accuracy**: Computed only over non-null pairs (true S + C + M).
   This eliminates the trivial N-majority inflation.
2. **Incremental improvement over Glasso baseline**: Fraction of C links recovered by the
   framework that are *not* recovered by Glasso on per-state data.
3. **Calibration under class imbalance**: Expected calibration error corrected for N-class
   dominance.
4. **Module-blind confusion matrix**: Compute separately for within-module and between-module
   pairs.

### Could this artificially favor the framework?

**Yes, through N-class inflation of aggregate metrics.** Any method that correctly
classifies N pairs (the vast majority) will appear to perform well on four-way accuracy.
Precision on C and recall on C, computed separately, are the scientifically relevant
metrics. **[HIGH confidence]**

---

## Summary of Critical Vulnerabilities

| ID | Vulnerability | Severity | Document |
|----|---------------|----------|---------|
| L1 | Definitional equivalence of C with ΔΩ | CRITICAL | GT spec |
| L2 | State lesion used for labeling AND validation | CRITICAL | Validation plan |
| L3 | Low-rank A component ambiguously structural | HIGH | GT spec |
| L4 | H2 topology unspecified; C labels underdetermined | HIGH | Protocol revision |
| L5 | z parameters potentially tuned to detectability | HIGH | Protocol revision |
| L6 | Module structure enables module-identity shortcuts | MED | Metrics |
| L7 | No baseline comparator specified | MED | Validation plan |
| W21 | S/M threshold undefined | MED | GT spec |
| W17 | Nonlinear observation conflated with S/C failure | MED | Validation plan |
| W14 | D and A low-rank components confounded | MED | Protocol revision |
| W11 | Noise modulation vs. current modulation conflated | MED | GT spec |
| W25 | AUROC inflated by N-class dominance | MED | Metrics |
| W19 | Observation fraction unrealistically generous | LOW | Protocol revision |

---

## Overall Assessment

The protocol is well-conceived and substantially more rigorous than prior phases. The
modular sparse architecture, hidden neuron design, and continuous state mechanism are
all scientifically defensible.

The critical unresolved issue is leakage vulnerabilities L1 and L2: the ground truth
definition for Class C is not yet sufficiently separated from the framework's own
quantities. Resolving this is the single most important task before implementation.

Secondary priorities: fix H2 topology specification (L4), lock z parameters from
biological priors (L5), and add module-aware baselines (L6, L7).

The framework can be proven wrong by this benchmark if and only if:
1. Ground truth labels are derived from construction topology, not from estimated statistics
2. z parameters are fixed in advance from priors, not tuned
3. Baselines are included that test non-current explanations
4. Metrics separate the trivial N-majority from the informative S/C distinction

These four conditions are currently not guaranteed. They must be guaranteed before
Phase 6B implementation begins.
