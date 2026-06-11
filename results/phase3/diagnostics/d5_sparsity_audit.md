# D5 — Sparsity Mismatch Audit
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Density Comparison

| | Nonzero entries | Density |
|---|---|---|
| Observed ΔQ (Class 4) | 243 / 1321 | 18.4% |
| Predicted ΔQ_M1 (Class 4) | 1321 / 1321 | 100.0% |

The Lyapunov-derived precision matrix is **dense** (all entries nonzero), while the
graphical lasso ΔQ_obs is **sparse** (82% zeros enforced by regularization).

## Top-K Rank Overlap

| K | Overlap | Expected (random) | Enrichment |
|---|---|---|---|
| 10 | 0 | 0.1 | 0.0× |
| 20 | 0 | 0.3 | 0.0× |
| 50 | 2 | 1.9 | 1.06× |
| 100 | 7 | 7.6 | 0.92× |
| 200 | 36 | 30.3 | 1.19× |
| 500 | 150 | 189.3 | 0.79× |

## Conditional Spearman (nonzero-observed pairs only)

Spearman on pairs where |ΔQ_obs| > 0:
ρ = 0.0897 (p = 0.1631, n = 243)

Compare to full training objective (all pairs, 82% zeros included): ρ = 0.0618

## Key Question

Is the weak Spearman caused by dense prediction vs. sparse observation?

The conditional Spearman on nonzero pairs (0.0897) is DIFFERENT FROM the full-pair Spearman (0.0618).
