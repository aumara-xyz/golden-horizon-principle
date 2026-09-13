import numpy as np, math, warnings, json, sys
warnings.simplefilter('ignore')
sys.path.insert(0,'../fable_d15_dirichlet'); src=open('../fable_d15_dirichlet/d15_slack.py').read().split('out={}')[0]; exec(src)
from scipy.special import eval_legendre
CHARS['zeta']=dict(q=1,a=0,chi=lambda n:1)
def lam_full(name,L,parity,scale=None):
    if name!='zeta': return lam(name,L,parity,scale)
    c=CHARS[name]; terms=[(k*math.log(p), 2*math.log(p)/p**(k/2)) for p,k in pps(L)]
    terms=[(u,w*(scale.get(round(math.exp(u)),1.0) if scale else 1.0)) for u,w in terms]
    B=sum(abs(w) for _,w in terms); T=max(1.3*2*math.pi*math.exp(B),60)
    NE=int(1.2*T*L)+40; ns=np.arange(parity,2*NE,2); npan=int(math.ceil(T)); ts=[];ws=[]
    for kp in range(npan):
        lo,hi=kp,min(kp+1,T); ts.append((hi-lo)/2*xg+(lo+hi)/2); ws.append((hi-lo)/2*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_chi(T,0)-B
    sym=a_chi(ts,0)-sum(w*np.cos(u*ts) for u,w in terms)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq; hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
    p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns]); A+=(2 if parity==0 else -2)*np.outer(p,p)
    return float(np.linalg.eigvalsh(A)[0]),T
NF=3e-14; res={}
for name,Ls in (('zeta',(0.7,)),('chi_-4',(1.0,1.1,1.2)),('chi_-3',(1.0,1.1)),('chi_5',(1.0,1.1,1.2))):
    for L in Ls:
        vis=[p**k for p,k in pps(L) if CHARS[name]['chi'](p**k)!=0]
        base=(lam_full(name,L,0)[0],lam_full(name,L,1)[0]); row=dict(base=base,places={})
        print(f"{name} L={L}: base even {base[0]:+.2e} odd {base[1]:+.2e}; visible {vis}",flush=True)
        for n in vis:
            e,_=lam_full(name,L,0,{n:0.0}); o,_=lam_full(name,L,1,{n:0.0}); dL=L-math.log(n)/2; lb=(e<-NF) or (o<-NF)
            row['places'][n]=dict(even=e,odd=o,deltaL=round(dL,3),load_bearing=lb,chi=CHARS[name]['chi'](n))
            print(f"   remove {n:2d} (chi={CHARS[name]['chi'](n):+d}, dL={dL:.3f}): even {e:+.2e} odd {o:+.2e} -> {'LOAD-BEARING' if lb else 'removable'}",flush=True)
        res[f"{name} L={L}"]=row
json.dump(res,open('d16_results.json','w'),indent=1)
