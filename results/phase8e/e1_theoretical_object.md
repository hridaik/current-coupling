# E1: The Paper's Theoretical Object

**Phase**: 8E — Label-Definition Audit  
**Date**: 2026-06-14  
**Constraint**: No tool use beyond document reading. No rerunning of simulations. No label modifications.

---

## 1. Source Documents Consulted

1. `task.md` — Real C. elegans analysis: ΔQ between roaming and dwelling states, Class 4 target
2. `phase6a_ground_truth_spec.md` — Formal benchmark definitions and theoretical framing
3. `phase6a_review.md` — Adversarial review, vulnerabilities W6 and W7
4. `phase6b_label_generation_spec.md` — SAREACHABLE algorithm and leakage audit
5. Phase 8A and 8B specifications — Framework inputs and metric definitions

---

## 2. The Paper's Stated Framework

The paper deploys a **current-velocity framework** designed to detect **probability-current-supported functional links** — pairs of neurons whose directed conditional dependence changes between behavioral states but are not explained by direct synaptic connectivity.

The formal object derives from the stationary Fokker-Planck equation for a linear OU system:

```
dx_i/dt = Σ_j A_ij x_j dt + √(2D) dW_i
```

In the stationary distribution, the **probability current** between neurons i and j is:

```
J_ij = Q_ij − Q_ji,   where Q = Ω D  (Ω = precision matrix, D = diffusion matrix)
```

Between two behavioral states (roaming, dwelling), **ΔQ = Q_roam − Q_dwell** captures the change in directed probability current.

---

## 3. Operational Definition of the Two Target Link Classes

### 3.1 Structural Link

**Definition**: A pair (i,j) is structural if it has direct anatomical connectivity in the C. elegans synaptic connectome:

```
Structural(i,j) ⟺ A_raw(i,j) ≥ 1  OR  A_raw(j,i) ≥ 1
```

where A_raw is the physical synapse count matrix (from the connectome atlas or Creamer connectome).

**Observable consequences**:
- Significant partial correlation persists regardless of behavioral state
- Q_ij does not change substantially between roaming and dwelling
- The pair (i,j) is NOT enriched for Class 4 (off-both-connectome) status

**Key property**: State-independent. The structural connection exists because of fixed anatomy.

---

### 3.2 Current-Supported Link

**Definition**: A pair (i,j) is current-supported if it is absent from the structural connectome but exhibits a large change in directed conditional dependence between behavioral states:

```
Current-supported(i,j) ⟺  A_raw(i,j) = 0  AND  A_raw(j,i) = 0
                            AND |ΔQ(i,j)| = |Q_roam(i,j) − Q_dwell(i,j)| is large
```

Both conditions are jointly required. Off-connectome pairs with no ΔQ are null (not current-supported). On-connectome pairs with ΔQ are structural (possibly with additive state-modulated component, but classified as structural by the primary criterion).

**Observable consequences**:
- Near-absent or non-significant partial correlation in one behavioral state (typically dwell)
- Significant partial correlation in the other state (typically roam)
- The pair is off BOTH the chemical synapse connectome AND the Creamer connectome
- Enriched for neuropeptide signaling (Class 4 in the worm analysis: off-both-connectomes)
- The functional connection is behaviorally removable: it diminishes when state changes

**Key property**: State-exclusive or strongly state-amplified. The functional link is present primarily because of state-modulated network influences (neuromodulators, gap junctions, polysynaptic paths), not fixed anatomical wiring.

---

### 3.3 Worm-Specific Instantiation (from task.md)

In the actual worm analysis:

- **Behavioral states**: roaming (high locomotion, exploratory) vs. dwelling (low locomotion, local search)
- **State variable**: a latent state variable z(t) extracted from neural activity, used to condition ΔΩ
- **Target class**: **Class 4** = off BOTH the raw connectome AND the Creamer connectome; these pairs show the largest ΔQ between states
- **Enrichment**: Class 4 pairs are enriched for neuropeptide signaling neuron pairs — consistent with a neuromodulatory mechanism that is anatomically diffuse but state-dependent

Concrete examples:
- RMEL-RMER: bilateral pair without direct synaptic connection; shows state-dependent synchrony during roaming
- ADEL-URY: off-connectome pair with state-dependent changes in conditional dependence
- These pairs presumably have near-zero Q(dwell) and significant Q(roam) — the coupling is state-exclusive or state-predominant

**OU example (leech)**: Analogous identification of pairs with small cross-coupling in resting state that become functionally connected during locomotor states, driven by shared neuromodulatory input rather than direct synaptic anatomy.

---

## 4. Critical Properties of the Theoretical Object

The paper's "current-supported link" has three jointly necessary properties:

| Property | Description | Necessity |
|----------|-------------|-----------|
| **Off-connectome** | Not in A_raw (synapse count = 0 in both directions) | Required |
| **State-dependent** | ΔQ(i,j) is large between behavioral states | Required |
| **Observable** | The signal is detectable in neural recordings | Required |

And one property that is strongly implied but not mathematically required:

| Property | Description | Notes |
|----------|-------------|-------|
| **State-exclusive/predominant** | The link is absent or negligible at baseline; it *appears* at the active state | Implied by Class 4 enrichment in worm analysis; not a hard boundary |

---

## 5. What the Theoretical Object Is NOT

- It is NOT defined by topology alone. A pair (i,j) that is off-connectome but shows no ΔQ is NULL, not current-supported.
- It is NOT equivalent to "confounded by a common unobserved cause." Per Phase 6A review, W7: *"The probability current between two neurons jointly driven by a common unobserved source need not involve nonequilibrium circulation. H2 creates a confounding effect, not a current-supported effect in the thermodynamic sense."* This vulnerability distinguishes the theoretical object from what the benchmark actually instantiates.
- It is NOT defined by ΔΩ (precision change) alone. In principle, ΔΩ and ΔQ can decouple when the diffusion matrix D is not uniform. The paper's Q = ΩD is a specific product.
- It is NOT necessarily causal in the mechanistic sense. It is a **probabilistic** object — a statement about the stationary distribution and how it changes between states.

---

## 6. Summary

The paper's theoretical object is **observable, state-conditioned, off-connectome conditional dependence change** — formally ΔQ(i,j) ≠ 0 for pairs absent from the structural connectome. This object is:

1. Grounded in the physics of probability current in the Fokker-Planck equation
2. Operationalized in the worm analysis as Class 4 pairs (off-both-connectome) enriched for neuropeptide signaling
3. Detectable in principle by comparing precision matrices between behavioral states

The benchmark operationalizes a *proxy* for this object using graph topology (SAREACHABLE through H2 neurons). Whether this proxy faithfully captures the theoretical object is the question examined in E2–E3.
