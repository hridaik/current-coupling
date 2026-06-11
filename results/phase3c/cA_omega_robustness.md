# Phase 3C-A — Ω Robustness to D
Date: 2026-06-03
Authorization: Phase 3C

## Identity and Setup

Q = D^{-1}(Ω − A)  →  Ω = D Q + A

For diagonal D (per-neuron noise variance):
  Ω_ij = D_ii · Q_ij + A_ij   (row-scaling of Q, plus anatomy)
  ΔΩ_ij = Ω_roam_ij − Ω_dwell_ij = D_ii · ΔQ_ij   (A cancels in the difference)

## D Models

| Model | Description | Range | Mean |
|---|---|---|---|
| D1 | Identity: D_ii = 1.0 | [1.0, 1.0] | 1.000 |
| D2 | CePNEM residual variance: D_ii = Var(x_i) pooled | [0.943, 1.096] | 1.025 |
| D3 | First-difference innovation variance: D_ii = Var(Δx_i) | [0.316, 0.483] | 0.405 |
| Creamer | Same D1 and D2 but A = Creamer A_C dynamics matrix | — | — |

D2 is nearly uniform (std = 0.031, range 0.943–1.096) because CePNEM residuals are
z-scored globally before estimation. The z-scoring makes per-neuron variance approximately
equal across neurons.

D3 (first-difference variance) is systematically lower than D2 (~40% of D2), reflecting
the temporal autocorrelation in CePNEM residuals (Δx is smaller than x when signal is
autocorrelated).

## Robustness Results

### Rank correlation across D models

All pairwise Spearman rank correlations of |ΔΩ| across Class 4 pairs:

| Comparison | ρ |
|---|---|
| D1 vs D2 | **1.0000** |
| D1 vs D3 | **0.9999** |
| D2 vs D3 | **0.9999** |
| D1 vs D1_Creamer | 1.0000 |
| D1 vs D2_Creamer | 1.0000 |

The |ΔΩ| ranking is **essentially identical across all D choices** (ρ > 0.999 for all
comparisons). This is a direct consequence of D2 being nearly uniform (D2/D1 varies
only ±10%) and D3 being a constant fraction of D2 (~0.40 for most neurons). A constant
rescaling does not change rankings.

### Top-20 overlap across D models

- D1 vs D2 top-20: 19/20 pairs in common
- D1 vs D3 top-20: 20/20 pairs in common
- **Robust top-20 (all three D_Araw variants)**: 19 pairs

The one pair difference between D1 and D2 top-20 is a rank-borderline case.

### Robust top-20 Class 4 pairs (present in all D choices)

19 of 20 top pairs are robust:

| Pair | ΔΩ (D1) | ΔΩ (D2) | ΔΩ (D3) | PDF? |
|---|---|---|---|---|
| IL1DR–URYVR | −0.2541 | −0.2754 | −0.0884 | — |
| AVER–I1L | −0.2160 | −0.2154 | −0.0838 | — |
| AVJR–OLLR | −0.1697 | −0.1790 | −0.0698 | — |
| AVJR–OLQVR | −0.1614 | −0.1702 | −0.0664 | — |
| **ADEL–URYVR** | **−0.1222** | **−0.1253** | **−0.0539** | **YES** |
| AIZL–AVJL | −0.1089 | −0.1139 | −0.0507 | — |
| AVER–AWAL | −0.1094 | −0.1091 | −0.0424 | — |
| OLLR–RICL | −0.0985 | −0.1050 | −0.0391 | — |
| **ADEL–URYDL** | **−0.0980** | **−0.1006** | **−0.0432** | **YES** |
| **ADEL–RMEL** | **−0.0957** | **−0.0982** | **−0.0422** | **YES** |
| I1L–IL2DR | +0.0903 | +0.0916 | +0.0354 | — |
| CEPDR–IL2VL | −0.0891 | −0.0910 | −0.0359 | — |
| CEPDR–IL2VR | −0.0863 | −0.0881 | −0.0348 | — |
| I2R–IL2DR | −0.0857 | −0.0881 | −0.0304 | — |
| OLLL–SMDVL | −0.0881 | −0.0853 | −0.0329 | — |
| **RMEL–URYDL** | **−0.0754** | **−0.0801** | **−0.0291** | **YES** |
| AVJR–URYDL | −0.0736 | −0.0776 | −0.0303 | — |
| AVER–NSMR | −0.0750 | −0.0747 | −0.0291 | — |
| ASGL–RMDVL | −0.0745 | −0.0738 | −0.0296 | — |

**4 of 19 robust top-20 pairs are PDF-annotated** (ADEL–URYVR, ADEL–URYDL,
ADEL–RMEL, RMEL–URYDL). The ADEL-centric PDF signal is robust to D choice.

### Effect of A choice (A_raw vs Creamer A_C)

A affects Ω_s (absolute values) but NOT ΔΩ (since A_raw cancels in the difference):
- ΔΩ = D ΔQ regardless of A
- The A choice changes Ω_s = D Q_s + A but not ΔΩ = D ΔQ

Therefore: all Spearman ρ comparisons involving different A (D1_Acreamer, D2_Acreamer)
give ρ = 1.0000 — identical ranking to A_raw results. The A choice is irrelevant for
the state-difference analysis.

## Key Conclusion

**The Ω framework, for the state-difference ΔΩ = D ΔQ, contains no additional
information beyond ΔQ when D is nearly uniform** (as for z-scored CePNEM residuals).
All D choices produce effectively the same ranking of Class 4 pairs.

The robustness confirmation serves as a validity check: the Phase 2 ΔQ results are
stable regardless of reasonable noise-model assumptions, which supports their
reliability as a characterization of state-dependent functional organization.

---
*3C-A scope: Ω robustness characterization. No hypothesis testing. No new fitting.*
