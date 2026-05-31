# Phase 2 Design Decisions Log

Status: **Empty at initialization**
Created: 2026-05-31
Phase 2 active: False

---

## Purpose

This log records the reasoning behind Phase 2 methodological decisions as they
are made. Each entry is written at the time the decision is authorized and is
immutable after recording.

Format:
```
## YYYY-MM-DD — [decision title]

Decision:
Context:
Alternatives considered:
Rationale:
Authorized by: human / [date]
Deviation record (if applicable): DEV-P2-NNN
```

---

## Open Questions at Initialization

The following questions must be resolved in Phase 2 Stage 0. They are
recorded here as placeholders, not as decisions.

  Q1 — Estimator class: Which estimator handles non-monotone recording-level
       missingness while producing a valid precision matrix? Candidates include
       pairwise GLASSO (assembled from pairwise sufficient statistics),
       EM-based covariance estimation, and node-wise pseudo-likelihood with
       masking. Not yet evaluated; not yet selected.

  Q2 — PSD guarantee: For the pairwise approach, is the assembled covariance
       matrix guaranteed positive semi-definite over the SF corpus neuron set?
       If not, what projection or correction is required, and what bias does
       it introduce?

  Q3 — Achievable neuron set: What is the largest neuron set for which every
       pair has sufficient co-observations for stable pairwise covariance
       estimation? This depends on the per-pair co-observation count distribution
       (not yet computed for Phase 2 planning).

  Q4 — Validation design: What synthetic missingness structure should Stage 0-V
       use? Options include: (a) exact SF missingness pattern replicated
       synthetically, (b) parametric model of the SF missingness structure,
       (c) bootstrap resampling of actual SF recording–neuron presence matrix.

  Q5 — Regime thresholds: What are the Phase 2 equivalents of the Phase 0
       n_eff/n_pairs viability thresholds? These must be established in
       Stage 0-V and cannot be assumed to equal the Phase 0 thresholds.

  Q6 — PRIMARY_TOP_K: With a potentially smaller neuron set (e.g., 13–61
       neurons), the locked PRIMARY_TOP_K=50 may exceed the number of
       off-connectome pairs. The enrichment test parameterization must be
       re-evaluated once the achievable neuron set is known.

---

## No Decisions Have Been Made

This log has no entries. No Phase 2 design decisions have been authorized.
The first entry will be made after the Stage 0 estimator-specification
checkpoint.
