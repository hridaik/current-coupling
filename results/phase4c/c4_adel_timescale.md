# Phase 4C.4 — Key Pair Timescale Profiles
Date: 2026-06-12

---

## Question

How do the key ADEL-centered and RMEL-URYDL pairs behave across timescales?
Are their ΔD and ΔΩ signs stable, or do they flip?

Pairs tracked: ADEL–URYVR, ADEL–URYDL, ADEL–RMEL, RMEL–URYDL.
All four are among the top-10 |ΔQ| Class-4 pairs and are PDF-annotated.

---

## Results

### ADEL–URYVR (ΔQ = −0.122, rank 5 by |ΔQ|)

| τ | D_roam | D_dwell | ΔD | ΔΩ |
|---|---|---|---|---|
| 1  | 0.0086 | 0.0113 | −0.0027 | −0.069 |
| 2  | 0.0310 | 0.0203 | +0.0107 | −0.085 |
| 5  | 0.0544 | 0.0583 | −0.0038 | −0.147 |
| 10 | 0.0861 | 0.1135 | −0.0274 | −0.217 |
| 20 | 0.1834 | 0.1686 | +0.0148 | −0.246 |

**ΔD sign:** Unstable. Sign changes at τ=2 (positive) and τ=20 (positive), but negative at τ=1, 5, 10.
**ΔΩ sign:** Consistently negative across all τ. ΔΩ magnitude increases monotonically (0.069 → 0.246).

### ADEL–URYDL (ΔQ = −0.098, rank 9 by |ΔQ|)

| τ | D_roam | D_dwell | ΔD | ΔΩ |
|---|---|---|---|---|
| 1  | 0.0145 | 0.0083 | +0.0062 | −0.050 |
| 2  | 0.0286 | 0.0202 | +0.0084 | −0.070 |
| 5  | 0.0721 | 0.0488 | +0.0232 | −0.091 |
| 10 | 0.1294 | 0.0948 | +0.0346 | −0.115 |
| 20 | 0.2452 | 0.1386 | +0.1066 | −0.092 |

**ΔD sign:** Consistently positive across all τ (roam > dwell). Magnitude grows from 0.006 to 0.107.
**ΔΩ sign:** Consistently negative across all τ. Magnitude increases then stabilizes (~0.09–0.12).

### ADEL–RMEL (ΔQ = −0.096, rank 10 by |ΔQ|)

| τ | D_roam | D_dwell | ΔD | ΔΩ |
|---|---|---|---|---|
| 1  | 0.0069 | 0.0113 | −0.0045 | −0.055 |
| 2  | 0.0082 | 0.0228 | −0.0146 | −0.086 |
| 5  | 0.0395 | 0.0778 | −0.0383 | −0.145 |
| 10 | 0.1062 | 0.0898 | +0.0164 | −0.135 |
| 20 | 0.2147 | 0.1242 | +0.0905 | −0.133 |

**ΔD sign:** Negative at τ=1, 2, 5 (dwell > roam); positive at τ=10, 20 (roam > dwell). Sign inversion at ~τ=7–10.
**ΔΩ sign:** Consistently negative across all τ. Magnitude peaks at τ=5 then stabilizes.

### RMEL–URYDL (ΔQ = −0.075, rank 18 by |ΔQ|)

| τ | D_roam | D_dwell | ΔD | ΔΩ |
|---|---|---|---|---|
| 1  | 0.0053 | 0.0060 | −0.0007 | −0.031 |
| 2  | 0.0107 | 0.0122 | −0.0014 | −0.047 |
| 5  | 0.0323 | 0.0404 | −0.0081 | −0.084 |
| 10 | 0.0849 | 0.0751 | +0.0098 | −0.103 |
| 20 | 0.1786 | 0.0628 | +0.1158 | −0.054 |

**ΔD sign:** Negative at τ=1, 2, 5; positive at τ=10, 20 (same inversion pattern as ADEL–RMEL).
**ΔΩ sign:** Consistently negative. Peaks at τ=10 then drops at τ=20.

---

## Cross-Pair Comparison

### ΔD Stability

| Pair | ΔD sign stability | Characteristic |
|---|---|---|
| ADEL–URYVR | Unstable (3× negative, 2× positive) | Noisy sign, unclear timescale |
| ADEL–URYDL | **Stable positive** (roam > dwell) | Fast-roam pairwise co-movement |
| ADEL–RMEL | Inverts at τ≈10 | Dwell-dominant fast, roam-dominant slow |
| RMEL–URYDL | Inverts at τ≈10 | Same as ADEL–RMEL |

### ΔΩ Stability

All four pairs show consistently negative ΔΩ at every τ. The sign of ΔΩ = Ω_roam − Ω_dwell < 0
means the combined state-dependent current is dwelling-dominant — the effective "flow"
through this circuit is stronger during dwelling than roaming, at every timescale tested.

| Pair | ΔΩ at τ=1 | ΔΩ at τ=20 | Peak τ |
|---|---|---|---|
| ADEL–URYVR | −0.069 | −0.246 | τ=20 (growing) |
| ADEL–URYDL | −0.050 | −0.092 | τ=10 |
| ADEL–RMEL  | −0.055 | −0.133 | τ=5 |
| RMEL–URYDL | −0.031 | −0.054 | τ=10 |

---

## Interpretation

### ΔΩ Is the Stable Descriptor

ΔD sign is unstable for 3 of 4 pairs across the timescale range tested. This instability
reflects the OU dynamics: at short lags, fast fluctuations may reverse the apparent
co-movement direction; at long lags, slow structural organization dominates. The ΔD sign
does not reliably identify the direction of state-dependent diffusion change for these pairs.

ΔΩ is more stable than ΔD: all four pairs maintain consistently negative ΔΩ at every τ.
The ΔΩ sign reflects the interaction of D(τ) and Q (the steady-state precision), and
inheriting the Q structure stabilizes the sign despite D(τ) fluctuations.

**Practical consequence:** ΔΩ is a more robust marker of state-dependent circuit
organization for these specific pairs than ΔD alone.

### ADEL–RMEL and RMEL–URYDL Share a Timescale Signature

Both pairs show dwell > roam diffusion at short lags and roam > dwell at long lags
(sign inversion at τ ≈ 10 frames ≈ 2.5 seconds). This suggests ADEL–RMEL–URYDL
forms a sub-circuit with a common timescale signature: the three-neuron combination
has dwelling-dominant fast fluctuations but roaming-dominant slow drifts.

### ADEL–URYDL Is the Most Consistent Pair

ADEL–URYDL shows positive ΔD (roam > dwell) at all timescales and growing magnitude.
This pair is the most structurally simple: the direction of diffusion state-difference
is consistent across all timescales, and grows monotonically.

---

## Summary

**Primary result:** ΔΩ is consistently negative for all four key pairs across all τ ∈ {1, 2, 5, 10, 20},
confirming dwelling-dominant current organization at every timescale. ΔD is sign-unstable
for 3 of 4 pairs, reflecting OU dynamics where short and long timescale state-dependent
organization point in different directions. ADEL–RMEL and RMEL–URYDL share a common sign
inversion at τ ≈ 10 frames, suggesting a ~2.5-second timescale for their state-dependent
organization.
