# Phase 9E — Task 2: Metric Translation

**Date:** 2026-06-15  
**Source metrics:** Phase 9D evaluation (`evaluation_results.json`)

This document provides plain scientific translations for each benchmark metric, avoiding jargon specific to the benchmark design.

---

## 1. Precision@50 = 0.920

### What the benchmark means
Among the 50 pairs of neurons most strongly flagged by the framework as belonging to state-dependent co-organization, 46 actually belong to the planted circuit.

### Scientific translation

**In terms of top recovered organization:**  
The 50 strongest links identified by the framework concentrate almost entirely within the planted state-modulated circuit. 46 of the 50 strongest recovered pairwise relationships are genuine members of the planted organization; 4 are not.

**In terms of precision at the top of the ranking:**  
At the detection threshold that captures the top-50 pairs, the framework operates at 92% precision. The planted circuit contains 181 pairs total, so the top-50 recovery captures the 46 most confidently detected circuit members.

**Alternative language:**  
"Of the 50 strongest detected relationships, 46 belong to the planted state-dependent organization (92% precision)."

---

## 2. PMC_AUROC = 0.794

### What the benchmark means
If you draw one pair at random from the planted circuit and one pair at random from outside it, the framework assigns the circuit pair a higher score with probability 0.794. (This is an area under the receiver-operating-characteristic curve across all 10,433 off-connectome pairs.)

### Scientific translation

**In terms of discrimination:**  
The framework reliably assigns higher organizational scores to pairs within the planted circuit than to pairs outside it. Across all ~10,000 possible pairings of a true circuit pair versus a non-circuit pair, the framework ranks the true circuit pair higher 79% of the time.

**In terms of separation:**  
There is meaningful separation between the score distribution for planted-circuit pairs and all other pairs. The overlap is partial — the framework is not perfect — but the signal is well above chance (50%).

**In terms of what it is not:**  
This is not the same as recovery precision. It measures whether the relative ordering of circuit vs non-circuit pairs is correct across the entire population, not just at the top.

**Alternative language:**  
"Pairs belonging to the planted organization were ranked above pairs outside it with 79% probability — substantially above chance (50%)."

---

## 3. ρ_Spearman = 0.190

### What the benchmark means
The framework's ranking of all 10,433 pairs correlates with the ground-truth oracle ranking at ρ = 0.190. A perfect framework would achieve ρ = 1.0; a random ranking gives ρ ≈ 0.

### Scientific translation

**In terms of global ranking quality:**  
The framework's overall ranking of all detected pairs shows a weak but statistically reliable positive correlation with the true underlying organization. The framework gets the coarse structure right (top pairs are circuit members) but the fine-grained ordering across all 10,433 pairs is substantially imprecise.

**In terms of what it captures vs. what it misses:**  
The framework excels at identifying the strongest circuit pairs (Precision@20 = 1.000, Precision@50 = 0.920) but assigns noisy scores within the larger set, particularly for weaker circuit pairs. The global ranking correlation is limited by this noise, not by the top-k recovery.

**Why ρ and Precision@50 can diverge:**  
Precision@50 captures only the top 50 of 10,433 pairs. The Spearman ρ captures agreement across all 10,433 pairs. A method that perfectly identifies the top circuit members but scrambles the ordering of the remaining 10,383 pairs would achieve high Precision@50 and low ρ. This is what is observed here.

**Alternative language:**  
"The framework's confidence scores show a positive but moderate correlation (ρ = 0.19) with the true strength of state-dependent organization across all detected pairs, indicating reliable identification of the strongest circuit components but imprecise ranking of weaker ones."

---

## 4. Combined interpretation

The three metrics together tell a consistent story:

| Metric | What it captures | Value | Interpretation |
|--------|-----------------|-------|----------------|
| Precision@20 | Top-tier recovery | 1.000 | Highest-ranked pairs: all circuit members |
| Precision@50 | Broad top-tier recovery | 0.920 | Top-50 pairs: 92% circuit members |
| PMC_AUROC | Population-level discrimination | 0.794 | Circuit vs non-circuit: 79% correct ordering |
| ρ_Spearman | Global ranking quality | 0.190 | Correct coarse structure, imprecise fine detail |

The pattern — high Precision@k, moderate AUROC, lower ρ — indicates a method that identifies the dominant circuit members with high confidence but loses precision when ranking less prominent circuit pairs against each other and against the background.

---

## 5. Comparison to chance

The planted circuit comprises 181 of 10,433 off-connectome pairs = 1.74% of all pairs.

| Metric | Chance level | Framework | Gain |
|--------|-------------|-----------|------|
| Precision@50 | 0.017 (1.74%) | 0.920 | ×53 |
| PMC_AUROC | 0.500 | 0.794 | +0.294 |
| ρ_Spearman | ≈ 0 | 0.190 | +0.190 |

The framework enriches the top-50 by 53-fold over chance selection from the background.
