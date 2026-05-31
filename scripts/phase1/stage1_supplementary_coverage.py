"""Supplementary neuron-coverage computation — Interpretation C.

Authorized by human checkpoint (2026-05-31): Stage 1.1 Gate A revealed
4/13 effective neurons under strict cross-recording complete-case. Human
approved Interpretation C: include neurons present in >= COVERAGE_FRACTION
of the recordings that contribute to each specific state x coordinate
combination. MISSING_NEURON_POLICY = nan_complete_case is retained; this
threshold governs which neurons enter the analysis, not whether frames
are imputed.

Outputs (written to results/phase1/data/):
    supplementary_coverage.json  — full per-state x coordinate report
    supplementary_coverage_neuron_table.json — per-neuron presence detail

No precision matrices, stability matrices, Delta-Q, or enrichment are
computed here. This script stops after the coverage report.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import phase0_config as cfg
from scripts.stage02_subgraph import decode_atanas_jld2
from scripts.stage06_neff_stationarity import (
    SAMPLING_HZ, NEFF_K_MAX_FRAMES,
    ewma, segment, get_epoch_slices,
    tau_int_batch,
)
from scripts.phase1.stage0_cepnem import build_label_maps

assert cfg.PHASE0_COMPLETE, "PHASE0_COMPLETE must be True"
assert cfg.COORD_PRIMARY == "cepnem_residual"
assert cfg.MISSING_NEURON_POLICY == "nan_complete_case"

H5_DIR    = ROOT / "data/atanas/AtanasKim-Cell2023"
LABEL_PATH = H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2"
RESID_DIR  = ROOT / "results/phase1/data/cepnem_residuals"
OUT_DIR    = ROOT / "results/phase1/data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Locked parameters
COVERAGE_FRACTION = cfg.COVERAGE_FRACTION        # 0.80
TAU   = cfg.EWMA_TIMESCALE_SECONDS               # 20.0
THR   = cfg.BEHAV_THRESHOLD                      # 0.284
W_FR  = int(cfg.W_TRANS_SECONDS  * SAMPLING_HZ)  # 50 frames
MB_FR = int(cfg.MIN_BOUT_SECONDS * SAMPLING_HZ)  # 50 frames

COMMON_61: list[str] = sorted({
    "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
    "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
    "CEPDR", "CEPVL", "FLPL", "I1L",  "I1R",  "I2L",  "I2R",  "I3",  "IL1DR",
    "IL1L", "IL1R",  "IL2DL","IL2DR","IL2VL","IL2VR","M1",   "M3L",  "M3R",
    "M4",   "MI",    "NSML", "NSMR", "OLLL", "OLLR", "OLQDL","OLQDR","OLQVL",
    "OLQVR","RICL",  "RID",  "RIVL", "RMDDR","RMDL", "RMDVL","RMDVR","RMEL",
    "RMER", "SMDVL", "URBL", "URXL", "URYDL","URYVL","URYVR",
})
N_FULL = len(COMMON_61)                          # 61
LABEL_IDX = {lbl: i for i, lbl in enumerate(COMMON_61)}


# ---------------------------------------------------------------------------
# Segmentation + epoch construction (identical to Gate A)
# ---------------------------------------------------------------------------

def build_epoch_dicts(
    label_maps: dict[str, dict[str, int]],
) -> tuple[
    dict[str, list[np.ndarray]],  # cep_roam
    dict[str, list[np.ndarray]],  # cep_dwell
    dict[str, list[np.ndarray]],  # gcamp_roam
    dict[str, list[np.ndarray]],  # gcamp_dwell
]:
    """Build per-state epoch dicts for both coordinates.

    Each value is {rec_id: [array(T_bout, N_full), ...]} where missing
    neurons are NaN (same convention as Gate A).
    """
    cep_roam:   dict[str, list[np.ndarray]] = {}
    cep_dwell:  dict[str, list[np.ndarray]] = {}
    gcamp_roam:  dict[str, list[np.ndarray]] = {}
    gcamp_dwell: dict[str, list[np.ndarray]] = {}

    neuropal_ids = sorted(label_maps.keys())
    print(f"  Building epoch dicts for {len(neuropal_ids)} recordings...")

    for rec_id in neuropal_ids:
        h5_path  = H5_DIR / f"{rec_id}-data.h5"
        npz_path = RESID_DIR / f"{rec_id}.npz"
        if not h5_path.exists() or not npz_path.exists():
            print(f"    SKIP {rec_id}: file missing")
            continue

        with h5py.File(h5_path, "r") as hf:
            v_raw    = hf["behavior/velocity"][:]
            trace_h5 = hf["gcamp/trace_array"][:]

        lbl_arr, ret = segment(v_raw, TAU, THR, W_FR, MB_FR)

        npz     = np.load(npz_path)
        resid   = npz["residual"]
        ep_mask = npz["epoch_mask"]
        sub_lbl = list(npz["neuron_labels"])
        T_rec   = resid.shape[0]

        ret_cep = ret & ep_mask
        col_map = label_maps[rec_id]

        resid_full = np.full((T_rec, N_FULL), np.nan)
        gcamp_full = np.full((T_rec, N_FULL), np.nan)

        for i_full, lbl_n in enumerate(COMMON_61):
            if lbl_n in sub_lbl:
                resid_full[:, i_full] = resid[:, sub_lbl.index(lbl_n)]
            if lbl_n in col_map:
                gcamp_full[:, i_full] = trace_h5[:, col_map[lbl_n]]

        for state_int, cep_d, gcamp_d in [
            (1, cep_roam,  gcamp_roam),
            (0, cep_dwell, gcamp_dwell),
        ]:
            cep_slices   = get_epoch_slices(lbl_arr, ret_cep, state_int)
            cep_epochs   = [resid_full[s:e] for s, e in cep_slices if e - s >= MB_FR]
            if cep_epochs:
                cep_d[rec_id] = cep_epochs

            gcamp_slices = get_epoch_slices(lbl_arr, ret, state_int)
            gcamp_epochs = [gcamp_full[s:e] for s, e in gcamp_slices if e - s >= MB_FR]
            if gcamp_epochs:
                gcamp_d[rec_id] = gcamp_epochs

    return cep_roam, cep_dwell, gcamp_roam, gcamp_dwell


# ---------------------------------------------------------------------------
# Per-recording neuron presence
# ---------------------------------------------------------------------------

def neuron_presence_matrix(
    epoch_dict: dict[str, list[np.ndarray]],
) -> np.ndarray:
    """(N_recs, N_full) bool: True if neuron is fully non-NaN in that recording.

    A neuron is "present" in a recording if it has no NaN in any frame
    across all of that recording's contributing state bouts.
    """
    rec_ids = sorted(epoch_dict.keys())
    mat = np.zeros((len(rec_ids), N_FULL), dtype=bool)
    for r, rec_id in enumerate(rec_ids):
        for X_ep in epoch_dict[rec_id]:
            # non-NaN in any frame: but we want fully non-NaN across all frames
            # For a column to be "present" it must be non-NaN in all frames
            # of this recording (consistent neuron identification).
            pass
        # Check: across all bouts, is this neuron non-NaN in every frame?
        all_frames = np.vstack(epoch_dict[rec_id])  # (T_total, N_full)
        mat[r] = ~np.any(np.isnan(all_frames), axis=0)
    return rec_ids, mat


# ---------------------------------------------------------------------------
# n_eff recomputation with included neurons and nan_complete_case
# ---------------------------------------------------------------------------

def neff_with_included(
    epoch_dict: dict[str, list[np.ndarray]],
    included_idx: np.ndarray,
    k_max: int = NEFF_K_MAX_FRAMES,
) -> tuple[float, int]:
    """Recompute n_eff (p25) for included neurons using complete-case rows.

    Returns (neff_p25, n_frames_complete_case).
    Under nan_complete_case: any frame where an included neuron is NaN is dropped.
    n_eff is computed per epoch via integrated autocorrelation of cross-products.
    """
    all_neff: list[float] = []
    n_frames_cc = 0

    for epoch_list in epoch_dict.values():
        for X_ep in epoch_list:
            X_sub = X_ep[:, included_idx]
            # Complete-case: drop rows with any NaN in included columns
            ok = ~np.any(np.isnan(X_sub), axis=1)
            X_clean = X_sub[ok]
            n_frames_cc += X_clean.shape[0]
            if X_clean.shape[0] < 4 or X_clean.shape[1] < 2:
                continue
            ii, jj = np.tril_indices(X_clean.shape[1], k=-1)
            Z = X_clean[:, ii] * X_clean[:, jj]
            tau_ep = tau_int_batch(Z, k_max)
            all_neff.extend((X_clean.shape[0] / tau_ep).tolist())

    neff_p25 = float(np.percentile(all_neff, 25)) if all_neff else 0.0
    return neff_p25, n_frames_cc


# ---------------------------------------------------------------------------
# Viability assessment
# ---------------------------------------------------------------------------

def assess_viability(
    n_neurons: int,
    n_frames_cc: int,
    neff: float,
    n_recordings: int,
    state: str,
) -> dict:
    """Apply Phase 0 validated-regime thresholds.

    Non-roaming optimistic: T>=2000, TPR=1.00
    Roaming pooled:         T>=1000, TPR=0.90
    Non-roaming middle:     T<300,   TPR=0.40 (underpowered)

    For precision estimation: need T >> N*(N-1)/2 pairs.
    Phase 0 minimum viable: T_eff >= 300 (non-roaming middle).
    """
    n_pairs = n_neurons * (n_neurons - 1) // 2
    ratio = neff / max(n_pairs, 1)

    if state == "dwelling":
        if neff >= 2000:
            regime = "optimistic (TPR=1.00 at effect=0.2)"
            viable = True
        elif neff >= 300:
            regime = "middle (TPR~0.40 at effect=0.2; underpowered)"
            viable = True
        else:
            regime = "below-middle (TPR<0.40; not validated)"
            viable = False
    else:  # roaming
        if n_recordings >= 25 and neff >= 1000:
            regime = "pooled-25-animals (TPR=0.90)"
            viable = True
        elif neff >= 300:
            regime = "middle (marginal; sensitive to data loss)"
            viable = False
        else:
            regime = "below-validated-threshold"
            viable = False

    return {
        "n_pairs": n_pairs,
        "neff_to_npairs_ratio": round(ratio, 3),
        "regime": regime,
        "viable": viable,
    }


# ---------------------------------------------------------------------------
# Main coverage computation
# ---------------------------------------------------------------------------

def compute_coverage(
    epoch_dict: dict[str, list[np.ndarray]],
    coord_name: str,
    state_name: str,
) -> dict:
    """Compute Interpretation C coverage for one state x coordinate."""
    n_contributing = len(epoch_dict)
    threshold = math.ceil(COVERAGE_FRACTION * n_contributing)

    rec_ids, presence_mat = neuron_presence_matrix(epoch_dict)
    counts = presence_mat.sum(axis=0)  # (N_full,) int

    included_mask = counts >= threshold
    included_labels = [lbl for lbl, ok in zip(COMMON_61, included_mask) if ok]
    excluded_labels = [lbl for lbl, ok in zip(COMMON_61, included_mask) if not ok]
    included_idx = np.where(included_mask)[0]

    # n_eff with included neurons under complete-case
    neff_p25, n_frames_cc = neff_with_included(epoch_dict, included_idx)

    viability = assess_viability(
        len(included_labels), n_frames_cc, neff_p25, n_contributing, state_name
    )

    # Gate A strict count for reference
    # (strict = present in ALL contributing recordings = count == n_contributing)
    n_strict = int((counts == n_contributing).sum())

    per_neuron = [
        {
            "neuron": lbl,
            "presence_count": int(counts[LABEL_IDX[lbl]]),
            "presence_fraction": round(counts[LABEL_IDX[lbl]] / n_contributing, 3),
            "included": bool(included_mask[LABEL_IDX[lbl]]),
        }
        for lbl in COMMON_61
    ]

    result = {
        "coord": coord_name,
        "state": state_name,
        "n_contributing_recordings": n_contributing,
        "coverage_fraction_threshold": COVERAGE_FRACTION,
        "threshold_count": threshold,
        "n_neurons_strict_complete_case": n_strict,
        "n_neurons_included_interpretation_c": len(included_labels),
        "n_neurons_excluded": len(excluded_labels),
        "included_neuron_labels": sorted(included_labels),
        "excluded_neuron_labels": sorted(excluded_labels),
        "n_frames_complete_case": n_frames_cc,
        "neff_p25": round(neff_p25, 2),
        "viability": viability,
        "per_neuron": per_neuron,
    }
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("Supplementary neuron-coverage computation — Interpretation C")
    print(f"  COVERAGE_FRACTION = {COVERAGE_FRACTION}")
    print(f"  MISSING_NEURON_POLICY = {cfg.MISSING_NEURON_POLICY}  (retained)")
    print()

    print("Loading NeuroPAL label dict...")
    label_records = decode_atanas_jld2(LABEL_PATH)
    label_maps = build_label_maps(label_records, H5_DIR)
    print(f"  {len(label_maps)} recordings mapped.\n")

    print("Building epoch dicts (segmentation identical to Gate A)...")
    cep_roam, cep_dwell, gcamp_roam, gcamp_dwell = build_epoch_dicts(label_maps)
    print()

    configs = [
        (cep_dwell,   "cepnem_residual",       "dwelling"),
        (cep_roam,    "cepnem_residual",       "roaming"),
        (gcamp_dwell, "gcamp_trace_array_zscore", "dwelling"),
        (gcamp_roam,  "gcamp_trace_array_zscore", "roaming"),
    ]

    all_results: list[dict] = []
    for epoch_dict, coord, state in configs:
        print(f"Computing coverage: {coord} / {state}")
        r = compute_coverage(epoch_dict, coord, state)
        all_results.append(r)
        print(f"  contributing_recs = {r['n_contributing_recordings']}")
        print(f"  threshold         = ceil(0.80 x {r['n_contributing_recordings']}) = {r['threshold_count']}")
        print(f"  n_neurons (strict)         = {r['n_neurons_strict_complete_case']}")
        print(f"  n_neurons (Interp. C)      = {r['n_neurons_included_interpretation_c']}")
        print(f"  excluded neurons           = {r['excluded_neuron_labels'] if r['excluded_neuron_labels'] else 'none'}")
        print(f"  n_frames (complete-case)   = {r['n_frames_complete_case']}")
        print(f"  n_eff_p25                  = {r['neff_p25']}")
        print(f"  viability: {r['viability']['regime']}  viable={r['viability']['viable']}")
        print()

    # Save full report
    summary = {
        "interpretation": "C",
        "coverage_fraction": COVERAGE_FRACTION,
        "missing_neuron_policy": cfg.MISSING_NEURON_POLICY,
        "note": (
            "Neuron included if present in >= ceil(COVERAGE_FRACTION * N_contributing) "
            "recordings for that specific state x coordinate. nan_complete_case retained: "
            "frames with any NaN in included neurons are dropped at estimation time."
        ),
        "results": all_results,
    }

    out_path = OUT_DIR / "supplementary_coverage.json"
    # Exclude per_neuron from top-level summary for readability; save separately
    summary_compact = {
        "interpretation": summary["interpretation"],
        "coverage_fraction": summary["coverage_fraction"],
        "missing_neuron_policy": summary["missing_neuron_policy"],
        "note": summary["note"],
        "results": [
            {k: v for k, v in r.items() if k != "per_neuron"}
            for r in all_results
        ],
    }
    with open(out_path, "w") as fh:
        json.dump(summary_compact, fh, indent=2)
    print(f"Summary saved -> {out_path}")

    # Save per-neuron detail table
    neuron_table = {
        f"{r['coord']}__{r['state']}": r["per_neuron"]
        for r in all_results
    }
    neuron_table_path = OUT_DIR / "supplementary_coverage_neuron_table.json"
    with open(neuron_table_path, "w") as fh:
        json.dump(neuron_table, fh, indent=2)
    print(f"Neuron table saved -> {neuron_table_path}")

    print("\nSupplementary coverage computation complete. Stopping as required.")


if __name__ == "__main__":
    main()
