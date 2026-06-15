# Primary-GL LOAO Details

Source: `results/phase10f/primary_gl_loo_table.csv` and `results/phase10f/f3_primary_gl_loo.md`.

| Item | Median rank | Min rank | Max rank | Worst exclusion |
|---|---:|---:|---:|---|
| ADEL-URYVR | 3 | 2 | 15 | 2023-01-16-15 |
| ADEL-URYDL | 12 | 1 | 258 | 2023-01-17-14 |
| ADEL-RMEL | 8 | 6 | 20 | 2023-01-10-14 |
| RMEL-URYDL | 11 | 6 | 37 | 2023-01-10-14 |
| RMEL-RMER | 54 | 24 | 827 | 2023-01-17-14 |
| DA_mech<->URY_URX module | 3 | 1 | 4 | 2022-06-28-01;2023-01-09-22;2023-01-10-14;2023-01-23-08 |

Per-exclusion details are in `primary_gl_loo_details.csv` with one `per_exclusion` row per animal.

Influential exclusions by worst rank:
- ADEL-URYVR: 2023-01-16-15 (worst rank 15).
- ADEL-URYDL: 2023-01-17-14 (worst rank 258).
- ADEL-RMEL: 2023-01-10-14 (worst rank 20).
- RMEL-URYDL: 2023-01-10-14 (worst rank 37).
- RMEL-RMER: 2023-01-17-14 (worst rank 827).
- DA_mech<->URY_URX module: 2022-06-28-01;2023-01-09-22;2023-01-10-14;2023-01-23-08 (worst rank 4).

PDF count in top 20 across LOAO exclusions: range 3-6, median 5.0.
PDF enrichment p-values per exclusion were not computed in Phase 10F; p-value-defined loss of enrichment cannot be assessed from saved Phase 10F outputs.
Any exclusion reduces PDF count below the full-data count of 4: yes (2023-01-10-14).
Any exclusion removes ADEL-URYVR from top 20: no.
Any exclusion removes ADEL-URYDL from top 20: yes (2022-06-28-01;2023-01-10-14;2023-01-17-14).

Module-rank caveat: Phase 10F saved `DA_URY_min_rank`, defined in code as the minimum of the ADEL-URYVR and ADEL-URYDL pair ranks, not a recomputed full block-mean module rank for each LOAO exclusion.
