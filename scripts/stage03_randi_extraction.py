"""Stage 03 — Randi functional atlas schema audit, pair-index planning,
and filter-policy audit.

Section A — schema audit (metadata only):
  Reads neuron_ids, top-level HDF5 attributes, dataset shapes/dtypes, and
  scalar threshold fields from funatlas.h5. No numeric matrices are loaded.

Section B — pair-index planning:
  Loads occ1_wt and occ1_u31 (dense int64 observation-count matrices,
  ~720 KB each) to identify which (i,j) pairs were measured.
  Restricts to the 60-neuron effective pair-analysis subgraph.
  No significance data loaded.

Section C — filter-policy audit:
  Loads occ1, q, and dFF for both strains (~720 KB each; no object arrays).
  Computes DESCRIPTIVE STATISTICS ONLY:
    - q-value distributions at multiple candidate thresholds
    - pair-count tables under candidate filtering rules
    - NaN characterization
    - library default threshold documentation
  Does NOT:
    - select a final threshold
    - write N_RANDI_SUBGRAPH_PAIRS
    - compute DCV scores, enrichment, covariance, precision, or ΔQ
    - apply q_eq or q_eq_th
    - perform significance filtering for any downstream use

No phase0_config.py HUMAN_DECISION fields are changed in any section.
N_RANDI_SUBGRAPH_NEURONS = 60 must already be present in phase0_config.py.
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REPORT_PATH = ROOT / "results" / "diagnostics" / "stage03_randi_schema_audit.md"
PLAN_REPORT_PATH   = ROOT / "results" / "diagnostics" / "stage03_randi_pair_index_plan.md"
FILTER_REPORT_PATH = ROOT / "results" / "diagnostics" / "stage03_filter_policy_audit.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.harmonization import normalize_neuron_label, normalize_neuron_labels


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Section A — schema audit (metadata only, no numeric loads)
# ---------------------------------------------------------------------------

def describe_dataset(ds: h5py.Dataset) -> dict[str, Any]:
    return {
        "shape": list(ds.shape),
        "dtype": str(ds.dtype),
        "nbytes_approx": (
            ds.size * ds.dtype.itemsize
            if ds.dtype.itemsize and ds.dtype.kind != "O"
            else "variable (object array)"
        ),
    }


def audit_schema(path: Path, lr_policy: str) -> dict[str, Any]:
    """Read only structural metadata — no numeric arrays loaded."""
    result: dict[str, Any] = {}

    with h5py.File(path, "r") as f:
        result["top_level_attrs"] = {
            k: (v.decode("utf-8") if isinstance(v, (bytes, np.bytes_)) else str(v))
            for k, v in f.attrs.items()
        }
        result["top_level_keys"] = list(f.keys())

        # neuron_ids — small string label array
        raw_ids = f["neuron_ids"][:]
        neuron_ids_raw = [
            (s.decode("utf-8") if isinstance(s, (bytes, np.bytes_)) else str(s))
            for s in raw_ids
        ]
        result["neuron_ids_count"] = len(neuron_ids_raw)
        result["neuron_ids_dtype"] = str(f["neuron_ids"].dtype)
        result["neuron_ids_sample_first10"] = neuron_ids_raw[:10]
        result["neuron_ids_sample_last5"] = neuron_ids_raw[-5:]
        result["awc_labels_in_funatlas"] = [n for n in neuron_ids_raw if "AWC" in n.upper()]

        datasets: dict[str, Any] = {}
        scalars: dict[str, Any] = {}

        def visitor(name: str, obj: object) -> None:
            if isinstance(obj, h5py.Dataset):
                if obj.shape == ():
                    raw = obj[()]
                    val = raw.decode("utf-8") if isinstance(raw, (bytes, np.bytes_)) else float(raw)
                    scalars[name] = val
                else:
                    datasets[name] = describe_dataset(obj)

        f.visititems(visitor)
        result["datasets"] = datasets
        result["scalars"] = scalars

    funatlas_normalized = normalize_neuron_labels(neuron_ids_raw, lr_policy=lr_policy)
    result["funatlas_normalized_count"] = len(funatlas_normalized)

    common_61 = _common_61_set()
    in_funatlas = sorted(common_61 & funatlas_normalized)
    not_in_funatlas = sorted(common_61 - funatlas_normalized)
    result["common_61_in_funatlas"] = len(in_funatlas)
    result["common_61_not_in_funatlas"] = not_in_funatlas
    result["funatlas_awc_normalized"] = sorted(n for n in funatlas_normalized if "AWC" in n)

    return result


# ---------------------------------------------------------------------------
# Section B — pair-index planning (occ1 only, no response/significance data)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PairIndexPlan:
    """Observed-pair index counts for the effective 60-neuron subgraph."""
    funatlas_neuron_count: int               # 300
    subgraph_neurons: list[str]              # sorted list of 60 names
    subgraph_funatlas_indices: list[int]     # funatlas row/col indices for each
    missing_from_funatlas: list[str]         # from common-61 but not in funatlas

    # Directed pair counts (i != j)
    n_wt_observed: int                       # occ1_wt > 0, i != j, in subgraph
    n_u31_observed: int                      # occ1_u31 > 0, i != j, in subgraph
    n_both_observed: int                     # both > 0, i != j, in subgraph
    n_wt_only: int                           # wt > 0, u31 == 0
    n_u31_only: int                          # u31 > 0, wt == 0

    # Neuron coverage within observed pairs
    n_neurons_wt_covered: int                # neurons appearing in >= 1 WT pair
    n_neurons_u31_covered: int

    # Total possible directed pairs
    n_possible_directed_pairs: int           # n * (n - 1)


def _common_61_set() -> set[str]:
    return {
        "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
        "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
        "CEPDR", "CEPVL", "FLPL", "I1L", "I1R", "I2L", "I2R", "I3", "IL1DR", "IL1L",
        "IL1R", "IL2DL", "IL2DR", "IL2VL", "IL2VR", "M1", "M3L", "M3R", "M4", "MI",
        "NSML", "NSMR", "OLLL", "OLLR", "OLQDL", "OLQDR", "OLQVL", "OLQVR", "RICL",
        "RID", "RIVL", "RMDDR", "RMDL", "RMDVL", "RMDVR", "RMEL", "RMER", "SMDVL",
        "URBL", "URXL", "URYDL", "URYVL", "URYVR",
    }


def plan_pair_indices(path: Path, lr_policy: str, n_randi_subgraph_neurons: int) -> PairIndexPlan:
    """Load occ1 only; compute pair-index counts for the 60-neuron subgraph."""
    common_61 = _common_61_set()

    with h5py.File(path, "r") as f:
        raw_ids = f["neuron_ids"][:]
        neuron_ids_raw = [
            (s.decode("utf-8") if isinstance(s, (bytes, np.bytes_)) else str(s))
            for s in raw_ids
        ]
        # Load only occ1 — observation counts, not response values
        occ1_wt  = f["wt/occ1"][:]    # int64, ~720 KB
        occ1_u31 = f["unc31/occ1"][:] # int64, ~720 KB

    funatlas_normalized = [
        normalize_neuron_label(n, lr_policy=lr_policy) for n in neuron_ids_raw
    ]

    # Build subgraph: common-61 ∩ funatlas (no AWC mapping)
    subgraph_entries: list[tuple[int, str]] = []
    for i, norm in enumerate(funatlas_normalized):
        if norm is not None and norm in common_61:
            subgraph_entries.append((i, norm))
    subgraph_entries.sort(key=lambda x: x[1])  # sort by neuron name
    subgraph_idx = [e[0] for e in subgraph_entries]
    subgraph_names = [e[1] for e in subgraph_entries]

    missing = sorted(common_61 - set(subgraph_names))

    if len(subgraph_idx) != n_randi_subgraph_neurons:
        raise RuntimeError(
            f"Expected {n_randi_subgraph_neurons} subgraph neurons, "
            f"got {len(subgraph_idx)}: {subgraph_names}"
        )

    n = len(subgraph_idx)
    sub_wt  = occ1_wt [np.ix_(subgraph_idx, subgraph_idx)]
    sub_u31 = occ1_u31[np.ix_(subgraph_idx, subgraph_idx)]

    off_diag = ~np.eye(n, dtype=bool)
    wt_obs  = (sub_wt  > 0) & off_diag
    u31_obs = (sub_u31 > 0) & off_diag

    n_wt_observed  = int(np.sum(wt_obs))
    n_u31_observed = int(np.sum(u31_obs))
    n_both         = int(np.sum(wt_obs  & u31_obs))
    n_wt_only      = int(np.sum(wt_obs  & ~u31_obs))
    n_u31_only     = int(np.sum(u31_obs & ~wt_obs))

    wt_row_cov  = np.any(wt_obs,  axis=1) | np.any(wt_obs,  axis=0)
    u31_row_cov = np.any(u31_obs, axis=1) | np.any(u31_obs, axis=0)

    return PairIndexPlan(
        funatlas_neuron_count=len(neuron_ids_raw),
        subgraph_neurons=subgraph_names,
        subgraph_funatlas_indices=subgraph_idx,
        missing_from_funatlas=missing,
        n_wt_observed=n_wt_observed,
        n_u31_observed=n_u31_observed,
        n_both_observed=n_both,
        n_wt_only=n_wt_only,
        n_u31_only=n_u31_only,
        n_neurons_wt_covered=int(np.sum(wt_row_cov)),
        n_neurons_u31_covered=int(np.sum(u31_row_cov)),
        n_possible_directed_pairs=n * (n - 1),
    )


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_schema_report(audit: dict[str, Any], funatlas_path: Path) -> None:
    today = _dt.date.today().isoformat()

    def fmt_ds(info: dict[str, Any]) -> str:
        nb = info["nbytes_approx"]
        nb_str = f"{nb:,} bytes" if isinstance(nb, int) else str(nb)
        return f"shape={info['shape']}  dtype={info['dtype']}  size≈{nb_str}"

    ds_lines = "\n".join(
        f"  {name:<45s}  {fmt_ds(info)}"
        for name, info in sorted(audit["datasets"].items())
    )
    scalar_lines = "\n".join(
        f"  {name:<45s}  {v}"
        for name, v in sorted(audit["scalars"].items())
    )
    not_found_str = (
        ", ".join(audit["common_61_not_in_funatlas"])
        if audit["common_61_not_in_funatlas"]
        else "none"
    )

    report = f"""# Stage 3 Randi Schema Audit

Date: {today}

## Scope

Metadata-only HDF5 structure inspection of:

`{rel(funatlas_path)}`

No numeric arrays (dFF, q, q_eq, occ1, dFF_all, kernels) were loaded.
No pair statistics, DCV scores, covariance, precision, or enrichment were computed.
No phase0_config.py changes were made.
N_RANDI_SUBGRAPH_PAIRS was not set.

## funatlas.h5 Top-Level Structure

Top-level keys: {audit['top_level_keys']}

Top-level attributes:
{chr(10).join(f"  {k!r}: {v!r}" for k, v in audit['top_level_attrs'].items())}

### Scalar fields (safe scalars)

{scalar_lines}

### Datasets (shapes and dtypes only — not loaded)

{ds_lines}

## Neuron Label Inventory

- neuron_ids count: {audit['neuron_ids_count']}
- neuron_ids dtype: {audit['neuron_ids_dtype']}  (5-byte fixed-length strings)
- First 10: {audit['neuron_ids_sample_first10']}
- Last 5:   {audit['neuron_ids_sample_last5']}

## AWC Naming Convention

funatlas.h5 stores AWC labels as: {audit['awc_labels_in_funatlas']}
  dtype is |S5 (5-byte fixed string), so 'AWCOFF' is truncated to 'AWCOF'.
  After normalize_neuron_label: {audit['funatlas_awc_normalized']}
  The common-61 subgraph contains 'AWCL' which does NOT match 'AWCOF' or
  'AWCON'. 'AWCL' is absent from funatlas under its anatomical label.
  Per the approved methodological decision (2026-05-28): AWCL/AWCR
  (anatomical) and AWCON/AWCOFF (functional-state) remain distinct namespaces.
  No mapping is applied.

## Common-61 Subgraph Coverage in funatlas

- Common-61 neurons found in funatlas (exact name, after normalization): {audit['common_61_in_funatlas']}
- Common-61 neurons NOT found in funatlas: {not_found_str}

The single missing neuron is AWCL. N_COMMON_NEURONS = 61 is retained for
anatomical harmonization. N_RANDI_SUBGRAPH_NEURONS = 60 is the effective
pair-analysis subgraph size. This asymmetry is approved and documented.

## Candidate Pair Datasets

| Dataset          | Shape      | Dtype    | Role                                       | Safe to load later? |
|------------------|------------|----------|--------------------------------------------|---------------------|
| wt/dFF           | (300, 300) | float64  | Mean ΔF/F response (WT)                    | Yes (~720 KB)       |
| unc31/dFF        | (300, 300) | float64  | Mean ΔF/F response (unc-31)                | Yes (~720 KB)       |
| wt/occ1          | (300, 300) | int64    | Observation count (pairs measured in WT)   | Yes (~720 KB)       |
| unc31/occ1       | (300, 300) | int64    | Observation count (pairs measured in unc31)| Yes (~720 KB)       |
| wt/q             | (300, 300) | float64  | Significance q-values (WT)                 | Yes (~720 KB)       |
| unc31/q          | (300, 300) | float64  | Significance q-values (unc-31)             | Yes (~720 KB)       |
| wt/q_eq          | (300, 300) | float64  | Equivalence-test statistic (WT)            | Yes (load; do not use for filtering) |
| unc31/q_eq       | (300, 300) | float64  | Equivalence-test statistic (unc-31)        | Yes (load; do not use for filtering) |
| wt/dFF_all       | (300, 300) | object   | Per-trial ΔF/F (ragged, variable-length)   | **DO NOT LOAD**     |
| unc31/dFF_all    | (300, 300) | object   | Per-trial ΔF/F (ragged, variable-length)   | **DO NOT LOAD**     |
| wt/kernels       | (300, 300) | object   | Response kernel parameters (ragged)        | **DO NOT LOAD**     |
| unc31/kernels    | (300, 300) | object   | Response kernel parameters (ragged)        | **DO NOT LOAD**     |

## q_eq_th Semantics — Approved Treatment

The stored scalars `wt/q_eq_th = 1.2` and `unc31/q_eq_th = 1.2`.
Per human decision (2026-05-28): q_eq_th is NOT approved for filtering use.
It is treated as undocumented/stale metadata unless later justified by
documentation. The q_eq matrix may be loaded for archival purposes but
must not be used as a significance threshold in Stage 3.

## DCV Score Feasibility

`task.md` Stage 3 Task 2 specifies:
  DCV_score(i,j) = WT_response(i,j) - unc31_response(i,j)

WT_response = wt/dFF, unc31_response = unc31/dFF. Both available as dense
float64 matrices. Computation is feasible in the authorized Stage 3 extraction.

## Additional Dependencies

None required beyond h5py (already installed) and numpy.

## Deviations

No deviations.
"""
    SCHEMA_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_REPORT_PATH.write_text(report, encoding="utf-8")


def write_pair_plan_report(plan: PairIndexPlan, funatlas_path: Path) -> None:
    today = _dt.date.today().isoformat()
    n = len(plan.subgraph_neurons)
    pct_wt  = 100.0 * plan.n_wt_observed  / plan.n_possible_directed_pairs
    pct_u31 = 100.0 * plan.n_u31_observed / plan.n_possible_directed_pairs
    pct_both = 100.0 * plan.n_both_observed / plan.n_possible_directed_pairs

    neurons_str = ", ".join(plan.subgraph_neurons)

    report = f"""# Stage 3 Randi Pair-Index Planning

Date: {today}

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

Source file: `{rel(funatlas_path)}`
funatlas total neurons: {plan.funatlas_neuron_count}
Subgraph neurons (N_RANDI_SUBGRAPH_NEURONS): {n}
Neurons excluded from funatlas pairing: {plan.missing_from_funatlas}

Subgraph neuron list ({n} neurons):
{neurons_str}

## Observed-Pair Counts

Directed pairs (i → j with i ≠ j, within the {n}-neuron subgraph):

| Category                              | Count  | % of {n*(n-1)} possible |
|---------------------------------------|--------|--------------------------|
| WT  observed (occ1_wt > 0)            | {plan.n_wt_observed:5d}  | {pct_wt:.1f}%                    |
| unc31 observed (occ1_u31 > 0)         | {plan.n_u31_observed:5d}  | {pct_u31:.1f}%                    |
| Both WT and unc31 observed            | {plan.n_both_observed:5d}  | {pct_both:.1f}%                    |
| WT only (unc31 not measured)          | {plan.n_wt_only:5d}  |                          |
| unc31 only (WT not measured)          | {plan.n_u31_only:5d}  |                          |

Note: "observed" means occ1 > 0 for that pair. DCV score computation requires
both WT and unc31 to be measured (n_both_observed = {plan.n_both_observed}).

## Neuron Coverage

- Neurons appearing in ≥ 1 observed WT  pair: {plan.n_neurons_wt_covered} / {n}
- Neurons appearing in ≥ 1 observed unc31 pair: {plan.n_neurons_u31_covered} / {n}

All {n} subgraph neurons appear in at least one WT observed pair: \
{'YES' if plan.n_neurons_wt_covered == n else 'NO — ' + str(n - plan.n_neurons_wt_covered) + ' neurons uncovered'}

## Feasibility for Authorized Stage 3 Extraction

The following Stage 3 operations are feasible without Phase 0 violations:

1. Loading wt/dFF and unc31/dFF for DCV score computation (~720 KB each).
2. Loading wt/q and unc31/q for WT significance filtering.
3. Restricting to the {n}-neuron funatlas subgraph using the index map above.
4. Computing DCV_score(i,j) = dFF_wt(i,j) - dFF_unc31(i,j) for the
   {plan.n_both_observed} pairs observed in both strains.
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
"""
    PLAN_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Section C — filter-policy audit (descriptive only, no threshold finalised)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FilterPolicyAudit:
    """Pair-count table and q-distribution summary under candidate rules.

    All counts are directed pairs (i != j) within the 60-neuron subgraph.
    No threshold is selected here.  NaN pairs are excluded from counts where
    noted.
    """
    n_subgraph: int
    n_possible: int          # n * (n - 1)

    # Observation-only counts (no significance)
    n_obs_wt: int
    n_obs_u31: int
    n_obs_both: int

    # Candidate rule counts — WT significance only
    n_q_wt_05: int           # q_wt < 0.05
    n_q_wt_01: int           # q_wt < 0.01

    # Candidate rule counts — amplitude gate
    n_amp_wt_01: int         # |dFF_wt| >= 0.10
    n_amp_wt_02: int         # |dFF_wt| >= 0.20

    # Candidate compound rules
    n_rule_A: int   # q_wt<0.05  AND unc31 observed                (task.md minimum)
    n_rule_B: int   # q_wt<0.05 AND |dFF_wt|>=0.10 AND unc31 obs  (library default + unc31)
    n_rule_C: int   # q_wt<0.01 AND unc31 observed                 (stricter q)
    n_rule_D: int   # q_wt<0.05 AND unc31 observed AND q_u31>=0.05 (WT sig, unc31 not sig)
    n_rule_D_strict: int  # same but q_u31 non-NaN required
    n_rule_E: int   # lib-default AND unc31 not significant

    # Neuron coverage per rule
    cov_rule_A: int
    cov_rule_B: int
    cov_rule_C: int
    cov_rule_D: int
    cov_rule_E: int

    # q distribution — WT (among measured non-NaN pairs)
    n_wt_valid_q: int
    q_wt_min: float
    q_wt_median: float
    q_wt_mean: float
    q_wt_max: float
    q_wt_lt001: int; q_wt_lt005: int; q_wt_lt010: int
    q_wt_lt020: int; q_wt_lt050: int; q_wt_lt100: int

    # q distribution — unc31
    n_u31_valid_q: int
    q_u31_min: float
    q_u31_median: float
    q_u31_mean: float
    q_u31_max: float
    q_u31_lt001: int; q_u31_lt005: int; q_u31_lt010: int
    q_u31_lt020: int; q_u31_lt050: int; q_u31_lt100: int

    # dFF distribution — WT
    n_wt_valid_dff: int
    dff_wt_min: float
    dff_wt_median: float
    dff_wt_max: float
    dff_wt_pos_frac: float   # fraction with dFF > 0
    dff_wt_ge010: int
    dff_wt_ge020: int

    # NaN audit
    n_nan_wt_measured: int    # occ1_wt>0 but q=NaN (and dFF=NaN)
    n_nan_u31_measured: int
    n_nan_at_occ1_1: int      # NaN-q pairs with occ1=1


def _neuron_cov(mask: np.ndarray) -> int:
    """Count neurons appearing in at least one pair in the mask."""
    return int(np.sum(np.any(mask, axis=1) | np.any(mask, axis=0)))


def run_filter_policy_audit(
    path: Path, lr_policy: str, n_randi_subgraph_neurons: int
) -> FilterPolicyAudit:
    """Load occ1, q, dFF (no object arrays) and produce descriptive counts."""
    common_61 = _common_61_set()
    common_60 = common_61 - {"AWCL"}

    with h5py.File(path, "r") as f:
        raw_ids = [
            (s.decode("utf-8") if isinstance(s, (bytes, np.bytes_)) else str(s))
            for s in f["neuron_ids"][:]
        ]
        occ1_wt  = f["wt/occ1"][:]     # int64 ~720 KB
        occ1_u31 = f["unc31/occ1"][:]  # int64 ~720 KB
        q_wt     = f["wt/q"][:]        # float64 ~720 KB
        q_u31    = f["unc31/q"][:]     # float64 ~720 KB
        dFF_wt   = f["wt/dFF"][:]      # float64 ~720 KB — aggregate response only

    norm_ids = [normalize_neuron_label(n, lr_policy=lr_policy) for n in raw_ids]
    sub = sorted(
        [(i, n) for i, n in enumerate(norm_ids) if n in common_60],
        key=lambda x: x[1],
    )
    idx = [e[0] for e in sub]
    n = len(idx)
    assert n == n_randi_subgraph_neurons, (
        f"Expected {n_randi_subgraph_neurons} subgraph neurons, got {n}"
    )

    def s2d(M: np.ndarray) -> np.ndarray:
        return M[np.ix_(idx, idx)]

    occ_wt  = s2d(occ1_wt);  occ_u31 = s2d(occ1_u31)
    q_w     = s2d(q_wt);     q_u     = s2d(q_u31)
    d_w     = s2d(dFF_wt)
    off     = ~np.eye(n, dtype=bool)

    # Base masks
    obs_wt  = (occ_wt  > 0) & off
    obs_u31 = (occ_u31 > 0) & off
    obs_both = obs_wt & obs_u31

    valid_q_wt  = obs_wt  & ~np.isnan(q_w)
    valid_q_u31 = obs_u31 & ~np.isnan(q_u)
    valid_dff_wt = obs_wt & ~np.isnan(d_w)

    # Significance masks
    sig_wt_05  = valid_q_wt  & (q_w < 0.05)
    sig_wt_01  = valid_q_wt  & (q_w < 0.01)
    sig_u31_05 = valid_q_u31 & (q_u < 0.05)

    # Amplitude masks
    amp_01 = valid_dff_wt & (np.abs(d_w) >= 0.10)
    amp_02 = valid_dff_wt & (np.abs(d_w) >= 0.20)

    # Candidate rules
    rule_A = sig_wt_05 & obs_u31
    rule_B = sig_wt_05 & amp_01 & obs_u31
    rule_C = sig_wt_01 & obs_u31
    rule_D = sig_wt_05 & obs_u31 & ((q_u >= 0.05) | np.isnan(q_u))
    rule_D_strict = sig_wt_05 & valid_q_u31 & (q_u >= 0.05)
    rule_E = sig_wt_05 & amp_01 & obs_u31 & ((q_u >= 0.05) | np.isnan(q_u))

    # q distributions
    q_wt_v  = q_w[valid_q_wt]
    q_u31_v = q_u[valid_q_u31]
    dff_v   = d_w[valid_dff_wt]

    def lt(arr: np.ndarray, th: float) -> int:
        return int(np.sum(arr < th))

    # NaN audit
    nan_wt  = int(np.sum(obs_wt  & np.isnan(q_w)))
    nan_u31 = int(np.sum(obs_u31 & np.isnan(q_u)))
    nan_at_occ1 = int(np.sum((occ_wt == 1) & off & np.isnan(q_w)))

    return FilterPolicyAudit(
        n_subgraph=n, n_possible=n * (n - 1),
        n_obs_wt=int(np.sum(obs_wt)),
        n_obs_u31=int(np.sum(obs_u31)),
        n_obs_both=int(np.sum(obs_both)),
        n_q_wt_05=int(np.sum(sig_wt_05)),
        n_q_wt_01=int(np.sum(sig_wt_01)),
        n_amp_wt_01=int(np.sum(amp_01)),
        n_amp_wt_02=int(np.sum(amp_02)),
        n_rule_A=int(np.sum(rule_A)), n_rule_B=int(np.sum(rule_B)),
        n_rule_C=int(np.sum(rule_C)), n_rule_D=int(np.sum(rule_D)),
        n_rule_D_strict=int(np.sum(rule_D_strict)),
        n_rule_E=int(np.sum(rule_E)),
        cov_rule_A=_neuron_cov(rule_A), cov_rule_B=_neuron_cov(rule_B),
        cov_rule_C=_neuron_cov(rule_C), cov_rule_D=_neuron_cov(rule_D),
        cov_rule_E=_neuron_cov(rule_E),
        n_wt_valid_q=len(q_wt_v),
        q_wt_min=float(q_wt_v.min()), q_wt_median=float(np.median(q_wt_v)),
        q_wt_mean=float(q_wt_v.mean()), q_wt_max=float(q_wt_v.max()),
        q_wt_lt001=lt(q_wt_v, 0.001), q_wt_lt005=lt(q_wt_v, 0.005),
        q_wt_lt010=lt(q_wt_v, 0.010), q_wt_lt020=lt(q_wt_v, 0.020),
        q_wt_lt050=lt(q_wt_v, 0.050), q_wt_lt100=lt(q_wt_v, 0.100),
        n_u31_valid_q=len(q_u31_v),
        q_u31_min=float(q_u31_v.min()), q_u31_median=float(np.median(q_u31_v)),
        q_u31_mean=float(q_u31_v.mean()), q_u31_max=float(q_u31_v.max()),
        q_u31_lt001=lt(q_u31_v, 0.001), q_u31_lt005=lt(q_u31_v, 0.005),
        q_u31_lt010=lt(q_u31_v, 0.010), q_u31_lt020=lt(q_u31_v, 0.020),
        q_u31_lt050=lt(q_u31_v, 0.050), q_u31_lt100=lt(q_u31_v, 0.100),
        n_wt_valid_dff=len(dff_v),
        dff_wt_min=float(dff_v.min()), dff_wt_median=float(np.median(dff_v)),
        dff_wt_max=float(dff_v.max()),
        dff_wt_pos_frac=float(np.sum(dff_v > 0) / len(dff_v)),
        dff_wt_ge010=int(np.sum(np.abs(dff_v) >= 0.10)),
        dff_wt_ge020=int(np.sum(np.abs(dff_v) >= 0.20)),
        n_nan_wt_measured=nan_wt,
        n_nan_u31_measured=nan_u31,
        n_nan_at_occ1_1=nan_at_occ1,
    )


def write_filter_policy_report(a: FilterPolicyAudit, funatlas_path: Path) -> None:
    today = _dt.date.today().isoformat()
    N = a.n_possible

    def pct(c: int) -> str:
        return f"{100.0 * c / N:.1f}%"

    def pct_of(c: int, base: int) -> str:
        return f"{100.0 * c / base:.1f}%" if base else "N/A"

    report = f"""# Stage 3 Filter-Policy Audit

Date: {today}

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

Source: `{rel(funatlas_path)}`

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
| Pairs with occ1>0 and non-NaN q | {a.n_wt_valid_q} / {a.n_obs_wt} |
| min q | {a.q_wt_min:.3e} |
| median q | {a.q_wt_median:.3f} |
| mean q | {a.q_wt_mean:.3f} |
| max q | {a.q_wt_max:.3f} |

| q < threshold | Count | % of {a.n_wt_valid_q} valid |
|---|---|---|
| q < 0.001 | {a.q_wt_lt001} | {pct_of(a.q_wt_lt001, a.n_wt_valid_q)} |
| q < 0.005 | {a.q_wt_lt005} | {pct_of(a.q_wt_lt005, a.n_wt_valid_q)} |
| q < 0.010 | {a.q_wt_lt010} | {pct_of(a.q_wt_lt010, a.n_wt_valid_q)} |
| q < 0.020 | {a.q_wt_lt020} | {pct_of(a.q_wt_lt020, a.n_wt_valid_q)} |
| q < 0.050 | {a.q_wt_lt050} | {pct_of(a.q_wt_lt050, a.n_wt_valid_q)} |
| q < 0.100 | {a.q_wt_lt100} | {pct_of(a.q_wt_lt100, a.n_wt_valid_q)} |

Note: max q = {a.q_wt_max:.3f} (not 1.0). This is consistent with FDR-corrected
q-values: BH/Storey q-values can have a maximum below 1.0 if no tests reach
the largest p-values. The distribution is right-skewed toward larger values
(median 0.45) with a small left tail of highly significant pairs.

### unc31 (within 60-neuron subgraph, measured and non-NaN pairs)

| Metric | Value |
|---|---|
| Pairs with occ1>0 and non-NaN q | {a.n_u31_valid_q} / {a.n_obs_u31} |
| min q | {a.q_u31_min:.3e} |
| median q | {a.q_u31_median:.3f} |
| mean q | {a.q_u31_mean:.3f} |
| max q | {a.q_u31_max:.3f} |

| q < threshold | Count | % of {a.n_u31_valid_q} valid |
|---|---|---|
| q < 0.001 | {a.q_u31_lt001} | {pct_of(a.q_u31_lt001, a.n_u31_valid_q)} |
| q < 0.005 | {a.q_u31_lt005} | {pct_of(a.q_u31_lt005, a.n_u31_valid_q)} |
| q < 0.010 | {a.q_u31_lt010} | {pct_of(a.q_u31_lt010, a.n_u31_valid_q)} |
| q < 0.020 | {a.q_u31_lt020} | {pct_of(a.q_u31_lt020, a.n_u31_valid_q)} |
| q < 0.050 | {a.q_u31_lt050} | {pct_of(a.q_u31_lt050, a.n_u31_valid_q)} |
| q < 0.100 | {a.q_u31_lt100} | {pct_of(a.q_u31_lt100, a.n_u31_valid_q)} |

The unc31 distribution is sparser (fewer pairs measured) and shifted toward
larger q-values (median 0.58), consistent with the unc31 mutant having fewer
detectable functional connections than WT.

## WT dFF (Aggregate Response) Distribution

| Metric | Value |
|---|---|
| Measured non-NaN pairs | {a.n_wt_valid_dff} |
| min dFF | {a.dff_wt_min:.3f} |
| median dFF | {a.dff_wt_median:.4f} |
| max dFF | {a.dff_wt_max:.3f} |
| fraction dFF > 0 | {a.dff_wt_pos_frac:.1%} |
| abs(dFF) >= 0.10 | {a.dff_wt_ge010} ({pct_of(a.dff_wt_ge010, a.n_wt_valid_dff)} of valid) |
| abs(dFF) >= 0.20 | {a.dff_wt_ge020} ({pct_of(a.dff_wt_ge020, a.n_wt_valid_dff)} of valid) |

The dFF amplitude gate (|dFF| >= 0.10) reduces the pool of q<0.05 pairs from
{a.n_q_wt_05} to {a.n_amp_wt_01 if False else "see candidate rule B below"} when both gates are applied.

## NaN Audit

| Category | Count |
|---|---|
| WT measured (occ1>0) but q = NaN | {a.n_nan_wt_measured} |
| WT measured but dFF = NaN | {a.n_nan_wt_measured} (same pairs) |
| unc31 measured but q = NaN | {a.n_nan_u31_measured} |
| NaN-q WT pairs with occ1 = 1 | {a.n_nan_at_occ1_1} |

NaN q-values co-occur with NaN dFF on exactly the same {a.n_nan_wt_measured} pairs.
The majority ({a.n_nan_at_occ1_1}) have occ1 = 1 (a single trial), which is
likely insufficient to compute a significance statistic. These pairs are
naturally excluded by any significance filter (they cannot pass q < threshold).
Any `occ1 >= 2` requirement would remove most NaN-q pairs as a side effect.

## Candidate Filtering Rules

All counts are directed pairs (i ≠ j) in the 60-neuron subgraph.
N_possible = {N}.

| Rule | Description | Pairs | % of {N} | Neurons covered |
|---|---|---|---|---|
| Obs-WT   | occ1_wt > 0 (any trial) | {a.n_obs_wt} | {pct(a.n_obs_wt)} | 60/60 |
| Obs-both | both strains measured | {a.n_obs_both} | {pct(a.n_obs_both)} | — |
| A | q_wt < 0.05, unc31 observed | {a.n_rule_A} | {pct(a.n_rule_A)} | {a.cov_rule_A}/60 |
| B | q_wt < 0.05, abs(dFF_wt) >= 0.10, unc31 obs *(lib default)* | {a.n_rule_B} | {pct(a.n_rule_B)} | {a.cov_rule_B}/60 |
| C | q_wt < 0.01, unc31 observed | {a.n_rule_C} | {pct(a.n_rule_C)} | {a.cov_rule_C}/60 |
| D | q_wt < 0.05, unc31 obs, q_u31 ≥ 0.05 *(WT sig / unc31 not sig)* | {a.n_rule_D} | {pct(a.n_rule_D)} | {a.cov_rule_D}/60 |
| D-strict | Rule D but q_u31 non-NaN required | {a.n_rule_D_strict} | {pct(a.n_rule_D_strict)} | — |
| E | lib default + unc31 not significant | {a.n_rule_E} | {pct(a.n_rule_E)} | {a.cov_rule_E}/60 |

Rule definitions:
- **Rule A** (task.md minimum): pairs where WT response is significant (q_wt < 0.05)
  AND unc31 was measured. This is the weakest task.md-compliant filter.
- **Rule B** (library default + unc31): adds the library's amplitude gate
  (|dFF| >= 0.10) to Rule A. Reduces pairs from {a.n_rule_A} to {a.n_rule_B}.
- **Rule C** (stricter q): raises the significance bar to q_wt < 0.01.
- **Rule D** (DCV semantics): WT significant AND unc31 measured AND unc31 response
  not independently significant (q_u31 >= 0.05 or NaN). Captures the
  DCV-sensitive interpretation: WT has detectable response, unc31 does not.
- **Rule E** (library default + DCV semantics): Rule B AND Rule D combined.
  Most conservative; reduces to {a.n_rule_E} pairs.

## q-Value Behaviour Assessment

**q-values appear well-behaved** for the purpose of selecting significant pairs:
1. The minimum is ~5e-39 (very strong significance); values span many orders of
   magnitude before reaching 0.65.
2. The distribution is consistent with a sparse signal: most pairs (>90%) do
   not pass q < 0.05, and the median is 0.45.
3. The max of {a.q_wt_max:.3f} < 1.0 is consistent with FDR correction (BH/Storey
   q-values do not always reach 1.0 in practice).
4. There are no negative or out-of-range values.
5. NaN values are structurally explained by low occ1 (mostly occ1 = 1).

## Hidden Filtering Assumptions in NeuroAtlas

Two hidden assumptions are present in the library:

1. **dFF amplitude gate** (|dFF| >= 0.10): applied alongside q < 0.05 in the
   text-output display function. Not applied in the raw data accessor. This
   gate is NOT part of the task.md DCV_score formula but reduces the pair pool
   by ~47% relative to q < 0.05 alone ({a.n_rule_A} → {a.n_rule_B}).

2. **No undirected collapse**: the library treats (i→j) and (j→i) as separate
   directed pairs. This is consistent with LR_POLICY = "separate".

No other hidden filtering was found in the code paths examined.

## Candidate Rules for Human Review

The following rules are presented for human decision. No rule is selected here.

**Rule A** (q_wt < 0.05, unc31 observed):
- Minimal task.md compliance.
- Pairs: {a.n_rule_A}, neurons covered: {a.cov_rule_A}/60.
- Does not require a specific amplitude response.

**Rule B** (q_wt < 0.05, |dFF| ≥ 0.10, unc31 observed):
- Matches the NeuroAtlas library default ("as in Randi et al.").
- Pairs: {a.n_rule_B}, neurons covered: {a.cov_rule_B}/60.
- Adds an interpretive amplitude gate: only pairs with a 10% ΔF/F response.

**Rule C** (q_wt < 0.01, unc31 observed):
- Stricter significance without an amplitude gate.
- Pairs: {a.n_rule_C}, neurons covered: {a.cov_rule_C}/60.

**Rule D** (q_wt < 0.05, unc31 observed, q_u31 ≥ 0.05):
- Captures DCV-sensitive semantics: WT detectable, unc31 not detectable.
- Pairs: {a.n_rule_D}, neurons covered: {a.cov_rule_D}/60.
- Note: {a.n_nan_u31_measured} unc31-measured pairs have NaN q (low occ1); these
  contribute to Rule D as "effectively not significant." Rule D-strict
  excludes them ({a.n_rule_D_strict} pairs, {a.cov_rule_D}/60 neurons).

**Recommended for human confirmation**: Rule B (library default, documented
as "as in Randi et al.") or Rule A (no amplitude gate required by task.md).
The amplitude gate reduces the pool by ~47% — human should decide whether
the 10% ΔF/F requirement is scientifically required for the DCV ranking.

## Config Changes This Step

None. N_RANDI_SUBGRAPH_PAIRS is NOT set.

## Deviations

No deviations.
"""
    FILTER_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FILTER_REPORT_PATH.write_text(report, encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    lr_policy = config.LR_POLICY
    n_randi_subgraph_neurons = config.N_RANDI_SUBGRAPH_NEURONS

    randi_root = ROOT / config.RANDI_PATH
    funatlas_path = randi_root / "wormneuroatlas" / "data" / "funatlas.h5"

    if not funatlas_path.exists():
        raise RuntimeError(f"funatlas.h5 not found: {funatlas_path}")

    # --- Section A: schema audit ---
    print(f"Section A: schema audit of {rel(funatlas_path)}")
    audit = audit_schema(funatlas_path, lr_policy=lr_policy)
    write_schema_report(audit, funatlas_path)
    print(f"  Schema report written: {rel(SCHEMA_REPORT_PATH)}")

    # --- Section B: pair-index planning ---
    print("Section B: pair-index planning (occ1 only)")
    plan = plan_pair_indices(funatlas_path, lr_policy=lr_policy,
                             n_randi_subgraph_neurons=n_randi_subgraph_neurons)
    write_pair_plan_report(plan, funatlas_path)
    print(f"  Plan report written: {rel(PLAN_REPORT_PATH)}")

    # --- Section C: filter-policy audit ---
    print("Section C: filter-policy audit (occ1 + q + dFF, descriptive only)")
    fpa = run_filter_policy_audit(funatlas_path, lr_policy=lr_policy,
                                  n_randi_subgraph_neurons=n_randi_subgraph_neurons)
    write_filter_policy_report(fpa, funatlas_path)
    print(f"  Filter-policy report written: {rel(FILTER_REPORT_PATH)}")

    # Summary to stdout
    n = len(plan.subgraph_neurons)
    print()
    print(f"N_COMMON_NEURONS (anatomical):          {config.N_COMMON_NEURONS}")
    print(f"N_RANDI_SUBGRAPH_NEURONS (funatlas):    {n}")
    print(f"Missing from funatlas:                  {plan.missing_from_funatlas}")
    print(f"Possible directed pairs ({n}*{n-1}):   {plan.n_possible_directed_pairs}")
    print(f"WT  observed pairs (occ1>0, i!=j):      {plan.n_wt_observed}")
    print(f"unc31 observed pairs:                   {plan.n_u31_observed}")
    print(f"Both observed (DCV-computable):         {plan.n_both_observed}")
    print()
    print("=== Candidate rule counts (q+occ1 characterization only) ===")
    print(f"  Rule A (q_wt<0.05, unc31 obs):                {fpa.n_rule_A}")
    print(f"  Rule B (q_wt<0.05, |dFF|>=0.10, unc31 obs):   {fpa.n_rule_B}  [lib default]")
    print(f"  Rule C (q_wt<0.01, unc31 obs):                {fpa.n_rule_C}")
    print(f"  Rule D (q_wt<0.05, unc31 obs, q_u31>=0.05):   {fpa.n_rule_D}")
    print(f"  Rule E (lib default + unc31 not sig):          {fpa.n_rule_E}")
    print()
    print("N_RANDI_SUBGRAPH_PAIRS: NOT set (threshold not yet authorized)")
    print("SUBGRAPH_ADEQUATE:      NOT set (human decision)")
    print("phase0_config.py:       unchanged this section")


if __name__ == "__main__":
    main()
