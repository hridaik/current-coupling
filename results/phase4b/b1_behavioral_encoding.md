# Phase 4B.1 — Behavioral Encoding Geometry
Date: 2026-06-12

---

## Method

For each of the 61 neurons, velocity encoding weight c_v was extracted from the CePNEM
NL10d posterior median (`params_med[1]`) stored in per-recording residual files.
Values were averaged across epochs within each recording, then averaged across all
recordings in which that neuron was observed. Head angle (c_θh) and pumping (c_P)
were extracted analogously from `params_med[2]` and `params_med[3]`.

All 61 neurons have at least 1 recording; most have 30+ recordings.

---

## Velocity Encoding (c_v): Population Distribution

The distribution of c_v across the 61-neuron population is centered near zero with
substantial spread, consistent with a mixed population spanning roaming-active and
dwelling-active neurons.

- **Population mean:** +0.095
- **Population std:** ~0.18
- **Range:** −0.393 to +0.528

### Top Velocity-Positive Neurons (active during roaming)

| Neuron | c_v | c_θh | c_P | n_recs | Cell type |
|---|---|---|---|---|---|
| AWBL | +0.528 | — | — | 36 | Amphid wing sensory |
| AVER | +0.518 | — | — | 33 | Command interneuron, locomotion |
| RICL | +0.515 | — | — | 35 | Ring interneuron |
| OLQVR | +0.443 | −0.030 | +0.182 | 32 | Mechanosensory |
| IL1R | +0.443 | — | — | 32 | Labial mechanosensory |
| OLQDL | +0.414 | — | — | 39 | Mechanosensory |
| NSML | +0.400 | — | — | 38 | Neurosecretory motor (serotonin) |
| IL2VL | +0.392 | — | — | 32 | Inner labial sensory |
| RMER | +0.367 | −0.005 | −0.017 | 38 | Ring motor, GABA |
| OLLR | +0.350 | — | — | 34 | Outer labial sensory |

**Biological interpretation:** AVE and RIC are known locomotion command interneurons;
their roaming-dominant encoding is consistent with their role in forward locomotion
initiation. NSM serotonin neurons are velocity-positive, suggesting serotonin signaling
tracks locomotion state (roaming). RMER (pdf-1 expressing ring motor) is velocity-positive.

### Top Velocity-Negative Neurons (active during dwelling)

| Neuron | c_v | c_θh | c_P | n_recs | Cell type |
|---|---|---|---|---|---|
| RMDVL | −0.393 | — | — | 33 | Ring motor, GABA |
| RMDDR | −0.212 | — | — | 32 | Ring motor, GABA |
| AIBL | −0.186 | — | — | 38 | Locomotion inhibitory interneuron |
| AVJR | −0.159 | — | — | 32 | Ventral cord interneuron |
| AVDL | −0.153 | +0.212 | +0.099 | 37 | ACh ventral cord interneuron (pdf-2 source) |
| RIVL | −0.144 | — | — | 38 | Ring interneuron, head movement |
| AVAR | −0.104 | — | — | 35 | Command interneuron (reversal) |
| IL2DL | −0.090 | — | — | 39 | Inner labial sensory |
| RID | −0.083 | +0.024 | +0.050 | 38 | DCV modulator (pdf-1 + pdf-2 source) |
| NSMR | −0.070 | — | — | 36 | Neurosecretory motor (serotonin) |

**Biological interpretation:** AVAR (reversal command) is velocity-negative, consistent
with its role in backward locomotion and pausing during dwelling. AIBL is a known
locomotion suppressor. AVDL (pdf-2 source) and RID (pdf-1+pdf-2 source) are both
dwelling-active — these PDF-producing neurons are MORE active during the dwelling state.
NSMR serotonin neuron is velocity-negative (the two NSM neurons have opposite sign:
NSML positive, NSMR negative — possibly reflecting left/right asymmetry or labeling
variability across recordings).

---

## PDF-Circuit Neuron Encoding

The neurons most relevant to the Phase 2 exploratory PDF signal:

| Neuron | Role | c_v | c_θh | c_P | Interpretation |
|---|---|---|---|---|---|
| ADEL | pdf-1 source, dopaminergic mechanosensor | +0.215 | +0.009 | +0.139 | Velocity-positive (roaming-active) |
| URYVR | pdfr-1 target, O2/social integrator | −0.068 | −0.213 | −0.084 | Weakly velocity-negative (dwelling-active) |
| URYDL | pdfr-1 target, O2/social integrator | +0.012 | +0.163 | +0.175 | Near-zero velocity encoding |
| RMEL | pdf-1 source + pdfr-1 target | +0.074 | −0.078 | +0.236 | Weakly velocity-positive |
| RMER | pdf-1 source | +0.367 | −0.005 | −0.017 | Strongly velocity-positive (roaming-active) |
| RID | pdf-1 + pdf-2 source | −0.083 | +0.024 | +0.050 | Weakly velocity-negative (dwelling-active) |
| AVDL | pdf-2 source | −0.153 | +0.212 | +0.099 | Velocity-negative, head-encoding |
| URXL | pdfr-1 target, O2 integrator | +0.261 | −0.122 | +0.091 | Velocity-positive |
| OLQVR | pdfr-1 target, mechanosensory | +0.443 | −0.030 | +0.182 | Strongly velocity-positive |

**Key observation:** The three highest-|ΔQ| PDF pairs involve neurons with OPPOSITE or
WEAK velocity encoding relative to ADEL:

- **ADEL–URYVR:** ADEL is velocity-positive (+0.215), URYVR is velocity-negative (−0.068).
  Scalar alignment = +0.215 × (−0.068) = −0.015 (anti-aligned).
- **ADEL–URYDL:** ADEL velocity-positive (+0.215), URYDL near-zero (+0.012).
  Scalar alignment = +0.215 × 0.012 = +0.003 (effectively unaligned).
- **ADEL–RMEL:** ADEL velocity-positive (+0.215), RMEL weakly positive (+0.074).
  Scalar alignment = +0.215 × 0.074 = +0.016 (weakly aligned, modest).

This means the strongest PDF-associated dwelling-dominant conditional dependence connects
neurons that are either anti-aligned or unaligned in velocity encoding.

---

## Summary

The 61-neuron population spans a broad range of behavioral encoding, from strongly
velocity-positive (AVER, AWBL, RMER) to strongly velocity-negative (RMDVL, AIBL).
The PDF-circuit neurons are distributed across this spectrum: ADEL and RMER are
velocity-positive (roaming-active), while RID and AVDL are dwelling-active.
URYVR, URYDL, and RMEL occupy the weakly-encoded middle range.

This encoding heterogeneity is the substrate for the Phase 4B alignment analysis.
