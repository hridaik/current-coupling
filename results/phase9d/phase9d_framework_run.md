# Phase 9D — Stage 4: Framework Execution Report

**Date:** 2026-06-14  
**Script:** `scripts/phase9d/evaluate_framework.py`  
**Status:** ONE-SHOT COMPLETE — output frozen

**Framework output hash:** `e85e17b843d31b96a7bba0738747b7f4ed7c1b51e1bee4d628f33197b5b16aef`

---

## Framework Implementation

The current-velocity framework recovers ΔΩ from observed trajectories:

```
Given: x_A (150000×150), x_B (150000×150), A_obs (150×150)

Step 1: Sigma_A_hat = cov(x_A.T)          # (150, 150) empirical covariance
         Sigma_B_hat = cov(x_B.T)

Step 2: Q_A_hat = inv(Sigma_A_hat)         # precision matrices
         Q_B_hat = inv(Sigma_B_hat)

Step 3: D_A_hat_ii = -(A_obs Σ_A + Σ_A A_obs^T)_ii / 2   # Lyapunov residual
         D_B_hat_ii = -(A_obs Σ_B + Σ_B A_obs^T)_ii / 2

Step 4: DeltaOmega_hat = D_A_hat @ Q_A_hat - D_B_hat @ Q_B_hat
```

Scores for off-connectome pairs: `|DeltaOmega_hat[i,j]|` (symmetrized).

---

## Audit Layer Verification

| Check | Status |
|-------|--------|
| LC-1: No ground_truth module imported | PASS (grep confirms) |
| LC-2: Interface is evaluate_framework(x_A, x_B, A_obs) only | PASS |
| LC-3: x_A.shape = (150000, 150) — no z column | PASS |
| LC-4: Oracle older than trajectories (0.23 h gap) | PASS |
| One-shot run only | PASS |
| No tuning or parameter adjustment | PASS |

---

## Output Statistics

| Statistic | Value |
|-----------|-------|
| Output shape | (150, 150) |
| All finite | Yes |
| Min | −1.207 |
| Max | +1.986 |
| Mean |ΔΩ_hat| | 0.0277 |
| Std | 0.0545 |
| Execution time | 5.77 s |

---

## Hash Verification

| File | Hash (SHA-256) |
|------|----------------|
| framework_DeltaOmega.npy | e85e17b843d31b96... |
| Dataset used (master hash) | f4db4ca61e268578... |
| Oracle used (master hash) | 79c98d032742ba36... |

The framework output file was set read-only immediately after saving.

---

## Status

STAGE 4 COMPLETE. Framework run exactly once. Output frozen. Proceed to Stage 5.
