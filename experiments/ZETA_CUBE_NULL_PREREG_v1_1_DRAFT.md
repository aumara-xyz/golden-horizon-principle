# Preregistration DRAFT — ZETA-CUBE-NULL v1.1 (externally authored statistics; for independent reimplementation)

- test_id: ZETA-CUBE-NULL-v1.1
- date_locked: **PENDING OWNER HASH-LEVEL SIGNATURE** (per the adopted sign-off standard: the owner approves this exact file by its SHA-256, not by blanket directive).
- purpose: the v1 NULL stands under its disclosed implementation choices; v1.1 exists for the independent-reimplementation round (external reviewer GPT 5.6 authors a reference implementation from THIS TEXT ALONE, without sight of our code; both run; verdicts and hashes diffed).
- statistical protocol (authored by the external reviewer, adopted verbatim):
  - S1 = chi-square occupancy vs uniform (raw chi2, Cramer's V, occupancy vector, max cell deviation reported).
  - S2 = lag-one mutual information of consecutive flattened cell indices, RAW PLUG-IN estimator, no analytic bias correction; bias handled empirically via matched nulls at identical sample size and alphabet. Report raw MI, median null MI, excess MI, null percentile.
  - Inferential null families: (1) uniform random ordinates through the identical pipeline; (2) gap-shuffled zeros preserving the observed gap multiset. **10,000 replicates per family**, committed seed ranges (uniform: 7000-series; gap-shuffle: 8000-series).
  - The prime sequence is a single descriptive structured comparator: never in a percentile spread, p-value, or verdict.
  - One-sided upper-tail test. p_{j,k} = (1 + #{S >= S_real}) / (B + 1) per endpoint j and family k; p_j = max over the two families; Holm correction across S1 and S2 at familywise alpha = 0.05.
  - Verdicts: NULL (neither endpoint survives Holm), FINITE ANOMALY (an endpoint survives against BOTH families — a digit-distribution observation only, triggering an untouched-block replication and no RH interpretation), VOID (integrity/freeze failures).
  - Freeze order: pipeline written → unit tests on synthetic fixtures → environment lock → code SHA-256 → data SHA-256 → seeds frozen → manifest committed → controls run → real zeros run; any post-control code change voids the run.
- sigma-blindness recorded as a formal property: F(sigma+it) = F(sigma'+it) for all sigma, sigma'. This test can never bear on RH under any outcome. RH-CUBE-001 as an RH-relevant claim is KILLED at definition (K3); the cube is retained as symbolic/visualization only.
- data: Odlyzko zeros1 table (SHA-256 recorded at freeze), first 10,000 ordinates, slicing and flattening rules pinned in the implementation manifest.
