# D23 — the dangerous wave is a prolate function, and the floor falls like e^{−C·e^{2L}} (Fable, 2026-09-13)
Predictions first (PREDICTIONS.md). Inputs: the eight D22 certified lower bounds and their frozen minimizers (T = 160, 160 modes). Floating arithmetic on certified inputs; no new certificates; no zero ordinates. d23_results.log/json.

## A. Profile model on the certified lower bounds (four points per parity)
| model | even: fitted slopes vs measured 53.1 / 64.8 / 83.2 | rel. RMS slope error | odd: fitted vs measured 44.7 / 58.4 / 78.6 | rel. RMS |
|---|---|---|---|---|
| M1: log λ = A − B·L | 66.8 / 66.8 / 66.8 | 0.188 | 60.4 ×3 | 0.244 |
| M2: log λ = A − C·e^{2L} | 54.1 / 66.1 / 80.7 (A = 15.68, C = 10.98) | **0.024** | 49.0 / 59.8 / 73.1 (A = 18.0, C = 9.94) | **0.070** |
Prediction HELD: the e^{2L} model fits within 10 % in both parities; the linear model fails. e^{2L} is the largest integer whose logarithm fits in the window, i.e. the size of the arithmetic the room can see. Four points, two parameters: a model comparison, not an asymptotic law; it is consistent with the changing-slope form Astra derived from Zhu's profile law in D20 and inconsistent with any constant rate.

## B. The certified minimizer is the top prolate spheroidal function of its parity
Overlap |⟨c, ψ_k(Ω*)⟩| with the leading even (k = 0) / odd (k = 1) prolate of bandwidth Ω on [−L, L] (top eigenvector of the time-frequency limiting operator in the same Legendre basis), maximized over Ω:
| L | even overlap | Ω* | c = Ω*L | odd overlap | Ω* | c |
|---|---|---|---|---|---|---|
| 0.4 | 0.99984 | 13.1 | 5.2 | 0.99707 | 11.8 | 4.7 |
| 0.5 | 0.99990 | 14.6 | 7.3 | 0.99897 | 13.3 | 6.7 |
| 0.6 | 0.99992 | 16.1 | 9.7 | 0.99922 | 14.9 | 8.9 |
| 0.7 | 0.99992 | 17.7 | 12.4 | 0.99930 | 16.5 | 11.6 |
Overlap with the second prolate of the same parity at Ω*: ≤ 0.008 everywhere (control HELD). Predictions HELD: overlap ≥ 0.99 in all eight cases; Ω* increases with L (≈ 13.1 + 15.3·(L − 0.4) even, ≈ 11.8 + 15.7·(L − 0.4) odd); c ∈ [3, 12] HELD in seven cases and narrowly FAILED for even L = 0.7 (12.39).

## Reading
1. The wave that decides positivity is, to four decimal places in overlap, a single classical special function: Slepian's prolate spheroidal wave function, with a bandwidth that grows linearly with the room. This is the first structural statement about the minimizer in the program, and it is the kind that can be turned into a formula: λmin(L) ≈ min over Ω of W(ψ_0^{Ω}) is a one-parameter minimization over a known family, so the margin, and the e^{2L} law, should be derivable from the known asymptotics of prolate functions against the Weil symbol. That is a derivation task, not a scan, and it is the concrete form of the "Landau–Widom" thread Astra marked UNVERIFIED.
2. It also explains why D22's brackets failed: the true minimizer has super-exponentially decaying Legendre coefficients and a very small Fourier tail (a prolate is nearly band-limited to |t| ≤ Ω* ≈ 13–18, far below every cutoff used), so the discarded tail is tiny, while the derivative-norm bound we used cannot see that. A prolate candidate at 80 modes scored with cutoffs up to 1024 is the natural next attempt at closing the brackets — proposed, not run (Test 2's cap is spent).
3. Scope: floating measurements on certified inputs; nothing about other windows or RH. No novelty claimed: prolate functions appear in Zhu's title and throughout the time-frequency literature; what is new to this lab is the measured identification of the minimizer with ψ_0 and the measured law Ω*(L).
