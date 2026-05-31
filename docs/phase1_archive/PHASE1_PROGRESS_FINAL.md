# Phase 1 Progress — FINAL ARCHIVE COPY

> **ARCHIVE RECORD**
> Archived: 2026-05-31
> Rationale: Phase 1 formally closed — structural observability obstruction.
>   N_COMMON_NEURONS = 61 and MISSING_NEURON_POLICY = "nan_complete_case" are
>   jointly unachievable on the Atanas SF freely-behaving corpus.
> Closure status: No further Phase 1 computation authorized.
> Phase 2 not yet authorized.
> Source file: PHASE1_PROGRESS.md (repo root) — preserved unchanged.

---

# Phase 1 Progress

Status: **FORMALLY CLOSED — structural observability obstruction**
Initialized: 2026-05-29
Closed: 2026-05-31
Last updated: 2026-05-31

Phase 0 progress log is archived at: `docs/phase0/operational/PROGRESS.md`

---

## Prerequisites Checklist

- [ ] Human reviews `docs/phase0/phase1_transition_manifest.md`
- [ ] Human reviews `task.md` (Phase 1 task specification)
- [ ] **DEV-003 authorized**: human accepts nonstationarity interpretation rule:
      "results represent time-averaged effective coupling under confirmed within-recording drift"
- [ ] **DEV-004 addressed**: CePNEM residuals are the Phase 1 primary coordinate (Stage 1.0 must pass)
- [ ] **DEV-005 authorized**: human confirms all-animal pooling without prior outlier screening;
      Stage 1.3 LOO sensitivity compensates
- [ ] `PHASE0_COMPLETE = True` set in `phase0_config.py` with CHECKPOINT_LOG entry
- [ ] `COORD_PRIMARY = "cepnem_residual"` updated after Stage 1.0 passes
- [ ] Guardrail re-verified after PHASE0_COMPLETE = True

---

## Stage Status

| Stage | Status | Key Numbers |
|---|---|---|
| 1.0 CePNEM residualization | **COMPLETE** (human authorized 2026-05-31) | 40 recordings; median 55 neurons/rec; identity PASS; decorrelation 0.545 on model inputs (v,θh,P) PASS; 14 var_ratio flagged; stationarity ratio 1.083 |
| 1.1 State-conditioned precision estimation | BLOCKED — Stage 1.1 CHECKPOINT required | — |
| 1.2 ΔQ computation and classification | BLOCKED | — |
| 1.3 LOO sensitivity | BLOCKED | — |
| 1.4 D-robustness check | BLOCKED | — |
| 1.5 Ω_C comparison | BLOCKED | — |
| 1.6 Enrichment tests | BLOCKED | — |
| 1.7 Coordinate comparison | BLOCKED | — |
| 1.8 Summary, figures, named pairs | BLOCKED | — |

---

## Stage 1.0 — CePNEM Residualization

**Status**: COMPLETE (human authorized 2026-05-29)

Pass conditions — final status:
- [x] CePNEM model evaluated for all 40 NeuroPAL animals × subgraph neurons
- [x] Tau parameter mapping verified: s = 10·exp(s0) confirmed from model.jl; identity check max error = 0.00e+00
- [x] Behavioral decorrelation: aggregate median reduction = 0.545 on model inputs (v, θh, P). Above 0.50 threshold → PASS. Covariate selection resolved by human decision (see CHECKPOINT_LOG.md and CONTEXT.md).
- [x] Variance ratios: 14 pairs flagged < 0.10 (documented, not excluded); 6 pairs > 1.0 (diagnosed as expected behavior, not excluded)
- [x] No epoch boundary artifacts (visual check; no systematic transient)
- [x] Residualized traces saved: 40 .npz files in results/phase1/data/cepnem_residuals/
- [x] Stationarity: drift ratio resid/raw = 1.083 median (residuals not more stationary); finding recorded

---

## Stage 1.1 — Precision Estimation

**Status**: BLOCKED — Stage 1.1 CHECKPOINT required (see CHECKPOINT_LOG.md pending entry)
**Prerequisite**: phase0_config.py must be updated (COORD_PRIMARY, COORD_ROBUSTNESS_1) before any real-data precision matrix is computed. This is authorized by the Stage 1.1 checkpoint.

Expected outputs (8 precision matrices):
- CePNEM residuals × roaming × discovery
- CePNEM residuals × roaming × confirmation
- CePNEM residuals × dwelling × discovery
- CePNEM residuals × dwelling × confirmation
- Raw GCaMP × roaming × discovery
- Raw GCaMP × roaming × confirmation
- Raw GCaMP × dwelling × discovery
- Raw GCaMP × dwelling × confirmation

Pass conditions:
- [ ] All 8 precision matrices computed and saved
- [ ] All positive definite and symmetric
- [ ] Condition numbers and n_eff per state per coordinate recorded
- [ ] No convergence failures

---

## Stage 1.2 — ΔQ and Classification

**Status**: BLOCKED

Expected outputs (4 ΔQ matrices: 2 coordinates × 2 estimators):
- [ ] Class counts recorded (Class 4 ≥ 20 required for enrichment)
- [ ] Class 3 count = 0 or documented
- [ ] Ranked pair lists saved (4 CSV files)
- [ ] Summary statistics recorded

---

## Stage 1.3 — LOO Sensitivity

**Status**: BLOCKED
Computational note: ~3900 graphical lasso fits. Run 3-animal pilot first to estimate time.

- [ ] LOO completed for all contributing animals
- [ ] Retention scores for top-50 pairs computed
- [ ] Median retention ≥ 0.70
- [ ] Influential animals identified

---

## Stage 1.4 — D-Robustness

**Status**: BLOCKED

- [ ] Three D-scaled ΔQ versions (D_C, D_diag, I) computed
- [ ] Spearman correlations among top-50 rankings recorded
- [ ] Go/no-go decision: all ρ ≥ 0.7 → PASS; any < 0.7 → FAIL

---

## Stage 1.5 — Ω_C Comparison

**Status**: BLOCKED (secondary; requires D-robustness result)

- [ ] Ω̂_s^(C) computed for both states
- [ ] ΔΩ̂^(C) matches D_C ΔQ within 1e-10
- [ ] Preparation-mismatch caveat present in all output files

---

## Stage 1.6 — Enrichment Tests

**Status**: BLOCKED

Tests to run:
- [ ] Test 1: Neuropeptide AUROC (PRIMARY) — simple + degree-preserving null
- [ ] Test 2: Neuropeptide Fisher top-K (SECONDARY) — both nulls
- [ ] Test 3: Randi unc-31 AUROC + Fisher (SECONDARY) — both nulls
- [ ] Test 4: Serotonin/PDF receptor AUROC + Fisher (EXPLORATORY)
- [ ] Confirmation estimator check (Test 1 repeated with anatomy-guided lasso ΔQ)
- [ ] Degree-preserving null validated (KS test p > 0.05 for ≥ 95% permutations)

**GATE**: All results saved to JSON BEFORE any figure is generated.

---

## Stage 1.7 — Coordinate Comparison

**Status**: BLOCKED
**NOTE**: Both coordinates' Stages 1.1–1.6 must be complete and saved before opening this stage.

Interpretation outcomes (from locked table):
- CePNEM sig + Raw sig → "Residual neural state organization" (strong claim)
- CePNEM sig + Raw not → "Neural organization masked by behavioral noise"
- CePNEM not + Raw sig → "Behavior-mediated state structure" (interpret cautiously)
- CePNEM not + Raw not → "Null result"

---

## Stage 1.8 — Summary and Figures

**Status**: BLOCKED

Deliverables:
- [ ] 6-panel primary figure (PDF + PNG)
- [ ] Summary table (results/phase1/tables/summary.csv)
- [ ] Named pair table (results/phase1/tables/named_pairs.csv) with prediction column
- [ ] Figure caption (results/phase1/figures/figure_caption.md)
- [ ] All figure source data saved separately

---

## Stage 1.1 — Supplementary Coverage (Interpretation C)

**Status**: COMPLETE (2026-05-31) — awaiting human decision

Supplementary neuron-coverage computation under Interpretation C executed and
verified. Full results in results/phase1/data/supplementary_coverage.json.

| Condition | n_neurons | n_frames_cc | n_eff_p25 | viable |
|---|---|---|---|---|
| CePNEM dwelling — strict (Gate A) | 4 | 30,583 | 33.09 | n/a (4-neuron space) |
| CePNEM dwelling — Interp. C (80%) | 53 | 166 | 36.07 | False |
| CePNEM roaming — strict (Gate A) | 13 | 5,587 | 24.17 | n/a (13-neuron space) |
| CePNEM roaming — Interp. C (80%) | 48 | 0 | 0.0 | False |
| GCaMP dwelling — Interp. C | 53 | 166 | 20.44 | False |
| GCaMP roaming — Interp. C | 48 | 0 | 0.0 | False |

Root cause: 80% marginal-presence + complete-case collapse. Each recording
  has ~50-58 of the 61 subgraph neurons; the recording-specific missing neurons
  differ across animals. After including neurons present in >= 32/39 (dwelling)
  or >= 16/19 (roaming) recordings, only 1 dwelling recording has all 53 included
  neurons (contributing 166 frames), and no roaming recording has all 48.

Excluded neurons (8, dwelling): AVJR, IL1R, IL2VL, IL2VR, M1, OLQVR, RMDDR, URYVR
Excluded neurons (13, roaming): AIBR, AIZL, AVEL, AVER, AVJR, IL1R, IL2VL, IL2VR,
                                  M1, OLQVL, RMDDR, RMDL, URBL

## Closure Statement

Phase 1 is formally closed as of 2026-05-31 due to a structural observability
obstruction. The locked parameters N_COMMON_NEURONS = 61 and
MISSING_NEURON_POLICY = "nan_complete_case" are jointly unachievable on the
Atanas SF freely-behaving corpus.

This is a dataset/observability limitation. It is not an implementation failure,
not a statistical failure, and not a coding failure.

No further Phase 1 computation is authorized.
Phase 2 has not been authorized.

Full closure record: PHASE1_CHECKPOINT_LOG.md (entry: 2026-05-31 ARCHIVE CHECKPOINT).
