# D24 source and reproducibility map

Reviewed snapshot: `2ab00ea` on `codex/metatron-prime-return-v0`, 2026-09-13. Primary source links and exact mathematical locations are in [RESULTS.md](RESULTS.md). The two local checkers save SHA256 hashes of their relevant sources and evidence. External papers are reviewed for the stated claims, not certified end-to-end.

## Required reading completed

- [Research hub](../../Reimann%20Research/README.md).
- [D21 and D21.1 report](../fable_d21_test1/RESULTS.md), [repair implementation](../fable_d21_test1/d21_1.py), [repaired endpoints](../fable_d21_test1/d21_1_results.json), [original frozen vectors](../fable_d21_test1/d21_results.json), [scalar scorer copy](../fable_d21_test1/d9_score_copy.py). Historical trial1 and controls remain untouched.
- [D22 results](../fable_d22_test2/RESULTS.md), [all prediction trials](../fable_d22_test2/PREDICTIONS.md), [certificate wrapper](../fable_d22_test2/d22_certify.py), [scalar scorer](../fable_d22_test2/d22_score.py), [trial4 selector](../fable_d22_test2/d22_candidates2.py), [earlier selector](../fable_d22_test2/d22_candidates.py), [certificate and score evidence directory](../fable_d22_test2/).
- [D23 results](../fable_d23_shape/RESULTS.md), [predictions](../fable_d23_shape/PREDICTIONS.md), [floating JSON](../fable_d23_shape/d23_results.json), [log](../fable_d23_shape/d23_results.log). These are the four committed files. **Construction script not present; requested, not supplied by completion of this review.**
- Appended corrections to [D13](../fable_d13_prime_weights/RESULTS.md), [D16](../fable_d16_places/RESULTS.md), [D17](../fable_d17_squares_exponent/RESULTS.md).

## Analytic and implementation dependencies

- [D5 certificate template](../weil_hidden_modes/d5_certify.py), [imported certificate utilities](../weil_hidden_modes/certify.py), [old float checker](../weil_hidden_modes/d4_checker.py).
- [D9 full-tail proof](../codex_d9_exact_scores/PROOF.md) and the D21/D22 scorer copies named above; these scalar quadratures use a different conservative Gauss allowance from D5/D22 matrix assembly.
- [D7 independent reconstruction](../weil_hidden_modes/opus_d7_rebuild.py), [D7 report](../weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md), and [D20 review](../astra_d20_review/RESULTS.md) provide prior audit scope; no D7 matrix replay was performed here.

## Evidence replayed, not regenerated

- [check_saved_certificates.py](check_saved_certificates.py) → [certificate_audit.json](certificate_audit.json): ten repaired conservative all-function scalar checks, eight planted controls, source and effective-wrapper hashes. Exact Python fractions retain tails below ordinary floating range.
- [check_saved_witnesses.py](check_saved_witnesses.py) → [witness_audit.json](witness_audit.json): D21.1 outward sign/route checks, D22 energy-gate rejections, controls and evidence hashes. The incomplete monotonicity-survivor export stays UNVERIFIED.
- D23 fits and overlaps were read from saved outputs. No concentration matrix, eigensolver, frequency sweep or profile fit was rerun.

## Search limits

The source audit checked the specifically requested Zhu and CCM versions, earlier Connes–Consani work, and classical/modern prolate references. It found established prolate–Weil connections but no theorem supplying D23's raw-prolate variational identity or coefficient. This is a scoped prior-art check, not an exhaustive novelty search. The original Landau–Widom article was bibliographically verified; its transition formula was checked through a cited primary research exposition. Web PDF screenshot retrieval was unavailable for the quadrature paper; its extracted theorem and node-count definition were checked directly. No claim depends on interpreting an unread illustration.

The deep-research workflow led to version-pinned primary references and separation of theorem, conjecture, finite observation and missing implementation. It did not authorize new experiments. The next computation remains preregistered and unrun in [PREDICTIONS.md](PREDICTIONS.md).
