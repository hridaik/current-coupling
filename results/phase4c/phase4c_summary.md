# Phase 4C — Final Summary
Date: 2026-06-12
Authorization: Phase 4C

---

## The Question

On what timescale do the observed structures (D, Q, Ω) exist? If a structure
disappears rapidly as Δτ increases, it is supported primarily by fast dynamics.
If it persists, it reflects slower state organization.

---

## Key Findings

### 1. Diffusion D(τ) is Sub-Linear — The Process Is Correlated

Per-neuron variance grows strongly sub-linearly with τ. The normalized rate D(τ)/τ
decreases from 0.42 (τ=1) to 0.075 (τ=20) for roaming and analogously for dwelling.
This monotone decrease confirms an Ornstein–Uhlenbeck (OU) process, not random walk,
with effective correlation time τ_c ≈ 5–10 frames (1.25–2.5 seconds).

**Roam–dwell inversion near τ ≈ 5 frames:** At short lags, roaming neurons have
slightly higher variance; at τ ≥ 5, dwelling neurons have higher cumulative variance.
The two states have structurally different temporal dynamics that are not simply rescaled
versions of each other.

### 2. State Separation Is a Slow Feature

The relative state difference ||ΔD(τ)||_F / ||D_roam(τ)||_F increases with τ:
0.23 at τ=1 → 0.36 at τ=20. State-dependent structure is more separable at longer
timescales. The ΔD–ΔQ correlation is weakest at τ=1 (ρ=0.056) and strongest at τ=20
(ρ=0.138). **The ΔQ precision organization is most closely related to long-timescale
(seconds) state-dependent diffusion, not fast frame-to-frame fluctuations.**

### 3. ΔΩ–ΔQ Alignment Decays but Persists

The Spearman correlation between |ΔΩ(τ)| and |ΔQ| on Class-4 pairs:
τ=1: ρ=0.331 → τ=20: ρ=0.136. The decay is monotone but the alignment remains
highly significant (p < 0.0001) at every timescale tested. The ΔΩ structure itself
changes rapidly across τ (self-correlation τ=1 vs τ=20: ρ=0.13), indicating that
which pairs dominate the current organization is timescale-dependent.

### 4. ΔΩ Is the Stable Descriptor for Key Pairs

For ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, and RMEL–URYDL:
- ΔD sign is unstable across τ for 3 of 4 pairs (sign reversals at different lags)
- **ΔΩ is consistently negative for all four pairs at every τ ∈ {1, 2, 5, 10, 20}**

The ΔΩ sign (dwelling-dominant current organization) is the most robust timescale-
invariant descriptor of these PDF-associated pairs. The ΔD sign fluctuates because
fast and slow state-dependent dynamics can point in opposite directions.

ADEL–RMEL and RMEL–URYDL share a sign inversion in ΔD at τ ≈ 10 frames (≈2.5 s),
suggesting a common ~2.5-second timescale for their state-dependent organization.
ADEL–URYDL shows consistently positive ΔD (roam > dwell) at all timescales, making
it the most structurally consistent pair.

### 5. Innovations Are Not White Noise — OU Over-Sampling Confirmed

Frame-to-frame innovations Δx(t) show mean diagonal autocorrelation of −0.232 at lag 1.
This strong negative autocorrelation confirms the system is sampled above the Nyquist
rate for its dominant correlation timescale. The off-diagonal cross-innovation at lag 1
is 37% of C(0) but structurally unrelated to C(0) (ρ = 0.038) and to ΔQ (ρ = 0.013,
p=0.64). **The latent dynamics generating cross-lag innovation covariance are orthogonal
to the state-dependent conditional organization in ΔQ.**

---

## Timescale Map of Observed Structures

| Structure | Timescale | Evidence |
|---|---|---|
| Correlated innovations (OU) | τ_c ≈ 1–2 s (5–10 frames) | Negative lag-1 autocorr = −0.23; D(τ)/τ decay |
| Roam–dwell diagonal inversion | ~5 frames (~1.25 s) | D_roam vs D_dwell crossover |
| ΔD pair rankings (consistent) | N/A — rapidly decorrelate | ρ(ΔD(τ=2), ΔD(τ=1)) = 0.59 |
| ΔΩ–ΔQ alignment | Persists 1–20 frames | ρ ranges 0.13–0.33 (all p<0.0001) |
| ΔΩ sign for ADEL-PDF pairs | Stable 1–20 frames | Consistently negative throughout |
| ΔQ-dominant state structure | Long timescales (~5–20 frames) | ρ(ΔD, ΔQ) grows with τ |

---

## Main Conclusion

**The state-dependent conditional organization indexed by ΔQ operates primarily on
slow timescales (τ ≈ 5–20 frames = 1.25–5 seconds), not on single-frame dynamics.**

This is supported by three independent lines of evidence:
1. The ΔD–ΔQ correlation increases monotonically from τ=1 to τ=20
2. The relative state difference ||ΔD||/||D|| also increases monotonically
3. The innovation diagnostic confirms the underlying process is correlated at τ_c ~ 1–2 s

The state-dependent organization identified in Phase 2–3 (ΔQ and ΔΩ signals) is a
feature of slow behavioral-state dynamics, not fast single-step fluctuations. This is
consistent with the behavioral state labels themselves being defined by a 20-second EWMA
of velocity — slow processes defined by slow segmentation.

ΔΩ is robust across timescales for the key ADEL-PDF pairs, always pointing toward
dwelling-dominant current organization. This makes ΔΩ a more interpretable and stable
descriptor than ΔD for the state-dependent network structure.

---

## Limitations

1. Only CePNEM coordinate analyzed (GCaMP not shown in this phase). The GCaMP coordinate
   may have different correlation timescales due to the fluorescence indicator dynamics.

2. State conditioning uses strict (all-frames-same-state) criterion. At τ=20 frames,
   transitions within the window are excluded, which may bias D(τ) estimates by excluding
   transition epochs. Frame count at τ=20: dwell n_min=29,146, roam n_min=8,792 — adequate.

3. The cross-innovation analysis pools all states. State-specific cross-innovation
   covariance (separately for roam and dwell) was not computed in this phase.

---

## Files

| File | Contents |
|---|---|
| `c1_diffusion_timescale.md` | D(τ) diagonal scaling, state inversion, ΔD–ΔQ alignment |
| `c2_current_timescale.md` | ΔΩ(τ) vs ΔQ alignment, ΔΩ self-consistency |
| `c3_precision_timescale.md` | Normalized D(τ)/τ, pair ranking decorrelation |
| `c4_adel_timescale.md` | Per-pair ΔD and ΔΩ profiles across τ |
| `c5_hidden_state_diagnostic.md` | Cross-innovation Cov(Δx(t), Δx(t+k)) |
| `phase4c_results.json` | All numeric results |
| `D_cepnem_tau{τ}_roam.npy` | D(τ) matrices for each τ, state |

---

## Authorization Boundary

This phase did NOT:
- Fit new models
- Evaluate held-out data
- Make perturbation predictions
- Revisit Ω vs Q debates from Phase 3
- Revisit information-limiting analysis from Phase 4B
- Revisit coupling models

**STOP. Awaiting review.**
