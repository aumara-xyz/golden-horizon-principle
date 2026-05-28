#!/usr/bin/env python3
"""Golden zipper / Sturmian memory toy for GHP.

Toy telemetry only. Not physics evidence.
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "golden_zipper_outputs"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN = 1.0 / PHI
SILVER = math.sqrt(2.0) - 1.0
BRONZE = (math.sqrt(13.0) - 3.0) / 2.0

SEED = 1729
STEPS = 4096
WINDOW_SIZES = [0.20, 0.34, 0.47]
WINDOW_PHASES = [0.0, 0.17]
WINDOW_TYPES = ["single", "moving", "double"]
BLOCK_LENGTHS = list(range(2, 13))
PERIOD_MAX = 256
RANDOM_ALPHA_COUNT = 5


@dataclass(frozen=True)
class SlopeSpec:
    name: str
    family: str
    alpha: float


def wrap01(x: float) -> float:
    return x % 1.0


def in_window(x: float, start: float, width: float) -> bool:
    end = start + width
    if end <= 1.0:
        return start <= x < end
    return x >= start or x < (end % 1.0)


def build_slopes() -> list[SlopeSpec]:
    slopes = [
        SlopeSpec("golden", "golden", GOLDEN),
        SlopeSpec("silver", "silver", SILVER),
        SlopeSpec("bronze", "bronze", BRONZE),
        SlopeSpec("rational_1_2", "rational_approx", 1.0 / 2.0),
        SlopeSpec("rational_2_3", "rational_approx", 2.0 / 3.0),
        SlopeSpec("rational_3_5", "rational_approx", 3.0 / 5.0),
        SlopeSpec("rational_5_8", "rational_approx", 5.0 / 8.0),
        SlopeSpec("rational_8_13", "rational_approx", 8.0 / 13.0),
        SlopeSpec("rational_13_21", "rational_approx", 13.0 / 21.0),
        SlopeSpec("control_1_3", "rational_control", 1.0 / 3.0),
        SlopeSpec("control_1_4", "rational_control", 1.0 / 4.0),
        SlopeSpec("control_2_5", "rational_control", 2.0 / 5.0),
    ]

    rng = np.random.default_rng(SEED)
    for idx in range(RANDOM_ALPHA_COUNT):
        alpha = float(rng.uniform(0.05, 0.95))
        slopes.append(SlopeSpec(f"random_{idx+1}", "random", alpha))
    return slopes


def generate_sequence(
    alpha: float,
    steps: int,
    window_size: float,
    phase: float,
    window_type: str,
) -> np.ndarray:
    seq = np.zeros(steps, dtype=np.int8)
    x = phase
    for n in range(steps):
        x = wrap01(x + alpha)
        if window_type == "single":
            hit = in_window(x, phase, window_size)
        elif window_type == "moving":
            drift = wrap01(phase + n * alpha * 0.07)
            hit = in_window(x, drift, window_size)
        elif window_type == "double":
            hit = in_window(x, phase, window_size / 2.0) or in_window(
                x, wrap01(phase + 0.5), window_size / 2.0
            )
        else:
            raise ValueError(f"unknown window type: {window_type}")
        seq[n] = 1 if hit else 0
    return seq


def subwords(seq: np.ndarray, length: int) -> list[tuple[int, ...]]:
    n = len(seq)
    return [tuple(int(x) for x in seq[i : i + length]) for i in range(n - length + 1)]


def balance_metrics(seq: np.ndarray) -> tuple[float, float]:
    good = 0
    max_spread = 0
    for length in BLOCK_LENGTHS:
        words = subwords(seq, length)
        counts = [sum(word) for word in words]
        spread = max(counts) - min(counts) if counts else 0
        max_spread = max(max_spread, spread)
        if spread <= 1:
            good += 1
    return good / len(BLOCK_LENGTHS), float(max_spread)


def complexity_metrics(seq: np.ndarray) -> tuple[float, float]:
    ratios = []
    deviations = []
    n = len(seq)
    for length in BLOCK_LENGTHS:
        words = subwords(seq, length)
        distinct = len(set(words))
        ideal = length + 1
        max_possible = min(2**length, n - length + 1)
        ratios.append(distinct / max_possible if max_possible else 0.0)
        deviations.append(abs(distinct - ideal) / ideal)
    return float(np.mean(ratios)), float(np.mean(deviations))


def periodicity_metrics(seq: np.ndarray) -> tuple[float, int]:
    prefix = seq[: min(len(seq), 1024)]
    for period in range(1, min(PERIOD_MAX, len(prefix) // 2) + 1):
        if np.array_equal(prefix[:-period], prefix[period:]):
            return 1.0 / period, period
    return 0.0, PERIOD_MAX + 1


def lz78_phrase_count(seq: np.ndarray) -> int:
    dictionary = set()
    phrases = 0
    i = 0
    symbols = "".join(str(int(x)) for x in seq)
    n = len(symbols)
    while i < n:
        j = i + 1
        while j <= n and symbols[i:j] in dictionary:
            j += 1
        dictionary.add(symbols[i:j])
        phrases += 1
        i = j
    return phrases


def predictive_score(seq: np.ndarray) -> float:
    counts: dict[tuple[int, int], Counter] = defaultdict(Counter)
    correct = 0
    total = 0
    for i in range(2, len(seq)):
        ctx = (int(seq[i - 2]), int(seq[i - 1]))
        if counts[ctx]:
            pred = 1 if counts[ctx][1] >= counts[ctx][0] else 0
            correct += int(pred == int(seq[i]))
            total += 1
        counts[ctx][int(seq[i])] += 1
    return correct / total if total else 0.5


def compression_metric(seq: np.ndarray) -> float:
    phrases = lz78_phrase_count(seq)
    phrase_density = phrases / len(seq)
    prediction = predictive_score(seq)
    return prediction / max(phrase_density, 1e-9)


def memory_policy(seq: np.ndarray) -> dict[str, float]:
    context_len = 4
    motif_len = 6
    next_counts: dict[tuple[int, ...], Counter] = defaultdict(Counter)
    motif_counts: Counter = Counter()

    for i in range(context_len, len(seq)):
        ctx = tuple(int(x) for x in seq[i - context_len : i])
        next_counts[ctx][int(seq[i])] += 1
    for i in range(len(seq) - motif_len + 1):
        motif = tuple(int(x) for x in seq[i : i + motif_len])
        motif_counts[motif] += 1

    max_motif = max(motif_counts.values()) if motif_counts else 1
    actions = []
    contradicted_writes = 0
    total_writes = 0
    delayed_meaning_kept = 0
    delayed_meaning_missed = 0

    for i, sym in enumerate(seq):
        if i < context_len:
            confidence = 0.5
            motif_score = 0.0
        else:
            ctx = tuple(int(x) for x in seq[i - context_len : i])
            counts = next_counts[ctx]
            total = sum(counts.values())
            confidence = counts[int(sym)] / total if total else 0.5
            if i <= len(seq) - motif_len:
                motif = tuple(int(x) for x in seq[i : i + motif_len])
                motif_score = motif_counts[motif] / max_motif
            else:
                motif_score = 0.0

        ambiguous = abs(confidence - 0.5) <= 0.14

        if confidence >= 0.82 or (confidence >= 0.70 and motif_score >= 0.25):
            action = "write"
        elif ambiguous or confidence >= 0.52 or motif_score >= 0.35:
            action = "witness"
        else:
            action = "release"
        actions.append(action)

        if action == "write":
            total_writes += 1
            if motif_score < 0.08:
                contradicted_writes += 1
        delayed_candidate = 0.18 <= motif_score <= 0.45 and confidence < 0.72
        if delayed_candidate and action == "witness":
            delayed_meaning_kept += 1
        elif delayed_candidate and action == "release":
            delayed_meaning_missed += 1

    action_counts = Counter(actions)
    pollution = contradicted_writes / total_writes if total_writes else 0.0
    delayed_total = delayed_meaning_kept + delayed_meaning_missed
    delayed_retention = (
        delayed_meaning_kept / delayed_total if delayed_total else 0.0
    )
    return {
        "write_count": float(action_counts["write"]),
        "witness_count": float(action_counts["witness"]),
        "release_count": float(action_counts["release"]),
        "pollution": pollution,
        "delayed_retention": delayed_retention,
    }


def summarize_sequence(seq: np.ndarray, width: int = 96) -> str:
    text = "".join(str(int(x)) for x in seq[:width])
    return text


def score_row(row: dict[str, float]) -> float:
    return (
        2.0 * row["balance_score"]
        + 1.2 * (1.0 - row["balance_spread"] / 4.0)
        + 1.0 * (1.0 - row["complexity_deviation"])
        + 1.0 * (1.0 - row["periodicity_match"])
        + 1.0 * (1.0 - row["pollution"])
        + 1.0 * row["delayed_retention"]
        + 0.5 * row["compression_score"] / max(row["compression_score_cap"], 1e-9)
    )


def plot_family_metric(
    rows: list[dict[str, float]],
    metric: str,
    title: str,
    ylabel: str,
    path: Path,
) -> None:
    families = []
    values = []
    for family in sorted({row["family"] for row in rows}):
        vals = [row[metric] for row in rows if row["family"] == family]
        families.append(family)
        values.append(float(np.mean(vals)))
    plt.figure(figsize=(10, 5))
    plt.bar(families, values, color="#d9a404")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_periodicity(rows: list[dict[str, float]], path: Path) -> None:
    families = sorted({row["family"] for row in rows})
    xs = np.arange(len(families))
    ys = [np.mean([r["periodicity_match"] for r in rows if r["family"] == fam]) for fam in families]
    ps = [np.mean([r["best_period"] for r in rows if r["family"] == fam]) for fam in families]
    plt.figure(figsize=(10, 5))
    plt.bar(xs, ys, color="#795548")
    for x, y, p in zip(xs, ys, ps):
        label = "aperiodic" if p > PERIOD_MAX else f"p~{int(round(p))}"
        plt.text(x, y + 0.005, label, ha="center", fontsize=8)
    plt.xticks(xs, families, rotation=30, ha="right")
    plt.ylabel("exact phase-lock score (1 / shortest period)")
    plt.title("Phase-lock / periodicity by slope family")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_action_counts(rows: list[dict[str, float]], path: Path) -> None:
    families = sorted({row["family"] for row in rows})
    writes = [np.mean([r["write_count"] for r in rows if r["family"] == fam]) for fam in families]
    witness = [np.mean([r["witness_count"] for r in rows if r["family"] == fam]) for fam in families]
    release = [np.mean([r["release_count"] for r in rows if r["family"] == fam]) for fam in families]
    xs = np.arange(len(families))
    plt.figure(figsize=(11, 6))
    plt.bar(xs, writes, label="write", color="#2e7d32")
    plt.bar(xs, witness, bottom=writes, label="witness", color="#f9a825")
    plt.bar(xs, release, bottom=np.array(writes) + np.array(witness), label="release", color="#546e7a")
    plt.xticks(xs, families, rotation=30, ha="right")
    plt.ylabel("mean action count")
    plt.title("Write / witness / release counts by slope family")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def write_csv(rows: list[dict[str, float]], path: Path) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_samples(samples: list[str], path: Path) -> None:
    path.write_text("\n\n".join(samples))


def family_means(rows: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    families = sorted({row["family"] for row in rows})
    numeric_keys = [
        key
        for key, value in rows[0].items()
        if isinstance(value, (int, float)) and key not in {"alpha"}
    ]
    for family in families:
        subset = [row for row in rows if row["family"] == family]
        out[family] = {key: float(np.mean([row[key] for row in subset])) for key in numeric_keys}
    return out


def strongest_and_weakest(rows: list[dict[str, float]]) -> tuple[dict[str, float], dict[str, float]]:
    scored = sorted(rows, key=lambda row: row["composite_score"], reverse=True)
    return scored[0], scored[-1]


def build_report(rows: list[dict[str, float]], path: Path) -> dict[str, str]:
    means = family_means(rows)
    golden = means["golden"]
    rational = means["rational_approx"]
    controls = means["rational_control"]
    random_family = means["random"]
    silver = means["silver"]
    bronze = means["bronze"]

    beat_balance = golden["balance_score"] > max(rational["balance_score"], controls["balance_score"], random_family["balance_score"])
    beat_phase = golden["periodicity_match"] < min(rational["periodicity_match"], controls["periodicity_match"])
    beat_pollution = golden["pollution"] < min(rational["pollution"], random_family["pollution"])
    beat_delayed = golden["delayed_retention"] > max(rational["delayed_retention"], controls["delayed_retention"])
    robust = statistics.pstdev([row["balance_score"] for row in rows if row["family"] == "golden"]) < 0.08

    silver_beats = []
    bronze_beats = []
    for metric in ("balance_score", "delayed_retention", "compression_score"):
        if silver[metric] > golden[metric]:
            silver_beats.append(metric)
        if bronze[metric] > golden[metric]:
            bronze_beats.append(metric)
    for metric in ("periodicity_match", "pollution"):
        if silver[metric] < golden[metric]:
            silver_beats.append(metric)
        if bronze[metric] < golden[metric]:
            bronze_beats.append(metric)

    strongest, weakest = strongest_and_weakest(rows)
    genuine_advantage = sum([beat_balance, beat_phase, beat_pollution, beat_delayed]) >= 3
    deserves_hardening = "yes" if genuine_advantage and robust else "maybe"
    golden_beats_controls = "yes" if beat_balance and beat_phase else "mixed"

    lines = [
        "# Golden Zipper Sturmian Memory Toy Report",
        "",
        "Toy telemetry only. Not physics evidence.",
        "",
        "## Summary",
        "",
        "This toy samples irrational rotations through finite observer windows and treats the resulting binary trail as a candidate memory record. The main comparison is whether the golden slope behaves more like a balanced, non-phase-locked, low-pollution symbolic trail than nearby rational, random, silver, and bronze controls.",
        "",
        "## Setup",
        "",
        "- Rotation rule: `x_(n+1) = (x_n + alpha) mod 1`",
        "- Observer windows: single interval, slowly moving phase window, and two-window bidirectional variant",
        "- Sequence length per run: 4096",
        "- Window sizes: 0.20, 0.34, 0.47",
        "- Window phases: 0.00, 0.17",
        "- Slopes: golden, silver, bronze, rational approximants, rational controls, and random slopes",
        "",
        "## Markov / Memory Policy",
        "",
        "- `write`: high local fit plus short-range future support",
        "- `witness`: ambiguous local fit or delayed-future support",
        "- `release`: low-fit / low-support symbol",
        "",
        "## Family Metric Means",
        "",
        "| Family | Balance | Balance spread | Complexity dev. | Periodicity match | Pollution | Delayed retention | Compression |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for family in sorted(means):
        m = means[family]
        lines.append(
            f"| {family} | {m['balance_score']:.3f} | {m['balance_spread']:.3f} | {m['complexity_deviation']:.3f} | {m['periodicity_match']:.3f} | {m['pollution']:.3f} | {m['delayed_retention']:.3f} | {m['compression_score']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Required Questions",
            "",
            f"1. Does golden/Sturmian sampling produce stronger balance than controls? **{'Yes' if beat_balance else 'No / mixed'}**.",
            f"2. Does golden sampling avoid phase-lock better than rational controls? **{'Yes' if beat_phase else 'No / mixed'}**.",
            f"3. Does golden sampling produce lower pollution or better delayed-meaning retention? **pollution: {'better' if beat_pollution else 'mixed'}; delayed meaning: {'better' if beat_delayed else 'mixed'}**.",
            f"4. Does silver or bronze beat golden on any metric? **silver: {', '.join(silver_beats) if silver_beats else 'no clear wins'}; bronze: {', '.join(bronze_beats) if bronze_beats else 'no clear wins'}**.",
            f"5. Are results robust to window size and phase? **{'reasonably' if robust else 'not strongly'}** within this toy sweep.",
            f"6. Does this support only symbolic intuition, or a genuine toy-model advantage? **{'genuine toy-model advantage' if genuine_advantage else 'mostly symbolic intuition / mixed telemetry'}**.",
            "",
            "## Strongest And Weakest Runs",
            "",
            f"- Strongest run: `{strongest['name']}` / `{strongest['window_type']}` / window={strongest['window_size']:.2f} / phase={strongest['phase']:.2f} / score={strongest['composite_score']:.3f}",
            f"- Weakest run: `{weakest['name']}` / `{weakest['window_type']}` / window={weakest['window_size']:.2f} / phase={weakest['phase']:.2f} / score={weakest['composite_score']:.3f}",
            "",
            "## Interpretation",
            "",
            "The toy does not test physical reality. It tests whether a finite observer window sampling a rotation can produce unusually balanced symbolic memory traces under the golden slope. The most meaningful positive outcome here is not 'phi is reality'; it is the narrower possibility that golden/Sturmian sampling gives a useful symbolic compromise between balance, non-repetition, and delayed-meaning retention.",
            "",
            "## Do-Not-Claim Ledger",
            "",
            "- does not prove GHP",
            "- does not prove phi is the code of reality",
            "- does not prove memory creates matter",
            "- does not prove VPH",
            "- does not prove consciousness",
            "- does not count as physics evidence",
            "- does not close the write-law",
            "",
            "## Final Toy Verdict",
            "",
            f"- strongest result: `{strongest['name']}`",
            f"- weakest result: `{weakest['name']}`",
            f"- whether golden slope beat controls: **{golden_beats_controls}**",
            f"- whether this deserves master hardening: **{deserves_hardening}**",
        ]
    )

    path.write_text("\n".join(lines))
    return {
        "golden_beats_controls": golden_beats_controls,
        "deserves_hardening": deserves_hardening,
        "strongest_result": strongest["name"],
        "weakest_result": weakest["name"],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slopes = build_slopes()
    rows: list[dict[str, float]] = []
    sample_lines = []

    compression_cap = 0.0
    for slope in slopes:
        for window_type in WINDOW_TYPES:
            for window_size in WINDOW_SIZES:
                for phase in WINDOW_PHASES:
                    seq = generate_sequence(slope.alpha, STEPS, window_size, phase, window_type)
                    balance_score, balance_spread = balance_metrics(seq)
                    complexity_ratio, complexity_deviation = complexity_metrics(seq)
                    periodicity_match, best_period = periodicity_metrics(seq)
                    policy = memory_policy(seq)
                    compression_score = compression_metric(seq)
                    compression_cap = max(compression_cap, compression_score)

                    row = {
                        "name": slope.name,
                        "family": slope.family,
                        "alpha": slope.alpha,
                        "window_type": window_type,
                        "window_size": window_size,
                        "phase": phase,
                        "balance_score": balance_score,
                        "balance_spread": balance_spread,
                        "complexity_ratio": complexity_ratio,
                        "complexity_deviation": complexity_deviation,
                        "periodicity_match": periodicity_match,
                        "best_period": best_period,
                        "write_count": policy["write_count"],
                        "witness_count": policy["witness_count"],
                        "release_count": policy["release_count"],
                        "pollution": policy["pollution"],
                        "delayed_retention": policy["delayed_retention"],
                        "compression_score": compression_score,
                        "compression_score_cap": 1.0,  # temporary; normalized later
                    }
                    rows.append(row)
                    if phase == WINDOW_PHASES[0] and window_size == WINDOW_SIZES[1]:
                        sample_lines.append(
                            f"[{slope.name} | {window_type} | alpha={slope.alpha:.12f}] {summarize_sequence(seq)}"
                        )

    for row in rows:
        row["compression_score_cap"] = compression_cap or 1.0
        row["composite_score"] = score_row(row)

    write_csv(rows, OUTPUT_DIR / "metrics.csv")
    write_samples(sample_lines, OUTPUT_DIR / "sample_sequences.txt")

    plot_family_metric(
        rows,
        "balance_score",
        "Balance score by slope family",
        "mean balance score",
        OUTPUT_DIR / "balance_plot.png",
    )
    plot_family_metric(
        rows,
        "complexity_deviation",
        "Complexity deviation from Sturmian ideal",
        "mean deviation",
        OUTPUT_DIR / "complexity_plot.png",
    )
    plot_periodicity(rows, OUTPUT_DIR / "periodicity_plot.png")
    plot_action_counts(rows, OUTPUT_DIR / "write_witness_release_counts.png")

    summary = build_report(rows, OUTPUT_DIR / "report.md")

    print(f"files created: {OUTPUT_DIR}")
    print(f"strongest result: {summary['strongest_result']}")
    print(f"weakest result: {summary['weakest_result']}")
    print(f"whether golden slope beat controls: {summary['golden_beats_controls']}")
    print(f"whether this deserves master hardening: {summary['deserves_hardening']}")


if __name__ == "__main__":
    main()
