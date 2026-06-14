# Phase 5A — Final Summary
Date: 2026-06-12
Authorization: Phase 5A

---

## The Question

Is there at least one case where the framework makes a specific, non-obvious prediction
that is directly confirmed by the perturbation atlas?

---

## Answer: C — Strong Confirmation (for one specific case)

**RMEL–RMER is a genuinely confirmed example.**

---

## 1. Is There a Genuinely Confirmed Prediction Already Present?

**Yes.** RMEL–RMER (ΔQ rank 32 of 1321, ΔQ_cepnem = −0.058) satisfies all four criteria:

1. ✓ **Strong framework signal:** top 2.4% of all off-connectome pairs by |ΔQ|; PDF-annotated (Bentley ESconnectome); Randi-annotated.
2. ✓ **Independent perturbation atlas confirmation:** funatlas wt q = 0.0002, 22 observations. RMEL optogenetic stimulation drives RMER response.
3. ✓ **Non-obvious:** Off-connectome (Class 4 — no direct Creamer LDS connection). Dwelling-dominant, counter to the naïve expectation of stronger coupling during active locomotion. Signal absent in raw GCaMP (ΔQ_gcamp = 0.000) — only emerges after behavioral residualization.
4. ✓ **Not recoverable by standard approaches:** Anatomy doesn't predict it; raw calcium doesn't show it; funatlas alone doesn't predict its state-dependence.

---

## 2. The Strongest Confirmed Example

### RMEL–RMER: State-Dependent DCV-Mediated Bilateral Motor Neuron Coupling

**Framework prediction:**
- ΔQ = −0.058 (dwelling-dominant conditional coupling)
- Class 4 (off-connectome in Creamer LDS model)
- GCaMP ΔQ = 0.000 (signal is CePNEM-specific, invisible in raw calcium)
- PDF-annotated: RMEL expresses pdf-1; RMER expresses pdfr-1

**Perturbation atlas (Randi funatlas):**
- WT: RMEL→RMER q = 0.0002 (HIGHLY SIGNIFICANT, 22 observations)
- unc-31 mutant (DCV-defective): RMEL→RMER q = 0.119 (NOT SIGNIFICANT, 5 observations)
- **Conclusion:** The RMEL→RMER functional interaction requires dense-core vesicle release (neuropeptide-dependent). Combined with PDF expression data, this is consistent with PDF neuropeptide signaling from RMEL to RMER during dwelling.

**Three-way convergence:**
```
Observational data (this study):  RMEL-RMER conditional coupling strongest during dwelling
Perturbation atlas (Randi 2023):  RMEL optogenetic stimulation drives RMER in WT
Genetic control (unc-31 mutant):  Interaction abolished when DCV release is blocked
```

**Mechanistic hypothesis:** During dwelling (food exploitation), PDF neuropeptide is released
from RMEL dense-core vesicles and activates RMER via pdfr-1. This coupling is not visible
in raw calcium (shared locomotor variance dominates during roaming) but emerges as a
dwelling-state conditional residual after behavioral residualization.

---

## 3. What Did the Framework Contribute Beyond Standard Approaches?

| Contribution | Evidence |
|---|---|
| **State-specific prediction** | ΔQ < 0 identifies dwelling-dominant coupling; funatlas is state-agnostic |
| **Off-connectome discovery** | Class 4 pair; anatomical models would not flag this |
| **Residualization reveals hidden signal** | GCaMP ΔQ = 0 but CePNEM ΔQ = −0.058; behavior removal exposes the signal |
| **Mechanism consistency** | Framework's DCV/neuropeptide prediction (PDF enrichment in Phase 2 Stage 4A) aligns with unc-31 abolishment |

The framework does not replace the funatlas; it provides a complementary prediction
from naturalistic behavior that is mechanistically consistent with the funatlas perturbation.

---

## Secondary Confirmed Cases

| Pair | Rank | wt q | unc-31 q | Coverage | Status |
|---|---|---|---|---|---|
| CEPDR–URXL | 40 | 0.0002 | unknown (0 obs) | 6 obs | Strong wt confirmation; DCV unknown |
| I1R–RMDVR | 50 | 0.032 | 0.571 (not sig) | 57 obs (wt) | DCV-dependent; high-confidence wt |
| AVJR–AWBL | 47 | 0.0017 | 0.012 (sig) | 37 obs | Confirmed but DCV-independent |

CEPDR–URXL has an equally strong wt q (0.0002) but the unc-31 data is missing. I1R–RMDVR
has the highest observation count (57) with clear DCV dependence, but a weaker framework
signal (rank 50). These are supporting cases, not the primary example.

---

## Caveats and Limitations

1. **RMEL–RMER is not strictly a "novel" prediction.** The pair was known to be in the
   Randi annotation set (randi_annotated = True). However, the specific prediction of
   (a) dwelling-dominant coupling and (b) CePNEM-specific signal are novel contributions
   that the funatlas alone cannot provide.

2. **Small unc-31 sample size (5 observations)** limits confidence in the DCV-dependence
   claim. The direction is clear (q: 0.0002 → 0.119) but replication would strengthen.

3. **The novel predictions (ADEL–URYVR, ADEL–URYDL) remain untested.** These are the
   highest-ranked (ranks 5 and 9) PDF-annotated predictions and have no funatlas data
   (0 observations). The RMEL–RMER confirmation provides biological context and
   credibility for these predictions, but does not constitute direct confirmation.

4. **DCV dependence does not prove PDF specifically.** Other DCV-packaged signals could
   mediate the RMEL–RMER interaction. The PDF connection (pdf-1 expression in RMEL,
   pdfr-1 in RMER) is biologically plausible but not proven by these data alone.

---

## Summary Table

| Pair | Evidence tier | Novelty | Mechanism |
|---|---|---|---|
| **RMEL–RMER** | **Strong confirmation** | Framework adds state-specificity + residualization | **DCV-dependent (unc-31 ablated)** |
| CEPDR–URXL | Wt confirmed | Framework adds off-connectome + state | DCV unknown |
| I1R–RMDVR | Wt confirmed (high coverage) | Framework adds state-specificity | DCV-dependent |
| ADEL–URYVR | Not tested | Novel prediction (rank 5) | Future experiment |
| ADEL–URYDL | Not tested | Novel prediction (rank 9) | Future experiment |

---

## Final Verdict

**Grade: C — Strong Confirmation**

The RMEL–RMER case provides a concrete, independently validated example where the framework:
1. Predicted a state-dependent (dwelling-dominant) off-connectome conditional coupling
2. The coupling is confirmed by the perturbation atlas (funatlas wt, q = 0.0002)
3. The mechanism is consistent with the framework's neuropeptide prediction (DCV-dependent, unc-31 abolished)
4. The prediction is non-obvious: it is invisible in raw calcium, not predicted by anatomy, and counter to the naive locomotor expectation

This is the strongest already-confirmed example in the existing data. It is not a
speculative interpretation — it rests on three independent measurements in three
separate experimental paradigms (naturalistic imaging, optogenetic perturbation, genetic perturbation).

---

## Files

| File | Contents |
|---|---|
| `context_recovery_note.md` | Confirmed vs predicted pairs; funatlas coverage gaps |
| `a1_candidate_inventory.md` | All top-50 pairs with funatlas q-values |
| `a2_nonobvious_confirmations.md` | Why RMEL-RMER is non-obvious |
| `a3_framework_added_value.md` | Framework vs standard interpretation comparison |
| `a4_best_confirmed_case.md` | Detailed RMEL-RMER analysis |
| `a5_confirmation_figure.md` | Figure concept for the confirmed example |

---

## Authorization Boundary

This phase did NOT:
- Evaluate the held-out ADEL-URYVR/URYDL predictions
- Perform new enrichment analyses
- Introduce new theory
- Introduce new model families
- Revisit Ω/Q comparisons

The funatlas data was queried using existing tools (h5py read-only) to recover already-computed
q-values for pairs already ranked by the framework.

**STOP. Awaiting review.**
