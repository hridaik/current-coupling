"""
Animation 4 v4 — From Precision to Current  (PHASE VIS-1F)
Geometry correction pass.

Changes from v3:
  S1  – Correct precision geometry.
        Single covariance ellipse only (no separate 'precision ellipse').
        SHORT axis = orange DoubleArrow = strongly constrained (large Q).
        LONG  axis = teal  DoubleArrow = weakly constrained  (small Q).
        Callout arrows from labels to axis tips, both labels outside the cloud.
        Axis labels ('Neuron 1/2 activity') moved to arrow tips via next_to.
  All – halo background-stroke reduced from 8 → 3 to prevent blurry text.
  S2  – axis labels already absent; no change needed.
"""

from manim import *
import numpy as np

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = ManimColor("#0F0F14")
C_BLU = ManimColor("#3D5A99")
C_ORG = ManimColor("#E07B39")   # Q / strongly-constrained annotation
C_TEA = ManimColor("#2A9D8F")   # D / weakly-constrained annotation
C_PUR = ManimColor("#8B5CF6")   # Ω / current
C_YEL = ManimColor("#F5C518")
C_DGR = ManimColor("#1A1A28")
C_MGR = ManimColor("#555566")
C_LGR = ManimColor("#888899")
C_DWL = ManimColor("#4895EF")   # dwelling state
C_ROM = ManimColor("#F92626")   # roaming state

# ── Shared math ───────────────────────────────────────────────────────────────
COV  = np.array([[2.0, 1.2], [1.2, 1.0]])
PREC = np.linalg.inv(COV)
A_SK = np.array([[0.0, -0.7], [0.7, 0.0]])

# Precompute COV eigenvectors once
_cov_vals, _cov_vecs = np.linalg.eigh(COV)   # ascending order
# _cov_vals[0] ≈ 0.2 → short axis → large Q → strongly constrained
# _cov_vals[1] ≈ 2.8 → long  axis → small Q → weakly constrained
SHORT_V = _cov_vecs[:, 0]   # [0.555, -0.832]
LONG_V  = _cov_vecs[:, 1]   # [-0.832, -0.555]  (eigh can flip signs)
SHORT_H = 1.5 * float(np.sqrt(_cov_vals[0]))   # 0.671
LONG_H  = 1.5 * float(np.sqrt(_cov_vals[1]))   # 2.510


def make_ellipse(cov, scale=1.5, **kw):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    ang = np.arctan2(float(vecs[1, 0]), float(vecs[0, 0]))
    w = 2 * scale * float(np.sqrt(max(vals[0], 1e-9)))
    h = 2 * scale * float(np.sqrt(max(vals[1], 1e-9)))
    e = Ellipse(width=w, height=h, **kw)
    e.rotate(ang)
    return e


def make_flow(A, nx=7, ny=5, xr=(-3.0, 3.0), yr=(-2.0, 2.0),
              alen=0.27, cx=0.0, cy=0.0, color=C_PUR, alpha=0.55):
    grp = VGroup()
    for x in np.linspace(*xr, nx):
        for y in np.linspace(*yr, ny):
            pos = np.array([x, y])
            vel = A @ pos
            spd = np.linalg.norm(vel)
            if spd < 0.05:
                continue
            tip = pos + vel / spd * alen
            arr = Arrow([cx+x, cy+y, 0], [cx+float(tip[0]), cy+float(tip[1]), 0],
                        buff=0, color=color, stroke_width=1.8,
                        max_tip_length_to_length_ratio=0.38)
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
            pos = pos + d*dt + rng.multivariate_normal([0,0], np.eye(2)*sig)*np.sqrt(dt)
            tr.append(pos.copy())
        out.append(tr)
    return out


def make_path(traj, cx=0, cy=0, color=C_BLU, width=1.8, alpha=0.7):
    vmo = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=alpha)
    vmo.set_points_smoothly([[cx+float(p[0]), cy+float(p[1]), 0] for p in traj])
    return vmo


def halo(txt, w=3):
    """Thin background stroke to keep labels readable over the data cloud."""
    txt.set_stroke(color=BG, width=w, background=True)
    return txt


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
        self.scene_bridge()
        self.scene_module_state_space()
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

    def cloud_dots(self, n=155):
        pts = self.rng.multivariate_normal([0, 0], COV, n)
        return VGroup(*[Dot([float(p[0]), float(p[1]), 0],
                             radius=0.04, color=C_BLU, fill_opacity=0.42)
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

    # ── Scene 1: Q — correct precision geometry ───────────────────────────────

    def scene1_q(self):
        hd, nl = self.scene_hdr("What Q sees", "1")
        self.play(FadeIn(hd, nl, run_time=0.7))

        # ── Coordinate axes with labels near the tips ──────────────────────
        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=9.0, y_length=6.0,
                  axis_config={"color": C_MGR, "stroke_width": 1.1,
                               "include_ticks": False}).move_to([0, -0.15, 0])

        # x-label: just below the positive-x arrow tip
        xl = Text("Neuron 1 activity", font_size=16, color=C_LGR)
        xl.next_to(ax.x_axis.get_right(), DOWN, buff=0.14)

        # y-label: just above the positive-y arrow tip (short enough to not crowd heading)
        yl = Text("Neuron 2 activity", font_size=16, color=C_LGR)
        yl.next_to(ax.y_axis.get_top(), UP, buff=0.07)

        self.play(Create(ax, run_time=0.9), FadeIn(xl, yl))

        # ── Gaussian cloud ─────────────────────────────────────────────────
        cloud = self.cloud_dots()
        c1 = self.cue("Each point = one moment in time",
                      italic=False, color=C_LGR)
        self.play(LaggedStart(*[FadeIn(d, scale=1.3) for d in cloud],
                              lag_ratio=0.007, run_time=2.4), FadeIn(c1))
        self.wait(1.0)

        # ── Covariance / confidence ellipse ────────────────────────────────
        # This is the 1.5 σ confidence contour — it IS the precision geometry.
        c_ell = make_ellipse(COV, scale=1.5, color=C_LGR,
                             fill_opacity=0, stroke_width=2.1)
        c_ell.set_stroke(opacity=0.68)
        c2 = self.cue("Covariance/confidence ellipse  —  where states tend to scatter")
        self.play(Create(c_ell, run_time=1.8), ReplacementTransform(c1, c2))
        self.wait(1.0)

        # ── Principal-axis annotations ─────────────────────────────────────
        # COV eigh (ascending): vals[0]=0.2 (short axis), vals[1]=2.8 (long axis)
        # SHORT axis: half-length 0.671, direction SHORT_V = [0.555, -0.832]
        #             → narrow spread → LARGE Q → STRONGLY constrained
        # LONG  axis: half-length 2.510, direction LONG_V  = [-0.832, -0.555]
        #             → broad spread  → SMALL Q → WEAKLY constrained

        sv = SHORT_V     # [0.555, -0.832]
        lv = LONG_V      # [-0.832, -0.555]
        sh = SHORT_H     # 0.671
        lh = LONG_H      # 2.510

        # DoubleArrow for SHORT axis — ORANGE (large Q, strongly constrained)
        # Short → visually narrow → reinforces "tight constraint"
        short_da = DoubleArrow(
            [-sv[0]*sh*1.10, -sv[1]*sh*1.10, 0],
            [ sv[0]*sh*1.10,  sv[1]*sh*1.10, 0],
            buff=0, color=C_ORG, stroke_width=2.6, tip_length=0.14)

        # DoubleArrow for LONG axis — TEAL (small Q, weakly constrained)
        # Long → visually wide → reinforces "loose constraint"
        long_da = DoubleArrow(
            [-lv[0]*lh*1.06, -lv[1]*lh*1.06, 0],
            [ lv[0]*lh*1.06,  lv[1]*lh*1.06, 0],
            buff=0, color=C_TEA, stroke_width=2.6, tip_length=0.14)

        # Callout labels outside the dense cloud region
        # Orange label: upper-left (toward the positive short-axis tip [-0.37, 0.56])
        lbl_short = Text("Large Q\nStrongly constrained",
                         font_size=19, color=C_ORG, line_spacing=0.82)
        lbl_short.move_to([-3.5, 1.55, 0])
        # Arrow from label to the positive short-axis tip
        s_ptip = np.array([-sv[0]*sh, -sv[1]*sh])   # = [-0.372, 0.558] (upper-left end)
        arr_short = Arrow(
            lbl_short.get_right(),
            [float(s_ptip[0]), float(s_ptip[1]), 0],
            buff=0.22, color=C_ORG, stroke_width=1.4,
            max_tip_length_to_length_ratio=0.22)

        # Teal label: upper-right (toward positive long-axis tip [2.09, 1.39])
        lbl_long = Text("Small Q\nWeakly constrained",
                        font_size=19, color=C_TEA, line_spacing=0.82)
        lbl_long.move_to([4.0, 0.55, 0])
        # Positive long-axis tip: -lv * lh = [0.832*2.51, 0.555*2.51] = [2.09, 1.39]
        l_ptip = np.array([-lv[0]*lh, -lv[1]*lh])   # = [2.089, 1.392]
        arr_long = Arrow(
            lbl_long.get_left(),
            [float(l_ptip[0]), float(l_ptip[1]), 0],
            buff=0.22, color=C_TEA, stroke_width=1.4,
            max_tip_length_to_length_ratio=0.22)

        c3 = self.cue(
            "Short axis: strongly constrained - large Q"
            "Long axis (teal):  weakly constrained - small Q",
            color=C_LGR, sz=18)

        self.play(
            Create(short_da, run_time=1.1),
            Create(long_da, run_time=1.5),
            FadeIn(lbl_short, arr_short, lbl_long, arr_long),
            ReplacementTransform(c2, c3))
        self.wait(2.2)

        # Precision ellipse
        p_ell = make_ellipse(PREC, scale=1.2, color=C_ORG,
                             fill_opacity=0, stroke_width=3.0)
        p_ell.set_z_index(5)
        c4 = self.cue(
            "Precision Q = Σ⁻¹  —  the inverse of the covariance",
            color=C_ORG, sz=22)
        self.play(Create(p_ell, run_time=2.0), ReplacementTransform(c3, c4))
        self.wait(0.8)

        c5 = self.cue("Q describes which combinations of activity are constrained.",
                      color=WHITE, sz=25, italic=False)
        self.play(ReplacementTransform(c4, c5))
        self.wait(2.8)

        self.play(FadeOut(
            VGroup(hd, nl, ax, xl, yl, cloud, c_ell, p_ell,
                   short_da, long_da, lbl_short, arr_short, lbl_long, arr_long,
                   c5),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 2: D ────────────────────────────────────────────────────────────

    def scene2_d(self):
        hd, nl = self.scene_hdr("What D sees", "2")
        self.play(FadeIn(hd, nl, run_time=0.7))

        ax = Axes(x_range=[-4,4,1], y_range=[-3,3,1],
                  x_length=9.0, y_length=6.0,
                  axis_config={"color": C_DGR, "stroke_width": 0.8,
                               "include_ticks": False}).move_to([0, -0.15, 0])
        ghost = make_ellipse(COV, scale=1.5, color=C_LGR,
                             fill_opacity=0, stroke_width=1.5)
        ghost.set_stroke(opacity=0.28)
        g_lbl = halo(Text("Stationary distribution (fixed)",
                           font_size=16, color=C_MGR))
        g_lbl.to_corner(UR, buff=0.45).shift(DOWN * 0.3)

        c0 = self.cue("D describes fluctuations entering the system.",
                      color=WHITE, sz=25, italic=False)
        self.play(Create(ax, run_time=0.6), Create(ghost, run_time=0.8),
                  FadeIn(g_lbl, c0))
        self.wait(1.2)

        pos4 = [[-1.0, 0.5], [0.9, 0.7], [1.1, -0.6], [-0.4, -0.8]]
        sdots = VGroup(*[Dot([p[0], p[1], 0], radius=0.10,
                              color=C_BLU, fill_opacity=0.9) for p in pos4])
        self.play(LaggedStart(*[FadeIn(d) for d in sdots],
                              lag_ratio=0.12, run_time=0.9))
        self.wait(0.5)

        D_ISO  = np.eye(2) * 0.36
        D_ANI  = np.diag([0.10, 0.72])
        D_CORR = np.array([[0.45, 0.38], [0.38, 0.45]])
        cases  = [
            (D_ISO,  "Isotropic D  —  kicks arrive equally in all directions"),
            (D_ANI,  "Anisotropic D  —  kicks arrive mainly along one axis"),
            (D_CORR, "Correlated D  —  kicks in x₁ and x₂ tend to arrive together"),
        ]

        def kick_group(D_mat):
            rng2 = np.random.default_rng(5)
            grp = VGroup()
            for p in pos4:
                raw = rng2.multivariate_normal([0, 0], D_mat, 10)
                kept = 0
                for k in raw:
                    mah2 = float(k @ np.linalg.inv(D_mat) @ k)
                    if np.linalg.norm(k) < 0.04 or mah2 > 1.4 or kept >= 3:
                        continue
                    a = Arrow([p[0], p[1], 0],
                               [p[0]+float(k[0]), p[1]+float(k[1]), 0],
                               buff=0, color=C_TEA, stroke_width=1.7,
                               max_tip_length_to_length_ratio=0.45)
                    a.set_stroke(opacity=0.75)
                    grp.add(a)
                    kept += 1
                e = make_ellipse(D_mat, scale=1.0, color=C_TEA,
                                 fill_opacity=0, stroke_width=1.1)
                e.set_stroke(opacity=0.30).shift(np.array([p[0], p[1], 0]))
                grp.add(e)
            return grp

        cur_grp, cur_cue = None, c0
        for D_mat, label in cases:
            grp = kick_group(D_mat)
            nc  = self.cue(label, color=C_TEA, sz=22)
            if cur_grp is None:
                self.play(
                    LaggedStart(*[Create(a) for a in grp],
                                lag_ratio=0.03, run_time=1.3),
                    ReplacementTransform(cur_cue, nc))
            else:
                self.play(FadeOut(cur_grp, run_time=0.5))
                self.play(
                    LaggedStart(*[Create(a) for a in grp],
                                lag_ratio=0.03, run_time=1.2),
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
                          fill_opacity=0, stroke_width=1.8).shift(LEFT*3.3)
        eR = make_ellipse(COV, scale=1.35, color=C_LGR,
                          fill_opacity=0, stroke_width=1.8).shift(RIGHT*3.3)
        eL.set_stroke(opacity=0.45); eR.set_stroke(opacity=0.45)
        div = DashedLine([0,-3.0,0],[0,3.0,0],
                         color=C_MGR, stroke_width=1.0, stroke_opacity=0.3)
        lL = Text("Equilibrium\nΩ = 0",    font_size=26, color=WHITE,  line_spacing=0.85)
        lL.move_to([LX, 2.85, 0])
        lR = Text("Non-equilibrium\nΩ ≠ 0", font_size=26, color=C_PUR, line_spacing=0.85)
        lR.move_to([RX, 2.85, 0])
        same = Text("Same density on both sides", font_size=18, color=C_LGR)
        same.move_to([0, -2.75, 0])

        c1 = self.cue("Both systems visit the same states  —  same stationary density")
        self.play(Create(eL,run_time=0.8), Create(eR,run_time=0.8),
                  FadeIn(div, lL, lR, same, c1))
        self.wait(1.0)

        arrows = make_flow(A_SK, nx=7, ny=5, xr=(-2.6,2.6), yr=(-1.8,1.8),
                           alen=0.26, cx=RX, cy=0, color=C_PUR, alpha=0.52)
        no_flow = Text("No net flow", font_size=20, color=C_LGR).move_to([LX, 0.0, 0])
        c2 = self.cue("Same density  —  but one system takes directed routes",
                      color=C_PUR, sz=24)
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.02, run_time=1.4),
                  FadeIn(no_flow), ReplacementTransform(c1, c2))
        self.wait(1.0)

        rng2 = np.random.default_rng(7)
        starts = rng2.multivariate_normal([0,0], COV*0.12, 4)
        trE = sim_ou(starts, n=160, dt=0.07, sig=0.10)
        trC = sim_ou(starts, A_extra=A_SK, n=160, dt=0.07, sig=0.07)
        pL = VGroup(*[make_path(t, cx=LX, color=C_BLU,  width=1.6) for t in trE])
        pR = VGroup(*[make_path(t, cx=RX, color=C_PUR, width=1.6) for t in trC])
        c3 = self.cue("Left: bounces randomly.   Right: takes directed routes.",
                      color=C_LGR, sz=22)
        self.play(ReplacementTransform(c2, c3))
        self.play(
            LaggedStart(*[Create(p, run_time=3.0) for p in pL], lag_ratio=0.18),
            LaggedStart(*[Create(p, run_time=3.0) for p in pR], lag_ratio=0.18))
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

        qe = make_ellipse(PREC, scale=1.3, color=C_ORG,
                          fill_opacity=0, stroke_width=2.8).shift([LX, CY, 0])
        qs = halo(Text("Geometry of\nconstraint", font_size=19, color=C_ORG,
                       line_spacing=0.8)).move_to([LX, CY-2.05, 0])
        c1 = self.cue("Q tells us where states relate", color=C_ORG, sz=25)
        self.play(Create(qe, run_time=1.5), FadeIn(qs, c1))
        self.wait(1.2)

        rng3 = np.random.default_rng(5)
        d_pos = [[-0.8, 0.5], [0.6, 0.4], [0.7, -0.5], [-0.4, -0.5], [0.0, 0.0]]
        D0 = np.eye(2) * 0.40
        d_grp = VGroup()
        for p in d_pos:
            raw = rng3.multivariate_normal([0,0], D0, 8)
            kept = 0
            for k in raw:
                mah2 = float(k @ np.linalg.inv(D0) @ k)
                if np.linalg.norm(k) < 0.04 or mah2 > 1.4 or kept >= 3:
                    continue
                a = Arrow([MX+p[0], CY+p[1], 0],
                           [MX+p[0]+float(k[0]), CY+p[1]+float(k[1]), 0],
                           buff=0, color=C_TEA, stroke_width=1.5,
                           max_tip_length_to_length_ratio=0.45)
                a.set_stroke(opacity=0.68)
                d_grp.add(a)
                kept += 1
        blob = make_ellipse(D0*3, scale=1.0, color=C_TEA,
                            fill_color=C_TEA, fill_opacity=0.11,
                            stroke_width=1.4).shift([MX, CY, 0])
        ds = halo(Text("Fluctuation\ninput", font_size=19, color=C_TEA,
                       line_spacing=0.8)).move_to([MX, CY-2.05, 0])
        c2 = self.cue("D tells us where fluctuations enter", color=C_TEA, sz=25)
        self.play(LaggedStart(*[Create(a) for a in d_grp], lag_ratio=0.04, run_time=1.2),
                  Create(blob, run_time=0.8),
                  FadeIn(ds), ReplacementTransform(c1, c2))
        self.wait(1.2)

        A_om = A_SK * 0.55 - np.eye(2) * 0.25
        om_flow = make_flow(A_om, nx=5, ny=5, xr=(-2.0,2.0), yr=(-1.6,1.6),
                            alen=0.30, cx=RX, cy=CY, color=C_PUR, alpha=0.62)
        os = halo(Text("Flow through\nstate space", font_size=19, color=C_PUR,
                       line_spacing=0.8)).move_to([RX, CY-2.05, 0])
        c3 = self.cue("Ω tells us how activity moves through state space",
                      color=C_PUR, sz=25)
        self.play(LaggedStart(*[Create(a) for a in om_flow], lag_ratio=0.04, run_time=1.4),
                  FadeIn(os), ReplacementTransform(c2, c3))
        self.wait(1.5)

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

    # ── Bridge: One System, Two States ───────────────────────────────────────

    # def scene_bridge(self):
    #     """15-20 s bridge between toy geometry and worm biology.
    #     Shows how D, Q, and Ω each change when the same system switches state."""

    #     hd = Text("One System, Two States", font_size=34, color=WHITE, weight=BOLD)
    #     hd.to_edge(UP, buff=0.38)
    #     nl = Text("Bridge", font_size=14, color=C_MGR).to_corner(UL, buff=0.26)

    #     LX, RX, CY = -3.2, 3.2, 0.15

    #     lbl_A = Text("State A", font_size=24, color=C_DWL, weight=BOLD)
    #     lbl_A.move_to([LX, 2.72, 0])
    #     lbl_B = Text("State B", font_size=24, color=C_ROM, weight=BOLD)
    #     lbl_B.move_to([RX, 2.72, 0])
    #     div = DashedLine([0, -2.8, 0], [0, 2.8, 0],
    #                      color=C_MGR, stroke_width=0.8, stroke_opacity=0.32)

    #     self.play(FadeIn(hd, nl, lbl_A, lbl_B, div, run_time=0.8))

    #     # Matrices for each state
    #     D_A   = np.diag([0.15, 0.72])   # Neuron 2 fluctuates more in State A
    #     D_B   = np.diag([0.72, 0.15])   # Neuron 1 fluctuates more in State B
    #     COV_A = np.array([[0.9, 0.70], [0.70, 0.9]])    # strong correlation
    #     COV_B = np.array([[1.3, 0.12], [0.12, 0.9]])    # weak  correlation
    #     # Distinct flow matrices for each state (State A: CW spiral, B: CCW)
    #     A_FA  = np.array([[-0.10, -0.40], [ 0.40, -0.10]])
    #     A_FB  = np.array([[-0.20,  0.40], [-0.40, -0.20]])

    #     def row_label(text):
    #         t = Text(text, font_size=18, color=C_LGR, slant=ITALIC)
    #         t.move_to([0, -2.32, 0])
    #         return t

    #     def make_kicks(D_mat, cx, col):
    #         rng2 = np.random.default_rng(33 + int(abs(cx)))
    #         grp = VGroup()
    #         kept = 0
    #         for k in rng2.multivariate_normal([0, 0], D_mat, 24):
    #             mah2 = float(k @ np.linalg.inv(D_mat) @ k)
    #             if np.linalg.norm(k) < 0.05 or mah2 > 1.3 or kept >= 6:
    #                 continue
    #             a = Arrow([cx, CY, 0],
    #                       [cx + float(k[0]), CY + float(k[1]), 0],
    #                       buff=0, color=col, stroke_width=1.7,
    #                       max_tip_length_to_length_ratio=0.45)
    #             a.set_stroke(opacity=0.75)
    #             grp.add(a)
    #             kept += 1
    #         return grp

    #     # ── Panel 1: D changes ─────────────────────────────────────────────
    #     d_ell_A = make_ellipse(D_A, scale=1.5, color=C_DWL, fill_color=C_DWL,
    #                            fill_opacity=0.12, stroke_width=2.2).shift([LX, CY, 0])
    #     d_ell_B = make_ellipse(D_B, scale=1.5, color=C_ROM, fill_color=C_ROM,
    #                            fill_opacity=0.12, stroke_width=2.2).shift([RX, CY, 0])
    #     k_A = make_kicks(D_A, LX, C_DWL)
    #     k_B = make_kicks(D_B, RX, C_ROM)
    #     d_row = row_label("D  —  fluctuations")

    #     c1 = self.cue("Who fluctuates changes.", color=WHITE, sz=26, italic=False)
    #     self.play(
    #         Create(d_ell_A, run_time=0.7), Create(d_ell_B, run_time=0.7),
    #         LaggedStart(*[Create(a) for a in k_A], lag_ratio=0.06, run_time=0.7),
    #         LaggedStart(*[Create(a) for a in k_B], lag_ratio=0.06, run_time=0.7),
    #         FadeIn(d_row, c1))
    #     self.wait(2.2)

    #     # ── Panel 2: Q changes ─────────────────────────────────────────────
    #     q_ell_A = make_ellipse(COV_A, scale=1.3, color=C_DWL,
    #                            fill_opacity=0, stroke_width=2.4).shift([LX, CY, 0])
    #     q_ell_B = make_ellipse(COV_B, scale=1.3, color=C_ROM,
    #                            fill_opacity=0, stroke_width=2.4).shift([RX, CY, 0])
    #     q_row = row_label("Q  —  conditional coupling")

    #     c2 = self.cue("Who is linked changes.", color=WHITE, sz=26, italic=False)
    #     self.play(FadeOut(VGroup(d_ell_A, d_ell_B, k_A, k_B, d_row, c1), run_time=0.5))
    #     self.play(
    #         Create(q_ell_A, run_time=1.0), Create(q_ell_B, run_time=1.0),
    #         FadeIn(q_row, c2))
    #     self.wait(2.2)

    #     # ── Panel 3: Ω changes ─────────────────────────────────────────────
    #     flow_A = make_flow(A_FA, nx=5, ny=5, xr=(-2.2, 2.2), yr=(-1.8, 1.8),
    #                        alen=0.24, cx=LX, cy=CY, color=C_DWL, alpha=0.58)
    #     flow_B = make_flow(A_FB, nx=5, ny=5, xr=(-2.2, 2.2), yr=(-1.8, 1.8),
    #                        alen=0.24, cx=RX, cy=CY, color=C_ROM, alpha=0.58)
    #     o_row = row_label("Ω  —  current organization")

    #     c3 = self.cue("Current organization combines both.", color=WHITE, sz=26, italic=False)
    #     self.play(FadeOut(VGroup(q_ell_A, q_ell_B, q_row, c2), run_time=0.5))
    #     self.play(
    #         LaggedStart(*[Create(a) for a in flow_A], lag_ratio=0.03, run_time=1.2),
    #         LaggedStart(*[Create(a) for a in flow_B], lag_ratio=0.03, run_time=1.2),
    #         FadeIn(o_row, c3))
    #     self.wait(2.2)

    #     # ── Bridge to worm ─────────────────────────────────────────────────
    #     self.play(FadeOut(
    #         VGroup(lbl_A, lbl_B, div, flow_A, flow_B, o_row, c3),
    #         run_time=0.6))

    #     bridge = VGroup(
    #         Text("Same circuit  —  different state  —  different D, Q, and Ω",
    #              font_size=22, color=C_LGR),
    #         Text("↓", font_size=30, color=C_MGR),
    #         Text("In C. elegans: roaming and dwelling",
    #              font_size=26, color=WHITE),
    #     ).arrange(DOWN, buff=0.42).move_to([0, 0.25, 0])

    #     c4 = self.cue(
    #         "Same circuit.  Two behavioral states.  Three ways to see the change.",
    #         color=C_LGR, sz=20)
    #     self.play(
    #         LaggedStart(*[FadeIn(b, shift=UP * 0.12) for b in bridge],
    #                     lag_ratio=0.35, run_time=1.5),
    #         FadeIn(c4))
    #     self.wait(2.8)

    #     self.play(FadeOut(VGroup(hd, nl, bridge, c4), run_time=0.9))
    #     self.wait(0.2)

    def scene_bridge(self):
        """Bridge between toy geometry and worm biology.
        Same two-neuron system, but now show how state changes D, Q, and Ω,
        and how particles behave differently in the two states.
        """

        hd = Text("One System, Two States", font_size=34, color=WHITE, weight=BOLD)
        hd.to_edge(UP, buff=0.38)
        nl = Text("Bridge", font_size=14, color=C_MGR).to_corner(UL, buff=0.26)

        # Use a state palette distinct from the D / Q / Ω colors used earlier.
        S_A = C_DWL
        S_B = C_ROM

        LX, RX, CY = -3.2, 3.2, 0.15

        lbl_A = Text("State A", font_size=24, color=S_A, weight=BOLD)
        lbl_A.move_to([LX, 2.72, 0])
        lbl_B = Text("State B", font_size=24, color=S_B, weight=BOLD)
        lbl_B.move_to([RX, 2.72, 0])

        div = DashedLine([0, -2.8, 0], [0, 2.8, 0],
                        color=C_MGR, stroke_width=0.8, stroke_opacity=0.32)

        def row_label(text, col=C_LGR):
            t = Text(text, font_size=18, color=col, slant=ITALIC)
            t.move_to([0, -2.32, 0])
            return t

        def panel_axes(cx, cy=CY, scale=1.0, col=C_LGR):
            """Small axes for a 2-neuron toy system."""
            x0 = np.array([cx - 1.05*scale, cy, 0])
            x1 = np.array([cx + 1.10*scale, cy, 0])
            y0 = np.array([cx, cy - 0.88*scale, 0])
            y1 = np.array([cx, cy + 0.92*scale, 0])

            ax = Arrow(x0, x1, buff=0, color=col, stroke_width=1.4,
                    max_tip_length_to_length_ratio=0.05)
            ay = Arrow(y0, y1, buff=0, color=col, stroke_width=1.4,
                    max_tip_length_to_length_ratio=0.05)

            # Keep labels close to the arrow tips, away from the center.
            lx = Text("Neuron 1", font_size=14, color=col)
            lx.next_to(ax.get_end(), DOWN, buff=0.08).shift(RIGHT * 0.06)
            ly = Text("Neuron 2", font_size=14, color=col)
            ly.next_to(ay.get_end(), LEFT, buff=0.08).shift(UP * 0.02)
            return VGroup(ax, ay, lx, ly)

        def clip_to_ellipse(v, Dmat, scale=0.78):
            invD = np.linalg.inv(Dmat)
            q = float(v @ invD @ v)
            if q < 1e-8:
                return v
            return v * (scale / np.sqrt(q))

        def make_cloud(Dmat, cx, col, n=10, seed=11):
            rng = np.random.default_rng(seed)
            dots = VGroup()
            for p in rng.multivariate_normal([0, 0], Dmat, n):
                pp = clip_to_ellipse(np.array(p, dtype=float), Dmat, scale=0.80)
                d = Dot(point=[cx + 0.92*float(pp[0]), CY + 0.92*float(pp[1]), 0],
                        radius=0.045, color=col)
                d.set_opacity(0.9)
                dots.add(d)
            return dots

        def make_d_panel(Dmat, cx, col, seed=7, ell_scale=0.60):
            """Per-particle kick arrows + small diffusion ellipse, matching scene2_d visual logic.
            For each of 4 particle positions: draw the particle dot, 3 kick arrows sampled
            from Dmat, and a small Dmat-shaped ellipse centered on that particle.
            """
            rng2 = np.random.default_rng(seed)
            inv_D = np.linalg.inv(Dmat)
            # 4 particle positions relative to panel center (cx, CY)
            pos_panel = [[-0.38, 0.22], [0.34, 0.28], [0.38, -0.22], [-0.14, -0.30]]
            grp = VGroup()
            for pp in pos_panel:
                px, py = cx + pp[0], CY + pp[1]
                # kick arrows (same filter logic as kick_group in scene2_d)
                kept = 0
                for k in rng2.multivariate_normal([0, 0], Dmat, 12):
                    mah2 = float(k @ inv_D @ k)
                    if np.linalg.norm(k) < 0.03 or mah2 > 1.4 or kept >= 3:
                        continue
                    a = Arrow(
                        [px, py, 0],
                        [px + float(k[0]), py + float(k[1]), 0],
                        buff=0, color=col, stroke_width=1.7,
                        max_tip_length_to_length_ratio=0.45)
                    a.set_stroke(opacity=0.75)
                    grp.add(a)
                    kept += 1
                # small diffusion ellipse centered on this particle
                e = make_ellipse(Dmat, scale=ell_scale, color=col,
                                 fill_opacity=0, stroke_width=1.1)
                e.set_stroke(opacity=0.32).shift(np.array([px, py, 0]))
                grp.add(e)
                # the particle dot itself
                grp.add(Dot([px, py, 0], radius=0.07, color=col, fill_opacity=0.88))
            return grp

        def make_paths(A_mat, cx, col, seed=13, n_traj=3, sig=0.075, dt=0.07):
            """Short trajectory traces with a visible flow direction."""
            rng = np.random.default_rng(seed)
            starts = rng.multivariate_normal([0, 0], np.array([[0.06, 0.0], [0.0, 0.06]]), n_traj)
            trajs = sim_ou(starts, A_extra=A_mat, n=140, dt=dt, sig=sig)
            paths = VGroup()
            for tr in trajs:
                p = make_path(tr, cx=cx, color=col, width=1.7)
                paths.add(p)
            return paths

        # -------------------------------------------------------------------------
        # Phase 1: D changes
        # -------------------------------------------------------------------------
        self.play(FadeIn(hd, nl, lbl_A, lbl_B, div, run_time=0.8))

        D_A = np.diag([0.15, 0.72])  # Neuron 2 fluctuates more in State A
        D_B = np.diag([0.72, 0.15])  # Neuron 1 fluctuates more in State B

        axA = panel_axes(LX, CY, scale=1.0, col=S_A)
        axB = panel_axes(RX, CY, scale=1.0, col=S_B)

        d_row = row_label("D  —  fluctuations")
        c1 = self.cue("Who fluctuates changes.", color=WHITE, sz=26, italic=False)

        # Per-particle: dots + kick arrows + small per-particle diffusion ellipses
        # (same visual language as scene2_d)
        d_panel_A = make_d_panel(D_A, LX, S_A, seed=33)
        d_panel_B = make_d_panel(D_B, RX, S_B, seed=37)

        self.play(FadeIn(axA, axB), FadeIn(d_row, c1))
        self.play(
            LaggedStart(*[Create(m) for m in d_panel_A], lag_ratio=0.04, run_time=1.2),
            LaggedStart(*[Create(m) for m in d_panel_B], lag_ratio=0.04, run_time=1.2),
        )
        self.wait(1.8)

        # -------------------------------------------------------------------------
        # Phase 2: Q changes
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(d_panel_A, d_panel_B, d_row, c1), run_time=0.55))

        # State A = stronger coupling / more elongated constraint direction
        COV_A = np.array([[0.95, 0.74], [0.74, 0.95]])
        # State B = weaker coupling / more circular, less constrained
        COV_B = np.array([[1.22, 0.10], [0.10, 0.92]])

        q_ell_A = make_ellipse(COV_A, scale=1.32, color=S_A, fill_opacity=0,
                            stroke_width=2.6).shift([LX, CY, 0])
        q_ell_B = make_ellipse(COV_B, scale=1.32, color=S_B, fill_opacity=0,
                            stroke_width=2.6).shift([RX, CY, 0])

        # A small number of points to show the stationary cloud shape.
        q_pts_A = make_cloud(COV_A, LX, S_A, n=8, seed=51)
        q_pts_B = make_cloud(COV_B, RX, S_B, n=8, seed=53)

        q_row = row_label("Q  —  conditional coupling")
        c2 = self.cue("Who is linked changes.", color=WHITE, sz=26, italic=False)

        self.play(
            Create(q_ell_A, run_time=0.9), Create(q_ell_B, run_time=0.9),
            FadeIn(q_row, c2),
            FadeIn(axA), FadeIn(axB),
        )
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.8) for d in q_pts_A], lag_ratio=0.05, run_time=0.9),
            LaggedStart(*[FadeIn(d, scale=0.8) for d in q_pts_B], lag_ratio=0.05, run_time=0.9),
        )
        self.wait(1.8)

        # -------------------------------------------------------------------------
        # Phase 3: Ω changes
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(q_ell_A, q_ell_B, q_pts_A, q_pts_B, q_row, c2),
                        run_time=0.55))

        # Distinct flow matrices for each state
        # State A: clockwise spiral; State B: counterclockwise spiral
        A_FA = np.array([[-0.10, -0.42], [ 0.40, -0.10]])
        A_FB = np.array([[-0.20,  0.40], [-0.40, -0.20]])

        flow_A = make_flow(A_FA, nx=4, ny=4, xr=(-1.7, 1.7), yr=(-1.25, 1.25),
                        alen=0.20, cx=LX, cy=CY, color=S_A, alpha=0.50)
        flow_B = make_flow(A_FB, nx=4, ny=4, xr=(-1.7, 1.7), yr=(-1.25, 1.25),
                        alen=0.20, cx=RX, cy=CY, color=S_B, alpha=0.50)

        # A few trajectory traces to make the state dependence visually obvious.
        paths_A = make_paths(A_FA, LX, S_A, seed=61, n_traj=3, sig=0.070, dt=0.07)
        paths_B = make_paths(A_FB, RX, S_B, seed=63, n_traj=3, sig=0.070, dt=0.07)

        o_row = row_label("Ω  —  current organization")
        c3 = self.cue("Same states. Different routes through those states.",
                    color=C_LGR, sz=24, italic=False)

        self.play(
            LaggedStart(*[Create(a) for a in flow_A], lag_ratio=0.03, run_time=1.0),
            LaggedStart(*[Create(a) for a in flow_B], lag_ratio=0.03, run_time=1.0),
            FadeIn(o_row, c3),
        )
        self.play(
            LaggedStart(*[Create(p, run_time=1.8) for p in paths_A], lag_ratio=0.18),
            LaggedStart(*[Create(p, run_time=1.8) for p in paths_B], lag_ratio=0.18),
        )
        self.wait(1.4)

        # -------------------------------------------------------------------------
        # Bridge to worm
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(lbl_A, lbl_B, div, axA, axB, flow_A, flow_B, paths_A, paths_B,
                                o_row, c3), run_time=0.65))

        bridge = VGroup(
            Text("Same system  —  different state  —  different D, Q, and Ω",
                font_size=22, color=C_LGR),
            Text("↓", font_size=30, color=C_MGR),
            Text("In C. elegans: roaming and dwelling",
                font_size=26, color=WHITE),
        ).arrange(DOWN, buff=0.42).move_to([0, 0.25, 0])

        c4 = self.cue(
            "Same circuit.  Two behavioral states.  D, Q, and Ω all change.",
            color=C_LGR, sz=20)

        self.play(
            LaggedStart(*[FadeIn(b, shift=UP * 0.12) for b in bridge],
                        lag_ratio=0.35, run_time=1.4),
            FadeIn(c4)
        )
        self.wait(2.6)

        self.play(FadeOut(VGroup(hd, nl, bridge, c4), run_time=0.8))
        self.wait(0.2)

    # ── Scene: Biological state space (VIS-2 bridge) ─────────────────────────

    def scene_module_state_space(self):
        """Biological state-space bridge (VIS-2).

        Module definitions:
          Food sensing = DA_mech module (ADEL + dopaminergic mechanosensors)
          Gas sensing  = URY_URX module (O2/social integrators: URYVR, URYDL, URXL)
        Module-average signal (no PCA). Schematic clouds, not actual neural data.

        Shows D, Q, and Ω on biological axes using the same visual language
        as the preceding abstract scenes:
          Q — confidence ellipse tilt (COV off-diagonal encodes coupling strength)
          D — per-particle kick arrows + small D-ellipses on 3 representative points per cloud
          Ω — 3 short trajectory traces per state, CW (dwelling) vs CCW (roaming)

        Cloud geometry reflects qualitative trends:
          Gas sensing activity elevated during roaming (Phase 3D: URY_URX D +20%)
          Food↔gas coupling stronger during roaming (Phase 2: DA_mech↔URY_URX ΔQ rank #2)
          Clouds overlap substantially (Phase 4A: no significant mean activity shifts)
        Target runtime: ~15 s.
        """
        # ── Header ────────────────────────────────────────────────────────────
        hd = Text("A biological state space", font_size=34, color=WHITE, weight=BOLD)
        hd.to_edge(UP, buff=0.38)
        nl = Text("Bridge · 2", font_size=14, color=C_MGR).to_corner(UL, buff=0.26)
        self.play(FadeIn(hd, nl, run_time=0.7))

        # ── Axes ──────────────────────────────────────────────────────────────
        ax = Axes(
            x_range=[-2.8, 2.8, 1], y_range=[-2.5, 2.5, 1],
            x_length=8.4, y_length=5.6,
            axis_config={"color": C_MGR, "stroke_width": 1.2, "include_ticks": False},
        ).move_to([0, -0.25, 0])
        xl = halo(Text("Food sensing activity", font_size=18, color=C_LGR))
        xl.next_to(ax.x_axis.get_right(), DOWN, buff=0.22)
        yl = halo(Text("Gas sensing activity", font_size=18, color=C_LGR))
        yl.next_to(ax.y_axis.get_top(), UP, buff=0.12)
        self.play(Create(ax, run_time=0.9), FadeIn(xl, yl))
        self.wait(0.2)

        # ── Beat 1: Point clouds ───────────────────────────────────────────────
        # COV encodes Q: COV_ROM has larger off-diagonal → stronger food↔gas coupling
        rng_sc = np.random.default_rng(42)
        MU_DWL  = np.array([-0.18, -0.50])
        MU_ROM  = np.array([ 0.20,  0.58])
        COV_DWL = np.array([[0.55, 0.06], [0.06, 0.42]])
        COV_ROM = np.array([[0.48, 0.25], [0.25, 0.55]])

        pts_dw = rng_sc.multivariate_normal(MU_DWL, COV_DWL, 65)
        pts_rm = rng_sc.multivariate_normal(MU_ROM, COV_ROM, 65)

        dw_dots = VGroup(*[
            Dot(ax.c2p(float(p[0]), float(p[1])), radius=0.042,
                color=C_DWL, fill_opacity=0.42)
            for p in pts_dw
        ])
        rm_dots = VGroup(*[
            Dot(ax.c2p(float(p[0]), float(p[1])), radius=0.042,
                color=C_ROM, fill_opacity=0.42)
            for p in pts_rm
        ])

        leg = VGroup(
            VGroup(Dot(radius=0.09, color=C_DWL, fill_opacity=0.85),
                   Text("Dwelling", font_size=19, color=C_DWL)).arrange(RIGHT, buff=0.18),
            VGroup(Dot(radius=0.09, color=C_ROM, fill_opacity=0.85),
                   Text("Roaming",  font_size=19, color=C_ROM)).arrange(RIGHT, buff=0.18),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        leg.to_corner(UR, buff=0.46).shift(DOWN * 0.55)

        c1 = self.cue("Each point: one moment of neural activity", color=C_LGR, sz=22)
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in dw_dots],
                        lag_ratio=0.009, run_time=1.2),
            FadeIn(c1))
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in rm_dots],
                        lag_ratio=0.009, run_time=1.2),
            FadeIn(leg))
        self.wait(0.4)

        # ── Beat 2: Q — confidence ellipses ────────────────────────────────────
        # Axis scale: data → scene units
        sx = 8.4 / 5.6   # 1.50 scene per data unit (x)
        sy = 5.6 / 5.0   # 1.12 scene per data unit (y)
        S  = np.diag([sx, sy])

        ell_dw = make_ellipse(S @ COV_DWL @ S.T, scale=1.0,
                              color=C_DWL, fill_opacity=0, stroke_width=2.0)
        ell_dw.set_stroke(opacity=0.65).move_to(ax.c2p(float(MU_DWL[0]), float(MU_DWL[1])))
        ell_rm = make_ellipse(S @ COV_ROM @ S.T, scale=1.0,
                              color=C_ROM, fill_opacity=0, stroke_width=2.0)
        ell_rm.set_stroke(opacity=0.65).move_to(ax.c2p(float(MU_ROM[0]), float(MU_ROM[1])))

        c2 = self.cue("Q  —  conditional coupling differs between states.",
                      color=C_ORG, sz=23, italic=False)
        self.play(Create(ell_dw, run_time=1.1), Create(ell_rm, run_time=1.1),
                  ReplacementTransform(c1, c2))
        self.wait(1.2)

        # ── Beat 3: D — per-particle kick arrows + small diffusion ellipses ────
        # D_DWL_bio: roughly uniform; D_ROM_bio: gas sensing (Y) clearly elevated
        # Reflects Phase 3D: URY_URX D_roam +20% vs D_dwell
        D_DWL_bio = np.diag([0.085, 0.052])
        D_ROM_bio = np.diag([0.085, 0.170])
        D_DWL_sc  = S @ D_DWL_bio @ S.T
        D_ROM_sc  = S @ D_ROM_bio @ S.T

        # 3 representative positions per cloud (data coords, within ~1σ of mean)
        d_pos_dw = [(-0.55, -0.78), (0.12, -0.32), (-0.40, -0.08)]
        d_pos_rm = [( 0.52,  0.28), (-0.14,  0.85), ( 0.30,  0.10)]

        rng_d = np.random.default_rng(55)

        def d_annotation(D_bio, D_sc, positions, col):
            grp = VGroup()
            inv_D = np.linalg.inv(D_bio)
            for px_d, py_d in positions:
                kept = 0
                for k in rng_d.multivariate_normal([0, 0], D_bio, 14):
                    mah2 = float(k @ inv_D @ k)
                    if np.linalg.norm(k) < 0.02 or mah2 > 1.4 or kept >= 3:
                        continue
                    a = Arrow(
                        ax.c2p(px_d, py_d),
                        ax.c2p(px_d + float(k[0]), py_d + float(k[1])),
                        buff=0, color=col, stroke_width=1.7,
                        max_tip_length_to_length_ratio=0.45)
                    a.set_stroke(opacity=0.75)
                    grp.add(a)
                    kept += 1
                e = make_ellipse(D_sc, scale=1.0, color=col,
                                 fill_opacity=0, stroke_width=1.1)
                e.set_stroke(opacity=0.32).move_to(ax.c2p(px_d, py_d))
                grp.add(e)
                grp.add(Dot(ax.c2p(px_d, py_d), radius=0.07,
                            color=col, fill_opacity=0.88))
            return grp

        d_ann_dw = d_annotation(D_DWL_bio, D_DWL_sc, d_pos_dw, C_DWL)
        d_ann_rm = d_annotation(D_ROM_bio, D_ROM_sc, d_pos_rm, C_ROM)

        c3 = self.cue("D  —  fluctuation geometry differs between states.",
                      color=C_TEA, sz=23, italic=False)
        self.play(
            LaggedStart(*[Create(m) for m in d_ann_dw], lag_ratio=0.04, run_time=1.1),
            LaggedStart(*[Create(m) for m in d_ann_rm], lag_ratio=0.04, run_time=1.1),
            ReplacementTransform(c2, c3))
        self.wait(1.2)

        # ── Beat 4: Ω — trajectory traces ─────────────────────────────────────
        # CW for dwelling, CCW for roaming — clearly distinct circulation patterns
        A_DWL_om = np.array([[ 0.0, -0.44], [ 0.44,  0.0]])
        A_ROM_om = np.array([[ 0.0,  0.55], [-0.55,  0.0]])

        starts_dw = [np.array([ 0.44,  0.06]),
                     np.array([-0.12, -0.40]),
                     np.array([-0.35,  0.18])]
        starts_rm = [np.array([ 0.40, -0.08]),
                     np.array([ 0.10,  0.44]),
                     np.array([-0.32, -0.14])]

        trajs_dw_raw = sim_ou(starts_dw, A_extra=A_DWL_om, n=80, dt=0.07, sig=0.048, seed=89)
        trajs_rm_raw = sim_ou(starts_rm, A_extra=A_ROM_om, n=80, dt=0.07, sig=0.048, seed=91)

        def shift_and_clip(traj, mu):
            result = []
            for p in traj:
                sp = p + mu
                result.append(np.array([
                    float(np.clip(sp[0], -2.65, 2.65)),
                    float(np.clip(sp[1], -2.35, 2.35))
                ]))
            return result

        def bio_path(traj_pts, color, width=1.7, alpha=0.62):
            vmo = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=alpha)
            vmo.set_points_smoothly(
                [ax.c2p(float(p[0]), float(p[1])) for p in traj_pts])
            return vmo

        trajs_dw = [shift_and_clip(t, MU_DWL) for t in trajs_dw_raw]
        trajs_rm = [shift_and_clip(t, MU_ROM) for t in trajs_rm_raw]

        paths_dw = VGroup(*[bio_path(t, C_DWL) for t in trajs_dw])
        paths_rm = VGroup(*[bio_path(t, C_ROM) for t in trajs_rm])

        c4 = self.cue("Ω  —  routes through state space differ between states.",
                      color=C_PUR, sz=23, italic=False)
        self.play(
            LaggedStart(*[Create(p, run_time=1.6) for p in paths_dw], lag_ratio=0.22),
            LaggedStart(*[Create(p, run_time=1.6) for p in paths_rm], lag_ratio=0.22),
            ReplacementTransform(c3, c4))
        self.wait(0.7)

        # ── Final caption ──────────────────────────────────────────────────────
        c_fin = self.cue("Behavior reorganizes the neural state space.",
                         color=WHITE, sz=28, italic=False)
        self.play(ReplacementTransform(c4, c_fin))
        self.wait(2.4)

        self.play(FadeOut(
            VGroup(hd, nl, ax, xl, yl, dw_dots, rm_dots, leg,
                   ell_dw, ell_rm, d_ann_dw, d_ann_rm, paths_dw, paths_rm, c_fin),
            run_time=1.0))
        self.wait(0.2)

    # ── Scene 5: Worm ─────────────────────────────────────────────────────────

    def scene5_worm(self):
        hd, nl = self.scene_hdr("In C. elegans", "5")
        self.play(FadeIn(hd, nl, run_time=0.7))
        self._worm_D()
        self._worm_Q()
        self._worm_Omega()
        self._final_card(hd, nl)

    def _worm_D(self):
        ttl = Text("D  —  Innovation variance by functional group",
                   font_size=24, color=C_TEA, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        groups  = ["Gas\nsensing", "Food\nsensing", "Motor\ncontrol", "Local\nsearch"]
        dwell_v = np.array([0.30, 0.38, 0.40, 0.40])
        roam_v  = np.array([0.48, 0.42, 0.39, 0.24])
        sig_dw  = [False, False, False, True ]
        sig_rm  = [True,  False, False, False]

        N  = len(groups)
        bw = 0.58
        gap = 0.12
        gw  = 2*bw + gap + 0.38
        x0  = -(N * gw) / 2 + gw / 2
        yb  = -1.4
        sc  = 3.5

        bars = VGroup()
        lbls = VGroup()
        stars = VGroup()

        for i, (g, dv, rv, sd, sr) in enumerate(zip(groups, dwell_v, roam_v,
                                                      sig_dw, sig_rm)):
            gx = x0 + i * gw
            dh = float(dv * sc)
            rh = float(rv * sc)
            alpha_d = 0.82 if sd else 0.45
            alpha_r = 0.82 if sr else 0.45

            db = Rectangle(width=float(bw*0.88), height=dh,
                           color=C_DWL, fill_color=C_DWL,
                           fill_opacity=alpha_d, stroke_width=0)
            db.move_to([gx - bw/2 - gap/2, yb + dh/2, 0])

            rb = Rectangle(width=float(bw*0.88), height=rh,
                           color=C_ROM, fill_color=C_ROM,
                           fill_opacity=alpha_r, stroke_width=0)
            rb.move_to([gx + bw/2 + gap/2, yb + rh/2, 0])

            bars.add(db, rb)

            gl = halo(Text(g, font_size=18, color=C_LGR, line_spacing=0.75))
            gl.move_to([gx, yb - 0.62, 0])
            lbls.add(gl)

            if sd:
                star = Text("★", font_size=22, color=C_DWL)
                star.move_to([gx - bw/2 - gap/2, yb + dh + 0.22, 0])
                stars.add(star)
            if sr:
                star = Text("★", font_size=22, color=C_ROM)
                star.move_to([gx + bw/2 + gap/2, yb + rh + 0.22, 0])
                stars.add(star)

        leg = VGroup(
            VGroup(Square(0.20, color=C_DWL, fill_color=C_DWL,
                          fill_opacity=0.9, stroke_width=0),
                   Text("Dwelling", font_size=18, color=C_DWL)).arrange(RIGHT, buff=0.16),
            VGroup(Square(0.20, color=C_ROM, fill_color=C_ROM,
                          fill_opacity=0.9, stroke_width=0),
                   Text("Roaming",  font_size=18, color=C_ROM)).arrange(RIGHT, buff=0.16),
        ).arrange(RIGHT, buff=0.6).to_corner(UR, buff=0.42)

        star_leg = Text("★ = notable change", font_size=16, color=C_LGR, slant=ITALIC)
        star_leg.to_corner(UR, buff=0.42).shift(DOWN * 0.55)

        zl = Line([x0-gw*0.5, yb, 0], [x0+N*gw, yb, 0],
                  color=C_MGR, stroke_width=0.9, stroke_opacity=0.5)

        c1 = self.cue(
            "Gas sensing fluctuates more during roaming.  "
            "Local search fluctuates more during dwelling.",
            color=C_TEA, sz=20)

        self.play(FadeIn(zl, leg, star_leg))
        self.play(
            LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.06, run_time=1.5),
            FadeIn(lbls, c1))
        self.play(
            LaggedStart(*[FadeIn(s, scale=1.5) for s in stars],
                        lag_ratio=0.1, run_time=0.6))
        self.wait(1.5)

        msg = Text("D reorganizes between states.", font_size=26,
                   color=C_TEA, weight=BOLD).move_to([0, 2.45, 0])
        self.play(Transform(ttl, msg, run_time=0.8))
        self.wait(1.8)

        self.play(FadeOut(VGroup(ttl, bars, lbls, stars, zl, leg, star_leg, c1),
                          run_time=0.9))
        self.wait(0.15)

    def _worm_Q(self):
        ttl = Text("Q  —  Conditional coupling between functional groups",
                   font_size=24, color=C_ORG, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        LX, RX, QY = -2.6, 2.6, 0.3

        def net(cx, state_lbl, state_col, edge_lw):
            nd1 = Circle(radius=0.55, color=C_ORG,
                         fill_color=C_ORG, fill_opacity=0.18, stroke_width=2.0)
            nd1.move_to([cx-1.25, QY, 0])
            nd2 = Circle(radius=0.55, color=C_ORG,
                         fill_color=C_ORG, fill_opacity=0.18, stroke_width=2.0)
            nd2.move_to([cx+1.25, QY, 0])
            l1 = halo(Text("Food\nsensing", font_size=15, color=C_ORG,
                            line_spacing=0.75)).move_to(nd1)
            l2 = halo(Text("Gas\nsensing",  font_size=15, color=C_ORG,
                            line_spacing=0.75)).move_to(nd2)
            edge = Line(nd1.get_right(), nd2.get_left(),
                        color=C_ORG, stroke_width=edge_lw, stroke_opacity=0.90)
            sl = Text(state_lbl, font_size=21, color=state_col, weight=BOLD)
            sl.move_to([cx, QY+1.5, 0])
            return VGroup(nd1, nd2, l1, l2, edge, sl)

        g_dw = net(LX, "DWELLING", C_DWL, 1.5)
        g_rm = net(RX, "ROAMING",  C_ROM, 6.5)
        div  = DashedLine([0,-1.8,0],[0,2.1,0],
                          color=C_MGR, stroke_width=0.8, stroke_opacity=0.28)
        ld = halo(Text("Weaker coupling", font_size=17, color=C_LGR))
        ld.move_to([LX, QY-1.5, 0])
        lr = halo(Text("Stronger coupling", font_size=17, color=C_ORG))
        lr.move_to([RX, QY-1.5, 0])

        c2 = self.cue(
            "Food sensing ↔ Gas sensing:  conditional coupling strengthens during roaming.",
            color=C_ORG, sz=21)
        self.play(FadeIn(g_dw, g_rm, div, ld, lr, c2))
        self.wait(2.0)

        msg = Text("Q reorganizes between states.", font_size=26,
                   color=C_ORG, weight=BOLD).move_to([0, 2.45, 0])
        self.play(Transform(ttl, msg, run_time=0.8))
        self.wait(1.8)

        self.play(FadeOut(VGroup(ttl, g_dw, g_rm, div, ld, lr, c2), run_time=0.9))
        self.wait(0.15)

    def _worm_Omega(self):
        ttl = Text("Ω  —  Incorporates both reorganizations",
                   font_size=24, color=C_PUR, weight=BOLD).move_to([0, 2.45, 0])
        self.play(FadeIn(ttl, run_time=0.6))

        ck_d = Text("D adds biology  ✓",       font_size=24, color=C_TEA)
        ck_q = Text("Q adds biology  ✓",       font_size=24, color=C_ORG)
        ck_o = Text("Ω = DQ + A  combines both", font_size=24, color=C_PUR)
        VGroup(ck_d, ck_q, ck_o).arrange(DOWN, buff=0.42,
                                          aligned_edge=LEFT).move_to([-2.0, 0.2, 0])

        box = RoundedRectangle(width=5.4, height=1.6, corner_radius=0.22,
                               color=C_PUR, fill_color=C_DGR,
                               fill_opacity=0.5, stroke_width=2.0).move_to([3.1, 0.2, 0])
        box_txt = Text("Same biological\ninterpretation",
                       font_size=22, color=WHITE, line_spacing=0.85).move_to(box)
        arr = Arrow([-0.3, 0.2, 0], [1.45, 0.2, 0],
                    buff=0, color=C_PUR, stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.2)

        c3 = self.cue(
            "D adds biology.  Q adds biology.  Ω combines both.",
            color=C_PUR, sz=23)
        self.play(FadeIn(c3))
        self.play(FadeIn(ck_d, shift=RIGHT*0.2, run_time=0.7))
        self.play(FadeIn(ck_q, shift=RIGHT*0.2, run_time=0.7))
        self.play(FadeIn(ck_o, shift=RIGHT*0.2, run_time=0.7))
        self.wait(0.6)
        self.play(Create(box, run_time=0.8), FadeIn(box_txt))
        self.play(Create(arr, run_time=0.6))
        self.wait(1.0)

        c4 = self.cue(
            "In this dataset, Ω does not change the biological interpretation.",
            color=WHITE, sz=23, italic=False)
        self.play(ReplacementTransform(c3, c4))
        self.wait(2.2)

        self.play(FadeOut(VGroup(ttl, ck_d, ck_q, ck_o, box, box_txt, arr, c4),
                          run_time=0.9))
        self.wait(0.15)

    def _final_card(self, hd, nl):
        rows = VGroup(
            VGroup(
                Text("D:", font_size=28, color=C_TEA, weight=BOLD),
                VGroup(
                    Text("Which neurons become dynamically variable?",
                         font_size=22, color=WHITE),
                    Text("Gas sensing ↑ roaming   ·   Local search ↑ dwelling",
                         font_size=20, color=C_LGR, slant=ITALIC),
                ).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
            ).arrange(RIGHT, buff=0.4, aligned_edge=UP),
            VGroup(
                Text("Q:", font_size=28, color=C_ORG, weight=BOLD),
                VGroup(
                    Text("Which neurons become conditionally linked?",
                         font_size=22, color=WHITE),
                    Text("Food sensing ↔ Gas sensing  (PDF-associated organization)",
                         font_size=20, color=C_LGR, slant=ITALIC),
                ).arrange(DOWN, buff=0.12, aligned_edge=LEFT),
            ).arrange(RIGHT, buff=0.4, aligned_edge=UP),
            VGroup(
                Text("Ω:", font_size=28, color=C_PUR, weight=BOLD),
                Text("Combines both reorganizations.",
                     font_size=22, color=WHITE),
            ).arrange(RIGHT, buff=0.4, aligned_edge=UP),
        ).arrange(DOWN, buff=0.50, aligned_edge=LEFT).move_to([0, 0.95, 0])

        result = VGroup(
            Text("Result:", font_size=22, color=C_YEL, weight=BOLD),
            Text("Same biological interpretation for the PDF-associated circuit.",
                 font_size=22, color=WHITE),
        ).arrange(RIGHT, buff=0.3).move_to([0, -0.72, 0])

        footer = Text(
            "Different mathematical descriptions.   Same circuit-level conclusion.",
            font_size=19, color=C_LGR, slant=ITALIC).move_to([0, -1.65, 0])

        for row in rows:
            self.play(FadeIn(row, shift=UP*0.15, run_time=0.75))
        self.wait(0.4)
        self.play(FadeIn(result, shift=UP*0.12, run_time=0.8))
        self.wait(0.4)
        self.play(FadeIn(footer, run_time=0.8))
        self.wait(3.8)

        self.play(FadeOut(VGroup(hd, nl, rows, result, footer), run_time=1.2))
