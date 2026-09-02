"""millennium-lab-v1: L1-L3. Run: python3 lab.py  -> writes zeros.txt, *.png, metrics.json"""
import json, time, numpy as np, mpmath as mp
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.linalg import eigvals, eigvalsh
NZ=1000; out={}
t0=time.time()
# ---------- L1 ----------
zeros=np.array([float(mp.im(mp.zetazero(n))) for n in range(1,NZ+1)])
re_parts=[float(mp.re(mp.zetazero(n))) for n in range(1,201)]
np.savetxt("zeros.txt",zeros,fmt="%.12f")
out["L1"]={"n_zeros":NZ,"max_abs_re_minus_half_first200":max(abs(r-0.5) for r in re_parts),
           "first5":zeros[:5].tolist()}
# |zeta(1/2+it)| on grid and check its minima coincide with zeros (dips) and nothing else
ts=np.linspace(0,zeros[199]+5,20000)
absz=np.array([float(abs(mp.zeta(mp.mpc(0.5,t)))) for t in ts])
dips=[i for i in range(1,len(ts)-1) if absz[i]<absz[i-1] and absz[i]<absz[i+1] and absz[i]<0.05]
out["L1"]["dips_below_0.05"]=len(dips)
plt.figure(figsize=(12,3)); plt.plot(ts,absz,lw=.5); plt.scatter(zeros[:200],np.zeros(200),s=6,c="r")
plt.xlim(0,120); plt.ylim(0,5); plt.title("|zeta(1/2+it)|, red = first zeros"); plt.savefig("L1_abszeta.png",dpi=120); plt.close()
# ---------- L2 ----------
def unfold_zeros(z): return np.diff(z)*np.log(z[:-1]/(2*np.pi))/(2*np.pi)
def primes(n):
    s=np.ones(n+1,bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
p=primes(200000).astype(float); p=p[p>1000][:NZ+1]
sp=np.diff(p)/np.log(p[:-1])
rng=np.random.default_rng(0); r=np.sort(rng.uniform(0,NZ,NZ+1)); sr=np.diff(r)  # density 1
sz=unfold_zeros(zeros)
gue=lambda s:(32/np.pi**2)*s**2*np.exp(-4*s**2/np.pi); poi=lambda s:np.exp(-s)
bins=np.linspace(0,3,31); c=(bins[:-1]+bins[1:])/2; w=bins[1]-bins[0]
def l1(sample,ref):
    h,_=np.histogram(sample,bins,density=True); return float(np.sum(np.abs(h-ref(c)))*w)
def r2(sample_pos,xmax=3,nb=30):
    # pair correlation of unfolded positions: count pairs at distance x, normalised by N
    u=np.cumsum(np.concatenate([[0],sample_pos])); d=[]
    for i in range(len(u)):
        dd=u[i+1:i+60]-u[i]; d.extend(dd[dd<xmax])
    h,_=np.histogram(d,np.linspace(0,xmax,nb+1)); return h/(len(u)*xmax/nb)
xs=np.linspace(0,3,31); xc=(xs[:-1]+xs[1:])/2
R2gue=lambda x:1-(np.sin(np.pi*x)/(np.pi*x))**2
out["L2"]={}
fig,ax=plt.subplots(2,3,figsize=(13,6))
for j,(name,s) in enumerate([("zeros",sz),("primes",sp),("random",sr)]):
    s=s/s.mean()
    out["L2"][name]={"mean":float(s.mean()),"L1_to_GUE":l1(s,gue),"L1_to_Poisson":l1(s,poi),
        "frac_below_0.2":float((s<0.2).mean())}
    R=r2(s); out["L2"][name]["R2_L1_to_GUE"]=float(np.mean(np.abs(R-R2gue(xc)))); out["L2"][name]["R2_L1_to_Poisson"]=float(np.mean(np.abs(R-1)))
    ax[0,j].hist(s,bins,density=True,alpha=.6); ax[0,j].plot(c,gue(c),"r",label="GUE"); ax[0,j].plot(c,poi(c),"k--",label="Poisson"); ax[0,j].set_title(f"NN spacing: {name}"); ax[0,j].legend()
    ax[1,j].bar(xc,R,width=.1,alpha=.6); ax[1,j].plot(xc,R2gue(xc),"r"); ax[1,j].axhline(1,c="k",ls="--"); ax[1,j].set_title(f"pair corr: {name}"); ax[1,j].set_ylim(0,1.6)
plt.tight_layout(); plt.savefig("L2_gue_controls.png",dpi=120); plt.close()
# ---------- L3 ----------
N=400; z20=zeros[:20]; target_spacing=np.mean(np.diff(z20))
def spectra(L):
    h=L/N; D=np.zeros((N,N))
    for i in range(N): D[i,(i+1)%N]=1/(2*h); D[i,(i-1)%N]=-1/(2*h)
    Dr=D.copy(); Dr[0,-1]=0; Dr[-1,0]=0           # reflecting: Dirichlet, drop wraparound
    theta=np.pi/3; Dt=D.astype(complex); Dt[N-1,0]*=np.exp(1j*theta); Dt[0,N-1]*=np.exp(-1j*theta)
    Da=np.zeros((N,N))                             # absorbing: upwind, open right end
    for i in range(N-1): Da[i,i]=-1/h; Da[i,i+1]=1/h
    Da[N-1,N-1]=-1/h
    res={}
    for nm,M in [("reflecting",-1j*Dr),("periodic",-1j*D),("twisted",-1j*Dt)]:
        ev=np.sort(eigvalsh(M)); res[nm]=ev[ev>1e-9][:20]
    ev=eigvals(-1j*Da); res["absorbing"]=ev
    return res
out["L3"]={"note":"L tuned so periodic comb spacing 2pi/L equals mean spacing of first 20 zeros","target_mean_spacing":float(target_spacing)}
L=2*np.pi/target_spacing; sp_=spectra(L); out["L3"]["L_tuned"]=float(L)
fig,ax=plt.subplots(1,2,figsize=(12,4))
ax[0].plot(range(1,21),z20,"ko-",label="zeta zeros")
for nm in ["reflecting","periodic","twisted"]:
    e=sp_[nm]; e=e[:20]
    # best affine fit e -> zeros to be generous, report raw and fitted RMS
    A=np.vstack([e,np.ones_like(e)]).T; coef,*_=np.linalg.lstsq(A,z20[:len(e)],rcond=None)
    out["L3"][nm]={"first5":e[:5].tolist(),"spacing_std_over_mean":float(np.std(np.diff(e))/np.mean(np.diff(e))),
        "RMS_raw":float(np.sqrt(np.mean((e-z20[:len(e)])**2))),"RMS_after_affine_fit":float(np.sqrt(np.mean((A@coef-z20[:len(e)])**2)))}
    ax[0].plot(range(1,len(e)+1),e,"o-",ms=3,label=nm)
ab=sp_["absorbing"]; out["L3"]["absorbing"]={"max_abs_imag":float(np.max(np.abs(ab.imag))),"n_complex":int(np.sum(np.abs(ab.imag)>1e-6)),"verdict":"non-self-adjoint; complex spectrum; disqualified as Hilbert-Polya candidate"}
out["L3"]["zeros"]={"spacing_std_over_mean":float(np.std(np.diff(z20))/np.mean(np.diff(z20))),"first_gap":float(z20[1]-z20[0]),"gap_19_20":float(z20[19]-z20[18])}
ax[0].legend(); ax[0].set_title("first 20 eigenvalues vs zeros (L tuned)")
# Secondary: counting function vs Berry-Keating smooth count
T=np.linspace(10,zeros[-1],500); Nz=np.searchsorted(zeros,T); Nbk=(T/(2*np.pi))*np.log(T/(2*np.pi*np.e))+7/8
ax[1].plot(T,Nz,"k",label="N(T) actual"); ax[1].plot(T,Nbk,"r--",label="BK smooth (T/2pi)ln(T/2pi e)+7/8"); ax[1].plot(T,T/target_spacing,"b:",label="comb N(T)=T/spacing"); ax[1].legend(); ax[1].set_title("counting function")
out["L3"]["counting"]={"max_abs_dev_BK_smooth":float(np.max(np.abs(Nz-Nbk))),"max_abs_dev_comb":float(np.max(np.abs(Nz-T/target_spacing)))}
plt.tight_layout(); plt.savefig("L3_xp_boundary.png",dpi=120); plt.close()
out["runtime_s"]=time.time()-t0
json.dump(out,open("metrics.json","w"),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
