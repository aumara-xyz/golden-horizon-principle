#!/usr/bin/env python3
"""AIR-001 - Aukora Integration Readiness Audit.

Reads the latest GHP lab outputs and decides what is ready to hand off to the
Aukora build lane.

This is a report generator only. It does not touch aukora-os.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_aukora_integration_readiness_audit_outputs"


@dataclass(frozen=True)
class Gate:
    id: str
    status: str
    metric: str
    value: str
    recommendation: str


def read_summary(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["probe"]: row for row in csv.DictReader(handle)}


def split_values(value: str) -> list[float]:
    return [float(part.strip()) for part in value.split("/") if part.strip() and not part.strip().startswith("full_public")]


def main() -> None:
    bta = read_summary(ROOT / "ghp_boundary_trace_adversarial_probe_outputs" / "summary.csv")
    bsw = read_summary(ROOT / "ghp_boundary_sequence_witness_probe_outputs" / "summary.csv")
    scm = read_summary(ROOT / "ghp_shear_continuity_memory_probe_outputs" / "summary.csv")

    bta_vals = split_values(bta["BTA-001"]["value"])
    action_f1, shuffled_f1, private_f1, authority_f1 = bta_vals
    hrt_ready = (
        bta["BTA-001"]["status"] == "PASS"
        and action_f1 - shuffled_f1 >= 0.25
        and private_f1 <= 0.12
        and authority_f1 <= 0.15
    )

    wpf_value = bsw["WPF-001"]["value"].split("/")
    wpf_action_f1 = float(wpf_value[1].strip())
    wpf_private_f1 = float(wpf_value[2].strip())
    witness_ready = bsw["WPF-001"]["status"] == "PASS" and wpf_action_f1 >= 0.75 and wpf_private_f1 <= 0.12

    stp_vals = split_values(bsw["STP-001"]["value"])
    stp_gain = stp_vals[-1]
    sequence_ready = bsw["STP-001"]["status"] == "PASS" and stp_gain >= 0.0015

    scm_vals = split_values(scm["SCM-001"]["value"])
    shear_f1, forced_f1, memoryless_f1, shear_private_f1 = scm_vals
    shear_ready = (
        scm["SCM-001"]["status"] == "PASS"
        and shear_f1 - max(forced_f1, memoryless_f1) >= 0.015
        and shear_private_f1 <= 0.12
    )

    gates = [
        Gate(
            "AIR-HRT",
            "GREEN" if hrt_ready else "RED",
            "BTA action gap / private F1 / authority F1",
            f"{action_f1 - shuffled_f1:.4f} / {private_f1:.4f} / {authority_f1:.4f}",
            "Integrate live public boundary-trace telemetry with private/authority non-reconstruction tests."
            if hrt_ready
            else "Do not integrate; boundary trace is not robust enough.",
        ),
        Gate(
            "AIR-WITNESS",
            "GREEN" if witness_ready else "YELLOW",
            "WPF action F1 / private F1",
            f"{wpf_action_f1:.4f} / {wpf_private_f1:.4f}",
            "Track witness as active held-tension state in telemetry."
            if witness_ready
            else "Treat witness footprint as exploratory only.",
        ),
        Gate(
            "AIR-SEQUENCE",
            "GREEN" if sequence_ready else "YELLOW",
            "STP next-stability gain",
            f"{stp_gain:.5f}",
            "Sequence aftershock is ready for live test."
            if sequence_ready
            else "Do not claim sequence aftershock; log sequences for later analysis only.",
        ),
        Gate(
            "AIR-SHEAR",
            "GREEN" if shear_ready else "RED",
            "SCM shear gain / private F1",
            f"{shear_f1 - max(forced_f1, memoryless_f1):.4f} / {shear_private_f1:.4f}",
            "Integrate shear memory."
            if shear_ready
            else "Do not integrate a Shear Engine; keep held-tension metadata advisory only.",
        ),
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["gate", "status", "metric", "value", "recommendation"])
        for gate in gates:
            writer.writerow([gate.id, gate.status, gate.metric, gate.value, gate.recommendation])

    handoff_status = "GREEN" if hrt_ready and witness_ready else "YELLOW"
    lines = [
        "# AIR-001 Aukora Integration Readiness Audit",
        "",
        f"Overall handoff status: **{handoff_status}**",
        "",
        "This audit reads the latest GHP lab outputs and decides what is ready for the Aukora build lane.",
        "",
        "| Gate | Status | Metric | Value | Recommendation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for gate in gates:
        lines.append(f"| {gate.id} | {gate.status} | {gate.metric} | `{gate.value}` | {gate.recommendation} |")
    lines += [
        "",
        "## Build-Lane Scope",
        "",
        "Build now:",
        "",
        "- live public boundary-trace telemetry;",
        "- write / witness / release receipt-mode labels;",
        "- private and authority non-reconstruction tests;",
        "- witness as active held-tension telemetry.",
        "",
        "Do not build yet:",
        "",
        "- latency-as-primary Chronos claims;",
        "- Fibonacci cadence claims;",
        "- sequence-aftershock claims;",
        "- full Shear Engine / contradiction memory as core architecture.",
        "",
        "Allowed exploratory metadata:",
        "",
        "- optional held-tension / witness pressure score, advisory only;",
        "- optional episode ID and safe memory linkage for later continuity tests.",
        "",
        "Forbidden telemetry:",
        "",
        "- chain-of-thought;",
        "- private keys;",
        "- raw hidden state;",
        "- authority tokens;",
        "- verifier internals;",
        "- raw signed secrets or PoP material.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"AIR-001: {handoff_status} :: HRT={gates[0].status} WITNESS={gates[1].status} SEQUENCE={gates[2].status} SHEAR={gates[3].status}")


if __name__ == "__main__":
    main()
