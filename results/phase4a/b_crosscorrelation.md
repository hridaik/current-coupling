# Phase 4A-B — State-Conditioned Cross-Correlations
Date: 2026-06-04
Authorization: Phase 4A

## Method

Cross-correlations computed within-state (dwelling and roaming epochs separately),
lags ±10 s (±50 frames at 5 Hz), normalized to correlation coefficient.
Averaged across recordings (n=21 for dwell, n=18 for roam).

---

## Peak Cross-Correlation Summary

| Pair | Dwell peak | Dwell lag | Roam peak | Roam lag | Roam/Dwell ratio |
|---|---|---|---|---|---|
| ADEL–URYVR | 0.113 | 0.0 s | 0.124 | 0.0 s | 1.10× |
| ADEL–URYDL | 0.089 | 0.0 s | 0.099 | −0.4 s | 1.11× |
| ADEL–URXL | 0.074 | 0.0 s | 0.100 | +0.2 s | 1.35× |
| **ADEL–RMEL** | **0.090** | **0.0 s** | **0.189** | **0.0 s** | **2.10×** |

---

## Key Findings

### 1. ADEL–RMEL correlation doubles during roaming

The most striking finding is ADEL–RMEL: peak cross-correlation is **0.189 during
roaming vs. 0.090 during dwelling** — a 2.1× increase. Both ADEL and RMEL are
PDF-producing neurons (both express pdf-1). Their elevated co-variation during
roaming suggests shared state-dependent modulation of the PDF ligand-producing
population during locomotion.

This is the **opposite of the ΔQ result**: ΔQ for ADEL–RMEL is negative
(Q_roam < Q_dwell), meaning the graphical-lasso conditional coupling is
STRONGER during dwelling. The higher marginal correlation during roaming is
consistent with shared external drive (both neurons increase/decrease together
when the animal is actively moving), while the stronger conditional coupling
during dwelling may reflect a more directed functional relationship once
that shared drive is removed.

### 2. ADEL–URY correlations are slightly higher during roaming

ADEL–URYVR and ADEL–URYDL show 10–11% higher peak correlation during roaming,
and ADEL–URXL shows a 35% increase. These are modest effects and within the
range expected from increased joint variance during roaming.

### 3. All correlations are near zero lag

All peak cross-correlations occur at lag ≈ 0 (±0.4 s). There is no evidence
for a systematic ADEL-leading or URY-leading relationship in the marginal
cross-correlation. Both neurons fluctuate together synchronously within each
state, not in a driver–follower pattern at the ms–second scale.

---

## Is the Relationship Stronger in Dwelling?

**No — for marginal cross-correlations, the relationship is slightly STRONGER
during roaming for all pairs.** This appears to contradict the ΔQ direction
(stronger dwelling conditional dependence for ADEL–URYVR and ADEL–URYDL).

The reconciliation: marginal correlation and conditional precision measure
different aspects. The graphical lasso ΔQ removes all pairwise shared
variance and measures residual conditional dependence. The cross-correlation
includes shared variance from all sources (behavioral drive, other neurons,
global states). The higher roaming cross-correlation likely reflects shared
locomotor/sensory drive to both ADEL and URY neurons during active movement.
The stronger dwelling conditional precision (ΔQ) reflects a more specific
ADEL–URY functional relationship that becomes apparent once shared drive
is conditioned out.

---

*B scope: cross-correlation characterization only. Figure: FigA2_crosscorrelations.pdf*
