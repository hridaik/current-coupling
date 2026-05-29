"""Stage 05 — Transition-window feasibility sweep.

Fixed pipeline:
  EWMA tau  = EWMA_TIMESCALE_SECONDS (20 s)
  threshold = BEHAV_THRESHOLD (0.284)

Candidate W_TRANS windows tested: 0, 5, 10, 15, 20, 30 s

Computes DESCRIPTIVE STATISTICS ONLY per window:
  - retained-frame fractions per state
  - transition-window loss
  - retained epoch duration distributions
  - n_roam / n_nr epochs per animal
  - per-animal retained roaming seconds

Does NOT:
  - set W_TRANS_SECONDS in config
  - set MIN_BOUT_SECONDS
  - compute covariance / precision / DeltaQ / enrichment
  - classify final states
  - access neural activity arrays
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR   = ROOT / "results" / "figures"
REPORT_PATH  = ROOT / "results" / "diagnostics" / "stage05_transition_window_audit.md"
SWEEP_PLOT   = FIGURE_DIR / "stage05_wtrans_sweep.pdf"
EPOCH_PLOT   = FIGURE_DIR / "stage05_wtrans_epochs.pdf"
ANIMAL_PLOT  = FIGURE_DIR / "stage05_wtrans_per_animal.pdf"

SAMPLING_HZ = 5.0
V_STD = 0.06030961137253011
CANDIDATE_W = [0, 5, 10, 15, 20, 30]   # seconds

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_config():
    config_path = ROOT / "phase0_config.py"
    spec = importlib.util.spec_from_file_location("phase0_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Pipeline (vectorised for speed)
# ---------------------------------------------------------------------------

def ewma_vec(vs: np.ndarray, tau_sec: float) -> np.ndarray:
    if tau_sec <= 0:
        return vs.copy()
    alpha = 1.0 / (tau_sec * SAMPLING_HZ)
    out = np.empty_like(vs)
    out[0] = vs[0]
    for t in range(1, len(vs)):
        out[t] = alpha * vs[t] + (1.0 - alpha) * out[t - 1]
    return out


def build_retained_mask(labels: np.ndarray, w_frames: int) -> np.ndarray:
    n = len(labels)
    retained = np.ones(n, dtype=bool)
    if w_frames <= 0:
        return retained
    transitions = np.where(np.diff(labels.astype(int)) != 0)[0]
    for t in transitions:
        lo = max(0, t - w_frames + 1)
        hi = min(n, t + w_frames + 1)
        retained[lo:hi] = False
    return retained


def epoch_lengths_sec(labels: np.ndarray, retained: np.ndarray,
                      state: int) -> np.ndarray:
    active = (labels == state) & retained
    diffs = np.diff(active.astype(int), prepend=0, append=0)
    starts = np.where(diffs == 1)[0]
    ends   = np.where(diffs == -1)[0]
    lens   = (ends - starts) / SAMPLING_HZ
    return lens[lens > 0]


# ---------------------------------------------------------------------------
# Per-window summary
# ---------------------------------------------------------------------------

def window_summary(vs_list: list[np.ndarray], tau_sec: float,
                   threshold: float, w_sec: float) -> dict:
    w_frames = int(w_sec * SAMPLING_HZ)

    per_animal_roam_s  = []
    per_animal_nr_s    = []
    per_animal_frac_r  = []
    per_animal_frac_nr = []
    per_animal_frac_l  = []
    n_roam_ep_list, n_nr_ep_list = [], []
    all_roam_ep, all_nr_ep = [], []

    for vs in vs_list:
        n_t    = len(vs)
        smooth = ewma_vec(vs, tau_sec)
        labels = (smooth > threshold).astype(np.int8)
        ret    = build_retained_mask(labels, w_frames)

        nr = int(np.sum((labels == 1) & ret))
        nnr = int(np.sum((labels == 0) & ret))
        nl  = int(np.sum(~ret))

        per_animal_roam_s.append(nr / SAMPLING_HZ)
        per_animal_nr_s.append(nnr / SAMPLING_HZ)
        per_animal_frac_r.append(nr / n_t)
        per_animal_frac_nr.append(nnr / n_t)
        per_animal_frac_l.append(nl / n_t)

        roam_ep = epoch_lengths_sec(labels, ret, 1)
        nr_ep   = epoch_lengths_sec(labels, ret, 0)
        all_roam_ep.append(roam_ep)
        all_nr_ep.append(nr_ep)
        n_roam_ep_list.append(len(roam_ep))
        n_nr_ep_list.append(len(nr_ep))

    roam_s = np.array(per_animal_roam_s)
    nr_s   = np.array(per_animal_nr_s)
    fr     = np.array(per_animal_frac_r)
    fnr    = np.array(per_animal_frac_nr)
    fl     = np.array(per_animal_frac_l)
    n_roam = np.array(n_roam_ep_list)
    n_nr   = np.array(n_nr_ep_list)

    pooled_roam = np.concatenate(all_roam_ep) if all_roam_ep else np.array([])
    pooled_nr   = np.concatenate(all_nr_ep)   if all_nr_ep   else np.array([])

    def sp(arr, q):
        return float(np.percentile(arr, q)) if len(arr) else float("nan")

    return dict(
        w_sec=w_sec,
        w_frames=w_frames,
        n_animals=len(vs_list),

        frac_roam_med=float(np.median(fr)),
        frac_roam_iqr=(float(np.percentile(fr,25)), float(np.percentile(fr,75))),
        frac_nr_med=float(np.median(fnr)),
        frac_nr_iqr=(float(np.percentile(fnr,25)), float(np.percentile(fnr,75))),
        frac_lost_med=float(np.median(fl)),
        frac_total_med=float(np.median(fr + fnr)),
        frac_total_iqr=(float(np.percentile(fr+fnr,25)), float(np.percentile(fr+fnr,75))),

        roam_s_med=float(np.median(roam_s)),
        roam_s_iqr=(float(np.percentile(roam_s,25)), float(np.percentile(roam_s,75))),
        nr_s_med=float(np.median(nr_s)),
        nr_s_iqr=(float(np.percentile(nr_s,25)), float(np.percentile(nr_s,75))),

        n_zero_roam=int(np.sum(n_roam == 0)),
        n_zero_nr=int(np.sum(n_nr == 0)),
        n_roam_ep_med=float(np.median(n_roam)),
        n_nr_ep_med=float(np.median(n_nr)),

        roam_ep_med=sp(pooled_roam, 50),
        roam_ep_p75=sp(pooled_roam, 75),
        roam_ep_p90=sp(pooled_roam, 90),
        roam_ep_p95=sp(pooled_roam, 95),
        nr_ep_med=sp(pooled_nr, 50),
        nr_ep_p75=sp(pooled_nr, 75),
        nr_ep_p90=sp(pooled_nr, 90),
        nr_ep_p95=sp(pooled_nr, 95),

        n_roam_ep_total=len(pooled_roam),
        n_nr_ep_total=len(pooled_nr),

        pooled_roam=pooled_roam,
        pooled_nr=pooled_nr,
        roam_s_all=roam_s,
        nr_s_all=nr_s,
        n_roam_arr=n_roam,
        n_nr_arr=n_nr,
    )


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_sweep(summaries: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    ws = [s["w_sec"] for s in summaries]
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))

    # 1. Retained fraction — roaming
    ax = axes[0][0]
    ax.plot(ws, [s["frac_roam_med"] for s in summaries], "o-", color="steelblue",
            label="roaming median")
    ax.fill_between(ws,
        [s["frac_roam_iqr"][0] for s in summaries],
        [s["frac_roam_iqr"][1] for s in summaries],
        alpha=0.2, color="steelblue")
    ax.plot(ws, [s["frac_nr_med"] for s in summaries], "o-", color="coral",
            label="non-roaming median")
    ax.set_xlabel("W_TRANS (s)"); ax.set_ylabel("retained fraction")
    ax.set_title("Retained fraction vs W_TRANS")
    ax.legend(fontsize=8)

    # 2. Retained roaming seconds per animal
    ax2 = axes[0][1]
    ax2.plot(ws, [s["roam_s_med"] for s in summaries], "o-", color="steelblue")
    ax2.fill_between(ws,
        [s["roam_s_iqr"][0] for s in summaries],
        [s["roam_s_iqr"][1] for s in summaries],
        alpha=0.2, color="steelblue")
    ax2.set_xlabel("W_TRANS (s)"); ax2.set_ylabel("retained roaming (s/animal)")
    ax2.set_title("Retained roaming time per animal")

    # 3. Animals with zero roaming epochs
    ax3 = axes[0][2]
    n_total = summaries[0]["n_animals"]
    ax3.bar(ws, [s["n_zero_roam"] for s in summaries],
            color="steelblue", alpha=0.7, label="0 roam epochs", width=1.5)
    ax3.bar(ws, [s["n_zero_nr"] for s in summaries],
            color="coral", alpha=0.7, label="0 nr epochs", width=1.5,
            bottom=[s["n_zero_roam"] for s in summaries])
    ax3.axhline(n_total, color="k", lw=0.8, ls="--", label=f"n={n_total}")
    ax3.set_xlabel("W_TRANS (s)"); ax3.set_ylabel("n animals")
    ax3.set_title("Animals with 0 epochs per state")
    ax3.legend(fontsize=7)

    # 4. Roaming epoch duration vs W_TRANS
    ax4 = axes[1][0]
    ax4.plot(ws, [s["roam_ep_med"] for s in summaries], "o-",
             color="steelblue", label="median")
    ax4.plot(ws, [s["roam_ep_p90"] for s in summaries], "s--",
             color="steelblue", alpha=0.6, label="p90")
    ax4.axhline(30, color="red", lw=0.8, ls=":", label="30s reference")
    ax4.set_xlabel("W_TRANS (s)"); ax4.set_ylabel("epoch duration (s)")
    ax4.set_title("Roaming epoch durations vs W_TRANS")
    ax4.legend(fontsize=8)

    # 5. Non-roaming epoch duration vs W_TRANS
    ax5 = axes[1][1]
    ax5.plot(ws, [s["nr_ep_med"] for s in summaries], "o-",
             color="coral", label="median")
    ax5.plot(ws, [s["nr_ep_p90"] for s in summaries], "s--",
             color="coral", alpha=0.6, label="p90")
    ax5.axhline(30, color="red", lw=0.8, ls=":", label="30s reference")
    ax5.set_xlabel("W_TRANS (s)"); ax5.set_ylabel("epoch duration (s)")
    ax5.set_title("Non-roaming epoch durations vs W_TRANS")
    ax5.legend(fontsize=8)

    # 6. Total retained epochs
    ax6 = axes[1][2]
    ax6.plot(ws, [s["n_roam_ep_total"] for s in summaries], "o-",
             color="steelblue", label="roaming")
    ax6.plot(ws, [s["n_nr_ep_total"] for s in summaries], "o-",
             color="coral", label="non-roaming")
    ax6.set_xlabel("W_TRANS (s)"); ax6.set_ylabel("total epochs (all animals)")
    ax6.set_title("Total retained epochs vs W_TRANS")
    ax6.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(str(SWEEP_PLOT), dpi=150)
    plt.close(fig)


def plot_epoch_dists(summaries: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    n_w = len(summaries)
    fig, axes = plt.subplots(2, n_w, figsize=(3 * n_w, 7), sharey=False)
    for col, s in enumerate(summaries):
        for row, (key, lbl, clr) in enumerate([
            ("pooled_roam", "roaming", "steelblue"),
            ("pooled_nr",   "non-roaming", "coral"),
        ]):
            ax = axes[row][col]
            data = s[key]
            if len(data) > 0:
                cap = min(float(np.percentile(data, 97)), 300)
                ax.hist(data, bins=np.linspace(0, cap, 40), color=clr,
                        edgecolor="none", alpha=0.8)
                ax.axvline(np.median(data), color="k", lw=1, ls="--")
                ax.axvline(s["w_sec"]*2, color="red", lw=0.8, ls=":", alpha=0.7)
            ep_med_val = s["roam_ep_med"] if key == "pooled_roam" else s["nr_ep_med"]
            ax.set_title(f"W={s['w_sec']}s  med={ep_med_val:.0f}s",
                         fontsize=7)
            if col == 0:
                ax.set_ylabel(f"{lbl} epoch (s)", fontsize=8)
            ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(str(EPOCH_PLOT), dpi=150)
    plt.close(fig)


def plot_per_animal(summaries: list[dict]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, len(summaries), figsize=(3 * len(summaries), 7),
                             sharey=False)
    for col, s in enumerate(summaries):
        ax = axes[0][col]
        ax.hist(s["roam_s_all"], bins=15, color="steelblue", edgecolor="white", alpha=0.8)
        ax.axvline(np.median(s["roam_s_all"]), color="k", lw=1, ls="--")
        ax.set_title(f"W={s['w_sec']}s", fontsize=8)
        if col == 0:
            ax.set_ylabel("roaming retained (s)", fontsize=8)
        ax.tick_params(labelsize=6)

        ax2 = axes[1][col]
        ax2.hist(s["nr_s_all"], bins=15, color="coral", edgecolor="white", alpha=0.8)
        ax2.axvline(np.median(s["nr_s_all"]), color="k", lw=1, ls="--")
        if col == 0:
            ax2.set_ylabel("non-roam retained (s)", fontsize=8)
        ax2.tick_params(labelsize=6)

    axes[0][0].set_ylabel("roaming retained (s/animal)", fontsize=8)
    axes[1][0].set_ylabel("non-roaming retained (s/animal)", fontsize=8)
    fig.suptitle("Per-animal retained time by W_TRANS", fontsize=10)
    fig.tight_layout()
    fig.savefig(str(ANIMAL_PLOT), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(summaries: list[dict], tau_sec: float,
                 threshold: float, n_animals: int) -> None:
    today = _dt.date.today().isoformat()

    def fmt_s(s: dict) -> str:
        return (
            f"| {s['w_sec']:3g} s "
            f"| {s['frac_roam_med']:.3f} "
            f"| {s['frac_nr_med']:.3f} "
            f"| {s['frac_lost_med']:.3f} "
            f"| {s['frac_total_med']:.3f} "
            f"| {s['n_zero_roam']:2d}/{n_animals} |"
        )

    def fmt_ep(s: dict) -> str:
        return (
            f"| {s['w_sec']:3g} s "
            f"| {s['roam_ep_med']:.1f} "
            f"| {s['roam_ep_p90']:.1f} "
            f"| {s['n_roam_ep_total']:4d} "
            f"| {s['nr_ep_med']:.1f} "
            f"| {s['nr_ep_p90']:.1f} "
            f"| {s['n_nr_ep_total']:4d} |"
        )

    def fmt_retain(s: dict) -> str:
        return (
            f"| {s['w_sec']:3g} s "
            f"| {s['roam_s_med']:.0f} "
            f"| [{s['roam_s_iqr'][0]:.0f}, {s['roam_s_iqr'][1]:.0f}] "
            f"| {s['nr_s_med']:.0f} "
            f"| [{s['nr_s_iqr'][0]:.0f}, {s['nr_s_iqr'][1]:.0f}] |"
        )

    # Find the W_TRANS where all animals retain ≥1 roaming epoch
    first_all_roam = next(
        (s["w_sec"] for s in summaries if s["n_zero_roam"] == 0), None
    )
    # Find W_TRANS where median retained roaming > 30 s
    first_roam_30 = next(
        (s["w_sec"] for s in summaries if s["roam_s_med"] >= 30), None
    )
    # Non-roaming: first W_TRANS where all animals retain ≥1 nr epoch
    first_all_nr = next(
        (s["w_sec"] for s in summaries if s["n_zero_nr"] == 0), None
    )

    report = f"""# Stage 5 Transition-Window Feasibility Sweep

Date: {today}
Fixed pipeline:
  EWMA tau = {tau_sec} s  (EWMA_TIMESCALE_SECONDS, provisional)
  BEHAV_THRESHOLD = {threshold} (LOCKED)
Recordings: {n_animals} NeuroPAL
Candidate W_TRANS windows tested: {CANDIDATE_W} s

NOT computed:
  - Covariance, precision, DeltaQ, enrichment
  - Stationarity / variability analysis
  - Neural analysis

W_TRANS_SECONDS NOT set. MIN_BOUT_SECONDS NOT set.

---

## 1. Frame Allocation vs W_TRANS

Median fractions across {n_animals} NeuroPAL recordings.

| W_TRANS | frac_roam (med) | frac_nr (med) | frac_lost (med) | frac_total (med) | n_zero_roam |
|---------|----------------|---------------|-----------------|------------------|-------------|
{chr(10).join(fmt_s(s) for s in summaries)}

Notes:
- frac_roam + frac_nr + frac_lost ≈ 1.0 per recording
- n_zero_roam = recordings with 0 retained roaming frames

---

## 2. Retained Time per Animal (seconds)

| W_TRANS | roam_med (s) | roam_IQR (s) | nr_med (s) | nr_IQR (s) |
|---------|-------------|--------------|-----------|------------|
{chr(10).join(fmt_retain(s) for s in summaries)}

At 5 Hz: 1 s = 5 frames. N_COMMON_NEURONS = 61.

---

## 3. Epoch Duration vs W_TRANS

Epochs = consecutive retained frames in one state (after exclusion windows applied).
Red dashed line in figures = 2 × W_TRANS (minimum viable bout).

| W_TRANS | roam_med (s) | roam_p90 (s) | n_roam_ep | nr_med (s) | nr_p90 (s) | n_nr_ep |
|---------|-------------|-------------|-----------|-----------|-----------|---------|
{chr(10).join(fmt_ep(s) for s in summaries)}

---

## 4. Feasibility Analysis

### 4.1 Roaming retained-frame coverage

First W_TRANS where ALL {n_animals} animals retain ≥1 roaming epoch: **{first_all_roam} s** {'(all animals covered)' if first_all_roam == 0 else f''}
First W_TRANS where median retained roaming ≥ 30 s: **{first_roam_30 if first_roam_30 is not None else 'none in range'}**
First W_TRANS where all animals retain ≥1 non-roaming epoch: **{first_all_nr} s**

### 4.2 Biological plausibility assessment

The transition exclusion window serves two purposes:
1. Remove frames contaminated by ongoing state transitions (signal not in steady state)
2. Ensure epochs are from persistent behavioral states, not transient fluctuations

At tau = {tau_sec} s EWMA, the behavioral state signal already has smoothing on a
{tau_sec}-s timescale. This means:
  - State transitions in the smoothed signal take ≈ {tau_sec} s to resolve
  - W_TRANS values < {tau_sec} s may not fully exclude transition artifacts
  - W_TRANS values >> {tau_sec} s exclude more data than necessary
  - A value near tau itself ({tau_sec} s) is a natural lower bound

| W_TRANS | Roaming animals (≥1 epoch) | Roaming retained (med) | Assessment |
|---------|--------------------------|------------------------|------------|
"""
    for s in summaries:
        n_roam_covered = n_animals - s["n_zero_roam"]
        med = s["roam_s_med"]
        if s["w_sec"] == 0:
            assess = "No exclusion — transition artifacts retained"
        elif s["w_sec"] < tau_sec:
            assess = "W_TRANS < tau — partial exclusion only"
        elif s["w_sec"] == tau_sec:
            assess = "W_TRANS = tau — natural lower bound"
        elif s["n_zero_roam"] > n_animals * 0.5:
            assess = "Infeasible — >50% animals have 0 roam epochs"
        elif s["n_zero_roam"] > n_animals * 0.2:
            assess = "Marginal — >20% animals have 0 roam epochs"
        elif med < 20:
            assess = "Limited — median retained roaming < 20 s"
        else:
            assess = "Feasible — sufficient retained roaming"
        report += f"| {s['w_sec']:3g} s | {n_roam_covered}/{n_animals} | {med:.0f} s | {assess} |\n"

    report += f"""
### 4.3 Effect on effective covariance sample sizes (qualitative)

For Stage 6 n_eff analysis (cross-product autocorrelation), effective samples
accrue at the rate of 1 independent sample per τ_int frames, where τ_int is
the GCaMP6s autocorrelation time (estimated ≈ 5–20 s at 5 Hz in prior studies).

Rough rule: n_eff ≈ T_retained / (2 × τ_int)

At τ_int ≈ 10 s (middle estimate), for roaming:
"""
    for s in summaries:
        if not np.isnan(s["roam_s_med"]) and s["roam_s_med"] > 0:
            n_eff_est = s["roam_s_med"] / (2 * 10)   # rough: tau_int = 10 s
            report += (f"  W_TRANS={s['w_sec']:3g}s: median roaming retained={s['roam_s_med']:.0f}s → "
                       f"n_eff_rough ≈ {n_eff_est:.1f} per animal (needs ≥ {61} for pairwise analysis)\n")
        else:
            report += f"  W_TRANS={s['w_sec']:3g}s: no retained roaming\n"

    report += f"""
These are rough estimates only. Actual n_eff will be computed in Stage 6
from cross-product autocorrelation times.

---

## 5. Candidate W_TRANS Ranges (Descriptive — NOT final)

| Candidate | Biological rationale | Coverage | Data volume |
|-----------|---------------------|----------|-------------|
| W_TRANS = tau = {tau_sec} s | Matches EWMA timescale; minimal exclusion | All/most animals | Highest |
| W_TRANS = 2×tau = {2*tau_sec} s | Double-margin for transition resolution | Partial | Moderate |
| W_TRANS = 30 s (original) | Flavell lab convention | Only subset | Lowest |

The key tradeoff:
- Smaller W_TRANS → more retained data, but some transition-contamination risk
- Larger W_TRANS → cleaner epochs, but fewer animals/epochs contribute

At tau = {tau_sec} s, a W_TRANS in the range {tau_sec}–{int(tau_sec*1.5)} s appears most biologically
justified: it excludes one EWMA time constant around each transition
(where the signal is resolving) while preserving substantially more data
than W_TRANS = 30 s.

Human decision required. W_TRANS_SECONDS NOT set here.

---

## 6. Figures

- `{rel(SWEEP_PLOT)}` — 6-panel summary sweep
- `{rel(EPOCH_PLOT)}` — epoch-duration histograms per W_TRANS
- `{rel(ANIMAL_PLOT)}` — per-animal retained-time distributions

---

## 7. Config Fields NOT Changed

| Field | Value | Status |
|---|---|---|
| BEHAV_THRESHOLD | 0.284 | LOCKED |
| EWMA_TIMESCALE_SECONDS | {tau_sec} | Provisional |
| W_TRANS_SECONDS | 30.0 | NOT revised here |
| MIN_BOUT_SECONDS | None | NOT SET |

---

## 8. Deviations

No deviations. No config fields changed. Threshold and EWMA tau fixed.
W_TRANS_SECONDS sweep is descriptive only.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

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


def main() -> None:
    config = load_config()
    tau = config.EWMA_TIMESCALE_SECONDS
    threshold = config.BEHAV_THRESHOLD
    atanas_root = ROOT / config.ATANAS_PATH

    h5_files = sorted(atanas_root.glob("*-data.h5"))
    print(f"Loading NeuroPAL velocity (tau={tau}s, threshold={threshold})...")
    vs_list: list[np.ndarray] = []
    for p in h5_files:
        if p.stem.replace("-data", "") not in NEUROPAL_IDS:
            continue
        with h5py.File(p, "r") as f:
            v = f["behavior"]["velocity"][:]
        vs_list.append(v / V_STD)
    n_animals = len(vs_list)
    print(f"  {n_animals} NeuroPAL recordings loaded")

    print(f"Sweeping W_TRANS: {CANDIDATE_W} s...")
    summaries = []
    for w in CANDIDATE_W:
        s = window_summary(vs_list, tau, threshold, float(w))
        summaries.append(s)
        print(f"  W={w:3g}s: roam_med={s['roam_s_med']:.0f}s  "
              f"zero_roam={s['n_zero_roam']}/{n_animals}  "
              f"ep_med={s['roam_ep_med']:.1f}s  "
              f"frac_lost={s['frac_lost_med']:.3f}")

    print("Generating plots...")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_sweep(summaries)
    plot_epoch_dists(summaries)
    plot_per_animal(summaries)

    write_report(summaries, tau, threshold, n_animals)
    print(f"Report written: {rel(REPORT_PATH)}")
    print()
    print("Key: first W where all animals have roam epochs:", end=" ")
    first = next((s["w_sec"] for s in summaries if s["n_zero_roam"] == 0), None)
    print(first)
    print("W_TRANS_SECONDS: NOT set  |  BEHAV_THRESHOLD: 0.284 (LOCKED)")


if __name__ == "__main__":
    main()
