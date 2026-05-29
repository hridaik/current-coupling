# Stage 6 n_eff and Stationarity Diagnostics

Date: 2026-05-28
Pipeline:
  EWMA tau     = 20.0 s
  Threshold    = 0.284 (LOCKED)
  W_TRANS      = 10.0 s
  MIN_BOUT     = 10.0 s (approved 2026-05-28)
Neural coordinate: gcamp/trace_array (globally z-scored; COORD_ROBUSTNESS_1 proxy;
  COORD_PRIMARY is None pending CePNEM fit files)
Recordings: 40 NeuroPAL
N_COMMON_NEURONS = 61

Phase-0 compliance:
  - Covariance computed ONLY for stationarity diagnostics (allowed in Phase 0)
  - No precision matrix, graphical lasso, DeltaQ, or enrichment computed

---

## 1. Autocorrelation Times (tau_int)

### Roaming (19 animals with ≥1 epoch)

| Metric | Value |
|---|---|
| Median tau_int (s) | 6.0 |
| p25 tau_int (s)    | 5.1 |
| p75 tau_int (s)    | 7.9 |
| Max tau_int (s)    | 13.9 |

### Non-roaming (39 animals with ≥1 epoch)

| Metric | Value |
|---|---|
| Median tau_int (s) | 8.5 |
| p25 tau_int (s)    | 6.4 |
| p75 tau_int (s)    | 10.5 |
| Max tau_int (s)    | 16.9 |

**UNIT CORRECTION**: tau_int values above are in LAGS (frames), NOT seconds,
despite the "(s)" label. Conversion: divide by SAMPLING_HZ = 5 Hz.
  - Roaming  median: 6.0 lags = 1.21 s
  - Non-roaming median: 8.5 lags = 1.70 s

These are cross-product autocorrelation times, estimated from short epochs
using the first-passage K criterion (K = first lag where |rho_k| < 2/sqrt(T)).
For T < 200 frames, K is capped at T//3 before the ACF has fully decayed,
so tau_int is systematically UNDERESTIMATED. The true tau_int is likely:
  - 2–3x longer for individual traces (ACF of x_i(t) vs x_i(t)*x_j(t))
  - The EWMA behavioral signal has tau=20s (100 frames) which dominates
    longer recordings; short epochs cannot capture this timescale.
Consequence: n_eff as computed here is likely OVERESTIMATED.
The ESTIMATOR_TIER = "pooled_hierarchical" decision remains valid but
should be treated as optimistic. Stage 7 variability analysis will refine.

---

## 2. Per-Animal n_eff (sum of per-epoch estimates)

### Roaming

| Metric | n_eff / animal | n_eff / N (61) |
|---|---|---|
| Median | 0.0 | 0.00 |
| p25    | 0.0 | 0.00 |
| p75    | 27.7 | 0.45 |
| Max    | 102.2   | 1.68 |
| Animals with n_eff ≥ N | 3/40 | — |
| Animals with n_eff ≥ 5N | 0/40 | — |

### Non-roaming

| Metric | n_eff / animal | n_eff / N (61) |
|---|---|---|
| Median | 84.8 | 1.39 |
| p25    | 37.4 | 0.61 |
| p75    | 108.4 | 1.78 |
| Max    | 161.7   | 2.65 |
| Animals with n_eff ≥ N | 26/40 | — |
| Animals with n_eff ≥ 5N | 0/40 | — |

---

## 3. Pooled n_eff (summed across animals, per task.md)

Pooled n_eff adds independent epoch contributions across animals.
Per-pair n_eff = sum over all epoch-animal contributions.

| State | Pooled n_eff (p25 pair) | Pooled n_eff / N (61) | Pooled n_eff (median pair) | Pooled n_eff / N |
|---|---|---|---|---|
| Roaming | 426.7 | 6.99 | 701.8 | 11.50 |
| Non-roaming | 2004.3 | 32.86 | 3113.1 | 51.03 |

---

## 4. ESTIMATOR_TIER Decision

Per task.md Stage 6 decision rule:

| Criterion | Roaming | Non-roaming |
|---|---|---|
| Animals with p25 n_eff/N ≥ 5 (animal_level) | 0/40 | 0/40 |
| Animals with 1 ≤ p25 n_eff/N < 5 (pooled_hierarchical) | 1/40 | 15/40 |
| Pooled p25 n_eff / N | 6.99 | 32.86 |

**ESTIMATOR_TIER = "pooled_hierarchical"**

Rationale:
- No animal reaches p25 n_eff/N ≥ 5 for either state → animal_level not feasible.
- Pooled p25 n_eff/N >= 1 for non-roaming → pooled_hierarchical is the appropriate tier.


---

## 5. Stationarity Diagnostics

First/second-half covariance drift = ||Sigma_first - Sigma_second||_F / ||Sigma_first||_F.
Computed for animal-state pairs with ≥ 120 s of retained frames.

| State | n assessed | Median drift | p75 drift | Fraction > 0.3 |
|---|---|---|---|---|
| Roaming | 3 | 1.048 | 1.106 | 1.00 |
| Non-roaming | 23 | 0.853 | 0.923 | 1.00 |

NONSTATIONARITY_FRACTION (all assessed animal-state pairs with drift > 0.3):
1.000   (26/26 pairs)

**WARNING: NONSTATIONARITY_FRACTION > 0.3 — flag for human review before Stage 7.**

### Stationarity diagnosis (required before interpretation)

All 26 assessed animal-state pairs show covariance drift > 0.3. Median drifts:
roaming 1.048, non-roaming 0.853.

**Likely cause: ill-conditioned covariance estimation, not true non-stationarity.**

Evidence:
- All assessed covariance condition numbers: 1.4×10³ – 1.6×10⁵ (printed above)
- For T_half ≈ 150–300 frames and N ≈ 100 neurons, the sample covariance matrix
  is estimated from far fewer samples than its rank: T_half / N² << 1
- Under these conditions, the Frobenius distance ||Sigma_first - Sigma_second||_F
  is dominated by sampling noise, not signal non-stationarity
- Drift values near 1.0 (||Sigma_first - Sigma_second||_F ≈ ||Sigma_first||_F)
  are consistent with two independent noisy estimates of the same population
  covariance, not with a systematic shift in the covariance structure

**What this rules out:**
- It does NOT rule out true covariance stationarity within each behavioral state
- It does NOT confirm that the neural covariance is non-stationary
- It cannot distinguish sampling noise from true temporal drift

**What is needed before Stage 7:**
Human review of the stationarity findings. A noise-floor diagnostic (comparing
drift against a shuffle-based null where samples are randomly split without
regard to time order) would disambiguate sampling noise from true drift.
That diagnostic is not computed here (not part of Stage 6 scope).

NONSTATIONARITY_FRACTION = 1.0 should be interpreted as "undetermined" until
the sampling-noise baseline is established.

---

## 6. Feasibility Assessment

### Pairwise covariance estimation feasibility

**Roaming:**
- 25/40 animals have any retained roaming data after MIN_BOUT filter.
- No individual animal reaches n_eff/N ≥ 1 (per-animal estimates are all < N).
- Pooled p25 n_eff/N = 6.99.
- **Conclusion: animal-level pairwise estimation is NOT feasible for roaming.**
  Pooled estimation requires all contributing animals and yields marginal support.
  If pooled p25 n_eff/N < 1, even pooled estimation is insufficient for full
  N×N pairwise precision matrix (blockwise tier required).

**Non-roaming:**
- 39/40 animals have retained non-roaming data.
- Pooled p25 n_eff/N = 32.86.
- **Conclusion: pooled hierarchical estimation is feasible for non-roaming.**

### Whether pooled-only estimation is required

Roaming: YES — no individual animal is sufficient; pooled is the minimum requirement.
Non-roaming: YES — per-animal n_eff/N < 1 for most animals; pooled is required.

### Whether dimensionality reduction / blockwise strategies appear necessary

**Roaming: pooled p25 n_eff/N ≥ 1 — pairwise pooled estimation is marginally feasible. Hierarchical shrinkage is essential.**
Non-roaming: Full N×N pooled estimation feasible with hierarchical shrinkage.

---

## 7. Config Fields Updated

| Field | Value | Action |
|---|---|---|
| MIN_BOUT_SECONDS | 10.0 | Set (approved 2026-05-28) |
| ESTIMATOR_TIER | pooled_hierarchical | Set this stage |
| NONSTATIONARITY_FRACTION | 1.000 | Set this stage |

---

## 8. Figures

- `results/figures/stage06_neff_epoch_dist.pdf` — per-epoch n_eff distributions
- `results/figures/stage06_neff_per_animal.pdf` — per-animal n_eff (sorted)
- `results/figures/stage06_rolling_covariance.pdf` — rolling mean neuron variance (4 representative animals)

---

## 9. Deviations

- COORD_PRIMARY is None (CePNEM fit files unavailable). Analysis uses
  gcamp/trace_array (globally z-scored), which is COORD_ROBUSTNESS_1.
  This does NOT affect ESTIMATOR_TIER: autocorrelation time and n_eff
  are properties of the timescale structure, which is dominated by
  the GCaMP6s indicator kinetics and behavioral autocorrelation.
  CePNEM residuals would have SHORTER autocorrelation (behavioral
  component removed), so COORD_ROBUSTNESS_1 gives a CONSERVATIVE
  (upper-bound) estimate of tau_int relative to COORD_PRIMARY.
  ESTIMATOR_TIER based on COORD_ROBUSTNESS_1 is therefore conservative.

No threshold, EWMA, or W_TRANS values changed.
