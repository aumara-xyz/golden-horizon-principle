"""D22: exact full-W scores (D9 scorer copy) of the certificate's frozen minimizers at compact cutoffs 128/256/512 with complete tails,
plus the monotonicity control R160 <= R240 <= W on one wave. argv: cert json path [cutoffs...]"""
import json, sys, time
ns9={'__name__':'d9scorer','__file__':__import__('os').path.abspath('d9_score_copy.py')}; exec(open('d9_score_copy.py').read(),ns9)
arb=ns9['arb']; acb=ns9['acb']; ctx=ns9['ctx']; PI=ns9['PI']; PP=ns9['PP']
norm2_=ns9['norm2']; shift_inner=ns9['shift_inner']; derivative_evidence=ns9['derivative_evidence']; arch_tail_bounds=ns9['arch_tail_bounds']; a9=ns9['a']; upper=ns9['upper']
def sign_of(x): return 'POSITIVE' if arb(x.lower())>0 else 'NEGATIVE' if arb(x.upper())<0 else 'UNRESOLVED'
def ep(x): return dict(lower=arb(x.lower()).str(40),upper=arb(x.upper()).str(40))
cert=json.load(open(sys.argv[1])); L=arb(cert['L']); parity=0 if cert['parity']=='even' else 1
ns9['L']=L   # D9 scorer functions read the module-global L: set it for this room (they were written for 7/10)
Lr=L; norm2=lambda b: sum((2*Lr*b[n]*b[n]/(2*n+1) for n in range(len(b))),arb(0))
def visible(): return [(u,w) for (u,w) in PP if u<2*Lr]
def pole_L(b,parity):
    y=Lr/2; total=arb(0)
    for n,v in enumerate(b):
        if n%2!=parity: continue
        total+=v*2*Lr*(PI/(2*y)).sqrt()*acb(y).bessel_i(acb(arb(n)+arb(1)/2)).real
    return (2 if parity==0 else -2)*total**2
def compact2(b,parity,T,kept,K=64):
    rho=arb(19)/10; h=arb(1)/2; aa=h*(rho+1/rho)/2; bb=h*(rho-1/rho)/2; delta=arb(1)/4-bb/2
    zmax=arb(1)/4+bb/2+(arb(T)+aa)/2; Ma=1+1/delta+2*zmax+PI.log(); Mf2=Lr/PI*norm2(b)*(2*Lr*bb).exp()
    Cq=h*8*rho/((rho-1)*rho**(2*K)); err_mass=upper(2*T*Cq*Mf2); err_arch=upper(err_mass*Ma); Mp=sum((abs(wn)*(u*bb).cosh() for (u,wn) in kept),arb(0)); err_pr=upper(err_mass*Mp)
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
ctx.prec=320; t0=time.time()
TR=float(__import__('os').environ.get('TRUNC','0'))
degs0=cert['modes']; coeffs0=cert['minimizer_frozen_40dig']
keepi=[i for i in range(len(coeffs0)) if TR==0 or abs(float(coeffs0[i]))>=TR]
degs=[degs0[i] for i in keepi]; coeffs=[coeffs0[i] for i in keepi]
b=[arb(0)]*(max(degs)+1)
for n,c in zip(degs,coeffs): b[n]=arb(c)*((2*n+1)/(2*Lr)).sqrt()
nrm=norm2(b); kept=visible(); B=sum(abs(w) for _,w in kept)
shifts=[shift_inner(b,u)/nrm for (u,w) in kept]; prime=sum((w*s for (u,w),s in zip(kept,shifts)),arb(0)); pol=pole_L(b,parity)/nrm; ev=derivative_evidence(b)
out=dict(truncation_threshold=TR,modes_kept=len(degs),frozen_coefficients=coeffs,degrees=degs,cert=sys.argv[1],L=cert['L'],parity=cert['parity'],certified_lower=cert['lambda0_certified'],verdict=cert['verdict'],trials=[])
cutoffs=[int(c) for c in sys.argv[2:]] or [128,256,512]
Rvals={}
for T in cutoffs:
    A0,mass,prT=compact2(b,parity,T,kept); A0/=nrm; mass/=nrm; prT/=nrm
    tails=[(m,upper(tail/nrm)) for m,tail in arch_tail_bounds(ev,T)]; m,tail=min(tails,key=lambda pr:float(pr[1]))
    masslow=max(arb(0),arb((1-mass).lower())); Atail_low=a9(T)*masslow
    A=arb(A0.lower()+Atail_low.lower(),0).union(arb((A0+tail).upper())); W=A+pol-prime
    beta=a9(arb(T))-B; R=pol+beta*(1-mass)+A0-prT; Rvals[T]=R
    lo=arb(cert['lambda0_certified']).lower()
    rel=(arb(W.upper())-arb(lo))/arb(lo) if arb(lo)>0 else None
    tr=dict(cutoff=T,W=ep(W),W_sign=sign_of(W),R_T=ep(R),R_sign=sign_of(R),tail_upper=tail.str(8),deriv_order=m,
            bracket_lower_certified=str(lo),bracket_upper_wave=W.upper().str(20),relative_width=(rel.str(6) if rel is not None else None),accepted=bool(rel is not None and rel<=arb('0.1') and arb(lo)>0),seconds=round(time.time()-t0))
    out['trials'].append(tr); print(cert['parity'],cert['L'],'cutoff',T,'W',W.str(15),'tail',tail.str(6),'rel width',tr['relative_width'],'accepted',tr['accepted'],flush=True)
    if tr['accepted']: break
if 160 in Rvals and 240 in Rvals:
    d1=Rvals[240]-Rvals[160]; d2=W-Rvals[240]; out['monotonicity_control']=dict(R240_minus_R160=ep(d1),W_minus_R240=ep(d2),both_certain_nonneg=bool(arb(d1.lower())>=0 and arb(d2.lower())>=0))
json.dump(out,open(sys.argv[1].replace('d22_cert','d22_score').replace('d22_cand2','d22_score_cand2').replace('.json',('_trunc.json' if TR else '.json')),'w'),indent=1); print('SCORE DONE',round(time.time()-t0),'s')
