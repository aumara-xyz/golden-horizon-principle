# GHP Trapped-Light / Boundary-Localization Probe

## Status

This is an engineering analogy probe, not physics evidence. It tests whether the
`trapped light` / vortex intuition and the sonoluminescence boundary-collapse
analogy produce useful Aukora-facing test shapes.

## Results

| Probe | Metric | Test | Control | Verdict |
|---|---:|---:|---:|---|
| CBT-001 | threshold_event_f1 | 0.9669 | 0.1060 | PASS |
| IRF-001 | mode_footprint_accuracy | 0.9963 | 0.3741 | PASS |
| LEI-001 | closed_loop_inertia_advantage | 0.9501 | 0.1118 | PASS |
| MDL-LOC-001 | structured_mdl_ratio_lower_is_better | 0.7031 | 5.7321 | PASS |
| VTR-001 | circulation_persistence_score | 0.9499 | 0.0329 | PASS |

Pass count: **5/5**.

## Interpretation

- A nonlinear boundary threshold can turn diffuse drive into discrete write-like events.
- Write, Witness, and Release can be modeled as separable public footprints: spike, plateau, scatter.
- Closed self-referential loops persist under perturbation better than open trajectories.
- MDL process memory is useful only for structured/localized traces; random traces resist compression.
- Closed circulation can be detected as an object-like signature, which is a useful metaphor for receipt formation.

## What This Strengthens

This strengthens the engineering direction, not the physics claim:

```text
hidden pressure / vibration -> boundary event -> public trace -> replayable memory
```

The strongest Aukora transfer is still:

```text
Canonical receipts remain truth.
Boundary telemetry may describe write/witness/release mode.
MDL summaries may compress public traces only after exact replay.
Telemetry, timing, vortices, loops, and phi samplers may never authorize.
```

## Next Tests

1. Port IRF-001 shape tests to real HRT sandbox traces.
2. Test whether Witness plateaus in live traces remain separable after adversarial noise.
3. Run MDL-LOC-001 on real receipt/HRT event windows instead of synthetic traces.
4. Keep vortex/circulation as an offline diagnostic only; do not promote it into runtime control.
