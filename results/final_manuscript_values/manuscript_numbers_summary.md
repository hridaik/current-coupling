# Manuscript Numbers Summary

## 1. Drift Scaling/Sign Audit
ADEL-URYVR remains rank 2 -> 2 -> 2; sign stays negative.
ADEL-URYDL remains high-ranked: 6 -> 3 -> 10; sign stays negative.
ADEL-RMEL is drift-sensitive: 4 -> 18 -> 837; sign stays negative.
DA_mech<->URY_URX module ranks 2 -> 1 -> 1 using Phase10A block aggregation.

## 2. Degree-Stratified PDF Annotation Null
At K=20 under |DeltaOmega_ss|, PDF count is 4/20; Fisher p=0.0114; simple permutation p=0.0115; Araw degree-stratified p=0.0300; C4-degree-stratified p=0.0085 (N=2000, seed 20260615).
Araw null mean count=1.209 with 95% interval [0, 4]; binning used 10 bins of symmetrized structural endpoint degree sum.

## 3. Primary-GL Leave-One-Animal-Out
ADEL-URYVR median rank 3 (range 2-15); worst exclusion 2023-01-16-15.
ADEL-URYDL median rank 12 (range 1-258); worst exclusion 2023-01-17-14.
ADEL-RMEL median rank 8 (range 6-20); RMEL-RMER median rank 54 (range 24-827).
PDF top-20 counts range 3-6; per-exclusion p-values and top-20 overlaps were not computed in Phase 10F.

## 4. Coupling-Corrected Enrichment
Under |DeltaOmega_ss + DeltaB| at K=20: PDF count=3/20, expected=0.924, OR=3.645, Fisher p=0.0610.
Under |DeltaOmega_ss + 2DeltaB| at K=20: PDF count=2/20, expected=0.924, OR=2.295, Fisher p=0.2350.
After excluding top-|DeltaB| pairs, K=20 Fisher results match Phase 10F: top-20 exclusion p=0.0107, top-50 p=0.0109, top-100 p=0.0016; ADEL-RMEL is excluded under all three, ADEL-URYVR and ADEL-URYDL are not.

## 5. Required Manuscript Wording Updates
Use Phase 10F annotation-null values under |DeltaOmega_ss|, not the older |DeltaQ| degree-permutation p=0.008.
Describe the annotation null as degree-stratified label permutation in 10 bins of endpoint degree sum; do not call it a generic annotation-count-preserving shuffle.
State the discrete-time D/B convention and add the continuous-time +2DeltaB sensitivity note, especially the ADEL-RMEL demotion.
Use primary-GL LOAO numbers for animal stability; keep ridge LOAO as a conservative lower bound only.

Missing values: coupling-corrected simple/degree-stratified permutation p-values were not saved and were not recomputed; LOAO per-exclusion enrichment p-values and top-20 overlaps were not computed in Phase 10F.
