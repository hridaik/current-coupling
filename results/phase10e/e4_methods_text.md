# Phase 10E.4 — Manuscript Methods Text
Date: 2026-06-15

---

## Draft Methods: Robustness Analyses

*[Note: This is a draft for integration into the Methods section or Supplementary Note.
Bracketed items indicate where specific values or citations should be confirmed.]*

---

### State-Specific Drift Correction

To assess the fixed-coupling assumption in the current formulation
(Ω_s = D_s Q_s + A, A constant), we fitted state-specific effective drift matrices
B_s by ridge regression of single-frame increments Δx(t) = B_s x(t) + ε(t)
separately within roaming and dwelling frames (ridge penalty λ = 277, selected by
leave-one-animal-out cross-validation). The coupling-corrected current was defined as
ΔΩ^B = ΔΩ_ss + (B_roam − B_dwell), which adds the differential effective drift
to the state-specific probability current difference. The relative Frobenius change
||ΔB||_F / ||B_roam||_F = 0.34 quantifies the degree of coupling state-dependence.
Key pair rankings were compared under ΔΩ_ss and ΔΩ^B to identify pairs whose rankings
are sensitive to the fixed-coupling assumption.

---

### Residualization Robustness Variants

The primary analysis uses CePNEM-residualized neural trajectories with anatomy-guided
graphical lasso (GL) precision estimation. Five preprocessing and estimator variants
were compared (Supplementary Table):
1. CePNEM + anatomy-guided GL (primary)
2. GCaMP + anatomy-guided GL (same estimator, raw calcium)
3. CePNEM + ridge precision (uniform penalty λ = 5% mean diagonal)
4. Velocity-regressed GCaMP + ridge precision
5. Raw GCaMP + ridge precision

The anatomy-guided GL estimator applies a 10× stiffer penalty on off-connectome
(Class-4) pairs (λ_off = 0.10) relative to on-connectome pairs (λ_on = 0.01),
encoding prior knowledge about connectivity. Rank changes across variants were
interpreted as reflecting (a) residualization effects and (b) estimator effects
(GL vs. ridge). The anatomy-guided GL is the pre-specified primary estimator; ridge
results are presented as conservative lower bounds.

---

### Animal Bootstrap and Leave-One-Animal-Out

Animal-level robustness was assessed using two protocols, both using ridge-regularized
precision (not anatomy-guided GL) for computational feasibility. This restriction means
these tests are conservative lower bounds on the primary estimator's stability, equivalent
to bootstrapping/LOAO of the CePNEM+Ridge variant (which ranks ADEL–URYVR 165th and
ADEL–URYDL 293rd), not the primary GL estimator.

**Bootstrap**: For each of 500 replicates, animals were sampled with replacement from
the 40-animal cohort; state-specific precision matrices Q_s^(b) were estimated by ridge
regression on the resampled data; pairs were ranked by |ΔΩ_ss^(b)| = |D_r^(b) Q_r^(b) −
D_d^(b) Q_d^(b)|. The fraction of replicates where each pair ranked in the top-20 was
recorded.

**Leave-one-animal-out (LOAO)**: Each of the 40 animals was excluded in turn; the
full CePNEM+Ridge analysis was repeated on the remaining 39 animals; pair ranks under
|ΔΩ_ss| were recorded. The most influential animal for each key pair was identified
as the one whose exclusion produced the largest rank change.

---

### Co-Observation Matched Null

To test whether high |ΔΩ_ss| rankings reflect differential co-observation support
rather than genuine coupling structure, we constructed a matched null separately for
each key pair. For each pair with co-observation count n_ij (number of animals where
both neurons were observed simultaneously), we identified all Class-4 pairs with
n_coobs within ±5 animals (stratum n ≈ 980–1090 pairs). The empirical percentile of
the key pair's |ΔΩ_ss| value within its matched stratum was recorded as the test
statistic; p-values are one-sided (probability of being as extreme or more extreme by
chance within the stratum). This test uses the primary CePNEM+anatomy-guided-GL values
directly and is unaffected by the ridge estimator caveat.

---

### Diffusion Specification and Shuffle Controls

**Specification comparison**: ΔΩ^(spec) was computed under five diffusion specifications:
identity (D_s = I, equivalent to ΔQ), pooled diagonal (single state mean), state-specific
diagonal (separate state means), pooled full matrix, and state-specific full matrix
(primary). Pair rankings were compared across specifications.

**Shuffle nulls**: Four null distributions were constructed from 500 permutations each:
(1) diagonal shuffle — neuron-specific diagonal entries shuffled randomly; (2) off-diagonal
shuffle — off-diagonal entries shuffled while preserving diagonal; (3) row/column permutation
— same permutation applied to both D_r and D_d (preserving spectral properties, breaking
neuron identity); (4) state-label swap — D_r and D_d swapped with each other. The p-value
for each null was defined as the fraction of permutations where the null rank equaled or
exceeded the primary rank for each pair.

**Hub control**: For each pair (i,j), hub score was defined as
sum_row_norm_roam = ||D_r[i,:]||_2 + ||D_r[j,:]||_2. Spearman correlation between hub
score and |ΔΩ_ss| was computed across all 1321 Class-4 pairs. Additionally, for each
key pair, a matched-hub null was constructed by identifying all Class-4 pairs with hub
score within ±20% (or ±0.05 absolute). The key pair's empirical percentile within its
hub-matched stratum was recorded.

---

### Diffusion/Precision Decomposition

ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell was decomposed into a precision-change term
and a diffusion-change term. Two state-conditioned decompositions were computed:

- Decomposition A: ΔΩ = D_roam @ ΔQ + ΔD @ Q_dwell
  (precision term = D_roam @ (Q_roam − Q_dwell); diffusion term = ΔD @ Q_dwell)

- Decomposition B: ΔΩ = D_dwell @ ΔQ + ΔD @ Q_roam
  (precision term = D_dwell @ ΔQ; diffusion term = ΔD @ Q_roam)

IMPORTANT: Neither decomposition is unique. Both are algebraically valid but represent
different choices of reference state. Fractions reported are from both forms; sign
agreement and dominance direction are robust across forms, while exact fractions vary
by ≤25 percentage points. The non-uniqueness is acknowledged and only sign consistency
and dominance direction (not exact fractions) are interpreted.

---

### Top-K Enrichment and FDR Correction

PDF annotation enrichment (Bentley ESconnectome, transmitter field containing "pdf")
in the top-K pairs ranked by |ΔΩ_ss| was assessed by one-sided Fisher exact test
(alternative: greater-than) at K ∈ {5, 10, 15, 20, 25, 30, 40, 50, 75, 100}.
The primary threshold K = 20 was pre-specified in Stage 2 prior to any analysis.
The K-sweep is a sensitivity analysis only; K was not changed post hoc.

Fisher p-values from the 70 annotation × K combinations (7 annotation sets × 10 K values)
were subjected to Benjamini–Hochberg (BH) FDR correction. Enrichment is described as
"FDR-controlled" only for combinations passing BH q < 0.05. The primary K = 20 test,
being pre-specified and single, is not subject to the K-sweep multiple-testing correction.

Degree-permutation p-values for the primary K=20 test were computed from 1000
permutations of the 1321 Class-4 pair labels, preserving annotation set size, to
control for annotation density effects.

---

### Reference Sensitivity Sweep

To confirm the "off-reference" classification of key pairs is not sensitive to connectome
source, we tested ten alternative reference definitions: Creamer 2023 chemical synapse
matrix at thresholds ≥1, ≥2, ≥3 synapses (any direction); Creamer 2023 gap junction
matrix (≥1); Creamer 2023 chemical or gap (≥1 in either); White 1986 chemical synapses
(≥1); White 1986 chemical + electrical (≥1); Witvliet 2020 adult chemical (≥1);
Creamer LDS effective coupling matrix (any non-zero weight); Creamer LDS (|weight| ≥ 0.05).
For each definition, the alternative Class-4 universe was constructed (off-reference AND
both neurons in the 56-neuron Creamer subspace) and key pair on/off-reference status was
recorded. The primary locked C4 universe (N = 1321 pairs from Phase 2) was not modified.
Alternative universes were used only for sensitivity assessment.

Note on RMEL–URYDL: This pair is ON-reference under Creamer chemical thr=1 (one directed
synapse RMEL→URYDL; count = 1) and under the LDS effective coupling (weight = 0.017).
At higher thresholds (≥2 synapses or |weight| ≥ 0.05) it is off-reference. This marginal
connectivity is disclosed wherever RMEL–URYDL results are reported.
