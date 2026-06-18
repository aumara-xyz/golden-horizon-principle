# GHP Receipt Boundary Reconstruction Probe

Status: synthetic toy telemetry only.

This isolates the receipt question: can a signed boundary record replay the public trajectory without exposing private payload text?

It does not prove holography, consciousness, or GHP physics.

## Results

### RBR-001: pass / chain recovers order

- Metric: ordered_digest_acc; chain_shuffled_digest_acc; naive_shuffled_digest_acc; ordered_completeness; chain_shuffled_completeness; naive_shuffled_completeness
- Value: 1.0000; 1.0000; 0.0000; 1.0000; 1.0000; 1.0000
- Null hypothesis: Boundary receipts do not carry enough linked information to reconstruct public trajectory or recover order from the chain.
- Safest read: The signed receipt chain is sufficient to replay the public trajectory and recover order even when transport order is scrambled. Presented order alone is not enough.
- Falsifier: Chain-aware replay fails to recover exact public digests, or naive shuffled replay matches chain-aware replay.

### RBR-002: pass / controls break replay

- Metric: ablated_digest_acc; tampered_digest_acc; dropped_digest_acc; tampered_completeness; dropped_completeness
- Value: 0.0000; 0.0125; 0.0141; 0.0125; 0.0141
- Null hypothesis: Effect tokens and intact chain links are not needed; reconstruction survives just as well after ablation, tampering, or missing receipts.
- Safest read: Replay depends on intact effect tokens and chain links. Once those are degraded, the public trajectory stops being reconstructible.
- Falsifier: Ablated, tampered, or dropped controls reconstruct just as well as the intact chain.

### RBR-003: pass / public-private split

- Metric: plaintext_payload_count; plaintext_leak_chars
- Value: 72; 0
- Null hypothesis: Public boundary receipts must expose private payload content in order to reconstruct public state.
- Safest read: Public replay can succeed with opaque effect tokens and state digests while raw private payload text stays outside the receipt schema.
- Falsifier: Receipt fields expose plaintext payloads or reconstruction requires plaintext content rather than opaque public tokens.

## Aukora Translation

```text
receipt_id + prev_receipt_id + effect token + state digest
  -> replayable public trajectory
```

Hard rule:

```text
Receipts may reconstruct the public trajectory.
Receipts may not expose private payload text by default.
Broken links, missing receipts, or ablated effect tokens should break replay.
```

## Suggested Live Port

- Add a local receipt-replay test that recomputes a public trace digest from signed receipts only.
- Verify replay still succeeds after transport reordering if chain links are intact.
- Verify replay fails closed under missing links, tampered effect tokens, or dropped receipts.
