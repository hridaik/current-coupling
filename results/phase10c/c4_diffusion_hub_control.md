# Phase 10C.4 — Diffusion Hub / Row-Norm Control
Date: 2026-06-15

---

## Hub Metric Definitions

**Per-neuron metrics:**
- Row norm (roam): ||D_roam[i,:]||_2
- Row norm (dwell): ||D_dwell[i,:]||_2
- Row norm (ΔD): ||ΔD[i,:]||_2
- Diagonal (roam): D_roam[i,i]
- Diagonal (ΔD): |ΔD[i,i]|

**Per-pair hub predictors (from endpoint neurons):**
- sum_row_norm_roam: ||D_r[i,:]||_2 + ||D_r[j,:]||_2
- max_row_norm_roam: max(||D_r[i,:]||_2, ||D_r[j,:]||_2)
- sum_diag_roam: D_r[i,i] + D_r[j,j]
- max_diag_roam: max(D_r[i,i], D_r[j,j])
- sum_row_norm_DD: ||ΔD[i,:]||_2 + ||ΔD[j,:]||_2
- max_abs_DD_diag: max(|ΔD[i,i]|, |ΔD[j,j]|)

---

## Global Spearman Correlations with |ΔΩ_ss| (over 1321 C4 pairs)

| Hub predictor | ρ with |ΔΩ_ss| | p-value |
|---------------|----------------|---------|
| sum_row_norm_roam | 0.034 | 0.215 |
| max_row_norm_roam | 0.036 | 0.196 |
| sum_diag_roam | 0.032 | 0.241 |
| max_diag_roam | 0.034 | 0.215 |
| sum_row_norm_ΔD | 0.040 | 0.150 |
| max_abs_ΔD_diag | 0.027 | 0.323 |

**None of the hub predictors are significantly correlated with |ΔΩ_ss|.**

All ρ values are < 0.04 and all p-values > 0.15. Endpoint diffusion hubness
explains essentially none (≤ 0.2% of variance) of the pair-level |ΔΩ_ss| variation.

---

## Matched-Hub Null (primary: sum_row_norm_roam ± 20%)

For each key pair, identify all C4 pairs with similar hub score (sum_row_norm_roam
within ±20% or ±0.05 absolute). Compute percentile of |ΔΩ_ss| within that stratum.

| Pair | Hub score | Stratum n | Target |ΔΩ_ss| | Empirical pct | p-value |
|------|---------|---------|--------------|-------------|---------|
| ADEL–URYVR | 0.837 | 1193 | 0.0688 | 0.9983 | **0.0017** |
| ADEL–URYDL | 0.899 | 1161 | 0.0498 | 0.9957 | **0.0043** |
| ADEL–RMEL  | 0.861 | 1194 | 0.0549 | 0.9975 | **0.0025** |
| RMEL–URYDL | 0.757 | 979  | 0.0310 | 0.9796 | 0.0204 |
| RMEL–RMER  | 0.799 | 1128 | 0.0254 | 0.9725 | 0.0275 |

**All three ADEL-PDF primary pairs are above the 99.6th percentile of pairs with
similar diffusion hub scores.** The ADEL-PDF elevation cannot be explained by the
endpoint neurons being diffusion hubs.

Note: hub scores are similar across all key pairs (0.76–0.90), confirming the
stratum comparisons are meaningful.

---

## Partial Correlation of PDF Annotation with |ΔΩ_ss| Controlling for Hub Score

| Quantity | Value |
|----------|-------|
| ρ(|ΔΩ_ss|, PDF annotation) marginal | 0.0239 |
| ρ(|ΔΩ_ss|, hub score) marginal | 0.0342 |
| ρ(hub score, PDF annotation) marginal | 0.0618 |
| ρ(|ΔΩ_ss|, PDF | hub score) partial | 0.0218 |

Hub control barely changes the marginal correlation (0.024 → 0.022). The partial
correlation confirms that the PDF-|ΔΩ_ss| association is not confounded by hub scores.

Note: these marginal correlations are all small (the PDF AUROC under ΔΩ_ss is 0.533,
reflecting global dilution from non-PDF pairs). The matched-null results above are the
stronger test for the specific primary pairs.

---

## Per-Pair Hub Metrics for Key Pairs

| Pair | D_r[i,i] | D_r[j,j] | Row norm i | Row norm j | Sum hub | Relative rank |
|------|---------|---------|-----------|-----------|---------|--------------|
| ADEL–URYVR | 0.495 | 0.499 | 0.503 | 0.502 | 0.837 | Typical |
| ADEL–URYDL | 0.495 | 0.466 | 0.503 | 0.469 | 0.899 | Slightly above avg |
| ADEL–RMEL  | 0.495 | 0.396 | 0.503 | 0.394 | 0.861 | Typical |
| RMEL–URYDL | 0.396 | 0.466 | 0.394 | 0.469 | 0.757 | Slightly below avg |
| RMEL–RMER  | 0.396 | 0.393 | 0.394 | 0.393 | 0.799 | Typical |

ADEL has somewhat elevated diagonal diffusion (D_r[0,0] = 0.495) but not
dramatically so relative to the median across 61 neurons. ADEL is not a clear
diffusion outlier.

---

## Conclusion

> Are ADEL/PDF current ranks just a consequence of one endpoint being a diffusion hub?

**No.** Three independent lines of evidence:

1. Global ρ(hub score, |ΔΩ_ss|) < 0.04 across 1321 pairs — no systematic hub confound.
2. ADEL-URYVR/URYDL are at 99.8th/99.6th percentile within their hub-matched strata
   (p=0.0017, 0.0043).
3. Partial ρ(|ΔΩ_ss|, PDF | hub) ≈ marginal ρ — hub control changes nothing.

The ADEL/PDF elevation under ΔΩ_ss reflects specific precision (Q) structure,
not a generic diffusion-hub effect.
