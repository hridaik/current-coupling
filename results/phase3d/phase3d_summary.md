# Phase 3D Summary
Date: 2026-06-03
Authorization: Phase 3D

---

## Phase 3D Context

Phase 3C established that the diagonal Ω pathway adds nothing beyond ΔQ.
Phase 3C-E through 3C-H established that the full D_emp @ ΔQ improvement in PDF
enrichment is an imputation artifact driven by RID/RMEL/RMER diffusion hubs, not
by ADEL-centered signal.

Phase 3D tested the two remaining possibilities:
- **A**: Wrong diffusion model (→ test state-specific D)
- **B**: Wrong organizational scale (→ test module-level Ω)

---

## Phase 3D-1: State-Dependent Diffusion

### Finding 1: Diffusion IS state-dependent

The per-neuron innovation variance changes dramatically between roaming and dwelling:
- ρ(D_roam diagonal, D_dwell diagonal) = **0.14 (CePNEM), 0.20 (GCaMP)**
- The neuron ordering by innovation variance is almost completely different between states
- URY_URX module: D_roam = 0.473 vs D_dwell = 0.395 (+20% roaming elevation)
- DA_mech module: D_roam = 0.420 vs D_dwell = 0.395 (+6%)
- RME module: D_roam = 0.396 vs D_dwell = 0.403 (slightly lower during roaming)
- ||ΔD||_F / ||D_roam||_F = 23% — substantial relative change

This is a genuine biological observation: roaming is characterized by more
heterogeneous neural dynamics across neurons, with URY_URX neurons being particularly
more active and RME neurons slightly less active.

### Finding 2: State-dependent D does NOT create new Ω information

Despite the large D reorganization, the state-specific diagonal Ω is essentially
identical to ΔQ:

| Framework | ρ(|ΔΩ|, |ΔQ|) | PDF AUROC | Fisher OR |
|---|---|---|---|
| ΔQ | — | 0.556 | 5.46 |
| ΔΩ_pooled | 0.566 | 0.664 | 7.41 |
| **ΔΩ_ss_diag** | **0.9998** | **0.557** | **3.78** |
| ΔΩ_ss_full | 0.331 | 0.533 | 5.46 |

State-specific diagonal Ω (ρ = 0.9998 with ΔQ) provides no improvement over ΔQ.
State-specific full Ω is WORSE than pooled full Ω (AUROC 0.533 vs 0.664) and
even worse than ΔQ itself in Fisher OR with k_ann=4 vs 3.

**The ΔΩ_pooled improvement does NOT come from state-dependent diffusion structure.**
It comes from the specific hub-connectivity of the pooled D_emp (Phase 3C-G/H).

### Why State-Specific D Doesn't Help

ΔΩ_ss_diag[i,j] = D_r[i,i]·Q_r[i,j] − D_d[i,i]·Q_d[i,j]
≈ D_mean[i,i]·ΔQ[i,j] + ΔD[i,i]·Q_mean[i,j]

The second term (ΔD·Q_mean) is small because:
1. Q_mean ≈ (Q_roam + Q_dwell)/2 is small for off-connectome pairs (graphical lasso)
2. Even though ΔD is large diagonally, the product ΔD[i,i]·Q_mean[i,j] adds noise

The ΔD·ΔQ correlation is also near-zero (ρ = 0.056), meaning the pairs that
reorganize most in D are not the pairs that reorganize most in Q — so no constructive
interference.

---

## Phase 3D-2: Module-Level Ω

### Finding 3: DA_mech↔URY_URX is rank #2 in every Ω formulation

| Framework | DA_mech↔URY_URX rank |
|---|---|
| ΔQ | 2 |
| ΔΩ_pooled | 2 |
| ΔΩ_ss_diag | 2 |
| ΔΩ_ss_full | 2 |

The targeted test (D2.4) finds no change. Ω does not make DA_mech↔URY_URX more prominent.

### Finding 4: No new module-level structure in Ω

All apparent divergences between ΔΩ_ss_full and ΔQ at the module level originate
from low-signal (ΔQ ≈ 0) block pairs receiving imputed values. No module pair that
was high-signal in ΔQ loses prominence, and no silent module pair becomes genuinely
prominent.

The RME↔RME bilateral coupling (the strongest within-block signal) is actually
REDUCED under ΔΩ_ss_full (0.0579 → 0.0254). State-specific full Ω partially
cancels the existing strongest signal.

---

## Critical Decision Question

**After allowing state-dependent D and module-level Ω, does Ω now provide genuinely
new biological information?**

```
[x] A. No — Q remains sufficient.
[ ] B. Minor refinement only.
[ ] C. Yes — Ω reveals organization absent from Q.
```

### Quantitative Justification

**Evidence for A (Q sufficient):**

1. **State-specific diagonal Ω ≡ ΔQ**: ρ = 0.9998, no AUROC improvement
2. **State-specific full Ω degrades enrichment**: AUROC 0.533 < ΔQ's 0.556
3. **DA_mech↔URY_URX rank invariant**: #2 in all four frameworks
4. **Module-level Ω ≈ ΔQ**: ρ(ΔΩ_pooled, ΔQ) = 0.980 at module level
5. **No new high-signal modules discovered**: all divergences are from near-zero ΔQ
6. **ΔD uncorrelated with ΔQ** (ρ = 0.056): diffusion and functional connectivity
   reorganize independently — no constructive interference in state-specific Ω

**The one genuine Phase 3D finding (state-dependent D with ρ = 0.14) is biologically
interesting but does not create useful Ω information for the current analysis task.**
The URY_URX and DA_mech D changes are consistent with their functional roles, but this
information is already captured in the interpretation of ΔQ (their pair-level ΔQ
is what identified them as significant in Phase 2).

**Evidence AGAINST B or C:**

- No Ω variant improves the state-specific analysis beyond pooled-D ΔΩ_pooled
- The ΔΩ_pooled improvement (established in 3C-E/F) is an imputation artifact (3C-G/H)
- State-specific D DEGRADES rather than improves the full-matrix Ω
- Every module ranking tested comes out the same as ΔQ

---

## New Biological Observation from Phase 3D

While the main conclusion is negative for the Ω pathway, Phase 3D produced one
genuinely new observation:

**The per-neuron innovation variance reorganizes almost completely between roaming
and dwelling (ρ(D_roam, D_dwell) = 0.14)**. This means the neural system's
dynamical "noise" structure changes dramatically with behavioral state, independent
of the changes in functional connectivity (ΔQ). URY_URX neurons become substantially
more dynamically variable during roaming (+20% D), consistent with their role in
reading the O₂ gradient that drives locomotion state transitions.

This is a observation about the behavioral state-dependence of neural dynamics
beyond what is captured by the mean covariance structure (ΔQ). Whether to pursue
this as a separate analysis thread is a decision for human review.

---

## Phase 3D Outputs

| File | Description |
|---|---|
| D_roam_cepnem.npy | (61×61) CePNEM roaming diffusion matrix |
| D_dwell_cepnem.npy | (61×61) CePNEM dwelling diffusion matrix |
| D_roam_gcamp.npy | (61×61) GCaMP roaming diffusion matrix |
| D_dwell_gcamp.npy | (61×61) GCaMP dwelling diffusion matrix |
| DO_state_cep_full.npy | (61×61) CePNEM state-specific full ΔΩ |
| DO_state_cep_diag.npy | (61×61) CePNEM state-specific diagonal ΔΩ |
| d1_diffusion_metrics.json | All D1/D2 metrics |
| d1_state_dependent_diffusion.md | D1 report |
| d2_module_organization.md | D2 report |
| phase3d_summary.md | This file |

---

## Stop Condition

**Phase 3D is complete.**

**DO NOT:**
- Evaluate held-out ADEL pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, ADEL–URXL)
- Generate perturbation predictions
- Start new model families
- Extend the state-dependent D analysis without new authorization

The held-out ADEL evaluation remains unconsumed.

---

*Phase 3D: STOP. Awaiting human review.*
