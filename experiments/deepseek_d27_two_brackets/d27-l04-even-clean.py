#!/usr/bin/env python3
"""D26 Task 2 move (a): rescore the SAME frozen wave with the mass-conditioned
tail at cutoff 1024; compute the certified infimum floor ell from the visible
cert JSON via the 2x2 Schur, then the infimum ratios at T=512 and T=1024."""
import json, sys, time, hashlib, math
from pathlib import Path

sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import PP_ALL, compact_integral, derivative_evidence, norm2, pole_term, shift_inner, a_func
from flint import arb, ctx

ctx.prec = 256
HERE = Path('/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d26_bracket')
CAND = Path('/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_even_L0.4.json')
CERT = HERE / 'd26_cert_visible_L05_odd_L0.5_T160_N160.json'

cert = json.loads(CERT.read_text())
lam0 = arb('0.000180934196848')          # certified eigenbound (printed value; radius negligible vs d)
eps_D = arb('1.045e-298')              # rounded UP from the printed interval
eps_C = arb('4.776e-146')
eps_p = arb('2.366e-957')
norm_pN = arb('0.14524224')            # upper-rounded
beta = arb('2.25703698')               # from beta_star, upper-rounded
d = beta - eps_D - 2 * eps_p * eps_p
coupling = eps_C + 2 * norm_pN * eps_p
c2 = coupling * coupling
# smaller root of (lam0 - mu)(d - mu) = c2
s = lam0 + d
disc = (s * s - 4 * (lam0 * d - c2)).sqrt()
ell = (s - disc) / 2
print(f"ell = {str(ell)[:40]}", flush=True)

cand_text = CAND.read_text()
cand = json.loads(cand_text)
L = arb(2) / 5  # D27: L=0.4 even
modes = cand['modes']
coeffs = [str(c) for c in cand['minimizer_frozen_40dig']]
b = [arb(0)] * (max(modes) + 1)
for dd, c in zip(modes, coeffs):
    b[dd] = arb(c) * ((2 * dd + 1) / (2 * L)).sqrt()
nrm = norm2(b, L)
visible = [(u, w) for u, w in PP_ALL if u < 2 * L]
prime_sum = sum((w * shift_inner(b, u, L) for u, w in visible), arb(0))
pol = pole_term(b, 0, L)
ev = derivative_evidence(b, L)
b_jump, D_norm = ev[0]['boundary'], ev[1]['norm2']

def run_T(T, K=64):
    arch, mass = compact_integral(b, 0, T, L, K=K)
    M_up = max(arb(0), nrm - mass.lower())
    M_lo = max(arb(0), nrm - mass.upper())
    C_T = (b_jump / arb.pi().sqrt() + (D_norm / arb(T)).sqrt()) ** 2
    M0 = min(M_up, C_T / arb(T))
    deltaT = arb.pi() / arb(T) + 1 / (8 * arb(T) ** 2)
    A_up = M0 * ((arb(T) / (2 * arb.pi())).log() + ((C_T / (M0 * arb(T))).log() + 1) + deltaT)
    A_lo = a_func(arb(T)) * M_lo
    W_lo = (arch.lower() + A_lo.lower() + pol.lower() - prime_sum.upper()) / nrm
    W_hi = (arch.upper() + A_up.upper() + pol.upper() - prime_sum.lower()) / nrm
    return W_lo, W_hi, A_up

out = {'wave': 'd22_cand2_odd_L0.4', 'candidate_sha256': hashlib.sha256(cand_text.encode()).hexdigest(),
       'ell': str(ell), 'lam0': str(lam0), 'eps_D': str(eps_D), 'eps_C': str(eps_C), 'eps_p': str(eps_p),
       'norm_pN': str(norm_pN), 'beta': str(beta), 'coupling': str(coupling)}
for T in (512, 1024):
    t0 = time.time()
    W_lo, W_hi, A_up = run_T(T)
    r_wave = W_hi / W_lo
    r_inf = W_hi / ell
    print(f"T={T}: W in [{str(W_lo)[:22]}, {str(W_hi)[:22]}] A_tail_up={str(A_up)[:18]} "
          f"wave_ratio={str(r_wave)[:12]} inf_ratio={str(r_inf)[:12]} ({time.time()-t0:.0f}s)", flush=True)
    out[f'T{T}'] = {'W_lower': str(W_lo), 'W_upper': str(W_hi), 'A_tail_upper': str(A_up),
                    'wave_ratio': str(r_wave), 'infimum_ratio': str(r_inf),
                    'gate_10pct_closed': bool(r_inf < arb('1.1'))}
(HERE / 'd27-l04-even-bracket.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps({k: v.get('infimum_ratio') if isinstance(v, dict) else v for k, v in out.items()}, indent=1)[:600])
