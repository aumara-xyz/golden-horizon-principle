# D19 — the critical exponent emerges from the window (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Floating numpy (D17 mutation n^{−σ}), bisection to 22 steps, search range σ ∈ [0.3, 0.7] (an edge reported as 0.300000 or 0.700000 means "beyond the search range", not a measured boundary). d19_results.log/json; figure d19_emergent_line.png. Labeled mutation; the σ ≠ 0.5 forms are not L-functions. MEASURED (floating).

## Allowed exponent intervals per parity, and their intersection
| form, L | even sector allows σ ∈ | odd sector allows σ ∈ | joint width | joint midpoint − 0.5 |
|---|---|---|---|---|
| ζ 0.30 | [<0.3, >0.7] | [<0.3, >0.7] | > 0.4 | 0 (unresolved) |
| ζ 0.35 | [<0.3, >0.7] | [<0.3, >0.7] | > 0.4 | 0 (unresolved) |
| ζ 0.40 | [0.4423, >0.7] | [<0.3, >0.7] | 0.258 | +0.071 |
| ζ 0.45 | [0.4979, >0.7] | [<0.3, 0.5230] | 2.5e-2 | +1.0e-2 |
| ζ 0.50 | [0.49992, 0.5295] | [<0.3, 0.50130] | 1.4e-3 | +6.1e-4 |
| ζ 0.55 | [0.499998, 0.5016] | [0.4297, 0.500058] | 6.0e-5 | +2.8e-5 |
| ζ 0.60 | [0.5000000, 0.500089] | [0.4915, 0.500002] | 1.9e-6 | +9.3e-7 |
| χ₋₄ 0.50 | [<0.3, >0.7] | [<0.3, >0.7] | > 0.4 | 0 (unresolved) |
| χ₋₄ 0.70 | [<0.3, 0.5765] | [<0.3, >0.7] | 0.276 | −0.062 |
| χ₋₄ 0.90 | [0.3703, 0.500137] | [0.4890, >0.7] | 1.1e-2 | −5.4e-3 |
| χ₋₄ 1.00 | [0.4848, 0.500003] | [0.49948, >0.7] | 5.2e-4 | −2.6e-4 |

## Reading
1. A small room does not know the exponent: for ζ below L ≈ 0.35 every σ in [0.3, 0.7] keeps both parities positive. The window carries no information about the critical line until the first prime fits.
2. The two parity sectors are a floor and a ceiling. For ζ the even sector forbids σ below 0.5 and the odd sector forbids σ above 0.5; for the odd character χ₋₄ the roles are swapped (even is the ceiling, odd the floor). In every case the two one-sided constraints close in on 0.5 from opposite sides, and the joint band collapses exponentially: width 0.26 → 2.5e-2 → 1.4e-3 → 6e-5 → 1.9e-6 for ζ from L = 0.40 to 0.60 (about a factor 30 per 0.05 in L), and 0.28 → 1.1e-2 → 5.2e-4 for χ₋₄ from 0.7 to 1.0.
3. The band is not centered on 0.5 while it is wide (midpoint offset +0.071 at ζ L = 0.40, i.e. 28 % of the width; −0.062 for χ₋₄ at 0.70) and its midpoint converges to 0.5 as it narrows (offset +9e-7 at L = 0.60). The critical exponent is not visible in any single finite room; it is the limit point of the rooms. Because the two edges belong to different parity sectors, "why 1/2" in this finite picture is "the only exponent the even and odd sectors can both live with as the room grows," a finite shadow of the functional equation's symmetry point.
4. Nothing here proves anything about zeros; the mutated forms are not L-functions. It is a measurement of how the finite method encodes the symmetry point, and it completes the D12–D17 map: every arithmetic ingredient, including the exponent, is pinned by the window only in the large-room limit, exponentially fast, from both sides.

## Prediction ledger
| prediction | outcome |
|---|---|
| (1) both parity intervals contain 0.5 at every L | HELD |
| (2) joint width shrinks monotonically, > 0.05 at L = 0.30, < 1e-6 at L = 0.60 | HELD except the last number: 1.86e-6 at 0.60 (FAILED narrowly) |
| (3) midpoint off 0.5 by > 10 % of width at small L, converging to 0.5 | HELD (28 % at L = 0.40; 9e-7 at 0.60) |
| (4) χ₋₄ parity intervals on opposite sides of 0.5, intersection a shrinking neighborhood | HELD (sides swapped relative to ζ, as the character is odd) |

## D19b — susceptibility to the exponent (appended; predictions in PREDICTIONS.md §D19b; d19b_susceptibility.log/json)
| form, L | even: margin, dλ/dσ | odd: margin, dλ/dσ |
|---|---|---|
| ζ 0.40 | 1.5e-4, +2.3e-3 | 1.3e-2, −4.5e-2 |
| ζ 0.50 | 7.3e-7, +8.9e-3 | 1.5e-4, −1.1e-1 |
| ζ 0.60 | 7.6e-10, +3.2e-2 | 2.8e-7, −1.5e-1 |
| χ₋₄ 0.70 | 6.1e-3, −8.0e-2 | 3.3e-1, +5.7e-1 |
| χ₋₄ 1.00 | 5.0e-7, −1.5e-1 | 2.6e-4, +5.0e-1 |
Signs: ζ even dλ/dσ > 0 (heavier primes, σ < ½, hurt), odd < 0 (heavier primes help); reversed for the odd character. HELD. Magnitudes: while the ζ margins fall by six (even) and five (odd) orders, |dλ/dσ| RISES from 2.3e-3 to 3.2e-2 (even) and from 0.045 to 0.15 (odd); for χ₋₄ it is flat at 0.08–0.15 (even) and 0.5–0.57 (odd). The band half-width is margin/|dλ/dσ| to within the bisection accuracy. So the exponent sensitivity is a second, independent, slowly varying quantity; the band collapse in D19 is entirely the collapse of the margin. Prediction HELD; kill (three-order drop) not triggered. In the finite-size-scaling analogy: the "susceptibility" does not diverge or vanish; the transition-like collapse is carried by the gap alone. Reading: the exponent is not what the room is sensitive to; the room is sensitive to positivity itself, and the exponent inherits that sensitivity. No RH content.
