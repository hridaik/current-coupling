# Phase 9D — Stage 1: Simulator Validation

**Date:** 2026-06-14  
**Script:** `scripts/phase9d/simulator.py`  
**Status:** ALL ACCEPTANCE TESTS PASS

---

## Simulator Design

Euler-Maruyama SDE integration:

```
x(t + Δt) = x(t) + A_full @ x(t) × Δt + sqrt(2D × Δt) × ε_t
ε_t ~ N(0, I_N_TOTAL)
```

- `A_full` loaded from oracle `A_full.npy` (180×180, hash-verified)
- `D_diag` loaded from oracle `D_A_diag.npy` / `D_B_diag.npy`
- Δt = 0.01, burn-in = 10,000 steps discarded per trajectory
- Output shape: (T_steps, N_OBS) = (150,000 × 150) — no z column (LC-3)
- Seeds: x_A=100, x_B=200, x_A_lesion=300

---

## Structural Lesion Construction

Lesion = A_full with all directed edges A_lesioned[M2_i, M1_j] zeroed.  
M1→M2 edges removed: **24 edges**.  
M2→M1 edges preserved.  
PMC relay path (PMC_SRC → HG → PMC_TGT) is **not disrupted** by this lesion.

---

## Acceptance Tests

| Test | Description | Result |
|------|-------------|--------|
| AT-3 | x_A.shape == (150000, 150) | PASS |
| AT-3 | x_B.shape == (150000, 150) | PASS |
| AT-3 | x_A_lesion.shape == (150000, 150) | PASS |
| AT-3 | No z column (LC-3 compliant) | PASS |
| AT-3b | State A stationarity (mean/var stability) | PASS |
| AT-3b | State B stationarity | PASS |
| AT-3b | State A lesion stationarity | PASS |
| AT-3c | PMC_SRC var ratio A/B = **4.89×** (> 1.0) | PASS |
| AT-3c | Background var ratio A/B = **1.02×** (≈ 1.0) | PASS |
| AT-3d | Empirical Sigma_A min eigenvalue = **0.4658** (> 0) | PASS |
| LC-4 | Oracle created **0.23h** before trajectories | PASS |

---

## Key Statistics

| Quantity | Value |
|----------|-------|
| PMC_SRC variance ratio (State A / State B) | 4.891× |
| Background variance ratio (State A / State B) | 1.024× |
| Empirical Sigma_A min eigenvalue | 0.4658 |
| Oracle creation → trajectory gap | 0.23 h |

The 4.89× PMC_SRC variance amplification in State A (driven by D_SRC_A = 5.0 vs D_BASE = 1.0) confirms that the state modulation is correctly reflected in the observed data.

---

## LC-3 Verification

```
x_A.shape  = (150000, 150)  ← N_OBS = 150, no z column
x_B.shape  = (150000, 150)
```

The simulator writes only `x[:N_OBS]` at each timestep; hidden HG neurons (indices 150–179) are never written to any output file.

---

## Status

STAGE 1 COMPLETE. Simulator validated. Proceed to Stage 2.
