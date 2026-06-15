# Phase 10E.2 — Publication Robustness Table
Date: 2026-06-15

## Table Legend

Grades: A=Strong, B=Moderate, C=Weak/Caveated, D=Absent/Fails

All ranks are within N_C4=1321 off-reference Class-4 pairs (CePNEM coordinate) unless noted.

---

## Comprehensive Robustness Table

| Concern Addressed | Test Performed | ADEL–URYVR | ADEL–URYDL | ADEL–RMEL | RMEL–RMER | Module DA↔URY | Verdict | Manuscript Implication |
|-------------------|----------------|-----------|-----------|---------|---------|----------------|---------|----------------------|
| **Fixed-coupling confound** | State-specific B_s ridge regression; ΔΩ^B = ΔΩ_ss + ΔB | Rank 2→2 (unchanged) | Rank 6→3 (promoted) | Rank 4→18 (minor) | Rank 38→371 (FAILS) | Rank 2→1 (strengthened) | **B** — primary pairs robust; RMEL-RMER fails | Disclose ΔΩ^B comparison; note RMEL-RMER fragility; ΔB ranks (370,601) confirm ADEL-PDF not driven by drift change |
| **State-specific drift explains signal?** | ΔB ranks of key pairs | Rank 370 in |ΔB| | Rank 601 in |ΔB| | Rank 1 in |ΔB| (confounded) | Rank 95 | N/A | **A** (ADEL-URY); **D** (ADEL-RMEL) | ADEL-URYVR/URYDL high rankings NOT explained by differential drift; ADEL-RMEL IS confounded |
| **Preprocessing/residualization** | 5 coordinate × estimator variants (B1) | GCaMP+GL rank 28 | GCaMP+GL rank 39 | GCaMP+GL rank 31 | GCaMP+GL rank 709 | GCaMP+GL rank 1 | **B** — signal direction preserved; magnitude estimator-dependent | Report GCaMP+GL ranks; state rank-2 requires CePNEM+anatomy-GL; signal genuine |
| **Estimator choice (GL vs ridge)** | CePNEM+Ridge (anatomy-uninformed) | Rank 165 | Rank 293 | Rank 1 | ~143–564 | Top-3 all variants | **B** — anatomy-guided GL amplifies signal; ridge is conservative lower bound | Anatomy-guided GL encodes prior knowledge; ridge result is conservative, not primary |
| **Animal-level bootstrap** | 500 replicates, ridge precision (conservative) | Median rank 336; top-20 in 5.2% | Median rank 450; top-20 in 4.4% | Median rank 6; top-20 in 76% | Median rank 433 | Median rank 6 | **C/lower bound** — ridge bootstrap ≡ CePNEM+Ridge B1; not a test of primary GL | Label as conservative; bootstrap of primary GL estimator not feasible for n=500 |
| **Leave-one-animal-out** | Remove each of 40 animals; ridge precision (conservative) | Rank range 87–478 | Rank range 72–1261 | Always rank 1–2 | Range 87–564 | Range ~3–14 | **C/lower bound** — same caveat as bootstrap | Identify influential animals; note 2023-01-17-14 most influential for ADEL-URYDL |
| **Co-observation structure** | Matched-pair null (n_coobs ±5) within primary GL values | 99.9th pct, p=0.001 | 99.5th pct, p=0.005 | 99.8th pct, p=0.002 | 97.4th pct, p=0.026 | N/A | **A** (ADEL-URY); **B** (RMEL-RMER) | Co-observation null is PRIMARY specificity test; uses actual GL values; p<0.01 for all ADEL pairs |
| **Dense diffusion creates signal?** | 5 diffusion specifications from D=I to state-specific full | D=I rank 5; full rank 2 | D=I rank 9; full rank 6 | D=I rank 10; full rank 4 | D=I rank 32; full rank 38 | Rank 1 in ALL specs | **A** — signal present under identity diffusion | Dense D refines but does not generate signal; ΔQ is sufficient for top-pair predictions |
| **Diffusion shuffle null** | Diagonal shuffle, off-diagonal shuffle, row/col permutation, state-label swap (n=500) | p=0.018 (row/col); p=0.052 (diag) | p=0.170 (row/col); p=0.060 (diag) | — | — | Row/col: rank 1 in 75% of perms | **A** (URYVR); **B/C** (URYDL) | Row/col null p=0.018 for URYVR; D-Q identity alignment specific to data |
| **Diffusion hub confound** | Hub Spearman ρ; hub-matched null per pair | 99.8th pct, p=0.0017 | 99.6th pct, p=0.0043 | 99.8th pct, p=0.0025 | 97.3th pct, p=0.027 | N/A | **A** — hub score ρ<0.04 globally; endpoint hubness does not explain signal | Dense D hubness is not a confound; results hold among hub-matched pairs |
| **Timescale sensitivity** | ΔΩ(τ) at τ=1,2,5,10,20 frames using Phase 4C D(τ) matrices | Rank 2–4 ALL τ (most stable) | Rank 6–12 (τ≤5); rank 220 (τ=20) | Rank 3–7 (τ≤10); rank 70 (τ=20) | Rank 48–171 (degrades τ≥2) | Rank 1 at τ=1 | **A** (URYVR); **B** (URYDL); **B** (RMEL); **C** (RMER) | ADEL-URYVR is most timescale-robust; ADEL-URYDL stable short-medium lags; sign stable ALL |
| **Diffusion/precision decomposition** | State-conditioned decompositions A and B | 83–96% precision-driven | 92–111% precision-driven | 81–92% precision-driven | 76–81% precision-driven | N/A | **A** — all pairs precision-dominant | ΔΩ signal driven primarily by ΔQ structure; D reweights but does not create signal |
| **Top-K enrichment sweep** | Fisher exact at K=5,10,15,20,25,30,40,50,75,100 | In top-K at ALL K≥5 | In top-K at ALL K≥10 | In top-K at ALL K≥5 | In top-K at K≥40 | N/A | **A** — PDF enriched at ALL K; BH-sig at K=30,40,50 | K=20 primary is not sensitive to K choice; 2/5 and 3/10 PDF at smaller K |
| **FDR correction** | BH across 70 annotation × K combinations | PDF BH-sig at K=30,40,50 (not K=20) | Same | Same | N/A | N/A | **B** — K=20 nominal; sweep BH-sig at K=30–50 | Primary K=20 was single pre-specified test; BH correction applies to sweep only |
| **Reference definition sensitivity** | 10 alternative connectome definitions (Creamer, White, Witvliet, LDS) | Off-reference ALL 10 | Off-reference ALL 10 | Off-reference ALL 10 | Off-reference ALL 10 | N/A | **A** (URYVR/URYDL/RMEL/RMER) | "Off-reference" claim is robust; must disclose RMEL-URYDL borderline case |
| **Baseline comparison** | |ΔQ|, |ΔΩ^B|, |ΔΣ|, |ΔCorr|, |ΔB| (Phase 10A) | Rank 2-5 in all non-ΔB objects | Rank 3-9 in all non-ΔB objects | Variable (1–31) | Variable (32–371) | Top-module in all | **A** (URYVR); **A/B** (URYDL) | Signal is not unique to one scoring object; recoverable in multiple formulations |

---

## Summary Row (Per-Claim)

| Claim | Overall Robustness Grade | Key Limiting Factor |
|-------|------------------------|---------------------|
| ADEL–URYVR | **A/B — Strong, with estimator caveat** | Rank-2 requires CePNEM+GL; no funatlas data |
| ADEL–URYDL | **A/B — Strong, with timescale caveat** | Degrades at τ=20; requires CePNEM+GL |
| ADEL–RMEL | **B — Moderate, ΔB confounded** | ΔB rank 1; partially confounded with coupling change |
| RMEL–URYDL | **C — Weak ranking** | Coupling-sensitive; borderline reference status |
| RMEL–RMER | **C — Ranking weak; confirmation strong** | Ranking fails coupling correction; funatlas confirmation independent |
| DA_mech ↔ URY_URX | **A — Robust** | Rank 1 across all objects; bootstrap-stable |
| PDF top-K enrichment | **A — Robust** | BH-sig at K=30–50; global AUROC p=0.196 |
| Off-reference status (ADEL pairs) | **A — Robust** | Zero synapses in all tested connectomes |

---

## Notes for Table Display in Manuscript

1. Bootstrap and LOAO rows should include footnote: "conservative (ridge precision, not GL)"
2. The co-observation null row should be labeled as "primary specificity test"
3. RMEL-RMER rows should split "ranking" from "confirmation" columns
4. The diffusion decomposition note should state: "decomposition is not unique"
5. FDR row should clarify: "BH applied to Phase 10D sweep only; primary K=20 was single test"
