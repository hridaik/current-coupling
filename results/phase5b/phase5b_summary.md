# Phase 5B — Final Summary
Date: 2026-06-12
Authorization: Phase 5B

---

## The Question

Does switching from ΔQ (precision difference) to ΔΩ_ss = D_roam @ Q_roam − D_dwell @ Q_dwell
(state-specific current difference) substantially change the biological story?

---

## Answer: B — Current Refines the Story

The core findings are preserved. Specific pair rankings shift and the PDF AUROC
enrichment loses statistical significance, but the top biological claims are unchanged or
strengthened. No key result reverses direction.

---

## 1. What Stayed the Same

**Sign stability (5/5):**
All five tracked pairs (ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, RMEL–URYDL, RMEL–RMER)
remain dwelling-dominant (ΔΩ_ss < 0) under the current formulation.
The state-preference prediction is robust to the choice of D-weighting.

**Confirmed case (RMEL–RMER):**
ΔΩ_ss = −0.0254, rank 38 (top 2.9%) vs ΔQ rank 32 (top 2.4%).
A modest 6-place demotion. RMEL–RMER is still unambiguously high-priority under both formulations.
The funatlas confirmation (wt q = 0.0002, unc-31 abolished) is unchanged.
**Grade C — Strong Confirmation from Phase 5A is not affected.**

**Top module block:**
DA_mech ↔ URY_URX is rank #1 by mean |ΔΩ_ss| AND rank #1 by mean |ΔQ|.
The mechanosensory/dopaminergic ↔ URY/URX sensory interaction is the dominant structural
pattern under both formulations.

**Fisher top-20 PDF count:**
4 PDF pairs appear in the top-20 under both ΔΩ_ss (ranks 2, 4, 6, 20) and ΔQ (ranks 5, 9, 10, 16).
The same density of annotation-positive pairs occupies the top prediction tier.

---

## 2. What Was Refined or Changed

**ADEL-PDF triplet promoted:**
Under ΔΩ_ss, ADEL–URYVR rises from rank 5 to rank 2, ADEL–RMEL from rank 10 to rank 4,
ADEL–URYDL from rank 9 to rank 6. The ADEL-PDF circuit predictions move to the very top
of the ranking. This is a positive refinement: the framework's primary experimental targets
are higher-priority under the preferred formulation.

**RMEL-hub pairs demoted:**
RMEL–URYDL: rank 16 → rank 23. RMEL–RMER: rank 32 → rank 38.
The RMEL node appears less central when D-weighting is included. The ADEL node rises;
the RMEL node falls slightly.

**IL ↔ IL block newly prominent:**
The inner labial (IL) neuron block rises from module rank 9 under ΔQ to module rank 4
under ΔΩ_ss (mean |ΔΩ_ss| doubles relative to mean |ΔQ|). IL neurons are mechanosensory
neurons around the mouth, involved in feeding-state modulation — a biologically coherent
amplification under dwelling-state weighting.

**PDF AUROC significance lost:**
Under ΔQ: PDF AUROC = 0.556, p_deg = 0.020 (significant).
Under ΔΩ_ss: PDF AUROC = 0.533, p_deg = 0.196 (not significant).
The significance loss is driven by non-PDF pairs being promoted into the middle ranks
(AVEL–RIVL, ASEL–CEPDR, FLPL–OLLL, CEPDR–URXL), diluting the global PDF enrichment signal.
The top-20 Fisher count is preserved (4/20 PDF in both), so the top-tier predictions
remain equally PDF-enriched.

**Novel high-ranking pair: CEPDR–URXL (ΔΩ rank 10):**
CEPDR–URXL rises from ΔQ rank 40 to ΔΩ_ss rank 10. It has funatlas wt q = 0.0002 (6 obs),
suggesting it is an additional confirmed off-connectome interaction under the current formulation.

---

## 3. What This Means for the Framework

The choice between ΔQ and ΔΩ_ss represents a trade-off:

| Criterion | ΔQ | ΔΩ_ss |
|-----------|-----|-------|
| PDF AUROC significance | **Yes (p=0.020)** | No (p=0.196) |
| Top predicted pairs (ADEL-PDF) | Ranks 5, 9, 10 | **Ranks 2, 4, 6** |
| Confirmed case rank | Rank 32 | Rank 38 |
| Top module | DA_mech↔URY_URX | DA_mech↔URY_URX |
| Sign stability | 5/5 | 5/5 |
| Rank correlation with ΔQ | — | ρ = 0.331 |

ΔΩ_ss is the theoretically preferred object (it is the actual difference in state-specific
probability current, not an approximation). Despite this theoretical preference, ΔQ
produces a stronger global enrichment signal. This tension suggests that the D matrix
introduces noise at moderate ranks (where non-annotated pairs are promoted) while
preserving or amplifying the signal at the very top (ADEL-PDF cluster).

---

## 4. Formal Verdict Per Dimension

| Dimension | Verdict |
|-----------|---------|
| Top pair rankings | **B** — substantially reshuffled (ρ=0.331), same biology at top |
| Module organization | **B** — #1 stable; IL↔IL, DA_mech↔RME promoted; AV-blocks demoted |
| PDF AUROC enrichment | **B/C** — significance lost; Fisher count preserved |
| Confirmed case | **A** — RMEL-RMER robust; grade unchanged |
| Sign stability | **A** — 5/5 dwell-dominant |

**Overall: B — Current refines the story.**

---

## 5. Caveats

1. The 6-place demotion of RMEL–RMER is the most consequential negative finding for
   the confirmed story, but rank 38 remains well within the high-priority tier (top 3%).

2. The PDF AUROC significance loss is real. If the global enrichment claim is central to
   the paper, ΔΩ_ss weakens it. If the specific top-pair predictions are central, ΔΩ_ss
   strengthens them.

3. The ASEL–CEPDR pair (ΔQ rank 85 → ΔΩ_ss rank 16) is a large, biologically potentially
   interesting promotion (chemosensory ↔ cephalic sensory, roaming-dominant) but is
   unvalidated and was not a prior hypothesis.

4. The IL ↔ IL block promotion under ΔΩ_ss is novel and biologically interpretable
   (feeding-circuit mechanosensation during dwelling), but was not the focus of prior analyses.

---

## Files

| File | Contents |
|------|---------|
| `context_recovery_note.md` | ΔΩ_ss definition, D and Q estimators, ranking provenance |
| `b1_top_current_pairs.md` | Top-20 by |ΔΩ_ss| with annotations, comparison with ΔQ top-20 |
| `b2_keypair_comparison.md` | ADEL-URYVR, ADEL-URYDL, ADEL-RMEL, RMEL-URYDL, RMEL-RMER |
| `b3_module_current.md` | Module-block organization under ΔΩ_ss; IL↔IL and DA↔RME |
| `b4_current_enrichment.md` | AUROC, Fisher, Randi enrichment under both formulations |
| `b5_rmel_rmer_current.md` | Confirmed case: rank 38, value -0.025, dwelling-dominant |
| `b6_current_vs_precision.md` | A/B/C classification per dimension |
| `phase5b_numerics.json` | All computed numbers (saved in previous session) |

---

## Authorization Boundary

This phase did NOT:
- Rerun Phase 5A analyses
- Consume held-out ADEL-URYVR/URYDL predictions (no new funatlas lookups beyond Phase 5A)
- Introduce new theory or new model families
- Use pooled D formulations or D_emp ΔQ approximations
- Use any Ω formulation other than D_roam Q_roam − D_dwell Q_dwell (exact ΔΩ_ss)

**STOP. Awaiting review.**
