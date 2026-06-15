# Phase 10A — Fixed-Coupling and Baseline Controls: Summary
Date: 2026-06-15
Authorization: Phase 10A

## Overview

This phase tested whether the fixed-coupling assumption in the main current
formulation (Ω_s = D_s Q_s + A, A constant across states) biases the key
biological finding (ADEL-PDF dwelling-dominant current organization).

## 1. All Key Pair Ranks Under Each Ranking Object

| Pair | |ΔΩ_ss| | |ΔQ| | |ΔΩ^B| | |ΔΣ| | |ΔCorr| | |ΔB| |
|------|--------|-----|-------|-----|--------|-----|
| ADEL–URYVR | 2 | 5 | 2 | 3 | 5 | 370 |
| ADEL–URYDL | 6 | 9 | 3 | 8 | 7 | 601 |
| ADEL–RMEL | 4 | 10 | 18 | 5 | 6 | 1 |
| ADEL–URXL | 29 | 59 | 95 | 75 | 77 | 337 |
| RMEL–URYDL | 23 | 16 | 168 | 7 | 9 | 125 |
| RMEL–URYVR | 34 | 21 | 81 | 10 | 12 | 273 |
| RMEL–RMER | 38 | 32 | 371 | 59 | 69 | 95 |

## 2. Baseline Comparison Summary

### PDF Pairs in Top-20

| Object | PDF/20 | Top-20 overlap w/ |ΔΩ_ss| |
|--------|--------|--------------------------|
| |ΔΩ_ss| | 4/20 | 20/20 |
| |ΔQ| | 4/20 | 15/20 |
| |ΔΩ^B| | 3/20 | 13/20 |
| |ΔΣ| | 6/20 | 12/20 |
| |ΔCorr| | 6/20 | 12/20 |
| |ΔB| | 2/20 | 4/20 |

### Ranking Correlation with |ΔΩ_ss|

| Object | ρ(object, |ΔΩ_ss|) |
|--------|---------------------|
| |ΔQ|     | 0.331 |
| |ΔΩ^B|  | 0.319 |
| |ΔΣ|    | 0.251 |
| |ΔCorr| | 0.257 |
| |ΔB|    | 0.099 |

## 3. Fixed-Coupling Verdict

**B. Fixed-coupling assumption approximately supported; minor qualification needed.**
**Additional finding: RMEL–RMER ranking is not robust to coupling correction.**

Key statistics:
- ||ΔB||_F / ||B_roam||_F = 0.3389 (moderate state-specific coupling change)
- ρ(|ΔΩ^B|, |ΔΩ_ss|) = 0.3188 (low global ρ, expected from full-matrix ΔB)
- Top-20 overlap ΔΩ^B vs ΔΩ_ss = 13/20
- ADEL-PDF pairs under |ΔB|: ranks 370 (ADEL–URYVR), 601 (ADEL–URYDL), 1 (ADEL–RMEL)
- ADEL-PDF pairs under |ΔΩ^B|: ranks 2, 3, 18 — PRIMARY RESULT PRESERVED
- DA_mech ↔ URY_URX module under |ΔΩ^B|: rank 1 — STRENGTHENED (was rank 2 under ΔΩ_ss)
- RMEL–RMER under |ΔΩ^B|: rank 371 — SUBSTANTIALLY DEMOTED (was rank 38)

**Interpretation split by claim:**

| Claim | Under ΔΩ_ss | Under ΔΩ^B | Assessment |
|-------|------------|-----------|------------|
| ADEL–URYVR (primary novel) | Rank 2 | Rank 2 | ROBUST — unchanged |
| ADEL–URYDL (primary novel) | Rank 6 | Rank 3 | ROBUST — promoted |
| ADEL–RMEL (secondary) | Rank 4 | Rank 18 | MINOR CHANGE — top-20 |
| DA_mech↔URY_URX (#1 module) | Rank 2 | Rank 1 | STRENGTHENED |
| RMEL–RMER (confirmed case) | Rank 38 | Rank 371 | NOT ROBUST to coupling |

The ADEL–URYVR and ADEL–URYDL high rankings under ΔΩ_ss are NOT explained by ΔB
(their ΔB ranks are 370 and 601), confirming their dominance reflects precision and
diffusion organization, not differential effective coupling.

RMEL–RMER's ranking under ΔΩ_ss is partly confounded with the fixed-A assumption.
Its biological confirmation (funatlas wt q = 0.0002, unc-31 abolished) is independent
and remains valid, but the claim that "RMEL–RMER ranks high under the current framework"
requires qualification.

## 4. Manuscript-Ready Conclusions

**For the primary ADEL-PDF claims:**
"To assess the fixed-coupling assumption, we fitted state-specific effective drift
matrices B_s by ridge regression (Δx_t = B_s x_t + ε_t, same-state frames,
ridge λ = 277). The coupling state change ||ΔB||/||B|| = 0.34 is non-trivial, but
the primary predictions ADEL–URYVR and ADEL–URYDL rank 2nd and 3rd respectively
under the fully corrected current ΔΩ^B = ΔΩ_ss + ΔB, identical or improved relative
to ΔΩ_ss alone. The fixed-coupling assumption does not confound these predictions,
as their high ΔΩ_ss rankings are not explained by differential effective coupling
(|ΔB| ranks 370 and 601 of 1321; Supplementary Note X)."

**For the RMEL–RMER confirmed case:**
"The RMEL–RMER pair, confirmed by optogenetic perturbation (funatlas wt q = 0.0002,
unc-31 abolished), drops from rank 38 to rank 371 under the coupling-corrected current
ΔΩ^B. The biological confirmation of RMEL–RMER is based on independent experimental
data, not on the model ranking; the framework prediction was a necessary precondition
for examining this pair, and the three-way convergence (observational, optogenetic,
genetic) remains unchanged."

## 5. Files Produced

| File | Contents |
|------|---------|
| phase10a_context_recovery.md | Context from prior phases |
| a1_state_specific_drift_fit.md | B_dwell, B_roam fitting report |
| a2_deltaB_keypair_analysis.md | ΔB ranking of key pairs |
| a3_state_specific_current_recompute.md | ΔΩ^B comparison with ΔΩ_ss |
| a4_baseline_comparison.md | All-object comparison table |
| a5_ranking_correlation_matrix.md | Spearman correlation matrix |
| ranking_correlation_matrix.csv | Same, CSV format |
| a6_fixed_coupling_verdict.md | Formal verdict and manuscript sentence |
| B_roam.npy | Fitted B_roam matrix |
| B_dwell.npy | Fitted B_dwell matrix |
| DeltaB.npy | ΔB = B_roam - B_dwell |
| DO_B.npy | ΔΩ^B = ΔΩ_ss + ΔB |

---
**STOP. Awaiting review.**
