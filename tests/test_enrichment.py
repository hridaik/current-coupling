"""Tests for enrichment statistics — synthetic data only."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.enrichment import (
    auroc,
    auroc_pvalue,
    fisher_topk,
    generate_enriched_scores,
    power_auroc,
    theoretical_auroc,
)


def test_auroc_random_annotations_near_half():
    """AUROC should be ~0.5 when there is no signal (OR=1)."""
    rng = np.random.default_rng(0)
    N = 200
    ann = np.zeros(N, dtype=int)
    ann[:20] = 1
    scores = rng.standard_normal(N)   # pure noise
    auc = auroc(ann, scores)
    assert 0.3 < auc < 0.7, f"Expected AUROC≈0.5 under H0, got {auc:.3f}"


def test_auroc_high_for_strong_signal():
    """AUROC should be clearly > 0.5 when annotated pairs have high scores."""
    rng = np.random.default_rng(1)
    N = 200
    ann = np.zeros(N, dtype=int)
    ann[:20] = 1
    scores = generate_enriched_scores(ann, or_=5.0, noise_level=0.5, rng=rng)
    auc = auroc(ann, scores)
    assert auc > 0.65, f"Expected AUROC > 0.65 at OR=5, got {auc:.3f}"


def test_auroc_pvalue_significant_at_strong_signal():
    """p-value should be < 0.05 at strong enrichment."""
    rng = np.random.default_rng(2)
    N = 300
    ann = np.zeros(N, dtype=int)
    ann[:30] = 1
    scores = generate_enriched_scores(ann, or_=5.0, noise_level=0.5, rng=rng)
    _, p = auroc_pvalue(ann, scores)
    assert p < 0.05, f"Expected p < 0.05 at strong enrichment, got {p:.4f}"


def test_auroc_pvalue_not_significant_under_null():
    """p-value should be large on average under H0 (OR=1)."""
    rng = np.random.default_rng(3)
    N = 300
    ann = np.zeros(N, dtype=int)
    ann[:30] = 1
    # Run 20 trials under H0, count fraction with p < 0.05 (should be ~0.05)
    significant = 0
    for _ in range(20):
        scores = rng.standard_normal(N)
        _, p = auroc_pvalue(ann, scores)
        if p < 0.05:
            significant += 1
    # False positive rate should be ≤ 0.25 (allowing for variance with only 20 trials)
    assert significant <= 5, f"Too many false positives under H0: {significant}/20"


def test_fisher_topk_zero_effect_not_significant():
    """Fisher top-K should not be significant under H0 for most trials."""
    rng = np.random.default_rng(4)
    N = 300
    ann = np.zeros(N, dtype=int)
    ann[:30] = 1
    significant = 0
    for _ in range(20):
        scores = rng.standard_normal(N)
        _, p = fisher_topk(ann, scores, k=30)
        if p < 0.05:
            significant += 1
    assert significant <= 5, f"Too many Fisher false positives under H0: {significant}/20"


def test_fisher_topk_strong_effect_significant():
    """Fisher top-K should be significant with concentrated strong enrichment."""
    rng = np.random.default_rng(5)
    N = 300
    ann = np.zeros(N, dtype=int)
    ann[:30] = 1
    scores = generate_enriched_scores(ann, or_=10.0, noise_level=0.5, rng=rng)
    _, p = fisher_topk(ann, scores, k=30)
    assert p < 0.05, f"Expected Fisher p < 0.05 at strong enrichment, got {p:.4f}"


def test_theoretical_auroc_matches_simulation():
    """Theoretical AUROC approximation should be close to simulated mean AUROC."""
    rng = np.random.default_rng(6)
    N = 500
    ann = np.zeros(N, dtype=int)
    ann[:50] = 1
    or_, noise = 3.0, 1.0
    theory = theoretical_auroc(or_, noise)
    simulated = np.mean([
        auroc(ann, generate_enriched_scores(ann, or_, noise, rng))
        for _ in range(50)
    ])
    assert abs(theory - simulated) < 0.10, (
        f"Theory AUROC {theory:.3f} vs simulated {simulated:.3f}: "
        f"difference {abs(theory-simulated):.3f} > 0.10"
    )


def test_power_auroc_increases_with_or():
    """AUROC power should increase as OR increases."""
    rng = np.random.default_rng(7)
    N, n_ann = 400, 40
    ann = np.zeros(N, dtype=int); ann[:n_ann] = 1
    powers = []
    for or_ in [1.0, 2.0, 4.0]:
        res = power_auroc(ann, or_, 1.0, n_sim=50, alpha=0.05, rng=rng)
        powers.append(res["power"])
    assert powers[0] <= powers[1] <= powers[2] + 0.1, (
        f"Power should increase with OR: {powers}"
    )


def test_power_enrichment_at_or2():
    """ENRICHMENT_POWER_AT_OR2 should be ≥ 0.6 at sufficient support (per task.md)."""
    rng = np.random.default_rng(8)
    # Non-roaming regime: N=1464 pairs, n_annotated=88, noise_level=0.5
    N, n_ann = 1464, 88
    ann = np.zeros(N, dtype=int)
    ann[:n_ann] = 1
    res = power_auroc(ann, or_=2.0, noise_level=0.5, n_sim=100, alpha=0.05, rng=rng)
    assert res["power"] >= 0.6, (
        f"ENRICHMENT_POWER_AT_OR2 should be ≥ 0.6 at non-roaming support, "
        f"got {res['power']:.2f}"
    )
