# BSW-001 Boundary Sequence & Witness Footprint Probe

Toy telemetry only. This tests witness footprint and public-trace sequence effects.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| WPF-001 | PASS | best_field_set / action_f1 / private_f1 / witness_confidence_plateau | `full_public / 0.9983 / 0.0272 / 0.0091` | Witness is active quarantine if it has a stable pressure footprint, not a null trace. |
| STP-001 | FAIL | sequence_mae / memoryless_mae / shuffled_mae / gain_vs_memoryless | `0.01880 / 0.01908 / 0.01908 / 0.00028` | Temporal boundary effects are useful only if prior public trace improves next-stability prediction over memoryless and shuffled controls. |

## Witness Field Sets

| Set | Action F1 | Private F1 | Fields |
| --- | ---: | ---: | --- |
| pressure_shape | 0.9965 | 0.0208 | confidence_delta+entropy_delta+stability_delta+retry_count |
| no_retry | 0.9960 | 0.0208 | confidence_delta+entropy_delta+stability_delta |
| friction_only | 0.6265 | 0.0208 | retry_count+refusal_cause |
| full_public | 0.9983 | 0.0272 | confidence_delta+entropy_delta+stability_delta+retry_count+refusal_cause |

## Safe Read

If WPF passes, witness should be treated as active quarantine, not a null trace.
If STP passes, the next live handoff should include sequence-level telemetry, not isolated events only.

Do not claim this proves GHP physics, consciousness, Markov blankets, split property, or literal thermodynamics.
