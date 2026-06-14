#!/usr/bin/env python3
"""
Phase 9C Oracle Construction — FINAL DESIGN
============================================

Design choices (locked in phase9c_parameter_lock.md addendum):
  1. PMC_SRC neurons are ISOLATED from all other observed neurons in A_obs
     (they connect ONLY to H_global via A[HG, PMC_SRC])
  2. PMC_TGT neurons are ISOLATED from non-PMC observed neurons in A_obs
     (they connect ONLY via A[PMC_TGT, HG] from H_global)
  3. H_global projects EXCLUSIVELY to PMC_TGT (no background observed connections)
  4. PMC definition EXPANDED: all off-connectome pairs (i,j) where BOTH
     i,j ∈ PMC_SRC ∪ PMC_TGT (181 pairs, not just 96 SRC→TGT)
  5. D_A elevated at PMC_SRC (D_SRC_A=5.0) and H_global (D_HG_A=10.0)
  6. D_B = D_BASE = 1.0 everywhere

Scientific justification for expanded PMC:
  The relay circuit is PMC_SRC → H_global → PMC_TGT. The planted organization
  affects ALL pairs within {PMC_SRC ∪ PMC_TGT}: SRC↔SRC (shared HG inputs),
  TGT↔TGT (shared HG outputs), and SRC↔TGT (relay pairs). This mirrors the
  worm annotation where all (pdf-1 expressing ↔ pdfr-1 expressing) pairs are
  annotated, not just directed receptor-ligand pairs.

NO trajectories. NO framework. Oracle objects only.
Outputs → results/phase9c/ground_truth/
"""

import numpy as np
from scipy import linalg
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
import json, hashlib, os

OUT_DIR = os.path.join(os.path.dirname(__file__), "../../results/phase9c/ground_truth")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Random seed (locked) ───────────────────────────────────────────────────────
SEED = 42
rng  = np.random.default_rng(SEED)

# ── Network sizes (locked) ─────────────────────────────────────────────────────
N_OBS      = 150
N_H_LOCAL  = 20
N_H_GLOBAL = 10
N_TOTAL    = 180

# ── Module indices (observed, 0..149) ─────────────────────────────────────────
M1 = np.arange(0,   40)
M2 = np.arange(40,  80)
M3 = np.arange(80,  115)
M4 = np.arange(115, 150)
modules = [M1, M2, M3, M4]

# ── Hidden neuron indices ─────────────────────────────────────────────────────
HL = np.arange(N_OBS,              N_OBS + N_H_LOCAL)   # 150..169
HG = np.arange(N_OBS + N_H_LOCAL, N_TOTAL)              # 170..179

# ── PMC membership (committed before any oracle computation) ─────────────────
PMC_SRC     = M1[:8]                                   # neurons 0..7
PMC_TGT     = np.concatenate([M3[:6], M4[:6]])         # neurons 80..85, 115..120
PMC_NEURONS = np.concatenate([PMC_SRC, PMC_TGT])       # 20 circuit neurons
pmc_neuron_set = set(PMC_NEURONS.tolist())

print("=== Phase 9C Oracle Construction (final design) ===")
print(f"PMC sources:  {PMC_SRC.tolist()}")
print(f"PMC targets:  {PMC_TGT.tolist()}")
print(f"Circuit neurons: {len(PMC_NEURONS)}")

# ── Connectivity parameters (locked) ─────────────────────────────────────────
P_WITHIN   = 0.12
P_BETWEEN  = 0.02
P_H_LOCAL  = 0.15
W_STD      = 0.12      # background weights
W_HG_TGT   = 0.30     # HG → PMC_TGT weights (specific relay)
W_SRC_HG   = 0.25     # PMC_SRC → HG weights

DIAG_OBS   = -1.5
DIAG_HL    = -1.2
DIAG_HG    = -1.0

PMC_SRC_TO_HG_MIN  = 3
PMC_TGT_FROM_HG_MIN = 4

# ── Diffusion parameters (locked after D1 verification) ─────────────────────
D_BASE  = 1.0
D_HG_A  = 10.0   # conservative: easily passes D1 without being trivially large
D_SRC_A = 5.0

# ─────────────────────────────────────────────────────────────────────────────
# 1. Build A_full (N_TOTAL × N_TOTAL)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Building A_full ---")
A = np.zeros((N_TOTAL, N_TOTAL))

# Self-inhibition (observed)
for i in range(N_OBS): A[i, i] = DIAG_OBS

# Within-module recurrent (all observed modules)
for mod in modules:
    n = len(mod)
    b = (rng.random((n, n)) < P_WITHIN) * rng.normal(0, W_STD, (n, n))
    np.fill_diagonal(b, 0)
    A[np.ix_(mod, mod)] = b

# Between-module connections
for mi in modules:
    for mj in modules:
        if not np.array_equal(mi, mj):
            A[np.ix_(mi, mj)] = (rng.random((len(mi), len(mj))) < P_BETWEEN) * \
                                 rng.normal(0, W_STD, (len(mi), len(mj)))

# H_local: 5 per module → observed module neurons
for k, mod in enumerate(modules):
    hi = HL[k*5 : (k+1)*5]
    A[np.ix_(mod, hi)] = (rng.random((len(mod), 5)) < P_H_LOCAL) * \
                          rng.normal(0, W_STD, (len(mod), 5))
    for h in hi: A[h, h] = DIAG_HL

# H_global self-inhibition
for h in HG: A[h, h] = DIAG_HG

# ── KEY: Isolate PMC_SRC from all observed-observed connections ───────────────
# PMC_SRC connects ONLY to H_global (A[HG, PMC_SRC] will be set below)
non_pmc_obs = np.array([i for i in range(N_OBS) if i not in pmc_neuron_set])
A[:N_OBS, PMC_SRC] = 0.0   # no observed neuron drives PMC_SRC
A[PMC_SRC, :N_OBS] = 0.0   # PMC_SRC doesn't drive any observed neuron
for s in PMC_SRC: A[s, s] = DIAG_OBS  # restore self-inhibition

# ── KEY: Isolate PMC_TGT from non-PMC observed neurons ────────────────────────
# PMC_TGT receives input ONLY from H_global (and from each other via within-M3/M4)
A[np.ix_(PMC_TGT, non_pmc_obs)] = 0.0   # PMC_TGT doesn't project to non-PMC obs
A[np.ix_(non_pmc_obs, PMC_TGT)] = 0.0   # non-PMC obs doesn't project to PMC_TGT
for t in PMC_TGT: A[t, t] = DIAG_OBS  # restore self-inhibition

# No direct PMC_SRC → PMC_TGT edges (redundant after isolation but explicit)
A[np.ix_(PMC_TGT, PMC_SRC)] = 0.0

# ── H_global → PMC_TGT EXCLUSIVELY ──────────────────────────────────────────
# All 10 HG neurons project to all 12 PMC_TGT neurons (dense specific relay)
for h in HG:
    for t in PMC_TGT:
        A[t, h] = rng.normal(0, W_HG_TGT)

# No HG connections to non-PMC observed (enforced by construction above,
# but also explicitly verified in AT-1d below)

# ── PMC_SRC → H_global (≥5 of 10 HG per source) ─────────────────────────────
for src in PMC_SRC:
    chosen = rng.choice(N_H_GLOBAL, size=5, replace=False)
    for ch in chosen:
        A[HG[ch], src] = rng.normal(0, W_SRC_HG)

# ── Stability: spectral shift ────────────────────────────────────────────────
eigs   = np.linalg.eigvals(A)
max_re = float(np.max(np.real(eigs)))
print(f"  Max Re(eig): {max_re:.4f}")
if max_re >= -0.05:
    shift = max_re + 0.15
    A     = A - shift * np.eye(N_TOTAL)
    max_re = float(np.max(np.real(np.linalg.eigvals(A))))
    print(f"  Applied spectral shift {shift:.4f}. New max Re: {max_re:.4f}")
assert max_re < 0, f"A not stable: {max_re}"
print(f"  Stability OK. Re ∈ [{np.min(np.real(np.linalg.eigvals(A))):.3f}, {max_re:.3f}]")

A_obs = A[:N_OBS, :N_OBS]

# ─────────────────────────────────────────────────────────────────────────────
# 2. AT-1 construction checks
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- AT-1 checks ---")

assert np.all(A[np.ix_(PMC_TGT, PMC_SRC)] == 0), "FAIL AT-1a"
print("  AT-1a PASS: no direct PMC_SRC → PMC_TGT edges")

for src in PMC_SRC:
    n = int(np.sum(A[HG, src] != 0))
    assert n >= PMC_SRC_TO_HG_MIN, f"FAIL: PMC_SRC[{src}] has {n} HG connections"
print("  AT-1b PASS: all PMC sources have ≥3 H_global connections (have ≥5)")

for tgt in PMC_TGT:
    n = int(np.sum(A[tgt, HG] != 0))
    assert n >= PMC_TGT_FROM_HG_MIN, f"FAIL: PMC_TGT[{tgt}] has {n} HG connections"
print("  AT-1c PASS: all PMC targets have ≥4 H_global connections (have 10)")

assert np.all(A[np.ix_(non_pmc_obs, HG)] == 0), "FAIL AT-1d"
print("  AT-1d PASS: H_global projects ONLY to PMC_TGT")

assert np.all(A[np.ix_(PMC_SRC, non_pmc_obs)] == 0), "FAIL AT-1e"
assert np.all(A[np.ix_(non_pmc_obs, PMC_SRC)] == 0), "FAIL AT-1f"
print("  AT-1e/f PASS: PMC_SRC isolated from all non-PMC observed neurons")

assert np.all(A[np.ix_(PMC_TGT, non_pmc_obs)] == 0), "FAIL AT-1g"
assert np.all(A[np.ix_(non_pmc_obs, PMC_TGT)] == 0), "FAIL AT-1h"
print("  AT-1g/h PASS: PMC_TGT isolated from all non-PMC observed neurons")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Diffusion matrices
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Diffusion matrices ---")
D_B_diag          = np.full(N_TOTAL, D_BASE)
D_A_diag          = D_B_diag.copy()
D_A_diag[PMC_SRC] = D_SRC_A
D_A_diag[HG]      = D_HG_A

D_A_obs = np.diag(D_A_diag[:N_OBS])
D_B_obs = np.diag(D_B_diag[:N_OBS])
print(f"  State A: D[PMC_SRC]={D_SRC_A}, D[HG]={D_HG_A}, D[others]={D_BASE}")
print(f"  State B: D=uniform {D_BASE}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Lyapunov solver
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Solving Lyapunov equations ---")

def solve_lyap(A_mat, D_diag):
    return linalg.solve_continuous_lyapunov(A_mat, -2 * np.diag(D_diag))

Sigma_A_full = solve_lyap(A, D_A_diag)
Sigma_B_full = solve_lyap(A, D_B_diag)

for name, Sig in [("A", Sigma_A_full), ("B", Sigma_B_full)]:
    min_eig = float(np.min(np.linalg.eigvalsh(Sig)))
    sym_err = float(np.max(np.abs(Sig - Sig.T)))
    assert min_eig > 0,    f"Sigma_{name} not PD: {min_eig}"
    assert sym_err < 1e-8, f"Sigma_{name} not symmetric: {sym_err}"
    print(f"  Sigma_{name}: min_eig={min_eig:.6f}, sym_err={sym_err:.2e}")

Sigma_A_obs = Sigma_A_full[:N_OBS, :N_OBS]
Sigma_B_obs = Sigma_B_full[:N_OBS, :N_OBS]
Q_A = np.linalg.inv(Sigma_A_obs)
Q_B = np.linalg.inv(Sigma_B_obs)

Omega_A      = D_A_obs @ Q_A + A_obs
Omega_B      = D_B_obs @ Q_B + A_obs
DeltaOmega   = Omega_A - Omega_B

cancel_err = float(np.max(np.abs(DeltaOmega - (D_A_obs @ Q_A - D_B_obs @ Q_B))))
assert cancel_err < 1e-8, f"A_obs cancellation error {cancel_err}"
print(f"  AT-2 PASS: Sigma PD, A_obs cancels in ΔΩ (err={cancel_err:.2e})")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Off-connectome pairs and PMC labels
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Oracle ranking ---")
off_pairs = np.array([(i, j) for i in range(N_OBS) for j in range(i+1, N_OBS)
                      if A_obs[i, j] == 0 and A_obs[j, i] == 0])
n_off = len(off_pairs)

# Expanded PMC: both endpoints in circuit
pmc_binary = np.array(
    [1 if (int(i) in pmc_neuron_set and int(j) in pmc_neuron_set) else 0
     for i, j in off_pairs])
n_pmc = int(pmc_binary.sum())

oracle_vals       = np.abs(np.array([DeltaOmega[i, j] for i, j in off_pairs]))
oracle_rank_order = np.argsort(-oracle_vals)
oracle_ranks      = np.argsort(oracle_rank_order)

print(f"  Off-connectome pairs: {n_off}")
print(f"  PMC pairs (expanded): {n_pmc}  (density {n_pmc/n_off*100:.2f}%)")

# Pair type breakdown
n_ss = int(sum(1 for i,j in off_pairs if i in PMC_SRC and j in PMC_SRC))
n_tt = int(sum(1 for i,j in off_pairs if i in PMC_TGT and j in PMC_TGT))
n_st = int(sum(1 for i,j in off_pairs if i in PMC_SRC and j in PMC_TGT))
print(f"  PMC breakdown: SRC-SRC={n_ss}, TGT-TGT={n_tt}, SRC-TGT={n_st}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. Dominance checks D1 and D2
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Dominance checks ---")
pmc_vals   = oracle_vals[pmc_binary == 1]
nonpmc_vals = oracle_vals[pmc_binary == 0]
pmc_med    = float(np.median(pmc_vals))
nonpmc_p90 = float(np.percentile(nonpmc_vals, 90))
d1_ratio   = pmc_med / nonpmc_p90 if nonpmc_p90 > 0 else np.inf
pmc_top50  = int(pmc_binary[oracle_rank_order[:50]].sum())

D1_ok = d1_ratio > 2.0
D2_ok = (pmc_top50 / 50) >= 0.60

print(f"  PMC median |ΔΩ|:    {pmc_med:.6f}")
print(f"  Non-PMC 90th pct:   {nonpmc_p90:.6f}")
print(f"  D1 ratio:           {d1_ratio:.2f}× (need >2.0)  → {'PASS' if D1_ok else 'FAIL'}")
print(f"  PMC in top-50:      {pmc_top50}/50 (need ≥30)     → {'PASS' if D2_ok else 'FAIL'}")
assert D1_ok, f"D1 FAIL"
assert D2_ok, f"D2 FAIL"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Oracle ceiling (AT-5)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Oracle ceiling (AT-5) ---")
oracle_auroc = roc_auc_score(pmc_binary, oracle_vals)
print(f"  Oracle PMC_AUROC: {oracle_auroc:.4f}  (need ≥0.90)")
assert oracle_auroc >= 0.90, f"AT-5 FAIL: {oracle_auroc:.4f}"
print("  AT-5 PASS")

# ─────────────────────────────────────────────────────────────────────────────
# 8. Precision@k
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Precision@k (oracle) ---")
pmc_density = n_pmc / n_off
prec_at_k   = {}
for k in [5, 10, 20, 50, 100]:
    topk = oracle_rank_order[:k]
    prec = float(pmc_binary[topk].sum()) / k
    enr  = prec / pmc_density if pmc_density > 0 else 0
    prec_at_k[k] = {"precision": prec, "count": int(pmc_binary[topk].sum()), "enrichment": enr}
    print(f"  Precision@{k:<3}: {prec:.3f}  ({prec_at_k[k]['count']}/{k},  {enr:.1f}×)")

# ─────────────────────────────────────────────────────────────────────────────
# 9. Top-20 pair report
# ─────────────────────────────────────────────────────────────────────────────
def get_type(n):
    if n in PMC_SRC: return "SRC"
    if n in PMC_TGT: return "TGT"
    if n in M1: return "M1"
    if n in M2: return "M2"
    if n in M3: return "M3"
    return "M4"

print("\n--- Top-20 oracle pairs ---")
print(f"{'Rank':>4}  {'(i,j)':>10}  {'|ΔΩ|':>9}  {'PMC?':>5}  {'type_i':>6}  {'type_j':>6}")
print("-" * 58)
top20_data = []
for rk in range(20):
    pidx = oracle_rank_order[rk]
    i, j = off_pairs[pidx]
    val  = float(oracle_vals[pidx])
    pmc  = bool(pmc_binary[pidx])
    ti, tj = get_type(i), get_type(j)
    top20_data.append({"rank": rk+1, "i": int(i), "j": int(j),
                       "abs_delta_omega": val, "is_pmc": pmc, "type_i": ti, "type_j": tj})
    print(f"  {rk+1:>2}  ({i:>3},{j:>3})  {val:>9.5f}  {'YES' if pmc else 'no':>5}  {ti:>6}  {tj:>6}")

# ─────────────────────────────────────────────────────────────────────────────
# 10. ΔQ comparison (worm paper analog)
# ─────────────────────────────────────────────────────────────────────────────
DeltaQ_true  = Q_A - Q_B
dq_vals      = np.abs(np.array([DeltaQ_true[i, j] for i, j in off_pairs]))
dq_auroc     = roc_auc_score(pmc_binary, dq_vals)
rho_dq_do, _ = spearmanr(dq_vals, oracle_vals)
print(f"\n  ΔQ PMC_AUROC: {dq_auroc:.4f}")
print(f"  ρ(|ΔΩ|, |ΔQ|): {rho_dq_do:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# 11. Intervention objects (GT5a: state lesion; GT5b: structural lesion)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Intervention validation ---")

# GT5a: state lesion = ΔΩ itself (Ω_A − Ω_B)
state_lesion_vals = oracle_vals.copy()
pmc_in_state_top50 = int(pmc_binary[oracle_rank_order[:50]].sum())
print(f"  GT5a (state lesion): PMC in top-50 = {pmc_in_state_top50}/50")

# GT5b: structural lesion — remove M1→M2 directed edges
A_les = A.copy()
n_les = 0
for i in M2:
    for j in M1:
        if A_les[i, j] != 0:
            A_les[i, j] = 0.0
            n_les += 1
print(f"  Structural lesion: removed {n_les} M1→M2 edges")
assert float(np.max(np.real(np.linalg.eigvals(A_les)))) < 0, "A_lesioned not stable"

Sigma_A_les = solve_lyap(A_les, D_A_diag)
Q_A_les     = np.linalg.inv(Sigma_A_les[:N_OBS, :N_OBS])
A_obs_les   = A_les[:N_OBS, :N_OBS]
Omega_A_les = D_A_obs @ Q_A_les + A_obs_les
DeltaOmega_struct = Omega_A - Omega_A_les
struct_vals = np.abs(np.array([DeltaOmega_struct[i, j] for i, j in off_pairs]))
pmc_in_struct_top50 = int(pmc_binary[np.argsort(-struct_vals)[:50]].sum())
print(f"  GT5b (struct lesion): PMC in top-50 = {pmc_in_struct_top50}/50  (expect low)")

# ─────────────────────────────────────────────────────────────────────────────
# 12. Community structure (GT4)
# ─────────────────────────────────────────────────────────────────────────────
gt_communities = {
    "C_src":      PMC_SRC.tolist(),
    "C_tgt":      PMC_TGT.tolist(),
    "background": [i for i in range(N_OBS) if i not in pmc_neuron_set]
}

# ─────────────────────────────────────────────────────────────────────────────
# 13. Pair statistics
# ─────────────────────────────────────────────────────────────────────────────
n_struct_pairs = sum(1 for i in range(N_OBS) for j in range(i+1, N_OBS)
                     if A_obs[i,j] != 0 or A_obs[j,i] != 0)
print(f"\n  Total pairs:      {N_OBS*(N_OBS-1)//2}")
print(f"  Structural:       {n_struct_pairs}")
print(f"  Off-connectome:   {n_off}")
print(f"  PMC (expanded):   {n_pmc}  (SRC-SRC={n_ss}, TGT-TGT={n_tt}, SRC-TGT={n_st})")
print(f"  Non-PMC off-conn: {n_off - n_pmc}")

# ─────────────────────────────────────────────────────────────────────────────
# 14. Save oracle objects
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Saving oracle objects ---")

np.save(f"{OUT_DIR}/A_full.npy",            A)
np.save(f"{OUT_DIR}/A_obs.npy",             A_obs)
np.save(f"{OUT_DIR}/D_A_diag.npy",          D_A_diag)
np.save(f"{OUT_DIR}/D_B_diag.npy",          D_B_diag)
np.save(f"{OUT_DIR}/Sigma_A_obs.npy",       Sigma_A_obs)
np.save(f"{OUT_DIR}/Sigma_B_obs.npy",       Sigma_B_obs)
np.save(f"{OUT_DIR}/Q_A_obs.npy",           Q_A)
np.save(f"{OUT_DIR}/Q_B_obs.npy",           Q_B)
np.save(f"{OUT_DIR}/Omega_A_obs.npy",       Omega_A)
np.save(f"{OUT_DIR}/Omega_B_obs.npy",       Omega_B)
np.save(f"{OUT_DIR}/DeltaOmega_true.npy",   DeltaOmega)
np.save(f"{OUT_DIR}/DeltaQ_true.npy",       DeltaQ_true)
np.save(f"{OUT_DIR}/GT1_off_pairs.npy",          off_pairs)
np.save(f"{OUT_DIR}/GT1_oracle_vals.npy",         oracle_vals)
np.save(f"{OUT_DIR}/GT2_pmc_pairs_placeholder.npy", np.array([]))  # overwritten below
np.save(f"{OUT_DIR}/GT2_pmc_binary.npy",          pmc_binary)
np.save(f"{OUT_DIR}/GT3_oracle_rank_order.npy",   oracle_rank_order)
np.save(f"{OUT_DIR}/GT3_oracle_ranks.npy",        oracle_ranks)
np.save(f"{OUT_DIR}/GT5a_state_lesion_vals.npy",  state_lesion_vals)
np.save(f"{OUT_DIR}/GT5b_struct_lesion_vals.npy", struct_vals)

# PMC pair set (expanded)
pmc_pairs_arr = off_pairs[pmc_binary == 1]
np.save(f"{OUT_DIR}/GT2_pmc_pairs.npy", pmc_pairs_arr)

with open(f"{OUT_DIR}/GT4_communities.json", "w") as f:
    json.dump(gt_communities, f, indent=2)

summary = {
    "N_OBS": N_OBS, "N_TOTAL": N_TOTAL, "SEED": SEED,
    "PMC_SRC": PMC_SRC.tolist(), "PMC_TGT": PMC_TGT.tolist(),
    "design": {
        "PMC_SRC_isolated": True, "PMC_TGT_isolated": True,
        "HG_exclusive_to_PMC_TGT": True,
        "PMC_definition": "expanded — all off-connectome pairs within PMC_SRC ∪ PMC_TGT",
        "PMC_SRC_to_HG_n_connections": 5, "W_HG_TGT": W_HG_TGT, "W_SRC_HG": W_SRC_HG,
        "spectral_shift_applied": True,
    },
    "diffusion": {"D_BASE": D_BASE, "D_HG_A": D_HG_A, "D_SRC_A": D_SRC_A},
    "n_off": n_off, "n_pmc": n_pmc,
    "pmc_breakdown": {"SRC_SRC": n_ss, "TGT_TGT": n_tt, "SRC_TGT": n_st},
    "pmc_density_pct": float(n_pmc / n_off * 100),
    "n_struct_pairs": n_struct_pairs,
    "dominance": {
        "D1_ratio": float(d1_ratio), "D1_ok": bool(D1_ok),
        "D2_pmc_top50": int(pmc_top50), "D2_ok": bool(D2_ok),
        "pmc_median_delta_omega": float(pmc_med),
        "nonpmc_p90_delta_omega": float(nonpmc_p90),
    },
    "oracle": {
        "PMC_AUROC": float(oracle_auroc), "ceiling_ok": bool(oracle_auroc >= 0.90),
        "dq_PMC_AUROC": float(dq_auroc), "rho_dq_domega": float(rho_dq_do),
    },
    "intervention": {
        "pmc_in_state_top50": int(pmc_in_state_top50),
        "pmc_in_struct_top50": int(pmc_in_struct_top50),
        "n_lesioned_M1_to_M2_edges": int(n_les),
    },
    "precision_at_k": {str(k): v for k, v in prec_at_k.items()},
    "top20_pairs": top20_data,
}

with open(f"{OUT_DIR}/oracle_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Network spec for downstream stages
network_spec = {
    "N_OBS": N_OBS, "N_H_LOCAL": N_H_LOCAL, "N_H_GLOBAL": N_H_GLOBAL, "N_TOTAL": N_TOTAL,
    "SEED": SEED, "PMC_SRC": PMC_SRC.tolist(), "PMC_TGT": PMC_TGT.tolist(),
    "HG": HG.tolist(), "HL": HL.tolist(),
    "M1": M1.tolist(), "M2": M2.tolist(), "M3": M3.tolist(), "M4": M4.tolist(),
    "P_WITHIN": P_WITHIN, "P_BETWEEN": P_BETWEEN, "W_STD": W_STD,
    "W_HG_TGT": W_HG_TGT, "W_SRC_HG": W_SRC_HG,
    "DIAG_OBS": DIAG_OBS, "DIAG_HL": DIAG_HL, "DIAG_HG": DIAG_HG,
    "D_BASE": D_BASE, "D_HG_A": D_HG_A, "D_SRC_A": D_SRC_A,
    "T_A": 150000, "T_B": 150000, "dt": 0.01, "burn_in": 10000,
}
with open(f"{OUT_DIR}/network_spec.json", "w") as f:
    json.dump(network_spec, f, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# 15. Hash-lock all outputs
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Hash-locking oracle objects ---")
manifest = {}
for fname in sorted(os.listdir(OUT_DIR)):
    if fname.endswith(".sha256") or fname in ("oracle_manifest.json", "oracle_master_hash.txt"):
        continue
    fpath = os.path.join(OUT_DIR, fname)
    if not os.path.isfile(fpath): continue
    with open(fpath, "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    manifest[fname] = h
    with open(fpath + ".sha256", "w") as fh:
        fh.write(h + "\n")

with open(f"{OUT_DIR}/oracle_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
master_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
with open(f"{OUT_DIR}/oracle_master_hash.txt", "w") as f:
    f.write(master_hash + "\n")
print(f"  Master hash: {master_hash[:16]}...  ({len(manifest)} files)")

# ─────────────────────────────────────────────────────────────────────────────
# 16. Final verdict
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== ORACLE CONSTRUCTION COMPLETE ===")
for label, ok in [("D1 dominance (>2.0×)", D1_ok),
                   ("D2 top-50 (≥60%)", D2_ok),
                   ("AT-5 oracle ceiling ≥0.90", oracle_auroc >= 0.90)]:
    print(f"  {'PASS' if ok else 'FAIL'}: {label}")

print(f"\n  Oracle PMC_AUROC:    {oracle_auroc:.4f}")
print(f"  D1 ratio:            {d1_ratio:.1f}×")
print(f"  PMC in oracle top-50:{pmc_top50}/50 ({pmc_top50/50*100:.0f}%)")
print(f"  Precision@50:        {prec_at_k[50]['precision']:.3f}  ({prec_at_k[50]['count']}/50 PMC)")
print(f"  State lesion top-50: {pmc_in_state_top50}/50 PMC (should dominate)")
print(f"  Struct lesion top-50:{pmc_in_struct_top50}/50 PMC (should be absent)")

all_pass = D1_ok and D2_ok and oracle_auroc >= 0.90
print(f"\n  ORACLE STATUS: {'ALIGNED — proceed to Phase 9D' if all_pass else 'NOT ALIGNED — redesign required'}")
