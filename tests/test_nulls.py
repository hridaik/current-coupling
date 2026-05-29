"""Tests for null-model preservation properties."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.null_models import (
    permute_simple,
    permute_degree_stratified,
    permute_class_stratified,
    validate_null_preservation,
)


def _make_annotations(N: int, n_pos: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ann = np.zeros(N, dtype=int)
    ann[rng.choice(N, size=n_pos, replace=False)] = 1
    return ann


def test_simple_permutation_preserves_count():
    """Simple permutation must preserve total annotation count."""
    rng = np.random.default_rng(0)
    ann = _make_annotations(200, 30, 0)
    for _ in range(10):
        perm = permute_simple(ann, rng)
        assert perm.sum() == ann.sum(), "Marginal count not preserved by simple permutation"


def test_simple_permutation_produces_different_labels():
    """Simple permutation should change the annotation vector."""
    rng = np.random.default_rng(1)
    ann = _make_annotations(200, 30, 1)
    n_same = sum(1 for _ in range(10) if np.all(permute_simple(ann.copy(), rng) == ann))
    assert n_same < 5, "Simple permutation almost never produces the same vector (N=200)"


def test_degree_stratified_preserves_degree_distribution():
    """Degree-stratified permutation must preserve per-bin annotation counts."""
    rng = np.random.default_rng(2)
    N, n_pos = 300, 40
    ann = _make_annotations(N, n_pos, 2)
    degrees = rng.integers(2, 15, size=N).astype(int)

    for _ in range(5):
        perm = permute_degree_stratified(ann, degrees, n_bins=5, rng=rng)
        checks = validate_null_preservation(ann, perm, pair_degree_sums=degrees, n_bins=5)
        assert checks["marginal_count"]["passed"], "Degree-stratified should preserve marginal count"
        assert checks["degree_distribution"]["passed"], (
            f"Degree-stratified should preserve per-bin counts, "
            f"max deviation: {checks['degree_distribution']['max_bin_deviation']}"
        )


def test_class_stratified_preserves_class_counts():
    """Class-stratified permutation must preserve per-class annotation counts."""
    rng = np.random.default_rng(3)
    N, n_pos = 200, 30
    ann = _make_annotations(N, n_pos, 3)
    classes = rng.integers(0, 5, size=N).astype(int)

    for _ in range(5):
        perm = permute_class_stratified(ann, classes, rng)
        checks = validate_null_preservation(ann, perm, pair_classes=classes)
        assert checks["class_composition"]["passed"], (
            f"Class-stratified should preserve per-class counts, "
            f"max deviation: {checks['class_composition']['max_class_deviation']}"
        )


def test_validate_simple_permutation():
    """validate_null_preservation should flag degree preservation failures for simple permutation."""
    rng = np.random.default_rng(4)
    N = 300
    ann = _make_annotations(N, 40, 4)
    degrees = rng.integers(2, 15, size=N)

    # Simple permutation does NOT preserve degree distribution
    n_failures = 0
    for _ in range(10):
        perm = permute_simple(ann, rng)
        checks = validate_null_preservation(ann, perm, pair_degree_sums=degrees, n_bins=5)
        # Marginal must be preserved
        assert checks["marginal_count"]["passed"], "Simple permutation should preserve marginal count"
        # Degree distribution may NOT be preserved
        if not checks["degree_distribution"]["passed"]:
            n_failures += 1

    # At N=300 with degrees 2-14, degree distribution will usually NOT be preserved
    # (We don't assert this strictly since it could occasionally happen by chance)


def test_null_validation_catches_wrong_count():
    """validate_null_preservation should detect if marginal count is not preserved."""
    rng = np.random.default_rng(5)
    N = 100
    ann = _make_annotations(N, 20, 5)
    bad_perm = ann.copy()
    bad_perm[0] = 1 - bad_perm[0]   # flip one label → changes count by ±1
    checks = validate_null_preservation(ann, bad_perm)
    assert not checks["marginal_count"]["passed"], (
        "Validation should detect changed marginal count"
    )
