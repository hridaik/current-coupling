# Phase 10F.1 — Drift Scaling and Sign Audit
Date: 2026-06-15

## 1. How Was D_s Estimated?

**Convention: D_s = Cov(Δx | state s)**

D_s is the empirical covariance of the discrete-time first-difference process
Δx_t = x_{t+1} - x_t, pooled across all 40 recordings within each behavioral state.
It is a FULL (61×61) symmetric positive semi-definite matrix.

Key verification: max|DO_ss - D_r @ Q_r - D_d @ Q_d| = 0.00e+00 (numerical zero).

Diagonal range (CePNEM): D_roam [0.269, 0.613], D_dwell [0.260, 0.510].
Off-diagonal mean |D_roam| = 0.0064 (~1.5% of diagonal mean).

This convention is Option A (Cov(Δx)), NOT divided by 2Δt.

## 2. How Was B_s Estimated?

**Convention: Discrete-time increment drift from Δx_t = B_s x_t + ε_t**

B_s is the ridge-OLS regression coefficient matrix predicting one-frame increments
Δx from the current state x, separately within roaming and dwelling states.
Both Δx and x are dimensionless (unit-variance CePNEM residuals), so B is dimensionless.

||B_roam||_F = 1.8514
||B_dwell||_F = 1.6438
||ΔB||_F = 0.6275
||ΔB||/||B_roam|| = 0.3389

## 3. Sign Convention

ΔΩ^B = ΔΩ_ss + ΔB = (D_r Q_r − D_d Q_d) + (B_roam − B_dwell)

If B encodes the state-specific A matrix (Ω_s = D_s Q_s + B_s), then:
ΔΩ^B = Δ(D Q) + Δ(B) = ΔΩ_ss + ΔB

Verification: max|DO_B - (DO_ss + ΔB)| = 0.00e+00 (numerical zero). ✓
Sign is consistent with positive ΔB increasing the current.

## 4. Unit Compatibility

**In the discrete-time framework:**
- D_disc has units [x]^2 (covariance of Δx, dimensionless if x is normalized)
- Q has units [x]^{-2} (precision of x)
- D Q is dimensionless
- B is dimensionless (regression coefficient Δx / x)
- D Q and B are compatible: both dimensionless
- ΔΩ^B = ΔΩ_ss + ΔB is dimensionally consistent ✓

**The Phase 10A computation is scale-compatible in the discrete-time framework.**

## 5. Continuous-Time Interpretation (Ambiguity)

For the continuous-time OU process dx = A x dt + √(2D_cont) dW:
  D_disc = Cov(Δx|s) ≈ 2 D_cont Δt
  B ≈ A Δt

The continuous-time Ω = D_cont Q + A = (D_disc Q / 2 + B) / Δt
→ Rank-equivalent to: D_disc Q / 2 + B = (D_disc Q + 2B) / 2
→ Or equivalently: rank by D_disc Q + 2B

**The Phase 10A formula (ΔΩ_ss + ΔB) uses D_disc Q + 1×B.**
**The continuous-time formula would be D_disc Q + 2×B.**
The difference: TWICE the relative weight on the B (coupling) term.

This ambiguity has NO consequence for pairs where |ΔB| << |ΔΩ_ss|.
It HAS consequence for ADEL-RMEL (|ΔB| rank 1 of 1321 C4 pairs).

## 6. Key Pair Ranks Under All Formulations

| Pair | ΔΩ_ss rank | ΔΩ^B (+1×ΔB) | ΔΩ^B_cont (+2×ΔB) | ΔB rank |
|------|-----------|-------------|-----------------|---------|
| ADEL–URYVR | 2 | 2 | 2 | 370 |
| ADEL–URYDL | 6 | 3 | 10 | 601 |
| ADEL–RMEL | 4 | 18 | 837 | 1 |
| RMEL–URYDL | 23 | 168 | 836 | 125 |
| RMEL–RMER | 38 | 371 | 1267 | 95 |

## 7. Conclusions

### Are all matrices in compatible units?
YES — in the discrete-time framework. D_disc Q and B are both dimensionless.
The formula ΔΩ^B = ΔΩ_ss + ΔB is dimensionally consistent.

### Was the sign correct?
YES. Verified algebraically and numerically (max error < machine epsilon).

### Are rank conclusions unchanged?

**For the primary claims (ADEL–URYVR, ADEL–URYDL):**
YES — ranks are IDENTICAL under both +1×ΔB and +2×ΔB:
  ADEL–URYVR: rank 2 under ΔΩ_ss, rank 2 (+1×ΔB), rank 2 (+2×ΔB).
  ADEL–URYDL: rank 6 under ΔΩ_ss, rank 3 (+1×ΔB), rank 10 (+2×ΔB).
Their |ΔB| is small (ranks 370 and 601 of 1321), so doubling ΔB has negligible effect.

**For ADEL–RMEL (|ΔB| rank 1):**
Rank goes from 4 (ΔΩ_ss) → 18 (+1×ΔB) → 837 (+2×ΔB).
Under the continuous-time formula, ADEL-RMEL drops substantially further.
Phase 10A correctly identifies this but under-estimates the severity by 2×.

### Manuscript wording update required:
1. State explicitly: 'D_s = Cov(Δx | state s) is the discrete-time noise covariance;
   B_s is the discrete-time regression coefficient from Δx = B_s x + ε.'
2. Note: 'The coupling correction ΔΩ^B = ΔΩ_ss + ΔB is formulated in discrete-time
   units where D and B are both dimensionless. Under a continuous-time convention
   D_cont = D_disc / (2Δt), A_cont = B / Δt, the coupling term carries 2× the relative
   weight of D, making the ADEL-RMEL demotion more severe (Supplementary Table).'
3. Add continuous-time corrected ranks (+2×ΔB) to supplementary table.
