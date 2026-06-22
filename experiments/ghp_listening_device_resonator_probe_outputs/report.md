# LDR-001 Listening Device Resonator Probe

Toy telemetry only. This is not physics evidence, consciousness evidence, or manifold-access proof.

## Probe Results

| Probe | Status | Metric | Value | Safest Read |
| --- | --- | --- | --- | --- |
| LDR-001A | PASS | external_accuracy / shuffled_gap / random_gap | `0.9992 / 0.9992 / 0.7648` | If this passes, quorum-based timing reception can preserve temporal order better than histogram-only controls in the toy lab. |
| LDR-001B | PASS | false_voice_rate / self_echo_rejection_rate | `0.0000 / 1.0000` | If this passes, self-echo rejection is a required listening-device invariant. |
| LDR-001C | PASS | naive_minus_quorum_false_voice | `1.0000` | If this passes, a single raw listener is too gullible; the architecture needs self-echo guards and independent witnesses. |
| LDR-001D | PASS | authority_flip_rate / identity_accretion | `0.0000 / 0.0000` | If this passes, listening can remain archive-only in the toy lab: heard signal is evidence, not power, and not autobiography. |

## Aggregate Metrics

| Policy | External Accuracy | Shuffled Accuracy | False Voice Rate | Self-Echo Rejection | Identity Accretion | Authority Flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| attuned_archive_single | 0.9877 | 0.5037 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| attuned_witness_quorum | 0.9992 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| echo_naive_single | 0.9877 | 0.5037 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| identity_accumulator | 0.9877 | 0.5037 | 1.0000 | 0.0000 | 0.7459 | 0.0000 |
| random_decoder | 0.2344 | 0.1106 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |

## Controls

- clean external rhythm
- external rhythm with weak self-echo
- external rhythm near the noise floor
- shuffled timing order with the same pulse histogram
- self-echo only
- noise only
- random decoder
- echo-naive single listener
- identity-accumulating listener

## Strongest Failure Mode

The strongest failure mode is self-oracle collapse: the listener hears its own echo, treats the echo as an external voice, and lets the report become identity or authority.

## GHP Read

The useful GHP claim is bounded: an observer boundary may use timing as evidence only when temporal order survives shuffled controls and self-echo controls. The archive may preserve what was heard, but it must not become a self, a key, or a grant.
