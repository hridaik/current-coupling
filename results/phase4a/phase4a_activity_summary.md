# Phase 4A Activity Summary
Date: 2026-06-04
Authorization: Phase 4A

---

## The Question

What does the ADEL–URY activity organization actually look like?

Is it:
- **A**: Shared state modulation (all neurons change together with state)
- **B**: State-dependent coordination (neurons have state-specific relationships)
- **C**: Coherent functional circuit (reproducible inter-neuron structure)

---

## Evidence Summary

| Analysis | Key Result | Supports |
|---|---|---|
| A: Activity profiles | No significant state-dependent mean differences (all p > 0.05) | Against A |
| A: Direction | URYVR/URYDL trend up in roam; RMEL trends down; ADEL flat | Against A (asymmetric) |
| B: Cross-correlations | ADEL–RMEL: 2× higher peak during roam (0.189 vs 0.090) | For B |
| B: ADEL–URY | Modestly higher in roam (+10–35%), near-zero lag | Weak for B |
| C: D→R transitions | RMEL changes first (0.2s), then URY sensors (2.6–3.4s) | For C |
| C: R→D transitions | URYVR first (1.4s), ADEL second (2.0s), RMEL last (3.8s) | For C |
| D: Module correlation | ADEL–URY: r≈0.16 in both states, p=0.975 | Against B/C at module level |

---

## Interpretation

### Best-Supported Answer: **B — State-dependent coordination (weak)**

**Evidence FOR B:**
1. The temporal ordering at state transitions is reproducible and asymmetric:
   - D→R: motor (RMEL) leads → sensors (URYVR, URXL) follow
   - R→D: sensor (URYVR) leads → dopaminergic (ADEL) follows → motor (RMEL) last
   
   This temporal structure implies different functional roles at each transition direction.

2. ADEL–RMEL cross-correlation is substantially higher during roaming (2×), suggesting
   these two PDF-producing neurons are more strongly co-regulated during locomotion.

3. The Phase 2 ΔQ result (ADEL–URYVR conditional coupling stronger during dwelling,
   rank 5) provides independent evidence for state-dependent conditional structure
   that is not captured by simple marginal correlation.

**Evidence AGAINST A (shared state modulation):**
- The network does not show uniform directional changes with state: URYVR/URYDL trend
  UP during roaming while RMEL trends DOWN. If this were simple state modulation, all
  neurons should change in the same direction.

**Evidence AGAINST C (coherent functional circuit):**
- No significant gross module coordination difference (p = 0.975): ADEL and URY_URX
  have essentially the same correlation in both states at the module level.
- All cross-correlations are weak (0.07–0.19), indicating the relationship is
  not strong enough to suggest dedicated circuit connectivity.
- ADEL does not show a clear response at dwell→roam transitions, weakening the
  hypothesis that ADEL is a primary driver.

---

## Observations vs Interpretations vs Predictions

### Observations (directly measured)

1. URYVR and URYDL activity is directionally higher during roaming than dwelling,
   but not significantly so (p = 0.14, 0.19).
2. ADEL activity does not significantly differ between states (p = 0.87).
3. ADEL–RMEL cross-correlation is ~2× higher during roaming.
4. At R→D transitions: URYVR changes ≈1.4s before ADEL, ADEL ≈0.6s before URXL.
5. At D→R transitions: RMEL changes at the transition; ADEL shows no reliable response.
6. ADEL–URY module correlation is +0.16 in both states (p = 0.975).

### Interpretations (from observations, less certain)

1. **The temporal asymmetry at transitions suggests functional directionality**:
   - During R→D: sensory detection (URYVR) appears to precede ADEL activation,
     consistent with URY→ADEL signaling (possibly through pdfr-1 → downstream → ADEL).
   - During D→R: ring motor (RMEL) leads, consistent with locomotor initiation driving
     sensory updates.

2. **ADEL–RMEL co-regulation during roaming** may reflect shared locomotor drive to
   both PDF-producing neurons, while dwelling reveals a more specific conditional
   structure (ΔQ) once shared variance is removed.

3. **The Phase 2 ΔQ signal (ADEL–URYVR, ADEL–URYDL) is a conditional, multi-neuron
   effect** that cannot be reduced to pairwise marginal correlations or module
   mean-activity differences. The signal is in the precision structure of the
   network, not in simple co-activation patterns.

### Predictions (from interpretation, more speculative)

1. The ≈1.4–2.0s lag between URYVR and ADEL at R→D transitions might reflect a
   real signaling pathway (neuropeptide or direct synaptic), but the lag is short
   relative to neuropeptide signaling timescales (typically seconds to minutes).

2. If ADEL is receiving input from URY at R→D transitions (consistent with the
   temporal order), this could represent a feedback pathway in the PDF circuit
   where O₂-sensing URY neurons signal back to the PDF-producing ADEL through
   the locomotion state network.

These predictions are NOT tested in Phase 4A and require held-out evaluation.

---

## Limitations

1. CePNEM residuals are model-based activity estimates, not raw fluorescence. Any
   inaccuracy in the CePNEM model for these specific neurons would affect results.
2. "Onset" detection uses a heuristic threshold (0.3 baseline-normalized units);
   different thresholds would shift estimates.
3. 22 recordings represent a single experimental protocol; the temporal structure
   (roaming-early pattern, Phase 2D) could bias transition analysis.
4. The lack of significant mean activity differences (Analysis A) could reflect
   insufficient power (22 recordings) or genuine biological absence.

---

## Do NOT Pursue Without Authorization

- Held-out ADEL pair evaluation (ADEL–URYVR, ADEL–URYDL ΔQ_obs not consulted)
- Perturbation predictions
- Phase 4A is descriptive characterization only

---

*Phase 4A: STOP. Awaiting human review.*
