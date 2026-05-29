# Stage 3 Randi Pair-Index Planning

Date: 2026-05-28

## Scope

Pair-index planning step using observed-pair counts from `wt/occ1` and
`unc31/occ1` in `funatlas.h5`. Restricted to the effective 60-neuron
pair-analysis subgraph.

Loaded in this step:
  - `neuron_ids`  (300 labels, string)
  - `wt/occ1`    (300×300 int64, ~720 KB)
  - `unc31/occ1` (300×300 int64, ~720 KB)

NOT loaded:
  - dFF, dFF_all, kernels, q, q_eq (no response values, no significance data)

NOT computed:
  - DCV scores, significance filters, enrichment, covariance, precision
  - Any threshold-based filtering
  - q_eq_th is not used (approved as undocumented/stale)

N_RANDI_SUBGRAPH_PAIRS is NOT set here (requires significance filtering,
authorized in a later step).

## Approved Namespace Asymmetry

- `N_COMMON_NEURONS = 61` — anatomical harmonization subgraph (Atanas ∩
  ConnectomeToolbox ∩ Randi head labels, approved 2026-05-28).
- `N_RANDI_SUBGRAPH_NEURONS = 60` — effective funatlas pair-analysis subgraph:
  common-61 minus AWCL, which has no funatlas entry under its anatomical label.
- AWCL (anatomical) and AWCOF/AWCON (functional-state) remain distinct
  namespaces. No mapping is applied. This asymmetry is approved and documented.

## Effective Pair-Analysis Subgraph

Source file: `data/randi/wormneuroatlas/wormneuroatlas/data/funatlas.h5`
funatlas total neurons: 300
Subgraph neurons (N_RANDI_SUBGRAPH_NEURONS): 60
Neurons excluded from funatlas pairing: ['AWCL']

Subgraph neuron list (60 neurons):
ADEL, AIBL, AIBR, AIZL, ASEL, ASGL, AUAL, AVAL, AVAR, AVDL, AVEL, AVER, AVJL, AVJR, AWAL, AWBL, CEPDL, CEPDR, CEPVL, FLPL, I1L, I1R, I2L, I2R, I3, IL1DR, IL1L, IL1R, IL2DL, IL2DR, IL2VL, IL2VR, M1, M3L, M3R, M4, MI, NSML, NSMR, OLLL, OLLR, OLQDL, OLQDR, OLQVL, OLQVR, RICL, RID, RIVL, RMDDR, RMDL, RMDVL, RMDVR, RMEL, RMER, SMDVL, URBL, URXL, URYDL, URYVL, URYVR

## Observed-Pair Counts

Directed pairs (i → j with i ≠ j, within the 60-neuron subgraph):

| Category                              | Count  | % of 3540 possible |
|---------------------------------------|--------|--------------------------|
| WT  observed (occ1_wt > 0)            |  3118  | 88.1%                    |
| unc31 observed (occ1_u31 > 0)         |  2057  | 58.1%                    |
| Both WT and unc31 observed            |  1964  | 55.5%                    |
| WT only (unc31 not measured)          |  1154  |                          |
| unc31 only (WT not measured)          |    93  |                          |

Note: "observed" means occ1 > 0 for that pair. DCV score computation requires
both WT and unc31 to be measured (n_both_observed = 1964).

## Neuron Coverage

- Neurons appearing in ≥ 1 observed WT  pair: 60 / 60
- Neurons appearing in ≥ 1 observed unc31 pair: 58 / 60

All 60 subgraph neurons appear in at least one WT observed pair: YES

## Feasibility for Authorized Stage 3 Extraction

The following Stage 3 operations are feasible without Phase 0 violations:

1. Loading wt/dFF and unc31/dFF for DCV score computation (~720 KB each).
2. Loading wt/q and unc31/q for WT significance filtering.
3. Restricting to the 60-neuron funatlas subgraph using the index map above.
4. Computing DCV_score(i,j) = dFF_wt(i,j) - dFF_unc31(i,j) for the
   1964 pairs observed in both strains.
5. Producing ranked pair list and subgraph-restricted CSV.

The DCV score computation is NOT run here. It requires a separate authorized
step with explicit human go-ahead after this planning report is reviewed.

## AWCL Pairs in Stage 3

AWCL contributes 0 directed pairs to the Randi functional atlas because
funatlas.h5 has no entry under the anatomical label 'AWCL'. All pairs
involving AWCL will be absent from the Randi pair list. This does NOT
affect N_COMMON_NEURONS or the primary harmonization subgraph. The
asymmetry is documented in phase0_config.py (N_RANDI_SUBGRAPH_NEURONS = 60)
and in this report.

## Config Fields Set This Step

- `N_RANDI_SUBGRAPH_NEURONS = 60` — added to phase0_config.py
  (SUBGRAPH / HARMONIZATION section)
- `N_RANDI_SUBGRAPH_PAIRS` — NOT set (requires significance filtering)
- `SUBGRAPH_ADEQUATE` — NOT set (human decision)

## Deviations

No deviations.
