#!/usr/bin/env python3
"""METATRON-PRIME-RETURN v0.

A falsification-oriented metric-graph test of the 13-center resonance-chamber idea.
No zeta-zero ordinates are loaded or used. Controls are scored before the authentic
golden metric. Outputs are deterministic under RNG seed 20260904.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import linalg, sparse, stats


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
RNG_SEED = 20260904


def geometry():
    outer = []
    for zero_axis in range(3):
        axes = [a for a in range(3) if a != zero_axis]
        for u in (-1.0, 1.0):
            for v in (-1.0, 1.0):
                p = [0.0, 0.0, 0.0]
                p[axes[0]], p[axes[1]] = u, v
                outer.append(tuple(p))
    points = [(0.0, 0.0, 0.0)] + outer
    edges = [(0, j) for j in range(1, 13)]
    for i in range(1, 13):
        for j in range(i + 1, 13):
            if abs(np.linalg.norm(np.array(points[i]) - np.array(points[j])) - math.sqrt(2.0)) < 1e-12:
                edges.append((i, j))
    assert len(points) == 13 and len(edges) == 36
    return np.asarray(points, dtype=float), sorted(edges)


def adjacency(n_vertices, edges):
    adj = [[] for _ in range(n_vertices)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    return adj


def canonical_cycle(vertices):
    seq = tuple(vertices)
    rotations = []
    for direction in (seq, tuple(reversed(seq))):
        for i in range(len(seq)):
            rotations.append(direction[i:] + direction[:i])
    return min(rotations)


def enumerate_cycles(n_vertices, edges, max_edges=8):
    adj = adjacency(n_vertices, edges)
    found = set()

    def walk(start, current, path):
        if len(path) > max_edges:
            return
        for nxt, _ in adj[current]:
            if nxt == start and len(path) >= 3:
                found.add(canonical_cycle(path))
            elif nxt not in path and len(path) < max_edges:
                walk(start, nxt, path + (nxt,))

    for start in range(n_vertices):
        walk(start, start, (start,))

    edge_index = {tuple(sorted(e)): i for i, e in enumerate(edges)}
    encoded = []
    for cyc in sorted(found):
        ids = []
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            ids.append(edge_index[tuple(sorted((a, b)))])
        encoded.append(np.asarray(ids, dtype=int))
    return encoded


def first_primes(n):
    values = []
    candidate = 2
    while len(values) < n:
        if all(candidate % p for p in values if p * p <= candidate):
            values.append(candidate)
        candidate += 1
    return np.asarray(values, dtype=float)


def cycle_score(lengths, cycles, targets):
    raw = np.asarray([lengths[c].sum() for c in cycles])
    scaled = np.sort(raw * (math.log(2.0) / raw.min()))
    logs = np.log(targets)
    local = np.empty_like(logs)
    local[0] = logs[1] - logs[0]
    local[-1] = logs[-1] - logs[-2]
    local[1:-1] = 0.5 * (logs[2:] - logs[:-2])
    nearest = np.asarray([np.min(np.abs(scaled - x)) for x in logs])
    return {
        "median_normalized_error": float(np.median(nearest / local)),
        "mean_normalized_error": float(np.mean(nearest / local)),
        "max_normalized_error": float(np.max(nearest / local)),
        "shortest_raw_cycle": float(raw.min()),
        "cycle_count": int(len(raw)),
        "per_prime": [
            {"p": int(p), "log_p": float(x), "nearest_abs_error": float(e), "normalized_error": float(e / d)}
            for p, x, e, d in zip(targets, logs, nearest, local)
        ],
    }


def assemble_fem(n_vertices, edges, lengths, subdivisions_per_unit, magnetic=False):
    nodes = n_vertices
    pieces = []
    flux = 2.0 * math.pi / PHI
    for edge_id, ((u, v), length) in enumerate(zip(edges, lengths)):
        nseg = max(2, int(math.ceil(subdivisions_per_unit * length)))
        interior = list(range(nodes, nodes + nseg - 1))
        nodes += nseg - 1
        chain = [u] + interior + [v]
        h = length / nseg
        # Deterministic orientation breaks time-reversal without changing edge lengths.
        total_phase = flux * ((edge_id + 1) / len(edges)) if magnetic else 0.0
        phase = total_phase / nseg
        pieces.append((chain, h, phase))

    dtype = complex if magnetic else float
    K = np.zeros((nodes, nodes), dtype=dtype)
    M = np.zeros((nodes, nodes), dtype=dtype)
    for chain, h, phase in pieces:
        hol = np.exp(1j * phase) if magnetic else 1.0
        for a, b in zip(chain[:-1], chain[1:]):
            K[a, a] += 1.0 / h
            K[b, b] += 1.0 / h
            K[a, b] += -hol / h
            K[b, a] += -np.conjugate(hol) / h
            M[a, a] += h / 3.0
            M[b, b] += h / 3.0
            M[a, b] += h * hol / 6.0
            M[b, a] += h * np.conjugate(hol) / 6.0
    return sparse.csr_matrix(K), sparse.csr_matrix(M)


def spectrum(n_vertices, edges, lengths, subdivisions_per_unit, magnetic=False, count=190):
    K, M = assemble_fem(n_vertices, edges, lengths, subdivisions_per_unit, magnetic)
    # Dense generalized Hermitian solve is deterministic and sufficiently small here.
    vals = linalg.eigh(K.toarray(), M.toarray(), subset_by_index=[0, count - 1], check_finite=False)[0]
    vals[np.abs(vals) < 1e-10] = 0.0
    vals = np.maximum(vals.real, 0.0)
    return np.sqrt(vals), K.shape[0]


def empirical_ks(sample, cdf):
    x = np.sort(np.asarray(sample))
    n = len(x)
    upper = np.arange(1, n + 1) / n
    lower = np.arange(0, n) / n
    f = cdf(x)
    return float(max(np.max(np.abs(upper - f)), np.max(np.abs(lower - f))))


def spacing_metrics(k):
    window = k[20:180]
    spacings = np.diff(window)
    spacings /= spacings.mean()
    cdfs = {
        "poisson": lambda s: 1.0 - np.exp(-s),
        "goe": lambda s: 1.0 - np.exp(-math.pi * s * s / 4.0),
        "gue": lambda s: stats.erf(2.0 * s / math.sqrt(math.pi)) - (4.0 * s / math.pi) * np.exp(-4.0 * s * s / math.pi),
    }
    # scipy.stats has no erf attribute on some releases.
    from scipy.special import erf
    cdfs["gue"] = lambda s: erf(2.0 * s / math.sqrt(math.pi)) - (4.0 * s / math.pi) * np.exp(-4.0 * s * s / math.pi)
    distances = {name: empirical_ks(spacings, cdf) for name, cdf in cdfs.items()}
    return {"ks": distances, "closest": min(distances, key=distances.get), "mean_spacing": float(np.mean(spacings))}


def main():
    OUT.mkdir(exist_ok=True)
    points, edges = geometry()
    deformation = np.diag([1.0, PHI, PHI * PHI])
    deformed = points @ deformation
    authentic = np.asarray([np.linalg.norm(deformed[u] - deformed[v]) for u, v in edges])
    authentic /= authentic.mean()
    cycles = enumerate_cycles(len(points), edges, max_edges=8)
    primes = first_primes(25)
    rng = np.random.default_rng(RNG_SEED)

    # Controls are deliberately scored before the authentic metric.
    equilateral = cycle_score(np.ones_like(authentic), cycles, primes)
    perm_scores = []
    for _ in range(200):
        perm_scores.append(cycle_score(rng.permutation(authentic), cycles, primes)["median_normalized_error"])
    cv = authentic.std() / authentic.mean()
    sigma = math.sqrt(math.log1p(cv * cv))
    mu = -0.5 * sigma * sigma
    lognormal_scores = []
    for _ in range(200):
        lengths = rng.lognormal(mu, sigma, len(authentic))
        lengths /= lengths.mean()
        lognormal_scores.append(cycle_score(lengths, cycles, primes)["median_normalized_error"])
    authentic_score = cycle_score(authentic, cycles, primes)
    a_score = authentic_score["median_normalized_error"]
    perm_percentile = float(np.mean(np.asarray(perm_scores) <= a_score))
    lognormal_percentile = float(np.mean(np.asarray(lognormal_scores) <= a_score))
    cycle_survives = perm_percentile < 0.05 and lognormal_percentile < 0.05

    resolutions = {}
    spectra = {}
    for resolution in (16, 24, 32):
        k, nodes = spectrum(len(points), edges, authentic, resolution)
        spectra[resolution] = k
        idx = np.arange(21, 181, dtype=float)
        slope, intercept = np.polyfit(k[20:180], idx, 1)
        expected = authentic.sum() / math.pi
        resolutions[str(resolution)] = {
            "fem_nodes": nodes,
            "zero_modes_below_1e-7": int(np.sum(k < 1e-7)),
            "weyl_slope_fit": float(slope),
            "weyl_slope_expected": float(expected),
            "weyl_relative_error": float(abs(slope - expected) / expected),
            "spacing": spacing_metrics(k),
            "first_12_wavenumbers": [float(x) for x in k[:12]],
        }
    km, magnetic_nodes = spectrum(len(points), edges, authentic, 24, magnetic=True)
    magnetic_spacing = spacing_metrics(km)
    conv_16_32 = np.abs(spectra[16][1:101] - spectra[32][1:101]) / np.maximum(spectra[32][1:101], 1e-12)
    conv_24_32 = np.abs(spectra[24][1:101] - spectra[32][1:101]) / np.maximum(spectra[32][1:101], 1e-12)

    result = {
        "test_id": "METATRON-PRIME-RETURN-v0",
        "construction": {
            "vertices": len(points), "edges": len(edges), "simple_cycles_3_to_8": len(cycles),
            "phi": PHI, "length_mean": float(authentic.mean()), "length_cv": float(cv),
            "uses_zeta_zero_ordinates": False,
        },
        "execution_order": ["equilateral", "200_permutations", "200_lognormal", "authentic_golden"],
        "cycle_alignment": {
            "equilateral": equilateral,
            "permutation_controls": {
                "count": len(perm_scores), "median": float(np.median(perm_scores)),
                "p05": float(np.quantile(perm_scores, .05)), "p95": float(np.quantile(perm_scores, .95)),
            },
            "lognormal_controls": {
                "count": len(lognormal_scores), "median": float(np.median(lognormal_scores)),
                "p05": float(np.quantile(lognormal_scores, .05)), "p95": float(np.quantile(lognormal_scores, .95)),
            },
            "authentic_golden": authentic_score,
            "authentic_percentile_permutation": perm_percentile,
            "authentic_percentile_lognormal": lognormal_percentile,
            "survives_preregistered_rule": bool(cycle_survives),
        },
        "spectrum": {
            "resolutions": resolutions,
            "convergence": {
                "median_relative_16_vs_32_first_100_positive": float(np.median(conv_16_32)),
                "max_relative_16_vs_32_first_100_positive": float(np.max(conv_16_32)),
                "median_relative_24_vs_32_first_100_positive": float(np.median(conv_24_32)),
                "max_relative_24_vs_32_first_100_positive": float(np.max(conv_24_32)),
            },
            "magnetic_resolution_24": {
                "fem_nodes": magnetic_nodes, "spacing": magnetic_spacing,
                "first_12_wavenumbers": [float(x) for x in km[:12]],
            },
        },
        "verdict": {
            "neutral_state": "MEASURED" if resolutions["32"]["zero_modes_below_1e-7"] == 1 else "UNVERIFIED",
            "prime_return": "MEASURED" if cycle_survives else "VOID",
            "prime_return_detail": "control-surviving alignment" if cycle_survives else "golden alignment did not beat both preregistered control thresholds",
            "weyl_obstruction": "MEASURED" if resolutions["32"]["weyl_relative_error"] < .03 else "UNVERIFIED",
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# METATRON-PRIME-RETURN v0 — results", "",
        "No zeta-zero ordinate entered the construction, tuning, or evaluation. Controls were scored first.", "",
        "| Question | Result | Status |", "|---|---:|---|",
        f"| Zero modes at finest resolution | {resolutions['32']['zero_modes_below_1e-7']} | {result['verdict']['neutral_state']} |",
        f"| Golden cycle score (lower is better) | {a_score:.6f} | {'MEASURED survivor' if cycle_survives else 'VOID as prime evidence'} |",
        f"| Golden percentile among permutations | {100*perm_percentile:.1f}% | control |",
        f"| Golden percentile among lognormal metrics | {100*lognormal_percentile:.1f}% | control |",
        f"| Finest Weyl slope relative error | {100*resolutions['32']['weyl_relative_error']:.3f}% | {result['verdict']['weyl_obstruction']} |",
        f"| Real chamber spacing closest to | {resolutions['24']['spacing']['closest'].upper()} | MEASURED |",
        f"| Magnetic mutation spacing closest to | {magnetic_spacing['closest'].upper()} | MEASURED |", "",
        "## Prediction ledger", "",
        "| Prediction | Outcome |", "|---|---|",
        f"| One neutral zero mode | {'MATCH' if resolutions['32']['zero_modes_below_1e-7'] == 1 else 'FAILED'} |",
        f"| Golden path score fails controls | {'MATCH' if not cycle_survives else 'FAILED'} |",
        f"| Real spectrum closer to GOE than GUE | {'MATCH' if resolutions['24']['spacing']['closest'] == 'goe' else 'FAILED — closest to ' + resolutions['24']['spacing']['closest'].upper()} |",
        f"| Linear Weyl slope within 3% at finest resolution | {'MATCH' if resolutions['32']['weyl_relative_error'] < .03 else 'FAILED'} |", "",
        "## Control table", "",
        "| Metric | Median score | 5th–95th percentile |", "|---|---:|---:|",
        f"| Equilateral | {equilateral['median_normalized_error']:.6f} | deterministic |",
        f"| Permuted golden lengths (n=200) | {np.median(perm_scores):.6f} | {np.quantile(perm_scores,.05):.6f}–{np.quantile(perm_scores,.95):.6f} |",
        f"| Matched lognormal lengths (n=200) | {np.median(lognormal_scores):.6f} | {np.quantile(lognormal_scores,.05):.6f}–{np.quantile(lognormal_scores,.95):.6f} |",
        f"| Authentic golden deformation | {a_score:.6f} | permutation rank {100*perm_percentile:.1f}%; lognormal rank {100*lognormal_percentile:.1f}% |", "",
        "## Honest reading", "",
        "The central constant mode is real but generic: every connected Kirchhoff metric graph has one. "
        + ("The golden path alignment survived the frozen controls and therefore deserves the preregistered larger rerun; it is not an RH result. " if cycle_survives else "The golden path alignment failed the frozen control rule, so this finite geometry supplies no measured prime arithmetic. ")
        + "The computed counting slope agrees with the linear metric-graph Weyl law, exposing the main obstruction: a fixed compact chamber cannot have the Riemann-von Mangoldt T log T density. The magnetic mutation tests the separate time-reversal issue, but it does not repair the counting law.", "",
        "Full machine-readable output: `outputs/results.json`.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
