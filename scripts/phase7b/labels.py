"""
Label generation — Phase 7B Stage 3.

Implements the exact algorithm from phase6b_label_generation_spec.md.

HARD CONSTRAINTS (enforced by design):
  - This module imports only numpy. No dynamics, audit, or simulation imports.
  - generate_labels() takes only A_sparse and SA as inputs.
  - No file I/O, no statistical computation, no data-derived quantities.
"""

import numpy as np
from typing import Optional
from . import config as cfg


def generate_labels(
    A_sparse: np.ndarray,
    SA: frozenset = cfg.SA,
) -> list[dict]:
    """
    Generate ground-truth labels for all 9,900 directed observed-neuron pairs.

    Parameters
    ----------
    A_sparse : (140, 140) float64 ndarray
        The coupling matrix. A[k,j] != 0 means j drives k (j→k convention).
    SA : frozenset of int (0-indexed)
        State-active neuron indices. Must equal cfg.SA by specification.

    Returns
    -------
    list of dicts, one per directed pair (i,j), sorted by (i,j):
        {'i', 'j', 'direct', 'sareachable', 'label', 'witness_h2'}
    """
    records = []
    sa_list = sorted(SA)  # deterministic iteration order

    for i in range(cfg.N_OBS):
        for j in range(cfg.N_OBS):
            if i == j:
                continue

            direct = _compute_direct(A_sparse, i, j)
            sareachable, witness = _compute_sareachable(A_sparse, i, j, sa_list)
            label = _assign_label(direct, sareachable)

            records.append({
                'i':           i,
                'j':           j,
                'direct':      int(direct),
                'sareachable': int(sareachable),
                'label':       label,
                'witness_h2':  witness,  # int or None
            })

    return records


def _compute_direct(A_sparse: np.ndarray, i: int, j: int) -> bool:
    """DIRECT(i→j): A_sparse[j, i] != 0 (neuron i drives neuron j)."""
    return A_sparse[j, i] != 0.0


def _compute_sareachable(
    A_sparse: np.ndarray, i: int, j: int, sa_list: list[int]
) -> tuple[bool, Optional[int]]:
    """
    SAREACHABLE(i→j): exists h in SA with A[h,i]!=0 AND A[j,h]!=0.

    Returns (True, lowest_witness_index) or (False, None).
    Witness is the lowest-index H2 neuron satisfying both conditions.
    """
    for h in sa_list:  # sa_list is sorted ascending → first match is lowest-index
        if A_sparse[h, i] != 0.0 and A_sparse[j, h] != 0.0:
            return True, h
    return False, None


def _assign_label(direct: bool, sareachable: bool) -> str:
    """
    S: direct and not sareachable
    M: direct and sareachable
    C: not direct and sareachable
    N: not direct and not sareachable
    """
    if direct and not sareachable:
        return 'S'
    elif direct and sareachable:
        return 'M'
    elif not direct and sareachable:
        return 'C'
    else:
        return 'N'


def class_counts(records: list[dict]) -> dict[str, int]:
    """Return {label: count} from a label record list."""
    counts = {'S': 0, 'C': 0, 'M': 0, 'N': 0}
    for r in records:
        counts[r['label']] += 1
    return counts
