# D28 construction-rule loop — prediction ledger (committed BEFORE any compute)

Base 2381988. Court FROZEN: no file under the court surface may change; a
proposal needing a court change is a tombstone with its diff attached.

## Frozen metric (Task 0)

For a case (L, parity): metric = W_hi(candidate, T=1024, mass-conditioned
tail) / ell, using the D27 floors (L=0.5 odd: ell=0.000180934196848; L=0.4
even: ell=0.000172308870206). Two cases: L=0.5 odd (open 1.1904), L=0.4 even
(open 1.1289).

## Frozen court surface (hashed at start)

- `riemann_dojo/dojo_court.py` (integral/pole/basis machinery) — hash recorded
- `court_frozen.py` (this dir; the score() + tail + norm wrapper) — hash recorded
Loop edits are allowed ONLY in `construct_candidate.py`.

## Predictions

1. **Fast tier equivalence**: the float tier ranks candidates consistently with
   the frozen court (final certified numbers come from the court only).
2. **Baseline optimizer** (penalty grid + constraint projection, no models):
   the unconstrained minimizer sits AT the floor but has a large tail;
   a tuned smoothness penalty should bring its certified ratio under 1.15 for
   L=0.5 odd and under 1.20 for L=0.4 even. Best baseline: I predict
   L=0.5 odd ~1.05-1.15, L=0.4 even ~1.05-1.20.
3. **Loop targets (preregistered)**: best rule brings L=0.4 even under 1.10
   and L=0.5 odd under 1.15; better is a favorable miss.
4. **Controls**: wrong-L mutant fails threading; omitted-tail rejected; a
   metric-gaming proposer ends in a tombstone.
5. Cost: <= $20 OpenRouter (expected <$1 with deepseek-v4.1-flash,
   qwen3.8-27b, glm-5.3-flash; kimi-k3 sparingly); 45 CPU-min for the loop.
