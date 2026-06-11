# Phase 4A-E — Exemplary Trace Examples
Date: 2026-06-04
Authorization: Phase 4A

## Selection Rule (Pre-Specified)

Among the 22 recordings with all 6 neurons present, select the 4 with the most
balanced roaming/dwelling ratio (|n_roam/n_dwell − 1| closest to 0), subject to
n_roam ≥ 100 frames and n_dwell ≥ 100 frames. This ensures examples showing both
states, minimizes cherry-picking bias, and is independent of any analysis result.

Neurons shown: ADEL, URYVR, URYDL (the primary Phase 2 predictions).

---

## Selected Recordings

| Recording | n_roam | n_dwell | Ratio | Notes |
|---|---|---|---|---|
| 2023-01-09-15 | 782 | 833 | 0.94 | Near-equal roam/dwell |
| 2023-01-09-22 | 757 | 858 | 0.88 | Many transitions (52 total) |
| 2023-01-23-15 | 856 | 744 | 1.15 | Slightly roam-dominant |
| 2022-06-14-07 | 892 | 708 | 1.26 | Earlier dataset; longer roam bouts |

---

## Trace Description

### 2023-01-09-15 (near-equal roam/dwell)

This recording shows alternating roaming and dwelling bouts of moderate duration.
ADEL activity is variable throughout with no obvious state bias. URYVR and URYDL
show variable, modestly higher activity during some roaming epochs. No single large
bout event dominates.

### 2023-01-09-22 (most transitions)

This recording has the highest transition count (52 R/D transitions in 1615 frames ≈
1 transition per 30 frames ≈ 1 per 6 seconds). Activity is highly fragmented with
many short bouts. The short within-state epochs make state-specific patterns harder
to visualize but are ideal for the transition analysis.

### 2023-01-23-15 (roaming-dominant)

An example with more roaming than dwelling. ADEL, URYVR, URYDL are visible
throughout; state differences in activity are modest and variable.

### 2022-06-14-07 (earliest dataset)

From the earliest recording cohort. Contains longer roaming bouts early in the
recording (consistent with the known temporal structure: animals often roam early
on a plate). Activity patterns are similar to the 2023 recordings.

---

## Visual Notes

- Roaming periods marked with red shading in FigA5.
- Activity traces show substantial within-animal variability; no single recording
  is "representative" of all 22.
- The dominant impression from all 4 examples is that activity variation is
  substantial both within and between states, without a consistent large step
  change at state transitions.

---

*E scope: exemplary trace selection only. Figure: FigA5_example_traces.pdf*
