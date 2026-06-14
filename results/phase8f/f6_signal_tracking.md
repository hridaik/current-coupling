# F6: What Signal Is the C-Score Tracking?

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**Analysis**: Spearman correlations between C-score and all accessible pair-level features  
**N**: 9,900 directed pairs

---

## Spearman Correlations with C-Score

| Feature | Spearman ρ | p-value | Direction | Interpretation |
|---------|-----------|---------|-----------|---------------|
| **direct_structural** | **−0.407** | ~0 | Negative | Direct pairs score LOW on C |
| **same_module** | **−0.268** | ~0 | Negative | Within-module pairs score LOW on C |
| **is_S** | **−0.267** | ~0 | Negative | S-labeled pairs score LOW on C |
| **S_score** | **−0.997** | ~0 | Negative | C-score ≈ inverse of S-score |
| **raw_corr** | **−0.156** | 10⁻⁵⁴ | Negative | Correlated pairs score LOW on C |
| **delta_corr (|ΔCorr|)** | **−0.140** | 10⁻⁴⁴ | Negative | State-sensitive pairs score LOW on C |
| **is_N** | **+0.236** | ~0 | Positive | N-labeled pairs score HIGH on C |
| **sareachable** | **−0.085** | 10⁻¹⁷ | Negative | SAREACHABLE pairs score LOW on C |
| **path_strength** | **−0.087** | 10⁻¹⁸ | Negative | Strong H2-path pairs score LOW on C |
| **is_C** | **−0.050** | 10⁻⁷ | Negative | C-labeled pairs score LOW on C |

---

## Key Finding 1: The C-Score Is Nearly the Inverse of the S-Score

Spearman ρ(C-score, S-score) = **−0.997**

This is the most important single finding. The C-score and S-score are near-perfectly anti-correlated because:

1. The framework assigns four logits: `s_score, c_score, m_score=harmonic(s,c), n_score=0`
2. With Temperature=5, `softmax_prob_C ≈ exp(5·delta) / sum(exp(5·[omega, delta, m, 0]))`
3. When `omega` (PCor_cond, structural) is high → `S_prob` high → `C_prob` low
4. When `omega` is low (weak structural coupling) → `S_prob` low → `C_prob` high by elimination
5. The harmonic mean M-score doesn't break the anti-correlation because it is bounded above by min(s,c)

**Consequence**: The C-score is NOT measuring how "C-like" a pair is. It is measuring how "not S-like" a pair is. Any pair with weak structural coupling will score high on C, regardless of state-dependence.

---

## Key Finding 2: Every Feature That Should Indicate C Membership Shows Negative ρ

| Feature that should → high C-score | ρ | Expected sign | Actual sign |
|------------------------------------|---|--------------|-------------|
| is_C (labeled C) | −0.050 | + | − |
| sareachable (H2 relay exists) | −0.085 | + | − |
| path_strength (relay strength) | −0.087 | + | − |
| delta_corr (observable state signal) | −0.140 | + | − |

Every single positive indicator of C-membership is NEGATIVELY correlated with C-score. The framework's C-score is negatively aligned with every property that would identify a C pair.

---

## Key Finding 3: Only One Feature Positively Predicts C-Score — is_N

| Feature with positive ρ | ρ | Interpretation |
|------------------------|---|---------------|
| is_N | **+0.236** | N-labeled pairs score high on C |

The only positive predictor of C-score is N-class membership. The framework's C-ranking is essentially a ranking of "how N-like" each pair is, not "how C-like."

---

## Class-Conditional C-Score Distributions

| Class | n | Mean C-score | Median C-score | Std |
|-------|---|-------------|---------------|-----|
| N | 8,457 | **0.2444** | **0.2470** | 0.0093 |
| C | 857 | 0.2425 | 0.2458 | 0.0109 |
| S | 497 | 0.2207 | 0.2284 | 0.0280 |
| M | 89 | 0.2209 | 0.2287 | 0.0245 |

Mean C-score ranks: N > C > S ≈ M

**The intended target class (C) ranks second-to-last in C-score, below the null class (N) and above only the structural classes (S, M).**

The difference between N-mean (0.2444) and C-mean (0.2425) is **0.0019** — a gap smaller than the standard deviation of either distribution. This near-overlap explains why C-AUROC is near 0.5 (slightly below) rather than near 0.0.

---

## Within-C: What Predicts Higher C-Score?

Within the C class alone, what drives C-score variation?

| Feature | ρ within C | p-value |
|---------|-----------|---------|
| path_strength | **−0.187** | 3.7×10⁻⁸ |
| delta_corr | **−0.162** | 1.8×10⁻⁶ |

**Negative ρ for both within-C.** Within C pairs, stronger H2-path connectivity (higher path_strength) and stronger observable state dependence (higher |ΔCorr|) are associated with LOWER C-scores. This is the source of the Phase 8D finding that "state-sensitive C pairs have the worst C-AUROC."

Mechanistic interpretation: Higher path_strength → stronger H2-mediated correlation between i and j → when z is regressed out of y, more z-correlated variance is removed → PCor_cond is lower AND Delta_PCor is also reduced (because the z-mediated component is more effectively removed) → S-score drops but C-score also drops → the softmax equilibrates but does not favor C.

---

## What IS the C-Score Detecting?

Reconstructing the positive signal from the anti-correlations:

**The C-score is high for pairs that have:**
1. No direct structural coupling (DIRECT=0)
2. No strong within-module shared inputs
3. Weak observable correlation (low raw_corr)
4. Low state-dependent signal (low |ΔCorr|)
5. No H2-mediated state-active relay

This describes **structurally isolated cross-module pairs** — pairs that are in different modules, have no direct coupling, receive little shared input, and show minimal state-modulated co-activity. These are the "background noise" pairs of the network.

**In terms of the softmax mechanism**: The C-score is high when `Delta_PCor > PCor_cond` — i.e., when the z-mediated precision change marginally exceeds the z-conditioned structural precision. For structurally isolated N pairs, both quantities are near zero, but finite-sample fluctuations can make `Delta_PCor` slightly exceed `PCor_cond`. The softmax with Temperature=5 amplifies this near-zero margin, assigning C-probability=0.257 instead of the null 0.25.

---

## Top-100 vs. Bottom-100 by C-Score

| Property | Top-100 by C-score | Bottom-100 by C-score |
|----------|-------------------|----------------------|
| % N-labeled | **96%** | 40% |
| % S-labeled | 1% | **43%** |
| Mean |ΔCorr| | 0.0508 | 0.0549 |
| Mean raw_corr | 0.5543 | **0.5805** |
| % same-module | 10% | varies |
| % direct | 2% | **43%** |

The bottom of the C-score ranking (lowest C-scores) is dominated by S-labeled pairs (43%) with high raw correlation (0.5805) and direct structural coupling (43%). The top of the C-score ranking is dominated by N pairs with weak structural coupling.

The framework is producing a reliable signal — but the wrong one: it ranks pairs by (roughly) **inverse structural coupling strength**, not by state-dependent off-connectome organization.

---

## Conclusion: The C-Score Tracks Anti-Structural Properties

| Question | Answer |
|---------|--------|
| What drives C-score UP? | Absence of direct structural coupling; N-class membership; cross-module; weak raw correlation |
| What drives C-score DOWN? | Presence of direct structural coupling; S/M-class membership; within-module; strong correlation |
| Does C-score track state-dependence? | NO — ρ(C-score, |ΔCorr|) = −0.140 (negative) |
| Does C-score track C-class membership? | NO — ρ(C-score, is_C) = −0.050 (negative) |
| Does C-score identify H2-mediated links? | NO — ρ(C-score, SAREACHABLE) = −0.085 (negative) |
| What does C-score identify? | N-labeled structurally-isolated pairs at maximum softmax entropy |

The C-score does not detect its intended signal. It is, by all measurable criteria, an **anti-C detector**: a ranking that places null pairs at the top and target pairs near the bottom.
