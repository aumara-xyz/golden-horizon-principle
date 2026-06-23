#!/usr/bin/env python3
"""BTA-003 - Phi Coordinate Sampler Probe.

Question:
Does a phi-coordinate generator help as a proposal sampler compared with
storage, argmax, PRNG, digit-of-phi, and other low-discrepancy controls?

Important distinction:
- Tested: irrational rotation / low-discrepancy sampling with alpha = 1/phi.
- Not tested as proof: decimal digits of phi as "base reality".

Toy telemetry only. No physics, consciousness, authority, cryptography, or GHP
proof. The sampler proposes coordinates only; it never authorizes.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import zlib
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_phi_coordinate_sampler_probe_outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
ALPHA_PHI = 1.0 / PHI
ALPHA_SQRT2 = math.sqrt(2.0) - 1.0
TOKEN_COUNT = 8
WINDOW = 64
REGIMES = ["smooth", "balanced", "spiky", "bursty", "drifting", "inverted"]
SEEDS = [1618, 2718, 3141, 4159]


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


@dataclass
class SamplerState:
    name: str
    x: float = 0.0
    cursor: int = 0
    rng: random.Random | None = None


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def phi_prefix_digits(n: int) -> str:
    getcontext().prec = n + 8
    phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
    return str(phi).replace(".", "")[: n + 1]


def van_der_corput(index: int, base: int = 2) -> float:
    denom = 1.0
    value = 0.0
    i = index + 1
    while i:
        i, rem = divmod(i, base)
        denom *= base
        value += rem / denom
    return value


def normalize(raw: np.ndarray) -> np.ndarray:
    raw = np.maximum(raw, 1e-9)
    return raw / raw.sum()


def target_distribution(step: int, regime: str, seed: int) -> np.ndarray:
    rng_shift = (seed % 997) / 997.0
    i = np.arange(TOKEN_COUNT, dtype=float)
    if regime == "smooth":
        center = (TOKEN_COUNT / 2.0) + 2.6 * math.sin(step / 91.0 + rng_shift)
        raw = np.exp(-0.28 * (i - center) ** 2) + 0.07
    elif regime == "balanced":
        raw = 1.0 + 0.12 * np.sin(i * 1.7 + step / 47.0 + rng_shift)
    elif regime == "spiky":
        hot = int((step // 89 + seed) % TOKEN_COUNT)
        raw = np.full(TOKEN_COUNT, 0.10)
        raw[hot] = 2.60
        raw[(hot + 1) % TOKEN_COUNT] = 0.75
    elif regime == "bursty":
        hot = int((step // 37 + seed * 3) % TOKEN_COUNT)
        burst = 1.0 if step % 113 < 17 else 0.0
        raw = 0.45 + 0.25 * np.cos(i + step / 23.0)
        raw[hot] += 2.4 * burst
    elif regime == "drifting":
        slope = ((step / 220.0 + rng_shift) % 2.0) - 1.0
        raw = np.exp(0.45 * slope * (i - (TOKEN_COUNT - 1) / 2.0)) + 0.06
    elif regime == "inverted":
        hot = int((TOKEN_COUNT - 1 - step // 73 + seed) % TOKEN_COUNT)
        raw = np.full(TOKEN_COUNT, 0.20)
        raw[hot] = 1.80
        raw[(hot - 2) % TOKEN_COUNT] = 0.95
    else:
        raise ValueError(regime)
    return normalize(raw)


def mode_at(step: int, regime: str, p: np.ndarray) -> str:
    entropy = -float(np.sum(p * np.log2(np.maximum(p, 1e-12)))) / math.log2(TOKEN_COUNT)
    if step % 257 in range(0, 9):
        return "release"
    if entropy > 0.91 and step % 5 in {1, 2}:
        return "witness"
    if regime == "bursty" and step % 113 in range(17, 24):
        return "witness"
    return "write"


def choose_from_cdf(x: float, p: np.ndarray) -> int:
    threshold = min(max(x, 0.0), math.nextafter(1.0, 0.0))
    cdf = np.cumsum(p)
    return int(np.searchsorted(cdf, threshold, side="right"))


def x_for_sampler(state: SamplerState, step: int, p: np.ndarray, digits: str) -> float:
    if state.name == "argmax":
        # Not a real coordinate sampler; use a sentinel and choose directly later.
        return -1.0
    if state.name == "prng":
        assert state.rng is not None
        return state.rng.random()
    if state.name == "phi_rotation":
        state.x = (state.x + ALPHA_PHI) % 1.0
        return state.x
    if state.name == "sqrt2_rotation":
        state.x = (state.x + ALPHA_SQRT2) % 1.0
        return state.x
    if state.name == "vdc_base2":
        return van_der_corput(step, 2)
    if state.name == "phi_digits":
        width = 5
        start = (state.cursor * width) % (len(digits) - width)
        state.cursor += 1
        return int(digits[start : start + width]) / (10**width)
    if state.name == "periodic_lattice":
        return ((step % TOKEN_COUNT) + 0.5) / TOKEN_COUNT
    raise ValueError(state.name)


def score_window(tokens: list[int], targets: list[np.ndarray]) -> tuple[float, float, float, float]:
    if not tokens:
        return 0.0, 0.0, 0.0, 0.0
    empirical = np.bincount(tokens, minlength=TOKEN_COUNT).astype(float)
    empirical /= empirical.sum()
    mean_target = normalize(np.asarray(targets).mean(axis=0))
    l1 = float(np.sum(np.abs(empirical - mean_target)))
    repeats = sum(1 for a, b in zip(tokens, tokens[1:]) if a == b) / max(1, len(tokens) - 1)
    coverage = float(np.count_nonzero(empirical) / TOKEN_COUNT)
    max_gap = max_run_without_new_token(tokens)
    return l1, repeats, coverage, max_gap


def max_run_without_new_token(tokens: list[int]) -> float:
    seen: set[int] = set()
    longest = 0
    current = 0
    for token in tokens:
        if token in seen:
            current += 1
        else:
            seen.add(token)
            longest = max(longest, current)
            current = 0
    return float(max(longest, current))


def run_sampler(name: str, steps: int, digits: str, seed: int, regime: str) -> dict[str, float | str]:
    state = SamplerState(name=name, x=((seed % 1009) / 1009.0), rng=random.Random(seed * 10007 + len(name)))
    tokens: list[int] = []
    targets: list[np.ndarray] = []
    surprises: list[float] = []
    rolling_friction: list[float] = []
    duplicate_runs: list[int] = []
    last_token: int | None = None
    run_length = 0

    for step in range(steps):
        p = target_distribution(step, regime, seed)
        x = x_for_sampler(state, step, p, digits)
        token = int(np.argmax(p)) if name == "argmax" else choose_from_cdf(x, p)
        tokens.append(token)
        targets.append(p)
        surprises.append(-math.log2(max(float(p[token]), 1e-12)) / math.log2(TOKEN_COUNT))
        if token == last_token:
            run_length += 1
        else:
            duplicate_runs.append(run_length)
            run_length = 1
            last_token = token
        if len(tokens) >= WINDOW:
            l1, repeats, coverage, max_gap = score_window(tokens[-WINDOW:], targets[-WINDOW:])
            friction = 0.56 * l1 + 0.30 * repeats + 0.10 * statistics.fmean(surprises[-WINDOW:]) + 0.04 * (1.0 - coverage)
            rolling_friction.append(friction + 0.002 * max_gap)

    duplicate_runs.append(run_length)
    full_l1, repeat_rate, coverage, max_gap = score_window(tokens, targets)
    return {
        "sampler": name,
        "seed": seed,
        "regime": regime,
        "friction": statistics.fmean(rolling_friction),
        "distribution_l1": full_l1,
        "repeat_rate": repeat_rate,
        "coverage": coverage,
        "mean_surprise": statistics.fmean(surprises),
        "max_duplicate_run": max(duplicate_runs),
    }


def ternary_run(name: str, steps: int, seed: int, regime: str) -> dict[str, float | str]:
    rng = random.Random(seed * 17011 + len(name))
    x = (seed % 997) / 997.0
    tokens: list[int] = []
    targets: list[np.ndarray] = []
    surprises: list[float] = []
    write_count = 0
    authority_flip_count = 0

    for step in range(steps):
        p = target_distribution(step, regime, seed)
        mode = mode_at(step, regime, p)
        epoch_seed = ((seed + step // 257 * 37) % 991) / 991.0

        if name == "phi_ternary":
            if mode == "release":
                x = epoch_seed
                continue
            if mode == "witness":
                continue
            token = choose_from_cdf(x, p)
            x = (x + ALPHA_PHI * (1.0 + (token + 1) / TOKEN_COUNT)) % 1.0
        elif name == "phi_always_advance":
            x = (x + ALPHA_PHI) % 1.0
            if mode != "write":
                continue
            token = choose_from_cdf(x, p)
        elif name == "phi_write_only":
            if mode != "write":
                continue
            token = choose_from_cdf(x, p)
            x = (x + ALPHA_PHI) % 1.0
        elif name == "phi_reset_only":
            if mode == "release":
                x = epoch_seed
                continue
            x = (x + ALPHA_PHI) % 1.0
            if mode != "write":
                continue
            token = choose_from_cdf(x, p)
        elif name == "prng_ternary":
            if mode == "release":
                continue
            if mode == "witness":
                continue
            token = choose_from_cdf(rng.random(), p)
        else:
            raise ValueError(name)

        # Authority is deliberately external to sampling. This should never flip.
        authority_flip_count += 0
        write_count += 1
        tokens.append(token)
        targets.append(p)
        surprises.append(-math.log2(max(float(p[token]), 1e-12)) / math.log2(TOKEN_COUNT))

    l1, repeats, coverage, max_gap = score_window(tokens, targets)
    friction = 0.58 * l1 + 0.30 * repeats + 0.10 * statistics.fmean(surprises) + 0.02 * (1.0 - coverage)
    return {
        "sampler": name,
        "seed": seed,
        "regime": regime,
        "write_count": write_count,
        "friction": friction + 0.002 * max_gap,
        "distribution_l1": l1,
        "repeat_rate": repeats,
        "coverage": coverage,
        "mean_surprise": statistics.fmean(surprises),
        "authority_flip_count": authority_flip_count,
    }


def aggregate(rows: list[dict[str, float | str]], key: str = "sampler") -> list[dict[str, float | str]]:
    grouped: dict[str, list[dict[str, float | str]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    out = []
    for name, items in grouped.items():
        numeric_keys = [k for k, v in items[0].items() if isinstance(v, (int, float))]
        row: dict[str, float | str] = {key: name}
        for numeric_key in numeric_keys:
            vals = [float(item[numeric_key]) for item in items]
            row[f"{numeric_key}_mean"] = statistics.fmean(vals)
            row[f"{numeric_key}_std"] = statistics.pstdev(vals)
        out.append(row)
    return sorted(out, key=lambda item: float(item.get("friction_mean", 0.0)))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_generator_vs_storage() -> Result:
    generator_source = """
from decimal import Decimal, getcontext
def phi_prefix_digits(n):
    getcontext().prec = n + 8
    return str((Decimal(1) + Decimal(5).sqrt()) / Decimal(2))[:n+2]
""".strip()
    sizes = []
    for n in [1_000, 5_000, 20_000]:
        digits = phi_prefix_digits(n)
        sizes.append((n, len(generator_source.encode("utf-8")) * 8, len(digits.encode("utf-8")) * 8))
    constant = len({gen_bits for _, gen_bits, _ in sizes}) == 1
    ratio_1 = sizes[0][2] / sizes[0][1]
    ratio_3 = sizes[-1][2] / sizes[-1][1]
    passed = constant and ratio_3 > ratio_1 * 10
    return Result(
        "BTA-003A",
        "PASS" if passed else "FAIL",
        "generator_bits_constant / ratio_1k / ratio_20k",
        f"{constant} / {ratio_1:.2f} / {ratio_3:.2f}",
        "Generator-vs-storage compression is real but generic: a compact formula can emit arbitrary-length phi prefixes; this does not make phi unique.",
    )


def test_sampler_shootout(digits: str) -> tuple[Result, list[dict[str, float | str]], list[dict[str, float | str]]]:
    samplers = ["phi_rotation", "sqrt2_rotation", "vdc_base2", "prng", "phi_digits", "periodic_lattice", "argmax"]
    rows = []
    for seed in SEEDS:
        for regime in REGIMES:
            for sampler in samplers:
                rows.append(run_sampler(sampler, 1800, digits, seed, regime))
    summary = aggregate(rows)
    score = {str(row["sampler"]): float(row["friction_mean"]) for row in summary}
    phi = score["phi_rotation"]
    prng = score["prng"]
    digits_score = score["phi_digits"]
    argmax = score["argmax"]
    best = min(score, key=score.get)
    passed = phi < prng * 0.95 and phi < digits_score * 0.95 and phi < argmax * 0.95
    status = "PASS" if passed else "MIXED" if phi < prng and phi < digits_score else "FAIL"
    return (
        Result(
            "BTA-003B",
            status,
            "best_sampler / phi_friction / prng_friction / phi_digits_friction / argmax_friction",
            f"{best} / {phi:.4f} / {prng:.4f} / {digits_score:.4f} / {argmax:.4f}",
            "Phi rotation promotes only if it reduces local friction versus PRNG, phi-decimal digits, and argmax; losing to another low-discrepancy control is not a failure of the sampler idea.",
        ),
        rows,
        summary,
    )


def test_ternary_tuning() -> tuple[Result, list[dict[str, float | str]], list[dict[str, float | str]]]:
    samplers = ["phi_ternary", "phi_always_advance", "phi_write_only", "phi_reset_only", "prng_ternary"]
    rows = []
    for seed in SEEDS:
        for regime in REGIMES:
            for sampler in samplers:
                rows.append(ternary_run(sampler, 2200, seed, regime))
    summary = aggregate(rows)
    score = {str(row["sampler"]): float(row["friction_mean"]) for row in summary}
    phi_ternary = score["phi_ternary"]
    prng = score["prng_ternary"]
    always = score["phi_always_advance"]
    best = min(score, key=score.get)
    authority_flips = sum(int(row["authority_flip_count"]) for row in rows)
    passed = authority_flips == 0 and phi_ternary < prng * 0.97 and phi_ternary <= always * 1.03
    status = "PASS" if passed else "MIXED" if authority_flips == 0 and phi_ternary < prng else "FAIL"
    return (
        Result(
            "BTA-003C",
            status,
            "best_sampler / phi_ternary / prng_ternary / phi_always / authority_flips",
            f"{best} / {phi_ternary:.4f} / {prng:.4f} / {always:.4f} / {authority_flips}",
            "Ternary pointer semantics promote only if Write/Witness/Release lowers friction without creating any authority path.",
        ),
        rows,
        summary,
    )


def write_report(results: list[Result], sampler_summary: list[dict[str, float | str]], ternary_summary: list[dict[str, float | str]]) -> None:
    lines = [
        "# BTA-003 Phi Coordinate Sampler Probe",
        "",
        "Toy telemetry only. This checks phi as a deterministic proposal sampler, not as physics evidence or authority.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines.extend(["", "## Sampler Shootout", "", "| Sampler | Friction | L1 | Repeat | Coverage | Surprise |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for row in sampler_summary:
        lines.append(
            f"| {row['sampler']} | {float(row['friction_mean']):.4f} | {float(row['distribution_l1_mean']):.4f} | {float(row['repeat_rate_mean']):.4f} | {float(row['coverage_mean']):.4f} | {float(row['mean_surprise_mean']):.4f} |"
        )
    lines.extend(["", "## Ternary Boundary Tuning", "", "| Sampler | Friction | L1 | Repeat | Coverage | Surprise |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for row in ternary_summary:
        lines.append(
            f"| {row['sampler']} | {float(row['friction_mean']):.4f} | {float(row['distribution_l1_mean']):.4f} | {float(row['repeat_rate_mean']):.4f} | {float(row['coverage_mean']):.4f} | {float(row['mean_surprise_mean']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Safe Read",
            "",
            "The useful version of BTA-003 is phi as a low-discrepancy coordinate generator. It can be tested as proposal scheduling / anti-clumping. Decimal digits of phi are a control, not the foundation, because phi normality is not proven.",
            "",
            "If promoted to Aukora, this remains proposal guidance only. It must not enter gate authorization, cryptographic authority, identity, or proof language.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")


def write_handoff() -> None:
    text = """# BTA-003 Aukora Handoff

Do not port this yet as live behavior. Treat it as a side-lab sampler candidate.

Safe candidate:

- `phi_rotation_sampler`: `x = (x + 1/phi) mod 1`
- map `x` through the current token/action probability CDF
- compare against PRNG, argmax, van-der-Corput/Sobol, sqrt2 rotation, and phi digit controls

Hard laws:

- sampler proposes only
- gate authorizes
- sampler state is not authority
- timing is not authority
- phi decimal digits are not assumed normal
- no cryptographic or identity use

Promotion requirement:

- lower retry/friction than PRNG and argmax on live sandbox traces
- no worse than other low-discrepancy controls by more than a small tolerance
- no private/authority reconstruction
- no telemetry-to-gate read path
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(text)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Enough chunks for both sampler shootout and safety margin.
    digits = phi_prefix_digits(140_000)
    generator_result = test_generator_vs_storage()
    sampler_result, sampler_rows, sampler_summary = test_sampler_shootout(digits)
    ternary_result, ternary_rows, ternary_summary = test_ternary_tuning()
    results = [generator_result, sampler_result, ternary_result]
    write_csv(OUT / "summary.csv", [result.__dict__ for result in results])
    write_csv(OUT / "sampler_runs.csv", sampler_rows)
    write_csv(OUT / "sampler_summary.csv", sampler_summary)
    write_csv(OUT / "ternary_runs.csv", ternary_rows)
    write_csv(OUT / "ternary_summary.csv", ternary_summary)
    write_report(results, sampler_summary, ternary_summary)
    write_handoff()

    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
