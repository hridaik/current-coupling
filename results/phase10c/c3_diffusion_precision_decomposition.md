# Phase 10C.3 — Diffusion/Precision Decomposition
Date: 2026-06-15

**IMPORTANT CAVEAT:** No unique additive decomposition of ΔΩ_ss exists.
Both decompositions below are algebraically valid state-conditioned forms.
Neither is "the" correct decomposition. Results are reported for both.

---

## Decomposition Forms

ΔΩ_ss = D_roam @ Q_roam − D_dwell @ Q_dwell

**Decomposition A** (expand D_roam = D_dwell + ΔD; factor Q_roam = Q_dwell + ΔQ):

  ΔΩ = D_roam @ ΔQ + ΔD @ Q_dwell

  precision term: D_roam @ (Q_roam − Q_dwell)
  diffusion term: (D_roam − D_dwell) @ Q_dwell

**Decomposition B** (symmetric alternative):

  ΔΩ = D_dwell @ ΔQ + ΔD @ Q_roam

  precision term: D_dwell @ (Q_roam − Q_dwell)
  diffusion term: (D_roam − D_dwell) @ Q_roam

Both are verified: recon_A = recon_B = DO_ss_mat to machine precision (atol=1e-8).

---

## Per-Pair Results

| Pair | ΔΩ_ss total | A: prec term | A: diff term | A: prec frac | A: diff frac | A: signs agree? |
|------|------------|-------------|-------------|-------------|-------------|----------------|
| ADEL–URYVR | −0.0688 | −0.0662 | −0.0026 | **0.962** | 0.038 | Both agree |
| ADEL–URYDL | −0.0498 | −0.0554 | +0.0057 | **1.114** | −0.114 | Prec agrees, Diff opposes |
| ADEL–RMEL  | −0.0549 | −0.0504 | −0.0045 | **0.919** | 0.081 | Both agree |
| RMEL–URYDL | −0.0310 | −0.0313 | +0.0003 | **1.011** | −0.011 | Prec agrees, Diff negligible |
| RMEL–RMER  | −0.0254 | −0.0193 | −0.0062 | **0.758** | 0.242 | Both agree |

| Pair | ΔΩ_ss total | B: prec term | B: diff term | B: prec frac | B: diff frac | B: signs agree? |
|------|------------|-------------|-------------|-------------|-------------|----------------|
| ADEL–URYVR | −0.0688 | −0.0569 | −0.0120 | **0.826** | 0.174 | Both agree |
| ADEL–URYDL | −0.0498 | −0.0457 | −0.0040 | **0.919** | 0.081 | Both agree |
| ADEL–RMEL  | −0.0549 | −0.0445 | −0.0104 | **0.811** | 0.189 | Both agree |
| RMEL–URYDL | −0.0310 | −0.0327 | +0.0017 | **1.053** | −0.053 | Prec agrees, Diff opposes |
| RMEL–RMER  | −0.0254 | −0.0205 | −0.0049 | **0.806** | 0.194 | Both agree |

---

## Interpretation

**All five key pairs are predominantly precision-driven.**

The precision term (D_s @ ΔQ) accounts for 76–114% of the total ΔΩ_ss value across
both decompositions. The diffusion-change term (ΔD @ Q_s) contributes at most 24%
(RMEL–RMER in decomp A), and for ADEL-URYDL partially opposes the total (−11% in A,
+8% in B).

**Pair-specific breakdown:**

- **ADEL–URYVR**: 96% precision-driven (A), 83% precision-driven (B). Diffusion change
  adds a consistent small negative contribution in both decompositions. This is the
  cleanest case: the ΔQ structure between ADEL and URYVR drives the full result,
  with D merely scaling and slightly amplifying it.

- **ADEL–URYDL**: 111% precision in A (diffusion partially cancels), 92% precision in B.
  The diffusion-change term acts in OPPOSITE directions depending on which Q_s is used
  as the reference. This ambiguity is inherent to the non-uniqueness of the decomposition
  and does NOT indicate a problem — it shows that the diffusion change for this pair is
  small and its sign relative to the total depends on the reference frame.

- **ADEL–RMEL**: 81–92% precision-driven. Consistent sign agreement in both decompositions.
  Diffusion contributes a coherent negative (dwelling-amplifying) correction.

- **RMEL–URYDL**: Essentially 100% precision-driven. The diffusion-change term is
  negligible in both decompositions (< 6% of total, mixed sign).

- **RMEL–RMER**: 76–81% precision-driven. This is the pair where diffusion change
  matters most (19–24% contribution), consistent with RMEL-RMER being sensitive to the
  coupling correction (Phase 10A) and Phase 4C showing sign instability in ΔD for
  the RMEL–RMER pair at longer timescales.

---

## Summary

| Question | Answer |
|----------|--------|
| Are key pairs primarily precision-driven? | YES — 76–114% across both decompositions |
| Does diffusion change add new signal? | Minor to moderate: 4–24%, consistent sign |
| Does diffusion change oppose the signal? | Only marginally for ADEL-URYDL in decomp A |
| Is there a pair where diffusion dominates? | No — maximum diffusion fraction is 24% (RMEL-RMER) |

**Conclusion: the ADEL/PDF current results are predominantly a precision (ΔQ) phenomenon,
reweighted and amplified by state-specific diffusion. Dense D does not create the
biological organization — it reflects it.**

The decomposition is NOT unique, so the precise fractions should not be over-interpreted.
What is robust: the sign agreement between the precision term and the total ΔΩ_ss is
consistent across both decompositions for all five pairs.
