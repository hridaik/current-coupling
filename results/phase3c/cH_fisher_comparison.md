# Phase 3C-H1 — Fisher Comparison: ΔQ vs ΔΩ_full
Date: 2026-06-03
Authorization: Phase 3C-H

## Question

Is ΔΩ improving concentration of signal, or merely increasing AUROC through diffuse rank shifts?

---

## Full Results Table (CePNEM, K=20, degree-preserving null, 500 perms)

| Annotation | n | ΔQ AUROC | p_deg | ΔΩ AUROC | p_deg | ΔAUROC |
|---|---|---|---|---|---|---|
| **Bentley PDF** | 61 | 0.5560 | 0.026 | **0.6644** | **0.000** | **+0.108** |
| Bentley serotonin | 33 | 0.4953 | 0.546 | 0.5367 | 0.308 | +0.042 |
| Bentley combined | 94 | 0.5356 | 0.048 | **0.6231** | **0.000** | **+0.088** |
| CeNGEN ser/PDF | 382 | 0.5221 | 0.026 | 0.5174 | 0.148 | −0.005 |
| Randi unc-31 | 91 | 0.5007 | 0.484 | 0.4905 | 0.676 | −0.010 |

| Annotation | ΔQ OR | p_deg | k_dq | ΔΩ OR | p_deg | k_do | ΔOR |
|---|---|---|---|---|---|---|---|
| **Bentley PDF** | 5.46 | 0.014 | 4 | **7.41** | **0.000** | **5** | **+1.95** |
| Bentley serotonin | 0.00 | 1.000 | 0 | 0.00 | 1.000 | 0 | 0.00 |
| Bentley combined | 3.36 | 0.064 | 4 | **4.54** | **0.008** | **5** | **+1.18** |
| CeNGEN ser/PDF | 0.82 | 0.694 | 5 | 1.05 | 0.536 | 6 | +0.24 |
| Randi unc-31 | 0.00 | 1.000 | 0 | 0.00 | 1.000 | 0 | 0.00 |

Expected in top-20: Bentley PDF = 0.9, serotonin = 0.5, combined = 1.4, CeNGEN = 5.8, Randi = 1.4

---

## Answer: AUROC Increase Is Diffuse, Not Concentrated

**The Fisher top-20 analysis confirms Phase 3C-G's finding**: the AUROC increase is
NOT primarily driven by new pairs entering the top-20.

### Bentley PDF top-20 count: 4 → 5 (+1 pair)

One additional PDF pair enters the top-20 under ΔΩ (RMEL–URYVR, from rank 21 to 19).
The Fisher OR increases from 5.46 to 7.41 (+1.95), and the p-value sharpens to < 0.002.
This is a genuine improvement in top-K concentration, but driven by a single pair movement.

**Is this concentration or diffuse shift?** Both:
- The Fisher OR improvement (5.46 → 7.41) indicates that the top-20 is modestly
  more concentrated. This is a real signal-concentration effect, small but genuine.
- The AUROC improvement (+0.108) is much larger than the Fisher OR improvement
  would suggest for just 1 extra pair. The AUROC gain comes from diffuse mid-tier
  shifts (pairs at ranks 200–1300 moving), not from top-tier restructuring.

**Conclusion**: The top-20 concentration improves slightly (by 1 PDF pair); the
AUROC improvement is primarily diffuse, driven by zero-ΔQ pairs in the mid-to-bottom
of the ranking being assigned nonzero ΔΩ values.

### CeNGEN degradation: key diagnostic

The CeNGEN serotonin/PDF annotation (n=382, 29% of C4) degrades:
- AUROC: 0.522 → 0.517 (p_deg: 0.026 → 0.148, PASS → FAIL)
- Fisher OR: 0.82 → 1.05 (still below 1 and not significant)

**The CeNGEN degradation confirms that D_emp mixing is not selective for biology.**
A broad neuropeptide/receptor annotation (382 pairs) that previously showed weak AUROC
enrichment LOSES its signal under ΔΩ_full. If ΔΩ_full were selectively amplifying
biologically relevant pairs, it would not degrade the broad CeNGEN annotation.

The different behavior between Bentley PDF (small, specific, improves) and CeNGEN
(large, broad, degrades) reflects the hub structure: RID/RMEL/RMER are PDF-specific
hubs in D_emp, and their imputed zero-pairs happen to be Bentley-PDF-annotated but
not CeNGEN-annotated.

### Serotonin and Randi: unchanged null

Both serotonin (n=33) and Randi unc-31 (n=91) remain null in both ΔQ and ΔΩ.
The Fisher OR for serotonin is zero in both (no serotonin pairs in top-20).
The AUROC for Randi moves from 0.501 to 0.491 — within noise and not significant.

---

## Summary

| Criterion | ΔQ | ΔΩ_full | Verdict |
|---|---|---|---|
| Bentley PDF AUROC | 0.556 (PASS) | 0.664 (PASS) | ΔΩ stronger |
| Bentley PDF Fisher OR | 5.46 (PASS) | 7.41 (PASS) | ΔΩ stronger |
| Bentley combined AUROC | PASS | PASS | maintained |
| Bentley combined Fisher | FAIL | **PASS** | ΔΩ upgrades |
| CeNGEN AUROC | PASS | FAIL | ΔΩ DEGRADES |
| Randi | null | null | unchanged |
| **Signal concentration?** | — | — | **Marginal (+1 PDF in top-20)** |
| **Diffuse shifts?** | — | — | **Yes (primary mechanism)** |

The ΔΩ_full Fisher improvement is real but marginal at the top-20 level. The
AUROC gain is primarily diffuse, from mid-ranking zero-pairs being assigned
nonzero ΔΩ. The CeNGEN degradation shows this is not selective for biology.

---

*3C-H1 scope: Fisher comparison only.*
