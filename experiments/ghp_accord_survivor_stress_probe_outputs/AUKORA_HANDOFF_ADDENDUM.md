# ASS-001 Aukora Handoff Addendum

The survivor stress battery keeps the same narrow handoff as AAP-001.

## Strongest Additions

- Require whole-regime holdout tests for any HRT boundary-mode classifier.
- Require field-ablation tests so one field cannot secretly encode the verdict.
- Require hidden-only perturbation tests; private/authority perturbations must not change advisory predictions.
- Require timing aggregation tests before storing cadence/timestamps.
- Require exact-token leak scans on reports and CSVs, not only runtime records.

## Build-Lane Rule

If an HRT field cannot survive holdouts, ablations, fake-positive controls, and leak scans, it stays offline or quarantined.
