# Phase 4B.4 — Alignment of the Strongest ΔQ Links
Date: 2026-06-12

---

## Question

Do the strongest state-dependent links preferentially connect neurons with aligned
behavioral encoding?

---

## Method

The 1321 Class-4 pairs are already ranked by |ΔQ_cepnem| descending (per
ranked_class4_cepnem.npy). Top-20 and top-50 subsets were taken directly.

**Permutation test:** For each subset size K (20 or 50), compare the mean scalar
alignment of the top-K pairs against a null distribution of mean alignments from
2000 randomly sampled K-subsets of all 1321 Class-4 pairs.

---

## Results

### Mean Scalar Alignment by Subset

| Subset | n | Mean align | Median align | Perm p-value | Null mean ± std |
|---|---|---|---|---|---|
| Top-20 |ΔQ| | 20 | +0.0181 | +0.0052 | 0.544 | 0.0199 ± 0.0119 |
| Top-50 |ΔQ| | 50 | +0.0300 | +0.0128 | 0.105 | 0.0203 ± 0.0078 |
| All Class-4 | 1321 | +0.0202 | +0.0069 | — | — |

### Top-20 Individual Pairs

The top-20 |ΔQ_cepnem| pairs (ranks 1–20) include a mix of alignment values:

| Rank | Pair | ΔQ_cepnem | Scalar align | PDF-annotated |
|---|---|---|---|---|
| 1 | IL1DR–URYVR | −0.254 | — | No |
| 2 | AVER–I1L | −0.216 | — | No |
| 3 | AVJR–OLLR | −0.170 | — | No |
| 4 | AVJR–OLQVR | −0.161 | — | No |
| 5 | ADEL–URYVR | −0.122 | −0.015 | **YES** |
| 9 | ADEL–URYDL | −0.098 | +0.003 | **YES** |
| 10 | ADEL–RMEL | −0.096 | +0.016 | **YES** |

No significant excess of high-alignment pairs in the top-20.

### Key Pair Positions in Alignment Ranking

| Pair | Scalar align | |Scalar| rank (of 1321) | Interpretation |
|---|---|---|---|
| ADEL–URYVR | −0.015 | ~847/1321 | Below median alignment |
| ADEL–URYDL | +0.003 | ~1210/1321 | Near bottom of alignment |
| ADEL–RMEL | +0.016 | ~824/1321 | Below median alignment |

The three strongest PDF pairs are all **below median** in alignment magnitude. ADEL–URYDL
is in the bottom 9% of all Class-4 pairs by absolute alignment.

---

## Interpretation

**No significant alignment enrichment in the top-20 or top-50 ΔQ pairs.**

- Top-20: p = 0.544 (not significant)
- Top-50: p = 0.105 (marginally below 0.5, not significant)

The mean alignment of the top-20 pairs (0.018) is slightly below the null mean (0.020).
The top-50 mean (0.030) is slightly above null (0.020), but not significantly.

The three ADEL-centered PDF pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL) that anchor the
Phase 2 PDF signal occupy ranks 847, 1210, and 824 out of 1321 by absolute alignment
magnitude — all below the median. **The strongest state-dependent links do not
preferentially connect neurons with aligned behavioral encoding.**

### Dissociation Between ΔQ Strength and Alignment

This is a clean dissociation:
- The ADEL–URYVR pair is among the top-5 pairs by |ΔQ_cepnem|.
- The ADEL–URYVR pair ranks ~847/1321 by |alignment| — far from the top.

High conditional organization change during state transitions does not require
high behavioral encoding alignment. These are independent dimensions.

---

## Summary

The strongest state-dependent conditional links do not preferentially connect neurons
with aligned behavioral encoding. The top-3 ADEL-PDF pairs are all below the
median alignment, with ADEL–URYVR showing negative alignment (ADEL and URYVR have
opposite velocity tuning). This is inconsistent with an information-limiting
interpretation of the PDF-state-dependent signal.
