"""
Animation 4 — From Precision to Current
matplotlib fallback render  (PHASE VIS-1B)
Storyboard: results/visualization/animation_DQ_current.md
Output:     results/visualization/dq_to_current_animation.mp4
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation, FFMpegWriter
import os, sys

# ── Render parameters ─────────────────────────────────────────────────────────
FPS   = 15
W, H  = 1280, 720
DPI   = 100

# ── Palette ───────────────────────────────────────────────────────────────────
BG     = '#0F0F14'
WHITE  = '#F0F0F0'
GRAY   = '#555566'
LGRAY  = '#888899'
ORANGE = '#E07B39'
TEAL   = '#2A9D8F'
PURPLE = '#8B5CF6'
BLUE   = '#3D5A99'
YELLOW = '#F5C518'

# ── Math helpers ──────────────────────────────────────────────────────────────
def sm(t):
    t = float(np.clip(t, 0, 1))
    return t * t * (3 - 2 * t)

def fr(f, f0, f1):
    return sm((f - f0) / max(1.0, f1 - f0))

def lerp(a, b, t):
    return a + (b - a) * np.clip(t, 0, 1)

def lerp_mat(A, B, t):
    return A + (B - A) * sm(np.clip(t, 0, 1))

def ell_pts(cov, sc=1.5, cx=0, cy=0, n=120):
    theta = np.linspace(0, 2 * np.pi, n)
    circle = np.array([np.cos(theta), np.sin(theta)])
    vals, vecs = np.linalg.eigh(cov)
    vals = np.maximum(vals, 1e-9)
    L = vecs @ np.diag(np.sqrt(vals)) * sc
    pts = L @ circle
    return pts[0] + cx, pts[1] + cy

# ── Scene boundary frames ─────────────────────────────────────────────────────
T = dict(title=0, s1=45, s2=345, s3=645, s4=870, s5=1200, end=1425)

# ── Pre-computed geometry ─────────────────────────────────────────────────────
rng = np.random.default_rng(42)

# Stationary covariance and precision
COV = np.array([[2.0, 1.2], [1.2, 1.0]])
PREC = np.linalg.inv(COV)
COV_TIGHT = np.array([[1.5, 1.35], [1.35, 1.25]])

# Pixel-space coordinate system
CX, CY, SC = 640, 370, 75   # main canvas

def to_px(x, y, cx=CX, cy=CY, sc=SC):
    return cx + x * sc, cy + y * sc

# Gaussian cloud
N_CLOUD = 170
CLOUD = rng.multivariate_normal([0, 0], COV, N_CLOUD)
CLOUD_PX = np.array([(CX + p[0] * SC, CY + p[1] * SC) for p in CLOUD])

# Pre-compute ellipse curves in pixel space
def px_ell(cov, cx=CX, cy=CY, sc=SC, scl=1.5, n=120):
    x, y = ell_pts(cov, sc=scl, cx=0, cy=0, n=n)
    return cx + x * sc, cy + y * sc

COV_EX, COV_EY   = px_ell(COV)
PREC_EX, PREC_EY = px_ell(PREC)

# Precision ellipse label positions
vals, vecs = np.linalg.eigh(PREC)
idx = vals.argsort()[::-1]
vals, vecs = vals[idx], vecs[:, idx]
STRONG = vecs[:, 0] * 1.5 * np.sqrt(vals[0]) * SC  # pixel offset
WEAK   = vecs[:, 1] * 1.5 * np.sqrt(vals[1]) * SC

# D shapes for Scene 2
D_ISO   = np.eye(2) * 0.35
D_ANISO = np.diag([0.12, 0.72])
D_CORR  = np.array([[0.45, 0.38], [0.38, 0.45]])
D_CASES = [D_ISO, D_ANISO, D_CORR]
D_LBLS  = [
    "D = I   (equal fluctuations in every direction)",
    "D diagonal, anisotropic   (x₂ fluctuates more)",
    "D off-diagonal   (x₁ and x₂ fluctuate together)"
]

KICK_POS = rng.multivariate_normal([0, 0], COV * 0.4, 7)
KICK_PX  = np.array([(CX + p[0] * SC, CY + p[1] * SC) for p in KICK_POS])

def kick_ell(D_mat, cpx, sc=28):
    t = np.linspace(0, 2 * np.pi, 36)
    circle = np.array([np.cos(t), np.sin(t)])
    vals, vecs = np.linalg.eigh(D_mat)
    vals = np.maximum(vals, 1e-9)
    L = vecs @ np.diag(np.sqrt(vals)) * sc
    pts = L @ circle
    return pts[0] + cpx[0], pts[1] + cpx[1]

# Scene 3: split screen
S3_LCX, S3_RCX, S3_CY = W // 4, 3 * W // 4, 370
S3_SC = 68

def s3_ell(cx):
    return px_ell(COV, cx=cx, cy=S3_CY, sc=S3_SC)

# Flow field for Scene 3 right panel
gx7, gy7 = np.meshgrid(np.linspace(-3, 3, 7), np.linspace(-3, 3, 7))
A_SK = np.array([[0.0, -0.65], [0.65, 0.0]])
gpos = np.stack([gx7.ravel(), gy7.ravel()], axis=1)
gflow = gpos @ A_SK.T
gspd  = np.sqrt((gflow ** 2).sum(1) + 0.01)
GU, GV = gflow[:, 0] / gspd, gflow[:, 1] / gspd
GPX = S3_RCX + gx7.ravel() * S3_SC
GPY = S3_CY  + gy7.ravel() * S3_SC

# Particle trajectories for Scene 3 (pre-computed)
N_PAR = 6
N_STEPS_S3 = 310

def sim_ou(n_steps, A_extra=None, seed=0):
    r2 = np.random.default_rng(seed)
    pos = r2.multivariate_normal([0, 0], COV * 0.15, N_PAR)
    traj = [pos.copy()]
    dt = 0.07
    for _ in range(n_steps):
        drift = -0.35 * pos
        if A_extra is not None:
            drift = drift + pos @ A_extra.T
        noise = r2.multivariate_normal([0, 0], np.eye(2) * 0.1, N_PAR)
        pos = pos + dt * drift + np.sqrt(dt) * noise
        traj.append(pos.copy())
    return np.array(traj)

TRAJ_EQ  = sim_ou(N_STEPS_S3, seed=0)
TRAJ_CIR = sim_ou(N_STEPS_S3, A_extra=A_SK, seed=1)

# Scene 4 panel geometry
S4_CY  = H // 2 + 15
S4_SC  = 58
S4_LCX = W // 4
S4_MCX = W // 2
S4_RCX = 3 * W // 4
BOX_HW, BOX_HH = 128, 120

def s4_ell(cov, cx, sc=S4_SC, scl=1.4):
    return px_ell(cov, cx=cx, cy=S4_CY, sc=sc, scl=scl)

S4_Q_EX,  S4_Q_EY  = s4_ell(COV, S4_LCX)
S4_QP_EX, S4_QP_EY = s4_ell(PREC, S4_LCX)

# Flow field for Scene 4 right panel (5×5 grid)
gx5, gy5 = np.meshgrid(np.linspace(-2.2, 2.2, 5), np.linspace(-2.2, 2.2, 5))
gpos5 = np.stack([gx5.ravel(), gy5.ravel()], axis=1)

# Scene 5 bar chart
NBAR = 10
BAR_LBLS  = ["URXL", "URYVL", "CEP", "IL1", "RID", "RMD", "RME", "AVJ", "AIZL", "AVJR"]
DELTA_D   = np.array([0.208, 0.149, 0.06, 0.04, 0.02, 0.01, -0.03, -0.10, -0.167, -0.150])
S5_BAR_SC = 220      # pixels per unit delta-D
S5_BAR_X0 = 22
S5_BAR_W  = (W // 4 - 40) / NBAR
S5_BAR_CY = H // 2 + 15

# Scene 5 Ω scatter
rng2 = np.random.default_rng(99)
dQ_v = rng2.standard_normal(70)
dO_v = 1.025 * dQ_v + rng2.standard_normal(70) * 0.002
S5_OMS_CX, S5_OMS_CY, S5_OMS_SC = 3 * W // 4, H // 2 + 15, 48
S5_dQ_PX = S5_OMS_CX + dQ_v * S5_OMS_SC
S5_dO_PY = S5_OMS_CY + dO_v * S5_OMS_SC
lim_sc = max(abs(dQ_v).max(), abs(dO_v).max()) * S5_OMS_SC * 1.15

# ── Figure + axes ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
ax  = fig.add_axes([0, 0, 1, 1], facecolor=BG)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis('off')
fig.subplots_adjust(0, 0, 1, 1)

# ── Create all artists ────────────────────────────────────────────────────────

def txt(x, y, s, color=WHITE, size=14, ha='center', va='center',
        bold=False, italic=False, alpha=0):
    fw = 'bold' if bold else 'normal'
    fs = 'italic' if italic else 'normal'
    return ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va,
                   fontweight=fw, fontstyle=fs, alpha=alpha)

def line(color=WHITE, lw=1.5, ls='-', alpha=0, zorder=2):
    return ax.plot([], [], color=color, lw=lw, ls=ls, alpha=alpha, zorder=zorder)[0]

def scat(color=BLUE, s=8, alpha=0, zorder=3):
    return ax.scatter([], [], s=s, color=color, alpha=alpha, zorder=zorder)

# Title
T_title = txt(W/2, H/2 + 45, "From Precision to Current",
              size=36, bold=True)
T_subt  = txt(W/2, H/2 - 18, "D,   Q,   and Ω   in a stochastic system",
              color=ORANGE, size=17)
T_scene = txt(32, H - 32, "", color=LGRAY, size=10, ha='left', va='top')
T_cue   = txt(W/2, 40, "", color=WHITE, size=14, italic=True)

# Scene 1
S1_ax_h  = line(color=WHITE, lw=0.8)
S1_ax_v  = line(color=WHITE, lw=0.8)
S1_ax_lx = txt(0, 0, "x₁", color=LGRAY, size=12, ha='left')
S1_ax_ly = txt(0, 0, "x₂", color=LGRAY, size=12, ha='left')
S1_cloud = scat(color=BLUE, s=6)
S1_cov   = line(color=LGRAY, lw=1.5, ls='--')
S1_prec  = line(color=ORANGE, lw=2.4, zorder=4)
S1_pl_st = txt(0, 0, "large Q\nstrong constraint", color=ORANGE, size=9)
S1_pl_wk = txt(0, 0, "small Q\nalmost free",        color=TEAL,   size=9)
S1_head  = txt(W/2, H - 62, "Scene 1 — What Q sees",
               color=WHITE, size=17, bold=True)

# Scene 2
S2_ghost = line(color=LGRAY, lw=1.3, ls='-')
S2_head  = txt(W/2, H - 62, "Scene 2 — What D sees",
               color=WHITE, size=17, bold=True)
S2_dlbl  = txt(W/2, 115, "", color=TEAL, size=13)
S2_summ  = txt(W/2, H/2 + 160, "", color=WHITE, size=14, bold=True)
N_KICK   = len(KICK_PX)
S2_kicks = [line(color=TEAL, lw=1.6, zorder=3) for _ in range(N_KICK)]

# Scene 3
S3_div    = line(color=WHITE, lw=0.8)
S3_ellL   = line(color=LGRAY, lw=1.6, zorder=2)
S3_ellR   = line(color=LGRAY, lw=1.6, zorder=2)
S3_head   = txt(W/2, H - 62, "Scene 3 — What Ω sees",
                color=WHITE, size=17, bold=True)
S3_lblL   = txt(S3_LCX, 115, "Detailed balance\nΩ = 0",
                color=WHITE, size=12)
S3_lblR   = txt(S3_RCX, 115, "Circulating current\nΩ ≠ 0",
                color=PURPLE, size=12)
S3_ann1   = txt(W/2, 188, "Same Q  →  same density", color=ORANGE, size=13, bold=True)
S3_ann2   = txt(W/2, 158, "Different Ω  →  different dynamics", color=PURPLE, size=13)
S3_eq_scats = [line(color=BLUE,   lw=1.5, zorder=4) for _ in range(N_PAR)]
S3_cir_scs  = [line(color=PURPLE, lw=1.5, zorder=4) for _ in range(N_PAR)]
S3_flow_q   = ax.quiver(GPX, GPY, GU, GV,
                         color=PURPLE, alpha=0, scale=24,
                         width=0.003, headwidth=4, zorder=3)

# Scene 4
S4_head    = txt(W/2, H - 62, "Scene 4 — Ω = DQ + A",
                 color=WHITE, size=17, bold=True)
S4_eq_lbl  = txt(W/2, H - 100, "Ω  =  DQ + A", color=WHITE, size=18, bold=True)
S4_lbl_q   = txt(S4_LCX, H - 130, "Q", color=ORANGE, size=24, bold=True)
S4_lbl_d   = txt(S4_MCX,  H - 130, "D", color=TEAL,   size=24, bold=True)
S4_lbl_o   = txt(S4_RCX,  H - 130, "Ω", color=PURPLE, size=24, bold=True)
S4_times   = txt(S4_LCX + BOX_HW + 18, S4_CY, "×", color=LGRAY, size=26)
S4_equals  = txt(S4_MCX + BOX_HW + 18, S4_CY, "=", color=LGRAY, size=26)

S4_q_ell   = line(color=ORANGE, lw=2.4, zorder=4)
S4_d_ell   = line(color=TEAL,   lw=2.4, zorder=4)
S4_o_ell   = line(color=PURPLE, lw=2.4, zorder=4)
S4_q_ref   = line(color=ORANGE, lw=1.2, ls='--', zorder=3)  # Q reference in Ω panel

S4_flow_q  = ax.quiver(np.zeros(25), np.zeros(25),
                        np.zeros(25), np.zeros(25),
                        color=PURPLE, alpha=0, scale=20,
                        width=0.003, headwidth=4, zorder=3)

S4_unif    = txt(S4_RCX, S4_CY - S4_SC * 1.9, "D ≈ I → Ω looks like Q",
                 color=LGRAY, size=11)
S4_nonunif = txt(S4_RCX, S4_CY - S4_SC * 1.9, "D non-uniform → Ω ≠ Q",
                 color=WHITE, size=11)

M_q = txt(W/2, 315, "Q  =  road map   (geometry of constraint)",    color=ORANGE, size=14)
M_d = txt(W/2, 270, "D  =  traffic volume   (fluctuation intensity)", color=TEAL,   size=14)
M_o = txt(W/2, 225, "Ω  =  traffic organization   (effective flow)",  color=PURPLE, size=14)

# Boxes for Scene 4 panels
def make_box(cx, col, hw=BOX_HW, hh=BOX_HH):
    rect = mpatches.FancyBboxPatch(
        (cx - hw, S4_CY - hh), 2*hw, 2*hh,
        boxstyle='round,pad=4', edgecolor=col, facecolor='none', lw=2, alpha=0)
    ax.add_patch(rect)
    return rect

S4_box_q = make_box(S4_LCX, ORANGE)
S4_box_d = make_box(S4_MCX,  TEAL)
S4_box_o = make_box(S4_RCX,  PURPLE)

# Scene 5
S5_head  = txt(W/2, H - 62, "Scene 5 — In C. elegans",
               color=WHITE, size=17, bold=True)
S5_hd_d  = txt(W//4,    H - 100, "D",  color=TEAL,   size=20, bold=True)
S5_hd_q  = txt(W//2,    H - 100, "Q",  color=ORANGE, size=20, bold=True)
S5_hd_o  = txt(3*W//4,  H - 100, "Ω",  color=PURPLE, size=20, bold=True)
S5_div1  = line(color=LGRAY, lw=0.6)
S5_div2  = line(color=LGRAY, lw=0.6)

S5_bars = [mpatches.Rectangle((0, 0), 1, 1, color=TEAL, alpha=0)
           for _ in range(NBAR)]
for b in S5_bars:
    ax.add_patch(b)

# S5 bar labels (shown at lf=75+)
S5_blbl = [txt(0, 0, BAR_LBLS[i], color=LGRAY, size=7) for i in range(NBAR)]

# S5 Q column: two nodes + edge
S5_q_node1 = plt.Circle((0, 0), 25, color=ORANGE, alpha=0, zorder=3)
S5_q_node2 = plt.Circle((0, 0), 25, color=ORANGE, alpha=0, zorder=3)
ax.add_patch(S5_q_node1)
ax.add_patch(S5_q_node2)
S5_q_edge  = line(color=ORANGE, lw=2, zorder=2)
S5_q_lbl1  = txt(0, 0, "DA_mech", color=ORANGE, size=9)
S5_q_lbl2  = txt(0, 0, "URY_URX", color=ORANGE, size=9)

# S5 Ω scatter
S5_o_pts  = scat(color=PURPLE, s=10, zorder=3)
S5_o_diag = line(color=LGRAY, lw=1.5, ls='--', zorder=2)
S5_o_rho  = txt(0, 0, "ρ = 0.9999", color=PURPLE, size=10)

# S5 Ω→Q arrow (two-segment line + head)
S5_arr_ln = line(color=PURPLE, lw=2.5, zorder=5)
S5_arr_hd = scat(color=PURPLE, s=120, zorder=5)

# S5 summary
S5_sum1 = txt(W/2, 175,
    "In this dataset, current does not add significant biological information",
    color=WHITE, size=12.5)
S5_sum2 = txt(W/2, 148,
    "beyond precision for the PDF-modulated case.",
    color=WHITE, size=12.5)
S5_sum3 = txt(W/2, 112,
    "Primary object:  ΔQ",
    color=YELLOW, size=15, bold=True)
S5_fine  = txt(W/2, 75,
    "Ω ≠ Q in general — only when D ≈ I after preprocessing (e.g. z-scoring)",
    color=LGRAY, size=9.5, italic=True)

# ── Helper: set all scene-specific artists invisible ─────────────────────────
ALL_S1 = [S1_ax_h, S1_ax_v, S1_ax_lx, S1_ax_ly, S1_cloud,
          S1_cov, S1_prec, S1_pl_st, S1_pl_wk, S1_head]
ALL_S2 = [S2_ghost, S2_head, S2_dlbl, S2_summ] + S2_kicks
ALL_S3 = ([S3_div, S3_ellL, S3_ellR, S3_head, S3_lblL, S3_lblR,
           S3_ann1, S3_ann2, S3_flow_q] +
          S3_eq_scats + S3_cir_scs)
ALL_S4 = ([S4_head, S4_eq_lbl, S4_lbl_q, S4_lbl_d, S4_lbl_o,
           S4_times, S4_equals, S4_q_ell, S4_d_ell, S4_o_ell,
           S4_q_ref, S4_flow_q, S4_unif, S4_nonunif,
           M_q, M_d, M_o, S4_box_q, S4_box_d, S4_box_o])
ALL_S5 = ([S5_head, S5_hd_d, S5_hd_q, S5_hd_o, S5_div1, S5_div2,
           S5_q_edge, S5_q_lbl1, S5_q_lbl2, S5_q_node1, S5_q_node2,
           S5_o_pts, S5_o_diag, S5_o_rho,
           S5_arr_ln, S5_arr_hd,
           S5_sum1, S5_sum2, S5_sum3, S5_fine] +
          S5_bars + S5_blbl)

ALL_SCENE_ARTISTS = ALL_S1 + ALL_S2 + ALL_S3 + ALL_S4 + ALL_S5

def fade_group(grp, alpha):
    for a in grp:
        a.set_alpha(alpha)


# ── Scene update functions ────────────────────────────────────────────────────

def upd_title(f):
    T_title.set_alpha(fr(f, 6, 30))
    T_subt.set_alpha(fr(f, 18, 44))


def upd_s1(lf):
    # lf in [0, 299]
    T_scene.set_text("1  ·  Q — geometry")
    T_scene.set_alpha(0.6)
    S1_head.set_alpha(fr(lf, 0, 20))

    # Axes
    a_ax = fr(lf, 0, 28) * 0.28
    S1_ax_h.set_data([to_px(-4.5, 0)[0], to_px(4.5, 0)[0]], [CY, CY])
    S1_ax_h.set_alpha(a_ax)
    S1_ax_v.set_data([CX, CX], [to_px(0, -3.8)[1], to_px(0, 3.8)[1]])
    S1_ax_v.set_alpha(a_ax)
    S1_ax_lx.set_position((to_px(4.7, 0)[0], CY - 16))
    S1_ax_lx.set_alpha(a_ax * 2)
    S1_ax_ly.set_position((CX + 10, to_px(0, 3.8)[1]))
    S1_ax_ly.set_alpha(a_ax * 2)

    # Cloud
    n_c = int(lerp(0, N_CLOUD, fr(lf, 18, 88)))
    if n_c > 0:
        S1_cloud.set_offsets(CLOUD_PX[:n_c])
        S1_cloud.set_alpha(0.33)

    # Covariance ellipse
    cf = fr(lf, 78, 148)
    nc = max(2, int(cf * len(COV_EX)))
    S1_cov.set_data(COV_EX[:nc], COV_EY[:nc])
    S1_cov.set_alpha(min(1.0, cf * 1.8) * 0.65)

    # Precision ellipse
    pf = fr(lf, 140, 215)
    np_ = max(2, int(pf * len(PREC_EX)))

    # Tightening: use linear interp of covariance matrix
    tight_t = sm(np.clip((lf - 228) / 32, 0, 1)) * np.sin(np.pi * np.clip((lf - 228) / 60, 0, 1))
    if lf > 228:
        cov_i = lerp_mat(COV, COV_TIGHT, tight_t)
        prec_i = np.linalg.inv(cov_i + np.eye(2) * 0.002)
        epx, epy = px_ell(prec_i)
        S1_prec.set_data(epx, epy)
    else:
        S1_prec.set_data(PREC_EX[:np_], PREC_EY[:np_])
    S1_prec.set_alpha(min(1.0, pf * 1.8))

    # Labels
    la = fr(lf, 205, 230)
    S1_pl_st.set_position((CX + STRONG[0] + 32 * np.sign(STRONG[0]),
                            CY + STRONG[1] + 26 * np.sign(STRONG[1]) + 10))
    S1_pl_st.set_alpha(la)
    S1_pl_wk.set_position((CX + WEAK[0] + 30 * np.sign(WEAK[0]),
                            CY + WEAK[1] + 26 * np.sign(WEAK[1]) + 10))
    S1_pl_wk.set_alpha(la)

    # Text cues
    if lf < 80:
        T_cue.set_text("States of a 2D stochastic system")
        T_cue.set_alpha(fr(lf, 20, 40) * 0.75)
    elif lf < 145:
        T_cue.set_text("Covariance — where states scatter")
        T_cue.set_alpha(fr(lf, 82, 100) * (1 - fr(lf, 135, 148)) * 0.75)
    elif lf < 240:
        T_cue.set_text("Precision (Q = Σ⁻¹) — which directions are constrained")
        T_cue.set_alpha(fr(lf, 143, 163) * (1 - fr(lf, 228, 243)) * 0.75)
    else:
        T_cue.set_text("Q tells us how the stationary density is shaped")
        T_cue.set_alpha(fr(lf, 243, 262) * 0.85)

    # Fade out
    if lf > 278:
        fo = 1 - fr(lf, 278, 299)
        for a in [S1_cloud, S1_cov, S1_prec, S1_ax_h, S1_ax_v,
                  S1_pl_st, S1_pl_wk, S1_head]:
            a.set_alpha((a.get_alpha() or 0) * fo)
        T_cue.set_alpha((T_cue.get_alpha() or 0) * fo)
        T_scene.set_alpha(0.6 * fo)


def upd_s2(lf):
    T_scene.set_text("2  ·  D — fluctuation input")
    T_scene.set_alpha(0.6)
    S2_head.set_alpha(fr(lf, 0, 20))

    # Ghost stationary ellipse
    S2_ghost.set_data(COV_EX, COV_EY)
    S2_ghost.set_alpha(fr(lf, 0, 18) * 0.28)

    # Determine which case
    if lf < 98:
        d_idx = 0; cs, ce = 12, 85
    elif lf < 198:
        d_idx = 1; cs, ce = 108, 185
    else:
        d_idx = 2; cs, ce = 208, 282

    D_cur = D_CASES[d_idx]
    ca = fr(lf, cs, cs + 18) * (1 - fr(lf, ce - 8, ce))

    for i, kp in enumerate(KICK_PX):
        kx, ky = kick_ell(D_cur, kp, sc=26)
        S2_kicks[i].set_data(kx, ky)
        S2_kicks[i].set_alpha(ca * 0.72)

    # Label
    S2_dlbl.set_text(D_LBLS[d_idx])
    S2_dlbl.set_alpha(ca * 0.88)

    # Transition arrows (brief text between cases)
    if 92 <= lf <= 110 or 192 <= lf <= 210:
        S2_summ.set_text("↓   D changes   ↓")
        S2_summ.set_alpha(fr(lf % 100, 92 % 100, 100) * 0.6
                          if lf < 150 else fr(lf, 192, 205) * 0.6)
    else:
        S2_summ.set_alpha(0)

    # Text cue
    T_cue.set_text(D_LBLS[d_idx])
    T_cue.set_alpha(ca * 0.78)

    if lf > 283:
        T_cue.set_text("D tells us where new fluctuations enter")
        T_cue.set_alpha(fr(lf, 283, 299) * 0.88)
        S2_dlbl.set_text("D changed — stationary distribution did not")
        S2_dlbl.set_color(WHITE)
        S2_dlbl.set_alpha(fr(lf, 283, 299) * 0.7)


def upd_s3(lf):
    T_scene.set_text("3  ·  Ω — probability current")
    T_scene.set_alpha(0.6)
    S3_head.set_alpha(fr(lf, 0, 20))

    # Divider
    S3_div.set_data([W/2, W/2], [78, H - 80])
    S3_div.set_alpha(fr(lf, 5, 25) * 0.28)

    # Density ellipses
    el_a = fr(lf, 5, 30) * 0.55
    lx, ly = s3_ell(S3_LCX);  S3_ellL.set_data(lx, ly); S3_ellL.set_alpha(el_a)
    rx, ry = s3_ell(S3_RCX);  S3_ellR.set_data(rx, ry); S3_ellR.set_alpha(el_a)

    # Panel labels
    S3_lblL.set_alpha(fr(lf, 12, 35))
    S3_lblR.set_alpha(fr(lf, 12, 35))

    # Particle frame index
    par_a = fr(lf, 28, 55)
    pf = min(max(0, lf - 28), N_STEPS_S3 - 1)
    trail = 12

    for i in range(N_PAR):
        # Left: equilibrium
        t0e = max(0, pf - trail)
        trx = S3_LCX + TRAJ_EQ[t0e:pf+1, i, 0] * S3_SC
        try_ = S3_CY  + TRAJ_EQ[t0e:pf+1, i, 1] * S3_SC
        S3_eq_scats[i].set_data(trx, try_)
        S3_eq_scats[i].set_alpha(par_a * 0.55)

        # Right: circulating
        t0c = max(0, pf - trail)
        trxc = S3_RCX + TRAJ_CIR[t0c:pf+1, i, 0] * S3_SC
        tryc = S3_CY  + TRAJ_CIR[t0c:pf+1, i, 1] * S3_SC
        S3_cir_scs[i].set_data(trxc, tryc)
        S3_cir_scs[i].set_alpha(par_a * 0.6)

    # Flow arrows
    flow_a = fr(lf, 35, 60) * (1 - fr(lf, 148, 162)) * 0.48
    S3_flow_q.set_offsets(np.column_stack([GPX, GPY]))
    S3_flow_q.set_UVC(GU, GV)
    S3_flow_q.set_alpha(flow_a)

    # Annotations
    if lf > 132:
        a = fr(lf, 132, 155)
        S3_ann1.set_alpha(a)
        S3_ann2.set_alpha(a)

    # Cue text
    if lf < 30:
        T_cue.set_text("Same stationary distribution — same Q")
        T_cue.set_alpha(fr(lf, 6, 22) * 0.78)
    elif lf < 135:
        T_cue.set_alpha(0)
    elif lf < 195:
        T_cue.set_text("Identical Q — identical where.   Different Ω — different how.")
        T_cue.set_alpha(fr(lf, 135, 155) * (1 - fr(lf, 185, 198)) * 0.8)
    else:
        T_cue.set_text("Ω describes movement through state space")
        T_cue.set_alpha(fr(lf, 196, 216) * 0.88)


def upd_s4(lf):
    T_scene.set_text("4  ·  Ω = DQ + A")
    T_scene.set_alpha(0.6)
    S4_head.set_alpha(fr(lf, 0, 20))
    S4_eq_lbl.set_alpha(fr(lf, 8, 32))

    # Boxes
    ba = fr(lf, 0, 22) * 0.72
    for box in [S4_box_q, S4_box_d, S4_box_o]:
        box.set_alpha(ba)

    # Labels
    la = fr(lf, 0, 22)
    S4_lbl_q.set_alpha(la); S4_lbl_d.set_alpha(la); S4_lbl_o.set_alpha(la)
    S4_times.set_alpha(la * 0.6); S4_equals.set_alpha(la * 0.6)

    # Q ellipse (left panel)
    qf = fr(lf, 18, 62)
    nq = max(2, int(qf * len(S4_Q_EX)))
    S4_q_ell.set_data(S4_Q_EX[:nq], S4_Q_EY[:nq])
    S4_q_ell.set_alpha(qf)

    # D morphs: iso (lf<165) → aniso (lf≥215)
    D_t = fr(lf, 165, 218)
    D4 = lerp_mat(D_ISO, D_ANISO, D_t)
    d_pts = px_ell(D4, cx=S4_MCX, cy=S4_CY, sc=S4_SC * 1.8, scl=1.2)
    S4_d_ell.set_data(d_pts[0], d_pts[1])
    S4_d_ell.set_alpha(fr(lf, 38, 70))

    # Ω ellipse (right panel) follows D@COV
    Om_cov = D4 @ COV + np.eye(2) * 0.01
    o_pts = px_ell(Om_cov, cx=S4_RCX, cy=S4_CY, sc=S4_SC, scl=1.4)
    S4_o_ell.set_data(o_pts[0], o_pts[1])
    S4_o_ell.set_alpha(fr(lf, 58, 88))

    # Q reference dashed in Ω panel (to show rotation)
    ref_a = fr(lf, 165, 210) * (1 - fr(lf, 310, 325))
    q_ref_pts = px_ell(COV, cx=S4_RCX, cy=S4_CY, sc=S4_SC, scl=1.4)
    S4_q_ref.set_data(q_ref_pts[0], q_ref_pts[1])
    S4_q_ref.set_alpha(ref_a * 0.45)

    # Flow arrows in Ω panel
    gflow5 = gpos5 @ (D4 @ PREC).T
    gspd5 = np.sqrt((gflow5**2).sum(1) + 0.01)
    gu5, gv5 = gflow5[:, 0] / gspd5, gflow5[:, 1] / gspd5
    gpx5 = S4_RCX + gx5.ravel() * S4_SC
    gpy5 = S4_CY  + gy5.ravel() * S4_SC
    S4_flow_q.set_offsets(np.column_stack([gpx5, gpy5]))
    S4_flow_q.set_UVC(gu5, gv5)
    S4_flow_q.set_alpha(fr(lf, 68, 95) * 0.55)

    # Cue text
    if lf < 62:
        T_cue.set_text("Ω = DQ + A")
        T_cue.set_alpha(fr(lf, 22, 42) * 0.82)
        S4_unif.set_alpha(0); S4_nonunif.set_alpha(0)
    elif lf < 165:
        T_cue.set_text("D = I  →  Ω looks like a rescaled Q")
        T_cue.set_alpha(fr(lf, 62, 82) * (1 - fr(lf, 155, 168)) * 0.82)
        S4_unif.set_alpha(fr(lf, 75, 95) * (1 - fr(lf, 158, 170)))
        S4_nonunif.set_alpha(0)
    elif lf < 285:
        T_cue.set_text("D non-uniform  →  Ω rotates away from Q")
        T_cue.set_alpha(fr(lf, 168, 188) * (1 - fr(lf, 275, 288)) * 0.82)
        S4_unif.set_alpha(0)
        S4_nonunif.set_alpha(fr(lf, 175, 200) * (1 - fr(lf, 275, 288)))
    else:
        T_cue.set_text("Same road map. Different traffic. Different flow.")
        T_cue.set_alpha(fr(lf, 288, 305) * 0.82)
        S4_unif.set_alpha(0); S4_nonunif.set_alpha(0)

    # Metaphor text
    M_q.set_alpha(fr(lf, 295, 318))
    M_d.set_alpha(fr(lf, 305, 325))
    M_o.set_alpha(fr(lf, 315, 329))


def upd_s5(lf):
    T_scene.set_text("5  ·  C. elegans")
    T_scene.set_alpha(0.6)
    S5_head.set_alpha(fr(lf, 0, 22))

    # Column headers + dividers
    ha = fr(lf, 8, 28)
    S5_hd_d.set_alpha(ha); S5_hd_q.set_alpha(ha); S5_hd_o.set_alpha(ha)
    S5_div1.set_data([W//4 + W//8, W//4 + W//8], [75, H - 80])
    S5_div2.set_data([W//2 + W//8, W//2 + W//8], [75, H - 80])
    S5_div1.set_alpha(fr(lf, 8, 28) * 0.22)
    S5_div2.set_alpha(fr(lf, 8, 28) * 0.22)

    # ── D bars ──────────────────────────────────────────────────────────────
    d_morph = sm(np.clip((lf - 22) / 42, 0, 1))
    d_col_a = fr(lf, 22, 48) * (1 - fr(lf, 72, 88))
    for i in range(NBAR):
        dv = DELTA_D[i] * d_morph
        bx = S5_BAR_X0 + i * S5_BAR_W
        by = S5_BAR_CY if dv >= 0 else S5_BAR_CY + dv * S5_BAR_SC
        bh = abs(dv) * S5_BAR_SC
        S5_bars[i].set_bounds(bx, by, S5_BAR_W * 0.78, max(bh, 1))
        S5_bars[i].set_facecolor(TEAL if DELTA_D[i] > 0 else ORANGE)
        S5_bars[i].set_alpha(d_col_a * 0.82)
        lbl_y = S5_BAR_CY - 14 if dv >= 0 else S5_BAR_CY + dv * S5_BAR_SC - 14
        S5_blbl[i].set_position((bx + S5_BAR_W * 0.35, lbl_y))
        S5_blbl[i].set_alpha(fr(lf, 55, 75) * (1 - fr(lf, 72, 85)))

    # Faded bars persisting after D phase
    if lf >= 88:
        for b in S5_bars:
            b.set_alpha(0.22)
        for bl in S5_blbl:
            bl.set_alpha(0)

    # ── Q column ──────────────────────────────────────────────────────────
    q_a = fr(lf, 82, 108) * (1 - fr(lf, 138, 152))

    S5_q_node1.center = (W//2 - 52, H//2 + 22)
    S5_q_node2.center = (W//2 + 52, H//2 + 22)
    S5_q_node1.set_alpha(q_a * 0.38)
    S5_q_node2.set_alpha(q_a * 0.38)

    edge_lw = lerp(1.5, 5.5, sm(np.clip((lf - 88) / 38, 0, 1)))
    S5_q_edge.set_data([W//2 - 27, W//2 + 27], [H//2 + 22, H//2 + 22])
    S5_q_edge.set_linewidth(edge_lw)
    S5_q_edge.set_alpha(q_a)
    S5_q_lbl1.set_position((W//2 - 52, H//2 + 22)); S5_q_lbl1.set_alpha(q_a)
    S5_q_lbl2.set_position((W//2 + 52, H//2 + 22)); S5_q_lbl2.set_alpha(q_a)

    # Faded Q persisting
    if lf >= 152:
        S5_q_node1.set_alpha(0.18); S5_q_node2.set_alpha(0.18)
        S5_q_edge.set_alpha(0.28); S5_q_lbl1.set_alpha(0.18); S5_q_lbl2.set_alpha(0.18)

    # ── Ω column ──────────────────────────────────────────────────────────
    o_a = fr(lf, 142, 165) * (1 - fr(lf, 175, 190))
    n_show = int(lerp(0, len(S5_dQ_PX), fr(lf, 142, 170)))
    if n_show > 0:
        S5_o_pts.set_offsets(np.column_stack([S5_dQ_PX[:n_show],
                                               S5_dO_PY[:n_show]]))
        S5_o_pts.set_alpha(o_a * 0.72)
    S5_o_diag.set_data([S5_OMS_CX - lim_sc, S5_OMS_CX + lim_sc],
                        [S5_OMS_CY - lim_sc, S5_OMS_CY + lim_sc])
    S5_o_diag.set_alpha(o_a * 0.5)
    S5_o_rho.set_position((S5_OMS_CX, S5_OMS_CY + lim_sc + 18))
    S5_o_rho.set_alpha(fr(lf, 155, 172) * (1 - fr(lf, 175, 190)))

    # Faded scatter persisting
    if lf >= 190:
        S5_o_pts.set_alpha(0.28)
        S5_o_diag.set_alpha(0.22)

    # ── Ω→Q convergence arrow ─────────────────────────────────────────────
    arr_a = fr(lf, 182, 198)
    ax1 = 3 * W // 4 - 30
    ax2 = W // 2 + 35
    ay  = H // 2 + 22
    # Draw as a line + arrowhead marker
    S5_arr_ln.set_data([ax1, ax2], [ay, ay])
    S5_arr_ln.set_alpha(arr_a)
    S5_arr_hd.set_offsets([[ax2, ay]])
    S5_arr_hd.set_alpha(arr_a)

    # ── Summary text ──────────────────────────────────────────────────────
    S5_sum1.set_alpha(fr(lf, 194, 210))
    S5_sum2.set_alpha(fr(lf, 200, 215))
    S5_sum3.set_alpha(fr(lf, 208, 222))
    S5_fine.set_alpha(fr(lf, 214, 224) * 0.72)

    # ── Cue text ─────────────────────────────────────────────────────────
    if lf < 88:
        T_cue.set_text("D reorganizes: aerotaxis sensors ↑ roaming,  olfactory/reversal ↑ dwelling")
        T_cue.set_alpha(fr(lf, 28, 48) * (1 - fr(lf, 76, 90)) * 0.78)
    elif lf < 152:
        T_cue.set_text("Q reorganizes: DA_mech ↔ URY_URX conditional coupling changes between states")
        T_cue.set_alpha(fr(lf, 88, 108) * (1 - fr(lf, 140, 155)) * 0.78)
    elif lf < 192:
        T_cue.set_text("ΔΩ ≈ ΔQ  (ρ = 0.9999)  —  z-scoring flattens D to near-uniform")
        T_cue.set_alpha(fr(lf, 145, 162) * (1 - fr(lf, 182, 195)) * 0.78)
    else:
        T_cue.set_alpha(0)


# ── Master update ─────────────────────────────────────────────────────────────
_prev_scene = [None]

def update(f):
    # Determine scene, zero out title artists between scenes
    scene = ('title' if f < T['s1'] else
             's1'    if f < T['s2'] else
             's2'    if f < T['s3'] else
             's3'    if f < T['s4'] else
             's4'    if f < T['s5'] else 's5')

    if scene != _prev_scene[0]:
        # On scene transition: hide title card
        if _prev_scene[0] == 'title':
            T_title.set_alpha(0)
            T_subt.set_alpha(0)
        _prev_scene[0] = scene

    if scene == 'title':
        upd_title(f)
    elif scene == 's1':
        upd_s1(f - T['s1'])
    elif scene == 's2':
        upd_s2(f - T['s2'])
    elif scene == 's3':
        upd_s3(f - T['s3'])
    elif scene == 's4':
        upd_s4(f - T['s4'])
    else:
        upd_s5(f - T['s5'])


# ── Render ────────────────────────────────────────────────────────────────────
def main():
    out_dir = os.path.join(os.path.dirname(__file__),
                           '../../results/visualization')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'dq_to_current_animation.mp4')

    ani = FuncAnimation(fig, update, frames=T['end'],
                        interval=1000 / FPS, blit=False)

    writer = FFMpegWriter(
        fps=FPS, codec='h264',
        extra_args=['-crf', '22', '-preset', 'fast', '-pix_fmt', 'yuv420p'])

    print(f"Rendering {T['end']} frames at {FPS} fps  →  {out_path}", flush=True)
    ani.save(out_path, writer=writer, dpi=DPI,
             progress_callback=lambda i, n: print(f"  {i}/{n}", end='\r', flush=True)
             if i % 50 == 0 else None)
    print(f"\nDone. Saved: {out_path}")

    # Remove placeholder if render succeeded
    ph = out_path + '.placeholder'
    if os.path.exists(ph):
        os.remove(ph)
        print("Removed placeholder file.")


if __name__ == '__main__':
    main()
