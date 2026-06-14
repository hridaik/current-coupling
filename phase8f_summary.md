# Phase 8F Summary: What Is the Framework Actually Recovering?

**Date**: 2026-06-14  
**Frozen verdict**: Phase 8B FAILURE (MacroAUROC=0.5385, C-AUROC=0.4484, LR-AUROC=0.4197)  
**Phase 8C**: Architecture-limited failure (signal insensitive; C-AUROC flat across 24× parameter range)  
**Phase 8D**: A — No useful recovery (zero C pairs in top-50; state-sensitive C pairs scored worst)  
**Phase 8E**: Benchmark partially aligned; failure is architectural, not label-induced  
**Phase 8F**: Characterization of what the framework IS recovering

---

## The Three Questions

---

### Q1: What does the framework place at the top of its C-score ranking?

**Answer: N-labeled, structurally isolated, cross-module pairs at maximum softmax entropy.**

#### Top-K class composition (by C-score):

| k | % N | % C | % S | % LR | OR(N) | p-value(N) |
|---|-----|-----|-----|------|-------|-----------|
| 10 | **100%** | 0% | 0% | 0% | 1.71 | 0.20 |
| 20 | **100%** | 0% | 0% | 0% | 3.41 | **0.04** |
| 50 | **100%** | 0% | 0% | 0% | **8.53** | **0.0001** |
| 100 | **96%** | 3% | 1% | 3% | **4.10** | **0.0006** |

At k=50: all 50 pairs are N-labeled. C-class is completely absent. N-class is enriched 8.5× (p=0.0001). The first C pair appears at rank 71/9,900.

#### Properties of the top-50 pairs:
- **100% off-connectome** (DIRECT=0) — but off-connectome is also true of N pairs
- **0% SAREACHABLE** — no H2-mediated state-active relay in any top-50 pair
- **Mean |ΔCorr| = 0.0455** — below the global mean (0.0476) and C-class mean (0.0517)
- **Predominantly cross-module**: M2↔M3 pairs dominate (17/50 = 34%)
- **Maximum softmax entropy**: top pair (51,71) has entropy = 1.3862 ≈ log(4) = 1.3863 (maximum possible)
- **C-score margin over S-score**: only 0.0093 for the top-ranked pair — essentially noise

**Hub neurons**: Neurons 32 (M2, 20 appearances in top-100) and 64 (M3, 18 appearances) dominate the ranking. Neither is a H2 neuron. Neither has special H2 connectivity. Their prominence reflects intermediate structural degree that produces near-maximum-entropy softmax scores.

---

### Q2: Is the framework recovering structure, state dependence, off-connectome organization, module organization, or something else?

#### Is it recovering structure?

| Metric | C-score performance | S-score performance |
|--------|-------------------|-------------------|
| Detects DIRECT=1 (structural) | NO — ρ(C-score, direct)=−0.407 | YES — ρ(S-score, direct)=+0.408 |
| Detects S-class | NO — ρ(C-score, is_S)=−0.267 | YES — S-AUROC=0.853, prec@50=0.52 |

The framework successfully detects structure — but through the **S-score**, not the C-score. The S-score is the correct signal for structural detection.

#### Is it recovering state-dependent organization?

**NO.** ρ(C-score, |ΔCorr|) = **−0.140** (p=10⁻⁴⁴).

State-sensitive pairs score LOWER on C-score than state-invariant pairs. The most state-dependent C pairs (top 10% by |ΔCorr|, n=86, mean |ΔCorr|=0.1137) have median C-score rank of 7,230/9,900 — near the bottom 27% of the ranking.

Top-K mean |ΔCorr| vs global mean:
- Top-10: 0.0289 (−39% below global mean)
- Top-50: 0.0455 (−4% below global mean)
- Mann-Whitney test "top-k is more state-dependent than random": p=0.998 at k=10 (framework selects MORE state-invariant pairs than chance)

#### Is it recovering off-connectome organization?

**SUPERFICIALLY YES, SUBSTANTIVELY NO.**

Top-50 is 100% off-connectome (DIRECT=0) — this is correct topologically. But within the off-connectome pool (8,314 N + 857 C = 9,314 pairs), the framework ranks N pairs **above** C pairs. Mean C-score: N=0.2444, C=0.2425. The framework cannot distinguish C from N within the off-connectome region. The "off-connectome" property of the top-K is a byproduct of the S/C softmax competition (on-connectome S pairs have high S-score → low C-score), not genuine off-connectome detection.

#### Is it recovering module organization?

**CROSS-MODULE bias, but not meaningful module signal.**

Top-K pairs are cross-module (within-module enrichment OR=0.35 at k=100, p>0.999 — within-module is significantly depleted). The M2↔M3 cross-module interface is over-represented. This reflects that N-labeled cross-module pairs have the weakest structural coupling (no H2 relay, no direct inter-module connections) and thus land in the maximum-entropy zone.

#### What IS it recovering?

**The pairs where the softmax has no information: maximum-uncertainty, structurally-absent, cross-module N pairs.**

The C-score is monotonically anti-correlated with the S-score (ρ=−0.997). It is not detecting anything — it is the residual class assignment when S-score, M-score, and N-score are all low. When all logits are near zero, the class with slightly higher logit (Delta_PCor vs PCor_cond) wins — but the winning margin is 0.0093 probability units, indistinguishable from sampling noise.

---

### Q3: How does this differ from the benchmark's C class and the worm signal?

#### vs. the Benchmark C Class

| Property | What C-score ranks #1–50 | Benchmark C class |
|----------|--------------------------|------------------|
| Label | N (100%) | C (0% of top-50) |
| SAREACHABLE | 0% | 100% |
| Direct | 0% | 0% |
| Mean |ΔCorr| | 0.046 | 0.052 |
| H2 path strength | 0.000 | median 0.027 |
| Module structure | Cross-module, M2↔M3 | Cross-module (H2 connects 2 modules) |

The top-50 by C-score is the complementary set to C — pairs that are off-connectome but have NO H2-mediated state signal. They share the "off-connectome" property but are opposite in every other meaningful dimension.

#### vs. the Worm Signal (Class 4 pairs: RMEL-RMER, ADEL-URY type)

| Property | What C-score ranks #1–50 | Worm Class 4 (ideal target) |
|----------|--------------------------|----------------------------|
| Off-connectome | YES | YES |
| State-dependent | BELOW AVERAGE | Strong (large ΔQ) |
| State mechanism | None (no relay) | Neuromodulatory / polysynaptic |
| Behaviorally meaningful | No (N pairs are structurally unremarkable) | YES (roaming-specific) |
| "Removable" by state change | N/A (no state-link to remove) | YES (link attenuates in dwell state) |

The framework's top-ranked pairs are the opposite of the worm-like target in every meaningful respect except topology (both are off-connectome).

---

## Classification

**A: Framework ranking is largely structural.**

The C-score is a near-perfect inversion of the S-score (ρ=−0.997). The framework's implicit ranking in C-score is determined by absence of structure. Pairs rank high on C because they lack structural coupling — NOT because they have state-dependent off-connectome organization.

Evidence for A:
1. ρ(C-score, direct_structural) = −0.407 — the strongest single predictor of C-score is absence of direct coupling
2. ρ(C-score, S-score) = −0.997 — C-score and S-score are nearly perfect inverses
3. Top-50 = 100% N (null class): the pairs with no structural coupling AND no state-modulated signal
4. ρ(C-score, is_N) = +0.236 — the only positive predictor of C-score is N-class membership
5. ρ(C-score, |ΔCorr|) = −0.140 — state-dependent pairs score LOWER
6. Top-50 have mean |ΔCorr| = 0.0455, below global mean 0.0476

Evidence against B (framework captures different-but-coherent organization):
- The "cross-module N" organization detected has no theoretical justification and is not present in the design specification
- The hub neurons (32, 64) are not biologically special; their prominence is network-generation artifact
- The maximum-entropy regime (entropy ≈ log(4)) in top-50 indicates the framework has NO signal, not a different signal

Evidence against C (framework ranking unrelated to meaningful organization):
- The C score is related to structural properties — it's just the wrong relationship (anti-structural)
- The S-score correctly identifies structural pairs; so the framework has a well-functioning structural detector that the C-score inverts

**Classification A with precision**: The framework ranking is **structurally anti-correlated** — it places the least structurally-connected pairs at the top of its C-ranking, and the most structurally-connected pairs at the bottom. This is not "structural detection" but rather "structural null" detection — the pairs left over when structure is absent.

---

## Mechanism Summary

The failure follows a complete causal chain:

```
Framework design: C-score = Delta_PCor = |PCor_raw − PCor_cond|
                  where y_resid = y − outer(z, beta)

For C-class pairs:
  → High z-mediated correlation in y_raw
  → z-regression removes this from y_resid
  → PCor_cond (from y_resid) is reduced
  → Delta_PCor = |PCor_raw - PCor_cond| is ALSO reduced
     (because PCor_raw includes H2-mediated signal,
      PCor_cond removes it, but their DIFFERENCE
      is also small because the H2 path is structural
      and persists even in y_resid to some degree)
  → S-score stays moderate (from residual structural paths)
  → Softmax assigns mediocre probabilities to C

For N-class pairs:
  → Very low PCor_raw (no structural or H2 coupling)
  → z-regression has minimal effect
  → PCor_cond ≈ PCor_raw (both near zero)
  → Tiny Delta_PCor from finite-sample noise
  → S-score is also near zero
  → Softmax reaches maximum entropy
  → C-score = 0.25 + tiny margin → wins by default

Result: N pairs float to the top; C pairs sink.
```

The framework does not detect the intended signal. It instead sorts pairs by absence of structural coupling, placing the structurally-null pairs at the top of the C-score ranking.

---

## Deliverables

| File | Status |
|------|--------|
| results/phase8f/f1_topk_inventory.md | COMPLETE |
| results/phase8f/f2_class_composition.md | COMPLETE |
| results/phase8f/f3_state_dependence.md | COMPLETE |
| results/phase8f/f4_offconnectome.md | COMPLETE |
| results/phase8f/f5_module_structure.md | COMPLETE |
| results/phase8f/f6_signal_tracking.md | COMPLETE |
| results/phase8f/f1_topk_inventory_data.json | COMPLETE |
| results/phase8f/f2_class_composition_data.json | COMPLETE |
| results/phase8f/f3_state_dependence_data.json | COMPLETE |
| results/phase8f/f4_offconnectome_data.json | COMPLETE |
| results/phase8f/f5_module_structure_data.json | COMPLETE |
| results/phase8f/f6_signal_tracking_data.json | COMPLETE |
| phase8f_summary.md | COMPLETE |
