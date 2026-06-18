# CEW-001 Aukora Handoff

Status: local lab run complete.

This is a toy write-law probe, not physics evidence.

## Bottom Line

The boundary law itself worked cleanly:

- `thresholded_projection` replayed the public trajectory exactly: `1.0000`
- shuffled projection collapsed: `0.0000`
- always-write collapsed: `0.0000`
- never-write was near-zero: `0.0008`
- private leakage count was exactly `0`
- hidden-only perturbations did not flip the legal writer

The only reason `CEW-001` stayed `watch` instead of a full pass is accounting:

- full hidden trace bits: `228840`
- full signed public receipt bits: `264576`

That means:

1. **boundary sufficiency passed**
2. **projection invariance passed**
3. **compression remains split**

The split is important: the legal write law looks good, but a full signed receipt chain carries overhead. In a follow-up audit, the minimal public write record compressed far below the hidden trace:

- minimal public record bits: `71576`
- projection-only bits: `19624`

So the clean read is:

> Projected state is sufficient to drive legal writes without hidden-state leakage, but full receipt-chain compression should be treated as a separate accounting question.

## Safe Invariant To Port

```text
Canonical writes may be triggered only by observer-visible projected state,
never by raw hidden/internal state.

Same visible projection -> same legal write decision.

Changing hidden-only fields must not change the legal writer.

Public receipts must replay the public trajectory without private-state leakage.
```

## What Not To Port

Do not port the cheat.

```text
raw_state_leak_cheat
```

It achieved perfect replay too, but it is inadmissible by design because it reads hidden/internal state.

## Recommended Aukora Next Step

Add a **projection-only shadow auditor** around the existing gate loop:

1. derive a scrubbed observer-visible projection for each proposal
2. compute a shadow legal-write prediction from that projection alone
3. log:
   - projection signature
   - shadow decision
   - actual gate verdict
   - public receipt digest
4. assert that hidden-only context changes do not alter the shadow decision
5. keep gate authority where it already lives

## Important Separation

If Aukora wants a compression metric, split it into two tracks:

1. **minimal public decision record**
2. **full signed receipt-chain overhead**

Do not fail the write-law just because the cryptographic receipt wrapper is verbose.
