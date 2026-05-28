# Golden Zipper v2B — Spiral / Observer-Window Mode

Toy telemetry only. Not physics evidence.

This mode separates observer-window effects from the pure Sturmian test. It compares moving-phase windows and a two-window bidirectional observer variant.

## Family Means

| Family | Balance | Spread | Complexity dev. | Phase-lock | Tradeoff |
|---|---:|---:|---:|---:|---:|
| bronze | 0.227 | 2.917 | 0.645 | 0.001 | 2.373 |
| golden | 0.212 | 2.750 | 0.610 | 0.000 | 2.419 |
| near_golden | 0.210 | 2.806 | 0.634 | 0.001 | 2.378 |
| random | 0.162 | 3.367 | 0.632 | 0.005 | 2.233 |
| rational_approx | 0.367 | 2.500 | 0.579 | 0.072 | 2.541 |
| rational_control | 0.379 | 2.514 | 0.594 | 0.075 | 2.469 |
| silver | 0.197 | 2.750 | 0.648 | 0.002 | 2.352 |

Key question: does golden sit in a broader admissible anti-locking band rather than as a single magical winner-point?

Answer from this sweep: **golden sits in a strong anti-locking region**.
Robustness to window shape and phase: **reasonable**.
Silver vs golden tradeoff: **silver lower**.
Bronze vs golden tradeoff: **bronze lower**.

Correct success language: Golden slope did not win every metric, but may occupy the best anti-locking tradeoff region.

Strongest run: `rational_13_21` / double / drift=0.00 / window=0.20 / phase=0.00
Weakest run: `rational_13_21` / double / drift=0.00 / window=0.34 / phase=0.17

Do-not-claim: this does not prove GHP, phi as reality-code, or observer-boundary physics.