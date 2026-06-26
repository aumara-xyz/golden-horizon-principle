# MEB-009 — E6 27 Branching Probe

## Status

This is a mathematical hardening probe, not physics evidence.

It asks whether the E6 27-weight scaffold branches into stable bookkeeping blocks under a stated complement-charge rule.

It does **not** derive SO(10), Standard Model fermions, hypercharge, anomaly cancellation, generations, masses, particles, or matter.

## Results

| Probe | Metric | Value | Control | Verdict |
|---|---:|---:|---:|---|
| MEB-009A | D5_candidate_count | 2.000000 | 2.000000 | PASS |
| MEB-009B | algorithmic_16_10_1_split | 1.000000 | 0.000000 | PASS |
| MEB-009C | naive_coordinate_control_failure | 1.000000 | 1.000000 | PASS |
| MEB-009D | random_charge_hit_rate | 0.000000 | 0.000000 | PASS |
| MEB-009E | conjugate_charge_match | 1.000000 | 1.000000 | PASS |
| MEB-009F | conjugate_node_stability | 1.000000 | 1.000000 | PASS |

Pass count: **6/6**.

## Branching Facts Recorded

- D5-like complement nodes: `[4, 5]`
- complement-charge signatures: `{'4': ((-2, 10), (1, 16), (4, 1)), '5': ((-4, 1), (-1, 16), (2, 10))}`

## Interpretation

- The E6 27 admits a clean 16 + 10 + 1 block split under an explicit inverse-Cartan complement charge.
- A naive coordinate control does not produce this split, and random charge maps rarely hit it.
- The conjugate 27-bar carries the opposite charge signature.
- This is a serious representation-bookkeeping result, but it is still not Standard Model physics.

## Next Test

MEB-010 should test whether the 16, 10, and 1 blocks have stable internal structure under the D5 Weyl action and whether any further subgroup chain can be specified without post-hoc labels.

## Do Not Claim

- Do not claim this derives SO(10) physics.
- Do not claim the 16 block is a Standard Model generation.
- Do not claim the complement charge is hypercharge.
- Do not claim this proves matter embedding.
