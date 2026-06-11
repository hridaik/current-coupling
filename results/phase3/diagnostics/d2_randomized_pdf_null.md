# D2 — Randomized-P Null Repair
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Method

For each of 100 degree-preserving randomized P graphs:
- Fit (α_r, α_d) independently using 52×52 grid + Nelder-Mead
- Same objective as M1: Spearman rank correlation on training Class 4 pairs
- Same J_base (directed A_raw with γ=6.131)

## Objective (ρ_train) Distribution

| Statistic | M2 null (proper) | M1 (real PDF) |
|---|---|---|
| Median | 0.0618 | — |
| p75 | 0.0618 | — |
| p95 | 0.0618 | — |
| p99 | 0.0618 | — |
| Max | 0.0618 | — |
| **M1 value** | — | **0.0618** |

**Empirical p-value P(M2 ≥ M1) = 1.000** (100/100 random graphs exceed M1)

## AUROC (PDF training pairs) Distribution

| Statistic | M2 null | M1 |
|---|---|---|
| Median | 0.9198 | 0.9193 |
| p95 | 0.9198 | — |

## Fitted α Distribution (M2 null)

| Parameter | Median | p5 | p95 |
|---|---|---|---|
| α_roam | -26.251 | -26.251 | -26.251 |
| α_dwell | -23.973 | -23.973 | -23.973 |
| Δα = α_d − α_r | 2.278 | 2.278 | 2.278 |

## Interpretation

An empirical p-value near 0 indicates M1 significantly exceeds the null.
An empirical p-value near 1 indicates M1 does not exceed random PDF structure.

Note: The M2 α distribution tells us what α values the objective selects for
random graphs — if these match M1's α, it means the optimum is driven by
degree structure, not PDF identity.
