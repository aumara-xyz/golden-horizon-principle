"""round 2: reconciliation, Antigravity audit, GUE@100k, Maass/Selberg, Li machine, closest pairs."""
import json, time, numpy as np, mpmath as mp
from scipy.stats import ks_2samp, kstest
from scipy.signal import find_peaks
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S="/private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad"
t0=time.time(); out={}; rng=np.random.default_rng(2701)
Z=np.loadtxt(S+"/zeros1.txt"); z1k=np.loadtxt("zeros.txt")
Ns=lambda T:(T/(2*np.pi))*np.log(T/(2*np.pi*np.e))+7/8
out["inputs"]={"odlyzko_n":len(Z),"odlyzko_max":float(Z[-1]),"max_abs_diff_vs_my_1000":float(np.max(np.abs(Z[:1000]-z1k)))}
# ---------- R2.1 reconciliation ----------
end=z1k[199]+5; n_in=int(np.searchsorted(Z,end,side="right"))
n=np.arange(1,1001); dev=np.maximum(np.abs(n-Ns(z1k)),np.abs((n-1)-Ns(z1k)))
d=np.mean(np.diff(z1k[:20])); devc=np.maximum(np.abs(n-z1k/d),np.abs((n-1)-z1k/d))
out["R2.1"]={"scan_end":float(end),"zeros_in_scan":n_in,"sup_smooth":float(dev.max()),"sup_smooth_at":int(dev.argmax()+1),
             "sup_comb":float(devc.max()),"sup_comb_at":int(devc.argmax()+1)}
# ---------- R2.2 Antigravity audit ----------
A={}
# L(E32,1) via functional-equation series
def primes(n):
    s=np.ones(n+1,bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
def ap(p):
    if p==2: return 0
    x=np.arange(p); r=(x**3-x)%p
    leg=np.where(r==0,0,np.where(np.array([pow(int(v),(p-1)//2,p) for v in r])==1,1,-1))
    return -int(leg.sum())
M=120; a={1:1}
for p in primes(M):
    p=int(p); a[p]=ap(p); pk=p*p; prev,cur=1,a[p]
    while pk<=M:
        nxt=a[p]*cur-(0 if p==2 else p)*prev; a[pk]=nxt; prev,cur=cur,nxt; pk*=p
def an(n):
    if n in a: return a[n]
    v=1; m=n
    for p in primes(n):
        p=int(p)
        if m%p==0:
            pk=1
            while m%p==0: m//=p; pk*=p
            v*=a[pk]
    return v
L32=2*sum(an(k)/k*np.exp(-2*np.pi*k/np.sqrt(32)) for k in range(1,M+1))
A["L_E32_1_series"]=float(L32); A["L_E32_1_antigravity"]=0.3912
# L6 detector on 100 zeros vs random control (same protocol as antigravity: 700 pts, height>=4, distance=10)
tv=np.linspace(0.1,3.5,700); g100=Z[:100]
def detect(g):
    F=np.cos(np.outer(tv,g)).sum(1); pk,_=find_peaks(F,height=4.0,distance=10); return tv[pk],F
targets={"ln2":np.log(2),"ln3":np.log(3),"ln4":np.log(4),"ln5":np.log(5),"ln7":np.log(7),"ln8":np.log(8),"ln9":np.log(9),"ln11":np.log(11)}
pz,Fz=detect(g100); hits_z=sum(np.min(np.abs(pz-v))<0.03 for v in targets.values())
ctrl=[]
for _ in range(200):
    gr=np.sort(rng.uniform(g100[0],g100[-1],100)); pr,_=detect(gr); ctrl.append((len(pr),sum(np.min(np.abs(pr-v))<0.03 for v in targets.values()) if len(pr) else 0))
ctrl=np.array(ctrl)
A["L6_protocol"]={"zeros_peaks":int(len(pz)),"zeros_target_hits_of_8":int(hits_z),"random_peaks_mean":float(ctrl[:,0].mean()),
   "random_target_hits_mean":float(ctrl[:,1].mean()),"random_hits_ge_zeros_frac":float((ctrl[:,1]>=hits_z).mean()),"noise_std_sum100cos":float(np.sqrt(50))}
# phenomenon at 100k: fine local grid (+-0.003, step 1e-5) around each ln p^k, Hann window over index; shuffled-spacing control
w=0.5*(1-np.cos(2*np.pi*np.arange(len(Z))/len(Z)))
def local_depth(g,v,half=0.003,step=1e-5):
    tl=np.arange(v-half,v+half,step); F=np.zeros(len(tl))
    for i in range(0,len(tl),50): F[i:i+50]=(np.cos(np.outer(tl[i:i+50],g))*w).sum(1)
    return float(-F.min()), float(tl[F.argmin()]), float(F.std())
gs=Z[0]+np.concatenate([[0],np.cumsum(rng.permutation(np.diff(Z)))])
ph={}; pc={}; loc={}
for k,v in targets.items():
    dz_,tz_,_=local_depth(Z,v); dc_,_,sc_=local_depth(gs,v); ph[k]=dz_; pc[k]=dc_; loc[k]=tz_-v
offt=[local_depth(Z,v)[0] for v in [0.8,1.0,1.3,1.5,1.7,2.0,2.3]]   # off-target windows for zeros
A["L6_100k"]={"peak_depth_zeros":ph,"peak_offset_from_lnp":loc,"same_window_control":pc,"zeros_offtarget_depths":offt,
   "ratio_ln3_ln2":ph["ln3"]/ph["ln2"],"ratio_ln4_ln2":ph["ln4"]/ph["ln2"],"pred_ln3_ln2":float((np.log(3)/np.sqrt(3))/(np.log(2)/np.sqrt(2))),"pred_ln4_ln2":float((np.log(2)/2)/(np.log(2)/np.sqrt(2)))}
# coarse picture with 2000 zeros for the plot
tt=np.linspace(0.5,2.6,8401); w2=0.5*(1-np.cos(2*np.pi*np.arange(2000)/2000))
Fz=(np.cos(np.outer(tt,Z[:2000]))*w2).sum(1); Fc=(np.cos(np.outer(tt,gs[:2000]))*w2).sum(1)
# musical chord base rate
ivs=sorted({nn/dd for nn in range(1,10) for dd in range(1,10) if 1<nn/dd<=2})
u=rng.uniform(1.1,2.0,200000); hit=(np.min(np.abs(u[:,None]-np.array(ivs)[None,:]),axis=1)<0.02).mean()
r2,r3=Z[1]/Z[0],Z[2]/Z[0]
A["chord"]={"n_intervals":len(ivs),"p_single_hit_within_0.02":float(hit),"p_two_hits":float(hit**2),"gamma2_over_gamma1":float(r2),"gamma3_over_gamma1":float(r3),
   "nearest_iv_2":float(min(ivs,key=lambda x:abs(x-r2))),"nearest_iv_3":float(min(ivs,key=lambda x:abs(x-r3)))}
# Selberg geodesic lengths vs ln(p^k)
tr=np.arange(3,41); Lg=2*np.log((tr+np.sqrt(tr**2-4))/2)
pp=primes(3000); lpk=np.sort(np.concatenate([np.log(pp**k) for k in range(1,5)])); lpk=lpk[lpk<Lg.max()+1]
def mind(L): return np.min(np.abs(L[:,None]-lpk[None,:]),axis=1)
dz=mind(Lg); ctrlm=np.array([mind(rng.uniform(Lg.min(),Lg.max(),len(Lg))).mean() for _ in range(2000)])
ctrlmin=np.array([mind(rng.uniform(Lg.min(),Lg.max(),len(Lg))).min() for _ in range(2000)])
def isprimepower(m):
    for p in primes(int(m**.5)+1):
        p=int(p)
        if m%p==0:
            while m%p==0: m//=p
            return m==1
    return m>1
m2=tr**2-2; pp_hits=[int(t) for t,m in zip(tr,m2) if isprimepower(int(m))]
ident=np.abs(Lg-np.log(m2.astype(float)))
A["selberg_identity"]={"note":"2 ln eps_t = ln(t^2-2-eps'^2): geodesic length is within 1/t^4 of ln(t^2-2)","max_abs_L_minus_ln_t2m2":float(ident.max()),
   "t_with_t2m2_primepower":pp_hits,"count":len(pp_hits),"of":int(len(tr))}
A["selberg"]={"mean_dist_actual":float(dz.mean()),"pct_of_random_means_below_actual":float((ctrlm<dz.mean()).mean()*100),
   "min_dist_actual":float(dz.min()),"pct_of_random_mins_below_actual":float((ctrlmin<dz.min()).mean()*100),
   "t3_len":float(Lg[0]),"t3_dist_ln7":float(abs(Lg[0]-np.log(7))),"t5_len":float(Lg[2]),"t5_dist_ln23":float(abs(Lg[2]-np.log(23)))}
# Li coefficients from 100k zeros (+tail) vs 100 zeros (antigravity)
rho=0.5+1j*Z; wlog=np.log(1-1/rho)
def li(nmax,zsub,tail=True):
    T=zsub[-1]; ws=wlog[:len(zsub)]; lam=[]
    for k in range(1,nmax+1):
        v=2*np.real(np.sum(1-np.exp(k*ws)))
        if tail: v+=k*(np.log(T/(2*np.pi))+1)/(2*np.pi*T)
        lam.append(v)
    return np.array(lam)
lam=li(200,Z); lam100=li(100,Z[:100],tail=False)
gE=0.5772156649015329; coffey=lambda k:(k/2)*(np.log(k)+gE-1-np.log(2*np.pi))+0.5
A["li"]={"lambda1":float(lam[0]),"lambda1_exact":1+gE/2-np.log(4*np.pi)/2,"lambda10":float(lam[9]),"lambda100":float(lam[99]),"lambda200":float(lam[199]),
   "coffey100":float(coffey(100)),"coffey200":float(coffey(200)),"from_100_zeros_lambda10":float(lam100[9]),"from_100_zeros_lambda100":float(lam100[99]),
   "monotone_to_200":bool(np.all(np.diff(lam)>0)),"all_positive":bool(np.all(lam>0))}
# Gram's law on 100k zeros
th=lambda t:(t/2)*np.log(t/(2*np.pi))-t/2-np.pi/8+1/(48*t)+7/(5760*t**3)
dth=lambda t:0.5*np.log(t/(2*np.pi))-1/(48*t**2)-21/(5760*t**4)
nmax=int(Ns(Z[-1]))-3; ng=np.arange(-1,nmax+1); g=np.maximum(2*np.pi*np.exp(1+2*np.pi*ng/np.log(np.maximum(ng,1)+20)),10.0)
g=np.full(len(ng),20.0)+ng*3.0; g=np.maximum(g,10.0)
for _ in range(60): g=g-(th(g)-ng*np.pi)/dth(g)
cnt=np.diff(np.searchsorted(Z,g,side="right")); viol=np.nonzero(cnt!=1)[0]
A["gram"]={"n_intervals":int(len(cnt)),"first_violation_gram_index":int(ng[viol[0]+1]) if len(viol) else None,"violation_frac":float((cnt!=1).mean()),
   "g0":float(g[1]),"g_last":float(g[-1]),"max_theta_residual":float(np.max(np.abs(th(g)-ng*np.pi)))}
out["R2.2"]=A
# ---------- R2.3 GUE with 100k zeros ----------
u=Ns(Z); sz=np.diff(u); sz=sz/sz.mean()
def gue_spacings(N=1000,draws=10):
    sp=[]
    for _ in range(draws):
        G=rng.normal(size=(N,N))+1j*rng.normal(size=(N,N)); H=(G+G.conj().T)/2; ev=np.sort(np.linalg.eigvalsh(H))
        k=np.arange(1,N+1); lo,hi=N//4,3*N//4; c=np.polyfit(ev[lo:hi],k[lo:hi],7); uu=np.polyval(c,ev[lo:hi]); sp.append(np.diff(uu))
    sp=np.concatenate(sp); return sp/sp.mean()
sg=gue_spacings()
surm_cdf=lambda s:1-np.exp(-4*s**2/np.pi)*(1+0)  # placeholder replaced below
from scipy.special import erf
surm_cdf=lambda s: erf(2*s/np.sqrt(np.pi)) - (4*s/np.pi)*np.exp(-4*s**2/np.pi)
out["R2.3"]={"n_spacings":int(len(sz)),"KS_zeros_vs_GUEmatrix":float(ks_2samp(sz,sg).statistic),"KS_zeros_vs_surmise":float(kstest(sz,surm_cdf).statistic),
   "KS_zeros_vs_exp":float(kstest(sz,'expon').statistic),"KS_GUEmatrix_vs_surmise":float(kstest(sg,surm_cdf).statistic),"n_gue_spacings":int(len(sg))}
# pair correlation 100k
R2=[]; xs=np.linspace(0,3,61); xc=(xs[:-1]+xs[1:])/2
dd=[]
for k in range(1,12):
    dd.append(u[k:]-u[:-k])
dd=np.concatenate(dd); dd=dd[dd<3]; h,_=np.histogram(dd,xs); R2=h/(len(u)*0.05)
gue_r2=1-(np.sin(np.pi*xc)/(np.pi*xc))**2
out["R2.3"]["pair_corr_L1_to_GUE"]=float(np.mean(np.abs(R2-gue_r2))); out["R2.3"]["pair_corr_L1_to_Poisson"]=float(np.mean(np.abs(R2-1)))
# positions control: correlation of spacing sequences (independent sequences -> ~0)
G1=gue_spacings(1000,1); G2=gue_spacings(1000,1); m=min(len(G1),len(G2))
out["R2.3"]["spacing_corr_GUE1_GUE2"]=float(np.corrcoef(G1[:m],G2[:m])[0,1]); out["R2.3"]["spacing_corr_GUE1_zeros"]=float(np.corrcoef(G1[:m],sz[:m])[0,1])
# ---------- R2.4 Maass forms ----------
Mz=np.loadtxt(S+"/maass_r.txt"); res={}
def unfold_poly(r,deg=3):
    k=np.arange(1,len(r)+1); X=np.vstack([r**2,r*np.log(r),r,np.ones_like(r)]).T; c,*_=np.linalg.lstsq(X,k,rcond=None); uu=X@c; s=np.diff(uu); return s/s.mean()
for name,mask in [("even",Mz[:,1]==1),("odd",Mz[:,1]==0),("mixed",np.ones(len(Mz),bool))]:
    r=np.sort(Mz[mask,0]); s=unfold_poly(r)
    res[name]={"n":int(len(r)),"KS_exp":float(kstest(s,'expon').statistic),"KS_surmise":float(kstest(s,surm_cdf).statistic),"frac_below_0.2":float((s<0.2).mean()),"frac_below_0.1":float((s<0.1).mean())}
out["R2.4"]=res
# ---------- R2.5 Li rogue machine ----------
nn=np.arange(1,2_000_001); base=coffey(nn); base[:200]=lam
def rogue(beta,gam):
    tot=np.zeros(len(nn))
    for r in [beta+1j*gam,(1-beta)+1j*gam]:
        lw=np.log(1-1/r); tot+=2*np.real(1-np.exp(nn*lw))
    return tot
rg={}
for beta in [0.75,0.6]:
    for gam in [14.134725,100.0,1000.0]:
        lamr=base+rogue(beta,gam); neg=np.nonzero(lamr<0)[0]
        rg[f"beta={beta},gamma={gam}"]=int(nn[neg[0]]) if len(neg) else "none below 2e6"
out["R2.5"]={"n_crit":rg,"growth_rate_formula":"|1-1/(1-rho)|^n ~ exp(n(2beta-1)/(2|1-rho|^2))"}
# ---------- R2.6 closest pairs ----------
idx=np.argsort(sz)[:5]
out["R2.6"]={"frac_s_below_0.1":float((sz<0.1).mean()),"gue_pred_0.1":float(np.pi**2/9*0.1**3),"frac_s_below_0.2":float((sz<0.2).mean()),"gue_pred_0.2":float(np.pi**2/9*0.2**3),
   "poisson_0.1":float(1-np.exp(-0.1)),"poisson_0.2":float(1-np.exp(-0.2)),
   "closest5":[{"n":int(i+1),"gamma":float(Z[i]),"gap":float(Z[i+1]-Z[i]),"s":float(sz[i])} for i in idx]}
li_idx=int(np.searchsorted(Z,7005.0)); out["R2.6"]["lehmer"]={"n":li_idx+1,"gamma":float(Z[li_idx]),"gap":float(Z[li_idx+1]-Z[li_idx]),"s":float(sz[li_idx]),"rank_among_100k":int(np.sum(sz<sz[li_idx])+1)}
# ---------- plots ----------
fig,ax=plt.subplots(2,2,figsize=(13,9)); b=np.linspace(0,3,61); c=(b[:-1]+b[1:])/2
ax[0,0].hist(sz,b,density=True,alpha=.5,label="100k zeta zeros"); ax[0,0].hist(sg,b,density=True,histtype="step",lw=2,label="GUE matrices N=1000")
ax[0,0].plot(c,np.exp(-c),"k--",label="Poisson"); ax[0,0].legend(); ax[0,0].set_title("nearest-neighbour spacing")
ax[0,1].bar(xc,R2,width=.05,alpha=.5); ax[0,1].plot(xc,gue_r2,"r"); ax[0,1].set_title("pair correlation, 100k zeros vs GUE"); ax[0,1].set_ylim(0,1.3)
ax[1,0].plot(tt,Fz,lw=.6,label="zeros"); ax[1,0].plot(tt,Fc,lw=.6,alpha=.6,label="shuffled-spacing control")
for k,v in targets.items(): ax[1,0].axvline(v,c="r",lw=.4)
ax[1,0].legend(); ax[1,0].set_title("sum_n w_n cos(gamma_n t), red = ln p^k")
for name,ls in [("even","-"),("odd","--")]:
    r=np.sort(Mz[Mz[:,1]==(1 if name=="even" else 0),0]); s=unfold_poly(r); ax[1,1].hist(s,np.linspace(0,3,21),density=True,histtype="step",lw=2,ls=ls,label=f"Maass {name} (n={len(r)})")
ax[1,1].plot(c,np.exp(-c),"k--",label="Poisson"); ax[1,1].plot(c,(32/np.pi**2)*c**2*np.exp(-4*c**2/np.pi),"r",label="GUE"); ax[1,1].legend(); ax[1,1].set_title("Maass forms PSL(2,Z): spacing per symmetry class")
plt.tight_layout(); plt.savefig("round2.png",dpi=120)
out["runtime_s"]=time.time()-t0
json.dump(out,open("metrics-round2.json","w"),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
