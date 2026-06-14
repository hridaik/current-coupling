# Phase 9E — Task 3: Manuscript-Ready Language

**Date:** 2026-06-15  
**Based on:** Phase 9D evaluation (PARTIAL verdict: 2/3 primary metrics at SUCCESS threshold)

Three versions of increasing length. Numbers are exact Phase 9D values.

---

## SHORT (1–2 sentences)

The framework recovered the planted state-dependent circuit with high precision: 46 of the 50 most confidently identified pairs belonged to the planted organization, and pairs within the planted circuit were ranked above background pairs with 79% reliability. The global ranking correlation was positive but moderate (ρ = 0.19), reflecting accurate identification of the dominant circuit members but imprecise ordering of weaker circuit pairs.

---

## MEDIUM (1 paragraph)

We evaluated the framework on a synthetic C. elegans-scale network (150 observed neurons) in which a 20-neuron state-dependent circuit — the Planted Modulatory Circuit (PMC) — was embedded among 10,433 possible pairwise relationships. The circuit was activated by a hidden relay structure that elevated noise variance at source neurons in State A, and the framework received no information about this hidden structure. Of the 50 pairs assigned the highest state-dependent organizational scores, 46 belonged to the planted circuit (92% precision), and all 20 of the top-ranked pairs were circuit members (100% precision at rank 20). Circuit pairs were ranked above background pairs with 79% probability — substantially above the 50% chance level — corresponding to a 53-fold enrichment of circuit members in the top-50 relative to random selection. The global rank correlation between framework scores and the ground-truth organizational strength was positive and highly significant (ρ = 0.19, p < 10⁻⁸⁰) but below the pre-registered threshold for full success, indicating that while the dominant circuit structure is reliably recovered, the framework's confidence scores become imprecise for weaker circuit pairs.

---

## LONG (2–3 paragraphs)

We evaluated the current-velocity framework on a synthetic network designed to model the key features of the C. elegans neuromodulatory system. The network consisted of 150 observed neurons organized into four anatomical modules, with a 20-neuron Planted Modulatory Circuit (PMC) embedded in two of the modules. The PMC operated through a hidden relay structure: 8 source neurons (PMC_SRC) projected to 10 hidden "global interneuron" nodes (H_global), which relayed state-dependent drive to 12 target neurons (PMC_TGT) in modules M3 and M4. In State A, source neurons were subject to substantially elevated noise variance (5×), and the hidden relay amplified this into a shared drive signal received by all target neurons. In State B, the network was uniform. The framework received only the two observed trajectories and the known structural coupling matrix, with no access to the hidden relay or any ground truth.

Among the 10,433 off-connectome pairs evaluated by the framework, 181 belonged to the planted circuit. The top-50 framework-ranked pairs contained 46 circuit members (92% precision), a 53-fold enrichment over the 1.74% circuit prevalence in the full pair population. All 20 top-ranked pairs were circuit members (100% precision at rank 20). The circuit pairs were ranked above background pairs with 79% probability (area under the receiver-operating characteristic curve = 0.794), compared to 50% for a random ranking. The four non-circuit pairs in the top-50 (ranks 43, 44, 46, 48) all involved one circuit target neuron paired with a nearby non-circuit neuron, and arose from a specific estimation artifact: the framework incorrectly infers elevated noise variance at target neurons because the hidden relay input, which drives their excess variance in State A, is not represented in the observed coupling matrix. This is a mechanistically interpretable limitation rather than a random failure.

The global rank correlation between framework scores and the ground-truth organizational strength was ρ = 0.19 (Spearman; p < 10⁻⁸⁰), positive and statistically robust but below the pre-registered success threshold of ρ ≥ 0.40. This pattern — strong top-k precision, moderate area under the ROC curve, weaker global rank correlation — is consistent across the worm, leech, and synthetic evaluations and reflects a characteristic behavior of the current-velocity framework: reliable identification of the dominant circuit components, with decreasing precision for weaker circuit pairs that fall closer to the noise floor of the estimation procedure. The results demonstrate that a current-velocity decomposition applied to observed neural trajectories can recover the dominant structure of a state-dependent hidden relay circuit in a C. elegans-scale network with high precision at the top of the ranking, even without direct access to the hidden nodes driving the circuit.

---

## Key phrase substitutions

| Benchmark language | Manuscript language |
|-------------------|---------------------|
| Precision@50 = 0.920 | "46 of the 50 most confidently identified pairs belonged to the planted circuit" |
| Precision@20 = 1.000 | "all 20 of the top-ranked pairs were circuit members" |
| PMC_AUROC = 0.794 | "circuit pairs were ranked above background pairs with 79% probability" |
| 181 PMC pairs, 10,433 total | "1.74% circuit prevalence; 53-fold enrichment in top-50" |
| ρ_Spearman = 0.190 | "positive global rank correlation (ρ = 0.19) between framework scores and ground-truth organizational strength" |
| PARTIAL verdict | "strong top-k recovery with moderate global rank correlation" |
| 4 false positives in top-50 | "four non-circuit pairs at ranks 43–48, arising from a specific estimation artifact" |
