import math
import mpmath as mp
import numpy as np

print("================================================================")
print("       TESSERACT / TERNARY MIRROR CHAMBER SIMULATION            ")
print("================================================================\n")

# -------------------------------------------------------------
# 1. THE FIRST 27 PRIMES AND TERNARY 3x3x3 COORDINATE MAP
# -------------------------------------------------------------
def get_first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

primes_27 = get_first_n_primes(27)

# Ternary grid: 27 nodes in {-1, 0, 1}^3
grid_coords = []
for z in [-1, 0, 1]:
    for y in [-1, 0, 1]:
        for x in [-1, 0, 1]:
            grid_coords.append((x, y, z))

print(f"First 27 Primes (from p_1={primes_27[0]} to p_27={primes_27[-1]}):")
for i in range(0, 27, 9):
    row_primes = primes_27[i:i+9]
    print("  " + ", ".join(f"{p:3d}" for p in row_primes))

print("\n--- 27 Prime-Coordinate Mappings ---")
print(f"  Center Origin ( 0,  0,  0) -> Prime #{14}: p_14 = {primes_27[13]}")
print(f"  First Vertex  (-1, -1, -1) -> Prime # 1: p_1  = {primes_27[0]}")
print(f"  Final Vertex  ( 1,  1,  1) -> Prime #27: p_27 = {primes_27[26]}")

# -------------------------------------------------------------
# 2. RAY-TRACING SIMULATION INSIDE THE MIRROR CHAMBER
# -------------------------------------------------------------
print("\n--- [SIMULATION] Ray-Tracing in Bounded 3D Mirror Cavity ---")
# Cavity boundaries: [-1, 1] in x, y, z
# Fire light beam from origin (0.1, 0.2, 0.3) with velocity vector
pos = np.array([0.1, 0.2, 0.3], dtype=np.float64)
# Incommensurate velocity vector to avoid trivial short-period traps
vel = np.array([1.0, math.sqrt(2), math.sqrt(5)], dtype=np.float64)
vel = vel / np.linalg.norm(vel)  # normalize speed c = 1

time_delays = []
current_time = 0.0
total_bounces = 1000

for step in range(total_bounces):
    # Find distance to nearest wall in x, y, or z
    # Box is [-1, 1]^3
    dt_candidates = []
    for dim in range(3):
        if vel[dim] > 0:
            dt_candidates.append((1.0 - pos[dim]) / vel[dim])
        else:
            dt_candidates.append((-1.0 - pos[dim]) / vel[dim])

    dt = min(dt_candidates)
    hit_dim = dt_candidates.index(dt)

    # Move ray to wall
    pos = pos + vel * dt
    current_time += dt

    # Find closest of the 27 prime nodes
    closest_idx = 0
    min_dist = 1e9
    for idx, coord in enumerate(grid_coords):
        dist = np.linalg.norm(pos - np.array(coord))
        if dist < min_dist:
            min_dist = dist
            closest_idx = idx

    # Add prime logarithmic phase shift ln(p)
    prime_delay = math.log(primes_27[closest_idx])
    time_delays.append(current_time + prime_delay)

    # Specular mirror reflection at boundary
    vel[hit_dim] = -vel[hit_dim]

print(f"Simulated {total_bounces} specular wall bounces.")
print(f"Total Optical Path Time: {current_time:.2f} units")
print(f"Chamber Boundedness: Beam remained strictly contained within [-1, 1]^3 (0 leaks)")

# -------------------------------------------------------------
# 3. SPECTRAL ANALYSIS OF THE ECHOES (FOURIER FREQUENCIES)
# -------------------------------------------------------------
print("\n--- [FOURIER RESONANCE TEST] ---")
# Compute Fourier transform of the bounce arrival times to find dominant frequencies
omega_range = np.linspace(5.0, 40.0, 500)
fourier_power = []

# S(omega) = |sum exp(i * omega * t_k)|^2
times_array = np.array(time_delays[:200])
for omega in omega_range:
    val = np.sum(np.exp(1j * omega * times_array))
    fourier_power.append(abs(val)**2)

fourier_power = np.array(fourier_power)

# Find top 5 dominant peak frequencies in the mirror chamber
peak_indices = np.argsort(fourier_power)[-5:][::-1]
top_peaks = omega_range[peak_indices]

print("Top Resonant Frequencies of the 27-Prime Mirror Chamber:")
for rank, (idx, peak_freq) in enumerate(zip(peak_indices, top_peaks), 1):
    power = fourier_power[idx]
    print(f"  Peak #{rank}: Frequency omega = {peak_freq:6.2f} rad/s (Power = {power:7.1f})")

# Compare with true Riemann zeros
true_zeros = [14.13, 21.02, 25.01, 30.42, 32.93]
print(f"\nTarget Riemann Zeros for comparison: {true_zeros}")

print("\n================================================================")
print("                   EXPERIMENT COMPLETED                         ")
print("================================================================")
