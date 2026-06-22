# Boundary Snap / Reconnection Notes

Status: toy telemetry only.

`ghp_boundary_snap_reconnection_probe.py` follows the post-BTA directive to stop treating sequence effects as a naive linear aftershock and instead test a local "snap" or reconnection shape around Write events.

## Results

- `WPF-002`: pass. Witness keeps the held-tension interpretation. It shows a low-amplitude plateau between Write spike and Release scatter.
- `SNAP-001`: pass in the easy detector. A before/center/after feature package predicts strict Write snap with F1 `0.8442`.
- `SNAP-002`: fail. Fake high-confidence spikes fool the detector with fake-fire rate `0.9711`.
- `SNAP-003`: fail. A context-only guard loses too much signal (`context_f1 0.3505`), so the snap shape is still center-spike dependent.
- `HYS-001`: pass. The toy shows hysteresis/friction around held tension (`hysteresis_gap 0.1292`).

## Current Read

The safe update is:

> Witness plateau and boundary hysteresis look worth carrying into live telemetry. Snap/reconnection is promising language, but not yet a promoted invariant.

The fake-snap failure matters. It says the current synthetic detector can confuse "big confidence movement" with "durable write transition." That is exactly the trap live HRT-002 must avoid.

## Handoff Discipline

For live Aukora:

- keep witness held-tension fields;
- keep transition-window telemetry for later offline analysis;
- log enough before/center/after context to retest snap honestly;
- do not use snap detection in any gate, retry, acceleration, or authorization path;
- do not claim write snap until fake-spike and context-guard controls pass on live fixture data.

Do not claim this proves GHP physics, consciousness, Markov blankets, plasma reconnection, Hawking radiation, or thermodynamics.
