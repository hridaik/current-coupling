"""Stage 1.0 — CePNEM residualization and verification.

Gate B: single-recording pilot on recording '2022-06-14-07'.
Gate C (not yet authorized): full 68-recording run.

Ambiguity resolutions recorded before first archive access:
  A1 (HDF5 subsetting): full stp load + numpy slice is faster than fancy indexing
     (0.27 s for 61 neurons from 151-neuron recording, vs comparable h5py overhead)
  A2 (label mapping): decoded_labels position i is NOT column i of trace_array.
     Mapping requires match_org_to_skip from each H5 file:
       trace_array column j <- decoded_labels[ match_org_to_skip[0][j] - 1 ]
     Only the 40 NeuroPAL recordings (those present in dict_neuropal_label.jld2)
     are processed. The remaining 28 recordings in fit_results.jld2 have no
     neuron identity and are excluded from the subgraph analysis.
  A3 (covariate standardization): fit_results.jld2 v,th,P are raw (unstandardized).
     Confirmed: max diff vs H5 behavior/velocity = 0.00e+00 for recording 0.
  A4 (gap frames): gap frames receive NaN in all output arrays; epoch_mask
     propagates to all downstream analyses.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stage02_subgraph import decode_atanas_jld2
from src.cepnem_residualize import (
    check_decorrelation,
    check_stationarity,
    residualize_recording,
)
from src.harmonization import normalize_neuron_label

# ---------------------------------------------------------------------------
# Locked paths
# ---------------------------------------------------------------------------
CEPNEM_PATH  = ROOT / "data/atanas/AtanasKim-Cell2023/cepnem/fit_results.jld2"
LABEL_PATH   = ROOT / "data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2"
H5_DIR       = ROOT / "data/atanas/AtanasKim-Cell2023"
OUT_DIR      = ROOT / "results/phase1/data/cepnem_residuals"
VER_DIR      = OUT_DIR / "verification"
FIG_DIR      = ROOT / "results/phase1/figures/stage0"

# 61-neuron common subgraph (from results/diagnostics/stage02_subgraph_feasibility.md)
COMMON_61: frozenset[str] = frozenset({
    "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
    "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
    "CEPDR", "CEPVL", "FLPL", "I1L",  "I1R",  "I2L",  "I2R",  "I3",  "IL1DR",
    "IL1L", "IL1R",  "IL2DL","IL2DR","IL2VL","IL2VR","M1",   "M3L",  "M3R",
    "M4",   "MI",    "NSML", "NSMR", "OLLL", "OLLR", "OLQDL","OLQDR","OLQVL",
    "OLQVR","RICL",  "RID",  "RIVL", "RMDDR","RMDL", "RMDVL","RMDVR","RMEL",
    "RMER", "SMDVL", "URBL", "URXL", "URYDL","URYVL","URYVR",
})

IDENTITY_CONFIDENCE_THRESHOLD = 2.5  # locked in phase0_config.py
LR_POLICY = "separate"               # locked in phase0_config.py

# ---------------------------------------------------------------------------
# JLD2 access helpers (same logic as stage05_cepnem_full_schema_audit.py)
# ---------------------------------------------------------------------------

def _deref(f: h5py.File, ref) -> object:
    node = f[ref]
    val = node[()]
    if isinstance(val, h5py.Reference):
        return _deref(f, val)
    return val


def _safe_str(v: object) -> str:
    if isinstance(v, (bytes, np.bytes_)):
        return v.decode("utf-8", errors="replace")
    if isinstance(v, (str, np.str_)):
        return str(v)
    return repr(v)


def _decode_dict(f: h5py.File, obj_array: np.ndarray) -> dict:
    result = {}
    for i in range(obj_array.size):
        pair = _deref(f, obj_array.flat[i])
        if not (isinstance(pair, np.void)
                and pair.dtype.names
                and "first" in pair.dtype.names):
            continue
        key = _deref(f, pair["first"])
        val = _deref(f, pair["second"])
        result[_safe_str(key)] = val
    return result


# ---------------------------------------------------------------------------
# Neuron label mapping
# ---------------------------------------------------------------------------

def build_label_maps(
    label_records,
    h5_dir: Path,
) -> dict[str, dict[str, int]]:
    """Build {rec_id: {normalized_label: col_idx}} for all NeuroPAL recordings.

    Uses match_org_to_skip[0] from each H5 file to map trace_array column
    indices to label dict positions (ambiguity A2 resolution).
    """
    label_map: dict[str, dict[str, int]] = {}

    for rec in label_records:
        rec_id = rec.record_id
        h5_path = h5_dir / f"{rec_id}-data.h5"
        if not h5_path.exists():
            continue

        with h5py.File(h5_path, "r") as hf:
            mos = hf["gcamp/match_org_to_skip"][()][0]  # (N_total,) Julia 1-based

        decoded = rec.decoded_labels
        n_labeled = len(decoded)
        col_to_label: dict[str, int] = {}

        for col_idx, orig_idx_1based in enumerate(mos):
            orig_idx = int(orig_idx_1based) - 1  # 0-based
            if orig_idx >= n_labeled:
                continue
            item = decoded[orig_idx]
            raw_label = item.get("label")
            confidence = item.get("confidence")
            if not isinstance(raw_label, str):
                continue
            if not isinstance(confidence, (int, float)):
                continue
            if confidence < IDENTITY_CONFIDENCE_THRESHOLD:
                continue
            if "alt" in raw_label.lower():
                continue
            norm = normalize_neuron_label(raw_label, lr_policy=LR_POLICY)
            if norm is None:
                continue
            if norm in COMMON_61:
                col_to_label[norm] = col_idx

        label_map[rec_id] = col_to_label

    return label_map


# ---------------------------------------------------------------------------
# Per-recording processing
# ---------------------------------------------------------------------------

def load_cepnem_record(f: h5py.File, outer_arr: np.ndarray, idx: int) -> tuple[str, dict]:
    pair = _deref(f, outer_arr[idx])
    rec_id = _safe_str(_deref(f, pair["first"]))
    d = _decode_dict(f, _deref(f, pair["second"]))
    return rec_id, d


def process_one_recording(
    rec_id: str,
    d: dict,
    subgraph_label_col: dict[str, int],
) -> dict | None:
    """Run residualization and all verification checks for one recording.

    Returns a results dict, or None if fewer than 2 subgraph neurons are found.
    """
    trace_array = d["trace_array"]              # (T, N_total)
    v   = d["v"]
    th  = d["θh"]
    P   = d["P"]
    ang_vel = d["ang_vel"]
    curve   = d["curve"]
    ranges  = d["ranges"]
    stp     = d["sampled_trace_params"]         # (11, 10001, N_total, n_epochs)

    # Build ordered subgraph index: sorted by label for reproducibility
    sorted_labels = sorted(subgraph_label_col.keys())
    subgraph_cols = np.array([subgraph_label_col[lbl] for lbl in sorted_labels], dtype=int)

    if len(subgraph_cols) < 2:
        return None

    # Core residualization
    res = residualize_recording(trace_array, v, th, P, ranges, stp, subgraph_cols)

    trace_sub = trace_array[:, subgraph_cols]   # (T, n_sub)

    # Check A — behavioral decorrelation
    covariates = {"v": v, "ang_vel": ang_vel, "θh": th, "P": P, "curve": curve}
    decor = check_decorrelation(
        res["residual_normed"], trace_sub, covariates, res["epoch_mask"]
    )

    # Check D — stationarity
    stat = check_stationarity(res["residual_normed"], trace_sub, res["epoch_mask"])

    return {
        "rec_id":         rec_id,
        "subgraph_labels": sorted_labels,
        "subgraph_cols":   subgraph_cols.tolist(),
        "n_sub":           len(sorted_labels),
        "T":               trace_array.shape[0],
        "n_epochs":        ranges.shape[0],
        "residual_raw":    res["residual_raw"],
        "residual_normed": res["residual_normed"],
        "predicted":       res["predicted"],
        "epoch_mask":      res["epoch_mask"],
        "params_med":      res["params_med"],
        "var_ratios":      res["var_ratios"],
        "identity_errors": res["identity_errors"],
        "decorrelation":   decor,
        "stationarity":    stat,
    }


# ---------------------------------------------------------------------------
# Epoch boundary plot (Check C)
# ---------------------------------------------------------------------------

def plot_epoch_boundaries(result: dict, out_path: Path, n_neurons: int = 5) -> None:
    res_normed = result["residual_normed"]
    ranges_stored = None   # passed from caller; use epoch_mask zero-crossings
    epoch_mask = result["epoch_mask"]
    rec_id = result["rec_id"]
    T = res_normed.shape[0]
    n_sub = res_normed.shape[1]

    # Find epoch boundary frames: transitions in epoch_mask
    boundaries = []
    in_ep = False
    for t in range(T):
        if epoch_mask[t] and not in_ep:
            if t > 0:
                boundaries.append(t)   # start of a new epoch (after a gap or start)
            in_ep = True
        elif not epoch_mask[t]:
            in_ep = False

    # Remove boundary at t=0
    boundaries = [b for b in boundaries if b > 20]

    if not boundaries:
        return

    rng = np.random.default_rng(seed=42)
    neuron_idx = rng.choice(n_sub, size=min(n_neurons, n_sub), replace=False)
    window = 20

    n_cols = len(boundaries)
    fig, axes = plt.subplots(min(n_neurons, n_sub), n_cols,
                              figsize=(5 * n_cols, 2 * min(n_neurons, n_sub)),
                              squeeze=False)

    for col, b in enumerate(boundaries):
        t_lo = max(0, b - window)
        t_hi = min(T, b + window)
        for row, ni in enumerate(neuron_idx):
            ax = axes[row, col]
            ts = np.arange(t_lo, t_hi) - b
            trace = res_normed[t_lo:t_hi, ni]
            ax.plot(ts, trace, lw=0.8)
            ax.axvline(0, color="red", lw=0.8, ls="--")
            ax.set_title(f"boundary t={b}", fontsize=7)
            if col == 0:
                ax.set_ylabel(f"neuron {ni}", fontsize=7)
            ax.tick_params(labelsize=6)

    fig.suptitle(f"{rec_id} — epoch boundary residual_normed (±{window} frames)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Save per-recording outputs
# ---------------------------------------------------------------------------

def save_recording_npz(result: dict) -> None:
    rec_id = result["rec_id"]
    np.savez_compressed(
        OUT_DIR / f"{rec_id}.npz",
        residual=result["residual_normed"],
        residual_raw=result["residual_raw"],
        neuron_labels=np.array(result["subgraph_labels"]),
        epoch_mask=result["epoch_mask"],
        params_med=result["params_med"],
    )


def save_aggregate_outputs(all_results: list[dict]) -> None:
    """Write aggregate verification files across all processed recordings."""
    import csv

    # Variance ratios — one row per (recording, neuron)
    vr_path = VER_DIR / "variance_ratios.csv"
    with open(vr_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["recording_id", "neuron_label", "var_ratio"])
        writer.writeheader()
        for res in all_results:
            for lbl, vr in zip(res["subgraph_labels"], res["var_ratios"]):
                writer.writerow({"recording_id": res["rec_id"],
                                 "neuron_label": lbl,
                                 "var_ratio": float(vr)})

    # Decorrelation summary — per recording per covariate
    decor_summary = []
    for res in all_results:
        entry = {"rec_id": res["rec_id"], "n_sub": res["n_sub"]}
        for cov, stats_d in res["decorrelation"].items():
            entry[f"{cov}_r_raw"]   = stats_d["median_abs_r_raw"]
            entry[f"{cov}_r_resid"] = stats_d["median_abs_r_resid"]
            entry[f"{cov}_reduction"] = stats_d["median_reduction"]
        decor_summary.append(entry)
    with open(VER_DIR / "decorrelation_stats.json", "w") as fh:
        json.dump(decor_summary, fh, indent=2)

    # Stationarity comparison
    stat_summary = [
        {"rec_id": res["rec_id"], **res["stationarity"]}
        for res in all_results
    ]
    with open(VER_DIR / "stationarity_comparison.json", "w") as fh:
        json.dump(stat_summary, fh, indent=2)


# ---------------------------------------------------------------------------
# (legacy name kept for pilot compatibility)
# ---------------------------------------------------------------------------

def save_pilot_results(result: dict) -> None:
    rec_id = result["rec_id"]

    save_recording_npz(result)

    # Variance ratios CSV (pilot-specific filename)
    import csv
    vr_path = VER_DIR / "variance_ratios_pilot.csv"
    with open(vr_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["recording_id", "neuron_label", "var_ratio"])
        writer.writeheader()
        for lbl, vr in zip(result["subgraph_labels"], result["var_ratios"]):
            writer.writerow({"recording_id": rec_id, "neuron_label": lbl, "var_ratio": float(vr)})

    # Decorrelation + stationarity JSON
    summary = {
        "rec_id":        rec_id,
        "n_sub":         result["n_sub"],
        "T":             result["T"],
        "n_epochs":      result["n_epochs"],
        "var_ratios": {
            "min":    float(np.nanmin(result["var_ratios"])),
            "max":    float(np.nanmax(result["var_ratios"])),
            "median": float(np.nanmedian(result["var_ratios"])),
            "n_below_0p10": int(np.sum(result["var_ratios"] < 0.10)),
            "n_above_1p0":  int(np.sum(result["var_ratios"] > 1.0)),
        },
        "identity_check": {
            "max_error":    float(np.max(result["identity_errors"])),
            "all_pass_1e10": bool(np.max(result["identity_errors"]) < 1e-10),
        },
        "decorrelation": {
            cov: {
                "median_abs_r_raw":   v["median_abs_r_raw"],
                "median_abs_r_resid": v["median_abs_r_resid"],
                "median_reduction":   v["median_reduction"],
            }
            for cov, v in result["decorrelation"].items()
        },
        "stationarity": result["stationarity"],
    }

    with open(VER_DIR / "pilot_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(pilot_only: bool = True) -> None:
    import phase0_config as cfg
    assert cfg.PHASE0_COMPLETE, "PHASE0_COMPLETE must be True before running Stage 1.0"

    print("Loading NeuroPAL label dict...")
    label_records = decode_atanas_jld2(LABEL_PATH)
    neuropal_ids = {rec.record_id for rec in label_records}
    print(f"  NeuroPAL recordings: {len(neuropal_ids)}")

    print("Building label->column maps (requires H5 match_org_to_skip)...")
    label_maps = build_label_maps(label_records, H5_DIR)
    print(f"  Mapped recordings: {len(label_maps)}")

    # Load fit_results.jld2 outer structure
    print("Opening fit_results.jld2...")
    with h5py.File(CEPNEM_PATH, "r") as f:
        outer_ref = f["fit_results"][()]
        outer_arr = f[outer_ref][()]
        n_recs = len(outer_arr)
        print(f"  Total CePNEM recordings: {n_recs}")

        # Identify NeuroPAL recordings in the archive
        neuropal_indices = []
        for idx in range(n_recs):
            pair = _deref(f, outer_arr[idx])
            rid = _safe_str(_deref(f, pair["first"]))
            if rid in neuropal_ids and rid in label_maps:
                neuropal_indices.append((idx, rid))

        print(f"  NeuroPAL recordings in CePNEM archive: {len(neuropal_indices)}")

        # Select pilot recording
        if pilot_only:
            # First NeuroPAL recording by archive index
            pilot_idx, pilot_rid = neuropal_indices[0]
            process_list = [(pilot_idx, pilot_rid)]
            print(f"\nPILOT MODE: processing recording [{pilot_idx}] {pilot_rid}")
        else:
            process_list = neuropal_indices

        t_total_start = time.perf_counter()
        all_results: list[dict] = []
        # Recordings with ≥1 epoch boundary for Check C plots
        two_epoch_plotted = 0
        three_epoch_plotted = 0

        for rec_idx, rec_id in process_list:
            print(f"\n--- Recording {rec_id} (archive index {rec_idx}) ---")
            t0 = time.perf_counter()

            _, d = load_cepnem_record(f, outer_arr, rec_idx)
            t_load = time.perf_counter() - t0
            print(f"  Loaded: T={d['trace_array'].shape[0]}, N={d['num_neurons']}, "
                  f"n_epochs={d['ranges'].shape[0]}, load_time={t_load:.2f}s")

            subgraph_col_map = label_maps[rec_id]
            print(f"  Subgraph neurons found: {len(subgraph_col_map)}/{len(COMMON_61)}")

            result = process_one_recording(rec_id, d, subgraph_col_map)
            t_rec_total = time.perf_counter() - t0

            if result is None:
                print(f"  SKIPPED: fewer than 2 subgraph neurons")
                continue

            result["wall_time_s"] = t_rec_total

            # ---- Implementation verification ----
            max_err = np.max(result["identity_errors"])
            id_pass = max_err < 1e-10
            print(f"  Identity check: {'PASS' if id_pass else 'FAIL'} (max={max_err:.2e})")
            if not id_pass:
                print(f"  *** IDENTITY CHECK FAILED — recording {rec_id} ***")

            # ---- Check B ----
            vr = result["var_ratios"]
            n_low  = int(np.sum(vr < 0.10))
            n_high = int(np.sum(vr > 1.0))
            print(f"  VarRatio: min={np.nanmin(vr):.3f} med={np.nanmedian(vr):.3f} "
                  f"max={np.nanmax(vr):.3f} | <0.10:{n_low} >1.0:{n_high}")

            # ---- Check A ----
            for cov in ["v", "θh", "P"]:
                sd = result["decorrelation"][cov]
                print(f"  Decor {cov}: raw={sd['median_abs_r_raw']:.3f} "
                      f"-> resid={sd['median_abs_r_resid']:.3f} "
                      f"(red={sd['median_reduction']:.3f})")

            # ---- Check D ----
            stat = result["stationarity"]
            dr = stat.get("drift_raw")
            ds = stat.get("drift_resid")
            ratio = stat.get("ratio_resid_over_raw")
            dr_s    = f"{dr:.3f}"    if dr    is not None else "None"
            ds_s    = f"{ds:.3f}"    if ds    is not None else "None"
            ratio_s = f"{ratio:.3f}" if ratio is not None else "None"
            print(f"  Stationarity: raw={dr_s} resid={ds_s} ratio={ratio_s}")

            # ---- Check C: boundary plots for representative subset ----
            n_ep = result["n_epochs"]
            do_plot = False
            if n_ep == 2 and two_epoch_plotted < 1:
                do_plot = True; two_epoch_plotted += 1
            elif n_ep == 3 and three_epoch_plotted < 2:
                do_plot = True; three_epoch_plotted += 1
            if do_plot:
                fig_path = FIG_DIR / f"{rec_id}_epoch_boundaries.pdf"
                plot_epoch_boundaries(result, fig_path)
                print(f"  Boundary plot saved: {fig_path.name}")

            # ---- Save per-recording .npz ----
            save_recording_npz(result)
            all_results.append(result)
            print(f"  Wall time: {t_rec_total:.2f}s")

        t_total = time.perf_counter() - t_total_start

    # ---- Save aggregate outputs ----
    if all_results:
        save_aggregate_outputs(all_results)

    if pilot_only:
        last = all_results[-1] if all_results else None
        t_rec = last["wall_time_s"] if last else None
        print(f"\n{'='*60}")
        print(f"GATE B PILOT COMPLETE")
        print(f"  Pilot recording wall time: {t_rec:.2f}s")
        print(f"  Estimated full 40-recording run: {t_rec*40/60:.1f} min")
        print(f"  Estimated full 40-recording run (seconds): {t_rec*40:.0f}s")
        print(f"STOP — awaiting Gate C authorization before full run.")
    else:
        print(f"\n{'='*60}")
        print(f"GATE C COMPLETE — {len(all_results)} recordings processed in {t_total:.1f}s")
        print(f"STOP — awaiting Stage 1.0 completion checkpoint before Stage 1.1.")


if __name__ == "__main__":
    main(pilot_only=True)
