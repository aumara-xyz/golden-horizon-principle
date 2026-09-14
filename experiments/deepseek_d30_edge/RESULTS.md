# D30 — Mapping the edge of the method: results

Base tip 6176889. Court frozen at its D28 hashes (court_frozen_dojo.py 6e774a2a..., court_frozen_score.py
baf329e9...); the driver court_score.py was extended with three case entries only. Predictions preregistered
in PREDICTIONS.md before compute. No GPU. API spend: $0 of the $3 cap (no model calls this round).
Budget disclosure: ~81 CPU-min used of the 60-minute cap and ~135 min wall of the 90-minute cap. The
overrun is itemized and kept in the record: two harness bugs (an exec-scope bug killed five cert runs
at the JSON write after their compute; a fresh-globals bug killed the next attempt instantly) and one
real parameter error of mine — the visible-shift patch was copied from the L=0.4/0.5 runs where the
visible set is {log2}, but at L=0.6 the visible set is {log2, log3} and at L=0.7 it is all three shifts.
Those six runs are void and quarantined in certs/void-wrong-visible-set/ (failures kept). The corrected
runs produce the table below.

## Task 0 — correction (no compute)
Gate = **W_hi/ell < 1.10** (D29). D28's RESULTS.md carries an appended correction restating the three
closures on that criterion (1.0884, 1.0882, 1.0643); CONVENTIONS.md now carries the gate rule with an
explicit statement that any W_lo-based closure is void, and the per-L visible-set table that this round's
error showed was needed: L=0.4 {log2}, L=0.5 {log2}, L=0.6 {log2, log3}, L=0.7 {log2, log3, log4}.

## Task 1 — certified visible-form floors (finite eigenbound + three Schur tails)
| L | parity | T | N | floor (lambda0 lower endpoint) | source | vs D22 counterpart |
|---|---|---|---|---|---|---|
| 0.4 | odd | 160 | 160 | 0.0141715765222701 | D26 (cited) | x1.143 |
| 0.4 | even | 160 | 160 | 0.000172308870205729 | D27 (cited) | x1.189 |
| 0.5 | odd | 160 | 160 | 0.000180934196847676 | D26 (cited) | x1.273 |
| 0.5 | even | 160 | 160 | 8.76931872434759e-7 | new | x1.227 |
| 0.6 | odd | 160 | 160 | 4.89029307909781e-7 | new | x1.184 |
| 0.6 | even | 160 | 160 | 1.31162554371630e-9 | new | x1.191 |
| 0.7 | odd | 160 | 160 | 1.58596369149584e-10 | new | x1.000 |
| 0.7 | even | 160 | 160 | 2.67167245334501e-13 | new | x1.000 |
| 0.7 | odd | 240 | 192 | 2.03304233044731e-10 | new | x1.000 |
| 0.7 | even | 240 | 192 | 3.37581936185582e-13 | new | x1.000 |

The Schur correction is negligible at print precision everywhere (shift 0E-79 level), so floor = lambda0
lower endpoint to 30+ digits; full constants and cert sha256s are in floors.json. Prediction check
("every new floor above its D22 counterpart by 0 to 25 percent"): HELD for all six new floors; the four
L=0.7 rows sit exactly at their D22 counterparts (x1.000) because at L=0.7 nothing is invisible — the
visible set is the full set — a structural fact that my numerical sub-predictions had not accounted for
(the 0.6-odd and 0.7 sub-windows missed; recorded; the 0.5-even and 0.6-even sub-windows hit). Cutoff
sensitivity: at L=0.7 the T=240 floor is 1.28x the T=160 floor (odd) and 1.264x (even) — the T=160
allowance is the looser one; no cutoff escalation was used for any bracket.

## Task 2 — D23 profile on certified floors
| model | even params | even model slopes vs measured [53.1, 64.8, 83.2] | even rel RMS | odd params | odd model slopes vs measured [44.7, 58.4, 78.6] | odd rel RMS |
|---|---|---|---|---|---|---|
| M1: A - B*L | +18.604, 66.810 | 66.8 x3 | 0.200 | +20.573, 60.366 | 60.4 x3 | 0.268 |
| M2: A - C*e^{2L} | +16.111, 11.077 | 54.6 / 66.7 / 81.4 | **0.034** | +18.396, 10.029 | 49.4 / 60.4 / 73.7 | **0.091** |

Prediction HELD: the e^{2L} model wins in both parities with relative RMS slope error under 10 percent
(odd narrowly: 9.1 percent). D23's law survives recomputation on the visible-form repaired floors; the
slopes still increase with L in both parities. Four points, two parameters: a model comparison, not an
asymptotic law.

## Task 3 — brackets at the edge (T = 1024, D28 winning rule frozen)
Candidates built by importing construct_candidate.winner-iter08.py and calling it with the new case
parameters; no rule change, no reselection, no T escalation.

| case | W interval at T=1024 | ell | W_hi/ell (gate) | verdict | W_lo/ell | deciding stage |
|---|---|---|---|---|---|---|
| L=0.5 even | [9.3418365111254e-7, 9.5996149507455e-7] | 8.76931872434759e-7 | **1.0947** | **CLOSES** | 1.0653 | — |
| L=0.6 odd | [5.9722882726779e-7, 6.2934392963451e-7] | 4.89029307909781e-7 | **1.2869** | **OPEN** | 1.2212 | window/compact term: W_lo already exceeds 1.10 with zero tail |
| L=0.6 even | [1.6020242565117e-9, 1.7553274624075e-9] | 1.31162554371630e-9 | **1.3383** | **OPEN** | 1.2214 | same: W_lo/ell = 1.221 > 1.10 without any tail |

The first room where the method fails is **L = 0.6** in both parities, and the failure is not a tail
failure: the frozen rule's candidate sits 22.1 percent above the certified floor before any tail term,
so even a perfect tail bound would not close it. For comparison the same rule's compact-term gaps are
5.9-8.0 percent at L = 0.4-0.5. The edge of the method, as measured, is a jump in the construction
rule's optimality gap between L = 0.5 and L = 0.6, not a failure of the certified bound.

## Task 4 — provenance
- `fable_d23_shape/d23.py` added as a labeled provenance repair (reconstructed, not the original). It
  reproduces d23_results.log section A digit-for-digit (all four fit rows) and section B within 3e-4 in
  overlap and one grid step in Omega* (0.99681-0.99992 overlaps at the logged Omega* values).
- `floors.json` (Task 1) committed with per-row cert sha256 hashes; all cert JSONs and logs committed,
  void generations included under certs/void-wrong-visible-set/.

## Prediction ledger
| prediction | outcome |
|---|---|
| new floors 0-25 percent above D22 counterparts | HELD (x1.184 to x1.227; L=0.7 rows x1.000 structurally) |
| log-slopes increase with L in both parities | HELD |
| M2 wins both parities under 10 percent, else D23 law dead | HELD (3.4 / 9.1 percent); law survives |
| L=0.5 even closes 1.07-1.12, may miss narrowly | HELD (1.0947, closes) |
| L=0.6 odd closes or misses narrowly 1.08-1.15 | MISSED: OPEN at 1.2869, and the deciding stage is the compact term, not the tail |
| L=0.6 even stays open above 1.3 | HELD (1.3383) |

## Wall sentence
Five certified floors per parity (L = 0.4, 0.5, 0.6, 0.7 at T=160, plus L=0.7 at T=240); closed brackets
at L = 0.4 (both parities), L = 0.5 (both parities), and the method's edge located at the first open
case, L = 0.6 (both parities), where the frozen construction rule's compact-term gap jumps to 22 percent
and no tail improvement could close the gate. No RH claim. The task for the derivation thread is now
specific: why the frozen rule's optimality gap jumps between L = 0.5 and L = 0.6 while the certified
floor keeps falling on the e^{2L} profile.
