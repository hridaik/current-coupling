# Stage 2 Atanas Label Decode

Date: 2026-05-28

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

- `IDENTITY_CONFIDENCE_THRESHOLD = 2.5`
- `LR_POLICY = "separate"`
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

- Atanas records decoded: 40
- Record IDs: `2022-06-14-01, 2022-06-14-07, 2022-06-14-13, 2022-06-28-01, 2022-06-28-07, 2022-07-15-06, 2022-07-15-12, 2022-07-20-01, 2022-07-26-01, 2022-08-02-01, 2022-12-21-06, 2023-01-05-01, 2023-01-05-18, 2023-01-06-01, 2023-01-06-08, 2023-01-06-15, 2023-01-09-08, 2023-01-09-15, 2023-01-09-22, 2023-01-09-28, 2023-01-10-07, 2023-01-10-14, 2023-01-13-07, 2023-01-16-01, 2023-01-16-08, 2023-01-16-15, 2023-01-16-22, 2023-01-17-01, 2023-01-17-07, 2023-01-17-14, 2023-01-18-01, 2023-01-19-01, 2023-01-19-08, 2023-01-19-15, 2023-01-19-22, 2023-01-23-01, 2023-01-23-08, 2023-01-23-15, 2023-01-23-21, 2023-03-07-01`
- Decoded label entries per record: min 88, median 111, max 139
- Confidence-filtered normalized labels per record: min 70, median 101, max 124
- Required records for 80% coverage: 32
- Atanas labels meeting confidence threshold in at least 80% of records: 61

Example high-coverage Atanas labels:

`ADEL, AIBL, AIBR, AIZL, ASEL, ASGL, AUAL, AVAL, AVAR, AVDL, AVEL, AVER, AVJL, AVJR, AWAL, AWBL, AWCL, CEPDL, CEPDR, CEPVL, FLPL, I1L, I1R, I2L, I2R, I3, IL1DR, IL1L, IL1R, IL2DL, IL2DR, IL2VL, IL2VR, M1, M3L, M3R, M4, MI, NSML, NSMR, ... (21 more)`

High-confidence labels with `?` or `alt` markers were not silently resolved.
Ambiguous/alternate examples observed:

`ADA?, ADE?, AIA?, AIB?, AIM?, AIN?, AIY?, AIZ?, ASI?, AVK?, AVL-alt, IL1V?, IL2?L, OLQV?, RIC?, RIF?, RIM?, RMDD?, RMF?, RMG?, RMH?, SAAD?, SABV?, SIA??, SIA?L, SIA?R, SIBV?, SIBV?-alt, SMB??, SMB?L, SMB?R, SMBD?, SMBV?, SMDD?, URAD?, URYD?`

## Ambiguity Assessment

The label and confidence fields are unambiguous for this h5py decoder: the
decoded leaf dictionaries contain literal `label` and `confidence` field names.

Remaining biological/name ambiguities such as `?`-marked labels are not
silently mapped. They do not contribute to the common subgraph unless they
already match canonical labels after the configured normalization and overlap
checks.

## Deviations

No deviations recorded.
