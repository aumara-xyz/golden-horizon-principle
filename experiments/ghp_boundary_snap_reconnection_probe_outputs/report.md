# BSR-001 Boundary Snap / Reconnection Probe

Toy telemetry only. This tests whether Write has a local snap signature rather than a naive linear aftershock.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| WPF-002 | PASS | plateau_gap / witness_retry / release_retry / witness_stability / write_stability | `0.0214 / 0.3158 / 0.6125 / 0.0140 / 0.0672` | Witness promotes only if it looks like a low-amplitude held-tension plateau between Write spike and Release scatter. |
| SNAP-001 | PASS | snap_f1 / precision / false_positive_rate / threshold | `0.8442 / 0.7495 / 0.0473 / 0.4176` | Write snap promotes only if a local before/after reconnection signature predicts durable Write better than generic event turbulence. |
| SNAP-002 | FAIL | fake_fire_rate / spike_only_fake_fire / fake_f1 | `0.9711 / 0.9999 / 0.2248` | A snap detector is useful only if fake high-confidence spikes do not fool it. |
| SNAP-003 | FAIL | context_f1 / context_precision / context_false_positive_rate / fake_fire_rate | `0.3505 / 0.2428 / 0.2878 / 0.2878` | Snap only promotes if surrounding relaxation context carries enough signal without center-spike dependence. |
| HYS-001 | PASS | witness_to_write_signal / release_to_write_signal / write_to_witness_signal / hysteresis_gap | `0.1570 / 0.1568 / 0.0278 / 0.1292` | Boundary hysteresis promotes only if moving out of held tension into Write requires stronger public signal than falling back from Write into Witness. |

## Strongest Safe Read

If SNAP-001 and SNAP-002 both pass, the next Aukora lab question is not linear `event N -> event N+1` aftershock. It is local boundary reconnection: a before/center/after telemetry shape around Write.

If SNAP-002 fails, the detector is only seeing generic confidence excitement and must not be promoted.

Do not claim this proves GHP physics, consciousness, Markov blankets, plasma reconnection, Hawking radiation, or literal thermodynamics.
