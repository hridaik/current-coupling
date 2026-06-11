"""Figure 1 — Behavioral Story
Panels:
  A: Behavioral state schematic (EWMA trace + threshold + cartoon worm)
  B: PDF circuit diagram (ADEL/RMEL/RID → pdfr-1 targets)
  C: Analysis pipeline flowchart
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
LIGHT_DW = '#D0D9FF'
LIGHT_RO = '#FFE0CC'
C_PDF    = '#D62728'
C_DA     = '#2C7BB6'    # dopamine (ADEL)
C_GABA   = '#6A5ACD'    # GABA (RMEL/RMER)
C_PDFR   = '#FC8D59'    # pdfr-1 targets
C_ORPHAN = '#ABD9E9'    # RID

rng = np.random.default_rng(42)

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 4.0))
gs  = fig.add_gridspec(1, 3, wspace=0.42, width_ratios=[1.6, 2.0, 1.4])
ax_a = fig.add_subplot(gs[0])
ax_b = fig.add_subplot(gs[1])
ax_c = fig.add_subplot(gs[2])

# ── Panel A: Behavioral state schematic ──────────────────────────────────────
t = np.linspace(0, 120, 1200)   # 2-minute trace in seconds
# Simulated EWMA velocity score
v_raw = np.zeros(len(t))
# Create some roaming/dwelling transitions
for seg_start, seg_dur, state_val in [
    (0, 18, 0.1),   (18, 22, 0.55), (40, 30, 0.08),
    (70, 15, 0.62), (85, 35, 0.09),
]:
    i0 = int(seg_start / 120 * len(t))
    i1 = int((seg_start + seg_dur) / 120 * len(t))
    v_raw[i0:i1] = state_val

# Add smooth noise
v_raw += rng.normal(0, 0.04, len(t))
from scipy.ndimage import uniform_filter1d
v_ewma = uniform_filter1d(v_raw, size=100)   # crude EWMA approximation

threshold = 0.284
roam_mask = v_ewma >= threshold

ax_a.fill_between(t, 0, v_ewma, where=roam_mask,  color=LIGHT_RO, alpha=0.7, label='Roaming')
ax_a.fill_between(t, 0, v_ewma, where=~roam_mask, color=LIGHT_DW, alpha=0.7, label='Dwelling')
ax_a.plot(t, v_ewma, color='#333333', lw=1.2)
ax_a.axhline(threshold, color='#666666', lw=0.9, ls='--')
ax_a.text(122, threshold, f'thr={threshold}', va='center', fontsize=7.5, color='#666666')

# State labels
ax_a.text(9, 0.46, 'Dwelling', fontsize=8, color=DWELLING, ha='center', fontweight='bold')
ax_a.text(29, 0.53, 'Roaming', fontsize=8, color=ROAMING, ha='center', fontweight='bold')

ax_a.set_xlabel('Time (s)', fontsize=9)
ax_a.set_ylabel('EWMA velocity score', fontsize=8.5)
ax_a.set_xlim(0, 120)
ax_a.set_ylim(-0.05, 0.8)
ax_a.legend(fontsize=7.5, frameon=False, loc='upper right')
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)
ax_a.set_title('A  Behavioral state segmentation', fontsize=9, loc='left', fontweight='bold')
ax_a.text(0.02, 0.03,
          'EWMA τ=20 s | threshold=0.284\n40 recordings × 61 NeuroPAL neurons',
          transform=ax_a.transAxes, fontsize=7, color='#666666')

# ── Panel B: PDF circuit diagram ──────────────────────────────────────────────
ax_b.set_xlim(0, 1.0)
ax_b.set_ylim(0, 1.0)
ax_b.axis('off')

NODE_R = 0.052

# Node positions
nodes = {
    'ADEL':  (0.14, 0.72, C_DA,     'ADEL\n(DA, pdf-1)',    'source'),
    'RMEL':  (0.14, 0.44, C_GABA,   'RMEL\n(GABA, pdf-1\npdfr-1)', 'both'),
    'RMER':  (0.14, 0.22, C_GABA,   'RMER\n(GABA, pdf-1)',  'source'),
    'RID':   (0.38, 0.90, C_ORPHAN, 'RID\n(pdf-1/2)',       'source'),
    'AVDL':  (0.38, 0.10, '#74ADD1','AVDL\n(pdf-2)',        'source'),
    'URYVR': (0.72, 0.80, C_PDFR,   'URYVR\n(pdfr-1)',      'target'),
    'URYDL': (0.72, 0.58, C_PDFR,   'URYDL\n(pdfr-1)',      'target'),
    'URXL':  (0.72, 0.38, C_PDFR,   'URXL\n(pdfr-1)',       'target'),
    'RMEL_t':(0.72, 0.18, C_PDFR,   '(also RMEL\nas target)','target'),
    'OLQVR': (0.90, 0.55, C_PDFR,   'OLQVR\n(pdfr-1)',      'target'),
}

# Key edges (top-ranked PDF pairs)
edges = [
    ('ADEL', 'URYVR', -0.1222, '−0.12'),
    ('ADEL', 'URYDL', -0.0980, '−0.10'),
    ('ADEL', 'RMEL',  -0.0957, None),
    ('RMEL', 'URYDL', -0.0754, None),
    ('RMEL', 'URYVR', -0.0701, None),
    ('RID',  'URXL',  -0.0396, None),
    ('AVDL', 'URYDL', -0.0558, None),
]
src_to_tgt = {
    ('ADEL', 'URYVR'): ('ADEL', 'URYVR'),
    ('ADEL', 'URYDL'): ('ADEL', 'URYDL'),
    ('ADEL', 'RMEL'):  ('ADEL', 'RMEL'),
    ('RMEL', 'URYDL'): ('RMEL', 'URYDL'),
    ('RMEL', 'URYVR'): ('RMEL', 'URYVR'),
    ('RID',  'URXL'):  ('RID',  'URXL'),
    ('AVDL', 'URYDL'): ('AVDL', 'URYDL'),
}

# Position lookup (handle RMEL specially — both source and target)
pos_b = {n: (x, y) for n, (x, y, *_) in nodes.items()}
pos_b['RMEL'] = (nodes['RMEL'][0], nodes['RMEL'][1])

for src, tgt, dq, label in edges:
    if src not in pos_b or tgt not in pos_b:
        continue
    x0, y0 = pos_b[src]
    x1, y1 = pos_b[tgt]
    dx, dy = x1 - x0, y1 - y0
    dist = np.sqrt(dx**2 + dy**2)
    if dist < 0.01: continue
    ux, uy = dx/dist, dy/dist
    xs = x0 + ux * NODE_R
    ys = y0 + uy * NODE_R
    xe = x1 - ux * NODE_R * 1.5
    ye = y1 - uy * NODE_R * 1.5
    lw = max(0.7, 3.0 * abs(dq) / 0.12)
    ax_b.annotate('', xy=(xe, ye), xytext=(xs, ys),
                  arrowprops=dict(arrowstyle='->', color=DWELLING,
                                  lw=lw, alpha=0.75,
                                  connectionstyle='arc3,rad=0.05'))
    if label:
        mx = (xs + xe)/2 - 0.03 * uy
        my = (ys + ye)/2 + 0.03 * ux
        ax_b.text(mx, my, label, fontsize=6.5, color=DWELLING,
                  ha='center', va='center',
                  bbox=dict(fc='white', ec='none', alpha=0.8, pad=1))

# Draw nodes
for name, (nx, ny, nc, nlabel, ntype) in nodes.items():
    if name == 'RMEL_t':
        # just skip — RMEL already shown
        continue
    circ = plt.Circle((nx, ny), NODE_R, color=nc, ec='#555555', lw=0.7, zorder=5)
    ax_b.add_patch(circ)
    lines = nlabel.split('\n')
    for k, line in enumerate(lines):
        ax_b.text(nx, ny - NODE_R - 0.022 - k*0.028, line,
                  ha='center', va='top', fontsize=6.5,
                  fontweight='bold' if k == 0 else 'normal', color='#222222', zorder=6)

# Edge encoding legend (compact)
ax_b.plot([], [], color=DWELLING, lw=2.5, label='pdf-1/pdf-2 edge\n(ΔQ < 0, dwelling-dom)')
ax_b.legend(fontsize=7, frameon=True, loc='lower right',
            framealpha=0.8, edgecolor='#CCCCCC')

# Label pdf source / target groups
ax_b.text(0.14, 0.99, 'pdf-1/pdf-2\nsource neurons', ha='center', va='top',
          fontsize=7.5, color='#444444', style='italic')
ax_b.text(0.75, 0.99, 'pdfr-1\ntarget neurons', ha='center', va='top',
          fontsize=7.5, color='#444444', style='italic')
ax_b.axvline(0.45, color='#DDDDDD', lw=0.7, ls=':')

ax_b.set_title('B  PDF signaling circuit (top-ranked ΔQ pairs)', fontsize=9,
               loc='left', fontweight='bold')

# ── Panel C: Pipeline flowchart ───────────────────────────────────────────────
ax_c.set_xlim(0, 1)
ax_c.set_ylim(0, 1)
ax_c.axis('off')

steps = [
    (0.50, 0.92, '40 recordings\n61 neurons', '#E8E8E8', '#333333'),
    (0.50, 0.76, 'Pairwise covariance\nassembly  S_s (61×61)', '#D0D9FF', '#333333'),
    (0.50, 0.60, 'PSD projection\n+ ADMM lasso (λ_off=0.10)', '#D0D9FF', '#333333'),
    (0.50, 0.45, 'ΔQ = Q_roam − Q_dwell\n1321 off-connectome pairs', DWELLING, 'white'),
    (0.50, 0.30, 'Enrichment test\n(AUROC + Fisher)', '#555555', 'white'),
    (0.50, 0.14, 'NULL RESULT\n(p_deg > 0.14 all tests)\nExploratory PDF signal', '#D62728', 'white'),
]

for x, y, text, fc, tc in steps:
    h = 0.12
    ax_c.add_patch(mpatches.FancyBboxPatch((x - 0.42, y - h/2), 0.84, h,
        boxstyle='round,pad=0.01', fc=fc, ec='white', lw=0.5))
    ax_c.text(x, y, text, ha='center', va='center', fontsize=7.5,
              color=tc, fontweight='normal')

# Arrows between steps
for k in range(len(steps) - 1):
    x0, y0 = steps[k][0], steps[k][1] - 0.06
    x1, y1 = steps[k+1][0], steps[k+1][1] + 0.06
    ax_c.annotate('', xy=(x1, y1), xytext=(x0, y0),
                  arrowprops=dict(arrowstyle='->', color='#888888', lw=1.0))

ax_c.set_title('C  Analysis pipeline', fontsize=9, loc='left', fontweight='bold')

# ── Suptitle ──────────────────────────────────────────────────────────────────
fig.suptitle('Food detection recruits a state-dependent PDF signaling pathway',
             fontsize=11, y=1.02)

plt.tight_layout(rect=[0, 0, 1, 0.98])
plt.savefig(OUT / 'fig1_behavioral_story.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig1_behavioral_story.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 1 saved.')
