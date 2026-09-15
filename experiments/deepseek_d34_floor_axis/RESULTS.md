# D34 — the floor axis at L=0.6: results

Base tip 01e8a5a; Fable's T=320 floors (his runs, 320 bits, N=256) consumed from
fable_d33_floor_T/. Court frozen (D28 hashes, confirmed twice). Zero GPU, zero API.
Predictions in PREDICTIONS.md before compute. Failures kept (three harness iterations on the
control script's patch asserts; the control itself is clean).

## Item 1 — the floor axis (frozen D32 winners' W_hi)
| floor cutoff | odd lambda0 | step | even lambda0 | step |
|---|---|---|---|---|
| T=160 | 4.89029307909781e-7 | — | 1.31162554371630e-9 | — |
| T=240 | 5.34232055637e-7 | x1.0922 | 1.43432066724e-9 | x1.0935 |
| T=320 | 5.53273750499e-7 | x1.0356 | 1.48755830782e-9 | x1.0371 |

Steps decay (9.2 → 3.6 percent) — the axis is converging. T=400 not triggered (the step is
below the 1.05 continue-rule) and not stopped (above 1.03): per the round's rule the axis
work ends here. Brackets at the best floor (T=320), frozen D32 winners' W_hi:

| case | bracket W_hi/ell_320 | over the 1.10 gate | verdict |
|---|---|---|---|
| L=0.6 odd | **1.1019** | +0.19 percent | OPEN (inside Fable's predicted 1.10-1.12 band) |
| L=0.6 even | **1.1107** | +1.07 percent | OPEN (my 1.13-1.17 band MISSED low — the axis was more generous to even than I predicted) |

Item 3 (the loop with the prolate seed) is SKIPPED by the round's rule: the odd bracket is
open by 0.19 percent, under the 3 percent threshold.

## Item 2 — the gap split into three named numbers (multiplicative identity, exact)
W_hi/ell = (W_hi/W_lo) x (W_lo/m_c) x (m_c/ell), with m_c the candidate's value in the SAME
reduced form the floor certifies (same L, T, N=192, K=48, visible set; float builds reproduce
the certified floors to 9 digits odd, 5 digits even).

At the T=320 floor (best), L=0.6 odd:
- (a) the wave's own enclosure width W_hi/W_lo - 1 = **1.18 percent**
- the candidate's reduced excess m_c/ell - 1 = **3.41 percent**
- the reduced-versus-full gap on the candidate W_lo/m_c - 1 = **5.32 percent**
- product check: 1.01179 x 1.05316 x 1.0341 = 1.1019 exact.

At the T=240 floor the same candidate reads: (a) 1.18, (b) m_c/m - 1 = 7.09, remainder 5.32
(total 14.11); even at T=240: (a) 1.70, (b) 7.38, remainder 5.48 (total 15.20); even at T=320:
(b) 3.54, remainder 5.48 (total 11.07).

The structure is parallel across parities and it behaves exactly as the mechanism predicts:
what D32 read as an unmovable 22 percent candidate excess was, at the T=160 floor, mostly
floor slack; as the floor's cutoff rises, the "candidate excess" share falls (7.1 -> 3.4
percent) while the candidate-side reduced-versus-full term stays near 5.3-5.5 percent — that
term is the candidate's own undercharged tail, the same object the floor axis is measuring
one level up.

## Prediction ledger
| prediction | outcome |
|---|---|
| ell_320/ell_240 in [1.03, 1.08] (Fable) | HELD (1.0356 / 1.0371) |
| odd bracket reaches 1.10-1.12 with floor alone (Fable) | HELD (1.1019) |
| axis steps decay geometrically (DeepSeek) | HELD (9.2 -> 3.6) |
| odd closes or lands within 3 percent of the gate (DeepSeek) | HELD (open by 0.19 percent) |
| even lands 1.13-1.17 (DeepSeek) | MISSED (1.1107) |
| candidate excess (b) under 6 percent (Fable) | MISSED at T=240 (7.09/7.38), HELD at T=320 (3.41/3.54) |
| wrong-set floor rejected by the kill rule | HELD (control) |
| threading control fails on wrong-L scoring | HELD (control) |

## Item 4 — controls (both run BEFORE the brackets were declared)
1. Wrong-visible-set floor (L=0.6 odd, T=240, full shift set including the invisible log4):
   lambda0 = 5.01334248216e-7 = 0.9384x the correct-set predecessor -> below it -> the kill
   rule rejects. The set used is recorded in the cert JSON (`CONTROL_WRONG_SET_ALL_SHIFTS`).
2. Threading: the L=0.6 odd candidate scored under the L=0.5 odd machinery gives an incoherent
   tight interval (W in [0.03649595, 0.03649629], inf ratio 201.71 vs the correct 1.25/1.10
   family) -> rejected, as in D30's C1.

## Wall sentence
**L = 0.6 is open in both parities with its gap split into three named numbers** — at the best
floor (T=320): odd 1.1019 = 1.18 percent enclosure x 3.41 percent candidate-reduced-excess x
5.32 percent reduced-versus-full; even 1.1107 with the same structure. The floor-side mechanism
accounted for a third of what D32 called an edge; the remaining ~5.3 percent is the
candidate-side undercharged tail, and the next lever against it is the prolate seed (item 3,
preregistered, now unblocked if a later round wants it). No RH claim.
