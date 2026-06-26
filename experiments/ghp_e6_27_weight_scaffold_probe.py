#!/usr/bin/env python3
"""
MEB-008 — E6 27-Weight Scaffold Probe

This is a mathematical hardening probe, not physics evidence.

Question:
After MEB-007 showed that E6 roots alone remain too symmetric, does the
E6 minuscule 27-weight orbit provide a cleaner representation-level scaffold
for matter-bookkeeping tests?

Safe interpretation:
The E6 27 and its conjugate 27-bar form a real non-self-conjugate
representation-level scaffold. This is closer to the kind of object matter
embedding programs care about than roots alone.

Forbidden interpretation:
This does not derive Standard Model fermions, charges, generations, masses,
Yukawas, anomaly cancellation, hypercharge, particles, or physical matter.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_e6_27_weight_scaffold_probe_outputs"
SEED = 48008


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
    """
    Dynkin-label reflection. If label_j=<lambda, alpha_j^vee>,
    s_i(lambda)=lambda-label_i alpha_i, and alpha_i has Dynkin labels C[i,*].
    """
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


def inner_weights(a: np.ndarray, b: np.ndarray, inv_cartan: np.ndarray) -> float:
    return float(a @ inv_cartan @ b)


def non_self_conjugacy_score(orbit: np.ndarray) -> float:
    keys = {tuple(w.tolist()) for w in orbit}
    missing_negatives = sum(1 for w in orbit if tuple((-w).tolist()) not in keys)
    return missing_negatives / len(orbit)


def conjugate_pair_score(orbit_a: np.ndarray, orbit_b: np.ndarray) -> float:
    keys_b = {tuple(w.tolist()) for w in orbit_b}
    hits = sum(1 for w in orbit_a if tuple((-w).tolist()) in keys_b)
    return hits / len(orbit_a)


def inner_product_signature(orbit: np.ndarray, inv_cartan: np.ndarray) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for a in orbit:
        for b in orbit:
            counts[f"{inner_weights(a, b, inv_cartan):.6f}"] += 1
    return dict(sorted(counts.items()))


def signature_complexity(signature: dict[str, int]) -> int:
    return len(signature)


def zero_sum_score(orbit: np.ndarray) -> float:
    return 1.0 if np.all(np.sum(orbit, axis=0) == 0) else 0.0


def run() -> list[ProbeResult]:
    cartan = e6_cartan()
    inv_cartan = np.linalg.inv(cartan.astype(float))

    orbit_27 = weight_orbit(4, cartan)
    orbit_27bar = weight_orbit(5, cartan)
    orbit_non_min = weight_orbit(3, cartan)

    sig_27 = inner_product_signature(orbit_27, inv_cartan)
    norms = sorted({round(inner_weights(w, w, inv_cartan), 6) for w in orbit_27})

    return [
        ProbeResult(
            "MEB-008A",
            "minuscule_orbit_count",
            float(len(orbit_27)),
            27.0,
            "PASS" if len(orbit_27) == 27 and len(orbit_27bar) == 27 else "FAIL",
            "E6 has two 27-weight minuscule orbits in this convention.",
        ),
        ProbeResult(
            "MEB-008B",
            "non_self_conjugacy",
            non_self_conjugacy_score(orbit_27),
            1.0,
            "PASS" if non_self_conjugacy_score(orbit_27) == 1.0 else "MIXED",
            "The 27 orbit is not self-conjugate; its negatives are not inside the same orbit.",
        ),
        ProbeResult(
            "MEB-008C",
            "conjugate_partner_match",
            conjugate_pair_score(orbit_27, orbit_27bar),
            1.0,
            "PASS" if conjugate_pair_score(orbit_27, orbit_27bar) == 1.0 else "MIXED",
            "The second 27-weight orbit supplies the conjugate partner, so the pair is balanced.",
        ),
        ProbeResult(
            "MEB-008D",
            "zero_sum_balance",
            zero_sum_score(orbit_27),
            1.0,
            "PASS" if zero_sum_score(orbit_27) == 1.0 else "MIXED",
            "The 27 orbit has zero total weight, preserving a basic balance constraint.",
        ),
        ProbeResult(
            "MEB-008E",
            "uniform_norm_count",
            float(len(norms)),
            1.0,
            "PASS" if len(norms) == 1 else "MIXED",
            "The 27 orbit has uniform weight norm, consistent with a clean Weyl orbit.",
        ),
        ProbeResult(
            "MEB-008F",
            "signature_complexity_vs_nonminuscule",
            float(signature_complexity(sig_27)),
            float(len(orbit_non_min)),
            "PASS" if signature_complexity(sig_27) <= 3 and len(orbit_non_min) > 27 else "MIXED",
            "The 27 orbit has a compact inner-product signature compared with a larger non-minuscule orbit.",
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
    inv_cartan = np.linalg.inv(cartan.astype(float))
    orbit_27 = weight_orbit(4, cartan)
    orbit_27bar = weight_orbit(5, cartan)
    sig_27 = inner_product_signature(orbit_27, inv_cartan)

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    report = [
        "# MEB-008 — E6 27-Weight Scaffold Probe",
        "",
        "## Status",
        "",
        "This is a mathematical hardening probe, not physics evidence.",
        "",
        "It asks whether the E6 27-weight orbit is a better matter-bookkeeping scaffold than roots alone.",
        "",
        "It does **not** derive Standard Model fermions, charges, generations, masses, hypercharge, anomaly cancellation, particles, or matter.",
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
            "## Representation Facts Recorded",
            "",
            f"- `27` orbit size: `{len(orbit_27)}`",
            f"- conjugate orbit size: `{len(orbit_27bar)}`",
            f"- inner-product signature: `{sig_27}`",
            "",
            "## Interpretation",
            "",
            "- E6 roots alone were too symmetric, but the E6 27-weight orbit is representation-level structure.",
            "- The 27 is non-self-conjugate and has a conjugate 27-bar partner, which is the first clean chiral-bookkeeping-shaped object in this matter lane.",
            "- This is still only a scaffold. It does not identify Standard Model fields, hypercharge, generations, masses, interactions, or anomaly cancellation.",
            "- The next serious test must be branching: can the 27 be decomposed under a specified subgroup chain without hand-labeling?",
            "",
            "## Next Test",
            "",
            "MEB-009 should test explicit branching controls:",
            "",
            "```text",
            "Can the E6 27 be branched through a stated subgroup chain",
            "into stable bookkeeping blocks without post-hoc labels?",
            "```",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim the E6 27 is the Standard Model.",
            "- Do not claim the 27 weights are particles.",
            "- Do not claim non-self-conjugacy is physical chirality.",
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
