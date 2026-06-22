# Cascade Depth Replication Notes

## CAS-004

Question:

```text
Does depth 3 remain the best finite observer-depth across regimes?
```

Result:

```text
FAIL
```

Why:

```text
depth 4 won in all four regimes.
```

Meaning:

CAS-004 falsified the specific depth-3 hunch, but strengthened the broader finite-depth question.

## CAS-005

Question:

```text
Does some intermediate finite depth repeatedly beat raw access, over-filtered access, shuffled controls, and leaky controls?
```

Result:

```text
FAIL by strict threshold, but directionally strong.
```

Observed:

```text
intermediate depths won in 7/8 regimes
modal winner was depth_4
average raw-access gap was large
shuffled controls were much worse
leaky/private controls did not materially help
average F1 was too low for promotion
```

## Paper-Safe Read

Do not promote this yet as evidence.

The safe internal conclusion is:

```text
finite intermediate projection depth is now the strongest paper-lane toy pattern,
but it needs a higher-F1 replication before the core paper should be updated.
```

## Next Test

`CAS-006` should focus on calibration rather than architecture:

- same finite-depth regimes,
- better thresholding / probability calibration,
- report precision-recall curves,
- require intermediate depths to win while raising F1 above the promotion floor.
