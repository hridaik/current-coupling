# Stage 5 Covariance-Support Feasibility Audit

Date: 2026-05-28
Pipeline:
  EWMA tau = 20.0 s
  BEHAV_THRESHOLD = 0.284 (LOCKED)
  W_TRANS_SECONDS = 10.0 s (= 50 frames, approved 2026-05-28)
Recordings: 40 NeuroPAL

NOT computed:
  - Covariance, precision, DeltaQ, enrichment
  - Stationarity / variability analysis
  - n_eff (actual — this requires Stage 6 autocorrelation computation)
MIN_BOUT_SECONDS NOT set.

---

## 1. Retained Epoch Durations

### Roaming epochs (51 total, 25/40 animals with ≥1 epoch)

| Metric | Value |
|---|---|
| Median epoch duration | 16.0 s |
| Mean epoch duration | 23.6 s |
| p75 | 27.5 s |
| p90 | 50.8 s |
| p95 | 72.9 s |
| Max | 159.8 s |
| Fraction >= 10 s | 0.627 |
| Fraction >= 20 s | 0.451 |
| Fraction >= 30 s | 0.216 |
| Fraction >= 60 s | 0.078 |
| Animals with 0 epochs | 15/40 |

### Non-roaming epochs (102 total, 39/40 animals with ≥1 epoch)

| Metric | Value |
|---|---|
| Median epoch duration | 28.9 s |
| Mean epoch duration | 61.5 s |
| p75 | 75.0 s |
| p90 | 164.1 s |
| p95 | 267.1 s |
| Max | 323.0 s |
| Fraction >= 10 s | 0.765 |
| Fraction >= 20 s | 0.559 |
| Fraction >= 30 s | 0.500 |
| Fraction >= 60 s | 0.333 |
| Animals with 0 epochs | 1/40 |

---

## 2. Per-Animal Retained Time

| Metric | Roaming (s/animal) | Non-roaming (s/animal) |
|---|---|---|
| Median | 8 | 145 |
| Mean | 30 | 157 |
| IQR | [0, 49] | [43, 256] |
| Min | 0 | 0 |
| Max | 207 | 323 |
| Animals > 0 | 25/40 | 39/40 |

Per-animal epoch counts:
  Roaming:     median n_epochs = 1, min=0, max=4
  Non-roaming: median n_epochs = 2, min=0, max=6

---

## 3. Rough n_eff Heuristics (Descriptive — NOT Stage 6)

n_eff_rough ≈ T_retained / (2 × tau_int)

This is a rough bound. Actual n_eff requires cross-product autocorrelation
computation (Stage 6). N_COMMON_NEURONS = 61.

| tau_int guess | roam n_eff (med animal) | roam animals >= N (61) | nr n_eff (med animal) | nr animals >= N (61) |
|---|---|---|---|---|
|   5 s | 4 | 0/40 | 15 | 0/40 |
|  10 s | 2 | 0/40 | 8 | 0/40 |
|  20 s | 1 | 0/40 | 4 | 0/40 |


---

## 4. Covariance-Support Classification (tau_int = 10 s reference)

| Class | Roaming | Non-roaming | Criteria |
|---|---|---|---|
| adequate | 0/40 | 0/40 | n_eff >= 5 × N AND max_epoch >= 2 × W_TRANS |
| marginal | 0/40 | 0/40 | n_eff >= N but < 5 × N, OR max_epoch < 2 × W_TRANS |
| insufficient | 25/40 | 39/40 | n_eff < N |
| none | 15/40 | 1/40 | 0 retained frames |

---

## 5. Feasibility Assessment

### Roaming covariance estimation

25/40 animals have retained roaming epochs.
15/40 animals contribute zero roaming frames — these animals would be
excluded from roaming-state covariance and n_eff estimates.

At tau_int = 10 s (middle estimate):
  - Median n_eff_rough (animals with data): 2.0
  - n_eff_rough >= N_COMMON_NEURONS (61): 0 / 40 animals

**Conclusion (roaming)**: Marginally feasible — limited to animals with roaming epochs. Pooled n_eff across 25 contributing animals may be sufficient for a pooled covariance estimate.

### Non-roaming covariance estimation

39/40 animals have retained non-roaming epochs.
At tau_int = 10 s:
  - Median n_eff_rough: 7.6
  - n_eff_rough >= N (61): 0 / 40 animals

**Conclusion (non-roaming)**: Non-roaming has substantially more retained data and is feasible for covariance estimation in most animals.

---

## 6. Whether Additional Bout Filtering Appears Necessary

Setting a MIN_BOUT_SECONDS threshold would exclude short epochs before covariance
estimation. Based on the epoch distributions above:

| Candidate MIN_BOUT_SECONDS | Roaming epochs surviving | Non-roaming surviving |
|---|---|---|
| No filter | 51 (100%) | 102 (100%) |
| 10 s | 32 (63%) | 78 (76%) |
| 20 s | 23 (45%) | 57 (56%) |
| 30 s | 11 (22%) | 51 (50%) |
| 60 s | 4 (8%) | 34 (33%) |

Additional bout filtering (MIN_BOUT_SECONDS) is primarily useful for excluding
very short epochs that contribute noise but little signal to cross-product estimates.
Whether it is required depends on the actual tau_int measured in Stage 6.

Human decision required on MIN_BOUT_SECONDS. NOT set here.

---

## 7. Config Fields Updated This Step

| Field | Value | Status |
|---|---|---|
| W_TRANS_SECONDS | 10.0 | **Updated** (approved 2026-05-28) |
| BEHAV_THRESHOLD | 0.284 | LOCKED |
| EWMA_TIMESCALE_SECONDS | 20.0 | Provisional |
| MIN_BOUT_SECONDS | None | NOT SET |

---

## 8. Figures

- `results/figures/stage05_covsupport_epochs.pdf` — epoch duration distributions for roaming and non-roaming
- `results/figures/stage05_covsupport_per_animal.pdf` — per-animal retained time and epoch count

---

## 9. Deviations

No deviations. Threshold, EWMA, and W_TRANS applied as approved.
MIN_BOUT_SECONDS not set.
