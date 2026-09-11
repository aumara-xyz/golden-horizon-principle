# D13 — how much of each prime is load-bearing? (predictions before compute, 2026-09-11)
Setup frozen as in D12 (floating numpy, T = max(1.3·2π e^{B_L}, 60), authentic β kept when weights are scaled down, noise floor 3e-14).
Test 1: scale only the n = 2 weight by θ ∈ [0,1] at L ∈ {0.40,…,0.60}; θ* = smallest θ keeping λmin > 3e-14. PREDICTED: θ* increases with L in both parities; odd θ*(0.5) > 0.8; even θ*(0.5) ∈ (0.3, 0.8); at L = 0.60 both θ* > 0.9.
Test 2: subsets of {2,3,4} at L = 0.7. PREDICTED: only subsets containing 2 stay positive; {2} alone positive in both parities; {3,4} negative in both.
Test 3: L = 0.30 control — all θ identical (no prime fits). Mutation at L = 0.5, shift 1.1·log 2: PREDICTED θ* moves by more than 0.1 in at least one parity (the correlation depends on the shift).
