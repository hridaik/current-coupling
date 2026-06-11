"""Figure 3 — Annotation Density
All values hard-coded from figure_specification_package.md / stage data.
No new analysis.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

# ── Color convention ─────────────────────────────────────────────────────────
C = {
    'total':      '#CCCCCC',
    'pep':        '#666666',
    'randi':      '#2CA02C',
    'pdf':        '#D62728',
    'serotonin':  '#9467BD',
    'combined':   '#8C564B',
    'cengen':     '#BCBD22',
}

# ── Data (from stage2_results.json, stage4_report.md, stage4a_results.json) ─
categories = [
    ('All Class 4 pairs',          1321, '#AAAAAA',   None),
    ('Neuropeptide\n(Ripoll-Sánchez)',  972, C['pep'],     '73.6%'),
    ('CeNGEN combined\n(exploratory)', 409, C['cengen'],  '31.0%'),
    ('Randi unc-31',               108, C['randi'],   '8.2%'),
    ('Bentley combined\n(PDF + serotonin)', 94, C['combined'], '7.1%'),
    ('Bentley PDF',                 61, C['pdf'],      '4.6%'),
    ('Bentley serotonin',           33, C['serotonin'],'2.5%'),
]

labels = [c[0] for c in categories]
counts = [c[1] for c in categories]
colors = [c[2] for c in categories]
pcts   = [c[3] for c in categories]

# ── Figure ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6.5, 3.6))

y = np.arange(len(categories))
bars = ax.barh(y, counts, height=0.62, color=colors, edgecolor='white', linewidth=0.5)

# Count labels inside/outside bars
for i, (bar, cnt, pct) in enumerate(zip(bars, counts, pcts)):
    x = bar.get_width()
    if x > 200:
        ax.text(x - 20, bar.get_y() + bar.get_height()/2,
                f'{cnt:,}', va='center', ha='right', fontsize=8,
                color='white', fontweight='bold')
    else:
        ax.text(x + 15, bar.get_y() + bar.get_height()/2,
                f'{cnt:,}', va='center', ha='left', fontsize=8, color='#333333')
    if pct:
        ax.text(1321 + 18, bar.get_y() + bar.get_height()/2,
                pct, va='center', ha='left', fontsize=7.5, color='#555555')

# Reference line at 1321
ax.axvline(1321, color='#999999', lw=0.8, ls='--')

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8.5)
ax.set_xlabel('Number of Class 4 pairs', fontsize=9)
ax.set_xlim(0, 1600)
ax.tick_params(axis='x', labelsize=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_title('Connectome annotation landscape — 61-neuron subgraph', fontsize=10, pad=8)

# Footnote
fig.text(0.01, 0.01,
         'Class 4: off A_raw, both neurons in Creamer 56-subspace (n = 1321). '
         'Randi: undirected unc-31-sensitive pairs (Phase 0 config: 189 directed → 108 Class 4 undirected). '
         'CeNGEN: exploratory transcriptomic tier.',
         fontsize=6, color='#777777', wrap=True,
         transform=fig.transFigure)

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig(OUT / 'fig3_annotation_density.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig3_annotation_density.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 3 saved.')
