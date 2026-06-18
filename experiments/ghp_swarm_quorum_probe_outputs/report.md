# GHP Swarm Quorum Probe

Status: synthetic toy telemetry only.

This tests whether a small observer mesh can preserve a shared estimate when one observer is corrupted or drifting.

It does not prove holography, consciousness, GHP physics, or literal observer-created reality.

## Results

### SWQ-001: pass

- Metric: clean_mae; naive_corrupt_mae; quorum_mae; bad_node_reject_rate; quorum_valid_rate
- Value: 0.0328; 0.4684; 0.0373; 1.0000; 1.0000
- Null hypothesis: A quorum mesh does not beat naive all-node reconstruction when one observer drifts.
- Safest read: A verified observer mesh can reject many bad local records and preserve a better shared estimate than naive averaging over all observers.
- Falsifier: Naive all-node reconstruction matches quorum, or quorum fails to reject drifting observers.

### SWQ-002: policy

- Metric: authority_status
- Value: quorum_is_evidence_not_authority
- Null hypothesis: n/a
- Safest read: Quorum should raise confidence or write shared estimates only after receipts verify. It must not directly authorize action.
- Falsifier: Any implementation lets quorum bypass grants, revocation, or memory-boundary rules.

## Aukora Translation

```text
many node observations + verified receipts + quorum filter
  -> shared estimate
  -> confidence / memory consequence
  -> never direct authority
```

Hard rule:

```text
Quorum may increase confidence.
Quorum may write a shared estimate.
Quorum may never bypass authorization.
```

## Next Test

Run the same structure on two or more live Aukora demo nodes watching the same bounded event stream, then introduce one delayed, drifting, or adversarial node.
