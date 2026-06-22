# Boundary-Collapse Hardening Battery

## Purpose

This battery tests the conservative imports added after the acoustic-cavitation / sonoluminescence grounding pass.

The goal is not to prove GHP physics.
The goal is to test whether three analogues can survive minimal controls as engineering grammar:

1. **CAC-001:** continuous drive can become discrete write only through nonlinear boundary collapse.
2. **NET-001:** "net" language is useful only when formalized as graph / tensor-neighborhood structure.
3. **CAS-001:** cascade language is useful only when formalized as nested finite-access projection / Markov-blanket coarse-graining.

## Probe Map

### CAC-001 - Cavitation Analogue Collapse Toy

```text
continuous drive a(t)
  -> nonlinear boundary compression
  -> discrete localized write event r_t
```

Controls:

- naive amplitude threshold,
- shuffled drive,
- random write rate.

Pass meaning:

```text
collapse rule beats naive and shuffled controls with low false writes
```

### NET-001 - Nodal Net Boundary Toy

```text
graph G=(V,E)
  -> node pressure + neighborhood coherence
  -> write / witness / release
```

Controls:

- flat node-only threshold,
- shuffled graph topology,
- always-release baseline.

Pass meaning:

```text
true topology matters enough that shuffled topology cannot reconstruct nearly as well
```

### CAS-001 - Cascade Coarse-Graining Probe

```text
M_0 -> M_1 -> M_2 -> N_t -> r_t
```

Controls:

- one-step compression,
- overcompressed public bit,
- leaky oracle using private hidden material.

Pass meaning:

```text
staged finite-access projection preserves write-relevant structure without private leakage
```

## Result Summary

- `CAC-001`: PASS.
- `NET-001`: FAIL under the pre-set shuffled-topology gap threshold.
- `CAS-001`: PASS.

The failed `NET-001` result is useful. It says the "net" analogue needs stronger topology-sensitive tests before it should be treated as hardened. Graph language is allowed as formal machinery, but not yet as a strong result.

## Strongest Failure Mode

The strongest failure mode is analogy laundering:

```text
real physical or symbolic pattern
  -> evocative metaphor
  -> treated as evidence
```

The battery prevents that by forcing each analogy through controls.
