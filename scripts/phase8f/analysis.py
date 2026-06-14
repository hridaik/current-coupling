"""
Phase 8F: What is the framework actually recovering?

Uses frozen framework_output.json, ground_truth/labels.json,
results/phase7c/canonical/data/ (oracle_z runs for |ΔCorr|),
and ground_truth/A_sparse.npy for structural metadata.

No new simulations. No framework changes. No label changes.
"""

import json
import os
import sys
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(ROOT, 'results', 'phase8f')
os.makedirs(OUT, exist_ok=True)

DATA_DIR = os.path.join(ROOT, 'results', 'phase7c', 'canonical', 'data')
SA = frozenset({132, 133, 134, 135, 136, 137, 138, 139})
N_OBS = 100

RNG = np.random.default_rng(42)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_framework_output():
    with open(os.path.join(ROOT, 'framework_output.json')) as f:
        d = json.load(f)
    preds = d['predictions']
    # Build (i,j) -> {class_prob, class_pred} dict + sorted ranking by C-score
    pred_map = {(p['i'], p['j']): p for p in preds}
    ranked_c = sorted(preds, key=lambda x: x['class_prob']['C'], reverse=True)
    ranked_s = sorted(preds, key=lambda x: x['class_prob']['S'], reverse=True)
    ranked_lr = sorted(preds, key=lambda x: x['class_prob']['C'] + x['class_prob']['M'], reverse=True)
    return pred_map, ranked_c, ranked_s, ranked_lr, preds


def load_labels():
    with open(os.path.join(ROOT, 'ground_truth', 'labels.json')) as f:
        ld = json.load(f)
    raw = ld['labels']
    labels = {(d['i'], d['j']): d['label'] for d in raw}
    return labels, raw


def load_A_sparse():
    return np.load(os.path.join(ROOT, 'ground_truth', 'A_sparse.npy'))


def load_oracle_runs():
    runs = []
    for r in range(5):
        path = os.path.join(DATA_DIR, f'oracle_z_run{r}.npz')
        data = np.load(path)
        runs.append({'y': data['y'].astype(np.float64),
                     'z_oracle': data['z_oracle'].astype(np.float64)})
    return runs


# ---------------------------------------------------------------------------
# Derived quantities
# ---------------------------------------------------------------------------

def compute_module(neuron):
    """Module assignment: M1=0..24, M2=25..49, M3=50..74, M4=75..99."""
    return neuron // 25 + 1


def compute_path_strength(i, j, A):
    """
    Max path_strength across all H2 witnesses h in SA.
    path_strength(i->j via h) = |A[h,i]| * |A[j,h]|
    """
    best = 0.0
    for h in SA:
        v = abs(A[h, i]) * abs(A[j, h])
        if v > best:
            best = v
    return best


def compute_sareachable(i, j, A):
    """True if any h in SA has A[h,i]!=0 and A[j,h]!=0."""
    for h in SA:
        if A[h, i] != 0 and A[j, h] != 0:
            return True
    return False


def compute_direct(i, j, A):
    """True if direct coupling in obs submatrix."""
    return A[i, j] != 0 or A[j, i] != 0


def compute_state_sensitivity(runs):
    """
    |ΔCorr|(i,j) = |corr(y|z>median) - corr(y|z≤median)| averaged across runs.
    Returns (N_OBS, N_OBS) matrix.
    """
    delta_acc = np.zeros((N_OBS, N_OBS))
    for run in runs:
        y = run['y']
        z = run['z_oracle']
        med = np.median(z)
        y_hi = y[z > med]
        y_lo = y[z <= med]
        corr_hi = np.corrcoef(y_hi.T)
        corr_lo = np.corrcoef(y_lo.T)
        delta_acc += np.abs(corr_hi - corr_lo)
    return delta_acc / len(runs)


def compute_raw_corr(runs):
    """Mean |corr(y_i, y_j)| across runs."""
    corr_acc = np.zeros((N_OBS, N_OBS))
    for run in runs:
        corr_acc += np.abs(np.corrcoef(run['y'].T))
    return corr_acc / len(runs)


# ---------------------------------------------------------------------------
# Enrichment helpers
# ---------------------------------------------------------------------------

def enrichment_or(scores_all, is_target, k, n_perm=10000):
    """
    Top-k enrichment odds ratio and permutation p-value.
    Returns: observed, expected, OR, p_value, precision
    """
    N = len(scores_all)
    n_pos = is_target.sum()
    top_idx = np.argsort(scores_all)[::-1][:k]
    observed = int(is_target[top_idx].sum())
    expected = float(k * n_pos / N)

    if n_pos == 0 or n_pos == N:
        return observed, expected, np.nan, np.nan, float(observed / k)

    n_not = N - n_pos
    # OR = (obs*(n_not)) / (n_pos*(k-obs))  — handle zeros
    num = observed * n_not
    den = n_pos * max(k - observed, 1)
    or_val = float(num / den) if den > 0 else np.inf

    perm_obs = np.array([
        int(is_target[RNG.choice(N, k, replace=False)].sum())
        for _ in range(n_perm)
    ])
    p_value = float((perm_obs >= observed).mean())
    return observed, expected, or_val, p_value, float(observed / k)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    pred_map, ranked_c, ranked_s, ranked_lr, all_preds = load_framework_output()
    labels, label_records = load_labels()
    A = load_A_sparse()
    print("Loading oracle runs (for |ΔCorr|)...")
    runs = load_oracle_runs()
    delta_corr = compute_state_sensitivity(runs)
    raw_corr   = compute_raw_corr(runs)
    print("Precomputing structural metadata...")

    # Build per-pair metadata lookup
    meta = {}
    for rec in label_records:
        i, j = rec['i'], rec['j']
        direct = compute_direct(i, j, A)
        sareachable = compute_sareachable(i, j, A)
        path_str = compute_path_strength(i, j, A)
        meta[(i, j)] = {
            'label': rec['label'],
            'direct': direct,
            'sareachable': sareachable,
            'path_strength': path_str,
            'mod_i': compute_module(i),
            'mod_j': compute_module(j),
            'same_module': compute_module(i) == compute_module(j),
            'delta_corr': float(delta_corr[i, j]),
            'raw_corr': float(raw_corr[i, j]),
        }

    # Build arrays over all 9900 pairs (in C-score ranking order)
    # We'll use pair index as reference
    all_i  = np.array([p['i'] for p in ranked_c])
    all_j  = np.array([p['j'] for p in ranked_c])
    c_scores  = np.array([p['class_prob']['C'] for p in ranked_c])
    s_scores  = np.array([p['class_prob']['S'] for p in ranked_c])
    lr_scores = np.array([p['class_prob']['C'] + p['class_prob']['M'] for p in ranked_c])
    all_labels    = np.array([meta[(p['i'],p['j'])]['label'] for p in ranked_c])
    all_direct    = np.array([meta[(p['i'],p['j'])]['direct'] for p in ranked_c])
    all_sareable  = np.array([meta[(p['i'],p['j'])]['sareachable'] for p in ranked_c])
    all_pathstr   = np.array([meta[(p['i'],p['j'])]['path_strength'] for p in ranked_c])
    all_mod_i     = np.array([meta[(p['i'],p['j'])]['mod_i'] for p in ranked_c])
    all_mod_j     = np.array([meta[(p['i'],p['j'])]['mod_j'] for p in ranked_c])
    all_same_mod  = np.array([meta[(p['i'],p['j'])]['same_module'] for p in ranked_c])
    all_dcorr     = np.array([meta[(p['i'],p['j'])]['delta_corr'] for p in ranked_c])
    all_rawcorr   = np.array([meta[(p['i'],p['j'])]['raw_corr'] for p in ranked_c])

    is_S  = all_labels == 'S'
    is_C  = all_labels == 'C'
    is_M  = all_labels == 'M'
    is_N  = all_labels == 'N'
    is_LR = all_sareable  # LR = SAREACHABLE

    n_total = len(ranked_c)
    n_S, n_C, n_M, n_N, n_LR = is_S.sum(), is_C.sum(), is_M.sum(), is_N.sum(), is_LR.sum()

    print(f"Class counts: S={n_S}, C={n_C}, M={n_M}, N={n_N}, LR={n_LR}, total={n_total}")

    # ===========================================================================
    # F1: TOP-K INVENTORY
    # ===========================================================================
    print("\n=== F1: Top-K Inventory ===")

    f1_rows = []
    for rank, p in enumerate(ranked_c[:100], start=1):
        i, j = p['i'], p['j']
        m = meta[(i, j)]
        f1_rows.append({
            'rank': rank,
            'i': i, 'j': j,
            'label': m['label'],
            'c_score': p['class_prob']['C'],
            's_score': p['class_prob']['S'],
            'class_pred': p['class_pred'],
            'mod_i': m['mod_i'],
            'mod_j': m['mod_j'],
            'same_module': bool(m['same_module']),
            'sareachable': bool(m['sareachable']),
            'direct': bool(m['direct']),
            'path_strength': m['path_strength'],
            'delta_corr': m['delta_corr'],
            'raw_corr': m['raw_corr'],
        })

    # Print top-10
    print("Top-10 by C-score:")
    for r in f1_rows[:10]:
        print(f"  rank={r['rank']} ({r['i']},{r['j']}) label={r['label']} "
              f"M{r['mod_i']}→M{r['mod_j']} {'same' if r['same_module'] else 'cross'} "
              f"direct={r['direct']} SA={r['sareachable']} "
              f"C-score={r['c_score']:.4f} |ΔCorr|={r['delta_corr']:.4f}")

    # Save
    with open(os.path.join(OUT, 'f1_topk_inventory_data.json'), 'w') as f:
        json.dump(f1_rows, f, indent=2)
    print(f"  Saved f1_topk_inventory_data.json ({len(f1_rows)} pairs)")

    # ===========================================================================
    # F2: CLASS COMPOSITION
    # ===========================================================================
    print("\n=== F2: Class Composition ===")

    ks = [10, 20, 50, 100]
    f2_results = {}

    for k in ks:
        top_labels = all_labels[:k]
        top_direct = all_direct[:k]
        top_sa     = all_sareable[:k]

        n_s_obs = (top_labels == 'S').sum()
        n_c_obs = (top_labels == 'C').sum()
        n_m_obs = (top_labels == 'M').sum()
        n_n_obs = (top_labels == 'N').sum()
        n_lr_obs = top_sa.sum()

        # Expected under base rate
        exp_S  = float(k * n_S / n_total)
        exp_C  = float(k * n_C / n_total)
        exp_M  = float(k * n_M / n_total)
        exp_N  = float(k * n_N / n_total)

        def calc_or(obs, n_class, k, n_total):
            n_not = n_total - n_class
            num = obs * n_not
            den = n_class * max(k - obs, 1)
            return float(num / den) if den > 0 else np.inf

        obs_S_ct, exp_S_ct, or_S, p_S, prec_S = enrichment_or(c_scores, is_S, k)
        obs_C_ct, exp_C_ct, or_C, p_C, prec_C = enrichment_or(c_scores, is_C, k)
        obs_N_ct, exp_N_ct, or_N, p_N, prec_N = enrichment_or(c_scores, is_N, k)

        result = {
            'k': k,
            'S': {'obs': int(n_s_obs), 'exp': round(exp_S, 2), 'pct': round(100*n_s_obs/k, 1), 'or': round(or_S, 3), 'p': round(p_S, 4)},
            'C': {'obs': int(n_c_obs), 'exp': round(exp_C, 2), 'pct': round(100*n_c_obs/k, 1), 'or': round(or_C, 4), 'p': round(p_C, 4)},
            'M': {'obs': int(n_m_obs), 'exp': round(float(k*n_M/n_total), 2), 'pct': round(100*n_m_obs/k, 1)},
            'N': {'obs': int(n_n_obs), 'exp': round(exp_N, 2), 'pct': round(100*n_n_obs/k, 1), 'or': round(or_N, 3), 'p': round(p_N, 4)},
            'LR': {'obs': int(n_lr_obs), 'exp': round(float(k*n_LR/n_total), 2), 'pct': round(100*n_lr_obs/k, 1)},
        }
        f2_results[k] = result
        print(f"  k={k}: S={n_s_obs}({round(100*n_s_obs/k)}%) C={n_c_obs}({round(100*n_c_obs/k)}%) "
              f"M={n_m_obs} N={n_n_obs}({round(100*n_n_obs/k)}%) LR={n_lr_obs} "
              f"|| or_S={round(or_S,2)} p_S={round(p_S,4)} || or_C={round(or_C,4)} p_C={round(p_C,4)} || or_N={round(or_N,2)} p_N={round(p_N,4)}")

    with open(os.path.join(OUT, 'f2_class_composition_data.json'), 'w') as f:
        json.dump(f2_results, f, indent=2)

    # ===========================================================================
    # F3: STATE DEPENDENCE
    # ===========================================================================
    print("\n=== F3: State Dependence ===")

    f3_results = {}
    for k in ks:
        top_dc = all_dcorr[:k]
        all_dc = all_dcorr
        c_dc   = all_dcorr[is_C]
        top10pct_c_mask = is_C & (all_dcorr >= np.quantile(all_dcorr[is_C], 0.90))
        top10pct_dc = all_dcorr[top10pct_c_mask]

        def desc(arr):
            return {
                'mean': float(np.mean(arr)),
                'median': float(np.median(arr)),
                'std': float(np.std(arr)),
                'p10': float(np.percentile(arr, 10)),
                'p90': float(np.percentile(arr, 90)),
            }

        # Mann-Whitney test: top-k dcorr vs all-pair dcorr
        mw_stat, mw_p = stats.mannwhitneyu(top_dc, all_dc, alternative='greater')
        result = {
            'k': k,
            'top_k_dcorr': desc(top_dc),
            'all_dcorr': desc(all_dc),
            'C_class_dcorr': desc(c_dc),
            'top10pct_C_dcorr': desc(top10pct_dc) if len(top10pct_dc) > 0 else None,
            'mw_topk_gt_all_p': float(mw_p),
            'n_top10pct_C_in_topk': int(top10pct_c_mask[:k].sum()),
        }
        f3_results[k] = result
        print(f"  k={k}: top-k mean|ΔCorr|={np.mean(top_dc):.4f} "
              f"vs all_mean={np.mean(all_dc):.4f} C_mean={np.mean(c_dc):.4f} "
              f"mw_p={mw_p:.4f} top10%C in top-k={top10pct_c_mask[:k].sum()}")

    with open(os.path.join(OUT, 'f3_state_dependence_data.json'), 'w') as f:
        json.dump(f3_results, f, indent=2)

    # ===========================================================================
    # F4: OFF-CONNECTOME ORGANIZATION
    # ===========================================================================
    print("\n=== F4: Off-Connectome Organization ===")

    f4_results = {}
    c_indices_in_ranked = np.where(is_C)[0]  # positions of C pairs in C-score ranking

    for k in ks:
        top_direct = all_direct[:k]
        top_sa     = all_sareable[:k]
        top_labels_k = all_labels[:k]

        n_offconn_top = int((~top_direct).sum())  # off-connectome = not direct
        n_onconn_top  = int(top_direct.sum())

        # Where do C pairs rank?
        c_ranks = c_indices_in_ranked + 1  # 1-indexed
        top_c_bool = top_labels_k == 'C'

        # Compare against top-k C by |ΔCorr|
        c_dcorr_sorted_idx = np.argsort(all_dcorr[is_C])[::-1][:k]
        # These are within-C indices; need to map back to labels
        # Just characterize top-k by C-score vs top-k C pairs by |ΔCorr|

        result = {
            'k': k,
            'n_off_connectome': n_offconn_top,
            'n_on_connectome': n_onconn_top,
            'pct_off_connectome': round(100 * n_offconn_top / k, 1),
            'pct_on_connectome': round(100 * n_onconn_top / k, 1),
            'n_sareachable': int(top_sa.sum()),
            'n_C_in_topk': int(top_c_bool.sum()),
            'n_S_in_topk': int((top_labels_k == 'S').sum()),
            'n_N_in_topk': int((top_labels_k == 'N').sum()),
            # For C pairs: where do they rank?
            'C_rank_p10': float(np.percentile(c_ranks, 10)),
            'C_rank_median': float(np.median(c_ranks)),
            'C_rank_p90': float(np.percentile(c_ranks, 90)),
            'C_rank_mean': float(np.mean(c_ranks)),
        }
        f4_results[k] = result
        print(f"  k={k}: off-conn={n_offconn_top}({round(100*n_offconn_top/k)}%) "
              f"on-conn={n_onconn_top}({round(100*n_onconn_top/k)}%) "
              f"C_in_topk={int(top_c_bool.sum())} N_in_topk={int((top_labels_k=='N').sum())}")

    print(f"  C-pair rank distribution: median={np.median(c_ranks):.0f} "
          f"p10={np.percentile(c_ranks,10):.0f} p90={np.percentile(c_ranks,90):.0f}")

    with open(os.path.join(OUT, 'f4_offconnectome_data.json'), 'w') as f:
        json.dump(f4_results, f, indent=2)

    # ===========================================================================
    # F5: MODULE STRUCTURE
    # ===========================================================================
    print("\n=== F5: Module Structure ===")

    # Module interaction matrix: 4x4 counts in top-k
    modules = [1, 2, 3, 4]

    f5_results = {}
    for k in ks:
        top_mod_i = all_mod_i[:k]
        top_mod_j = all_mod_j[:k]
        top_same  = all_same_mod[:k]

        # Module pair counts
        mod_matrix = np.zeros((4, 4), dtype=int)
        for mi, mj in zip(top_mod_i, top_mod_j):
            mod_matrix[mi-1, mj-1] += 1

        n_within  = int(top_same.sum())
        n_between = k - n_within
        exp_within = float(k * 4 * (25*24) / (n_total))  # approx
        base_within = 4 * 25 * 24  # directed within-module pairs
        base_between = n_total - base_within
        or_within, _, _, p_within_perm, _ = enrichment_or(
            -all_same_mod.astype(float),  # negate so "within" is at top
            all_same_mod,
            k
        )
        # Redo proper within-module enrichment
        obs_wm, exp_wm, or_wm, p_wm, prec_wm = enrichment_or(
            c_scores,  # using c_scores as ranking key
            all_same_mod.astype(bool),
            k
        )

        result = {
            'k': k,
            'n_within_module': n_within,
            'n_between_module': n_between,
            'pct_within': round(100*n_within/k, 1),
            'base_rate_within': round(100*base_within/n_total, 1),
            'or_within': round(or_wm, 3),
            'p_within': round(p_wm, 4),
            'module_matrix': mod_matrix.tolist(),
        }
        f5_results[k] = result
        print(f"  k={k}: within-module={n_within}({round(100*n_within/k)}%) "
              f"(base={round(100*base_within/n_total)}%) "
              f"or_within={round(or_wm,3)} p={round(p_wm,4)}")
        print(f"    Module matrix:\n    {mod_matrix.tolist()}")

    with open(os.path.join(OUT, 'f5_module_structure_data.json'), 'w') as f:
        json.dump({str(k): v for k,v in f5_results.items()}, f, indent=2)

    # ===========================================================================
    # F6: SIGNAL TRACKING — CORRELATES OF C-SCORE
    # ===========================================================================
    print("\n=== F6: Signal Tracking ===")

    c_score_all = np.array([p['class_prob']['C'] for p in all_preds])
    s_score_all = np.array([p['class_prob']['S'] for p in all_preds])
    pair_i_all  = np.array([p['i'] for p in all_preds])
    pair_j_all  = np.array([p['j'] for p in all_preds])
    label_all   = np.array([meta[(p['i'],p['j'])]['label'] for p in all_preds])
    direct_all  = np.array([meta[(p['i'],p['j'])]['direct'] for p in all_preds], dtype=float)
    sa_all      = np.array([meta[(p['i'],p['j'])]['sareachable'] for p in all_preds], dtype=float)
    pathstr_all = np.array([meta[(p['i'],p['j'])]['path_strength'] for p in all_preds])
    dcorr_all   = np.array([meta[(p['i'],p['j'])]['delta_corr'] for p in all_preds])
    rawcorr_all = np.array([meta[(p['i'],p['j'])]['raw_corr'] for p in all_preds])
    samemod_all = np.array([meta[(p['i'],p['j'])]['same_module'] for p in all_preds], dtype=float)
    is_C_all    = (label_all == 'C').astype(float)
    is_S_all    = (label_all == 'S').astype(float)
    is_N_all    = (label_all == 'N').astype(float)

    def spearman(x, y, label=''):
        r, p = stats.spearmanr(x, y)
        return float(r), float(p)

    features = {
        'direct_structural': direct_all,
        'sareachable': sa_all,
        'path_strength': pathstr_all,
        'delta_corr (|ΔCorr|)': dcorr_all,
        'raw_corr': rawcorr_all,
        'same_module': samemod_all,
        'is_C': is_C_all,
        'is_S': is_S_all,
        'is_N': is_N_all,
        'S_score': s_score_all,
    }

    f6_results = {}
    print("  Spearman ρ between C-score and features:")
    for feat_name, feat_arr in features.items():
        r, p = spearman(feat_arr, c_score_all)
        f6_results[feat_name] = {'rho': round(r, 4), 'p': float(p), 'direction': 'positive' if r > 0 else 'negative'}
        print(f"    C-score ~ {feat_name}: ρ={r:.4f} p={p:.2e}")

    # Also check S-score correlates
    f6_s_results = {}
    print("  Spearman ρ between S-score and features:")
    for feat_name, feat_arr in features.items():
        r, p = spearman(feat_arr, s_score_all)
        f6_s_results[feat_name] = {'rho': round(r, 4), 'p': float(p)}
        print(f"    S-score ~ {feat_name}: ρ={r:.4f} p={p:.2e}")

    # Class-conditional C-score distributions
    f6_class_stats = {}
    for cls in ['S', 'C', 'M', 'N']:
        mask = label_all == cls
        scores = c_score_all[mask]
        f6_class_stats[cls] = {
            'n': int(mask.sum()),
            'mean': float(np.mean(scores)),
            'median': float(np.median(scores)),
            'std': float(np.std(scores)),
            'p10': float(np.percentile(scores, 10)),
            'p90': float(np.percentile(scores, 90)),
        }

    # Within-class, does C-score correlate with path_strength or |ΔCorr| within C pairs?
    c_mask = label_all == 'C'
    rho_c_pathstr, p_c_pathstr = spearman(pathstr_all[c_mask], c_score_all[c_mask])
    rho_c_dcorr,   p_c_dcorr   = spearman(dcorr_all[c_mask],   c_score_all[c_mask])
    rho_n_dcorr,   p_n_dcorr   = spearman(dcorr_all[~c_mask],  c_score_all[~c_mask])

    print(f"  Within C-class: C-score ~ path_strength: ρ={rho_c_pathstr:.4f} p={p_c_pathstr:.2e}")
    print(f"  Within C-class: C-score ~ |ΔCorr|: ρ={rho_c_dcorr:.4f} p={p_c_dcorr:.2e}")

    f6_full = {
        'c_score_correlates': f6_results,
        's_score_correlates': f6_s_results,
        'class_conditional_c_score': f6_class_stats,
        'within_C_c_score_path_strength': {'rho': rho_c_pathstr, 'p': p_c_pathstr},
        'within_C_c_score_dcorr': {'rho': rho_c_dcorr, 'p': p_c_dcorr},
    }

    with open(os.path.join(OUT, 'f6_signal_tracking_data.json'), 'w') as f:
        json.dump(f6_full, f, indent=2)

    # ===========================================================================
    # Additional: score distribution summary for writing
    # ===========================================================================

    # What IS the C-score measuring? Let's look at its raw correlates vs
    # the underlying quantities (PCor_cond, Delta_PCor, Current_norm)
    # We can proxy Delta_PCor by looking at what distinguishes top-C from bottom-C

    # Top-100 C-score pair characteristics
    top100_labels = all_labels[:100]
    top100_direct = all_direct[:100]
    top100_dcorr  = all_dcorr[:100]
    top100_rawcorr = all_rawcorr[:100]
    top100_same   = all_same_mod[:100]

    # Bottom-100 (lowest C-scores)
    bot100_labels  = all_labels[-100:]
    bot100_direct  = all_direct[-100:]
    bot100_dcorr   = all_dcorr[-100:]
    bot100_rawcorr = all_rawcorr[-100:]

    print("\n  Top-100 by C-score vs Bottom-100:")
    print(f"    Top-100: mean_dcorr={np.mean(top100_dcorr):.4f} mean_rawcorr={np.mean(top100_rawcorr):.4f} "
          f"pct_N={100*(top100_labels=='N').mean():.1f}% pct_S={100*(top100_labels=='S').mean():.1f}%")
    print(f"    Bot-100: mean_dcorr={np.mean(bot100_dcorr):.4f} mean_rawcorr={np.mean(bot100_rawcorr):.4f} "
          f"pct_N={100*(bot100_labels=='N').mean():.1f}% pct_S={100*(bot100_labels=='S').mean():.1f}%")

    contrast = {
        'top100': {
            'n_N': int((top100_labels=='N').sum()),
            'n_S': int((top100_labels=='S').sum()),
            'n_C': int((top100_labels=='C').sum()),
            'mean_dcorr': float(np.mean(top100_dcorr)),
            'mean_rawcorr': float(np.mean(top100_rawcorr)),
            'pct_same_module': float(np.mean(top100_same)),
            'pct_direct': float(np.mean(top100_direct)),
        },
        'bot100': {
            'n_N': int((bot100_labels=='N').sum()),
            'n_S': int((bot100_labels=='S').sum()),
            'n_C': int((bot100_labels=='C').sum()),
            'mean_dcorr': float(np.mean(bot100_dcorr)),
            'mean_rawcorr': float(np.mean(bot100_rawcorr)),
            'pct_same_module': float(np.mean(all_same_mod[-100:])),
            'pct_direct': float(np.mean(all_direct[-100:])),
        }
    }
    f6_full['top_vs_bottom_100'] = contrast
    with open(os.path.join(OUT, 'f6_signal_tracking_data.json'), 'w') as f:
        json.dump(f6_full, f, indent=2)

    print("\nAll analysis complete. Data files written to results/phase8f/")
    return {
        'f1': f1_rows,
        'f2': f2_results,
        'f3': f3_results,
        'f4': f4_results,
        'f5': f5_results,
        'f6': f6_full,
        'meta_arrays': {
            'c_scores': c_scores,
            'is_S': is_S,
            'is_C': is_C,
            'is_N': is_N,
            'all_labels': all_labels,
            'all_direct': all_direct,
            'all_sareable': all_sareable,
            'all_dcorr': all_dcorr,
            'all_rawcorr': all_rawcorr,
            'all_same_mod': all_same_mod,
            'all_mod_i': all_mod_i,
            'all_mod_j': all_mod_j,
        }
    }


if __name__ == '__main__':
    main()
