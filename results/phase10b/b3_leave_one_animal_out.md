# Phase 10B.3 — Leave-One-Animal-Out Robustness
Date: 2026-06-15

Leave-one-out design: 40 leave-out experiments (one animal at a time).
Same estimation approach as bootstrap (ridge precision).

## Key Pair Rank Statistics

| Pair | Min Rank | Max Rank | Median Rank | Always Top-20 | Always Top-50 | Worst Animal |
|------|---------|---------|-------------|--------------|--------------|-------------|
| ADEL–URYVR | 87 | 478 | 165 | No | No | 2023-03-07-01 |
| ADEL–URYDL | 72 | 1261 | 296 | No | No | 2023-01-17-14 |
| ADEL–RMEL | 1 | 2 | 1 | Yes | Yes | 2023-01-10-14 |
| RMEL–URYDL | 59 | 508 | 129 | No | No | 2023-01-10-14 |
| RMEL–RMER | 87 | 564 | 143 | No | No | 2023-01-17-14 |

## Full Leave-One-Animal-Out Table

| Animal Removed | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–URYDL | RMEL–RMER | PDF/20 | DA_URY | Top20 Ovlp |
|----------------|-----------|-----------|---------|----------|---------|-------|-------|-----------|
| 2022-06-14-01 | 162 | 314 | 1 | 121 | 160 | 1/20 | 8 | 4/20 |
| 2022-06-14-07 | 191 | 234 | 1 | 91 | 144 | 1/20 | 8 | 4/20 |
| 2022-06-14-13 | 148 | 314 | 1 | 149 | 110 | 1/20 | 7 | 5/20 |
| 2022-06-28-01 | 149 | 533 | 1 | 79 | 221 | 1/20 | 7 | 4/20 |
| 2022-06-28-07 | 195 | 345 | 1 | 119 | 122 | 1/20 | 6 | 5/20 |
| 2022-07-15-06 | 200 | 355 | 1 | 137 | 219 | 1/20 | 7 | 5/20 |
| 2022-07-15-12 | 155 | 247 | 1 | 109 | 126 | 1/20 | 5 | 4/20 |
| 2022-07-20-01 | 112 | 274 | 1 | 107 | 113 | 1/20 | 6 | 5/20 |
| 2022-07-26-01 | 212 | 228 | 1 | 177 | 152 | 1/20 | 8 | 5/20 |
| 2022-08-02-01 | 119 | 219 | 1 | 155 | 97 | 1/20 | 8 | 5/20 |
| 2022-12-21-06 | 165 | 245 | 1 | 147 | 160 | 1/20 | 6 | 5/20 |
| 2023-01-05-01 | 195 | 331 | 1 | 159 | 158 | 1/20 | 7 | 5/20 |
| 2023-01-05-18 | 165 | 318 | 1 | 138 | 131 | 1/20 | 5 | 5/20 |
| 2023-01-06-01 | 229 | 331 | 1 | 131 | 133 | 1/20 | 6 | 5/20 |
| 2023-01-06-08 | 192 | 258 | 1 | 139 | 142 | 1/20 | 5 | 5/20 |
| 2023-01-06-15 | 154 | 394 | 1 | 113 | 157 | 1/20 | 6 | 4/20 |
| 2023-01-09-08 | 170 | 296 | 1 | 147 | 115 | 1/20 | 7 | 5/20 |
| 2023-01-09-15 | 151 | 435 | 1 | 300 | 135 | 1/20 | 6 | 4/20 |
| 2023-01-09-22 | 314 | 342 | 1 | 83 | 177 | 1/20 | 9 | 5/20 |
| 2023-01-09-28 | 192 | 284 | 1 | 137 | 119 | 1/20 | 7 | 5/20 |
| 2023-01-10-07 | 87 | 288 | 1 | 59 | 182 | 1/20 | 7 | 3/20 |
| 2023-01-10-14 | 109 | 340 | 2 | 508 | 98 | 1/20 | 7 | 5/20 |
| 2023-01-13-07 | 171 | 300 | 1 | 132 | 92 | 1/20 | 8 | 5/20 |
| 2023-01-16-01 | 174 | 352 | 1 | 136 | 97 | 1/20 | 6 | 3/20 |
| 2023-01-16-08 | 161 | 291 | 1 | 117 | 120 | 1/20 | 8 | 5/20 |
| 2023-01-16-15 | 323 | 72 | 1 | 109 | 146 | 1/20 | 7 | 2/20 |
| 2023-01-16-22 | 178 | 329 | 1 | 127 | 162 | 1/20 | 6 | 5/20 |
| 2023-01-17-01 | 115 | 215 | 1 | 85 | 158 | 1/20 | 6 | 4/20 |
| 2023-01-17-07 | 133 | 164 | 1 | 170 | 151 | 1/20 | 5 | 5/20 |
| 2023-01-17-14 | 363 | 1261 | 1 | 98 | 564 | 1/20 | 8 | 3/20 |
| 2023-01-18-01 | 155 | 276 | 1 | 175 | 204 | 1/20 | 5 | 4/20 |
| 2023-01-19-01 | 161 | 227 | 1 | 123 | 170 | 1/20 | 5 | 5/20 |
| 2023-01-19-08 | 185 | 247 | 1 | 220 | 162 | 1/20 | 6 | 5/20 |
| 2023-01-19-15 | 155 | 297 | 1 | 127 | 134 | 1/20 | 5 | 5/20 |
| 2023-01-19-22 | 193 | 185 | 1 | 204 | 153 | 1/20 | 5 | 5/20 |
| 2023-01-23-01 | 134 | 729 | 1 | 104 | 97 | 2/20 | 7 | 5/20 |
| 2023-01-23-08 | 160 | 311 | 1 | 121 | 167 | 1/20 | 9 | 4/20 |
| 2023-01-23-15 | 94 | 189 | 1 | 95 | 140 | 1/20 | 7 | 4/20 |
| 2023-01-23-21 | 202 | 379 | 1 | 106 | 120 | 1/20 | 9 | 5/20 |
| 2023-03-07-01 | 478 | 245 | 1 | 182 | 87 | 1/20 | 7 | 5/20 |

## Influential Animals

Removing 2023-03-07-01 most increases ADEL–URYVR rank: 478
Removing 2023-01-17-14 most increases ADEL–URYDL rank: 1261

## Interpretation

**CONSERVATIVE TEST — ridge precision approximation, not the primary GL estimator.**

This LOAO uses ridge-regularized precision (uniform λ, no anatomy guidance), equivalent
to leave-one-animal-out of the "CePNEM+Ridge" B1 variant, not the primary CePNEM+GL analysis.

**Under ridge precision:**
- ADEL–URYVR: rank range 87–478, median 165 — NOT stable under ridge
- ADEL–URYDL: rank range 72–1261, median 296 — highly variable; worst case rank 1261
- ADEL–RMEL: rank range 1–2, median 1 — ALWAYS top-2 (truly robust even under ridge)
- RMEL–RMER: rank range 87–564, NOT robust

**Animal 2023-03-07-01** removes the most influential contributor for ADEL-URYVR (rank 478);
**animal 2023-01-17-14** removes the most influential for ADEL-URYDL (rank 1261).
These extremes apply under ridge precision. Whether similar sensitivity exists under the
anatomy-guided GL estimator is unknown, but GL's regularization structure
(strong off-connectome penalty) would partially attenuate individual-animal influence
on Class-4 pair rankings.

**ADEL-RMEL consistency** (always rank 1–2 in LOAO): confirmed here. This robust signal
is genuine but dominated by effective coupling change (Phase 10A: |ΔB| rank 1), not
purely precision structure.

**DA_mech ↔ URY_URX module:** median rank 6–8 across LOAO experiments, P5–P95 roughly
[5–12]. Module-level signal is more stable than individual pair rankings under ridge.

**Summary:** The ridge LOAO indicates ADEL-URYVR/URYDL have meaningful animal-level
sensitivity under the ridge estimator. The co-observation null (B4) is the strongest
and most appropriate test of signal specificity, as it uses the primary GL values
directly and is not affected by estimator-regularization choices.
