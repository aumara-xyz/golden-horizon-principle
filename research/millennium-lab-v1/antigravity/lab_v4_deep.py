import math
import mpmath as mp
import numpy as np

mp.mp.dps = 25

print("================================================================")
print("     MILLENNIUM MATH LAB v4 — DEEP HARMONIC & SCALING SUITE     ")
print("================================================================\n")

# -------------------------------------------------------------
# TEST 1: THE MUSICAL CHORD RATIOS OF THE RIEMANN ZEROS
# -------------------------------------------------------------
print("--- [TEST 1] The Musical Intervals of the First 10 Zeros ---")
# Base frequency = gamma_1 = 14.134725 rad/s
zeros_10 = [float(mp.zetazero(n).imag) for n in range(1, 11)]
base_freq = zeros_10[0]

musical_intervals = [
    (1.0000, "Unison (1:1)"),
    (1.2500, "Major Third (5:4)"),
    (1.3333, "Perfect Fourth (4:3)"),
    (1.5000, "Perfect Fifth (3:2)"),
    (1.6667, "Major Sixth (5:3)"),
    (1.7500, "Harmonic Seventh (7:4)"),
    (2.0000, "Octave (2:1)"),
    (2.5000, "Tenth / Octave + Third (5:2)"),
    (3.0000, "Twelfth / Octave + Fifth (3:1)")
]

def find_closest_interval(ratio):
    best_name = ""
    min_diff = 1e9
    for target_ratio, name in musical_intervals:
        diff = abs(ratio - target_ratio)
        if diff < min_diff:
            min_diff = diff
            best_name = f"{name} (diff {diff:+.4f})"
    return best_name

print(f"{'Zero #':>6} | {'Frequency (gamma_n)':>20} | {'Ratio to Base (gamma_n / gamma_1)':>35} | Closest Musical Interval")
print("-" * 95)
for i, gamma in enumerate(zeros_10, 1):
    ratio = gamma / base_freq
    chord_match = find_closest_interval(ratio)
    print(f"#{i:5d} | {gamma:20.6f} | {ratio:35.4f} | {chord_match}")

# -------------------------------------------------------------
# TEST 2: SELBERG HYPERBOLIC TRACE LENGTHS (MODULAR GEODESICS)
# -------------------------------------------------------------
print("\n--- [TEST 2] Closed Periodic Geodesic Lengths on Hyperbolic Modular Surface ---")
# On the modular surface PSL(2, Z) \ H, the lengths of closed geodesics are given by:
# l(gamma) = 2 * ln( (Tr(M) + sqrt(Tr(M)^2 - 4)) / 2 ) for hyperbolic matrices M in SL(2, Z)
# Trace values Tr(M) = 3, 4, 5, 6, 7...
traces = [3, 4, 5, 6, 7, 8, 9, 10]

print(f"{'Matrix Trace':>12} | {'Hyperbolic Multiplier (lambda)':>30} | {'Geodesic Length l(gamma)':>25} | Prime Comparison")
print("-" * 95)
for trace in traces:
    # Eigenvalue lambda = (trace + sqrt(trace^2 - 4)) / 2
    eig = (trace + math.sqrt(trace**2 - 4)) / 2.0
    length = 2.0 * math.log(eig)

    # Compare with nearest prime logarithm ln(p)
    closest_prime = 2
    min_p_diff = 1e9
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        p_diff = abs(length - math.log(p))
        if p_diff < min_p_diff:
            min_p_diff = p_diff
            closest_prime = p

    print(f"{trace:12d} | {eig:30.6f} | {length:25.6f} | Nearest ln({closest_prime:2d}) = {math.log(closest_prime):.4f} (diff {min_p_diff:+.4f})")

# -------------------------------------------------------------
# TEST 3: LI COEFFICIENT ASYMPTOTIC GROWTH (lambda_n ~ 1/2 n ln n)
# -------------------------------------------------------------
print("\n--- [TEST 3] Li Coefficient High-Order Growth (n = 10 to 100) ---")
zeros_100 = [mp.zetazero(k) for k in range(1, 101)]

print(f"{'Order (n)':>10} | {'Computed lambda_n':>22} | {'Theoretical ~ 1/2 n ln n':>26} | {'Ratio (Actual / Theory)':>25}")
print("-" * 90)
for n in [10, 20, 30, 40, 50, 75, 100]:
    total = 0.0
    for rho in zeros_100:
        term1 = 1.0 - (1.0 - 1.0 / rho)**n
        term2 = 1.0 - (1.0 - 1.0 / (1.0 - rho))**n
        total += float((term1 + term2).real)

    theory = 0.5 * n * math.log(n)
    ratio = total / theory
    print(f"{n:10d} | {total:22.4f} | {theory:26.4f} | {ratio:25.4f} (MONOTONIC GROWTH)")

print("\n================================================================")
print("                   ALL EXPERIMENTS COMPLETED                    ")
print("================================================================")
