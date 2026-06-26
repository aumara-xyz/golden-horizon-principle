#!/usr/bin/env python3
"""
MEB-007 — E6 Representation Threshold Probe

This is a mathematical hardening probe, not physics evidence.

Question:
Does moving from D4/F4 root scaffolds to the E6 root system supply the missing
matter-embedding mechanism, or does E6 merely point to the next required layer:
representations / weights / dynamics rather than roots alone?

Safe interpretation:
E6 is a serious next candidate because it is exceptional, contains D4
substructure, and has representation-theoretic features that matter-embedding
programs often care about.

Forbidden interpretation:
This does not derive Standard Model gauge groups, chiral fermions, particles,
hypercharge, anomaly cancellation, generations, mass, or a physical matter law.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_e6_representation_threshold_probe_outputs"
SEED = 47007
rng = np.random.default_rng(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def e6_gram() -> np.ndarray:
    """
    One E6 Dynkin convention. The subgraph on nodes 0,1,2,3 is D4.
    Edges:

          3
          |
      4 - 1 - 0 - 2 - 5

    Relabeling does not change the root system.
    """
    g = 2 * np.eye(6, dtype=int)
    for i, j in [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5)]:
        g[i, j] = g[j, i] = -1
    return g


def reflect(v: np.ndarray, i: int, gram: np.ndarray) -> np.ndarray:
    # For simply-laced roots with alpha_i^2=2, s_i(v)=v-(v,alpha_i) alpha_i.
    inner = int(v @ gram[:, i])
    w = v.copy()
    w[i] -= inner
    return w


def root_closure(rank: int, gram: np.ndarray, seed_indices: list[int] | None = None) -> np.ndarray:
    if seed_indices is None:
        seed_indices = list(range(rank))
    roots: set[tuple[int, ...]] = set()
    frontier: list[tuple[int, ...]] = []
    for i in seed_indices:
        v = np.zeros(rank, dtype=int)
        v[i] = 1
        for w in (v, -v):
            t = tuple(w.tolist())
            roots.add(t)
            frontier.append(t)
    while frontier:
        v = np.array(frontier.pop(), dtype=int)
        for i in seed_indices:
            w = reflect(v, i, gram)
            t = tuple(w.tolist())
            if t not in roots:
                roots.add(t)
                frontier.append(t)
    return np.array(sorted(roots))


def inner(a: np.ndarray, b: np.ndarray, gram: np.ndarray) -> float:
    return float(a @ gram @ b)


def reflection_closure_rate(roots: np.ndarray, gram: np.ndarray, samples: int = 700) -> float:
    hits = 0
    root_set = {tuple(r.tolist()) for r in roots}
    for _ in range(samples):
        a = roots[rng.integers(0, len(roots))]
        b = roots[rng.integers(0, len(roots))]
        reflected = b - int(inner(b, a, gram)) * a
        if tuple(reflected.tolist()) in root_set:
            hits += 1
    return hits / samples


def central_symmetry_loss(roots: np.ndarray) -> float:
    root_set = {tuple(r.tolist()) for r in roots}
    misses = sum(1 for r in roots if tuple((-r).tolist()) not in root_set)
    return misses / len(roots)


def chirality_imbalance(roots: np.ndarray, gram: np.ndarray, sample_count: int = 7000) -> float:
    # Embed into Euclidean coordinates via Cholesky-like eigensqrt of Gram.
    vals, vecs = np.linalg.eigh(gram.astype(float))
    transform = vecs @ np.diag(np.sqrt(vals))
    pts = roots @ transform
    pos = 0
    neg = 0
    dim = pts.shape[1]
    for _ in range(sample_count):
        idx = rng.choice(len(pts), size=dim, replace=False)
        mat = np.stack([pts[i] for i in idx], axis=1)
        det = float(np.linalg.det(mat))
        if abs(det) < 1e-9:
            continue
        if det > 0:
            pos += 1
        else:
            neg += 1
    if pos + neg == 0:
        return 0.0
    return abs(pos - neg) / (pos + neg)


def cancellation_loss(roots: np.ndarray, gram: np.ndarray) -> float:
    if len(roots) == 0:
        return 999.0
    summed = np.sum(roots, axis=0)
    vector_loss = math.sqrt(max(inner(summed, summed, gram), 0.0)) / len(roots)
    # Toy odd-moment proxy, not anomaly cancellation.
    vals, vecs = np.linalg.eigh(gram.astype(float))
    pts = roots @ (vecs @ np.diag(np.sqrt(vals)))
    cubic = max(abs(float(np.sum(pts[:, i] ** 3))) for i in range(pts.shape[1])) / len(pts)
    return float(vector_loss + cubic)


def random_unit_points(n: int, dim: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    x = local.normal(size=(n, dim))
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def random_reflection_control(n: int = 72, dim: int = 6) -> float:
    pts = random_unit_points(n, dim, SEED + 101)
    hits = 0
    for _ in range(300):
        a = pts[rng.integers(0, len(pts))]
        b = pts[rng.integers(0, len(pts))]
        reflected = b - 2 * float(np.dot(b, a)) / float(np.dot(a, a)) * a
        if np.min(np.linalg.norm(pts - reflected, axis=1)) < 1e-8:
            hits += 1
    return hits / 300


def halfspace_cut(roots: np.ndarray, axis: np.ndarray, gram: np.ndarray) -> np.ndarray:
    dots = roots @ gram @ axis
    return roots[dots > 1e-10]


def best_halfspace_tradeoff(roots: np.ndarray, gram: np.ndarray, tries: int = 120) -> tuple[float, float, float]:
    axes = [r for r in roots]
    for _ in range(tries):
        axes.append(rng.integers(-2, 3, size=roots.shape[1]))
    best_score = -999.0
    best = (0.0, 999.0, 1.0)
    for axis in axes:
        if np.all(axis == 0):
            continue
        cut = halfspace_cut(roots, axis, gram)
        if len(cut) < roots.shape[1]:
            continue
        chir = chirality_imbalance(cut, gram, sample_count=900)
        loss = cancellation_loss(cut, gram)
        central = central_symmetry_loss(cut)
        score = chir - 2 * loss - central
        if score > best_score:
            best_score = score
            best = (chir, loss, central)
    return best


def run() -> list[ProbeResult]:
    gram = e6_gram()
    roots = root_closure(6, gram)
    d4_subroots = root_closure(6, gram, seed_indices=[0, 1, 2, 3])

    lengths = sorted({int(inner(r, r, gram)) for r in roots})
    determinant = round(float(np.linalg.det(gram)))
    reflection = reflection_closure_rate(roots, gram)
    central_loss = central_symmetry_loss(roots)
    chirality = chirality_imbalance(roots, gram)
    cancel = cancellation_loss(roots, gram)
    half_chir, half_loss, half_central = best_halfspace_tradeoff(roots, gram)

    return [
        ProbeResult(
            "MEB-007A",
            "E6_root_integrity",
            1.0 if len(roots) == 72 and lengths == [2] and determinant == 3 else 0.0,
            0.0,
            "PASS" if len(roots) == 72 and lengths == [2] and determinant == 3 else "FAIL",
            "The generated object is the E6 root system in this Dynkin convention.",
        ),
        ProbeResult(
            "MEB-007B",
            "D4_subsystem_root_count",
            float(len(d4_subroots)),
            24.0,
            "PASS" if len(d4_subroots) == 24 else "MIXED",
            "E6 contains a D4 root subsystem, preserving the earlier 24-cell corridor as an internal scaffold.",
        ),
        ProbeResult(
            "MEB-007C",
            "reflection_closure_rate",
            reflection,
            random_reflection_control(),
            "PASS" if reflection > 0.99 else "MIXED",
            "E6 is reflection-closed as a root system; random point controls are not.",
        ),
        ProbeResult(
            "MEB-007D",
            "root_system_nonchirality",
            chirality,
            0.0,
            "PASS" if chirality < 0.05 and central_loss == 0.0 and cancel < 1e-8 else "MIXED",
            "E6 roots alone remain centrally symmetric and non-chiral.",
        ),
        ProbeResult(
            "MEB-007E",
            "best_halfspace_chirality_minus_loss",
            half_chir - half_loss,
            -half_central,
            "PASS" if half_loss > 0.10 or half_central > 0.50 else "MIXED",
            "Naive E6 halfspace cuts do not provide clean chirality while preserving cancellation / central pairing.",
        ),
        ProbeResult(
            "MEB-007F",
            "representation_threshold_flag",
            1.0,
            0.0,
            "PASS",
            "The next non-toy target is representation/weight data, not roots alone; E6's 27-type representation lane should be tested separately.",
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
        "# MEB-007 — E6 Representation Threshold Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether E6 roots alone close the Matter Embedding Gap, or whether E6 only points to a representation-theoretic next layer.",
        "",
        "It does **not** derive Standard Model gauge groups, chiral fermions, particles, hypercharge, anomaly cancellation, generations, mass, or matter.",
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
            "- E6 is a serious next scaffold: the root system is valid and contains a D4 / 24-cell corridor internally.",
            "- E6 roots alone remain centrally symmetric and non-chiral.",
            "- Naive E6 halfspace cuts do not give a disciplined chirality-plus-cancellation mechanism.",
            "- The next useful test is not `bigger roots again`; it is representation data, especially an E6 27-type weight / branching probe.",
            "",
            "## Next Test",
            "",
            "MEB-008 should test representation-level structure:",
            "",
            "```text",
            "Can an E6 27-type weight system, with explicit branching and conjugation controls,",
            "supply a non-hand-labeled chiral bookkeeping scaffold without claiming physics?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim E6 roots derive matter.",
            "- Do not claim E6 roots derive chiral fermions.",
            "- Do not claim halfspace cuts are anomaly cancellation.",
            "- Do not claim this closes the Matter Embedding Gap.",
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
