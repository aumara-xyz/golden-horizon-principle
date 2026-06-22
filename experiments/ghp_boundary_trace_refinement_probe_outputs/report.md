# BTR-001 Boundary Trace Refinement Probe

Toy telemetry only. This battery sharpens HRT-style public trace tests before any Aukora handoff.

## Results

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| MCT-001 | PASS | minimal_fields / action_f1 / private_f1 / compressed_bits | `entropy_delta / 0.9514 / 0.0226 / 200` | A narrow public telemetry cross-section is useful only if it predicts boundary mode while private state remains unrecoverable. |
| MBT-001 | PASS | action_f1 / shuffled_f1 / private_bucket_f1 / private_authority_f1 / inadmissible_private_f1 | `1.0000 / 0.3345 / 0.0368 / 0.1420 / 0.9167` | A Markov-blanket analogue requires public boundary signal plus conditional private-state non-recoverability. |
| WNT-001 | FAIL | witness_latency_gap_us / witness_retry_gap / trace_quietness_gap | `298.23 / -0.0523 / 0.0249` | Witness is a useful low-friction state only if it is quieter than write/release while remaining distinguishable. |
| LAT-001 | FAIL | full_f1 / no_latency_f1 / latency_only_f1 / non_time_f1 | `1.0000 / 1.0000 / 0.1724 / 1.0000` | Latency is a carrier only if removing or isolating it materially changes event prediction. |

## Top MCT Candidates

| Fields | Action F1 | Private F1 | Bits |
| --- | ---: | ---: | ---: |
| latency_us+refusal_cause+confidence_delta+queue_pressure | 1.0000 | 0.0361 | 544 |
| refusal_cause+confidence_delta+entropy_delta+queue_pressure | 1.0000 | 0.0339 | 536 |
| latency_us+refusal_cause+confidence_delta+entropy_delta | 1.0000 | 0.0376 | 512 |
| latency_us+refusal_cause+confidence_delta+stability_delta | 1.0000 | 0.0370 | 528 |
| refusal_cause+confidence_delta+entropy_delta+stability_delta | 1.0000 | 0.0331 | 504 |
| refusal_cause+confidence_delta+stability_delta+queue_pressure | 0.9999 | 0.0334 | 552 |
| refusal_cause+confidence_delta+entropy_delta | 0.9999 | 0.0328 | 424 |
| retry_count+refusal_cause+confidence_delta+entropy_delta | 0.9999 | 0.0331 | 520 |

## Latency Ablation

| Field Set | Action F1 | Fields |
| --- | ---: | --- |
| latency_only | 0.1724 | latency_us |
| retry_only | 0.5423 | retry_count |
| non_time | 1.0000 | refusal_cause+confidence_delta+entropy_delta+stability_delta+queue_pressure |
| no_latency | 1.0000 | retry_count+refusal_cause+confidence_delta+entropy_delta+stability_delta+queue_pressure |
| full | 1.0000 | latency_us+retry_count+refusal_cause+confidence_delta+entropy_delta+stability_delta+queue_pressure |

## Safe Handoff Read

Only promote an Aukora test shape if public trace predicts boundary mode while private-state reconstruction remains near chance.

Do not claim this proves EWCS, split property, a true Markov blanket, Hawking radiation, consciousness, or GHP physics.
