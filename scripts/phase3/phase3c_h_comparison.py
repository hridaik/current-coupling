"""Phase 3C-H — Comprehensive Ω vs Q Comparison.

Authorization: Phase 3C-H, 2026-06-03.

Computes H1 Fisher, H2 ADEL analysis, H3 blockwise, H4 sparsity audit,
H5 localization. Reuses D_emp, DQ, and annotation data from prior phases.

PROHIBITIONS: No new fitting. No held-out evaluation. No perturbation predictions.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT3C = ROOT / "results/phase3c"

# ── Metadata ──────────────────────────────────────────────────────────────────
with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)
ii_all, jj_all = np.triu_indices(N, k=1)

# ── Class 4 pairs ──────────────────────────────────────────────────────────────
ranked_c4 = np.load(ROOT / "results/phase2/stage2/ranked_class4_cepnem.npy")
ii_c4 = ii_all[ranked_c4]; jj_c4 = jj_all[ranked_c4]
N_C4 = len(ranked_c4)
c4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

# A_raw reconstruction from off-set
ranked_off = np.load(ROOT / "results/phase2/stage2/ranked_off_cepnem.npy")
off_set = set(zip(map(int, ii_all[ranked_off]), map(int, jj_all[ranked_off])))
A_raw = np.zeros((N, N), dtype=bool)
for k in range(len(ii_all)):
    i, j = int(ii_all[k]), int(jj_all[k])
    if (i, j) not in off_set:
        A_raw[i, j] = A_raw[j, i] = True
deg_raw = A_raw.astype(int).sum(axis=1)
pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]
N_BINS = 10; K = 20; N_PERM = 500; SEED = 123

# ── ΔQ and ΔΩ_full ────────────────────────────────────────────────────────────
PREC_DIR = ROOT / "results/phase2/stage1/precision"
Q_r = np.load(PREC_DIR / "Q_cepnem_roam_conf.npy");  Q_r = (Q_r + Q_r.T)/2
Q_d = np.load(PREC_DIR / "Q_cepnem_dwell_conf.npy"); Q_d = (Q_d + Q_d.T)/2
DQ  = Q_r - Q_d
D_emp = np.load(OUT3C / "D_emp_cepnem.npy")
DO    = D_emp @ DQ
dq_c4 = np.abs(DQ[ii_c4, jj_c4])
do_c4 = np.abs(DO[ii_c4, jj_c4])

# ── Annotations ───────────────────────────────────────────────────────────────
DATA_DIR = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"

def load_bentley(csv_path, keep_fn):
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

CENGEN_TO_61 = {
    "ADE":["ADEL"],"AIB":["AIBL","AIBR"],"AIZ":["AIZL"],"ASEL":["ASEL"],
    "ASG":["ASGL"],"AUA":["AUAL"],"AVA":["AVAL","AVAR"],"AVD":["AVDL"],
    "AVE":["AVEL","AVER"],"AVJ":["AVJL","AVJR"],"AWA":["AWAL"],"AWB":["AWBL"],
    "AWC_OFF":["AWCL"],"FLP":["FLPL"],"I1":["I1L","I1R"],"I2":["I2L","I2R"],
    "I3":["I3"],"IL1":["IL1DR","IL1L","IL1R"],"IL2_DV":["IL2DL","IL2DR"],
    "IL2_LR":["IL2VL","IL2VR"],"M1":["M1"],"M3":["M3L","M3R"],"M4":["M4"],
    "MI":["MI"],"NSM":["NSML","NSMR"],"OLL":["OLLL","OLLR"],
    "OLQ":["OLQDL","OLQDR","OLQVL","OLQVR"],"RIC":["RICL"],"RID":["RID"],
    "RIV":["RIVL"],"RMD_DV":["RMDDR","RMDVL"],"RMD_LR":["RMDL","RMDVR"],
    "RME_DV":["RMEL"],"RME_LR":["RMER"],"SMD":["SMDVL"],"URB":["URBL"],
    "URX":["URXL"],"URY":["URYDL","URYVL","URYVR"],"CEP":["CEPDL","CEPDR","CEPVL"],
}

def parse_cengen_expressed(csv_path, genes):
    expressed = set()
    with open(csv_path) as f:
        reader = csv.reader(f); header = next(reader)
        col_names = header[4:]
        for row in reader:
            if len(row) < 5: continue
            gene = row[1].strip()
            if gene not in genes: continue
            try: thr = float(row[3]) if row[3] else 0.0
            except: thr = 0.0
            for k, cname in enumerate(col_names):
                cname = cname.strip()
                try: val = float(row[4+k]) if row[4+k] else 0.0
                except: val = 0.0
                if val > thr:
                    for n61 in CENGEN_TO_61.get(cname, []):
                        expressed.add(n61)
    return expressed

CENGEN_CSV = DATA_DIR / "cengen_021821_conservative_threshold3.csv"
ser_lig = parse_cengen_expressed(CENGEN_CSV, {"tph-1","cat-1"})
ser_rec = parse_cengen_expressed(CENGEN_CSV, {"ser-1","ser-4","ser-5","ser-7","mod-1"})
pdf_lig = parse_cengen_expressed(CENGEN_CSV, {"pdf-1","pdf-2"})
pdf_rec = parse_cengen_expressed(CENGEN_CSV, {"pdfr-1"})
cengen_mat = np.zeros((N, N), dtype=bool)
for i in range(N):
    for j in range(N):
        if i == j: continue
        ni, nj = NEURONS[i], NEURONS[j]
        if ((ni in ser_lig and nj in ser_rec) or (nj in ser_lig and ni in ser_rec) or
            (ni in pdf_lig and nj in pdf_rec) or (nj in pdf_lig and ni in pdf_rec)):
            cengen_mat[i,j] = cengen_mat[j,i] = True

import h5py
randi_mat = np.zeros((N, N), dtype=bool)
with h5py.File(DATA_DIR / "funatlas.h5", "r") as f:
    neuron_ids = [n.decode() if isinstance(n, bytes) else n for n in f["neuron_ids"][:]]
    q_unc31 = f["unc31/q"][:]
for i_r, id_r in enumerate(neuron_ids):
    if id_r not in n2i: continue
    i61 = n2i[id_r]
    for j_r, id_j in enumerate(neuron_ids):
        if j_r == i_r or id_j not in n2i: continue
        j61 = n2i[id_j]
        if q_unc31[i_r, j_r] < 0.10:
            randi_mat[i61, j61] = randi_mat[j61, i61] = True

PEP_CSV = DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv"
MONO_CSV = DATA_DIR / "esconnectome_monoamines_Bentley_2016.csv"
bent_pdf  = load_bentley(PEP_CSV,  lambda r: "pdf" in r[2].strip().lower())
bent_ser  = load_bentley(MONO_CSV, lambda r: r[2].strip().lower() == "serotonin")
bent_comb = bent_pdf | bent_ser

# PDF directed sources
pdf_sources: set = set(); pdf_targets: set = set()
with open(PEP_CSV) as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt = row[0].strip(), row[1].strip()
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        if "pdf" not in row[2].strip().lower(): continue
        a, b = n2i[src], n2i[tgt]
        if (min(a,b), max(a,b)) in c4_set:
            pdf_sources.add(a); pdf_targets.add(b)

ANNOTATIONS = {
    "Bentley_PDF":     bent_pdf[ii_c4, jj_c4].astype(bool),
    "Bentley_serotonin": bent_ser[ii_c4, jj_c4].astype(bool),
    "Bentley_combined":  bent_comb[ii_c4, jj_c4].astype(bool),
    "CeNGEN_ser_PDF":  cengen_mat[ii_c4, jj_c4].astype(bool),
    "Randi_unc31":     randi_mat[ii_c4, jj_c4].astype(bool),
}

# ── Enrichment utilities ──────────────────────────────────────────────────────
def auroc(ann, scores):
    n1=ann.sum(); n0=(~ann).sum()
    if n1==0 or n0==0: return float("nan"), float("nan")
    u, p = stats.mannwhitneyu(scores[ann], scores[~ann], alternative="greater")
    return float(u/(n1*n0)), float(p)

def fisher_topk(ann, scores, k=20):
    top = set(np.argsort(scores)[::-1][:k])
    a = sum(1 for i in range(N_C4) if i in top and ann[i])
    b = sum(1 for i in range(N_C4) if i in top and not ann[i])
    c = sum(1 for i in range(N_C4) if i not in top and ann[i])
    d = sum(1 for i in range(N_C4) if i not in top and not ann[i])
    or_, p = stats.fisher_exact([[a,b],[c,d]], alternative="greater")
    return float(or_), float(p), int(a), float(ann.sum()*k/N_C4)

def deg_perm_auroc(ann, scores, n_perm, seed):
    rng = np.random.default_rng(seed)
    be = np.percentile(pair_deg_raw, np.linspace(0,100,N_BINS+1))
    be = np.unique(be); bi = np.digitize(pair_deg_raw, be[1:], right=True)
    null = np.empty(n_perm)
    for i in range(n_perm):
        perm = ann.copy()
        for b in np.unique(bi):
            mask = bi==b; sub = perm[mask]; rng.shuffle(sub); perm[mask] = sub
        a, _ = auroc(perm, scores); null[i] = a
    obs, _ = auroc(ann, scores)
    return float((null >= obs).sum()/n_perm)

def deg_perm_fisher(ann, scores, k, n_perm, seed):
    rng = np.random.default_rng(seed+1)
    be = np.percentile(pair_deg_raw, np.linspace(0,100,N_BINS+1))
    be = np.unique(be); bi = np.digitize(pair_deg_raw, be[1:], right=True)
    null_or = np.empty(n_perm)
    for i in range(n_perm):
        perm = ann.copy()
        for b in np.unique(bi):
            mask = bi==b; sub = perm[mask]; rng.shuffle(sub); perm[mask] = sub
        or_,_,_,_ = fisher_topk(perm, scores, k); null_or[i] = or_
    obs_or,_,_,_ = fisher_topk(ann, scores, k)
    return float((null_or >= obs_or).sum()/n_perm)

# =============================================================================
# H1 — Fisher Comparison
# =============================================================================
print("="*70); print("H1 — Fisher Comparison")
h1_results = {}
for name, ann in ANNOTATIONS.items():
    if ann.sum() == 0: continue
    auc_q, _ = auroc(ann, dq_c4)
    auc_o, _ = auroc(ann, do_c4)
    or_q, p_q, k_q, exp_q = fisher_topk(ann, dq_c4, K)
    or_o, p_o, k_o, exp_o = fisher_topk(ann, do_c4, K)
    p_deg_auc_q = deg_perm_auroc(ann, dq_c4, N_PERM, SEED)
    p_deg_auc_o = deg_perm_auroc(ann, do_c4, N_PERM, SEED)
    p_deg_fish_q = deg_perm_fisher(ann, dq_c4, K, N_PERM, SEED)
    p_deg_fish_o = deg_perm_fisher(ann, do_c4, K, N_PERM, SEED)
    print(f"\n  {name} (n={ann.sum()}):")
    print(f"    AUROC: ΔQ={auc_q:.4f}(p={p_deg_auc_q:.3f}) → ΔΩ={auc_o:.4f}(p={p_deg_auc_o:.3f}) Δ={auc_o-auc_q:+.4f}")
    print(f"    Fisher OR: ΔQ={or_q:.2f}(p={p_deg_fish_q:.3f}) [k={k_q}/exp={exp_q:.1f}] → ΔΩ={or_o:.2f}(p={p_deg_fish_o:.3f}) [k={k_o}] Δ={or_o-or_q:+.2f}")
    h1_results[name] = {
        "n": int(ann.sum()),
        "auroc_dq": float(auc_q), "p_deg_auroc_dq": float(p_deg_auc_q),
        "auroc_do": float(auc_o), "p_deg_auroc_do": float(p_deg_auc_o),
        "or_dq": float(or_q), "p_deg_fish_dq": float(p_deg_fish_q), "k_dq": int(k_q),
        "or_do": float(or_o), "p_deg_fish_do": float(p_deg_fish_o), "k_do": int(k_o),
        "exp_topk": float(exp_q),
        "delta_auroc": float(auc_o-auc_q), "delta_or": float(or_o-or_q),
    }

# =============================================================================
# H2 — ADEL-Centered Analysis
# =============================================================================
print("\n"+"="*70); print("H2 — ADEL-Centered Analysis")
ADEL = n2i["ADEL"]
pdf_c4 = set((min(ii_c4[k],jj_c4[k]),max(ii_c4[k],jj_c4[k]))
              for k in range(N_C4) if ANNOTATIONS["Bentley_PDF"][k])

rank_dq = np.empty(N_C4, dtype=int); rank_dq[np.argsort(-dq_c4)] = np.arange(1,N_C4+1)
rank_do = np.empty(N_C4, dtype=int); rank_do[np.argsort(-do_c4)] = np.arange(1,N_C4+1)

adel_rows = []
for k in range(N_C4):
    i, j = ii_c4[k], jj_c4[k]
    if i != ADEL and j != ADEL: continue
    is_pdf = (min(i,j),max(i,j)) in pdf_c4
    adel_rows.append({
        "k": k, "pair": f"{NEURONS[i]}–{NEURONS[j]}",
        "dq": float(dq_c4[k]), "do": float(do_c4[k]),
        "rank_dq": int(rank_dq[k]), "rank_do": int(rank_do[k]),
        "delta": int(rank_dq[k]-rank_do[k]), "pdf": is_pdf,
    })

adel_pdf   = [r for r in adel_rows if r["pdf"]]
adel_nonpdf = [r for r in adel_rows if not r["pdf"]]

def top_k_count(rows, k):
    return sum(1 for r in rows if r["rank_do"] <= k)

def top_k_count_q(rows, k):
    return sum(1 for r in rows if r["rank_dq"] <= k)

print(f"\nADEL Class 4 pairs: {len(adel_rows)} total ({len(adel_pdf)} PDF, {len(adel_nonpdf)} non-PDF)")
if adel_pdf:
    deltas_pdf = [r["delta"] for r in adel_pdf]
    print(f"  PDF:    mean_Δ={np.mean(deltas_pdf):+.1f} median_Δ={np.median(deltas_pdf):+.1f}")
    print(f"  top-20 ΔQ={top_k_count_q(adel_pdf,20)} ΔΩ={top_k_count(adel_pdf,20)}")
    print(f"  top-50 ΔQ={top_k_count_q(adel_pdf,50)} ΔΩ={top_k_count(adel_pdf,50)}")
if adel_nonpdf:
    deltas_npdf = [r["delta"] for r in adel_nonpdf]
    print(f"  Non-PDF: mean_Δ={np.mean(deltas_npdf):+.1f} median_Δ={np.median(deltas_npdf):+.1f}")
    print(f"  top-20 ΔQ={top_k_count_q(adel_nonpdf,20)} ΔΩ={top_k_count(adel_nonpdf,20)}")

print("\nADEL pairs sorted by Δrank:")
for r in sorted(adel_rows, key=lambda x: -x["delta"]):
    print(f"  {r['pair']:20s}: ΔQ_rank={r['rank_dq']:5d} ΔΩ_rank={r['rank_do']:5d} Δ={r['delta']:+5d} {'PDF' if r['pdf'] else ''}")

h2_results = {
    "adel_pdf": adel_pdf, "adel_nonpdf": adel_nonpdf,
    "adel_pdf_mean_delta": float(np.mean([r["delta"] for r in adel_pdf])) if adel_pdf else 0,
    "adel_nonpdf_mean_delta": float(np.mean([r["delta"] for r in adel_nonpdf])) if adel_nonpdf else 0,
    "adel_pdf_top20_dq": top_k_count_q(adel_pdf, 20),
    "adel_pdf_top20_do": top_k_count(adel_pdf, 20),
    "adel_pdf_top50_dq": top_k_count_q(adel_pdf, 50),
    "adel_pdf_top50_do": top_k_count(adel_pdf, 50),
}

# =============================================================================
# H3 — Blockwise Comparison (condensed)
# =============================================================================
print("\n"+"="*70); print("H3 — Blockwise (DA_mech ↔ URY_URX focus)")
BLOCKS = {
    "DA_mech":    [n2i[n] for n in ["ADEL","CEPDL","CEPDR","CEPVL"]],
    "RID":        [n2i["RID"]],
    "RME":        [n2i["RMEL"],n2i["RMER"]],
    "URY_URX":    [n2i[n] for n in ["URYDL","URYVL","URYVR","URXL"]],
    "command_IN": [n2i[n] for n in ["AVAL","AVAR","AVEL","AVER","AVDL","AVJL","AVJR"]],
    "OLL_OLQ":    [n2i[n] for n in ["OLLL","OLLR","OLQDL","OLQDR","OLQVL","OLQVR"]],
    "IL1_IL2":    [n2i[n] for n in ["IL1DR","IL1L","IL1R","IL2DL","IL2DR","IL2VL","IL2VR"]],
    "pharyngeal": [n2i[n] for n in ["I1L","I1R","I2L","I2R","I3","M1","M3L","M3R","M4","MI","NSML","NSMR"]],
    "RMD_SMD":    [n2i[n] for n in ["RMDDR","RMDL","RMDVL","RMDVR","SMDVL"]],
    "other":      [n2i[n] for n in ["AIBL","AIBR","AIZL","ASEL","ASGL","AUAL","AWAL","AWBL","AWCL","FLPL","RICL","RIVL","URBL"]],
}
block_names = list(BLOCKS.keys()); B = len(block_names)

def block_flow(scores):
    flow = {}
    for b1 in range(B):
        for b2 in range(b1, B):
            vals = []
            for i in BLOCKS[block_names[b1]]:
                for j in BLOCKS[block_names[b2]]:
                    if i==j or (b1==b2 and j<=i): continue
                    key = (min(i,j),max(i,j))
                    if key in c4_set:
                        ki = next((k for k in range(N_C4) if (ii_c4[k]==i and jj_c4[k]==j) or
                                   (ii_c4[k]==j and jj_c4[k]==i)), None)
                        if ki is not None: vals.append(scores[ki])
            if vals:
                flow[(block_names[b1],block_names[b2])] = (float(np.mean(np.abs(vals))), len(vals))
    return sorted(flow.items(), key=lambda x: -x[1][0])

bflow_dq = block_flow(dq_c4)
bflow_do = block_flow(do_c4)

# Focus: DA_mech ↔ URY_URX rank in each
da_ury_rank_dq = next((i+1 for i,(k,_) in enumerate(bflow_dq) if k==("DA_mech","URY_URX") or k==("URY_URX","DA_mech")), None)
da_ury_rank_do = next((i+1 for i,(k,_) in enumerate(bflow_do) if k==("DA_mech","URY_URX") or k==("URY_URX","DA_mech")), None)
print(f"  DA_mech↔URY_URX: ΔQ rank={da_ury_rank_dq}  ΔΩ rank={da_ury_rank_do}")
print("\n  Top-10 ΔQ blockwise:")
for (b1,b2),(mean_val,n) in bflow_dq[:10]:
    print(f"    {b1:12s}↔{b2:12s}: mean={mean_val:.4f} n={n}")
print("\n  Top-10 ΔΩ blockwise:")
for (b1,b2),(mean_val,n) in bflow_do[:10]:
    print(f"    {b1:12s}↔{b2:12s}: mean={mean_val:.4f} n={n}")

h3_results = {
    "da_ury_rank_dq": da_ury_rank_dq, "da_ury_rank_do": da_ury_rank_do,
    "top10_dq": [{"pair":f"{b1}↔{b2}","mean":float(m),"n":n} for (b1,b2),(m,n) in bflow_dq[:10]],
    "top10_do": [{"pair":f"{b1}↔{b2}","mean":float(m),"n":n} for (b1,b2),(m,n) in bflow_do[:10]],
}

# =============================================================================
# H4 — Sparsity Audit
# =============================================================================
print("\n"+"="*70); print("H4 — Sparsity Audit (ΔQ=0, ΔΩ≠0)")
ZERO_THRESH = 1e-10
is_zero_dq = (dq_c4 < ZERO_THRESH)
is_nonzero_do = (do_c4 >= ZERO_THRESH)
rescued = is_zero_dq & is_nonzero_do

# Build "unannotated" mask
any_ann = np.zeros(N_C4, dtype=bool)
for ann in ANNOTATIONS.values(): any_ann |= ann
unann = ~any_ann

all_masks = {**ANNOTATIONS, "unannotated": unann}
print(f"\n  Total C4 pairs with ΔQ=0: {is_zero_dq.sum()}")
print(f"  Total C4 pairs with ΔQ=0 AND ΔΩ≠0 (rescued): {rescued.sum()}")
h4_results = {}
for name, ann in all_masks.items():
    n_zero_both  = int((is_zero_dq & (do_c4 < ZERO_THRESH) & ann).sum())
    n_rescued    = int((rescued & ann).sum())
    n_always_nz  = int((~is_zero_dq & ann).sum())
    n_total_ann  = int(ann.sum())
    frac_rescued = n_rescued / n_total_ann if n_total_ann > 0 else 0
    print(f"  {name:20s}: total={n_total_ann:4d}  "
          f"rescued(ΔQ=0→ΔΩ≠0)={n_rescued:4d} ({100*frac_rescued:.1f}%)  "
          f"both_nonzero={n_always_nz:4d}")
    h4_results[name] = {
        "n_total": n_total_ann, "n_rescued": n_rescued,
        "n_both_nonzero": n_always_nz, "n_both_zero": n_zero_both,
        "frac_rescued": float(frac_rescued),
    }

# =============================================================================
# H5 — Localization Analysis
# =============================================================================
print("\n"+"="*70); print("H5 — Localization: AUROC Contribution by Source")

# AUROC per source class: use only PDF pairs from that source as "positive"
# Compare partial AUROC (those source pairs vs all non-PDF) under ΔQ vs ΔΩ
source_groups = {
    "ADEL":     n2i["ADEL"],
    "RID":      n2i["RID"],
    "RMEL":     n2i["RMEL"],
    "RMER":     n2i["RMER"],
    "AVDL":     n2i["AVDL"],
}
pdf_mask_full = ANNOTATIONS["Bentley_PDF"]
nonpdf_scores_dq = dq_c4[~pdf_mask_full]
nonpdf_scores_do = do_c4[~pdf_mask_full]
N_nonpdf = int((~pdf_mask_full).sum())

h5_results = {}
print(f"\n  Source-specific partial AUROC (source pairs vs all {N_nonpdf} non-PDF pairs):")
for src_name, src_idx in source_groups.items():
    src_mask = np.array([(ii_c4[k]==src_idx or jj_c4[k]==src_idx) and pdf_mask_full[k]
                          for k in range(N_C4)])
    if src_mask.sum() == 0: continue
    src_scores_dq = dq_c4[src_mask]; src_scores_do = do_c4[src_mask]
    # Partial AUROC: P(score_src > score_nonpdf)
    conc_dq = sum(int((nonpdf_scores_dq < s).sum()) for s in src_scores_dq)
    conc_do = sum(int((nonpdf_scores_do < s).sum()) for s in src_scores_do)
    total = int(src_mask.sum()) * N_nonpdf
    pauc_dq = conc_dq / total; pauc_do = conc_do / total
    delta_conc = conc_do - conc_dq
    print(f"  {src_name:6s}: n_pairs={src_mask.sum():2d}  "
          f"AUROC_ΔQ={pauc_dq:.4f}  AUROC_ΔΩ={pauc_do:.4f}  "
          f"Δ={pauc_do-pauc_dq:+.4f}  ΔConcordant={delta_conc:+d}")
    h5_results[src_name] = {
        "n_pairs": int(src_mask.sum()),
        "auroc_dq": float(pauc_dq), "auroc_do": float(pauc_do),
        "delta_auroc": float(pauc_do-pauc_dq),
        "delta_concordant": int(delta_conc),
    }

# Decompose total AUROC change by source
total_delta_conc = sum(v["delta_concordant"] for v in h5_results.values())
total_delta = 31082  # from G4
print(f"\n  Total Δconcordant (all PDF vs non-PDF): +{total_delta}")
print(f"  Attributed to named sources: {total_delta_conc} ({100*total_delta_conc/total_delta:.1f}%)")
for src, v in h5_results.items():
    frac = 100*v["delta_concordant"]/total_delta if total_delta > 0 else 0
    print(f"    {src:6s}: Δconcordant={v['delta_concordant']:+7d} ({frac:+.1f}% of total)")

# Save
result = {
    "date": "2026-06-03",
    "authorization": "Phase 3C-H",
    "H1_fisher": h1_results,
    "H2_adel": h2_results,
    "H3_blockwise": h3_results,
    "H4_sparsity": h4_results,
    "H5_localization": h5_results,
    "H5_total_delta_concordant": total_delta,
    "H5_attributed_concordant": total_delta_conc,
}

def sanitize(obj):
    if isinstance(obj, (np.floating,)):
        v=float(obj); return None if (v!=v or abs(v)==float("inf")) else v
    if isinstance(obj, float): return None if (obj!=obj or abs(obj)==float("inf")) else obj
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.bool_,)):   return bool(obj)
    if isinstance(obj, np.ndarray):    return [sanitize(v) for v in obj.tolist()]
    if isinstance(obj, dict):          return {k: sanitize(v) for k,v in obj.items()}
    if isinstance(obj, (list,tuple)):  return [sanitize(v) for v in obj]
    return obj

import json as json_mod
with open(OUT3C / "phase3c_h_results.json","w") as f:
    json_mod.dump(sanitize(result), f, indent=2)
print("\nSaved: phase3c_h_results.json")
