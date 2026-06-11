# R3 — Sparse Forward Model
Date: 2026-06-03
Authorization: Phase 3A.6

## Question

Is the architecture failure caused by the dense/sparse mismatch?
Observed ΔQ_obs: 18.4% nonzero (sparse graphical lasso).
Predicted ΔQ_pred: 100% nonzero (dense Lyapunov).

Does applying the same sparsification as Phase 2 to the Lyapunov prediction
recover top-pair overlap?

## Method

Three variants, all applied to the M1-fitted (α_r = −26.25, α_d = −23.97) prediction:

**R3A**: Apply Phase 2 ADMM confirmation estimator (λ_on=0.01, λ_off=0.10) to
Lyapunov-derived correlation matrices Σ_r and Σ_d (normalized to unit diagonal),
yielding sparse Q_r and Q_d. ΔQ_R3A = Q_r_sparse − Q_d_sparse.

**R3B**: Top-k density threshold — zero out all but the top 243 entries of |ΔQ_M1|
(matching observed density of 18.4%).

**R3C**: Apply R3A sparsification at R2-fitted parameters (degenerate; ΔQ = 0).

## Results

| Variant | ρ | AUROC_pdf | Nonzero | top-10 | top-20 | top-50 | top-100 |
|---|---|---|---|---|---|---|---|
| R1 (baseline, dense) | 0.062 | 0.920 | 1321/1321 | 0 | 0 | 2 | 7 |
| **R3A** (ADMM sparse) | **0.033** | **0.779** | **110/1321** | **0** | **1** | **4** | **11** |
| R3B (threshold) | 0.040 | 0.915 | 243/1321 | 0 | 0 | 2 | ~8 |
| R3C (R2 α, degenerate) | — | — | 0 | artifact | artifact | — | — |

Expected top-K by chance: top-10=0.1, top-20=0.3, top-50=1.9, top-100=7.6.

## Key Findings

### R3A: ADMM sparsification improves top-20 from 0 to 1

The ADMM graphical lasso applied to Lyapunov Σ selects 110/1321 pairs as nonzero
(8.3% density). The top-20 overlap increases from 0 (R1) to **1** (R3A).

This is a MARGINAL improvement. Expected by chance: 0.3 pairs in top-20 out of 1.
Observed 1 is ~3× chance for a single trial, but not statistically meaningful.
Top-100 overlap is 11 vs expected 7.6 (1.4× — near-chance).

The ADMM sparsification does NOT recover the correct predicted structure. The top
pairs selected by R3A are DIFFERENT from the top observed pairs — the ADMM selects
based on the Lyapunov covariance structure (dominated by RMEL/AVDL/RID), not on
the patterns in the data.

### R3B: Density-matching threshold does not improve top-K overlap

Setting density equal to observed (243 nonzero) by thresholding preserves the same
top-K predictions as the dense R1. The density mismatch is NOT the cause of zero
top-K overlap. The ranking problem is more fundamental.

### Interpretation

The sparsity mismatch is a secondary issue. The PRIMARY failure is that the Lyapunov
forward model ranks the WRONG pairs as highest-ΔQ, regardless of density treatment.

The ADMM sparsification (R3A) brings a marginal improvement to top-20 (0→1) but this
does not constitute architecture repair. The graphical lasso selects a sparse subset
of the Lyapunov prediction that overlaps weakly with the sparse observed structure.

## Conclusion

R3 produces marginal improvement (top-20 overlap 0→1 for R3A). This is insufficient
to constitute architecture repair. The failure is in the RANKING produced by the
Lyapunov forward model, not in the density mismatch.

---
*R3 scope: sparsification variants of M1 prediction only. No held-out evaluation.*
