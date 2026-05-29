"""Stage 02 label-only subgraph feasibility under locked threshold.

This script decodes only NeuroPAL label/confidence metadata from the Atanas
JLD2 label artifact and small approved label tables from ConnectomeToolbox and
wormneuroatlas. It does not import external repository packages, execute
notebooks, load neural activity arrays, load behavioral time series, or compute
any covariance/precision/DeltaQ-like quantity.
"""

from __future__ import annotations

import csv
import datetime as _dt
import importlib.util
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FEASIBILITY_REPORT_PATH = ROOT / "results" / "diagnostics" / "stage02_subgraph_feasibility.md"
ATANAS_DECODE_REPORT_PATH = ROOT / "results" / "diagnostics" / "stage02_atanas_label_decode.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.harmonization import is_awc_on_off_label, normalize_neuron_label, normalize_neuron_labels


class DecodeAmbiguity(RuntimeError):
    """Raised when h5py cannot identify label/confidence semantics safely."""


@dataclass(frozen=True)
class AtanasRecordLabels:
    record_id: str
    decoded_labels: tuple[dict[str, Any], ...]
    label_child_shapes: tuple[tuple[int, ...], ...]

    def confident_labels(self, *, threshold: float, lr_policy: str) -> set[str]:
        labels: set[str] = set()
        for item in self.decoded_labels:
            label = item.get("label")
            confidence = item.get("confidence")
            if not isinstance(label, str):
                continue
            if not isinstance(confidence, (int, float)):
                continue
            if confidence < threshold:
                continue
            if "alt" in label.lower():
                continue
            normalized = normalize_neuron_label(label, lr_policy=lr_policy)
            if normalized is not None:
                labels.add(normalized)
        return labels

    def ambiguous_confident_labels(self, *, threshold: float) -> set[str]:
        values: set[str] = set()
        for item in self.decoded_labels:
            label = item.get("label")
            confidence = item.get("confidence")
            if (
                isinstance(label, str)
                and isinstance(confidence, (int, float))
                and confidence >= threshold
                and ("?" in label or "alt" in label.lower())
            ):
                values.add(label)
        return values


def load_config():
    config_path = ROOT / "phase0_config.py"
    spec = importlib.util.spec_from_file_location("phase0_config", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {config_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_atanas_reference_labels(path: Path, lr_policy: str) -> set[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return normalize_neuron_labels((row.get("neuron") for row in reader), lr_policy=lr_policy)


def read_individual_neurons(path: Path, lr_policy: str) -> set[str]:
    labels: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            labels.append(stripped.split(";", 1)[0])
    return normalize_neuron_labels(labels, lr_policy=lr_policy)


def read_all_cell_info_labels(path: Path, lr_policy: str) -> set[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return normalize_neuron_labels((row.get("Cell name") for row in reader), lr_policy=lr_policy)


def read_randi_neuron_ids(path: Path, lr_policy: str) -> set[str]:
    labels: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.strip().split()
            if len(parts) >= 2:
                labels.append(parts[1])
    return normalize_neuron_labels(labels, lr_policy=lr_policy)


def read_randi_head_ids(path: Path, lr_policy: str) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    head_groups = data.get("head", [])
    labels: list[str] = []
    for group in head_groups:
        values = data.get(group, [])
        if isinstance(values, list):
            labels.extend(str(value) for value in values)
    return normalize_neuron_labels(labels, lr_policy=lr_policy)


def read_csv_header_labels(path: Path, lr_policy: str) -> set[str]:
    """Read only the header row from an adjacency-like CSV."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
    return normalize_neuron_labels(header[1:], lr_policy=lr_policy)


def decode_scalar(value: object) -> object:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.bytes_):
        return bytes(value).decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    return value


def h5_class(dataset: h5py.Dataset) -> int:
    return dataset.id.get_type().get_class()


def scalar_value(dataset: h5py.Dataset) -> object:
    """Read small scalar/string/numeric label metadata only."""
    cls = h5_class(dataset)
    if dataset.shape == () and cls in {h5py.h5t.STRING, h5py.h5t.INTEGER, h5py.h5t.FLOAT}:
        return decode_scalar(dataset[()])
    if dataset.shape is not None and dataset.size <= 16 and cls in {h5py.h5t.INTEGER, h5py.h5t.FLOAT}:
        return [decode_scalar(value) for value in dataset[...].flat]
    if dataset.shape is None:
        return None
    raise DecodeAmbiguity(
        f"Unsupported scalar metadata dataset shape={dataset.shape}, dtype={dataset.dtype}"
    )


def object_refs(value: object) -> list[h5py.Reference]:
    refs: list[h5py.Reference] = []
    if isinstance(value, h5py.Reference) and bool(value):
        refs.append(value)
    elif isinstance(value, np.ndarray):
        if value.dtype == object:
            refs.extend(item for item in value.flat if isinstance(item, h5py.Reference) and bool(item))
        elif value.dtype.fields:
            for item in value.flat:
                refs.extend(object_refs(item))
    elif isinstance(value, np.void) and value.dtype.fields:
        for field in value.dtype.names or ():
            refs.extend(object_refs(value[field]))
    return refs


def refs_from_dataset(dataset: h5py.Dataset, *, limit: int = 1000) -> list[h5py.Reference]:
    if not isinstance(dataset, h5py.Dataset):
        raise DecodeAmbiguity("Expected HDF5 dataset while reading object references")
    if dataset.size is None or dataset.size > limit:
        raise DecodeAmbiguity(
            f"Reference dataset exceeds label-metadata traversal limit: shape={dataset.shape}"
        )
    cls = h5_class(dataset)
    if cls not in {h5py.h5t.REFERENCE, h5py.h5t.COMPOUND}:
        raise DecodeAmbiguity(f"Expected REFERENCE/COMPOUND dataset, got dtype={dataset.dtype}")
    value = dataset[()] if dataset.shape == () else dataset[...]
    return object_refs(value)


def pair_parts(h5: h5py.File, dataset: h5py.Dataset) -> tuple[object, h5py.Dataset | None]:
    if dataset.shape != () or dataset.dtype.names is None:
        raise DecodeAmbiguity(f"Expected scalar pair-like compound, got shape={dataset.shape}")
    value = dataset[()]
    names = dataset.dtype.names
    if names != ("first", "second") and names != ("1", "2"):
        raise DecodeAmbiguity(f"Unexpected pair field names: {names}")
    raw_key = value[names[0]]
    raw_value = value[names[1]]
    if isinstance(raw_key, h5py.Reference) and bool(raw_key):
        key_obj = h5[raw_key]
        if not isinstance(key_obj, h5py.Dataset):
            raise DecodeAmbiguity("Pair key reference did not point to a dataset")
        key = scalar_value(key_obj)
    else:
        key = decode_scalar(raw_key)
    value_obj = h5[raw_value] if isinstance(raw_value, h5py.Reference) and bool(raw_value) else None
    return key, value_obj


def decode_label_dict(h5: h5py.File, vector_dataset: h5py.Dataset) -> dict[str, object]:
    if vector_dataset.shape is None or len(vector_dataset.shape) != 1:
        raise DecodeAmbiguity("Expected one-dimensional label dictionary vector")
    result: dict[str, object] = {}
    for pair_ref in refs_from_dataset(vector_dataset):
        pair_obj = h5[pair_ref]
        if not isinstance(pair_obj, h5py.Dataset):
            raise DecodeAmbiguity("Label field reference did not point to a dataset")
        key, value_obj = pair_parts(h5, pair_obj)
        if not isinstance(key, str):
            raise DecodeAmbiguity(f"Label field key is not a string: {key!r}")
        if not isinstance(value_obj, h5py.Dataset):
            result[key] = None
            continue
        result[key] = scalar_value(value_obj)
    required = {"label", "confidence"}
    if not required.issubset(result):
        raise DecodeAmbiguity(f"Label dictionary missing required keys: {sorted(required - set(result))}")
    if not isinstance(result.get("label"), str):
        raise DecodeAmbiguity("Decoded label value is not a string")
    if not isinstance(result.get("confidence"), (int, float)):
        raise DecodeAmbiguity("Decoded confidence value is not numeric")
    return result


def decode_label_child(h5: h5py.File, child: h5py.Dataset) -> tuple[dict[str, object], ...] | None:
    """Decode a child if it is the string-keyed neuron-label dictionary."""
    labels: list[dict[str, object]] = []
    top_keys: list[object] = []
    try:
        top_refs = refs_from_dataset(child)
        for class_ref in top_refs:
            class_pair = h5[class_ref]
            if not isinstance(class_pair, h5py.Dataset):
                return None
            class_key, label_vector = pair_parts(h5, class_pair)
            top_keys.append(class_key)
            if not isinstance(class_key, str):
                return None
            if not isinstance(label_vector, h5py.Dataset):
                return None
            for label_ref in refs_from_dataset(label_vector):
                label_obj = h5[label_ref]
                if not isinstance(label_obj, h5py.Dataset):
                    return None
                labels.append(decode_label_dict(h5, label_obj))
    except DecodeAmbiguity:
        return None
    if not top_keys or not labels:
        return None
    return tuple(labels)


def decode_atanas_jld2(path: Path) -> tuple[AtanasRecordLabels, ...]:
    """Decode only record IDs and NeuroPAL label/confidence metadata."""
    records: list[AtanasRecordLabels] = []
    with h5py.File(path, "r") as h5:
        if "dict_neuropal_label" not in h5:
            raise DecodeAmbiguity("Missing top-level dict_neuropal_label key")
        root = h5["dict_neuropal_label"]
        if not isinstance(root, h5py.Dataset) or root.shape != ():
            raise DecodeAmbiguity("dict_neuropal_label is not a scalar object-reference dataset")
        root_refs = refs_from_dataset(root, limit=1)
        if len(root_refs) != 1:
            raise DecodeAmbiguity("dict_neuropal_label did not contain exactly one object reference")
        record_vector = h5[root_refs[0]]
        if not isinstance(record_vector, h5py.Dataset) or record_vector.shape is None:
            raise DecodeAmbiguity("dict_neuropal_label target is not a dataset vector")
        for entry_ref in refs_from_dataset(record_vector):
            entry_obj = h5[entry_ref]
            if not isinstance(entry_obj, h5py.Dataset):
                raise DecodeAmbiguity("Record entry reference did not point to a dataset")
            record_id, value_obj = pair_parts(h5, entry_obj)
            if not isinstance(record_id, str):
                raise DecodeAmbiguity(f"Record key is not a string: {record_id!r}")
            if not isinstance(value_obj, h5py.Dataset):
                raise DecodeAmbiguity(f"Record {record_id} does not point to a value tuple")
            value_children = [h5[ref] for ref in refs_from_dataset(value_obj)]
            label_candidates: list[tuple[dict[str, object], ...]] = []
            child_shapes: list[tuple[int, ...]] = []
            for child in value_children:
                if not isinstance(child, h5py.Dataset) or child.shape is None:
                    continue
                child_shapes.append(tuple(int(dim) for dim in child.shape))
                decoded = decode_label_child(h5, child)
                if decoded is not None:
                    label_candidates.append(decoded)
            if len(label_candidates) != 1:
                raise DecodeAmbiguity(
                    f"Record {record_id} had {len(label_candidates)} label-like children; expected exactly 1"
                )
            records.append(
                AtanasRecordLabels(
                    record_id=record_id,
                    decoded_labels=label_candidates[0],
                    label_child_shapes=tuple(child_shapes),
                )
            )
    if not records:
        raise DecodeAmbiguity("No records decoded from dict_neuropal_label")
    return tuple(records)


def label_count_table(records: tuple[AtanasRecordLabels, ...], *, threshold: float, lr_policy: str) -> Counter[str]:
    coverage: Counter[str] = Counter()
    for record in records:
        coverage.update(record.confident_labels(threshold=threshold, lr_policy=lr_policy))
    return coverage


def sample_labels(labels: set[str] | list[str] | tuple[str, ...], limit: int = 40) -> str:
    values = sorted(labels)
    shown = ", ".join(values[:limit])
    if len(values) > limit:
        shown += f", ... ({len(values) - limit} more)"
    return shown or "none"


def bullet(items: list[str]) -> str:
    if not items:
        return "- none\n"
    return "".join(f"- `{item}`\n" for item in items)


def write_phase0_n_common(value: int) -> None:
    config_path = ROOT / "phase0_config.py"
    text = config_path.read_text(encoding="utf-8")
    updated, count = re.subn(r"^N_COMMON_NEURONS = .*$", f"N_COMMON_NEURONS = {value}", text, count=1, flags=re.M)
    if count != 1:
        raise RuntimeError("Could not update N_COMMON_NEURONS in phase0_config.py")
    if updated != text:
        config_path.write_text(updated, encoding="utf-8")


def write_reports(
    *,
    threshold: float,
    lr_policy: str,
    loaded_files: list[str],
    records: tuple[AtanasRecordLabels, ...],
    coverage_required_records: int,
    atanas_high_coverage: set[str],
    connectome_labels: set[str],
    randi_all: set[str],
    randi_head: set[str],
    ripoll_labels: set[str],
    common_all_randi: set[str],
    common_head_randi: set[str],
    awc_on_off_labels: set[str],
) -> None:
    today = _dt.date.today().isoformat()
    head_not_all = common_head_randi - common_all_randi
    all_not_head = common_all_randi - common_head_randi
    record_counts = [len(record.decoded_labels) for record in records]
    confident_counts = [
        len(record.confident_labels(threshold=threshold, lr_policy=lr_policy)) for record in records
    ]
    ambiguous_confident = sorted(
        {
            label
            for record in records
            for label in record.ambiguous_confident_labels(threshold=threshold)
        }
    )
    decode_report = f"""# Stage 2 Atanas Label Decode

Date: {today}

## Scope

Label-only h5py decoding feasibility step for:

`data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`

No neural activity arrays, behavioral time series, model arrays, covariance-like
matrices, connectome adjacency matrices, full functional matrices, full
neuropeptide matrices, covariance, precision, inverse covariance, graphical
lasso, DeltaQ, D_C DeltaQ, Omega_s, enrichment, behavioral thresholds,
current-velocity statistics, or state-conditioned neural statistics were loaded
or computed.

## Locked Inputs

- `IDENTITY_CONFIDENCE_THRESHOLD = {threshold}`
- `LR_POLICY = "{lr_policy}"`
- Atanas record coverage rule from `task.md`: labels must pass the confidence
  threshold in at least 80% of Atanas records.

The threshold and LR policy were not changed.

## Decoder Schema Check

The JLD2 file contains a top-level `dict_neuropal_label` dictionary encoded as
a 40-entry object-reference vector. Each top-level key is an Atanas-style record
ID. For each record, exactly one child object was identifiable as the
label-bearing structure because:

- its top-level keys are neuron-class strings;
- its leaf objects decode as key-value dictionaries;
- every decoded label dictionary contains a string `label` field and a numeric
  `confidence` field.

The other child object is integer-keyed and was not used for label coverage.

## Tiny Metadata Values Read

- Atanas record ID strings.
- Label dictionary field names.
- Label strings, `neuron_class`, `LR`, `DV`, `region`, small `roi_id` integer
  lists, and scalar `confidence` values.

These are NeuroPAL label metadata only.

## Atanas Decode Summary

- Atanas records decoded: {len(records)}
- Record IDs: `{sample_labels([record.record_id for record in records], limit=80)}`
- Decoded label entries per record: min {min(record_counts)}, median {sorted(record_counts)[len(record_counts)//2]}, max {max(record_counts)}
- Confidence-filtered normalized labels per record: min {min(confident_counts)}, median {sorted(confident_counts)[len(confident_counts)//2]}, max {max(confident_counts)}
- Required records for 80% coverage: {coverage_required_records}
- Atanas labels meeting confidence threshold in at least 80% of records: {len(atanas_high_coverage)}

Example high-coverage Atanas labels:

`{sample_labels(atanas_high_coverage)}`

High-confidence labels with `?` or `alt` markers were not silently resolved.
Ambiguous/alternate examples observed:

`{sample_labels(ambiguous_confident)}`

## Ambiguity Assessment

The label and confidence fields are unambiguous for this h5py decoder: the
decoded leaf dictionaries contain literal `label` and `confidence` field names.

Remaining biological/name ambiguities such as `?`-marked labels are not
silently mapped. They do not contribute to the common subgraph unless they
already match canonical labels after the configured normalization and overlap
checks.

## Deviations

No deviations recorded.
"""
    ATANAS_DECODE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ATANAS_DECODE_REPORT_PATH.write_text(decode_report, encoding="utf-8")

    feasibility_report = f"""# Stage 2 Subgraph Feasibility Under Locked Threshold

Date: {today}

## Scope

Stage 2 label-only feasibility check using:

- the Atanas NeuroPAL label JLD2 artifact;
- small ConnectomeToolbox label tables;
- small wormneuroatlas label metadata tables;
- Ripoll-Sanchez CSV header rows only.

No connectome adjacency matrices, biological activity arrays, behavioral time
series, functional atlas matrices, covariance-like matrices, covariance,
precision, inverse covariance, graphical lasso, DeltaQ, D_C DeltaQ, Omega_s,
enrichment, behavioral threshold, current-velocity statistic, or
state-conditioned neural statistic was computed.

## Small Tables / Metadata Loaded

{bullet(loaded_files)}
The Ripoll-Sanchez CSVs were used only for their header-row neuron labels;
matrix entries were not loaded or analyzed.

## Harmonization Rules Applied

- Whitespace and quote characters were stripped; labels were uppercased.
- Missing-like labels (`NA`, `N/A`, `NONE`, `MISSING`, `NAN`) were dropped.
- Numbered ventral-cord labels with zero padding were normalized, for example
  `VA01 -> VA1`, `DB07 -> DB7`, and `AS09 -> AS9`.
- `LR_POLICY = "separate"` was enforced: left/right homologs such as `AVAL` and
  `AVAR` remained separate nodes.
- Dorsal/ventral, numbered, and bilateral classes were not collapsed.
- AWC ON/OFF labels were not silently mapped to left/right labels. The Randi
  metadata contains AWC ON/OFF-style labels: {sample_labels(awc_on_off_labels)}.

## Atanas Confidence Coverage

- Atanas records decoded: {len(records)}
- Locked confidence threshold: {threshold}
- Required records for 80% Atanas coverage: {coverage_required_records}
- Atanas labels passing threshold in at least 80% of records: {len(atanas_high_coverage)}

## Label Overlap

- Atanas high-coverage labels intersection ConnectomeToolbox labels intersection Randi all-neuron labels:
  {len(common_all_randi)}
- Atanas high-coverage labels intersection ConnectomeToolbox labels intersection Randi head labels:
  {len(common_head_randi)}
- Above all-neuron overlap intersection Ripoll-Sanchez neuropeptide header labels:
  {len(common_all_randi & ripoll_labels)}

Randi label-source convention note:

- Common labels present in the Randi head-ganglia metadata but absent from
  `neuron_ids.txt`: `{sample_labels(head_not_all)}`
- Common labels present in `neuron_ids.txt` but absent from the Randi
  head-ganglia metadata: `{sample_labels(all_not_head)}`

For the AWC class, `neuron_ids.txt` uses `AWCON`/`AWCOFF`, while
`aconnectome_ids_ganglia.json` uses `AWCL`/`AWCR`. This was not silently
resolved; both source conventions are reported for human review.

Primary `N_COMMON_NEURONS` is recorded as the Randi-head overlap because Randi
2023 is a head-ganglion preparation in the verified Phase 0 config.

## Computed Config-Field Outcomes

- `N_COMMON_NEURONS = {len(common_head_randi)}`
- `N_RANDI_SUBGRAPH_PAIRS`: unavailable; Stage 3 functional pair extraction was
  not run.
- `SUBGRAPH_ADEQUATE`: remains `None`; this is a human decision.

Common labels used for `N_COMMON_NEURONS`:

`{sample_labels(common_head_randi, limit=120)}`

## Deviations

No deviations recorded.
"""
    FEASIBILITY_REPORT_PATH.write_text(feasibility_report, encoding="utf-8")


def main() -> None:
    config = load_config()
    threshold = config.IDENTITY_CONFIDENCE_THRESHOLD
    lr_policy = config.LR_POLICY
    coverage_fraction = config.COVERAGE_FRACTION
    if threshold != 2.5:
        raise RuntimeError(f"Expected locked IDENTITY_CONFIDENCE_THRESHOLD=2.5, got {threshold!r}")
    if lr_policy != "separate":
        raise RuntimeError(f"Expected locked LR_POLICY='separate', got {lr_policy!r}")

    atanas_root = ROOT / config.ATANAS_PATH
    connectome_root = ROOT / config.CONNECTOME_PATH
    randi_root = ROOT / config.RANDI_PATH
    for name, path in (
        ("ATANAS_PATH", atanas_root),
        ("CONNECTOME_PATH", connectome_root),
        ("RANDI_PATH", randi_root),
    ):
        if not path.exists():
            raise RuntimeError(f"{name} does not exist: {path}")

    atanas_jld2_path = atanas_root / "neuropal_label_prj_kfc" / "dict_neuropal_label.jld2"
    atanas_reference_path = (
        atanas_root / "src" / "ANTSUN" / "NeuroPALData.jl" / "src" / "reference" / "neuron_class_all.csv"
    )
    connectome_individual_path = connectome_root / "cect" / "data" / "IndividualNeurons.csv"
    connectome_all_cell_info_path = connectome_root / "cect" / "data" / "all_cell_info.csv"
    randi_neuron_ids_path = randi_root / "wormneuroatlas" / "data" / "neuron_ids.txt"
    randi_ganglia_path = randi_root / "wormneuroatlas" / "data" / "aconnectome_ids_ganglia.json"
    ripoll_paths = [
        connectome_root / "cect" / "data" / "01022024_neuropeptide_connectome_short_range_model.csv",
        connectome_root / "cect" / "data" / "01022024_neuropeptide_connectome_mid_range_model.csv",
        connectome_root / "cect" / "data" / "01022024_neuropeptide_connectome_long_range_model.csv",
    ]

    required = [
        atanas_jld2_path,
        atanas_reference_path,
        connectome_individual_path,
        connectome_all_cell_info_path,
        randi_neuron_ids_path,
        randi_ganglia_path,
        *ripoll_paths,
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Missing required small label/metadata files: " + ", ".join(missing))

    records = decode_atanas_jld2(atanas_jld2_path)
    record_count = len(records)
    coverage_required_records = math.ceil(record_count * coverage_fraction)
    coverage_counts = label_count_table(records, threshold=threshold, lr_policy=lr_policy)
    atanas_high_coverage = {
        label for label, count in coverage_counts.items() if count >= coverage_required_records
    }

    # Reference labels are loaded as a consistency filter, not as a substitute for
    # per-record confidence coverage.
    atanas_reference = read_atanas_reference_labels(atanas_reference_path, lr_policy)
    atanas_high_coverage &= atanas_reference

    connectome_individual = read_individual_neurons(connectome_individual_path, lr_policy)
    connectome_all_cell_info = read_all_cell_info_labels(connectome_all_cell_info_path, lr_policy)
    connectome_labels = connectome_individual & connectome_all_cell_info
    randi_all = read_randi_neuron_ids(randi_neuron_ids_path, lr_policy)
    randi_head = read_randi_head_ids(randi_ganglia_path, lr_policy)

    ripoll_labels: set[str] = set()
    for path in ripoll_paths:
        ripoll_labels.update(read_csv_header_labels(path, lr_policy))

    common_all_randi = atanas_high_coverage & connectome_labels & randi_all
    common_head_randi = atanas_high_coverage & connectome_labels & randi_head
    awc_on_off_labels = {label for label in randi_all if is_awc_on_off_label(label)}

    n_common = len(common_head_randi)
    write_phase0_n_common(n_common)

    loaded_files = [
        rel(atanas_jld2_path),
        rel(atanas_reference_path),
        rel(connectome_individual_path),
        rel(connectome_all_cell_info_path),
        rel(randi_neuron_ids_path),
        rel(randi_ganglia_path),
        *[rel(path) + " (header row only)" for path in ripoll_paths],
    ]
    write_reports(
        threshold=threshold,
        lr_policy=lr_policy,
        loaded_files=loaded_files,
        records=records,
        coverage_required_records=coverage_required_records,
        atanas_high_coverage=atanas_high_coverage,
        connectome_labels=connectome_labels,
        randi_all=randi_all,
        randi_head=randi_head,
        ripoll_labels=ripoll_labels,
        common_all_randi=common_all_randi,
        common_head_randi=common_head_randi,
        awc_on_off_labels=awc_on_off_labels,
    )

    print(f"Stage 2 Atanas label decode report written: {rel(ATANAS_DECODE_REPORT_PATH)}")
    print(f"Stage 2 feasibility report written: {rel(FEASIBILITY_REPORT_PATH)}")
    print(f"Locked threshold used: IDENTITY_CONFIDENCE_THRESHOLD={threshold}")
    print(f"Locked LR policy used: LR_POLICY={lr_policy}")
    print(f"Atanas records decoded: {record_count}")
    print(f"Required records for 80% coverage: {coverage_required_records}")
    print(f"Atanas high-coverage labels: {len(atanas_high_coverage)}")
    print(f"Atanas/connectome/Randi all-neuron overlap: {len(common_all_randi)}")
    print(f"N_COMMON_NEURONS: {n_common}")
    print("N_RANDI_SUBGRAPH_PAIRS: unavailable; Stage 3 functional pair extraction not run")
    print("SUBGRAPH_ADEQUATE remains None")


if __name__ == "__main__":
    main()
