# Aukora HRT-002 Guardian Build Prompt

Status: sanitized build-thread prompt.

This supersedes the longer research handoff for implementation purposes. The build thread should receive this prompt, not the full GHP / Shear / continuity research trail.

## Copy-Paste Prompt

```text
You are Codex in the Aukora build lane.

Primary repo:
/Users/peterviviani/aukora-os

Task:
Implement HRT-002 — Live Boundary Trace Telemetry.

Classification:
TELEMETRY_ONLY. Evidence never authority.

Purpose:
Build a boundary stethoscope: a scrubbed public trace around gate / boundary decisions that records which mode the boundary was in without exposing private state or granting power.

Important prior lab summary, for context only:
- Boundary-trace telemetry survived adversarial proxy tests:
  action F1 0.7624 vs shuffled 0.3333.
  private reconstruction 0.0230.
  authority reconstruction 0.0730.
- Witness footprint survived as active held tension:
  action F1 0.9983.
  private reconstruction 0.0272.
- Witness plateau and boundary hysteresis survived as telemetry candidates:
  WPF-002 plateau gap 0.0214.
  HYS-001 hysteresis gap 0.1292.
- Sequence aftershock did not survive:
  next-stability gain only 0.00028.
- Snap/reconnection did not survive promotion:
  SNAP-001 looked promising, but fake high-confidence spikes fooled it.
  SNAP-002 fake-fire rate 0.9711.
  SNAP-003 context guard F1 only 0.3505.
- Full Shear Engine did not survive:
  shear memory did not beat memoryless or forced coherence.

Build now:
- safe public boundary-trace telemetry;
- receiptMode labels: write | witness | release | unknown;
- sanitizer with positive allowlist;
- recursive forbidden-field scanner;
- local fixture test for mode signal vs shuffled control;
- local fixture test for private/authority non-reconstruction;
- witness held-tension telemetry as advisory write-only metadata.
- optional transition-window logging for offline snap/hysteresis retesting only.

Do not build:
- full Shear Engine;
- sequence-aftershock law;
- live snap/reconnection decision logic;
- Fibonacci cadence;
- latency-as-primary Chronos payload;
- GHP physics / Hawking / consciousness / Markov-blanket claims;
- any telemetry path that can influence gate authorization.

Strict order:
1. Fixture-first module and tests only.
2. Sanitizer allowlist.
3. Recursive forbidden-field scanner.
4. Local synthetic fixture tests.
5. Only after tests pass, wire to sandbox/read-only or sandbox-apply events.
6. Do not wire to live mutation pathways until the user explicitly asks.

Suggested placement:
- Edge-node module near active inference / gate code.
- Mirror existing fixture-first safety-test style if present, especially cockpit/source safety style tests.
- No network or IPC in the fixture test.
- Fixture output must be visibly labeled as fixture/test, not live telemetry.

Required safe event schema:
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

Forbidden fields, including nested keys:
- chainOfThought
- rawPrompt
- rawModelHiddenState
- privateKey
- signing secret
- PoP secret
- signed secret body
- authorityToken
- verifierInternals
- raw receipt signature body
- raw hypothesis evidence bundle if it contains signatures/secrets
- arbitrary meta/payload blobs that have not passed allowlist sanitization

Security conditions:
1. Recursive scanner must fail closed.
   If any forbidden key appears at any depth, drop the entire record or throw.
2. Allowlist only.
   Unknown fields do not pass through.
3. Witness held-tension score is write-only to telemetry.
   It must have no read path into gate/access-control logic.
4. Transition-window / snap / hysteresis metadata is offline-analysis only.
   It must have no read path into gate/access-control logic.
5. Telemetry cannot authorize, deny, retry, accelerate, or alter any gate decision.
6. Latency is secondary evidence only. Never authority.
7. No raw PoP material or signature body in telemetry.
8. No generic meta: any / payload: any escape hatch unless recursively scrubbed.

Tests to add:
1. Sanitizer allows only approved public fields.
2. Sanitizer rejects/drops nested forbidden fields.
3. Unknown fields are removed or fail closed.
4. Fixture write/witness/release events produce sanitized trace records.
5. Trace recording cannot affect gate verdict.
6. Held-tension metadata cannot grant capability or alter verdict.
7. Transition-window metadata cannot grant capability or alter verdict.
8. Stored traces contain zero forbidden keys.
9. Synthetic fixture classifier/control:
   - public trace predicts receiptMode above shuffled labels by at least 0.15 macro-F1;
   - private/authority reconstruction from public trace stays near chance;
   - inadmissible private-field positive control only works when illegally injected and must be marked forbidden.
10. Fake-snap safety:
   - high confidence/stability spikes without durable write must not trigger live behavior;
   - snap/reconnection labels, if present, must be offline-only and explicitly non-authoritative.
11. Latency-only fixture is insufficient or secondary; do not treat latency as the main carrier.
12. Optional temporal-channel guard:
   - rate limit, aggregate, or jitter export if telemetry emission cadence itself could leak gate timing;
   - add a test or TODO proving timing is not a covert authority or private-state channel.

Return GREEN / YELLOW / RED.

GREEN only if:
- fixture-first module exists;
- sanitizer and recursive forbidden scanner pass;
- no forbidden fields are stored;
- telemetry has no authorization path;
- witness metadata is advisory/write-only;
- transition-window/snap metadata is offline-only;
- local HRT-002 fixture test passes.

YELLOW if:
- instrumentation exists but fixture metrics are inconclusive,
- or live wiring is deferred.

RED if:
- telemetry can influence gate decisions;
- private/authority fields leak;
- scanner is blocklist-only or non-recursive;
- arbitrary meta/payload bypass exists;
- witness metadata changes verdicts;
- snap or transition-window metadata changes verdicts;
- tests are missing.

Report:
- changed files;
- exact telemetry schema;
- test output;
- whether anything is fixture-only vs wired;
- whether transition-window/snap is strictly offline;
- any fields that could not be instrumented yet;
- remaining risks before sandbox/live apply.
```

## Do Not Send To Build Thread

Do not send:

- full GHP master/paper research context;
- Shear Engine specification;
- continuity research attachment;
- physics/consciousness framing;
- iCloud research paths;
- raw experiment archives unless explicitly requested for audit.

The build lane needs the sanitized constraints and the passed/failed lab summary only.
