"""
PHASE VIS-1 — Figure Sketches
Generates explanatory figure sketches for D, Q, Omega, and current velocity.
Audience: neuroscientists, physicists, systems biologists.
Output: results/visualization/figure_sketches.pdf
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import multivariate_normal

rng = np.random.default_rng(42)

# ── palette ──────────────────────────────────────────────────────────────────
C_DENSITY    = "#CCCCCC"
C_COV        = "#888888"
C_PRECISION  = "#E07B39"
C_DIFFUSION  = "#2A9D8F"
C_CURRENT    = "#6A0DAD"
C_TRAJ       = "#1A237E"
C_HIGHLIGHT  = "#C0392B"
C_TEXT       = "#222222"
C_FAINT      = "#DDDDDD"

ALPHA_CLOUD  = 0.25
ALPHA_ELLIPSE= 0.85


def make_ellipse(cov, center=(0, 0), n_std=1.5, **kwargs):
    """Return a matplotlib Ellipse patch for a covariance matrix."""
    from matplotlib.patches import Ellipse
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * n_std * np.sqrt(vals)
    return Ellipse(xy=center, width=width, height=height, angle=angle, **kwargs)


def sample_gaussian(cov, n=400, seed=0):
    rng2 = np.random.default_rng(seed)
    return rng2.multivariate_normal([0, 0], cov, n)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1: "What Q Sees"
# ─────────────────────────────────────────────────────────────────────────────
def fig1_what_q_sees():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Figure 1 — What Q Sees", fontsize=14, fontweight="bold", y=1.01)

    cov = np.array([[2.0, 1.2], [1.2, 1.0]])
    Q   = np.linalg.inv(cov)
    pts = sample_gaussian(cov, 350)

    for ax, title in zip(axes, ["Covariance: where states are",
                                  "Precision (Q): which relationships are enforced"]):
        ax.scatter(pts[:, 0], pts[:, 1], s=8, alpha=ALPHA_CLOUD, color=C_TRAJ, zorder=1)
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.set_xlabel("x₁", fontsize=10); ax.set_ylabel("x₂", fontsize=10)
        ax.axhline(0, color=C_FAINT, lw=0.5); ax.axvline(0, color=C_FAINT, lw=0.5)
        ax.set_title(title, fontsize=10, pad=8)

    # Left panel: covariance ellipse
    ax = axes[0]
    ell_cov = make_ellipse(cov, n_std=1.5,
                           edgecolor=C_COV, facecolor="none", linewidth=2,
                           linestyle="--", label="1.5σ covariance", zorder=3)
    ax.add_patch(ell_cov)
    ax.annotate("Spread — high variance\nalong this direction",
                xy=(1.8, 1.2), xytext=(2.5, 2.8),
                arrowprops=dict(arrowstyle="->", color=C_COV), color=C_COV, fontsize=8)
    ax.legend(handles=[ell_cov], loc="lower right", fontsize=8)

    # Right panel: precision ellipse (inverted shape)
    ax = axes[1]
    ell_cov2 = make_ellipse(cov, n_std=1.5,
                            edgecolor=C_FAINT, facecolor="none", linewidth=1,
                            linestyle="--", zorder=2)
    ax.add_patch(ell_cov2)

    ell_prec = make_ellipse(Q, n_std=1.2,
                            edgecolor=C_PRECISION, facecolor=C_PRECISION,
                            alpha=0.12, linewidth=2.5, zorder=3,
                            label="Precision ellipse (Q)")
    ax.add_patch(ell_prec)

    # Annotate axes of precision ellipse
    vals, vecs = np.linalg.eigh(Q)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]

    strong_dir = vecs[:, 0] * 1.2 * np.sqrt(vals[0])
    weak_dir   = vecs[:, 1] * 1.2 * np.sqrt(vals[1])

    ax.annotate("Large Q\nStrong constraint",
                xy=tuple(strong_dir), xytext=(strong_dir[0]+1.0, strong_dir[1]+1.2),
                arrowprops=dict(arrowstyle="->", color=C_PRECISION),
                color=C_PRECISION, fontsize=8, ha="center")
    ax.annotate("Small Q\nWeak constraint\n(almost free)",
                xy=tuple(weak_dir), xytext=(weak_dir[0]-2.0, weak_dir[1]+0.8),
                arrowprops=dict(arrowstyle="->", color=C_DIFFUSION),
                color=C_DIFFUSION, fontsize=8, ha="center")

    ax.legend(handles=[ell_prec], loc="lower right", fontsize=8)

    fig.text(0.5, -0.03,
             "Q is the inverse covariance. It measures which conditional relationships are enforced, not where states lie.\n"
             "A large off-diagonal Q[i,j] means i and j are directly coupled — even after removing shared influences.",
             ha="center", fontsize=8.5, color=C_TEXT, style="italic")

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2: "What D Sees"
# ─────────────────────────────────────────────────────────────────────────────
def fig2_what_d_sees():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    fig.suptitle("Figure 2 — What D Sees", fontsize=14, fontweight="bold", y=1.02)

    # Shared stationary distribution (same across all panels)
    cov_stat = np.array([[1.8, 0.9], [0.9, 0.8]])
    ell_kwargs = dict(edgecolor=C_DENSITY, facecolor=C_DENSITY, alpha=0.3, linewidth=1.5,
                      linestyle="-", zorder=1)

    subtitles = ["A.  Isotropic D\n(equal fluctuations)",
                 "B.  Anisotropic D\n(x₂ fluctuates more)",
                 "C.  Correlated D\n(x₁ and x₂ fluctuate together)"]
    D_mats = [
        np.array([[0.3, 0.0], [0.0, 0.3]]),
        np.array([[0.15, 0.0], [0.0, 0.7]]),
        np.array([[0.4, 0.35], [0.35, 0.4]]),
    ]
    D_labels = ["D = σ²·I", "D = diag(σ₁², σ₂²)\nσ₂ >> σ₁", "Off-diagonal D ≠ 0\ncorrelated noise"]

    rng3 = np.random.default_rng(1)
    n_starts = 8
    starts = rng3.multivariate_normal([0, 0], cov_stat * 0.1, n_starts)

    for ax, D, subtitle, dlabel in zip(axes, D_mats, subtitles, D_labels):
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.set_xlabel("x₁", fontsize=10); ax.set_ylabel("x₂", fontsize=10)
        ax.axhline(0, color=C_FAINT, lw=0.5); ax.axvline(0, color=C_FAINT, lw=0.5)
        ax.set_title(subtitle, fontsize=9.5, pad=6)

        # Stationary distribution (same in all three)
        ell_stat = make_ellipse(cov_stat, n_std=1.5, **ell_kwargs)
        ax.add_patch(ell_stat)
        ax.text(-3.5, 3.2, "stationary\ndistribution\n(same)", fontsize=7,
                color=C_COV, ha="left")

        # Diffusion blobs from starting points
        for s in starts:
            steps = rng3.multivariate_normal([0, 0], D * 4, 18)
            pts = s + steps
            ax.scatter(pts[:, 0], pts[:, 1], s=6, alpha=0.5, color=C_DIFFUSION, zorder=3)
            ax.plot([s[0]], [s[1]], "o", color=C_HIGHLIGHT, ms=4, zorder=4)

        # Diffusion ellipse overlay
        ell_D = make_ellipse(D * 5, n_std=1.5,
                             edgecolor=C_DIFFUSION, facecolor=C_DIFFUSION,
                             alpha=0.15, linewidth=2, zorder=2)
        ax.add_patch(ell_D)

        ax.text(0, -3.7, dlabel, ha="center", fontsize=8, color=C_DIFFUSION)

    # Bottom caption
    fig.text(0.5, -0.06,
             "D encodes where fluctuations enter. The stationary distribution (gray, same in all panels) is set by Q.\n"
             "D changes independently: the same stationary state can arise from isotropic, anisotropic, or correlated noise.",
             ha="center", fontsize=8.5, color=C_TEXT, style="italic")

    # Worm callback strip
    ax_worm = fig.add_axes([0.1, -0.22, 0.8, 0.1])
    neurons = ["URXL\n+0.21", "URYVL\n+0.15", "...", "AIZL\n−0.17", "AVJR\n−0.15"]
    colors  = [C_DIFFUSION, C_DIFFUSION, C_FAINT, C_HIGHLIGHT, C_HIGHLIGHT]
    heights = [0.21, 0.15, 0.0, -0.17, -0.15]
    x_pos   = [0, 1, 2, 3, 4]
    ax_worm.bar(x_pos, heights, color=colors, alpha=0.7, width=0.6)
    ax_worm.axhline(0, color="black", lw=0.8)
    ax_worm.set_xticks(x_pos); ax_worm.set_xticklabels(neurons, fontsize=7.5)
    ax_worm.set_ylabel("ΔD[i,i]", fontsize=8)
    ax_worm.set_title("Worm: D reorganizes between roaming (teal) and dwelling (red)  ·  ρ(D_roam, D_dwell) ≈ 0.14",
                      fontsize=8.5)
    ax_worm.spines["top"].set_visible(False)
    ax_worm.spines["right"].set_visible(False)

    fig.tight_layout(rect=[0, 0.12, 1, 1])
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3: "What Ω Sees"
# ─────────────────────────────────────────────────────────────────────────────
def _flow_field(x, y, omega):
    """Linear flow field from Omega matrix."""
    pos = np.stack([x, y], axis=-1)
    return (pos @ omega.T)


def fig3_what_omega_sees():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    fig.suptitle("Figure 3 — What Ω Sees", fontsize=14, fontweight="bold", y=1.02)

    cov_stat = np.array([[1.5, 0.5], [0.5, 0.8]])

    subtitles = ["A.  Detailed balance (Ω = 0)\nNo net circulation",
                 "B.  Circulating current (Ω ≠ 0)\nProbability flows clockwise",
                 "C.  Time-reversed (−Ω)\nSame density, opposite flow"]

    # Omega matrices for panels B and C
    omega_B = np.array([[0.0, -1.0], [1.0,  0.0]]) * 0.5
    omega_C = -omega_B

    omegas = [None, omega_B, omega_C]

    rng4 = np.random.default_rng(7)
    n_traj = 6
    traj_seeds = rng4.multivariate_normal([0, 0], cov_stat * 0.3, n_traj)

    for ax, Om, subtitle in zip(axes, omegas, subtitles):
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.set_xlabel("x₁", fontsize=10); ax.set_ylabel("x₂", fontsize=10)
        ax.axhline(0, color=C_FAINT, lw=0.5); ax.axvline(0, color=C_FAINT, lw=0.5)
        ax.set_title(subtitle, fontsize=9.5, pad=6)

        # Stationary distribution ellipse
        ell_stat = make_ellipse(cov_stat, n_std=1.5,
                                edgecolor=C_DENSITY, facecolor=C_DENSITY,
                                alpha=0.3, linewidth=1.5)
        ax.add_patch(ell_stat)

        if Om is not None:
            # Flow field arrows
            grid_x, grid_y = np.meshgrid(np.linspace(-3, 3, 9), np.linspace(-3, 3, 9))
            shape = grid_x.shape
            pos = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
            drift = pos @ Om.T
            U, V = drift[:, 0].reshape(shape), drift[:, 1].reshape(shape)
            speed = np.sqrt(U**2 + V**2) + 1e-8
            ax.quiver(grid_x, grid_y, U/speed, V/speed,
                      alpha=0.4, color=C_CURRENT, scale=18, width=0.004, zorder=2)

            # Example trajectory (Euler integration)
            for seed in traj_seeds[:3]:
                traj = [seed.copy()]
                dt = 0.15
                for _ in range(60):
                    x_cur = traj[-1]
                    drift_cur = Om @ x_cur
                    noise = rng4.multivariate_normal([0, 0], np.eye(2) * 0.04)
                    x_new = x_cur + dt * drift_cur + np.sqrt(dt) * noise
                    traj.append(x_new)
                traj = np.array(traj)
                ax.plot(traj[:, 0], traj[:, 1], lw=1.0, alpha=0.6, color=C_TRAJ, zorder=3)
                ax.plot(traj[0, 0], traj[0, 1], "o", color=C_HIGHLIGHT, ms=4, zorder=4)
        else:
            # Panel A: random walk (no net flow)
            for seed in traj_seeds[:3]:
                traj = [seed.copy()]
                for _ in range(60):
                    x_cur = traj[-1]
                    noise = rng4.multivariate_normal([0, 0], np.eye(2) * 0.08)
                    # Mild restoring force toward origin (equilibrium)
                    x_new = x_cur - 0.05 * x_cur + np.sqrt(0.08) * noise
                    traj.append(x_new)
                traj = np.array(traj)
                ax.plot(traj[:, 0], traj[:, 1], lw=1.0, alpha=0.6, color=C_TRAJ, zorder=3)
                ax.plot(traj[0, 0], traj[0, 1], "o", color=C_HIGHLIGHT, ms=4, zorder=4)
            ax.text(0, 3.5, "No arrows:\nno net circulation", ha="center",
                    fontsize=8, color=C_COV)

        # Label
        ax.text(-3.5, -3.5, "Same Q\n(same density)", fontsize=7.5, color=C_COV)

    axes[1].text(2.5, 3.2, "Circulates\nclockwise", fontsize=8, color=C_CURRENT, ha="center")
    axes[2].text(2.5, 3.2, "Circulates\ncounter-CW", fontsize=8, color=C_CURRENT, ha="center")

    fig.text(0.5, -0.04,
             "Ω measures probability current — how states move through state space, not where they accumulate.\n"
             "All three panels have identical stationary distributions (same Q). Only the flow pattern (Ω) differs.",
             ha="center", fontsize=8.5, color=C_TEXT, style="italic")

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4: "From D and Q to Ω"
# ─────────────────────────────────────────────────────────────────────────────
def fig4_dq_to_omega():
    fig = plt.figure(figsize=(13, 8))
    fig.suptitle("Figure 4 — Combining Fluctuations and Organization: Ω = DQ + A",
                 fontsize=13, fontweight="bold")

    gs = GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.4,
                  left=0.06, right=0.82, top=0.88, bottom=0.08)

    cov_stat = np.array([[1.5, 0.6], [0.6, 0.8]])
    Q_fixed  = np.linalg.inv(cov_stat)

    D_cases = [
        ("A.  Uniform small D\n(Ω ≈ small, follows Q)",
         np.eye(2) * 0.2,
         "Same structure as Q\n(just smaller)"),
        ("B.  Anisotropic D\nx₁ gets more noise\n(Ω reweights toward x₁)",
         np.diag([0.9, 0.1]),
         "Ω biased toward\nhigh-noise direction"),
        ("C.  Uniform large D\n(Ω ∝ Q, bigger scale)",
         np.eye(2) * 0.9,
         "Same structure as Q\n(just larger)"),
        ("D.  Correlated D\n(off-diagonal non-zero)\n(Ω reveals new directions)",
         np.array([[0.5, 0.4], [0.4, 0.5]]),
         "New direction\nnot in Q alone"),
    ]

    panel_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    rng5 = np.random.default_rng(99)

    for (row, col), (title, D, annotation) in zip(panel_positions, D_cases):
        ax = fig.add_subplot(gs[row, col])
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=8.5, pad=5)
        ax.set_xlabel("x₁", fontsize=9); ax.set_ylabel("x₂", fontsize=9)
        ax.axhline(0, color=C_FAINT, lw=0.5); ax.axvline(0, color=C_FAINT, lw=0.5)

        # Stationary distribution (fixed Q)
        ell_stat = make_ellipse(cov_stat, n_std=1.5,
                                edgecolor=C_DENSITY, facecolor=C_DENSITY, alpha=0.25,
                                linewidth=1.5)
        ax.add_patch(ell_stat)

        # D blobs at sample points
        n_pts = 6
        pts = rng5.multivariate_normal([0, 0], cov_stat * 0.5, n_pts)
        for p in pts:
            blob = make_ellipse(D * 3, center=tuple(p), n_std=1.0,
                                edgecolor=C_DIFFUSION, facecolor=C_DIFFUSION,
                                alpha=0.25, linewidth=1.2)
            ax.add_patch(blob)

        # Ω arrows (DQ product direction)
        try:
            Omega = D @ Q_fixed
        except Exception:
            Omega = Q_fixed
        grid_x, grid_y = np.meshgrid(np.linspace(-2.5, 2.5, 7),
                                     np.linspace(-2.5, 2.5, 7))
        shape = grid_x.shape
        pos = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
        flow = pos @ Omega.T
        U, V = flow[:, 0].reshape(shape), flow[:, 1].reshape(shape)
        spd = np.sqrt(U**2 + V**2) + 1e-8
        ax.quiver(grid_x, grid_y, U/spd, V/spd,
                  color=C_CURRENT, alpha=0.55, scale=20, width=0.005, zorder=3)

        ax.text(0, -3.7, annotation, ha="center", fontsize=7.5, color=C_CURRENT)

    # Metaphor sidebar
    ax_meta = fig.add_subplot(gs[:, 2])
    ax_meta.axis("off")
    ax_meta.set_xlim(0, 1); ax_meta.set_ylim(0, 1)

    # Box
    rect = mpatches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9,
                                   boxstyle="round,pad=0.02",
                                   edgecolor="#AAAAAA", facecolor="#F8F8F8", linewidth=1.5)
    ax_meta.add_patch(rect)

    ax_meta.text(0.5, 0.95, "Visual Metaphor", ha="center", va="top",
                 fontsize=10, fontweight="bold", color=C_TEXT)

    metaphors = [
        (0.78, "Q", C_PRECISION,   "Road map\n(where are the roads?)"),
        (0.54, "D", C_DIFFUSION,   "Traffic volume\n(how many cars per lane?)"),
        (0.28, "Ω", C_CURRENT,     "Traffic organization\n(where does traffic flow?)"),
    ]
    for y, sym, col, desc in metaphors:
        ax_meta.text(0.2, y, sym, ha="center", va="center",
                     fontsize=22, fontweight="bold", color=col)
        ax_meta.text(0.62, y, desc, ha="center", va="center",
                     fontsize=9, color=C_TEXT)

    ax_meta.text(0.5, 0.1,
                 "Same road map (Q).\nDifferent traffic (D).\nDifferent flow (Ω).",
                 ha="center", va="bottom", fontsize=9, color=C_TEXT, style="italic")

    ax_meta.set_title("", fontsize=10)

    fig.text(0.42, 0.01,
             "Ω = DQ + A.  When D is uniform, Ω is a scaled copy of Q (panels A, C).\n"
             "When D is non-uniform or correlated, Ω reveals new structure (panels B, D).",
             ha="center", fontsize=8.5, color=C_TEXT, style="italic")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5: "What Happened in C. elegans?"
# ─────────────────────────────────────────────────────────────────────────────
def fig5_worm_application():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Figure 5 — What Happened in C. elegans?", fontsize=13,
                 fontweight="bold")

    # ── Panel A: Diffusion reorganization ─────────────────────────────────
    ax = axes[0]
    ax.set_title("A.  Diffusion reorganization", fontsize=10, fontweight="bold")

    # Stylized ΔD bar chart — schematic values inspired by phase3e results
    neuron_labels = ["URXL", "URYVL", "RMD", "IL1", "RID", "CEP", "RME", "AVJ", "AIZ", "AVD"]
    delta_D = [0.208, 0.149, 0.06, 0.04, 0.02, -0.01, -0.03, -0.10, -0.167, -0.150]
    colors_d = [C_DIFFUSION if v > 0 else C_HIGHLIGHT for v in delta_D]

    x_pos = np.arange(len(neuron_labels))
    bars = ax.bar(x_pos, delta_D, color=colors_d, alpha=0.75, width=0.65, zorder=3)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(neuron_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("ΔD[i,i]  (roam − dwell)", fontsize=9)
    ax.set_ylim(-0.28, 0.28)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.text(0.5, 0.96,
            "ρ(D_roam, D_dwell) ≈ 0.14\n(rank order reshuffles)", transform=ax.transAxes,
            ha="center", va="top", fontsize=8, color=C_COV,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_FAINT))

    # Legend
    ax.text(1.0, 0.19, "Roaming-dominant\n(aerotaxis sensors)", transform=ax.transAxes,
            ha="left", fontsize=7.5, color=C_DIFFUSION)
    ax.text(1.0, 0.03, "Dwelling-dominant\n(olfactory / reversal)", transform=ax.transAxes,
            ha="left", fontsize=7.5, color=C_HIGHLIGHT)

    # ── Panel B: Precision reorganization ─────────────────────────────────
    ax = axes[1]
    ax.set_title("B.  Precision reorganization", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    # Module nodes
    modules = {
        "DA_mech\n(ADEL/CEP)": (3.0, 7.5),
        "URY_URX\n(aerotaxis)": (7.0, 7.5),
        "RME\n(GABA)":          (7.5, 4.5),
        "RMD_SMD\n(motor)":     (3.0, 1.5),
        "IL1_IL2":              (7.5, 1.5),
        "RID":                  (5.0, 5.0),
    }
    module_colors = {
        "DA_mech\n(ADEL/CEP)": C_HIGHLIGHT,
        "URY_URX\n(aerotaxis)": C_HIGHLIGHT,
        "RME\n(GABA)":          C_DIFFUSION,
        "RMD_SMD\n(motor)":     C_COV,
        "IL1_IL2":              C_COV,
        "RID":                  C_COV,
    }

    for label, (x, y) in modules.items():
        col = module_colors.get(label, C_COV)
        circle = plt.Circle((x, y), 0.8, color=col, alpha=0.25, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color=col,
                fontweight="bold", zorder=3)

    # Key edge: DA_mech ↔ URY_URX (bold, highlighted)
    ax.annotate("", xy=(6.2, 7.5), xytext=(3.8, 7.5),
                arrowprops=dict(arrowstyle="<->", lw=3.5, color=C_HIGHLIGHT), zorder=4)
    ax.text(5.0, 8.1, "ΔQ rank 1–10\nPDF-enriched\nAUROC = 0.556",
            ha="center", fontsize=7.5, color=C_HIGHLIGHT)

    # Thin edges for background
    edges = [("RID", "DA_mech\n(ADEL/CEP)"), ("RID", "URY_URX\n(aerotaxis)"),
             ("RME\n(GABA)", "URY_URX\n(aerotaxis)"), ("RMD_SMD\n(motor)", "DA_mech\n(ADEL/CEP)")]
    for a, b in edges:
        x1, y1 = modules[a]; x2, y2 = modules[b]
        ax.plot([x1, x2], [y1, y2], lw=0.8, color=C_FAINT, zorder=1)

    ax.text(5.0, 0.3, "12 Class-4 pairs in DA_mech ↔ URY_URX block\n"
            "ΔQ is independent of ΔD (ρ ≈ 0.05)",
            ha="center", fontsize=7.5, color=C_COV)

    # ── Panel C: Current convergence ──────────────────────────────────────
    ax = axes[2]
    ax.set_title("C.  Current convergence\n(Ω collapses to Q)", fontsize=10, fontweight="bold")

    # Scatter plot: ΔΩ vs ΔQ (simulated near-perfect correlation)
    rng6 = np.random.default_rng(11)
    n_pairs = 150
    dQ = rng6.standard_normal(n_pairs)
    dOmega = 1.025 * dQ + rng6.standard_normal(n_pairs) * 0.003
    ax.scatter(dQ, dOmega, s=12, alpha=0.45, color=C_CURRENT, zorder=2)

    # Identity line
    lim = max(abs(dQ).max(), abs(dOmega).max()) * 1.1
    ax.plot([-lim, lim], [-lim, lim], "--", color=C_COV, lw=1.5, label="Ω = Q", zorder=3)
    ax.set_xlabel("ΔQ (precision change)", fontsize=9)
    ax.set_ylabel("ΔΩ (current change)", fontsize=9)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, loc="upper left")

    ax.text(0.97, 0.05,
            "ρ(ΔΩ, ΔQ) = 0.9999\n(CePNEM z-scoring\nforces D ≈ 1·I)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
            color=C_CURRENT,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_FAINT))

    fig.text(0.5, -0.02,
             "D changes (Panel A). Q changes (Panel B). But ΔΩ ≈ ΔQ (Panel C).\n"
             "z-scoring forces D ≈ constant·I, making Ω a near-constant rescaling of Q.\n"
             "The biological interpretation rests on ΔQ — Ω adds nothing here.",
             ha="center", fontsize=8.5, color=C_TEXT, style="italic")

    fig.tight_layout(rect=[0, 0.06, 1, 1])
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6: "When Ω Matters"
# ─────────────────────────────────────────────────────────────────────────────
def fig6_when_omega_matters():
    fig, axes = plt.subplots(3, 4, figsize=(13, 8))
    fig.suptitle("Figure 6 — When Ω Matters", fontsize=13, fontweight="bold")

    systems = ["OU cascade\n(toy)", "Leech", "Worm\n(this study)"]
    d_desc  = ["Non-uniform\n(input node)", "Heterogeneous\nacross neurons", "Near-uniform\n(z-scored)"]
    o_desc  = ["Long-range structure\nemerges in Ω", "Module rankings\ndiverge from Q", "ΔΩ ≡ ΔQ\n(ρ = 0.9999)"]
    verdict = ["✓  Ω adds\ninformation", "✓  Ω adds\ninformation", "✗  Ω = Q\nno new signal"]
    verdict_col = [C_DIFFUSION, C_DIFFUSION, C_HIGHLIGHT]

    D_sketches = [
        np.diag([0.9, 0.1]),
        np.array([[0.7, 0.2], [0.2, 0.3]]),
        np.eye(2) * 0.5,
    ]
    Omega_sketches = [
        np.array([[0.0, 0.9], [0.3, 0.0]]),
        np.array([[0.0, 0.6], [0.4, 0.0]]),
        np.array([[0.4, 0.0], [0.0, 0.4]]),
    ]

    col_titles = ["System", "D structure", "Ω structure", "Verdict"]
    for j, ct in enumerate(col_titles):
        axes[0, j].set_title(ct, fontsize=10, fontweight="bold", pad=8)

    rng7 = np.random.default_rng(5)
    cov_ref = np.array([[1.2, 0.4], [0.4, 0.8]])

    for i, (system, dd, od, vd, vc, D_s, O_s) in enumerate(
            zip(systems, d_desc, o_desc, verdict, verdict_col, D_sketches, Omega_sketches)):

        # Col 0: system label
        axes[i, 0].axis("off")
        axes[i, 0].text(0.5, 0.5, system, ha="center", va="center",
                        fontsize=12, fontweight="bold", color=C_TEXT)

        # Col 1: D structure
        ax = axes[i, 1]
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
        ax.axis("off")
        ell_d = make_ellipse(D_s * 4, n_std=1.5,
                             edgecolor=C_DIFFUSION, facecolor=C_DIFFUSION, alpha=0.3, lw=2)
        ax.add_patch(ell_d)
        ax.text(0, -2.7, dd, ha="center", fontsize=8, color=C_DIFFUSION)

        # Col 2: Ω structure (flow field)
        ax = axes[i, 2]
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
        ax.axis("off")

        ell_stat = make_ellipse(cov_ref, n_std=1.5,
                                edgecolor=C_DENSITY, facecolor=C_DENSITY, alpha=0.2, lw=1)
        ax.add_patch(ell_stat)

        grid_x, grid_y = np.meshgrid(np.linspace(-2.5, 2.5, 7), np.linspace(-2.5, 2.5, 7))
        shape = grid_x.shape
        pos = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
        flow = pos @ O_s.T
        U, V = flow[:, 0].reshape(shape), flow[:, 1].reshape(shape)
        spd = np.sqrt(U**2 + V**2) + 1e-8
        ax.quiver(grid_x, grid_y, U/spd, V/spd,
                  color=C_CURRENT, alpha=0.5, scale=20, width=0.005)
        ax.text(0, -2.7, od, ha="center", fontsize=8, color=C_CURRENT)

        # Col 3: verdict
        axes[i, 3].axis("off")
        axes[i, 3].text(0.5, 0.5, vd, ha="center", va="center",
                        fontsize=13, fontweight="bold", color=vc)

    # Row separators
    for i in range(1, 3):
        for j in range(4):
            axes[i, j].spines["top"].set_linewidth(0.5)

    # Information gain bar chart (below main grid)
    ax_bar = fig.add_axes([0.15, 0.01, 0.7, 0.07])
    gains = [1.0, 0.55, 0.0]
    bar_colors = [C_DIFFUSION, C_DIFFUSION, C_HIGHLIGHT]
    bars = ax_bar.barh(["OU cascade", "Leech", "Worm"], gains,
                       color=bar_colors, alpha=0.7, height=0.5)
    ax_bar.set_xlim(0, 1.2)
    ax_bar.set_xlabel("Ω information gain (relative)", fontsize=8.5)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.set_title(
        "Ω utility depends on D non-uniformity — z-scoring collapses Ω → Q",
        fontsize=9, pad=4)

    fig.tight_layout(rect=[0, 0.10, 1, 0.97])
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    import os
    out_dir = os.path.join(os.path.dirname(__file__),
                           "../../results/visualization")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "figure_sketches.pdf")

    builders = [
        fig1_what_q_sees,
        fig2_what_d_sees,
        fig3_what_omega_sees,
        fig4_dq_to_omega,
        fig5_worm_application,
        fig6_when_omega_matters,
    ]

    with PdfPages(out_path) as pdf:
        for i, build in enumerate(builders, start=1):
            print(f"  Rendering Figure {i}...", flush=True)
            fig = build()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
