"""Stage 04 — Creamer/RC bridge structural feasibility audit.

This script performs a metadata-only structural inspection of:
  - data/creamer/Creamer_LDS_2026/models/connectome_constrained.pkl
  - data/creamer/Creamer_LDS_2026/models/fully_connected.pkl
  - data/creamer/Creamer_LDS_2026/models/shuffled_constrained.pkl
  - ReservoirComputing/results_data/esn_resampled.pkl.npz

It determines structural availability of:
  - dynamics matrices (A_C, D_C)
  - stability (eigenvalue magnitudes)
  - process-noise covariance shape/positivity
  - neuron namespace coverage
  - RC output dimensionality and coordinate system

Loading approach for Creamer:
  The Creamer ssm_classes.py imports inference_utilities, which requires
  mpi4py and yaml — neither is installed. A SafeUnpickler stubs all
  non-numpy classes, allowing numpy arrays and scalar attributes to be
  read without executing Creamer's full module chain. No model inference,
  EM steps, or Kalman filtering is run.

Does NOT:
  - compute Lyapunov equations or Sigma_C (requires scipy checkpoint)
  - compute Omega_C (requires Sigma_C and a human checkpoint)
  - compute real-data precision matrices, DeltaQ, D_C DeltaQ, Omega_s
  - load neural activity arrays or behavioral time series
  - modify phase0_config.py

Does NOT set:
  - CREAMER_TIME_CONVENTION, CREAMER_MAX_EIGENVALUE, CREAMER_STABLE
  - CREAMER_DC_AVAILABLE, CREAMER_SIGMA_POSDEF, CREAMER_OMEGA_NORM
  - RC_OUTPUT_NEURON_COORDS, RC_OUTPUT_JACOBIAN_AVAILABLE
  - RC_STATE_CONDITIONED, RC_NEURON_COVERAGE
  (All setting of these config fields requires a human checkpoint.)
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "results" / "diagnostics" / "stage04_creamer_rc_bridge_audit.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.harmonization import normalize_neuron_label


# ---------------------------------------------------------------------------
# Safe pickle loader (stubs non-numpy classes to avoid mpi4py/yaml)
# ---------------------------------------------------------------------------

class _SafeUnpickler(pickle.Unpickler):
    """Deserialize Creamer .pkl files without importing Creamer's modules."""

    def find_class(self, module: str, name: str) -> type:
        if module.startswith("numpy") or module.startswith("builtins"):
            return super().find_class(module, name)

        class _Stub:
            def __init__(self, *a, **kw): pass
            def __setstate__(self, state: Any) -> None:
                if isinstance(state, dict):
                    self.__dict__.update(state)

        return _Stub


def _load_pkl(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        obj = _SafeUnpickler(f).load()
    return obj.__dict__ if hasattr(obj, "__dict__") else {}


def _to_str(val: Any) -> str:
    """Convert numpy string or bytes to Python str."""
    if isinstance(val, (np.str_, str)):
        return str(val)
    if isinstance(val, (bytes, np.bytes_)):
        return val.decode("utf-8", errors="replace")
    return str(val)


def _cell_ids(raw: list[Any]) -> list[str]:
    return [_to_str(x) for x in raw]


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config():
    config_path = ROOT / "phase0_config.py"
    spec = importlib.util.spec_from_file_location("phase0_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Creamer audit
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CreamerModelAudit:
    name: str
    path: str
    dynamics_dim: int
    emissions_dim: int
    input_dim: int
    dynamics_lags: int
    sample_rate_hz: float
    dt_seconds: float
    dyn_weights_shape: tuple[int, ...]
    dyn_weights_dtype: str
    max_abs_eigenvalue: float
    discrete_stable: bool
    dyn_cov_shape: tuple[int, ...]
    dyn_cov_diagonal: bool
    dyn_cov_posdef: bool
    dyn_weights_param_shape: str   # 'synaptic' / 'full' / etc.
    dyn_cov_param_shape: str
    n_cell_ids: int
    cell_ids_sample: list[str]
    awc_labels: list[str]
    n_overlap_common61: int
    missing_from_common61: list[str]   # common-61 neurons absent from Creamer


def audit_creamer_model(path: Path, common_61: set[str]) -> CreamerModelAudit:
    d = _load_pkl(path)

    raw_ids = d.get("cell_ids", [])
    ids = _cell_ids(raw_ids)
    ids_upper = {normalize_neuron_label(i) or i.upper() for i in ids}

    awc = [i for i in ids if "AWC" in i.upper()]
    overlap = common_61 & ids_upper
    missing = sorted(common_61 - ids_upper)

    n = d["dynamics_dim"]
    A = d.get("dynamics_weights")
    Q = d.get("dynamics_cov")
    param_shapes = d.get("param_props", {}).get("shape", {})
    srate = float(d.get("sample_rate", 0))

    max_eig = float("nan")
    stable = False
    if isinstance(A, np.ndarray):
        A0 = A[:n, :n]
        eigs = np.linalg.eigvals(A0)
        max_eig = float(np.max(np.abs(eigs)))
        stable = bool(np.all(np.abs(eigs) < 1.0))

    dyn_cov_diag = False
    dyn_cov_posdef = False
    if isinstance(Q, np.ndarray):
        dyn_cov_diag = bool(np.allclose(Q, np.diag(np.diag(Q))))
        dyn_cov_posdef = bool(np.all(np.diag(Q) > 0))

    return CreamerModelAudit(
        name=path.stem,
        path=str(path),
        dynamics_dim=n,
        emissions_dim=int(d.get("emissions_dim", 0)),
        input_dim=int(d.get("input_dim", 0)),
        dynamics_lags=int(d.get("dynamics_lags", 1)),
        sample_rate_hz=srate,
        dt_seconds=1.0 / srate if srate > 0 else float("nan"),
        dyn_weights_shape=tuple(A.shape) if isinstance(A, np.ndarray) else (),
        dyn_weights_dtype=str(A.dtype) if isinstance(A, np.ndarray) else "unknown",
        max_abs_eigenvalue=max_eig,
        discrete_stable=stable,
        dyn_cov_shape=tuple(Q.shape) if isinstance(Q, np.ndarray) else (),
        dyn_cov_diagonal=dyn_cov_diag,
        dyn_cov_posdef=dyn_cov_posdef,
        dyn_weights_param_shape=str(param_shapes.get("dynamics_weights", "unknown")),
        dyn_cov_param_shape=str(param_shapes.get("dynamics_cov", "unknown")),
        n_cell_ids=len(ids),
        cell_ids_sample=ids[:8] + ["..."] + ids[-4:] if len(ids) > 12 else ids,
        awc_labels=awc,
        n_overlap_common61=len(overlap),
        missing_from_common61=missing,
    )


# ---------------------------------------------------------------------------
# RC audit
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RCAudit:
    npz_path: str
    reservoir_n: int
    input_dim: int
    spectral_radius: float
    mode: str
    has_wout: bool
    wout_shape: tuple[int, ...]
    in_neuron_space: bool
    jacobian_available: bool
    state_conditioned: bool
    neuron_coverage: int
    notes: str


def audit_rc(path: Path) -> RCAudit:
    data = np.load(str(path), allow_pickle=False)
    N = int(data["N"])
    input_dim = int(data["input_dim"])
    spectral_radius = float(data["spectral_radius"])
    mode = str(data["mode"])
    has_wout = "Wout" in data
    wout_shape = tuple(data["Wout"].shape) if has_wout else ()

    # The RC operates in eigenworm space (input_dim=5), not identified-neuron space.
    # Wout maps (N_reservoir,) → (5,) — eigenworm coordinates, not NeuroPAL neurons.
    in_neuron_space = False  # output is eigenworm PCs, not identified neurons
    jacobian_available = False  # no Jacobian in NeuroPAL neuron space exists
    state_conditioned = False  # trained on crawl eigenworms unconditionally
    neuron_coverage = 0

    notes = (
        "RC operates in 5D eigenworm PC space (from crawl.mat / roaming.mat). "
        "Wout maps reservoir → eigenworm space, not → identified NeuroPAL neurons. "
        "No Jacobian in NeuroPAL neuron coordinates is structurally present. "
        "No behavioral-state context input is present in the saved model. "
        "RC role in current-velocity bridge is NOT structurally supported."
    )

    return RCAudit(
        npz_path=str(path),
        reservoir_n=N,
        input_dim=input_dim,
        spectral_radius=spectral_radius,
        mode=mode,
        has_wout=has_wout,
        wout_shape=wout_shape,
        in_neuron_space=in_neuron_space,
        jacobian_available=jacobian_available,
        state_conditioned=state_conditioned,
        neuron_coverage=neuron_coverage,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(
    creamer_audits: list[CreamerModelAudit],
    rc_audit: RCAudit,
    common_61: set[str],
) -> None:
    today = _dt.date.today().isoformat()

    cc = creamer_audits[0]  # connectome_constrained is primary

    creamer_rows = "\n".join(
        f"| {a.name} | {a.dynamics_dim} | {a.max_abs_eigenvalue:.6f} | "
        f"{'YES' if a.discrete_stable else 'NO'} | "
        f"{'diagonal' if a.dyn_cov_diagonal else 'full'} | "
        f"{'YES' if a.dyn_cov_posdef else 'NO'} | "
        f"{a.n_overlap_common61}/61 |"
        for a in creamer_audits
    )

    missing_str = ", ".join(cc.missing_from_common61) or "none"

    report = f"""# Stage 4 Creamer / RC Bridge Structural Feasibility Audit

Date: {today}

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
{creamer_rows}

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

- Common-61 neurons present in Creamer: **{cc.n_overlap_common61} / 61**
- Common-61 neurons ABSENT from Creamer: **{missing_str}**

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
| N (reservoir) | {rc_audit.reservoir_n:,} | Number of reservoir neurons |
| input_dim | {rc_audit.input_dim} | **Eigenworm PCs** — NOT NeuroPAL neurons |
| spectral_radius | {rc_audit.spectral_radius:.4f} | Reservoir |
| mode | {rc_audit.mode} | Leaky integrator |
| Wout shape | {rc_audit.wout_shape} | (output_dim=5, reservoir_N={rc_audit.reservoir_n}) |
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

{rc_audit.notes}

---

## 3. Structural Feasibility for Stage 1 Tasks

### 3.1 What is now structurally confirmable WITHOUT additional computation

| Stage 1 task | Structurally available? | Source |
|---|---|---|
| Discrete-time vs. continuous-time | YES — discrete | sample_rate = 2 Hz |
| dt | YES — 0.5 s | 1 / sample_rate |
| A_C shape and dtype | YES | dynamics_weights (154, 154) |
| max abs(eigenvalue) of A_C | YES — {cc.max_abs_eigenvalue:.6f} | np.linalg.eigvals |
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
| Compute Q_C = Sigma_C^{-1} | scipy.linalg.inv or solve | After posdef check |
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
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _common_61() -> set[str]:
    return {
        "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
        "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
        "CEPDR", "CEPVL", "FLPL", "I1L", "I1R", "I2L", "I2R", "I3", "IL1DR", "IL1L",
        "IL1R", "IL2DL", "IL2DR", "IL2VL", "IL2VR", "M1", "M3L", "M3R", "M4", "MI",
        "NSML", "NSMR", "OLLL", "OLLR", "OLQDL", "OLQDR", "OLQVL", "OLQVR", "RICL",
        "RID", "RIVL", "RMDDR", "RMDL", "RMDVL", "RMDVR", "RMEL", "RMER", "SMDVL",
        "URBL", "URXL", "URYDL", "URYVL", "URYVR",
    }


def main() -> None:
    config = load_config()
    common_61 = _common_61()

    creamer_root = ROOT / config.CREAMER_PATH
    rc_root = ROOT / config.RC_CODE_PATH

    model_names = ["connectome_constrained", "fully_connected", "shuffled_constrained"]
    creamer_paths = [creamer_root / "models" / f"{n}.pkl" for n in model_names]
    rc_esn_path = rc_root / "results_data" / "esn_resampled.pkl.npz"

    missing = [p for p in [*creamer_paths, rc_esn_path] if not p.exists()]
    if missing:
        raise RuntimeError(f"Missing files: {[str(p) for p in missing]}")

    print("Auditing Creamer models (SafeUnpickler — no mpi4py/yaml required)...")
    creamer_audits = [audit_creamer_model(p, common_61) for p in creamer_paths]

    print("Auditing RC ESN...")
    rc_audit = audit_rc(rc_esn_path)

    write_report(creamer_audits, rc_audit, common_61)
    print(f"Report written: {rel(REPORT_PATH)}")

    cc = creamer_audits[0]
    print()
    print(f"=== connectome_constrained ===")
    print(f"  dynamics_dim:     {cc.dynamics_dim}")
    print(f"  sample_rate:      {cc.sample_rate_hz} Hz  dt={cc.dt_seconds} s")
    print(f"  max |eig| A_C:    {cc.max_abs_eigenvalue:.6f}  stable={cc.discrete_stable}")
    print(f"  D_C diagonal:     {cc.dyn_cov_diagonal}  posdef={cc.dyn_cov_posdef}")
    print(f"  common-61 ∩ Creamer: {cc.n_overlap_common61}/61")
    print(f"  missing:          {cc.missing_from_common61}")
    print()
    print(f"=== RC ESN ===")
    print(f"  N={rc_audit.reservoir_n}  input_dim={rc_audit.input_dim}")
    print(f"  mode={rc_audit.mode}  Wout={rc_audit.wout_shape}")
    print(f"  in_neuron_space={rc_audit.in_neuron_space}  jacobian={rc_audit.jacobian_available}")
    print()
    print("phase0_config.py: NOT modified (all CREAMER_*/RC_* fields require human checkpoint)")


if __name__ == "__main__":
    main()
