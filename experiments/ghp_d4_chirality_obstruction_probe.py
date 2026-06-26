#!/usr/bin/env python3
"""
MEB-003 — D4 Chirality Obstruction Probe

This is a mathematical hardening probe, not physics evidence.

Question:
Can the 24-cell / D4 root scaffold produce intrinsic left/right
asymmetry without an extra orientation-breaking choice?

Expected hardening result:
Because the D4 root system is centrally symmetric and reflection-symmetric,
intrinsic chirality should fail. That is not bad; it is a guardrail.

Forbidden conclusion:
Do not infer Standard Model chirality, weak interactions, fermions, matter,
or a closed Matter Embedding Gap from this probe.
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
OUT = ROOT / "ghp_d4_chirality_obstruction_probe_outputs"
SEED = 43003
rng = np.random.default_rng(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


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


def random_s3_points(n: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    x = local.normal(size=(n, 4))
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def central_symmetry_score(points: np.ndarray, tol: float = 1e-8) -> float:
    hits = 0
    for v in points:
        if np.any(np.linalg.norm(points + v, axis=1) < tol):
            hits += 1
    return hits / len(points)


def reflection_closure_score(points: np.ndarray, tol: float = 1e-8) -> float:
    """
    Closure under coordinate sign flips and swaps. D4 should be closed.
    Generic random controls should not be.
    """
    point_set = {tuple(np.round(v, 8)) for v in points}
    transforms = []
    for coord in range(4):
        signs = np.ones(4)
        signs[coord] = -1.0
        transforms.append(("flip", signs, None))
    for i, j in itertools.combinations(range(4), 2):
        transforms.append(("swap", None, (i, j)))

    hits = 0
    total = 0
    for kind, signs, swap in transforms:
        if kind == "flip":
            transformed = points * signs
        else:
            transformed = points.copy()
            i, j = swap
            transformed[:, [i, j]] = transformed[:, [j, i]]
        for v in transformed:
            total += 1
            if tuple(np.round(v, 8)) in point_set:
                hits += 1
    return hits / total


def oriented_tetra_volume(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    mat = np.stack([a, b, c, d], axis=1)
    return float(np.linalg.det(mat))


def chirality_imbalance(points: np.ndarray, sample_count: int = 6000) -> float:
    """
    Measures signed orientation imbalance across sampled quadruples.
    A reflection-symmetric non-chiral scaffold should be close to zero.
    """
    pos = 0
    neg = 0
    n = len(points)
    for _ in range(sample_count):
        idx = rng.choice(n, size=4, replace=False)
        vol = oriented_tetra_volume(points[idx[0]], points[idx[1]], points[idx[2]], points[idx[3]])
        if abs(vol) < 1e-10:
            continue
        if vol > 0:
            pos += 1
        else:
            neg += 1
    if pos + neg == 0:
        return 0.0
    return abs(pos - neg) / (pos + neg)


def orientation_breaking_needed(points: np.ndarray) -> float:
    """
    If a scaffold is reflection-closed and centrally symmetric, intrinsic chirality is blocked.
    Score 1 means an external orientation-breaking rule is needed to get chirality.
    """
    central = central_symmetry_score(points)
    reflect = reflection_closure_score(points)
    imbalance = chirality_imbalance(points)
    return 1.0 if central > 0.99 and reflect > 0.99 and imbalance < 0.05 else 0.0


def anomaly_like_cancellation_score(points: np.ndarray) -> float:
    """
    Toy cancellation sanity: vector sum and cubic projection moments should cancel
    for the full D4 root set. This is not anomaly cancellation; it is only a
    symmetry-cancellation scaffold.
    """
    vector_norm = np.linalg.norm(np.sum(points, axis=0))
    axes = np.eye(4)
    cubic_moments = [abs(float(np.sum((points @ axis) ** 3))) for axis in axes]
    return 1.0 if vector_norm < 1e-10 and max(cubic_moments) < 1e-10 else 0.0


def run() -> list[ProbeResult]:
    roots = d4_roots()
    controls = [random_s3_points(24, SEED + i) for i in range(1, 51)]

    central = central_symmetry_score(roots)
    control_central = float(np.median([central_symmetry_score(c) for c in controls]))

    reflect = reflection_closure_score(roots)
    control_reflect = float(np.median([reflection_closure_score(c) for c in controls]))

    imbalance = chirality_imbalance(roots)
    control_imbalance = float(np.median([chirality_imbalance(c, sample_count=1200) for c in controls[:12]]))

    obstruction = orientation_breaking_needed(roots)
    control_obstruction = float(np.median([orientation_breaking_needed(c) for c in controls[:12]]))

    cancellation = anomaly_like_cancellation_score(roots)
    control_cancellation = float(np.median([anomaly_like_cancellation_score(c) for c in controls]))

    return [
        ProbeResult(
            "MEB-003A",
            "central_symmetry_score",
            central,
            control_central,
            "PASS" if central == 1.0 and control_central == 0.0 else "MIXED",
            "D4 is exactly centrally symmetric; this blocks intrinsic matter/antimatter asymmetry without extra structure.",
        ),
        ProbeResult(
            "MEB-003B",
            "reflection_closure_score",
            reflect,
            control_reflect,
            "PASS" if reflect == 1.0 and control_reflect == 0.0 else "MIXED",
            "D4 is reflection-closed; intrinsic chirality is not available from the bare scaffold.",
        ),
        ProbeResult(
            "MEB-003C",
            "chirality_imbalance_lower_is_nonchiral",
            imbalance,
            control_imbalance,
            "PASS" if imbalance < 0.05 else "MIXED",
            "Sampled oriented volumes show no strong intrinsic handedness; this is a chirality obstruction.",
        ),
        ProbeResult(
            "MEB-003D",
            "orientation_breaking_needed",
            obstruction,
            control_obstruction,
            "PASS" if obstruction == 1.0 else "FAIL",
            "A bare D4/24-cell scaffold needs an extra orientation-breaking rule before it can model chiral matter.",
        ),
        ProbeResult(
            "MEB-003E",
            "symmetry_cancellation_score",
            cancellation,
            control_cancellation,
            "PASS" if cancellation == 1.0 and control_cancellation == 0.0 else "MIXED",
            "D4 has exact vector/cubic cancellation as a scaffold, but this is not Standard Model anomaly cancellation.",
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
        "# MEB-003 — D4 Chirality Obstruction Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether the bare 24-cell / D4 root scaffold can produce intrinsic chirality without an extra orientation-breaking rule.",
        "",
        "It does **not** derive weak interactions, Standard Model chirality, fermions, matter, or anomaly cancellation.",
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
            "- The bare D4 / 24-cell scaffold is highly symmetric and non-chiral.",
            "- That is useful as a guardrail: it blocks premature claims that D4 alone gives chiral matter.",
            "- Any future matter-embedding bridge needs an additional orientation-breaking mechanism, projection, or dynamical sector.",
            "- The symmetry-cancellation result is only a toy cancellation scaffold, not Standard Model anomaly cancellation.",
            "",
            "## Next Test",
            "",
            "MEB-004 should test candidate orientation-breaking mechanisms:",
            "",
            "```text",
            "Can a non-arbitrary projection, boundary condition, or triality choice",
            "break D4 symmetry while preserving enough cancellation structure",
            "to remain mathematically disciplined?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim D4 derives chiral fermions.",
            "- Do not claim D4 derives the weak interaction.",
            "- Do not claim the symmetry-cancellation score is anomaly cancellation.",
            "- Do not claim this closes the Matter Embedding Gap.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    (OUT / "metadata.json").write_text(json.dumps({"seed": SEED, "pass_count": pass_count, "total": len(results)}, indent=2) + "\n")


if __name__ == "__main__":
    results = run()
    write_outputs(results)
    print(f"PASS {sum(1 for r in results if r.verdict == 'PASS')}/{len(results)}")
    for r in results:
        print(f"{r.probe}: {r.verdict} value={r.value:.6f} control={r.control:.6f}")
