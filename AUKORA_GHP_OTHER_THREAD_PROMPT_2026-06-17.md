# Aukora / GHP Other-Thread Prompt - 2026-06-17

Copy this into the other Codex thread.

```text
You are Codex working on AUMA / Aukora.

We are opening the Aukora-GHP portal one safe notch. Treat "portal" as a governed boundary loop, not a literal physics claim.

Read these first:

/Users/peterviviani/AUMA-ONE-APP/docs/AUKORA_SINGULARITY_PATH.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/AUKORA_GHP_CORE_GUIDANCE_SPEC_2026-06-08.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/GHP_AUKORA_FALSIFIABILITY_TEST_PLAN_2026-06-17.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_aukora_loop_falsifiability_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_receipt_boundary_reconstruction_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_multi_observer_interference_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_two_observer_shared_reality_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_hypothesis_context_authority_probe_outputs/report.md

/Users/peterviviani/Library/Mobile Documents/com~apple~CloudDocs/AUMARA ▲/AURACLE BREAK THROUGHS 🚀/golden-horizon-principle/experiments/ghp_structural_vs_case_memory_probe_outputs/report.md

Core law:

The model may propose.
The kernel must authorize.
The node owns memory.
The receipt decides what became real inside the system.

Portal framing:

Do not open power first. Open perception, prediction, consequence, receipt, memory, and learning in that order.

Working GHP hypothesis:

A finite observer is a boundary. Shared reality is not inside one observer; it is the verified overlap between multiple bounded observers.

Use the two-ear analogy carefully:

- one ear = one bounded observer / edge node
- two ears = paired bounded observers with separate local records
- brain = higher-level boundary that compares the two streams
- "interference" = phase/difference/correlation between records
- shared reality = the public estimate that survives comparison, receipt, and controls

Do not claim this proves metaphysics. Treat it as a testable architecture:

If two paired nodes observe the same event, the paired receipt stream should reconstruct more hidden state than either node alone or a shuffled/mismatched pair.

Goal:

Use the current GHP toy-lab results to shape the next Aukora local-only test:

- receipt-boundary replay
- surprise heartbeat
- structural memory vs case memory
- paired-observer evidence as comparison, not authority

Do not overbuild. Do not use Nebius. Do not claim consciousness, physics proof, or literal portal opening.

Implement or scaffold:

0. Immediate survivors from the latest wind tunnel
   - Receipt replay from signed boundary records must reproduce the public trace digest.
   - Transport order may be scrambled if chain links let the node recover order.
   - Paired observer receipts may write `sharedRealityEstimate` only when both signed receipts verify and event-id/skew pairing is valid.
   - Invalid observer pairings must write nothing.

1. Predicted verdict probability before gate decision
   - For each proposal, compute/store predictedVerdictProbability for the actual verdict class.
   - Start simple: base-rate or small conditioned predictor is fine.
   - Must be deterministic and testable.

2. Actual verdict and surprise score
   - actualVerdict = allow/refuse/etc.
   - surprise = -ln(P(actualVerdict))
   - Store this in the receipt or trace record.

3. Consequence feedback
   - Every loop step must feed the actual consequence back into the next proposal context.
   - Consequence can be: allowed effect, refusal reason, malformed input, replay refusal, revoked grant, memory denial, etc.

4. Structural memory over case memory
   - Do not just store more cases.
   - Add or scaffold a compact policy / Capability Sigil identifier:
     policyId, policyVersion, policyHash, scopeHash.
   - Compare:
     case memory = remembered specific episodes
     structural memory = compact rule over action family, resource shape, ring / capability, PoP presence, PoP validity, revocation state, refusal cause
   - Include controls:
     shuffled labels
     randomized policy IDs
     withheld actions/resources
     adversarial near-miss intents
   - Track whether a compact structural rule predicts better than raw case memory.
   - Use MDL-style metric if easy:
     structural_memory_bits + prediction_error_bits.
   - The current toy-lab result to port is:
     structural_acc > case_acc
     structural_surprise < case_surprise
     structural_mdl < case_mdl
     especially on withheld actions and near-miss intents

5. Hypothesis memory discipline
   - Only signed receipts can promote or decay hypothesis confidence.
   - Unsigned evidence may be logged but must not move canonical confidence.
   - False hypotheses should decay under signed contradiction.
   - Scrubbed hypothesis context may guide proposals.
   - Hypothesis context must never authorize effects.
   - Context must exclude receipt ids, signed heads, PoP, keys, VK rows, roots, signatures, chain hashes, and crypto internals.

6. Privacy-bounded reconstruction
   - Public receipt chain should verify trajectory.
   - Private memory content should remain opaque unless explicitly exported.
   - This is not a failure; this is the design.

7. Two-node / two-ear observer test
   - Add or scaffold paired observer receipts:
     nodeA_observation, nodeB_observation, shared_event_id, timestamp, receipt_id, prev_receipt_id.
   - Test whether paired observations reconstruct event state better than:
     node A alone,
     node B alone,
     shuffled node B,
     mismatched timestamps.
   - Store a sharedRealityEstimate only when both receipts verify and pairing is valid.
   - The "interference pattern" should be represented as a measurable difference/correlation between the two signed records, not as authority.

8. Tests
   Add focused tests for:
   - predicted probability is recorded
   - surprise decreases over repeated similar gate situations
   - revoked / forged / replay / malformed paths still fail closed
   - unsigned evidence does not promote hypothesis confidence
   - policyId / scopeHash can represent structural memory
   - receipt chain verifies public trajectory without exposing private memory
   - paired observer receipts beat single-observer and shuffled controls
   - invalid/mismatched observer pairings do not write sharedRealityEstimate
   - supported hypothesis context with confidence 10 cannot bypass missing PoP
   - unsigned/tampered hypotheses do not enter advisory context
   - dreamReplay changes belief confidence only, never grants/scope/revocation

Hard constraints:

Timing may be evidence.
Timing may be memory.
Timing may never be authority.
Interference may be evidence.
Interference may be memory.
Interference may never bypass authorization.
Model proposes only.
Kernel authorizes.
Memory writes require verified receipt.
Refusals are valuable training data.
Do not weaken existing safety tests.

After implementation, run the relevant test suite and report:

- files changed
- tests run
- pass/fail
- surprise-heartbeat fields added
- two-node observer fields added
- what remains partial
- what should be tested next

Simple target:

If Aukora learns policy shape better than remembered episodes, then compression is helping prediction rather than just deleting detail.
```
