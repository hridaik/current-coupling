"""Stage 3 — Leave-One-Recording-Out sensitivity analysis.

Authorization: 2026-06-01, human supervisor.

Scope:
  - LOO for EVERY contributing recording (40 total)
  - Both coordinates: CePNEM residuals, raw GCaMP
  - Confirmation estimator only (ADMM, λ_on=0.01, λ_off=0.10) per authorization
  - Metrics: rank correlation, top-50 retention, influential-recording identification
  - DEV-005 assessment: whether pooling drives the ΔQ structure

Inputs: sufficient statistics from Stage 1 suff_stats/ (no new H5 loading).
Outputs: all saved before any enrichment analysis.

STOP after report. Stage 4 requires separate authorization.
"""
from __future__ import annotations
import json, sys, time, warnings
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phase2_config as p2cfg
import phase0_config as p0cfg
assert p2cfg.PHASE2_ACTIVE

N        = p2cfg.PHASE2_N_NEURONS          # 61
LAM_ON   = p2cfg.LAMBDA_ON                  # 0.01
LAM_OFF  = p2cfg.LAMBDA_OFF                 # 0.10
MIN_CP   = p2cfg.MIN_COPRESENCE_RECORDINGS  # 9
PSD_FLOOR = p2cfg.PSD_EIGENVALUE_FLOOR      # 1e-6

SUFF_DIR = ROOT / "results/phase2/stage1/suff_stats"
PREC_DIR = ROOT / "results/phase2/stage1/precision"
STG2_DIR = ROOT / "results/phase2/stage2"
OUT_DIR  = ROOT / "results/phase2/stage3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(ROOT / "results/phase2/stage0/copresence_report.json") as f:
    cop = json.load(f)
NEURONS  = cop["neurons"]
REC_IDS  = cop["recording_ids"]
N_REC    = len(REC_IDS)

A_raw        = np.load("/tmp/A_raw_61.npy").astype(bool)
creamer_mask = np.load("/tmp/creamer_mask_61.npy").astype(bool)
randi_61     = np.load("/tmp/randi_61.npy").astype(bool)

ii_all, jj_all = np.triu_indices(N, k=1)
n_pairs = len(ii_all)

on_raw  = A_raw[ii_all, jj_all]
off_raw = ~on_raw
both_cm = np.outer(creamer_mask, creamer_mask)[ii_all, jj_all]
class4  = off_raw & both_cm          # Class 4 mask (1321 pairs)
n_class4 = int(class4.sum())

class4_idx = np.where(class4)[0]    # indices into ii_all/jj_all

print(f"Stage 3 LOO | N={N}, N_REC={N_REC}, Class 4={n_class4}")
print(f"  λ_on={LAM_ON}, λ_off={LAM_OFF}, MIN_CP={MIN_CP}, PSD_FLOOR={PSD_FLOOR}")


# ── Utilities ────────────────────────────────────────────────────────────────

def psd_project(S):
    S_sym = (S + S.T) / 2
    ev, vc = np.linalg.eigh(S_sym)
    n_clip = int((ev < PSD_FLOOR).sum())
    S_proj = (vc @ np.diag(np.maximum(ev, PSD_FLOOR)) @ vc.T + S_sym.T) / 2
    return S_proj, n_clip


def admm_z(S_proj, lam_on, lam_off, rho=1.0, max_iter=1000, tol=1e-5):
    L = np.where(A_raw > 0, lam_on, lam_off).astype(float)
    np.fill_diagonal(L, 0.0)
    Theta = np.eye(N); Z = np.eye(N); U = np.zeros((N, N))
    for _ in range(max_iter):
        B = Z - U - S_proj / rho; B = (B + B.T) / 2
        ev, vc = np.linalg.eigh(B)
        Theta = vc @ np.diag((ev + np.sqrt(ev**2 + 4/rho)) / 2) @ vc.T
        W = Theta + U
        Z_new = np.sign(W) * np.maximum(np.abs(W) - L/rho, 0.0)
        Z_new[np.arange(N), np.arange(N)] = W[np.arange(N), np.arange(N)]
        res = Theta - Z_new; U += res; Z = Z_new
        if np.max(np.abs(res)) < tol:
            break
    return Z


def assemble_pairwise(n_frames, suf_xi, suf_xii, suf_xixj, mask_r, s_int):
    """Assemble (N,N) pairwise covariance from a subset of recordings."""
    S = np.zeros((N, N), dtype=np.float64)
    nf_s = n_frames[:, :, s_int]         # (N_REC, N)
    xi_s = suf_xi[:, :, s_int]           # (N_REC, N)
    xii_s = suf_xii[:, :, s_int]         # (N_REC, N)
    xij_s = suf_xixj[:, :, :, s_int]    # (N_REC, N, N)

    # Off-diagonal
    for i in range(N):
        for j in range(i + 1, N):
            cp = mask_r & (nf_s[:, i] > 0) & (nf_s[:, j] > 0)
            if cp.sum() < MIN_CP:
                continue
            T = int(nf_s[cp, i].sum())
            if T < 2:
                continue
            Sxi  = float(xi_s[cp, i].sum())
            Sxj  = float(xi_s[cp, j].sum())
            Sxij = float(xij_s[cp, i, j].sum())
            mi = Sxi / T; mj = Sxj / T
            S[i, j] = S[j, i] = (Sxij - T * mi * mj) / (T - 1)

    # Diagonal
    for i in range(N):
        pres = mask_r & (nf_s[:, i] > 0)
        Ti = int(nf_s[pres, i].sum())
        if Ti < 2:
            S[i, i] = 1.0; continue
        Sxi  = float(xi_s[pres, i].sum())
        Sxii = float(xii_s[pres, i].sum())
        mi   = Sxi / Ti
        v    = (Sxii - Ti * mi**2) / (Ti - 1)
        S[i, i] = v if v > 0 else 1.0

    return S


def rank_class4(dq_mat):
    """Return rank array for Class 4 pairs (lower rank = higher |ΔQ|)."""
    abs_dq = np.abs(dq_mat[ii_all, jj_all])[class4_idx]
    return np.argsort(np.argsort(-abs_dq))   # rank 0 = largest


# ── Load full-data ΔQ and reference rankings ─────────────────────────────────

DQ_full = {}
ranks_full = {}
top50_full = {}

for coord in ["cepnem", "gcamp"]:
    DQ = np.load(STG2_DIR / f"DQ_{coord}.npy")
    DQ_full[coord]    = DQ
    ranks_full[coord] = rank_class4(DQ)
    top50_full[coord] = set(np.argsort(ranks_full[coord])[:50])   # indices into class4_idx
    dq_c4 = np.abs(DQ[ii_all, jj_all])[class4_idx]
    print(f"  Full-data {coord}: n_nonzero={int((dq_c4>1e-9).sum())}, "
          f"max={dq_c4.max():.4f}")


# ── Load sufficient statistics ────────────────────────────────────────────────

suff = {}
for coord in ["cepnem", "gcamp"]:
    suff[coord] = {
        "n_frames": np.load(SUFF_DIR / f"n_frames_{coord}.npy"),   # (N_REC, N, 2)
        "suf_xi":   np.load(SUFF_DIR / f"suf_xi_{coord}.npy"),     # (N_REC, N, 2)
        "suf_xii":  np.load(SUFF_DIR / f"suf_xii_{coord}.npy"),    # (N_REC, N, 2)
        "suf_xixj": np.load(SUFF_DIR / f"suf_xixj_{coord}.npy"),   # (N_REC, N, N, 2)
    }

# Identify which recordings contribute to each state, per coord
contrib = {}
for coord in ["cepnem", "gcamp"]:
    nf = suff[coord]["n_frames"]
    contrib[coord] = {
        "roam":  [r for r in range(N_REC) if nf[r, :, 1].sum() > 0],
        "dwell": [r for r in range(N_REC) if nf[r, :, 0].sum() > 0],
    }
    print(f"  {coord}: roam={len(contrib[coord]['roam'])} recs, "
          f"dwell={len(contrib[coord]['dwell'])} recs")


# ── LOO main loop ─────────────────────────────────────────────────────────────

print(f"\nRunning LOO ({N_REC} iterations × 2 coords) ...")
t_loo = time.time()

loo_results = {coord: [] for coord in ["cepnem", "gcamp"]}

for r_idx in range(N_REC):
    rec_id = REC_IDS[r_idx]

    for coord in ["cepnem", "gcamp"]:
        nf  = suff[coord]["n_frames"]
        xi  = suff[coord]["suf_xi"]
        xii = suff[coord]["suf_xii"]
        xij = suff[coord]["suf_xixj"]

        # Mask for all recordings EXCEPT r_idx
        mask_loo = np.ones(N_REC, dtype=bool)
        mask_loo[r_idx] = False

        # Assemble LOO covariance for each state
        S_roam_loo  = assemble_pairwise(nf, xi, xii, xij, mask_loo, 1)
        S_dwell_loo = assemble_pairwise(nf, xi, xii, xij, mask_loo, 0)

        # PSD project
        S_roam_proj,  n_clip_r = psd_project(S_roam_loo)
        S_dwell_proj, n_clip_d = psd_project(S_dwell_loo)

        # ADMM confirmation
        Q_roam_loo  = admm_z(S_roam_proj,  LAM_ON, LAM_OFF)
        Q_dwell_loo = admm_z(S_dwell_proj, LAM_ON, LAM_OFF)

        # LOO ΔQ
        DQ_loo = Q_roam_loo - Q_dwell_loo

        # Class 4 ranking in LOO
        ranks_loo = rank_class4(DQ_loo)
        top50_loo = set(np.argsort(ranks_loo)[:50])

        # Retention of full-data top-50 in LOO top-50
        retention = len(top50_full[coord] & top50_loo) / 50.0

        # Spearman rank correlation over ALL Class 4 pairs
        rho_spear = float(stats.spearmanr(ranks_full[coord], ranks_loo)[0])

        # Spearman over top-100 full-data pairs (more sensitive to top changes)
        top100_full_idx = np.argsort(ranks_full[coord])[:100]
        rho_top100 = float(stats.spearmanr(
            ranks_full[coord][top100_full_idx],
            ranks_loo[top100_full_idx]
        )[0])

        # ΔQ correlation (raw values)
        dq_full_c4 = np.abs(DQ_full[coord][ii_all, jj_all])[class4_idx]
        dq_loo_c4  = np.abs(DQ_loo[ii_all, jj_all])[class4_idx]
        rho_dq = float(stats.pearsonr(dq_full_c4, dq_loo_c4)[0])

        r_contributes_roam  = r_idx in contrib[coord]["roam"]
        r_contributes_dwell = r_idx in contrib[coord]["dwell"]

        loo_results[coord].append({
            "recording_idx":   r_idx,
            "recording_id":    rec_id,
            "contributes_roam":  r_contributes_roam,
            "contributes_dwell": r_contributes_dwell,
            "retention_top50": float(retention),
            "spearman_all":    rho_spear,
            "spearman_top100": rho_top100,
            "pearson_dq":      rho_dq,
            "n_psd_clip_roam": n_clip_r,
            "n_psd_clip_dwell": n_clip_d,
        })

    elapsed = time.time() - t_loo
    if (r_idx + 1) % 10 == 0:
        remaining = elapsed / (r_idx + 1) * (N_REC - r_idx - 1)
        print(f"  {r_idx+1}/{N_REC} done  ({elapsed:.0f}s elapsed, "
              f"~{remaining:.0f}s remaining)")

print(f"\nLOO complete. Total: {time.time()-t_loo:.0f}s")


# ── Aggregate metrics and influential recording identification ─────────────────

metrics = {}
RETENTION_THRESHOLD  = 0.70
SPEARMAN_THRESHOLD   = 0.70
INFLUENCE_THRESHOLD  = 0.70   # retention drop below this flags a recording

for coord in ["cepnem", "gcamp"]:
    res = loo_results[coord]
    retentions   = np.array([r["retention_top50"] for r in res])
    spearman_all = np.array([r["spearman_all"]    for r in res])
    spearman_100 = np.array([r["spearman_top100"] for r in res])
    pearson_dq   = np.array([r["pearson_dq"]      for r in res])

    # Influential = retention drops BELOW threshold when that recording is removed
    influential_mask = retentions < INFLUENCE_THRESHOLD
    influential_recs = [res[r]["recording_id"] for r in np.where(influential_mask)[0]]

    metrics[coord] = {
        "retention_median":    float(np.median(retentions)),
        "retention_mean":      float(np.mean(retentions)),
        "retention_min":       float(np.min(retentions)),
        "retention_p25":       float(np.percentile(retentions, 25)),
        "retention_p75":       float(np.percentile(retentions, 75)),
        "n_below_07":          int(influential_mask.sum()),
        "spearman_all_median": float(np.median(spearman_all)),
        "spearman_all_min":    float(np.min(spearman_all)),
        "spearman_top100_median": float(np.median(spearman_100)),
        "pearson_dq_median":   float(np.median(pearson_dq)),
        "pearson_dq_min":      float(np.min(pearson_dq)),
        "influential_recordings": influential_recs,
        "pass_median_ge_070":  float(np.median(retentions)) >= RETENTION_THRESHOLD,
    }

    print(f"\n  {coord}:")
    print(f"    Retention top-50: median={metrics[coord]['retention_median']:.3f}  "
          f"min={metrics[coord]['retention_min']:.3f}  "
          f"p25={metrics[coord]['retention_p25']:.3f}  "
          f"[{'PASS' if metrics[coord]['pass_median_ge_070'] else 'FAIL'} ≥0.70]")
    print(f"    Spearman (all C4): median={metrics[coord]['spearman_all_median']:.4f}  "
          f"min={metrics[coord]['spearman_all_min']:.4f}")
    print(f"    Pearson |ΔQ|: median={metrics[coord]['pearson_dq_median']:.4f}  "
          f"min={metrics[coord]['pearson_dq_min']:.4f}")
    print(f"    Influential recordings (retention<0.70): "
          f"{metrics[coord]['n_below_07']}  {influential_recs}")


# ── DEV-005 Assessment ────────────────────────────────────────────────────────

print("\nDEV-005 Assessment — all-animal pooling without outlier screening ...")

# DEV-005: no systematic outlier identification was done before Stage 1.
# LOO provides the post-hoc check: if removing any single recording
# causes retention < 0.70, that recording is disproportionately influential.

dev005_cepnem = metrics["cepnem"]
dev005_gcamp  = metrics["gcamp"]

dev005_pass_cepnem = len(dev005_cepnem["influential_recordings"]) == 0
dev005_pass_gcamp  = len(dev005_gcamp["influential_recordings"])  == 0

dev005_assessment = {
    "description": (
        "DEV-005: all-animal pooling without prior outlier screening. "
        "LOO provides the post-hoc sensitivity check. A recording is flagged as "
        "influential if removing it reduces top-50 Class 4 pair retention below 0.70."
    ),
    "cepnem": {
        "n_influential": len(dev005_cepnem["influential_recordings"]),
        "influential_recordings": dev005_cepnem["influential_recordings"],
        "min_retention": dev005_cepnem["retention_min"],
        "verdict": "No influential recordings found." if dev005_pass_cepnem
                   else f"{len(dev005_cepnem['influential_recordings'])} influential recordings flagged.",
    },
    "gcamp": {
        "n_influential": len(dev005_gcamp["influential_recordings"]),
        "influential_recordings": dev005_gcamp["influential_recordings"],
        "min_retention": dev005_gcamp["retention_min"],
        "verdict": "No influential recordings found." if dev005_pass_gcamp
                   else f"{len(dev005_gcamp['influential_recordings'])} influential recordings flagged.",
    },
    "overall_verdict": (
        "DEV-005 COMPENSATED: No single recording drives the ΔQ structure in either coordinate."
        if (dev005_pass_cepnem and dev005_pass_gcamp)
        else "DEV-005 UNRESOLVED: At least one influential recording identified. "
             "See influential_recordings lists."
    ),
}

print(f"  CePNEM: {dev005_assessment['cepnem']['verdict']}")
print(f"  GCaMP:  {dev005_assessment['gcamp']['verdict']}")
print(f"  Overall: {dev005_assessment['overall_verdict']}")


# ── Save all outputs ──────────────────────────────────────────────────────────

results_full = {
    "date": "2026-06-01",
    "stage": "3",
    "authorization": "2026-06-01 human supervisor",
    "n_recordings": N_REC,
    "n_class4_pairs": n_class4,
    "thresholds": {
        "retention_threshold": RETENTION_THRESHOLD,
        "spearman_threshold": SPEARMAN_THRESHOLD,
        "min_copresence": MIN_CP,
    },
    "summary_metrics": metrics,
    "dev005_assessment": dev005_assessment,
    "pass_conditions": {
        "cepnem_median_retention_ge_070": metrics["cepnem"]["pass_median_ge_070"],
        "gcamp_median_retention_ge_070":  metrics["gcamp"]["pass_median_ge_070"],
    },
    "per_recording_cepnem": loo_results["cepnem"],
    "per_recording_gcamp":  loo_results["gcamp"],
}

with open(OUT_DIR / "stage3_results.json", "w") as f:
    json.dump(results_full, f, indent=2)
print(f"\nSaved: results/phase2/stage3/stage3_results.json")

# Per-recording arrays for plotting
for coord in ["cepnem", "gcamp"]:
    ret = np.array([r["retention_top50"] for r in loo_results[coord]])
    spr = np.array([r["spearman_all"]    for r in loo_results[coord]])
    np.save(OUT_DIR / f"retention_{coord}.npy", ret)
    np.save(OUT_DIR / f"spearman_{coord}.npy",  spr)

print("Saved: retention_*.npy, spearman_*.npy")


# ── Stage 3 report ────────────────────────────────────────────────────────────

def fmt_rec(r): return r.replace("-", "‑")   # non-breaking hyphens for readability

lines = [
    "# Stage 3 Report — LOO Sensitivity Analysis",
    "Date: 2026-06-01",
    "",
    "## Pass Conditions (phase2_task.md §3.1)",
    "",
    "| Condition | CePNEM | GCaMP |",
    "|---|---|---|",
    f"| Median top-50 retention ≥ 0.70 | "
    f"{'**PASS**' if metrics['cepnem']['pass_median_ge_070'] else '**FAIL**'} "
    f"({metrics['cepnem']['retention_median']:.3f}) | "
    f"{'**PASS**' if metrics['gcamp']['pass_median_ge_070'] else '**FAIL**'} "
    f"({metrics['gcamp']['retention_median']:.3f}) |",
    "",
    "## Retention Summary",
    "",
    "| Metric | CePNEM | GCaMP |",
    "|---|---|---|",
]
for key, label in [
    ("retention_median", "Median"),
    ("retention_mean",   "Mean"),
    ("retention_min",    "Min"),
    ("retention_p25",    "25th percentile"),
    ("retention_p75",    "75th percentile"),
    ("n_below_07",       "N recordings with retention < 0.70"),
]:
    lines.append(
        f"| {label} | {metrics['cepnem'][key]:.3f if isinstance(metrics['cepnem'][key], float) else metrics['cepnem'][key]} | "
        f"{metrics['gcamp'][key]:.3f if isinstance(metrics['gcamp'][key], float) else metrics['gcamp'][key]} |"
    )

lines += [
    "",
    "## Rank Correlation Summary",
    "",
    "| Metric | CePNEM | GCaMP |",
    "|---|---|---|",
    f"| Spearman (all Class 4, median) | {metrics['cepnem']['spearman_all_median']:.4f} | {metrics['gcamp']['spearman_all_median']:.4f} |",
    f"| Spearman (all Class 4, min) | {metrics['cepnem']['spearman_all_min']:.4f} | {metrics['gcamp']['spearman_all_min']:.4f} |",
    f"| Spearman (top-100, median) | {metrics['cepnem']['spearman_top100_median']:.4f} | {metrics['gcamp']['spearman_top100_median']:.4f} |",
    f"| Pearson |ΔQ| (median) | {metrics['cepnem']['pearson_dq_median']:.4f} | {metrics['gcamp']['pearson_dq_median']:.4f} |",
    f"| Pearson |ΔQ| (min) | {metrics['cepnem']['pearson_dq_min']:.4f} | {metrics['gcamp']['pearson_dq_min']:.4f} |",
    "",
    "## Per-Recording Retention",
    "",
    "| Rec | ID | CePNEM ret. | GCaMP ret. | CePNEM ρ | GCaMP ρ | Roam? | Influential? |",
    "|---|---|---|---|---|---|---|---|",
]

for r_idx in range(N_REC):
    ce = loo_results["cepnem"][r_idx]
    gc = loo_results["gcamp"][r_idx]
    influenced = ce["retention_top50"] < INFLUENCE_THRESHOLD or gc["retention_top50"] < INFLUENCE_THRESHOLD
    lines.append(
        f"| {r_idx:2d} | {REC_IDS[r_idx]} | "
        f"{ce['retention_top50']:.3f} | {gc['retention_top50']:.3f} | "
        f"{ce['spearman_all']:.4f} | {gc['spearman_all']:.4f} | "
        f"{'YES' if ce['contributes_roam'] else ''} | "
        f"{'**FLAG**' if influenced else ''} |"
    )

lines += [
    "",
    "## DEV-005 Assessment",
    "",
    "DEV-005: All-animal pooling without prior systematic outlier screening.",
    "LOO provides the post-hoc sensitivity check.",
    "A recording is flagged as influential if removing it reduces top-50 retention below 0.70.",
    "",
    f"**CePNEM:** {dev005_assessment['cepnem']['verdict']} "
    f"(min retention = {dev005_assessment['cepnem']['min_retention']:.3f})",
    f"**GCaMP:** {dev005_assessment['gcamp']['verdict']} "
    f"(min retention = {dev005_assessment['gcamp']['min_retention']:.3f})",
    "",
    f"**Overall verdict:** {dev005_assessment['overall_verdict']}",
    "",
    "## Coordinate-Specific Sensitivity",
    "",
]

for coord in ["cepnem", "gcamp"]:
    m = metrics[coord]
    lines += [
        f"**{coord.upper()}:**",
        f"  Retention range: [{m['retention_min']:.3f}, 1.000], median={m['retention_median']:.3f}",
        f"  Spearman range: [{m['spearman_all_min']:.4f}, 1.000], median={m['spearman_all_median']:.4f}",
        "",
    ]

lines += [
    "## Next Step",
    "",
    "Stage 4 (enrichment tests) requires **explicit human authorization**.",
    "Do NOT begin enrichment analysis automatically.",
    "",
    "---",
    "*Stage 3 scope: LOO sensitivity, rank stability, influential-recording identification, DEV-005 assessment. No enrichment statistics.*",
]

with open(OUT_DIR / "stage3_report.md", "w") as f:
    f.write("\n".join(lines))
print("Saved: results/phase2/stage3/stage3_report.md")
print(f"\n=== STAGE 3 COMPLETE. Await Stage 4 authorization. ===")
