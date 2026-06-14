# Phase 9C — Oracle Ceiling Check (AT-5)

**Date:** 2026-06-14  
**Source:** results/phase9c/ground_truth/oracle_summary.json  

---

## Purpose

The oracle ceiling check (AT-5) verifies that the ground-truth oracle (using ΔΩ_true
directly) achieves PMC_AUROC ≥ 0.90 before any framework evaluation begins. This check
was ABSENT in Phases 6–8 — the benchmark declared failure before verifying that the
oracle itself was meaningful. Phase 9B introduced AT-5 as a mandatory pre-condition.

---

## Oracle Baseline (B4)

**Definition:** Rank off-connectome pairs by |ΔΩ_true[i,j]| (perfect knowledge of
the true current difference matrix).

**PMC_AUROC for B4:**
```
Oracle PMC_AUROC = 0.9983   (requirement: ≥ 0.90)
```

**AT-5 STATUS: PASS**

---

## All Benchmark-Validity Checks

| Check | Criterion | Observed | Pass? |
|-------|-----------|----------|-------|
| D1: PMC dominance | PMC med > 2× non-PMC P90 | 2758× | PASS |
| D2: Top-50 saturation | ≥60% of top-50 are PMC | 100% (50/50) | PASS |
| AT-5: Oracle ceiling | PMC_AUROC ≥ 0.90 | 0.9983 | PASS |
| AT-1a: No direct PMC edges | A[PMC_TGT, PMC_SRC] = 0 | Verified | PASS |
| AT-1b: PMC_SRC → HG connectivity | ≥3 HG per source | min=5 | PASS |
| AT-1c: HG → PMC_TGT connectivity | ≥4 HG per target | min=10 | PASS |
| AT-1d: HG exclusive | A[non-PMC, HG] = 0 | Verified | PASS |
| AT-1e/f: PMC_SRC isolated | A_obs[PMC_SRC,:]=A_obs[:,PMC_SRC]=0 | Verified | PASS |
| AT-1g/h: PMC_TGT isolated | A_obs[PMC_TGT,non-PMC]=0 | Verified | PASS |
| AT-2: Sigma positive-definite | min_eig > 0 | 0.391 (State B) | PASS |
| AT-2b: A_obs cancellation | max|ΔΩ − (D_A Q_A − D_B Q_B)| < 1e-8 | 1.1e-16 | PASS |

All 11 checks pass.

---

## Oracle Performance Summary

```
PMC_AUROC:              0.9983  [threshold: 0.90  — 0.0983 above threshold]
ΔQ PMC_AUROC:           0.9970  [for reference]
Oracle Precision@20:    1.000   [all top-20 are PMC pairs]
Oracle Precision@50:    1.000   [all top-50 are PMC pairs]
Oracle Precision@100:   1.000   [all top-100 are PMC pairs]

D1 ratio:               2758×   [threshold: 2.0×]
D2 top-50:              50/50   [threshold: 30/50]

State lesion top-50:    50/50 PMC (dissolves correctly)
Struct lesion top-50:   0/50 PMC (survives correctly)
```

---

## Comparison: Oracle vs Framework Success Criteria

| Metric | Oracle (B4) | Framework success | Framework partial |
|--------|-------------|-------------------|-------------------|
| PMC_AUROC | **0.9983** | ≥ 0.75 | ≥ 0.60 |
| Precision@50 | **1.000** | ≥ 0.25 | ≥ 0.10 |
| Rank ρ | **1.000** | ≥ 0.40 | ≥ 0.15 |

The oracle ceiling is well above all framework thresholds. A framework that achieves
PMC_AUROC = 0.75 would be at 75% of oracle performance (0.75/0.9983 ≈ 75%). A framework
at 0.85 AUROC would represent approximately 85% of oracle.

**Gap to framework success threshold:**  
Oracle AUROC (0.9983) − Framework success threshold (0.75) = 0.2483  
This gap leaves room for estimation noise, finite sample variance, and framework approximation
error. A framework must achieve ≥75% of the oracle AUROC to declare success.

---

## What Prevents AT-5 Failure

Phase 8B failed AT-5 retroactively: the Graphical Lasso oracle (intended as B4) did not
converge, invalidating the benchmark. Phase 9C's oracle uses ANALYTICAL Lyapunov solution
(not estimated), so convergence failure is impossible. The oracle is mathematically exact.

Checks in order:
1. A_full is stable (eigenvalues have negative real parts) — verified
2. Lyapunov equation has a unique solution (guaranteed for stable A) — verified
3. Sigma is positive-definite — verified (min_eig = 0.392)
4. Sigma is invertible (Q = Sigma^{-1} exists) — guaranteed by PD
5. ΔΩ_true is computed exactly — verified (A cancellation error < 1e-15)
6. PMC_AUROC is computed over off-connectome pairs only — verified (n_off = 10,433)

---

## Ground Truth Hash Lock

The oracle objects are hash-locked before any trajectory generation or framework evaluation:

```
Oracle master hash: 79c98d032742ba36...
Files locked: 24 (including all GT1–GT5, A matrices, Sigma, Q, Omega)
Lock timestamp: must be OLDER than any trajectory file (LC-4 audit check)
```

The master hash must be recorded in the Phase 9D manifest to confirm oracle objects
were not modified after trajectory generation.
