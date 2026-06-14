# E2: Benchmark Label Definitions — What Each Class Actually Measures

**Phase**: 8E — Label-Definition Audit  
**Date**: 2026-06-14  
**Constraint**: No label modifications. Strictly descriptive.

---

## Construction Rules

Labels are assigned by the Phase 6B algorithm based on two binary criteria:

**DIRECT(i,j)**: direct structural coupling exists between i and j in the observed (obs) submatrix of A_sparse.  
Formal rule: `A_sparse[i,j] ≠ 0 OR A_sparse[j,i] ≠ 0`

**SAREACHABLE(i→j)**: a two-hop path i→h→j exists through a state-active H2 neuron.  
Formal rule: `∃ h ∈ SA: A_sparse[h,i] ≠ 0 AND A_sparse[j,h] ≠ 0`  
where `SA = {132,133,134,135,136,137,138,139}` (the 8 neurons driven by z(t)).

The four classes partition the 9900 directed obs-obs pairs exhaustively.

---

## Class-by-Class Analysis

---

### Class S: Structural (n=497)

**Construction rule**:  
`DIRECT(i,j) = 1  AND  SAREACHABLE(i→j) = 0`

Direct coupling exists in A_sparse between i and j (either direction). No two-hop H2-mediated path exists.

**What the criterion guarantees**:
- The pair (i,j) is coupled structurally in the benchmark's connectivity matrix
- No state-active relay neuron exists that could modulate the pair's co-activity via H2

**Observable consequence**:
- Pair (i,j) shows significant partial correlation (PCor) regardless of z
- The correlation has minimal state-dependence — the coupling is structural, not z-gated
- Some co-activity exists due to shared inputs (H1 noise, H2 at z=0), but the direct coupling term dominates

**Necessarily state-dependent?** NO.  
By construction (SAREACHABLE=0), no H2-mediated state-modulation pathway exists. S pairs may show slight correlation changes due to global state effects, but there is no mechanism for H2-driven state specificity.

**Necessarily off-connectome?** NO.  
By definition, DIRECT=1 means the pair IS in the benchmark's structural connectome. This is the "on-connectome" class.

**Analog to paper's object**: Structural link. Good proxy.

---

### Class C: Current-mediated (n=857)

**Construction rule**:  
`DIRECT(i,j) = 0  AND  SAREACHABLE(i→j) = 1`

No direct coupling between i and j. Exactly one or more H2 neurons h ∈ SA exist such that i→h→j path is present in A_sparse.

**What the criterion guarantees**:
- The pair is off the benchmark's structural connectome (direct coupling absent)
- A topological pathway exists through a state-active relay: i influences h (A[h,i]≠0), and h influences j (A[j,h]≠0)
- The relay neuron h is driven by z(t) at strength γ_H2 × z(t) ← *only this neuron receives the z drive*

**What the criterion does NOT guarantee**:
- That the H2-mediated coupling is strong enough to produce detectable signal. Path strength = |A[h,i]| × |A[j,h]| ranges from 0.000 to 0.392; ~28% of C pairs have path_strength < 0.01.
- That the pair's correlation changes *between states* rather than *during states*. Both phenomena contribute to |ΔCorr|, but the H2-mediated correlation is present even at z=0 (because the structural path h→j and h←i exists always; z merely amplifies h's activity).
- That the mechanism is "current-supported" in the thermodynamic sense. Per Phase 6A review W7: the pair is jointly driven by a common unobserved source (h), which is a confounding structure, not probability-current circulation.

**Observable consequence**:
- Pair (i,j) shows correlation partly mediated through h, which increases with z (because z drives h, h drives j and is driven by i)
- Observable state-dependent signal |ΔCorr| is present above chance (B5 C-AUROC=0.5517; C pairs are 1.18× enriched in state-sensitive quartile)
- Signal strength varies widely across C pairs: top 10% |ΔCorr| mean = 0.1137; bottom quartile |ΔCorr| ≤ 0.030

**Necessarily state-dependent?** IN EXPECTATION, YES — but NOT GUARANTEED per individual pair.  
The path exists (topological guarantee), but whether the empirical |ΔCorr| is detectable above noise depends on path_strength and finite-sample variability. Confirmed on average (B5 above chance), not guaranteed individually.

**Necessarily off-connectome?** YES.  
DIRECT=0 is required by construction. Every C pair is absent from the structural benchmark connectome.

**Analog to paper's object**: Intended proxy for current-supported links. See E3 for alignment analysis.

---

### Class M: Mixed (n=89)

**Construction rule**:  
`DIRECT(i,j) = 1  AND  SAREACHABLE(i→j) = 1`

Both direct coupling AND H2-mediated path exist simultaneously.

**What the criterion guarantees**:
- The pair has structural coupling in A_sparse
- AND a state-active relay pathway also exists through H2

**Observable consequence**:
- Pair (i,j) shows both structural (z-invariant) AND state-modulated (H2-mediated) correlation
- The structural component dominates the total correlation
- ΔCorr is present (1.30× enrichment in state-sensitive quartile), but the pair is also on the structural connectome
- Framework S-score is high for M pairs (direct coupling detected), while C-score is low → M pairs are misclassified as S by the framework (C-AUROC for M = 0.1518)

**Necessarily state-dependent?** PARTIALLY — by topology (H2 path exists), but structural coupling co-exists and dominates.

**Necessarily off-connectome?** NO — DIRECT=1 means the pair IS on the structural connectome.

**Analog to paper's object**: No direct analog. The paper separates off-connectome (Class 4) from on-connectome; M is a mixed case that the paper's framework would likely classify by the structural component.

---

### Class N: Null (n=8457)

**Construction rule**:  
`DIRECT(i,j) = 0  AND  SAREACHABLE(i→j) = 0`

No direct coupling and no H2-mediated path. The vast majority of directed pairs fall here.

**What the criterion guarantees**:
- No structural coupling in A_sparse between i and j
- No H2 relay (either h∈SA has no connection to i, or h∈SA has no connection to j)

**Observable consequence**:
- Pair (i,j) has no mechanism for H2-driven state-dependent co-activity
- Background correlation exists from shared H1 inputs, other indirect paths through non-SA neurons, and H2 neurons in their basal (z=0) state
- Correlation is structurally present but NOT z-modulated through the H2 mechanism
- Provides the null distribution against which C-detection AUROC is computed

**Necessarily state-dependent?** NO. No state-active relay pathway exists.

**Necessarily off-connectome?** YES — DIRECT=0 by construction. N pairs are off-connectome but not state-modulated (contrast with C: off-connectome AND state-modulated).

**Analog to paper's object**: Closest to the paper's null class (no special functional link in either direction).

---

### Class LR: Left-Right / SAREACHABLE (n=946 = C+M)

**Construction rule**:  
`SAREACHABLE(i→j) = 1`  (i.e., C ∪ M)

This is the combined class of all pairs with H2-mediated paths, regardless of direct coupling.

**What the criterion measures**:
- All pairs that have ANY state-active relay through H2
- Includes both off-connectome pairs (C, n=857) and on-connectome pairs (M, n=89)

**Observable consequence**:
- LR-AUROC should measure whether the framework can identify H2-regulated pairs in general
- Contains M pairs, which the framework classifies as structural (high S-score, not C-score) — this dilutes LR-AUROC relative to C-AUROC for any C-score-based ranking
- LR-AUROC=0.4197 (worse than C-AUROC=0.4484)

**Analog to paper's object**: The paper names LR as the "primary detection target of the current-velocity framework." However, the LR class includes on-connectome M pairs, which blurs the off-connectome signal.

---

## Summary Table

| Class | n | direct=? | sareachable=? | Necessarily state-dep? | Necessarily off-connectome? | Paper analog |
|-------|---|---------|--------------|----------------------|---------------------------|-------------|
| S | 497 | 1 | 0 | NO | NO (on-connectome) | Structural link |
| C | 857 | 0 | 1 | IN EXPECTATION (not guaranteed) | YES | Current-supported (partial proxy) |
| M | 89 | 1 | 1 | PARTIALLY | NO (on-connectome) | Mixed (no direct analog) |
| N | 8457 | 0 | 0 | NO | YES (off-connectome but not state-mod) | Null |
| LR | 946 | — | 1 | IN EXPECTATION | PARTIALLY (includes M) | Primary detection target |

---

## Key Asymmetry

The N class is **also off-connectome** (direct=0) — which means "off-connectome" alone is not what distinguishes C from N. What distinguishes C from N is the **H2-mediated state-modulation path**.

From the benchmark's perspective:
- Off-connectome + state-modulated = C (positive target)  
- Off-connectome + not state-modulated = N (negative control)

This is a reasonable operationalization. The critical issue (explored in E3) is whether the benchmark's "state-modulated" (SAREACHABLE) correctly operationalizes the paper's "current-supported" (ΔQ ≠ 0).
