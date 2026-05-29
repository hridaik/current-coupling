# Stage 4 Creamer LDS Numerical Feasibility Audit

Date: 2026-05-28

## Scope

Numerical feasibility of the Lyapunov solve and Omega_C computation for the
Creamer-compatible 56-neuron subspace (common-61 minus AIBL, AIBR, AWCL, IL1L, IL1R).

Computed in this step:
  - Sigma_C via scipy.linalg.solve_discrete_lyapunov
  - Positive-definiteness and condition-number checks
  - Q_C = Sigma_C^{-1}
  - Omega_C = A_C + D_C @ Q_C (Frobenius and spectral norms)

NOT computed:
  - Any real-data covariance or precision matrices
  - DeltaQ, D_C DeltaQ, Omega_s, enrichment
  - Behavioral/state-conditioned statistics

Model used: connectome_constrained (primary model per task.md Stage 1).

---

## Human-Approved Space Definitions

| Namespace | Size | Notes |
|---|---|---|
| Anatomical harmonization space | **61** neurons | Atanas ∩ Connectome ∩ Randi head; N_COMMON_NEURONS |
| Functional-pair space (Randi) | **60** neurons | Excludes AWCL (not in funatlas); N_RANDI_SUBGRAPH_NEURONS |
| Creamer-compatible LDS space | **56** neurons | Excludes AIBL, AIBR, AWCL, IL1L, IL1R; N_CREAMER_SUBGRAPH_NEURONS |

Missing Creamer neurons (NOT imputed or padded): AIBL, AIBR, AWCL, IL1L, IL1R

---

## A_C (Dynamics Matrix) — 56-Neuron Subspace

| Property | Value | Interpretation |
|---|---|---|
| Shape | (56, 56) | Subspace restriction of the 154-neuron A_C |
| max abs(eigenvalue) | **0.984367** | Discrete-time stable (< 1) |
| All abs(eig) < 1 | True | Subspace remains stable after restriction |
| Reference (full 154-neuron) | 0.996609 | Both stable |

The subspace restriction reduces the maximum eigenvalue magnitude from 0.9966
to 0.9844. Both are discrete-time stable.

---

## D_C (Process-Noise Covariance) — 56-Neuron Subspace

| Property | Value |
|---|---|
| Shape | (56, 56) diagonal |
| Diagonal range | [4.84e-3, 1.30e-1] |
| All diagonal entries > 0 | True (posdef) |
| Condition number (max/min diag) | **26.9** |

D_C is diagonal by model design (`param_props['shape']['dynamics_cov'] = 'diag'`).
Well-conditioned for the subspace.

---

## Sigma_C = solve_discrete_lyapunov(A_C, D_C)

Computes the discrete-time stationary covariance satisfying:
  Sigma_C = A_C @ Sigma_C @ A_C.T + D_C

Solver: `scipy.linalg.solve_discrete_lyapunov`

| Property | 56-neuron subspace | Full 154-neuron (reference) |
|---|---|---|
| Shape | (56, 56) | (154, 154) |
| min eigenvalue | **9.97e-3** | 9.70e-3 |
| max eigenvalue | **3.50e-1** | 1.85 |
| Positive definite | **True** | True |
| Condition number kappa | **35.1** | 190.3 |

**Sigma_C is positive definite and well-conditioned** (kappa = 35.1).
No numerical instability detected. The 56-neuron subspace is better conditioned
than the full model, consistent with removing weakly-coupled peripheral neurons.

---

## Omega_C = A_C + D_C @ Q_C (where Q_C = Sigma_C^{-1})

| Property | 56-neuron subspace | Full 154-neuron (reference) |
|---|---|---|
| Shape | (56, 56) | (154, 154) |
| Frobenius norm | **8.6089** | 14.12 |
| Spectral norm (L2) | **1.3685** | — |
| max Re(eigenvalue) | 1.2289 | — |
| min Re(eigenvalue) | 1.0154 | — |

`CREAMER_OMEGA_NORM = 8.6089` is recorded for the 56-neuron subspace.

The real part of all Omega_C eigenvalues > 1.0, meaning the current-velocity
Jacobian is entirely excitatory/positive in this subspace. This is a property
of the connectome-constrained model and should be noted when interpreting
the current-velocity bridge results.

---

## RC Role Fields (Updated)

Per human decision 2026-05-28 (RC scope restriction):

| Field | Previous | New |
|---|---|---|
| `RC_ROLE_SAMPLING` | `"audit_only"` | `"behavioral_eigenworm_only"` |
| `RC_ROLE_JACOBIAN` | `"audit_only"` | `"not_viable"` |
| `RC_ROLE_DRIVE_SWEEP` | `"not_used_phase0"` | `"not_viable"` |
| `RC_OUTPUT_NEURON_COORDS` | `None` | `False` |
| `RC_OUTPUT_JACOBIAN_AVAILABLE` | `None` | `False` |
| `RC_STATE_CONDITIONED` | `None` | `False` |
| `RC_NEURON_COVERAGE` | `None` | `0` |

Rationale: RC input/output is in 5D eigenworm space (training data: crawl.mat
eigenworm PCs). Wout maps (N=10000 reservoir) → (5D eigenworm), with no path
to identified NeuroPAL neuron coordinates.

---

## Config Fields Updated

| Field | Value | Section |
|---|---|---|
| `CREAMER_TIME_CONVENTION` | `"discrete_time"` | CREAMER |
| `CREAMER_DT` | `0.5` | CREAMER |
| `CREAMER_MAX_EIGENVALUE` | `0.996609` | CREAMER (full model) |
| `CREAMER_STABLE` | `True` | CREAMER |
| `CREAMER_DC_AVAILABLE` | `True` | CREAMER |
| `CREAMER_LABEL_CONVENTION` | `"neuropal_str"` | CREAMER |
| `CREAMER_SIGMA_POSDEF` | `True` | CREAMER |
| `CREAMER_OMEGA_NORM` | `8.6089` | CREAMER (56-neuron subspace) |
| `N_CREAMER_SUBGRAPH_NEURONS` | `56` | SUBGRAPH / HARMONIZATION |
| `RC_ROLE_SAMPLING` | `"behavioral_eigenworm_only"` | RC |
| `RC_ROLE_JACOBIAN` | `"not_viable"` | RC |
| `RC_ROLE_DRIVE_SWEEP` | `"not_viable"` | RC |
| `RC_OUTPUT_NEURON_COORDS` | `False` | RC |
| `RC_OUTPUT_JACOBIAN_AVAILABLE` | `False` | RC |
| `RC_STATE_CONDITIONED` | `False` | RC |
| `RC_NEURON_COVERAGE` | `0` | RC |

---

## Deviations

No deviations. All computations are authorized.
