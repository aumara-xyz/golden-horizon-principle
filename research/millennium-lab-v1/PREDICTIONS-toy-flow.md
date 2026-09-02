# Toy T4 — de Bruijn–Newman flow on the first 1000 zeros (before compute)
Dynamics (Rodgers–Tao 2018, eq. for real simple zeros of H_t): x_j' = sum_{k != j} 2/(x_j - x_k) + sum_k 2/(x_j + x_k)   (H_t is even; mirror zeros included). Forward t: repulsion. Backward t: attraction.
Truncation: only the first 1000 zeros; the unseen zeros above are a missing far field. Report the inner 800 to limit edge effects; state the caveat.
PREDICTED F1 (forward): the coefficient of variation of locally-normalized spacings falls from ~0.42 at t=0 to below 0.15 by t=2: the zeros head toward a comb (Coulomb-gas equilibrium is the lattice).
PREDICTED F2 (forward): no collisions ever (repulsion), min gap increases monotonically.
PREDICTED B1 (backward): the first collision (two zeros meeting, then leaving the line) happens at t_c ~ -g_min^2/8 within a factor of 2, where g_min is the smallest gap among the first 1000 zeros; and the colliding pair IS that closest pair.
PREDICTED B2: with the full zero set the true statement is Rodgers–Tao's Lambda >= 0: collisions occur for every t<0 somewhere far up. Our truncated t_c is an upper bound on |Lambda| only in spirit; it is not a measurement of Lambda. Written here so nobody reads it as one.
Kill: a collision in the forward direction, or a backward collision that is not the closest pair.
