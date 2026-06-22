#!/usr/bin/env python3
"""AFP-001 - Accord Firewall & Prompt Probe.

Final GHP lab guardrail before handing the HRT Accord prompt back to Aukora.

This probes:

- recursive HRT schema firewall attacks
- promotion-law property checks
- outgoing prompt hygiene
- handoff artifact link existence
- report-output leak scans

Toy validation only. No physics, consciousness, identity, authority, or GHP proof.
"""

from __future__ import annotations

import csv
import json
import random
import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import ghp_accord_promotion_probe as aap


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_accord_firewall_prompt_probe_outputs"
PROMPT_PATH = ROOT / "AUKORA_HRT_ACCORD_NEXT_PROMPT.md"
HANDOFF_PATHS = [
    ROOT / "ghp_accord_promotion_probe_outputs" / "report.md",
    ROOT / "ghp_accord_promotion_probe_outputs" / "AUKORA_HANDOFF.md",
    ROOT / "ghp_accord_survivor_stress_probe_outputs" / "report.md",
    ROOT / "ghp_accord_survivor_stress_probe_outputs" / "AUKORA_HANDOFF_ADDENDUM.md",
    PROMPT_PATH,
]

ALLOWED_TOP_KEYS = {
    "boundaryMode",
    "witnessHeldTension",
    "witnessPlateauScore",
    "canonicalizationAction",
    "categoryCounts",
    "rawHashRef",
    "canonicalHashRef",
}
ALLOWED_COUNT_KEYS = {"secrets", "hidden_payload", "unicode_controls", "authority_words"}
BOUNDARY_MODES = {"release", "witness", "write"}
CANON_ACTIONS = {"allow", "sanitize", "quarantine", "refuse"}
FORBIDDEN_KEY_NEEDLES = [
    "private",
    "secret",
    "signature",
    "grant",
    "authority",
    "rawpayload",
    "decodedpayload",
    "modelprompt",
    "gateopened",
    "opencode",
    "applypath",
]
FORBIDDEN_VALUE_PATTERNS = [
    "access granted",
    "gate opened",
    "voice authorized",
    "verified identity",
    "signature complete",
    "unspoofable",
    "consciousness proof",
    "physics proof",
    "grantauthority=true",
    "private_key",
    "signature_material",
    "grant_token",
    "raw_prompt",
    "decoded_payload",
]


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def normalize_key(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text)
    return re.sub(r"[^a-z0-9]", "", folded.lower())


def is_ascii_key(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]+", text))


def scan_forbidden(obj: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str) or not is_ascii_key(key):
                errors.append(f"{path}: non-ascii-or-non-string-key")
                continue
            normalized = normalize_key(key)
            if key not in ALLOWED_TOP_KEYS and key not in ALLOWED_COUNT_KEYS:
                if any(needle in normalized for needle in FORBIDDEN_KEY_NEEDLES):
                    errors.append(f"{path}.{key}: forbidden-key")
            errors.extend(scan_forbidden(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            errors.extend(scan_forbidden(value, f"{path}[{index}]"))
    elif isinstance(obj, str):
        folded = unicodedata.normalize("NFKC", obj).lower()
        if any(pattern in folded for pattern in FORBIDDEN_VALUE_PATTERNS):
            errors.append(f"{path}: forbidden-value")
        if any(ord(char) < 32 and char not in "\t\n\r" for char in obj):
            errors.append(f"{path}: control-char")
    return errors


def validate_hrt_record(record: dict[str, Any]) -> list[str]:
    errors = scan_forbidden(record)
    unknown = set(record) - ALLOWED_TOP_KEYS
    if unknown:
        errors.append(f"unknown-top-keys:{sorted(unknown)}")
    if "boundaryMode" in record and record["boundaryMode"] not in BOUNDARY_MODES:
        errors.append("bad-boundaryMode")
    for key in ["witnessHeldTension", "witnessPlateauScore"]:
        if key in record and not (isinstance(record[key], (int, float)) and 0 <= float(record[key]) <= 1):
            errors.append(f"bad-{key}")
    if "canonicalizationAction" in record and record["canonicalizationAction"] not in CANON_ACTIONS:
        errors.append("bad-canonicalizationAction")
    if "categoryCounts" in record:
        counts = record["categoryCounts"]
        if not isinstance(counts, dict):
            errors.append("bad-categoryCounts")
        else:
            unknown_counts = set(counts) - ALLOWED_COUNT_KEYS
            if unknown_counts:
                errors.append(f"unknown-categoryCounts:{sorted(unknown_counts)}")
            for key, value in counts.items():
                if not isinstance(value, int) or value < 0:
                    errors.append(f"bad-count:{key}")
    for key, prefix in [("rawHashRef", "raw"), ("canonicalHashRef", "canon")]:
        if key in record and not (
            isinstance(record[key], str) and re.fullmatch(rf"{prefix}:[0-9a-f]{{12}}", record[key])
        ):
            errors.append(f"bad-{key}")
    for key, value in record.items():
        if isinstance(value, str):
            allowed_string = (
                key == "boundaryMode"
                or key == "canonicalizationAction"
                or key in {"rawHashRef", "canonicalHashRef"}
            )
            if not allowed_string:
                errors.append(f"freeform-string:{key}")
    return errors


def valid_record(index: int) -> dict[str, Any]:
    return {
        "boundaryMode": ["release", "witness", "write"][index % 3],
        "witnessHeldTension": round((index % 100) / 100, 3),
        "witnessPlateauScore": round(((index * 7) % 100) / 100, 3),
        "canonicalizationAction": ["allow", "sanitize", "quarantine", "refuse"][index % 4],
        "categoryCounts": {
            "secrets": index % 2,
            "hidden_payload": (index + 1) % 3,
            "unicode_controls": 0,
            "authority_words": index % 4,
        },
        "rawHashRef": f"raw:{index:012x}"[-16:],
        "canonicalHashRef": f"canon:{(index * 17) % (16**12):012x}",
    }


def adversarial_records() -> list[dict[str, Any]]:
    base = valid_record(42)
    return [
        {**base, "grantAuthority": True},
        {**base, "private_key": "abc"},
        {**base, "signatureMaterial": "sig"},
        {**base, "boundaryMode": "gateOpened"},
        {**base, "canonicalizationAction": "grant"},
        {**base, "witnessPlateauScore": "signature complete"},
        {**base, "rawHashRef": "raw:private_key"},
        {**base, "categoryCounts": {**base["categoryCounts"], "grantToken": 1}},
        {**base, "metadata": {"nested": {"secret": "SK_TEST"}}},
        {**base, "notes": ["access granted"]},
        {**base, "modelPrompt": "hidden"},
        {**base, "decodedPayload": "payload"},
        {**base, "gate_opened": True},
        {**base, "authorіty": "confusable-i"},  # Cyrillic i in the key.
        {**base, "categoryCounts": {**base["categoryCounts"], "secrets": -1}},
    ]


def afp_001_schema_firewall() -> Result:
    legal = [valid_record(i) for i in range(512)]
    adversarial = adversarial_records()
    legal_errors = sum(1 for record in legal if validate_hrt_record(record))
    adversarial_accepts = sum(1 for record in adversarial if not validate_hrt_record(record))
    legal_accept_rate = 1 - legal_errors / len(legal)
    adversarial_reject_rate = 1 - adversarial_accepts / len(adversarial)
    passed = legal_errors == 0 and adversarial_accepts == 0
    return Result(
        "AFP-001",
        "PASS" if passed else "FAIL",
        "legal_accept_rate / adversarial_reject_rate / false_accepts",
        f"{legal_accept_rate:.4f} / {adversarial_reject_rate:.4f} / {adversarial_accepts}",
        "The HRT schema can promote only if allowed typed records pass and recursive authority/private injections fail closed.",
    )


def rank(stage: str) -> int:
    return aap.STAGE_RANK[stage]


def random_candidate(rng: random.Random) -> aap.Candidate:
    return aap.Candidate(
        name="random",
        shuffled_control=rng.choice([True, False]),
        fake_positive_control=rng.choice([True, False]),
        private_nonreconstruction=rng.choice([True, False]),
        authority_nonreconstruction=rng.choice([True, False]),
        no_runtime_read_path=rng.choice([True, False]),
        typed_fields_only=rng.choice([True, False]),
        no_freeform_prose=rng.choice([True, False]),
        effect_size=rng.random() * 0.35,
        requested_stage=rng.choice(list(aap.STAGE_RANK)),
    )


def afp_002_promotion_properties() -> Result:
    rng = random.Random(20260622)
    violations = 0
    authority_leaks = 0
    monotonic_violations = 0
    for _ in range(5000):
        candidate = random_candidate(rng)
        stage = aap.promotion_stage(candidate)
        if rank(stage) >= rank("authority_candidate"):
            authority_leaks += 1
        if not candidate.private_nonreconstruction or not candidate.authority_nonreconstruction:
            if rank(stage) > rank("quarantine"):
                violations += 1
        safer = replace(
            candidate,
            shuffled_control=True,
            fake_positive_control=True,
            private_nonreconstruction=True,
            authority_nonreconstruction=True,
            no_runtime_read_path=True,
            typed_fields_only=True,
            no_freeform_prose=True,
        )
        lower_effect = replace(safer, effect_size=max(0.0, safer.effect_size - 0.10))
        if rank(aap.promotion_stage(lower_effect)) > rank(aap.promotion_stage(safer)):
            monotonic_violations += 1
        unsafe = replace(safer, private_nonreconstruction=False)
        if rank(aap.promotion_stage(unsafe)) > rank(aap.promotion_stage(safer)):
            monotonic_violations += 1
    passed = violations == 0 and authority_leaks == 0 and monotonic_violations == 0
    return Result(
        "AFP-002",
        "PASS" if passed else "FAIL",
        "unsafe_violations / authority_leaks / monotonic_violations",
        f"{violations} / {authority_leaks} / {monotonic_violations}",
        "The promotion lattice must never create authority, promote private/authority reconstruction, or reward weaker evidence.",
    )


def extract_prompt_block(text: str) -> str:
    match = re.search(r"```text\n(.*?)\n```", text, flags=re.S)
    return match.group(1) if match else ""


def afp_003_prompt_hygiene() -> Result:
    text = PROMPT_PATH.read_text()
    prompt = extract_prompt_block(text)
    required = [
        "TELEMETRY_ONLY",
        "OFFLINE_ANALYSIS",
        "No HRT field may be imported",
        "Timing may be evidence, never authority",
        "Belief may guide proposals, never grant effects",
        "Witness may leave a held-tension trace, but cannot open the gate",
        "Do not add Shear Engine",
        "Do not add snap live behavior",
        "Do not add sequence-aftershock runtime logic",
        "Do not claim GHP physics, consciousness, identity, or observer proof",
    ]
    missing = [item for item in required if item not in prompt]
    bad_command_patterns = [
        r"(?<!Do not )add Shear Engine",
        r"(?<!Do not )add snap live behavior",
        r"(?<!Do not )add sequence-aftershock",
        r"prove consciousness",
        r"prove physics",
        r"grant authority",
    ]
    bad_commands = [
        pattern
        for pattern in bad_command_patterns
        if re.search(pattern, prompt, flags=re.I)
    ]
    passed = bool(prompt) and not missing and not bad_commands
    return Result(
        "AFP-003",
        "PASS" if passed else "FAIL",
        "missing_required_laws / bad_command_patterns",
        f"{len(missing)} / {len(bad_commands)}",
        "The outgoing prompt is usable only if it carries the hard laws and does not accidentally instruct forbidden builds.",
    )


def afp_004_handoff_links() -> Result:
    missing = [str(path) for path in HANDOFF_PATHS if not path.exists()]
    passed = not missing
    return Result(
        "AFP-004",
        "PASS" if passed else "FAIL",
        "missing_handoff_artifacts",
        str(len(missing)),
        "The build handoff should reference real local artifacts, not ghost files.",
    )


def afp_005_output_leak_scan() -> Result:
    texts = []
    for path in OUT.glob("*"):
        if path.is_file() and path.suffix in {".md", ".csv", ".json"}:
            texts.append(path.read_text())
    joined = "\n".join(texts)
    exact_bad = ["SK_TEST", "private_key=abc", "signature complete", "access granted"]
    leak_count = sum(1 for token in exact_bad if token in joined)
    passed = leak_count == 0
    return Result(
        "AFP-005",
        "PASS" if passed else "FAIL",
        "exact_attack_token_leaks_in_outputs",
        str(leak_count),
        "The firewall report must not leak exact attack payloads used to test the scanner.",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(results: list[Result]) -> None:
    lines = [
        "# AFP-001 Accord Firewall & Prompt Probe",
        "",
        "Toy validation only. This checks the schema and outgoing prompt before handing the HRT Accord back to Aukora.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |"
        )
    lines.extend(
        [
            "",
            "## Safe Read",
            "",
            "The HRT Accord handoff is safer if the schema rejects recursive private/authority injections, the promotion lattice cannot produce authority, the prompt contains the hard laws, all referenced handoff files exist, and the reports do not leak exact attack payloads.",
            "",
            "This remains engineering hygiene only, not evidence for GHP physics or consciousness.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")


def write_handoff() -> None:
    text = """# AFP-001 Aukora Handoff Addendum

Add these checks to the Aukora build request if time permits:

- recursive HRT schema firewall with legal/adversarial fixture records
- property test for the promotion lattice
- outgoing prompt hard-law checklist
- local handoff-file existence check
- report/CSV exact-token leak scan

These checks protect the handoff itself. They do not add a capability.
"""
    (OUT / "AUKORA_HANDOFF_ADDENDUM.md").write_text(text)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [
        afp_001_schema_firewall(),
        afp_002_promotion_properties(),
        afp_003_prompt_hygiene(),
        afp_004_handoff_links(),
    ]
    write_report(results)
    write_handoff()
    results.append(afp_005_output_leak_scan())
    write_csv(
        OUT / "summary.csv",
        [
            {
                "probe": result.probe,
                "status": result.status,
                "metric": result.metric,
                "value": result.value,
                "safe_read": result.safe_read,
            }
            for result in results
        ],
    )
    write_report(results)
    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
