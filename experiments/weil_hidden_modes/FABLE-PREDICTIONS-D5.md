# D5 predictions — odd-sector certificate at L=0.7, and one bounded two-observer (unitary dilation) test. Written before compute.

## Part 1: odd sector
Form (real f ∈ L²[−L,L], unitary FT F(t) = (2π)^{-1/2}∫f e^{−ixt}): W(f) = ∫_ℝ Ψ(t)|F(t)|² dt + 2·(∫f e^{x/2}dx)(∫f e^{−x/2}dx), Ψ = a − prime comb.
Pole term derived (not assumed): for f = f_e + f_o, ∫f e^{±x/2} = C ± S with C = ∫f_e cosh(x/2), S = ∫f_o sinh(x/2); so pole = 2C² − 2S². Odd sector: pole = −2S² ≤ 0, NOT zero. Sectors decouple for real f; complex f = f1 + i f2 gives W(f) = W(f1) + W(f2) (cross term is purely imaginary inside a real part). Hence real even + real odd certificates cover all complex f.
Basis: odd Legendre q_n, n = 1,3,…,159 (80 modes); F_n = (−i)(−1)^{(n−1)/2}·√((2n+1)/(2L))·2L j_n(tL)/√(2π); common phase −i drops out of |F|². Pole vector s_n = ∫q_n sinh(x/2) = √((2n+1)/(2L))·2L·i_n(L/2) for odd n; tail bound identical to the even p_n bound.
A_odd = M + β*I − 2 s sᵀ; discarded block ≥ (β* − ε_D − 2‖s_D‖²)I; coupling ≤ ε_C + 2‖s_N‖‖s_D‖ — same checker (d4_checker.py, unchanged).
PREDICTED: λ₀(A_odd) ∈ [1.0e-10, 3.4e-10] (Codex's 32-sine-mode odd minimum is 3.313e-10; 80 Legendre modes should be at or below it, same order). ε_C < 1e-15, ε_D < 1e-30, ε_p < 1e-300. Verdict ACCEPT with margin ≈ λ₀.
Control/mutation: flip the pole sign (+2ssᵀ). PREDICTED: λ₀ changes by more than a factor 10 (the pole term is load-bearing in the odd sector). If it does not change, the pole derivation above is not being tested by this run and must be re-examined.
Method: as run 4 (certified GL, analytic strip bound, shifted digamma), plus: certify V invertible by Gershgorin on VᵀV (λmin(VᵀV) > 0) and use λmin(A) ≥ λmin(VᵀAV)/λmax(VᵀV); rerun the even sector with this addition for the record.

## Part 2: unitary dilation
U = [[A, (I−AA†)^{1/2}],[(I−A†A)^{1/2}, −A†]] is unitary for every contraction A (Halmos 1950); proof uses A(I−A†A)^{1/2} = (I−AA†)^{1/2}A.
Preregistered question: does completing a lossy subsystem into a norm-preserving whole force the subsystem's resonances (eigenvalues of A) onto the real line or the unit circle?  PREDICTED: no. The upper-left block of U is A itself; its eigenvalues are untouched. Numerically: nonnormal 2×2 A with complex eigenvalues inside the disk → U unitary to 1e-14, eig(A) unchanged, eig(U) on the unit circle.
Compression of powers: upper-left block of U² = A² + (I−AA†)^{1/2}(I−A†A)^{1/2} ≠ A² unless A is unitary. PREDICTED: ‖P U² P − A²‖ > 0.1 for BOTH the nonnormal mutation and the diagonal real control (diag(0.5, −0.3) gives P U² P = I). Existence of finite-dimensional N-step power dilations for any fixed N (Egerváry) and of the infinite-dimensional Sz.-Nagy power dilation: cited as established mathematics, UNVERIFIED from memory, not used in any conclusion.
No zeta-zero inputs. No φ. No physical identification.
