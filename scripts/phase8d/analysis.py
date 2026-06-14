"""
Phase 8D: Structure-of-interest evaluation for the recurrent benchmark.

Uses frozen framework_output.json and frozen labels. Does NOT rerun the
framework or change any ground truth. Re-evaluates with rank-based metrics
and biologically meaningful subsets.

Produces data tables for D1–D5 deliverables.
"""

import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.phase7b import config as cfg

ROOT    = cfg.PROJECT_ROOT
OUT_DIR = os.path.join(ROOT, 'results', 'phase8d')
os.makedirs(OUT_DIR, exist_ok=True)

N_PERM  = 10_000
RNG     = np.random.default_rng(42)


# ---------------------------------------------------------------------------
# Load frozen artifacts
# ---------------------------------------------------------------------------

def load_all():
    """Load framework output, labels, A_sparse, and oracle_z data."""
    print('Loading frozen artifacts...')

    # Framework output
    with open(os.path.join(ROOT, 'framework_output.json')) as f:
        fw = json.load(f)

    # Build score arrays (9900 pairs, aligned)
    pairs    = []
    c_prob   = []
    lr_prob  = []
    s_prob   = []
    m_prob   = []
    n_prob   = []
    for p in fw['predictions']:
        pairs.append((p['i'], p['j']))
        cp = p['class_prob']
        s_prob.append(cp['S'])
        c_prob.append(cp['C'])
        m_prob.append(cp['M'])
        n_prob.append(cp['N'])
        lr_prob.append(cp['C'] + cp['M'])

    pairs   = pairs
    c_prob  = np.array(c_prob)
    lr_prob = np.array(lr_prob)
    s_prob  = np.array(s_prob)
    m_prob  = np.array(m_prob)
    n_prob  = np.array(n_prob)
    print(f'  Framework: {len(pairs)} pairs')

    # Labels
    with open(os.path.join(ROOT, 'ground_truth', 'labels.json')) as f:
        lbl_data = json.load(f)['labels']

    lbl_map = {(d['i'], d['j']): d for d in lbl_data}

    # Align labels with pair order
    true_lbl   = [lbl_map[(i, j)]['label'] for i, j in pairs]
    direct_arr = np.array([lbl_map[(i, j)]['direct'] for i, j in pairs], dtype=int)
    sareach_arr = np.array([lbl_map[(i, j)]['sareachable'] for i, j in pairs], dtype=int)
    witness_h2 = [lbl_map[(i, j)]['witness_h2'] for i, j in pairs]
    true_arr   = np.array(true_lbl)

    # A_sparse for path strength computation
    A = np.load(os.path.join(ROOT, 'ground_truth', 'A_sparse.npy'))

    # Compute H2 path strength for every pair (0 for non-C/M pairs)
    path_strength = np.zeros(len(pairs), dtype=np.float64)
    for k, ((i, j), wh) in enumerate(zip(pairs, witness_h2)):
        if wh is not None:
            path_strength[k] = abs(A[wh, i]) * abs(A[j, wh])

    print(f'  Labels aligned. C={( true_arr=="C").sum()}, M={(true_arr=="M").sum()}, '
          f'S={(true_arr=="S").sum()}, N={(true_arr=="N").sum()}')

    # Oracle_z data (for state analysis + baseline recomputation)
    data_dir = os.path.join(ROOT, 'results', 'phase7c', 'canonical', 'data')
    runs = []
    for r in range(5):
        d = np.load(os.path.join(data_dir, f'oracle_z_run{r}.npz'))
        runs.append({'y': d['y'].astype(np.float64), 'z_oracle': d['z_oracle'].astype(np.float64)})
    print(f'  Oracle_z runs: {len(runs)}, shape: {runs[0]["y"].shape}')

    return {
        'pairs':          pairs,
        'c_prob':         c_prob,
        'lr_prob':        lr_prob,
        's_prob':         s_prob,
        'm_prob':         m_prob,
        'n_prob':         n_prob,
        'true_arr':       true_arr,
        'direct_arr':     direct_arr,
        'sareach_arr':    sareach_arr,
        'path_strength':  path_strength,
        'runs':           runs,
    }


# ---------------------------------------------------------------------------
# Enrichment statistics
# ---------------------------------------------------------------------------

def topk_enrichment(scores: np.ndarray, is_target: np.ndarray, k: int,
                    n_perm: int = N_PERM) -> dict:
    """
    Compute top-k enrichment statistics for a binary target.

    Parameters
    ----------
    scores : (N,) float — higher = ranked higher
    is_target : (N,) bool — 1 for target class members
    k : int — number of top items
    n_perm : int — permutation samples for p-value

    Returns
    -------
    dict with observed, expected, OR, p_value, precision, recall, f1
    """
    N       = len(scores)
    n_pos   = is_target.sum()
    top_idx = np.argsort(scores)[::-1][:k]

    observed = is_target[top_idx].sum()
    expected = k * n_pos / N
    precision = observed / k
    recall    = observed / n_pos if n_pos > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)

    # Odds ratio: (obs/k−obs) / (n_pos/N−n_pos)
    a = observed
    b = k - observed
    c = n_pos - observed
    d = N - k - c
    if b > 0 and c > 0:
        odds_ratio = (a * d) / (b * c)
    elif b == 0:
        odds_ratio = float('inf')
    else:
        odds_ratio = 0.0

    # Permutation p-value: P(perm_count >= observed)
    perm_counts = np.array([
        is_target[RNG.choice(N, k, replace=False)].sum()
        for _ in range(n_perm)
    ])
    p_value = float((perm_counts >= observed).mean())

    return {
        'k':          k,
        'observed':   int(observed),
        'expected':   float(expected),
        'odds_ratio': odds_ratio,
        'p_value':    p_value,
        'precision':  float(precision),
        'recall':     float(recall),
        'f1':         float(f1),
    }


def auroc_safe(y_true, y_score):
    if y_true.sum() == 0 or y_true.sum() == len(y_true):
        return float('nan')
    return float(roc_auc_score(y_true, y_score))


def auprc_safe(y_true, y_score):
    if y_true.sum() == 0:
        return float('nan')
    return float(average_precision_score(y_true, y_score))


# ---------------------------------------------------------------------------
# State sensitivity computation (from oracle_z data)
# ---------------------------------------------------------------------------

def compute_state_sensitivity(runs: list[dict]) -> np.ndarray:
    """
    For each directed pair (i,j), compute state sensitivity =
    |corr(y_i, y_j | z > median) - corr(y_i, y_j | z ≤ median)|
    averaged across runs.

    Returns (N_OBS, N_OBS) matrix (diagonal = 0).
    """
    N_OBS = 100
    sensitivity = np.zeros((N_OBS, N_OBS), dtype=np.float64)

    for run in runs:
        y = run['y']       # (T, 100)
        z = run['z_oracle']  # (T,)

        z_thresh  = np.median(z)
        high_mask = z > z_thresh
        low_mask  = ~high_mask

        y_high = y[high_mask]  # (T_high, 100)
        y_low  = y[low_mask]   # (T_low, 100)

        # Correlation matrices
        c_high = np.corrcoef(y_high.T)   # (100, 100)
        c_low  = np.corrcoef(y_low.T)    # (100, 100)
        sensitivity += np.abs(c_high - c_low)

    sensitivity /= len(runs)
    np.fill_diagonal(sensitivity, 0.0)
    return sensitivity


# ---------------------------------------------------------------------------
# Baseline score computation (from oracle_z data)
# ---------------------------------------------------------------------------

def compute_b3_scores(runs: list[dict]) -> np.ndarray:
    """B3: mean |Pearson corr(y_i, y_j)| across runs. Returns (N_OBS, N_OBS)."""
    N_OBS = 100
    corr_sum = np.zeros((N_OBS, N_OBS), dtype=np.float64)
    for run in runs:
        corr_sum += np.abs(np.corrcoef(run['y'].T))
    corr = corr_sum / len(runs)
    np.fill_diagonal(corr, 0.0)
    return corr


def compute_b5_scores(runs: list[dict]) -> np.ndarray:
    """B5: mean |corr(y|z_high) - corr(y|z_low)| across runs. Returns (N_OBS, N_OBS)."""
    return compute_state_sensitivity(runs)


def compute_b6_scores() -> np.ndarray:
    """B6: within-module indicator. N_OBS=100, 4 modules of 25 each. Returns (N_OBS, N_OBS)."""
    N_OBS = 100
    module = np.arange(N_OBS) // 25
    b6 = (module[:, None] == module[None, :]).astype(float)
    np.fill_diagonal(b6, 0.0)
    return b6


def matrix_to_pair_scores(mat: np.ndarray, pairs: list) -> np.ndarray:
    """Extract (N_pairs,) score vector from (100, 100) matrix."""
    return np.array([mat[i, j] for i, j in pairs])


# ---------------------------------------------------------------------------
# D1: Top-k enrichment for C class
# ---------------------------------------------------------------------------

def run_d1(data: dict) -> dict:
    """Top-k enrichment of the C class using framework's C-score."""
    print('\n--- D1: Top-k enrichment for C class ---')
    is_C  = data['true_arr'] == 'C'
    score = data['c_prob']   # framework C-score

    print(f'  n(C)={is_C.sum()}, n_total={len(is_C)}, base_rate={is_C.mean():.4f}')
    print(f'  C-AUROC = {auroc_safe(is_C.astype(int), score):.4f}')

    results = {}
    for k in [10, 20, 50, 100, 200, 500]:
        r = topk_enrichment(score, is_C, k)
        results[k] = r
        print(f'  k={k:4d}: obs={r["observed"]:3d}, exp={r["expected"]:.1f}, '
              f'OR={r["odds_ratio"]:.3f}, p={r["p_value"]:.4f}, '
              f'prec={r["precision"]:.4f}, rec={r["recall"]:.4f}')

    # Also compute enrichment with INVERTED score (for reference)
    # Since C-AUROC < 0.5, maybe the BOTTOM k by c_prob is enriched for C
    print('  [inverted score: bottom-k by c_prob, i.e. top-k by -c_prob]')
    results_inv = {}
    for k in [10, 20, 50, 100]:
        r = topk_enrichment(-score, is_C, k)
        results_inv[k] = r
        print(f'  k={k:4d}: obs={r["observed"]:3d}, exp={r["expected"]:.1f}, '
              f'OR={r["odds_ratio"]:.3f}, p={r["p_value"]:.4f}')

    return {'top_k': results, 'inverted_top_k': results_inv}


# ---------------------------------------------------------------------------
# D2: Off-connectome / structure-of-interest subset
# ---------------------------------------------------------------------------

def run_d2(data: dict) -> dict:
    """Enrichment analysis on biologically relevant subsets."""
    print('\n--- D2: Structure-of-interest subset ---')
    true_arr = data['true_arr']
    c_prob   = data['c_prob']
    lr_prob  = data['lr_prob']
    s_prob   = data['s_prob']
    path_str = data['path_strength']

    # Define subsets
    is_C = true_arr == 'C'
    is_M = true_arr == 'M'
    is_S = true_arr == 'S'
    is_N = true_arr == 'N'
    is_LR = is_C | is_M

    # Strong C: C pairs with path_strength > median of C path strengths
    c_strengths = path_str[is_C]
    strength_median = np.median(c_strengths)
    is_strong_C = is_C & (path_str > strength_median)
    is_weak_C   = is_C & (path_str <= strength_median)

    print(f'  C median path strength: {strength_median:.4f}')
    print(f'  n(strong_C)={is_strong_C.sum()}, n(weak_C)={is_weak_C.sum()}')

    results = {}

    # Per-class AUROCs (C-score ranking)
    for name, mask in [('C_all', is_C), ('M', is_M), ('S', is_S), ('LR', is_LR),
                       ('strong_C', is_strong_C), ('weak_C', is_weak_C)]:
        if mask.sum() == 0:
            continue
        rest = ~mask
        # Score: C-prob (biologically: should rank C/M above S and N)
        score = c_prob
        au = auroc_safe(mask.astype(int), score)
        pr = auprc_safe(mask.astype(int), score)
        print(f'  {name:12s}: n={mask.sum():4d}, C-AUROC={au:.4f}, C-AUPRC={pr:.6f}')
        results[name] = {'auroc': au, 'auprc': pr}

    # Top-k enrichment for each subset (using C-prob as ranking)
    print('\n  Top-k enrichment by C-prob score:')
    topk_results = {}
    for name, mask in [('C_all', is_C), ('strong_C', is_strong_C), ('weak_C', is_weak_C),
                       ('M', is_M), ('LR', is_LR), ('S', is_S)]:
        if mask.sum() == 0:
            continue
        row = {}
        for k in [50, 100, 200]:
            r = topk_enrichment(c_prob, mask, k, n_perm=5000)
            row[k] = r
        topk_results[name] = row
        print(f'  {name:12s}: k=50 OR={row[50]["odds_ratio"]:.3f} p={row[50]["p_value"]:.4f} | '
              f'k=100 OR={row[100]["odds_ratio"]:.3f} | k=200 OR={row[200]["odds_ratio"]:.3f}')

    # Also test LR-score ranking for LR detection
    print('\n  Top-k enrichment by LR-prob score:')
    for name, mask in [('C_all', is_C), ('strong_C', is_strong_C), ('weak_C', is_weak_C),
                       ('LR', is_LR)]:
        if mask.sum() == 0:
            continue
        row = {}
        for k in [50, 100, 200]:
            r = topk_enrichment(lr_prob, mask, k, n_perm=5000)
            row[k] = r
        print(f'  {name:12s} [LR-score]: k=50 OR={row[50]["odds_ratio"]:.3f} p={row[50]["p_value"]:.4f} | '
              f'k=100 OR={row[100]["odds_ratio"]:.3f} | k=200 OR={row[200]["odds_ratio"]:.3f}')

    return {'auroc_per_subset': results, 'topk_c_score': topk_results,
            'path_strength_median': float(strength_median)}


# ---------------------------------------------------------------------------
# D3: State-sensitive analysis
# ---------------------------------------------------------------------------

def run_d3(data: dict) -> dict:
    """Test whether framework preferentially recovers state-sensitive edges."""
    print('\n--- D3: State-sensitive analysis ---')
    pairs    = data['pairs']
    true_arr = data['true_arr']
    c_prob   = data['c_prob']
    lr_prob  = data['lr_prob']
    s_prob   = data['s_prob']
    runs     = data['runs']

    print('  Computing state sensitivity (|ΔCorr| across z splits)...')
    sens_mat = compute_state_sensitivity(runs)
    sens_arr = matrix_to_pair_scores(sens_mat, pairs)   # (9900,)

    # Define state-sensitive / state-invariant pairs
    p25, p75 = np.percentile(sens_arr, [25, 75])
    is_sensitive  = sens_arr >= p75
    is_invariant  = sens_arr <= p25
    is_C = true_arr == 'C'
    is_M = true_arr == 'M'
    is_S = true_arr == 'S'
    is_LR = is_C | is_M

    print(f'  State sensitivity: p25={p25:.4f}, p75={p75:.4f}')
    print(f'  n(sensitive)={is_sensitive.sum()}, n(invariant)={is_invariant.sum()}')

    # Joint distribution: what fraction of C pairs are state-sensitive?
    print(f'  C ∩ sensitive: {(is_C & is_sensitive).sum()} / {is_C.sum()} = '
          f'{(is_C & is_sensitive).mean() / is_C.mean():.3f}× enrichment')
    print(f'  C ∩ invariant: {(is_C & is_invariant).sum()} / {is_C.sum()} = '
          f'{(is_C & is_invariant).mean() / is_C.mean():.3f}× enrichment')
    print(f'  S ∩ sensitive: {(is_S & is_sensitive).sum()} / {is_S.sum()} = '
          f'{(is_S & is_sensitive).mean() / is_S.mean():.3f}× enrichment')

    # AUROC: does framework's C-score rank state-sensitive pairs?
    auroc_sens  = auroc_safe(is_sensitive.astype(int), c_prob)
    auroc_c_in_sens = auroc_safe(
        (is_C & is_sensitive).astype(int), c_prob
    )
    auroc_c_in_inv = auroc_safe(
        (is_C & is_invariant).astype(int), c_prob
    )
    print(f'  C-AUROC for state-sensitive pairs:  {auroc_c_in_sens:.4f}')
    print(f'  C-AUROC for state-invariant pairs:  {auroc_c_in_inv:.4f}')

    # Top-k enrichment: does framework top-k preferentially recover state-sensitive C?
    print('\n  Top-k enrichment by C-prob score:')
    topk_results = {}
    for name, mask in [
        ('sensitive_C',   is_C & is_sensitive),
        ('invariant_C',   is_C & is_invariant),
        ('sensitive_all', is_sensitive),
        ('S',             is_S),
    ]:
        if mask.sum() == 0:
            continue
        row = {}
        for k in [50, 100, 200]:
            r = topk_enrichment(c_prob, mask, k, n_perm=5000)
            row[k] = r
        topk_results[name] = row
        print(f'  {name:18s}: k=50 OR={row[50]["odds_ratio"]:.3f} p={row[50]["p_value"]:.4f} | '
              f'k=100 OR={row[100]["odds_ratio"]:.3f} | k=200 OR={row[200]["odds_ratio"]:.3f}')

    # Use STATE SENSITIVITY as a score: does it preferentially rank C above N?
    print('\n  Using state_sensitivity score directly (B5 proxy):')
    au_c_from_sens = auroc_safe(is_C.astype(int), sens_arr)
    au_lr_from_sens = auroc_safe(is_LR.astype(int), lr_prob)
    print(f'  C-AUROC from |ΔCorr|: {au_c_from_sens:.4f}')
    print(f'  LR-AUROC from LR-score: {au_lr_from_sens:.4f}')

    return {
        'p25_sensitivity': float(p25),
        'p75_sensitivity': float(p75),
        'c_in_sensitive_count': int((is_C & is_sensitive).sum()),
        'c_in_invariant_count': int((is_C & is_invariant).sum()),
        'auroc_c_in_sensitive': auroc_c_in_sens,
        'auroc_c_in_invariant': auroc_c_in_inv,
        'topk': topk_results,
        'auroc_c_from_state_sensitivity': float(au_c_from_sens),
    }


# ---------------------------------------------------------------------------
# D4: Baseline comparison with rank-based metrics
# ---------------------------------------------------------------------------

def run_d4(data: dict) -> dict:
    """Top-k enrichment for all baselines vs framework."""
    print('\n--- D4: Baseline rank comparison ---')
    pairs    = data['pairs']
    true_arr = data['true_arr']
    runs     = data['runs']

    is_C  = true_arr == 'C'
    is_LR = (true_arr == 'C') | (true_arr == 'M')
    is_S  = true_arr == 'S'

    # Compute baseline scores
    print('  Computing B3 (correlation)...')
    b3_mat = compute_b3_scores(runs)
    b3_arr = matrix_to_pair_scores(b3_mat, pairs)

    print('  Computing B5 (state-ΔCorr)...')
    b5_mat = compute_b5_scores(runs)
    b5_arr = matrix_to_pair_scores(b5_mat, pairs)

    print('  Computing B6 (module oracle)...')
    b6_mat = compute_b6_scores()
    b6_arr = matrix_to_pair_scores(b6_mat, pairs)

    # Framework scores
    fw_c_arr  = data['c_prob']
    fw_lr_arr = data['lr_prob']
    fw_s_arr  = data['s_prob']

    results = {}
    K_VALUES = [10, 20, 50, 100, 200]

    for target_name, is_target in [('C', is_C), ('LR', is_LR), ('S', is_S)]:
        print(f'\n  Target={target_name} (n={is_target.sum()}):')
        row = {}

        # AUROC for each baseline
        for bname, score in [
            ('Framework-C', fw_c_arr),
            ('Framework-LR', fw_lr_arr),
            ('B3-corr', b3_arr),
            ('B5-dCorr', b5_arr),
            ('B6-module', b6_arr),
        ]:
            au = auroc_safe(is_target.astype(int), score)
            print(f'    AUROC({bname}): {au:.4f}')

        # Top-k enrichment
        print(f'    Top-k enrichment:')
        topk_row = {}
        for bname, score in [
            ('Framework-C', fw_c_arr),
            ('B3-corr', b3_arr),
            ('B5-dCorr', b5_arr),
            ('B6-module', b6_arr),
        ]:
            tk = {}
            for k in K_VALUES:
                r = topk_enrichment(score, is_target, k, n_perm=3000)
                tk[k] = r
            topk_row[bname] = tk
            k50 = tk[50]
            print(f'      {bname:16s}: k=50 OR={k50["odds_ratio"]:.3f} '
                  f'p={k50["p_value"]:.4f} prec={k50["precision"]:.4f}')
        row['topk'] = topk_row
        results[target_name] = row

    return results


# ---------------------------------------------------------------------------
# D5: Metric calibration
# ---------------------------------------------------------------------------

def run_d5(data: dict) -> dict:
    """Compare AUROC vs rank-based metrics for calibration."""
    print('\n--- D5: Metric calibration ---')
    true_arr = data['true_arr']
    c_prob   = data['c_prob']
    lr_prob  = data['lr_prob']
    s_prob   = data['s_prob']

    is_C  = true_arr == 'C'
    is_M  = true_arr == 'M'
    is_S  = true_arr == 'S'
    is_LR = is_C | is_M
    is_N  = true_arr == 'N'

    n_total = len(true_arr)
    results = {}

    print(f'  n_total={n_total}, base rates: C={is_C.mean():.4f}, '
          f'M={is_M.mean():.4f}, S={is_S.mean():.4f}, N={is_N.mean():.4f}')

    for target_name, is_target, score in [
        ('C (c_score)',  is_C,  c_prob),
        ('LR (lr_score)', is_LR, lr_prob),
        ('S (s_score)',  is_S,  s_prob),
    ]:
        n_pos    = is_target.sum()
        base_rate = n_pos / n_total
        auroc    = auroc_safe(is_target.astype(int), score)
        auprc    = auprc_safe(is_target.astype(int), score)

        # Top-k precision and enrichment at multiple k
        topk_data = {}
        for k in [10, 20, 50, 100, 200, 500]:
            r = topk_enrichment(score, is_target, k, n_perm=2000)
            topk_data[k] = r

        print(f'\n  {target_name}: n_pos={n_pos}, base_rate={base_rate:.4f}')
        print(f'    AUROC={auroc:.4f}')
        print(f'    AUPRC={auprc:.4f}  (vs base_rate {base_rate:.4f})')
        print(f'    Top-k precision:  ', end='')
        for k in [10, 20, 50, 100]:
            print(f'k={k}: {topk_data[k]["precision"]:.4f}  ', end='')
        print()
        print(f'    Top-k OR:         ', end='')
        for k in [10, 20, 50, 100]:
            print(f'k={k}: {topk_data[k]["odds_ratio"]:.3f}  ', end='')
        print()

        results[target_name] = {
            'auroc':      auroc,
            'auprc':      auprc,
            'base_rate':  float(base_rate),
            'topk':       topk_data,
        }

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('='*60)
    print('Phase 8D: Structure-of-interest evaluation')
    print('='*60)

    data = load_all()

    d1 = run_d1(data)
    d2 = run_d2(data)
    d3 = run_d3(data)
    d4 = run_d4(data)
    d5 = run_d5(data)

    # Save raw results
    out = {'d1': d1, 'd2': d2, 'd3': d3, 'd5': d5}
    # d4 has non-serializable inf values — replace
    def clean(obj):
        if isinstance(obj, float) and (np.isinf(obj) or np.isnan(obj)):
            return str(obj)
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj
    out['d4'] = clean(d4)
    out = clean(out)

    with open(os.path.join(OUT_DIR, 'analysis_results.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nResults saved to {OUT_DIR}/analysis_results.json')

    return d1, d2, d3, d4, d5


if __name__ == '__main__':
    main()
