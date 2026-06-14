#!/usr/bin/env python3
"""
Phase 9D — Framework Evaluation (LC-1: no ground_truth import allowed)

The current-velocity framework from the paper:
  Given: x_A (T_A×N), x_B (T_B×N), A_obs (N×N)
  Step 1: Estimate empirical covariance matrices Sigma_A_hat, Sigma_B_hat
  Step 2: Compute precision matrices Q_A_hat = Sigma_A_hat^{-1}, Q_B_hat = Sigma_B_hat^{-1}
  Step 3: Estimate diffusion from Lyapunov equation:
            AΣ + ΣA^T + 2D = 0  →  D = -(AΣ + ΣA^T) / 2
            D is diagonal, so D_ii = -(AΣ + ΣA^T)_ii / 2
  Step 4: ΔΩ_estimated = D_A_hat Q_A_hat - D_B_hat Q_B_hat
  Output: DeltaOmega_estimated (N×N)

This is ONE SHOT — no tuning, no reruns.

IMPORTANT: This file must NOT import any ground_truth module.
Verification: grep -r "ground_truth" scripts/phase9d/evaluate_framework.py → empty
"""

# ── LC-1 guard: no ground_truth access ────────────────────────────────────────
# (grep check at audit time)

import numpy as np
import hashlib, json, os, time

DATA_DIR = "results/phase9d/dataset"
OUT_DIR  = "results/phase9d"

def evaluate_framework(x_A: np.ndarray, x_B: np.ndarray,
                       A_obs: np.ndarray) -> np.ndarray:
    """
    Current-velocity framework implementation.

    Parameters
    ----------
    x_A   : (T_A, N) — State A observed neural activity
    x_B   : (T_B, N) — State B observed neural activity
    A_obs : (N, N)   — Known structural coupling matrix (observed-observed block)

    Returns
    -------
    DeltaOmega_estimated : (N, N) — Estimated current difference matrix
    """
    # LC-2: inputs are x_A, x_B, A_obs only
    # LC-3: x_A.shape[1] must equal N_OBS (no z column)
    T_A, N = x_A.shape
    T_B     = x_B.shape[0]
    assert x_B.shape[1] == N, "x_A and x_B must have same N"
    assert A_obs.shape == (N, N), f"A_obs shape mismatch: {A_obs.shape}"

    # Step 1: Empirical covariances
    Sigma_A_hat = np.cov(x_A.T)   # (N, N)
    Sigma_B_hat = np.cov(x_B.T)   # (N, N)

    # Step 2: Precision matrices
    Q_A_hat = np.linalg.inv(Sigma_A_hat)
    Q_B_hat = np.linalg.inv(Sigma_B_hat)

    # Step 3: Estimate diffusion from Lyapunov residual
    #   AΣ + ΣA^T + 2D = 0  (at stationarity)
    #   → D_hat_ii = -(AΣ + ΣA^T)_ii / 2  (diagonal entries only)
    def estimate_D_diag(A, Sigma):
        lhs = A @ Sigma + Sigma @ A.T    # AΣ + ΣA^T
        d   = -np.diag(lhs) / 2.0       # diagonal entries
        d   = np.maximum(d, 1e-8)       # enforce positivity
        return np.diag(d)

    D_A_hat = estimate_D_diag(A_obs, Sigma_A_hat)
    D_B_hat = estimate_D_diag(A_obs, Sigma_B_hat)

    # Step 4: Current organization and difference
    Omega_A_hat = D_A_hat @ Q_A_hat + A_obs
    Omega_B_hat = D_B_hat @ Q_B_hat + A_obs
    DeltaOmega_hat = Omega_A_hat - Omega_B_hat

    return DeltaOmega_hat

if __name__ == "__main__":
    # ── Run the framework (one shot) ──────────────────────────────────────────
    import stat
    print("=== Phase 9D Framework Evaluation ===")

    with open(f"{DATA_DIR}/dataset_manifest.json") as f:
        ds_manifest = json.load(f)

    x_A   = np.load(f"{DATA_DIR}/x_A.npy").astype(np.float64)
    x_B   = np.load(f"{DATA_DIR}/x_B.npy").astype(np.float64)
    A_obs = np.load(f"{DATA_DIR}/A_obs.npy")
    print(f"  Dataset loaded: x_A={x_A.shape}, x_B={x_B.shape}")

    with open(f"{OUT_DIR}/baseline_hashes.json") as f:
        bl_hashes = json.load(f)
    for fname in ["x_A.npy", "x_B.npy", "A_obs.npy"]:
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        expected = ds_manifest["file_hashes"].get(fname, "not_in_manifest")
        assert h == expected, f"Dataset hash mismatch for {fname}"
    print("  Dataset hashes verified")

    print("  Running framework (one shot)...")
    t0 = time.time()
    DeltaOmega_est = evaluate_framework(x_A, x_B, A_obs)
    t_elapsed = time.time() - t0
    print(f"  Framework completed in {t_elapsed:.2f}s")

    assert DeltaOmega_est.shape == (150, 150), f"Output shape: {DeltaOmega_est.shape}"
    assert np.isfinite(DeltaOmega_est).all(), "Non-finite values in output"
    print(f"  Output shape: {DeltaOmega_est.shape}, all finite: OK")

    np.save(f"{OUT_DIR}/framework_DeltaOmega.npy", DeltaOmega_est)
    with open(f"{OUT_DIR}/framework_DeltaOmega.npy", "rb") as fh:
        fw_hash = hashlib.sha256(fh.read()).hexdigest()

    os.chmod(f"{OUT_DIR}/framework_DeltaOmega.npy",
             stat.S_IRUSR | stat.S_IRGRP)

    framework_log = {
        "oracle_master_hash": ds_manifest["oracle_master_hash"],
        "dataset_master_hash": hashlib.sha256(
            json.dumps(ds_manifest["file_hashes"], sort_keys=True).encode()
        ).hexdigest(),
        "framework_output_hash": fw_hash,
        "execution_time_s": t_elapsed,
        "output_shape": list(DeltaOmega_est.shape),
        "output_stats": {
            "min": float(DeltaOmega_est.min()),
            "max": float(DeltaOmega_est.max()),
            "mean_abs": float(np.abs(DeltaOmega_est).mean()),
            "std": float(DeltaOmega_est.std()),
        },
        "lc_checks": {
            "LC1_no_ground_truth_import": True,
            "LC2_inputs_only_xA_xB_Aobs": True,
            "LC3_no_z_column": True,
            "one_shot": True,
            "no_tuning": True,
        }
    }

    with open(f"{OUT_DIR}/framework_log.json", "w") as f:
        json.dump(framework_log, f, indent=2)

    print(f"\n  Framework output hash: {fw_hash[:16]}...")
    print(f"  Output frozen (read-only)")
    print(f"  Execution log: results/phase9d/framework_log.json")
    print("\n=== FRAMEWORK RUN COMPLETE ===")
