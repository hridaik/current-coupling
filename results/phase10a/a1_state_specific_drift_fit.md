# Phase 10A.1 — State-Specific Effective Drift Fit
Date: 2026-06-15

## Model

Discrete-time effective drift: x_{t+1} - x_t = B_s x_t + ε_t

Fitted separately for s ∈ {dwell, roam} using same-state consecutive frames.
Coordinates: CePNEM residual (61-neuron head subgraph).
State segmentation: locked Phase 2 parameters (EWMA 20s, threshold 0.284, W_trans 10s).
Missing neurons: pairwise available-case (NaN→0 with valid indicator, BLAS accumulation).

## Fitting Procedure

Δx_t = B_s x_t + ε_t

Per-state OLS with ridge regularization:
  B_s^T = (X_s^T X_s + λI)^{-1} X_s^T ΔX_s

Ridge λ = 276.997642
  Choice: 1% of median diagonal of pooled XtX matrix.
  This is a conservative ridge (≪ typical diagonal ≈ 1e4) to ensure
  numerical stability without shrinking estimated coefficients strongly.
  Same λ used for both states.

## Sample Counts

- Recordings used: 40 of 40
- Dwell same-state consecutive frames: 46438
- Roam same-state consecutive frames: 17117
- Frame ratio (roam/dwell): 0.369

## Stability of Fitted Matrices

### B_dwell
- ||B_dwell||_F = 1.6438
- Eigenvalue real parts: range [-0.2748, -0.1067]
- Stability (all real parts < 0): YES

### B_roam
- ||B_roam||_F = 1.8514
- Eigenvalue real parts: range [-0.3658, -0.0938]
- Stability (all real parts < 0): YES

## Summary Norms

- ||B_dwell||_F = 1.6438
- ||B_roam||_F  = 1.8514
- ||ΔB||_F      = 0.6275
- Relative change ||ΔB|| / ||B_roam|| = 0.3389

## Is ΔB Globally Large or Small?

Moderate (20–50%): ||ΔB||/||B_roam|| = 0.339. Non-trivial but not dominant state change in coupling.

For comparison: ||ΔD||_F / ||D_roam||_F ≈ 0.23 (from Phase 3D).
The relative magnitude of coupling vs diffusion state-change provides context
for how much each assumption (fixed A, fixed D) might matter.

## Files Saved
- results/phase10a/B_roam.npy
- results/phase10a/B_dwell.npy
- results/phase10a/DeltaB.npy
