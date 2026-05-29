# SUPERVISOR_HANDOFF.md

## Project Status

This repository is in Phase 0 of the C. elegans project.

The coding agent is NOT allowed to perform biological analysis beyond explicitly authorized Phase 0 audit/feasibility steps.

The coding agent must follow:

* `task.md`
* `AGENTS.md`

as binding specifications.

---

# Hard Integrity Constraints (Critical)

During Phase 0, the coding agent MUST NOT:

* compute state-conditioned precision matrices from real data
* compute real-data inverse covariance
* compute graphical lasso on real data
* compute real-data ΔQ
* compute real-data `D_C ΔQ`
* compute real-data `Ω_s`
* run enrichment using real ΔQ
* compute current-velocity statistics from real data
* tune thresholds using downstream feasibility or neural-analysis outputs

Real-data covariance matrices are allowed only for:

* n_eff
* stationarity
* inter-animal variability

Precision matrices are allowed ONLY on synthetic data for estimator dry runs.

`src/estimators.py` contains a guardrail enforcing this.

`PHASE0_COMPLETE = False`.

---

# Current Repository State

Scaffold initialized and guardrails tested.

All work so far has been restricted to:

* repository setup
* source audits
* metadata audits
* label harmonization feasibility
* NeuroPAL label decoding feasibility

No forbidden neural analysis has been run.

---

# Approved Human Decisions

The following config decisions are approved and already written to `phase0_config.py`:

```python
DATA_ROOT = "data"

ATANAS_PATH = "data/atanas/AtanasKim-Cell2023"
CREAMER_PATH = "data/creamer/Creamer_LDS_2026"
CONNECTOME_PATH = "data/connectome/ConnectomeToolbox"
RANDI_PATH = "data/randi/wormneuroatlas"
NEUROPEPTIDE_PATH = "data/randi/wormneuroatlas"

RC_CODE_PATH = "ReservoirComputing"

RC_ROLE_SAMPLING = "audit_only"
RC_ROLE_JACOBIAN = "audit_only"
RC_ROLE_DRIVE_SWEEP = "not_used_phase0"

CREAMER_D_TYPE = (
    "discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D"
)

IDENTITY_CONFIDENCE_THRESHOLD = 2.5

LR_POLICY = "separate"
```

---

# Current Stage

Stage 2 label-only decode / harmonization feasibility.

Stage 3 has NOT started.

---

# Important Current Outputs

The coding agent decoded:

`dict_neuropal_label.jld2`

using metadata-safe `h5py` inspection.

Reported outputs:

* Atanas records decoded: 40
* Required records for 80% coverage: 32
* Atanas labels passing threshold in ≥80% of records: 61
* Atanas ∩ ConnectomeToolbox ∩ Randi all-neuron labels: 60
* Atanas ∩ ConnectomeToolbox ∩ Randi head labels: 61
* `N_COMMON_NEURONS = 61`

BUT:

There is an unresolved inconsistency:

* head overlap > all-neuron overlap

and possible unauthorized use of:

* an 80% coverage rule

This has NOT yet been diagnosed.

---

# Critical Current Issue

The previous coding agent was instructed to perform a DIAGNOSIS-ONLY step.

The diagnosis was NOT completed because usage limits were hit.

NO FIXES are authorized yet.

DO NOT:

* modify `phase0_config.py`
* recompute final counts
* revise thresholds
* revise harmonization policy
* revise AWC mappings
* revise overlap rules

until diagnosis is complete and reviewed.

---

# Exact Pending Supervisor Instruction

The next authorized action is:

1. Diagnose why:

   * all-neuron overlap = 60
   * head overlap = 61
   * `N_COMMON_NEURONS = 61`

2. Determine whether the “80% coverage” rule:

   * was explicitly authorized
   * or was silently introduced

3. Diagnose exact handling of:

   * AWCON
   * AWCOFF
   * AWCL
   * AWCR

4. Determine whether writing:

   * `N_COMMON_NEURONS = 61`

was procedurally valid or premature.

5. Produce only a diagnosis report.

NO corrections yet.

---

# Files Relevant To Current Diagnosis

Review:

* `results/diagnostics/stage02_atanas_label_decode.md`
* `results/diagnostics/stage02_subgraph_feasibility.md`
* `scripts/stage02_subgraph.py`
* `src/harmonization.py`
* `phase0_config.py`
* `CHECKPOINT_LOG.md`
* `PROGRESS.md`

---

# Allowed Actions For The Next Step

Allowed:

* diagnosis
* code inspection
* report writing
* reading already-created metadata outputs

Forbidden:

* fixing code
* recomputing approved results
* changing config values
* Stage 3
* behavioral analysis
* covariance/precision/ΔQ/enrichment/current-velocity analysis

---

# Required Final Output Of The Next Step

A diagnosis-only report explaining:

* the 60 vs 61 inconsistency
* whether the 80% rule was authorized
* exact AWC handling
* whether `N_COMMON_NEURONS = 61` was premature
* whether a deviation should be recorded

No fixes.
