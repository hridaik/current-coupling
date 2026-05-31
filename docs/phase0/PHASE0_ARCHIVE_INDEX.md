# Phase 0 Archive Index

Date archived: 2026-05-29
PHASE0_COMPLETE = False
PHASE0_METHOD_LOCK_COMPLETE = True

This index lists all Phase 0 artifacts, their locations, and their purpose.
Originals remain in `results/`, `scripts/`, `src/`, and `tests/`.
Copies of key lock documents are in `docs/phase0/`.

---

## Lock and Handoff Documents (docs/phase0/)

| File | Purpose |
|---|---|
| `PHASE0_EXECUTIVE_SUMMARY.md` | Human-readable summary of Phase 0 outcomes |
| `PHASE0_ARCHIVE_INDEX.md` | This file |
| `hypothesis_lock.md` | Locked primary hypothesis (copy of results/hypothesis_lock.md) |
| `phase0_final_summary.md` | Stage completion table and deviation log (copy) |
| `phase1_transition_manifest.md` | Phase 1 handoff package — all locked values and remaining blockers (copy) |
| `phase0_locked_config_snapshot.json` | Machine-readable frozen config values (copy) |
| `cepnem_full_schema_confirmation.md` | Direct confirmation of CePNEM full archive structure (copy) |

---

## Config and Lock Files (repo root)

| File | Purpose |
|---|---|
| `phase0_config.py` | **Single source of truth** for all Phase 0 parameters. DO NOT modify methodology fields. |
| `PROGRESS.md` | Cumulative stage progress log |
| `CHECKPOINT_LOG.md` | Chronological log of all checkpoints and human decisions |
| `CONTEXT.md` | Reasoning notes on non-obvious outcomes |
| `DEVIATIONS.md` | DEV-001 through DEV-005 log |
| `AGENTS.md` | Session contract and scientific background |
| `task.md` | Master task specification for Phase 0 |
| `PHASE1_STARTER_MANIFEST.md` | Phase 1 archival reference (NOT a Phase 1 plan) |

---

## Key Diagnostic Reports (results/diagnostics/)

### Lock outputs
| File | Content |
|---|---|
| `phase0_final_summary.md` | Stage completion, key numbers, deviations |
| `phase0_locked_config_snapshot.json` | Frozen config (no large arrays) |
| `phase0_manifest.json` | File checksums at Stage 10 |
| `phase0_midproject_checkpoint.md` | Mid-project state snapshot |
| `phase1_transition_manifest.md` | Full Phase 1 handoff package |

### CePNEM artifact audits
| File | Content |
|---|---|
| `cepnem_lite_schema_audit.md` | Lite archive: 11 fields, no residuals, τ posterior only |
| `cepnem_lite_schema_audit.json` | Machine-readable per-recording metadata |
| `cepnem_full_schema_audit.md` | Full archive: source-code inferred (file was truncated) |
| `cepnem_full_schema_audit.json` | Machine-readable inferred field inventory |
| `cepnem_full_schema_confirmation.md` | **Direct confirmation** of sampled_trace_params; NL10d param ordering |
| `cepnem_full_schema_confirmation.json` | Machine-readable confirmation data |

### Stage reports
| File | Stage | Key finding |
|---|---|---|
| `stage01_creamer_audit.md` | 1 | Creamer LDS: discrete-time, stable, D_C available |
| `stage02_*.md` | 2 | N_COMMON_NEURONS=61, AWC convention locked |
| `stage03_*.md` | 3 | N_RANDI_SUBGRAPH_PAIRS=189 (Rule A) |
| `stage04_creamer_numerical_feasibility.md` | 4 | Σ_C posdef, Ω_C=8.6089; RC role = eigenworm only |
| `stage04_creamer_rc_bridge_audit.md` | 4 | Structural audit of Creamer + RC |
| `stage05_behavior_descriptive_audit.md` | 5 | 68 recordings, velocity stats, NeuroPAL coverage |
| `stage05_threshold_characterization.md` | 5 | Trimodal velocity; trough at 0.284 |
| `stage05_ewma_characterization.md` | 5 | EWMA τ=20s selected |
| `stage05_segmentation_descriptive.md` | 5 | Raw bouts too short; EWMA required |
| `stage05_retained_frame_audit.md` | 5 | W_TRANS=30s infeasible; W=10s selected |
| `stage05_transition_window_audit.md` | 5 | Transition-window sweep |
| `stage05_covariance_support_audit.md` | 5 | Roaming: 25/40 animals, 8s/animal median |
| `stage06_neff_audit.md` | 6 | pooled_hierarchical; NONSTATIONARITY=1.0 |
| `stage06_stationarity_robustness.md` | 6 | Temporal drift confirmed real (not noise) |
| `neff_report.json` | 6 | n_eff per animal per state |
| `stage07_synthetic_estimator_dryrun.md` | 8 | SS TPR≥0.8; full-matrix pooled best |
| `stage07_dryrun_results.json` | 8 | Machine-readable TPR by regime |
| `stage08_nonstationary_synthetic_robustness.md` | 8 | Drift-robust; TPR 0.8–1.0 across drift 0–100% |
| `stage08_synthetic_blockwise.md` | 8 | Blockwise estimation rejected |
| `stage09_synthetic_enrichment_power.md` | 9 | AUROC power=1.0 at OR=2 all regimes |
| `stage09_power_results.json` | 9 | Machine-readable power curves |

---

## Figures (results/figures/)

All figures are Stage 5–9 diagnostics. Key figures:

| File | Content |
|---|---|
| `stage05_velocity_kde.pdf` | Per-animal and pooled velocity distributions (basis for BEHAV_THRESHOLD) |
| `stage05_retained_summary.pdf` | Retained frames by W_TRANS and tau |
| `stage06_neff_per_animal.pdf` | n_eff distribution across animals and states |
| `stage06_rolling_covariance.pdf` | Within-state covariance drift over time |
| `stage06_drift_vs_support.pdf` | Temporal drift vs sample support (confirms real drift) |
| `stage08_drift_robustness_tpr.pdf` | Nonstationarity robustness: TPR vs drift fraction |
| `stage08_pooled_animals_tpr.pdf` | TPR vs n_animals pooled (25 animals → TPR=0.90) |
| `stage09_power_curves.pdf` | Enrichment power curves (AUROC + Fisher) |
| `stage09_null_calibration.pdf` | Null model type-I error calibration |

---

## Source Modules (src/)

| File | Purpose |
|---|---|
| `estimators.py` | **Guardrail** + stability selection + anatomy-guided lasso |
| `enrichment.py` | AUROC, Fisher_topK, power simulation |
| `null_models.py` | Permutation null models |
| `preprocessing.py` | Coordinate systems, behavioral segmentation |
| `neff.py` | Integrated autocorrelation time, n_eff |
| `stationarity.py` | Within-state covariance drift |
| `variability.py` | Inter-animal covariance consistency |
| `harmonization.py` | Neuron name mapping across datasets |
| `data_access.py` | Load Atanas, Creamer, connectome, Randi data |
| `power_analysis.py` | Enrichment power under synthetic null/signal |

---

## Test Suite (tests/)

| File | Tests | What it verifies |
|---|---|---|
| `test_phase0_guard.py` | 4 | **PHASE0_COMPLETE=False; METHOD_LOCK=True; real blocked; synth ok** |
| `test_estimators.py` | 8 | Synthetic precision recovery, circularity control, real blocked |
| `test_enrichment.py` | 9 | AUROC, Fisher, power, null calibration |
| `test_nulls.py` | 6 | Null model preservation of degree/class/proximity |
| `test_harmonization.py` | 4 | Neuron name mapping on known cases |
| `test_neff.py` | 1 | n_eff formula on AR(1) with known τ |

Total: 27 tests; 27/27 pass as of archive date.

---

## Scripts (scripts/)

| File | Stage | Purpose |
|---|---|---|
| `stage01_creamer_check.py` | 1 | Creamer LDS stability and D_C audit |
| `stage02_subgraph.py` | 2 | Common neuron subgraph construction |
| `stage03_randi_extraction.py` | 3 | Randi DCV pair extraction |
| `stage04_rc_check.py` | 4 | RC capability audit |
| `stage05_preprocessing.py` | 5 | Behavioral descriptive audit |
| `stage05_threshold_characterization.py` | 5 | Velocity KDE and trough analysis |
| `stage05_ewma_characterization.py` | 5 | EWMA timescale sweep |
| `stage05_segmentation_descriptive.py` | 5 | Raw bout duration analysis |
| `stage05_retained_frame_audit.py` | 5 | Retained frames at locked params |
| `stage05_transition_window_audit.py` | 5 | Transition window sweep |
| `stage05_covariance_support_audit.py` | 5 | Epoch feasibility at locked params |
| `stage05_cepnem_lite_schema_audit.py` | 5 | CePNEM lite archive metadata audit |
| `stage05_cepnem_full_schema_audit.py` | 5 | CePNEM full archive schema confirmation |
| `stage06_neff_stationarity.py` | 6 | n_eff and stationarity analysis |
| `stage06_stationarity_robustness.py` | 6 | Temporal vs null drift comparison |
| `stage07_variability.py` | 7 | Inter-animal variability (not run) |
| `stage08_estimator_dryrun.py` | 8 | Synthetic estimation dry-run |
| `stage09_power.py` | 9 | Enrichment power simulation |
| `stage10_hypothesis_lock.py` | 10 | Hypothesis document generation |
