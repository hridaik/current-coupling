# Phase 10B.4 — Co-Observation-Preserving Null
Date: 2026-06-15

## Method: Matched-Pair Null

For each key pair, identify a matched stratum of Class-4 pairs with similar
co-observation support (number of animals ± 5 where both neurons are present).
Report the empirical percentile of the key pair's |ΔΩ_ss| within this stratum.

This tests: are ADEL/PDF pairs high-ranked because they are well-co-observed,
or because they have genuinely higher state-dependent organization?

## Key Pair Co-observation Support

| Pair | n_coobs_animals | total_frames | |ΔΩ_ss| | Primary Rank |
|------|----------------|-------------|---------|-------------|
| ADEL–URYVR | 28 | 44790 | 0.0688 | 2 |
| ADEL–URYDL | 29 | 46390 | 0.0498 | 6 |
| ADEL–RMEL | 30 | 47989 | 0.0549 | 4 |
| RMEL–URYDL | 30 | 47989 | 0.0310 | 23 |
| RMEL–RMER | 34 | 54388 | 0.0254 | 38 |

## Matched-Pair Empirical Percentiles

| Pair | n_match_pairs | key_val | matched_median | empirical_pct | p_matched |
|------|--------------|---------|---------------|--------------|-----------|
| ADEL–URYVR | 981 | 0.0688 | 0.0053 | 0.999 | 0.001 |
| ADEL–URYDL | 1092 | 0.0498 | 0.0053 | 0.995 | 0.005 |
| ADEL–RMEL | 1241 | 0.0549 | 0.0052 | 0.998 | 0.002 |
| RMEL–URYDL | 1241 | 0.0310 | 0.0052 | 0.982 | 0.018 |
| RMEL–RMER | 1230 | 0.0254 | 0.0050 | 0.974 | 0.026 |

## Interpretation

If empirical_pct ≥ 0.95 for ADEL/PDF pairs, their high |ΔΩ_ss| is unlikely to be
explained by co-observation support alone.

STRONG: ADEL–URYVR and ADEL–URYDL are in the top tier of their co-observation-matched strata. Signal is not explained by co-observation support.
