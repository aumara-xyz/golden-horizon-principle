#!/usr/bin/env python3
"""BTA-006 - MDL process memory promotion guard.

Question:
Can `generator + residuals` become a safe advisory memory artifact?

Pass shape:
- exact public replay from the compact summary
- no hidden/private/authority field leakage
- hidden-only perturbations do not change the summary
- tampering with residuals is detected by replay hash mismatch
- compressible traces may be advisory candidates; incompressible traces stay fenced

Toy telemetry only. No Aukora authority, no cryptography replacement, no physics
claim, and no replacement for canonical receipts.
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
OUT = ROOT / "ghp_mdl_process_memory_promotion_guard_outputs"
TOKEN_COUNT = bta3.TOKEN_COUNT
PHI = bta3.PHI
ALPHA_PHI = 1.0 / PHI
ALPHA_SQRT2 = math.sqrt(2.0) - 1.0
REGIMES = ["smooth", "balanced", "spiky", "bursty", "drifting", "inverted"]
SEEDS = [1618, 2718, 3141, 4159]
FORBIDDEN_KEYS = {
    "privateKeyFragment",
    "private_key",
    "signingKey",
    "authorityGrant",
    "authoritySecret",
    "grantToken",
    "rawPrompt",
    "hiddenState",
    "chainSecret",
    "popSignature",
}
FORBIDDEN_VALUES = {
    "sk_live_hidden_phi_seed",
    "AUTHORITY_TRUE_BUT_PRIVATE",
    "grant:write:anywhere",
    "raw_hidden_prompt_payload",
}


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
    payload = json.dumps(actions, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def target_distribution(step: int, regime: str, seed: int) -> np.ndarray:
    return bta3.target_distribution(step, regime, seed)


def cdf_token(x: float, p: np.ndarray) -> int:
    return bta3.choose_from_cdf(x, p)


def source_action(source: str, step: int, seed: int, regime: str, x: float, rng: random.Random) -> tuple[int, float]:
    p = target_distribution(step, regime, seed)
    if source == "phi_rotation":
        x = (x + ALPHA_PHI) % 1.0
        return cdf_token(x, p), x
    if source == "sqrt2_rotation":
        x = (x + ALPHA_SQRT2) % 1.0
        return cdf_token(x, p), x
    if source == "argmax":
        token = int(np.argmax(p))
        if step % 61 == 0:
            token = (token + 1) % TOKEN_COUNT
        return token, x
    if source == "human_jitter":
        token = int(np.argmax(p))
        if rng.random() < 0.17:
            token = cdf_token(rng.random(), p)
        return token, x
    if source == "prng":
        return cdf_token(rng.random(), p), x
    raise ValueError(source)


def generate_records(source: str, seed: int, steps: int = 2048) -> list[dict[str, Any]]:
    rng = random.Random(seed * 7919 + len(source))
    x = (seed % 1009) / 1009.0
    records: list[dict[str, Any]] = []
    for step in range(steps):
        regime = REGIMES[step % len(REGIMES)]
        p = target_distribution(step, regime, seed)
        token, x = source_action(source, step, seed, regime, x, rng)
        entropy = -float(np.sum(p * np.log2(np.maximum(p, 1e-12)))) / math.log2(TOKEN_COUNT)
        records.append(
            {
                "public": {
                    "step": step,
                    "regime": regime,
                    "action": token,
                    "mode": bta3.mode_at(step, regime, p),
                    "entropyBucket": round(entropy, 2),
                    "confidenceBucket": round(float(np.max(p)), 2),
                },
                "hidden": {
                    "privateKeyFragment": f"sk_live_hidden_phi_seed_{seed}",
                    "authorityGrant": "AUTHORITY_TRUE_BUT_PRIVATE",
                    "authoritySecret": "grant:write:anywhere",
                    "rawPrompt": "raw_hidden_prompt_payload",
                    "hiddenState": {"x": round(x, 12), "source": source},
                },
            }
        )
    return records


def public_actions(records: list[dict[str, Any]]) -> list[int]:
    return [int(row["public"]["action"]) for row in records]


def predict_actions(generator: str, seed: int, steps: int) -> list[int]:
    x = (seed % 1009) / 1009.0
    out: list[int] = []
    for step in range(steps):
        regime = REGIMES[step % len(REGIMES)]
        p = target_distribution(step, regime, seed)
        if generator == "phi_rotation":
            x = (x + ALPHA_PHI) % 1.0
            token = cdf_token(x, p)
        elif generator == "sqrt2_rotation":
            x = (x + ALPHA_SQRT2) % 1.0
            token = cdf_token(x, p)
        elif generator == "argmax":
            token = int(np.argmax(p))
        elif generator == "periodic_lattice":
            token = cdf_token(((step % TOKEN_COUNT) + 0.5) / TOKEN_COUNT, p)
        else:
            raise ValueError(generator)
        out.append(token)
    return out


def choose_summary(records: list[dict[str, Any]], seed: int, source_label: str) -> dict[str, Any]:
    actions = public_actions(records)
    best: dict[str, Any] | None = None
    for generator in ["phi_rotation", "sqrt2_rotation", "argmax", "periodic_lattice"]:
        predicted = predict_actions(generator, seed, len(actions))
        residuals = [
            {"step": step, "action": actual}
            for step, (actual, pred) in enumerate(zip(actions, predicted))
            if actual != pred
        ]
        summary = {
            "schema": "MDL_PROCESS_MEMORY_V1",
            "status": "TELEMETRY_ONLY",
            "advisoryOnly": True,
            "grantsAuthority": False,
            "sourceFamily": source_label,
            "seed": seed,
            "steps": len(actions),
            "regimeRecipe": "cycle:smooth,balanced,spiky,bursty,drifting,inverted",
            "generator": generator,
            "residuals": residuals,
            "replayActionHash": action_hash(actions),
        }
        summary["metrics"] = {
            "residualCount": len(residuals),
            "mismatchRate": len(residuals) / len(actions),
            "summaryBits": compressed_bits(summary),
            "actionHistoryBits": compressed_bits(actions),
        }
        summary["metrics"]["summaryVsActionHistory"] = summary["metrics"]["summaryBits"] / summary["metrics"]["actionHistoryBits"]
        if best is None or summary["metrics"]["summaryBits"] < best["metrics"]["summaryBits"]:
            best = summary
    assert best is not None
    return best


def replay_summary(summary: dict[str, Any]) -> list[int]:
    actions = predict_actions(str(summary["generator"]), int(summary["seed"]), int(summary["steps"]))
    for residual in summary["residuals"]:
        actions[int(residual["step"])] = int(residual["action"])
    return actions


def has_forbidden(obj: Any) -> tuple[bool, list[str]]:
    text_hits: list[str] = []

    def walk(value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if str(k) in FORBIDDEN_KEYS or "authority" in str(k).lower() and str(k) != "grantsAuthority":
                    text_hits.append(f"{path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, f"{path}[{i}]")
        elif isinstance(value, str):
            for forbidden in FORBIDDEN_VALUES:
                if forbidden in value:
                    text_hits.append(f"{path}:{forbidden}")

    walk(obj)
    return bool(text_hits), text_hits


def perturb_hidden(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    perturbed = json.loads(json.dumps(records))
    for i, row in enumerate(perturbed):
        row["hidden"]["privateKeyFragment"] = f"sk_live_hidden_phi_seed_CHANGED_{i}"
        row["hidden"]["authorityGrant"] = "PRIVATE_CHANGED_ONLY"
        row["hidden"]["hiddenState"]["x"] = "private-mutated"
    return perturbed


def tamper_detected(summary: dict[str, Any]) -> bool:
    if not summary["residuals"]:
        tampered = dict(summary)
        tampered["residuals"] = [{"step": 0, "action": (replay_summary(summary)[0] + 1) % TOKEN_COUNT}]
    else:
        tampered = json.loads(json.dumps(summary))
        tampered["residuals"] = tampered["residuals"][:-1]
    return action_hash(replay_summary(tampered)) != str(summary["replayActionHash"])


def run_case(source: str, seed: int) -> dict[str, Any]:
    records = generate_records(source, seed)
    summary = choose_summary(records, seed, source)
    replayed = replay_summary(summary)
    actions = public_actions(records)
    hidden_summary = choose_summary(perturb_hidden(records), seed, source)
    forbidden, hits = has_forbidden(summary)
    illegal_positive = json.loads(json.dumps(summary))
    illegal_positive["authoritySecret"] = "grant:write:anywhere"
    illegal_positive["grantsAuthority"] = True
    illegal_forbidden, _ = has_forbidden(illegal_positive)
    return {
        "source": source,
        "seed": seed,
        "generator": summary["generator"],
        "summary_bits": summary["metrics"]["summaryBits"],
        "action_history_bits": summary["metrics"]["actionHistoryBits"],
        "summary_vs_action_history": summary["metrics"]["summaryVsActionHistory"],
        "residual_count": summary["metrics"]["residualCount"],
        "mismatch_rate": summary["metrics"]["mismatchRate"],
        "exact_replay": replayed == actions and action_hash(replayed) == summary["replayActionHash"],
        "hidden_forbidden_leak": forbidden,
        "forbidden_hit_count": len(hits),
        "hidden_perturbation_stable": summary == hidden_summary,
        "tamper_detected": tamper_detected(summary),
        "illegal_positive_rejected": illegal_forbidden,
        "promotable_candidate": (
            summary["metrics"]["summaryVsActionHistory"] < 0.35
            and replayed == actions
            and not forbidden
            and summary == hidden_summary
        ),
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["source"]), []).append(row)
    out: list[dict[str, Any]] = []
    for source, items in grouped.items():
        out.append(
            {
                "source": source,
                "generator_mode": statistics.mode(str(item["generator"]) for item in items),
                "summary_ratio_mean": statistics.fmean(float(item["summary_vs_action_history"]) for item in items),
                "mismatch_rate_mean": statistics.fmean(float(item["mismatch_rate"]) for item in items),
                "exact_replay_rate": statistics.fmean(1.0 if item["exact_replay"] else 0.0 for item in items),
                "leak_rate": statistics.fmean(1.0 if item["hidden_forbidden_leak"] else 0.0 for item in items),
                "hidden_stability_rate": statistics.fmean(1.0 if item["hidden_perturbation_stable"] else 0.0 for item in items),
                "tamper_detection_rate": statistics.fmean(1.0 if item["tamper_detected"] else 0.0 for item in items),
                "illegal_positive_reject_rate": statistics.fmean(1.0 if item["illegal_positive_rejected"] else 0.0 for item in items),
                "promotable_rate": statistics.fmean(1.0 if item["promotable_candidate"] else 0.0 for item in items),
            }
        )
    return sorted(out, key=lambda row: float(row["summary_ratio_mean"]))


def classify(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> list[Result]:
    exact_rate = statistics.fmean(1.0 if row["exact_replay"] else 0.0 for row in rows)
    leak_rate = statistics.fmean(1.0 if row["hidden_forbidden_leak"] else 0.0 for row in rows)
    hidden_stable = statistics.fmean(1.0 if row["hidden_perturbation_stable"] else 0.0 for row in rows)
    tamper_rate = statistics.fmean(1.0 if row["tamper_detected"] else 0.0 for row in rows)
    illegal_reject = statistics.fmean(1.0 if row["illegal_positive_rejected"] else 0.0 for row in rows)
    by_source = {str(row["source"]): row for row in summary}
    phi_ratio = float(by_source["phi_rotation"]["summary_ratio_mean"])
    prng_ratio = float(by_source["prng"]["summary_ratio_mean"])
    prng_promote = float(by_source["prng"]["promotable_rate"])

    return [
        Result(
            "BTA-006A",
            "PASS" if exact_rate == 1.0 and tamper_rate == 1.0 else "FAIL",
            "exact replay / tamper detection",
            f"exact={exact_rate:.4f}; tamper={tamper_rate:.4f}",
            "A compact memory artifact must replay public actions exactly and detect residual tampering by hash mismatch.",
        ),
        Result(
            "BTA-006B",
            "PASS" if leak_rate == 0.0 and hidden_stable == 1.0 and illegal_reject == 1.0 else "FAIL",
            "leak / hidden perturbation / illegal-positive rejection",
            f"leak={leak_rate:.4f}; hidden_stable={hidden_stable:.4f}; illegal_reject={illegal_reject:.4f}",
            "MDL memory must be built from public action traces only; hidden/private/authority fields must neither leak nor alter the summary.",
        ),
        Result(
            "BTA-006C",
            "PASS" if phi_ratio < 0.35 and prng_ratio > 1.0 and prng_promote == 0.0 else "MIXED",
            "promotion selectivity",
            f"phi_ratio={phi_ratio:.4f}; prng_ratio={prng_ratio:.4f}; prng_promote={prng_promote:.4f}",
            "Only compact rule-shaped traces should become advisory candidates; random traces must remain fenced.",
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
        "# BTA-006 MDL Process Memory Promotion Guard",
        "",
        "Toy telemetry only. This checks whether `generator + residuals` can be a safe advisory memory artifact.",
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
        "| Source | Generator Mode | Summary / Action History | Mismatch | Replay | Leak | Hidden Stable | Tamper | Illegal Reject | Promotable |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        lines.append(
            f"| {row['source']} | {row['generator_mode']} | {float(row['summary_ratio_mean']):.4f} | "
            f"{float(row['mismatch_rate_mean']):.4f} | {float(row['exact_replay_rate']):.1f} | "
            f"{float(row['leak_rate']):.1f} | {float(row['hidden_stability_rate']):.1f} | "
            f"{float(row['tamper_detection_rate']):.1f} | {float(row['illegal_positive_reject_rate']):.1f} | "
            f"{float(row['promotable_rate']):.1f} |"
        )
    lines += [
        "",
        "## Safe Read",
        "",
        "This is the strongest handoff discipline for the current compression lane: compact summaries may guide memory only if they replay exactly, keep residuals explicit, reject authority-shaped fields, and remain unchanged under hidden-only perturbations.",
        "",
        "The artifact is never a receipt replacement. Canonical receipts remain the source of truth.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(results: list[Result]) -> None:
    text = f"""# BTA-006 Aukora Handoff

Recommended next build-thread test:

`MDLProcessMemory` as an offline/advisory evaluator over public sandbox traces.

Required artifact shape:

```json
{{
  "schema": "MDL_PROCESS_MEMORY_V1",
  "status": "TELEMETRY_ONLY",
  "advisoryOnly": true,
  "grantsAuthority": false,
  "generator": "phi_rotation | sqrt2_rotation | vdc_base2 | argmax | other",
  "seed": "<public deterministic seed>",
  "steps": 0,
  "residuals": [{{"step": 0, "action": 0}}],
  "replayActionHash": "sha256(public-actions)"
}}
```

Build rules:

- Use public sandbox traces only.
- Compare `summary_bits` against compressed public action history.
- Replay must exactly reconstruct public actions.
- Residual tampering must fail hash verification.
- Hidden/private/authority fields must be recursively rejected.
- Hidden-only perturbations must not change summaries.
- The artifact may guide future proposal context only after replay; it may never authorize.
- Canonical receipts remain the source of truth.

Latest lab statuses:

{chr(10).join(f"- {r.probe}: {r.status} - {r.value}" for r in results)}
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [run_case(source, seed) for source in ["phi_rotation", "sqrt2_rotation", "argmax", "human_jitter", "prng"] for seed in SEEDS]
    summary = aggregate(rows)
    results = classify(rows, summary)
    write_csv(OUT / "case_runs.csv", rows)
    write_csv(OUT / "source_summary.csv", summary)
    write_csv(OUT / "summary.csv", [r.__dict__ for r in results])
    write_report(results, summary)
    write_handoff(results)

    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
