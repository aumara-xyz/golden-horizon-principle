# Fable audit of the Weil hidden-modes program (2026-09-06)

Predictions: FABLE-PREDICTIONS-audit.md (commit 3b5d3ac, before D1/D2 ran). Codex's files were read, replayed, and not edited. Vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID. Numerical means midpoint arithmetic; certified means Arb balls or a hand proof.

## 1. Disagreement table
| item | Codex | Fable | verdict |
|---|---|---|---|
| form normalization | CC 2021 eqs (1)–(3) | matches CCM 2025 (3.7)–(3.11) and our round-5 code term by term | agree, MEASURED |
| pure-tail lemma constants 0.5600 / 0.4428 | Arb-validated | re-derived by hand, every step; leakage bound is an equality up to phase | agree, MEASURED (hand) |
| N=32 sector minima | 5.972e-13 / 3.313e-10 (certified signs, 1e-16 / 1e-12 lower bounds) | rebuilt at 160 bits: 5.9720862e-13 / 3.313126e-10; third implementation (Fourier basis, N=60): 4.467e-13 / 2.808e-10 | agree, MEASURED |
| test replays | 5 tests | 5/5 pass on saved balls; prereg commits precede results | agree |
| "modes 33–4096 + coupling unclosed" | correct | correct, and now quantified: naive Schur fails by 12 orders (D1) | agree |
| Zhu 2608.24827 | v2 read, UNVERIFIED | v2 confirmed (Xuefeng Zhu, 2 Sep 2026; v1 25 Aug listed another name); positivity for ALL complex L² f on [−0.8,0.8], bound 8.9e-18, zeros only in proposals/validation; no data URL in HTML | agree, UNVERIFIED; partial reproduction in §3 |
| Lee–Yang | illustrates known theorem | agree; analytic obstruction stated in §4 | agree |
No numerical disagreement found. No defect found in the certificate or the lemma.

## 2. D1 — why mode-index splitting cannot close the gap (MEASURED, numerical, N=48, 160 bits)
| sector | λmin(A: 1–32) | λmin(D: 33–48) | ‖C‖_F | naive Schur ‖C‖² < λA·λD | k = coupling energy along ξ_A | k/λmin(A) | λmin(full 48) |
|---|---|---|---|---|---|---|---|
| even | 5.972e-13 | 1.709 | 0.498 | FAILS (needs ‖C‖ < 1e-6) | 8.57e-14 | 0.144 | 4.994e-13 |
| odd | 3.313e-10 | 1.723 | 0.533 | FAILS | 3.86e-11 | 0.116 | 2.895e-10 |
Reading: positivity survives adding modes 33–48 only because the near-null vector ξ_A is nearly orthogonal to the coupling; λmin(full) ≈ λmin(A) − k to 3 %. Any norm-based Schur argument in the sine index is dead by twelve orders. The entire question is the size of Σ_{j>32} |⟨φ_j, coupled ξ⟩|² relative to 6e-13, i.e. the coupling of ONE direction (the CCM ground state) to everything above it. This is the same wall as the CCM "prolate bridge": the near-null direction must be handled exactly, not by norms. PREDICTED and held: k/λ < 0.5.

## 3. D2 — Zhu's frequency-envelope reduction, reproduced at L = 0.7 (see below for numbers)
Why it works where D1 cannot: in Fourier space the prime terms are multiplication by cos(u t), diagonal, so they couple nothing; a(t) is monotone; for |t| ≥ T♯ the whole symbol is ≥ β* = a(T♯) − B. The remaining compact-frequency part is a compact operator on L²[−L,L] whose Legendre-basis matrix has super-exponentially decaying entries. Positivity of ALL f reduces to a finite matrix plus a tail bound. The gap Codex could not close in the sine index is closed by changing the splitting variable. At L=0.7: B = 2.9420, so β* > 0 needs a(T♯) > 2.94, i.e. T♯ ≳ 120 (Zhu's T₁ = 2π e^{A_L} ≈ 119).
