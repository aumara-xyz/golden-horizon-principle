# Golden Zipper Sturmian Memory Toy Report

Toy telemetry only. Not physics evidence.

## Summary

This toy samples irrational rotations through finite observer windows and treats the resulting binary trail as a candidate memory record. The main comparison is whether the golden slope behaves more like a balanced, non-phase-locked, low-pollution symbolic trail than nearby rational, random, silver, and bronze controls.

## Setup

- Rotation rule: `x_(n+1) = (x_n + alpha) mod 1`
- Observer windows: single interval, slowly moving phase window, and two-window bidirectional variant
- Sequence length per run: 4096
- Window sizes: 0.20, 0.34, 0.47
- Window phases: 0.00, 0.17
- Slopes: golden, silver, bronze, rational approximants, rational controls, and random slopes

## Markov / Memory Policy

- `write`: high local fit plus short-range future support
- `witness`: ambiguous local fit or delayed-future support
- `release`: low-fit / low-support symbol

## Family Metric Means

| Family | Balance | Balance spread | Complexity dev. | Periodicity match | Pollution | Delayed retention | Compression |
|---|---:|---:|---:|---:|---:|---:|---:|
| bronze | 0.212 | 3.111 | 0.635 | 0.001 | 0.004 | 0.494 | 11.076 |
| golden | 0.192 | 2.667 | 0.632 | 0.000 | 0.002 | 0.778 | 10.787 |
| random | 0.176 | 3.289 | 0.625 | 0.009 | 0.004 | 0.482 | 11.252 |
| rational_approx | 0.639 | 1.750 | 0.474 | 0.191 | 0.002 | 0.296 | 18.323 |
| rational_control | 0.690 | 1.685 | 0.539 | 0.214 | 0.002 | 0.130 | 20.197 |
| silver | 0.192 | 2.556 | 0.656 | 0.000 | 0.005 | 0.556 | 10.658 |

## Required Questions

1. Does golden/Sturmian sampling produce stronger balance than controls? **No / mixed**.
2. Does golden sampling avoid phase-lock better than rational controls? **Yes**.
3. Does golden sampling produce lower pollution or better delayed-meaning retention? **pollution: mixed; delayed meaning: better**.
4. Does silver or bronze beat golden on any metric? **silver: no clear wins; bronze: balance_score, compression_score**.
5. Are results robust to window size and phase? **reasonably** within this toy sweep.
6. Does this support only symbolic intuition, or a genuine toy-model advantage? **mostly symbolic intuition / mixed telemetry**.

## Strongest And Weakest Runs

- Strongest run: `rational_13_21` / `single` / window=0.34 / phase=0.00 / score=6.997
- Weakest run: `random_1` / `single` / window=0.47 / phase=0.17 / score=1.524

## Interpretation

The toy does not test physical reality. It tests whether a finite observer window sampling a rotation can produce unusually balanced symbolic memory traces under the golden slope. The most meaningful positive outcome here is not 'phi is reality'; it is the narrower possibility that golden/Sturmian sampling gives a useful symbolic compromise between balance, non-repetition, and delayed-meaning retention.

## Do-Not-Claim Ledger

- does not prove GHP
- does not prove phi is the code of reality
- does not prove memory creates matter
- does not prove VPH
- does not prove consciousness
- does not count as physics evidence
- does not close the write-law

## Final Toy Verdict

- strongest result: `rational_13_21`
- weakest result: `random_1`
- whether golden slope beat controls: **mixed**
- whether this deserves master hardening: **maybe**