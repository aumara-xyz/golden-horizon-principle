# VPH-EXT-001 Viviani Phi Surface Extendability Probe

Rigor harness only. This checks whether the VPS identity behaves like a genuine Schwarzschild scalar identity rather than a bad-coordinate artifact.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| VPH-001 | PASS | abs(gamma(phi)-phi) / abs(sqrt(-xi^2)*r-rs) | `2.220e-16 / 2.220e-16` | The exact Schwarzschild fixed point and invariant product identity hold at phi. |
| VPH-002 | PASS | sqrt(-xi^2)_VPS / K_dimless_VPS / sqrt(-xi^2)_near_horizon | `0.618033988750 / 0.668737080010 / 0.000031622778` | VPS is outside the horizon with nonzero Killing norm and finite curvature; it is not a null/Killing horizon. |
| VPH-EXT-001 | PASS | invariant_root_spread / nearest_bad-coordinate_offset | `0.000e+00 / 0.381966` | The invariant VPS survives coordinate changes, while bad-coordinate fixed points move; this is the extendability/artifact discipline. |
| VPH-SONO-001 | PASS | allowed_status / forbidden_upgrades | `analogy_only / evidence,proof,horizon,dynamics` | Sonoluminescence can illustrate nonlinear boundary collapse into readable emission, but it does not support or upgrade the VPS identity. |

## Paper Upgrade Candidate

Add a short section to the VPH preprint stating that VPS passes the coordinate/artifact discipline in Schwarzschild because it is defined by Killing-vector norm and areal radius. Bad-coordinate fixed-point equations move under reparameterization and are not admissible.

Add sonoluminescence only as analogy: a driven boundary can convert hidden acoustic/interference structure into visible emission. It is not evidence for VPS, not a horizon upgrade, and not a dynamics claim.
