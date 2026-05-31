# Phase 0 Operational Freeze

Date: 2026-05-29
PHASE0_COMPLETE = False
PHASE0_METHOD_LOCK_COMPLETE = True

---

## Status

Phase 0 operational files have been archived. The Phase 0 methodology is frozen.
This document records the transition from Phase 0 to Phase 1 preparation.

---

## Archived Operational Files

The following live operational files have been copied (unchanged) to
`docs/phase0/operational/` as immutable historical records:

| File | Archived as |
|---|---|
| `task.md` | `docs/phase0/operational/task.md` |
| `AGENTS.md` | `docs/phase0/operational/AGENTS.md` |
| `CHECKPOINT_LOG.md` | `docs/phase0/operational/CHECKPOINT_LOG.md` |
| `CONTEXT.md` | `docs/phase0/operational/CONTEXT.md` |
| `PROGRESS.md` | `docs/phase0/operational/PROGRESS.md` |

The originals at repo root remain active and may continue to be updated.
The copies in `docs/phase0/operational/` reflect the state at the time of archival
and should be treated as read-only historical records.

---

## Phase 0 Methodology Frozen

All methodological choices recorded in `phase0_config.py` are frozen:

- Subgraph: N_COMMON_NEURONS=61, LR_POLICY="separate"
- Behavioral threshold: BEHAV_THRESHOLD=0.284, EWMA=20s, W_TRANS=10s
- Estimators: pooled_hierarchical, stability_selection + anatomy_guided_lasso
- Enrichment: AUROC primary, simple_permutation null
- Hypothesis: locked (see docs/phase0/hypothesis_lock.md)

These values must not be changed without human authorization and a new
CHECKPOINT_LOG entry.

---

## phase0_config.py Remains Authoritative

`phase0_config.py` (repo root) is the single source of truth for all Phase 0
parameters. It will remain the authoritative configuration file for:

- All Phase 0 guardrail checks (PHASE0_COMPLETE, PHASE0_METHOD_LOCK_COMPLETE)
- All locked methodological values
- All frozen estimator and enrichment parameters

Do NOT rename it. Do NOT create `phase1_config.py` without explicit human authorization.

---

## Future Work Uses Phase 1 Operational Files

Once Phase 1 planning is authorized, future sessions should use:

| File | Purpose |
|---|---|
| `PHASE1_PROGRESS.md` | Phase 1 progress tracking |
| `PHASE1_CHECKPOINT_LOG.md` | Phase 1 checkpoints |
| `PHASE1_CONTEXT.md` | Phase 1 context notes |
| `PHASE1_STARTER_MANIFEST.md` | Phase 1 entry point and reference |

Phase 0 operational files (`PROGRESS.md`, `CHECKPOINT_LOG.md`, `CONTEXT.md`) may
continue to be updated for continuity, but the Phase 1 files are the primary
operational record going forward.

---

## Guardrail Remains Active

```python
PHASE0_COMPLETE = False             # real-data precision BLOCKED
PHASE0_METHOD_LOCK_COMPLETE = True  # methodology frozen
```

The guardrail in `src/estimators.py` remains active. Real-data precision estimation
raises `RuntimeError`. 27/27 tests pass.
