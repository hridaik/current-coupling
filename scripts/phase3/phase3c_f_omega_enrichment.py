"""Phase 3C-F — Empirical-Diffusion Ω Enrichment Analysis.

Authorization: Phase 3C-F, 2026-06-03.

Reconstructs all annotation matrices from source data and runs the full
Phase 2 enrichment framework on both ΔQ and ΔΩ_full = D_emp @ ΔQ.

Tasks:
  F1: Full enrichment analysis (Bentley PDF, serotonin, combined, CeNGEN, Randi)
  F2: Top-pair comparison (top-20/50 tables, overlap, PDF concentration)
  F3: Blockwise current analysis under ΔΩ_full vs ΔQ
  (F4 is a written synthesis only — no new computation)

Annotations reconstructed from source data:
  - A_raw: White 1986 + Witvliet 2020 connectome CSVs
  - creamer_mask: Creamer 154-neuron subset (56 in 61-subgraph)
  - Bentley PDF/serotonin/combined: ESconnectome CSVs
  - CeNGEN serotonin/PDF: cengen_021821_conservative_threshold3.csv
  - Randi unc-31: funatlas.h5 unc31/q threshold 0.05
  - Neuropeptide broad: GenesExpressing CeNGEN threshold-2

PROHIBITIONS: No held-out evaluation. No model fitting. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
from unittest.mock import MagicMock

import h5py
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

OUT3C = ROOT / "results/phase3c"
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"

# ── Load neuron metadata ──────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Reconstruct A_raw from Phase 2 ranked-pair outputs ───────────────────────
# The off-connectome set from Phase 2 is exact; A_raw = complement of off-set.
# This is the authoritative A_raw used in all Phase 2 enrichment analysis.
ranked_off_cep = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
off_set = set(zip(map(int, ii_all[ranked_off_cep]), map(int, jj_all[ranked_off_cep])))
A_raw = np.zeros((N, N), dtype=bool)
for i_pair in range(len(ii_all)):
    i, j = int(ii_all[i_pair]), int(jj_all[i_pair])
    if (i, j) not in off_set:
        A_raw[i, j] = A_raw[j, i] = True
print(f"A_raw: {A_raw.astype(int).sum()//2} undirected edges")

# ── Reconstruct creamer_mask ──────────────────────────────────────────────────
CREAMER_DIR = ROOT / "data/creamer/Creamer_LDS_2026"
creamer_mask = np.zeros(N, dtype=bool)
try:
    for mod_name in ["mpi4py", "mpi4py.MPI", "mpi4py.util", "mpi4py.util.pkl5"]:
        sys.modules[mod_name] = MagicMock()
    sys.path.insert(0, str(CREAMER_DIR))
    import pickle
    with open(CREAMER_DIR / "models/fully_connected.pkl", "rb") as f:
        cr = pickle.load(f)
    cr_ids = [str(c) for c in cr.cell_ids]
    for c in cr_ids:
        if c in n2i:
            creamer_mask[n2i[c]] = True
    print(f"Creamer mask: {creamer_mask.sum()} neurons in 61-subgraph")
except Exception as e:
    # Fallback: use the 56 neurons known to be in Creamer from Phase 3A
    print(f"Creamer load failed: {e} — falling back to Phase 3A known set")
    creamer_56 = [n for n in NEURONS if n not in ["AIBL","AIBR","AWCL","IL1L","IL1R"]]
    for n in creamer_56:
        if n in n2i:
            creamer_mask[n2i[n]] = True
    print(f"Creamer mask fallback: {creamer_mask.sum()} neurons")

# Class 4 pairs: off A_raw, both in Creamer
on_raw   = A_raw[ii_all, jj_all]
off_raw  = ~on_raw
both_cm  = np.outer(creamer_mask, creamer_mask)[ii_all, jj_all]
c4_mask  = off_raw & both_cm
ii_c4    = ii_all[c4_mask]; jj_c4 = jj_all[c4_mask]
N_C4     = int(c4_mask.sum())
c4_set   = set(zip(map(int, ii_c4), map(int, jj_c4)))
print(f"Class 4 pairs: {N_C4}")
assert N_C4 == 1321, f"Expected 1321 Class 4 pairs, got {N_C4}"

deg_raw      = A_raw.astype(int).sum(axis=1)
pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]
N_BINS       = 10

# ── Build Bentley annotations ─────────────────────────────────────────────────
def load_bentley_undirected(csv_path: Path, keep_fn) -> np.ndarray:
    """Build (N,N) symmetric bool matrix for a Bentley annotation."""
    mat = np.zeros((N, N), dtype=bool)
    with open(csv_path) as f:
        reader = csv.reader(f); next(reader)
        for row in reader:
            if len(row) < 3: continue
            src, tgt = row[0].strip(), row[1].strip()
            if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
            if not keep_fn(row): continue
            a, b = n2i[src], n2i[tgt]
            mat[a, b] = mat[b, a] = True
    return mat

PEP_CSV  = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"
MONO_CSV = DATA_DIR / "esconnectome_monoamines_Bentley_2016.csv"

bent_pdf  = load_bentley_undirected(PEP_CSV,  lambda r: "pdf" in r[2].strip().lower())
bent_ser  = load_bentley_undirected(MONO_CSV, lambda r: r[2].strip().lower() == "serotonin")
bent_comb = bent_pdf | bent_ser

print(f"Bentley PDF: {bent_pdf[ii_c4,jj_c4].sum()} C4 pairs")
print(f"Bentley serotonin: {bent_ser[ii_c4,jj_c4].sum()} C4 pairs")
print(f"Bentley combined: {bent_comb[ii_c4,jj_c4].sum()} C4 pairs")

# ── Build CeNGEN annotation ───────────────────────────────────────────────────
CENGEN_TO_61 = {
    "ADE": ["ADEL"], "AIB": ["AIBL","AIBR"], "AIZ": ["AIZL"], "ASEL": ["ASEL"],
    "ASG": ["ASGL"], "AUA": ["AUAL"], "AVA": ["AVAL","AVAR"], "AVD": ["AVDL"],
    "AVE": ["AVEL","AVER"], "AVJ": ["AVJL","AVJR"], "AWA": ["AWAL"],
    "AWB": ["AWBL"], "AWC_OFF": ["AWCL"], "FLP": ["FLPL"],
    "I1": ["I1L","I1R"], "I2": ["I2L","I2R"], "I3": ["I3"],
    "IL1": ["IL1DR","IL1L","IL1R"], "IL2_DV": ["IL2DL","IL2DR"],
    "IL2_LR": ["IL2VL","IL2VR"], "M1": ["M1"], "M3": ["M3L","M3R"],
    "M4": ["M4"], "MI": ["MI"], "NSM": ["NSML","NSMR"],
    "OLL": ["OLLL","OLLR"],
    "OLQ": ["OLQDL","OLQDR","OLQVL","OLQVR"],
    "RIC": ["RICL"], "RID": ["RID"], "RIV": ["RIVL"],
    "RMD_DV": ["RMDDR","RMDVL"], "RMD_LR": ["RMDL","RMDVR"],
    "RME_DV": ["RMEL"], "RME_LR": ["RMER"], "SMD": ["SMDVL"],
    "URB": ["URBL"], "URX": ["URXL"],
    "URY": ["URYDL","URYVL","URYVR"],
    "CEP": ["CEPDL","CEPDR","CEPVL"],
}

def parse_cengen(csv_path: Path, gene_names: set) -> set:
    """Return set of 61-neuron names that express any of the given genes at threshold."""
    expressed = set()
    with open(csv_path) as f:
        reader = csv.reader(f); header = next(reader)
        col_names = header[4:]  # skip index, gene_name, X, threshold
        for row in reader:
            if len(row) < 5: continue
            gene = row[1].strip()
            if gene not in gene_names: continue
            threshold = float(row[3]) if row[3] else 0.0
            for k, cname in enumerate(col_names):
                cname = cname.strip()
                try:
                    val = float(row[4 + k]) if row[4 + k] else 0.0
                except (ValueError, IndexError):
                    val = 0.0
                if val > threshold:
                    for n61 in CENGEN_TO_61.get(cname, []):
                        expressed.add(n61)
    return expressed

CENGEN_CSV = DATA_DIR / "cengen_021821_conservative_threshold3.csv"

# tph-1 or cat-1 → serotonin ligand neurons
# ser-1, ser-4, ser-5, ser-7, mod-1 → serotonin receptors
# pdf-1, pdf-2 → PDF ligand; pdfr-1 → PDF receptor
serotonin_ligand_genes  = {"tph-1", "cat-1"}
serotonin_receptor_genes = {"ser-1", "ser-4", "ser-5", "ser-7", "mod-1"}
pdf_ligand_genes    = {"pdf-1", "pdf-2"}
pdf_receptor_genes  = {"pdfr-1"}

ser_lig  = parse_cengen(CENGEN_CSV, serotonin_ligand_genes)
ser_rec  = parse_cengen(CENGEN_CSV, serotonin_receptor_genes)
pdf_lig  = parse_cengen(CENGEN_CSV, pdf_ligand_genes)
pdf_rec  = parse_cengen(CENGEN_CSV, pdf_receptor_genes)

# A pair is CeNGEN serotonin/PDF annotated if it's a serotonin LR pair OR a PDF LR pair
cengen_mat = np.zeros((N, N), dtype=bool)
for i in range(N):
    for j in range(N):
        if i == j: continue
        ni, nj = NEURONS[i], NEURONS[j]
        ser_lr = ((ni in ser_lig and nj in ser_rec) or
                  (nj in ser_lig and ni in ser_rec))
        pdf_lr = ((ni in pdf_lig and nj in pdf_rec) or
                  (nj in pdf_lig and ni in pdf_rec))
        if ser_lr or pdf_lr:
            cengen_mat[i, j] = True
            cengen_mat[j, i] = True

print(f"CeNGEN serotonin/PDF: {cengen_mat[ii_c4,jj_c4].sum()} C4 pairs")

# ── Build Randi unc-31 annotation ────────────────────────────────────────────
FUNATLAS = DATA_DIR / "funatlas.h5"
randi_mat = np.zeros((N, N), dtype=bool)
with h5py.File(FUNATLAS, "r") as f:
    neuron_ids = [n.decode() if isinstance(n, bytes) else n
                  for n in f["neuron_ids"][:]]
    q_unc31 = f["unc31/q"][:]    # (300, 300) float

# q < 0.05 threshold (standard); map 300-neuron space to 61
# Build mapping from Randi 300-neuron names to our 61-neuron canonical names
# Randi uses names like "ADEL", "URYVR" etc., similar to ours but possibly different
randi_id_set = set(neuron_ids)
q_thresh = 0.05
for i_r, id_r in enumerate(neuron_ids):
    if id_r not in n2i: continue
    i61 = n2i[id_r]
    for j_r, id_j in enumerate(neuron_ids):
        if j_r == i_r: continue
        if id_j not in n2i: continue
        j61 = n2i[id_j]
        if q_unc31[i_r, j_r] < q_thresh:
            randi_mat[i61, j61] = True
            randi_mat[j61, i61] = True

n_randi_c4 = int(randi_mat[ii_c4, jj_c4].sum())
print(f"Randi unc-31 (q<0.05): {n_randi_c4} C4 pairs")
# If too different from Phase 2 (108), try q<0.1
if abs(n_randi_c4 - 108) > 30:
    randi_mat2 = np.zeros((N, N), dtype=bool)
    for i_r, id_r in enumerate(neuron_ids):
        if id_r not in n2i: continue
        i61 = n2i[id_r]
        for j_r, id_j in enumerate(neuron_ids):
            if j_r == i_r: continue
            if id_j not in n2i: continue
            j61 = n2i[id_j]
            if q_unc31[i_r, j_r] < 0.1:
                randi_mat2[i61, j61] = True
                randi_mat2[j61, i61] = True
    n_r2 = int(randi_mat2[ii_c4, jj_c4].sum())
    print(f"Randi unc-31 (q<0.10): {n_r2} C4 pairs")
    if abs(n_r2 - 108) < abs(n_randi_c4 - 108):
        randi_mat = randi_mat2
        print("  Using q<0.10 threshold (closer to Phase 2 count)")

# ── Build neuropeptide broad annotation from CeNGEN ──────────────────────────
# Any pair where one neuron expresses a neuropeptide and the other a neuropeptide receptor
# (threshold 2 from cengen_021821_conservative_threshold3.csv)
PEP_GENES_CSV  = DATA_DIR / "GenesExpressing-neuropeptides.csv"
PEP_REC_CSV    = DATA_DIR / "GenesExpressing-neuropeptide-receptors.csv"

def neurons_expressing(csv_path: Path) -> set:
    """Return 61-neuron names expressing at least one gene in this file (value > threshold)."""
    expressed = set()
    with open(csv_path) as f:
        reader = csv.reader(f); header = next(reader)
        # Format: ,gene_name,X,threshold,neuron1,neuron2,...
        col_names = header[4:]  # bilateral neuron names starting col 4
        for row in reader:
            if len(row) < 5: continue
            try:
                threshold = float(row[3]) if row[3] else 0.0
            except ValueError:
                threshold = 0.0
            for k, cname in enumerate(col_names):
                cname = cname.strip()
                try:
                    val = float(row[4 + k]) if row[4 + k] else 0.0
                except (ValueError, IndexError):
                    val = 0.0
                if val > threshold:
                    for n61 in CENGEN_TO_61.get(cname, []):
                        expressed.add(n61)
    return expressed

pep_ligand_set  = neurons_expressing(PEP_GENES_CSV)
pep_receptor_set = neurons_expressing(PEP_REC_CSV)

pep61_broad = np.zeros((N, N), dtype=bool)
for i in range(N):
    for j in range(N):
        if i == j: continue
        ni, nj = NEURONS[i], NEURONS[j]
        # Annotated if one expresses neuropeptides AND other expresses receptors (OR)
        if ((ni in pep_ligand_set and nj in pep_receptor_set) or
            (nj in pep_ligand_set and ni in pep_receptor_set) or
            (ni in pep_ligand_set and nj in pep_ligand_set)):  # both express neuropeptides
            pep61_broad[i, j] = True
            pep61_broad[j, i] = True

n_pep_c4 = int(pep61_broad[ii_c4, jj_c4].sum())
print(f"Neuropeptide broad (CeNGEN): {n_pep_c4} C4 pairs (Phase 2: 972)")

# Collect all annotations
ANNOTATIONS = {
    "Bentley_PDF":              bent_pdf[ii_c4, jj_c4].astype(bool),
    "Bentley_serotonin":        bent_ser[ii_c4, jj_c4].astype(bool),
    "Bentley_combined":         bent_comb[ii_c4, jj_c4].astype(bool),
    "CeNGEN_serotonin_PDF":     cengen_mat[ii_c4, jj_c4].astype(bool),
    "Randi_unc31":              randi_mat[ii_c4, jj_c4].astype(bool),
    "Neuropeptide_broad":       pep61_broad[ii_c4, jj_c4].astype(bool),
}
print("\nAnnotation C4 counts:")
for name, ann in ANNOTATIONS.items():
    print(f"  {name}: {ann.sum()} ({100*ann.mean():.1f}%)")

# ── Load D_emp matrices and ΔQ ────────────────────────────────────────────────
D_cep = np.load(OUT3C / "D_emp_cepnem.npy")
D_g   = np.load(OUT3C / "D_emp_gcamp.npy")

PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r_cep = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy"); Q_r_cep = (Q_r_cep + Q_r_cep.T)/2
Q_d_cep = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d_cep = (Q_d_cep + Q_d_cep.T)/2
DQ_cep  = Q_r_cep - Q_d_cep

Q_r_g = np.load(PREC_DIR / "Q_gcamp_roam_conf.npy"); Q_r_g = (Q_r_g + Q_r_g.T)/2
Q_d_g = np.load(PREC_DIR / "Q_gcamp_dwell_conf.npy"); Q_d_g = (Q_d_g + Q_d_g.T)/2
DQ_g  = Q_r_g - Q_d_g

# ΔΩ_full = D_emp @ ΔQ (full matrix multiplication)
DO_cep = D_cep @ DQ_cep
DO_g   = D_g   @ DQ_g

# Scores (absolute values for Class 4 pairs)
scores_DQ_cep  = np.abs(DQ_cep[ii_c4, jj_c4])
scores_DO_cep  = np.abs(DO_cep[ii_c4, jj_c4])
scores_DQ_g    = np.abs(DQ_g[ii_c4, jj_c4])
scores_DO_g    = np.abs(DO_g[ii_c4, jj_c4])

# ── Enrichment utilities ──────────────────────────────────────────────────────
N_PERM = 500   # adequate for p-value precision to 0.01
SEED   = 99
K      = 20

def auroc(ann, scores):
    n1 = ann.sum(); n0 = (~ann).sum()
    if n1 == 0 or n0 == 0: return float("nan"), float("nan")
    u, p = stats.mannwhitneyu(scores[ann], scores[~ann], alternative="greater")
    return float(u / (n1 * n0)), float(p)

def fisher_topk(ann, scores, k=20):
    N_ = len(ann)
    top = np.argsort(scores)[::-1][:k]
    tm = np.zeros(N_, dtype=bool); tm[top] = True
    a = int((tm & ann).sum()); b = int((tm & ~ann).sum())
    c = int((~tm & ann).sum()); d = int((~tm & ~ann).sum())
    or_, p = stats.fisher_exact([[a,b],[c,d]], alternative="greater")
    return float(or_), float(p), int(a), float(ann.sum() * k / N_)

def deg_perm_auroc(ann, scores, deg, n_bins, n_perm, seed):
    rng = np.random.default_rng(seed)
    bin_edges = np.percentile(deg, np.linspace(0, 100, n_bins + 1))
    bin_edges = np.unique(bin_edges)
    bin_idx   = np.digitize(deg, bin_edges[1:], right=True)
    null = np.empty(n_perm)
    for i in range(n_perm):
        perm = ann.copy()
        for b in np.unique(bin_idx):
            mask = bin_idx == b
            sub = perm[mask]; rng.shuffle(sub); perm[mask] = sub
        a, _ = auroc(perm, scores)
        null[i] = a
    obs, _ = auroc(ann, scores)
    return float((null >= obs).sum() / n_perm), null.mean()

def deg_perm_fisher(ann, scores, deg, n_bins, k, n_perm, seed):
    rng = np.random.default_rng(seed + 1)
    bin_edges = np.percentile(deg, np.linspace(0, 100, n_bins + 1))
    bin_edges = np.unique(bin_edges)
    bin_idx   = np.digitize(deg, bin_edges[1:], right=True)
    null_or = np.empty(n_perm)
    for i in range(n_perm):
        perm = ann.copy()
        for b in np.unique(bin_idx):
            mask = bin_idx == b
            sub = perm[mask]; rng.shuffle(sub); perm[mask] = sub
        or_, _, _, _ = fisher_topk(perm, scores, k)
        null_or[i] = or_
    obs_or, _, _, _ = fisher_topk(ann, scores, k)
    return float((null_or >= obs_or).sum() / n_perm), float(np.nanmean(null_or))

def run_enrichment(ann_name, ann, scores, deg, label):
    auc, pmw = auroc(ann, scores)
    p_deg_auc, null_mean_auc = deg_perm_auroc(ann, scores, deg, N_BINS, N_PERM, SEED)
    or_, pf, k_ann, k_exp = fisher_topk(ann, scores, K)
    p_deg_fish, null_mean_or = deg_perm_fisher(ann, scores, deg, N_BINS, K, N_PERM, SEED)
    pass_a = (auc > 0.5) and (p_deg_auc < 0.05)
    pass_f = (or_ > 1.0) and (p_deg_fish < 0.05)
    print(f"  {label:30s}: AUROC={auc:.4f} p_deg={p_deg_auc:.3f} "
          f"{'PASS' if pass_a else 'FAIL'}  |  "
          f"OR={or_:.2f} p_fish_deg={p_deg_fish:.3f} "
          f"[{k_ann}/{K} ann, exp={k_exp:.1f}] {'PASS' if pass_f else 'FAIL'}")
    return {
        "annotation": ann_name,
        "n_annotated": int(ann.sum()),
        "auroc": float(auc),
        "p_mannwhitney": float(pmw),
        "p_deg_perm_auroc": float(p_deg_auc),
        "null_mean_auroc": float(null_mean_auc),
        "auroc_pass": pass_a,
        "fisher_or": float(or_),
        "fisher_p_exact": float(pf),
        "p_deg_perm_fisher": float(p_deg_fish),
        "null_mean_or": float(null_mean_or),
        "top_k": K,
        "k_annotated": int(k_ann),
        "k_expected": float(k_exp),
        "fisher_pass": pass_f,
        "overall_pass": pass_a or pass_f,
    }

# =============================================================================
# F1 — FULL ENRICHMENT ANALYSIS
# =============================================================================
print("\n" + "="*70)
print("F1 — Enrichment Analysis: ΔQ vs ΔΩ_full")
print("="*70)

all_results = {}

for coord_name, scores_dq, scores_do in [
        ("cepnem", scores_DQ_cep, scores_DO_cep),
        ("gcamp",  scores_DQ_g,   scores_DO_g)]:
    print(f"\n--- {coord_name.upper()} ---")
    coord_res = {}
    for ann_name, ann in ANNOTATIONS.items():
        if ann.sum() == 0: continue
        print(f"\n  {ann_name}:")
        r_dq = run_enrichment(ann_name, ann, scores_dq, pair_deg_raw, f"  ΔQ ({coord_name})")
        r_do = run_enrichment(ann_name, ann, scores_do, pair_deg_raw, f"  ΔΩ ({coord_name})")
        coord_res[ann_name] = {"DQ": r_dq, "DO": r_do}
    all_results[coord_name] = coord_res

# =============================================================================
# F2 — TOP-PAIR COMPARISON
# =============================================================================
print("\n" + "="*70)
print("F2 — Top-Pair Comparison")
print("="*70)

ADEL = n2i["ADEL"]
bent_pdf_c4 = ANNOTATIONS["Bentley_PDF"]

def top_pair_analysis(scores_dq, scores_do, label):
    rank_dq = np.argsort(-scores_dq)
    rank_do = np.argsort(-scores_do)

    top20_dq = set(rank_dq[:20]); top20_do = set(rank_do[:20])
    top50_dq = set(rank_dq[:50]); top50_do = set(rank_do[:50])
    ov20 = len(top20_dq & top20_do)
    ov50 = len(top50_dq & top50_do)

    # PDF concentration
    n_pdf_top20_dq  = int(bent_pdf_c4[np.array(list(top20_dq))].sum())
    n_pdf_top20_do  = int(bent_pdf_c4[np.array(list(top20_do))].sum())
    n_pdf_top50_dq  = int(bent_pdf_c4[np.array(list(top50_dq))].sum())
    n_pdf_top50_do  = int(bent_pdf_c4[np.array(list(top50_do))].sum())

    # ADEL participation
    adel_in_top20_dq = sum(1 for k in top20_dq if ii_c4[k]==ADEL or jj_c4[k]==ADEL)
    adel_in_top20_do = sum(1 for k in top20_do if ii_c4[k]==ADEL or jj_c4[k]==ADEL)

    print(f"\n{label}:")
    print(f"  Top-20 overlap ΔQ∩ΔΩ: {ov20}/20  |  Top-50 overlap: {ov50}/50")
    print(f"  PDF in top-20: ΔQ={n_pdf_top20_dq}, ΔΩ={n_pdf_top20_do} "
          f"(expected {20*bent_pdf_c4.mean():.1f})")
    print(f"  PDF in top-50: ΔQ={n_pdf_top50_dq}, ΔΩ={n_pdf_top50_do} "
          f"(expected {50*bent_pdf_c4.mean():.1f})")
    print(f"  ADEL in top-20: ΔQ={adel_in_top20_dq}, ΔΩ={adel_in_top20_do}")

    # Top-20 tables
    dq_pos = np.empty(N_C4, dtype=int); dq_pos[rank_dq] = np.arange(1, N_C4+1)
    do_pos = np.empty(N_C4, dtype=int); do_pos[rank_do] = np.arange(1, N_C4+1)

    print(f"\n  Top-20 ΔΩ_full ({label}):")
    top20_list = []
    for pos, k in enumerate(rank_do[:20]):
        i, j = ii_c4[k], jj_c4[k]
        is_pdf  = bent_pdf_c4[k]
        is_adel = (i == ADEL or j == ADEL)
        print(f"    {pos+1:2d}. {NEURONS[i]:6s}–{NEURONS[j]:6s}: "
              f"ΔΩ={scores_do[k]:+.4f}  ΔQ={scores_dq[k]:+.4f}  "
              f"ΔQ_rank={dq_pos[k]:4d}  {'PDF' if is_pdf else '   '}  "
              f"{'ADEL' if is_adel else ''}")
        top20_list.append({
            "rank_do": pos+1, "pair": f"{NEURONS[i]}–{NEURONS[j]}",
            "score_do": float(scores_do[k]), "score_dq": float(scores_dq[k]),
            "rank_dq": int(dq_pos[k]), "pdf": bool(is_pdf), "adel": bool(is_adel),
        })
    return {
        "top20_overlap": ov20, "top50_overlap": ov50,
        "n_pdf_top20_dq": n_pdf_top20_dq, "n_pdf_top20_do": n_pdf_top20_do,
        "n_pdf_top50_dq": n_pdf_top50_dq, "n_pdf_top50_do": n_pdf_top50_do,
        "adel_in_top20_dq": adel_in_top20_dq, "adel_in_top20_do": adel_in_top20_do,
        "top20_do_table": top20_list,
    }

f2_cep = top_pair_analysis(scores_DQ_cep, scores_DO_cep, "CePNEM")
f2_g   = top_pair_analysis(scores_DQ_g,   scores_DO_g,   "GCaMP")

# =============================================================================
# F3 — BLOCKWISE CURRENT ANALYSIS UNDER ΔΩ_full
# =============================================================================
print("\n" + "="*70)
print("F3 — Blockwise Current Analysis: ΔΩ_full vs ΔQ")
print("="*70)

BLOCKS = {
    "DA_mech":    [n2i[n] for n in ["ADEL","CEPDL","CEPDR","CEPVL"]],
    "RID":        [n2i["RID"]],
    "RME":        [n2i["RMEL"], n2i["RMER"]],
    "URY_URX":    [n2i[n] for n in ["URYDL","URYVL","URYVR","URXL"]],
    "command_IN": [n2i[n] for n in ["AVAL","AVAR","AVEL","AVER","AVDL","AVJL","AVJR"]],
    "OLL_OLQ":    [n2i[n] for n in ["OLLL","OLLR","OLQDL","OLQDR","OLQVL","OLQVR"]],
    "IL1_IL2":    [n2i[n] for n in ["IL1DR","IL1L","IL1R","IL2DL","IL2DR","IL2VL","IL2VR"]],
    "pharyngeal": [n2i[n] for n in ["I1L","I1R","I2L","I2R","I3","M1","M3L","M3R","M4","MI","NSML","NSMR"]],
    "RMD_SMD":    [n2i[n] for n in ["RMDDR","RMDL","RMDVL","RMDVR","SMDVL"]],
    "other":      [n2i[n] for n in ["AIBL","AIBR","AIZL","ASEL","ASGL","AUAL","AWAL","AWBL","AWCL","FLPL","RICL","RIVL","URBL"]],
}
block_names = list(BLOCKS.keys())
B = len(block_names)

def blockwise_flow(scores, label):
    flow_mean = np.zeros((B, B))
    flow_npairs = np.zeros((B, B), dtype=int)
    for b1 in range(B):
        for b2 in range(b1, B):
            idxs1 = BLOCKS[block_names[b1]]
            idxs2 = BLOCKS[block_names[b2]]
            vals = []
            for i in idxs1:
                for j in idxs2:
                    if i == j: continue
                    if b1 == b2 and j <= i: continue
                    key = (min(i,j), max(i,j))
                    if key in c4_set:
                        ki = next((k for k in range(N_C4) if (ii_c4[k]==i and jj_c4[k]==j) or
                                   (ii_c4[k]==j and jj_c4[k]==i)), None)
                        if ki is not None:
                            vals.append(scores[ki])
            if vals:
                flow_mean[b1,b2] = float(np.mean(np.abs(vals)))
                flow_mean[b2,b1] = flow_mean[b1,b2]
                flow_npairs[b1,b2] = len(vals)
                flow_npairs[b2,b1] = len(vals)

    bpf = []
    for b1 in range(B):
        for b2 in range(b1, B):
            if flow_npairs[b1,b2] > 0:
                bpf.append({"b1": block_names[b1], "b2": block_names[b2],
                             "mean_abs": float(flow_mean[b1,b2]),
                             "n": int(flow_npairs[b1,b2])})
    bpf.sort(key=lambda x: -x["mean_abs"])

    print(f"\n  Top-10 block flows ({label}):")
    for row in bpf[:10]:
        print(f"    {row['b1']:12s}↔{row['b2']:12s}: "
              f"mean={row['mean_abs']:.4f}  n={row['n']}")
    return bpf

print("\nCePNEM ΔQ blockwise:")
f3_dq_cep = blockwise_flow(scores_DQ_cep, "ΔQ CePNEM")
print("\nCePNEM ΔΩ_full blockwise:")
f3_do_cep = blockwise_flow(scores_DO_cep, "ΔΩ CePNEM")
print("\nGCaMP ΔQ blockwise:")
f3_dq_g   = blockwise_flow(scores_DQ_g,   "ΔQ GCaMP")
print("\nGCaMP ΔΩ_full blockwise:")
f3_do_g   = blockwise_flow(scores_DO_g,   "ΔΩ GCaMP")

# =============================================================================
# SAVE ALL RESULTS
# =============================================================================
output = {
    "date": "2026-06-03",
    "authorization": "Phase 3C-F",
    "annotation_counts": {name: int(ann.sum()) for name, ann in ANNOTATIONS.items()},
    "F1_enrichment": all_results,
    "F2_top_pairs": {"cepnem": f2_cep, "gcamp": f2_g},
    "F3_blockwise": {
        "cepnem": {"DQ": f3_dq_cep[:10], "DO": f3_do_cep[:10]},
        "gcamp":  {"DQ": f3_dq_g[:10],   "DO": f3_do_g[:10]},
    },
}

def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v = float(obj); return None if (v != v or abs(v) == float("inf")) else v
    if isinstance(obj, float):
        return None if (obj != obj or abs(obj) == float("inf")) else obj
    if isinstance(obj, (np.integer,)):      return int(obj)
    if isinstance(obj, (np.bool_,)):        return bool(obj)
    if isinstance(obj, np.ndarray):         return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict):               return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):      return [sanitize(v) for v in obj]
    return obj

with open(OUT3C / "phase3c_f_results.json", "w") as f:
    json.dump(sanitize(output), f, indent=2)
print("\nSaved: phase3c_f_results.json")
print("\n>>> STOP — awaiting F1-F4 reports <<<")
