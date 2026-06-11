# Phase 3D-1 — State-Dependent Diffusion Analysis
Date: 2026-06-03
Authorization: Phase 3D

---

## D1.1 — State-Specific D Matrices

Empirical diffusion D_s = Cov(Δx | state s) estimated using consecutive same-state
first-differences, pooled across all 40 recordings.

### CePNEM

| State | Diagonal range | Mean | Std | CV |
|---|---|---|---|---|
| Dwell | [0.260, 0.510] | 0.399 | 0.042 | **0.105** |
| Roam | [0.269, 0.613] | 0.418 | 0.074 | **0.177** |
| Pooled (Phase 3C-E) | [0.316, 0.483] | 0.405 | 0.038 | 0.093 |

### GCaMP

| State | Diagonal range | Mean | Std | CV |
|---|---|---|---|---|
| Dwell | [0.139, 0.331] | 0.228 | 0.038 | **0.168** |
| Roam | [0.136, 0.413] | 0.238 | 0.056 | **0.234** |
| Pooled (Phase 3C-E) | [0.156, 0.323] | 0.231 | 0.035 | 0.151 |

**Key observation**: Roaming has substantially higher diagonal CV than dwelling in both
coordinates (CePNEM: 0.177 vs 0.105; GCaMP: 0.234 vs 0.168). Neural dynamics are
more heterogeneous across neurons during roaming — some neurons increase innovation
variance substantially while others decrease, whereas during dwelling the system is
more uniformly regulated.

---

## D1.2 — ΔD = D_roam − D_dwell

### Magnitude

| Coordinate | ||ΔD||_F | Relative to ||D_roam|| |
|---|---|---|
| CePNEM | 0.776 | **23%** |
| GCaMP | 0.537 | **28%** |

The diffusion matrix changes by ~25% (Frobenius) between states. This is substantial —
much larger than the ~10% CV of pooled D, confirming that state-dependent diffusion
is not trivially isotropic.

### The key diagnostic: per-neuron D ordering changes between states

| Coordinate | ρ(diag_D_roam, diag_D_dwell) |
|---|---|
| CePNEM | **0.139** |
| GCaMP | **0.201** |

**ρ ≈ 0.14–0.20 means the rank ordering of neurons by innovation variance changes
almost completely between roaming and dwelling.** A neuron that has high D during
roaming may have low D during dwelling, and vice versa. This is a genuine biological
state-dependence of the noise structure — not just a scaling.

### ΔD vs ΔQ correlation

| Coordinate | ρ(|ΔD|, |ΔQ|) on Class 4 |
|---|---|
| CePNEM | **0.056** |
| GCaMP | **0.031** |

The diffusion reorganization is essentially **uncorrelated** with the functional
connectivity reorganization (ΔQ). The pairs that change most in D are not the
same pairs that change most in Q. These are independent sources of state-dependent
information.

### Module-level D changes

| Module | D_roam | D_dwell | ΔD | Notes |
|---|---|---|---|---|
| URY_URX | 0.4734 | 0.3950 | **+0.0784** | Largest module gain |
| RMD_SMD | 0.4350 | 0.4079 | +0.0271 | |
| DA_mech | 0.4204 | 0.3950 | +0.0254 | ADEL/CEP more active during roaming |
| RID | 0.4963 | 0.4776 | +0.0187 | |
| IL1_IL2 | 0.4016 | 0.3828 | +0.0188 | |
| RME | 0.3958 | 0.4028 | **−0.0070** | Slightly LESS active during roaming |

**URY_URX has the largest state-dependent D change (+0.078):** aerotaxis/O₂-sensing
neurons have substantially higher innovation variance during roaming. This is
biologically coherent — these neurons are thought to be more dynamically active
during roaming-to-dwelling transitions, sensing O₂ gradients that influence state.

The ADEL/CEP (DA_mech) module also has higher roaming D (+0.025), consistent with
dopaminergic mechanosensory neurons being more active on substrate during roaming.

**RME is the only module with lower D during roaming (−0.007)** — GABA ring motor
neurons are marginally quieter during roaming. This is counter-intuitive but
statistically marginal.

---

## D1.3 — State-Specific ΔΩ vs ΔQ

### Rank correlations on Class 4 pairs

| Framework | ρ(|ΔΩ|, |ΔQ|) |
|---|---|
| ΔΩ_pooled (Phase 3C-E) | 0.566 |
| **ΔΩ_ss_diag** (D_r·Q_r − D_d·Q_d, diagonal D) | **0.9998** |
| **ΔΩ_ss_full** (D_r @ Q_r − D_d @ Q_d, full D) | **0.331** |
| ρ(ΔΩ_ss_full, ΔΩ_pooled) | 0.254 |

### Why ΔΩ_ss_diag ≈ ΔQ (ρ = 0.9998)

The state-specific diagonal ΔΩ decomposes as:

    ΔΩ_ss_diag[i,j] = D_r[i,i]·Q_r[i,j] − D_d[i,i]·Q_d[i,j]
                     = D_mean[i,i]·ΔQ[i,j] + ΔD[i,i]/2·Q_mean[i,j]

The first term dominates because ΔQ has much larger absolute values than ΔD·Q_mean
for the pairs that matter. Even though ΔD has ρ(D_r,D_d)=0.14 (large ordering change),
the cross-term ΔD·Q_mean is small because Q_mean is approximately equal across states
for most pairs. Result: ΔΩ_ss_diag ≈ D_mean·ΔQ ≈ ΔQ (up to scaling).

### Why ΔΩ_ss_full diverges most (ρ = 0.331)

The full-matrix multiplication D_r @ Q_r − D_d @ Q_d is the most general but also
the most noise-amplifying. With ρ(D_r,D_d) ≈ 0.14, the two full diffusion matrices
are essentially unrelated, so the cross-terms D_r·Q_r and D_d·Q_d partially add
rather than cancel, creating large departures from ΔQ. Crucially, ρ(ΔΩ_ss_full,
ΔΩ_pooled) = 0.254 — the state-specific and pooled full versions are very different.

---

## D1.4 — PDF Enrichment Under All Ω Frameworks

| Framework | CePNEM AUROC | Fisher OR (k_ann) | GCaMP AUROC | Fisher OR |
|---|---|---|---|---|
| **ΔQ** | **0.556** | **5.46 [4]** | 0.526 | 1.09 [1] |
| ΔΩ_pooled | 0.664 | 7.41 [5] | 0.488 | 1.09 [1] |
| ΔΩ_ss_diag | 0.557 | 3.78 [3] | 0.530 | 1.09 [1] |
| ΔΩ_ss_full | 0.533 | 5.46 [4] | 0.539 | 1.09 [1] |

### Critical result

**State-specific diagonal Ω (ΔΩ_ss_diag) gives essentially the same AUROC as ΔQ
(0.557 vs 0.556).** Adding state-specificity to the diagonal D model provides NO
enrichment improvement.

**State-specific full Ω (ΔΩ_ss_full) is WORSE than both ΔQ and ΔΩ_pooled.**
CePNEM AUROC = 0.533 vs 0.556 (ΔQ) — the state-specific full model actually
degrades PDF enrichment.

The ΔΩ_pooled improvement (AUROC 0.664) seen in Phase 3C-E/F does NOT arise from
state-dependent diffusion structure. It arises from the pooled D_emp having specific
hub-connectivity properties (RID/RMEL/RMER hubs) that happen to elevate zero-ΔQ
PDF pairs — a property established in Phase 3C-G/H.

### GCaMP

Fisher OR is identical (1.09) for all four frameworks, and the GCaMP top-20 PDF
count remains 1 in all cases. State-specific D does not help GCaMP.

---

## Is Diffusion Itself State-Dependent?

**Yes, definitively.** D reorganizes substantially between roaming and dwelling:
- ρ(D_r, D_d) = 0.14 — almost completely different neuron ordering
- ||ΔD||_F / ||D_roam|| = 23% — 23% relative magnitude change
- URY_URX module gains +0.078 (largest), DA_mech gains +0.025

**But state-dependent D does not provide additional information beyond ΔQ for
the PDF enrichment task.** The state-specific ΔΩ (diagonal) ≈ ΔQ (ρ = 0.9998).

---

*D1 scope: state-dependent diffusion characterization only.*
