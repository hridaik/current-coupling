"""Small neuron-label harmonization helpers for Phase 0.

These helpers intentionally implement only convention-level normalization.
They do not resolve biological ambiguities such as AWC ON/OFF versus left/right.
"""

from __future__ import annotations

import re
from collections.abc import Iterable


ZERO_PAD_PREFIXES = ("AS", "DA", "DB", "DD", "VA", "VB", "VC", "VD")
_ZERO_PAD_RE = re.compile(rf"^({'|'.join(ZERO_PAD_PREFIXES)})0+([1-9][0-9]*)$")


def normalize_neuron_label(label: object, *, lr_policy: str = "separate") -> str | None:
    """Normalize a source neuron label to the project's canonical string form.

    The current Phase 0 policy keeps left/right homologs separate. This function
    therefore performs only safe textual normalization and source-convention
    cleanup, such as removing zero padding in numbered ventral-cord neurons.
    """
    if lr_policy != "separate":
        raise ValueError(f"Unsupported LR policy: {lr_policy!r}")
    if label is None:
        return None

    value = str(label).strip().strip('"').strip("'").upper()
    if not value or value in {"NA", "N/A", "NONE", "MISSING", "NAN"}:
        return None

    value = re.sub(r"\s+", "", value)
    match = _ZERO_PAD_RE.match(value)
    if match:
        prefix, number = match.groups()
        return f"{prefix}{int(number)}"
    return value


def normalize_neuron_labels(
    labels: Iterable[object], *, lr_policy: str = "separate"
) -> set[str]:
    """Normalize labels and drop empty/missing values."""
    normalized: set[str] = set()
    for label in labels:
        value = normalize_neuron_label(label, lr_policy=lr_policy)
        if value is not None:
            normalized.add(value)
    return normalized


def is_awc_on_off_label(label: object) -> bool:
    """Return whether a label uses AWC ON/OFF rather than AWC left/right naming."""
    value = normalize_neuron_label(label)
    return value in {"AWCON", "AWCOFF", "AWCOF"}
