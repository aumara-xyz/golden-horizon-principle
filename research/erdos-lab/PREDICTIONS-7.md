# Erdős #7 — odd covering system? VERIFIABLE. Written before compute (2026-09-03, evening).
Setup: a distinct covering system with all moduli odd, lcm L, uses at most one residue class per divisor d>1 of L. Exists iff the SAT instance "choose residue r_d for a subset of divisors d|L, d>1, such that every n mod L is covered" is satisfiable. Necessary (folklore, thread): L odd abundant (σ(L) ≥ 2L), so L ≥ 945; BBMST: not squarefree; Hough–Nielsen/BBMST: 9 | L or 15 | L.
Encoding: variables x_{d,r}; at-most-one r per d; for each n in Z_L a clause OR over (d,r) with r ≡ n mod d. Solver: CaDiCaL via pysat. Per-instance timeout 300 s.
P1: every odd abundant L ≤ 50,000 is UNSAT. PREDICTED (an example would contradict 70 years of failed search plus the squarefree theorem's heuristic).
P2: the solver proves UNSAT in under 10 s for L ≤ 10,000; the first instance to time out has L > 20,000. PREDICTED.
P3: the "gap" 1 − Σ_{d|L,d>1} 1/d-weighted coverage is not the binding constraint: some L with Σ 1/d ≥ 1.2 are still UNSAT. PREDICTED.
Positive control: the same encoding with the modulus 2 allowed (L even) must find the classical coverings, e.g. L=12 {0 mod 2, 0 mod 3, 1 mod 4, 5 mod 6, 7 mod 12}. Must be SAT or the encoder is wrong.
Kill: any SAT on an odd L is verified by exact enumeration before being reported.
What a miss is: a table of certified-UNSAT odd abundant L, MEASURED, possibly overlapping the ResearchGate preprint's certificates (UNVERIFIED overlap).
