# Coupling-Corrected PDF Enrichment

Scoring-object rows are extracted from `results/phase10f/coupling_corrected_enrichment.csv`; expected counts are computed from the same 61/1321 PDF density. Simple and degree-stratified permutation p-values for these coupling-corrected scoring objects were not saved or recomputed.

| Statistic | K | PDF count | Expected | OR | Fisher p | Simple perm p | Degree-strat p |
|---|---:|---:|---:|---:|---:|---|---|
| abs(DeltaOmega^B) = abs(DeltaOmega_ss + DeltaB) | 10 | 2 | 0.462 | 5.164 | 0.0744 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega_ss + 2DeltaB) | 10 | 2 | 0.462 | 5.164 | 0.0744 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega^B) = abs(DeltaOmega_ss + DeltaB) | 20 | 3 | 0.924 | 3.645 | 0.0610 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega_ss + 2DeltaB) | 20 | 2 | 0.924 | 2.295 | 0.2350 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega^B) = abs(DeltaOmega_ss + DeltaB) | 30 | 3 | 1.385 | 2.295 | 0.1575 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega_ss + 2DeltaB) | 30 | 3 | 1.385 | 2.295 | 0.1575 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega^B) = abs(DeltaOmega_ss + DeltaB) | 40 | 4 | 1.847 | 2.295 | 0.1087 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega_ss + 2DeltaB) | 40 | 3 | 1.847 | 1.675 | 0.2801 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega^B) = abs(DeltaOmega_ss + DeltaB) | 50 | 4 | 2.309 | 1.796 | 0.1961 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |
| abs(DeltaOmega_ss + 2DeltaB) | 50 | 4 | 2.309 | 1.796 | 0.1961 | not_available_not_computed_in_phase10f | not_available_not_computed_in_phase10f |

Drift-confounded pair exclusion rows were recomputed only because Phase 10F saved K=20 but not all requested K values. K=20 recomputation matched the Phase 10F summary for all three exclusions.

| Exclusion | K | Remaining N | ADEL-RMEL excluded | ADEL-URYVR excluded | ADEL-URYDL excluded | PDF count | Expected | OR | Fisher p |
|---|---:|---:|---|---|---|---:|---:|---:|---:|
| exclude_top_20_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 10 | 1301 | yes | no | no | 2 | 0.453 | 5.263 | 0.0720 |
| exclude_top_20_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 20 | 1301 | yes | no | no | 4 | 0.907 | 5.263 | 0.0107 |
| exclude_top_20_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 30 | 1301 | yes | no | no | 6 | 1.360 | 5.263 | 0.0017 |
| exclude_top_20_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 40 | 1301 | yes | no | no | 7 | 1.814 | 4.465 | 0.0016 |
| exclude_top_20_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 50 | 1301 | yes | no | no | 7 | 2.267 | 3.427 | 0.0059 |
| exclude_top_50_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 10 | 1271 | yes | no | no | 2 | 0.456 | 5.228 | 0.0728 |
| exclude_top_50_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 20 | 1271 | yes | no | no | 4 | 0.913 | 5.228 | 0.0109 |
| exclude_top_50_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 30 | 1271 | yes | no | no | 6 | 1.369 | 5.228 | 0.0018 |
| exclude_top_50_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 40 | 1271 | yes | no | no | 7 | 1.825 | 4.436 | 0.0016 |
| exclude_top_50_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 50 | 1271 | yes | no | no | 7 | 2.282 | 3.405 | 0.0061 |
| exclude_top_100_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 10 | 1221 | yes | no | no | 3 | 0.459 | 8.916 | 0.0087 |
| exclude_top_100_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 20 | 1221 | yes | no | no | 5 | 0.917 | 6.935 | 0.0016 |
| exclude_top_100_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 30 | 1221 | yes | no | no | 6 | 1.376 | 5.201 | 0.0018 |
| exclude_top_100_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 40 | 1221 | yes | no | no | 6 | 1.835 | 3.671 | 0.0081 |
| exclude_top_100_abs_DeltaB_pairs_then_rank_by_abs_DeltaOmega_ss | 50 | 1221 | yes | no | no | 6 | 2.293 | 2.837 | 0.0235 |
