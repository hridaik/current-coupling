"""Figure 6 — Atlas Cross-Reference
Three panels:
  A: Categorization table (confirmed / novel / tested-not-sig)
  B: Category summary bar
  C: Funatlas observation count bar
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

DWELLING = '#4C6EF5'
C_GREEN  = '#2CA02C'   # confirmed
C_RED    = '#D62728'   # novel prediction (untested)
C_GRAY   = '#AAAAAA'   # tested, not significant

# ── Data from phase2b_pdf_audit.md §6 and figure_specification_package.md ────
confirmed_pairs = [
    {'pair': 'RMEL↔RMER', 'q': 'q_wt=0.000', 'occ': 22, 'dq': -0.0579, 'note': 'wt-sig'},
    {'pair': 'RMER→URYVR', 'q': 'q_wt=0.000', 'occ': 8, 'dq': None, 'note': 'wt-sig'},
    {'pair': 'RMER→RMEL', 'q': 'q_unc31=0.001', 'occ': 16, 'dq': None, 'note': 'unc-31'},
    {'pair': 'RMEL→OLQVR', 'q': 'q_wt=0.028', 'occ': 13, 'dq': None, 'note': 'wt-sig'},
    {'pair': 'RMER→OLQVR', 'q': 'q_wt=0.036', 'occ': 13, 'dq': None, 'note': 'wt-sig'},
    {'pair': 'RMEL→OLLL', 'q': 'q_unc31=0.002', 'occ': 19, 'dq': None, 'note': 'unc-31'},
    {'pair': 'RMER→OLLL', 'q': 'q_unc31=0.012', 'occ': 19, 'dq': None, 'note': 'unc-31'},
    {'pair': 'RMER→I1L', 'q': 'q_unc31=0.049', 'occ': 6, 'dq': None, 'note': 'unc-31'},
]
novel_pairs = [
    {'pair': 'ADEL→URYVR', 'occ': 0, 'dq_c': -0.1222, 'dq_g': -0.0853, 'rank': 5},
    {'pair': 'ADEL→URYDL', 'occ': 0, 'dq_c': -0.0980, 'dq_g': -0.0841, 'rank': 9},
]
notsig_pairs = [
    {'pair': 'ADEL→RMEL', 'q': 'q_wt=0.492', 'occ': 5, 'dq_c': -0.0957},
    {'pair': 'ADEL→URXL', 'q': 'q_wt=0.534', 'occ': 7, 'dq_c': -0.0450},
]

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 5.5))
gs  = fig.add_gridspec(1, 3, wspace=0.45, width_ratios=[3, 1, 1.6])
ax_a = fig.add_subplot(gs[0])
ax_b = fig.add_subplot(gs[1])
ax_c = fig.add_subplot(gs[2])

# ── Panel A: Categorization table ────────────────────────────────────────────
ax_a.axis('off')
ax_a.set_xlim(0, 1)
ax_a.set_ylim(0, 1)

section_configs = [
    ('CONFIRMED (funatlas q < 0.05)', confirmed_pairs, C_GREEN),
    ('NOVEL PREDICTIONS (occ = 0)', novel_pairs, C_RED),
    ('TESTED, NOT SIGNIFICANT', notsig_pairs, C_GRAY),
]

y_cursor = 0.95
header_h = 0.07
box_h    = 0.072
pad      = 0.012

for section_title, pairs_list, col in section_configs:
    # Section header
    ax_a.add_patch(mpatches.FancyBboxPatch(
        (0.01, y_cursor - header_h), 0.98, header_h,
        boxstyle='round,pad=0.01', fc=col, ec='none', alpha=0.85))
    ax_a.text(0.5, y_cursor - header_h/2, section_title,
              ha='center', va='center', fontsize=8.5, fontweight='bold',
              color='white')
    y_cursor -= header_h + pad

    for entry in pairs_list:
        pair_name = entry['pair']
        # Pair name box
        ax_a.add_patch(mpatches.FancyBboxPatch(
            (0.01, y_cursor - box_h), 0.34, box_h,
            boxstyle='round,pad=0.01', fc=col, ec='none', alpha=0.15))
        ax_a.text(0.18, y_cursor - box_h/2, pair_name,
                  ha='center', va='center', fontsize=8, fontweight='bold')

        # Stats
        if 'q' in entry:
            ax_a.text(0.40, y_cursor - box_h/2, entry['q'],
                      ha='left', va='center', fontsize=7.5, color='#444444')
        if 'occ' in entry:
            ax_a.text(0.62, y_cursor - box_h/2, f'occ={entry["occ"]}',
                      ha='left', va='center', fontsize=7.5, color='#444444')
        if entry.get('dq') is not None:
            ax_a.text(0.75, y_cursor - box_h/2,
                      f'ΔQ={entry["dq"]:.3f}', ha='left', va='center',
                      fontsize=7.5, color=DWELLING)
        if 'dq_c' in entry:
            ax_a.text(0.40, y_cursor - box_h/2,
                      f'ΔQ={entry["dq_c"]:.3f} (rank {entry.get("rank","?")})',
                      ha='left', va='center', fontsize=7.5,
                      color=DWELLING, fontweight='bold')
        if 'note' in entry:
            ax_a.text(0.88, y_cursor - box_h/2, entry.get('note',''),
                      ha='center', va='center', fontsize=7, color='#666666')

        y_cursor -= box_h + pad/2

    y_cursor -= pad

ax_a.set_title('A  Funatlas validation status', fontsize=9, loc='left', fontweight='bold')

# ── Panel B: Category count bar ───────────────────────────────────────────────
cat_names  = ['Confirmed\n(q<0.05)', 'Novel\n(occ=0)', 'Not sig.']
cat_counts = [8, 2, 2]
cat_colors = [C_GREEN, C_RED, C_GRAY]

bars = ax_b.bar(cat_names, cat_counts, color=cat_colors, width=0.6,
                edgecolor='white', linewidth=0.5)
for bar, cnt in zip(bars, cat_counts):
    ax_b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
              str(cnt), ha='center', va='bottom', fontsize=9, fontweight='bold')

ax_b.set_ylim(0, 11)
ax_b.set_ylabel('Number of pairs', fontsize=9)
ax_b.set_title('B  Summary', fontsize=9, loc='left', fontweight='bold')
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)
ax_b.tick_params(axis='x', labelsize=8)

# ── Panel C: Observation count bar ───────────────────────────────────────────
all_pairs = []
all_occ   = []
all_cols  = []
all_labels = []

for p in confirmed_pairs:
    all_pairs.append(p['pair'])
    all_occ.append(p['occ'])
    all_cols.append(C_GREEN)

for p in novel_pairs:
    all_pairs.append(p['pair'])
    all_occ.append(p['occ'])
    all_cols.append(C_RED)

for p in notsig_pairs:
    all_pairs.append(p['pair'])
    all_occ.append(p['occ'])
    all_cols.append(C_GRAY)

y_c = np.arange(len(all_pairs))
hbars = ax_c.barh(y_c, all_occ, color=all_cols, height=0.65,
                   edgecolor='white', linewidth=0.3)
ax_c.axvline(5, color='#CCCCCC', lw=0.7, ls='--', label='occ=5 threshold')
ax_c.set_yticks(y_c)
ax_c.set_yticklabels(all_pairs, fontsize=7.5)
ax_c.set_xlabel('Funatlas observation count', fontsize=8.5)
ax_c.set_title('C  Funatlas coverage', fontsize=9, loc='left', fontweight='bold')
ax_c.spines['top'].set_visible(False)
ax_c.spines['right'].set_visible(False)
ax_c.legend(fontsize=7, frameon=False)

# ── Footnote ─────────────────────────────────────────────────────────────────
fig.text(0.01, -0.01,
         'Confirmed: q_wt < 0.05 or q_unc31 < 0.05 in Randi/Leifer funatlas. '
         'Novel predictions: occ_wt = 0 (never measured). '
         'ΔQ values are from CePNEM coordinate (Phase 2 Stage 2). '
         'ADEL wt-significant targets in funatlas (ADAL, ADER, AINL, AQR, FLPL) are outside the 61-neuron set.',
         fontsize=6.5, color='#777777', transform=fig.transFigure)

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
fig.suptitle('Functional validation landscape for PDF network predictions', fontsize=10, y=0.99)
plt.savefig(OUT / 'fig6_atlas_crossref.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig6_atlas_crossref.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 6 saved.')
