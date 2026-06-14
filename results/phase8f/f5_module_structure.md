# F5: Module Structure of Top-Ranked Pairs

**Phase**: 8F — What is the framework actually recovering?  
**Date**: 2026-06-14  
**Module definition**: M1={0..24}, M2={25..49}, M3={50..74}, M4={75..99}  
**Base rate within-module**: 4×(25×24)/9900 = 2400/9900 = 24.2%

---

## Module Composition at Top-K

### Module Interaction Matrix — Top-50 by C-score

Rows = source module (i), Columns = target module (j):

```
           M1    M2    M3    M4
M1  →  [   0,    1,    6,    0 ]
M2  →  [   3,    5,    8,    1 ]
M3  →  [   4,    9,    2,    5 ]
M4  →  [   0,    4,    2,    0 ]
```

Dominant pairs: M3→M2 (9), M2→M3 (8), M1→M3 (6), M3→M4 (5), M2→M2 (5)

**Within-module count at top-50**: M1→M1=0, M2→M2=5, M3→M3=2, M4→M4=0 → total = **7/50 = 14%**

Base rate within-module = 24.2%.

### Module Interaction Matrix — Top-100 by C-score

```
           M1    M2    M3    M4
M1  →  [   1,    6,    9,    1 ]
M2  →  [   8,    5,   18,    4 ]
M3  →  [  11,   14,    3,    7 ]
M4  →  [   3,    5,    4,    1 ]
```

Dominant cross-module pairs: M2→M3 (18), M3→M2 (14), M3→M1 (11), M1→M3 (9), M2→M1 (8)

**Within-module count at top-100**: M1→M1=1, M2→M2=5, M3→M3=3, M4→M4=1 → total = **10/100 = 10%**

---

## Within-Module vs. Cross-Module Enrichment

| k | Within observed | Within expected | % Within | OR (within) | p-value |
|---|----------------|----------------|----------|------------|---------|
| 10 | 1 | 2.42 | 10% | 0.347 | 0.9418 |
| 20 | 2 | 4.85 | 10% | 0.347 | 0.9695 |
| 50 | 7 | 12.1 | 14% | 0.509 | 0.9739 |
| 100 | 10 | 24.2 | 10% | 0.347 | 0.9999 |

**The framework's top-K by C-score is systematically below base rate for within-module pairs.** OR=0.347 at k=100 (p>0.99) means within-module pairs are significantly DEPLETED.

---

## Cross-Module Enrichment

Since within-module pairs are depleted, cross-module pairs must be enriched:

| k | Cross-module obs | Cross-module exp | % Cross | OR (cross) |
|---|-----------------|-----------------|---------|-----------|
| 10 | 9 | 7.58 | 90% | — |
| 50 | 43 | 37.9 | 86% | ~1.45× |
| 100 | 90 | 75.8 | 90% | ~1.56× |

The top-K by C-score is biased toward **cross-module pairs**, particularly M2↔M3 interactions.

---

## Hub Analysis

Neurons appearing most frequently in top-100 by C-score:

| Neuron | Module | Count | Structural role | H2 inputs |
|--------|--------|-------|----------------|-----------|
| 32 | M2 | 20 | 11 in, 10 out (OBS) | receives H2-139 (but only 1) |
| 64 | M3 | 18 | 9 in, 7 out (OBS) | none from H2 |
| 51 | M3 | 16 | — | — |
| 22 | M1 | 13 | — | — |
| 70 | M3 | 9 | — | — |

Neurons 32 and 64 together account for 38% of top-100 pairs (as i or j). Both are in M2 and M3 — the two most-connected modules in the benchmark's H2 target structure.

**Key property**: These hub neurons are NOT special because of H2 connectivity. Neuron 64 has no H2 inputs; neuron 32 receives from only H2-139 (one of 8 H2 neurons). Their prominence in the C-score ranking reflects their role as "moderately connected" observed neurons that, when paired with neurons from other modules, produce the near-maximal-entropy softmax scores that push pairs to the top of the C-score ranking.

---

## Why Cross-Module Pairs Dominate

In the benchmark architecture, each H2 neuron connects exactly 2 modules. H2 connectivity creates cross-module coupling. After z-regression, the H2-mediated cross-module coupling is partially removed from y_resid — but the cross-module structural paths (direct inter-module obs connections) are also captured in PCor_cond.

The N-labeled cross-module pairs (which dominate the top-K) share a structural property: they have weak cross-module coupling in A_sparse (no direct H2 relay, weak H1-indirect coupling) AND weak within-module H1-mediated coupling. This combination produces the low PCor_cond and near-zero Delta_PCor that pushes them to maximum softmax entropy — and thus high C-score by default.

The within-module N pairs, by contrast, may have slightly stronger co-activity from shared local inputs (H1 neurons preferentially connect within modules), giving them slightly higher PCor_cond and thus lower C-score.

---

## Module 4 (M4) Absence

M4 (neurons 75–99) is conspicuously absent from the top-K:
- Top-50: M4-source pairs = 4/50 (8%), M4-target pairs = 6/50 (12%)
- Both below the expected ~25%

This may reflect that M4 neurons have different connectivity patterns in the randomly-generated A_sparse (either more structured, creating more detectable PCor_cond, or differently connected to H1). This is a network-specific artifact, not a systematic design feature.

---

## Latent Structural Hub Check

Is the top-K dominated by pairs involving neurons that are "hub nodes" in the H2 connectivity?

| Neuron class | Count in SA | Avg occurrences in top-100 |
|-------------|------------|---------------------------|
| SA neurons (132–139) | 8 | 0 (not in obs pool) |
| Obs neurons with 2+ H2 inputs | varies | — |

Since SA neurons (132–139) are hidden and outside the 0–99 obs pool, they cannot directly appear in top-K. The "hubs" (32, 64) are in the obs pool and are prominent because of their intermediate structural degree — enough connections to appear in many pairs but not so many that PCor_cond becomes large.

---

## Conclusion

The module structure of the framework's top-K reveals:

1. **Cross-module bias**: Top-K pairs are systematically cross-module (OR≈0.35 for within-module at k=100)
2. **M2–M3 dominance**: The M2↔M3 interface is the most over-represented module pair (17 out of 50 top pairs)
3. **Hub neurons 32 and 64**: Not special by H2 connectivity, but prominent because of intermediate structural degree
4. **No M4**: Module 4 is largely absent — a network-specific connectivity artifact

These patterns reflect the network's structural properties filtered through the softmax dynamics, **not any detection of state-modulated off-connectome organization**. The cross-module bias in particular mimics the spatial distribution of C pairs (which also tend to be cross-module, since H2 neurons each connect 2 modules) — but C pairs are entirely absent from the top-50.

The framework appears to identify cross-module pairs with intermediate structural degree (neither strongly coupled nor completely uncoupled) — pairs that lie in the maximum-entropy zone of the softmax, where no class can claim dominance.
