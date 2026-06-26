#!/usr/bin/env python3
"""
MEB-004 — D4 Orientation-Breaking Probe

This is a mathematical hardening probe, not physics evidence.

Question:
Can a non-hand-labeled orientation-breaking rule applied to the D4 / 24-cell
scaffold create chirality while preserving enough cancellation structure to
remain a plausible matter-embedding bridge?

Expected hardening result:
Naive orientation-breaking should either remain arbitrary or destroy the
symmetry/cancellation properties that made D4 useful. If so, the matter-
embedding lane stays promising but blocked.

Forbidden conclusion:
Do not infer chiral fermions, weak interactions, hypercharge, anomaly
cancellation, Standard Model recovery, particles, matter, or a closed
Matter Embedding Gap from this probe.
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
OUT = ROOT / "ghp_d4_orientation_breaking_probe_outputs"
SEED = 44004
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


def normalize(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x)
    return x / n if n else x


def chirality_imbalance(points: np.ndarray, sample_count: int = 5000) -> float:
    if len(points) < 4:
        return 0.0
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


def cancellation_loss(points: np.ndarray) -> float:
    """
    Simple symmetry-preservation cost. Zero is perfect.
    Not anomaly cancellation.
    """
    if len(points) == 0:
        return 999.0
    vector_norm = np.linalg.norm(np.sum(points, axis=0)) / len(points)
    axes = np.eye(4)
    cubic = max(abs(float(np.sum((points @ axis) ** 3))) for axis in axes) / len(points)
    return float(vector_norm + cubic)


def antipode_loss(points: np.ndarray, tol: float = 1e-8) -> float:
    if len(points) == 0:
        return 1.0
    misses = 0
    for v in points:
        if not np.any(np.linalg.norm(points + v, axis=1) < tol):
            misses += 1
    return misses / len(points)


def positive_halfspace(points: np.ndarray, axis: np.ndarray) -> np.ndarray:
    dots = points @ normalize(axis)
    return points[dots > 1e-10]


def simple_root_basis() -> np.ndarray:
    """
    One conventional D4 simple-root basis. This is deliberately marked
    as a structured-but-choiceful rule, not a unique natural projection.
    """
    return np.array(
        [
            [1, -1, 0, 0],
            [0, 1, -1, 0],
            [0, 0, 1, -1],
            [0, 0, 1, 1],
        ],
        dtype=float,
    ) / math.sqrt(2.0)


def weyl_positive_roots(points: np.ndarray) -> np.ndarray:
    basis = simple_root_basis()
    # Fundamental chamber vector: positive on all simple roots.
    axis = np.sum(basis, axis=0)
    return positive_halfspace(points, axis)


def triality_like_spinor_axis() -> np.ndarray:
    # Symmetric all-ones spinor-like axis. Structured, but still an extra choice.
    return normalize(np.array([1.0, 1.0, 1.0, 1.0]))


def score_break(points: np.ndarray) -> tuple[float, float, float]:
    return chirality_imbalance(points), cancellation_loss(points), antipode_loss(points)


def random_axis_controls(points: np.ndarray, n: int = 60) -> list[tuple[float, float, float]]:
    out = []
    for _ in range(n):
        axis = normalize(rng.normal(size=4))
        out.append(score_break(positive_halfspace(points, axis)))
    return out


def find_best_axis(points: np.ndarray, n: int = 500) -> tuple[float, float, float]:
    """
    Inadmissible oracle-ish control: searches random axes and selects the
    best chirality/cancellation tradeoff after looking at the data.
    """
    best = None
    best_score = -999.0
    for _ in range(n):
        axis = normalize(rng.normal(size=4))
        s = score_break(positive_halfspace(points, axis))
        chir, loss, antipode = s
        score = chir - 2.0 * loss - antipode
        if score > best_score:
            best_score = score
            best = s
    return best if best is not None else (0.0, 999.0, 1.0)


def run() -> list[ProbeResult]:
    roots = d4_roots()
    full_chir, full_loss, full_antipode = score_break(roots)

    chamber = weyl_positive_roots(roots)
    chamber_chir, chamber_loss, chamber_antipode = score_break(chamber)

    spinor_half = positive_halfspace(roots, triality_like_spinor_axis())
    spinor_chir, spinor_loss, spinor_antipode = score_break(spinor_half)

    controls = random_axis_controls(roots)
    control_chir = float(np.median([x[0] for x in controls]))
    control_loss = float(np.median([x[1] for x in controls]))
    control_antipode = float(np.median([x[2] for x in controls]))

    best_chir, best_loss, best_antipode = find_best_axis(roots)

    # A candidate is acceptable only if it creates notable chirality while
    # keeping cancellation loss small. This is expected to fail for naive rules.
    chamber_accept = chamber_chir > 0.20 and chamber_loss < 0.10
    spinor_accept = spinor_chir > 0.20 and spinor_loss < 0.10
    best_accept = best_chir > 0.20 and best_loss < 0.10

    return [
        ProbeResult(
            "MEB-004A",
            "bare_D4_chirality",
            full_chir,
            0.0,
            "PASS" if full_chir < 0.05 and full_loss < 1e-10 else "MIXED",
            "Bare D4 remains non-chiral and cancellation-preserving.",
        ),
        ProbeResult(
            "MEB-004B",
            "weyl_chamber_chirality_minus_loss",
            chamber_chir - chamber_loss,
            control_chir - control_loss,
            "PASS" if not chamber_accept else "MIXED",
            "A conventional Weyl-chamber halfspace is a choiceful orientation break and does not pass the chirality-plus-cancellation criterion.",
        ),
        ProbeResult(
            "MEB-004C",
            "spinor_axis_chirality_minus_loss",
            spinor_chir - spinor_loss,
            control_chir - control_loss,
            "PASS" if not spinor_accept else "MIXED",
            "A symmetric spinor-like halfspace is still an extra choice and does not pass the chirality-plus-cancellation criterion.",
        ),
        ProbeResult(
            "MEB-004D",
            "oracle_axis_admissibility",
            best_chir - best_loss,
            control_chir - control_loss,
            "PASS" if not best_accept else "MIXED",
            "Even a best-of-random-axis search does not establish an admissible non-hand-labeled orientation-breaking law.",
        ),
        ProbeResult(
            "MEB-004E",
            "antipode_loss_after_breaking",
            min(chamber_antipode, spinor_antipode, best_antipode),
            control_antipode,
            "PASS" if min(chamber_antipode, spinor_antipode, best_antipode) > 0.5 else "MIXED",
            "Naive orientation-breaking destroys the antipodal pairing that made the full D4 scaffold cancellation-clean.",
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
        "# MEB-004 — D4 Orientation-Breaking Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether simple non-hand-labeled orientation-breaking rules can make D4 chiral while preserving cancellation structure.",
        "",
        "It does **not** derive weak chirality, Standard Model fermions, hypercharge, anomaly cancellation, particles, matter, or a closed Matter Embedding Gap.",
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
            "- Bare D4 is non-chiral and cancellation-clean.",
            "- Naive orientation-breaking choices do not pass the joint chirality-plus-cancellation criterion.",
            "- This keeps the Matter Embedding Gap open and prevents premature Standard Model recovery claims.",
            "- The next bridge would need a principled orientation-breaking mechanism, not a hand-picked halfspace.",
            "",
            "## Next Test",
            "",
            "MEB-005 should look outside bare D4 for a principled breaker:",
            "",
            "```text",
            "Does F4, E6, a boundary condition, or a categorical/dynamical sector",
            "supply orientation-breaking while retaining cancellation constraints?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim D4 orientation breaking derives chiral matter.",
            "- Do not claim Weyl-chamber choice is a physical law.",
            "- Do not claim spinor-axis choice is hypercharge.",
            "- Do not claim random-axis search is admissible.",
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
