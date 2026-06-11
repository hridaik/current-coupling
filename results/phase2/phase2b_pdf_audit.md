# Phase 2B — PDF Follow-Up Audit
Date: 2026-06-01
Status: Read-only audit. No enrichment tests run. No files modified.

---

## 1. Overview

This audit characterizes the exploratory Bentley PDF signal identified in Stage 4A
(CePNEM AUROC=0.556, p_deg=0.023; Fisher OR=5.456, p_deg=0.008) by identifying the
exact pairs driving the signal, their source/target neuron identities, and cross-referencing
against perturbation atlas data and circuit literature already present in the repository.

**Audit goal:** Determine whether the PDF signal corresponds to known causal propagation
structure. No new hypothesis testing is performed here.

---

## 2. The 61 Bentley PDF Class 4 Pairs — Structure

### 2.1 Source and target neurons

Five source neurons account for all 61 Bentley PDF Class 4 pairs:

| Source | Ligand | Class 4 directed edges | Neurotransmitter | Cell type |
|---|---|---|---|---|
| RID | pdf-1 + pdf-2 | 28 | Unknown (orphan) | Ring interneuron, dorsal cord projector |
| AVDL | pdf-2 | 14 | ACh | Ventral cord interneuron |
| ADEL | pdf-1 | 12 | Dopamine | Anterior deirid mechanosensor |
| RMEL | pdf-1 | 12 | GABA | Head ring motor neuron |
| RMER | pdf-1 | 12 | GABA | Head ring motor neuron |

All five source neurons are pdfr-1-negative (none appear in pdfr-1 CeNGEN expression at conservative threshold). All target neurons are pdfr-1-expressing per CeNGEN.

### 2.2 Structure by ΔQ

Of the 61 PDF Class 4 pairs, only 17 have nonzero CePNEM ΔQ (zero-ΔQ pairs contribute
to AUROC through their ranking among non-PDF pairs but not as signal carriers). The
top-10 by |ΔQ_cepnem|:

| Rank | Pair | ΔQ_cep | ΔQ_gca | Source | Target | Ligand |
|---|---|---|---|---|---|---|
| 1 | ADEL–URYVR | −0.1222 | −0.0853 | ADEL | URYVR | pdf-1 |
| 2 | ADEL–URYDL | −0.0980 | −0.0841 | ADEL | URYDL | pdf-1 |
| 3 | ADEL–RMEL | −0.0957 | −0.0824 | ADEL | RMEL | pdf-1 |
| 4 | RMEL–URYDL | −0.0754 | −0.1259 | RMEL | URYDL | pdf-1 |
| 5 | RMEL–URYVR | −0.0701 | −0.1232 | RMEL | URYVR | pdf-1 |
| 6 | RMEL–RMER | −0.0579 | +0.0000 | RMEL↔RMER | bilateral | pdf-1 |
| 7 | AVDL–URYDL | −0.0558 | −0.0240 | AVDL | URYDL | pdf-2 |
| 8 | ADEL–URXL | −0.0450 | −0.1516 | ADEL | URXL | pdf-1 |
| 9 | RID–URXL | −0.0396 | −0.0220 | RID | URXL | pdf-1 + pdf-2 |
| 10 | ADEL–OLQVR | −0.0215 | +0.0000 | ADEL | OLQVR | pdf-1 |

Fisher top-K finding: 4 of the top-20 CePNEM |ΔQ| pairs overall are PDF-annotated — ADEL–URYVR (rank 5), ADEL–URYDL (rank 9), ADEL–RMEL (rank 10), RMEL–URYDL (rank 16). All four are ADEL- or RMEL-centric.

### 2.3 Sign direction

**All 14 non-zero negative ΔQ pairs have ΔQ < 0 (14/17 nonzero; the 3 positive are low-magnitude).**

ΔQ = Q_roam − Q_dwell < 0 means conditional dependence is **stronger during dwelling than
during roaming**. For all top ADEL-centric and RMEL-centric pairs:
- Q_roam ≈ 0 (essentially decoupled during roaming)
- Q_dwell < 0 (inversely coupled during dwelling)

This is a consistent directional signal: the PDF-linked pairs are **specifically decoupled
during roaming** relative to their dwelling state.

---

## 3. Which Neurons Dominate the Signal?

The Fisher K=20 enrichment result is driven entirely by ADEL-centric pairs.
ADEL's 5 top non-synaptic Class 4 partners with nonzero ΔQ are: URYVR, URYDL, RMEL,
URXL, OLQVR — all pdf-1/pdfr-1 directed edges in the Bentley atlas.

**ADEL is a dopaminergic anterior deirid mechanosensory neuron.** It is not primarily
known as a neuromodulatory interneuron. Its pdf-1 expression (CeNGEN conservative
threshold: ADEL expresses pdf-1 in tph-1/cat-1 co-expression neighborhood) makes it
a potential PDF co-transmitter source.

**ADEL's synaptic partners in the 61-neuron subgraph** include AVAL, AVAR, AVDL, AVEL,
CEPDL, FLPL, IL1L, OLLL, RIVL, RMDL, RMER, URBL — all on-connectome and therefore
excluded from Class 4. ADEL's Class 4 (off-connectome) interactions with URY, RMEL,
URXL, and OLQ neurons are not direct synaptic connections but would require
volume transmission or polysynaptic propagation.

**RID is annotated as:** "Predominantly contains dense-core vesicles, modulate locomotion"
(Creamer anatomical data, citing Lim et al. 2016). RID expresses both pdf-1 and pdf-2.
RID is the second-largest contributor to nonzero CePNEM ΔQ in PDF pairs (8 nonzero pairs).

---

## 4. Are These Neurons Known PDFR-1-Expressing Targets?

**Yes, directly.** From CeNGEN (conservative threshold):

| Target neuron | PDFR-1 expression | In top PDF ΔQ pairs |
|---|---|---|
| URYVR | YES (pdfr-1 expressed) | Ranks 1, 5 |
| URYDL | YES | Ranks 2, 4, 7 |
| RMEL | YES | Ranks 3, 4–6 |
| URXL | YES | Ranks 8, 9 |
| OLQVR | YES | Rank 10 |

All five top-signal targets are confirmed pdfr-1-expressors at the conservative CeNGEN
threshold. The signal structure (ADEL/RMEL → pdfr-1 neurons) is entirely consistent
with the Bentley PDF annotation — this is not a mislabeling artefact.

---

## 5. Are These Known Roaming/Dwelling Regulators?

### ADEL (dopamine, mechanosensor)
ADEL is a lateral mechanosensory neuron in the head. Dopaminergic signaling is known
to regulate locomotion state — dopamine mutants show altered roaming/dwelling balance.
ADEL is one of the dopaminergic neurons (alongside CEP and ADE bilaterals) that sense
substrate contact and mediate dopamine-dependent slowing (mechanosensory-induced
dwelling). ADEL's state-dependent decoupling from URY/RMEL during roaming is
consistent with reduced dopaminergic/extrasynaptic tone during high-locomotion states.

### RID (orphan modulator, dense-core vesicles)
RID was identified by Lim et al. (2016, eLife) as a single unpaired neuron that
"promotes locomotion through dense-core vesicle-mediated signaling." RID is specifically
implicated in regulating forward versus reversal locomotion — not roaming vs. dwelling
per se, but locomotion initiation. RID expresses pdf-1 + pdf-2 and is connected to the
PDF signaling system.

### RMEL/RMER (GABAergic ring motor neurons)
RMEL and RMER are bilateral GABAergic head ring motor neurons that control head
oscillation amplitude. They are part of the mechanosensory-motor circuit. Their
PDFR-1 expression suggests they receive PDF signaling.

### URY neurons (URYDL, URYVR, URXL)
URY neurons are head neurons involved in O2 sensing and locomotion. URX (left) and URY
are part of the aerotaxis and social behavior circuit that responds to O2 gradients and
regulates dwelling vs. dispersal behavior. URXL is an O2/CO2/social signal integrator.
PDFR-1 expression in URX/URY is documented in the CeNGEN atlas.

**The functional context is coherent:** ADEL (dopaminergic mechanosensor) → URY/URX
(O2/social signal integrators, PDFR-1+) connects a substrate-sensing dopaminergic
neuron to locomotion-state-modulating sensory interneurons via extrasynaptic PDF.
The dwelling-dominant co-modulation (ΔQ < 0) is consistent with increased
PDF/PDFR-1 tone during dwelling states.

---

## 6. Perturbation Atlas Cross-Reference (Randi/Leifer funatlas)

### 6.1 Coverage of ADEL→URY measurements

| Measurement | q_wt | q_unc31 | dFF_wt | occ_wt | Notes |
|---|---|---|---|---|---|
| ADEL→URYVR | — | — | — | 0 | **Not measured in unc-31 condition** |
| ADEL→URYDL | — | — | — | 0 | **Not measured** |
| ADEL→RMEL | 0.492 | 0.371 | +0.026 | 5 | Measured, not significant |
| ADEL→URXL | 0.534 | nan | −0.030 | 7 | WT measured; unc-31 not measured |

**Critical gap: ADEL→URYVR and ADEL→URYDL have zero observations in funatlas.** These
are the highest-ΔQ PDF pairs in the CePNEM analysis, but they have never been measured
in the Randi/Leifer atlas (neither wt nor unc-31 condition).

### 6.2 Coverage of RID and RMEL/RMER

| Measurement | q_wt | q_unc31 | dFF_wt | occ_wt | Notes |
|---|---|---|---|---|---|
| RMEL→RMER | **0.000** | 0.119 | +0.094 | 22 | **wt significant** |
| RMER→RMEL | 0.086 | **0.001** | +0.072 | 16 | **unc-31 significant** |
| RMER→URYVR | **0.000** | nan | +0.151 | 8 | **wt significant; unc-31 unmeasured** |
| RMEL→OLQVR | **0.028** | nan | +0.222 | 13 | **wt significant** |
| RMER→OLQVR | **0.036** | nan | +0.080 | 13 | **wt significant** |
| RMEL→OLLL | 0.396 | **0.002** | +0.104 | 19 | **unc-31 significant** |
| RMER→OLLL | 0.177 | **0.012** | +0.072 | 19 | **unc-31 significant** |
| RMER→I1L | 0.462 | **0.049** | +0.078 | 6 | **unc-31 significant** |
| RID→AVAR | **0.020** | 0.763 | +0.088 | 2 | **wt significant; low obs.** |

**Key observations:**
- RMEL↔RMER are functionally connected in funatlas (wt significant), with RMER→RMEL
  also unc-31 sensitive. This confirms the RMEL–RMER bidirectional ΔQ pair (rank 6)
  has a measured functional substrate.
- RMER→URYVR is wt-significant (q=0.000), the strongest RMER→target signal in funatlas.
  This is consistent with RMEL–URYVR and RMER–URYVR ΔQ being large (ranks 5, in top PDF).
- RMEL/RMER → OLQ neurons show wt-significant propagation; RMEL/RMER → OLLL is also
  unc-31-sensitive, indicating dense-core vesicle contribution.

### 6.3 ADEL's unc-31 signature

ADEL → any target: **zero unc-31-significant targets** in funatlas. ADEL has 5 wt-significant
targets (ADAL, ADER, AINL, AQR, FLPL — none in the 61-neuron PDF-target set). This
means:
- Either ADEL's PDF signaling to URY/RMEL is not captured by the Randi atlas
  (because those pairs were never measured, not because unc-31 was tested and failed)
- Or ADEL releases pdf-1 constitutively and the effect is unc-31-independent in the
  Randi experiment design

The zero-observation gap (occ1=0 for ADEL→URYVR, ADEL→URYDL) is the operationally
important fact: these are **untested pairs**, not failed tests.

---

## 7. Findings: Already-Tested / Exploratory / Genuinely New

### 7.1 Already-tested findings (in existing resources)

1. **RMEL↔RMER functional connectivity** — confirmed by Randi funatlas (q_wt=0.000).
   The RMEL–RMER ΔQ pair (rank 6) has a known wt functional substrate.

2. **RMER→URYVR functional propagation** — wt-significant in funatlas (q=0.000).
   RMER activates URYVR in the WT condition. The RMEL/RMER–URY ΔQ pairs (ranks 4–5)
   involve a neuron pair where directional functional connectivity is documented.

3. **RMEL/RMER → OLLL is unc-31-sensitive** — funatlas q_unc31 < 0.01.
   Dense-core vesicle release from RMEL/RMER contributes to OLLL activation.

4. **RID is a locomotion modulator using dense-core vesicles** — Lim et al. 2016.
   RID's role in locomotion is established, and its pdf-1/pdf-2 expression is documented.

5. **URX/URY neurons integrate O2 signals and modulate locomotion state** — established
   in multiple papers. PDFR-1 expression in these neurons has been documented.

### 7.2 Exploratory observations (from this analysis)

1. **ADEL is the primary source neuron for the Fisher K=20 enrichment.** 4 of the 4
   top-K-enriched pairs involve ADEL as pdf-1 source or RMEL as intermediate. ADEL's
   role as a pdf-1 source for URY/RMEL neurons has not been characterized experimentally.

2. **The ΔQ direction is consistently dwelling-dominant for all top PDF pairs.**
   ADEL–URY, RMEL–URY, and RID–URX pairs show Q_roam ≈ 0, Q_dwell < 0.
   This means the conditional dependence is a dwelling-specific phenomenon — the
   ADEL/RMEL → pdfr-1 co-modulation exists during dwelling but disappears during roaming.

3. **The structure involves ADEL (dopamine DA) → pdfr-1 neurons via pdf-1, not via
   dopamine.** ADEL's synaptic targets (AVAL, AVAR, AVDL, AVEL, OLLL, etc.) are all
   on-connectome and excluded from Class 4. The off-connectome ΔQ signal is exclusively
   associated with ADEL's extrasynaptic pdf-1 projections.

4. **RID's pdf-1/pdf-2 → URXL signal is a second cluster** (rank 9): RID → URXL with
   both pdf-1 and pdf-2 directed edges. RID–URXL has low funatlas observations (occ=2)
   and borderline non-significant wt.

### 7.3 Genuinely new predictions

**Prediction 1 (highest priority):**
ADEL → URYDL and ADEL → URYVR exhibit dwelling-dominant conditional dependence
(Q_dwell < Q_roam for both pairs). These pairs have never been measured in the
Randi/Leifer atlas (occ1 = 0 for both). The prediction from the CePNEM ΔQ signal is:
optogenetic or electrical stimulation of ADEL should produce a stronger co-activation
signal in URYDL/URYVR during dwelling bouts than during roaming bouts, and this
coupling should depend on dense-core vesicle release (unc-31-sensitive).

This is a **state-conditioned** prediction that the Randi atlas was not designed to test
(it measures global, state-averaged functional propagation). A state-conditioned
optogenetics experiment targeting ADEL in freely-behaving animals would be the
appropriate test.

**Prediction 2:**
RID (pdf-1 + pdf-2 source, locomotion modulator) → URXL (pdf-1/pdfr-1 connection,
rank 9 in ΔQ). The prediction: RID→URXL functional propagation is stronger during
dwelling and would be detectable in a state-conditioned analysis. This pair has
insufficient Randi atlas coverage (occ_wt=2) to assess.

**Prediction 3 (lower confidence):**
The entire ADEL-centric PDF signal is dwelling-dominant. If pdf-1 signaling is
specifically elevated during dwelling (consistent with reduced locomotion/
mechanosensory input during dwelling), then ADEL-pdf-1 → pdfr-1 target co-activation
should be state-selective. This is consistent with the known role of PDF in circadian
rhythms and state persistence, applied to the C. elegans roaming/dwelling context.

---

## 8. Can a Concrete Prediction Use Existing Perturbation-Atlas Data?

**Partially, but not fully.** The perturbation atlas (funatlas) measures state-averaged
functional propagation — it does not condition on behavioral state. To test the specific
prediction (dwelling-dominant ADEL → URY coupling), state-conditioned analysis of the
funatlas data would be needed.

One accessible check: the funatlas records per-pair observation counts (occ1) and
potentially the behavioral state during each recording. If the funatlas data can be
stratified by behavioral state post-hoc, the ADEL→URYDL/URYVR pairs could be tested
without new experiments. However, this would require access to the raw funatlas
trial-level data, which is not present in the current repository (only summary statistics
are available: dFF, q, occ1, not trial-level traces).

The RMEL/RMER → URYVR connection is the most directly testable: funatlas already has
8+ observations of RMER→URYVR (q_wt=0.000, significant in wt). Stratifying these
existing observations by behavioral state during stimulation would test whether the
RMEL–URY coupling is state-dependent.

---

## 9. Summary for Report

| Question | Answer |
|---|---|
| Which neurons dominate the PDF signal? | ADEL (pdf-1 source, DA sensory), RMEL/RMER (pdf-1 source, GABA motor), RID (pdf-1+pdf-2 source, locomotion modulator) |
| Are targets confirmed PDFR-1-expressing? | Yes — URYVR, URYDL, RMEL, URXL, OLQVR all express pdfr-1 at conservative CeNGEN threshold |
| Are these known roaming/dwelling regulators? | Partially. ADEL-dependent dopaminergic slowing is established. RID is a locomotion modulator. URX/URY regulate aerotaxis and locomotion state. |
| Do perturbation-atlas resources contain measurements? | ADEL→URYVR/URYDL: **zero observations** — never measured. RMER→URYVR: measured and wt-significant. RMEL/RMER→OLQ: measured, some unc-31-sensitive. |
| Can a concrete prediction be formulated? | Yes. ADEL→{URYDL, URYVR} dwelling-dominant functional connectivity, unc-31-sensitive, not captured by state-averaged Randi atlas. Requires state-conditioned experiment. |

---

*Read-only audit. No enrichment tests run. No files modified. No new hypotheses registered.*
*All statistics from Stage 4A results. All cross-references from files already in repository.*
