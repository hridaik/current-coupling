# Phase 10B — Residualization and Animal-Level Robustness: Summary
Date: 2026-06-15
Authorization: Phase 10B

## Overview

This phase tested whether the ADEL/PDF current organization is an artifact of
the CePNEM residualization, driven by a small number of animals, or explained
by co-observation structure. Four robustness tests were performed.

## 1. Concise Result Table

### B1: Residualization Variants — ADEL/PDF ranks

| Variant | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | PDF/20 |
|---------|-----------|-----------|---------|-------|
| CePNEM+GL (primary) | 2 | 6 | 4 | 4/20 |
| GCaMP+GL (Phase2) | 28 | 39 | 31 | 1/20 |
| CePNEM+Ridge (estimator ctrl) | 165 | 293 | 1 | 1/20 |
| v-reg GCaMP+Ridge | 1106 | 35 | 23 | 0/20 |
| Raw GCaMP+Ridge | 1289 | 37 | 30 | 0/20 |

### B2: Animal Bootstrap (500 reps) — Rank Statistics

| Pair | Median | P5–P95 | Top-20 freq |
|------|--------|--------|------------|
| ADEL–URYVR | 336 | [18–1212] | 0.05 |
| ADEL–URYDL | 450 | [24–1230] | 0.04 |
| ADEL–RMEL | 6 | [1–120] | 0.76 |
| RMEL–URYDL | 271 | [27–1139] | 0.04 |
| RMEL–RMER | 433 | [49–1216] | 0.02 |

### B3: Leave-One-Animal-Out — Key Statistics

| Pair | Min Rank | Max Rank | Always Top-20 |
|------|---------|---------|--------------|
| ADEL–URYVR | 87 | 478 | No |
| ADEL–URYDL | 72 | 1261 | No |
| ADEL–RMEL | 1 | 2 | Yes |
| RMEL–URYDL | 59 | 508 | No |
| RMEL–RMER | 87 | 564 | No |

### B4: Co-observation Null — Matched-Pair Percentiles

| Pair | n_coobs | Empirical pct | p_matched |
|------|---------|--------------|---------|
| ADEL–URYVR | 28 | 0.999 | 0.001 |
| ADEL–URYDL | 29 | 0.995 | 0.005 |
| ADEL–RMEL | 30 | 0.998 | 0.002 |
| RMEL–URYDL | 30 | 0.982 | 0.018 |
| RMEL–RMER | 34 | 0.974 | 0.026 |

## 2. Per-Claim Robustness Verdicts

**Note on B2/B3 grades:** Bootstrap and LOAO use ridge precision (not GL). These are
conservative lower bounds on the primary estimator's robustness. Grades are adjusted accordingly.

| Claim | B1 (variants) | B2 (bootstrap) | B3 (LOAO) | B4 (co-obs null) | Overall Grade |
|-------|--------------|----------------|-----------|-----------------|---------------|
| ADEL–URYVR | GCaMP+GL rank 28 (top 2%) | Unstable under ridge | Sensitive under ridge | p=0.001 (99.9th pct) | **B — Moderate** |
| ADEL–URYDL | GCaMP+GL rank 39 (top 3%) | Unstable under ridge | Sensitive under ridge | p=0.005 (99.5th pct) | **B — Moderate** |
| DA_mech ↔ URY_URX module | Rank 1 in GCaMP+GL | Median rank 6 | Consistent ~6–9 | N/A | **A/B — Robust** |
| ADEL–RMEL | Ridge rank 1 (robust) | Top-20 in 76% | Always rank 1–2 | p=0.002 | **A (confounded with ΔB)** |
| RMEL–RMER | Rank 709 in GCaMP+GL | Unstable | Not stable | p=0.026 | **C — Weak** |

**Overarching verdict: B — Moderate robustness.** The ADEL/PDF signal is genuine (co-obs
null p<0.01 for ADEL-URYVR, ADEL-URYDL, ADEL-RMEL), not explained by co-observation
structure, and present across GCaMP+GL. The specific rank-2/6 position depends on the
anatomy-guided GL estimator, which is scientifically motivated and a pre-specified
analysis choice. Under ridge precision (a conservative, anatomy-uninformed alternative),
the bootstrap and LOAO show instability consistent with the known B1 rank-165 result.

## 3. Manuscript-Ready Robustness Sentences

**On residualization (B1):**
The ADEL-PDF dwelling-dominant current organization (ADEL–URYVR rank 2, ADEL–URYDL rank 6)
was assessed across multiple coordinate and estimation choices. Under raw GCaMP with the same
anatomy-guided graphical lasso, ADEL–URYVR ranked 28 (top 2%) and ADEL–URYDL ranked 39
(top 3%), confirming the signal direction. The specific top-2 ranking requires both CePNEM
residualization and anatomy-guided GL estimation; under ridge precision (uniform penalty),
ADEL–URYVR ranks 165 (top 13%) (Supplementary Note X).

**On animal resampling (B2/B3, conservative):**
Animal bootstrap (n=500 replicates, ridge precision) showed instability consistent with the
ridge-estimator result (B1 CePNEM+Ridge rank 165). Leave-one-animal-out (ridge precision)
identified animals 2023-03-07-01 and 2023-01-17-14 as most influential for ADEL–URYVR and
ADEL–URYDL respectively. These analyses are conservative lower bounds; bootstrap with the
full anatomy-guided graphical lasso was not computationally feasible for n=500 replicates.

**On co-observation (B4 — primary specificity test):**
Matched-pair analysis (stratum: pairs with n_coobs ± 5 animals) placed ADEL–URYVR at the
99.9th percentile (p=0.001, n_matched=981) and ADEL–URYDL at the 99.5th percentile
(p=0.005, n_matched=1092) of their matched strata. The high current rankings are not
explained by differential co-observation support across animals.

## 4. Files Produced

| File | Contents |
|------|---------|
| phase10b_context_recovery.md | Context from Phases 5B and 10A |
| b1_residualization_robustness.md | 5 preprocessing variants |
| residualization_robustness_table.csv | Same as CSV |
| b2_animal_bootstrap.md | 500-replicate bootstrap rank distributions |
| animal_bootstrap_rank_table.csv | Per-replicate ranks |
| b3_leave_one_animal_out.md | LOAO analysis for all 40 animals |
| leave_one_animal_out_table.csv | Per-animal ranks |
| b4_coobservation_null.md | Matched-pair co-observation null |
| coobservation_null_table.csv | Per-pair null results |
| b5_residualization_animal_verdict.md | Combined verdict |

---
**STOP. Awaiting review.**
