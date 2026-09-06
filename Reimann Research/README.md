# Riemann research — central hub

Folder named `Reimann Research` as requested. Updated 2026-09-06.

This is the single entry point for the recent Riemann-related work in Golden Horizon Principle. Original experiment files remain in place to preserve executable paths, provenance, and collaborators' working files. Links below lead to the canonical files, not duplicate snapshots. This is an organizational index, not a claim that every linked experiment has passed an independent audit.

## Start here

1. [Current status, the two 0.7s, and your friend's contribution](../experiments/prime_gears_codex/STATUS-AND-CONTRIBUTIONS.md)
2. [Latest independent implementation audit: Opus D7](../experiments/weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md) · [Codex scope/readout note](D7-READOUT.md)
3. [Codex gear / prime-coordinate / ternary toy results](../experiments/prime_gears_codex/RESULTS.md)
4. [Completed round's directive: Opus D7 independent audit](NEXT-ROUND-D7.md)

**Status:** Opus D7 reports a separate derivation and implementation supporting Fable's compact-window positivity at L=0.7, both parity sectors. The two implementations share a machine and Arb build. Codex has reviewed the report and selected outputs, not independently replayed the full certificate; its readout note corrects overstated sandwich precision in D7. Analytic proof review and cross-stack validation remain outstanding. No RH proof, new all-window positivity argument, physical hologram result, or novelty claim has been established. GHP's c=0.7 central charge and the chosen L=0.7 cutoff are different quantities with no established bridge.

## Certificate and audit track

| Stage | Canonical report | Predictions / implementation |
|---|---|---|
| Initial finite Weil forms | [Results](../experiments/weil_hidden_modes/RESULTS.md), [Interpretation](../experiments/weil_hidden_modes/INTERPRETATION.md) | [Predictions](../experiments/weil_hidden_modes/PREDICTIONS.md), [all source and data](../experiments/weil_hidden_modes/) |
| Higher precision | [Results](../experiments/weil_hidden_modes/RESULTS-high-precision.md) | [Predictions](../experiments/weil_hidden_modes/PREDICTIONS-high-precision.md) |
| Codex finite certificate | [Certificate](../experiments/weil_hidden_modes/CERTIFICATE.md) | [Predictions](../experiments/weil_hidden_modes/PREDICTIONS-certified.md) |
| Infinite pure tail / parity | [Results](../experiments/weil_hidden_modes/RESULTS-parity-tail.md), [Pure-tail lemma](../experiments/weil_hidden_modes/PURE-TAIL-LEMMA.md) | [Predictions](../experiments/weil_hidden_modes/PREDICTIONS-parity-tail.md) |
| Fable audit and D4 | [Audit, including withdrawals](../experiments/weil_hidden_modes/FABLE-AUDIT.md) | [Audit predictions](../experiments/weil_hidden_modes/FABLE-PREDICTIONS-audit.md), [D4 predictions](../experiments/weil_hidden_modes/FABLE-PREDICTIONS-D4.md) |
| D5 odd sector / unitary dilation | [D5 results](../experiments/weil_hidden_modes/FABLE-ROUND-D5-RESULTS.md) | [Predictions](../experiments/weil_hidden_modes/FABLE-PREDICTIONS-D5.md) |
| D6 analytic and endpoint corrections | [D6 results](../experiments/weil_hidden_modes/FABLE-ROUND-D6-RESULTS.md) | [Predictions](../experiments/weil_hidden_modes/FABLE-PREDICTIONS-D6.md) |
| D7 independent reconstruction and checker attacks | [Opus D7 results](../experiments/weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md), [Codex readout](D7-READOUT.md) | [Predictions](../experiments/weil_hidden_modes/OPUS-PREDICTIONS-D7.md), [independent implementation](../experiments/weil_hidden_modes/opus_d7_rebuild.py) |

Read chronologically when reconstructing a claim: earlier claims were corrected or withdrawn, not deleted. D6 supersedes D5's upward-rounded odd constant and false pointwise complex-function identity.

## Mirror, geometry, and controlled toy track

Each experiment directory contains its available code, raw outputs, and predictions; a link does not certify the interpretation.

- [Prime gears: results](../experiments/prime_gears_codex/RESULTS.md) · [code and data](../experiments/prime_gears_codex/) · [figure](../experiments/prime_gears_codex/prime-gears.png)
- [Lee–Yang bridge](../experiments/lee_yang_bridge/RESULTS.md) · [directory](../experiments/lee_yang_bridge/)
- [Mirror inertia lemma](../experiments/mirror_inertia_lemma/MIRROR_INERTIA_LEMMA.md) · [results](../experiments/mirror_inertia_lemma/RESULTS.md)
- [Observer mirror operator](../experiments/observer_mirror_operator/RESULTS.md) · [directory](../experiments/observer_mirror_operator/)
- [Metatron prime return](../experiments/metatron_prime_return/RESULTS.md) · [finite chamber no-go](../experiments/metatron_prime_return/FINITE_CHAMBER_NO_GO.md)
- [Golden billiard prime return](../experiments/golden_billiard_prime_return/RESULTS.md) · [directory](../experiments/golden_billiard_prime_return/)
- [Two-sided irrational horizon](../experiments/two_sided_irrational_horizon/)
- [Prime horn](../experiments/prime_horn/README.md)
- [Zeta cube null](../experiments/zeta_cube_null/VERDICT.md) · [original preregistration](../experiments/ZETA_CUBE_NULL_PREREG_v1.md)

## Related instruments and GHP context — not RH evidence

- [Zeta harp](../experiments/zeta_harp/README.md), [quantum harp](../experiments/zeta_harp_quantum/README.md)
- [Harp mathematical specification](../instruments/zeta_harp_v2/MATH_SPEC.md), [claim boundary](../instruments/zeta_harp_v2/CLAIM_BOUNDARY.md), [prior art](../instruments/zeta_harp_v2/PRIOR_ART.md)
- [Quantum resource audit](../research/quantum/ZETA_HARP_QUANTUM_RESOURCE_AUDIT.md), [qutrit overlap bridge](../research/quantum/ZETA_HARP_QUTRIT_OVERLAP_BRIDGE.md)
- [GHP core and golden-chain context](../GHP_CORE_v3.md)
- [Viviani–phi Surface, explicitly not a physical horizon](../VIVIANI_PHI_HORIZON.md)
- [Do-not-claim ledger](../DO_NOT_CLAIM.md)

## Provenance and limits of this collection

- This hub indexes the locally available recent research; it is not a verbatim archive of private chat, bathroom photographs, or friends' messages.
- Earlier rounds discussed in `aukora-deep` have not been copied or independently inventoried here. Do not assume this is a complete archive of those other-repository rounds.
- Toy predictions were committed at `8df1c25`; toy results at `b68b14c`. Fable D6 records result commit `af286a9` and prediction commit `bb517fe`.
- The hub and recent files are local unless a successful GitHub push is explicitly confirmed. A GitHub-shaped URL alone is not evidence of publication.
- Future work: add a dated report and a link here; preserve predictions, controls, failures, exact scopes, and original author files. Keep MEASURED / UNVERIFIED / PREDICTED / VOID labels.

Reproducibility commands should be run from the repository root unless the original script documents a different working directory.
