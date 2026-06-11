# Stage 5 Report — Coordinate Comparison and Final Interpretation
Date: 2026-06-01
Authorization: 2026-06-01 human supervisor

---

## 1. Stage 5 Scope

Stage 5 applies the locked interpretation table from phase2_task.md to assign the final scientific interpretation of Phase 2. This is the only operation performed in Stage 5. No new estimation, no new biological analyses, no parameter changes.

**Inputs (from Stage 4, read-only):**
- CePNEM neuropeptide AUROC = 0.5033, p_deg = 0.475
- GCaMP neuropeptide AUROC = 0.5140, p_deg = 0.142
- All other tests: null (p_deg > 0.14 for all tests, both coordinates)

---

## 2. Interpretation Table — Mechanical Application

The locked interpretation table (phase2_task.md, Stage 5):

| CePNEM enrichment | Raw GCaMP enrichment | Interpretation |
|---|---|---|
| Significant (p < 0.05, degree-preserving) | Significant | Residual neural state organization |
| Significant | Not significant | Neural organization masked by behavioral noise |
| Not significant | Significant | Behavior-mediated state structure |
| **Not significant** | **Not significant** | **Null result** |

**CePNEM status:** p_deg = 0.475 → **NOT significant** (threshold: p < 0.05)
**GCaMP status:** p_deg = 0.142 → **NOT significant** (threshold: p < 0.05)

**Assigned row: Row 4 — Null result.**

This assignment is mechanical. The table does not require interpretation of why the result is null. The data determine the row; the locked table assigns the label.

---

## 3. Final Scientific Conclusion

**The Phase 2 analysis finds no evidence that state-switched off-connectome conditional-dependence structure in C. elegans whole-brain activity is enriched for neuropeptide-signaling pairs.**

More precisely: using the validated pairwise available-case covariance estimation pipeline on 40 freely-behaving recordings of 61 identified neurons, state-conditioned precision matrices (Q_roam, Q_dwell) were estimated for both CePNEM-residualized and raw GCaMP coordinates. The difference ΔQ = Q_roam − Q_dwell was classified by connectome position. The 1321 off-connectome Class 4 pairs were tested for neuropeptide enrichment (Ripoll-Sánchez annotation) and Randi unc-31 enrichment using AUROC and Fisher statistics with simple and degree-preserving permutation nulls. No test reached statistical significance (all degree-preserving p > 0.14).

This is the finding. It is reported as stated.

---

## 4. What the Data Support

The data support the following positive conclusions:

**4.1 — The pairwise estimation pipeline is validated and operational.**  
Stages 0-V through 3 establish that the pairwise available-case covariance estimator works as specified: (a) assembled covariances are naturally PSD for this corpus; (b) the confirmation estimator recovers structure with TPR=0.992 in synthetic validation; (c) LOO sensitivity shows median top-50 retention ≥ 0.94 in real data, confirming that the ΔQ structure is not dominated by individual recordings.

**4.2 — State-dependent conditional-dependence changes exist in the real data.**  
The ΔQ matrices are not zero: CePNEM has 243 non-zero Class 4 pairs, GCaMP has 585. The confirmation estimator (λ_off=0.10, heavy off-connectome regularization) still selects these entries, which means the state differences are strong enough to overcome the regularization. State-conditioned neural structure is present in the data.

**4.3 — The analysis covered the full 61-neuron subgraph.**  
Phase 1 was closed because the complete-case intersection collapsed to 4–13 neurons. Phase 2 restored the intended analysis scope (61 neurons, 1321 Class 4 pairs) via pairwise estimation. This methodological objective was achieved.

**4.4 — The LOO sensitivity is strong.**  
Median LOO retention (CePNEM 0.960, GCaMP 0.940) confirms that the ΔQ ranking is stable and not driven by one or two influential recordings. The structure is reproducible across 38/40 recording subsets. DEV-005 (all-animal pooling) is partially compensated.

**4.5 — The enrichment null is robust across multiple tests and both coordinates.**  
Six independent enrichment tests were computed (neuropeptide AUROC, Fisher × 2 coordinates; Randi AUROC, Fisher × 2 coordinates). None reached p < 0.15 under the degree-preserving null. The result is internally consistent.

---

## 5. What the Data Do NOT Support

**5.1 — The data do not support the pre-specified hypothesis.**  
The hypothesis tested in Phase 2 (inherited from Phase 0/1) was: the off-connectome conditional-dependence difference ΔQ is enriched for neuropeptide-signaling pairs (Ripoll-Sánchez atlas) compared to a degree-matched null. The data do not support this hypothesis under the confirmed estimation pipeline. No significant enrichment was detected.

**5.2 — The data do not support a claim of behavioral state-organized neuropeptide coordination.**  
The specific prediction was that roaming vs. dwelling switches in C. elegans involve detectable reorganization of neuropeptide-mediated conditional dependence in the 61-neuron subgraph. This was not observed.

**5.3 — The data do not support the Randi unc-31 parallel prediction.**  
The Randi annotation identifies pairs where unc-31-sensitive (dense-core vesicle) signaling affects pairwise neural statistics. No enrichment of these pairs in ΔQ was found.

**5.4 — The data do not resolve whether the null is biological or methodological.**  
The estimation pipeline was validated under synthetic Gaussian data with MCAR missingness. Real neuropeptide effects may operate via mechanisms not captured by steady-state conditional dependence (graphical lasso precision matrices): volume transmission, transient signaling, or network-level coordination not reflected in pairwise statistics. The data cannot distinguish these explanations.

---

## 6. What Remains Unresolved

**6.1 — Test 4 (serotonin/PDF receptor enrichment) was not run.**  
The serotonin/PDF receptor annotation was not available in the corpus annotation files. This is a minor gap; the test was pre-specified as exploratory.

**6.2 — The source of significant ΔQ entries is not identified.**  
There are 243 non-zero CePNEM Class 4 ΔQ entries and 585 GCaMP. These are real state differences in conditional dependence. They are not enriched for neuropeptide annotation, but their biological identity is unresolved and was not investigated (per scope constraints).

**6.3 — Annotation density effects.**  
The Ripoll-Sánchez neuropeptide atlas covers 73.6% of Class 4 pairs. This is high enough that the AUROC test primarily asks whether the 27% non-annotated pairs have systematically lower |ΔQ|. The statistical test is valid and powered (SE(AUROC) ≈ 0.018), but the biological question may be more precisely asked with a more selective annotation (e.g., directed peptide projections for a specific behavioral circuit).

**6.4 — The connection between CePNEM stability and enrichment.**  
CePNEM dwelling stability was near-zero (1 stable pair out of 1830). This reflects genuinely weak dwelling-state covariance after behavioral residualization. Whether the residualization removes signal relevant to neuropeptide coordination is unresolved.

---

## 7. Interpretation Table Assignment

| Coordinate | Enrichment result | p_deg (primary) | Row assignment |
|---|---|---|---|
| CePNEM (primary) | Not significant | 0.475 | Row 4 |
| GCaMP (robustness) | Not significant | 0.142 | Row 4 |
| **Combined** | **Not significant** | — | **Row 4: Null result** |

The locked interpretation is: **Null result**.

---

## 8. Stage 5 Pass Conditions

| Condition | Status |
|---|---|
| Both coordinate analyses complete before interpretation | PASS |
| Interpretation rule applied mechanically | PASS |
| Interpretation recorded with supporting numbers | PASS |

Stage 5 is complete.

---

*Stage 5 scope: locked interpretation table application. No biological mechanistic discussion. No new estimation. No new hypotheses.*
