# Phase 6B — Readiness Assessment

## Purpose

This document answers the five exit criterion questions from the Phase 6B brief, ranks
all remaining unresolved risks, and makes a binary go/no-go recommendation for Phase 7
implementation.

---

## Exit Criterion Evaluations

### Q1 — Is the simulator fully specified?

**Answer: YES.**

Every component is exact and complete:

| Component | Status |
|---|---|
| Neuron counts and indices | Exact: 100 obs, 32 H1, 8 H2, 140 total |
| Module assignments | Exact: 4 modules of 25 each, indices listed |
| H2 target module assignments | Exact: 8 H2 neurons with specific module pairs |
| Coupling matrix A | Exact: sparsity probabilities, weight distributions, self-inhibition |
| State process z(t) | Exact: OU, θ_z=0.10, σ_z=1.0 |
| z→H2 drive | Exact: B_h(z) = 3.0 × z for all h ∈ SA |
| Diffusion D | Exact: d_0=1.0 diagonal + 0.1×uuᵀ rank-1 component |
| Observation model | Exact: softplus, κ_ca=0.50, σ_obs=0.10 |
| Integration | Exact: Euler-Maruyama, dt=0.10, T=50,000, R=5 |
| Random seeds | Exact: master seed 42, sub-seeds defined per component |
| Stability check | Specified: spectral abscissa < -0.1 required |
| Warm-up | Exact: discard first 2,000 steps |

An independent engineer can implement the simulator solely from `phase6b_architecture_spec.md`
and `phase6b_parameter_registry.md` without making any scientific decision.

**Confidence: HIGH.**

---

### Q2 — Can labels be generated without simulation?

**Answer: YES.**

The label generation algorithm in `phase6b_label_generation_spec.md` requires only:

1. The sparsity pattern of A_sparse (which entries are nonzero) — deterministic from
   seed 42 and the connectivity probabilities p_within, p_between, p_H1_in, p_H1_out,
   p_H2_in, p_H2_out.
2. The SA set = {133,...,140} — known from construction, never changes.
3. The DIRECT(i→j) indicator — read directly from A_sparse[j,i] ≠ 0.
4. The SAREACHABLE(i→j) indicator — O(N² × |SA|) lookup over A_sparse, no simulation.

Time to compute all 9,900 labels from A_sparse: milliseconds.
No trajectory, covariance, precision matrix, or framework output is consulted.

**Confidence: HIGH.**

---

### Q3 — Is leakage eliminated?

**Answer: YES, for the primary label categories. One residual note applies.**

**Critical leakage L1 (definitional equivalence of C with ΔΩ): RESOLVED.**

The SAREACHABLE criterion is defined in terms of the binary sparsity pattern of A_sparse
and the H2 identity set SA. It does not reference Ω, Q, ΔΩ, or any quantity in the
framework's estimating family. As proven in the leakage audit (label generation spec,
Section "Leakage Audit"), SAREACHABLE is not equivalent to "ΔΩ[i,j] is large":
- Two pairs can have identical ΔΩ but different SAREACHABLE values (one has the required H2 path, one does not).
- Two pairs can both be SAREACHABLE with different ΔΩ values (depending on weight magnitudes).
- A pair can be SAREACHABLE with near-zero ΔΩ (if H2 weights are near zero).

**Critical leakage L2 (state lesion used for both labeling and validation): RESOLVED.**

Labels are assigned from the sparsity pattern only. The state lesion experiment (virtual
suppression of z) is now only a post-hoc sanity check (Check LG in label generation
spec), not a labeling criterion. The sanity check does not modify labels.

**Critical leakage L3 (low-rank A ambiguity): RESOLVED by elimination.**

A_lr = 0 in the primary benchmark. No LR class exists. The ambiguity is removed.

**Critical leakage L4 (H2 topology underspecified): RESOLVED.**

H2 topology is completely specified: 8 H2 neurons, exact target module assignments,
exact connectivity probabilities p_H2_in = 0.20 and p_H2_out = 0.20.

**Residual note on weight magnitudes (MINOR, not P0):**

The SAREACHABLE criterion is binary — it depends on A_sparse[h,i] ≠ 0, not on the
magnitude of A_sparse[h,i]. A pair can be SAREACHABLE with a very small H2 weight
(e.g., drawn near zero from N(0, 0.35²)), giving a true C label but a near-undetectable
signal. This does not constitute leakage (the label is correct — the H2 path exists),
but it creates finite-SNR C labels that the framework may miss.

This is an expected feature of a realistic benchmark, not a flaw. The framework failing
to detect C links with very small H2 weights is a genuine framework limitation, not a
label error.

**Confidence: HIGH for L1–L4. LOW residual risk from near-zero H2 weights (P2 risk).**

---

### Q4 — Is circular validation eliminated?

**Answer: YES.**

The Phase 6A review identified two circularity risks (L2 and a secondary mechanistic
validation circularity, W25/W26). Both are resolved:

**L2 (state lesion circularity): RESOLVED.**
Labels come from A_sparse topology only. State lesion outcomes are post-hoc sanity
checks, not inputs to labeling.

**Mechanistic validation circularity (W25/W26 from Phase 6A review):**
The "state sensitivity" mechanistic metric is now an independent check rather than a
circular confirmation:
- Ground truth C is defined: A_sparse[j,i]=0 AND SAREACHABLE (topology)
- State sensitivity of the framework's output is an observed quantity: does the framework's
  score for (i,j) change between high-z and low-z conditions?
- These are independent: topology (ground truth) and score-change (framework output).
  The test is whether the framework's state sensitivity aligns with the topological C label,
  which is a genuine scientific test, not a tautology.

**Module-shortcut circularity (CF3 from Phase 6A failure modes):**
Three pre-registered baselines (random, module-membership, Glasso) are computed before
any framework output is evaluated. The module classifier baseline will reveal the
performance floor attributable to module structure alone.

**Confidence: HIGH.**

---

### Q5 — Can an independent implementation proceed?

**Answer: YES, with one recommended verification step.**

The specification documents provide:
1. Exact neuron counts and index ranges
2. Exact connectivity probabilities and weight distributions
3. Exact dynamics equations (Euler-Maruyama SDE)
4. Exact observation model (softplus, calcium filter, noise)
5. Exact label generation algorithm (pseudocode provided)
6. Exact seeds and sub-seed assignments
7. Verification checks at each stage (stability check, label sanity checks)

**Recommended verification step before running R=5 full simulations:**

Run a single 5,000-step pilot (not used for evaluation) and verify:
- Spectral abscissa of A_sparse < -0.1
- Label counts |C| ≥ 20, |S| ≥ 20, |M| ≥ 5
- z process has empirical variance ≈ σ_z²/(2θ_z) = 5.0 (within ±30%)
- Calcium traces y(t) have finite variance and no NaN/Inf values

This takes ~1 minute of compute time and confirms the implementation is correct before
committing to the full R=5 runs.

**Confidence: HIGH.**

---

## Remaining Risks

### P0 — Risks that block implementation

**None.** All P0 risks from Phase 6A (L1, L2, L3, L4, stability, SNR) have been
addressed. The specification is complete and internally consistent.

---

### P1 — Risks requiring monitoring during implementation

**Risk P1-A: Near-zero H2 weights create undetectable C links**

Mechanism: some SAREACHABLE pairs will have very small H2 weights (drawn from
N(0,0.35²), the tail near zero). These pairs are correctly labeled C but may have
ΔΩ ≈ 0, making them invisible to any method. If many C-labeled pairs fall in this
category, C-recall will be low even for a perfect framework.

Detection: after label generation, compute the distribution of effective H2 path
strength for all C-labeled pairs: strength(i→j) = max_{h: witness} |A[h,i]| × |A[j,h]|.
Report the fraction of C pairs with strength < 0.01 (effectively undetectable).

Mitigation: if more than 20% of C pairs have strength < 0.01, consider imposing a
minimum weight floor (e.g., resample H2 weights until |A[h,i]| > 0.05 for all
edges incident to H2) or increasing σ_H2_out. This must be pre-registered as a
construction-stage filter, not a post-hoc label change.

**Risk P1-B: Stability check requires resampling**

Mechanism: random weight draws may occasionally produce A_sparse with spectral
abscissa ≥ -0.1. The protocol specifies resampling up to 10 times; if 10 resamples
are needed, reduce σ values by 10%.

Detection: record number of resamples at construction time.

Mitigation: the resampling protocol is already specified. If σ reduction is needed,
document it and verify C-link SNR is still ≥ 1 (recompute expected SNR with reduced σ).

**Risk P1-C: Class imbalance more extreme than expected**

Mechanism: random seed 42 may produce an A_sparse with fewer-than-expected C or S links
due to realization variance. The expected counts (C≈691, S≈518) have standard deviation
roughly sqrt(n × p × (1-p)); for C, SD ≈ sqrt(9900 × 0.07 × 0.93) ≈ 25. A 3-sigma
shortfall could give |C| ≈ 616, still above the minimum threshold of 20.

Detection: check LG1 verifies |C| ≥ 20 and |S| ≥ 20.

Mitigation: LG1 specifies resampling with seed + 1000 if minimum thresholds are violated.

---

### P2 — Risks to monitor and report but that do not block implementation

**Risk P2-A: H1 interneurons create false-S detections**

H1 neurons create correlated activity between within-module observed pairs (both driven
by shared H1 input). The precision matrix Ω will have nonzero entries for such pairs
even when A_sparse_oo[i,j] = 0 and SAREACHABLE = False (N-labeled). The framework may
classify these as S.

This is expected behavior documented in failure mode DF3 (Phase 6A). It is not a label
error — these pairs are correctly N-labeled, and the framework's misclassification is
a known limitation. Report the false-S rate stratified by H1-proximity.

**Risk P2-B: Low-rank D component creates apparent coupling**

D_lr = 0.1 × u × uᵀ creates weak correlated noise across all neurons. With
||D_lr||_F / ||D_diag||_F ≈ 0.0085, this is very small. However, for pairs (i,j) where
u_i and u_j are large (i.e., i and j are in the "active" direction of D_lr), the
apparent correlation may be detectable. Report the correlation between D_lr[i,j] and
false-positive detections.

**Risk P2-C: Calcium observation model breaks framework assumptions**

If the framework assumes linear Gaussian dynamics and the softplus nonlinearity +
calcium filter violates this, the framework may fail for reasons unrelated to S/C
classification. The `neural_state` evaluation condition (which bypasses the observation
model) isolates this contribution. If performance in `neural_state` >> `oracle_z`,
the observation model is a major source of error.

**Risk P2-D: Euler-Maruyama discretization error**

At dt=0.10 and self-inhibition -1.5, the discrete-time stability factor is
(1 + A[k,k] × dt) = (1 - 0.15) = 0.85. This is stable, but coupling terms may
introduce discrete-time resonances not present in the continuous system. Reducing dt
to 0.05 in a verification run and confirming outputs are similar mitigates this risk.

---

## Go / No-Go Recommendation

**RECOMMENDATION: GO.**

All five exit criteria are satisfied:
1. Simulator is fully specified ✓
2. Labels are generatable without simulation ✓
3. Leakage is eliminated at the level required for a valid benchmark ✓
4. Circular validation is eliminated ✓
5. Independent implementation can proceed ✓

No P0 risks remain.

P1 risks have specified monitoring and mitigation procedures. P1-A (near-zero H2 weights)
is the highest priority and should be checked immediately after A_sparse construction,
before committing the full simulation run.

**Recommended first action in Phase 7**:

1. Implement the network construction (A_sparse generation, stability check, D)
2. Run label generation and verification (LG1–LG4 sanity checks)
3. Check P1-A: compute H2 path strength distribution for C-labeled pairs
4. If P1-A passes: commit labels (hash lock, Step 3 of pre-registration protocol)
5. If P1-A fails: apply minimum weight floor, re-generate labels, re-hash
6. Implement dynamics and observation pipeline
7. Run 5,000-step verification pilot (not used for evaluation)
8. Run R=5 full simulations per condition
9. Apply framework; save outputs
10. Reveal labels, verify hash, compute metrics

The benchmark is scientifically valid and implementation-ready.
