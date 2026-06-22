# BTA-001 Boundary Trace Adversarial Probe

Toy telemetry only. This stress-tests the HRT/MCT/MBT trace under harder regime holdouts.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| BTA-001 | PASS | cross_action_f1 / shuffled_f1 / private_f1 / authority_f1 | `0.7624 / 0.3333 / 0.0230 / 0.0730` | The public trace survives harder regime holdout only if it beats shuffled controls while private state remains near chance. |
| LAT-001R | FAIL | latency_only_f1 / full_minus_no_entropy | `0.5206 / -0.0781` | Latency is not primary unless it carries signal under regime holdout and materially improves the full model. |

## Field Sets

| Set | Action F1 | Shuffled F1 | Private F1 | Authority F1 | Bits |
| --- | ---: | ---: | ---: | ---: | ---: |
| full | 0.7553 | 0.3331 | 0.0393 | 0.0909 | 704 |
| minimal_noisy | 0.3537 | 0.2907 | 0.0145 | 0.0501 | 200 |
| cross_section | 0.7624 | 0.3333 | 0.0230 | 0.0730 | 504 |
| no_entropy | 0.8334 | 0.3246 | 0.0311 | 0.0728 | 664 |
| latency_only | 0.5206 | 0.2980 | 0.0150 | 0.0500 | 176 |

## Safe Read

If this passes, the HRT handoff becomes stronger but remains an engineering analogue only.

Do not claim this proves EWCS, Markov blankets, split property, Hawking radiation, consciousness, or GHP physics.
