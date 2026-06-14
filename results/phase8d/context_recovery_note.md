# Phase 8D Context Recovery Note

**Written before any Phase 8D analysis is run.**

---

## Benchmark Label Definitions

| Class | direct | sareachable | Label | Definition |
|-------|--------|-------------|-------|------------|
| S | 1 | 0 | Structural | A[j,i] ≠ 0 (direct structural edge), NOT H2-mediated |
| C | 0 | 1 | Current-supported | NOT direct, but ∃ h∈SA: A[h,i]≠0 AND A[j,h]≠0 (H2-mediated path only) |
| M | 1 | 1 | Mixed | Both direct AND H2-mediated |
| N | 0 | 0 | Null | Neither direct nor H2-mediated |
| LR | — | 1 | Latent-Regulated | C ∪ M (any H2-mediated component) |

SA = {132,133,134,135,136,137,138,139} — the 8 state-active H2 neurons driven by z(t).

SAREACHABLE(i→j) = ∃ h ∈ SA: A[h,i]≠0 AND A[j,h]≠0 — purely topological.

Class counts (frozen): S=497, C=857, M=89, N=8457 (total 9900 directed pairs).

---

## Biological Analog

The C class is the primary biologically relevant analog of worm-style off-connectome / state-dependent organization:
- **Off-connectome**: direct=0 (not in the structural connectivity graph)
- **State-dependent**: sareachable=1 (modulated through H2 neurons that are driven by the latent state z)
- **Latent-regulated**: the influence on output j comes through a hidden neuron h, not a direct synaptic connection

This is analogous to:
- Worm: neuromodulatory / extra-synaptic signaling that is state-dependent
- Leech / OU analyses: current-supported but non-structural paths that depend on the behavioral state

The M class represents *both* structural and state-dependent organization (an edge exists in the connectome AND has a state-modulated H2 path). S class is purely structural (connectome-only). N class is neither.

---

## Frozen Outputs and Results

### Frozen artifacts (must not be regenerated)
- `framework_output.json` — SHA-256 e71364e2… (read-only)
- `results/phase8b/verdict.json` — SHA-256 5f47a402… (read-only, FAILURE)
- `results/phase8b/evaluation_audit.jsonl` — 6 events complete
- `ground_truth/labels.json` — SHA-256 dc99697e… (frozen)

### Frozen Phase 8B results

| Metric | Framework | B3 (corr) | B4 (GLasso) | B5 (ΔCorr) | B6 (module) |
|--------|-----------|-----------|------------|-----------|------------|
| MacroAUROC | 0.5385 | 0.5277 | 0.5000 | 0.5348 | 0.6340 |
| C-AUROC | 0.4484 | 0.5314 | 0.5000 | 0.5517 | 0.3830 |
| LR-AUROC | 0.4197 | 0.5327 | 0.5000 | 0.5503 | 0.3617 |
| S-AUROC | 0.8531 | — | — | — | — |
| Direct-AUROC | 0.8585 | 0.5173 | 0.5000 | 0.4898 | 0.7058 |

Key finding: Framework C-AUROC=0.4484 < 0.50 (anti-informative for C); S-AUROC=0.8531 (strong structural detection).

Phase 8D will re-evaluate using rank-based metrics (top-k enrichment, precision@k) and biologically meaningful subsets.
