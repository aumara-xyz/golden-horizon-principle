# CAS-005 Finite-Depth Optimum Audit

Toy telemetry only. This audits whether an intermediate finite projection depth repeatedly beats raw, over-deep, shuffled, and leaky controls.

| Probe | Status | Metric | Value | Safest Read |
| --- | --- | --- | --- | --- |
| CAS-005 | FAIL | intermediate_wins / modal / avg_f1 / raw_gap / overdeep_gap / shuffled_gap / leaky_gain | `7/8 / depth_4:4 / 0.6418 / 0.4832 / 0.0169 / 0.5015 / -0.0038` | If this passes, the paper-safe claim is finite intermediate projection depth can outperform raw and over-filtered access in toy observer-boundary regimes; no universal depth is claimed. |

## Regime Summary

| Regime | Best Clean | F1 | Raw Gap | Overdeep Gap | Shuffled Gap | Leaky Gain | AUC-like |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable | depth_4 | 0.5976 | 0.4859 | 0.0196 | 0.4750 | 0.0073 | 0.9794 |
| noisy | depth_5 | 0.6838 | 0.4807 | 0.0092 | 0.6514 | -0.0126 | 0.9567 |
| drifty | depth_5 | 0.6425 | 0.4819 | 0.0080 | 0.4889 | -0.0033 | 0.9651 |
| bursty | depth_4 | 0.6371 | 0.5201 | 0.0196 | 0.6371 | 0.0019 | 0.9744 |
| sparse | depth_4 | 0.5229 | 0.4748 | 0.0523 | 0.1245 | 0.0043 | 0.9902 |
| dense | depth_5 | 0.7217 | 0.4479 | 0.0207 | 0.5395 | 0.0007 | 0.9617 |
| volatile | depth_4 | 0.6843 | 0.4512 | 0.0058 | 0.5050 | -0.0070 | 0.9571 |
| smooth | depth_7 | 0.6444 | 0.5232 | 0.0000 | 0.5908 | -0.0217 | 0.9818 |

## Paper-Safe Read

If used, say only that finite intermediate projection depth can outperform raw access and over-filtered access in toy observer-boundary regimes.

Do not claim a universal magic depth, GHP physics evidence, consciousness evidence, or observer-created reality.
