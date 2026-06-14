# Phase 5B.5 — RMEL–RMER Under ΔΩ_ss
Date: 2026-06-12

---

## RMEL–RMER: Full Comparison

| Metric | ΔΩ_ss | ΔQ | Funatlas |
|--------|-------|-----|---------|
| Value | −0.0254 | −0.058 | wt q = 0.0002 (22 obs) |
| Rank | 38 of 1321 | 32 of 1321 | 4th highest of any annotated pair |
| Top percentile | 2.9% | 2.4% | — |
| Sign | Dwell-dominant | Dwell-dominant | Confirmed (WT stimulation drives response) |
| DCV-dependent | — | — | Yes (unc-31 q = 0.119, abolished) |

---

## What Changed

**Rank change:** 32 → 38 (demoted 6 places, from top 2.4% to top 2.9%).
**Magnitude change:** |ΔΩ_ss| = 0.0254 vs |ΔQ| = 0.058 — the state-specific current is
**less than half the magnitude** of the precision difference for this pair.

The reduction in magnitude indicates that for RMEL–RMER, the D matrix partially cancels
the Q effect: the dwelling-state D_dwell @ Q_dwell product is relatively large compared
to the roaming-state D_roam @ Q_roam product, so the difference is smaller than ΔQ alone.

**What did not change:**
- Sign: RMEL–RMER remains dwelling-dominant under both formulations (ΔΩ_ss < 0, ΔQ < 0)
- Funatlas confirmation is unchanged (independent measurement)
- Rank tier: top 3% under both formulations
- Biological interpretation: dwelling-dominant, DCV-dependent, off-connectome

---

## Does the Demotion Affect the Confirmed Case Status?

**No.** The Phase 5A confirmation (Grade C — Strong Confirmation) rests on three independent
measurements:
1. Framework: dwelling-dominant ΔQ < 0, top 2.4% (now: ΔΩ_ss < 0, top 2.9%)
2. Perturbation atlas: funatlas wt q = 0.0002, 22 obs (unchanged)
3. Genetic control: unc-31 abolishment, q = 0.119 (unchanged)

The funatlas confirmation is an independent dataset and is not affected by the choice of
ΔΩ_ss vs ΔQ as the framework's primary object. The claim "the framework predicted it"
only requires RMEL–RMER to be in the top tier of off-connectome pairs under the framework —
it is (top 3% under ΔΩ_ss, top 2.4% under ΔQ; neither changes the qualitative prediction).

---

## Quantitative Assessment of Demotion

Under ΔΩ_ss, 6 new pairs enter the top-38 that were ranked 33–38 under ΔQ:
- Ranks 33–38 under ΔΩ_ss include pairs that were distributed around ranks 12–40 under ΔQ
- RMEL–RMER (ΔQ rank 32) is displaced by pairs that are elevated by diffusion weighting

The pairs that displace RMEL–RMER (between ranks 32–38 under ΔΩ_ss) include:
- AVEL–RIVL (ΔQ rank 20 → ΔΩ_ss rank 5; substantially promoted, not directly adjacent)
- ASEL–CEPDR (ΔQ rank 85 → ΔΩ_ss rank 16; large promotion)
- Other IL/CEPDR-cluster pairs

The demotion of RMEL–RMER is modest in rank terms (6 places) and does not move it out
of the "high-priority tier" under any reasonable cutoff (top 5% = ranks ≤ 66; RMEL-RMER is rank 38).

---

## Conclusion for RMEL–RMER

**Under ΔΩ_ss:** rank 38, value −0.0254, dwelling-dominant.
**Under ΔQ:** rank 32, value −0.058, dwelling-dominant.

The confirmed case is **slightly weaker** under the current formulation (rank 38 vs 32,
magnitude 0.0254 vs 0.058), but:
- Still unambiguously high-priority (top 3%)
- Still dwelling-dominant (same sign)
- Funatlas confirmation is unchanged

The 6-place demotion does not change the qualitative conclusion from Phase 5A.
For a published paper, either formulation supports the claim that RMEL–RMER is a
framework-predicted, funatlas-confirmed, DCV-dependent off-connectome interaction.

**The confirmed case survives the transition to state-specific current.**
