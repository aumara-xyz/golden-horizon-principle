import mpmath as mp

mp.mp.dps = 25

print("=== HADAMARD PROOF BY CONTRADICTION (1896) ===")
print("Testing Inequality: zeta(sigma)^3 * |zeta(sigma+it)|^4 * |zeta(sigma+2it)| >= 1.0\n")

t0 = 14.1347

print(f"{'sigma':>8} | {'zeta(sigma)^3':>15} | {'|zeta(sigma+it)|^4':>20} | {'Product':>15} | Status")
print("-" * 75)
for sigma in [1.5, 1.2, 1.1, 1.05, 1.01, 1.001]:
    z1 = float(mp.zeta(sigma))**3
    z2 = float(abs(mp.zeta(sigma + 1j * t0)))**4
    z3 = float(abs(mp.zeta(sigma + 2j * t0)))
    prod = z1 * z2 * z3
    status = ">= 1.0 (HOLDS)" if prod >= 1.0 else "CONTRADICTION (< 1.0)"
    print(f"{sigma:8.3f} | {z1:15.2f} | {z2:20.4e} | {prod:15.4f} | {status}")
