# Phase 4B.5 — Information-Limiting Interpretation Test
Date: 2026-06-12
Status: Executed per protocol (alignment enrichment was tested; result: no enrichment)

---

## Applicability Criterion

This analysis was specified as conditional:
> "Only if alignment enrichment is detected."

**The Phase 4B.3 alignment enrichment test found no enrichment.**
PDF-annotated pairs have AUROC = 0.426 for scalar alignment (p_perm = 0.978) —
meaning PDF pairs are, if anything, depleted among high-alignment pairs.

The information-limiting interpretation is therefore **not supported**.

This section reports the quantitative joint test for completeness, as specified
in the Phase 4B authorization, and to explicitly document the non-result.

---

## Recap: What Information-Limiting Correlations Require

Information-limiting correlations arise when two neurons:
1. Encode the **same behavioral variable** in the **same direction** (aligned encoding)
2. Share correlated variability

If both conditions hold, the shared variability cannot be removed by averaging across
trials/neurons — it directly limits population coding precision (Moreno-Bote et al., 2014).

For this mechanism to explain the PDF-associated state-dependent ΔQ signal, we would
require:
- Positive alignment (same-direction behavioral encoding) among PDF-annotated pairs
- PDF pairs occupying the upper tail of the alignment × |ΔQ| joint distribution

Neither condition is met.

---

## Joint Test: Alignment × |ΔQ_cepnem|

Joint score for each Class-4 pair:
```
S_ij = |c_v_i × c_v_j| × |ΔQ_ij|
```

This score captures pairs that are simultaneously behaviorally aligned AND show strong
state-dependent conditional reorganization.

**Results:**

| Group | Mean joint score | n |
|---|---|---|
| Bentley PDF pairs | 0.000225 | 61 |
| All Class-4 pairs | 0.000246 | 1321 |

**Permutation p = 0.464** (2000 permutations, testing whether PDF pairs have higher
joint score than random 61-pair subsets).

The PDF pairs have LOWER average joint score than the null expectation. This reflects
the combined effect of:
1. PDF pairs having lower alignment (b3: mean=0.008 vs null=0.021)
2. PDF pairs having modest but above-average |ΔQ| (AUROC = 0.556 in Phase 2)

These two effects partially offset, but the joint test is not significant.

### Top-Quartile Joint Occupancy

Pairs in the top quartile of BOTH |alignment| AND |ΔQ_cepnem| simultaneously:

| Group | n in both top quartiles | n total | Fraction |
|---|---|---|---|
| Bentley PDF | 12 | 61 | 19.7% |
| All Class-4 | 331 | 1321 | 25.1% |

PDF pairs are slightly under-represented in the joint top-quartile (19.7% vs 25.1% expected
under independence), consistent with the anti-alignment trend observed in b3.

---

## Explicit Statement

The following distinction is critical:

**Observed:** Bentley PDF-annotated Class-4 pairs show elevated |ΔQ_cepnem| (Phase 2:
AUROC = 0.556, p_deg = 0.023). The conditional dependence structure is stronger or more
reorganized for PDF-connected neuron pairs during the dwelling state.

**Not observed:** These same PDF-annotated pairs do NOT have higher behavioral encoding
alignment. The state-dependent conditional organization does not preferentially involve
same-direction velocity-encoding neurons.

**Conclusion regarding the information-limiting interpretation:**
**No support.**

The phrase "information-limiting correlations" should not be applied to this data.
The PDF-associated state-dependent signal is not, based on current evidence, consistent
with a mechanism that degrades population coding of velocity or locomotion state.

The complementary question — whether the signal instead involves cross-variable
coordination (e.g., velocity-positive ADEL coordinating with velocity-negative URYVR) —
is biologically plausible and discussed in b6.

---

## Limitations

1. This analysis uses the posterior median of c_v as the encoding weight. Uncertainty in
   the behavioral encoding estimate (recording-to-recording variance is moderate) could
   attenuate the true alignment signal.

2. The CePNEM model encodes instantaneous velocity, not the EWMA state score. A neuron
   that responds to the dwelling state via a different mechanism (e.g., threshold response
   to prolonged low velocity) might have near-zero c_v but strong state encoding.

3. With only 61 PDF pairs, the alignment enrichment test has limited power to detect
   small enrichment effects (AUROC ≈ 0.53–0.55). The null result rules out a strong
   effect but does not rule out a weak one.
