# Atanas JLD2 HDF5 Metadata Audit

Date: 2026-05-28

## Scope

Human checkpoint approved installing exactly one additional `.venv`
dependency, `h5py`, for metadata-only inspection of:

`data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`

No full dataset contents were loaded. No neural activity arrays, behavioral time
series, common-neuron counts, subgraph statistics, covariance, precision,
inverse covariance, graphical lasso, DeltaQ, `D_C DeltaQ`, `Omega_s`,
enrichment, behavioral thresholds, current-velocity statistics, or
state-conditioned neural statistics were computed.

`phase0_config.py` was not modified. `IDENTITY_CONFIDENCE_THRESHOLD` was not
changed. `SUBGRAPH_ADEQUATE` was not set. Stage 3 was not started.

## Dependency Installation

First sandboxed attempt failed because network access was unavailable:

```text
ERROR: Could not find a version that satisfies the requirement h5py (from versions: none)
ERROR: No matching distribution found for h5py
```

The escalated retry, using the exact human-approved command, succeeded:

```text
Collecting h5py
  Using cached h5py-3.16.0-cp312-cp312-manylinux_2_28_x86_64.whl.metadata (3.0 kB)
Requirement already satisfied: numpy>=1.21.2 in ./.venv/lib/python3.12/site-packages (from h5py) (2.4.6)
Using cached h5py-3.16.0-cp312-cp312-manylinux_2_28_x86_64.whl (5.4 MB)
Installing collected packages: h5py
Successfully installed h5py-3.16.0
```

Confirmed `h5py.__version__ == "3.16.0"`.

## File Metadata

- Path: `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`
- Size: `11343265` bytes
- HDF5 user block: `512` bytes
- Top-level HDF5 keys: `_types`, `dict_neuropal_label`
- Root attributes: none

## Named HDF5/JLD2 Structure

The named HDF5 tree is sparse:

- `_types`: group
- `_types/00000001` through `_types/00000013`: JLD2 datatype definitions
- `dict_neuropal_label`: scalar dataset, HDF5 class `REFERENCE`, dtype
  `object`, shape `()`, storage `8` bytes, no attributes

The scalar `dict_neuropal_label` object reference points to an unnamed dataset:

- shape `(40,)`
- HDF5 class `REFERENCE`
- dtype `object`
- storage `320` bytes
- attribute: `julia_type`

This is consistent with a Julia/JLD2 dictionary encoded as a vector of object
references.

## Tiny Previews Read

The following tiny values were read only to identify the encoded structure:

- the scalar object reference stored in `dict_neuropal_label`
- the 40 object references in the referenced dictionary-entry vector
- the scalar string keys for those 40 entries
- object references in sampled dictionary values
- a single sampled seven-field leaf record containing scalar string/numeric
  previews

No full label arrays or confidence arrays were loaded.

## Dictionary Keys

The top-level dictionary contains 40 Atanas-style record IDs:

```text
2023-01-17-07
2022-06-28-01
2023-01-19-15
2023-01-06-08
2023-01-23-15
2023-01-06-01
2023-01-09-22
2023-03-07-01
2022-06-14-07
2022-07-15-06
2022-07-26-01
2022-12-21-06
2023-01-13-07
2022-07-20-01
2023-01-19-01
2023-01-06-15
2023-01-16-08
2023-01-18-01
2023-01-17-01
2023-01-19-08
2023-01-19-22
2023-01-10-07
2023-01-16-15
2023-01-09-08
2022-06-28-07
2022-06-14-13
2023-01-23-08
2023-01-17-14
2023-01-10-14
2023-01-23-21
2023-01-05-18
2022-07-15-12
2023-01-23-01
2023-01-09-28
2022-08-02-01
2023-01-09-15
2023-01-16-01
2023-01-16-22
2023-01-05-01
2022-06-14-01
```

## Sample Value Structure

For record `2023-01-17-07`, the value is a scalar compound object containing
two object-reference fields:

- first referenced child: shape `(124,)`, class `REFERENCE`, attribute
  `julia_type`
- second referenced child: shape `(52,)`, class `REFERENCE`, attribute
  `julia_type`

For two additional sampled records:

- `2022-06-28-01`: children with shapes `(104,)` and `(56,)`
- `2023-01-19-15`: children with shapes `(97,)` and `(51,)`

Sampled lower-level leaves are Julia compound/reference containers. One sampled
seven-field leaf record contained scalar previews:

- string: `I6`
- string: `I6`
- string: `undefined`
- null/empty object
- integer array with shape `(1,)` (values not read)
- float scalar: `3.0`
- string: `undefined`

The scalar `3.0` is confidence-like and compatible with the notebook's
confidence-threshold usage, but h5py does not expose Julia field names for this
object.

## Sufficiency Assessment

The file appears to contain the right class of information for a later
confidence-filtered `N_COMMON_NEURONS` computation:

- it is keyed by 40 Atanas-style record IDs
- each record points to per-record label-like arrays
- sampled leaves contain label-like strings and a confidence-like float scalar

However, h5py exposes the object graph as unnamed Julia/JLD2 reference and
compound containers. It does not recover Julia field names or dictionary
semantics. A later count should therefore use Julia/JLD2 semantic decoding, or
a separately reviewed h5py decoder validated against the Atanas notebook
structure, before using these data for `N_COMMON_NEURONS`.

## Next Checkpoint Need

Before computing `N_COMMON_NEURONS`, the human should approve one extraction
route:

- preferred: Julia with `JLD2.jl`, matching the source notebooks; or
- fallback: a tightly reviewed h5py decoder for this specific JLD2 object graph.

No extraction route was implemented in this audit.

## Deviations

No deviations recorded.
