#!/usr/bin/env python3
"""D28 construct_candidate.py v0 -- baseline construction-rule optimizer.

This is the ONLY file the loop's proposer models may edit. It contains the
construction rule: how a candidate c is chosen for a case from the solution
space. Everything downstream (build verification, court scoring, gate) is
frozen.

v0 rule (baseline, no models): search over
  - boundary-constraint families: value + first k derivatives vanish at +-L
    (k = 0, 2, 4, 6),
  - smoothness penalties: lambda * (exact derivative Gram),
lambda grid, selected by the float proxy
    proxy_ratio = (c^T A c + A_up_float(c)) / ell
where A is the D22 verbatim build (T=160, NE=80) and A_up_float is the
mass-conditioned tail upper from b_jump, D_norm and the float tail mass.

Output: candidate JSONs in the D22 format + a summary table.
"""
import json, math, itertools
from pathlib import Path
import numpy as np
from scipy.special import spherical_jn, digamma, eval_legendre

T_BUILD = 1024  # build at the metric cutoff: the 160-1024 band contributes ~1e-5 to W
NE = 80
T_METRIC = 1024
K48 = 48
xg, wg = np.polynomial.legendre.leggauss(K48)
PPf = [(math.log(2), 2 * math.log(2) / math.sqrt(2)),
       (math.log(3), 2 * math.log(3) / math.sqrt(3)),
       (2 * math.log(2), math.log(2))]

# ---- frozen float basis for the tail-mass estimate (T_METRIC, K=64) ----
K64 = 64
xg64, wg64 = np.polynomial.legendre.leggauss(K64)

def a_t(t):
    return np.real(digamma(0.25 + 0.5j * np.asarray(t, dtype=complex))) - math.log(math.pi)

def build_A(L, parity, dtype=np.float64):
    pp = [(u, w) for u, w in PPf if u < 2 * L]
    B = sum(w for _, w in pp)
    ns = np.arange(parity, 2 * NE, 2)
    ts = np.concatenate([0.5 * xg + kp + 0.5 for kp in range(T_BUILD)])
    ws = np.concatenate([0.5 * wg for _ in range(T_BUILD)])
    beta = float(a_t(T_BUILD)) - B
    sym = a_t(ts) - sum(w * np.cos(u * ts) for u, w in pp) - beta
    F = np.array([np.sqrt((2 * n + 1) / (2 * L)) * 2 * L * spherical_jn(n, ts * L) / math.sqrt(2 * math.pi) * (-1) ** (n // 2)
                  for n in ns])
    F[~np.isfinite(F)] = 0.0
    A = 2.0 * (F * (ws * sym)) @ F.T + beta * np.eye(len(ns))
    xq, wq = np.polynomial.legendre.leggauss(200)
    x = L / 2 * xq + L / 2
    wx = L / 2 * wq
    hyp = np.cosh(x / 2) if parity == 0 else np.sinh(x / 2)
    p = np.array([2 * np.sum(wx * np.sqrt((2 * n + 1) / (2 * L)) * eval_legendre(n, x / L) * hyp) for n in ns])
    A += (-2 if parity == 1 else 2) * np.outer(p, p)
    return ns.astype(int), A.astype(dtype)

def deriv_gram(L, ns, dtype=np.float64):
    # b_n = c_n * s_n, s_n = sqrt((2n+1)/(2L)); d_k = (2k+1)/L * sum_{n>k, n-k even} b_n
    s = np.sqrt((2 * ns + 1) / (2 * L)).astype(dtype)
    N = len(ns)
    M = np.zeros((N, N), dtype=dtype)
    for k in range(N):
        for n in range(N):
            if ns[n] > ns[k] and (ns[n] - ns[k]) % 2 == 0:
                M[k, n] = (2 * ns[k] + 1) / L * s[n]
    dn = 2 * L / (2 * ns + 1)
    return M.T @ np.diag(dn) @ M

def constraint_matrix(L, ns, k_max):
    # f^(k)(+-L) with f = sum c_n s_n P_n(x/L): d^k/dx^k P_n(x/L) = L^-k P_n^(k)(x/L)
    s = np.sqrt((2 * ns + 1) / (2 * L))
    N = len(ns)
    rows = []
    for k in range(0, k_max + 1, 2):
        for xv in (1.0, -1.0):
            row = []
            for i, n in enumerate(ns):
                if k > n:
                    row.append(0.0)
                else:
                    der = math.factorial(n + k) / (2 ** k * math.factorial(k) * math.factorial(n - k))
                    val = der * (xv ** (n - k)) / (L ** k)
                    row.append(s[i] * val)
            rows.append(row)
    R = np.array(rows)
    norms = np.linalg.norm(R, axis=1)
    norms[norms == 0] = 1.0
    return R / norms[:, None]

def endpoint_values(L, ns, c):
    s = np.sqrt((2 * ns + 1) / (2 * L))
    fp = float(np.sum(c * s))
    fm = float(np.sum(c * s * ((-1.0) ** ns)))
    return fp, fm

def build_mass_gram(L, ns):
    ts = np.concatenate([0.5 * xg64 + kp + 0.5 for kp in range(T_METRIC)])
    ws = np.concatenate([0.5 * wg64 for _ in range(T_METRIC)])
    F = np.array([np.sqrt((2 * n + 1) / (2 * L)) * 2 * L * spherical_jn(n, ts * L) / math.sqrt(2 * math.pi) * (-1) ** (n // 2)
                  for n in ns])
    F[~np.isfinite(F)] = 0.0
    return 2.0 * (F * ws) @ F.T

def tail_upper_float(L, ns, c, mass_gram):
    fp, fm = endpoint_values(L, ns, c)
    b_jump = abs(fp) + abs(fm)
    s = np.sqrt((2 * ns + 1) / (2 * L))
    b = c * s
    bpad = np.zeros(int(ns[-1]) + 1)
    for i, n in enumerate(ns):
        bpad[n] = b[i]
    diff = np.array([(2 * k + 1) / L * np.sum(bpad[k + 1::2]) for k in range(len(bpad) - 1)])
    D_norm = float(np.sum(2 * L * diff ** 2 / (2 * np.arange(len(diff)) + 1)))
    C_T = (b_jump / math.sqrt(math.pi) + math.sqrt(D_norm / T_METRIC)) ** 2
    mass_full = float(c @ (mass_gram @ c))
    M_up = max(0.0, 1.0 - mass_full)
    M0 = min(M_up, C_T / T_METRIC)
    deltaT = math.pi / T_METRIC + 1 / (8 * T_METRIC ** 2)
    if M0 <= 0:
        return 0.0
    A_up = M0 * (math.log(T_METRIC / (2 * math.pi)) + (math.log(C_T / (M0 * T_METRIC)) + 1) + deltaT)
    return A_up

def construct(case_name, L, parity, ell):
    ns, A = build_A(L, parity)
    G = deriv_gram(L, ns)
    mass_gram = build_mass_gram(L, ns)
    results = []
    for k_max, lam in itertools.product([0, 2, 4, 6, 8], [0.0, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5]):
        C = constraint_matrix(L, ns, k_max)
        if k_max > 0:
            U, S, Vt = np.linalg.svd(C.astype(float))
            rank = int(np.sum(S > S[0] * 1e-10))
            Z = Vt[rank:].T
            if Z.shape[1] < 2:
                continue
            Az = Z.T @ (A + lam * G) @ Z
            wv, vv = np.linalg.eigh((Az + Az.T) / 2)
            v = vv[:, 0]
            c = Z @ v
        else:
            M = A + lam * G
            wv, vv = np.linalg.eigh((M + M.T) / 2)
            c = vv[:, 0]
            norm = np.linalg.norm(c)
            if norm > 0:
                c = c / norm
        c = np.asarray(c, dtype=float)
        score = float(c @ (A.astype(float) @ c))
        A_up = tail_upper_float(L, ns, c, mass_gram)
        a_T = float(a_t(T_METRIC))
        mass_full = float(c @ (mass_gram @ c))
        M_lo = max(0.0, 1.0 - mass_full)
        proxy_ratio = (score + a_T * M_lo + A_up) / ell
        fp, fm = endpoint_values(L, ns, c)
        results.append({'k_max': k_max, 'lam': lam, 'score': score, 'A_up': A_up,
                        'proxy_ratio': proxy_ratio, 'b_jump': abs(fp) + abs(fm), 'c': c.copy()})
    results.sort(key=lambda r: r['proxy_ratio'])
    return ns, A, results

def save_candidate(outdir, name, L, parity, ns, A, r, ell, filename):
    fp, fm = endpoint_values(L, ns, r['c'])
    ns_list = [int(n) for n in ns]
    doc = {
        'L': L, 'parity': 'odd' if parity == 1 else 'even',
        'T_select': T_METRIC, 'NE': NE,
        'constraint': f"value and first {r['k_max']} derivatives vanish at +-L" if r['k_max'] else 'none',
        'smoothness_lambda': r['lam'],
        'reduced_min_unconstrained': float(np.linalg.eigvalsh(A.astype(float))[0]),
        'reduced_min_selected': r['score'],
        'proxy_ratio': r['proxy_ratio'],
        'ratio': r['proxy_ratio'],
        'boundary_residual': abs(fp) + abs(fm),
        'ell': ell,
        'modes': ns_list,
        'minimizer_frozen_40dig': [repr(float(x)) for x in r['c']],
    }
    p = Path(outdir) / filename
    p.write_text(json.dumps(doc, indent=1) + '\n')
    return p

def main():
    HERE = Path(__file__).parent
    cases = {
        'l05-odd': {'L': 0.5, 'parity': 1, 'ell': 0.000180934196848},
        'l04-even': {'L': 0.4, 'parity': 0, 'ell': 0.000172308870206},
    }
    for name, case in cases.items():
        ns, A, results = construct(name, case['L'], case['parity'], case['ell'])
        print(f"=== {name} (ell={case['ell']}) ===")
        print(f"{'k_max':>5} {'lambda':>9} {'score':>22} {'A_up':>11} {'proxy_ratio':>12} {'b_jump':>10}")
        for r in results[:8]:
            print(f"{r['k_max']:>5} {r['lam']:>9.0e} {r['score']:>22.15f} {r['A_up']:>11.3e} {r['proxy_ratio']:>12.6f} {r['b_jump']:>10.2e}")
        best = results[0]
        p = save_candidate(HERE, name, case['L'], case['parity'], ns, A, best, case['ell'],
                           f'candidate_{name.replace("-", "_")}_v0.json')
        print(f"[saved] {p.name}  proxy_ratio={best['proxy_ratio']:.6f}\n", flush=True)

if __name__ == '__main__':
    main()
