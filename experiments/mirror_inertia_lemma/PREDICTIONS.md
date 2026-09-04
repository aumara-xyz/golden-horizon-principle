# MIRROR-INERTIA-LEMMA v0 — preregistration

- Date locked: 2026-09-04
- Purpose: isolate the exact finite-dimensional algebra behind “the middle of the mirror.”
- This is a lemma/model of the spectral Weil pairing, not a proof of RH.

## Frozen construction

Let a finite index set be invariant under a mirror involution `J`. Each index is either a
fixed point (`Jz=z`, modeling a zero on the critical line) or belongs to a two-cycle
`z <-> Jz` (modeling an off-line mirror pair). On observer amplitudes `a`, define

`Q_J(a) = <a, J a>`.

In the index basis, `J` has a `[1]` block for every fixed point and a swap block

`[[0,1],[1,0]]`

for every two-cycle. Test configurations with 0 through 8 fixed points and 0 through 8
two-cycles. Compute Hermitian inertia and explicitly test the mirror-even and mirror-odd
observer vectors. Controls: restrict observers to the even sector, and add a positive
regularizer `c I` for `c in {0.5,1,1.5}`.

## Predictions

1. **PREDICTED:** each fixed point contributes one positive eigenvalue.
2. **PREDICTED:** each off-line two-cycle contributes one positive and one negative
   eigenvalue; therefore `Q_J >= 0` on all observer amplitudes if and only if every index
   is mirror-fixed.
3. **PREDICTED:** restricting to mirror-even observers hides every negative direction.
   This demonstrates why positivity must hold for all admissible test functions.
4. **PREDICTED:** adding `cI` masks the negative direction exactly when `c>=1`; a finite
   numerical regularization can therefore create false positivity.
5. **PREDICTED:** the finite algebra will be exact. The unresolved step is proving the
   corresponding prime-side Weil quadratic form positive on the full infinite test-function
   space without using the zeros or assuming RH.
