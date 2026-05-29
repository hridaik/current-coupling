# Stage 4 Creamer / RC Bridge Structural Feasibility Audit

Date: 2026-05-28

## Scope

Metadata-only structural inspection of Creamer LDS model artifacts and RC ESN.

Loaded (metadata only, via SafeUnpickler or np.load):
  - Creamer models: connectome_constrained.pkl, fully_connected.pkl,
    shuffled_constrained.pkl
  - RC ESN: ReservoirComputing/results_data/esn_resampled.pkl.npz

NOT loaded / NOT computed:
  - Neural activity arrays or behavioral time series
  - Lyapunov equations or Sigma_C (requires scipy checkpoint)
  - Omega_C = A_C + D_C Q_C (requires Sigma_C)
  - Real-data precision matrices, DeltaQ, D_C DeltaQ, Omega_s, enrichment

phase0_config.py was NOT modified. All CREAMER_* and RC_* fields remain
at their current values pending human checkpoints.

---

## 1. Creamer LDS Model Artifacts

### 1.1 File inventory

| File | Role |
|---|---|
| `models/connectome_constrained.pkl` | Primary: dynamics constrained to synaptic connectome |
| `models/fully_connected.pkl` | Ablation: unconstrained (fully connected A_C) |
| `models/shuffled_constrained.pkl` | Ablation: shuffled connectome constraint |
| `anatomical_data/cell_ids.pkl` | Neuron ID list |
| `anatomical_data/chemical.pkl` | Chemical synapse adjacency |
| `anatomical_data/gap.pkl` | Gap junction adjacency |
| `anatomical_data/peptide.pkl` | Neuropeptide adjacency |
| `data/example_recording.pkl` | Example data (not loaded) |
| `data/measured_corr.pkl` | Measured correlations (not loaded) |
| `trained_models/` | Empty (no additional saved checkpoints) |

### 1.2 Model dimensions (all three models identical)

| Field | Value | Interpretation |
|---|---|---|
| `dynamics_dim` | 154 | Number of neurons in the LDS |
| `emissions_dim` | 154 | Same as dynamics_dim (identity-like emissions) |
| `input_dim` | 154 | Optogenetic stimulation inputs (one per neuron) |
| `dynamics_lags` | 1 | Single time lag (first-order Markov) |
| `dynamics_input_lags` | 45 | 45-frame input history (~22.5 s at 2 Hz) |
| `sample_rate` | 2 Hz | dt = 0.5 s |
| `A_C shape` | (154, 154) | Lag-0 block = full A_C matrix |

### 1.3 Stability and D_C summary

| Model | n neurons | max abs(eig) | Discrete-time stable | D_C (dynamics_cov) diagonal | D_C posdef | common-61 overlap |
|---|---|---|---|---|---|---|
| connectome_constrained | 154 | 0.996609 | YES | diagonal | YES | 56/61 |
| fully_connected | 154 | 0.997181 | YES | diagonal | YES | 56/61 |
| shuffled_constrained | 154 | 0.997942 | YES | diagonal | YES | 56/61 |

**All three models are discrete-time stable** (all eigenvalues inside the unit circle).

**`dynamics_cov` is the D_C** (process-noise covariance):
- Shape: (154, 154)
- Structure: diagonal (confirmed by inspection of all three models)
- Positive definite: YES (all diagonal entries > 0)
- `param_props['shape']['dynamics_cov'] = 'diag'` confirms diagonal structure by design
- This matches `CREAMER_D_TYPE = "discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D"` (approved 2026-05-28)

**Loading requirement:** The Creamer .pkl files can be loaded for metadata
inspection and Stage 1 computations WITHOUT the Creamer Python module chain
(which requires `mpi4py` and `yaml`), using a custom SafeUnpickler that
passes numpy arrays through directly.

### 1.4 Neuron label convention

- Creamer cell_ids use NeuroPAL-style names: ADAL, ADAR, ADEL, ..., URYVR
- Plus VB-class neurons: VA1, VB1, VB2 (ventral cord)
- **No AWC labels of any type** (AWCL, AWCR, AWCON, AWCOFF are all absent)

### 1.5 Namespace overlap with common-61

- Common-61 neurons present in Creamer: **56 / 61**
- Common-61 neurons ABSENT from Creamer: **AIBL, AIBR, AWCL, IL1L, IL1R**

This is a newly identified namespace gap. Five neurons from the primary analysis
subgraph (N_COMMON_NEURONS = 61) have no Creamer representation. Consequences:
- For the anatomy-guided lasso using A_raw from Creamer, the subgraph must be
  restricted to the 56-neuron Creamer intersection.
- `D_C ΔQ` computation will cover 56 of 61 neurons; the 5 missing neurons
  will have no Creamer-based current-velocity attribution.
- This gap requires a human decision on whether to (a) use a fallback D for the
  5 missing neurons, (b) restrict the D_C ΔQ analysis to 56 neurons, or
  (c) treat D_C ΔQ as incomplete and rely on ΔQ alone for those 5 neurons.
- This decision is NOT made here; it must be recorded as a new gap at the Stage 1
  human checkpoint.

---

## 2. RC (Reservoir Computing) ESN

### 2.1 File inventory

| File | Role |
|---|---|
| `results_data/esn_resampled.pkl.npz` | Trained ESN (saved via ESN.save()) |
| `data_eigenworm/crawl.mat` | C. elegans crawl eigenworm data (training data) |
| `data_eigenworm/roaming.mat` | C. elegans roaming eigenworm data |
| `rc/esn.py` | ESN class with train/predict/Lyapunov |
| `rc/dynamics.py` | Reservoir update dynamics |

### 2.2 ESN structure

| Field | Value | Interpretation |
|---|---|---|
| N (reservoir) | 10,000 | Number of reservoir neurons |
| input_dim | 5 | **Eigenworm PCs** — NOT NeuroPAL neurons |
| spectral_radius | 0.1810 | Reservoir |
| mode | leaky | Leaky integrator |
| Wout shape | (5, 10000) | (output_dim=5, reservoir_N=10000) |
| Wout_bias | present | — |

### 2.3 RC coordinate system and Phase 0 role assessment

The RC operates in **5-dimensional eigenworm space** (the first 5 principal
components of worm body posture from crawl recordings). Training script
`figure/worm/train_esns.py` confirms `INPUT_DIM = 5` and loads eigenworm
PCs from `data_eigenworm/crawl.mat`. There is no mapping from reservoir
states or Wout to identified NeuroPAL neuron coordinates.

| RC capability | Status | Reason |
|---|---|---|
| Outputs in identified-neuron coordinates | **NO** | Output is 5D eigenworm space |
| Jacobian in NeuroPAL neuron space | **NO** | Wout maps to eigenworm, not neurons |
| State-conditioned generation (roam/dwell) | **NOT PRESENT** | Saved model has no context input |
| NeuroPAL neuron coverage | **0** | No neuron-space output |
| RC_ROLE_JACOBIAN viable | **NO** | Structurally incompatible |
| RC_ROLE_SAMPLING viable | **Conditional** | Can generate eigenworm trajectories, not neural |

The RC appears to have been designed to reconstruct Lyapunov/ergodic properties
from behavioral eigenworm data, which is a valid use case but is orthogonal to
the current-velocity bridge in NeuroPAL neuron coordinates.

RC operates in 5D eigenworm PC space (from crawl.mat / roaming.mat). Wout maps reservoir → eigenworm space, not → identified NeuroPAL neurons. No Jacobian in NeuroPAL neuron coordinates is structurally present. No behavioral-state context input is present in the saved model. RC role in current-velocity bridge is NOT structurally supported.

---

## 3. Structural Feasibility for Stage 1 Tasks

### 3.1 What is now structurally confirmable WITHOUT additional computation

| Stage 1 task | Structurally available? | Source |
|---|---|---|
| Discrete-time vs. continuous-time | YES — discrete | sample_rate = 2 Hz |
| dt | YES — 0.5 s | 1 / sample_rate |
| A_C shape and dtype | YES | dynamics_weights (154, 154) |
| max abs(eigenvalue) of A_C | YES — 0.996609 | np.linalg.eigvals |
| Discrete-time stability (all eig < 1) | YES — True | from eigenvalues |
| D_C available? | YES | dynamics_cov (154, 154) diagonal, posdef |
| D_C structure (diagonal) | YES | confirmed |
| Neuron label convention | YES — NeuroPAL-style | cell_ids |
| AWC label convention | YES — absent | No AWC in Creamer |

### 3.2 What requires scipy (not yet installed) and a human checkpoint

| Stage 1 task | Requires | Checkpoint needed? |
|---|---|---|
| Solve discrete Lyapunov: Sigma_C = A_C Sigma_C A_C^T + D_C | `scipy.linalg.solve_discrete_lyapunov` | YES |
| Check Sigma_C positive definite | scipy or numpy eigenvalues on result | After Lyapunov |
| Compute Q_C = Sigma_C^-1 | scipy.linalg.inv or solve | After posdef check |
| Compute Omega_C = A_C + D_C Q_C | numpy once Q_C is available | After Q_C |
| Record CREAMER_OMEGA_NORM | numpy.linalg.norm | After Omega_C |

### 3.3 What requires additional human decisions

| Config field | Gap identified | Decision needed |
|---|---|---|
| D_C ΔQ subgraph (56 vs 61 neurons) | 5 common-61 neurons absent from Creamer | How to handle missing D_C for AIBL, AIBR, AWCL, IL1L, IL1R |
| RC role assignment (Stage 4) | RC operates in eigenworm, not neuron space | All RC_ROLE_* fields need human decision |
| RC_ROLE_JACOBIAN | Structurally NOT viable | Must set to False; human confirmation |
| RC_ROLE_SAMPLING | Eigenworm only, not neural | Human decision on scope |

---

## 4. Dependencies Required for Stage 1 Execution

| Package | Purpose | Status |
|---|---|---|
| `scipy` | Lyapunov solver, matrix inverse | NOT installed |
| `yaml` | Creamer loading_utilities | NOT needed if using SafeUnpickler |
| `mpi4py` | Creamer inference_utilities | NOT needed for Stage 1 tasks |

The Stage 1 computations (eigenvalues, Lyapunov solve, Omega_C) can be
implemented using ONLY numpy (already installed) and scipy (not yet installed),
without importing any Creamer Python modules. A checkpoint is required before
installing scipy.

---

## 5. Deviations

No new deviations. Findings above are diagnostic only; no config changes made.
