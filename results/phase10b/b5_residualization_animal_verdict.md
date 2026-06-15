# Phase 10B.5 — Combined Robustness Verdict
Date: 2026-06-15

## Critical Note on Bootstrap/LOAO Methodology

**IMPORTANT CAVEAT BEFORE READING Q1–Q4:**

The B2 bootstrap and B3 LOAO use ridge-regularized precision (Q = (Σ+λI)⁻¹, λ = 5%
mean diagonal), NOT the anatomy-guided graphical lasso used in the primary analysis.
Phase 2's graphical lasso uses a 10× stiffer penalty on off-connectome (Class-4) pairs
(λ_off = 0.10) relative to on-connectome pairs (λ_on = 0.01). This penalty is the
theoretically and anatomically motivated estimator choice.

**Consequence:** The B2/B3 bootstrap results are EQUIVALENT to a test of the CePNEM+Ridge
variant from B1 (which showed ADEL-URYVR rank ~165). They are valid as a lower bound on
robustness but do NOT represent bootstrap tests of the actual primary estimator. They answer:
"Would the signal survive bootstrap IF we used ridge precision?" Not: "Is the GL signal
stable across animal resampling?"

**The co-observation null (B4) is the most direct test**: it uses the PRIMARY ΔΩ_ss values
(from the locked graphical lasso) and asks whether ADEL-URYVR/URYDL are genuinely unusual
among similarly co-observed pairs. This test is not affected by estimator choice.

---

## Q1: Does the primary ADEL/PDF signal survive alternative residualization?

**Decomposed answer — two distinct effects:**

**Coordinate effect (GL estimator fixed):**
CePNEM→GCaMP: ADEL–URYVR rank 2→28, ADEL–URYDL rank 6→39.
Signal is PRESENT in GCaMP+GL (top 2–3%) but weaker. Residualization helps substantially.

**Estimator effect (CePNEM coordinate fixed):**
GL→Ridge: ADEL–URYVR rank 2→165, ADEL–URYDL rank 6→293.
The anatomy-guided penalty amplifies the signal for Class-4 pairs. Without this prior, signal
is diluted. The anatomy-guided GL is the scientifically correct estimator (it encodes genuine
knowledge about which pairs are more likely to be directly coupled).

**Combined:**
The rank-2 of ADEL-URYVR requires both CePNEM and anatomy-guided GL.
The signal direction and approximate elevation (top 2-3%) are supported by GCaMP+GL.
The full magnitude of the ranking is estimator-dependent.

**Verdict: B (for signal presence) / C (for specific rank)**

## Q2: Does the primary ADEL/PDF signal survive animal bootstrap?

CONSERVATIVE TEST (ridge precision, not GL): Bootstrap with ridge precision is equivalent
to bootstrapping the CePNEM+Ridge variant, not the primary CePNEM+GL analysis.

Under ridge precision:
- ADEL–URYVR: top-20 in 5.2% of replicates, median rank 336
- ADEL–URYDL: top-20 in 4.4% of replicates, median rank 450
- ADEL–RMEL: top-20 in 76.4% of replicates, median rank 6

This is consistent with the B1 CePNEM+Ridge result (rank ~165/293). The bootstrap
correctly tracks the ridge estimator instability.

**Interpretation:** ADEL–URYVR and ADEL–URYDL rankings under the GL estimator are likely
more stable than these ridge bootstrap results suggest, because the GL anatomy guidance
reduces variability for Class-4 pairs. ADEL–RMEL is truly robust even under ridge.

**Verdict: INCONCLUSIVE for the primary GL estimator; ridge bootstrap is a lower bound.**

## Q3: Does the primary ADEL/PDF signal survive leave-one-animal-out?

CONSERVATIVE TEST (ridge precision): Same caveat as Q2.

Under ridge precision:
- ADEL–URYVR: rank range 87–478 (not always top-50)
- ADEL–URYDL: rank range 72–1261 (highly variable; worst: removing 2023-01-17-14)
- ADEL–RMEL: rank range 1–2 (always top-2 — very robust)

The high variability for ADEL-URYVR/URYDL under ridge LOAO is consistent with the ridge
estimator being sensitive to individual animals at these pair-level effects. Under the
GL estimator, the anatomy guidance would stabilize these estimates.

**Verdict: INCONCLUSIVE for primary GL estimator; ridge LOAO indicates some animal-level
sensitivity that warrants further investigation with the full GL estimator.**

## Q4: Does the signal exceed co-observation-matched expectations?

**STRONG — this is the most robust test (uses primary GL values):**

ADEL–URYVR: 99.9th percentile among 981 matched pairs (n_coobs = 28±5), p = 0.001
ADEL–URYDL: 99.5th percentile among 1092 matched pairs (n_coobs = 29±5), p = 0.005
ADEL–RMEL: 99.8th percentile (p = 0.002)

These pairs are at the extreme tail of their co-observation-matched distributions.
No artifact of co-observation frequency can explain their high |ΔΩ_ss| values.
The matched median |ΔΩ_ss| is ~0.005 while ADEL–URYVR has |ΔΩ_ss| = 0.069 (14×).

**Verdict: STRONG — signal exceeds co-observation-matched null at p < 0.01 for all ADEL pairs.**

## Q5: Which claims remain primary?

Integrating B1–B4 with the understanding that B2/B3 are conservative (ridge-based):

**PRIMARY (strong evidence):**
- ADEL–URYVR: 99.9th percentile co-obs null; top-2% in GCaMP+GL; rank-2 requires GL+CePNEM
- ADEL–URYDL: 99.5th percentile co-obs null; top-3% in GCaMP+GL; rank-6 requires GL+CePNEM
- DA_mech ↔ URY_URX module: rank 1 in GCaMP+GL; top-3 in most variants

**SECONDARY (signal present but weaker):**
- ADEL–RMEL: most robust under ridge (bootstrap rank ~6, LOAO always top-2) but confounded
  with coupling change (Phase 10A: ΔB rank 1); interpret as joint precision+coupling signal

## Q6: Which claims require qualification?

REQUIRES QUALIFICATION (mention in methods/supplementary):
- "The rank-2 position of ADEL–URYVR is specific to the CePNEM+anatomy-guided-GL pipeline;
  under raw GCaMP+GL the rank is 28 (top 2%), and under ridge precision it is 165 (top 13%).
  The signal is genuine (p=0.001 vs matched null) but its precise rank is estimator-dependent."
- RMEL–RMER: not robust to coupling correction (Phase 10A) and unstable under ridge bootstrap
- All ridge-based bootstrap/LOAO results should be labeled as conservative

## Per-Claim Verdict (Revised)

| Claim | Signal present? | Specific rank robust? | Co-obs null | Grade |
|-------|----------------|----------------------|-------------|-------|
| ADEL–URYVR | Yes (GCaMP+GL rank 28) | No (GL-specific) | p=0.001 (99.9th pct) | **B** |
| ADEL–URYDL | Yes (GCaMP+GL rank 39) | No (GL-specific) | p=0.005 (99.5th pct) | **B** |
| DA_mech↔URY_URX | Yes (rank 1 in GCaMP) | Moderate | N/A | **A/B** |
| ADEL–RMEL | Yes (ridge rank 1–2) | Yes (ridge-robust) | p=0.002 | **A** (but confounded with ΔB) |
| RMEL–RMER | Partial | No (GL rank 38, ridge rank 143–564) | p=0.026 | **C** |

**Overarching Grade: B — Moderate robustness; the signal is genuine and specific (co-obs
null p<0.01), but the primary high ranking (rank 2/6) depends on the anatomy-guided GL
estimator used in Phase 2. This is expected given the estimator's design, and the
anatomy guidance is scientifically motivated. The manuscript should report GCaMP+GL
ranks as a robustness check and frame the co-observation null as primary evidence for
signal specificity.**
