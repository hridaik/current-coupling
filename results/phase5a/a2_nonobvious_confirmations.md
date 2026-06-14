# Phase 5A.2 — Non-Obvious Confirmations
Date: 2026-06-12

---

## Question

Which confirmed pairs would NOT have been obvious from:
- anatomical connectivity alone
- pairwise activity alone
- generic functional connectivity

---

## Leading Case: RMEL–RMER

### What Would Standard Approaches Say?

**Anatomical connectivity:** RMEL and RMER are bilateral homologs of the ring motor neuron.
In the Creamer LDS model — the anatomical backbone used in this analysis — they are classified
as **Class 4 (off-connectome)**. Their direct synaptic connection is absent or absent from
the LDS model. A naïve anatomy-based prediction would not flag them as functionally coupled
in a non-trivial way (beyond bilateral homolog correlation).

**Pairwise activity:** Phase 4A showed that the ADEL-PDF circuit neurons do not show
strong pairwise correlations. More generally, bilateral homologs tend to co-activate
(shared input), which would produce a non-zero raw correlation at all times — not
specifically state-dependent coupling. A pure pairwise correlation analysis would not
reveal the dwelling-specific nature of the interaction.

**Generic functional connectivity:** The Randi funatlas wt q = 0.0002 for RMEL→RMER
means the funatlas itself confirms functional propagation. But the funatlas does not
ask about STATE DEPENDENCE — it measures functional propagation in a single average
condition. Standard functional connectivity analyses (resting-state correlation, average
coherence) would confirm the pair is connected but would not identify WHEN that
connection is most active.

### What Did the Framework Add?

The framework uniquely identifies:
1. **State-dependent specificity:** ΔQ = −0.058 means the conditional coupling between
   RMEL and RMER is significantly stronger during DWELLING than during roaming.
2. **After-residualization signal:** GCaMP ΔQ = 0.000. The state-dependent coupling
   is invisible in raw calcium traces and only emerges after CePNEM residualization
   (removal of velocity, head angle, and pumping covariates). This means the
   coupling exists in the UNEXPLAINED variance — shared conditional dependence
   that is not driven by common behavioral correlates.
3. **Neuropeptide mechanism specificity:** Combined with the funatlas DCV result
   (unc-31 abolishes the RMEL→RMER interaction), the framework's signal aligns with
   a DCV-mediated mechanism, consistent with PDF neuropeptide signaling between
   pdf-1-expressing RMEL and pdfr-1-expressing RMER.

**Key insight:** A standard analysis would identify RMEL-RMER as functionally coupled
(funatlas confirms this). But it would not predict:
- That the coupling is specifically stronger during dwelling
- That it is absent from raw calcium but present after behavioral residualization
- That this aligns with a neuropeptide (DCV-dependent) mechanism

The framework makes a non-obvious QUANTITATIVE, STATE-SPECIFIC prediction
that is independently validated by the perturbation atlas.

---

## Why Is State-Dependence Non-Obvious?

RMEL and RMER are ring motor neurons involved in head movement. During roaming, the
animal makes directed head sweeps and body undulations — both RMEL and RMER would be
jointly recruited for locomotion. One might naively expect RMEL-RMER coupling to be
STRONGER during roaming (when motor activity is high) rather than during dwelling.

The framework predicts the opposite: dwelling-dominant conditional coupling (ΔQ < 0).
This is non-obvious because:
1. Dwelling involves food exploitation and reduced locomotion — both neurons are less
   actively recruited for movement
2. The conditional coupling during dwelling (in the behavioral-residualized coordinate)
   reflects shared conditional variance NOT explained by movement
3. This shared variance during dwelling may represent PDF neuropeptide signaling
   (RMEL releases PDF, RMER receives it via pdfr-1) that is obscured during roaming
   by the shared locomotor drive

---

## Secondary Cases: Off-Connectome Specificity

Both RMEL-RMER and CEPDR-URXL are **off-connectome** pairs (Class 4 in the Creamer LDS
model). The funatlas confirms they have functional interactions. This means the
functional interaction occurs without a direct (Creamer-predicted) synaptic connection
— consistent with volume transmission / neuropeptide signaling.

A naïve approach using only the connectome to prioritize pairs would miss both.

---

## Negative Case: AVJR–AWBL

By contrast, AVJR–AWBL (rank 47) shows both WT and unc-31 significant interactions.
This is a DCV-independent interaction — consistent with gap junctions or classical
neurotransmitters. This is the type of pair that standard connectome-based approaches
might also find, and represents a less interesting case for the framework's added value.

---

## Summary

RMEL–RMER is the most non-obvious confirmed case because:
1. Off-connectome (anatomy doesn't predict it)
2. State-dependent in the non-obvious direction (dwelling, not roaming)
3. Only visible after behavioral residualization (GCaMP ΔQ = 0)
4. DCV-dependent (requires neuropeptide mechanism, confirmed by unc-31)
5. Biologically interpretable (both neurons express pdf-1; RMER expresses pdfr-1)
