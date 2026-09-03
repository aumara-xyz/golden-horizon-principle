# Erdős #699 — assessment after reading both proof notes (2026-09-03)

Sources read in full (Overleaf, public read links from the problem's proof-claims thread):
1. "Common Prime Divisors of Binomial Coefficients", author line "GPT 5.6 Sol Pro", submitted by Liam Price, accepted by the site: proves the conjecture for j ≤ 3i/2 and for n = 2j. Mechanism: Kummer/Legendre localization (Lemma: if q ≥ i divides C(n,i) but not C(n,j), then q^a | j−r and q^a | n−j−s with r+s < i), so V_i(n) | C(j,i); EEES 1978 gives C(n,i) < V_i(n)²; Vandermonde closes j ≤ 3i/2. Central case n=2j: analytic bound for k ≥ 2500 plus an exact finite check of 666 endpoint ratios (code included).
2. "Binomial coefficients sharing a large prime divisor", van Doorn & Rocca (proof found by ChatGPT 5.6 Sol, human-written): Bergman-type determinant bound G := gcd(C(n,i),C(n,j)) > e^{−2i}(n/i)^{i/4} for 4 ≤ i < j ≤ n/2. With G ≤ n^{π(i)} for a counterexample (all prime factors ≤ i), finiteness follows for i ≥ 121 (effective) and for 4 ≤ i ≤ 120 via Bugeaud–Evertse–Győry S-parts (ineffective). i = 3 not excluded. They state i ≥ 1000 has no counterexamples (explicit prime bounds + prime-gap tables to 4·10^18; maximal gap 1476 explains the "1475").

What "closing the finite set" would cost (my computation from their inequality): a counterexample needs ln n < (2i + (i/4) ln i)/(i/4 − π(i)).
| i | horizon on n |
|---|---|
| 121 | 10^672 |
| 200 | 10^72 |
| 500 | 10^26 |
| 1000 | 10^20 |
| 1475 | 10^18 |
For i < 121 no effective horizon exists at all. The Rust search (conglu) covers n ≤ 10^7 for all i. So the gap between "searched" and "proved" is 10^7 to 10^18 at i≈1475 and 10^7 to 10^672 at i=121, with nothing effective below. Verdict: NOT closable by laptop or Codex-scale computation. What would close it is mathematics: a better exponent than i/4 in the Bergman bound, or an effective S-parts theorem. UNVERIFIED that either is within reach; both are real research.
Lab decision: #699 dropped as a computational target. Recorded so nobody in this lab re-derives this.
