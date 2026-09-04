# METATRON-PRIME-RETURN v0 — preregistration

- Date locked: 2026-09-04
- Lane: Riemann adjacency; analogue and falsification instrument only.
- Construction embargo: no zeta-zero ordinate is used to choose the graph, lengths,
  scale, magnetic phase, numerical window, or acceptance threshold.
- Claim vocabulary: `MEASURED`, `UNVERIFIED`, `PREDICTED`, `VOID`.

## Construction fixed before computation

Use the 13-center three-dimensional lift of the Metatron drawing: one central vertex and
the 12 vertices of a cuboctahedron. Join the 24 cuboctahedron edges and all 12 radial
spokes, giving a connected 13-vertex, 36-edge metric graph. The central vertex is the
multiplicative-identity analogy (the constant or zero-frequency state); it is not called
a prime.

The authentic metric is obtained by deforming the cuboctahedron coordinates by the fixed
diagonal map `diag(1, phi, phi^2)`, taking Euclidean edge lengths, and normalizing their
mean to one. The wave operator is the standard self-adjoint metric-graph Laplacian with
continuity and Kirchhoff conditions at every vertex. A finite-element discretization will
use 24 subdivisions per unit length and will be checked at 16 and 32.

For the primitive-return test, enumerate every undirected simple cycle of 3 through 8
edges, remove reversal and cyclic duplicates, and rescale the entire graph once so that
its shortest cycle has length `log(2)`. Score the first 25 primes by the median, over
`log(p)`, of the distance to the nearest cycle length divided by the local adjacent
`log(prime)` spacing. This one-scale calibration is declared in advance and uses no zeta
zero.

## Controls — computed before the authentic score

1. Equilateral metric on the same graph.
2. Two hundred independent random permutations of the authentic edge-length multiset.
3. Two hundred independent lognormal edge sets matched to the authentic mean and
   coefficient of variation, seed 20260904.
4. Spectral-statistics control: the authentic real/Kirchhoff operator compared with the
   same metric carrying a fixed irrational magnetic flux `2*pi/phi` through a deterministic
   edge orientation. The latter is a mutation, not part of the prime-return claim.

Clarification locked before the first run: spectral spacings use positive eigen-wavenumber
indices 21 through 180 inclusive; the Weyl-slope fit uses the same window. The cycle-score
control percentile is the fraction of control scores less than or equal to the authentic
score, so a surviving result must be below the 5th percentile in both random ensembles.

## Predictions and decision rules

1. **PREDICTED — neutral state.** The connected Kirchhoff graph has exactly one zero
   eigenvalue. This realizes `1` as a neutral foundation only; it carries no prime data.
2. **PREDICTED — prime-return test fails.** The authentic golden metric will not beat the
   95th percentile of both random-control ensembles (smaller score is better). If it does,
   rerun with 1,000 controls and cycles through 10 edges before calling it `MEASURED`.
3. **PREDICTED — wrong symmetry class.** After removing the zero mode and unfolding a
   fixed middle spectral window, the real/Kirchhoff chamber will be closer in
   Kolmogorov–Smirnov distance to GOE than GUE. The magnetic mutation may move toward GUE.
4. **PREDICTED — Weyl-law obstruction survives.** A fixed finite metric graph has
   `N(k) = (L_total/pi) k + O(1)`, not the Riemann-von Mangoldt `T log T` leading growth.
   Numerics should recover the linear slope within 3% at the finest discretization.
5. **VOID rule.** Any claimed prime alignment is `VOID` if the control order is violated,
   if a zeta zero enters construction or tuning, or if the result disappears at either
   convergence resolution.

## What would count as progress

A control-surviving `log(p)` alignment would identify a finite geometric pattern worth
independent reconstruction. It would still not establish RH. A self-adjoint extension
with broken time-reversal symmetry and the correct non-linear counting law would remain
necessary before this could resemble a Hilbert–Pólya candidate.
