# Storyboards: D, Q, Ω, Current Velocity
## Panel-by-Panel Specifications
Date: 2026-06-04
Authorization: PHASE VIS-1

Format: Text storyboards with ASCII layout sketches.
Audience: Neuroscientists, physicists, systems biologists.
Tone: Explanatory. Build intuition first, connect to biology second.

---

## FIGURE 1 STORYBOARD — "What Q Sees"

### Panel dimensions: 1 row × 2 columns

```
┌─────────────────────────────┬─────────────────────────────┐
│  LEFT PANEL                 │  RIGHT PANEL                │
│                             │                             │
│  "What the covariance sees" │  "What Q sees"              │
│                             │                             │
│  ·  · ·  ·                  │  ·  · ·  ·                  │
│   · ·●·· ·                  │   · ·●·· ·                  │
│  ·   ··  ·                  │  ·   ··  ·                  │
│                             │                             │
│  Gray dashed ellipse =      │  Faint gray ellipse behind  │
│  1σ covariance contour      │  (same points)              │
│  Elongated toward x₁-x₂     │                             │
│  correlation direction      │  ORANGE SOLID ellipse =     │
│                             │  precision contour          │
│  Arrow: "spread here"       │  (perpendicular orientation)│
│                             │                             │
│                             │  Arrows on short axis:      │
│                             │  "Large Q → strong          │
│                             │   constraint here"          │
│                             │                             │
│                             │  Arrows on long axis:       │
│                             │  "Small Q → almost free"    │
└─────────────────────────────┴─────────────────────────────┘
```

### Annotation layer (applied to right panel only)
- Dashed line connecting one scatter point to the precision ellipse
  boundary, labeled: "A point outside the precision ellipse is
  statistically unlikely given its neighborhood"
- Bottom legend: Gray = covariance / Orange = precision

### Narrative caption (below figure)
> "The covariance tells you where states are.
>  The precision matrix Q tells you which relationships are enforced.
>  These are not the same thing: a pair can co-vary strongly
>  due to a shared third partner while having a small direct Q entry."

### Transition to next figure
Small text bottom-right: "Next: where do fluctuations enter? →"

---

## FIGURE 2 STORYBOARD — "What D Sees"

### Panel dimensions: 1 row × 3 columns

```
┌───────────────┬───────────────┬───────────────┐
│  PANEL A      │  PANEL B      │  PANEL C      │
│  Isotropic D  │  Anisotropic  │  Correlated   │
│               │               │               │
│      ○        │               │               │
│    ○●○        │    ○ ○        │   ○           │
│      ○        │    ●          │  ●            │
│               │    ○          │  ○            │
│               │               │               │
│  Circle of    │  Tall ellipse │  Tilted       │
│  trajectories │  along x₂    │  ellipse      │
│               │               │               │
│  D = σ²·I    │  D[1,1] >> D  │  D off-diag   │
│               │  [2,2]        │  ≠ 0          │
│  "x₁ and x₂  │  "x₂ gets    │  "x₁ and x₂  │
│   fluctuate   │   most noise" │   fluctuate   │
│   equally"    │               │   together"   │
└───────────────┴───────────────┴───────────────┘
```

### Key device: ghost stationary distribution
In all three panels, draw the same faint gray stationary density contour.
This emphasizes: D changes, the stationary distribution (set by Q) stays the same.
Label: "Same Q, same stationary distribution, different D"

### Narrative caption
> "D is not the covariance. D tells you where randomness enters.
>  You can have the same steady state (same Q) with very different
>  innovation structure (different D). D[i,i] is how much neuron i
>  wiggles due to private noise. D[i,j] ≠ 0 means neurons i and j
>  receive correlated noise from a shared upstream source."

### Worm callback panel (bottom strip, across all three panels)
Small bar chart embedded below panels showing ΔD per neuron (worm data).
Two bars highlighted: URXL (roaming-dominant), AIZL (dwelling-dominant).
Label: "In the worm: D reorganizes by ~25% between roaming and dwelling,
        with ρ(D_roam, D_dwell) ≈ 0.14"

---

## FIGURE 3 STORYBOARD — "What Ω Sees"

### Panel dimensions: 1 row × 3 columns

```
┌───────────────┬───────────────┬───────────────┐
│  PANEL A      │  PANEL B      │  PANEL C      │
│  Ω = 0        │  Ω ≠ 0        │  Ω reversed   │
│  (Equilibrium)│  (Circulating)│  (Time mirror)│
│               │               │               │
│  ◎            │  ◎            │  ◎            │
│  Density      │  Density      │  Density      │
│  contours     │  contours     │  contours     │
│  (same in all │  (same in all │  (same in all │
│   three)      │   three)      │   three)      │
│               │               │               │
│  No arrows    │  ↑ → ↓ ←     │  ↓ ← ↑ →     │
│               │  Clockwise    │  Counter-CW   │
│               │  streamlines  │  streamlines  │
│               │               │               │
│  "Bounces     │  "Spirals     │  "Spirals     │
│   back and    │   around"     │   the other   │
│   forth"      │               │   way"        │
└───────────────┴───────────────┴───────────────┘
```

### Key device: single trajectory trace
In Panel A: Draw a squiggly path that jumps around without directionality.
In Panel B: Draw a path that spirals/circulates around the density contour.
In Panel C: Same path as B but with arrows reversed.

Label connecting all three: "Same stationary distribution → same Q"
Label distinguishing B and C from A: "Different current → different Ω"

### Time-reversal inset (sidebar right)
Small sketched pair:
- Panel B trajectory (forward time)
- Mirror image of Panel B trajectory (time-reversed)
These are DIFFERENT, confirming Ω ≠ 0.

For Panel A, both forward and time-reversed trajectories look the same.

### Narrative caption
> "Ω is about movement, not accumulation.
>  Two systems can have identical Q — identical stationary distributions —
>  but completely different Ω. One circulates. The other doesn't.
>  Only Ω distinguishes them."

### Worm callback
Bottom strip caption:
> "In the worm: diagonal D forces ΔΩ ≈ ΔQ. Current organization
>  is absorbed into the precision structure. Time-reversal asymmetry
>  is not independently accessible here."

---

## FIGURE 4 STORYBOARD — "From D and Q to Ω"

### Panel dimensions: 2 rows × 2 columns

```
┌──────────────────────┬──────────────────────┐
│  PANEL A             │  PANEL B             │
│  Q fixed, D isotropic│  Q fixed, D aniso.   │
│  (small)             │  large on x₁         │
│                      │                      │
│  Density ellipse     │  Density ellipse     │
│  (same both panels)  │  (same)              │
│                      │                      │
│  Small equal blobs   │  Tall blob along x₁  │
│  at each point       │  Small blob along x₂ │
│  (noise sources)     │  (noise sources)     │
│                      │                      │
│  Ω arrows: small,    │  Ω arrows: large     │
│  follow constraint   │  bias toward x₁      │
│  directions          │                      │
├──────────────────────┼──────────────────────┤
│  PANEL C             │  PANEL D             │
│  D large, isotropic  │  D correlated        │
│                      │  (off-diagonal)      │
│  Density ellipse     │  Density ellipse     │
│  (same)              │  (same)              │
│                      │                      │
│  Large equal blobs   │  Tilted 45° blobs    │
│  (same ratio as A)   │                      │
│                      │                      │
│  Ω arrows: large,    │  Ω arrows: rotated   │
│  same structure as A │  — new direction     │
│  (just scaled)       │  not in Q alone      │
└──────────────────────┴──────────────────────┘
```

### Visual metaphor sidebar (right margin)
Three labeled icons:
```
[MAP ICON]    Q = road map
              (where are the roads?)

[CAR ICON]    D = traffic volume
              (how many cars per lane?)

[FLOW ICON]   Ω = traffic organization
              (where does traffic actually go?)
```

### The key visual lesson
Draw a visual comparison at the bottom: "Same road map (Q), different traffic (D),
different effective flow (Ω)."
Show Panel A vs Panel D: same ellipse, completely different Ω arrows.

### Narrative caption
> "Ω = DQ + A. D is the weight. Q is the structure.
>  When D is uniform (Panel A, C), Ω is just a scaled version of Q.
>  When D is non-uniform (Panel B, D), Ω highlights directions that
>  Q alone underemphasizes. The biological question becomes:
>  Is D non-uniform in this system?"

### Worm annotation
Arrow from Panel A labeled: "CePNEM (after z-scoring): D ≈ 1.025·I → Ω ≈ Q"
Arrow from Panel B labeled: "Leech / OU cascade: D non-uniform → Ω ≠ Q"

---

## FIGURE 5 STORYBOARD — "What Happened in C. elegans?"

### Panel dimensions: 1 row × 3 columns (labeled A, B, C)

```
┌───────────────────┬───────────────────┬───────────────────┐
│  PANEL A          │  PANEL B          │  PANEL C          │
│  Diffusion        │  Precision        │  Current          │
│  Reorganization   │  Reorganization   │  Convergence      │
│                   │                   │                   │
│  Sorted bar chart │  Module diagram   │  Scatter plot     │
│  61 neurons       │                   │  ΔΩ vs ΔQ         │
│                   │  [DA_mech]        │                   │
│  █ URXL +0.21     │     ↕↕            │       ·  ·        │
│  █ URYVL +0.15    │  [URY_URX]        │    · ···          │
│  │ ...            │                   │   ···· ρ=0.9999   │
│  │ AIZL -0.17     │  Bold arrow =     │   ·               │
│  │ AVJR -0.15     │  ΔQ signal        │                   │
│                   │                   │  "Ω ≈ Q"          │
│  ρ(D_r,D_d)=0.14  │  ADEL→URYVR #5   │  "D is uniform    │
│  "Reshuffles"     │  PDF enriched     │   after z-scoring"│
└───────────────────┴───────────────────┴───────────────────┘
```

### Connective tissue between panels
Arrows between panels with labels:
- A→B: "Independent of each other (ρ ≈ 0.05)"
- B→C: "Ω = DQ → ΔΩ = D·ΔQ ≈ ΔQ (D ≈ 1)"

### Summary statement (full width, below all panels)
Box with text:
> "D reorganizes (Panel A): aerotaxis sensors become more driven during roaming.
>  Q reorganizes (Panel B): dopaminergic mechanosensory → aerotaxis pathway decouples.
>  Ω converges (Panel C): preprocessing makes D uniform, so Ω adds nothing.
>  The biological interpretation (Panel B) is stable and does not depend on Ω."

### Design note
Panel A can use a real-data-inspired sketch (the pattern from results/phase3e/e2).
Panels B and C should remain schematic to emphasize the conceptual message.
Do not use real neuron names in the final sketch — substitute with placeholder
labels A1, A2, B1, B2 until the figure reaches publication stage.

---

## FIGURE 6 STORYBOARD — "When Ω Matters"

### Panel dimensions: 3 rows (one per system) × 4 columns

```
┌──────────┬──────────────┬──────────────┬──────────┐
│ System   │ D structure  │ Ω structure  │ Verdict  │
├──────────┼──────────────┼──────────────┼──────────┤
│ OU       │ Non-uniform  │ Long-range   │    ✓     │
│ cascade  │ (inputs at   │ connections  │ Ω adds   │
│          │  one node)   │ visible      │ info     │
│          │ [elongated   │ [rotated     │          │
│          │  ellipse]    │  ellipse]    │          │
├──────────┼──────────────┼──────────────┼──────────┤
│ Leech    │ Heterogeneous│ Module       │    ✓     │
│          │ across       │ rankings     │ Ω adds   │
│          │ neurons      │ diverge from │ info     │
│          │ [irregular   │  Q           │          │
│          │  blob]       │              │          │
├──────────┼──────────────┼──────────────┼──────────┤
│ Worm     │ Near-uniform │ ΔΩ ≡ ΔQ      │    ✗     │
│ (this    │ after        │ (ρ = 0.9999) │ Ω = Q    │
│ study)   │ z-scoring    │              │ no gain  │
│          │ [perfect     │ [same        │          │
│          │  circle]     │  ellipse]    │          │
└──────────┴──────────────┴──────────────┴──────────┘
```

### "Information gain" visual bar (below table)
Three horizontal bars:

```
OU cascade  ████████████████ full
Leech       ████████░░░░░░░░ partial
Worm        ░░░░░░░░░░░░░░░░ none
```

### Causal arrow
Above the table: "What determines whether Ω adds information?"
Arrow: D non-uniform → Ω ≠ Q → Ω adds information
Arrow: D uniform (e.g., z-scored) → Ω = Q → Ω adds nothing

### Narrative caption
> "Current organization is not universally necessary.
>  Its utility depends on whether D is non-uniform.
>  Z-scoring enforces uniform D and eliminates the Ω pathway.
>  This is not a failure of the framework —
>  it is information about the preprocessing choice."

### Key message
This figure is the punchline of the series. It should be presented LAST.
The viewer should feel: "I now understand why the worm result is not disappointing —
it is informative about the system and the measurement."

---

## Design Consistency Notes

### Color palette (consistent across all six figures)
- Stationary distribution / density: light gray (#D3D3D3) or faint blue
- Q / precision: deep orange (#E07B39)
- D / diffusion ellipses: teal (#2A9D8F)
- Ω / current arrows: purple (#6A0DAD)
- Trajectory traces: dark blue (#1A237E)
- Highlight (key pairs, key neurons): red (#C0392B)
- Background: white

### Typography
- Panel labels (A, B, C): 14pt bold
- Axis labels: 11pt
- Callout text in panels: 9pt, not in bold
- Figure captions: 10pt, full width

### Figure sizing
- Figures 1–4: target 14 cm × 7 cm (two-column journal width, landscape)
- Figure 5: target 18 cm × 7 cm (three-panel, landscape)
- Figure 6: target 12 cm × 10 cm (portrait table)

### Anti-patterns to avoid
- No equations in panel interiors (equations belong in captions only)
- No more than two overlaid elements per panel
- No 3D plots (all figures are 2D)
- No color maps — use single colors with opacity variation

---

*PHASE VIS-1: storyboard package. No new data analysis performed.*
