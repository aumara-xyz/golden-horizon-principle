# RRL-001 Readability Relaxation Law Probe

Toy telemetry only. This tests the narrowed law: receipt -> public readability shift -> lagged surprise relaxation.

Status: **FAIL**

Primary metric: `min_uncertainty_gain / lagged_surprise_gain / max_leaky_gain`

Value: `0.0017 / 0.0002 / 0.0018`

## Metrics

| Policy | Target | MAE | Gain vs Projection | Gain vs Shuffled | Leaky Gain | Feature Bits | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| projection | delta_uncertainty_1 | 0.0070 | 0.0000 | -0.0000 | 0.0014 | 480 | 0.0 |
| receipt | delta_uncertainty_1 | 0.0053 | 0.0017 | 0.0017 | 0.0014 | 632 | 0.0 |
| shuffled | delta_uncertainty_1 | 0.0070 | 0.0000 | 0.0000 | 0.0014 | 632 | 0.0 |
| leaky | delta_uncertainty_1 | 0.0040 | 0.0031 | 0.0031 | 0.0014 | 704 | 1.0 |
| projection | delta_uncertainty_2 | 0.0130 | 0.0000 | -0.0000 | 0.0018 | 480 | 0.0 |
| receipt | delta_uncertainty_2 | 0.0107 | 0.0023 | 0.0023 | 0.0018 | 632 | 0.0 |
| shuffled | delta_uncertainty_2 | 0.0130 | 0.0000 | 0.0000 | 0.0018 | 632 | 0.0 |
| leaky | delta_uncertainty_2 | 0.0089 | 0.0041 | 0.0041 | 0.0018 | 704 | 1.0 |
| projection | delta_surprise_2 | 0.0650 | 0.0000 | 0.0000 | 0.0000 | 480 | 0.0 |
| receipt | delta_surprise_2 | 0.0648 | 0.0002 | 0.0002 | 0.0000 | 632 | 0.0 |
| shuffled | delta_surprise_2 | 0.0650 | -0.0000 | 0.0000 | 0.0000 | 632 | 0.0 |
| leaky | delta_surprise_2 | 0.0647 | 0.0002 | 0.0002 | 0.0000 | 704 | 1.0 |

## Safe Read

If this passes, the paper-safe result is that actual receipt actions can improve prediction of public readability relaxation and later surprise relaxation in a controlled toy boundary.

Do not claim this proves GHP physics, sonoluminescence, time extrusion, consciousness, identity, or observer selection.
