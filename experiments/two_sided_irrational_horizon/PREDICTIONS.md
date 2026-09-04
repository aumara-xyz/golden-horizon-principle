# TWO-SIDED-IRRATIONAL-HORIZON v0 — preregistration

- Date locked: 2026-09-04
- Status lane: mathematical scattering toy; no RH or Hawking-physics claim.
- No prime list and no zeta-zero ordinate enters the construction or tuning.
- Vocabulary: `MEASURED`, `UNVERIFIED`, `PREDICTED`, `VOID`.

## Fixed model

Two channels, left and right, meet at a symmetric seam. At real frequency `omega`, use

`S(omega) = [[sqrt(1-q), i sqrt(q)], [i sqrt(q), sqrt(1-q)]]`,

where `q(omega) = exp(-2*pi*omega/kappa)` and `kappa=1`. This is only a
Hawking-*like* Boltzmann leakage profile, not a derivation of Hawking radiation. The full
two-channel scattering matrix should be unitary. A one-sided observer retains reflection
amplitude `r=sqrt(1-q)` and treats the other channel as radiation.

The two propagation phases are `exp(i t)` and `exp(i alpha t)`. The authentic irrational
choice is `alpha=phi`. Controls are `alpha=3/2`, `sqrt(2)`, `pi-3`, and 500 uniform random
irrationals in `[0.1,0.9]`, seed 20260904.

For recurrence, evaluate integer winding times `t=2*pi*q` and the phase mismatch
`||q alpha||`, distance to the nearest integer. Use the tail statistic

`C(alpha) = min_{100 <= q <= 10000} q ||q alpha||`.

Larger `C` means rational phase locking is more strongly delayed. The random controls run
before `phi`. Also report the continued-fraction/Fibonacci recurrence sequence for `phi`.

For a one-sided loop of length `L=1` with reflection amplitude frozen at carrier
`omega_0`, poles of `1-r exp(i z L)` occur at

`z_n = 2*pi*n + i log(r)`.

Evaluate carriers `omega_0 in {0.05, 0.1, 0.25, 0.5, 1}`. Finally, use an unrelated
off-line quartet with `beta=0.7`, `gamma=phi` to test whether the mirror equations
`F(1-s)=F(s)` and `F(conj(s))=conj(F(s))` alone force the symmetry line.

## Predictions

1. **PREDICTED:** full two-sided unitarity and mirror commutation hold to `1e-12` over
   `omega in [0.01,10]`.
2. **PREDICTED:** after discarding the mirror side, every tested nonzero leakage produces
   a pole strictly below the real frequency axis. Radiation does not itself force reality.
3. **PREDICTED:** the off-line quartet satisfies both mirror identities to `1e-12`, proving
   those symmetries alone are insufficient.
4. **PREDICTED:** `phi` has a larger delayed-recurrence statistic than at least 95% of the
   500 random controls. If not, the finite-window “golden non-recurrence” claim is `VOID`.
5. **PREDICTED:** none of these checks generates primes, the `T log T` counting law, or a
   zeta trace formula. Any RH interpretation remains `UNVERIFIED`.
