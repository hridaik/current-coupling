# Phase 9A.1 — Theoretical Target: Current-Supported Organization

## Purpose

Define, precisely and operationally, the theoretical object the benchmark must test. This
object is common across the OU cascade, the leech CPG, and the C. elegans worm analysis.
It is an organization-level object, not a pair-level label.

---

## Reading the Three Systems

### OU Cascade

**States:** Source drive α ∈ {1, 5, 20}. Coupling matrix A is fixed throughout.

**Observable organization:** The off-local partial correlation matrix — conditional dependence
between non-adjacent nodes |i−j| > 1. At α=1, off-local conditional dependence accounts
for 5.0% of total conditional dependence. At α=20, it accounts for 14.7%. The organization
grows sixfold while A never changes.

**Current-supported structure:** Because A is fixed, every change in Q (and therefore every
change in the off-local partial correlation matrix) is entirely attributable to the change in
Ω. The dominant off-local link (nodes 6 and 8) has A[6,8] = 0 throughout; its precision
entry Q[6,8] grows from −0.026 to −0.257 as α increases. The entry is, by construction,
equal to Ω[6,8] at every α.

**State dependence:** The off-local organization is not present at α=1 (near-zero). It is a
creation of the high-drive regime. The topology is set by the cascade structure; the gain is
set by α. Both are required.

**Intervention logic:**
- State intervention (reduce α): off-local conditional dependence returns to baseline
  without touching A. The link from node 6 to node 8 dissolves.
- Structural intervention: not applicable in the OU cascade (A is fixed by assumption).
  In principle, removing a relay node from the cascade would eliminate the indirect path
  but this is not tested in the paper.

**The paper's evaluation:** Not "classify every pair as structural or current-supported."
Instead: report the Frobenius norm of the off-local current matrix Scur = ‖M⊙Ω‖_F and the
off-local conditional dependence fraction Sstat, and show they grow with α. The evaluation
is organizational, not pairwise.

---

### Leech Swimming CPG

**States:** Coupling gain ∈ {0, nominal}. Anatomical coupling matrix K is fixed.

**Observable organization:** The set of non-adjacent ganglion-pair conditional couplings
that are present at nominal gain and absent at zero gain. At nominal gain, 55–56 non-adjacent
ganglion pairs acquire significant Ω entries. These pairs form a structured topology
determined by the wave's coupling phase geometry, not by gain amplitude.

**Current-supported structure:** These 55–56 pairs all have K[i,j] = 0 (they are off the
anatomical coupling matrix). Their Ω[i,j] entries are entirely current-supported by
construction. The topology is switched on by the wave regime; the amplitude is scaled by gain.

**Two separable effects:**
1. Onset effect: specific pairs become conditionally coupled as soon as the wave is
   established. The topology is determined by coupling phase, not gain.
2. Amplitude effect: the magnitude of Ω entries scales continuously with gain, growing
   tenfold between 10% and 100% of nominal gain.

**Intervention logic:**
- State intervention (reduce gain to zero): all 55–56 current-supported pairs dissolve.
  The current-velocity term is exactly zero at zero gain.
- Structural intervention (remove cells 27 and 33): the wave persists, phase lag decreases
  from 11.5° to 7.6° per ganglion, but many current-supported pairs remain. The 55–56 pairs
  are NOT eliminated by this structural lesion. They survive structural perturbation.
- Structural intervention (remove load-bearing cells 208/123 or cell 28): wave collapses.
  When the regime collapses, its current-supported organization also collapses. But this
  is a regime-destroying intervention, not a targeted structural intervention.

**The paper's evaluation:** Not "classify each ganglion pair." Instead: show that the
framework correctly separates the three classes — load-bearing structural connections,
current-supported connections, coupling-supported connections — based on how each class
responds to the two types of intervention. The evaluation is topological and modular.

---

### C. elegans Worm

**States:** Dwelling (slow local search) vs. roaming (fast exploration). Coupling matrices
A_raw and A_C are fixed. Behavioral state modulates neuromodulatory tone.

**Observable organization:** The off-connectome ΔΩ matrix — differences in current
organization between dwelling and roaming, restricted to Class 4 pairs (A_raw = 0, A_C = 0).
The dominant organization is the PDF-receptor circuit: sources ADEL, RMEL, RMER, RID
(pdf-1/pdf-2 expressing) → targets URYVR, URYDL, URXL (pdfr-1 expressing).

**Current-supported structure:** All top-ranked PDF pairs have A_raw[i,j] = 0 and A_C[i,j] = 0.
Their ΔΩ entries are entirely current-supported. The circuit is dwelling-dominant: present
during dwelling, absent during roaming. The neurons and receptor machinery are present in
both states; what changes is the dynamical regime.

**State dependence:** PDF-annotated Class 4 pairs are significantly enriched among the
strongest |ΔΩ| entries (AUROC = 0.664, p = 0.004; Fisher OR = 7.2, p = 0.002). The same
enrichment is absent in raw GCaMP coordinates (AUROC = 0.541, p = 0.18), consistent with
behavioral masking in the raw signal.

**Intervention logic:**
- State intervention (change behavioral state from dwelling to roaming): PDF circuit
  coordination disappears (ΔΩ = 0 for these pairs in roaming).
- Structural intervention: the prediction is that activation of ADEL during dwelling
  should produce responses in URYVR and URYDL; the response should be absent during roaming,
  require dense-core vesicle release, and disappear in pdfr-1 mutants. This is a state
  (neuromodulatory) intervention.
- The signal is NOT present when raw GCaMP is used (behavioral confound masks it). CePNEM
  residualization is required to observe the neural-state organization.

**The paper's evaluation:** Not "classify every Class 4 pair." Instead: test whether the
PDF-receptor-annotated pairs are enriched among the top off-connectome ΔΩ entries. The
evaluation is circuit-level enrichment, not pair-level accuracy.

---

## Operational Definition: Current-Supported Organization

The following definition is common across all three systems.

**Current-supported organization** is a structured set P of neuron pairs satisfying:

### 1. Off-structural
For all (i,j) ∈ P:
```
A[i,j] = 0
```
No direct anatomical coupling. The coupling reference (A) is the best available at the
relevant spatial scale.

### 2. State-dependent conditional dependence change
For all (i,j) ∈ P:
```
ΔΩ[i,j] = Ω_A[i,j] − Ω_B[i,j] ≠ 0
```
where state A and state B differ only in their dynamical regime (drive, gain, neuromodulation),
not in their structural coupling matrix A.

### 3. Structured topology
P is not a random set of off-connectome pairs. It forms a coherent subnetwork:
- a set of source neurons (increased drive or neuromodulatory activity in state A)
- a set of target neurons (conditionally linked to sources via current propagation)
- a topology determined by the regime's dynamics, not by A

### 4. State-intervention dissolution
Under state intervention (reduce drive, suppress gain, change neuromodulatory regime):
```
ΔΩ[i,j] → 0   for (i,j) ∈ P
```
The organization disappears when the regime that creates it is removed.

### 5. Structural-intervention survival
Under structural intervention (remove specific anatomical connections NOT within P):
```
ΔΩ[i,j] ≈ ΔΩ_original[i,j]   for (i,j) ∈ P
```
The organization persists when edges elsewhere in the circuit are lesioned, as long as
the regime-sustaining structure is intact. (Regime-destroying lesions are a separate case.)

---

## What This Is NOT

**Not pair-level classification.** The question is not "which pairs are current-supported?"
It is "can the framework recover the dominant current-supported organization?" A framework
that recovers 40 of the top 50 ΔΩ pairs but cannot assign a binary label to every pair
still succeeds.

**Not AUROC over all off-connectome pairs.** AUROC treats every pair as equally important.
The paper's evaluation is about the dominant organization — the top-ranked pairs, the
modules they form, the circuits they imply. A framework that correctly identifies the PDF
circuit (7× enrichment among top 20) but ranks many weak off-connectome pairs randomly
still recovers the organization.

**Not dependent on exact pair labels.** The worm analysis does not ask "is ADEL→URYVR
a Class C pair?" It asks "is the PDF-annotated set enriched among the highest ΔΩ entries?"
The evaluation is distributional and topological, not pair-by-pair.

---

## Summary

The theoretical object is:

> The dominant structured set of off-connectome pairs whose conditional dependence
> is state-created (present in state A, absent in state B), organized as a coherent
> functional subnetwork, and removed by state intervention but not by targeted
> structural intervention.

The benchmark must test whether the framework **recovers this organization** — its ranking,
its topology, and its intervention behavior — not whether it can label every pair.
