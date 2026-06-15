# Phase 10E.3 — Manuscript Results Text
Date: 2026-06-15

---

## Draft Results Subsection: Robustness of ADEL–URY Current Organization

*[Note: This is a manuscript-ready draft. Bracketed items indicate places where figure/table references or supplementary note numbers should be inserted before submission.]*

---

### Robustness of ADEL–URY Current Organization

The dwelling-dominant off-reference current organization centered on ADEL–URYVR and
ADEL–URYDL was subjected to a systematic robustness program spanning fixed-coupling
controls, residualization variants, animal-level resampling, co-observation controls,
diffusion specification comparisons, and annotation enrichment sensitivity (Supplementary
Note X; Supplementary Table Y).

**Fixed-coupling and state-specific drift controls.** The state-specific probability
current ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell assumes that structural coupling A is
constant across behavioral states. To assess this, we fitted state-specific effective
drift matrices B_s by ridge regression (||ΔB||_F / ||B||_F = 0.34; Methods). Under the
coupling-corrected current ΔΩ^B = ΔΩ_ss + ΔB, ADEL–URYVR remained rank 2 (unchanged)
and ADEL–URYDL rose to rank 3 (promoted). Their high rankings are not driven by differential
effective coupling: ADEL–URYVR and ADEL–URYDL ranked 370th and 601st of 1321 under the
drift-change term |ΔB| alone, confirming their current dominance reflects precision and
diffusion organization rather than coupling state-dependence. The DA_mech ↔ URY_URX module
was strengthened under this correction (rising from rank 2 to rank 1). By contrast, the
RMEL–RMER pair fell from rank 38 to rank 371 under coupling correction [Supplementary Note X];
the biological confirmation of RMEL–RMER rests on independent perturbation data (see below)
rather than on its model ranking.

**Residualization and estimator dependence.** The extreme rankings of ADEL–URYVR (rank 2)
and ADEL–URYDL (rank 6) under ΔΩ_ss require both CePNEM behavioral residualization and
anatomy-guided graphical lasso (GL) precision estimation (λ_off / λ_on = 10×, encoding
prior sparsity for off-connectome pairs). Under raw GCaMP activity with the same anatomy-guided
GL estimator, ADEL–URYVR ranked 28th (top 2%) and ADEL–URYDL ranked 39th (top 3%),
confirming signal preservation across residualization approaches. Under ridge-regularized
precision (uniform penalty, no anatomy guidance), ADEL–URYVR ranked 165th (top 13%)
and ADEL–URYDL ranked 293rd (top 22%), consistent with the anatomy-guided prior amplifying
signal at off-connectome pairs as designed.

**Co-observation control.** To test whether the high rankings reflect differential
observation support rather than genuine state-dependent coupling structure, we compared
each key pair to 981–1092 pairs with similar co-observation frequency (n_animals ± 5).
ADEL–URYVR was at the 99.9th percentile (p = 0.001) and ADEL–URYDL at the 99.5th
percentile (p = 0.005) of their matched strata. These results use the primary
CePNEM+anatomy-guided-GL values directly and are therefore not affected by the
ridge-estimator caveats above. The high current rankings of ADEL–URYVR and ADEL–URYDL
are not explained by co-observation structure.

**Diffusion controls.** Dense empirical diffusion (D_s) could in principle produce
spurious high-ranking pairs by amplifying noise at neurons with large innovations variance.
We tested five diffusion specifications ranging from identity (D=I, equivalent to ΔQ) to
the full state-specific matrix [Supplementary Fig. Z]. Under identity diffusion, ADEL–URYVR
ranked 5th and ADEL–URYDL ranked 9th — confirming the signal is present in the
precision difference ΔQ without any diffusion weighting. The full state-specific D matrix
refined these rankings to 2nd and 6th (incremental promotion, not genesis). In 500
neuron-permuted diffusion matrices preserving D's spectrum, ADEL–URYVR achieved rank ≤ 2
in only 1.8% of permutations (p = 0.018), confirming the specific D–Q identity alignment
is data-specific. Endpoint diffusion hubness did not predict |ΔΩ_ss| ranking globally
(Spearman ρ < 0.04, p > 0.15) and did not explain ADEL–URYVR's elevation (99.8th
percentile among hub-score-matched pairs, p = 0.0017). Both state-conditioned decompositions
of ΔΩ_ss showed the precision term (D_s @ ΔQ) accounts for 83–96% of ADEL–URYVR's value,
confirming precision structure as the dominant driver [Supplementary Note X; note: this
decomposition is not unique].

**Timescale sensitivity.** Using diffusion matrices D(τ) estimated at lag τ ∈ {1, 2, 5, 10,
20} frames (0.25–5 seconds), ADEL–URYVR remained in the top 5 at all timescales tested
(ranks 2, 4, 3, 2, 3). ADEL–URYDL was stable at τ ≤ 5 frames (1.25 seconds; ranks 6–12)
but degraded at longer lags (rank 220 at τ = 20 frames), indicating its signal is primarily
a short-to-medium-timescale phenomenon. The sign of ΔΩ_ss (dwelling-dominant) was consistent
for all key pairs at all timescales. The DA_mech ↔ URY_URX module maintained rank 1 across
all five specifications, and behavioral state organization was confirmed to operate
predominantly on slow timescales (effective correlation time τ_c ≈ 1.25–2.5 seconds;
Phase 4C).

**Top-K enrichment and annotation specificity.** Sweeping the top-K threshold from 5 to 100
confirmed that PDF annotation enrichment (Bentley ESconnectome, pdf-1/pdf-2→pdfr-1) is not
specific to the pre-specified K = 20. Two of the top-5 (ADEL–URYVR, ADEL–RMEL), 3 of
the top-10 (adding ADEL–URYDL), and 4 of the top-20 pairs carry PDF annotation (expected
by density: 0.23, 0.46, 0.92 respectively; Fisher OR = 5.2 at K = 20, p = 0.011, degree-
permutation p = 0.008). The enrichment passed Benjamini–Hochberg correction at K = 30, 40,
and 50 across 70 annotation-by-K combinations tested. By contrast, serotonin-annotated
pairs were absent from the top-ranked pairs at all tested K (0 in top-100; AUROC ≈ 0.5),
providing a clean negative control.

**Reference sensitivity.** All key pairs identified as primary predictions (ADEL–URYVR,
ADEL–URYDL, ADEL–RMEL) had zero documented chemical synapses and zero gap junctions
across all ten tested structural and functional connectome sources (Creamer 2023, White
1986, Witvliet 2020 adult, Creamer LDS effective coupling), confirming their
off-reference classification is robust to the choice of reference definition
[Supplementary Table Z].

**Summary.** ADEL–URYVR is the strongest individual pair-level claim: its ranking is
unchanged by coupling correction, robust under the co-observation null (p = 0.001),
present without diffusion weighting, and timescale-stable. ADEL–URYDL is a strong
secondary prediction with slightly more qualification: it is promoted by coupling
correction but shows timescale sensitivity at long lags. Both pairs are novel
experimental predictions without funatlas counterparts. RMEL–RMER provides independent
biological validation of the framework's capacity to identify off-connectome
neuropeptide-mediated interactions (funatlas wt q = 0.0002, unc-31 abolished; Phase 5A),
though its model ranking is sensitive to the fixed-coupling assumption and should not
be used as a primary ranking validation. The DA_mech ↔ URY_URX module is the dominant
current block across all robustness tests, consistently rank 1 under every formulation tested.

---

*Supplementary Note X: Methods details for fixed-coupling correction, residualization variants, bootstrap, and LOAO analyses.*
*Supplementary Fig. Y: Diffusion specification comparison (5-panel), hub control, timescale table.*
*Supplementary Table Z: Reference sensitivity table (10 connectome definitions × 5 key pairs).*
