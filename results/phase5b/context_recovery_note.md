# Phase 5B — Context Recovery Note
Date: 2026-06-12

---

## Sources Read

1. `results/phase3d/phase3d_summary.md` — State-specific D and Ω analyses; DO_state_cep_full.npy verified
2. `results/phase4c/phase4c_summary.md` — Multi-timescale results; ΔΩ sign stability confirmed for key pairs
3. `results/phase5a/phase5a_summary.md` — Best confirmed case (RMEL-RMER); perturbation atlas results
4. `results/phase3d/DO_state_cep_full.npy` — Loaded and verified: exact match to D_roam@Q_roam - D_dwell@Q_dwell

---

## Exact ΔΩ_ss Definition Used

```
ΔΩ_ss[i,j] = (D_roam Q_roam)[i,j] - (D_dwell Q_dwell)[i,j]
```

Since Ω_s = D_s Q_s + A, the full state-specific current difference is:

```
ΔΩ_ss = Ω_roam - Ω_dwell = (D_roam Q_roam + A) - (D_dwell Q_dwell + A)
       = D_roam Q_roam - D_dwell Q_dwell
```

The A matrix cancels exactly. The saved `DO_state_cep_full.npy` is verified to match
this formula to machine precision (max diff = 0.00e+00 vs recomputation).

---

## Exact D Estimator Used

State-conditioned pairwise-complete-case Cov(Δx(t) | state), where Δx(t) = x(t+1) - x(t)
(consecutive first differences, τ = 1 frame). Pooled across all 40 recordings.
State condition: both frames t and t+1 in the same behavioral state.
NaN-zero imputation for absent neurons in pairwise complete case.
Source: `results/phase3d/D_roam_cepnem.npy`, `D_dwell_cepnem.npy`.

---

## Exact Q Estimator Used

Anatomy-guided ADMM confirmation matrices:
- Q_roam: `results/phase2/stage1/precision/Q_cepnem_roam_conf.npy`
- Q_dwell: `results/phase2/stage1/precision/Q_cepnem_dwell_conf.npy`
- λ_on = 0.01 (on-connectome penalty), λ_off = 0.10 (off-connectome penalty)
- Symmetrized: Q = (Q + Q^T) / 2

These are the same Q matrices used throughout Phases 2–5A.

---

## Whether Rankings Exist or Need Recomputation

The ΔΩ_ss matrix `DO_state_cep_full.npy` exists as a saved (61×61) array.
A dedicated ranked Class-4 list by |ΔΩ_ss| does NOT exist as a saved .npy file.
Rankings were recomputed in this phase from the existing matrix.

Spearman ρ(|ΔΩ_ss|, |ΔQ|) on Class-4 = **0.3311** (p = 3.7×10⁻³⁵).
The ordering is substantially different from ΔQ — Phase 5B analysis is non-trivial.

---

## Summary of Phase 3D Relevance

Phase 3D already tested ΔΩ_ss_full and found:
- ρ(|ΔΩ_ss_full|, |ΔQ|) = 0.331 (confirmed)
- PDF AUROC = 0.533 (worse than ΔQ's 0.556)
- Fisher OR = 5.46 (same as ΔQ) with k_ann = 4 annotated in top-20
- DA_mech↔URY_URX: rank #2 in all Ω formulations

Phase 5B expands on Phase 3D by: (1) constructing the full ranked top-20 list,
(2) reporting key-pair positions, (3) auditing module-level organization under ΔΩ_ss,
and (4) running the formal enrichment tests with degree-preserving null and comparing
with ΔQ side-by-side.
