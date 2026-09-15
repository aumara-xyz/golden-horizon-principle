# D35 — the axis endgame at L=0.6: predictions (before compute)

Base tip dc09c9a. Court frozen (D28 hashes, confirmed twice). Frozen: the D32 winners' W_hi
(odd 6.09636462949219549e-7, even 1.65226628474386972e-9) — no new scoring, no new candidates.
Zero GPU, zero API. Machinery: Fable's d30_certify.py, PREC=320 (the 192-bit Bessel trap is
recorded in D33 and avoided), N=320, K=48, the correct visible set by the runtime filter.

## Why this round exists
D34 left the axis at T=320 with brackets odd 1.1019 / even 1.1107 — both open, odd by only
0.19 percent over the 1.10 gate. Peter's tune-in authorizes the next axis probes. The floor
needs to rise 0.17 percent (odd) / 0.97 percent (even) over its T=320 value for the room to
close with the frozen W_hi values.

## Predictions
1. The axis step decays geometrically (measured: 9.2 -> 3.6 percent). Prediction:
   **ell_400/ell_320 in [1.005, 1.02]** for both parities (even's step within 0.3 points of
   odd's, as at every prior step).
2. **The odd room CLOSES at T=400** with floor-side work alone: bracket in 1.080-1.098.
   (Kill condition: if ell_400/ell_320 < 1.002 the axis is exhausted below the closing
   threshold and the room stays open — a floor that will not give further.)
3. The even room closes or lands within 0.5 percent of the gate: bracket 1.085-1.105.
4. The decomposition at the best floor shifts the shares again: the candidate-reduced-excess
   term (m_c/ell - 1) falls below 2 percent; the reduced-versus-full remainder stays
   5.3-5.5 percent (it is the candidate-side object and does not move with the floor).
5. Controls: inherited from D34 (wrong-set floor rejected 0.9384x; threading incoherent) and
   extended: the T=400 certs must use the runtime visible filter (correct set asserted by the
   machinery's own check) and the axis kill rule (a floor below its predecessor is rejected)
   is armed on the new rows too.

## Budget
Two certifications (odd + even, T=400, N=320, K=48, 320 bits), ~15-20 min each in parallel;
~40 CPU-min total; wall 60 min hard stop. If a T=400 cert fails to converge at 320 bits, the
failure is kept and the axis ends at T=320 with the split-gap wall sentence.
