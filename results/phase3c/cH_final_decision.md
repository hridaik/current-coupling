# Phase 3C-H6 — Final Decision Table
Date: 2026-06-03
Authorization: Phase 3C-H

---

## Decision Table

| Criterion | ΔQ | ΔΩ_full | Winner | Evidence |
|---|---|---|---|---|
| **PDF AUROC** | 0.556 | 0.664 | **ΔΩ** | +0.108; p_deg < 0.002 |
| **PDF Fisher OR** | 5.46 | 7.41 | **ΔΩ** | +1.95; p_deg < 0.002 |
| **ADEL signal** | Ranks 5,9,10 | Ranks 5,7,8 | **Tie** | ±2 positions |
| **Blockwise interpretability** | DA_mech↔URY rank 2 | DA_mech↔URY rank 2 | **Tie** | Identical structure |
| **Sparsity fidelity** | 1078 zeros preserved | 1078 zeros imputed | **ΔQ** | ΔΩ overrides lasso |
| **Theoretical alignment** | Matches CePNEM model | Requires new theory | **ΔQ** | Diagonal D ≡ ΔQ |
| **Cross-coordinate robustness** | PDF AUROC consistent | GCaMP degrades | **ΔQ** | GCaMP: 0.526→0.488 |
| **Annotation selectivity** | N/A | Not selective | **ΔQ** | Unann rescued > PDF |
| **Source attribution** | ADEL primary | RID/RMER primary | **ΔQ** | ADEL only 13% of gain |

---

## Final Recommendation

```
[x] A. ΔQ primary, Ω secondary (or not used at all for the current analysis)
[ ] B. ΔQ and Ω co-primary
[ ] C. Ω primary, Q special case
```

---

## Justification

### Why NOT B (co-primary) or C (Ω primary):

**The AUROC/Fisher improvement does not reflect new biological signal.**

Phase 3C-H has established through five independent analyses that the ΔΩ_full
improvement over ΔQ is an artifact of D_emp imputation, not a biological discovery:

1. **H4 (Sparsity)**: The rescue rate for unannotated pairs (83%) exceeds that for
   PDF pairs (72%). D_emp is not selective for biological annotation.

2. **H5 (Localization)**: 87% of the AUROC gain comes from RID/RMEL/RMER hub
   structure — not from ADEL, which is the motivated hypothesis. The improvement
   comes from the wrong source class.

3. **G1 (Pair movement)**: All 20 largest upward-moving pairs had ΔQ = 0. They
   were set to zero by the graphical lasso because the data provided no evidence
   for state-dependent conditional dependence. D_emp overrides that null assignment.

4. **H1 (Fisher)**: The CeNGEN annotation (broader biological context) DEGRADES
   under ΔΩ. A genuinely better summary statistic would not degrade one annotation
   while improving another.

5. **H3 (Blockwise)**: Block-level structure is unchanged. No new biological insight
   comes from ΔΩ at the module level.

### Why A (ΔQ primary):

**ΔQ preserves the graphical-lasso decision that zero-ΔQ pairs lack evidence.**

The confirmation estimator (ADMM, λ_off = 0.10) is the Phase 2 authorized estimator.
It sets ΔQ = 0 for 82% of pairs because the data provide insufficient evidence for
state-dependent partial correlation. This is the correct statistical decision under
the pre-specified analysis plan.

ΔΩ_full overrides 1078 of those null decisions using the off-diagonal structure of
D_emp. Since D_emp is agnostic to biological annotation (rescue rate higher for
unannotated than for PDF pairs), this override does not add biological content.

**The ADEL predictions are unaffected.** The four held-out ADEL pairs
(URYVR, URYDL, RMEL, URXL) change by ≤2 rank positions under ΔΩ_full. If the
purpose of the Ω investigation was to strengthen the ADEL case, it has failed.

**ΔQ has superior theoretical grounding.** Under the CePNEM diagonal noise model,
ΔΩ = D·ΔQ ≈ ΔQ (Phase 3C established ρ > 0.9999 for diagonal D). The full-matrix
D_emp formulation requires new theoretical justification that has not been developed.

### Scope of ΔΩ_full as a secondary finding

ΔΩ_full's stronger Bentley PDF Fisher OR (7.41 vs 5.46) is a real empirical result
that could be mentioned in supporting material. The correct framing:

> "A diffusion-weighted combination D_emp @ ΔQ, using the empirical first-difference
> covariance matrix, yields a higher Bentley PDF Fisher OR (7.41) than ΔQ alone (5.46).
> However, this improvement is driven by zero-ΔQ PDF pairs being assigned imputed
> nonzero values via D_emp mixing (Phase 3C-G/H), primarily through the hub position
> of RID and RMEL/RMER in the CePNEM diffusion structure rather than through the
> ADEL→URY pathway of primary biological interest. The primary analysis uses ΔQ."

---

## Phase 3C Complete

Phase 3C, including sub-phases 3C-E through 3C-H, has comprehensively evaluated the
Ω pathway from multiple angles:

| Sub-phase | Finding |
|---|---|
| 3C | Diagonal Ω ≡ ΔQ (ρ > 0.9999); terminate diagonal Ω pathway |
| 3C-E | Full D_emp is moderately anisotropic (isotropy score 0.16); D_emp @ ΔQ ≠ ΔQ |
| 3C-F | CePNEM PDF AUROC improves 0.556 → 0.664; GCaMP degrades; ADEL preserved |
| 3C-G | AUROC gain is zero-pair imputation; ADEL neutral; RID/RMEL/RMER drive improvement |
| 3C-H | Non-selective rescue; ADEL 13% of gain; blockwise unchanged; sparsity fidelity violated |

**Convergent conclusion across all sub-phases**: ΔQ is the correct primary object.
The Ω pathway does not provide scientifically superior predictions for the
ADEL-centered biological hypothesis.

**Held-out ADEL evaluation status**: Unconsumed. ADEL–URYVR, ADEL–URYDL,
ADEL–RMEL, ADEL–URXL ΔQ_obs not consulted. Await human review.

---

*Phase 3C-H: STOP. Awaiting human review.*
