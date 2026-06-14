# Phase 8A Readiness Assessment
**Date:** 2026-06-13  
**Question:** Is the evaluation fully specified and may Phase 8B begin?

---

## 1. Is Evaluation Fully Specified?

**YES.**

All evaluation inputs are defined with forbidden/allowed distinctions (phase8a_evaluation_spec.md).  
The output schema is fully specified with no ambiguity (§3 of eval spec).  
The evaluation unit is defined (directed pair).  
The evaluation order is specified (oracle_z primary, others secondary).  
All five evaluation conditions are assigned roles.

**Gaps:** None. All decisions that could have been left open have been closed.

---

## 2. Are Metrics Frozen?

**YES.**

The metric registry (phase8a_metric_registry.md) defines:
- 14 metrics with full formulas
- Primary metrics: M6, M1-C, M1-LR
- Secondary and exploratory metrics enumerated and cannot be promoted
- Statistical uncertainty procedures: 2,000-sample bootstrap, Bonferroni correction for 3 primary metrics
- Degenerate output handling procedures

**No metric may be added, removed, or redefined after framework evaluation begins.**

---

## 3. Are Success Criteria Frozen?

**YES.**

Phase8a_success_criteria.md defines:
- Exact numerical thresholds for SUCCESS, PARTIAL, FAILURE (before seeing any framework output)
- INCONCLUSIVE codes with specific conditions
- Failure-mode overrides (FO-1 through FO-5) with pre-specified triggers
- Reporting order requirements (verdict before narrative)

**Threshold derivation is documented.** Thresholds were set from first principles (theoretical performance of a working estimator, expected baseline performance) without knowledge of actual framework outputs.

---

## 4. Are Baselines Frozen?

**YES.**

Six baselines are fully specified (phase8a_baseline_spec.md):
- B1: Null (chance)
- B2: Marginal frequency prior
- B3: Pairwise correlation
- B4: Graphical lasso (with pre-specified alpha selection procedure)
- B5: State-dependent correlation difference
- B6: Module-membership oracle

**No baseline may be added after evaluation begins.** Failed baselines are excluded (not replaced or re-specified).

---

## 5. Is Label Leakage Prevented?

**YES, with acknowledged residual risks.**

### Structural barriers (enforced)
- labels.json: chmod 444, not in framework's input bundle
- A_sparse.npy: chmod 444, not in framework's input bundle
- H2 topology: not present in any observable file accessible to the framework
- Output freeze: framework outputs are hashed immediately after writing

### Audited vulnerabilities
14 vulnerabilities were identified in the leakage audit. None are P0. The most significant residual risks:

| Vulnerability | Severity | Risk |
|--------------|----------|------|
| V-E1 (module index) | P1 | Low; B6 comparison diagnostic |
| V-E8 (hyperparameter tuning) | P1 | Medium; cannot fully prevent prior familiarity |
| V-E11 (SAREACHABLE circularity) | P1 | Medium; B5 diagnostic targets this |
| V-E12 (M-class instability) | P1 | Medium; CI monitoring |
| V-E13 (near-zero C paths) | P1 | Medium; FO-2 override available |

**No P0 vulnerabilities remain unresolved.**

---

## 6. Can Framework Evaluation Begin?

**YES, conditionally.**

### Exit criteria check

| Exit criterion | Status |
|---------------|--------|
| EC-1: Evaluation inputs frozen | ✓ COMPLETE |
| EC-2: Evaluation outputs schema frozen | ✓ COMPLETE |
| EC-3: Metrics frozen | ✓ COMPLETE |
| EC-4: Baselines frozen | ✓ COMPLETE |
| EC-5: Success criteria frozen | ✓ COMPLETE |
| EC-6: Blinding protocol frozen | ✓ COMPLETE |
| EC-7: No unresolved P0 leakage | ✓ COMPLETE (0 P0 vulnerabilities) |

All 7 exit criteria are satisfied.

### Preconditions for Phase 8B

Before running the framework, Phase 8B must complete the following setup steps:

1. Implement evaluation harness (`scripts/phase8/evaluation_harness.py`) with:
   - Input bundle construction per eval spec §2.3
   - Output hash recording
   - Blinding checks BC-1 through BC-4
   - Metric computation per metric registry
   - Evaluation audit log

2. Implement baseline computation (`scripts/phase8/baselines.py`) for B1–B6

3. Implement metric computation (`scripts/phase8/compute_metrics.py`) for M1–M14

4. Verify that `results/phase8b/` output directory exists and has no prior content

5. Confirm frozen dataset integrity:
   - `ground_truth/labels.json` hash = `dc99697ec10309cc9a95880352d1e6c7f017b76942b541ad9ddf36e41f892081`
   - `results/phase7c/canonical/hashes.json` meta-hash = `7f398677135dcbcb3c0e114a64bc0e71a0a5afb54701872c99e79cbf34ad0aed`

Only after these setup steps are confirmed complete may the framework be provided with its first input bundle.

---

## 7. Risk Ranking Summary

### P0 Risks (Block Phase 8B)
**None.**

### P1 Risks (Require Monitoring)

| Risk | Monitoring action |
|------|------------------|
| V-E1 module leakage | Mandatory B6 comparison in report |
| V-E8 hyperparameter tuning | Framework developer disclosure statement |
| V-E11 SAREACHABLE circularity | B5 comparison is mandatory secondary metric |
| V-E12 M-class instability | Report M-AUROC CI width; flag if > 0.20 |
| V-E13 near-zero C paths | Report stratified C-AUROC (high-strength vs low-strength) as exploratory |

### P2 Risks (Monitor, No Action Required)
V-E2, V-E3, V-E4, V-E5, V-E6, V-E7, V-E9, V-E10, V-E14 — all mitigated by pre-registration structure.

---

## 8. Open Issues

**Issue 1 — Framework disclosure statement (P1)**  
The framework developer must disclose prior familiarity with the benchmark parameters before Phase 8B begins. Specifically: was the framework developed or tuned using any data with similar network parameters (P_WITHIN=0.15, P_BETWEEN=0.03, N_H2=8, GAMMA_H2=3.00)? This disclosure does not invalidate the evaluation but must be recorded.

**Issue 2 — Computation of B4 Glasso (P1)**  
The graphical lasso baseline (B4) requires fitting on 100-neuron data with 192,000 time points. This is a large computation. The pre-specified alpha grid must be used; no modification is permitted. If B4 fails to converge at any alpha, the failed alpha is excluded and BIC is computed over remaining alphas. If all alphas fail, B4 is excluded from comparison (noted in report; does not affect verdict).

**Issue 3 — Framework output format compliance (P1)**  
The framework must produce outputs that conform to the schema in eval spec §3.1. If the framework cannot produce class_prob summing to 1 for all 9,900 pairs, the degenerate-output handling procedure (metric registry §8) will be applied. This should be verified by the evaluation harness before blinding checks.

---

## 9. Phase 8A Document Inventory

| Document | Status |
|----------|--------|
| phase8a_evaluation_spec.md | FROZEN |
| phase8a_metric_registry.md | FROZEN |
| phase8a_baseline_spec.md | FROZEN |
| phase8a_success_criteria.md | FROZEN |
| phase8a_blinding_protocol.md | FROZEN |
| phase8a_evaluation_leakage_audit.md | FROZEN |
| phase8a_readiness_assessment.md | FINAL |

**Phase 8A is complete. Phase 8B may begin.**
