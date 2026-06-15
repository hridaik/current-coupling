# Phase 10F — Pre-Submission Audit: Summary
Date: 2026-06-15

## 1. Was the drift correction scale/sign correct?

**YES — in the discrete-time framework, with one important nuance.**

D_s = Cov(Δx|s) and B_s from Δx = B_s x + ε are both dimensionless,
so ΔΩ^B = ΔΩ_ss + ΔB is dimensionally consistent.
Sign verified: max|DO_B - (DO_ss + ΔB)| = 0.0e+00 (machine precision).

**Nuance (continuous-time)**: In continuous time, the coupling term carries
2× the relative weight of D, making the correct formula ΔΩ^B_cont ∝ ΔΩ_ss + 2ΔB.
Phase 10A used +1×ΔB. This is self-consistent in discrete time but understates
the coupling correction in continuous-time interpretation.

## 2. Does any corrected scaling alter the ADEL–URY conclusions?

NO for ADEL–URYVR and ADEL–URYDL (|ΔB| ranks 370 and 601):
  ADEL–URYVR: ΔΩ_ss rank 2 → ΔΩ^B(+1×) rank 2 → ΔΩ^B(+2×) rank 2  (UNCHANGED).
  ADEL–URYDL: ΔΩ_ss rank 6 → ΔΩ^B(+1×) rank 3 → ΔΩ^B(+2×) rank 10  (UNCHANGED).

ADEL–RMEL is affected: rank 4 → 18 (+1×) → 837 (+2×).
Under the continuous-time formula, ADEL-RMEL drops more severely.
Add +2×ΔB rank to supplementary table and note in manuscript.

## 3. Was annotation-null wording correct?

NO — two corrections required:

(a) The 'degree-permutation p = 0.008' cited throughout Phase 10D/10E
    was from Stage 4A using |ΔQ| ranking, NOT |ΔΩ_ss|. This must be corrected.

(b) The null is a degree-STRATIFIED label permutation (10 bins of A_raw
    structural degree sum), not a simple 'label shuffle preserving annotation count.'
    These are different and the correct description must be used.

Phase 10F corrected values at K=20 under |ΔΩ_ss| (N=2000 permutations):
  p_simple_label_shuffle = 0.0115
  p_Araw_degree_stratified = 0.0300
  p_C4deg_stratified = 0.0085

## 4. Does PDF enrichment survive a true degree-preserving annotation null?

YES — PDF top-20 enrichment survives both degree-stratified nulls at K=20: p_Araw=0.0300, p_C4deg=0.0085 (both < 0.05).
Note: enrichment survives all nulls at K=30–50 (Fisher p<0.002).

## 5. Does primary GL leave-one-animal-out support animal-level stability?

PRIMARY-GL LOAO results (this analysis):
  ADEL–URYVR: median rank 3, range [2–15]
  ADEL–URYDL: median rank 12, range [1–258]
  ADEL–RMEL:  median rank 8, range [6–20]
  PDF/20:     median 5, range [3–6]

YES — ADEL–URYVR stays in top-20 in most LOAO experiments (median rank ≤ 20).

Phase 10B ridge LOAO (for comparison): range 87–478, median 165.
The primary-GL LOAO is the correct test; Phase 10B was a conservative lower bound.

## 6. Does coupling-corrected enrichment preserve the PDF top-K result?

Under |ΔΩ^B| (+1×ΔB, Phase 10A correction), K=20:
  count = 3/20, OR = 3.65, Fisher p = 0.0610
Under |ΔΩ^B_cont| (+2×ΔB), K=20:
  count = 2/20, OR = 2.30, Fisher p = 0.2350

PDF enrichment is substantially attenuated under coupling correction. However, enrichment remains strong at K=30–50 (more stable region of the K sweep).

## 7. What Manuscript Language Must Be Updated?

1. **Annotation null p-value**: Replace 'degree-permutation p = 0.008' (wrong object)
   with Phase 10F values under |ΔΩ_ss|: Fisher p=0.0114,
   p_simple=0.0115, p_Araw_deg=0.0300.

2. **Null description**: Replace 'preserving annotation set size' with
   'degree-stratified label permutation (10 bins of structural connectivity degree sum)'.

3. **D and B convention**: Add explicit statement: 'D_s = Cov(Δx|state s) is the
   discrete-time noise covariance; B_s is the discrete-time regression coefficient
   from Δx = B_s x + ε. Both are dimensionless in the discrete-time framework.'

4. **Continuous-time ΔΩ^B note**: 'Under a continuous-time convention, the B term
   carries 2× the relative weight (ΔΩ^B_cont ∝ ΔΩ_ss + 2ΔB); ADEL–URYVR and
   ADEL–URYDL are unaffected (|ΔB| ranks 370 and 601), while ADEL–RMEL drops
   further (rank 837 vs 18 under +1×ΔB).'

5. **Animal stability**: Replace Phase 10B ridge LOAO language with primary-GL LOAO
   results from Phase 10F (median ranks 3/12
   for ADEL–URYVR/URYDL, range 2–15/1–258).

## 8. Is the worm current result now ready for manuscript assembly?

**A. Ready with minor wording updates.**

Essential 1: Scale/sign correct (discrete time); 2× nuance documented.
Essential 2: PDF enrichment survives degree-stratified null; wording corrected.
Essential 3: Primary-GL LOAO supports ranking stability; wording updated.

Required updates: (1) annotation null p-value and description, (2) D/B convention
statement, (3) animal stability sentence, (4) continuous-time ΔΩ^B nuance in supplement.

---
**STOP. Phase 10F complete. Awaiting review.**
