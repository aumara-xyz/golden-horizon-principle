# GHP / Aukora Loop Falsifiability Probe

Status: synthetic toy telemetry only.

This harness tests whether a receipt-bound boundary loop can reconstruct state, reduce surprise, compress experience, separate true from false hypotheses, and carry bounded timing information better than controls.

It does not prove consciousness, GHP physics, gravity, holography, or a literal birth event.

## Results

### AUK-F001: pass / privacy-bounded

- Metric: public_chain_acc; shuffled_chain_acc; private_state_reconstruction_acc; ablated_private_acc; private_shuffled_acc; missing_entropy_bits; receipt_completeness
- Value: 1.0000; 0.0000; 0.1208; 0.0000; 0.0167; 0.0000; 1.0000
- Null hypothesis: Boundary receipts do not verify public trajectory better than shuffled controls.
- Safest read: Ordered receipts verify the public trajectory, while private memory content is not reconstructable from hashes alone. This is good custody, not a failure, if the design goal is public proof plus private memory.
- Falsifier: Receipt chain verification fails or shuffled order verifies as well as the true order.

### AUK-F002: pass

- Metric: memory_mean_surprise; base_mean_surprise; improvement; memory_first_to_last_decrease
- Value: 0.2635; 0.5939; 0.3304; 0.1600
- Null hypothesis: Receipt memory does not reduce prediction surprise more than a base-rate control.
- Safest read: Conditioned receipt memory reduces verdict surprise over the loop in this synthetic gate.
- Falsifier: Memory surprise stays flat, worsens, or matches the base-rate control.

### AUK-F003: pass / structural-memory

- Metric: raw_zlib_bytes; count_memory_bytes; base_bytes; structural_rule_bytes; count_memory_mdl_bits; base_mdl_bits; structural_mdl_bits; count_to_raw_ratio
- Value: 26517; 363; 41; 63; 3177.68; 944.93; 504.00; 0.0137
- Null hypothesis: VK-style compressed memory is smaller only because it loses predictive function.
- Safest read: A count-table memory reduces surprise but is not MDL-efficient against a tiny base-rate model. A structural boundary rule is the better compression target in this synthetic gate.
- Falsifier: No compact structural memory beats the base-rate control, or compression only works by losing prediction.

### AUK-F004: pass

- Metric: true_confidence; max_false_confidence; confidence_gap; unsigned_ignored_events
- Value: 0.9985; 0.6834; 0.3151; 46
- Null hypothesis: Hypothesis confidence is not meaningfully shaped by signed evidence.
- Safest read: Signed receipts sharply separate the true boundary rule from false shortcut hypotheses.
- Falsifier: False hypotheses remain high after signed contradiction, or unsigned evidence moves confidence.

### AUK-F005: pass

- Metric: BER_low; BER_mid; BER_high; shuffled_BER; capacity_proxy_low; collapse_jitter
- Value: 0.0000; 0.0492; 0.2388; 0.4988; 1.0000; 30
- Null hypothesis: Pulse gaps carry no recoverable signal beyond shuffled timing controls.
- Safest read: Timing carries bounded local information under low jitter and collapses under high jitter; timing remains evidence, never authority.
- Falsifier: Low-jitter BER is near chance, or shuffled timing performs the same as ordered timing.

## Engineering Interpretation

The most important implementation rule is:

```text
proposal -> verdict -> consequence -> receipt -> memory consequence -> next proposal
```

The loop only becomes a useful GHP proving ground if every step is measured and controls are kept close.

## Next Live Aukora Hooks

1. Add predicted verdict probability to each gate receipt.
2. Add receipt completeness and reconstruction health to the UI.
3. Add hypothesis confidence updates that require signed receipts.
4. Add MDL-style trace compression metrics to the harvester.
5. Keep Chronos timing as side-lab telemetry only.
