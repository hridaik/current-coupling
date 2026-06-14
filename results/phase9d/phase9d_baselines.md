# Phase 9D — Stage 3: Baseline Results

**Date:** 2026-06-14  
**Script:** `scripts/phase9d/baselines.py`  
**Status:** COMPLETE — hash-locked

**Baseline hash file:** `results/phase9d/baseline_hashes.json`

---

## Baseline Definitions

| ID | Method | Description |
|----|--------|-------------|
| B1 | Random | Uniform random scores, seed=9001 |
| B2 | \|ΔCorr\| | Absolute correlation change: \|Corr_A[i,j] − Corr_B[i,j]\| |
| B3 | Glasso | \|Q_pooled[i,j]\| from GraphicalLassoCV on x_A ∥ x_B |
| B4 | Oracle | \|ΔΩ_true[i,j]\| from Phase 9C ground truth |

---

## Results

| Baseline | PMC_AUROC | ρ_Spearman | Prec@20 | Prec@50 | Prec@100 |
|----------|-----------|------------|---------|---------|----------|
| B1 Random | 0.5105 | +0.013 | 0.000 | 0.020 | 0.030 |
| B2 \|ΔCorr\| | 0.4440 | −0.161 | 0.400 | 0.220 | 0.140 |
| B3 Glasso | 0.4971 | −0.157 | 0.850 | 0.380 | 0.200 |
| B4 Oracle | 0.9983 | +1.000 | 1.000 | 1.000 | 1.000 |

---

## Notes on Baseline Performance

**B2 (|ΔCorr|):** PMC_AUROC = 0.444 — below random. This is expected: with PMC_SRC and PMC_TGT isolated (no A_obs edges to background), their marginal correlations with each other are small and mediated entirely through the hidden HG relay. |ΔCorr| cannot detect this latent relay, and the background neurons with direct structural connections show larger correlation changes. The negative ρ confirms that |ΔCorr| is anti-correlated with the oracle.

**B3 (Glasso, pooled):** Prec@50 = 0.380 is above the success threshold (0.25), but PMC_AUROC = 0.497 is near chance and ρ = −0.157 is negative. The pooled Glasso detects PMC_TGT-TGT partial correlation structure (which is large due to shared HG drive in State A), but cannot distinguish State A from State B, giving inverted AUROC and ρ relative to the oracle. The elevated Prec@50 reflects that PMC_TGT neurons cluster together even in pooled data.

**B4 (Oracle):** Confirms benchmark validity. AUROC = 0.9983 ≥ 0.90 (AT-5 PASS). This was verified in Phase 9C.

---

## File Hashes (SHA-256, first 16)

| File | Hash |
|------|------|
| b1_scores.npy | 6e4475e32a26ebe5... |
| b2_scores.npy | 1d521e3b7e67d68e... |
| b3_scores.npy | 6530cda1cbb1f376... |
| b4_scores.npy | 92d9c998849ce189... |
| baseline_results.json | c4f02d5306bc7568... |

---

## Status

STAGE 3 COMPLETE. Baselines computed and hash-locked. Proceed to Stage 4.
