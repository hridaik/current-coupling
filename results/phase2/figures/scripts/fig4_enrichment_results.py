"""Figure 4 — Enrichment Results
Forest plot. True uncertainty for neuropeptide rows (null_std from stage4_results.json).
No borrowed uncertainty for Randi/PDF rows — null_mean only, explicit disclosure.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

# ── Color convention ─────────────────────────────────────────────────────────
DWELLING = '#4C6EF5'
ROAMING  = '#FF6B35'
C_PEP    = '#666666'
C_RANDI  = '#2CA02C'
C_PDF    = '#D62728'
C_PASS   = '#D62728'   # PASS row highlight
C_FAIL   = '#AAAAAA'   # FAIL row point color

# ── AUROC data ───────────────────────────────────────────────────────────────
# (row_label, coord_label, auroc_obs, null_mean, null_std_or_None, p_deg, is_pass, ann_color)
auroc_rows = [
    ('Neuropeptide',  'CePNEM', 0.5033, 0.5021, 0.01172,  0.475,  False, C_PEP),
    ('Neuropeptide',  'GCaMP',  0.5140, 0.4979, 0.01596,  0.142,  False, C_PEP),
    ('Randi unc-31',  'CePNEM', 0.4953, 0.5037, None,     0.656,  False, C_RANDI),
    ('Randi unc-31',  'GCaMP',  0.5167, 0.5014, None,     0.278,  False, C_RANDI),
    ('Bentley PDF*',  'CePNEM', 0.5560, 0.5015, None,     0.023,  True,  C_PDF),
    ('Bentley PDF*',  'GCaMP',  0.5260, 0.5039, None,     0.261,  False, C_PDF),
]

# ── Fisher OR data ───────────────────────────────────────────────────────────
# (row_label, coord_label, or_obs, p_deg, is_pass, ann_color, special_zero)
or_rows = [
    ('Neuropeptide',  'CePNEM', 0.533,  0.981,  False, C_PEP,   False),
    ('Neuropeptide',  'GCaMP',  0.835,  0.716,  False, C_PEP,   False),
    ('Randi unc-31',  'CePNEM', 0.000,  1.000,  False, C_RANDI, True),   # OR=0, special
    ('Randi unc-31',  'GCaMP',  0.587,  0.792,  False, C_RANDI, False),
    ('Bentley PDF*',  'CePNEM', 5.456,  0.008,  True,  C_PDF,   False),
    ('Bentley PDF*',  'GCaMP',  1.089,  0.670,  False, C_PDF,   False),
]

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(8.5, 5.8))
gs  = fig.add_gridspec(1, 2, wspace=0.55)
ax_a = fig.add_subplot(gs[0])   # AUROC forest
ax_b = fig.add_subplot(gs[1])   # Fisher OR forest

# ── Panel A: AUROC ────────────────────────────────────────────────────────────
n = len(auroc_rows)
y_pos = np.arange(n)[::-1]   # top row = row 0

# Group separators
group_bounds = [0, 2, 4, 6]   # every 2 rows = one annotation type

for idx, (row_lbl, coord, auroc, null_mn, null_sd, p_deg, is_pass, col) in enumerate(auroc_rows):
    y = y_pos[idx]
    dot_color = col if is_pass else C_FAIL
    dot_size  = 70 if is_pass else 45

    # Error bar (true: ±2SD; absent: no bar)
    if null_sd is not None:
        ax_a.errorbar(auroc, y, xerr=[[auroc - (null_mn - 2*null_sd)],
                                      [(null_mn + 2*null_sd) - auroc]],
                      fmt='none', ecolor='#CCCCCC', elinewidth=1.2, capsize=3, capthick=1)

    # Null mean tick
    ax_a.plot(null_mn, y, '|', color='#999999', markersize=10, markeredgewidth=1.2)

    # Observed point
    marker = 'D' if is_pass else 'o'
    ax_a.scatter(auroc, y, s=dot_size, color=dot_color, zorder=5,
                 marker=marker, edgecolors='white', linewidths=0.5)

    # p-value annotation
    p_str = f'p={p_deg:.3f}' if p_deg >= 0.001 else f'p<0.001'
    ax_a.text(0.620, y, p_str, va='center', ha='left', fontsize=7,
              color=col if is_pass else '#888888',
              fontweight='bold' if is_pass else 'normal')

ax_a.axvline(0.5, color='#333333', lw=0.8, ls='--', label='Null (AUROC=0.5)')
ax_a.set_xlim(0.44, 0.65)
ax_a.set_ylim(-0.7, n - 0.3)
ax_a.set_yticks(y_pos)

# Y-tick labels: combine annotation + coord
ylabels = [f'{r[0]}\n({r[1]})' for r in auroc_rows]
ax_a.set_yticklabels(ylabels, fontsize=8)
ax_a.set_xlabel('AUROC', fontsize=9)
ax_a.set_title('A  AUROC enrichment tests', fontsize=9, loc='left', fontweight='bold')
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)

# Group separators
for b in [2, 4]:
    ax_a.axhline(n - b - 0.5, color='#DDDDDD', lw=0.6)

# Significance threshold note
ax_a.axvline(0.5, color='#333333', lw=0.8, ls='--')

# ── Panel B: Fisher OR ────────────────────────────────────────────────────────
OR_FLOOR = 0.15   # floor for log scale (OR=0 plotted here with triangle)
ax_b.set_xscale('log')

for idx, (row_lbl, coord, or_obs, p_deg, is_pass, col, is_zero) in enumerate(or_rows):
    y = y_pos[idx]
    dot_color = col if is_pass else C_FAIL
    dot_size  = 70 if is_pass else 45

    if is_zero:
        # OR = 0: left-pointing triangle at floor
        ax_b.scatter(OR_FLOOR * 1.05, y, s=60, color=C_RANDI, marker='<',
                     zorder=5, edgecolors='white', linewidths=0.5)
        ax_b.text(OR_FLOOR * 1.12, y, 'OR=0', va='center', fontsize=7, color='#666666')
    else:
        marker = 'D' if is_pass else 'o'
        ax_b.scatter(or_obs, y, s=dot_size, color=dot_color, zorder=5,
                     marker=marker, edgecolors='white', linewidths=0.5)

    p_str = f'p={p_deg:.3f}' if p_deg >= 0.001 else 'p<0.001'
    ax_b.text(18, y, p_str, va='center', ha='left', fontsize=7,
              color=col if is_pass else '#888888',
              fontweight='bold' if is_pass else 'normal')

ax_b.axvline(1.0, color='#333333', lw=0.8, ls='--')
ax_b.set_xlim(OR_FLOOR, 25)
ax_b.set_ylim(-0.7, n - 0.3)
ax_b.set_yticks(y_pos)

ylabels_b = [f'{r[0]}\n({r[1]})' for r in or_rows]
ax_b.set_yticklabels(ylabels_b, fontsize=8)
ax_b.set_xlabel('Fisher OR  (top K=20, log scale)', fontsize=9)
ax_b.set_title('B  Fisher K=20 odds ratios', fontsize=9, loc='left', fontweight='bold')
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)
ax_b.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
    lambda x, _: f'{x:.0f}' if x >= 1 else f'{x:.1f}'))

for b in [2, 4]:
    ax_b.axhline(n - b - 0.5, color='#DDDDDD', lw=0.6)

# ── Legend ────────────────────────────────────────────────────────────────────
leg_handles = [
    mlines.Line2D([], [], color=C_PEP,   marker='o', ls='none', markersize=6, label='Neuropeptide (Ripoll-Sánchez)'),
    mlines.Line2D([], [], color=C_RANDI, marker='o', ls='none', markersize=6, label='Randi unc-31'),
    mlines.Line2D([], [], color=C_PDF,   marker='D', ls='none', markersize=6, label='Bentley PDF (pass)'),
    mlines.Line2D([], [], color='#CCCCCC', ls='-', lw=1.5, label='Null ± 2SD (neuropeptide only)'),
    mlines.Line2D([], [], color='#999999', marker='|', ls='none', markersize=8, label='Null mean'),
]
fig.legend(handles=leg_handles, loc='lower center', ncol=3, fontsize=7.5,
           bbox_to_anchor=(0.5, -0.02), frameon=False)

# ── Footnote ─────────────────────────────────────────────────────────────────
note = (
    'Error bars: ±2 SD of degree-preserving permutation null (1000 permutations). '
    'Shown for neuropeptide rows only (null SD available). '
    'Randi and PDF rows: null mean shown; SD not stored in result files. '
    '* Bentley PDF is an exploratory post-hoc annotation (not pre-specified). '
    'Threshold: degree-preserving p < 0.05.'
)
fig.text(0.01, -0.04, note, fontsize=6.5, color='#666666',
         transform=fig.transFigure, wrap=True)

plt.tight_layout(rect=[0, 0.04, 1, 0.97])
fig.suptitle('No evidence for broad neuropeptide enrichment; exploratory PDF signal in CePNEM',
             fontsize=10, y=0.99)

plt.savefig(OUT / 'fig4_enrichment_results.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig4_enrichment_results.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 4 saved.')
