"""Opus D7.1 normalization control - independent of Fable's d6_sameform.py.

Is the FREQUENCY-space form W(f) = Pi(f) + int_R Psi |F|^2 that I derived from the explicit formula the SAME
quadratic form as Codex's POSITION-space certified matrix (certified_results.json, 'authentic', 16 sine modes,
384-bit Arb)?  A wrong 2pi, a wrong factor 2 on the prime weights, or a wrong pole ordering shows at >= 1e-3.

Test: evaluate my form on Codex's basis, truncating the frequency integral at T_b, for three T_b.  The residual
must then fall like the analytic tail (|F_i| = O(t^-2), |Psi| = O(log t) => tail = O(log(T_b)/T_b^3)).
A T_b-independent residual would mean a normalization error.  Transforms re-derived here:
  a_i = i pi/(2L);  E(w) = (e^{2iwL}-1)/(iw)
  F_i(t)  = (2pi)^{-1/2} e^{iLt} (E(a_i-t) - E(-a_i-t)) / (2i sqrt L)
  fhat_i(c) = e^{-cL} a_i (1 - (-1)^i e^{2cL}) / (sqrt L (a_i^2+c^2))
  Pi_ij = fhat_i(1/2) fhat_j(-1/2) + fhat_j(1/2) fhat_i(-1/2)
Quadrature is a fixed oversampled composite Gauss-Legendre (half-period panels, 24 nodes); this control does not
need a certified error bound, only enough accuracy to separate 1e-3 from 1e-13, and node-count doubling is reported.
"""
import json, time
from flint import arb, acb, ctx
ctx.prec = 160
L = arb(7)/10
pi = arb.pi()
PP = [(arb(2).log(), 2*arb(2).log()/arb(2).sqrt()), (arb(3).log(), 2*arb(3).log()/arb(3).sqrt()),
      (2*arb(2).log(), 2*arb(2).log()/2)]
NSHIFT = 4
def _psi(s):
    r = (s + NSHIFT).digamma()
    for k in range(NSHIFT): r = r - 1/(s + k)
    return r
def Psi(t):
    tc = acb(t)
    a = (_psi(acb(arb(1)/4) + acb(0,1)*tc/2) + _psi(acb(arb(1)/4) - acb(0,1)*tc/2)).real/2 - pi.log()
    return a - sum((w*(u*t).cos() for u, w in PP), arb(0))
def Fi(i, t):
    a = i*pi/(2*L)
    def E(w):
        return ((acb(0,1)*w*2*L).exp() - 1)/(acb(0,1)*w)
    return (acb(0,1)*L*t).exp()*(E(acb(a) - t) - E(acb(-a) - t))/(acb(0,2)*L.sqrt()*(2*pi).sqrt())
def fhat(i, c):
    a = i*pi/(2*L)
    return (-c*L).exp()*a*(1 - (-1)**i*(2*c*L).exp())/(L.sqrt()*(a*a + c*c))

def gl(K):
    return [arb.legendre_p_root(K, k, weight=True) for k in range(K)]
def integrate(i, j, Tb, K, wpan):
    nodes = gl(K); h = wpan/2
    npan = int(float((Tb/wpan).mid()))
    tot = arb(0)
    for kp in range(npan):
        c = wpan*kp + h
        for (x, w) in nodes:
            t = c + h*x
            v = Fi(i, acb(t))*Fi(j, acb(t)).conjugate()
            tot += w*h*Psi(t)*v.real
    return 2*tot

codex = json.load(open('certified_results.json'))
ent = [r for r in codex['rows'] if r['model'] == 'authentic'][0]['entries']
wpan = pi/(2*L)                      # half oscillation period of the sine transforms
res = {}; t0 = time.time()
for (i, j) in [(1,1), (2,2), (1,2)]:
    pole = fhat(i, arb(1)/2)*fhat(j, -arb(1)/2) + fhat(j, arb(1)/2)*fhat(i, -arb(1)/2)
    theirs = arb(ent[i-1][j-1]) if ent[i-1][j-1] != '0' else arb(0)
    row = {"codex": (ent[i-1][j-1] if ent[i-1][j-1] != '0' else '0'), "pole": pole.str(18)}
    prev = None
    for Tb in (20000, 60000, 180000):
        main = integrate(i, j, arb(Tb), 24, wpan)
        mine = main + pole
        d = mine - theirs
        row[f"Tb={Tb}"] = {"mine": mine.str(20), "diff": d.str(4)}
        if prev is not None: row[f"shrink {prev[0]}->{Tb}"] = (prev[1]/d).str(6)
        prev = (Tb, d)
        print(i, j, Tb, 'diff', d.str(4), f'{time.time()-t0:.0f}s', flush=True)
    # node-count control at the smallest T_b: 24 vs 36 nodes must agree far below the diffs
    m24 = integrate(i, j, arb(20000), 24, wpan); m36 = integrate(i, j, arb(20000), 36, wpan)
    row["quadrature_selfcheck_24_vs_36_nodes"] = (m24 - m36).str(4)
    res[f"{i},{j}"] = row
    print(i, j, 'nodecheck', (m24-m36).str(4), flush=True)
res["rule"] = ("SAME FORM iff diff -> 0 at the O(log Tb / Tb^3) rate (predicted shrink 26.0 per 3x in Tb); "
               "a wrong 2pi / factor 2 / pole ordering leaves a Tb-independent residual >= 1e-3")
json.dump(res, open('opus_d7_sameform.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
