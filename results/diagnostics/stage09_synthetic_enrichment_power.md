# Stage 9 — Synthetic Enrichment Power Analysis

Date: 2026-05-29
Synthetic only. No real-data ΔQ or enrichment. Phase 0 guard active.

## Setup

| Parameter | Value |
|---|---|
| N_total_off_connectome | 1464 |
| N_annotated (peptide) | 88 |
| Annotation fraction | 6.0% |
| OR values tested | [1.5, 2.0, 3.0, 5.0] |
| K values (Fisher) | [10, 20, 50] |
| n_sim | 200 |
| α | 0.05 |

Support regime → noise level calibration:

| Regime | noise_level | Empirical basis | Approx TPR proxy |
|---|---|---|---|
| non_roaming_optimistic | 0.4 | T_pooled≈6280 (Stage 6) | ~0.89 |
| roaming_pooled_25animals | 0.7 | T_pooled≈1000 (Stage 8) | ~0.76 |
| roaming_conservative | 1.5 | T_pooled≈400 (Stage 8 boundary) | ~0.63 |
| roaming_failed | 3.0 | T_pooled≈60 (Stage 7 failure) | ~0.56 |

The noise level controls the signal-to-noise of the |ΔQ| ranking. Neuropeptide
pairs receive a boost of log(OR)/noise_level over random pairs.

---

## 1. AUROC Power (primary enrichment statistic)

Power = fraction of 200 simulations where AUROC p < 0.05 (Mann-Whitney one-sided).

| Regime | noise_level | OR=1.5 | OR=2.0 | OR=3.0 | OR=5.0 |
|---|---|---|---|---|---|
| non_roaming_optimistic | 0.4 | **1.00** | **1.00** | **1.00** | **1.00** |
| roaming_pooled_25animals | 0.7 | **1.00** | **1.00** | **1.00** | **1.00** |
| roaming_conservative | 1.5 | **0.78** | **1.00** | **1.00** | **1.00** |
| roaming_failed | 3.0 | 0.36 | **0.67** | **0.94** | **1.00** |

**Bold** entries = power ≥ 0.6 (minimum viable threshold).

---

## 2. Fisher Top-K Power (secondary enrichment statistic, K=20)

Power = fraction of 200 simulations where Fisher exact p < 0.05.

| Regime | OR=1.5 | OR=2.0 | OR=3.0 | OR=5.0 |
|---|---|---|---|---|
| non_roaming_optimistic | **0.98** | **1.00** | **1.00** | **1.00** |
| roaming_pooled_25animals | **0.60** | **0.99** | **1.00** | **1.00** |
| roaming_conservative | 0.12 | 0.41 | **0.83** | **0.99** |
| roaming_failed | 0.09 | 0.17 | 0.23 | 0.49 |

---

## 3. Fisher Power vs K at Moderate OR=2

| K | non_roaming_opt | roaming_pooled | roaming_cons | roaming_failed |
|---|---|---|---|---|
| 10 | 1.00 | 0.86 | 0.26 | 0.09 |
| 20 | 1.00 | 0.99 | 0.41 | 0.17 |
| 50 | 1.00 | 1.00 | 0.52 | 0.12 |

---

## 4. Null Model Calibration (AUROC power, noise_level=0.7)

50 trials, 200 permutations per null.
At OR=1 (H0): expected power ≈ α = 0.05.
At OR>1 (H1): higher power = better null.

| OR | Simple permutation | Degree-stratified |
|---|---|---|
| OR=1.0 | 0.04 | 0.02 |
| OR=2.0 | 1.00 | 1.00 |
| OR=3.0 | 1.00 | 1.00 |

**Recommended NULL_MODEL_PRIMARY: simple_permutation (equivalent power, lower computational cost)**

---

## 5. AUROC vs Fisher: Robustness Comparison

| Regime | OR | AUROC power | Best Fisher power (over K) |
|---|---|---|---|
| non_roaming_optimistic | 2.0 | 1.00 | 1.00 |
| roaming_pooled_25animals | 2.0 | 1.00 | 1.00 |

AUROC appears more robust (higher power at marginal regime).

---

## 6. Whether Pooled Roaming Support Remains Sufficient

At roaming_pooled_25animals (noise_level=0.7):
  AUROC power at OR=2.0: 1.00
  AUROC power at OR=3.0: 1.00
  AUROC power at OR=5.0: 1.00

**Roaming pooled: SUFFICIENT for OR≥2.0 (power≥0.6 at roaming_pooled_25animals).**

At non_roaming_optimistic (noise_level=0.4):
  AUROC power at OR=2.0: 1.00
**Non-roaming: WELL-POWERED at OR=2.0.**

---

## 7. ENRICHMENT_POWER_AT_OR2

ENRICHMENT_POWER_AT_OR2 (non-roaming, primary regime) = 1.000

≥ 0.6: meets minimum viable threshold.

---

## 8. Config Fields Updated

| Field | Value |
|---|---|
| LAMBDA_ON | 0.04 (approved 2026-05-29) |
| LAMBDA_OFF | 0.45 (approved 2026-05-29) |
| LAMBDA_OFF_ON_RATIO | 11.25 |
| ENRICHMENT_POWER_AT_OR2 | 1.000 (set this stage) |
| NULL_MODEL_PRIMARY | simple_permutation (recommended; human decision required) |

---

## 9. Figures

- `results/figures/stage09_power_curves.pdf` — power vs OR (AUROC) and vs K (Fisher)
- `results/figures/stage09_null_calibration.pdf` — null model comparison

---

## 10. Deviations

None. Synthetic data only. Real-data precision and enrichment blocked.
