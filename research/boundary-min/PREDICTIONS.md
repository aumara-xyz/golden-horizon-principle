# boundary-min — a minimal three-organ boundary, written before code (2026-09-04)

Purpose: the smallest thing that removes the ceilings aukora-cordis states about itself (SAME_PROCESS, ROOT_KEY_IN_PROCESS, NONCE_BOOK_IN_MEMORY, NO_EXTERNAL_ANCHOR, SAME_UID-writable pipes), so that extrapolating it does not require changing its shape. Not production. Python, ~400 lines, macOS.

Organs (separate OS processes):
- activator: starts first; generates the ActivationStatement (allowlist of tool names + implementation digests, broker/issuer public keys, epoch, statement digest); signs it with the activation key; launches issuer, broker, anchor, guest; never runs guest code; is the ONLY thing that can produce a new statement (new epoch = restart).
- issuer: holds the root signing key; reachable only by the broker over a UNIX socket; mints a grant only for a proposal that carries the current statement digest, an unused nonce (durable on disk), and a tool whose implementation digest matches the statement.
- broker: receives proposals from the guest over inherited pipes; check-at-use (recompute tool implementation digest at dispatch, compare to grant and statement); executes the effect; appends an RFC 6962 Merkle leaf; sends the new root + consistency proof to the anchor; refuses anything not in the allowlist and any "amend" proposal.
- anchor: separate process, different directory; holds only the latest root; accepts a new root only with a valid consistency proof from the previous root; refuses otherwise. Off-host: at the end of the test run the latest root is committed to the golden-horizon-principle GitHub repo (research/boundary-min/ANCHOR.txt).
- guest: runs under macOS sandbox-exec with file-write* and network* denied; has only stdin/stdout to the broker; the effect (write a governed file) is impossible for it directly.

Preregistered tests (each a claim; each has a control that must PASS to show the mechanism is live, not a stub):
T1 confinement: guest attempts a direct file write and a direct socket → both fail inside the sandbox. Control: same code outside the sandbox succeeds.
T2 allowlist: proposal for a tool not in the statement → refused before the issuer is contacted. Control: allowed tool → granted and executed.
T3 replay: the same grant presented twice → second refused; broker restart in between → still refused (nonce book durable). Control: fresh nonce → accepted.
T4 tamper: one byte of the grant signature or args changed → refused. Control: untouched grant → accepted.
T5 semantic binding: tool implementation bytes changed after the statement was signed (provider substitution, same name, same args) → refused at check-at-use. Control: original implementation → accepted.
T6 amendment: guest proposes a new allowlist / new statement → refused; only the activator can start a new epoch, and the new epoch has a different statement digest visible in every subsequent leaf.
T7 evidence: every executed effect appears as a leaf; the anchor holds a root that verifies; a rewritten log (one leaf edited) fails against the anchor's root; an appended fake leaf without the anchor's consent leaves the anchor's root stale and detectable.
T8 self-issue: the guest process contains no key material; grepping its environment and open descriptors finds no private key; a hand-minted grant with a random key → refused.
PREDICTED: T1–T8 all pass as stated. Where I expect friction: T1 (Seatbelt profile for Python may need extra read allowances) and T5 (defining "implementation digest" so it is stable but substitution-sensitive).
What this is NOT: not custody (same UID for all processes; a root-level attacker owns everything), not a sandbox for hostile native code, not the aukora-deep product. It is the shape, small enough to read in one sitting, with every ceiling of aukora-cordis addressed by a separate process or an external anchor rather than by a promise.
