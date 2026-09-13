# D18 — the center observer: what the interference pattern of all rays can and cannot know (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Exact linear algebra over GF(3) and over the rationals; d18_results.log. Applies to the lab's 27-cell ternary observer code (OBSERVER-CODE.md, 54-trit code) and its 3⁴ extension; nothing here is about RH. MEASURED (exact, finite).

## T1 — how many viewing directions until the cube is known
| directions the center sees | line sums | rank | ghosts (undetectable coordinated changes) |
|---|---|---|---|
| 3 axes (the lab's 54-code) | 27 | 19 | 8 dimensions = 6561 cubes per pattern |
| 3 axes + 6 face diagonals | 81 | 27 | **0** — the pattern determines the cube |
| all 13 lattice directions | 109 | 27 | 0 |
Same ranks over the rationals. Prediction "≤ 2 ghosts with face diagonals" HELD (0); "0 with 13" HELD.
## T2 — how coordinated an invisible change must be (3-axis observer)
All 3⁸ ghosts enumerated. Minimum weight 8: a 2×2×2 alternating-sign block on the corners (54 such ghosts); weight histogram {8: 54, 12: 162, 14: 540, 15: 216, 17: 1728, 18: 1266, 20: 1944, 21: 540, 23: 108, 27: 2}. Prediction HELD. With face diagonals added there are no ghosts at all (prediction "≥ 12 or empty" HELD).
## T3 — one 4D observer versus four 3D observers
3⁴ cube with 4 axes: 108 sums, rank 65, 16 ghosts (19.8 % of cells). Four separate 27-cubes: 32 ghosts of 108 (29.6 %). One higher-dimensional observer sees more than four separate ones (HELD). Adding the 2-diagonal directions (16 directions total) already removes every ghost from the 3⁴ cube (prediction "≤ 40" HELD).
## T4 — what an honest single change looks like from the center
3 axes: one cell moves 3 sums (plus the retained source trit = the lab's "exactly 4 outputs"); two cells move 5–6. Thirteen directions: one cell moves 13 sums; two cells move 13–25 (prediction 13–26 HELD).

## Reading
1. The lab's intuition "consistency does not authenticate" has two separate causes, and only one is fixable. With three axes the observer is blind to an 8-dimensional ghost space, so a coordinated 8-cell change is invisible even without recomputing anything. Adding the six face-diagonal families makes the pattern a lossless encoding of the cube: every change, coordinated or not, moves at least 9 sums. That is a real, cheap upgrade to the observer code (81 sums instead of 27), and it is the mathematical content of "the observer is the interference pattern of all of them": with enough directions, the interference IS the object.
2. What remains unfixable by geometry: an adversary who replaces the cube and recomputes all 81 sums produces a valid pattern for a different cube. Injectivity means the pattern is the cube, not that the cube is the right one. Authentication still requires the verifier that recomputes a keyed digest, exactly as the lab states. The center observer can know WHAT is there; it cannot know WHETHER it should be.
3. Higher-dimensional observers are more efficient than more separate observers (19.8 % vs 29.6 % ghosts), and in 4D, 16 directions suffice for uniqueness. This is standard discrete tomography (uniqueness from enough lattice directions; switching components as the obstruction); nothing here is claimed new.
4. Suggested one-line record for the lab: "3-axis observer code: 8-dimensional GF(3) ghost space, minimum invisible change 8 cells; adding the 6 face-diagonal families gives an injective 81-sum code (no ghosts, minimum detectable change moves 9 sums); coordinated replacement remains undetectable without a keyed verifier."
