"""Stage 1.1 Gate A: behavioral segmentation, state counts, n_eff, effective neurons.
Stage 1.1 Limited Pilot: 5 real-data graphical-lasso fits (cepnem_residual x dwelling).

Segmentation reproduces Stage 6 exactly (SAMPLING_HZ=5.0 convention).
Pilot matrices are not saved and must not be used for downstream analysis.
"""

from __future__ import annotations

import json
import sys
import time
import warnings as _warnings
from pathlib import Path

import h5py
import numpy as np
from sklearn.covariance import GraphicalLasso

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

H5_DIR    = ROOT / "data/atanas/AtanasKim-Cell2023"
LABEL_PATH = H5_DIR / "neuropal_label_prj_kfc/dict_neuropal_label.jld2"
RESID_DIR  = ROOT / "results/phase1/data/cepnem_residuals"
OUT_DIR    = ROOT / "results/phase1/data/precision"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Segmentation constants — Stage 6 conventions
TAU   = cfg.EWMA_TIMESCALE_SECONDS
THR   = cfg.BEHAV_THRESHOLD
W_FR  = int(cfg.W_TRANS_SECONDS  * SAMPLING_HZ)   # 50 frames
MB_FR = int(cfg.MIN_BOUT_SECONDS  * SAMPLING_HZ)   # 50 frames

COMMON_61: frozenset[str] = frozenset({
    "ADEL","AIBL","AIBR","AIZL","ASEL","ASGL","AUAL","AVAL","AVAR",
    "AVDL","AVEL","AVER","AVJL","AVJR","AWAL","AWBL","AWCL","CEPDL",
    "CEPDR","CEPVL","FLPL","I1L","I1R","I2L","I2R","I3","IL1DR",
    "IL1L","IL1R","IL2DL","IL2DR","IL2VL","IL2VR","M1","M3L","M3R",
    "M4","MI","NSML","NSMR","OLLL","OLLR","OLQDL","OLQDR","OLQVL",
    "OLQVR","RICL","RID","RIVL","RMDDR","RMDL","RMDVL","RMDVR","RMEL",
    "RMER","SMDVL","URBL","URXL","URYDL","URYVL","URYVR",
})


# ---------------------------------------------------------------------------
# BIC alpha selection (replicated from estimators.py _bic_alpha logic)
# ---------------------------------------------------------------------------

def _bic_alpha(X: np.ndarray, alpha_grid: np.ndarray) -> float:
    """Select graphical lasso alpha via BIC on full data."""
    T, N = X.shape
    S = np.cov(X.T)
    best_bic = np.inf
    best_alpha = alpha_grid[0]
    for alpha in alpha_grid:
        try:
            gl = GraphicalLasso(alpha=alpha, max_iter=200, tol=1e-3)
            gl.fit(X)
            Q = gl.precision_
            sign, logdet = np.linalg.slogdet(Q)
            if sign <= 0:
                continue
            ll = 0.5 * T * (logdet - np.trace(S @ Q))
            n_edges = int(np.sum(np.abs(Q) > 1e-6)) // 2
            bic = -2 * ll + n_edges * np.log(T)
            if bic < best_bic:
                best_bic = bic
                best_alpha = alpha
        except Exception:
            continue
    return float(best_alpha)


# ---------------------------------------------------------------------------
# n_eff helpers (replicate Stage 6 method)
# ---------------------------------------------------------------------------

def _neff_pooled(epoch_list: list[np.ndarray], k_max: int = NEFF_K_MAX_FRAMES) -> float:
    all_neff: list[float] = []
    for X_ep in epoch_list:
        if X_ep.shape[0] < 4 or X_ep.shape[1] < 2:
            continue
        ii, jj = np.tril_indices(X_ep.shape[1], k=-1)
        Z = X_ep[:, ii] * X_ep[:, jj]
        tau_ep = tau_int_batch(Z, k_max)
        all_neff.extend((X_ep.shape[0] / tau_ep).tolist())
    return float(np.percentile(all_neff, 25)) if all_neff else 0.0


def _effective_neurons(
    epoch_dict: dict[str, list[np.ndarray]],
    all_labels: list[str],
) -> list[str]:
    """Labels with no NaN in any contributing recording's epochs."""
    n_sub = len(all_labels)
    present = np.ones(n_sub, dtype=bool)
    for epoch_list in epoch_dict.values():
        for X_ep in epoch_list:
            present &= ~np.any(np.isnan(X_ep), axis=0)
    return [lbl for lbl, ok in zip(all_labels, present) if ok]


# ---------------------------------------------------------------------------
# Gate A
# ---------------------------------------------------------------------------

def run_gate_a(
    label_maps: dict[str, dict[str, int]],
) -> tuple[dict, dict, dict, list[str]]:
    """Run segmentation, counts, n_eff, and effective-neuron computation.

    Returns
    -------
    results      : dict with counts/n_eff for both coordinates × states
    cep_dwell    : {rec_id: [epoch arrays]} — CePNEM dwelling epochs
    gcamp_dwell  : {rec_id: [epoch arrays]} — raw GCaMP dwelling epochs
    all_labels   : ordered subgraph label list (from CePNEM .npz)
    """
    cep_roam:   dict[str, list[np.ndarray]] = {}
    cep_dwell:  dict[str, list[np.ndarray]] = {}
    gcamp_roam:  dict[str, list[np.ndarray]] = {}
    gcamp_dwell: dict[str, list[np.ndarray]] = {}
    all_labels: list[str] = []

    # Work in the full COMMON_61 space; pad missing neurons with NaN
    all_labels = sorted(COMMON_61)  # 61-element canonical order
    N_full = len(all_labels)
    label_to_col = {lbl: i for i, lbl in enumerate(all_labels)}

    neuropal_ids = sorted(label_maps.keys())
    print(f"Gate A: processing {len(neuropal_ids)} NeuroPAL recordings "
          f"(full space: {N_full} neurons)...")

    for rec_id in neuropal_ids:
        h5_path  = H5_DIR / f"{rec_id}-data.h5"
        npz_path = RESID_DIR / f"{rec_id}.npz"
        if not h5_path.exists() or not npz_path.exists():
            print(f"  SKIP {rec_id}: missing file")
            continue

        with h5py.File(h5_path, "r") as hf:
            v_raw    = hf["behavior/velocity"][:]
            trace_h5 = hf["gcamp/trace_array"][:]

        lbl_arr, ret = segment(v_raw, TAU, THR, W_FR, MB_FR)

        npz     = np.load(npz_path)
        resid   = npz["residual"]      # (T, n_sub) — n_sub varies per recording
        ep_mask = npz["epoch_mask"]    # (T,) bool
        sub_lbl = list(npz["neuron_labels"])
        T_rec   = resid.shape[0]

        ret_cep = ret & ep_mask

        col_map = label_maps[rec_id]

        # Build full-space (T, N_full) arrays with NaN for missing neurons
        resid_full = np.full((T_rec, N_full), np.nan)
        gcamp_full = np.full((T_rec, N_full), np.nan)

        for i_full, lbl_n in enumerate(all_labels):
            # CePNEM: from .npz if label present in sub_lbl
            if lbl_n in sub_lbl:
                resid_full[:, i_full] = resid[:, sub_lbl.index(lbl_n)]
            # raw GCaMP: from H5 if label present in col_map
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

    # Aggregate
    results: dict = {}
    for coord, roam_d, dwell_d in [
        ("cepnem_residual", cep_roam,  cep_dwell),
        ("gcamp_zscore",    gcamp_roam, gcamp_dwell),
    ]:
        results[coord] = {}
        for state, ed in [("roaming", roam_d), ("dwelling", dwell_d)]:
            n_recs   = len(ed)
            epochs   = [X for ep_list in ed.values() for X in ep_list]
            n_frames = sum(X.shape[0] for X in epochs)
            neff     = _neff_pooled(epochs)
            eff_lbl  = _effective_neurons(ed, all_labels)
            results[coord][state] = {
                "n_recordings":          n_recs,
                "n_frames":              n_frames,
                "neff_p25":              round(neff, 2),
                "n_neurons_effective":   len(eff_lbl),
                "effective_neuron_labels": eff_lbl,
            }
            print(f"  {coord} / {state}: "
                  f"recs={n_recs}  frames={n_frames}  "
                  f"n_eff_p25={neff:.1f}  n_neurons={len(eff_lbl)}")

    return results, cep_dwell, gcamp_dwell, all_labels


# ---------------------------------------------------------------------------
# 5-fit limited precision-estimation pilot
# ---------------------------------------------------------------------------

def run_pilot(
    dwell_dict: dict[str, list[np.ndarray]],
    all_labels: list[str],
    eff_labels: list[str],
) -> dict:
    """5 graphical-lasso fits on pooled CePNEM dwelling frames.

    Pilot matrices are NOT saved and must NOT be used for downstream analysis.
    """
    eff_idx  = np.array([all_labels.index(l) for l in eff_labels], dtype=int)
    epochs   = [X[:, eff_idx] for ep_list in dwell_dict.values() for X in ep_list]
    clean    = []
    for X_ep in epochs:
        ok = ~np.any(np.isnan(X_ep), axis=1)
        if ok.sum() > 1:
            clean.append(X_ep[ok])
    X_pool = np.vstack(clean)
    T_pool, N_eff = X_pool.shape
    print(f"\nPilot: X_pool = ({T_pool}, {N_eff})  coordinate=cepnem_residual  state=dwelling")

    # BIC alpha on full pooled data
    alpha_grid = np.logspace(-2.0, 0.0, 15)
    print("Pilot: selecting BIC alpha...")
    t_bic0 = time.perf_counter()
    alpha_bic = _bic_alpha(X_pool, alpha_grid)
    t_bic1 = time.perf_counter()
    print(f"  alpha_bic={alpha_bic:.4g}  (BIC selection: {t_bic1-t_bic0:.1f}s)")

    T_boot = T_pool // 2
    rng    = np.random.default_rng(42)
    per_fit: list[dict] = []

    print("Pilot: running 5 graphical-lasso fits...")
    for i in range(5):
        idx    = rng.choice(T_pool, size=T_boot, replace=False)
        X_boot = X_pool[idx]
        t0     = time.perf_counter()
        converged = True
        cond_num  = None
        warns: list[str] = []
        try:
            with _warnings.catch_warnings(record=True) as caught:
                _warnings.simplefilter("always")
                gl = GraphicalLasso(alpha=alpha_bic, max_iter=300, tol=1e-3)
                gl.fit(X_boot)
            Q    = gl.precision_
            eigs = np.linalg.eigvalsh(Q)
            cond_num = float(eigs.max() / max(eigs.min(), 1e-12))
            warns = [str(w.message) for w in caught]
        except Exception as exc:
            converged = False
            warns = [str(exc)]
        t1 = time.perf_counter()
        fit_rec = {
            "fit_index":       i + 1,
            "alpha_bic":       float(alpha_bic),
            "wall_time_s":     round(t1 - t0, 3),
            "converged":       converged,
            "condition_number": round(cond_num, 2) if cond_num else None,
            "numerical_warnings": warns,
        }
        per_fit.append(fit_rec)
        cond_str = f"{cond_num:.2e}" if cond_num else "N/A"
        print(f"  Fit {i+1}: {'PASS' if converged else 'FAIL'}  "
              f"alpha={alpha_bic:.4g}  cond={cond_str}  t={t1-t0:.2f}s"
              + (f"  WARNS={warns}" if warns else ""))

    good_times = [f["wall_time_s"] for f in per_fit if f["converged"]]
    avg_t      = float(np.mean(good_times)) if good_times else None
    extrap     = avg_t * 200 if avg_t else None

    pilot = {
        "T_pool":                    T_pool,
        "N_eff":                     N_eff,
        "n_fits":                    5,
        "alpha_bic":                 float(alpha_bic),
        "per_fit":                   per_fit,
        "avg_per_fit_s":             round(avg_t, 3) if avg_t else None,
        "extrapolated_gate_b_s":     round(extrap, 0) if extrap else None,
        "extrapolated_gate_b_min":   round(extrap / 60, 1) if extrap else None,
        "within_30min_threshold":    (extrap < 1800) if extrap else None,
        "note": "Pilot matrices not saved. Not for downstream use.",
    }
    print(f"\nPilot summary:")
    print(f"  Avg per fit: {avg_t:.2f}s")
    print(f"  Extrapolated 200-fit Gate B: {extrap/60:.1f} min")
    print(f"  Within 30-min threshold: {extrap < 1800 if extrap else 'N/A'}")
    return pilot


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading NeuroPAL label dict...")
    label_records = decode_atanas_jld2(LABEL_PATH)
    label_maps    = build_label_maps(label_records, H5_DIR)
    print(f"  {len(label_maps)} recordings mapped.\n")

    gate_a, cep_dwell, _, all_labels = run_gate_a(label_maps)

    # Save Gate A (without neuron label lists for compactness)
    compact = {
        coord: {
            state: {k: v for k, v in d.items() if k != "effective_neuron_labels"}
            for state, d in states.items()
        }
        for coord, states in gate_a.items()
    }
    with open(OUT_DIR / "stage11_gate_a.json", "w") as fh:
        json.dump(compact, fh, indent=2)
    print(f"\nGate A saved → {OUT_DIR/'stage11_gate_a.json'}")

    # Pilot
    eff_labels = gate_a["cepnem_residual"]["dwelling"]["effective_neuron_labels"]
    pilot = run_pilot(cep_dwell, all_labels, eff_labels)
    with open(OUT_DIR / "stage11_pilot.json", "w") as fh:
        json.dump(pilot, fh, indent=2)
    print(f"Pilot saved → {OUT_DIR/'stage11_pilot.json'}")
    print("\nGate A + pilot complete. Stopping as required by checkpoint.")


if __name__ == "__main__":
    main()
