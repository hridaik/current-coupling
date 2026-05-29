# Stage 2 Diagnosis Report

Date: 2026-05-28

**Scope:** Diagnosis only. No code was modified, no recomputation was run,
no config values were changed.

---

## 1. Why all-neuron overlap = 60 and head overlap = 61

The single-neuron difference is `AWCL`.

The script builds two Randi label sets from two different source files:

```
randi_all  ← neuron_ids.txt            → uses AWCON / AWCOFF convention
randi_head ← aconnectome_ids_ganglia.json → uses AWCL / AWCR convention
```

The Atanas high-confidence label set contains `AWCL` (it is in the
61-neuron `N_COMMON_NEURONS` list in the feasibility report).

Intersection logic in `scripts/stage02_subgraph.py` lines 629–630:

```python
common_all_randi  = atanas_high_coverage & connectome_labels & randi_all
common_head_randi = atanas_high_coverage & connectome_labels & randi_head
```

- `AWCL` is NOT in `randi_all` (that set contains `AWCON`/`AWCOFF`, not
  `AWCL`/`AWCR`), so `AWCL` is excluded from `common_all_randi`.
  Result: 60.
- `AWCL` IS in `randi_head` (the ganglia JSON uses left/right convention),
  so `AWCL` passes the intersection for `common_head_randi`.
  Result: 61.

The feasibility report confirms this directly:

> "Common labels present in the Randi head-ganglia metadata but absent from
> `neuron_ids.txt`: `AWCL`"

The difference of exactly 1 is entirely explained by the AWC naming
convention mismatch between the two Randi source files.

---

## 2. The 80% coverage rule — authorized or silently introduced

**Authorized.** The rule is stated verbatim in `task.md` Stage 2, Task 4:

> "Define the primary neuron set as: neurons identified with high confidence
> (confidence score ≥ threshold; see Stage 5) in ≥ 80% of Atanas animals…"

The feasibility report and decode report both cite this source:

> "Atanas record coverage rule from `task.md`: labels must pass the
> confidence threshold in at least 80% of Atanas records."

**Minor bookkeeping issue (not a deviation but worth noting):**
The fraction is hardcoded in `scripts/stage02_subgraph.py` line 31:

```python
COVERAGE_FRACTION = 0.80
```

It is not imported from `phase0_config.py`. The coding expectations in
`AGENTS.md` say "Never hard-code parameter values in scripts; always import
from `phase0_config.py`." The value matches `task.md` exactly, so no
scientific harm was done, but the constant is not under config control.

There is one additional subtlety: `task.md` says "confidence score ≥
threshold; **see Stage 5**" — implying the threshold was to be set at the
Stage 5 human decision checkpoint. Instead, `IDENTITY_CONFIDENCE_THRESHOLD
= 2.5` was set at a Stage 2 checkpoint (logged in `CHECKPOINT_LOG.md`
2026-05-28 entry "Identity-confidence threshold human decision recorded").
The checkpoint log records this was done before any label tables or subgraph
statistics were computed, and the value came from an explicit NeuroPAL
notebook threshold. This is procedurally a deviation from the stage ordering
in `task.md` but was logged and human-approved.

---

## 3. Exact AWC handling

### AWCON and AWCOFF

Both names pass through `normalize_neuron_label` unchanged (they are not
zero-padded ventral-cord labels and contain no whitespace). They are
recognized by `is_awc_on_off_label` as ON/OFF-style labels and reported,
but they are **not mapped** to `AWCL`/`AWCR`. No silent resolution.

`randi_all` therefore contains `AWCON` and `AWCOFF` as literal strings.
These do not match `AWCL` in the Atanas set, so they contribute nothing
to the common subgraph.

### AWCL

- Present in `atanas_high_coverage` (passes confidence threshold ≥ 2.5 in
  ≥ 32/40 Atanas records).
- Present in `randi_head` (from `aconnectome_ids_ganglia.json`, which uses
  left/right convention).
- NOT present in `randi_all` (from `neuron_ids.txt`, which uses ON/OFF
  convention).
- Outcome: included in `common_head_randi` (count 61), excluded from
  `common_all_randi` (count 60).
- `AWCL` appears in the reported 61-neuron label list.

### AWCR

- NOT present in the reported 61-neuron `N_COMMON_NEURONS` list.
- The feasibility report lists only `AWCL` (not `AWCR`) as a label present
  in `randi_head` but absent from `neuron_ids.txt`. This means either:
  (a) `AWCR` is also absent from `randi_head`, or
  (b) `AWCR` is present in both `randi_head` and `randi_all` (which would
      require `randi_all` to contain `AWCR`, inconsistent with it using only
      ON/OFF labels).

  Option (a) is more likely: the ganglia JSON may assign only `AWCL` (and
  `AWCON` is the right-side / OFF neuron in that preparation), but this has
  not been confirmed by inspecting the JSON contents.

- The more probable explanation, consistent with biology: Atanas records do
  not identify AWCR with sufficient confidence to pass the 80% threshold.
  The AWCOFF/AWCR neuron has less consistent spatial NeuroPAL identity
  across recordings, or it is labeled with uncertainty markers (`?`) and
  thus excluded by the ambiguity filter in `confident_labels`.

The exact reason AWCR is absent requires inspection of either the raw Atanas
confidence counts for AWCR or the ganglia JSON contents. This has not been
done; it is left for the human's review.

### AWCOFF and AWCON in the subgraph

Neither `AWCOFF` nor `AWCON` appears in the final 61-neuron label list.
`randi_all` has `AWCON` and `AWCOFF`; Atanas has `AWCL`; these do not
match. No neuron with an ON/OFF label enters the common subgraph through
any path in the current code.

---

## 4. Whether writing N_COMMON_NEURONS = 61 was premature

**Partially premature. Explanation follows.**

### What the script did

At line 633–634 of `scripts/stage02_subgraph.py`:

```python
n_common = len(common_head_randi)
write_phase0_n_common(n_common)
```

The script automatically wrote `N_COMMON_NEURONS = 61` to
`phase0_config.py` using the head-intersection value. This happened
without a checkpoint.

### The non-trivial choice made by the script

`task.md` Stage 2 Task 4 says: "present in both the Cook/Witvliet
connectome **and the Randi atlas**." It does not specify which Randi label
file to use. The script chose `randi_head` (from `aconnectome_ids_ganglia.json`)
over `randi_all` (from `neuron_ids.txt`), justified inline in the report as:

> "Primary `N_COMMON_NEURONS` is recorded as the Randi-head overlap because
> Randi 2023 is a head-ganglion preparation in the verified Phase 0 config."

This justification is scientifically reasonable — `RANDI_PREPARATION =
"immobilized"` confirms the Randi atlas covers head ganglia — but the
choice between "head label file" and "all-neuron label file" was a script
decision, not an explicit human decision at a checkpoint.

### What remains unresolved

Three open issues bear on whether N_COMMON_NEURONS = 61 is the correct
value:

1. **AWC convention is unresolved.** Whether `AWCL` should be in the
   subgraph depends on whether the `AWCL` label in Atanas maps to the
   same neuron as `AWCL` in the ganglia JSON — and more fundamentally,
   whether the Randi functional atlas covers that neuron under the ON/OFF
   or left/right identity. This has been flagged but not resolved.

2. **`SUBGRAPH_ADEQUATE` is still `None`.** The human decision on whether
   the 61-neuron composition is biologically adequate has not been made.
   `N_COMMON_NEURONS` is written before that decision.

3. **The head vs. all-neuron choice was not a human decision.** Using
   `randi_head` rather than `randi_all` directly determines whether AWCL
   is included (and potentially other neurons that differ between the two
   label files). This should have been a checkpoint item.

### Conclusion on prematurity

`N_COMMON_NEURONS = 61` was written to `phase0_config.py` before:
- the human reviewed the head vs. all-neuron Randi label-set choice,
- the AWC convention was resolved, and
- `SUBGRAPH_ADEQUATE` was set.

The value may be correct, but the write was procedurally premature. The
script made a non-trivial methodological choice (head overlap as primary)
and immediately wrote it to config without a checkpoint.

---

## 5. Whether a deviation should be recorded

Two items meet the deviation criteria:

**Deviation A (minor): `COVERAGE_FRACTION` hardcoded in script**
`AGENTS.md` coding expectations: "Never hard-code parameter values in
scripts; always import from `phase0_config.py`."
`COVERAGE_FRACTION = 0.80` is hardcoded in `stage02_subgraph.py` line 31
and is absent from `phase0_config.py`. The value is correct (matches
`task.md`) but is not under config control.

**Deviation B (procedural): N_COMMON_NEURONS written without checkpoint**
The script automatically wrote `N_COMMON_NEURONS = 61` to `phase0_config.py`
using a methodological choice (head vs. all-neuron Randi intersection) that
was not subject to a human checkpoint. The `AGENTS.md` checkpoint protocol
requires a checkpoint before "Any change to: … any item in `phase0_config.py`"
and before "Any deviation from `task.md`." Choosing which Randi label file
to treat as canonical is a choice not specified in `task.md`.

Neither deviation involved forbidden neural analysis or violated the hard
constraint. No ΔQ, precision matrix, covariance, or behavioral threshold was
computed. The scientific harm is limited, but both items should be recorded
in `DEVIATIONS.md` and reviewed before Stage 3 proceeds.

---

## Summary table

| Question | Finding |
|---|---|
| 60 vs 61 | AWCL is the sole differing neuron; randi_all uses AWCON/AWCOFF, randi_head uses AWCL/AWCR |
| 80% rule authorized? | Yes — explicit in task.md Stage 2 Task 4; constant hardcoded (not config-controlled) |
| AWC handling | No silent mapping; AWCL included via head path only; AWCR absent (likely Atanas coverage); AWCON/AWCOFF not in subgraph |
| N_COMMON_NEURONS = 61 premature? | Partially: head vs. all-neuron choice was script-made; AWC unresolved; SUBGRAPH_ADEQUATE not set |
| Deviation to record? | Two: (A) COVERAGE_FRACTION hardcoded; (B) N_COMMON_NEURONS written without checkpoint |
