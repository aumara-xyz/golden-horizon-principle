import numpy as np, json
from scipy.stats import kstest
from scipy.special import erf
from scipy.integrate import quad
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S="/private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad"
rng=np.random.default_rng(11)
def load(f,base,skip):
    v=np.array([float(l) for l in open(S+"/"+f).read().split("\n")[skip:] if l.strip()]); return (v,base)
sets={"A: zeros 1-1e4":(np.loadtxt(S+"/zeros1.txt")[:10000],0.0),"B: #1e12":load("zeros3.txt",267653395647.0,9),"C: #1e21":load("zeros4.txt",144176897509546973000.0,9),"D: #1e22":load("zeros5.txt",1370919909931995300000.0,9)}
surm=lambda s: erf(2*s/np.sqrt(np.pi))-(4*s/np.pi)*np.exp(-4*s**2/np.pi)
Ls=np.concatenate([np.linspace(0.1,3,30),np.linspace(3.5,90,174)]); Y=lambda x:(np.sin(np.pi*x)/(np.pi*x))**2 if x>0 else 1.0
gue=np.array([L-2*quad(lambda x:(L-x)*Y(x),0,L,limit=300)[0] for L in Ls]); xs=np.linspace(0,3,31); xc=(xs[:-1]+xs[1:])/2; r2g=1-(np.sin(np.pi*xc)/(np.pi*xc))**2
def sigma2(u,nstart=30000):
    out=[]
    for L in Ls:
        x=rng.uniform(u[0],u[-1]-L,nstart); out.append((np.searchsorted(u,x+L)-np.searchsorted(u,x)).var())
    return np.array(out)
res={}; fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for (name,g),col in zip(sets.items(),["tab:blue","tab:green","tab:orange","tab:red"]):
    # the far tables give gamma - base with limited relative precision; use differences (exact in the table) for unfolding
    g,base=g; T=base+g[len(g)//2]; lnT=np.log(T/(2*np.pi)); d=lnT/(2*np.pi); u=((g/(2*np.pi))*np.log(g/(2*np.pi*np.e))+7/8) if base==0 else (g-g[0])*d; s=np.diff(u); s=s/s.mean(); assert np.all(np.diff(g)>0), name
    ks=kstest(s,surm).statistic; s2=sigma2(u)
    dd=np.concatenate([u[k:]-u[:-k] for k in range(1,12)]); dd=dd[dd<3]; h,_=np.histogram(dd,xs); R2=h/(len(u)*0.1); l1=float(np.mean(np.abs(R2-r2g)))
    m=Ls>=3; X=np.vstack([np.ones(m.sum()),np.log(Ls[m]),np.log(Ls[m])**2]).T; c,*_=np.linalg.lstsq(X,s2[m],rcond=None); r=s2[m]-X@c
    P=np.linspace(3,90,871); pw=[abs(np.sum(r*np.exp(2j*np.pi*Ls[m]/p)))**2 for p in P]; Pb=float(P[int(np.argmax(pw))])
    res[name]={"T":float(T),"lnT2pi":float(lnT),"KS_surmise":float(ks),"S2_at_30":float(np.interp(30,Ls,s2)),"S2_at_60":float(np.interp(60,Ls,s2)),"GUE_30":float(np.interp(30,Ls,gue)),"GUE_60":float(np.interp(60,Ls,gue)),
        "pair_corr_L1":l1,"pred_period_p2":float(lnT/np.log(2)),"best_period":Pb,"period_err_frac":float(abs(Pb-lnT/np.log(2))/(lnT/np.log(2)))}
    b=np.linspace(0,3,31); ax[0].hist(s,b,density=True,histtype="step",color=col,label=name); ax[1].plot(Ls,s2,color=col,label=name); ax[2].plot(Ls[m],r,color=col,lw=.9,label=f"{name} period {Pb:.0f}")
cc=(b[:-1]+b[1:])/2; ax[0].plot(cc,(32/np.pi**2)*cc**2*np.exp(-4*cc**2/np.pi),"k--",label="GUE"); ax[0].legend(fontsize=7); ax[0].set_title("spacings at four heights")
ax[1].plot(Ls,gue,"k--",label="GUE"); ax[1].set_ylim(0,1); ax[1].legend(fontsize=7); ax[1].set_title("number variance: saturation rises with height")
ax[2].axhline(0,c="k",lw=.5); ax[2].legend(fontsize=7); ax[2].set_title("residual: prime-2 period stretches with height")
plt.tight_layout(); plt.savefig("toy-height.png",dpi=120); json.dump(res,open("toy-height.json","w"),indent=1); print(json.dumps(res,indent=1))
