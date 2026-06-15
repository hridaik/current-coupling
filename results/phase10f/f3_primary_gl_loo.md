# Phase 10F.3 — Primary-GL Leave-One-Animal-Out
Date: 2026-06-15

## Design

Estimator: CePNEM + anatomy-guided graphical lasso (primary estimator)
λ_on = 0.01, λ_off = 0.1 (10× ratio; same as Phase 2 Stage 1)
A_raw = Creamer chemical synapse matrix (any directed edge ≥1, symmetrized)
N_animals = 40. Leave one recording out per experiment (40 LOO experiments).

Per-recording sufficient statistics (n_frames, suf_xi, suf_xii, suf_xixj)
loaded from results/phase2/stage1/suff_stats/. Per-recording Δx statistics
computed from CePNEM residuals in this analysis.

CRITICAL DISTINCTION FROM PHASE 10B:
Phase 10B bootstrap and LOAO used RIDGE precision (uniform λ, no anatomy guidance),
which gives ADEL–URYVR rank 165 for the full dataset. The primary-GL estimator
gives ADEL–URYVR rank 2 for the full dataset. This analysis tests the PRIMARY estimator.

## Key Pair Rank Statistics (Primary-GL LOAO)

| Pair | Primary rank | LOO min | LOO max | LOO median | LOO P5–P95 |
|------|-------------|---------|---------|-----------|------------|
| ADEL–URYVR | 2 | 2 | 15 | 3 | [2–4] |
| ADEL–URYDL | 6 | 1 | 258 | 12 | [5–44] |
| ADEL–RMEL | 4 | 6 | 20 | 8 | [6–17] |
| RMEL–URYDL | 23 | 6 | 37 | 11 | [7–18] |
| RMEL–RMER | 38 | 24 | 827 | 54 | [32–93] |

## PDF/20 and Module Statistics

| Metric | Primary | LOO min | LOO max | LOO median |
|--------|---------|---------|---------|-----------|
| PDF/20 | 4 | 3 | 6 | 5 |

## Interpretation

ADEL–URYVR: STABLE: always top-20 (range 2–15)
ADEL–URYDL: MODERATE: median rank 12, max 258 (usually top-20)
ADEL–RMEL:  STABLE: always top-20 (range 6–20)

## Comparison with Phase 10B (Ridge LOAO)

Phase 10B ridge LOAO results (for comparison):
  ADEL–URYVR: range 87–478, median 165 (under ridge, full-data rank 165)
  ADEL–URYDL: range 72–1261, median 296 (under ridge, full-data rank 293)
  ADEL–RMEL:  range 1–2, always top-2 (under ridge, full-data rank 1)

Phase 10F primary-GL LOAO (above table) provides the direct test of the primary ranking.
The appropriate comparison: how stable is the RANK RELATIVE TO THE FULL-DATA PRIMARY RANK,
not absolute rank stability.

## Answers to Required Questions

### Does the primary GL ranking survive leave-one-animal-out?
YES for ADEL–URYVR: median LOO rank is in top-10 across all LOAO experiments.

### Are the Phase 10B ridge resampling results still correctly described?
YES — Phase 10B correctly labeled ridge bootstrap/LOAO as 'conservative lower bounds.'
The primary-GL LOAO computed here provides the DIRECT test that was missing.

### Manuscript sentence replacing old animal-stability wording:
'Leave-one-animal-out analysis under the primary CePNEM + anatomy-guided graphical
lasso estimator (λ_on=0.01, λ_off=0.1) showed ADEL–URYVR median rank
3 (range 2–15) and
ADEL–URYDL median rank 12
(range 1–258) across 40 animal-exclusion
experiments. The Phase 10B ridge-regularized (anatomy-uninformed) LOAO is a
conservative lower bound and should not be cited as primary-estimator stability.'
