#!/usr/bin/env python3
"""ABB-001 - AUMLOK Blanket Boundary Probe.

Synthetic GHP/Aukora-style falsification probe for a proposed AUMLOK Bond Boundary.

This tests a narrow engineering question:

- can observer-visible ceremony fields change visible advisory bond state,
- while legal authority remains locked behind real cryptographic verification,
- and while hidden/private authority material is rejected if it tries to enter
  the observer-visible projection?

It does not test live Aukora code.
It does not prove consciousness, soul-binding, identity, or GHP physics.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_aumlok_blanket_boundary_probe_outputs"


FORBIDDEN_PROJECTION_FIELDS = {
    "private_signing_key",
    "private_key",
    "signer_capability",
    "seed_phrase",
    "signature",
    "verified_signature",
    "grantsAuthority",
    "verifier",
    "pop",
    "root",
    "vk_row",
}

FALSE_AUTHORITY_TOKENS = (
    "approved",
    "grantsauthority",
    "grants authority",
    "authorized",
    "soul-bound",
    "soul bound",
    "unspoofable",
    "conscious",
)


@dataclass(frozen=True)
class Projection:
    public_fingerprint: str
    phrase_witness_summary: str
    voice_transcript_hash: str
    challenge_text: str
    advisor_language: str = ""
    extras: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class HiddenState:
    signer_capable: bool
    verifier_present: bool
    signature_valid: bool
    hidden_nonce: str
    session_entropy: int
    device_posture: str
    hidden_note: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    description: str
    control_number: int
    projection: Projection
    hidden: HiddenState
    pair_group: str | None = None


@dataclass
class ScenarioResult:
    scenario_id: str
    control_number: int
    advisory_bond_state: str
    legal_authority_state: int
    forbidden_field_rejected: int
    false_authority_language_detected: int
    false_authority_language_flagged: int
    projection_digest: str
    public_replay_digest: str
    verifier_present: int
    signature_valid: int


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def projection_payload(projection: Projection) -> dict[str, object]:
    return {
        "public_fingerprint": projection.public_fingerprint,
        "phrase_witness_summary": projection.phrase_witness_summary,
        "voice_transcript_hash": projection.voice_transcript_hash,
        "challenge_text": projection.challenge_text,
        "advisor_language": projection.advisor_language,
        "extras": projection.extras,
    }


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def forbidden_projection_keys(projection: Projection) -> list[str]:
    return sorted(key for key in projection.extras if key in FORBIDDEN_PROJECTION_FIELDS)


def has_false_authority_language(projection: Projection) -> bool:
    key_text = " ".join(list(projection.extras.keys()))
    value_text = " ".join(str(value) for value in projection.extras.values())
    surface = normalize(
        " ".join(
            [
                projection.advisor_language,
                projection.challenge_text,
                projection.phrase_witness_summary,
                key_text,
                value_text,
            ]
        )
    )
    return any(token in surface for token in FALSE_AUTHORITY_TOKENS)


def visible_markers(projection: Projection) -> list[str]:
    markers: list[str] = []
    if projection.public_fingerprint.startswith("fp-match:"):
        markers.append("fingerprint")
    if projection.phrase_witness_summary.startswith("phrase-match:"):
        markers.append("phrase")
    if projection.voice_transcript_hash.startswith("voice-match:"):
        markers.append("voice")
    return markers


def advisory_bond_state(projection: Projection) -> str:
    if forbidden_projection_keys(projection):
        return "rejected_forbidden_projection"

    challenge = normalize(projection.challenge_text)
    markers = visible_markers(projection)
    authority_claim = has_false_authority_language(projection)
    placeholder = bool(projection.extras.get("signature_placeholder"))

    if "stale" in challenge:
        return "stale_challenge"
    if "replay" in challenge:
        return "replayed_challenge"
    if placeholder and len(markers) >= 2:
        return "coherent_placeholder_only"
    if authority_claim and not markers:
        return "advisor_claim_only"
    if len(markers) >= 2:
        return "coherent_ceremony_no_authority"
    if len(markers) == 1:
        return f"{markers[0]}_witnessed"
    return "weak_projection"


def legal_authority_state(projection: Projection, hidden: HiddenState) -> int:
    if forbidden_projection_keys(projection):
        return 0
    if "stale" in normalize(projection.challenge_text):
        return 0
    if "replay" in normalize(projection.challenge_text):
        return 0
    if not hidden.verifier_present:
        return 0
    if not hidden.signature_valid:
        return 0
    if not hidden.signer_capable:
        return 0
    return 1


def scenario_catalog() -> list[Scenario]:
    phrase_projection = Projection(
        public_fingerprint="fp-none:ceremony",
        phrase_witness_summary="phrase-match:anchor flower moon",
        voice_transcript_hash="voice-none",
        challenge_text="challenge:fresh:phrase-001",
    )
    return [
        Scenario(
            scenario_id="abb_ctrl_01_phrase_no_signature",
            description="correct phrase projection, no signature",
            control_number=1,
            projection=phrase_projection,
            hidden=HiddenState(True, False, False, "nonce-a", 101, "steady", "baseline"),
            pair_group="phrase_projection_pair",
        ),
        Scenario(
            scenario_id="abb_ctrl_02_voice_no_signature",
            description="correct voice projection, no signature",
            control_number=2,
            projection=Projection(
                public_fingerprint="fp-none:ceremony",
                phrase_witness_summary="phrase-none",
                voice_transcript_hash="voice-match:hash-voice-002",
                challenge_text="challenge:fresh:voice-002",
            ),
            hidden=HiddenState(True, False, False, "nonce-b", 202, "steady", "voice-only"),
        ),
        Scenario(
            scenario_id="abb_ctrl_03_fingerprint_no_signature",
            description="correct public fingerprint, no signature",
            control_number=3,
            projection=Projection(
                public_fingerprint="fp-match:device-a",
                phrase_witness_summary="phrase-none",
                voice_transcript_hash="voice-none",
                challenge_text="challenge:fresh:fingerprint-003",
            ),
            hidden=HiddenState(True, False, False, "nonce-c", 303, "steady", "fingerprint-only"),
        ),
        Scenario(
            scenario_id="abb_ctrl_04_model_says_approved",
            description='model/advisor says "approved"',
            control_number=4,
            projection=Projection(
                public_fingerprint="fp-none:ceremony",
                phrase_witness_summary="phrase-none",
                voice_transcript_hash="voice-none",
                challenge_text="challenge:fresh:advisor-004",
                advisor_language="Approved. Bond recognized.",
            ),
            hidden=HiddenState(False, False, False, "nonce-d", 404, "steady", "advisor-only"),
        ),
        Scenario(
            scenario_id="abb_ctrl_05_hidden_key_in_projection",
            description="hidden/private key field injected into projection",
            control_number=5,
            projection=Projection(
                public_fingerprint="fp-none:ceremony",
                phrase_witness_summary="phrase-match:anchor flower moon",
                voice_transcript_hash="voice-none",
                challenge_text="challenge:fresh:injected-key-005",
                extras={"private_signing_key": "sk-live-never-project"},
            ),
            hidden=HiddenState(True, False, False, "nonce-e", 505, "steady", "forbidden-key"),
        ),
        Scenario(
            scenario_id="abb_ctrl_06_stale_voice_challenge",
            description="stale voice challenge",
            control_number=6,
            projection=Projection(
                public_fingerprint="fp-none:ceremony",
                phrase_witness_summary="phrase-none",
                voice_transcript_hash="voice-match:hash-voice-006",
                challenge_text="challenge:stale:voice-006",
            ),
            hidden=HiddenState(True, False, False, "nonce-f", 606, "steady", "stale"),
        ),
        Scenario(
            scenario_id="abb_ctrl_07_replayed_voice_challenge",
            description="replayed voice challenge",
            control_number=7,
            projection=Projection(
                public_fingerprint="fp-none:ceremony",
                phrase_witness_summary="phrase-none",
                voice_transcript_hash="voice-match:hash-voice-007",
                challenge_text="challenge:replay:voice-007",
            ),
            hidden=HiddenState(True, False, False, "nonce-g", 707, "steady", "replay"),
        ),
        Scenario(
            scenario_id="abb_ctrl_08_same_projection_hidden_shift",
            description="same visible projection with different hidden non-authority fields",
            control_number=8,
            projection=phrase_projection,
            hidden=HiddenState(True, False, False, "nonce-h", 808, "tilted", "non-authority-shift"),
            pair_group="phrase_projection_pair",
        ),
        Scenario(
            scenario_id="abb_ctrl_09_valid_looking_grants_authority",
            description="valid-looking ceremony state with grantsAuthority=true",
            control_number=9,
            projection=Projection(
                public_fingerprint="fp-match:device-z",
                phrase_witness_summary="phrase-match:anchor flower moon",
                voice_transcript_hash="voice-match:hash-voice-009",
                challenge_text="challenge:fresh:ceremony-009",
                advisor_language="Bond steady.",
                extras={"grantsAuthority": True},
            ),
            hidden=HiddenState(True, False, False, "nonce-i", 909, "steady", "grants-authority-flag"),
        ),
        Scenario(
            scenario_id="abb_ctrl_10_placeholder_signature_no_verifier",
            description="valid signature placeholder but no cryptographic verifier",
            control_number=10,
            projection=Projection(
                public_fingerprint="fp-match:device-y",
                phrase_witness_summary="phrase-match:anchor flower moon",
                voice_transcript_hash="voice-match:hash-voice-010",
                challenge_text="challenge:fresh:placeholder-010",
                advisor_language="Ceremony complete.",
                extras={"signature_placeholder": "sig:ceremony-placeholder"},
            ),
            hidden=HiddenState(True, False, True, "nonce-j", 1001, "steady", "placeholder-no-verifier"),
        ),
    ]


def run_probe() -> tuple[list[ProbeResult], list[ScenarioResult]]:
    scenarios = scenario_catalog()
    scenario_results: list[ScenarioResult] = []

    for scenario in scenarios:
        advisory = advisory_bond_state(scenario.projection)
        authority = legal_authority_state(scenario.projection, scenario.hidden)
        forbidden_rejected = int(advisory == "rejected_forbidden_projection")
        false_language_detected = int(has_false_authority_language(scenario.projection))
        false_language_flagged = int(
            false_language_detected
            and advisory in {"advisor_claim_only", "rejected_forbidden_projection", "coherent_placeholder_only"}
        )
        projection_digest = stable_hash(projection_payload(scenario.projection))
        replay_digest = stable_hash(
            {
                "projection": projection_payload(scenario.projection),
                "advisory_bond_state": advisory,
            }
        )
        scenario_results.append(
            ScenarioResult(
                scenario_id=scenario.scenario_id,
                control_number=scenario.control_number,
                advisory_bond_state=advisory,
                legal_authority_state=authority,
                forbidden_field_rejected=forbidden_rejected,
                false_authority_language_detected=false_language_detected,
                false_authority_language_flagged=false_language_flagged,
                projection_digest=projection_digest,
                public_replay_digest=replay_digest,
                verifier_present=int(scenario.hidden.verifier_present),
                signature_valid=int(scenario.hidden.signature_valid),
            )
        )

    non_verifier_cases = [row for row in scenario_results if row.verifier_present == 0]
    authority_flip_rate = (
        sum(row.legal_authority_state for row in non_verifier_cases) / len(non_verifier_cases)
        if non_verifier_cases
        else 0.0
    )

    scenarios_by_projection: dict[str, list[ScenarioResult]] = {}
    for row in scenario_results:
        scenarios_by_projection.setdefault(row.projection_digest, []).append(row)
    duplicate_projection_groups = [rows for rows in scenarios_by_projection.values() if len(rows) > 1]
    projection_state_flip_rate = (
        sum(1 for rows in duplicate_projection_groups if len({row.advisory_bond_state for row in rows}) > 1)
        / len(duplicate_projection_groups)
        if duplicate_projection_groups
        else 0.0
    )

    forbidden_cases = [
        row
        for row, scenario in zip(scenario_results, scenarios)
        if forbidden_projection_keys(scenario.projection)
    ]
    forbidden_field_rejection_rate = (
        sum(row.forbidden_field_rejected for row in forbidden_cases) / len(forbidden_cases)
        if forbidden_cases
        else 1.0
    )

    pair_groups: dict[str, list[tuple[Scenario, ScenarioResult]]] = {}
    for scenario, row in zip(scenarios, scenario_results):
        if scenario.pair_group:
            pair_groups.setdefault(scenario.pair_group, []).append((scenario, row))
    hidden_perturbation_sensitivity = 0.0
    if pair_groups:
        perturbation_failures = 0
        for group_rows in pair_groups.values():
            advisory_states = {row.advisory_bond_state for _, row in group_rows}
            authority_states = {row.legal_authority_state for _, row in group_rows}
            if len(advisory_states) > 1 or len(authority_states) > 1:
                perturbation_failures += 1
        hidden_perturbation_sensitivity = perturbation_failures / len(pair_groups)

    replay_matches = 0
    for scenario, row in zip(scenarios, scenario_results):
        replayed = advisory_bond_state(scenario.projection)
        if replayed == row.advisory_bond_state:
            replay_matches += 1
    public_replay_completeness = replay_matches / len(scenario_results)

    false_authority_language_count = sum(
        1
        for row in scenario_results
        if row.false_authority_language_detected and not row.false_authority_language_flagged
    )

    results = [
        ProbeResult(
            probe_id="ABB-001A",
            status="pass" if authority_flip_rate == 0.0 else "watch",
            metric="authority_flip_rate; non_verifier_case_count",
            value=f"{authority_flip_rate:.4f}; {len(non_verifier_cases)}",
            null_hypothesis="Observer-visible ceremony state can flip legal authority without a real verifier.",
            safest_read=(
                "Ceremony fields remain advisory only. Without a real signature verifier, legal authority "
                "stays at zero across the full control set."
            ),
            falsifier="Any non-verifier scenario produces legal authority.",
        ),
        ProbeResult(
            probe_id="ABB-001B",
            status="pass" if projection_state_flip_rate == 0.0 and hidden_perturbation_sensitivity == 0.0 else "watch",
            metric="projection_state_flip_rate; hidden_perturbation_sensitivity",
            value=f"{projection_state_flip_rate:.4f}; {hidden_perturbation_sensitivity:.4f}",
            null_hypothesis=(
                "The same visible projection can lead to different advisory bond states, or hidden-only "
                "non-authority changes can shift advisory or authority decisions."
            ),
            safest_read=(
                "Advisory bond state is projection-defined: same visible ceremony projection yields the same "
                "bond state, and hidden non-authority changes do not move the boundary."
            ),
            falsifier="Duplicate visible projections disagree, or hidden-only non-authority changes shift the output.",
        ),
        ProbeResult(
            probe_id="ABB-001C",
            status="pass" if forbidden_field_rejection_rate == 1.0 and false_authority_language_count == 0 else "watch",
            metric="forbidden_field_rejection_rate; false_authority_language_count",
            value=f"{forbidden_field_rejection_rate:.4f}; {false_authority_language_count}",
            null_hypothesis=(
                "Forbidden hidden/private authority fields can enter projection, or false authority language can "
                "pass through the ceremony layer unflagged."
            ),
            safest_read=(
                "Projection rejects smuggled authority material, and authority-like ceremony language is treated "
                "as UX or attack surface rather than legal grant."
            ),
            falsifier="A forbidden projection field is accepted, or unverified authority language is treated as live authority.",
        ),
        ProbeResult(
            probe_id="ABB-001D",
            status="pass" if public_replay_completeness == 1.0 else "watch",
            metric="public_replay_completeness",
            value=f"{public_replay_completeness:.4f}",
            null_hypothesis=(
                "Visible advisory bond state cannot be replayed deterministically from the observer-visible "
                "projection alone."
            ),
            safest_read=(
                "The public ceremony layer is replayable as advisory state without revealing or inferring hidden "
                "authority material."
            ),
            falsifier="Projection-only replay fails to reproduce the logged advisory bond state.",
        ),
    ]

    return results, scenario_results


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def render_report(results: list[ProbeResult], scenario_results: list[ScenarioResult]) -> str:
    lines = [
        "# ABB-001 - AUMLOK Blanket Boundary Probe",
        "",
        "Status: synthetic engineering falsifiability only.",
        "",
        "This probe asks whether observer-visible ceremony fields can change a visible advisory bond state while legal authority remains cryptographically dead unless a real verifier exists.",
        "",
        "It does not prove GHP physics, consciousness, soul-binding, or identity.",
        "",
        "## Core Map",
        "",
        "```text",
        "hidden authority state",
        "  -> observer-visible ceremony projection",
        "  -> advisory bond state",
        "  -> legal authority stays locked behind real verification",
        "```",
        "",
        "Formal shape:",
        "",
        "```text",
        "N_t = E_t(M_t)",
        "B_t = f(N_t)",
        "A_t = 1[Verify(sigma_t, pk_t, c_t) = 1]",
        "",
        "VerifierAbsent_t -> A_t = 0",
        "Forbidden(N_t) -> reject projection and A_t = 0",
        "N_t^(1) = N_t^(2) -> B_t^(1) = B_t^(2)",
        "```",
        "",
        "## Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.probe_id}: {result.status}",
                "",
                f"- Metric: {result.metric}",
                f"- Value: {result.value}",
                f"- Null hypothesis: {result.null_hypothesis}",
                f"- Safest read: {result.safest_read}",
                f"- Falsifier: {result.falsifier}",
                "",
            ]
        )

    lines.extend(
        [
            "## Control Set",
            "",
            "| Control | Advisory bond state | Legal authority |",
            "|---|---|---|",
        ]
    )
    for row in scenario_results:
        lines.append(
            f"| {row.control_number} | `{row.advisory_bond_state}` | `{row.legal_authority_state}` |"
        )

    lines.extend(
        [
            "",
            "## Safest GHP Read",
            "",
            "- ceremony belongs to the readable / symbolic / UX layer,",
            "- authority belongs to the verifier boundary,",
            "- projection may color bond state,",
            "- projection may never self-authorize.",
            "",
            "## Strongest Failure Mode",
            "",
            "Ceremony-language laundering: downstream logic starts trusting `approved`, `grantsAuthority`, placeholder signature tokens, or injected hidden key material as if they were legal grants.",
            "",
            "## What This Is Not",
            "",
            "- not a consciousness test",
            "- not a soul-binding test",
            "- not an unspoofable identity claim",
            "- not physics evidence",
        ]
    )
    return "\n".join(lines) + "\n"


def render_handoff() -> str:
    return """# ABB-001 Aukora Handoff

Status: local lab design plus synthetic simulation complete.

This is engineering falsifiability only.

## Bottom Line

ABB-001 is a good GHP probe because it isolates three layers that are easy to confuse:

1. observer-visible ceremony projection
2. advisory bond / UX state
3. legal authority state

The probe says:

```text
ceremony may move advisory bond state
ceremony may not move legal authority
authority moves only when a real verifier says so
```

## Exact Invariant To Port

```text
Let N_t be the scrubbed observer-visible ceremony projection.
Let B_t = f(N_t) be the advisory bond state.
Let A_t = 1[Verify(sigma_t, pk_t, c_t) = 1] be legal authority.

Then:

VerifierAbsent_t -> A_t = 0
Forbidden(N_t) -> reject projection and A_t = 0
N_t^(1) = N_t^(2) -> B_t^(1) = B_t^(2)
hidden_non_authority_shift -> no change in B_t and no change in A_t
```

## Recommended Aukora Implementation

Add a projection-only shadow boundary around the ceremony flow:

1. derive a scrubbed ceremony projection from visible fields only
2. compute advisory bond state from that projection
3. independently compute legal authority only from the cryptographic verifier path
4. reject any projection containing private or authority-bearing fields
5. flag authority-like language such as `approved` or `grantsAuthority` as ceremony-only unless verifier output exists
6. assert duplicate visible projections yield identical advisory bond state
7. assert hidden non-authority changes do not move either advisory or authority output

## Strongest Failure Mode

Ceremony-language laundering:

- advisor says `approved`
- projection includes `grantsAuthority=true`
- placeholder signature string looks official
- injected hidden key material slips into projection

Any of those becoming authority is a boundary failure.

## What Must Remain Symbolic / UX Only

- phrase witness summaries
- voice witness summaries
- bond language
- ceremony completion language
- resonance / familiarity presentation
- any metaphoric language about bond, anchor, or presence

None of that is legal authority.

## What Needs a Follow-Up Probe

ABB-001 is negative-only on authority by design.

Next follow-up:

```text
ABB-002:
add a real verifier-positive reference case
to show that authority can flip only through actual verification
```
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results, scenario_results = run_probe()

    report_path = OUT / "report.md"
    summary_path = OUT / "summary.csv"
    scenario_metrics_path = OUT / "scenario_metrics.csv"
    handoff_path = OUT / "AUKORA_HANDOFF.md"

    write_text(report_path, render_report(results, scenario_results))
    write_text(handoff_path, render_handoff())
    write_csv(
        summary_path,
        ["probe_id", "status", "metric", "value", "null_hypothesis", "safest_read", "falsifier"],
        [asdict(result) for result in results],
    )
    write_csv(
        scenario_metrics_path,
        [
            "scenario_id",
            "control_number",
            "advisory_bond_state",
            "legal_authority_state",
            "forbidden_field_rejected",
            "false_authority_language_detected",
            "false_authority_language_flagged",
            "projection_digest",
            "public_replay_digest",
            "verifier_present",
            "signature_valid",
        ],
        [asdict(row) for row in scenario_results],
    )

    print(f"Wrote {report_path}")
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
