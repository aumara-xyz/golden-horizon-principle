# Golden Zipper v6 - Observer Ternary Zipper Shear

Toy telemetry only. Conservative by design. Not evidence for physics, consciousness, or write-law closure.

## Setup

The observer is modeled as a ternary zipper boundary on a circle-like phase line with states `-1, 0, +1`.
Two flow families are used:
- `counter_double`: one positive band and one counter-moving negative band
- `counter_triple`: the same counter-flow plus a second offset pair to mimic a multi-band torus slice

Anchors compared: golden, silver, bronze, bounded_probe, and one deterministic random bounded-CF control.

## Metrics

- shear hotspot stability: how tightly best offsets cluster across observer conditions
- phase-lock resistance: `1 - phase_lock_score`, so higher is less periodic lock-in
- delayed retention: witness-like uncertain states later resolved instead of dropped
- pollution: fraction of writes contradicted by short-horizon future resolution
- rigidity-after-zipping: similarity after a small shadow perturbation

## Verdict

**D-leaning: toy zipper shear does not keep a durable golden hotspot.**

## Anchor Summary

| Anchor | Global hotspot | Stability | Perturbed stability | Phase-lock resistance | Delayed retention | Pollution | Rigidity |
|---|---:|---:|---:|---:|---:|---:|---:|
| golden | 0.0060 | 0.250 | 0.229 | 0.763 | 0.845 | 0.018 | 0.963 |
| silver | 0.0240 | 0.250 | 0.250 | 0.752 | 0.857 | 0.035 | 0.963 |
| bronze | 0.0060 | 0.625 | 0.625 | 0.755 | 0.907 | 0.039 | 0.964 |
| bounded_probe | -0.0510 | 0.750 | 0.719 | 0.756 | 0.877 | 0.043 | 0.962 |
| random_bad_cf | 0.0360 | 0.500 | 0.500 | 0.731 | 0.891 | 0.033 | 0.961 |

## Reading

This is a stress toy for symbolic behavior under ternary observer zipping. The numbers only say whether some anchors keep a reasonably stable local offset preference under these small observer distortions.

Strongest anchor in this toy: `bounded_probe` with stability `0.750` and mean hotspot score `0.858`.
Weakest anchor in this toy: `silver` with stability `0.250` and mean hotspot score `0.854`.

## Golden-Specific Note

- Golden global hotspot offset: `0.0060`
- Golden hotspot stability: `0.250`
- Golden perturbed stability: `0.229`
- Golden pollution: `0.018`

## Do-Not-Claim Ledger

- does not prove GHP
- does not prove any anchor is fundamental
- does not justify changing shared theory documents
- does not count as physics evidence
- does not establish observer realism