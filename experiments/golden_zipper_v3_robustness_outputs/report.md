# Golden Zipper v3 — Robustness Sweep

Toy telemetry only. Not physics evidence.

This sweep varies the memory-policy thresholds to test whether golden remains top-tier across many plausible write / witness / release policies, or only under one chosen policy.

Threshold grid size: **243** policy settings.

## Robustness Table

| Family | #1 count | #2 count | #3 count | Mean tradeoff | Mean phase-lock | Mean delayed retention | Mean pollution |
|---|---:|---:|---:|---:|---:|---:|---:|
| bronze | 12 | 28 | 38 | 2.099 | 0.000 | 0.235 | 0.018 |
| golden | 130 | 43 | 6 | 2.421 | 0.000 | 0.518 | 0.002 |
| near_golden | 36 | 42 | 114 | 2.179 | 0.001 | 0.300 | 0.016 |
| random | 9 | 42 | 16 | 2.060 | 0.007 | 0.249 | 0.032 |
| rational_approx | 0 | 0 | 3 | 1.851 | 0.287 | 0.099 | 0.001 |
| rational_control | 0 | 0 | 0 | 1.564 | 0.340 | 0.000 | 0.001 |
| silver | 56 | 88 | 66 | 2.248 | 0.000 | 0.356 | 0.013 |

## Supports

Golden remains robustly top-tier in anti-locking / delayed-retention tradeoff across threshold sweeps.

- The sweep cleanly separates policy tuning from the underlying symbolic trail.
- Near-golden perturbations help show whether golden is a point winner or part of a broader admissible band.
- The Pareto views make it easier to see whether lower phase-lock comes with retention costs.

## Does Not Support

- no proof
- no physics evidence
- no write-law closure
- no VPH derivation
- no consciousness claim

## Next Test

- expand the near-golden band beyond +/-0.02 into a denser local alpha sweep
- test whether the same tradeoff survives moving-window observer variants under the same threshold grid
- compare the top-tier families against a null family of low-discrepancy irrational slopes, not only silver/bronze/random controls

Strongest run: `rational_13_21` policy=61 window=0.34 phase=0.00
Weakest run: `random_1` policy=162 window=0.20 phase=0.17

Success language: Golden remains robustly top-tier in anti-locking / delayed-retention tradeoff across threshold sweeps.