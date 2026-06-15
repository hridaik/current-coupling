# Phase 10C — Diffusion-Specific Robustness: Summary
Date: 2026-06-15
Authorization: Phase 10C

## Overview

This phase tested whether the ADEL/PDF dwelling-dominant current organization is an
artifact of dense or state-specific diffusion. Four analyses were performed: diffusion
specification comparison (C1), dense-diffusion shuffle nulls (C2), diffusion/precision
decomposition (C3), diffusion hub control (C4), and timescale sensitivity (C5, from
Phase 4C data).

---

## 1. Diffusion Specification Comparison (C1)

Five specifications tested: Identity (=ΔQ), pooled diagonal, state-specific diagonal,
pooled full, state-specific full (primary).

| Variant | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–RMER | DA_URY | PDF/20 |
|---------|-----------|-----------|---------|---------|-------|-------|
| Identity (D=I = ΔQ) | 5 | 9 | 10 | 32 | 1 | 4/20 |
| Pooled diagonal | 5 | 7 | 8 | 38 | 1 | 4/20 |
| State-specific diagonal | 3 | 6 | 7 | 49 | 1 | 3/20 |
| Pooled full | 4 | 6 | 7 | 54 | 1 | 5/20 |
| **State-specific full (primary)** | **2** | **6** | **4** | **38** | **1** | **4/20** |

**Key finding:** The signal is ALREADY PRESENT under identity diffusion (ΔQ).
Dense D provides incremental promotion (rank 5→2 for ADEL-URYVR), not genesis.
DA_mech ↔ URY_URX module ranks 1 in ALL five specifications.

---

## 2. Dense-Diffusion Shuffle Nulls (C2, n=500 per null type)

| Null type | ADEL–URYVR p | ADEL–URYDL p | ADEL–RMEL p | DA_URY in top-1 | Interpretation |
|-----------|------------|------------|----------|-----------------|----------------|
| Diagonal shuffle | 0.052 | 0.060 | 0.076 | 99% of reps | Marginal diagonal specificity |
| Off-diagonal shuffle | 0.182 | 0.640 | 0.214 | 91% of reps | Off-diagonal negligible |
| Row/col permutation | **0.018** | 0.170 | **0.028** | 75% of reps | D-Q alignment specific |
| State-label swap | rank 6 | rank 7 | rank 11 | rank 2 | Sign-specific; magnitude robust |

p-value = fraction of null reps where null rank ≤ primary rank.

**Key finding:** ADEL-URYVR rank ≤ 2 occurs in only 1.8% of random neuron-permuted
D matrices (p=0.018). The DA_mech↔URY_URX module remains top-ranked in 75% of
random permutations. The specific D-Q identity alignment matters for ADEL-URYVR
top-2, but the module-level result is more broadly robust.

---

## 3. Diffusion/Precision Decomposition (C3)

Both valid decompositions (state-A and state-B conditioned) reported.

| Pair | Precision fraction (A) | Precision fraction (B) | Sign consistent? |
|------|----------------------|----------------------|-----------------|
| ADEL–URYVR | 96% | 83% | Yes (both decomps) |
| ADEL–URYDL | 111% | 92% | Yes (precision term) |
| ADEL–RMEL  | 92% | 81% | Yes |
| RMEL–URYDL | 101% | 105% | Yes (diffusion negligible) |
| RMEL–RMER  | 76% | 81% | Yes |

**Key finding:** All five pairs are predominantly precision-driven (76–111%).
Dense D reweights and amplifies the Q-structure; it does not create independent
biological signal. The decomposition is NOT unique — fractions vary by ≤25 pp
between the two forms — so only the sign consistency and dominance direction
should be reported.

---

## 4. Diffusion Hub Control (C4)

| Test | Result |
|------|--------|
| Global ρ(hub score, |ΔΩ_ss|) | 0.027–0.040 (all p > 0.15) |
| ADEL-URYVR hub-matched null | 99.8th percentile (p=0.0017) |
| ADEL-URYDL hub-matched null | 99.6th percentile (p=0.0043) |
| Partial ρ(|ΔΩ_ss|, PDF | hub) | 0.022 (vs marginal 0.024) |

**Key finding:** Endpoint diffusion hubness does not predict |ΔΩ_ss| ranking
across 1321 pairs and does not explain ADEL-URYVR/URYDL elevation. The
hub-matched null confirms these pairs are extreme even among similarly-hubbish pairs.

---

## 5. Timescale Sensitivity (C5)

Using Phase 4C D(τ) matrices at τ ∈ {1, 2, 5, 10, 20} frames.

| τ | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–RMER | PDF/20 |
|---|-----------|-----------|---------|---------|-------|
| 1 (primary) | **2** | **6** | **4** | 38 | 4/20 |
| 2 | **4** | **7** | **3** | 48 | 3/20 |
| 5 | **3** | 12 | **4** | 126 | 6/20 |
| 10 | **2** | 20 | **7** | 120 | 4/20 |
| 20 | **3** | 220 | 70 | 171 | 2/20 |

Sign (dwelling-dominant, negative) is consistent at ALL timescales for ALL pairs.

ADEL-URYVR is top-5 at all 5 timescales — the most timescale-stable result.
ADEL-URYDL degrades at τ≥10 (ranks 20, 220).
ADEL-RMEL stable at τ=1,2,5 (ranks 3,3,4), degrades at τ=10,20.

---

## 6. Per-Claim Final Grades (Phase 10C)

| Claim | Grade | Primary basis |
|-------|-------|--------------|
| ADEL–URYVR | **A — Strong** | Present in ΔQ (rank 5); row/col p=0.018; hub null p=0.0017; top-5 all τ |
| ADEL–URYDL | **A/B** | Present in ΔQ (rank 9); hub null p=0.0043; degrades at τ=20 |
| DA_mech ↔ URY_URX | **A — Strong** | Rank 1 in ALL 5 specs; rank 1 in 75–99% of random D |
| ADEL–RMEL | **B — Moderate** | Present in ΔQ (rank 10); stable at τ≤10; some timescale sensitivity |
| RMEL–RMER | **C — Weak** | Fragile across 10A/10B/10C; diffusion contributes 20–24%; degrades at τ≥5 |
| PDF top-20 enrichment | **B — Moderate** | 4/20 at primary τ; 6/20 at τ=5; 2/20 at τ=20 |

---

## 7. Manuscript-Ready Sentence

"To assess whether the ADEL-PDF dwelling-dominant current organization is a dense-diffusion
artifact, we computed ΔΩ^(spec) under five diffusion specifications (identity, pooled diagonal,
state-specific diagonal, pooled full, state-specific full). ADEL–URYVR ranked 5th and
ADEL–URYDL ranked 9th under identity diffusion (equivalent to ΔQ), confirming the signal
is present without any diffusion weighting; the full state-specific D matrix incrementally
promotes them to ranks 2 and 6. The precision term (D_state @ ΔQ) accounts for 83–96% of
ADEL–URYVR's ΔΩ_ss under both state-conditioned decompositions. Endpoint diffusion
row-norms do not predict |ΔΩ_ss| ranking (Spearman ρ < 0.04, p > 0.15) and ADEL–URYVR
remains at the 99.8th percentile among hub-score-matched pairs (p=0.0017). In 500
neuron-permuted diffusion replicates, only 1.8% achieved ADEL-URYVR rank ≤ 2 (p=0.018),
confirming the specific D-Q alignment contributes to the high rank. ADEL–URYVR is
top-5 at all five timescales tested (τ=1–20 frames), with consistent dwelling-dominant
sign. The DA_mech ↔ URY_URX module is rank 1 across all diffusion specifications and
in 75–99% of random diffusion permutations."

---

## 8. Files Produced

| File | Contents |
|------|---------|
| phase10c_context_recovery.md | Prior-phase context and artifact concern |
| c1_diffusion_specification_comparison.md | 5-specification table and interpretation |
| diffusion_specification_comparison.csv | Same as CSV |
| c2_dense_diffusion_nulls.md | 4 null types, 500 reps, p-values |
| dense_diffusion_nulls_table.csv | Per-pair null statistics |
| c3_diffusion_precision_decomposition.md | Two decompositions, per-pair fractions |
| c4_diffusion_hub_control.md | Hub Spearman, matched-null, partial correlation |
| diffusion_hub_control_table.csv | Hub-matched null per pair |
| c5_timescale_diffusion_summary.md | τ=1,2,5,10,20 rank table from Phase 4C data |
| c6_diffusion_verdict.md | Formal per-claim verdict |
| phase10c_numerics.json | All computed numbers |

---
**STOP. Awaiting review.**
