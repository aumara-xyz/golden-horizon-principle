"""D21 / Astra Test 1. Exact fixed-wave scores (D9 scorer copy, functions only) for deletion mutations at zeta L=0.7.
Proposal waves come from FIXED-RULER reduced forms (beta from authentic B) at T=160, 240 with 160 modes/parity (double precision), frozen as decimals."""
import json, math, sys, time, hashlib, warnings
import numpy as np
warnings.simplefilter('ignore')
from scipy.special import spherical_jn, digamma, eval_legendre
# ---- D9 scorer (provenance-recorded copy; import functions without running main)
ns9={'__name__':'d9scorer','__file__':__import__('os').path.abspath('d9_score_copy.py')}; exec(open('d9_score_copy.py').read(),ns9)
arb=ns9['arb']; acb=ns9['acb']; ctx=ns9['ctx']; PI=ns9['PI']; Lr=ns9['L']; PP=ns9['PP']; B9=ns9['B']
norm2=ns9['norm2']; shift_inner=ns9['shift_inner']; pole=ns9['pole']; derivative_evidence=ns9['derivative_evidence']; arch_tail_bounds=ns9['arch_tail_bounds']; a9=ns9['a']; upper=ns9['upper']
def compact2(b,parity,T,kept,K=64,prec=None):
    """D9 compact() extended: also returns the compact prime integral sum_{n in kept} w_n int_{-T}^T cos(t log n)|F|^2 (disclosed extension)."""
    if prec: ctx.prec=prec
    rho=arb(19)/10; h=arb(1)/2; aa=h*(rho+1/rho)/2; bb=h*(rho-1/rho)/2; delta=arb(1)/4-bb/2; assert delta>0
    zmax=arb(1)/4+bb/2+(arb(T)+aa)/2; Ma=1+1/delta+2*zmax+PI.log(); Mf2=Lr/PI*norm2(b)*(2*Lr*bb).exp()
    Cq=h*8*rho/((rho-1)*rho**(2*K)); err_mass=upper(2*T*Cq*Mf2); err_arch=upper(err_mass*Ma); err_pr=upper(err_mass*B9)
    nodes=[arb.legendre_p_root(K,k,weight=True) for k in range(K)]
    active=[(n,v*2*Lr/(2*PI).sqrt()*(-1)**(n//2)) for n,v in enumerate(b) if n%2==parity]
    arch=arb(0); mass=arb(0); pr=arb(0)
    for panel in range(T):
        centre=arb(panel)+h
        for x,w in nodes:
            t=centre+h*x; z=acb(Lr*t); common=(PI/(2*Lr*t)).sqrt()
            H=sum((v*common*z.bessel_j(acb(arb(n)+arb(1)/2)).real for n,v in active),arb(0)); val=2*h*w*H**2
            mass+=val; arch+=val*a9(t); pr+=val*sum((wn*(u*t).cos() for (u,wn) in kept),arb(0))
    return arch+arb(0,err_arch), mass+arb(0,err_mass), pr+arb(0,err_pr)
# ---- fixed-ruler reduced form (double) for proposal waves
L=0.7; K48=48; xg,wg=np.polynomial.legendre.leggauss(K48)
PPf=[(math.log(2),2*math.log(2)/math.sqrt(2)),(math.log(3),2*math.log(3)/math.sqrt(3)),(2*math.log(2),math.log(2))]; Bf=sum(w for _,w in PPf)
def a_t(t): return np.real(digamma(0.25+0.5j*np.asarray(t,dtype=complex)))-math.log(math.pi)
def proposal(parity,T,keep,NE=160):
    ns=np.arange(parity,2*NE,2); ts=[];ws=[]
    for kp in range(T):
        lo,hi=kp,kp+1; ts.append((hi-lo)/2*xg+(lo+hi)/2); ws.append((hi-lo)/2*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_t(T)-Bf
    sym=a_t(ts)-sum(w*np.cos(u*ts) for i,(u,w) in enumerate(PPf) if i in keep)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq; hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
    p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns]); A+=(2 if parity==0 else -2)*np.outer(p,p)
    ev,V=np.linalg.eigh(A); return ns, V[:,0], float(ev[0]), beta
def exact_score(coeffs_dec,degrees,parity,keep,T=128,K=64,prec=320):
    ctx.prec=prec
    b=[arb(0)]*(max(degrees)+1)
    for n,c in zip(degrees,coeffs_dec): b[n]=arb(c)*((2*n+1)/(2*Lr)).sqrt()
    nrm=norm2(b); assert nrm>0
    kept=[PP[i] for i in keep]
    shifts={i:shift_inner(b,PP[i][0])/nrm for i in range(3)}
    prime_full=sum((PP[i][1]*shifts[i] for i in keep),arb(0))
    pol=pole(b,parity)/nrm; ev=derivative_evidence(b)
    A0,mass,prT=compact2(b,parity,T,kept,K=K); A0/=nrm; mass/=nrm; prT/=nrm
    tails=[(m,upper(tail/nrm)) for m,tail in arch_tail_bounds(ev,T)]; m,tail=min(tails,key=lambda pr:float(pr[1]))
    masslow=max(arb(0),arb((1-mass).lower())); Atail_low=a9(T)*masslow
    A=arb(A0.lower()+Atail_low.lower(),0).union(arb((A0+tail).upper()))
    W=A+pol-prime_full
    # fixed-ruler reduced score on the SAME wave at this T (T=128 here is the scorer's compact cutoff; R uses beta=a(T)-B_auth)
    beta=a9(arb(T))-B9; R=pol+beta*(1-mass)+A0-prT
    excess=W-R   # must be >= 0 (positive discarded tail) within enclosures
    sign=lambda v:'POSITIVE' if v>0 else 'NEGATIVE' if v<0 else 'UNVERIFIED'
    return dict(W=W.str(20),W_sign=sign(W),W_lower=arb(W.lower()).str(20),W_upper=arb(W.upper()).str(20),R_T128=R.str(20),R_sign=sign(R),
                excess_W_minus_R=excess.str(12),excess_nonneg_certain=bool(excess>=0) or bool(excess.upper()>=0 and not excess<0),
                arch_full=A.str(15),pole=pol.str(15),prime_kept=prime_full.str(15),shift_corr={str((2,3,4)[i]):shifts[i].str(12) for i in range(3)},
                tail_upper=tail.str(8),deriv_order=m,norm=nrm.str(12))
t0=time.time(); out=dict(trial=2,base_commit='07913fa',scorer_sha=open('PROVENANCE.txt').read().split()[0],numpy=np.__version__,cases={})
# ---- controls first
print('controls: D9 scorer controls()',flush=True); ns9['sys'].argv=['x','controls']; ns9['controls']()
# D9 replay control: rescore D9's frozen even wave with the copied scorer and compare to saved W
fr=json.load(open('../codex_d9_exact_scores/frozen_even.json')); saved=json.load(open('../codex_d9_exact_scores/scores_even.json'))
rep=exact_score(fr['coefficients'],fr['degrees'],0,[0,1,2],T=128)
savedW=arb(saved['trials'][0]['W']); ok=arb(rep['W']).overlaps(savedW); out['control_D9_replay']=dict(replayed_W=rep['W'],saved_W=saved['trials'][0]['W'],overlap=bool(ok)); print('D9 replay overlap:',ok,rep['W'],saved['trials'][0]['W'],flush=True)
assert ok, 'D9 replay control failed'
# ---- frozen cases
cases={'delete_4':[0,1],'delete_2':[1,2],'prime_free':[]}
for cname,keep in cases.items():
    for parity,pn in ((0,'even'),(1,'odd')):
        for T in (160,240):
            ns,c,lam_red,beta=proposal(parity,T,keep); c=np.where(np.abs(c)<1e-13,0.0,c); keepidx=[i for i in range(len(c)) if c[i]!=0]; degs=[int(ns[i]) for i in keepidx]; dec=[repr(float(c[i])) for i in keepidx]
            key=f"{cname} {pn} T{T}"; print(f"{key}: fixed-ruler reduced lambda_min = {lam_red:+.3e} (beta={beta:.4f}); scoring exact W ...",flush=True)
            sc=exact_score(dec,degs,parity,keep); sc.update(proposal_T=T,fixed_ruler_reduced_lambda_min=lam_red,frozen_coefficients=dec,degrees=degs,modes_kept=len(degs))
            if cname=='delete_4':   # operator route, CONDITIONAL on the D7 certificate: W_del4(f)/||f||^2 >= m_par + w4*I4(f)/||f||^2
                m_par=arb('1.031e-13') if parity==0 else arb('5.859e-11'); I4=arb(sc['shift_corr']['4']); bound=m_par+PP[2][1]*I4
                sc['operator_route_conditional_D7']=dict(I4=I4.str(15),lower_bound_W_del4=bound.str(15),positive=bool(bound>0))
                if bound>0 and sc['W_sign']=='UNVERIFIED': sc['W_sign']='POSITIVE (conditional on D7 operator certificate)'
            cls='(a) certified W-negative witness' if sc['W_sign']=='NEGATIVE' else ('(b) R-negative but W '+sc['W_sign'] if (lam_red<0 or sc['R_sign']=='NEGATIVE') else '(b*) R positive, W '+sc['W_sign'])
            sc['class']=cls; out['cases'][key]=sc
            print(f"   W_mut = {sc['W']}  [{sc['W_sign']}]  R_128 = {sc['R_T128']} [{sc['R_sign']}]  excess>=0: {sc['excess_nonneg_certain']}  corr4 {sc['shift_corr']['4']}  -> {cls}",flush=True)
            json.dump(out,open('d21_results.json','w'),indent=1)
# ---- survivor mutation: class (a) witnesses rescored with K=80 nodes, 400 bits, same vector
for key,sc in list(out['cases'].items()):
    if sc['W_sign']=='NEGATIVE':
        cname,pn,_=key.split(); keep=cases[cname]; parity=0 if pn=='even' else 1
        sc2=exact_score(sc['frozen_coefficients'],sc['degrees'],parity,keep,T=128,K=80,prec=400)
        out['cases'][key]['survivor_mutation_K80_400bit']=dict(W=sc2['W'],W_sign=sc2['W_sign']); print(f"survivor {key}: K=80/400bit W = {sc2['W']} [{sc2['W_sign']}]",flush=True)
out['seconds']=time.time()-t0; json.dump(out,open('d21_results.json','w'),indent=1); print('DONE',round(out['seconds']),'s')
