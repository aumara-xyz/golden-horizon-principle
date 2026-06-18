# GHP Two-Observer Shared-Reality Probe

Status: synthetic toy telemetry only.

This is the Aukora-shaped two-ear test: two signed observer streams each carry partial event information, and the paired estimate should beat either single stream while still failing closed on invalid pairings.

It does not prove that reality is literally made of observer interference.

## Results

### TSR-001: pass / paired lift

- Metric: single_a_acc; single_b_acc; paired_acc; shuffled_pair_acc; single_a_surprise; paired_surprise
- Value: 0.5577; 0.6374; 0.7088; 0.3501; 1.5219; 1.3862
- Null hypothesis: Two bounded observers do not reconstruct hidden event state better than either single observer or a shuffled pair.
- Safest read: Paired bounded observers reconstruct refusal cause and allow-state better than either observer alone, and the benefit collapses when one stream is mismatched.
- Falsifier: Single-observer or shuffled-pair accuracy matches the paired estimate, or paired surprise does not improve.

### TSR-002: pass / no invalid writes

- Metric: invalid_pair_shared_write_rate
- Value: 0.0000
- Null hypothesis: Invalid or mismatched observer pairings still produce a shared estimate.
- Safest read: Shared-reality estimates should only be written when both receipts verify and the pairing relation is valid.
- Falsifier: Mismatched or unsigned pairings still count as valid shared estimates.

### TSR-003: policy

- Metric: authority_status
- Value: shared_estimate_is_evidence_not_authority
- Null hypothesis: n/a
- Safest read: Even a high-confidence shared estimate is an evidential or mnemonic object. Authorization remains a separate gate decision.
- Falsifier: Any implementation lets observer fusion bypass the gate.

## Aukora Translation

```text
node A signed receipt + node B signed receipt + valid pairing
  -> sharedRealityEstimate
  -> optional memory / confidence consequence
```

Hard rule:

```text
Observer fusion may be evidence.
Observer fusion may be memory.
Observer fusion may never be authority.
Invalid or unsigned pairings should write nothing.
```

## Suggested Live Port

- Add paired observer receipt fields: `sharedEventId`, `observerNodeId`, `pairingSkewMs`, `sharedRealityEstimate`.
- Require both signed receipts plus event-id and skew validation before writing the shared estimate.
- Compare paired estimate accuracy against node-A-only, node-B-only, and shuffled-pair controls.
