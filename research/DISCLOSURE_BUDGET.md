# The Disclosure Budget

**A closed form for what an auditor accumulates per inclusion proof.**

Status: measured, exact, no free parameters. Engineering result. Not physics.
Date: 2026-08-10. Method: preregistered with predictions and kill conditions committed before the run.

---

## The finding

Every RFC 6962 inclusion proof discloses **two** leaf hashes, not one: the requested leaf, and its
level-0 sibling — which is an **adjacent record the requester never asked for and was never
authorised to see**. Measured at exactly 2.00 across every tree size tested.

After *k* proofs on an *n*-leaf tree, the recipient holds leaf hashes for

> **coverage(k) = 1 − (n − k)(n − k − 1) / ( n (n − 1) )**

Solving for half the tree gives an exact constant with no fitting:

> **k₅₀ = (1 − 1/√2) · n ≈ 0.2929 n**   ·   **k₉₀ ≈ 0.684 n**

| n | measured k₅₀ / n | measured k₉₀ / n | leaves per proof | node coverage at k₅₀ |
|---:|---:|---:|---:|---:|
| 256 | 0.285 | 0.691 | 2.00 | 0.676 |
| 1024 | 0.288 | 0.688 | 2.00 | 0.682 |
| 4096 | 0.292 | 0.684 | 2.00 | 0.678 |

Closed form vs. brute-force simulation: **RMS 0.00244**.

Internal-node coverage runs *ahead* of leaf coverage — 0.68 of internal nodes held at the point
where half the leaves are covered. Upper levels are shared between proofs, so **structure leaks
faster than content**.

---

## What was retracted

An earlier framing proposed a "Disclosure Page Time" with a **½ threshold**, by analogy to the
Page curve, where a black hole begins revealing correlations at half its entropy.

**That threshold does not transfer and is withdrawn.** The Page curve *turns* because Hawking
radiation is finite and correlations must eventually surface. Merkle disclosure has no turning
point — proofs only accumulate. The measured curve is smooth, concave and monotone throughout.

Ship the curve. Do not ship the constant.

## An instrument self-catch, recorded

The first run reported a knee. It was the instrument, not the world. Two defects, both mine:

1. The predicted model assumed sampling **with** replacement (coupon-collector). The real process
   draws **without** replacement. Correct model: RMS 0.00244. Incorrect model: RMS 0.11392 — 47× worse.
2. The knee test used a second-difference threshold of 1e-4, while coverage advances in steps of
   2/n = 0.00195. The threshold sat **below the quantisation floor**, so a discrete staircase
   exceeded it automatically.

Same class as a shuffle control that over-split under skewed marginals. Recorded rather than
quietly fixed.

---

## Scope fence

This bounds what the **recipient holds**. It is not a confidentiality proof: hashes are not
preimages, and holding a leaf hash is not holding the record.

What it does bound is the recipient's ability to **confirm or deny records they were never shown**,
and to **detect a split view**. Coverage must never be read as disclosure of content.

## Why it matters

It answers, with a number, the first question any security reviewer asks of selective disclosure:
*how many proofs can I issue before I have given away the tree?*

The answer is now a curve with a derived constant, and the honest limit is stated alongside it.
