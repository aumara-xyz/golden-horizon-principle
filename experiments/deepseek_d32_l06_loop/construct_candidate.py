#!/usr/bin/env python3
"""D28 construct_candidate.py v4 -- construction-rule optimizer.

Strategy:
  - Same frozen float basis (NE=80) and A-matrix construction as v3.
  - Add a direct penalty on the tail-mass upper bound C_T (which controls
    A_up = M0 * log(...)).  C_T = (b_jump/sqrt(pi) + sqrt(D_norm/T))^2.
  - Add a penalty on the in-band mass deficit M_lo = 1 - c^T M c, which
    directly multiplies a_T in the proxy.
  - Use a log-spaced grid for all penalty weights to cover a wider range.
  - For each (k_max, penalties) combination, take the eigenvector of the
    penalised matrix and evaluate the *honest* proxy (score + a_T*M_lo + A_up).
  - Emit the candidate with the lowest honest proxy.

The key insight from v3 results: the proxy at T=1024 is already very close
to the gate threshold (~1.10 for l05-odd, ~1.07 for l04-even), but the court
at T=160 shows the wave_lo ratio is already passing.  The bottleneck is the
inf_ratio (which uses A_up).  So we need to simultaneously:
  1. Keep the in-band score low (eigenvalue of A).
  2. Keep the tail mass deficit M_lo small (high in-band mass).
  3. Keep C_T small (small b_jump and D_norm).

We penalise all three components directly.
"""
import json, math, itertools
from pathlib import Path
import numpy as np
from scipy.special import spherical_jn, digamma, eval_legendre

T_BUILD = 1024
NE = 80
T_METRIC = 1024
K48 = 48
xg, wg = np.polynomial.legendre.leggauss(K48)
PPf = [(math.log(2), 2 * math.log(2) / math.sqrt(2)),
       (math.log(3), 2 * math.log(3) / math.sqrt(3)),
       (2 * math.log(2), math.log(2))]

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


def build_mass_gram(L, ns):
    ts = np.concatenate([0.5 * xg64 + kp + 0.5 for kp in range(T_METRIC)])
    ws = np.concatenate([0.5 * wg64 for _ in range(T_METRIC)])
    F = np.array([np.sqrt((2 * n + 1) / (2 * L)) * 2 * L * spherical_jn(n, ts * L) / math.sqrt(2 * math.pi) * (-1) ** (n // 2)
                  for n in ns])
    F[~np.isfinite(F)] = 0.0
    return 2.0 * (F * ws) @ F.T


def endpoint_values(L, ns, c):
    s = np.sqrt((2 * ns + 1) / (2 * L))
    fp = float(np.sum(c * s))
    fm = float(np.sum(c * s * ((-1.0) ** ns)))
    return fp, fm


def compute_D_norm(L, ns, c):
    s = np.sqrt((2 * ns + 1) / (2 * L))
    b = c * s
    bpad = np.zeros(int(ns[-1]) + 1)
    for i, n in enumerate(ns):
        bpad[int(n)] = b[i]
    diff = np.array([(2 * k + 1) / L * np.sum(bpad[k + 1::2]) for k in range(len(bpad) - 1)])
    D_norm = float(np.sum(2 * L * diff ** 2 / (2 * np.arange(len(diff)) + 1)))
    return D_norm


def tail_upper_float(L, ns, c, mass_gram):
    fp, fm = endpoint_values(L, ns, c)
    b_jump = abs(fp) + abs(fm)
    D_norm = compute_D_norm(L, ns, c)
    C_T = (b_jump / math.sqrt(math.pi) + math.sqrt(D_norm / T_METRIC)) ** 2
    mass_full = float(c @ (mass_gram @ c))
    M_up = max(0.0, 1.0 - mass_full)
    M0 = min(M_up, C_T / T_METRIC)
    deltaT = math.pi / T_METRIC + 1 / (8 * T_METRIC ** 2)
    if M0 <= 0:
        return 0.0
    A_up = M0 * (math.log(T_METRIC / (2 * math.pi)) + (math.log(C_T / (M0 * T_METRIC)) + 1) + deltaT)
    return A_up


def constraint_matrix(L, ns, k_max):
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
                    der = math.factorial(int(n) + k) / (2 ** k * math.factorial(k) * math.factorial(int(n) - k))
                    val = der * (xv ** (int(n) - k)) / (L ** k)
                    row.append(s[i] * val)
            rows.append(row)
    R = np.array(rows, dtype=float)
    if len(R) == 0:
        return np.eye(N, dtype=float)
    norms = np.linalg.norm(R, axis=1)
    norms[norms == 0] = 1.0
    return R / norms[:, None]


def construct(case_name, L, parity, ell):
    ns, A = build_A(L, parity)
    mass_gram = build_mass_gram(L, ns)
    a_T = float(a_t(T_METRIC))
    N = len(ns)

    # Precompute endpoint vectors for penalty
    s = np.sqrt((2 * ns + 1) / (2 * L))
    p_plus = s.copy()
    p_minus = s * ((-1.0) ** ns)
    Pe = np.outer(p_plus, p_plus) + np.outer(p_minus, p_minus)

    # D_norm quadratic form: D_norm = c^T Dm c where Dm is built from the
    # structure of the derivative norm.  We build it once.
    max_n = int(ns[-1])
    Dm = np.zeros((N, N), dtype=float)
    for k in range(max_n):
        coef = 2.0 * (2 * k + 1) / L
        idx = [i for i in range(N) if ns[i] > k and ((ns[i] - k) % 2) == 1]
        if not idx:
            continue
        for i in idx:
            for j in idx:
                Dm[i, j] += coef
    # D_norm = sum_k 2*(2k+1)/L * (sum_{n>k, n-k odd} s_n c_n)^2
    # = c^T [sum_k 2*(2k+1)/L * v_k v_k^T] c  where v_k[i] = s_i if ns[i]>k and (ns[i]-k)%2==1 else 0
    # But we already have Dm as the sum of coef * (indicator vectors outer products)
    # Actually Dm as built above is: Dm[i,j] = sum_k coef_k * 1_{i in idx_k} * 1_{j in idx_k}
    # Then c^T Dm c = sum_k coef_k * (sum_{i in idx_k} c_i)^2
    # But we need (sum s_i c_i)^2, so we need to incorporate s:
    # D_norm = c^T (diag(s) Dm diag(s)) c
    Dm = np.diag(s) @ Dm @ np.diag(s)

    # Mass deficit penalty: M_lo = 1 - c^T M c.  We penalise -c^T M c (i.e. reward mass).
    # Equivalently, add -mu_m * M to the matrix being minimised (since we want to maximise c^T M c).
    # But that can make the matrix non-PSD.  Instead, we penalise (1 - c^T M c)^2 approximated
    # by penalising -c^T M c linearly (since c is unit-norm, c^T M c <= 1, so 1 - c^T M c >= 0).
    # Adding -mu_m * M to W and minimising c^T W c will push c^T M c up.

    k_max_grid = [0, 2, 4, 6, 8, 10, 12]
    # Log-spaced grids for penalty weights
    lam_grid = [0.0, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    mu_D_grid = [0.0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    mu_e_grid = [0.0, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    mu_m_grid = [0.0, 1e-4, 1e-3, 1e-2, 0.1, 0.5]

    results = []
    count = 0
    for k_max in k_max_grid:
        C = constraint_matrix(L, ns, k_max)
        if k_max > 0:
            U, S, Vt = np.linalg.svd(C.astype(float))
            rank = int(np.sum(S > S[0] * 1e-10))
            Z = Vt[rank:].T
            if Z.shape[1] < 2:
                continue
            ZtAZ = Z.T @ A @ Z
            ZtDZ = Z.T @ Dm @ Z
            ZtPeZ = Z.T @ Pe @ Z
            ZtMZ = Z.T @ mass_gram @ Z
        else:
            Z = np.eye(N)
            ZtAZ = A.copy()
            ZtDZ = Dm.copy()
            ZtPeZ = Pe.copy()
            ZtMZ = mass_gram.copy()

        for lam, mu_D, mu_e, mu_m in itertools.product(lam_grid, mu_D_grid, mu_e_grid, mu_m_grid):
            # W = A + lam*G (we skip G for speed, focus on the tail penalties)
            # Actually let's include a small smoothness term to avoid pathological solutions
            # But G is expensive to build each time; let's skip it and rely on the other penalties.
            W = ZtAZ.copy()
            if mu_D > 0:
                W += mu_D * ZtDZ
            if mu_e > 0:
                W += mu_e * ZtPeZ
            if mu_m > 0:
                W -= mu_m * ZtMZ  # reward in-band mass
            W = (W + W.T) / 2
            try:
                wv, vv = np.linalg.eigh(W)
            except np.linalg.LinAlgError:
                continue
            v = vv[:, 0]
            c = Z @ v
            nrm = float(np.linalg.norm(c))
            if nrm < 1e-15:
                continue
            c = c / nrm
            c = np.asarray(c, dtype=float)

            score = float(c @ (A.astype(float) @ c))
            mass_full = float(c @ (mass_gram @ c))
            M_lo = max(0.0, 1.0 - mass_full)
            A_up = tail_upper_float(L, ns, c, mass_gram)
            proxy_ratio = (score + a_T * M_lo + A_up) / ell

            fp, fm = endpoint_values(L, ns, c)
            b_jump = abs(fp) + abs(fm)
            D_norm = compute_D_norm(L, ns, c)

            results.append({
                'k_max': k_max, 'lam': lam, 'mu_D': mu_D, 'mu_e': mu_e, 'mu_m': mu_m,
                'score': score, 'A_up': A_up, 'M_lo': M_lo,
                'proxy_ratio': proxy_ratio,
                'b_jump': b_jump, 'D_norm': D_norm,
                'mass_full': mass_full,
                'c': c.copy(),
            })
            count += 1

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
        'd_norm_penalty': r['mu_D'],
        'endpoint_penalty': r['mu_e'],
        'mass_reward': r['mu_m'],
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
        'l06-odd': {'L': 0.6, 'parity': 1, 'ell': 4.89029307909781e-7},
        'l06-even': {'L': 0.6, 'parity': 0, 'ell': 1.31162554371630e-9},
    }
    for name, case in cases.items():
        ns, A, results = construct(name, case['L'], case['parity'], case['ell'])
        print(f"=== {name} (ell={case['ell']}) ===")
        print(f"{'k_max':>5} {'lam':>9} {'mu_D':>9} {'mu_e':>9} {'mu_m':>7} {'score':>18} {'A_up':>10} {'M_lo':>10} {'proxy':>10} {'b_jump':>9} {'D_norm':>9}")
        for r in results[:10]:
            print(f"{r['k_max']:>5} {r['lam']:>9.0e} {r['mu_D']:>9.0e} {r['mu_e']:>9.0e} {r['mu_m']:>7.0e} "
                  f"{r['score']:>18.12f} {r['A_up']:>10.3e} {r['M_lo']:>10.4e} {r['proxy_ratio']:>10.6f} "
                  f"{r['b_jump']:>9.2e} {r['D_norm']:>9.2e}")
        best = results[0]
        p = save_candidate(HERE, name, case['L'], case['parity'], ns, A, best, case['ell'],
                           f'candidate_{name.replace("-", "_")}_v4.json')
        print(f"[saved] {p.name}  proxy_ratio={best['proxy_ratio']:.6f}\n", flush=True)


if __name__ == '__main__':
    main()