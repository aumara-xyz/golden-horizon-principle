# D32 — the construction-rule loop at the L=0.6 edge: predictions (before compute)

Base tip 2a2e084. Court frozen at its D28 hashes (6e774a2a..., baf329e9...; unchanged per
Fable's 2a2e084 confirmation). Zero GPU; API spend expected under $0.60; loop receipts at
T=160 (the D28 loop instrument), final certification at T=1024. Work in this directory.

## The question
D30 located the method's edge at L=0.6: the D28 winning rule's candidate sits 22.1 percent
above the certified floor on the COMPACT term alone (W_lo/ell = 1.221 both parities), so no
tail improvement could close the gate. Peter's round: rerun the construction-rule optimizer
at L=0.6 with the court frozen, allowing the rule's constraint ORDER and PENALTY to move.

## Incumbents (to beat)
| case | ell (certified floor, D30) | D30 candidate proxy | certified T=1024 ratio (W_hi/ell) |
|---|---|---|---|
| L=0.6 odd | 4.89029307909781e-7 | 1.337134 | 1.2869 |
| L=0.6 even | 1.31162554371630e-9 | 1.399742 | 1.3383 |

## Predictions (preregistered)
1. Peter's: the 22 percent compact-term gap comes down to under 10 percent for the odd
   sector; the even sector stays open.
2. Mine, on top: (a) the best odd candidate lands in 1.09-1.16 (gap 9-16 percent — I expect
   the gap to improve but not necessarily under the gate; anything at or under 1.10 closes
   the room); (b) the best even ratio stays above 1.25 (open); (c) the loop keeps 1-2 of 8
   proposals (the D28 loop kept 2 of 8); (d) no proposal tombstones for touching frozen
   files (the guard holds).
3. Failure modes kept: any proposal that moves the scoring, tail, floor, L or T is
   tombstoned with its diff and never applied.

## Budget
8 iterations; ~12 court-minutes (T=160 receipts ~11 s each, incumbents + finals at T=1024
about 7 min); API under $0.60; wall 90 min hard stop.
