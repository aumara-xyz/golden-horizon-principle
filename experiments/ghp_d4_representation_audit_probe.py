#!/usr/bin/env python3
"""
MEB-002 — D4 Representation Audit Probe

This is a mathematical scaffold probe, not physics evidence.

Question:
Does the D4 / 24-cell root system contain non-hand-labeled
A2 + A1 + U(1)-like substructure more cleanly than generic 24-point
controls?

Safe interpretation:
Finding A2 and A1 sub-root scaffolds is useful for the Matter Embedding Gap.

Forbidden interpretation:
This does not derive SU(3) x SU(2) x U(1), Standard Model charges,
chirality, hypercharge, generations, particles, or matter.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np


SEED = 42024
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_d4_representation_audit_probe_outputs"
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


def rank(x: np.ndarray, tol: float = 1e-8) -> int:
    return int(np.linalg.matrix_rank(x, tol=tol))


def has_antipode(v: np.ndarray, subset: np.ndarray, tol: float = 1e-8) -> bool:
    return bool(np.any(np.linalg.norm(subset + v, axis=1) < tol))


def is_a2_subset(subset: np.ndarray, tol: float = 1e-8) -> bool:
    if len(subset) != 6 or rank(subset, tol) != 2:
        return False
    for v in subset:
        if not has_antipode(v, subset, tol):
            return False
    dots = subset @ subset.T
    off = dots[~np.eye(6, dtype=bool)]
    allowed = np.array([-1.0, -0.5, 0.5])
    for x in off:
        if np.min(np.abs(allowed - x)) > 1e-7:
            return False
    return True


def canonical_subset_key(indices: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(indices))


def antipodal_pairs(points: np.ndarray, tol: float = 1e-8) -> list[tuple[int, int]]:
    pairs = []
    for i, j in itertools.combinations(range(len(points)), 2):
        if np.linalg.norm(points[i] + points[j]) < tol:
            pairs.append((i, j))
    return pairs


def find_a2_subsystems(points: np.ndarray, max_count: int | None = None) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []
    pairs = antipodal_pairs(points)
    if len(pairs) < 3:
        return out
    for triple in itertools.combinations(pairs, 3):
        comb = tuple(sorted(i for pair in triple for i in pair))
        subset = points[list(comb)]
        if is_a2_subset(subset):
            out.append(canonical_subset_key(comb))
            if max_count is not None and len(out) >= max_count:
                break
    return out


def orthonormal_basis(x: np.ndarray, tol: float = 1e-8) -> np.ndarray:
    _, s, vh = np.linalg.svd(x, full_matrices=False)
    keep = s > tol
    return vh[keep]


def projection_residual_norm(v: np.ndarray, basis: np.ndarray) -> float:
    if len(basis) == 0:
        return float(np.linalg.norm(v))
    proj = basis.T @ (basis @ v)
    return float(np.linalg.norm(v - proj))


def count_a2_a1_extensions(points: np.ndarray, a2s: list[tuple[int, ...]], tol: float = 1e-8) -> int:
    count = 0
    seen = set()
    all_indices = set(range(len(points)))
    for a2 in a2s:
        basis = orthonormal_basis(points[list(a2)], tol)
        remaining = sorted(all_indices - set(a2))
        for i, j in antipodal_pairs(points[remaining], tol):
            i, j = remaining[i], remaining[j]
            vi, vj = points[i], points[j]
            if projection_residual_norm(vi, basis) < 1.0 - 1e-7:
                continue
            full = tuple(sorted((*a2, i, j)))
            if full not in seen and rank(points[list(full)], tol) == 3:
                seen.add(full)
                count += 1
    return count


def u1_residual_charge_bins(points: np.ndarray, a2: tuple[int, ...], a1_pair: tuple[int, int]) -> int:
    selected = points[list(a2) + list(a1_pair)]
    basis = orthonormal_basis(selected)
    # Null direction of the A2 + A1 span gives a rank-1 residual U(1)-like axis.
    _, _, vh = np.linalg.svd(basis)
    # This SVD is on a 3x4 basis; the null vector is the last row of Vh.
    axis = vh[-1]
    charges = points @ axis
    rounded = np.round(charges, 8)
    return len(set(float(x) for x in rounded))


def best_extension(points: np.ndarray, a2s: list[tuple[int, ...]]) -> tuple[tuple[int, ...], tuple[int, int]] | None:
    all_indices = set(range(len(points)))
    for a2 in a2s:
        basis = orthonormal_basis(points[list(a2)])
        remaining = sorted(all_indices - set(a2))
        for i, j in antipodal_pairs(points[remaining]):
            i, j = remaining[i], remaining[j]
            if projection_residual_norm(points[i], basis) > 1.0 - 1e-7:
                return a2, (i, j)
    return None


def run() -> list[ProbeResult]:
    roots = d4_roots()
    controls = [random_s3_points(24, SEED + i) for i in range(1, 31)]

    a2s = find_a2_subsystems(roots)
    control_a2_counts = [len(find_a2_subsystems(c, max_count=1)) for c in controls]
    control_a2 = float(np.median(control_a2_counts))

    extensions = count_a2_a1_extensions(roots, a2s)
    control_extensions = []
    for c in controls:
        ca2 = find_a2_subsystems(c, max_count=1)
        control_extensions.append(count_a2_a1_extensions(c, ca2) if ca2 else 0)
    control_ext = float(np.median(control_extensions))

    best = best_extension(roots, a2s)
    if best is None:
        bins = 999
    else:
        bins = u1_residual_charge_bins(roots, *best)
    control_bins = 24.0

    # A non-hand-labeling score: A2 exists, A1 extension exists, residual rank-1 axis exists.
    rank_score = 1.0 if a2s and extensions > 0 and bins < 24 else 0.0

    # Triality-neutrality sanity: D4 should have three outer legs in its Dynkin diagram.
    # We test this indirectly by counting A2 subsystems around each coordinate pair.
    coordinate_supports = []
    for a2 in a2s:
        support = tuple(np.where(np.any(np.abs(roots[list(a2)]) > 1e-8, axis=0))[0])
        coordinate_supports.append(support)
    support_variety = len(set(coordinate_supports))
    control_variety = 0.0

    return [
        ProbeResult(
            "MEB-002A",
            "algorithmic_A2_subsystem_count",
            float(len(a2s)),
            control_a2,
            "PASS" if len(a2s) > 0 and control_a2 == 0.0 else "MIXED",
            "An algorithm finds A2-like hexagonal root subsystems inside D4 without hand-labeling.",
        ),
        ProbeResult(
            "MEB-002B",
            "algorithmic_A2_plus_A1_extension_count",
            float(extensions),
            control_ext,
            "PASS" if extensions > 0 and control_ext == 0.0 else "MIXED",
            "Strict orthogonal A2 + A1 extension is not established when the extension count is zero.",
        ),
        ProbeResult(
            "MEB-002C",
            "residual_U1_like_charge_bins_lower_than_24",
            float(bins),
            control_bins,
            "PASS" if bins < 24 else "MIXED",
            "Residual U(1)-like bookkeeping is unavailable unless a strict A2 + A1 extension exists.",
        ),
        ProbeResult(
            "MEB-002D",
            "rank_coverage_score",
            rank_score,
            0.0,
            "PASS" if rank_score == 1.0 else "FAIL",
            "The strict rank-4 A2 + A1 + residual decomposition is not established by this probe.",
        ),
        ProbeResult(
            "MEB-002E",
            "support_variety",
            float(support_variety),
            control_variety,
            "PASS" if support_variety >= 3 else "MIXED",
            "Multiple coordinate supports appear, consistent with D4's high symmetry; this is not a Standard Model generation claim.",
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
        "# MEB-002 — D4 Representation Audit Probe",
        "",
        "## Status",
        "",
        "This is a mathematical scaffold probe, not physics evidence.",
        "",
        "It asks whether the 24-cell / D4 root system contains algorithmically discoverable A2 + A1 + rank-1-residual structure more cleanly than random 24-point controls.",
        "",
        "It does **not** derive SU(3) x SU(2) x U(1), Standard Model charges, chirality, hypercharge, generations, masses, particles, or matter.",
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
            "- D4 contains algorithmically discoverable A2-like hexagonal sub-root scaffolds.",
            "- The stricter A2 + A1 + rank-1-residual decomposition did **not** pass in this exact root-subsystem test.",
            "- This blocks the premature claim that D4 directly gives SU(3) x SU(2) x U(1)-like bookkeeping.",
            "- The result is still useful because it upgrades the A2/color-like scaffold while demoting the full Standard-Model-like mapping.",
            "",
            "## Next Test",
            "",
            "MEB-003 should test chirality and anomaly-like constraints:",
            "",
            "```text",
            "Can a D4-derived scaffold produce asymmetric left/right representation",
            "bookkeeping without manual sign choices, and does it obey any",
            "nontrivial cancellation law under controls?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim this derives the Standard Model.",
            "- Do not claim A2 is literally SU(3) color here.",
            "- Do not claim A1 is literally weak isospin here.",
            "- Do not claim the residual axis is hypercharge.",
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
