"""Enrichment statistics and power simulation for Phase 0.

All computations here are SYNTHETIC ONLY during Phase 0. The real-data
enrichment test (using actual ΔQ) is forbidden until PHASE0_COMPLETE=True.

Implements:
  - AUROC enrichment statistic (Mann-Whitney / ranking-based)
  - Fisher top-K enrichment statistic
  - Synthetic ΔQ ranking generation with specified odds-ratio enrichment
  - Enrichment power simulation across support regimes
"""

from __future__ import annotations

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Core enrichment statistics
# ---------------------------------------------------------------------------

def auroc(annotations: np.ndarray, scores: np.ndarray) -> float:
    """Area under the ROC curve for binary annotations vs continuous scores.

    Equivalent to the Mann-Whitney U statistic normalized to [0, 1].
    Higher score → predicted positive; annotations==1 are the positives.

    Parameters
    ----------
    annotations : (N,) int/bool array — 1 = annotated (positive class)
    scores      : (N,) float array — higher value = predicted positive

    Returns
    -------
    float in [0, 1]; 0.5 = random; 1.0 = perfect discrimination
    """
    ann = np.asarray(annotations, dtype=bool)
    sc  = np.asarray(scores, dtype=float)
    n1  = ann.sum()
    n0  = (~ann).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    u, _ = stats.mannwhitneyu(sc[ann], sc[~ann], alternative="greater")
    return float(u / (n1 * n0))


def auroc_pvalue(annotations: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """AUROC and one-sided p-value using Mann-Whitney U test.

    Tests H1: annotated pairs tend to have higher scores (one-sided).

    Returns
    -------
    (auroc_value, p_value)
    """
    ann = np.asarray(annotations, dtype=bool)
    sc  = np.asarray(scores, dtype=float)
    n1  = int(ann.sum())
    n0  = int((~ann).sum())
    if n1 == 0 or n0 == 0:
        return float("nan"), float("nan")
    u, p = stats.mannwhitneyu(sc[ann], sc[~ann], alternative="greater")
    auc = float(u / (n1 * n0))
    return auc, float(p)


def fisher_topk(annotations: np.ndarray, scores: np.ndarray,
                k: int) -> tuple[float, float]:
    """Fisher exact test for over-representation of annotated pairs in top-K.

    Tests H1: more annotated pairs in top-K than expected by chance.

    Parameters
    ----------
    annotations : (N,) binary array
    scores      : (N,) float array — higher = more enriched
    k           : number of top pairs to examine

    Returns
    -------
    (odds_ratio, p_value) from Fisher exact test
    """
    ann = np.asarray(annotations, dtype=bool)
    N   = len(ann)
    k   = min(k, N)
    top_idx = np.argsort(scores)[::-1][:k]
    top_mask = np.zeros(N, dtype=bool)
    top_mask[top_idx] = True

    a = int(( top_mask &  ann).sum())   # top-K, annotated
    b = int(( top_mask & ~ann).sum())   # top-K, not annotated
    c = int((~top_mask &  ann).sum())   # rest, annotated
    d = int((~top_mask & ~ann).sum())   # rest, not annotated

    table = np.array([[a, b], [c, d]])
    or_, p = stats.fisher_exact(table, alternative="greater")
    return float(or_), float(p)


# ---------------------------------------------------------------------------
# Synthetic ΔQ score generation
# ---------------------------------------------------------------------------

def generate_enriched_scores(
    annotations: np.ndarray,
    or_: float,
    noise_level: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate synthetic |ΔQ| scores with specified enrichment odds ratio.

    Model: score_i = log(or_) × annotation_i / noise_level + N(0,1)

    Annotated pairs (neuropeptide) receive a positive boost proportional to
    log(OR). The noise_level controls signal-to-noise:
      - noise_level=0.5: high-quality ΔQ recovery (non-roaming optimistic)
      - noise_level=1.0: moderate quality (roaming pooled)
      - noise_level=2.0: low quality (roaming conservative)
      - noise_level=4.0: very low (roaming at T=400)

    The effective AUROC under this model is approximately:
        AUC ≈ Φ(log(OR) / (noise_level × √2))

    Parameters
    ----------
    annotations  : (N,) binary — 1=neuropeptide
    or_          : odds ratio ≥ 1.0
    noise_level  : noise standard deviation (1.0 = unit noise)
    rng          : random generator

    Returns
    -------
    (N,) float score array
    """
    ann     = np.asarray(annotations, dtype=float)
    boost   = np.log(max(or_, 1.0 + 1e-9)) * ann / noise_level
    return boost + rng.standard_normal(len(ann))


def theoretical_auroc(or_: float, noise_level: float) -> float:
    """Approximate theoretical AUROC for the enrichment model."""
    signal = np.log(max(or_, 1.0 + 1e-9)) / noise_level
    return float(stats.norm.cdf(signal / np.sqrt(2)))


# ---------------------------------------------------------------------------
# Power simulation
# ---------------------------------------------------------------------------

def power_auroc(
    annotations: np.ndarray,
    or_: float,
    noise_level: float,
    n_sim: int,
    alpha: float,
    rng: np.random.Generator,
) -> dict:
    """Estimate AUROC enrichment power by simulation.

    Parameters
    ----------
    annotations  : (N,) binary annotation vector (fixed across simulations)
    or_          : odds ratio for the enrichment signal
    noise_level  : score noise level (see generate_enriched_scores)
    n_sim        : number of simulations
    alpha        : significance threshold (typically 0.05)
    rng          : random generator

    Returns
    -------
    dict with keys: power, mean_auroc, std_auroc, mean_pvalue
    """
    auc_vals, p_vals = [], []
    for _ in range(n_sim):
        scores  = generate_enriched_scores(annotations, or_, noise_level, rng)
        auc, pv = auroc_pvalue(annotations, scores)
        auc_vals.append(auc)
        p_vals.append(pv)

    auc_arr = np.array(auc_vals)
    p_arr   = np.array(p_vals)
    return {
        "power"      : float(np.mean(p_arr < alpha)),
        "mean_auroc" : float(np.mean(auc_arr)),
        "std_auroc"  : float(np.std(auc_arr)),
        "mean_pvalue": float(np.mean(p_arr)),
        "n_sim"      : n_sim,
        "alpha"      : alpha,
    }


def power_fisher(
    annotations: np.ndarray,
    or_: float,
    noise_level: float,
    k: int,
    n_sim: int,
    alpha: float,
    rng: np.random.Generator,
) -> dict:
    """Estimate Fisher top-K enrichment power by simulation."""
    p_vals, or_vals = [], []
    for _ in range(n_sim):
        scores = generate_enriched_scores(annotations, or_, noise_level, rng)
        or_obs, pv = fisher_topk(annotations, scores, k)
        or_vals.append(or_obs)
        p_vals.append(pv)

    p_arr  = np.array(p_vals)
    or_arr = np.array([v for v in or_vals if not np.isinf(v) and not np.isnan(v)])
    return {
        "power"      : float(np.mean(p_arr < alpha)),
        "k"          : k,
        "mean_or"    : float(np.mean(or_arr)) if len(or_arr) > 0 else float("nan"),
        "n_sim"      : n_sim,
        "alpha"      : alpha,
    }


def run_full_power_simulation(
    n_total: int,
    n_annotated: int,
    or_values: list[float],
    noise_levels: dict[str, float],
    k_values: list[int],
    n_sim: int,
    alpha: float,
    seed: int,
) -> dict:
    """Full power simulation across OR values and noise regimes.

    Parameters
    ----------
    n_total      : total off-connectome pairs (e.g. 1464 for N=61, 20% connectome)
    n_annotated  : pairs with neuropeptide annotation (e.g. 88 for ~6%)
    or_values    : list of OR values to test
    noise_levels : {regime_label: noise_level} dict
    k_values     : K values for Fisher test
    n_sim        : simulations per condition
    alpha        : significance threshold
    seed         : global seed for reproducibility

    Returns
    -------
    Nested dict: results[regime][or_][test] = power dict
    """
    rng_master = np.random.default_rng(seed)

    # Fixed annotation vector (same across all simulations for consistency)
    ann = np.zeros(n_total, dtype=int)
    idx_pep = rng_master.choice(n_total, size=n_annotated, replace=False)
    ann[idx_pep] = 1

    results = {}
    for regime, noise_level in noise_levels.items():
        results[regime] = {}
        for or_ in or_values:
            rng = np.random.default_rng(rng_master.integers(2**31))
            auroc_res = power_auroc(ann, or_, noise_level, n_sim, alpha, rng)
            fisher_res = {}
            for k in k_values:
                rng_k = np.random.default_rng(rng_master.integers(2**31))
                fisher_res[k] = power_fisher(ann, or_, noise_level, k, n_sim, alpha, rng_k)
            results[regime][or_] = {
                "AUROC"     : auroc_res,
                "Fisher"    : fisher_res,
                "theoretical_auroc": theoretical_auroc(or_, noise_level),
            }

    results["_setup"] = {
        "n_total"    : n_total,
        "n_annotated": n_annotated,
        "annotation_fraction": n_annotated / n_total,
        "or_values"  : or_values,
        "k_values"   : k_values,
        "n_sim"      : n_sim,
        "alpha"      : alpha,
    }
    return results
