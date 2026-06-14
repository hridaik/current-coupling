# Phase 4B.2 — Pairwise Alignment Matrix
Date: 2026-06-12

---

## Construction

Two alignment matrices were computed over all 1321 Class-4 pairs.

### Scalar Alignment

For each pair (i, j):
```
A_scalar[i,j] = c_v_i × c_v_j
```

Interpretation:
- Large positive: both neurons encode velocity in the same direction (both roaming-active or both dwelling-active)
- Large negative: neurons have opposite velocity encoding (one roaming-active, one dwelling-active)
- Near zero: at least one neuron has weak velocity encoding

### Cosine Alignment (3D)

For each pair (i, j), using behavioral weight vector w_i = [c_v, c_θh, c_P]:
```
A_cosine[i,j] = (w_i / ||w_i||) · (w_j / ||w_j||)
```

Interpretation:
- +1.0: identical behavioral tuning profile
- −1.0: opposite behavioral tuning profile
- 0.0: orthogonal tuning (independent behavioral encoding)

---

## Population Statistics (over 1321 Class-4 pairs)

### Scalar Alignment

| Metric | Value |
|---|---|
| Mean | +0.0202 |
| Median | +0.0069 |
| Std | 0.0426 |
| Min | −0.2072 |
| Max | +0.2730 |
| % positive | ~63% |
| % negative | ~37% |

The positive mean reflects that most neuron pairs have the same-sign velocity encoding
(the population is slightly skewed toward velocity-positive neurons in this 61-neuron set).

### Cosine Alignment

| Metric | Value |
|---|---|
| Mean | ~+0.10 |
| Median | ~+0.08 |
| Range | [−0.999, +1.000] |

The cosine alignment distribution is broader, reflecting genuine variation in the 3D
tuning profile across all behavioral dimensions.

---

## Key Pair Alignment Values

| Pair | c_v_i | c_v_j | Scalar align. | Cosine align. | ΔQ_cepnem | Interpretation |
|---|---|---|---|---|---|---|
| ADEL–URYVR | +0.215 | −0.068 | −0.015 | −0.462 | −0.122 | Anti-aligned |
| ADEL–URYDL | +0.215 | +0.012 | +0.003 | +0.464 | −0.098 | Near-neutral |
| ADEL–RMEL | +0.215 | +0.074 | +0.016 | +0.722 | −0.096 | Weakly aligned |

The anti-alignment of ADEL–URYVR is notable: ADEL is roaming-active (c_v=+0.215) while
URYVR is dwelling-active (c_v=−0.068). Their scalar alignment is negative (−0.015),
ranking in the lower half of all Class-4 pairs by |alignment| (~rank 847/1321).

The cosine alignment for ADEL–URYDL (+0.464) and ADEL–RMEL (+0.722) are higher than
the scalar alignment because head-angle and pumping components agree in direction even
though velocity encoding differs. ADEL–URYVR has negative cosine alignment (−0.462),
confirming opposite behavioral tuning profile.

---

## Alignment Rank of Key Pairs

| Pair | |scalar align.| | Approx. rank (of 1321, high=more aligned) |
|---|---|---|
| ADEL–URYVR | 0.015 | ~847/1321 (below median) |
| ADEL–URYDL | 0.003 | ~1210/1321 (near bottom) |
| ADEL–RMEL | 0.016 | ~824/1321 (below median) |

None of the top-3 PDF pairs by |ΔQ| are in the upper half of alignment. This immediately
suggests that the dwelling-dominant conditional reorganization is NOT driven by same-variable
encoding alignment.

---

## Files Saved

- `alignment_matrix.npy` — (61, 61) scalar alignment matrix (c_v product)
- `alignment_matrix_vector.npy` — (61, 61) cosine alignment matrix (3D)
