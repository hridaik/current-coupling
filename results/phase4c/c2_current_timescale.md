# Phase 4C.2 — Multi-Timescale Ω(Δτ)
Date: 2026-06-12

---

## Question

How does the state-dependent current organization ΔΩ(τ) = D_roam(τ)Q_roam − D_dwell(τ)Q_dwell
change as τ increases? Does the ΔΩ–ΔQ alignment persist or decay?

---

## Method

ΔΩ(τ) is computed using the multi-timescale diffusion D(τ) from C1 combined with
the τ=1 precision matrices Q_roam and Q_dwell (Phase 2 state-specific graphical
models). For each τ:

```
Ω_roam(τ) = D_roam(τ) @ Q_roam
Ω_dwell(τ) = D_dwell(τ) @ Q_dwell
ΔΩ(τ) = Ω_roam(τ) − Ω_dwell(τ)
```

This uses the stationary precision Q (τ=1 estimate) as the structural reference.
The D(τ) captures how the noise covariance scales with timescale.

Antisymmetric fraction: ||antisym(ΔΩ)||_F / ||ΔΩ||_F captures how much of the
state change involves a genuine probability current (antisymmetric part of ΔΩ).

---

## Results

### ΔΩ(τ) Structure as a Function of Lag

| τ | ρ(|ΔΩ(τ)|, |ΔQ|) on C4 | p-value | ||ΔΩ(τ)||_F | Anti-sym frac |
|---|---|---|---|---|
| 1  | 0.331 | <0.0001 | 1.037 | 0.125 |
| 2  | 0.286 | <0.0001 | 1.483 | 0.131 |
| 5  | 0.234 | <0.0001 | 2.435 | 0.130 |
| 10 | 0.194 | <0.0001 | 3.446 | 0.131 |
| 20 | 0.136 | <0.0001 | 4.569 | 0.145 |

### ΔΩ(τ) Self-Consistency Across Timescales

| τ | ρ(|ΔΩ(τ)|, |ΔΩ(1)|) on C4 |
|---|---|
| 1  | 1.000 |
| 2  | 0.650 |
| 5  | 0.331 |
| 10 | 0.238 |
| 20 | 0.133 |

---

## Interpretation

### ΔΩ–ΔQ Alignment Decays but Remains Significant

The Spearman rank correlation between |ΔΩ(τ)| and |ΔQ| on Class-4 pairs starts at
ρ = 0.33 at τ = 1 and decays to ρ = 0.14 at τ = 20 — but it remains highly significant
(p < 0.0001) at every timescale tested. The state-dependent current organization, as
measured by the ΔΩ–ΔQ alignment, is not a purely fast-dynamics feature that vanishes
at long timescales. It survives, attenuated, up to τ = 20 frames (≈5 seconds).

The decay pattern is consistent with the interpretation from C1: D(τ) mixes fast and
slow components. At short τ, fast dynamics dominate D(τ); these have weaker ΔQ alignment.
At long τ, slow dynamics dominate D(τ); these have stronger ΔQ alignment (per C1). But
the combination D(τ) @ Q shows decreasing alignment with ΔQ as τ increases, because
the precision Q itself was estimated at τ=1, and becomes an increasingly poor approximation
to the effective slow-dynamics precision at longer τ.

### ΔΩ(τ) Self-Decorrelation Is Rapid

The pair-ranking correlation of ΔΩ with itself across timescales drops from 1.00 to 0.65
at τ=2, then to 0.33 at τ=5, and to 0.13 at τ=20. This rapid decay indicates that which
pairs have the most current-organization change is highly τ-dependent. The top ΔΩ pairs
at τ=20 are largely different from the top pairs at τ=1.

This reflects that different neuron pairs contribute state-dependent dynamics at different
timescales — the ΔΩ structure is not a single timescale-invariant organization.

### Antisymmetric Fraction Is Stable

The antisymmetric fraction of ΔΩ — representing genuine probability current contribution —
is approximately constant at 0.12–0.15 across all τ values. The fraction of ΔΩ attributable
to directed current is not timescale-dependent; the current contribution to total ΔΩ
magnitude is a stable ~13% regardless of lag.

### ||ΔΩ||_F Grows with τ

The total magnitude of ΔΩ grows from 1.04 at τ=1 to 4.57 at τ=20. This growth is
less than linear (τ×1.04 would give 4.08 at τ=4 not 20; the actual 4.57 at τ=20
implies slower-than-linear growth). The state-difference in Ω accumulates with lag
but saturates, consistent with bounded OU dynamics.

---

## Summary

**Primary result:** ΔΩ–ΔQ alignment is strong at τ=1 (ρ=0.33) and decays monotonically
to ρ=0.14 at τ=20, but remains significant throughout. The ΔΩ pair-ranking structure
changes substantially with τ (ρ=0.65 at τ=2, 0.13 at τ=20) — which pairs dominate the
current organization depends strongly on the timescale of analysis. The antisymmetric
(current) fraction of ΔΩ is stable at ~13% regardless of timescale.
