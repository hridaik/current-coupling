# Phase 3 Design Package
## State-Dependent PDF Effective-Connectivity Model

Date: 2026-06-03  
Status: Design only. No model fitting. No simulation. No parameter estimation.

---

## Background

Phase 2 established:

- **Primary result**: Broad neuropeptide enrichment is null. Randi null. Behavioral ΔQ structure exists (243 nonzero Class 4 CePNEM pairs, 585 GCaMP) but is not globally enriched for annotated neuromodulatory pairs.
- **Exploratory result**: Bentley PDF annotation passes in CePNEM (AUROC=0.556, p_deg=0.023; Fisher OR=5.456, p_deg=0.008). This signal is post-hoc, not pre-specified, and is treated as hypothesis-generating.
- **Strongest novel predictions**: ADEL–URYVR (rank 5) and ADEL–URYDL (rank 9) among 1321 Class 4 pairs. These pairs have NEVER been measured in the Randi perturbation atlas.
- **Signal direction**: All top PDF pairs have ΔQ < 0 (dwelling-dominant conditional dependence; Q_dwell > Q_roam).

Phase 3 objective: replace post-hoc enrichment with a forward mechanistic model. The question is no longer "what ΔQ exists?" but "does a PDF signaling model predict the observed ΔQ structure?"

---

## 1. Candidate Model Family

### 1.1 Core formulation

The central model family is:

```
J_eff(s) = J + α_s * P
```

where:

- **J**: anatomical effective-connectivity base matrix (61×61, or 56×56 for Creamer subspace)
- **P**: PDF signaling graph (directed, 61×61)
- **α_s ∈ ℝ**: state-dependent scalar gain, s ∈ {roam, dwell}
- **J_eff(s)**: the effective connectivity matrix for behavioral state s

The forward model maps J_eff(s) to an observable precision matrix Q_s, yielding a predicted:

```
ΔQ_model = Q_roam^{model} - Q_dwell^{model}
```

which is compared to the Phase 2 observed ΔQ.

---

### 1.2 The J matrix: candidate choices

Three candidates, ordered by modeling philosophy:

**J1 — Anatomical adjacency (A_raw)**
- 61×61 binary synaptic adjacency from White 1986 + Witvliet 2020 (both chemical + electrical)
- 260 undirected on-connectome edges
- Pros: directly available, maximally conservative assumption
- Cons: directed vs. undirected ambiguity; mixes chemical and electrical

**J2 — Chemical-only adjacency (A_chem)**
- Chemical synapses only, threshold ≥ 1 synapse
- Captures directed neurotransmitter-mediated connectivity
- Pros: more mechanistically motivated (neuropeptide volume transmission is analogous to chemical synapses in timescale)
- Cons: loses gap junction contribution

**J3 — Creamer LDS dynamics matrix (A_C)**
- From Creamer et al. 2026: A_C is the anatomically constrained LGSSM transition matrix fitted to freely-behaving calcium imaging data
- Restricted to the 56-neuron Creamer subspace (56×56; the same 56 neurons from Phase 2 Class 4 analysis)
- Pros: incorporates dynamical fitting from real data; represents actual inferred effective connectivity; available from `data/creamer/Creamer_LDS_2026/`
- Cons: fitted to a different corpus; Creamer dataset uses 154 neurons — the 56-subspace A_C must be extracted; state-averaged (not roaming/dwelling-specific)

**J0 — Null anatomy (zero matrix)**
- J = 0, so J_eff(s) = α_s * P
- Purely phenomenological: all state-dependent structure attributed to PDF
- Pros: eliminates anatomical assumptions; maximal parsimony
- Cons: biologically implausible for non-PDF pairs; treats all ΔQ as PDF-driven

**Recommendation**: Use J1 (A_raw) as primary and J3 (Creamer A_C) as a robustness check. J0 provides a lower bound on anatomical confounding.

---

### 1.3 The P matrix: PDF signaling graph

**P_Bentley**: Directed Bentley ESconnectome PDF annotation
- From `data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_neuropeptides_Bentley_2016.csv`
- Restricted to 61-neuron subgraph: 74 directed edges (before Class 4 filter)
- Class 4 pairs only: 61 undirected pairs
- Directed interpretation: P[i,j] = 1 if neuron i expresses pdf-1 or pdf-2 and neuron j expresses pdfr-1 per Bentley curation
- Matrix representation: asymmetric (directed), but the Class 4 filter makes most relevant entries off-connectome

**P_CeNGEN**: Expression-based ligand-receptor pairs (pdf-1/pdf-2 → pdfr-1)
- From CeNGEN conservative threshold 3: broader, more speculative
- 409 Class 4 pairs at 31% density — substantially sparser signal in individual pairs
- Use as exploratory robustness check only

**Matrix formulations for P**:

1. **Directed (asymmetric)**: P[source, target] = 1. Use as-is for asymmetric J_eff.
2. **Symmetrized**: P_sym = (P + P^T) / 2. Required if J_eff is constrained to be symmetric (needed for real-eigenvalue stability analysis).
3. **Normalized**: P / ||P||_F. Scale-free; α absorbs the magnitude.
4. **Weighted by synapse count**: P[i,j] = Bentley edge weight (if available). Not currently available in Phase 2 data.

**Primary choice**: P_Bentley, symmetrized (P_sym = (P + P^T) / 2), normalized by Frobenius norm. Directed version used as sensitivity check.

---

### 1.4 Alternative operator forms

Beyond the basic J_eff = J + αP, six alternative forms are documented:

**Form A (additive, linear)** — PRIMARY:
```
J_eff(s) = J - γI + α_s * P_sym
```
The -γI term ensures baseline stability (diagonal stabilizer). γ is a positive nuisance parameter fixed by requiring all eigenvalues of J - γI to be negative.

**Form B (multiplicative modulation)**:
```
J_eff(s) = J ⊙ (I + α_s * P_norm)
```
Element-wise scaling: PDF modulates existing anatomical weights rather than adding new pathways. Requires on-connectome entries of P to be nonzero (which they largely are not for PDF Class 4 pairs — this form is likely near-equivalent to Form A for off-connectome pairs).

**Form C (rank-1 perturbation)**:
```
J_eff(s) = J + α_s * u_s * v_s^T
```
u_s = vector of pdf-1/pdf-2 source neuron indicators; v_s = vector of pdfr-1 target indicators. Reduces to J_eff = J + αP when P is a rank-1 outer product — not generally true for Bentley P. This form assumes a single unified signaling mode; biologically restrictive.

**Form D (state-switching with baseline)**:
```
Q_s^{model} = Q_base + α_s * P_Q
```
Model directly in precision space. P_Q = symmetrized PDF pair indicator matrix. Q_base is estimated from anatomy (e.g., -J_base^{-1}). Bypasses the Lyapunov equation. Less principled but simpler to fit.

**Form E (differential)**:
```
ΔQ_model = (α_roam - α_dwell) * G(J, P)
```
where G is a matrix-valued function of J and P. If α_roam and α_dwell enter only as a difference, the model is not separately identifiable — only Δα = α_roam - α_dwell is identified. This form makes identifiability explicit. Useful if the goal is predicting ΔQ without recovering individual Q_s.

**Form F (full state-switching LDS)**:
```
dx/dt = J_eff(s) * x + noise
Σ_s from Lyapunov: J_eff(s) Σ_s + Σ_s J_eff(s)^T = -D
Q_s = Σ_s^{-1}
```
Most principled: derives Q from first-principles linear dynamics. Requires specifying noise covariance D (see Open Questions §2). This is the form that most naturally connects to the Creamer LDS framework.

**Recommended primary form**: Form A with the Lyapunov forward model (Form F derivative). Form D as a fast exploratory approximation. Form E for identifiability analysis before committing to Form A.

---

## 2. Stability Constraint

### 2.1 Requirement

For all parameter values considered in fitting:

```
max Re(λ(J_eff(s))) < 0    for s ∈ {roam, dwell}
```

This is the necessary condition for the linear dynamical system to have a well-defined steady-state covariance.

Equivalently, for symmetric J_eff: J_eff must be negative definite (all eigenvalues strictly negative).

### 2.2 Baseline stabilizer γ

The anatomical J matrices (A_raw, A_C) are not guaranteed to be stable. A diagonal stabilizer is added:

```
J_base = J - γ * I
```

γ is chosen as the smallest value such that J_base is stable:
```
γ_min = max(Re(λ(J))) + ε
```
where ε = 0.01 is a small margin. γ is treated as a fixed nuisance parameter, not fitted.

Implementation:
```python
gamma = np.max(np.real(np.linalg.eigvals(J))) + 0.01
J_base = J - gamma * np.eye(N)
assert np.all(np.real(np.linalg.eigvals(J_base)) < 0)
```

### 2.3 α feasibility region

For J_eff(s) = J_base + α_s * P_sym, the maximum stable α is:

```
α_max(s) = inf{α : max Re(λ(J_base + α * P_sym)) ≥ 0}
```

This is computed numerically by:
1. Starting from α = 0 (known stable)
2. Increasing α until the real part of the dominant eigenvalue crosses zero
3. Binary search for α_max to within tolerance 1e-4

For negative α (the expected direction, given dwelling-dominant PDF signal):
```
α_min(s) = sup{α < 0 : max Re(λ(J_base + α * P_sym)) ≥ 0}
```

The feasible region for (α_roam, α_dwell) is:
```
{(α_r, α_d) : α_min < α_r < α_max AND α_min < α_d < α_max}
```

### 2.4 Distance-to-instability

For each fitted (α_roam, α_dwell), report:

```
distance_to_instability(s) = α_max(s) - α_s     if α_s > 0
                            = α_s - α_min(s)      if α_s < 0
```

Expressed as fraction of feasible range: 0 = at stability boundary, 1 = at α = 0.

A fitted α with distance < 0.1 (within 10% of instability boundary) should be flagged as a potentially pathological fit.

### 2.5 Lyapunov solution

Given stable J_eff and noise covariance D:

```
J_eff Σ + Σ J_eff^T = -D
```

Solved using `scipy.linalg.solve_continuous_lyapunov(J_eff, -D)`.

Initial choice: D = I (homogeneous noise). Robustness check: D = diag(σ²_i) with per-neuron noise estimated from residual variance.

```
Q_model(s) = inv(Σ(s))
```

---

## 3. The PDF-State Paradox and Fitting Framework

### 3.1 The apparent contradiction

**Literature**: "PDF promotes roaming" (Choi et al. 2013; Flavell et al. 2020 review).

**Phase 2 result**: All top PDF Class 4 pairs have ΔQ < 0, meaning Q_dwell > Q_roam. Conditional dependence among PDF pairs is STRONGER during dwelling than roaming.

At first reading, these appear contradictory: if PDF promotes roaming, should PDF pairs not show stronger coupling during roaming?

### 3.2 Resolution: causal vs. correlational state assignment

The contradiction dissolves when the causal direction is specified:

**Causal chain**: Dwelling state → PDF release → PDF-mediated coupling → TRANSITION to roaming.

Under this chain:
- PDF signaling is ACTIVE DURING DWELLING (as a dwelling-exit mechanism)
- The functional coupling between PDF source and target neurons (ADEL → URY, RMEL → URY) is measurable in dwelling because that is when PDF is being released
- Once the transition completes, the animal is roaming — and PDF signaling is no longer driving anything, so coupling is absent

**Prediction from this chain**: α_dwell > 0, α_roam ≈ 0 (or α_roam < α_dwell).

This is consistent with the known biology:
- ADEL is a dopaminergic mechanosensory neuron active when the animal is stationary (dwelling); its output DECREASES during locomotion
- PDF signaling in *Drosophila* is known to reset circadian arousal from a quiet/sleep-like state into activity — a direct analogy to dwelling-to-roaming transitions
- URX neurons (also showing PDF-correlated ΔQ) integrate O₂/social signals and modulate arousal state; pdfr-1 expression there is consistent with dwelling-phase sensitization

### 3.3 Fitting framework — no pre-specified sign of α

**CRITICAL**: α_roam and α_dwell must NOT be assumed to have any particular sign or ordering. The fitting framework:

1. **Treat (α_roam, α_dwell) as two free scalar parameters**
2. **Fit both simultaneously from data** (using the anti-circular design in Section 4)
3. **Report the estimated values and their confidence intervals**
4. **Interpret post-hoc**: compare estimated values to the causal chain prediction

The prior expectation (α_dwell > α_roam, both likely non-positive given dwelling-dominant ΔQ signal) is stated here for transparency but is NOT encoded as a constraint in the fitting.

**Identifiability note (Form E)**:

If the model is written as ΔQ_model = f(α_dwell - α_roam), then only Δα = α_dwell - α_roam is identified from ΔQ alone. To identify α_roam and α_dwell separately, one of two strategies is needed:

1. **Anchor**: Fix α_roam = 0 and fit only α_dwell (one free parameter). This assumes roaming is the "null" state.
2. **Additional constraint**: Use the absolute Q_s values (not just ΔQ) to identify each α_s separately — requires fitting Q_roam and Q_dwell simultaneously.

Both strategies are documented. Strategy 2 is preferred as it uses more data.

### 3.4 Signed vs. unsigned α

The model J_eff(s) = J_base + α_s * P_sym is linear in α_s. The sign of α_s has physical meaning:

- **α_s > 0**: PDF signaling ADDS coupling in state s (strengthens effective connectivity along PDF edges)
- **α_s < 0**: PDF signaling SUPPRESSES coupling in state s (inhibitory modulation)

Given ΔQ = Q_roam - Q_dwell < 0 for top PDF pairs, and Q = -J_eff^{-1}:
- Q_dwell > Q_roam implies |J_eff(dwell)| < |J_eff(roam)| — paradoxically, dwelling coupling in precision space is larger when effective connectivity is smaller (due to matrix inversion)
- This non-intuitive sign reversal through matrix inversion is why the forward model is essential; naive reading of ΔQ sign does not directly give sign of Δα

The forward model (Form F) resolves this by computing Q from J_eff through the Lyapunov equation, making the sign correspondence explicit.

---

## 4. Anti-Circularity Plan

### 4.1 The circularity risk

The Phase 2B audit identified ADEL as the primary source neuron driving the Fisher K=20 enrichment. Four ADEL-centric pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, ADEL–URXL) are the "motivating observations" of Phase 3. Using these pairs directly in fitting would produce a circular evaluation: the model would be fitted to predict precisely the pairs used to motivate it.

### 4.2 Held-out set definition

The following pairs are **HELD OUT from all fitting** and reserved exclusively for evaluation:

**Held-out pairs (ADEL-centric)**:
1. ADEL–URYVR (rank 5, ΔQ = −0.122)
2. ADEL–URYDL (rank 9, ΔQ = −0.098)
3. ADEL–RMEL  (rank 10, ΔQ = −0.096)
4. ADEL–URXL  (rank 59, ΔQ = −0.045)

These 4 pairs constitute the primary held-out evaluation set. Additional ADEL-centric pairs (ADEL–OLQVR, rank 121) may optionally be added.

**Rationale**: ADEL was identified as the primary driver of the PDF signal in Phase 2B. All pairs where ADEL is the source neuron are held out. This creates a leave-source-out cross-validation: the model is fitted without any knowledge of ADEL's state-dependent coupling and then evaluated on ADEL predictions.

### 4.3 Training data

**For fitting (α_roam, α_dwell)**, the following data may be used:

1. **All non-ADEL PDF Class 4 pairs**: the 57 Bentley PDF Class 4 pairs where neither neuron is ADEL. These provide the PDF signal for fitting.

2. **Non-PDF Class 4 pairs**: all 1260 (= 1321 − 61) Class 4 pairs without PDF annotation. These provide the "background" ΔQ distribution against which PDF effects are estimated. They enter the fitting through a global objective function (see Section 5).

3. **The ΔQ matrices themselves** (from Phase 2 Stage 2): DQ_cepnem.npy, DQ_gcamp.npy. These are pre-computed and read-only; no re-estimation.

**Not allowed in fitting**:
- Any ADEL-centric pair ΔQ value
- Any knowledge of which specific pairs drove the Phase 2B enrichment signal
- The Phase 2B report conclusions (used only for design motivation, not as fitting targets)

### 4.4 Cross-validation option

As an alternative to the leave-source-out strategy, k-fold cross-validation on PDF pairs is possible:

- 5-fold CV over the 61 PDF Class 4 pairs
- Each fold: train α on 4/5 of PDF pairs, evaluate on held-out 1/5
- Report mean and variance of evaluation metric across folds

This provides a less biased estimate of model generalization across all 61 PDF pairs. The leave-ADEL-out strategy is preferred for interpretability.

### 4.5 The global-objective anti-circularity check

If a global objective is used (e.g., rank correlation on ALL Class 4 pairs), the held-out ADEL pairs do NOT enter the objective. The model is fitted to maximize correlation on 1317 pairs (= 1321 − 4 held-out), then evaluated on the 4.

Critically: the held-out evaluation metric is computed **after** fitting is complete, from the held-out pairs only. The evaluation result cannot feed back into the fitting.

---

## 5. Candidate Fitting Objectives

### 5.1 Objective A: Rank correlation on ΔQ (training pairs)

```
L_A(α_r, α_d) = Spearman(|ΔQ_model(i,j)|, |ΔQ_obs(i,j)|)
                over all training Class 4 pairs (i,j)
```

**Pros**: Direct match to the Phase 2 enrichment test (which uses ranks). Non-parametric; robust to outliers and heavy-tailed ΔQ distributions. Interpretable (same metric as AUROC).

**Cons**: Discontinuous gradient — not differentiable; requires derivative-free optimization. Maximizing correlation does not guarantee good absolute-scale predictions.

### 5.2 Objective B: Fréchet loss on precision matrices

```
L_B(α_r, α_d) = ||Q_roam^{model} - Q_roam^{obs}||_F²
              + ||Q_dwell^{model} - Q_dwell^{obs}||_F²
```

**Pros**: Uses full precision matrix structure (not just ranks). Differentiable; amenable to gradient-based optimization.

**Cons**: Penalizes absolute scale mismatches which may be dominated by on-connectome entries (Class 1/2); requires accurate Q_model absolute scale (sensitive to noise covariance D choice). The graphical lasso regularization in Q_obs introduces systematic sparsity that Q_model (from Lyapunov) does not replicate.

**Modification (off-connectome restricted)**:
```
L_B'(α_r, α_d) = ||ΔQ_model[C4] - ΔQ_obs[C4]||_F²
```
restricted to Class 4 pairs only. Removes on-connectome confounding.

### 5.3 Objective C: Log-likelihood (Gaussian graphical model)

If the covariance Σ_s^{model} = J_eff(s)^{-1} D is the true model:
```
L_C(α_r, α_d) = Σ_s [ N_s/2 * log det(Q_s^{model}) 
                       - N_s/2 * tr(Q_s^{model} S_s^{obs}) ]
```
where N_s = total frames in state s, S_s^{obs} = observed sample covariance.

**Pros**: Principled statistical objective; maximum likelihood under the linear Gaussian model. Incorporates sample size weighting (N_roam vs N_dwell are very different: 5587 vs 30583 frames).

**Cons**: Requires specified noise covariance D; highly sensitive to model misspecification; non-sparse Q_model may poorly fit sparse Q_obs. Dwells have ~5× more frames, dominating the objective.

### 5.4 Objective D: PDF-specific held-out prediction

```
L_D(α_r, α_d) = correlation(ΔQ_model[PDF_train], ΔQ_obs[PDF_train])
```
evaluated exclusively on PDF training pairs. This directly targets the PDF prediction task.

**Pros**: Maximally targeted; avoids contamination from non-PDF signal in the objective.

**Cons**: With only 57 non-ADEL PDF training pairs, overfitting risk is high for a two-parameter model (α_r, α_d). The objective may be noisy.

### 5.5 Recommended primary objective

**Recommendation: Objective A (Spearman rank correlation on ΔQ over all training Class 4 pairs), restricted to non-ADEL pairs.**

Rationale:
1. The enrichment test in Phase 2 was rank-based (AUROC = Mann-Whitney U statistic). Using rank correlation as the fitting objective ensures the fitting target matches the evaluation metric.
2. The heavy sparsity of ΔQ_obs (1078/1321 pairs with ΔQ = 0) makes absolute-scale objectives (B, C) poorly conditioned — zero entries are numerically trivial but constitute the majority.
3. Two free parameters (α_r, α_d) with ~1317 training pairs: rank correlation is sufficiently stable.
4. Derivative-free optimization (Nelder-Mead, or grid search over α ∈ [α_min, α_max]² is practical for two parameters.

Objective C (log-likelihood) is recommended as a secondary robustness check to assess whether α estimates are consistent under a fully parametric objective.

---

## 6. Model-Comparison Framework

### 6.1 Models

| ID | Model | Description |
|---|---|---|
| M0 | J_eff(s) = J_base (no PDF) | Anatomy-only baseline. ΔQ_model comes entirely from state-dependent J differences. Since J_base is state-independent, ΔQ_M0 ≡ 0. |
| M0+ | J_eff(s) = J_base + α * I | Scalar global gain; no structure. Tests whether a state-dependent scalar offset fits the data. |
| M1 | J_eff(s) = J_base + α_s * P_sym | Anatomy + PDF; primary model. |
| M2 | J_eff(s) = J_base + α_s * P_rand | Randomized PDF (degree-preserving permutation of P). Tests whether any off-connectome structure fits, not specifically PDF. |
| M3 | J_eff(s) = J_base + α_s * P_CeNGEN | CeNGEN expression-based PDF (broader, exploratory). |
| M1_directed | J_eff(s) = J_base + α_s * P_directed | Directed (asymmetric) P; robustness check for symmetrization choice. |

**M0 is the critical null model**. Since J_base is state-independent, M0 predicts ΔQ = 0 for all pairs. Any nonzero ΔQ_model requires either PDF (M1) or some other off-connectome term.

### 6.2 Evaluation metrics (computed on held-out ADEL pairs)

1. **Rank correlation**: Spearman(|ΔQ_model[ADEL]|, |ΔQ_obs[ADEL]|) across 4 held-out pairs. Range: [−1, 1]; higher is better.

2. **Sign accuracy**: Fraction of held-out pairs where sign(ΔQ_model) = sign(ΔQ_obs). For 4 pairs: 0/4, 1/4, 2/4, 3/4, 4/4.

3. **Relative enrichment**: Rank of each ADEL held-out pair in the model's |ΔQ_model| distribution over all 1321 Class 4 pairs. Expected under M1 success: rank < 50 (top 4%).

4. **PDF-class AUROC**: AUROC of model |ΔQ_model| for distinguishing PDF Class 4 pairs (57 training + 4 held-out) from non-PDF Class 4 pairs. Computed AFTER fitting.

5. **Stability margin**: distance_to_instability(α_fitted) — ensures fitted model is not at the boundary of instability.

### 6.3 Success criteria — defined before any fitting

The following criteria are pre-specified. They must be evaluated in order without modification after fitting begins.

**Primary success criterion (M1 vs M0)**:
```
AUROC(|ΔQ_M1[PDF_C4]|, |ΔQ_obs[PDF_C4]|) 
> AUROC(|ΔQ_M0|, |ΔQ_obs[PDF_C4]|) + 0.05
```
That is: M1 achieves at least 5 AUROC points above the anatomy-only baseline on the PDF Class 4 pairs.

**Secondary criterion (M1 vs M2 — structure vs. noise)**:
```
AUROC(M1 on PDF pairs) > AUROC(M2 on PDF pairs) + 0.03
```
M1 must outperform randomized PDF by at least 3 AUROC points.

**Tertiary criterion (ADEL held-out)**:
All 4 ADEL held-out pairs rank in the top 15% (≤198 of 1321) of |ΔQ_model| — that is, the model assigns above-average ΔQ to the held-out pairs.

**Stability criterion**: distance_to_instability(α_dwell) > 0.1 (not within 10% of instability boundary).

**Failure conditions** (triggers redesign before proceeding to Phase 3C):
- M1 AUROC < M0 AUROC on PDF pairs (model adds noise not signal)
- Fitted |α_dwell| or |α_roam| > α_max * 0.9 (fitting pushes to instability boundary)
- M1 performance is not distinguishable from M2 (PDF structure is not the relevant signal)

---

## 7. Phase 3 Roadmap

### Phase 3A: Model specification and data preparation

**Objective**: Implement the forward model, verify stability machinery, prepare train/held-out splits, run identifiability analysis.

**Inputs**:
- DQ_cepnem.npy, DQ_gcamp.npy (Phase 2 Stage 2)
- copresence_actual.json (Phase 2D Task A)
- A_raw_61 (reconstructed from Phase 2 analysis)
- Bentley PDF annotation (from Stage 4A)
- Creamer A_C matrix (optional; requires extraction from Creamer 154-neuron model)
- CePNEM residuals (Phase 1; for per-neuron noise variance estimation)

**Outputs**:
- `results/phase3/3A/forward_model.py` — implements J_eff(α), Lyapunov solver, Q_model(α)
- `results/phase3/3A/stability_analysis.json` — α_min, α_max, γ for each J candidate
- `results/phase3/3A/train_held_out_splits.json` — explicit lists of training/held-out pairs
- `results/phase3/3A/identifiability_analysis.md` — Form E analysis; documents whether α_r and α_d are jointly identifiable
- `results/phase3/3A/design_verification_report.md` — confirms all anti-circularity constraints are satisfied

**Stop condition**: Human review of design_verification_report.md before Phase 3B begins.

**Critical checks before proceeding**:
- Forward model produces Q_M0 ≡ 0 (ΔQ under M0)
- α_max > 0 exists for all J candidates
- Held-out ADEL pairs not used in any objective construction
- Identifiability: if only Form E is identified, document which parameterization is used

---

### Phase 3B: Fitting and model comparison

**Objective**: Estimate (α_roam, α_dwell) for M1 and M2. Compute training-set evaluation metrics. Report α estimates and stability margins.

**Inputs**: All outputs from Phase 3A.

**Fitting procedure for M1**:
1. Grid search over (α_r, α_d) ∈ [α_min, α_max]² on a 50×50 grid (2500 evaluations)
2. Identify grid maximum; refine with Nelder-Mead local optimization from best grid point
3. Report fitted (α̂_r, α̂_d), objective value, stability margin
4. Bootstrap uncertainty: resample recording-level sufficient statistics (same N_BOOT=25 as Phase 2), refit on each bootstrap; report 95% CI for (α̂_r, α̂_d)

**Fitting procedure for M2 (null model)**:
1. Draw 1000 degree-preserving random permutations of P
2. For each permutation, fit optimal α and record AUROC
3. Report the 5th, 50th, 95th percentile of M2 AUROC distribution

**Outputs**:
- `results/phase3/3B/fitting_results.json` — α̂_r, α̂_d, CIs, stability margins, all models
- `results/phase3/3B/model_comparison_training.md` — training-set metrics for M0, M1, M2, M3
- `results/phase3/3B/objective_surface.npy` — (50×50) grid of objective values for M1 (diagnostic)
- `results/phase3/3B/bootstrap_alpha.npy` — bootstrap distribution of (α̂_r, α̂_d)

**Stop condition**: Human review of fitting_results.json and model_comparison_training.md.

**Pre-commitment**: The model comparison pre-success criteria from Section 6.3 are evaluated here on training data. If M1 fails the primary training criterion, redesign (Phase 3A revision) is triggered rather than proceeding to held-out evaluation.

---

### Phase 3C: Held-out evaluation and interpretation

**Objective**: Evaluate M1 predictions on held-out ADEL pairs. Apply interpretation. Generate quantitative predictions for follow-up experiments.

**Trigger**: Phase 3B must be complete and reviewed; held-out evaluation is one-shot and irreversible.

**Inputs**: Phase 3B outputs + held-out ADEL pairs ΔQ values.

**Evaluation**:
1. For M1 fitted α̂_r, α̂_d: compute |ΔQ_model(ADEL–URYVR)|, |ΔQ_model(ADEL–URYDL)|, |ΔQ_model(ADEL–RMEL)|, |ΔQ_model(ADEL–URXL)|
2. Compute rank of each held-out pair in full 1321-pair |ΔQ_model| distribution
3. Compute sign accuracy for 4 held-out pairs
4. Apply success criteria from Section 6.3 (one-shot)

**Outputs**:
- `results/phase3/3C/held_out_evaluation.json` — ranks, sign accuracy, AUROC for held-out pairs
- `results/phase3/3C/prediction_table.md` — for each held-out pair: predicted rank, observed rank, sign agreement
- `results/phase3/3C/phase3_interpretation.md` — final interpretation: does M1 succeed, fail, or partially succeed?
- `results/phase3/3C/experimental_predictions.md` — concrete, testable predictions for experimental follow-up

**Experimental predictions format**:
For each successfully predicted pair:
```
Pair: ADEL–URYVR
Model prediction: Q_dwell > Q_roam (coupling stronger during dwelling)
Predicted α_dwell: [value] (coupling strength in dwelling state)
Experimental test: State-conditioned optogenetic stimulation of ADEL; measure URYVR response during roaming vs. dwelling bouts
Expected result: ADEL stimulation produces larger URYVR response during dwelling than roaming
Confound control: unc-31 animals (eliminates DCV release, expected to abolish state-conditioned difference)
```

**Stop condition**: Unconditional. Phase 3C terminates after interpretation. No further computation is authorized within Phase 3.

---

## Appendix: Key Phase 2 Numbers for Phase 3 Reference

| Quantity | Value | Source |
|---|---|---|
| N_neurons | 61 | Phase 2 Stage 0 |
| N_class4_pairs | 1321 | Phase 2 Stage 2 |
| N_pdf_class4 | 61 | Phase 2 Stage 4A |
| N_pdf_nonzero_DQ | 17 of 61 | Phase 2 Stage 4A |
| PDF AUROC (CePNEM) | 0.556, p_deg=0.023 | Phase 2 Stage 4A |
| PDF Fisher OR | 5.456, p_deg=0.008 | Phase 2 Stage 4A |
| ΔQ sign (top PDF pairs) | ALL negative | Phase 2B audit |
| ADEL–URYVR ΔQ | −0.1222 | Phase 2 Stage 2 |
| ADEL–URYDL ΔQ | −0.0980 | Phase 2 Stage 2 |
| RMEL–URYDL ΔQ | −0.0754 | Phase 2 Stage 2 |
| RMER–URYVR ΔQ | 0.000 | Phase 2B audit |
| CePNEM median drift ratio | 0.000 | Phase 2D Task B |
| CePNEM p95 drift ratio | 4.905 | Phase 2D Task B |
| Roaming mean position | 0.234 | Phase 2D Task B |
| Dwelling mean position | 0.524 | Phase 2D Task B |
| LOO median retention (CePNEM) | 0.960 | Phase 2 Stage 3 |
| Creamer subspace overlap | 56/61 neurons | Phase 2D data check |

---

*Design package only. No model fitting. No simulation. No parameter estimation.*
*No ADEL–URY results used in any objective construction.*
