# Codex prime gears: what survives the toy

2026-09-06. Preregistration commit: `8df1c25`. Controls executed before authentic prime-wheel results. No zeta zeros, parameter fitting, physical model, Fable code, or Fable file edits. Results are finite MEASURED tests of established elementary mathematics, not a new theorem or RH evidence.

## 1. Nested gears reproduce the sieve

The mask is m(n)=product over d of (1-[d divides n]). Each base prime is excluded from this mask and must be restored separately when generating a prime list. Crossed-out numbers do not become composite by being crossed out. The sieve detects pre-existing divisibility.

| Prime gear periods | Exact minimal mask period | First composite that slips through | Composite survivors in 2..10000 |
|---|---:|---:|---:|
| 2,3 | 6 | 25 | 2105 |
| 2,3,5 | 30 | 49 | 1439 |
| 2,3,5,7 | 210 | 121 | 1059 |
| 2,3,5,7,11 | 2310 | 169 | 852 |

MEASURED: adding the next prime removes that first composite; the next first composites are 49,121,169,289 respectively. Explanation: a composite below the next prime's square has a prime factor among the existing gears. No assumption of random independence is required.

Control: pairwise coprime COMPOSITE periods 4,9,25 also give exact repetition (900 ticks) and strong Fourier peaks (power 0.0455111 at frequency 1/4). Thus the existence of peaks does not distinguish prime from composite periods. This control is not density-matched; no claim about relative spectral strength or the exact YouTube visualization is made. These are sieve-mask spectra, not spectra of prime gaps or zeta.

Mutation: adding period 4 to 2,3,5 changes the full clock-configuration period from 30 to 60, but leaves the observed mask's minimal period at 30. A changed underlying state can be invisible to this observer. This is an exact coarse-graining example, not an information-preservation theorem.

## 2. Primes as coordinates — preserve labels

MEASURED: all integers 1..1000 reconstruct exactly from their prime-exponent vectors: 1000 distinct addresses. Summing all exponents (making every prime the same step) leaves only 10 distinct labels. For example, 4 and 6 both become two steps, though their prime addresses differ. Multiplication becomes coordinate addition, independently tested for every pair in 1..39.

The origin is 1, the empty product. Signed integers reconstruct exactly with a separate sign bit; erasing it merges 1000 pairs n,-n. Zero is outside this multiplicative encoding. This is a lossless representation, not a demonstrated storage compression scheme.

## 3. Same 27 states, different wrap rules

MEASURED, integer-exact: 9a+3b+c with a,b,c in {-1,0,1} bijects onto -13..13.

| Label count | One cyclic counter: maximum additive order | Independent digit counters: maximum additive order |
|---|---:|---:|
| 9 (two trits) | 9 | 3 |
| 25 (two base-5 digits) | 25 | 5 |
| 27 (three trits) | 27 | 3 |

Z/27Z and (Z/3Z)^3 have identical cardinality but different group laws. In the former, adding 1 visits all 27 states; in the latter, repeatedly adding any fixed vector returns within 3 steps. This is algebra/dynamics, not a distinction between their finite discrete topologies (both are 27-point discrete spaces). A torus, graph adjacency, or tesseract embedding requires additional structure not forced by the labels.

## 4. Phi scaling

Scale all periods by c and compare at correspondingly scaled times: exp(2*pi*i*(c*u)/(c*p))=exp(2*pi*i*u/p). This exact cancellation predicts no distinguished c. MEASURED floating discrepancies: phi 2.85e-14 or less, sqrt(2) 1.44e-14 or less; tolerance 1e-12. These errors are numerical, not tiny physical effects.

Mutation: scale ONLY the period-5 gear. The return at t=30 is lost for both phi (unit-circle chord distance 1.5872) and sqrt(2) (1.3811). In either case irrational relative timing prevents an exact positive common return with the unchanged period-2 gear. This does not compare approximate long-time recurrence quality. Other relative-coupling models are UNVERIFIED, not ruled out by this limited test.

## Ledger and verification

All preregistered predictions HELD within their stated finite scope; individual outcomes recorded in results.json. No prediction removed. An additional assertion explicitly checks that the next square survives each next-prime mutation. Four independent unittest checks cover gcd equivalence and exact density, direct Fourier summation for a control peak, multiplicative coordinate reconstruction, and ternary carry/order behavior. Floating arithmetic is confined to FFT/phase diagnostics and the figure; masks, primality, factorizations and additive orders use integers.

Run: `python3 experiments/prime_gears_codex/run.py`

Tests: `python3 -m unittest discover -s experiments/prime_gears_codex -p 'test_*.py'`

Python 3, NumPy 2.0.2, Matplotlib; no network required. Matplotlib reported an unwritable default font cache and used a temporary directory; figure output succeeded. Figure inspected visually.

## What landed / honest paragraph

The gear intuition precisely describes periodic divisibility filters. Independent prime axes preserve arithmetic information. But circles, Fourier spikes, a chosen 27-state encoding, and global phi scaling do not add an RH mechanism. The potentially useful engineering lesson is that the observer's mask can hide changed underlying dynamics, and that identical state labels can implement inequivalent transition rules. Neither is claimed as new. No infinite-limit certificate, zeta spectral identity, holographic physics, or new prime-counting bound was obtained.

Background: sieve of Eratosthenes, unique factorization, and [Chinese remainder theorem](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/crt.pdf). Arithmetic topology is a separate established research subject, not implemented here.
