#!/usr/bin/env python3
"""
MEB-001 — 24-Cell Matter-Embedding Scaffold Probe

This is a mathematical scaffold probe, not physics evidence.

Question:
Can the 24-cell / D4 root system serve as a non-arbitrary discrete
label alphabet for boundary-shear events better than generic 24-point
controls?

Forbidden conclusion:
Do not infer Standard Model charges, particles, matter, consciousness,
or a closed GHP matter embedding from this probe.
"""

from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np


SEED = 24024
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_24cell_matter_embedding_scaffold_probe_outputs"
rng = np.random.default_rng(SEED)
random.seed(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def d4_roots() -> np.ndarray:
    """24 roots of D4: all permutations of (±1, ±1, 0, 0)."""
    roots = []
    for i in range(4):
        for j in range(i + 1, 4):
            for si in (-1.0, 1.0):
                for sj in (-1.0, 1.0):
                    v = np.zeros(4)
                    v[i] = si
                    v[j] = sj
                    roots.append(v)
    return np.array(roots, dtype=float)


def normalize_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def random_s3_points(n: int, seed: int) -> np.ndarray:
    local = np.random.default_rng(seed)
    x = local.normal(size=(n, 4))
    return normalize_rows(x)


def nearest_indices(points: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    # Unit vectors: maximize dot product.
    if not np.isfinite(points).all() or not np.isfinite(codebook).all():
        raise ValueError("non-finite point/codebook in nearest_indices")
    dots = np.einsum("ij,kj->ik", points, codebook)
    return np.argmax(dots, axis=1)


def pairwise_distances(x: np.ndarray) -> np.ndarray:
    diff = x[:, None, :] - x[None, :, :]
    d = np.linalg.norm(diff, axis=-1)
    return d[np.triu_indices(len(x), k=1)]


def covariance_isotropy_score(codebook: np.ndarray) -> float:
    cov = codebook.T @ codebook / len(codebook)
    target = np.eye(4) / 4.0
    return float(np.linalg.norm(cov - target, ord="fro"))


def min_distance_score(codebook: np.ndarray) -> float:
    return float(np.min(pairwise_distances(codebook)))


def stability_score(codebook: np.ndarray, clean: np.ndarray, sigma: float = 0.18, trials: int = 64) -> float:
    stable = 0
    total = 0
    clean_labels = nearest_indices(clean, codebook)
    for _ in range(trials):
        noisy = normalize_rows(clean + rng.normal(scale=sigma, size=clean.shape))
        noisy_labels = nearest_indices(noisy, codebook)
        stable += int(np.sum(noisy_labels == clean_labels))
        total += len(clean)
    return stable / total


def equivariance_score(codebook: np.ndarray) -> float:
    """
    Measures closure under signed coordinate permutations.
    D4 roots should map exactly back onto themselves under this finite symmetry family.
    Generic random controls should not.
    """
    rounded = {tuple(np.round(row, 8)) for row in codebook}
    hits = 0
    total = 0
    perms = [
        (0, 1, 2, 3),
        (1, 0, 2, 3),
        (2, 1, 0, 3),
        (3, 1, 2, 0),
        (0, 2, 1, 3),
        (0, 3, 2, 1),
    ]
    signs = [
        np.array([1, 1, 1, 1]),
        np.array([-1, 1, 1, 1]),
        np.array([1, -1, 1, 1]),
        np.array([1, 1, -1, 1]),
        np.array([1, 1, 1, -1]),
        np.array([-1, -1, 1, 1]),
        np.array([1, -1, -1, 1]),
        np.array([1, 1, -1, -1]),
        np.array([-1, 1, -1, 1]),
        np.array([-1, 1, 1, -1]),
    ]
    for p in perms:
        for s in signs:
            transformed = codebook[:, list(p)] * s
            for row in transformed:
                total += 1
                if tuple(np.round(row, 8)) in rounded:
                    hits += 1
    return hits / total


def quantization_error(points: np.ndarray, codebook: np.ndarray) -> float:
    if not np.isfinite(points).all() or not np.isfinite(codebook).all():
        raise ValueError("non-finite point/codebook in quantization_error")
    dots = np.einsum("ij,kj->ik", points, codebook)
    best = np.max(dots, axis=1)
    # Squared Euclidean distance between unit vectors = 2 - 2 dot.
    return float(np.mean(2.0 - 2.0 * best))


def local_shear_samples(clean_roots: np.ndarray, n_per_root: int = 80, sigma: float = 0.22) -> np.ndarray:
    chunks = []
    for root in clean_roots:
        samples = root + rng.normal(scale=sigma, size=(n_per_root, 4))
        chunks.append(samples)
    return normalize_rows(np.vstack(chunks))


def run() -> list[ProbeResult]:
    raw_roots = d4_roots()
    roots = normalize_rows(raw_roots)
    controls = [random_s3_points(24, SEED + i) for i in range(1, 101)]

    # MEB-001A: exact D4 construction sanity.
    norms_ok = np.allclose(np.linalg.norm(raw_roots, axis=1), math.sqrt(2.0))
    unique_ok = len({tuple(row) for row in raw_roots}) == 24
    dot_values = sorted(set(np.round((raw_roots @ raw_roots.T).flatten(), 8)))
    dot_ok = dot_values == [-2.0, -1.0, 0.0, 1.0, 2.0]
    integrity = 1.0 if norms_ok and unique_ok and dot_ok else 0.0

    # Controls cannot pass exact D4 integrality by construction.
    control_integrity = 0.0

    # MEB-001B: isotropic second moment.
    iso = covariance_isotropy_score(roots)
    control_iso = float(np.median([covariance_isotropy_score(c) for c in controls]))

    # MEB-001C: packing / separation.
    sep = min_distance_score(roots)
    control_sep = float(np.median([min_distance_score(c) for c in controls]))

    # MEB-001D: stable labels under noisy local shear.
    stability = stability_score(roots, roots)
    control_stability = float(np.median([stability_score(c, roots) for c in controls[:25]]))

    # MEB-001E: symmetry closure.
    equiv = equivariance_score(roots)
    control_equiv = float(np.median([equivariance_score(c) for c in controls[:25]]))

    # MEB-001F: quantization of D4-near shear events.
    samples = local_shear_samples(roots)
    qerr = quantization_error(samples, roots)
    control_qerr = float(np.median([quantization_error(samples, c) for c in controls]))

    return [
        ProbeResult(
            "MEB-001A",
            "D4 root integrity",
            integrity,
            control_integrity,
            "PASS" if integrity == 1.0 else "FAIL",
            "The 24-cell codebook is exactly the D4 root system, not an arbitrary list of 24 labels.",
        ),
        ProbeResult(
            "MEB-001B",
            "isotropy_error_lower_is_better",
            iso,
            control_iso,
            "PASS" if iso < 1e-12 and iso < control_iso * 0.05 else "MIXED",
            "The 24-cell is perfectly balanced in four dimensions, unlike generic random 24-point controls.",
        ),
        ProbeResult(
            "MEB-001C",
            "minimum_separation_higher_is_better",
            sep,
            control_sep,
            "PASS" if sep > control_sep * 1.25 else "MIXED",
            "The 24-cell gives a cleaner separated label alphabet than typical random 24-point controls.",
        ),
        ProbeResult(
            "MEB-001D",
            "noisy_shear_label_stability",
            stability,
            control_stability,
            "PASS" if stability > 0.88 and stability > control_stability + 0.20 else "MIXED",
            "D4-root labels remain stable under local perturbation better than generic controls.",
        ),
        ProbeResult(
            "MEB-001E",
            "signed_permutation_equivariance",
            equiv,
            control_equiv,
            "PASS" if equiv == 1.0 and control_equiv < 0.05 else "MIXED",
            "The 24-cell has exact signed-coordinate symmetry closure; random controls do not.",
        ),
        ProbeResult(
            "MEB-001F",
            "quantization_error_lower_is_better",
            qerr,
            control_qerr,
            "PASS" if qerr < control_qerr * 0.70 else "MIXED",
            "D4-near synthetic shear events quantize more cleanly to the 24-cell than to generic codebooks.",
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
        "# MEB-001 — 24-Cell Matter-Embedding Scaffold Probe",
        "",
        "## Status",
        "",
        "This is a mathematical scaffold probe, not physics evidence.",
        "",
        "It tests whether the 24-cell / D4 root system is a cleaner discrete label alphabet for boundary-shear events than generic 24-point controls.",
        "",
        "It does **not** derive matter, gauge charge, the Standard Model, chirality, hypercharge, masses, or a GHP matter embedding.",
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
            "- The 24-cell / D4 roots form a highly symmetric, non-arbitrary 24-label scaffold in four dimensions.",
            "- This is useful for the GHP Matter Embedding Gap as a candidate *label alphabet* for boundary-shear events.",
            "- The scaffold beats generic 24-point controls on isotropy, separation, perturbation stability, symmetry closure, and quantization of D4-near synthetic shear.",
            "- This still does not identify the labels with Standard Model particles or charges.",
            "",
            "## Safe Next Step",
            "",
            "Build a stricter `MEB-002` representation audit:",
            "",
            "```text",
            "Can any non-arbitrary projection of D4 / SO(8) triality recover",
            "SU(3) x SU(2) x U(1)-like bookkeeping without hand-labeling?",
            "```",
            "",
            "Failure to recover chirality, hypercharge, anomaly cancellation, or representation structure should demote the matter-embedding branch back to symbolic scaffold.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim the 24-cell derives the Standard Model.",
            "- Do not claim D4 roots are physical gauge charges.",
            "- Do not claim matter is boundary exhaust.",
            "- Do not claim Algorithmic Sonoluminescence writes matter into existence.",
            "- Do not claim this closes the Matter Embedding Gap.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")

    meta = {
        "seed": SEED,
        "pass_count": pass_count,
        "total": len(results),
        "forbidden_claims": [
            "Standard Model derivation",
            "gauge charge proof",
            "matter proof",
            "consciousness proof",
            "GHP physics proof",
        ],
    }
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    results = run()
    write_outputs(results)
    print(f"PASS {sum(1 for r in results if r.verdict == 'PASS')}/{len(results)}")
    for r in results:
        print(f"{r.probe}: {r.verdict} value={r.value:.6f} control={r.control:.6f}")
