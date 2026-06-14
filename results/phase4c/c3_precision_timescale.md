# Phase 4C.3 — Multi-Timescale ΔQ Comparison via D(τ)/τ
Date: 2026-06-12

---

## Question

Does the state-dependent conditional organization ΔQ — estimated from instantaneous
precision — reflect short or long timescale dynamics? How do the normalized diffusion
D(τ)/τ pair rankings relate to ΔQ as τ increases?

---

## Method

For each τ, compute ΔD_norm(τ) = (D_roam(τ) − D_dwell(τ)) / τ. For a Markov process,
D(τ)/τ → 2Σ (the stationary covariance) as τ increases. ΔΣ and ΔQ are related by
ΔΣ ≈ −Σ_r ΔQ Σ_d (linearization), so ΔD_norm(τ) should correlate with ΔQ more
strongly when D(τ)/τ approximates the stationary covariance — i.e., at longer τ.

Three metrics per τ:
1. Spearman ρ(|ΔD_norm(τ)|, |ΔQ|) — alignment with precision structure
2. Spearman ρ(|ΔD_norm(τ)|, |ΔD_norm(1)|) — self-consistency with τ=1
3. Top-20 pair overlap with τ=1 — which pairs dominate at each timescale

---

## Results

### Normalized Diffusion Diagnostics

| τ | ρ(|ΔD/τ|, |ΔQ|) C4 | p-val | ρ(ΔD/τ, ΔD(1)) C4 | Top-20 overlap | D_r/τ | D_d/τ |
|---|---|---|---|---|---|---|
| 1  | 0.056 | 0.043  | 1.000 | 20/20 | 0.418 | 0.399 |
| 2  | 0.092 | 0.0008 | 0.591 | 10/20 | 0.312 | 0.309 |
| 5  | 0.090 | 0.0010 | 0.228 | 6/20  | 0.188 | 0.205 |
| 10 | 0.108 | 0.0001 | 0.138 | 4/20  | 0.119 | 0.136 |
| 20 | 0.138 | <0.0001 | 0.086 | 2/20 | 0.075 | 0.084 |

---

## Interpretation

### ΔD–ΔQ Alignment Improves with Timescale

The Spearman rank correlation between |ΔD_norm(τ)| and |ΔQ| increases from 0.056 at τ=1
to 0.138 at τ=20. The correlation is statistically significant at all timescales ≥ τ=2
(p ≤ 0.001), and only marginally at τ=1 (p=0.043).

This result has a clear interpretation: **the ΔQ precision structure reflects slow
state-dependent dynamics, not fast noise.** The instantaneous (τ=1) diffusion is
the weakest predictor of which pairs have the largest ΔQ. The long-lag (τ=20) diffusion
is the strongest predictor. The two quantities are measuring the same underlying
state-dependent organization but at different timescales — and the ΔQ is better aligned
with the slow scale.

### Pair Rankings Decorrelate Rapidly

The normalized ΔD pair rankings decorrelate rapidly with τ. By τ=2, only 10 of the top-20
pairs from τ=1 survive. By τ=5, only 6/20. By τ=20, only 2/20. The top pairs identified
by short-timescale state diffusion are almost completely different from those identified at
long timescales.

This rapid decorrelation reflects the OU nature of the dynamics: fast fluctuations (τ≤2)
reflect a different noise process than slow drifts (τ≥10). The pairs that fluctuate most
between states at short timescales are not the same as those that drift most at long timescales.

### Normalized Variance D(τ)/τ Decreases Monotonically

D_roam/τ: 0.418 → 0.312 → 0.188 → 0.119 → 0.075 (monotone decrease)
D_dwell/τ: 0.399 → 0.309 → 0.205 → 0.136 → 0.084 (monotone decrease)

The monotone decrease confirms sub-linear D(τ) growth (correlated dynamics).
For an OU process with correlation time τ_c:
D(τ) ≈ 2σ² · τ_c · (1 − exp(−τ/τ_c)) → 2σ²τ_c as τ → ∞

From the D(τ)/τ decay pattern, the effective single-neuron correlation time is
τ_c ≈ 5–10 frames (1.25–2.5 seconds), consistent with the C1 inversion point.

### Dwell Slower Than Roam at Long Timescales

At short τ, D_roam/τ > D_dwell/τ (roaming has faster fluctuations). At τ≥5,
D_dwell/τ > D_roam/τ (dwelling neurons drift more at long timescales). This crossover
recapitulates the C1 diagonal inversion and confirms that the two states have structurally
different temporal dynamics, not just rescaled versions of the same noise.

---

## Summary

**Primary result:** The ΔQ precision-level state difference is most strongly predicted
by LONG-timescale (τ=20) diffusion state differences (ρ=0.138) and most weakly by
single-step (τ=1) diffusion (ρ=0.056). Pair rankings under ΔD(τ)/τ are essentially
uncorrelated with τ=1 rankings at τ=20 (ρ=0.086, 2/20 top pairs overlap). This indicates
that the state-dependent conditional organization captured by ΔQ operates primarily on
slow timescales (seconds), not single-frame dynamics.
