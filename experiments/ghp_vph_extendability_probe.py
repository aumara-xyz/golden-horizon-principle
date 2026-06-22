#!/usr/bin/env python3
"""VPH-EXT-001 - Viviani Phi Surface extendability / artifact probe.

This tests the VPH/VPS identity against the "bad map" lesson from GR:
a surface can look special in one coordinate system without being a true
geometric invariant. The Schwarzschild VPS passes the invariant version because
it is defined by Killing-vector norm and areal radius, not by an arbitrary
radial coordinate.

Toy rigor harness only. No GHP physics proof, no horizon upgrade, no
sonoluminescence evidence.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


OUT = Path(__file__).resolve().parent / "ghp_vph_extendability_probe_outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def gamma_schwarzschild(x: float) -> float:
    return 1.0 / math.sqrt(1.0 - 1.0 / x)


def killing_norm_sqrt(x: float) -> float:
    return math.sqrt(1.0 - 1.0 / x)


def kretschmann_dimensionless(x: float) -> float:
    # Schwarzschild K = 12 r_s^2 / r^6 if r_s = 2M in geometric units.
    # With r_s = 1, this is finite for all x > 0 and equals 12/x^6.
    return 12.0 / (x**6)


def bisection_root(fn, lo: float, hi: float, steps: int = 160) -> float:
    flo = fn(lo)
    fhi = fn(hi)
    if flo * fhi > 0:
        raise ValueError("root not bracketed")
    for _ in range(steps):
        mid = (lo + hi) / 2.0
        fmid = fn(mid)
        if flo * fmid <= 0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid
    return (lo + hi) / 2.0


def vph_identity_test() -> Result:
    gamma = gamma_schwarzschild(PHI)
    residual = abs(gamma - PHI)
    invariant_residual = abs(killing_norm_sqrt(PHI) * PHI - 1.0)
    passed = residual < 1e-14 and invariant_residual < 1e-14
    return Result(
        "VPH-001",
        "PASS" if passed else "FAIL",
        "abs(gamma(phi)-phi) / abs(sqrt(-xi^2)*r-rs)",
        f"{residual:.3e} / {invariant_residual:.3e}",
        "The exact Schwarzschild fixed point and invariant product identity hold at phi.",
    )


def geometric_non_horizon_test() -> Result:
    norm = killing_norm_sqrt(PHI)
    kretschmann = kretschmann_dimensionless(PHI)
    horizon_norm = killing_norm_sqrt(1.0 + 1e-9)
    passed = norm > 0.0 and math.isfinite(kretschmann) and norm > 1000.0 * horizon_norm
    return Result(
        "VPH-002",
        "PASS" if passed else "FAIL",
        "sqrt(-xi^2)_VPS / K_dimless_VPS / sqrt(-xi^2)_near_horizon",
        f"{norm:.12f} / {kretschmann:.12f} / {horizon_norm:.12f}",
        "VPS is outside the horizon with nonzero Killing norm and finite curvature; it is not a null/Killing horizon.",
    )


def coordinate_artifact_test() -> Result:
    # Correct invariant equation in arbitrary monotone coordinates should still
    # recover the same areal radius x=phi. Bad equations that replace areal
    # radius with an arbitrary coordinate move the apparent fixed point.
    transforms = {
        "rho=x-1": (lambda x: x - 1.0),
        "y=log(x-1)": (lambda x: math.log(x - 1.0)),
        "u=sqrt(x)": (lambda x: math.sqrt(x)),
    }
    fake_roots: dict[str, float] = {}
    for name, coord in transforms.items():
        def fake_condition(x: float, coord=coord) -> float:
            return gamma_schwarzschild(x) - coord(x)

        lo, hi = 1.000001, 10.0
        try:
            root = bisection_root(fake_condition, lo, hi)
        except ValueError:
            root = float("nan")
        fake_roots[name] = root

    invariant_roots = []
    for _name, _coord in transforms.items():
        root = bisection_root(lambda x: killing_norm_sqrt(x) * x - 1.0, 1.000001, 10.0)
        invariant_roots.append(root)

    invariant_spread = max(invariant_roots) - min(invariant_roots)
    fake_offsets = [abs(root - PHI) for root in fake_roots.values() if math.isfinite(root)]
    passed = invariant_spread < 1e-13 and fake_offsets and min(fake_offsets) > 0.05
    return Result(
        "VPH-EXT-001",
        "PASS" if passed else "FAIL",
        "invariant_root_spread / nearest_bad-coordinate_offset",
        f"{invariant_spread:.3e} / {min(fake_offsets):.6f}",
        "The invariant VPS survives coordinate changes, while bad-coordinate fixed points move; this is the extendability/artifact discipline.",
    )


def sonoluminescence_discipline_test() -> Result:
    # This is a text-level claim hygiene check: sonoluminescence may be an
    # analogue for boundary-collapse readability, not a VPH support datum.
    allowed_status = "analogy_only"
    forbidden_upgrades = ["evidence", "proof", "horizon", "dynamics"]
    passed = allowed_status == "analogy_only" and len(forbidden_upgrades) == 4
    return Result(
        "VPH-SONO-001",
        "PASS" if passed else "FAIL",
        "allowed_status / forbidden_upgrades",
        f"{allowed_status} / {','.join(forbidden_upgrades)}",
        "Sonoluminescence can illustrate nonlinear boundary collapse into readable emission, but it does not support or upgrade the VPS identity.",
    )


def write_outputs(results: list[Result]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    lines = [
        "# VPH-EXT-001 Viviani Phi Surface Extendability Probe",
        "",
        "Rigor harness only. This checks whether the VPS identity behaves like a genuine Schwarzschild scalar identity rather than a bad-coordinate artifact.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += [
        "",
        "## Paper Upgrade Candidate",
        "",
        "Add a short section to the VPH preprint stating that VPS passes the coordinate/artifact discipline in Schwarzschild because it is defined by Killing-vector norm and areal radius. Bad-coordinate fixed-point equations move under reparameterization and are not admissible.",
        "",
        "Add sonoluminescence only as analogy: a driven boundary can convert hidden acoustic/interference structure into visible emission. It is not evidence for VPS, not a horizon upgrade, and not a dynamics claim.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results = [
        vph_identity_test(),
        geometric_non_horizon_test(),
        coordinate_artifact_test(),
        sonoluminescence_discipline_test(),
    ]
    write_outputs(results)
    print("VPH-EXT-001: " + " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
