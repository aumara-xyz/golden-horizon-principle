# VERDICT — ZETA-CUBE-NULL v1

- test_id: ZETA-CUBE-NULL-v1
- contract: experiments/ZETA_CUBE_NULL_PREREG_v1.md (SIGNED)
- data: Odlyzko zeros1 table (first 10,000 of 100,000), n=10000
- integrity check: PASS (first three ordinates match mpmath zetazero to 6 decimals)

## Scores (controls run FIRST, per contract)

| series | S1 (chi-square, df 26) | S2 (MI, bits) |
|---|---|---|
| uniform control band (2.5–97.5 pct, 200 reps) | 13.843 – 42.510 | 0.04438 – 0.05498 |
| gap-shuffled control band (2.5–97.5 pct, 200 reps) | 14.877 – 41.401 | 0.05689 – 0.06632 |
| pooled control band (kill-condition band) | 14.605 – 42.388 | 0.04487 – 0.06589 |
| primes scaled (deterministic control) | 13.760 | 0.59926 |
| **real zeros** | **23.847** | **0.06355** |

## Kill condition (applied mechanically)

- S1 within pooled band: True
- S2 within pooled band: True
- Rule: NULL iff both S1 and S2 fall within the pooled 2.5-97.5 percentile band of the 400 stochastic control replicates.

## Verdict: **NULL**

The contract's stated prediction was NULL. That prediction held: the base-3 digit mapping of the zero ordinates is statistically indistinguishable from the controls. A NULL confirms known equidistribution and closes the digit-cube door with a receipt.

## Fence (verbatim from the SIGNED contract)

Under no outcome does this test bear on the Riemann Hypothesis, GHP, φ, or the 27-cell frame's symbolic uses.
