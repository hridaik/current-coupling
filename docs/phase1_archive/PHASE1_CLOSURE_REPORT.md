# Phase 1 Closure Report

Archived: 2026-05-31
Status: FORMALLY CLOSED — structural observability obstruction
Phase 2: Not yet authorized

---

## 1. Original Phase 1 Objective

Test whether off-connectome precision matrix differences between roaming and
dwelling behavioral states in freely-behaving C. elegans are enriched in
neuropeptide-signaling neuron pairs. Primary coordinate: CePNEM residuals.
Robustness coordinate: raw GCaMP z-score. Analysis subgraph: 61 neurons
(N_COMMON_NEURONS = 61). Estimation policy: nan_complete_case.

The execution plan comprised eight stages:
  1.0  CePNEM residualization
  1.1  State-conditioned precision estimation (8 matrices)
  1.2  ΔQ computation and four-class connectome classification
  1.3  LOO sensitivity analysis
  1.4  D-robustness (three D-scaling variants)
  1.5  Ω_C Creamer subspace comparison
  1.6  Enrichment tests (neuropeptide AUROC primary; Fisher, Randi, serotonin secondary)
  1.7  CePNEM vs. raw GCaMP coordinate comparison
  1.8  Summary figures and named pair table

---

## 2. Completed Work

### Phase 0 Summary

Phase 0 established the full analysis architecture and validated it on synthetic data.

Corpus: 40 NeuroPAL whole-brain calcium imaging recordings from freely-behaving
C. elegans (Atanas et al., SF dataset, DANDI:000776).

61-neuron subgraph: defined by marginal presence ≥ 80% of all 40 recordings.

Behavioral segmentation locked: EWMA-smoothed velocity (tau=20s), threshold=0.284,
W_TRANS=10s, MIN_BOUT=10s.

Estimator validation (Stage 8 synthetic dry run): stability-selection GLASSO
(discovery) and anatomy-guided GLASSO ADMM (confirmation) validated on synthetic
complete-case pooled data. LAMBDA_ON=0.04, LAMBDA_OFF=0.45 locked. Validated
regimes: non_roaming_optimistic (T=2000), roaming_optimistic (T=420),
pooled_25_animals (T=1000). Regime thresholds: T ≥ 2000 optimistic;
T ≥ 300 middle (TPR=0.40); below-middle not validated.

Deviations authorized: DEV-003 (nonstationarity interpretation), DEV-004
(CePNEM as primary coordinate), DEV-005 (all-animal pooling without
outlier screening).

PHASE0_COMPLETE = True. All parameters frozen in phase0_config.py.

### Stage 1.0 — CePNEM Residualization (COMPLETE, authorized 2026-05-31)

40 NeuroPAL recordings residualized. All pass conditions met.
- Tau reparameterization: PASS (max error = 0.00e+00)
- Behavioral decorrelation: PASS (aggregate median reduction = 0.545 ≥ 0.50
  on model inputs v, θh, P; human-resolved covariate interpretation)
- Variance ratios: 14 pairs flagged < 0.10 (documented, not excluded);
  6 pairs > 1.0 (expected Bayesian behavior, not excluded)
- Epoch boundary artifacts: none observed (visual check)
- Stationarity: drift ratio resid/raw = 1.083 median; DEV-003 applies
- 40 .npz files saved: results/phase1/data/cepnem_residuals/
- COORD_PRIMARY updated to "cepnem_residual"; DEV-004 resolved

### Stage 1.1 Gate A — Complete-Case Characterization (COMPLETE)

Strict complete-case (all 40 recordings, all 61 subgraph neurons required):

  State      Neurons  Frames   n_eff_p25  Recordings
  Dwelling   4        30,583   33.09      39 of 40
  Roaming    13       5,587    24.17      19 of 40

Interpretation C (per-state 80% marginal threshold):

  Condition                  Neurons  Frames  n_eff_p25  Viable
  CePNEM dwelling            53       166     36.07      False
  CePNEM roaming             48       0       0.0        False
  GCaMP dwelling             53       166     20.44      False
  GCaMP roaming              48       0       0.0        False

Root cause: 80% marginal-presence + complete-case collapse. Each recording
has ~50–58 of the 61 subgraph neurons; missing neurons differ across animals.
After including neurons present in ≥32/39 (dwelling) or ≥16/19 (roaming)
recordings, only 1 dwelling recording has all included neurons (166 frames),
and no roaming recording has all included neurons simultaneously.

### Construction-B Tradeoff (COMPLETE)

Full greedy sweep over all K × N operating points, all four state × coordinate
combinations. No operating point achieves N ≥ 61 neurons and K ≥ 19 roaming
recordings simultaneously. Full table: results/phase1/data/construction_b_tradeoff.json

### Joint Subgraph Analysis (COMPLETE)

Largest joint subgraph with full roaming and dwelling coverage
(K_roam = 19, K_dwell = 34): 13 neurons — entirely pharyngeal and head sensory
(M3L, M3R, I2L, I3, IL2DL, OLQDL, CEPDL, OLQDR, RMEL, RMER, RIVL, RID, I2R).
No canonical locomotion interneurons present (AVA, RIM, AIY, AIA absent).
Full table: results/phase1/data/joint_subgraph_tradeoff.json

### Dwelling-vs-Baseline Feasibility at K=34 (COMPLETE)

11 neurons; 55 total pairs; 7 on-connectome; 48 off-connectome; 16 neuropeptide-
annotated off-connectome. Dwelling: 26,961 frames, n_eff=26.9. Baseline-A:
31,085 frames, n_eff=79.9. PRIMARY_TOP_K=50 not executable (50 > 48 off-connectome).
Signal diluted ~7.7× (dwelling = 87% of baseline pool).

### Corpus-Feasibility Audit (COMPLETE)

7 public NeuroPAL Ca²⁺ datasets surveyed (118 animals, 5 labs).
Source: Sprague, Rusch et al. 2025, Cell Reports Methods, PMC11840940.

  Dataset             N    Freely behaving  Ca²⁺  Avg neurons labeled  % of 302
  NP (Yemini)         10   No               No    190                  63%
  EY (Yemini lab)     21   No (microfluid)  Yes   175                  58%
  KK (Kimura lab)     9    No (microfluid)  Yes   154                  51%
  HL (Chaudhary/Lu)   9    No               No    64                   21%
  SF (Atanas/Flavell) 38   YES              YES   70                   23%  ← only
  SK1 (Kato lab)      21   No               Part  48                   16%
  SK2 (Kato lab)      10   No               No    49                   16%

SF is the only freely-behaving + Ca²⁺ + neuron ID dataset in the public corpus.
Per-animal coverage ceiling (~70 neurons, 23% of 302) is optical/motion-limited.
Automated re-ID pipelines cannot recover neurons below optical resolution floor.
Adding more SF-type animals does not increase the complete-case intersection.

---

## 3. Exact Reason Phase 1 Is Not Executable

The locked parameters N_COMMON_NEURONS = 61 and
MISSING_NEURON_POLICY = "nan_complete_case" are jointly unachievable on the
Atanas SF freely-behaving corpus.

The 61-neuron subgraph was defined by marginal presence (≥80% of recordings).
Complete-case estimation requires all 61 neurons to be present simultaneously
in each contributing recording. Because different recordings are missing
different neurons, the complete-case intersection is 4 neurons.

This is a set-intersection property of the recording-level neuron presence
matrix. No threshold adjustment, re-identification effort, or corpus expansion
resolves it. The SF dataset is the only freely-behaving calcium imaging dataset
with neuron identification in the world (2026-05-31).

Failure point: Stage 1.1, Gate A, data-object assembly — before any
statistical estimation is attempted.

---

## 4. Evidence

  E1  Gate A pilot (strict): dwelling 4 neurons; roaming 13 neurons
  E2  Interpretation C: dwelling 166 frames (1 recording); roaming 0 frames
  E3  Construction-B sweep: no point achieves N≥61 and K≥19 roaming simultaneously
  E4  Joint subgraph ceiling: 13 neurons; no locomotion interneurons
  E5  Dwelling-vs-baseline: signal diluted 7.7×; PRIMARY_TOP_K not executable
  E6  Corpus audit: SF is the only freely-behaving dataset; 70-neuron ceiling
      is optical/motion hardware-limited; automated re-ID cannot help

---

## 5. Nature of the Failure

This is a dataset and observability limitation.

It is NOT an implementation failure: Stage 1.0 and Gate A executed correctly
with no errors. All scripts produced verified outputs.

It is NOT a statistical failure: the GLASSO estimators, regularization
parameters, n_eff thresholds, and stability-selection procedure are not
implicated. They remain Phase 0-validated for their intended application.

It is NOT a coding failure: nan_complete_case is correctly implemented and
applied. The supplementary coverage scripts, Construction-B analysis, and
joint-subgraph computations performed as designed.

The failure is external to the analysis pipeline. The freely-behaving NeuroPAL
imaging modality cannot resolve sufficient neurons per animal simultaneously to
produce the 61-neuron complete-case pooled matrix that Phase 1 requires.

---

## 6. Lessons Learned

L1 — Simultaneous observability must be checked before subgraph lock.
  The marginal-presence criterion (≥80% per neuron) does not answer "how many
  neurons can be included in a complete-case pooled matrix." The Construction-B
  quantity — the largest N such that K recordings simultaneously contain all N
  neurons — must be computed as part of the subgraph-definition step.

L2 — Complete-case pooling and recording-level missingness are fundamentally
  incompatible at scale when different recordings are missing different neurons.
  At N=61 with ~8 missing neurons per recording drawn from different positions,
  the probability of simultaneous presence in any recording is near zero.

L3 — Per-animal neuron identification coverage in free movement is far below
  immobilized coverage (23% vs. 51–63%), and this gap is hardware-limited.
  Immobilized datasets cannot substitute because they lack behavioral correlates.

L4 — The SF dataset is the only freely-behaving whole-brain identified-neuron
  corpus in the field. No second dataset exists to expand to.

---

## 7. Recommended Successor Projects

SUCCESSOR-A — Phase 2: Pairwise-Estimator Extension
  Same biological question; replace nan_complete_case with pairwise or EM-based
  precision estimator. Requires new Phase 0-equivalent validation under SF
  missingness structure. Classification: new project.

SUCCESSOR-B — RC/Model-Based Branch
  Population-level hierarchical graphical model marginalizing over per-animal
  neuron subsets. Requires new statistical framework and validation.
  Classification: new project with reframed scientific question.

SUCCESSOR-C — Future Experimental Branch
  Improve per-animal coverage in freely-behaving recordings through faster
  volumetric acquisition or motion-corrected NeuroPAL. At ≥90% per-animal
  coverage, the original Phase 1 object becomes constructible.
  No computational action required now.

---

## 8. Reusable Assets

  results/phase1/data/cepnem_residuals/           40 .npz files; valid
  results/phase1/data/construction_b_tradeoff.json all feasible complete-case operating points
  results/phase1/data/joint_subgraph_tradeoff.json joint roaming+dwelling operating points
  results/phase1/data/supplementary_coverage.json  marginal and complete-case frame counts
  results/phase1/data/supplementary_coverage_neuron_table.json  per-neuron presence detail
  src/cepnem_residualize.py                        verified correct
  scripts/phase1/stage0_cepnem.py                  including build_label_maps()
  scripts/phase1/stage1_supplementary_coverage.py  estimator-agnostic coverage/n_eff tools
  src/estimators.py                                Phase 0-validated GLASSO; complete-case only
  phase0_config.py                                 behavioral segmentation and connectome
                                                   parameters carry forward
  scripts/stage06_neff_stationarity.py             behavioral segmentation and n_eff pipeline
  herm_full_edgelist_MODIFIED.csv                  connectome adjacency; carry forward
  scripts/stage08_estimator_dryrun.py              Phase 0 regime thresholds; reference only;
                                                   do not transfer to pairwise/EM estimators
                                                   without re-validation

---

## Authorization State at Closure

No further Phase 1 computation is authorized.
Phase 2 has not been authorized.
No successor-direction work may begin without a separate project kickoff
and explicit human authorization.
