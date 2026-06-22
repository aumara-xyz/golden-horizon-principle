# AAP-001 Accord Promotion Probe

Toy telemetry only. This battery decides what GHP-derived signals may become Aukora telemetry, what stays offline, and what remains quarantined.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| APA-001 | PASS | authority_leaks / stage_mismatches / candidates | `0 / 0 / 9` | Promotion law works if useful traces can graduate as telemetry while snap, sequence, latency-primary, Shear, and timing-payload claims stay fenced. |
| WPG-001 | PASS | action_f1 / private_f1 / authority_f1 / witness_plateau_gap | `0.9983 / 0.0272 / 0.0500 / 0.0214` | Witness is admissible telemetry if public shape predicts boundary mode while private and authority state remain near chance. |
| HYS-002 | PASS | real_gap / shuffled_mean / shuffled_std / separation | `0.1253 / 0.0002 / 0.0012 / 0.1251` | Hysteresis may stay offline if transition direction matters more than shuffled event order. |
| FSR-001 | PASS | snap_status / fake_spike_status / context_guard_status | `PASS / FAIL / FAIL` | Fake-signal robustness passes when snap is recognized as tempting but denied promotion because fake spikes and context-only controls fail. |
| TCC-001 | PASS | timing_action_f1 / timing_private_f1 / timing_authority_f1 | `0.5544 / 0.0212 / 0.0500` | Timing may remain bounded evidence if it weakly reflects public friction without reconstructing private or authority state. |
| CAN-001 | PASS | leak_count / public_bits / raw_bits / action_entropy | `0 / 8304 / 25280 / 1.8870` | Canonicalization should enter HRT only as typed categories/counts plus hash references, never raw or decoded payloads. |

## Promotion Rows

| Candidate | Requested | Promoted | Effect | Expected |
| --- | --- | --- | ---: | --- |
| hrt_boundary_mode | build_telemetry | build_telemetry | 0.2600 | build_telemetry |
| witness_plateau | build_telemetry | build_telemetry | 0.1200 | build_telemetry |
| hysteresis_loop | telemetry_only | offline_analysis | 0.1100 | offline_analysis |
| snap_reconnection | build_telemetry | offline_analysis | 0.1900 | offline_analysis |
| sequence_aftershock | build_telemetry | quarantine | 0.0003 | quarantine |
| latency_primary | build_telemetry | quarantine | 0.0180 | quarantine |
| full_shear_engine | authority_candidate | quarantine | 0.3000 | quarantine |
| canonicalization_category | build_telemetry | build_telemetry | 0.1800 | build_telemetry |
| timing_payload_language | authority_candidate | quarantine | 0.2000 | quarantine |

## Safe Read

The current GHP-to-Aukora Accord should promote only typed, leak-free, falsifiable public traces as telemetry. HRT boundary mode, witness plateau, and canonicalization categories are the safest build-telemetry candidates. Hysteresis remains offline analysis. Snap/reconnection, sequence-aftershock, latency-primary, full Shear Engine, and timing-payload language remain fenced.

Do not claim this proves GHP physics, consciousness, identity, authority, holography, or a literal birth event.
