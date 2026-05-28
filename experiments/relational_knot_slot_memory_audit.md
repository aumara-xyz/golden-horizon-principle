# Relational Knot-Slot Memory Audit

Date: 2026-05-23  
Status: experiment-side note only  
Do not harden into master/core paper yet.

## Current Claim

The strongest current toy result is not "phi writes memory."

The stronger claim is:

> Memory-like writes improve when delayed observer-boundary events are modeled as repeated landings in relationally linked slots, where nearby slots support the same knot-family.

## Best Supporting Tests

### v30 - Relational Knot Slots

File:

`golden_zipper_v30_relational_knot_slots.py`

Result:

- independent slots mean score: `0.503`
- relational slots mean score: `0.570`
- best branch: `relational:silver` at `0.575`
- golden relational mean: `0.572`
- golden density gap: `+0.164`
- golden block gap: `+0.226`
- golden rupture rate: `0.006`

Interpretation:

This supports the idea that memory is not an isolated bead in an isolated slot. It behaves better when repeated events stack in linked probability slots.

### v31 - Path-Phase Groove Memory

File:

`golden_zipper_v31_path_phase_groove_memory.py`

Result:

- slot_stack mean score: `0.491`
- relational mean score: `0.647`
- phase_groove mean score: `0.737`
- best branch: `phase_groove:silver` at `0.745`
- golden phase-groove mean: `0.740`
- golden density gap: `+0.336`
- golden block gap: `+0.406`
- golden phase scramble gap: `-0.032`

Interpretation:

Path grooves strongly improve the score and preserve density/block gaps, but the negative phase-scramble gap means the phase-specific claim is not yet secure.

## Simple Picture

The observer is not just catching isolated beads.

Delayed information falls through a fixed probability board. Repeated landings carve grooves. Nearby grooves reinforce each other. A memory is a knot-like region made by repeated path landings, not a static stored object.

## Red-Team Boundary

Do not claim:

- phi uniquely wins
- Aharonov-Bohm proves GHP
- magnetism derives observer-memory
- path phase is physically established in GHP
- torus geometry is technically identified with the toy
- the VPS becomes a horizon or dynamical driver

Safe claim:

> The latest toy results support relational/path-history memory as a better model than isolated local slot storage.

## Paper Recommendation

Do not update the master or core paper yet.

Do update the research ledger or experiment appendix with:

- v30 as the strongest clean positive
- v31 as a promising but not-yet-secure phase-groove extension
- explicit note that golden is competitive but not unique
- explicit note that relational structure is doing more work than phi selection

## Next Test

`v31b_phase_scramble_repair.py`

Question:

> Does the phase-groove effect survive a stricter phase-null panel when the phase observable is made gauge-like, meaning arbitrary phase offsets should cancel but broken path order should not?

Success:

- phase_groove remains above relational
- phase-scramble gap turns positive
- arbitrary constant phase shift changes little

Failure:

- phase_groove advantage disappears under clean phase nulls
- phase shifts change the score too much

