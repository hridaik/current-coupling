# Phase 3C Decision Memo
Date: 2026-06-03
Authorization: Phase 3C

---

## Recommendation

[x] **Terminate Ω pathway**
[ ] Continue Ω pathway

---

## Justification

### The core question

Phase 3C asked whether Ω = D Q + A provides information absent from ΔQ.
Specifically: does the current organization Ω, via its D-weighting of Q,
reveal connectivity structure that ΔQ alone would miss?

### The answer

**No. ΔΩ = D · ΔQ exactly, and D is near-uniform in this dataset.**

This is not a null result from insufficient power — it is a structural result
from the preprocessing of the input data.

### Evidence for termination

**1. Mathematical: A cancels, D is near-identity**

ΔΩ = Ω_roam − Ω_dwell = D·Q_roam + A − D·Q_dwell − A = D·ΔQ

The anatomical baseline A is state-independent and eliminates exactly.
The remaining D factor is near-uniform because CePNEM z-scoring forces
per-neuron residual variance ≈ 1.0 across all 61 neurons (D2 range:
0.943–1.096, CV = 3%).

Therefore ΔΩ ≈ 1.025 × ΔQ — a constant scaling with no discriminative
content.

**2. Empirical: Rankings are identical (ρ > 0.9999)**

| Comparison | ρ |
|---|---|
| ΔΩ_D1 vs ΔQ | 1.0000 |
| ΔΩ_D2 vs ΔQ | 1.0000 |
| ΔΩ_D3 vs ΔQ | 0.9999 |

No choice of D model — identity, residual variance, or first-difference
variance — produces a materially different ranking of Class 4 pairs.

**3. No new signal: PDF AUROC and ADEL ranks unchanged**

PDF AUROC: 0.5560 (ΔQ) → 0.5566 (ΔΩ_D3, the largest change). Δ = +0.0006.
ADEL–URYVR: rank 5 in both ΔQ and ΔΩ. ADEL–URYDL: rank 9 in both.

The Phase 2 findings are exactly reproduced in Ω-space, not enhanced.

**4. A choice is irrelevant**

Spearman ρ(ΔΩ_Araw, ΔΩ_Acreamer) = 1.0000 for any D.
A does not enter ΔΩ.

**5. Pathway to non-trivial Ω requires fundamentally different inputs**

For ΔΩ to diverge from constant × ΔQ, D must be substantially non-uniform.
This requires abandoning CePNEM z-scoring (a core preprocessing step) or
adopting a biophysical noise model with large neuron-to-neuron variation.
Neither is justified by the current evidence base, and neither has been
authorized.

### What Phase 3C did achieve (not grounds for continuation)

1. **Robustness validation**: Phase 2 ΔQ top-20 is stable across all D
   and A choices. This strengthens confidence in the Phase 2 ADEL predictions
   but does not create a new pathway.

2. **Block-level resolution (cC)**: DA_mech↔URY_URX is the dominant
   multi-pair reorganization pathway (12 Class 4 pairs, mean |ΔΩ| = 0.027).
   This is a Phase 2 interpretive extension, not a new Ω-specific discovery.
   The same block structure is present in ΔQ.

### What this memo does NOT decide

- Whether the Phase 2 ADEL predictions (ADEL→URYVR, ADEL→URYDL) should
  be advanced. Phase 2 conclusions stand on their own.

- Whether the held-out ADEL evaluation should proceed. That decision belongs
  to the Phase 3A evaluation criterion (pending human review per Phase 3A
  stop condition).

- Whether alternative Ω formulations (raw fluorescence D, biophysical models)
  are worth exploring in a future phase. The current data cannot answer that.

---

## Conclusion

The Ω pathway, as implemented with CePNEM-processed data, collapses to
ΔΩ ≈ constant × ΔQ. The theoretical hope that Ω would reveal
current-supported structure absent from ΔQ is not realized in this dataset.
Continuing the Ω pathway would duplicate existing ΔQ analysis without adding
scientific content.

**Phase 3C is complete. Terminate Ω pathway. Await human review.**
