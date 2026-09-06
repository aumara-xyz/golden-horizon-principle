"""D5: parity-aware copy of d4_certify_v2.py (run 4 kept unchanged). argv: NE K parity(even|odd) polesign(+1|-1).
D4 run 3: interval-certified frequency reduction at L=0.7, even sector, T#=120, 80 even Legendre modes (n<=158).
Differences from d4_certify.py (runs 1-2, kept): (i) spherical Bessel j_n by elementary ball-friendly forms (Taylor series with
rigorous tail for |z|<n, Rayleigh forward recurrence from sin/cos for |z|>=n); (ii) own certified composite Gauss-Legendre with
Bernstein-ellipse error bound (Trefethen ATAP Thm 19.3) instead of acb.integral, whose Bessel enclosures on wide balls were the
run-1/2 bottleneck. Everything is arb/acb ball arithmetic; nodes/weights are Arb's rigorous legendre_p_root enclosures."""
import sys, json, time
sys.path.insert(0,"/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes")
from flint import arb, acb, ctx
from certify import ldl
from d4_checker import verdict
ctx.prec=192; t0=time.time()
L=arb('7/10'); T=120; NE=int(sys.argv[1]) if len(sys.argv)>1 else 80; ns=[2*m+(1 if (len(sys.argv)>3 and sys.argv[3]=='odd') else 0) for m in range(NE)]; ncut=ns[-1]+2
K=int(sys.argv[2]) if len(sys.argv)>2 else 48
PAR=sys.argv[3] if len(sys.argv)>3 else 'even'; PSIGN=int(sys.argv[4]) if len(sys.argv)>4 else 1
assert PAR in ('even','odd') and PSIGN in (1,-1)      # GL nodes per unit panel
J=6                                               # boxes covering the Bernstein-ellipse bounding rectangle
rho=arb(2); h=arb(1)/2; a_ax=h*(rho+1/rho)/2; b_ax=h*(rho-1/rho)/2   # ellipse semi-axes 0.625, 0.375 (< 0.5 = nearest digamma pole)
pi=arb.pi()
pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt()),(arb(3).log(),2*arb(3).log()/arb(3).sqrt()),(2*arb(2).log(),2*arb(2).log()/2)]
B=sum((w for _,w in pp),arb(0))
def _psi(sv): return (sv+1).digamma()-1/sv        # exact identity; shifted argument avoids pole-adjacent wrapping on wide boxes
def a_c(t):
    s1=acb(arb(1)/4)+acb(0,1)*t/2; s2=acb(arb(1)/4)-acb(0,1)*t/2
    return (_psi(s1)+_psi(s2))/2-acb(pi.log())
def Psi_c(t): return a_c(t)-sum((acb(w)*(acb(u)*t).cos() for u,w in pp),acb(0))
a0=arb(0)-arb.const_euler()-pi/2-3*arb(2).log()-pi.log()
aT=a_c(acb(T)).real; beta=aT-B; assert beta>0
psi_lo=a0-B-beta; psi_hi=aT+B-beta; sup_psi=max(abs(psi_lo).abs_upper(),abs(psi_hi).abs_upper())
TAIL=arb('1e-62')
def dfact_odd(n):
    v=arb(1)
    for k in range(1,2*n+2,2): v*=k
    return v
DF={}
def DFn(n):
    if n not in DF: DF[n]=dfact_odd(n)
    return DF[n]
def jn_series(n,z):
    """j_n(z)=z^n/(2n+1)!! * sum_k (-z^2/2)^k/(k! (2n+3)(2n+5)...(2n+2k+1)), tail bounded rigorously."""
    R=z.abs_upper(); x=R*R/(2*(2*n+3)); ex=x.exp()
    s=acb(1); term=acb(1); q=-z*z/2; k=0; fact=arb(1); xp=arb(1)
    while True:
        k+=1; term=term*q/(k*(2*n+2*k+1)); s+=term
        fact*=k+1; xp*=x
        bound=xp*x/fact*ex          # sum_{j>k} x^j/j! <= x^{k+1}/(k+1)! e^x
        if bound<TAIL or k>2000: break
    s+=acb(arb(0,bound.abs_upper()),arb(0,bound.abs_upper()))
    return z**n/DFn(n)*s
# Rayleigh closed form j_n(z) = a_n(u) sin z + b_n(u) cos z, u=1/z, a_n,b_n exact-integer polynomials from
# a_{n+1} = (2n+1) u a_n - a_{n-1} (same for b); a_0=u, b_0=0, a_1=u^2, b_1=-u. Horner on a box wraps only linearly in n
# (the forward recurrence on wide boxes wrapped exponentially: run 3, kept).
def _polys(nmax):
    A=[[0,1],[0,0,1]]; Bq=[[0],[0,-1]]
    for k in range(1,nmax):
        def step(P,Pm):
            q=[0]+[(2*k+1)*c for c in P]
            q+= [0]*(len(Pm)-len(q))
            for i,c in enumerate(Pm): q[i]-=c
            return q
        A.append(step(A[k],A[k-1])); Bq.append(step(Bq[k],Bq[k-1]))
    return A,Bq
POLA,POLB=_polys(max(ns[-1],160)+1)
def horner(P,u):
    acc=acb(0)
    for c in reversed(P): acc=acc*u+c
    return acc
def jn_closed(n,z):
    u=1/z; return horner(POLA[n],u)*z.sin()+horner(POLB[n],u)*z.cos()
def jn_all(nmax,z):
    """dict n->j_n(z) for even n<=nmax: closed form while n<=|z|, series beyond (the series has no cancellation there)."""
    R=z.abs_upper(); out={}
    for n in range(nmax%2,nmax+1,2):
        out[n]=jn_closed(n,z) if n<=R else jn_series(n,z)
    return out
cn_pref={n:((2*n+1)/(2*L)).sqrt()*L*2/(2*pi).sqrt()*(-1)**(n//2) for n in ns}   # n//2 = n/2 (even) or (n-1)/2 (odd)
def F_all(t):  # dict n->F_n(t) at complex/real t
    js=jn_all(ns[-1],t*acb(L)); return {n:acb(cn_pref[n])*js[n] for n in ns}
# closed-form vs series consistency on a wide box (the run-3 failure mode)
for n in (20,60,100):
    zb=acb(arb(84,0.1),arb(0,0.26)); print(f'box check n={n} closed |j|<= {jn_closed(n,zb).abs_upper()} series |j|<= {jn_series(n,zb).abs_upper()}',flush=True)
# self-test of j_n against Arb's bessel_j on narrow balls
for (n,zt) in [(0,3.3),(2,0.7),(10,12.5),(40,20.0),(80,84.0),(158,50.0),(158,84.0),(60,84.0),(100,84.0),(84,84.0)]:
    z=acb(zt); ref=(acb(pi)/(2*z)).sqrt()*z.bessel_j(acb(n+arb(1)/2)); mine=jn_all(n,z)[n]
    assert ref.overlaps(mine), (n,zt,ref,mine)
    print(f"selftest j_{n}({zt}) ok, rad {mine.rad()}", flush=True)
# nodes/weights (rigorous) on [-1,1]
nodes=[arb.legendre_p_root(K,k,weight=True) for k in range(K)]
Cq=arb(64)/15*h*rho**(-2*K)/(rho*rho-1)   # per-panel quadrature error factor, times M_rho
panels=list(range(T))
# pass 1: nodal values
Fv={n:[] for n in ns}; Pv=[]; Wv=[]
for kp in panels:
    c=arb(kp)+h
    for (x,w) in nodes:
        t=c+h*x; tt=acb(t)
        Fs=F_all(tt)
        for n in ns: Fv[n].append(Fs[n].real)
        Pv.append(Psi_c(tt).real-beta); Wv.append(w*h)
    if kp%10==0: print(f"nodal pass panel {kp} t={time.time()-t0:.0f}s",flush=True)
# pass 2: ellipse maxima. |F_n(z)| <= |c_n| e^{|Im z| L} on the strip |Im z|<=b (Poisson integral, DLMF 10.54.2, |P_n|<=1);
# the run-3/4a box evaluations (recurrence, then Horner closed form) wrapped by 1e10-1e19 for n ~ |z| and are replaced by this bound.
# |Psi-beta| is still bounded by Arb on a box cover of the bounding rectangle, now with the shifted-digamma identity.
MF={n:[abs(cn_pref[n])*(b_ax*L).exp() for kp in panels] for n in ns}; MP=[]
for kp in panels:
    c=arb(kp)+h; mp=arb(0)
    for j in range(J):
        xr=-a_ax+a_ax*(2*j+1)/J
        for v in range(4):
            yr=-b_ax+b_ax*(2*v+1)/4; sub=acb(c+arb(xr,(a_ax/J).abs_upper()), arb(yr,(b_ax/4).abs_upper()))
            mp=max(mp,(Psi_c(sub)-acb(beta)).abs_upper())
    MP.append(mp)
print(f"ellipse pass done t={time.time()-t0:.0f}s; max MP {max(MP)}, MF[158] {MF[ns[-1]][0]}",flush=True)
# assemble M_mn = 2*int_0^T (Psi-beta) F_m F_n  with rigorous quadrature error balls
G={m:[Wv[i]*Pv[i]*Fv[m][i] for i in range(len(Wv))] for m in ns}
M=[[arb(0)]*NE for _ in range(NE)]; maxq=arb(0)
for i,m in enumerate(ns):
    for j in range(i,NE):
        n=ns[j]
        S=sum((G[m][k]*Fv[n][k] for k in range(len(Wv))),arb(0))
        err=sum((Cq*MP[kp]*MF[m][kp]*MF[n][kp] for kp in panels),arb(0)).abs_upper()
        maxq=max(maxq,err)
        M[i][j]=M[j][i]=2*(S+arb(0,err))
print(f"matrix assembled t={time.time()-t0:.0f}s; max quadrature error {maxq}; M00={M[0][0].str(15)}",flush=True)
# cross-check three entries against the run-1/2 black-box integrator (wide radii, but must overlap)
def F_old(n,t,analytic=False):
    z=t*acb(L)
    if analytic and not (z.real>0): return acb('nan')
    return acb(cn_pref[n])*(acb(pi)/(2*z)).sqrt()*z.bessel_j(acb(n+arb(1)/2))
xchk={}
for (i,j) in [(0,0),(0,1),(min(10,NE-1),min(20,NE-1))]:
    m,n=ns[i],ns[j]
    def integrand(t,analytic): return (Psi_c(t)-acb(beta))*F_old(m,t,analytic)*F_old(n,t,analytic)
    I=acb.integral(integrand,acb(arb('1e-30')),acb(T),abs_tol=arb('1e-25'),rel_tol=arb('1e-25'),eval_limit=2000000,depth_limit=600)
    head=arb('1e-30')*sup_psi*abs(cn_pref[m])*abs(cn_pref[n]); old=2*(I.real+arb(0,head.abs_upper()))
    xchk[f"{m},{n}"]={"new":M[i][j].str(20),"old":old.str(20),"overlap":bool(old.overlaps(M[i][j]))}
    print("xcheck",m,n,xchk[f"{m},{n}"],flush=True)
# pole vector
tol=arb('1e-40'); p=[]
for n in ns:
    def integ2(x,analytic): return (acb((2*n+1))/(2*acb(L))).sqrt()*(x/acb(L)).legendre_p(acb(n))*((x/2).cosh() if PAR=='even' else (x/2).sinh())
    I=acb.integral(integ2,acb(0),acb(L),abs_tol=tol,rel_tol=tol); p.append(2*I.real)
normpN=sum((v*v for v in p),arb(0)).sqrt()
POLE=(1 if PAR=='even' else -1)*PSIGN
A=[[M[i][j]+2*POLE*p[i]*p[j]+(beta if i==j else 0) for j in range(NE)] for i in range(NE)]
lam0=None; cert=None; statuses={}
for k in (12,13,14,15,16,17,18):
    r=ldl(A,'1e-'+str(k)); statuses['1e-%d'%k]=r['status']+('/positive' if r.get('positive') else '')
    if r['status']=='MEASURED' and r['positive'] and lam0 is None: lam0=arb('1e-'+str(k)); cert=k
r0=ldl(A,'0')
# Eigenbasis Gershgorin certificate (rigorous for ANY real invertible V): lambda_min(A) >= min_i Gersh_i(V^T A V) / lambda_max(V^T V).
# Naive interval LDL fails here because cond(A) ~ 1e14 amplifies the 1e-22 radii past the 1e-13 pivots (kept as UNVERIFIED above).
import mpmath as mp; mp.mp.dps=60; te=time.time()
Amid=mp.matrix([[mp.mpf(A[i][j].mid().str(70,radius=False)) for j in range(NE)] for i in range(NE)])
Emp,Vmp=mp.eigsy(Amid)
V=[[arb(str(Vmp[i,j])) for j in range(NE)] for i in range(NE)]
AV=[[sum((A[i][k]*V[k][j] for k in range(NE)),arb(0)) for j in range(NE)] for i in range(NE)]
Bm=[[sum((V[k][i]*AV[k][j] for k in range(NE)),arb(0)) for j in range(NE)] for i in range(NE)]
VtV=[[sum((V[k][i]*V[k][j] for k in range(NE)),arb(0)) for j in range(NE)] for i in range(NE)]
gersh=[Bm[i][i].lower()-sum((Bm[i][j].abs_upper() for j in range(NE) if j!=i),arb(0)) for i in range(NE)]
vtvmin=min(VtV[i][i].lower()-sum((VtV[i][j].abs_upper() for j in range(NE) if j!=i),arb(0)) for i in range(NE))
assert vtvmin>0, 'V not certified invertible'
gmin=min(gersh); vtvmax=max(VtV[i][i].upper()+sum((VtV[i][j].abs_upper() for j in range(NE) if j!=i),arb(0)) for i in range(NE))
lam_low=gmin/vtvmax; maxoff=max(Bm[i][j].abs_upper() for i in range(NE) for j in range(NE) if i!=j)
eig_cert={"lambda_min_lower_bound":lam_low.str(12),"gershgorin_min":gmin.str(12),"lambda_max_VtV_upper":vtvmax.str(20),"lambda_min_VtV_lower_(invertibility)":vtvmin.str(20),
          "max_offdiag_VtAV":str(maxoff),"approx_smallest_eigs_float":[float(Emp[i]) for i in range(3)],"seconds":time.time()-te}
print("eigen-Gershgorin certificate:",eig_cert,flush=True)
if lam_low>0 and (lam0 is None or lam_low>lam0): lam0=arb(lam_low.lower()); cert='eig'
# tail bounds B2-B4 (identical to runs 1-2)
x=arb(T)*L
cn=lambda n: ((2*n+1)/(2*L)).sqrt()*L*2/(2*pi).sqrt()
def s(n): return cn(n)*x**n/dfact_odd(n)*(x*x/(2*(2*n+3))).exp()
s0=s(ncut); ratio=(x*x/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt(); assert ratio<1 or NE<20
sum_s=s0/(1-ratio); sum_s2=s0*s0/(1-ratio*ratio)
eps_D=2*T*sup_psi*sum_s*sum_s
sum_cm2=sum((cn(m)**2 for m in ns),arb(0)); eps_C=2*T*sup_psi*sum_cm2.sqrt()*sum_s2.sqrt()
y=L/2
def sp(n): return ((2*n+1)/(2*L)).sqrt()*L*2*y**n/dfact_odd(n)*(y*y/(2*(2*n+3))).exp()
sp0=sp(ncut); ratio_p=(y*y/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt(); eps_p=(sp0*sp0/(1-ratio_p*ratio_p)).sqrt()
f=lambda v: float(v.abs_upper())
res=verdict(lam0 is not None, float(lam0) if lam0 else 0.0, eps_D=f(eps_D), eps_C=f(eps_C), eps_p=f(eps_p), beta=float(beta.lower()), norm_pN=f(normpN))
out={"run":5,"parity":PAR,"pole_sign_mutation":PSIGN,"pole_term_sign_used":POLE,"NE":NE,"ncut":ncut,"prec_bits":192,"GL_nodes_per_unit_panel":K,"rho":2,"cover_boxes":J,"beta_star":beta.str(20),
     "sup_psi_minus_beta":str(sup_psi),"lambda0_certified":(lam0.lower().str(12) if lam0 is not None else None),"certified_by":('eigenbasis-Gershgorin' if cert=='eig' else ('interval-LDL' if cert else None)),"eigen_certificate":eig_cert,"ldl_statuses":statuses,
     "ldl_at_0_positive":r0.get('positive'),"eps_D":eps_D.str(6),"eps_C":eps_C.str(6),"eps_p":eps_p.str(6),"norm_pN":normpN.str(12),
     "max_entry_radius":str(max(v.rad() for r in M for v in r)),"max_quadrature_error_bound":str(maxq),
     "verdict":res,"cross_check_vs_acb_integral":xchk,"runtime_s":time.time()-t0}
json.dump(out,open(f"d5_results_{PAR}_NE{NE}_pole{POLE:+d}.json","w"),indent=1); print(json.dumps(out,indent=1))
