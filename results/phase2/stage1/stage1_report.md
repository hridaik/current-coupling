# Stage 1 Report — Real-Data Pairwise Precision Estimation

Date: 2026-06-01  
Script: `scripts/phase2/stage1_estimation.py`

---

## Overall Status

**Stage 1 complete. No genuine halt conditions. All precision matrices (Q_conf) are positive definite and well-conditioned.**

The script triggered halt flags for the discovery matrices (Q_disc) failing the PD check. This is a **scripting diagnostic error**: Q_disc matrices are stability score matrices (bootstrap selection frequencies in [0,1]), not precision matrices. Applying a PD check to them is not meaningful. The actual precision matrices — Q_conf from the anatomy-guided ADMM lasso — are all positive definite.

**Stage 2 (ΔQ) requires explicit human authorization before proceeding.**

---

## 1. Covariance Assembly

All four pairwise covariance matrices are naturally positive semi-definite. PSD_EIGENVALUE_FLOOR (1e-6) was not triggered for any matrix. Consistent with Stage 0-V synthetic prediction (0 clipped).

| Matrix | Diag range | Off-diag range | Eigenvalues clipped | Min eigenvalue |
|---|---|---|---|---|
| S_cepnem_dwell | [0.922, 1.097] | [−0.056, +0.154] | **0** | +0.573 |
| S_cepnem_roam | [0.794, 1.307] | [−0.216, +0.417] | **0** | +0.370 |
| S_gcamp_dwell | [0.936, 1.088] | [−0.150, +0.257] | **0** | +0.376 |
| S_gcamp_roam | [0.882, 1.417] | [−0.369, +0.471] | **0** | +0.167 |

---

## 2. Confirmation Precision Matrices — Q_conf

These are the precision matrices for Stage 2. All positive definite, symmetric, well-conditioned.

| Matrix | PD | Cond. | Min eigenvalue | n_edges |
|---|---|---|---|---|
| Q_cepnem_roam_conf | **YES** | 3.57 | 0.425 | 461 |
| Q_cepnem_dwell_conf | **YES** | 2.10 | 0.634 | 305 |
| Q_gcamp_roam_conf | **YES** | 9.71 | 0.207 | 745 |
| Q_gcamp_dwell_conf | **YES** | 3.61 | 0.418 | 517 |

No ADMM convergence failures. All condition numbers << 10^6.

---

## 3. Stability Scores — Stab

Stability scores are bootstrap selection frequencies, not precision matrices. Used for weighting ranked pairs in Stage 2.

| Coord | State | Stable pairs (≥ 0.75) | Max stab | Median nonzero stab | Notes |
|---|---|---|---|---|---|
| cepnem | roam | 1768 / 1830 (96.6%) | 1.000 | 0.960 | Near-saturation |
| cepnem | dwell | **1** / 1830 (0.05%) | 0.760 | 0.160 | Near-zero — see §4A |
| gcamp | roam | 1830 / 1830 (100%) | 1.000 | 1.000 | Saturated — see §4B |
| gcamp | dwell | 1830 / 1830 (100%) | 1.000 | 1.000 | Saturated — see §4B |

All 25 bootstraps converged (gcamp_roam: 23/25 minor).

---

## 4. Notable Findings

### 4A — CePNEM dwelling stability near-zero (1 stable pair)

Only 1 of 1830 pairs achieves stability ≥ 0.75 in the dwelling-state CePNEM residual coordinate. Two interpretations:

**Biological:** After removing the behavioral confound, dwelling neural activity is genuinely sparse in conditional dependence. Dwelling is a low-coordination state where neurons fire more independently.

**Statistical:** The dwelling covariance has weak off-diagonal structure (max = 0.154). At λ=0.15, each bootstrap graphical lasso regularizes away essentially all edges, giving uniformly low stability. The λ was calibrated to the pooled regime — it may be too conservative for the dwelling-only signal strength.

**Consequence for Stage 2:** ΔQ is computed from Q_conf (ADMM), not from stability scores. Q_cepnem_dwell_conf has 305 edges and is well-conditioned. Stage 2 proceeds normally. However, the stability weighting formula `min(stab_roam, stab_dwell)` will yield near-zero weights for all CePNEM pairs, since stab_dwell ≈ 0 almost everywhere. **Supervisor must specify the preferred ranking weight for Stage 2 (see §7, Q2).**

### 4B — GCaMP stability saturation (all pairs stable)

All 1830 pairs achieve stability ≥ 0.75 in both GCaMP states. Raw GCaMP contains behavioral confound signals (locomotion velocity, head curvature, pumping) that create global correlations among neurons. At λ=0.15, these correlations are not regularized away in any bootstrap subsample. The ADMM confirmation (λ_off=0.10 heavy off-connectome penalty) partially recovers sparsity: Q_gcamp_roam_conf=745 edges, Q_gcamp_dwell_conf=517 edges. The stability weighting for GCaMP will not discriminate between pairs (all stab=1.000).

This finding validates the CePNEM residualization as essential: it removes the behavioral confound that otherwise produces uninformative universal stability in raw GCaMP.

### 4C — Scripting diagnostic issue

The Q_disc matrices saved are stability score masks (entries in [0,1]), not precision matrices. The automatic PD checker incorrectly flagged them. This is a documentation issue, not a methodological problem. No re-run is needed.

---

## 5. Halt Condition Audit

| Flag triggered | Genuine? | Reason |
|---|---|---|
| NOT_PD / HIGH_COND on Q_*_disc | **NO** | Q_disc is a stability score matrix; PD not applicable |

**Zero genuine halt conditions.**

---

## 6. Output Files

**Covariance matrices (S):** 4 pre-projection + 4 PSD-projected = 8 files ✓  
**Stability scores:** 4 files ✓  
**Precision matrices (Q_conf):** 4 files ✓  
**Sufficient statistics:** 8 files (2 coords × 4 arrays) ✓  
**Diagnostics:** `stage1_diagnostics.json`, `covariance/psd_diagnostics.json` ✓

Total: all 24 output files produced.

---

## 7. Questions for Human Review Before Stage 2

**Q1 — CePNEM dwelling sparsity:** Is 1 stable dwelling pair consistent with the expected biological regime, or does this indicate a parameter calibration issue (λ too heavy for dwelling)?

**Q2 — Ranking weight formula for Stage 2:** Phase 2 spec says rank by `|ΔQ| × min(stab_roam, stab_dwell)`. With stab_cepnem_dwell ≈ 0 for essentially all pairs, this formula yields near-zero ranking weights for all CePNEM pairs. Options:
- (a) Keep `min(stab_roam, stab_dwell)` as pre-specified — all CePNEM pairs rank near-zero by weight; enrichment test on raw |ΔQ| order still valid
- (b) Use `max(stab_roam, stab_dwell)` — roaming stability dominates for CePNEM
- (c) Use `stab_roam` only for CePNEM (since dwell is uninformative)
- (d) Report but do not alter — use |ΔQ| alone for CePNEM ranking

**Q3 — GCaMP saturation:** With GCaMP stability saturated, the stability weighting provides no discrimination. Is this acceptable? The ADMM Q_conf provides the only sparsity signal in GCaMP.

**Q4 — Precision matrices for ΔQ:** Confirm Stage 2 uses Q_conf (not Q_disc) as input: `ΔQ_cepnem = Q_cepnem_roam_conf − Q_cepnem_dwell_conf`.

---

## 8. Authorization Required for Stage 2

Record authorization in `PHASE2_CHECKPOINT_LOG.md` as CHECKPOINT P2-006, addressing Q1–Q4 above.

Specify: which Q matrices, which weighting formula, any caveats.

**Stage 2 does not begin automatically.**

---

*Stage 1 scope: covariance assembly, PSD safeguard, stability selection, ADMM confirmation. No ΔQ, no enrichment, no interpretation.*
