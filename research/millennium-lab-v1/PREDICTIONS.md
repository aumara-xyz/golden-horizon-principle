# PREDICTIONS — millennium-lab-v1 (written before any computation ran)

Vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID. No breakthrough words.
Scope this round: L1–L3 only (hyper-efficient pass). L4/L5 deferred, stubs noted.

## L1 — see it
PREDICTED: all first 200 nontrivial zeros have Re(s)=1/2 to working precision (trivially, mpmath computes them on the line; the real check is that |zeta(1/2+it)| touches 0 at exactly those t and nowhere else in range).
Kill condition: any zero off the line, or a zero of |zeta| between listed zeros.

## L2 — GUE vs controls
Unfolding: s_n = (t_{n+1}-t_n) * ln(t_n/2pi)/(2pi) for zeros; primes s = (p_{n+1}-p_n)/ln(p_n); randoms uniform -> s = gap * density.
Reference curves: nearest-neighbour GUE Wigner surmise p(s)=(32/pi^2) s^2 exp(-4 s^2/pi); Poisson p(s)=exp(-s). Pair correlation GUE R2(x)=1-(sin(pi x)/(pi x))^2; Poisson R2=1.
PREDICTED (1000 zeros): zeros closer to GUE than to Poisson on both statistics; level repulsion visible (histogram ~0 near s=0).
PREDICTED: random uniform matches Poisson, not GUE.
PREDICTED: primes match NEITHER cleanly — prime gaps are roughly Poisson-like but with parity/small-gap structure (gaps are even, gap 2 is common); they will look Poisson-ish, not GUE. If primes ALSO match GUE the zero match is meaningless.
Metric: L1 distance between empirical histogram and each reference. Winner = smaller distance. Report numbers, no adjectives.

## L3 — Peter's knob: boundary conditions on H = xp
Setup: symmetric H=(xp+px)/2 = -i(x d/dx + 1/2). In u=ln x it is unitarily -i d/du on L^2(du). Bounded interval u in [0, L].
Finite-difference matrix D (central difference) so H = -i D.
  reflecting  : Dirichlet ends (matrix truncated)             -> real spectrum, symmetric +-
  periodic    : circulant (torus, "loops")                    -> exact e.v. 2 pi n / L, an equally spaced comb
  twisted     : circulant with phase theta                    -> comb shifted by theta/L
  absorbing   : upwind (one-sided) difference, non-Hermitian  -> complex eigenvalues, not a spectrum of a self-adjoint operator
PREDICTED ranking by RMS gap to first 20 zeros after ONE tuned scale (L chosen so mean spacing matches): periodic ~ twisted < reflecting < absorbing (complex, disqualified).
PREDICTED failure signature (the actual point): every self-adjoint option gives spacings that are CONSTANT in n; the zeros' spacings SHRINK like 2pi/ln(t/2pi). No boundary condition on plain xp on a fixed interval can produce a log-growing density, because the operator is -i d/du and a first-order operator on an interval only has comb spectra. That is the gap Berry-Keating fill with the semiclassical cutoff |x|>l_x, |p|>l_p, and even that only reproduces the SMOOTH counting function N(T) ~ (T/2pi) ln(T/2pi e), not the individual zeros.
Oracle-leak rule: if any option lands within RMS < 0.5 of the first 20 zeros, assume the scale-tuning smuggled the answer in and re-test with L fixed a priori.
Secondary MEASURED: compare N(T) of zeros against Berry-Keating smooth count to show that part does work.

## L4, L5 — deferred this round
L4 (BSD on y^2=x^3-x) and L5 (artifact interrogation) not run. Stubs in RESULTS.md.
