#!/usr/bin/env python3
"""D28 frozen-court driver: score one candidate at one cutoff, per case.

This is a parameterization wrapper, not a change to the court. It imports the
FROZEN dojo functions from riemann_dojo/dojo_court.py (the same imports the
frozen scorers use) and executes the frozen `run_T` arithmetic VERBATIM as
copied from court_frozen_score.py lines 33-59 and court_frozen_dojo.py's
evaluate_wave, with only (L, parity, cert constants, modes, coeffs, T) left
free. Frozen-file hashes are recorded in every receipt.

Usage: python3 court_score.py <case> <candidate.json> --T 160 [--T 1024]
Cases: l05-odd | l04-even
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import PP_ALL, compact_integral, derivative_evidence, norm2, pole_term, shift_inner, a_func
from flint import arb, ctx

ctx.prec = 256
HERE = Path(__file__).parent
FROZEN = ['court_frozen_dojo.py', 'court_frozen_score.py']

CASES = {
    'l05-odd': {
        'L': arb(1) / 2, 'parity': 1,
        'lam0': '0.000180934196848', 'eps_D': '1.045e-298', 'eps_C': '4.776e-146',
        'eps_p': '2.366e-957', 'norm_pN': '0.14524224', 'beta': '2.25703698',
        'default_cand': '/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_odd_L0.5.json',
    },
    'l05-even': {
        'L': arb(0.5), 'parity': 0,
        'lam0': '8.76931872434759E-7', 'eps_D': '6.93876438E-297', 'eps_C': '3.880130749E-145',
        'eps_p': '6.07546299E-954', 'norm_pN': '1.01049260536322', 'beta': '2.2570369777406411502431',
        'default_cand': '/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d28_construction_loop/candidate_l05_even_d30.json',
    },
    'l06-odd': {
        'L': arb(0.6), 'parity': 1,
        'lam0': '4.89029307909781E-7', 'eps_D': '6.83156111E-246', 'eps_C': '1.32897283E-119',
        'eps_p': '6.77274230E-932', 'norm_pN': '0.191451252668248', 'beta': '0.988468776545513195870299',
        'default_cand': '/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d28_construction_loop/candidate_l06_odd_d30.json',
    },
    'l06-even': {
        'L': arb(0.6), 'parity': 0,
        'lam0': '1.31162554371630E-9', 'eps_D': '3.19500354E-244', 'eps_C': '9.05883436E-119',
        'eps_p': '1.44936443E-928', 'norm_pN': '1.11204927146292', 'beta': '0.988468776545513195870299',
        'default_cand': '/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d28_construction_loop/candidate_l06_even_d30.json',
    },
    'l04-even': {
        'L': arb(2) / 5, 'parity': 0,
        'lam0': '0.000172308870206', 'eps_D': '1.44842e-360', 'eps_C': '5.04218e-177',
        'eps_p': '5.29556e-985', 'norm_pN': '0.900417861775', 'beta': '2.2570369777406411502',
        'default_cand': '/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_even_L0.4.json',
    },
}

def ell_for(case):
    lam0, eps_D, eps_C, eps_p = (arb(case[k]) for k in ('lam0', 'eps_D', 'eps_C', 'eps_p'))
    norm_pN, beta = arb(case['norm_pN']), arb(case['beta'])
    d = beta - eps_D - 2 * eps_p * eps_p
    coupling = eps_C + 2 * norm_pN * eps_p
    c2 = coupling * coupling
    s = lam0 + d
    disc = (s * s - 4 * (lam0 * d - c2)).sqrt()
    return (s - disc) / 2

def load_candidate(path, L):
    cand = json.loads(Path(path).read_text())
    modes = cand['modes']
    coeffs = [str(c) for c in cand['minimizer_frozen_40dig']]
    b = [arb(0)] * (max(modes) + 1)
    for dd, c in zip(modes, coeffs):
        b[dd] = arb(c) * ((2 * dd + 1) / (2 * L)).sqrt()
    return cand, b

def run_T(b, parity, L, T, K=64):
    nrm = norm2(b, L)
    visible = [(u, w) for u, w in PP_ALL if u < 2 * L]
    prime_sum = sum((w * shift_inner(b, u, L) for u, w in visible), arb(0))
    pol = pole_term(b, parity, L)
    ev = derivative_evidence(b, L)
    b_jump, D_norm = ev[0]['boundary'], ev[1]['norm2']
    arch, mass = compact_integral(b, parity, T, L, K=K)
    M_up = max(arb(0), nrm - mass.lower())
    M_lo = max(arb(0), nrm - mass.upper())
    C_T = (b_jump / arb.pi().sqrt() + (D_norm / arb(T)).sqrt()) ** 2
    M0 = min(M_up, C_T / arb(T))
    deltaT = arb.pi() / arb(T) + 1 / (8 * arb(T) ** 2)
    A_up = M0 * ((arb(T) / (2 * arb.pi())).log() + ((C_T / (M0 * arb(T))).log() + 1) + deltaT)
    A_lo = a_func(arb(T)) * M_lo
    W_lo = (arch.lower() + A_lo.lower() + pol.lower() - prime_sum.upper()) / nrm
    W_hi = (arch.upper() + A_up.upper() + pol.upper() - prime_sum.lower()) / nrm
    return {'T': T, 'W_lower': str(W_lo), 'W_upper': str(W_hi), 'A_tail_upper': str(A_up),
            'mass_upper': str(mass.upper()), 'b_jump': str(b_jump), 'D_norm': str(D_norm)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case', choices=list(CASES))
    ap.add_argument('candidate', nargs='?')
    ap.add_argument('--T', type=int, action='append', default=None)
    ap.add_argument('--out')
    args = ap.parse_args()
    case = CASES[args.case]
    L, parity = case['L'], case['parity']
    cand_path = args.candidate or case['default_cand']
    cand, b = load_candidate(cand_path, L)
    ell = ell_for(case)
    out = {'case': args.case, 'candidate_path': str(cand_path),
           'candidate_sha256': hashlib.sha256(Path(cand_path).read_bytes()).hexdigest(),
           'frozen_hashes': {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in FROZEN},
           'ell': str(ell), 'lam0': case['lam0']}
    print(f"ell = {str(ell)[:34]}", flush=True)
    for T in (args.T or [160]):
        t0 = time.time()
        r = run_T(b, parity, L, T)
        W_lo, W_hi = arb(r['W_lower']), arb(r['W_upper'])
        r['infimum_ratio'] = str(W_hi / ell)
        r['wave_ratio'] = str(W_hi / W_lo)
        r['wave_lower_ratio'] = str(W_lo / ell)
        r['gate_10pct_closed'] = bool(W_lo / ell < arb('1.1'))
        r['gate_10pct_strict'] = bool(W_hi / ell < arb('1.1'))
        r['seconds'] = round(time.time() - t0, 1)
        out[f'T{T}'] = r
        print(f"T={T}: W in [{str(W_lo)[:20]}, {str(W_hi)[:20]}] inf_ratio={r['infimum_ratio'][:10]} "
              f"wave_lo_ratio={r['wave_lower_ratio'][:10]} gate(lo<1.1)={r['gate_10pct_closed']} ({r['seconds']}s)", flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=1) + '\n')
        print(f"[receipt] {args.out}", flush=True)

if __name__ == '__main__':
    main()
