# Phase 1 Context — FINAL ARCHIVE COPY

> **ARCHIVE RECORD**
> Archived: 2026-05-31
> Rationale: Phase 1 formally closed — structural observability obstruction.
>   N_COMMON_NEURONS = 61 and MISSING_NEURON_POLICY = "nan_complete_case" are
>   jointly unachievable on the Atanas SF freely-behaving corpus.
> Closure status: No further Phase 1 computation authorized.
> Phase 2 not yet authorized.
> Source file: PHASE1_CONTEXT.md (repo root) — preserved unchanged.

---

# Phase 1 Context

Status: **FORMALLY CLOSED — structural observability obstruction (2026-05-31)**
Initialized: 2026-05-29

Phase 0 context notes are archived at: `docs/phase0/operational/CONTEXT.md`

---

## Inherited Technical Context

### CePNEM Archive (fit_results.jld2)

- **File**: `data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2` — 19.55 GB, h5py opens OK
- **68 recordings** present; bit-identical alignment to H5 gcamp/trace_array files confirmed
- **`sampled_trace_params`** shape: `(11, 10001, N, n_epochs)` — directly confirmed in all 68 recordings
- **NL10d parameter ordering** confirmed by param[4] = 0.0000 exactly across all samples/neurons/epochs
  - param[0] = c_vT (velocity rectification)
  - param[1] = c_v (velocity encoding weight)
  - param[2] = c_θh (head curvature weight)
  - param[3] = c_P (pumping weight)
  - param[4] = 0 (disabled constant — NL10d structural confirmation)
  - param[5] = y0 (initial neural activity)
  - param[6] = s0 (EWMA timescale parameter — NON-TRIVIAL reparameterization; see below)
  - param[7] = b (baseline)
  - param[8] = ℓ0 (GP residual length scale)
  - param[9] = σ0_SE (GP amplitude)
  - param[10] = σ0_noise (noise amplitude)
- **Precomputed residuals**: NOT present. Must compute from sampled_trace_params.
- **Behavioral covariates available in fit_results.jld2**: v, ang_vel, θh, P, curve

### Critical Implementation Warning: s0 Reparameterization

The timescale parameter `s0` (param[6]) is stored in the MCMC sampler's internal
parameterization, NOT the natural parameterization. The formula `tau = log(s/(s+1)) /
log(0.5) * dt` with `s = 10*exp(s0)` gives approximate agreement for fast neurons
but fails by factor ~100× for slow neurons. The CePNEM model forward equations
(model_nl8 in CePNEM.jl) must be used directly — do not use the simplified formula.
The behavioral encoding weights (params 0–3) appear to be in natural space and
are reliable for the predicted behavioral component.

This is a Stage 1.0 implementation requirement, not a blocker for planning.

### Nonstationarity (DEV-003)

All 26 assessed animal-state pairs show temporal covariance drift.
Temporal excess over random-split null: median 0.666 (all 26 pairs positive).
Leading cause: photobleaching (GCaMP6s, 30–60 min recordings).
Interpretation rule (from task.md): accepted as design constraint.
Results represent time-averaged effective coupling under confirmed drift.

### Subgraph Structure (three spaces)

| Space | N neurons | Notes |
|---|---|---|
| Anatomical (primary) | 61 | NeuroPAL confidence ≥ 2.5, coverage ≥ 80% |
| Randi pair analysis | 60 | AWCL absent from funatlas namespace |
| Creamer/current-velocity bridge | 56 | AIBL, AIBR, AWCL, IL1L, IL1R absent |

AWC namespace: AWCL/AWCR (anatomical) ≠ AWCON/AWCOFF (functional). No cross-mapping.

### Behavioral Regime Support

- Non-roaming: 39/40 animals — primary regime, adequate power
- Roaming: 25/40 animals — exploratory only (pooled, fragile; TPR=0.90 at T=1000 frames)

### Estimation Validated Regimes (Phase 0 Stage 8 Synthetic)

| Regime | T | TPR | Status |
|---|---|---|---|
| Non-roaming optimistic | 2000 | 1.00 | PASS |
| Roaming optimistic | 420 | 0.80 | PASS |
| Pooled 25 animals (T=1000) | — | 0.90 | PASS |
| Non-roaming middle | 300 | 0.40 | FAIL — underpowered |

Full-matrix estimation confirmed superior to blockwise (Stage 8 decision).

### Creamer Parameters (56-neuron subspace)

- CREAMER_MAX_EIGENVALUE = 0.9966 (stable discrete-time)
- CREAMER_DT = 0.5 s (2 Hz sampling)
- CREAMER_OMEGA_NORM = 8.6089 (Frobenius norm of Ω_C in 56-neuron subspace)
- D_C: diagonal, positive-definite, available

---

## Phase 1 Ordering Constraint (CRITICAL)

**CePNEM residualization (Stage 1.0) must pass ALL verification checks before
any precision matrix is computed from real data (Stage 1.1).**

Once both coordinate systems' precision matrices exist:
**Stages 1.1–1.6 must run for BOTH coordinates before Stage 1.7 (coordinate comparison)
is opened.** Previewing one coordinate's enrichment before the other is computed
would contaminate the coordinate comparison interpretation.

---

## Phase 1 Configuration Changes Required (Human Authorization Needed)

Before Stage 1.1 may begin, in `phase0_config.py`:
1. Set `PHASE0_COMPLETE = True` (lifts the estimators.py guardrail)
2. Update `COORD_PRIMARY = "cepnem_residual"` (resolves DEV-004 once Stage 1.0 passes)
3. Update `COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"` (raw GCaMP becomes robustness)

These require explicit human authorization recorded in CHECKPOINT_LOG.md.

---

## DEV-004 Resolution Status

task.md declares DEV-004 "Now RESOLVED" — CePNEM residuals are the primary coordinate
for Phase 1. However, actual residual computation still requires:
1. Human authorization checkpoint (PHASE0_COMPLETE = True)
2. Stage 1.0 implementation and verification
3. Update to COORD_PRIMARY after Stage 1.0 passes

The Phase 1 task plan resolves DEV-004 by design; the human gate remains active.

---

## DEV-005 Resolution Status

task.md addresses DEV-005 via Stage 1.3 (leave-one-animal-out sensitivity):
LOO compensates for the missing inter-animal variability characterization.
Human must confirm all-animal pooling without prior outlier screening.

---

## Stage 1.0 Context Notes (recorded 2026-05-29)

### Recording scope: 40, not 68

fit_results.jld2 contains 68 recordings. Only 40 have NeuroPAL identity labels in
dict_neuropal_label.jld2. The remaining 28 have no neuron identity and cannot be
mapped to the 61-neuron common subgraph. Stage 1.0 and all downstream stages
operate on 40 recordings. PHASE1_PROGRESS.md prerequisite list had "68-recording
pipeline"; this is corrected to 40.

### Neuron label mapping: match_org_to_skip required

The column ordering of decoded_labels in dict_neuropal_label.jld2 does NOT match the
column ordering of trace_array / sampled_trace_params. The correct mapping is:
  column j of trace_array → decoded_labels[ match_org_to_skip[0][j] - 1 ]
using match_org_to_skip from each H5 file (Julia 1-based permutation). The direct
positional assumption (decoded_labels[j] = column j) is wrong. This is now implemented
in scripts/phase1/stage0_cepnem.py and must be used in all Stage 1.1+ scripts that
access subgraph neuron columns.

### Behavioral decorrelation findings — human-resolved interpretation

Official result (human decision 2026-05-31):
  Covariates: CePNEM model inputs — v (velocity), θh (head angle), P (pumping)
  These are the covariates the model was fit to remove (model.jl line 45: `v, θh, P`).
  Aggregate median reduction = 0.545 → PASS (≥ 0.50 threshold)

Per-covariate medians:
  v:  raw=0.148, resid=0.064, reduction=0.545
  θh: raw=0.095, resid=0.053, reduction=0.380
  P:  raw=0.148, resid=0.039, reduction=0.677
  (ang_vel: raw=0.077, resid=0.063, reduction=0.181 — not a model input, reported for completeness)
  (curve:   raw=0.141, resid=0.071, reduction=0.461 — not a model input, reported for completeness)

Documented artifact inconsistency (for future reference):
  task.md check (a) lists "velocity, angular velocity, curvature" as the covariates.
  This does not match the CePNEM model inputs (v, θh, P). ang_vel and curve are in
  the archive but are not model inputs. The human resolved this ambiguity in favor of
  model inputs on 2026-05-31. The alternate interpretations and their outcomes were:
    Literal list (v, ang_vel, curve): aggregate median = 0.461, would have been below threshold
    All five covariates:              aggregate median = 0.461, below threshold
    Model inputs only (v, θh, P):    aggregate median = 0.545, PASS (selected)
  This resolution is recorded here for methodological transparency. It does not
  constitute a post-hoc parameter change — the criterion (50% reduction) and the
  measurement method (aggregate median) were pre-specified; only the covariate
  identity was ambiguous in the artifact.

Caveat for Stage 1.7 (coordinate comparison):
  θh decorrelation is 38.0% — the weakest among model inputs. Some head-angle
  behavioral confound remains in the CePNEM residual coordinate. Stage 1.7
  interpretation should note this when comparing CePNEM vs. raw GCaMP enrichment.

### Variance ratio > 1.0 findings (6 pairs)

Six (recording, neuron) pairs showed var_ratio marginally > 1.0 (range 1.003–1.073).
Diagnosis: mathematically expected for weakly behaviorally-tuned neurons. The condition
  Var(predicted) > 2·Cov(trace, predicted) is satisfied whenever Corr(trace, pred) < √R/2
  where R = Var(pred)/Var(trace). All 6 cases: positive Cov, Corr < 0.25, R < 0.22.
  Posterior median Bayesian weights (with Normal(0,1) prior) are shrunk toward zero for
  weak encoders; the small predicted component has correct sign (positive Cov) but
  insufficient correlation to reduce variance.
This is NOT an implementation error (identity check passed perfectly, max error = 0.00e+00).
All 6 neurons are flagged in variance_ratios.csv. Not excluded.
Neurons involved: M3R, SMDVL (rec 2023-01-09-15); CEPVL (rec 2023-01-17-07);
  IL2DR (rec 2023-01-16-15); M4 (rec 2023-01-16-22); IL2VL (rec 2023-01-17-01).

### Variance ratio < 0.10 findings (14 pairs)

14 (recording, neuron) pairs showed var_ratio < 0.10, indicating high CePNEM model fit.
Strongest: ASGL (rec 2023-01-10-14, vr=0.060), I3 (rec 2023-01-16-15, vr=0.065),
  NSML (rec 2022-06-14-13, vr=0.064), AWAL (rec 2023-01-09-15, vr=0.065).
All 14 flagged in variance_ratios.csv. None excluded. For Stage 1.1: these neurons
  have almost no residual variance in the CePNEM coordinate; their contribution to
  precision estimation will be near-zero. Watch their condition-number effect.

### Residual stationarity: no improvement over raw

CePNEM residualization does NOT reduce temporal covariance drift:
  Median drift_raw = 0.785, drift_resid = 0.867, ratio = 1.083
  33/40 recordings: residual more nonstationary than raw trace
The behavioral model (v, θh, P) does not capture the long-timescale drift
(photobleaching). DEV-003 interpretation ("time-averaged effective structure") applies
to CePNEM residuals equally as to raw GCaMP. This does not affect the scientific
value of residualization — it means photobleaching is not behavior-mediated drift.

### Stationarity implementation bug (found and corrected)

The check_stationarity function in src/cepnem_residualize.py initially applied its
NaN filter over all T frames including trailing frames after the last epoch. This
caused NaN results for 21/40 recordings (those with T_total > epoch_span). Fixed by
restricting the NaN check to in_ep_idx frames only. Stationarity recomputed from
saved .npz files and H5 raw traces. Residualized traces are unaffected.

### COORD_PRIMARY update: IMPLEMENTED 2026-05-31

Per the Stage 1.0 completion checkpoint (approved 2026-05-31):
  COORD_PRIMARY      = "cepnem_residual"       (was "gcamp_trace_array_zscore")
  COORD_ROBUSTNESS_1 = "gcamp_trace_array_zscore"  (was None)
DEV-004 is now formally resolved.
All Stage 1.1+ scripts must import COORD_PRIMARY from phase0_config.py and use
"cepnem_residual" as the primary coordinate. Raw GCaMP is the robustness coordinate.

### Notes to watch in Stage 1.1

- Neurons with var_ratio < 0.10 may have near-zero residual variance; watch their
  impact on precision matrix condition numbers.
- θh decorrelation partial (38%): some behavioral confound remains in the CePNEM
  residual coordinate. State this caveat in all Stage 1.7 interpretations.
- Stationarity unchanged: time-averaged interpretation applies equally to both coordinates.
- Only 40 recordings in CePNEM coordinate; raw GCaMP (Stage 1.1 robustness coordinate)
  could in principle use all 68 H5 recordings for the subgraph neurons — but to maintain
  a comparable basis, both coordinates should be restricted to the same 40 recordings.
