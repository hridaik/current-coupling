# Phase 10E — Context Recovery
Date: 2026-06-15
Authorization: Phase 10E — Publication Robustness Synthesis

---

## 1. Primary Result Under Synthesis

**State-specific probability current:**
  ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell

where D_s = state-specific innovations covariance (61×61), Q_s = anatomy-guided
graphical-lasso precision (61×61, λ_on=0.01, λ_off=0.10), A = fixed coupling.

**Primary biological claim**: A state-dependent, dwelling-dominant, PDF-associated
ADEL–URY current organization is detected among off-reference Class-4 pairs.

---

## 2. Primary Pair Ranks Across All Scoring Objects

| Pair | |ΔΩ_ss| | |ΔQ| | |ΔΩ^B| | GCaMP+GL | CePNEM+Ridge | Phase 5A funatlas |
|------|--------|-----|-------|---------|-------------|-------------------|
| ADEL–URYVR | **2** | 5 | 2 | 28 | 165 | 0 obs (novel prediction) |
| ADEL–URYDL | **6** | 9 | 3 | 39 | 293 | 0 obs (novel prediction) |
| ADEL–RMEL  | **4** | 10 | 18 | 31 | 1 | — |
| RMEL–URYDL | 23 | 16 | 168 | — | — | — |
| RMEL–RMER  | 38 | 32 | 371 | 709 | ~143–564 | wt q=0.0002, unc-31 abolished |

All ranks are within N_C4 = 1321 off-reference Class-4 pairs.
|ΔΩ_ss| and |ΔQ| rankings use CePNEM coordinate throughout.
GCaMP+GL uses raw GCaMP with same anatomy-guided GL precision (Phase 10B B1).
CePNEM+Ridge uses uniform-penalty ridge precision (Phase 10B B1).
|ΔΩ^B| = corrected current adding state-specific coupling (Phase 10A).

---

## 3. PDF Annotation Context

- Bentley PDF (Bentley ESconnectome, pdf-1/pdf-2/pdfr-1): 61 C4 pairs
- Bentley serotonin: 33 C4 pairs
- PDF pairs in top-20 by |ΔΩ_ss|: 4 (ranks 2, 4, 6, 20)
- PDF pairs in top-20 by |ΔQ|: 4 (ranks 5, 9, 10, 16)
- PDF AUROC under |ΔΩ_ss|: 0.533 (p=0.196, not significant globally)
- PDF AUROC under |ΔQ|: 0.556 (p=0.023, significant)
- PDF Fisher K=20 under |ΔΩ_ss|: OR=5.2, p=0.011, p_degree_perm=0.008

---

## 4. Robustness Grades by Phase

### Phase 10A — Fixed-Coupling / ΔB Control

| Claim | Grade |
|-------|-------|
| ADEL–URYVR under ΔΩ^B | **Robust** — rank unchanged (2→2) |
| ADEL–URYDL under ΔΩ^B | **Robust** — rank promoted (6→3) |
| ADEL–RMEL under ΔΩ^B | **Minor change** — rank 4→18 (remains top-20) |
| DA_mech↔URY_URX module | **Strengthened** — rank 1 under ΔΩ^B |
| RMEL–RMER under ΔΩ^B | **Sensitive** — rank 38→371 |
| ΔB explains ADEL-PDF? | **No** — ΔB ranks of ADEL-URYVR/URYDL: 370, 601 |
| Overall fixed-coupling verdict | **B — approximately supported** |

Key metric: ||ΔB||_F / ||B_roam||_F = 0.339 (non-trivial coupling change but not a confound for primary pairs)

### Phase 10B — Residualization and Animal Robustness

| Claim | Grade |
|-------|-------|
| ADEL–URYVR (signal presence) | **B** — GCaMP+GL rank 28, top 2% |
| ADEL–URYDL (signal presence) | **B** — GCaMP+GL rank 39, top 3% |
| ADEL–URYVR vs co-obs null | **Strong** — p=0.001, 99.9th pct |
| ADEL–URYDL vs co-obs null | **Strong** — p=0.005, 99.5th pct |
| Animal bootstrap (ridge) | CONSERVATIVE — equivalent to CePNEM+Ridge B1 |
| LOAO (ridge) | CONSERVATIVE — same caveat; ADEL-RMEL always top-2 |
| DA_mech↔URY_URX | **A/B** — rank 1 in GCaMP+GL, bootstrap rank ~6 |
| RMEL–RMER | **C** — rank 709 in GCaMP+GL; bootstrap unstable |
| Overall grade | **B — Moderate robustness** |

Critical note: bootstrap/LOAO use ridge (not GL), so they are conservative lower bounds.

### Phase 10C — Diffusion-Specific Robustness

| Claim | Grade |
|-------|-------|
| ADEL–URYVR (diffusion) | **A** — rank 5 in ΔQ/D=I; hub null p=0.0017; top-5 all τ |
| ADEL–URYDL (diffusion) | **A/B** — rank 9 in D=I; degrades at τ=20 |
| DA_mech↔URY_URX (diffusion) | **A** — rank 1 across all 5 diffusion specs |
| ADEL–RMEL (diffusion) | **B** — stable τ≤10, degrades τ=20 |
| RMEL–RMER (diffusion) | **C** — 24% diffusion-driven; degrades τ≥5 |
| PDF top-20 enrichment (diff) | **B** — 4/20 at τ=1, 2/20 at τ=20 |
| Dense diffusion creates ADEL/PDF? | **No** — signal present under D=I (rank 5/9) |
| Diffusion hub explains signal? | **No** — hub ρ<0.04; hub-matched null p=0.0017 |
| Decomposition: precision-dominant? | **Yes** — 76–114% across both decompositions |

### Phase 10D — Top-K and Reference Sensitivity

| Claim | Grade |
|-------|-------|
| PDF enrichment K-robust | **A** — significant at all K=5–100; BH-sig at K=30,40,50 |
| ADEL-URYVR/URYDL off-reference | **A** — off-ref under all 10 connectome definitions |
| ADEL-RMEL/RMEL-RMER off-reference | **A** — off-ref under all 10 definitions |
| RMEL-URYDL off-reference | **B/Disclose** — ON-ref under Creamer chem thr=1 (1 synapse) |
| Serotonin enrichment | **D — Absent** (0 in top-K at all K) |
| FDR status K=20 primary | Nominal (single pre-specified test); BH within sweep: n.s. |
| FDR status K=30,40,50 | BH-significant within 70-test sweep |

---

## 5. Phase 5A/5B Context

**Phase 5A (confirmation):**
- RMEL–RMER: confirmed by funatlas (wt q=0.0002, n=22 obs; unc-31 abolished, n=5)
- Three-way convergence: observational ΔQ + optogenetic funatlas + genetic unc-31
- CAVEAT: RMEL-RMER is not robust to coupling correction (Phase 10A: rank 38→371)
- ADEL-URYVR, ADEL-URYDL: 0 funatlas observations — untested novel predictions
- Secondary confirmations: CEPDR-URXL (wt q=0.0002), I1R-RMDVR (wt q=0.032, DCV-dep)

**Phase 5B (ΔΩ vs ΔQ comparison):**
- All five pairs sign-stable (dwelling-dominant) under both formulations
- ADEL-PDF triplet PROMOTED under ΔΩ_ss (ranks 5,9,10 → 2,6,4)
- PDF AUROC significance LOST under ΔΩ_ss (p=0.020 → p=0.196)
- Top-20 Fisher count PRESERVED (4/20 both)
- RMEL-RMER modestly demoted (rank 32→38)

**Phase 4B (behavioral encoding):**
- PDF pairs do NOT preferentially connect neurons with aligned behavioral encoding
- ADEL-URYVR alignment = −0.015 (anti-aligned: ADEL roaming-active, URYVR dwelling-active)
- Information-limiting interpretation: NO SUPPORT
- Verdict: "Information-limiting correlations" should NOT be claimed

**Phase 4C (timescale):**
- State-specific structure operates on slow timescales (τ_c ≈ 5–10 frames = 1.25–2.5 s)
- ΔΩ sign for ADEL-PDF pairs: stable at ALL τ=1,2,5,10,20 frames
- ADEL-URYVR: rank 2–4 at all timescales tested
- ADEL-URYDL: stable τ≤5, degrades at τ≥10
- ΔD sign: unstable across τ for most pairs (not a reliable descriptor)

---

## 6. Available Files

| Phase | File | Status |
|-------|------|--------|
| 10A | phase10a_summary.md | Read ✓ |
| 10A | a6_fixed_coupling_verdict.md | Read ✓ |
| 10B | phase10b_summary.md | Read ✓ |
| 10B | b5_residualization_animal_verdict.md | Read ✓ |
| 10C | phase10c_summary.md | Read ✓ (via prior context) |
| 10C | c6_diffusion_verdict.md | Read ✓ (via prior context) |
| 10D | phase10d_summary.md | Read ✓ |
| 10D | d6_topK_reference_verdict.md | Read ✓ |
| 5A | phase5a_summary.md | Read ✓ |
| 5B | phase5b_summary.md | Read ✓ |
| 4A | phase4a_activity_summary.md | Read ✓ |
| 4B | phase4b_summary.md | Read ✓ |
| 4C | phase4c_summary.md | Read ✓ |

---

## 7. Key Inconsistencies and Tensions

**Tension 1 — RMEL-RMER confirmation vs. ranking fragility**
Phase 5A: strong funatlas confirmation (Grade C — Strong).
Phase 10A: rank drops 38→371 under coupling correction.
Phase 10B: rank 709 in GCaMP+GL; bootstrap unstable; co-obs p=0.026.
**Resolution**: The funatlas confirmation is real but independent of the model ranking.
RMEL-RMER should be presented as a "biologically confirmed case" NOT as a "model-ranking validation." Its ranking under ΔΩ_ss is confounded by the fixed-coupling assumption.

**Tension 2 — PDF AUROC significance depends on scoring object**
Under |ΔQ|: AUROC=0.556, p=0.023 (significant).
Under |ΔΩ_ss|: AUROC=0.533, p=0.196 (not significant globally).
Top-20 Fisher: 4/20 for both; K-sweep: enriched at all K.
**Resolution**: The global AUROC significance loss is real and should be disclosed.
The top-tier PDF enrichment (Fisher/K-sweep) is preserved. Claim should use Fisher/K-sweep, not AUROC, as the primary enrichment statistic.

**Tension 3 — CePNEM+GL vs. GCaMP+GL dependence**
Extreme ranks (2,6) depend on CePNEM residualization AND anatomy-guided GL.
GCaMP+GL ranks (28, 39) are top 2–3% but not top-5.
**Resolution**: Both components (residualization + anatomy-guided estimator) contribute scientifically motivated signal. Report GCaMP+GL as robustness check; state estimator dependence explicitly. Co-obs null (p=0.001, 0.005) provides estimator-independent evidence for signal genuineness.

**Tension 4 — RMEL-URYDL reference status**
Primary locked C4=1321 treats RMEL-URYDL as off-reference.
Creamer chem thr=1 (closest approximation to primary A_raw) gives RMEL-URYDL as ON-reference.
**Resolution**: Disclose that RMEL-URYDL has marginal Creamer connectivity (1 directed synapse). Treat it as a secondary/borderline result in any reference-sensitivity claim.

**No missing files.** All 13 required input files were read successfully.

---

**Proceeding to Phase 10E synthesis.**
