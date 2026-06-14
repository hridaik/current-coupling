# F1: Top-K Inventory — Framework's Highest-Ranked Pairs

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**Ranking criterion**: C-score = class_prob['C'] (descending)  
**Frozen framework output**: framework_output.json

---

## Top-10 Pairs (by C-score)

| Rank | (i,j) | Label | Modules | Cross/Same | SAREACHABLE | Direct | C-score | S-score | |ΔCorr| |
|------|-------|-------|---------|-----------|------------|--------|---------|---------|--------|
| 1 | (51,71) | **N** | M3→M3 | same | No | No | 0.2570 | 0.2477 | 0.0493 |
| 2 | (32,64) | **N** | M2→M3 | cross | No | No | 0.2570 | 0.2483 | 0.0223 |
| 3 | (64,32) | **N** | M3→M2 | cross | No | No | 0.2555 | 0.2497 | 0.0223 |
| 4 | (64,22) | **N** | M3→M1 | cross | No | No | 0.2551 | 0.2485 | 0.0167 |
| 5 | (22,64) | **N** | M1→M3 | cross | No | No | 0.2550 | 0.2486 | 0.0167 |
| 6 | (45,51) | **N** | M2→M3 | cross | No | No | 0.2546 | 0.2485 | 0.0269 |
| 7 | (70,22) | **N** | M3→M1 | cross | No | No | 0.2541 | 0.2487 | 0.0135 |
| 8 | (51,45) | **N** | M3→M2 | cross | No | No | 0.2538 | 0.2489 | 0.0269 |
| 9 | (51,88) | **N** | M3→M4 | cross | No | No | 0.2538 | 0.2495 | 0.0337 |
| 10 | (22,28) | **N** | M1→M2 | cross | No | No | 0.2537 | 0.2500 | 0.0605 |

**Notable properties of top-10**:
- 10/10 (100%) labeled N
- 10/10 (100%) NOT SAREACHABLE (no H2-mediated path)
- 10/10 (100%) NOT directly connected (off-connectome structurally)
- 9/10 cross-module
- Mean |ΔCorr| = 0.0289 (below global mean of 0.0476 and C-class mean of 0.0517)
- C-scores are near-uniform: 0.2537–0.2570 (maximum possible ≈ 0.2570)

---

## Softmax Score Analysis — Top Pair (51,71)

The top pair illustrates the scoring regime for the highest-ranked pairs:

```
Neuron 51 → Neuron 71
S-score:  0.2477
C-score:  0.2570  ← assigned label
M-score:  0.2484
N-score:  0.2469
Entropy:  1.3862  (maximum entropy = log(4) = 1.3863)
C exceeds S by: 0.0093
C exceeds N by: 0.0101
```

This is maximum-entropy scoring. The framework is at maximum uncertainty. "C" wins only because Delta_PCor marginally exceeds PCor_cond by a tiny absolute amount — not because the framework detects any C-class signal. The 0.0093 margin is effectively noise.

---

## Top-20 Summary

Ranks 11–20 continue the same pattern. All 20 pairs are N-labeled, with no SAREACHABLE pairs, no direct pairs. Prominent hub neurons: 32 (M2), 64 (M3), 51 (M3), 22 (M1).

---

## Top-50 Summary

| Property | Top-10 | Top-20 | Top-50 |
|----------|--------|--------|--------|
| % N-labeled | 100% | 100% | **100%** |
| % C-labeled | 0% | 0% | 0% |
| % S-labeled | 0% | 0% | 0% |
| % SAREACHABLE | 0% | 0% | 0% |
| % direct | 0% | 0% | 0% |
| Mean |ΔCorr| | 0.0289 | 0.0339 | 0.0455 |
| Mean C-score | 0.2556 | 0.2545 | 0.2534 |

At k=50: 100% N, 100% off-connectome, 0% SAREACHABLE, below-average state sensitivity.

**Module distribution in top-50**: M3↔M2 pairs dominate (17/50 = 34%), followed by M1↔M3 (10/50 = 20%). Module 4 is almost entirely absent.

---

## Top-100 Summary

The first non-N pair appears at:
- **Rank 62**: (80,99), label=**S**, M4→M4, direct=True — the first structural pair
- **Rank 71**: (25,17), label=**C**, M2→M1, SA=True, |ΔCorr|=0.0955

At k=100: 96 N, 3 C, 1 S, 0 M. The 3 C pairs that appear are not the highest-signal C pairs — their |ΔCorr| values (0.0955, 0.0577, 0.0440) are moderate but not exceptional.

---

## Hub Neuron Analysis

Neurons appearing most frequently in top-100 by C-score:

| Neuron | Module | Count in top-100 | H2 connections | Structural connections |
|--------|--------|-----------------|---------------|----------------------|
| 32 | M2 | 20 | receives from H2-139 | 11 in, 10 out |
| 64 | M3 | 18 | none from H2 | 9 in, 7 out |
| 51 | M3 | 16 | (check) | — |
| 22 | M1 | 13 | — | — |
| 70 | M3 | 9 | — | — |

These hub neurons are NOT in SA (they are observed neurons 0–99, not H2 neurons 132–139). Their prominence in the top-C ranking reflects the framework's softmax dynamics: neurons with moderate-to-weak structural connectivity appear in many N-labeled pairs that score high on C-score.

---

## Key Observation

The framework's top-50 by C-score is a **structurally homogeneous set**: 100% N-labeled, 100% off-connectome, 0% state-modulated, below-average state sensitivity, predominantly cross-module (M2–M3 pairs). These are not the pairs the framework is supposed to detect. They are the pairs the framework is most uncertain about — and in that maximum-uncertainty regime, the C-score marginally exceeds the S-score by noise-level amounts.

---

## Comparison: Top-10 C-scored Pairs vs. Top-10 C-class Pairs (by |ΔCorr|)

| Property | Top-10 by C-score | Top-10 C-class by |ΔCorr| |
|----------|------------------|--------------------------|
| Labels | N (100%) | C (100%) |
| SAREACHABLE | 0% | 100% |
| Direct | 0% | 0% |
| Mean |ΔCorr| | 0.029 | ~0.114 |
| Mean C-score | 0.256 | ~0.243 |
| Framework rank | 1–10 | ~6000–9000 |

The framework ranks the most state-dependent C pairs near the **bottom** of its ranking, while N pairs with minimal state-dependent signal appear at the **top**.
