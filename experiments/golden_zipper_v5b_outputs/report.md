# Golden Zipper v5b - Single-Mechanism Ablation

Toy telemetry only. Not physics evidence. Not proof of GHP. Not a claim of unique phi recovery.

## Setup

This run starts from exact anchors (`golden`, `silver`, `bronze`, `bounded_probe`) and turns on exactly one perturbation mechanism at a time.

Mechanisms scanned:
- `phase_lag` only
- `window_drift` only
- `delay` only
- `noise` only
- `rational_cutoff` only

Direct near-best band definition: offsets whose direct-scan mean tradeoff stays within `0.010` of the condition-wise direct best.

A derived run counts as a band match when its nearest direct-scan effective offset lands inside that band.

## Conservative Read

This is a mapping test, not a uniqueness test. A high band-match fraction only says a given one-knob perturbation can often imitate a direct near-best offset under this toy scorer.

## Mechanism Summary

| Mechanism | Variant | Band-match fraction | Mean effective offset | Mean tradeoff gap |
|---|---|---:|---:|---:|
| phase_lag | small | 0.000 | 0.0000 | -0.097 |
| phase_lag | big | 0.000 | 0.0000 | -0.094 |
| window_drift | small | 0.000 | -0.0040 | -0.113 |
| window_drift | big | 0.000 | 0.0093 | -0.095 |
| delay | small | 0.000 | -0.0060 | -0.094 |
| delay | big | 0.000 | 0.0233 | -0.090 |
| noise | small | 0.000 | 0.0000 | -0.094 |
| noise | big | 0.000 | 0.0000 | -0.090 |
| rational_cutoff | q34 | 0.000 | 0.0135 | -0.175 |
| rational_cutoff | q55 | 0.000 | 0.0123 | -0.129 |

## Stronger Anchor-Mechanism Matches

| Anchor | Mechanism | Variant | Band-match fraction | Mean effective offset | Mean match distance |
|---|---|---|---:|---:|---:|
| silver | window_drift | big | 0.000 | 0.0227 | 0.413 |
| silver | noise | big | 0.000 | 0.0000 | 0.005 |
| silver | noise | small | 0.000 | 0.0000 | 0.001 |
| silver | delay | big | 0.000 | 0.0467 | 0.417 |
| silver | delay | small | 0.000 | -0.0240 | 0.418 |

## Weaker Anchor-Mechanism Matches

| Anchor | Mechanism | Variant | Band-match fraction | Mean effective offset | Mean match distance |
|---|---|---|---:|---:|---:|
| bounded_probe | rational_cutoff | q55 | 0.000 | 0.0200 | 0.431 |
| golden | rational_cutoff | q55 | 0.000 | 0.0413 | 0.420 |
| golden | window_drift | big | 0.000 | -0.0280 | 0.418 |
| silver | delay | small | 0.000 | -0.0240 | 0.418 |
| silver | rational_cutoff | q34 | 0.000 | 0.0207 | 0.417 |

## Best / Worst Derived Runs

- Best derived tradeoff: `silver` / `noise` / `big` / capacity `50` / effective offset `0.0000` / tradeoff `0.621`
- Weakest derived tradeoff: `bounded_probe` / `rational_cutoff` / `q34` / capacity `400` / effective offset `-0.0160` / tradeoff `0.248`

## Do-Not-Claim Ledger

- does not prove GHP
- does not prove phi is uniquely rescued by a single perturbation mechanism
- does not show that any mechanism is physically real
- does not justify changing the core paper
- does not show uniqueness against a broader control family