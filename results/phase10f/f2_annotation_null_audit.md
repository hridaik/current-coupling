# Phase 10F.2 — Annotation Null Audit
Date: 2026-06-15

## 1. Audit of Prior Wording

### Problem 1: Wrong ranking object for p=0.008

The 'degree-permutation p = 0.008' cited in Phase 10D context recovery and
propagated to Phase 10E comes from Stage 4A (Phase 2) where ranking was by
|ΔQ| (precision-only), NOT by |ΔΩ_ss|. No degree-preserving null was run
under |ΔΩ_ss| ranking in Phase 10D (which only computed Fisher exact tests).

Stage 4A (|ΔQ| ranking, N_PERM=1000, K=20):
  p_simple_perm = 0.006  (uniform label shuffle)
  p_degree_perm = 0.008  (stratified by A_raw degree, 10 bins)

These values must NOT be cited as applying to |ΔΩ_ss| ranking.

### Problem 2: Misdescription of null type

The Phase 10E e4_methods_text.md states:
  'degree-permutation p-values... computed from 1000 permutations of
   Class-4 pair labels, preserving annotation set size'

This is wrong in two ways:
(a) It describes only a simple label shuffle (preserving count). Stage 4A
    used a DEGREE-STRATIFIED shuffle (stratified within 10 bins of A_raw
    structural degree sum). These are different.
(b) It was computed on |ΔQ| ranking, not |ΔΩ_ss|.

## 2. Corrected Null Implemented Here (N_PERM=2000, under |ΔΩ_ss|)

Three null distributions at K ∈ {10, 20, 30, 40, 50}:

**Null 1 — Simple label shuffle**: Randomly reassign PDF annotation to any
61 of 1321 C4 pairs, uniformly. No degree constraint.

**Null 2 — A_raw degree-stratified** (equivalent to Stage 4A, now under |ΔΩ_ss|):
Pairs binned into 10 strata by (A_raw_degree_i + A_raw_degree_j).
PDF annotation labels shuffled WITHIN each stratum.
A_raw = Creamer chemical synapse matrix (any directed edge ≥1, symmetrized).
This is correctly called 'A_raw degree-stratified label permutation', not
'degree-preserving.' It controls for annotation propensity correlated with
structural connectivity degree.

**Null 3 — C4-degree stratified**: Pairs binned by (C4_degree_i + C4_degree_j)
where C4_degree_i = number of C4 pairs neuron i is part of.
This controls for neurons that appear in many C4 pairs being more likely
annotated by density alone.

## 3. Results

### Observed Fisher test (|ΔΩ_ss| ranking, K=20, pre-specified primary):
  count = 4/20, OR = 5.16, Fisher p = 0.0114

### Null p-values under |ΔΩ_ss| (this Phase 10F, N=2000 permutations):

| K | Observed | OR | p_fisher | p_simple | p_Araw_deg | p_C4deg |
|---|----------|-----|---------|---------|-----------|--------|
| 10 | 3/10 | 8.852 | 0.0089 | 0.0130 | 0.0175 | 0.0125 |
| 20 | 4/20 | 5.164 | 0.0114 | 0.0115 | 0.0300 | 0.0085 |
| 30 | 6/30 | 5.164 | 0.0019 | 0.0025 | 0.0045 | 0.0005 |
| 40 | 8/40 | 5.164 | 0.0003 | 0.0005 | 0.0020 | 0.0000 |
| 50 | 9/50 | 4.534 | 0.0003 | 0.0005 | 0.0010 | 0.0000 |

### Comparison with Stage 4A (|ΔQ| ranking):
  Stage 4A K=20: p_simple=0.006, p_Araw_deg=0.008 (under |ΔQ|)
  Phase 10F K=20: p_simple=0.0115, p_Araw_deg=0.0300 (under |ΔΩ_ss|)

## 4. Answers to Required Questions

### Was prior wording correct?
NO — two errors:
(1) p=0.008 was from |ΔQ| ranking, not |ΔΩ_ss|.
(2) The null was degree-stratified (not just 'preserving annotation set size').

### Corrected wording:
'PDF annotation enrichment at the pre-specified K=20 was assessed by Fisher
exact test (one-sided greater) and a degree-stratified label permutation null
(N=2000, 10 strata of structural connectivity degree sum; Bentley A_raw proxy).
The observed count of 4/20 PDF pairs in the top-20 by
|ΔΩ_ss| corresponds to OR=5.16 (Fisher p=0.0114;
p_simple=0.0115, p_Araw_deg=0.0300,
p_C4deg=0.0085 from permutation nulls under |ΔΩ_ss|).'

### Does PDF top-K enrichment survive the degree-stratified null?
YES — p_Araw_deg=0.0300 < 0.05 at primary K=20 under |ΔΩ_ss|.

### Important note on Stage 4A
Stage 4A computed the degree-stratified null on |ΔQ| ranking (coordinate 'cepnem'),
which ranks by precision change only. Stage 4A's OR=5.46 and Fisher p=0.011 are
for |ΔQ| ranking. Phase 10F uses |ΔΩ_ss| ranking (OR may differ slightly because
rankings differ). Both are valid; the primary ranking object for the manuscript is
|ΔΩ_ss|, so Phase 10F values should be cited for enrichment under the primary object.
