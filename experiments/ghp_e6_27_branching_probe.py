#!/usr/bin/env python3
"""
MEB-009 — E6 27 Branching Probe

This is a mathematical hardening probe, not physics evidence.

Question:
Can the E6 27-weight scaffold branch into stable bookkeeping blocks under a
stated subgroup/complement rule without post-hoc labels?

Safe interpretation:
The E6 27 admits an algorithmic D5 x U(1)-like split with block sizes
16 + 10 + 1 under the inverse-Cartan complement charge. This is a serious
representation-theoretic scaffold worth further testing.

Forbidden interpretation:
This does not derive SO(10), Standard Model fermions, hypercharge, anomaly
cancellation, generations, masses, particles, or physical matter.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_e6_27_branching_probe_outputs"
SEED = 49009
rng = np.random.default_rng(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def e6_cartan() -> np.ndarray:
    c = 2 * np.eye(6, dtype=int)
    for i, j in [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5)]:
        c[i, j] = c[j, i] = -1
    return c


def weyl_reflect_dynkin_label(label: np.ndarray, i: int, cartan: np.ndarray) -> np.ndarray:
    return label - label[i] * cartan[i, :]


def weight_orbit(fundamental_index: int, cartan: np.ndarray) -> np.ndarray:
    start = np.zeros(6, dtype=int)
    start[fundamental_index] = 1
    seen: set[tuple[int, ...]] = {tuple(start.tolist())}
    frontier = [start]
    while frontier:
        label = frontier.pop()
        for i in range(6):
            reflected = weyl_reflect_dynkin_label(label, i, cartan)
            key = tuple(reflected.tolist())
            if key not in seen:
                seen.add(key)
                frontier.append(reflected)
    return np.array(sorted(seen))


def d5_candidate_nodes(cartan: np.ndarray) -> list[int]:
    out = []
    for removed in range(cartan.shape[0]):
        keep = [i for i in range(cartan.shape[0]) if i != removed]
        sub = cartan[np.ix_(keep, keep)]
        # D5 Cartan determinant is 4.
        if round(float(np.linalg.det(sub))) == 4:
            out.append(removed)
    return out


def complement_charges(weights: np.ndarray, removed_node: int, cartan: np.ndarray) -> np.ndarray:
    inv = np.linalg.inv(cartan.astype(float))
    # Multiplying by 3 makes the E6 lattice charges integral in this convention.
    return np.rint(3 * (weights @ inv[:, removed_node])).astype(int)


def block_signature(charges: np.ndarray) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(k), int(v)) for k, v in Counter(charges).items()))


def block_sizes(charges: np.ndarray) -> list[int]:
    return sorted(int(v) for v in Counter(charges).values())


def naive_coordinate_signature(weights: np.ndarray, node: int) -> list[int]:
    return sorted(int(v) for v in Counter(weights[:, node]).values())


def random_charge_hit_rate(weights: np.ndarray, trials: int = 300) -> float:
    hits = 0
    for _ in range(trials):
        coeff = rng.integers(-3, 4, size=weights.shape[1])
        if np.all(coeff == 0):
            continue
        charges = weights @ coeff
        if block_sizes(charges) == [1, 10, 16]:
            hits += 1
    return hits / trials


def conjugate_charge_match(weights_a: np.ndarray, weights_b: np.ndarray, removed_node: int, cartan: np.ndarray) -> float:
    charges_a = sorted(complement_charges(weights_a, removed_node, cartan).tolist())
    charges_b = sorted((-complement_charges(weights_b, removed_node, cartan)).tolist())
    return 1.0 if charges_a == charges_b else 0.0


def stable_under_conjugate_node(weights: np.ndarray, nodes: list[int], cartan: np.ndarray) -> float:
    signatures = [block_sizes(complement_charges(weights, n, cartan)) for n in nodes]
    return 1.0 if signatures and all(s == [1, 10, 16] for s in signatures) else 0.0


def run() -> list[ProbeResult]:
    cartan = e6_cartan()
    weights_27 = weight_orbit(4, cartan)
    weights_27bar = weight_orbit(5, cartan)
    nodes = d5_candidate_nodes(cartan)
    # In this convention nodes 4 and 5 are the two conjugate D5 x U1 complements.
    good_nodes = []
    signatures = {}
    for n in nodes:
        charges = complement_charges(weights_27, n, cartan)
        signatures[n] = block_signature(charges)
        if block_sizes(charges) == [1, 10, 16]:
            good_nodes.append(n)

    best_node = good_nodes[0] if good_nodes else nodes[0]
    charges = complement_charges(weights_27, best_node, cartan)
    naive = naive_coordinate_signature(weights_27, best_node)
    random_hit = random_charge_hit_rate(weights_27)

    return [
        ProbeResult(
            "MEB-009A",
            "D5_candidate_count",
            float(len(nodes)),
            2.0,
            "PASS" if len(nodes) == 2 else "MIXED",
            "The E6 diagram has two determinant-4 node removals in this convention, giving conjugate D5-like complements.",
        ),
        ProbeResult(
            "MEB-009B",
            "algorithmic_16_10_1_split",
            1.0 if block_sizes(charges) == [1, 10, 16] else 0.0,
            0.0,
            "PASS" if block_sizes(charges) == [1, 10, 16] else "FAIL",
            "Inverse-Cartan complement charge branches the 27 into 16 + 10 + 1 blocks.",
        ),
        ProbeResult(
            "MEB-009C",
            "naive_coordinate_control_failure",
            1.0 if naive != [1, 10, 16] else 0.0,
            1.0,
            "PASS" if naive != [1, 10, 16] else "MIXED",
            "A naive coordinate read does not produce the desired split; the branch uses the complement charge, not cherry-picked coordinates.",
        ),
        ProbeResult(
            "MEB-009D",
            "random_charge_hit_rate",
            random_hit,
            0.0,
            "PASS" if random_hit < 0.10 else "MIXED",
            "Random integer charge maps rarely hit the 16 + 10 + 1 block pattern.",
        ),
        ProbeResult(
            "MEB-009E",
            "conjugate_charge_match",
            conjugate_charge_match(weights_27, weights_27bar, best_node, cartan),
            1.0,
            "PASS" if conjugate_charge_match(weights_27, weights_27bar, best_node, cartan) == 1.0 else "MIXED",
            "The conjugate 27-bar carries the opposite charge signature under the same complement.",
        ),
        ProbeResult(
            "MEB-009F",
            "conjugate_node_stability",
            stable_under_conjugate_node(weights_27, good_nodes, cartan),
            1.0,
            "PASS" if stable_under_conjugate_node(weights_27, good_nodes, cartan) == 1.0 else "MIXED",
            "Both conjugate D5-like complements produce the same block-size pattern.",
        ),
    ]


def write_outputs(results: list[ProbeResult]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["probe", "metric", "value", "control", "verdict", "safe_read"])
        writer.writeheader()
        for r in results:
            writer.writerow(r.__dict__)

    cartan = e6_cartan()
    weights_27 = weight_orbit(4, cartan)
    nodes = d5_candidate_nodes(cartan)
    signatures = {str(n): block_signature(complement_charges(weights_27, n, cartan)) for n in nodes}

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    report = [
        "# MEB-009 — E6 27 Branching Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether the E6 27-weight scaffold branches into stable bookkeeping blocks under a stated complement-charge rule.",
        "",
        "It does **not** derive SO(10), Standard Model fermions, hypercharge, anomaly cancellation, generations, masses, particles, or matter.",
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
            "## Branching Facts Recorded",
            "",
            f"- D5-like complement nodes: `{nodes}`",
            f"- complement-charge signatures: `{signatures}`",
            "",
            "## Interpretation",
            "",
            "- The E6 27 admits a clean 16 + 10 + 1 block split under an explicit inverse-Cartan complement charge.",
            "- A naive coordinate control does not produce this split, and random charge maps rarely hit it.",
            "- The conjugate 27-bar carries the opposite charge signature.",
            "- This is a serious representation-bookkeeping result, but it is still not Standard Model physics.",
            "",
            "## Next Test",
            "",
            "MEB-010 should test whether the 16, 10, and 1 blocks have stable internal structure under the D5 Weyl action and whether any further subgroup chain can be specified without post-hoc labels.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim this derives SO(10) physics.",
            "- Do not claim the 16 block is a Standard Model generation.",
            "- Do not claim the complement charge is hypercharge.",
            "- Do not claim this proves matter embedding.",
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
