# BTA-006 MDL Process Memory Promotion Guard

Toy telemetry only. This checks whether `generator + residuals` can be a safe advisory memory artifact.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| BTA-006A | PASS | exact replay / tamper detection | `exact=1.0000; tamper=1.0000` | A compact memory artifact must replay public actions exactly and detect residual tampering by hash mismatch. |
| BTA-006B | PASS | leak / hidden perturbation / illegal-positive rejection | `leak=0.0000; hidden_stable=1.0000; illegal_reject=1.0000` | MDL memory must be built from public action traces only; hidden/private/authority fields must neither leak nor alter the summary. |
| BTA-006C | PASS | promotion selectivity | `phi_ratio=0.2541; prng_ratio=3.7938; prng_promote=0.0000` | Only compact rule-shaped traces should become advisory candidates; random traces must remain fenced. |

## Source Summary

| Source | Generator Mode | Summary / Action History | Mismatch | Replay | Leak | Hidden Stable | Tamper | Illegal Reject | Promotable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phi_rotation | phi_rotation | 0.2541 | 0.0000 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| sqrt2_rotation | sqrt2_rotation | 0.3085 | 0.0000 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| argmax | argmax | 0.7315 | 0.0166 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| human_jitter | argmax | 1.2891 | 0.1176 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| prng | argmax | 3.7938 | 0.6575 | 1.0 | 0.0 | 1.0 | 1.0 | 1.0 | 0.0 |

## Safe Read

This is the strongest handoff discipline for the current compression lane: compact summaries may guide memory only if they replay exactly, keep residuals explicit, reject authority-shaped fields, and remain unchanged under hidden-only perturbations.

The artifact is never a receipt replacement. Canonical receipts remain the source of truth.
