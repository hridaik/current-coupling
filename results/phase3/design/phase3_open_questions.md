# Phase 3 Open Questions
Date: 2026-06-03

These questions must be resolved (or explicitly accepted as a modeling choice) before Phase 3A begins.
They are organized by type: scientific, methodological, and data.

---

## Scientific Questions

### OQ-S1: What does J represent?

**Question**: Is J the anatomical synaptic connectivity (A_raw), the dynamically-inferred effective connectivity (Creamer A_C), or something else?

**Why it matters**: The model J_eff = J + αP asserts that the observed precision structure derives from two sources — anatomy and PDF modulation. If J is A_raw (structural), it may differ substantially from the actual effective connectivity at the timescale of calcium imaging (~5 Hz). If J is Creamer A_C (dynamically inferred), it already incorporates some effective-connectivity that may absorb PDF effects, making α non-identifiable.

**Key complication**: Creamer A_C was fitted to state-averaged data from a different corpus (Creamer 154-neuron LDS), not to roaming/dwelling-separated data. If A_C already absorbed PDF-mediated effects in the training data, then J_eff = A_C + αP would double-count.

**Options**:
1. Use A_raw: clean separation between anatomy and dynamics
2. Use A_C: more accurate base, but risk of circularity
3. Use J = 0: fully phenomenological, avoids anatomical assumptions entirely
4. Fit J jointly with α (very expensive; requires additional constraints)

**Resolution needed before Phase 3A**.

---

### OQ-S2: Is the PDF signaling graph directed or undirected?

**Question**: Should P be the directed (asymmetric) Bentley matrix or its symmetrized version?

**Why it matters**: PDF signaling is directional — ADEL (source, pdf-1-expressing) → URYVR (target, pdfr-1-expressing). An asymmetric J_eff may produce complex (non-real) eigenvalues, complicating stability analysis and the Lyapunov solution.

The precision matrix Q (from graphical lasso) is by construction symmetric. If Q = −J_eff^{−1} and J_eff is asymmetric, then −J_eff^{−1} is generally asymmetric — inconsistent with a symmetric Q.

**Resolution options**:
1. Symmetrize P and constrain J_eff to be symmetric (clean; loses directional information)
2. Use directed P but symmetrize J_eff before Lyapunov solve (ad hoc)
3. Work in the directed framework and use a non-symmetric forward model (requires different inference framework)
4. Note that for CLASS 4 pairs, the pairs in Bentley are directed but when restricted to (i,j) with i<j (upper triangle), each pair is undirected anyway — so symmetrization may be harmless at the pair level even if directional at the neuron level

**Resolution needed before Phase 3A**.

---

### OQ-S3: What is the noise covariance D?

**Question**: In the Lyapunov equation J_eff Σ + Σ J_eff^T = −D, what is D?

**Why it matters**: D determines the absolute scale of Σ and hence Q. If D is misspecified, Q_model will have the right structure but wrong scale, making objective functions based on absolute values (Objective B, C) unreliable.

**Options**:
1. D = I: simplest; assumes homogeneous noise; may be inconsistent with observed diagonal variance structure
2. D = diag(σ²_i): per-neuron noise variance estimated from Phase 2 residuals; more accurate; still ignores noise correlations
3. D = estimated from data: requires additional fitting; significantly increases model complexity
4. Avoid D entirely by working only with rank-correlation objectives (Objective A), which are scale-invariant

**If Objective A (rank correlation) is the primary fitting objective, D is irrelevant**. D only matters if Objective B or C is used.

**Resolution needed before Phase 3A if B or C objectives are used**.

---

### OQ-S4: Does the Lyapunov forward model apply to CePNEM residuals?

**Question**: CePNEM residuals are behavioral-confound-removed neural traces. The linear dynamics model assumes x_t comes from a stationary Gaussian process. Does this assumption hold for CePNEM residuals?

**Known complication**: Phase 2D showed systematic state-time segregation (roaming early, dwelling throughout). Even after CePNEM residualization removes behavioral regressors, the residuals may retain state-dependent structure that the LDS model does not account for.

**Additionally**: The CePNEM model already uses a different set of dynamics (LGSSM structure). The residuals are not the raw calcium traces; they are outputs of a model that presumably already captured most of the linear dynamics. The residual process may have weaker autocorrelation than the raw traces.

**This does NOT affect Phase 2 analysis** (which used graphical lasso, not LDS), but IS relevant for Phase 3 which interprets Q as arising from linear Gaussian dynamics.

**Options**:
1. Accept the LDS assumption as an approximation; validate that Q_model is qualitatively consistent with Q_obs
2. Use raw GCaMP traces as primary input to Phase 3 (unresidated; more consistent with LDS)
3. Use the CePNEM residuals but accept the limitation and report it explicitly

**Resolution needed before Phase 3A**. See OQ-M4 for the CePNEM vs. GCaMP choice.

---

### OQ-S5: Is α_s a scalar or a matrix?

**Question**: Should the PDF gain be a single scalar per state (α_s ∈ ℝ) or a more general matrix (A_s ∈ ℝ^{N×N})?

**Why it matters**: A scalar α assumes all PDF edges scale uniformly with behavioral state. A matrix allows different gains for different source-target pairs. Biologically, different neurons may have different pdfr-1 expression levels, different sensitivities.

**Practical constraint**: With only 61 PDF Class 4 pairs and 243 nonzero ΔQ entries, fitting a general matrix is severely underdetermined (61 free parameters from 243 observations, but with strong collinearity among PDF pairs).

**Options**:
1. Scalar α_s: parsimony; identified (2 free parameters)
2. Source-specific scalar: one α per PDF source neuron (5 sources: RID, AVDL, ADEL, RMEL, RMER = 5 × 2 states = 10 parameters). Identifiable if sources are spread across the ΔQ distribution.
3. Full matrix: not identified given current data
4. Low-rank decomposition: α_s = sum_k β_k u_k v_k^T where K is small (e.g., K=1 or 2)

**Recommendation**: Start with scalar α_s. After fitting, test whether source-specific scalars improve fit significantly (AIC/BIC comparison with 8 additional parameters).

---

### OQ-S6: How to handle the 44 PDF pairs with ΔQ = 0?

**Question**: 44 of 61 PDF Class 4 pairs have zero CePNEM ΔQ. How should these enter the model?

**Why it matters**: These pairs are annotated as PDF but show no state-dependent coupling change. Under the model J_eff = J + αP, if α ≠ 0, ALL PDF pairs should show nonzero ΔQ_model. The model predicts a signal where the data shows none for 72% of PDF pairs.

**Biological interpretation**: The 44 zero-ΔQ PDF pairs may have genuinely weak coupling (too weak for the confirmation estimator to detect). The graphical lasso confirms only pairs where signal exceeds the λ_off = 0.10 threshold; weaker pairs are set to zero.

**Options**:
1. Treat zero-ΔQ pairs as censored (the true ΔQ is below detection threshold, not necessarily zero). Use a censored regression or tobit objective.
2. Treat zero-ΔQ pairs as genuine zeros and penalize the model for predicting nonzero ΔQ there.
3. Exclude zero-ΔQ pairs from the objective and evaluate only on pairs where ΔQ ≠ 0.
4. Use absolute ΔQ values in Spearman rank — zeros all get tied ranks; the 17 nonzero PDF pairs drive the correlation.

**Resolution needed before Phase 3A: the treatment of zero-ΔQ pairs fundamentally changes the objective**.

---

## Methodological Questions

### OQ-M1: Is the model identifiable?

**Question**: Given the training data, can (α_roam, α_dwell) be uniquely estimated?

**Known issue (Form E)**: If ΔQ_model = f(α_dwell − α_roam) only depends on the difference Δα, then the two parameters are not jointly identified from ΔQ alone. One parameter must be anchored.

**Resolution strategy**: Use both Q_roam^{model} and Q_dwell^{model} simultaneously in the objective (Objective B), not just their difference. This breaks the Δα-only identification and allows joint estimation.

**Verification**: Before fitting, run an identifiability check:
1. Generate synthetic data from M1 with known (α̂_r, α̂_d)
2. Fit from random starting points; check whether the optimizer converges to the true values
3. If α_r and α_d are not jointly recovered, switch to anchored form (anchor α_r = 0)

---

### OQ-M2: How to handle the extreme sparsity of ΔQ?

**Question**: 1078 / 1321 = 82% of Class 4 ΔQ entries are exactly zero (from graphical lasso regularization). The rank correlation objective will have many tied ranks at zero. Does this degrade the quality of the fitting objective?

**Concern**: If 82% of pairs have ΔQ = 0, the rank correlation is dominated by tie-breaking. Spearman rank correlation treats all zeros as equal rank, which is reasonable but means the objective signal comes primarily from the 243 nonzero pairs.

**Options**:
1. Restrict objective to nonzero ΔQ pairs only (243 pairs). Reduces statistical power.
2. Use a soft-thresholded Spearman: weight pair by min(|ΔQ_obs|, threshold) to emphasize signal.
3. Use Kendall's τ instead of Spearman — less sensitive to extreme ties.
4. Accept Spearman with tied zero ranks; the 243 nonzero pairs still provide sufficient signal for a 2-parameter model.

---

### OQ-M3: What is the appropriate null distribution for α?

**Question**: How do we assess whether the fitted α is significantly different from zero?

**Approaches**:
1. Bootstrap CI (recorded in Phase 3B plan): does the CI for Δα = α_dwell − α_roam exclude zero?
2. Permutation test: compare fitted objective L(α̂) to distribution under M2 (randomized P)
3. Likelihood ratio test: L(M1) vs L(M0) under Objective C

**Resolution needed before Phase 3B**: the inference framework must be pre-specified.

---

### OQ-M4: Should Phase 3 use CePNEM residuals or raw GCaMP?

**Question**: Phase 2 primary analysis used CePNEM residuals; Phase 2B exploratory found PDF signal in CePNEM (not GCaMP). For Phase 3, which coordinate should be primary?

**Arguments for CePNEM**:
- PDF signal was detected in CePNEM (AUROC=0.556)
- Residualization removes behavioral confounds; the precision matrix reflects purer neural coupling
- OQ-S4 notes potential LDS assumption issues, but CePNEM is the Phase 2 primary coordinate

**Arguments for GCaMP**:
- Raw GCaMP is more consistent with the LDS interpretation (raw dynamics without residualization)
- Creamer used raw calcium (or normalized calcium), not CePNEM residuals
- The LDS model is more naturally applicable to raw signals

**Recommendation**: Use CePNEM as primary (consistent with Phase 2 primary result). Use raw GCaMP as robustness check. Document the disconnect between LDS assumptions and CePNEM residuals explicitly.

---

### OQ-M5: Can the Creamer A_C matrix be reliably extracted for the 56-neuron subspace?

**Question**: The Creamer data (`data/creamer/Creamer_LDS_2026/`) contains 154 neurons. The Phase 2 Creamer 56-neuron subspace is the intersection with our 61-neuron list. Can A_C be extracted?

**Technical issue**: The Creamer model is stored as `models/fully_connected.pkl` and requires the `ssm_classes` module from the Creamer package. The module is available in `data/creamer/Creamer_LDS_2026/ssm_classes.py` but hasn't been imported in this project.

**Two sub-questions**:
1. Can the A_C matrix be extracted from the fitted Creamer model?
2. Is the 56×56 submatrix of A_C a valid effective connectivity matrix, or does subspace extraction introduce errors (off-subspace marginalization)?

**Resolution needed before Phase 3A if J3 (Creamer A_C) is used**.

---

### OQ-M6: How to handle the CePNEM dwelling stability anomaly?

**Question**: Phase 2 showed near-zero CePNEM dwelling stability (1/1830 stable pairs at threshold 0.75). The confirmation estimator still produced 305 nonzero Q_dwell_cepnem entries. But the dwelling precision matrix may be less reliable than the roaming precision matrix.

**For Phase 3**: Should Q_roam and Q_dwell be weighted differentially in the objective, given their different estimation reliability?

**Options**:
1. Equal weight (ignore stability discrepancy)
2. Down-weight Q_dwell contribution by factor proportional to median dwelling stability / median roaming stability
3. Use only |ΔQ| = |Q_roam − Q_dwell| and avoid modeling Q_s individually (directly uses Form E)

---

## Data Questions

### OQ-D1: Is the PDF directed-pair structure complete?

**Question**: The Bentley ESconnectome PDF annotation was constructed from literature curation of directed signaling pairs. Is the annotation complete for all 61 neurons, or are there plausible PDF edges missing?

**Known gaps from Phase 2B**:
- ADEL→URYVR and ADEL→URYDL have occ_funatlas = 0 (never measured in perturbation atlas)
- RID→URXL: occ_wt = 2 (borderline measured)
- AVDL: pdf-2 source but fewer documented targets

**Implication for Phase 3**: The P matrix has known false negatives (missing PDF edges). Fitting α with incomplete P will underestimate α. If the model fails, it might be because P is incomplete rather than because the model is wrong.

**Resolution**: Document the known gaps explicitly. Run sensitivity analysis with augmented P (add CeNGEN expression-based pairs not in Bentley).

---

### OQ-D2: Are there PDF pairs that are on-connectome and therefore excluded?

**Question**: The Phase 2 analysis uses Class 4 pairs (off-connectome, both in Creamer). PDF pairs that are on-connectome (Class 1 or 2) are excluded from the enrichment test. Do important PDF pairs fall outside Class 4?

**Known from Phase 2D**: Several Bentley PDF pairs are on-connectome and NOT in Class 4:
- ADEL–AVDL: on-connectome (synaptic)
- ADEL–FLPL, ADEL–OLLL, ADEL–RMER: on-connectome
- OLLL–RMEL, OLLR–RMEL, OLLR–RMER: on-connectome
- RMEL–URYDL: Class 4 (off-connectome) — INCLUDED
- AVDL–URYDL: Class 4 — INCLUDED

**Implication for Phase 3**: The model J_eff = J + αP should include ALL PDF pairs in P, not just Class 4. The evaluation is conducted on Class 4 pairs, but the model should account for the full P structure including on-connectome PDF edges (which contribute to dynamics through J and αP together, not separately).

This means the P matrix for Phase 3 should be the full 61×61 Bentley PDF directed matrix, not filtered to Class 4 only. The Class 4 filter applies to evaluation only, not to the model specification.

---

### OQ-D3: What recordings to include in fitting vs. evaluation?

**Question**: Phase 2 used all 40 recordings pooled. Should Phase 3 use the same 40 recordings, or should a recording-level train/test split be used?

**Considerations**:
1. The ΔQ matrices (from Phase 2 Stage 2) are already aggregated over all 40 recordings. Recording-level splits cannot be applied post-hoc without re-running the Phase 2 estimator.
2. The Phase 2 sufficient statistics (n_frames, suf_xi, suf_xixj) are saved per recording and could be used to compute ΔQ for recording subsets — but this would constitute "re-running Stage 2" which is outside Phase 3 scope.
3. Bootstrap uncertainty (recording-level resampling) is used for CI estimation in Phase 3B. This provides a form of recording-level cross-validation without requiring new Stage 2 runs.

**Resolution**: Use the Phase 2 Stage 2 ΔQ matrices as fixed inputs. Recording-level uncertainty is addressed through bootstrap CI in Phase 3B. No new Stage 2 estimation is authorized.

---

### OQ-D4: Should GCaMP provide additional constraint on α?

**Question**: PDF AUROC is null in GCaMP (p_deg=0.261). Does this mean:
(a) PDF effects are absent in raw calcium, or
(b) PDF effects exist but are masked by behavioral confounds in GCaMP?

**Why it matters for Phase 3**:
- If (a): The Phase 3 model should predict NULL PDF signal in GCaMP, which means the GCaMP ΔQ provides no constraint on α and should be excluded from fitting.
- If (b): The GCaMP ΔQ contains PDF signal mixed with behavioral noise. Using it in fitting could add noise rather than signal.

**Recommendation from Phase 2B**: The CePNEM specificity (PDF pass in CePNEM, fail in GCaMP) is "consistent with signal present after behavioral confound removal." This supports interpretation (b). Therefore GCaMP should not be used as a primary fitting input — its PDF signal is masked, not absent.

**Implication**: Phase 3 uses CePNEM ΔQ as the primary fitting target. GCaMP ΔQ serves as a negative robustness check only.

---

## Questions Requiring Human Resolution Before Phase 3A

The following questions have answers that significantly affect Phase 3A implementation and cannot be resolved by the analysis team alone:

| ID | Question | Options | Decision needed by |
|---|---|---|---|
| OQ-S1 | Which J matrix? | A_raw, A_C, A_chem, J=0 | Before Phase 3A |
| OQ-S2 | Symmetric or directed P? | Symmetric (default) or directed | Before Phase 3A |
| OQ-S6 | Treatment of zero-ΔQ PDF pairs | Censored, excluded, or rank-tied | Before Phase 3A |
| OQ-M3 | Null distribution for α | Bootstrap, permutation, or LRT | Before Phase 3B |
| OQ-M5 | Use Creamer A_C? | Yes (requires ssm_classes import) or No | Before Phase 3A |

---

*Open questions file. No implementation decisions. No fitting recommendations beyond what is required for Phase 3A setup.*
