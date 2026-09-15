# D35 — the axis endgame: L=0.6 CLOSED in both parities by floor-side work alone

Base tip dc09c9a. Court frozen (D28 hashes, confirmed twice). The D32 winners' W_hi values
frozen throughout — no new scoring, no new candidates. Zero GPU, zero API. Machinery: Fable's
d30_certify.py at PREC=320, N=320, K=48, correct visible set (the runtime filter asserted
log2+log3 only). Predictions in PREDICTIONS.md before compute.

## The certified floors and the axis
| floor cutoff | odd lambda0 | step | even lambda0 | step |
|---|---|---|---|---|
| T=160 | 4.89029307909781e-7 | — | 1.31162554371630e-9 | — |
| T=240 | 5.34232055637e-7 | x1.0922 | 1.43432066724e-9 | x1.0935 |
| T=320 | 5.53273750499e-7 | x1.0356 | 1.48755830782e-9 | x1.0371 |
| T=400 | 5.63722754525e-7 | x1.0189 | 1.51629835207e-9 | x1.0193 |

Steps decay: 9.2 -> 3.6 -> 1.9 percent. Certificates: d33_cert_{parity}_L0.6_T400_N320.json
(this directory's predecessor), 1192/1190 s each at 320 bits.

## The verdict — both rooms close
| case | bracket W_hi/ell_400 | gate 1.10 | prediction band | verdict |
|---|---|---|---|---|
| L=0.6 odd | **1.0814** | -1.86 percent | 1.080-1.098 | **CLOSES** (dead center) |
| L=0.6 even | **1.0897** | -0.93 percent | 1.085-1.105 | **CLOSES** |

The kill conditions did not fire: the axis steps (1.019) are above the 1.002 exhaustion
threshold, the floors rise monotonically, and the W_hi values are the frozen certified
brackets from D32. No candidate changed, no scoring changed: the 22 percent "edge" of
D30/D32 is now measured as floor cutoff slack plus a bounded candidate-side tail, and the
room closes when the floor stops undercharging it.

## The decomposition at the closing floor (odd)
1.0814 = 1.0118 (enclosure) x 1.0532 (reduced-versus-full on the candidate, unchanged) x
1.0149 (candidate-reduced-excess, down from 7.09 percent at T=160-floors to 1.49 percent).
The candidate-side remainder (5.3 percent) is now the dominant named term — exactly the
object the prolate-seed lever (item 3 of D34, still preregistered) targets if a later round
wants the L=0.7 edge attacked.

## Prediction ledger
| prediction | outcome |
|---|---|
| ell_400/ell_320 in [1.005, 1.02], parities within 0.3 points | HELD (1.0189 / 1.0193) |
| odd closes, bracket 1.080-1.098 | HELD (1.0814) |
| even closes or within 0.5 percent | HELD (closes, 1.0897) |
| candidate-reduced-excess under 2 percent at the best floor | HELD (1.49 / 1.58 percent) |
| remainder stays 5.3-5.5 percent | HELD (5.32 / 5.48) |
| axis kill rule armed | not triggered |

## The map now
| room | status |
|---|---|
| L=0.4 odd | closed 1.0884 (D26) |
| L=0.4 even | closed 1.0643 (D28) |
| L=0.5 odd | closed 1.0882 (D28) |
| L=0.5 even | closed 1.0947 (D30) |
| **L=0.6 odd** | **closed 1.0814 (D35, floor-side)** |
| **L=0.6 even** | **closed 1.0897 (D35, floor-side)** |
| L=0.7 (both) | open — the next edge; floors certified at T=160/240, the axis probe and candidates are the next round |

Six closed brackets, two machines, one located and now-shrinking edge at L=0.7. No RH claim.
