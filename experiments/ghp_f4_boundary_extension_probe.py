#!/usr/bin/env python3
"""
MEB-005 — F4 Boundary Extension Probe

This is a mathematical hardening probe, not physics evidence.

Question:
Does the F4 root system supply a principled extension of the D4 / 24-cell
scaffold that solves the chirality / orientation-breaking obstruction found
in MEB-003 and MEB-004?

Safe interpretation:
F4 may be a stronger boundary alphabet because it contains D4 plus a second
dual 24-cell-like layer.

Forbidden interpretation:
This does not derive Standard Model gauge groups, chiral fermions, particles,
matter, hypercharge, anomaly cancellation, generations, or a closed Matter
Embedding Gap.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_f4_boundary_extension_probe_outputs"
SEED = 45005
rng = np.random.default_rng(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def canonical(v: np.ndarray, ndigits: int = 8) -> tuple[float, ...]:
    return tuple(float(x) for x in np.round(v, ndigits))


def unique_rows(rows: list[np.ndarray]) -> np.ndarray:
    seen: dict[tuple[float, ...], np.ndarray] = {}
    for row in rows:
        seen[canonical(row)] = row
    return np.array(list(seen.values()))


def d4_roots() -> np.ndarray:
    roots = []
    for i in range(4):
        for j in range(i + 1, 4):
            for si in (-1.0, 1.0):
                for sj in (-1.0, 1.0):
                    v = np.zeros(4)
                    v[i] = si
                    v[j] = sj
                    roots.append(v / math.sqrt(2.0))
    return np.array(roots)


def f4_roots() -> np.ndarray:
    roots: list[np.ndarray] = []

    # Coordinate roots: ±e_i.
    for i in range(4):
        for s in (-1.0, 1.0):
            v = np.zeros(4)
            v[i] = s
            roots.append(v)

    # D4 / 24-cell roots: (±e_i ± e_j)/sqrt(2).
    roots.extend(list(d4_roots()))

    # Half-sign roots: (±e1 ± e2 ± e3 ± e4)/2.
    for signs in itertools.product((-1.0, 1.0), repeat=4):
        roots.append(np.array(signs) / 2.0)

    return unique_rows(roots)


def random_s3_points(n: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    x = local.normal(size=(n, 4))
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def contains_all(points: np.ndarray, subset: np.ndarray, tol: float = 1e-8) -> bool:
    return all(np.any(np.linalg.norm(points - v, axis=1) < tol) for v in subset)


def antipode_loss(points: np.ndarray, tol: float = 1e-8) -> float:
    misses = 0
    for v in points:
        if not np.any(np.linalg.norm(points + v, axis=1) < tol):
            misses += 1
    return misses / len(points)


def reflection_closure_rate(points: np.ndarray, samples: int = 500, tol: float = 1e-8) -> float:
    hits = 0
    for _ in range(samples):
        a = points[rng.integers(0, len(points))]
        b = points[rng.integers(0, len(points))]
        reflected = b - 2.0 * float(np.dot(b, a)) / float(np.dot(a, a)) * a
        if np.any(np.linalg.norm(points - reflected, axis=1) < tol):
            hits += 1
    return hits / samples


def chirality_imbalance(points: np.ndarray, sample_count: int = 7000) -> float:
    pos = 0
    neg = 0
    for _ in range(sample_count):
        idx = rng.choice(len(points), size=4, replace=False)
        mat = np.stack([points[i] for i in idx], axis=1)
        vol = float(np.linalg.det(mat))
        if abs(vol) < 1e-10:
            continue
        if vol > 0:
            pos += 1
        else:
            neg += 1
    if pos + neg == 0:
        return 0.0
    return abs(pos - neg) / (pos + neg)


def orbit_counts(points: np.ndarray) -> dict[str, int]:
    d4 = d4_roots()
    d4_set = {canonical(v) for v in d4}
    d4_count = sum(1 for v in points if canonical(v) in d4_set)
    return {"d4_layer": d4_count, "extra_layer": len(points) - d4_count}


def nearest_quantization_error(points: np.ndarray, samples: np.ndarray) -> float:
    total = 0.0
    for x in samples:
        total += float(np.min(np.linalg.norm(points - x, axis=1)))
    return total / len(samples)


def run() -> list[ProbeResult]:
    d4 = d4_roots()
    f4 = f4_roots()
    controls = [random_s3_points(len(f4), SEED + i) for i in range(1, 21)]
    control_reflection = float(np.median([reflection_closure_rate(c, samples=120) for c in controls]))
    control_chirality = float(np.median([chirality_imbalance(c, sample_count=1000) for c in controls]))
    control_antipode = float(np.median([antipode_loss(c) for c in controls]))

    counts = orbit_counts(f4)

    sample_points = random_s3_points(1200, SEED + 999)
    d4_q = nearest_quantization_error(d4, sample_points)
    f4_q = nearest_quantization_error(f4, sample_points)
    control_q = float(np.median([nearest_quantization_error(c, sample_points) for c in controls]))

    f4_chirality = chirality_imbalance(f4)
    f4_antipode = antipode_loss(f4)
    f4_reflection = reflection_closure_rate(f4)

    return [
        ProbeResult(
            "MEB-005A",
            "F4_root_count_and_D4_embedding",
            1.0 if len(f4) == 48 and contains_all(f4, d4) else 0.0,
            0.0,
            "PASS" if len(f4) == 48 and contains_all(f4, d4) else "FAIL",
            "F4 contains the D4 / 24-cell scaffold as an exact sublayer and adds another 24 roots.",
        ),
        ProbeResult(
            "MEB-005B",
            "dual_layer_balance",
            float(counts["extra_layer"] / max(counts["d4_layer"], 1)),
            1.0,
            "PASS" if counts["d4_layer"] == 24 and counts["extra_layer"] == 24 else "MIXED",
            "F4 gives a balanced D4-plus-extra-root boundary alphabet, not merely an arbitrary enlargement.",
        ),
        ProbeResult(
            "MEB-005C",
            "reflection_closure_rate",
            f4_reflection,
            control_reflection,
            "PASS" if f4_reflection > 0.99 and control_reflection < 0.10 else "MIXED",
            "F4 is a genuine root system closed under its root reflections; random controls are not.",
        ),
        ProbeResult(
            "MEB-005D",
            "chirality_obstruction",
            f4_chirality,
            control_chirality,
            "PASS" if f4_chirality < 0.05 else "MIXED",
            "F4 is still non-chiral by itself; adding the F4 extension does not solve the chirality problem.",
        ),
        ProbeResult(
            "MEB-005E",
            "antipode_cancellation_preservation",
            f4_antipode,
            control_antipode,
            "PASS" if f4_antipode == 0.0 and control_antipode > 0.9 else "MIXED",
            "F4 preserves antipodal cancellation structure; this is useful but not a matter derivation.",
        ),
        ProbeResult(
            "MEB-005F",
            "quantization_improvement_over_D4",
            d4_q - f4_q,
            control_q - f4_q,
            "PASS" if f4_q < d4_q and f4_q < control_q else "MIXED",
            "The F4 extension improves nearest-root coverage of S3 samples over D4 in this toy metric.",
        ),
    ]


def write_outputs(results: list[ProbeResult]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["probe", "metric", "value", "control", "verdict", "safe_read"])
        writer.writeheader()
        for r in results:
            writer.writerow(r.__dict__)

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    report = [
        "# MEB-005 — F4 Boundary Extension Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether F4 extends the D4 / 24-cell scaffold in a way that solves the previous chirality obstruction.",
        "",
        "It does **not** derive the Standard Model, particles, matter, hypercharge, anomaly cancellation, or a closed Matter Embedding Gap.",
        "",
        "## Results",
        "",
        "| Probe | Metric | Value | Control | Verdict |",
        "|---|---:|---:|---:|---|",
    ]
    for r in results:
        report.append(f"| {r.probe} | {r.metric} | {r.value:.6f} | {r.control:.6f} | {r.verdict} |")
    report.extend(
        [
            "",
            f"Pass count: **{pass_count}/{len(results)}**.",
            "",
            "## Interpretation",
            "",
            "- F4 is a real, principled enlargement of D4: it contains the 24-cell scaffold and adds a second balanced 24-root layer.",
            "- F4 is reflection-closed and cancellation-clean, so it is a stronger boundary alphabet candidate than bare D4.",
            "- F4 does **not** solve chirality by itself; it remains too symmetric.",
            "- The safe upgrade is therefore: F4 may be a better scaffold for future Matter Embedding Gap work, but it is not the missing matter law.",
            "",
            "## Next Test",
            "",
            "MEB-006 should test a projection or boundary-condition rule on F4:",
            "",
            "```text",
            "Can a natural observer-boundary projection of F4 break chirality",
            "while preserving enough cancellation structure?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim F4 derives chiral matter.",
            "- Do not claim F4 derives SU(3) x SU(2) x U(1).",
            "- Do not claim the extra 24 roots are particles.",
            "- Do not claim F4 closes the Matter Embedding Gap.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "pass_count": pass_count,
                "total": len(results),
                "status": "mathematical_hardening_probe_not_physics_evidence",
            },
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    results = run()
    write_outputs(results)
    pass_count = sum(1 for r in results if r.verdict == "PASS")
    print(f"PASS {pass_count}/{len(results)}")
    for r in results:
        print(f"{r.probe}: {r.verdict} value={r.value:.6f} control={r.control:.6f}")


if __name__ == "__main__":
    main()
