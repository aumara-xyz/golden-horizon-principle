# PENTORA: an exact spherical research instrument

**Research note and proposed no-float contract — 30 October 2026.**

This folder contains a reproducible exact-arithmetic instrument for PENTORA's 110 spherical directions. Its central guarantee is finite and precise: for a declared spherical polynomial of degree at most five, the weighted sample norm equals the continuous normalized spherical norm exactly.

**Start with [SPEC.md](SPEC.md).** It defines the mathematics, exact field, wire format, resource caps, tail semantics, source assumptions, and adoption boundary. This is a research proposal, not a newly implemented X2 cell.

The companion [Riemann operator paper](../riemann-operator-bridge/README.md) contains the full Weil window certificate, prolate controls, compact-mesh comparison, and finite Cayley tests. Those analytic calculations are external to this exact polynomial profile.

## Findings that change the engineering plan

1. **Q(phi) alone is not enough for individual normalized samples.** The inner shells introduce sqrt(2) and sqrt(3). The oracle uses eight rational coefficients in Q(sqrt(2),sqrt(3),sqrt(5)); all arithmetic remains integer/Fraction arithmetic.
2. **The common weight denominator is 69300.** Per-point numerators are 800, 512, and 729 on the raw radius-squared 1, 2, and 3 shells. The rule remains exactly pinned to the canonical geometry.
3. **Use a 36-coordinate polynomial basis without orthonormal square roots.** Reduce z² to 1-x²-y². The result has 21 coefficients for A(x,y) and 15 for zB(x,y).
4. **An external tail remains unknown unless a separate proof adapter verifies it.** A nonnegative supplied bound is labelled asserted, not certified. The declared polynomial's zero tail says nothing about an outside PSWF or Weil minimizer.
5. **Exact spherical norm quadrature does not evaluate the Weil operator automatically.** Its image may contain higher modes even when the input is a low-degree polynomial. A measure-correct lift and an operator compression are different requirements.

## Executed checks

Run:

~~~bash
python3 test_reference.py
~~~

**RAN: 33 test groups passed, 0 failed.** The scripts require only Python's standard library. No NumPy, SciPy, floating square roots, zeta zeros, product builds, or Wasm execution enter these tests.

| Check | Result |
| --- | --- |
| Pinned geometry SHA-256 | Exact match |
| All 110 unit directions | Exact norm one in the radical field |
| All 364 moments through degree eleven | Exact match |
| Degree-twelve x^12 control | Exact failure 29/640640 |
| Zero, constant, x, mixed Q(phi), hidden-on-32 harmonic, dense 36-coefficient field | Analytic and sampled norms exactly equal |
| h=xyz(x²-y²) | Zero at the 32 dual directions; true and 110-point energy 4/3465 |
| Five-frame degree-25 H | Zero at all 110 points; exact nonzero raw probe at (1,2,3) |
| Viviani addresses | Exact sphere/cylinder identities, including a 256-bit n |
| Noncanonical fractions, floats, duplicate keys, geometry/dimension/basis mismatch | Refused |
| Negative or mislabeled tail claims | Refused; asserted positive bound remains unverified |
| Oversized integers, denominator-LCM growth, intermediate growth, arithmetic exhaustion | Refused |

The dense 36-coefficient case used fewer than 332000 logical arithmetic operations and produced less than 22000 canonical response bytes. Those are Python-oracle measurements, not a Wasm fuel benchmark. Exact timings and complete output values are in [results.json](results.json).

During implementation, a denominator-LCM preflight was added to make the bounded allocation contract explicit. The reference was rerun after that hardening, yielding the 33-group result above. This exploratory exercise was informed by the previous cubature report; it is not described as a blind preregistered discovery.

## Example

[example_frame.json](example_frame.json) is the exact frame for h=xyz(x²-y²). Its 110-point norm is 4/3465. A renderer may approximate its radical values for pixels, but the original exact values and their mathematical scope remain available.

To construct an input programmatically:

~~~python
import reference as p
coefficients = [p.Phi() for _ in p.BASIS]
coefficients[p.BASIS.index((3, 1, 1))] = p.Phi(1)
coefficients[p.BASIS.index((1, 3, 1))] = p.Phi(-1)
request = p.canonical_json(p.make_request(coefficients))
frame = p.evaluate_request(request)
assert frame['norm_squared'] == {'a': ['4', '3465'], 'b': ['0', '1']}
~~~

The stdin interface accepts one canonical inner request and returns one frame or an atomic refusal. It deliberately does not pretend to be the current X2 ABI dispatch.

## Scope and product boundary

The source review confirms X2's no-float meter constraint at main revision b2c7aaffc40694a94dc5f621421e728115cd8ae5. No source in that repository was modified. [SOURCE_REVIEW.md](SOURCE_REVIEW.md) records the exact inspected files.

This instrument has **zero product authority**. It does not authenticate a person, verify co-presence, strengthen an encryption primitive, prove a full analytic tail, or prove RH. Existing two-person pairing and optional witnesses are unchanged. The finite norm result is suitable for a precisely labelled research display and verifier.

## Files

| File | Purpose |
| --- | --- |
| SPEC.md | Full proposed exact research contract |
| reference.py | Standard-library exact evaluator and request verifier |
| test_reference.py | Meaningful exact identities and refusal controls |
| results.json | Recorded executed test results |
| example_frame.json | Exact 110-point frame for the dual-32 invisible harmonic |
| PLAN.md | Scope frozen before the new reference run |
| SOURCE_REVIEW.md | Current X2 source evidence and limitations |
| data/geometry_index_table_v1.json | Unmodified pinned geometry bytes |

## References

- Canonical geometry: [X2 pinned geometry](https://github.com/aumara-xyz/aukora-x2/blob/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/pentora/vectors/geometry_index_table_v1.json).
- Related classical 32-point cubature: Borodachov et al., [arXiv:2403.07457, Example 2.5](https://arxiv.org/pdf/2403.07457).
- The 110-point rule and its scope were established in the prior PENTORA–Viviani report and rechecked here. No publication-priority or optimality claim is made.

Geometry provenance and its original AGPL-3.0-or-later project context are retained. A production port must comply with the source project's license and adoption process.
