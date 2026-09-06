# Physics bridges: symmetry versus zero confinement

2026-09-06. Predictions committed at85c20ab before computation. No zeta
zero ordinates used. No new RH theorem or novelty claim.

## Lee–Yang control experiment

For spins sigma_i in {-1,+1}, use dimensionless coupling K and
q=exp(-2K). Removing a positive common factor, the uniform-field partition
polynomial is P(z)=sum_sigma q^(number of disagreeing edges) z^(number of
down spins). The two-spin case has one edge; the four-spin case is a ring.
Global spin reversal makes coefficients palindromic for BOTH signs of K.
All weights are positive. Ferromagnetism means K>=0, or 0<q<=1.

| Model | Exact coefficients, ascending | Zero location |
|---|---|---|
| 2 spins, q=2 control | 1,4,1 | off circle |
| 4 spins, q=2 control | 1,16,48,16,1 | off circle |
| 2 spins, q=1/2 | 1,1,1 | on circle |
| 4 spins, q=1/2 | 1,1,9/8,1,1 | on circle |
| Independent spins q=1 | binomial coefficients | all at -1 |

Coefficients came from exhaustive enumeration with exact rational arithmetic;
independent closed formulas were asserted. Four-spin numerical roots have
circle deviation <5e-16 in the ferromagnetic case; the control has real
roots approximately -12.1604,-3.46910,-0.288259,-0.0822341. Root outputs
are MEASURED diagnostics, not interval root certificates.

An algebraic check avoids relying on numerical root locations. For
P(z)=1+bz+cz^2+bz^3+z^4, divide by z^2 and set y=z+1/z.
The equation becomes y^2+by+c-2=0. For q=1/2 the y roots are
-1/2 +/- 3sqrt(2)/4, both strictly between -2 and2, so all z roots lie on
the unit circle. For q=2 the y roots are -8 +/- 3sqrt(2), both below -2,
so the z roots are negative real reciprocal pairs off the circle.

For two spins P(z)=z^2+2qz+1. If q<=1 its roots are
-q +/- i sqrt(1-q^2), of modulus1; if q>1 they are
-q +/- sqrt(q^2-1), off the circle. Thus the simplest case shows exactly
what reflection does NOT supply: a restriction on interaction strengths.

The general ferromagnetic circle theorem is due to Lee and Yang (1952),
not this experiment. These finite tests illustrate it and its hypotheses.
[Original paper](https://journals.aps.org/pr/abstract/10.1103/PhysRev.87.410).

## Ternary does not automatically imply circle zeros

One three-state variable s in {-1,0,+1}, with endpoint weights1 and
middle weight a>0, has Laurent partition expression z^-1+a+z.
Multiplying by z gives P_a(z)=1+az+z^2; no zero is introduced at0.
All cases are reflection-symmetric and all coefficients positive.

- a=1: two circle zeros.
- a=2: a double root at -1.
- a=3: two off-circle roots (-3 +/- sqrt(5))/2.

The last pair is -phi^2 and -phi^-2, with phi=(1+sqrt(5))/2. This was
not a tuning input: a=3 was preregistered before calculation. It is an
elementary algebraic identity, NOT evidence connecting the golden ratio
to RH; here it occurs in the counterexample to circle confinement.
The discriminant a^2-4 proves the classification for every a>0.

## What would actually transfer to Riemann?

A sufficient route would be a family of entire functions F_m(t) obtained
from a proven real-zero class of statistical-mechanics models, converging
uniformly on every compact subset of C to Xi(t)=xi(1/2+it). If every F_m
has no nonreal zeros and the nonzero limit is Xi, Hurwitz's theorem implies
that Xi has no nonreal zeros. This is a conditional proof blueprint, not
a construction we possess. Matching finitely many values, coefficients,
or zeros does not establish that convergence or preserve the hypotheses.

The unresolved tasks are (1) a representation determined independently
from zeta's arithmetic, (2) the actual Lee–Yang hypotheses, and (3) rigorous
complex-domain convergence and normalization. Our finite Weil certificates
establish none of these three. Ferromagnetic Ising inequalities cannot
simply be assigned to a matrix because its entries have a convenient sign.

## Other fields: useful role and non-transfer

| Field | Useful connection | What is not established |
|---|---|---|
| Quantum chaos | Random-matrix statistics motivate spectral operators | Statistical resemblance does not identify all zeta zeros |
| Statistical mechanics | Interaction hypotheses can force partition zeros onto a circle | No such exact zeta representation constructed here |
| Holographic quantum coding | Isometric bulk-to-boundary encoding and recoverability | No observer-created universe, zeta spectrum or quark model follows |
| Classical waves | Operator domains, energy estimates, boundary conditions | A resonant horn does not automatically have a prime or zeta spectrum |
| Chemistry/biology | Possible sources of coupled-system models | No specific quantitative bridge to RH identified in this pass |

The quantum-chaos connection is existing research, not a new test here:
[IAS overview](https://www.ias.edu/ideas/2013/primes-random-matrices).
Pastawski, Yoshida, Harlow and Preskill's 2015 holographic code constructs
an isometry and recoverable quantum information in an explicit toy model;
it does not assert a conscious observer creates reality.
[Paper](https://arxiv.org/abs/1503.06237).

For Aukora, the concrete transfer is to test reconstruction under declared
erasures against an explicit decoder, and distinguish reversible encoding
from genuine error correction. The existing ternary experiment's parity-only
null pattern already warns that multiple views need not recover an interior.
No new quantum code or runtime integration was implemented in this pass.

## Ledger and scope

All preregistered predictions survived. Controls executed before matched
models; two-to-four-spin mutation retained the distinction. q=1 repeated
roots were treated algebraically. Source coefficients are exact; general
physics/theorem references are not newly verified experiments.

The result is a clearer target: interaction conditions and a convergence
theorem, rather than symmetry or ternary labels alone. RH, a novel physical
mechanism, and any claimed unification remain UNVERIFIED. No paper's claimed
RH proof is adopted here. Nothing in this pass changes the status of our
finite and pure-tail Weil bounds.

Reproduce with Python, numpy: `python experiments/lee_yang_bridge/run.py`.
The script asserts exact enumerated coefficients; full output is results.json.
