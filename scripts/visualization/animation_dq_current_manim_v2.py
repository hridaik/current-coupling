"""
Animation 4 v2 — From Precision to Current  (PHASE VIS-1D)
Conceptual refinement pass.
Output: results/visualization/dq_to_current_animation_v2.mp4
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
C_DGR = ManimColor("#1A1A28")
C_MGR = ManimColor("#555566")
C_LGR = ManimColor("#888899")

# ── Shared math ───────────────────────────────────────────────────────────────
COV  = np.array([[2.0, 1.2], [1.2, 1.0]])
PREC = np.linalg.inv(COV)
A_SK = np.array([[0.0, -0.7], [0.7, 0.0]])    # antisymmetric (circulating) drift


def make_ellipse(cov, scale=1.5, **kw):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.arctan2(float(vecs[1, 0]), float(vecs[0, 0]))
    w = 2 * scale * float(np.sqrt(max(vals[0], 1e-9)))
    h = 2 * scale * float(np.sqrt(max(vals[1], 1e-9)))
    ell = Ellipse(width=w, height=h, **kw)
    ell.rotate(angle)
    return ell


def make_flow(A, nx=7, ny=5, xr=(-3.0, 3.0), yr=(-2.0, 2.0),
              alen=0.28, cx=0.0, cy=0.0, color=C_PUR, alpha=0.55):
    grp = VGroup()
    for x in np.linspace(*xr, nx):
        for y in np.linspace(*yr, ny):
            pos = np.array([x, y])
            vel = A @ pos
            spd = np.linalg.norm(vel)
            if spd < 0.05:
                continue
            tip = pos + vel / spd * alen
            arr = Arrow(
                start=[cx + x, cy + y, 0],
                end=[cx + float(tip[0]), cy + float(tip[1]), 0],
                buff=0, color=color, stroke_width=1.8,
                max_tip_length_to_length_ratio=0.38,
            )
            arr.set_stroke(opacity=alpha)
            grp.add(arr)
    return grp


def sim_ou(starts, A_extra=None, n=200, dt=0.06, sig=0.10, seed=77):
    rng = np.random.default_rng(seed)
    out = []
    for s0 in starts:
        pos = s0.copy()
        tr = [pos.copy()]
        for _ in range(n):
            d = -0.38 * pos + (pos @ A_extra.T if A_extra is not None else 0)
            pos = pos + d * dt + rng.multivariate_normal([0, 0], np.eye(2) * sig) * np.sqrt(dt)
            tr.append(pos.copy())
        out.append(tr)
    return out


def make_path(traj, cx=0, cy=0, color=C_BLU, width=1.8, alpha=0.7):
    vmo = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=alpha)
    vmo.set_points_smoothly([[cx + float(p[0]), cy + float(p[1]), 0] for p in traj])
    return vmo


# ── Scene ─────────────────────────────────────────────────────────────────────
class DQCurrentAnimation(Scene):

    def setup(self):
        self.camera.background_color = BG
        self.rng = np.random.default_rng(42)

    def construct(self):
        self.title_card()
        self.scene1_q()
        self.scene2_d()
        self.scene3_omega()
        self.scene4_combine()
        self.scene5_worm()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def cue(self, s, color=C_LGR, sz=23, italic=True):
        t = Text(s, font_size=sz, color=color,
                 slant=ITALIC if italic else NORMAL)
        t.to_edge(DOWN, buff=0.48)
        return t

    def scene_hdr(self, s, n):
        h = Text(s, font_size=34, color=WHITE, weight=BOLD)
        h.to_edge(UP, buff=0.38)
        n_lbl = Text(f"{n} / 5", font_size=14, color=C_MGR)
        n_lbl.to_corner(UL, buff=0.26)
        return h, n_lbl

    def dots(self, n=155, cov=None):
        pts = self.rng.multivariate_normal([0, 0], cov if cov is not None else COV, n)
        return VGroup(*[
            Dot([float(p[0]), float(p[1]), 0], radius=0.04,
                color=C_BLU, fill_opacity=0.42)
            for p in pts])

    # ── Title ─────────────────────────────────────────────────────────────────

    def title_card(self):
        t1 = Text("From Precision to Current",
                  font_size=52, color=WHITE, weight=BOLD)
        t2 = Text("D,   Q,   and Ω   in a stochastic system",
                  font_size=26, color=C_ORG)
        t2.next_to(t1, DOWN, buff=0.5)
        g = VGroup(t1, t2).move_to(ORIGIN)
        self.play(FadeIn(g, run_time=1.2))
        self.wait(2.0)
        self.play(FadeOut(g, run_time=0.9))

    # ── Scene 1: Q ────────────────────────────────────────────────────────────

    def scene1_q(self):
        hd, nl = self.scene_hdr("What Q sees", "1")
        self.play(FadeIn(hd, nl, run_time=0.7))

        # Axes with biological labels
        ax = Axes(
            x_range=[-4, 4, 1], y_range=[-3, 3, 1],
            x_length=9.0, y_length=6.0,
            axis_config={"color": C_MGR, "stroke_width": 1.1,
                         "include_ticks": False},
        ).move_to([0, -0.15, 0])
        xl = Text("Neuron 1 activity", font_size=19, color=C_LGR)
        xl.next_to(ax.x_axis, DOWN, buff=0.22)
        yl = Text("Neuron 2 activity", font_size=19, color=C_LGR)
        yl.next_to(ax.y_axis, LEFT, buff=0.20).rotate(PI / 2)

        self.play(Create(ax, run_time=0.9), FadeIn(xl, yl))

        # Cloud
        cloud = self.dots()
        c1 = self.cue("Each point = one moment in time", italic=False, color=C_LGR)
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in cloud],
                        lag_ratio=0.007, run_time=2.4),
            FadeIn(c1))
        self.wait(1.0)

        # Covariance ellipse
        c_ell = make_ellipse(COV, scale=1.5, color=C_LGR,
                             fill_opacity=0, stroke_width=2.0)
        c_ell.set_stroke(opacity=0.55)
        c2 = self.cue("Covariance  —  where states tend to scatter")
        self.play(Create(c_ell, run_time=1.8), ReplacementTransform(c1, c2))
        self.wait(1.0)

        # Precision ellipse — stays visible from here onward
        p_ell = make_ellipse(PREC, scale=1.2, color=C_ORG,
                             fill_opacity=0, stroke_width=3.0)
        p_ell.set_z_index(5)
        c3 = self.cue("Precision Q = Σ⁻¹  —  short axis = tight constraint",
                      color=C_ORG, sz=21)
        self.play(Create(p_ell, run_time=2.0), ReplacementTransform(c2, c3))
        self.wait(1.0)

        # Axis labels — placed outside ellipse with pointer arrows
        vals, vecs = np.linalg.eigh(PREC)
        idx = vals.argsort()[::-1]
        vals, vecs = vals[idx], vecs[:, idx]
        s_tip = vecs[:, 0] * 1.2 * float(np.sqrt(vals[0]))
        w_tip = vecs[:, 1] * 1.2 * float(np.sqrt(vals[1]))

        def lbl_pos(tip, off=1.55):
            d = tip / (np.linalg.norm(tip) + 1e-9)
            p = tip + d * off
            p[0] = float(np.clip(p[0], -5.5, 5.5))
            p[1] = float(np.clip(p[1], -2.5, 2.5))
            return [p[0], p[1], 0]

        lb_s = Text("Large Q\nStrong constraint", font_size=19, color=C_ORG,
                    line_spacing=0.8).move_to(lbl_pos(s_tip))
        lb_w = Text("Small Q\nAlmost free", font_size=19, color=C_TEA,
                    line_spacing=0.8).move_to(lbl_pos(w_tip))
        ar_s = Arrow(lb_s.get_center(),
                     [float(s_tip[0]) * 0.88, float(s_tip[1]) * 0.88, 0],
                     buff=0.28, color=C_ORG, stroke_width=1.3,
                     max_tip_length_to_length_ratio=0.22)
        ar_w = Arrow(lb_w.get_center(),
                     [float(w_tip[0]) * 0.88, float(w_tip[1]) * 0.88, 0],
                     buff=0.28, color=C_TEA, stroke_width=1.3,
                     max_tip_length_to_length_ratio=0.22)

        self.play(FadeIn(lb_s, ar_s, run_time=0.8))
        self.wait(0.3)
        self.play(FadeIn(lb_w, ar_w, run_time=0.8))
        self.wait(1.5)

        c4 = self.cue("Q describes which combinations of activity are constrained.",
                      color=WHITE, sz=25, italic=False)
        self.play(ReplacementTransform(c3, c4))
        self.wait(2.8)

        self.play(FadeOut(
            VGroup(hd, nl, ax, xl, yl, cloud, c_ell, p_ell,
                   lb_s, lb_w, ar_s, ar_w, c4), run_time=1.0))
        self.wait(0.2)

    # ── Scene 2: D ────────────────────────────────────────────────────────────

    def scene2_d(self):
        hd, nl = self.scene_hdr("What D sees", "2")
        self.play(FadeIn(hd, nl, run_time=0.7))

        # Light axes for context
        ax = Axes(
            x_range=[-4, 4, 1], y_range=[-3, 3, 1],
            x_length=9.0, y_length=6.0,
            axis_config={"color": C_DGR, "stroke_width": 0.8,
                         "include_ticks": False},
        ).move_to([0, -0.15, 0])
        ghost = make_ellipse(COV, scale=1.5, color=C_LGR,
                             fill_opacity=0, stroke_width=1.5)
        ghost.set_stroke(opacity=0.28)
        g_lbl = Text("Stationary distribution (fixed)", font_size=16, color=C_MGR)
        g_lbl.to_corner(UR, buff=0.45).shift(DOWN * 0.3)

        c0 = self.cue("D describes fluctuations entering the system.",
                      color=WHITE, sz=25, italic=False)
        self.play(Create(ax, run_time=0.6), Create(ghost, run_time=0.8),
                  FadeIn(g_lbl, c0))
        self.wait(1.2)

        # Five state positions
        pos5 = [[-1.1, 0.5], [0.9, 0.7], [1.2, -0.6], [-0.4, -0.8], [0.1, 0.1]]
        sdots = VGroup(*[Dot([p[0], p[1], 0], radius=0.10,
                              color=C_BLU, fill_opacity=0.9) for p in pos5])
        self.play(LaggedStart(*[FadeIn(d) for d in sdots],
                              lag_ratio=0.12, run_time=0.9))
        self.wait(0.5)

        D_ISO   = np.eye(2) * 0.36
        D_ANI   = np.diag([0.10, 0.72])
        D_CORR  = np.array([[0.45, 0.38], [0.38, 0.45]])
        cases   = [
            (D_ISO,  "Isotropic D  —  kicks arrive equally in all directions"),
            (D_ANI,  "Anisotropic D  —  kicks arrive mainly along one axis"),
            (D_CORR, "Correlated D  —  kicks in x₁ and x₂ tend to arrive together"),
        ]

        def kick_group(D_mat):
            rng2 = np.random.default_rng(5)
            grp = VGroup()
            for p in pos5:
                for k in rng2.multivariate_normal([0, 0], D_mat, 6) * 1.2:
                    if np.linalg.norm(k) < 0.06:
                        continue
                    a = Arrow(
                        start=[p[0], p[1], 0],
                        end=[p[0] + float(k[0]), p[1] + float(k[1]), 0],
                        buff=0, color=C_TEA, stroke_width=1.6,
                        max_tip_length_to_length_ratio=0.45)
                    a.set_stroke(opacity=0.72)
                    grp.add(a)
                # Faint envelope ellipse
                e = make_ellipse(D_mat, scale=1.1, color=C_TEA,
                                 fill_opacity=0, stroke_width=1.1)
                e.set_stroke(opacity=0.28).shift(np.array([p[0], p[1], 0]))
                grp.add(e)
            return grp

        cur_grp, cur_cue = None, c0
        for D_mat, label in cases:
            grp = kick_group(D_mat)
            nc  = self.cue(label, color=C_TEA, sz=22)
            if cur_grp is None:
                self.play(
                    LaggedStart(*[Create(a) for a in grp],
                                lag_ratio=0.025, run_time=1.4),
                    ReplacementTransform(cur_cue, nc))
            else:
                self.play(FadeOut(cur_grp, run_time=0.5))
                self.play(
                    LaggedStart(*[Create(a) for a in grp],
                                lag_ratio=0.025, run_time=1.3),
                    ReplacementTransform(cur_cue, nc))
            self.wait(2.2)
            cur_grp, cur_cue = grp, nc

        cs = self.cue("D tells us where fluctuations enter  —  the density is unchanged",
                      color=WHITE, sz=23, italic=False)
        self.play(ReplacementTransform(cur_cue, cs))
        self.wait(2.5)

        self.play(FadeOut(
            VGroup(hd, nl, ax, ghost, g_lbl, sdots, cur_grp, cs),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 3: Ω ────────────────────────────────────────────────────────────

    def scene3_omega(self):
        hd, nl = self.scene_hdr("What Ω sees", "3")
        self.play(FadeIn(hd, nl, run_time=0.7))

        LX, RX = -3.3, 3.3
        eL = make_ellipse(COV, scale=1.35, color=C_LGR,
                          fill_opacity=0, stroke_width=1.8).shift(LEFT * 3.3)
        eR = make_ellipse(COV, scale=1.35, color=C_LGR,
                          fill_opacity=0, stroke_width=1.8).shift(RIGHT * 3.3)
        eL.set_stroke(opacity=0.45); eR.set_stroke(opacity=0.45)
        div = DashedLine([0, -3.0, 0], [0, 3.0, 0],
                         color=C_MGR, stroke_width=1.0, stroke_opacity=0.3)

        lL = Text("Equilibrium\nΩ = 0",    font_size=26, color=WHITE,  line_spacing=0.85)
        lL.move_to([LX, 2.85, 0])
        lR = Text("Non-equilibrium\nΩ ≠ 0", font_size=26, color=C_PUR, line_spacing=0.85)
        lR.move_to([RX, 2.85, 0])
        same = Text("Same density on both sides",
                    font_size=18, color=C_LGR).move_to([0, -2.75, 0])

        c1 = self.cue("Both systems visit the same states  —  same stationary density")
        self.play(Create(eL, run_time=0.8), Create(eR, run_time=0.8),
                  FadeIn(div, lL, lR, same, c1))
        self.wait(1.0)

        # Flow arrows on right only
        arrows = make_flow(A_SK, nx=7, ny=5, xr=(-2.6, 2.6), yr=(-1.8, 1.8),
                           alen=0.26, cx=RX, cy=0, color=C_PUR, alpha=0.52)
        no_flow = Text("No net flow", font_size=20, color=C_LGR).move_to([LX, 0.0, 0])
        c2 = self.cue("Same density  —  but one system takes directed routes",
                      color=C_PUR, sz=24)
        self.play(
            LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.02, run_time=1.4),
            FadeIn(no_flow), ReplacementTransform(c1, c2))
        self.wait(1.0)

        # Particle paths
        rng2 = np.random.default_rng(7)
        starts = rng2.multivariate_normal([0, 0], COV * 0.12, 4)
        trE = sim_ou(starts, n=160, dt=0.07, sig=0.10)
        trC = sim_ou(starts, A_extra=A_SK, n=160, dt=0.07, sig=0.07)
        pL = VGroup(*[make_path(t, cx=LX, color=C_BLU,  width=1.6) for t in trE])
        pR = VGroup(*[make_path(t, cx=RX, color=C_PUR, width=1.6) for t in trC])
        c3 = self.cue("Left: bounces randomly.   Right: takes directed routes.",
                      color=C_LGR, sz=22)
        self.play(ReplacementTransform(c2, c3))
        self.play(
            LaggedStart(*[Create(p, run_time=3.0) for p in pL], lag_ratio=0.18),
            LaggedStart(*[Create(p, run_time=3.0) for p in pR], lag_ratio=0.18),
        )
        self.wait(0.8)

        c4 = self.cue("Same states visited.   Different routes through those states.",
                      color=WHITE, sz=26, italic=False)
        self.play(ReplacementTransform(c3, c4))
        self.wait(2.5)

        c5 = self.cue("Ω is movement,  not occupancy.",
                      color=C_PUR, sz=28, italic=False)
        self.play(ReplacementTransform(c4, c5))
        self.wait(2.0)

        self.play(FadeOut(
            VGroup(hd, nl, eL, eR, div, lL, lR, same, no_flow,
                   arrows, pL, pR, c5), run_time=1.0))
        self.wait(0.2)

    # ── Scene 4: Ω = DQ + A ───────────────────────────────────────────────────

    def scene4_combine(self):
        eq_hd = Text("Ω = DQ + A", font_size=46, color=WHITE, weight=BOLD)
        eq_hd.to_edge(UP, buff=0.38)
        nl = Text("4 / 5", font_size=14, color=C_MGR).to_corner(UL, buff=0.26)
        self.play(FadeIn(eq_hd, nl, run_time=0.7))

        LX, MX, RX, CY = -4.4, 0.0, 4.4, 0.15
        hQ = Text("Q", font_size=42, color=C_ORG, weight=BOLD).move_to([LX, 2.65, 0])
        hD = Text("D", font_size=42, color=C_TEA, weight=BOLD).move_to([MX, 2.65, 0])
        hO = Text("Ω", font_size=42, color=C_PUR, weight=BOLD).move_to([RX, 2.65, 0])
        tx = Text("×", font_size=34, color=C_MGR).move_to([-2.1, CY, 0])
        te = Text("=", font_size=34, color=C_MGR).move_to([ 2.1, CY, 0])
        self.play(FadeIn(hQ, hD, hO, tx, te, run_time=0.9))

        # Q panel: precision ellipse = geometry
        qe = make_ellipse(PREC, scale=1.3, color=C_ORG,
                          fill_opacity=0, stroke_width=2.8).shift([LX, CY, 0])
        qs = Text("Geometry of\nconstraint", font_size=19, color=C_ORG,
                  line_spacing=0.8).move_to([LX, CY - 2.05, 0])
        c1 = self.cue("Q tells us where states relate", color=C_ORG, sz=25)
        self.play(Create(qe, run_time=1.5), FadeIn(qs, c1))
        self.wait(1.2)

        # D panel: kick arrows = fluctuation input
        rng3 = np.random.default_rng(5)
        d_pos = [[-0.9, 0.6], [0.7, 0.5], [0.8, -0.5], [-0.5, -0.6], [0.0, 0.0]]
        D0 = np.eye(2) * 0.4
        d_grp = VGroup()
        for p in d_pos:
            for k in rng3.multivariate_normal([0, 0], D0, 5) * 1.1:
                if np.linalg.norm(k) < 0.05:
                    continue
                a = Arrow(
                    start=[MX + p[0], CY + p[1], 0],
                    end=[MX + p[0] + float(k[0]), CY + p[1] + float(k[1]), 0],
                    buff=0, color=C_TEA, stroke_width=1.5,
                    max_tip_length_to_length_ratio=0.45)
                a.set_stroke(opacity=0.68)
                d_grp.add(a)
        blob = make_ellipse(D0 * 3, scale=1.0, color=C_TEA,
                            fill_color=C_TEA, fill_opacity=0.12,
                            stroke_width=1.4).shift([MX, CY, 0])
        ds = Text("Fluctuation\ninput", font_size=19, color=C_TEA,
                  line_spacing=0.8).move_to([MX, CY - 2.05, 0])
        c2 = self.cue("D tells us where fluctuations enter", color=C_TEA, sz=25)
        self.play(
            LaggedStart(*[Create(a) for a in d_grp], lag_ratio=0.03, run_time=1.3),
            Create(blob, run_time=0.9),
            FadeIn(ds), ReplacementTransform(c1, c2))
        self.wait(1.2)

        # Ω panel: FLOW FIELD — not an ellipse
        A_om = A_SK * 0.55 - np.eye(2) * 0.25   # spiral inward while circulating
        om_flow = make_flow(A_om, nx=5, ny=5, xr=(-2.0, 2.0), yr=(-1.6, 1.6),
                            alen=0.30, cx=RX, cy=CY, color=C_PUR, alpha=0.62)
        os = Text("Flow through\nstate space", font_size=19, color=C_PUR,
                  line_spacing=0.8).move_to([RX, CY - 2.05, 0])
        c3 = self.cue("Ω tells us how activity moves through state space",
                      color=C_PUR, sz=25)
        self.play(
            LaggedStart(*[Create(a) for a in om_flow], lag_ratio=0.04, run_time=1.4),
            FadeIn(os), ReplacementTransform(c2, c3))
        self.wait(1.5)

        # Metaphor
        self.play(FadeOut(
            VGroup(hQ, hD, hO, tx, te, qe, qs, d_grp, blob, ds, om_flow, os, c3),
            run_time=0.9))
        meta = VGroup(
            Text("Q  =  road map",             font_size=30, color=C_ORG),
            Text("D  =  traffic volume",       font_size=30, color=C_TEA),
            Text("Ω  =  traffic organization", font_size=30, color=C_PUR),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to([0, 0.1, 0])
        c4 = self.cue("Same road map.  Different traffic.  Different flow.",
                      color=WHITE, sz=26, italic=False)
        self.play(FadeIn(c4))
        self.play(LaggedStart(*[Write(m) for m in meta], lag_ratio=0.38, run_time=2.2))
        self.wait(2.5)
        self.play(FadeOut(VGroup(eq_hd, nl, meta, c4), run_time=1.0))
        self.wait(0.2)

    # ── Scene 5: Worm ─────────────────────────────────────────────────────────

    def scene5_worm(self):
        hd, nl = self.scene_hdr("In C. elegans", "5")
        self.play(FadeIn(hd, nl, run_time=0.7))

        # ── Beat 1: D  ────────────────────────────────────────────────────
        self._worm_D()
        # ── Beat 2: Q  ────────────────────────────────────────────────────
        self._worm_Q()
        # ── Beat 3: Ω summary  ────────────────────────────────────────────
        self._worm_Omega()
        # ── Beat 4: Final card  ───────────────────────────────────────────
        self._final_card(hd, nl)

    def _worm_D(self):
        """DWELLING vs ROAMING bar chart, biological function labels."""
        groups   = ["Gas\nsensing", "Food\nsensing", "Motor\ncontrol", "Local\nsearch"]
        dwell_v  = np.array([0.30, 0.38, 0.40, 0.40])
        roam_v   = np.array([0.48, 0.42, 0.39, 0.24])

        ttl = Text("D  —  Innovation variance by functional group",
                   font_size=24, color=C_TEA, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        N = len(groups)
        bw   = 0.50
        gap  = 0.10
        gw   = 2 * bw + gap
        x0   = -(N * gw) / 2 + gw / 2
        yb   = -1.3
        sc   = 3.4

        bars = VGroup()
        lbls = VGroup()
        for i, (g, dv, rv) in enumerate(zip(groups, dwell_v, roam_v)):
            gx = x0 + i * gw
            dh, rh = float(dv * sc), float(rv * sc)

            db = Rectangle(width=float(bw * 0.86), height=dh,
                           color=C_ORG, fill_color=C_ORG,
                           fill_opacity=0.82, stroke_width=0)
            db.move_to([gx - bw / 2 - gap / 2, yb + dh / 2, 0])

            rb = Rectangle(width=float(bw * 0.86), height=rh,
                           color=C_TEA, fill_color=C_TEA,
                           fill_opacity=0.82, stroke_width=0)
            rb.move_to([gx + bw / 2 + gap / 2, yb + rh / 2, 0])

            bars.add(db, rb)
            gl = Text(g, font_size=16, color=C_LGR, line_spacing=0.75)
            gl.move_to([gx, yb - 0.55, 0])
            lbls.add(gl)

        # Legend
        leg = VGroup(
            VGroup(Square(0.18, color=C_ORG, fill_color=C_ORG,
                          fill_opacity=0.9, stroke_width=0),
                   Text("Dwelling", font_size=17, color=C_ORG)).arrange(RIGHT, buff=0.14),
            VGroup(Square(0.18, color=C_TEA, fill_color=C_TEA,
                          fill_opacity=0.9, stroke_width=0),
                   Text("Roaming", font_size=17, color=C_TEA)).arrange(RIGHT, buff=0.14),
        ).arrange(RIGHT, buff=0.55).to_corner(UR, buff=0.42)

        zl = Line([x0 - gw * 0.5, yb, 0], [x0 + N * gw, yb, 0],
                  color=C_MGR, stroke_width=0.9, stroke_opacity=0.5)

        c1 = self.cue(
            "Gas sensing fluctuates more during roaming.   "
            "Local search fluctuates more during dwelling.",
            color=C_TEA, sz=20)

        self.play(FadeIn(zl, leg))
        self.play(
            LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.06, run_time=1.5),
            FadeIn(lbls, c1))
        self.wait(1.5)

        msg = Text("D reorganizes between states.", font_size=26,
                   color=C_TEA, weight=BOLD).move_to([0, 2.45, 0])
        self.play(Transform(ttl, msg, run_time=0.8))
        self.wait(1.8)

        self.play(FadeOut(VGroup(ttl, bars, lbls, zl, leg, c1), run_time=0.9))
        self.wait(0.15)

    def _worm_Q(self):
        """DWELLING vs ROAMING network diagrams, functional labels."""
        ttl = Text("Q  —  Conditional coupling between functional groups",
                   font_size=24, color=C_ORG, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        LX, RX, QY = -2.5, 2.5, 0.25

        def net(cx, state_col, edge_lw, state_lbl, state_lbl_col):
            nd1 = Circle(radius=0.52, color=C_ORG, fill_color=C_ORG,
                         fill_opacity=0.20, stroke_width=2.0).move_to([cx - 1.2, QY, 0])
            nd2 = Circle(radius=0.52, color=C_ORG, fill_color=C_ORG,
                         fill_opacity=0.20, stroke_width=2.0).move_to([cx + 1.2, QY, 0])
            l1 = Text("Food\nsensing", font_size=15, color=C_ORG,
                      line_spacing=0.75).move_to(nd1)
            l2 = Text("Gas\nsensing",  font_size=15, color=C_ORG,
                      line_spacing=0.75).move_to(nd2)
            edge = Line(nd1.get_right(), nd2.get_left(),
                        color=C_ORG, stroke_width=edge_lw, stroke_opacity=0.88)
            sl = Text(state_lbl, font_size=20, color=state_lbl_col, weight=BOLD)
            sl.move_to([cx, QY + 1.4, 0])
            return VGroup(nd1, nd2, l1, l2, edge, sl)

        g_dwell = net(LX, C_ORG, 1.8, "DWELLING", C_LGR)
        g_roam  = net(RX, C_ORG, 6.5, "ROAMING",  C_TEA)
        div = DashedLine([0, -1.8, 0], [0, 2.0, 0],
                         color=C_MGR, stroke_width=0.8, stroke_opacity=0.28)

        lbl_dwell = Text("Weak coupling", font_size=17, color=C_LGR)
        lbl_dwell.move_to([LX, QY - 1.4, 0])
        lbl_roam  = Text("Stronger coupling", font_size=17, color=C_ORG)
        lbl_roam.move_to([RX, QY - 1.4, 0])

        c2 = self.cue(
            "Food sensing ↔ Gas sensing:  conditional coupling strengthens during roaming.",
            color=C_ORG, sz=21)
        self.play(FadeIn(g_dwell, g_roam, div, lbl_dwell, lbl_roam, c2))
        self.wait(2.0)

        msg = Text("Q reorganizes between states.", font_size=26,
                   color=C_ORG, weight=BOLD).move_to([0, 2.45, 0])
        self.play(Transform(ttl, msg, run_time=0.8))
        self.wait(1.8)

        self.play(FadeOut(
            VGroup(ttl, g_dwell, g_roam, div, lbl_dwell, lbl_roam, c2),
            run_time=0.9))
        self.wait(0.15)

    def _worm_Omega(self):
        """Ω summary: combines D and Q, same biological conclusion."""
        ttl = Text("Ω  —  Incorporates both reorganizations",
                   font_size=24, color=C_PUR, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        ck_d = Text("D reorganizes  ✓", font_size=24, color=C_TEA)
        ck_q = Text("Q reorganizes  ✓", font_size=24, color=C_ORG)
        ck_o = Text("Ω = DQ + A  combines both", font_size=24, color=C_PUR)
        VGroup(ck_d, ck_q, ck_o).arrange(DOWN, buff=0.42,
                                          aligned_edge=LEFT).move_to([-2.0, 0.2, 0])

        box = RoundedRectangle(width=5.2, height=1.5, corner_radius=0.22,
                               color=C_PUR, fill_color=C_DGR,
                               fill_opacity=0.5, stroke_width=2.0).move_to([3.1, 0.2, 0])
        box_txt = Text("Same biological\ninterpretation",
                       font_size=22, color=WHITE, line_spacing=0.85).move_to(box)

        arr = Arrow([-0.3, 0.2, 0], [1.45, 0.2, 0],
                    buff=0, color=C_PUR, stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.2)

        c3 = self.cue(
            "The current formulation incorporates both reorganizations.",
            color=C_PUR, sz=22)

        self.play(FadeIn(c3))
        self.play(FadeIn(ck_d, shift=RIGHT * 0.2, run_time=0.7))
        self.play(FadeIn(ck_q, shift=RIGHT * 0.2, run_time=0.7))
        self.play(FadeIn(ck_o, shift=RIGHT * 0.2, run_time=0.7))
        self.wait(0.6)
        self.play(Create(box, run_time=0.8), FadeIn(box_txt))
        self.play(Create(arr, run_time=0.6))
        self.wait(1.0)

        c4 = self.cue(
            "In this dataset, it does not change the biological conclusion.",
            color=WHITE, sz=23, italic=False)
        self.play(ReplacementTransform(c3, c4))
        self.wait(2.2)

        self.play(FadeOut(
            VGroup(ttl, ck_d, ck_q, ck_o, box, box_txt, arr, c4),
            run_time=0.9))
        self.wait(0.15)

    def _final_card(self, hd, nl):
        """Final summary card."""
        rows = VGroup(
            VGroup(Text("D:", font_size=28, color=C_TEA, weight=BOLD),
                   Text("Which neurons become dynamically variable?",
                        font_size=24, color=WHITE)).arrange(RIGHT, buff=0.4),
            VGroup(Text("Q:", font_size=28, color=C_ORG, weight=BOLD),
                   Text("Which neurons become conditionally linked?",
                        font_size=24, color=WHITE)).arrange(RIGHT, buff=0.4),
            VGroup(Text("Ω:", font_size=28, color=C_PUR, weight=BOLD),
                   Text("Combines both reorganizations.",
                        font_size=24, color=WHITE)).arrange(RIGHT, buff=0.4),
        ).arrange(DOWN, buff=0.44, aligned_edge=LEFT).move_to([0, 0.85, 0])

        result = VGroup(
            Text("Result:", font_size=22, color=C_YEL, weight=BOLD),
            Text("Same biological interpretation for the PDF-associated circuit.",
                 font_size=22, color=WHITE),
        ).arrange(RIGHT, buff=0.3).move_to([0, -0.55, 0])

        footer = Text("Different mathematics.   Same biological conclusion.",
                      font_size=19, color=C_LGR, slant=ITALIC).move_to([0, -1.6, 0])

        for row in rows:
            self.play(FadeIn(row, shift=UP * 0.15, run_time=0.75))
        self.wait(0.4)
        self.play(FadeIn(result, shift=UP * 0.12, run_time=0.8))
        self.wait(0.4)
        self.play(FadeIn(footer, run_time=0.8))
        self.wait(3.8)

        self.play(FadeOut(VGroup(hd, nl, rows, result, footer), run_time=1.2))
