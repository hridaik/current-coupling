# Phase 10E — Publication Robustness Synthesis: Final Summary
Date: 2026-06-15
Authorization: Phase 10E

---

## 1. Is the Worm ADEL/PDF Current Result Publication-Ready?

**YES — with mandatory caveats explicitly stated.**

The result meets the threshold for publication as a primary finding in a methods
or systems neuroscience paper, provided the caveats in sections 4 and 5 below are
included in full. No critical flaw was identified that would undermine the core claim.

---

## 2. Final Grade

**B — Moderate, publication-ready with explicit caveats**

**Justification**: The signal is genuine (co-observation null p < 0.01 for primary pairs),
not explained by state-specific drift (ΔΩ^B unchanged), not created by dense diffusion
(present under D=I), not explained by diffusion hubness, enriched for PDF annotation
at all tested K thresholds, and off-reference under all tested connectome definitions.
The signal direction is preserved across residualization. However, the precise extreme
ranking (ADEL-URYVR rank 2, ADEL-URYDL rank 6) is specific to the anatomy-guided GL
estimator, the pairs lack direct experimental confirmation (funatlas has 0 observations),
the global PDF AUROC is not significant under ΔΩ_ss, and animal-level robustness could
not be tested with the full primary estimator.

For ADEL-URYVR specifically, the grade approaches A: the coupling-corrected rank is
unchanged, the co-obs null p=0.001 is strong, timescale robustness is complete (top-5
at all τ), and multiple independent control tests all converge. ADEL-URYDL is one
step below: robust at the primary τ but more sensitive at longer lags.

---

## 3. Final Main-Text Claim

The recommended main-text claim (balanced version from e5):

> "The primary ADEL–URY organization is a precision-dominant, dwelling-dominant,
> off-reference current structure that is incrementally strengthened by empirically
> aligned diffusion, not explained by state-specific drift, co-observation structure,
> or generic dense diffusion. Its top rankings (ADEL–URYVR rank 2, ADEL–URYDL rank 6
> of 1321 off-reference pairs) depend on the primary CePNEM residual and anatomy-guided
> graphical-lasso pipeline, but the signal remains elevated in raw GCaMP under the same
> estimator (ranks 28 and 39) and significant in co-observation-matched controls
> (p = 0.001 and p = 0.005). PDF-associated pairs (pdf-1/pdfr-1) are enriched in
> the top-ranked off-reference pairs across all tested K thresholds (Fisher OR = 5.2
> at K = 20, degree-permutation p = 0.008), while serotonin-annotated pairs are entirely
> absent from the top-ranked pairs at any K. The DA_mech ↔ URY_URX module is the
> dominant current block across all robustness checks."

---

## 4. Mandatory Caveats (Must Appear in Paper)

**Caveat 1 — Estimator dependence (MUST appear in Methods or Results):**
"The extreme top-2/6 rankings of ADEL–URYVR and ADEL–URYDL require both CePNEM
behavioral residualization and anatomy-guided graphical lasso estimation. Under raw
GCaMP with the same estimator, ranks are 28 and 39. Under ridge-regularized precision
(anatomy-uninformed), ranks are 165 and 293."

**Caveat 2 — No direct experimental confirmation for primary pairs (MUST appear in Results or Discussion):**
"ADEL–URYVR and ADEL–URYDL have zero observations in the Randi et al. perturbation
atlas and are novel predictions not yet evaluated by optogenetic methods."

**Caveat 3 — RMEL-RMER ranking fragility (MUST appear in Supplement or Methods):**
"The model ranking of RMEL-RMER (rank 38 under ΔΩ_ss) drops to rank 371 under
state-specific coupling correction (ΔΩ^B). The funatlas confirmation of RMEL-RMER
is independent of the model ranking."

**Caveat 4 — PDF AUROC not globally significant under ΔΩ_ss (MUST appear in Results):**
"The global PDF AUROC under ΔΩ_ss is 0.533 (p = 0.196), not significant. The top-K
Fisher enrichment (pre-specified K = 20) is significant (p = 0.008 degree-permutation)."

**Caveat 5 — Animal resampling is conservative (MUST appear in Methods):**
"Animal bootstrap and LOAO analyses used ridge precision for computational feasibility
and are conservative lower bounds on the primary estimator's animal-level stability."

**Caveat 6 — Decomposition non-uniqueness (MUST appear in Methods):**
"The diffusion/precision decomposition of ΔΩ_ss is not unique; two valid forms are
reported and only sign consistency and precision dominance direction are interpreted."

---

## 5. What Should Move to Supplement

| Item | Location |
|------|---------|
| Full residualization variant table (5 variants × 5 pairs) | Supplementary Table |
| Animal bootstrap rank distributions | Supplementary Table |
| Leave-one-animal-out per-animal ranks | Supplementary Table |
| All diffusion specification comparison (5 specs × 5 pairs) | Supplementary Figure or Table |
| Diffusion hub Spearman correlations (all 6 hub metrics) | Supplementary Table |
| Hub-matched null for all 5 pairs | Supplementary Table |
| Reference sensitivity table (10 defs × 5 pairs) | Supplementary Table |
| Full BH FDR audit table (70 annotation × K combinations) | Supplementary Table |
| Timescale rank table (5 τ × 5 pairs) | Supplementary Table |
| RMEL-RMER coupling-correction caveat | Supplementary Note |
| Diffusion/precision decomposition fractions | Supplementary Note (both forms) |
| Co-observation null for RMEL-RMER, RMEL-URYDL | Supplementary Table |

---

## 6. Final One-Paragraph Manuscript Summary

"Analysis of state-specific probability currents in C. elegans identified a
dwelling-dominant, precision-driven current organization centered on ADEL–URYVR
and ADEL–URYDL — the two highest-ranked off-reference pairs (ranks 2 and 6 of 1321)
with pdf-1/pdfr-1 neuromodulatory annotation. Their elevations are not explained by
differential effective coupling (ΔΩ^B ranks unchanged at 2 and 3), co-observation
structure (99.9th and 99.5th percentiles vs matched pairs, p = 0.001 and p = 0.005),
diffusion hubness (hub-matched null p = 0.0017 and p = 0.0043), or dense empirical
diffusion (signal present under identity diffusion, ranks 5 and 9). The signal is
present in raw GCaMP activity with the same estimator (ranks 28 and 39), and the
DA_mech ↔ URY_URX mechanosensory/dopaminergic module is the dominant current block
across all robustness tests. PDF annotation enrichment holds across K = 5 to 100
(Fisher OR = 5.2 at K = 20, degree-permutation p = 0.008; BH-significant at K = 30–50),
while serotonin annotation is entirely absent from the top-ranked pairs. The independent
confirmation of RMEL–RMER (funatlas wt q = 0.0002, unc-31-abolished) demonstrates
that the framework can identify genuine off-connectome neuropeptide-mediated interactions,
providing biological context for the novel ADEL–URY predictions. The extreme rankings
of ADEL–URYVR and ADEL–URYDL are estimator-dependent (requiring CePNEM + anatomy-guided
GL) and represent novel predictions requiring future experimental validation."

---

## 7. Files Produced in Phase 10E

| File | Contents |
|------|---------|
| phase10e_context_recovery.md | All primary ranks, grades, caveats, inconsistencies |
| e1_claim_hierarchy.md | A/B/C/D classification for all 10 claims |
| e2_publication_robustness_table.md | 15-row comprehensive robustness table |
| publication_robustness_table.csv | Same as CSV |
| e3_results_text.md | Manuscript-ready Results subsection |
| e4_methods_text.md | Manuscript-ready Methods text (all 8 robustness protocols) |
| e5_final_claim_language.md | Three versions of main claim (conservative/balanced/strong) |
| e6_what_not_to_claim.md | 11 explicit prohibitions with alternatives |
| e7_figure_supplement_plan.md | Assignment of each result to main/extended/supplement |
| phase10e_summary.md | This file |

---

**STOP. Phase 10E complete. Awaiting review.**
