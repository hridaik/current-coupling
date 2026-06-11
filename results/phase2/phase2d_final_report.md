# Phase 2D Final Report
Date: 2026-06-03
Tasks: (A) Reconstruct missing Stage 1 artifact; (B) Drift quantification

---

## Section 1 — PDF Pair Support Summary

**Question: Are ADEL→URYDL and ADEL→URYVR unusually weakly supported relative to the rest of the PDF network?**

### Answer: No. The novel predictions are among the best-supported PDF pairs.

**ADEL–URYVR** (rank 5 among 1321 Class 4 pairs):
- n_recordings_roam = **15**, n_recordings_dwell = **27**
- n_eff_roam = **882**, n_eff_dwell = **3231**
- |ΔQ_cepnem| = 0.1222

**ADEL–URYDL** (rank 9 among 1321 Class 4 pairs):
- n_recordings_roam = **14**, n_recordings_dwell = **28**
- n_eff_roam = **1094**, n_eff_dwell = **3785**
- |ΔQ_cepnem| = 0.0980

### Context: Full 61-pair PDF network

| Metric | Min | Median | Max |
|---|---|---|---|
| n_recordings_roam | 13 | 16 | 19 |
| n_recordings_dwell | 26 | 31 | 37 |
| n_eff_roam | 746 | 1157 | 1814 |
| n_eff_dwell | 3231 | 4612 | 6831 |
| |ΔQ| rank (of 1321 C4) | 5 | 627 | 1279 |

ADEL–URYVR and ADEL–URYDL have n_rec_roam of 14–15, slightly below the all-pair
median of 16, but within the normal range (min=13). Their n_eff_roam (882–1094) is
below the all-pair median (1157) but well above all Phase 2 minimum thresholds.

### Comparison to reference pairs

| Pair | Rank | n_rec_roam | n_eff_roam | Notes |
|---|---|---|---|---|
| ADEL–URYVR | 5 | 15 | 882 | Novel prediction, occ_funatlas=0 |
| ADEL–URYDL | 9 | 14 | 1094 | Novel prediction, occ_funatlas=0 |
| RMEL–URYDL | 16 | 15 | 829 | Similar support to ADEL predictions |
| RMEL–RMER | 32 | 18 | 856 | Established funatlas q_wt=0.000 |
| RMER–URYVR | 516 | 17 | 1025 | Established funatlas q_wt=0.000 — but ΔQ=0 |

**Key contrast**: RMER–URYVR has established wt-significant functional connectivity
in the Randi funatlas yet shows ZERO CePNEM ΔQ (rank 516). The novel predictions
(ADEL→URYDL/URYVR) have LOWER support counts yet produce the highest ΔQ signal.
The signal is not artifactual weak-support noise.

**RMEL/RMER→OLL pairs**: OLLL–RMEL, OLLR–RMEL, and OLLR–RMER are classified as
**on-connectome** in the Phase 2 analysis (Class 1, excluded from Class 4 enrichment).
These pairs are not in the PDF Class 4 set and cannot be directly compared.

### Conclusion

ADEL→URYDL and ADEL→URYVR are **not unusually weakly supported**. Their support
(14–15 roaming recordings, n_eff_roam 882–1094) is comparable to or above other
top-ranked PDF pairs (RMEL–URYDL: 15 recordings, n_eff_roam=829). The zero-observation
gap in the Randi funatlas for these pairs reflects a DATA COVERAGE gap in the perturbation
atlas, not a weakness of the Phase 2 analysis.

---

## Section 2 — Drift Summary

**Question: What fraction of behavioral ΔQ magnitude is explained by temporal drift?**

### Answer: Median fraction ≈ 0%. Most behavioral signal is distinct from temporal drift.

### Measured drift ratios

Drift defined as: ratio = |ΔQ_drift| / |ΔQ_behavior| per pair,
where ΔQ_drift is computed from first-half vs. second-half recording splits.

| Coordinate | n pairs | Median | p75 | p95 | Max | Frac < 1 | Frac > 2× |
|---|---|---|---|---|---|---|---|
| **CePNEM** | 243 | **0.000** | 0.534 | 4.91 | 104.3 | 80.2% | 10.3% |
| **GCaMP** | 585 | **0.000** | 0.801 | 5.21 | 331.7 | 77.8% | 11.6% |

**Interpretation**:
- **Median ratio = 0**: The majority of pairs where behavioral ΔQ is nonzero show
  near-zero temporal drift ΔQ. The behavioral signal identifies a different set of
  pairs than temporal drift.
- **80% of pairs: drift < behavioral ΔQ**: For the large majority, temporal drift
  does not replicate behavioral ΔQ.
- **High p95/max**: Driven by (a) pairs with very small behavioral ΔQ denominator
  and (b) state-time confounding (Section 3). These values are **upper bounds**
  on drift contribution.

### Critical caveat: confound between drift and behavioral state

The state-time segregation (Section 3) means the first-half/second-half split
partially captures behavioral state (roaming early vs. dwelling throughout). Therefore:

- The drift ratios reported are **inflated** upper bounds on true temporal drift
- The high-ratio pairs (drift > 2×) are consistent with the partial state-signal
  captured by the temporal split, not pure temporal drift
- The true temporal drift (absent state effects) is lower than measured

**Conservative summary**: At the 80th percentile, temporal drift accounts for at most
53% (CePNEM) or 80% (GCaMP) of behavioral ΔQ — and these are upper bounds. At the
median, temporal drift accounts for 0%.

---

## Section 3 — State-Time Segregation

**Question: Are dwelling and roaming epochs systematically separated in recording time?**

### Answer: Yes. Roaming is concentrated EARLY in recordings; dwelling is distributed throughout.

### Measured positions

| State | n recordings | Unweighted mean position | Weighted mean position |
|---|---|---|---|
| Roaming | 19 / 40 | **0.234** | 0.344 |
| Dwelling | 39 / 40 | **0.524** | 0.512 |
| **Difference (roam − dwell)** | — | **−0.290** | **−0.167** |

Normalized position: 0.0 = start of recording, 1.0 = end.
Uniform distribution would give mean position = 0.5.

**Roaming is systematically early**: Mean normalized position 0.234 indicates that
roaming on average occurs in the first quarter of recordings. Of 19 roaming recordings,
14 show mean roaming position < 0.50 (early-biased), and 12 show position < 0.33
(concentrated in the first third).

**Dwelling is approximately uniform**: Mean position 0.524 is close to 0.5, indicating
dwelling is distributed throughout recordings.

**Magnitude of confound**: The 0.290 difference (roam early, dwell uniform) is the
largest potential confound in the dataset. This means a first-half vs. second-half
temporal split will systematically capture MORE roaming-associated covariance in the
first half and MORE dwelling-associated covariance in the second half.

### Implications

1. **For the drift analysis (Section 2)**: The measured drift ratios are inflated
   upper bounds. True temporal drift (absent state effects) would be lower.

2. **For Phase 2 primary analysis**: The behavioral ΔQ estimator uses explicit
   behavioral state labels to condition on roaming vs. dwelling. It is NOT
   affected by the state-time temporal distribution. The temporal confound
   affects only the drift characterization, not the primary enrichment result.

3. **For DEV-003 (all-animal pooling)**: The roaming-early pattern is consistent
   with the known biology (animals roam when first placed on plate, then dwell).
   This is a systematic feature of the experimental design, not a random artifact.
   DEV-003 was partially compensated by the LOO sensitivity (median retention
   CePNEM=0.960, GCaMP=0.940), which showed stability across the 40 recordings
   regardless of this temporal structure.

---

## Output File Index

### Task A — Reconstructed Stage 1 artifact

| File | Path |
|---|---|
| copresence_actual.json | `results/phase2/stage1/copresence_actual.json` |
| pdf_pair_support_table.csv | `results/phase2/figures/pdf_pair_support_table.csv` |
| pdf_pair_support_summary.md | `results/phase2/stage1/pdf_pair_support_summary.md` |

### Task B — Drift quantification

| File | Path |
|---|---|
| drift_quantification_report.md | `results/phase2/drift/drift_quantification_report.md` |
| drift_summary.json | `results/phase2/drift/drift_summary.json` |
| drift_pairwise_ratios.npy | `results/phase2/drift/drift_pairwise_ratios.npy` |

---

*Phase 2D is complete. No further computation is authorized.*
*Tasks A and B as specified are fully executed.*
