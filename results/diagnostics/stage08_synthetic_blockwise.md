# Stage 8 — Blockwise and Pooled Multi-Animal Robustness

Date: 2026-05-29
Synthetic only. Phase 0 guard active.
N_COMMON_NEURONS = 61. Effect size = 0.2. K_BLOCKS = 6. B = 30.
T_per_animal = 40 frames (median roaming frames per animal, Stage 5).

---

## 1. Blockwise vs Full-Matrix Stability Selection

K = 6 blocks, block size ≈ 10 neurons.
Effective T / N_block ratio vs full T / N:

| Regime | T | T/N_block | Full TPR | Full FPR | Block TPR | Block FPR |
|---|---|---|---|---|---|---|
| roaming_middle | 60 | 6.0 | 0.00 | 0.00 | 0.00 | 0.00 |
| roaming_optimistic | 420 | 42.0 | 0.80 | 0.02 | 0.00 | 0.00 |
| non_roaming_middle | 300 | 30.0 | 0.30 | 0.01 | 0.30 | 0.01 |

---

## 2. Pooled Multi-Animal Recovery

Each animal contributes T_per_animal = 40 frames.
Total pooled T = n_animals × 40.

| n_animals | T_total | TPR | FPR_on |
|---|---|---|---|
| 1 | 40 | 0.00 | 0.00 |
| 3 | 120 | 0.20 | 0.00 |
| 5 | 200 | 0.20 | 0.00 |
| 10 | 400 | 0.30 | 0.00 |
| 25 | 1000 | 0.90 | 0.15 |
| 40 | 1600 | 1.00 | 0.10 |

First n_animals where TPR ≥ 0.6: 25

---

## 3. Interpretation

### 3.1 Blockwise structure

The blockwise estimator fits K=6 separate precision matrices, each of size
10×10. For T=60 frames (roaming_middle), the per-block
T/N_block ratio = 6 vs T/N = 60/61 ≈ 1.0 (full matrix).
A T/N_block ratio > 1 means the blockwise estimator is more tractable.

Key question: if the signal (ΔQ) happens to fall within one block, does blockwise
estimation detect it? The signal pairs are randomly placed — most signal pairs fall
in different blocks (cross-block) and are invisible to within-block estimation.

Limitation: blockwise estimation misses cross-block signal pairs entirely.
It only helps when signal is concentrated within a single block. For arbitrary
off-connectome signal (as assumed here), blockwise offers limited benefit.

### 3.2 Pooled multi-animal recovery

Adding animals increases total T linearly. The TPR-vs-T curve shows at what
pooled support the estimator becomes reliable. The threshold of TPR ≥ 0.6
at effect=0.2 is reached at n_animals=25 (T=1000).

For the real roaming analysis:
- 25 animals contribute roaming data (Stage 5: 25/40 animals with ≥1 roaming epoch)
- Median T_per_animal ≈ 8s = 40 frames at 5Hz
- Total pooled T ≈ 25 × 40 = 1000 frames

The pooled result here uses T_per_animal=40 frames/animal. This is
the median real-world contribution. The roaming_optimistic regime used T=420 (pooled p25
estimate), which would correspond to ~10 animals contributing 40 frames each.

### 3.3 Recommended strategy

Based on both the blockwise and pooled experiments:

1. **Full-matrix pooled estimation** is viable at T≥420 (optimistic roaming)
   and T≥2000 (non-roaming). This matches Stage 6 pooled p25 estimates.

2. **Blockwise estimation** does NOT help for randomly placed signal.
   It would only help if signal is concentrated within the block structure
   (e.g., if signal pairs share a common brain region). This is not guaranteed
   for the off-connectome ΔQ hypothesis.

3. **Pooled multi-animal** is the primary strategy for roaming. Reaching
   TPR ≥ 0.6 requires enough animals to push total T above ~1000.

---

## 4. Figures

- `results/figures/stage08_blockwise_vs_fullmatrix.pdf` — blockwise vs full-matrix TPR
- `results/figures/stage08_pooled_animals_tpr.pdf` — TPR vs total pooled T

---

## 5. Deviations

None. Synthetic data only. Real-data precision blocked.
