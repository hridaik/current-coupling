"""Phase 4B — Behavioral Encoding Alignment Analysis.

Tests whether state-dependent PDF-associated conditional organization
preferentially links neurons with aligned behavioral encoding.

Outputs to results/phase4b/:
  encoding_weights.npy         (61, 4) — c_vT, c_v, c_th, c_P per neuron
  alignment_matrix.npy         (61, 61) — pairwise scalar (c_v) alignment
  alignment_matrix_vector.npy  (61, 61) — pairwise cosine alignment
  phase4b_results.json         — all numeric results
  b0..b6 markdown reports written separately
"""

from __future__ import annotations
import os, json, csv, glob, warnings
import numpy as np
from scipy import stats

# ── paths ──────────────────────────────────────────────────────────────────
ROOT       = "/home/hridai/code/worm-phase0"
RESID_DIR  = f"{ROOT}/results/phase1/data/cepnem_residuals"
PHASE2_DIR = f"{ROOT}/results/phase2"
DATA_DIR   = f"{ROOT}/data/randi/wormneuroatlas/wormneuroatlas/data"
OUT_DIR    = f"{ROOT}/results/phase4b"
os.makedirs(OUT_DIR, exist_ok=True)

# ── CePNEM parameter indices (confirmed from cepnem_residualize.py) ──────────
_P_CVT, _P_CV, _P_CTH, _P_CP = 0, 1, 2, 3

# ── 61-neuron list & recording IDs ──────────────────────────────────────────
copresence = json.load(open(f"{PHASE2_DIR}/stage0/copresence_report.json"))
NEURONS_61 = copresence["neurons"]
N = len(NEURONS_61)
assert N == 61
n2i = {n: i for i, n in enumerate(NEURONS_61)}
neurons_set = set(NEURONS_61)
RECORDING_IDS = copresence["recording_ids"]
assert len(RECORDING_IDS) == 40

# ── DQ matrices & ranked upper-triangle indices ──────────────────────────────
DQ_cepnem = np.load(f"{PHASE2_DIR}/stage2/DQ_cepnem.npy")   # (61,61)
DQ_gcamp  = np.load(f"{PHASE2_DIR}/stage2/DQ_gcamp.npy")    # (61,61)

# ranked_class4_cepnem.npy: indices into np.triu_indices(61,k=1) array
# — already sorted by |DQ_cepnem| descending
ranked_c4_utidx = np.load(f"{PHASE2_DIR}/stage2/ranked_class4_cepnem.npy")  # (1321,)
ii_all, jj_all = np.triu_indices(N, k=1)   # (1830,) upper-triangle pairs
assert len(ranked_c4_utidx) == 1321

# Convert upper-triangle indices to actual (i,j) neuron pair indices
c4_i = ii_all[ranked_c4_utidx]   # (1321,) row indices, correctly decoded
c4_j = jj_all[ranked_c4_utidx]   # (1321,) col indices
c4_set = set(zip(map(int, c4_i), map(int, c4_j)))  # set of (i,j) with i<j

n_c4 = len(ranked_c4_utidx)
assert n_c4 == 1321

# ── Stage2 results ─────────────────────────────────────────────────────────
s2 = json.load(open(f"{PHASE2_DIR}/stage2/stage2_results.json"))


# ════════════════════════════════════════════════════════════════════════════
# STEP 0: BUILD ANNOTATION MASKS
# ════════════════════════════════════════════════════════════════════════════

def load_bentley_pairs(csv_path: str, keep_fn) -> set:
    """Return set of (i,j) with i<j for pairs in 61-neuron subgraph satisfying keep_fn."""
    pairs = set()
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            src, tgt = row[0].strip(), row[1].strip()
            if src not in neurons_set or tgt not in neurons_set:
                continue
            if src == tgt:
                continue
            if not keep_fn(row):
                continue
            a, b = n2i[src], n2i[tgt]
            pairs.add((min(a, b), max(a, b)))
    return pairs

# PDF annotation
pdf_all_61 = load_bentley_pairs(
    f"{DATA_DIR}/esconnectome_neuropeptides_Bentley_2016.csv",
    lambda row: "pdf" in row[2].strip().lower(),
)
pdf_c4 = pdf_all_61 & c4_set
assert len(pdf_c4) == 61, f"Expected 61 PDF C4 pairs, got {len(pdf_c4)}"

# Serotonin annotation
sero_all_61 = load_bentley_pairs(
    f"{DATA_DIR}/esconnectome_monoamines_Bentley_2016.csv",
    lambda row: row[2].strip().lower() == "serotonin",
)
sero_c4 = sero_all_61 & c4_set
assert len(sero_c4) == 33, f"Expected 33 serotonin C4 pairs, got {len(sero_c4)}"

# Combined
comb_c4 = pdf_c4 | sero_c4

# Randi: reconstruct from stage2 top50 pairs with randi_annotated=True
# (full 108-pair mask unavailable without funatlas H5; use partial sample)
randi_from_top50 = set()
for entry in (s2["coordinates"]["cepnem"]["top50_class4"] +
              s2["coordinates"]["gcamp"]["top50_class4"]):
    if entry["randi_annotated"]:
        randi_from_top50.add((min(entry["i"], entry["j"]),
                              max(entry["i"], entry["j"])))
randi_c4_partial = randi_from_top50 & c4_set
N_RANDI_PARTIAL = len(randi_c4_partial)   # 8 pairs; partial sample only

# Convert annotations to boolean arrays aligned with ranked order
def pairs_to_boolvec(pair_set: set) -> np.ndarray:
    """(1321,) bool array: True where (c4_i[k], c4_j[k]) is in pair_set."""
    return np.array([(int(c4_i[k]), int(c4_j[k])) in pair_set for k in range(n_c4)])

pdf_flag      = pairs_to_boolvec(pdf_c4)
sero_flag     = pairs_to_boolvec(sero_c4)
comb_flag     = pairs_to_boolvec(comb_c4)
randi_flag    = pairs_to_boolvec(randi_c4_partial)  # partial

print(f"Annotation counts (Class-4):")
print(f"  PDF:       {pdf_flag.sum()} (expected 61)")
print(f"  Serotonin: {sero_flag.sum()} (expected 33)")
print(f"  Combined:  {comb_flag.sum()} (expected 94)")
print(f"  Randi:     {randi_flag.sum()} (partial, 8/108)")


# ════════════════════════════════════════════════════════════════════════════
# STEP 1: EXTRACT BEHAVIORAL ENCODING WEIGHTS
# ════════════════════════════════════════════════════════════════════════════

print("\n=== Extracting behavioral encoding weights ===")

weights_sum   = np.zeros((N, 4))
weights_count = np.zeros(N, dtype=int)
weights_all   = [[] for _ in range(N)]   # list per neuron, each entry = [c_v, c_th, c_P]

for rec_id in RECORDING_IDS:
    fpath = f"{RESID_DIR}/{rec_id}.npz"
    if not os.path.exists(fpath):
        print(f"  MISSING: {fpath}")
        continue
    d     = np.load(fpath, allow_pickle=True)
    labels = list(d["neuron_labels"])
    pm    = d["params_med"]           # (11, N_rec, n_epochs)
    pm_mean = pm.mean(axis=2)         # (11, N_rec) — mean across epochs

    for local_idx, name in enumerate(labels):
        if name not in n2i:
            continue
        gi = n2i[name]
        c_vT = float(pm_mean[_P_CVT, local_idx])
        c_v  = float(pm_mean[_P_CV,  local_idx])
        c_th = float(pm_mean[_P_CTH, local_idx])
        c_P  = float(pm_mean[_P_CP,  local_idx])
        weights_sum[gi]   += [c_vT, c_v, c_th, c_P]
        weights_count[gi] += 1
        weights_all[gi].append([c_v, c_th, c_P])

encoding_weights = np.zeros((N, 4))
for i in range(N):
    if weights_count[i] > 0:
        encoding_weights[i] = weights_sum[i] / weights_count[i]
    else:
        encoding_weights[i] = np.nan

n_obs = (weights_count > 0).sum()
print(f"  Neurons with ≥1 recording: {n_obs}/61")

np.save(f"{OUT_DIR}/encoding_weights.npy", encoding_weights)

# Per-neuron std across recordings
encoding_std = np.zeros((N, 3))   # c_v, c_th, c_P
for i in range(N):
    if len(weights_all[i]) >= 2:
        encoding_std[i] = np.array(weights_all[i]).std(axis=0)


# ════════════════════════════════════════════════════════════════════════════
# STEP 2: PAIRWISE ALIGNMENT MATRICES
# ════════════════════════════════════════════════════════════════════════════

print("\n=== Building pairwise alignment matrices ===")

cv_vec = encoding_weights[:, _P_CV].copy()
cv_vec[np.isnan(cv_vec)] = 0.0

# Scalar alignment: w_i * w_j (c_v only)
A_scalar = np.outer(cv_vec, cv_vec)

# Vector alignment: cosine similarity over [c_v, c_th, c_P]
w_vec = encoding_weights[:, 1:4].copy()
w_vec[np.isnan(w_vec)] = 0.0
norms = np.linalg.norm(w_vec, axis=1, keepdims=True)
norms[norms == 0] = 1.0
w_norm = w_vec / norms
A_cosine = w_norm @ w_norm.T   # (61, 61)

np.save(f"{OUT_DIR}/alignment_matrix.npy", A_scalar)
np.save(f"{OUT_DIR}/alignment_matrix_vector.npy", A_cosine)

# Alignment vectors for all Class-4 pairs (correct indexing)
align_scalar = A_scalar[c4_i, c4_j]
align_cosine = A_cosine[c4_i, c4_j]

# DQ vectors (correctly indexed)
dq_signed = DQ_cepnem[c4_i, c4_j]
dq_abs    = np.abs(dq_signed)

print(f"  Scalar alignment range: [{align_scalar.min():.5f}, {align_scalar.max():.5f}]")
print(f"  Cosine alignment range: [{align_cosine.min():.5f}, {align_cosine.max():.5f}]")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3: ENRICHMENT TESTS (alignment by annotation category)
# ════════════════════════════════════════════════════════════════════════════

print("\n=== Alignment enrichment tests ===")

def mannwhitney_auroc(pos_scores, neg_scores):
    if len(pos_scores) == 0 or len(neg_scores) == 0:
        return np.nan, np.nan
    u, p = stats.mannwhitneyu(pos_scores, neg_scores, alternative="greater")
    return float(u / (len(pos_scores) * len(neg_scores))), float(p)

def permutation_auroc(ann_flag: np.ndarray, scores: np.ndarray, n_perm=2000, seed=42):
    rng = np.random.default_rng(seed)
    n_pos = int(ann_flag.sum())
    n_all = len(scores)
    pos_scores = scores[ann_flag]
    neg_scores = scores[~ann_flag]
    obs_auc, obs_p = mannwhitney_auroc(pos_scores, neg_scores)
    null_aucs = []
    idx_all = np.arange(n_all)
    for _ in range(n_perm):
        perm = rng.choice(idx_all, n_pos, replace=False)
        perm_flag = np.zeros(n_all, dtype=bool)
        perm_flag[perm] = True
        auc, _ = mannwhitney_auroc(scores[perm_flag], scores[~perm_flag])
        null_aucs.append(auc)
    null_aucs = np.array(null_aucs)
    p_perm = (null_aucs >= obs_auc).mean()
    return obs_auc, obs_p, float(p_perm), float(null_aucs.mean()), float(null_aucs.std())

results_enrichment = {}

ann_groups = [
    ("Bentley_PDF", pdf_flag),
    ("Bentley_serotonin", sero_flag),
    ("Bentley_combined", comb_flag),
]

for ann_name, ann_flag in ann_groups:
    n_pos = int(ann_flag.sum())
    if n_pos < 5:
        print(f"  [{ann_name}] n={n_pos} — insufficient, skipping")
        results_enrichment[ann_name] = {"n": n_pos, "skipped": True}
        continue

    auc_sc, p_mw_sc, p_perm_sc, null_mean_sc, null_std_sc = permutation_auroc(
        ann_flag, align_scalar, n_perm=2000, seed=42
    )
    auc_co, p_mw_co, p_perm_co, null_mean_co, null_std_co = permutation_auroc(
        ann_flag, align_cosine, n_perm=2000, seed=43
    )

    results_enrichment[ann_name] = {
        "n": n_pos,
        "scalar": {
            "mean_pos": float(align_scalar[ann_flag].mean()),
            "mean_neg": float(align_scalar[~ann_flag].mean()),
            "median_pos": float(np.median(align_scalar[ann_flag])),
            "auroc": auc_sc,
            "p_mannwhitney": p_mw_sc,
            "p_perm": p_perm_sc,
            "null_mean": null_mean_sc,
            "null_std": null_std_sc,
        },
        "cosine": {
            "mean_pos": float(align_cosine[ann_flag].mean()),
            "mean_neg": float(align_cosine[~ann_flag].mean()),
            "median_pos": float(np.median(align_cosine[ann_flag])),
            "auroc": auc_co,
            "p_mannwhitney": p_mw_co,
            "p_perm": p_perm_co,
            "null_mean": null_mean_co,
            "null_std": null_std_co,
        },
    }
    print(f"\n  [{ann_name}] n={n_pos}")
    print(f"    scalar: mean_pos={align_scalar[ann_flag].mean():.5f}  mean_neg={align_scalar[~ann_flag].mean():.5f}")
    print(f"    scalar AUROC={auc_sc:.4f}  p_perm={p_perm_sc:.4f}  null={null_mean_sc:.4f}±{null_std_sc:.4f}")
    print(f"    cosine AUROC={auc_co:.4f}  p_perm={p_perm_co:.4f}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4: TOP ΔQ LINK ALIGNMENT
# ════════════════════════════════════════════════════════════════════════════

print("\n=== Top |ΔQ| link alignment ===")

# ranked array is already sorted by |DQ| descending
top20_pos = slice(0, 20)
top50_pos = slice(0, 50)

t20_align = align_scalar[:20]
t50_align = align_scalar[:50]
t20_dq    = dq_signed[:20]
t50_dq    = dq_signed[:50]

print(f"  Top-20: mean_align={t20_align.mean():.5f}  median={np.median(t20_align):.5f}")
print(f"  Top-50: mean_align={t50_align.mean():.5f}  median={np.median(t50_align):.5f}")
print(f"  All C4: mean_align={align_scalar.mean():.5f}  median={np.median(align_scalar):.5f}")

# Permutation test: does top-K have higher alignment than random K from all C4?
def perm_mean_test(obs_mean, pool, k, n_perm=2000, seed=99):
    rng = np.random.default_rng(seed)
    null = np.array([rng.choice(pool, k, replace=False).mean() for _ in range(n_perm)])
    p = float((null >= obs_mean).mean())
    return p, float(null.mean()), float(null.std())

p20, nm20, ns20 = perm_mean_test(t20_align.mean(), align_scalar, 20)
p50, nm50, ns50 = perm_mean_test(t50_align.mean(), align_scalar, 50)
print(f"  Top-20 perm p={p20:.4f}  null={nm20:.5f}±{ns20:.5f}")
print(f"  Top-50 perm p={p50:.4f}  null={nm50:.5f}±{ns50:.5f}")

# Key pair alignment values
print("\n  Key pair details:")
key_pairs_report = {}
for pname, (pi, pj) in [("ADEL-URYVR", (0, 60)),
                          ("ADEL-URYDL", (0, 58)),
                          ("ADEL-RMEL",  (0, 53))]:
    a_sc  = float(A_scalar[pi, pj])
    a_co  = float(A_cosine[pi, pj])
    dq_v  = float(DQ_cepnem[pi, pj])
    cv_i  = float(cv_vec[pi])
    cv_j  = float(cv_vec[pj])
    # find rank in C4 by |alignment| (signed alignment)
    pair_key = (min(pi,pj), max(pi,pj))
    if pair_key in c4_set:
        pos = list(c4_set).index(pair_key) if False else None
        # find position in ordered c4 list
        for k in range(n_c4):
            if int(c4_i[k]) == min(pi,pj) and int(c4_j[k]) == max(pi,pj):
                align_rank_among_c4 = int(np.sum(np.abs(align_scalar) >= abs(a_sc)))
                break
    else:
        align_rank_among_c4 = None
    print(f"    {pname}: c_v_i={cv_i:+.4f}  c_v_j={cv_j:+.4f}  "
          f"scalar={a_sc:+.5f}  cosine={a_co:+.4f}  DQ={dq_v:+.5f}  "
          f"|align| rank ≈{align_rank_among_c4}/{n_c4}")
    key_pairs_report[pname] = {
        "c_v_i": cv_i, "c_v_j": cv_j,
        "align_scalar": a_sc, "align_cosine": a_co,
        "dq_cepnem": dq_v,
        "align_rank_approx": align_rank_among_c4,
    }

toplink_results = {
    "top20": {"mean_align": float(t20_align.mean()), "median_align": float(np.median(t20_align)),
              "p_perm": p20, "null_mean": nm20, "null_std": ns20},
    "top50": {"mean_align": float(t50_align.mean()), "median_align": float(np.median(t50_align)),
              "p_perm": p50, "null_mean": nm50, "null_std": ns50},
    "all_c4": {"mean_align": float(align_scalar.mean()), "median_align": float(np.median(align_scalar))},
    "key_pairs": key_pairs_report,
}


# ════════════════════════════════════════════════════════════════════════════
# STEP 5: INFORMATION-LIMITING JOINT TEST (alignment × |ΔQ|)
# ════════════════════════════════════════════════════════════════════════════

print("\n=== Information-limiting joint test ===")

# Joint score: |alignment| × |DQ|
joint_score = np.abs(align_scalar) * dq_abs

pdf_joint_mean = float(joint_score[pdf_flag].mean())
all_joint_mean = float(joint_score.mean())
print(f"  PDF pairs joint mean: {pdf_joint_mean:.7f}")
print(f"  All C4   joint mean: {all_joint_mean:.7f}")

p_joint, nm_joint, ns_joint = perm_mean_test(pdf_joint_mean, joint_score, int(pdf_flag.sum()))
print(f"  Perm p={p_joint:.4f}  null={nm_joint:.7f}±{ns_joint:.7f}")

# Fraction of PDF in top-quartile of BOTH alignment AND |DQ|
q75_align = float(np.percentile(np.abs(align_scalar), 75))
q75_dq    = float(np.percentile(dq_abs, 75))
both_top  = (np.abs(align_scalar) >= q75_align) & (dq_abs >= q75_dq)
n_both_pdf = int((both_top & pdf_flag).sum())
n_both_all = int(both_top.sum())
frac_pdf   = n_both_pdf / int(pdf_flag.sum())
frac_all   = n_both_all / n_c4
print(f"  Both top-quartile: PDF={n_both_pdf}/{int(pdf_flag.sum())} ({100*frac_pdf:.1f}%)  "
      f"all={n_both_all}/{n_c4} ({100*frac_all:.1f}%)")

il_results = {
    "joint_score_mean_pdf": pdf_joint_mean,
    "joint_score_mean_all": all_joint_mean,
    "p_perm": float(p_joint),
    "null_mean": float(nm_joint),
    "null_std": float(ns_joint),
    "top_quartile_both": {
        "pdf_n": n_both_pdf,
        "pdf_total": int(pdf_flag.sum()),
        "pdf_frac": frac_pdf,
        "all_frac": frac_all,
        "q75_align": q75_align,
        "q75_dq": q75_dq,
    }
}


# ════════════════════════════════════════════════════════════════════════════
# STEP 6: REPORT TOP-NEURON BEHAVIORAL ENCODINGS (for b1 doc)
# ════════════════════════════════════════════════════════════════════════════

cv = encoding_weights[:, _P_CV]

top_pos_idx = np.argsort(cv)[::-1][:10]
top_neg_idx = np.argsort(cv)[:10]

top_pos_enc = [(NEURONS_61[i], float(cv[i]), float(encoding_weights[i,2]),
                float(encoding_weights[i,3]), int(weights_count[i])) for i in top_pos_idx]
top_neg_enc = [(NEURONS_61[i], float(cv[i]), float(encoding_weights[i,2]),
                float(encoding_weights[i,3]), int(weights_count[i])) for i in top_neg_idx]

# Key neuron details
key_neurons = ["ADEL", "URYVR", "URYDL", "RMEL", "RMER", "RID", "AVDL", "URXL", "OLQVR"]
key_enc = {}
for nm in key_neurons:
    if nm in n2i:
        gi = n2i[nm]
        key_enc[nm] = {
            "c_v": float(cv[gi]),
            "c_th": float(encoding_weights[gi,2]),
            "c_P": float(encoding_weights[gi,3]),
            "c_vT": float(encoding_weights[gi,0]),
            "n_recordings": int(weights_count[gi]),
        }

print("\n  Key PDF-circuit neuron encodings:")
for nm, d in key_enc.items():
    print(f"    {nm:8s}: c_v={d['c_v']:+.4f}  c_th={d['c_th']:+.4f}  c_P={d['c_P']:+.4f}  "
          f"n_recs={d['n_recordings']}")


# ════════════════════════════════════════════════════════════════════════════
# SAVE JSON RESULTS
# ════════════════════════════════════════════════════════════════════════════

def to_json_safe(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, dict): return {k: to_json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [to_json_safe(x) for x in o]
    if isinstance(o, bool): return bool(o)
    return o

json_out = {
    "phase": "4B",
    "date": "2026-06-12",
    "n_neurons": N,
    "n_class4": n_c4,
    "annotations": {
        "PDF_c4": int(pdf_flag.sum()),
        "serotonin_c4": int(sero_flag.sum()),
        "combined_c4": int(comb_flag.sum()),
        "randi_partial": N_RANDI_PARTIAL,
    },
    "key_neuron_encoding": key_enc,
    "top_velocity_positive": [(nm, round(cv_v, 5)) for nm, cv_v, *_ in top_pos_enc],
    "top_velocity_negative": [(nm, round(cv_v, 5)) for nm, cv_v, *_ in top_neg_enc],
    "alignment_enrichment": results_enrichment,
    "toplink_alignment": toplink_results,
    "information_limiting": il_results,
}

with open(f"{OUT_DIR}/phase4b_results.json", "w") as f:
    json.dump(to_json_safe(json_out), f, indent=2)

print(f"\n[DONE] All results computed and saved to {OUT_DIR}/phase4b_results.json")
print(f"  PDF AUROC (scalar): {results_enrichment['Bentley_PDF']['scalar']['auroc']:.4f}  "
      f"p_perm={results_enrichment['Bentley_PDF']['scalar']['p_perm']:.4f}")
print(f"  Top-20 perm p={p20:.4f}")
print(f"  Joint IL p_perm={p_joint:.4f}")
