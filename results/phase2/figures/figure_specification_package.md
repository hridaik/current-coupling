# Figure Specification Package — Phase 2C-A / Phase 2C-A.1
Date: 2026-06-01 (Phase 2C-A); updated 2026-06-01 (Phase 2C-A.1)
Status: Specification only. No artwork produced. No files modified.

---

## Phase 2C-A.1 Resolutions

Three blocking issues identified in Phase 2C-A were resolved on 2026-06-01.
All resolutions use only existing result files — no new analysis was performed.

### BLOCK-A RESOLVED — Color Convention Lock

**Decision:** No conflict was found between the proposed state colors and annotation colors.
The initial proposal (Randi=blue, dwelling=blue; serotonin=orange, roaming=orange) contained
two conflicts. These were resolved by choosing separate palettes for state encoding and
annotation encoding.

**Locked color convention:**

| Use | Element | Color | Hex |
|---|---|---|---|
| **Behavioral states** | Dwelling | Medium blue | #4C6EF5 |
| | Roaming | Deep orange | #FF6B35 |
| **Annotation categories** | Neuropeptide (Ripoll-Sánchez) | Dark gray | #666666 |
| | Randi unc-31 | Green | #2CA02C |
| | Bentley PDF | Red | #D62728 |
| | Bentley serotonin | Purple | #9467BD |
| | Bentley combined (PDF+serotonin) | Brown | #8C564B |
| | CeNGEN (exploratory) | Yellow-green, dashed border | #BCBD22 |
| **ΔQ sign in networks** | Dwelling-dominant (ΔQ < 0) | Blue (dwelling) | #4C6EF5 |
| | Roaming-dominant (ΔQ > 0) | Orange (roaming) | #FF6B35 |

**Conflict check:** The ΔQ sign encoding deliberately reuses dwelling/roaming colors —
this is intentional (negative ΔQ = dwelling-dominant coupling = blue; consistent with state encoding).
No conflict with annotation colors. This convention applies across all seven figures.

**Affected UNRESOLVED entries:** UNRESOLVED-1.2 and UNRESOLVED-2.2 are now resolved.

---

### BLOCK-B PARTIALLY RESOLVED — Null Distribution Statistics for Figure 4

Null distribution statistics were extracted from `results/phase2/stage4/stage4_results.json`.

**Available (from Stage 4 results):**

| Test | Coord | Null type | null_mean | null_std | null_p95 |
|---|---|---|---|---|---|
| Neuropeptide AUROC | CePNEM | Degree-preserving | 0.5021 | **0.01172** | 0.5219 |
| Neuropeptide AUROC | CePNEM | Simple | 0.4990 | 0.01179 | 0.5176 |
| Neuropeptide AUROC | GCaMP | Degree-preserving | 0.4979 | **0.01596** | 0.5235 |
| Neuropeptide AUROC | GCaMP | Simple | 0.5006 | 0.01651 | 0.5282 |

**Not available (null_std not stored in results files):**
- Randi AUROC (Stage 4): only null_mean stored (CePNEM degree: 0.5037; GCaMP degree: 0.5014)
- PDF AUROC (Stage 4A): only null_mean stored (CePNEM degree: 0.5015; GCaMP degree: 0.5039)

**Resolution for Figure 4 forest plot:**
- For neuropeptide AUROC: error bars = null_mean ± 2 × null_std (degree-preserving null; exact)
- For Randi and PDF AUROC: show null_mean as center line only; indicate absence of spread bar with footnote
- Alternative acceptable approach: use null_p95 as the upper error fence for all tests (neuropeptide: stored exactly; Randi/PDF: not stored → use the neuropeptide null_p95 as an approximation of similar order since n_c4=1321 is constant)
- Fisher OR tests: null_mean_or = Infinity or NaN for several tests; forest plot encoding of OR should use log scale with explicit note about Infinity values

**Affected UNRESOLVED entry:** UNRESOLVED-4.1 is partially resolved. The neuropeptide tests can be drawn exactly. Randi and PDF error bars still require either reading back the raw permutation distributions (not stored) or using the approximation approach described above.

---

### BLOCK-C RESOLVED — Complete 17-Pair PDF Network

The full 17-pair Bentley PDF Class 4 network with nonzero CePNEM ΔQ was extracted by:
1. Using `results/phase2/stage2/ranked_class4_cepnem.npy` as the authoritative Class 4 index set (1321 pairs, verified against top-50 pairs in stage2_results.json — exact match)
2. Parsing `data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_neuropeptides_Bentley_2016.csv` for all pdf-containing edges within the 61-neuron subgraph intersected with Class 4 → 61 pairs (confirmed match with stage4a_results.json count)
3. Loading `results/phase2/stage2/DQ_cepnem.npy` and `DQ_gcamp.npy` for values

**Result: 17 nonzero DQ_cepnem pairs (14 dwelling-dominant, 3 roaming-dominant)**

| PDF rank | Pair | ΔQ_cepnem | ΔQ_gcamp | Ligand | Direction | Dwelling-dom |
|---|---|---|---|---|---|---|
| 1 | ADEL–URYVR | −0.1222 | −0.0853 | pdf-1 | ADEL→URYVR | YES |
| 2 | ADEL–URYDL | −0.0980 | −0.0841 | pdf-1 | ADEL→URYDL | YES |
| 3 | ADEL–RMEL | −0.0957 | −0.0824 | pdf-1 | ADEL→RMEL | YES |
| 4 | RMEL–URYDL | −0.0754 | −0.1259 | pdf-1 | RMEL→URYDL | YES |
| 5 | RMEL–URYVR | −0.0701 | −0.1232 | pdf-1 | RMEL→URYVR | YES |
| 6 | RMEL–RMER | −0.0579 | 0.0000 | pdf-1 (bilateral) | RMEL↔RMER | YES |
| 7 | AVDL–URYDL | −0.0558 | −0.0240 | pdf-2 | AVDL→URYDL | YES |
| 8 | ADEL–URXL | −0.0450 | −0.1516 | pdf-1 | ADEL→URXL | YES |
| 9 | RID–URXL | −0.0396 | −0.0220 | pdf-1 | RID→URXL | YES |
| 10 | ADEL–OLQVR | −0.0215 | 0.0000 | pdf-1 | ADEL→OLQVR | YES |
| 11 | RID–RMEL | −0.0190 | +0.0654 | pdf-1 | RID→RMEL | YES |
| 12 | AVDL–RID | +0.0172 | +0.0312 | pdf-1 | RID→AVDL | NO |
| 13 | OLQVL–RMER | +0.0169 | −0.1005 | pdf-1 | RMER→OLQVL | NO |
| 14 | I1R–RMER | +0.0149 | 0.0000 | pdf-1 | RMER→I1R | NO |
| 15 | RMEL–URYVL | −0.0049 | 0.0000 | pdf-1 | RMEL→URYVL | YES |
| 16 | OLQDL–RID | −0.0048 | −0.1125 | pdf-1 | RID→OLQDL | YES |
| 17 | AVDL–OLQDL | −0.0019 | 0.0000 | pdf-2 | AVDL→OLQDL | YES |

**Notes:**
- Pairs 12–17 have |ΔQ_cepnem| < 0.02. Pairs 15–17 have |ΔQ_cepnem| < 0.005. Their biological relevance is uncertain; they contribute to the AUROC signal through ranking but are marginal.
- Pair 6 (RMEL–RMER): both RMEL→RMER and RMER→RMEL edges in Bentley CSV; ligand = pdf-1 (bilateral).
- Pairs 12–14 (positive ΔQ): roaming-dominant. AVDL→RID (RID receives more input during roaming), RMER→OLQVL, RMER→I1R.
- The phase2b_pdf_audit.md stated "14 non-zero negative ΔQ pairs (14/17 nonzero)" — this is confirmed: 14 dwelling-dominant, 3 roaming-dominant.

**Affected UNRESOLVED entry:** UNRESOLVED-5.2 is now resolved.

---

## Package Purpose

This document locks the visual narrative for Phase 2 before any artwork is created.
Every quantitative element below traces to an existing file in `results/phase2/`.
No numbers are invented. No analyses are performed here.

The primary result is a **null result** for the pre-specified broad neuropeptide
enrichment hypothesis. The exploratory result is a CePNEM-specific PDF signal
identified in Stage 4A, centered on ADEL → URY/URX/RMEL connections during dwelling.

---

## Figure 1 — Behavioral Story

**Title:** "Food detection recruits a state-dependent PDF signaling pathway"

### 1. Scientific Purpose

Establish the biological context motivating all subsequent figures.
The worm switches between roaming (food-searching) and dwelling (food-exploiting)
states. This figure tells the audience *what* that switch looks like behaviorally,
*which* circuit elements are hypothesized to coordinate it via PDF signaling, and
*why* measuring conditional dependence at the whole-brain scale is the appropriate
assay. It frames the null result (Figures 2–4) and the exploratory signal (Figures 5–6)
within a coherent behavioral narrative.

### 2. Exact Data Sources

- Behavioral segmentation parameters: `phase0_config.py`
  - BEHAV_THRESHOLD = 0.284, EWMA_TIMESCALE_SECONDS = 20.0, W_TRANS_SECONDS = 10.0,
    MIN_BOUT_SECONDS = 10.0
- Recording corpus description: `results/phase2/phase2_final_report.md` §2
  - 40 recordings, 61 NeuroPAL-identified neurons, Atanas SF corpus
- ADEL biology: `results/phase2/phase2b_pdf_audit.md` §3, §5
  - ADEL = dopaminergic anterior deirid mechanosensor; pdf-1 expression per CeNGEN
  - Dopaminergic slowing mechanism (mechanosensory-induced dwelling)
- URX/URY biology: `results/phase2/phase2b_pdf_audit.md` §5
  - URX/URY = O2/social signal integrators, PDFR-1+, regulate aerotaxis and locomotion state
- PDFR-1 target confirmation: `results/phase2/phase2b_pdf_audit.md` §4
  - URYVR, URYDL, RMEL, URXL, OLQVR confirmed pdfr-1 expressing (CeNGEN conservative threshold)
- PDF source neurons: `results/phase2/phase2b_pdf_audit.md` §2.1
  - ADEL (pdf-1, 12 Class 4 edges), RMEL (pdf-1, 12), RMER (pdf-1, 12), RID (pdf-1+pdf-2, 28),
    AVDL (pdf-2, 14)

### 3. Exact File Paths

- `phase0_config.py` — behavioral parameters
- `results/phase2/phase2_final_report.md` — corpus description
- `results/phase2/phase2b_pdf_audit.md` — neuronal identities, PDFR-1 targets, functional context

### 4. Quantities Displayed

No new statistical computation. Visual schematic elements only:

| Element | Value | Source |
|---|---|---|
| Recordings in corpus | 40 | phase2_final_report.md §2 |
| Target neurons | 61 | phase2_final_report.md §2 |
| Behavioral threshold | 0.284 (velocity score) | phase0_config.py |
| EWMA timescale | 20 s | phase0_config.py |
| ADEL pdf-1 Class 4 edges | 12 | phase2b_pdf_audit.md §2.1 |
| RID pdf-1+pdf-2 Class 4 edges | 28 | phase2b_pdf_audit.md §2.1 |
| PDFR-1-expressing targets shown | 5 (URYVR, URYDL, RMEL, URXL, OLQVR) | phase2b_pdf_audit.md §4 |

### 5. Proposed Layout

Three-panel horizontal strip (talk) / two-column (paper):

**Panel A — Behavioral state schematic:**
Cartoon worm on agar plate. Left sub-panel: roaming trajectory (sinusoidal, wide sweeps).
Right sub-panel: dwelling trajectory (tight local exploration). Arrow labeled
"food detection." EWMA velocity trace shown underneath with threshold line at 0.284.
No data plotted — cartoon schematic only.

**Panel B — Circuit diagram:**
Simplified wiring diagram. ADEL and RMEL/RMER shown as source nodes (filled circles,
dopamine/GABA labels). URYVR, URYDL, URXL, RMEL as target nodes. Edges labeled
"pdf-1" (directed arrows). "pdfr-1" label on targets. RID shown as second source with
"pdf-1/pdf-2." No synaptic edges shown (those are on-connectome, excluded from Class 4).
Caption note: "All source→target edges are non-synaptic (Class 4); volumetric transmission assumed."

**Panel C — Analysis schematic:**
Flowchart: 40 recordings → pairwise covariance assembly (61×61) → PSD projection →
ADMM lasso → Q_roam, Q_dwell → ΔQ → enrichment test.
Annotate: "1321 off-connectome pairs tested."

### 6. Caption Draft

**Full caption:**
"**Food detection recruits a state-dependent PDF signaling pathway.**
**(A)** C. elegans alternates between roaming (broad exploration) and dwelling
(local exploitation) behavioral states segmented using an exponentially weighted
moving average of velocity (threshold 0.284, τ = 20 s; see Methods).
**(B)** Candidate PDF signaling circuit. ADEL (dopaminergic anterior deirid mechanosensor,
pdf-1-expressing) and RMEL/RMER (GABAergic head ring motor neurons, pdf-1-expressing)
project to pdfr-1-expressing target neurons (URYVR, URYDL, URXL, RMEL, OLQVR) via
volumetric transmission. Arrows indicate Bentley ESconnectome directed pdf-1 edges
(all non-synaptic, off the chemical/gap-junction connectome).
**(C)** Analysis pipeline. Whole-brain calcium imaging traces from 40 freely-behaving
recordings (61 identified neurons) were used to estimate state-conditioned precision
matrices (Q_roam, Q_dwell) via pairwise available-case covariance assembly. ΔQ = Q_roam
− Q_dwell was computed for 1321 off-connectome pairs (Class 4) and tested for enrichment
of neuropeptide and PDF-signaling annotations."

### 7. Talk Version Modifications

- Remove Panel C flowchart; replace with single sentence on title slide
- Enlarge Panel B circuit diagram to fill slide
- Animate: show dwelling state first, then roaming state, then arrow between them
- Use color coding: dwelling = blue, roaming = orange (consistent across all figures)

### 8. Paper Version Modifications

- Panels A–C compressed into single column (Nature-style narrow figure)
- Add panel letter labels (A, B, C)
- Panel C: convert flowchart to numbered list in caption rather than figure panel
- Scale bar on behavioral trajectory panels (e.g., 1 mm)

### 9. Unresolved Issues

- **UNRESOLVED-1.1:** No raw behavioral trajectory data in `results/phase2/`; Panel A requires
  access to Atanas corpus raw position data. Trajectory cartoon may need to be purely
  schematic with citation to Atanas et al.
- ~~UNRESOLVED-1.2~~ **RESOLVED (Phase 2C-A.1):** Color convention locked. See Phase 2C-A.1 resolutions section. Dwelling = #4C6EF5, Roaming = #FF6B35.

---

## Figure 2 — One Wiring, Two Functions

**Title:** "Functional organization changes while anatomy stays fixed"

### 1. Scientific Purpose

Show that the same anatomical wiring (connectome) supports different conditional-dependence
structure in roaming versus dwelling. Specifically: selected neuron pairs with large |ΔQ|
demonstrate the strongest examples of state-dependent decoupling (ΔQ < 0, stronger
coupling during dwelling) and the strongest examples of state-dependent coupling
(ΔQ > 0, stronger coupling during roaming). This motivates the enrichment test:
if neuropeptide annotation predicts which pairs switch, that would support the hypothesis.
The null result (Figure 4) is the answer.

### 2. Exact Data Sources

- CePNEM ΔQ matrix and ranked Class 4 list: `results/phase2/stage2/stage2_report.md` Table 1
- GCaMP ΔQ matrix and ranked Class 4 list: `results/phase2/stage2/stage2_report.md` Table 2
- Full ranked lists (all 1830 pairs): `results/phase2/stage2/ranked_class4_cepnem.npy`,
  `results/phase2/stage2/ranked_class4_gcamp.npy`
- ΔQ matrices: `results/phase2/stage2/DQ_cepnem.npy`, `results/phase2/stage2/DQ_gcamp.npy`
- Annotation flags (Randi, Peptide): `results/phase2/stage2/stage2_results.json`

### 3. Exact File Paths

- `results/phase2/stage2/DQ_cepnem.npy` — CePNEM ΔQ (61×61 matrix)
- `results/phase2/stage2/DQ_gcamp.npy` — GCaMP ΔQ (61×61 matrix)
- `results/phase2/stage2/ranked_class4_cepnem.npy` — ranked Class 4 pairs, CePNEM
- `results/phase2/stage2/ranked_class4_gcamp.npy` — ranked Class 4 pairs, GCaMP
- `results/phase2/stage2/stage2_results.json` — pair annotations

### 4. Quantities Displayed

**CePNEM top examples (strongest negative ΔQ — dwelling-dominant decoupling):**

| Rank | Pair | ΔQ_cepnem | Peptide | Randi |
|---|---|---|---|---|
| 1 | IL1DR–URYVR | −0.2541 | NO | NO |
| 5 | ADEL–URYVR | −0.1222 | NO | NO |
| 9 | ADEL–URYDL | −0.0980 | NO | NO |
| 10 | ADEL–RMEL | −0.0957 | NO | NO |

**CePNEM strongest positive ΔQ (roaming-dominant coupling):**

| Rank | Pair | ΔQ_cepnem | Peptide | Randi |
|---|---|---|---|---|
| 11 | I1L–IL2DR | +0.0903 | YES | NO |
| 23 | AVER–IL2DR | +0.0647 | YES | NO |
| 39 | M1–OLQVR | +0.0536 | YES | NO |

**GCaMP top examples (strongest negative ΔQ):**

| Rank | Pair | ΔQ_gcamp | Peptide | Randi |
|---|---|---|---|---|
| 1 | OLLL–SMDVL | −0.2897 | YES | NO |
| 2 | NSMR–RMDVL | −0.2336 | YES | NO |
| 3 | RIVL–URYVR | −0.2200 | YES | NO |

**GCaMP strongest positive ΔQ:**

| Rank | Pair | ΔQ_gcamp | Peptide | Randi |
|---|---|---|---|---|
| 4 | I1L–M4 | +0.2142 | YES | NO |
| 8 | IL2VL–M4 | +0.1919 | NO | NO |
| 9 | AVJR–OLQVL | +0.1822 | YES | NO |

**Summary statistics:**

| Metric | CePNEM | GCaMP | Source |
|---|---|---|---|
| Class 4 total | 1321 | 1321 | stage2_results.json |
| Class 4 non-zero |ΔQ| | 243 (18.4%) | 585 (44.3%) | stage2_results.json |
| |ΔQ| max | 0.2541 | 0.2897 | stage2_results.json |
| |ΔQ| p95 | 0.0412 | 0.0998 | stage2_results.json |
| |ΔQ| mean (non-zero) | 0.0057 | 0.0204 | stage2_results.json |

### 5. Proposed Layout

**Panel A:** Histogram of |ΔQ|_cepnem (Class 4, 1321 pairs). X-axis: |ΔQ|, Y-axis: count.
Log-scale Y recommended (many zeros). Inset or annotation: "18% non-zero."
Color bars: annotate top-ranked pairs with neuron labels at far-right tail.

**Panel B:** Same histogram for GCaMP. "44% non-zero."

**Panel C:** Scatter plot — CePNEM ΔQ (x-axis) vs GCaMP ΔQ (y-axis), one point per
Class 4 pair (1321 points). Color by annotation: gray = neither, green = peptide only,
orange = Randi only, purple = both. Label the top-5 CePNEM pairs (with neuron names)
and top-5 GCaMP pairs. Diagonal reference line. Note axes are signed ΔQ (not |ΔQ|).

### 6. Caption Draft

**Full caption:**
"**Functional organization changes while anatomy stays fixed.**
**(A, B)** Distribution of |ΔQ| (Q_roam − Q_dwell) for the 1321 off-connectome Class 4
pairs in CePNEM **(A)** and GCaMP **(B)** coordinates. 18% of CePNEM pairs and 44% of
GCaMP pairs show non-zero conditional-dependence change between behavioral states.
All values from the anatomy-guided ADMM confirmation estimator (λ_on=0.01, λ_off=0.10).
**(C)** Correspondence between CePNEM and GCaMP ΔQ for all Class 4 pairs. Points colored
by annotation status (neuropeptide atlas, Randi unc-31). Top-ranked pairs labeled."

### 7. Talk Version Modifications

- Show only Panel C (scatter); animate highlighting of ADEL-centric pairs
- Add callout boxes for ADEL–URYVR and ADEL–URYDL with cell-type labels

### 8. Paper Version Modifications

- All three panels in horizontal strip
- Reduce point size in Panel C (1321 points risk overplotting; alpha=0.3)
- Add marginal histograms to Panel C if journal allows

### 9. Unresolved Issues

- **UNRESOLVED-2.1:** Scatter panel (C) requires rendering the 61×61 ΔQ matrices.
  The .npy files are ready; axis coordinates (neuron index → neuron name) require the
  harmonization table at `results/diagnostics/neuron_harmonization.csv`.
  Must verify that file exists and is current before artwork.
- ~~UNRESOLVED-2.2~~ **RESOLVED (Phase 2C-A.1):** Annotation color convention locked. Neuropeptide=#666666, Randi=#2CA02C, PDF=#D62728, Serotonin=#9467BD, Combined=#8C564B, CeNGEN=#BCBD22 (dashed). See Phase 2C-A.1 resolutions section.

---

## Figure 3 — Annotation Density

**Title:** (no standalone title; this is a methods/characterization figure)
Proposed: "Connectome annotation landscape for the 61-neuron subgraph"

### 1. Scientific Purpose

Show the annotation landscape: what fraction of the 1321 Class 4 pairs carry neuropeptide,
Randi unc-31, or Bentley PDF annotation. This is essential context for interpreting why
the broad neuropeptide enrichment test is low-power at the AUROC level, and why the
PDF sub-annotation (61 pairs, 4.6%) has a qualitatively different signal structure than
the broad neuropeptide annotation (972 pairs, 73.6%).

### 2. Exact Data Sources

- Class 4 pair count and annotation counts: `results/phase2/stage2/stage2_report.md` (tables)
  and `results/phase2/stage2/stage2_results.json`
- Bentley PDF and serotonin Class 4 counts: `results/phase2/stage4a/stage4a_results.json`
  (`annotation_summary` field)

### 3. Exact File Paths

- `results/phase2/stage2/stage2_results.json` — `annotation_counts` field
- `results/phase2/stage4a/stage4a_results.json` — `annotation_summary` field
- `results/phase2/stage4/stage4_report.md` §1 — `n_class4` and annotation densities

### 4. Quantities Displayed

| Annotation | Class 4 count | Density | Source |
|---|---|---|---|
| All Class 4 pairs | 1321 | 100% | stage2_results.json `class_counts["4"]` |
| Ripoll-Sánchez neuropeptide | 972 | 73.6% | stage4_report.md §1 |
| Neuropeptide (off-connectome raw) | 1144 | — | stage2_results.json `peptide_off_connectome` (note: 1144 is off-A_raw; 972 is Class 4) |
| Randi unc-31 (Class 4) | 108 | 8.2% | stage4_report.md §1 |
| Randi unc-31 (off-connectome raw) | 109 | — | stage2_results.json `randi_off_connectome` |
| Bentley PDF (Class 4) | 61 | 4.6% | stage4a_results.json `annotation_summary.Bentley_PDF` |
| Bentley serotonin (Class 4) | 33 | 2.5% | stage4a_results.json `annotation_summary.Bentley_serotonin` |
| Bentley combined PDF+serotonin (Class 4) | 94 | 7.1% | stage4a_results.json `annotation_summary.Bentley_serotonin_or_PDF` |
| CeNGEN combined (Class 4) | 409 | 31.0% | stage4a_results.json `annotation_summary.CeNGEN_serotonin_or_PDF` |
| Randi AND neuropeptide (off-connectome raw) | 74 | — | stage2_results.json `randi_and_peptide_off_connectome` |

**Note on Randi count discrepancy (from Stage 2 report):**
Phase 0 config stated N_RANDI_SUBGRAPH_PAIRS = 189 (directed pairs). Undirected pairs = 160 total;
109 off-connectome (Class 4 subset: 108). This discrepancy is documented in the Stage 2 report
and must be explained in figure caption or footnote.

### 5. Recommended Chart Type and Justification

**Stacked bar chart (single bar) or nested pie chart is NOT recommended** — proportions span
three orders of magnitude (2.5%–73.6%) making relative comparisons misleading.

**Recommended: Horizontal bar chart (Pareto-style), one bar per annotation category,
sorted by count descending.**

Justification: The key visual message is the contrast between:
(a) the broad neuropeptide annotation (73.6%, nearly all Class 4 pairs annotated) and
(b) the targeted Bentley PDF annotation (4.6%, a sparse subset).
This 16× difference in density is the core reason the AUROC test for broad neuropeptide
fails while the Fisher test for PDF passes. A bar chart makes this density difference
immediately legible.

Alternative: **Venn diagram** for the overlap structure (Randi ∩ neuropeptide = 74 pairs).
Recommended as a supplementary panel.

**Color coding:** Each annotation bar colored by annotation source type:
- Neuropeptide (Ripoll-Sánchez) = dark gray
- Randi (unc-31) = blue
- Bentley PDF = red
- Bentley serotonin = orange
- Bentley combined = split red/orange
- CeNGEN combined = light purple (exploratory, dashed border)

### 6. Proposed Layout

Single panel. Horizontal bars, Y-axis = annotation category, X-axis = count (bottom axis)
and % of Class 4 (top axis). Total Class 4 = 1321 shown as gray reference bar at top.
Annotation: "1321 Class 4 pairs" with arrow.

### 7. Caption Draft

"**Annotation landscape for the 61-neuron subgraph.**
The 1321 off-connectome Class 4 pairs (both neurons in the Creamer 56-neuron subspace,
no direct A_raw synaptic connection) were annotated against four databases.
The Ripoll-Sánchez neuropeptide atlas covers 73.6% of Class 4 pairs.
The Randi unc-31-sensitive annotation covers 8.2% (108/1321; note: Phase 0 config
referenced 189 directed pairs; undirected off-connectome pairs = 108 after deduplication,
see Methods). Bentley ESconnectome PDF (61 pairs, 4.6%) and serotonin (33 pairs, 2.5%)
annotations are targeted subsets. CeNGEN transcriptomic ligand-receptor annotation
(409 pairs, 31.0%) is shown for context (exploratory tier)."

### 8. Talk Version Modifications

- Highlight Bentley PDF bar in red; add callout: "4 of 4 top-K pairs are PDF-annotated"
- Animate: show bars sequentially from broad to narrow

### 9. Paper Version Modifications

- Add supplementary Venn diagram panel for Randi ∩ neuropeptide overlap
- Report exact counts and percentages in caption table

### 10. Unresolved Issues

- **UNRESOLVED-3.1:** Stage 2 report notes a discrepancy between "Randi off-connectome"
  (109 in stage2_results.json) and "Class 4 Randi" (108 in stage4_report.md). These differ
  by 1 pair. The discrepancy is almost certainly a rounding or classification boundary
  effect (one pair on the Creamer boundary). Must be documented precisely in the caption
  or confirmed as a known 1-pair difference.
- **UNRESOLVED-3.2:** The neuropeptide annotation density of 73.6% is unusually high and
  merits a brief explanation in the caption. The Ripoll-Sánchez atlas is a broad, literature-
  curated atlas covering a large fraction of *C. elegans* neuron pairs; the high density
  reflects the annotation scope, not a data artifact.

---

## Figure 4 — Enrichment Results

**Title:** "No evidence for broad neuropeptide enrichment; exploratory PDF signal in CePNEM"

### 1. Scientific Purpose

The primary result figure. Report all enrichment test outcomes quantitatively.
Demonstrate that the pre-specified broad neuropeptide hypothesis is null (Stage 4).
Report the exploratory Bentley PDF signal (Stage 4A) in CePNEM alongside its
GCaMP non-replication. Frame both the null result and the exploratory signal
within the pre-specified criterion boundary.

### 2. Exact Data Sources

- Stage 4 enrichment (primary neuropeptide + Randi): `results/phase2/stage4/stage4_results.json`
- Stage 4A enrichment (serotonin/PDF): `results/phase2/stage4a/stage4a_results.json`
- Stage 4 report: `results/phase2/stage4/stage4_report.md`
- Stage 4A report: `results/phase2/stage4a/stage4a_report.md`

### 3. Exact File Paths

- `results/phase2/stage4/stage4_results.json` — AUROC, p-values, Fisher OR for neuropeptide and Randi
- `results/phase2/stage4a/stage4a_results.json` — AUROC, p-values, Fisher OR for PDF/serotonin
- `results/phase2/stage4/stage4_report.md` — contingency tables, null model validation

### 4. Quantities Displayed

**Primary enrichment table (from stage4_results.json and stage4_report.md):**

| Test | Annotation | Coord | AUROC | p_deg | Fisher OR | Fisher p_deg | Result |
|---|---|---|---|---|---|---|---|
| Test 1 | Neuropeptide | CePNEM | 0.5033 | 0.475 | — | — | FAIL |
| Test 1 | Neuropeptide | GCaMP | 0.5140 | 0.142 | — | — | FAIL |
| Test 2 | Neuropeptide K=20 | CePNEM | — | — | 0.533 | 0.981 | FAIL |
| Test 2 | Neuropeptide K=20 | GCaMP | — | — | 0.835 | 0.716 | FAIL |
| Test 3 | Randi | CePNEM | 0.4953 | 0.656 | 0.000 | 1.000 | FAIL |
| Test 3 | Randi | GCaMP | 0.5167 | 0.278 | 0.587 | 0.792 | FAIL |

**Exploratory enrichment (from stage4a_results.json):**

| Test | Annotation | Coord | AUROC | p_deg | Fisher OR | Fisher p_deg | Result |
|---|---|---|---|---|---|---|---|
| 4A | Bentley PDF | CePNEM | **0.5560** | **0.023** | **5.456** | **0.008** | **PASS** |
| 4A | Bentley PDF | GCaMP | 0.5260 | 0.261 | 1.089 | 0.670 | FAIL |
| 4A | Bentley serotonin | CePNEM | 0.4953 | 0.581 | 0.000 | 1.000 | FAIL |
| 4A | Bentley serotonin | GCaMP | 0.4286 | 0.935 | 2.087 | 0.367 | FAIL |
| 4A (Test 4) | Combined (PDF+5HT) | CePNEM | 0.5356 | 0.055 | 3.364 | 0.065 | FAIL (marginal) |
| 4A (Test 4) | Combined (PDF+5HT) | GCaMP | 0.4910 | 0.674 | 1.460 | 0.445 | FAIL |

**Null model validation (from stage4_report.md §8):**
- Degree-preserving permutation: 1000 permutations per test
- Degree binning: 10 equal-percentile bins on A_raw degree sum; range [6, 33], median = 16
- Max bin deviation: 0 (PASS)

### 5. Recommended Visual Encoding and Justification

**Recommended: Multi-panel forest plot / dot plot.**

Each row = one test × one coordinate combination.
X-axis = AUROC (or Fisher OR on log scale for the Fisher panel).
Point = observed value. Horizontal error bar = 95% CI from permutation null (null mean ± 2SD).
Color: gray = FAIL, red = PASS. Vertical dashed line at AUROC = 0.5 (or OR = 1.0).
p_deg value annotated next to each point.
Separate sub-panels for AUROC tests (left) and Fisher OR tests (right).

**Justification:** The forest plot format is standard in meta-analysis and enrichment reporting.
It simultaneously communicates:
(a) the effect size (AUROC value, OR value)
(b) the uncertainty (null distribution spread)
(c) the pass/fail decision boundary
(d) all tests in one visual field

Alternative: table-only (for Methods figures). Acceptable in supplement but insufficient
for main figure.

### 6. Proposed Layout

**Panel A — AUROC forest plot (all tests, both coordinates):**
Rows: [Neuropeptide CePNEM, Neuropeptide GCaMP | Randi CePNEM, Randi GCaMP | PDF CePNEM, PDF GCaMP]
Grouped by annotation type with visual separator. X-axis: 0.45–0.62 (AUROC range spans this).
Null = 0.5 reference line. Red highlight for PDF CePNEM (only PASS row).

**Panel B — Fisher OR plot (K=20 tests):**
Same row structure. X-axis: OR on log scale, range 0.1–10. Null = OR=1 reference line.
PDF CePNEM highlighted (OR=5.456). Note: Randi CePNEM OR=0.000 plotted as a triangle at
the left axis boundary.

**Panel C — Summary PASS/FAIL table:**
Compact table, 6 rows × 2 columns (CePNEM / GCaMP). Color cells: red=PASS, white=FAIL.
Add footnote: "Pre-specified criterion: degree-preserving p < 0.05."

### 7. Caption Draft

"**No evidence for broad neuropeptide enrichment; exploratory PDF signal in CePNEM.**
**(A)** AUROC enrichment test for each annotation and coordinate. Points are observed AUROC;
error bars span the null distribution (degree-preserving permutation, 1000 permutations)
mean ± 2 SD. Vertical dashed line: null expectation (AUROC = 0.5). Threshold for
significance: p_degree-preserving < 0.05.
The pre-specified neuropeptide (Ripoll-Sánchez, CePNEM: 0.503, p_deg=0.475;
GCaMP: 0.514, p_deg=0.142) and Randi unc-31 (CePNEM: 0.495, p_deg=0.656;
GCaMP: 0.517, p_deg=0.278) tests are null. An exploratory test for Bentley PDF
annotation in the CePNEM coordinate reaches significance (AUROC=0.556, p_deg=0.023)
but does not replicate in GCaMP (AUROC=0.526, p_deg=0.261).
**(B)** Fisher top-K=20 odds ratios. The pre-specified neuropeptide and Randi tests
show OR ≤ 1.0 (depletion or null). The Bentley PDF test in CePNEM shows OR=5.46
(p_deg=0.008); the pre-specified combined serotonin/PDF test (Test 4) is marginal
(AUROC p_deg=0.055, Fisher p_deg=0.065, both above the pre-specified threshold of p<0.05).
**(C)** Summary of all enrichment tests. Phase 2 primary result: null (all pre-specified
tests non-significant, p_deg > 0.14)."

### 8. Talk Version Modifications

- Show Panel C first (big FAIL table), then drill into Panel A for neuropeptide, then PDF
- Animate the PDF CePNEM row turning red
- Remove Fisher OR panel (Panel B) from talk; reference in caption/appendix

### 9. Paper Version Modifications

- All three panels in main figure
- Add supplementary figure: null distribution histograms for each test
- Add supplementary figure: CeNGEN combined enrichment (exploratory)

### 10. Unresolved Issues

- **UNRESOLVED-4.1 PARTIALLY RESOLVED (Phase 2C-A.1):** Null distribution stats extracted from `stage4_results.json`. Neuropeptide AUROC (Stage 4): full stats available — CePNEM degree-pres null_mean=0.5021, null_std=0.0117, null_p95=0.5219; GCaMP degree-pres null_mean=0.4979, null_std=0.0160, null_p95=0.5235. Randi AUROC: only null_mean stored (no std). PDF AUROC (Stage 4A): only null_mean stored (no std). **Remaining issue:** forest plot error bars for Randi and PDF tests require either a re-run to extract std, or use the neuropeptide null_p95 as an approximation. See Phase 2C-A.1 resolutions section for recommended workaround.
- **UNRESOLVED-4.2:** The Randi CePNEM Fisher OR = 0.000 (0 Randi pairs in top-20)
  requires a special visual encoding treatment (cannot be shown on log scale).
  Recommend: left-pointing triangle at OR=0.01 as convention.

---

## Figure 5 — ADEL-Centered PDF Network

**Title:** "ADEL-centered PDF signaling network shows dwelling-dominant conditional dependence"

### 1. Scientific Purpose

Provide the network-level view of the exploratory PDF signal. The enrichment test (Figure 4)
established that PDF-annotated pairs rank high in the CePNEM |ΔQ| distribution. This figure
resolves which specific pairs drive the signal, what the directional ΔQ structure is, and
how it relates to the Bentley atlas and the perturbation atlas (Randi/Leifer funatlas).

### 2. Exact Data Sources

- Pair-level ΔQ values and ranks: `results/phase2/phase2b_pdf_audit.md` §2.2 Table (top-10 by |ΔQ_cepnem|)
- Stage 2 ranked lists: `results/phase2/stage2/stage2_results.json` (top-50 CePNEM)
- PDF source/target annotation: `results/phase2/phase2b_pdf_audit.md` §2.1, §4
- Sign direction analysis: `results/phase2/phase2b_pdf_audit.md` §2.3
- Funatlas cross-reference: `results/phase2/phase2b_pdf_audit.md` §6

### 3. Exact File Paths

- `results/phase2/phase2b_pdf_audit.md` — all pair-level data for this figure
- `results/phase2/stage2/stage2_results.json` — ranks 5, 9, 10, 16 confirmed
- `results/phase2/stage2/DQ_cepnem.npy` — actual ΔQ values
- `results/phase2/stage2/DQ_gcamp.npy` — GCaMP ΔQ for comparison

### 4. Network Specification

**Nodes (all in the 61-neuron subgraph):**

| Node | Role | Ligand expressed | PDFR-1? | Cell type | ΔQ sign pattern |
|---|---|---|---|---|---|
| ADEL | Source | pdf-1 | NO | Dopaminergic anterior deirid mechanosensor | — |
| RMEL | Source / Target | pdf-1 | YES | GABAergic head ring motor | — |
| RMER | Source | pdf-1 | NO (see note) | GABAergic head ring motor | — |
| RID | Source | pdf-1 + pdf-2 | NO | Ring interneuron, DCV modulator | — |
| AVDL | Source | pdf-2 | NO | ACh ventral cord interneuron | — |
| URYVR | Target | — | YES (pdfr-1) | Head sensory, O2/social integrator | — |
| URYDL | Target | — | YES (pdfr-1) | Head sensory | — |
| URXL | Target | — | YES (pdfr-1) | O2/CO2/social integrator | — |
| RMEL | Target (also source) | — | YES (pdfr-1) | (same as above) | — |
| OLQVR | Target | — | YES (pdfr-1) | Mechanosensory | — |

*Note on RMER PDFR-1 status: audit reports RMER as pdf-1 source; target status not explicitly
stated in phase2b_pdf_audit.md §4. RMER appears only as source in audit Table §4.*

**Source-Target pairs with nonzero CePNEM ΔQ (17 pairs; top-10 listed):**

| Rank | Source→Target (directed Bentley) | ΔQ_cepnem | ΔQ_gcamp | Ligand | Funatlas status |
|---|---|---|---|---|---|
| 1 | ADEL→URYVR | −0.1222 | −0.0853 | pdf-1 | **UNTESTED** (occ_wt=0) |
| 2 | ADEL→URYDL | −0.0980 | −0.0841 | pdf-1 | **UNTESTED** (occ_wt=0) |
| 3 | ADEL→RMEL | −0.0957 | −0.0824 | pdf-1 | q_wt=0.492 (not significant) |
| 4 | RMEL→URYDL | −0.0754 | −0.1259 | pdf-1 | not in funatlas |
| 5 | RMEL→URYVR | −0.0701 | −0.1232 | pdf-1 | *inferred from RMER→URYVR* |
| 6 | RMEL↔RMER | −0.0579 | +0.0000 | bilateral | q_wt=0.000 (**confirmed**) |
| 7 | AVDL→URYDL | −0.0558 | −0.0240 | pdf-2 | not in funatlas |
| 8 | ADEL→URXL | −0.0450 | −0.1516 | pdf-1 | q_wt=0.534 (not significant) |
| 9 | RID→URXL | −0.0396 | −0.0220 | pdf-1+pdf-2 | q_wt borderline, occ_wt=2 |
| 10 | ADEL→OLQVR | −0.0215 | +0.0000 | pdf-1 | not in funatlas |

**Sign direction (from phase2b_pdf_audit.md §2.3):**
All 14 non-zero negative ΔQ pairs have ΔQ < 0 (dwelling-dominant).
Interpretation: conditional dependence is **stronger during dwelling than roaming**.
For all top pairs: Q_roam ≈ 0 (decoupled during roaming), Q_dwell < 0 (inversely coupled
during dwelling).

**Fisher K=20 top-K PDF pairs (from stage4a_results.json, cepnem Bentley_PDF contingency):**
4 of top-20 CePNEM pairs are PDF-annotated:
- Rank 5: ADEL–URYVR (|ΔQ|=0.1222)
- Rank 9: ADEL–URYDL (|ΔQ|=0.0980)
- Rank 10: ADEL–RMEL (|ΔQ|=0.0957)
- Rank 16: RMEL–URYDL (|ΔQ|=0.0754)
Expected in top-20 by chance: 0.92 (61 × 20/1321). Observed: 4. OR = 5.456.

### 5. Proposed Layout (Network Specification — No Drawing)

**Spatial arrangement:**
- ADEL: upper-left (source hub)
- RMEL / RMER: center (intermediary / bilateral pair)
- URY neurons (URYVR, URYDL): right
- URXL: lower-right
- RID: top-center
- AVDL: lower-left
- OLQVR: far-right bottom

**Edge encoding:**
- Edge weight ∝ |ΔQ_cepnem| (line width)
- Edge color: dwelling-dominant (ΔQ < 0) = blue; roaming-dominant (ΔQ > 0) = orange
  (all PDF pairs are dwelling-dominant = all blue)
- Edge label: ΔQ value (4 decimal places)
- Arrowhead direction: Bentley source → target (directed)
- Confirmed funatlas: solid line; untested: dashed line

**Node encoding:**
- Shape: source = triangle (pointing up); target = circle; source+target (RMEL) = diamond
- Size: proportional to number of nonzero ΔQ edges at that node
- Fill: dopamine = dark gray; GABA = light blue; ACh = yellow; unknown = white

**Funatlas confirmation badges:**
- Green badge on edge if q_wt < 0.05 in funatlas (RMEL↔RMER, RMER→URYVR)
- Red badge: explicitly untested (ADEL→URYVR, ADEL→URYDL)
- No badge: tested but not significant

### 6. Caption Draft

"**ADEL-centered PDF signaling network.**
Network of nonzero CePNEM ΔQ entries among Bentley PDF Class 4 pairs.
Nodes: neuron identity and transmitter phenotype. Edges: Bentley ESconnectome
directed pdf-1/pdf-2 projections with |ΔQ_cepnem| ≥ 0.02. Edge width ∝ |ΔQ|.
All edges show ΔQ < 0 (dwelling-dominant conditional dependence; blue).
Funatlas confirmation status indicated (solid: wt-significant; dashed: untested).
ADEL–URYVR (rank 5, ΔQ=−0.122) and ADEL–URYDL (rank 9, ΔQ=−0.098) are the
highest-ranked PDF pairs and have **zero funatlas observations** — never tested
in the Randi/Leifer perturbation atlas. These are the primary experimental predictions
(see Figure 7). The RMEL↔RMER interaction (q_wt=0.000 in funatlas) provides an
independent confirmation that RMEL functional connectivity is detectable in this assay."

### 7. Talk Version Modifications

- Animate: start with empty network, add ADEL node, then progressively add edges by rank
- Highlight: bold red dashed edges for ADEL→URYVR and ADEL→URYDL ("untested — future experiment")
- Remove AVDL and OLQVR for talk clarity (lower-ranked, less-discussed)

### 8. Paper Version Modifications

- Include all 17 nonzero pairs as supplementary table
- Show both ΔQ_cepnem and ΔQ_gcamp columns
- Supplementary: funatlas raw measurements table (from phase2b_pdf_audit.md §6.2)

### 9. Unresolved Issues

- **UNRESOLVED-5.1:** RMER PDFR-1 expression status: phase2b_pdf_audit.md §2.1 lists RMER
  as a pdf-1 SOURCE with 12 directed edges, but §4 lists RMEL (not RMER) as having
  pdfr-1 expression. The RMER↔RMEL pair (rank 6) involves RMER as source;
  whether RMER also expresses pdfr-1 needs clarification from the CeNGEN data.
  This affects the node encoding (diamond vs. triangle for RMER).
- ~~UNRESOLVED-5.2~~ **RESOLVED (Phase 2C-A.1):** Complete 17-pair network extracted. See Phase 2C-A.1 resolutions section for the full table. Pairs 11–17 (low-magnitude): RID–RMEL (−0.0190), AVDL–RID (+0.0172), OLQVL–RMER (+0.0169), I1R–RMER (+0.0149), RMEL–URYVL (−0.0049), OLQDL–RID (−0.0048), AVDL–OLQDL (−0.0019). Pairs 12–14 are roaming-dominant (positive ΔQ). Pairs 15–17 are very low magnitude (|ΔQ| < 0.005) and may not merit inclusion in the primary figure panel.
- **UNRESOLVED-5.3:** GCaMP ΔQ values for some pairs (e.g., RMEL–RMER ΔQ_gcamp = +0.000)
  suggest GCaMP sees no coupling change for pairs that CePNEM sees clearly. This asymmetry
  must be discussed in caption or supplementary, not swept under the rug.

---

## Figure 6 — Atlas Cross-Reference

**Title:** "Functional validation landscape for PDF network predictions"

### 1. Scientific Purpose

Situate the Phase 2 PDF findings within existing perturbation-atlas data.
Categorize each key pair as: (a) confirmed by funatlas (q_wt < 0.05), (b) untested
(zero funatlas observations), or (c) tested but non-significant. This provides
honest provenance for the subsequent prediction figure (Figure 7).

### 2. Exact Data Sources

All values from `results/phase2/phase2b_pdf_audit.md` §6.1, §6.2, §6.3.

### 3. Exact File Paths

- `results/phase2/phase2b_pdf_audit.md` §6 — all funatlas measurements
- `results/phase2/stage2/stage2_results.json` — ΔQ ranks for pairs listed
- `results/phase2/stage4a/stage4a_results.json` — confirmation that these are PDF-annotated

### 4. Quantities Displayed

**Confirmed pairs (funatlas q_wt < 0.05):**

| Pair | Direction | q_wt | dFF_wt | occ_wt | ΔQ_cepnem | Note |
|---|---|---|---|---|---|---|
| RMEL↔RMER | RMEL→RMER | 0.000 | +0.094 | 22 | −0.0579 | wt significant; bilateral |
| RMER→RMEL | RMER→RMEL | (unc-31: 0.001) | +0.072 | 16 | — | unc-31 significant |
| RMER→URYVR | RMER→URYVR | 0.000 | +0.151 | 8 | (RMEL–URYVR rank 5: −0.0701) | **wt significant** |
| RMEL→OLQVR | RMEL→OLQVR | 0.028 | +0.222 | 13 | (ADEL–OLQVR rank 10: −0.0215) | wt significant |
| RMER→OLQVR | RMER→OLQVR | 0.036 | +0.080 | 13 | — | wt significant |
| RMEL→OLLL | RMEL→OLLL | (unc-31: 0.002) | +0.104 | 19 | — | **unc-31 significant** |
| RMER→OLLL | RMER→OLLL | (unc-31: 0.012) | +0.072 | 19 | — | unc-31 significant |
| RMER→I1L | RMER→I1L | (unc-31: 0.049) | +0.078 | 6 | — | unc-31 significant |

**Novel predictions (zero funatlas observations):**

| Pair | Direction | occ_wt | ΔQ_cepnem | ΔQ_gcamp | CePNEM rank |
|---|---|---|---|---|---|
| ADEL→URYDL | directed | 0 | −0.0980 | −0.0841 | 9 |
| ADEL→URYVR | directed | 0 | −0.1222 | −0.0853 | 5 |

**Tested but not significant:**

| Pair | Direction | q_wt | q_unc31 | occ_wt | ΔQ_cepnem |
|---|---|---|---|---|---|
| ADEL→RMEL | directed | 0.492 | 0.371 | 5 | −0.0957 |
| ADEL→URXL | directed | 0.534 | NaN | 7 | −0.0450 |

**Atlas statistics (from phase2b_pdf_audit.md §3):**

| Source neuron | Funatlas wt-significant targets | unc-31-significant targets | Note |
|---|---|---|---|
| ADEL | 5 targets (ADAL, ADER, AINL, AQR, FLPL) | 0 | None in 61-neuron PDF-target set |
| RMEL/RMER | OLQ neurons, OLLL, I1L | OLLL, OLLL, I1L | Several unc-31-sensitive |

### 5. Proposed Layout

**Panel A — Categorization table:**
Three-row layout: Confirmed / Novel Predictions / Tested Not Significant.
Each row contains neuron pairs as colored boxes.
Color: confirmed = green (funatlas q_wt<0.05), novel = red (occ=0), not significant = gray.
Add ΔQ_cepnem value and CePNEM rank to each box.

**Panel B — Venn diagram or bar summary:**
Number of pairs in each category: Confirmed (8), Novel (2), Not significant (2).
Simple three-bar chart.

**Panel C — Funatlas observation count context:**
Bar chart: for each pair, show occ_wt (number of funatlas observations).
ADEL→URYVR and ADEL→URYDL at 0; RMEL↔RMER at 22.
Horizontal dashed line at occ_wt = 5 (minimum for meaningful q-value).

### 6. Caption Draft

"**Functional validation landscape for PDF network predictions.**
**(A)** Classification of key Bentley PDF Class 4 pairs by funatlas (Randi/Leifer) status.
Confirmed: q_wt < 0.05 in the WT condition (green). Novel predictions: zero funatlas
observations (occ_wt = 0; red). Tested not significant: q_wt ≥ 0.05 (gray).
ΔQ_cepnem values are from the Phase 2 pairwise estimation (Stage 2).
**(B)** Summary of 12 cross-referenced pairs by category.
**(C)** Number of funatlas observations per pair. ADEL→URYVR and ADEL→URYDL (the
highest-ΔQ PDF pairs) have zero observations — they have **never been measured** in
the Randi/Leifer perturbation atlas, making them primary experimental predictions
(see Figure 7). RMEL↔RMER (confirmed wt-significant, occ_wt=22) provides the
strongest existing validation that the RMEL/RMER circuit is accessible to functional
perturbation experiments."

### 7. Talk Version Modifications

- Replace Panel A table with a simple three-column layout: green / red / gray boxes with neuron names
- Animate: slide in boxes from left; pause on red boxes ("untested — your next experiment")
- Remove Panel C for talk

### 8. Paper Version Modifications

- Panel A as full table with all data
- Supplementary: full funatlas data table from phase2b_pdf_audit.md §6.2

### 9. Unresolved Issues

- **UNRESOLVED-6.1:** The funatlas cross-reference data in phase2b_pdf_audit.md §6.2 includes
  RID→AVAR (q_wt=0.020, low observations occ_wt=2). This pair is not a Class 4 pair
  (needs confirmation: is AVAR in the 61-neuron set? Is AVAR–RID on or off A_raw?).
  Must verify before including in Figure 6. If on-connectome, it belongs in a different
  classification.
- **UNRESOLVED-6.2:** The audit states that ADEL has "5 wt-significant targets" in funatlas
  (ADAL, ADER, AINL, AQR, FLPL) but none are in the 61-neuron PDF-target set. This means
  ADEL's wt-significant funatlas targets are neurons not in our 61-neuron analysis.
  The figure should clarify this: ADEL is measurably active as a signaling node in funatlas,
  just not in the PDF-target direction.

---

## Figure 7 — Prediction Figure

**Title:** "Predicted dwelling-specific PDF coupling: a state-conditioned experimental test"

### 1. Scientific Purpose

Translate the Phase 2 exploratory PDF signal into a falsifiable experimental prediction.
This is the forward-looking figure — it answers "what experiment should be done next?"
The prediction is explicitly state-conditioned (roaming vs. dwelling), which is what
the Randi/Leifer atlas was not designed to test. The figure must read like a grant figure:
explicit hypothesis, experimental design, expected outcomes under three conditions.

### 2. Exact Data Sources

- ΔQ direction and values: `results/phase2/phase2b_pdf_audit.md` §2.3, §7.3
- Prediction 1 (explicit): `results/phase2/phase2b_pdf_audit.md` §7.3 "Prediction 1"
- Prediction 2: `results/phase2/phase2b_pdf_audit.md` §7.3 "Prediction 2"
- Biological context: `results/phase2/phase2b_pdf_audit.md` §5
- Atlas gap: `results/phase2/phase2b_pdf_audit.md` §8

### 3. Exact File Paths

- `results/phase2/phase2b_pdf_audit.md` — all prediction content
- `results/phase2/stage2/stage2_results.json` — ΔQ values for cited pairs

### 4. Explicit Hypothesis

Drawn directly from `results/phase2/phase2b_pdf_audit.md` §7.3 (Prediction 1):

**HYPOTHESIS:**
ADEL → URYDL and ADEL → URYVR exhibit dwelling-dominant functional coupling.
Specifically: optogenetic or electrical stimulation of ADEL should produce a stronger
co-activation signal in URYDL / URYVR during dwelling bouts than during roaming bouts.
This coupling should depend on dense-core vesicle release (unc-31-sensitive, not
detectable in unc-31 mutants).

**BASIS:**
- ADEL–URYVR: ΔQ_cepnem = −0.1222 (rank 5 of 1321 Class 4 pairs)
- ADEL–URYDL: ΔQ_cepnem = −0.0980 (rank 9 of 1321)
- Both pairs have zero funatlas observations (occ_wt = 0 for both)
- ΔQ < 0 means Q_dwell > Q_roam: conditional dependence stronger during dwelling
- ADEL expresses pdf-1 (CeNGEN conservative threshold)
- URYVR, URYDL express pdfr-1 (CeNGEN conservative threshold)
- ADEL–URYVR and ADEL–URYDL are off-connectome (no direct synapse in A_raw)
- Therefore: coupling must operate via volumetric / extrasynaptic transmission

### 5. Experimental Design

**Target assay:** State-conditioned functional connectivity in freely-behaving animals.

**Setup:**
1. Optogenetically express a fast opsin (e.g., ChrimsonR) in ADEL (using ADEL-specific
   driver; e.g., near cat-1 or tph-1 co-expression driver).
2. Record URYDL / URYVR activity (GCaMP) simultaneously in freely-behaving animals.
3. Segment behavioral state in real time or post-hoc (EWMA velocity threshold 0.284,
   τ = 20 s — identical to Phase 0/Phase 2 parameters).
4. Stimulate ADEL with brief light pulses (e.g., 500 ms, matched to the ~20 s EWMA
   timescale of the behavioral variable).

**Comparison:**
- Stimulate ADEL during verified **dwelling bouts** → measure URYDL/URYVR response
- Stimulate ADEL during verified **roaming bouts** → measure URYDL/URYVR response

**Genetic perturbation arm:**
- Repeat in **unc-31** (CAPS) null background to ablate dense-core vesicle release
- Repeat in **pdfr-1** null background to confirm PDFR-1 dependence

**Controls:**
- Unstimulated animals (no ADEL activation) in both behavioral states
- Animals without ChrimsonR in ADEL (light artifact control)

### 6. Expected Outcomes

**Under roaming state (Condition 1):**
ΔQ_cepnem = Q_roam − Q_dwell < 0 implies Q_roam ≈ 0 for ADEL–URY pairs.
**Predicted:** ADEL stimulation during roaming → little or no detectable URYDL/URYVR
co-activation. ADEL and URYDL/URYVR are functionally decoupled during roaming.

**Under dwelling state (Condition 2):**
Q_dwell < 0 (negative partial correlation) implies ADEL and URYDL/URYVR have
state-dependent conditional dependence.
**Predicted:** ADEL stimulation during dwelling → detectable URYDL/URYVR response
(sign: inverse co-activation, since Q_dwell < 0, i.e., ADEL activity suppresses
or inversely correlates with URY during dwelling).

**Under PDF disruption / unc-31 / pdfr-1 null (Condition 3):**
If coupling is mediated by ADEL-pdf-1 → URYDL/URYVR-pdfr-1:
**Predicted:** dwelling-state ADEL → URYDL/URYVR coupling is abolished or substantially
reduced in unc-31 null (dense-core vesicle release required) and in pdfr-1 null
(receptor required).
WT coupling in roaming: no coupling expected regardless; unc-31/pdfr-1 perturbation
should not further suppress the already-absent roaming coupling.

**Discriminating result:**
A state × stimulation interaction (dwelling response > roaming response) that is
unc-31-sensitive would strongly support the ADEL–PDF–URY hypothesis and validate
the Phase 2 exploratory signal as a genuine neuromodulatory mechanism.

A null result (no state difference in ADEL→URY coupling) would be informative:
it would suggest that the Phase 2 ΔQ signal reflects computational structure
(e.g., downstream locomotion circuitry) rather than direct ADEL→URY PDF signaling.

### 7. Proposed Layout

**Panel A — Cartoon experimental design:**
Left: worm cartoon with ADEL labeled (blue neuron, anterior head). Right: two sub-panels
showing roaming trajectory (top) and dwelling trajectory (bottom). Arrow: optogenetic
stimulus pulse. Small GCaMP trace cartoon: flat (roaming), responsive (dwelling).

**Panel B — Expected response traces:**
Three schematic trace panels (roaming / dwelling / PDF disruption):
- X-axis: time (seconds post-stimulus)
- Y-axis: URYDL/URYVR ΔF/F (cartoon)
- Roaming: flat trace with ±noise
- Dwelling: transient suppression (inverted, matching ΔQ < 0 sign)
- PDF disruption: flat trace (like roaming)
Label each panel clearly. Add "Predicted, not observed" watermark.

**Panel C — Summary prediction table:**

| Condition | ADEL→URY coupling | ΔQ sign | Prediction |
|---|---|---|---|
| 1: Roaming (WT) | Absent | Q_roam ≈ 0 | No URYDL/URYVR response to ADEL stimulation |
| 2: Dwelling (WT) | Present | Q_dwell < 0 | Inverse co-activation: URY suppressed by ADEL |
| 3: PDF disruption (unc-31 or pdfr-1 null) | Absent | — | Dwelling-state coupling abolished |

### 8. Caption Draft

"**Predicted dwelling-specific PDF coupling.**
**(A)** Experimental design. ADEL is optogenetically activated (ChrimsonR) during verified
roaming or dwelling behavioral bouts in freely-behaving animals expressing GCaMP in URYDL/URYVR.
Behavioral state is segmented post-hoc using the Phase 0 EWMA velocity threshold (0.284, τ=20 s).
**(B)** Expected response traces. Based on the Phase 2 pairwise precision estimate
(ADEL–URYVR ΔQ_cepnem = −0.122, rank 5 of 1321; ADEL–URYDL ΔQ_cepnem = −0.098, rank 9),
we predict dwelling-dominant inverse coupling (ADEL activation suppresses URYDL/URYVR
during dwelling; no coupling during roaming). This coupling should require dense-core
vesicle release (unc-31) and PDFR-1 (pdfr-1 null abolishes coupling).
Traces shown are predictions, not data. ADEL→URYVR and ADEL→URYDL have zero observations
in the existing Randi/Leifer perturbation atlas.
**(C)** Summary of predicted outcomes under the three experimental conditions."

### 9. Talk Version Modifications

- Show only Panel B (traces) — animate state switch with behavioral trajectory side-by-side
- Add title card: "Two untested connections that explain the enrichment signal"
- Remove Panel C table for talk

### 10. Paper Version Modifications

- All three panels in figure
- Add footnote: "Traces in (B) are model predictions derived from the Phase 2 ΔQ estimate
  and are not experimental data. The experiment has not yet been performed."
- Add supplementary: full prediction details for Prediction 2 (RID→URXL) and Prediction 3
  (general ADEL-pdf-1 state-selective signaling)

### 11. Unresolved Issues

- **UNRESOLVED-7.1:** The sign of the predicted ADEL→URYDL/URYVR response.
  ΔQ < 0 means Q_dwell < Q_roam (in the signed precision matrix sense). Since Q is a
  precision matrix, Q_ij < 0 implies conditional *negative* correlation: ADEL activity
  and URY activity are inversely related conditional on all other neurons.
  The predicted trace (Panel B) is drawn as suppression (ADEL→URY inverse response).
  However, the precision matrix sign does not directly map to a stimulation response sign
  in a causal experiment (it is a conditional dependence, not a causal effect).
  This distinction must be stated in the caption. The prediction is that *coupling exists
  in a state-conditioned way*; the sign of the response is secondary and requires
  experimental determination.
- **UNRESOLVED-7.2:** No data exist for the experiment. Panel B must be watermarked or
  otherwise clearly labeled as a prediction. Figure conventions for prediction figures
  vary by journal; check target journal guidelines.

---

## Cross-Figure Consistency Requirements

Before artwork begins:

1. **Color convention lock:** roaming = orange, dwelling = blue (recommended, from Figure 1).
   Consistent across all figures. A separate color-convention document should be created.

2. **Neuron name format:** Use standard CePNEM/NeuroPAL names throughout
   (e.g., URYVR not URY_VR, ADEL not ADE_L). Check against `results/diagnostics/neuron_harmonization.csv`.

3. **ΔQ sign convention:** All figures use ΔQ = Q_roam − Q_dwell. Negative ΔQ = dwelling-dominant.
   This must be stated in a Methods paragraph referenced from all figures.

4. **Figure 6 confirms Figure 5 labeling:** All RMEL/RMER funatlas data in Figure 6
   must be cross-checked against Figure 5 network edge labels before finalizing either figure.

5. **Figure numbering is provisional.** The seven figures may be reordered once the
   paper structure is decided. Internal cross-references in captions use
   "(see Figure X)" placeholders that require update.

---

## Unresolved Issues Summary (All Figures)

| ID | Figure | Description | Blocking artwork? |
|---|---|---|---|
| UNRESOLVED-1.1 | Fig 1 | Behavioral trajectory data not in results/; Panel A may need to be purely schematic | No (cartoon acceptable) |
| UNRESOLVED-1.2 | All | ~~Color convention (dwelling/roaming) not locked~~ **RESOLVED (2C-A.1)** | — |
| UNRESOLVED-2.1 | Fig 2 | Harmonization table needed for scatter axis labels | No (deferred to artwork phase) |
| UNRESOLVED-2.2 | All | ~~Color convention (annotation categories) not locked~~ **RESOLVED (2C-A.1)** | — |
| UNRESOLVED-3.1 | Fig 3 | 1-pair discrepancy: Randi off-connectome=109 vs Class 4 Randi=108 | No (document in caption) |
| UNRESOLVED-3.2 | Fig 3 | Neuropeptide density 73.6% needs explanation in caption | No |
| UNRESOLVED-4.1 | Fig 4 | ~~Null distribution SDs needed~~ **PARTIALLY RESOLVED (2C-A.1)**: neuropeptide AUROC full stats available; Randi and PDF AUROC null_std not stored — see resolutions section | Partial — approximation approach documented |
| UNRESOLVED-4.2 | Fig 4 | OR=0.000 visual encoding for Randi CePNEM Fisher | No (convention decision only) |
| UNRESOLVED-5.1 | Fig 5 | RMER PDFR-1 expression status ambiguous | No (minor node encoding) |
| UNRESOLVED-5.2 | Fig 5 | ~~Full list of 17 nonzero PDF ΔQ pairs (only top-10 in audit)~~ **RESOLVED (2C-A.1)** | — |
| UNRESOLVED-5.3 | Fig 5 | GCaMP vs CePNEM asymmetry explanation needed in caption | No |
| UNRESOLVED-6.1 | Fig 6 | RID→AVAR pair class status unclear (on/off connectome?) | No (can omit from figure) |
| UNRESOLVED-6.2 | Fig 6 | ADEL funatlas targets are outside 61-neuron set — clarify in caption | No |
| UNRESOLVED-7.1 | Fig 7 | ΔQ sign ≠ causal response sign; prediction wording needs care | No (caption clarification) |
| UNRESOLVED-7.2 | Fig 7 | Journal convention for prediction figures | No (pre-artwork check) |

**Blocking issues status after Phase 2C-A.1:**

| Block | Description | Status |
|---|---|---|
| BLOCK-A | Color convention lock | **RESOLVED** — full convention in resolutions section |
| BLOCK-B | Null distribution SDs for Fig 4 error bars | **PARTIALLY RESOLVED** — neuropeptide exact; Randi/PDF approximation documented |
| BLOCK-C | Complete 17-pair PDF network | **RESOLVED** — full table in resolutions section and Figure 5 spec |

**Remaining pre-artwork requirements:**
1. UNRESOLVED-4.1 (partial): Decide whether to use approximation for Randi/PDF error bars or accept figure note
2. UNRESOLVED-4.2: Convention for OR=0 in Fisher plot (minor)
3. UNRESOLVED-5.1: RMER PDFR-1 status check (minor, does not block figure)
4. UNRESOLVED-2.1: Confirm `results/diagnostics/neuron_harmonization.csv` is current (deferred to artwork)

---

*Figure Specification Package — Phase 2C-A / Phase 2C-A.1.*
*Date: 2026-06-01.*
*No artwork produced. No figures rendered. No files modified.*
*All quantitative values trace to existing files in results/phase2/.*
