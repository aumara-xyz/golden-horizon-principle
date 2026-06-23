# BTA-007 Crossing-Complexity Simplification Probe

Toy telemetry only. `Crossing number` here means a public engineering proxy, not literal knot theory.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| BTA-007A | MIXED | real pressure improvement gap over shuffled control | `phi_gap=0.0155; sqrt2_gap=-0.0642` | A crossing-complexity proxy is useful only if real high-pressure windows select cheaper future replay than shuffled-pressure windows. |
| BTA-007B | MIXED | strategy selectivity / PRNG non-promotion | `phi_mode=argmax; sqrt2_mode=reset_sqrt2; prng_improvement=0.1032` | Simplification must select the matching compact family when one exists and avoid treating random traces as clean topology. |
| BTA-007C | PASS | exact replay and leak scan | `replay=1.0000; leak=0.0000` | Any simplification summary must replay public actions and carry no private or authority-shaped fields. |

## Source Summary

| Source | Shuffled | Strategy Mode | Improvement | Mismatch | Shock | Replay | Leak | Summary/Actions | Windows |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| argmax | 0 | argmax | 0.3534 | 0.4774 | 0.1141 | 1.0 | 0.0 | 3.8259 | 48 |
| argmax | 1 | argmax | 0.4042 | 0.4247 | 0.1296 | 1.0 | 0.0 | 3.9353 | 48 |
| human_jitter | 0 | argmax | 0.3330 | 0.4907 | 0.1220 | 1.0 | 0.0 | 2.9540 | 48 |
| human_jitter | 1 | argmax | 0.3704 | 0.4527 | 0.1419 | 1.0 | 0.0 | 2.9963 | 48 |
| phi_resettable | 0 | argmax | 0.0998 | 0.7463 | 0.1300 | 1.0 | 0.0 | 2.4974 | 48 |
| phi_resettable | 1 | continue_phi | 0.0843 | 0.6074 | 0.1636 | 1.0 | 0.0 | 2.5071 | 48 |
| prng | 0 | argmax | 0.1032 | 0.6528 | 0.1428 | 1.0 | 0.0 | 2.4063 | 48 |
| prng | 1 | argmax | 0.1016 | 0.6576 | 0.1649 | 1.0 | 0.0 | 2.4139 | 48 |
| sqrt2_resettable | 0 | reset_sqrt2 | 0.1450 | 0.7090 | 0.1157 | 1.0 | 0.0 | 2.9256 | 48 |
| sqrt2_resettable | 1 | argmax | 0.2092 | 0.6458 | 0.1261 | 1.0 | 0.0 | 2.9514 | 48 |

## Safe Read

This probe supports testing a simplification pass only as offline advisory analysis. It does not justify live sampler resets. The useful invariant is: high public knot pressure may identify moments where a compact replay model should be re-fit, but any resulting summary must remain replayable, residual-explicit, and authority-isolated.
