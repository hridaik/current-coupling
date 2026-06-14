# Phase 5A.4 — Best Confirmed Case
Date: 2026-06-12

---

## Selected Case: RMEL–RMER

**ΔQ rank:** 32 of 1321 Class-4 pairs (top 2.4%)
**ΔQ_cepnem:** −0.058 (dwelling-dominant)
**ΔQ_gcamp:** 0.000 (CePNEM-specific)
**PDF annotation:** Yes (Bentley ESconnectome; both neurons express pdf-1 per CeNGEN)
**Randi annotation:** Yes (pair is in the unc-31 funatlas annotation set)

---

## 1. What the Framework Predicted

The state-conditioned precision matrix analysis (Phase 2) assigns RMEL–RMER a
conditional dependence change of ΔQ = −0.058 (Q_roam − Q_dwell). This value is
negative, meaning **the conditional coupling between RMEL and RMER is stronger
during dwelling than during roaming**, after removing the shared effects of velocity,
head angle, and pumping behavior.

RMEL–RMER ranks 32nd among all 1321 off-connectome pairs by |ΔQ|, placing it in the
top 2.4% of state-dependent conditional organization. It is classified as Class 4
(off-connectome in the Creamer LDS anatomical model), meaning no direct synaptic
connection is predicted.

The signal is **CePNEM-specific:** GCaMP ΔQ = 0.000. The state-dependent coupling is
absent in raw calcium traces and only emerges after residualizing out kinematic
behavioral covariates. This suggests the shared variance responsible for the coupling
is not explained by locomotion kinematics — consistent with a non-kinematic signaling
pathway such as neuropeptide volume transmission.

The pair is annotated in the Bentley ESconnectome PDF neuropeptide data: RMEL expresses
pdf-1 (confirmed by CeNGEN transcriptomics); RMER is predicted to express pdfr-1
(PDF receptor). This makes the framework prediction biologically specific: dwelling-state
conditional coupling via PDF neuropeptide.

---

## 2. What the Perturbation Atlas Observed

Randi et al. (2023), funatlas dataset (wt and unc-31 conditions):

**Wild-type:**
- RMEL→RMER: q = 0.0002 (HIGHLY SIGNIFICANT), 22 observations
- RMER→RMEL: q = 0.086 (not significant), 16 observations

The RMEL→RMER direction shows a strong, well-replicated functional propagation in wild-type
animals: optogenetic stimulation of RMEL reliably drives a calcium response in RMER.

**unc-31 mutant (DCV-defective, cannot release neuropeptides):**
- RMEL→RMER: q = 0.119 (NOT SIGNIFICANT), 5 observations
- RMER→RMEL: q = 0.0011 (significant), 6 observations

In unc-31 animals, the RMEL→RMER interaction IS ABSENT: the q-value rises from 0.0002
to 0.119. The interaction requires dense-core vesicle (DCV) release, consistent with
neuropeptide signaling (specifically PDF, which is released from DCVs).

Note: In unc-31, the reverse direction (RMER→RMEL, q = 0.0011) becomes significant.
This reveals that when DCV-mediated signaling is blocked, a previously masked interaction
in the opposite direction is unmasked — possibly a compensatory or competing pathway.

---

## 3. Why the Match Is Meaningful

**Three independent observations converge:**

(i) **Observational framework (this study):** RMEL and RMER show stronger conditional
coupling during dwelling than during roaming in freely-behaving whole-brain calcium imaging.
The coupling is only visible after behavioral residualization, suggesting it is not driven
by common locomotor inputs.

(ii) **Perturbation atlas (Randi 2023):** Optogenetic stimulation of RMEL drives a
calcium response in RMER in WT. This confirms that RMEL has functional influence over
RMER that is not predicted by direct anatomical connectivity.

(iii) **Genetic perturbation (unc-31):** The RMEL→RMER interaction requires DCV release.
This is the biochemical signature of neuropeptide signaling (PDF is packaged in DCVs
and released upon activity). When DCV release is blocked, the interaction disappears.

**Mechanistic hypothesis supported by all three:**
During dwelling, RMEL activity releases PDF neuropeptide via DCVs, which diffuses to
RMER (expressing pdfr-1) and modulates its activity. This neuropeptide-mediated
coordination does not manifest in raw calcium (RMEL and RMER respond similarly to
locomotor inputs during roaming) but becomes apparent in the conditional residual
structure during dwelling, when locomotor variance is low.

**The state-dependence (dwelling-dominant, not roaming-dominant) is the non-obvious
prediction.** The naive expectation for motor neuron bilateral homologs is stronger
coupling during roaming (when both are active for locomotion). The framework
predicts the opposite, and the funatlas DCV result provides the mechanism: the
coupling is neuropeptide-mediated and thus slower, more diffuse, and more prominent
during the low-locomotion dwelling state.

---

## 4. Why a Standard Approach Would Not Emphasize This

| Standard method | Prediction for RMEL-RMER | What it misses |
|---|---|---|
| Anatomical connectivity (Creamer model) | Off-connectome, no prediction | State-dependent off-connectome coupling |
| Pairwise GCaMP correlation | Non-zero correlation (bilateral homologs) | State-dependence, DCV-specificity |
| General functional connectivity (any-state) | Coupled (consistent with funatlas) | Dwelling-dominant specificity |
| Funatlas alone (no ΔQ) | Coupled in WT (q=0.0002) | State-dependence; residualized nature |
| Funatlas + unc-31 alone | DCV-dependent coupling | State-dependent specificity from this framework |

No single standard approach recovers all three properties simultaneously: (1) off-connectome,
(2) dwelling-dominant, (3) DCV-dependent. The framework + funatlas combination is required.

---

## Caveats

1. The unc-31 comparison has fewer observations (5) than the WT comparison (22). The
   q-value change (0.0002 → 0.119) is large and consistent with abolishment, but more
   unc-31 observations would strengthen confidence.

2. The framework does not directly confirm PDF as the specific mediator — only that DCV
   release is required. Other DCV-packaged signals could also mediate the interaction.

3. The RMER→RMEL direction emerging in unc-31 (q=0.0011) suggests a complex bidirectional
   interaction that is not fully explained by the unidirectional PDF model.
