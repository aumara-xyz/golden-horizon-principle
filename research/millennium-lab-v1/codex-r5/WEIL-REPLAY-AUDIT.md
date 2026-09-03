# Codex R5 Weil reconstruction audit

Status: **MEASURED**. This replay used Connes--Consani--Moscovici, arXiv:2511.22755v1, equations (2.9)--(2.10), (4.2)--(4.4), (4.12)--(4.14), (5.5), and (5.25). It did not read any Fable R5 code and did not import target ordinates. The executable record is `outputs/weil-replay-audit.json`.

## Builder provenance

| artifact | SHA-256 | note |
|---|---|---|
| frozen pseudo-prime gate builder | `35add5e4b96f679ece19c27503ec4ea1f8c429c285f521179ec9b8eb3ca1d844` | committed pre-fix builder; frozen pseudo spectra retained; binary64 was adequate because these hostile matrices have order-one separated minima |
| audited exact-weight builder | `28aa0d44f7800f60316a3853db6fce1434ff495a04fff8595d6d0e9949f7f1ec` | recomputes `log(p)/sqrt(q)` at active precision and keeps the hypergeometric constant real |

The audit found two precision-path defects before the final reconstruction: the custom hypergeometric series initially returned an `mpc` with zero imaginary part, which broke the binary64 conversion, and true prime weights were initially serialized at 80 decimal digits, which capped a nominal 200/400-digit matrix. Both are fixed in the audited builder. The old blind-control artifacts and their builder hash were not overwritten.

## Formula replay

At 100 decimal digits, I built a full `(2N+1) x (2N+1)` matrix entry by entry for `N=8`, independently projected it onto orthonormal even/odd bases, and compared it with the structured builder. The archimedean and pole terms were also integrated directly. The transform was checked by direct Mellin integration, and the finite perturbed-scaling spectrum was checked against a high-precision companion matrix derived from (5.5).

| `lambda^2` | max archimedean formula/direct | max pole formula/direct | max complete entry formula/direct | max parity projection error | max (5.25)/direct transform | mp root/companion |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | `1.21e-100` | `1.79e-102` | `1.14e-100` | `1.96e-101` | `1.05e-101` | `4.53e-93` |
| 13 | `2.86e-101` | `3.57e-102` | `2.86e-101` | `2.86e-101` | `4.37e-102` | `2.40e-93` |
| 14 | `4.29e-101` | `5.71e-101` | `4.29e-101` | `2.86e-101` | `3.59e-102` | `7.89e-93` |

The full matrices were symmetric to at worst `1.8e-102` and exactly invariant under simultaneous index reflection. The binary64 root path agreed with the high-precision companion calculation to `1.3e-14`, `6.0e-14`, and `2.0e-13`; this is its intended precision floor, not a disagreement in the formulas. Recomputing a small matrix with active-precision prime weights agreed with a separately generated 225-digit prime comb to `4.43e-221`.

The smallest eigenvector was even in all three mutations. At `N=8`, the even/odd minima were respectively `3.00007e-23 / 1.60499e-20` for `lambda^2=12`, `7.67439e-23 / 3.91485e-20` for 13, and `1.46279e-23 / 6.73974e-21` for 14.

## Efficient N=120 high-precision solve

A full symmetric eigensolve at 130 working digits seeded Rayleigh inverse iteration at 230 and 430 digits. One guarded inverse step sufficed at each later precision; full eigenvalue-only solves independently validated the results.

| requested / working digits | even minimum | odd minimum | parity gap | eigen residual | refinement time |
|---:|---:|---:|---:|---:|---:|
| 100 / 130 | `3.48398819933127749919814493969e-59` | `3.05591339751516566896257925518e-55` | `3.05556499869523254121265944068e-55` | `1.36e-130` | `39.5 s` full seed |
| 200 / 230 | same leading digits | same leading digits | same leading digits | `4.31e-232` | `3.55 s` |
| 400 / 430 | same leading digits | same leading digits | same leading digits | `4.78e-433` | `5.19 s` |

The second even eigenvalue is `1.31185428456946836815892877103e-51`, so the nearest competitor is the odd minimum. The 230- and 430-digit Rayleigh values differed from full symmetric eigenvalue calculations by `8.18e-231` and `2.99e-431`. This makes continuation from the preceding precision substantially cheaper than repeating all eigenvectors.

## Exact 100/200/400-digit root repeat

For `N=120`, `lambda^2=13`, I independently repeated the matrix, lowest-vector, and first 60 positive-root computation at exactly 100, 200, and 400 working digits. Root indices, rather than height windows, fixed the selection. No external ordinate entered the construction or bracketing.

| comparison on frozen indices 20--50 | largest absolute difference | worst index |
|---|---:|---:|
| 100 vs 200 digits | `4.3931754983868613060e-49` | 49 |
| 200 vs 400 digits | `1.1135637206545281807e-149` | 49 |

At index 20 the two differences are `3.3040e-69` and `8.3351e-170`; at index 50 they are `2.7224e-49` and `6.9011e-150`. Thus adding 100 working digits adds approximately 100 stable digits to this comparison, while the loss of about 51 digits at the upper end is consistent with the `~3.06e-55` nearest-sector gap. Maximum transform residuals were `1.20e-101`, `1.72e-201`, and `1.64e-401`.

Against the root driver's separately recorded values at audit time, the largest discrepancies on indices 20--50 were `6.30e-49`, `7.21e-149`, and `1.74e-349` at 100, 200, and 400 digits, all at index 49. The 100-digit driver was subsequently rerun with the final builder so every primary driver artifact now carries the final hash; `outputs/weil-replay-final-driver-reconciliation.json` records that post-audit comparison. The first two comparisons sit at the forward-accuracy floor predicted by the gap; the 400-digit continuations converge much farther.

Provenance detail: `outputs/weil-replay-audit.json` is a historical snapshot
whose driver-comparison block retains the intermediate 100-digit artifact
hash `ad7266...` that existed at audit time. The primary 100-digit driver was
subsequently rerun and now, like the 200- and 400-digit files, carries final
builder SHA-256 `28aa0d...`. The audit's own 100/200/400 sequence used the
final builder throughout; `outputs/weil-replay-final-driver-reconciliation.json`
records the current primary-file comparison.

## Residual issue

**MEASURED:** the unused `refine_positive_roots` helper is not bracket-preserving; in a 60-root replay its unguarded secant steps sent two adjacent seeds to the same root. The production reconstruction uses `enumerate_positive_roots_mp`, whose secant step is checked against a sign bracket and falls back to bisection, so this did not affect any recorded reconstruction. The unused helper should be removed or given the same guard.

Conclusion: **MEASURED** agreement supports the finite-matrix and perturbed-scaling implementation, including its parity reduction and high-precision continuation. It does not verify the paper's asymptotic bridge from the prolate candidate to the true Weil ground state; that claim remains **UNVERIFIED**.
