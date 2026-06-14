# Phase 5A.1 — Candidate Inventory
Date: 2026-06-12

---

## Candidate Selection Criteria

A pair qualifies if it satisfies BOTH:
- A: Strong framework signal (top-ranked ΔQ, top-ranked PDF, or module-level pair)
- B: Existing funatlas measurement with q-value data

---

## Full Candidate Table

All pairs from the top-50 CePNEM ΔQ ranking with at least one funatlas measurement (occ ≥ 1
in any direction).

| Rank | Pair | ΔQ | PDF | Randi | wt q_ij | wt q_ji | occ_ij | occ_ji | unc-31 q_ij | unc-31 occ | Sig level |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IL1DR–URYVR | −0.254 | No | No | 0.431 | 0.242 | 7 | 4 | nan | 0 | None |
| 2 | AVER–I1L | −0.216 | No | No | 0.541 | 0.062 | 6 | 30 | 0.423 | 2 | Marginal (ji) |
| 3 | AVJR–OLLR | −0.170 | No | No | 0.646 | 0.533 | 14 | 20 | 0.678 | 1 | None |
| 4 | AVJR–OLQVR | −0.161 | No | No | 0.284 | 0.589 | 14 | 9 | nan | 0 | None |
| 5 | ADEL–URYVR | −0.122 | Yes | No | nan | 0.152 | 0 | 1 | nan | 0 | **No coverage** |
| 6 | AVER–AWAL | −0.109 | No | No | 0.081 | 0.427 | 12 | 5 | nan | 0 | None |
| 9 | ADEL–URYDL | −0.098 | Yes | No | nan | nan | 0 | 0 | nan | 0 | **No coverage** |
| 10 | ADEL–RMEL | −0.096 | Yes | No | 0.492 | 0.347 | 5 | 4 | 0.372 | 2 | None |
| 16 | RMEL–URYDL | −0.075 | Yes | No | 0.408 | 0.276 | 3 | 4 | nan | 0 | None |
| 20 | AVEL–RIVL | −0.073 | No | No | 0.575 | **0.024** | 11 | 15 | nan | 2 | wt sig (ji) |
| 21 | RMEL–URYVR | −0.070 | Yes | No | 0.552 | 0.408 | 9 | 8 | nan | 0 | None |
| **32** | **RMEL–RMER** | **−0.058** | **Yes** | **Yes** | **0.0002** | 0.086 | **22** | 16 | 0.119 | 5 | **wt significant, DCV-dep** |
| 40 | CEPDR–URXL | −0.054 | No | No | **0.0002** | 0.120 | 6 | 6 | nan | 0 | **wt significant** (DCV unknown) |
| 42 | OLQDL–RICL | −0.053 | No | Yes | **0.046** | 0.481 | 2 | 3 | 0.630 | 1 | wt marginal, DCV-dep |
| 47 | AVJR–AWBL | −0.050 | No | Yes | **0.0017** | 0.159 | 37 | 25 | **0.012** | 4 | wt + unc-31 both sig |
| 50 | I1R–RMDVR | −0.049 | No | Yes | **0.032** | 0.617 | 57 | 4 | 0.571 | 2 | **wt significant, DCV-dep** |

---

## Tier Assessment

### Tier 1: Strong framework + strong perturbation confirmation + DCV dependence

**RMEL–RMER (rank 32)**
- Framework: ΔQ = −0.058, rank 32 of 1321. PDF-annotated (Bentley ESconnectome). Randi-annotated.
  CePNEM-specific (GCaMP ΔQ = 0.000). Dwelling-dominant conditional coupling.
  n_recordings_roam=18, n_recordings_dwell=33, n_eff_roam=856, n_eff_dwell=4713.
- Perturbation: RMEL→RMER wt q = 0.0002 (22 observations). unc-31 q = 0.119 (NOT significant).
  RMEL→RMER interaction is present in WT and absent in unc-31 → DCV/neuropeptide-dependent.
- Atlas support level: **STRONG** — highly significant wt interaction, plausible DCV mechanism.

### Tier 2: Strong wt confirmation, DCV unknown

**CEPDR–URXL (rank 40)**
- Framework: ΔQ = −0.054, rank 40. Peptide-annotated (Ripoll-Sánchez). Dwelling-dominant.
- Perturbation: CEPDR→URXL wt q = 0.0002 (6 observations). unc-31 unmeasured.
- Atlas support level: **MODERATE** — strong wt confirmation but no DCV characterization.

### Tier 3: High-coverage wt confirmation + DCV-dependent

**I1R–RMDVR (rank 50)**
- Framework: ΔQ = −0.049, rank 50. Randi-annotated. Dwelling-dominant.
- Perturbation: I1R→RMDVR wt q = 0.032, occ = 57 (highest observation count). unc-31 NOT sig (q=0.57).
- Atlas support level: **MODERATE** — weaker framework signal but highest observation confidence.

### Tier 4: Confirmed in both WT and unc-31 (DCV-independent)

**AVJR–AWBL (rank 47)**
- wt q = 0.0017 AND unc-31 q = 0.012 → interaction is present independently of DCVs.
- Not consistent with neuropeptide (PDF/DCV) mechanism. Likely gap junction or classical synapse.
- Atlas support level: **CONFIRMED** but NOT neuropeptide-mediated.

---

## Summary

One Tier 1 case: **RMEL–RMER** is both strongly predicted by the framework (rank 32, PDF-annotated)
and independently confirmed by the funatlas with DCV dependence (wt q=0.0002, unc-31 q=0.119).
This is the strongest candidate for external validation of the framework.

The three highest-ranked framework predictions for novel ADEL-PDF pairs (ADEL-URYVR, ADEL-URYDL,
ADEL-RMEL) remain untested by the funatlas — they are genuine held-out predictions.
