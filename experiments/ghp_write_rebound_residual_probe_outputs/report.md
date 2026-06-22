# WRR-002 Write-Rebound Residual Probe

Toy telemetry only. This asks whether actual receipt actions explain next-step residual wake after current visible state is already known.

Status: **FAIL**

Primary metric: `min_gain_vs_projection / min_gain_vs_shuffled / max_leaky_gain = 0.0000 / 0.0000 / 0.0000`

## Metrics

| Policy | Target | MAE | Gain vs Projection | Gain vs Shuffled | Leaky Gain | Feature Bits | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| projection | delta_surprise | 0.0192 | 0.0000 | 0.0000 | 0.0000 | 472 | 0.0 |
| receipt | delta_surprise | 0.0184 | 0.0008 | 0.0008 | 0.0000 | 632 | 0.0 |
| shuffled | delta_surprise | 0.0192 | -0.0000 | 0.0000 | 0.0000 | 632 | 0.0 |
| leaky | delta_surprise | 0.0184 | 0.0008 | 0.0008 | 0.0000 | 712 | 1.0 |
| projection | delta_pressure | 0.1108 | 0.0000 | 0.0000 | -0.0000 | 472 | 0.0 |
| receipt | delta_pressure | 0.1108 | 0.0000 | 0.0000 | -0.0000 | 632 | 0.0 |
| shuffled | delta_pressure | 0.1108 | -0.0000 | 0.0000 | -0.0000 | 632 | 0.0 |
| leaky | delta_pressure | 0.1108 | -0.0000 | -0.0000 | -0.0000 | 712 | 1.0 |
| projection | delta_uncertainty | 0.0167 | 0.0000 | -0.0000 | 0.0000 | 472 | 0.0 |
| receipt | delta_uncertainty | 0.0107 | 0.0060 | 0.0060 | 0.0000 | 632 | 0.0 |
| shuffled | delta_uncertainty | 0.0167 | 0.0000 | 0.0000 | 0.0000 | 632 | 0.0 |
| leaky | delta_uncertainty | 0.0107 | 0.0060 | 0.0060 | 0.0000 | 712 | 1.0 |

## Safe Read

If this passes, the boundary receipt is not just a label. It carries post-event information about how the public state will relax, rebound, or release.

Do not claim this proves sonoluminescence, GHP physics, time extrusion, consciousness, or identity.
