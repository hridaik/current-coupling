# Phase 9D — Stage 2: Dataset Freeze Report

**Date:** 2026-06-14  
**Directory:** `results/phase9d/dataset/`  
**Status:** FROZEN — files set read-only; hashes locked

---

## Files Generated

| File | Shape | Hash (SHA-256, first 16) |
|------|-------|--------------------------|
| x_A.npy | (150000, 150) | bd42b13572f50eca... |
| x_B.npy | (150000, 150) | a79a124cef0b063b... |
| x_A_lesion.npy | (150000, 150) | 867a33b052590581... |
| A_obs.npy | (150, 150) | 0abb12d0e8a9a167... |

Full hashes recorded in `dataset/dataset_manifest.json`.

**Dataset master hash:** `f4db4ca61e268578...`

---

## Generation Parameters

| Parameter | Value |
|-----------|-------|
| N_OBS | 150 |
| N_TOTAL | 180 |
| T_A = T_B | 150,000 steps |
| dt | 0.01 |
| burn_in | 10,000 steps |
| Seed (x_A) | 100 |
| Seed (x_B) | 200 |
| Seed (x_A_lesion) | 300 |

---

## Integrity Checks

| Check | Result |
|-------|--------|
| Oracle master hash verified before generation | PASS (79c98d032742ba36...) |
| LC-4: oracle_master_hash.txt older than trajectories | PASS (gap = 0.23 h) |
| All three trajectory files set read-only (chmod 444) | PASS |
| A_obs = A_full[:150, :150] — no ground truth | PASS |

---

## Dataset Statistics

| Statistic | Value |
|-----------|-------|
| PMC_SRC variance ratio A/B | 4.891× |
| Background variance ratio A/B | 1.024× |
| Empirical Sigma_A min eigenvalue | 0.4658 |

---

## Regeneration Fingerprint

To reproduce any trajectory exactly:

```python
from scripts.phase9d.simulator import simulate
import numpy as np

A_full   = np.load("results/phase9c/ground_truth/A_full.npy")
D_A_diag = np.load("results/phase9c/ground_truth/D_A_diag.npy")

x_A       = simulate(A_full, D_A_diag, T_steps=150000, seed=100)
x_B       = simulate(A_full, D_B_diag, T_steps=150000, seed=200)
```

Oracle files used: from `results/phase9c/ground_truth/`, master hash `79c98d032742ba36...`.

---

## Status

STAGE 2 COMPLETE. Dataset frozen and hash-locked. Proceed to Stage 3.
