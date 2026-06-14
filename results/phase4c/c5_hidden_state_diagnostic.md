# Phase 4C.5 — Latent-State Diagnostic: Cross-Innovation Covariance
Date: 2026-06-12

---

## Question

Are the frame-to-frame innovations Δx(t) = x(t+1) − x(t) white noise, or do they
exhibit cross-lag correlation? Non-zero Cov(Δx(t), Δx(t+k)) for k ≥ 1 implies that
the innovations are structured — either by latent dynamics not captured in the residual
coordinate, or by over-sampling a correlated process (OU above Nyquist).

---

## Method

Compute Cov(Δx(t), Δx(t+k)) pooled across all 40 recordings and all behavioral states.
For each lag k ∈ {0, 1, 2, 5}:
- Diagonal: per-neuron autocorrelation of innovations at lag k
- Off-diagonal: cross-innovation covariance between neuron pairs

Reported metrics:
- ||C(k)_off||_F / ||C(0)_off||_F — relative off-diagonal magnitude
- Mean diagonal autocorrelation C(k)[i,i] / C(0)[i,i]
- ρ(|C(k)|, |C(0)|) — whether cross-lag structure mirrors instantaneous structure
- ρ(|C(k)|, |ΔQ|) on Class-4 — whether cross-lag structure relates to ΔQ

---

## Results

| k | ||C(k)_off||/||C(0)_off|| | Mean diag autocorr | frac(|r|>0.05) | ρ(C(k), C(0)) | ρ(C(k), |ΔQ|) C4 | p-val |
|---|---|---|---|---|---|---|
| 0 | 1.000 | 1.000 | 1.000 | 1.000 | 0.146 | <0.0001 |
| 1 | 0.370 | −0.232 | 1.000 | 0.038 | 0.013 | 0.642 |
| 2 | 0.323 | −0.070 | 0.951 | 0.083 | −0.039 | 0.161 |
| 5 | 0.287 | 0.000 | 0.000 | 0.026 | 0.0003 | 0.992 |

---

## Interpretation

### Negative Lag-1 Autocorrelation: OU Process Above Nyquist

The mean diagonal autocorrelation at lag k=1 is **−0.232**. All 61 neurons show
|autocorr| > 0.05 at lag 1. This strong negative autocorrelation of frame-to-frame
innovations is a signature of an Ornstein–Uhlenbeck (mean-reverting) process sampled
at a rate faster than its correlation time.

Intuition: if the underlying process x(t) is OU with correlation time τ_c, and we sample
at interval Δt < τ_c, then the innovations Δx(t) will be negatively autocorrelated:
after a positive step, the mean-reversion pulls x(t+1) back, so Δx(t+1) tends to be
negative. This anti-correlation is the statistical fingerprint of over-sampling.

Given the sampling rate of ~4 fps and the C1 estimate of τ_c ≈ 5–10 frames ≈ 1.25–2.5 s,
the system is indeed sampled above the Nyquist rate for its dominant correlation timescale.

**Conclusion: The CePNEM residuals are NOT a white-noise process at 4 fps. They exhibit
correlated dynamics with τ_c ~ 1–2 seconds.**

### Off-Diagonal Cross-Innovation Is Substantial but Unrelated to C(0)

The off-diagonal magnitude at lag 1 (||C(1)_off|| / ||C(0)_off|| = 0.370) is 37% of
the instantaneous off-diagonal covariance. This is large — it means cross-neuron
co-fluctuations at lag 1 are a third of instantaneous co-fluctuations.

However, the cross-lag off-diagonal structure is UNRELATED to the instantaneous structure:
ρ(|C(1)|, |C(0)|) = 0.038 (near zero). Which pairs co-fluctuate at lag 1 is different
from which pairs co-fluctuate instantaneously. This rules out a simple scalar rescaling
of the same network structure.

### Cross-Innovation Unrelated to ΔQ

The k=0 (instantaneous) covariance has ρ(|C(0)|, |ΔQ|) = 0.146 on Class-4 pairs —
significant (p < 0.0001). This is the basis for the state-dependent signal in ΔQ.

At k=1, 2, 5: ρ drops to 0.013, −0.039, and 0.0003 respectively (all p > 0.15).
The cross-innovation structure does not carry information about which pairs have large |ΔQ|.

**Implication:** The latent dynamics that generate the cross-lag innovation covariance are
distinct from the state-dependent network structure that generates ΔQ. There may be a
shared latent neural state (e.g., global activity fluctuations) that creates off-diagonal
cross-innovations, but this latent state is orthogonal to the behavioral-state-specific
conditional organization.

### Lag-2 vs Lag-5 Comparison

At lag 2 (k=2), the mean diagonal autocorrelation is −0.070, with 95% of neurons still
showing |r| > 0.05. The off-diagonal magnitude remains elevated at 0.323.

At lag 5, the mean diagonal autocorrelation is essentially zero (−0.002), and no neurons
show |r| > 0.05. Off-diagonal magnitude is 0.287.

This indicates that the per-neuron autocorrelation of innovations decays to zero between
lag 2 and lag 5 (consistent with τ_c ~ 2–5 frames). The residual off-diagonal magnitude
at lag 5 (0.287) reflects cross-neuron cross-lag covariance that decays more slowly than
per-neuron autocorrelation — suggesting shared network-level slow fluctuations persist
longer than single-neuron autocorrelation.

---

## Summary

**Primary result:** Frame-to-frame CePNEM residual innovations are NOT white noise.
The strong negative lag-1 diagonal autocorrelation (mean = −0.232) confirms that
the system is sampled above the Nyquist rate for its dominant correlation timescale
(τ_c ≈ 1–2 seconds). The off-diagonal cross-innovation is substantial (37% of C(0))
but structurally unrelated to C(0) or ΔQ. There is no evidence that the latent dynamics
driving cross-lag innovation structure are the same as those driving the state-dependent
conditional organization. The ΔQ structure resides primarily in the instantaneous (k=0)
covariance and not in lagged innovation covariance.
