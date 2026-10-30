# PENTORA exact spherical research instrument

**Version:** 1-proposal, 30 October 2026.  
**Status:** research contract and executed Python specification oracle. Not an implemented Rust/Wasm operation.  
**Authority:** none. Two people remain sufficient for ordinary pairing; a third witness remains optional.

## 1. Purpose and established result

The instrument evaluates a declared spherical polynomial, reports its exact mean-square norm, and records what is unknown about any larger external field. It is designed to fit X2's integer-only computation boundary without silently approximating algebraic coordinates.

For the pinned 110 noncentral directions, with normalized spherical area dmu=dOmega/(4*pi), the weights satisfy

$$
\int_{S^2}P\,d\mu=\sum_{i=1}^{110}w_iP(n_i)
$$

for every polynomial of degree at most eleven. Hence, for every real spherical polynomial f of degree at most five,

$$
\|f\|_{L^2(S^2,d\mu)}^2=\sum_iw_i f(n_i)^2.
$$

The mathematical theorem permits arbitrary real coefficients. This finite wire profile accepts exactly representable coefficients in Q(phi); unsupported real or algebraic values must not be rounded while retaining an exact label. A declared rational approximation is a different mathematical object and needs a separate error statement if it represents an external wave.

## 2. Current X2 source, independently read

The inspected main head is **b2c7aaffc40694a94dc5f621421e728115cd8ae5**. The current files establish:

| File | Source fact |
| --- | --- |
| cells/pentora/src/lib.rs | Strict canonical request handling; pinned geometry; integer state expansion; the current four operations are geometry, expand, snapshot, observe. |
| cells/pentora/README.md | Observer-only scope; no installed-app claim; no-float build requirement. |
| cells/pentora/build.mjs | Rust to wasm32 build, SHA-pinned meter, export stripping, recorded byte/fuel limits. |
| cells/aperture/meter.mjs | Rejects floating-point value types and opcodes, imports, and unsupported instructions. Accepted variable-cost memory operations are charged; they are not all categorically rejected. |

The meter SHA-256 pinned by the build is **0c8fcc36550a6c379317780f3f063cdbb04ce514fd64a43dc3a9a8781dfd2714**. The source review did not build or execute that Wasm binary. The new research operations described here do not exist in the inspected decision dispatch.

Pinned source URLs and Git blob identifiers are in SOURCE_REVIEW.md. The current integer-only constraint is preserved, but this proposal still needs a Rust port, metered build, independent Wasm vectors, and adoption before integration.

## 3. Geometry and measure

The accepted geometry bytes have SHA-256:

~~~text
96b27c9b4de41cd961612be5b1e88d40e973a2fded16bd320415b3e15e3b8c61
~~~

Index 55 is the fixed center and is not projected. All other indices retain their existing order. The raw Q(phi) coordinate triples have squared radii 1, 2, and 3. The product's common display scaling by 1/sqrt(3) does not change radial directions; this instrument normalizes each raw point by its own length.

| Raw squared radius | Points | Per-point weight | Integer numerator at denominator 69300 |
| --- | ---: | ---: | ---: |
| 1 | 30 | 8/693 | 800 |
| 2 | 60 | 128/17325 | 512 |
| 3 | 20 | 81/7700 | 729 |

The integer check is 30*800+60*512+20*729=69300. All calculations use the probability measure dOmega/(4*pi), not unnormalized surface area. A renderer must display the measure whenever it reports a norm.

The cubature rule is a degree-eleven weighted rule. Equal weights are not a compatible optimization. It fails at x^12 by exactly 29/640640. Its norm guarantee is degree five, not degree eleven.

## 4. Exact algebraic representation: Q(phi) alone is insufficient

The raw geometry belongs to Q(phi), but normalizing the inner shells introduces sqrt(2) and sqrt(3). For example, a normalized raw coordinate 1 on the radius-squared-two shell becomes 1/sqrt(2), which is not in Q(phi).

Use the fixed field

$$
K=\mathbb Q(\sqrt2,\sqrt3,\sqrt5)
$$

with eight rational coefficients in the ordered basis

~~~text
[1, sqrt(2), sqrt(3), sqrt(6), sqrt(5), sqrt(10), sqrt(15), sqrt(30)]
~~~

These are symbolic basis elements, not evaluated floating numbers. A coefficient index is a three-bit mask selecting sqrt(2), sqrt(3), sqrt(5). Multiplication XORs the masks and multiplies by 2, 3, or 5 for every repeated bit. This reduces every product exactly to the same eight slots.

Embed a+b*phi as

$$
(a+b/2)+(b/2)\sqrt5.
$$

The normalization factors are 1, sqrt(2)/2, and sqrt(3)/3. Every normalized direction and every accepted polynomial sample therefore lies in K. The integrated norm for Q(phi) polynomial coefficients lies in Q(phi); the other radical coefficients must cancel exactly in the weighted sample norm. A nonzero forbidden radical component is an invariant failure.

A Q(phi)-only implementation can keep symbolic shell factors and parity-separated evaluation instead. That is another encoding of the same missing radicals, not permission to discard them. The explicit eight-slot field is selected here because it gives a simple, auditable closure rule.

This field is scoped to the 110 canonical directions. Normalizing the twelve dual icosahedral points can require sqrt(phi+2), which is not asserted to lie in K. Their homogeneous zero-control is proved using raw coordinates, so the reference does not silently extend its runtime field. Generic probe directions such as (1,2,3)/sqrt(14) likewise need additional radicals; the degree-25 control uses homogeneity instead of pretending that probe is in K.

## 5. A canonical 36-coordinate polynomial basis

Use the sphere relation z²=1-x²-y² to reduce every degree-five polynomial to

$$
f(x,y,z)=A(x,y)+zB(x,y),\qquad\deg A\le5,\quad\deg B\le4.
$$

There are 21 coefficients for A and 15 for B, giving 36 real degrees of freedom. This is the full spherical space H_5, without square-root normalizations from an orthonormal harmonic basis.

The wire basis is **sphere-z-reduced-degree5-v1**. Order monomials by total degree d=0,...,5; within d, list z exponent k=0 then k=1 when allowed; within k, list x exponent i from 0 to d-k, with y exponent j=d-k-i. The basis is fully specified by

~~~python
[(i, d-k-i, k)
 for d in range(6)
 for k in (0, 1) if k <= d
 for i in range(d-k+1)]
~~~

The numbers per total-degree shell are 1,3,5,7,9,11. This representation is unique on the sphere. If A+zB vanishes on the whole sphere, comparing the positive and negative z branches over the open unit disk shows A=B=0 there, hence as polynomials.

An axisymmetric lift of a one-dimensional polynomial of degree at most five occupies **six dimensions**, a subspace of H_5. It must not be reported as 36 independently tested one-dimensional modes.

### Exact analytic norm

Compute the norm by polynomial multiplication and exact spherical moments:

$$
\int x^{2a}y^{2b}z^{2c}\,d\mu
=\frac{(2a-1)!!(2b-1)!!(2c-1)!!}{(2a+2b+2c+1)!!};
$$

any odd exponent gives zero. Independently evaluate all 110 samples and their weighted squares. The two answers must agree exactly. This checks the declared polynomial and the rule, not an external field's accuracy.

Complex fields can be handled by separate real and imaginary polynomials and the sum of their squared norms. That extension is not part of the executed single-real-field v1 request schema; a future profile must state its doubled resource bounds and exact bytes.

## 6. Canonical rational and integer wire formats

A rational number is an array of two decimal strings:

~~~json
["-7","12"]
~~~

Requirements:

- Numerator uses exactly 0 or a minus sign followed by nonzero-leading digits, or positive nonzero-leading digits.
- Denominator is strictly positive, with no leading zero.
- Numerator and denominator are relatively prime.
- Zero is exactly ["0","1"]. Negative zero, a plus sign, decimal notation, exponent notation, and JSON floating numbers are refused.
- Big integers are strings so JavaScript does not silently round them through a binary64 number.
- Coefficients use Q(phi) objects with exactly the keys a and b, each containing one canonical rational.
- A K sample is an array of exactly eight canonical rationals in the basis order of §4, including explicit zeros.

A future Rust implementation may use signed-magnitude u32 limbs internally, with a unique zero sign and no leading zero limbs. Internal limb encoding is not a second permitted wire encoding. The canonical mathematical bytes remain the decimal-string representation.

The selected research JSON uses sorted ASCII keys, no whitespace, no duplicate keys, and no trailing newline in requests. All profile-controlled strings are ASCII. The reference refuses noncanonical bytes before evaluation. A Wasm adapter must use the repository's canonical encoder and test byte equality, rather than assume a generic JSON library is equivalent for unrestricted Unicode or control characters.

## 7. Bounded resources and fail-closed behavior

These are proposed research-profile caps, not measurements of the cost of a completed Rust port:

| Quantity | Cap |
| --- | ---: |
| Request bytes | 65536 |
| Response bytes | 262144 |
| Polynomial coefficients | Exactly 36 Q(phi) values |
| Bits per input numerator/denominator | 256 |
| Bits in the least common multiple of all input coefficient denominators | 1024 |
| Bits per reduced intermediate numerator/denominator | 4096 |
| Rational field-operation counter in Python oracle | 20000000 |
| Viviani integer n | 1 through 2^256-1 |

The denominator-LCM preflight prevents individually small denominators from creating an uncontrolled common denominator. The implementation must still check every intermediate and output length. Overflow, excessive denominator growth, exhausted budget, and output overflow refuse the whole request. No approximate fallback, truncation, wraparound, or partial success is permitted.

The Python counter is a reproducible logical operation bound. It is not equivalent to X2's Wasm instruction fuel. A Rust port must have bounded allocation, charge integer/GCD work through the adopted meter, run the negative vectors after compilation, and obtain a new reviewed pin. The current cell's 400-million fuel setting must not be declared sufficient merely because the Python tests completed.

Fraction operations in the oracle use bounded operands and check reduced intermediates. The Rust design should allow a bounded scratch product before reduction, account for that scratch space, and refuse before any unbounded allocation. Worst-case input vectors must be tested at the chosen bit and byte caps.

## 8. Request and result contract

The reference accepts an inner research request with exactly these fields:

~~~text
profile
geometry_sha256
basis
coefficients
target_kind
tail
source_digest
~~~

The profile is **pentora.research.sphere.exact.v1-proposal**. An eventual X2 ABI wrapper would bind an adopted operation name, sequence, and this exact input under the existing ABI. That wrapper is not implemented here, and the proposed profile name must not be added to production dispatch without the normal code review.

The output includes the exact norm from moments, the exact norm from weighted samples, all 110 indexed K values, geometry pin, basis/version/measure, input digest, source label, tail status, and explicit authority limits. The digest domain is

~~~text
pentora.research.sphere.v1\0
~~~

followed by the canonical input bytes. This commits the input; it does not authenticate its origin. A supplied source digest is reported with source_authenticated=false.

The selected sample indices are every canonical global index except 55. The center does not acquire a direction, weight, missing-data status, or implicit zero sample.

## 9. Tail semantics and allowed conclusions

### Declared polynomial

When target_kind is **declared-polynomial**, the mathematical object is exactly the 36 supplied coefficients. Its tail is **zero-for-declared-polynomial**. The output certifies the norm of that declared object. It does not establish that an outside PSWF, Weil minimizer, message, or physical field equals those coefficients.

### External projection

When target_kind is **external-projection**, the represented coefficients are claimed to approximate or project an external object. The default tail is **unknown**.

A nonnegative rational **asserted-upper-bound** may be displayed with an evidence digest, but this profile adds the status **not-verified-by-this-profile**. Negative bounds are refused. Merely attaching a digest does not promote an assertion to an interval proof.

This v1 profile has no general analytic-tail proof adapter. It therefore always emits full_external_norm_certified=false and Weil_energy_computed=false. If a later adapter verifies a tail theorem, it must bind the function, measure, norm, bandwidth, exact coefficient construction, parameter ranges, source/certificate version, and all error terms. A bound for L² mass is not a bound for the Weil quadratic form.

An alleged exact projection is itself a claim about the outside field. Orthogonality and Pythagoras cannot be assumed merely because the field was passed through a least-squares fit.

## 10. Rational Viviani event addresses

The address operation accepts a canonical positive integer n and returns

$$
\left(\frac{(n^2-1)^2}{(n^2+1)^2},
-\frac{2n(n^2-1)}{(n^2+1)^2},
\frac{2n}{n^2+1}\right).
$$

The reference reduces each rational and checks exactly that x²+y²+z²=1 and x²+y²=x. It does not compute logarithms, trigonometric functions, floating square roots, primality, or a proof that n is a prime power. The result labels the parameter as t=log(n), not numerically evaluated, and primality_checked=false.

This makes prime-power event positions exact once a separate arithmetic producer identifies the relevant n. A producer claiming prime-power eligibility must provide its own verified p,k and primality evidence under a named profile. The address alone is not that evidence.

Every finite accepted n is retained beside the rendered point. Pixel coincidence near the node must not merge event IDs or imply equal mathematical coordinates. Infinity is a symbolic limit marker, not a valid n input, a numeric overflow value, or a finite event at the center. The node is (1,0,0), on the sphere.

## 11. Mandatory adversarial mathematical controls

### The dual 32-point blind spot

The polynomial h=xyz(x²-y²) has degree five, is harmonic, and is zero on all 20 dodecahedral plus 12 dual icosahedral directions. Its true squared norm is 4/3465. The verifier checks its zeros using raw homogeneous coordinates, then checks the exact energy from spherical moments. The 110-point rule must return 4/3465 for the same polynomial.

### The 110-point blind spot

Let (u_a,v_a,w_a) be coordinates in cube frame a. The degree-25 polynomial

$$
H(n)=\prod_{a=1}^5u_av_aw_a(u_a^2-v_a^2)
$$

vanishes at all 110 directions. Its raw value at (1,2,3) is

$$
\frac{55071306675}{262144}
+\frac{244124503425}{524288}\phi,
$$

which is nonzero. Homogeneity proves a nonzero value at the corresponding unit direction without expanding the runtime field to include sqrt(7).

The degree-five coefficient profile must refuse an attempted degree-25 basis. If a zero coefficient vector is advertised as an external projection of H, its residual stays unknown. The zero sample vector cannot certify that the external field is zero.

### Other required controls

- Exact x^12 mismatch 29/640640, retained as a failure beyond the cubature range.
- Geometry hash mismatch, altered index order, or center normalization.
- Noncanonical, unreduced, negative-denominator, oversized, and floating inputs.
- Denominator-LCM growth and arithmetic exhaustion.
- Claimed authority fields, unknown fields, wrong coefficient count, and unsupported basis.
- Negative residual bounds and an external field claiming the declared-polynomial zero-tail status.
- A 32-direction implementation incorrectly substituted for the 110-direction operation.

The executed tests cover the listed mathematical identities and the implemented schema/resource refusals. They are not a complete Rust/Wasm or UI conformance suite; that distinction must remain in the test report.

## 12. What a measure-correct operator lift does and does not supply

For a fixed unit axis a, define

$$
(Uf)(n)=\sqrt{2L}\,f(L\,a\cdot n).
$$

With the stated measures, this preserves the norm from L²([-L,L],dx) to the axisymmetric subspace of L²(S²,dmu). A degree-five one-dimensional polynomial maps to a six-dimensional part of H_5. Exact runtime representation additionally depends on the coefficients and axis belonging to the selected field; unsupported algebraic axes or irrational coefficients require another explicit profile or certified approximation.

This does not make the complete Weil operator a polynomial. Even if f is low degree, Qf may have arbitrarily high angular content after the lift. The product (Uf)*(UQf) therefore need not lie in the degree-eleven cubature class. To compute or rigorously enclose the finite block A, an implementation needs an independently derived operator matrix and coefficient error bounds, or an explicitly justified projected operator, not just exact norm quadrature. General Weil matrix entries are analytic interval or symbolic data; this exact polynomial profile does not accept them as exact Q(phi) coefficients.

The coefficient wire domain is Q(phi), while K is the sample-value field. An orthonormal lifted Legendre basis introduces sqrt(2k+1), which need not be accepted as a coefficient even when it belongs to K. Unnormalized P_k(z), with the correct Gram matrix retained, avoids that unnecessary coefficient-field extension.

## 13. Display and authority rules

The renderer may convert exact values to floats for pixels outside the no-float research organ. It must retain the exact source values and report that rendering is approximate. The rendered scene must state degree five, normalized spherical measure, and tail status. Unknown or asserted tails must remain visible.

A refusal must not be displayed as a fresh success using a previous frame. Research sample values are not fingerprint trits, health predicates, identity decisions, signature checks, co-presence evidence, or authorization. No field in this profile can enable an effect or upgrade a product permission.

The no-float cell verifies an algebraic object. The numerical research lab evaluates functions and operator estimates. The renderer displays a chosen approximation. Those responsibilities have explicit data contracts; none inherits authority from the others.

## 14. Adoption checklist

1. Review and freeze the exact field, polynomial basis, profile, limits, and byte vectors.
2. Port the oracle into bounded integer Rust code without floating conversions.
3. Compile and run the metered Wasm acceptance and refusal vectors.
4. Independently verify the geometry and finite norm identities.
5. Test fuel exhaustion, maximal inputs, output limits, and atomic refusal.
6. Test renderer state transitions, exact-value inspection, and unknown-tail presentation.
7. Adopt a new versioned operation only after those checks; do not edit existing fingerprint or pairing derivations.

This proposal establishes an exact finite research instrument. It adds no RH proof, universal tail theorem, authentication primitive, or new product authority.
