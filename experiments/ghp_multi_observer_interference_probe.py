#!/usr/bin/env python3
"""Synthetic multi-observer interference probe for GHP/Aukora.

This tests a bounded version of the "two ears" idea:

- each observer receives a noisy local projection of the same hidden source;
- the paired streams reconstruct more hidden state than either observer alone;
- shuffling one observer destroys the shared estimate;
- the shared estimate is evidence only, never authority.

It does not prove that reality is literally made of observer interference.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_multi_observer_interference_probe_outputs"


@dataclass
class ObserverEvent:
    event_id: int
    x: float
    y: float
    left_distance: float
    right_distance: float
    left_observation: float
    right_observation: float
    left_receipt_ok: bool
    right_receipt_ok: bool


@dataclass
class InterferenceResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def generate_events(seed: int = 1618, n: int = 2000, noise_sigma: float = 0.035) -> list[ObserverEvent]:
    rng = random.Random(seed)
    events: list[ObserverEvent] = []
    for event_id in range(n):
        x = rng.uniform(-2.0, 2.0)
        y = rng.uniform(0.5, 4.0)
        left_distance = math.hypot(x + 1.0, y)
        right_distance = math.hypot(x - 1.0, y)
        left_observation = max(0.001, left_distance + rng.gauss(0.0, noise_sigma))
        right_observation = max(0.001, right_distance + rng.gauss(0.0, noise_sigma))
        events.append(
            ObserverEvent(
                event_id=event_id,
                x=x,
                y=y,
                left_distance=left_distance,
                right_distance=right_distance,
                left_observation=left_observation,
                right_observation=right_observation,
                left_receipt_ok=True,
                right_receipt_ok=True,
            )
        )
    return events


def paired_estimate(left_obs: float, right_obs: float) -> tuple[float, float]:
    # Observers sit at (-1, 0) and (1, 0). With distances r_l and r_r:
    # r_l^2 - r_r^2 = 4x. Then y^2 = r_l^2 - (x+1)^2.
    x_hat = ((left_obs * left_obs) - (right_obs * right_obs)) / 4.0
    y2_hat = max(0.0, (left_obs * left_obs) - ((x_hat + 1.0) ** 2))
    return x_hat, math.sqrt(y2_hat)


def single_left_estimate(left_obs: float) -> tuple[float, float]:
    # A single distance ring cannot identify x. Use the symmetry baseline x=0.
    x_hat = 0.0
    y_hat = max(0.0, left_obs * left_obs - 1.0) ** 0.5
    return x_hat, y_hat


def mae(values: list[float]) -> float:
    return sum(abs(v) for v in values) / len(values)


def side_accuracy(xs: list[float], estimates: list[float]) -> float:
    correct = 0
    for x, x_hat in zip(xs, estimates):
        if (x >= 0) == (x_hat >= 0):
            correct += 1
    return correct / len(xs)


def run_probe() -> list[InterferenceResult]:
    events = generate_events()
    shuffled_right = [event.right_observation for event in events]
    random.Random(42).shuffle(shuffled_right)

    paired = [paired_estimate(event.left_observation, event.right_observation) for event in events]
    single = [single_left_estimate(event.left_observation) for event in events]
    shuffled = [paired_estimate(event.left_observation, right_obs) for event, right_obs in zip(events, shuffled_right)]

    xs = [event.x for event in events]
    ys = [event.y for event in events]
    paired_x = [item[0] for item in paired]
    paired_y = [item[1] for item in paired]
    single_x = [item[0] for item in single]
    single_y = [item[1] for item in single]
    shuffled_x = [item[0] for item in shuffled]
    shuffled_y = [item[1] for item in shuffled]

    paired_x_mae = mae([x - x_hat for x, x_hat in zip(xs, paired_x)])
    single_x_mae = mae([x - x_hat for x, x_hat in zip(xs, single_x)])
    shuffled_x_mae = mae([x - x_hat for x, x_hat in zip(xs, shuffled_x)])
    paired_y_mae = mae([y - y_hat for y, y_hat in zip(ys, paired_y)])
    single_y_mae = mae([y - y_hat for y, y_hat in zip(ys, single_y)])
    shuffled_y_mae = mae([y - y_hat for y, y_hat in zip(ys, shuffled_y)])
    paired_side = side_accuracy(xs, paired_x)
    single_side = side_accuracy(xs, single_x)
    shuffled_side = side_accuracy(xs, shuffled_x)

    pairing_status = (
        "pass"
        if paired_x_mae < single_x_mae * 0.35
        and paired_x_mae < shuffled_x_mae * 0.35
        and paired_side > 0.95
        and shuffled_side < 0.75
        else "watch"
    )

    return [
        InterferenceResult(
            probe_id="MOI-001",
            status=pairing_status,
            metric=(
                "paired_x_mae; single_x_mae; shuffled_x_mae; "
                "paired_y_mae; single_y_mae; shuffled_y_mae; "
                "paired_side_acc; single_side_acc; shuffled_side_acc"
            ),
            value=(
                f"{paired_x_mae:.4f}; {single_x_mae:.4f}; {shuffled_x_mae:.4f}; "
                f"{paired_y_mae:.4f}; {single_y_mae:.4f}; {shuffled_y_mae:.4f}; "
                f"{paired_side:.4f}; {single_side:.4f}; {shuffled_side:.4f}"
            ),
            null_hypothesis="Paired observers do not reconstruct hidden source state better than one observer or shuffled pairing.",
            safest_read=(
                "Correctly paired bounded observers reconstruct more hidden geometry than either single observer "
                "or a mismatched observer stream."
            ),
            falsifier="Single-observer or shuffled-pair controls match the paired reconstruction.",
        ),
        InterferenceResult(
            probe_id="MOI-002",
            status="policy",
            metric="authority_status",
            value="interference_is_evidence_not_authority",
            null_hypothesis="n/a",
            safest_read=(
                "The paired estimate can inform memory or confidence only after both observer receipts verify. "
                "It must not bypass gate authorization."
            ),
            falsifier="Any implementation lets phase/interference directly authorize action.",
        ),
    ]


def write_outputs(results: list[InterferenceResult]) -> None:
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
        "# GHP Multi-Observer Interference Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This tests the two-ear / two-node idea in a bounded way: two separate observer records can reconstruct more hidden state when paired correctly, and fail when mismatched.",
        "",
        "It does not prove that reality is literally made from observer interference.",
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
            "node A observation + node B observation + verified pairing",
            "  -> shared estimate",
            "  -> receipt",
            "  -> optional memory / learning consequence",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Interference may be evidence.",
            "Interference may be memory.",
            "Interference may never be authority.",
            "```",
            "",
            "## Next Test",
            "",
            "Move from synthetic distance observations to two live Aukora demo nodes watching the same bounded event stream. Compare paired receipts against single-node and shuffled-pair controls.",
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

