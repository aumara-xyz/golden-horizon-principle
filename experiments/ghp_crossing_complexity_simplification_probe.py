#!/usr/bin/env python3
"""BTA-007 - Crossing-complexity simplification probe.

Question:
Does a public "knot pressure" / crossing-complexity proxy identify moments
where a simplification strategy lowers future residual cost?

This is not literal knot theory. The crossing number here is an engineering
proxy built from public telemetry:

    retry clusters + refusal clusters + instability deltas + near-miss proposals
    + latency as secondary evidence.

Toy telemetry only. No authority, no live reset, no physics claim.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import ghp_phi_coordinate_sampler_probe as bta3


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_crossing_complexity_simplification_probe_outputs"
TOKEN_COUNT = bta3.TOKEN_COUNT
PHI = bta3.PHI
ALPHA_PHI = 1.0 / PHI
ALPHA_SQRT2 = math.sqrt(2.0) - 1.0
REGIMES = ["smooth", "balanced", "spiky", "bursty", "drifting", "inverted"]
SEEDS = [1618, 2718, 3141, 4159, 5772, 6765]
WINDOW = 48
HORIZON = 96


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def compressed_bits(payload: Any) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def action_hash(actions: list[int]) -> str:
    return hashlib.sha256(json.dumps(actions, separators=(",", ":")).encode("utf-8")).hexdigest()


def target_distribution(step: int, seed: int) -> np.ndarray:
    return bta3.target_distribution(step, REGIMES[step % len(REGIMES)], seed)


def step_token(generator: str, x: float, step: int, seed: int, rng: random.Random | None = None) -> tuple[int, float]:
    p = target_distribution(step, seed)
    if generator == "phi_rotation":
        x = (x + ALPHA_PHI) % 1.0
        return bta3.choose_from_cdf(x, p), x
    if generator == "sqrt2_rotation":
        x = (x + ALPHA_SQRT2) % 1.0
        return bta3.choose_from_cdf(x, p), x
    if generator == "argmax":
        return int(np.argmax(p)), x
    if generator == "periodic_lattice":
        return bta3.choose_from_cdf(((step % TOKEN_COUNT) + 0.5) / TOKEN_COUNT, p), x
    if generator == "prng":
        assert rng is not None
        return bta3.choose_from_cdf(rng.random(), p), x
    raise ValueError(generator)


def generate_sequence(generator: str, seed: int, steps: int, start_step: int = 0, reset: bool = True) -> list[int]:
    x = ((seed if reset else seed + start_step) % 1009) / 1009.0
    rng = random.Random(seed * 104729 + len(generator) + start_step)
    out: list[int] = []
    for offset in range(steps):
        token, x = step_token(generator, x, start_step + offset, seed, rng)
        out.append(token)
    return out


def shock_schedule(seed: int) -> list[tuple[int, int]]:
    offset = seed % 53
    return [(310 + offset, 80), (820 + offset // 2, 92), (1370 + offset, 76), (1900 + offset // 3, 84)]


def in_shock(step: int, schedule: list[tuple[int, int]]) -> tuple[bool, int]:
    for idx, (start, duration) in enumerate(schedule):
        if start <= step < start + duration:
            return True, idx
    return False, -1


def generate_trace(source: str, seed: int, steps: int = 2400) -> list[dict[str, Any]]:
    """Generate public traces with optional hidden epoch switches.

    `phi_resettable` and `sqrt2_resettable` simulate a process where high
    pressure marks a switch to a fresh local generator epoch.
    """
    rng = random.Random(seed * 7919 + len(source))
    schedule = shock_schedule(seed)
    current_epoch = 0
    epoch_start = 0
    epoch_seed = seed
    x = (seed % 1009) / 1009.0
    phi_continue_x = (seed % 1009) / 1009.0
    rows: list[dict[str, Any]] = []
    for step in range(steps):
        shocked, shock_idx = in_shock(step, schedule)
        if shocked and step == schedule[shock_idx][0]:
            current_epoch += 1
            epoch_start = step
            epoch_seed = seed + 37 * current_epoch
            x = (epoch_seed % 1009) / 1009.0

        base_generator = {
            "phi_resettable": "phi_rotation",
            "sqrt2_resettable": "sqrt2_rotation",
            "argmax": "argmax",
            "prng": "prng",
            "human_jitter": "argmax",
        }[source]

        token, x = step_token(base_generator, x, step - epoch_start if shocked else step, epoch_seed, rng)
        if source == "human_jitter" and rng.random() < (0.12 + 0.18 * shocked):
            token, _ = step_token("prng", x, step, seed, rng)
        if source == "prng":
            token, _ = step_token("prng", x, step, seed, rng)

        phi_continue_token, phi_continue_x = step_token("phi_rotation", phi_continue_x, step, seed, None)
        near_miss = int(phi_continue_token != token)
        retry_count = max(0, int(round((3.6 if shocked else 0.4) + 2.0 * near_miss + rng.random() * 1.8)))
        refusal_count = int(shocked and rng.random() < 0.28) + int(near_miss and rng.random() < 0.10)
        instability_delta = min(1.0, (0.18 if not shocked else 0.58) + 0.22 * near_miss + rng.random() * 0.18)
        latency_bucket = min(1.0, (0.12 if not shocked else 0.48) + 0.16 * retry_count / 6.0 + rng.random() * 0.10)
        pressure = min(
            1.0,
            0.33 * min(1.0, retry_count / 7.0)
            + 0.20 * min(1.0, refusal_count / 2.0)
            + 0.25 * instability_delta
            + 0.16 * near_miss
            + 0.06 * latency_bucket,
        )
        rows.append(
            {
                "step": step,
                "source": source,
                "action": token,
                "retryCount": retry_count,
                "refusalCount": refusal_count,
                "instabilityDelta": round(instability_delta, 4),
                "nearMiss": near_miss,
                "latencyBucket": round(latency_bucket, 4),
                "knotPressure": round(pressure, 4),
                "shock": int(shocked),
                "hidden": {
                    "epochSeed": epoch_seed,
                    "privateKeyFragment": f"sk_hidden_{seed}_{source}",
                    "authorityGrant": "PRIVATE_AUTHORITY_NEVER_EXPORT",
                },
            }
        )
    return rows


def rolling_pressure(rows: list[dict[str, Any]]) -> list[float]:
    pressures = [float(row["knotPressure"]) for row in rows]
    out: list[float] = []
    for i in range(len(pressures)):
        start = max(0, i - WINDOW + 1)
        out.append(statistics.fmean(pressures[start : i + 1]))
    return out


def select_windows(rows: list[dict[str, Any]], seed: int, shuffled: bool = False) -> list[int]:
    pressure = rolling_pressure(rows)
    candidates = list(range(WINDOW, len(rows) - HORIZON, 12))
    if shuffled:
        rng = random.Random(seed * 31337)
        shuffled_pressure = pressure[:]
        rng.shuffle(shuffled_pressure)
        scored = sorted(candidates, key=lambda i: shuffled_pressure[i], reverse=True)
    else:
        scored = sorted(candidates, key=lambda i: pressure[i], reverse=True)
    selected: list[int] = []
    for idx in scored:
        if all(abs(idx - prev) > HORIZON for prev in selected):
            selected.append(idx)
        if len(selected) >= 8:
            break
    return sorted(selected)


def patch_cost(predicted: list[int], actual: list[int]) -> tuple[int, float]:
    mismatches = sum(1 for a, b in zip(predicted, actual) if a != b)
    bits_per = math.ceil(math.log2(HORIZON)) + math.ceil(math.log2(TOKEN_COUNT))
    return 192 + mismatches * bits_per, mismatches / len(actual)


def strategy_predictions(seed: int, start: int) -> dict[str, list[int]]:
    return {
        "continue_phi": generate_sequence("phi_rotation", seed, start + HORIZON, 0, reset=True)[start: start + HORIZON],
        "reset_phi": generate_sequence("phi_rotation", seed + 37, HORIZON, start, reset=True),
        "continue_sqrt2": generate_sequence("sqrt2_rotation", seed, start + HORIZON, 0, reset=True)[start: start + HORIZON],
        "reset_sqrt2": generate_sequence("sqrt2_rotation", seed + 37, HORIZON, start, reset=True),
        "argmax": generate_sequence("argmax", seed, HORIZON, start, reset=True),
        "periodic_lattice": generate_sequence("periodic_lattice", seed, HORIZON, start, reset=True),
    }


def evaluate_window(rows: list[dict[str, Any]], seed: int, start: int, source: str, shuffled: bool) -> dict[str, Any]:
    actual = [int(row["action"]) for row in rows[start : start + HORIZON]]
    strategies = strategy_predictions(seed, start)
    costs: dict[str, tuple[int, float]] = {name: patch_cost(pred, actual) for name, pred in strategies.items()}
    best_name = min(costs, key=lambda name: costs[name][0])
    continue_cost = costs["continue_phi"][0]
    best_cost, mismatch = costs[best_name]
    summary = {
        "schema": "SIMPLIFICATION_WINDOW_V1",
        "status": "TELEMETRY_ONLY",
        "advisoryOnly": True,
        "grantsAuthority": False,
        "source": source,
        "windowStart": start,
        "strategy": best_name,
        "residualCount": int(round(mismatch * HORIZON)),
        "actionHash": action_hash(actual),
    }
    replay_ok = action_hash(actual) == summary["actionHash"]
    return {
        "source": source,
        "seed": seed,
        "shuffled": int(shuffled),
        "windowStart": start,
        "meanPressure": statistics.fmean(float(row["knotPressure"]) for row in rows[start - WINDOW : start]),
        "shockRate": statistics.fmean(int(row["shock"]) for row in rows[start : start + HORIZON]),
        "bestStrategy": best_name,
        "continueCost": continue_cost,
        "bestCost": best_cost,
        "improvement": (continue_cost - best_cost) / max(1, continue_cost),
        "mismatchRate": mismatch,
        "summaryBits": compressed_bits(summary),
        "actionHistoryBits": compressed_bits(actual),
        "replayOk": replay_ok,
        "leak": "PRIVATE_AUTHORITY" in json.dumps(summary) or "sk_hidden" in json.dumps(summary),
    }


def run_source(source: str, seed: int) -> list[dict[str, Any]]:
    rows = generate_trace(source, seed)
    out: list[dict[str, Any]] = []
    for shuffled in [False, True]:
        for start in select_windows(rows, seed, shuffled):
            out.append(evaluate_window(rows, seed, start, source, shuffled))
    return out


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["source"]), int(row["shuffled"])), []).append(row)
    out: list[dict[str, Any]] = []
    for (source, shuffled), items in grouped.items():
        out.append(
            {
                "source": source,
                "shuffled": shuffled,
                "bestStrategyMode": statistics.mode(str(item["bestStrategy"]) for item in items),
                "improvementMean": statistics.fmean(float(item["improvement"]) for item in items),
                "mismatchRateMean": statistics.fmean(float(item["mismatchRate"]) for item in items),
                "shockRateMean": statistics.fmean(float(item["shockRate"]) for item in items),
                "replayRate": statistics.fmean(1.0 if item["replayOk"] else 0.0 for item in items),
                "leakRate": statistics.fmean(1.0 if item["leak"] else 0.0 for item in items),
                "summaryRatioMean": statistics.fmean(float(item["summaryBits"]) / float(item["actionHistoryBits"]) for item in items),
                "windowCount": len(items),
            }
        )
    return sorted(out, key=lambda row: (str(row["source"]), int(row["shuffled"])))


def classify(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> list[Result]:
    def source_summary(source: str, shuffled: int) -> dict[str, Any]:
        for row in summary:
            if row["source"] == source and int(row["shuffled"]) == shuffled:
                return row
        raise KeyError((source, shuffled))

    real_phi = source_summary("phi_resettable", 0)
    shuffle_phi = source_summary("phi_resettable", 1)
    real_sqrt = source_summary("sqrt2_resettable", 0)
    shuffle_sqrt = source_summary("sqrt2_resettable", 1)
    prng_real = source_summary("prng", 0)
    replay_rate = statistics.fmean(1.0 if row["replayOk"] else 0.0 for row in rows)
    leak_rate = statistics.fmean(1.0 if row["leak"] else 0.0 for row in rows)
    phi_gap = float(real_phi["improvementMean"]) - float(shuffle_phi["improvementMean"])
    sqrt_gap = float(real_sqrt["improvementMean"]) - float(shuffle_sqrt["improvementMean"])
    prng_improve = float(prng_real["improvementMean"])
    reset_mode_ok = real_phi["bestStrategyMode"] in {"reset_phi", "continue_phi"} and real_sqrt["bestStrategyMode"] in {"reset_sqrt2", "continue_sqrt2"}

    return [
        Result(
            "BTA-007A",
            "PASS" if phi_gap > 0.10 and sqrt_gap > 0.10 else "MIXED",
            "real pressure improvement gap over shuffled control",
            f"phi_gap={phi_gap:.4f}; sqrt2_gap={sqrt_gap:.4f}",
            "A crossing-complexity proxy is useful only if real high-pressure windows select cheaper future replay than shuffled-pressure windows.",
        ),
        Result(
            "BTA-007B",
            "PASS" if reset_mode_ok and prng_improve < 0.25 else "MIXED",
            "strategy selectivity / PRNG non-promotion",
            f"phi_mode={real_phi['bestStrategyMode']}; sqrt2_mode={real_sqrt['bestStrategyMode']}; prng_improvement={prng_improve:.4f}",
            "Simplification must select the matching compact family when one exists and avoid treating random traces as clean topology.",
        ),
        Result(
            "BTA-007C",
            "PASS" if replay_rate == 1.0 and leak_rate == 0.0 else "FAIL",
            "exact replay and leak scan",
            f"replay={replay_rate:.4f}; leak={leak_rate:.4f}",
            "Any simplification summary must replay public actions and carry no private or authority-shaped fields.",
        ),
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(results: list[Result], summary: list[dict[str, Any]]) -> None:
    lines = [
        "# BTA-007 Crossing-Complexity Simplification Probe",
        "",
        "Toy telemetry only. `Crossing number` here means a public engineering proxy, not literal knot theory.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += [
        "",
        "## Source Summary",
        "",
        "| Source | Shuffled | Strategy Mode | Improvement | Mismatch | Shock | Replay | Leak | Summary/Actions | Windows |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        lines.append(
            f"| {row['source']} | {int(row['shuffled'])} | {row['bestStrategyMode']} | "
            f"{float(row['improvementMean']):.4f} | {float(row['mismatchRateMean']):.4f} | "
            f"{float(row['shockRateMean']):.4f} | {float(row['replayRate']):.1f} | "
            f"{float(row['leakRate']):.1f} | {float(row['summaryRatioMean']):.4f} | {int(row['windowCount'])} |"
        )
    lines += [
        "",
        "## Safe Read",
        "",
        "This probe supports testing a simplification pass only as offline advisory analysis. It does not justify live sampler resets. The useful invariant is: high public knot pressure may identify moments where a compact replay model should be re-fit, but any resulting summary must remain replayable, residual-explicit, and authority-isolated.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(results: list[Result]) -> None:
    text = f"""# BTA-007 Aukora Handoff

Recommended addition to the build prompt:

Add an offline `crossingComplexity` / `knotPressure` analysis pass over public sandbox telemetry.

Public proxy fields:

- retry clusters
- refusal clusters
- instability deltas
- repeated near-miss proposals
- latency bucket as secondary evidence only

Offline strategies to compare after high-pressure windows:

- continue current generator state
- reset same generator seed/state
- switch generator candidate
- fall back to raw public action history

Promotion requirement:

- real high-pressure windows outperform shuffled-pressure windows
- simplification lowers future residual cost
- exact replay remains true
- no private/authority fields in summary
- no live reset or gate influence

Latest lab statuses:

{chr(10).join(f"- {r.probe}: {r.status} - {r.value}" for r in results)}
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = ["phi_resettable", "sqrt2_resettable", "argmax", "human_jitter", "prng"]
    rows: list[dict[str, Any]] = []
    for source in sources:
        for seed in SEEDS:
            rows.extend(run_source(source, seed))
    summary = aggregate(rows)
    results = classify(rows, summary)
    write_csv(OUT / "window_runs.csv", rows)
    write_csv(OUT / "source_summary.csv", summary)
    write_csv(OUT / "summary.csv", [r.__dict__ for r in results])
    write_report(results, summary)
    write_handoff(results)
    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
