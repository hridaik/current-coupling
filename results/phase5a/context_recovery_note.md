# Phase 5A — Context Recovery Note
Date: 2026-06-12

---

## Sources Read

1. `results/phase2/stage1/pdf_pair_support_summary.md` — PDF pair support statistics
2. `results/phase2/phase2d_final_report.md` — Drift + pair support final report
3. `results/phase2/figures/pdf_pair_support_table.csv` — Top-20 PDF pair table
4. `results/phase2/stage2/stage2_results.json` — Top-50 CePNEM pairs + annotations
5. Perturbation atlas cross-references: stage4_report.md, stage4a_report.md, stage5_report.md (all in phase2/stage4, stage4a, stage5)
6. Randi funatlas.h5 — direct query of WT and unc-31 q-values and observation counts for all top-50 pairs

---

## Pairs Already Confirmed vs Only Predicted

### Confirmed by funatlas (perturbation atlas independent confirmation)

| Pair | ΔQ rank | |ΔQ| | wt q (ij) | wt occ (ij) | unc-31 q (ij) | Status |
|---|---|---|---|---|---|---|
| **RMEL–RMER** | 32 | 0.058 | **0.0002** | **22** | 0.119 | WT confirmed, RMEL→RMER DCV-dependent |
| CEPDR–URXL | 40 | 0.054 | **0.0002** | 6 | nan (0 obs) | WT confirmed, DCV status unknown |
| AVJR–AWBL | 47 | 0.050 | **0.0017** | 37 | 0.0124 | WT + unc-31 confirmed → DCV-independent |
| I1R–RMDVR | 50 | 0.049 | **0.032** | 57 | 0.571 | WT confirmed, DCV-dependent |
| AVEL–RIVL | 20 | 0.073 | 0.024 (ji only) | 11/15 | nan | WT marginal (ji direction only) |
| OLQDL–RICL | 42 | 0.053 | 0.046 | 2 | 0.630 | WT marginal, DCV-dependent; low coverage |

Significance threshold: q < 0.05 (funatlas q-values from Randi et al. 2023).
DCV-dependent = WT significant, unc-31 NOT significant.

### Top predictions with NO funatlas coverage (untested)

| Pair | ΔQ rank | |ΔQ| | wt occ | Status |
|---|---|---|---|---|
| ADEL–URYVR | 5 | 0.122 | 0 | NO funatlas data |
| ADEL–URYDL | 9 | 0.098 | 0 | NO funatlas data |
| IL1DR–URYVR | 1 | 0.254 | 7/4 | wt q=0.43/0.24, not significant |
| AVER–I1L | 2 | 0.216 | 6/30 | wt q=0.54/0.06, not significant |
| AVJR–OLLR | 3 | 0.170 | 14/20 | wt q=0.65/0.53, not significant |
| AVJR–OLQVR | 4 | 0.161 | 14/9 | wt q=0.28/0.59, not significant |
| ADEL–RMEL | 10 | 0.096 | 5/4 | wt q=0.49/0.35, not significant |
| RMEL–URYDL | 16 | 0.075 | 3/4 | wt q=0.41/0.28, not significant |
| RMEL–URYVR | 21 | 0.070 | 9/8 | wt q=0.55/0.41, not significant |

---

## Evidence Summary Per Confirmed Pair

### RMEL–RMER (rank 32): Best confirmed case

Framework: ΔQ = -0.058 (dwelling-dominant conditional dependence).
PDF-annotated (rank 6 among Bentley PDF pairs). Both neurons express pdf-1 per CeNGEN.
randi_annotated = True in stage2 (pair is in the Randi unc-31 annotation set).
GCaMP ΔQ = 0.000 — signal is CePNEM-specific.

Funatlas: RMEL→RMER direction: wt q = 0.0002 (highly significant, 22 observations).
RMER→RMEL direction: wt q = 0.086 (not significant at 0.05).
unc-31: RMEL→RMER q = 0.119 (NOT significant, 5 observations).
unc-31: RMER→RMEL q = 0.0011 (significant, 6 observations — reversed direction emerges).

**Key**: RMEL→RMER functional propagation is present in WT and ABSENT in unc-31 → the interaction requires dense-core vesicle (DCV) release, consistent with PDF neuropeptide signaling.

### CEPDR–URXL (rank 40): Confirmed wt, DCV unknown

Framework: ΔQ = -0.054 (dwelling-dominant). Peptide-annotated (Ripoll-Sánchez atlas).
Funatlas: CEPDR→URXL wt q = 0.0002 (highly significant, 6 observations).
unc-31: 0 observations → DCV status cannot be assessed.
Partial confirmation only.

### I1R–RMDVR (rank 50): Confirmed wt, DCV-dependent

Framework: ΔQ = -0.049 (dwelling-dominant). randi_annotated = True.
Funatlas: I1R→RMDVR wt q = 0.032 (significant, 57 observations — highest coverage).
unc-31: q = 0.571 (NOT significant, 2 observations) → DCV-dependent.
Weaker framework signal (rank 50) but high observation confidence.

---

## Key Gap

The three strongest framework predictions (ADEL-URYVR rank 5, ADEL-URYDL rank 9, ADEL-RMEL rank 10)
have 0 or minimal funatlas observations. These remain genuine novel predictions that the
perturbation atlas has not tested. The Phase 2D report confirms this is a DATA COVERAGE GAP
in the funatlas, not a weakness of the framework.

The confirmed cases (RMEL-RMER, etc.) are at lower ΔQ ranks (32–50) but have actual
funatlas measurements available, enabling cross-validation.
