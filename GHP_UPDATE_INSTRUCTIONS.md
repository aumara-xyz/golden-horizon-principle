# GHP Update Instructions

**Use this file first.** Give it to Codex, Opus, Claude, GPT, Gemini, or any other AI before asking for a GHP update.

## Live Files

- `GHP_v1_618_MASTER.md` — live archival working master / full organism.
- `GHP_v0_714.md` — preserved historical snapshot / lineage anchor.
- `GHP_CORE_SHARE_PAPER.md` — concise shareable core paper.
- `GHP_RESEARCH_LEDGER.md` — canonical claim/status/update ledger.
- `GHP_WORKING_MASTER_CONTROL.md` — detailed operating protocol.
- `GHP_OPUS_4_7_REVIEW_PROMPT.md` — prompt for Opus review.

## Golden Rule

The ledger updates first. The master updates second. The core paper updates last, and only if the material is strong enough.

## Local + GitHub Sync Rule

When GHP is updated locally on this computer, Codex must also check whether the public GitHub package needs to be updated.

Local authoritative files remain in:

- `GOLDEN HORIZON PRINCIPLE 🔱/`

Public GitHub package lives in:

- local folder: `../golden-horizon-principle/`
- public repo: `https://github.com/aumara-xyz/golden-horizon-principle`

### Canonical Path Lock

The local authoritative folder is always `GOLDEN HORIZON PRINCIPLE 🔱/`.

Do not treat `../golden-horizon-principle/` as the source of truth. That folder is only a public GitHub package / publish target. Every update must begin in `GOLDEN HORIZON PRINCIPLE 🔱/`, then be distilled or synced outward if public release is appropriate.

Before editing any GHP file, Codex must verify the working directory path and state which folder is being edited. If the path is not `GOLDEN HORIZON PRINCIPLE 🔱/` or an explicitly intended public package sync, stop and correct the path before making changes.

Incident note: on 2026-06-23, BTA-003 through BTA-007 work was accidentally performed first in the public package folder. The recovery rule is: merge important public-package work back into the canonical folder, preserve both backups, then publish from canonical outward.

Default behavior:

1. Update the local canonical files first: ledger, master, core paper, instructions, and any relevant local experiment/report files.
2. If the material is public-facing, update the distilled public GitHub package too.
3. Commit and push the public package after the public files are updated.
4. If GitHub auth or network access blocks the push, leave the public package committed locally if possible and report the exact blocker plus the next command needed.

Privacy rule:

- Do **not** publish `GHP_v1_618_MASTER.md`, raw AI chats, messy addenda, Holographic Resonator code, business/funding/product strategy, private credentials, or private working files unless Peter explicitly requests that exact file be public.
- Public GitHub updates should be distilled, status-labeled, and guardrail-preserving.

Instruction self-update rule:

- If the workflow changes, update this instruction file first.
- If this instruction file changes in a way that affects public release behavior, check whether the public repo README, ledger, or guardrail files need a matching public note.

## Ternary / Operator Addendum Rule

For write / witness / release, Ricci-pressure, Markov-blanket, trefoil-cycle, Tao, Auracle-memory-policy, or other operator-language updates, default status is `symbolic` or `open` unless a theorem or audited computation exists. These updates may enter the master as addenda and the ledger as quarantined claims, but they do not enter the core paper by default.

Never promote operator language into proof, physics evidence, §5.1B closure, consciousness derivation, VPH validation, quantum-measurement mind claims, or software-as-physics support.

## Status Labels

Use only the ledger status vocabulary:

- `theorem`
- `verified-computation`
- `candidate`
- `toy-telemetry`
- `symbolic`
- `external-machinery`
- `open`
- `rejected`

Do not use vague labels like "evidence" when a narrower label applies.

## Update Steps

1. Create a packet ID: `GHP-PACKET-YYYYMMDD-XX`.
2. Update `GHP_RESEARCH_LEDGER.md` with claim IDs, status, evidence type, destination, failure condition, and forbidden upgrade sentence.
3. Update `GHP_v1_618_MASTER.md` only if the packet belongs in the archival master.
4. Update `GHP_CORE_SHARE_PAPER.md` only if the claim passes the strength filter.
5. Update `GHP_UPDATE_INSTRUCTIONS.md` when the workflow itself changes.
6. Check whether the public GitHub package needs matching distilled updates.
7. If public-facing files changed, commit and push `../golden-horizon-principle/`.
8. If a claim weakens, use a demotion or retraction packet.
9. If more than three packets happen in one day, make a daily rollup before continuing.
10. For a shareable release, core and ledger versions must match.

## Core Paper Strength Filter

Material enters the core paper only if it is:

- theorem-grade math,
- verified internal computation,
- a concrete falsifier,
- a defined physical bridge,
- required to understand the central thesis,
- or a necessary guardrail against overclaim.

Everything else stays in the master and ledger.

## Never Claim

- GHP is proven.
- GHP is a completed theory of everything.
- Mathematical minimality proves physical selection.
- VPH proves GHP.
- Ricci proves GHP.
- Toy telemetry is physics evidence.
- Software success is physics evidence.
- Tao, I Ching, Kabbalah, mythology, or lived practice are scientific proof.
- External theory resemblance is validation.

## Codex / Opus Division

Codex patches files, keeps IDs synchronized, and verifies cross-references.

Opus reviews coherence, overclaim, missing demotion conditions, and whether the core paper is readable to a serious outsider.

Opus reviews. Codex patches.

## Snapshot Rule

Keep the live filenames stable. Create versioned snapshots only at meaningful checkpoints:

- after Opus review,
- after a major claim change,
- after a demotion or retraction,
- after a big pruning pass,
- or after a heavy update day.

Store snapshots inside `GHP_VERSIONING/` using dated folders so the live master can stay stable while historical checkpoints remain recoverable.
