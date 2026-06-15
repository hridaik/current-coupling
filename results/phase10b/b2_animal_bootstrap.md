# Phase 10B.2 — Animal Bootstrap
Date: 2026-06-15

Bootstrap design: 500 replicates, animals resampled with replacement (n=40).
Within-animal time structure and state labels preserved.
Precision: ridge-regularized (λ = 5% mean diagonal of Σ_s).

## Key Pair Rank Statistics

| Pair | Median Rank | 5th–95th %ile | Top-10 freq | Top-20 freq | Top-50 freq |
|------|-------------|---------------|-------------|-------------|-------------|
| ADEL–URYVR | 336 | [18–1212] | 0.02 | 0.05 | 0.12 |
| ADEL–URYDL | 450 | [24–1230] | 0.03 | 0.04 | 0.10 |
| ADEL–RMEL | 6 | [1–120] | 0.61 | 0.76 | 0.88 |
| RMEL–URYDL | 271 | [27–1139] | 0.02 | 0.04 | 0.09 |
| RMEL–RMER | 433 | [49–1216] | 0.00 | 0.02 | 0.05 |

## Module and Enrichment Statistics

DA_mech ↔ URY_URX module rank: median=6, P5–P95=[2–13]
PDF in top-20: median=1, P5–P95=[0–3]

## ADEL–URYVR Top-K Frequencies

- Top-10: 0.02 (2% of bootstrap replicates)
- Top-20: 0.05
- Top-50: 0.12

## ADEL–URYDL Top-K Frequencies

- Top-10: 0.03
- Top-20: 0.04
- Top-50: 0.10

## Interpretation

**CONSERVATIVE TEST — ridge precision approximation, not the primary GL estimator.**

This bootstrap uses ridge-regularized precision (uniform λ, no anatomy guidance) for
computational feasibility. It is therefore equivalent to a bootstrap of the "CePNEM+Ridge"
B1 variant, not of the primary CePNEM+GL pipeline.

**Under ridge precision:**
- ADEL–URYVR: median rank 336, top-20 in only 5% of replicates → UNSTABLE under ridge
- ADEL–URYDL: median rank 450, top-20 in only 4% of replicates → UNSTABLE under ridge
- ADEL–RMEL: median rank 6, top-20 in 76% of replicates → STABLE under ridge

This is consistent with B1: the CePNEM+Ridge variant gives ADEL-URYVR rank 165 (not top-20).
The anatomy-guided GL estimator (which gives rank 2) uses a 10× stiffer penalty on
off-connectome pairs, making their state-specific differences more visible. Under ridge,
this amplification is absent, and the pairs' ranks regress toward the background.

**Most informative result from this analysis:**
ADEL–RMEL is genuinely robust even under ridge (median rank 6, top-20 in 76% of replicates).
However, Phase 10A showed ADEL–RMEL has |ΔB| rank 1 of 1321, indicating its signal is partly
driven by effective coupling change rather than pure precision structure. The ADEL-RMEL
"robustness" here may reflect coupling rather than current organization.

**DA_mech ↔ URY_URX module:** median rank 6 with P5–P95 = [2–13] — moderately robust even
under ridge, though not as dominant as under GL (where it's consistently rank 1–2).
