# Boundary Trace Refinement Notes

Status: toy telemetry only.

These probes refine the HRT line before any live Aukora handoff.

## BTR-001

File: `ghp_boundary_trace_refinement_probe.py`

Probes:

- `MCT-001` Minimal Cross-Section Trace
- `MBT-001` Markov Blanket Conditional Independence
- `WNT-001` Witness Null Trace
- `LAT-001` Latency Carrier Ablation

Result:

- `MCT-001`: pass. A very small public trace can predict boundary mode while private reconstruction remains near chance.
- `MBT-001`: pass. Full public telemetry predicts action above shuffled control while private bucket / private authority reconstruction stays low, and an inadmissible private-field positive control works.
- `WNT-001`: fail. Witness is not yet validated as a clean null-friction state.
- `LAT-001`: fail. Latency is not the primary carrier in this proxy because non-time telemetry performs just as well.

The first pass was too clean because single fields such as `entropy_delta` nearly encoded the action. That required adversarial follow-up.

## BTA-001

File: `ghp_boundary_trace_adversarial_probe.py`

Question: does the public boundary trace survive regime holdout and an intentionally inverted/noisy entropy mapping?

Result:

- `BTA-001`: pass. The cross-section trace reaches action F1 `0.7624` versus shuffled `0.3333`, while private bucket F1 is `0.0230` and private authority F1 is `0.0730`.
- `LAT-001R`: fail. Latency-only F1 is `0.5206`, but the full model does not benefit from entropy/latency in the required way; latency should not be treated as the primary carrier yet.

## Current Handoff Shape

The strongest next live Aukora test is:

> public cross-section trace predicts boundary mode, while private / authority state remains unrecoverable.

Use a multi-field public cross-section rather than a single shortcut:

- refusal cause,
- confidence delta,
- entropy or logprob proxy if safe,
- stability delta,
- retry count / latency as secondary features.

Do not assume:

- witness is a null trace,
- latency is the carrier frequency,
- Fibonacci cadence is present,
- the result proves EWCS, split property, Markov blankets, Hawking radiation, consciousness, or GHP physics.
