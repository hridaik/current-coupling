# Phase 0 Mid-Project Checkpoint

Date: 2026-05-28
Status: Stage 3 pair-filtering locked; Stage 1 Creamer/RC and Stage 3 DCV extraction pending.

---

## 1. Approved Methodological and Configuration Decisions

### 1.1 Harmonization Policy

| Decision | Value | Basis | Approved |
|---|---|---|---|
| `LR_POLICY` | `"separate"` | task.md Stage 2 explicit requirement | task.md |
| `IDENTITY_CONFIDENCE_THRESHOLD` | `2.5` | NeuroPAL notebook threshold `θ_confidence_label=2.5`, extracted from source; set pre-Stage-2 | 2026-05-28 checkpoint |
| `COVERAGE_FRACTION` | `0.80` | task.md Stage 2 Task 4: "in ≥ 80% of Atanas animals" | task.md |
| Canonical anatomical namespace | `AWCL`/`AWCR` (head-ganglia JSON) | `RANDI_PREPARATION = "immobilized"` — Randi 2023 is a head-ganglion preparation | 2026-05-28 |
| AWC non-mapping decision | `AWCON`/`AWCOFF` are functional-state labels; NOT mapped to `AWCL`/`AWCR` | Approved distinct namespaces; no cross-mapping | 2026-05-28 |
| Randi canonical label source | `aconnectome_ids_ganglia.json` (head namespace) | `randi_all` (`neuron_ids.txt`) uses ON/OFF convention; head JSON uses anatomical L/R | 2026-05-28 |

### 1.2 Subgraph Counts

| Field | Value | Meaning |
|---|---|---|
| `N_COMMON_NEURONS` | **61** | Atanas high-confidence (≥2.5, ≥80% coverage) ∩ ConnectomeToolbox ∩ Randi head labels |
| `N_RANDI_SUBGRAPH_NEURONS` | **60** | Common-61 neurons with a direct name match in `funatlas.h5`; AWCL excluded (funatlas uses AWCOF/AWCON) |
| `N_RANDI_SUBGRAPH_PAIRS` | **189** | Directed pairs (i≠j) with q_wt < 0.05 AND occ1_wt > 0 AND occ1_u31 > 0 within the 60-neuron subgraph |

**Approved asymmetry**: N_COMMON_NEURONS = 61 is retained for all anatomical
harmonization analyses. N_RANDI_SUBGRAPH_NEURONS = 60 applies only to the
Randi functional-pair extraction. The gap is exactly one neuron (AWCL), whose
funatlas representation (`AWCOF`/`AWCON`) uses the functional-state namespace
that is not mapped to the anatomical namespace.

### 1.3 Randi Pair-Filtering Rule

**Primary rule: Rule A (approved 2026-05-28)**

```
q_wt < 0.05   AND   occ1_wt > 0   AND   occ1_u31 > 0
```

| Config field | Value | Meaning |
|---|---|---|
| `RANDI_WT_Q_THRESHOLD` | `0.05` | WT significance threshold; documented as "Default: 0.05, as in Randi et al." in NeuroAtlas library |
| `RANDI_AMPLITUDE_GATE_DFF` | `None` | Amplitude gate INTENTIONALLY EXCLUDED from primary rule |

**Amplitude gate exclusion rationale**: The NeuroAtlas library applies
`|dFF| >= 0.10` as a display/visualization heuristic (`sigprop_dff_th`). This
gate is NOT stated in the task.md DCV_score formula, reduces neuron coverage
from 51/60 to 45/60, and shrinks the pair pool from 189 to 101 (~47%). It is
retained as Rule B for later robustness analysis ONLY.

### 1.4 Data Paths (all approved 2026-05-28)

| Field | Value |
|---|---|
| `DATA_ROOT` | `"data"` |
| `ATANAS_PATH` | `"data/atanas/AtanasKim-Cell2023"` |
| `CREAMER_PATH` | `"data/creamer/Creamer_LDS_2026"` |
| `CONNECTOME_PATH` | `"data/connectome/ConnectomeToolbox"` |
| `RANDI_PATH` | `"data/randi/wormneuroatlas"` |
| `NEUROPEPTIDE_PATH` | `"data/randi/wormneuroatlas"` |

### 1.5 Creamer and RC Decisions (partial — Stage 1 not fully executed)

| Field | Value | Status |
|---|---|---|
| `CREAMER_D_TYPE` | `"discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D"` | Approved 2026-05-28 from source audit |
| `RC_CODE_PATH` | `"ReservoirComputing"` | Approved 2026-05-28 |
| `RC_ROLE_SAMPLING` | `"audit_only"` | Provisional placeholder |
| `RC_ROLE_JACOBIAN` | `"audit_only"` | Provisional placeholder |
| `RC_ROLE_DRIVE_SWEEP` | `"not_used_phase0"` | Provisional placeholder |
| All other CREAMER_* fields | `None` | Stage 1 model-loading not yet authorized |

### 1.6 Fixed Analysis Defaults (from task.md schema, not requiring human decision)

| Field | Value |
|---|---|
| `NORMALIZATION` | `"z_score_global"` |
| `MISSING_NEURON_POLICY` | `"nan_complete_case"` |
| `W_TRANS_SECONDS` | `30.0` |
| `NEFF_METHOD` | `"cross_product_integrated_autocorrelation"` |
| `NEFF_K_MAX_FRAMES` | `200` |
| `SYNAPSE_COUNT_THRESHOLD` | `1` |
| `SYNAPSE_COUNT_THRESHOLD_SENSITIVITY` | `3` |
| `DISCOVERY_ESTIMATOR` | `"unstructured_stability_selection"` |
| `CONFIRMATION_ESTIMATOR` | `"anatomy_guided_lasso"` |
| `PRIMARY_ENRICHMENT_STAT` | `"AUROC"` |
| `SECONDARY_ENRICHMENT_STAT` | `"Fisher_topK"` |
| `RANDOM_SEED` | `20260527` |
| `PHASE0_COMPLETE` | `False` |

---

## 2. Remaining Unset Human-Decision Fields

### 2.1 Fields in HUMAN_DECISION_FIELDS that are still None

| Field | Stage required | Blocker |
|---|---|---|
| `SUBGRAPH_ADEQUATE` | Stage 2 checkpoint | Human must review 61-neuron biological composition |
| `COORD_PRIMARY` | Stage 5 | Requires Stage 5 preprocessing implementation |
| `COORD_ROBUSTNESS_1` | Stage 5 | Requires Stage 5 |
| `COORD_ROBUSTNESS_2` | Stage 5 | Requires Stage 5 |
| `BEHAVIOR_SCORE_SOURCE` | Stage 5 | Requires CePNEM score access |
| `BEHAV_THRESHOLD` | Stage 5 | Must NOT be set before Stage 5; behavioral KDE required |
| `BEHAV_THRESHOLD_RULE` | Stage 5 | With BEHAV_THRESHOLD |
| `MIN_BOUT_SECONDS` | Stage 5 | After epoch duration distribution |
| `COORD_INTERP_RULE` | Stage 5 | Pre-specifies interpretation of ΔQ_CePNEM vs ΔQ_raw |
| `EXCLUDED_ANIMALS_PRIMARY` | Stage 7 | Requires inter-animal consistency analysis |
| `POOLING_STRATEGY` | Stage 7 | After ESTIMATOR_TIER and consistency assessment |
| `LAMBDA_ON` | Stage 7 | CV tuning in estimation pipeline |
| `LAMBDA_OFF` | Stage 7 | With LAMBDA_ON |
| `LAMBDA_OFF_ON_RATIO` | Stage 7 | With LAMBDA_ON / LAMBDA_OFF |
| `NFOLDS` | Stage 7 | After fold strategy confirmed |
| `NULL_MODEL_PRIMARY` | Stage 9 | After null model validation |
| `PRIMARY_HYPOTHESIS_TEXT` | Stage 10 | Human-written; last step |
| `PRIMARY_TOP_K` | Stage 10 | After enrichment power analysis |
| `D_ROBUSTNESS_RHO` | Stage 10 | Human-written; last step |

### 2.2 Computational fields not yet populated (not in HUMAN_DECISION_FIELDS)

These are outputs of pending stages, not direct human decisions:

| Field | Stage | Status |
|---|---|---|
| `CREAMER_TIME_CONVENTION` | Stage 1 | Stage 1 model-loading not yet run |
| `CREAMER_DT` | Stage 1 | — |
| `CREAMER_MAX_EIGENVALUE` | Stage 1 | — |
| `CREAMER_STABLE` | Stage 1 | — |
| `CREAMER_DC_AVAILABLE` | Stage 1 | — |
| `CREAMER_LABEL_CONVENTION` | Stage 1 | — |
| `CREAMER_SIGMA_POSDEF` | Stage 1 | — |
| `CREAMER_OMEGA_NORM` | Stage 1 | — |
| `RC_OUTPUT_NEURON_COORDS` | Stage 4 | Provisional "audit_only" pending Stage 4 |
| `RC_OUTPUT_JACOBIAN_AVAILABLE` | Stage 4 | — |
| `RC_STATE_CONDITIONED` | Stage 4 | — |
| `RC_NEURON_COVERAGE` | Stage 4 | — |
| `DECONV_AVAILABLE` | Stage 5 | — |
| `ESTIMATOR_TIER` | Stage 6 | Determined after n_eff analysis |
| `NONSTATIONARITY_FRACTION` | Stage 6 | — |
| `OUTLIER_ANIMALS` | Stage 7 | Computed from inter-animal consistency |
| `CV_FOLD_ASSIGNMENTS_PATH` | Stage 7 | — |
| `ENRICHMENT_POWER_AT_OR2` | Stage 9 | — |

---

## 3. Deviations

### DEV-001 — COVERAGE_FRACTION hardcoded in script (minor)
**Stage 2 / Resolved 2026-05-28.** `COVERAGE_FRACTION = 0.80` was hardcoded
in `scripts/stage02_subgraph.py` instead of imported from `phase0_config.py`.
Value was correct (matches task.md). Fixed by moving constant to config.
No scientific impact.

### DEV-002 — N_COMMON_NEURONS written to config without checkpoint (procedural)
**Stage 2 / Resolved 2026-05-28.** Script automatically wrote
`N_COMMON_NEURONS = 61` using an uncheckpointed choice of Randi label source
(`randi_head` over `randi_all`). Human reviewed and approved the head-namespace
choice and the count. `SUBGRAPH_ADEQUATE` remains `None` pending biological
adequacy review.

**No open deviations.**

---

## 4. Confirmation: No Forbidden Computations on Real Data

The following have NOT been computed at any point in Phase 0:

| Forbidden computation | Status |
|---|---|
| State-conditioned precision matrices Q_roam, Q_dwell | **NOT computed** |
| ΔQ = Q_roam − Q_dwell | **NOT computed** |
| D_C ΔQ (current-velocity statistic) | **NOT computed** |
| Ω_s (current-velocity Jacobian) | **NOT computed** |
| Graphical lasso on real data | **NOT computed** |
| Inverse covariance on real data | **NOT computed** |
| Enrichment test using real ΔQ | **NOT computed** |
| Current-velocity statistics on real data | **NOT computed** |
| State-conditioned covariance on real data | **NOT computed** |
| Behavioral state threshold set from neural output | **NOT done** |

What HAS been computed:
- NeuroPAL label metadata extracted from Atanas JLD2 (string/confidence values only)
- Label overlap counts (set intersections of string labels)
- Randi funatlas.h5: `occ1` (observation counts), `q` (significance values),
  `dFF` (aggregate mean response) — these are pre-computed atlas statistics
  from Randi 2023, not derived from the Atanas behavioral data used in the
  main analysis
- Pair-count tables under candidate significance thresholds (descriptive only)

The `src/estimators.py` guardrail blocks any attempt to call precision
estimation with `data_kind="real"` while `PHASE0_COMPLETE = False`.
This is verified by `tests/test_phase0_guard.py`.

---

## 5. Approved Dependency Set

Current `.venv` packages:

| Package | Version | Purpose |
|---|---|---|
| `h5py` | 3.16.0 | JLD2/HDF5 inspection of Atanas NeuroPAL artifact and funatlas.h5 |
| `numpy` | 2.4.6 | Array operations in all scripts |
| `pytest` | 9.0.3 | Test suite |
| `Pygments` | 2.20.0 | pytest dependency |
| `packaging` | 26.2 | pytest dependency |
| `pluggy` | 1.6.0 | pytest dependency |
| `iniconfig` | 2.3.0 | pytest dependency |

**Not yet installed** (required for later stages):
- `scipy` — n_eff, stationarity, Lyapunov solver, optimization
- `matplotlib` — diagnostic figures
- `scikit-learn` — graphical lasso, stability selection
- `pandas` — CSV tables, harmonization table
- `networkx` — connectome graph operations
- `statsmodels` — regression null models (Stage 9)

Each additional dependency requires a brief checkpoint noting its purpose
before installation, per `AGENTS.md` coding expectations.

---

## 6. Remaining Blockers Before Preprocessing and Behavioral-State Stages

### Blocker 1 — SUBGRAPH_ADEQUATE not set (Stage 2 checkpoint)
The human must review the 61-neuron biological composition and record
`SUBGRAPH_ADEQUATE = True/False` with justification in `phase0_config.py`
before Stage 3 DCV extraction can be considered fully closed and before
Stage 5 preprocessing can begin in earnest. Key neurons to verify: AVA, RIM,
AIY, AIA, RIG (as specified in task.md Stage 2 human decision checkpoint).

### Blocker 2 — Stage 1 Creamer LDS feasibility not run
The Stage 1 Creamer checkpoint (loading A_C, checking eigenvalues, solving
Lyapunov equation for Σ_C, computing Ω_C) has not been executed. The CHECKPOINT_LOG
records only a source audit. Before Stage 4 (RC check) and before any
current-velocity bridge computations, Stage 1 must be completed:
- `CREAMER_TIME_CONVENTION`, `CREAMER_MAX_EIGENVALUE`, `CREAMER_DC_AVAILABLE`,
  `CREAMER_STABLE`, `CREAMER_SIGMA_POSDEF`, `CREAMER_OMEGA_NORM`,
  `CREAMER_LABEL_CONVENTION` all remain `None`.

### Blocker 3 — Stage 3 DCV extraction not yet run
N_RANDI_SUBGRAPH_PAIRS = 189 is set (Rule A approved), but the DCV extraction
itself (loading dFF, computing DCV_score = dFF_wt − dFF_u31, producing ranked
pair CSV, saving `randi_dcv_pairs.csv`) requires a separate human authorization.
`SUBGRAPH_ADEQUATE` should be set first.

### Blocker 4 — BEHAV_THRESHOLD requires Stage 5 behavioral KDE
The behavioral state threshold must be set from the CePNEM score distribution
alone (bimodality, KDE trough). It MUST NOT be set before Stage 5 runs the
KDE analysis. No neural output (covariance, precision, ΔQ) may inform it.

---

## 7. Recommended Next Stage Candidates

The following are presented descriptively. No stage is selected or started here.

**Option A — Complete Stage 3 DCV extraction**
- Prerequisite: human sets `SUBGRAPH_ADEQUATE`
- Action: load `wt/dFF`, `unc31/dFF`, apply Rule A filter, compute
  DCV_score(i,j) = dFF_wt(i,j) − dFF_u31(i,j), rank pairs, save
  `randi_dcv_pairs.csv`
- Closes Stage 3 pass conditions; short, bounded computation

**Option B — Execute Stage 1 Creamer LDS feasibility**
- No prerequisite beyond current state
- Action: load A_C matrix, check eigenvalues, check D_C availability,
  solve Lyapunov equation for Σ_C, compute Ω_C
- Unblocks Stage 4 RC check; unblocks current-velocity bridge planning
- Requires `scipy` dependency (checkpoint before installing)

**Option C — Stage 4 RC check (after Stage 1)**
- Prerequisite: Stage 1 complete
- Action: load RC model, verify output coordinates, assign RC roles

The natural order following task.md is: complete Stage 3 DCV extraction →
Stage 1 Creamer → Stage 4 RC → Stage 5 preprocessing. Stages 1 and 3 are
independent and could be sequenced in either order.

---

## Consistency Notes

One ordering anomaly is on record: `IDENTITY_CONFIDENCE_THRESHOLD = 2.5` was
set during Stage 2 (before Stage 5, where task.md implies it would be set as
part of the behavioral/preprocessing confidence review). The value came from
an explicit NeuroPAL notebook threshold and was approved by the human before
any label-coverage computation. The confidence threshold was thus not tuned
using downstream neural analysis — the procedural irregularity has no
scientific impact. This is noted for completeness; it is not a new deviation.

The `funatlas.h5` contains pre-computed Randi atlas statistics (q-values and
dFF responses from the published Randi 2023 optogenetic stimulation dataset).
These are independent of the Atanas behavioral imaging data that will be used
in the main analysis. Loading q and dFF from funatlas.h5 does NOT constitute
computing state-conditioned statistics from real behavioral data.
