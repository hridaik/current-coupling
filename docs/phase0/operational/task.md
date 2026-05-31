# task.md — C. elegans Phase 0
## Feasibility Assessment, Preprocessing Lock, and Hypothesis Specification

---

## Naming convention

Throughout this document:

- **Phase 0** refers to the entire pre-analysis program.
- **Stages 1–10** refer to the operational steps within Phase 0.
- Script names use `stage01_...` through `stage10_...`.
- No state-conditioned precision matrix from real behavioral data may be computed until Phase 0 is complete.

---

## Scientific purpose

This Phase 0 exists to protect the integrity of the main analysis. Its job is to determine
everything that can be determined — about dataset compatibility, statistical feasibility,
preprocessing choices, and the estimation pipeline — before any state-conditioned precision
matrix is computed from real behavioral data. It produces four locked artefacts:

1. A feasibility report from Stages 1–6
2. A frozen preprocessing specification (`phase0_config.py`, fully populated)
3. An estimation pipeline validated on synthetic data in Stage 8
4. A locked primary hypothesis statement with pre-defined null models from Stages 9–10

The main analysis (ΔQ, D_C ΔQ, enrichment against neuropeptide/serotonin/PDF resources,
prospective mutant predictions) proceeds only after all four artefacts are complete and the
human has signed off on each decision checkpoint.

The scientific question the main analysis will address: does the conditional-dependence
structure of identified C. elegans neurons differ between roaming and dwelling behavioral
states in a way that (a) cannot be attributed to the fixed synaptic connectome and (b) is
enriched for non-synaptic signaling? Phase 0 determines whether the available data and
methods can address that question credibly.

---

## THE HARD CONSTRAINT: NO ΔQ ON REAL DATA DURING PHASE 0

The following are **ABSOLUTELY FORBIDDEN** during Phase 0:

- Computing state-conditioned precision matrices Q_roam or Q_dwell from real behavioral data
- Computing ΔQ = Q_roam − Q_dwell from real behavioral data
- Computing Ω_s, D_C ΔQ, or any current-velocity-based statistic from real behavioral data
- Running any enrichment test against the neuropeptide, Randi, serotonin/PDF, or any
  biological annotation resource using real ΔQ outputs as input

The following are **PERMITTED** during Phase 0:

- Computing state-conditioned covariance matrices Σ_s (not precision) for the purpose of
  n_eff estimation, stationarity testing, and inter-animal variability assessment
- Computing precision matrices on **synthetic** data to test the estimation pipeline
- Running power simulations using synthetic pair lists

The reason: all preprocessing decisions, threshold values, estimator choices, and the primary
hypothesis must be locked before the state-conditioned precision structure is observed.
Informing any decision with a preview of ΔQ makes the final enrichment test uninterpretable.

**Any action that computes Q_s or ΔQ on real behavioral data is a critical deviation.
Stop immediately and notify the human.**

---

## Code-level guardrail for the hard constraint

Every function that computes a precision matrix, graphical-lasso estimate, inverse covariance,
or ΔQ-like object must require an explicit argument:

```python
data_kind: Literal["synthetic", "real"]
```

During Phase 0:

* If `data_kind == "real"`, precision estimation must raise `RuntimeError`.
* Synthetic precision estimation is allowed only for Stage 8 estimator validation.
* Add a unit test verifying that real behavioral data cannot be passed into precision-estimation code during Phase 0.

Real-data covariance estimation remains allowed.

---

## External data access

If an external repository, supplementary file, package, Git LFS resource, or browser download
cannot be accessed:

1. Stop and report the exact missing resource.
2. Record the issue in `PROGRESS.md` and `CONTEXT.md`.
3. Do not substitute unrelated data.
4. Use mock data only for synthetic pipeline tests, never for biological feasibility conclusions.

---

## Primary references

**Dataset: C. elegans whole-brain calcium imaging**
Atanas AA, Kim J, Wang Z, et al. Brain-wide representations of behavior spanning multiple
timescales and states in C. elegans. Cell 186:4134–4151.e31, 2023.
GitHub: [https://github.com/flavell-lab/AtanasKim-Cell2023](https://github.com/flavell-lab/AtanasKim-Cell2023)
Browser: [https://wormwideweb.org](https://wormwideweb.org)

**Dataset: Connectome-constrained linear dynamical system**
Creamer MS, Leifer AM, Pillow JW. Bridging the gap between the connectome and whole-brain
activity in C. elegans. bioRxiv 2024.09.22.614271, 2024.
GitHub: [https://github.com/Nondairy-Creamer/Creamer_LDS_2024](https://github.com/Nondairy-Creamer/Creamer_LDS_2024)

**Dataset: C. elegans synaptic connectome**
Cook SJ, Jarrell TA, Brittin CA, et al. Whole-animal connectomes of both C. elegans sexes.
Nature 571:63–71, 2019.
Witvliet D, Mulcahy B, Mitchell JK, et al. Connectomes across development reveal principles
of brain maturation. Nature 596:257–261, 2021.
Access via: [https://github.com/openworm/ConnectomeToolbox](https://github.com/openworm/ConnectomeToolbox) or wormneuroatlas

**Dataset: Neural signal propagation atlas with optogenetic perturbations**
Randi F, Sharma AK, Dvali S, Leifer AM. Neural signal propagation atlas of C. elegans.
Nature 623:406–414, 2023.
Access via: [https://github.com/francescorandi/wormneuroatlas](https://github.com/francescorandi/wormneuroatlas)

**Dataset: Neuropeptide signaling connectome**
Ripoll-Sánchez L, Watteyne J, Sun H, et al. The neuropeptidergic connectome of C. elegans.
Neuron 111:3570–3589.e5, 2023.
Supplementary data available from the Neuron paper.

**Dataset: Serotonin brain-wide imaging and receptor genetics**
Dag U, Nwabudike I, Kang D ... Flavell SW.
Dissecting the functional organization of the C. elegans serotonergic system at whole-brain scale
Cell, 2023; 186, 2574-2592.e20

**Dataset: Roaming/dwelling circuit and neuromodulatory control**
Ni Ji, Flavell SW. A neural circuit for flexible control of persistent behavioral states.
eLife 10:e62889, 2021.

**RC model (user-provided)**
"Optimizing Reservoir Computing for Reconstructing Ergodic Properties" (arxiv preprint).
Check user for exact citation and code location before beginning Stage 4.

**Theory**
Khurana H. One wiring, two functions: identifying state-dependent functional organization
in driven circuits with a current-velocity diagnostic for approximate Markov blankets and
polycomputing. Draft 2026. (The paper whose C. elegans extension this analysis implements.)

---

## Verified dataset properties

The following are established from the primary references and may be treated as ground truth.
Hard-code in `phase0_config.py` under `VERIFIED`.

```python
# ---------------------------------------------------------------
# VERIFIED — do not change without a new primary source
# ---------------------------------------------------------------

# Atanas 2023
ATANAS_SAMPLING_HZ   = 5.0       # volumetric rate, Hz [Atanas 2023 methods]
ATANAS_INDICATOR     = "GCaMP6s" # nuclear-localized [Atanas 2023 methods]
ATANAS_N_ANIMALS_APPROX = 30     # ~30 animals with NeuroPAL identification [Atanas 2023]
ATANAS_GITHUB        = "https://github.com/flavell-lab/AtanasKim-Cell2023"

# C. elegans nervous system
N_NEURONS_TOTAL      = 302       # hermaphrodite [White et al. 1986]
N_HEAD_NEURONS_APPROX = 180      # head ganglion, approximate [multiple sources]

# Cook / Witvliet connectome
COOK_N_NEURONS       = 302       # both sexes [Cook et al. 2019]
COOK_N_SYNAPSES_APPROX = 7000    # chemical + gap junction, approximate [Cook 2019]
CONNECTOME_GITHUB    = "https://github.com/openworm/ConnectomeToolbox"

# Randi 2023
RANDI_N_PAIRS        = 23433     # measured neuron pairs, head [Randi 2023 abstract]
RANDI_PREPARATION    = "immobilized"  # head ganglion [Randi 2023 methods]
RANDI_GITHUB         = "https://github.com/francescorandi/wormneuroatlas"

# Creamer 2024
CREAMER_GITHUB       = "https://github.com/Nondairy-Creamer/Creamer_LDS_2024"
CREAMER_MODEL_TYPE   = "noisy_linear_dynamical_system"  # [Creamer 2024 abstract]
CREAMER_CONNECTOME_CONSTRAINED = True   # [Creamer 2024: nonzero weights only at synapses]
```

---

## Required `phase0_config.py` schema

Create `phase0_config.py` before Stage 1. It is the single source of truth for all paths,
parameters, and human decisions. It must contain at least the following sections.

```python
# phase0_config.py — required schema

# ----------------
# VERIFIED
# ----------------
ATANAS_SAMPLING_HZ = 5.0
ATANAS_INDICATOR = "GCaMP6s"
ATANAS_N_ANIMALS_APPROX = 30
ATANAS_GITHUB = "https://github.com/flavell-lab/AtanasKim-Cell2023"

N_NEURONS_TOTAL = 302
N_HEAD_NEURONS_APPROX = 180

COOK_N_NEURONS = 302
COOK_N_SYNAPSES_APPROX = 7000
CONNECTOME_GITHUB = "https://github.com/openworm/ConnectomeToolbox"

RANDI_N_PAIRS = 23433
RANDI_PREPARATION = "immobilized"
RANDI_GITHUB = "https://github.com/francescorandi/wormneuroatlas"

CREAMER_GITHUB = "https://github.com/Nondairy-Creamer/Creamer_LDS_2024"
CREAMER_MODEL_TYPE = "noisy_linear_dynamical_system"
CREAMER_CONNECTOME_CONSTRAINED = True

# ----------------
# PATHS
# ----------------
DATA_ROOT = None
ATANAS_PATH = None
CREAMER_PATH = None
CONNECTOME_PATH = None
RANDI_PATH = None
NEUROPEPTIDE_PATH = None
RESULTS_DIR = "results"
RANDOM_SEED = 20260527

# ----------------
# CREAMER
# ----------------
CREAMER_TIME_CONVENTION = None
CREAMER_DT = None
CREAMER_MAX_EIGENVALUE = None
CREAMER_STABLE = None
CREAMER_DC_AVAILABLE = None
CREAMER_D_TYPE = None
CREAMER_LABEL_CONVENTION = None
CREAMER_SIGMA_POSDEF = None
CREAMER_OMEGA_NORM = None

# ----------------
# RC
# ----------------
RC_CODE_PATH = None
RC_OUTPUT_NEURON_COORDS = None
RC_OUTPUT_JACOBIAN_AVAILABLE = None
RC_STATE_CONDITIONED = None
RC_NEURON_COVERAGE = None
RC_ROLE_SAMPLING = None
RC_ROLE_JACOBIAN = None
RC_ROLE_DRIVE_SWEEP = None

# ----------------
# SUBGRAPH / HARMONIZATION
# ----------------
LR_POLICY = "separate"
IDENTITY_CONFIDENCE_THRESHOLD = None
N_COMMON_NEURONS = None
SUBGRAPH_ADEQUATE = None
SYNAPSE_COUNT_THRESHOLD = 1
SYNAPSE_COUNT_THRESHOLD_SENSITIVITY = 3
N_RANDI_SUBGRAPH_PAIRS = None

# ----------------
# PREPROCESSING / STATES
# ----------------
COORD_PRIMARY = None
COORD_ROBUSTNESS_1 = None
COORD_ROBUSTNESS_2 = None
DECONV_AVAILABLE = None
NORMALIZATION = "z_score_global"
MISSING_NEURON_POLICY = "nan_complete_case"
BEHAVIOR_SCORE_SOURCE = None
BEHAV_THRESHOLD = None
BEHAV_THRESHOLD_RULE = None
W_TRANS_SECONDS = 30.0
MIN_BOUT_SECONDS = None
COORD_INTERP_RULE = None

# ----------------
# N_EFF / STATIONARITY
# ----------------
NEFF_METHOD = "cross_product_integrated_autocorrelation"
NEFF_K_MAX_FRAMES = 200
ESTIMATOR_TIER = None
NONSTATIONARITY_FRACTION = None

# ----------------
# INTER-ANIMAL / ESTIMATION
# ----------------
OUTLIER_ANIMALS = None
EXCLUDED_ANIMALS_PRIMARY = None
POOLING_STRATEGY = None
DISCOVERY_ESTIMATOR = "unstructured_stability_selection"
CONFIRMATION_ESTIMATOR = "anatomy_guided_lasso"
LAMBDA_ON = None
LAMBDA_OFF = None
LAMBDA_OFF_ON_RATIO = None
NFOLDS = None
CV_FOLD_ASSIGNMENTS_PATH = None

# ----------------
# ENRICHMENT / NULLS
# ----------------
PRIMARY_ENRICHMENT_STAT = "AUROC"
SECONDARY_ENRICHMENT_STAT = "Fisher_topK"
NULL_MODEL_PRIMARY = None
ENRICHMENT_POWER_AT_OR2 = None

# ----------------
# HYPOTHESIS LOCK
# ----------------
PRIMARY_HYPOTHESIS_TEXT = None
PRIMARY_TOP_K = None
D_ROBUSTNESS_RHO = None
PHASE0_COMPLETE = False
```

All human-decision fields start as `None`. Any script that uses such a field must assert
that it has been set.

---

## Repository scaffold

```
src/
  data_access.py         # load Atanas, Creamer, connectome, Randi, neuropeptide data
  harmonization.py       # neuron name mapping across all datasets; master table
  preprocessing.py       # CePNEM residuals, raw GCaMP, deconvolution; normalization;
                         # epoch segmentation; left/right policy; missing-neuron handling
  neff.py                # integrated autocorrelation time; n_eff for cross-products
  stationarity.py        # rolling covariance; first/second-half comparison; spectral checks
  variability.py         # inter-animal covariance consistency; PCA summary
  estimators.py          # stability selection; anatomy-guided lasso; connectome prior
  enrichment.py          # Fisher test; AUROC; Mann-Whitney; GSEA-style ranking test
  power_analysis.py      # enrichment power under synthetic null and synthetic signal
  null_models.py         # degree-, class-, proximity-, neuropeptide-degree-aware permutation
  plotting.py            # diagnostic figures
scripts/
  stage01_creamer_check.py      # Stage 1: Creamer LDS feasibility checks
  stage02_subgraph.py           # Stage 2: common identified-neuron subgraph construction
  stage03_randi_extraction.py   # Stage 3: Randi unc-31-sensitive pair rankings, harmonization
  stage04_rc_check.py           # Stage 4: RC implementation check
  stage05_preprocessing.py      # Stage 5: implement coordinate systems and state threshold diagnostics
  stage06_neff_stationarity.py  # Stage 6: n_eff from cross-products; stationarity testing
  stage07_variability.py        # Stage 7: inter-animal consistency; estimator decision
  stage08_estimator_dryrun.py   # Stage 8: estimation pipeline on synthetic data
  stage09_power.py              # Stage 9: enrichment power; null model validation
  stage10_hypothesis_lock.py    # Stage 10: format and verify hypothesis document
phase0_config.py                # single source of truth for all parameters and decisions
PROGRESS.md                     # updated after every stage and checkpoint
CONTEXT.md                      # reasoning notes on non-obvious outcomes
CHECKPOINT_LOG.md               # record of all checkpoints and their outcomes
DEVIATIONS.md                   # record of all deviations from this spec
results/
  diagnostics/           # all Phase 0 numerical outputs (.npy, .csv, .json)
  figures/               # all diagnostic figures
tests/
  test_harmonization.py  # verify name-mapping table on known cases
  test_neff.py           # verify n_eff formula on AR(1) with known τ
  test_estimators.py     # verify stability selection and lasso on synthetic data
  test_enrichment.py     # verify enrichment tests on synthetic pair lists
  test_nulls.py          # verify null models preserve degree/class/proximity distributions
  test_phase0_guard.py   # verify real-data precision estimation is blocked during Phase 0
```

---

## Stage 1 — Creamer feasibility check and provisional RC triage

### Purpose

Determine whether the Creamer LDS can be used in the main analysis as intended, and make a
provisional triage of RC capabilities. If Creamer A_C is unstable or D_C is unavailable,
the current-velocity bridge step (D_C ΔQ) must use fallback estimates. If the RC does
not expose an output-space Jacobian over identified neurons, it is restricted to a
generative sampling or drive-sweep role.

Final RC role assignment is not locked until Stage 4.

### Tasks

**Creamer LDS:**

1. Clone or download the Creamer repository. Identify the exported model objects.
2. Determine whether the model is continuous-time (dx/dt = A_C x + noise) or
   discrete-time (x_{t+1} = A_C x_t + noise). Check the paper methods section and
   the repository README. Record in `phase0_config.py` under `CREAMER_TIME_CONVENTION`.
3. Load A_C. Check eigenvalues:

   * Continuous-time: stability requires max Re(λ_i(A_C)) < 0
   * Discrete-time: stability requires max |λ_i(A_C)| < 1
     Record max Re(λ) or max |λ| in `CREAMER_MAX_EIGENVALUE`.
4. If discrete-time: compute the continuous-time equivalent A_C^cont = (1/dt) log(A_C^disc)
   for use in the continuous-time Lyapunov equation. Document the time step dt. If the
   main analysis remains in discrete time, record that separately.
5. Check whether D_C is exported. D_C is the process-noise covariance, diagonal variance,
   or innovation covariance in the LDS equation. Record `CREAMER_DC_AVAILABLE = True/False`.
   If not available, record what is available.
6. Check neuron label convention in the Creamer model. Determine whether labels use
   NeuroPAL names, numeric indices, or another convention. Record in `CREAMER_LABEL_CONVENTION`.
7. If D_C is available and A_C is stable, compute Σ_C by solving the appropriate Lyapunov
   equation. Check that Σ_C is positive definite.
8. If Σ_C is positive definite, compute Ω_C = A_C + D_C Q_C where Q_C = Σ_C^{-1}.
   Record ||Ω_C||_F in `CREAMER_OMEGA_NORM`.
   This is the current structure the connectome-only model predicts — not zero in general.

Do not use a Frobenius-norm comparison between Creamer weights and raw synapse counts as a
pass/fail criterion. Raw connectome support and weight/count correlations may be recorded
later as diagnostics after Stage 2 harmonization.

**Provisional RC triage:**

1. Locate the RC code for "Optimizing Reservoir Computing for Reconstructing Ergodic
   Properties." Ask the human for the exact location if not found in the repository.
2. Determine whether the RC appears to produce outputs in identified-neuron coordinates
   (i.e., whether there is an output map W_out such that x_predicted = W_out r, where x is
   in identified-neuron space and r is the reservoir state).
3. Determine whether the RC appears to accept a behavioral-state context variable as input
   (enabling state-conditioned generation).
4. Record provisional values:

   * `RC_OUTPUT_NEURON_COORDS`
   * `RC_OUTPUT_JACOBIAN_AVAILABLE`
   * `RC_STATE_CONDITIONED`
   * `RC_NEURON_COVERAGE`

These are provisional until Stage 4 loads and runs the RC.

### Pass conditions

```
CREAMER_MAX_EIGENVALUE < 0 (continuous-time) or < 1 (discrete-time)
Σ_C positive definite if D_C is available and Lyapunov solve is attempted
Ω_C computed and recorded if D_C and Σ_C are available
All values written to phase0_config.py
CREAMER_DC_AVAILABLE recorded (True or False; fallback plan noted if False)
Provisional RC capability fields recorded
```

**HUMAN DECISION CHECKPOINT after Stage 1:**
The human reviews the Creamer stability report, D_C availability, and provisional RC capability summary.
Decisions to record in `phase0_config.py`:

* Whether to use Creamer D_C, fallback diagonal D, or identity for the current-velocity bridge
* Whether Stage 6/secondary Lyapunov comparison should proceed or fall back to sensitivity analysis
* Whether Stage 4 should attempt a full RC implementation check

Do not begin Stage 2 until the human has completed this checkpoint.

---

## Stage 2 — Common identified-neuron subgraph construction and harmonization

### Purpose

Build the single resource that every subsequent analysis depends on: a master harmonization
table mapping each identified neuron to its label in every dataset, and a common subgraph
object containing only neurons with confirmed identity in the Atanas 2023 recordings.

### Tasks

**Master harmonization table:**

1. Extract neuron labels from each of the following sources:

   * Atanas 2023 identified neurons (NeuroPAL names from WormWideWeb / GitHub data files)
   * Creamer LDS (whatever label convention was found in Stage 1)
   * Cook/Witvliet connectome (traditional 3-letter names from White et al. 1986 + L/R suffix)
   * Randi 2023 atlas (NeuroPAL or WormAtlas names from wormneuroatlas)
   * Ripoll-Sánchez neuropeptide connectome (neuron labels from supplementary data)
   * Serotonin/PDF annotations (from Wan et al. 2023 and Kim & Flavell 2021)
2. Build a CSV table `results/diagnostics/neuron_harmonization.csv` with one row per
   neuron and one column per dataset, containing the label as it appears in that dataset
   (or NaN if absent). The canonical key column uses NeuroPAL names.
3. For any neuron where the mapping is ambiguous (e.g., left/right homolog split differently
   across datasets), flag the row and write the ambiguity to CONTEXT.md.
   Do NOT silently resolve ambiguous mappings. Require human sign-off on each ambiguous case.

**Left/right homolog policy:**
The default is to treat bilateral pairs (e.g., AVAL / AVAR) as separate nodes. This must
be implemented in the harmonization table. Record `LR_POLICY = "separate"` in `phase0_config.py`.
The human may override this for specific neuron classes after reviewing the table.

**Common identified-neuron subgraph:**

4. Define the primary neuron set as: neurons identified with high confidence (confidence
   score ≥ threshold; see Stage 5) in ≥ 80% of Atanas animals, and present in both the
   Cook/Witvliet connectome and the Randi atlas. Record the count as `N_COMMON_NEURONS`.
5. Construct four binary adjacency matrices restricted to this subgraph:

   * `A_raw`: synaptic support from Cook/Witvliet (1 if ≥ 1 synapse; chemical + gap junction)
   * `A_gj`: gap junction only (for sensitivity)
   * `A_chem`: chemical synapse only
   * `A_peptide`: neuropeptide support from Ripoll-Sánchez (any ligand-receptor pair in
     either direction; undirected union)
6. Record synapse-count thresholds: primary uses ≥ 1 synapse; sensitivity uses ≥ 3 synapses.
   Record `SYNAPSE_COUNT_THRESHOLD = 1` in `phase0_config.py`.
7. Print the following statistics:

   * N_COMMON_NEURONS
   * Fraction of pairs that are synaptic (in A_raw)
   * Fraction of pairs that are peptidergic but not synaptic (in A_peptide AND NOT A_raw)
   * Fraction of Ripoll-Sánchez neuropeptide pairs in the common subgraph

Randi unc-31-sensitive pair coverage is not computed in Stage 2, because the Randi pair list
is extracted in Stage 3.

**HUMAN DECISION CHECKPOINT after Stage 2:**
The human reviews N_COMMON_NEURONS, the biological composition of the subgraph
(which named neurons are included and excluded), and the coverage fractions.
Decision: Is the common subgraph biologically adequate for testing the roaming/dwelling
state-switch hypothesis? If critical neurons (AVA, RIM, AIY, AIA, RIG) are absent,
the subgraph may need extension to a lower identity confidence threshold.
Record decision in `phase0_config.py` as `SUBGRAPH_ADEQUATE = True/False` with justification.

### Pass conditions

```
Harmonization table built with no silent ambiguity resolutions
All ambiguous cases flagged and noted in CONTEXT.md
N_COMMON_NEURONS ≥ 30 for pairwise analysis (below this: HUMAN_DECISION required on scope)
A_raw, A_gj, A_chem, A_peptide all restricted to common subgraph and saved to disk
Coverage fractions printed and recorded in PROGRESS.md
HUMAN DECISION CHECKPOINT completed and phase0_config.py updated
```

---

## Stage 3 — Randi unc-31-sensitive pair extraction

### Purpose

Build the ranked list of DCV-sensitive (neuropeptide-dependent) neuron pairs from Randi 2023.
This list is used in the enrichment test (Stage 9). It must be built and restricted to the
common subgraph before any ΔQ is computed.

### Tasks

1. Using the wormneuroatlas package (`pip install wormneuroatlas`), access the Randi 2023
   wild-type and unc-31 functional atlas data. Alternatively, load from the supplementary
   data files if the package is unavailable.
2. Use Randi et al.'s published response and significance metrics if available. If no
   published DCV-sensitivity metric is provided, compute:

   ```
   DCV_score(i,j) = WT_response(i,j) - unc31_response(i,j)
   ```

   where response is the documented calcium signal amplitude following optogenetic stimulation.
   Record the exact response amplitude and significance definition used.
3. Produce a ranked table of pairs by |DCV_score|, restricted to pairs where WT response
   is significant and unc-31 response is significantly reduced, if those significance labels
   are available.
4. Map all pairs to the common identified-neuron subgraph using the harmonization table.
   Record how many pairs survive the subgraph restriction.
5. Save the full ranked list and the subgraph-restricted list to
   `results/diagnostics/randi_dcv_pairs.csv`.
6. Report the fraction of Randi unc-31-sensitive pairs that fall in the common subgraph.

### Pass conditions

```
At least one successful data access route to Randi WT and unc-31 data
DCV_score or published equivalent defined and documented
Subgraph-restricted pair list saved
N_RANDI_SUBGRAPH_PAIRS recorded in phase0_config.py
```

---

## Stage 4 — RC implementation check and role assignment

### Purpose

Confirm the specific capabilities of the RC model and assign its role in the main analysis.
This stage requires the human to provide the RC code location if not already in the repository.

Stage 1 records provisional RC capabilities. Stage 4 confirms them by loading and, if possible,
running the RC. Final `RC_ROLE_*` fields are locked here.

### Tasks

1. Load the RC model. Verify it produces outputs in identified-neuron coordinates or
   that outputs can be mapped back to identified neurons.
2. Test state-conditioned generation if supported: provide a roaming context input and a
   dwelling context input; verify that the RC produces stationary-like trajectories in each
   condition. If the RC does not accept behavioral context, it can only be used for drive sweeps
   or unconditional sampling.
3. If an output-space Jacobian is available: compute J_RC as the Jacobian of the RC output
   dynamics at the mean state in each behavioral context. Verify it is numerically stable and
   has the correct dimensions (N_COMMON_NEURONS × N_COMMON_NEURONS). Do not use a hidden
   reservoir Jacobian as a biological neuron-space J.
4. Assign the RC to its specific roles in phase0_config.py:

   ```
   RC_ROLE_SAMPLING = True/False     # generate long Σ_s estimates
   RC_ROLE_JACOBIAN = True/False     # provide J_RC for current-velocity bridge
   RC_ROLE_DRIVE_SWEEP = True/False  # vary drive input; replicate OU cascade
   ```

### Pass conditions

```
RC produces outputs in identified-neuron coordinates, or this is documented as impossible
RC_ROLE_* fields populated in phase0_config.py
If RC_ROLE_JACOBIAN: J_RC is N_COMMON_NEURONS × N_COMMON_NEURONS and saved
HUMAN DECISION: human confirms RC role assignment
```

---

## Stage 5 — Coordinate system implementation and behavioral-state threshold lock

### Purpose

Implement three coordinate systems for the neural activity data and lock the behavioral-state
threshold. The scientific default coordinate system is CePNEM residuals, but the final primary
coordinate is locked only at the human decision checkpoint.

### Coordinate systems

**Scientific default:** CePNEM residuals in identified-neuron coordinates.
CePNEM (from Atanas 2023) decomposes each neuron's calcium trace into a behavioral encoding
component and a residual. The residual controls for behavioral confounds: state-conditioned
differences in CePNEM residuals reflect neural organization beyond what the behavioral
kinematics explain.

**Robustness 1:** Processed raw GCaMP traces (ΔF/F, normalized per neuron, smoothed).
Results in raw GCaMP coordinates are interpreted as "current-like residuals in effective
calcium dynamics."

**Robustness 2:** Deconvolved activity estimates, if stable deconvolution is available
from the Atanas data pipeline. If deconvolution is not available or produces unstable
estimates (negative values, large amplitudes), omit and record `DECONV_AVAILABLE = False`.

### Behavioral-threshold independence requirement

The behavioral threshold must be based only on behavioral variables or state scores that are
independent of the neural residual covariance/precision analysis. If a proposed CePNEM state
score is derived using the same neural activity traces being analyzed, stop and require human
review before using it for state thresholding.

The threshold must not be chosen using any neural covariance, precision, ΔQ, enrichment,
or current-velocity output.

### Tasks

**For each coordinate system:**

1. Implement a preprocessing function in `src/preprocessing.py` that takes raw Atanas
   data for one animal and returns the neural activity matrix (T × N_COMMON_NEURONS).
2. Normalize: each neuron's trace has zero mean and unit variance across time,
   within the full recording (not per epoch). Record this as `NORMALIZATION = "z_score_global"`.
3. Handle missing neurons: if a neuron is absent from an animal's recording, fill with NaN
   for that animal; do not impute. Record `MISSING_NEURON_POLICY = "nan_complete_case"`.

**Freezing behavioral-state threshold:**

4. Load behavioral scores for all animals. For each animal, plot the kernel density
   estimate of the primary behavioral score across the full recording.
5. Identify the presence or absence of bimodality (roaming peak vs. dwelling peak).
   Record the KDE for each animal. Compute the Hartigan dip statistic for bimodality if
   the required package is available; otherwise record the fallback bimodality diagnostic used.
6. Print: fraction of animals with significant bimodality, median trough location
   between peaks, interquartile range of trough location across animals.
7. Save KDE plots to `results/figures/behavioral_score_kde.pdf`.

**Transition exclusion:**

8. Implement a transition exclusion window: epochs within W_trans seconds of a
   roaming↔dwelling boundary are excluded. Use `W_trans = 30.0` seconds as the default
   (recorded in `phase0_config.py`). The human may revise W_trans after seeing the
   epoch-duration distribution.
9. Compute the distribution of epoch durations after transition exclusion for both states.
   Report: median epoch duration, fraction of total recording time retained per state.

### Coordinate interpretation rule

The human decision checkpoint must pre-specify the interpretation rule:

* If ΔQ_CePNEM ≈ 0 but ΔQ_raw is significant: report as behavior-mediated state-dependent conditional structure.
* If both ΔQ_CePNEM and ΔQ_raw are significant: report as residual neural state organization.
* If ΔQ_CePNEM is significant but ΔQ_raw is weak: report as preprocessing-dependent or regression-unmasked; require robustness review.
* If both are near zero: report as null in this subgraph/coordinate system.

This rule must be recorded in `phase0_config.py` as `COORD_INTERP_RULE` before any real-data
precision analysis.

### Pass conditions

```
Three coordinate systems implemented in src/preprocessing.py where available
Preprocessing functions tested on one animal's data
Behavioral score KDE plots saved
Bimodality statistics computed and recorded
Epoch duration distribution computed for default W_trans
HUMAN DECISION CHECKPOINT:
  - Behavioral state threshold (BEHAV_THRESHOLD) set in phase0_config.py
  - Threshold justified by behavioral score distribution, NOT by neural output
  - W_trans confirmed or revised
  - COORD_PRIMARY, COORD_ROBUSTNESS_1, COORD_ROBUSTNESS_2 set
  - COORD_INTERP_RULE set
```

Do not begin Stage 6 until the human has set BEHAV_THRESHOLD in phase0_config.py.

---

## Stage 6 — n_eff computation and stationarity testing

### Purpose

Determine the effective sample size per behavioral state and assess whether within-state
neural dynamics are sufficiently stationary for the precision matrix analysis. Both outcomes
directly determine which estimation approach is used in Stage 7.

### n_eff computation

For the primary coordinate system, within sustained behavioral state epochs using the
threshold and exclusion window from Stage 5:

1. For each animal, for each behavioral state s ∈ {roaming, dwelling}, extract all epoch
   segments passing the inclusion criteria.

2. Do not compute autocorrelation across epoch boundaries or animal boundaries. Compute
   autocorrelation within each epoch, then aggregate effective sample sizes across independent
   epoch blocks and animal blocks.

3. Compute the integrated autocorrelation time for the cross-products x_i · x_j:

   ```
   τ_int(i,j) = 1 + 2 · Σ_{k=1}^{K} ρ_ij(k)
   ```

   where ρ_ij(k) is the sample autocorrelation of x_i(t)·x_j(t) at lag k within an epoch,
   and K is the first lag where ρ_ij(k) < 2/sqrt(T) (standard 95% significance bound).
   Use K_max = 200 frames (40 seconds) as a hard cutoff.

4. Compute n_eff(i,j) ≈ T_epoch / τ_int(i,j) for each pair (i,j), epoch, animal, and state.
   Aggregate additively across independent epoch blocks:

   ```
   n_eff_animal_state(i,j) = sum_epochs n_eff_epoch(i,j)
   n_eff_pooled_state(i,j) = sum_animals n_eff_animal_state(i,j)
   ```

5. Report, per animal per state:

   * Median n_eff across all pairs
   * 25th percentile n_eff (conservative estimate)
   * n_eff / N_COMMON_NEURONS ratio at median and 25th percentile

6. Report pooled n_eff by summing animal-level n_eff values. Do not compute autocorrelation
   across animal boundaries.

7. Apply the decision rule:

   ```
   If n_eff_25th_percentile / N_COMMON_NEURONS ≥ 5 per state per animal:
       ESTIMATOR_TIER = "animal_level"   (animal-level precision estimation may be attempted)
   If n_eff_25th_percentile / N_COMMON_NEURONS ∈ [1, 5):
       ESTIMATOR_TIER = "pooled_hierarchical"  (must pool with hierarchical shrinkage)
   If pooled n_eff / N_COMMON_NEURONS < 1:
       ESTIMATOR_TIER = "blockwise"      (full precision estimation not feasible; descope)
   ```

   Record ESTIMATOR_TIER in `phase0_config.py`.

The final feasibility of animal-level precision estimation depends on Stage 8 synthetic recovery,
not n_eff alone.

### Stationarity testing

8. For each animal-state pair with ≥ 2 sustained epochs of ≥ 60 seconds each:

   * Compute the sample covariance matrix Σ_first (first half of frames in state) and
     Σ_second (second half of frames in state).
   * Compute Frobenius distance ||Σ_first - Σ_second||_F / ||Σ_first||_F.
   * Record as within-state covariance drift.

9. Compute rolling covariance with window = 30 seconds and step = 10 seconds for a
   representative subset of animals. Plot as heatmaps over time.
   Save to `results/figures/rolling_covariance.pdf`.

10. Perform a spectral check: compute the power spectrum of each neuron's trace within
    roaming epochs. Flag any neurons with significant spectral power at periods > 120 seconds,
    as these may indicate non-stationarity or cyclostationarity.

11. Check bout-phase dependence: compare covariance in early, middle, and late portions of
    sustained bouts when enough data are available. If covariance depends strongly on bout
    phase, flag possible cyclostationarity.

12. Record the fraction of animal/state/pair or animal/state/block combinations where
    normalized within-state covariance drift > 0.3. Record as `NONSTATIONARITY_FRACTION`
    in `phase0_config.py`.

Stationarity metrics are diagnostic during Phase 0. Epoch or animal exclusion thresholds
require human approval and must be locked before the main analysis.

### Pass conditions

```
n_eff computed from cross-products x_i x_j (not marginals)
n_eff decision rule applied and ESTIMATOR_TIER set
Stationarity drift computed and NONSTATIONARITY_FRACTION recorded
Cyclostationarity diagnostics recorded
If NONSTATIONARITY_FRACTION > 0.3: flag for human review before Stage 7
All outputs saved to results/diagnostics/neff_report.json
```

---

## Stage 7 — Inter-animal variability and estimator selection

### Purpose

Characterize how consistent the neural covariance structure is across animals within each
behavioral state, and determine the final estimation strategy based on all feasibility
findings so far.

### Tasks

1. For each animal, compute a summary covariance matrix Σ_animal_s by pooling that
   animal's frames in state s. This is NOT the full precision matrix — compute covariance
   only, not its inverse.

2. Compute the leading K=5 principal components of each Σ_animal_s.
   Check that the top-K eigenvectors are consistent across animals using cosine similarity.
   Report: median pairwise cosine similarity of top eigenvectors across all animal pairs.

3. Compute the element-wise correlation of Σ_animal_s across animals:
   for each pair (animal_a, animal_b), compute the Pearson correlation of
   vec(Σ_animal_a_s) and vec(Σ_animal_b_s). Report the distribution of these correlations
   separately for roaming and dwelling.

4. Identify candidate outlier animals (bottom 10% by mean inter-animal covariance correlation).
   Record their IDs in `phase0_config.py` as `OUTLIER_ANIMALS`.
   Do not automatically exclude outlier animals from the primary analysis. Exclusion requires
   a human decision and must be recorded in `EXCLUDED_ANIMALS_PRIMARY` with a technical
   justification. Default is to retain all animals.

5. Based on ESTIMATOR_TIER (Stage 6), NONSTATIONARITY_FRACTION, and the inter-animal
   consistency results, implement the estimation pipeline.

   **Discovery estimator (always implemented):**
   Unstructured stability selection with graphical lasso. Procedure:

   * Define B = 50 bootstrap subsamples of animals (or of frames if animal count < 20).
     Each subsample uses half the animals (or half the frames) drawn without replacement.
   * For each subsample, fit graphical lasso with λ chosen by 5-fold cross-validation on
     that subsample (or by BIC if n_eff is too low for CV).
   * Stability score for each edge (i,j): fraction of subsamples where that edge is selected.
   * Threshold stability at 0.75 for the primary result; report stability curves.

   **Confirmation estimator (always implemented):**
   Anatomy-guided lasso. Connectome-weighted penalties:

   * λ_off = LAMBDA_OFF for positions where A_raw = 0 (off-connectome)
   * λ_on  = LAMBDA_ON  for positions where A_raw = 1 (on-connectome)
   * Default: LAMBDA_OFF = 10 × LAMBDA_ON (stronger penalty on off-connectome entries)
   * Tune LAMBDA_ON by cross-validation on held-out animals.
     Record LAMBDA_OFF and LAMBDA_ON in `phase0_config.py`.

   **Circularity / conservativeness control:**
   The anatomy-guided estimator penalizes off-connectome entries MORE HEAVILY.
   It is therefore conservative against off-connectome discoveries.

   * Use the unstructured stability-selection estimator for discovery.
   * Use the anatomy-guided estimator as conservative confirmation.
   * If an off-connectome entry appears in both, it has higher confidence.
   * If it appears only in the unstructured estimator and vanishes under anatomy-guided penalties,
     it has lower confidence.
   * Never use the anatomy-guided estimator alone to claim an off-connectome result.

6. Define nested animal-level cross-validation:

   * Divide animals into NFOLDS = 5 folds, stratified by behavioral state balance where possible.
   * Record fold assignments in `results/diagnostics/cv_folds.json`.
   * Use leave-one-fold-out: preprocessing choices and regularization parameters are tuned
     on the training folds; final pair stability is assessed on held-out folds.
     Record NFOLDS in `phase0_config.py`.

### Pass conditions

```
Inter-animal covariance consistency quantified and recorded
Candidate outlier animals identified and recorded in OUTLIER_ANIMALS
No animal excluded from primary analysis without human approval
Stability selection pipeline implemented and tested on synthetic data in Stage 8
Anatomy-guided lasso implemented
CV fold structure defined and saved
HUMAN DECISION CHECKPOINT:
  - Human reviews inter-animal consistency, ESTIMATOR_TIER, NONSTATIONARITY_FRACTION
  - Confirms LAMBDA_OFF / LAMBDA_ON ratio
  - Confirms NFOLDS and fold strategy
  - Signs off on ESTIMATOR_TIER or escalates to blockwise if needed
  - Records POOLING_STRATEGY: "animal_level", "pooled", or "hierarchical"
  - Records EXCLUDED_ANIMALS_PRIMARY, if any
```

---

## Stage 8 — Estimation pipeline dry run on synthetic data

### Purpose

Verify that the full estimation pipeline (stability selection + anatomy-guided lasso +
nested CV) works correctly and produces interpretable output, before it is run on real
behavioral data. Use synthetic data only.

### Synthetic data generation

Generate a synthetic Gaussian dataset with the following known structure:

```python
# Synthetic ground truth
N = N_COMMON_NEURONS      # match real problem dimension
T_synth = 10000           # sufficient for ground truth

# True precision matrix: block structure matching connectome sparsity
Q_true_roam  # sparse, with some off-connectome entries set to a specified effect size
Q_true_dwell # same as Q_true_roam except selected off-connectome entries set to 0.0
# True ΔQ is entirely off-connectome
```

Use pre-specified synthetic effect sizes corresponding to plausible standardized partial-correlation
changes, for example 0.1, 0.2, and 0.3. The moderate effect setting is 0.2 unless the human
sets a different value before this stage.

1. Generate multivariate Gaussian samples X_roam ~ N(0, Q_true_roam^{-1}) and
   X_dwell ~ N(0, Q_true_dwell^{-1}), with sample sizes matching empirical n_eff estimates.
2. Run stability selection on X_roam and X_dwell separately.
3. Run anatomy-guided lasso on X_roam and X_dwell.
4. Compare recovered synthetic ΔQ to true synthetic ΔQ. Compute:

   * True positive rate for off-connectome entries (recovered with stability ≥ 0.75 in
     discovery estimator)
   * False positive rate on on-connectome entries
   * Whether the same off-connectome entries survive the anatomy-guided lasso
5. Report whether the conservative confirmation control works: synthetic off-connectome
   entries of the pre-specified effect size should survive the anatomy-guided lasso despite
   heavier off-connectome penalty.

### Unit tests for all core functions

Run the full test suite before proceeding:

```
pytest tests/test_harmonization.py  # known-case name mappings
pytest tests/test_neff.py           # AR(1) with known τ; verify n_eff
pytest tests/test_estimators.py     # recovery on synthetic data
pytest tests/test_enrichment.py     # enrichment test on synthetic pair list with known signal
pytest tests/test_nulls.py          # null models preserve degree/class/proximity/peptide-degree
pytest tests/test_phase0_guard.py   # real-data precision estimation blocked during Phase 0
```

All tests must pass before Stage 9.

### Pass conditions

```
All pytest tests pass
Synthetic ΔQ recovery at moderate effect size: true positive rate ≥ 0.6 at n_eff matching empirical estimates
Conservative confirmation verified: synthetic off-connectome entries survive anatomy-guided lasso at moderate effect size
No silent numerical failures (negative eigenvalues, NaN in Q, convergence warnings, etc.)
```

If Stage 8 fails because empirical n_eff is too low or the estimator is underpowered, stop and
diagnose before changing any estimator, regularization value, or synthetic effect size.

---

## Stage 9 — Enrichment power analysis and null model validation

### Purpose

Determine whether the enrichment tests planned for the main analysis are well-powered given
the restricted subgraph, and validate the null models.

### Tasks

1. Implement the primary enrichment test:

   * Input: synthetic ranked list of pairs by |ΔQ_ij| (off-connectome only)
   * Annotation: binary label for each pair — is this pair in the neuropeptide connectome
     (A_peptide)?
   * Statistic: AUROC (ranking-based); secondary: Fisher test on top-K pairs
   * Primary null: degree-, class-, proximity-, and neuropeptide-degree-aware permutation
     restricted to the common identified-neuron subgraph.

2. Null model fallback hierarchy:

   * First attempt exact degree-preserving or degree-constrained rewiring/permutation where feasible.
   * If exact preservation is infeasible in the restricted subgraph, use degree- and class-stratified permutation.
   * If permutation constraints remain infeasible, use conditional logistic/ranking regression with covariates:
     synaptic degree, neuropeptide degree, neuron class, spatial/anatomical proximity, and homolog status.
   * Record which null model is primary and why.

3. Run power simulation:

   * Specify a range of true enrichment effects: OR = {1.5, 2.0, 3.0, 5.0} (odds ratios
     for neuropeptide pairs appearing in top-K ΔQ)
   * For each OR, simulate 200 synthetic ΔQ ranked lists with that enrichment level
   * Compute power as fraction of simulations where enrichment p-value < 0.05
   * Report power curves vs. K (top-K threshold) for Fisher test and vs. OR for AUROC
   * Record `ENRICHMENT_POWER_AT_OR2` in `phase0_config.py`

4. Validate the null model preserves or controls for all four properties:

   * Node degree in A_raw
   * Node class (sensory, inter, motor)
   * Spatial/anatomical proximity or synaptic-hop distance
   * Node degree in A_peptide

5. Define the Randi unc-31-sensitive validation as a secondary test:

   * Same structure as neuropeptide test, using the DCV_score ranked list from Stage 3
   * Report power separately where possible

### Pass conditions

```
AUROC and Fisher enrichment tests implemented with documented null
Null model preserves or controls for degree, class, proximity, and neuropeptide degree
Power curves computed and saved
ENRICHMENT_POWER_AT_OR2 ≥ 0.6 (otherwise flag for human review — may require more animals
  or descoping to block analysis)
Randi secondary test implemented
```

---

## Stage 10 — Hypothesis lock

### Purpose

Lock the primary hypothesis, D-robustness criterion, and secondary analysis definitions
before any ΔQ is computed. This stage produces the locked hypothesis document.

### Tasks

The agent formats and checks internal consistency. The human writes the decision text.

1. Format the locked hypothesis as a structured document `results/hypothesis_lock.md`.
   The document must contain:

   **Primary hypothesis** (human-written):

   ```
   The top [K] stable off-synaptic ΔQ entries in [COORD_PRIMARY] — classified against
   both raw Cook/Witvliet connectome support and Creamer A_C support — are enriched for
   non-synaptic signaling annotations (neuropeptide connectome or Randi unc-31-sensitive
   relationships), using degree-, class-, proximity-, and neuropeptide-degree-aware
   permutation or regression nulls restricted to the [N_COMMON_NEURONS]-neuron identified subgraph.
   ```

   The human fills in K, COORD_PRIMARY, and N_COMMON_NEURONS and confirms the wording.

   **D-robustness go/no-go criterion** (human-written):

   ```
   Candidate rankings under D_C, residual diagonal D, and I must share a Spearman
   correlation of ≥ [RHO] in the top-K pairs. If not, D_C ΔQ is reported as inconclusive
   and the main claim rests on ΔQ alone.
   ```

   The human fills in RHO (suggested: 0.7).

   **Coordinate interpretation rule**:
   Copy COORD_INTERP_RULE from phase0_config.py into the document.

   **Secondary analyses** (pre-specified):

   * D_C ΔQ: current-velocity bridge (conditional on D-robustness)
   * Ω_C comparison: departure from Creamer synapse-only model (secondary, preparation mismatch acknowledged)
   * Sign-specific tests (positive vs. negative ΔQ entries, secondary)
   * RC drive sweeps (if RC_ROLE_DRIVE_SWEEP = True)
   * Homolog symmetrization sensitivity
   * Mutant predictions from the top enriched pairs

2. The agent checks the document for internal consistency:

   * K ≤ N_COMMON_NEURONS · (N_COMMON_NEURONS - 1) / 2
   * All referenced config values exist in phase0_config.py
   * Secondary analyses list does not include any primary-analysis outputs that would require previewing real ΔQ during Phase 0

3. Commit `results/hypothesis_lock.md` and tag the git repository as `phase0_complete`.
   If this is not a git repository, write a manifest with filenames and checksums to
   `results/diagnostics/phase0_manifest.json`.

### Pass conditions

```
hypothesis_lock.md complete with all fields filled by human
Agent consistency check passes
Git tag `phase0_complete` created, or manifest written if git unavailable
phase0_config.py fully populated (no None values in HUMAN_DECISION fields)
All test suite checks pass
```

---

## Passing criteria — graded

### Minimum viable

```
1. Creamer A_C stability verified; D_C availability recorded; Ω_C computed if D_C is available
2. Common identified-neuron subgraph built with N_COMMON_NEURONS ≥ 30, or human-approved descope
3. Harmonization table complete with no unresolved ambiguities
4. Behavioral state threshold set and locked
5. n_eff computed; ESTIMATOR_TIER determined
6. Stationarity: NONSTATIONARITY_FRACTION < 0.5, or human-approved descope/alternative
7. Estimation pipeline runs on synthetic data without errors
8. hypothesis_lock.md complete and committed
```

### Adequate

All minimum plus:

```
9. Inter-animal consistency characterized; candidate OUTLIER_ANIMALS identified
10. Nested CV folds defined and saved
11. Enrichment power ≥ 0.6 at OR = 2, or human-approved block/ranking-only descope
12. All pytest tests pass
13. D-robustness criterion defined in hypothesis_lock.md
14. RC role assigned
```

### Good

All adequate plus:

```
15. Both discovery and confirmation estimators validated on synthetic data
16. Randi unc-31-sensitive pair list restricted to subgraph
17. Power curves for both enrichment tests saved
18. Three coordinate systems implemented and tested where available
19. All phase0_config.py values populated with justifications
```

---

## Failure modes to diagnose before changing any parameter

**Common subgraph smaller than expected:**

* Check NeuroPAL identity confidence thresholds in Atanas data
* Check whether harmonization table has unresolved ambiguities reducing the intersection
* Do NOT lower confidence threshold without human approval

**Creamer A_C not stable:**

* Verify continuous vs. discrete-time convention (Stage 1, Task 2)
* If discrete-time and eigenvalues inside unit circle: correct; convert to continuous-time only if required
* If genuinely unstable: compute a nearest stable projection only as sensitivity; report clearly

**D_C not available:**

* Record what noise quantities are available
* Use fallback hierarchy only after human approval:

  1. diagonal residual D from state-specific LDS residuals
  2. identity D in whitened coordinates
  3. report D_C ΔQ bridge as unavailable

**n_eff too low for pairwise estimation:**

* Check that epoch segmentation is not too aggressive
* Check autocorrelation length — if τ_int > 50 frames, the calcium signal is very slow
* Do NOT reduce transition exclusion window to gain timepoints without human approval

**Stationarity drift unexpectedly large:**

* Check for within-epoch behavioral state transitions
* Check for photobleaching or motion artifact trends
* Report structure of the non-stationary covariance drift before changing anything

**Estimation pipeline fails on synthetic data:**

* Verify Q_true_roam is positive definite before sampling
* Verify n_eff inputs to the synthetic data generation match empirical estimates
* Check that graphical lasso is converging (increase max iterations only after checkpoint)

---

## Minimum viable success

Phase 0 succeeds if it produces:

1. A common identified-neuron subgraph of N_COMMON_NEURONS ≥ 30, or a human-approved
   block/subnetwork descope
2. A locked behavioral state threshold justified by behavioral score distribution only
3. An n_eff assessment determining whether pairwise or blockwise estimation is appropriate
4. A functional estimation pipeline verified on synthetic data
5. A completed `hypothesis_lock.md` with human-written primary hypothesis

This is sufficient to proceed to the main ΔQ analysis with scientific integrity.