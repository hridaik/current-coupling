"""Figure 5 — ADEL-Centered PDF Network
Manual node layout with matplotlib patches and FancyArrowPatch.
Shows all 17 nonzero DQ_cepnem pairs. Line width ∝ |DQ_cepnem|.
Color: dwelling-dominant (DQ<0)=dwelling blue; roaming-dominant(DQ>0)=roaming orange.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

DWELLING = '#4C6EF5'
ROAMING  = '#FF6B35'
C_PDF    = '#D62728'

# ── Complete 17-pair network (from Phase 2C-A.1 extraction) ──────────────────
pairs = [
    # (source, target, dq_cepnem, dq_gcamp, ligand, funatlas_status)
    # status: 'confirmed', 'untested', 'not_sig', 'na'
    ('ADEL', 'URYVR', -0.1222, -0.0853, 'pdf-1',  'untested'),
    ('ADEL', 'URYDL', -0.0980, -0.0841, 'pdf-1',  'untested'),
    ('ADEL', 'RMEL',  -0.0957, -0.0824, 'pdf-1',  'not_sig'),
    ('RMEL', 'URYDL', -0.0754, -0.1259, 'pdf-1',  'na'),
    ('RMEL', 'URYVR', -0.0701, -0.1232, 'pdf-1',  'na'),
    ('RMEL', 'RMER',  -0.0579,  0.0000, 'pdf-1',  'confirmed'),
    ('AVDL', 'URYDL', -0.0558, -0.0240, 'pdf-2',  'na'),
    ('ADEL', 'URXL',  -0.0450, -0.1516, 'pdf-1',  'not_sig'),
    ('RID',  'URXL',  -0.0396, -0.0220, 'pdf-1',  'na'),
    ('ADEL', 'OLQVR', -0.0215,  0.0000, 'pdf-1',  'na'),
    ('RID',  'RMEL',  -0.0190,  0.0654, 'pdf-1',  'na'),
    ('RID',  'AVDL',  +0.0172, +0.0312, 'pdf-1',  'na'),   # roaming-dom
    ('RMER', 'OLQVL', +0.0169, -0.1005, 'pdf-1',  'na'),   # roaming-dom
    ('RMER', 'I1R',   +0.0149,  0.0000, 'pdf-1',  'na'),   # roaming-dom
    ('RMEL', 'URYVL', -0.0049,  0.0000, 'pdf-1',  'na'),   # marginal
    ('RID',  'OLQDL', -0.0048, -0.1125, 'pdf-1',  'na'),   # marginal
    ('AVDL', 'OLQDL', -0.0019,  0.0000, 'pdf-2',  'na'),   # marginal
]

# ── Node metadata ─────────────────────────────────────────────────────────────
node_info = {
    'ADEL':  {'color': '#2C7BB6', 'label': 'ADEL\n(DA, pdf-1)', 'shape': '^'},   # triangle = source
    'AVDL':  {'color': '#74ADD1', 'label': 'AVDL\n(ACh, pdf-2)', 'shape': '^'},
    'RID':   {'color': '#ABD9E9', 'label': 'RID\n(pdf-1/2)', 'shape': '^'},
    'RMEL':  {'color': '#6A5ACD', 'label': 'RMEL\n(GABA, pdf-1\npdfr-1)', 'shape': 's'},  # square = source+target
    'RMER':  {'color': '#7B68EE', 'label': 'RMER\n(GABA, pdf-1)', 'shape': '^'},
    'URYVR': {'color': '#D73027', 'label': 'URYVR\n(pdfr-1)', 'shape': 'o'},
    'URYDL': {'color': '#FC8D59', 'label': 'URYDL\n(pdfr-1)', 'shape': 'o'},
    'URYVL': {'color': '#FEE090', 'label': 'URYVL\n(pdfr-1)', 'shape': 'o'},
    'URXL':  {'color': '#E0F3F8', 'label': 'URXL\n(pdfr-1)', 'shape': 'o'},
    'OLQVR': {'color': '#FFFFBF', 'label': 'OLQVR\n(pdfr-1)', 'shape': 'o'},
    'OLQVL': {'color': '#FFFFBF', 'label': 'OLQVL', 'shape': 'o'},
    'OLQDL': {'color': '#FFFFBF', 'label': 'OLQDL', 'shape': 'o'},
    'I1R':   {'color': '#FFFFFF', 'label': 'I1R', 'shape': 'o'},
}

# ── Node positions (x, y in data coordinates) ─────────────────────────────────
pos = {
    'ADEL':  (0.12, 0.82),
    'AVDL':  (0.12, 0.32),
    'RID':   (0.40, 0.92),
    'RMEL':  (0.42, 0.65),
    'RMER':  (0.42, 0.40),
    'URYVR': (0.78, 0.82),
    'URYDL': (0.78, 0.58),
    'URYVL': (0.78, 0.48),
    'URXL':  (0.78, 0.32),
    'OLQVR': (0.92, 0.68),
    'OLQVL': (0.92, 0.40),
    'OLQDL': (0.78, 0.18),
    'I1R':   (0.62, 0.20),
}

# ── Utility ───────────────────────────────────────────────────────────────────
def edge_color(dq):
    return DWELLING if dq < 0 else ROAMING

def edge_lw(dq):
    # Scale: |dq|=0.12 → lw=3.5, |dq|=0.005 → lw=0.6
    return max(0.5, 3.5 * abs(dq) / 0.12)

def edge_alpha(dq):
    return max(0.25, min(1.0, abs(dq) / 0.06))

def edge_style(status):
    return '--' if status == 'untested' else '-'

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6.5))
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.05)
ax.set_aspect('equal')
ax.axis('off')

NODE_R = 0.055   # node circle radius

# Draw edges first (behind nodes)
edge_label_offset = {}   # avoid overlap
for src, tgt, dq_c, dq_g, ligand, status in pairs:
    if abs(dq_c) < 0.001:
        continue
    if src not in pos or tgt not in pos:
        continue
    x0, y0 = pos[src]
    x1, y1 = pos[tgt]
    col = edge_color(dq_c)
    lw  = edge_lw(dq_c)
    alp = edge_alpha(dq_c)
    ls  = edge_style(status)

    # Shorten edge so arrowhead starts at node boundary
    dx, dy = x1 - x0, y1 - y0
    dist = np.sqrt(dx**2 + dy**2)
    if dist < 0.01:
        continue
    dx_n, dy_n = dx / dist, dy / dist
    xs = x0 + dx_n * NODE_R
    ys = y0 + dy_n * NODE_R
    xe = x1 - dx_n * NODE_R * 1.4
    ye = y1 - dy_n * NODE_R * 1.4

    ax.annotate('', xy=(xe, ye), xytext=(xs, ys),
                arrowprops=dict(
                    arrowstyle='->', color=col,
                    lw=lw, alpha=alp,
                    linestyle=ls,
                    connectionstyle='arc3,rad=0.05',
                ))

    # Edge label: |ΔQ| value for top edges
    if abs(dq_c) >= 0.04:
        mx = (xs + xe) / 2 + 0.02 * (-dy_n)
        my = (ys + ye) / 2 + 0.02 * dx_n
        ax.text(mx, my, f'{abs(dq_c):.3f}', fontsize=5.5,
                color=col, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.7))

    # Funatlas badge
    if status == 'confirmed':
        mx = (xs + xe) / 2 - 0.025 * (-dy_n)
        my = (ys + ye) / 2 - 0.025 * dx_n
        ax.text(mx, my, '✓', fontsize=7, color='#2CA02C', ha='center', va='center',
                fontweight='bold')
    elif status == 'untested':
        mx = (xs + xe) / 2 - 0.025 * (-dy_n)
        my = (ys + ye) / 2 - 0.025 * dx_n
        ax.text(mx, my, '?', fontsize=7, color='#D62728', ha='center', va='center',
                fontweight='bold')

# Draw nodes
for neuron, (nx, ny) in pos.items():
    if neuron not in node_info:
        continue
    info = node_info[neuron]
    circle = plt.Circle((nx, ny), NODE_R, color=info['color'],
                         ec='#555555', lw=0.8, zorder=5)
    ax.add_patch(circle)
    # Label below node
    lines = info['label'].split('\n')
    for k, line in enumerate(lines):
        ax.text(nx, ny - NODE_R - 0.025 - k * 0.032, line,
                ha='center', va='top', fontsize=7,
                fontweight='bold' if k == 0 else 'normal',
                color='#222222', zorder=6)

# ── Legend ────────────────────────────────────────────────────────────────────
leg_x, leg_y0 = 0.02, 0.16
ax.add_patch(plt.Circle((leg_x + 0.015, leg_y0), 0.012, color=DWELLING, ec='#555555', lw=0.5))
ax.text(leg_x + 0.035, leg_y0, 'ΔQ < 0  (dwelling-dominant)', va='center', fontsize=7.5)
ax.add_patch(plt.Circle((leg_x + 0.015, leg_y0 - 0.045), 0.012, color=ROAMING, ec='#555555', lw=0.5))
ax.text(leg_x + 0.035, leg_y0 - 0.045, 'ΔQ > 0  (roaming-dominant)', va='center', fontsize=7.5)

# Line styles
ax.plot([leg_x, leg_x + 0.035], [leg_y0 - 0.09, leg_y0 - 0.09],
        color='#555555', lw=2, ls='-')
ax.text(leg_x + 0.045, leg_y0 - 0.09, 'Tested in funatlas', va='center', fontsize=7.5)
ax.plot([leg_x, leg_x + 0.035], [leg_y0 - 0.125, leg_y0 - 0.125],
        color='#555555', lw=2, ls='--')
ax.text(leg_x + 0.045, leg_y0 - 0.125, 'Untested (occ=0 in funatlas)', va='center', fontsize=7.5)

# Badges
ax.text(leg_x + 0.01, leg_y0 - 0.16, '✓', fontsize=9, color='#2CA02C', fontweight='bold')
ax.text(leg_x + 0.035, leg_y0 - 0.16, 'wt-significant in funatlas', va='center', fontsize=7.5)
ax.text(leg_x + 0.01, leg_y0 - 0.195, '?', fontsize=9, color='#D62728', fontweight='bold')
ax.text(leg_x + 0.035, leg_y0 - 0.195, 'Never measured (occ=0)', va='center', fontsize=7.5)

# Line width legend
for dq_ex, label in [(0.12, '|ΔQ|=0.12'), (0.06, '0.06'), (0.02, '0.02')]:
    lw = edge_lw(dq_ex)
    # proxy
ax.text(0.01, 0.01,
        'Edge width ∝ |ΔQ_CePNEM|.  Source nodes (triangles in spec): ADEL, AVDL, RID, RMER.  '
        'Source+target (RMEL): dual role.  Target nodes: pdfr-1 expressing.',
        fontsize=6, color='#777777', transform=ax.transAxes, wrap=True)

ax.set_title('ADEL-centered PDF signaling network — dwelling-dominant conditional dependence',
             fontsize=10, pad=10)

plt.tight_layout()
plt.savefig(OUT / 'fig5_adel_pdf_network.pdf', bbox_inches='tight', dpi=300)
plt.savefig(OUT / 'fig5_adel_pdf_network.png', bbox_inches='tight', dpi=150)
plt.close()
print('Fig 5 saved.')
