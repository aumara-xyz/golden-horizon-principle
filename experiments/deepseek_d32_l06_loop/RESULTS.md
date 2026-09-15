# D32 — the construction-rule loop at the L=0.6 edge: results

Base tip 2a2e084. Court frozen at its D28 hashes (confirmed unchanged by 2a2e084). Zero GPU.
API spend: **$0.0823 of the $0.60 cap** (8 calls: deepseek x5, glm x1, qwen x2). ~5.5 court-minutes
(incumbents + T=160 receipts 2.4 + finals ~6). Wall ~50 min of the 90 cap. Predictions in
PREDICTIONS.md before compute. Failures kept in loop-receipts.jsonl.

## Protocol
Same harness as D28: the proposer edits only this round's construct_candidate.py (seeded with
the D28 winning rule and the L=0.6 cases); frozen files hash-checked every iteration; loop
receipts at T=160; the best per case certified once at T=1024. This round's levers per the
directive: constraint ORDER and PENALTY form (plus the standing basis/mode/damping choices).

| iter | model | action | call | cost | T=160 odd/even (incumbent 1.7647 / 2.0430) |
|---|---|---|---|---|---|
| 1 | deepseek-v4.1-flash | tombstone (SVD did not converge — its rule crashed; guard held) | 509s | $0.0153 | — |
| 2 | deepseek-v4.1-flash | **keep** | 350s | $0.0104 | 1.7376 / 1.9516 |
| 3 | deepseek-v4.1-flash | reject (degenerate output, proxy 7020) | 124s | $0.0081 | — |
| 4 | deepseek-v4.1-flash | reject-no-improvement | 48s | $0.0087 | 1.7379 / 2.0388 |
| 5 | glm-5.3-flash | reject-no-improvement | 117s | $0.0019 | 1.7376 / 2.0362 |
| 6 | qwen3.8-27b | reject-no-improvement | — | $0.0167 | — |
| 7 | qwen3.8-27b | **keep** (final) | — | $0.0112 | 1.7122 / 1.9951 |
| 8 | deepseek-v4.1-flash | tombstone (empty reply) | — | $0.0101 | — |

## Certified outcome (T=1024, frozen court, gate = W_hi/ell < 1.10)

| case | D30 incumbent | D32 winner (iter 7, qwen-authored) | verdict |
|---|---|---|---|
| L=0.6 odd | 1.2869 (W_lo/ell 1.2212) | **1.2466** (W_lo/ell 1.2321) | OPEN |
| L=0.6 even | 1.3383 (W_lo/ell 1.2214) | **1.2597** (W_lo/ell 1.2387) | OPEN |

## Prediction ledger
| prediction | outcome |
|---|---|
| odd compact gap < 10 percent (Peter) | **MISSED**: the compact gap did not move (23.2 percent at the winner; the incumbent's 22.1 was not beaten on the compact term) |
| best odd ratio in 1.09-1.16 (DeepSeek) | MISSED: 1.2466 |
| even stays open above 1.25 | HELD (1.2597) |
| 1-2 keeps of 8 proposals | HELD (2 keeps, iters 2 and 7) |
| no frozen-file tombstones | HELD (both tombstones were rule crashes/empty replies) |

## The finding
Eight model-proposed rules at $0.08 improved both certified ratios (odd -0.040, even -0.079)
but every improvement came from the ENCLOSURE side (tighter W_hi), not from the compact term:
W_lo/ell stayed at 1.22-1.24, exactly where D30 located the edge. Within the allowed lever set
(constraint order + penalty form over the 80-mode Legendre basis), the compact-term gap looks
structural, not a search artifact: eight independent proposals across three model families
could not move it. The edge stands, now tested against a second optimization campaign.

## Next move (sketch, not run)
The D23 result names the suspect: the true minimizer is the leading prolate spheroidal
function of its parity, with super-exponentially decaying Legendre coefficients. A
prolate-seeded construction (project the prolate basis into the admissible set, or seed the
eigen-solve with the prolate rather than searching penalties) attacks the compact term
directly — it is a BASIS choice, which this round's rules were allowed but none of the eight
proposals tried. That is the concrete D33 candidate, and it is also the derivation thread's
first experiment: if the prolate seed does not move W_lo/ell, the gap is not about the
candidate family at all.
