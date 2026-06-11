"""Figure 2 — One Wiring, Two Functions
Panels A/B: |ΔQ| histograms (CePNEM, GCaMP). Panel C: ΔQ scatter.
Data from stage2 saved arrays.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT  = Path(__file__).resolve().parents[1]

# ── Color convention ─────────────────────────────────────────────────────────
C_GRAY   = '#CCCCCC'
C_PDF    = '#D62728'
C_PEP    = '#999999'
C_RANDI  = '#2CA02C'
C_BOTH   = '#8C564B'
C_NONE   = '#CCCCCC'
DWELLING = '#4C6EF5'
ROAMING  = '#FF6B35'

# ── Load data ─────────────────────────────────────────────────────────────────
STG2 = ROOT / 'results/phase2/stage2'
DQ_c = np.load(STG2 / 'DQ_cepnem.npy')    # (61,61)
DQ_g = np.load(STG2 / 'DQ_gcamp.npy')

ranked_c4 = np.load(STG2 / 'ranked_class4_cepnem.npy')   # (1321,) indices
ranked_c4_g = np.load(STG2 / 'ranked_class4_gcamp.npy')

N = 61
ii_all, jj_all = np.triu_indices(N, k=1)

ii_c4 = ii_all[ranked_c4]
jj_c4 = jj_all[ranked_c4]

dq_c_vals = DQ_c[ii_c4, jj_c4]   # signed, 1321 values
dq_g_vals = DQ_g[ii_c4, jj_c4]

# Authoritative nonzero counts from stage2_results.json (avoid floating-point threshold artefacts)
with open(STG2 / 'stage2_results.json') as _f:
    _s2 = json.load(_f)
NONZERO_C_AUTH = _s2['coordinates']['cepnem']['n_class4_nonzero_dq']   # 243
NONZERO_G_AUTH = _s2['coordinates']['gcamp']['n_class4_nonzero_dq']    # 585

# ── Load Bentley PDF annotation (same method as extraction script) ────────────
import csv
with open(ROOT / 'results/phase2/stage0/copresence_report.json') as f:
    cop = json.load(f)
NEURONS = cop['neurons']
n2i = {n: i for i, n in enumerate(NEURONS)}
neurons_set = set(NEURONS)

class4_set = set(zip(map(int, ii_c4), map(int, jj_c4)))

pdf_path = ROOT / 'data/randi/wormneuroatlas/wormneuroatlas/data/esconnectome_neuropeptides_Bentley_2016.csv'
bentley_pdf_c4 = set()
with open(pdf_path) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 3: continue
        src, tgt, tx = row[0].strip(), row[1].strip(), row[2].strip()
        if 'pdf' not in tx.lower(): continue
        if src not in neurons_set or tgt not in neurons_set or src == tgt: continue
        a, b = n2i[src], n2i[tgt]
        key = (min(a,b), max(a,b))
        if key in class4_set:
            bentley_pdf_c4.add(key)

pdf_flag = np.array([(int(ii_c4[k]), int(jj_c4[k])) in bentley_pdf_c4
                     for k in range(len(ii_c4))], dtype=bool)

# Top-labeled pairs from spec
TOP_PAIRS_C = [
    ('IL1DR-URYVR', -0.2541), ('AVER-I1L', -0.2160),
    ('ADEL-URYVR', -0.1222), ('I1L-IL2DR', +0.0903),
]
TOP_PAIRS_G = [
    ('OLLL-SMDVL', -0.2897), ('NSMR-RMDVL', -0.2336),
    ('I1L-M4', +0.2142),
]
# Pair indices for labeling (CePNEM top ranked)
def pair_idx(name):
    a, b = name.split('–')
    if a in n2i and b in n2i:
        i, j = n2i[a], n2i[b]
        k = (min(i,j), max(i,j))
        for pos in range(len(ii_c4)):
            if (int(ii_c4[pos]), int(jj_c4[pos])) == k:
                return pos
    return None

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(9, 3.8))
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)
ax_a = fig.add_subplot(gs[0])
ax_b = fig.add_subplot(gs[1])
ax_c = fig.add_subplot(gs[2])

# ── Panel A: |ΔQ| CePNEM histogram ──────────────────────────────────────────
abs_c = np.abs(dq_c_vals)
bins = np.linspace(0, 0.28, 40)
ax_a.hist(abs_c[~pdf_flag], bins=bins, color='#AAAAAA', alpha=0.85,
          label='Other Class 4', edgecolor='none', linewidth=0)
ax_a.hist(abs_c[pdf_flag],  bins=bins, color=C_PDF, alpha=0.9,
          label='Bentley PDF', edgecolor='none', linewidth=0)
ax_a.set_yscale('log')
ax_a.set_xlabel('|ΔQ| CePNEM', fontsize=9)
ax_a.set_ylabel('Pair count (log)', fontsize=9)
ax_a.set_title('A  CePNEM', fontsize=9, loc='left', fontweight='bold')
nonzero_c = NONZERO_C_AUTH
ax_a.text(0.97, 0.55, f'n={len(abs_c):,}\n{nonzero_c} non-zero\n({100*nonzero_c/len(abs_c):.0f}%)',
          transform=ax_a.transAxes, va='top', ha='right', fontsize=7.5, color='#555555')
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)
ax_a.legend(fontsize=7, frameon=False, loc='upper right')

# ── Panel B: |ΔQ| GCaMP histogram ───────────────────────────────────────────
abs_g = np.abs(dq_g_vals)
ax_b.hist(abs_g[~pdf_flag], bins=bins, color='#AAAAAA', alpha=0.85,
          edgecolor='none', linewidth=0)
ax_b.hist(abs_g[pdf_flag],  bins=bins, color=C_PDF, alpha=0.9,
          edgecolor='none', linewidth=0)
ax_b.set_yscale('log')
ax_b.set_xlabel('|ΔQ| GCaMP', fontsize=9)
ax_b.set_title('B  GCaMP', fontsize=9, loc='left', fontweight='bold')
nonzero_g = NONZERO_G_AUTH
ax_b.text(0.97, 0.97, f'n={len(abs_g):,}\n{nonzero_g} non-zero\n({100*nonzero_g/len(abs_g):.0f}%)',
          transform=ax_b.transAxes, va='top', ha='right', fontsize=7.5, color='#555555')
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)

# ── Panel C: Scatter ΔQ_cepnem vs ΔQ_gcamp ──────────────────────────────────
# Background: all non-PDF pairs
ax_c.scatter(dq_c_vals[~pdf_flag], dq_g_vals[~pdf_flag],
             s=2, color='#CCCCCC', alpha=0.5, linewidths=0, rasterized=True)
# PDF pairs
ax_c.scatter(dq_c_vals[pdf_flag], dq_g_vals[pdf_flag],
             s=18, color=C_PDF, alpha=0.85, linewidths=0.3,
             edgecolors='white', zorder=5, label='Bentley PDF (n=61)')

# Diagonal reference
lim = 0.32
ax_c.plot([-lim, lim], [-lim, lim], color='#DDDDDD', lw=0.7, ls='--')
ax_c.axhline(0, color='#EEEEEE', lw=0.5)
ax_c.axvline(0, color='#EEEEEE', lw=0.5)

# Label top CePNEM pairs
top_labels = [
    ('ADEL–URYVR', 0),    # rank 5 CePNEM
    ('ADEL–URYDL', 0),    # rank 9
    ('RMEL–URYDL', 0),    # rank 16
    ('OLLL–SMDVL', 0),    # rank 1 GCaMP
]
# Find these pairs in ranked list and label
label_pairs = {
    ('ADEL', 'URYVR'): 'ADEL–URYVR',
    ('ADEL', 'URYDL'): 'ADEL–URYDL',
    ('RMEL', 'URYDL'): 'RMEL–URYDL',
    ('OLLL', 'SMDVL'): 'OLLL–SMDVL',
}
for pos in range(len(ii_c4)):
    na, nb = NEURONS[ii_c4[pos]], NEURONS[jj_c4[pos]]
    label = label_pairs.get((na, nb)) or label_pairs.get((nb, na))
    if label:
        xv, yv = dq_c_vals[pos], dq_g_vals[pos]
        off_x = 0.015 if xv > 0 else -0.015
        ha = 'left' if xv > 0 else 'right'
        ax_c.annotate(label, (xv, yv), (xv + off_x, yv + 0.01),
                      fontsize=6.5, color='#333333',
                      arrowprops=dict(arrowstyle='-', color='#AAAAAA', lw=0.5))

ax_c.set_xlabel('ΔQ CePNEM (signed)', fontsize=9)
ax_c.set_ylabel('ΔQ GCaMP (signed)', fontsize=9)
ax_c.set_xlim(-lim, lim)
ax_c.set_ylim(-lim, lim)
ax_c.set_title('C  CePNEM vs GCaMP ΔQ', fontsize=9, loc='left', fontweight='bold')
ax_c.legend(fontsize=7, frameon=False, loc='lower right')
ax_c.spines['top'].set_visible(False)
ax_c.spines['right'].set_visible(False)
ax_c.tick_params(labelsize=8)

# ── Caption note ─────────────────────────────────────────────────────────────
fig.text(0.01, 0.0,
         'ΔQ = Q_roam − Q_dwell. Class 4: off-connectome pairs, both neurons in Creamer 56-subspace (n=1,321). '
         'Red: Bentley PDF annotated pairs (n=61). Grey: all other Class 4 pairs.',
         fontsize=6.5, color='#777777', transform=fig.transFigure)

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig(OUT / 'fig2_one_wiring_two_functions.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig2_one_wiring_two_functions.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 2 saved.')
