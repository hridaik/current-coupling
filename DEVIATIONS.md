# DEVIATIONS

## Entries

### DEV-001 — COVERAGE_FRACTION hardcoded in script (minor)

Date: 2026-05-28
Stage: 2
Severity: Minor / bookkeeping

**What happened:**
`scripts/stage02_subgraph.py` contained `COVERAGE_FRACTION = 0.80` as a
module-level constant rather than importing the value from `phase0_config.py`.

**Rule violated:**
`AGENTS.md` coding expectations: "Never hard-code parameter values in
scripts; always import from `phase0_config.py`."

**Scientific impact:**
None. The value 0.80 matches `task.md` Stage 2 Task 4 exactly ("in ≥ 80%
of Atanas animals"). No analysis output was affected.

**Resolution (2026-05-28):**
`COVERAGE_FRACTION = 0.80` added to `phase0_config.py` (SUBGRAPH /
HARMONIZATION section). The module-level constant was removed from
`scripts/stage02_subgraph.py`; `main()` now reads `config.COVERAGE_FRACTION`.
No overlap counts or config values were recomputed.

**Authorized by:** Human procedural cleanup instruction 2026-05-28.

---

### DEV-002 — N_COMMON_NEURONS written to config without checkpoint (procedural)

Date: 2026-05-28
Stage: 2
Severity: Procedural / methodology choice not checkpointed

**What happened:**
`scripts/stage02_subgraph.py` automatically wrote `N_COMMON_NEURONS = 61`
to `phase0_config.py` by calling `write_phase0_n_common(n_common)` where
`n_common = len(common_head_randi)`. The choice of `randi_head`
(`aconnectome_ids_ganglia.json`) over `randi_all` (`neuron_ids.txt`) as the
canonical Randi label source was a script decision, not an explicit human
checkpoint. The write occurred before `SUBGRAPH_ADEQUATE` was set and before
the AWC naming convention was resolved.

**Rule violated:**
`AGENTS.md` checkpoint protocol: checkpoint required before "Any change to
… any item in `phase0_config.py`." The choice of which Randi label file is
canonical for the harmonization intersection is not specified in `task.md`
and should have been a human decision.

**Scientific impact:**
None beyond what has been diagnosed. The head-label namespace choice is
scientifically defensible (`RANDI_PREPARATION = "immobilized"` confirms
Randi 2023 is a head-ganglion preparation). The AWC inconsistency (one extra
neuron, `AWCL`, in `randi_head` vs `randi_all`) has been diagnosed and
documented.

**Resolution (2026-05-28):**
Human has approved:
- `randi_head` (`aconnectome_ids_ganglia.json`) as the canonical anatomical
  namespace for Randi overlap.
- `AWCL`/`AWCR` as anatomical labels; `AWCON`/`AWCOFF` as functional-state
  labels not mapped to anatomical laterality.
- `N_COMMON_NEURONS = 61` provisionally accepted pending `SUBGRAPH_ADEQUATE`
  human decision (still `None`).

No recomputation was performed. `N_COMMON_NEURONS` remains 61 in
`phase0_config.py`.

**Authorized by:** Human procedural cleanup instruction 2026-05-28.

---

### DEV-003 — NONSTATIONARITY_FRACTION = 1.0 accepted with real-data stationarity limitation

Date: 2026-05-28
Stage: 6
Severity: Known limitation / accepted risk

**What happened:**
The Stage 6 stationarity robustness audit found that within-behavioral-state neural
covariance drifts substantially within recordings (temporal drift median 0.891 vs
random-split null median 0.214; excess median 0.666; all 26/26 assessed pairs).
The excess does not decrease with sample support (r = -0.162), ruling out
sampling noise as the sole explanation.

**Rule involved:**
task.md Stage 5: "Stationarity metrics are diagnostic during Phase 0. Epoch or animal
exclusion thresholds require human approval and must be locked before the main analysis."
task.md Stage 6: "If NONSTATIONARITY_FRACTION > 0.3: flag for human review before Stage 7."

**Root-cause hypotheses (not yet disambiguated):**
Primary: photobleaching (GCaMP6s signal-to-noise decreases over ~30–60 min recordings;
global z-scoring does not remove photobleaching effects on pairwise covariance structure).
Secondary: slow neuromodulatory drift, within-state behavioral evolution.

**Scientific impact:**
Pooled covariance estimates will represent a time-averaged effective functional coupling
across a drifting process, not a stationary latent-state covariance. This weakens the
interpretation of the precision matrix as a snapshot of a stationary state, but the
estimate remains interpretable as the "mean" coupling structure within a labeled behavioral
state. The enrichment test (off-connectome ΔQ enriched for neuropeptide annotations) tests
a contrast between states and is less sensitive to within-state drift than to between-state
drift.

**Resolution (2026-05-28):**
Human accepted NONSTATIONARITY_FRACTION = 1.0 as a confirmed finding. Project will
proceed under the interpretation that:
- Later covariance estimates represent time-averaged effective covariance structure,
  NOT perfectly stationary latent-state covariance.
- This limitation must be reported alongside primary findings.
- Stage 7 (synthetic estimator dry-runs) proceeds; the synthetic data is stationary
  by construction and tests the estimation pipeline, not real-data stationarity.
- NONSTATIONARITY_FRACTION remains 1.0 in phase0_config.py.

**Authorized by:** Human decision 2026-05-28.
