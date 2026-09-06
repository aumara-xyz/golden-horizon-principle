# Riemann research — central hub

Folder named `Reimann Research` as requested. Updated 2026-09-06.

This is the single entry point for the recent Riemann-related work in Golden Horizon Principle. Original experiment files remain in place to preserve executable paths, provenance, and collaborators' working files. Links below lead to the canonical files, not duplicate snapshots. This is an organizational index, not a claim that every linked experiment has passed an independent audit.

## Start here

1. [Current status, the two 0.7s, and your friend's contribution](../experiments/prime_gears_codex/STATUS-AND-CONTRIBUTIONS.md)
2. [Latest independent implementation audit: Opus D7](../experiments/weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md) · [Codex scope/readout note](D7-READOUT.md)
3. [Codex gear / prime-coordinate / ternary toy results](../experiments/prime_gears_codex/RESULTS.md)
4. [Completed round's directive: Opus D7 independent audit](NEXT-ROUND-D7.md)
5. [Fable D8: can confinement limit the arithmetic contribution? — lemma proved, combination obstructed](../experiments/fable_d8_confinement/REPORT.md)
6. [Codex D9: exact fixed-wave scores with rigorous infinite-tail bounds](../experiments/codex_d9_exact_scores/RESULTS.md) · [proofs](../experiments/codex_d9_exact_scores/PROOF.md)
7. [Codex D10: Viviani-inspired joint geometry — scoped local obstruction and finite square completion](../experiments/codex_d10_joint_geometry/RESULTS.md) · [proofs and scope](../experiments/codex_d10_joint_geometry/PROOF.md)
8. [Next: Fable D11 — D10 audit and a short certificate for the joint balance](FABLE-HANDOFF-D10-D11.md) (directive only; not run)

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
| D8 confinement lemma (truncated translations) and its combination with the archimedean term | [Fable D8 report](../experiments/fable_d8_confinement/REPORT.md) | [Predictions](../experiments/fable_d8_confinement/PREDICTIONS.md), [code and outputs](../experiments/fable_d8_confinement/) |
| D9 exact fixed-vector test of the D8 mixing family | [Codex D9 results](../experiments/codex_d9_exact_scores/RESULTS.md), [analytic bounds](../experiments/codex_d9_exact_scores/PROOF.md) | [Predictions](../experiments/codex_d9_exact_scores/PREDICTIONS.md), [code, frozen vectors and endpoints](../experiments/codex_d9_exact_scores/) |
| D10 joint-kernel geometry and pole-directed completion of squares | [Codex D10 results](../experiments/codex_d10_joint_geometry/RESULTS.md), [proofs and limits](../experiments/codex_d10_joint_geometry/PROOF.md) | [Predictions](../experiments/codex_d10_joint_geometry/PREDICTIONS.md), [code and interval endpoints](../experiments/codex_d10_joint_geometry/) |

Read chronologically when reconstructing a claim: earlier claims were corrected or withdrawn, not deleted. D6 supersedes D5's upward-rounded odd constant and false pointwise complex-function identity.

D9 supplies exact negative witnesses for the D8 modified form at theta=0.1,0.25,1, not for W itself. It also corrects D8's universal 'every theta>0 fails' claim: tiny positive theta preserves the D7 all-wave margin. Removing arithmetic makes the tested odd wave negative, so a small prime contribution relative to a crude bound must not be described as irrelevant to the residual score. D9 is a fixed-vector calculation, not a new all-window certificate.

D10 excludes a local diagonal-gauge positive-conductance representation using an exact signed-kernel triangle, while a positive three-variable control shows that general sums of squares remain possible. A pole-directed joint completion is certified for finite D7 lower-envelope blocks: it substantially improves the remaining minimum eigenvalue but leaves small modes and a delicate scalar balance. It does not provide an all-window positivity mechanism. Separate full-W pole-mutation witnesses retain D9's entire tail. The Viviani connection is methodological inspiration, not mathematical evidence from family history or physical geometry.

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
- Publication status is recorded in [PUBLICATION.md](PUBLICATION.md). Historical 'not pushed' notes describe the state when each report was written; consult the publication record for later uploads. A GitHub-shaped URL alone is not evidence of publication.
- User instruction, 2026-09-06: publish every completed research round to `origin/codex/metatron-prime-return-v0` after committing its results and hub link. This supersedes older no-push instructions for future rounds, but never authorizes force-pushing, overwriting collaborator work, or merging to main. Predictions must still be committed before computation.
- Future work: add a dated report and a link here; preserve predictions, controls, failures, exact scopes, and original author files. Keep MEASURED / UNVERIFIED / PREDICTED / VOID labels.

Reproducibility commands should be run from the repository root unless the original script documents a different working directory.
