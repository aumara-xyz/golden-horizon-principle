# MIRROR-INERTIA-LEMMA v0 — results

For observer amplitudes indexed by a finite mirror-invariant set, the pairing is `Q_J(a)=<a,Ja>`.

| Check | Result | Status |
|---|---:|---|
| Configurations `(fixed,two-cycles)` checked | 80 | control grid |
| Maximum `||J^2-I||` | 0.0e+00 | MEASURED |
| Inertia formula `(+,0,-)=(f+p,0,p)` | True | MEASURED |
| Single-pair even observer | Q=1.0 | positive |
| Single-pair odd observer | Q=-1.0 | negative witness |
| Even-only restriction hides all negatives | True | MEASURED warning |
| Every two-cycle detected in odd sector | True | MEASURED |

## Exact block calculation

A mirror-fixed point contributes `[1]`. An off-center mirror pair contributes

```text
M = [[0, 1],
     [1, 0]].
```

Its normalized even and odd observer vectors are `(1,1)/sqrt(2)` and `(1,-1)/sqrt(2)`, with energies `+1` and `-1`. Therefore each off-center pair creates exactly one negative direction.

## Regularizer control

| Added `cI` | Minimum eigenvalue | PSD? |
|---:|---:|---|
| 0.5 | -0.5 | False |
| 1.0 | 0.0 | True |
| 1.5 | 0.5 | True |

## Prediction ledger

| Prediction | Outcome |
|---|---|
| Fixed point contributes one positive direction | MATCH |
| Two-cycle contributes one positive and one negative direction | MATCH |
| Even-only observers hide the negative direction | MATCH |
| `cI` masks negativity exactly at `c>=1` | MATCH |
| Prime-side infinite positivity remains unresolved | MATCH |

## Honest paragraph

This is the precise algebra behind the mirror picture. The critical line is the fixed set of `J(s)=1-conj(s)`: fixed zeros give positive square blocks, while every off-line mirror pair carries a mirror-odd negative direction. This does not prove RH, because the computation indexed hypothetical zero locations. Weil's criterion moves the same question to admissible test functions and the prime-side explicit formula. The remaining proof obligation is to show that the actual infinite prime-side form is nonnegative for every observer without assuming where the zeros are. Restricting observers to the even sector or adding a numerical diagonal shift can conceal the exact negative witness.

See `MIRROR_INERTIA_LEMMA.md` for the proof and scope.
