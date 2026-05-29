# SUPERVISOR_HANDOFF_STAGE5.md

## Current Stage

Stage 5 behavioral segmentation / covariance-support feasibility.

Do NOT begin Stage 6.

---

# Hard Phase 0 Prohibitions

Still forbidden:

* real-data precision matrices
* graphical lasso on real data
* ΔQ
* `D_C ΔQ`
* `Ω_s`
* enrichment
* state-conditioned covariance estimation
* current-velocity statistics
* neural-informed behavioral threshold optimization

`PHASE0_COMPLETE = False`

Guardrails in:

* `src/estimators.py`

---

# Locked Methodological Decisions

## Harmonization

```python id="6n9kyl"
LR_POLICY = "separate"

IDENTITY_CONFIDENCE_THRESHOLD = 2.5

N_COMMON_NEURONS = 61
N_RANDI_SUBGRAPH_NEURONS = 60
N_CREAMER_SUBGRAPH_NEURONS = 56
```

No:

* AWCON↔AWCL mapping
* AWCOFF↔AWCR mapping

Anatomical, functional-pair, and Creamer spaces remain distinct.

---

# Locked Pair Definition

```python id="6eixv6"
RANDI_WT_Q_THRESHOLD = 0.05
RANDI_AMPLITUDE_GATE_DFF = None
N_RANDI_SUBGRAPH_PAIRS = 189
```

Amplitude gate intentionally excluded.

---

# Locked Behavioral Decisions

```python id="0l0yv3"
BEHAVIOR_SCORE_SOURCE = "velocity_s"

BEHAV_THRESHOLD = 0.284

BEHAV_THRESHOLD_RULE = (
    "pooled_velocity_s_kde_trough_between_dwelling_and_roaming"
)

EWMA_TIMESCALE_SECONDS = 20.0

W_TRANS_SECONDS = 10.0   # provisional but approved for feasibility audit
```

Interpretation:

* roaming/dwelling are slow latent behavioral states
* raw velocity thresholding was insufficient
* EWMA smoothing is literature-grounded (Atanas/Kim Cell 2023)

---

# Important Current Findings

## Raw thresholding failed

Raw velocity thresholding produced:

* ~1–3 s bouts
* excessive transitions
* no sustained latent states

## EWMA smoothing

EWMA ~20 s produced biologically plausible persistence.

## Transition exclusion sweep

Large exclusion windows (20–30 s) caused catastrophic roaming data loss.

10 s was approved as the best current compromise between:

* latent-state purity
* retained data
* statistical feasibility

---

# Current Pending Task

Perform ONLY:

## Stage 5 covariance-support feasibility audit

Goal:
Determine whether the current segmentation policy provides enough continuous retained data for later covariance estimation.

Allowed:

* descriptive retained-duration analysis
* contiguous epoch analysis
* effective sample-duration heuristics
* retained-frame summaries

Forbidden:

* covariance computation
* precision
* ΔQ
* `D_C ΔQ`
* `Ω_s`
* enrichment
* stationarity
* variability
* estimator fitting

Do NOT:

* change thresholds
* change EWMA timescale
* change W_TRANS
* set MIN_BOUT_SECONDS

---

# Required Output

Report:

* retained contiguous durations
* covariance-support feasibility
* whether roaming covariance estimation appears feasible
* whether additional bout filtering is required
* candidate MIN_BOUT_SECONDS ranges (descriptive only)

Do not proceed beyond descriptive feasibility analysis.