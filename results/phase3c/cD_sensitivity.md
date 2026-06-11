# Phase 3C-D — Sensitivity to D and A Choice
Date: 2026-06-03
Authorization: Phase 3C

## Central Question

Does any major Phase 3C conclusion depend on the choice of D (noise model)
or A (anatomical baseline)?

---

## D Sensitivity

### D models tested

| Model | Description | Range | Mean |
|---|---|---|---|
| D1 | Identity: D_ii = 1.0 | [1.000, 1.000] | 1.000 |
| D2 | CePNEM residual variance (pooled) | [0.943, 1.096] | 1.025 |
| D3 | First-difference innovation variance | [0.316, 0.483] | 0.405 |

**D2 near-uniformity**: CePNEM residuals are z-scored globally before
estimation. This forces per-neuron residual variance ≈ 1.0 for all neurons.
The observed D2 range (0.943–1.096) is within ±8% of unity; the coefficient
of variation is ≈3%. D2 is effectively a constant rescaling.

**D3 systematic offset**: D3 (first-difference variance) is uniformly lower
than D2 (mean D3/D2 ≈ 0.395), reflecting temporal autocorrelation in the
CePNEM residuals. D3 is also near-uniform (range 0.316–0.483, CV ≈ 10%).
D3 is a different near-constant rescaling of ΔQ.

### Rank stability: ΔΩ vs ΔQ across D choices

Since ΔΩ = D · ΔQ (A cancels in the state difference), rank stability is
determined entirely by how uniform D is.

| Comparison | Spearman ρ(|ΔΩ_i|, |ΔΩ_j|) |
|---|---|
| D1 vs D2 | **0.99999** |
| D1 vs D3 | **0.99994** |
| D2 vs D3 | **0.99993** |

All pairwise correlations exceed 0.9999. The |ΔΩ| rankings are effectively
identical regardless of which D model is used.

### Top-20 overlap across D choices

| Comparison | Pairs in common (of 20) |
|---|---|
| D1 vs D2 | **19 / 20** |
| D1 vs D3 | **20 / 20** |

The single D1/D2 discordance is a rank-borderline case at position 19–20.
The remaining 19 pairs are stable across all three D variants.

### Per-neuron variation for key neurons

| Neuron | D2 (residual var) | D3 (firstdiff var) | D3/D2 |
|---|---|---|---|
| ADEL | 1.026 | 0.441 | 0.430 |
| URYVR | 0.999 | 0.351 | 0.351 |
| URYDL | 1.054 | 0.397 | 0.376 |
| RMEL | 1.062 | 0.386 | 0.364 |
| RID | 1.096 | 0.483 | 0.441 |

The ADEL D2 value (1.026) and URYVR D2 value (0.999) are both near 1.0.
Their ratio ≈ 1.027, meaning the ADEL→URYVR pair ΔΩ_D2 ≈ 1.026 × ΔQ_ADEL-URYVR.
This is a trivial scaling with no effect on rankings.

---

## A Sensitivity

### Mathematical argument

The identity Q = D^{-1}(Ω − A) implies:

    Ω_s = D Q_s + A

The state difference is:

    ΔΩ = Ω_roam − Ω_dwell = D Q_roam + A − (D Q_dwell + A) = D · ΔQ

A cancels exactly in the state difference. Therefore:

**The A choice (A_raw vs Creamer A_C) is completely irrelevant for ΔΩ.**

This is not an approximation — it is exact regardless of what A contains,
provided A is state-independent (i.e., the same anatomical matrix for both
roaming and dwelling states).

### Verification

Spearman ρ(ΔΩ_D1_Araw, ΔΩ_D1_Acreamer) = **1.0000** (confirmed in cA).
Spearman ρ(ΔΩ_D2_Araw, ΔΩ_D2_Acreamer) = **1.0000** (confirmed in cA).

The A choice has zero influence on ΔΩ rankings.

---

## Summary Table

| Axis | Variation tested | Effect on ΔΩ ranking | Effect on PDF AUROC |
|---|---|---|---|
| D: identity vs residual variance | D1 vs D2 | ρ = 0.99999 | 0.5560 → 0.5563 |
| D: residual vs first-difference variance | D2 vs D3 | ρ = 0.99993 | 0.5563 → 0.5566 |
| A: A_raw vs Creamer A_C | Araw vs Acreamer | ρ = 1.0000 | no change |

---

## Answer: Does Any Major Conclusion Depend on D or A?

**No.**

1. **D choice**: All three D variants produce near-identical ΔΩ rankings
   (ρ > 0.9999). The near-uniformity of D2 (z-scoring artifact) and the
   constant-offset nature of D3 mean that no D choice reveals structure
   absent from the others.

2. **A choice**: A cancels exactly in ΔΩ = D·ΔQ. A_raw and Creamer A_C
   produce identical ΔΩ rankings.

3. **Implications for Phase 3C conclusions**: All findings in cA, cB, and cC
   are fully robust. The conclusion that ΔΩ adds no information beyond ΔQ
   holds for every tested combination of D and A.

---

## Why D Is Near-Uniform: A Structural Comment

The near-uniformity of D is a direct consequence of the CePNEM fitting
procedure, which z-scores neural activity globally. This global normalization
is a preprocessing choice that intentionally equalizes signal scales across
neurons. It does not reflect biology — different neurons genuinely have
different noise levels in raw fluorescence data. If D were estimated from
raw (un-z-scored) data, it would vary more across neurons and ΔΩ might
diverge slightly from constant × ΔQ.

However, for this Phase 3C analysis operating on CePNEM-processed data,
the near-uniform D is an inherent property of the input, not an assumption.
The sensitivity analysis confirms that even the maximum biologically plausible
D variation (D3, using first-difference variance) leaves the conclusions
unchanged.

---

*3C-D scope: sensitivity characterization only. No hypothesis testing. No new fitting.*
