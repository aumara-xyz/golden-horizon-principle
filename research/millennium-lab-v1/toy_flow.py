import numpy as np, json
from scipy.integrate import solve_ivp
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
x0=np.loadtxt("zeros.txt"); N=len(x0)
def rhs(t,x):
    d=x[:,None]-x[None,:]; np.fill_diagonal(d,np.inf); return (2/d).sum(1)+(2/(x[:,None]+x[None,:])).sum(1)
def cv(x,inner=slice(100,900)):
    g=np.diff(x); loc=np.convolve(g,np.ones(51)/51,mode="same"); s=(g/loc)[inner]; return float(s.std()/s.mean()), s
g0=np.diff(x0); jmin=int(np.argmin(g0)); gmin=float(g0[jmin])
out={"N":N,"g_min":gmin,"closest_pair_index":jmin+1,"closest_pair_gamma":float(x0[jmin]),"t_c_predicted":gmin**2/8,"cv_t0":cv(x0)[0]}
# forward
ts=[0.25,0.5,1,2]; fw=solve_ivp(rhs,(0,2),x0,t_eval=ts,rtol=1e-8,atol=1e-10,method="DOP853")
out["forward"]={f"t={t}":{"cv":cv(fw.y[:,i])[0],"min_gap":float(np.diff(fw.y[:,i]).min())} for i,t in enumerate(ts)}
# backward with collision event
def ev(t,x): return np.diff(x).min()-1e-3
ev.terminal=True; ev.direction=-1
bw=solve_ivp(rhs,(0,-0.5),x0,events=ev,rtol=1e-8,atol=1e-10,method="DOP853",dense_output=True)
tc=float(bw.t_events[0][0]) if len(bw.t_events[0]) else None
xc=bw.y_events[0][0] if tc else None; jc=int(np.argmin(np.diff(xc))) if tc else None
out["backward"]={"t_collision":tc,"colliding_pair_index":(jc+1) if tc else None,"colliding_pair_gamma":float(xc[jc]) if tc else None,"is_closest_pair":(jc==jmin) if tc else None,"ratio_tc_to_pred":(abs(tc)/(gmin**2/8)) if tc else None}
# gap trajectory of the closest pair backward
tt=np.linspace(0,tc,200); gap=[np.diff(bw.sol(t))[jmin] for t in tt]
fig,ax=plt.subplots(1,2,figsize=(13,4.5)); b=np.linspace(0,3,31)
for lab,x in [("t=0 (the zeros)",x0),("t=+0.5",fw.y[:,1]),("t=+2",fw.y[:,3])]:
    ax[0].hist(cv(x)[1],b,density=True,histtype="step",lw=1.5,label=f"{lab}, cv={cv(x)[0]:.2f}")
ax[0].legend(); ax[0].set_title("forward flow: spacings sharpen toward a comb"); ax[0].set_xlabel("normalized spacing")
ax[1].plot(tt,gap,"r"); ax[1].axhline(0,c="k",lw=.5); ax[1].set_xlabel("t (backward)"); ax[1].set_ylabel(f"gap of pair #{jmin+1} (gamma~{x0[jmin]:.1f})"); ax[1].set_title(f"backward flow: closest pair collides at t={tc:.2e}" if tc else "no collision")
plt.tight_layout(); plt.savefig("toy-flow.png",dpi=120); json.dump(out,open("toy-flow.json","w"),indent=1); print(json.dumps(out,indent=1))
