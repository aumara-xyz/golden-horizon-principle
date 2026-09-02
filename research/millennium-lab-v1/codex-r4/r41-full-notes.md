# R4.1 all-node finite-block flow

## Scope and method

**MEASURED:** `r41_full_flow.py` dynamically evolves every retained node in
each 10,000-zero block and places a terminal event on the minimum of all 9,999
consecutive gaps. The equation is Fable's toy-T4 finite system,

\[
 \dot x_j=\sum_{k\ne j}\frac{2}{x_j-x_k}
          +\sum_k\frac{2}{x_j+x_k}.
\]

The printed offsets are parsed as decimal numbers before a local origin is
chosen, so the high-block bases are never discarded through binary64
subtraction. For block A every mirror term is summed directly. For blocks
B--D the mirror field is recomputed on every force call with a cubic moment
expansion; the largest recorded first-omitted-tail bound is below
$2.5\times10^{-40}$. The dense direct Cauchy sums use float64 PyTorch on CPU;
DOP853 uses `rtol=2e-9`, `atol=2e-12`. The event is at one percent of the
initial minimum gap and the residual two-body tail $\epsilon^2/8$ is added.

All four input files are hashed afresh by the runner and checked against the
frozen expected SHA-256 values. As an implementation control, the full
1,000-node toy T4 reproduces Fable's published event time
`0.003317670111905755` and pair 922--923 exactly at the stored precision. As
an independent numerical cross-check, a separately coded 1,024-node active
window agrees with every primary and mutation time within $7.1\times10^{-9}$
relative; Poisson cross-checks agree within $2.1\times10^{-6}$.

For a portable replay, download official tables `zeros1`, `zeros3`, `zeros4`,
and `zeros5` from <https://www-users.cse.umn.edu/~odlyzko/zeta_tables/>, save
them without byte changes as the corresponding `.txt` names, and pass their
directory with `--data-dir`. The full runner's fresh hash checks reject any
other bytes. The committed source replaces the run host's session-local
default path only; numerical parsing and the hash-validated inputs are
unchanged.

## Primary events

| Block | midpoint $T$ | global colliding pair | $g_{\min}$ | $g_{\min}^2/8$ | full-block time | actual / predicted |
|---|---:|---:|---:|---:|---:|---:|
| A, first $10^4$ | 5448.908413286 | 6709--6710 | 0.037698499 | 1.77647103e-4 | 1.77801162e-4 | 1.000867 |
| B, near ordinal $10^{12}$ | 267653396932.4000896404 | 1000000008625--1000000008626 | 0.0055569683 | 3.85998709e-6 | 3.86067467e-6 | 1.000178 |
| C, near ordinal $10^{21}$ | 144176897509546974243.30009392 | 1000000000000000001635--1000000000000000001636 | 0.00530012 | 3.51140900e-6 | 3.51394660e-6 | 1.000723 |
| D, near ordinal $10^{22}$ | 1370919909931995308897.54512111 | 10000000000000000006442--10000000000000000006443 | 0.00881124 | 9.70474379e-6 | 9.80213467e-6 | 1.010035 |

**MEASURED:** the initial global minimum-gap pair collided first in all four
blocks; every ratio lies inside the registered 0.90--1.15 interval.

## Controls and mutations

| Block | Poisson time | Poisson / Odlyzko | delete-pair mutation time | mutation ratio | mutation global pair |
|---|---:|---:|---:|---:|---:|
| A | 2.58501e-12 | 1.45388e-8 | 2.34117738e-4 | 1.001084 | 4765--4766 |
| B | 5.48602e-10 | 1.42100e-4 | 1.62042893e-5 | 1.000813 | 1000000004240--1000000004241 |
| C | 1.23660e-10 | 3.51911e-5 | 1.07095256e-5 | 1.001600 | 1000000000000000006362--1000000000000000006363 |
| D | 9.88680e-11 | 1.00864e-5 | 1.39328938e-5 | 1.003804 | 10000000000000000003763--10000000000000000003764 |

**MEASURED:** every fixed-seed, density-matched Poisson time is below
$10^{-3}$ of its Odlyzko counterpart; the closest Poisson pair collides first
and each two-body ratio is within $10^{-5}$ of one at the supported event/tail
precision. After deleting the
primary event pair, the next closest pair collides first in all four blocks
and every mutation ratio lies inside 0.85--1.20.

## Scaling and theorem boundary

**PREDICTED:** for fixed $n=10^4$, the GUE cubic small-gap CDF gives
$s_{\min}=O(n^{-1/3})$. At density
$d(T)=\log(T/2\pi)/(2\pi)$ this gives
$|t_c|=O(n^{-2/3}d(T)^{-2})$: density/log-height exponent $-2$, literal
$T$-power exponent zero with a squared-log correction. A Poisson block has
$|t_c|=O(n^{-2}d(T)^{-2})$ and ensemble-scale ratio $n^{-4/3}$.

**MEASURED:** regressing the four realized Odlyzko times gives slope
$-1.78035$ for $\log |t_c|$ on $\log d(T)$. It has the registered negative
sign, but four extreme gaps do not measure the ensemble exponent.

These are truncated finite-block collision times. They are not measurements,
estimates, upper bounds, or lower bounds for $\Lambda$. Rodgers--Tao (2018)
proved $\Lambda\ge0$: at every negative heat time, some zero is nonreal.
D.H.J. Polymath (2019) proved $\Lambda\le0.22$: at every heat time at least
0.22, all zeros are real. Neither theorem identifies a finite-block first
collision with $\Lambda$.

Primary sources: [Rodgers--Tao 2018](https://arxiv.org/abs/1801.05914) and
[D.H.J. Polymath 2019](https://arxiv.org/abs/1904.12438).
