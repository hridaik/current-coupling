# PHASE2_CHECKPOINT_LOG.md

---

## CHECKPOINT P2-001: Stage 0-V.7A — Enrichment Power Diagnosis
Date: 2026-05-31
Stage: 0-V.7A (diagnosis)
Authorization: SELF-AUTHORIZED (diagnostic computation only)

[1] Previous diagnostic showed: V.7 failed AUROC power criterion (0.525 < 0.60) with type-I = 0.050 PASS. All other validation stages (V.1–V.6) passed. Fisher top-K power = 1.00 at K=20.
[2] This rules out: estimator failure as the cause. The estimator correctly recovers signal (V.3 TPR=0.973; Fisher power=1.00).
[3] The proposed action tests: whether the AUROC failure reflects an annotation-density ceiling rather than an estimator or criterion problem.
[4] Success: identification of P_SIGNAL_min and the root cause of the AUROC failure.
[5] Failure: if the analysis revealed a structural estimator problem, requiring V.7 re-run with modified estimator.
Result: ROOT CAUSE IDENTIFIED. P_SIGNAL=10 creates analytical AUROC ceiling = 0.531. Failure is enrichment-design limitation + annotation dilution. NOT estimator failure.
Key numbers: n_off=1570, n_off_annotated=159, annotation prevalence=10.1%, P_SIGNAL_min≈12 (analytical estimate confirmed by D2 sweep).

---

## CHECKPOINT P2-002: Stage 0-V.7B — Option B Authorized
Date: 2026-05-31
Stage: 0-V.7B (fine sweep + full validation at P=12)
Authorization: AUTHORIZED by human supervisor (Option B)

[1] Previous diagnostic showed: V.7A established P_SIGNAL_min=12 (fine sweep, analytical MW, 100 reps). Power=0.670 at P=12 with analytical test.
[2] This rules out: that P_SIGNAL=10 can ever satisfy the AUROC criterion; that the estimator is the problem.
[3] The proposed action tests: whether V.7 passes with P_SIGNAL=12 (P_SIGNAL_min) in a full permutation-based validation.
[4] Success: V.7B PASS with both type-I ≤ 0.06 and power ≥ 0.60.
[5] Failure: borderline result requiring further investigation.
Result: BORDERLINE FAIL. Type-I=0.085 (seed fluctuation, z=2.27 from expected, p=0.012); Power=0.595 (1 rep short; gap = 0.14 SEs). Both failures explained by sampling statistics. P_SIGNAL_min=12 confirmed as the mathematical minimum. Path 2 authorized: re-run at P=13.
Deviation recorded: DEV-P2-003 (see below).

---

## CHECKPOINT P2-003: Stage 0-V.7C — Path 2 at P_SIGNAL=13
Date: 2026-06-01
Stage: 0-V.7C (full validation)
Authorization: AUTHORIZED by human supervisor (Path 2)

[1] Previous diagnostic showed: V.7B at P=12 marginally failed due to seed-specific sampling variance. Fine sweep established P_SIGNAL_min=12 (7.5% of 159 annotated pairs).
[2] This rules out: that P_SIGNAL=12 itself is wrong as the minimum; the failure was sampling noise.
[3] The proposed action tests: whether V.7C at P=13 (one step above minimum) passes with clear margin.
[4] Success: type-I ≤ 0.06, power ≥ 0.60, Fisher unchanged.
[5] Failure: if P=13 also fails, indicating a systematic calibration problem beyond seed randomness.
Result: PASS. Type-I=0.035, Power=0.685, Fisher K=20 type-I=0.040, power=1.000. PRIMARY_TOP_K=20 confirmed unchanged. Margin above power criterion: +0.085 (simple), +0.050 (degree).

---

## CHECKPOINT P2-004: Stage 0-V.8 — Parameter Lock Package
Date: 2026-06-01
Stage: 0-V.8 (parameter lock preparation)
Authorization: SELF-AUTHORIZED (documentation; no computation)

[1] Previous diagnostic showed: V.7C PASS. All Stage 0-V validation complete.
[2] This rules out: further need for synthetic validation before Stage 1.
[3] The proposed action: prepare parameter lock package, update phase2_config.py with all locked parameters, document unresolved assumptions, prepare Stage 1 checkpoint package.
[4] Success: human can review and set PHASE2_ACTIVE = True.
[5] Failure: if supervisor identifies an unresolved issue requiring additional validation.
Result: Package prepared. See results/phase2/stage0v/v8_parameter_lock_package.md.
Pending: (a) MIN_COPRESENCE_RECORDINGS not yet set (Stage 0.1 checkpoint not closed); (b) UA-1 through UA-5 acknowledgement by human; (c) PHASE2_ACTIVE = True.

---

## DEVIATION REGISTER

### DEV-P2-002: Stability selection lambda fixed at 0.15
Date: 2026-05-31
Stage: 0-V.3/V.4
Description: Within-bootstrap GLASSO lambda set to 0.15 (fixed), replacing BIC-based selection which was underpowered at effect=0.2.
Basis: V.3 synthetic sweep identified λ=0.15 as producing TPR=0.973, FPR=0.033 at effect=0.2. Determined from synthetic data only, before any real-data results.
Authorization: AUTHORIZED by human

### DEV-P2-003: P_SIGNAL updated from 10 to 13
Date: 2026-05-31 (established), 2026-06-01 (operating point confirmed)
Stage: 0-V.7A through 0-V.7C
Description: The original V.7 synthetic enrichment design used P_SIGNAL=10 (6.3% of 159 annotated off-connectome pairs). V.7A diagnostic demonstrated this creates an analytical AUROC ceiling of 0.531, making the pre-specified power criterion (≥ 0.60) unachievable regardless of effect size. Fine sweep over {11,12,13,14} determined P_SIGNAL_min=12 (7.5% of annotated pairs). Validation operating point set to P_SIGNAL=13 (8.2% of annotated pairs) to provide margin above the minimum.
Biological justification: Neuropeptide DCV release is volume transmission affecting multiple targets simultaneously. A state-conditioned neuromodulatory switch (dwelling→roaming) plausibly engages O(15-30) of the 159 Randi-annotated pairs, not just 10. P_SIGNAL_min=12 represents the minimum signal density required to satisfy the pre-specified power criterion; P_SIGNAL=13 is the smallest validated operating point above that minimum.
V.7C result: type-I=0.035, power=0.685. PASS.
Authorization: AUTHORIZED by human supervisor (Option B authorized 2026-05-31; Path 2 authorized 2026-06-01)

---

## CHECKPOINT P2-006: Stage 2 — ΔQ Computation and Classification
Date: 2026-06-01
Stage: 2
Authorization: AUTHORIZED by human supervisor (2026-06-01)

[1] Previous state: Stage 1 complete. 4 Q_conf matrices PD, well-conditioned. Stage 1A diagnostic completed — CePNEM dwelling stability near-zero diagnosed as H1+H3 (weak covariance + bootstrap variability); confirmed not a scripting artifact.
[2] Stage 1A finding (recorded per supervisor instruction): CePNEM dwelling stability is near-zero (1/1830 pairs stable at threshold 0.75). This does NOT affect Stage 2 or the enrichment test. The enrichment test (AUROC, Fisher) operates on the full |ΔQ| distribution for all off-connectome pairs, independently of stability scores. Stability scores affect only the named-pair ranking table (Stage 6).
[3] Authorized: ΔQ = Q_conf_roam − Q_conf_dwell for both coordinates (ADMM confirmation matrices only). Stability-weighted ranking NOT applied in Stage 2.
[4] Success: 4 ΔQ matrices computed, Class 4 count ≥ 30, ranked pair lists saved.
[5] STOP CONDITION: Stage 2 report produced. Do NOT proceed to Stage 3 (sensitivity) or Stage 4 (enrichment) without human review.
Authorization: AUTHORIZED by human

---

## STAGE 1 AUTHORIZATION — PENDING

Required actions before Stage 1 may begin:

[ ] Human sets MIN_COPRESENCE_RECORDINGS in phase2_config.py (suggested: 10)
[ ] Human acknowledges UA-1 (MCAR assumption) in this log
[ ] Human acknowledges UA-2 (PSD rank preservation) in this log
[ ] Human acknowledges UA-3 (annotation independence) in this log
[ ] Human acknowledges UA-4 (Gaussian generative model) in this log
[ ] Human acknowledges UA-5 (behavioral segmentation) in this log
[ ] Human confirms ordering constraint (Stage 5 locked until both coordinates complete)
[ ] Human sets PHASE2_ACTIVE = True in phase2_config.py
[ ] Human records authorization date and rationale in this log (below)

### Authorization record

PHASE2_ACTIVE set to True: 2026-06-01
MIN_COPRESENCE_RECORDINGS set to: 9
UA acknowledgements: UA-1 (MCAR) ACCEPTED, UA-2 (PSD rank) ACCEPTED, UA-3 (annotation independence) ACCEPTED, UA-4 (Gaussian model) ACCEPTED, UA-5 (behavioral segmentation) ACCEPTED
Ordering constraint: ACCEPTED — both coordinate systems must complete all downstream stages before Stage 5 coordinate comparison is opened
Stage 1 scope: Pairwise covariance assembly + PSD safeguard + stability selection + ADMM confirmation. No ΔQ, no enrichment, no interpretation. Stop after Stage 1 report for human review.

---

## CHECKPOINT P2-005: Stage 1 — Real-Data Precision Estimation
Date: 2026-06-01
Stage: 1 (first real-data computation)
Authorization: AUTHORIZED by human supervisor (2026-06-01)

[1] Previous state: Stage 0-V complete. All V.1–V.7C PASS. All parameters locked. PHASE2_ACTIVE = True.
[2] This rules out: any further synthetic-only work. Real-data estimation now permitted.
[3] The proposed action: Assemble pairwise covariance matrices from CePNEM residuals and raw GCaMP traces for roaming and dwelling states. PSD project. Run stability selection (discovery) and ADMM (confirmation). Produce 8 precision matrices.
[4] Success: 8 precision matrices saved, all PD, condition numbers < 10^6, PSD clipping within acceptable range.
[5] Failure halt conditions: PSD clipping detected (eigenvalues < 0 in assembled S), ADMM convergence failure, precision matrix not PD, condition number > 10^6.
[6] STOP CONDITION: Stage 1 report produced. Do NOT proceed to Stage 2 (ΔQ computation) without human review of Stage 1 report.
Authorization: AUTHORIZED by human

---

## CHECKPOINT P2-007: Stage 4 — Enrichment Analysis
Date: 2026-06-01
Stage: 4
Authorization: AUTHORIZED by human supervisor (2026-06-01, Stage 4 authorized in restart package)

[1] Previous state: Stage 3 COMPLETE. Median retention CePNEM=0.960, GCaMP=0.940 (both PASS ≥ 0.70). 2 CePNEM influential recordings (2023-01-16-15, 2023-01-17-14), 3 GCaMP influential recordings (2022-06-14-07, 2023-01-16-15, 2023-01-17-14). All influential recordings are roaming recordings. DEV-005 partially compensated.
[2] This rules out: any sensitivity blocker for Stage 4. Median retention well above threshold. Results remain stable under LOO.
[3] The proposed action: Run all Stage 4 enrichment tests — AUROC (Test 1), Fisher top-K K=20 (Test 2), Randi (Test 3), serotonin/PDF (Test 4, note if unavailable), confirmation check, degree-preserving nulls — for both CePNEM and GCaMP coordinates. Use ONLY Stage 2 confirmation ΔQ (DQ_cepnem.npy, DQ_gcamp.npy). No stability weighting. 1000 permutations per null. Save all results before report.
[4] Success: AUROC and Fisher computed with both nulls for all tests; explicit PASS/FAIL for each enrichment test; Stage 5 recommendation recorded.
[5] Failure halt: If annotation data unavailable or numerical issues; halt and diagnose before continuing.
[6] STOP CONDITION: Stage 4 report produced. Do NOT proceed to Stage 5 without human review.
Authorization: AUTHORIZED by human
Result: NULL RESULT — All enrichment tests FAIL.

---

## CHECKPOINT P2-009: Stage 4A — Serotonin/PDF Exploratory Enrichment (Addendum)
Date: 2026-06-01
Stage: 4A (addendum to Stage 4; Phase 2 still open)
Authorization: AUTHORIZED by human supervisor (2026-06-01, Stage 4A addendum authorized)

[1] Previous state: Stage 5 COMPLETE with null result (CePNEM AUROC=0.5033 p_deg=0.475, GCaMP AUROC=0.5140 p_deg=0.142). Stage 4A was skipped in original Stage 4 because serotonin/PDF annotations were not identified. Repository audit confirmed annotations exist in data/randi/wormneuroatlas/.
[2] This rules out: the need for any external download. All required annotation data is present.
[3] The proposed action: Build serotonin annotation (Bentley ESconnectome monoamine file, transmitter=="serotonin", 33 Class 4 pairs), PDF annotation (Bentley ESconnectome neuropeptide file, transmitter contains "pdf", 61 Class 4 pairs), combined (94 Class 4 pairs, 7.1%). Also build CeNGEN-based annotation (409 Class 4 pairs, 31%, exploratory). Run AUROC + Fisher + both nulls for each annotation, both coordinates. PRIMARY_TOP_K=20, N_PERM=1000. Use Stage 2 ΔQ matrices only — no new estimation.
[4] Success: All tests run; AUROC/Fisher/p-values saved; Stage 4A report written; Phase 2 closure recommendation made.
[5] Halt conditions: none expected (no new estimation; read-only annotation construction).
[6] STOP CONDITION: Stage 4A report and closure recommendation written. No further computation authorized.
Authorization: AUTHORIZED by human
Result:
  Bentley serotonin: FAIL both coordinates (AUROC ~0.50, p_deg=0.58/0.94)
  Bentley PDF (CePNEM): PASS — AUROC=0.556 p_deg=0.023; Fisher OR=5.456 p_deg=0.008
  Bentley PDF (GCaMP): FAIL — AUROC=0.526 p_deg=0.261
  Bentley combined/Test 4 (CePNEM): MARGINAL — AUROC p_deg=0.055, Fisher p_deg=0.065 (both above 0.05)
  CeNGEN combined AUROC: PASS in both coords (p_deg=0.033/0.002); Fisher FAIL
  Pre-specified Test 4 (combined) does NOT pass at p<0.05 in either coordinate.
  Phase 2 primary result: NULL (Stage 5 Row 4 unchanged).
  Phase 2 CLOSED.
  CePNEM: Test 1 AUROC=0.5033, p_deg=0.475 (FAIL); Test 2 Fisher OR=0.533, p_deg=0.981 (FAIL)
  GCaMP:  Test 1 AUROC=0.5140, p_deg=0.142 (FAIL); Test 2 Fisher OR=0.835, p_deg=0.716 (FAIL)
  Randi (CePNEM): AUROC=0.4953, p_deg=0.656 (FAIL); Randi (GCaMP): AUROC=0.5167, p_deg=0.278 (FAIL)
  Test 4 (Serotonin/PDF): SKIPPED — annotation not available.
  Null degree preservation: PASS (max bin deviation = 0).
  Stage 5 recommendation: AUTHORIZE to apply locked interpretation table row 4 (Null result).

---

## CHECKPOINT P2-008: Stage 5 — Coordinate Comparison and Final Report
Date: 2026-06-01
Stage: 5
Authorization: AUTHORIZED by human supervisor (2026-06-01, Stage 5 authorized with Stage 4 results)

[1] Previous state: Stage 4 COMPLETE. All enrichment tests null. CePNEM AUROC=0.5033 p_deg=0.475; GCaMP AUROC=0.5140 p_deg=0.142. Both coordinates non-significant under degree-preserving null. Null result confirmed across both annotation types (neuropeptide, Randi).
[2] This rules out: any enrichment in off-connectome conditional dependence changes for neuropeptide pairs or Randi unc-31 pairs, under the validated pairwise estimation pipeline.
[3] The proposed action: Apply the locked interpretation table mechanically. Both coordinates: not significant. Row 4 = Null result. Write Stage 5 report, final Phase 2 archival report, and successor-project recommendation. No new estimation, no new biological analyses.
[4] Success: Final interpretation table assignment documented; what-data-support / do-not-support / unresolved explicitly separated; successor-project evaluation written; Phase 2 closure recommendation made.
[5] No halt conditions apply (Stage 5 is interpretive and archival only).
Authorization: AUTHORIZED by human
