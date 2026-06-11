"""Figure 7 — Prediction Figure
"Predicted dwelling-specific PDF coupling"
Panels: A = experimental design schematic, B = predicted response traces, C = outcome table.
All schematic — no experimental data. Labeled PREDICTED throughout.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

DWELLING = '#4C6EF5'
ROAMING  = '#FF6B35'
LIGHT_DW = '#A8BFFF'
LIGHT_RO = '#FFCBA8'
C_PDF    = '#D62728'

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 5.5))
gs  = fig.add_gridspec(1, 3, wspace=0.45, width_ratios=[1.6, 2.2, 1.2])
ax_a = fig.add_subplot(gs[0])
ax_b = fig.add_subplot(gs[1])
ax_c = fig.add_subplot(gs[2])

# ── Panel A: Experimental design ─────────────────────────────────────────────
ax_a.axis('off')
ax_a.set_xlim(0, 1)
ax_a.set_ylim(0, 1)

def rounded_box(ax, x, y, w, h, color, text, fontsize=9, alpha=0.9, text_color='white'):
    ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h,
        boxstyle='round,pad=0.01', fc=color, ec='none', alpha=alpha))
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, fontweight='bold')

# Animal + ADEL expression
rounded_box(ax_a, 0.05, 0.80, 0.90, 0.14, '#4A90D9',
            'ADEL :: ChrimsonR\n(optogenetic driver)', fontsize=8.5)

# Arrow down
ax_a.annotate('', xy=(0.50, 0.73), xytext=(0.50, 0.80),
              arrowprops=dict(arrowstyle='->', color='#555555', lw=1.2))

# State segmentation box
rounded_box(ax_a, 0.05, 0.58, 0.90, 0.13, '#888888',
            'Behavioral segmentation\n(EWMA vel, τ=20 s, thr=0.284)', fontsize=8, alpha=0.7)

# Two branches
ax_a.plot([0.50, 0.25, 0.25], [0.58, 0.52, 0.47], color='#555555', lw=1.2)
ax_a.plot([0.50, 0.75, 0.75], [0.58, 0.52, 0.47], color='#555555', lw=1.2)

rounded_box(ax_a, 0.02, 0.38, 0.42, 0.09, DWELLING, 'Dwelling bout', fontsize=9)
rounded_box(ax_a, 0.56, 0.38, 0.42, 0.09, ROAMING, 'Roaming bout', fontsize=9)

ax_a.annotate('', xy=(0.23, 0.38), xytext=(0.23, 0.32),
              arrowprops=dict(arrowstyle='->', color='#555555', lw=1.2))
ax_a.annotate('', xy=(0.77, 0.38), xytext=(0.77, 0.32),
              arrowprops=dict(arrowstyle='->', color='#555555', lw=1.2))

# Stimulation
rounded_box(ax_a, 0.02, 0.22, 0.42, 0.09, LIGHT_DW,
            'ADEL stim.\nRecord URY', fontsize=8, text_color='#333333')
rounded_box(ax_a, 0.56, 0.22, 0.42, 0.09, LIGHT_RO,
            'ADEL stim.\nRecord URY', fontsize=8, text_color='#333333')

# Genetic arms
ax_a.text(0.50, 0.14, '+ unc-31(e928) null  /  + pdfr-1(ok3425) null',
          ha='center', va='center', fontsize=7.5, color='#555555', style='italic')

rounded_box(ax_a, 0.05, 0.03, 0.90, 0.09, '#DDDDDD',
            'Measure: ΔF/F in URYDL / URYVR during and after ADEL stimulation',
            fontsize=7.5, text_color='#333333', alpha=0.7)

ax_a.set_title('A  Experimental design', fontsize=9, loc='left', fontweight='bold', pad=4)

# ── Panel B: Predicted response traces ────────────────────────────────────────
t = np.linspace(0, 10, 500)  # seconds post-stimulus

def gaussian_pulse(t, center=1.5, width=1.5, amp=1.0):
    return amp * np.exp(-0.5 * ((t - center) / width)**2)

# Condition 1: Roaming — flat
trace_roam = np.random.default_rng(42).normal(0, 0.04, len(t))

# Condition 2: Dwelling — suppression pulse (inverted, matching Q_dwell < 0)
trace_dwell = -gaussian_pulse(t, center=1.5, width=1.2, amp=0.6) + \
              np.random.default_rng(43).normal(0, 0.04, len(t))

# Condition 3: PDF disruption — flat (like roaming)
trace_pdf_ko = np.random.default_rng(44).normal(0, 0.04, len(t))

conditions = [
    ('1: Roaming (WT)', trace_roam, ROAMING, 'No coupling\n(Q_roam ≈ 0)'),
    ('2: Dwelling (WT)', trace_dwell, DWELLING, 'Inverse coupling\n(Q_dwell < 0)'),
    ('3: PDF disruption\n(unc-31 / pdfr-1 null)', trace_pdf_ko, '#888888', 'Coupling abolished\n(prediction)'),
]

gs_b = ax_b.get_subplotspec().get_gridspec()
ax_b.remove()
axs_b = []
for k in range(3):
    a = fig.add_subplot(gs_b[0, 1], frame_on=True)
    axs_b.append(a)

# Replace with actual sub-gridspec
from matplotlib.gridspec import GridSpecFromSubplotSpec
inner_gs = GridSpecFromSubplotSpec(3, 1, subplot_spec=gs_b[0, 1], hspace=0.55)
axs_b_new = [fig.add_subplot(inner_gs[k]) for k in range(3)]
for a in axs_b:
    a.remove()

for k, (cond_label, trace, col, outcome) in enumerate(conditions):
    ax = axs_b_new[k]
    # Shaded stimulus window
    ax.axvspan(0, 0.5, color='yellow', alpha=0.3, label='stim')
    ax.plot(t, trace, color=col, lw=1.4)
    ax.axhline(0, color='#CCCCCC', lw=0.6, ls='--')
    ax.set_xlim(0, 8)
    ax.set_ylim(-1.0, 0.6)
    ax.set_yticks([-0.5, 0, 0.5])
    ax.tick_params(labelsize=7)
    ax.set_title(cond_label, fontsize=8, color=col, fontweight='bold', pad=2)
    ax.text(0.97, 0.05, outcome, transform=ax.transAxes,
            ha='right', va='bottom', fontsize=7, color=col)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if k < 2:
        ax.set_xticklabels([])
    else:
        ax.set_xlabel('Time post-stim (s)', fontsize=8)
    if k == 1:
        ax.set_ylabel('URYDL/URYVR  ΔF/F', fontsize=8)

# PREDICTED watermark on the middle trace axes
axs_b_new[1].text(0.5, 0.5, 'PREDICTED\n(not observed)',
                  transform=axs_b_new[1].transAxes,
                  ha='center', va='center', fontsize=11,
                  color='#BBBBBB', alpha=0.6, rotation=20,
                  fontweight='bold')

axs_b_new[0].set_title('B  Predicted response traces (PREDICTED — no data)',
                        fontsize=9, loc='left', fontweight='bold',
                        pad=4, x=-0.18)

# ── Panel C: Summary prediction table ─────────────────────────────────────────
ax_c.axis('off')
ax_c.set_xlim(0, 1)
ax_c.set_ylim(0, 1)

headers = ['Condition', 'ADEL→URY\ncoupling', 'Prediction']
rows_c = [
    ['1: Roaming\n(WT)', 'Absent\n(Q_roam ≈ 0)', 'No URY response'],
    ['2: Dwelling\n(WT)', 'Present\n(Q_dwell < 0)', 'Inverse\nco-activation'],
    ['3: unc-31 /\npdfr-1 null', 'Absent', 'Dwelling\ncoupling abolished'],
]
row_colors_c = [LIGHT_RO, LIGHT_DW, '#EEEEEE']

col_x = [0.02, 0.36, 0.68]
col_w = [0.32, 0.30, 0.30]

# Header
for c_idx, h in enumerate(headers):
    ax_c.add_patch(mpatches.FancyBboxPatch(
        (col_x[c_idx], 0.90), col_w[c_idx], 0.08,
        boxstyle='round,pad=0.005', fc='#444444', ec='none'))
    ax_c.text(col_x[c_idx] + col_w[c_idx]/2, 0.94, h,
              ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')

y_start = 0.88
row_h   = 0.26
for r_idx, (row_data, row_col) in enumerate(zip(rows_c, row_colors_c)):
    y_r = y_start - r_idx * (row_h + 0.02)
    for c_idx, cell_text in enumerate(row_data):
        ax_c.add_patch(mpatches.FancyBboxPatch(
            (col_x[c_idx], y_r - row_h), col_w[c_idx], row_h,
            boxstyle='round,pad=0.005', fc=row_col, ec='white', lw=0.5, alpha=0.6))
        ax_c.text(col_x[c_idx] + col_w[c_idx]/2, y_r - row_h/2,
                  cell_text, ha='center', va='center', fontsize=7.5, color='#222222')

ax_c.set_title('C  Predicted outcomes', fontsize=9, loc='left', fontweight='bold', pad=4)

# ── Suptitle + footnote ───────────────────────────────────────────────────────
fig.suptitle('Predicted dwelling-specific PDF coupling', fontsize=11, y=1.01)
fig.text(0.01, -0.02,
         'Traces in B are model predictions derived from CePNEM ΔQ estimates '
         '(ADEL–URYVR ΔQ=−0.122, rank 5/1321; ADEL–URYDL ΔQ=−0.098, rank 9/1321). '
         'ADEL→URYVR and ADEL→URYDL have zero funatlas observations — never tested experimentally. '
         'Behavioral segmentation parameters: EWMA threshold=0.284, τ=20 s (Phase 0 locked values).',
         fontsize=6.5, color='#777777', transform=fig.transFigure)

plt.savefig(OUT / 'fig7_prediction_figure.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig7_prediction_figure.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 7 saved.')
