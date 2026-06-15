# Phase 10A.5 — Ranking Correlation Matrix
Date: 2026-06-15

Spearman rank correlations between all pairwise-absolute-value ranking objects,
computed over all 1321 Class-4 pairs.

## Correlation Matrix

| Object | |ΔΩ_ss| | |ΔQ| | |ΔΩ^B| | |ΔΣ| | |ΔCorr| | |ΔB| |
|--------|--------|--------|--------|--------|--------|--------|
| |ΔΩ_ss| | 1.000 | 0.331 | 0.319 | 0.251 | 0.257 | 0.099 |
| |ΔQ| | 0.331 | 1.000 | 0.152 | 0.538 | 0.536 | 0.213 |
| |ΔΩ^B| | 0.319 | 0.152 | 1.000 | 0.111 | 0.117 | 0.216 |
| |ΔΣ| | 0.251 | 0.538 | 0.111 | 1.000 | 0.997 | 0.140 |
| |ΔCorr| | 0.257 | 0.536 | 0.117 | 0.997 | 1.000 | 0.143 |
| |ΔB| | 0.099 | 0.213 | 0.216 | 0.140 | 0.143 | 1.000 |

## Key Observations

- ρ(|ΔΩ_ss|, |ΔQ|) = 0.331  (main framework: current vs precision; same as Phase 5B)
- ρ(|ΔΩ_ss|, |ΔΩ^B|) = 0.319  (current vs coupling-corrected current; ≈ ρ with ΔQ)
- ρ(|ΔΩ_ss|, |ΔΣ|) = 0.251  (current vs covariance change)
- ρ(|ΔΩ_ss|, |ΔCorr|) = 0.257  (current vs correlation change)
- ρ(|ΔΩ_ss|, |ΔB|) = 0.099  (current vs drift change — nearly orthogonal)
- ρ(|ΔQ|, |ΔΣ|) = 0.538  (precision vs covariance — moderate overlap)
- ρ(|ΔQ|, |ΔCorr|) = 0.536  (precision vs correlation — nearly identical to ΔΣ)

## Structural Interpretation

**Three clusters of ranking objects:**

1. **Precision/current cluster**: |ΔΩ_ss|, |ΔQ| (ρ = 0.331).
   Both extract conditional structure after removing locomotor variance (CePNEM residual).

2. **Covariance cluster**: |ΔΣ|, |ΔCorr| (ρ = 0.997).
   Nearly identical — correlation is just normalized covariance change.
   Moderately correlated with ΔQ (ρ ≈ 0.54) but weakly with ΔΩ_ss (ρ ≈ 0.25).

3. **Coupling cluster**: |ΔB| is nearly independent of everything (max ρ = 0.213 with ΔQ).
   |ΔΩ^B| is also weakly correlated with all objects (max ρ = 0.319 with ΔΩ_ss),
   because ΔB adds large independent variation to the full ranking.

**Key implication**: The current object (ΔΩ_ss) is nearly as far from |ΔΩ^B| (ρ = 0.319)
as it is from |ΔQ| (ρ = 0.331). Adding ΔB does not bring ΔΩ^B "closer" to ΔQ. The
three objects (ΔΩ_ss, ΔQ, ΔΩ^B) are mutually weakly correlated, representing three
distinct but overlapping views of state-dependent neural organization.
