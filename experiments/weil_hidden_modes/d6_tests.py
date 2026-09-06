"""D6.3 adversarial tests T1, T3, T5, T6 (T4 in d6_sameform.py). Balls where stated; mpmath elsewhere (floating, independent implementation)."""
import json, subprocess, sys, random
from flint import arb, acb, ctx
import mpmath as mp
ctx.prec=192; mp.mp.dps=30
L=arb('7/10'); T=120; pi=arb.pi(); out={}
pp=[(arb(2).log(),2*arb(2).log()/arb(2).sqrt()),(arb(3).log(),2*arb(3).log()/arb(3).sqrt()),(2*arb(2).log(),2*arb(2).log()/2)]
def a_c(t):
    s1=acb(arb(1)/4)+acb(0,1)*t/2; s2=acb(arb(1)/4)-acb(0,1)*t/2
    return ((s1+1).digamma()-1/s1+(s2+1).digamma()-1/s2)/2-acb(pi.log())
def Psi_c(t): return a_c(t)-sum((acb(w)*(acb(u)*t).cos() for u,w in pp),acb(0))
# ---- T1: complex cross term. f1=q0 (even), f2=q1 (odd). F1 = c0 j0(tL) real even; F2 = -i c1 j1(tL) (imaginary, odd).
c0=(arb(1)/(2*L)).sqrt()*2*L/(2*pi).sqrt(); c1=(arb(3)/(2*L)).sqrt()*2*L/(2*pi).sqrt()
def F1(t): z=t*acb(L); return acb(c0)*z.sin()/z
def F2(t): z=t*acb(L); return -acb(0,1)*acb(c1)*(z.sin()/(z*z)-z.cos()/z)
t1=acb(1); lhs=abs(F1(t1)+acb(0,1)*F2(t1))**2; rhs=abs(F1(t1))**2+abs(F2(t1))**2
out['T1_pointwise_diff_at_t1']=str((lhs-rhs).real)
def cross(t,analytic):   # |F1+iF2|^2 - |F1|^2 - |F2|^2 = -2 Im(conj(F1) F2)
    return Psi_c(t)*(-2)*((F1(t).conjugate()*F2(t)).imag)
I=acb.integral(cross,acb(-T),acb(T),abs_tol=arb('1e-30'),rel_tol=arb('1e-30'),eval_limit=2000000,depth_limit=600)
out['T1_integrated_cross_over_[-T,T]']=str(I.real); out['T1_integrated_contains_zero']=bool(I.real.contains(0))
Ih=acb.integral(cross,acb(0),acb(T),abs_tol=arb('1e-30'),rel_tol=arb('1e-30'),eval_limit=2000000,depth_limit=600)
out['T1_half_integral_[0,T]_(nonzero_expected)']=str(Ih.real)
# pole: C0 = int q0 cosh(x/2), S1 = int q1 sinh(x/2)
q0=lambda x:(acb(1)/(2*acb(L))).sqrt(); q1=lambda x:(acb(3)/(2*acb(L))).sqrt()*x/acb(L)
C0=acb.integral(lambda x,a:q0(x)*(x/2).cosh(),acb(-L),acb(L)).real; S1=acb.integral(lambda x,a:q1(x)*(x/2).sinh(),acb(-L),acb(L)).real
fh_plus=acb(C0,S1); fh_minus=acb(C0,-S1)          # f=q0+i q1: int f e^{x/2} = C0 + i S1 ; int f e^{-x/2} = C0 - i S1
herm=2*(fh_plus*fh_minus.conjugate()).real; naive=2*(fh_plus*fh_minus); sep=2*C0*C0-2*S1*S1
out['T1_pole_hermitian_minus_sum_of_parities']=str(herm-sep); out['T1_pole_naive_minus_hermitian']=str((naive-acb(herm)).abs_upper())
# ---- T3: replay the D4 checker
r=subprocess.run([sys.executable,'d4_checker.py'],capture_output=True,text=True); out['T3_d4_checker']=r.stdout.strip().splitlines()[-1]
# ---- T5: independent floating evaluation of certified Legendre entries (mpmath Bessel/digamma, tanh-sinh panels)
even=json.load(open('d5_results_even_NE80_pole+1.json')); odd=json.load(open('d5_results_odd_NE80_pole-1.json'))
Lm=mp.mpf(7)/10; B=sum(2*mp.log(p)/mp.sqrt(p**k) for p,k in ((2,1),(3,1),(2,2)))
def a_m(t): return mp.re(mp.digamma(mp.mpf(1)/4+1j*t/2))-mp.log(mp.pi)
def Psi_m(t): return a_m(t)-sum(2*mp.log(p)/mp.sqrt(p**k)*mp.cos(t*k*mp.log(p)) for p,k in ((2,1),(3,1),(2,2)))
beta=a_m(T)-B
def Fm(n,t):
    z=t*Lm; jn=mp.besselj(n+mp.mpf(1)/2,z)*mp.sqrt(mp.pi/(2*z)) if z!=0 else (1 if n==0 else 0)
    return mp.sqrt((2*n+1)/(2*Lm))*2*Lm*jn/mp.sqrt(2*mp.pi)*(-1)**(n//2)
T5={}
for name,d in (('even',even),('odd',odd)):
    for key,val in d['cross_check_vs_acb_integral'].items():
        m,n=map(int,key.split(','))
        v=2*mp.quad(lambda t:(Psi_m(t)-beta)*Fm(m,t)*Fm(n,t),mp.linspace(0,T,121))
        cert=arb(val['new']); diff=abs(float(v)-float(cert.mid())) if False else (arb(str(v))-cert)
        T5[f"{name} ({m},{n})"]={"mpmath":mp.nstr(v,22),"certified":val['new'],"diff":diff.str(3),"inside_ball":bool(cert.contains(arb(str(v))))}
        print("T5",name,(m,n),T5[f"{name} ({m},{n})"],flush=True)
out['T5']=T5
# ---- T6: numerical sanity of the two analytic lemmas
random.seed(6); viol=0; worst=0
for _ in range(200):
    n=random.choice(range(0,159)); x=random.uniform(-90,90); y=random.uniform(-0.3,0.3); z=mp.mpc(x,y)
    jn=abs(mp.besselj(n+mp.mpf(1)/2,z)*mp.sqrt(mp.pi/(2*z))); ratio=float(jn/mp.exp(abs(y))); worst=max(worst,ratio); viol+=ratio>1
out['T6_strip_bound_violations']=viol; out['T6_strip_bound_worst_ratio']=worst
errs=[]
for _ in range(20):
    n=random.choice(range(0,40)); z=mp.mpc(random.uniform(0.1,3),random.uniform(-1,1))
    lhs=mp.quad(lambda s:mp.exp(z*s)*mp.legendre(n,s),[-1,1]); rhs=2*mp.besseli(n+mp.mpf(1)/2,z)*mp.sqrt(mp.pi/(2*z))
    errs.append(float(abs(lhs-rhs)))
out['T6_legendre_in_identity_max_err']=max(errs)
json.dump(out,open('d6_tests.json','w'),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
