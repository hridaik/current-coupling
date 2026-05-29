# Stage 2 Subgraph Feasibility Under Locked Threshold

Date: 2026-05-28

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

- `data/atanas/AtanasKim-Cell2023/neuropal_label_prj_kfc/dict_neuropal_label.jld2`
- `data/atanas/AtanasKim-Cell2023/src/ANTSUN/NeuroPALData.jl/src/reference/neuron_class_all.csv`
- `data/connectome/ConnectomeToolbox/cect/data/IndividualNeurons.csv`
- `data/connectome/ConnectomeToolbox/cect/data/all_cell_info.csv`
- `data/randi/wormneuroatlas/wormneuroatlas/data/neuron_ids.txt`
- `data/randi/wormneuroatlas/wormneuroatlas/data/aconnectome_ids_ganglia.json`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_short_range_model.csv (header row only)`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_mid_range_model.csv (header row only)`
- `data/connectome/ConnectomeToolbox/cect/data/01022024_neuropeptide_connectome_long_range_model.csv (header row only)`

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
  metadata contains AWC ON/OFF-style labels: AWCOFF, AWCON.

## Atanas Confidence Coverage

- Atanas records decoded: 40
- Locked confidence threshold: 2.5
- Required records for 80% Atanas coverage: 32
- Atanas labels passing threshold in at least 80% of records: 61

## Label Overlap

- Atanas high-coverage labels intersection ConnectomeToolbox labels intersection Randi all-neuron labels:
  60
- Atanas high-coverage labels intersection ConnectomeToolbox labels intersection Randi head labels:
  61
- Above all-neuron overlap intersection Ripoll-Sanchez neuropeptide header labels:
  60

Randi label-source convention note:

- Common labels present in the Randi head-ganglia metadata but absent from
  `neuron_ids.txt`: `AWCL`
- Common labels present in `neuron_ids.txt` but absent from the Randi
  head-ganglia metadata: `none`

For the AWC class, `neuron_ids.txt` uses `AWCON`/`AWCOFF`, while
`aconnectome_ids_ganglia.json` uses `AWCL`/`AWCR`. This was not silently
resolved; both source conventions are reported for human review.

Primary `N_COMMON_NEURONS` is recorded as the Randi-head overlap because Randi
2023 is a head-ganglion preparation in the verified Phase 0 config.

## Computed Config-Field Outcomes

- `N_COMMON_NEURONS = 61`
- `N_RANDI_SUBGRAPH_PAIRS`: unavailable; Stage 3 functional pair extraction was
  not run.
- `SUBGRAPH_ADEQUATE`: remains `None`; this is a human decision.

Common labels used for `N_COMMON_NEURONS`:

`ADEL, AIBL, AIBR, AIZL, ASEL, ASGL, AUAL, AVAL, AVAR, AVDL, AVEL, AVER, AVJL, AVJR, AWAL, AWBL, AWCL, CEPDL, CEPDR, CEPVL, FLPL, I1L, I1R, I2L, I2R, I3, IL1DR, IL1L, IL1R, IL2DL, IL2DR, IL2VL, IL2VR, M1, M3L, M3R, M4, MI, NSML, NSMR, OLLL, OLLR, OLQDL, OLQDR, OLQVL, OLQVR, RICL, RID, RIVL, RMDDR, RMDL, RMDVL, RMDVR, RMEL, RMER, SMDVL, URBL, URXL, URYDL, URYVL, URYVR`

## Deviations

No deviations recorded.
