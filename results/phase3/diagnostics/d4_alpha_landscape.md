# D4 — α Landscape
Date: 2026-06-03
Authorization: Phase 3A.5-D

## Sweep 1: α_r = 0, α_d varied across full stability range [-41.72, 0.060]

| Range | Max ρ | Best α_d | Shape |
|---|---|---|---|
| Full | 0.0390 | -4.078 | 97 points above half-max |

α_max boundary at 0.0671. α_min boundary at -43.92.

## Sweep 2: Δα varied (mean α fixed at M1 mean = -25.11)

| Δα range | Max ρ | Best Δα | Optimum boundary-seeking? |
|---|---|---|---|
| [−10, +10] | 0.0617 | -2.250 | NO (interior) |

M1 fitted Δα = +2.278.

## Sweep 3: α_r = -26.25 (M1 fitted), α_d varied

Max ρ = 0.0621 at α_d = -26.663.
Shape: 97/102 points above half-max objective.
Shape classification: BROAD PLATEAU — objective weakly sensitive to exact α_d.

## Summary

The α landscape characterizes whether:
- The optimum is sharply localized (strong signal), or
- A broad plateau (objective weakly informative), or
- Boundary-seeking (pushed against the stability limit)

Implications:
- Boundary-seeking: model at edge of stability → potentially pathological fit
- Broad plateau: weak signal; many α values give similar ρ
- Sharp peak: strong constraint on α from data
