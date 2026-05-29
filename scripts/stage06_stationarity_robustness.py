"""Stage 06 supplement — restricted stationarity robustness audit.

Purpose: disambiguate sampling-noise artifact from true biological
non-stationarity in the Stage 6 NONSTATIONARITY_FRACTION = 1.0 finding.

Allowed operations (Phase 0):
  - covariance matrix estimation for stationarity diagnostics
  - Frobenius norm comparison between covariance halves
  - random-split null (permuted-time-index split) as noise-floor reference

Forbidden:
  - precision matrices on real data
  - graphical lasso, DeltaQ, enrichment, estimator fitting

Key diagnostics:
  1. Temporal split vs random-split null drift per animal-state pair
     → If temporal ≈ null: sampling noise dominates, stationarity plausible
     → If temporal >> null: evidence for true temporal drift
  2. Drift vs effective support (T_half / N_avail)
     → If drift decreases as T/N increases: noise-dominated
  3. Per-quartile summary (best-supported vs worst-supported segments)
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR  = ROOT / "results" / "figures"
DIAG_DIR    = ROOT / "results" / "diagnostics"
REPORT_PATH = DIAG_DIR / "stage06_stationarity_robustness.md"
FIG_SCATTER = FIGURE_DIR / "stage06_stationary_null_scatter.pdf"
FIG_SUPPORT = FIGURE_DIR / "stage06_drift_vs_support.pdf"
FIG_KAPPA   = FIGURE_DIR / "stage06_drift_vs_kappa.pdf"

SAMPLING_HZ = 5.0
V_STD       = 0.06030961137253011
N_NULL_PERMS = 10          # random-split permutations per animal-state pair
MIN_FRAMES_ASSESS = int(120 * SAMPLING_HZ)   # 120 s

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

NEUROPAL_IDS = {
    "2022-06-14-01","2022-06-14-07","2022-06-14-13","2022-06-28-01",
    "2022-06-28-07","2022-07-15-06","2022-07-15-12","2022-07-20-01",
    "2022-07-26-01","2022-08-02-01","2022-12-21-06","2023-01-05-01",
    "2023-01-05-18","2023-01-06-01","2023-01-06-08","2023-01-06-15",
    "2023-01-09-08","2023-01-09-15","2023-01-09-22","2023-01-09-28",
    "2023-01-10-07","2023-01-10-14","2023-01-13-07","2023-01-16-01",
    "2023-01-16-08","2023-01-16-15","2023-01-16-22","2023-01-17-01",
    "2023-01-17-07","2023-01-17-14","2023-01-18-01","2023-01-19-01",
    "2023-01-19-08","2023-01-19-15","2023-01-19-22","2023-01-23-01",
    "2023-01-23-08","2023-01-23-15","2023-01-23-21","2023-03-07-01",
}


def load_config():
    spec = importlib.util.spec_from_file_location(
        "phase0_config", ROOT / "phase0_config.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# Segmentation (identical to Stage 6)
# ---------------------------------------------------------------------------

def ewma(vs: np.ndarray, tau_sec: float) -> np.ndarray:
    if tau_sec <= 0:
        return vs.copy()
    alpha = 1.0 / (tau_sec * SAMPLING_HZ)
    out = np.empty_like(vs)
    out[0] = vs[0]
    for t in range(1, len(vs)):
        out[t] = alpha * vs[t] + (1.0 - alpha) * out[t - 1]
    return out


def segment(v_raw, tau_sec, threshold, w_frames, min_bout_frames):
    vs   = v_raw / V_STD
    sm   = ewma(vs, tau_sec)
    lbl  = (sm > threshold).astype(np.int8)
    n    = len(lbl)
    ret  = np.ones(n, dtype=bool)
    if w_frames > 0:
        for t in np.where(np.diff(lbl.astype(int)) != 0)[0]:
            lo = max(0, t - w_frames + 1)
            hi = min(n, t + w_frames + 1)
            ret[lo:hi] = False
    if min_bout_frames > 0:
        for s in [0, 1]:
            active = (lbl == s) & ret
            d = np.diff(active.astype(int), prepend=0, append=0)
            starts = np.where(d == 1)[0]
            ends   = np.where(d == -1)[0]
            for st, en in zip(starts, ends):
                if (en - st) < min_bout_frames:
                    ret[st:en] = False
    return lbl, ret


# ---------------------------------------------------------------------------
# Covariance drift utilities (covariance only — allowed in Phase 0)
# ---------------------------------------------------------------------------

def temporal_drift(X: np.ndarray) -> tuple[float, float, float, float]:
    """First/second-half Frobenius drift.

    Returns (drift, kappa_first, kappa_second, T_half).
    """
    T, N = X.shape
    mid  = T // 2
    Sf   = np.cov(X[:mid], rowvar=False)
    Ss   = np.cov(X[mid:], rowvar=False)
    kf   = float(np.linalg.cond(Sf))
    ks   = float(np.linalg.cond(Ss))
    nf   = float(np.linalg.norm(Sf, "fro"))
    if nf < 1e-12:
        return float("nan"), kf, ks, float(mid)
    drift = float(np.linalg.norm(Sf - Ss, "fro") / nf)
    return drift, kf, ks, float(mid)


def random_split_drift(X: np.ndarray, rng: np.random.Generator,
                       n_perms: int = N_NULL_PERMS) -> float:
    """Null drift: randomly split time indices (no temporal structure).

    Returns median drift across n_perms permutations.
    This is the expected drift under stationarity + sampling noise.
    """
    T, N = X.shape
    drifts = []
    for _ in range(n_perms):
        idx = rng.permutation(T)
        mid = T // 2
        Xp  = X[idx]
        Sf  = np.cov(Xp[:mid], rowvar=False)
        Ss  = np.cov(Xp[mid:], rowvar=False)
        nf  = float(np.linalg.norm(Sf, "fro"))
        if nf < 1e-12:
            continue
        drifts.append(float(np.linalg.norm(Sf - Ss, "fro") / nf))
    return float(np.median(drifts)) if drifts else float("nan")


# ---------------------------------------------------------------------------
# Per-animal robustness computation
# ---------------------------------------------------------------------------

def assess_animal(rec_id: str, h5path: Path, config,
                  rng: np.random.Generator) -> list[dict]:
    """Return one dict per state that qualifies (≥ MIN_FRAMES_ASSESS retained)."""
    tau   = config.EWMA_TIMESCALE_SECONDS
    thr   = config.BEHAV_THRESHOLD
    w_fr  = int(config.W_TRANS_SECONDS  * SAMPLING_HZ)
    mb_fr = int(config.MIN_BOUT_SECONDS * SAMPLING_HZ)

    with h5py.File(h5path, "r") as f:
        v_raw  = f["behavior/velocity"][:]
        traces = f["gcamp/trace_array"][:]   # (T, N)

    lbl, ret = segment(v_raw, tau, thr, w_fr, mb_fr)
    results  = []

    for state_name, state_int in [("roaming", 1), ("non_roaming", 0)]:
        idx = np.where((lbl == state_int) & ret)[0]
        if len(idx) < MIN_FRAMES_ASSESS:
            continue

        X = traces[idx, :]
        ok = ~np.any(np.isnan(X), axis=0)
        X  = X[:, ok]
        T, N = X.shape
        if N < 5:
            continue

        tdrift, kf, ks, t_half = temporal_drift(X)
        null_drift = random_split_drift(X, rng)

        results.append({
            "rec_id"       : rec_id,
            "state"        : state_name,
            "T_retained"   : T,
            "T_half"       : int(t_half),
            "N_avail"      : N,
            "support_ratio": float(t_half / N),   # T_half / N
            "kappa_first"  : kf,
            "kappa_second" : ks,
            "temporal_drift" : tdrift,
            "null_drift"   : null_drift,
            "drift_excess" : float(tdrift - null_drift),  # > 0 → temporal effect
        })
        print(f"    {state_name}: T={T}  N={N}  T/N={t_half/N:.2f}  "
              f"kappa={kf:.2e}  temporal={tdrift:.3f}  null={null_drift:.3f}  "
              f"excess={tdrift-null_drift:.3f}")

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def make_plots(rows: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    colors = {"roaming": "steelblue", "non_roaming": "coral"}

    # --- scatter: temporal drift vs null drift ---
    fig, ax = plt.subplots(figsize=(6, 5))
    for state in ["roaming", "non_roaming"]:
        pts = [r for r in rows if r["state"] == state]
        if not pts:
            continue
        td = [r["temporal_drift"] for r in pts]
        nd = [r["null_drift"]     for r in pts]
        ax.scatter(nd, td, c=colors[state], alpha=0.75, s=40,
                   label=state.replace("_", "-"))
    lim = max(r["temporal_drift"] for r in rows if not np.isnan(r["temporal_drift"]))
    lim = max(lim, max(r["null_drift"] for r in rows if not np.isnan(r["null_drift"])))
    lim *= 1.1
    ax.plot([0, lim], [0, lim], "k--", lw=1, alpha=0.5, label="y = x (no excess)")
    ax.set_xlabel("null drift (random split)")
    ax.set_ylabel("temporal drift (first / second half)")
    ax.set_title("Temporal vs null-split covariance drift\n"
                 "Points near y=x: sampling noise dominates")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(FIG_SCATTER), dpi=150)
    plt.close(fig)

    # --- scatter: temporal drift vs T_half / N ---
    fig, ax = plt.subplots(figsize=(6, 5))
    for state in ["roaming", "non_roaming"]:
        pts = [r for r in rows if r["state"] == state]
        if not pts:
            continue
        sr = [r["support_ratio"]  for r in pts]
        td = [r["temporal_drift"] for r in pts]
        ax.scatter(sr, td, c=colors[state], alpha=0.75, s=40,
                   label=state.replace("_", "-"))
    ax.axhline(0.3, color="gray", ls="--", lw=1, alpha=0.7, label="drift=0.3 threshold")
    ax.set_xlabel("support ratio (T_half / N_avail)")
    ax.set_ylabel("temporal drift")
    ax.set_title("Temporal drift vs effective sample support\n"
                 "Decreasing trend → noise dominated")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(FIG_SUPPORT), dpi=150)
    plt.close(fig)

    # --- scatter: drift excess vs log10(kappa) ---
    fig, ax = plt.subplots(figsize=(6, 5))
    for state in ["roaming", "non_roaming"]:
        pts = [r for r in rows if r["state"] == state
               and not np.isnan(r["kappa_first"])]
        if not pts:
            continue
        kappa = [np.log10(r["kappa_first"]) for r in pts]
        de    = [r["drift_excess"] for r in pts]
        ax.scatter(kappa, de, c=colors[state], alpha=0.75, s=40,
                   label=state.replace("_", "-"))
    ax.axhline(0, color="k", ls="--", lw=1, alpha=0.5, label="no temporal excess")
    ax.set_xlabel("log₁₀(κ)  condition number first-half cov")
    ax.set_ylabel("drift excess (temporal − null)")
    ax.set_title("Drift excess vs ill-conditioning\n"
                 "No clear trend → excess not driven by κ alone")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(FIG_KAPPA), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(rows: list[dict]) -> None:
    today = _dt.date.today().isoformat()

    def sp(a, q): return float(np.percentile(a, q)) if a else float("nan")

    nr_rows = [r for r in rows if r["state"] == "non_roaming"]
    r_rows  = [r for r in rows if r["state"] == "roaming"]

    def summary_block(pts, label):
        if not pts:
            return f"No {label} animal-state pairs assessed.\n"
        td  = [r["temporal_drift"] for r in pts]
        nd  = [r["null_drift"]     for r in pts]
        sr  = [r["support_ratio"]  for r in pts]
        de  = [r["drift_excess"]   for r in pts]
        n_excess = sum(1 for r in pts if r["drift_excess"] > 0.05)

        # Quartile breakdown by support
        pts_sorted = sorted(pts, key=lambda r: r["support_ratio"])
        n = len(pts_sorted)
        low_q  = pts_sorted[:n//2]
        high_q = pts_sorted[n//2:]
        td_low  = [r["temporal_drift"] for r in low_q]
        td_high = [r["temporal_drift"] for r in high_q]

        return (
            f"n assessed = {len(pts)}\n\n"
            f"| Metric | Median | p25 | p75 |\n"
            f"|---|---|---|---|\n"
            f"| temporal drift | {sp(td,50):.3f} | {sp(td,25):.3f} | {sp(td,75):.3f} |\n"
            f"| null drift (random split) | {sp(nd,50):.3f} | {sp(nd,25):.3f} | {sp(nd,75):.3f} |\n"
            f"| drift excess (temporal − null) | {sp(de,50):.3f} | {sp(de,25):.3f} | {sp(de,75):.3f} |\n"
            f"| support ratio (T_half/N) | {sp(sr,50):.2f} | {sp(sr,25):.2f} | {sp(sr,75):.2f} |\n\n"
            f"Pairs with excess > 0.05 (evidence for temporal effect): "
            f"{n_excess}/{len(pts)}\n\n"
            f"**Quartile comparison by support ratio (T_half/N):**\n\n"
            f"| Support tier | n | Median temporal drift | Median null drift |\n"
            f"|---|---|---|---|\n"
            f"| Low support (bottom half) | {len(low_q)} "
            f"| {sp(td_low,50):.3f} | {sp([r['null_drift'] for r in low_q],50):.3f} |\n"
            f"| High support (top half) | {len(high_q)} "
            f"| {sp(td_high,50):.3f} | {sp([r['null_drift'] for r in high_q],50):.3f} |\n"
        )

    # Pearson correlation: drift_excess vs log10(kappa)
    def corr_excess_kappa(pts):
        de = np.array([r["drift_excess"] for r in pts
                       if not np.isnan(r["kappa_first"])])
        lk = np.array([np.log10(r["kappa_first"]) for r in pts
                       if not np.isnan(r["kappa_first"])])
        if len(de) < 3:
            return float("nan")
        return float(np.corrcoef(de, lk)[0, 1])

    # Overall interpretation
    all_td  = [r["temporal_drift"] for r in rows]
    all_nd  = [r["null_drift"]     for r in rows]
    all_de  = [r["drift_excess"]   for r in rows]
    n_excess_any = sum(1 for d in all_de if d > 0.05)
    median_excess = float(np.median(all_de)) if all_de else float("nan")

    # Support-drift correlation
    sr  = np.array([r["support_ratio"]  for r in rows])
    td  = np.array([r["temporal_drift"] for r in rows])
    corr_sr_td = float(np.corrcoef(sr, td)[0, 1]) if len(sr) >= 3 else float("nan")

    report = f"""# Stage 6 Stationarity Robustness Audit

Date: {today}
Pipeline: EWMA=20s, threshold=0.284, W_TRANS=10s, MIN_BOUT=10s
Neural coordinate: gcamp/trace_array (z-scored)
n_perms (null split): {N_NULL_PERMS}
Animals assessed (≥ 120s retained): {len(rows)} animal-state pairs

Phase-0 compliance:
  - Covariance computed ONLY for stationarity diagnostics
  - No precision matrix, DeltaQ, enrichment, or estimator computed

---

## 1. Non-roaming

{summary_block(nr_rows, 'non-roaming')}

---

## 2. Roaming

{summary_block(r_rows, 'roaming')}

---

## 3. Overall Assessment

### 3.1 Temporal drift vs null drift

| Metric | All pairs (n={len(rows)}) |
|---|---|
| Median temporal drift | {sp(all_td,50):.3f} |
| Median null drift (random split) | {sp(all_nd,50):.3f} |
| Median drift excess (temporal − null) | {median_excess:.3f} |
| Pairs with excess > 0.05 | {n_excess_any}/{len(rows)} |

**Key diagnostic**: If temporal drift ≈ null drift, the first/second-half
Frobenius distance is entirely explained by sampling noise with no temporal
structure required. If temporal drift >> null drift, there is evidence that
covariance shifts over time within the behavioral state.

### 3.2 Drift vs sample support

Pearson r(temporal_drift, T_half/N) = {corr_sr_td:.3f}

A negative correlation means drift decreases as sample support increases,
consistent with a sampling-noise dominant model (more data → better-estimated
covariance → smaller apparent drift). A near-zero or positive correlation
suggests a signal component independent of sample size.

### 3.3 Drift excess vs ill-conditioning

Pearson r(drift_excess, log10(κ)) for non-roaming: {corr_excess_kappa(nr_rows):.3f}

If drift excess (temporal − null) is UNCORRELATED with κ, the excess is not
explained by ill-conditioning alone and may reflect true temporal structure.
If strongly correlated, both temporal and null drift are driven by the same
conditioning regime.

---

## 4. Interpretation

{_interpret(rows, all_td, all_nd, all_de, corr_sr_td, median_excess, n_excess_any)}

---

## 5. Whether Stage 7 Appears Justified

{_stage7_justification(rows, all_td, all_nd, all_de, corr_sr_td)}

---

## 6. Figures

- `results/figures/stage06_stationary_null_scatter.pdf` — temporal vs null drift
- `results/figures/stage06_drift_vs_support.pdf` — temporal drift vs T_half/N
- `results/figures/stage06_drift_vs_kappa.pdf` — drift excess vs log10(κ)

---

## 7. Deviations

None. No thresholds, EWMA, or segmentation parameters changed.
"""

    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def _interpret(rows, all_td, all_nd, all_de, corr_sr_td, median_excess, n_excess_any):
    sp = lambda a, q: float(np.percentile(a, q)) if a else float("nan")
    null_close  = abs(sp(all_td,50) - sp(all_nd,50)) < 0.1
    support_neg = corr_sr_td < -0.2
    excess_small = median_excess < 0.1
    n_strong = sum(1 for d in all_de if d > 0.20)

    lines = []
    if null_close and excess_small:
        lines.append("**SAMPLING NOISE DOMINATES**: Median temporal drift "
                     f"({sp(all_td,50):.3f}) is close to null drift ({sp(all_nd,50):.3f}) "
                     f"and drift excess is small ({median_excess:.3f}). "
                     "NONSTATIONARITY_FRACTION = 1.0 is consistent with being a "
                     "sampling-noise artifact. No evidence of biologically meaningful "
                     "temporal covariance drift within behavioral states.")
    elif n_strong > 0 and n_strong / len(rows) > 0.3:
        lines.append(f"**MIXED SIGNAL**: {n_strong}/{len(rows)} pairs have excess > 0.20, "
                     "suggesting some temporal structure beyond sampling noise. "
                     "Further investigation recommended before Stage 7.")
    else:
        lines.append(f"**WEAK TEMPORAL SIGNAL**: {n_excess_any}/{len(rows)} pairs "
                     f"have drift excess > 0.05. Median excess = {median_excess:.3f}. "
                     "The evidence for true non-stationarity is weak but not zero.")

    if support_neg:
        lines.append(f"\nSupport-drift correlation r = {corr_sr_td:.3f} (negative), "
                     "consistent with noise-dominated drift: better-supported segments "
                     "show lower drift as expected under sampling noise.")
    else:
        lines.append(f"\nSupport-drift correlation r = {corr_sr_td:.3f} (not clearly "
                     "negative), suggesting the drift may not purely decrease with "
                     "sample size. Weak temporal structure cannot be ruled out.")

    return "\n".join(lines)


def _stage7_justification(rows, all_td, all_nd, all_de, corr_sr_td):
    sp = lambda a, q: float(np.percentile(a, q)) if a else float("nan")
    median_excess = float(np.median(all_de)) if all_de else float("nan")
    null_close = abs(sp(all_td,50) - sp(all_nd,50)) < 0.15
    excess_ok  = median_excess < 0.15

    if null_close and excess_ok:
        return (
            "**Proceeding to Stage 7 appears justified.**\n\n"
            "The stationarity robustness audit indicates that the NONSTATIONARITY_FRACTION "
            "= 1.0 finding is consistent with a sampling-noise artifact:\n"
            f"- Median temporal drift ({sp(all_td,50):.3f}) ≈ null-split drift "
            f"({sp(all_nd,50):.3f})\n"
            f"- Median excess = {median_excess:.3f} (< 0.15)\n"
            "- The data do not provide evidence of biologically meaningful "
            "within-state covariance non-stationarity.\n\n"
            "Stage 7 estimator dry-runs on synthetic data are appropriate. "
            "The NONSTATIONARITY_FRACTION field remains at 1.0 but is now "
            "interpreted as reflecting sampling limitations, not confirmed biology."
        )
    else:
        return (
            "**Caution: stage 7 should proceed but flag stationarity concern.**\n\n"
            f"Median drift excess = {median_excess:.3f}. Some temporal structure "
            "beyond sampling noise cannot be excluded. Stage 7 should include "
            "stationarity sensitivity checks. Document this in DEVIATIONS.md "
            "if proceeding without further diagnostic."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    rng    = np.random.default_rng(config.RANDOM_SEED)

    atanas_root = ROOT / config.ATANAS_PATH
    h5_files    = {
        p.stem.replace("-data", ""): p
        for p in sorted(atanas_root.glob("*-data.h5"))
        if p.stem.replace("-data", "") in NEUROPAL_IDS
    }
    print(f"Stationarity robustness audit: {len(h5_files)} NeuroPAL recordings")
    print(f"MIN_FRAMES_ASSESS = {MIN_FRAMES_ASSESS} frames ({MIN_FRAMES_ASSESS/SAMPLING_HZ:.0f}s)")
    print(f"N_NULL_PERMS = {N_NULL_PERMS}")

    all_rows = []
    for i, (rid, h5p) in enumerate(sorted(h5_files.items())):
        print(f"  [{i+1:02d}] {rid}")
        rows = assess_animal(rid, h5p, config, rng)
        all_rows.extend(rows)

    print(f"\n{len(all_rows)} animal-state pairs assessed")

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    make_plots(all_rows)

    write_report(all_rows)

    print(f"\nReport: {REPORT_PATH}")
    print(f"Figures: {FIG_SCATTER.name}, {FIG_SUPPORT.name}, {FIG_KAPPA.name}")

    # Print summary
    all_td = [r["temporal_drift"] for r in all_rows]
    all_nd = [r["null_drift"]     for r in all_rows]
    all_de = [r["drift_excess"]   for r in all_rows]
    print(f"\n=== Robustness Summary ===")
    print(f"  Temporal drift median: {np.median(all_td):.3f}  p75: {np.percentile(all_td,75):.3f}")
    print(f"  Null drift median:     {np.median(all_nd):.3f}  p75: {np.percentile(all_nd,75):.3f}")
    print(f"  Excess median:         {np.median(all_de):.3f}")
    sr = np.array([r["support_ratio"]  for r in all_rows])
    td = np.array([r["temporal_drift"] for r in all_rows])
    print(f"  r(drift, T/N) = {np.corrcoef(sr, td)[0,1]:.3f}")
    n_excess = sum(1 for d in all_de if d > 0.05)
    print(f"  Pairs with excess > 0.05: {n_excess}/{len(all_rows)}")


if __name__ == "__main__":
    main()
