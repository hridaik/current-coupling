"""Phase 3E — Current vs Precision Difference Analysis.

Authorization: Phase 3E, 2026-06-03.

E1: Ω–Q Disagreement Map  (R = |ΔΩ_full - ΔQ|)
E2: State-dependent diffusion organization (ΔD biology)
E3: Distance and topology (are Ω-emphasized pairs more long-range?)
E4: Network motif analysis (conditional on E1/E3 signal)

PROHIBITIONS: No model fitting. No held-out evaluation. No perturbation predictions.
"""
from __future__ import annotations
import collections, csv, json, sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT3E = ROOT / "results/phase3e"

# ── Metadata ──────────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Class 4 pairs and annotations ────────────────────────────────────────────
ranked_c4 = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

ranked_off = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
off_set = set(zip(map(int, ii_all[ranked_off]), map(int, jj_all[ranked_off])))
A_raw = np.zeros((N, N), dtype=bool)
for k in range(len(ii_all)):
    i, j = int(ii_all[k]), int(jj_all[k])
    if (i, j) not in off_set:
        A_raw[i, j] = A_raw[j, i] = True

DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
PEP_CSV  = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"
MONO_CSV = DATA_DIR / "esconnectome_monoamines_Bentley_2016.csv"

def load_bentley(csv_path, keep_fn):
    mat = np.zeros((N, N), dtype=bool)
    with open(csv_path) as f:
        reader = csv.reader(f); next(reader)
        for row in reader:
            if len(row) < 3: continue
            src, tgt = row[0].strip(), row[1].strip()
            if src not in neurons_set or tgt not in neurons_set or src==tgt: continue
            if not keep_fn(row): continue
            a, b = n2i[src], n2i[tgt]
            mat[a,b] = mat[b,a] = True
    return mat

pdf_mat  = load_bentley(PEP_CSV,  lambda r: "pdf" in r[2].lower())
ser_mat  = load_bentley(MONO_CSV, lambda r: r[2].strip().lower()=="serotonin")

import h5py
randi_mat = np.zeros((N, N), dtype=bool)
with h5py.File(DATA_DIR / "funatlas.h5", "r") as f:
    nids = [n.decode() if isinstance(n, bytes) else n for n in f["neuron_ids"][:]]
    q_unc = f["unc31/q"][:]
for i_r, id_r in enumerate(nids):
    if id_r not in n2i: continue
    for j_r, id_j in enumerate(nids):
        if j_r==i_r or id_j not in n2i: continue
        if q_unc[i_r,j_r] < 0.10:
            randi_mat[n2i[id_r],n2i[id_j]] = randi_mat[n2i[id_j],n2i[id_r]] = True

pdf_c4   = pdf_mat[ii_c4, jj_c4].astype(bool)
ser_c4   = ser_mat[ii_c4, jj_c4].astype(bool)
randi_c4 = randi_mat[ii_c4, jj_c4].astype(bool)
comb_c4  = pdf_c4 | ser_c4
any_ann  = comb_c4 | randi_c4
unann_c4 = ~any_ann

# ── ΔQ and ΔΩ_full ────────────────────────────────────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r+Q_r.T)/2
Q_d = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d+Q_d.T)/2
DQ  = Q_r - Q_d
D_emp = np.load(ROOT / "results/phase3c/D_emp_cepnem.npy")
DO    = D_emp @ DQ

dq_c4 = DQ[ii_c4, jj_c4]      # signed
do_c4 = DO[ii_c4, jj_c4]      # signed
abs_dq = np.abs(dq_c4)
abs_do = np.abs(do_c4)

ZERO_THR = 1e-10
is_zero_dq = abs_dq < ZERO_THR

# ── State-specific D ─────────────────────────────────────────────────────────
D_roam  = np.load(ROOT / "results/phase3d/D_roam_cepnem.npy")
D_dwell = np.load(ROOT / "results/phase3d/D_dwell_cepnem.npy")
delta_D = D_roam - D_dwell
delta_D_diag = np.diag(delta_D)

# =============================================================================
# E1: Disagreement Map
# =============================================================================
print("="*70); print("E1 — Ω–Q Disagreement Map: R = |ΔΩ_full - ΔQ|")

R_c4 = np.abs(do_c4 - dq_c4)   # disagreement per Class 4 pair

# Also compute signed disagreement
signed_R = do_c4 - dq_c4  # positive: Ω > Q; negative: Q > Ω

print(f"\nR statistics:")
print(f"  mean={R_c4.mean():.4f}  median={np.median(R_c4):.4f}  "
      f"std={R_c4.std():.4f}  max={R_c4.max():.4f}")

# Top 50 disagreement pairs
top50_R = np.argsort(-R_c4)[:50]
rank_dq = np.empty(N_C4, dtype=int); rank_dq[np.argsort(-abs_dq)] = np.arange(1,N_C4+1)
rank_do = np.empty(N_C4, dtype=int); rank_do[np.argsort(-abs_do)] = np.arange(1,N_C4+1)

print(f"\nTop 50 disagreement pairs (R = |ΔΩ - ΔQ|):")
top50_list = []
for pos, k in enumerate(top50_R):
    i, j = ii_c4[k], jj_c4[k]
    row = {
        "rank_R": pos+1, "pair": f"{NEURONS[i]}–{NEURONS[j]}",
        "R": float(R_c4[k]), "dq": float(dq_c4[k]), "do": float(do_c4[k]),
        "rank_dq": int(rank_dq[k]), "rank_do": int(rank_do[k]),
        "pdf": bool(pdf_c4[k]), "serotonin": bool(ser_c4[k]),
        "randi": bool(randi_c4[k]), "adel": bool(ii_c4[k]==n2i.get("ADEL") or jj_c4[k]==n2i.get("ADEL")),
        "ury": bool(any(NEURONS[x] in {"URYDL","URYVL","URYVR","URXL"} for x in [i,j])),
        "zero_dq": bool(is_zero_dq[k]),
    }
    top50_list.append(row)
    src = "PDF" if row["pdf"] else ("SER" if row["serotonin"] else ("RANDI" if row["randi"] else "----"))
    print(f"  {pos+1:3d}. {NEURONS[i]:6s}–{NEURONS[j]:6s}: "
          f"R={R_c4[k]:.4f}  ΔQ={dq_c4[k]:+.4f}  ΔΩ={do_c4[k]:+.4f}  "
          f"ΔQrank={rank_dq[k]:4d}  Ωrank={rank_do[k]:4d}  {src}")

# E1.2: R by annotation
print(f"\nE1.2 — R by annotation category:")
groups = [
    ("PDF",    pdf_c4),
    ("Serotonin", ser_c4),
    ("Randi",  randi_c4),
    ("Unannotated", unann_c4),
    ("ALL",    np.ones(N_C4, dtype=bool)),
]
e12 = {}
for name, mask in groups:
    if mask.sum() == 0: continue
    rs = R_c4[mask]
    rho, p = stats.mannwhitneyu(rs, R_c4[~mask & (mask!=mask)], alternative="greater") if False else (0,1)
    print(f"  {name:15s}: n={mask.sum():4d}  mean_R={rs.mean():.4f}  "
          f"median_R={np.median(rs):.4f}  max_R={rs.max():.4f}")
    e12[name] = {"n": int(mask.sum()), "mean_R": float(rs.mean()),
                 "median_R": float(np.median(rs)), "max_R": float(rs.max())}

# E1.3: R vs ΔQ rank
print(f"\nE1.3 — R vs |ΔQ| correlation:")
rho_R_dq, _ = stats.spearmanr(R_c4, abs_dq)
rho_R_do, _ = stats.spearmanr(R_c4, abs_do)
print(f"  ρ(R, |ΔQ|) = {rho_R_dq:.4f}")
print(f"  ρ(R, |ΔΩ|) = {rho_R_do:.4f}")

# R by ΔQ=0 vs ΔQ≠0
R_zero = R_c4[is_zero_dq]; R_nz = R_c4[~is_zero_dq]
print(f"  Mean R for ΔQ=0: {R_zero.mean():.4f}  ΔQ≠0: {R_nz.mean():.4f}")
print(f"  Fraction of top-50 R pairs with ΔQ≠0: {sum(1 for k in top50_R if not is_zero_dq[k])}/50")
print(f"  Fraction of top-50 R pairs with ΔQ=0:  {sum(1 for k in top50_R if is_zero_dq[k])}/50")

# Where Ω inflates (do > dq) vs deflates (do < dq)
n_inflate = int((signed_R > 0.01).sum())
n_deflate = int((signed_R < -0.01).sum())
print(f"\n  Pairs where Ω significantly inflates (ΔΩ > ΔQ + 0.01): {n_inflate}")
print(f"  Pairs where Ω significantly deflates (ΔΩ < ΔQ - 0.01): {n_deflate}")
print(f"  Mean signed_R for PDF pairs:       {signed_R[pdf_c4].mean():+.4f}")
print(f"  Mean signed_R for non-PDF pairs:   {signed_R[~pdf_c4].mean():+.4f}")

# =============================================================================
# E2: State-Dependent Diffusion Organization
# =============================================================================
print("\n"+"="*70); print("E2 — State-Dependent Diffusion Organization")

# E2.1: Top neurons by ΔD_ii (roam - dwell diagonal)
print("\nE2.1 — Top neurons by ΔD_ii (D_roam_ii - D_dwell_ii):")
idx_sorted_up   = np.argsort(-delta_D_diag)   # largest positive (roam > dwell)
idx_sorted_down = np.argsort(delta_D_diag)    # largest negative (dwell > roam)

print("  Top 10 ROAMING-dominant (most increased D in roam):")
e21_up = []
for rank, i in enumerate(idx_sorted_up[:10]):
    n = NEURONS[i]
    print(f"  {rank+1:2d}. {n:8s}: ΔD={delta_D_diag[i]:+.4f}  "
          f"D_roam={D_roam[i,i]:.4f}  D_dwell={D_dwell[i,i]:.4f}")
    e21_up.append({"neuron": n, "delta_D": float(delta_D_diag[i]),
                   "D_roam": float(D_roam[i,i]), "D_dwell": float(D_dwell[i,i])})

print("  Top 10 DWELLING-dominant (most increased D in dwell):")
e21_down = []
for rank, i in enumerate(idx_sorted_down[:10]):
    n = NEURONS[i]
    print(f"  {rank+1:2d}. {n:8s}: ΔD={delta_D_diag[i]:+.4f}  "
          f"D_roam={D_roam[i,i]:.4f}  D_dwell={D_dwell[i,i]:.4f}")
    e21_down.append({"neuron": n, "delta_D": float(delta_D_diag[i]),
                     "D_roam": float(D_roam[i,i]), "D_dwell": float(D_dwell[i,i])})

# E2.3: ΔD vs ΔQ correlation per neuron
# For each neuron i, compare delta_D_diag[i] vs mean |ΔQ| of pairs involving i
ADEL = n2i["ADEL"]
mean_dq_per_neuron = np.zeros(N)
for k in range(N_C4):
    i, j = ii_c4[k], jj_c4[k]
    mean_dq_per_neuron[i] += abs_dq[k]
    mean_dq_per_neuron[j] += abs_dq[k]
pair_count = np.zeros(N, dtype=int)
for k in range(N_C4):
    pair_count[ii_c4[k]] += 1; pair_count[jj_c4[k]] += 1
mean_dq_per_neuron /= np.maximum(pair_count, 1)

rho_dD_dQ, p_dD_dQ = stats.spearmanr(delta_D_diag, mean_dq_per_neuron)
print(f"\nE2.3 — ρ(ΔD_ii, mean|ΔQ|_i) across neurons: {rho_dD_dQ:.4f} (p={p_dD_dQ:.4f})")
print("  (Positive = neurons with larger D increase in roaming also have larger ΔQ)")

# =============================================================================
# E3: Distance and Topology
# =============================================================================
print("\n"+"="*70); print("E3 — Distance and Topology")

# Build full connectome graph (undirected BFS distances)
conn_dir = DATA_DIR
graph: dict[str, set] = collections.defaultdict(set)
for fname in ["aconnectome_white_1986_A.csv",
              "aconnectome_witvliet_2020_7.csv",
              "aconnectome_witvliet_2020_8.csv"]:
    with open(conn_dir / fname) as f:
        reader = csv.reader(f, delimiter='\t'); next(reader)
        for row in reader:
            if len(row) < 4: continue
            pre, post = row[0].strip(), row[1].strip()
            try: w = int(row[3])
            except: w = 1
            if w >= 1 and pre != post:
                graph[pre].add(post); graph[post].add(pre)

conn_nodes = set(graph.keys())
neurons_61_in_conn = [n for n in NEURONS if n in conn_nodes]
print(f"  Connected neurons in 61-subgraph: {len(neurons_61_in_conn)}/61")

def bfs_distance(start: str, end: str, g: dict) -> int:
    """BFS shortest path in undirected graph. Returns -1 if unreachable."""
    if start not in g or end not in g: return -1
    if start == end: return 0
    visited = {start}; queue = collections.deque([(start, 0)])
    while queue:
        node, d = queue.popleft()
        for nb in g[node]:
            if nb == end: return d + 1
            if nb not in visited:
                visited.add(nb); queue.append((nb, d+1))
    return -1  # unreachable

# Pre-compute distances between all 61 neuron pairs
print("  Computing pairwise BFS distances ...")
dist_61 = np.full((N, N), -1, dtype=int)
for a, na in enumerate(NEURONS):
    for b, nb in enumerate(NEURONS):
        if a == b: dist_61[a,b] = 0
        elif a < b:
            d = bfs_distance(na, nb, graph)
            dist_61[a,b] = dist_61[b,a] = d

# Distances for Class 4 pairs
dist_c4 = np.array([dist_61[ii_c4[k], jj_c4[k]] for k in range(N_C4)])
reachable = dist_c4 >= 0
print(f"  C4 pairs with defined distance: {reachable.sum()}/{N_C4}")
print(f"  Distance distribution (reachable only): "
      f"mean={dist_c4[reachable].mean():.2f}  median={np.median(dist_c4[reachable]):.1f}  "
      f"max={dist_c4[reachable].max()}")

# E3.2: Compare distance distributions
# Groups: top-50 ΔQ, top-50 ΔΩ, top-50 high-R, zero-ΔQ-nonzero-ΔΩ ("Ω-only")
top50_dq_idx = set(np.argsort(-abs_dq)[:50])
top50_do_idx = set(np.argsort(-abs_do)[:50])
top50_R_idx  = set(top50_R)
omega_only   = np.where(is_zero_dq & (abs_do >= ZERO_THR))[0]  # zero ΔQ, nonzero ΔΩ

def dist_stats(indices, label, reachable_mask=None):
    if len(indices) == 0:
        print(f"  {label:25s}: no pairs"); return {}
    if isinstance(indices, set): indices = list(indices)
    ds = dist_c4[indices]
    reach = ds >= 0
    if reach.sum() == 0:
        print(f"  {label:25s}: no reachable pairs"); return {}
    d_reach = ds[reach]
    print(f"  {label:25s}: n={len(indices):4d}  reachable={reach.sum():4d}  "
          f"mean_dist={d_reach.mean():.2f}  median={np.median(d_reach):.1f}  "
          f"frac_dist2+={((d_reach >= 2).sum()/reach.sum()):.2f}  "
          f"frac_inf={(~reach).sum()/len(indices):.2f}")
    return {"n": len(indices), "n_reachable": int(reach.sum()),
            "mean_dist": float(d_reach.mean()), "median_dist": float(np.median(d_reach)),
            "frac_dist_ge2": float((d_reach>=2).sum()/reach.sum()),
            "frac_unreachable": float((~reach).sum()/len(indices))}

print("\nE3.2 — Distance distributions:")
e3 = {}
e3["all_C4"]    = dist_stats(list(range(N_C4)),   "All Class 4")
e3["top50_dq"]  = dist_stats(list(top50_dq_idx),  "Top-50 ΔQ")
e3["top50_do"]  = dist_stats(list(top50_do_idx),  "Top-50 ΔΩ")
e3["top50_R"]   = dist_stats(top50_R.tolist(),    "Top-50 disagreement R")
e3["omega_only"]= dist_stats(omega_only.tolist(), "Ω-only (ΔQ=0, ΔΩ≠0)")
e3["pdf_c4"]    = dist_stats(list(np.where(pdf_c4)[0]),  "PDF C4 pairs")
e3["nonpdf_c4"] = dist_stats(list(np.where(~pdf_c4)[0]), "Non-PDF C4 pairs")

# Statistical test: top-50 ΔΩ vs top-50 ΔQ distance
d_top50_do = dist_c4[list(top50_do_idx)]; d_top50_do = d_top50_do[d_top50_do>=0]
d_top50_dq = dist_c4[list(top50_dq_idx)]; d_top50_dq = d_top50_dq[d_top50_dq>=0]
if len(d_top50_do) > 0 and len(d_top50_dq) > 0:
    stat, pval = stats.mannwhitneyu(d_top50_do, d_top50_dq, alternative="two-sided")
    print(f"\n  Mann-Whitney U test top-50 ΔΩ vs top-50 ΔQ distances: p={pval:.4f}")
    e3["mannwhitney_do_vs_dq_p"] = float(pval)

# Ω-only vs top-50 ΔQ
d_oo = dist_c4[omega_only]; d_oo = d_oo[d_oo>=0]
if len(d_oo) > 0 and len(d_top50_dq) > 0:
    stat2, pval2 = stats.mannwhitneyu(d_oo, d_top50_dq, alternative="two-sided")
    print(f"  Mann-Whitney U test Ω-only vs top-50 ΔQ distances: p={pval2:.4f}")
    e3["mannwhitney_omegaonly_vs_dq_p"] = float(pval2)

# =============================================================================
# E4: Network Motif Analysis (conditional)
# =============================================================================
# Check if E1/E3 show clear signal: examine Ω-only pairs for motifs
print("\n"+"="*70); print("E4 — Network Motif Analysis")

# Build directed PDF graph sources/targets
pdf_sources = set(); pdf_targets = set()
with open(PEP_CSV) as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src==tgt: continue
        if "pdf" not in row[2].lower(): continue
        a, b = n2i[src], n2i[tgt]
        pdf_sources.add(a); pdf_targets.add(b)

# For Ω-only pairs: what fraction share a common source?
print(f"\nΩ-only pairs (ΔQ=0, ΔΩ≠0): {len(omega_only)}")

# Check motifs among top-100 Ω-only pairs by |ΔΩ|
omega_only_sorted = omega_only[np.argsort(-abs_do[omega_only])]
top100_omega_only = omega_only_sorted[:100]

# Common source motif: pairs (i,j) where i or j is a hub in D_emp
# Hub = neuron with many large off-diagonal D_emp entries
d_off = D_emp.copy(); np.fill_diagonal(d_off, 0)
hub_score = np.abs(d_off).sum(axis=1)   # sum of |off-diagonal D_emp| per neuron
top_hubs = np.argsort(-hub_score)[:10]
print(f"Top-10 D_emp hubs (by off-diagonal energy):")
for r, i in enumerate(top_hubs):
    print(f"  {r+1:2d}. {NEURONS[i]:8s}: off_diag_energy={hub_score[i]:.4f}")

# For Ω-only pairs: how many involve a top hub?
hub_set = set(top_hubs[:5])
n_hub_pairs = sum(1 for k in top100_omega_only
                  if ii_c4[k] in hub_set or jj_c4[k] in hub_set)
print(f"\nFraction of top-100 Ω-only pairs involving a top-5 D_emp hub: "
      f"{n_hub_pairs}/100 ({n_hub_pairs}%)")

# OU cascade motif: pairs (i,j) where i is a PDF source neuron
n_source_pairs = sum(1 for k in top100_omega_only
                     if ii_c4[k] in pdf_sources or jj_c4[k] in pdf_sources)
n_target_pairs = sum(1 for k in top100_omega_only
                     if ii_c4[k] in pdf_targets or jj_c4[k] in pdf_targets)
print(f"Fraction of top-100 Ω-only pairs involving a PDF source: {n_source_pairs}/100")
print(f"Fraction of top-100 Ω-only pairs involving a PDF target: {n_target_pairs}/100")

# Motif: feedforward chain (A→B in connectome, (A,C) is an Ω-only pair → B linked to C?)
# Check: for each Ω-only pair (i,j), is there a direct connectome path i→j?
n_directly_connected = sum(1 for k in top100_omega_only
                           if A_raw[ii_c4[k], jj_c4[k]])  # sanity: should be 0 (C4=off-connectome)
print(f"Ω-only pairs in top-100 that are on-connectome (sanity check): {n_directly_connected}")

# Are Ω-only pairs more common between neurons that share a connectome neighbor?
def share_neighbor(i, j, adj):
    ni = set(np.where(adj[i])[0])
    nj = set(np.where(adj[j])[0])
    return len(ni & nj) > 0

n_share = sum(1 for k in top100_omega_only
              if share_neighbor(ii_c4[k], jj_c4[k], A_raw))
n_share_c4 = sum(1 for k in range(min(100, N_C4))
                 if share_neighbor(ii_c4[k], jj_c4[k], A_raw))
print(f"Top-100 Ω-only pairs sharing a connectome neighbor: {n_share}/100")
print(f"Top-100 ΔQ pairs sharing a connectome neighbor (comparison): {n_share_c4}/100")

e4_data = {
    "n_omega_only": len(omega_only),
    "top5_D_emp_hubs": [NEURONS[i] for i in top_hubs[:5]],
    "n_hub_pairs_in_top100_omega_only": n_hub_pairs,
    "n_pdf_source_in_top100_omega_only": n_source_pairs,
    "n_pdf_target_in_top100_omega_only": n_target_pairs,
    "n_share_neighbor_top100_omega_only": n_share,
    "n_share_neighbor_top100_dq": n_share_c4,
}

# =============================================================================
# Save results
# =============================================================================
def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v = float(obj); return None if (v!=v or abs(v)==float("inf")) else v
    if isinstance(obj, float): return None if (obj!=obj or abs(obj)==float("inf")) else obj
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.bool_,)): return bool(obj)
    if isinstance(obj, np.ndarray): return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict): return {k: sanitize(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)): return [sanitize(v) for v in obj]
    return obj

import json as json_mod
output = {
    "date": "2026-06-03", "authorization": "Phase 3E",
    "E1_top50_R": top50_list[:50],
    "E1_R_by_annotation": e12,
    "E1_rho_R_DQ": float(rho_R_dq), "E1_rho_R_DO": float(rho_R_do),
    "E1_mean_R_zero_dq": float(R_zero.mean()),
    "E1_mean_R_nonzero_dq": float(R_nz.mean()),
    "E1_signed_R_pdf_mean": float(signed_R[pdf_c4].mean()),
    "E1_signed_R_nonpdf_mean": float(signed_R[~pdf_c4].mean()),
    "E2_top10_roam_dominant": e21_up,
    "E2_top10_dwell_dominant": e21_down,
    "E2_rho_deltaD_deltaQ": float(rho_dD_dQ),
    "E2_pval_deltaD_deltaQ": float(p_dD_dQ),
    "E3_distance": e3,
    "E4_motif": e4_data,
}
with open(OUT3E / "phase3e_results.json","w") as f:
    json_mod.dump(sanitize(output), f, indent=2)
print("\nSaved: phase3e_results.json")
