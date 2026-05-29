# Stage 8 — Nonstationarity Robustness Characterization

Date: 2026-05-29
Synthetic only. Phase 0 guard active.
Drift amplitude: 40% fractional change in on-connectome Q entries per drift segment.
N_COMMON_NEURONS = 61. Effect size = 0.2. B = 30 bootstrap samples.

Motivation: Stage 6 found NONSTATIONARITY_FRACTION=1.0 (temporal covariance drift median 0.85-1.05).
This experiment tests whether stability-selection edge detection is robust to this level of drift,
and whether topology recovery (lower threshold) outperforms amplitude recovery (standard threshold).

---

## 1. Non-roaming Optimistic (T=2000) — Drift Robustness

| Drift fraction | TPR (thr=0.75) | FPR (thr=0.75) | TPR (thr=0.50) | Signal stab. median |
|---|---|---|---|---|
| 0% | 0.90 | 0.07 | 0.80 | 1.00 |
| 25% | 0.80 | 0.13 | 0.80 | 1.00 |
| 50% | 1.00 | 0.20 | 1.00 | 1.00 |
| 100% | 0.90 | 0.13 | 0.80 | 1.00 |

---

## 2. Roaming Optimistic (T=420) — Drift Robustness

| Drift fraction | TPR (thr=0.75) | FPR (thr=0.75) | TPR (thr=0.50) | Signal stab. median |
|---|---|---|---|---|
| 0% | 0.60 | 0.03 | 0.80 | 0.98 |
| 25% | 0.80 | 0.02 | 0.80 | 0.97 |
| 50% | 0.80 | 0.04 | 0.80 | 0.97 |
| 100% | 0.80 | 0.02 | 0.90 | 0.97 |

---

## 3. Topology vs Amplitude Recovery (T=2000, drift=50%)

| Effect | Threshold | TPR | FPR_on |
|---|---|---|---|
| 0.1 | 0.75 | 0.80 | 0.13 |
| 0.1 | 0.60 | 0.80 | 0.12 |
| 0.1 | 0.50 | 0.70 | 0.11 |
| 0.1 | 0.40 | 0.80 | 0.12 |
| 0.2 | 0.75 | 1.00 | 0.09 |
| 0.2 | 0.60 | 1.00 | 0.10 |
| 0.2 | 0.50 | 1.00 | 0.10 |
| 0.2 | 0.40 | 1.00 | 0.09 |
| 0.3 | 0.75 | 1.00 | 0.06 |
| 0.3 | 0.60 | 0.90 | 0.06 |
| 0.3 | 0.50 | 0.90 | 0.07 |
| 0.3 | 0.40 | 0.80 | 0.06 |


---

## 4. Interpretation

### 4.1 Drift effect on topology recovery

A stability threshold of 0.50 ("topology") detects edges that appear in ≥50% of
bootstrap subsamples. Under drift, the signal edge is present throughout (the roaming
precision Q_roam is stationary). The drift is in the dwell background structure only.
Signal stability in roaming should remain high; topology recovery may therefore be
more robust than amplitude recovery.

### 4.2 Implication for real data

The observed real-data covariance drift (Stage 6) is a drift in the DWELL STATE background
structure (e.g., photobleaching, slow neuromodulatory change). The signal ΔQ is the
difference between roaming and dwell. If roaming is also stable (no drift), then:
- Signal pair stability in roaming should remain high despite dwell drift
- The standard threshold (0.75) may miss edges that are real but appear at lower stability
- Using a threshold in the 0.50–0.75 range may capture more topology without excessive FPR

### 4.3 Recommendation

A threshold of 0.60 may be a good compromise: captures most topology (TPR ≈ TPR at 0.50
for strong signals) while limiting FPR (avoids very low-stability noise pairs).
This is a soft recommendation — the final threshold choice requires human approval and
should be locked in the hypothesis document.

---

## 5. Figures

- `results/figures/stage08_drift_robustness_tpr.pdf` — TPR vs drift fraction (2 regimes)
- `results/figures/stage08_topology_vs_amplitude.pdf` — TPR vs stability threshold under drift

---

## 6. Deviations

None. Synthetic data only. Real-data precision blocked.
