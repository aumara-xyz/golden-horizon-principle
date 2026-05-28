# Golden Zipper v8 - Torus Lagged Memory

Toy telemetry only. Not physics evidence. Not proof of GHP. Not proof that phi is fundamental. Not write-law closure.

## Executive Summary

Mixed/negative: closed-surface delayed memory is interesting, but it does not beat the simpler flat ternary baseline yet.

This run compared:
- `flat_ternary`
- `torus_single_flow`
- `torus_counter_flow`
- `sphere_projected_torus`

All four used the same lagged witness-to-write rule, so the comparison is about geometry, not just scoring.

## Model Means

| Model | Mean composite | Mean hotspot stability | Mean surrogate gap |
|---|---:|---:|---:|
| flat_ternary | 0.857 | 0.450 | -0.116 |
| torus_single_flow | 0.693 | 0.362 | -0.083 |
| torus_counter_flow | 0.686 | 0.325 | -0.101 |
| sphere_projected_torus | 0.863 | 0.475 | -0.106 |

Best model by mean composite: `sphere_projected_torus`.

## Sphere/torus Read

- Top anchor under `sphere_projected_torus`: `fib_13_21` with composite `0.930`
- Golden rank under `sphere_projected_torus`: `3` / `10`
- Golden torus composite: `0.922`
- Golden hotspot stability: `0.750`
- Golden surrogate gap: `-0.035`
- Golden mean closure latency: `2.872`

## What This Supports

- Delayed witness-to-write rules fit the observer intuition better than instant closure.
- Closed-surface return geometry is worth testing directly rather than compressing everything into a flat line.

## What This Does Not Support

- does not prove GHP
- does not prove torus/sphere geometry is the correct physical model
- does not prove phi uniquely organizes memory
- does not justify hardening the paper or master

## Recommendation

Use this as a geometry diagnostic. If a torus/sphere mode becomes competitive, the next pass should tighten around its winning anchors and vary only the return geometry, not everything at once.
