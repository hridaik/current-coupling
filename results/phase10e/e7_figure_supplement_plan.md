# Phase 10E.7 — Figure and Supplement Recommendations
Date: 2026-06-15

---

## Classification System

- **A. Main figure**: Core finding; non-redundant with main text description
- **B. Extended data figure**: Important detail; too much for main but needed for full picture
- **C. Supplementary table**: Data tables; searchable reference
- **D. Supplementary methods only**: Procedural detail not requiring visual presentation

---

## Item-by-Item Recommendations

---

### 1. Key-Pair Robustness Summary Table

**Recommendation: A — Main figure (as panel in robustness figure) OR C — Supplementary Table**

Content: Rows = key pairs + module; Columns = 10A (ΔΩ^B rank), 10B (GCaMP+GL rank, co-obs p), 10C (D=I rank, hub null p, timescale), 10D (K=5 count, off-ref status), Grade.

**If space in main figure**: A 5-pair × 5-test color-coded grade matrix (A/B/C/D) would communicate the synthesis at a glance.

**If supplement**: Supplementary Table 1 with full numeric detail from e2.

---

### 2. Top-K Enrichment Curve (PDF and Serotonin)

**Recommendation: A — Main figure (small panel)**

Content: Line plot of OR (or count/expected) vs K for Bentley_PDF (filled line) and Bentley_serotonin (dashed line, flat at 0). Show K=5,10,20,30,50,100. Mark K=20 as primary.

This panel communicates the robustness of PDF enrichment to K-choice AND the serotonin negative control in a single image.

**Key elements to include**:
- OR on y-axis vs K on x-axis (log scale for OR recommended)
- Horizontal dashed line at OR=1
- Star at K=20 (pre-specified) and at K=30,40,50 (BH-significant)
- Serotonin clearly labelled as "0 pairs at all K"

---

### 3. Diffusion Specification Comparison (5-panel or table figure)

**Recommendation: B — Extended data figure**

Content: Table figure showing ADEL-URYVR rank, ADEL-URYDL rank, RMEL-RMER rank, PDF/20 count across 5 diffusion specs (D=I, pooled diag, state diag, pooled full, state full). Columns = specs; rows = pairs.

**Highlight**: D=I column shows signal is present WITHOUT diffusion weighting.

---

### 4. Diffusion Hub Control

**Recommendation: B — Extended data figure (combined panel)**

Content:
- Panel 1: Global scatter of hub score vs |ΔΩ_ss| for all 1321 C4 pairs (ρ<0.04)
- Panel 2: Hub-matched null distribution for ADEL-URYVR (histogram, vertical line at observed)

Demonstrates both global (no hub confound) and local (ADEL-URYVR extreme within hub stratum) controls.

---

### 5. Co-Observation Null Distribution

**Recommendation: B — Extended data figure**

Content: Matched-pair null histogram for ADEL-URYVR and ADEL-URYDL showing their
|ΔΩ_ss| values vs the distribution of matched pairs (n_coobs ±5). Vertical lines at
pair values. Labelled p-values.

This is the PRIMARY specificity test and warrants its own visual.

---

### 6. Reference Sensitivity Table

**Recommendation: C — Supplementary Table**

Content: Table from D3 — 10 reference definitions × 5 key pairs, on/off-reference status, N_C4. Include raw synapse counts for each pair in a sub-table.

No figure needed; tabular format sufficient.

---

### 7. Claim Hierarchy Schematic

**Recommendation: B — Extended data figure (optional) OR D — Methods only**

Content: Visual grade hierarchy: primary claims (A) → secondary (B) → supplementary (C) with brief supporting statistics.

This could be presented as a summary "evidence panel" at the end of the robustness section, but may be redundant if a robustness table is already included. Optional.

---

### 8. Robustness Table (Full Comprehensive)

**Recommendation: B — Extended data figure (as formatted table figure)**

Content: The full table from e2 (15 rows × 9 columns). Too large for main text but critical for reviewer scrutiny. A table-figure format (like a heat-map table with grades A/B/C/D color-coded) would work well.

---

### 9. Timescale Sensitivity (τ = 1–20) Table

**Recommendation: C — Supplementary Table (rows) OR B — Extended data panel**

Content: Table of ranks for each pair at τ=1,2,5,10,20 (from Phase 10C C5 and Phase 4C). Sign stability row.

If space allows: a line plot of rank vs τ for ADEL-URYVR and ADEL-URYDL in the same extended data figure as the diffusion spec comparison.

---

### 10. Residualization Comparison Table (5 variants)

**Recommendation: C — Supplementary Table**

Content: B1 table from Phase 10B: 5 variants × 5 pairs. Highlight which rows are "primary" vs "conservative lower bound."

---

### 11. RMEL-RMER Confirmation Panel (Phase 5A)

**Recommendation: A — Main figure (panel in framework validation figure)**

Content:
- Funatlas bar or scatter: wt q=0.0002 (RMEL→RMER, n=22 obs) vs unc-31 q=0.119 (n=5 obs)
- Framework rank: ΔQ rank 32, ΔΩ_ss rank 38 (of 1321 off-reference pairs)
- PDF annotation indicator
- Explicit label: "Biologically confirmed case" NOT "ranking validation"

This is the only biologically validated case and deserves prominent display.

---

## Summary Table

| Item | Recommended Placement |
|------|----------------------|
| Key-pair grade matrix (5×5) | A — Main or C — Supp Table |
| Top-K enrichment curve (PDF vs serotonin) | A — Main figure panel |
| Diffusion specification comparison | B — Extended data |
| Diffusion hub control (global + matched) | B — Extended data |
| Co-observation null distributions | B — Extended data |
| Reference sensitivity table | C — Supplementary Table |
| Claim hierarchy schematic | D — Methods only (optional B) |
| Full robustness table (15 rows) | B — Extended data |
| Timescale sensitivity (ranks vs τ) | C — Supplementary Table |
| Residualization variant table | C — Supplementary Table |
| RMEL-RMER confirmation panel | A — Main figure |

---

## Suggested Main Figure Structure (Robustness Figure)

Panel A: Top-K enrichment curve (PDF vs serotonin, K=5–100)
Panel B: Key-pair grade matrix (5 pairs × 5 robustness domains, color-coded A/B/C)
Panel C: RMEL-RMER funatlas confirmation (wt vs unc-31)
Panel D: Co-observation null for ADEL-URYVR (histogram with p=0.001 line)

Extended data: Diffusion specification + hub control + timescale sensitivity
Supplementary tables: Full robustness table, reference sensitivity, residualization variants
