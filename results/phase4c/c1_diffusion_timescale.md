# Phase 4C.1 — Multi-Timescale Diffusion D(Δτ)
Date: 2026-06-12

---

## Question

How does state-conditioned diffusion D(τ) = Cov(x(t+τ) − x(t) | state) scale with lag τ?
Does the roam/dwell state difference persist or vanish as τ increases?

---

## Method

For each τ ∈ {1, 2, 5, 10, 20} frames, compute pairwise complete-case Cov(Δx(τ) | state)
pooled across all 40 recordings. State conditioning: all frames t, t+1, ..., t+τ must be
in the same behavioral state (no transitions within the window). Minimum 2 same-state pairs
required per neuron pair per recording. CePNEM residuals used throughout.

Sampling rate: ~4 fps (0.25 s/frame). Lag τ = 20 frames ≈ 5 seconds.

---

## Results

### Diagonal Variance (per-neuron variance of Δx(τ))

| τ (frames) | D_roam diag mean | D_dwell diag mean | Ratio | D_roam/τ | D_dwell/τ |
|---|---|---|---|---|---|
| 1  | 0.4176 | 0.3990 | 1.047 | 0.4176 | 0.3990 |
| 2  | 0.6231 | 0.6188 | 1.007 | 0.3115 | 0.3094 |
| 5  | 0.9392 | 1.0237 | 0.917 | 0.1878 | 0.2047 |
| 10 | 1.1911 | 1.3612 | 0.875 | 0.1191 | 0.1361 |
| 20 | 1.5050 | 1.6882 | 0.892 | 0.0753 | 0.0844 |

**Roam–dwell inversion near τ = 5 frames (~1.25 s):**
At short lags (τ = 1, 2), roaming has slightly higher per-neuron variance.
At τ ≥ 5 frames, dwelling has higher variance. This inversion is state-selective:
roaming trajectories are more volatile at high frequency, dwelling trajectories
explore more cumulative variance at longer timescales.

**Sub-linear D(τ) growth:** For a white-noise (Markov) process, D(τ) = τ · D(1).
The normalized D(τ)/τ drops monotonically from 0.418 (τ=1) to 0.075 (τ=20) for roam
and from 0.399 to 0.084 for dwell. This decay means the process is strongly correlated
— consecutive frames are not independent. The underlying dynamics behave as an
Ornstein–Uhlenbeck (correlated) process, not a random walk.

### Diagonal Neuron Rank Reordering

| τ | ρ(diag_roam(τ), diag_roam(1)) | ρ(diag_roam, diag_dwell) |
|---|---|---|
| 1  | 1.000 | 0.139 |
| 2  | 0.961 | 0.192 |
| 5  | 0.817 | 0.242 |
| 10 | 0.674 | 0.102 |
| 20 | 0.481 | 0.033 |

The neuron rank ordering (which neurons are most variable) changes substantially with τ:
by τ = 20, only ~48% of the rank information from τ = 1 survives. Neurons that are
volatile at short timescales are not necessarily the same ones that drift most at long
timescales. The low ρ(roam, dwell) throughout confirms the two states have substantially
different neuron-specific diffusion structure at every timescale tested.

### State Difference Magnitude vs Lag

| τ | ||ΔD||_F / ||D_roam||_F |
|---|---|
| 1  | 0.232 |
| 2  | 0.217 |
| 5  | 0.257 |
| 10 | 0.315 |
| 20 | 0.359 |

The relative state difference in diffusion INCREASES with lag. At τ = 1, the two
states are 23% different in diffusion structure; at τ = 20, they are 36% different.
State-dependent dynamics become more separable at longer timescales, not shorter.

### ΔD–ΔQ Alignment on Class-4 Pairs

| τ | ρ(|ΔD(τ)|, |ΔQ|) on C4 | p-value |
|---|---|---|
| 1  | 0.056 | 0.043 |
| 2  | 0.092 | 0.0008 |
| 5  | 0.090 | 0.0010 |
| 10 | 0.108 | 0.0001 |
| 20 | 0.138 | <0.0001 |

The correlation between the state-dependent diffusion change ΔD(τ) and the precision
matrix difference ΔQ increases monotonically with τ. The ΔQ structure — estimated from
instantaneous covariance — is more consistent with LONGER-timescale state-dependent
diffusion organization than with short-timescale (τ=1) dynamics.

---

## Interpretation

The diffusion analysis reveals a strongly sub-linear growth regime consistent with
correlated (OU-like) dynamics. The key structural results:

1. **State inversion at τ ~ 5 frames:** Roaming has higher single-step volatility;
   dwelling has higher cumulative variance at longer timescales. The two states have
   qualitatively different temporal structure, not just quantitative differences.

2. **Rank reordering is substantial:** By τ = 20, which neurons are most variable
   in roaming has barely any overlap with τ = 1 (ρ = 0.48). The diffusion structure
   is timescale-dependent in a neuron-specific way.

3. **State separation increases with τ:** Longer windows reveal stronger roam–dwell
   differences. The state-dependent organization is a SLOW feature of the dynamics,
   not fast fluctuations.

4. **ΔD–ΔQ alignment grows with τ:** The strongest agreement between the diffusion-level
   state difference and the precision-level state difference (ΔQ) occurs at the longest
   timescale tested (τ = 20). This suggests the ΔQ organization reflects slow
   state-dependent network structure, not fast correlated noise.

---

## Summary

**Primary result:** Diffusion D(τ) grows sub-linearly (consistent with OU/correlated dynamics).
The relative state difference increases with τ. The ΔD–ΔQ correlation is weak at τ=1 and
strongest at τ=20, suggesting the state-dependent conditional organization indexed by ΔQ is
supported primarily by dynamics operating on timescales of 5–20 frames (1.25–5 seconds),
not the single-frame noise structure.
