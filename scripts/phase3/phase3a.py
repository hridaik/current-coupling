"""Phase 3A — State-dependent PDF effective-connectivity model.

Authorization: 2026-06-03, human supervisor.

Locked decisions:
  J  = White/Witvliet directed anatomical connectome (A_raw directed)
  P  = Directed Bentley PDF graph (pdf-1/pdf-2 → pdfr-1)
  α  = scalar per state {roam, dwell}; no matrix-valued α
  Objective = Spearman rank correlation on training Class 4 pairs
  Held-out  = ADEL-URYVR, ADEL-URYDL, ADEL-RMEL, ADEL-URXL (4 pairs; evaluation-only)
  M3 = Creamer A_C as J (fully_connected dynamics_weights, 154→56 subspace)

Models:
  M0: J_eff = J_base (state-independent), ΔQ_pred ≡ 0
  M1: J_eff(s) = J_base + α_s * P  (primary)
  M2: J_eff(s) = J_base + α_s * P_rand (randomized P ensemble; 1000 draws)
  M3: J_eff(s) = J_base_creamer + α_s * P  (Creamer A_C base)

STOP after model comparison report. No held-out evaluation.
"""
from __future__ import annotations
import csv, json, sys, time, warnings
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
from scipy import linalg, stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "results/phase3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

import phase0_config as p0cfg
import phase2_config as p2cfg

SEED = 2026_06_03
rng  = np.random.default_rng(SEED)

# ── Canonical neuron list ─────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS  = cop["neurons"]
REC_IDS  = cop["recording_ids"]
N        = len(NEURONS)           # 61
n2i      = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)

OUTSIDE_CREAMER = {"AIBL", "AIBR", "AWCL", "IL1L", "IL1R"}
creamer_mask = np.array([n not in OUTSIDE_CREAMER for n in NEURONS], dtype=bool)  # (61,) 56 True

# Held-out pairs (authoritative; these 4 ONLY — not all ADEL pairs)
HELD_OUT_PAIRS = frozenset([
    (n2i["ADEL"], n2i["URYVR"]),
    (n2i["ADEL"], n2i["URYDL"]),
    (n2i["ADEL"], n2i["RMEL"]),
    (n2i["ADEL"], n2i["URXL"]),
])

# Class 4 pair indices from Phase 2 (authoritative)
ranked_c4   = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_all, jj_all = np.triu_indices(N, k=1)
ii_c4       = ii_all[ranked_c4]
jj_c4       = jj_all[ranked_c4]
N_C4        = len(ranked_c4)      # 1321

# Observed ΔQ (Phase 2 Stage 2 confirmation matrices)
DQ_obs_cep = np.load(ROOT / "results/phase2/stage2/DQ_cepnem.npy")  # (61,61)

# Training indices: Class 4 pairs excluding the 4 held-out
train_mask  = np.array([
    (ii_c4[k], jj_c4[k]) not in HELD_OUT_PAIRS
    for k in range(N_C4)
], dtype=bool)
train_ii    = ii_c4[train_mask]
train_jj    = jj_c4[train_mask]
DQ_obs_train = DQ_obs_cep[train_ii, train_jj]

# PDF Class 4 pairs (for evaluation metrics; from Phase 2 Stage 4A)
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"

def load_bentley_pdf_pairs() -> set:
    pairs: set = set()
    with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 3: continue
            src, tgt = row[0].strip(), row[1].strip()
            if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
            if "pdf" not in row[2].strip().lower(): continue
            a, b = n2i[src], n2i[tgt]
            pairs.add((min(a, b), max(a, b)))
    return pairs

c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))
bentley_pdf_c4 = load_bentley_pdf_pairs() & c4_set
pdf_c4_array   = np.array(sorted(bentley_pdf_c4))   # (61, 2)

print(f"N_C4={N_C4}  N_train={train_mask.sum()}  N_held_out=4")
print(f"N_PDF_C4={len(bentley_pdf_c4)}")

# =============================================================================
# STAGE 3A.1 — Network construction
# =============================================================================
print("\n" + "="*70)
print("STAGE 3A.1 — Network construction")
print("="*70)

# ── J: directed anatomical connectome ────────────────────────────────────────
# Re-build from source CSVs (directed, not symmetrized)
J_directed = np.zeros((N, N), dtype=float)
for fname in ["aconnectome_white_1986_whole.csv", "aconnectome_witvliet_2020_7.csv"]:
    fpath = DATA_DIR / fname
    if not fpath.exists():
        continue
    with open(fpath) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            parts = row[0].split("\t")
            if len(parts) < 4: continue
            pre, post, typ, nsyn_str = parts
            if pre not in neurons_set or post not in neurons_set: continue
            try:
                nsyn = int(nsyn_str)
            except ValueError:
                continue
            if nsyn >= p0cfg.SYNAPSE_COUNT_THRESHOLD:
                a, b = n2i[pre], n2i[post]
                J_directed[a, b] = max(J_directed[a, b], nsyn)

# Binarize (use binary adjacency as in A_raw)
J = (J_directed > 0).astype(float)
print(f"J directed edges: {int(J.sum())}  (unique undirected pairs covered: {int(((J+J.T)>0).sum())//2})")
print(f"J density: {J.sum()/(N*(N-1)):.3f}")

# ── P: directed Bentley PDF ───────────────────────────────────────────────────
P = np.zeros((N, N), dtype=float)
P_edge_list: list[tuple[str, str]] = []
P_seen: set = set()
with open(DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        key = (a, b)
        if key in P_seen: continue
        P_seen.add(key)
        P[a, b] = 1.0
        P_edge_list.append((src, tgt))

N_P_edges = int(P.sum())
print(f"P directed edges: {N_P_edges}")

# Normalize P by Frobenius norm (scale-free; α absorbs magnitude)
P_norm = P / (np.linalg.norm(P, "fro") + 1e-12)

# ── P_rand ensemble: degree-preserving random permutations of P ──────────────
N_RAND = 1000
print(f"Building {N_RAND} randomized P graphs (degree-preserving permutation)...")

def randomize_directed_graph(adj: np.ndarray, rng: np.random.Generator,
                              n_swaps: int = None) -> np.ndarray:
    """Random edge-swap preserving in-degree and out-degree exactly."""
    rows, cols = np.where(adj > 0)
    edges = list(zip(rows.tolist(), cols.tolist()))
    n_e   = len(edges)
    if n_swaps is None:
        n_swaps = n_e * 10
    adj_r = adj.copy()
    attempts = 0
    for _ in range(n_swaps):
        if n_e < 2: break
        i1, i2 = rng.integers(0, n_e, size=2)
        if i1 == i2: continue
        a, b  = edges[i1]
        c, d  = edges[i2]
        if a == c or b == d or a == d or c == b: continue
        if adj_r[a, d] > 0 or adj_r[c, b] > 0: continue
        # Swap: (a→b, c→d) becomes (a→d, c→b)
        adj_r[a, b] = 0; adj_r[c, d] = 0
        adj_r[a, d] = 1; adj_r[c, b] = 1
        edges[i1] = (a, d); edges[i2] = (c, b)
        attempts += 1
    return adj_r

P_rand_list: list[np.ndarray] = []
for k in range(N_RAND):
    P_rand_list.append(randomize_directed_graph(P, rng))

# Verify degree preservation (spot-check)
check = P_rand_list[0]
assert np.allclose(check.sum(axis=0), P.sum(axis=0)), "In-degree mismatch"
assert np.allclose(check.sum(axis=1), P.sum(axis=1)), "Out-degree mismatch"
print(f"  Degree-preservation verified.")

# Normalize each P_rand
P_rand_norm_list = [pr / (np.linalg.norm(pr, "fro") + 1e-12) for pr in P_rand_list]

# ── Creamer A_C ───────────────────────────────────────────────────────────────
CREAMER_DIR = ROOT / "data/creamer/Creamer_LDS_2026"
CREAMER_AVAILABLE = False
J_creamer = None
creamer_cell_ids = None

try:
    for mod_name in ["mpi4py", "mpi4py.MPI", "mpi4py.util", "mpi4py.util.pkl5"]:
        sys.modules[mod_name] = MagicMock()
    sys.path.insert(0, str(CREAMER_DIR))
    import ssm_classes  # type: ignore
    import pickle as _pkl
    with open(CREAMER_DIR / "models/fully_connected.pkl", "rb") as f:
        cr_model = _pkl.load(f)
    A_C_full   = cr_model.dynamics_weights   # (154, 154)
    cr_ids     = [str(c) for c in cr_model.cell_ids]  # 154 neuron names
    # Restrict to our 61-neuron subgraph
    cr_in_61   = [c for c in cr_ids if c in n2i]
    cr_idx_cr  = [cr_ids.index(c) for c in cr_in_61]   # indices in 154 list
    cr_idx_61  = [n2i[c] for c in cr_in_61]             # indices in 61 list
    n_cr       = len(cr_in_61)
    J_creamer_sub = A_C_full[np.ix_(cr_idx_cr, cr_idx_cr)]  # (n_cr, n_cr)
    # Expand to 61×61 (zeros for neurons not in Creamer)
    J_creamer  = np.zeros((N, N), dtype=float)
    for ki, i61 in enumerate(cr_idx_61):
        for kj, j61 in enumerate(cr_idx_61):
            J_creamer[i61, j61] = J_creamer_sub[ki, kj]
    CREAMER_AVAILABLE = True
    creamer_cell_ids  = cr_in_61
    print(f"Creamer A_C loaded: {n_cr} neurons mapped to 61-subgraph")
except Exception as e:
    print(f"Creamer A_C unavailable: {e}")

# Save network matrices
np.save(OUT_DIR / "phase3a_J_directed.npy",   J)
np.save(OUT_DIR / "phase3a_P_directed.npy",   P)
np.save(OUT_DIR / "phase3a_P_norm.npy",       P_norm)
np.save(OUT_DIR / "phase3a_P_rand.npy",       np.stack(P_rand_list))
np.save(OUT_DIR / "phase3a_P_rand_norm.npy",  np.stack(P_rand_norm_list))
if CREAMER_AVAILABLE:
    np.save(OUT_DIR / "phase3a_J_creamer.npy", J_creamer)
print("Network matrices saved.")

# =============================================================================
# STAGE 3A.2 — Stability analysis
# =============================================================================
print("\n" + "="*70)
print("STAGE 3A.2 — Stability analysis")
print("="*70)

def compute_gamma(J_mat: np.ndarray, margin: float = 0.01) -> float:
    """Minimal diagonal stabilizer γ s.t. max Re(λ(J - γI)) < 0."""
    ev = np.linalg.eigvals(J_mat)
    max_re = float(np.max(np.real(ev)))
    return max(max_re + margin, 0.0)  # γ=0 if already stable

def is_stable(J_mat: np.ndarray) -> bool:
    ev = np.linalg.eigvals(J_mat)
    return bool(np.all(np.real(ev) < 0))

def alpha_boundary(J_base: np.ndarray, P_mat: np.ndarray,
                   direction: str = "pos", tol: float = 1e-3,
                   lo: float = 0.0, hi: float = 200.0) -> float:
    """Binary search for α boundary (positive or negative) where J_base + αP goes unstable."""
    sign = 1.0 if direction == "pos" else -1.0
    if not is_stable(J_base + sign * hi * P_mat):
        # unstable even at hi; binary search between lo and hi
        for _ in range(40):
            mid = (lo + hi) / 2
            if is_stable(J_base + sign * mid * P_mat):
                lo = mid
            else:
                hi = mid
            if hi - lo < tol:
                break
        return sign * lo
    return sign * hi  # still stable at full range → return boundary

# ── M1: J directed ───────────────────────────────────────────────────────────
gamma_J = compute_gamma(J)
J_base  = J - gamma_J * np.eye(N)
assert is_stable(J_base), "J_base not stable after γ correction"
ev_J    = np.real(np.linalg.eigvals(J_base))
print(f"\nJ_base (directed A_raw):")
print(f"  γ = {gamma_J:.4f}")
print(f"  max Re(λ) = {ev_J.max():.4f}  (must be < 0)")

alpha_max_M1 = alpha_boundary(J_base, P_norm, "pos")
alpha_min_M1 = alpha_boundary(J_base, P_norm, "neg")
print(f"  α_max (positive, with P_norm) = {alpha_max_M1:.4f}")
print(f"  α_min (negative, with P_norm) = {alpha_min_M1:.4f}")

# ── M3: Creamer ───────────────────────────────────────────────────────────────
gamma_cr = alpha_max_cr = alpha_min_cr = None
J_base_cr = None
if CREAMER_AVAILABLE:
    gamma_cr   = compute_gamma(J_creamer)
    J_base_cr  = J_creamer - gamma_cr * np.eye(N)
    assert is_stable(J_base_cr), "J_base_cr not stable"
    ev_cr      = np.real(np.linalg.eigvals(J_base_cr))
    alpha_max_cr = alpha_boundary(J_base_cr, P_norm, "pos")
    alpha_min_cr = alpha_boundary(J_base_cr, P_norm, "neg")
    print(f"\nJ_base_creamer:")
    print(f"  γ = {gamma_cr:.4f}")
    print(f"  max Re(λ) = {ev_cr.max():.4f}")
    print(f"  α_max = {alpha_max_cr:.4f}, α_min = {alpha_min_cr:.4f}")

stability_report = {
    "date": "2026-06-03",
    "M1_J_directed": {
        "gamma": float(gamma_J),
        "max_Re_lambda_J_base": float(ev_J.max()),
        "alpha_max_P_norm": float(alpha_max_M1),
        "alpha_min_P_norm": float(alpha_min_M1),
    },
    "M3_J_creamer": {
        "available": CREAMER_AVAILABLE,
        "gamma":         float(gamma_cr) if gamma_cr is not None else None,
        "max_Re_lambda_J_base": float(np.real(np.linalg.eigvals(J_base_cr)).max()) if J_base_cr is not None else None,
        "alpha_max_P_norm": float(alpha_max_cr) if alpha_max_cr is not None else None,
        "alpha_min_P_norm": float(alpha_min_cr) if alpha_min_cr is not None else None,
    },
}
with open(OUT_DIR / "phase3a_stability_report.json", "w") as f:
    json.dump(stability_report, f, indent=2)
print("\nStability report saved.")

# =============================================================================
# STAGE 3A.3 — Forward prediction machinery
# =============================================================================
print("\n" + "="*70)
print("STAGE 3A.3 — Forward prediction machinery")
print("="*70)

def lyapunov_Q(J_eff: np.ndarray, D: np.ndarray | None = None) -> np.ndarray | None:
    """Compute steady-state precision Q from continuous-time LDS.

    Solves: J_eff Σ + Σ J_eff^T = -D  →  Σ  →  Q = Σ^{-1}

    Returns Q (N×N, symmetric) or None if Σ is not PSD.
    """
    if D is None:
        D = np.eye(J_eff.shape[0])
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Sigma = linalg.solve_continuous_lyapunov(J_eff, -D)
        # Symmetrize (numerical noise)
        Sigma = (Sigma + Sigma.T) / 2
        # Check PSD
        ev = np.linalg.eigvalsh(Sigma)
        if ev.min() < -1e-8:
            return None
        Sigma = Sigma + max(0, -ev.min() + 1e-10) * np.eye(N)
        Q = np.linalg.inv(Sigma)
        Q = (Q + Q.T) / 2
        return Q
    except Exception:
        return None

def predict_deltaQ(alpha_r: float, alpha_d: float,
                   J_base_mat: np.ndarray, P_mat: np.ndarray) -> np.ndarray | None:
    """Compute ΔQ_pred = Q_roam - Q_dwell for given (α_r, α_d)."""
    J_r = J_base_mat + alpha_r * P_mat
    J_d = J_base_mat + alpha_d * P_mat
    Q_r = lyapunov_Q(J_r)
    Q_d = lyapunov_Q(J_d)
    if Q_r is None or Q_d is None:
        return None
    return Q_r - Q_d

# Sanity checks
DQ_zero = predict_deltaQ(0.0, 0.0, J_base, P_norm)
assert DQ_zero is not None, "Lyapunov failed at α=0"
assert np.allclose(DQ_zero, 0.0, atol=1e-8), f"ΔQ at α_r=α_d=0 should be 0, got max={np.abs(DQ_zero).max():.2e}"
print("  ΔQ(α_r=0, α_d=0) = 0  ✓")

# Use α within stability region for test (α_max is small, use 50% of range)
alpha_test = float(alpha_min_M1 * 0.5)   # negative direction has large range
DQ_test = predict_deltaQ(0.0, alpha_test, J_base, P_norm)
assert DQ_test is not None, f"Lyapunov failed at (0, {alpha_test:.3f})"
assert np.abs(DQ_test).max() > 1e-6, "ΔQ test should be nonzero"
print(f"  ΔQ(α_r=0, α_d={alpha_test:.2f}): max|ΔQ|={np.abs(DQ_test).max():.4f}  (nonzero ✓)")

# Check sign convention: negative α_d → what direction does ΔQ move for PDF pairs?
pdf_dq_test  = float(DQ_test[pdf_c4_array[:, 0], pdf_c4_array[:, 1]].mean())
nonpdf_idx   = np.array([(not ((min(train_ii[k],train_jj[k]),
                                max(train_ii[k],train_jj[k])) in bentley_pdf_c4))
                          for k in range(len(train_ii))])
npdf_dq_test = float(DQ_test[train_ii[nonpdf_idx], train_jj[nonpdf_idx]].mean()) if nonpdf_idx.any() else 0.0
print(f"  Test: mean ΔQ PDF={pdf_dq_test:.4f}, non-PDF={npdf_dq_test:.4f}")
print("  Forward model verified.")

# =============================================================================
# STAGE 3A.4 — Fitting objective
# =============================================================================
print("\n" + "="*70)
print("STAGE 3A.4 — Fitting objective")
print("="*70)

def spearman_objective(alpha_r: float, alpha_d: float,
                       J_base_mat: np.ndarray, P_mat: np.ndarray,
                       ii: np.ndarray, jj: np.ndarray,
                       dq_obs: np.ndarray) -> float:
    """Spearman rank correlation between |ΔQ_pred| and |ΔQ_obs| on training pairs.

    Returns NaN if stability violated or Lyapunov fails.
    """
    DQ = predict_deltaQ(alpha_r, alpha_d, J_base_mat, P_mat)
    if DQ is None:
        return float("nan")
    dq_pred = np.abs(DQ[ii, jj])
    dq_o    = np.abs(dq_obs)
    rho, _  = stats.spearmanr(dq_pred, dq_o)
    return float(rho) if not np.isnan(rho) else 0.0

# Verify objective = 0 at α=0 for M0 (ΔQ_pred=0, rank correlation undefined → 0)
rho0 = spearman_objective(0.0, 0.0, J_base, P_norm, train_ii, train_jj, DQ_obs_train)
print(f"  ρ(M0, train) = {rho0:.4f}  (expected 0 or NaN)")

# =============================================================================
# STAGE 3A.5 — Fit M0 / M1 / M2 / M3
# =============================================================================
print("\n" + "="*70)
print("STAGE 3A.5 — Model fitting")
print("="*70)

# ── Grid search parameters ───────────────────────────────────────────────────
# The stability range is highly asymmetric: α_min << 0 and α_max is small positive.
# Build a focused grid: dense near zero (where signal likely lives), sparse far negative.
# Two-part grid: fine range [α_min*0.05, α_max*0.9] + coarse range [α_min*0.9, α_min*0.05)
ALPHA_LO_COARSE = float(alpha_min_M1 * 0.9)   # very negative
ALPHA_LO_FINE   = float(alpha_min_M1 * 0.05)   # moderately negative
ALPHA_HI_FIT    = float(alpha_max_M1 * 0.9)    # near positive boundary
GRID_N_FINE     = 41    # 41 points covering fine range
GRID_N_COARSE   = 11    # 11 points covering coarse range
alpha_fine   = np.linspace(ALPHA_LO_FINE,   ALPHA_HI_FIT,    GRID_N_FINE)
alpha_coarse = np.linspace(ALPHA_LO_COARSE, ALPHA_LO_FINE,   GRID_N_COARSE, endpoint=False)
alpha_grid   = np.concatenate([alpha_coarse, alpha_fine])
GRID_N       = len(alpha_grid)
ALPHA_LO_FIT = ALPHA_LO_COARSE
print(f"\nGrid search: α ∈ [{ALPHA_LO_FIT:.2f}, {ALPHA_HI_FIT:.3f}]")
print(f"  fine [{ALPHA_LO_FINE:.2f}, {ALPHA_HI_FIT:.3f}] ({GRID_N_FINE} pts) + coarse [{ALPHA_LO_COARSE:.2f}, {ALPHA_LO_FINE:.2f}] ({GRID_N_COARSE} pts)")
print(f"  Total {GRID_N}×{GRID_N} = {GRID_N**2} grid points")

# ── M1: fit (α_r, α_d) ───────────────────────────────────────────────────────
print("\n[M1] Fitting α_roam, α_dwell ...")
t0 = time.time()

obj_surface = np.full((GRID_N, GRID_N), np.nan)
for i, ar in enumerate(alpha_grid):
    for j, ad in enumerate(alpha_grid):
        obj_surface[i, j] = spearman_objective(
            ar, ad, J_base, P_norm, train_ii, train_jj, DQ_obs_train
        )
    if (i + 1) % 10 == 0:
        print(f"  {i+1}/{GRID_N} rows done  ({time.time()-t0:.1f}s)")

# Best grid point
valid = ~np.isnan(obj_surface)
best_idx = np.nanargmax(obj_surface)
best_i, best_j = np.unravel_index(best_idx, obj_surface.shape)
alpha_r_grid = alpha_grid[best_i]
alpha_d_grid = alpha_grid[best_j]
rho_grid_best = obj_surface[best_i, best_j]
print(f"\n  Grid best: α_r={alpha_r_grid:.4f}, α_d={alpha_d_grid:.4f}, ρ={rho_grid_best:.4f}")

# Nelder-Mead refinement from best grid point
from scipy.optimize import minimize

def neg_obj(params):
    ar, ad = params
    # Enforce strict stability (90% of boundary)
    if ar <= ALPHA_LO_FIT * 1.05 or ar >= ALPHA_HI_FIT * 1.05: return 1.0
    if ad <= ALPHA_LO_FIT * 1.05 or ad >= ALPHA_HI_FIT * 1.05: return 1.0
    v = spearman_objective(ar, ad, J_base, P_norm, train_ii, train_jj, DQ_obs_train)
    return -v if not np.isnan(v) else 1.0

res_M1 = minimize(neg_obj, [alpha_r_grid, alpha_d_grid], method="Nelder-Mead",
                  options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-5})
alpha_r_M1 = float(res_M1.x[0])
alpha_d_M1 = float(res_M1.x[1])
rho_M1     = float(-res_M1.fun)
print(f"  Nelder-Mead: α_r={alpha_r_M1:.4f}, α_d={alpha_d_M1:.4f}, ρ={rho_M1:.4f}")

# Stability margin
dist_r_M1 = min(abs(alpha_r_M1 - ALPHA_HI_FIT), abs(alpha_r_M1 - ALPHA_LO_FIT)) / (ALPHA_HI_FIT - ALPHA_LO_FIT)
dist_d_M1 = min(abs(alpha_d_M1 - ALPHA_HI_FIT), abs(alpha_d_M1 - ALPHA_LO_FIT)) / (ALPHA_HI_FIT - ALPHA_LO_FIT)
print(f"  Distance-to-instability: roam={dist_r_M1:.3f}, dwell={dist_d_M1:.3f}  (>0.1 = safe)")

np.save(OUT_DIR / "phase3a_objective_surface_M1.npy", obj_surface)

# ── M2: randomized P ensemble ─────────────────────────────────────────────────
print(f"\n[M2] Fitting optimal α_d (α_r=0 fixed) on {N_RAND} randomized P graphs ...")
# For each P_rand, fit single α_d (1D search) with α_r fixed at α_r_M1 value
# Use 1D grid over α_d only (faster)
t0 = time.time()
M2_rho_best  = np.full(N_RAND, np.nan)
M2_alpha_best= np.full(N_RAND, np.nan)

alpha_1d = alpha_grid  # same grid as M1

for k, P_rn in enumerate(P_rand_norm_list):
    best_rho_k = -np.inf
    best_a_k   = 0.0
    for ad in alpha_1d:
        rho = spearman_objective(
            alpha_r_M1, ad, J_base, P_rn, train_ii, train_jj, DQ_obs_train
        )
        if not np.isnan(rho) and rho > best_rho_k:
            best_rho_k = rho
            best_a_k   = ad
    M2_rho_best[k]   = best_rho_k
    M2_alpha_best[k] = best_a_k
    if (k + 1) % 100 == 0:
        print(f"  {k+1}/{N_RAND}  ({time.time()-t0:.1f}s)  running median ρ={np.nanmedian(M2_rho_best[:k+1]):.4f}")

M2_median = float(np.nanmedian(M2_rho_best))
M2_p95    = float(np.nanpercentile(M2_rho_best, 95))
M2_p99    = float(np.nanpercentile(M2_rho_best, 99))
print(f"\n  M2 null: median ρ={M2_median:.4f}, p95={M2_p95:.4f}, p99={M2_p99:.4f}")
print(f"  M1 ρ={rho_M1:.4f} vs M2 p95={M2_p95:.4f}  (margin={rho_M1-M2_p95:+.4f})")

np.save(OUT_DIR / "phase3a_M2_rho_distribution.npy", M2_rho_best)

# ── M3: Creamer ───────────────────────────────────────────────────────────────
rho_M3 = alpha_r_M3 = alpha_d_M3 = None
if CREAMER_AVAILABLE and J_base_cr is not None:
    print("\n[M3] Fitting α_r, α_d with Creamer J_base ...")
    a_lo_cr_c = float(alpha_min_cr * 0.9)
    a_lo_cr_f = float(alpha_min_cr * 0.05)
    a_hi_cr_f = float(alpha_max_cr * 0.9)
    ag_cr     = np.concatenate([
        np.linspace(a_lo_cr_c, a_lo_cr_f, 11, endpoint=False),
        np.linspace(a_lo_cr_f, a_hi_cr_f, 41),
    ])
    GN_cr     = len(ag_cr)
    obj_M3_surf = np.full((GN_cr, GN_cr), np.nan)
    for i, ar in enumerate(ag_cr):
        for j, ad in enumerate(ag_cr):
            obj_M3_surf[i, j] = spearman_objective(
                ar, ad, J_base_cr, P_norm, train_ii, train_jj, DQ_obs_train
            )
    best_m3 = np.nanargmax(obj_M3_surf)
    bi3, bj3 = np.unravel_index(best_m3, obj_M3_surf.shape)
    ar0_cr, ad0_cr = ag_cr[bi3], ag_cr[bj3]

    def neg_obj_cr(params):
        ar, ad = params
        if ar <= a_lo_cr_c * 1.05 or ar >= a_hi_cr_f * 1.05: return 1.0
        if ad <= a_lo_cr_c * 1.05 or ad >= a_hi_cr_f * 1.05: return 1.0
        v = spearman_objective(ar, ad, J_base_cr, P_norm, train_ii, train_jj, DQ_obs_train)
        return -v if not np.isnan(v) else 1.0

    res_M3 = minimize(neg_obj_cr, [ar0_cr, ad0_cr], method="Nelder-Mead",
                      options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-5})
    alpha_r_M3 = float(res_M3.x[0])
    alpha_d_M3 = float(res_M3.x[1])
    rho_M3     = float(-res_M3.fun)
    print(f"  M3: α_r={alpha_r_M3:.4f}, α_d={alpha_d_M3:.4f}, ρ={rho_M3:.4f}")
else:
    print("\n[M3] Creamer unavailable — skipped.")

# ── M0: anatomy only ─────────────────────────────────────────────────────────
# ΔQ_M0 = 0 → Spearman = 0 by construction (tie at zero ranks)
rho_M0 = 0.0
print(f"\n[M0] Anatomy only: ρ = {rho_M0:.4f} (ΔQ_pred ≡ 0)")

# =============================================================================
# EVALUATION METRICS on training PDF pairs
# =============================================================================
print("\n" + "="*70)
print("TRAINING-SET PDF EVALUATION (not held-out)")
print("="*70)

pdf_train_mask = np.array([
    (min(ii_c4[k], jj_c4[k]), max(ii_c4[k], jj_c4[k])) in bentley_pdf_c4
    and (ii_c4[k], jj_c4[k]) not in HELD_OUT_PAIRS
    for k in range(N_C4)
], dtype=bool)
pdf_train_ii = ii_c4[pdf_train_mask]
pdf_train_jj = jj_c4[pdf_train_mask]
N_pdf_train  = pdf_train_mask.sum()

def auroc_pdf_vs_nonpdf(dq_pred_flat: np.ndarray) -> float:
    """AUROC: do PDF training pairs rank higher than non-PDF training pairs?"""
    pdf_scores    = np.abs(dq_pred_flat[pdf_train_mask])
    nonpdf_scores = np.abs(dq_pred_flat[~pdf_train_mask])
    if len(pdf_scores) == 0 or len(nonpdf_scores) == 0:
        return 0.5
    # Mann-Whitney U statistic = AUROC
    n1, n2 = len(pdf_scores), len(nonpdf_scores)
    U, _ = stats.mannwhitneyu(pdf_scores, nonpdf_scores, alternative="greater")
    return float(U / (n1 * n2))

# ΔQ_pred under M1 at fitted α
DQ_M1 = predict_deltaQ(alpha_r_M1, alpha_d_M1, J_base, P_norm)
assert DQ_M1 is not None
dq_M1_flat = np.abs(DQ_M1[ii_c4, jj_c4])

# Spearman on ALL training pairs (including non-PDF)
rho_M1_all_check = spearman_objective(alpha_r_M1, alpha_d_M1, J_base, P_norm,
                                       train_ii, train_jj, DQ_obs_train)

# AUROC on training PDF pairs
auroc_M1_train = auroc_pdf_vs_nonpdf(dq_M1_flat)

# M0: all zeros → AUROC = 0.5
auroc_M0_train = 0.5

# M2 best: use median P_rand best α
best_m2_idx = int(np.nanargmax(M2_rho_best))
DQ_M2_best  = predict_deltaQ(alpha_r_M1, float(M2_alpha_best[best_m2_idx]),
                              J_base, P_rand_norm_list[best_m2_idx])
auroc_M2_train = auroc_pdf_vs_nonpdf(np.abs(DQ_M2_best[ii_c4, jj_c4])) if DQ_M2_best is not None else 0.5

print(f"\nTraining-set metrics (N_pdf_train={N_pdf_train}, N_nonpdf_train={train_mask.sum()-N_pdf_train}):")
print(f"  M0: ρ={rho_M0:.4f}  AUROC(PDF)={auroc_M0_train:.4f}")
print(f"  M1: ρ={rho_M1:.4f}  AUROC(PDF)={auroc_M1_train:.4f}")
print(f"  M2: ρ=median {M2_median:.4f} / best {M2_rho_best[best_m2_idx]:.4f}  AUROC(best)={auroc_M2_train:.4f}")

if CREAMER_AVAILABLE and rho_M3 is not None:
    DQ_M3 = predict_deltaQ(alpha_r_M3, alpha_d_M3, J_base_cr, P_norm)
    auroc_M3_train = auroc_pdf_vs_nonpdf(np.abs(DQ_M3[ii_c4, jj_c4])) if DQ_M3 is not None else 0.5
    print(f"  M3: ρ={rho_M3:.4f}  AUROC(PDF)={auroc_M3_train:.4f}")
else:
    auroc_M3_train = None

# Pre-specified success criteria
print("\n--- Pre-specified success criteria (Section 6.3 of design package) ---")
crit1_pass = (auroc_M1_train - auroc_M0_train) > 0.05
crit2_pass = (auroc_M1_train - auroc_M2_train) > 0.03
crit3_pass = min(dist_r_M1, dist_d_M1) > 0.1
print(f"  Criterion 1: AUROC(M1) > AUROC(M0) + 0.05 : {auroc_M1_train:.4f} > {auroc_M0_train+0.05:.4f} → {'PASS' if crit1_pass else 'FAIL'}")
print(f"  Criterion 2: AUROC(M1) > AUROC(M2_best) + 0.03: {auroc_M1_train:.4f} > {auroc_M2_train+0.03:.4f} → {'PASS' if crit2_pass else 'FAIL'}")
print(f"  Criterion 3: stability margin > 0.10: min={min(dist_r_M1,dist_d_M1):.3f} → {'PASS' if crit3_pass else 'FAIL'}")

# α sign interpretation
delta_alpha = alpha_d_M1 - alpha_r_M1
print(f"\nFitted α values:")
print(f"  α_roam  = {alpha_r_M1:.4f}")
print(f"  α_dwell = {alpha_d_M1:.4f}")
print(f"  Δα (dwell − roam) = {delta_alpha:+.4f}")

# =============================================================================
# SAVE ALL OUTPUTS
# =============================================================================
print("\n" + "="*70)
print("SAVING OUTPUTS")
print("="*70)

fit_params = {
    "date": "2026-06-03",
    "authorization": "Phase 3A 2026-06-03",
    "J_type": "directed White+Witvliet A_raw (binarized)",
    "P_type": "directed Bentley PDF (pdf-1/pdf-2 → pdfr-1)",
    "P_normalization": "Frobenius",
    "alpha_grid_range": [float(ALPHA_LO_FIT), float(ALPHA_HI_FIT)],
    "grid_n": GRID_N,
    "M0": {"alpha_roam": 0.0, "alpha_dwell": 0.0, "rho_train": rho_M0, "auroc_pdf_train": auroc_M0_train},
    "M1": {
        "alpha_roam":  alpha_r_M1, "alpha_dwell": alpha_d_M1,
        "delta_alpha": delta_alpha,
        "rho_train":   rho_M1,
        "auroc_pdf_train": auroc_M1_train,
        "dist_instability_roam":  dist_r_M1,
        "dist_instability_dwell": dist_d_M1,
        "grid_best_rho": rho_grid_best,
    },
    "M2": {
        "n_rand": N_RAND,
        "median_rho": M2_median,
        "p95_rho":    M2_p95,
        "p99_rho":    M2_p99,
        "auroc_pdf_best": auroc_M2_train,
    },
    "M3": {
        "available": CREAMER_AVAILABLE,
        "J_type": "Creamer LDS dynamics_weights (154→56 subspace)" if CREAMER_AVAILABLE else "N/A",
        "alpha_roam":  alpha_r_M3,
        "alpha_dwell": alpha_d_M3,
        "rho_train":   rho_M3,
        "auroc_pdf_train": auroc_M3_train,
    },
    "success_criteria": {
        "criterion_1_auroc_M1_vs_M0": {"result": crit1_pass, "M1": auroc_M1_train, "M0": auroc_M0_train, "threshold": 0.05},
        "criterion_2_auroc_M1_vs_M2": {"result": crit2_pass, "M1": auroc_M1_train, "M2_best": auroc_M2_train, "threshold": 0.03},
        "criterion_3_stability_margin": {"result": crit3_pass, "margin": min(dist_r_M1, dist_d_M1), "threshold": 0.1},
    },
    "held_out_pairs": ["ADEL-URYVR", "ADEL-URYDL", "ADEL-RMEL", "ADEL-URXL"],
    "held_out_evaluated": False,
}

with open(OUT_DIR / "phase3a_fit_parameters.json", "w") as f:
    json.dump(fit_params, f, indent=2)

summary = {
    "date": "2026-06-03",
    "stage": "3A",
    "N": N, "N_C4": N_C4, "N_train": int(train_mask.sum()),
    "N_held_out": 4,
    "N_pdf_c4": len(bentley_pdf_c4),
    "J_directed_edges": int(J.sum()),
    "P_directed_edges": N_P_edges,
    "gamma_J": float(gamma_J),
    "alpha_max_M1": float(alpha_max_M1),
    "alpha_min_M1": float(alpha_min_M1),
    "M0_rho": rho_M0,
    "M1_alpha_roam":  alpha_r_M1, "M1_alpha_dwell": alpha_d_M1,
    "M1_rho_train":   rho_M1,
    "M1_auroc_pdf_train": auroc_M1_train,
    "M2_median_rho":  M2_median, "M2_p95_rho": M2_p95,
    "M1_vs_M2_margin": rho_M1 - M2_median,
    "M1_vs_M2_vs_p95": rho_M1 - M2_p95,
    "M3_available": CREAMER_AVAILABLE, "M3_rho": rho_M3,
    "all_criteria_pass": crit1_pass and crit2_pass and crit3_pass,
    "criterion_1_pass": crit1_pass,
    "criterion_2_pass": crit2_pass,
    "criterion_3_pass": crit3_pass,
    "held_out_evaluated": False,
    "stop_condition": "STOP — held-out evaluation requires separate authorization",
}

with open(OUT_DIR / "phase3a_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("  phase3a_fit_parameters.json  ✓")
print("  phase3a_summary.json         ✓")
print("  phase3a_objective_surface_M1.npy  ✓")
print("  phase3a_M2_rho_distribution.npy   ✓")
print("  phase3a_J_directed.npy            ✓")
print("  phase3a_P_directed.npy            ✓")

print(f"\nElapsed: {time.time()-t0:.1f}s total from grid start")
print("\n>>> STOP CONDITION REACHED <<<")
print("Phase 3A complete. Awaiting human review before held-out evaluation.")
