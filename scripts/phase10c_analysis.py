"""Phase 10C — Diffusion-Specific Robustness.

Authorization: Phase 10C, 2026-06-15.

Tests whether the ADEL/PDF current result is a generic artifact of
dense or state-specific diffusion vs a specific biological signal.

Sub-analyses:
  C1 — Diffusion specification comparison (5 variants)
  C2 — Dense-diffusion shuffle nulls (4 null types, 500 reps)
  C3 — Diffusion/precision decomposition (two state-conditioned forms)
  C4 — Diffusion hub / row-norm control
  C5 — Timescale sensitivity (from phase4c data)

PROHIBITIONS:
- No change to state segmentation or Class-4 definitions
- No change to key-pair list after seeing results
- No claim of unique D/Q decomposition
- No tuning to preserve ADEL results
"""

from __future__ import annotations
import csv, json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "results/phase10c"
OUT.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20260615)
N_BOOT = 500

# ── Neuron metadata ────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}

# ── Pair indexing ──────────────────────────────────────────────────────────────
ii_all, jj_all = np.triu_indices(N, k=1)   # all upper-triangle pairs
ranked_c4  = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ranked_off = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
ii_c4  = ii_all[ranked_c4]
jj_c4  = jj_all[ranked_c4]
N_C4   = len(ranked_c4)

def pair_idx(a: str, b: str) -> int | None:
    ai, bi = n2i.get(a), n2i.get(b)
    if ai is None or bi is None:
        return None
    lo, hi = min(ai, bi), max(ai, bi)
    for k in range(N_C4):
        if ii_c4[k] == lo and jj_c4[k] == hi:
            return k
    return None

# ── PDF pairs ──────────────────────────────────────────────────────────────────
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
PEP_CSV  = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"
pdf_pairs: set = set()
with open(PEP_CSV) as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in n2i or tgt not in n2i or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        pdf_pairs.add((min(a, b), max(a, b)))
pdf_pairs &= c4_set
pdf_mask = np.array(
    [(min(ii_c4[k], jj_c4[k]), max(ii_c4[k], jj_c4[k])) in pdf_pairs
     for k in range(N_C4)], dtype=bool
)

# ── Key pairs ──────────────────────────────────────────────────────────────────
KEY_PAIRS_NAMES = [
    ("ADEL", "URYVR"),
    ("ADEL", "URYDL"),
    ("ADEL", "RMEL"),
    ("RMEL", "URYDL"),
    ("RMEL", "RMER"),
]
key_idxs = {f"{a}–{b}": pair_idx(a, b) for a, b in KEY_PAIRS_NAMES}

# ── Module definitions (consistent with phase10a) ─────────────────────────────
BLOCKS = {
    "DA_mech":  [n2i[n] for n in ["ADEL","CEPDL","CEPDR","CEPVL"] if n in n2i],
    "URY_URX":  [n2i[n] for n in ["URYVR","URYDL","URYVL","URXL"] if n in n2i],
    "RME":      [n2i[n] for n in ["RMEL","RMER"] if n in n2i],
    "IL":       [n2i[n] for n in ["IL1DR","IL1L","IL1R","IL2DL","IL2DR","IL2VL","IL2VR"] if n in n2i],
    "AV":       [n2i[n] for n in ["AVJL","AVJR","AVEL","AVER"] if n in n2i],
}

def da_ury_rank(scores_c4: np.ndarray) -> int:
    """Rank of DA_mech ↔ URY_URX block by mean |score| among cross-block pairs."""
    abs_sc = np.abs(scores_c4)
    bnames = list(BLOCKS.keys())
    block_lists = [BLOCKS[b] for b in bnames]
    # For each pair of blocks, compute mean abs score
    pair_means = {}
    for bi, b1 in enumerate(bnames):
        for bj, b2 in enumerate(bnames):
            if bj <= bi:
                continue
            mask = np.array(
                [(ii_c4[k] in BLOCKS[b1] and jj_c4[k] in BLOCKS[b2]) or
                 (ii_c4[k] in BLOCKS[b2] and jj_c4[k] in BLOCKS[b1])
                 for k in range(N_C4)], dtype=bool
            )
            if mask.sum() == 0:
                continue
            pair_means[(b1, b2)] = abs_sc[mask].mean()
    if not pair_means:
        return -1
    sorted_keys = sorted(pair_means, key=lambda x: -pair_means[x])
    for rank, key in enumerate(sorted_keys, 1):
        if set(key) == {"DA_mech", "URY_URX"}:
            return rank
    return -1

def rank_scores(scores_c4: np.ndarray) -> np.ndarray:
    """Return dense ranks by |score| descending (rank 1 = highest |score|)."""
    order = np.argsort(-np.abs(scores_c4))
    ranks = np.empty(N_C4, dtype=int)
    ranks[order] = np.arange(1, N_C4 + 1)
    return ranks

def summary_row(label: str, vals_c4: np.ndarray) -> dict:
    """Compute standard summary for a scoring vector over C4 pairs."""
    ranks = rank_scores(vals_c4)
    primary_do = np.load(ROOT / "results/phase3d/DO_state_cep_full.npy")
    primary_vals = np.array([primary_do[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
    rho = float(stats.spearmanr(np.abs(vals_c4), np.abs(primary_vals)).statistic)
    top20_set = set(np.argsort(-np.abs(vals_c4))[:20])
    primary_top20 = set(np.argsort(-np.abs(primary_vals))[:20])
    overlap = len(top20_set & primary_top20)
    pdf_in_top20 = int(pdf_mask[list(top20_set)].sum())
    row = {
        "variant": label,
        "DA_URY_rank": da_ury_rank(vals_c4),
        "top20_overlap_primary": overlap,
        "PDF_top20": pdf_in_top20,
        "spearman_primary": round(rho, 4),
    }
    for name, idx in key_idxs.items():
        if idx is not None:
            row[f"{name}_rank"] = int(ranks[idx])
            row[f"{name}_val"]  = float(vals_c4[idx])
        else:
            row[f"{name}_rank"] = -1
            row[f"{name}_val"]  = float("nan")
    return row

# ── Load primary matrices ──────────────────────────────────────────────────────
PREC = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r + Q_r.T) / 2
Q_d = np.load(PREC / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d + Q_d.T) / 2
DQ  = Q_r - Q_d

D3D = ROOT / "results/phase3d"
D_r = np.load(D3D / "D_roam_cepnem.npy")
D_d = np.load(D3D / "D_dwell_cepnem.npy")
DD  = D_r - D_d    # ΔD
DO_ss_mat = np.load(D3D / "DO_state_cep_full.npy")  # D_r @ Q_r - D_d @ Q_d

# Extract primary C4 values
do_c4 = np.array([DO_ss_mat[ii_c4[k], jj_c4[k]] for k in range(N_C4)])

# ─────────────────────────────────────────────────────────────────────────────
# C1 — Diffusion Specification Comparison
# ─────────────────────────────────────────────────────────────────────────────
print("Running C1: diffusion specifications...")

D_pool = (D_r + D_d) / 2
D_I    = np.eye(N)
D_r_diag = np.diag(np.diag(D_r))
D_d_diag = np.diag(np.diag(D_d))
D_pool_diag = np.diag(np.diag(D_pool))

specs = [
    ("Identity (D=I)",           D_I,         D_I),
    ("Pooled diagonal",          D_pool_diag, D_pool_diag),
    ("State-specific diagonal",  D_r_diag,    D_d_diag),
    ("Pooled full",              D_pool,      D_pool),
    ("State-specific full (primary)", D_r,    D_d),
]

c1_rows = []
for label, Dr_spec, Dd_spec in specs:
    mat = Dr_spec @ Q_r - Dd_spec @ Q_d
    vals = np.array([mat[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
    c1_rows.append(summary_row(label, vals))

# Also save raw DO_ss for the identity and pooled-full specs
DO_identity  = D_I @ Q_r - D_I @ Q_d   # = Q_r - Q_d = DQ
DO_pool_full = D_pool @ Q_r - D_pool @ Q_d
DO_pool_diag = D_pool_diag @ Q_r - D_pool_diag @ Q_d
DO_ss_diag   = D_r_diag @ Q_r - D_d_diag @ Q_d

# ─────────────────────────────────────────────────────────────────────────────
# C2 — Dense-Diffusion Shuffle Nulls
# ─────────────────────────────────────────────────────────────────────────────
print("Running C2: shuffle nulls...")

def null_ranks_key_pairs(Dr_null: np.ndarray, Dd_null: np.ndarray) -> dict[str, int]:
    mat = Dr_null @ Q_r - Dd_null @ Q_d
    vals = np.array([mat[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
    ranks = rank_scores(vals)
    result = {}
    for name, idx in key_idxs.items():
        result[name] = int(ranks[idx]) if idx is not None else -1
    # DA_URY rank
    result["DA_URY"] = da_ury_rank(vals)
    # PDF top-20
    top20 = set(np.argsort(-np.abs(vals))[:20])
    result["PDF_top20"] = int(pdf_mask[list(top20)].sum())
    return result

def run_null(name: str, gen_fn) -> dict:
    """Run 500 permutation reps. gen_fn(rng) -> (Dr_null, Dd_null)."""
    key_results = {kp: [] for kp in key_idxs}
    key_results["DA_URY"] = []
    key_results["PDF_top20"] = []
    for _ in range(N_BOOT):
        Dr_n, Dd_n = gen_fn(RNG)
        res = null_ranks_key_pairs(Dr_n, Dd_n)
        for k in key_results:
            key_results[k].append(res[k])
    # Compute p-values: fraction of null reps where rank <= primary rank
    primary_ranks = rank_scores(do_c4)
    out = {"null_name": name, "n_reps": N_BOOT}
    for kp, idx in key_idxs.items():
        null_arr = np.array(key_results[kp])
        prim_rank = int(primary_ranks[idx]) if idx is not None else -1
        out[f"{kp}_primary_rank"] = prim_rank
        out[f"{kp}_null_median"]  = int(np.median(null_arr))
        out[f"{kp}_null_p5"]      = float(np.percentile(null_arr, 5))
        out[f"{kp}_null_p95"]     = float(np.percentile(null_arr, 95))
        # p-value: fraction of reps achieving rank <= primary (better or equal)
        out[f"{kp}_p_value"]      = float(np.mean(null_arr <= prim_rank))
    # DA_URY
    da_arr = np.array(key_results["DA_URY"])
    prim_da = da_ury_rank(do_c4)
    out["DA_URY_primary_rank"] = prim_da
    out["DA_URY_null_median"]  = int(np.median(da_arr))
    out["DA_URY_p_value"]      = float(np.mean(da_arr <= prim_da))
    # PDF top-20
    pdf_arr = np.array(key_results["PDF_top20"])
    prim_pdf = int(pdf_mask[list(set(np.argsort(-np.abs(do_c4))[:20]))].sum())
    out["PDF_top20_primary"] = prim_pdf
    out["PDF_top20_null_median"] = int(np.median(pdf_arr))
    # P(null >= primary top-20 count) — test for enrichment
    out["PDF_top20_p_value"] = float(np.mean(pdf_arr >= prim_pdf))
    return out

# Null 1: diagonal shuffle (shuffle diag of D_r and D_d independently)
def gen_diag_shuffle(rng: np.random.Generator):
    Dr_n = D_r.copy()
    Dd_n = D_d.copy()
    d_r = np.diag(D_r).copy(); rng.shuffle(d_r)
    d_d = np.diag(D_d).copy(); rng.shuffle(d_d)
    np.fill_diagonal(Dr_n, d_r)
    np.fill_diagonal(Dd_n, d_d)
    return Dr_n, Dd_n

# Null 2: off-diagonal shuffle (keep diagonal, shuffle upper-tri off-diag)
iu = np.triu_indices(N, k=1)
def gen_offdiag_shuffle(rng: np.random.Generator):
    Dr_n = D_r.copy()
    Dd_n = D_d.copy()
    # shuffle off-diagonal upper triangle independently
    od_r = Dr_n[iu].copy(); rng.shuffle(od_r)
    od_d = Dd_n[iu].copy(); rng.shuffle(od_d)
    Dr_n[iu] = od_r; Dr_n[iu[1], iu[0]] = od_r  # mirror
    Dd_n[iu] = od_d; Dd_n[iu[1], iu[0]] = od_d
    return Dr_n, Dd_n

# Null 3: row/column permutation (same permutation for D_r and D_d)
def gen_rowcol_perm(rng: np.random.Generator):
    perm = rng.permutation(N)
    Dr_n = D_r[np.ix_(perm, perm)]
    Dd_n = D_d[np.ix_(perm, perm)]
    return Dr_n, Dd_n

# Null 4: state-label swap (D_roam paired with Q_dwell, D_dwell with Q_roam)
# This is a single computation, not a distribution; we run it once.
DO_swap = D_r @ Q_d - D_d @ Q_r
swap_vals = np.array([DO_swap[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
swap_ranks = rank_scores(swap_vals)
primary_ranks_c4 = rank_scores(do_c4)

swap_result = {"null_name": "State-label swap (D_r@Q_d - D_d@Q_r)", "n_reps": 1}
for kp, idx in key_idxs.items():
    if idx is not None:
        swap_result[f"{kp}_primary_rank"]  = int(primary_ranks_c4[idx])
        swap_result[f"{kp}_swap_rank"]     = int(swap_ranks[idx])
        swap_result[f"{kp}_swap_val"]      = float(swap_vals[idx])
        swap_result[f"{kp}_primary_val"]   = float(do_c4[idx])
swap_result["DA_URY_primary_rank"] = da_ury_rank(do_c4)
swap_result["DA_URY_swap_rank"]    = da_ury_rank(swap_vals)
pdf_top20_swap = int(pdf_mask[list(set(np.argsort(-np.abs(swap_vals))[:20]))].sum())
swap_result["PDF_top20_swap"] = pdf_top20_swap

null1_result = run_null("Diagonal shuffle", gen_diag_shuffle)
null2_result = run_null("Off-diagonal shuffle", gen_offdiag_shuffle)
null3_result = run_null("Row/column permutation", gen_rowcol_perm)

# ─────────────────────────────────────────────────────────────────────────────
# C3 — Diffusion/Precision Decomposition
# ─────────────────────────────────────────────────────────────────────────────
print("Running C3: decomposition...")

# ΔΩ = D_r @ Q_r - D_d @ Q_d
# Decomposition A: ΔΩ = D_r @ ΔQ + ΔD @ Q_d
# Decomposition B: ΔΩ = D_d @ ΔQ + ΔD @ Q_r
term_A_prec = D_r @ DQ          # D_r(Q_r - Q_d)
term_A_diff = DD @ Q_d          # (D_r - D_d) Q_d
term_B_prec = D_d @ DQ          # D_d(Q_r - Q_d)
term_B_diff = DD @ Q_r          # (D_r - D_d) Q_r

# Verify: total should equal DO_ss_mat
recon_A = term_A_prec + term_A_diff
recon_B = term_B_prec + term_B_diff
assert np.allclose(recon_A, DO_ss_mat, atol=1e-8), "Decomp A mismatch"
assert np.allclose(recon_B, DO_ss_mat, atol=1e-8), "Decomp B mismatch"

c3_rows = []
for a_name, b_name in KEY_PAIRS_NAMES:
    idx = key_idxs.get(f"{a_name}–{b_name}")
    if idx is None:
        continue
    i, j = int(ii_c4[idx]), int(jj_c4[idx])
    total  = float(DO_ss_mat[i, j])
    aP     = float(term_A_prec[i, j])
    aD     = float(term_A_diff[i, j])
    bP     = float(term_B_prec[i, j])
    bD     = float(term_B_diff[i, j])
    frac_aP = aP / total if abs(total) > 1e-12 else float("nan")
    frac_aD = aD / total if abs(total) > 1e-12 else float("nan")
    frac_bP = bP / total if abs(total) > 1e-12 else float("nan")
    frac_bD = bD / total if abs(total) > 1e-12 else float("nan")
    sign_agree_A = (np.sign(aP) == np.sign(total), np.sign(aD) == np.sign(total))
    sign_agree_B = (np.sign(bP) == np.sign(total), np.sign(bD) == np.sign(total))
    c3_rows.append({
        "pair": f"{a_name}–{b_name}",
        "total_DO_ss":    round(total, 5),
        "A_prec_term":    round(aP, 5),
        "A_diff_term":    round(aD, 5),
        "B_prec_term":    round(bP, 5),
        "B_diff_term":    round(bD, 5),
        "A_frac_prec":    round(frac_aP, 3),
        "A_frac_diff":    round(frac_aD, 3),
        "B_frac_prec":    round(frac_bP, 3),
        "B_frac_diff":    round(frac_bD, 3),
        "A_sign_prec":    sign_agree_A[0],
        "A_sign_diff":    sign_agree_A[1],
        "B_sign_prec":    sign_agree_B[0],
        "B_sign_diff":    sign_agree_B[1],
    })

# ─────────────────────────────────────────────────────────────────────────────
# C4 — Diffusion Hub / Row-Norm Control
# ─────────────────────────────────────────────────────────────────────────────
print("Running C4: hub control...")

# Per-neuron hub metrics
row_norm_r  = np.linalg.norm(D_r, axis=1)   # ||D_r[i,:]||_2
row_norm_d  = np.linalg.norm(D_d, axis=1)
row_norm_dd = np.linalg.norm(DD,  axis=1)
diag_r  = np.diag(D_r)
diag_d  = np.diag(D_d)
diag_dd = np.diag(DD)
diag_abs_dd = np.abs(diag_dd)

# Per-pair hub predictors
sum_rn_r  = np.array([row_norm_r[ii_c4[k]]  + row_norm_r[jj_c4[k]]  for k in range(N_C4)])
max_rn_r  = np.array([max(row_norm_r[ii_c4[k]], row_norm_r[jj_c4[k]]) for k in range(N_C4)])
sum_diag_r= np.array([diag_r[ii_c4[k]] + diag_r[jj_c4[k]]            for k in range(N_C4)])
max_diag_r= np.array([max(diag_r[ii_c4[k]], diag_r[jj_c4[k]])         for k in range(N_C4)])
sum_rn_dd = np.array([row_norm_dd[ii_c4[k]] + row_norm_dd[jj_c4[k]]  for k in range(N_C4)])
max_abs_dd_diag = np.array([max(diag_abs_dd[ii_c4[k]], diag_abs_dd[jj_c4[k]]) for k in range(N_C4)])

abs_do = np.abs(do_c4)

hub_predictors = {
    "sum_row_norm_roam":  sum_rn_r,
    "max_row_norm_roam":  max_rn_r,
    "sum_diag_roam":      sum_diag_r,
    "max_diag_roam":      max_diag_r,
    "sum_row_norm_DD":    sum_rn_dd,
    "max_abs_DD_diag":    max_abs_dd_diag,
}

hub_spearman = {}
for name, pred in hub_predictors.items():
    rho, pv = stats.spearmanr(abs_do, pred)
    hub_spearman[name] = {"rho": round(float(rho), 4), "pval": float(pv)}

# Matched-hub null: for each key pair, percentile of |ΔΩ_ss| within
# stratum of C4 pairs with similar sum_rn_r (± 20% or ±0.05 absolute)
hub_null_rows = []
for kp_name, idx in key_idxs.items():
    if idx is None:
        continue
    hub_score = float(sum_rn_r[idx])
    tol = max(0.05, 0.20 * hub_score)
    strat_mask = np.abs(sum_rn_r - hub_score) <= tol
    strat_vals = abs_do[strat_mask]
    target_val = abs_do[idx]
    pct = float(np.mean(strat_vals < target_val))
    hub_null_rows.append({
        "pair":         kp_name,
        "hub_score":    round(hub_score, 4),
        "strat_n":      int(strat_mask.sum()),
        "target_abs_DO": round(float(target_val), 5),
        "empirical_pct": round(pct, 4),
        "p_value":      round(1.0 - pct, 4),
    })

# Also test whether PDF annotation is partially explained by hub score
# Partial rank correlation: ρ(|ΔΩ_ss|, PDF) controlling for hub score
# Use Spearman partial correlation via residual approach
pdf_int = pdf_mask.astype(float)
rho_do_pdf = float(stats.spearmanr(abs_do, pdf_int).statistic)
rho_hub_pdf = float(stats.spearmanr(sum_rn_r, pdf_int).statistic)
rho_hub_do  = float(stats.spearmanr(sum_rn_r, abs_do).statistic)
# partial rho(do, pdf | hub) via formula
num = rho_do_pdf - rho_hub_do * rho_hub_pdf
den = np.sqrt((1 - rho_hub_do**2) * (1 - rho_hub_pdf**2))
partial_rho = float(num / den) if abs(den) > 1e-12 else float("nan")

# ─────────────────────────────────────────────────────────────────────────────
# C5 — Timescale Sensitivity (from Phase 4C data)
# ─────────────────────────────────────────────────────────────────────────────
print("Running C5: timescale analysis...")

P4C = ROOT / "results/phase4c"
TAUS = [1, 2, 5, 10, 20]

c5_rows = []
for tau in TAUS:
    Dr_tau = np.load(P4C / f"D_cepnem_tau{tau}_roam.npy")
    Dd_tau = np.load(P4C / f"D_cepnem_tau{tau}_dwell.npy")
    DO_tau = Dr_tau @ Q_r - Dd_tau @ Q_d
    vals_tau = np.array([DO_tau[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
    ranks_tau = rank_scores(vals_tau)
    rho_prim = float(stats.spearmanr(np.abs(vals_tau), abs_do).statistic)
    top20_set = set(np.argsort(-np.abs(vals_tau))[:20])
    pdf_count = int(pdf_mask[list(top20_set)].sum())
    row = {"tau": tau, "rho_primary": round(rho_prim, 4), "PDF_top20": pdf_count}
    for kp_name, idx in key_idxs.items():
        if idx is not None:
            row[f"{kp_name}_rank"] = int(ranks_tau[idx])
            row[f"{kp_name}_val"]  = round(float(vals_tau[idx]), 5)
            row[f"{kp_name}_sign"] = int(np.sign(vals_tau[idx]))
        else:
            row[f"{kp_name}_rank"] = -1
    c5_rows.append(row)

# ─────────────────────────────────────────────────────────────────────────────
# Save numerics
# ─────────────────────────────────────────────────────────────────────────────
numerics = {
    "date": "2026-06-15",
    "authorization": "Phase 10C",
    "N_C4": N_C4,
    "N_BOOT": N_BOOT,
    "c1_specs": c1_rows,
    "c2_null1_diag_shuffle":  null1_result,
    "c2_null2_offdiag_shuffle": null2_result,
    "c2_null3_rowcol_perm":   null3_result,
    "c2_null4_state_swap":    swap_result,
    "c3_decomposition":       c3_rows,
    "c4_hub_spearman":        hub_spearman,
    "c4_hub_matched_null":    hub_null_rows,
    "c4_partial_rho_do_pdf_given_hub": round(partial_rho, 4),
    "c4_rho_do_pdf_marginal": round(rho_do_pdf, 4),
    "c4_rho_hub_do":          round(rho_hub_do, 4),
    "c4_rho_hub_pdf":         round(rho_hub_pdf, 4),
    "c5_timescale": c5_rows,
}

with open(OUT / "phase10c_numerics.json", "w") as f:
    json.dump(numerics, f, indent=2, default=str)

# ─────────────────────────────────────────────────────────────────────────────
# Save CSVs
# ─────────────────────────────────────────────────────────────────────────────
import csv as csv_mod

# C1 CSV
kp_fields = [f"{n}_{t}" for n in [n.replace("–", "_") for n in key_idxs] for t in ["rank", "val"]]
c1_headers = ["variant", "DA_URY_rank", "top20_overlap_primary", "PDF_top20", "spearman_primary"] + kp_fields
with open(OUT / "diffusion_specification_comparison.csv", "w", newline="") as f:
    w = csv_mod.DictWriter(f, fieldnames=c1_headers, extrasaction="ignore")
    w.writeheader(); w.writerows(c1_rows)

# C4 hub CSV
hub_headers = ["pair", "hub_score", "strat_n", "target_abs_DO", "empirical_pct", "p_value"]
with open(OUT / "diffusion_hub_control_table.csv", "w", newline="") as f:
    w = csv_mod.DictWriter(f, fieldnames=hub_headers)
    w.writeheader(); w.writerows(hub_null_rows)

# C2 nulls CSV
null_names = ["Diagonal shuffle", "Off-diagonal shuffle", "Row/col permutation", "State swap"]
null_keys_for_csv = [kp.replace("–", "_") for kp in key_idxs]
with open(OUT / "dense_diffusion_nulls_table.csv", "w", newline="") as f:
    fieldnames = ["null_type", "pair", "primary_rank", "null_median", "null_p5", "null_p95", "p_value"]
    w = csv_mod.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for null_res, null_nm in [
        (null1_result, "Diagonal shuffle"),
        (null2_result, "Off-diagonal shuffle"),
        (null3_result, "Row/col permutation"),
    ]:
        for kp in key_idxs:
            kpc = kp.replace("–", "_").replace(" ", "_")
            w.writerow({
                "null_type":    null_nm,
                "pair":         kp,
                "primary_rank": null_res.get(f"{kp}_primary_rank", ""),
                "null_median":  null_res.get(f"{kp}_null_median", ""),
                "null_p5":      null_res.get(f"{kp}_null_p5", ""),
                "null_p95":     null_res.get(f"{kp}_null_p95", ""),
                "p_value":      null_res.get(f"{kp}_p_value", ""),
            })
    # State swap
    for kp in key_idxs:
        w.writerow({
            "null_type":    "State swap",
            "pair":         kp,
            "primary_rank": swap_result.get(f"{kp}_primary_rank", ""),
            "null_median":  swap_result.get(f"{kp}_swap_rank", ""),
            "null_p5":      "N/A",
            "null_p95":     "N/A",
            "p_value":      "N/A (single comparison)",
        })

print("Done. Numerics and CSVs saved.")
print("JSON:", OUT / "phase10c_numerics.json")
