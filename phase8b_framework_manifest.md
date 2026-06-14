# Phase 8B Framework Manifest

**Date**: 2026-06-13

---

## Framework Identity

| Field | Value |
|-------|-------|
| Framework name | current_velocity_v1 |
| Framework version | Phase 8B first blinded evaluation |
| Implementation file | `scripts/phase8b_framework.py` |
| Git commit (at time of execution) | `b6117b238f510109f3b964d07c60bd9b2c6d3ddc` |

---

## Execution Command

```
python scripts/phase8b_framework.py
python -m scripts.phase8.harness --condition oracle_z --output framework_output.json
```

---

## Framework Hyperparameters (frozen before output generation)

| Parameter | Value |
|-----------|-------|
| TEMPERATURE | 5.0 |
| KAPPA (current weight in S-score) | 0.3 |
| RIDGE (Tikhonov regularization) | 1e-3 |
| N_RUNS | 5 |
| CONDITION | oracle_z |

---

## Framework Output

| Field | Value |
|-------|-------|
| Output file | `framework_output.json` |
| SHA-256 | `e71364e2ef3fdc7a764cb5e888efdefd42c492ca51cd77bc5a90a2b104ef7034` |
| File size | 1,556,545 bytes |
| Pairs scored | 9900 |
| Predicted class S | 9612 |
| Predicted class C | 288 |
| Predicted class M | 0 |
| Predicted class N | 0 |

---

## Method Summary

For oracle_z condition (y(t) and z_oracle(t) available):

1. Regress z_oracle out of each neuron's activity: `y_resid = y - outer(z, beta)`
2. Compute unconditional precision matrix `Omega_raw = inv(Cov(y) + ridge*I)`
3. Compute z-conditioned precision matrix `Omega_cond = inv(Cov(y_resid) + ridge*I)`
4. Convert to partial correlation: `PCor[i,j] = -Omega[i,j] / sqrt(Omega[ii]*Omega[jj])`
5. Compute `Delta_PCor = |PCor_raw - PCor_cond|` (z-mediated change)
6. Compute lag-1 cross-correlation asymmetry: `Current_norm[j,i] = (C1_cond[j,i] - C1_cond[i,j]) / (std_i * std_j)` (directed causal signal, z-conditioned)
7. For directed pair (i→j):
   - S-score = `|PCor_cond[i,j]| + 0.3 * max(0, Current_norm[j,i])`
   - C-score = `Delta_PCor[i,j]`
   - M-score = `2 * S * C / (S + C)` (harmonic mean)
   - N-score = 0
   - Apply softmax(scores * 5.0) → class_prob

---

## Runtime Environment

| Field | Value |
|-------|-------|
| Python | 3.12 (.venv) |
| numpy | installed |
| scipy | installed |
| sklearn | installed |
| Platform | Linux WSL2 |

---

## Audit Hash

Framework output hash recorded in evaluation_audit.jsonl at timestamp_unix 1781349477.

Verdict hash: `5f47a4020622157fee19d76b9e02995222948812b9d6747cec845d5acd21d31f`
