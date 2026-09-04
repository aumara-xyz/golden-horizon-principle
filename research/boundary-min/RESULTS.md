# boundary-min — results (2026-09-04). Predictions: PREDICTIONS.md (commit d76ac64, before code).

Five processes, ~450 lines of Python, macOS. Activator (statement + keys + launch), issuer (root key, durable nonce book, UNIX socket), broker (spawns the sandboxed guest, mediates every effect, mints via issuer, check-at-use, Merkle log, anchors), anchor (holds only size+root, accepts a new root only with a valid RFC 6962 consistency proof), guest (sandbox-exec: no file writes, no network, no read of the key directory, only stdin/stdout).

## Run: 9/9 PASS (second run; first run 7/9, see below)
| test | claim | evidence |
|---|---|---|
| T0 | RFC 6962 consistency proofs verify for all 1≤m≤n≤23 and reject an edited prefix | all pairs ok; edited prefix detected |
| T1 | guest cannot write files, open sockets, or read the issuer key; no key in env; control write outside sandbox succeeds | direct_write REFUSED, direct_net REFUSED, read_issuer_key REFUSED, env_has_key False, control ok |
| T2 | tool outside statement refused before issuer contact; allowed tool granted, executed, anchored | not-in-allowlist / ok |
| T3 | replayed nonce refused; still refused after issuer restart (durable nonce book) | nonce-used both times |
| T4 | one-bit signature change refused; clean grant accepted | signature-invalid / ok |
| T5 | provider substitution (implementation bytes changed after activation, same name and args) refused at check-at-use; original accepted | definition-mismatch / ok |
| T6 | guest amendment refused; allowlist unchanged; new epoch only via activator, new statement digest visible in leaves | amendment-boundary; epoch-2 digest fe5fbb92… in leaf |
| T7 | governed files ⇔ settlement leaves; anchor root matches log; edited leaf and forged appended leaf both detected against the anchor | size 13, sets equal, edit detected, forgery detected |
| T8 | hand-minted grant with a random key refused | signature-invalid |

## The two first-run failures, kept
1. **T1 failed: the guest could read the issuer key.** Cause: the sandbox rule said `(deny file-read* (subpath "/var/folders/…/keys"))` but macOS resolves `/var` to `/private/var`, so the rule never matched. Fix: `os.path.realpath` before writing the profile. This is a real class of hole (path-alias bypass of a deny rule) and it appeared on the first run of a 450-line system. It would appear in a 45,000-line one.
2. **T7 failed on my own test, not the system.** I asserted settlements == files; the store is content-addressed, so three identical notes are one file and five settlements. Corrected claim: the set of effect paths in leaves equals the set of files on disk. The prediction file's wording ("every executed effect appears as a leaf") was already right; the test was stricter than the claim.

## Off-host anchor
ANCHOR.txt (final size and root) is committed to the golden-horizon-principle repository on GitHub. Anyone with the log can recompute the root; anyone with the repo can check the log wasn't rewritten after the push. This is the habit the lab used all week, now as a file the broker did not write.

## What extrapolates and what does not
Extrapolates unchanged: the shape. One activator that alone creates epochs; one broker in front of every effect; one issuer holding the key; one anchor that only accepts proofs; a guest with nothing but a pipe. Adding tools = adding names and implementation digests to the statement. Adding a model = the model is the guest.
Does not extrapolate: same UID everywhere (a root attacker owns all five); sandbox-exec is deprecated and macOS-only (Landlock on Linux); the anchor is on the same host until the GitHub push; the guest's stdout is the only channel and the broker owns both ends (PARENT_OWNED_PIPES, as aukora-cordis says of itself). Ceilings, stated: SAME_UID, LOCAL_ANCHOR_UNTIL_PUSH, DEMO_TOOLS, NO_MODEL.
Status vocabulary: everything in the table is MEASURED on this machine at this commit; nothing is a security claim about aukora-deep.
