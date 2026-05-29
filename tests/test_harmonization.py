import importlib.util
from pathlib import Path

import pytest

from src.harmonization import (
    is_awc_on_off_label,
    normalize_neuron_label,
    normalize_neuron_labels,
)


def _load_config():
    config_path = Path(__file__).resolve().parents[1] / "phase0_config.py"
    spec = importlib.util.spec_from_file_location("phase0_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_zero_padded_ventral_cord_labels() -> None:
    assert normalize_neuron_label("VA01") == "VA1"
    assert normalize_neuron_label("DB07") == "DB7"
    assert normalize_neuron_label("AS10") == "AS10"


def test_lr_policy_separate_does_not_collapse_homologs() -> None:
    assert normalize_neuron_labels(["AVAL", "AVAR"]) == {"AVAL", "AVAR"}


def test_awc_on_off_is_flagged_not_silently_mapped() -> None:
    assert is_awc_on_off_label("AWCON")
    assert is_awc_on_off_label("AWCOFF")
    assert normalize_neuron_label("AWCON") == "AWCON"


def test_unsupported_lr_policy_raises() -> None:
    with pytest.raises(ValueError):
        normalize_neuron_label("AVAL", lr_policy="collapsed")


def test_coverage_fraction_in_config() -> None:
    """COVERAGE_FRACTION must be in phase0_config.py, not hardcoded in scripts."""
    config = _load_config()
    assert hasattr(config, "COVERAGE_FRACTION"), "COVERAGE_FRACTION missing from phase0_config.py"
    assert config.COVERAGE_FRACTION == 0.80


def test_awc_anatomical_labels_not_mapped_to_functional() -> None:
    """AWCL and AWCR must not be treated as AWC ON/OFF labels."""
    assert not is_awc_on_off_label("AWCL")
    assert not is_awc_on_off_label("AWCR")
    assert normalize_neuron_label("AWCL") == "AWCL"
    assert normalize_neuron_label("AWCR") == "AWCR"


def test_behavioral_threshold_config() -> None:
    """Verify BEHAV_THRESHOLD and related fields set after Stage 5 human decision.

    Threshold approved 2026-05-28 from pooled velocity_s KDE trough.
    Must NOT be None (it has been set) and must equal the approved value.
    Must NOT have been derived from neural output (enforcement is procedural,
    not testable here, but we verify the value matches the approved decision).
    """
    config = _load_config()

    assert config.BEHAVIOR_SCORE_SOURCE == "velocity_s"

    assert config.BEHAV_THRESHOLD == 0.284, (
        f"BEHAV_THRESHOLD must be 0.284 (pooled KDE trough), got {config.BEHAV_THRESHOLD}"
    )
    assert config.BEHAV_THRESHOLD_RULE == (
        "pooled_velocity_s_kde_trough_between_dwelling_and_roaming"
    )

    # MIN_BOUT_SECONDS intentionally not set yet
    assert config.MIN_BOUT_SECONDS is None, (
        "MIN_BOUT_SECONDS must remain None until bout-distribution review"
    )

    # W_TRANS_SECONDS must not be changed without a checkpoint
    assert config.W_TRANS_SECONDS == 30.0


def test_creamer_rc_numerical_feasibility_config() -> None:
    """Verify Creamer LDS and RC config fields set after Stage 4 numerical audit."""
    config = _load_config()

    # Creamer structural fields
    assert config.CREAMER_TIME_CONVENTION == "discrete_time"
    assert config.CREAMER_DT == 0.5
    assert 0.99 < config.CREAMER_MAX_EIGENVALUE < 1.0, \
        "A_C must be discrete-time stable with max |eig| close to but below 1"
    assert config.CREAMER_STABLE is True
    assert config.CREAMER_DC_AVAILABLE is True
    assert config.CREAMER_LABEL_CONVENTION == "neuropal_str"
    assert config.CREAMER_SIGMA_POSDEF is True
    assert config.CREAMER_OMEGA_NORM > 0, "Omega_C Frobenius norm must be positive"

    # Creamer subgraph
    assert config.N_CREAMER_SUBGRAPH_NEURONS == 56, \
        "56 of 61 common neurons have Creamer representations; 5 absent (not imputed)"
    # Three-space consistency
    assert config.N_COMMON_NEURONS == 61
    assert config.N_RANDI_SUBGRAPH_NEURONS == 60
    assert config.N_CREAMER_SUBGRAPH_NEURONS == 56

    # RC role fields
    assert config.RC_ROLE_JACOBIAN == "not_viable"
    assert config.RC_ROLE_DRIVE_SWEEP == "not_viable"
    assert config.RC_ROLE_SAMPLING == "behavioral_eigenworm_only"
    assert config.RC_OUTPUT_NEURON_COORDS is False
    assert config.RC_OUTPUT_JACOBIAN_AVAILABLE is False
    assert config.RC_STATE_CONDITIONED is False
    assert config.RC_NEURON_COVERAGE == 0


def test_phase0_midproject_config_integrity() -> None:
    """Verify all approved mid-project config values are still intact.

    Guards against accidental regression of approved values during
    later-stage work.
    """
    config = _load_config()

    # Harmonization policy
    assert config.LR_POLICY == "separate"
    assert config.IDENTITY_CONFIDENCE_THRESHOLD == 2.5
    assert config.COVERAGE_FRACTION == 0.80

    # Subgraph counts
    assert config.N_COMMON_NEURONS == 61
    assert config.N_RANDI_SUBGRAPH_NEURONS == 60
    assert config.N_RANDI_SUBGRAPH_PAIRS == 189

    # Randi pair-filtering policy
    assert config.RANDI_WT_Q_THRESHOLD == 0.05
    assert config.RANDI_AMPLITUDE_GATE_DFF is None

    # SUBGRAPH_ADEQUATE intentionally still None — human decision pending
    assert config.SUBGRAPH_ADEQUATE is None, (
        "SUBGRAPH_ADEQUATE was set without a recorded human decision checkpoint."
    )

    # Phase 0 must not be marked complete prematurely
    assert config.PHASE0_COMPLETE is False

    # Creamer D-type approved
    assert config.CREAMER_D_TYPE == (
        "discrete_time_dynamics_cov_process_noise_covariance_diag_in_paper_not_continuous_D"
    )

    # Data paths all set
    for field in ("DATA_ROOT", "ATANAS_PATH", "CREAMER_PATH",
                  "CONNECTOME_PATH", "RANDI_PATH", "NEUROPEPTIDE_PATH"):
        assert getattr(config, field) is not None, f"{field} should be set"


def test_randi_pair_filtering_policy_in_config() -> None:
    """Randi pair-filtering Rule A fields must be present and correct.

    Primary rule: q_wt < RANDI_WT_Q_THRESHOLD AND occ1_wt > 0 AND occ1_u31 > 0.
    Amplitude gate must be explicitly excluded (None) from the primary rule.
    N_RANDI_SUBGRAPH_PAIRS must equal 189 (Rule A count, approved 2026-05-28).
    """
    config = _load_config()

    assert hasattr(config, "RANDI_WT_Q_THRESHOLD"), \
        "RANDI_WT_Q_THRESHOLD missing from phase0_config.py"
    assert config.RANDI_WT_Q_THRESHOLD == 0.05, \
        f"Expected 0.05, got {config.RANDI_WT_Q_THRESHOLD}"

    assert hasattr(config, "RANDI_AMPLITUDE_GATE_DFF"), \
        "RANDI_AMPLITUDE_GATE_DFF missing from phase0_config.py"
    assert config.RANDI_AMPLITUDE_GATE_DFF is None, (
        "RANDI_AMPLITUDE_GATE_DFF must be None — amplitude gate is intentionally "
        "excluded from the primary pair definition (Rule A)."
    )

    assert hasattr(config, "N_RANDI_SUBGRAPH_PAIRS"), \
        "N_RANDI_SUBGRAPH_PAIRS missing from phase0_config.py"
    assert config.N_RANDI_SUBGRAPH_PAIRS == 189, \
        f"Expected 189 (Rule A, approved 2026-05-28), got {config.N_RANDI_SUBGRAPH_PAIRS}"
