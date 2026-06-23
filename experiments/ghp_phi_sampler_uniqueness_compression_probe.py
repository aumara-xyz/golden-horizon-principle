#!/usr/bin/env python3
"""BTA-004 - Phi sampler uniqueness and compression envelope probe.

Question:
Is phi special as a proposal sampler, and does a phi generator create a new
general compression method?

Safe reading:
- A generator can compress the sequence it generates.
- A generator does not compress arbitrary payloads unless the payload already
  has matching structure.
- Phi rotation is tested as one low-discrepancy sampler among controls, not as
  base reality, authority, identity, or physics evidence.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_phi_coordinate_sampler_probe as bta3


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_phi_sampler_uniqueness_compression_probe_outputs"
TOKEN_COUNT = bta3.TOKEN_COUNT
SEEDS = bta3.SEEDS
REGIMES = bta3.REGIMES
WINDOW = bta3.WINDOW
PHI = bta3.PHI


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def plastic_constant() -> float:
    x = 1.3
    for _ in range(24):
        x -= (x**3 - x - 1.0) / (3.0 * x**2 - 1.0)
    return x


def alpha_candidates() -> list[tuple[str, float]]:
    plastic = plastic_constant()
    base = [
        ("phi_inv", 1.0 / PHI),
        ("sqrt2_minus_1", math.sqrt(2.0) - 1.0),
        ("sqrt3_minus_1_frac", math.sqrt(3.0) - 1.0),
        ("pi_minus_3", math.pi - 3.0),
        ("e_minus_2", math.e - 2.0),
        ("plastic_inv", 1.0 / plastic),
        ("silver_inv", 1.0 / (1.0 + math.sqrt(2.0))),
        ("rational_1_8", 1.0 / 8.0),
        ("rational_3_8", 3.0 / 8.0),
        ("rational_5_13", 5.0 / 13.0),
    ]
    rng = random.Random(1618033)
    for i in range(40):
        base.append((f"random_alpha_{i:02d}", rng.uniform(0.05, 0.95)))
    return [(name, alpha % 1.0) for name, alpha in base if 0.0 < alpha % 1.0 < 1.0]


def score_window(tokens: list[int], targets: list[np.ndarray]) -> tuple[float, float, float, float]:
    return bta3.score_window(tokens, targets)


def run_alpha_rotation(name: str, alpha: float, steps: int, seed: int, regime: str) -> dict[str, float | str]:
    x = (seed % 1009) / 1009.0
    tokens: list[int] = []
    targets: list[np.ndarray] = []
    surprises: list[float] = []
    rolling_friction: list[float] = []

    for step in range(steps):
        p = bta3.target_distribution(step, regime, seed)
        x = (x + alpha) % 1.0
        token = bta3.choose_from_cdf(x, p)
        tokens.append(token)
        targets.append(p)
        surprises.append(-math.log2(max(float(p[token]), 1e-12)) / math.log2(TOKEN_COUNT))
        if len(tokens) >= WINDOW:
            l1, repeats, coverage, max_gap = score_window(tokens[-WINDOW:], targets[-WINDOW:])
            friction = 0.56 * l1 + 0.30 * repeats + 0.10 * statistics.fmean(surprises[-WINDOW:]) + 0.04 * (1.0 - coverage)
            rolling_friction.append(friction + 0.002 * max_gap)

    full_l1, repeat_rate, coverage, max_gap = score_window(tokens, targets)
    return {
        "sampler": name,
        "alpha": alpha,
        "seed": seed,
        "regime": regime,
        "friction": statistics.fmean(rolling_friction),
        "distribution_l1": full_l1,
        "repeat_rate": repeat_rate,
        "coverage": coverage,
        "mean_surprise": statistics.fmean(surprises),
        "max_duplicate_run": max_gap,
    }


def aggregate(rows: list[dict[str, float | str]], key: str) -> list[dict[str, float | str]]:
    grouped: dict[str, list[dict[str, float | str]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    out: list[dict[str, float | str]] = []
    for name, items in grouped.items():
        numeric_keys = [k for k, v in items[0].items() if isinstance(v, (int, float)) and k != "seed"]
        agg: dict[str, float | str] = {key: name}
        for k in numeric_keys:
            values = [float(item[k]) for item in items]
            agg[f"{k}_mean"] = statistics.fmean(values)
            agg[f"{k}_std"] = statistics.pstdev(values)
        out.append(agg)
    return sorted(out, key=lambda row: float(row["friction_mean"]))


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def quantized_rotation_tokens(alpha: float, length: int, seed: int = 0) -> list[int]:
    x = (seed % 1009) / 1009.0
    out: list[int] = []
    for _ in range(length):
        x = (x + alpha) % 1.0
        out.append(min(TOKEN_COUNT - 1, int(x * TOKEN_COUNT)))
    return out


def correction_bits(candidate: list[int], target: list[int]) -> int:
    mismatches = sum(1 for a, b in zip(candidate, target) if a != b)
    # Position of mismatch plus corrected token. This is deliberately generous:
    # real patch streams also need framing.
    return int(mismatches * (math.ceil(math.log2(len(target))) + math.ceil(math.log2(TOKEN_COUNT))))


def best_generator_patch_cost(target: list[int], candidates: list[tuple[str, float]]) -> dict[str, float | str]:
    best: dict[str, float | str] | None = None
    for name, alpha in candidates:
        for seed in [0, 1, 7, 13, 31]:
            generated = quantized_rotation_tokens(alpha, len(target), seed)
            mismatches = sum(1 for a, b in zip(generated, target) if a != b)
            model_bits = 192
            bits = model_bits + correction_bits(generated, target)
            row = {
                "generator": name,
                "seed": seed,
                "mismatches": mismatches,
                "mismatch_rate": mismatches / len(target),
                "bits": bits,
            }
            if best is None or float(row["bits"]) < float(best["bits"]):
                best = row
    assert best is not None
    return best


def test_sampler_uniqueness() -> tuple[Result, list[dict[str, float | str]], list[dict[str, float | str]]]:
    rows: list[dict[str, float | str]] = []
    for name, alpha in alpha_candidates():
        for seed in SEEDS:
            for regime in REGIMES:
                rows.append(run_alpha_rotation(name, alpha, 1600, seed, regime))

    summary = aggregate(rows, "sampler")
    names = [str(row["sampler"]) for row in summary]
    phi_rank = names.index("phi_inv") + 1
    phi_friction = next(float(row["friction_mean"]) for row in summary if row["sampler"] == "phi_inv")
    best = summary[0]
    random_rows = [row for row in summary if str(row["sampler"]).startswith("random_alpha_")]
    random_median = statistics.median(float(row["friction_mean"]) for row in random_rows)
    rational_rows = [row for row in summary if str(row["sampler"]).startswith("rational_")]
    rational_best = min(float(row["friction_mean"]) for row in rational_rows)

    status = "PASS" if phi_rank <= max(5, int(len(summary) * 0.20)) and phi_friction < random_median else "MIXED"
    if phi_friction >= random_median:
        status = "FAIL"
    value = (
        f"phi_rank={phi_rank}/{len(summary)}; best={best['sampler']}:{float(best['friction_mean']):.4f}; "
        f"phi={phi_friction:.4f}; random_median={random_median:.4f}; rational_best={rational_best:.4f}"
    )
    result = Result(
        "BTA-004A",
        status,
        "phi_rank / best / random_median / rational_best",
        value,
        "Phi is useful only if it behaves like a strong low-discrepancy sampler; this test does not allow uniqueness unless it beats the broader irrational family.",
    )
    return result, rows, summary


def test_compression_envelope() -> tuple[Result, list[dict[str, float | str]]]:
    candidates = alpha_candidates()[:10]
    length = 4096
    rng = random.Random(20260622)
    phi_payload = quantized_rotation_tokens(1.0 / PHI, length, seed=7)
    sqrt_payload = quantized_rotation_tokens(math.sqrt(2.0) - 1.0, length, seed=13)
    random_payload = [rng.randrange(TOKEN_COUNT) for _ in range(length)]
    structured_payload = [(i // 7) % TOKEN_COUNT for i in range(length)]

    rows: list[dict[str, float | str]] = []
    for name, payload in [
        ("phi_generated", phi_payload),
        ("sqrt2_generated", sqrt_payload),
        ("random_payload", random_payload),
        ("structured_periodic", structured_payload),
    ]:
        raw_bits = len(payload) * math.ceil(math.log2(TOKEN_COUNT))
        zlib_bits = compressed_bits(payload)
        best = best_generator_patch_cost(payload, candidates)
        rows.append(
            {
                "payload": name,
                "raw_bits": raw_bits,
                "zlib_bits": zlib_bits,
                "best_generator": best["generator"],
                "best_seed": best["seed"],
                "generator_patch_bits": best["bits"],
                "mismatch_rate": best["mismatch_rate"],
                "generator_vs_raw_ratio": float(best["bits"]) / raw_bits,
                "zlib_vs_raw_ratio": zlib_bits / raw_bits,
            }
        )

    phi_ratio = next(float(row["generator_vs_raw_ratio"]) for row in rows if row["payload"] == "phi_generated")
    random_ratio = next(float(row["generator_vs_raw_ratio"]) for row in rows if row["payload"] == "random_payload")
    status = "PASS" if phi_ratio < 0.05 and random_ratio > 1.0 else "MIXED"
    value = f"phi_generated_ratio={phi_ratio:.4f}; random_payload_ratio={random_ratio:.4f}"
    result = Result(
        "BTA-004B",
        status,
        "generator compression ratio on generated vs arbitrary payload",
        value,
        "Generator compression works on generated structure, not arbitrary data. This supports proposal scheduling, not universal compression.",
    )
    return result, rows


def test_base_encoding() -> tuple[Result, list[dict[str, float | str]]]:
    value = int("1618033988749894848204586834365638117720309179805762862135448622705260462818902449707207204189391137")
    alphabets = {
        "base2": "01",
        "base10": "0123456789",
        "base16": "0123456789abcdef",
        "base36": "0123456789abcdefghijklmnopqrstuvwxyz",
        "base62": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    }

    rows: list[dict[str, float | str]] = []
    for name, alphabet in alphabets.items():
        n = value
        base = len(alphabet)
        chars: list[str] = []
        while n:
            n, rem = divmod(n, base)
            chars.append(alphabet[rem])
        encoded = "".join(reversed(chars)) or alphabet[0]
        theoretical_bits = len(encoded) * math.log2(base)
        rows.append(
            {
                "encoding": name,
                "base": base,
                "symbols": len(encoded),
                "symbol_capacity_bits": theoretical_bits,
                "zlib_bits": len(zlib.compress(encoded.encode("ascii"), 9)) * 8,
            }
        )

    capacities = [float(row["symbol_capacity_bits"]) for row in rows]
    spread = max(capacities) - min(capacities)
    status = "PASS" if spread < 8.0 else "MIXED"
    result = Result(
        "BTA-004C",
        status,
        "same integer encoded across bases",
        f"capacity_spread_bits={spread:.2f}",
        "Changing base changes symbol count and glyph density, but not the information content of the underlying state.",
    )
    return result, rows


def write_report(results: list[Result], sampler_summary: list[dict[str, float | str]], compression_rows: list[dict[str, float | str]], base_rows: list[dict[str, float | str]]) -> None:
    lines = [
        "# BTA-004 Phi Sampler Uniqueness & Compression Envelope",
        "",
        "Toy telemetry only. This probes phi as a proposal-sampling and generator-compression candidate, not as physics evidence.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(f"| {r.probe} | {r.status} | {r.metric} | `{r.value}` | {r.safe_read} |")

    lines += [
        "",
        "## Top Samplers",
        "",
        "| Rank | Sampler | Friction | Alpha | Repeat | L1 |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(sampler_summary[:12], start=1):
        lines.append(
            f"| {rank} | {row['sampler']} | {float(row['friction_mean']):.4f} | "
            f"{float(row.get('alpha_mean', 0.0)):.6f} | {float(row['repeat_rate_mean']):.4f} | {float(row['distribution_l1_mean']):.4f} |"
        )

    lines += [
        "",
        "## Compression Envelope",
        "",
        "| Payload | Raw Bits | Zlib Bits | Best Generator | Patch Bits | Mismatch | Ratio |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in compression_rows:
        lines.append(
            f"| {row['payload']} | {int(row['raw_bits'])} | {int(row['zlib_bits'])} | {row['best_generator']} | "
            f"{int(row['generator_patch_bits'])} | {float(row['mismatch_rate']):.4f} | {float(row['generator_vs_raw_ratio']):.4f} |"
        )

    lines += [
        "",
        "## Base Encoding Check",
        "",
        "| Encoding | Base | Symbols | Capacity Bits | Zlib Bits |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in base_rows:
        lines.append(
            f"| {row['encoding']} | {int(row['base'])} | {int(row['symbols'])} | "
            f"{float(row['symbol_capacity_bits']):.2f} | {int(row['zlib_bits'])} |"
        )

    lines += [
        "",
        "## Safe Read",
        "",
        "This strengthens the sampler lane and weakens the uniqueness/compression overclaim lane. The useful object is a bounded proposal scheduler: deterministic, cheap, non-clumping, and comparable against other low-discrepancy controls.",
        "",
        "Do not promote phi digits, base-N glyph density, or generator compression into authority, identity, physics, or universal compression claims.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(results: list[Result]) -> None:
    text = f"""# BTA-004 Aukora Handoff

Do not port as live control yet.

Candidate worth testing later:

- Add `phi_rotation_sampler` only as an optional proposal scheduler.
- Compare it against `sqrt2_rotation`, van-der-Corput/Sobol-style controls, PRNG, argmax, and current sampler behavior.
- Use live sandbox traces only.

Non-candidates:

- Phi decimal digits as memory or address space.
- Base-N glyph density as compression proof.
- Generator compression as arbitrary-payload compression.
- Any sampler state as gate authority.

Promotion requirement:

- Improves retry/friction or exploration coverage on sandbox traces.
- Performs near the best low-discrepancy controls, not merely better than PRNG.
- Does not reconstruct private/authority state.
- Has no read path into gate/apply/OpenCode authority.

Latest lab statuses:

{chr(10).join(f"- {r.probe}: {r.status} - {r.value}" for r in results)}
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sampler_result, sampler_rows, sampler_summary = test_sampler_uniqueness()
    compression_result, compression_rows = test_compression_envelope()
    base_result, base_rows = test_base_encoding()
    results = [sampler_result, compression_result, base_result]

    write_csv(OUT / "sampler_runs.csv", sampler_rows)
    write_csv(OUT / "sampler_summary.csv", sampler_summary)
    write_csv(OUT / "compression_summary.csv", compression_rows)
    write_csv(OUT / "base_encoding_summary.csv", base_rows)
    write_csv(OUT / "summary.csv", [r.__dict__ for r in results])
    write_report(results, sampler_summary, compression_rows, base_rows)
    write_handoff(results)

    for r in results:
        print(f"{r.probe}: {r.status} | {r.metric}: {r.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
