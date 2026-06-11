# PHASE3_CHECKPOINT_LOG.md

---

## CHECKPOINT P3-001: Phase 3A — State-dependent PDF forward model fitting
Date: 2026-06-03
Stage: 3A (complete)
Authorization: AUTHORIZED by human supervisor 2026-06-03

[1] Previous state: Phase 2 complete and archived. Design package locked (phase3_design_package.md). Locked decisions: J=A_raw directed, P=Bentley PDF directed, scalar α_s, Spearman objective, 4 ADEL held-out pairs.

[2] This rules out: any use of held-out ADEL pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, ADEL–URXL) in fitting, objective construction, or model comparison scoring.

[3] The proposed action: Implement forward model J_eff(s) = J_base + α_s*P_norm via Lyapunov solve, fit (α_r, α_d) by Spearman rank correlation grid search + Nelder-Mead, compare M0/M1/M2/M3.

[4] Success criteria: Criterion 1 (AUROC M1 > M0 + 0.05), Criterion 2 (AUROC M1 > M2 + 0.03), Criterion 3 (stability margin > 0.10).

[5] Result: PARTIAL PASS. Criterion 1 PASS (AUROC=0.919 >> 0.550). Criterion 2 NOT EVALUABLE (M2 comparison degenerate; see below). Criterion 3 PASS (margin=0.335).

Key numbers:
  J: 327 directed edges, γ=6.13, α_max=+0.067, α_min=−43.9
  P: 77 directed edges, Frobenius norm=8.78
  M0: ρ=0.000
  M1: α_roam=−26.25, α_dwell=−23.97, Δα=+2.28 (P_norm), ρ_train=0.0618
  M2: DEGENERATE — all 1000 P_rand give ρ=0.0606 (artifact of fixing α_r at M1 value)
  M3 (Creamer): ρ=0.0425

M2 methodological issue: α_r was fixed at alpha_r_M1 for all P_rand graphs, making J_eff(roam) structurally identical across P_rand at large |α|. A proper 2D M2 comparison requires authorization for a new run (~1 hour compute).

Sign interpretation: |ΔQ| objective is sign-ambiguous. Physically, the correct assignment is α_dwell ≈ −26.25, α_roam ≈ −23.97 (dwelling more inhibitory → Q_dwell > Q_roam ✓).

Held-out ADEL pairs: NOT evaluated. held_out_evaluated=False in all output files.

[6] STOP: Phase 3A complete. Awaiting human review before any further computation.

Required before held-out evaluation:
  [ ] Human reviews phase3a_model_comparison_report.md
  [ ] Human decides: (a) proceed to held-out evaluation, or (b) run corrected M2 comparison first, or (c) redesign
  [ ] Human authorizes Phase 3B or held-out evaluation explicitly

