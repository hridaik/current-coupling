# Phase 4B — Final Summary
Date: 2026-06-12
Authorization: Phase 4B

---

## The Question

Do PDF-associated state-dependent conditional links preferentially connect neurons that
encode the same behavioral variable in the same direction?

---

## Key Findings

### 1. Do PDF-associated links preferentially connect neurons with aligned behavioral encoding?

**Answer: No. Grade A — No support.**

Bentley PDF-annotated Class-4 pairs (n=61) show scalar alignment AUROC = 0.426,
p_perm = 0.978. The PDF pairs have LOWER mean alignment (0.008) than non-PDF pairs
(0.021). The cosine alignment (3D behavioral vector) shows the same pattern:
AUROC = 0.454, p_perm = 0.875.

**The PDF-associated conditional organization does not preferentially connect
neurons with aligned velocity or behavioral encoding.**

The result is in the opposite direction of enrichment: PDF pairs appear to preferentially
connect neurons with complementary or anti-aligned behavioral encoding.

| Test | AUROC | p_perm | Direction |
|---|---|---|---|
| PDF scalar alignment | 0.426 | 0.978 | Depletion (opposite of enrichment) |
| PDF cosine alignment | 0.454 | 0.875 | Depletion |
| Serotonin scalar | 0.438 | 0.894 | Depletion |
| Combined scalar | 0.428 | 0.987 | Depletion |

---

### 2. Do the strongest state-dependent links preferentially connect aligned neurons?

**Answer: No. Grade A — No support.**

Top-20 |ΔQ_cepnem| pairs: mean alignment = 0.018, p_perm = 0.544 (not significant).
Top-50 |ΔQ_cepnem| pairs: mean alignment = 0.030, p_perm = 0.105 (not significant).

The three ADEL-centered PDF pairs (ranks 5, 9, 10 by |ΔQ|) rank at positions 847, 1210,
and 824 out of 1321 in the alignment distribution. All are below the population median.

- **ADEL–URYVR:** scalar alignment = −0.015 (anti-aligned; ADEL roaming-active, URYVR dwelling-active)
- **ADEL–URYDL:** scalar alignment = +0.003 (essentially unaligned)
- **ADEL–RMEL:** scalar alignment = +0.016 (weakly aligned, below median)

There is no coupling between the strength of state-dependent conditional reorganization
and the similarity of behavioral encoding profiles.

---

### 3. Is there evidence for an information-limiting interpretation?

**Answer: No. Grade A — No support.**

The joint test (|alignment| × |ΔQ|) for PDF pairs:
- Mean joint score: 0.000225 (PDF) vs 0.000246 (all Class-4), p_perm = 0.464
- Top-quartile joint occupancy: PDF = 19.7%, all C4 = 25.1% (PDF under-represented)

The information-limiting interpretation requires that PDF-associated links connect neurons
that (a) encode the same variable in the same direction AND (b) show strong state-dependent
conditional reorganization simultaneously. Neither condition is met: PDF pairs fail on
condition (a) completely.

**The phrase "information-limiting correlations" should not be applied to this data.**

---

## Grade Summary

**Grade: A — No support** for all three questions.

This is a clean, internally consistent null result. The absence of alignment enrichment is
not a marginal near-miss: PDF pairs show AUROC of 0.43 for both scalar and cosine alignment,
well below the null mean of 0.50, consistently across all annotation categories tested.

---

## What The Data Does Show

The null result has a positive interpretation. The ADEL–PDF–URY circuit reorganization
during dwelling involves neurons with COMPLEMENTARY behavioral profiles:

- **ADEL** (pdf-1 source): velocity-positive (c_v=+0.215), roaming-active mechanosensor
- **URYVR** (pdfr-1 target): velocity-negative (c_v=−0.068), dwelling-active O2 integrator
- **URYDL** (pdfr-1 target): near-zero velocity encoding (c_v=+0.012), high pumping response

The dwelling-state conditional dependence between ADEL and URYVR/URYDL connects neurons
that have OPPOSITE or WEAK velocity encoding. This is more consistent with a
**cross-variable coordination** function (integrating mechanosensory and chemosensory
inputs during food exploitation) than with shared-noise amplification of a common signal.

---

## Data Quality Note

All 61 neurons had behavioral encoding weights from at least 32 recordings.
The annotation counts exactly match phase2 stage4a results:
- PDF: 61 Class-4 pairs ✓
- Serotonin: 33 Class-4 pairs ✓
- Combined: 94 Class-4 pairs ✓

The flat index encoding error (initial script used N×N rather than upper-triangle indexing)
was identified and corrected before computing any reported results.

---

## Files

| File | Contents |
|---|---|
| `b0_context_note.md` | Available behavioral variables, data sources |
| `b1_behavioral_encoding.md` | Per-neuron encoding weights, population distribution |
| `b2_alignment_matrix.md` | Pairwise alignment construction and key pair values |
| `b3_alignment_enrichment.md` | Annotation enrichment tests (AUROC + permutation) |
| `b4_toplink_alignment.md` | Top ΔQ link alignment analysis |
| `b5_information_limiting_test.md` | Joint alignment × |ΔQ| test |
| `b6_attention_symmetry.md` | Attention comparison (not supported) |
| `encoding_weights.npy` | (61,4) behavioral encoding weights per neuron |
| `alignment_matrix.npy` | (61,61) scalar (c_v) alignment |
| `alignment_matrix_vector.npy` | (61,61) cosine (3D) alignment |
| `phase4b_results.json` | All numeric results |

---

## Authorization Boundary

This phase did NOT:
- Re-examine Ω or diffusion analyses
- Revisit coupling models
- Consume held-out ADEL evaluation
- Make perturbation predictions

**STOP. Awaiting review.**
