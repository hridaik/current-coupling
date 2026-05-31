# CONTEXT

## Phase 0 archived (2026-05-29)

Phase 0 has been archived in docs/phase0/. The archive is a historical record.
- docs/phase0/PHASE0_EXECUTIVE_SUMMARY.md — human-readable outcomes summary
- docs/phase0/PHASE0_ARCHIVE_INDEX.md — full artifact inventory
- docs/phase0/hypothesis_lock.md — locked hypothesis (copy)
- docs/phase0/phase0_final_summary.md — stage completion (copy)
- docs/phase0/phase1_transition_manifest.md — handoff package (copy)
- docs/phase0/phase0_locked_config_snapshot.json — frozen config values (copy)
- docs/phase0/cepnem_full_schema_confirmation.md — CePNEM structure (copy)
- PHASE1_STARTER_MANIFEST.md (repo root) — Phase 1 reference index

phase0_config.py is unchanged (md5 f75f82212886b2c987da3586ed6f5b77).
Phase 1 planning has not begun. Awaiting human authorization for DEV-003/004/005.

## CePNEM full archive — CONFIRMED findings (2026-05-29, updated)

**File status**: FULLY DECOMPRESSED (19.55 GB). h5py opens without error.

**sampled_trace_params: DIRECTLY CONFIRMED** — shape (11, 10001, N, n_epochs), float64,
present in all 68 recordings. param[4]=0.0000 (NL10d disabled constant) is the definitive
structural confirmation of the parameter ordering.

**Behavioral encoding weights directly accessible**: params[0–3] = c_vT, c_v, c_θh, c_P.
Ranges are consistent with MCMC samples from a well-mixed posterior with unit-normal priors:
- c_vT: [−5.4, 4.1] — velocity rectification
- c_v:  [−3.9, 3.5] — velocity encoding weight
- c_θh: [−5.1, 4.4] — head curvature weight
- c_P:  [−2.3, 3.0] — pumping rate weight

**Timescale parameter reparameterization (new finding)**:
stp[6] (s0) has r≈+0.99 correlation with sampled_tau_vals, but the simple formula
`compute_s(s0) = 10*exp(s0)` with `tau = log(s/(s+1))/log(0.5)*dt` does NOT reproduce
the sampled_tau_vals values. Specifically:
- For the slowest neurons (tau~244s): stp[6] is ~4.07 (positive), but the formula would
  require s0 → −∞ to produce such long timescales.
- The MCMC sampler likely uses a different reparameterization of the timescale than the
  "natural" parameterization in get_free_params.
- sampled_tau_vals appear to store tau directly in seconds (biologically interpretable).
- The mismatch means the residual computation CANNOT use the simplified formula and must
  use the full CePNEM model_nl8 forward equations: predict y[t] from params by recursion,
  then compute residual = trace_array − predicted.
- Behavioral encoding params (0–3) do NOT appear affected by this reparameterization.

**No precomputed residuals**: Neither lite nor full archive stores them. Custom computation
required. Authorized at future checkpoint only.

**Path to CePNEM residuals** (post-checkpoint):
1. Extract params = np.median(sampled_trace_params[:, :, neuron, epoch], axis=1) → 11 values
2. Run CePNEM model_nl8 recursion forward from params (c_vT, c_v, c_θh, c_P, y0, s0, b)
3. residual[t] = trace_array[neuron, t] - predicted[t]
Note: step 2 requires verifying the exact unit convention and transform for s0→s.

## CePNEM full archive — key findings (2026-05-29)

**File status:** fit_results.jld2 is truncated (4.23 GB of 19.55 GB). The JLD2 HDF5 root
group is stored at byte 19,546,888,935 — inside the missing ~15 GB portion. h5py cannot
open the file. The bz2 (12.38 GB) is the complete source and must be fully decompressed.

**Key additional field (source-code inferred): `sampled_trace_params`**

Shape (Python): `(11, 10001, N, n_epochs)` float64

This is the 11-parameter MCMC posterior for CePNEM model NL10d, per neuron per epoch.
It contains the behavioral encoding weights that the lite archive omits:

- param[1] = c_v   (velocity encoding weight)
- param[2] = c_θh  (head curvature encoding weight)
- param[3] = c_P   (pumping encoding weight)
- param[0] = c_vT  (velocity rectification)
- param[7] = b     (baseline)
- param[6] = s0    (EWMA timescale — same source as sampled_tau_vals in lite)

**Why this matters for DEV-004 (COORD_PRIMARY = gcamp_trace_array_zscore):**

With `sampled_trace_params`, CePNEM residuals can be computed via the closed-form
`model_nl8` formula (no OLS regression needed):

```python
params = np.median(sampled_trace_params[:, :, neuron, epoch], axis=1)
c_vT, c_v, c_θh, c_P = params[0], params[1], params[2], params[3]
s0, b = params[6], params[7]
s = compute_s(s0)   # EWMA decay per frame
# predicted[t] = rect * (c_v*v[t] + c_θh*θh[t] + c_P*P[t]) / (s+1) + (prev - b)*s/(s+1) + b
# residual[t]  = trace_array[neuron, t] - predicted[t]
```

This is more accurate than the lite-only OLS approach (which requires estimating β from τ̂).

**Before residuals can be computed (not yet authorized):**
1. Complete bzip2 decompression: `bzip2 -dk fit_results.jld2.bz2`
2. Verify complete file with h5py (confirm sampled_trace_params present and shape)
3. Request checkpoint to implement `compute_cepnem_residuals()` in src/preprocessing.py
4. Verify residual quality on subset before full 68-recording run

**Lite archive JLD2 status:** fit_results_lite.jld2 no longer on disk; only .bz2 remains.
Both archives need decompression before use.

## CePNEM lite artifact — what's there and what's not (2026-05-29)

fit_results_lite.jld2 is now available. Schema audit findings:

**What the lite artifact CONTAINS:**
- `trace_array` (T×N float64): bit-identical to H5 gcamp/trace_array. This is the z-scored
  GCaMP input that CePNEM was fitted on, NOT the residuals.
- `trace_original` (T×N float64): raw fluorescence (mean≈0.6, not z-scored).
- `v`, `ang_vel`, `θh`, `P`, `curve` (T,): all 5 behavioral covariates that CePNEM uses.
- `sampled_tau_vals` (10001×N×n_epochs float64): MCMC posterior samples of the EWMA timescale
  parameter τ per neuron per epoch. This is the primary CePNEM output in the lite file.
- `ranges` (n_epochs,): epoch boundary frame indices (start/stop pairs).
- `avg_timestep`, `num_neurons`: scalar metadata.

**What the lite artifact is MISSING (relative to full fit_results):**
- `beta` / `sampled_beta_vals`: behavioral encoding coefficients. These are needed to
  directly compute predicted traces and residuals. NOT PRESENT in lite.
- Precomputed residuals: NOT PRESENT.
- Log-likelihoods, convergence diagnostics: NOT PRESENT.

**Implication for DEV-004 (COORD_PRIMARY = gcamp_trace_array_zscore):**
The lite artifact makes CePNEM residuals computable but not directly readable. To upgrade
COORD_PRIMARY from "gcamp_trace_array_zscore" to "cepnem_residuals", a future checkpoint must:
1. Authorize implementing compute_cepnem_residuals() in src/preprocessing.py
2. The function would: τ̂_i = median(sampled_tau_vals[:,i,e]) → EWMA(behavioral;τ̂_i) →
   OLS fit → residuals ε_i(t) = trace_array_i - β̂_i·EWMA_i
3. Verify residual quality before use in analysis
This is a non-trivial computation requiring human authorization. Until that checkpoint,
COORD_PRIMARY stays "gcamp_trace_array_zscore".

**Sampling rate note:**
The processed H5 data and CePNEM fits run at ~1.66 Hz (avg_timestep ≈ 0.6 s/frame),
not 5 Hz. ATANAS_SAMPLING_HZ=5.0 in config is the raw volumetric acquisition rate from
the paper. The downstream processing pipeline resamples. This does not affect any locked
methodological decision (NEFF_K_MAX_FRAMES, EWMA_TIMESCALE_SECONDS, W_TRANS_SECONDS were
set in frame units or independently of sampling rate).

## Re-lock rationale (2026-05-29)

PHASE0_COMPLETE=True was set prematurely at the end of Stage 10. The correct
state is:

- PHASE0_COMPLETE = False  (real-data guardrail active in src/estimators.py)
- PHASE0_METHOD_LOCK_COMPLETE = True  (methodology and synthetic validation frozen)

The distinction matters: the *methodology* is complete and frozen (all preprocessing
choices, estimator design, hypothesis text, enrichment test design, lambda values,
etc. are locked). But *real-data inference* (computing Q_s, ΔQ, enrichment on real
Atanas data) is still prohibited because three deviations remain unresolved:

DEV-003: NONSTATIONARITY_FRACTION=1.0. Confirmed real temporal covariance drift.
  Leading cause: photobleaching. Until this is accepted as a design-level constraint
  (e.g., by explicitly scoping the main analysis to time-averaged effective coupling),
  real-data inference is premature.

DEV-004: COORD_PRIMARY=gcamp_trace_array_zscore (fallback; CePNEM files unavailable).
  Results in this coordinate contain behavioral confounds. Proceeding with real-data
  inference before CePNEM replication is possible, but it must be explicitly authorized
  so the human understands the limitation.

DEV-005: Stage 7 (inter-animal variability) not completed. OUTLIER_ANIMALS=[].
  CV fold assignments not generated. The pooled estimation can still proceed, but
  the human must explicitly sign off on this gap before real-data inference runs.

The re-lock was authorized by the incoming session instructions. The guardrail is
restored via the config change (no changes to src/estimators.py code were needed
— the existing _phase0_complete() check re-reads the config on each call).

## Notes

### Stage 5 data status (2026-05-28, updated)

Processed H5 files (68 recordings) are now available locally under
`data/atanas/AtanasKim-Cell2023/`. 40 recordings have NeuroPAL registration;
28 do not. The behavioral descriptive audit has been completed.

CePNEM fit results (required for COORD_PRIMARY = CePNEM residuals) are NOT
yet locally available. These are a separate Zenodo artifact. COORD_PRIMARY
cannot be set until these are provided.

The velocity KDE plots (`results/figures/stage05_velocity_kde.pdf`) show the
per-animal and pooled velocity distributions needed for BEHAV_THRESHOLD review.

### Raw velocity_s bouts are too short for sustained-state analysis (2026-05-28)

When BEHAV_THRESHOLD = 0.284 is applied to raw velocity_s (unsmoothed),
bouts have median 1.8 s and 0% of bouts exceed 30 s. This means
W_TRANS_SECONDS = 30 s would remove 100% of raw bouts.

This is expected from the literature: the Atanas/Flavell lab routinely uses
EWMA (exponentially-weighted moving average) smoothing of velocity before
behavioral-state classification. The "EWMA alternative comparison" notebook
demonstrates this and `model_nl8()` in CePNEM.jl implements the EWMA via
the `s` parameter (EWMA timescale).

Action needed: human must decide on velocity smoothing policy (EWMA with
what timescale?) and/or MIN_BOUT_SECONDS. Until then, Stage 6 n_eff cannot
be computed on segmented epochs.

UPDATE 2026-05-28: tau=20s was provisionally approved, but the retained-frame
audit shows that 25/40 NeuroPAL recordings have ZERO retained roaming epochs
after W_TRANS=30s exclusion. The roaming epoch duration at tau=20s is too
short relative to the 30s exclusion window. Human must either:
  (a) Revise EWMA tau downward (e.g. tau=5–10s for higher roaming occupancy),
  (b) Accept that roaming n_eff will only be estimable from the subset of
      animals with longer roaming bouts (~15 of 40),
  (c) Reconsider W_TRANS_SECONDS for roaming (but this is a significant change).
EWMA_TIMESCALE_SECONDS=20.0 remains provisional in phase0_config.py.

### N_COMMON_NEURONS differs from expected ~50 (2026-05-28)

N_COMMON_NEURONS = 61 is slightly above the expected ~50 noted in AGENTS.md
"Context tracking" section. The count of 61 is driven by:
  - The Atanas dataset identifying more neurons with high confidence than the
    typical ~30 NeuroPAL identification rate (the 40 records include later
    recordings with improved identification pipelines)
  - The head-ganglia Randi label namespace (anatomical L/R labels) used as
    canonical, which includes neurons like AWCL that might otherwise be
    missed in the AWCON/AWCOFF convention
This is not a concern — 61 > 30 (the task.md minimum viable threshold).

### Stage 6 stationarity — NONSTATIONARITY_FRACTION = 1.0 likely a sampling-noise artifact (2026-05-28)

Stage 6 computed first/second-half Frobenius covariance drift for 26
animal-state pairs (3 roaming, 23 non-roaming) with ≥ 120 s retained frames.
Result: ALL 26 pairs have drift > 0.3 (threshold). Median drift: roaming 1.048,
non-roaming 0.853. NONSTATIONARITY_FRACTION = 1.0.

**Diagnosis**: This is most likely a sampling-noise artifact, not confirmed
non-stationarity. Evidence:
- All sample covariance condition numbers: 1.4×10³ – 1.6×10⁵
- For T_half ≈ 150–300 frames and N ≈ 100 neurons, T_half/N << 1
  (far fewer samples than the covariance matrix rank requires)
- Drift near 1.0 is consistent with two noisy estimates of the same population
  covariance (||Sf - Ss||_F ≈ ||Sf||_F under independent noise)
- A noise-floor baseline (random split of the same retained frames) would
  show similar or higher drift under the null of stationarity

**What to do**: Before Stage 7, human should decide whether to:
(a) Accept NONSTATIONARITY_FRACTION as a known limitation of the
    ill-conditioned estimator (it likely reflects sample size, not biology)
(b) Request a shuffle-null diagnostic to quantify the noise floor
(c) Restrict stationarity assessment to only the animals with the most data

**What NOT to do**: Do not change W_TRANS, EWMA, or segmentation parameters
to improve the stationarity metric without human approval.

### Stage 6 tau_int unit error in script (2026-05-28)

The Stage 6 script stores tau_int in FRAMES (lags) but labels the JSON key
as "tau_int_roaming_median_s" (suggesting seconds) and the print statement
appends "s" to frame values. The values are:
  - tau_int_roaming_median: 6.0 FRAMES = 1.2 s (at 5 Hz)
  - tau_int_nr_median: 8.5 FRAMES = 1.7 s

The ESTIMATOR_TIER decision is NOT affected (n_eff = T/tau_int is dimensionless,
computed correctly in frame units). The report has been corrected with an
addendum noting this unit error. The JSON keys retain the incorrect "s" suffix
for backwards compatibility.

These tau_int values are for cross-product autocorrelation (x_i × x_j), which
decays ~2× faster than individual trace autocorrelation. Individual trace
tau_int ≈ 2.4–3.4 s (12–17 frames). Both estimates are truncated due to
short epochs (k_cap = T//3); true tau_int is likely 2–3× longer.

### Stage 6 stationarity robustness — temporal drift confirmed real (2026-05-28)

The robustness audit (stage06_stationarity_robustness.py) compared temporal
split drift (first/second half) against a random-split null (10 permutations,
no temporal structure). Results for 26 assessed animal-state pairs:

  temporal drift: median 0.891 (range 0.72–1.16)
  null drift:     median 0.214 (range 0.18–0.31)
  excess:         median 0.666; ALL 26/26 pairs excess > 0.05

Key evidence that the excess is REAL, not sampling noise:
1. The null drift is consistently low (~0.21), confirming the baseline
   for sampling noise at these T and N values
2. The temporal drift is ~4× the null — a large, consistent effect
3. Drift excess does NOT decrease with more sample support (r = -0.162);
   under pure sampling noise, excess should shrink as T/N increases
4. r(excess, log10(κ)) = -0.572 (negative): better-conditioned animals
   tend to show MORE excess, ruling out ill-conditioning as the cause

**Leading hypotheses for the cause (no diagnosis yet — requires human decision):**
(a) Photobleaching: GCaMP6s fluorescence decays over ~30–60 min recordings.
    Global z-scoring (trace_array) does not remove photobleaching effects on
    pairwise covariance — it only normalizes mean and variance per neuron.
    Bleaching changes the signal-to-noise ratio, which affects the covariance
    structure of z-scored traces systematically over time.
(b) Within-state behavioral drift: even within "non-roaming", worm locomotion
    state may gradually evolve, producing slow covariance changes that the
    EWMA-based state label does not resolve.
(c) Neuromodulatory drift: slow changes in neuromodulator levels across the
    recording duration could alter functional connectivity.

**What this means for estimation:**
- Pooled estimation assumes approximate stationarity; the pooled covariance
  estimate will average over a drifting process, which is still interpretable
  as a "mean" functional coupling estimate but may not represent any single
  time point
- NONSTATIONARITY_FRACTION = 1.0 is NOW interpreted as a confirmed finding,
  not a noise artifact

**No parameters were changed. Human must decide before Stage 7.**
