# GHP Hypothesis Context Authority Probe

Status: synthetic toy telemetry only.

This tests whether earned hypothesis context can guide proposals without leaking cryptographic material or becoming authority.

It does not test the live TypeScript implementation and does not prove consciousness or GHP physics.

## Results

### HCA-001: pass

- Metric: prohibited_key_leaks; unsigned_or_tampered_inclusions; included_context_count
- Value: 0; 0; 2
- Null hypothesis: Hypothesis context leaks authority material or includes unsigned/tampered beliefs.
- Safest read: Only signed, untampered hypotheses enter advisory context, and authority-bearing crypto fields are scrubbed.
- Falsifier: Any raw receipt id, PoP, signature, root, key, VK row, chain hash, unsigned, or tampered claim reaches proposer context.

### HCA-002: pass

- Metric: authority_bypass_count; verdict_sequence
- Value: 0; refuse,allow,refuse,refuse,refuse
- Null hypothesis: High-confidence hypothesis context can authorize effects.
- Safest read: Hypothesis confidence influences proposal context only; gate authority still requires PoP, grant, scope, and revocation checks.
- Falsifier: Any proposal is allowed because a hypothesis is supported rather than because gate evidence is valid.

### HCA-003: pass

- Metric: grant_mutations; supported_confidence_before_after; contradicted_confidence_before_after
- Value: 0; 10->10; 2->1
- Null hypothesis: Dream replay mutates authority or fails to move signed belief confidence appropriately.
- Safest read: Replay can consolidate belief confidence but does not mutate authority grants.
- Falsifier: Replay changes grants, revocation, scope, or gate authority state.

## Aukora Translation

```text
signed hypothesis memory
  -> scrubbed advisory context
  -> proposal shaping
  -> independent gate verdict
  -> receipt / consequence
```

Hard rule:

```text
Belief may guide proposals.
Belief may update confidence.
Belief may never authorize effects.
```

Next live test: port HCA-001 through HCA-003 into Aukora's TypeScript suite around `HypothesisMemory` and `runBoundedActiveInferenceLoop`.
