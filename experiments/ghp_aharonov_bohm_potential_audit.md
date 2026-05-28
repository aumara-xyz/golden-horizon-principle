# GHP Aharonov-Bohm / Potential Audit

Date: 2026-05-22  
Status: experiment-side note only  
Scope: analogy audit, not paper hardening

## One-Line Read

The Aharonov-Bohm effect is useful for GHP as an analogy for **architecture affecting observable phase without local force**, but it does not prove the GHP, the VPS, phi selection, observer collapse, or memory write-laws.

## Why It Feels Relevant

The useful structural pattern is:

- local force/field can vanish in the particle path
- a global/topological quantity can still change the observable phase
- the observable is not the potential value alone, but a path-dependent phase relation
- a toroidal geometry can hide local field while preserving a measurable phase difference

In GHP language, this rhymes with:

- observer sees rendered outcomes, not raw hidden structure
- memory may depend on path/history/phase, not isolated events
- the zero-boundary may be a comparison surface, not a force source
- relational knot-slots may matter more than pointwise values

## Strict Red-Team Boundary

This must **not** be framed as:

- proof that GHP is physically true
- proof that zero-boundary observer collapse is quantum mechanical
- proof that phi is selected by magnetism
- proof that torus geometry in the toy corresponds to electromagnetic gauge theory
- proof that potentials are the missing write-law

The safe claim is much narrower:

> Aharonov-Bohm gives a real physics example where observable behavior depends on global phase/topology rather than local force along the path. This supports using global/relational toy variables as analogies, not as derivations.

## What Transfers To The GHP Toys

### 1. Phase Is More Fundamental Than Point-Force In Some Regimes

The AB effect is a warning against thinking only in local pushes. For GHP toys, this supports testing:

- accumulated phase
- winding history
- slot relation
- path-dependent memory
- delayed comparison
- global topology of returns

This fits the v30 result better than earlier one-point crossing toys.

### 2. The Torus Matters As A Topological Separator

The toroidal magnet in the AB setup is relevant as a clean image:

- field can be confined inside the torus
- electrons outside can still show a shifted interference pattern
- what matters is not simply local contact, but how paths wrap around hidden structure

For GHP, the safe analogy is:

> the observer may not access the hidden interior directly, but path/history around the boundary can still affect what becomes observable.

### 3. The Observable Is Relational

The AB phase shift is measured by interference between paths. This strongly rhymes with v30:

- not one bead
- not one isolated slot
- relation between neighboring/linked slots
- repeated path history forms a knot-like memory family

This is a better fit than early "single write point" models.

## What Does Not Transfer

### 1. Gauge Theory Does Not Derive GHP

The electromagnetic vector potential is a U(1) gauge object. That does not derive:

- Fibonacci anyons
- phi as memory anchor
- VPS horizon language
- observer-consciousness collapse
- Markov blanket write-laws

Any paper language implying this would be a forced fit.

### 2. Torus Geometry Is Not Automatically The Same Torus

The AB torus is a physical magnetic confinement geometry. The GHP torus/zero-boundary toy is an observer-memory metaphor and simulation object.

They can rhyme structurally, but they are not the same mathematical object unless a formal map is built.

### 3. Potentials Are Gauge-Subtle

The physically meaningful AB quantity is not an arbitrary potential height. It is a gauge-invariant phase relation, usually expressed through a loop/path integral.

For GHP, this means:

> if we use "potential" language, we need a gauge-invariant observable analogue, not just a poetic hidden field.

## Impact On Current GHP Direction

This strengthens the case for the **relational knot-slot** branch, not the old phi-uniqueness branch.

The best current toy result remains v30:

- independent slots mean score: 0.503
- relational slots mean score: 0.570
- golden relational mean score: 0.572
- golden density gap: +0.164
- golden block gap: +0.226

AB-like lesson:

> memory may not be a local bead in a local slot; it may be a path-dependent phase/knot relation across slots.

## Recommended Next Test

`golden_zipper_v31_path_phase_knot_memory.py`

Core question:

> Does memory improve when slot writes depend on accumulated loop/path phase, not just repeated slot landings?

Test modes:

- `slot_stack`: v30 baseline
- `relational_slot_stack`: v30 relational mode
- `path_phase`: write depends on accumulated path phase around slots
- `path_phase_relational`: accumulated phase plus neighboring knot support
- `phase_scrambled_null`: same slot densities, broken path phase
- `gauge_shift_null`: add arbitrary constant offset to phase; result should not change

Success condition:

- path-phase relational mode beats v30 relational
- positive density/block/phase-scramble gaps
- gauge-shift null does not alter results materially

Failure condition:

- phase language adds no predictive value
- scrambled phase does just as well
- arbitrary gauge shifts change the outcome

## Red-Team Addition To The Protocol

Yes, add the EWCS/reflected-entropy ablation parameter.

Suggested clause:

> **Bridge-Ablation Requirement:** Re-run the argument after deleting all EWCS, reflected entropy, holographic entropy, and subfactor bridge language. If the core VPS/GHP claim weakens, the bridge language is carrying argumentative load and must be demoted to speculative vocabulary. If the core claim survives, the bridge candidates may remain as optional future formalization lanes only.

## Overnight Verdict

This is a meaningful update, but not because "magnetism proves GHP."

It is meaningful because AB gives us a disciplined external analogy for:

- hidden topology
- path-dependent phase
- relational observables
- toroidal separation between hidden interior and measurable boundary

The next serious move is not to cite AB as evidence. The next move is to test whether **path phase** improves the v30 relational knot-slot toy.

