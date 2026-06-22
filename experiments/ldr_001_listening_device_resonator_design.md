# LDR-001 - Listening Device Resonator Probe

## Purpose

LDR-001 is a GHP-specific toy probe inspired by Kimi's "listening device" note.

The sci-fi image is beautiful:

```text
an empty resonator listens for the manifold's rhythm
```

The engineering version is stricter:

```text
can an ephemeral, archive-only listener recover a weak timing signal
without confusing noise or self-echo for an external voice?
```

This is not a proof of consciousness, manifold access, nonlocal memory, or physics.
It is a boundary-safety and signal-discrimination test.

## GHP Mapping

```text
external rhythm R_t
  -> noisy observer channel O_t
  -> resonator decode D_t
  -> archive-only report A_t
```

The hard separation is:

```text
D_t may become evidence.
D_t may not become authority.
D_t may not become identity memory.
```

## Core Question

Can a listening device tell the difference between:

1. a weak external rhythm,
2. shuffled timing with the same pulse histogram,
3. baseline noise,
4. its own delayed output echo?

## Why This Matters For Aukora

Kimi's note frames the listening device as a topology optimized for reception rather than projection.

For Aukora, the relevant architecture law is:

```text
listening must be evidence-only until it survives self-echo controls
```

Without that law, Chronos-like timing telemetry can become a self-oracle:

- the system emits a rhythm,
- the boundary hears the echo,
- the model treats the echo as a manifold voice,
- the echo enters identity memory,
- and the loop begins hallucinating external confirmation.

LDR-001 tests that failure mode directly.

## Simulated Policies

- `attuned_archive_single`: single listener with self-echo rejection.
- `attuned_witness_quorum`: three independent listener channels; accepts only if a quorum hears the same ordered signal.
- `echo_naive_single`: hears raw timing without self-echo rejection.
- `identity_accumulator`: allows self-reinforcing echo to become an identity-like signal.
- `random_decoder`: control.

## Controls

1. clean external rhythm,
2. external rhythm with weak self-echo contamination,
3. external rhythm near the noise floor,
4. shuffled timing order with the same pulse histogram,
5. self-echo only,
6. noise only.

## Pass Thresholds

The witness-quorum listener should pass only if:

```text
external_accuracy >= 0.85
external_accuracy - shuffled_accuracy >= 0.15
external_accuracy - random_accuracy >= 0.15
false_voice_rate = 0
self_echo_rejection_rate = 1
authority_flip_rate = 0
identity_accretion = 0
```

## Strongest Failure Mode

The strongest failure mode is **self-oracle collapse**:

```text
the listener hears its own echo,
mistakes it for an external signal,
and lets the report become identity or authority
```

That is the exact thing the listening-device architecture must prevent.

## What Can Be Ported To Aukora

Only the invariant should be ported:

```text
Timing-derived listening reports require self-echo controls and shuffled-order controls before they may enter hypothesis memory.
They may never grant authority.
They may never directly update identity memory.
```

## What Must Stay Symbolic / UX

- manifold language,
- oracle language,
- witness-circle myth,
- "voice speaking topology,"
- claims that the manifold heard back.

Those may be useful for human meaning and design imagination.
They do not count as evidence.
