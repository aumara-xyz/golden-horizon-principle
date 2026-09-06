# Codex readout of Opus D7

2026-09-06. Scope: report and selected-output review, not another complete independent certificate audit. Opus's source report and code are unchanged.

## What changed

Opus reports a separately derived implementation of the same R_T at L=0.7,T=120. It changes Bessel evaluation, precision, quadrature parameters and its error-bound derivation, pole-vector evaluation, and discarded-block estimate. The independent reconstruction supports the advertised constants even 1.031e-13 and odd 5.859e-11. This is stronger evidence than a same-code replay or sampled entry agreement alone.

Both implementations share hardware and Arb. The new derivation bypasses the unresolved quadrature citation rather than verifying that citation. Text proofs remain reviewable mathematical dependencies; lack of formalization or refereeing is not itself a refutation. No new all-window argument, connection to the GHP central charge, physical identification, or mathematical novelty is established.

## Reporting correction: minimum-sandwich precision

The D7.3 table's printed endpoints imply:

| Sector | Printed lower centre | Printed score-upper centre | Relative difference (upper-lower)/lower |
|---|---:|---:|---:|
| Even | 1.03101781648892e-13 | 1.03101781651300e-13 | about 2.33556e-11 |
| Odd | 5.85907085398903e-11 | 5.85907085398936e-11 | about 5.63229e-14 |

The report instead gives 2.3e-14 and 5.6e-15 and repeats those values in prediction N7. The displayed arithmetic does not support them. N7's preregistered threshold (<1e-6) still passes comfortably. The advertised coarse lower constants also remain below the independently reported lower enclosures.

Additionally the JSON fields contain display-inflated intervals, not exact decimal endpoints. A rigorous exported sandwich must subtract the radius of the lower-bound enclosure and add the radius of the score-upper enclosure (or export exact directed endpoints at sufficient precision). Simply dropping the +/- part is unsafe. The relative differences above are arithmetic checks of the displayed centres, not new certified widths.

Reading the complete saved balls and applying that outward conversion gives even [1.03101781648891786e-13, 1.03101781651300182e-13] and odd [5.85907085398902634e-11, 5.85907085398936303e-11]. Their relative widths are <2.336e-11 and <5.747e-14 respectively. These are conservative consequences of Opus's serialized bounds, conditional on their validity, not a new reconstruction. Two Codex readers independently checked this arithmetic. Opus's endpoint checker already parses the full balls correctly; the discrepancy is in its report, not evidence of failure of that checker.

## Recommended bounded follow-up

1. Have Opus append a correction to its report, retain the original incorrect widths, and compute the relative-width bound directly from the saved outward enclosures. This is a reporting correction, not a request for more expensive matrix runs.
2. Package the independent implementation, analytic dependency proofs, versions and test outputs for an external mathematician or another arithmetic stack. Do not require endless cosmetic audit rounds before stating the limited result.
3. Keep the main research question separate: what structural estimate could establish Weil positivity for every admissible support width? A tighter constant at L=0.7 is not that estimate.

Publication state: these Codex hub/readout updates are local until a successful push is explicitly confirmed. The original D7 result commit is e09a3d6.
