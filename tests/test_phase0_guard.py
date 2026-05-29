"""Phase 0 guardrail tests — re-locked state.

Phase 0 methodology lock is complete (PHASE0_METHOD_LOCK_COMPLETE=True)
but real-data precision inference remains blocked (PHASE0_COMPLETE=False)
pending resolution of DEV-003, DEV-004, DEV-005.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from src.estimators import estimate_precision, inverse_covariance


def _load_config():
    spec = importlib.util.spec_from_file_location(
        "phase0_config", Path(__file__).parents[1] / "phase0_config.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_phase0_complete_is_false() -> None:
    """PHASE0_COMPLETE must be False — real-data inference is still prohibited."""
    m = _load_config()
    assert m.PHASE0_COMPLETE is False, (
        "PHASE0_COMPLETE must be False: real-data precision remains blocked "
        "until DEV-003/DEV-004/DEV-005 are resolved and human authorizes inference."
    )


def test_phase0_method_lock_complete_is_true() -> None:
    """PHASE0_METHOD_LOCK_COMPLETE must be True — methodology is frozen."""
    m = _load_config()
    assert getattr(m, "PHASE0_METHOD_LOCK_COMPLETE", None) is True, (
        "PHASE0_METHOD_LOCK_COMPLETE must be True: scientific methodology "
        "and synthetic validation are complete and frozen."
    )


def test_real_data_precision_estimation_is_blocked() -> None:
    """Real-data precision must raise RuntimeError while PHASE0_COMPLETE is False."""
    covariance = np.eye(3)
    neuron_list = ["AVAL", "AVAR", "RIML"]
    with pytest.raises(RuntimeError, match="PHASE0_COMPLETE"):
        estimate_precision(
            covariance,
            data_kind="real",
            neuron_list=neuron_list,
        )


def test_synthetic_precision_estimation_allowed() -> None:
    """Synthetic precision estimation must still work regardless of PHASE0_COMPLETE."""
    covariance = np.eye(3)
    neuron_list = ["AVAL", "AVAR", "RIML"]
    precision = inverse_covariance(
        covariance,
        data_kind="synthetic",
        neuron_list=neuron_list,
    )
    np.testing.assert_allclose(precision, np.eye(3))
