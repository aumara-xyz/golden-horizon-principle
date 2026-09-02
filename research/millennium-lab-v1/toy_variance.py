import numpy as np, json
from scipy.integrate import quad
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S="/private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad"
Z=np.loadtxt(S+"/zeros1.txt"); rng=np.random.default_rng(7)
Ns=lambda T:(T/(2*np.pi))*np.log(T/(2*np.pi*np.e))+7/8
Ls=np.concatenate([np.linspace(0.1,3,30),np.linspace(3.5,60,114)])
def sigma2(u,Ls,nstart=40000):
    u=np.sort(u); out=[]
    for L in Ls:
        x=rng.uniform(u[0],u[-1]-L,nstart); c=np.searchsorted(u,x+L)-np.searchsorted(u,x); out.append(c.var())
    return np.array(out)
Y=lambda x:(np.sin(np.pi*x)/(np.pi*x))**2 if x>0 else 1.0
gue=np.array([L-2*quad(lambda x:(L-x)*Y(x),0,L,limit=200)[0] for L in Ls])
bands={"low (zeros 1-20k)":Z[:20000],"high (zeros 80k-100k)":Z[80000:]}
res={}
fig,ax=plt.subplots(1,2,figsize=(13,4.5))
ax[0].plot(Ls,gue,"r",label="GUE exact"); ax[0].plot(Ls,Ls,"k--",lw=.8,label="Poisson (L, off scale)")
# GUE matrix control
def gue_unfolded(N=1000,draws=6):
    us=[]
    for _ in range(draws):
        G=rng.normal(size=(N,N))+1j*rng.normal(size=(N,N)); H=(G+G.conj().T)/2; ev=np.sort(np.linalg.eigvalsh(H)); k=np.arange(1,N+1); lo,hi=N//4,3*N//4
        c=np.polyfit(ev[lo:hi],k[lo:hi],7); us.append(np.polyval(c,ev[lo:hi]))
    return us
sg=np.mean([sigma2(u,Ls,8000) for u in gue_unfolded()],axis=0); ax[0].plot(Ls,sg,color="gray",lw=1,label="GUE matrices")
for (name,z),col in zip(bands.items(),["tab:blue","tab:orange"]):
    u=Ns(z); s2=sigma2(u,Ls); ax[0].plot(Ls,s2,color=col,lw=1.2,label=name)
    T=z[len(z)//2]; lnT=np.log(T/(2*np.pi)); m=Ls>=3
    # residual vs smooth quadratic-in-lnL fit; dominant period via Lomb-like scan
    X=np.vstack([np.ones(m.sum()),np.log(Ls[m]),np.log(Ls[m])**2]).T; coef,*_=np.linalg.lstsq(X,s2[m],rcond=None); r=s2[m]-X@coef
    periods=np.linspace(4,30,521); power=[abs(np.sum(r*np.exp(2j*np.pi*Ls[m]/P)))**2 for P in periods]; Pbest=float(periods[int(np.argmax(power))])
    ax[1].plot(Ls[m],r,color=col,lw=1,label=f"{name} residual, best period {Pbest:.1f}")
    res[name]={"T_mid":float(T),"lnT2pi":float(lnT),"pred_period_p2":float(lnT/np.log(2)),"pred_period_p3":float(lnT/np.log(3)),"best_period":Pbest,
               "max_abs_dev_from_GUE_L<=2":float(np.max(np.abs(s2[Ls<=2]-gue[Ls<=2]))),"S2_at_30":float(np.interp(30,Ls,s2)),"GUE_at_30":float(np.interp(30,Ls,gue)),
               "S2_mean_40_60":float(s2[Ls>=40].mean()),"S2_mean_10_20":float(s2[(Ls>=10)&(Ls<=20)].mean())}
res["GUE_matrices"]={"S2_at_30":float(np.interp(30,Ls,sg)),"S2_mean_40_60":float(sg[Ls>=40].mean())}
ax[0].set_ylim(0,1.0); ax[0].set_xlabel("window L (mean spacings)"); ax[0].set_ylabel("number variance"); ax[0].legend(fontsize=8); ax[0].set_title("Berry's number variance: zeros saturate, GUE keeps growing")
ax[1].axhline(0,c="k",lw=.5); ax[1].set_xlabel("L"); ax[1].legend(fontsize=8); ax[1].set_title("residual: the primes' fingerprint")
plt.tight_layout(); plt.savefig("toy-variance.png",dpi=120); json.dump(res,open("toy-variance.json","w"),indent=1); print(json.dumps(res,indent=1))
