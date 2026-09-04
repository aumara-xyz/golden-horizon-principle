#!/usr/bin/env python3
"""Exact finite-dimensional checks for the mirror-inertia lemma."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
TOL = 1e-12


def mirror_matrix(fixed, pairs):
    size = fixed + 2 * pairs
    j = np.zeros((size, size), dtype=float)
    for i in range(fixed):
        j[i, i] = 1.0
    for k in range(pairs):
        a, b = fixed + 2 * k, fixed + 2 * k + 1
        j[a, b] = j[b, a] = 1.0
    return j


def sector_bases(fixed, pairs):
    size = fixed + 2 * pairs
    even = []
    odd = []
    for i in range(fixed):
        v = np.zeros(size); v[i] = 1.0; even.append(v)
    for k in range(pairs):
        a, b = fixed + 2 * k, fixed + 2 * k + 1
        ep = np.zeros(size); ep[a] = ep[b] = 1.0 / np.sqrt(2.0); even.append(ep)
        em = np.zeros(size); em[a] = 1.0 / np.sqrt(2.0); em[b] = -1.0 / np.sqrt(2.0); odd.append(em)
    e = np.column_stack(even) if even else np.zeros((size, 0))
    o = np.column_stack(odd) if odd else np.zeros((size, 0))
    return e, o


def inertia(values):
    return {
        "positive": int(np.sum(values > TOL)),
        "zero": int(np.sum(np.abs(values) <= TOL)),
        "negative": int(np.sum(values < -TOL)),
    }


def analyze(fixed, pairs):
    j = mirror_matrix(fixed, pairs)
    ev = np.linalg.eigvalsh(j) if len(j) else np.asarray([])
    e, o = sector_bases(fixed, pairs)
    even_form = np.einsum("ia,ij,jb->ab", e, j, e) if e.shape[1] else np.zeros((0, 0))
    odd_form = np.einsum("ia,ij,jb->ab", o, j, o) if o.shape[1] else np.zeros((0, 0))
    even_ev = np.linalg.eigvalsh(even_form) if e.shape[1] else np.asarray([])
    odd_ev = np.linalg.eigvalsh(odd_form) if o.shape[1] else np.asarray([])
    return {
        "fixed_points": fixed, "two_cycles": pairs, "dimension": len(j),
        "inertia": inertia(ev),
        "even_sector_inertia": inertia(even_ev),
        "odd_sector_inertia": inertia(odd_ev),
        "minimum_eigenvalue": float(ev.min()) if len(ev) else None,
        "involution_residual": float(np.linalg.norm(np.einsum("ik,kj->ij", j, j) - np.eye(len(j)), ord=2)) if len(j) else 0.0,
    }


def main():
    OUT.mkdir(exist_ok=True)
    grid = [analyze(f, p) for f in range(9) for p in range(9) if f + p > 0]
    formula_ok = all(
        row["inertia"] == {"positive": row["fixed_points"] + row["two_cycles"], "zero": 0, "negative": row["two_cycles"]}
        for row in grid
    )
    even_hides = all(row["even_sector_inertia"]["negative"] == 0 for row in grid)
    odd_detects = all(row["odd_sector_inertia"]["negative"] == row["two_cycles"] for row in grid)
    involution_ok = max(row["involution_residual"] for row in grid) < TOL

    regularizers = []
    base = mirror_matrix(3, 4)
    for c in (0.5, 1.0, 1.5):
        ev = np.linalg.eigvalsh(base + c * np.eye(len(base)))
        regularizers.append({"c": c, "minimum_eigenvalue": float(ev.min()), "positive_semidefinite": bool(ev.min() >= -TOL)})
    masking_exact = [x["positive_semidefinite"] for x in regularizers] == [False, True, True]

    pair = mirror_matrix(0, 1)
    even_observer = np.asarray([1.0, 1.0]) / np.sqrt(2.0)
    odd_observer = np.asarray([1.0, -1.0]) / np.sqrt(2.0)
    q_even = float(np.einsum("i,ij,j", even_observer, pair, even_observer))
    q_odd = float(np.einsum("i,ij,j", odd_observer, pair, odd_observer))

    result = {
        "test_id": "MIRROR-INERTIA-LEMMA-v0",
        "configurations_checked": len(grid),
        "maximum_involution_residual": max(row["involution_residual"] for row in grid),
        "inertia_formula_exact_on_grid": formula_ok,
        "even_restriction_hides_all_negative_directions": even_hides,
        "odd_sector_detects_every_two_cycle": odd_detects,
        "single_pair": {"Q_even": q_even, "Q_odd": q_odd, "matrix": pair.tolist()},
        "regularizer_control_fixed_points_3_two_cycles_4": regularizers,
        "regularizer_threshold_exact_on_test": masking_exact,
        "grid": grid,
        "verdict": {
            "finite_mirror_inertia_lemma": "MEASURED" if formula_ok and even_hides and odd_detects and involution_ok else "UNVERIFIED",
            "finite_regularizer_warning": "MEASURED" if masking_exact else "UNVERIFIED",
            "prime_side_infinite_positivity": "UNVERIFIED",
            "RH": "UNVERIFIED",
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    report = [
        "# MIRROR-INERTIA-LEMMA v0 — results", "",
        "For observer amplitudes indexed by a finite mirror-invariant set, the pairing is `Q_J(a)=<a,Ja>`.", "",
        "| Check | Result | Status |", "|---|---:|---|",
        f"| Configurations `(fixed,two-cycles)` checked | {len(grid)} | control grid |",
        f"| Maximum `||J^2-I||` | {result['maximum_involution_residual']:.1e} | MEASURED |",
        f"| Inertia formula `(+,0,-)=(f+p,0,p)` | {formula_ok} | MEASURED |",
        f"| Single-pair even observer | Q={q_even:.1f} | positive |",
        f"| Single-pair odd observer | Q={q_odd:.1f} | negative witness |",
        f"| Even-only restriction hides all negatives | {even_hides} | MEASURED warning |",
        f"| Every two-cycle detected in odd sector | {odd_detects} | MEASURED |", "",
        "## Exact block calculation", "",
        "A mirror-fixed point contributes `[1]`. An off-center mirror pair contributes", "",
        "```text", "M = [[0, 1],", "     [1, 0]].", "```", "",
        "Its normalized even and odd observer vectors are `(1,1)/sqrt(2)` and `(1,-1)/sqrt(2)`, with energies `+1` and `-1`. Therefore each off-center pair creates exactly one negative direction.", "",
        "## Regularizer control", "",
        "| Added `cI` | Minimum eigenvalue | PSD? |", "|---:|---:|---|",
        *[f"| {x['c']:.1f} | {x['minimum_eigenvalue']:.1f} | {x['positive_semidefinite']} |" for x in regularizers], "",
        "## Prediction ledger", "",
        "| Prediction | Outcome |", "|---|---|",
        f"| Fixed point contributes one positive direction | {'MATCH' if formula_ok else 'FAILED'} |",
        f"| Two-cycle contributes one positive and one negative direction | {'MATCH' if formula_ok else 'FAILED'} |",
        f"| Even-only observers hide the negative direction | {'MATCH' if even_hides else 'FAILED'} |",
        f"| `cI` masks negativity exactly at `c>=1` | {'MATCH' if masking_exact else 'FAILED'} |",
        "| Prime-side infinite positivity remains unresolved | MATCH |", "",
        "## Honest paragraph", "",
        "This is the precise algebra behind the mirror picture. The critical line is the fixed set of `J(s)=1-conj(s)`: fixed zeros give positive square blocks, while every off-line mirror pair carries a mirror-odd negative direction. This does not prove RH, because the computation indexed hypothetical zero locations. Weil's criterion moves the same question to admissible test functions and the prime-side explicit formula. The remaining proof obligation is to show that the actual infinite prime-side form is nonnegative for every observer without assuming where the zeros are. Restricting observers to the even sector or adding a numerical diagonal shift can conceal the exact negative witness.", "",
        "See `MIRROR_INERTIA_LEMMA.md` for the proof and scope.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
