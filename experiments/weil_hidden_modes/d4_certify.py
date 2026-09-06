"""D4: interval-certified frequency reduction at L=0.7, even sector, T#=120, retained even Legendre n<=158. Arb throughout."""
import sys, json, time
sys.path.insert(0,"/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes")
from flint import arb, acb, ctx
from certify import ldl
from d4_checker import verdict
ctx.prec=128; t0=time.time()
L=arb('7/10'); T=arb(120); NE=int(sys.argv[1]) if len(sys.argv)>1 else 80; ns=[2*m for m in range(NE)]; ncut=ns[-1]+2   # first discarded even n
pi=arb.pi(); tol=arb('1e-25')
pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt()),(arb(3).log(),2*arb(3).log()/arb(3).sqrt()),(2*arb(2).log(),2*arb(2).log()/2)]
B=sum((w for _,w in pp),arb(0))
def a_c(t):  # analytic continuation of a(t)=Re psi(1/4+it/2)-log pi
    return (acb(arb(1)/4,0)+acb(0,1)*t/2).digamma()/2+(acb(arb(1)/4,0)-acb(0,1)*t/2).digamma()/2-acb(pi.log())
def Psi_c(t): return a_c(t)-sum((acb(w)*(acb(u)*t).cos() for u,w in pp),acb(0))
a0=arb(0)-arb.const_euler()-pi/2-3*arb(2).log()-pi.log()
aT=a_c(acb(T)).real; beta=aT-B
assert beta>0, beta
psi_lo=a0-B-beta; psi_hi=aT+B-beta; sup_psi=max(abs(psi_lo).abs_upper(),abs(psi_hi).abs_upper())
def F_c(n,t,analytic=False):  # unitary FT of q_n at complex t; entire, but computed via J_{n+1/2} and sqrt which have a branch cut on Re z<=0
    z=t*acb(L)
    if analytic and not (z.real > 0): return acb('nan')   # ball touches the cut: tell the integrator this evaluation is not analytic
    jn=(acb(pi)/(2*z)).sqrt()*z.bessel_j(acb(n+arb(1)/2))
    return acb((-1)**(n//2))*(acb((2*n+1))/(2*acb(L))).sqrt()*acb(L)*2*jn/acb(2*pi).sqrt()
eps0=arb('1e-30')  # integrate [eps0,T]; bound [0,eps0] by sup: |(Psi-beta)F_mF_n| <= sup_psi * s_m s_n with |F_n|<=c_n
cn=lambda n: ((2*n+1)/(2*L)).sqrt()*L*2/(2*pi).sqrt()   # sup_t |F_n(t)| using |j_n|<=1
M=[[arb(0)]*NE for _ in range(NE)]
for i,m in enumerate(ns):
    ti=time.time()
    for j in range(i,NE):
        n=ns[j]
        def integrand(t,analytic): return (Psi_c(t)-acb(beta))*F_c(m,t,analytic)*F_c(n,t,analytic)
        I=acb.integral(integrand,acb(eps0),acb(T),abs_tol=tol,rel_tol=tol,eval_limit=2000000,depth_limit=600)
        if not I.is_finite(): raise ArithmeticError(("unresolved",m,n))
        head=eps0*sup_psi*cn(m)*cn(n)
        val=2*(I.real+arb(0,head.abs_upper()))
        M[i][j]=M[j][i]=val
    print(f"row n={m} done in {time.time()-ti:.0f}s, first entry rad {M[i][i].rad()}",flush=True)
# pole vector p_n = 2*int_0^L q_n(x) cosh(x/2) dx (even n), rigorous
p=[]
for n in ns:
    def integ(x,analytic): return (acb((2*n+1))/(2*acb(L))).sqrt()*x.legendre_p(acb(n))* (x/2).cosh() if True else None
    # legendre_p on acb: use x/L scaling
    def integ2(x,analytic): return (acb((2*n+1))/(2*acb(L))).sqrt()*(x/acb(L)).legendre_p(acb(n))*(x/2).cosh()
    I=acb.integral(integ2,acb(0),acb(L),abs_tol=tol,rel_tol=tol); p.append(2*I.real)
normpN=sum((v*v for v in p),arb(0)).sqrt()
# A = M + 2 p p^T + beta I ; interval LDL lower bound lambda0
A=[[M[i][j]+2*p[i]*p[j]+(beta if i==j else 0) for j in range(NE)] for i in range(NE)]
lam0=None; cert=None
for k in (12,13,14,15,16):
    r=ldl(A,'1e-'+str(k))
    if r['status']=='MEASURED' and r['positive']: lam0=arb('1e-'+str(k)); cert=k; break
# tail bounds (B2-B4): s_n = c_n * x^n/(2n+1)!! * exp(x^2/(2(2n+3))), x=T L
x=T*L
def dfact_odd(n):  # (2n+1)!!
    v=arb(1)
    for k in range(1,2*n+2,2): v*=k
    return v
def s(n): return cn(n)*x**n/dfact_odd(n)*(x*x/(2*(2*n+3))).exp()
s0=s(ncut); ratio=(x*x/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt(); assert ratio<1
sum_s=s0/(1-ratio); sum_s2=s0*s0/(1-ratio*ratio)
eps_D=2*T*sup_psi*sum_s*sum_s
sum_cm2=sum((cn(m)**2 for m in ns),arb(0))
eps_C=2*T*sup_psi*sum_cm2.sqrt()*sum_s2.sqrt()
y=L/2  # cosh(x/2) Legendre coefficients: |p_n| <= sqrt((2n+1)/(2L)) * L*2 * i_n(y) bound, i_n(y)<= y^n/(2n+1)!! exp(y^2/(2(2n+3)))
def sp(n): return ((2*n+1)/(2*L)).sqrt()*L*2*y**n/dfact_odd(n)*(y*y/(2*(2*n+3))).exp()
sp0=sp(ncut); ratio_p=(y*y/((2*ncut+3)*(2*ncut+5)))*(arb(2*ncut+5)/(2*ncut+1)).sqrt(); eps_p=(sp0*sp0/(1-ratio_p*ratio_p)).sqrt()
f=lambda v: float(v.abs_upper()) if hasattr(v,'abs_upper') else float(v)
res=verdict(lam0 is not None, float(lam0) if lam0 else 0.0, eps_D=f(eps_D), eps_C=f(eps_C), eps_p=f(eps_p), beta=float(beta.lower()), norm_pN=f(normpN))
out={"NE":NE,"ncut":ncut,"prec_bits":128,"beta_star":beta.str(20),"sup_psi_minus_beta":str(sup_psi),"lambda0_certified":('1e-%d'%cert) if cert else None,
     "ldl_status_at_1e-13":ldl(A,'1e-13')['status'],"eps_D":eps_D.str(6),"eps_C":eps_C.str(6),"eps_p":eps_p.str(6),"norm_pN":normpN.str(12),
     "max_entry_radius":str(max(v.rad() for r in M for v in r)),"verdict":res,"runtime_s":time.time()-t0}
json.dump(out,open(f"d4_results_NE{NE}.json","w"),indent=1); print(json.dumps(out,indent=1))
