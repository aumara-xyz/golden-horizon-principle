# ASS-001 Accord Survivor Stress Probe

Toy telemetry only. This stress test attacks the signals that survived AAP-001 before they are handed to Aukora.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| ASS-001 | PASS | min_holdout_action_f1 / max_private_f1 / max_authority_f1 | `0.7608 / 0.0538 / 0.1143` | Approved HRT fields survive promotion only if whole-regime holdouts still predict boundary mode without private/authority recovery. |
| ASS-002 | PASS | full_action / no_refusal_action / friction_action / best_single_action | `0.9983 / 0.9965 / 0.6265 / 0.8457` | The HRT signal is healthier if it is distributed across pressure shape, not secretly one refusal or timing-like field. |
| ASS-003 | PASS | hidden_only_prediction_flip_rate | `0.000000` | Hidden-only fields must not change advisory boundary-mode predictions. |
| ASS-004 | PASS | raw_timing_action_f1 / bucket_action_f1 / bucket_private_f1 / bucket_authority_f1 | `0.5544 / 0.3292 / 0.0208 / 0.0500` | Timing should be aggregated enough that it cannot become a covert authority/private channel. |
| ASS-005 | MIXED | secret_leak_count / illegal_action_count / public_bits / raw_bits / compressed | `0 / 0 / 31864 / 16288 / False` | Canonicalization telemetry is safe if exact raw secrets disappear, but per-event hash refs are overhead and should not be sold as compression on tiny payloads. |
| ASS-006 | PASS | exact_synthetic_secret_leaks_in_outputs | `0` | The lab report itself must not leak the exact secret-like tokens used by the adversarial canonicalization fixture. |

## Safe Read

If this battery is green or green-with-overhead, the next Aukora handoff can ask for HRT Accord tests with more confidence: typed boundary-mode telemetry, witness held-tension telemetry, canonicalization categories, offline hysteresis analysis, and no live authority path.

The canonicalization result is allowed to be mixed on compression: leak-free typed telemetry matters first, while per-event hash references may be larger than tiny raw fixtures. Do not market canonicalization telemetry as compression unless payload size and batching support that claim.

Do not promote snap/reconnection, sequence-aftershock, latency-primary, full Shear Engine, timing-payload language, consciousness, identity, or physics claims.
