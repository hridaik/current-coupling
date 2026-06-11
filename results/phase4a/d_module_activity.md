# Phase 4A-D — Module-Level Activity
Date: 2026-06-04
Authorization: Phase 4A

## Module Definitions

- **DA_mech (ADEL)**: ADEL as the sole target neuron from the dopaminergic
  mechanosensory module (CEP neurons not analyzed here due to off-target noise).
- **URY_URX**: Mean of URYVR, URYDL, URXL.

---

## ADEL vs URY_URX Module Correlation

### By State

| State | Mean Pearson r | Std | n recordings |
|---|---|---|---|
| Overall | **+0.176** | ±0.167 | 22 |
| Dwelling | **+0.155** | ±0.167 | 22 |
| Roaming | **+0.157** | ±0.223 | 21 |
| t-test (roam vs dwell) | — | — | p = 0.975 |

The correlation between ADEL and the mean URY_URX module activity is **positive
in both states** (~0.16) and shows **no significant state-dependent change**
(p = 0.975).

---

## Findings

### 1. ADEL and URY_URX are weakly positively correlated in both states

A mean Pearson r of 0.176 indicates that ADEL and the URY/URX module co-vary
positively on average. However:
- The correlation is highly variable across recordings (std = 0.167)
- In some recordings r > 0.4, in others r ≈ 0 or negative
- No recording systematically inverts the relationship

### 2. Module coordination is NOT state-dependent (p = 0.975)

The gross module correlation (ADEL × mean URY_URX) does not differ between
roaming and dwelling. This is consistent with:
- The Phase 2 ΔQ result being a CONDITIONAL (multi-neuron) effect, not visible
  in pairwise marginal correlations
- The state-dependent Q signal arising from a multi-neuron coordination structure
  that averages away when projecting to module-level correlations

### 3. Comparison with Phase 2 ΔQ

Phase 2 found ΔQ_ADEL-URYVR = −0.122 (rank 5), meaning Q_dwell > Q_roam — tighter
conditional coupling during dwelling. But the marginal module correlation is the same
in both states. This is not a contradiction: the graphical lasso precision Q controls
for all other pairwise relationships. The dwelling state may have a tighter ADEL–URY
functional link even if the marginal correlation is similar, because shared variance
from other sources (locomotor drive, global brain state) is conditioned out.

---

## Answers to Analysis D Questions

**1. Do module trajectories become coordinated?**

Weakly and non-specifically. The correlation is positive (~0.16) in both states,
indicating the modules co-vary together but not strongly. There is no sharp state-
dependent onset of coordination.

**2. Is coordination state-dependent?**

**No** at the gross module level (p = 0.975). Any state-dependent coordination in
the ADEL–URY axis is not captured by a simple linear correlation between module
mean activity traces. It may only be visible in the conditional structure (ΔQ).

---

*D scope: module coordination characterization only. Figure: FigA4_module_coordination.pdf*
