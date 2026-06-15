# Annotation Null Details

Statistic: `|DeltaOmega_ss|`. Primary K: 20. Observed PDF count: 4/20; annotated PDF pairs in universe: 61/1321.
Permutations: 2000; random seed: 20260615. Recomputed interval diagnostics matched the saved Phase 10F table at displayed precision.

| Null | p-value | Null mean | Null 95% interval | Degree/binning definition |
|---|---:|---:|---|---|
| simple_label_shuffle | 0.0115 | 0.945 | [0, 3] | none |
| Araw_degree_stratified | 0.0300 | 1.209 | [0, 4] | A_raw structural endpoint degree sum |
| C4_degree_stratified | 0.0085 | 0.906 | [0, 3] | C4 endpoint degree sum |

Exact logic from `scripts/phase10f_analysis.py`:
- Simple null: uniformly choose 61 PDF-labeled pair indices among the 1321 C4 pairs.
- Araw stratified null: `pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]`; 10 percentile bins; PDF labels shuffled within each bin.
- C4 stratified null: `pair_c4_deg = c4_degree[ii_c4] + c4_degree[jj_c4]`; 10 percentile bins; PDF labels shuffled within each bin.
- Araw degree used the Creamer chemical synapse matrix, thresholded at any directed edge >=1 and symmetrized before row-sum degree calculation.
- Source/target direction was not preserved; Bentley directed PDF rows were collapsed to undirected pair labels before shuffling.
- The Class-4/off-reference universe was preserved in every null.
