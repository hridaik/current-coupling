# Animation Storyboards: D, Q, Ω, Current Velocity
## Three Short Animations
Date: 2026-06-04
Authorization: PHASE VIS-1

Target runtime per animation: 20–40 seconds.
Format: Looping GIF or MP4. No audio required.
Intended use: Seminar slides, lab website, supplementary materials.

---

## ANIMATION 1 — "Diffusion Reorganization"
### Subtitle: "Same stationary distribution, different D"

**Concept**: Show particles diffusing from a starting point, then change D and
show the diffusion pattern change — while the stationary distribution stays constant.

---

### Frame sequence

**Frames 1–10: Setup (1–2 sec)**
- 2D state space appears
- Faint gray ellipse drawn slowly: "stationary distribution"
- Title card fades in: "Same where states live..."

**Frames 11–25: Isotropic diffusion (2–3 sec)**
- 20 colored dots appear at center
- Dots spread outward as a circle
- Circle slowly matches the stationary distribution ellipse
- Label: "D = σ²·I — isotropic noise"

**Frames 26–35: Transition (1 sec)**
- Dots reset to center
- Subtle color shift in D blobs

**Frames 36–50: Anisotropic diffusion (2–3 sec)**
- Same 20 dots at center
- Dots spread as a vertical ellipse (x₂ fluctuates more)
- The stationary ellipse stays unchanged
- Label: "D[2,2] >> D[1,1] — x₂ gets more noise"

**Frames 51–60: Transition (1 sec)**
- Dots reset again

**Frames 61–80: Correlated diffusion (2–3 sec)**
- Dots spread as a tilted ellipse (45°)
- Stationary ellipse unchanged
- Label: "Off-diagonal D — correlated noise"

**Frames 81–90: Summary hold (2 sec)**
- All three spreading patterns shown simultaneously (three clusters side by side)
- Stationary distribution highlighted: "Q unchanged across all"
- D sketches shown below each: circle, tall ellipse, tilted ellipse

**Loop**: Return to frame 1.

---

### Design notes
- Dot colors: teal for D=isotropic, deep orange for D=anisotropic, purple for D=correlated
- Stationary ellipse: light gray, stays fully visible throughout
- Spreading animation: use alpha falloff on dots as they move away from center
- Transition between cases: quick fade (10 frames), not a cut

### Key message to communicate in the animation
The spreading pattern (D) changes. The final distribution (Q) does not.
These are controlled by different parts of the system.

---

## ANIMATION 2 — "Same Density, Different Currents"
### Subtitle: "Ω is about movement, not accumulation"

**Concept**: Hold the stationary distribution fixed, show two different flow fields
(circulating vs equilibrium), and let the viewer observe that the density is
identical but the dynamics are completely different.

---

### Frame sequence

**Frames 1–10: Setup (2 sec)**
- 2D state space appears
- Fixed density ellipse (gray) fills in
- Title card: "Same stationary distribution..."

**Frames 11–15: Split screen appears (1 sec)**
- Screen divides left/right with vertical divider
- Left label: "Detailed balance (Ω = 0)"
- Right label: "Circulating current (Ω ≠ 0)"
- Both sides show the same density ellipse

**Frames 16–50: Simultaneous particle dynamics (5–6 sec)**
LEFT SIDE:
- 10 particles release from center of density
- Particles bounce around randomly within density contour
- No net directionality
- Trajectory is irregular, criss-crossing

RIGHT SIDE:
- Same 10 particles release from same positions
- Particles circulate around the density contour (orbit)
- Density cloud looks the same
- Trajectory follows the current arrows (shown as faint blue streamlines)

**Frames 51–60: Freeze and highlight (2 sec)**
- Particles freeze
- Current streamlines brighten on right side
- "No arrows" text on left side
- Text overlay: "Identical Q — identical where. Different Ω — different how."

**Frames 61–80: Time reversal test (3 sec)**
- On right side: particles reverse direction (counter-clockwise now)
- Label: "Time-reversed: different"
- On left side: particles reverse direction
- Label: "Time-reversed: same"
- Text: "Ω ≠ 0 means time-reversal changes the dynamics"

**Frames 81–90: Summary (2 sec)**
- Small icons below each side
- Left: "Q only" icon
- Right: "Q + Ω" icon
- Caption: "You need Ω to detect irreversibility"

**Loop**: Return to frame 1.

---

### Design notes
- Density ellipse: same gray on both sides, never changing
- LEFT particles: random walk inside density, dark blue
- RIGHT particles: orbit driven by clockwise flow field, purple
- Current streamlines on right: faint purple arrows, drawn first then revealed
- Time reversal: simply reverse particle velocity vectors mid-animation

### Key message to communicate
Two systems can look identical in terms of what states they occupy (same Q)
but differ in how they move through those states (different Ω). Without tracking
trajectories over time, you cannot distinguish them from a snapshot.

---

## ANIMATION 3 — "Worm Summary: D → Q → Ω"
### Subtitle: "Why ΔΩ ≈ ΔQ in C. elegans"

**Concept**: Walk through the worm result as a 3-act animation. Act 1: D reorganizes
between states. Act 2: Q reorganizes independently. Act 3: Ω is computed and
collapses to Q.

---

### Frame sequence

**ACT 1: Frames 1–30 — D reorganizes (5–6 sec)**

Frame 1–5: Title card "Act 1: Diffusion reorganizes between states"

Frame 6–15: Show two D "fingerprints" side by side
- LEFT: D during DWELLING — bar chart of per-neuron variances
  - Bars are moderate height, relatively uniform
  - Highlight: AIZL and AVJR are tallest
- RIGHT: D during ROAMING — same neurons, different bar heights
  - Highlight: URXL and URYVL are now tallest
  - AIZL and AVJR are now short

Frame 16–25: Animate the transition between the two bar charts
- Bars morph from DWELLING to ROAMING
- Color coding: neurons that gain variance = teal; neurons that lose = orange

Frame 26–30: Hold with caption
- "ρ(D_roam, D_dwell) ≈ 0.14 — almost completely reshuffled"
- "These neurons are more driven during roaming" (arrow to URXL/URYVL)
- "These are more driven during dwelling" (arrow to AIZL/AVJR)

---

**ACT 2: Frames 31–60 — Q reorganizes independently (5–6 sec)**

Frame 31–35: Title card "Act 2: Precision reorganizes independently"

Frame 36–45: Show module connection diagram
- Six modules shown as labeled nodes: DA_mech, URY_URX, RME, RMD_SMD, IL1_IL2, RID
- During DWELLING: thin gray edges connecting all
- During ROAMING: same edges, but DA_mech ↔ URY_URX edge becomes thick and highlighted

Frame 46–55: Animate the edge thickness change
- Edge DA_mech ↔ URY_URX grows from thin to thick
- Label appears: "ADEL → URYVR: rank 5 in ΔQ"
- Second label: "PDF-signaling enrichment: AUROC = 0.556"

Frame 56–60: Small text at bottom
- "ρ(ΔD, ΔQ) ≈ 0.05 — diffusion and precision reorganize independently"

---

**ACT 3: Frames 61–90 — Ω is computed and collapses to Q (5–6 sec)**

Frame 61–65: Title card "Act 3: Ω = DQ — but D is nearly uniform here"

Frame 66–75: Show the D "fingerprint" from Act 1
- Then show it being "flattened" — a horizontal bar sweeping across, making all bars
  equal height
- Caption: "z-scoring: forces variance ≈ 1 per neuron"
- D bars equalize → round circle icon

Frame 76–82: Compute ΔΩ
- Two columns: ΔQ ranked list (left), ΔΩ ranked list (right)
- Pairs connected by lines — lines are straight (no crossing)
- Label: "ρ(ΔΩ, ΔQ) = 0.9999 — identical ranking"

Frame 83–90: Punchline
- The two columns merge into one
- Caption: "ΔΩ ≈ ΔQ — current organization collapses to precision here"
- Subtitle: "The biology is in Q. Ω does not change the interpretation."

**Final frame (90–100): Summary card**
```
D reorganizes:  urxl, uryvl ↑ roaming
                aizl, avjr  ↑ dwelling

Q reorganizes:  DA_mech ↔ URY_URX decouples
                PDF-enriched signal

Ω collapses:    ΔΩ ≈ ΔQ (z-scoring kills D non-uniformity)

Primary object: ΔQ
```

**Loop**: Return to frame 1.

---

### Design notes
- Act 1 (D): teal color scheme
- Act 2 (Q): orange color scheme
- Act 3 (Ω): purple color scheme
- Transition between acts: title cards with brief pause (2 sec)
- No equations visible inside frames — equations may appear in captions only
- Do not use real neuron names in presentation version — use "Node X" labels
  until figure is approved for public release

---

## Common Animation Production Notes

### Software options (in order of preference for this use case)
1. **Manim** — best for mathematical figures with smooth transitions
2. **matplotlib.animation** — fastest to prototype, acceptable quality
3. **After Effects / Keynote** — for non-code production

### Resolution and format
- Resolution: 1080×720 (16:9) or 800×800 (square for social/seminar)
- Frame rate: 24 fps
- Format: MP4 (H.264) for presentations, GIF for web embedding
- File size target: < 5 MB per animation

### Accessibility
- All color-coded information should also be distinguishable by shape or label
- Include text captions embedded in the animation (not just audio descriptions)
- Avoid rapid flashing (< 3 Hz is safe)

### Looping behavior
- Animations 1 and 2: clean loop (final frame matches first frame)
- Animation 3: single play or extended hold on final summary card before loop

---

*PHASE VIS-1: animation storyboards. No new data analysis performed.*

---

## ANIMATION 4 — "From Precision to Current"
### Subtitle: "D, Q, and Ω in a stochastic system"
### Authorization: PHASE VIS-1A addendum

**Target runtime**: ~95 seconds  
**Export path**: `results/visualization/dq_to_current_animation.mp4`  
**Full storyboard**: see `animation_DQ_current.md`

**Concept**: A single end-to-end animation that builds intuition for Q, D, Ω,
and current in the style of 3Blue1Brown — geometric first, biological application
last. Uses a 2D toy system for the first four scenes, then connects to the worm
result in the final scene.

---

### Five-Scene Structure

**SCENE 1 — Precision Geometry (~20 sec)**

Goal: establish Q as the geometry of constraint, not the geometry of spread.

Key visual: a 2D Gaussian cloud with two overlaid ellipses — the gray covariance
ellipse (where states scatter) and an orange precision ellipse (which directions
are tightly coupled). The precision ellipse *tightens* in one direction to show
what increasing Q[i,j] means.

On-screen text:
> *"Q tells us how the stationary density is shaped"*
> *"High Q[i,j]: knowing xᵢ constrains xⱼ directly"*

Misconception corrected: covariance and precision describe the same thing.
They describe orthogonal aspects: spread vs. constraint.

---

**SCENE 2 — Diffusion Input (~20 sec)**

Goal: establish D as the noise source, independent of the stationary distribution.

Key visual: the same stationary cloud stays in the background (faint gray) while
the foreground shows small teal "noise kick" ellipses at each point in state space.
Three cases:
- D = I: circular kicks, equal in all directions
- D diagonal anisotropic: kicks elongated along x₂
- D off-diagonal: kicks tilted at 45°

On-screen text:
> *"D tells us where new fluctuations enter"*
> *"D changed — stationary distribution (Q) did not"*

Misconception corrected: D is the covariance. D is the per-step innovation
variance; the stationary covariance is shaped by both D and the drift.

---

**SCENE 3 — Current and Flow (~15 sec)**

Goal: establish that Ω encodes dynamics through state space, not the shape
of the stationary distribution. Split-screen: equilibrium (left) vs. circulating
(right) — same density ellipse on both sides.

Key visual: particles orbit on the right; bounce randomly on the left.
Time-reversal test shown: reversing the circulating particles changes their path;
reversing the equilibrium particles does not.

On-screen text:
> *"Identical Q — identical where. Different Ω — different how."*
> *"Ω describes movement through state space"*

Misconception corrected: "the stationary distribution tells you everything
about the dynamics." False for non-equilibrium systems.

---

**SCENE 4 — The Combination: Ω = DQ + A (~22 sec)**

Goal: show why non-uniform D changes Ω, and why uniform D makes Ω ≡ Q.

Key visual: three panels (Q, D, Ω). The teal D circle "multiplies" the orange
Q ellipse to produce the purple Ω ellipse. When D = circle, Ω and Q have the
same orientation (just rescaled). When D elongates, the Ω ellipse *rotates*
away from Q.

Side-by-side comparison:
- D ≈ I: Q and Ω aligned → no new information
- D non-uniform: Q and Ω diverge → Ω reveals new structure

Metaphor overlay (appears one by one):
```
Q  =  road map         (geometry of constraint)
D  =  traffic volume   (fluctuation intensity)
Ω  =  traffic flow     (effective movement)
```

On-screen text:
> *"The utility of Ω depends on whether D is non-uniform"*
> *"Same road map. Different traffic. Different flow."*

Misconception corrected: "Ω always provides information beyond Q."
Only when D is non-uniform.

---

**SCENE 5 — Worm Connection (~15 sec)**

Goal: honestly summarize the C. elegans result. Three columns (D, Q, Ω).

- D column: bar chart morphing between roaming and dwelling states;
  URXL/URYVL gain, AIZL/AVJR lose; ρ(D_r, D_d) ≈ 0.14
- Q column: DA_mech ↔ URY_URX edge thickens; ΔQ signal
- Ω column: ΔΩ vs ΔQ scatter falls on the diagonal; ρ = 0.9999

A curved purple arrow draws from the Ω column to the Q column: "reduces to →"

On-screen text (final frame):
> *"In this dataset, current does not add significant biological information"*
> *"beyond precision for the PDF-modulated case."*
> *"Primary object: ΔQ"*

Small disclaimer (smallest font, bottom, gray italic):
> *"Ω ≠ Q in general — only when D ≈ I after preprocessing (e.g. z-scoring)"*

Misconception corrected: "If Ω didn't add information in the worm, the
framework is wrong." The framework is correct; z-scoring flattens D,
which is a property of this preprocessing pipeline.

---

### Summary: What the Viewer Learns

| Question | Scene |
|---|---|
| What does Q show? | 1 — constraint geometry, precision ellipse |
| What does D show? | 2 — noise input direction and magnitude |
| What does Ω show? | 3 — flow through state space, not density |
| Why can Ω differ from Q? | 4 — non-uniform D rotates Ω away from Q |
| Why same biology in worm? | 5 — z-scoring makes D ≈ I so Ω ≡ Q |

---

### Design notes
- Background: near-black (#0F0F14)
- Q objects: orange (#E07B39)
- D objects: teal (#2A9D8F)
- Ω / current objects: purple (#8B5CF6)
- Transitions: smooth easing, minimum 12 frames, no hard cuts
- Text: white primary, gray secondary; fades in, never sudden
- Equations: kept out of main visual layer; appear only as small captions

*PHASE VIS-1A: animation storyboard addendum. No new data analysis performed.*
