# Erdős #307 — two finite sets of primes P, Q with (Σ_P 1/p)(Σ_Q 1/q) = 1. VERIFIABLE. Written before compute.

Structure (Fable, derived by hand, to be checked by the code): for distinct primes, Σ_{p∈P} 1/p = A/ΠP in lowest terms with A = Σ_p Π_{p'≠p} p' coprime to ΠP. Likewise Σ_Q 1/q = B/ΠQ. Product 1 ⟹ A·B = ΠP·ΠQ; coprimality forces ΠQ | A and ΠP | B, hence A = ΠQ and B = ΠP exactly. So a solution is: a set Q whose reciprocal-sum numerator B is squarefree with prime factors disjoint from Q, P := those factors, and then A_P = ΠQ must hold. Given Q, P is determined. Enumerating the smaller set covers every solution whose smaller set is within the enumeration.
Known fact (site): P, Q disjoint, |P ∪ Q| ≥ 60.
Positive control: allowing 1 ∈ Q, the same algorithm must recover the site's examples (1+1/5)(1/2+1/3)=1 and (1+1/41)(1/2+1/3+1/7)=1 and the primary-pseudoperfect family. If it does not, the code is wrong and nothing else counts.
P1: no solution with the smaller set Q ⊆ first 30 primes and |Q| ≤ 7 (≈ 2.6M sets). PREDICTED: none.
P2: the positive control recovers both site examples. PREDICTED: yes.
P3: for |Q| ≤ 7, B = numerator(Σ_Q 1/q) is squarefree with all factors outside Q in fewer than 5 % of sets; and among those, A_P = ΠQ never holds. PREDICTED.
Kill: any (P,Q) found is checked by exact rational arithmetic before being reported; a hit that fails exact re-verification is a bug.
What a hit would be: a new theorem-level fact (an example). What a miss is: a bounded negative, MEASURED, and the derived structure A=ΠQ, B=ΠP, which may or may not be in the literature (UNVERIFIED).
