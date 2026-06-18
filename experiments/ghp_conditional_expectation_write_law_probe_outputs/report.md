# GHP Conditional Expectation Write-Law Probe

Status: synthetic toy telemetry only.

This asks whether observer-visible projected state is sufficient for legal canonical writes, while raw hidden state stays out of the writer and out of the public receipts.

It does not prove GHP physics or consciousness.

## Results

### CEW-001: watch

- Metric: threshold_replay_acc; shuffled_replay_acc; always_replay_acc; never_replay_acc; threshold_false_write; threshold_missed_write; hidden_bits; threshold_public_bits; leakage_count
- Value: 1.0000; 0.0000; 0.0000; 0.0008; 0.0000; 0.0000; 228840; 264576; 0
- Null hypothesis: The thresholded projection writer does not outperform shuffled / always-write / never-write controls on public trajectory reconstruction, once private leakage is forbidden.
- Safest read: A legal writer using only observer-visible projected state can replay the public trajectory cleanly while keeping hidden state inaccessible.
- Falsifier: Shuffled or flat controls match replay accuracy, or any private hidden payload leaks into public outputs.

### CEW-002: pass / projection invariance

- Metric: projection_equivalence_violations; hidden_only_flip_rate; cheat_projection_violations; cheat_hidden_flip_rate
- Value: 0; 0.0000; 0; 0.0000
- Null hypothesis: Legal write decisions change under hidden-only perturbations or for hidden states sharing the same observer projection.
- Safest read: Canonical legal writes are projection-defined: same visible projection gives the same write decision, and changing hidden-only fields does not move the legal writer.
- Falsifier: Projection-equivalent states yield different legal writes, or hidden-only perturbations flip the legal writer.

### CEW-003: pass / threshold and seed stability

- Metric: threshold_sweep_accs; seed_mean_replay_acc; seed_std_replay_acc; seed_mean_shuffled_acc; seed_std_shuffled_acc
- Value: 4:0.0017; 5:1.0000; 6:1.0000; 7:0.0125; 1.0000; 0.0000; 0.0005; 0.0007
- Null hypothesis: The observed win is threshold-cherry-picked or unstable across deterministic seeds.
- Safest read: The projected writer stays strong across deterministic seeds, and the threshold sweep shows a small stable band rather than a one-threshold miracle.
- Falsifier: Only one threshold works or performance collapses under seed changes.

### CEW-004: inadmissible cheat

- Metric: cheat_replay_acc; cheat_false_write; cheat_missed_write; cheat_public_bits
- Value: 1.0000; 0.0000; 0.0000; 264976
- Null hypothesis: Raw hidden/internal state is a valid legal writer if it performs well enough.
- Safest read: Raw hidden-state access may be computationally useful, but it is outside the admissible write law and must not be promoted into canonical writing authority.
- Falsifier: The framework celebrates raw hidden-state writing as a legitimate canonical writer.

## Controls Included

- thresholded projection writer
- always-write control
- never-write control
- shuffled-projection control
- raw-state-leak cheat control
- projection-equivalence control
- hidden-only perturbation control
- threshold sweep
- seed stability sweep
- leakage scanner

## Aukora Translation

```text
hidden state M_t
  -> observer-visible projection E_t(M_t) = N_t
  -> thresholded legal write decision
  -> signed public receipt
  -> replayable public trajectory
```

Handoff law:

```text
Canonical writes may be triggered only by observer-visible projected state,
never by raw hidden/internal state.
Public receipts must replay public trajectory without private-state leakage.
```

Hard rule:

```text
Raw hidden-state access may exist as an inadmissible cheat control.
It must never be promoted into canonical writer authority.
```
