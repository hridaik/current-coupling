# Phase 3C Summary
Date: 2026-06-03
Authorization: Phase 3C
Status: COMPLETE — awaiting human review

---

## Phase 3C Goal (Recapitulation)

Determine whether the current organization Ω = D Q + A reveals information
about state-dependent functional connectivity that is absent from ΔQ alone.

The theoretical motivation: Q = D^{-1}(Ω − A), so Ω rescales Q by per-neuron
noise variance D and adds anatomical baseline A. If D is non-uniform, Ω
up-weights high-noise neurons and might reveal different structure than ΔQ.

---

## Outcome: C — Essentially Equivalent to ΔQ

**ΔΩ provides no new information beyond ΔQ in this dataset.**

This outcome follows directly from two structural properties of the data:

1. **D is near-uniform**: CePNEM z-scoring forces per-neuron residual
   variance ≈ 1.0. The actual D2 range is [0.943, 1.096] (within ±8%),
   meaning ΔΩ ≈ 1.025 × ΔQ as a near-constant scaling.

2. **A cancels exactly**: ΔΩ = D·ΔQ regardless of A (since A is
   state-independent and subtracts out). No information is lost or gained
   by including A.

---

## Answers to Required Questions

### 1. What did Ω add beyond ΔQ?

Nothing, for the state-difference ΔΩ.

Mathematically: ΔΩ = D · ΔQ. With D near-uniform (CV ≈ 3%), this is
a constant rescaling. Spearman rank correlation between |ΔΩ_D2| and |ΔQ|
is 0.9999932 — indistinguishable from 1.0 at any practical precision.

A non-uniform D would in principle reveal different structure by upweighting
high-noise neurons. That leverage does not exist here because z-scoring
removed the variance differences.

### 2. Did PDF enrichment strengthen, weaken, or remain unchanged?

**Unchanged.**

| Framework | PDF AUROC |
|---|---|
| ΔQ (Phase 2 result) | 0.5560 |
| ΔΩ_D1 | 0.5560 |
| ΔΩ_D2 | 0.5563 |
| ΔΩ_D3 | 0.5566 |

The maximum change across all D models is +0.0006. The PDF enrichment
signal established in Phase 2 (AUROC = 0.556, significant for 61-pair
subgraph) is exactly preserved in Ω-space — because ΔΩ is ΔQ rescaled.

### 3. Did ADEL-related pairs become more prominent?

**No.**

ADEL held-out pairs maintain identical ranks in ΔΩ vs ΔQ:

| Pair | ΔQ rank | ΔΩ_D2 rank | Change |
|---|---|---|---|
| ADEL–URYVR | 5 | 5 | 0 |
| ADEL–URYDL | 9 | 9 | 0 |
| ADEL–RMEL | 10 | 10 | 0 |
| ADEL–URXL | 59 | 58 | −1 |

The −1 rank change for ADEL–URXL is a numerical tie-breaking artifact.
No ADEL pair moved more than one position.

### 4. Did Ω reveal any hidden structure not visible in Phase 2?

**No.**

Only 1 pair appeared in the top-200 ΔΩ_D2 but not in the top-200 ΔQ:
RMEL–URYVL (ΔΩ_D2 = −0.0052, ΔQ = −0.0049). This is a rank-borderline
case at position ≈200, not a substantive new signal.

The blockwise attribution (cC) confirms this: the dominant block flows in
ΔΩ (DA_mech↔URY_URX, RME↔RME, RID↔IL1_IL2) are identical to those that
would be inferred from ΔQ. No block pair that was silent in ΔQ became
prominent in ΔΩ.

### 5. Does the Ω pathway justify further development?

**No.**

The Ω formulation was motivated by the possibility that ΔΩ would highlight
current-supported connections not apparent in ΔQ. That possibility is
foreclosed by the near-uniform D arising from CePNEM z-scoring.

Further development of the Ω pathway would require either:
(a) Operating on un-z-scored data to recover non-uniform D — which would
    require re-running all Phase 2 estimations; or
(b) A different definition of D (e.g., from biophysical noise models) that
    produces substantially non-uniform weights.

Neither is warranted given the current evidence.

---

## Blockwise Structure (cC Synthesis)

The blockwise attribution in cC — the one genuinely new analysis angle in
Phase 3C — confirms and extends Phase 2, but does not contradict it.

**Key blockwise finding**: DA_mech (ADEL+CEP) ↔ URY_URX is the second-largest
block flow by mean |ΔΩ| (0.027 over 12 Class 4 pairs) and the largest
multi-pair block flow by aggregate signal (sum |ΔΩ| = 0.33). This establishes
that the dopaminergic mechanosensory → aerotaxis/O₂-sensor pathway undergoes
the most extensive state-dependent reorganization of any cross-module connection
in the 61-neuron subgraph.

This is consistent with Phase 2 (ADEL→URYVR rank 5, ADEL→URYDL rank 9) but
adds interpretive resolution: the signal is not just two strong pairs but a
systematic module-level decoupling across 12 pairs.

The RME↔RME block (RMEL–RMER bilateral coupling, rank 1 by mean |ΔΩ|) is the
single highest-signal pair, consistent with Phase 2 (RMEL–RMER rank 1 in D3
contribution map).

---

## Critical Interpretation: Did ΔΩ ≈ constant × ΔQ?

**Yes. This is the central finding of Phase 3C.**

The original motivation was Q = D^{-1}(Ω − A), suggesting Ω could carry
structure invisible in Q by reversing the D weighting. In practice:

- ΔΩ = D · ΔQ (exact cancellation of A)
- D is near-constant (~1.025 ± 3% for D2, ~0.405 ± 10% for D3)
- Therefore ΔΩ ≈ 1.025 × ΔQ (constant rescaling, rank-invariant)

The Ω pathway is **not** a richer representation — it is a renaming of ΔQ
with a negligible reweighting. The theoretical pathway from Ω to new
biological insight exists mathematically but is blocked empirically by
the z-scoring of the input data.

---

## What Phase 3C Achieved

Despite the null finding on new information, Phase 3C provides two positive
contributions:

1. **Validation**: The cA/cB robustness confirmation shows that the Phase 2
   ΔQ results are stable across all noise-model assumptions. The top-20 pairs
   (including ADEL–URYVR, ADEL–URYDL, ADEL–RMEL) are robust across D1, D2, D3.

2. **Block-level resolution**: The cC blockwise attribution identifies
   DA_mech↔URY_URX as the dominant multi-pair reorganization pathway, providing
   a systems-level context for the pairwise Phase 2 findings. This framing
   may be useful for experimental follow-up (targeting the ADEL/CEP → URY/URX
   module as a functional unit).

---

## Output File Index

| File | Status |
|---|---|
| omega_models.json | Complete |
| cA_omega_robustness.md | Complete |
| cB_deltaOmega.md | Complete |
| cC_blockwise_attribution.md | Complete |
| cD_sensitivity.md | Complete |
| phase3c_summary.md | This file |
| phase3c_decision_memo.md | See companion file |

---

*Phase 3C: STOP. Awaiting human review.*
*DO NOT: start new model families, revisit Phase 3A, generate perturbation predictions, evaluate held-out ADEL pairs.*
