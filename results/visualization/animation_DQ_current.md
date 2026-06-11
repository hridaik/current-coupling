# Animation 4 — From Precision to Current
## Detailed Production Storyboard
Date: 2026-06-04
Authorization: PHASE VIS-1A

**Target runtime**: 85–95 seconds  
**Frame rate**: 24 fps (~2040–2280 frames)  
**Format**: MP4 (H.264), 1920×1080, dark background  
**Style reference**: 3Blue1Brown / Manim aesthetic  
**Export path**: `results/visualization/dq_to_current_animation.mp4` (placeholder)

---

## Design Principles

### Visual language
- Background: near-black (#0F0F14)
- Axes / grid: faint white (#FFFFFF at 15% opacity)
- Points / trajectory traces: dark blue (#3D5A99)
- Q / precision objects: warm orange (#E07B39)
- D / diffusion objects: teal (#2A9D8F)
- Ω / current objects: soft purple (#8B5CF6)
- On-screen text (primary): white (#F0F0F0)
- On-screen text (secondary / annotation): light gray (#AAAAAA)
- Highlight / emphasis: bright yellow (#F5C518), used sparingly

### Motion principles
- All transitions: smooth easing (ease-in-out), minimum 12 frames
- Text appearance: fade-in over 8 frames, never sudden cut
- Ellipses "draw themselves": stroke traces from angle 0 around the contour
- Matrix objects: appear as colored blocks, then morph into geometric objects
- No element disappears abruptly: always fade or transform

### Layout
- Main geometric canvas: centered, 60% of frame width
- Text cues: bottom strip (bottom 15% of frame), full width, center-aligned
- Scene labels: top-left corner, small, gray, always visible
- Equations: only in captions, never dominating the visual layer

---

## TITLE CARD
**Duration**: 3 seconds (frames 1–72)

- Frame 1–24: Black canvas. Nothing.
- Frame 25–48: Title fades in, centered:
  ```
  From Precision to Current
  ```
  Font: large, white, weight-400. Line below it, orange:
  ```
  D,  Q,  and Ω  in a stochastic system
  ```
- Frame 49–60: Both lines hold.
- Frame 61–72: Title fades to 20% opacity (stays as a ghost watermark in top-left).

---

## SCENE 1 — Precision Geometry
**Duration**: ~20 seconds (frames 73–552)  
**Scene label**: "1 / Q — geometry"

### Purpose
Establish Q as the object that encodes the *shape of constraint* in state space.
The viewer should leave this scene thinking: "Q is about which directions are tight."

### Misconception corrected
"The covariance and the precision describe the same thing."
They do not — Q is the inverse and encodes a different geometric object.

---

**BEAT 1 — Axes appear** (frames 73–120, ~2 sec)
- 2D coordinate axes animate in from center: thin white lines extending outward
- Axis labels appear at tips: `x₁` (horizontal), `x₂` (vertical)
- Grid lines: very faint, 15% opacity
- Scene label appears top-left: "1 · Q"

**BEAT 2 — Gaussian cloud materializes** (frames 121–216, ~4 sec)
- ~200 small blue dots appear one by one, scattering from origin
- Each dot fades in at its final Gaussian-sampled position (not animated movement)
- The cloud has covariance: [[2.0, 1.2], [1.2, 1.0]] — a tilted distribution
- By frame 216 the full cloud is visible
- Text cue (bottom strip): *"States of a 2D stochastic system"*

**BEAT 3 — Covariance ellipse traces** (frames 217–288, ~3 sec)
- Gray ellipse (dashed) draws itself clockwise from angle 0
- The ellipse aligns with the long axis of the point cloud
- Duration: 3 full seconds for the stroke to complete
- Text cue: *"Covariance ellipse — where states scatter"*
- Small label near the ellipse's long axis: "high variance"

**BEAT 4 — Precision ellipse traces** (frames 289–384, ~4 sec)
- Orange ellipse draws itself, same center
- It is the *inverse* geometry: shorter where covariance is long, longer where covariance is short
- The orange ellipse is perpendicular to the gray ellipse in its principal axes
- Both ellipses remain visible simultaneously
- Text cue: *"Precision ellipse (Q = Σ⁻¹) — which directions are constrained"*
- Two label arrows appear:
  - Pointing along orange short axis: "large Q — strong constraint"
  - Pointing along orange long axis: "small Q — weak constraint / almost free"

**BEAT 5 — Tightening demonstration** (frames 385–480, ~4 sec)
- The orange precision ellipse *morphs* — the short axis shrinks further
  (simulating an increase in Q[1,2], tighter x₁–x₂ coupling)
- The point cloud *squeezes* along that direction correspondingly
- The gray covariance ellipse updates to match
- Label fades in: "increase Q[1,2] → stronger conditional coupling"
- Then the ellipse morphs back to original shape

**BEAT 6 — Transition hold** (frames 481–552, ~3 sec)
- Orange precision ellipse fades to 50%, cloud fades to 30%
- Large bold text fades in (center, white):
  ```
  Q tells us how the stationary density is shaped
  ```
- Sub-text below, gray, smaller:
  ```
  High Q[i,j]: knowing xᵢ constrains xⱼ directly
  ```
- After 2 seconds, text fades and scene transitions

---

## SCENE 2 — Diffusion Input
**Duration**: ~20 seconds (frames 553–1032)  
**Scene label**: "2 / D — fluctuation input"

### Purpose
Establish D as the object encoding where randomness *enters* the system.
The viewer should leave thinking: "D is about the noise source, not the steady state."

### Misconception corrected
"D is the covariance." D is the innovation variance per time step.
The same stationary distribution (same Q) can arise from different D.

---

**BEAT 1 — Scene transition** (frames 553–600, ~2 sec)
- Point cloud and precision ellipse fade to 20% (ghost background)
- A new faint gray ellipse (same stationary distribution) holds in background
- Text cue bottom: *"Same stationary distribution throughout..."*
- Scene label updates: "2 · D"

**BEAT 2 — Introduce D as local noise kicks** (frames 601–672, ~3 sec)
- A single large blue dot appears at the center of the distribution
- Around it: a small teal circle appears, growing slowly
- Text cue: *"At each moment, the system receives a random kick..."*
- The circle represents the distribution of one-step innovations
- Label next to circle: "D = uncertainty per step"

**BEAT 3 — Isotropic D case** (frames 673–768, ~4 sec)
- 15 blue starting dots scatter to positions within the stationary cloud
- At each dot: a small teal circle (D = I shape)
- All circles are identical — perfect circles
- From each dot: 8 short random "step" lines radiate in random directions,
  all of equal length
- The steps land on new positions (teal dots)
- Text cue: *"D = I — equal fluctuations in every direction"*
- Label below the circle icons: "isotropic"

**BEAT 4 — Morphing to anisotropic D** (frames 769–864, ~4 sec)
- The teal circles smoothly deform into tall vertical ellipses
  (D[2,2] >> D[1,1])
- The random step lines correspondingly stretch upward
- New positions are predominantly above/below starting positions
- Text cue: *"D anisotropic — x₂ receives more fluctuation"*
- Small bar icons appear: two bars labeled "D[1,1]" (short) and "D[2,2]" (tall)

**BEAT 5 — Morphing to correlated D** (frames 865–960, ~4 sec)
- The teal ellipses tilt to ~45°
- Steps now have a systematic diagonal component
- Text cue: *"D off-diagonal — x₁ and x₂ fluctuate together"*

**BEAT 6 — Contrast panel** (frames 961–1032, ~3 sec)
- Three small side-by-side sub-panels appear at the top of the frame:
  - Panel a: circle icon + label "D = I"
  - Panel b: vertical ellipse + label "D diagonal"
  - Panel c: tilted ellipse + label "D correlated"
- The main stationary cloud (background) brightens back to full opacity
- Text cue (large, white):
  ```
  D tells us where new fluctuations enter
  ```
- Sub-text, gray:
  ```
  D changed — stationary distribution (Q) did not
  ```

---

## SCENE 3 — Current and Flow
**Duration**: ~15 seconds (frames 1033–1392)  
**Scene label**: "3 / Ω — flow"

### Purpose
Establish that current (Ω) encodes *dynamics through* state space, not the
shape of the stationary distribution. Two systems with identical Q can have
different Ω.

### Misconception corrected
"If I know where states live, I know how the system moves."
False for non-equilibrium systems. Q is silent on circulation.

---

**BEAT 1 — Scene setup** (frames 1033–1080, ~2 sec)
- Previous elements fade out
- New canvas: only the stationary density ellipse remains (gray, 50% opacity)
- Scene label: "3 · Ω"
- Text cue: *"Same stationary distribution — same Q..."*

**BEAT 2 — Split screen** (frames 1081–1128, ~2 sec)
- A thin white vertical line appears down the center, dividing the canvas
- Left label (white, top): "Detailed balance"
- Right label (purple, top): "Circulating current"
- Both sides show the same gray density ellipse

**BEAT 3 — Equilibrium dynamics (left)** (frames 1129–1224, ~4 sec)
- On the LEFT: 6 dark blue particles appear at random positions inside the ellipse
- They undergo symmetric random walks (no net directionality)
- Trails fade quickly (alpha 0 after 12 frames)
- The motion is diffuse, criss-crossing, no orbital tendency
- Small "Ω = 0" label appears below the left panel

**BEAT 4 — Circulating dynamics (right)** (frames 1129–1224, same frames as Beat 3)
- On the RIGHT: same 6 particles at mirror positions
- They follow clockwise orbits around the density ellipse
- Faint purple streamlines trace the flow field (arrows pointing clockwise)
- The density ellipse is identical to the left side
- Small "Ω ≠ 0" label appears below the right panel

**BEAT 5 — Freeze and annotate** (frames 1225–1296, ~3 sec)
- Particles freeze
- On the left: a "⟷" icon with label "same Q" centered under both panels
- The density ellipses on both sides glow briefly (orange outline) to emphasize they are identical
- The streamlines on the right brighten
- Text cue (full width, large):
  ```
  Identical Q — identical where
  Different Ω — different how
  ```

**BEAT 6 — Time-reversal reveal** (frames 1297–1368, ~3 sec)
- On the RIGHT: the particles reverse direction (counter-clockwise)
- Text appears on right: "time-reversed: different path"
- On the LEFT: the particles "run in reverse" — but the random walk is symmetric,
  so the motion looks statistically identical
- Text appears on left: "time-reversed: indistinguishable"
- Label connecting both: "Ω ≠ 0 means the system breaks time-reversal symmetry"

**BEAT 7 — Hold and transition** (frames 1369–1392, ~1 sec)
- Large text fades in (white):
  ```
  Ω describes movement through state space
  ```

---

## SCENE 4 — The Combination: Ω = DQ + A
**Duration**: ~22 seconds (frames 1393–1920)  
**Scene label**: "4 / Ω = DQ + A"

### Purpose
Show mechanically how D and Q combine to produce Ω, and why non-uniform D
changes the current structure.

### Misconception corrected
"Ω is always a richer object than Q." Only when D is non-uniform.
When D ≈ constant·I, Ω is a scaled copy of Q and adds nothing.

---

**BEAT 1 — Setup: three objects** (frames 1393–1464, ~3 sec)
- Three rectangular panels appear horizontally across the frame:
  - LEFT panel (orange outline): "Q"
    Inside: the tilted covariance/precision ellipse from Scene 1 (orange)
  - CENTER panel (teal outline): "D"
    Inside: a teal circle (isotropic case first)
  - RIGHT panel (purple outline): "Ω"
    Inside: empty at first, "?" text
- Between LEFT and CENTER: a "×" symbol
- Between CENTER and RIGHT: a "=" symbol
- Text cue: *"Ω = DQ + A"*
  Sub-text, gray: *"(A is the antisymmetric drift — fixed wiring)"*

**BEAT 2 — Computing Ω: uniform D case** (frames 1465–1560, ~4 sec)
- Animation: the teal circle in the D panel "multiplies" the orange ellipse in Q
  - Visual metaphor: the circle icon "stamps" each point on the Q ellipse
  - The result: a purple ellipse appears in the Ω panel — same orientation as Q
- The Ω ellipse and Q ellipse are shown side-by-side briefly:
  they have the same orientation but different scale
- Flow arrows appear in the Ω panel (purple, pointing along the ellipse)
- Text cue: *"D = constant · I → Ω looks like a rescaled Q"*
- Small equation hint (gray, bottom): "D ≈ σ²I → Ω = σ²·Q + A"

**BEAT 3 — Morphing D to anisotropic** (frames 1561–1656, ~4 sec)
- The teal circle in the D panel slowly deforms into a tall vertical ellipse
- As it deforms, the purple Ω ellipse in the right panel *rotates*
  — it is no longer aligned with the Q ellipse
- New flow arrows appear: they point in a direction that is NOT the principal axis of Q
- Text cue: *"D non-uniform → Ω rotates away from Q"*
- Two ellipses shown side-by-side at the bottom of the frame:
  - Left: Q ellipse (orange)
  - Right: Ω ellipse (purple), clearly different orientation
  - Label: "Same Q, different D → different Ω"

**BEAT 4 — The critical comparison** (frames 1657–1752, ~4 sec)
- Split screen: left half = "D ≈ I", right half = "D non-uniform"
- LEFT: Q ellipse and Ω ellipse overlaid — they align nearly perfectly
  Label: "Ω ≈ Q — no new information"
- RIGHT: Q ellipse and Ω ellipse overlaid at different angles
  Label: "Ω reveals structure Q cannot"
- Text cue (full width):
  ```
  The utility of Ω depends on whether D is non-uniform
  ```

**BEAT 5 — Metaphor reveal** (frames 1753–1848, ~4 sec)
- The geometric panels fade to 30%
- Three icon-plus-text rows appear (bottom-up reveal, one per 1 second):
  ```
  [MAP ICON]    Q  =  road map   (geometry of constraint)
  [CAR ICON]    D  =  traffic volume   (fluctuation intensity)
  [FLOW ICON]   Ω  =  traffic organization   (effective flow)
  ```
- Each row appears with a short horizontal line connecting icon to text
- Colors: orange for Q row, teal for D row, purple for Ω row
- Text cue: *"Same road map. Different traffic. Different flow."*

**BEAT 6 — Hold** (frames 1849–1920, ~3 sec)
- Metaphor rows hold at full opacity
- Sub-text, gray:
  ```
  When D is uniform, Ω is just a rescaled Q
  When D is non-uniform, Ω shows new structure
  ```

---

## SCENE 5 — Worm Connection
**Duration**: ~15 seconds (frames 1921–2280)  
**Scene label**: "5 / C. elegans"

### Purpose
Honestly connect to the worm result. Show that D and Q both reorganize,
but Ω collapses to Q because z-scoring flattens D.
Do NOT imply Ω is better in the worm. Do NOT imply Ω is always equivalent to Q.

### Misconception corrected
"If Ω didn't add information in the worm, the framework is wrong."
The framework is correct. This particular preprocessing (z-scoring) makes D ≈ I,
which is a *property of the dataset and pipeline*, not a limitation of Ω.

---

**BEAT 1 — Transition to worm** (frames 1921–1968, ~2 sec)
- All prior objects fade out
- Scene label: "5 · C. elegans"
- Text cue (large, white): *"What happened in C. elegans?"*

**BEAT 2 — Three-column layout appears** (frames 1969–2016, ~2 sec)
- Three equal columns appear with headers:
  - Left: "D" (teal)
  - Center: "Q" (orange)
  - Right: "Ω" (purple)
- Dividing lines appear between columns

**BEAT 3 — D column animates** (frames 2017–2064, ~2 sec)
- In the D column: a small bar chart of ~10 neurons appears
- Bars morph between "dwelling" and "roaming" heights
- Two bars highlight in teal: "URXL ↑ roaming"
- Two bars highlight in orange: "AIZL ↓ roaming"
- Sub-text in column: "ρ(D_r, D_d) ≈ 0.14  rank reshuffles"

**BEAT 4 — Q column animates** (frames 2065–2112, ~2 sec)
- In the Q column: two modules (small circles) labeled "DA" and "URY"
- A connecting edge between them: thin during dwelling, thickens during roaming
- Sub-text in column: "DA_mech ↔ URY_URX  ΔQ signal"

**BEAT 5 — Ω column animates** (frames 2113–2160, ~2 sec)
- In the Ω column: a small scatter plot of ΔΩ vs ΔQ
- Points fall near-perfectly on the diagonal line
- The diagonal is labeled: "ρ = 0.9999"
- Sub-text in column: "ΔΩ ≈ ΔQ  (z-scoring flattens D)"

**BEAT 6 — The convergence arrow** (frames 2161–2208, ~2 sec)
- A curved purple arrow draws itself from the Ω column to the Q column
- Label on the arrow: "reduces to →"
- The Ω column text dims slightly

**BEAT 7 — Honest summary** (frames 2209–2280, ~3 sec)
- Text fades in full-width at the bottom, white:
  ```
  In this dataset, current does not add significant biological information
  beyond precision for the PDF-modulated case.
  ```
- Then below it, orange:
  ```
  Primary object: ΔQ
  ```
- Then below that, gray:
  ```
  D reorganization is a separate biological finding (independent of Ω)
  ```
- Final small text, very bottom, smallest font, gray italic:
  ```
  Ω ≠ Q in general — only when D ≈ I after preprocessing (e.g. z-scoring)
  ```

---

## SUCCESS CRITERIA CHECKLIST

After watching this animation, a viewer should be able to answer:

| Question | Scene where the answer is given |
|---|---|
| What does Q show? | Scene 1 — precision ellipse, constraint geometry |
| What does D show? | Scene 2 — noise kicks, directional fluctuations |
| What does Ω show? | Scene 3 — circulation / flow, not density |
| Why can Ω differ from Q? | Scene 4 — non-uniform D rotates Ω away from Q |
| Why the same biology in worm? | Scene 5 — z-scoring makes D ≈ I, so Ω ≡ Q |

---

---

## VIS-1F GEOMETRY AND LABEL FIXES (applied in v4)

### Scene 1 — Precision geometry corrected
- Removed the separate `make_ellipse(PREC)` object, which was geometrically misleading
  (it used `width = 2·scale·√λ_PREC` which gives a large axis in the strongly-constrained
  direction — the opposite of the correct geometry).
- Now shows a **single confidence ellipse** (`make_ellipse(COV)`) with two DoubleArrow
  axis annotations drawn along the actual principal directions of the ellipse:
  - **Orange DoubleArrow** along the **SHORT axis** (half-length 0.67 units) →
    labels "Large Q / Strongly constrained". Short = narrow spread = high precision.
  - **Teal DoubleArrow** along the **LONG axis** (half-length 2.51 units) →
    labels "Small Q / Weakly constrained". Long = broad spread = low precision.
  - Visual length contrast (1.34 vs 5.02 units) directly encodes the constraint
    difference.
- Callout labels placed outside the dense cloud region with pointer arrows:
  orange label at (−3.5, 1.55) → tip (−0.37, 0.56); teal label at (4.0, 0.55) → tip (2.09, 1.39).
- Axis labels ("Neuron 1 activity", "Neuron 2 activity") repositioned to arrow tips
  using `next_to(ax.x_axis.get_right(), DOWN)` and `next_to(ax.y_axis.get_top(), UP)`.
- No "tightening" animation. No separate precision ellipse. Geometry is unambiguous.

### Text rendering
- `halo()` background-stroke width reduced from 8 → 3.
  Width-8 strokes were causing text to appear heavy/blurry at 720p.
  Width-3 gives a clean thin outline sufficient for readability over the data cloud.

---

## VIS-1D CONCEPTUAL REVISIONS (applied in v2)

### Scene 1 — Q
- Added coordinate axes with labels "Neuron 1 activity" / "Neuron 2 activity"
- Added "Each point = one moment in time" as initial cue
- Precision ellipse given `z_index=5` so it never disappears behind the cloud
- Removed tightening animation; replaced with steady axis-label arrows
- Summary cue changed to: "Q describes which combinations of activity are constrained."

### Scene 2 — D
- Axes remain visible for context
- Opening cue: "D describes fluctuations entering the system." (not an isotropy claim)
- Noise kicks shown as explicit Arrow objects radiating from state positions
- Faint envelope ellipse retained only as a secondary visual; arrows are primary
- Three cases shown sequentially: isotropic → anisotropic → correlated
- No mention of "D ≈ I" or z-scoring at this stage

### Scene 3 — Ω
- Left/right panel labels changed to "Equilibrium Ω = 0" / "Non-equilibrium Ω ≠ 0"
- Added "Same density on both sides" label between panels
- Cue text changed to: "Same states visited. Different routes through those states."
- Closing cue: "Ω is movement, not occupancy."

### Scene 4 — Ω = DQ + A
- **Ω panel is now a flow-field (arrows), not an ellipse.**
  An ellipse would falsely suggest Ω is another covariance object.
  Flow arrows correctly communicate "movement through state space."
- Q panel: precision ellipse (geometry of constraint)
- D panel: kick arrows + faint envelope (fluctuation input)
- Sub-labels: "Geometry of constraint" / "Fluctuation input" / "Flow through state space"
- Cue progression: "Q tells us where states relate" → "D tells us where fluctuations enter"
  → "Ω tells us how activity moves through state space"

### Scene 5 — Worm
- **No neuron names.** Uses biological functional labels throughout:
  Gas sensing, Food sensing, Motor control, Local search
- **D panel**: grouped bar chart with DWELLING (orange) and ROAMING (teal) bars
  per functional group; shows absolute innovation variance, not just ΔD
  Cue: "Gas sensing fluctuates more during roaming. Local search fluctuates more during dwelling."
- **Q panel**: two network diagrams (DWELLING / ROAMING) side by side
  Nodes: "Food sensing" and "Gas sensing"
  Edge thickness differs between states
  Cue: "Food sensing ↔ Gas sensing: conditional coupling strengthens during roaming."
- **Ω panel**: checklist showing D reorganizes ✓, Q reorganizes ✓, Ω combines both
  Box: "Same biological interpretation"
  Cue: "The current formulation incorporates both reorganizations.
  In this dataset, it does not change the biological conclusion."
- **Removed**: "ρ = 0.9999", "Ω collapses to Q", "D ≈ I", "z-scoring kills D non-uniformity"
  These statements are no longer supported as the final framing.

### Final card (v2)
```
D:  Which neurons become dynamically variable?
Q:  Which neurons become conditionally linked?
Ω:  Combines both reorganizations.

Result:  Same biological interpretation for the PDF-associated circuit.

Different mathematics.   Same biological conclusion.
```

---

## PRODUCTION NOTES

### Recommended implementation: Manim Community
```
manim -pqh animation_dq_current.py DQCurrentAnimation
```

Scene class structure suggestion:
```
class DQCurrentAnimation(Scene):
    def scene1_precision(self): ...
    def scene2_diffusion(self): ...
    def scene3_current(self): ...
    def scene4_combination(self): ...
    def scene5_worm(self): ...
    def construct(self):
        self.scene1_precision()
        self.scene2_diffusion()
        ...
```

### Alternative: matplotlib.animation
If Manim is not available, the animation can be rendered in segments using
`matplotlib.animation.FuncAnimation` with FFMpeg writer, then concatenated.
Quality will be lower for ellipse morphing transitions.

### Key implementation challenges
1. **Ellipse morphing** (Beats 4–5 in Scene 1, Beats 3–4 in Scene 4):
   Parametrize both ellipses by their covariance matrices; interpolate the
   matrix elements linearly in time; recompute the Ellipse patch each frame.

2. **Particle trajectories** (Scenes 2–3):
   Use Euler–Maruyama integration at 24fps. Store trajectories as numpy arrays
   before the animation loop; play back during rendering for speed.

3. **Flow field arrows** (Scenes 3–4):
   Use `ax.quiver` for static snapshots; for animated arrows, update U/V arrays
   each frame using the interpolated Ω matrix.

4. **Text fade transitions**:
   Interpolate `Text.set_alpha()` over 8 frames between 0 and 1.

### File size target
- Full resolution (1920×1080 at 24fps, ~90 seconds): ~15–25 MB MP4
- Web version (1280×720): ~8–12 MB
- GIF version (800×450 at 15fps): ~25–40 MB (consider splitting by scene)

### Export path
```
results/visualization/dq_to_current_animation.mp4
results/visualization/dq_to_current_animation_720p.mp4  (web version)
```

---

## FRAME TIMING SUMMARY

| Scene | Start frame | End frame | Duration |
|---|---|---|---|
| Title card | 1 | 72 | 3.0 s |
| Scene 1: Q geometry | 73 | 552 | 20.0 s |
| Scene 2: D diffusion | 553 | 1032 | 20.0 s |
| Scene 3: Current | 1033 | 1392 | 15.0 s |
| Scene 4: Ω = DQ + A | 1393 | 1920 | 22.0 s |
| Scene 5: Worm | 1921 | 2280 | 15.0 s |
| **Total** | | | **95.0 s** |

At 24 fps: 2280 frames.

---

*PHASE VIS-1A: animation storyboard addendum. No new data analysis performed.*
