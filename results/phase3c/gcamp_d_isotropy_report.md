# Isotropic vs Anisotropic Diffusion in CePNEM and GCaMP Coordinates
Date: 2026-06-03
Authorization: Phase 3C supplement

---

## Background

In the current organization model Q = D^{-1}(Ω − A), D is the diagonal diffusion
matrix encoding per-neuron noise variance. Phase 3C showed that CePNEM D is
near-uniform (isotropic), making ΔΩ ≈ constant × ΔQ. This report asks whether
the same holds for the raw GCaMP coordinate, using identical D-construction procedures.

---

## D2 — Residual (Total) Variance

D2_ii = pooled variance of the neural signal x_i across all recordings and states.
Source: sufficient statistics (suf_xi, suf_xii, n_frames) for each coordinate.

| Statistic | CePNEM D2 | GCaMP D2 |
|---|---|---|
| Range | [0.943, 1.096] | [0.967, 1.084] |
| Mean | 1.025 | 1.031 |
| Std | 0.031 | 0.026 |
| **CV** | **0.031** | **0.025** |

**Both D2 distributions are highly isotropic (CV < 4%).** This is a direct consequence
of global z-scoring applied to both CePNEM residuals and raw GCaMP traces during
preprocessing. GCaMP D2 is marginally *more* uniform than CePNEM D2 (CV 2.5% vs 3.1%),
likely because the GCaMP z-scoring operates on traces that are already temporally
smoothed (fluorescence signals), reducing neuron-to-neuron variance differences.

---

## D3 — Innovation (First-Difference) Variance

D3_ii = mean of (Δx_i)^2 over all time steps, pooled across recordings.
This measures high-frequency signal content (inverse of temporal autocorrelation).

| Statistic | CePNEM D3 | GCaMP D3 |
|---|---|---|
| Range | [0.316, 0.483] | [0.156, 0.323] |
| Mean | 0.405 | 0.231 |
| Std | 0.038 | 0.035 |
| **CV** | **0.093** | **0.151** |

**GCaMP D3 is substantially more anisotropic than CePNEM D3 (CV 15.1% vs 9.3%).**
Two structural differences drive this:

1. **Lower mean**: GCaMP D3 mean (0.231) ≈ 57% of CePNEM D3 mean (0.405). GCaMP
   fluorescence traces are temporally smoother than CePNEM residuals (which capture
   moment-to-moment fluctuations after model removal). Smoother signals have smaller
   first differences.

2. **Larger ratio spread**: GCaMP D3 spans 0.156–0.323 (2.06× range), while CePNEM
   D3 spans 0.316–0.483 (1.53× range). The wider GCaMP D3 spread reflects genuine
   inter-neuron differences in temporal autocorrelation structure.

### GCaMP D3 — top 10 most active neurons (largest D3, highest innovation)

| Rank | Neuron | D3 | Function |
|---|---|---|---|
| 1 | RID | 0.323 | PDF neuropeptide modulator |
| 2 | AIZL | 0.301 | Olfactory interneuron |
| 3 | URXL | 0.298 | O₂/aerotaxis sensor (pdfr-1) |
| 4 | IL2VR | 0.296 | Inner labial sensory |
| 5 | SMDVL | 0.292 | Head ring motor |
| 6 | AVAL | 0.290 | Forward/reversal command |
| 7 | AWCL | 0.287 | Olfactory sensory |
| 8 | ADEL | 0.287 | Dopaminergic mechanosensory |
| 9 | RMDVL | 0.278 | Head motor |
| 10 | URYVL | 0.273 | O₂/aerotaxis sensor (pdfr-1) |

### GCaMP D3 — top 10 least active neurons (smallest D3, most autocorrelated)

| Rank | Neuron | D3 | Function |
|---|---|---|---|
| 1 | MI | 0.156 | Pharyngeal interneuron |
| 2 | NSMR | 0.170 | Serotonergic pharyngeal modulator |
| 3 | AVAR | 0.187 | Reversal command interneuron |
| 4 | AVJR | 0.190 | Command interneuron |
| 5 | FLPL | 0.191 | Touch sensory (mechanosensory) |
| 6 | IL1L | 0.192 | Inner labial sensory |
| 7 | AIBL | 0.196 | Bistable interneuron (AIB) |
| 8 | URYVR | 0.196 | O₂/aerotaxis sensor (pdfr-1) |
| 9 | IL1R | 0.198 | Inner labial sensory |
| 10 | AVER | 0.198 | Forward command interneuron |

Note: RID (PDF source) is the most dynamically active; URYVR (PDF receptor target)
is among the least active. This is biologically coherent — a slow-integrating receptor
neuron shows high autocorrelation, while a fast-signaling neuropeptide source does not.

---

## ΔΩ vs ΔQ Rankings

ΔΩ = D · ΔQ (exact; A cancels in state difference). Rankings determined by D uniformity.

| Comparison | CePNEM | GCaMP |
|---|---|---|
| ρ(ΔΩ_D2, ΔQ) | 0.999993 | 0.999960 |
| ρ(ΔΩ_D3, ΔQ) | 0.999936 | 0.998819 |
| ρ(ΔΩ_D2, ΔΩ_D3) | 0.999934 | 0.998724 |
| Top-20 overlap (D2 vs ΔQ) | 19/20 | **20/20** |
| Pairs in top-200 ΔΩ_D2, not ΔQ | 1 | 2 |

**GCaMP D3 is the most anisotropic model tested (ρ = 0.9988 vs ΔQ).** This is
substantially lower than all CePNEM comparisons (ρ > 0.9999), but still high enough
that no meaningful reordering occurs in practice: top-20 overlap remains 20/20 for D2,
and only 2 pairs enter the top-200 under D3 that were not already there under ΔQ.

The GCaMP D3 anisotropy (CV = 15%) is larger than CePNEM D3 (9%), but the 2-pair
displacement in the top-200 is inconsequential — these pairs move from rank ~200 to ~198.

---

## PDF AUROC Comparison

| Framework | CePNEM | GCaMP |
|---|---|---|
| ΔQ | 0.5560 | 0.5260 |
| ΔΩ_D1 | 0.5560 | 0.5260 |
| ΔΩ_D2 | 0.5563 | 0.5272 |
| ΔΩ_D3 | 0.5566 | 0.5285 |

Two observations:
1. **GCaMP PDF AUROC is weaker than CePNEM** (0.526 vs 0.556): the PDF network enrichment
   signal is less pronounced in raw GCaMP than in CePNEM residuals. This is consistent
   with CePNEM capturing state-dependent neural dynamics more precisely by removing
   behavioral covariates.

2. **In both coordinates, ΔΩ_D3 gives a marginal AUROC gain** (+0.006 for CePNEM,
   +0.0025 for GCaMP). This is the only metric where D3 anisotropy translates into a
   quantitative difference — and the effect is too small to be actionable.

---

## ADEL Ranks in GCaMP vs CePNEM

The key Phase 2 predictions differ dramatically between coordinates:

| Pair | CePNEM ΔQ rank | GCaMP ΔQ rank | CePNEM ΔΩ_D2 rank | GCaMP ΔΩ_D2 rank |
|---|---|---|---|---|
| ADEL–URYVR | **5** | 84 | **5** | 81 |
| ADEL–URYDL | **9** | 86 | **9** | 85 |
| ADEL–RMEL | **10** | 90 | **10** | 89 |
| ADEL–URXL | 59 | **19** | 58 | **19** |

The ADEL→URY prediction (ranks 5, 9 in CePNEM) is at ranks 84–90 in GCaMP, indicating
the state-dependent signal in these pairs is better captured by CePNEM than by raw
GCaMP fluorescence. Notably, ADEL–URXL ranks higher in GCaMP (rank 19) than CePNEM
(rank 59), suggesting a different aspect of ADEL–aerotaxis coupling is prominent in
the two coordinates.

D choice does not change this pattern: ADEL–URYVR moves from rank 84 (ΔQ) to rank 81
(ΔΩ_D2) in GCaMP, a negligible shift of 3 positions.

---

## Summary: Isotropic vs Anisotropic

| Metric | CePNEM D2 | GCaMP D2 | CePNEM D3 | GCaMP D3 |
|---|---|---|---|---|
| CV | 0.031 | 0.025 | 0.093 | **0.151** |
| Regime | Near-isotropic | Near-isotropic | Near-isotropic | Moderately anisotropic |
| ρ(ΔΩ, ΔQ) | 0.999993 | 0.999960 | 0.999936 | **0.998819** |
| Top-20 change | 1/20 different | 0/20 different | N/A | 0/20 different |
| Conclusion | ΔΩ ≈ ΔQ | ΔΩ ≈ ΔQ | ΔΩ ≈ ΔQ | **ΔΩ ≈ ΔQ** |

**Both coordinates are effectively isotropic at the ranking level, despite GCaMP D3
being the most anisotropic D model evaluated.** The GCaMP D3 CV of 15% is the largest
non-uniformity in the dataset — neurons like RID and ADEL have ~2× higher innovation
variance than slow pharyngeal neurons like MI and NSM — but this 2× spread is
insufficient to reorder any top-20 pair or change any scientific conclusion from Phase 3C.

**The Phase 3C decision to terminate the Ω pathway holds equally for GCaMP.**

---

*Files: gcamp_d_characterization.json (full per-neuron D values and rankings)*
*Computation: scripts/phase3/phase3c_gcamp_d.py*
*No new fitting. No new hypotheses. No held-out evaluation.*
