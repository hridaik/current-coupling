# Atanas Input Discovery Audit

Date: 2026-05-28

## Scope

Read-only filename and text discovery under `data/atanas/`.

Allowed materials inspected: filenames, README/docs, scripts, notebooks, and
lightweight code text. No neural activity arrays, behavioral time series, HDF5
datasets, JLD2 objects, or Excel workbooks were loaded.

No covariance, precision, inverse covariance, graphical lasso, DeltaQ,
`D_C DeltaQ`, `Omega_s`, enrichment, behavioral thresholds,
current-velocity statistics, state-conditioned neural statistics,
common-neuron counts, or functional-pair counts were computed.

## Required Confidence-Bearing Inputs

The audit searched for:

- `list_neuropal_label.jld2`
- `Neuron ID.xlsx`
- `neuropal_registration`
- `roi_match_confidence`
- `match_confidence`
- Zenodo / WormWideWeb / processed data instructions

## Local Presence Check

The required confidence-bearing Atanas label files were not found under
`data/atanas/`.

Not found:

- `list_neuropal_label.jld2`
- any `*Neuron ID.xlsx`
- Atanas processed `*-data.h5` files containing `neuropal_registration`

The only `.h5` files found under `data/atanas/` were test/resource files in the
bundled `pytorch-3dunet` subtree:

- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/pytorch-3dunet/tests/resources/sample_ovule.h5`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/pytorch-3dunet/resources/random3D.h5`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/pytorch-3dunet/resources/random4D.h5`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/pytorch-3dunet/resources/sample_ovule.h5`

These are not the Atanas processed data files referenced by the NeuroPAL
notebooks.

## Public Source / Repository Instructions Found

`data/atanas/AtanasKim-Cell2023/README.md` gives the public data source:

> The processed data files and the trained neural network weights are available in [the repository](https://doi.org/10.5281/zenodo.8150514).

The same README points to WormWideWeb:

> The datasets and modeling results (encoding detection) from this project can be browsed in [WormWideWeb](https://wormwideweb.org/).

`data/atanas/AtanasKim-Cell2023/src/CePNEM/CePNEMAnalysis.jl/README.md`
also points to preprocessed data from WormWideWeb:

> This notebook can also be used by downloading our preprocessed data from wormwideweb.org and examining it here.

## Internal Paths Referenced by Notebooks

The notebooks expect processed HDF5 files with a `neuropal_registration` key.

`data/atanas/AtanasKim-Cell2023/notebook/NeuroPAL circuit.ipynb`:

```julia
path_data = "/scratch/prj_kfc/processed_h5/$(data_uid)-data.h5"
data_dict = import_data(path_data, custom_keys=["neuropal_registration"])
```

The same notebook expects a precompiled NeuroPAL-label JLD2 file:

```julia
list_neuropal_label = load("/scratch/prj_kfc/list_neuropal_label.jld2")["list_neuropal_label"];
```

`data/atanas/AtanasKim-Cell2023/notebook/connectome analysis.ipynb` shows
the source pattern for per-dataset Excel labels:

```julia
path_label = joinpath("/data1/prj_neuropal/data/neuropal_label_prj_kfc/", "$(data_uid) Neuron ID.xlsx")
push!(list_neuropal_label, import_neuropal_label(path_label))
```

`data/atanas/AtanasKim-Cell2023/src/CePNEM/CePNEMAnalysis.jl/notebook/CePNEM-analysis.ipynb`
uses another processed-HDF5 root:

```julia
path_h5_data = "/data1/prj_kfc/data/processed_h5"
```

and later loads registrations from those files:

```julia
path_data = joinpath(path_h5_data, "$(data_uid)-data.h5")
data_dict = import_data(path_data, custom_keys=["neuropal_registration"])
```

## Confidence Fields Confirmed in Code Text

`data/atanas/AtanasKim-Cell2023/src/CePNEM/ANTSUNDataJLD2.jl/src/data_h5.jl`
documents the HDF5 storage key:

```julia
g4 = create_group(h5f, "neuropal_registration")
g4["roi_match_confidence"] = data_dict_match["roi_match_confidence"]
g4["roi_match"] = data_dict_match["roi_matches"]
```

`data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/match.jl`
shows that the matching pipeline reads the HDF5 registration fields:

```julia
neuropal_reg = data_dict["neuropal_registration"]
roi_match = neuropal_reg["roi_match"]
roi_match_confidence = neuropal_reg["roi_match_confidence"]
```

The same file contains the locked threshold source discovered earlier:

```julia
function get_list_match_dict(list_neuropal_label; list_data_dict, list_dict_fit, list_class_ordered,
    list_class_classify_dv_enc, θ_confidence = 2., θ_confidence_label = 2.5)
```

and applies it to label confidence:

```julia
if isa(roi_gcamp, Int) && match["confidence"] >= θ_confidence_label && !occursin("alt", match["label"])
```

`data/atanas/AtanasKim-Cell2023/src/ANTSUN/ExtractRegisteredData.jl/src/register_neurons.jl`
defines the match-confidence output:

```julia
roi_match_confidence = zeros(maximum(keys(roi_matches)))
```

and returns it:

```julia
roi_matches, inv_matches, roi_match_best, roi_match_confidence
```

## Recommended Local Destination

Recommended local placement under `data/atanas/`:

- processed HDF5 files:
  `data/atanas/AtanasKim-Cell2023/processed_h5/<data_uid>-data.h5`
- per-dataset NeuroPAL Excel labels:
  `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/<data_uid> Neuron ID.xlsx`
- optional precompiled NeuroPAL label bundle, if supplied:
  `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/list_neuropal_label.jld2`

This mirrors the source notebooks while keeping the inputs under the configured
Atanas repository root.

## Outcome

The missing blocker is a local input-availability issue, not a threshold or
harmonization-code issue. `IDENTITY_CONFIDENCE_THRESHOLD = 2.5` remains locked
and was not changed. `phase0_config.py` was not modified.

Stage 3 was not started.

## Deviations

No deviations recorded.
