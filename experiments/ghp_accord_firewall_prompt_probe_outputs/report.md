# AFP-001 Accord Firewall & Prompt Probe

Toy validation only. This checks the schema and outgoing prompt before handing the HRT Accord back to Aukora.

| Probe | Status | Metric | Value | Safe Read |
| --- | --- | --- | --- | --- |
| AFP-001 | PASS | legal_accept_rate / adversarial_reject_rate / false_accepts | `1.0000 / 1.0000 / 0` | The HRT schema can promote only if allowed typed records pass and recursive authority/private injections fail closed. |
| AFP-002 | PASS | unsafe_violations / authority_leaks / monotonic_violations | `0 / 0 / 0` | The promotion lattice must never create authority, promote private/authority reconstruction, or reward weaker evidence. |
| AFP-003 | PASS | missing_required_laws / bad_command_patterns | `0 / 0` | The outgoing prompt is usable only if it carries the hard laws and does not accidentally instruct forbidden builds. |
| AFP-004 | PASS | missing_handoff_artifacts | `0` | The build handoff should reference real local artifacts, not ghost files. |
| AFP-005 | PASS | exact_attack_token_leaks_in_outputs | `0` | The firewall report must not leak exact attack payloads used to test the scanner. |

## Safe Read

The HRT Accord handoff is safer if the schema rejects recursive private/authority injections, the promotion lattice cannot produce authority, the prompt contains the hard laws, all referenced handoff files exist, and the reports do not leak exact attack payloads.

This remains engineering hygiene only, not evidence for GHP physics or consciousness.
