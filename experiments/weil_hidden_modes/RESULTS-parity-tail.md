# Parity sectors and the pure infinite tail

2026-09-05. Predictions: ae7424b; tail-constant follow-up: 535af86.
No zero ordinates entered constructions, cutoffs, basis choices or vectors.
All work is local. No Fable files edited.

## 1. Finite computation: 16, 24, 32 modes

L=7/10, zero-extended normalized Dirichlet sines. Odd sine indices are
spatially EVEN; even indices are spatially ODD. Reflection gives exact
decoupling. This is true for the authentic matrix and all three controls.

Entries were enclosed with Arb at 512 bits, integral tolerances 10^-55,
epsilon=10^-65, and the proven omitted-integral bound used previously,
now with maximum sine index 32. The old N16 entry enclosures all overlap
the new independently integrated leading blocks. Interval LDL proves
the finite signs. Saved midpoint eigenvalues below are approximations,
not interval eigenvalue enclosures.

| Total N | Even sector minimum (MEASURED approximation) | Odd sector minimum (MEASURED approximation) | Certified lower bounds, even / odd |
|---|---:|---:|---:|
| 16 | 1.89239053550e-12 | 7.66218977016e-10 | 1e-12 / 1e-12 |
| 24 | 6.29052863285e-13 | 4.51242211158e-10 | 1e-16 / 1e-12 |
| 32 | 5.97208622358e-13 | 3.31312599366e-10 | 1e-16 / 1e-12 |

N32 means 16 modes in each sector, not 32 per sector. The bounds use the
preregistered coarse powers-of-ten grid; they are deliberately weaker than
the displayed numerical minima. Midpoint eigensolver residuals are below
2e-100. This is a diagnostic of the midpoint calculation, not extra proof.

| Model at N32 | Even minimum approximation | Odd minimum approximation | Interval-certified signs |
|---|---:|---:|---|
| Archimedean-only | -0.2397838773 | -0.7207130982 | both have a negative direction |
| Prime logs +10% | -0.0957529298 | -0.1201493518 | both have a negative direction |
| Prime logs -10% | -0.1998248230 | +0.1054915125 | even negative direction; odd positive |
| Authentic | +5.972086224e-13 | +3.313125994e-10 | both positive |

Controls ran before authentic diagnostics. Their signs persist at N16 and
N24. In particular, one control's odd sector is positive: positivity of a
single symmetry sector is not by itself an arithmetic discriminator.

## 2. An analytic estimate covering infinitely many high modes

This is a pure-tail bound, not a full-window positivity certificate. Its
proof is given in PURE-TAIL-LEMMA.md. For a real H_0^1 test function on
[-7/10,7/10] with all sine coefficients j<=4096 equal to zero, we obtain

    Q(f_even) >= 0.5600 ||f_even||_2^2,
    Q(f_odd)  >= 0.4428 ||f_odd||_2^2.

The displayed constants are rounded DOWN from validated balls. Thus the
combined pure tail satisfies Q(f)>=0.4428||f||_2^2. This statement covers
infinitely many coefficients at once; no 4096-by-4096 matrix was built.
It uses Fourier cutoff R=256 and a bound on leakage of high sine modes
into lower Fourier frequencies. The arithmetic is bounded by its total
weight, so all controls also pass:

| Model | Even pure-tail lower bound, j>4096 | Odd pure-tail lower bound, j>4096 |
|---|---:|---:|
| Archimedean-only | 3.5020 | 3.3848 |
| Prime logs +10% | 1.2531 | 1.1360 |
| Prime logs -10% | 0.5600 | 0.4428 |
| Authentic | 0.5600 | 0.4428 |

Mutation j>8192 with R unchanged improves the authentic bounds to 0.6627
and 0.5456. All these decimals are rounded down. This result is based on
an elementary spectral estimate; no novelty claim is made.

The agent's exploratory N32,R10 version of the estimate gave negative lower
bounds and was inconclusive. Negative LOWER bounds do not establish negative
directions. This calculation preceded the tail follow-up preregistration;
it is recorded as exploratory, not as a successful preregistered test.

## 3. The gap we have NOT closed

We certified the first 32 modes and bounded the pure tail after 4096.
Modes 33 through 4096 have not been certified together. More importantly,
positivity of separate low and high blocks does not prove positivity of
their combination. The mixed term must be controlled WITHIN each parity
sector. Mirror symmetry only removes coupling BETWEEN the sectors.

For example, the matrix [[1,2],[2,1]] has positive diagonal blocks but a
negative eigenvalue. The corresponding requirement is a justified bound
on C relative to the positive blocks A and D, or a different reduction
that controls the interaction with a definite sign. Our pure-tail bound
alone gives neither. No full-window or all-window theorem is claimed.

Another correction: decreasing finite minima at fixed L do not show that
the limiting minimum is zero. A tiny positive limit is compatible with
all the data. Nor does RH require one common positive margin for all L.

## 4. Literature check changes the next target

[arXiv:2608.24827v2](https://arxiv.org/html/2608.24827v2), by Xuefeng Zhu,
revised September 2, 2026, already claims all-function positivity on
[-0.8,0.8], including the odd sector. Its earlier v1 lists Marcus Chuk;
the arXiv record explicitly notes the author/affiliation update. We cite
the version actually read, not an inferred attribution.

The preprint replaces a high-frequency part by a lower envelope, then
controls a Legendre-basis truncation and its tail. If its certificate is
valid, support inclusion already covers our L=0.7 window. We have NOT
independently reproduced that certificate. The claim therefore remains
UNVERIFIED in this lab; a posted theorem is not our verification of it.
Its upper-bound pipeline also uses zeros to propose some trial vectors,
unlike our no-zero construction rule. We have not imported those vectors.

The better next bounded task is an independent reproduction/audit of that
frequency-envelope reduction and its data, not another small sine matrix
presented as new progress on RH. A known or claimed fixed-window result
is not an all-window result.

## 5. Prediction ledger and honest paragraph

- Authentic finite sectors positive: survived with interval signs.
- Finite minima decrease and even is smaller: survived numerically.
- Controls retain a negative sector: survived with interval signs.
- Symmetry alone fails as discriminator: established by controls.
- Infinite pure-tail even >0.5 and odd >0.3 at j>4096: survived with bounds.
- Tail controls also positive; moving cut to8192 improves bounds: survived.
- No usable full-window bound from symmetry alone: unchanged; no such proof.

We improved a finite certificate and derived a quantitative bound on an
infinite class of high-mode test functions. We did not prove positivity
for mixtures of all modes, discover a zeta operator, establish a new
physical interpretation, or establish novelty. The work now identifies
the coupling estimate and the existing frequency-envelope construction
as more useful targets than further geometric analogies.

## Reproduce

In an environment with python-flint 0.6.0:
`python experiments/weil_hidden_modes/parity_tail.py` and
`python experiments/weil_hidden_modes/pure_tail_bound.py`.
For midpoint diagnostics, mpmath 1.3.0:
`python experiments/weil_hidden_modes/parity_diagnostics.py`.
Outputs are the corresponding *_results.json and parity_diagnostics.json.
