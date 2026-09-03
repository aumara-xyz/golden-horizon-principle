# Erdős #7 — results (Fable, 2026-09-03 night). Predictions: PREDICTIONS-7.md (commit 2209d49, before compute). Code: sat_7.py (exact), count_7.py (exact MaxSAT), score_7.py (heuristic).

## What happened, in order
1. Exact SAT (CaDiCaL), all-or-nothing, L=945 (2,000 variables): no answer in > 5 min. P2 ("under 10 s for L ≤ 10,000") VOID.
2. Exact MaxSAT (RC2), minimum bare houses, L=945: no answer in 2 h 36 min. Killed.
3. Heuristic (greedy by increasing step + simulated annealing, 20,000 moves, 4 restarts): best-found bare count per loop in seconds. These are UPPER bounds on the true minimum u(L).
Positive controls: even brushes allowed, L=6 → 1 bare (matches hand computation), L=12 → 0 bare (a covering found and verified). Both held.

## Scoreboard (odd abundant L < 8000 with 9|L or 15|L, one start per odd divisor d>1)
| L | best bare found | random-start baseline | best/baseline | bare fraction | spare strokes |
|---|---|---|---|---|---|
| 945 | 191 | 299.2 | 0.64 | 20 % | 30 |
| 1575 | 314 | 491.0 | 0.64 | 20 % | 74 |
| 2205 | 480 | 709.3 | 0.68 | 22 % | 36 |
| 2835 | 539 | 882.5 | 0.61 | 19 % | 138 |
| 3465 | 597 | 959.7 | 0.62 | 17 % | 558 |
| 4095 | 746 | 1167.8 | 0.64 | 18 % | 546 |
| 4725 | 791 | 1396.7 | 0.57 | 17 % | 470 |
| 5355 | 1041 | 1585.4 | 0.66 | 19 % | 522 |
| 5775 | 1290 | 1778.2 | 0.73 | 22 % | 354 |
| 5985 | 1189 | 1794.6 | 0.66 | 20 % | 510 |
| 6435 | 1425 | 2038.3 | 0.70 | 22 % | 234 |
| 6615 | 1227 | 2019.3 | 0.61 | 19 % | 450 |
| 6825 | 1600 | 2161.1 | 0.74 | 23 % | 238 |
| 7245 | 1485 | 2213.3 | 0.67 | 20 % | 486 |
| 7425 | 1543 | 2433.9 | 0.63 | 21 % | 30 |
| 7875 | 1514 | 2422.8 | 0.62 | 19 % | 474 |

Random-start baseline = L·Π_{d|L, d>1}(1 − 1/d), the expected bare count with no skill.

## Reading
MEASURED: clever placement beats random starts by a nearly constant factor (0.57–0.72) at every L; the bare fraction sits at 17–22 % of the loop and does not trend to zero as L grows over this range. Mechanism (elementary): two brushes with coprime steps overlap on exactly L/(d₁d₂) houses regardless of starts (CRT), so most overlap is forced before any choice is made; only brushes sharing a factor can be arranged. That is the same fact the BBMST squarefree theorem is built on.
UNVERIFIED: the true minima u(L) (the heuristic is weak; exact solvers did not finish). The 2026 ResearchGate preprint in the thread claims closed-form certificates for u(M); overlap not checked.
VOID: P2 (solver speed). P1 (no covering ≤ 50,000) not tested as stated — the exact scan never ran; the heuristic found none, which is weaker.
Lab decision: the exact problem is out of reach for generic SAT/MaxSAT at these sizes; the scorer is useful as a fitness function for a proposer loop (FunSearch-style), which is the only computational continuation worth building.
