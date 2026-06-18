# Aukora / GHP Wind-Tunnel Handoff - 2026-06-18

Copy this into the main Aukora coding chat after reading the linked reports.

```text
You are Codex working in the Aukora coding lane.

Stay local-only. No Nebius. No production overbuild. Port only the test shapes that survived the GHP wind tunnel.

Read these first:

/Users/peterviviani/AUMA-ONE-APP/docs/AUKORA_SINGULARITY_PATH.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/GHP_AUKORA_FALSIFIABILITY_TEST_PLAN_2026-06-17.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_receipt_boundary_reconstruction_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_two_observer_shared_reality_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_structural_vs_case_memory_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_hypothesis_context_authority_probe_outputs/report.md

Current safe read from the wind tunnel:

1. Receipt boundary replay survived.
   - Signed receipts plus `prevReceiptId` plus effect token plus public state digest were enough to replay the public trajectory exactly.
   - Replay still worked when transport order was scrambled, as long as chain links were intact.
   - Replay collapsed under ablated effect tokens, tampered links, or dropped receipts.
   - Public replay did not require private payload plaintext.

2. Two-observer shared reality survived in bounded form.
   - A valid paired observer estimate beat node-A-only, node-B-only, and shuffled-pair controls on hidden event-state reconstruction.
   - Invalid or mismatched pairings wrote nothing.
   - Shared estimate remains evidence/memory only, never authority.

3. Structural memory vs case memory already survived.
   - Compact structural memory beat raw case memory on withheld actions and MDL.

4. Belief-is-not-authority already survived.
   - Hypothesis context may guide proposals but never bypasses gate authority.

Your job:
Port the two newest survivors into Aukora's local test lane with minimal surface area.

Priority order:

Priority A: Receipt Boundary Replay
Priority B: Paired Observer Shared Reality

Do not weaken existing gate or hypothesis tests.

Implement or scaffold:

A. Receipt boundary replay test
- Add a focused local test that rebuilds a public trace digest from signed receipts only.
- Required fields:
  - `receiptId`
  - `prevReceiptId`
  - `timestamp`
  - `publicEffectToken` or equivalent replayable public delta token
  - `publicStateDigest`
- Add controls:
  1. intact ordered chain -> replay succeeds
  2. transport-scrambled receipts with intact links -> replay still succeeds
  3. ablated effect token -> replay fails
  4. tampered `prevReceiptId` or token -> replay fails
  5. dropped receipt -> replay completeness and digest check fail
- Hard rule:
  public replay may reconstruct trajectory
  private payload text must remain out of default public receipts

B. Paired observer shared-reality test
- Add or scaffold observer receipt fields:
  - `sharedEventId`
  - `observerNodeId`
  - `observerTimestamp`
  - `pairingSkewMs`
  - `sharedRealityEstimate`
  - `sharedRealityConfidence`
- Valid shared estimate requires:
  - both receipts signed
  - same `sharedEventId`
  - acceptable timestamp skew
- Add controls:
  1. valid pair -> paired estimate written
  2. node-A-only -> lower reconstruction accuracy
  3. node-B-only -> lower reconstruction accuracy
  4. shuffled/mismatched pair -> lower reconstruction accuracy or no write
  5. invalid/unsigned pair -> no shared estimate write
- Hard rule:
  shared reality estimate may guide memory or confidence
  shared reality estimate may never authorize effects

Suggested test names:
- `receiptReplay.test.ts`
- `pairedObserverReality.test.ts`

Suggested first minimal API shape:
- `replayPublicTraceFromReceipts(receipts) -> { digestMatches: boolean, completeness: number }`
- `buildSharedRealityEstimate(leftReceipt, rightReceipt) -> SharedRealityEstimate | null`

Report back with:
- files changed
- tests added
- test results
- any partial scaffolds
- exact next follow-up after these land

Hard laws:
- model proposes only
- gate authorizes
- receipts decide what became real
- timing may be evidence, never authority
- observer fusion may be evidence, never authority
- hypothesis context may guide, never authorize
```
