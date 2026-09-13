"""D21.1 repairs (Astra/Codex review of D21). Uses the frozen trial-2 vectors from d21_results.json; no reselection.
(1) crossing-zero rejection: a quantity is 'certainly >= 0' only if its lower endpoint >= 0; (2) cutoffs separated: selector T vs scoring cutoff 128;
(3) ledger entry for the failed I4 sign prediction; (4) complex-cosine growth allowance cosh(u*b) in the compact prime-integral error;
exported rigorous endpoints; positive-and-negative survivor rechecks at K=80/400 bits; W>=R_128 monotonicity route."""
import json, time, math
ns9={'__name__':'d9scorer','__file__':__import__('os').path.abspath('d9_score_copy.py')}; exec(open('d9_score_copy.py').read(),ns9)
arb=ns9['arb']; acb=ns9['acb']; ctx=ns9['ctx']; PI=ns9['PI']; Lr=ns9['L']; PP=ns9['PP']; B9=ns9['B']
norm2=ns9['norm2']; shift_inner=ns9['shift_inner']; pole=ns9['pole']; derivative_evidence=ns9['derivative_evidence']; arch_tail_bounds=ns9['arch_tail_bounds']; a9=ns9['a']; upper=ns9['upper']
def certain_nonneg(x): return bool(arb(x.lower())>=0)          # repair (1)
def sign_of(x): return 'POSITIVE' if arb(x.lower())>0 else 'NEGATIVE' if arb(x.upper())<0 else 'UNRESOLVED'
def ep(x): return dict(lower=arb(x.lower()).str(40),upper=arb(x.upper()).str(40))
def compact2(b,parity,T,kept,K=64):
    rho=arb(19)/10; h=arb(1)/2; aa=h*(rho+1/rho)/2; bb=h*(rho-1/rho)/2; delta=arb(1)/4-bb/2; assert delta>0
    zmax=arb(1)/4+bb/2+(arb(T)+aa)/2; Ma=1+1/delta+2*zmax+PI.log(); Mf2=Lr/PI*norm2(b)*(2*Lr*bb).exp()
    Cq=h*8*rho/((rho-1)*rho**(2*K)); err_mass=upper(2*T*Cq*Mf2); err_arch=upper(err_mass*Ma)
    Mp=sum((abs(wn)*(u*bb).cosh() for (u,wn) in kept),arb(0))   # repair (4): |cos(u z)| <= cosh(u Im z) on the ellipse
    err_pr=upper(err_mass*Mp)
    nodes=[arb.legendre_p_root(K,k,weight=True) for k in range(K)]
    active=[(n,v*2*Lr/(2*PI).sqrt()*(-1)**(n//2)) for n,v in enumerate(b) if n%2==parity]
    arch=arb(0); mass=arb(0); pr=arb(0)
    for panel in range(T):
        centre=arb(panel)+h
        for x,w in nodes:
            t=centre+h*x; z=acb(Lr*t); common=(PI/(2*Lr*t)).sqrt()
            H=sum((v*common*z.bessel_j(acb(arb(n)+arb(1)/2)).real for n,v in active),arb(0)); val=2*h*w*H**2
            mass+=val; arch+=val*a9(t); pr+=val*sum((wn*(u*t).cos() for (u,wn) in kept),arb(0))
    return arch+arb(0,err_arch), mass+arb(0,err_mass), pr+arb(0,err_pr), dict(err_mass=err_mass.str(6),err_arch=err_arch.str(6),err_prime=err_pr.str(6),Mp=Mp.str(8))
def score(coeffs,degrees,parity,keep,T=128,K=64,prec=320):
    ctx.prec=prec
    b=[arb(0)]*(max(degrees)+1)
    for n,c in zip(degrees,coeffs): b[n]=arb(c)*((2*n+1)/(2*Lr)).sqrt()
    nrm=norm2(b); kept=[PP[i] for i in keep]
    shifts={i:shift_inner(b,PP[i][0])/nrm for i in range(3)}; prime_full=sum((PP[i][1]*shifts[i] for i in keep),arb(0))
    pol=pole(b,parity)/nrm; ev=derivative_evidence(b)
    A0,mass,prT,errs=compact2(b,parity,T,kept,K=K); A0/=nrm; mass/=nrm; prT/=nrm
    tails=[(m,upper(tail/nrm)) for m,tail in arch_tail_bounds(ev,T)]; m,tail=min(tails,key=lambda pr:float(pr[1]))
    masslow=max(arb(0),arb((1-mass).lower())); Atail_low=a9(T)*masslow
    A=arb(A0.lower()+Atail_low.lower(),0).union(arb((A0+tail).upper())); W=A+pol-prime_full
    beta=a9(arb(T))-B9; R=pol+beta*(1-mass)+A0-prT; excess=W-R
    Wsign=sign_of(W); route='direct'
    if Wsign=='UNRESOLVED' and sign_of(R)=='POSITIVE': Wsign='POSITIVE'; route='monotonicity W>=R_128 (T=128>=T_env)'
    return dict(W=ep(W),W_sign=Wsign,W_route=route,R128=ep(R),R128_sign=sign_of(R),excess=ep(excess),excess_certain_nonneg=certain_nonneg(excess),
                I4=ep(shifts[2]),I4_sign=sign_of(shifts[2]),quadrature_errors=errs,tail_upper=tail.str(8),deriv_order=m)
# controls for repair (1): crossing-zero rejection and endpoint reparse
ctrl={'[-1,1] certain_nonneg':certain_nonneg(arb(0,1)),'[1,2] certain_nonneg':certain_nonneg(arb(arb(3)/2,arb(1)/2)),'[-2,-1] sign':sign_of(arb(-2).union(arb(-1))),'[-1e-40,1e-40] sign':sign_of(arb(0,arb('1e-40')))}
assert ctrl['[-1,1] certain_nonneg'] is False and ctrl['[1,2] certain_nonneg'] is True and ctrl['[-2,-1] sign']=='NEGATIVE' and ctrl['[-1e-40,1e-40] sign']=='UNRESOLVED'
d=json.load(open('d21_results.json')); cases={'delete_4':[0,1],'delete_2':[1,2],'prime_free':[]}
out=dict(base='5f57f40',repairs=['crossing-zero rejection','cutoffs separated','I4 ledger','cosh growth allowance','endpoints exported','pos+neg survivor rechecks','monotonicity route'],controls=ctrl,cases={}); t0=time.time()
for key,v in d['cases'].items():
    cname,pn,Ttag=key.split(); parity=0 if pn=='even' else 1; keep=cases[cname]
    sc=score(v['frozen_coefficients'],v['degrees'],parity,keep); sc['selector_T']=int(Ttag[1:]); sc['selector_reduced_lambda_min_(not_a_score)']=v['fixed_ruler_reduced_lambda_min']; sc['scoring_cutoff']=128
    if sc['W_sign'] in ('POSITIVE','NEGATIVE'):
        sc2=score(v['frozen_coefficients'],v['degrees'],parity,keep,K=80,prec=400); sc['survivor_K80_400']=dict(W=sc2['W'],W_sign=sc2['W_sign'],route=sc2['W_route'])
        # reparse exported endpoints and re-derive the sign from strings
        lo=arb(sc['W']['lower']); hi=arb(sc['W']['upper']); sc['endpoint_reparse_sign']='POSITIVE' if lo>0 else 'NEGATIVE' if hi<0 else 'UNRESOLVED'
    out['cases'][key]=sc
    print(f"{key:24s} selT={sc['selector_T']} R128 {sc['R128_sign']:10s} W {sc['W_sign']:10s} via {sc['W_route'][:14]:14s} excess>=0 certain: {sc['excess_certain_nonneg']} I4 {sc['I4_sign']:10s} survivor {sc.get('survivor_K80_400',{}).get('W_sign','-')} reparse {sc.get('endpoint_reparse_sign','-')} errPrime {sc['quadrature_errors']['err_prime']}",flush=True)
out['seconds']=time.time()-t0; json.dump(out,open('d21_1_results.json','w'),indent=1); print('DONE',round(out['seconds']))
