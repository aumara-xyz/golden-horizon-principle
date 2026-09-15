# D34 — the floor axis at L=0.6: predictions (before compute)

Base tip 01e8a5a (+ the T=320 append when it lands). Court frozen (D28 hashes, confirmed twice).
Frozen: the D32 winners' W_hi values (odd 6.09636e-7, even 1.65227e-9 at T=1024) — no new scoring,
no new candidates for items 1-2. Zero GPU, zero API. Work in this directory.

## The mechanism under test (Fable, D33)
The 22 percent compact-term gap at L=0.6 may live in the FLOOR, not the candidate: the certified
floor is the infimum of the reduced form at its cutoff (T=160), whose beta-balance undercharges
the spectral tail of boundary-carrying minimizers. Signature already measured: the L=0.7 floor
rose 26 percent from T=160 to T=240; D33 lifted the L=0.6 floors 9.2/9.4 percent at T=240
(odd lambda0 5.34232055637e-7, even 1.43432066724e-9), moving the frozen-winner brackets from
1.2466/1.2597 to 1.1416/1.1522. Kill rule for the axis: a floor step below its predecessor (or
under 1.03 relative rise) stops the axis; a wrong-set certification must land BELOW its
correct-set predecessor and be rejected.

## Item 1 — finish the floor axis (after Fable's T=320 lands)
- Fable's prediction: ell_320/ell_240 in [1.03, 1.08]; the odd bracket reaches 1.10-1.12 with
  floor alone.
- Mine: (a) the axis steps DECAY geometrically (the reduced form's T-dependence is governed by
  the minimizer's spectral tail, which decays; predict ell_400/ell_320 < ell_320/ell_240); 
  (b) the odd bracket lands at or under 1.10 by the floor axis alone (closes the room) or lands
  within 3 percent of the gate (item 3 then skipped); (c) the even bracket lands 1.13-1.17
  (open; the even sector's floor rise should mirror odd's within a point).
- Stop rule: first step under 1.03, or 40 CPU-minutes on the axis.

## Item 2 — decompose the remaining gap at the best floor (odd, then even)
gap = (W_hi/ell - 1) = (a) the wave's own enclosure width (W_hi/W_lo - 1; measured 1.18 percent
odd at the D32 winner) + (b) the candidate's reduced excess (m_c/m - 1, with m_c the candidate's
value in the SAME reduced form the floor certifies, same T/N/K/prec-parameters, float) +
(c) the floor's Schur slack (m/ell - 1, tiny) + the remainder = the reduced-versus-full gap on
the candidate (W_lo/m_c - 1), the undercharged-tail term the axis is measuring at the floor.
- Fable's prediction: (b) under 6 percent.
- Mine: (b) will come out larger than 6 percent as W_lo/m (12.8 percent at T=240) unless the
  candidate's reduced value m_c is meaningfully above the certified infimum m; the interesting
  number is the remainder. I predict the remainder is 8-12 percent at the T=240 floor and falls
  along the axis (it is the same object item 1 measures).

## Item 3 — only if the odd bracket remains open by more than 3 percent after the floor work
The D28 loop at L=0.6 with the gate against the BEST certified floor, one added lever: the
prolate seed (project the top prolate at Omega* ~= 16 into the admissible set). Fable's
prediction: the seed lowers W_lo/m_c by 2-5 points; if it does not move at all, the candidate
family is not the issue and the round ends.

## Item 4 — controls, both BEFORE any bracket is declared
1. wrong-visible-set floor: certify the L=0.6 odd floor at T=240 with the FULL shift set
   (including the invisible log4). It must land BELOW the correct-set predecessor (5.3423e-7)
   and be rejected by the kill rule.
2. threading: the L=0.6 odd candidate scored against the L=0.5 odd floor constants must fail
   the threading check (incoherent enclosure), as in D30's C1.

## Wall sentence target
L=0.6 odd closed by floor-side work alone, or open with its gap split into three named numbers.
