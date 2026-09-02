# R4.1 active-window surrogate notes

> This artifact is retained as an independent numerical cross-check. It was
> superseded as the primary R4.1 measurement by `r41_full_flow.py`, which
> dynamically evolved all 10,000 retained nodes and monitored every gap. See
> `r41-full-results.json`, `r41-full-results.csv`, and `r41-full-notes.md`.

## Scope and method

**MEASURED active-window approximation.** The runner parses every printed
offset as a `Decimal` and keeps the integer base separate. For each 10,000-row
case it evaluates the complete all-particle force and the diagonal one-body
derivative at $t=0$. It then evolves 128, 256, 512, and 1,024 moving zeros
centered on the initial closest pair; omitted nodes enter through that exact
initial field plus its linear response. The reported time is the 1,024-window
value. It is therefore not an exact full-10,000 integration.

At the first block, every mirror term is summed directly. At the remote
blocks, the initialized mirror field uses a cubic moment expansion in the
offset/base ratio. The largest first-omitted-term bound was
$1.76\times10^{-40}$. The event threshold is $10^{-3}g_{\min}$, with the
remaining two-body tail $\epsilon^2/8$ included in the reported zero-gap
time.

The legacy full-1,000 T4 calculation was reproduced with exactly the published
event time and pair. Under close-pair recentering and tighter tolerances, the
128/256/512/1,000 active-window relative errors against a full-1,000 reference
were $2.00\times10^{-9}$, $6.57\times10^{-10}$,
$8.57\times10^{-11}$, and $3.59\times10^{-12}$, respectively. Across the
new primary and mutation runs, the 512-to-1,024 time change was at most
$4.59\times10^{-11}$; for the Poisson controls it was at most
$8.74\times10^{-7}$. The looser-tolerance 1,024-window check differed by at
most $5.32\times10^{-7}$.

## Primary events

| Block | exact midpoint used for density | closest global zero pair | $g_{\min}$ | $g_{\min}^2/8$ | event time | actual / predicted |
|---|---:|---:|---:|---:|---:|---:|
| A, first 10,000 | 5448.908413286 | 6709–6710 | 0.037698499 | 1.7764710336e-4 | 1.7780116276e-4 | 1.0008672 |
| B, ordinal $10^{12}$ | 267653396932.4000896404 | 1000000008625–1000000008626 | 0.0055569683 | 3.8599870859e-6 | 3.8606746988e-6 | 1.0001781 |
| C, ordinal $10^{21}$ | 144176897509546974243.30009392 | 1000000000000000001635–1000000000000000001636 | 0.00530012 | 3.5114090018e-6 | 3.5139466203e-6 | 1.0007227 |
| D, ordinal $10^{22}$ | 1370919909931995308897.54512111 | 10000000000000000006442–10000000000000000006443 | 0.00881124 | 9.7047437922e-6 | 9.8021347371e-6 | 1.0100354 |

**MEASURED:** every event pair was the initial global minimum-gap pair, and all
four ratios lie inside the registered 0.90–1.15 interval.

## Controls and registered mutations

| Block | Poisson event time | Poisson / Odlyzko | mutated event time | mutated actual / predicted | mutated global event pair |
|---|---:|---:|---:|---:|---:|
| A | 2.5850073204e-12 | 1.45388e-8 | 2.3411773986e-4 | 1.0010841 | 4765–4766 |
| B | 5.4860215854e-10 | 1.42100e-4 | 1.6204289452e-5 | 1.0008132 | 1000000004240–1000000004241 |
| C | 1.2365954147e-10 | 3.51911e-5 | 1.0709525647e-5 | 1.0015996 | 1000000000000000006362–1000000000000000006363 |
| D | 9.8868117792e-11 | 1.00864e-5 | 1.3932893922e-5 | 1.0038035 | 10000000000000000003763–10000000000000000003764 |

**MEASURED:** all four fixed-seed, density-matched Poisson controls were below
$10^{-3}$ of the corresponding Odlyzko time and their two-body ratios were
within $1.1\times10^{-6}$ of one. After deleting each primary event pair,
the new closest pair collided first in all four blocks and every ratio lay
inside the registered 0.85–1.20 interval.

## Height scaling and boundary

**PREDICTED:** fixed-$N$ GUE cubic small-gap statistics give
$t_c\asymp d(T)^{-2}\asymp[\log(T/2\pi)]^{-2}$: density exponent $-2$,
literal $T$-power exponent zero with a squared-log correction.

**MEASURED:** the four individual Odlyzko events give slope $-1.78035$ in a
regression of $\log t_c$ on $\log d$, so the preregistered negative-slope
prediction survived. Four extreme gaps do not measure the ensemble exponent
$-2$.

These are finite, truncated-block active-window surrogate times. They are not
measurements, estimates, upper bounds, or lower bounds for the
de Bruijn–Newman constant $\Lambda$. Rodgers and Tao, *The de Bruijn–Newman
constant is non-negative* (2018), proved $\Lambda\ge0$. D.H.J. Polymath,
*Effective approximation of heat flow evolution of the Riemann xi function,
and a new upper bound for the de Bruijn–Newman constant* (2019), proved
$\Lambda\le0.22$.

## Limitation

The active-window convergence is numerical evidence about the stated
finite-block approximation. Omitted zeros are not dynamically evolved, so the
artifacts do not claim an exact first-collision theorem for any full 10,000-zero
system. The delete-pair runs independently expose the next closest candidate;
its event remained later in every block.
