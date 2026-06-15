# Phase 10A — Context Recovery Note
Date: 2026-06-15
Authorization: Phase 10A

## 1. Current-Primary Object Definition

The primary theoretical object is the state-specific probability current:
  Ω_s = D_s Q_s + A
where D_s is the state-specific (diagonal) diffusion matrix,
Q_s is the state-specific precision matrix (graphical lasso, CePNEM residual),
and A is the **fixed** effective coupling matrix (shared across states).

The primary ranking object is:
  ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell  (A cancels)

The precision-only comparison object is:
  ΔQ = Q_roam − Q_dwell

## 2. Key Pair Ranks

| Pair | ΔΩ_ss | ΔΩ_ss Rank | ΔQ | ΔQ Rank |
|------|-------|-----------|-----|---------|
| ADEL–URYVR | -0.0688 | 2 | -0.1222 | 5 |
| ADEL–URYDL | -0.0498 | 6 | -0.0980 | 9 |
| ADEL–RMEL | -0.0549 | 4 | -0.0957 | 10 |
| ADEL–URXL | -0.0288 | 29 | -0.0450 | 59 |
| RMEL–URYDL | -0.0310 | 23 | -0.0754 | 16 |
| RMEL–URYVR | -0.0267 | 34 | -0.0701 | 21 |
| RMEL–RMER | -0.0254 | 38 | -0.0579 | 32 |

## 3. Confirmed RMEL–RMER Facts

- ΔΩ_ss = −0.0254, rank 38 of 1321 (top 2.9%)
- ΔQ = −0.058, rank 32 of 1321 (top 2.4%)
- Funatlas wt q = 0.0002 (22 obs), unc-31 q = 0.119 (not significant)
- PDF-annotated: RMEL expresses pdf-1, RMER expresses pdfr-1
- DCV-dependent interaction: abolished by unc-31
- GCaMP ΔQ = 0.000; signal is CePNEM-specific

## 4. Module-Level Conclusion

DA_mech ↔ URY_URX is the top module block under both ΔΩ_ss (rank 1) and ΔQ (rank 1).
Under ΔΩ_ss: IL↔IL rises (rank 4) and DA_mech↔RME rises (rank 2) relative to ΔQ.
AV-interneuron blocks (AV↔IL, AV↔URY_URX) are demoted under ΔΩ_ss.

## 5. Current vs Precision Relationship

- Spearman ρ(|ΔΩ_ss|, |ΔQ|) on Class-4 pairs = 0.331
- ΔΩ_ss promotes ADEL-PDF pairs: ADEL–URYVR rank 5→2, ADEL–RMEL rank 10→4, ADEL–URYDL rank 9→6
- ΔΩ_ss demotes RMEL-centered pairs: RMEL–URYDL rank 16→23, RMEL–RMER rank 32→38
- PDF AUROC under ΔΩ_ss = 0.533 (p=0.196, not significant)
- PDF AUROC under ΔQ = 0.556 (p=0.020, significant)
- Fisher top-20 PDF count: 4/20 under both

## 6. Phase 3D Finding on State-Dependent D

- ρ(D_roam diagonal, D_dwell diagonal) = 0.14 (CePNEM): D reorganizes between states
- ||ΔD||_F / ||D_roam||_F ≈ 23%: substantial relative change
- ΔD–ΔQ correlation = 0.056: diffusion and functional connectivity
  reorganize independently — no constructive interference
- ΔΩ_ss_diag ≡ ΔQ (ρ = 0.9998): diagonal D correction is trivial
- The ΔD reorganization is genuine biology but does not create new Ω information

## 7. Phase 4C Timescale Finding

- ΔΩ–ΔQ alignment decays but persists: ρ ranges 0.13–0.33 at τ=1–20 frames
- ΔΩ sign for ADEL-PDF pairs: consistently negative at all τ (dwelling-dominant)
- State-dependent organization is primarily slow-timescale (τ_c ≈ 5–10 frames = 1.25–2.5 s)

## 8. Phase 5A RMEL–RMER Confirmation

- Three-way convergence: observational ΔQ, optogenetic perturbation atlas, unc-31 mutant
- Framework adds state-specificity and residualization beyond funatlas
- Confirmed as strong (Grade C) case in Phase 5A

## 9. Files Present / Missing

Files confirmed present for Phase 10A:
- results/phase2/stage1/precision/Q_cepnem_{roam,dwell}_conf.npy
- results/phase3d/D_{roam,dwell}_cepnem.npy
- results/phase3d/DO_state_cep_full.npy
- results/phase2/stage2/ranked_class4_cepnem.npy
- results/phase1/data/cepnem_residuals/*.npz (41 recordings)

Files not present (not needed for Phase 10A):
- Graphical-lasso edge appearance/disappearance score (not computed previously)
- ΔSigma and ΔCorr matrices (will be computed from state-specific covariances)
- State-specific drift matrices B_roam, B_dwell (to be fitted in Phase 10A.1)
