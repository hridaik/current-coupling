"""CePNEM residualization for Phase 1, Stage 1.0.

Implements the model_nl8 forward pass from CePNEM.jl/src/model.jl and the full
residualization and verification pipeline for one recording at a time.

All equations are direct translations of the confirmed Julia source:
  data/atanas/AtanasKim-Cell2023/src/CePNEM/CePNEM.jl/src/model.jl
Standardization constants from:
  data/atanas/AtanasKim-Cell2023/src/CePNEM/CePNEM.jl/src/antsun_data.jl
"""

from __future__ import annotations

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Standardization constants (confirmed from antsun_data.jl)
# ---------------------------------------------------------------------------
V_STD  = 0.06030961137253011
TH_STD = 0.49429038957075727
P_STD  = 1.2772001409506841

# NL10d parameter ordering (confirmed by param[4]=0.0 across all 68 recordings)
# stp[0]=c_vT, [1]=c_v, [2]=c_th, [3]=c_P, [4]=0 (disabled), [5]=y0, [6]=s0, [7]=b
# [8]=l0, [9]=sigma0_SE, [10]=sigma0_noise  (GP residual params, not used here)
_P_CVT = 0
_P_CV  = 1
_P_CTH = 2
_P_CP  = 3
_P_Y0  = 5
_P_S0  = 6
_P_B   = 7


def model_nl8_forward(
    c_vT: float, c_v: float, c_th: float, c_P: float,
    y0: float, s0: float, b: float,
    v_ep: np.ndarray, th_ep: np.ndarray, P_ep: np.ndarray,
) -> np.ndarray:
    """Predicted behavioral component for one neuron, one epoch.

    Direct translation of model_nl8() from CePNEM.jl/src/model.jl.
    c = 0.0 for NL10d (param[4] confirmed zero in all 68 recordings).

    Parameters
    ----------
    v_ep, th_ep, P_ep : (T_ep,) arrays — raw (unstandardized) covariates
        for this epoch slice. Standardization is applied internally.

    Returns
    -------
    activity : (T_ep,) array — predicted behavioral trace (same scale as
        the input trace_array, which is globally z-scored).
    """
    std_v  = v_ep  / V_STD
    std_th = th_ep / TH_STD
    std_P  = P_ep  / P_STD
    s = 10.0 * np.exp(s0)  # compute_s(s0) from model.jl

    denom  = s + 1.0
    # Direction-sensitive rectification factors (neuron-level scalars)
    sqrt_term = np.sqrt(c_vT**2 + 1.0)
    A = (c_vT + 1.0) / sqrt_term    # positive-velocity factor
    B = 2.0 * c_vT / sqrt_term      # negative-velocity correction

    T_ep = len(v_ep)
    activity = np.empty(T_ep, dtype=np.float64)
    activity_prev = y0

    for t in range(T_ep):
        # D is the direction-rectified gain at time t
        D = A - B * float(std_v[t] < 0.0)
        behavioral_input = D * (c_v * std_v[t] + c_th * std_th[t] + c_P * std_P[t])
        activity[t] = (behavioral_input / denom
                       + (activity_prev - b) * s / denom
                       + b)
        activity_prev = activity[t]

    return activity


def first_frame_analytical(
    c_vT: float, c_v: float, c_th: float, c_P: float,
    y0: float, s0: float, b: float,
    v0: float, th0: float, P0: float,
) -> float:
    """Closed-form expression for model_nl8_forward()[t=0].

    No recursion: activity[0] depends only on the parameters and the first
    frame of each covariate. Used for implementation verification
    (first-frame algebraic identity check) without biological assumptions.
    """
    std_v0  = v0  / V_STD
    std_th0 = th0 / TH_STD
    std_P0  = P0  / P_STD
    s = 10.0 * np.exp(s0)
    sqrt_term = np.sqrt(c_vT**2 + 1.0)
    D0 = ((c_vT + 1.0) / sqrt_term
          - 2.0 * c_vT / sqrt_term * float(std_v0 < 0.0))
    return (D0 * (c_v * std_v0 + c_th * std_th0 + c_P * std_P0) / (s + 1.0)
            + (y0 - b) * s / (s + 1.0) + b)


def residualize_recording(
    trace_array: np.ndarray,
    v: np.ndarray,
    th: np.ndarray,
    P: np.ndarray,
    ranges: np.ndarray,
    stp: np.ndarray,
    subgraph_cols: np.ndarray,
) -> dict:
    """Compute raw and normalized residuals for one recording.

    Parameters
    ----------
    trace_array : (T, N_total) — globally z-scored calcium trace
    v, th, P    : (T,) — raw covariates (confirmed unstandardized)
    ranges      : (n_epochs,) structured array with fields 'start', 'stop'
                  in Julia 1-based indexing
    stp         : (11, 10001, N_total, n_epochs) — posterior samples
    subgraph_cols : (n_sub,) int array — column indices into trace_array / stp
                   for the common-61-neuron subgraph, in subgraph order

    Returns
    -------
    dict with keys:
        residual_raw    : (T, n_sub) — raw residual before normalization; NaN at gap frames
        residual_normed : (T, n_sub) — z_score_global normalized residual
        predicted       : (T, n_sub) — behavioral predicted component; NaN at gap frames
        epoch_mask      : (T,) bool — True for in-epoch frames
        params_med      : (11, n_sub, n_epochs) — posterior medians (for audit)
        var_ratios      : (n_sub,) — var(residual_raw) / var(trace_array), in-epoch frames
        identity_errors : (n_sub, n_epochs) — |forward[t=0] - analytical[t=0]|
    """
    T_total, N_total = trace_array.shape
    n_sub = len(subgraph_cols)
    n_epochs = ranges.shape[0]

    residual_raw    = np.full((T_total, n_sub), np.nan)
    predicted       = np.full((T_total, n_sub), np.nan)
    epoch_mask      = np.zeros(T_total, dtype=bool)

    # Compute posterior medians: (11, n_sub, n_epochs)
    stp_sub = stp[:, :, subgraph_cols, :]     # (11, 10001, n_sub, n_epochs)
    params_med = np.median(stp_sub, axis=1)   # (11, n_sub, n_epochs)

    identity_errors = np.zeros((n_sub, n_epochs), dtype=np.float64)

    for e_idx in range(n_epochs):
        # Julia 1-based → Python 0-based slice
        t_start = int(ranges[e_idx]['start']) - 1
        t_stop  = int(ranges[e_idx]['stop'])      # inclusive in Julia → exclusive end in Python
        epoch_mask[t_start:t_stop] = True

        v_ep  = v[t_start:t_stop]
        th_ep = th[t_start:t_stop]
        P_ep  = P[t_start:t_stop]
        T_ep  = t_stop - t_start

        # Vectorized forward pass over all subgraph neurons for this epoch
        p = params_med[:, :, e_idx]   # (11, n_sub)
        c_vT_vec = p[_P_CVT]          # (n_sub,)
        c_v_vec  = p[_P_CV]
        c_th_vec = p[_P_CTH]
        c_P_vec  = p[_P_CP]
        y0_vec   = p[_P_Y0]
        s0_vec   = p[_P_S0]
        b_vec    = p[_P_B]

        std_v  = v_ep  / V_STD        # (T_ep,)
        std_th = th_ep / TH_STD
        std_P  = P_ep  / P_STD

        s_vec     = 10.0 * np.exp(s0_vec)    # (n_sub,)
        sqrt_term = np.sqrt(c_vT_vec**2 + 1.0)
        A_vec = (c_vT_vec + 1.0) / sqrt_term
        B_vec = 2.0 * c_vT_vec / sqrt_term

        act = np.zeros((T_ep, n_sub), dtype=np.float64)
        act_prev = y0_vec.copy()              # (n_sub,)

        for t in range(T_ep):
            neg = float(std_v[t] < 0.0)
            D_t = A_vec - B_vec * neg         # (n_sub,)
            behav = D_t * (c_v_vec * std_v[t] + c_th_vec * std_th[t] + c_P_vec * std_P[t])
            act[t] = behav / (s_vec + 1.0) + (act_prev - b_vec) * s_vec / (s_vec + 1.0) + b_vec
            act_prev = act[t]

        predicted[t_start:t_stop, :] = act

        # First-frame identity check for each neuron in this epoch
        for ni in range(n_sub):
            expected = first_frame_analytical(
                c_vT_vec[ni], c_v_vec[ni], c_th_vec[ni], c_P_vec[ni],
                y0_vec[ni], s0_vec[ni], b_vec[ni],
                v_ep[0], th_ep[0], P_ep[0],
            )
            identity_errors[ni, e_idx] = abs(act[0, ni] - expected)

    # Compute raw residual for in-epoch frames
    in_ep = epoch_mask
    trace_sub = trace_array[:, subgraph_cols]   # (T, n_sub)
    residual_raw[in_ep, :] = trace_sub[in_ep, :] - predicted[in_ep, :]

    # Variance ratio — computed on residual_raw BEFORE normalization
    var_ratios = np.full(n_sub, np.nan)
    for ni in range(n_sub):
        r_ep = residual_raw[in_ep, ni]
        t_ep = trace_sub[in_ep, ni]
        var_t = np.var(t_ep)
        if var_t > 1e-12:
            var_ratios[ni] = np.var(r_ep) / var_t

    # z_score_global normalization of raw residual (in-epoch frames only)
    residual_normed = np.full((T_total, n_sub), np.nan)
    for ni in range(n_sub):
        r = residual_raw[in_ep, ni]
        mu = np.mean(r)
        sigma = np.std(r)
        if sigma > 1e-12:
            residual_normed[in_ep, ni] = (r - mu) / sigma
        else:
            residual_normed[in_ep, ni] = r - mu

    return {
        "residual_raw":    residual_raw,
        "residual_normed": residual_normed,
        "predicted":       predicted,
        "epoch_mask":      epoch_mask,
        "params_med":      params_med,
        "var_ratios":      var_ratios,
        "identity_errors": identity_errors,
    }


def check_decorrelation(
    residual_normed: np.ndarray,
    trace_sub: np.ndarray,
    covariates: dict[str, np.ndarray],
    epoch_mask: np.ndarray,
) -> dict:
    """Check A: behavioral decorrelation.

    Parameters
    ----------
    residual_normed : (T, n_sub)
    trace_sub       : (T, n_sub) — raw trace for subgraph neurons
    covariates      : {name: (T,)} — all covariates to test
    epoch_mask      : (T,) bool

    Returns
    -------
    dict with per-covariate arrays r_raw (n_sub,), r_resid (n_sub,), reduction (n_sub,)
    """
    results = {}
    for cov_name, cov in covariates.items():
        cov_ep = cov[epoch_mask]
        r_raw   = np.zeros(residual_normed.shape[1])
        r_resid = np.zeros(residual_normed.shape[1])
        for ni in range(residual_normed.shape[1]):
            t_ep = trace_sub[epoch_mask, ni]
            re_ep = residual_normed[epoch_mask, ni]
            valid_t = ~np.isnan(t_ep) & ~np.isnan(cov_ep)
            valid_r = ~np.isnan(re_ep) & ~np.isnan(cov_ep)
            if valid_t.sum() > 2:
                r_raw[ni] = stats.pearsonr(t_ep[valid_t], cov_ep[valid_t])[0]
            if valid_r.sum() > 2:
                r_resid[ni] = stats.pearsonr(re_ep[valid_r], cov_ep[valid_r])[0]
        reduction = 1.0 - np.abs(r_resid) / np.maximum(np.abs(r_raw), 1e-6)
        results[cov_name] = {
            "r_raw":    r_raw.tolist(),
            "r_resid":  r_resid.tolist(),
            "reduction": reduction.tolist(),
            "median_abs_r_raw":   float(np.median(np.abs(r_raw))),
            "median_abs_r_resid": float(np.median(np.abs(r_resid))),
            "median_reduction":   float(np.median(reduction)),
        }
    return results


def check_stationarity(
    residual_normed: np.ndarray,
    trace_sub: np.ndarray,
    epoch_mask: np.ndarray,
) -> dict:
    """Check D: first/second-half covariance drift (single recording).

    For each recording, split in-epoch frames into first and second half
    chronologically. Compute Frobenius-norm drift of the covariance matrix.
    Compare CePNEM residual drift to raw trace drift.

    Returns
    -------
    dict with drift_raw, drift_resid, and ratio (resid/raw).
    """
    in_ep_idx = np.where(epoch_mask)[0]
    n = len(in_ep_idx)
    if n < 4:
        return {"drift_raw": None, "drift_resid": None, "ratio": None,
                "note": "insufficient frames"}
    half = n // 2
    first_idx  = in_ep_idx[:half]
    second_idx = in_ep_idx[half:]

    def _cov_drift(X: np.ndarray) -> float:
        # NaN check on in-epoch frames only: trailing frames after the last epoch
        # are NaN in residual_normed and must not discard otherwise valid columns.
        ok = ~np.any(np.isnan(X[in_ep_idx]), axis=0)
        X = X[:, ok]
        if X.shape[1] < 2:
            return np.nan
        C1 = np.cov(X[first_idx].T)
        C2 = np.cov(X[second_idx].T)
        fn1 = np.linalg.norm(C1, 'fro')
        if fn1 < 1e-12:
            return np.nan
        return float(np.linalg.norm(C2 - C1, 'fro') / fn1)

    drift_raw   = _cov_drift(trace_sub)
    drift_resid = _cov_drift(residual_normed)
    ratio = (drift_resid / drift_raw
             if drift_raw and drift_raw > 1e-12 and not np.isnan(drift_resid)
             else None)

    return {
        "drift_raw":   drift_raw,
        "drift_resid": drift_resid,
        "ratio_resid_over_raw": ratio,
        "note": "first/second-half Frobenius drift; ratio < 1 means residualization reduces drift",
    }
