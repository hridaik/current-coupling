# Phase 10E.6 — What Not to Claim
Date: 2026-06-15

---

## Claims That Must NOT Be Made

The following list identifies statements that would be incorrect, misleading,
or unsupported given the Phase 10A–10D robustness program. Each entry includes
the reason it should be avoided and what to say instead.

---

### 1. "Current uniquely discovers ADEL/PDF"

**Why NOT to claim**: The PDF top-20 enrichment is 4/20 under both |ΔΩ_ss| AND |ΔQ|
(Phase 5B). The global PDF AUROC under |ΔΩ_ss| is NOT significant (p=0.196), while
under |ΔQ| it IS significant (p=0.023). Other baselines (|ΔΣ|, |ΔCorr|) also show
6/20 PDF in top-20. The current formulation does not uniquely discover the PDF signal.

**What to say instead**: "The state-specific probability current ΔΩ_ss promotes the
primary ADEL-PDF predictions from ranks 5/9 (under ΔQ alone) to ranks 2/6, refining
but not uniquely enabling the PDF discovery."

---

### 2. "Current empirically outperforms all simpler baselines in worm"

**Why NOT to claim**: Phase 10A shows |ΔΣ| and |ΔCorr| achieve 6/20 PDF pairs (more
than ΔΩ_ss's 4/20 and ΔQ's 4/20). The global ranking correlation between |ΔΩ_ss|
and |ΔQ| is only ρ = 0.331. Global AUROC significance is lost under ΔΩ_ss.
The specific top-pair promotions are advantageous, but overall empirical superiority
cannot be claimed.

**What to say instead**: "Among the tested scoring objects, ΔΩ_ss most strongly
promotes ADEL–URYVR and ADEL–URYDL within the top-5. Global enrichment metrics
(AUROC) do not consistently favor one formulation."

---

### 3. "RMEL–RMER is a robust current-ranking validation"

**Why NOT to claim**: RMEL-RMER drops from rank 38 to rank 371 under coupling
correction (ΔΩ^B). Its rank is 709 in GCaMP+GL. Its bootstrap rank is unstable.
Its model ranking is sensitive to the fixed-coupling assumption. Using RMEL-RMER
to "validate" that high ΔΩ_ss ranks correspond to real interactions conflates the
funatlas confirmation (independent experimental data) with the model ranking (fragile).

**What to say instead**: "RMEL–RMER provides independent evidence that the framework
identifies genuine off-connectome neuropeptide interactions. Its funatlas confirmation
is based on optogenetic perturbation data, not on its model rank, and is independent
of the fixed-coupling assumption. The pair's model ranking is presented in Supplementary
Table X as a caveated secondary finding."

---

### 4. "ADEL–URY is robust across all residualization pipelines"

**Why NOT to claim**: The extreme rank (2/6) depends on both CePNEM and anatomy-guided
GL. Under ridge precision: ranks 165/293. The signal is present in GCaMP+GL (ranks
28/39) but not at top-5. "Robust" without qualification is too strong.

**What to say instead**: "The signal direction (dwelling-dominant elevation) is
preserved across residualization choices. The extreme top-2/6 ranking is specific
to the primary CePNEM+anatomy-guided-GL pipeline."

---

### 5. "PDF enrichment is globally significant across all tests"

**Why NOT to claim**: The global PDF AUROC under |ΔΩ_ss| is NOT significant (p=0.196).
The K=20 Fisher test is a nominal p (primary, single pre-specified test) but does not
pass BH correction when compared to the 70-test sweep. BH-significance emerges at
K=30–50 in the sweep.

**What to say instead**: "PDF annotation is significantly enriched at the pre-specified
K=20 threshold (Fisher p=0.011, degree-permutation p=0.008) and passes BH correction
in the sensitivity sweep at K=30, 40, and 50. The global AUROC enrichment test is
not significant under ΔΩ_ss (p=0.196)."

---

### 6. "All top current pairs are off-connectome under every reference"

**Why NOT to claim**: RMEL-URYDL has 1 directed chemical synapse in the Creamer
connectome and is ON-reference under Creamer chemical thr=1 (the closest approximation
to the primary A_raw). It is also ON-reference under Creamer LDS effective coupling.

**What to say instead**: "All primary PDF-pair predictions (ADEL–URYVR, ADEL–URYDL,
ADEL–RMEL) are off-reference under all 10 tested connectome definitions. RMEL–URYDL
is borderline: it has one directed Creamer chemical synapse (RMEL→URYDL) and would
be on-reference under Creamer chemical thr=1."

---

### 7. "Diffusion is irrelevant to the ADEL/PDF signal"

**Why NOT to claim**: The full state-specific D promotes ADEL-URYVR from rank 5 (D=I)
to rank 2. The row/column permuted diffusion null gives p=0.018, showing the specific
D-Q identity alignment is data-specific and contributes meaningfully. Claiming diffusion
is "irrelevant" contradicts these results.

**What to say instead**: "The signal is present without diffusion weighting (rank 5
under identity diffusion), but the specific empirical D-Q alignment incrementally
promotes ADEL-URYVR to rank 2 (p=0.018 in permuted-D null). Dense diffusion does not
CREATE the signal but does REFINE it."

---

### 8. "The information-limiting framework explains the PDF pattern"

**Why NOT to claim**: Phase 4B found NO support for information-limiting structure.
PDF pairs show LOWER alignment (AUROC=0.426) than expected by chance (p=0.978 for
enrichment). ADEL–URYVR has scalar alignment = −0.015 (anti-aligned). The phrase
"information-limiting correlations" is directly contradicted by Phase 4B results.

**What to say instead**: Do not use "information-limiting" framing for this dataset.
The ADEL-URYVR/URYDL connection is not between neurons with aligned behavioral encoding.

---

### 9. "ADEL–URYVR and ADEL–URYDL are funatlas-confirmed"

**Why NOT to claim**: Both pairs have ZERO funatlas observations (Phase 5A table).
They are novel predictions that have not been tested by optogenetic perturbation.

**What to say instead**: "ADEL–URYVR and ADEL–URYDL are novel experimental predictions
that have not been evaluated in the Randi et al. perturbation atlas."

---

### 10. "CePNEM+GL is the universally superior estimator"

**Why NOT to claim**: GCaMP+GL (same estimator, raw calcium) gives weaker results
(ranks 28/39 vs 2/6). The anatomy-guided GL is the theoretically motivated choice for
off-connectome pair discrimination, but it depends on the accuracy of the connectome
reference. If the reference is wrong, the λ_off penalty may be misapplied.

**What to say instead**: "The anatomy-guided GL estimator encodes prior sparsity for
off-connectome pairs (λ_off = 10×λ_on), which is scientifically motivated and pre-specified.
Results are reported under both CePNEM+GL and GCaMP+GL to allow readers to assess
the contribution of each component."

---

### 11. "The decomposition shows X% of the signal comes from diffusion"

**Why NOT to claim**: Phase 10C explicitly showed that the diffusion/precision decomposition
is NOT UNIQUE. The fraction attributed to diffusion vs precision varies by up to 25 pp
between the two valid decompositions. Only sign consistency and dominance direction
(precision-dominant) are robustly interpretable.

**What to say instead**: "Both valid state-conditioned decompositions show the precision
term (D_s @ ΔQ) accounts for 76–114% of the total ΔΩ_ss value for key pairs, indicating
precision-dominant structure. The exact fraction is not unique and should not be
over-interpreted."
