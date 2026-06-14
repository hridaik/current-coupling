# Phase 4B.3 — Alignment Enrichment
Date: 2026-06-12

---

## Question

Are Bentley PDF-annotated Class-4 pairs unusually aligned in behavioral encoding?

---

## Method

**AUROC enrichment test:** For each annotation category, compute the AUROC of the
binary annotation label against the continuous alignment score (scalar or cosine),
using a permutation null (2000 permutations, simple random shuffle of annotation labels).

AUROC > 0.5 would indicate annotated pairs have higher alignment than unannotated pairs.

Three annotation categories tested:
- Bentley PDF (n=61, 4.6% of Class-4)
- Bentley serotonin (n=33, 2.5%)
- Bentley combined PDF+serotonin (n=94, 7.1%)

Note: Randi unc-31 annotation is unavailable in full (funatlas H5 file not present;
only 8 pairs recoverable from stage2 top50 — insufficient for a reliable enrichment test).

---

## Results

### Scalar Alignment (c_v product)

| Annotation | n | Mean align (pos) | Mean align (neg) | AUROC | p_perm | Null mean |
|---|---|---|---|---|---|---|
| Bentley PDF | 61 | +0.0079 | +0.0208 | **0.426** | 0.978 | 0.5005 |
| Bentley serotonin | 33 | +0.0162 | +0.0203 | 0.438 | 0.894 | 0.5004 |
| Bentley combined | 94 | +0.0108 | +0.0209 | 0.428 | 0.987 | 0.5003 |

### Cosine Alignment (3D)

| Annotation | n | AUROC | p_perm | Null mean |
|---|---|---|---|---|
| Bentley PDF | 61 | 0.454 | 0.875 | ~0.500 |
| Bentley serotonin | 33 | 0.524 | 0.299 | ~0.500 |
| Bentley combined | 94 | 0.478 | 0.754 | ~0.500 |

---

## Interpretation

**No alignment enrichment is detected for any annotation category.**

All AUROC values are below 0.5. For Bentley PDF pairs specifically:
- Scalar AUROC = 0.426, p_perm = 0.978 — the PDF pairs have LOWER alignment than chance.
- Cosine AUROC = 0.454, p_perm = 0.875 — similarly depleted.

The mean scalar alignment among PDF pairs (0.0079) is lower than among non-PDF pairs
(0.0208). This pattern is consistent across both scalar and cosine metrics.

**The Bentley PDF-annotated Class-4 pairs do NOT preferentially connect neurons with
aligned velocity encoding.**

In fact, the directional signal is the opposite: PDF pairs appear slightly enriched among
pairs with LOW or NEGATIVE alignment (anti-aligned neurons). The effect is not significant
in either direction, but the trend is clear: the state-dependent conditional organization
indexed by the PDF annotation does not require same-direction behavioral tuning.

### Why Might PDF Pairs Tend Toward Anti-Alignment?

The ADEL → URY circuit provides a biological explanation. ADEL is roaming-active
(velocity-positive, c_v=+0.215) while URYVR is dwelling-active (velocity-negative,
c_v=−0.068). Their state-dependent conditional coupling during dwelling — the strongest
PDF signal — involves neurons with COMPLEMENTARY behavioral roles:
- During roaming: ADEL is active, URYVR is suppressed; they are conditionally decoupled.
- During dwelling: ADEL activity declines, URYVR may increase; conditional structure emerges.

This complementarity is compatible with a modulation function: ADEL-pdf-1 signaling may
serve to coordinate sensory (URY: O2 detection) with mechanosensory (ADEL: touch) input
during the dwelling phase, precisely BECAUSE these neurons have different behavioral tuning.

---

## Comparison with Null

The permutation null distribution for AUROC is centered at 0.50 with std ≈ 0.037 (PDF)
to 0.051 (serotonin). All observed AUROCs fall well below the null mean:
- PDF: observed=0.426, null mean=0.501 — 2.0 std BELOW null
- This is the opposite tail from what an enrichment test would flag.

**Result: No enrichment. If anything, a (non-significant) depletion of alignment
among PDF-annotated pairs.**

---

## Limitations

1. Randi unc-31 annotation could not be reconstructed (funatlas H5 unavailable without h5py).
   Only 8 of 108 Randi pairs were available from the stage2 top50; these are insufficient
   for a meaningful enrichment test.

2. The CePNEM behavioral encoding weights represent epoch-averaged posterior medians.
   Recording-level variance in encoding (across the 32–39 recordings per neuron) is not
   propagated into the alignment metric.

3. CePNEM encodes instantaneous behavioral covariates (velocity at each timepoint), not
   the EWMA behavioral state score used for dwelling/roaming classification. The c_v
   weight reflects velocity tuning, which is correlated with but not identical to state.
