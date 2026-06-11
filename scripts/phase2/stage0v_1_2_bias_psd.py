"""Stage 0-V.1 and 0-V.2 — Pairwise covariance bias/variance and PSD projection.

Authorized: 2026-05-31. Implements V.1 and V.2 only per human authorization.
Stops after V.2. Does not proceed to V.3.

Outputs written to results/phase2/stage0v/:
    v1_bias_variance.json
    v2_psd_characterization.json

All seeds from phase0_config.RANDOM_SEED = 20260527.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import phase0_config as cfg

# ── Constants ────────────────────────────────────────────────────────────────

RANDOM_SEED  = cfg.RANDOM_SEED          # 20260527
N_REP        = 100                      # synthetic replications (V.1 and V.2)
EFFECT_SIZE  = 0.2                      # planted ΔQ magnitude
P_SIGNAL     = 10                       # planted off-connectome pairs
N            = 61                       # number of neurons
PSD_FLOORS   = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]  # sweep for V.2

OUT_DIR = ROOT / "results" / "phase2" / "stage0v"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMON_61 = sorted([
    "ADEL", "AIBL", "AIBR", "AIZL", "ASEL", "ASGL", "AUAL", "AVAL", "AVAR",
    "AVDL", "AVEL", "AVER", "AVJL", "AVJR", "AWAL", "AWBL", "AWCL", "CEPDL",
    "CEPDR", "CEPVL", "FLPL", "I1L",  "I1R",  "I2L",  "I2R",  "I3",  "IL1DR",
    "IL1L", "IL1R",  "IL2DL","IL2DR","IL2VL","IL2VR","M1",   "M3L",  "M3R",
    "M4",   "MI",    "NSML", "NSMR", "OLLL", "OLLR", "OLQDL","OLQDR","OLQVL",
    "OLQVR","RICL",  "RID",  "RIVL", "RMDDR","RMDL", "RMDVL","RMDVR","RMEL",
    "RMER", "SMDVL", "URBL", "URXL", "URYDL","URYVL","URYVR",
])
assert len(COMMON_61) == N

# ── Load SF corpus structure from Stage 0.1 outputs ─────────────────────────

presence    = np.load("/tmp/presence_matrix.npy")     # (40, 61) bool
roam_frames  = np.load("/tmp/roam_frames.npy")         # (40,) int
dwell_frames = np.load("/tmp/dwell_frames.npy")        # (40,) int
A_raw       = np.load("/tmp/A_raw_61.npy")             # (61, 61) int

with open("/tmp/rec_ids.json") as f:
    rec_ids = json.load(f)

N_REC = len(rec_ids)  # 40

# State-available (neuron present AND recording contributes state frames)
roam_avail  = (presence & (roam_frames  > 0)[:, None]).astype(bool)  # (40, 61)
dwell_avail = (presence & (dwell_frames > 0)[:, None]).astype(bool)  # (40, 61)

# Off-connectome pairs (upper triangle)
ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)

off_connectome_mask = A_raw[ii_all, jj_all] == 0  # (n_pairs,) bool
off_pairs_ii = ii_all[off_connectome_mask]
off_pairs_jj = jj_all[off_connectome_mask]
n_off = off_connectome_mask.sum()
print(f"Off-connectome pairs: {n_off} / {n_pairs} total pairs")


# ── True precision matrix constructor ────────────────────────────────────────

def make_true_precisions(rng: np.random.Generator, effect_size: float = EFFECT_SIZE,
                         p_signal: int = P_SIGNAL) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct Q_true_roam, Q_true_dwell, Sigma_true_shared.

    Returns:
        Q_true_roam:  (N, N) true precision, roaming state
        Q_true_dwell: (N, N) true precision, dwelling state
        Sigma_dwell:  (N, N) = Q_true_dwell^{-1}
        signal_pairs: (p_signal, 2) array of planted (i, j) off-connectome pairs
    """
    # Build a shared baseline sparse positive-definite precision Q_0.
    # Use Wishart(df=2*N, scale=I/N) — produces a well-conditioned matrix.
    W = rng.standard_normal((2 * N, N))
    Q_base = (W.T @ W) / (2 * N) + 0.5 * np.eye(N)  # ensure PD

    # Threshold to impose sparsity matching connectome density (~14%)
    # Keep diagonal + on-connectome entries + a random sparse off-connectome fraction
    sparsity_mask = np.zeros((N, N), dtype=bool)
    np.fill_diagonal(sparsity_mask, True)
    # On-connectome: always non-zero
    sparsity_mask |= A_raw.astype(bool)
    # Off-connectome: randomly keep ~15% to match realistic sparsity
    off_mask_full = (A_raw == 0)
    np.fill_diagonal(off_mask_full, False)
    off_ii, off_jj = np.where(np.triu(off_mask_full, k=1))
    keep = rng.random(len(off_ii)) < 0.15
    for k in np.where(keep)[0]:
        sparsity_mask[off_ii[k], off_jj[k]] = True
        sparsity_mask[off_jj[k], off_ii[k]] = True

    Q_0 = Q_base * sparsity_mask
    # Force PD by adding a scaled identity
    min_eig = np.linalg.eigvalsh(Q_0).min()
    if min_eig < 0.1:
        Q_0 += (0.1 - min_eig + 0.05) * np.eye(N)

    # Dwelling state precision = Q_0
    Q_true_dwell = Q_0.copy()

    # Roaming state: plant signal in p_signal off-connectome pairs
    signal_choice = rng.choice(n_off, size=p_signal, replace=False)
    signal_ii = off_pairs_ii[signal_choice]
    signal_jj = off_pairs_jj[signal_choice]

    Q_true_roam = Q_true_dwell.copy()
    for si, sj in zip(signal_ii, signal_jj):
        Q_true_roam[si, sj] += effect_size
        Q_true_roam[sj, si] += effect_size

    # Ensure roaming Q is also PD
    min_eig_roam = np.linalg.eigvalsh(Q_true_roam).min()
    if min_eig_roam < 0.05:
        Q_true_roam += (0.05 - min_eig_roam + 0.01) * np.eye(N)

    signal_pairs = np.column_stack([signal_ii, signal_jj])
    return Q_true_roam, Q_true_dwell, signal_pairs


# ── Synthetic data generator ─────────────────────────────────────────────────

def generate_synthetic_data(Q_true_s: np.ndarray,
                            state_frames: np.ndarray,
                            avail: np.ndarray,
                            rng: np.random.Generator) -> dict[int, np.ndarray]:
    """Generate synthetic data for one state under exact SF missingness.

    For each recording r where avail[r] has ≥1 True neuron and state_frames[r] > 0:
      - Identify O_r = present neurons
      - Compute marginal covariance Sigma_s[O_r, O_r] = (Q_true_s[O_r, O_r])^{-1}
      - Draw T_{r,s} multivariate Gaussian samples
      - Store as (T_{r,s}, N) array with NaN for absent neurons

    Returns: dict rec_idx → array(T_r, N) with NaN for absent columns
    """
    Sigma_true = np.linalg.inv(Q_true_s)
    rec_data = {}

    for r in range(N_REC):
        T_r = int(state_frames[r])
        if T_r == 0:
            continue
        O_r = np.where(avail[r])[0]  # indices of present neurons in this recording
        if len(O_r) == 0:
            continue

        # Marginal covariance for observed neurons (submatrix of full inverse)
        Sigma_r = Sigma_true[np.ix_(O_r, O_r)]

        # Ensure numerical symmetry and PD
        Sigma_r = (Sigma_r + Sigma_r.T) / 2
        min_eig = np.linalg.eigvalsh(Sigma_r).min()
        if min_eig < 1e-10:
            Sigma_r += (1e-8 - min_eig) * np.eye(len(O_r))

        # Generate samples: mean 0, covariance Sigma_r
        L = np.linalg.cholesky(Sigma_r)
        Z = rng.standard_normal((T_r, len(O_r)))
        samples = Z @ L.T  # (T_r, |O_r|)

        # Assemble full-N array with NaN for absent neurons
        X_r = np.full((T_r, N), np.nan)
        X_r[:, O_r] = samples

        rec_data[r] = X_r

    return rec_data


# ── Pairwise covariance assembly ─────────────────────────────────────────────

def assemble_pairwise_cov(rec_data: dict[int, np.ndarray],
                          avail: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Assemble 61×61 pairwise available-case covariance matrix.

    Returns:
        S:         (N, N) symmetric assembled covariance
        n_frames:  (N, N) int — number of frames used per pair
        n_recs:    (N, N) int — number of recordings used per pair
    """
    # Accumulate cross-products and counts per pair
    # Using running sums to avoid storing all frames
    sum_xi    = np.zeros((N, N))      # Σ x_i for each (i, j) pair
    sum_xj    = np.zeros((N, N))
    sum_xixj  = np.zeros((N, N))
    n_frames_mat = np.zeros((N, N), dtype=int)
    n_recs_mat   = np.zeros((N, N), dtype=int)

    # Diagonal: use all marginal recordings for each neuron
    sum_xi_diag  = np.zeros(N)
    sum_xi2_diag = np.zeros(N)
    n_frames_diag = np.zeros(N, dtype=int)

    for r, X_r in rec_data.items():
        T_r = X_r.shape[0]
        present = np.where(avail[r])[0]

        # Diagonal accumulation
        for i in present:
            xi = X_r[:, i]  # no NaN guaranteed for present neurons
            sum_xi_diag[i]  += xi.sum()
            sum_xi2_diag[i] += (xi ** 2).sum()
            n_frames_diag[i] += T_r

        # Off-diagonal: accumulate for all co-present pairs
        for k, i in enumerate(present):
            xi = X_r[:, i]
            for j in present[k + 1:]:
                xj = X_r[:, j]
                sum_xi[i, j]   += xi.sum()
                sum_xj[i, j]   += xj.sum()
                sum_xixj[i, j] += (xi * xj).sum()
                n_frames_mat[i, j] += T_r
                n_recs_mat[i, j]   += 1

    # Compute sample covariance per pair: cov(i,j) = (Σ xi*xj - n*mean_i*mean_j) / (n-1)
    S = np.zeros((N, N))

    # Diagonal
    for i in range(N):
        n = n_frames_diag[i]
        if n >= 2:
            mean_i = sum_xi_diag[i] / n
            S[i, i] = (sum_xi2_diag[i] - n * mean_i ** 2) / (n - 1)
        else:
            S[i, i] = np.nan

    # Off-diagonal
    for i in range(N):
        for j in range(i + 1, N):
            n = n_frames_mat[i, j]
            if n >= 2:
                mean_i = sum_xi[i, j] / n
                mean_j = sum_xj[i, j] / n
                cov_ij = (sum_xixj[i, j] - n * mean_i * mean_j) / (n - 1)
                S[i, j] = cov_ij
                S[j, i] = cov_ij
                n_frames_mat[j, i] = n_frames_mat[i, j]
                n_recs_mat[j, i]   = n_recs_mat[i, j]
            else:
                S[i, j] = S[j, i] = np.nan

    return S, n_frames_mat, n_recs_mat


# ── PSD projection (eigenvalue clipping) ─────────────────────────────────────

def psd_project(S: np.ndarray, floor: float) -> tuple[np.ndarray, dict]:
    """Clip negative eigenvalues to floor. Return projected matrix + diagnostics."""
    S_sym = (S + S.T) / 2  # enforce symmetry numerically
    eigvals, eigvecs = np.linalg.eigh(S_sym)

    n_clipped = int((eigvals < floor).sum())
    spectral_mass_removed = float(np.maximum(0, floor - eigvals).sum())
    spectral_mass_total   = float(eigvals.sum())

    eigvals_clipped = np.maximum(eigvals, floor)
    S_proj = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    S_proj = (S_proj + S_proj.T) / 2  # enforce symmetry numerically

    cond_number = float(eigvals_clipped.max() / eigvals_clipped.min()) if eigvals_clipped.min() > 0 else np.inf

    diag = {
        "eigenvalues_original": eigvals.tolist(),
        "n_clipped": n_clipped,
        "clip_fraction": n_clipped / N,
        "spectral_mass_removed": spectral_mass_removed,
        "spectral_mass_total": spectral_mass_total,
        "spectral_mass_removed_fraction": (spectral_mass_removed / spectral_mass_total
                                           if spectral_mass_total > 0 else 0.0),
        "condition_number": cond_number,
        "psd_floor": floor,
    }
    return S_proj, diag


# ── WN-PSD projection (weighted nearest PSD via ADMM) ────────────────────────

def wn_psd_project(S: np.ndarray, weights: np.ndarray,
                   max_iter: int = 2000, tol: float = 1e-6) -> tuple[np.ndarray, dict]:
    """Weighted nearest PSD: minimize Σ w_ij (S_ij - Σ̂_ij)² subject to Σ̂ ≻ 0.

    Uses Dykstra-like alternating projections:
        Project onto PSD cone (eigenvalue clipping at 0)
        Project back toward observed S weighted by W
    This is equivalent to the Douglas-Rachford splitting for the
    indicator function of PSD cone + weighted L2 fidelity.

    For the weighted problem with general W, we use ADMM:
        min  (1/2)||W^{1/2} ⊙ (S - X)||_F²  s.t.  X ≻ 0
    Augmented Lagrangian: separate X (fidelity) and Z (PSD cone) variables.
    """
    W = weights  # (N, N) symmetric non-negative weights
    S_sym = (S + S.T) / 2

    # ADMM: min f(X) + g(Z) s.t. X = Z
    # f(X) = (1/2) Σ w_ij (S_ij - X_ij)²   (element-wise weighted L2)
    # g(Z) = 0 if Z ≻ 0, else ∞              (PSD indicator)
    # Augmented: f(X) + g(Z) + (rho/2)||X - Z + U||_F²

    rho = 1.0  # ADMM step size
    X = S_sym.copy()
    Z = S_sym.copy()
    U = np.zeros_like(S_sym)

    prev_Z = Z.copy()

    for iteration in range(max_iter):
        # X-update: minimize (1/2) Σ w_ij (S_ij - X_ij)² + (rho/2)||X - Z + U||_F²
        # Closed form element-wise: X_ij = (w_ij * S_ij + rho * (Z_ij - U_ij)) / (w_ij + rho)
        X = (W * S_sym + rho * (Z - U)) / (W + rho)
        X = (X + X.T) / 2  # keep symmetric

        # Z-update: project X + U onto PSD cone
        M = X + U
        M = (M + M.T) / 2
        eigvals, eigvecs = np.linalg.eigh(M)
        eigvals_clipped = np.maximum(eigvals, 0.0)
        Z = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
        Z = (Z + Z.T) / 2

        # Dual update
        U = U + X - Z

        # Convergence check
        primal_res = np.linalg.norm(X - Z, 'fro')
        dual_res   = rho * np.linalg.norm(Z - prev_Z, 'fro')
        prev_Z = Z.copy()

        if primal_res < tol and dual_res < tol:
            break

    # Diagnostics using Z (the PSD-projected output)
    eigvals_final = np.linalg.eigvalsh(Z)
    n_negative = int((eigvals_final < 0).sum())
    cond_number = float(eigvals_final.max() / max(eigvals_final.min(), 1e-15))
    fidelity = float(np.sum(W * (S_sym - Z) ** 2))

    diag = {
        "method": "wn_psd_admm",
        "n_admm_iterations": iteration + 1,
        "converged": (primal_res < tol and dual_res < tol),
        "primal_residual_final": float(primal_res),
        "dual_residual_final": float(dual_res),
        "n_negative_eigenvalues_remaining": n_negative,
        "min_eigenvalue": float(eigvals_final.min()),
        "condition_number": cond_number,
        "weighted_fidelity_loss": fidelity,
    }
    return Z, diag


# ── Stage 0-V.1 — Bias and variance characterization ─────────────────────────

def run_v1(rng_master: np.random.Generator) -> dict:
    """Run 100 synthetic replications; characterize pairwise covariance bias/variance."""
    print("\n" + "=" * 60)
    print("Stage 0-V.1 — Pairwise covariance bias/variance")
    print("=" * 60)

    # Use a fixed Q_true constructed with a dedicated seed for reproducibility
    rng_design = np.random.default_rng(RANDOM_SEED)
    Q_true_roam, Q_true_dwell, signal_pairs = make_true_precisions(rng_design)
    Sigma_true_dwell = np.linalg.inv(Q_true_dwell)
    Sigma_true_roam  = np.linalg.inv(Q_true_roam)

    print(f"Q_true_dwell: min eig = {np.linalg.eigvalsh(Q_true_dwell).min():.4f}, "
          f"max eig = {np.linalg.eigvalsh(Q_true_dwell).max():.4f}")
    print(f"Q_true_roam:  min eig = {np.linalg.eigvalsh(Q_true_roam).min():.4f}, "
          f"max eig = {np.linalg.eigvalsh(Q_true_roam).max():.4f}")
    print(f"Planted signal pairs (off-connectome, roaming): {len(signal_pairs)}")

    # Collect pairwise S estimates across replications for both states
    S_roam_reps  = np.zeros((N_REP, N, N))
    S_dwell_reps = np.zeros((N_REP, N, N))

    t0 = time.time()
    for rep in range(N_REP):
        rng_rep = np.random.default_rng(RANDOM_SEED + rep + 1000)

        rec_data_roam  = generate_synthetic_data(Q_true_roam,  roam_frames,  roam_avail,  rng_rep)
        rec_data_dwell = generate_synthetic_data(Q_true_dwell, dwell_frames, dwell_avail, rng_rep)

        S_roam,  _, _ = assemble_pairwise_cov(rec_data_roam,  roam_avail)
        S_dwell, _, _ = assemble_pairwise_cov(rec_data_dwell, dwell_avail)

        S_roam_reps[rep]  = S_roam
        S_dwell_reps[rep] = S_dwell

        if (rep + 1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"  Rep {rep+1}/{N_REP} done ({elapsed:.0f}s)")

    print(f"All {N_REP} replications done in {time.time()-t0:.0f}s")

    # ── Compute bias and variance diagnostics ──────────────────────────────
    results = {}
    for state, S_reps, Sigma_true in [
        ("roaming",  S_roam_reps,  Sigma_true_roam),
        ("dwelling", S_dwell_reps, Sigma_true_dwell),
    ]:
        # Off-diagonal entries only (upper triangle)
        S_stack   = S_reps[:, ii_all, jj_all]   # (N_REP, n_pairs)
        truth_vec = Sigma_true[ii_all, jj_all]   # (n_pairs,)

        # Per-entry bias
        mean_S = np.nanmean(S_stack, axis=0)     # (n_pairs,)
        bias   = mean_S - truth_vec               # (n_pairs,)
        abs_truth = np.abs(truth_vec)

        # Normalized bias (skip entries where truth ≈ 0 to avoid division)
        nonzero_mask = abs_truth > 1e-6
        norm_bias = np.abs(bias[nonzero_mask]) / abs_truth[nonzero_mask]

        frac_bias_lt_001 = float((norm_bias < 0.01).mean())
        frac_bias_lt_005 = float((norm_bias < 0.05).mean())

        # Pearson correlation per replication
        pearson_per_rep = np.array([
            np.corrcoef(S_stack[r][nonzero_mask], truth_vec[nonzero_mask])[0, 1]
            for r in range(N_REP)
        ])
        median_pearson = float(np.nanmedian(pearson_per_rep))
        p10_pearson    = float(np.nanpercentile(pearson_per_rep, 10))

        # Variance per entry
        var_S = np.nanvar(S_stack, axis=0)
        median_var = float(np.nanmedian(var_S))

        # Pass conditions
        pass_bias    = frac_bias_lt_001 >= 0.95
        pass_pearson = median_pearson >= 0.90

        print(f"\n  {state.upper()}:")
        print(f"    Fraction entries with |bias|/|truth| < 0.01: {frac_bias_lt_001:.3f} "
              f"{'[PASS]' if pass_bias else '[FAIL]'}")
        print(f"    Fraction entries with |bias|/|truth| < 0.05: {frac_bias_lt_005:.3f}")
        print(f"    Median bias (abs): {np.nanmedian(np.abs(bias)):.6f}")
        print(f"    Max bias (abs):    {np.nanmax(np.abs(bias)):.6f}")
        print(f"    Median |bias|/|truth| (nonzero entries): {float(np.nanmedian(norm_bias)):.5f}")
        print(f"    Max    |bias|/|truth| (nonzero entries): {float(np.nanmax(norm_bias)):.5f}")
        print(f"    Pearson corr(S_pairwise, Sigma_true): median={median_pearson:.4f}, "
              f"p10={p10_pearson:.4f} {'[PASS]' if pass_pearson else '[FAIL]'}")
        print(f"    Median entry variance across reps: {median_var:.6f}")

        results[state] = {
            "frac_norm_bias_lt_001": frac_bias_lt_001,
            "frac_norm_bias_lt_005": frac_bias_lt_005,
            "median_abs_bias": float(np.nanmedian(np.abs(bias))),
            "max_abs_bias": float(np.nanmax(np.abs(bias))),
            "median_norm_bias": float(np.nanmedian(norm_bias)),
            "max_norm_bias": float(np.nanmax(norm_bias)),
            "pearson_median": median_pearson,
            "pearson_p10": p10_pearson,
            "pearson_per_rep": pearson_per_rep.tolist(),
            "median_entry_variance": median_var,
            "pass_bias_criterion": pass_bias,
            "pass_pearson_criterion": pass_pearson,
        }

    overall_pass = all(results[s]["pass_bias_criterion"] and results[s]["pass_pearson_criterion"]
                       for s in ["roaming", "dwelling"])

    report = {
        "stage": "0-V.1",
        "date": "2026-05-31",
        "n_rep": N_REP,
        "effect_size": EFFECT_SIZE,
        "p_signal": P_SIGNAL,
        "n_neurons": N,
        "random_seed": RANDOM_SEED,
        "pass_conditions": {
            "norm_bias_lt_001_for_95pct_entries": "frac_norm_bias_lt_001 >= 0.95",
            "pearson_corr_ge_090": "pearson_median >= 0.90",
        },
        "results": results,
        "overall_pass": overall_pass,
    }

    out_path = OUT_DIR / "v1_bias_variance.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  V.1 report saved to {out_path}")
    print(f"  Overall V.1 pass: {overall_pass}")

    # Return S_reps for V.2 (avoids re-generating synthetic data)
    return report, S_roam_reps, S_dwell_reps, Sigma_true_roam, Sigma_true_dwell


# ── Stage 0-V.2 — PSD projection characterization ────────────────────────────

def run_v2(S_roam_reps:  np.ndarray,
           S_dwell_reps: np.ndarray,
           Sigma_true_roam:  np.ndarray,
           Sigma_true_dwell: np.ndarray) -> dict:
    """Sweep PSD floor values; characterize clipping and rank-order preservation."""
    print("\n" + "=" * 60)
    print("Stage 0-V.2 — PSD projection characterization")
    print("=" * 60)

    # Compute n_eff weights from Stage 0.1 (used if WN-PSD escalation triggered)
    roam_neff_arr  = np.load("/tmp/roam_neff.npy")   # (n_pairs,)
    dwell_neff_arr = np.load("/tmp/dwell_neff.npy")  # (n_pairs,)

    def build_weight_matrix(neff_arr: np.ndarray) -> np.ndarray:
        """Assemble (N, N) weight matrix from per-pair n_eff array (upper-triangle order)."""
        W = np.zeros((N, N))
        for k, (i, j) in enumerate(zip(ii_all, jj_all)):
            W[i, j] = W[j, i] = neff_arr[k]
        # Diagonal: use mean of column n_eff for that neuron
        for i in range(N):
            neighbors = [k for k, (a, b) in enumerate(zip(ii_all, jj_all)) if a == i or b == i]
            W[i, i] = np.mean(neff_arr[neighbors]) if neighbors else 1.0
        return W

    W_roam  = build_weight_matrix(roam_neff_arr)
    W_dwell = build_weight_matrix(dwell_neff_arr)

    results = {}
    escalation_triggered = False  # set True if eigenvalue clipping fails V.2

    for state, S_reps, Sigma_true, W_mat in [
        ("roaming",  S_roam_reps,  Sigma_true_roam,  W_roam),
        ("dwelling", S_dwell_reps, Sigma_true_dwell, W_dwell),
    ]:
        print(f"\n  {state.upper()}:")
        truth_off = Sigma_true[ii_all, jj_all]  # (n_pairs,) true off-diagonal
        state_results = {"floors": {}}

        best_floor_clipping = None   # floor selected by calibration rule
        best_floor_spearman = None   # for escalation check

        for floor in PSD_FLOORS:
            clip_fracs   = []
            frob_dists   = []
            spearman_rs  = []
            cond_numbers = []
            mass_removed_fracs = []

            for rep in range(N_REP):
                S = S_reps[rep]
                S_proj, diag = psd_project(S, floor)

                proj_off = S_proj[ii_all, jj_all]   # (n_pairs,)

                # Frobenius distance (full matrix)
                frob_S_true = np.linalg.norm(Sigma_true, 'fro')
                frob_dist   = np.linalg.norm(S_proj - Sigma_true, 'fro') / frob_S_true

                # Spearman rank correlation (off-diagonal only)
                rho, _ = stats.spearmanr(proj_off, truth_off)

                clip_fracs.append(diag["clip_fraction"])
                frob_dists.append(frob_dist)
                spearman_rs.append(rho)
                cond_numbers.append(diag["condition_number"])
                mass_removed_fracs.append(diag["spectral_mass_removed_fraction"])

            clip_fracs   = np.array(clip_fracs)
            spearman_rs  = np.array(spearman_rs)
            cond_numbers = np.array(cond_numbers)
            frob_dists   = np.array(frob_dists)
            mass_removed_fracs = np.array(mass_removed_fracs)

            pass_clip     = float(np.median(clip_fracs)) <= 0.15
            pass_spearman = float(np.mean(spearman_rs >= 0.95)) >= 0.90
            pass_cond     = float(np.mean(np.array(cond_numbers) < 1e6)) >= 0.99

            print(f"    floor={floor:.0e}: "
                  f"clip_frac median={np.median(clip_fracs):.3f} "
                  f"[{'P' if pass_clip else 'F'}], "
                  f"Spearman≥0.95 in {100*np.mean(spearman_rs>=0.95):.0f}% reps "
                  f"[{'P' if pass_spearman else 'F'}], "
                  f"median Spearman={np.median(spearman_rs):.4f}, "
                  f"cond<1e6 in {100*np.mean(np.array(cond_numbers)<1e6):.0f}% reps "
                  f"[{'P' if pass_cond else 'F'}]")

            state_results["floors"][str(floor)] = {
                "clip_fraction_median":     float(np.median(clip_fracs)),
                "clip_fraction_p90":        float(np.percentile(clip_fracs, 90)),
                "clip_fraction_max":        float(np.max(clip_fracs)),
                "clip_fraction_per_rep":    clip_fracs.tolist(),
                "spearman_median":          float(np.median(spearman_rs)),
                "spearman_p10":             float(np.percentile(spearman_rs, 10)),
                "frac_reps_spearman_ge_095": float(np.mean(spearman_rs >= 0.95)),
                "frob_dist_median":         float(np.median(frob_dists)),
                "cond_number_median":       float(np.median(cond_numbers)),
                "frac_reps_cond_lt_1e6":    float(np.mean(np.array(cond_numbers) < 1e6)),
                "spectral_mass_removed_frac_median": float(np.median(mass_removed_fracs)),
                "pass_clip":     pass_clip,
                "pass_spearman": pass_spearman,
                "pass_cond":     pass_cond,
                "all_pass":      (pass_clip and pass_spearman and pass_cond),
            }

        # Calibration rule: select smallest floor where median clip_fraction ≤ 0.10
        # (tighter than the ≤ 0.15 pass condition — prefer conservative clipping)
        calibrated_floor = None
        for floor in PSD_FLOORS:
            cf = state_results["floors"][str(floor)]["clip_fraction_median"]
            if cf <= 0.10:
                calibrated_floor = floor
                break

        if calibrated_floor is None:
            # Relax to ≤ 0.15 (pass condition threshold)
            for floor in PSD_FLOORS:
                cf = state_results["floors"][str(floor)]["clip_fraction_median"]
                if cf <= 0.15:
                    calibrated_floor = floor
                    break

        state_results["calibrated_floor"] = calibrated_floor

        # Check whether the calibrated floor passes the Spearman criterion
        if calibrated_floor is not None:
            cal_spearman_pass = state_results["floors"][str(calibrated_floor)]["pass_spearman"]
            state_results["calibrated_floor_passes_spearman"] = cal_spearman_pass
            if not cal_spearman_pass:
                escalation_triggered = True
                print(f"  *** ESCALATION TRIGGER: {state} Spearman criterion fails at calibrated floor "
                      f"{calibrated_floor:.0e} ***")
        else:
            state_results["calibrated_floor_passes_spearman"] = False
            escalation_triggered = True
            print(f"  *** ESCALATION TRIGGER: no calibrated floor found for {state} ***")

        results[state] = state_results

    # ── WN-PSD escalation if triggered ───────────────────────────────────────
    wn_psd_results = None
    if escalation_triggered:
        print("\n" + "-" * 60)
        print("ESCALATION: eigenvalue clipping failed — running WN-PSD projection")
        print("-" * 60)
        wn_psd_results = {}

        for state, S_reps, Sigma_true, W_mat in [
            ("roaming",  S_roam_reps,  Sigma_true_roam,  W_roam),
            ("dwelling", S_dwell_reps, Sigma_true_dwell, W_dwell),
        ]:
            print(f"\n  WN-PSD {state.upper()}:")
            truth_off = Sigma_true[ii_all, jj_all]

            clip_fracs_wn  = []
            frob_dists_wn  = []
            spearman_rs_wn = []
            cond_numbers_wn = []
            convergence_wn  = []
            iters_wn        = []

            for rep in range(N_REP):
                S = S_reps[rep]
                S_proj_wn, diag_wn = wn_psd_project(S, W_mat)

                proj_off_wn = S_proj_wn[ii_all, jj_all]
                frob_S_true  = np.linalg.norm(Sigma_true, 'fro')
                frob_dist_wn = np.linalg.norm(S_proj_wn - Sigma_true, 'fro') / frob_S_true

                rho_wn, _ = stats.spearmanr(proj_off_wn, truth_off)

                # Clip fraction equivalent: neg eigenvalues remaining
                eigvals_wn = np.linalg.eigvalsh(S_proj_wn)
                n_neg = (eigvals_wn < 0).sum()
                cond_wn = eigvals_wn.max() / max(eigvals_wn.min(), 1e-15)

                clip_fracs_wn.append(n_neg / N)
                frob_dists_wn.append(frob_dist_wn)
                spearman_rs_wn.append(rho_wn)
                cond_numbers_wn.append(cond_wn)
                convergence_wn.append(diag_wn["converged"])
                iters_wn.append(diag_wn["n_admm_iterations"])

                if (rep + 1) % 25 == 0:
                    print(f"    Rep {rep+1}/{N_REP}")

            clip_fracs_wn  = np.array(clip_fracs_wn)
            spearman_rs_wn = np.array(spearman_rs_wn)

            pass_spearman_wn = float(np.mean(spearman_rs_wn >= 0.95)) >= 0.90

            print(f"    WN-PSD: neg-eig frac median={np.median(clip_fracs_wn):.4f}, "
                  f"Spearman≥0.95 in {100*np.mean(spearman_rs_wn>=0.95):.0f}% reps "
                  f"[{'PASS' if pass_spearman_wn else 'FAIL'}], "
                  f"median Spearman={np.median(spearman_rs_wn):.4f}, "
                  f"convergence rate={np.mean(convergence_wn):.2f}")

            wn_psd_results[state] = {
                "neg_eig_fraction_median": float(np.median(clip_fracs_wn)),
                "spearman_median": float(np.median(spearman_rs_wn)),
                "frac_reps_spearman_ge_095": float(np.mean(spearman_rs_wn >= 0.95)),
                "frob_dist_median": float(np.median(frob_dists_wn)),
                "convergence_rate": float(np.mean(convergence_wn)),
                "mean_admm_iterations": float(np.mean(iters_wn)),
                "pass_spearman": pass_spearman_wn,
            }

    # ── Overall V.2 summary ───────────────────────────────────────────────────
    overall_pass_v2 = not escalation_triggered  # eigenvalue clipping passed
    if escalation_triggered and wn_psd_results is not None:
        # WN-PSD passes if both states pass Spearman
        wn_pass = all(wn_psd_results[s]["pass_spearman"] for s in ["roaming", "dwelling"])
        overall_pass_v2_wn = wn_pass
        print(f"\n  WN-PSD overall V.2 pass: {overall_pass_v2_wn}")
    else:
        overall_pass_v2_wn = None

    print(f"\n  Eigenvalue clipping V.2 pass: {overall_pass_v2}")
    print(f"  Escalation triggered: {escalation_triggered}")

    # Determine selected PSD method
    if not escalation_triggered:
        # Eigenvalue clipping passed — select the calibrated floor
        calibrated_floors = {s: results[s]["calibrated_floor"] for s in ["roaming", "dwelling"]}
        # Use the larger of the two floors (more conservative, ensures both states are covered)
        valid_floors = [f for f in calibrated_floors.values() if f is not None]
        selected_floor = max(valid_floors) if valid_floors else None
        selected_method = "eigenvalue_clipping"
        print(f"\n  Calibrated PSD_EIGENVALUE_FLOOR proposal: "
              f"roaming={calibrated_floors['roaming']:.0e}, "
              f"dwelling={calibrated_floors['dwelling']:.0e}")
        print(f"  Recommended PSD_EIGENVALUE_FLOOR: {selected_floor:.0e} (max of two states)")
    else:
        selected_floor = 0.0
        selected_method = "wn_psd" if (overall_pass_v2_wn) else "NEITHER_PASSED"

    report = {
        "stage": "0-V.2",
        "date": "2026-05-31",
        "n_rep": N_REP,
        "psd_floors_swept": PSD_FLOORS,
        "pass_conditions": {
            "median_clip_frac_le_015": "True",
            "frac_reps_spearman_ge_095_ge_090pct": "True",
            "frac_reps_cond_lt_1e6_ge_099pct": "True",
        },
        "eigenvalue_clipping": results,
        "escalation_triggered": escalation_triggered,
        "wn_psd_results": wn_psd_results,
        "overall_pass_eigenvalue_clipping": overall_pass_v2,
        "overall_pass_wn_psd": overall_pass_v2_wn,
        "selected_psd_method": selected_method,
        "recommended_psd_floor": selected_floor,
    }

    out_path = OUT_DIR / "v2_psd_characterization.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  V.2 report saved to {out_path}")

    return report


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 0-V.1 and 0-V.2 — PAC-PSD-GL Validation")
    print("Authorized: V.1 and V.2 only. Will not proceed to V.3.")
    print(f"N_REP={N_REP}, EFFECT_SIZE={EFFECT_SIZE}, RANDOM_SEED={RANDOM_SEED}")
    print("=" * 60)

    t_start = time.time()
    rng_master = np.random.default_rng(RANDOM_SEED)

    # V.1
    v1_report, S_roam_reps, S_dwell_reps, Sigma_true_roam, Sigma_true_dwell = run_v1(rng_master)

    # V.2 (uses the same synthetic S matrices from V.1)
    v2_report = run_v2(S_roam_reps, S_dwell_reps, Sigma_true_roam, Sigma_true_dwell)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"V.1 overall pass:  {v1_report['overall_pass']}")
    print(f"V.2 eigenclip pass: {v2_report['overall_pass_eigenvalue_clipping']}")
    print(f"V.2 escalation triggered: {v2_report['escalation_triggered']}")
    if v2_report['escalation_triggered']:
        print(f"V.2 WN-PSD pass:   {v2_report['overall_pass_wn_psd']}")
    print(f"Selected PSD method: {v2_report['selected_psd_method']}")
    if v2_report['recommended_psd_floor'] is not None:
        print(f"Recommended PSD_EIGENVALUE_FLOOR: {v2_report['recommended_psd_floor']:.0e}")
    print(f"\nTotal wall time: {time.time()-t_start:.0f}s")
    print("\nSTOPPING after V.2 as authorized. V.3 not run.")


if __name__ == "__main__":
    main()
