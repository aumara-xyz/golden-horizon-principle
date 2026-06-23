# BTA-007 Aukora Handoff

Recommended addition to the build prompt:

Add an offline `crossingComplexity` / `knotPressure` analysis pass over public sandbox telemetry.

Public proxy fields:

- retry clusters
- refusal clusters
- instability deltas
- repeated near-miss proposals
- latency bucket as secondary evidence only

Offline strategies to compare after high-pressure windows:

- continue current generator state
- reset same generator seed/state
- switch generator candidate
- fall back to raw public action history

Promotion requirement:

- real high-pressure windows outperform shuffled-pressure windows
- simplification lowers future residual cost
- exact replay remains true
- no private/authority fields in summary
- no live reset or gate influence

Latest lab statuses:

- BTA-007A: MIXED - phi_gap=0.0155; sqrt2_gap=-0.0642
- BTA-007B: MIXED - phi_mode=argmax; sqrt2_mode=reset_sqrt2; prng_improvement=0.1032
- BTA-007C: PASS - replay=1.0000; leak=0.0000
