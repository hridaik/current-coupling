# Phase 9E — Task 4: Contextualization vs OU / Leech / Worm

**Date:** 2026-06-15

---

## What all four benchmarks are testing

All four benchmarks (OU, Leech, Worm, Phase 9D synthetic) evaluate the same core question:

> Given multivariate neural trajectory data from two behavioral states and known structural connectivity, can the current-velocity framework identify which pairs of neurons show state-dependent changes in organizational structure that exceed what the structural connectivity alone predicts?

The difference lies in what "planted organization" means in each system, and whether the ground truth is analytically known.

---

## OU (Ornstein-Uhlenbeck baseline)

**What it tests:** Recovery of planted pairwise state changes in a network where the dynamics are simple OU processes and the true ΔΩ is directly known. This is the "clean room" scenario: the framework was designed for this model class, A is fully known, D is exactly diagonal, and the only question is whether finite-sample noise degrades recovery.

**Ground truth origin:** Analytical (closed-form ΔΩ from specified parameters).

**What is analogous to Phase 9D:** Both use known A and estimate D from data. Both compare a State A with elevated D at selected nodes to a uniform State B. Both evaluate recovery against an analytical oracle.

**What is different:** In OU, the planted pairs are typically direct (both endpoints have elevated D), so the oracle ΔΩ is large and the boundary between planted and non-planted is clear. In Phase 9D, the target neurons (PMC_TGT) have D_true = 0 elevated; their state-dependent co-organization arises entirely through the hidden relay. This hidden-relay mechanism is not present in the OU baseline, and it introduces the D estimation error that creates the four false positives.

---

## Leech (oscillatory circuit)

**What it tests:** Recovery of state-dependent organization in a system with known biophysical structure (C. elegans leech ganglia), where the planted organization is a set of circuit pairs that change coupling strength between swim and crawl states. The ground truth is defined by the known circuit diagram, not an analytical formula.

**Ground truth origin:** Anatomical (known synaptic circuit structure between swim/crawl CPG neurons).

**What is analogous to Phase 9D:** Both have a small planted circuit embedded in a larger background network. Both have "target" neurons that receive state-dependent input from a relay structure (proprioceptive feedback in the leech; H_global in Phase 9D). Both evaluate whether the framework can identify inter-module pairs that change organizational strength across states.

**What is different:** The leech ground truth is based on anatomical knowledge, not an analytical oracle. Evaluation in the leech benchmark is therefore approximate: pairs "should" change but the true magnitude of ΔΩ is not available. In Phase 9D, the oracle ΔΩ is exact (Lyapunov solution). Additionally, in the leech, the relay structure is partially observed (proprioceptive neurons are in the recording), whereas in Phase 9D the relay (H_global) is fully hidden and never observed.

**Performance comparison:**
- Leech PMC_AUROC ≈ 0.72, Phase 9D = 0.794 (better circuit discrimination in Phase 9D)
- Leech ρ ≈ 0.30, Phase 9D ρ = 0.190 (better global ranking in leech — likely because the leech relay is partially observed)

The Phase 9D performance reflects a harder test in one dimension (fully hidden relay) and an easier test in another (exact oracle, strong D modulation signal).

---

## Worm (C. elegans neuromodulatory system)

**What it tests:** Recovery of state-dependent organization between roaming (State A) and dwelling (State B) behavioral states in *C. elegans*. The planted organization is the known pdf-1 → pdfr-1 neuromodulatory circuit, which is biologically validated but not analytically characterized.

**Ground truth origin:** Biological / genetic (pdf-1 knockout experiments, receptor distribution maps).

**What is analogous to Phase 9D:** Phase 9D is explicitly designed to model the worm benchmark. The PMC_SRC neurons model pdf-1 neurons (neuropeptide-releasing, elevated activity during roaming), H_global models the volume-transmission relay (neuropeptide diffusion), and PMC_TGT models pdfr-1 neurons (neuropeptide receptors in M3/M4 modules). The D-only modulation (elevated D at source neurons in State A) directly mirrors the observed excess variance of URXL/URYVL neurons in roaming. The complete isolation of PMC_SRC and PMC_TGT from background connectivity in A_obs mirrors the fact that pdf-1/pdfr-1 neurons communicate primarily through neuropeptide signaling rather than canonical synaptic connections.

**What is different:**  
1. Phase 9D has an analytical oracle; the worm benchmark does not. Recovery in the worm must be evaluated against imperfect biological ground truth.  
2. Phase 9D's relay is completely hidden (H_global never appears in data); the worm benchmark's relay (neuropeptide diffusion) is also unobserved, making this an accurate model.  
3. The PMC definition in Phase 9D is expanded to include TGT-TGT pairs (consistent with bidirectional pdfr-1↔pdfr-1 annotation in the worm). In the worm benchmark, directed pdf-1→pdfr-1 pairs were the primary annotation target.  
4. Phase 9D controls signal strength precisely (D_HG_A = 10.0, D1 ratio = 2758×); the worm's actual signal strength is not controlled.

**What Phase 9D adds that the worm cannot provide:** A clean analytical answer to "did the framework find the right pairs?" In the worm, it is possible that a pair the framework ranks highly is biologically correct even if not in the pdf-1/pdfr-1 annotation. In Phase 9D, the ground truth is unambiguous.

---

## Summary comparison

| Property | OU | Leech | Worm | Phase 9D |
|----------|----|----|----|----|
| Ground truth | Analytical | Anatomical | Biological | Analytical |
| Relay structure | None (direct D) | Partially observed | Fully hidden | Fully hidden |
| PMC boundary | Sharp | Approximate | Approximate | Sharp |
| Signal strength | Controlled | Unknown | Unknown | Controlled (2758×) |
| Models worm mechanism | No | Partially | Yes (target) | Yes (designed analog) |
| Oracle AUROC available | Yes | No | No | Yes (0.9983) |
| False positive mechanism | Finite-sample noise | Circuit boundary ambiguity | Annotation incompleteness | HG-drive absorption |

---

## What Phase 9D demonstrates that the others cannot

Phase 9D provides the first controlled, analytically grounded test of the framework on a system with a **fully hidden relay** structure — where the state-dependent signal propagates entirely through unobserved nodes. This is the most direct analog of the worm's neuropeptide volume-transmission system, and it demonstrates:

1. The framework can identify the downstream targets of a hidden relay circuit (PMC_TGT pairs) at 92% precision in the top-50.
2. The framework incorrectly attributes the relay-driven excess variance at target neurons to elevated source diffusion at those nodes — a mechanistically specific estimation artifact.
3. Despite this attribution error, the circuit pairs are correctly separated from background pairs at the AUROC level (0.794), because the co-organization signal among PMC_TGT pairs is strong enough even under imprecise D estimation.
