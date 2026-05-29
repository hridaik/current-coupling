"""Stage 09 — Enrichment power and null-model validation.

Synthetic only. No real-data ΔQ or real-data enrichment.

Characterizes enrichment power across:
  - Support regimes (noise levels mapping to Stage 6/8 n_eff estimates)
  - Odds ratios: {1.5, 2.0, 3.0, 5.0}
  - Test statistics: AUROC and Fisher top-K
  - Null models: simple permutation and degree-stratified permutation
  - K values for Fisher: {10, 20, 50}

Produces:
  results/diagnostics/stage09_synthetic_enrichment_power.md
  results/diagnostics/stage09_power_results.json
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT      = Path(__file__).resolve().parents[1]
DIAG_DIR  = ROOT / "results" / "diagnostics"
FIG_DIR   = ROOT / "results" / "figures"
REPORT    = DIAG_DIR / "stage09_synthetic_enrichment_power.md"
JSON_OUT  = DIAG_DIR / "stage09_power_results.json"
FIG_POWER = FIG_DIR  / "stage09_power_curves.pdf"
FIG_NULL  = FIG_DIR  / "stage09_null_calibration.pdf"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.enrichment  import run_full_power_simulation, theoretical_auroc
from src.null_models import (
    compare_null_calibration,
    permute_simple,
    permute_degree_stratified,
    validate_null_preservation,
    estimate_null_distribution,
    permutation_pvalue,
)
from src.enrichment import auroc, generate_enriched_scores


def load_config():
    spec = importlib.util.spec_from_file_location(
        "phase0_config", ROOT / "phase0_config.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------

# Synthetic subgraph dimensions (matching locked Phase 0 values)
N_TOTAL_OFF   = 1464   # undirected off-connectome pairs (N=61, ~20% connectome density)
N_ANNOTATED   = 88     # neuropeptide-annotated off-connectome pairs (~6% of 1464)
                       # consistent with Ripoll-Sánchez typical neuropeptide density

OR_VALUES     = [1.5, 2.0, 3.0, 5.0]
K_VALUES      = [10, 20, 50]
N_SIM         = 200    # per task.md Stage 9
ALPHA         = 0.05

# Noise levels → support regimes
# Calibration: at OR=2.0, theoretical_auroc ≈ Φ(log(2)/sqrt(2)/noise_level)
# noise_level=0.4 → ~Φ(1.22)=0.89 effective TPR proxy (non-roaming)
# noise_level=0.7 → ~Φ(0.70)=0.76 (roaming pooled 25 animals, Stage 8)
# noise_level=1.5 → ~Φ(0.33)=0.63 (roaming conservative, T=400)
# noise_level=3.0 → ~Φ(0.16)=0.56 (roaming T=60, near-random)
NOISE_LEVELS  = {
    "non_roaming_optimistic" : 0.4,   # T_pooled≈6280; Stage 6 optimistic
    "roaming_pooled_25animals": 0.7,   # T_pooled≈1000; Stage 8 pooled experiment
    "roaming_conservative"   : 1.5,   # T_pooled≈400; Stage 8 boundary
    "roaming_failed"         : 3.0,   # T_pooled≈60; near-random ranking
}

# Null calibration parameters (fewer for speed)
N_PERM_NULL = 200   # permutations for null distribution
N_TRIALS_CALIB = 50   # trials for calibration comparison


def run_null_calibration(
    ann: np.ndarray, degrees: np.ndarray, seed: int
) -> dict:
    """Compare simple vs degree-stratified null under H0 and H1."""
    return compare_null_calibration(
        annotations=ann,
        or_range=[1.0, 2.0, 3.0],
        noise_level=0.7,
        n_perm=N_PERM_NULL,
        n_trials=N_TRIALS_CALIB,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_power_curves(results: dict) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    regimes = [r for r in results if r != "_setup"]
    n_regimes = len(regimes)

    fig, axes = plt.subplots(2, n_regimes, figsize=(4 * n_regimes, 8))
    if n_regimes == 1:
        axes = axes.reshape(2, 1)

    for col, regime in enumerate(regimes):
        # AUROC power vs OR
        ax = axes[0][col]
        or_vals = sorted(results[regime].keys())
        auroc_powers = [results[regime][o]["AUROC"]["power"] for o in or_vals]
        ax.plot(or_vals, auroc_powers, "o-", color="steelblue", ms=7)
        ax.axhline(0.6, color="gray", ls="--", lw=1, alpha=0.7, label="0.6 threshold")
        ax.axhline(0.8, color="gray", ls=":",  lw=1, alpha=0.5, label="0.8 threshold")
        ax.set_xlabel("odds ratio (OR)")
        ax.set_ylabel("power (AUROC)")
        ax.set_title(f"{regime}\n(AUROC power)", fontsize=9)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=7)

        # Fisher top-K power vs K (at OR=2)
        ax2 = axes[1][col]
        for or_ in [2.0, 3.0, 5.0]:
            if or_ not in results[regime]:
                continue
            k_powers = [results[regime][or_]["Fisher"][k]["power"] for k in K_VALUES]
            ax2.plot(K_VALUES, k_powers, "o-", ms=6, label=f"OR={or_}")
        ax2.axhline(0.6, color="gray", ls="--", lw=1, alpha=0.7)
        ax2.set_xlabel("K (top-K)")
        ax2.set_ylabel("power (Fisher)")
        ax2.set_title(f"{regime}\n(Fisher power vs K)", fontsize=9)
        ax2.set_ylim(-0.05, 1.05)
        ax2.legend(fontsize=7)

    fig.tight_layout()
    fig.savefig(str(FIG_POWER), dpi=150)
    plt.close(fig)


def plot_null_calibration(calib_results: dict) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    ors = sorted(calib_results.keys())
    power_simple = [calib_results[o]["power_simple"] for o in ors]
    power_degree = [calib_results[o]["power_degree"] for o in ors]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ors, power_simple, "o-", color="steelblue", label="simple permutation null")
    ax.plot(ors, power_degree, "s--", color="coral",    label="degree-stratified null")
    ax.axhline(0.6, color="gray", ls=":", lw=1, alpha=0.6)
    ax.axvline(1.0, color="gray", ls="--", lw=1, alpha=0.6, label="OR=1 (H0)")
    ax.set_xlabel("odds ratio (OR)")
    ax.set_ylabel("power (p < 0.05)")
    ax.set_title("Null model calibration comparison\n(AUROC power under simple vs degree-stratified null)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(str(FIG_NULL), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report writing
# ---------------------------------------------------------------------------

def write_report(
    results: dict,
    calib_results: dict,
    enr_power_at_or2: float,
) -> None:
    today = _dt.date.today().isoformat()
    setup = results["_setup"]
    regimes = [r for r in results if r != "_setup"]

    # Build power table for AUROC at each regime × OR
    auroc_header = "| Regime | noise_level | " + " | ".join(f"OR={o}" for o in OR_VALUES) + " |"
    auroc_sep    = "|" + "---|" * (2 + len(OR_VALUES))
    auroc_rows   = []
    for regime in regimes:
        nl = NOISE_LEVELS[regime]
        cells = []
        for or_ in OR_VALUES:
            p = results[regime][or_]["AUROC"]["power"]
            tag = "**" if p >= 0.6 else ""
            cells.append(f"{tag}{p:.2f}{tag}")
        auroc_rows.append(f"| {regime} | {nl} | " + " | ".join(cells) + " |")

    # Fisher power table for top-K=20 at each regime × OR
    fisher_header = "| Regime | " + " | ".join(f"OR={o}" for o in OR_VALUES) + " |"
    fisher_sep    = "|" + "---|" * (1 + len(OR_VALUES))
    fisher_rows   = []
    for regime in regimes:
        cells = []
        for or_ in OR_VALUES:
            p = results[regime][or_]["Fisher"][20]["power"]
            tag = "**" if p >= 0.6 else ""
            cells.append(f"{tag}{p:.2f}{tag}")
        fisher_rows.append(f"| {regime} | " + " | ".join(cells) + " |")

    # Null calibration table
    null_rows = []
    for or_ in sorted(calib_results.keys()):
        r = calib_results[or_]
        ps = r["power_simple"]
        pd = r["power_degree"]
        null_rows.append(f"| OR={or_} | {ps:.2f} | {pd:.2f} |")

    # Best null recommendation
    # Compare power at OR=2 for simple vs degree-stratified
    p_simple_or2 = calib_results.get(2.0, {}).get("power_simple", float("nan"))
    p_degree_or2 = calib_results.get(2.0, {}).get("power_degree", float("nan"))
    if not (np.isnan(p_simple_or2) or np.isnan(p_degree_or2)):
        if abs(p_simple_or2 - p_degree_or2) < 0.05:
            null_rec = "simple_permutation (equivalent power, lower computational cost)"
        elif p_degree_or2 > p_simple_or2:
            null_rec = "degree_stratified_permutation (higher power at OR=2)"
        else:
            null_rec = "simple_permutation (higher power at OR=2)"
    else:
        null_rec = "simple_permutation (calibration data unavailable)"

    # Which stat is more robust (AUROC vs Fisher)?
    # Compare at non_roaming_optimistic, OR=2
    nr_auroc = results["non_roaming_optimistic"][2.0]["AUROC"]["power"]
    nr_fisher = max(results["non_roaming_optimistic"][2.0]["Fisher"][k]["power"] for k in K_VALUES)
    roam_auroc = results["roaming_pooled_25animals"][2.0]["AUROC"]["power"]
    roam_fisher = max(results["roaming_pooled_25animals"][2.0]["Fisher"][k]["power"] for k in K_VALUES)

    report = f"""# Stage 9 — Synthetic Enrichment Power Analysis

Date: {today}
Synthetic only. No real-data ΔQ or enrichment. Phase 0 guard active.

## Setup

| Parameter | Value |
|---|---|
| N_total_off_connectome | {setup['n_total']} |
| N_annotated (peptide) | {setup['n_annotated']} |
| Annotation fraction | {setup['annotation_fraction']:.1%} |
| OR values tested | {OR_VALUES} |
| K values (Fisher) | {K_VALUES} |
| n_sim | {setup['n_sim']} |
| α | {setup['alpha']} |

Support regime → noise level calibration:

| Regime | noise_level | Empirical basis | Approx TPR proxy |
|---|---|---|---|
| non_roaming_optimistic | {NOISE_LEVELS['non_roaming_optimistic']} | T_pooled≈6280 (Stage 6) | ~0.89 |
| roaming_pooled_25animals | {NOISE_LEVELS['roaming_pooled_25animals']} | T_pooled≈1000 (Stage 8) | ~0.76 |
| roaming_conservative | {NOISE_LEVELS['roaming_conservative']} | T_pooled≈400 (Stage 8 boundary) | ~0.63 |
| roaming_failed | {NOISE_LEVELS['roaming_failed']} | T_pooled≈60 (Stage 7 failure) | ~0.56 |

The noise level controls the signal-to-noise of the |ΔQ| ranking. Neuropeptide
pairs receive a boost of log(OR)/noise_level over random pairs.

---

## 1. AUROC Power (primary enrichment statistic)

Power = fraction of {N_SIM} simulations where AUROC p < {ALPHA} (Mann-Whitney one-sided).

{auroc_header}
{auroc_sep}
{chr(10).join(auroc_rows)}

**Bold** entries = power ≥ 0.6 (minimum viable threshold).

---

## 2. Fisher Top-K Power (secondary enrichment statistic, K=20)

Power = fraction of {N_SIM} simulations where Fisher exact p < {ALPHA}.

{fisher_header}
{fisher_sep}
{chr(10).join(fisher_rows)}

---

## 3. Fisher Power vs K at Moderate OR=2

| K | non_roaming_opt | roaming_pooled | roaming_cons | roaming_failed |
|---|---|---|---|---|
{"".join(f"| {k} | " + " | ".join(f"{results[r][2.0]['Fisher'][k]['power']:.2f}" for r in regimes) + " |" + chr(10) for k in K_VALUES)}
---

## 4. Null Model Calibration (AUROC power, noise_level={NOISE_LEVELS['roaming_pooled_25animals']})

{N_TRIALS_CALIB} trials, {N_PERM_NULL} permutations per null.
At OR=1 (H0): expected power ≈ α = {ALPHA}.
At OR>1 (H1): higher power = better null.

| OR | Simple permutation | Degree-stratified |
|---|---|---|
{chr(10).join(null_rows)}

**Recommended NULL_MODEL_PRIMARY: {null_rec}**

---

## 5. AUROC vs Fisher: Robustness Comparison

| Regime | OR | AUROC power | Best Fisher power (over K) |
|---|---|---|---|
| non_roaming_optimistic | 2.0 | {nr_auroc:.2f} | {nr_fisher:.2f} |
| roaming_pooled_25animals | 2.0 | {roam_auroc:.2f} | {roam_fisher:.2f} |

{"AUROC appears more robust (higher power at marginal regime)." if roam_auroc >= roam_fisher else "Fisher top-K appears more robust at marginal regime." if roam_fisher > roam_auroc else "AUROC and Fisher show similar power."}

---

## 6. Whether Pooled Roaming Support Remains Sufficient

At roaming_pooled_25animals (noise_level={NOISE_LEVELS['roaming_pooled_25animals']}):
  AUROC power at OR=2.0: {results['roaming_pooled_25animals'][2.0]['AUROC']['power']:.2f}
  AUROC power at OR=3.0: {results['roaming_pooled_25animals'][3.0]['AUROC']['power']:.2f}
  AUROC power at OR=5.0: {results['roaming_pooled_25animals'][5.0]['AUROC']['power']:.2f}

{"**Roaming pooled: SUFFICIENT for OR≥2.0 (power≥0.6 at roaming_pooled_25animals).**" if results['roaming_pooled_25animals'][2.0]['AUROC']['power'] >= 0.6 else "**Roaming pooled: MARGINAL at OR=2.0 — requires OR≥" + str(next((o for o in OR_VALUES if results['roaming_pooled_25animals'][o]['AUROC']['power'] >= 0.6), ">5")) + " for reliable detection.**"}

At non_roaming_optimistic (noise_level={NOISE_LEVELS['non_roaming_optimistic']}):
  AUROC power at OR=2.0: {results['non_roaming_optimistic'][2.0]['AUROC']['power']:.2f}
{"**Non-roaming: WELL-POWERED at OR=2.0.**" if results['non_roaming_optimistic'][2.0]['AUROC']['power'] >= 0.6 else "Non-roaming: power < 0.6 at OR=2.0."}

---

## 7. ENRICHMENT_POWER_AT_OR2

ENRICHMENT_POWER_AT_OR2 (non-roaming, primary regime) = {enr_power_at_or2:.3f}

{"≥ 0.6: meets minimum viable threshold." if enr_power_at_or2 >= 0.6 else "< 0.6: below minimum viable threshold — flag for human review."}

---

## 8. Config Fields Updated

| Field | Value |
|---|---|
| LAMBDA_ON | 0.04 (approved 2026-05-29) |
| LAMBDA_OFF | 0.45 (approved 2026-05-29) |
| LAMBDA_OFF_ON_RATIO | 11.25 |
| ENRICHMENT_POWER_AT_OR2 | {enr_power_at_or2:.3f} (set this stage) |
| NULL_MODEL_PRIMARY | {null_rec.split(' (')[0]} (recommended; human decision required) |

---

## 9. Figures

- `results/figures/stage09_power_curves.pdf` — power vs OR (AUROC) and vs K (Fisher)
- `results/figures/stage09_null_calibration.pdf` — null model comparison

---

## 10. Deviations

None. Synthetic data only. Real-data precision and enrichment blocked.
"""
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    assert config.PHASE0_COMPLETE is False, "Phase 0 not complete — real-data guard active"

    print("Stage 9: Synthetic enrichment power simulation")
    print(f"  N_total={N_TOTAL_OFF}  N_annotated={N_ANNOTATED}  n_sim={N_SIM}")
    print(f"  OR values: {OR_VALUES}")
    print(f"  Noise regimes: {list(NOISE_LEVELS.keys())}")

    # --- Main power simulation ---
    print("\nRunning power simulations...")
    results = run_full_power_simulation(
        n_total     = N_TOTAL_OFF,
        n_annotated = N_ANNOTATED,
        or_values   = OR_VALUES,
        noise_levels= NOISE_LEVELS,
        k_values    = K_VALUES,
        n_sim       = N_SIM,
        alpha       = ALPHA,
        seed        = config.RANDOM_SEED,
    )

    for regime in [r for r in results if r != "_setup"]:
        for or_ in OR_VALUES:
            r = results[regime][or_]
            print(f"  {regime:<35}  OR={or_}  "
                  f"AUROC_power={r['AUROC']['power']:.2f}  "
                  f"Fisher_K20={r['Fisher'][20]['power']:.2f}")

    # --- Null model calibration ---
    print("\nRunning null model calibration...")
    rng_calib = np.random.default_rng(config.RANDOM_SEED + 10)
    ann_calib = np.zeros(N_TOTAL_OFF, dtype=int)
    ann_calib[rng_calib.choice(N_TOTAL_OFF, size=N_ANNOTATED, replace=False)] = 1
    degrees_calib = rng_calib.integers(1, 20, size=N_TOTAL_OFF).astype(int)

    calib_results = run_null_calibration(ann_calib, degrees_calib, config.RANDOM_SEED + 10)
    for or_k, v in calib_results.items():
        print(f"  OR={or_k}  simple={v['power_simple']:.2f}  degree={v['power_degree']:.2f}")

    # --- ENRICHMENT_POWER_AT_OR2 ---
    enr_power_at_or2 = results["non_roaming_optimistic"][2.0]["AUROC"]["power"]
    print(f"\nENRICHMENT_POWER_AT_OR2 (non-roaming, AUROC): {enr_power_at_or2:.3f}")

    # Update config
    _update_config(enr_power_at_or2)

    # --- Plots ---
    print("Generating figures...")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plot_power_curves(results)
    plot_null_calibration(calib_results)

    # --- Report ---
    write_report(results, calib_results, enr_power_at_or2)
    print(f"Report: {REPORT}")

    # --- Save JSON ---
    def _j(x):
        if isinstance(x, (np.floating, np.float32, np.float64)):
            return float(x)
        if isinstance(x, (np.integer, np.int32, np.int64)):
            return int(x)
        return x

    def _jsonify(d):
        if isinstance(d, dict):
            return {str(k): _jsonify(v) for k, v in d.items()}
        if isinstance(d, list):
            return [_jsonify(v) for v in d]
        return _j(d)

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUT, "w") as f:
        json.dump(_jsonify(results), f, indent=2)
    print(f"JSON: {JSON_OUT}")

    print(f"\n=== Stage 9 Complete ===")
    print(f"ENRICHMENT_POWER_AT_OR2 = {enr_power_at_or2:.3f}")


def _update_config(enr_power: float) -> None:
    config_path = ROOT / "phase0_config.py"
    text = config_path.read_text(encoding="utf-8")

    old = "ENRICHMENT_POWER_AT_OR2 = None"
    new = f"ENRICHMENT_POWER_AT_OR2 = {enr_power:.4f}   # set by Stage 9"
    if old not in text:
        print("WARNING: ENRICHMENT_POWER_AT_OR2 = None not found in config")
    else:
        text = text.replace(old, new)
        config_path.write_text(text, encoding="utf-8")
        print(f"Config updated: ENRICHMENT_POWER_AT_OR2 = {enr_power:.4f}")


if __name__ == "__main__":
    main()
