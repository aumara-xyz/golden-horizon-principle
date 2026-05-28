# GHP Boundary Access Channel Toy Spec

Status: build spec for the next 5.4 implementation pass.

Not proof. Not a paper update.

## Goal

Build the smallest toy that tests this question:

> Does Fibonacci-style branching preserve a better combined package of access, recovery, redundancy, and shared-overlap than simpler comparison branchings?

## Core Object

Use the bridge-hunt notation:

```text
O_t = (M_t, N_t, E_t, R_t, Red_t, S_shared)
```

Minimal toy meanings:

- `M_t`: hidden ambient state graph
- `N_t`: observer-readable state subset
- `E_t`: access map from hidden state to readable state
- `R_t`: recovery score after erasure or masking
- `Red_t`: redundancy score across observer fragments
- `S_shared`: overlap score between two observer fragments

## Comparison Families

Implement four branch families:

1. binary abelian branching
2. generic ternary branching
3. Fibonacci branching
4. one non-Fibonacci non-abelian control, if easy

The comparison is not "who gets the prettiest score."

The comparison is:

```text
access + recovery + redundancy + shared overlap
```

under the same compression / erasure pressure.

## Minimal Dynamics

At each step:

1. generate or update hidden ambient state `M_t`
2. apply branch rule
3. project through access map `E_t`
4. split readable traces into at least two observer fragments
5. measure direct access fidelity
6. mask or erase part of the readable state
7. measure recovery `R_t`
8. measure redundancy `Red_t`
9. measure overlap `S_shared`

## First Metrics

Use simple metrics first:

- `Access fidelity`
  how much of the hidden structure is preserved in readable form

- `Recovery score`
  how well masked readable state can be reconstructed

- `Redundancy score`
  how much the two observer fragments both preserve enough of the same record

- `Shared-overlap score`
  how much the two fragments agree on the same meaningful structure

- `Compression failure score`
  how quickly the branch family collapses under over-compression

## Promotion Rule

Fibonacci does not need to dominate every metric.

It needs to show a stronger combined package on:

- access
- recovery
- redundancy
- shared overlap

while staying stable under damage / compression.

## Demotion Rule

If binary or generic ternary branching matches Fibonacci across the combined package, weaken the "minimal readable architecture" claim.

If the toy cannot distinguish branching families in a stable way, do not promote anything.

## Connection To The "Zero Observer" Intuition

In toy terms:

- hidden state = potential side
- access map `E_t` = boundary crossing
- readable state = written side
- repeated readable access = memory ordering / time-like sequence

That intuition is allowed to guide the toy shape.

It is not allowed to count as evidence by itself.

## First Implementation Constraint

Keep the first toy boring.

No topology theater.

No consciousness language.

No fancy geometry unless it changes the metric outcomes.

The first pass should answer only this:

> Is there any measurable reason to think Fibonacci-style branching helps the observer-boundary package more than simpler branchings do?

