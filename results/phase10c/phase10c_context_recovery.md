# Phase 10C — Context Recovery
Date: 2026-06-15
Authorization: Phase 10C

---

## Primary Object Definition

The state-specific probability current contrast is:

  ΔΩ_ss = D_roam @ Q_roam − D_dwell @ Q_dwell

where:
- D_s (61×61): innovations covariance matrix for state s, estimated from residuals of
  CePNEM behavioral model (Phase 3D). Full matrix; not purely diagonal.
  ρ(diag(D_roam), diag(D_dwell)) = 0.14 — substantial state-dependent reorganization.
- Q_s (61×61): anatomy-guided graphical lasso precision matrix for state s (Phase 2).
  10× stiffer penalty on off-connectome (Class-4) pairs.
- A (coupling matrix): assumed constant across states, cancels in ΔΩ_ss.

Evaluated over 1321 Class-4 (off-connectome) pairs.

---

## Role of D_s from Prior Phases

**Phase 3D (state-specific diffusion):**
- D reorganizes dramatically between states (ρ = 0.14): the strongest argument for
  using state-specific D.
- State-specific diagonal ΔΩ ≡ ΔQ (ρ = 0.9998): diagonal D adds no new information.
- State-specific FULL ΔΩ (the primary object) has ρ = 0.331 with ΔQ: low but
  significant restructuring, particularly for the ADEL-PDF pairs.
- ΔD-ΔQ correlation ≈ 0 (ρ = 0.056): pairs that reorganize most in D are NOT the
  same pairs that reorganize most in Q — no constructive interference, but also
  no confound.

**Phase 3E (Ω-specific structure search):**
- No uniquely Ω-specific biological organization found; DA_mech ↔ URY_URX remains
  rank 1 in all formulations.
- D itself (ΔD) is biologically interpretable: URY_URX neurons are most roaming-dominant
  in innovation variance (ρ = 0.14 between states, URXL +0.208, URYVL +0.149).

**Phase 4C (timescale sensitivity):**
- D(τ) grows sub-linearly with τ (OU process, τ_c ≈ 5–10 frames = 1.25–2.5 s).
- ΔΩ(τ) sign for ADEL-PDF pairs is CONSISTENTLY negative at all τ ∈ {1,2,5,10,20}.
- ΔΩ(τ=20)–ΔQ rank correlation decays to ρ = 0.136 (still significant, p<0.0001).

---

## Key ADEL/PDF Ranks Under ΔΩ_ss

| Pair | ΔΩ_ss rank | ΔΩ_ss value | ΔQ rank | Sign |
|------|-----------|------------|---------|------|
| ADEL–URYVR | 2 | −0.0688 | 5 | Dwelling-dominant |
| ADEL–URYDL | 6 | −0.0498 | 9 | Dwelling-dominant |
| ADEL–RMEL  | 4 | −0.0549 | 10 | Dwelling-dominant |
| RMEL–URYDL | 23 | −0.0310 | 16 | Dwelling-dominant |
| RMEL–RMER  | 38 | −0.0254 | 32 | Dwelling-dominant |

DA_mech ↔ URY_URX module rank: 1 (in both ΔΩ_ss and ΔQ).
PDF pairs in top-20: 4/20 (ranks 2, 4, 6, 20).

---

## Phase 10A Caveats Entering Phase 10C

- Fixed-coupling assumption tested: |ΔB|/|B| = 0.34 (non-trivial coupling change).
- ADEL-URYVR under ΔΩ^B = ΔΩ_ss + ΔB: rank unchanged (2→2). ADEL-URYDL promoted (6→3).
- ADEL-URYVR and ADEL-URYDL are NOT explained by coupling change (|ΔB| ranks 370, 601).
- RMEL-RMER: rank drops from 38 to 371 under ΔΩ^B — not robust to coupling correction.

## Phase 10B Caveats Entering Phase 10C

- Residualization: rank 2/6 requires BOTH CePNEM + anatomy-guided GL.
  Under GCaMP+GL (same estimator): ranks 28/39 (top 2-3%).
  Under CePNEM+Ridge: ranks 165/293.
- Co-observation null (primary test, uses GL values): ADEL-URYVR p=0.001, ADEL-URYDL p=0.005.
  Signal is NOT explained by differential co-observation support.
- Overall grade: B — Moderate robustness.

---

## Diffusion-Artifact Concern Being Tested (Phase 10C)

A reviewer may ask: "Is the ADEL/PDF result just an artifact of dense diffusion?"

Specifically: because D_s is a full 61×61 matrix (not purely diagonal), the product
D_s @ Q_s creates off-reference entries even for pairs where Q_s[i,j] = 0, via:

  (D_s @ Q_s)[i,j] = Σ_k D_s[i,k] * Q_s[k,j]

This is an "indirect diffusion path" — row i of D couples neuron i to all neighbors k,
and Q_s[k,j] propagates this to the (i,j) off-diagonal current entry.

The concern is that if D_s has large entries for neurons i or j (a "diffusion hub"),
then ΔΩ_ss[i,j] = Σ_k ΔD[i,k] * Q_mean[k,j] + ... could be large merely because
neuron i is a diffusion hub, not because of biological specificity.

Phase 10C tests:
1. (C1) Is the signal already present without dense D? — compare identity, diagonal, full.
2. (C2) Can random dense D reproduce the signal? — shuffle nulls.
3. (C3) What fraction of ΔΩ_ss is attributable to ΔQ vs ΔD reweighting? — decomposition.
4. (C4) Is ADEL/URYVR/URYDL merely a diffusion hub pair? — row-norm control.
5. (C5) Is the signal timescale-dependent? — uses Phase 4C D(τ) matrices.
