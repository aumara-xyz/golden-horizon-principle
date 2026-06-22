# Boundary Sequence & Witness Notes

Status: toy telemetry only.

`ghp_boundary_sequence_witness_probe.py` follows the BTA/BTR line by asking two narrower questions:

- `WPF-001`: if witness is not a null trace, what is its public footprint?
- `STP-001`: does the public trace of event `N` improve prediction of event `N+1`?

## Results

- `WPF-001`: pass. Witness behaves like an active quarantine / pressure-holding state, not a null state. The best public pressure-shape package reaches action F1 `0.9983` with private reconstruction F1 `0.0272`.
- `STP-001`: fail. Sequence-aware prediction improves next stability only weakly (`0.00028` MAE gain over memoryless), below promotion threshold.

## Current Read

The witness correction is useful:

> witness is not silence; witness is held tension.

But the temporal aftershock law is not yet established:

> event N public trace does not yet strongly predict event N+1 public stability in this toy.

## Handoff Discipline

For live Aukora, include witness footprint telemetry, but do not yet claim a sequence law.

Recommended safe telemetry:

- confidence delta,
- entropy / logprob proxy if safe,
- stability delta,
- retry count,
- refusal cause.

Do not assume:

- witness is null,
- latency is primary,
- sequence aftershock is proven,
- the toy proves GHP physics, consciousness, Markov blankets, split property, or thermodynamics.
