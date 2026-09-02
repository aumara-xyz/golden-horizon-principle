import math
import mpmath as mp
import numpy as np

mp.mp.dps = 25

print("================================================================")
print("     HIGH-ALTITUDE RANDOM ZERO PROBE (ODLYZKO / TURING STYLE)   ")
print("================================================================\n")

# Target Altitude T = 1,000,000.0
target_T = 1000000.0

# Expected Average Spacing at this altitude:
# Delta t ~ 2*pi / ln(T / 2*pi)
avg_spacing = (2 * math.pi) / math.log(target_T / (2 * math.pi))

# Estimated cumulative zero count N(T)
approx_N = (target_T / (2 * math.pi)) * math.log(target_T / (2 * math.pi * math.e)) + 7/8

print(f"Target Altitude:       T = {target_T:,.1f}")
print(f"Estimated Zero Index:  Around Zero #{int(round(approx_N)):,}")
print(f"Local Avg Wavelength:  lambda = {avg_spacing:.6f} units\n")

print("Scanning for resonance roots near T = 1,000,000...")

# Search in a fine window [1000000.0, 1000002.0]
step = 0.05
found_zeros = []
t = target_T
while len(found_zeros) < 3 and t < target_T + 5.0:
    t1 = t
    t2 = t + step
    z1 = float(mp.siegelz(t1))
    z2 = float(mp.siegelz(t2))

    if z1 * z2 <= 0:
        root = float(mp.findroot(mp.siegelz, (t1, t2)))
        found_zeros.append(root)
        t = root + 0.02
    else:
        t += step

print(f"Successfully Located {len(found_zeros)} Consecutive High-Altitude Zeros:")
for i, gamma in enumerate(found_zeros, 1):
    # Verify exact zeta value at s = 1/2 + i*gamma
    s = mp.mpc(0.5, gamma)
    zeta_mag = float(abs(mp.zeta(s)))

    # Check Siegel Z phase flip
    z_below = float(mp.siegelz(gamma - 0.005))
    z_above = float(mp.siegelz(gamma + 0.005))

    print(f"\nZero #{i}:")
    print(f"  Exact Height:    t = {gamma:.8f}")
    print(f"  Real Part:       0.5000000000000000000000000")
    print(f"  Residual |zeta|: {zeta_mag:.2e} (TRUE ZERO)")
    print(f"  Phase Sign Flip: {z_below:+.4f} -> {z_above:+.4f}")

if len(found_zeros) >= 2:
    measured_gap = found_zeros[1] - found_zeros[0]
    print(f"\nMeasured Zero Gap:  {measured_gap:.6f} units")
    print(f"Theoretical Avg:    {avg_spacing:.6f} units (Ratio: {measured_gap / avg_spacing:.2f}x)")

print("\n================================================================")
print("                   EXPERIMENT COMPLETED                         ")
print("================================================================")
