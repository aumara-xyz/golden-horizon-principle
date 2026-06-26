#!/usr/bin/env python3
"""
MEB-006 — F4 Boundary Projection Probe

This is a mathematical hardening probe, not physics evidence.

Question:
If F4 is a stronger boundary alphabet than bare D4, can a natural observer-
boundary projection or halfspace rule create chirality while preserving
cancellation structure?

Safe interpretation:
Projection is a plausible next bridge object because observer theories often
turn hidden high-dimensional state into a lower-dimensional readable boundary.

Forbidden interpretation:
This does not derive chiral fermions, weak interactions, Standard Model
matter, hypercharge, anomaly cancellation, particles, or physical reality.
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
OUT = ROOT / "ghp_f4_boundary_projection_probe_outputs"
SEED = 46006
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
    for i in range(4):
        for s in (-1.0, 1.0):
            v = np.zeros(4)
            v[i] = s
            roots.append(v)
    roots.extend(list(d4_roots()))
    for signs in itertools.product((-1.0, 1.0), repeat=4):
        roots.append(np.array(signs) / 2.0)
    return unique_rows(roots)


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n else v


def orthogonal_basis(axis: np.ndarray) -> np.ndarray:
    axis = normalize(axis)
    candidates = np.eye(4)
    basis: list[np.ndarray] = []
    for c in candidates:
        v = c - np.dot(c, axis) * axis
        for b in basis:
            v = v - np.dot(v, b) * b
        if np.linalg.norm(v) > 1e-8:
            basis.append(normalize(v))
    if len(basis) < 3:
        # Deterministic fallback for axes too close to coordinate candidates.
        for c in np.array(list(itertools.product((-1.0, 1.0), repeat=4))):
            v = c - np.dot(c, axis) * axis
            for b in basis:
                v = v - np.dot(v, b) * b
            if np.linalg.norm(v) > 1e-8:
                basis.append(normalize(v))
            if len(basis) == 3:
                break
    return np.array(basis[:3])


def project_to_boundary(points: np.ndarray, axis: np.ndarray) -> np.ndarray:
    basis = orthogonal_basis(axis)
    return points @ basis.T


def antipode_loss(points: np.ndarray, tol: float = 1e-8) -> float:
    if len(points) == 0:
        return 1.0
    misses = 0
    for v in points:
        if not np.any(np.linalg.norm(points + v, axis=1) < tol):
            misses += 1
    return misses / len(points)


def cancellation_loss(points: np.ndarray) -> float:
    if len(points) == 0:
        return 999.0
    vector_norm = np.linalg.norm(np.sum(points, axis=0)) / len(points)
    cubic = 0.0
    for axis in np.eye(points.shape[1]):
        cubic = max(cubic, abs(float(np.sum((points @ axis) ** 3))) / len(points))
    return float(vector_norm + cubic)


def chirality_imbalance_3d(points: np.ndarray, sample_count: int = 5000) -> float:
    if len(points) < 3:
        return 0.0
    pos = 0
    neg = 0
    for _ in range(sample_count):
        idx = rng.choice(len(points), size=3, replace=False)
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


def positive_halfspace(points: np.ndarray, axis: np.ndarray) -> np.ndarray:
    dots = points @ normalize(axis)
    return points[dots > 1e-10]


def random_s3_points(n: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    x = local.normal(size=(n, 4))
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def natural_axes(points: np.ndarray) -> np.ndarray:
    return unique_rows([normalize(v) for v in points])


def score_halfspace(points: np.ndarray, axis: np.ndarray) -> tuple[float, float, float]:
    half = positive_halfspace(points, axis)
    projected = project_to_boundary(half, axis)
    return chirality_imbalance_3d(projected), cancellation_loss(half), antipode_loss(half)


def run() -> list[ProbeResult]:
    f4 = f4_roots()
    axes = natural_axes(f4)

    quotient_scores = []
    unique_counts = []
    for axis in axes:
        projected = project_to_boundary(f4, axis)
        quotient_scores.append(chirality_imbalance_3d(projected, sample_count=1200))
        unique_counts.append(len({canonical(v) for v in projected}))

    half_scores = [score_halfspace(f4, axis) for axis in axes]
    natural_best = max((chir - 2.0 * loss - anti for chir, loss, anti in half_scores), default=-999.0)
    natural_best_chir = max((chir for chir, _, _ in half_scores), default=0.0)
    natural_best_loss = min((loss for _, loss, _ in half_scores), default=999.0)
    natural_best_antipode = min((anti for _, _, anti in half_scores), default=1.0)

    random_scores = []
    for _ in range(120):
        axis = normalize(rng.normal(size=4))
        random_scores.append(score_halfspace(f4, axis))
    random_best = max((chir - 2.0 * loss - anti for chir, loss, anti in random_scores), default=-999.0)
    random_chir = float(np.median([x[0] for x in random_scores]))
    random_loss = float(np.median([x[1] for x in random_scores]))
    random_antipode = float(np.median([x[2] for x in random_scores]))

    controls = [random_s3_points(len(f4), SEED + i) for i in range(1, 16)]
    control_projection_chir = []
    for c in controls:
        axis = normalize(rng.normal(size=4))
        control_projection_chir.append(chirality_imbalance_3d(project_to_boundary(c, axis), sample_count=800))

    # Projection is expected to preserve symmetry rather than generate chirality.
    quotient_chirality = float(np.median(quotient_scores))
    quotient_unique_ratio = float(np.median(unique_counts) / len(f4))

    half_accept = natural_best_chir > 0.20 and natural_best_loss < 0.10 and natural_best_antipode < 0.20

    return [
        ProbeResult(
            "MEB-006A",
            "quotient_projection_nonchirality",
            quotient_chirality,
            float(np.median(control_projection_chir)),
            "PASS" if quotient_chirality < 0.05 else "MIXED",
            "Natural F4-to-boundary quotient projections preserve symmetry; they do not generate chirality.",
        ),
        ProbeResult(
            "MEB-006B",
            "projection_unique_ratio",
            quotient_unique_ratio,
            1.0,
            "PASS" if quotient_unique_ratio > 0.50 else "MIXED",
            "Projection retains a substantial readable boundary alphabet rather than collapsing everything to one point.",
        ),
        ProbeResult(
            "MEB-006C",
            "natural_halfspace_admissibility",
            natural_best,
            random_best,
            "PASS" if not half_accept else "MIXED",
            "Natural F4-root halfspaces do not pass the joint chirality-plus-cancellation criterion.",
        ),
        ProbeResult(
            "MEB-006D",
            "natural_best_chirality",
            natural_best_chir,
            random_chir,
            "PASS" if natural_best_chir < 0.20 or natural_best_loss >= 0.10 else "MIXED",
            "Any apparent chirality from a halfspace remains tied to cancellation loss, not a clean physical split.",
        ),
        ProbeResult(
            "MEB-006E",
            "antipode_loss_after_boundary_cut",
            natural_best_antipode,
            random_antipode,
            "PASS" if natural_best_antipode > 0.50 else "MIXED",
            "Boundary cuts destroy antipodal pairing; this blocks treating a naive cut as anomaly-safe matter.",
        ),
        ProbeResult(
            "MEB-006F",
            "best_cancellation_loss",
            natural_best_loss,
            random_loss,
            "PASS" if natural_best_loss >= 0.10 else "MIXED",
            "The best natural halfspace still carries too much cancellation loss for a disciplined matter bridge.",
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
        "# MEB-006 — F4 Boundary Projection Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether natural F4 boundary projections or root halfspaces solve the chirality obstruction.",
        "",
        "It does **not** derive chiral fermions, weak interactions, matter, or a closed Matter Embedding Gap.",
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
            "- Natural quotient projection keeps F4 readable but does not create chirality.",
            "- Natural root halfspaces can create asymmetry only by destroying the cancellation / antipodal structure.",
            "- This blocks the simple answer: `F4 plus observer projection gives matter`.",
            "- The next viable bridge likely needs a richer representation-theoretic or dynamical rule, not a geometric cut alone.",
            "",
            "## Next Test",
            "",
            "MEB-007 should compare larger candidate structures such as E6 against the same chirality/cancellation constraints.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim F4 projection derives chirality.",
            "- Do not claim observer projection alone solves Matter Embedding.",
            "- Do not claim boundary cuts are anomaly cancellation.",
            "- Do not claim this derives particles or physical matter.",
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
