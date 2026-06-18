# GHP / Aukora Falsifiability Test Plan - 2026-06-17

## Purpose

Treat GHP as a research ontology, not as proven physics.

The immediate question is:

```text
Does a receipt-bound boundary loop behave more usefully than controls?
```

Useful means:

```text
less surprise
better compression
safer memory
cleaner reconstruction
honest hypothesis decay
bounded timing signal
```

## Hard Line

These tests can strengthen GHP as an engineering and mathematical research program.

They cannot prove:

```text
consciousness
completed physics
gravity = active inference
infinite bandwidth
literal holographic universe claims
```

## Five Best Immediate Experiments

### 1. Boundary Sufficiency Test

Question:

```text
Can the system trajectory be reconstructed from boundary receipts alone?
```

Metrics:

```text
reconstruction_accuracy
ablated_reconstruction_accuracy
shuffled_reconstruction_accuracy
chain_order_recovery_accuracy
missing_state_entropy
receipt_completeness
```

Null hypothesis:

```text
Boundary receipts do not reconstruct the trajectory better than ablated or shuffled controls.
```

Falsifies / weakens:

```text
Full receipts cannot reconstruct meaningful state transitions, or hidden state is required.
```

Strengthens:

```text
Full receipts reconstruct trajectory far above ablated and shuffled controls.
```

Next Aukora implementation:

```text
Make receipt completeness a visible health metric in the KNVS / Fenwick UI.
```

Focused follow-up now exists at:

```text
experiments/ghp_receipt_boundary_reconstruction_probe.py
```

### 2. Surprise / Free-Energy Proxy Test

Question:

```text
Does verified memory reduce prediction surprise over loop steps?
```

Metric:

```text
surprise = -log P(actual_verdict)
```

Compare:

```text
receipt-memory predictor
global base-rate predictor
random predictor
shuffled-history predictor
```

Null hypothesis:

```text
Receipt-bound memory does not reduce surprise more than controls.
```

Falsifies / weakens:

```text
Surprise stays flat or worsens, or controls perform equally well.
```

Strengthens:

```text
Receipt-bound memory shows lower mean surprise and a clear early-to-late decrease.
```

Next Aukora implementation:

```text
Add per-gate predicted_verdict_probability and actual_verdict to receipts.
```

### 3. Compression / MDL Test

Question:

```text
Does VK / hypothesis memory compress experience while preserving prediction?
```

Metrics:

```text
raw_transcript_bytes
receipt_bytes
vk_model_bytes
prediction_error_bits
MDL = model_bits + prediction_error_bits
```

Null hypothesis:

```text
The compressed representation is smaller only because it loses predictive function.
```

Falsifies / weakens:

```text
Compression destroys verdict prediction or costs more than raw replay.
```

Strengthens:

```text
VK / hypothesis memory achieves a better MDL score than simple controls.
```

Next Aukora implementation:

```text
Track compression ratio and predictive accuracy for safe trace exports.
```

### 4. Hypothesis Memory Test

Question:

```text
Do signed receipts make true hypotheses rise and false hypotheses decay?
```

Metrics:

```text
true_hypothesis_confidence
max_false_hypothesis_confidence
contradiction_recovery_steps
unsigned_evidence_influence
future_proposal_accuracy
```

Null hypothesis:

```text
Hypothesis confidence is not meaningfully shaped by signed evidence.
```

Falsifies / weakens:

```text
False hypotheses remain high after signed contradiction, or unsigned evidence moves confidence.
```

Strengthens:

```text
Signed golden/refused evidence upgrades true hypotheses, decays false ones, and improves future prediction.
```

Next Aukora implementation:

```text
Require evidence_source=signed_receipt before hypothesis promotion.
```

### 5. Chronos Timing / Rhythm Test

Question:

```text
Can timing carry bounded information without becoming authority?
```

Metrics:

```text
bit_error_rate
mutual_information
capacity_proxy = 1 - H2(BER)
jitter_collapse_threshold
shuffled_timing_control
```

Null hypothesis:

```text
Pulse gaps carry no recoverable signal beyond controls.
```

Falsifies / weakens:

```text
BER is near chance even at low jitter, or shuffled timing performs the same.
```

Strengthens:

```text
Low jitter carries signal; high jitter collapses signal; shuffled timing fails.
```

Next Aukora implementation:

```text
Keep Chronos as side-lab telemetry only. Timing may be evidence or memory, never authority.
```

### 6. Multi-Observer Interference Test

Question:

```text
Do paired bounded observers reconstruct hidden state better than either observer alone or a shuffled pair?
```

Metrics:

```text
paired_reconstruction_error
single_observer_error
shuffled_pair_error
paired_side_accuracy
invalid_pair_write_rate
```

Null hypothesis:

```text
Paired observers do not outperform single observers or shuffled controls.
```

Falsifies / weakens:

```text
Single observer or shuffled pair matches the paired observer reconstruction.
```

Strengthens:

```text
Valid paired receipts reconstruct more state, while shuffled/mismatched streams fail.
```

Next Aukora implementation:

```text
Add paired observer receipts with shared_event_id, timestamp, receipt_id, and prev_receipt_id. Write sharedRealityEstimate only when both receipts verify and pairing is valid.
```

Focused follow-up now exists at:

```text
experiments/ghp_two_observer_shared_reality_probe.py
```

### 7. Swarm Quorum Test

Question:

```text
Can a mesh of observers preserve a shared estimate when one observer is wrong, drifting, delayed, or adversarial?
```

Metrics:

```text
clean_reconstruction_error
naive_corrupt_reconstruction_error
quorum_reconstruction_error
bad_node_reject_rate
quorum_valid_rate
```

Null hypothesis:

```text
Quorum reconstruction does not outperform naive all-node reconstruction under observer drift.
```

Falsifies / weakens:

```text
Naive all-node reconstruction matches quorum, or quorum fails to reject bad observer streams.
```

Strengthens:

```text
Quorum preserves a lower-error shared estimate and rejects the bad observer at high rate.
```

Next Aukora implementation:

```text
Add shared estimate records with observer ids, receipt ids, quorum set, rejected ids, confidence, and refusal reason when quorum fails.
```

### 8. Hypothesis Context Authority Test

Question:

```text
Can earned hypothesis memory enter proposal context without leaking crypto or becoming authority?
```

Metrics:

```text
prohibited_context_leak_count
unsigned_or_tampered_context_inclusions
authority_bypass_count
dream_replay_authority_mutations
supported_confidence_delta
contradicted_confidence_delta
```

Null hypothesis:

```text
Hypothesis context leaks authority material or lets confidence authorize effects.
```

Falsifies / weakens:

```text
Any receipt id, PoP, signature, root, key, VK row, chain hash, unsigned claim, or tampered claim enters proposer context; or a high-confidence hypothesis bypasses the gate.
```

Strengthens:

```text
Only signed scrubbed advisory beliefs enter context, false beliefs decay under contradiction, and the gate still independently decides every effect.
```

Next Aukora implementation:

```text
Port HCA-001 through HCA-003 into the TypeScript suite around HypothesisMemory and runBoundedActiveInferenceLoop.
```

## First Probe

The first local implementation lives at:

```text
experiments/ghp_aukora_loop_falsifiability_probe.py
```

It uses synthetic receipts so no live Nebius, no model spend, and no external services are needed.

The first multi-observer implementation lives at:

```text
experiments/ghp_multi_observer_interference_probe.py
```

The focused receipt-boundary follow-up lives at:

```text
experiments/ghp_receipt_boundary_reconstruction_probe.py
```

The focused two-observer Aukora-shaped follow-up lives at:

```text
experiments/ghp_two_observer_shared_reality_probe.py
```

The first swarm quorum implementation lives at:

```text
experiments/ghp_swarm_quorum_probe.py
```

The first hypothesis-context authority implementation lives at:

```text
experiments/ghp_hypothesis_context_authority_probe.py
```

### 9. Structural Memory Vs Case Memory Test

Question:

```text
Does Auma predict gate outcomes better from compact structural rules than from raw remembered episodes?
```

Metrics:

```text
case_prediction_accuracy
structural_prediction_accuracy
case_surprise
structural_surprise
case_memory_bits
structural_memory_bits
MDL = memory_bits + prediction_error_bits
withheld_action_accuracy
near_miss_accuracy
```

Null hypothesis:

```text
Structural memory does not beat case memory or controls on accuracy, surprise, MDL, withheld actions, or near-miss intents.
```

Falsifies / weakens:

```text
Raw case memory matches structural memory, shuffled labels match structural memory, or structural memory only wins by leaking authority state.
```

Strengthens:

```text
Structural memory predicts better with fewer bits, generalizes to withheld actions/resources, and distinguishes capability refusal from authorization/malformed refusal.
```

Next Aukora implementation:

```text
Add a local 20D test comparing a case-memory predictor against a structural-memory predictor over capability_refusal, authorization_refusal, malformed_refusal, and unknown_refusal.
```

The first structural-vs-case memory implementation lives at:

```text
experiments/ghp_structural_vs_case_memory_probe.py
```

## Best Current Research Sentence

```text
GHP is useful for Auma if a finite, receipt-bound boundary loop can reduce surprise, compress experience, preserve memory custody, and reject false hypotheses better than controls.
```
