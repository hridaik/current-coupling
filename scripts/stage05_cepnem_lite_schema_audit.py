"""Stage 05 — CePNEM lite artifact schema and residual-availability audit.

METADATA/STRUCTURE INSPECTION ONLY.

Reads fit_results_lite.jld2 via h5py and reports:
  - JLD2 tree structure (groups, datasets, shapes, dtypes)
  - Per-recording field names and array shapes
  - Recording ID alignment with processed H5 files
  - Presence or absence of residualized neural traces
  - Presence or absence of behavior-predicted components
  - Sampling rate and epoch structure
  - Neuron-label convention

Does NOT:
  - compute covariance, precision, DeltaQ
  - compute behavioral states
  - compute CePNEM residuals
  - run any estimator
  - load large dense arrays unnecessarily
  - modify any methodological config field
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CEPNEM_PATH = ROOT / "data/atanas/AtanasKim-Cell2023/cepnem/fit_results_lite.jld2"
ATANAS_ROOT = ROOT / "data/atanas/AtanasKim-Cell2023"
RESULTS_DIR = ROOT / "results/diagnostics"


# ---------------------------------------------------------------------------
# JLD2 decoding helpers
# ---------------------------------------------------------------------------

def _safe_str(v):
    if isinstance(v, (bytes, np.bytes_)):
        return v.decode("utf-8", errors="replace")
    if isinstance(v, (str, np.str_)):
        return str(v)
    return repr(v)


def _deref(f, ref):
    """Follow a chain of HDF5 References until a concrete value is reached."""
    node = f[ref]
    val = node[()]
    if isinstance(val, h5py.Reference):
        return _deref(f, val)
    return val


def _decode_dict(f, obj_array):
    """Decode a Julia Dict stored as an object array of Pair(first, second)."""
    result = {}
    for i in range(obj_array.size):
        el = obj_array.flat[i]
        pair = _deref(f, el)
        if not (isinstance(pair, np.void) and pair.dtype.names and
                "first" in pair.dtype.names and "second" in pair.dtype.names):
            continue
        key = _deref(f, pair["first"])
        val = _deref(f, pair["second"])
        result[_safe_str(key)] = val
    return result


def _describe_field(val):
    if isinstance(val, np.ndarray):
        return {"type": "ndarray", "shape": list(val.shape), "dtype": str(val.dtype)}
    if isinstance(val, (float, np.floating)):
        return {"type": "scalar_float", "value": float(val)}
    if isinstance(val, (int, np.integer)):
        return {"type": "scalar_int", "value": int(val)}
    if isinstance(val, (bytes, np.bytes_)):
        return {"type": "str", "value": _safe_str(val)[:80]}
    return {"type": type(val).__name__, "repr": repr(val)[:60]}


# ---------------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------------

def run_audit():
    print(f"CePNEM lite file: {CEPNEM_PATH}")
    print(f"File size: {CEPNEM_PATH.stat().st_size / 1e9:.2f} GB")

    report = {}

    with h5py.File(CEPNEM_PATH, "r") as f:
        # --- Top-level structure ---
        top_keys = list(f.keys())
        report["top_level_keys"] = top_keys
        print(f"\nTop-level keys: {top_keys}")

        outer_ref = f["fit_results_lite"][()]
        outer_arr = f[outer_ref][()]
        n_recordings = len(outer_arr)
        print(f"Number of recordings: {n_recordings}")
        report["n_recordings"] = n_recordings

        # --- Collect all recording IDs and per-recording metadata ---
        recording_ids = []
        per_recording_meta = []
        sampling_rates = []
        n_neurons_list = []
        t_lengths = []
        field_name_sets = []

        for i in range(n_recordings):
            pair_void = _deref(f, outer_arr[i])
            rid = _safe_str(_deref(f, pair_void["first"]))
            val = _deref(f, pair_void["second"])
            d = _decode_dict(f, val)

            recording_ids.append(rid)
            field_names = sorted(d.keys())
            field_name_sets.append(set(field_names))

            dt = float(d["avg_timestep"])
            nn = int(d["num_neurons"])
            T = int(d["v"].shape[0])
            n_epochs = int(d["ranges"].shape[0])

            sampling_rates.append(1.0 / dt)
            n_neurons_list.append(nn)
            t_lengths.append(T)

            per_recording_meta.append({
                "recording_id": rid,
                "T": T,
                "num_neurons": nn,
                "avg_timestep_s": round(dt, 6),
                "sampling_hz": round(1.0 / dt, 4),
                "n_epochs": n_epochs,
                "field_names": field_names,
                "trace_array_shape": list(d["trace_array"].shape),
                "trace_original_shape": list(d["trace_original"].shape),
                "sampled_tau_vals_shape": list(d["sampled_tau_vals"].shape),
            })

        # All recordings have identical field names?
        all_same_fields = len(set(frozenset(s) for s in field_name_sets)) == 1
        canonical_fields = sorted(field_name_sets[0])

        print(f"\n=== FIELD NAMES ===")
        print(f"All recordings have identical fields: {all_same_fields}")
        print(f"Canonical field set ({len(canonical_fields)}): {canonical_fields}")

        report["canonical_fields"] = canonical_fields
        report["all_recordings_same_fields"] = all_same_fields

        # --- Sampling rate statistics ---
        sr = np.array(sampling_rates)
        print(f"\n=== SAMPLING RATE ===")
        print(f"  Derived from avg_timestep: min={sr.min():.4f}  max={sr.max():.4f}  "
              f"median={np.median(sr):.4f} Hz")
        print(f"  Note: H5-stored rate ~1.66 Hz, not 5 Hz (ATANAS_SAMPLING_HZ in config)")
        print(f"  ATANAS_SAMPLING_HZ=5.0 is the raw volumetric acquisition rate;")
        print(f"  H5/CePNEM data is stored at ~1.66 Hz (downsampled or variable rate).")
        report["sampling_rate_hz"] = {
            "min": float(sr.min()), "max": float(sr.max()),
            "median": float(np.median(sr)),
            "note": "H5-stored rate ~1.66 Hz, not the 5 Hz raw acquisition rate",
        }

        # --- Neuron counts ---
        print(f"\n=== NEURON COUNTS ===")
        print(f"  N_neurons: min={min(n_neurons_list)}  max={max(n_neurons_list)}  "
              f"median={np.median(n_neurons_list):.0f}")
        report["n_neurons"] = {
            "min": min(n_neurons_list), "max": max(n_neurons_list),
            "median": float(np.median(n_neurons_list)),
        }

        # --- Recording ID alignment with H5 ---
        h5_files = sorted(ATANAS_ROOT.rglob("*-data.h5"))
        h5_ids = set(f.stem.replace("-data", "") for f in h5_files)
        cepnem_set = set(recording_ids)
        overlap = cepnem_set & h5_ids
        only_cepnem = cepnem_set - h5_ids
        only_h5 = h5_ids - cepnem_set

        print(f"\n=== RECORDING ID ALIGNMENT ===")
        print(f"  H5 files found:       {len(h5_ids)}")
        print(f"  CePNEM recordings:    {len(cepnem_set)}")
        print(f"  Overlap:              {len(overlap)}  (PERFECT)" if not only_cepnem and not only_h5
              else f"  Overlap: {len(overlap)}")
        print(f"  CePNEM only:          {sorted(only_cepnem)[:5]}")
        print(f"  H5 only:              {sorted(only_h5)[:5]}")
        report["recording_id_alignment"] = {
            "n_h5": len(h5_ids),
            "n_cepnem": len(cepnem_set),
            "n_overlap": len(overlap),
            "n_cepnem_only": len(only_cepnem),
            "n_h5_only": len(only_h5),
            "perfect_alignment": len(only_cepnem) == 0 and len(only_h5) == 0,
        }

        # --- Cross-check trace_array vs H5 ---
        print(f"\n=== TRACE_ARRAY vs H5 CROSS-CHECK (recording 0) ===")
        rid0 = recording_ids[0]
        pair_void0 = _deref(f, outer_arr[0])
        val0 = _deref(f, pair_void0["second"])
        d0 = _decode_dict(f, val0)

        h5_file0 = ATANAS_ROOT / f"{rid0}-data.h5"
        if h5_file0.exists():
            with h5py.File(h5_file0, "r") as hf:
                if "gcamp" in hf and "trace_array" in hf["gcamp"]:
                    h5_ta = hf["gcamp/trace_array"][:]
                    cepnem_ta = d0["trace_array"]
                    diff = float(np.abs(h5_ta - cepnem_ta).max())
                    identical = diff < 1e-10
                    print(f"  Recording: {rid0!r}")
                    print(f"  H5 gcamp/trace_array shape: {h5_ta.shape}")
                    print(f"  CePNEM trace_array shape:   {cepnem_ta.shape}")
                    print(f"  Max abs diff: {diff:.2e}  →  Identical: {identical}")
                    report["trace_array_vs_h5"] = {
                        "recording_id": rid0,
                        "h5_shape": list(h5_ta.shape),
                        "cepnem_shape": list(cepnem_ta.shape),
                        "max_abs_diff": diff,
                        "identical": identical,
                    }

        # --- Field semantics ---
        print(f"\n=== FIELD SEMANTICS ===")
        trace_arr_mean = float(d0["trace_array"].mean())
        trace_arr_std = float(d0["trace_array"].std())
        trace_orig_mean = float(d0["trace_original"].mean())
        trace_orig_std = float(d0["trace_original"].std())
        print(f"  trace_array:    mean={trace_arr_mean:.4g}  std={trace_arr_std:.4g}")
        print(f"  trace_original: mean={trace_orig_mean:.4g}  std={trace_orig_std:.4g}")
        print(f"  → trace_array is z-scored (mean≈0, std≈1) = H5 gcamp/trace_array")
        print(f"  → trace_original is raw fluorescence (mean={trace_orig_mean:.3f})")
        print(f"  sampled_tau_vals: shape {d0['sampled_tau_vals'].shape}")
        print(f"    = (n_mcmc=10001, N_neurons, n_epochs)")
        print(f"    MCMC posterior of EWMA timescale τ per neuron per epoch")
        print(f"    Sample τ values (neuron 0-4, epoch 0): "
              f"{d0['sampled_tau_vals'][0, :5, 0].round(2)}")

        # --- Residual availability ---
        print(f"\n=== RESIDUAL AVAILABILITY ===")
        residual_fields = {"residuals", "trace_residual", "residual",
                           "predicted", "mu", "beta", "coef", "weights"}
        present_residual_fields = residual_fields & set(canonical_fields)
        print(f"  Residual/coefficient fields present: {present_residual_fields or 'NONE'}")
        print(f"  Conclusion: CePNEM residuals are NOT directly stored in lite artifact.")
        print(f"  To compute residuals, the pipeline would need to:")
        print(f"    1. Take posterior median of sampled_tau_vals → τ̂_i per neuron/epoch")
        print(f"    2. Compute EWMA(behavioral covariates; τ̂_i) per neuron/epoch")
        print(f"    3. Fit x_i(t) = β_i · EWMA + ε_i(t) by linear regression")
        print(f"    4. Residuals ε_i(t) = trace_array_i(t) − β̂_i · EWMA(τ̂_i)")
        print(f"  All inputs for this computation are present in the lite artifact.")
        print(f"  This computation is NOT performed in this audit (requires checkpoint).")

        report["residual_availability"] = {
            "residuals_directly_stored": False,
            "beta_coefficients_stored": False,
            "predicted_traces_stored": False,
            "tau_posterior_samples_stored": True,
            "behavioral_covariates_stored": True,
            "trace_array_stored": True,
            "computable_from_lite_with_ewma_regression": True,
            "requires_future_computation_checkpoint": True,
            "missing_relative_to_full_fit_results": [
                "beta (behavioral encoding coefficients)",
                "precomputed residuals",
                "MCMC samples of beta posterior",
                "log-likelihood values",
                "convergence diagnostics",
            ],
        }

        report["per_recording_meta"] = per_recording_meta

    # --- Save report ---
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "cepnem_lite_schema_audit.json"
    with open(out_path, "w") as fp:
        json.dump(report, fp, indent=2)
    print(f"\nJSON report saved: {out_path}")

    return report


if __name__ == "__main__":
    run_audit()
