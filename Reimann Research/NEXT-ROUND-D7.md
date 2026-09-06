# Opus D7 — independent certificate audit

Directive saved from the conversation, 2026-09-06. Proposed work, not completed results.

## Goal and rules

Independently verify or refute the L=0.7 compact-window certificate. Read repository instructions, FABLE-ROUND-D6-RESULTS.md and its dependencies, Codex's sine-basis conventions, and the status report linked in README.md. Resolve and record the base commit.

Work in author-owned files only. Commit predictions before computation; preserve failed predictions; use MEASURED / UNVERIFIED / PREDICTED / VOID. No zero ordinates, new physical models, larger windows, or fitted matching constants. Set a compute budget before running. Commit locally; do not push.

## D7.1 Analytic audit

Independently derive W, R_T and W>=R_T, including normalization, prime powers 2/3/4, Hermitian pole signs, complex decomposition and domains. Check hypotheses of the quadrature theorem, discarded-block/coupling bounds, and basis invertibility/norm conversion. Supply proofs or exact authoritative references with hypotheses checked. Numerical spot checks do not prove inequalities. Preregister the most likely failing step without assuming all remaining issues are editorial.

## D7.2 Independent reconstruction

Implement the same R_T at L=0.7,T=120 without copying Fable's matrix-construction or tail-bound code. The same normalized Legendre basis is acceptable for meaningful entrywise comparison. A different basis alone is not implementation independence.

Report rigorous entry enclosures, finite-block lower bounds, infinite coupling/tail bounds and full lower bounds. Target even 1.031e-13 and odd 5.859e-11; a smaller rigorously positive bound is valid. Do not force agreement.

## D7.3 Sensitive directions

Freeze approximate minimizing vectors as exact finite coefficient vectors and independently evaluate their scores with errors sufficiently small to resolve signs. A vector's score supplies an upper bound on the minimum, not a certificate of a lower bound. Individual entries agreeing to 1e-11 do not resolve a 1e-13 margin independently.

## D7.4 Adversarial checker tests first

- Missing tail evidence: no certificate.
- Excessive coupling: rejection when the certified inequality fails.
- Claimed constant above endpoint: rejection.
- Singular basis transformation: rejection.
- Nonorthogonal invertible basis: correct norm conversion.
- Wrong pole sign: detected by independent model validation. A positivity checker need not reject a positive matrix representing the wrong model.

## D7.5 Output and stop

Write OPUS-ROUND-D7-RESULTS.md with dependency audit, reconstruction comparison, sensitive-direction tests, controls, ledger, commands and versions. Link it from this hub when available.

Verdict: independently verified (exact scope/constants); positive with weaker independent bound; specific defect found; or UNVERIFIED with the exact obligation. If the budget prevents completion, report partial results without promotion. End with a plain-language explanation of why a fixed window does not cover all windows.

Do not conflate GHP's central charge c=0.7 with the chosen support half-width L=0.7. No bridge is established.
