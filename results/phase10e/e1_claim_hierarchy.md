# Phase 10E.1 — Final Claim Hierarchy
Date: 2026-06-15

---

## Classification System

- **A. Primary main-text claim**: Strong evidence; suitable as a central finding
- **B. Secondary main-text claim**: Present with explicit qualification
- **C. Supplementary / caveated claim**: Valid finding; requires dedicated caveat
- **D. Do not use as claim**: Insufficient robustness or misleading framing

---

## 1. ADEL–URYVR Dwelling-Dominant Current Organization

**Classification: A — Primary main-text claim**

**Evidence supporting it:**
- |ΔΩ_ss| rank 2 (CePNEM+GL); |ΔQ| rank 5; GCaMP+GL rank 28 (top 2%)
- |ΔΩ^B| rank 2 — unchanged after coupling correction (Phase 10A)
- Co-observation null: 99.9th percentile, p=0.001 (Phase 10B)
- D=I (ΔQ alone) rank 5 — present without diffusion weighting (Phase 10C)
- Hub-matched null: 99.8th percentile, p=0.0017 (Phase 10C)
- Row/col permuted diffusion null: p=0.018 (top-2 in only 1.8% of permutations)
- ADEL-URYVR is PDF-annotated (Bentley ESconnectome, pdf-1→pdfr-1)
- Top-5 at ALL five diffusion timescales τ=1–20 (Phase 10C C5)
- Sign (dwelling-dominant) stable at ALL timescales τ=1–20
- Off-reference under ALL 10 tested connectome definitions (Phase 10D)

**Caveats:**
- Extreme rank (2) requires CePNEM residualization + anatomy-guided GL
- Under CePNEM+Ridge: rank 165 (top 13%)
- Under GCaMP+GL: rank 28 (top 2%); signal direction preserved
- No funatlas experimental data (0 observations) — untested novel prediction
- ΔD sign (not ΔΩ sign) is unstable across timescales

**Recommended manuscript location:**
Results section, primary finding paragraph. ADEL–URYVR should lead the experimental prediction.

**Exact wording constraints:**
- MUST state the rank depends on CePNEM+anatomy-guided-GL
- MUST report GCaMP+GL rank 28 as robustness check
- MUST report co-observation null p=0.001 as primary specificity evidence
- MUST NOT claim ADEL-URYVR is "funatlas-confirmed" — it is a novel prediction
- MAY describe as "the highest-ranked novel PDF-associated prediction"

---

## 2. ADEL–URYDL Dwelling-Dominant Current Organization

**Classification: A — Primary main-text claim (slightly more qualified than ADEL-URYVR)**

**Evidence supporting it:**
- |ΔΩ_ss| rank 6 (CePNEM+GL); |ΔQ| rank 9; GCaMP+GL rank 39 (top 3%)
- |ΔΩ^B| rank 3 — PROMOTED after coupling correction (Phase 10A)
- Co-observation null: 99.5th percentile, p=0.005 (Phase 10B)
- D=I (ΔQ alone) rank 9 — present without diffusion weighting (Phase 10C)
- Hub-matched null: 99.6th percentile, p=0.0043 (Phase 10C)
- PDF-annotated (Bentley ESconnectome, pdf-1→pdfr-1)
- Off-reference under ALL 10 tested connectome definitions (Phase 10D)

**Caveats:**
- Rank degrades to 220 at τ=20 frames (5 seconds) — timescale-sensitive (Phase 10C C5)
- Under CePNEM+Ridge: rank 293 (top 22%)
- No funatlas experimental data — novel prediction
- GCaMP+GL rank 39 (top 3%); notably weaker than ADEL-URYVR (rank 28)
- More sensitive than ADEL-URYVR in LOAO analysis (worst case rank 1261 under ridge)

**Recommended manuscript location:**
Results section, co-reported with ADEL-URYVR. Should be distinguished as "slightly more qualified" with explicit timescale sensitivity note.

**Exact wording constraints:**
- MUST state the rank is stable for τ≤10 frames but degrades at τ=20
- MUST report co-observation null p=0.005
- SHOULD note it is promoted (rank 6→3) after coupling correction, supporting signal authenticity
- MUST NOT equate its robustness to ADEL-URYVR without acknowledging timescale sensitivity

---

## 3. ADEL–RMEL Dwelling-Dominant Current Organization

**Classification: B — Secondary main-text claim**

**Evidence supporting it:**
- |ΔΩ_ss| rank 4; |ΔQ| rank 10; CePNEM+Ridge rank 1 (most robust under ridge)
- Bootstrap (ridge): top-20 in 76% of replicates, median rank 6 (Phase 10B)
- LOAO (ridge): always rank 1–2 (Phase 10B)
- Co-observation null: p=0.002 (Phase 10B)
- Off-reference under all 10 connectome definitions (Phase 10D)

**Caveats:**
- CONFOUNDED WITH ΔB: ADEL-RMEL has ΔB rank 1 (largest coupling state change among key pairs)
  Under ΔΩ^B, rank changes 4→18 (demoted but remains top-20) (Phase 10A)
- GCaMP+GL rank 31 (weaker than ADEL-URYVR/URYDL signal direction)
- Timescale: stable τ≤10, degrades to rank 70 at τ=20 (Phase 10C C5)
- ADEL-RMEL is NOT PDF-annotated — it is the third ADEL pair but no pdfr-1 on RMEL

**Recommended manuscript location:**
Results section, as "third ranked ADEL-centered pair" with qualification that ADEL-RMEL
may partly reflect state-specific coupling change (ΔB rank 1). Can be grouped with ADEL-URYVR/URYDL for the module claim.

**Exact wording constraints:**
- MUST disclose ΔB rank 1 confound
- MUST NOT present ADEL-RMEL as equivalent in robustness to ADEL-URYVR/URYDL
- MAY note its remarkable bootstrap robustness under ridge (top-20 in 76%)
- SHOULD note it is part of the DA_mech↔URY_URX module

---

## 4. RMEL–URYDL Dwelling-Dominant Current Organization

**Classification: C — Supplementary / caveated claim**

**Evidence supporting it:**
- |ΔΩ_ss| rank 23; |ΔQ| rank 16
- Co-observation null: p=0.018 (Phase 10B)
- Sign stable across all timescales

**Caveats:**
- Under ΔΩ^B: rank 168 (Phase 10A) — sensitive to coupling correction
- Enters top-K only at K≥25 (not in top-20)
- Off-reference status borderline: ON-reference under Creamer chem thr=1 (1 directed synapse RMEL→URYDL)
- Not PDF-annotated

**Recommended manuscript location:**
Supplementary table only. Should not appear in main-text claims. May appear in module discussion as part of RME↔URY cross-block structure.

---

## 5. RMEL–RMER Dwelling-Dominant Current Organization

**Classification: C — Supplementary / caveated claim (for the MODEL RANKING)**
**For the FUNATLAS CONFIRMATION: Special status (see below)**

**Evidence supporting it (model ranking):**
- |ΔΩ_ss| rank 38 (top 3%); |ΔQ| rank 32
- Sign stable across all timescales
- PDF-annotated (RMEL→RMER, pdf-1→pdfr-1)

**Evidence supporting it (funatlas confirmation — from Phase 5A):**
- wt q = 0.0002 (22 observations): RMEL optogenetic stimulation drives RMER response
- unc-31 mutant: q = 0.119 (not significant) — DCV-dependent
- Three-way convergence: observational + optogenetic + genetic

**Caveats:**
- Under ΔΩ^B: rank 371 — NOT ROBUST to coupling correction (Phase 10A)
- Under GCaMP+GL: rank 709 (Phase 10B)
- Bootstrap (ridge): top-20 in only 2% of replicates (Phase 10B)
- Co-obs null: p=0.026 (weakest among key pairs) (Phase 10B)
- Phase 10C: C — Weak (24% diffusion-driven; degrades at τ≥5)
- Small unc-31 sample (n=5 observations)

**Recommended manuscript location:**
The funatlas confirmation should appear in Results as a "biologically confirmed case" providing existence proof that the framework's off-reference predictions can correspond to real functional interactions — explicitly decoupled from its model ranking. The ranking caveat (rank 38→371 under coupling correction) must appear in Methods or Supplement.

**Exact wording constraints:**
- MUST NOT use RMEL-RMER ranking as validation of the ΔΩ_ss scoring system
- MAY use RMEL-RMER funatlas confirmation as "proof of concept" for the framework
- MUST disclose that RMEL-RMER ranking is sensitive to fixed-coupling assumption
- MUST NOT describe "three-way convergence" as proving the ranking — only proving the interaction

---

## 6. DA_mech ↔ URY_URX Module

**Classification: A — Primary main-text claim**

**Evidence supporting it:**
- Rank 1 by mean |ΔΩ_ss| cross-block coupling (Phase 3D/10C)
- Rank 1 under ALL 5 diffusion specifications (D=I through state-specific full) (Phase 10C C1)
- Rank 1 in GCaMP+GL (Phase 10B)
- Strengthened under coupling correction: rank 2→1 under ΔΩ^B (Phase 10A)
- Bootstrap (ridge): rank 1 in 75–99% of permutations (Phase 10C C2)
- Bootstrap (animal): median rank 6 (Phase 10B B2, conservative)
- Sign stable: all cross-block pairs dwelling-dominant

**Caveats:**
- DA_mech = {ADEL, CEPDL, CEPDR, CEPVL}; URY_URX = {URYVR, URYDL, URYVL, URXL}
- Module claim is aggregate; individual pairs within have varying robustness
- Module definition is pre-specified (not chosen to maximize rank)

**Recommended manuscript location:**
Results section, co-reported with primary pair claims. Frame as the dominant structural feature across methods.

---

## 7. PDF Top-K Enrichment

**Classification: A — Primary main-text claim (enrichment at K=20, pre-specified)**

**Evidence supporting it:**
- K=20 (locked): 4/20 top pairs PDF-annotated; OR=5.2, Fisher p=0.011, degree-perm p=0.008
- K-sweep (K=5–100): enriched at ALL K values, monotonically present
- BH-significant within 70-test sweep at K=30, 40, 50
- At K=5: 2/5 PDF (expected 0.23); at K=10: 3/10 (expected 0.46)
- Serotonin: 0 in top-K at ALL K values — clean negative control

**Caveats:**
- K=20 primary test: nominal p; BH-significance emerges at K=30–50
- Global PDF AUROC: 0.533, p=0.196 (NOT globally significant under |ΔΩ_ss|)
- PDF AUROC is significant under |ΔQ| (p=0.023) — disclose which scoring object
- "PDF enrichment" should always be specified as "top-K Fisher enrichment" not "global AUROC"

**Recommended manuscript location:**
Results section, as primary quantification of the annotation enrichment. Report Fisher OR and degree-permutation p as pre-specified primary statistics.

---

## 8. Serotonin Negative Control

**Classification: A — Should be explicitly stated as negative control**

**Evidence:**
- 0 serotonin pairs in top-K at ALL K values (K=5 through K=100)
- Serotonin AUROC ≈ 0.495 (chance)
- Sharp contrast to PDF enrichment

**Recommended manuscript location:**
One sentence in Results: "By contrast, serotonin-annotated pairs were not enriched in the top-K at any tested threshold (0 in top-100; AUROC ≈ 0.5)."

---

## 9. Funatlas RMEL–RMER Support

**Classification: C — Supplementary (for ranking validation); A — Primary (for framework validation)**

See claim 5 above. Distinguish two uses:
- As "proof of concept" that framework identifies real interactions: A (main text)
- As "ranking validation" of ΔΩ_ss: C (cannot claim; ranking fragile)

---

## 10. Current-Over-Precision Statement

**Classification: B — Secondary claim with nuance**

The statement that ΔΩ_ss (probability current) is preferable to ΔQ (precision difference):

**Evidence:**
- ADEL-PDF pairs are promoted under ΔΩ_ss (ranks 5,9,10 → 2,6,4)
- ΔΩ_ss sign is more timescale-stable than ΔD sign
- Phase 5B verdict: "B — Current refines the story"
- Theoretical preference: ΔΩ_ss is the actual probability flux (D_sQ_s includes D weighting)

**Caveats:**
- Global PDF AUROC SIGNIFICANCE LOST under ΔΩ_ss vs ΔQ
- Top-20 count preserved (4/20 both), AUROC global diluted
- Low global correlation: ρ(|ΔΩ_ss|, |ΔQ|) = 0.331
- The statement "current is empirically superior" cannot be sustained globally

**Recommended manuscript location:**
Methods subsection: frame as theoretical choice (probability flux), note that it promotes key pairs and sign is stable but global enrichment AUROC weakens.

**Exact wording constraints:**
- MUST NOT claim current "outperforms" ΔQ in global enrichment
- MAY state that ΔΩ_ss provides a more stable descriptor for key ADEL-PDF pairs
- MUST disclose AUROC significance loss
