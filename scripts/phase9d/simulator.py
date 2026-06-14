#!/usr/bin/env python3
"""
Phase 9D Simulator — generate trajectories from the frozen oracle network.

Loads A_full and D parameters from results/phase9c/ground_truth/.
Generates:
  x_A:        (T_A, N_OBS) — State A observations
  x_B:        (T_B, N_OBS) — State B observations
  x_A_lesion: (T_A, N_OBS) — State A with structural lesion (A_lesioned)

z(t) is NEVER written to any output file.
Output shape: (T, N_OBS) = (150000, 150) — no z column (LC-3).
"""

import numpy as np
import hashlib, json, os, time

GT_DIR  = os.path.join(os.path.dirname(__file__), "../../results/phase9c/ground_truth")
OUT_DIR = os.path.join(os.path.dirname(__file__), "../../results/phase9d/dataset")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load oracle objects (verify hashes before use) ────────────────────────────
print("=== Phase 9D Simulator ===")
print("Loading oracle objects...")

with open(f"{GT_DIR}/oracle_manifest.json") as f:
    manifest = json.load(f)
with open(f"{GT_DIR}/oracle_master_hash.txt") as f:
    stored_master = f.read().strip()
computed_master = hashlib.sha256(
    json.dumps(manifest, sort_keys=True).encode()
).hexdigest()
assert stored_master == computed_master, "Oracle master hash mismatch — abort"
print(f"  Oracle master hash: {stored_master[:16]}... VERIFIED")

A_full   = np.load(f"{GT_DIR}/A_full.npy")
D_A_diag = np.load(f"{GT_DIR}/D_A_diag.npy")
D_B_diag = np.load(f"{GT_DIR}/D_B_diag.npy")
spec     = json.load(open(f"{GT_DIR}/network_spec.json"))

N_OBS    = spec["N_OBS"]    # 150
N_TOTAL  = spec["N_TOTAL"]  # 180
T_A      = spec["T_A"]      # 150000
T_B      = spec["T_B"]      # 150000
DT       = spec["dt"]       # 0.01
BURN_IN  = spec["burn_in"]  # 10000

assert A_full.shape == (N_TOTAL, N_TOTAL)
assert D_A_diag.shape == (N_TOTAL,)
print(f"  Network: {N_OBS} observed, {N_TOTAL} total")
print(f"  T_A=T_B={T_A}, dt={DT}, burn_in={BURN_IN}")

# ── Build structural lesion matrix ────────────────────────────────────────────
M1 = np.array(spec["M1"])
M2 = np.array(spec["M2"])
A_lesioned = A_full.copy()
n_les = 0
for i in M2:
    for j in M1:
        if A_lesioned[i, j] != 0:
            A_lesioned[i, j] = 0.0
            n_les += 1
print(f"  Structural lesion: {n_les} M1→M2 edges removed")

# ── Euler-Maruyama SDE integrator ─────────────────────────────────────────────
def simulate(A_mat, D_diag, T_steps, seed, burn_in=BURN_IN):
    """
    Euler-Maruyama: dx = A x dt + sqrt(2D dt) * eps
    Returns: (T_steps, N_OBS) observed trajectories only.
    z(t) is never written.
    """
    rng_sim  = np.random.default_rng(seed)
    N        = A_mat.shape[0]
    noise_sd = np.sqrt(2 * D_diag * DT)   # per-neuron noise std per step
    x        = np.zeros(N)                  # initial condition

    # Burn-in
    for _ in range(burn_in):
        x = x + A_mat @ x * DT + noise_sd * rng_sim.standard_normal(N)

    # Record observed neurons only (LC-3: no z column)
    out = np.empty((T_steps, N_OBS), dtype=np.float32)
    for t in range(T_steps):
        x = x + A_mat @ x * DT + noise_sd * rng_sim.standard_normal(N)
        out[t] = x[:N_OBS].astype(np.float32)
    return out

# ── Acceptance test: stationarity check ────────────────────────────────────────
def check_stationarity(x, name, tol=5.0):
    """Compare first-half vs second-half mean and variance."""
    T = x.shape[0]; half = T // 2
    mean1, mean2 = x[:half].mean(0), x[half:].mean(0)
    var1,  var2  = x[:half].var(0),  x[half:].var(0)
    max_mean_diff = float(np.max(np.abs(mean1 - mean2)))
    max_var_ratio = float(np.max(np.abs(var1 - var2) / (var1 + 1e-8)))
    print(f"  {name}: max_mean_diff={max_mean_diff:.4f}, max_var_ratio={max_var_ratio:.4f}")
    assert max_mean_diff < tol,    f"Stationarity FAIL ({name}): mean shift {max_mean_diff:.3f}"
    assert max_var_ratio < 1.0,    f"Stationarity FAIL ({name}): var ratio {max_var_ratio:.3f}"

# ── Generate trajectories ──────────────────────────────────────────────────────
print("\n--- Generating State A ---")
t0 = time.time()
x_A = simulate(A_full, D_A_diag, T_A, seed=100)
print(f"  Done in {time.time()-t0:.1f}s. Shape: {x_A.shape}")

print("\n--- Generating State B ---")
t0 = time.time()
x_B = simulate(A_full, D_B_diag, T_B, seed=200)
print(f"  Done in {time.time()-t0:.1f}s. Shape: {x_B.shape}")

print("\n--- Generating State A (structural lesion) ---")
t0 = time.time()
x_A_lesion = simulate(A_lesioned, D_A_diag, T_A, seed=300)
print(f"  Done in {time.time()-t0:.1f}s. Shape: {x_A_lesion.shape}")

# ── Acceptance tests ──────────────────────────────────────────────────────────
print("\n--- Acceptance tests ---")

# AT-3: shape checks (LC-3)
assert x_A.shape == (T_A, N_OBS), f"Shape fail: {x_A.shape}"
assert x_B.shape == (T_B, N_OBS), f"Shape fail: {x_B.shape}"
print("  AT-3 PASS: shapes correct (150000, 150) — no z column")

# AT-3b: stationarity
check_stationarity(x_A, "State A")
check_stationarity(x_B, "State B")
check_stationarity(x_A_lesion, "State A lesion")
print("  AT-3b PASS: stationarity in all three trajectories")

# AT-3c: PMC source neurons have elevated variance in State A vs State B
PMC_SRC = np.array(spec["PMC_SRC"])
PMC_TGT = np.array(spec["PMC_TGT"])
pmc_src_varA = x_A[:, PMC_SRC].var(0).mean()
pmc_src_varB = x_B[:, PMC_SRC].var(0).mean()
nonpmc_varA  = x_A[:, np.array([i for i in range(N_OBS) if i not in PMC_SRC])].var(0).mean()
nonpmc_varB  = x_B[:, np.array([i for i in range(N_OBS) if i not in PMC_SRC])].var(0).mean()
ratio_src  = float(pmc_src_varA / pmc_src_varB)
ratio_bg   = float(nonpmc_varA  / nonpmc_varB)
print(f"  PMC_SRC var ratio A/B:  {ratio_src:.3f}x (expect >1.0)")
print(f"  Background var ratio A/B: {ratio_bg:.3f}x (expect ≈1.0)")
assert ratio_src > 1.0, f"AT-3c FAIL: PMC_SRC not more variable in State A"
print("  AT-3c PASS: PMC_SRC elevated variance in State A confirmed")

# AT-3d: sample covariance rank check
Sigma_A_hat = np.cov(x_A.T.astype(np.float64))  # (150, 150)
min_eig     = float(np.min(np.linalg.eigvalsh(Sigma_A_hat)))
print(f"  AT-3d: min eigenvalue of empirical Sigma_A = {min_eig:.6f}")
assert min_eig > 0, f"AT-3d FAIL: empirical Sigma_A not PD"
print("  AT-3d PASS: empirical Sigma_A is positive-definite")

# ── Save trajectories ─────────────────────────────────────────────────────────
print("\n--- Saving trajectories ---")
oracle_mtime = os.path.getmtime(f"{GT_DIR}/oracle_master_hash.txt")
gen_time     = time.time()
assert gen_time > oracle_mtime, "LC-4 FAIL: oracle not older than generation time"
print(f"  LC-4 PASS: oracle created {(gen_time-oracle_mtime)/3600:.2f}h before trajectories")

np.save(f"{OUT_DIR}/x_A.npy",        x_A)
np.save(f"{OUT_DIR}/x_B.npy",        x_B)
np.save(f"{OUT_DIR}/x_A_lesion.npy", x_A_lesion)

# Hash trajectories
traj_hashes = {}
for fname in ["x_A.npy", "x_B.npy", "x_A_lesion.npy"]:
    fpath = os.path.join(OUT_DIR, fname)
    with open(fpath, "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    traj_hashes[fname] = h
    print(f"  {fname}: {h[:16]}...")

# Also save A_obs for framework use (no ground truth — just structure)
A_obs = A_full[:N_OBS, :N_OBS]
np.save(f"{OUT_DIR}/A_obs.npy", A_obs)
with open(f"{OUT_DIR}/A_obs.npy", "rb") as fh:
    traj_hashes["A_obs.npy"] = hashlib.sha256(fh.read()).hexdigest()

# Dataset manifest
dataset_manifest = {
    "oracle_master_hash": stored_master,
    "generation_timestamp": gen_time,
    "oracle_timestamp": oracle_mtime,
    "lc4_oracle_before_trajectories": gen_time > oracle_mtime,
    "parameters": {
        "N_OBS": N_OBS, "N_TOTAL": N_TOTAL,
        "T_A": T_A, "T_B": T_B, "dt": DT, "burn_in": BURN_IN,
        "seed_A": 100, "seed_B": 200, "seed_lesion": 300,
    },
    "dataset_stats": {
        "x_A_shape": list(x_A.shape),
        "x_B_shape": list(x_B.shape),
        "x_A_lesion_shape": list(x_A_lesion.shape),
        "pmc_src_var_ratio_A_over_B": float(ratio_src),
        "background_var_ratio_A_over_B": float(ratio_bg),
        "empirical_sigma_A_min_eig": float(min_eig),
    },
    "file_hashes": traj_hashes,
}

with open(f"{OUT_DIR}/dataset_manifest.json", "w") as f:
    json.dump(dataset_manifest, f, indent=2)

dataset_master = hashlib.sha256(
    json.dumps(traj_hashes, sort_keys=True).encode()
).hexdigest()
with open(f"{OUT_DIR}/dataset_master_hash.txt", "w") as f:
    f.write(dataset_master + "\n")
print(f"\n  Dataset master hash: {dataset_master[:16]}...")

# ── Make trajectories read-only ───────────────────────────────────────────────
import stat
for fname in ["x_A.npy", "x_B.npy", "x_A_lesion.npy"]:
    fpath = os.path.join(OUT_DIR, fname)
    os.chmod(fpath, stat.S_IRUSR | stat.S_IRGRP)
    print(f"  {fname}: set read-only")

print("\n=== SIMULATOR COMPLETE ===")
print("  All acceptance tests PASS")
print("  Trajectories frozen (read-only)")
print(f"  Dataset master hash: {dataset_master[:16]}...")
