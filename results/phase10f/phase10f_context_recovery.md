# Phase 10F — Pre-Submission Audit: Context Recovery
Date: 2026-06-15
Authorization: Phase 10F

---

## 1. Current Object Used in Manuscript

Primary ranking object:
  ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell

Source files:
  - D_roam, D_dwell: results/phase3d/D_roam_cepnem.npy, D_dwell_cepnem.npy
  - Q_roam, Q_dwell: results/phase2/stage1/precision/Q_cepnem_{roam,dwell}_conf.npy
  - ΔΩ_ss: results/phase3d/DO_state_cep_full.npy  (= D_r @ Q_r - D_d @ Q_d, verified)

Coupling-corrected ranking:
  ΔΩ^B = ΔΩ_ss + ΔB = ΔΩ_ss + (B_roam − B_dwell)
Source: results/phase10a/DO_B.npy, DeltaB.npy

---

## 2. Diffusion D Estimation Convention

**Convention: D_s = Cov(Δx | state s)**

From Phase 3D documentation:
  "Empirical diffusion D_s = Cov(Δx | state s) estimated using consecutive same-state
   first-differences, pooled across all 40 recordings."

D_s is the DISCRETE-TIME empirical covariance of the first-difference process.
  - Δx_t = x_{t+1} - x_t (consecutive frames within same state)
  - D_s = (1/T_s) Σ_t (Δx_t - mean_Δx)(Δx_t - mean_Δx)^T

Key values (CePNEM, diagonal):
  - D_roam diagonal mean = 0.418, range [0.269, 0.613]
  - D_dwell diagonal mean = 0.399, range [0.260, 0.510]
  - D is a FULL 61×61 matrix (off-diagonal mean abs = 0.006, ~1.5% of diagonal)

D_s is NOT divided by 2Δt. It is the raw per-frame noise covariance.

Continuous-time relationship:
  D_disc = Cov(Δx) ≈ 2 D_cont Δt
  Therefore D_cont = D_disc / (2Δt)

---

## 3. Drift B Estimation Convention

**Convention: B_s from discrete-time regression Δx_t = B_s x_t + ε_t**

From Phase 10A script:
  - Model: Δx_t = B_s x_t + ε_t (discrete-time increment drift)
  - B_s[i,j]: how much neuron j's current value drives Δx_i
  - Fitted by ridge OLS: B_s = XtdX_s.T @ (XtX_s + λI)^{-1}
  - Ridge lambda = 1% of median pooled XtX diagonal (~277 in actual run)
  - B is dimensionless (Δx and x have same units)

Key values:
  - ||B_roam||_F  = 1.8514
  - ||B_dwell||_F = 1.6438
  - ||ΔB||_F      = 0.6275
  - ||ΔB||/||B_roam|| = 0.3389

Continuous-time relationship:
  B_disc ≈ A_cont × Δt
  Therefore A_cont = B_disc / Δt

---

## 4. Coupling Correction Formula and Compatibility

Phase 10A computed:
  ΔΩ^B = ΔΩ_ss + ΔB = (D_r Q_r − D_d Q_d) + (B_roam − B_dwell)

**Discrete-time dimensional analysis:**
  - D_disc Q: [x]^2 × [x]^{-2} = dimensionless
  - B: Δx / x = dimensionless
  - Both terms are dimensionless → compatible units in discrete time ✓

**Continuous-time interpretation:**
  - D_cont Q = (D_disc / 2Δt) Q → D_disc Q / (2Δt)  [units: 1/time]
  - A_cont = B / Δt  [units: 1/time]
  - Continuous-time Ω = D_cont Q + A_cont

  Ratio of coupling term to D Q term in continuous time:
    A_cont / (D_cont Q) = [B/Δt] / [D_disc Q / (2Δt)] = 2B / (D_disc Q)
  
  In discrete-time formula:
    B / (D_disc Q) [weight ratio is 1× not 2×]
  
  **This means Phase 10A underweights the B term by 2× relative to the
  continuous-time formula. The continuous-time equivalent would be:**
    ΔΩ^B_cont ∝ ΔΩ_ss + 2 ΔB  [in discrete units]

  For ADEL-URYVR (|ΔB| rank 370, ΔB≈0): No practical difference.
  For ADEL-RMEL (|ΔB| rank 1, ΔB large): The 2× factor matters substantially.

---

## 5. Annotation Null Currently Described

**In Phase 10E e4_methods_text.md:**
"Degree-permutation p-values for the primary K=20 test were computed from 1000
permutations of the 1321 Class-4 pair labels, preserving annotation set size, to
control for annotation density effects."

This description is imprecise for two reasons:

1. **Wrong ranking object**: The "degree-permutation p = 0.008" (reported in Phase 10D
   context recovery and propagated to Phase 10E) was computed in Stage 4A using
   ranking by |ΔQ| (precision-only), NOT by |ΔΩ_ss|. No degree-preserving null
   was run under |ΔΩ_ss| ranking in Phase 10D.

   Stage 4A result for |ΔQ| ranking:
   - p_simple_perm = 0.006 (1000 perms, uniform label shuffle)
   - p_degree_perm = 0.008 (1000 perms, degree-stratified within 10 bins of A_raw degree)

2. **Wrong null description**: The null used in Stage 4A is NOT a simple "label shuffle
   preserving annotation set size." It is a **degree-stratified label permutation**:
   pairs are binned into 10 strata by (A_raw_degree_i + A_raw_degree_j), and labels
   are shuffled within each stratum. This controls for the confound that neurons with
   high structural connectivity may be more likely to be PDF-annotated AND may have
   higher |ΔΩ_ss| values.

**Action required**: Run degree-stratified permutation null under |ΔΩ_ss| ranking
and update wording throughout. Also implement a C4-degree-stratified null as a
complementary test.

---

## 6. Animal Resampling Estimator (Phase 10B)

Phase 10B bootstrap and LOAO used **ridge-regularized precision** (uniform penalty,
no anatomy guidance). This is the CePNEM+Ridge variant, NOT the primary estimator.

Key distinction from primary CePNEM+GL:
- Ridge: uniform λ = 5% of mean diagonal of Σ_s (anatomy-uninformed)
- Primary GL: λ_on = 0.01 (on-reference), λ_off = 0.10 (off-reference), 10× ratio
- Under CePNEM+Ridge: ADEL-URYVR rank 165, ADEL-URYDL rank 293

Phase 10B properly labeled this as a "conservative lower bound."

Essential 3 requires: run LOAO under the PRIMARY CePNEM+GL estimator
(λ_on=0.01, λ_off=0.10, same A_raw adjacency as Phase 2 Stage 1).

---

## 7. Phase 10E Claims That May Require Revision

From phase10e/e3_results_text.md and e4_methods_text.md:

**Claim 1**: "degree-permutation p = 0.008"
- Status: INCORRECT RANKING OBJECT. This p was from |ΔQ| ranking, not |ΔΩ_ss|.
- Fix: Run under |ΔΩ_ss| and report new value.

**Claim 2**: "degree-permutation p-values... computed from 1000 permutations of
  Class-4 pair labels, preserving annotation set size"
- Status: DESCRIPTION UNDERSTATES THE NULL. Stage 4A used degree-stratified permutation.
- Fix: Accurately describe as "degree-stratified label permutation (10 A_raw degree bins)."

**Claim 3** (Phase 10B): "Animal bootstrap... ridge precision"
- Status: CORRECTLY LABELED as conservative lower bound. No change needed.

**Claim 4**: Animal-level stability of primary GL ranking
- Status: Not tested. Phase 10B only tested ridge.
- Fix: Run LOAO under primary GL (Essential 3).

---

## 8. Key Pair Ranks Under All Scoring Objects

| Pair | |ΔΩ_ss| rank | |ΔΩ^B| rank | |ΔQ| rank | |ΔΩ_ss| value |
|------|------------|-----------|----------|-------------|
| ADEL–URYVR | 2 | 2 | 5 | −0.0688 |
| ADEL–URYDL | 6 | 3 | 9 | −0.0498 |
| ADEL–RMEL  | 4 | 18 | 10 | −0.0549 |
| RMEL–URYDL | 23 | 168 | 16 | −0.0310 |
| RMEL–RMER  | 38 | 371 | 32 | −0.0254 |

All from Phase 10A summary (1321 Class-4 pairs).

---

## 9. Files to Produce in Phase 10F

| File | Analysis |
|------|---------|
| phase10f_context_recovery.md | This file |
| f1_drift_scaling_sign_audit.md | Essential 1 |
| drift_scaling_keypair_table.csv | Essential 1 |
| f2_annotation_null_audit.md | Essential 2 |
| degree_preserving_annotation_null.csv | Essential 2 |
| f3_primary_gl_loo.md | Essential 3 |
| primary_gl_loo_table.csv | Essential 3 |
| f4_coupling_corrected_enrichment.md | Optional |
| coupling_corrected_enrichment.csv | Optional |
| phase10f_summary.md | Final verdict |
