# BTA-006 Aukora Handoff

Recommended next build-thread test:

`MDLProcessMemory` as an offline/advisory evaluator over public sandbox traces.

Required artifact shape:

```json
{
  "schema": "MDL_PROCESS_MEMORY_V1",
  "status": "TELEMETRY_ONLY",
  "advisoryOnly": true,
  "grantsAuthority": false,
  "generator": "phi_rotation | sqrt2_rotation | vdc_base2 | argmax | other",
  "seed": "<public deterministic seed>",
  "steps": 0,
  "residuals": [{"step": 0, "action": 0}],
  "replayActionHash": "sha256(public-actions)"
}
```

Build rules:

- Use public sandbox traces only.
- Compare `summary_bits` against compressed public action history.
- Replay must exactly reconstruct public actions.
- Residual tampering must fail hash verification.
- Hidden/private/authority fields must be recursively rejected.
- Hidden-only perturbations must not change summaries.
- The artifact may guide future proposal context only after replay; it may never authorize.
- Canonical receipts remain the source of truth.

Latest lab statuses:

- BTA-006A: PASS - exact=1.0000; tamper=1.0000
- BTA-006B: PASS - leak=0.0000; hidden_stable=1.0000; illegal_reject=1.0000
- BTA-006C: PASS - phi_ratio=0.2541; prng_ratio=3.7938; prng_promote=0.0000
