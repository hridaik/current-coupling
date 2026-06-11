# Phase 3C Final Recommendation
Date: 2026-06-03
Authorization: Phase 3C + 3C-E + 3C-F

---

## Situation Summary

Phase 3C established that **under a diagonal noise model (D = diagonal), ΔΩ ≈ ΔQ**
for both CePNEM and GCaMP coordinates. This is a mathematically exact result:
ΔΩ = D · ΔQ (elementwise row-scaling), and D is near-uniform (CV ≈ 3–15%) due to
z-scored CePNEM residuals and normalized GCaMP traces.

Phase 3C-E introduced the **full empirical diffusion matrix** D_emp = Cov(Δx),
which has 13–14% off-diagonal energy and condition number 2.5–2.9. Under D_emp,
ΔΩ_full = D_emp @ ΔQ differs materially from ΔQ (Spearman ρ = 0.57 for CePNEM).

Phase 3C-F found that CePNEM ΔΩ_full has **stronger Bentley PDF enrichment**
(AUROC 0.664 vs 0.556), but GCaMP ΔΩ_full degrades the same annotation (0.488 vs 0.526).

---

## Final Question: Can the manuscript present Ω as the primary object?

```
YES  [ ]
PARTIALLY  [x]
NO  [ ]
```

---

## Answer: PARTIALLY

With the following precise conditions that determine the scope of "partially":

---

### Where YES applies

**For the diagonal model (Ω = D Q + A, D diagonal):**

The manuscript CAN state that Ω and Q are numerically equivalent for this dataset,
provided it specifies the diagonal noise assumption. Under the per-neuron innovation
variance D (which is what CePNEM uses by construction), ΔΩ = D · ΔQ with D
near-uniform (CV = 9%). Top-20 overlap is 19/20. Enrichment is unchanged. This
justifies using either ΔQ or ΔΩ as the primary object with equivalent results.

**For the CePNEM × Bentley PDF enrichment analysis:**

The manuscript CAN report that a diffusion-weighted combination D_emp @ ΔQ yields
stronger PDF enrichment (AUROC 0.664 vs 0.556, p_deg < 0.002). This is an empirical
finding that strengthens confidence in the PDF signal. However, it must be presented
as an exploratory finding with a properly named object (not "Ω" from the diagonal model).

---

### Where NO applies

**For claiming Ω as a generally superior primary object:**

1. The improvement from D_emp @ ΔQ is **coordinate-specific**: present in CePNEM
   (AUROC +0.108) but absent/negative in GCaMP (AUROC −0.038). A universally superior
   object would improve in both coordinates.

2. **D_emp @ ΔQ is NOT Ω from the model Q = D^{-1}(Ω − A)** unless D is taken as
   the full covariance matrix, which requires new theoretical justification not developed
   here. The current model derivation assumes diagonal D.

3. The CeNGEN serotonin/PDF annotation DEGRADES in CePNEM under D_emp (PASS → FAIL),
   indicating annotation-dependent rather than universally better performance.

4. The interpretability of D_emp @ ΔQ as "current organization" requires additional
   theoretical development.

---

## Recommended Manuscript Language

The findings support the following structured claims:

**Primary statement (on ΔQ):**
> "We use the state-dependent change in graphical-lasso precision, ΔQ = Q_roam − Q_dwell,
> as the primary summary statistic for off-connectome pair ranking. Under the per-neuron
> diagonal noise model assumed by CePNEM, the current organization Ω = D Q + A produces
> ΔΩ ≡ D · ΔQ, which is equivalent to ΔQ up to a near-uniform rescaling (D diagonal CV ≈ 9%,
> Spearman ρ > 0.9999 with ΔQ), so both objects support identical conclusions."

**Exploratory statement (on D_emp @ ΔQ):**
> "As a sensitivity check, we replaced the diagonal D with the full empirical first-
> difference covariance D_emp. Under this full-matrix formulation, the Bentley PDF
> enrichment increases from AUROC 0.556 to 0.664 in the CePNEM coordinate (p_deg < 0.002),
> with the primary ADEL→URY predictions preserved at the same ranks. This suggests the
> cross-neuron diffusion structure partially amplifies the PDF signal, though the effect
> is coordinate-specific (absent in GCaMP) and the theoretical basis for this formulation
> requires further development."

---

## What Does and Does Not Change

### Phase 2 conclusions: UNCHANGED

- ADEL→URYVR (rank 5) and ADEL→URYDL (rank 9) remain the strongest novel predictions
- PDF AUROC = 0.556 (CePNEM ΔQ) is the authoritative primary result
- Bentley PDF is the only annotation to reach both AUROC PASS and Fisher PASS in Phase 2

### Phase 3C conclusion: UNCHANGED

- Under the model-appropriate diagonal D, ΔΩ ≈ ΔQ
- Phase 3C termination decision for the diagonal Ω pathway remains valid

### New findings from Phase 3C-E/F (exploratory, not yet primary)

- Full D_emp is moderately anisotropic (isotropy score 0.16–0.20) but diagonally dominant (98%)
- D_emp @ ΔQ strengthens CePNEM PDF enrichment to AUROC 0.664 (+0.108)
- ADEL predictions are preserved/improved under D_emp @ ΔQ
- Blockwise structure is unchanged
- GCaMP PDF degrades under D_emp @ ΔQ

---

## Decision Table

| Question | Answer | Basis |
|---|---|---|
| Is diagonal Ω ≈ ΔQ? | YES | Phase 3C: ρ > 0.9999 |
| Does full D_emp @ ΔQ outperform ΔQ? | COORD-SPECIFIC | Phase 3C-F: +0.108 CePNEM, −0.038 GCaMP |
| Do ADEL predictions survive? | YES | Phase 3C-F: ranks 5,7,8 (improved from 5,9,10) |
| Is Ω the primary manuscript object? | PARTIALLY | Diagonal Ω = ΔQ; full Ω exploratory |
| Should D_emp pathway continue? | UNCLEAR | Requires theoretical development + GCaMP reconciliation |
| Is Phase 2 PDF result valid? | YES | Unchanged under all Ω formulations in CePNEM |

---

## Stop Condition

Phase 3C (including sub-phases 3C-E and 3C-F) is complete.

**DO NOT:**
- Evaluate held-out ADEL pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, ADEL–URXL)
- Generate perturbation predictions
- Begin new model families
- Extend D_emp framework without new authorization

The held-out ADEL evaluation remains unconsumed. Await human review before proceeding.

---

## Phase 3C Output File Index

| File | Status |
|---|---|
| cA_omega_robustness.md | Complete |
| cB_deltaOmega.md | Complete |
| cC_blockwise_attribution.md | Complete |
| cD_sensitivity.md | Complete |
| cE_diffusion_structure.md | Complete |
| cF_omega_enrichment.md | Complete |
| cF_top_pair_comparison.md | Complete |
| cF_blockwise_comparison.md | Complete |
| cF_method_comparison.md | Complete |
| phase3c_summary.md | Complete (pre-3C-E; see 3C-F for updated conclusions) |
| phase3c_decision_memo.md | Complete (superseded by this final recommendation) |
| **phase3c_final_recommendation.md** | **This file** |
| omega_models.json | Complete |
| gcamp_d_characterization.json | Complete |
| diffusion_metrics.json | Complete |
| diffusion_matrices.json | Complete |
| phase3c_f_results.json | Complete |
| D_emp_cepnem.npy | Complete |
| D_emp_gcamp.npy | Complete |

---

*Phase 3C: STOP. All authorized tasks complete. Awaiting human review.*
