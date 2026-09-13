import numpy as np, math, warnings, json, sys
warnings.simplefilter('ignore')
sys.path.insert(0,'../fable_d15_dirichlet'); exec(open('../fable_d15_dirichlet/d15_slack.py').read().split('out={}')[0])
from scipy.special import eval_legendre
CHARS['zeta']=dict(q=1,a=0,chi=lambda n:1)
def lam2(name,L,parity,scale=None,sigma=0.5,kill_k=None):
    c=CHARS[name]; terms=[]
    for p,k in pps(L):
        n=p**k; w=c['chi'](n)*2*math.log(p)/n**sigma
        if kill_k=='powers' and k>=2: w=0
        if kill_k=='primes' and k==1: w=0
        if scale: w*=scale.get(n,1.0)
        if w!=0: terms.append((k*math.log(p),w))
    B=sum(abs(w) for _,w in terms); shift=math.log(c['q'])
    if name=='zeta': T=max(1.3*2*math.pi*math.exp(B),60)
    else:
        T=60.0
        while a_chi(T,c['a'])+shift-B<0.01: T*=1.3
        T=max(1.3*T,60) if T>60 else 60.0
    NE=int(1.2*T*L)+40; ns=np.arange(parity,2*NE,2); npan=int(math.ceil(T)); ts=[];ws=[]
    for kp in range(npan):
        lo,hi=kp,min(kp+1,T); ts.append((hi-lo)/2*xg+(lo+hi)/2); ws.append((hi-lo)/2*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_chi(T,c['a'])+shift-B
    sym=a_chi(ts,c['a'])+shift-sum(w*np.cos(u*ts) for u,w in terms)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    if name=='zeta':
        xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq; hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
        p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns]); A+=(2 if parity==0 else -2)*np.outer(p,p)
    return float(np.linalg.eigvalsh(A)[0])
res={'A':{},'B':{}}
print("Test A: remove all prime POWERS (k>=2) vs remove all PRIMES (k=1)")
for name,L in (('zeta',0.7),('chi_-4',1.2),('chi_-3',1.1),('chi_5',1.2)):
    pw=[p**k for p,k in pps(L) if k>=2 and CHARS[name]['chi'](p**k)!=0]
    base=(lam2(name,L,0),lam2(name,L,1)); nop=(lam2(name,L,0,kill_k='powers'),lam2(name,L,1,kill_k='powers')); nopr=(lam2(name,L,0,kill_k='primes'),lam2(name,L,1,kill_k='primes'))
    res['A'][f"{name} L={L}"]=dict(powers=pw,base=base,no_powers=nop,no_primes=nopr)
    print(f"  {name} L={L} powers={pw}: base {base[0]:+.2e}/{base[1]:+.2e} | no powers {nop[0]:+.2e}/{nop[1]:+.2e} | no primes {nopr[0]:+.2e}/{nopr[1]:+.2e}",flush=True)
print("Test B: weight exponent sigma (0.5 = critical line)")
for name,L in (('zeta',0.6),('chi_-4',1.0)):
    row={}
    for s in (0.45,0.48,0.49,0.50,0.51,0.52,0.55):
        e=lam2(name,L,0,sigma=s); o=lam2(name,L,1,sigma=s); row[str(s)]=(e,o); print(f"  {name} L={L} sigma={s:.2f}: even {e:+.2e} odd {o:+.2e}",flush=True)
    res['B'][f"{name} L={L}"]=row
json.dump(res,open('d17_results.json','w'),indent=1)
