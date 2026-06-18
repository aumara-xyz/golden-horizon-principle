#!/usr/bin/env python3
"""Exact-anchor rigor checks for the Golden Horizon Principle.

This script verifies narrow algebraic anchors used by the GHP papers.
It does not prove GHP, does not prove physical selection, and does not
turn bridge candidates into established physics.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import mpmath as mp


mp.mp.dps = 100

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_rigor_check_outputs"
TOL = mp.mpf("1e-80")
NEGATIVE_TOL = mp.mpf("1e-30")


@dataclass
class CheckResult:
    check_id: str
    anchor: str
    status: str
    max_error: mp.mpf
    threshold: mp.mpf
    scope: str
    note: str


def phi() -> mp.mpf:
    return (mp.mpf(1) + mp.sqrt(5)) / 2


def write_csv(rows: list[CheckResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "check_id",
                "anchor",
                "status",
                "max_error",
                "threshold",
                "scope",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "check_id": row.check_id,
                    "anchor": row.anchor,
                    "status": row.status,
                    "max_error": mp.nstr(row.max_error, 40),
                    "threshold": mp.nstr(row.threshold, 40),
                    "scope": row.scope,
                    "note": row.note,
                }
            )


def assert_pass(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def vph_001() -> CheckResult:
    """Check the Schwarzschild static-observer fixed point at r = phi r_s."""

    ph = phi()
    r_s = mp.mpf(1)
    r = ph * r_s
    normalized_radius = r / r_s
    gamma = 1 / mp.sqrt(1 - (r_s / r))
    error = abs(gamma - normalized_radius)

    # Negative control: a nearby radius must not satisfy the fixed point.
    perturb = mp.mpf("1e-20")
    x_bad = ph * (1 + perturb)
    gamma_bad = 1 / mp.sqrt(1 - 1 / x_bad)
    bad_error = abs(gamma_bad - x_bad)

    assert_pass(error <= TOL, "VPH fixed-point equality failed at phi.")
    assert_pass(
        bad_error > NEGATIVE_TOL,
        "VPH negative control failed; perturbed radius still looked fixed.",
    )

    return CheckResult(
        check_id="VPH-001",
        anchor="Viviani Phi Surface / Schwarzschild fixed point",
        status="pass",
        max_error=error,
        threshold=TOL,
        scope="Areal-radius Schwarzschild static-observer identity only; not a horizon proof.",
        note=(
            "At x=r/r_s=phi, gamma=1/sqrt(1-1/x) equals x. "
            f"Perturbed-radius negative control error was {mp.nstr(bad_error, 12)}."
        ),
    )


def mrk_001() -> CheckResult:
    """Check the Perron-Frobenius Markov kernel for Fibonacci fusion."""

    ph = phi()
    d2 = 2 + ph
    p_fib = mp.matrix(
        [
            [mp.mpf(0), mp.mpf(1)],
            [1 / (ph**2), 1 / ph],
        ]
    )

    row_errors = [
        abs((p_fib[0, 0] + p_fib[0, 1]) - 1),
        abs((p_fib[1, 0] + p_fib[1, 1]) - 1),
    ]
    pi = mp.matrix([[1 / d2, (ph**2) / d2]])
    pi_next = pi * p_fib
    stationary_errors = [abs(pi[0, idx] - pi_next[0, idx]) for idx in range(2)]
    error = max(row_errors + stationary_errors)

    # Negative control: swap the lower-row weights. It remains row-stochastic
    # but no longer preserves the Fibonacci stationary distribution.
    p_bad = mp.matrix(
        [
            [mp.mpf(0), mp.mpf(1)],
            [1 / ph, 1 / (ph**2)],
        ]
    )
    bad_pi = pi * p_bad
    bad_stationary_error = max(abs(pi[0, idx] - bad_pi[0, idx]) for idx in range(2))

    assert_pass(error <= TOL, "Fibonacci Markov kernel row/stationary check failed.")
    assert_pass(
        bad_stationary_error > NEGATIVE_TOL,
        "Markov-kernel negative control failed; wrong kernel preserved stationary vector.",
    )

    return CheckResult(
        check_id="MRK-001",
        anchor="Markovized Fibonacci fusion kernel",
        status="pass",
        max_error=error,
        threshold=TOL,
        scope="Perron-Frobenius normalized bridge kernel only; not physical selection.",
        note=(
            "Rows sum to 1 and stationary weights are proportional to (1, phi^2). "
            f"Wrong-kernel negative control drift was {mp.nstr(bad_stationary_error, 12)}."
        ),
    )


def rank2_dimension(m: int) -> mp.mpf:
    """Positive root of d^2 = 1 + m d for the rank-2 fusion-ring family."""

    mm = mp.mpf(m)
    return (mm + mp.sqrt((mm**2) + 4)) / 2


def mtc_001(max_m: int = 32) -> CheckResult:
    """Check the rank-2 categorical floor in the stated numerical subdomain.

    The code checks the rank-2 fusion-ring family x^2 = 1 + m x and includes
    the monotonic witness that d_m increases for m >= 1. The full UMTC and
    braiding-universal minimality claim rests on classification theorems cited
    in the paper, not on this finite script.
    """

    ph = phi()
    fib_d2 = 1 + ph**2

    pointed_d = rank2_dimension(0)
    pointed_d2 = 1 + pointed_d**2
    assert_pass(pointed_d == 1, "Pointed m=0 control did not have dimension 1.")
    assert_pass(pointed_d2 < fib_d2, "Pointed control should be smaller but excluded.")

    rows: list[tuple[int, mp.mpf, mp.mpf]] = []
    for m in range(1, max_m + 1):
        d = rank2_dimension(m)
        total = 1 + d**2
        rows.append((m, d, total))

    min_m, min_d, min_total = min(rows, key=lambda item: item[2])
    enumeration_error = abs(min_total - fib_d2)

    # Monotonic witness: d_m' = (1 + m/sqrt(m^2+4))/2 > 0 for m >= 1,
    # so D^2=1+d_m^2 is also increasing for all m >= 1.
    derivative_floor = min((1 + mp.mpf(m) / mp.sqrt((mp.mpf(m) ** 2) + 4)) / 2 for m in range(1, max_m + 1))

    assert_pass(min_m == 1, "Rank-2 non-pointed enumeration did not minimize at m=1.")
    assert_pass(enumeration_error <= TOL, "Rank-2 Fibonacci D^2 equality failed.")
    assert_pass(derivative_floor > 0, "Rank-2 monotonic witness failed.")

    rows_path = OUT / "rank2_family_scan.csv"
    OUT.mkdir(parents=True, exist_ok=True)
    with rows_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["m", "d", "D2", "classification"])
        writer.writeheader()
        writer.writerow(
            {
                "m": 0,
                "d": mp.nstr(pointed_d, 40),
                "D2": mp.nstr(pointed_d2, 40),
                "classification": "pointed / excluded control",
            }
        )
        for m, d, total in rows:
            writer.writerow(
                {
                    "m": m,
                    "d": mp.nstr(d, 40),
                    "D2": mp.nstr(total, 40),
                    "classification": "Fibonacci floor" if m == 1 else "larger rank-2 non-pointed family member",
                }
            )

    return CheckResult(
        check_id="MTC-001",
        anchor="Rank-2 categorical floor / Fibonacci D^2",
        status="pass",
        max_error=enumeration_error,
        threshold=TOL,
        scope=(
            "Script-level check covers the rank-2 fusion-ring family x^2=1+m x. "
            "Full UMTC and braiding-universal minimality still relies on cited classification theorems."
        ),
        note=(
            f"Minimum non-pointed checked case is m={min_m}, d={mp.nstr(min_d, 20)}, "
            f"D^2={mp.nstr(min_total, 20)}. Pointed m=0 is smaller but excluded."
        ),
    )


def write_report(results: list[CheckResult]) -> None:
    lines = [
        "# GHP Rigor Check",
        "",
        "Status: algebraic anchor validation only.",
        "",
        "These checks do not prove GHP, do not prove physical selection, do not solve the write-law, and do not upgrade bridge candidates into physics. They verify that specific mathematical anchors used by the papers are internally consistent and protected by negative controls.",
        "",
        "## Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.check_id}: {result.anchor}",
                "",
                f"- status: `{result.status}`",
                f"- max error: `{mp.nstr(result.max_error, 24)}`",
                f"- threshold: `{mp.nstr(result.threshold, 24)}`",
                f"- scope: {result.scope}",
                f"- note: {result.note}",
                "",
            ]
        )

    lines.extend(
        [
            "## Safest Reading",
            "",
            "- VPH remains a checked Schwarzschild fixed-point identity, not a technical horizon or GR derivation.",
            "- The Fibonacci Markov kernel remains a precise stochastic bridge representation, not evidence that Markov trace logic selects Fibonacci in nature.",
            "- The rank-2 scan confirms the Fibonacci floor inside the explicit script-level family; full categorical minimality remains theorem-backed by external classification results, not by this script alone.",
            "",
            "## Next Hardening Step",
            "",
            "Add this harness to a small CI-style check and keep expanding it with explicit failure controls for every exact algebraic anchor before any paper-facing upgrade.",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [vph_001(), mrk_001(), mtc_001()]
    write_csv(results, OUT / "summary.csv")
    write_report(results)
    for result in results:
        print(f"[PASS] {result.check_id}: {result.anchor}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
