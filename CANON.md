# GHP Canon — Document Map

**As of 2026-07-19** (supersedes the 2026-07-03 map). This file is the single source of truth for *which document is which*. Read it first.

## The two canonical documents (start here)

| Document | What it is | Read it if… |
|---|---|---|
| **`GHP_CORE_v3.md`** | The canonical **short paper**. Thesis, scoreboard, the closed lanes, the remaining deciding experiments, methodology, falsification conditions. | You want the whole argument in one sitting. |
| **`GHP_BOUNDARY_PROGRAM_v2.md`** | The canonical **working paper** (~70 pp, hardening edition). Full mathematics, every test protocol and verdict, the bridge stack, the toy-model arcs, the engineering lane, open problems — organized *claim → test → verdict → guardrail* — plus an editorial status map, an errata register, and the 2026-07-19 addendum. | You want to check the work, reproduce a result, or build on it. |

Both carry the same three-layer discipline and the same Do-Not-Claim rules. Neither asks you to read the master.

## The living status board

| Document | What it is |
|---|---|
| **`RESEARCH_LEDGER.md`** | The **claim ledger** — every individual claim with its current status (proven / conjecture / toy / null / killed / generic / closed), evidence, and next gate. This is where a result's *current* standing is recorded. New results land here first. |

## The frozen archive (provenance, not for citation)

| Document | Status |
|---|---|
| **`GHP_v1_618_MASTER.md`** | The original 15,635-line research master. **Frozen, append-only archive of record.** Cite it only for provenance ("this was done on this date"), never as the current statement of what a result *means*. |
| **`GHP_CORE_SHARE_PAPER.md`** (core-v0.023) | **Superseded** (by v2, then v3). Retained unedited below its 2026-07-19 banner as the timestamped priority record. Do not cite as current. |
| **`GHP_CORE_v2.md`** | **Superseded** by `GHP_CORE_v3.md`. Retained with a dated deprecation banner. Do not cite as current. |
| **`GHP_BOUNDARY_PROGRAM.md`** (v1) | **Superseded** by `GHP_BOUNDARY_PROGRAM_v2.md`. Retained with a dated deprecation banner. Do not cite as current. |
| **`GHP_RESEARCH_LEDGER.md`** | **Superseded** by `RESEARCH_LEDGER.md`; now a pointer. Its full prior content (111,151 bytes, frozen 2026-07-04) is preserved byte-for-byte at **`archive/GHP_RESEARCH_LEDGER.2026-07-04.md`**. |
| **`docs/ERRATA_2026-07-19.md`** | The dated errata register for the 2026-07-19 hardening pass: every cross-document inconsistency, naming violation, and packaging defect, marked — not silently rewritten. |

## The rule going forward

New results land in **`RESEARCH_LEDGER.md`** first. When they mature, they are written up in **`GHP_BOUNDARY_PROGRAM_v2.md`** (by addendum) and, if load-bearing for the headline argument, reflected in **`GHP_CORE_v3.md`**. The master is never edited again except by strict append; it exists so the trail is never broken.

**Nothing is left behind:** every claim, null, and kill from the master and the old share paper is carried forward into the canonical documents or the ledger — or explicitly marked in the errata register. If you find something in the archive that is *not* reflected in the canon or the errata, that is a bug — flag it.
