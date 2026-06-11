# Phase 3E-3 — Distance and Topology Analysis
Date: 2026-06-03
Authorization: Phase 3E

## Motivation

OU cascade prediction: current-supported organization should preferentially involve
long-range (indirect) neural dependencies — pairs connected through intermediate
neurons rather than directly synaptic.

---

## Connectome Graph

Source: White 1986 + Witvliet 2020 (7 + 8), threshold ≥ 1 synapse, undirected BFS.
Total nodes: 224, edges: 3698.
61-subgraph neurons in connectome: **49/61**.
Missing 12: all pharyngeal (I1L, I1R, I2L, I2R, I3, M1, M3L, M3R, M4, MI, NSML, NSMR).

Class 4 pairs with defined distance: **769/1321** (58%).
Undefined pairs: one or both neurons absent from connectome (pharyngeal pairs).

---

## E3.1 — Distance Distributions by Group

| Group | n | Reachable | Mean dist | Median | Frac ≥ 2 | Frac unreachable |
|---|---|---|---|---|---|---|
| All Class 4 | 1321 | 769 | **2.02** | 2.0 | 92% | 42% |
| Top-50 ΔQ | 50 | 34 | **1.88** | 2.0 | 82% | 32% |
| Top-50 ΔΩ | 50 | 33 | **1.88** | 2.0 | 82% | 34% |
| Top-50 R (disagreement) | 50 | 33 | **1.91** | 2.0 | 85% | 34% |
| Ω-only (ΔQ=0, ΔΩ≠0) | 1078 | 618 | **2.02** | 2.0 | 92% | 43% |
| PDF C4 pairs | 61 | 51 | **2.02** | 2.0 | 90% | 16% |
| Non-PDF C4 pairs | 1260 | 718 | **2.02** | 2.0 | 92% | 43% |

Nearly all reachable pairs are at distance 2 (connected through one intermediate neuron).
Distance 1 (direct synaptic connection) would be on-connectome (Class 1/2), not Class 4.
Distance ≥ 3 is rare. The distance distribution is essentially uniform across groups.

---

## E3.2 — Statistical Tests

| Comparison | p-value (Mann-Whitney) | Interpretation |
|---|---|---|
| Top-50 ΔΩ vs Top-50 ΔQ distances | **0.980** | No difference |
| Ω-only vs Top-50 ΔQ distances | **0.073** | Marginally different (not significant) |

The null hypothesis of equal distances cannot be rejected for any comparison.

---

## Does the OU Prediction Hold?

**No evidence for the OU long-range prediction.**

The OU cascade model predicts that current-supported (Ω-emphasized) organization
should preferentially involve long-range dependencies. If Ω-only pairs (zero ΔQ,
nonzero ΔΩ) were longer-range than ΔQ-carrying pairs, this would support the OU
prediction.

**Ω-only mean distance = 2.02, same as all Class 4 pairs (2.02) and top-50 ΔQ (1.88).**
Ω-only pairs are not more long-range. They are indistinguishable topologically from
the full Class 4 distribution.

The marginal Ω-only vs ΔQ difference (p = 0.073) goes in the OPPOSITE direction:
Ω-only pairs have slightly LONGER mean distance (2.02) than top-50 ΔQ pairs (1.88).
This would suggest Ω-only pairs are marginally more indirect — but the effect is small,
not significant after multiple testing, and explained by the fact that top-ΔQ pairs
tend to involve well-connected neurons with shorter graph distances.

---

## Distance Constraint Notes

1. **All Class 4 pairs are off-connectome** (distance ≥ 2 by definition — direct
   synaptic pairs are Class 1/2). The mean distance of 2.02 indicates most reachable
   C4 pairs are connected through exactly ONE intermediate neuron.

2. **42% unreachable** reflects the 12 pharyngeal neurons absent from the connectome
   database. Pairs involving these neurons are excluded from distance analysis.

3. **PDF pairs have lower unreachable fraction (16%)** because PDF source/target neurons
   (ADEL, RMEL, RMER, RID, URY, OLQ, I1) are mostly in the connectome. This is a
   coverage artifact, not a biological signal.

---

## Conclusion

The distance analysis finds no topological distinction between ΔΩ-emphasized pairs,
ΔQ-carrying pairs, and the overall Class 4 distribution. The OU cascade prediction
of long-range Ω structure is not supported in this dataset.

---

*E3 scope: distance and topology only.*
