"""Independent analytic-correlation evaluation; convergence, not certification."""
import json
from pathlib import Path
import mpmath as m


def correlation(i, j, u, L):
    if (i+j) % 2 or u >= 2*L:
        return m.mpf(0)
    a, b, length = i*m.pi/(2*L), j*m.pi/(2*L), 2*L-u
    def integral(c, phase):
        return length*m.cos(phase) if c == 0 else (
            m.sin(c*length+phase)-m.sin(phase))/c
    def directed(a, b):
        return (integral(a-b, a*u)-integral(a+b, a*u))/(2*L)
    return (directed(a,b)+directed(b,a))/2


def pole(i, c, L):
    a = i*m.pi/(2*L)
    return m.exp(-c*L)/m.sqrt(L)*a*(1-(-1)**i*m.exp(2*c*L))/(a*a+c*c)


def arithmetic(L, shift):
    if shift is None:
        return []
    out = []
    for p in range(2, int(m.ceil(m.exp(2*L/shift)))+1):
        if any(p % q == 0 for q in range(2, int(p**0.5)+1)):
            continue
        k = 1
        while k*m.log(p)*shift < 2*L:
            out.append((k*m.log(p)*shift, 2*m.log(p)/m.power(p,m.mpf(k)/2)))
            k += 1
    return out


def matrices(L, N, order):
    nodes, weights = m.gauss_quadrature(order, 'legendre')
    nodes = [L*(v+1) for v in nodes]
    weights = [L*v for v in weights]
    a, alt = m.matrix(N), m.matrix(N)
    for i in range(1,N+1):
        for j in range(i,N+1):
            if (i+j) % 2:
                continue
            d = m.mpf(i == j)
            gs = [correlation(i,j,u,L) for u in nodes]
            poles = pole(i,m.mpf('.5'),L)*pole(j,m.mpf('-.5'),L)+pole(j,m.mpf('.5'),L)*pole(i,m.mpf('-.5'),L)
            v = poles-(m.euler+m.log(4*m.pi)+m.log(m.tanh(L)))*d
            v += m.fsum(w*(d-m.exp(u/2)*g)/m.sinh(u) for u,w,g in zip(nodes,weights,gs))
            v2 = poles-(m.euler+m.log(m.pi)+m.log(1-m.exp(-4*L)))*d
            v2 += m.fsum(w*2*(m.exp(-2*u)*d-m.exp(-u/2)*g)/(1-m.exp(-2*u)) for u,w,g in zip(nodes,weights,gs))
            a[i-1,j-1] = a[j-1,i-1] = v
            alt[i-1,j-1] = alt[j-1,i-1] = v2
    return a, m.norm(a-alt)


def minimum(a):
    return m.eigsy(a, eigvals_only=True)[0]


def diagnostic(w, N):
    w = w[:N,:N]
    a, c, d = w[:4,:4], w[:4,4:], w[4:,4:]
    schur = a-c*(d**-1)*c.T
    out = dict(minimum=minimum(w), visible_minimum=minimum(a),
               hidden_minimum=minimum(d), schur_minimum=minimum(schur))
    out['schur_visible_ratio'] = out['schur_minimum']/out['visible_minimum']
    return {k:m.nstr(v,m.mp.dps-10) for k,v in out.items()}


def run():
    results = []
    for precision in (80,160):
        m.mp.dps = precision
        L = m.mpf('.7')
        for order in (64,128):
            arch, discrepancy = matrices(L,16,order)
            for model, shift in [('arch_only',None),('shift_plus',m.mpf('1.1')),
                                 ('shift_minus',m.mpf('.9')),('authentic',m.mpf(1))]:
                w = arch.copy()
                for u, weight in arithmetic(L,shift):
                    for i in range(1,17):
                        for j in range(i,17):
                            v = weight*correlation(i,j,u,L)
                            w[i-1,j-1] -= v
                            if i != j:
                                w[j-1,i-1] -= v
                row = dict(precision=precision,order=order,model=model,
                           arch_formula_difference=m.nstr(discrepancy,65),
                           restrictions={str(n):diagnostic(w,n) for n in (8,12,16)})
                results.append(row)
                print(json.dumps(row),flush=True)
    Path(__file__).with_name('high_precision_results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    run()
