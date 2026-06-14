# Phase 9D — Preflight Report

**Date:** 2026-06-14  
**Status:** ALL CHECKS PASS — implementation authorized

---

## Oracle Integrity

| Check | Result |
|-------|--------|
| Oracle master hash | 79c98d032742ba36... VERIFIED |
| GT2_pmc_binary.npy | Hash matches manifest |
| DeltaOmega_true.npy | Hash matches manifest |
| GT3_oracle_rank_order.npy | Hash matches manifest |
| Total oracle files | 24 files, all hash-locked |

---

## Protocol Documents Read

| Document | Key frozen elements |
|----------|-------------------|
| phase9a_protocol.md | Benchmark objective, network design, PMC definition, metrics |
| phase9b_implementation_plan.md | Stage order, function signatures, audit checks |
| phase9b_audit_layer.md | LC-1–4, BV-4/5, CG-1, verdict isolation |
| phase9c_summary.md | Decision A (aligned), parameter addendum, master hash |

---

## A1–A7 Resolution

| ID | Resolution |
|----|-----------|
| A1 | D-only modulation — no z_high search required (D_HG_A=10.0, locked) |
| A2 | g_mod/g_base subsumed by D-only design — eliminated |
| A3 | PMC = expanded (181 pairs, both endpoints in PMC_SRC ∪ PMC_TGT) |
| A4 | Structural lesion = M1→M2 directed edges (24 edges removed) |
| A5 | T_A = T_B = 150,000 steps, dt=0.01, burn_in=10,000 |
| A6 | S label = A_obs[i,j]≠0 OR A_obs[j,i]≠0 (observed-observed block) |
| A7 | SpectralClustering(n_clusters=3, affinity='precomputed', random_state=42, n_init=20) |

---

## Precondition Status

| Condition | Status |
|-----------|--------|
| D1: PMC med > 2× non-PMC P90 | PASS (2758×) |
| D2: ≥60% of top-50 are PMC | PASS (50/50 = 100%) |
| AT-5: Oracle PMC_AUROC ≥ 0.90 | PASS (0.9983) |
| Oracle hash integrity | PASS |
| Network spec locked | PASS |
| Metrics pre-registered | PASS |

---

## Frozen Thresholds (verbatim from Phase 9B)

```
SUCCESS: Precision@50 ≥ 0.25  AND  ρ_Spearman ≥ 0.40  AND  PMC_AUROC ≥ 0.75
PARTIAL: at least one primary metric ≥ partial threshold (see below)
FAILURE: all primary metrics below partial thresholds

Partial thresholds: Precision@50 ≥ 0.10, ρ ≥ 0.15, PMC_AUROC ≥ 0.60
```

These thresholds are locked. No post-hoc adjustment permitted.

---

## Audit Layer Commitments

| Check | Commitment |
|-------|-----------|
| LC-1 | evaluate_framework.py must not import ground_truth module |
| LC-2 | Framework interface: evaluate_framework(x_A, x_B, A_obs) only |
| LC-3 | x_A.shape = (150000, 150) — no z(t) column |
| LC-4 | oracle_master_hash.txt timestamp < trajectory file timestamps |
| BV-4 | Oracle B4 AUROC = 0.9983 ≥ 0.90 — VERIFIED |
| BV-5 | A_obs cancellation error < 1e-8 — VERIFIED (1.1e-16) |
| CG-1 | PMC indices committed in network_spec.json BEFORE Lyapunov call |

---

## PREFLIGHT VERDICT

ALL 22 CHECKS PASS.

PROCEED TO STAGE 1: SIMULATOR IMPLEMENTATION.
