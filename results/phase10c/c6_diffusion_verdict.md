# Phase 10C.6 — Diffusion Robustness Verdict
Date: 2026-06-15

---

## Q1: Does dense empirical diffusion create the ADEL/PDF signal generically?

**NO.**

Under identity diffusion (D=I, equivalent to ΔQ), ADEL-URYVR ranks 5th and
ADEL-URYDL ranks 9th out of 1321 Class-4 pairs. The signal EXISTS without any
diffusion weighting. Dense D promotes them further (to ranks 2/6) but does not
create them.

The C3 decomposition confirms: 83–96% of ADEL-URYVR's ΔΩ_ss is the precision
term D_roam @ ΔQ (where ΔQ is the driving structure); the diffusion-change term
contributes 4–17%.

---

## Q2: Is the signal already present under identity or diagonal diffusion?

**YES, the signal is present under identity and diagonal diffusion.**

| Spec | ADEL–URYVR | ADEL–URYDL |
|------|-----------|-----------|
| D=I (ΔQ) | rank 5 | rank 9 |
| Pooled diagonal | rank 5 | rank 7 |
| State-specific diagonal | rank 3 | rank 6 |
| Primary (state-specific full) | rank 2 | rank 6 |

The full state-specific D provides incremental improvement (5→2 for ADEL-URYVR),
not a categorical transformation. The diagonal state-specific D already achieves
ADEL-URYVR rank 3.

---

## Q3: Do shuffled or misaligned D nulls reproduce the signal?

**Partially — depends on which null.**

- **Off-diagonal shuffle** (500 reps): ADEL-URYVR achieves rank ≤ 2 in 18.2% of reps.
  Off-diagonal D is small; shuffling it is uninformative.

- **Diagonal shuffle** (500 reps): ADEL-URYVR achieves rank ≤ 2 in 5.2% of reps (p≈0.05).
  Marginal specificity to neuron-specific diagonal assignment.

- **Row/column permutation** (500 reps): ADEL-URYVR achieves rank ≤ 2 in only 1.8%
  of reps (p=0.018). This is the most stringent null. Preserving D's spectrum and scale
  but breaking its neuron-identity alignment with Q reduces the probability of achieving
  rank 2 to ≈1/55. The empirical alignment is specific.

- **State-label swap** (single): ADEL-URYVR swap rank = 6 (+0.054, sign reversed).
  The pair remains elevated by |ΔΩ| even when D and Q are misaligned between states.
  This is consistent with the Q-dominance in C3: the Q structure makes the pair extreme
  regardless of D's state-assignment.

**Interpretation:** Random dense diffusion can reproduce the ADEL/PDF top-ranking
if the neuron identity is preserved (off-diagonal or magnitude shuffles). The
SPECIFIC neuron-identity alignment of D with Q is what pushes ADEL-URYVR from
rank ~5 (ΔQ) to rank 2. The signal at rank 2 is partly D-specific; the signal
at rank 5 is not.

---

## Q4: Are key pairs explained by diffusion hubs?

**NO.**

- Global ρ(hub score, |ΔΩ_ss|) = 0.027–0.040 (all p > 0.15) — no systematic confound.
- ADEL-URYVR is at 99.8th percentile within pairs with similar hub score (p=0.0017).
- ADEL-URYDL is at 99.6th percentile (p=0.0043).
- Partial ρ(|ΔΩ_ss|, PDF | hub) ≈ marginal ρ — hub control changes nothing.
- ADEL itself is NOT a diffusion hub outlier (D_roam diagonal = 0.495, typical range).

---

## Q5: Are key pairs primarily precision-driven, diffusion-driven, or mixed?

**Primarily precision-driven; diffusion provides incremental reweighting.**

| Pair | Precision fraction (A) | Precision fraction (B) | Character |
|------|----------------------|----------------------|-----------|
| ADEL–URYVR | 96% | 83% | **Precision-dominant** |
| ADEL–URYDL | 111% (diff opposes) | 92% | **Precision-dominant** |
| ADEL–RMEL  | 92% | 81% | **Precision-dominant** |
| RMEL–URYDL | 101% (diff negligible) | 105% | **Precision-dominant** |
| RMEL–RMER  | 76% | 81% | Mostly precision; diffusion contributes ~20% |

Note: decomposition fractions are not unique and should not be over-interpreted.
What is robust: the precision term and total ΔΩ have consistent sign for all pairs
in both decompositions.

---

## Q6: What exact manuscript qualification is needed?

**One sentence for methods:**
"The state-specific current ΔΩ_ss = D_roam Q_roam − D_dwell Q_dwell uses the full
61×61 empirical innovations covariance D_s, which introduces off-reference current
entries via indirect diffusion paths. Control analyses confirmed that (i) the ADEL-PDF
signal is present under identity diffusion (ranks 5/9 vs 2/6 with full D), (ii) random
neuron-permuted diffusion achieves rank ≤ 2 for ADEL-URYVR in only 1.8% of 500
permutations, and (iii) endpoint diffusion hubness does not predict |ΔΩ_ss| ranking
(ρ<0.04) and does not explain ADEL-URYVR elevation (p=0.0017, hub-matched null)."

---

## Per-Claim Verdicts

| Claim | Grade | Key basis |
|-------|-------|-----------|
| ADEL–URYVR | **A — Strong** | Present under D=I (rank 5); row/col perm p=0.018; hub null p=0.0017; top-5 at all τ |
| ADEL–URYDL | **A/B — Strong/Moderate** | Present under D=I (rank 9); hub null p=0.0043; degrades at τ=20 |
| DA_mech ↔ URY_URX module | **A — Strong** | Rank 1 across ALL 5 D specifications; rank 1 in 75–99% of random D |
| ADEL–RMEL | **B — Moderate** | Present under D=I (rank 10); mixed diffusion/precision character at longer τ |
| RMEL–RMER | **C — Weak** | Already fragile (10A, 10B); further degradation at τ≥5; 24% diffusion-driven |
| PDF top-20 enrichment | **B — Moderate** | 4/20 at τ=1,10; 6/20 at τ=5; 2/20 at τ=20; degrades at longer timescales |

**Formal classification:**

- ADEL–URYVR: **A — Diffusion robustness strong**
- ADEL–URYDL: **A/B — Diffusion robustness strong/moderate**
- DA_mech ↔ URY_URX: **A — Diffusion robustness strong**
- ADEL–RMEL: **B — Diffusion robustness moderate**
- RMEL–RMER: **C — Diffusion robustness weak; major qualification needed**
- PDF top-K enrichment: **B — Moderate; present at frame-lag timescale, degrades at slow lags**
