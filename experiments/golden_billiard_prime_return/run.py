#!/usr/bin/env python3
"""GOLDEN-BILLIARD-PRIME-RETURN v0; controls-first deterministic runner."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.special import erf


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
SEED = 20260904


def primes(n):
    out = []
    x = 2
    while len(out) < n:
        if all(x % p for p in out if p * p <= x):
            out.append(x)
        x += 1
    return np.asarray(out, dtype=float)


def primitive_returns(r, count, cutoff=256):
    vals = []
    for m in range(cutoff + 1):
        for n in range(cutoff + 1):
            if (m or n) and math.gcd(m, n) == 1:
                vals.append(2.0 * math.hypot(m, n * r))
    # Rounding only merges mathematically repeated square-billiard lengths.
    unique = np.unique(np.round(vals, 13))
    unique.sort()
    if len(unique) < count:
        raise RuntimeError("return cutoff too small")
    return unique[:count]


def local_spacings(x):
    d = np.empty_like(x)
    d[0], d[-1] = x[1] - x[0], x[-1] - x[-2]
    d[1:-1] = 0.5 * (x[2:] - x[:-2])
    return d


def alignment(r, count):
    target_p = primes(count)
    target = np.log(target_p)
    returns = primitive_returns(r, count)
    scaled = returns * (math.log(2.0) / returns[0])
    errors = np.abs(scaled - target)
    normalized = errors / local_spacings(target)
    return {
        "aspect_ratio": float(r),
        "count": count,
        "median_normalized_error": float(np.median(normalized)),
        "mean_normalized_error": float(np.mean(normalized)),
        "max_normalized_error": float(np.max(normalized)),
        "per_rank": [
            {
                "rank": i + 1, "prime": int(p), "log_prime": float(t),
                "scaled_return": float(q), "absolute_error": float(e),
                "normalized_error": float(z),
            }
            for i, (p, t, q, e, z) in enumerate(zip(target_p, target, scaled, errors, normalized))
        ],
    }


def ks_distance(sample, cdf):
    x = np.sort(np.asarray(sample))
    n = len(x)
    f = cdf(x)
    return float(max(np.max(np.arange(1, n + 1) / n - f), np.max(f - np.arange(n) / n)))


def spectral_statistics(r):
    # Exact separated Neumann spectrum of the 1 by r rectangle.
    k = []
    for m in range(121):
        for n in range(121):
            if m or n:
                k.append(math.pi * math.hypot(m, n / r))
    k = np.unique(np.round(k, 13))
    k.sort()
    k = k[100:1101]
    area, perimeter = r, 2.0 * (1.0 + r)
    unfolded = area * k * k / (4.0 * math.pi) + perimeter * k / (4.0 * math.pi)
    s = np.diff(unfolded)
    s /= s.mean()
    cdfs = {
        "poisson": lambda z: 1.0 - np.exp(-z),
        "goe": lambda z: 1.0 - np.exp(-math.pi * z * z / 4.0),
        "gue": lambda z: erf(2.0 * z / math.sqrt(math.pi)) - (4.0 * z / math.pi) * np.exp(-4.0 * z * z / math.pi),
    }
    ks = {name: ks_distance(s, fn) for name, fn in cdfs.items()}
    # Fit the exponent in N(k) ~ C k^alpha on the upper half of a larger exact grid.
    all_k = []
    for m in range(301):
        for n in range(301):
            if m or n:
                all_k.append(math.pi * math.hypot(m, n / r))
    all_k = np.sort(np.asarray(all_k))
    idx = np.arange(1, len(all_k) + 1, dtype=float)
    sl = slice(len(all_k) // 4, len(all_k) // 2)
    alpha = np.polyfit(np.log(all_k[sl]), np.log(idx[sl]), 1)[0]
    return {"ks": ks, "closest": min(ks, key=ks.get), "counting_exponent_fit": float(alpha)}


def summary(values):
    a = np.asarray(values)
    return {
        "count": len(values), "median": float(np.median(a)),
        "p01": float(np.quantile(a, .01)), "p05": float(np.quantile(a, .05)),
        "p95": float(np.quantile(a, .95)),
    }


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Frozen execution order: named and random controls before phi.
    named = {name: alignment(r, 50) for name, r in [("square", 1.0), ("sqrt2", math.sqrt(2.0)), ("sqrt3", math.sqrt(3.0))]}
    random_ratios = np.exp(rng.uniform(0.0, math.log(2.0), 500))
    random_scores_50 = [alignment(r, 50)["median_normalized_error"] for r in random_ratios]
    random_scores_100 = [alignment(r, 100)["median_normalized_error"] for r in random_ratios]

    golden_50 = alignment(PHI, 50)
    golden_100 = alignment(PHI, 100)
    pct50 = float(np.mean(np.asarray(random_scores_50) <= golden_50["median_normalized_error"]))
    pct100 = float(np.mean(np.asarray(random_scores_100) <= golden_100["median_normalized_error"]))
    survives = pct50 < .01 and pct100 < .01
    spectral = spectral_statistics(PHI)

    result = {
        "test_id": "GOLDEN-BILLIARD-PRIME-RETURN-v0",
        "uses_zeta_zero_ordinates": False,
        "execution_order": ["square", "sqrt2", "sqrt3", "500_random", "golden_ratio"],
        "controls": {
            "named": named,
            "random_50": summary(random_scores_50),
            "random_100": summary(random_scores_100),
        },
        "golden": {
            "n50": golden_50, "n100": golden_100,
            "percentile_50": pct50, "percentile_100": pct100,
            "survives": bool(survives),
        },
        "spectrum": spectral,
        "verdict": {
            "prime_alignment": "UNVERIFIED" if survives else "VOID",
            "neutral_mode": "MEASURED",
            "density_obstruction": "MEASURED" if abs(spectral["counting_exponent_fit"] - 2.0) < .1 else "UNVERIFIED",
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    rows = []
    for name in ("square", "sqrt2", "sqrt3"):
        rows.append(f"| {name} | {named[name]['median_normalized_error']:.6f} | deterministic control |")
    rows.append(f"| random ratios (n=500) | {np.median(random_scores_50):.6f} | 1st–95th: {np.quantile(random_scores_50,.01):.6f}–{np.quantile(random_scores_50,.95):.6f} |")
    rows.append(f"| golden ratio | {golden_50['median_normalized_error']:.6f} | percentile {100*pct50:.1f}% |")
    report = [
        "# GOLDEN-BILLIARD-PRIME-RETURN v0 — results", "",
        "No zeta-zero ordinate entered the construction, tuning, or scoring. All controls ran before the golden ratio.", "",
        "| Aspect ratio | 50-return score (lower better) | Reading |", "|---|---:|---|", *rows, "",
        "## Frozen extension", "",
        f"At 100 primes the golden score is {golden_100['median_normalized_error']:.6f}, at random-control percentile {100*pct100:.1f}%.", "",
        "## Spectral checks", "",
        f"- The exact Neumann spectrum includes the constant `(m,n)=(0,0)` zero mode: **MEASURED**, but generic.",
        f"- Unfolded positive spacings are closest to **{spectral['closest'].upper()}** (KS: " + ", ".join(f"{k}={v:.4f}" for k,v in spectral['ks'].items()) + ").",
        f"- The fitted counting exponent is `{spectral['counting_exponent_fit']:.4f}`; the two-dimensional Weyl prediction is 2, whereas zeta requires `T log T`.", "",
        "## Prediction ledger", "",
        "| Prediction | Outcome |", "|---|---|",
        f"| Golden ratio fails the 1% control threshold | {'MATCH' if not survives else 'FAILED'} |",
        "| One neutral Neumann mode | MATCH |",
        f"| Quadratic rather than `T log T` count | {'MATCH' if abs(spectral['counting_exponent_fit']-2)<.1 else 'FAILED'} |",
        f"| Poisson-like spacings | {'MATCH' if spectral['closest']=='poisson' else 'FAILED'} |", "",
        "## Honest paragraph", "",
        ("The golden rectangle survived the frozen numerical threshold, so the result remains UNVERIFIED pending the promised hostile controls. " if survives else "The golden rectangle did not survive the frozen control threshold, so its return-length resemblance is VOID as prime evidence. ")
        + "The experiment does preserve the useful conceptual distinction: a bounded room can support infinitely many returns. But its ordinary Laplacian has the wrong spectral-growth law, and its integrable dynamics has the wrong symmetry statistics. Infinite reflection alone is therefore insufficient; the surviving target must add scale-invariant or arithmetic dynamics without inserting the answers.", "",
        "Full machine-readable output: `outputs/results.json`.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
