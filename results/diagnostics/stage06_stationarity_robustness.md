# Stage 6 Stationarity Robustness Audit

Date: 2026-05-28
Pipeline: EWMA=20s, threshold=0.284, W_TRANS=10s, MIN_BOUT=10s
Neural coordinate: gcamp/trace_array (z-scored)
n_perms (null split): 10
Animals assessed (≥ 120s retained): 26 animal-state pairs

Phase-0 compliance:
  - Covariance computed ONLY for stationarity diagnostics
  - No precision matrix, DeltaQ, enrichment, or estimator computed

---

## 1. Non-roaming

n assessed = 23

| Metric | Median | p25 | p75 |
|---|---|---|---|
| temporal drift | 0.853 | 0.842 | 0.923 |
| null drift (random split) | 0.215 | 0.196 | 0.245 |
| drift excess (temporal − null) | 0.655 | 0.589 | 0.686 |
| support ratio (T_half/N) | 4.45 | 3.06 | 5.59 |

Pairs with excess > 0.05 (evidence for temporal effect): 23/23

**Quartile comparison by support ratio (T_half/N):**

| Support tier | n | Median temporal drift | Median null drift |
|---|---|---|---|
| Low support (bottom half) | 11 | 0.905 | 0.249 |
| High support (top half) | 12 | 0.850 | 0.199 |


---

## 2. Roaming

n assessed = 3

| Metric | Median | p25 | p75 |
|---|---|---|---|
| temporal drift | 1.048 | 1.029 | 1.106 |
| null drift (random split) | 0.209 | 0.201 | 0.219 |
| drift excess (temporal − null) | 0.820 | 0.810 | 0.896 |
| support ratio (T_half/N) | 3.57 | 2.87 | 3.87 |

Pairs with excess > 0.05 (evidence for temporal effect): 3/3

**Quartile comparison by support ratio (T_half/N):**

| Support tier | n | Median temporal drift | Median null drift |
|---|---|---|---|
| Low support (bottom half) | 1 | 1.009 | 0.209 |
| High support (top half) | 2 | 1.106 | 0.211 |


---

## 3. Overall Assessment

### 3.1 Temporal drift vs null drift

| Metric | All pairs (n=26) |
|---|---|
| Median temporal drift | 0.891 |
| Median null drift (random split) | 0.214 |
| Median drift excess (temporal − null) | 0.666 |
| Pairs with excess > 0.05 | 26/26 |

**Key diagnostic**: If temporal drift ≈ null drift, the first/second-half
Frobenius distance is entirely explained by sampling noise with no temporal
structure required. If temporal drift >> null drift, there is evidence that
covariance shifts over time within the behavioral state.

### 3.2 Drift vs sample support

Pearson r(temporal_drift, T_half/N) = -0.162

A negative correlation means drift decreases as sample support increases,
consistent with a sampling-noise dominant model (more data → better-estimated
covariance → smaller apparent drift). A near-zero or positive correlation
suggests a signal component independent of sample size.

### 3.3 Drift excess vs ill-conditioning

Pearson r(drift_excess, log10(κ)) for non-roaming: -0.572

If drift excess (temporal − null) is UNCORRELATED with κ, the excess is not
explained by ill-conditioning alone and may reflect true temporal structure.
If strongly correlated, both temporal and null drift are driven by the same
conditioning regime.

---

## 4. Interpretation

**MIXED SIGNAL**: 26/26 pairs have excess > 0.20, suggesting some temporal structure beyond sampling noise. Further investigation recommended before Stage 7.

Support-drift correlation r = -0.162 (not clearly negative), suggesting the drift may not purely decrease with sample size. Weak temporal structure cannot be ruled out.

---

## 5. Whether Stage 7 Appears Justified

**Caution: stage 7 should proceed but flag stationarity concern.**

Median drift excess = 0.666. Some temporal structure beyond sampling noise cannot be excluded. Stage 7 should include stationarity sensitivity checks. Document this in DEVIATIONS.md if proceeding without further diagnostic.

---

## 6. Figures

- `results/figures/stage06_stationary_null_scatter.pdf` — temporal vs null drift
- `results/figures/stage06_drift_vs_support.pdf` — temporal drift vs T_half/N
- `results/figures/stage06_drift_vs_kappa.pdf` — drift excess vs log10(κ)

---

## 7. Deviations

None. No thresholds, EWMA, or segmentation parameters changed.
