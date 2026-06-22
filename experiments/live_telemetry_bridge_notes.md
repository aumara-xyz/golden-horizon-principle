# Live Telemetry Bridge Notes

Status: toy telemetry only.

`ghp_live_telemetry_bridge_probe.py` is a GHP-lab proxy for the next live Aukora telemetry handoff. It does not touch `aukora-os`.

## LTB-001 Results

The battery contains three probe shapes:

- `AET-001` Epistemic Shockwave Telemetry
- `HRT-001` Horizon Radiation Trace
- `FBC-001` Fibonacci Cadence Window

Current run:

- `AET-001`: fail. Write entropy drop is too weak in this proxy, although release retry cost appears clearly.
- `HRT-001`: pass. Public telemetry carries an exterior event trace while private state remains unrecoverable unless an inadmissible private field is supplied.
- `FBC-001`: fail. Fibonacci cadence windows do not beat linear windows in this proxy.

## Hawking Analogy Discipline

Hawking radiation is useful here only as a horizon analogy:

> a private boundary event should not leak private state, but it may leave a bounded public trace.

This is not evidence that Aukora has Hawking radiation, that GHP physics is proven, or that software telemetry proves consciousness.

## Strongest Handoff

The first live Aukora test should be `HRT-002`, not the full shockwave story.

Core invariant:

> Hidden/internal boundary events may leave public telemetry traces, but public traces must not reconstruct private state, keys, raw hidden memory, or authority material.

Live telemetry fields should be safe public proxies:

- receipt mode,
- gate verdict,
- refusal cause,
- retry count,
- latency,
- safe confidence delta,
- safe entropy/logprob proxy if available,
- hypothesis stability score.

Forbidden:

- chain-of-thought,
- private keys,
- raw hidden state,
- authority tokens,
- raw verifier internals.

## Current Read

The write-law path got narrower again:

- keep `write/witness/release` as the ternary boundary grammar,
- promote `HRT` as the cleanest live test,
- keep `AET` as secondary until live entropy proxies exist,
- keep `FBC` as exploratory until real telemetry beats linear and power-of-two windows.
