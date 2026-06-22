# AIR-001 Aukora Integration Readiness Audit

Overall handoff status: **GREEN**

This audit reads the latest GHP lab outputs and decides what is ready for the Aukora build lane.

| Gate | Status | Metric | Value | Recommendation |
| --- | --- | --- | --- | --- |
| AIR-HRT | GREEN | BTA action gap / private F1 / authority F1 | `0.4291 / 0.0230 / 0.0730` | Integrate live public boundary-trace telemetry with private/authority non-reconstruction tests. |
| AIR-WITNESS | GREEN | WPF action F1 / private F1 | `0.9983 / 0.0272` | Track witness as active held-tension state in telemetry. |
| AIR-SEQUENCE | YELLOW | STP next-stability gain | `0.00028` | Do not claim sequence aftershock; log sequences for later analysis only. |
| AIR-SHEAR | RED | SCM shear gain / private F1 | `0.0000 / 0.0153` | Do not integrate a Shear Engine; keep held-tension metadata advisory only. |

## Build-Lane Scope

Build now:

- live public boundary-trace telemetry;
- write / witness / release receipt-mode labels;
- private and authority non-reconstruction tests;
- witness as active held-tension telemetry.

Do not build yet:

- latency-as-primary Chronos claims;
- Fibonacci cadence claims;
- sequence-aftershock claims;
- full Shear Engine / contradiction memory as core architecture.

Allowed exploratory metadata:

- optional held-tension / witness pressure score, advisory only;
- optional episode ID and safe memory linkage for later continuity tests.

Forbidden telemetry:

- chain-of-thought;
- private keys;
- raw hidden state;
- authority tokens;
- verifier internals;
- raw signed secrets or PoP material.
