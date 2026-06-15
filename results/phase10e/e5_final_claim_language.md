# Phase 10E.5 — Final Worm Claim Language
Date: 2026-06-15

---

## Three Versions of the Main Worm Conclusion

---

### Version 1: Conservative

"Analysis of state-specific probability currents in C. elegans identified ADEL–URYVR and
ADEL–URYDL as the highest-ranked off-reference pairs with pdf-1/pdfr-1 neuromodulatory
annotation (ranks 2 and 6 of 1321 off-reference pairs; Fisher OR = 5.2 for top-20 PDF
enrichment, p = 0.008). These rankings depend on both CePNEM behavioral residualization
and anatomy-guided graphical lasso precision estimation; under raw GCaMP activity with
the same estimator, the pairs rank 28th and 39th (top 2–3%). A co-observation matched
null confirms the rankings are not explained by differential observation support
(ADEL–URYVR: p = 0.001; ADEL–URYDL: p = 0.005). The rankings are unchanged by coupling
correction (ΔΩ^B ranks 2 and 3), are present under identity diffusion (ΔQ alone, ranks 5
and 9), and are not explained by endpoint diffusion hubness (hub-matched null p = 0.0017
and p = 0.0043). These pairs are novel predictions without direct experimental confirmation.
The biologically confirmed case in this dataset is RMEL–RMER (funatlas wt q = 0.0002,
unc-31 abolished), whose model ranking is sensitive to coupling assumptions but whose
functional connection demonstrates that the framework can identify genuine off-connectome
neuropeptide-mediated interactions."

**What this version claims**: Signal elevation is genuine and specific; not an artifact.
Robustness of the specific ranking to all tested controls. Honest about estimator
dependence and lack of experimental confirmation.

---

### Version 2: Balanced (Recommended)

"The primary ADEL–URY organization is a precision-dominant, dwelling-dominant,
off-reference current structure that is incrementally strengthened by empirically aligned
diffusion, not explained by state-specific drift, co-observation structure, or generic
dense diffusion. Its top rankings (ADEL–URYVR rank 2, ADEL–URYDL rank 6 of 1321
off-reference pairs) depend on the primary CePNEM residual and anatomy-guided
graphical-lasso pipeline, but the signal remains elevated in raw GCaMP under the same
estimator (ranks 28 and 39) and significant in co-observation-matched controls
(p = 0.001 and p = 0.005). PDF-associated pairs (pdf-1/pdfr-1, Bentley ESconnectome)
are enriched in the top-ranked off-reference pairs across all tested K thresholds
(Fisher OR = 5.2 at the pre-specified K = 20, degree-permutation p = 0.008; enrichment
BH-significant at K = 30–50), while serotonin-annotated pairs are entirely absent from
the top-ranked pairs at any K. The DA_mech ↔ URY_URX mechanosensory/dopaminergic module
is the dominant current block across all robustness checks. ADEL–URYVR is the most
timescale-stable prediction (top-5 at all tested diffusion timescales). The framework's
ability to identify genuine off-connectome interactions is demonstrated by the independent
confirmation of RMEL–RMER (funatlas wt q = 0.0002, unc-31-dependent, n = 22 observations)
as a dwelling-dominant DCV-mediated interaction."

**What this version claims**: Names the full finding with honest qualification of
estimator dependence and interpretation. Shows robustness support for each element.
Identifies ADEL-URYVR as primary, RMEL-RMER as proof of concept. Balanced tone.

---

### Version 3: Strong

"Off-reference probability current analysis during C. elegans locomotor state transitions
reveals a dwelling-dominant ADEL–PDF neuropeptide circuit organization as the highest-ranked
novel biological prediction. ADEL–URYVR (rank 2) and ADEL–URYDL (rank 6) of 1321
off-reference Class-4 pairs carry pdf-1→pdfr-1 annotation and are at the 99.9th and
99.5th percentiles of co-observation-matched distributions (p = 0.001 and p = 0.005).
Their rankings survive state-specific coupling correction (ΔΩ^B ranks 2 and 3), are
present under identity diffusion (ranks 5 and 9 in ΔQ alone), pass all four diffusion
control tests, and are robust to every tested connectome reference definition. PDF
annotation enrichment holds from K = 5 (2 in top-5) through K = 100 (11 in top-100)
with odds ratios of 5–14. The DA_mech ↔ URY_URX dopaminergic/mechanosensory module
is the top-ranked current block under all five diffusion specifications, all coupling
corrections, and in raw GCaMP. Together with the independently confirmed RMEL–RMER
funatlas interaction (wt q = 0.0002, unc-31 abolished), these results establish
state-dependent neuropeptide-mediated off-connectome current organization as a
distinctive feature of the C. elegans behavioral state network."

**What this version claims**: Full positive framing, foregrounding the strength of
the evidence. Less hedging on estimator dependence. Appropriate for a high-confidence
interpretation if full caveats appear in Methods/Supplement.

**CAUTION — strong version requires**: The statement "robust to every tested connectome
reference definition" must exclude RMEL-URYDL or be narrowed to ADEL pairs. The phrase
"highest-ranked novel biological prediction" should be qualified as "within the primary
analysis pipeline."

---

## Recommended Approach

Use **Version 2 (balanced)** in the main paper Results section.

Use **Version 3 (strong)** in the Abstract, abbreviated.

Use **Version 1 (conservative)** framing in the Discussion limitations paragraph.

---

## Core Fixed Phrases (Use in All Versions)

These phrases should appear verbatim or very close to verbatim:

1. **On the ranking**: "ranks 2 and 6 of 1321 off-reference pairs by state-specific probability current"

2. **On estimator dependence**: "the specific top-2 ranking requires CePNEM behavioral residualization and anatomy-guided graphical lasso estimation; under raw GCaMP with the same estimator, the ranks are 28 and 39 (top 2–3%)"

3. **On co-observation null**: "ADEL–URYVR is at the 99.9th percentile of co-observation-matched pairs (p = 0.001) and ADEL–URYDL at the 99.5th percentile (p = 0.005)"

4. **On diffusion**: "the signal is present under identity diffusion (ranks 5 and 9 without diffusion weighting) and is not explained by diffusion hubness (hub-matched null p = 0.0017)"

5. **On coupling correction**: "rankings are unchanged or improved under state-specific coupling correction (ADEL–URYVR rank 2, ADEL–URYDL rank 3 under ΔΩ^B)"

6. **On enrichment**: "PDF annotation is enriched in the top-K for all tested K (2/5, 3/10, 4/20; Fisher OR = 5.2 at K = 20, degree-permutation p = 0.008)"

7. **On RMEL-RMER**: "RMEL–RMER (funatlas wt q = 0.0002, unc-31 DCV-dependent; n = 22 observations) provides independent validation of the framework's capacity to identify genuine off-connectome neuropeptide interactions; its model ranking is sensitive to the fixed-coupling assumption"

8. **On module**: "DA_mech ↔ URY_URX is the dominant current module across all robustness tests (rank 1 under all diffusion specifications, coupling corrections, and raw GCaMP)"

---

## What Each Version Does NOT Claim

All versions refrain from:
- Claiming funatlas confirmation of ADEL-URYVR or ADEL-URYDL
- Claiming PDF enrichment is globally FDR-controlled at K=20
- Claiming diffusion is irrelevant or that ΔQ is sufficient
- Claiming RMEL-RMER ranking validates the model
- Claiming "information-limiting" interpretation (Phase 4B: no support)
- Claiming current empirically outperforms ΔQ globally
