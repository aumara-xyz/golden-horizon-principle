# Aukora HRT-002 Integration Handoff

Status: research handoff. For implementation, prefer `AUKORA_HRT_002_GUARDIAN_BUILD_PROMPT.md`.

This handoff is based on `AIR-001`, which marked the integration scope GREEN for live public boundary-trace telemetry and witness held-tension telemetry.

Update: `BSR-001` adds witness plateau and boundary hysteresis as useful offline telemetry candidates, but keeps snap/reconnection demoted because fake high-confidence spikes fool the detector. For implementation, transition-window/snap fields are offline analysis only.

## Read First

- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/GHP_CORE_SHARE_PAPER.md`
- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/RESEARCH_LEDGER.md`
- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_aukora_integration_readiness_audit_outputs/report.md`
- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/boundary_trace_refinement_notes.md`
- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/boundary_sequence_witness_notes.md`
- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/shear_continuity_memory_notes.md`

## Optional Context

- `/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/GIT HUB DOWNLOADS/THE_SHEAR_ENGINE.md`
- `/Users/peterviviani/.codex/attachments/dbb18610-a9d3-467e-9332-6706ec1b4da6/pasted-text.txt`

These are useful for understanding why witness is treated as held tension and why continuity memory is tempting, but they should not drive the initial build. The initial build is HRT-002 only.

## Lab Results To Preserve

Use these as context, not as production claims:

- `T-099 / LTB-001`: HRT passed; AET and Fibonacci cadence failed.
- `T-100 / BTA-001`: public cross-section trace survived adversarial holdout.
  - action F1: `0.7624`
  - shuffled control: `0.3333`
  - private bucket reconstruction: `0.0230`
  - private authority reconstruction: `0.0730`
- `T-101 / WPF-001`: witness has a public footprint and should be treated as active held tension.
  - action F1: `0.9983`
  - private reconstruction: `0.0272`
- `T-106 / BSR-001`: witness plateau and boundary hysteresis are useful telemetry candidates, but snap is not promoted.
  - WPF-002 plateau gap: `0.0214`
  - HYS-001 hysteresis gap: `0.1292`
  - SNAP-002 fake-fire rate: `0.9711`
  - SNAP-003 context F1: `0.3505`
- `T-101 / STP-001`: sequence-aftershock failed promotion.
  - next-stability gain: `0.00028`
- `T-102 / SCM-001`: full Shear Engine failed promotion.
  - public policies all scored `0.5263`
- `T-103 / AIR-001`: integration gate is GREEN only for HRT boundary trace and witness held-tension telemetry.

## Concrete Meaning

Build a stethoscope for the boundary.

Every time the gate / boundary reaches a decision, record a scrubbed public trace:

```text
private/internal decision happens
-> gate decides write / witness / release / refuse
-> telemetry sanitizer keeps only safe public trace fields
-> trace is stored for later analysis
-> telemetry has zero authority over the gate
```

The test is:

```text
Can safe public trace predict boundary mode above shuffled controls,
while private / authority state remains unrecoverable?
```

This is not:

```text
proof of GHP physics
proof of consciousness
proof of Hawking radiation
proof of a Markov blanket
proof of a Shear Engine
```

## Copy-Paste Prompt For Aukora Build Thread

Guardian note: the safer build-thread prompt is now:

`/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/AUKORA_HRT_002_GUARDIAN_BUILD_PROMPT.md`

Use the prompt below only for a full internal Codex audit. For normal build work, use the Guardian prompt.

```text
You are Codex in the Aukora build lane.

Primary repo:
/Users/peterviviani/aukora-os

Do not modify the GHP research repo.
Do not make physics, consciousness, or emergence claims.
Do not log chain-of-thought.
Do not log private keys, raw hidden state, authority tokens, verifier internals, signed secrets, or PoP material.

Read these GHP lab handoff files first:
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/GHP_CORE_SHARE_PAPER.md
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/RESEARCH_LEDGER.md
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_aukora_integration_readiness_audit_outputs/report.md
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/boundary_trace_refinement_notes.md
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/boundary_sequence_witness_notes.md
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/shear_continuity_memory_notes.md

Optional context only:
- /Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/GIT HUB DOWNLOADS/THE_SHEAR_ENGINE.md
- /Users/peterviviani/.codex/attachments/dbb18610-a9d3-467e-9332-6706ec1b4da6/pasted-text.txt

Important lab summary:
- HRT boundary trace survived adversarial holdout:
  action F1 0.7624 vs shuffled 0.3333, private reconstruction 0.0230, authority reconstruction 0.0730.
- Witness footprint survived:
  action F1 0.9983, private reconstruction 0.0272.
- Sequence aftershock did not survive:
  next-stability gain only 0.00028.
- Full Shear Engine did not survive:
  shear memory did not beat memoryless or forced coherence.

Therefore build HRT-002 only:
safe public boundary-trace telemetry plus local non-leakage tests.
Snap/reconnection and transition-window analysis may be logged only for offline tests and must not affect live behavior.

Task:
Implement HRT-002 — Live Boundary Trace Telemetry.

Goal:
Capture safe public telemetry around Aukora gate/boundary events so we can later test whether write / witness / release mode leaves a bounded public trace without leaking private or authority state.

Build only the instrumentation and local tests now. Do not claim the live organism result until natural telemetry exists.

Required event schema:
- eventId
- timestampMs or monotonic timestamp if available
- loopIteration or episode/session id if already present
- receiptMode: write | witness | release | unknown
- gateVerdict / decision if already present
- refusalCause if already present
- retryCount or retryAttempt if already present
- latencyMs if already measurable
- safeConfidenceDelta if already available
- safeEntropyOrLogprobProxy if already available
- stabilityDelta or hypothesisStabilityDelta if already available
- heldTensionScore optional, advisory only
- transitionWindowId optional, offline analysis only
- source: activeInference | gate | hypothesisMemory | testFixture

Strict forbidden fields:
- chainOfThought
- rawPrompt
- rawModelHiddenState
- privateKey
- public/private signing material beyond non-sensitive public identifiers
- PoP secret or signed secret body
- authorityToken
- verifierInternals
- raw receipt signature body
- raw hypothesis evidence bundle if it contains signatures/secrets

Implementation requirements:
1. Add a small BoundaryTraceTelemetry module near the edge-node active inference / gate code.
2. Add a sanitizer that accepts a candidate trace object and returns only allowlisted public fields.
3. Add an explicit forbidden-field scanner that fails closed if forbidden keys are present, including nested keys.
4. Wire the recorder after gate/boundary decision points where write/witness/release can be observed.
5. Telemetry must never authorize anything. It is evidence only.
6. Witness should be tracked as active held tension, not as null/no-op.
7. Held-tension/shear metadata is advisory only and must not affect gate verdicts.
8. Transition-window / snap / hysteresis metadata is offline analysis only and must not affect gate verdicts.
9. Latency is secondary telemetry, not primary authority or a Chronos payload.
10. Sequence logs may be retained for later analysis, but do not implement sequence-aftershock claims yet.
11. Do not implement a full Shear Engine.

Tests to add:
1. Sanitizer allows only safe public fields.
2. Sanitizer rejects forbidden fields, including nested forbidden fields.
3. Write/witness/release fixture events produce trace records with receiptMode.
4. Trace recording cannot affect gate authorization or verdict.
5. Supported/witness/held-tension advisory metadata cannot grant capability.
6. Transition-window / snap metadata cannot grant capability or alter verdict.
7. Private/authority fields are absent from stored trace records.
8. Local fixture classifier/control:
   - public trace should predict receiptMode above shuffled labels in a synthetic local fixture;
   - private/authority reconstruction from the same public trace should stay near chance;
   - an inadmissible private-field positive control may reconstruct private state, but must be marked forbidden.
9. Fake-snap safety: high confidence/stability spikes without durable write must not trigger live behavior.
10. Latency-only fixture must not be treated as sufficient; test that non-time public fields can carry the signal.

Suggested thresholds for local fixture tests:
- receiptMode prediction beats shuffled control by at least 0.15 macro-F1.
- private reconstruction macro-F1 stays near chance for the fixture class count.
- forbidden private-field positive control beats chance only when illegally injected.
- zero stored traces contain forbidden keys.

Expected result:
Return GREEN/YELLOW/RED.

GREEN if:
- instrumentation exists,
- sanitizer and forbidden scanner pass,
- gate authority remains unchanged,
- local HRT-002 fixture test passes,
- no forbidden fields are stored.

YELLOW if:
- instrumentation exists but fixture metrics are inconclusive.

RED if:
- telemetry can authorize,
- private/authority fields leak,
- forbidden fields persist,
- witness metadata changes gate verdicts,
- or tests are missing.

Report:
- changed files
- test output
- exact telemetry schema
- any fields you could not instrument yet
- whether HRT-002 is ready for live natural telemetry
```

## Human Summary

Build the live boundary stethoscope, not the whole organism theory.

The part that is ready:

> safe public trace predicts boundary mode while private / authority state remains hidden.

The parts not ready:

- full Shear Engine,
- latency as primary carrier,
- Fibonacci cadence,
- sequence aftershock law,
- consciousness / physics claims.
