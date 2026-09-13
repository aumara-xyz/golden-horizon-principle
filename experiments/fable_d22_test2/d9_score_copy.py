"""Rigorous scalar scores on fixed polynomial waves, not an operator certificate."""
import json, sys, time
from pathlib import Path
from flint import arb, acb, ctx
ctx.prec = 320
ROOT = Path(__file__).resolve().parent
L = arb(7)/10
PI = arb.pi()
PP = [(arb(2).log(), 2*arb(2).log()/arb(2).sqrt()),
      (arb(3).log(), 2*arb(3).log()/arb(3).sqrt()),
      (2*arb(2).log(), arb(2).log())]
B = sum((w for a,w in PP), arb(0))
C = PP[0][1]/arb(2).sqrt() + (PP[1][1]+PP[2][1])/2

def upper(x): return arb(x.upper())
def absup(x): return arb(x.abs_upper())
def a(t): return acb(arb(1)/4,t/2).digamma().real - PI.log()
def endpoints(x):
    return {'lower_enclosure':arb(x.lower()).str(60), 'upper_enclosure':arb(x.upper()).str(60)}

def real_poly(b,x):
    """Legendre polynomial p(x) from unnormalized Legendre coefficients b."""
    u=x/L
    p0=arb(1)
    out=b[0]*p0
    if len(b)==1: return out
    p1=u
    out+=b[1]*p1
    for n in range(1,len(b)-1):
        p2=((2*n+1)*u*p1-n*p0)/(n+1)
        out+=b[n+1]*p2
        p0,p1=p1,p2
    return out

def shift_inner(b,shift,nodes_extra=0):
    if shift>=2*L: return arb(0)
    assert shift>=0
    K=len(b)+nodes_extra  # 2K-1 >=2deg(b)
    half=(2*L-shift)/2
    val=arb(0)
    for k in range(K):
        u,w=arb.legendre_p_root(K,k,weight=True)
        val+=w*real_poly(b,shift/2+half*u)*real_poly(b,-shift/2+half*u)
    return half*val

def diff_coeff(b):
    out=[arb(0)]*max(1,len(b)-1)
    for k in range(len(b)-1):
        out[k]=(2*k+1)/L*sum((b[n] for n in range(k+1,len(b),2)),arb(0))
    return out

def norm2(b): return sum((2*L*b[n]*b[n]/(2*n+1) for n in range(len(b))),arb(0))

def derivative_evidence(b):
    ev=[]
    for m in range(13):
        endp=sum(b,arb(0))
        endm=sum(((-1)**n*v for n,v in enumerate(b)),arb(0))
        ev.append(dict(m=m, boundary=upper(absup(endp)+absup(endm)), norm2=upper(norm2(b))))
        b=diff_coeff(b)
    return ev

def arch_tail_bounds(ev,T):
    """For t>=T>=128, 0<a(t)<=log(t); positive tail bounds for each IBP order."""
    T=arb(T)
    assert T>=128
    assert a(T)>0
    assert PI/T+1/(8*T*T)<(2*PI).log()
    out=[]
    for m in range(1,13):
        E=arb(0)
        for j in range(m):
            for k in range(m):
                p=j+k+2
                J=T**(1-p)*(T.log()/(p-1)+arb(1)/(p-1)**2)
                E+=ev[j]['boundary']*ev[k]['boundary']*J/PI
        H=ev[m]['norm2']*T.log()/T**(2*m)
        bound=upper((E.sqrt()+H.sqrt())**2)
        out.append((m,bound))
    return out

def pole(b,parity):
    y=L/2
    total=arb(0)
    for n,v in enumerate(b):
        if n%2!=parity: continue
        inn=(PI/(2*y)).sqrt()*acb(y).bessel_i(acb(arb(n)+arb(1)/2)).real
        total+=v*2*L*inn
    return (2 if parity==0 else -2)*total**2

def compact(b,parity,T,K=64):
    """Certified ∫_{-T}^T a|F|² and mass, unit panels, analytic ellipse bound."""
    t0=time.time()
    rho=arb(19)/10
    h=arb(1)/2
    aa=h*(rho+1/rho)/2
    bb=h*(rho-1/rho)/2
    delta=arb(1)/4-bb/2
    assert delta>0
    # psi(z)=-gamma-1/z+sum_{k>=1} z/[k(k+z)], Re z>=delta.
    # |psi(z)| <= 1+1/delta+2|z| since gamma<1 and sum1/k²<2.
    zmax=arb(1)/4+bb/2+(arb(T)+aa)/2
    Ma=1+1/delta+2*zmax+PI.log()
    Mf2=L/PI*norm2(b)*(2*L*bb).exp()
    Cq=h*8*rho/((rho-1)*rho**(2*K))
    err_mass=upper(2*T*Cq*Mf2)
    err_arch=upper(err_mass*Ma)
    nodes=[arb.legendre_p_root(K,k,weight=True) for k in range(K)]
    active=[(n,v*2*L/(2*PI).sqrt()*(-1)**(n//2)) for n,v in enumerate(b) if n%2==parity]
    arch=arb(0); mass=arb(0)
    for panel in range(T):
        centre=arb(panel)+h
        for x,w in nodes:
            t=centre+h*x
            z=acb(L*t)
            common=(PI/(2*L*t)).sqrt()
            H=sum((v*common*z.bessel_j(acb(arb(n)+arb(1)/2)).real for n,v in active),arb(0))
            val=2*h*w*H**2
            mass+=val
            arch+=val*a(t)
        if panel%128==0:
            print('compact',parity,T,'panel',panel,'seconds',round(time.time()-t0,1),flush=True)
    return arch+arb(0,err_arch), mass+arb(0,err_mass), err_arch, err_mass

def classify(base,tail):
    if tail is None or not tail.is_finite() or not tail>=0 or not base.is_finite():
        return 'UNVERIFIED'
    total=base+arb(tail/2,upper(tail/2))
    return 'POSITIVE' if total>0 else 'NEGATIVE' if total<0 else 'UNVERIFIED'

def controls():
    b0=[1/(2*L).sqrt()]
    b1=[arb(0),(arb(3)/(2*L)).sqrt()]
    sh=L/2
    c0=shift_inner(b0,sh)
    expected0=1-sh/(2*L)
    # Integrate 3*x*(x-a)/(2L³) exactly via endpoint primitive.
    primitive=lambda x: x**3/3-sh*x*x/2
    expected1=3/(2*L**3)*(primitive(L)-primitive(-L+sh))
    c1=shift_inner(b1,sh)
    d=diff_coeff([arb(0),arb(0),arb(1)])
    comp64=compact(b0,0,2,64)
    comp80=compact(b0,0,2,80)
    tests={
        'constant_shift_exact': (c0-expected0).contains(0),
        'linear_shift_exact': (c1-expected1).contains(0),
        'zero_overlap': shift_inner(b1,arb(2))==0,
        'touching_endpoints_encloses_zero': shift_inner(b1,2*L).contains(0),
        'P2_derivative': (d[1]-3/L).contains(0) and d[0]==0,
        'quadrature_64_80_overlap': comp64[0].overlaps(comp80[0]) and comp64[1].overlaps(comp80[1]),
        'missing_tail_refused': classify(arb(-1),None)=='UNVERIFIED',
        'negative_tail_refused': classify(arb(-1),arb(-1))=='UNVERIFIED',
        'nonfinite_tail_refused': classify(arb(-1),arb('nan'))=='UNVERIFIED',
        'crossing_interval_refused': classify(arb(-1),arb(2))=='UNVERIFIED',
        'negative_control': classify(arb(-2),arb(1))=='NEGATIVE',
        'positive_control': classify(arb(2),arb(1))=='POSITIVE',
    }
    assert all(tests.values()),tests
    (ROOT/'controls.json').write_text(json.dumps(tests,indent=2)+'\n')
    print('CONTROLS',tests,flush=True)

def main():
    if sys.argv[1]=='controls': return controls()
    assert all(json.loads((ROOT/'controls.json').read_text()).values())
    par=sys.argv[1]; parity=0 if par=='even' else 1
    frozen=json.loads((ROOT/('frozen_'+par+'.json')).read_text())
    assert frozen['parity']==par and all(n%2==parity for n in frozen['degrees'])
    b=[arb(0)]*(max(frozen['degrees'])+1)
    for n,c in zip(frozen['degrees'],frozen['coefficients']): b[n]=arb(c)*((2*n+1)/(2*L)).sqrt()
    nrm=norm2(b)
    assert nrm>0
    shifts=[shift_inner(b,shift)/nrm for shift,w in PP]
    checked=[shift_inner(b,shift,16)/nrm for shift,w in PP]
    assert all(x.overlaps(y) for x,y in zip(shifts,checked))
    arithmetic=sum((w*s for (a,w),s in zip(PP,shifts)),arb(0))
    pol=pole(b,parity)/nrm
    ev=derivative_evidence(b)
    trials=[]
    for T in (128,256,512,1024):
        A0,mass,errA,errM=compact(b,parity,T)
        A0/=nrm; mass/=nrm
        tails=[(m,upper(tail/nrm)) for m,tail in arch_tail_bounds(ev,T)]
        m,tail=min(tails,key=lambda pair:float(pair[1]))
        # Tail arch >= a(T)*tailmass, with tailmass >=0 by Plancherel.
        tm=upper(1-mass)
        masslow=max(arb(0),arb((1-mass).lower()))
        Atail_low=a(T)*masslow
        A=arb(A0.lower()+Atail_low.lower(),0).union(arb((A0+tail).upper()))
        W=A+pol-arithmetic
        thetas=['0','1e-15','1e-14','1e-13','1e-12','0.1','0.25','1']
        scores={th:W-arb(th)*(C-arithmetic) for th in thetas}
        signs={th:('POSITIVE' if v>0 else 'NEGATIVE' if v<0 else 'UNVERIFIED') for th,v in scores.items()}
        trial=dict(T=T, derivative_order=m,arch_compact=A0.str(30), arch_tail_lower=Atail_low.str(15),
                   arch_tail_upper=tail.str(15), all_tail_bounds={str(k):v.str(12) for k,v in tails},
                   tail_mass_interval=(1-mass).str(15),arch_full=A.str(30),W=W.str(30),
                   scores={th:v.str(30) for th,v in scores.items()},signs=signs,
                   score_endpoints={th:endpoints(v) for th,v in scores.items()},
                   component_endpoints={'archimedean':endpoints(A),'pole':endpoints(pol),
                                        'prime_sum':endpoints(arithmetic),'W':endpoints(W),
                                        'without_primes':endpoints(A+pol),
                                        'wrong_pole':endpoints(A-pol-arithmetic)},
                   wrong_pole_W=(A-pol-arithmetic).str(30),
                   without_prime_W=(A+pol).str(30),quadrature_error_arch=(errA/nrm).str(12))
        for th,e in trial['score_endpoints'].items():
            lo=arb(e['lower_enclosure']).lower()
            hi=arb(e['upper_enclosure']).upper()
            if signs[th]=='POSITIVE': assert lo>0
            if signs[th]=='NEGATIVE': assert hi<0
        trials.append(trial)
        print(par,'T',T,'tail',tail.str(6),'W',W.str(12),'signs',signs,flush=True)
        # Stop when the three preregistered large theta signs are resolved.
        if all(signs[th]=='NEGATIVE' for th in ('0.1','0.25','1')): break
    tiny=arb('1.031e-13')-arb('1e-14')*(C+B)
    assert tiny>0
    out=dict(parity=par,norm=nrm.str(30),B=B.str(30),c=C.str(30),
             prime_shift_correlations={str(n):s.str(30) for n,s in zip((2,3,4),shifts)},
             weighted_prime_terms={str(n):(s*w).str(30) for n,s,(a,w) in zip((2,3,4),shifts,PP)},
             prime_sum=arithmetic.str(30),pole=pol.str(30),trials=trials,
             D7_conditional_operator_margin_theta_1e14=tiny.str(25),
             note='Fixed-vector scalar interval results; not new all-vector certificate. Tiny-theta operator margin conditional on D7.')
    (ROOT/('scores_'+par+'.json')).write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__': main()
