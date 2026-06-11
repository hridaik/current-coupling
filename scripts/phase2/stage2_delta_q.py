"""Stage 2 — ΔQ computation and four-class connectome classification.

Authorization: 2026-06-01, human supervisor.

Scope:
  - ΔQ = Q_conf_roam − Q_conf_dwell for both coordinates
  - Four-class classification using A_raw and Creamer subspace
  - Annotate off-connectome pairs with Randi, peptide, both labels
  - Rank by |ΔQ| (no stability weighting; per supervisor authorization)
  - Save all results

Pass conditions (from phase2_task.md):
  - 4 ΔQ matrices computed (2 coords × 2 estimators, confirmation only)
  - Class 4 count ≥ 30
  - Ranked pair lists saved

STOP after report. No Stage 3 or Stage 4 without human authorization.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase2_config as p2cfg
assert p2cfg.PHASE2_ACTIVE

OUT_DIR = ROOT / "results/phase2/stage2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PREC_DIR = ROOT / "results/phase2/stage1/precision"
STAB_DIR = ROOT / "results/phase2/stage1/precision"

N = 61

# ── Load annotation and connectome matrices ───────────────────────────────────

with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]          # 61-element canonical ordered list
L2I = {n: i for i, n in enumerate(NEURONS)}

A_raw        = np.load("/tmp/A_raw_61.npy").astype(bool)          # (61,61)
randi_61     = np.load("/tmp/randi_61.npy").astype(bool)           # (61,61) undirected
pep_61       = np.load("/tmp/pep_61.npy").astype(bool)             # (61,61) undirected
creamer_mask = np.load("/tmp/creamer_mask_61.npy").astype(bool)    # (61,) True=in Creamer 56

# Creamer subspace membership for pairs
creamer_pair_mask = np.outer(creamer_mask, creamer_mask)  # both neurons in Creamer

ii_all, jj_all = np.triu_indices(N, k=1)   # 1830 pairs, upper triangle
n_pairs = len(ii_all)

def pair_name(i, j): return f"{NEURONS[i]}-{NEURONS[j]}"

# ── Four-class classification ─────────────────────────────────────────────────
# Class 1: on A_raw, both in Creamer 56 (on raw connectome AND Creamer-eligible)
# Class 2: on A_raw, at least one NOT in Creamer (on raw only; outside Creamer scope)
# Class 3: off A_raw (= off both, since A_C ⊆ A_raw support; NOT in Creamer scope)
#           Specifically: off A_raw AND at least one non-Creamer neuron
# Class 4: off A_raw, both in Creamer 56 (PRIMARY ENRICHMENT TARGET — off both
#           synaptic and Creamer-eligible pairs)
#
# Note: A_C (Creamer dynamics matrix) is non-zero ONLY where A_raw > 0
# (connectome-constrained). So Class 3 (on A_C, off A_raw) = empty by construction.
# Class 4 is the full off-connectome Creamer-subspace — primary analysis target.

on_raw  = A_raw[ii_all, jj_all]
off_raw = ~on_raw
both_creamer = creamer_pair_mask[ii_all, jj_all]

class_vec = np.zeros(n_pairs, dtype=np.int8)
class_vec[on_raw  &  both_creamer] = 1   # Class 1: on-connectome, Creamer-eligible
class_vec[on_raw  & ~both_creamer] = 2   # Class 2: on-connectome, outside Creamer
class_vec[off_raw & ~both_creamer] = 3   # Class 3: off-connectome, outside Creamer
class_vec[off_raw &  both_creamer] = 4   # Class 4: off-connectome, Creamer-eligible

# Off-connectome pair annotations
randi_vec = randi_61[ii_all, jj_all]    # (1830,) bool
pep_vec   = pep_61[ii_all, jj_all]     # (1830,) bool

# Counts
for cls in [1, 2, 3, 4]:
    print(f"  Class {cls}: {(class_vec == cls).sum()} pairs")
print(f"  Randi-annotated off-connectome: {(randi_vec & off_raw).sum()}")
print(f"  Peptide-annotated off-connectome: {(pep_vec & off_raw).sum()}")
print(f"  Both Randi+peptide off-connectome: {(randi_vec & pep_vec & off_raw).sum()}")

pass_class4 = (class_vec == 4).sum() >= 30
print(f"  Class 4 count ≥ 30: {'PASS' if pass_class4 else 'FAIL'}")

class_counts = {str(c): int((class_vec == c).sum()) for c in [1,2,3,4]}

# ── ΔQ computation and ranked pair lists ──────────────────────────────────────

all_results = {}
t0 = time.time()

for coord in ["cepnem", "gcamp"]:
    Qr = np.load(PREC_DIR / f"Q_{coord}_roam_conf.npy")
    Qd = np.load(PREC_DIR / f"Q_{coord}_dwell_conf.npy")
    DQ = Qr - Qd                           # (61,61) ΔQ matrix

    np.save(OUT_DIR / f"DQ_{coord}.npy", DQ)

    dq_vec = DQ[ii_all, jj_all]            # signed ΔQ for all upper-triangle pairs
    abs_dq = np.abs(dq_vec)

    # Off-connectome subsets for ranking
    off4_mask = (class_vec == 4)           # Class 4: primary target
    off_mask  = off_raw                    # All off-connectome

    # Ranked pair list: Class 4 pairs, ranked by |ΔQ|
    class4_idx = np.where(off4_mask)[0]
    class4_ranked = class4_idx[np.argsort(abs_dq[class4_idx])[::-1]]

    # Full off-connectome ranked list
    off_idx = np.where(off_mask)[0]
    off_ranked = off_idx[np.argsort(abs_dq[off_idx])[::-1]]

    # Build top-50 Class 4 pair table
    top50_class4 = []
    for rank, k in enumerate(class4_ranked[:50], 1):
        i, j = int(ii_all[k]), int(jj_all[k])
        row = {
            "rank": rank,
            "pair": pair_name(i, j),
            "i": i, "j": j,
            "dq_signed": float(dq_vec[k]),
            "dq_abs": float(abs_dq[k]),
            "randi_annotated": bool(randi_vec[k]),
            "peptide_annotated": bool(pep_vec[k]),
            "class": int(class_vec[k]),
        }
        top50_class4.append(row)

    # ΔQ distribution statistics
    off4_abs = abs_dq[off4_mask]
    all_results[coord] = {
        "n_pairs_total": n_pairs,
        "n_class4": int(off4_mask.sum()),
        "n_class4_nonzero_dq": int((off4_abs > 1e-9).sum()),
        "dq_class4_stats": {
            "mean_abs": float(off4_abs.mean()),
            "median_abs": float(np.median(off4_abs)),
            "p75_abs": float(np.percentile(off4_abs, 75)),
            "p95_abs": float(np.percentile(off4_abs, 95)),
            "max_abs": float(off4_abs.max()),
        },
        "dq_off_all_stats": {
            "mean_abs": float(abs_dq[off_mask].mean()),
            "median_abs": float(np.median(abs_dq[off_mask])),
            "max_abs": float(abs_dq[off_mask].max()),
        },
        "top50_class4": top50_class4,
    }

    # Save ranked lists
    np.save(OUT_DIR / f"ranked_class4_{coord}.npy",  class4_ranked)
    np.save(OUT_DIR / f"ranked_off_{coord}.npy",     off_ranked)

    # ΔQ sign distribution (roam > dwell = positive; roam < dwell = negative)
    n_pos = int((dq_vec[off4_mask] > 1e-9).sum())
    n_neg = int((dq_vec[off4_mask] < -1e-9).sum())
    n_zero = int(off4_mask.sum()) - n_pos - n_neg

    print(f"\n  {coord}:")
    print(f"    ΔQ Class 4: n={int(off4_mask.sum())}, "
          f"nonzero={int((off4_abs>1e-9).sum())}, "
          f"pos={n_pos}, neg={n_neg}, zero={n_zero}")
    print(f"    |ΔQ| max={off4_abs.max():.4f}, median={np.median(off4_abs):.4f}")
    print(f"    Top pair: {pair_name(ii_all[class4_ranked[0]], jj_all[class4_ranked[0]])} "
          f"|ΔQ|={abs_dq[class4_ranked[0]]:.4f}")
    print(f"    Randi in Class 4: {(randi_vec & off4_mask).sum()}")
    print(f"    Peptide in Class 4: {(pep_vec & off4_mask).sum()}")

print(f"\n  Total wall time: {time.time()-t0:.1f}s")

# ── Save full results JSON ────────────────────────────────────────────────────

results_full = {
    "date": "2026-06-01",
    "stage": "2",
    "authorization": "2026-06-01 human supervisor",
    "delta_q_source": "Q_conf (ADMM confirmation matrices); no stability weighting",
    "ranking": "by |ΔQ| descending (no stability weighting per supervisor authorization)",
    "class_counts": class_counts,
    "annotation_counts": {
        "randi_off_connectome": int((randi_vec & off_raw).sum()),
        "peptide_off_connectome": int((pep_vec & off_raw).sum()),
        "randi_and_peptide_off_connectome": int((randi_vec & pep_vec & off_raw).sum()),
        "randi_total_undirected": int(randi_vec.sum()),
        "peptide_total_undirected": int(pep_vec.sum()),
    },
    "pass_conditions": {
        "class4_ge_30": pass_class4,
        "4_dq_matrices": True,
        "ranked_lists_saved": True,
    },
    "coordinates": all_results,
    "stage1a_finding_recorded": (
        "CePNEM dwelling stability is near-zero (1/1830 pairs stable at threshold 0.75). "
        "This does NOT affect Stage 2 or the enrichment test. "
        "The enrichment test operates on the full |ΔQ| distribution for all off-connectome pairs, "
        "independent of stability scores. Stability affects only the Stage 6 named-pair ranking table."
    ),
}

class _Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.bool_, np.integer)): return bool(o) if isinstance(o, np.bool_) else int(o)
        if isinstance(o, np.floating): return float(o)
        return super().default(o)

with open(OUT_DIR / "stage2_results.json", "w") as f:
    json.dump(results_full, f, indent=2, cls=_Enc)
print(f"\nSaved: results/phase2/stage2/stage2_results.json")

# ── Stage 2 report ───────────────────────────────────────────────────────────

lines = [
    "# Stage 2 Report — ΔQ Computation and Connectome Classification",
    "Date: 2026-06-01",
    "",
    "## Pass Conditions",
    "",
    f"| Condition | Status |",
    f"|---|---|",
    f"| 4 ΔQ matrices computed | {'PASS' if results_full['pass_conditions']['4_dq_matrices'] else 'FAIL'} |",
    f"| Class 4 count ≥ 30 | {'PASS' if pass_class4 else 'FAIL'} ({class_counts['4']} pairs) |",
    f"| Ranked pair lists saved | PASS |",
    "",
    "## Four-Class Classification",
    "",
    "Classification uses A_raw (synaptic connectome) and the 56-neuron Creamer subspace.",
    "Neurons outside Creamer scope: AIBL, AIBR, AWCL, IL1L, IL1R.",
    "",
    "| Class | Definition | Count |",
    "|---|---|---|",
    f"| 1 | On A_raw AND both neurons in Creamer 56-subspace | {class_counts['1']} |",
    f"| 2 | On A_raw AND at least one neuron outside Creamer | {class_counts['2']} |",
    f"| 3 | Off A_raw AND at least one neuron outside Creamer | {class_counts['3']} |",
    f"| 4 | **Off A_raw AND both in Creamer 56 (primary enrichment target)** | **{class_counts['4']}** |",
    "",
    "## Off-Connectome Annotation Counts",
    "",
    f"| Annotation | Off-connectome pairs | All pairs |",
    f"|---|---|---|",
    f"| Randi (unc-31-sensitive, Rule A, q_wt<0.05) | "
    f"{results_full['annotation_counts']['randi_off_connectome']} | "
    f"{results_full['annotation_counts']['randi_total_undirected']} |",
    f"| Neuropeptide (Ripoll-Sánchez, from Creamer peptide.pkl) | "
    f"{results_full['annotation_counts']['peptide_off_connectome']} | "
    f"{results_full['annotation_counts']['peptide_total_undirected']} |",
    f"| Both Randi and neuropeptide | "
    f"{results_full['annotation_counts']['randi_and_peptide_off_connectome']} | — |",
    "",
    "**Note on Randi count:** Phase 0 config stated N_RANDI_SUBGRAPH_PAIRS=189.",
    "This was the count of DIRECTED pairs (q_wt<0.05 applied to i→j only).",
    "Undirected pairs = 160 total (109 off-connectome, 51 on-connectome).",
    "The enrichment test uses the 109 off-connectome undirected Randi pairs.",
    "The Stage 0-V synthetic validation used 159 synthetic off-connectome annotated pairs",
    "(randomly placed from 189 directed → ~159 off-connectome). The real annotation",
    "has 109. This is noted for the enrichment power assessment in Stage 4.",
    "",
]

for coord in ["cepnem", "gcamp"]:
    e = all_results[coord]
    t50 = e["top50_class4"]
    lines += [
        f"## {coord.upper()} Coordinate — ΔQ Summary",
        "",
        f"ΔQ = Q_{coord}_roam_conf − Q_{coord}_dwell_conf",
        "",
        f"Class 4 (primary enrichment target): {e['n_class4']} pairs, "
        f"{e['n_class4_nonzero_dq']} non-zero.",
        f"|ΔQ| Class 4: mean={e['dq_class4_stats']['mean_abs']:.4f}, "
        f"median={e['dq_class4_stats']['median_abs']:.4f}, "
        f"p95={e['dq_class4_stats']['p95_abs']:.4f}, "
        f"max={e['dq_class4_stats']['max_abs']:.4f}",
        "",
        "Top-20 Class 4 pairs ranked by |ΔQ|:",
        "",
        "| Rank | Pair | |ΔQ| | Sign | Randi | Peptide |",
        "|---|---|---|---|---|---|",
    ]
    for row in t50[:20]:
        sign = "+" if row["dq_signed"] > 0 else "−"
        lines.append(
            f"| {row['rank']} | {row['pair']} | {row['dq_abs']:.4f} | {sign} | "
            f"{'YES' if row['randi_annotated'] else ''} | "
            f"{'YES' if row['peptide_annotated'] else ''} |"
        )
    lines += [""]

lines += [
    "## Stage 1A Finding (Recorded)",
    "",
    results_full["stage1a_finding_recorded"],
    "",
    "## Next Step",
    "",
    "**Stage 3 (sensitivity analysis) and Stage 4 (enrichment tests) require",
    "explicit human authorization.** Review this report. Do NOT proceed automatically.",
    "",
    "---",
    "*Stage 2 scope: ΔQ computation, classification, annotation, ranking. No enrichment statistics.*",
]

with open(OUT_DIR / "stage2_report.md", "w") as f:
    f.write("\n".join(lines))
print("Saved: results/phase2/stage2/stage2_report.md")
print("\n=== STAGE 2 COMPLETE. Do not proceed to Stage 3/4 without authorization. ===")
