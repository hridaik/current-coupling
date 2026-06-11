"""Stage 4A — Serotonin/PDF exploratory enrichment analysis.

Authorization: 2026-06-01, human supervisor. Phase 2 addendum.

Scope:
  Primary annotation (Bentley ESconnectome, directed, undirected collapse):
    - Bentley serotonin:        monoamines file, transmitter == "serotonin"
    - Bentley PDF:              neuropeptides file, transmitter contains "pdf"
    - Bentley combined (OR):    serotonin OR PDF

  Secondary annotation (CeNGEN expression-based, exploratory):
    - CeNGEN serotonin/PDF combined (conservative threshold 3)
      ligand-receptor logic: (tph-1/cat-1) → (ser-1/4/5/7/mod-1)
                             (pdf-1/pdf-2) → (pdfr-1)

  Applied independently to:
    - CePNEM coordinate
    - GCaMP coordinate

  Enrichment tests (same machinery as Stage 4):
    AUROC + Mann-Whitney analytical p
    Fisher top-K (K=20) + Fisher exact p
    Simple permutation null (1000 perms)
    Degree-preserving null (A_raw degree, 10 bins, 1000 perms)

Inputs (read-only; no new estimation):
  results/phase2/stage2/DQ_cepnem.npy
  results/phase2/stage2/DQ_gcamp.npy
  data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_monoamines_Bentley_2016.csv
  data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_neuropeptides_Bentley_2016.csv
  data/randi/wormneuroatlas/wormneuroatlas/data/cengen_021821_conservative_threshold3.csv
  /tmp/A_raw_61.npy, /tmp/creamer_mask_61.npy
  results/phase2/stage0/copresence_report.json

STOP after report. No further computation authorized.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase2_config as p2cfg

assert p2cfg.PHASE2_ACTIVE

# ── Configuration ─────────────────────────────────────────────────────────────

N       = p2cfg.PHASE2_N_NEURONS        # 61
K       = p2cfg.PRIMARY_TOP_K           # 20
N_PERM  = 1000
N_BINS  = 10
SEED    = 43                            # distinct from Stage 4 seed (42)

DATA_DIR   = ROOT / "data/randi/wormneuroatlas/wormneuroatlas/data"
STG2_DIR   = ROOT / "results/phase2/stage2"
OUT_DIR    = ROOT / "results/phase2/stage4a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Stage 4A — Serotonin/PDF Exploratory Enrichment")
print(f"  PRIMARY_TOP_K={K}, N_PERM={N_PERM}, SEED={SEED}")
print("=" * 70)

# ── Load ΔQ matrices and subgraph metadata ────────────────────────────────────

DQ_cepnem = np.load(STG2_DIR / "DQ_cepnem.npy")
DQ_gcamp  = np.load(STG2_DIR / "DQ_gcamp.npy")

A_raw        = np.load("/tmp/A_raw_61.npy").astype(bool)
creamer_mask = np.load("/tmp/creamer_mask_61.npy").astype(bool)

with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]
N_NEURONS = len(NEURONS)
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)

# Class 4 pair indices
ii_all, jj_all = np.triu_indices(N, k=1)
on_raw    = A_raw[ii_all, jj_all]
off_raw   = ~on_raw
both_cm   = np.outer(creamer_mask, creamer_mask)[ii_all, jj_all]
class4    = off_raw & both_cm
ii_c4     = ii_all[class4]
jj_c4     = jj_all[class4]
n_c4      = int(class4.sum())
class4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

# Degree for null model
deg_raw = A_raw.astype(int).sum(axis=1)
pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]

assert n_c4 == 1321, f"Expected 1321 Class 4 pairs, got {n_c4}"

# ── CeNGEN bilateral → 61-neuron mapping ──────────────────────────────────────

CENGEN_TO_61 = {
    "ADE": ["ADEL"], "AIB": ["AIBL", "AIBR"], "AIZ": ["AIZL"], "ASEL": ["ASEL"],
    "ASG": ["ASGL"], "AUA": ["AUAL"], "AVA": ["AVAL", "AVAR"], "AVD": ["AVDL"],
    "AVE": ["AVEL", "AVER"], "AVJ": ["AVJL", "AVJR"], "AWA": ["AWAL"],
    "AWB": ["AWBL"], "AWC_OFF": ["AWCL"], "FLP": ["FLPL"],
    "I1": ["I1L", "I1R"], "I2": ["I2L", "I2R"], "I3": ["I3"],
    "IL1": ["IL1DR", "IL1L", "IL1R"], "IL2_DV": ["IL2DL", "IL2DR"],
    "IL2_LR": ["IL2VL", "IL2VR"], "M1": ["M1"], "M3": ["M3L", "M3R"],
    "M4": ["M4"], "MI": ["MI"], "NSM": ["NSML", "NSMR"],
    "OLL": ["OLLL", "OLLR"],
    "OLQ": ["OLQDL", "OLQDR", "OLQVL", "OLQVR"],
    "RIC": ["RICL"], "RID": ["RID"], "RIV": ["RIVL"],
    "RMD_DV": ["RMDDR", "RMDVL"], "RMD_LR": ["RMDL", "RMDVR"],
    "RME_DV": ["RMEL"], "RME_LR": ["RMER"], "SMD": ["SMDVL"],
    "URB": ["URBL"], "URX": ["URXL"],
    "URY": ["URYDL", "URYVL", "URYVR"],
    "CEP": ["CEPDL", "CEPDR", "CEPVL"],
}


# ── Build Bentley annotations ─────────────────────────────────────────────────

def load_bentley_pairs(csv_path: Path, keep_fn) -> set:
    """Parse a Bentley ESconnectome CSV and return undirected pairs (i,j) with i<j
    that are within the 61-neuron subgraph and satisfy keep_fn(row)."""
    pairs = set()
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader)   # skip header
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


bentley_ser_all = load_bentley_pairs(
    DATA_DIR / "esconnectome_monoamines_Bentley_2016.csv",
    lambda row: row[2].strip().lower() == "serotonin",
)
bentley_pdf_all = load_bentley_pairs(
    DATA_DIR / "esconnectome_neuropeptides_Bentley_2016.csv",
    lambda row: "pdf" in row[2].strip().lower(),
)

bentley_ser_c4   = bentley_ser_all & class4_set
bentley_pdf_c4   = bentley_pdf_all & class4_set
bentley_comb_c4  = (bentley_ser_all | bentley_pdf_all) & class4_set

print(f"\nBentley annotations (Class 4 / {n_c4}):")
print(f"  Serotonin:  {len(bentley_ser_c4)}  ({100*len(bentley_ser_c4)/n_c4:.1f}%)")
print(f"  PDF:        {len(bentley_pdf_c4)}  ({100*len(bentley_pdf_c4)/n_c4:.1f}%)")
print(f"  Combined:   {len(bentley_comb_c4)}  ({100*len(bentley_comb_c4)/n_c4:.1f}%)")


# ── Build CeNGEN annotation ───────────────────────────────────────────────────

_cengen_targets = {
    "ser-1", "ser-4", "ser-5", "ser-7", "mod-1",
    "pdfr-1", "tph-1", "cat-1", "pdf-1", "pdf-2",
}

def _load_cengen_gene(gene_name: str, cengen_csv: Path) -> set:
    """Return set of 61-neuron subgraph indices expressing gene_name."""
    nset: set = set()
    with open(cengen_csv) as f:
        reader = csv.reader(f)
        header = next(reader)
        celltypes = header[3:]
        for row in reader:
            if len(row) > 1 and row[1].strip().lower() == gene_name:
                for i, ct in enumerate(celltypes):
                    val_str = row[3 + i] if 3 + i < len(row) else ""
                    try:
                        val = float(val_str)
                    except (ValueError, TypeError):
                        val = 0.0
                    if val > 0 and ct in CENGEN_TO_61:
                        for n in CENGEN_TO_61[ct]:
                            if n in n2i:
                                nset.add(n2i[n])
                return nset  # found and parsed; return immediately
    return nset  # not found


cengen_csv = DATA_DIR / "cengen_021821_conservative_threshold3.csv"
tph1_idx = _load_cengen_gene("tph-1", cengen_csv)
cat1_idx = _load_cengen_gene("cat-1", cengen_csv)
ser_rx_idx = (
    _load_cengen_gene("ser-1", cengen_csv) |
    _load_cengen_gene("ser-4", cengen_csv) |
    _load_cengen_gene("ser-5", cengen_csv) |
    _load_cengen_gene("ser-7", cengen_csv) |
    _load_cengen_gene("mod-1", cengen_csv)
)
pdf_lig_idx = _load_cengen_gene("pdf-1", cengen_csv) | _load_cengen_gene("pdf-2", cengen_csv)
pdfr1_idx   = _load_cengen_gene("pdfr-1", cengen_csv)

cengen_ser_lig = tph1_idx | cat1_idx

cengen_ser_c4  = set()
cengen_pdf_c4  = set()
for a, b in zip(map(int, ii_c4), map(int, jj_c4)):
    key = (min(a, b), max(a, b))
    if (a in cengen_ser_lig and b in ser_rx_idx) or (b in cengen_ser_lig and a in ser_rx_idx):
        cengen_ser_c4.add(key)
    if (a in pdf_lig_idx and b in pdfr1_idx) or (b in pdf_lig_idx and a in pdfr1_idx):
        cengen_pdf_c4.add(key)

cengen_comb_c4 = cengen_ser_c4 | cengen_pdf_c4

print(f"\nCeNGEN annotations (Class 4 / {n_c4}, conservative threshold):")
print(f"  Serotonin:  {len(cengen_ser_c4)}  ({100*len(cengen_ser_c4)/n_c4:.1f}%)")
print(f"  PDF:        {len(cengen_pdf_c4)}  ({100*len(cengen_pdf_c4)/n_c4:.1f}%)")
print(f"  Combined:   {len(cengen_comb_c4)}  ({100*len(cengen_comb_c4)/n_c4:.1f}%)")


# ── Convert pair sets to boolean annotation vectors ───────────────────────────

def pairs_to_vec(pair_set: set) -> np.ndarray:
    """Convert a set of (i,j) pairs to a boolean (n_c4,) annotation vector."""
    vec = np.zeros(n_c4, dtype=bool)
    pair_list = list(zip(map(int, ii_c4), map(int, jj_c4)))
    for k, p in enumerate(pair_list):
        if p in pair_set:
            vec[k] = True
    return vec


ann_bentley_ser  = pairs_to_vec(bentley_ser_c4)
ann_bentley_pdf  = pairs_to_vec(bentley_pdf_c4)
ann_bentley_comb = pairs_to_vec(bentley_comb_c4)
ann_cengen_comb  = pairs_to_vec(cengen_comb_c4)

# Verify counts
assert ann_bentley_ser.sum()  == len(bentley_ser_c4)
assert ann_bentley_pdf.sum()  == len(bentley_pdf_c4)
assert ann_bentley_comb.sum() == len(bentley_comb_c4)
assert ann_cengen_comb.sum()  == len(cengen_comb_c4)


# ── Enrichment utilities (identical to Stage 4) ───────────────────────────────

def compute_auroc(ann: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    ann_b = ann.astype(bool)
    n1, n0 = int(ann_b.sum()), int((~ann_b).sum())
    if n1 == 0 or n0 == 0:
        return float("nan"), float("nan")
    u, p = stats.mannwhitneyu(scores[ann_b], scores[~ann_b], alternative="greater")
    return float(u / (n1 * n0)), float(p)


def compute_fisher(ann: np.ndarray, scores: np.ndarray, k: int
                   ) -> tuple[float, float, dict]:
    ann_b = ann.astype(bool)
    N_   = len(ann_b)
    top  = np.zeros(N_, dtype=bool)
    top[np.argsort(scores)[::-1][:min(k, N_)]] = True
    a = int(( top &  ann_b).sum())
    b = int(( top & ~ann_b).sum())
    c = int((~top &  ann_b).sum())
    d = int((~top & ~ann_b).sum())
    or_, p = stats.fisher_exact([[a, b], [c, d]], alternative="greater")
    return float(or_), float(p), {"a": a, "b": b, "c": c, "d": d}


def permute_simple(ann: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    r = ann.copy()
    rng.shuffle(r)
    return r


def permute_degree(ann: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    r = ann.copy().astype(bool)
    edges = np.percentile(pair_deg_raw, np.linspace(0, 100, N_BINS + 1))
    edges = np.unique(edges)
    bins  = np.digitize(pair_deg_raw, edges[1:], right=True)
    for b in np.unique(bins):
        mask = bins == b
        sub  = r[mask]
        rng.shuffle(sub)
        r[mask] = sub
    return r


def run_null(ann: np.ndarray, scores: np.ndarray,
             perm_fn, stat_fn, n_perm: int,
             rng: np.random.Generator) -> np.ndarray:
    return np.array([stat_fn(perm_fn(ann, rng), scores) for _ in range(n_perm)])


def perm_p(obs: float, null: np.ndarray) -> float:
    return float((null >= obs).sum() / len(null))


# ── Run one annotation on one coordinate ─────────────────────────────────────

def run_one(ann_vec: np.ndarray, ann_name: str,
            scores: np.ndarray, coord: str,
            rng: np.random.Generator) -> dict:
    n_ann = int(ann_vec.sum())
    n_non = n_c4 - n_ann

    print(f"  [{coord}] {ann_name}: n_ann={n_ann}, n_non={n_non}")

    if n_ann == 0:
        return {
            "annotation": ann_name, "coord": coord,
            "n_annotated": 0, "n_class4": n_c4,
            "status": "SKIPPED — zero annotated pairs",
        }

    # AUROC
    auroc_obs, p_mw = compute_auroc(ann_vec, scores)

    rng_s = np.random.default_rng(rng.integers(2**32))
    null_a_s = run_null(ann_vec, scores, permute_simple,
                        lambda a, s: compute_auroc(a, s)[0], N_PERM, rng_s)
    p_simple_a = perm_p(auroc_obs, null_a_s)

    rng_d = np.random.default_rng(rng.integers(2**32))
    null_a_d = run_null(ann_vec, scores, permute_degree,
                        lambda a, s: compute_auroc(a, s)[0], N_PERM, rng_d)
    p_deg_a = perm_p(auroc_obs, null_a_d)

    # Fisher
    or_obs, p_fe, ctab = compute_fisher(ann_vec, scores, K)

    rng_fs = np.random.default_rng(rng.integers(2**32))
    null_f_s = run_null(ann_vec, scores, permute_simple,
                        lambda a, s: compute_fisher(a, s, K)[0], N_PERM, rng_fs)
    p_simple_f = perm_p(or_obs, null_f_s)

    rng_fd = np.random.default_rng(rng.integers(2**32))
    null_f_d = run_null(ann_vec, scores, permute_degree,
                        lambda a, s: compute_fisher(a, s, K)[0], N_PERM, rng_fd)
    p_deg_f = perm_p(or_obs, null_f_d)

    auroc_pass  = (auroc_obs > 0.5) and (p_deg_a < 0.05)
    fisher_pass = (or_obs > 1.0)    and (p_deg_f < 0.05)

    print(f"         AUROC={auroc_obs:.4f} p_mw={p_mw:.3e} "
          f"p_simple={p_simple_a:.3f} p_deg={p_deg_a:.3f} "
          f"→ {'PASS' if auroc_pass else 'FAIL'}")
    print(f"         Fisher OR={or_obs:.3f} p_fe={p_fe:.3e} "
          f"p_simple={p_simple_f:.3f} p_deg={p_deg_f:.3f} "
          f"→ {'PASS' if fisher_pass else 'FAIL'}")

    # Top-K overlap with annotated pairs
    top_k_idx = set(np.argsort(scores)[::-1][:K])
    top_k_ann = int(sum(1 for i in top_k_idx if ann_vec[i]))
    expected_in_topk = n_ann * K / n_c4

    return {
        "annotation": ann_name,
        "coord":      coord,
        "n_annotated": n_ann,
        "n_non_annotated": n_non,
        "n_class4": n_c4,
        "annotation_density": float(n_ann / n_c4),
        "auroc": {
            "observed":    float(auroc_obs),
            "p_mannwhitney": float(p_mw),
            "p_simple_perm": float(p_simple_a),
            "p_degree_perm": float(p_deg_a),
            "null_simple_mean": float(null_a_s.mean()),
            "null_degree_mean": float(null_a_d.mean()),
            "pass_fail": "PASS" if auroc_pass else "FAIL",
        },
        "fisher": {
            "k":            K,
            "or_observed":  float(or_obs),
            "p_fisher_exact": float(p_fe),
            "p_simple_perm": float(p_simple_f),
            "p_degree_perm": float(p_deg_f),
            "contingency":  ctab,
            "top_k_annotated": top_k_ann,
            "expected_in_topk": round(expected_in_topk, 2),
            "pass_fail": "PASS" if fisher_pass else "FAIL",
        },
        "pass_criterion": "AUROC>0.5 AND p_deg<0.05 (AUROC); OR>1 AND p_deg<0.05 (Fisher)",
    }


# ── Main loop: all annotations × both coordinates ────────────────────────────

rng_master = np.random.default_rng(SEED)

annotations = [
    ("Bentley_serotonin",         ann_bentley_ser,  "primary",    "Bentley ESconnectome, transmitter==serotonin"),
    ("Bentley_PDF",               ann_bentley_pdf,  "primary",    "Bentley ESconnectome, transmitter contains pdf"),
    ("Bentley_serotonin_or_PDF",  ann_bentley_comb, "primary",    "Bentley ESconnectome, serotonin OR PDF"),
    ("CeNGEN_serotonin_or_PDF",   ann_cengen_comb,  "exploratory","CeNGEN conservative threshold, directed ligand-receptor"),
]

coords = [
    ("cepnem", DQ_cepnem),
    ("gcamp",  DQ_gcamp),
]

all_results: dict = {
    "date": "2026-06-01",
    "stage": "4A",
    "authorization": "2026-06-01 human supervisor",
    "seed": SEED,
    "n_perm": N_PERM,
    "n_bins_degree": N_BINS,
    "primary_top_k": K,
    "n_class4": n_c4,
    "annotation_summary": {
        "Bentley_serotonin":        int(ann_bentley_ser.sum()),
        "Bentley_PDF":              int(ann_bentley_pdf.sum()),
        "Bentley_serotonin_or_PDF": int(ann_bentley_comb.sum()),
        "CeNGEN_serotonin_or_PDF":  int(ann_cengen_comb.sum()),
    },
    "results": {},
}

t_total = time.time()
for coord_name, DQ_mat in coords:
    scores = np.abs(DQ_mat[ii_c4, jj_c4])
    all_results["results"][coord_name] = {}
    print(f"\n{'='*60}")
    print(f"Coordinate: {coord_name}  |ΔQ| max={scores.max():.4f}, "
          f"nonzero={int((scores>0).sum())}/{n_c4}")
    for ann_name, ann_vec, ann_tier, ann_desc in annotations:
        rng_local = np.random.default_rng(rng_master.integers(2**32))
        res = run_one(ann_vec, ann_name, scores, coord_name, rng_local)
        res["tier"]        = ann_tier
        res["description"] = ann_desc
        all_results["results"][coord_name][ann_name] = res

print(f"\nTotal elapsed: {time.time()-t_total:.1f}s")

# ── Save JSON before report ───────────────────────────────────────────────────

out_json = OUT_DIR / "stage4a_results.json"
with open(out_json, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\nResults saved: {out_json}")

# ── Print summary table ───────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("STAGE 4A — FINAL PASS/FAIL TABLE")
print("=" * 70)
hdr = f"{'Annotation':<30} {'Coord':<8} {'AUROC':>7} {'p_deg_A':>8} {'OR':>7} {'p_deg_F':>8}  {'Verdict'}"
print(hdr)
print("-" * 80)
for coord_name, _ in coords:
    for ann_name, _, _, _ in annotations:
        r = all_results["results"][coord_name][ann_name]
        if "auroc" not in r:
            print(f"  {ann_name:<30} {coord_name:<8}  SKIPPED")
            continue
        auroc  = r["auroc"]["observed"]
        p_da   = r["auroc"]["p_degree_perm"]
        or_    = r["fisher"]["or_observed"]
        p_df   = r["fisher"]["p_degree_perm"]
        a_pf   = r["auroc"]["pass_fail"]
        f_pf   = r["fisher"]["pass_fail"]
        verdict = "PASS" if (a_pf == "PASS" or f_pf == "PASS") else "FAIL"
        print(f"  {ann_name:<30} {coord_name:<8} {auroc:>7.4f} {p_da:>8.3f} "
              f"{or_:>7.3f} {p_df:>8.3f}  {verdict}")

print()
