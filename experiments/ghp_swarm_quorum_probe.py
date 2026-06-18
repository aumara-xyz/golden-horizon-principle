#!/usr/bin/env python3
"""Synthetic swarm quorum probe for GHP/Aukora.

This extends the two-observer interference test into a small observer mesh:

- five bounded observers receive noisy distance records for the same hidden event;
- one observer is corrupted / drifting;
- naive all-node reconstruction is compared with quorum reconstruction;
- quorum must improve reconstruction and identify the bad observer often enough.

It does not prove holography, consciousness, or GHP physics. It tests a useful
architecture rule: shared estimates should come from verified overlap and quorum,
not from any single observer or unfiltered average.
"""

from __future__ import annotations

import csv
import itertools
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_swarm_quorum_probe_outputs"


@dataclass
class SwarmResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def observer_positions() -> list[tuple[float, float]]:
    radius = 4.0
    return [
        (radius * math.cos(2 * math.pi * idx / 5), radius * math.sin(2 * math.pi * idx / 5))
        for idx in range(5)
    ]


def solve_2x2(a11: float, a12: float, a22: float, b1: float, b2: float) -> tuple[float, float] | None:
    det = (a11 * a22) - (a12 * a12)
    if abs(det) < 1e-9:
        return None
    x = ((b1 * a22) - (b2 * a12)) / det
    y = ((a11 * b2) - (a12 * b1)) / det
    return x, y


def estimate_point(positions: list[tuple[float, float]], distances: list[float], subset: tuple[int, ...]) -> tuple[float, float] | None:
    ref = subset[0]
    x0, y0 = positions[ref]
    d0 = distances[ref]
    ata11 = ata12 = ata22 = atb1 = atb2 = 0.0

    for idx in subset[1:]:
        xi, yi = positions[idx]
        di = distances[idx]
        a = 2 * (xi - x0)
        b = 2 * (yi - y0)
        c = (d0 * d0) - (di * di) + (xi * xi + yi * yi) - (x0 * x0 + y0 * y0)
        ata11 += a * a
        ata12 += a * b
        ata22 += b * b
        atb1 += a * c
        atb2 += b * c

    return solve_2x2(ata11, ata12, ata22, atb1, atb2)


def residuals(positions: list[tuple[float, float]], distances: list[float], estimate: tuple[float, float]) -> list[float]:
    x, y = estimate
    return [abs(math.hypot(x - ox, y - oy) - d) for ox, oy, d in zip([p[0] for p in positions], [p[1] for p in positions], distances)]


def point_error(estimate: tuple[float, float], truth: tuple[float, float]) -> float:
    return math.hypot(estimate[0] - truth[0], estimate[1] - truth[1])


def quorum_estimate(
    positions: list[tuple[float, float]],
    distances: list[float],
    threshold: float = 0.16,
) -> tuple[tuple[float, float], list[int], int] | None:
    best: tuple[tuple[float, float], list[int], float] | None = None
    for subset in itertools.combinations(range(len(positions)), 4):
        estimate = estimate_point(positions, distances, subset)
        if estimate is None:
            continue
        res = residuals(positions, distances, estimate)
        inliers = [idx for idx, value in enumerate(res) if value <= threshold]
        median_residual = sorted(res)[len(res) // 2]
        score = (len(inliers), -median_residual)
        if best is None or score > (len(best[1]), -best[2]):
            best = (estimate, inliers, median_residual)

    if best is None:
        return None
    estimate, inliers, _ = best
    rejected = [idx for idx in range(len(positions)) if idx not in inliers]
    rejected_idx = rejected[0] if rejected else -1
    return estimate, inliers, rejected_idx


def run_probe(seed: int = 20260617, n: int = 1200) -> list[SwarmResult]:
    rng = random.Random(seed)
    positions = observer_positions()
    clean_errors: list[float] = []
    naive_corrupt_errors: list[float] = []
    quorum_errors: list[float] = []
    bad_rejections = 0
    quorum_valid = 0

    for _ in range(n):
        truth = (rng.uniform(-1.7, 1.7), rng.uniform(-1.7, 1.7))
        clean_distances = [
            math.hypot(truth[0] - ox, truth[1] - oy) + rng.gauss(0.0, 0.035)
            for ox, oy in positions
        ]
        corrupt_distances = list(clean_distances)
        bad_idx = rng.randrange(len(positions))
        corrupt_distances[bad_idx] += rng.choice([-1.0, 1.0]) * rng.uniform(0.75, 1.4)

        clean_estimate = estimate_point(positions, clean_distances, tuple(range(len(positions))))
        naive_estimate = estimate_point(positions, corrupt_distances, tuple(range(len(positions))))
        quorum = quorum_estimate(positions, corrupt_distances)

        if clean_estimate is not None:
            clean_errors.append(point_error(clean_estimate, truth))
        if naive_estimate is not None:
            naive_corrupt_errors.append(point_error(naive_estimate, truth))
        if quorum is not None:
            quorum_valid += 1
            q_estimate, _inliers, rejected_idx = quorum
            quorum_errors.append(point_error(q_estimate, truth))
            if rejected_idx == bad_idx:
                bad_rejections += 1

    clean_mae = sum(clean_errors) / len(clean_errors)
    naive_mae = sum(naive_corrupt_errors) / len(naive_corrupt_errors)
    quorum_mae = sum(quorum_errors) / len(quorum_errors)
    reject_rate = bad_rejections / quorum_valid
    valid_rate = quorum_valid / n

    status = (
        "pass"
        if quorum_mae < naive_mae * 0.55 and reject_rate > 0.70 and valid_rate > 0.95
        else "watch"
    )

    return [
        SwarmResult(
            probe_id="SWQ-001",
            status=status,
            metric="clean_mae; naive_corrupt_mae; quorum_mae; bad_node_reject_rate; quorum_valid_rate",
            value=f"{clean_mae:.4f}; {naive_mae:.4f}; {quorum_mae:.4f}; {reject_rate:.4f}; {valid_rate:.4f}",
            null_hypothesis="A quorum mesh does not beat naive all-node reconstruction when one observer drifts.",
            safest_read=(
                "A verified observer mesh can reject many bad local records and preserve a better shared estimate "
                "than naive averaging over all observers."
            ),
            falsifier="Naive all-node reconstruction matches quorum, or quorum fails to reject drifting observers.",
        ),
        SwarmResult(
            probe_id="SWQ-002",
            status="policy",
            metric="authority_status",
            value="quorum_is_evidence_not_authority",
            null_hypothesis="n/a",
            safest_read=(
                "Quorum should raise confidence or write shared estimates only after receipts verify. It must not "
                "directly authorize action."
            ),
            falsifier="Any implementation lets quorum bypass grants, revocation, or memory-boundary rules.",
        ),
    ]


def write_outputs(results: list[SwarmResult]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "probe_id",
                "status",
                "metric",
                "value",
                "null_hypothesis",
                "safest_read",
                "falsifier",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))

    lines = [
        "# GHP Swarm Quorum Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This tests whether a small observer mesh can preserve a shared estimate when one observer is corrupted or drifting.",
        "",
        "It does not prove holography, consciousness, GHP physics, or literal observer-created reality.",
        "",
        "## Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.probe_id}: {result.status}",
                "",
                f"- Metric: {result.metric}",
                f"- Value: {result.value}",
                f"- Null hypothesis: {result.null_hypothesis}",
                f"- Safest read: {result.safest_read}",
                f"- Falsifier: {result.falsifier}",
                "",
            ]
        )

    lines.extend(
        [
            "## Aukora Translation",
            "",
            "```text",
            "many node observations + verified receipts + quorum filter",
            "  -> shared estimate",
            "  -> confidence / memory consequence",
            "  -> never direct authority",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Quorum may increase confidence.",
            "Quorum may write a shared estimate.",
            "Quorum may never bypass authorization.",
            "```",
            "",
            "## Next Test",
            "",
            "Run the same structure on two or more live Aukora demo nodes watching the same bounded event stream, then introduce one delayed, drifting, or adversarial node.",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = run_probe()
    write_outputs(results)
    print(f"Wrote {OUT / 'report.md'}")
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()

