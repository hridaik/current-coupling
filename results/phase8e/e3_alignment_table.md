# E3: Theory–Benchmark Alignment Table

**Phase**: 8E — Label-Definition Audit  
**Date**: 2026-06-14  
**Constraint**: No label modifications. Analysis only.

---

## Alignment Structure

The paper defines two core link classes (Structural, Current-supported) and an implicit Null class. The benchmark defines four classes (S, C, M, N) and one composite (LR). This document evaluates the correspondence.

---

## Primary Alignment Table

| Paper object | Benchmark label | Alignment | Key gaps |
|-------------|----------------|-----------|---------|
| Structural link | **S** | EXACT | — |
| Current-supported link | **C** | PARTIAL | See below |
| Null (neither) | **N** | PARTIAL | N is off-connectome; paper null is not restricted to off-connectome |
| — | **M** | NOT SAME | No direct paper analog exists |
| Primary detection target | **LR** | PARTIAL | LR includes on-connectome M pairs |

---

## Detailed Alignment: S ↔ Structural

**Verdict: EXACT**

| Property | Paper's structural | S-label |
|----------|-------------------|---------|
| Direct anatomical coupling | A_raw(i,j) ≥ 1 | A_sparse[i,j] ≠ 0 ∨ A_sparse[j,i] ≠ 0 |
| State-independent | Yes — anatomy doesn't change between states | Yes — SAREACHABLE=0, no H2 relay |
| Detectable by partial correlation | Yes — directly connected pairs have high PCor | Yes — S-AUROC=0.8531, confirming detection |

**Qualification**: The paper's "structural" uses a real anatomical connectome (synapse counts, electron microscopy). The benchmark uses a randomly sampled sparse coupling matrix (drawn from the same model). Both capture the same property (direct coupling that does not require state modulation), and both are detectable by the same method (high partial correlation). The S class is a faithful operationalization.

---

## Detailed Alignment: C ↔ Current-supported

**Verdict: PARTIAL — two specific gaps**

### Properties that match

| Property | Paper's current-supported | C-label | Match? |
|----------|--------------------------|---------|--------|
| Off-connectome | A_raw(i,j)=0 (no direct anatomical synapse) | DIRECT=0 (A_sparse[i,j]=0) | EXACT ✓ |
| State-modulated in principle | ΔQ ≠ 0 between states | SAREACHABLE=1 (H2 relay exists) | STRUCTURAL ✓ (topology guarantees a mechanism, not an observation) |
| Observable | Measured in calcium imaging | Present in oracle runs (B5 C-AUROC=0.5517) | CONFIRMED ✓ |
| Enriched for non-synaptic signaling | Class 4 enriched for neuropeptides | No direct analog in benchmark | N/A |

### Gap 1: Topological proxy ≠ observed signal

The paper's "current-supported" is an **observed** property: ΔQ is computed from data and must be statistically significant. The benchmark's C label is a **topological** property: it requires only that the structural path exists, not that it produces detectable signal.

Consequence:
- ~28% of C pairs have path_strength < 0.01 — the H2-mediated coupling is sub-threshold
- Even well-supported C pairs show wide |ΔCorr| variation (p10=0.024, p90=0.091)
- The label assigns C status to pairs that may not exhibit observable ΔQ under finite sampling

**Magnitude of gap**: 
- D3 confirmed C pairs ARE enriched for state-sensitive signal on average (1.18× over-represented in top |ΔCorr| quartile)
- Even the weakest C subset is tested by a framework that fails for ALL C pairs (including strong C AUROC=0.4069)
- This gap matters for benchmark validity but does not explain the framework failure

### Gap 2: Hidden common cause ≠ probability current

The paper's theoretical object involves **probability current** circulation:

```
J_ij = Q_ij − Q_ji  where Q = Ω D
```

For this quantity to change between states (ΔQ ≠ 0), the CONDITIONAL directed influence between i and j must change — which requires changes in the precision matrix Ω entries that are asymmetric.

The benchmark's C mechanism is a **hidden common cause**:
- Both i and j receive inputs from h (via A[h,i] and A[j,h])
- At high z: h is additionally driven by z(t), increasing h's activity and amplifying the i→h→j relay AND the shared h-drive to both i and j
- The pair (i,j) gains correlation from: (a) the relay i→h→j AND (b) the shared drive z→h→(i,j)

Per Phase 6A review, W7: *"The probability current between two neurons jointly driven by a common unobserved source need not involve nonequilibrium circulation. H2 creates a confounding effect, not a current-supported effect in the thermodynamic sense."*

This is the definitional misalignment:
- Paper: current-supported links have ΔQ ≠ 0 (directed probability current changes between states)
- Benchmark C: pairs have a topological H2-relay (confounding structure; common hidden cause)

**These are not equivalent.** A common cause creates symmetric covariance (both i and j respond to h), not directed current. A current-supported link creates asymmetric directed flow (i→j flow exceeds j→i flow in one state but not another).

**Magnitude of gap**: 
- The benchmark C mechanism creates SYMMETRIC ΔΩ (both i and j respond to h symmetrically through h's activity boost)
- The paper's ΔQ = ΔΩD is non-symmetric when D is diagonal (uniform): ΔQ_ij = ΔΩ_ij × D_jj, ΔQ_ji = ΔΩ_ji × D_ii
- For a common-cause structure (H2→i and H2→j), the Ω off-diagonal entries ΔΩ_ij ≈ ΔΩ_ji (symmetric), so ΔQ_ij ≈ ΔQ_ji
- **The benchmark's C mechanism primarily creates symmetric ΔΩ (common cause), not asymmetric ΔQ (current)**

This means the C class tests correlation/covariance structure changes, not probability current changes. The distinction matters more for theoretical precision than for the framework failure diagnosis: the framework's C-score (Delta_PCor) measures ΔΩ, not ΔQ — so it is also measuring the wrong quantity (but a different wrong quantity than what the labels test).

---

## Detailed Alignment: N ↔ Null

**Verdict: PARTIAL**

| Property | Paper's null | N-label |
|----------|-------------|---------|
| No direct coupling | Varies (includes on-connectome pairs not targeted) | DIRECT=0 (always off-connectome) |
| No state-dependent signal | No ΔQ between states | No H2 relay (SAREACHABLE=0) |
| Serves as negative control | Background correlation | Background correlation from non-SA neurons |

**Gap**: N pairs are restricted to off-connectome pairs (DIRECT=0). In the paper's framework, the null class includes both on-connectome AND off-connectome pairs without state-dependent signals. The benchmark excludes on-connectome non-SAREACHABLE pairs from N — those are class S. So the benchmark N is a subset of the paper's null class.

**Practical impact**: Because the framework's C-vs-N AUROC computes ranks among all non-C pairs (not just N), this distinction is mainly conceptual. The discrimination challenge is C vs. N, where N pairs lack H2-relay and C pairs have one.

---

## Detailed Alignment: M ↔ No paper analog

**Verdict: NOT SAME**

The M class (DIRECT=1, SAREACHABLE=1) has no direct analog in the paper's framework:
- It is "structural" by the primary direct-coupling criterion
- But it also has state-modulated H2-relay

In the worm analysis, such pairs would likely be classified as structural (direct anatomical connection present and detectable). The additional state modulation would be a secondary effect on top of a strong structural signal.

**Impact**: M pairs contaminate LR-AUROC. Because M pairs are correctly identified as "direct" by the framework's S-score but counted as LR (positive class), they suppress LR-AUROC. This is a definitional issue in how LR is constructed, not a framework failure.

---

## Detailed Alignment: LR ↔ Primary Detection Target

**Verdict: PARTIAL — structurally contaminated**

The Phase 8A metric registry names LR as the "primary detection target of the current-velocity framework." LR = C ∪ M.

**Problem**: LR includes M (n=89, 9.4% of LR), which is on-connectome. The framework correctly identifies M pairs as S — which is the right structural characterization — but counts this as a false negative for LR. This is a benchmark design inconsistency: the framework is penalized for correctly classifying on-connectome pairs as structural.

If LR were defined as C only (SAREACHABLE=1 AND DIRECT=0), the target would be cleaner. As defined, LR-AUROC (0.4197) is worse than C-AUROC (0.4484) partly because M pairs add false-negative pressure.

---

## Complete Alignment Summary

| Paper object | Properties | Best benchmark proxy | Alignment verdict | Gap severity |
|-------------|-----------|---------------------|-----------------|-------------|
| Structural link | Direct coupling, state-independent | S | EXACT | None |
| Current-supported | Off-connectome, ΔQ≠0 between states | C | PARTIAL | Moderate (see below) |
| Null | No special coupling | N (off-connectome only) | PARTIAL | Minor |
| — (mixed) | — | M | NO ANALOG | — |
| Primary target | H2-regulated pairs | LR (C+M) | PARTIAL | Structural contamination |

**Gap severity for C↔current-supported**:

| Gap | Severity | Explains framework failure? |
|-----|---------|----------------------------|
| Topological label vs. observed signal (28% weak C) | Moderate | NO — even strong C fails (AUROC=0.4069) |
| Common cause vs. probability current | Moderate | PARTIALLY — benchmark measures ΔΩ, paper targets ΔQ; framework measures ΔΩ through wrong method |

---

## Conclusion

The benchmark labels are a **reasonable but imperfect proxy** for the paper's theoretical objects. The S↔Structural alignment is exact and the framework exploits it correctly (S-AUROC=0.8531). The C↔current-supported alignment has two structural gaps:

1. Topological label vs. observed signal (fixable by adding path_strength threshold)
2. Common-cause mechanism vs. probability current (deeper theoretical mismatch noted in Phase 6A review W7; not easily fixable by relabeling)

Neither gap explains the framework failure: the signal is present (B5 C-AUROC=0.5517), even the strongest-signal C pairs fail (strong C AUROC=0.4069), and the failure is architectural. The label mismatch is a theoretical precision issue, not the source of the empirical failure.
