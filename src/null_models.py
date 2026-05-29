"""Null-model generation and validation for Phase 0 enrichment tests.

Null models permute the neuropeptide annotation labels while preserving
specified graph-structural properties (degree, class, proximity).

Per task.md Stage 9:
  Primary null: degree-, class-, proximity-, and neuropeptide-degree-aware
  permutation restricted to the common identified-neuron subgraph.

All functions operate on SYNTHETIC labels during Phase 0.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Core null-model functions
# ---------------------------------------------------------------------------

def permute_simple(
    annotations: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Simple random permutation of annotation labels.

    Preserves the marginal count of annotated pairs (n_annotated) but
    not any structural properties. Fastest null; baseline for comparison.

    Parameters
    ----------
    annotations : (N,) binary array — original labels
    rng         : random generator

    Returns
    -------
    (N,) binary array — permuted labels with same sum
    """
    result = annotations.copy()
    rng.shuffle(result)
    return result


def permute_degree_stratified(
    annotations: np.ndarray,
    pair_degree_sums: np.ndarray,
    n_bins: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Degree-stratified permutation: shuffles annotations within degree bins.

    Preserves the degree distribution of annotated vs non-annotated pairs.
    For each pair (i,j), pair_degree_sum = degree(i) + degree(j) in A_raw.

    Parameters
    ----------
    annotations       : (N,) binary — original labels
    pair_degree_sums  : (N,) int — degree_i + degree_j for each pair
    n_bins            : number of degree bins to use
    rng               : random generator

    Returns
    -------
    (N,) binary array — permuted labels preserving degree distribution
    """
    result = annotations.copy()
    bin_edges = np.percentile(pair_degree_sums, np.linspace(0, 100, n_bins + 1))
    bin_edges = np.unique(bin_edges)   # remove duplicate edges for degenerate data
    bin_idx   = np.digitize(pair_degree_sums, bin_edges[1:], right=True)

    for b in np.unique(bin_idx):
        mask = bin_idx == b
        sub  = result[mask]
        rng.shuffle(sub)
        result[mask] = sub

    return result


def permute_class_stratified(
    annotations: np.ndarray,
    pair_classes: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Class-stratified permutation: shuffles annotations within pair-class groups.

    pair_classes encodes the class combination of a pair (e.g., hash of the
    two node classes). Shuffling within groups preserves the class-composition
    of the annotated pair set.

    Parameters
    ----------
    annotations  : (N,) binary — original labels
    pair_classes : (N,) int — class label per pair (e.g. class_i × 10 + class_j)
    rng          : random generator

    Returns
    -------
    (N,) binary permuted labels
    """
    result = annotations.copy()
    for cls in np.unique(pair_classes):
        mask = pair_classes == cls
        sub  = result[mask]
        rng.shuffle(sub)
        result[mask] = sub
    return result


# ---------------------------------------------------------------------------
# Null-model validation
# ---------------------------------------------------------------------------

def validate_null_preservation(
    original: np.ndarray,
    permuted: np.ndarray,
    pair_degree_sums: np.ndarray | None = None,
    pair_classes: np.ndarray | None = None,
    n_bins: int = 5,
) -> dict:
    """Check that a permuted annotation vector preserves desired properties.

    Checks:
    1. Marginal count (total n_annotated preserved)
    2. Degree distribution of annotated pairs (if pair_degree_sums provided)
    3. Class composition of annotated pairs (if pair_classes provided)

    Parameters
    ----------
    original          : (N,) original binary annotation vector
    permuted          : (N,) permuted binary annotation vector
    pair_degree_sums  : (N,) optional degree sums for degree check
    pair_classes      : (N,) optional class labels for class check
    n_bins            : number of degree bins for degree check

    Returns
    -------
    dict with check names as keys and (observed, expected, passed) tuples as values
    """
    checks = {}

    # 1. Marginal count
    n_orig = int(original.sum())
    n_perm = int(permuted.sum())
    checks["marginal_count"] = {
        "original": n_orig, "permuted": n_perm,
        "passed": n_orig == n_perm,
    }

    # 2. Degree distribution
    if pair_degree_sums is not None:
        bin_edges = np.percentile(pair_degree_sums, np.linspace(0, 100, n_bins + 1))
        bin_edges = np.unique(bin_edges)
        bin_idx   = np.digitize(pair_degree_sums, bin_edges[1:], right=True)
        bin_counts_orig = np.array([
            int((original.astype(bool) & (bin_idx == b)).sum())
            for b in np.unique(bin_idx)
        ])
        bin_counts_perm = np.array([
            int((permuted.astype(bool) & (bin_idx == b)).sum())
            for b in np.unique(bin_idx)
        ])
        max_dev = int(np.max(np.abs(bin_counts_orig - bin_counts_perm)))
        checks["degree_distribution"] = {
            "bin_counts_original": bin_counts_orig.tolist(),
            "bin_counts_permuted": bin_counts_perm.tolist(),
            "max_bin_deviation": max_dev,
            "passed": max_dev == 0,   # strict: exact per-bin preservation
        }

    # 3. Class composition
    if pair_classes is not None:
        unique_classes = np.unique(pair_classes)
        class_counts_orig = np.array([
            int((original.astype(bool) & (pair_classes == c)).sum())
            for c in unique_classes
        ])
        class_counts_perm = np.array([
            int((permuted.astype(bool) & (pair_classes == c)).sum())
            for c in unique_classes
        ])
        max_dev_cls = int(np.max(np.abs(class_counts_orig - class_counts_perm)))
        checks["class_composition"] = {
            "class_counts_original": class_counts_orig.tolist(),
            "class_counts_permuted": class_counts_perm.tolist(),
            "max_class_deviation": max_dev_cls,
            "passed": max_dev_cls == 0,
        }

    checks["all_passed"] = all(v["passed"] for v in checks.values() if isinstance(v, dict))
    return checks


def estimate_null_distribution(
    annotations: np.ndarray,
    scores: np.ndarray,
    null_fn,
    stat_fn,
    n_perm: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate null distribution of a statistic by permuting annotation labels.

    Parameters
    ----------
    annotations : (N,) binary — original annotation labels
    scores      : (N,) float — fixed |ΔQ| scores
    null_fn     : callable(annotations, rng) → permuted_annotations
    stat_fn     : callable(annotations, scores) → float statistic
    n_perm      : number of permutations
    rng         : random generator

    Returns
    -------
    (n_perm,) null distribution of the statistic
    """
    null_stats = np.zeros(n_perm)
    for i in range(n_perm):
        perm_ann = null_fn(annotations, rng)
        null_stats[i] = stat_fn(perm_ann, scores)
    return null_stats


def permutation_pvalue(
    observed_stat: float,
    null_stats: np.ndarray,
    alternative: str = "greater",
) -> float:
    """Compute empirical p-value from null distribution.

    Parameters
    ----------
    observed_stat : the observed test statistic
    null_stats    : (n_perm,) null distribution
    alternative   : "greater", "less", or "two-sided"

    Returns
    -------
    empirical p-value
    """
    n = len(null_stats)
    if alternative == "greater":
        return float((null_stats >= observed_stat).sum() / n)
    elif alternative == "less":
        return float((null_stats <= observed_stat).sum() / n)
    else:
        extreme = np.abs(null_stats - np.mean(null_stats)) >= abs(observed_stat - np.mean(null_stats))
        return float(extreme.sum() / n)


def compare_null_calibration(
    annotations: np.ndarray,
    or_range: list[float],
    noise_level: float,
    n_perm: int,
    n_trials: int,
    seed: int,
) -> dict:
    """Compare simple vs degree-stratified null p-value calibration under H0 (OR=1).

    Under H0 (no enrichment, OR=1), both nulls should give uniform p-values.
    Under H1 (OR>1), both should have power > 0.

    Returns calibration results for reporting.
    """
    from src.enrichment import generate_enriched_scores, auroc

    rng = np.random.default_rng(seed)
    N   = len(annotations)

    # Synthetic degree sums (random but fixed)
    degree_sums_fake = rng.integers(2, 20, size=N).astype(int)

    results = {}
    for or_ in or_range:
        pvals_simple = []
        pvals_degree = []
        for _ in range(n_trials):
            rng_t = np.random.default_rng(rng.integers(2**31))
            scores = generate_enriched_scores(annotations, or_, noise_level, rng_t)
            obs    = auroc(annotations, scores)

            # Simple null
            null_s = estimate_null_distribution(
                annotations, scores,
                null_fn=lambda a, r: permute_simple(a, r),
                stat_fn=lambda a, s: auroc(a, s),
                n_perm=n_perm, rng=rng_t,
            )
            p_simple = permutation_pvalue(obs, null_s, "greater")

            # Degree-stratified null
            null_d = estimate_null_distribution(
                annotations, scores,
                null_fn=lambda a, r: permute_degree_stratified(a, degree_sums_fake, 5, r),
                stat_fn=lambda a, s: auroc(a, s),
                n_perm=n_perm, rng=rng_t,
            )
            p_degree = permutation_pvalue(obs, null_d, "greater")

            pvals_simple.append(p_simple)
            pvals_degree.append(p_degree)

        results[or_] = {
            "power_simple": float(np.mean(np.array(pvals_simple) < 0.05)),
            "power_degree": float(np.mean(np.array(pvals_degree) < 0.05)),
        }
    return results
