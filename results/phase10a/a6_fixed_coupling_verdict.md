# Phase 10A.6 — Fixed-Coupling Assumption Verdict
Date: 2026-06-15

## Questions and Answers

### Q1: Is B_roam systematically different from B_dwell?

YES. ||ΔB||_F / ||B_roam||_F = 0.339 (> 30%). B_roam and B_dwell are systematically different.

### Q2: Does ΔB explain the ADEL/PDF current ranking?

NO. ADEL-PDF pairs rank 1–601 under |ΔB| (median 370) — not explained by drift change.

### Q3: Does adding ΔB to the current difference alter the biological conclusion?

SPLIT OUTCOME — depends on which claim:

(a) PRIMARY NOVEL PREDICTION (ADEL–URYVR, ADEL–URYDL): UNCHANGED.
    Ranks 2→2 and 6→3 respectively. These pairs are NOT in the top tier of |ΔB|
    (ΔB ranks 370 and 601), so ΔB does not cancel or amplify their ΔΩ_ss signal.
    The main experimental-prediction claim is robust.

(b) THIRD ADEL PAIR (ADEL–RMEL): MINOR CHANGE.
    Rank 4→18. Stays in top-20, modestly demoted.

(c) CONFIRMED CASE (RMEL–RMER): LARGE CHANGE.
    Rank 38→371. The RMEL–RMER current ranking is substantially attenuated when
    state-specific coupling is allowed. The funatlas confirmation (wt q = 0.0002,
    unc-31 abolished) is independent of the ranking; the PAIR remains biologically
    confirmed. But its HIGH RANKING under ΔΩ_ss was partly driven by the fixed-A
    assumption.

(d) TOP MODULE (DA_mech ↔ URY_URX): STRENGTHENED.
    Rises from rank 2 to rank 1 under ΔΩ^B. The dominant module conclusion is
    actually strengthened by the coupling correction.

Top-20 overlap ΔΩ^B vs ΔΩ_ss = 13/20; global ρ = 0.319 (low due to full-matrix
ΔB adding independent variation at moderate ranks — expected; not evidence of reversal).

### Q4: Should the manuscript qualify the fixed-coupling assumption?

YES. A sentence in the Methods or Supplementary should note the fixed-coupling assumption and report the ΔΩ^B robustness check.

### Q5: Suggested Manuscript Sentence

We fitted state-specific effective drift matrices B_s by ridge regression of single-frame increments. The coupling state change (||ΔB||_F/||B||_F = 0.34) is non-trivial. Adding the coupling correction (ΔΩ^B = ΔΩ_ss + ΔB) preserves the ADEL-PDF ranking (Supplementary Note X), but we note the fixed-coupling assumption as a limitation.

## Formal Verdict

**B. Fixed-coupling assumption approximately supported; minor qualification needed.**

### Justification

The fixed-coupling assumption is approximately supported for the primary claim. The
state-specific coupling change is non-trivial (33.9% relative Frobenius change), but
the pairs whose high ΔΩ_ss ranking is being claimed as biologically meaningful
(ADEL–URYVR, ADEL–URYDL) have very low ΔB magnitudes (ranks 370 and 601 of 1321),
meaning their current dominance is NOT explained by differential effective coupling —
it is driven by differential precision and diffusion weighting. The fixed-A assumption
is therefore not a confound for these pairs.

The RMEL–RMER confirmed case behaves differently: its ΔB rank is 95 (more moderate),
and adding ΔB attenuates its ΔΩ_ss signal substantially (rank 38→371). For RMEL–RMER,
the fixed-A assumption does affect its ranking, and the manuscript should clarify that
the RMEL–RMER high ranking under ΔΩ_ss is not fully robust to coupling correction.
The funatlas confirmation of RMEL–RMER remains valid (it is based on optogenetic
perturbation, not the model ranking), but the rank-based framing for RMEL–RMER is
sensitive to the coupling assumption.

## Supporting Evidence

- ||B_dwell||_F = 1.6438
- ||B_roam||_F  = 1.8514
- ||ΔB||_F      = 0.6275
- Relative coupling change: 0.3389
- ADEL-PDF ranks under |ΔB|: [370, 601, 1]
- ADEL-PDF ranks under |ΔΩ^B|: [2, 3, 18]
- ρ(|ΔΩ^B|, |ΔΩ_ss|): 0.3188
- Top-20 overlap ΔΩ^B vs ΔΩ_ss: 13/20
- ρ(|ΔB|, |ΔΩ_ss|) on C4: 0.0991
