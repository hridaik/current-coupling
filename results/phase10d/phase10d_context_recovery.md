# Phase 10D — Context Recovery
Date: 2026-06-15
Authorization: Phase 10D — Top-K Enrichment and Coupling-Reference Sensitivity

---

## 1. Primary Result Being Tested

**Phase 2 Stage 4A finding**: The top-20 Class-4 pairs by |ΔΩ_ss| are enriched for
PDF neuromodulatory annotation (Bentley ESconnectome, pdf-1/pdf-2/pdfr-1).
  - Top-20 contained 4 PDF pairs; expected ~0.92 by density
  - Fisher OR = 5.46, p_fisher = 0.011, p_degree_perm = 0.008
  - AUROC = 0.556, p = 0.023 (degree-adjusted)

**Primary key pairs** (by |ΔΩ_ss| rank among 1321 Class-4 pairs):
  - ADEL–URYVR: rank 2, |ΔΩ_ss| = 0.0688 (dwelling-dominant)
  - ADEL–URYDL: rank 6, |ΔΩ_ss| = 0.0498 (dwelling-dominant)
  - ADEL–RMEL:  rank 4, |ΔΩ_ss| = 0.0549 (dwelling-dominant)
  - DA_mech ↔ URY_URX module: rank 1 by mean cross-block |ΔΩ_ss|

Additional tracked pairs:
  - RMEL–URYDL: rank 23
  - RMEL–RMER:  rank 38

All ranks from `results/phase3d/DO_state_cep_full.npy` scored at C4 pairs from
`results/phase2/stage2/ranked_class4_cepnem.npy`.

---

## 2. Class-4 Universe (LOCKED)

**Definition (locked at Stage 2)**:
  - Off-reference (A_raw): pair (i,j) NOT in primary structural connectome
  - Both neurons in Creamer 56-neuron subspace (not in {AIBL, AIBR, AWCL, IL1L, IL1R})
  - Total: N_C4 = 1321 pairs from N=61 neuron universe (1830 upper-triangle pairs total)

**Critical**: The primary A_raw was loaded from `/tmp/A_raw_61.npy` during Phase 2
execution and was not saved persistently. Reverse engineering indicates it is most
likely the Creamer chemical synapse matrix (any directed edge ≥1, symmetrized), which
gives C4=1322 (off by 1 from actual 1321). Exact reconstruction of A_raw is not
possible, but the locked `ranked_class4_cepnem.npy` defines the authoritative universe.

For Phase 10D D3 (reference sensitivity), alternative universes are built FRESH and
NOT substituted for the primary locked set.

---

## 3. Primary Annotations (from Stage 4A)

| Annotation | Source | N (C4) | Stage 4A result |
|------------|--------|--------|-----------------|
| Bentley_PDF | ESconnectome neuropeptides, transmitter∋"pdf" | 61 | K=20: 4/20, OR=5.46, p_deg=0.008 ★ |
| Bentley_serotonin | ESconnectome monoamines, transmitter∋"serotonin" | 33 | K=20: 0/20, OR=0, p=n.s. |
| Bentley_serotonin_or_PDF | union | 94 | AUROC=0.536, p=0.047 |
| CeNGEN_serotonin_or_PDF | directed ligand-receptor, threshold 3 | 409 | AUROC=0.521, p=0.028 |

Additional for Phase 10D (exploratory):
  - Neuropeptide/Ripoll-Sánchez: Creamer peptide.pkl, any directed edge >0, symmetrized (NEW)
  - Combined neuromodulatory: PDF ∪ serotonin ∪ neuropeptide (NEW, exploratory)
  - Randi/Funatlas: unc-31-sensitive pairs, q_wt<0.05 either direction (N=108 C4)

---

## 4. Key Pair Annotation Status

| Pair | PDF? | Serotonin? | Neuropeptide? | Randi? |
|------|------|-----------|--------------|--------|
| ADEL–URYVR | YES (pdf-1→pdfr-1) | No | TBD | TBD |
| ADEL–URYDL | YES (pdf-1→pdfr-1) | No | TBD | TBD |
| ADEL–RMEL | No | No | TBD | TBD |
| RMEL–URYDL | No | No | TBD | TBD |
| RMEL–RMER | No | No | TBD | TBD |

---

## 5. Primary Top-K Context

**K = 20 was LOCKED at Stage 2 and is the primary K.**
  - Phase 10D sweeps K to test sensitivity — NOT to choose a new K.
  - DO NOT change the primary K=20 result or report after seeing the sweep.

Key pairs in top-K:
  - At K=20: ADEL-URYVR (rank 2), ADEL-URYDL (rank 6), ADEL-RMEL (rank 4)
  - All three are in top-10 as well
  - RMEL-URYDL (rank 23): not in top-20; RMEL-RMER (rank 38): not in top-20

Expected PDF counts by chance at each K: K × (61/1321)

---

## 6. Reference Sensitivity Context

**Synaptic counts for key pairs** (from Phase 10D exploration):

| Pair | Creamer chem | Creamer gap | White 1986 chem | Witvliet 2020 | LDS weight |
|------|-------------|------------|----------------|--------------|-----------|
| ADEL–URYVR | 0 | 0 | 0 | 0 | 0 |
| ADEL–URYDL | 0 | 0 | 0 | 0 | 0 |
| ADEL–RMEL  | 0 | 0 | 0 | 0 | 0 |
| RMEL–URYDL | 0 | 0 | 0 | 0 | 0.017 |
| RMEL–RMER  | 0 | 0 | 0 | 0 | 0 |

All five key pairs are off-reference under ALL structural connectome definitions tested.
RMEL-URYDL has a weak LDS effective coupling (0.017), which we flag.

---

## 7. Phase 10C Grades (Forward Context)

From Phase 10C, the diffusion-robustness grades informing interpretation:
  - ADEL–URYVR: **A** (present in ΔQ; hub null p=0.0017; top-5 at all timescales)
  - ADEL–URYDL: **A/B** (present in ΔQ; hub null p=0.0043; degrades at τ=20)
  - DA_mech ↔ URY_URX: **A** (rank 1 across all diffusion specs and random permutations)
  - ADEL–RMEL: **B** (timescale-stable at τ≤10)
  - RMEL–RMER: **C** (fragile across multiple phases)
  - PDF top-20 enrichment: **B** (4/20 at primary τ; degrades at τ=20)

---

## 8. Phase 10D Prohibitions

Per the Phase 10D authorization:
- DO NOT change the primary ranking (ΔΩ_ss from Phase 3D)
- DO NOT change the primary Class-4 definition retroactively
- DO NOT choose a new K after seeing results
- DO NOT add new annotation sets without labeling them **[EXPLORATORY]**
- DO NOT hide reference definitions where key pairs become connected
- DO NOT overstate nominal enrichment as FDR-controlled
- DO NOT claim global AUROC significance if not present

---

**Proceeding to Phase 10D analysis.**
