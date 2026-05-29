# Atanas NeuroPAL Label Artifact Metadata Audit

Date: 2026-05-28

## Scope

Read-only metadata audit of:

`data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`

No neural activity arrays, behavioral time series, HDF5/JLD2 datasets, or label
tables were loaded. No common-neuron counts were computed.

## File Presence

The file exists.

- Path: `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`
- Size: `11343265` bytes (`10.818` MiB)

Surrounding directory entries:

- `dict_neuropal_label.jld2` — file, `11343265` bytes
- `dict_neuropal_label.jld2.bz2` — file, `1313076` bytes
- `dict_neuropal_label.jld2.bz2:Zone.Identifier` — file, `25` bytes

## Format Probe

The first 16 bytes were:

```text
484446352d6261736564204a756c6961
```

The file does not begin with the raw HDF5 signature at byte 0. The leading bytes
decode to an `HDF5-based Julia...` marker, consistent with a Julia JLD2
container that needs a JLD2/HDF5-aware reader for key inspection.

## Available Dependency Check

The repository-local `.venv` does not currently provide a package capable of
inspecting this JLD2 file's keys/structure:

- `h5py`: unavailable
- Python `jld2`: unavailable
- Python `julia`: unavailable

Because of this, JLD2 keys, groups, datasets, object structure, and Julia
dictionary fields could not be inspected with current dependencies.

## Needed Mapping Status

Unconfirmed. The filename and placement are consistent with the intended public
packaged NeuroPAL-label artifact, but the current environment cannot verify
whether it contains:

- per-animal or per-record label mappings
- label IDs / neuron labels
- label-confidence fields
- the confidence-bearing information needed to apply
  `IDENTITY_CONFIDENCE_THRESHOLD = 2.5`

`N_COMMON_NEURONS` was not computed.

## Dependency Checkpoint Needed

A further dependency/tool checkpoint is needed before this artifact can be used
for Stage 2 feasibility.

Preferred inspection route:

- Julia with `JLD2.jl`, because the artifact is a Julia JLD2 container and may
  store Julia dictionaries/objects that Python HDF5 tools cannot decode
  semantically.

Possible metadata-only fallback:

- Python `h5py`, if approved, may be sufficient to inspect top-level HDF5/JLD2
  group and dataset names/shapes without reading dataset payloads, but it may
  not decode Julia object semantics.

No dependency was installed during this audit.

## Guardrail Status

No covariance, precision, inverse covariance, graphical lasso, DeltaQ,
`D_C DeltaQ`, `Omega_s`, enrichment, behavioral thresholds,
current-velocity statistics, state-conditioned neural statistics,
common-neuron counts, or functional-pair counts were computed.

`phase0_config.py` was not modified. `IDENTITY_CONFIDENCE_THRESHOLD` was not
changed. `SUBGRAPH_ADEQUATE` was not set. Stage 3 was not started.

## Deviations

No deviations recorded.
