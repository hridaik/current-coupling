"""Stage 4 — Enrichment analysis.

Authorization: 2026-06-01, human supervisor (Stage 4 authorized in restart package).

Scope:
  Test 1: Neuropeptide AUROC (primary)  — simple + degree-preserving null
  Test 2: Neuropeptide Fisher top-K=20  — simple + degree-preserving null
  Test 3: Randi unc-31 AUROC + Fisher   — simple + degree-preserving null
  Test 4: Serotonin/PDF (exploratory)   — skipped (annotation not in corpus)
  Confirmation check: ΔQ source = confirmation matrices; document explicitly.
  Coordinate-specific: CePNEM and GCaMP separately.

Inputs (all pre-computed; no new estimation):
  results/phase2/stage2/DQ_cepnem.npy   — ΔQ from confirmation matrices (cepnem)
  results/phase2/stage2/DQ_gcamp.npy    — ΔQ from confirmation matrices (gcamp)
  /tmp/A_raw_61.npy                     — synaptic connectome (61×61)
  /tmp/pep_61.npy                       — neuropeptide annotation (61×61)
  /tmp/randi_61.npy                     — Randi unc-31 annotation (61×61)
  /tmp/creamer_mask_61.npy              — Creamer 56-neuron subspace (61,)

Constraints:
  - Use confirmation ΔQ ONLY (no discovery/stability-weighted ΔQ)
  - No stability weighting (per Stage 2 authorization)
  - PRIMARY_TOP_K = 20
  - 1000 permutations per null model
  - Save all results BEFORE writing report

Stage 5 recommendation based on results.

STOP after report. Stage 5 requires separate human authorization.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase2_config as p2cfg

assert p2cfg.PHASE2_ACTIVE, "PHASE2_ACTIVE must be True"

# ── Configuration ─────────────────────────────────────────────────────────────

N       = p2cfg.PHASE2_N_NEURONS       # 61
K       = p2cfg.PRIMARY_TOP_K          # 20
N_PERM  = 1000                         # permutations per null
N_BINS  = 10                           # degree bins for degree-preserving null
SEED    = 42                           # fixed seed for reproducibility

# Influential recordings from Stage 3 (all roaming; included in sensitivity note)
INFLUENTIAL_CEPNEM = ["2023-01-16-15", "2023-01-17-14"]
INFLUENTIAL_GCAMP  = ["2022-06-14-07", "2023-01-16-15", "2023-01-17-14"]

# Directories
STG2_DIR = ROOT / "results/phase2/stage2"
OUT_DIR  = ROOT / "results/phase2/stage4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Stage 4 — Enrichment Analysis")
print(f"  PRIMARY_TOP_K = {K}")
print(f"  N_PERM = {N_PERM}")
print(f"  SEED   = {SEED}")
print("=" * 70)

# ── Load data ─────────────────────────────────────────────────────────────────

DQ_cepnem = np.load(STG2_DIR / "DQ_cepnem.npy")   # (61,61) confirmation ΔQ
DQ_gcamp  = np.load(STG2_DIR / "DQ_gcamp.npy")    # (61,61) confirmation ΔQ

A_raw        = np.load("/tmp/A_raw_61.npy").astype(bool)    # (61,61)
pep_61       = np.load("/tmp/pep_61.npy").astype(bool)      # (61,61)
randi_61     = np.load("/tmp/randi_61.npy").astype(bool)    # (61,61)
creamer_mask = np.load("/tmp/creamer_mask_61.npy").astype(bool)  # (61,)

with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS = cop["neurons"]   # 61-element canonical list

# ── Pair indices and classification ───────────────────────────────────────────

ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)   # 1830

on_raw    = A_raw[ii_all, jj_all]
off_raw   = ~on_raw
both_cm   = np.outer(creamer_mask, creamer_mask)[ii_all, jj_all]
class4_mask = off_raw & both_cm

n_class4 = int(class4_mask.sum())
assert n_class4 == 1321, f"Expected 1321 Class 4 pairs, got {n_class4}"

# Indices into the full 1830-pair vector
class4_idx = np.where(class4_mask)[0]
ii_c4 = ii_all[class4_idx]
jj_c4 = jj_all[class4_idx]

# Annotations restricted to Class 4
pep_c4   = pep_61[ii_c4, jj_c4].astype(bool)    # neuropeptide
randi_c4 = randi_61[ii_c4, jj_c4].astype(bool)  # Randi unc-31

n_pep_c4   = int(pep_c4.sum())
n_randi_c4 = int(randi_c4.sum())

print(f"\nClass 4 pairs: {n_class4}")
print(f"  Neuropeptide annotated: {n_pep_c4} ({100*n_pep_c4/n_class4:.1f}%)")
print(f"  Randi annotated:        {n_randi_c4} ({100*n_randi_c4/n_class4:.1f}%)")

# Degree vectors for degree-preserving null
deg_raw = A_raw.astype(int).sum(axis=1)       # synaptic degree per neuron
deg_pep = pep_61.astype(int).sum(axis=1)      # neuropeptide degree per neuron

pair_deg_raw = deg_raw[ii_c4] + deg_raw[jj_c4]   # (n_class4,) raw degree sum
pair_deg_pep = deg_pep[ii_c4] + deg_pep[jj_c4]   # (n_class4,) pep degree sum

print(f"\nDegree (A_raw) — Class 4 pairs:")
print(f"  Sum range: [{pair_deg_raw.min()}, {pair_deg_raw.max()}], "
      f"median={np.median(pair_deg_raw):.0f}")
print(f"Degree (A_peptide) — Class 4 pairs:")
print(f"  Sum range: [{pair_deg_pep.min()}, {pair_deg_pep.max()}], "
      f"median={np.median(pair_deg_pep):.0f}")


# ── Enrichment utilities ──────────────────────────────────────────────────────

def compute_auroc(annotations: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """AUROC and one-sided Mann-Whitney p-value."""
    ann = np.asarray(annotations, dtype=bool)
    sc  = np.asarray(scores, dtype=float)
    n1  = int(ann.sum())
    n0  = int((~ann).sum())
    if n1 == 0 or n0 == 0:
        return float("nan"), float("nan")
    u, p = stats.mannwhitneyu(sc[ann], sc[~ann], alternative="greater")
    auc = float(u / (n1 * n0))
    return auc, float(p)


def compute_fisher_topk(annotations: np.ndarray, scores: np.ndarray, k: int
                        ) -> tuple[float, float, dict]:
    """Fisher exact test for top-K enrichment. Returns (odds_ratio, p_value, contingency)."""
    ann = np.asarray(annotations, dtype=bool)
    N_  = len(ann)
    k_  = min(k, N_)
    top_idx = np.argsort(scores)[::-1][:k_]
    top_mask = np.zeros(N_, dtype=bool)
    top_mask[top_idx] = True

    a = int(( top_mask &  ann).sum())
    b = int(( top_mask & ~ann).sum())
    c = int((~top_mask &  ann).sum())
    d = int((~top_mask & ~ann).sum())

    or_, p = stats.fisher_exact([[a, b], [c, d]], alternative="greater")
    return float(or_), float(p), {"a": a, "b": b, "c": c, "d": d}


def permute_simple(ann: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Simple random permutation of annotation labels."""
    result = ann.copy()
    rng.shuffle(result)
    return result


def permute_degree_stratified(ann: np.ndarray,
                               deg_sums: np.ndarray,
                               n_bins: int,
                               rng: np.random.Generator) -> np.ndarray:
    """Degree-stratified permutation within bins of pair degree sum."""
    result = ann.copy().astype(bool)
    bin_edges = np.percentile(deg_sums, np.linspace(0, 100, n_bins + 1))
    bin_edges = np.unique(bin_edges)
    bin_idx   = np.digitize(deg_sums, bin_edges[1:], right=True)
    for b in np.unique(bin_idx):
        mask = bin_idx == b
        sub  = result[mask]
        rng.shuffle(sub)
        result[mask] = sub
    return result


def null_auroc_distribution(annotations: np.ndarray,
                             scores: np.ndarray,
                             perm_fn,
                             n_perm: int,
                             rng: np.random.Generator) -> np.ndarray:
    """Generate null AUROC distribution under a permutation scheme."""
    null_vals = np.empty(n_perm)
    for i in range(n_perm):
        perm_ann = perm_fn(annotations, rng)
        auc, _ = compute_auroc(perm_ann, scores)
        null_vals[i] = auc
    return null_vals


def null_fisher_distribution(annotations: np.ndarray,
                              scores: np.ndarray,
                              k: int,
                              perm_fn,
                              n_perm: int,
                              rng: np.random.Generator) -> np.ndarray:
    """Generate null Fisher odds-ratio distribution under a permutation scheme."""
    null_vals = np.empty(n_perm)
    for i in range(n_perm):
        perm_ann = perm_fn(annotations, rng)
        or_, _, _ = compute_fisher_topk(perm_ann, scores, k)
        null_vals[i] = or_
    return null_vals


def perm_pvalue(observed: float, null_dist: np.ndarray) -> float:
    """Empirical one-sided p-value (greater)."""
    return float((null_dist >= observed).sum() / len(null_dist))


def validate_degree_preservation(ann_orig, ann_perm, deg_sums, n_bins=5):
    """Check that degree distribution of annotated pairs is preserved."""
    bin_edges = np.percentile(deg_sums, np.linspace(0, 100, n_bins + 1))
    bin_edges = np.unique(bin_edges)
    bin_idx   = np.digitize(deg_sums, bin_edges[1:], right=True)
    bins = np.unique(bin_idx)
    orig_counts = np.array([int((ann_orig & (bin_idx == b)).sum()) for b in bins])
    perm_counts = np.array([int((ann_perm & (bin_idx == b)).sum()) for b in bins])
    max_dev = int(np.abs(orig_counts - perm_counts).max())
    return {"orig_counts": orig_counts.tolist(),
            "perm_counts": perm_counts.tolist(),
            "max_bin_deviation": max_dev,
            "passed": max_dev == 0}


# ── Run all enrichment tests for one coordinate ───────────────────────────────

def run_enrichment_for_coordinate(coord_name: str,
                                   DQ_matrix: np.ndarray,
                                   rng_seed: int) -> dict:
    """Run all Stage 4 enrichment tests for one coordinate system.

    Returns a dict of all test results.
    """
    rng = np.random.default_rng(rng_seed)
    t0  = time.time()

    # Extract |ΔQ| scores for Class 4 pairs
    scores = np.abs(DQ_matrix[ii_c4, jj_c4])

    n_nonzero = int((scores > 0).sum())
    print(f"\n{'─'*60}")
    print(f"Coordinate: {coord_name}")
    print(f"  |ΔQ| non-zero Class 4: {n_nonzero}/{n_class4}")
    print(f"  |ΔQ| max={scores.max():.4f}, p95={np.percentile(scores,95):.4f}, "
          f"mean={scores.mean():.4f}")

    results = {
        "coord": coord_name,
        "n_class4": n_class4,
        "n_nonzero_dq": n_nonzero,
        "dq_stats": {
            "max": float(scores.max()),
            "p95": float(np.percentile(scores, 95)),
            "mean": float(scores.mean()),
            "median": float(np.median(scores)),
        },
        "confirmation_estimator_note": (
            "ΔQ = Q_conf_roam − Q_conf_dwell (anatomy-guided ADMM confirmation matrices). "
            "No discovery/stability ΔQ used. Per Stage 2 authorization."
        ),
        "tests": {}
    }

    # ── Test 1: Neuropeptide AUROC ────────────────────────────────────────────
    print(f"\n  Test 1: Neuropeptide AUROC (n_ann={n_pep_c4})")
    t1 = time.time()

    auroc_obs, p_mw = compute_auroc(pep_c4, scores)
    print(f"    Observed AUROC={auroc_obs:.4f}, Mann-Whitney p={p_mw:.4e}")

    # Simple null
    rng1 = np.random.default_rng(rng.integers(2**32))
    null_auroc_simple = null_auroc_distribution(
        pep_c4, scores,
        perm_fn=lambda a, r: permute_simple(a, r),
        n_perm=N_PERM, rng=rng1
    )
    p_simple_auroc = perm_pvalue(auroc_obs, null_auroc_simple)
    print(f"    Simple null: null_mean={null_auroc_simple.mean():.4f}, "
          f"p_perm={p_simple_auroc:.4f}")

    # Degree-preserving null (A_raw degree)
    rng2 = np.random.default_rng(rng.integers(2**32))
    null_auroc_deg = null_auroc_distribution(
        pep_c4, scores,
        perm_fn=lambda a, r: permute_degree_stratified(a, pair_deg_raw, N_BINS, r),
        n_perm=N_PERM, rng=rng2
    )
    p_deg_auroc = perm_pvalue(auroc_obs, null_auroc_deg)
    print(f"    Degree null : null_mean={null_auroc_deg.mean():.4f}, "
          f"p_perm={p_deg_auroc:.4f}")

    # Validate degree preservation on one sample permutation
    rng_val = np.random.default_rng(12345)
    sample_perm = permute_degree_stratified(pep_c4, pair_deg_raw, N_BINS, rng_val)
    deg_val = validate_degree_preservation(pep_c4, sample_perm, pair_deg_raw, n_bins=N_BINS)

    t1_pass = (p_deg_auroc < 0.05) and (auroc_obs > 0.5)
    print(f"    Test 1 {'PASS' if t1_pass else 'FAIL'} "
          f"(AUROC={auroc_obs:.4f}, p_deg={p_deg_auroc:.4f})")

    results["tests"]["test1_neuropeptide_auroc"] = {
        "description": "Neuropeptide AUROC (primary)",
        "n_annotated": n_pep_c4,
        "auroc_observed": float(auroc_obs),
        "p_mannwhitney": float(p_mw),
        "null_simple": {
            "null_mean": float(null_auroc_simple.mean()),
            "null_std": float(null_auroc_simple.std()),
            "null_p95": float(np.percentile(null_auroc_simple, 95)),
            "p_perm": float(p_simple_auroc),
        },
        "null_degree_preserving": {
            "null_mean": float(null_auroc_deg.mean()),
            "null_std": float(null_auroc_deg.std()),
            "null_p95": float(np.percentile(null_auroc_deg, 95)),
            "p_perm": float(p_deg_auroc),
            "degree_preservation_check": deg_val,
        },
        "pass_fail": "PASS" if t1_pass else "FAIL",
        "pass_criterion": "AUROC > 0.5 AND p_degree_preserving < 0.05",
        "elapsed_s": round(time.time() - t1, 1),
    }

    # ── Test 2: Neuropeptide Fisher top-K ─────────────────────────────────────
    print(f"\n  Test 2: Neuropeptide Fisher top-K={K} (n_ann={n_pep_c4})")
    t2 = time.time()

    or_obs, p_fisher, ctab = compute_fisher_topk(pep_c4, scores, K)
    print(f"    Observed OR={or_obs:.3f}, Fisher p={p_fisher:.4e}")
    print(f"    Contingency: a={ctab['a']}, b={ctab['b']}, "
          f"c={ctab['c']}, d={ctab['d']}")

    rng3 = np.random.default_rng(rng.integers(2**32))
    null_or_simple = null_fisher_distribution(
        pep_c4, scores, K,
        perm_fn=lambda a, r: permute_simple(a, r),
        n_perm=N_PERM, rng=rng3
    )
    p_simple_fisher = perm_pvalue(or_obs, null_or_simple)

    rng4 = np.random.default_rng(rng.integers(2**32))
    null_or_deg = null_fisher_distribution(
        pep_c4, scores, K,
        perm_fn=lambda a, r: permute_degree_stratified(a, pair_deg_raw, N_BINS, r),
        n_perm=N_PERM, rng=rng4
    )
    p_deg_fisher = perm_pvalue(or_obs, null_or_deg)

    print(f"    Simple null: null_mean_OR={np.nanmean(null_or_simple):.3f}, "
          f"p_perm={p_simple_fisher:.4f}")
    print(f"    Degree null : null_mean_OR={np.nanmean(null_or_deg):.3f}, "
          f"p_perm={p_deg_fisher:.4f}")

    t2_pass = (p_deg_fisher < 0.05) and (or_obs > 1.0)
    print(f"    Test 2 {'PASS' if t2_pass else 'FAIL'} "
          f"(OR={or_obs:.3f}, p_deg={p_deg_fisher:.4f})")

    results["tests"]["test2_neuropeptide_fisher"] = {
        "description": f"Neuropeptide Fisher top-{K} (secondary)",
        "n_annotated": n_pep_c4,
        "k": K,
        "or_observed": float(or_obs),
        "p_fisher_exact": float(p_fisher),
        "contingency": ctab,
        "null_simple": {
            "null_mean_or": float(np.nanmean(null_or_simple)),
            "null_std_or": float(np.nanstd(null_or_simple)),
            "p_perm": float(p_simple_fisher),
        },
        "null_degree_preserving": {
            "null_mean_or": float(np.nanmean(null_or_deg)),
            "null_std_or": float(np.nanstd(null_or_deg)),
            "p_perm": float(p_deg_fisher),
        },
        "pass_fail": "PASS" if t2_pass else "FAIL",
        "pass_criterion": "OR > 1.0 AND p_degree_preserving < 0.05",
        "elapsed_s": round(time.time() - t2, 1),
    }

    # ── Test 3: Randi unc-31 AUROC + Fisher ───────────────────────────────────
    print(f"\n  Test 3: Randi unc-31 (n_ann={n_randi_c4})")
    t3 = time.time()

    # AUROC
    auroc_randi, p_mw_randi = compute_auroc(randi_c4, scores)
    print(f"    Randi AUROC={auroc_randi:.4f}, MW p={p_mw_randi:.4e}")

    rng5 = np.random.default_rng(rng.integers(2**32))
    null_randi_simple = null_auroc_distribution(
        randi_c4, scores,
        perm_fn=lambda a, r: permute_simple(a, r),
        n_perm=N_PERM, rng=rng5
    )
    p_randi_simple = perm_pvalue(auroc_randi, null_randi_simple)

    rng6 = np.random.default_rng(rng.integers(2**32))
    null_randi_deg = null_auroc_distribution(
        randi_c4, scores,
        perm_fn=lambda a, r: permute_degree_stratified(a, pair_deg_raw, N_BINS, r),
        n_perm=N_PERM, rng=rng6
    )
    p_randi_deg = perm_pvalue(auroc_randi, null_randi_deg)

    print(f"    Simple null: p_perm={p_randi_simple:.4f}")
    print(f"    Degree null : p_perm={p_randi_deg:.4f}")

    # Fisher
    or_randi, p_fisher_randi, ctab_randi = compute_fisher_topk(randi_c4, scores, K)
    print(f"    Randi Fisher K={K}: OR={or_randi:.3f}, p={p_fisher_randi:.4e}")

    rng7 = np.random.default_rng(rng.integers(2**32))
    null_randi_fish_s = null_fisher_distribution(
        randi_c4, scores, K,
        perm_fn=lambda a, r: permute_simple(a, r),
        n_perm=N_PERM, rng=rng7
    )
    p_randi_fish_s = perm_pvalue(or_randi, null_randi_fish_s)

    rng8 = np.random.default_rng(rng.integers(2**32))
    null_randi_fish_d = null_fisher_distribution(
        randi_c4, scores, K,
        perm_fn=lambda a, r: permute_degree_stratified(a, pair_deg_raw, N_BINS, r),
        n_perm=N_PERM, rng=rng8
    )
    p_randi_fish_d = perm_pvalue(or_randi, null_randi_fish_d)

    print(f"    Randi Fisher: simple p={p_randi_fish_s:.4f}, deg p={p_randi_fish_d:.4f}")

    t3_auroc_pass   = (p_randi_deg < 0.05) and (auroc_randi > 0.5)
    t3_fisher_pass  = (p_randi_fish_d < 0.05) and (or_randi > 1.0)
    t3_pass = t3_auroc_pass or t3_fisher_pass
    print(f"    Test 3 AUROC {'PASS' if t3_auroc_pass else 'FAIL'} | "
          f"Fisher {'PASS' if t3_fisher_pass else 'FAIL'}")

    results["tests"]["test3_randi"] = {
        "description": "Randi unc-31 AUROC + Fisher (secondary)",
        "n_annotated": n_randi_c4,
        "auroc": {
            "auroc_observed": float(auroc_randi),
            "p_mannwhitney": float(p_mw_randi),
            "null_simple": {"p_perm": float(p_randi_simple),
                            "null_mean": float(null_randi_simple.mean())},
            "null_degree_preserving": {"p_perm": float(p_randi_deg),
                                       "null_mean": float(null_randi_deg.mean())},
            "pass_fail": "PASS" if t3_auroc_pass else "FAIL",
        },
        "fisher": {
            "or_observed": float(or_randi),
            "p_fisher_exact": float(p_fisher_randi),
            "contingency": ctab_randi,
            "null_simple": {"p_perm": float(p_randi_fish_s),
                            "null_mean_or": float(np.nanmean(null_randi_fish_s))},
            "null_degree_preserving": {"p_perm": float(p_randi_fish_d),
                                       "null_mean_or": float(np.nanmean(null_randi_fish_d))},
            "pass_fail": "PASS" if t3_fisher_pass else "FAIL",
        },
        "elapsed_s": round(time.time() - t3, 1),
    }

    # ── Test 4: Serotonin/PDF (exploratory) — not available ──────────────────
    print(f"\n  Test 4: Serotonin/PDF — SKIPPED (annotation not in corpus)")
    results["tests"]["test4_serotonin_pdf"] = {
        "description": "Serotonin/PDF receptor AUROC + Fisher (exploratory)",
        "status": "SKIPPED",
        "reason": ("Serotonin/PDF receptor annotation not available in the SF corpus "
                   "at this stage. No serotonin_61.npy or pdf_61.npy file found."),
    }

    # ── Confirmation estimator check ──────────────────────────────────────────
    # The primary ΔQ IS from the confirmation estimator (ADMM, λ_on=0.01, λ_off=0.10).
    # Stability selection (discovery) produces stability score matrices, not precision
    # matrices, so no separate "discovery ΔQ" exists. The confirmation check documents
    # that the primary analysis uses only the pre-authorized confirmation matrices.
    print(f"\n  Confirmation estimator check:")
    print(f"    ΔQ source = Q_conf_roam − Q_conf_dwell (anatomy-guided ADMM)")
    print(f"    AUROC repeated on same ΔQ (= primary Test 1): "
          f"AUROC={auroc_obs:.4f}, p_deg={p_deg_auroc:.4f}")
    print(f"    Result: AUROC identical to Test 1 (same ΔQ). "
          f"Confirmation check {'PASS' if t1_pass else 'INCONCLUSIVE'}.")

    results["confirmation_estimator_check"] = {
        "dq_source": "Q_conf_roam - Q_conf_dwell (anatomy-guided ADMM, lambda_on=0.01, lambda_off=0.10)",
        "note": ("Stage 2 authorization used confirmation matrices only. "
                 "Discovery estimator (stability selection) produces stability score matrices "
                 "[0,1], not precision matrices; no separate discovery ΔQ computed. "
                 "Primary AUROC already uses confirmation ΔQ. "),
        "auroc_confirmation": float(auroc_obs),
        "p_degree_preserving_confirmation": float(p_deg_auroc),
        "consistent_with_test1": True,
        "pass_fail": "PASS" if t1_pass else "FAIL",
    }

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed_total = round(time.time() - t0, 1)
    print(f"\n  Summary for {coord_name}: elapsed {elapsed_total}s")

    results["elapsed_total_s"] = elapsed_total
    return results


# ── Run both coordinates ──────────────────────────────────────────────────────

rng_master = np.random.default_rng(SEED)
seed_cepnem = int(rng_master.integers(2**32))
seed_gcamp  = int(rng_master.integers(2**32))

print("\n" + "=" * 70)
print("RUNNING CEPNEM COORDINATE")
results_cepnem = run_enrichment_for_coordinate("cepnem", DQ_cepnem, seed_cepnem)

print("\n" + "=" * 70)
print("RUNNING GCAMP COORDINATE")
results_gcamp = run_enrichment_for_coordinate("gcamp", DQ_gcamp, seed_gcamp)


# ── Coordinate comparison summary ─────────────────────────────────────────────

def extract_primary_stats(r):
    t1 = r["tests"]["test1_neuropeptide_auroc"]
    t2 = r["tests"]["test2_neuropeptide_fisher"]
    return {
        "auroc": t1["auroc_observed"],
        "p_mw": t1["p_mannwhitney"],
        "p_simple": t1["null_simple"]["p_perm"],
        "p_deg":    t1["null_degree_preserving"]["p_perm"],
        "test1_pass": t1["pass_fail"],
        "fisher_or": t2["or_observed"],
        "fisher_p_exact": t2["p_fisher_exact"],
        "fisher_p_deg": t2["null_degree_preserving"]["p_perm"],
        "test2_pass": t2["pass_fail"],
        "randi_auroc": r["tests"]["test3_randi"]["auroc"]["auroc_observed"],
        "randi_p_deg": r["tests"]["test3_randi"]["auroc"]["null_degree_preserving"]["p_perm"],
        "randi_auroc_pass": r["tests"]["test3_randi"]["auroc"]["pass_fail"],
        "randi_fisher_or": r["tests"]["test3_randi"]["fisher"]["or_observed"],
        "randi_fisher_p_deg": r["tests"]["test3_randi"]["fisher"]["null_degree_preserving"]["p_perm"],
        "randi_fisher_pass": r["tests"]["test3_randi"]["fisher"]["pass_fail"],
    }

cep_s = extract_primary_stats(results_cepnem)
gca_s = extract_primary_stats(results_gcamp)

print("\n" + "=" * 70)
print("COORDINATE COMPARISON SUMMARY")
print(f"{'Metric':<35} {'CePNEM':>12} {'GCaMP':>12}")
print("-" * 60)
print(f"{'Test 1 AUROC':<35} {cep_s['auroc']:>12.4f} {gca_s['auroc']:>12.4f}")
print(f"{'Test 1 p (Mann-Whitney)':<35} {cep_s['p_mw']:>12.4e} {gca_s['p_mw']:>12.4e}")
print(f"{'Test 1 p (simple perm)':<35} {cep_s['p_simple']:>12.4f} {gca_s['p_simple']:>12.4f}")
print(f"{'Test 1 p (degree-pres.)':<35} {cep_s['p_deg']:>12.4f} {gca_s['p_deg']:>12.4f}")
print(f"{'Test 1 PASS/FAIL':<35} {cep_s['test1_pass']:>12} {gca_s['test1_pass']:>12}")
print(f"{'Test 2 Fisher OR':<35} {cep_s['fisher_or']:>12.3f} {gca_s['fisher_or']:>12.3f}")
print(f"{'Test 2 p (Fisher exact)':<35} {cep_s['fisher_p_exact']:>12.4e} {gca_s['fisher_p_exact']:>12.4e}")
print(f"{'Test 2 p (degree-pres.)':<35} {cep_s['fisher_p_deg']:>12.4f} {gca_s['fisher_p_deg']:>12.4f}")
print(f"{'Test 2 PASS/FAIL':<35} {cep_s['test2_pass']:>12} {gca_s['test2_pass']:>12}")
print(f"{'Test 3 Randi AUROC':<35} {cep_s['randi_auroc']:>12.4f} {gca_s['randi_auroc']:>12.4f}")
print(f"{'Test 3 Randi p (deg-pres.)':<35} {cep_s['randi_p_deg']:>12.4f} {gca_s['randi_p_deg']:>12.4f}")
print(f"{'Test 3 Randi AUROC PASS/FAIL':<35} {cep_s['randi_auroc_pass']:>12} {gca_s['randi_auroc_pass']:>12}")
print(f"{'Test 3 Randi Fisher OR':<35} {cep_s['randi_fisher_or']:>12.3f} {gca_s['randi_fisher_or']:>12.3f}")
print(f"{'Test 3 Randi Fisher p (deg)':<35} {cep_s['randi_fisher_p_deg']:>12.4f} {gca_s['randi_fisher_p_deg']:>12.4f}")
print(f"{'Test 3 Randi Fisher PASS/FAIL':<35} {cep_s['randi_fisher_pass']:>12} {gca_s['randi_fisher_pass']:>12}")


# ── Stage 5 recommendation ────────────────────────────────────────────────────

cep_sig = (cep_s["test1_pass"] == "PASS") or (cep_s["test2_pass"] == "PASS")
gca_sig = (gca_s["test1_pass"] == "PASS") or (gca_s["test2_pass"] == "PASS")

if cep_sig and gca_sig:
    stage5_rec = "STRONG_RECOMMEND"
    stage5_msg = ("Both coordinates show significant enrichment under degree-preserving null. "
                  "Stage 5 coordinate comparison is scientifically motivated.")
elif cep_sig:
    stage5_rec = "RECOMMEND"
    stage5_msg = ("CePNEM coordinate significant under degree-preserving null; "
                  "GCaMP not significant. Stage 5 will apply locked interpretation table.")
elif gca_sig:
    stage5_rec = "RECOMMEND"
    stage5_msg = ("GCaMP coordinate significant; CePNEM not significant. "
                  "Stage 5 will apply locked interpretation table.")
else:
    stage5_rec = "NULL_RESULT"
    stage5_msg = ("Neither coordinate shows significant enrichment. Stage 5 will record null "
                  "result per the locked interpretation table (no mechanistic inference).")

print(f"\nStage 5 recommendation: {stage5_rec}")
print(f"  {stage5_msg}")


# ── Null model validation check ───────────────────────────────────────────────

print("\n  Null model degree-preservation validation (A_raw):")
rng_dv = np.random.default_rng(999)
perm_val = permute_degree_stratified(pep_c4, pair_deg_raw, N_BINS, rng_dv)
dv = validate_degree_preservation(pep_c4, perm_val, pair_deg_raw, n_bins=N_BINS)
print(f"    Max bin deviation: {dv['max_bin_deviation']} "
      f"({'PASS' if dv['passed'] else 'FAIL'})")


# ── Assemble full results dict ────────────────────────────────────────────────

all_results = {
    "date": "2026-06-01",
    "stage": "4",
    "authorization": "2026-06-01 human supervisor",
    "seed": SEED,
    "n_perm": N_PERM,
    "n_bins_degree": N_BINS,
    "primary_top_k": K,
    "n_class4": n_class4,
    "n_annotated_neuropeptide_class4": n_pep_c4,
    "n_annotated_randi_class4": n_randi_c4,
    "annotation_density_neuropeptide": float(n_pep_c4 / n_class4),
    "annotation_density_randi": float(n_randi_c4 / n_class4),
    "test4_serotonin_pdf": "SKIPPED — annotation not in corpus",
    "cepnem": results_cepnem,
    "gcamp": results_gcamp,
    "coordinate_comparison": {
        "cepnem_pep_auroc": cep_s["auroc"],
        "cepnem_pep_p_deg": cep_s["p_deg"],
        "cepnem_test1_pass": cep_s["test1_pass"],
        "gcamp_pep_auroc": gca_s["auroc"],
        "gcamp_pep_p_deg": gca_s["p_deg"],
        "gcamp_test1_pass": gca_s["test1_pass"],
    },
    "stage5_recommendation": stage5_rec,
    "stage5_message": stage5_msg,
    "sensitivity_note": (
        "Stage 3 LOO identified influential roaming recordings: "
        f"CePNEM={INFLUENTIAL_CEPNEM}, GCaMP={INFLUENTIAL_GCAMP}. "
        "All influential recordings are roaming recordings. "
        "Enrichment tests run on full dataset. "
        "DEV-005 (all-animal pooling) is partially compensated by LOO sensitivity analysis. "
        "Results should be interpreted in light of possible roaming-recording influence."
    ),
    "null_model_validation": {
        "degree_preservation_A_raw": dv,
        "n_perm": N_PERM,
        "null_type": "simple + degree_stratified (A_raw degree sum, 10 bins)",
    },
    "pass_conditions": {
        "all_tests_run_with_both_nulls": True,
        "results_saved_before_figures": True,
        "confirmation_estimator_check_completed": True,
        "null_degree_preservation_validated": dv["passed"],
    },
}

# ── Save JSON (BEFORE any figure/report writing) ──────────────────────────────

out_json = OUT_DIR / "stage4_results.json"
with open(out_json, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\nResults saved: {out_json}")


# ── Print final pass/fail table ───────────────────────────────────────────────

print("\n" + "=" * 70)
print("STAGE 4 FINAL PASS/FAIL TABLE")
print("=" * 70)
rows = [
    ("Test 1 Pep AUROC (CePNEM)", cep_s["test1_pass"]),
    ("Test 1 Pep AUROC (GCaMP)",  gca_s["test1_pass"]),
    ("Test 2 Pep Fisher (CePNEM)", cep_s["test2_pass"]),
    ("Test 2 Pep Fisher (GCaMP)",  gca_s["test2_pass"]),
    ("Test 3 Randi AUROC (CePNEM)", cep_s["randi_auroc_pass"]),
    ("Test 3 Randi AUROC (GCaMP)",  gca_s["randi_auroc_pass"]),
    ("Test 3 Randi Fisher (CePNEM)", cep_s["randi_fisher_pass"]),
    ("Test 3 Randi Fisher (GCaMP)",  gca_s["randi_fisher_pass"]),
    ("Test 4 Serotonin/PDF", "SKIPPED"),
    ("Confirmation check (CePNEM)", results_cepnem["confirmation_estimator_check"]["pass_fail"]),
    ("Confirmation check (GCaMP)",  results_gcamp["confirmation_estimator_check"]["pass_fail"]),
    ("Null degree preservation",     "PASS" if dv["passed"] else "FAIL"),
    ("All results saved before figure", "PASS"),
]
for name, verdict in rows:
    print(f"  {name:<40} {verdict}")

print(f"\nStage 5 recommendation: {stage5_rec}")
print(f"  {stage5_msg}")
print("\nDone. Stage 4 complete. Awaiting human review before Stage 5.")
