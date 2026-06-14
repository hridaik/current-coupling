# Phase 5A.3 — Framework vs. Standard Interpretation
Date: 2026-06-12

---

## Question

For each leading candidate: what exactly did the framework add over a naïve interpretation?

---

## Case 1: RMEL–RMER

### Naïve Interpretation

**Anatomical:**
RMEL and RMER are bilateral homologs of the ring motor neuron, known to coordinate
head movement. In the Creamer LDS model they are off-connectome (Class 4). A naïve
anatomical reading is: "They're symmetric neurons with overlapping function; they
probably share inputs and co-activate, but there's no direct connection in the model."

**Standard functional connectivity:**
The Randi funatlas already shows RMEL→RMER wt q = 0.0002 — a highly significant functional
interaction. A standard interpretation would say: "RMEL and RMER are functionally coupled.
RMEL stimulation drives RMER response. The coupling may be indirect via shared circuits."

**Generic correlation:**
As bilateral homologs, they are expected to correlate (same behavioral drivers, shared
interneuron inputs). High correlation is expected and is not informative about mechanism.

### Framework Interpretation

**State-dependent conditional organization:**
ΔQ = −0.058, rank 32 of 1321 off-connectome pairs. The conditional coupling between RMEL
and RMER is **specifically stronger during dwelling than during roaming**, after removing
the shared effects of velocity, head angle, and pumping.

**CePNEM specificity:**
GCaMP ΔQ = 0.000 — the raw calcium traces show no state-dependent conditional coupling.
The signal only emerges in the CePNEM-residualized coordinate (shared variance not
explained by behavioral kinematics). This means the state-dependent coupling is in the
RESIDUAL dimension — the behavioral-strategy-correlated activity that cannot be
attributed to individual kinematic variables.

### What Did the Framework Add?

| Question | Naïve approach answer | Framework answer |
|---|---|---|
| Is RMEL-RMER functionally connected? | Yes (funatlas confirms) | Yes (same) |
| In which behavioral state is the coupling strongest? | Unknown (funatlas is state-agnostic) | **Dwelling** |
| Does behavioral variance explain the coupling? | Unknown | **No** (signal is CePNEM-specific) |
| Is the coupling neuropeptide-mediated? | Unknown | **Consistent** (DCV-dependent per funatlas unc-31) |
| Is this pair predicted by anatomical models? | **No** (off-connectome) | **Yes** (top 2.4% of pairs by ΔQ) |

**Key addition:** The framework converts a known-but-unexplained functional interaction
(funatlas: RMEL→RMER, highly significant) into a specific mechanistic prediction:
the interaction is strongest during dwelling and is invisible in raw calcium but present
in behavioral-residualized activity — consistent with a neuropeptide-based mechanism
that operates independently of immediate behavioral kinematics.

---

## Case 2: CEPDR–URXL

### Naïve Interpretation

CEPDR is a cephalic (sensory) neuron; URXL is an oxygen-sensing neuron involved in
social behavior and fat sensing. There is no direct predicted synaptic connection in
the Creamer model (Class 4, off-connectome). A naïve approach would not connect these.

### Framework Interpretation

ΔQ = −0.054 (rank 40). The conditional coupling between CEPDR and URXL is dwelling-dominant.
Both are sensory neurons that integrate environmental signals relevant to food/oxygen status.

**Added value:** Identifies a sensory–sensory state-dependent coupling between anatomically
unconnected neurons. Funatlas confirms CEPDR→URXL wt q = 0.0002 (6 observations) — a strong
functional interaction that was not predicted by anatomy. DCV status unknown (unmeasured).

---

## Case 3: I1R–RMDVR

### Naïve Interpretation

I1R is a pharyngeal motor/sensory neuron; RMDVR is a ring motor neuron. They are in different
anatomical compartments (pharynx vs. head ring). No Creamer-predicted connection (Class 4).
A naïve approach would not link them.

### Framework Interpretation

ΔQ = −0.049 (rank 50). Dwelling-dominant conditional coupling. DCV-dependent (wt significant,
unc-31 not). High observation confidence (occ = 57).

**Added value:** Identifies a pharyngeal–motor state-dependent coupling (invisible from anatomy)
that requires DCV signaling. This connecting pharyngeal and ring motor neurons during dwelling
is consistent with the known role of the pharyngeal pacemaker in feeding-state modulation.

---

## Case 4 (Negative Example): AVJR–AWBL

### Naïve Interpretation

AVJR is an interneuron; AWBL is an olfactory sensory neuron. The funatlas shows AVJR→AWBL
wt q = 0.0017 (37 observations). A standard approach would say: "AVJR drives AWBL in both
WT and unc-31" (unc-31 q = 0.012, also significant). This is a DCV-INDEPENDENT interaction.

### Framework vs Naïve

| Question | Naïve | Framework |
|---|---|---|
| Is AVJR-AWBL functionally connected? | Yes | Yes |
| DCV-dependent? | No (unc-31 still sig) | Same |
| Behavioral state-dependent coupling? | Unknown | Dwelling-dominant (ΔQ = −0.050) |

**Framework adds:** behavioral state-dependence. But the interaction is DCV-independent, so
the mechanism link to neuropeptide signaling is weaker. This case confirms the framework's
state prediction but does not provide mechanistic novelty.

---

## Summary

The framework's primary value-add over standard approaches is **state-specificity + residualization**:

1. **State-specificity**: The framework identifies WHEN an interaction is strongest (dwelling vs.
   roaming). Funatlas measures average functional connectivity; it cannot answer this question.

2. **Residualization**: CePNEM removes kinematic behavioral variance. The remaining signal reflects
   coordination that is not driven by common behavioral drivers. RMEL-RMER shows ΔQ ≠ 0 only in
   the residualized coordinate (GCaMP ΔQ = 0) — the framework reveals what raw calcium hides.

3. **Off-connectome prioritization**: By design, the framework tests off-connectome pairs. All
   confirmed cases (RMEL-RMER, CEPDR-URXL, I1R-RMDVR) are off-connectome. A connectome-first
   approach would not have prioritized these.

4. **Neuropeptide alignment**: The framework's state-dependent signal is enriched for PDF-annotated
   pairs (Phase 2 Stage 4A result). Combined with funatlas DCV dependence, this connects the
   statistical prediction to a specific signaling mechanism.
