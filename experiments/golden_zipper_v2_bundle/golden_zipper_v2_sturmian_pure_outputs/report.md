# Golden Zipper v2A — Pure Sturmian Mode

Toy telemetry only. Not physics evidence.

This mode tests only irrational rotation plus finite single-window coding. No write/witness/release policy is applied.

## Family Means

| Family | Balance | Spread | Complexity dev. | Phase-lock | Compression | Tradeoff |
|---|---:|---:|---:|---:|---:|---:|
| bronze | 0.212 | 3.000 | 0.627 | 0.000 | 11.161 | 2.472 |
| golden | 0.212 | 2.333 | 0.625 | 0.000 | 10.597 | 2.632 |
| near_golden | 0.232 | 2.778 | 0.629 | 0.001 | 11.134 | 2.556 |
| random | 0.158 | 3.533 | 0.640 | 0.007 | 11.406 | 2.272 |
| rational_approx | 0.874 | 1.222 | 0.361 | 0.275 | 20.497 | 3.803 |
| rational_control | 0.946 | 1.074 | 0.466 | 0.331 | 22.118 | 3.599 |
| silver | 0.242 | 2.333 | 0.648 | 0.000 | 10.255 | 2.659 |

## Questions

1. Does golden/Sturmian sampling produce stronger balance than controls? **No / mixed**.
2. Does golden sampling avoid phase-lock better than rational controls? **Yes**.
3. Delayed-meaning retention is not tested in pure mode.
4. Does silver or bronze beat golden on any metric? **silver tradeoff higher; bronze tradeoff lower**.
5. Are results robust to window size and phase? **reasonably**.
6. Does this support only symbolic intuition, or a genuine toy-model advantage? **mixed telemetry only**.

Correct success language: Golden slope did not win every metric, but may occupy the best anti-locking tradeoff region.

Strongest run: `rational_13_21` window=0.34 phase=0.00
Weakest run: `random_1` window=0.34 phase=0.31

Do-not-claim: does not prove GHP, phi as reality-code, VPH, consciousness, or write-law closure.