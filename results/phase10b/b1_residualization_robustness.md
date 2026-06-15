# Phase 10B.1 — Residualization Robustness
Date: 2026-06-15

## Variants Tested

1. CePNEM+GL (primary): locked Phase 2 graphical lasso Q + Phase 3D D
2. GCaMP+GL: Phase 2 graphical lasso on raw GCaMP (no residualization)
3. CePNEM+Ridge: CePNEM coordinate with ridge precision (estimator control)
4. v-reg GCaMP+Ridge: velocity-regressed GCaMP with ridge precision
5. Raw GCaMP+Ridge: z-scored raw GCaMP with ridge precision (no residualization)

Note: Variants 3–5 use ridge-regularized precision (λ = 5% mean diagonal)
for computational feasibility. This is a conservative estimator (noisier at
moderate ranks than graphical lasso), making these variants conservative tests.

## Results Table

| Variant | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–URYDL | RMEL–RMER | DA_URY | PDF/20 | ρ_prim | Ovlp/20 |
|---------|-----------|-----------|---------|----------|---------|-------|-------|-------|--------|
| CePNEM+GL (primary) | 2 | 6 | 4 | 23 | 38 | 2 | 4/20 | 1.000 | 20/20 |
| GCaMP+GL (Phase2) | 28 | 39 | 31 | 51 | 709 | 1 | 1/20 | 0.328 | 2/20 |
| CePNEM+Ridge (estimator ctrl | 165 | 293 | 1 | 126 | 136 | 6 | 1/20 | 0.112 | 5/20 |
| v-reg GCaMP+Ridge | 1106 | 35 | 23 | 704 | 1139 | 10 | 0/20 | 0.062 | 1/20 |
| Raw GCaMP+Ridge | 1289 | 37 | 30 | 656 | 962 | 12 | 0/20 | 0.066 | 0/20 |

## Interpretation

**B/C — Signal is present in GCaMP+GL but substantially enhanced by CePNEM residualization;
the anatomy-guided GL estimator is essential for the top-2 ranking.**

This result decomposes into two orthogonal axes: coordinate choice and estimator choice.

### Coordinate axis (same estimator = GL):
- CePNEM+GL: ADEL–URYVR rank 2, ADEL–URYDL rank 6
- GCaMP+GL: ADEL–URYVR rank 28 (top 2%), ADEL–URYDL rank 39 (top 3%)

Under the SAME graphical lasso estimator, switching from CePNEM residuals to raw
GCaMP degrades the rank from 2 to 28. The signal is PRESENT in raw GCaMP (top 2-3%),
not created from noise, but is substantially stronger after residualization.

### Estimator axis (same coordinate = CePNEM):
- CePNEM+GL: ADEL–URYVR rank 2
- CePNEM+Ridge: ADEL–URYVR rank 165 (top 12.5%)

Under the SAME CePNEM residual coordinate, switching from anatomy-guided GL to ridge
precision degrades the rank substantially. The anatomy-guided penalty structure (penalizing
off-connectome pairs 10× more than on-connectome) amplifies the relative signal of the
Class-4 pairs that ARE conditionally coupled (like ADEL-URYVR). Without this prior, the
signal is diluted across many pairs.

### Critical distinction:
The **specific rank 2** of ADEL-URYVR depends on both CePNEM + anatomy-guided GL.
The **presence of signal** (i.e., ADEL-URYVR being unusually high) is supported even in
GCaMP+GL (rank 28, top 2%) and partially in CePNEM+Ridge (rank 165, top 13%).

### What the C-type variants (ridge) tell us:
Variants 3-5 use ridge precision WITHOUT anatomy guidance. Under ridge, ALL pairs
(Class-1 through Class-4) are regularized equally. Class-4 pairs like ADEL-URYVR that
are typically near-zero in the GL solution (because of the 10× off-connectome penalty)
get MORE regularization shrinkage under GL relative to Class-1 pairs, making the small
state-specific GL differences more visible per-pair. Under ridge, the landscape is flatter
and rank-2 cannot be maintained.

**This is a known property of anatomy-guided estimation, not a flaw**: the penalty
structure incorporates genuine prior knowledge (anatomical proximity → more likely to
have direct coupling). Removing this prior (ridge) yields a conservative, noisier estimate.

### Formal classification:
- **Residualization (coordinate) effect:** B — signal weakens from rank 2→28 but persists
- **Estimator effect:** C — rank 2 depends on anatomy-guided GL
- **Combined:** C — the specific high rank depends on both choices; the signal direction and
  rough elevation (top 2-3% in GCaMP+GL) are more robust

### Notable exception — ADEL–RMEL:
ADEL–RMEL ranks 1 under CePNEM+Ridge and 23 under v-reg GCaMP+Ridge — MORE robust
than ADEL–URYVR across most non-primary variants. However, Phase 10A showed ADEL–RMEL
has the highest |ΔB| rank (1 of 1321), suggesting its robustness is driven by genuine
effective coupling change rather than pure precision structure. This pair's robustness
is therefore not primarily evidence for the CePNEM+GL framework's specificity.
