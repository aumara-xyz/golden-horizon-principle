# Golden Zipper v5 - Phi Anchor Shear Derivation Test

Toy telemetry only. Not physics evidence. Not proof of GHP. Not write-law closure.

## Executive Summary

This test starts from exact anchors and applies finite-observer distortions: phase lag, window drift, delay, noise, and rational approximation cutoff. It then asks whether the resulting symbolic trails land in the same near-anchor band that direct offset scans prefer.

Verdict: **D/E-leaning / current shear derivation does not rescue phi cleanly**
Recommendation: **no hardening, keep symbolic only**

## What This Supports

- Golden mean effective offset: `0.0043`
- Golden offset-match fraction to its own direct best band: `0.194`
- Golden mean tradeoff gap to direct best: `-0.085`

## Anchor Comparison

| Anchor | Mean effective offset | Offset-match fraction | Mean tradeoff gap |
|---|---:|---:|---:|
| golden | 0.0043 | 0.194 | -0.085 |
| silver | 0.0022 | 0.653 | -0.036 |
| bronze | 0.0040 | 0.028 | -0.156 |
| bounded_probe | 0.0017 | 0.023 | -0.135 |

## Reading

If the phi-shear idea is real, the exact phi anchor should, under finite observation, generate symbolic trails whose effective offsets cluster near the same near-phi band that direct scans prefer.

This test does not ask whether exact phi wins raw memory tradeoff. It asks whether near-phi winners can be produced from exact phi by finite-observer distortion rather than chosen by hand.

## Red-Team View

The skeptical threat remains scoring artifact and generic-anchor behavior. If silver, bronze, or a bounded irrational anchor produce the same kind of shear-band mapping, then the result does not rescue phi uniquely.

## Strongest Result

- Strongest derived run: `silver` / `noise_big` / capacity `50` / effective offset `0.0000` / tradeoff `0.621`

## Weakest Result

- Weakest derived run: `bounded_probe` / `cutoff_34` / capacity `400` / effective offset `-0.0160` / tradeoff `0.248`

## Do-Not-Claim Ledger

- does not prove GHP
- does not prove phi is the code of reality
- does not prove the write-law
- does not prove memory creates matter
- does not prove consciousness
- does not prove VPH
- does not count as physics evidence
- does not justify changing the core share paper