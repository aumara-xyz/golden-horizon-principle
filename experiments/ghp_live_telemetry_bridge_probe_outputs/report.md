# LTB-001 Live Telemetry Bridge Proxy

Toy telemetry only. This is a handoff-shaping battery for Aukora live telemetry, not evidence for GHP physics.

## Probe Results

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| AET-001 | FAIL | write_entropy_drop / witness_confidence_delta / release_retry_cost / release_entropy_cost | `0.0003 / 0.0044 / 0.5491 / 0.0020` | Write lowers public entropy, witness is comparatively stabilizing, and release carries a short-term retry/entropy cost. |
| HRT-001 | PASS | action_f1 / shuffled_f1 / private_f1 / inadmissible_private_f1 / forbidden_leak_count | `0.7816 / 0.3325 / 0.0134 / 0.8750 / 0` | Public telemetry can carry an exterior event trace while private state remains unrecoverable unless an inadmissible private field is supplied. |
| FBC-001 | FAIL | best_window_set / fib_gain_vs_next_best | `linear / -0.0000` | Fibonacci cadence windows are a useful operator shape only if they beat nearby cadence controls; this toy is not live evidence. |

## HRT Split-Trace Metrics

- public action F1: `0.7816`
- shuffled action F1: `0.3325`
- private reconstruction F1 from public trace: `0.0134`
- inadmissible private-field reconstruction F1: `0.8750`
- public trace bits: `568`
- sampled private payload bits: `456`

## FBC Window Scores

| Window Set | MAE | Feature Bits |
| --- | ---: | ---: |
| linear | 0.00497 | 536 |
| fibonacci | 0.00498 | 536 |
| wide | 0.00498 | 520 |
| random_fixed | 0.00498 | 512 |
| powers2 | 0.00498 | 512 |

## Aukora Handoff

Port the telemetry shape, not the synthetic result:

- log safe entropy proxies, confidence deltas, retry counts, refusal causes, latency, and receipt mode;
- never log chain-of-thought, private keys, raw hidden state, or authority material;
- test write/witness/release after-effects against shuffled receipts and memoryless controls;
- test public horizon traces for event signal and private-state non-recoverability;
- compare Fibonacci windows against powers-of-two, linear, and random windows on real telemetry.

Do not claim Hawking radiation, split property, Trace Logic, or Fibonacci cadence is proven by this toy battery.
