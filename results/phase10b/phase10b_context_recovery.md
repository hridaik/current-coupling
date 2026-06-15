# Phase 10B — Context Recovery Note
Date: 2026-06-15
Authorization: Phase 10B

## 1. Primary Object

ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell  (A cancels, fixed-coupling).
D_s: state-specific diffusion matrix (full, 61×61), from Phase 3D.
Q_s: anatomy-guided graphical lasso precision, from Phase 2 Stage 1.

## 2. Key Pair Ranks from Phase 5B

| Pair | ΔΩ_ss | ΔΩ_ss Rank | ΔQ Rank |
|------|-------|-----------|--------|
| ADEL–URYVR | −0.069 | 2 | 5 |
| ADEL–URYDL | −0.050 | 6 | 9 |
| ADEL–RMEL  | −0.055 | 4 | 10 |
| RMEL–URYDL | −0.031 | 23 | 16 |
| RMEL–RMER  | −0.025 | 38 | 32 |

## 3. Phase 10A Fixed-Coupling Verdict

**B. Fixed-coupling assumption approximately supported; minor qualification needed.**
- ADEL–URYVR: rank 2 → 2 under ΔΩ^B (coupling-corrected) — ROBUST
- ADEL–URYDL: rank 6 → 3 — ROBUST (promoted)
- ADEL–RMEL: rank 4 → 18 — MINOR CHANGE
- RMEL–RMER: rank 38 → 371 — NOT ROBUST to coupling correction
- DA_mech ↔ URY_URX module: rank 2 → 1 — STRENGTHENED

## 4. Claim Status Entering Phase 10B

**Primary (to be robustness-tested):**
- ADEL–URYVR (rank 2): novel prediction, 0 funatlas observations
- ADEL–URYDL (rank 6): novel prediction, 0 funatlas observations

**Secondary:**
- ADEL–RMEL (rank 4): mixed current/drift character (ΔB rank 1), top-20 under ΔΩ^B
- DA_mech ↔ URY_URX module (rank 2): dominant module under both ΔΩ_ss and ΔQ

**Qualified:**
- RMEL–RMER (rank 38): confirmed by funatlas, but ranking not robust to coupling correction
- RMEL–URYDL (rank 23): lacks independent experimental confirmation

## 5. Robustness Targets for Phase 10B

B1: Does ADEL–URYVR/URYDL signal appear in non-CePNEM coordinates?
B2: Is the signal stable across animal bootstrap resampling?
B3: Does any single animal drive the ADEL–URYVR/URYDL result?
B4: Is the ADEL–URYVR/URYDL rank stronger than expected given co-observation support?

## 6. Note on Estimation Approach for Bootstrap/LOAO

Bootstrap and LOAO analyses use ridge-regularized precision matrices
(Q_s = (Σ_s + λI)^{-1}, λ = 5% of mean diagonal) rather than the Phase 2
graphical lasso, for computational feasibility. Ridge precision is a conservative
estimator: if the signal survives under ridge (which is noisier at moderate ranks),
it is expected to survive under graphical lasso.
