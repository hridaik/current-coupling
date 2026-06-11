"""
Animation 4 — From Precision to Current  (PHASE VIS-1C)
Rendered with Manim 0.20.
Output: results/visualization/dq_to_current_animation_refined.mp4

Five scenes:
  1. Q — precision geometry
  2. D — diffusion input
  3. Ω — probability current
  4. Ω = DQ + A — the combination
  5. C. elegans — honest worm summary
"""

from manim import *
import numpy as np

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = ManimColor("#0F0F14")
C_BLU = ManimColor("#3D5A99")
C_ORG = ManimColor("#E07B39")
C_TEA = ManimColor("#2A9D8F")
C_PUR = ManimColor("#8B5CF6")
C_YEL = ManimColor("#F5C518")
C_DGR = ManimColor("#333344")   # dark gray (panel outlines)
C_MGR = ManimColor("#555566")   # mid gray
C_LGR = ManimColor("#888899")   # light gray

# ── Shared math ───────────────────────────────────────────────────────────────
COV_STAT = np.array([[2.0, 1.2], [1.2, 1.0]])
PREC_STAT = np.linalg.inv(COV_STAT)
A_SKEW = np.array([[0.0, -0.7], [0.7, 0.0]])   # circulating drift


def cov_ellipse(cov, scale=1.5, **kwargs):
    """Return a Manim Ellipse aligned to the covariance principal axes."""
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.arctan2(vecs[1, 0], vecs[0, 0])
    w = 2 * scale * np.sqrt(max(vals[0], 1e-9))
    h = 2 * scale * np.sqrt(max(vals[1], 1e-9))
    ell = Ellipse(width=w, height=h, **kwargs)
    ell.rotate(angle)
    return ell


def flow_field(A, nx=7, ny=5, x_range=(-3.0, 3.0), y_range=(-2.0, 2.0),
               arrow_len=0.28, cx=0, cy=0, color=C_PUR, opacity=0.55):
    """Return a VGroup of short Arrows forming a flow field for drift A."""
    xs = np.linspace(*x_range, nx)
    ys = np.linspace(*y_range, ny)
    grp = VGroup()
    for x in xs:
        for y in ys:
            pos = np.array([x, y])
            vel = A @ pos
            spd = np.linalg.norm(vel)
            if spd < 0.05:
                continue
            tip = pos + vel / spd * arrow_len
            arr = Arrow(
                start=[cx + x, cy + y, 0],
                end=[cx + tip[0], cy + tip[1], 0],
                buff=0, color=color, stroke_width=1.8,
                max_tip_length_to_length_ratio=0.38,
            )
            arr.set_stroke(opacity=opacity)
            grp.add(arr)
    return grp


def particle_path(traj, cx=0, cy=0, color=C_BLU, width=1.8, opacity=0.7):
    """Return a VMobject smooth path for a particle trajectory."""
    vmo = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    pts = [[cx + float(p[0]), cy + float(p[1]), 0] for p in traj]
    vmo.set_points_smoothly(pts)
    return vmo


# ── Main scene ────────────────────────────────────────────────────────────────

class DQCurrentAnimation(Scene):

    def setup(self):
        self.camera.background_color = BG
        self.rng = np.random.default_rng(42)

    def construct(self):
        self.title_card()
        self.scene1_precision()
        self.scene2_diffusion()
        self.scene3_current()
        self.scene4_combination()
        self.scene5_worm()

    # ── Utility ──────────────────────────────────────────────────────────────

    def cue_text(self, s, color=C_LGR, size=24, italic=True):
        """Bottom-strip cue text, never overlapping visuals."""
        t = Text(s, font_size=size, color=color,
                 slant=ITALIC if italic else NORMAL)
        t.to_edge(DOWN, buff=0.5)
        return t

    def scene_header(self, s, n_of_5):
        """Top-strip scene heading + scene counter."""
        h = Text(s, font_size=34, color=WHITE, weight=BOLD)
        h.to_edge(UP, buff=0.38)
        n = Text(f"{n_of_5} of 5", font_size=15, color=C_MGR)
        n.to_corner(UL, buff=0.28)
        return h, n

    def gaussian_dots(self, n=150, cov=None):
        if cov is None:
            cov = COV_STAT
        pts = self.rng.multivariate_normal([0, 0], cov, n)
        return VGroup(*[
            Dot(point=[float(p[0]), float(p[1]), 0],
                radius=0.04, color=C_BLU, fill_opacity=0.45)
            for p in pts
        ])

    def sim_ou(self, starts, A_extra=None, n_steps=200, dt=0.06, noise=0.1):
        rng2 = np.random.default_rng(77)
        trajs = []
        for s0 in starts:
            pos = s0.copy()
            tr = [pos.copy()]
            for _ in range(n_steps):
                d = -0.38 * pos
                if A_extra is not None:
                    d = d + pos @ A_extra.T
                pos = pos + d * dt + rng2.multivariate_normal([0, 0], np.eye(2) * noise) * np.sqrt(dt)
                tr.append(pos.copy())
            trajs.append(tr)
        return trajs

    # ── Scene 0: title ────────────────────────────────────────────────────────

    def title_card(self):
        t1 = Text("From Precision to Current",
                  font_size=52, color=WHITE, weight=BOLD)
        t2 = Text("D,   Q,   and Ω   in a stochastic system",
                  font_size=26, color=C_ORG)
        t2.next_to(t1, DOWN, buff=0.5)
        grp = VGroup(t1, t2).move_to(ORIGIN)
        self.play(FadeIn(grp, run_time=1.2))
        self.wait(2.2)
        self.play(FadeOut(grp, run_time=0.9))

    # ── Scene 1: Q ────────────────────────────────────────────────────────────

    def scene1_precision(self):
        hd, nlbl = self.scene_header("What Q sees", "1")
        self.play(FadeIn(hd, nlbl, run_time=0.7))

        # Cloud
        dots = self.gaussian_dots(160)
        cue = self.cue_text("States of a 2D stochastic system")
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in dots],
                        lag_ratio=0.008, run_time=2.5),
            FadeIn(cue),
        )
        self.wait(0.8)

        # Covariance ellipse
        c_ell = cov_ellipse(COV_STAT, scale=1.5, color=C_LGR,
                            fill_opacity=0, stroke_width=2.0)
        c_ell.set_stroke(opacity=0.6)
        cue2 = self.cue_text("Covariance — where states scatter")
        self.play(Create(c_ell, run_time=1.8), ReplacementTransform(cue, cue2))
        self.wait(0.8)

        # Precision ellipse
        p_ell = cov_ellipse(PREC_STAT, scale=1.2, color=C_ORG,
                            fill_opacity=0, stroke_width=2.8)
        cue3 = self.cue_text("Precision Q = Σ⁻¹ — which directions are constrained",
                             color=C_ORG, size=22)
        self.play(Create(p_ell, run_time=2.0), ReplacementTransform(cue2, cue3))
        self.wait(0.8)

        # Axis labels on the precision ellipse
        vals, vecs = np.linalg.eigh(PREC_STAT)
        idx = vals.argsort()[::-1]
        vals, vecs = vals[idx], vecs[:, idx]
        # Tip of strong axis on the ellipse (unit vec × scale × sqrt(eigenval))
        s_tip = vecs[:, 0] * 1.2 * float(np.sqrt(vals[0]))   # data units
        w_tip = vecs[:, 1] * 1.2 * float(np.sqrt(vals[1]))

        # Clamp label positions to safe zone
        def safe_label_pos(tip, radial_offset=1.3, max_y=2.3):
            mag = np.linalg.norm(tip)
            direction = tip / (mag + 1e-9)
            pos = tip + direction * radial_offset
            pos[1] = np.clip(pos[1], -max_y, max_y)
            return [float(pos[0]), float(pos[1]), 0]

        lbl_s = Text("large Q\nstrong constraint",
                     font_size=20, color=C_ORG, line_spacing=0.8)
        lbl_s.move_to(safe_label_pos(s_tip))

        lbl_w = Text("small Q\nalmost free",
                     font_size=20, color=C_TEA, line_spacing=0.8)
        lbl_w.move_to(safe_label_pos(w_tip))

        arr_s = Arrow(lbl_s.get_center(),
                      [float(s_tip[0]) * 0.9, float(s_tip[1]) * 0.9, 0],
                      buff=0.28, color=C_ORG, stroke_width=1.4,
                      max_tip_length_to_length_ratio=0.2)
        arr_w = Arrow(lbl_w.get_center(),
                      [float(w_tip[0]) * 0.9, float(w_tip[1]) * 0.9, 0],
                      buff=0.28, color=C_TEA, stroke_width=1.4,
                      max_tip_length_to_length_ratio=0.2)

        self.play(FadeIn(lbl_s, arr_s, run_time=0.7))
        self.wait(0.4)
        self.play(FadeIn(lbl_w, arr_w, run_time=0.7))
        self.wait(1.5)

        cue4 = self.cue_text("Q tells us how the stationary density is shaped",
                             color=WHITE, size=26, italic=False)
        self.play(ReplacementTransform(cue3, cue4))
        self.wait(2.5)

        self.play(FadeOut(
            VGroup(hd, nlbl, dots, c_ell, p_ell, lbl_s, lbl_w, arr_s, arr_w, cue4),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 2: D ────────────────────────────────────────────────────────────

    def scene2_diffusion(self):
        hd, nlbl = self.scene_header("What D sees", "2")
        self.play(FadeIn(hd, nlbl, run_time=0.7))

        # Ghost stationary distribution
        ghost = cov_ellipse(COV_STAT, scale=1.5, color=C_LGR,
                            fill_opacity=0, stroke_width=1.5)
        ghost.set_stroke(opacity=0.28)
        ghost_lbl = Text("stationary distribution (fixed)", font_size=16, color=C_MGR)
        ghost_lbl.next_to(ghost, UP, buff=0.12).shift(RIGHT * 1.5)

        cue0 = self.cue_text("Same stationary distribution throughout...")
        self.play(Create(ghost, run_time=0.9), FadeIn(ghost_lbl, cue0))
        self.wait(1.2)

        # Five state positions inside the cloud
        positions = [
            [-1.1,  0.5], [0.9,  0.7], [1.2, -0.6],
            [-0.3, -0.8], [0.1,  0.1],
        ]
        state_dots = VGroup(*[
            Dot(point=[p[0], p[1], 0], radius=0.09, color=C_BLU, fill_opacity=0.9)
            for p in positions])
        self.play(LaggedStart(*[FadeIn(d, scale=1.4) for d in state_dots],
                              lag_ratio=0.1, run_time=1.0))
        self.wait(0.5)

        # Three D cases
        D_ISO   = np.eye(2) * 0.36
        D_ANISO = np.diag([0.1, 0.72])
        D_CORR  = np.array([[0.45, 0.38], [0.38, 0.45]])

        cases = [
            (D_ISO,   "D = I   ·   equal fluctuations in every direction",   C_TEA),
            (D_ANISO, "D diagonal, anisotropic   ·   x₂ fluctuates more",  C_TEA),
            (D_CORR,  "D off-diagonal   ·   x₁ and x₂ fluctuate together", C_TEA),
        ]

        def kick_group(D_mat, color):
            grp = VGroup()
            for p in positions:
                e = cov_ellipse(D_mat, scale=1.15, color=color,
                                fill_color=color, fill_opacity=0.14,
                                stroke_width=2.0)
                e.shift(np.array([p[0], p[1], 0]))
                grp.add(e)
            return grp

        current_kicks = None
        current_cue = cue0

        for D_mat, label, col in cases:
            kicks = kick_group(D_mat, col)
            new_cue = self.cue_text(label, color=C_TEA, size=24)
            if current_kicks is None:
                self.play(
                    LaggedStart(*[Create(k) for k in kicks], lag_ratio=0.08, run_time=1.3),
                    ReplacementTransform(current_cue, new_cue),
                )
            else:
                self.play(
                    ReplacementTransform(current_kicks, kicks, run_time=1.2),
                    ReplacementTransform(current_cue, new_cue),
                )
            self.wait(2.2)
            current_kicks = kicks
            current_cue = new_cue

        sum_cue = self.cue_text(
            "D tells us where new fluctuations enter   ·   Q (stationary distribution) unchanged",
            color=WHITE, size=22, italic=False)
        self.play(ReplacementTransform(current_cue, sum_cue))
        self.wait(2.5)

        self.play(FadeOut(
            VGroup(hd, nlbl, ghost, ghost_lbl, state_dots, current_kicks, sum_cue),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 3: Ω ────────────────────────────────────────────────────────────

    def scene3_current(self):
        hd, nlbl = self.scene_header("What Ω sees", "3")
        self.play(FadeIn(hd, nlbl, run_time=0.7))

        LX, RX = -3.3, 3.3
        # Two identical density ellipses
        ell_L = cov_ellipse(COV_STAT, scale=1.35, color=C_LGR,
                            fill_opacity=0, stroke_width=1.8).shift(LEFT * 3.3)
        ell_R = cov_ellipse(COV_STAT, scale=1.35, color=C_LGR,
                            fill_opacity=0, stroke_width=1.8).shift(RIGHT * 3.3)
        ell_L.set_stroke(opacity=0.45); ell_R.set_stroke(opacity=0.45)

        divider = DashedLine([0, -3.0, 0], [0, 3.0, 0],
                              color=C_MGR, stroke_width=1.0, stroke_opacity=0.35)

        lbl_L = Text("Detailed balance\nΩ = 0",
                     font_size=26, color=WHITE, line_spacing=0.85)
        lbl_L.move_to([LX, 2.85, 0])
        lbl_R = Text("Circulating current\nΩ ≠ 0",
                     font_size=26, color=C_PUR, line_spacing=0.85)
        lbl_R.move_to([RX, 2.85, 0])

        cue1 = self.cue_text("Same stationary distribution — same Q")
        self.play(Create(ell_L, run_time=0.8), Create(ell_R, run_time=0.8),
                  FadeIn(divider, lbl_L, lbl_R, cue1))
        self.wait(0.8)

        # Flow arrows on RIGHT panel only
        arrows = flow_field(A_SKEW, nx=7, ny=5, x_range=(-2.6, 2.6),
                            y_range=(-1.8, 1.8), arrow_len=0.26,
                            cx=RX, cy=0, color=C_PUR, opacity=0.5)
        cue2 = self.cue_text("Probability circulates on the right — density identical",
                             color=C_PUR, size=24)
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.02, run_time=1.5),
                  ReplacementTransform(cue1, cue2))
        self.wait(0.8)

        # Particle paths
        rng2 = np.random.default_rng(7)
        starts = rng2.multivariate_normal([0, 0], COV_STAT * 0.12, 4)
        trajs_eq  = self.sim_ou(starts, A_extra=None,       n_steps=160, dt=0.07, noise=0.10)
        trajs_cir = self.sim_ou(starts, A_extra=A_SKEW,     n_steps=160, dt=0.07, noise=0.07)

        paths_L = VGroup(*[particle_path(tr, cx=LX, cy=0, color=C_BLU,  width=1.6)
                           for tr in trajs_eq])
        paths_R = VGroup(*[particle_path(tr, cx=RX, cy=0, color=C_PUR, width=1.6)
                           for tr in trajs_cir])

        cue3 = self.cue_text("Trajectories orbit on the right — diffuse randomly on the left",
                             color=C_LGR, size=22)
        self.play(ReplacementTransform(cue2, cue3))
        self.play(
            LaggedStart(*[Create(p, run_time=3.0) for p in paths_L], lag_ratio=0.18),
            LaggedStart(*[Create(p, run_time=3.0) for p in paths_R], lag_ratio=0.18),
        )
        self.wait(0.8)

        cue4 = self.cue_text(
            "Identical Q  —  identical where.   Different Ω  —  different how.",
            color=WHITE, size=26, italic=False)
        self.play(ReplacementTransform(cue3, cue4))
        self.wait(2.5)

        cue5 = self.cue_text("Ω describes movement through state space",
                             color=C_PUR, size=28, italic=False)
        self.play(ReplacementTransform(cue4, cue5))
        self.wait(2.0)

        self.play(FadeOut(
            VGroup(hd, nlbl, ell_L, ell_R, divider,
                   lbl_L, lbl_R, arrows, paths_L, paths_R, cue5),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 4: Ω = DQ + A ───────────────────────────────────────────────────

    def scene4_combination(self):
        eq_hd = Text("Ω = DQ + A", font_size=46, color=WHITE, weight=BOLD)
        eq_hd.to_edge(UP, buff=0.38)
        nlbl = Text("4 of 5", font_size=15, color=C_MGR)
        nlbl.to_corner(UL, buff=0.28)
        self.play(FadeIn(eq_hd, nlbl, run_time=0.7))

        # Panel positions
        LX, MX, RX = -4.4, 0.0, 4.4
        CY = 0.15

        # Panel labels
        h_q = Text("Q", font_size=42, color=C_ORG, weight=BOLD).move_to([LX, 2.65, 0])
        h_d = Text("D", font_size=42, color=C_TEA, weight=BOLD).move_to([MX, 2.65, 0])
        h_o = Text("Ω", font_size=42, color=C_PUR, weight=BOLD).move_to([RX, 2.65, 0])

        op_x  = Text("×", font_size=34, color=C_MGR).move_to([-2.1, CY, 0])
        op_eq = Text("=", font_size=34, color=C_MGR).move_to([ 2.1, CY, 0])

        self.play(FadeIn(h_q, h_d, h_o, op_x, op_eq, run_time=0.9))

        # Q ellipse
        q_ell = cov_ellipse(COV_STAT, scale=1.35, color=C_ORG,
                            fill_opacity=0, stroke_width=2.8).shift([LX, CY, 0])
        cue1 = self.cue_text("Q — road map of constraint (fixed throughout)", color=C_ORG, size=24)
        self.play(Create(q_ell, run_time=1.8), FadeIn(cue1))
        self.wait(1.0)

        # ── Case A: uniform D ──────────────────────────────────────────────
        D_ISO = np.eye(2) * 0.4
        d_iso = cov_ellipse(D_ISO, scale=1.6, color=C_TEA,
                            fill_opacity=0, stroke_width=2.8).shift([MX, CY, 0])

        Om_iso_cov = D_ISO @ COV_STAT + np.eye(2) * 0.01
        o_iso = cov_ellipse(Om_iso_cov, scale=1.35, color=C_PUR,
                            fill_opacity=0, stroke_width=2.8).shift([RX, CY, 0])
        q_ref_a = cov_ellipse(COV_STAT, scale=1.35, color=C_ORG,
                              fill_opacity=0, stroke_width=1.2)
        q_ref_a.set_stroke(opacity=0.35).shift([RX, CY, 0])

        cue2 = self.cue_text("D = I   →   Ω looks like a rescaled Q", color=C_TEA, size=26)
        self.play(Create(d_iso, run_time=1.4), ReplacementTransform(cue1, cue2))
        self.play(Create(o_iso, run_time=1.4), Create(q_ref_a, run_time=1.0))

        eq_lbl = Text("≈ Q", font_size=22, color=C_LGR).move_to([RX + 1.9, CY - 1.6, 0])
        self.play(FadeIn(eq_lbl))
        self.wait(1.8)

        # ── Case B: non-uniform D ──────────────────────────────────────────
        D_ANI = np.diag([0.1, 0.78])
        d_ani = cov_ellipse(D_ANI, scale=1.6, color=C_TEA,
                            fill_opacity=0, stroke_width=2.8).shift([MX, CY, 0])

        Om_ani_cov = D_ANI @ COV_STAT + np.eye(2) * 0.01
        o_ani = cov_ellipse(Om_ani_cov, scale=1.35, color=C_PUR,
                            fill_opacity=0, stroke_width=2.8).shift([RX, CY, 0])

        cue3 = self.cue_text("D non-uniform   →   Ω rotates away from Q",
                             color=WHITE, size=26, italic=False)
        self.play(
            Transform(d_iso, d_ani, run_time=1.8),
            Transform(o_iso, o_ani, run_time=1.8),
            FadeOut(eq_lbl, run_time=0.6),
            ReplacementTransform(cue2, cue3),
        )
        self.wait(2.0)

        # ── Metaphor phase ─────────────────────────────────────────────────
        cue4 = self.cue_text(
            "Same road map. Different traffic. Different flow.",
            color=WHITE, size=28, italic=False)
        self.play(
            FadeOut(VGroup(h_q, h_d, h_o, op_x, op_eq,
                           q_ell, d_iso, o_iso, q_ref_a, cue3),
                    run_time=0.9),
        )
        meta = VGroup(
            Text("Q  =  road map",             font_size=30, color=C_ORG),
            Text("D  =  traffic volume",       font_size=30, color=C_TEA),
            Text("Ω  =  traffic organization", font_size=30, color=C_PUR),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to([0, 0.1, 0])
        self.play(FadeIn(cue4))
        self.play(LaggedStart(*[Write(m) for m in meta], lag_ratio=0.38, run_time=2.2))
        self.wait(2.5)

        self.play(FadeOut(VGroup(eq_hd, nlbl, meta, cue4), run_time=1.0))
        self.wait(0.2)

    # ── Scene 5: Worm ─────────────────────────────────────────────────────────

    def scene5_worm(self):
        hd, nlbl = self.scene_header("In C. elegans", "5")
        self.play(FadeIn(hd, nlbl, run_time=0.7))

        # Column positions (three equal panels)
        LX, MX, RX = -4.4, 0.0, 4.4
        MID_Y = 0.2

        # Column headers
        h_d = Text("D", font_size=32, color=C_TEA, weight=BOLD).move_to([LX, 2.55, 0])
        h_q = Text("Q", font_size=32, color=C_ORG, weight=BOLD).move_to([MX, 2.55, 0])
        h_o = Text("Ω", font_size=32, color=C_PUR, weight=BOLD).move_to([RX, 2.55, 0])

        div1 = DashedLine([-1.6, -3.0, 0], [-1.6, 3.0, 0],
                           color=C_MGR, stroke_width=0.8, stroke_opacity=0.25)
        div2 = DashedLine([ 1.6, -3.0, 0], [ 1.6, 3.0, 0],
                           color=C_MGR, stroke_width=0.8, stroke_opacity=0.25)
        self.play(FadeIn(h_d, h_q, h_o, div1, div2, run_time=0.8))

        # ── D column: bar chart ────────────────────────────────────────────
        neurons  = ["URXL", "URYVL", "CEP", "RMD", "RME", "AVJ", "AIZL", "AVJR"]
        delta_d  = [ 0.208,  0.149,   0.06,  0.01, -0.03, -0.10, -0.167, -0.150]
        N = len(neurons)
        bar_w    = 0.38
        bar_sc   = 3.8          # data unit → Manim units
        x0 = LX - (N * bar_w * 0.55)   # left edge of first bar

        bars  = VGroup()
        blbls = VGroup()
        for i, (lbl, dv) in enumerate(zip(neurons, delta_d)):
            bx    = x0 + i * bar_w * 1.12
            bh    = abs(dv) * bar_sc
            bot_y = MID_Y if dv >= 0 else MID_Y - bh
            col   = C_TEA if dv > 0 else C_ORG
            rect  = Rectangle(width=bar_w * 0.86, height=max(bh, 0.05),
                               color=col, fill_color=col, fill_opacity=0.8,
                               stroke_width=0)
            rect.align_to([bx, bot_y, 0], DOWN + LEFT)
            rect.shift(UP * (0 if dv >= 0 else 0))   # already aligned correctly
            rect.move_to([bx, bot_y + bh / 2, 0])
            bars.add(rect)
            tl = Text(lbl, font_size=11, color=C_LGR)
            tl.rotate(PI / 3)
            tl.move_to([bx, MID_Y - 0.58, 0])
            blbls.add(tl)

        zero_ln = Line([x0 - 0.1, MID_Y, 0], [x0 + N * bar_w * 1.12, MID_Y, 0],
                        color=C_MGR, stroke_width=0.9, stroke_opacity=0.55)

        cue1 = self.cue_text(
            "D reorganizes:  aerotaxis sensors ↑ roaming   /   olfactory & reversal ↑ dwelling",
            color=C_TEA, size=20)
        self.play(FadeIn(zero_ln),
                  LaggedStart(*[GrowFromEdge(b, DOWN if d >= 0 else UP)
                                for b, d in zip(bars, delta_d)], lag_ratio=0.06, run_time=1.6),
                  FadeIn(blbls, cue1))
        self.wait(2.0)
        self.play(bars.animate.set_opacity(0.3), blbls.animate.set_opacity(0.15))

        # ── Q column: module diagram ───────────────────────────────────────
        cue2 = self.cue_text(
            "Q reorganizes:  DA_mech ↔ URY_URX conditional coupling changes between states",
            color=C_ORG, size=20)

        nd1 = Circle(radius=0.52, color=C_ORG,
                     fill_color=C_ORG, fill_opacity=0.2, stroke_width=2.5)
        nd1.move_to([MX - 1.2, MID_Y, 0])
        nd2 = Circle(radius=0.52, color=C_ORG,
                     fill_color=C_ORG, fill_opacity=0.2, stroke_width=2.5)
        nd2.move_to([MX + 1.2, MID_Y, 0])

        l1 = Text("DA\nmech", font_size=17, color=C_ORG, line_spacing=0.75)
        l1.move_to(nd1)
        l2 = Text("URY\nURX",  font_size=17, color=C_ORG, line_spacing=0.75)
        l2.move_to(nd2)

        edge_thin  = Line(nd1.get_right(), nd2.get_left(),
                           color=C_ORG, stroke_width=1.5, stroke_opacity=0.4)
        edge_thick = Line(nd1.get_right(), nd2.get_left(),
                           color=C_ORG, stroke_width=6.0, stroke_opacity=0.9)

        auroc = Text("AUROC = 0.556\nPDF-signaling enriched",
                     font_size=16, color=C_ORG, line_spacing=0.85)
        auroc.next_to(nd2, UR, buff=0.2)

        self.play(FadeIn(nd1, nd2, l1, l2, edge_thin),
                  ReplacementTransform(cue1, cue2))
        self.wait(0.5)
        self.play(Transform(edge_thin, edge_thick, run_time=1.2), FadeIn(auroc))
        self.wait(2.0)
        self.play(VGroup(nd1, nd2, l1, l2, edge_thin, auroc).animate.set_opacity(0.3))

        # ── Ω column: rank-correlation visual ─────────────────────────────
        cue3 = self.cue_text(
            "ΔΩ ≈ ΔQ  (ρ = 0.9999)  —  z-scoring forces D ≈ I",
            color=C_PUR, size=22)

        N_R = 7
        ys = np.linspace(1.8, -1.6, N_R)
        lx = RX - 1.5
        rx = RX + 0.9

        hdr_l = Text("ΔQ rank", font_size=16, color=C_ORG).move_to([lx, 2.2, 0])
        hdr_r = Text("ΔΩ rank", font_size=16, color=C_PUR).move_to([rx, 2.2, 0])

        rank_segs = VGroup(*[
            Line([lx, float(y), 0], [rx, float(y), 0],
                 color=C_LGR, stroke_width=1.4, stroke_opacity=0.55)
            for y in ys])
        dots_l = VGroup(*[Dot([lx, float(y), 0], radius=0.09, color=C_ORG) for y in ys])
        dots_r = VGroup(*[Dot([rx, float(y), 0], radius=0.09, color=C_PUR) for y in ys])

        rho_lbl = Text("ρ = 0.9999", font_size=26, color=C_PUR, weight=BOLD)
        rho_lbl.move_to([RX, -2.2, 0])

        self.play(FadeIn(hdr_l, hdr_r),
                  LaggedStart(*[Create(s) for s in rank_segs], lag_ratio=0.06, run_time=1.0),
                  LaggedStart(*[FadeIn(d) for d in dots_l], lag_ratio=0.06),
                  LaggedStart(*[FadeIn(d) for d in dots_r], lag_ratio=0.06),
                  ReplacementTransform(cue2, cue3))
        self.play(Write(rho_lbl))
        self.wait(1.8)

        # ── Convergence arrow ──────────────────────────────────────────────
        conv_arr = Arrow([RX - 0.2, -2.8, 0], [MX + 0.2, -2.8, 0],
                          color=C_PUR, stroke_width=2.5, buff=0,
                          max_tip_length_to_length_ratio=0.18)
        conv_lbl = Text("reduces to →", font_size=18, color=C_LGR)
        conv_lbl.next_to(conv_arr, UP, buff=0.12)
        self.play(Create(conv_arr, run_time=1.0), FadeIn(conv_lbl))
        self.wait(1.2)

        # ── Honest summary ─────────────────────────────────────────────────
        self.play(FadeOut(VGroup(
            h_d, h_q, h_o, div1, div2,
            bars, blbls, zero_ln,
            nd1, nd2, l1, l2, edge_thin, auroc,
            hdr_l, hdr_r, rank_segs, dots_l, dots_r, rho_lbl,
            conv_arr, conv_lbl, cue3), run_time=0.9))

        lines = [
            Text(
                "In this dataset, current does not add significant biological information",
                font_size=27, color=WHITE),
            Text(
                "beyond precision for the PDF-modulated case.",
                font_size=27, color=WHITE),
            Text("Primary object:  ΔQ", font_size=36, color=C_YEL, weight=BOLD),
            Text(
                "Ω ≠ Q in general — only when D ≈ I after preprocessing (e.g. z-scoring)",
                font_size=18, color=C_LGR, slant=ITALIC),
        ]
        summary = VGroup(*lines).arrange(DOWN, buff=0.48).move_to([0, 0.15, 0])

        for i, line in enumerate(lines):
            self.play(FadeIn(line, shift=UP * 0.15, run_time=0.85))
            if i == 2:
                self.wait(0.4)

        self.wait(3.5)
        self.play(FadeOut(VGroup(hd, nlbl, summary), run_time=1.2))
