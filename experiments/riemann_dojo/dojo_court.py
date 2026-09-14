"""AUKORA Riemann Dojo Court: Rigorous Interval Evaluation of Weil Form W(f).
Takes candidate wave coefficients, computes exact components with complete tails using Flint Arb,
and returns interval-certified receipts.
"""
import json, sys, time
from flint import arb, acb, ctx

ctx.prec = 320
PI = arb.pi()

# Primes and prime powers
PP_ALL = [
    (arb(2).log(), 2 * arb(2).log() / arb(2).sqrt()),
    (arb(3).log(), 2 * arb(3).log() / arb(3).sqrt()),
    (2 * arb(2).log(), arb(2).log()),  # 4 = 2^2, weight = 2*log(2)/sqrt(4) = log(2)
    (arb(5).log(), 2 * arb(5).log() / arb(5).sqrt()),
    (arb(7).log(), 2 * arb(7).log() / arb(7).sqrt()),
    (3 * arb(2).log(), 2 * arb(2).log() / arb(8).sqrt()),  # 8 = 2^3
    (2 * arb(3).log(), 2 * arb(3).log() / 3),              # 9 = 3^2
]

def a_func(t):
    return acb(arb(1)/4, t/2).digamma().real - PI.log()

def norm2(b, L):
    return sum((2 * L * b[n] * b[n] / (2*n + 1) for n in range(len(b))), arb(0))

def real_poly(b, x, L):
    u = x / L
    p0 = arb(1)
    out = b[0] * p0
    if len(b) == 1: return out
    p1 = u
    out += b[1] * p1
    for n in range(1, len(b) - 1):
        p2 = ((2*n + 1) * u * p1 - n * p0) / (n + 1)
        out += b[n + 1] * p2
        p0, p1 = p1, p2
    return out

def shift_inner(b, shift, L, K=None):
    if shift >= 2 * L: return arb(0)
    assert shift >= 0
    if K is None:
        K = max(64, len(b) + 8)
    half = (2 * L - shift) / 2
    val = arb(0)
    for k in range(K):
        u, w = arb.legendre_p_root(K, k, weight=True)
        val += w * real_poly(b, shift/2 + half*u, L) * real_poly(b, -shift/2 + half*u, L)
    return half * val

def diff_coeff(b, L):
    out = [arb(0)] * max(1, len(b) - 1)
    for k in range(len(b) - 1):
        out[k] = (2*k + 1) / L * sum((b[n] for n in range(k + 1, len(b), 2)), arb(0))
    return out

def derivative_evidence(b, L):
    ev = []
    curr_b = list(b)
    for m in range(13):
        endp = sum(curr_b, arb(0))
        endm = sum(((-1)**n * v for n, v in enumerate(curr_b)), arb(0))
        ev.append({
            'boundary': arb(abs(endp).abs_upper() + abs(endm).abs_upper()),
            'norm2': arb(norm2(curr_b, L).abs_upper())
        })
        curr_b = diff_coeff(curr_b, L)
    return ev

def arch_tail_bounds(ev, T):
    T_arb = arb(T)
    assert T >= 128
    out = []
    for m in range(1, 13):
        E = arb(0)
        for j in range(m):
            for k in range(m):
                p = j + k + 2
                J = T_arb**(1 - p) * (T_arb.log() / (p - 1) + arb(1) / (p - 1)**2)
                E += ev[j]['boundary'] * ev[k]['boundary'] * J / PI
        H = ev[m]['norm2'] * T_arb.log() / T_arb**(2*m)
        bound = arb((E.sqrt() + H.sqrt())**2).abs_upper()
        out.append((m, bound))
    return out

def pole_term(b, parity, L):
    y = L / 2
    total = arb(0)
    for n, v in enumerate(b):
        if n % 2 != parity: continue
        inn = (PI / (2*y)).sqrt() * acb(y).bessel_i(acb(arb(n) + arb(1)/2)).real
        total += v * 2 * L * inn
    return (2 if parity == 0 else -2) * total**2

def compact_integral(b, parity, T, L, K=64):
    rho = arb(19)/10
    h = arb(1)/2
    aa = h * (rho + 1/rho) / 2
    bb = h * (rho - 1/rho) / 2
    delta = arb(1)/4 - bb/2
    assert delta > 0
    zmax = arb(1)/4 + bb/2 + (arb(T) + aa) / 2
    Ma = 1 + 1/delta + 2*zmax + PI.log()
    Mf2 = L / PI * norm2(b, L) * (2 * L * bb).exp()
    Cq = h * 8 * rho / ((rho - 1) * rho**(2*K))
    err_mass = arb(2 * T * Cq * Mf2).abs_upper()
    err_arch = arb(err_mass * Ma).abs_upper()
    
    nodes = [arb.legendre_p_root(K, k, weight=True) for k in range(K)]
    active = [(n, v * 2 * L / (2 * PI).sqrt() * (-1)**(n // 2)) for n, v in enumerate(b) if n % 2 == parity]
    
    arch = arb(0)
    mass = arb(0)
    for panel in range(T):
        centre = arb(panel) + h
        for x, w in nodes:
            t = centre + h * x
            z = acb(L * t)
            common = (PI / (2 * L * t)).sqrt()
            H = sum((v * common * z.bessel_j(acb(arb(n) + arb(1)/2)).real for n, v in active), arb(0))
            val = 2 * h * w * H**2
            mass += val
            arch += val * a_func(t)
    return arch + arb(0, err_arch), mass + arb(0, err_mass)

def evaluate_wave(L_str, parity_str, degrees, coeffs_str, T_cutoff=256):
    L = arb(L_str)
    parity = 0 if parity_str == 'even' else 1
    max_deg = max(degrees)
    b = [arb(0)] * (max_deg + 1)
    for d, c in zip(degrees, coeffs_str):
        b[d] = arb(c) * ((2*d + 1) / (2 * L)).sqrt()
    
    nrm = norm2(b, L)
    assert nrm > 0
    
    visible_primes = [(u, w) for u, w in PP_ALL if u < 2 * L]
    shifts = [shift_inner(b, u, L) / nrm for u, w in visible_primes]
    prime_val = sum((w * s for (u, w), s in zip(visible_primes, shifts)), arb(0))
    pol_val = pole_term(b, parity, L) / nrm
    
    ev = derivative_evidence(b, L)
    arch_comp, mass = compact_integral(b, parity, T_cutoff, L)
    arch_comp /= nrm
    mass /= nrm
    
    tails = arch_tail_bounds(ev, T_cutoff)
    best_m, best_tail = min(tails, key=lambda pair: float(pair[1]))
    best_tail = arb(best_tail) / nrm
    
    mass_lower = max(arb(0), arb(1) - mass.abs_upper())
    a_tail_lower = a_func(arb(T_cutoff)) * mass_lower
    
    arch_lower = arch_comp.lower() + a_tail_lower.lower()
    arch_upper = (arch_comp + best_tail).abs_upper()
    
    W_lower = arch_lower + pol_val.lower() - prime_val.upper()
    W_upper = arch_upper + pol_val.upper() - prime_val.lower()
    
    is_negative = W_upper < 0
    is_positive = W_lower > 0
    
    return {
        'L': L_str,
        'parity': parity_str,
        'T_cutoff': T_cutoff,
        'norm2': str(nrm),
        'pole': str(pol_val),
        'prime_visible_sum': str(prime_val),
        'visible_primes_count': len(visible_primes),
        'arch_compact': str(arch_comp),
        'tail_bound': str(best_tail),
        'best_tail_deriv_order': best_m,
        'W_lower': str(W_lower),
        'W_upper': str(W_upper),
        'is_counterexample_negative': is_negative,
        'is_certified_positive': is_positive
    }

if __name__ == '__main__':
    # Self-test using D22 odd L=0.4 candidate
    test_L = '0.4'
    test_par = 'odd'
    test_degs = [1, 3, 5]
    test_coeffs = ['1.0', '0.1', '0.01']
    res = evaluate_wave(test_L, test_par, test_degs, test_coeffs, T_cutoff=128)
    print(json.dumps(res, indent=2))
