# Phase 5A.5 — Figure Concept: RMEL–RMER Confirmation
Date: 2026-06-12

---

## Concept: Three-Panel Convergence Figure

**Title:** State-dependent conditional coupling predicts DCV-mediated functional interaction

The figure communicates: prediction → independent confirmation → mechanistic link.
One column per evidence source; three rows encode the same pair.

---

## Panel Layout (landscape, 3 columns × 1 row)

```
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│  PANEL A: Framework     │  PANEL B: Funatlas WT   │  PANEL C: Funatlas      │
│  Prediction             │  Confirmation           │  unc-31 (DCV blocked)   │
│                         │                         │                         │
│  ΔQ ranking:            │  Optogenetic stim.      │  Same stimulation in    │
│  RMEL-RMER shown as     │  of RMEL → calcium      │  unc-31 mutant:         │
│  rank 32 among 1321     │  response in RMER       │  RMEL→RMER interaction  │
│  off-connectome pairs   │  q = 0.0002             │  absent (q = 0.119)     │
│                         │  (22 observations)      │  (5 observations)       │
│  ΔQ < 0: dwelling-      │                         │                         │
│  dominant coupling      │  [schematic: RMEL→RMER  │  [same schematic, but   │
│                         │   arrow, wt condition,  │   arrow dashed/absent,  │
│  [ΔQ dot highlighted    │   q-value annotated]    │   unc-31 label]         │
│   in scatter of all     │                         │                         │
│   1321 pairs: roam vs.  │                         │                         │
│   dwell state]          │                         │                         │
│                         │                         │                         │
│  GCaMP ΔQ = 0           │  Both neurons express   │  DCV-dependent →        │
│  (raw calcium: no sig.) │  pdf-1 (RMEL) /         │  consistent with PDF    │
│  CePNEM ΔQ = −0.058     │  pdfr-1 (RMER)          │  neuropeptide release   │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

## Simplified Single-Panel Alternative

If only one panel is permitted:

```
   Framework                     Perturbation Atlas
   ─────────────────────────     ────────────────────────────────────────
   RMEL─────ΔQ─────RMER          WT:    RMEL ──(q=0.0002)──► RMER  ✓
   [off-connectome, rank 32]
   [ΔQ < 0: dwelling state]      unc31: RMEL ──(q=0.119)───► RMER  ✗
   [GCaMP ΔQ = 0]                       (DCV blocked → interaction lost)
   
   → PDF neuropeptide: RMEL (pdf-1) → RMER (pdfr-1), via DCV release during dwelling
```

The single panel shows:
- Left: The framework identifies RMEL-RMER as off-connectome with dwelling-dominant ΔQ
- Center: The funatlas confirms the RMEL→RMER interaction in WT (significant)
- Right: The unc-31 result shows the interaction requires DCVs (neuropeptide mechanism)
- Bottom: The biological interpretation — PDF signaling from pdf-1+ RMEL to pdfr-1+ RMER

---

## Data Points Needed

| Panel | Data | Source |
|---|---|---|
| A (Framework) | All 1321 Class-4 ΔQ values | `results/phase2/stage2/DQ_cepnem.npy` |
| A | RMEL-RMER highlighted (index i=53, j=54) | Same |
| A | "Dwelling-dominant" annotation (ΔQ < 0) | Signed ΔQ |
| B (WT) | q = 0.0002, n = 22 | funatlas.h5/wt |
| B | Average dFF trace (RMEL stim → RMER response) | funatlas.h5/wt/dFF |
| C (unc-31) | q = 0.119, n = 5 | funatlas.h5/unc31 |
| C | Average dFF trace (RMEL stim → RMER, unc-31) | funatlas.h5/unc31/dFF |

---

## Key Design Choices

1. **One pair only.** The figure is about a single confirmed example, not an enrichment
   result. No AUROC plots, no permutation distributions — just the mechanistic story.

2. **Three sources, three panels.** Panel A = framework, Panel B = perturbation (WT),
   Panel C = genetic control (unc-31). The three together make the causal argument.

3. **Show the raw dFF traces.** Panels B and C should show the actual average calcium
   response of RMER to RMEL stimulation in WT vs. unc-31. This makes the result concrete
   and visually compelling without requiring statistical background.

4. **CePNEM vs GCaMP contrast.** Panel A should annotate that GCaMP ΔQ = 0 (no signal
   in raw calcium). This is a key part of the added-value story: the framework recovers
   the prediction that raw calcium misses.

5. **Annotation simplicity.** Annotate RMEL as "pdf-1+" and RMER as "pdfr-1+" to give
   the mechanistic context without a separate panel. The unc-31 label can say "DCV-deficient."
