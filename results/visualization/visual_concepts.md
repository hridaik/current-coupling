# Visual Concepts: D, Q, Ω, and Current Velocity
## Intuition Package for Neuroscientists, Physicists, and Systems Biologists
Date: 2026-06-04
Authorization: PHASE VIS-1

---

## Framing Statement

This document describes the conceptual design of six explanatory figures and three
animations. The goal is to build intuition, not to prove theorems. Each section
specifies what the viewer should understand, what misconception it corrects, and how
it connects to the C. elegans findings.

These are storyboard-level descriptions. No new data analysis was performed.

---

## The Core Objects

Before the figures: a one-paragraph orienting description of each object.

**D — the diffusion matrix**
D encodes where fluctuations enter the system. Each diagonal element D[i,i] is
the innovation variance of variable i — how much it independently wiggles. Off-diagonal
elements D[i,j] encode whether variables i and j tend to fluctuate together
(correlated noise sources). D is about the *input* to the system: where the
randomness comes from.

**Q — the precision matrix**
Q is the inverse covariance matrix. Q[i,j] measures the direct conditional dependence
between variables i and j after accounting for all other variables. Large Q[i,j] means
i and j are tightly coupled: knowing one tells you about the other, even holding
everything else fixed. Q encodes the *geometry of the stationary distribution*:
which directions are constrained and which are free.

**Ω — the current organization matrix**
In a stochastic dynamical system at steady state, Ω = DQ + A (where A is the
antisymmetric part of the drift). Ω encodes the *probability current* — the net
flow of the probability distribution through state space. When Ω = 0 everywhere,
the system is in detailed balance: no net circulation. When Ω ≠ 0, probability
circulates: the system breaks time-reversal symmetry.

**Current velocity**
The steady-state probability current J at a state x is the flux of probability
moving through that point. J is not where probability accumulates (that is Q)
— it is the vector field of how probability flows. J can be large even in regions
of low density, and the density can be stationary while currents circulate.

---

## Figure 1: "What Q Sees"

### Subtitle
State space geometry — the shape of the constraint

### Core visual
A 2D scatter cloud drawn from a bivariate Gaussian with off-diagonal covariance.
Two ellipses overlaid:
- **Covariance ellipse** (outer): elongated in the direction of high variance
- **Precision ellipse** (inner, rotated): elongated in the direction of *weak* constraint

### Labeling scheme
The long axis of the precision ellipse should be labeled:
> "Small Q → weak constraint → this direction is almost free"

The short axis of the precision ellipse:
> "Large Q → strong constraint → states are tightly coupled here"

### Color palette
Points: light blue. Covariance ellipse: gray dashed. Precision ellipse: deep orange
solid. Label arrows: black.

### What the viewer should understand
Q measures the geometry of constraint, not the geometry of spread. The covariance
tells you where states *are*. Q tells you which relationships are *enforced*.
A high-Q pair is one where the data are squeezed into a narrow conditional relationship
— knowing one variable tells you the other.

### Misconception corrected
Common confusion: "large off-diagonal covariance = large Q off-diagonal."
False in general. A large covariance between x₁ and x₂ can arise purely because
both are driven by a third variable x₃. Q removes that indirect pathway and
reports only the *direct* relationship.

### Connection to worm results
In the worm, ΔQ = Q_roam − Q_dwell captures which pairwise conditional relationships
change between behavioral states. The top pair (RMEL–RMER) has the largest ΔQ:
their bilateral coupling changes the most. The ADEL→URYVR signal (rank 5) says
the direct conditional dependence between a dopaminergic mechanosensory neuron
and an aerotaxis sensor reorganizes across states — not because their raw activities
change, but because their *conditional* relationship does.

---

## Figure 2: "What D Sees"

### Subtitle
Diffusion structure — where fluctuations enter

### Core visual
Three panels, same 2D state space, same stationary distribution sketched in the
background (faint gray ellipse).

**Panel A — Isotropic D**
Show a single starting point and ~20 short trajectory segments spreading as a
circle. Both variables fluctuate equally and independently.
Caption: "D = σ²·I — equal fluctuations in every direction"

**Panel B — Anisotropic D**
Same starting point, trajectories spread as an ellipse aligned with one axis.
x₁ fluctuates much more than x₂.
Caption: "D = diag(σ₁², σ₂²) — variable 1 fluctuates more"

**Panel C — Correlated D**
Trajectories spread as a tilted ellipse. Both variables fluctuate together.
Caption: "Off-diagonal D — correlated fluctuations"

### What the viewer should understand
D is about the *noise source*, not the steady state. You can have the same
stationary distribution (same Q) with very different D. D tells you which
variables receive the most innovation — which neurons are most "driven" by
exogenous fluctuations at each moment.

### Misconception corrected
D is not the covariance. The covariance is shaped by both D (noise input) and
the drift A (how the system restores). A highly variable neuron (large D[i,i])
is not necessarily one with high variance in the stationary distribution — a
strong restoring force (large Q) can suppress that variance.

### Connection to worm results
D reorganizes dramatically between roaming and dwelling. In the worm:
- URXL and URYVL gain ~+0.2 units of innovation variance during roaming
  (aerotaxis sensors become more driven during the state that relies on O₂ sensing)
- AIZL and AVJR lose ~−0.15 units (olfactory interneuron and reversal command
  neuron become less driven during roaming)
The rank ordering of neurons by innovation variance is nearly completely reshuffled:
ρ(D_roam, D_dwell) ≈ 0.14. This is not a simple scaling — it is a genuine
reorganization of which neurons are most dynamically active.

---

## Figure 3: "What Ω Sees"

### Subtitle
Probability current — flow through state space, independent of density

### Core visual
Three panels, same 2D state space.

**Panel A — Equilibrium system (Ω = 0)**
Static cloud of points. No arrows. Stationary distribution shown.
Caption: "Detailed balance — fluctuations are symmetric in time"

**Panel B — Same density, circulating current**
Same density contours as Panel A. Overlaid: streamlines of the probability current
circulating clockwise around the attractor. The density contours have NOT changed.
Caption: "Ω ≠ 0 — same where states are, different how they move"

**Panel C — Time-reversed current**
Same density, current arrows reversed (counter-clockwise).
Caption: "Same Q, opposite Ω — time-reversal changes the current"

### Key device
Draw a time-lapse of a single trajectory in Panel B: it spirals *around* the
attractor, then in Panel A it bounces *back and forth* along the same arc.
Same density, different trajectory statistics.

### What the viewer should understand
Ω is about movement, not accumulation. Two systems can have identical steady-state
distributions (identical Q) but completely different dynamics: one circulates, one
is time-reversible. The probability current captures this difference. Measuring
only Q cannot distinguish them.

### Misconception corrected
"The stationary distribution tells you everything about the system's dynamics."
False for non-equilibrium systems. Q measures the steady-state geometry. Ω
measures the irreversibility of the dynamics that generated it.

### Connection to worm results
In the worm, the diagonal D model gives ΔΩ ≈ constant × ΔQ (ρ = 0.9999).
This means that for this system, under z-scored CePNEM coordinates, measuring
the current organization provides no additional information beyond the precision
structure. The dynamical irreversibility signal is absorbed into the precision
matrix because the noise is nearly uniform across neurons.

---

## Figure 4: "From D and Q to Ω"

### Subtitle
Ω = DQ + A — combining fluctuations and organization

### Core visual
A 2×2 grid of panels. Fixed Q (road map) in all four, varying D.

**Left column (header): "Road map — Q fixed"**
Show the same stationary density ellipse in both panels.

**Top-left: Low, uniform D**
Small, equal-radius diffusion blobs at each point on the road map.
Ω arrows are small and follow the constraint directions.
Caption: "D isotropic, small → Ω ≈ small"

**Bottom-left: Non-uniform D, large on x₁**
Large diffusion blob along x₁, small along x₂.
Ω arrows are larger, biased toward x₁.
Caption: "D anisotropic → Ω reweights the current toward high-noise directions"

**Top-right: D large overall, isotropic**
Big equal blobs.
Ω arrows are uniformly large.
Caption: "D large, isotropic → Ω ∝ Q (same structure, bigger)"

**Bottom-right: D correlated**
Blobs tilted at 45°.
Ω arrows rotated.
Caption: "Correlated D → Ω reveals new directions not in Q alone"

### Visual metaphor panel (sidebar)
Small inset boxes with text:
- Q = road map (where are the roads?)
- D = traffic volume at each junction (how many cars per lane?)
- Ω = effective traffic organization (where does traffic actually flow?)

Same road map. Different traffic patterns. Different effective flow.

### What the viewer should understand
Ω is the product of two things: the precision structure Q and the noise structure D.
If D is uniform (all roads have equal traffic), Ω just rescales Q and adds no new
information. If D is non-uniform (some roads are much busier), Ω reorganizes the
picture and can highlight connections that appeared weak in Q but are heavily
trafficked.

### Misconception corrected
"Ω always provides information beyond Q." Only when D is non-uniform. If the system
is z-scored so that all variables have equal marginal variance, D ≈ constant·I and
Ω = constant·Q. The same mathematics can either add information (non-uniform noise)
or add nothing (uniform noise).

### Connection to worm results
The worm result is the "Top-left panel" case. CePNEM z-scoring forces D to be
nearly uniform (CV ≈ 9%). Therefore ΔΩ ≈ ΔQ and no new information enters via
the current. The leech dataset is the "Bottom-left panel" case: substantially
non-uniform D, so Ω and Q disagree.

---

## Figure 5: "What Happened in C. elegans?"

### Subtitle
D changes. Q changes. Ω converges back to Q. Biology is stable.

### Panel A: Diffusion reorganization
**Visual**: Dot plot or sorted bar chart, 61 neurons on x-axis, ΔD[i,i] on y-axis.
Two colors: roaming-dominant (positive ΔD, blue) and dwelling-dominant (negative ΔD, orange).

Label the extremes:
- Most roaming-dominant: URXL (+0.208), URYVL (+0.149) — aerotaxis/O₂ sensors
- Most dwelling-dominant: AIZL (−0.167), AVJR (−0.150) — olfactory / reversal command

Inset text:
> "ρ(D_roam, D_dwell) = 0.14 — the neuron noise ranking almost completely reshuffles"

Caption: "Neural dynamics become more heterogeneous during roaming"

### Panel B: Precision reorganization
**Visual**: Module connection diagram (simplified). Highlight DA_mech module (ADEL/CEP)
→ URY_URX module with thick arrow.

Label the arrow:
> "DA_mech ↔ URY_URX: largest multi-pair ΔQ block"
> "12 off-connectome pairs, AUROC enrichment for PDF signaling"

Show ADEL→URYVR highlighted (rank 5 in ΔQ).

Inset text:
> "PDF signal: AUROC = 0.556, enriched for neuropeptide pairs"

Caption: "Conditional dependence structure reorganizes around known neuromodulatory pathways"

### Panel C: Current convergence
**Visual**: Three-column schematic. Left column: ΔD (heterogeneous). Middle column: ΔQ
(patterned). Right column: ΔΩ.

An arrow from ΔD + ΔQ → ΔΩ with the label "Ω = DQ + A".

Show that ΔΩ and ΔQ are nearly identical (scatter plot with ρ = 0.9999 or just the
visual of near-identical rank lists).

Caption:
> "D is near-uniform after z-scoring (CV ≈ 9%)"
> "Therefore ΔΩ ≈ constant × ΔQ"
> "Current adds nothing beyond precision here"

### What the viewer should understand
Three things reorganize between behavioral states: D (who fluctuates), Q (who
couples), and Ω (how current flows). In the worm, D and Q carry independent signals
(ρ(ΔD, ΔQ) ≈ 0.05). But Ω fails to add information because the D reorganization
is nearly isotropic after z-scoring, leaving only the Q structure visible through Ω.

### Misconception corrected
"If D changes between states, then Ω must add new information beyond Q." Not if D
changes isotropically. The worm's z-scoring erases the amplitude differences in D,
leaving only the rank-order reshuffling — and rank reshuffling of near-equal-amplitude D
doesn't produce non-trivial Ω.

---

## Figure 6: "When Ω Matters"

### Subtitle
Ω adds information in some systems, not others

### Core visual
A 3-row comparison table, rendered as a schematic panel (not a text table).

For each system, show:
1. A small sketch of the D structure (uniform disk vs heterogeneous ellipse)
2. A small sketch of the Ω structure (same as Q vs rotated from Q)
3. A verdict symbol (✓ Ω adds information / ✗ Ω ≡ Q)

**Row 1: OU cascade (toy model)**
D: designed to be non-uniform (inputs enter at one node)
Ω: long-range dependencies appear that are absent in Q
Verdict: ✓ — "Ω reveals downstream propagation structure"

**Row 2: Leech**
D: substantially non-uniform across neurons
Ω: module structure diverges meaningfully from Q
Verdict: ✓ — "Ω reweights connections toward high-noise modules"

**Row 3: Worm (this study)**
D: near-uniform after z-scoring (CV ≈ 9%)
Ω: ΔΩ ≈ ΔQ (ρ = 0.9999)
Verdict: ✗ — "Ω collapses to Q; primary object is ΔQ"

### Summary bar / visual
A horizontal "information gain" bar for each system:
- OU cascade: full bar (Ω adds substantial new information)
- Leech: partial bar (Ω adds moderate new information)
- Worm: empty bar (Ω adds nothing detectable)

Caption:
> "Current organization is not universally necessary.
>  Its utility depends on whether D is non-uniform.
>  Z-scoring enforces uniform D and kills the Ω pathway."

### What the viewer should understand
Ω is not a universal upgrade over Q. Whether it adds information depends on the
noise structure D of the specific system and preprocessing choices. Z-scoring is
a common and often appropriate preprocessing step — but it has the side effect of
homogenizing D and making Ω redundant.

### Misconception corrected
"We should always compute Ω because it is the most general object." Computing Ω is
warranted when D is non-uniform. When D is forced to near-uniform by preprocessing,
Ω is just a scaled copy of Q and does not justify the additional model complexity.

---

## Cross-Figure Narrative Thread

The six figures form a single argument:

1. Q tells you the *geometry* (Figure 1)
2. D tells you the *noise input* (Figure 2)
3. Ω tells you the *flow* (Figure 3)
4. Ω = DQ + A combines all three (Figure 4)
5. In the worm: D changes, Q changes, but Ω ≡ Q (Figure 5)
6. Ω matters when D is non-uniform; not in this dataset (Figure 6)

This narrative is suitable for:
- A 15-minute chalk talk (one figure per ~2 minutes)
- A methods supplement (one figure per major mathematical object)
- A seminar introduction before presenting the main results

---

*PHASE VIS-1: storyboard package. No new data analysis performed.*
