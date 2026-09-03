#!/usr/bin/env python3
"""Score the frozen post-hoc controls, emitting every pseudo score first."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Sequence

import mpmath as mp


HERE = Path(__file__).resolve().parent
BLIND = HERE / "outputs" / "posthoc-matched-controls-blind.json"
OUTPUT = HERE / "outputs" / "posthoc-matched-controls-scored.json"
INDICES = list(range(20, 51))
LANDING_RMSE = mp.mpf("0.01")
LANDING_MAXIMUM = mp.mpf("0.05")
TRUE_ARTIFACTS = {
    (14, 112): "mutation-x14-N112-dps100.json",
    (14, 120): "true-x14-N120-dps100.json",
    (14, 128): "mutation-x14-N128-dps100.json",
    (14, 140): "npath-x14-N140-dps100.json",
    (14, 168): "npath-x14-N168-dps100.json",
    (16, 128): "npath-x16-N128-dps100.json",
    (16, 160): "npath-x16-N160-dps100.json",
    (16, 192): "npath-x16-N192-dps100.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(roots: Sequence[str], targets: Sequence[mp.mpf]) -> dict[str, object]:
    selected = [mp.mpf(roots[index - 1]) for index in INDICES]
    errors = [candidate - target for candidate, target in zip(selected, targets)]
    absolute = [abs(error) for error in errors]
    rmse = mp.sqrt(mp.fsum(error * error for error in errors) / len(errors))
    maximum = max(absolute)
    return {
        "rmse": mp.nstr(rmse, 90),
        "maximum_absolute_error": mp.nstr(maximum, 90),
        "median_absolute_error": mp.nstr(sorted(absolute)[len(absolute) // 2], 90),
        "lands": bool(rmse <= LANDING_RMSE and maximum <= LANDING_MAXIMUM),
    }


def main() -> None:
    blind = json.loads(BLIND.read_text(encoding="utf-8"))
    if blind.get("target_data_present") is not False or blind.get("scoring_present") is not False:
        raise RuntimeError("blind artifact is contaminated by target/scoring data")
    if not blind.get("source_audit", {}).get("passed"):
        raise RuntimeError("blind artifact source audit failed")
    expected_pairs = [list(pair) for pair in TRUE_ARTIFACTS]
    if blind.get("parameters", {}).get("pairs") != expected_pairs:
        raise RuntimeError("blind artifact pair grid mismatch")
    records_by_pair = {
        (int(row["x"]), int(row["N"])): row for row in blind["records"]
    }
    if set(records_by_pair) != set(TRUE_ARTIFACTS) or len(records_by_pair) != len(blind["records"]):
        raise RuntimeError("blind artifact does not cover every pair exactly once")
    if any(len(row[k]["spectrum"]["positive_roots"]) < max(INDICES)
           for row in blind["records"] for k in ("pseudo_prime", "archimedean_only", "prolate_only")):
        raise RuntimeError("blind artifact has too few roots")

    mp.mp.dps = 110
    targets = [mp.im(mp.zetazero(index)) for index in INDICES]

    # Compute and emit the entire pseudo-prime block before any other accuracy.
    pseudo_scores = []
    for row in blind["records"]:
        metric = score(row["pseudo_prime"]["spectrum"]["positive_roots"], targets)
        pseudo_scores.append({"x": row["x"], "N": row["N"], **metric})
    print(json.dumps({
        "first_reported_accuracy_kind": "post-hoc parameter-matched pseudo-prime controls",
        "ordinal_indices": INDICES,
        "scores": pseudo_scores,
    }), flush=True)

    arch_scores = []
    prolate_scores = []
    true_scores = []
    for row in blind["records"]:
        key = (int(row["x"]), int(row["N"]))
        arch_scores.append({
            "x": key[0], "N": key[1],
            **score(row["archimedean_only"]["spectrum"]["positive_roots"], targets),
        })
        prolate_scores.append({
            "x": key[0], "N": key[1],
            **score(row["prolate_only"]["spectrum"]["positive_roots"], targets),
        })
        true_path = HERE / TRUE_ARTIFACTS[key]
        true_payload = json.loads(true_path.read_text(encoding="utf-8"))
        if (int(true_payload["parameters"]["x"]), int(true_payload["parameters"]["N"])) != key:
            raise RuntimeError(f"true-artifact parameter mismatch in {true_path.name}")
        true_scores.append({
            "x": key[0], "N": key[1], "artifact": true_path.name,
            **score(true_payload["positive_roots"], targets),
        })

    rows = []
    for pseudo, arch, prolate_row, true in zip(
        pseudo_scores, arch_scores, prolate_scores, true_scores
    ):
        key = (int(true["x"]), int(true["N"]))
        blind_row = records_by_pair[key]
        controls_present = all(
            name in blind_row for name in ("pseudo_prime", "archimedean_only", "prolate_only")
        )
        control_root_counts_sufficient = controls_present and all(
            len(blind_row[name]["spectrum"]["positive_roots"]) >= max(INDICES)
            for name in ("pseudo_prime", "archimedean_only", "prolate_only")
        )
        scores_present = all(
            isinstance(item.get("rmse"), str)
            and isinstance(item.get("maximum_absolute_error"), str)
            and isinstance(item.get("lands"), bool)
            for item in (pseudo, arch, prolate_row, true)
        )
        rows.append({
            "x": true["x"],
            "N": true["N"],
            "true_lands": true["lands"],
            "pseudo_lands": pseudo["lands"],
            "archimedean_lands": arch["lands"],
            "prolate_only_lands": prolate_row["lands"],
            "controls_present": controls_present,
            "control_root_counts_sufficient": control_root_counts_sufficient,
            "scores_present": scores_present,
            "coverage_complete": bool(
                true["lands"]
                and controls_present
                and control_root_counts_sufficient
                and scores_present
            ),
        })
    if not all(row["true_lands"] for row in rows):
        raise RuntimeError("the audited pair grid includes a nonmatching true spectrum")

    complete_coverage = all(row["coverage_complete"] for row in rows)
    if not complete_coverage:
        raise RuntimeError("a matching true spectrum lacks a same-(x,N) scored control")

    payload = {
        "schema": "codex-r5-posthoc-matched-controls-scored-v1",
        "status": "MEASURED",
        "registration": "post-hoc audit; not preregistered",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "blind_artifact": BLIND.name,
        "blind_artifact_sha256": sha256(BLIND),
        "scoring_order": ["pseudo_prime_scores", "archimedean_only_scores", "prolate_only_scores", "true_scores"],
        "pseudo_was_first_reported_accuracy": True,
        "target_indices": INDICES,
        "landing_rule": {"rmse_at_most": "0.01", "maximum_at_most": "0.05"},
        "pseudo_prime_scores": pseudo_scores,
        "archimedean_only_scores": arch_scores,
        "prolate_only_scores": prolate_scores,
        "true_scores": true_scores,
        "coverage": rows,
        "summary": {
            "pair_count": len(rows),
            "true_landing_count": sum(row["lands"] for row in true_scores),
            "pseudo_landing_count": sum(row["lands"] for row in pseudo_scores),
            "archimedean_landing_count": sum(row["lands"] for row in arch_scores),
            "prolate_only_landing_count": sum(row["lands"] for row in prolate_scores),
            "all_true_matches_have_parameter_matched_pseudo_arch_and_prolate_controls": complete_coverage,
        },
    }
    # Deliberately retain insertion order: pseudo metrics precede every other
    # accuracy block in the persistent output, as they did on stdout.
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), **payload["summary"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
