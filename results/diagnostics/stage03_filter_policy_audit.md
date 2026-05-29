# Stage 3 Filter-Policy Audit

Date: 2026-05-28

## Scope

Descriptive characterization of candidate WT/unc31 pair-filtering rules within
the effective 60-neuron pair-analysis subgraph.

Loaded in this step:
  - neuron_ids (300 labels)
  - wt/occ1, unc31/occ1   (int64, ~720 KB each)
  - wt/q,    unc31/q       (float64, ~720 KB each)
  - wt/dFF                 (float64, ~720 KB — aggregate response only)

NOT loaded:
  - dFF_all, kernels (ragged object arrays)
  - q_eq (approved as stale/undocumented; not used)

NOT computed:
  - DCV scores
  - Any significance-filtered pair set for downstream use
  - N_RANDI_SUBGRAPH_PAIRS (not set)
  - Enrichment, covariance, precision, ΔQ

Source: `data/randi/wormneuroatlas/wormneuroatlas/data/funatlas.h5`

## NeuroAtlas Documented Defaults

The NeuroAtlas library (`NeuroAtlas.everything_about_to_text`) uses a
**compound filter** with two explicitly documented defaults:

1. **q < 0.05** — stated in the docstring as "Default: 0.05, as in Randi et al."
   This is the only threshold described as matching the published paper.
2. **|dFF| >= 0.10** — amplitude threshold (10% ΔF/F), documented as
   `sigprop_dff_th`, default 0.1. Applied as a second gate alongside q.

Both thresholds appear only in the text-output/display function, not in any
primary data extraction function. The raw API (`get_signal_propagation_map`,
`get_signal_propagation_q`) returns unfiltered matrices; the user is
responsible for applying thresholds.

The `q_eq_th = 1.2` stored in funatlas.h5 is NOT used by the library and is
not approved for filtering (approved as stale/undocumented, 2026-05-28).

## q-Value Distributions

### WT (within 60-neuron subgraph, measured and non-NaN pairs)

| Metric | Value |
|---|---|
| Pairs with occ1>0 and non-NaN q | 3041 / 3118 |
| min q | 4.788e-39 |
| median q | 0.451 |
| mean q | 0.396 |
| max q | 0.650 |

| q < threshold | Count | % of 3041 valid |
|---|---|---|
| q < 0.001 | 98 | 3.2% |
| q < 0.005 | 142 | 4.7% |
| q < 0.010 | 171 | 5.6% |
| q < 0.020 | 208 | 6.8% |
| q < 0.050 | 286 | 9.4% |
| q < 0.100 | 407 | 13.4% |

Note: max q = 0.650 (not 1.0). This is consistent with FDR-corrected
q-values: BH/Storey q-values can have a maximum below 1.0 if no tests reach
the largest p-values. The distribution is right-skewed toward larger values
(median 0.45) with a small left tail of highly significant pairs.

### unc31 (within 60-neuron subgraph, measured and non-NaN pairs)

| Metric | Value |
|---|---|
| Pairs with occ1>0 and non-NaN q | 1880 / 2057 |
| min q | 1.771e-04 |
| median q | 0.576 |
| mean q | 0.510 |
| max q | 0.763 |

| q < threshold | Count | % of 1880 valid |
|---|---|---|
| q < 0.001 | 4 | 0.2% |
| q < 0.005 | 16 | 0.9% |
| q < 0.010 | 22 | 1.2% |
| q < 0.020 | 40 | 2.1% |
| q < 0.050 | 81 | 4.3% |
| q < 0.100 | 126 | 6.7% |

The unc31 distribution is sparser (fewer pairs measured) and shifted toward
larger q-values (median 0.58), consistent with the unc31 mutant having fewer
detectable functional connections than WT.

## WT dFF (Aggregate Response) Distribution

| Metric | Value |
|---|---|
| Measured non-NaN pairs | 3041 |
| min dFF | -0.374 |
| median dFF | 0.0225 |
| max dFF | 0.895 |
| fraction dFF > 0 | 73.8% |
| abs(dFF) >= 0.10 | 451 (14.8% of valid) |
| abs(dFF) >= 0.20 | 137 (4.5% of valid) |

The dFF amplitude gate (|dFF| >= 0.10) reduces the pool of q<0.05 pairs from
286 to see candidate rule B below when both gates are applied.

## NaN Audit

| Category | Count |
|---|---|
| WT measured (occ1>0) but q = NaN | 77 |
| WT measured but dFF = NaN | 77 (same pairs) |
| unc31 measured but q = NaN | 177 |
| NaN-q WT pairs with occ1 = 1 | 62 |

NaN q-values co-occur with NaN dFF on exactly the same 77 pairs.
The majority (62) have occ1 = 1 (a single trial), which is
likely insufficient to compute a significance statistic. These pairs are
naturally excluded by any significance filter (they cannot pass q < threshold).
Any `occ1 >= 2` requirement would remove most NaN-q pairs as a side effect.

## Candidate Filtering Rules

All counts are directed pairs (i ≠ j) in the 60-neuron subgraph.
N_possible = 3540.

| Rule | Description | Pairs | % of 3540 | Neurons covered |
|---|---|---|---|---|
| Obs-WT   | occ1_wt > 0 (any trial) | 3118 | 88.1% | 60/60 |
| Obs-both | both strains measured | 1964 | 55.5% | — |
| A | q_wt < 0.05, unc31 observed | 189 | 5.3% | 51/60 |
| B | q_wt < 0.05, abs(dFF_wt) >= 0.10, unc31 obs *(lib default)* | 101 | 2.9% | 45/60 |
| C | q_wt < 0.01, unc31 observed | 112 | 3.2% | 44/60 |
| D | q_wt < 0.05, unc31 obs, q_u31 ≥ 0.05 *(WT sig / unc31 not sig)* | 168 | 4.7% | 50/60 |
| D-strict | Rule D but q_u31 non-NaN required | 159 | 4.5% | — |
| E | lib default + unc31 not significant | 83 | 2.3% | 44/60 |

Rule definitions:
- **Rule A** (task.md minimum): pairs where WT response is significant (q_wt < 0.05)
  AND unc31 was measured. This is the weakest task.md-compliant filter.
- **Rule B** (library default + unc31): adds the library's amplitude gate
  (|dFF| >= 0.10) to Rule A. Reduces pairs from 189 to 101.
- **Rule C** (stricter q): raises the significance bar to q_wt < 0.01.
- **Rule D** (DCV semantics): WT significant AND unc31 measured AND unc31 response
  not independently significant (q_u31 >= 0.05 or NaN). Captures the
  DCV-sensitive interpretation: WT has detectable response, unc31 does not.
- **Rule E** (library default + DCV semantics): Rule B AND Rule D combined.
  Most conservative; reduces to 83 pairs.

## q-Value Behaviour Assessment

**q-values appear well-behaved** for the purpose of selecting significant pairs:
1. The minimum is ~5e-39 (very strong significance); values span many orders of
   magnitude before reaching 0.65.
2. The distribution is consistent with a sparse signal: most pairs (>90%) do
   not pass q < 0.05, and the median is 0.45.
3. The max of 0.650 < 1.0 is consistent with FDR correction (BH/Storey
   q-values do not always reach 1.0 in practice).
4. There are no negative or out-of-range values.
5. NaN values are structurally explained by low occ1 (mostly occ1 = 1).

## Hidden Filtering Assumptions in NeuroAtlas

Two hidden assumptions are present in the library:

1. **dFF amplitude gate** (|dFF| >= 0.10): applied alongside q < 0.05 in the
   text-output display function. Not applied in the raw data accessor. This
   gate is NOT part of the task.md DCV_score formula but reduces the pair pool
   by ~47% relative to q < 0.05 alone (189 → 101).

2. **No undirected collapse**: the library treats (i→j) and (j→i) as separate
   directed pairs. This is consistent with LR_POLICY = "separate".

No other hidden filtering was found in the code paths examined.

## Candidate Rules for Human Review

The following rules are presented for human decision. No rule is selected here.

**Rule A** (q_wt < 0.05, unc31 observed):
- Minimal task.md compliance.
- Pairs: 189, neurons covered: 51/60.
- Does not require a specific amplitude response.

**Rule B** (q_wt < 0.05, |dFF| ≥ 0.10, unc31 observed):
- Matches the NeuroAtlas library default ("as in Randi et al.").
- Pairs: 101, neurons covered: 45/60.
- Adds an interpretive amplitude gate: only pairs with a 10% ΔF/F response.

**Rule C** (q_wt < 0.01, unc31 observed):
- Stricter significance without an amplitude gate.
- Pairs: 112, neurons covered: 44/60.

**Rule D** (q_wt < 0.05, unc31 observed, q_u31 ≥ 0.05):
- Captures DCV-sensitive semantics: WT detectable, unc31 not detectable.
- Pairs: 168, neurons covered: 50/60.
- Note: 177 unc31-measured pairs have NaN q (low occ1); these
  contribute to Rule D as "effectively not significant." Rule D-strict
  excludes them (159 pairs, 50/60 neurons).

**Recommended for human confirmation**: Rule B (library default, documented
as "as in Randi et al.") or Rule A (no amplitude gate required by task.md).
The amplitude gate reduces the pool by ~47% — human should decide whether
the 10% ΔF/F requirement is scientifically required for the DCV ranking.

## Config Changes This Step

None. N_RANDI_SUBGRAPH_PAIRS is NOT set.

## Deviations

No deviations.
