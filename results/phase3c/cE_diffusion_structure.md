# Phase 3C-E — Diffusion Structure Analysis
Date: 2026-06-03
Authorization: Phase 3C-E

---

## Purpose

Determine whether the empirical diffusion structure supports the Ω → Q reduction
used in the manuscript: Q = D^{-1}(Ω − A).

Specific manuscript claim under evaluation:

> "The diffusion structure is sufficiently close to isotropic that Ω and Q become
> numerically equivalent for this dataset."

All tasks use D_emp = Cov(Δx) estimated from pooled first-differences across all
40 recordings. Gap frames are excluded implicitly (NaN propagation).

---

## E1 — Empirical Diffusion Matrices

Computed D_emp = Cov(Δx_i, Δx_j) for all 61×61 neuron pairs using pairwise
complete-case estimation. All 1830 off-diagonal pairs have coverage across recordings.

| | CePNEM | GCaMP |
|---|---|---|
| Diagonal range | [0.316, 0.483] | [0.156, 0.323] |
| Zero-diagonal entries | 0 | 0 |
| Off-diagonal pairs covered | 1830/1830 | 1830/1830 |

Note: D_emp diagonal = D3 (first-difference variance) by construction. This is
a different quantity from D2 (total variance). The relevant D for the Q = D^{-1}(Ω − A)
identity under an OU-like process is the innovation covariance, here approximated
by Cov(Δx) ≈ D3 on the diagonal.

---

## E2 — Isotropy Metrics

### CePNEM D_emp

| Metric | Value |
|---|---|
| Diagonal mean | 0.4043 |
| Diagonal std | 0.0376 |
| **Diagonal CV** | **0.093** |
| Diagonal range | [0.316, 0.483] |
| Condition number κ | **2.50** |
| **Isotropy score** ||D−cI||/||D|| | **0.162** |
| Diagonal energy fraction ||diag(D)||²/||D||² | **0.982** |
| Eigenvalue range | [0.302, 0.755] |
| Negative eigenvalues | 0 |

### GCaMP D_emp

| Metric | Value |
|---|---|
| Diagonal mean | 0.2310 |
| Diagonal std | 0.0349 |
| **Diagonal CV** | **0.151** |
| Diagonal range | [0.156, 0.323] |
| Condition number κ | **2.94** |
| **Isotropy score** ||D−cI||/||D|| | **0.203** |
| Diagonal energy fraction ||diag(D)||²/||D||² | **0.981** |
| Eigenvalue range | [0.149, 0.438] |
| Negative eigenvalues | 0 |

### Interpretation

The two isotropy measures tell different stories:

**Diagonal CV (9–15%)**: Measures how uniform the per-neuron innovation variances
are. These are moderate — GCaMP is more anisotropic than CePNEM on this metric.
For a diagonal D approximation, this is the only relevant measure.

**Full isotropy score (16–20%)**: Measures ||D − cI||_F / ||D||_F including all
off-diagonal entries. The 16–20% deviation from scalar multiple of identity is non-
trivial but far from strongly anisotropic (a uniform matrix would score 1.0).

**Eigenvalue spectrum**: Condition numbers of 2.5–2.9 indicate moderate spread.
The eigenvalue ratio 2.5–2.9× is consistent with what would arise from a randomly
correlated multivariate system, not from a structured (low-rank) anisotropy.

Both matrices are **positive definite** (no negative eigenvalues), validating the
pairwise estimation procedure.

---

## E3 — Density Metrics

| Metric | CePNEM | GCaMP |
|---|---|---|
| Off-diagonal energy frac ||D−diag(D)||/||D|| | **0.133** | **0.139** |
| Median \|D_ij\| (off-diag) | 0.0055 | 0.0032 |
| Median D_ii (diagonal) | 0.404 | 0.229 |
| **Median \|off-diag\| / median D_ii** | **0.0135** | **0.0141** |

### Top-10 largest off-diagonal entries

#### CePNEM
| Pair | D_ij |
|---|---|
| AVAR–RMDVL | +0.0215 |
| IL1DR–OLQVL | +0.0203 |
| ASEL–OLQDL | +0.0201 |
| IL2VL–SMDVL | +0.0191 |
| AVJR–M3R | +0.0190 |
| M1–OLLL | +0.0190 |
| IL2VL–RMDDR | +0.0187 |
| OLQDL–OLQVL | +0.0185 |
| AVAR–URBL | +0.0176 |
| M3L–OLQVR | +0.0174 |

#### GCaMP
| Pair | D_ij |
|---|---|
| IL1DR–OLQVL | +0.0129 |
| AVAL–IL2VR | +0.0121 |
| ADEL–RICL | +0.0121 |
| M1–OLLL | +0.0120 |
| IL2VL–SMDVL | +0.0117 |
| AVAL–RMDDR | +0.0114 |
| AVAR–RMDVL | +0.0114 |
| AWAL–CEPDR | +0.0114 |
| AVJR–M3R | +0.0113 |
| ASEL–OLQDL | +0.0111 |

### Interpretation

**The diffusion matrix is diagonally dominant**. Off-diagonal entries contribute
13–14% of total Frobenius energy, but the median off-diagonal magnitude is only
1.35–1.41% of the median diagonal. Individual off-diagonal entries are at most
4–5% of a typical diagonal entry.

**Structurally, both D_emp matrices are well-approximated by their diagonals.**
The off-diagonal terms reflect weak shared noise (correlated measurement or biological
co-variation in fluctuations), not a dominant cross-neuron diffusion channel.

Several pairs appear in both CePNEM and GCaMP top-10 (AVAR–RMDVL, IL1DR–OLQVL,
ASEL–OLQDL, M1–OLLL, IL2VL–SMDVL, AVJR–M3R) — these are the most consistently
correlated fluctuation pairs across coordinates. None are PDF-annotated pairs.

---

## E4 — Principal Modes

| | CePNEM | GCaMP |
|---|---|---|
| Variance explained PC1 | 3.1% | 3.1% |
| Variance explained PC1+2 | 5.1% | 5.4% |
| Variance explained PC1–5 | 11.0% | 11.9% |

**PC1 loadings (top neurons):**
- CePNEM PC1: AWCL (−0.181), RID (−0.170), URBL (−0.170), OLQVL (−0.170), OLQVR (−0.169)
- GCaMP PC1: AWCL (−0.230), RID (−0.220), ADEL (−0.197), URXL (−0.190), SMDVL (−0.189)

### Interpretation

**No dominant latent diffusion mode exists.** PC1 explains only 3.1% of variance
in both coordinates. In a 61-dimensional space, a perfectly isotropic matrix would
have each PC explaining 1/61 ≈ 1.6% of variance. The empirical PC1 at 3.1% is
only 2× above the isotropic baseline — a very weak concentration.

The PC1–5 cumulative fraction (11.0–11.9%) compares to 8.2% for a perfectly
isotropic 61-dimensional matrix. The empirical structure is 1.4× above isotropic
in the top 5 components — again, weak.

Biological note: RID (PDF neuropeptide modulator) appears in the top-5 of PC1
for both coordinates, suggesting its innovation variance is slightly elevated
and correlated with a broad set of neurons. This is consistent with RID's
proposed role as a slow neuromodulatory source.

---

## E5 — ΔΩ_emp = D_emp @ ΔQ vs ΔQ

This task computes ΔΩ_emp[i,j] = Σ_k D_emp[i,k] × ΔQ[k,j], the full matrix
product (not elementwise scaling as in the diagonal case).

| Metric | CePNEM | GCaMP |
|---|---|---|
| Spearman ρ(|ΔΩ_emp|, |ΔQ|) | **0.566** | **0.798** |
| Top-20 overlap | 18/20 | 16/20 |
| Top-100 overlap | 93/100 | 87/100 |
| New pairs in top-200 ΔΩ_emp | 33 | 25 |
| PDF AUROC ΔΩ_emp | **0.664** | 0.488 |
| PDF AUROC ΔQ | 0.556 | 0.526 |

### Contrast with diagonal D results

| Model | CePNEM ρ | GCaMP ρ |
|---|---|---|
| D = I (diagonal, uniform) | 1.0000 | 1.0000 |
| D = D2 (diagonal, total var) | 0.9999 | 0.9999 |
| D = D3 (diagonal, innovation var) | 0.9999 | 0.9988 |
| **D = D_emp (full matrix)** | **0.566** | **0.798** |

The full empirical D_emp, when applied as a matrix multiplication, substantially
reorders pairs compared to ΔQ. This is the key finding of E5.

### Why ρ drops to 0.57 (CePNEM)

The full matrix product ΔΩ_emp = D_emp @ ΔQ effectively computes, for each row i:

    ΔΩ_emp[i, :] = Σ_k D_emp[i,k] × ΔQ[k, :]

The off-diagonal D_emp[i,k] (k ≠ i) cross-couples row i of ΔQ into row j.
Even though each D_emp[i,k] is small (median off-diagonal = 1.4% of diagonal),
the sum over 61 terms accumulates to a material perturbation: each row of ΔΩ_emp
receives contributions from ~60 other ΔQ rows. The total off-diagonal contribution
scales as ~60 × 1.4% ≈ 85% of the diagonal contribution.

This "dilution" effect means the full matrix product is a non-trivial mixing of
ΔQ rows, not a simple rescaling — explaining why ρ drops to 0.57.

### ADEL pairs under D_emp @ ΔQ (CePNEM)

| Pair | ΔQ rank | ΔΩ_emp rank | Δ |
|---|---|---|---|
| ADEL–URYVR | 5 | 5 | 0 |
| ADEL–URYDL | 9 | 7 | −2 |
| ADEL–RMEL | 10 | 8 | −2 |
| ADEL–I2L | 26 | 18 | −8 |
| ADEL–URXL | 59 | 59 | 0 |

The top ADEL predictions (ADEL→URYVR, ADEL→URYDL, ADEL→RMEL) are **preserved or
improved** under D_emp @ ΔQ. This is a positive robustness result: the strongest
signals survive the full-matrix mixing.

### PDF AUROC increase under D_emp (CePNEM only)

The PDF AUROC increases from 0.556 (ΔQ) to 0.664 (ΔΩ_emp) for CePNEM. This is
a notably large increase. The interpretation is that cross-neuron diffusion coupling
in CePNEM residuals amplifies the PDF network signal when applied as a matrix
multiplier to ΔQ. However, this observation is **not pursued further** per Phase 3C-E
scope (no new hypotheses, no new fitting). It is recorded here as an observation
for potential future investigation.

For GCaMP, PDF AUROC decreases (0.526 → 0.488), consistent with the GCaMP coordinate
being noisier and the off-diagonal diffusion coupling introducing dilution rather than amplification.

---

## Final Question: Manuscript Claim Evaluation

**Claim**: "The diffusion structure is sufficiently close to isotropic that Ω and Q
become numerically equivalent for this dataset."

### Answer: PARTIALLY

**YES, under the diagonal noise model appropriate for CePNEM:**

The CePNEM estimator assumes diagonal noise covariance by construction (per-neuron
independent residuals). Under this model assumption:

- D is diagonal, and D2 (total variance) has CV = 3.1%, making D ≈ 1.025 × I
- ΔΩ = D · ΔQ (elementwise row-scaling) → ρ(ΔΩ, ΔQ) = 0.9999
- Top-20 overlap = 19/20; top-100 overlap = 100/100
- The diagonal energy fraction of D_emp = 98.2%, supporting the diagonal approximation

Within the CePNEM modeling framework, the manuscript claim is quantitatively supported.
The diagonal D is not just an approximation — it is the model-appropriate choice.

**NO, under the full empirical diffusion model:**

If D is estimated as the full Cov(Δx) matrix:

- Isotropy score = 16–20% (non-negligible deviation from scalar multiple of identity)
- ΔΩ_emp = D_emp @ ΔQ gives ρ = 0.57 (CePNEM), 0.80 (GCaMP) — substantial reordering
- 33 new pairs enter the top-200 ΔΩ_emp for CePNEM (not in top-200 ΔQ)

Under a full diffusion model, Ω and Q are not numerically equivalent. However, this
model is not the one used in the manuscript — CePNEM does not assume full diffusion
covariance.

### Recommended manuscript language

The Phase 3C finding supports the following statement:

> "Under the per-neuron diagonal noise model assumed by the CePNEM estimator,
> the empirical innovation variances are near-uniform (CV ≈ 9%), making the
> current organization Ω a near-constant rescaling of the precision matrix Q.
> The state-difference ΔΩ = D·ΔQ is functionally equivalent to ΔQ for ranking
> off-connectome pairs (Spearman ρ > 0.9999, top-20 overlap 19/20), supporting
> the use of ΔQ as the primary summary statistic."

The stronger claim that D is "isotropic" should not be made without the qualifier
"under the diagonal model." The full empirical diffusion matrix has measurable
off-diagonal structure (13% off-diagonal energy, condition number 2.5) that
distinguishes Ω from Q under a full diffusion model. This structure does not
invalidate the Phase 2 results, but it means Ω and Q are not equivalent in all
senses of the word.

---

## Summary Table

| Metric | CePNEM D_emp | GCaMP D_emp | Assessment |
|---|---|---|---|
| Diagonal CV | 9.3% | 15.1% | Near-isotropic diagonal |
| Isotropy score | 0.162 | 0.203 | Moderately anisotropic (full) |
| Off-diagonal energy | 13.3% | 13.9% | Diagonally dominant |
| Median off/diag ratio | 1.4% | 1.4% | Off-diagonal individually small |
| Condition number | 2.50 | 2.94 | Moderate spread |
| PC1 variance explained | 3.1% | 3.1% | No dominant mode |
| ρ(ΔΩ_diag, ΔQ) | 0.9999 | 0.9988 | Diagonal: equivalent |
| ρ(ΔΩ_emp, ΔQ) | 0.566 | 0.798 | Full matrix: not equivalent |
| ADEL top-3 preserved | YES (ranks 5,7,8) | — | Core signal robust |

**Conclusion**: The diffusion structure is diagonally dominant (98% diagonal energy)
and lacks dominant off-diagonal modes (PC1 = 3%), supporting the diagonal D
approximation. Under this approximation, Ω and Q are numerically equivalent
(ρ > 0.9999). Under the full empirical diffusion model, they are not equivalent,
but the full model is not the appropriate choice for CePNEM-based analysis.

---

## Output Files

| File | Description |
|---|---|
| D_emp_cepnem.npy | (61×61) CePNEM empirical diffusion matrix |
| D_emp_gcamp.npy | (61×61) GCaMP empirical diffusion matrix |
| diffusion_metrics.json | All E1–E5 metrics (structured) |
| diffusion_matrices.json | Per-neuron diagonal values |
| cE_diffusion_structure.md | This report |

---

*Phase 3C-E: STOP. Awaiting human review.*
*DO NOT: start new model families, evaluate held-out pairs, generate predictions.*
