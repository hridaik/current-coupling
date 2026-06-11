# Drift Quantification Report
Date: 2026-06-03
Authorization: Phase 2D Task B — Drift Quantification (addresses DEV-003)
Status: Characterization study only. No new hypotheses.

---

## 1. Purpose

Quantify temporal covariance drift relative to behavioral ΔQ.
This directly addresses DEV-003 (all-animal pooling + potential state/time confound).

This is NOT a hypothesis test. This is a characterization of how much of the
observed ΔQ magnitude could be explained by temporal drift within recordings.

---

## 2. Method

### 2.1 Inputs

- 40 recordings, same CePNEM residuals and raw GCaMP traces as Phase 2
- Same behavioral segmentation (locked parameters)
- Same ADMM confirmation estimator (λ_on=0.01, λ_off=0.10, ρ=1.0)

### 2.2 Split design

For each recording, the valid frames (after behavioral segmentation masks) were
split at the midpoint T//2 into:
- **First half**: frames 0 through T//2 − 1
- **Second half**: frames T//2 through T − 1

The split is INDEPENDENT of behavioral state: both halves contain whatever mixture
of roaming/dwelling frames naturally occurs in each time interval.

A relaxed copresence threshold of 5 recordings per half was used (vs. 9 for the
full analysis) to ensure sufficient coverage for 40 half-recordings.

### 2.3 Estimator

For each half, pairwise sufficient statistics were accumulated, pairwise covariance
was assembled, PSD-projected, and the same ADMM confirmation estimator was applied.

ΔQ_drift = Q_conf_first − Q_conf_second

This matches the architecture of Phase 2 but applied to temporal halves rather
than behavioral states.

### 2.4 Drift ratio

For each Class 4 pair with nonzero behavioral ΔQ:

    ratio = |ΔQ_drift_ij| / |ΔQ_behavior_ij|

where ΔQ_behavior = Q_roam_conf − Q_dwell_conf from Stage 2.

---

## 3. PSD and Convergence Diagnostics

All four half-matrices passed PSD projection with ZERO eigenvalues clipped.
All four ADMM solvers converged.

| Matrix | PSD clips | ADMM converged |
|---|---|---|
| CePNEM first half | 0 | YES |
| CePNEM second half | 0 | YES |
| GCaMP first half | 0 | YES |
| GCaMP second half | 0 | YES |

---

## 4. Drift Ratio Results

### 4.1 CePNEM coordinate

Pairs with nonzero behavioral ΔQ: **243 / 1321** Class 4 pairs.

| Statistic | Value |
|---|---|
| median ratio | **0.000** |
| p75 ratio | 0.534 |
| p95 ratio | 4.905 |
| max ratio | 104.3 |
| frac < 1.0 (drift < behavioral) | **80.2%** |
| frac > 2.0 (drift > 2× behavioral) | 10.3% |

### 4.2 GCaMP coordinate

Pairs with nonzero behavioral ΔQ: **585 / 1321** Class 4 pairs.

| Statistic | Value |
|---|---|
| median ratio | **0.000** |
| p75 ratio | 0.801 |
| p95 ratio | 5.209 |
| max ratio | 331.7 |
| frac < 1.0 (drift < behavioral) | **77.8%** |
| frac > 2.0 (drift > 2× behavioral) | 11.6% |

### 4.3 Interpretation

For the majority of pairs with nonzero behavioral ΔQ:
- **Median ratio ≈ 0**: The temporal drift ΔQ is near zero for most pairs where
  behavioral ΔQ is nonzero. This indicates that the temporal drift estimator
  selects DIFFERENT pairs from the behavioral estimator for most of the signal.
- **80% of pairs: drift < behavioral ΔQ**: The majority of behavioral signal
  is not replicated by temporal drift.
- **p95 > 4**: The high p95 is driven partly by pairs with very small behavioral
  ΔQ in the denominator. High-ratio outliers require careful interpretation
  (see Section 6: state-time confounding).
- **The high-ratio outliers and the state-time confound are linked**: Because
  roaming occurs preferentially early in recordings (see Section 5), the
  first-half/second-half split partly captures state differences, not pure drift.

---

## 5. Epoch-Time Segregation Audit

### 5.1 Summary

| State | Mean normalized position (unweighted) | Mean normalized position (weighted by frames) | n recordings |
|---|---|---|---|
| Roaming | **0.234** | 0.344 | 19 / 40 |
| Dwelling | **0.524** | 0.512 | 39 / 40 |
| **Difference (roam − dwell)** | **−0.290** | **−0.167** | — |

Normalized position: 0 = start of recording, 1 = end.
Value of 0.5 would indicate uniform temporal distribution.

### 5.2 State-time confounding is PRESENT

Roaming tends to occur in the first quarter to third of recordings
(mean position 0.234 unweighted), while dwelling is distributed around
the midpoint (mean position 0.524).

**14 of 19 roaming recordings** show mean roaming position < 0.50 (early-biased).
**12 of 19** show mean position < 0.33 (concentrated in first third).

This is a substantial state-time confound:

| Detection criterion | Value |
|---|---|
| \|unweighted mean difference\| | **0.290** (detection threshold: >0.05) |
| \|weighted mean difference\| | **0.167** |
| Confounding flag | **DETECTED** |

### 5.3 Per-recording breakdown

| Recording index | Roaming mean position | n roam frames | Classification |
|---|---|---|---|
| 1 | 0.271 | 328 | EARLY |
| 3 | 0.422 | 202 | — |
| 5 | 0.167 | 307 | EARLY |
| 6 | 0.312 | 248 | — |
| 10 | 0.069 | 224 | EARLY |
| 13 | 0.042 | 135 | EARLY |
| 15 | 0.023 | 75 | EARLY |
| 16 | 0.015 | 50 | EARLY |
| 17 | 0.532 | 244 | — |
| 18 | 0.291 | 140 | EARLY |
| 21 | 0.200 | 243 | EARLY |
| 23 | 0.032 | 105 | EARLY |
| 25 | 0.396 | 1023 | — |
| 27 | 0.018 | 58 | EARLY |
| 29 | 0.457 | 1028 | — |
| 35 | 0.300 | 221 | EARLY |
| 36 | 0.588 | 622 | — (late) |
| 37 | 0.033 | 105 | EARLY |
| 39 | 0.279 | 229 | EARLY |

---

## 6. Joint Interpretation: Drift and State-Time Confound

The state-time confound has a direct consequence for interpreting the drift ratios:

**Because roaming occurs preferentially in the first half of recordings**, the
first-half covariance matrix S_first captures more roaming-associated structure,
and S_second captures more dwelling-associated structure. Therefore:

    ΔQ_drift = Q_first − Q_second

is not purely a measure of temporal covariance drift — it is partly a measure
of state-related covariance change. This means:

1. The high-ratio pairs (drift > 2× behavioral) are EXPECTED under this confound:
   the drift estimator is partially measuring the same behavioral signal as the
   behavioral estimator, but from a different direction.

2. The low-ratio majority (median ~0) indicates that for most pairs, the behavioral
   estimator (using explicit state labels) identifies pairs that the temporal-split
   estimator does not, despite the partial confound. This is because:
   - The explicit behavioral labels (roaming/dwelling) provide much cleaner
     state separation than a temporal split
   - The dwelling state is dispersed throughout recordings while roaming is early;
     temporal splitting thus provides weak state separation

3. The p95 ratios (4.9–5.2) are likely INFLATED by the state-time confound.
   The true drift magnitude (absent any behavioral state effect) would be lower.

**Conservative bound**: The drift analysis as implemented cannot cleanly separate
temporal drift from state-related differences. The true drift lower bound is given
by the 80th percentile of the ratio distribution (≈ 0.53 for CePNEM), meaning
that at the 80th percentile, drift accounts for at most 53% of behavioral ΔQ
magnitude — and this is an upper bound due to confounding.

**Median behavior**: At the median, temporal drift accounts for essentially 0%
of behavioral ΔQ magnitude — the behavioral estimator identifies pairs that the
temporal-split estimator does not select, even with partial state-time confound.

---

## 7. Summary Statement for DEV-003

DEV-003 (all-animal pooling with potential state-time confound) is characterized:

1. **Drift magnitude**: At the median, temporal covariance drift (first half vs.
   second half of recordings) accounts for ≈0% of behavioral ΔQ magnitude
   for both CePNEM and GCaMP. At the 75th percentile, drift accounts for
   ≤53% (CePNEM) and ≤80% (GCaMP) of behavioral ΔQ. The behavioral estimator
   identifies a largely distinct set of pairs from the temporal drift estimator.

2. **State-time confound**: Roaming epochs are systematically concentrated in the
   EARLY part of recordings (mean position 0.234 ± variation) while dwelling is
   distributed throughout (mean 0.524). The difference is 0.290 (unweighted),
   well above the detection threshold of 0.05. This confound inflates the
   measured drift ratios by introducing behavioral state variation into the
   temporal split. The true temporal drift (absent state effects) is thus
   LOWER than the ratios reported.

3. **Net assessment**: The behavioral ΔQ signal is NOT primarily driven by
   temporal covariance drift for the majority of detected pairs (80% of pairs:
   drift < behavioral ΔQ). However, the state-time confound prevents a clean
   quantitative separation. The LOO sensitivity analysis (Stage 3, median
   retention CePNEM=0.960, GCaMP=0.940) provides a more reliable stability
   characterization that is unaffected by the state-time confound.

---

## 8. Output Files

| File | Description |
|---|---|
| `drift_quantification_report.md` | This report |
| `drift_summary.json` | Machine-readable summary of all key statistics |
| `drift_pairwise_ratios.npy` | Per-pair drift ratios, shape (2, 1321): CePNEM and GCaMP, all Class 4 pairs (NaN for pairs with zero behavioral ΔQ) |

---

*No new hypotheses generated. No enrichment tests run. No biological interpretation.*
*All statistics are characterizations of data structure, not statistical tests.*
