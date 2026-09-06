"""Opus D7.2 - INDEPENDENT reconstruction of the lower-envelope form R_T at L=7/10, T=120.

Written from my own derivation of W and R_T (see OPUS-ROUND-D7-RESULTS.md D7.1).
Deliberately different from d5_certify.py in every computational ingredient except the basis:
  * spherical Bessel j_n from Arb's own bessel_j(n+1/2) (hypergeometric), NOT a hand Taylor/Rayleigh scheme;
  * Gauss-Legendre with rho=1.9, K=56 nodes/panel, and an error constant DERIVED HERE from Bernstein's
    Chebyshev-coefficient theorem plus positivity of Gauss weights (no remembered ATAP constant);
  * pole vector from the closed form p_n = sqrt((2n+1)/(2L)) 2L i_n(L/2) with Arb's bessel_i, NOT numerical integration;
  * discarded-block bound by Cauchy-Schwarz (sum of squares), not (sum)^2.
Same normalized Legendre basis q_n(x)=sqrt((2n+1)/(2L)) P_n(x/L) so entrywise comparison is meaningful.
argv: parity(even|odd) [NE] [polesign(+1|-1)]
"""
import sys, json, time
from flint import arb, acb, ctx
ctx.prec = 256
t0 = time.time()

PAR   = sys.argv[1] if len(sys.argv) > 1 else 'even'
NE    = int(sys.argv[2]) if len(sys.argv) > 2 else 80
PSIGN = int(sys.argv[3]) if len(sys.argv) > 3 else 1
assert PAR in ('even', 'odd') and PSIGN in (1, -1)

L = arb(7)/10
T = 120
par = 0 if PAR == 'even' else 1
ns = [2*m + par for m in range(NE)]
ncut = ns[-1] + 2
pi = arb.pi()

# ---------- symbol ----------
# a(t) = Re psi(1/4 + i t/2) - log pi ; P(t) = sum 2 Lambda(n) n^{-1/2} cos(t log n), n in {2,3,4} (log n <= 2L)
PP = [(arb(2).log(),      2*arb(2).log()/arb(2).sqrt()),
      (arb(3).log(),      2*arb(3).log()/arb(3).sqrt()),
      (2*arb(2).log(),    2*arb(2).log()/2)]
assert all(u <= 2*L for u, _ in PP) and arb(5).log() > 2*L
B = sum((w for _, w in PP), arb(0))

NSHIFT = 8
def _psi(s):
    # psi(s) = psi(s+N) - sum_{k<N} 1/(s+k)  (recurrence psi(z+1)=psi(z)+1/z, applied N times).
    # Arb's digamma returns nan on the wide boxes used for the ellipse cover; the shifted argument is
    # well inside its working region.  N=8 chosen empirically; the identity is exact for any N.
    r = (s + NSHIFT).digamma()
    for k in range(NSHIFT): r = r - 1/(s + k)
    return r
def a_c(t):                      # analytic continuation, |Im t| < 1/2
    return (_psi(acb(arb(1)/4 + acb(0,1)*t/2)) + _psi(acb(arb(1)/4 - acb(0,1)*t/2)))/2 - acb(pi.log())
def Psi_c(t):
    return a_c(t) - sum((acb(w)*(acb(u)*t).cos() for u, w in PP), acb(0))

a0   = _psi(acb(arb(1)/4)).real - pi.log()
aT   = a_c(acb(T)).real
beta = aT - B
assert beta > 0, 'beta* not positive'
# sup_{0<=t<=T} |Psi - beta*| : a is increasing on t>0 (proved in the results file), |P| <= B
sup_psi = max((a0 - B - beta).abs_upper(), (aT + B - beta).abs_upper())
sup_psi = arb(sup_psi)

# ---------- basis / Fourier transform ----------
# F_n(t) = (2pi)^{-1/2} int q_n e^{-ixt} dx = (2pi)^{-1/2} sqrt((2n+1)/(2L)) 2L (-i)^n j_n(Lt)
# using int_{-1}^{1} e^{izs} P_n(s) ds = 2 i^n j_n(z).  Common phase (-i)^par drops out of |F|^2.
cmag = {n: ((2*n+1)/(2*L)).sqrt()*2*L/(2*pi).sqrt() for n in ns}
cpre = {n: cmag[n]*(-1)**(n//2) for n in ns}

def jn_arb(n, z):                # j_n(z) = sqrt(pi/(2z)) J_{n+1/2}(z), Arb's own Bessel
    return (acb(pi)/(2*z)).sqrt()*z.bessel_j(acb(n) + acb(arb(1)/2))

# ---------- quadrature: composite Gauss-Legendre, panels of width 1, K nodes ----------
# DERIVED error bound (no remembered constant): if g is analytic in the Bernstein ellipse E_rho of the
# panel and |g| <= M there, then with p the best degree-(2K-1) polynomial approximation,
#   |I(g) - I_K(g)| = |(I - I_K)(g - p)| <= (2 + 2)||g-p||_inf         (Gauss weights positive, sum 2)
#   ||g - p||_inf <= 2 M rho^{-(2K-1)}/(rho - 1)                       (Bernstein: |a_k| <= 2 M rho^{-k})
# hence |I - I_K| <= 8 M rho / ((rho-1) rho^{2K}) on [-1,1], times the panel half-width h.
K    = 56
rho  = arb(19)/10
h    = arb(1)/2
a_ax = h*(rho + 1/rho)/2
b_ax = h*(rho - 1/rho)/2
assert b_ax < arb(1)/2, 'ellipse crosses the digamma pole line |Im t| = 1/2'
Cq   = h*8*rho/((rho - 1)*rho**(2*K))
nodes = [arb.legendre_p_root(K, k, weight=True) for k in range(K)]
panels = list(range(T))

# nodal pass
Fv = {n: [] for n in ns}; Wv = []; Pv = []
for kp in panels:
    c = arb(kp) + h
    for (x, w) in nodes:
        t = c + h*x
        z = acb(t)*acb(L)
        for n in ns:
            Fv[n].append((acb(cpre[n])*jn_arb(n, z)).real)
        Pv.append(Psi_c(acb(t)).real - beta)
        Wv.append(w*h)
    if kp % 20 == 0: print(f'nodal panel {kp} t={time.time()-t0:.0f}s', flush=True)
NN = len(Wv)

# ellipse maxima.  |j_n(z)| <= e^{|Im z|}  from j_n(z) = (2 i^n)^{-1} int_{-1}^1 e^{izs} P_n(s) ds, |P_n|<=1.
MFc = {n: cmag[n]*(b_ax*L).exp() for n in ns}
NX, NY = 20, 24
MP = []
for kp in panels:
    c = arb(kp) + h; mp_ = arb(0)
    for jx in range(NX):
        xr = c - a_ax + a_ax*(2*jx+1)/NX
        for jy in range(NY):
            yr = -b_ax + b_ax*(2*jy+1)/NY
            box = acb(arb(xr.mid(), (a_ax/NX).abs_upper()), arb(yr.mid(), (b_ax/NY).abs_upper()))
            v = (Psi_c(box) - acb(beta)).abs_upper()
            assert arb(v).is_finite(), f'non-finite Psi box, panel {kp}'
            mp_ = max(mp_, v)
    MP.append(arb(mp_))
maxMP = max(MP)
print(f'ellipse pass done t={time.time()-t0:.0f}s maxMP={maxMP.str(8)} Cq={Cq.str(6)}', flush=True)

# matrix M_mn = 2 int_0^T (Psi - beta*) F_m F_n dt
G = {m: [Wv[k]*Pv[k]*Fv[m][k] for k in range(NN)] for m in ns}
sumMP = sum((MP[kp] for kp in panels), arb(0))
M = [[arb(0)]*NE for _ in range(NE)]; maxq = arb(0); maxrad = arb(0)
for i, m in enumerate(ns):
    Gm = G[m]
    for j in range(i, NE):
        n = ns[j]
        Fn = Fv[n]
        S = sum((Gm[k]*Fn[k] for k in range(NN)), arb(0))
        err = (Cq*sumMP*MFc[m]*MFc[n]).abs_upper()
        maxq = max(maxq, arb(err))
        M[i][j] = M[j][i] = 2*(S + arb(0, err))
        maxrad = max(maxrad, arb(M[i][j].rad()))
    if i % 20 == 0: print(f'row {i} t={time.time()-t0:.0f}s', flush=True)
print(f'matrix done t={time.time()-t0:.0f}s maxq={maxq.str(6)} maxrad={maxrad.str(6)} M00={M[0][0].str(20)}', flush=True)

# ---------- pole vector, closed form ----------
# p_n = <q_n, cosh(x/2)> (even) or <q_n, sinh(x/2)> (odd) = sqrt((2n+1)/(2L)) * 2L * i_n(L/2)
def in_arb(n, z):
    return (acb(pi)/(2*z)).sqrt()*z.bessel_i(acb(n) + acb(arb(1)/2))
y = L/2
p = [(((2*n+1)/(2*L)).sqrt()*2*L*in_arb(n, acb(y)).real) for n in ns]
normpN = sum((v*v for v in p), arb(0)).sqrt()

POLE = (1 if PAR == 'even' else -1)*PSIGN
A = [[M[i][j] + 2*POLE*p[i]*p[j] + (beta if i == j else arb(0)) for j in range(NE)] for i in range(NE)]

# ---------- certified lambda_min of the finite block ----------
import mpmath as mp
mp.mp.dps = 60
te = time.time()
Amid = mp.matrix([[mp.mpf(A[i][j].mid().str(75, radius=False)) for j in range(NE)] for i in range(NE)])
Emp, Vmp = mp.eigsy(Amid)
V  = [[arb(str(Vmp[i, j])) for j in range(NE)] for i in range(NE)]
AV = [[sum((A[i][k]*V[k][j] for k in range(NE)), arb(0)) for j in range(NE)] for i in range(NE)]
Bm = [[sum((V[k][i]*AV[k][j] for k in range(NE)), arb(0)) for j in range(NE)] for i in range(NE)]
VtV= [[sum((V[k][i]*V[k][j] for k in range(NE)), arb(0)) for j in range(NE)] for i in range(NE)]
gersh = [Bm[i][i].lower() - sum((Bm[i][j].abs_upper() for j in range(NE) if j != i), arb(0)) for i in range(NE)]
vtvmin = min(VtV[i][i].lower() - sum((VtV[i][j].abs_upper() for j in range(NE) if j != i), arb(0)) for i in range(NE))
vtvmax = max(VtV[i][i].upper() + sum((VtV[i][j].abs_upper() for j in range(NE) if j != i), arb(0)) for i in range(NE))
assert vtvmin > 0, 'V not certified invertible'
gmin = min(gersh)
lam_low = gmin/vtvmax if gmin > 0 else gmin/vtvmin      # correct direction for a negative Gershgorin min too
print(f'eigen step {time.time()-te:.1f}s lam_low={lam_low.str(15)} float eigs {[float(Emp[i]) for i in range(3)]}', flush=True)

# ---------- frozen sensitive direction (D7.3): exact 40-digit coefficient vector, rigorous score ----------
cvec = [arb(mp.nstr(Vmp[i, 0], 40)) for i in range(NE)]
nrm2 = sum((v*v for v in cvec), arb(0))
quad = sum((cvec[i]*sum((M[i][j]*cvec[j] for j in range(NE)), arb(0)) for i in range(NE)), arb(0))
pdot = sum((p[i]*cvec[i] for i in range(NE)), arb(0))
score = (quad + beta*nrm2 + 2*POLE*pdot*pdot)/nrm2

# ---------- infinite tails ----------
def dfact_odd(n):
    v = arb(1)
    for k in range(1, 2*n+2, 2): v *= k
    return v
xT = arb(T)*L
def sbar(n): return cmag[n] if False else ((2*n+1)/(2*L)).sqrt()*2*L/(2*pi).sqrt()*xT**n/dfact_odd(n)*(xT*xT/(2*(2*n+3))).exp()
s0 = sbar(ncut)
r1 = (xT*xT/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt()
assert r1 < 1
sum_s2 = s0*s0/(1 - r1*r1)                       # >= sum_{n>=ncut, step 2} sbar(n)^2
eps_D  = 2*T*sup_psi*sum_s2                      # Cauchy-Schwarz form
sum_c2 = sum((cmag[m]**2 for m in ns), arb(0))   # sup|F_m| <= cmag[m] since |j_m| <= 1
eps_C  = 2*T*sup_psi*sum_c2.sqrt()*sum_s2.sqrt()
def pbar(n): return ((2*n+1)/(2*L)).sqrt()*2*L*y**n/dfact_odd(n)*(y*y/(2*(2*n+3))).exp()
q0 = pbar(ncut); rp = (y*y/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt()
eps_p = (q0*q0/(1 - rp*rp)).sqrt()

# ---------- full-form Schur bound ----------
lam_lo = arb(lam_low.lower())
off    = arb((eps_C + 2*normpN*eps_p).upper())
d_low  = arb((beta - eps_D - 2*eps_p*eps_p).lower())
assert d_low > 0
mu = (lam_lo + d_low)/2 - (((d_low - lam_lo)/2)**2 + off*off).sqrt() if lam_lo > 0 else None

out = dict(auditor='Opus', parity=PAR, pole_sign_mutation=PSIGN, pole_term_sign_used=POLE, NE=NE, ncut=ncut,
           prec_bits=256, GL_nodes_per_panel=K, rho='1.9', ellipse_semiminor=b_ax.str(8), cover_boxes=[NX, NY],
           B=B.str(20), beta_star=beta.str(20), a0=a0.str(20), aT=aT.str(20), sup_psi_minus_beta=sup_psi.str(20),
           quadrature_constant_Cq=Cq.str(6), max_quadrature_error_bound=maxq.str(6), max_entry_radius=maxrad.str(6),
           maxMP=maxMP.str(8),
           M_entries={f'{ns[i]},{ns[j]}': M[i][j].str(22) for (i, j) in [(0,0),(0,1),(10,20),(1,1),(0,2),(79,79)] if i < NE and j < NE},
           norm_pN=normpN.str(15), p0=p[0].str(20),
           lambda0_finite_block_lower=lam_low.str(15), gershgorin_min=gmin.str(15),
           lambda_max_VtV_upper=vtvmax.str(20), lambda_min_VtV_lower=vtvmin.str(20),
           float_smallest_eigs=[float(Emp[i]) for i in range(4)],
           frozen_vector_score=score.str(15), frozen_vector_score_upper=arb(score.upper()).str(15),
           eps_D=eps_D.str(6), eps_C=eps_C.str(6), eps_p=eps_p.str(6),
           d_low=d_low.str(10), off_upper=off.str(6),
           full_form_lower_bound=(mu.lower().str(15) if mu is not None else None),
           schur_correction=((lam_lo - arb(mu.lower())).str(4) if mu is not None else None),
           runtime_s=time.time()-t0)
fn = f'opus_d7_{PAR}_NE{NE}_pole{POLE:+d}.json'
json.dump(out, open(fn, 'w'), indent=1)
print(json.dumps(out, indent=1))
