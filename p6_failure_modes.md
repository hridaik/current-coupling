# Phase 9A.6 — Failure Modes

## Purpose

Define what success, partial success, and failure look like for the benchmark, with
biologically interpretable criteria. Each outcome is linked to a mechanism.

---

## Outcome A: Framework Succeeds

### Criteria (all three must hold)

```
PMC_AUROC ≥ 0.75    AND
Precision@50 ≥ 0.25 AND
Rank correlation ρ ≥ 0.40
```

### What this means

The framework correctly identifies the planted off-connectome organization. The PMC
circuit is enriched among the framework's top-ranked off-connectome pairs at a rate
substantially above both random (0.87% density → ~0.87% Precision@50) and the
correlation-change baseline (B2).

### Biological interpretation

The framework can recover state-dependent circuit organization of the kind observed in:
- The OU cascade (correct identification of the 6–8 off-local link at high α)
- The leech (correct identification of the 55–56 current-supported ganglion pairs at
  nominal gain)
- The worm (PDF-receptor circuit enriched at AUROC = 0.664)

A framework that succeeds here would, applied to the real worm data, be expected to
recover the PDF-receptor circuit from the ΔΩ organization.

### Mechanism for success

The framework must:
1. Correctly estimate the state difference ΔΩ (or ΔQ as an approximation)
2. Not suppress the z-mediated signal before computing conditional dependence
3. Correctly identify that PMC source-target pairs have larger ΔΩ than non-PMC
   off-connectome pairs

---

## Outcome B: Framework Partially Succeeds

### Criteria

At least one primary metric meets partial threshold but not full success:

```
PMC_AUROC ≥ 0.60   OR
Precision@50 ≥ 0.10 OR
Rank correlation ρ ≥ 0.15
```

with at least one metric below the full success threshold.

### What this means

The framework recovers some of the planted organization but not all. This might arise from:

### B1. Signal attenuation by z-regression
The framework removes z-correlated variance from neural activity before computing
conditional dependence. This is the failure mode identified in Phase 8D (state-sensitive
C pairs received the LOWEST C-scores). In the new benchmark, PMC pairs would receive
slightly-above-chance rankings because some z-mediated correlation survives the
regression step, but the enrichment is weak.

**Biological interpretation:** The framework partially detects the current-supported
organization but attenuates the very signal it should amplify. Like identifying only
the weakest connections in the PDF-receptor circuit while missing the ADEL-URY coupling.

### B2. Hidden-variable confounding
The H_global relay that creates PMC organization also drives non-PMC neurons in M1, M2,
M3, M4 weakly. The framework may pick up diffuse H_global signatures throughout the
off-connectome matrix rather than concentrating on PMC pairs. Precision@50 would be
above random but below 0.25.

**Biological interpretation:** The framework identifies that "many neurons co-vary with
the state" but does not isolate the specific functional circuit. Like finding neuropeptide
enrichment across the broad Class 4 pool (AUROC = 0.664 in the worm) without identifying
the specific PDF-receptor circuit.

### B3. Module structure recovered but not pairs
NMI_module meets the success threshold (≥ 0.40) but Precision@50 does not. The framework
correctly identifies that PMC sources cluster together and PMC targets cluster together,
but within each cluster the pair-level ranking is noisy.

**Biological interpretation:** The framework identifies the correct circuit modules
(equivalent to knowing "food-sensing and gas-sensing circuits co-organize during dwelling")
but cannot specify which pairs are the dominant links (equivalent to not knowing that
ADEL→URYVR is the strongest link).

---

## Outcome C: Framework Fails

### Criteria

All primary metrics below partial threshold:

```
PMC_AUROC < 0.55   AND
Precision@50 < 0.05 AND
Rank correlation ρ < 0.10
```

### What this means

The framework cannot recover the planted organization at above-random levels. This
is the full failure scenario — equivalent to Phase 8B's verdict of FAILURE on C-AUROC.

### Mechanism sub-types for failure

#### C1: Z-regression destroys signal (same failure as Phase 8B)
The framework's preprocessing removes the z-correlated signal from the neural activity
before computing conditional dependence. PMC pairs, which are specifically marked by
z-mediated correlation in State A, are rendered indistinguishable from non-PMC pairs
after z-regression.

**Signature:** PMC_AUROC < 0.50 (anti-informative ranking). PMC pairs receive LOWER
framework scores than non-PMC off-connectome pairs. The ranking is inverted.

**What to check:** Does the framework include any step that regresses state information
out of the neural traces before computing covariance? If yes, this failure is expected
and has a clear architectural fix (use z as an instrument, not a nuisance covariate).

#### C2: Precision estimation noise dominates signal
With N_obs = 150 neurons and finite time series, the 150×150 precision matrix estimation
is noisy. The estimated ΔΩ at the off-connectome entries is dominated by estimation
variance rather than the true ΔΩ_true signal.

**Signature:** ρ_rank ≈ 0 (no correlation between estimated and oracle rankings).
PMC_AUROC ≈ 0.50 (not anti-informative, just random). S-class detection may still work
(structural links are strong and many), but the off-connectome PMC signal is below the
noise floor.

**Biological interpretation:** The framework is operating below the signal-to-noise
threshold for off-connectome organization recovery at this scale. The same framework
would fail on the real worm data at 150 neurons.

#### C3: Framework recovers structural pairs only
The framework correctly identifies structural pairs (S_AUROC high) but cannot detect
PMC organization (PMC_AUROC ≈ 0.50 or below).

**Signature:** S_AUROC ≥ 0.75, PMC_AUROC < 0.55. This is exactly the Phase 8B failure
pattern: the framework detects structure but not current-supported organization.

**Biological interpretation:** The framework measures what anatomy predicts it should
measure (the structural coupling A). It does not add information about the dynamical
organization that exists OFF the anatomical structure.

---

## Outcome D: Benchmark Invalid

This outcome applies to the benchmark itself, not the framework. The benchmark is
invalid if the dominance condition D1 fails:

```
Dominance condition D1: Median |ΔΩ_true| for PMC pairs ≤ 2 × 90th percentile |ΔΩ_true|
                        for non-PMC off-connectome pairs
```

If D1 fails, the planted signal is too weak to detect even with the oracle. The benchmark
must be redesigned (increase z_high or redesign H_global connectivity) before any
framework evaluation occurs.

**How to check D1:** Verify analytically from the Lyapunov solution. This is a
pre-implementation check. If D1 fails, the parameter z_high is increased until it holds.
The final z_high is reported as a benchmark parameter.

---

## Biological Interpretability of Each Outcome

| Outcome | PMC_AUROC | Biological meaning |
|---|---|---|
| A (Success) | ≥ 0.75 | Framework recovers PDF-circuit-scale organization in a controlled system |
| B1 (Partial: attenuation) | 0.55–0.74 | Framework detects organization but suppresses state signal |
| B2 (Partial: diffuse) | 0.55–0.74 | Framework detects state activity but not focused circuit |
| B3 (Module success only) | < 0.55 | Framework finds correct groups but not pair-level links |
| C1 (Anti-informative) | < 0.50 | Same architectural failure as Phase 8B; z-regression inverts signal |
| C2 (Noise floor) | ≈ 0.50 | Estimation noise dominates at this scale |
| C3 (Structure only) | ≈ 0.50 | Framework is a structural connectivity detector, not an organization detector |
| D (Invalid benchmark) | N/A | Planted signal too weak; redesign required |

---

## What Outcomes A–C Do NOT Mean

**Outcome A does not mean:**
The framework's theory is correct. It means the framework correctly recovers the
planted organization in a synthetic system. Real-data validation requires applying
the framework to C. elegans recordings with the same quality of ground truth.

**Outcome C does not mean:**
Current-supported organization does not exist in biology. It means the specific
framework implementation fails to recover the planted organization. A different
framework implementation (e.g., one that uses z as an instrument rather than a
nuisance covariate) might succeed.

**Outcome B does not mean:**
The framework is partially right. It means the framework has partial sensitivity to
the organization. The mechanism of partial sensitivity must be diagnosed (B1, B2, or B3)
to determine whether it can be fixed by architectural changes.

---

## Diagnostic Checklist for Each Failure Mode

Upon observing an outcome, the following diagnostics are run:

### If C1 is suspected (anti-informative ranking):
1. Check ρ(PMC-score, |ΔCorr_AB|). If ρ < 0, the framework is inverting the state signal.
2. Check what preprocessing step precedes covariance estimation.
3. Compute PMC_AUROC using only the framework's state-averaged output (no ΔΩ computation);
   if this is above 0.55, the z-regression step is the failure point.

### If C2 is suspected (noise floor):
1. Compute rank correlation ρ using the oracle ΔΩ_true as input. If ρ → 1 (it should),
   the oracle works and the failure is estimation.
2. Increase T (trajectory length) by 4× and recheck PMC_AUROC. If it improves to ≥ 0.60,
   the failure is finite-sample, not architectural.

### If C3 is suspected (structure only):
1. Verify S_AUROC ≥ 0.75 (structural detection is working).
2. Verify PMC_AUROC < 0.55 (off-connectome detection is failing).
3. Check whether the framework's off-connectome scores are positively or negatively
   correlated with |ΔΩ_true|. If ρ ≈ 0, the off-connectome score is uninformative.
   If ρ < 0, the framework is systematically wrong.
