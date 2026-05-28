# Golden Zipper v2C — Memory Policy Mode

Toy telemetry only. Not physics evidence.

This mode applies write / witness / release only after the base symbolic trail is generated. It asks whether golden sampling gives a better structured-enough-to-remember but irrational-enough-not-to-freeze tradeoff.

## Family Means

| Family | Phase-lock | Pollution | Delayed retention | Write | Witness | Release | Tradeoff |
|---|---:|---:|---:|---:|---:|---:|---:|
| bronze | 0.000 | 0.001 | 0.333 | 2929.0 | 1166.3 | 0.7 | 2.222 |
| golden | 0.000 | 0.002 | 1.000 | 3041.7 | 1054.0 | 0.3 | 2.952 |
| near_golden | 0.001 | 0.003 | 0.406 | 3110.4 | 942.4 | 43.1 | 2.306 |
| random | 0.007 | 0.003 | 0.446 | 3125.9 | 892.6 | 77.5 | 2.299 |
| rational_approx | 0.287 | 0.001 | 0.111 | 3683.4 | 412.4 | 0.1 | 1.865 |
| rational_control | 0.340 | 0.001 | 0.000 | 4092.0 | 4.0 | 0.0 | 1.564 |
| silver | 0.000 | 0.002 | 0.667 | 3057.0 | 1038.3 | 0.7 | 2.598 |

## Key Result

Golden slope did not win every metric, but may occupy the best anti-locking / delayed-retention tradeoff region.

- Anti-locking vs rationals: **better**
- Delayed-meaning retention: **better**
- Stable write behavior: **better**
- Robust to window size/phase: **reasonably**
- Silver beats golden? **no clear overall**
- Bronze beats golden? **no clear overall**

Strongest run: `rational_13_21` window=0.34 phase=0.00
Weakest run: `control_1_3` window=0.47 phase=0.17

Do-not-claim: no confirmation, no write-law closure, no VPH derivation, no consciousness derivation.